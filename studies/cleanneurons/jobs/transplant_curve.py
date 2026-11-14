"""cleanneurons Part T (specs/SPEC1.md): the transplant curve. The base with an edit applied in memory is scored against RL with
teacher forcing on stored T1 and T2 answers. Inference only. One H100, both models in bf16, on the team runner:

    uv run tools/gpu.py submit h100 --hours 0.7 -- "python -m studies.cleanneurons.jobs.transplant_curve --commit $(git rev-parse HEAD)"
    smoke: add  --smoke   (per cell the 2 shortest eligible answers; arms all, mlp, attn, other, top1, rnd1_s0, mlpL0-7, none)
    shorter: --rows 20    (the run time is proportional to the rows)

Inputs: /runs/inputs/rln5/T1.jsonl and T2.jsonl, asserted against studies/rlneurons/data/rln5/map_inputs.json; sequences from
rln5_map.build (prompt + cue + generated tokens + stop token). Rows: per cell the answers with 500 <= n_new <= 3,000 that are not cap
hits and re-tokenize to within 1 % of n_new, sorted by problem index, --rows of them evenly spaced. Scored positions: every token
after the prompt.

Per row: RL's log-probs once, the unedited base once (KL(RL || base), which defines the decisive positions), then every arm: apply
the edit to the base in memory, one forward pass, KL(RL || arm) in nats and the arm's top-1 token, undo. `none` runs last, after
every other arm of the row was applied and undone. Arms (lib/neurons.py holds the edit format):
  none, all            no edit; every tensor from RL
  mlp, attn, other     one whole family from RL
  top{k}               the k % of neurons with the largest s, k in 0.1, 0.3, 1, 3, 10, 30 (s: squared L2 norm of RL - base over the
                       neuron's three weight vectors, float32; ties by neuron index)
  rnd{k}_s{0,1}        the same number of neurons drawn uniformly without replacement, numpy default_rng([seed, number])
  mlpL{a}-{b}          all neurons of a quarter of the layers
Decisive positions: per cell the 4 % of scored positions with the largest KL(RL || base).
Closure of an arm on a position set: 1 - mean KL(RL || arm) / mean KL(RL || base).

Outputs in --out (default $OUT_DIR):
  metrics.json   config, commit, job id, models; base[cell]: mean_kl_all, mean_kl_decisive, top1_agree_all, top1_agree_decisive;
                 arms[arm]: neurons (number of neurons taken from RL), share_of_sum_s, cells[cell]: the same four numbers plus
                 closure_all and closure_decisive; cells[cell]: rows (problem indices), positions, decisive_positions, the smallest
                 decisive KL; controls with their numbers and pass flags
  rank.npz       s, float32 [layers, width]
  profile.json   share of sum(s) per layer; share held by the top 0.1 ... 30 % of neurons; squared weight change and its share in
                 mlp / attn / other
  examples.json  per cell, for the row with the most decisive positions: its 20 decisive positions with the largest KL(RL || base):
                 the 40 tokens before, the written token, the top-1 tokens of RL, the base and top1, KL(RL || base), KL(RL || top1)
  kl.npz         per cell: <cell>_kl float32 [1 + arms, positions] (row 0 the base, then the arms in the order of arm_order in
                 metrics.json), <cell>_offsets (row r is positions offsets[r]:offsets[r+1]), <cell>_decisive (bool)
  edit_top1.json, edit_top3.json, edit_rnd1_s0.json, edit_mlp.json, edit_attn.json   those arms in the edit-file format (Part G)

Controls (the job writes every file, then fails if one fails): `all` has mean KL below 1e-4 in every cell; `none` has exactly the
unedited base's KL and top-1 at every position; after each arm of each row the edit is undone and one tensor it edited is compared
bit for bit with a copy taken before the arm was first applied (a tensor that the comparison called different while the edit was on).

--dry-run: lib/neurons.tiny_pair (a random 4-layer Llama and a perturbed copy) on synthetic rows, CPU, no download; the same controls
are asserted, and the five edit files go through build_checkpoint and diff_checkpoint on the tiny pair. Fail loud: no try/except.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import tempfile
import time

import numpy as np
import torch

from studies.cleanneurons.lib import neurons as N
from studies.rlneurons.jobs import rln5_map as M5

KS = (0.1, 0.3, 1, 3, 10, 30)                         # per cent of the neurons
SEEDS = (0, 1)
N_MIN, N_MAX = 500, 3000                              # n_new of an eligible answer
DECISIVE = 0.04
ALL_KL_TOL = 1e-4
EDIT_FILES = ("top1", "top3", "rnd1_s0", "mlp", "attn")
N_EXAMPLES, CONTEXT = 20, 40


def count(k, total):
    return max(1, round(total * k / 100))


def by_layer(flat, W):
    return {str(l): sorted(int(n) for n in flat[flat // W == l] % W) for l in sorted(set((flat // W).tolist()))}


def make_arms(s):
    """{arm: edit} in the order they run (none last) and the names of the layer groups. s: float32 [L, W]."""
    L, W = s.shape
    assert L % 4 == 0, L
    order = np.argsort(-s.ravel(), kind="stable")
    arms = {"all": {"copy_families": list(N.FAMILIES)}, **{f: {"copy_families": [f]} for f in N.FAMILIES}}
    for k in KS:
        n = count(k, L * W)
        arms[f"top{k:g}"] = {"copy_neurons": by_layer(order[:n], W)}
        for seed in SEEDS:
            arms[f"rnd{k:g}_s{seed}"] = {"copy_neurons": by_layer(np.random.default_rng([seed, n]).choice(L * W, n, replace=False), W)}
    groups = [f"mlpL{a}-{a + L // 4 - 1}" for a in range(0, L, L // 4)]
    for g, a in zip(groups, range(0, L, L // 4)):
        arms[g] = {"copy_neurons": {str(l): list(range(W)) for l in range(a, a + L // 4)}}
    arms["none"] = {}
    return {k: {"name": k, **v} for k, v in arms.items()}, groups


def select(seqs, n, smoke):
    """seqs: the eligible answers of one cell, sorted by problem index."""
    if smoke:
        return sorted(sorted(seqs, key=lambda s: (s["n_new"], s["idx"]))[:2], key=lambda s: s["idx"])
    if len(seqs) <= n:
        return seqs
    pick = np.linspace(0, len(seqs) - 1, n).round().astype(int)
    assert len(set(pick.tolist())) == n
    return [seqs[i] for i in pick]


def stored_sequences(a, fz, cells):
    """The eligible answers of each cell as rln5_map.build sequences, and the tokenizer. The asserts on the inputs are those of
    rln5_map.main, which holds them inline."""
    D4, frozen = M5.D4, json.loads((M5.D5 / "map_inputs.json").read_text())
    assert M5.sha(D4 / "math500.json") == fz["sha256"]["math500.json"]
    math = json.loads((D4 / "math500.json").read_text())
    assert all(int(p["index"]) == i for i, p in enumerate(math))
    n13 = json.loads((D4 / "prompt_ids.json").read_text())
    assert n13["pair"] == "pair1"
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"]))
    assert tok.decode(fz["prefill_ids"]) == fz["prefill_text"]
    seqs = {}
    for c in cells:
        p, f = pathlib.Path(a.inputs) / f"{c}.jsonl", frozen["files"][f"{c}.jsonl"]
        assert p.stat().st_size == f["bytes"] and M5.sha(p) == f["sha256"], f"{p} differs from data/rln5/map_inputs.json"
        rows = sorted((json.loads(l) for l in p.read_text().splitlines()), key=lambda r: r["problem_index"])
        assert [r["problem_index"] for r in rows] == list(range(500)) and all(r["cell"] == c and r["sampling"] == fz["cells"][c][2] for r in rows)
        built = [M5.build(tok, fz, r, math[r["problem_index"]], n13["ids"][r["problem_index"]])
                 for r in rows if N_MIN <= r["n_new"] <= N_MAX and not r["cap_hit"]]
        seqs[c] = [s for s in built if abs(s["retok_diff"]) <= M5.TOL * s["n_new"]]
    return seqs, tok, frozen["files"]


def synthetic_sequences(cells, vocab):
    """--dry-run: 12 rows per cell with random token ids; some are too short, too long or cap hits."""
    g, seqs = np.random.default_rng(0), {}
    for c in cells:
        rows = [(i, int(g.integers(300, 3600)), i % 5 == 4) for i in range(12)]
        seqs[c] = [{"idx": i, "ids": g.integers(2, vocab, 20 + n).tolist() + [1], "n_prompt": 20, "n_cue": 3 * (c == "T1"),
                    "n_gen": n - 3 * (c == "T1"), "has_stop": 1, "n_new": n} for i, n, cap in rows if N_MIN <= n <= N_MAX and not cap]
    return seqs


def changed_tensor(base, rl, edit, ops, sd):
    """A tensor that the edit changes (the last such in the plan) and its copy from before the edit: what the undo control compares.
    The edit is applied and undone here once, so the comparison has seen an applied edit and has called it different.
    (None, None) for an edit that changes no bit."""
    for name in reversed(list(ops)):
        before = sd[name].clone()
        undo = N.apply_edit(base, rl, edit, ops)
        changed = not N.bits_equal(sd[name], before)
        undo()
        assert N.bits_equal(sd[name], before), ("undo", edit["name"], name)
        if changed:
            return name, before
    return None, None


@torch.inference_mode()
def logp(model, x, first):
    return torch.log_softmax(model(input_ids=x, use_cache=False).logits[0, first:].float(), -1)


def kl_top1(lp_rl, p_rl, lp):
    return (p_rl * (lp_rl - lp)).sum(-1).cpu().numpy(), lp.argmax(-1).cpu().numpy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", default="/runs/inputs/rln5")
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--commit", required=True, help="the submitted commit: $(git rev-parse HEAD), expanded on the laptop")
    ap.add_argument("--cells", default="T1,T2")
    ap.add_argument("--rows", type=int, default=40, help="answers per cell")
    ap.add_argument("--smoke", action="store_true", help="per cell the 2 shortest eligible answers, and 8 arms")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    assert a.out, "no --out and no $OUT_DIR"
    assert re.fullmatch(r"[0-9a-f]{40}", a.commit), f"--commit {a.commit!r} is not a full git sha"
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / "metrics.json").exists(), f"{out}/metrics.json exists: one fresh directory per run"
    cells = a.cells.split(",")
    assert all(c in M5.CELLS for c in cells)
    m = {"status": "loading", "config": {**vars(a), "out": str(out), "n_new": [N_MIN, N_MAX], "decisive_share": DECISIVE}, "commit": a.commit,
         "job_id": os.environ.get("JOB_ID"), "started_utc": M5.utc(), "torch": torch.__version__}
    M5.dump(out / "metrics.json", m)

    if a.dry_run:
        dev = "cpu"
        base, rl = N.tiny_pair()
        m["models"] = {"dry_run": True, "class": type(base).__name__}
        seqs, decode = synthetic_sequences(cells, base.config.vocab_size), lambda ids: " ".join(str(i) for i in ids)
    else:
        dev = "cuda"
        fz = json.loads((M5.D4 / "frozen4.json").read_text())
        seqs, tok, m["inputs"] = stored_sequences(a, fz, cells)
        decode = lambda ids: tok.decode(ids, skip_special_tokens=False)
        m["gpu"] = torch.cuda.get_device_name(0)
        (base, ib), (rl, ir) = M5.load(fz, "base", dev), M5.load(fz, "rl", dev)
        m["models"] = {"base": ib, "rl": ir}
    sel = {c: select(seqs[c], a.rows, a.smoke) for c in cells}
    m["cells"] = {c: {"eligible": len(seqs[c]), "rows": [s["idx"] for s in sel[c]]} for c in cells}
    sd, sd_rl = base.state_dict(), rl.state_dict()
    shapes = N.shapes_of(sd)
    assert shapes == N.shapes_of(sd_rl) and all(sd[k].dtype == sd_rl[k].dtype for k in sd), "the two models do not hold the same tensors"

    # ranking, profile, arms, edit files
    s = N.rank(sd, sd_rl).cpu().numpy()
    assert s.dtype == np.float32 and np.isfinite(s).all()
    L, W = s.shape
    np.savez(out / "rank.npz", s=s)
    s64, change = s.astype(np.float64), N.weight_change(sd, sd_rl)
    total, desc = s64.sum(), np.sort(s64.ravel())[::-1]
    assert abs(total - change["mlp"]) <= 1e-3 * total, ("sum(s) against the mlp family's squared change", total, change["mlp"])
    top_share = {f"{k:g}": {"neurons": count(k, L * W), "share": float(desc[:count(k, L * W)].sum() / total)} for k in KS}
    M5.dump(out / "profile.json", {"layers": L, "width": W, "neurons": L * W, "sum_s": total,
                                   "share_of_sum_s_per_layer": (s64.sum(1) / total).tolist(), "share_of_sum_s_top_percent": top_share,
                                   "squared_weight_change": change,
                                   "share_of_squared_weight_change": {f: v / sum(change.values()) for f, v in change.items()}})
    edits, groups = make_arms(s)
    for name in EDIT_FILES:
        M5.dump(out / f"edit_{name}.json", edits[name])
    order = ["all", *N.FAMILIES, "top1", "rnd1_s0", groups[0], "none"] if a.smoke else list(edits)
    assert order[-1] == "none" and {"all", "top1"} <= set(order)
    plans = {k: N.plan(edits[k], shapes, dev) for k in order}
    check = {k: changed_tensor(base, rl, edits[k], plans[k], sd) for k in order}  # arm -> (tensor compared after undo, its copy)
    arm_info = {k: {"neurons": int(N.neuron_mask(edits[k], L, W).sum()),
                    "share_of_sum_s": float(s64[N.neuron_mask(edits[k], L, W).numpy()].sum() / total)} for k in order}
    m.update(status="running", load_s=time.time() - t0, arm_order=order, undo_check_tensor={k: v[0] for k, v in check.items()})
    M5.dump(out / "metrics.json", m)

    # the pass
    res = {c: {"kl": {k: [] for k in ["base", *order]}, "top": {k: [] for k in ("rl", "base", *order)}} for c in cells}
    undo_checks, undo_failed, t_run, n_forward = 0, [], time.time(), 0
    for c in cells:
        for i, q in enumerate(sel[c]):
            x, first = torch.tensor(q["ids"][:-1], device=dev)[None], q["n_prompt"] - 1
            lp_rl = logp(rl, x, first)
            p_rl, R = lp_rl.exp(), res[c]
            R["top"]["rl"].append(lp_rl.argmax(-1).cpu().numpy())
            for k in ["base", *order]:
                undo = N.apply_edit(base, rl, edits[k], plans[k]) if k != "base" else None
                kl, top = kl_top1(lp_rl, p_rl, logp(base, x, first))
                if undo:
                    undo()
                    if check[k][0]:
                        undo_checks += 1
                        if not N.bits_equal(sd[check[k][0]], check[k][1]):
                            undo_failed.append([c, q["idx"], k, check[k][0]])
                assert len(kl) == len(q["ids"]) - q["n_prompt"] and np.isfinite(kl).all(), ("KL", c, q["idx"], k)
                R["kl"][k].append(kl)
                R["top"][k].append(top)
            n_forward += (len(order) + 2) * x.shape[1]
            print(f"{M5.utc()} {c} row {i + 1}/{len(sel[c])} problem {q['idx']}: {len(kl)} positions; {time.time() - t_run:.0f} s", flush=True)

    # per cell: decisive positions, closures, examples
    m["base"], m["arms"], examples, npz, none_diff = {}, {k: {**arm_info[k], "cells": {}} for k in order}, {}, {}, {}
    for c in cells:
        R = res[c]
        kl = {k: np.concatenate(v).astype(np.float64) for k, v in R["kl"].items()}
        top = {k: np.concatenate(v) for k, v in R["top"].items()}
        n = len(kl["base"])
        dec = np.zeros(n, dtype=bool)
        dec[np.argsort(-kl["base"], kind="stable")[:max(1, round(DECISIVE * n))]] = True
        row = lambda k: {"mean_kl_all": float(kl[k].mean()), "mean_kl_decisive": float(kl[k][dec].mean()),
                         "top1_agree_all": float((top[k] == top["rl"]).mean()), "top1_agree_decisive": float((top[k] == top["rl"])[dec].mean())}
        m["base"][c] = row("base")
        for k in order:
            m["arms"][k]["cells"][c] = {**row(k), "closure_all": float(1 - kl[k].mean() / kl["base"].mean()),
                                        "closure_decisive": float(1 - kl[k][dec].mean() / kl["base"][dec].mean())}
        m["cells"][c].update(positions=n, decisive_positions=int(dec.sum()), smallest_decisive_kl=float(kl["base"][dec].min()))
        none_diff[c] = {"max_abs_kl_difference": float(np.abs(kl["none"] - kl["base"]).max()), "top1_differ": int((top["none"] != top["base"]).sum())}
        off = np.cumsum([0] + [len(v) for v in R["kl"]["base"]])
        npz |= {f"{c}_kl": np.stack([kl[k] for k in ["base", *order]]).astype(np.float32), f"{c}_offsets": off, f"{c}_decisive": dec}
        r = int(np.argmax([dec[off[j]:off[j + 1]].sum() for j in range(len(sel[c]))]))
        q, lo = sel[c][r], off[r]
        pos = [j for j in np.argsort(-kl["base"][lo:off[r + 1]], kind="stable") if dec[lo + j]][:N_EXAMPLES]
        examples[c] = {"problem_index": q["idx"], "decisive_positions_in_row": int(dec[lo:off[r + 1]].sum()), "positions": [
            {"position": int(j), "context": decode(q["ids"][max(0, q["n_prompt"] + j - CONTEXT):q["n_prompt"] + j]),
             "written": decode([q["ids"][q["n_prompt"] + j]]), **{f"top1_token_{k}": decode([int(top[k][lo + j])]) for k in ("rl", "base", "top1")},
             "kl_rl_base": float(kl["base"][lo + j]), "kl_rl_top1": float(kl["top1"][lo + j])} for j in pos]}
    np.savez_compressed(out / "kl.npz", **npz)
    M5.dump(out / "examples.json", examples)

    all_kl = {c: m["arms"]["all"]["cells"][c]["mean_kl_all"] for c in cells}
    m["controls"] = {"all": {"mean_kl": all_kl, "below": ALL_KL_TOL, "pass": all(v < ALL_KL_TOL for v in all_kl.values())},
                     "none": {**none_diff, "pass": all(v["max_abs_kl_difference"] == 0 and v["top1_differ"] == 0 for v in none_diff.values())},
                     "undo": {"checks": undo_checks, "failed": undo_failed, "arms_that_change_no_bit": [k for k in order if not check[k][0]],
                              "pass": undo_checks > 0 and not undo_failed}}
    sec = time.time() - t_run
    m.update(status="done", wall_s=time.time() - t0, pass_s=sec, forward_tokens=n_forward, forward_tokens_per_s=n_forward / max(sec, 1e-9))
    M5.dump(out / "metrics.json", m)
    if a.dry_run:                                                 # the edit files through the Part G build, on the tiny pair
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            b2, r2 = N.saved_pair(tmp)
            x = torch.tensor(sel[cells[0]][0]["ids"][:64])[None]
            m["dry_run_builds"] = {}
            for k in EDIT_FILES:
                rep = N.roundtrip(b2, r2, tmp / "base", tmp / "rl", json.loads((out / f"edit_{k}.json").read_text()), tmp / k, x)
                m["dry_run_builds"][k] = {"shards_rewritten": len(rep["shards_rewritten"]), "entries_differ": rep["diff"]["entries_differ"]}
    else:
        m["gpu_max_memory_gb"] = torch.cuda.max_memory_allocated() / 2 ** 30
    M5.dump(out / "metrics.json", m)
    closure = {k: {c: round(v["cells"][c]["closure_decisive"], 4) for c in cells} for k, v in m["arms"].items()}
    print(json.dumps({"controls": m["controls"], "wall_s": m["wall_s"], "pass_s": sec, "base": m["base"]}, indent=1), flush=True)
    print("closure on decisive positions:\n" + "\n".join(f"  {k:12s} {v}" for k, v in closure.items()), flush=True)
    failed = [k for k, v in m["controls"].items() if not v["pass"]]
    assert not failed, f"controls failed: {failed} (see metrics.json)"


if __name__ == "__main__":
    main()
