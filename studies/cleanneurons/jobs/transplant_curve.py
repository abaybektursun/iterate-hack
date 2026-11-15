"""cleanneurons Part T (specs/SPEC1.md): the transplant curve. The base with an edit applied in memory is scored against RL with
teacher forcing on stored T1 and T2 answers. Inference only. One H100, both models in bf16, on the team runner:

    uv run tools/gpu.py submit h100 --hours 0.7 -- "python -m studies.cleanneurons.jobs.transplant_curve --commit $(git rev-parse HEAD)"
    smoke: add  --smoke   (per cell the 2 shortest eligible answers; arms all, mlp, attn, other, top1, rnd1_s0, mlpL0-7, none)
    shorter: --rows 20    (the run time is proportional to the rows)
    Part T2: add  --rank attr   (the attribution ranking and the attr{k} arms; with --smoke also attr1)
    Part T3: add  --bias        (constant-shift and dense-neuron arms; alone or with --rank attr; with --smoke all of them)

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
Position sets, per cell: all; decisive (the 4 % of all with the largest KL(RL || base)); after_cue (all but the first 3 scored
positions of every row: the cue, prefilled in T1 and written by RL in T2); decisive_after_cue (the 4 % of after_cue with the largest
KL(RL || base)). The after-cue sets are the ones to read: in the first run the cue held 24 % of the decisive KL.
Closure of an arm on a position set: 1 - mean KL(RL || arm) / mean KL(RL || base).

Part T2 (--rank attr). Row j of a cell's rows (in order of problem index) is in half A when j is even, in half B when odd. On half
A: KL(RL || base) of every row gives the decisive positions after the cue (4 % per cell, within half A); L is the mean KL(RL || base)
over them, both cells pooled. One backward pass per row (the base in bf16, only the MLP matrices require grad); after each row
neurons.attr_step turns the bf16 gradients into the per-neuron product with (RL - base) in float32, summed over rows in float64 (the
score is linear in the gradient, so this equals a float32 gradient accumulator and saves its 17 GB). Score of a neuron: the
first-order drop of L when it is copied from RL. Arms attr{k}, k in 0.1, 0.3, 1, 3, 10: the k % of neurons with the largest score.
Every arm also gets after_cue_half_B and decisive_after_cue_half_B (the 4 % within half B): the held-out numbers.

Part T3 (--bias; the same half split, no gradient pass). Does the RL change act as one constant vector per layer? Measured on the
scored positions of half A (cue included), during the base's own forward pass:
  d_mlp[l]    mean of RL_mlp_l(x) - base_mlp_l(x), x the input of the base's MLP module l (RL's MLP module applied to it in a hook)
  d_layer[l]  mean of RL_layer_l(args) - base_layer_l(args), on the args and kwargs the base's layer l was called with
  dense       neurons with |a| above their layer's p97 of |a| at more than half of those positions (a: the input of down_proj; the
              p97 over all neurons at 32 random positions per row, numpy default_rng(0))
Arms (hooks on the base, removed after each forward pass; neurons.shift_hooks):
  bias_mlp, bias_layer          d_mlp[l] added to the output of MLP module l (in Olmo 3 a norm follows it), d_layer[l] added to the
                                output of layer l (the residual stream); at every position, rounded to bf16 stochastically, so the
                                mean output moves by exactly d
  bias_mlp_nearest, bias_layer_nearest   the same with round-to-nearest: a shift below half the bf16 spacing of an entry is lost there
  bias_mlp_rnd                  per layer a random vector with the norm of d_mlp[l] (torch seed 0), stochastic rounding: the control
  bias_zero                     zero vectors through both hooks: must reproduce the base exactly
  dense, dense_rnd              the dense neurons copied from RL; per layer the same number drawn from the other neurons
                                (numpy default_rng([2, layer]))

Outputs in --out (default $OUT_DIR):
  metrics.json   config, commit, job id, models; base[cell]: mean_kl_all, mean_kl_decisive, top1_agree_all, top1_agree_decisive;
                 arms[arm]: neurons (number of neurons taken from RL), share_of_sum_s, cells[cell]: the same four numbers plus
                 closure_all and closure_decisive; cells[cell]: rows (problem indices), positions, decisive_positions, the smallest
                 decisive KL; controls with their numbers and pass flags. For every other position set <set>: mean_kl_<set> and
                 closure_<set> next to those, and in cells[cell] its size, smallest decisive KL and share_of_decisive_kl_on_cue.
                 With --rank attr: attr (the split rule, half_A and half_B problem indices, decisive positions of half A, L on half
                 A from the gradient pass and from the scoring pass, sum of all scores; arms[arm]: predicted_drop = sum of the
                 scores of the arm's neurons, measured_drop = L(base) - L(arm) on half A's decisive positions, and for attr arms
                 the neurons shared with top{k})
                 With --bias: bias (per layer the norm of d, the mean norm of the base's MLP output or layer update and their
                 ratio, for mlp and layer; the p97 and the number of dense neurons per layer; positions of half A); with either
                 flag: halves (the split rule, half_A and half_B problem indices)
  rank_attr.npz  (--rank attr) score, float32 [layers, width]
  bias.npz       (--bias) d_mlp, d_layer, d_mlp_rnd float32 [layers, hidden]; dense_share float32 [layers, width] (share of half A's
                 positions with |a| above the layer's p97); p97 float32 [layers]
  rank.npz       s, float32 [layers, width]
  profile.json   share of sum(s) per layer; share held by the top 0.1 ... 30 % of neurons; squared weight change and its share in
                 mlp / attn / other
  examples.json  per cell, for the row with the most decisive positions: its 20 decisive positions with the largest KL(RL || base):
                 the 40 tokens before, the written token, the top-1 tokens of RL, the base and top1, KL(RL || base), KL(RL || top1)
                 (examples use the decisive positions after the cue; with --rank attr also attr1's token and KL)
  kl.npz         per cell: <cell>_kl float32 [1 + arms, positions] (row 0 the base, then the arms in the order of arm_order in
                 metrics.json), <cell>_offsets (row r is positions offsets[r]:offsets[r+1]), <cell>_decisive,
                 <cell>_decisive_after_cue (bool), with --rank attr <cell>_half_B (bool, per position)
  edit_top1.json, edit_top3.json, edit_rnd1_s0.json, edit_mlp.json, edit_attn.json   those arms in the edit-file format (Part G);
                 with --rank attr also edit_attr1.json and edit_attr3.json, with --bias edit_dense.json

Controls (the job writes every file, then fails if one fails): `all` has mean KL below 1e-4 in every cell; `none` has exactly the
unedited base's KL and top-1 at every position; after each arm of each row the edit is undone and one tensor it edited is compared
bit for bit with a copy taken before the arm was first applied (a tensor that the comparison called different while the edit was on).
With --rank attr: attr1 lowers L on half A (a ranking whose top set does not lower L on its own rows is broken; the first-order
prediction is reported next to the measured drop), and the scoring pass finds the decisive positions the ranking used.
With --bias: bias_zero has exactly the unedited base's KL and top-1 at every position.

--dry-run: lib/neurons.tiny_pair (a random 4-layer Llama and a perturbed copy) on synthetic rows, CPU, no download; the same controls
are asserted, and the edit files go through build_checkpoint and diff_checkpoint on the tiny pair. With --bias, bias_stats must
recover a vector planted with shift_hooks in a copy of the base (as d_mlp, then as d_layer), and the stand-in's always-on neuron
must be dense. Fail loud: no try/except.
"""
from __future__ import annotations

