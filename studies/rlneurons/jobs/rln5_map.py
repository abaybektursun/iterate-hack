"""RLN-5 map (specs/SPEC5_map.md): both models' next-token distributions at every position of the 1,000 stored T1 and T2
answers. Inference only: teacher forcing, no sampling. One H100, both models in bf16, on the team runner:

    uv run tools/gpu.py submit h100 --hours 1 -- "python -m studies.rlneurons.jobs.rln5_map --commit $(git rev-parse HEAD)"
    smoke: add  --n 10 --mid 1 --long 1   (per cell: the 10 shortest answers, the one nearest 6,000 tokens, the longest)

Inputs: /runs/inputs/rln5/T1.jsonl and T2.jsonl (the Volume iterate-runs; sha256 and size asserted against
data/rln5/map_inputs.json). The rows hold text, not token ids, so the answer is re-tokenized with the RL tokenizer
(rln4_lib.encode_answer, which keeps the opening's three sampled ids). A row whose re-tokenized count differs from the
row's n_new by more than 1 % is listed in tokenize_check.json and left out of the map.

Sequence of one row: rendered prompt + cue (T1 rows) + generated tokens + the stop token (rows that are not cap hits).
Scored positions: every token after the prompt. Position kinds: 0 cue (prefilled), 1 generated, 2 stop token.

Outputs in --out (default $OUT_DIR):
  tokenize_check.json     per-row re-tokenized count against n_new; the rows left out
  <cell>_map_<kkk>.npz    shards of about --shard-positions positions, answers in order of length. Per position: tok (written
                          token id), kind, lp_base, lp_rl (log-prob of the written token), ent_base, ent_rl (entropy, nats),
                          kl_base_rl = KL(base||RL), kl_rl_base = KL(RL||base), top1_base, top1_rl, rank_base, rank_rl (rank of
                          the written token, 1 = top, capped at 100), lp_top1_base, lp_top1_rl (each model's log-prob of its own
                          top-1), lp_base_of_rl_top1, lp_rl_of_base_top1, lp_eos_base, lp_eos_rl (the stop token 100257),
                          lp_mark_base, lp_mark_rl (log of the summed probability of every vocabulary token whose string
                          contains "boxed" or "Answer"). Probabilities are stored as natural-log probabilities in float16.
                          Per row: problem_index, offsets (row r is positions offsets[r]:offsets[r+1]), n_prompt, n_cue, n_gen,
                          has_stop, n_new (the row's stored count).
  index.json              the shards written so far (rewritten after each shard; a killed job keeps every finished shard)
  identity_check.npz      the same arrays for --identity answers scored base against base
  checks.json             the four controls of SPEC5_map.md §5 with their numbers and pass flags
  metrics.json            config, commit, job id, counts, tokens per second, memory

The job writes every file, then fails if a control failed. --dry-run uses stand-in models (random fixed logits, no weights, no
GPU) to test the file pipeline on a laptop; its controls are computed and not asserted. Fail loud: no try/except, no fallback.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import time
import types

import numpy as np
import torch

from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

STUDY = pathlib.Path(__file__).resolve().parents[1]
D4, D5 = STUDY / "data" / "rln4", STUDY / "data" / "rln5"
CELLS = {"T1": "base", "T2": "rl"}                    # cell -> the model that generated it
MODELS = {"base": "base", "rl": "s2800"}              # keys of frozen4.json "models"
RANK_CAP = 100
TOL = 0.01                                            # re-tokenized count against n_new
MAX_EXCLUDED = 25                                     # per cell; more rows left out than this fails the job
MID_LEN, MID_MIN = 6000, 4500                         # the cache check needs an answer longer than the 4,096 sliding window
# control thresholds (SPEC5_map.md §5)
IDENTITY_TOL = 1e-6
CUE_RATIO = 2.0
CAL_TOL = 0.05
STORED_TOL = 0.02
CACHE_MEAN_TOL, CACHE_BIG, CACHE_BIG_SHARE = 0.02, 0.25, 0.001
F16 = ("lp_base", "lp_rl", "ent_base", "ent_rl", "kl_base_rl", "kl_rl_base", "lp_top1_base", "lp_top1_rl", "lp_base_of_rl_top1",
       "lp_rl_of_base_top1", "lp_eos_base", "lp_eos_rl", "lp_mark_base", "lp_mark_rl")
I32 = ("tok", "top1_base", "top1_rl")
U8 = ("rank_base", "rank_rl")


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def dump(path, obj):
    tmp = pathlib.Path(str(path) + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1))
    tmp.replace(path)


# ------------------------------------------------------------------------------------------------ sequences
def build(tok, fz, row, prob, n13_ids):
    pids = S.render_ids(tok, prob["problem"])
    assert pids == n13_ids and len(pids) == row["prompt_n_tokens"], ("prompt ids", row["problem_index"])
    assert row["unique_id"] == prob["unique_id"]
    ids, _ = R.encode_answer(tok, row["text"], fz["prefill_text"], fz["prefill_ids"])
    n_cue = row["n_prefix"]
    assert n_cue in (0, len(fz["prefill_ids"])) and ids[:n_cue] == fz["prefill_ids"][:n_cue], ("cue", row["problem_index"])
    stop = [] if row["cap_hit"] else [S.STOP_ID]
    n_gen = len(ids) - n_cue
    return {"idx": int(row["problem_index"]), "ids": pids + [int(i) for i in ids] + stop, "n_prompt": len(pids), "n_cue": n_cue,
            "n_gen": n_gen, "has_stop": len(stop), "n_new": int(row["n_new"]), "retok_diff": n_gen - int(row["n_new"]),
            "roundtrip": tok.decode(ids, skip_special_tokens=False) == row["text"], "stored_mean_logprob": row["mean_logprob"]}


def kinds(s):
    return np.array([0] * s["n_cue"] + [1] * s["n_gen"] + [2] * s["has_stop"], dtype=np.uint8)


# ------------------------------------------------------------------------------------------------ models
class StandIn:
    """--dry-run: logits are a fixed random function of the current token. No weights, no GPU."""

    def __init__(self, seed, vocab):
        g = torch.Generator().manual_seed(seed)
        self.E, self.W = torch.randn(vocab, 8, generator=g), 3.0 * torch.randn(8, vocab, generator=g)

    def __call__(self, input_ids, past_key_values=None, use_cache=True):
        return types.SimpleNamespace(logits=(self.E[input_ids[0]] @ self.W)[None], past_key_values=None)

    def to(self, _):
        return self


def load(fz, name, dev):
    from huggingface_hub import snapshot_download
    from transformers import AutoModelForCausalLM
    repo, _, rev = fz["models"][MODELS[name]]
    d = snapshot_download(repo, revision=rev, allow_patterns=["*.json", "*.safetensors", "*.jinja", "*.txt"])
    m = AutoModelForCausalLM.from_pretrained(d, dtype=torch.bfloat16).to(dev).eval()
    assert next(m.parameters()).dtype == torch.bfloat16
    return m, {"repo": repo, "revision": rev, "dir": d, "class": type(m).__name__, "vocab_size": int(m.config.vocab_size)}


# ------------------------------------------------------------------------------------------------ per-position statistics
def stats(lg_a, lg_b, y, mark):
    la, lb = torch.log_softmax(lg_a.float(), -1), torch.log_softmax(lg_b.float(), -1)
    pa, pb, d = la.exp(), lb.exp(), la - lb
    ta, tb = la.argmax(-1), lb.argmax(-1)
    col = lambda l, i: l.gather(1, i[:, None])[:, 0]
    lpa, lpb = col(la, y), col(lb, y)
    return {"tok": y, "lp_base": lpa, "lp_rl": lpb, "ent_base": -(pa * la).sum(-1), "ent_rl": -(pb * lb).sum(-1),
            "kl_base_rl": (pa * d).sum(-1), "kl_rl_base": -(pb * d).sum(-1), "top1_base": ta, "top1_rl": tb,
            "rank_base": ((la > lpa[:, None]).sum(-1) + 1).clamp(max=RANK_CAP),
            "rank_rl": ((lb > lpb[:, None]).sum(-1) + 1).clamp(max=RANK_CAP),
            "lp_top1_base": col(la, ta), "lp_top1_rl": col(lb, tb), "lp_base_of_rl_top1": col(la, tb), "lp_rl_of_base_top1": col(lb, ta),
            "lp_eos_base": la[:, S.STOP_ID], "lp_eos_rl": lb[:, S.STOP_ID],
            "lp_mark_base": torch.logsumexp(la[:, mark], -1), "lp_mark_rl": torch.logsumexp(lb[:, mark], -1)}


def logit_chunks(models, x, a, dev):
    """Yields (start, logits of model 0, logits of model 1) over the inputs x in chunks of a.chunk positions."""
    n = x.shape[1]
    if a.forward == "cache":
        past = [None, None]
        for s in range(0, n, a.chunk):
            lg = []
            for k, m in enumerate(models):
                o = m(input_ids=x[:, s:s + a.chunk], past_key_values=past[k], use_cache=True)
                past[k] = o.past_key_values
                lg.append(o.logits[0])
            yield s, lg[0], lg[1]
        return
    full = []
    for k, m in enumerate(models):                    # one pass over the whole sequence; logits stay in bf16
        other = models[1 - k]
        swap = n > a.swap_above and other is not m
        if swap:
            other.to("cpu")
            torch.cuda.empty_cache()
        full.append(m(input_ids=x, use_cache=False).logits[0])
        if swap:
            other.to(dev)
    for s in range(0, n, a.chunk):
        yield s, full[0][s:s + a.chunk], full[1][s:s + a.chunk]


@torch.inference_mode()
def score(models, s, mark, a, dev):
    """Per-position arrays for every token after the prompt of sequence s, model 0 as 'base' and model 1 as 'rl'."""
    x = torch.tensor(s["ids"][:-1], device=dev)[None]
    y = torch.tensor(s["ids"][1:], device=dev)
    first, outs = s["n_prompt"] - 1, []
    for st, lg_a, lg_b in logit_chunks(models, x, a, dev):
        lo = max(first - st, 0)
        if lo < lg_a.shape[0]:
            outs.append({k: v.cpu() for k, v in stats(lg_a[lo:], lg_b[lo:], y[st + lo:st + lg_a.shape[0]], mark).items()})
    res = {}
    for k in outs[0]:
        v = torch.cat([o[k] for o in outs])
        res[k] = v.numpy().astype(np.float16 if k in F16 else np.int32 if k in I32 else np.uint8)
    assert len(res["tok"]) == len(s["ids"]) - s["n_prompt"] == s["n_cue"] + s["n_gen"] + s["has_stop"]
    assert all(np.isfinite(res[k].astype(np.float32)).all() for k in F16), ("non-finite value", s["idx"])
    return res


@torch.inference_mode()
def oneshot_lp(m, s, dev, chunk):
    """Log-prob of the written tokens from one pass over the whole sequence with no cache."""
    x = torch.tensor(s["ids"][:-1], device=dev)[None]
    y = torch.tensor(s["ids"][1:], device=dev)
    lg = m(input_ids=x, use_cache=False).logits[0]
    out = [torch.log_softmax(lg[i:i + chunk].float(), -1).gather(1, y[i:i + chunk, None])[:, 0].cpu() for i in range(0, len(y), chunk)]
    return torch.cat(out).numpy()[s["n_prompt"] - 1:]


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", default="/runs/inputs/rln5")
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--commit", required=True, help="the submitted commit: $(git rev-parse HEAD), expanded on the laptop")
    ap.add_argument("--cells", default="T1,T2")
    ap.add_argument("--n", type=int, default=None, help="per cell: only the n shortest answers (smoke)")
    ap.add_argument("--mid", type=int, default=0, help="with --n: also the answer nearest 6,000 generated tokens")
    ap.add_argument("--long", type=int, default=0, help="with --n: also the longest answer")
    ap.add_argument("--identity", type=int, default=2, help="answers of the first cell scored base against base")
    ap.add_argument("--forward", default="cache", choices=("cache", "oneshot"))
    ap.add_argument("--swap-above", type=int, default=9000, help="oneshot: move the other model to the CPU above this length")
    ap.add_argument("--chunk", type=int, default=1024)
    ap.add_argument("--shard-positions", type=int, default=250_000)
    ap.add_argument("--check-only", action="store_true", help="tokenizer only: write tokenize_check.json and stop")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    assert a.out, "no --out and no $OUT_DIR"
    assert re.fullmatch(r"[0-9a-f]{40}", a.commit), f"--commit {a.commit!r} is not a full git sha"
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / "index.json").exists(), f"{out}/index.json exists: one fresh directory per run"
    cells = a.cells.split(",")
    assert all(c in CELLS for c in cells)

    fz = json.loads((D4 / "frozen4.json").read_text())
    frozen = json.loads((D5 / "map_inputs.json").read_text())
    assert sha(D4 / "math500.json") == fz["sha256"]["math500.json"]
    math = json.loads((D4 / "math500.json").read_text())
    assert all(int(p["index"]) == i for i, p in enumerate(math))
    n13 = json.loads((D4 / "prompt_ids.json").read_text())
    assert n13["pair"] == "pair1"
    rows = {}
    for c in cells:
        p, f = pathlib.Path(a.inputs) / f"{c}.jsonl", frozen["files"][f"{c}.jsonl"]
        assert p.stat().st_size == f["bytes"] and sha(p) == f["sha256"], f"{p} differs from data/rln5/map_inputs.json"
        rows[c] = sorted((json.loads(l) for l in p.read_text().splitlines()), key=lambda r: r["problem_index"])
        assert [r["problem_index"] for r in rows[c]] == list(range(500)) and all(r["cell"] == c for r in rows[c])
        assert all(r["sampling"] == fz["cells"][c][2] for r in rows[c])

    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer
    tok_dir = snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"])
    tok = AutoTokenizer.from_pretrained(tok_dir)
    assert tok.decode(fz["prefill_ids"]) == fz["prefill_text"]
    seqs, tcheck = {}, {"tolerance": TOL, "cells": {}}
    for c in cells:
        seqs[c] = [build(tok, fz, r, math[r["problem_index"]], n13["ids"][r["problem_index"]]) for r in rows[c]]
        bad = [s for s in seqs[c] if abs(s["retok_diff"]) > TOL * s["n_new"]]
        tcheck["cells"][c] = {"n": len(seqs[c]), "exact_count": sum(s["retok_diff"] == 0 for s in seqs[c]),
                              "text_roundtrip": sum(s["roundtrip"] for s in seqs[c]),
                              "differs": [{"problem_index": s["idx"], "n_new": s["n_new"], "retokenized": s["n_gen"]}
                                          for s in seqs[c] if s["retok_diff"]],
                              "left_out": [s["idx"] for s in bad], "stored_tokens": sum(s["n_new"] for s in seqs[c])}
        print(f"{c}: {tcheck['cells'][c]['exact_count']} of {len(seqs[c])} rows re-tokenize to the stored count; LEFT OUT (over 1 %):"
              f" {tcheck['cells'][c]['left_out']}", flush=True)
        assert len(bad) <= MAX_EXCLUDED, f"{c}: {len(bad)} rows differ by more than 1 %"
        seqs[c] = [s for s in seqs[c] if abs(s["retok_diff"]) <= TOL * s["n_new"]]
    dump(out / "tokenize_check.json", tcheck)
    if a.check_only:
        return

    sel = {}
    for c in cells:
        order = sorted(seqs[c], key=lambda s: (len(s["ids"]), s["idx"]))
        if a.n is not None:
            extra = ([min(order, key=lambda s: abs(s["n_gen"] - MID_LEN))] if a.mid else []) + ([order[-1]] if a.long else [])
            order = sorted({s["idx"]: s for s in order[:a.n] + extra}.values(), key=lambda s: (len(s["ids"]), s["idx"]))
        sel[c] = order

    vocab_tokens = tok.convert_ids_to_tokens(list(range(len(tok))))
    mark_ids = [i for i, t in enumerate(vocab_tokens) if t is not None and ("boxed" in t or "Answer" in t)]
    assert mark_ids, "no marker token in the vocabulary"
    m = {"status": "loading", "config": {**vars(a), "out": str(out)}, "commit": a.commit, "job_id": os.environ.get("JOB_ID"),
         "started_utc": utc(), "inputs": frozen["files"], "tokenizer": fz["tokenizer"], "torch": torch.__version__,
         "marker_tokens": {str(i): vocab_tokens[i] for i in mark_ids}, "stop_id": S.STOP_ID,
         "selected": {c: {"answers": len(sel[c]), "positions": sum(len(s["ids"]) - s["n_prompt"] for s in sel[c])} for c in cells}}
    import transformers
    m["transformers"] = transformers.__version__
    dump(out / "metrics.json", m)

    if a.dry_run:
        dev, vocab = "cpu", len(tok)
        model = {"base": StandIn(1, vocab), "rl": StandIn(2, vocab)}
        m["models"] = {"dry_run": True}
    else:
        dev = "cuda"
        m["gpu"] = torch.cuda.get_device_name(0)
        model, m["models"] = {}, {}
        for name in ("base", "rl"):
            model[name], m["models"][name] = load(fz, name, dev)
        vocab = m["models"]["base"]["vocab_size"]
        assert vocab == m["models"]["rl"]["vocab_size"] and max(mark_ids) < vocab and S.STOP_ID < vocab
    mark = torch.tensor(mark_ids, device=dev)
    m["load_s"] = time.time() - t0
    m["status"] = "running"
    dump(out / "metrics.json", m)
    pair = (model["base"], model["rl"])
    checks = {}

    # control 1: identity. The first cell's shortest answers scored base against base.
    ident = [score((model["base"], model["base"]), s, mark, a, dev) for s in sel[cells[0]][:a.identity]]
    cat = {k: np.concatenate([r[k] for r in ident]) for k in ident[0]}
    np.savez_compressed(out / "identity_check.npz", **cat)
    f32 = lambda v: v.astype(np.float32)
    checks["identity"] = {"answers": len(ident), "positions": int(len(cat["tok"])),
                          "max_abs_kl": float(max(np.abs(f32(cat["kl_base_rl"])).max(), np.abs(f32(cat["kl_rl_base"])).max())),
                          "max_abs_logprob_difference": float(np.abs(f32(cat["lp_base"]) - f32(cat["lp_rl"])).max()),
                          "top1_differ": int((cat["top1_base"] != cat["top1_rl"]).sum())}
    checks["identity"]["pass"] = (checks["identity"]["max_abs_kl"] <= IDENTITY_TOL and checks["identity"]["top1_differ"] == 0
                                  and checks["identity"]["max_abs_logprob_difference"] <= IDENTITY_TOL)

    # control 4b: the cached chunked pass against one pass with no cache, on an answer longer than the sliding window.
    cands = [s for c in cells for s in sel[c] if s["n_gen"] >= MID_MIN]
    if cands and a.forward == "cache":
        s = min(cands, key=lambda s: abs(s["n_gen"] - MID_LEN))
        got = score(pair, s, mark, a, dev)
        cc = {"problem_index": s["idx"], "positions": int(len(got["tok"])), "stored_mean_logprob": s["stored_mean_logprob"]}
        for name, key in (("base", "lp_base"), ("rl", "lp_rl")):
            one = oneshot_lp(model[name], s, dev, a.chunk)
            d = np.abs(one - f32(got[key]))
            g = kinds(s) == 1
            cc[name] = {"mean_abs_difference": float(d.mean()), "max_abs_difference": float(d.max()), "share_over_0.25": float((d > CACHE_BIG).mean()),
                        "mean_logprob_generated_cached": float(f32(got[key])[g].mean()), "mean_logprob_generated_oneshot": float(one[g].mean())}
            cc[name]["pass"] = cc[name]["mean_abs_difference"] <= CACHE_MEAN_TOL and cc[name]["share_over_0.25"] <= CACHE_BIG_SHARE
        cc["pass"] = cc["base"]["pass"] and cc["rl"]["pass"]
        checks["cache_against_oneshot"] = cc
    else:
        checks["cache_against_oneshot"] = {"skipped": "no selected answer of at least 4,500 tokens, or --forward oneshot", "pass": None}
    dump(out / "checks.json", checks)
    print(json.dumps(checks, indent=1), flush=True)

    index = {"shards": [], "arrays": list(F16 + I32 + U8) + ["kind"], "per_row": ["problem_index", "offsets", "n_prompt", "n_cue", "n_gen", "has_stop", "n_new"]}
    per_row, n_pos, t_run = {c: [] for c in cells}, 0, time.time()
    for c in cells:
        gen = "lp_base" if CELLS[c] == "base" else "lp_rl"
        ent = "ent_base" if CELLS[c] == "base" else "ent_rl"
        buf, k = [], 0

        def flush():
            nonlocal buf, k
            arrs = {key: np.concatenate([r[key] for _, r in buf]) for key in buf[0][1]}
            arrs["kind"] = np.concatenate([kinds(s) for s, _ in buf])
            arrs["offsets"] = np.cumsum([0] + [len(r["tok"]) for _, r in buf]).astype(np.int64)
            arrs["problem_index"] = np.array([s["idx"] for s, _ in buf], dtype=np.int32)
            for key in ("n_prompt", "n_cue", "n_gen", "has_stop", "n_new"):
                arrs[key] = np.array([s[key] for s, _ in buf], dtype=np.int32)
            name = f"{c}_map_{k:03d}.npz"
            np.savez_compressed(out / name, **arrs)
            index["shards"].append({"file": name, "cell": c, "answers": len(buf), "positions": int(len(arrs["tok"]))})
            sec = time.time() - t_run
            m["progress"] = {"positions": n_pos, "seconds": sec, "positions_per_s": n_pos / max(sec, 1e-9), "updated_utc": utc()}
            dump(out / "index.json", index)
            dump(out / "metrics.json", m)
            print(f"{utc()} {name}: {len(buf)} answers, {len(arrs['tok'])} positions; {n_pos} positions in {sec:.0f} s", flush=True)
            buf, k = [], k + 1

        for s in sel[c]:
            r = score(pair, s, mark, a, dev)
            kd = kinds(s)
            g, own = kd == 1, kd >= 1
            per_row[c].append({"problem_index": s["idx"], "n_gen": s["n_gen"], "retok_diff": s["retok_diff"],
                               "cue_logprob_base": float(f32(r["lp_base"])[kd == 0].sum()), "cue_logprob_rl": float(f32(r["lp_rl"])[kd == 0].sum()),
                               "sum_logprob_own": float(f32(r[gen])[own].sum()), "sum_entropy_own": float(f32(r[ent])[own].sum()), "n_own": int(own.sum()),
                               "mean_logprob_generated": float(f32(r[gen])[g].mean()), "stored_mean_logprob": s["stored_mean_logprob"]})
            buf.append((s, r))
            n_pos += len(r["tok"])
            if sum(len(x["tok"]) for _, x in buf) >= a.shard_positions:
                flush()
        if buf:
            flush()

    # controls 2 and 3
    if "T1" in cells:
        pb = np.exp([r["cue_logprob_base"] for r in per_row["T1"]])
        pr = np.exp([r["cue_logprob_rl"] for r in per_row["T1"]])
        checks["cue"] = {"answers": len(pb), "median_p_cue_base": float(np.median(pb)), "median_p_cue_rl": float(np.median(pr)),
                         "mean_p_cue_base": float(pb.mean()), "mean_p_cue_rl": float(pr.mean()),
                         "what": "product of the three cue tokens' probabilities after the prompt, per T1 answer"}
        checks["cue"]["pass"] = checks["cue"]["median_p_cue_rl"] >= CUE_RATIO * checks["cue"]["median_p_cue_base"]
    checks["calibration"] = {}
    for c in cells:
        pr = per_row[c]
        n = sum(r["n_own"] for r in pr)
        lp, en = sum(r["sum_logprob_own"] for r in pr) / n, sum(r["sum_entropy_own"] for r in pr) / n
        d = np.abs([r["mean_logprob_generated"] - r["stored_mean_logprob"] for r in pr])
        exact = np.array([r["retok_diff"] == 0 for r in pr])
        checks["calibration"][c] = {"model": CELLS[c], "answers": len(pr), "positions": n, "mean_logprob_written": lp, "mean_entropy": en,
                                    "logprob_plus_entropy": lp + en, "pass_entropy": abs(lp + en) <= CAL_TOL,
                                    "stored_mean_logprob": {"median_abs_difference": float(np.median(d)), "max_abs_difference": float(d.max()),
                                                            "median_abs_difference_exact_rows": float(np.median(d[exact])) if exact.any() else None,
                                                            "worst_problem_index": pr[int(d.argmax())]["problem_index"]},
                                    "pass_stored": float(np.median(d)) <= STORED_TOL}
    checks["per_row"] = per_row
    dump(out / "checks.json", checks)
    flags = {"identity": checks["identity"]["pass"], "cache_against_oneshot": checks["cache_against_oneshot"]["pass"],
             "cue": checks.get("cue", {}).get("pass"),
             **{f"calibration_entropy_{c}": checks["calibration"][c]["pass_entropy"] for c in cells},
             **{f"calibration_stored_{c}": checks["calibration"][c]["pass_stored"] for c in cells}}
    m.update(status="done", wall_s=time.time() - t0, controls=flags, counts={"positions": n_pos, "answers": sum(len(v) for v in per_row.values())})
    if not a.dry_run:
        m["gpu_max_memory_gb"] = torch.cuda.max_memory_allocated() / 2 ** 30
    dump(out / "metrics.json", m)
    print(json.dumps({"controls": flags, "wall_s": m["wall_s"], "progress": m["progress"]}, indent=1), flush=True)
    failed = [k for k, v in flags.items() if v is False]
    if a.dry_run:
        print(f"dry run: controls not asserted (failed with stand-in models: {failed})")
        return
    assert not failed, f"controls failed: {failed} (see checks.json)"


if __name__ == "__main__":
    main()