import argparse
import copy
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
ATTR_KS = (0.1, 0.3, 1, 3, 10)
N_CUE = 3                                             # scored positions left out at the start of every row
SUB, P97, DENSE_SHARE, BIAS_SEED = 32, 0.97, 0.5, 0   # Part T3: positions per row for the layer's p97 of |a|; the dense rule
SPLIT = "row j of a cell's rows (in order of problem index) is in half A when j is even, in half B when j is odd"
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


def make_arms(s, attr=None):
    """{arm: edit} in the order they run (none last) and the names of the layer groups. s, attr: float32 [L, W]."""
    L, W = s.shape
    assert L % 4 == 0, L
    order = np.argsort(-s.ravel(), kind="stable")
    arms = {"all": {"copy_families": list(N.FAMILIES)}, **{f: {"copy_families": [f]} for f in N.FAMILIES}}
    for k in KS:
        n = count(k, L * W)
        arms[f"top{k:g}"] = {"copy_neurons": by_layer(order[:n], W)}
        if attr is not None and k in ATTR_KS:
            arms[f"attr{k:g}"] = {"copy_neurons": by_layer(np.argsort(-attr.ravel(), kind="stable")[:n], W)}
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


def after_cue(lengths):
    """bool over the concatenated positions of rows with these lengths: False on the first N_CUE of every row."""
    keep = np.ones(sum(lengths), dtype=bool)
    for a in np.cumsum([0] + list(lengths))[:-1]:
        keep[a:a + N_CUE] = False
    return keep


def decisive(kl, keep):
    """bool: the DECISIVE share of the positions in keep with the largest kl (ties by position)."""
    idx, dec = np.flatnonzero(keep), np.zeros(len(kl), dtype=bool)
    dec[idx[np.argsort(-kl[idx], kind="stable")[:max(1, round(DECISIVE * len(idx)))]]] = True
    return dec


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


def row_input(q, dev):
    return torch.tensor(q["ids"][:-1], device=dev)[None], q["n_prompt"] - 1


def attribution(base, rl, sd_rl, rows, dev):
    """Part T2 on half A (rows: {cell: sequences}). Returns the score (float32 [L, W]), L from the gradient pass, and the decisive
    positions it used ({cell: one bool array per row})."""
    dec, acc, n_dec, loss_sum = {}, 0, 0, 0.0
    for c, qs in rows.items():
        kl = []
        for q in qs:
            x, first = row_input(q, dev)
            lp_rl = logp(rl, x, first)
            kl.append(kl_top1(lp_rl, lp_rl.exp(), logp(base, x, first))[0])
        lens = [len(v) for v in kl]
        dec[c] = np.split(decisive(np.concatenate(kl).astype(np.float64), after_cue(lens)), np.cumsum(lens)[:-1])
    N.mlp_grad(base, True)
    for c, qs in rows.items():
        for q, d in zip(qs, dec[c]):
            if not d.any():
                continue
            x, first = row_input(q, dev)
            pos = torch.tensor(np.flatnonzero(d), device=dev)
            lp_rl = logp(rl, x, first)[pos].clone()               # a normal tensor: autograd cannot save an inference tensor
            lp = torch.log_softmax(base(input_ids=x, use_cache=False).logits[0, first:][pos].float(), -1)
            loss = (lp_rl.exp() * (lp_rl - lp)).sum()
            loss.backward()
            acc = acc + N.attr_step(base, sd_rl).double()
            n_dec, loss_sum = n_dec + len(pos), loss_sum + float(loss)
    N.mlp_grad(base, False)
    score = (acc / n_dec).float().cpu().numpy()
    assert np.isfinite(score).all(), "attribution: non-finite score"
    return score, loss_sum / n_dec, dec


@torch.inference_mode()
def bias_stats(base, rl, rows, dev):
    """Part T3 on half A (rows: sequences of both cells): d_mlp and d_layer (float32 [L, H], on dev), the mean norm of the base's MLP
    output and of its layer update per layer, the layer's p97 of |a| and each neuron's share of positions above it."""
    bl, rll, st = base.model.layers, rl.model.layers, {}
    L, (W, H) = len(bl), bl[0].mlp.gate_proj.weight.shape
    rng, sub = np.random.default_rng(BIAS_SEED), [[] for _ in bl]
    hs = [bl[l].mlp.down_proj.register_forward_pre_hook(lambda mod, args, l=l: sub[l].append(args[0][0, st["idx"]].abs())) for l in range(L)]
    for q in rows:                                                # pass 1: |a| of every neuron at SUB positions per row
        x, first = row_input(q, dev)
        n = x.shape[1] - first
        st["idx"] = torch.tensor(first + np.sort(rng.choice(n, min(SUB, n), replace=False)), device=dev)
        base(input_ids=x, use_cache=False)
    for h in hs:
        h.remove()
    p97 = [torch.cat(v).flatten().float() for v in sub]
    p97 = torch.stack([v.kthvalue(int(P97 * (v.numel() - 1)) + 1).values for v in p97])
    cnt, acc = torch.zeros(L, W, dtype=torch.int64, device=dev), torch.zeros(2, L, H, dtype=torch.float64, device=dev)
    norm = torch.zeros(2, L, dtype=torch.float64, device=dev)

    def hooks(l):
        def pre(mod, args):
            cnt[l] += (args[0][0, st["first"]:].abs() > p97[l]).sum(0)

        def mlp(mod, args, out):
            acc[0, l] += (rll[l].mlp(args[0]).float() - out.float())[0, st["first"]:].sum(0, dtype=torch.float64)
            norm[0, l] += out[0, st["first"]:].float().norm(dim=-1).sum(dtype=torch.float64)

        def layer(mod, args, kwargs, out):
            assert torch.is_tensor(out) and kwargs.get("past_key_values") is None, "bias_layer: the layer returned a tuple or got a cache"
            acc[1, l] += (rll[l](*args, **kwargs).float() - out.float())[0, st["first"]:].sum(0, dtype=torch.float64)
            norm[1, l] += (out.float() - args[0].float())[0, st["first"]:].norm(dim=-1).sum(dtype=torch.float64)
        return [bl[l].mlp.down_proj.register_forward_pre_hook(pre), bl[l].mlp.register_forward_hook(mlp),
                bl[l].register_forward_hook(layer, with_kwargs=True)]
    hs, n_pos = [h for l in range(L) for h in hooks(l)], 0
    for q in rows:                                                # pass 2: the mean differences, the norms, the counts above p97
        x, st["first"] = row_input(q, dev)
        base(input_ids=x, use_cache=False)
        n_pos += x.shape[1] - st["first"]
    for h in hs:
        h.remove()
    d = (acc / n_pos).float()
    assert torch.isfinite(d).all() and torch.isfinite(p97).all()
    return {"d_mlp": d[0], "d_layer": d[1], "norm_mlp": (norm[0] / n_pos).tolist(), "norm_layer": (norm[1] / n_pos).tolist(),
            "p97": p97.cpu().numpy(), "share": (cnt / n_pos).float().cpu().numpy(), "positions": n_pos}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", default="/runs/inputs/rln5")
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--commit", required=True, help="the submitted commit: $(git rev-parse HEAD), expanded on the laptop")
    ap.add_argument("--cells", default="T1,T2")
    ap.add_argument("--rows", type=int, default=40, help="answers per cell")
    ap.add_argument("--smoke", action="store_true", help="per cell the 2 shortest eligible answers, and 8 arms")
    ap.add_argument("--rank", default="weight", choices=("weight", "attr"), help="attr: Part T2, the attribution ranking and its arms")
    ap.add_argument("--bias", action="store_true", help="Part T3: the constant-shift and dense-neuron arms")
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
    m = {"status": "loading", "config": {**vars(a), "out": str(out), "n_new": [N_MIN, N_MAX], "decisive_share": DECISIVE, "n_cue": N_CUE}, "commit": a.commit,
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
    attr, edit_files, split = None, EDIT_FILES, a.rank == "attr" or a.bias
    if split:
        assert all(len(sel[c]) >= 2 for c in cells), "--rank attr and --bias need two rows per cell"
        m["halves"] = {"split": SPLIT, "half_A": {c: [q["idx"] for q in sel[c][0::2]] for c in cells},
                       "half_B": {c: [q["idx"] for q in sel[c][1::2]] for c in cells}}
    if a.rank == "attr":
        t_attr = time.time()
        attr, attr_L, attr_dec = attribution(base, rl, sd_rl, {c: sel[c][0::2] for c in cells}, dev)
        np.savez(out / "rank_attr.npz", score=attr)
        edit_files = EDIT_FILES + ("attr1", "attr3")
        m["attr"] = {**m["halves"], "decisive_positions_half_A": int(sum(d.sum() for c in cells for d in attr_dec[c])), "L_half_A_gradient_pass": attr_L,
                     "sum_of_scores": float(attr.astype(np.float64).sum()), "seconds": time.time() - t_attr}
    edits, groups = make_arms(s, attr)
    for name in edit_files:
        M5.dump(out / f"edit_{name}.json", edits[name])
    smoke_arms = ["all", *N.FAMILIES, "top1", *(["attr1"] if attr is not None else []), "rnd1_s0", groups[0], "none"]
    order, shifts = smoke_arms if a.smoke else list(edits), {}
    if a.bias:
        t_bias = time.time()
        st = bias_stats(base, rl, [q for c in cells for q in sel[c][0::2]], dev)
        gen = torch.Generator(device=dev).manual_seed(BIAS_SEED)                  # the stochastic rounding of every shift arm
        rnd = torch.randn(st["d_mlp"].shape, generator=torch.Generator().manual_seed(BIAS_SEED)).to(dev)
        rnd, zero = rnd * st["d_mlp"].norm(dim=1, keepdim=True) / rnd.norm(dim=1, keepdim=True), torch.zeros_like(st["d_mlp"])
        shifts = {"bias_mlp": [("mlp", st["d_mlp"], gen)], "bias_layer": [("layer", st["d_layer"], gen)], "bias_mlp_rnd": [("mlp", rnd, gen)],
                  "bias_mlp_nearest": [("mlp", st["d_mlp"], None)], "bias_layer_nearest": [("layer", st["d_layer"], None)],
                  "bias_zero": [("mlp", zero, gen), ("layer", zero, gen)]}
        dense = st["share"] > DENSE_SHARE
        others = [np.random.default_rng([2, l]).choice(np.flatnonzero(~dense[l]), int(dense[l].sum()), replace=False) + l * W for l in range(L)]
        edits |= {k: {"name": k} for k in shifts}
        for k, flat in (("dense", np.flatnonzero(dense.ravel())), ("dense_rnd", np.concatenate(others))):
            edits[k] = {"name": k, **({"copy_neurons": by_layer(flat, W)} if len(flat) else {})}
        M5.dump(out / "edit_dense.json", edits["dense"])
        edit_files, order = edit_files + ("dense",), [k for k in order if k != "none"] + [*shifts, "dense", "dense_rnd", "none"]
        np.savez(out / "bias.npz", d_mlp=st["d_mlp"].cpu().numpy(), d_layer=st["d_layer"].cpu().numpy(), d_mlp_rnd=rnd.cpu().numpy(),
                 dense_share=st["share"], p97=st["p97"])
        per_layer = lambda d, norms: {"norm_of_d": d.norm(dim=1).tolist(), "mean_norm": norms, "ratio": (d.norm(dim=1).cpu() / torch.tensor(norms)).tolist()}
        m["bias"] = {"arm_2": "bias_layer: the RL layer is called with the args and kwargs of the base's layer (no cache object with use_cache=False)",
                     "rounding": "bias_mlp, bias_layer, bias_mlp_rnd, bias_zero: stochastic to bf16; *_nearest: round to nearest",
                     "positions_half_A": st["positions"], "mlp": {**per_layer(st["d_mlp"], st["norm_mlp"]), "mean_norm_of": "the base's MLP output"},
                     "layer": {**per_layer(st["d_layer"], st["norm_layer"]), "mean_norm_of": "the base layer's update (output - input)"},
                     "dense": {"rule": f"|a| above the layer's p{100 * P97:g} of |a| at more than {DENSE_SHARE:g} of half A's scored positions",
                               "p97_of_abs_a": st["p97"].tolist(), "neurons_per_layer": dense.sum(1).tolist(), "neurons": int(dense.sum())},
                     "seconds": time.time() - t_bias}
        if a.dry_run:           # bias_stats must recover a planted shift: a copy of the base with a known vector added by shift_hooks
            v, rows_a, m["dry_run_bias_check"] = 0.05 * torch.randn(L, shapes[N.tensor_names(0)[2]][0]), [q for c in cells for q in sel[c][0::2]], {}
            for where, other in (("mlp", "layer"), ("layer", "mlp")):
                twin = copy.deepcopy(base)
                N.shift_hooks(twin, [(where, v, gen)])
                got = bias_stats(base, twin, rows_a, dev)
                err = float((got[f"d_{where}"] - v).abs().max() / v.abs().max())
                m["dry_run_bias_check"][where] = {"largest_error_over_largest_entry": err, "norm_of_other_d": float(got[f"d_{other}"].norm())}
                assert err < 0.02 and (got[f"d_{other}"].norm() > 0) == (where == "mlp"), ("bias_stats: planted shift", where, err)
            assert 5 in edits["dense"]["copy_neurons"]["0"], "dense: the stand-in's always-on neuron (0, 5) is missing"
    assert order[-1] == "none" and {"all", "top1"} <= set(order) and (attr is None or "attr1" in order)
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
            x, first = row_input(q, dev)
            lp_rl = logp(rl, x, first)
            p_rl, R = lp_rl.exp(), res[c]
            R["top"]["rl"].append(lp_rl.argmax(-1).cpu().numpy())
            for k in ["base", *order]:
                undo = N.apply_edit(base, rl, edits[k], plans[k]) if k != "base" else None
                remove = N.shift_hooks(base, shifts[k]) if k in shifts else None
                kl, top = kl_top1(lp_rl, p_rl, logp(base, x, first))
                if remove:
                    remove()
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

    # per cell: position sets, closures, examples
    m["base"], m["arms"], examples, npz, none_diff, zero_diff = {}, {k: {**arm_info[k], "cells": {}} for k in order}, {}, {}, {}, {}
    ex_arms = ("top1", "attr1") if attr is not None else ("top1",)
    half_a = {"sum": {k: 0.0 for k in ["base", *order]}, "n": 0, "same": True}       # half A's decisive positions, cells pooled
    for c in cells:
        R = res[c]
        kl = {k: np.concatenate(v).astype(np.float64) for k, v in R["kl"].items()}
        top = {k: np.concatenate(v) for k, v in R["top"].items()}
        lens = [len(v) for v in R["kl"]["base"]]
        n, off, keep = sum(lens), np.cumsum([0] + lens), after_cue(lens)
        sets = {"all": np.ones(n, dtype=bool), "decisive": decisive(kl["base"], np.ones(n, dtype=bool)), "after_cue": keep,
                "decisive_after_cue": decisive(kl["base"], keep)}
        if split:
            in_b = np.repeat(np.arange(len(lens)) % 2 == 1, lens)
            sets |= {"after_cue_half_B": keep & in_b, "decisive_after_cue_half_B": decisive(kl["base"], keep & in_b)}
            npz[f"{c}_half_B"] = in_b
        if attr is not None:
            dec_a = decisive(kl["base"], keep & ~in_b)
            half_a["same"] &= all(np.array_equal(dec_a[off[j]:off[j + 1]], attr_dec[c][j // 2]) for j in range(0, len(lens), 2))
            half_a["n"] += int(dec_a.sum())
            for k in half_a["sum"]:
                half_a["sum"][k] += float(kl[k][dec_a].sum())
        dec, dec_ac = sets["decisive"], sets["decisive_after_cue"]
        row = lambda k: {**{f"mean_kl_{name}": float(kl[k][v].mean()) for name, v in sets.items()},
                         "top1_agree_all": float((top[k] == top["rl"]).mean()), "top1_agree_decisive": float((top[k] == top["rl"])[dec].mean())}
        m["base"][c] = row("base")
        for k in order:
            m["arms"][k]["cells"][c] = {**row(k), **{f"closure_{name}": float(1 - kl[k][v].mean() / kl["base"][v].mean()) for name, v in sets.items()}}
        m["cells"][c].update(positions=n, decisive_positions=int(dec.sum()), smallest_decisive_kl=float(kl["base"][dec].min()),
                             **{("decisive_positions" + name[8:] if name.startswith("decisive") else "positions_" + name): int(v.sum())
                                for name, v in sets.items() if name not in ("all", "decisive")},
                             smallest_decisive_kl_after_cue=float(kl["base"][dec_ac].min()),
                             share_of_decisive_kl_on_cue=float(kl["base"][dec & ~keep].sum() / kl["base"][dec].sum()))
        same = lambda k: {"max_abs_kl_difference": float(np.abs(kl[k] - kl["base"]).max()), "top1_differ": int((top[k] != top["base"]).sum())}
        none_diff[c] = same("none")
        if a.bias:
            zero_diff[c] = same("bias_zero")
        npz |= {f"{c}_kl": np.stack([kl[k] for k in ["base", *order]]).astype(np.float32), f"{c}_offsets": off, f"{c}_decisive": dec,
                f"{c}_decisive_after_cue": dec_ac}
        r = int(np.argmax([dec_ac[off[j]:off[j + 1]].sum() for j in range(len(sel[c]))]))
        q, lo = sel[c][r], off[r]
        pos = [j for j in np.argsort(-kl["base"][lo:off[r + 1]], kind="stable") if dec_ac[lo + j]][:N_EXAMPLES]
        examples[c] = {"problem_index": q["idx"], "decisive_positions_in_row": int(dec_ac[lo:off[r + 1]].sum()), "positions": [
            {"position": int(j), "context": decode(q["ids"][max(0, q["n_prompt"] + j - CONTEXT):q["n_prompt"] + j]),
             "written": decode([q["ids"][q["n_prompt"] + j]]), **{f"top1_token_{k}": decode([int(top[k][lo + j])]) for k in ("rl", "base", *ex_arms)},
             "kl_rl_base": float(kl["base"][lo + j]), **{f"kl_rl_{k}": float(kl[k][lo + j]) for k in ex_arms}} for j in pos]}
    np.savez_compressed(out / "kl.npz", **npz)
    M5.dump(out / "examples.json", examples)

    all_kl = {c: m["arms"]["all"]["cells"][c]["mean_kl_all"] for c in cells}
    m["controls"] = {"all": {"mean_kl": all_kl, "below": ALL_KL_TOL, "pass": all(v < ALL_KL_TOL for v in all_kl.values())},
                     "none": {**none_diff, "pass": all(v["max_abs_kl_difference"] == 0 and v["top1_differ"] == 0 for v in none_diff.values())},
                     "undo": {"checks": undo_checks, "failed": undo_failed, "arms_that_change_no_bit": [k for k in order if not check[k][0]],
                              "pass": undo_checks > 0 and not undo_failed}}
    if a.bias:
        m["controls"]["bias_zero"] = {**zero_diff, "pass": all(v["max_abs_kl_difference"] == 0 and v["top1_differ"] == 0 for v in zero_diff.values())}
    if attr is not None:
        L_a, a64, top_sets = {k: v / half_a["n"] for k, v in half_a["sum"].items()}, attr.astype(np.float64), {}
        for k in order:
            mlp_only = edits[k].get("copy_families", ["mlp"]) == ["mlp"]
            mask = N.neuron_mask(edits[k], L, W).numpy()
            m["attr"].setdefault("arms", {})[k] = {"predicted_drop": float(a64[mask].sum()) if mlp_only else None, "measured_drop": L_a["base"] - L_a[k]}
            if k.startswith("attr") and "top" + k[4:] in order:
                m["attr"]["arms"][k]["neurons_shared_with_top"] = int((mask & N.neuron_mask(edits["top" + k[4:]], L, W).numpy()).sum())
        m["attr"].update(L_half_A=L_a["base"], decisive_positions_half_A_scoring_pass=half_a["n"])
        a1 = m["attr"]["arms"]["attr1"]
        m["controls"]["attr"] = {"L_half_A": L_a["base"], "attr1_predicted_drop": a1["predicted_drop"], "attr1_measured_drop": a1["measured_drop"],
                                 "decisive_positions_as_ranked": bool(half_a["same"]), "pass": a1["measured_drop"] > 0 and bool(half_a["same"])}
    sec = time.time() - t_run
    m.update(status="done", wall_s=time.time() - t0, pass_s=sec, forward_tokens=n_forward, forward_tokens_per_s=n_forward / max(sec, 1e-9))
    M5.dump(out / "metrics.json", m)
    if a.dry_run:                                                 # the edit files through the Part G build, on the tiny pair
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            b2, r2 = N.saved_pair(tmp)
            x = torch.tensor(sel[cells[0]][0]["ids"][:64])[None]
            m["dry_run_builds"] = {}
            for k in edit_files:
                rep = N.roundtrip(b2, r2, tmp / "base", tmp / "rl", json.loads((out / f"edit_{k}.json").read_text()), tmp / k, x)
                m["dry_run_builds"][k] = {"shards_rewritten": len(rep["shards_rewritten"]), "entries_differ": rep["diff"]["entries_differ"]}
    else:
        m["gpu_max_memory_gb"] = torch.cuda.max_memory_allocated() / 2 ** 30
    M5.dump(out / "metrics.json", m)
    key = "closure_decisive_after_cue" + ("_half_B" if split else "")
    closure = {k: {c: round(v["cells"][c][key], 4) for c in cells} for k, v in m["arms"].items()}
    print(json.dumps({"controls": m["controls"], "wall_s": m["wall_s"], "pass_s": sec, "base": m["base"]}, indent=1), flush=True)
    print(f"{key}:\n" + "\n".join(f"  {k:12s} {v}" for k, v in closure.items()), flush=True)
    failed = [k for k, v in m["controls"].items() if not v["pass"]]
    assert not failed, f"controls failed: {failed} (see metrics.json)"


if __name__ == "__main__":
    main()
