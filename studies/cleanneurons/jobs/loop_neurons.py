"""cleanneurons Part L (specs/SPEC1.md): MLP neurons that make the Olmo 3 base loop, found with the base only, and switched
off. One H100, the base in bf16, on the team runner:

    uv run tools/gpu.py submit h100 --hours 1 -- "python -m studies.cleanneurons.jobs.loop_neurons --commit $(git rev-parse HEAD)"
    smoke: add  --rows 12 --steps 600 --conditions none,attr100,mask860 --normal 8 --min-loops 2
    laptop: uv run --no-project --with torch --with transformers==5.22.2 --with numpy python -m studies.cleanneurons.jobs.loop_neurons \
            --dry-run --commit <sha> --out <new dir> --steps 420 --tail 120 --back 4 --cont 320 --normal 6 --kl-max 0.5
    loops from saved answers instead of the K rows: add  --answers /runs/<run_cell job id>/answers.jsonl --max-loops 40
            (laptop: add --answers synthetic --chunk 16 to the dry run)

Inputs: studies/rlneurons/data/rln4 (k.json: the 78 K rows; own_prefix_ids already starts with the three cue ids, so a row's
context is prompt_ids.json ids[problem_index] + own_prefix_ids), and /runs/inputs/rln5/T1.jsonl (sha256 and size asserted
against data/rln5/map_inputs.json) for the normal text: the rows with 500 <= n_new <= 3,000 that are not cap hits and are
right under the first of score_v3, score_v2, score that the row carries, sorted by problem index, --normal evenly spaced.

Steps (sampling T 0.6, top-p 1.0, noise a function of (seed, problem index, step); lib/loops.py):
  1 each K row is continued for up to --steps tokens; a row that the detector flags is continued to --tail tokens after its
    onset and then stopped. Looped rows, sorted by problem index, alternate between half A (ranking) and half B (held out).
    With --answers nothing is generated: the file holds the rows of a studies.rlneurons.jobs.run_cell run (base, cue,
    MATH-500; one row per problem). Each answer is turned into prompt + cue + generated tokens with rln5_map.build (rows whose
    re-tokenized count differs from n_new by more than 1 % are left out and counted); the detector scans all its generated
    tokens and the first position at which it fires gives the row's onset and period. A looped row keeps its tokens up to
    --tail after the onset; its context (n_context) is prompt + cue, so the noise step of a token is its index among the
    generated ones, as in the K route. metrics.json compares the token detector with the rows' loop_A.
  2 half A, one window per row: up to 3,000 tokens ending --tail tokens after the onset; when the row is longer, the window is
    the prompt followed by the last 3,000 - prompt tokens before that end, so the model always sees the problem (the token
    right after the prompt is then scored in no set). Loop positions: the tokens from
    onset + period on; normal positions: as many, drawn after the prompt and before the onset (the loop positions are
    subsampled when fewer normal ones exist). m = sum of log P(token) over a set; attribution = a * dm/da summed over the
    set's prediction positions. attr = mean over rows of the loop attribution - |mean of the normal attribution|;
    act = (mean a at loop positions - mean a at normal positions) / pooled standard deviation, ranked by |act|.
  3 conditions: none; attr{K}, act{K} (zero the top K); rnd{K}_s{seed} (as many neurons per layer as attr{K}, drawn uniformly);
    mask{K} (per position and layer keep the K largest |a|); rndmask{K} (keep K random ones; its draws depend on the batch).
    For each: half B restarted --back tokens before the onset (at the first generated token when the onset is earlier) and
    continued --cont tokens with the same noise, the restart context run under the intervention too; and teacher forcing on
    the normal rows, every position after the prompt.
  4 the attr/act set with the lowest held-out loop rate among those with normal-text KL below --kl-max (0.01 nats) ->
    edit_loop.json.

Outputs in --out (default $OUT_DIR):
  metrics.json     config, commit, job id, model, seconds per stage, loops (source, rows, looped, halves), answers (--answers:
                   rows, left out, cap hits, loop_A, token_detector, both, loop_A_only, token_detector_only), windows (per half-A row:
                   positions per set, m_loop, m_norm), conditions (per condition: kind, k, neurons, heldout {n, looped, rate,
                   stopped}, normal {kl = mean KL(base || condition) in nats, logprob = mean log-prob of the written token,
                   logprob_change, loss_change_relative, positions}), selected, controls
  loops.json       {"detector", "rows"}; per K row: problem_index, n_prompt, n_context, n_generated, end, looped; a looped row
                   also has half, ids (prompt + prefix + everything generated), onset and flagged_at (positions in ids),
                   period, text_before (the 300 characters before the onset) and text_loop (the text from the onset on)
  rank.npz         float32 [layers, neurons]: attr, act, attr_loop, attr_norm (mean attributions), mean_loop, mean_norm (mean a)
  edit_<condition>.json   {"name", "zero": {"<layer>": [neuron, ...]}} for every zero condition; edit_loop.json the selected one
  heldout.json     per condition and half-B row: restart, end, flag, the continuation's token ids
  examples.json    under the selected edit (or, with none selected, the attr/act set with the lowest loop rate): one held-out
                   row that stopped looping and one that did not, with the text before the restart and both continuations

Controls (the job writes every file, then fails if one fails): the detector flags a planted loop and none of the first 20
normal answers; the shortest context's next-token distribution is the same alone and left-padded in a batch with a sequence
longer than the sliding window (KL at most 5e-3 nats; skipped with --batch 1, which pads nothing); the buffer cache gives the
logits of transformers' DynamicCache on that sequence; `none` restarted reproduces its own continuation token for token
(skipped with --answers: those answers were sampled by vLLM with other noise)
(bf16 rounding differs between a context fed in chunks and one fed token by token, so this one can fail on the GPU without a
bug: metrics.json holds the rows and the first differing token); zeroing through the hook and through the weights gives the
same logits, and the weights come back bit for bit.
Fewer than --min-loops looped rows: loops.json and metrics.json are written and the job fails.

--dry-run: a random 4-layer Olmo3ForCausalLM (64 neurons per layer, vocabulary 64, sliding window 48) and synthetic rows on
the CPU, with K scaled to 64 neurons; no download. Fail loud: no try/except, no fallback.
"""
from __future__ import annotations

import argparse
import collections
import contextlib
import json
import os
import pathlib
import re
import time
import types

import numpy as np
import torch

from studies.cleanneurons.lib import loops as L
from studies.rlneurons.jobs.rln5_map import build, dump, load, sha, utc
from studies.rlneurons.lib import n13_score as S

RLN = pathlib.Path(__file__).resolve().parents[2] / "rlneurons" / "data"
TEMP, WIN = 0.6, 3000
KS = {"zero": (10, 100, 1000), "rnd": (100, 1000), "mask": (3300, 1100, 860, 330), "rndmask": (860,)}
KS_DRY = {"zero": (2, 4, 8), "rnd": (4, 8), "mask": (48, 24, 16, 8), "rndmask": (16,)}
GRADE_FIELDS = ("score_v3", "score_v2", "score")
PAD_KL_TOL, CACHE_TOL, EQ_TOL = 5e-3, 1e-3, 1e-4      # padding: 1.08e-3 measured in bf16 on the H200 smoke (base against RL is 0.06 to 0.09)
REPRO_TOKENS = 20                                      # none_reproduces: bf16 rounding (one chunk against token by token) may flip a near-tie later


# ------------------------------------------------------------------------------------------------ inputs
def read_inputs(a, fz, tok):
    """The K rows (shortest prefix first) and the normal rows; each a dict with idx, n_prompt and ids (K rows: ctx)."""
    n13 = json.loads((RLN / "rln4" / "prompt_ids.json").read_text())
    assert n13["pair"] == "pair1" and sha(RLN / "rln4" / "k.json") == fz["sha256"]["k.json"]
    rows = []
    for r in sorted(json.loads((RLN / "rln4" / "k.json").read_text())["rows"], key=lambda r: (r["L"], r["problem_index"]))[:a.rows]:
        cue, pre = fz["prefill_ids"], r["own_prefix_ids"]
        assert pre[:len(cue)] == cue and len(pre) == r["L"], ("own prefix", r["problem_index"])
        rows.append({"idx": r["problem_index"], "n_prompt": len(n13["ids"][r["problem_index"]]), "ctx": n13["ids"][r["problem_index"]] + pre})
    p, f = pathlib.Path(a.inputs) / "T1.jsonl", json.loads((RLN / "rln5" / "map_inputs.json").read_text())["files"]["T1.jsonl"]
    assert p.stat().st_size == f["bytes"] and sha(p) == f["sha256"], f"{p} differs from data/rln5/map_inputs.json"
    assert sha(RLN / "rln4" / "math500.json") == fz["sha256"]["math500.json"]
    math = json.loads((RLN / "rln4" / "math500.json").read_text())
    t1 = [json.loads(l) for l in p.read_text().splitlines()]
    field = next((k for k in GRADE_FIELDS if k in t1[0]), None)
    assert field is None or all(field in r for r in t1)
    cand = sorted((r for r in t1 if 500 <= r["n_new"] <= 3000 and not r["cap_hit"] and (field is None or r[field] == 1)), key=lambda r: r["problem_index"])
    assert len(cand) >= a.normal, f"{len(cand)} normal candidates, {a.normal} asked"
    pick = [cand[int(round(x))] for x in np.linspace(0, len(cand) - 1, a.normal)]
    normal = [build(tok, fz, r, math[r["problem_index"]], n13["ids"][r["problem_index"]]) for r in pick]
    return rows, normal, {"grade_field": field, "candidates": len(cand), "problem_indices": [s["idx"] for s in normal]}


def read_answers(path, n, encode, tail):
    """--answers: the file's rows (the first n by problem index) as step-1 rows: ctx = prompt + cue, gen = the generated tokens
    (a looped row: up to `tail` after its onset), flag = the detector's first firing on all generated tokens; and the counts
    that compare the token detector with loop_A. encode(row) is rln5_map.build's dict."""
    raw = [json.loads(l) for l in pathlib.Path(path).read_text().splitlines()]
    for r in raw:
        r.setdefault("problem_index", r.get("idx"))
    raw = sorted(raw, key=lambda r: r["problem_index"])[:n]
    assert len({r["problem_index"] for r in raw}) == len(raw), "more than one row per problem (samples or restarts): not handled"
    rows, left, both = [], [], collections.Counter()
    for r in raw:
        s = encode(r)
        if abs(s["retok_diff"]) > 0.01 * s["n_new"]:
            left.append(s["idx"])
            continue
        n_ctx = s["n_prompt"] + s["n_cue"]
        gen = s["ids"][n_ctx:len(s["ids"]) - s["has_stop"]]
        hit = L.scan(gen)
        both[bool(r["loop_A"]), hit is not None] += 1
        rows.append({"idx": s["idx"], "n_prompt": s["n_prompt"], "ctx": s["ids"][:n_ctx], "gen": gen[:max(hit[0], hit[2] + tail)] if hit else gen,
                     "end": "loop" if hit else "steps" if r["cap_hit"] else "stop", "flag": hit and {"n": hit[0], "period": hit[1], "onset": hit[2]},
                     "loop_A": bool(r["loop_A"]), "cap_hit": bool(r["cap_hit"]), "answer_tokens": len(gen)})
    return rows, {"file": str(path), "sha256": sha(path), "rows": len(raw), "left_out_retokenized": left, "cap_hits": sum(r["cap_hit"] for r in rows),
                  "loop_A": both[True, True] + both[True, False], "token_detector": both[True, True] + both[False, True], "both": both[True, True],
                  "loop_A_only": both[True, False], "token_detector_only": both[False, True], "neither": both[False, False]}


def answer_encoder(fz, tok):
    n13, math = json.loads((RLN / "rln4" / "prompt_ids.json").read_text()), json.loads((RLN / "rln4" / "math500.json").read_text())
    return lambda r: build(tok, fz, r, math[r["problem_index"]], n13["ids"][r["problem_index"]])


def dry_answers(a, model, path, gen, stop_id):
    """--dry-run --answers: writes a synthetic run_cell file (prompt and text as space-separated ids): the stand-in's own
    continuations of random prompts, --steps tokens each; loop_A is the token detector's verdict, flipped on every fifth row;
    one row states a wrong n_new. Returns the encoder for its rows."""
    g, join = np.random.default_rng(2), lambda ids: " ".join(map(str, ids))
    ctx = [g.integers(0, model.config.vocab_size - 2, 11).tolist() for _ in range(a.rows or 30)]
    res = L.generate_rows(model, [{"ctx": c, "key": i, "step0": 0} for i, c in enumerate(ctx)], a.steps, tail=a.steps, **gen)
    path.write_text("".join(json.dumps({"problem_index": 3 * i + 1, "prompt": join(c[:8]), "n_prefix": 3, "text": join(c[8:] + r["tokens"]), "cap_hit": r["end"] != "stop",
                                        "loop_A": bool(r["flag"]) != (i % 5 == 0), "n_new": len(r["tokens"]) + 40 * (i == 2)}) + "\n" for i, (c, r) in enumerate(zip(ctx, res))))

    def encode(r):
        ids, text = [int(x) for x in r["prompt"].split()], [int(x) for x in r["text"].split()]
        return {"idx": r["problem_index"], "ids": ids + text + [stop_id] * (not r["cap_hit"]), "n_prompt": len(ids), "n_cue": r["n_prefix"],
                "has_stop": int(not r["cap_hit"]), "n_new": r["n_new"], "retok_diff": len(text) - r["n_prefix"] - r["n_new"]}
    return encode


def dry_inputs(a, vocab):
    g = np.random.default_rng(1)
    ids = lambda n: g.integers(0, vocab - 2, int(n)).tolist()
    rows = [{"idx": 3 * i + 1, "n_prompt": 8, "ctx": ids(8) + ids(g.integers(20, 90))} for i in range(a.rows or 24)]
    normal = [{"idx": i, "n_prompt": 8, "ids": ids(g.integers(300, 420))} for i in range(a.normal)]
    return rows, normal, {"grade_field": None, "dry_run": True}


def stand_in(vocab):
    """--dry-run model: random Olmo3ForCausalLM, 3 sliding layers and 1 full one. The attention output is scaled down and the
    output logits up, so the next token is nearly a function of the current one and sampled text falls into loops."""
    from transformers import Olmo3Config, Olmo3ForCausalLM
    torch.manual_seed(0)
    cfg = Olmo3Config(vocab_size=vocab, hidden_size=16, intermediate_size=64, num_hidden_layers=4, num_attention_heads=2,
                      max_position_embeddings=4096, sliding_window=48, pad_token_id=vocab - 2, eos_token_id=vocab - 1)
    model = Olmo3ForCausalLM(cfg).eval()
    with torch.no_grad():
        for p in model.parameters():
            if p.ndim == 2:
                p.normal_(0, 1)
        for layer in model.model.layers:
            layer.post_attention_layernorm.weight.fill_(0.1)
        model.lm_head.weight.mul_(1.5)
    return model


# ------------------------------------------------------------------------------------------------ controls
@torch.inference_mode()
def pad_control(model, short, long, pad_id, chunk, cache):
    """`short` alone against `short` left-padded in a batch with `long`: KL of the next-token distribution after the context
    and after one more cached step (the row's last token fed again)."""
    def run(rows):
        ids, mask = L.left_pad(rows, pad_id, 1, L.device(model))
        kv = L.new_cache(model, mask.shape[1], cache, chunk)
        first = torch.log_softmax(L.last_logits(model, ids, mask[:, :-1], kv, chunk), -1)[0]
        return first, torch.log_softmax(L.last_logits(model, ids[:, -1:], mask, kv, chunk), -1)[0]
    kl = lambda p, q: float((p.exp() * (p - q)).sum())
    alone, padded = run([short]), run([short, long])
    out = {"tokens": [len(short), len(long)], "kl_after_context": kl(alone[0], padded[0]), "kl_after_step": kl(alone[1], padded[1]),
           "max_abs_logprob_difference": float(max((x - y).abs().max() for x, y in zip(alone, padded))), "tolerance_kl": PAD_KL_TOL}
    out["pass"] = max(out["kl_after_context"], out["kl_after_step"]) <= PAD_KL_TOL
    return out


@torch.inference_mode()
def cache_control(model, seq, chunk):
    """The buffer cache against transformers' DynamicCache on one sequence: the logits after all but 8 tokens fed in chunks
    and after each of the last 8 fed one by one."""
    x, n, lg = torch.tensor(seq, device=L.device(model))[None], len(seq) - 8, []
    for kind in ("buffer", "dynamic"):
        kv = L.new_cache(model, len(seq), kind, chunk)
        one = torch.ones_like(x)
        lg.append(torch.cat([L.last_logits(model, x[:, :n], one[:, :n], kv, chunk)] + [L.last_logits(model, x[:, i:i + 1], one[:, :i + 1], kv, chunk) for i in range(n, len(seq))]))
    d = float((lg[0] - lg[1]).abs().max())
    return {"tokens": len(seq), "max_abs_logit_difference": d, "tolerance": CACHE_TOL, "pass": d <= CACHE_TOL}


@torch.inference_mode()
def zero_control(model, ids, sets):
    """One window: the logits with the neurons zeroed by the hook and by the weight edit, and the weights after the edit is undone."""
    x = torch.tensor(ids, device=L.device(model))[None]
    w = L.mlps(model)[int(next(iter(sets)))].down_proj.weight
    before = w.clone()
    base = model(input_ids=x, use_cache=False).logits[0].float()
    with L.zero(model, sets):
        hook = model(input_ids=x, use_cache=False).logits[0].float()
    with L.zero_weights(model, sets):
        edited = not torch.equal(w, before)
        weights = model(input_ids=x, use_cache=False).logits[0].float()
    out = {"tokens": len(ids), "neurons": sum(len(v) for v in sets.values()), "max_abs_logit_difference_hook_weights": float((hook - weights).abs().max()),
           "max_abs_logit_change_from_base": float((hook - base).abs().max()), "weights_changed_inside": edited,
           "weights_restored_bit_for_bit": bool(torch.equal(w, before)), "tolerance": EQ_TOL}
    out["pass"] = (out["max_abs_logit_difference_hook_weights"] <= EQ_TOL and out["max_abs_logit_change_from_base"] > 0 and edited
                   and out["weights_restored_bit_for_bit"])
    return out


# ------------------------------------------------------------------------------------------------ step 2: ranking
def window(r, tail):
    """The window's ids and the prediction positions inside it (the logits at q score token q + 1) of the loop and normal sets.
    The window ends `tail` tokens after the onset; a row longer than WIN gives the prompt + the last WIN - prompt tokens."""
    full, o, p, n0 = r["ctx"] + r["gen"], len(r["ctx"]) + r["flag"]["onset"], r["flag"]["period"], r["n_prompt"]
    end = min(o + tail, len(full))
    start = 0 if end <= WIN else end - (WIN - n0)           # tokens start..end follow the prompt; start itself is scored in no set
    shift = start - n0 if start else 0                      # token i >= start sits at window index i - shift
    loop, norm = np.arange(max(o + p, start + 1), end), np.arange(max(n0, start + 1), o)
    n = min(len(loop), len(norm))
    assert n > 0, ("no loop or no normal position", r["idx"], len(loop), len(norm))
    g = np.random.default_rng(r["idx"])
    return (full[:n0] if start else []) + full[start:end], {"loop": np.sort(g.choice(loop, n, replace=False)) - 1 - shift,
                                                            "norm": np.sort(g.choice(norm, n, replace=False)) - 1 - shift}


def attribute(model, ids, sets):
    """One forward pass over the window and one backward pass per set. Per set: m, attr [layers, neurons] = sum over the set's
    positions of a * dm/da, and the sum and the sum of squares of a over them."""
    x = torch.tensor(ids, device=L.device(model))[None]
    emb = model.get_input_embeddings()(x).detach().requires_grad_(True)       # the parameters need no gradient; the graph starts here
    with L.capture(model) as acts:
        logits = model(inputs_embeds=emb, use_cache=False).logits[0]
    out = {}
    for i, (name, q) in enumerate(sets.items()):
        q = torch.as_tensor(q, device=x.device)
        m = torch.log_softmax(logits[q].float(), -1).gather(1, x[0, q + 1, None]).sum()
        grads = torch.autograd.grad(m, acts, retain_graph=i + 1 < len(sets))
        a = [t.detach()[0, q].float() for t in acts]
        out[name] = {"m": float(m.detach()), "attr": torch.stack([(t * g[0, q].float()).sum(0) for t, g in zip(a, grads)]).cpu().numpy(),
                     "sum": torch.stack([t.sum(0) for t in a]).double().cpu().numpy(), "sq": torch.stack([(t * t).sum(0) for t in a]).double().cpu().numpy()}
        assert np.isfinite(out[name]["attr"]).all(), "non-finite attribution"
    return out


def top(score, k):
    """The k neurons with the largest score as {"<layer>": [neuron, ...]}."""
    sets = collections.defaultdict(list)
    for i in np.argsort(-score.ravel(), kind="stable")[:k]:
        sets[int(i) // score.shape[1]].append(int(i) % score.shape[1])
    return {str(l): sorted(sets[l]) for l in sorted(sets)}


def matched(sets, neurons, seed):
    """As many neurons per layer as `sets`, drawn uniformly without replacement."""
    g = np.random.default_rng(seed)
    return {l: sorted(int(n) for n in g.choice(neurons, len(ns), replace=False)) for l, ns in sets.items()}


def intervention(model, c, seed):
    if c["kind"] == "zero":
        return L.zero(model, c["zero"])
    if c["kind"] in ("mask", "rndmask"):
        return L.keep_k(model, c["k"], seed if c["kind"] == "rndmask" else None)
    assert c["kind"] == "none"
    return contextlib.nullcontext()


@torch.inference_mode()
def logprobs(model, s):
    """Float32 log-probabilities at every position after the prompt of one sequence: [positions, vocabulary]."""
    x = torch.tensor(s["ids"][:-1], device=L.device(model))[None]
    return torch.log_softmax(model(input_ids=x, use_cache=False).logits[0, s["n_prompt"] - 1:].float(), -1)


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", default="/runs/inputs/rln5")
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--commit", required=True, help="the submitted commit: $(git rev-parse HEAD), expanded on the laptop")
    ap.add_argument("--rows", type=int, default=None, help="only the n K rows with the shortest prefix (they loop soonest); --answers: the first n answers")
    ap.add_argument("--answers", default=None, help="a run_cell answers.jsonl: the looped rows come from it and step 1 generates nothing")
    ap.add_argument("--max-loops", type=int, default=None, help="use at most this many looped rows, evenly spaced by problem index")
    ap.add_argument("--steps", type=int, default=2500, help="step 1: tokens per row at most")
    ap.add_argument("--tail", type=int, default=1000, help="a flagged row runs to this many tokens after its onset; the ranking window ends there")
    ap.add_argument("--back", type=int, default=300, help="step 3: restart this many tokens before the onset")
    ap.add_argument("--cont", type=int, default=800, help="step 3: tokens after the restart")
    ap.add_argument("--normal", type=int, default=40, help="normal-text rows")
    ap.add_argument("--conditions", default=None, help="comma list of condition names; default all; none always runs")
    ap.add_argument("--kl-max", type=float, default=0.01, help="step 4: normal-text KL (nats) a selected set stays below")
    ap.add_argument("--min-loops", type=int, default=8)
    ap.add_argument("--batch", type=int, default=16, help="rows per batch at most; 1 pads nothing")
    ap.add_argument("--kv-gb", type=float, default=50.0, help="KV cache per batch at most")
    ap.add_argument("--chunk", type=int, default=1024, help="context tokens per forward pass")
    ap.add_argument("--cache", default="buffer", choices=("buffer", "dynamic"))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    assert a.out, "no --out and no $OUT_DIR"
    assert a.min_loops >= 2, "one looped row for the ranking and one held out at least"
    assert a.max_loops is None or a.max_loops >= a.min_loops, "--max-loops below --min-loops"
    assert re.fullmatch(r"[0-9a-f]{40}", a.commit), f"--commit {a.commit!r} is not a full git sha"
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / "metrics.json").exists(), f"{out}/metrics.json exists: one fresh directory per run"
    m = {"status": "loading", "config": {**vars(a), "out": str(out), "temperature": TEMP, "top_p": 1.0, "window": WIN,
                                    "window_rule": "the row up to --tail after the onset; longer than the window: prompt + the last window - prompt tokens"},
         "commit": a.commit, "job_id": os.environ.get("JOB_ID"), "started_utc": utc(), "torch": torch.__version__, "seconds": {}, "controls": {}}
    clock = [time.time()]

    def lap(name):
        m["seconds"][name] = round(time.time() - clock[0], 1)
        clock[0] = time.time()
        print(f"{utc()} {name}: {m['seconds'][name]} s", flush=True)
        dump(out / "metrics.json", m)

    assert L.selfcheck()
    if a.dry_run:
        vocab, ks = 64, KS_DRY
        model, stop_id, tok = stand_in(vocab), vocab - 1, types.SimpleNamespace(decode=lambda ids, **_: " ".join(map(str, ids)))
        rows, normal, m["normal_rows"] = dry_inputs(a, vocab)
        m["model"] = {"dry_run": True, "class": type(model).__name__}
    else:
        from huggingface_hub import snapshot_download
        from transformers import AutoTokenizer
        fz, ks, stop_id = json.loads((RLN / "rln4" / "frozen4.json").read_text()), KS, S.STOP_ID
        tok = AutoTokenizer.from_pretrained(snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"]))
        assert tok.decode(fz["prefill_ids"]) == fz["prefill_text"]
        rows, normal, m["normal_rows"] = read_inputs(a, fz, tok)
        model, m["model"] = load(fz, "base", "cuda")
        m["gpu"] = torch.cuda.get_device_name(0)
    model.requires_grad_(False)
    layers, neurons = L.check_model(model)
    assert a.dry_run or (layers, neurons) == (32, 11008), (layers, neurons)
    pad_id, dev = model.config.pad_token_id, L.device(model)
    assert pad_id is not None and stop_id < model.config.vocab_size
    gen = {"temp": TEMP, "seed": a.seed, "stop_id": stop_id, "pad_id": pad_id, "chunk": a.chunk, "cache": a.cache, "batch": a.batch,
           "kv_budget": int(a.kv_gb * 2 ** 30)}
    m["model"].update(layers=layers, neurons=neurons, kv_bytes_per_token=L.kv_bytes(model), sliding_window=model.config.sliding_window,
                      layer_types=dict(collections.Counter(model.config.layer_types)), pad_id=pad_id, stop_id=stop_id)
    m["status"] = "running"
    lap("load")

    # controls that need no result: detector, padding, cache
    by_len = sorted(rows, key=lambda r: len(r["ctx"]))
    two, span = by_len[-1]["ctx"] + by_len[-2]["ctx"], model.config.sliding_window + 600
    long = (two * (span // len(two) + 1))[:span]                               # two contexts, repeated to pass the sliding window
    flagged = [s["idx"] for s in normal[:20] if L.scan(s["ids"][s["n_prompt"]:]) is not None]
    m["controls"]["detector"] = {"planted_loop_flagged": True, "normal_answers": len(normal[:20]), "normal_answers_flagged": flagged, "pass": not flagged}
    m["controls"]["padding"] = pad_control(model, by_len[0]["ctx"], long, pad_id, a.chunk, a.cache) if a.batch > 1 else {"skipped": "--batch 1", "pass": None}
    m["controls"]["cache"] = cache_control(model, long, a.chunk)
    lap("controls_before")

    # step 1: loops, generated from the K rows or read from saved answers
    if a.answers:
        path = out / "answers.jsonl" if a.dry_run else pathlib.Path(a.answers)
        encode = dry_answers(a, model, path, gen, stop_id) if a.dry_run else answer_encoder(fz, tok)
        rows, m["answers"] = read_answers(path, a.rows, encode, a.tail)
    else:
        res = L.generate_rows(model, [{"ctx": r["ctx"], "key": r["idx"], "step0": 0} for r in rows], a.steps, tail=a.tail, **gen)
        for r, g in zip(rows, res):
            r.update(gen=g["tokens"], end=g["end"], flag=g["flag"])
    looped = sorted((r for r in rows if r["flag"]), key=lambda r: r["idx"])
    if a.max_loops and len(looped) > a.max_loops:
        looped = [looped[int(round(x))] for x in np.linspace(0, len(looped) - 1, a.max_loops)]
    for i, r in enumerate(looped):
        r["half"] = "AB"[i % 2]
    recs = []
    for r in sorted(rows, key=lambda r: r["idx"]):
        recs.append({"problem_index": r["idx"], "n_prompt": r["n_prompt"], "n_context": len(r["ctx"]), "n_generated": len(r["gen"]), "end": r["end"], "looped": bool(r["flag"]),
                     **{k: r[k] for k in ("loop_A", "cap_hit", "answer_tokens") if k in r}})
        if "half" in r:
            full, o = r["ctx"] + r["gen"], len(r["ctx"]) + r["flag"]["onset"]
            recs[-1].update(half=r["half"], onset=o, period=r["flag"]["period"], flagged_at=len(r["ctx"]) + r["flag"]["n"], ids=full,
                            text_before=tok.decode(full[max(0, o - 300):o], skip_special_tokens=False)[-300:], text_loop=tok.decode(full[o:], skip_special_tokens=False))
    dump(out / "loops.json", {"detector": {"window": L.W, "matches_needed": L.NEED, "periods": [L.PMIN, L.PMAX], "what": "onset, flagged_at: positions in ids"}, "rows": recs})
    A, B = [r for r in looped if r["half"] == "A"], [r for r in looped if r["half"] == "B"]
    m["loops"] = {"source": "answers" if a.answers else "K rows", "rows": len(rows), "looped": sum(bool(r["flag"]) for r in rows), "used": len(looped), "ended": dict(collections.Counter(r["end"] for r in rows)),
                  "generated_tokens": sum(len(r["gen"]) for r in rows), "half_A": [r["idx"] for r in A], "half_B": [r["idx"] for r in B]}
    lap("step1_loops")
    if len(looped) < a.min_loops:
        m["status"] = f"failed: {len(looped)} of {len(rows)} rows looped, fewer than --min-loops {a.min_loops}; the ranking needs loops"
        dump(out / "metrics.json", m)
        raise AssertionError(m["status"])

    # step 2: ranking on half A
    acc, m["windows"], first = {}, [], None
    for r in A:
        ids, sets = window(r, a.tail)
        first = first or ids
        w = attribute(model, ids, sets)
        for name, v in w.items():
            for k in ("attr", "sum", "sq"):
                acc[name, k] = acc.get((name, k), 0) + v[k]
        m["windows"].append({"problem_index": r["idx"], "tokens": len(ids), "positions_per_set": len(sets["loop"]), "m_loop": w["loop"]["m"], "m_norm": w["norm"]["m"]})
    n_pos = sum(w["positions_per_set"] for w in m["windows"])
    mean = {s: acc[s, "sum"] / n_pos for s in ("loop", "norm")}
    sd = np.sqrt(sum(np.maximum(acc[s, "sq"] / n_pos - mean[s] ** 2, 0) for s in ("loop", "norm")) / 2)
    rank = {"attr_loop": acc["loop", "attr"] / len(A), "attr_norm": acc["norm", "attr"] / len(A), "mean_loop": mean["loop"], "mean_norm": mean["norm"],
            "act": np.divide(mean["loop"] - mean["norm"], sd, out=np.zeros_like(sd), where=sd > 0)}
    rank["attr"] = rank["attr_loop"] - np.abs(rank["attr_norm"])
    np.savez_compressed(out / "rank.npz", **{k: v.astype(np.float32) for k, v in rank.items()})
    if not a.dry_run:
        torch.cuda.empty_cache()

    conds = {"none": {"kind": "none"}}
    for name, score in (("attr", rank["attr"]), ("act", np.abs(rank["act"]))):
        conds.update({f"{name}{k}": {"kind": "zero", "k": k, "zero": top(score, k)} for k in ks["zero"]})
    conds.update({f"rnd{k}_s{s}": {"kind": "zero", "k": k, "zero": matched(top(rank["attr"], k), neurons, [a.seed, s, k])} for k in ks["rnd"] for s in (0, 1)})
    conds.update({f"mask{k}": {"kind": "mask", "k": k} for k in ks["mask"]})
    conds.update({f"rndmask{k}": {"kind": "rndmask", "k": k} for k in ks["rndmask"]})
    for name, c in conds.items():
        if c["kind"] == "zero":
            c["neurons"], c["layers"] = sum(len(v) for v in c["zero"].values()), len(c["zero"])
            dump(out / f"edit_{name}.json", {"name": name, "zero": c["zero"]})
    if a.conditions:
        want = ["none"] + [c for c in a.conditions.split(",") if c != "none"]
        assert all(c in conds for c in want), (want, list(conds))
        conds = {c: conds[c] for c in want}
    m["conditions"] = {name: {k: v for k, v in c.items() if k != "zero"} for name, c in conds.items()}
    m["controls"]["zero_hook_equals_weight_edit"] = zero_control(model, first, top(rank["attr"], ks["zero"][-1]))
    lap("step2_ranking")

    # step 3a: held-out loop rate
    for r in B:
        r["restart"] = max(r["flag"]["onset"] - a.back, 0)
    test, held = [{"ctx": r["ctx"] + r["gen"][:r["restart"]], "key": r["idx"], "step0": r["restart"]} for r in B], {}
    for name, c in conds.items():
        t = time.time()
        with intervention(model, c, a.seed):
            res = L.generate_rows(model, test, a.cont, tail=0, **gen)
        held[name] = [{"problem_index": r["idx"], "restart": r["restart"], **g} for r, g in zip(B, res)]
        n = sum(bool(g["flag"]) for g in res)
        m["conditions"][name]["heldout"] = {"n": len(B), "looped": n, "rate": n / len(B), "stopped": sum(g["end"] == "stop" for g in res), "seconds": round(time.time() - t, 1)}
        print(f"{utc()} {name}: held-out loops {n}/{len(B)} in {time.time() - t:.0f} s", flush=True)
        dump(out / "metrics.json", m)
    dump(out / "heldout.json", held)
    pairs = [list(zip(r["gen"][r["restart"]:], h["tokens"])) for r, h in zip(B, held["none"])]      # step 1 against `none`, over the overlap
    diff = {r["idx"]: next(i for i, (x, y) in enumerate(p) if x != y) for r, p in zip(B, pairs) if any(x != y for x, y in p)}
    m["controls"]["none_reproduces"] = {"skipped": "--answers: the answers were sampled with other noise", "pass": None} if a.answers else {"rows": len(B), "identical": len(B) - len(diff), "first_difference_after_restart": diff,
                                        "tokens_compared": sum(map(len, pairs)), "first_tokens_required": REPRO_TOKENS,
                                        "pass": sum(v < REPRO_TOKENS for v in diff.values()) <= len(B) // 2}
    lap("step3_heldout")

    # step 3b: normal text, teacher forcing
    tot = {name: np.zeros(3) for name in conds}
    for s in normal:
        y = torch.tensor(s["ids"][s["n_prompt"]:], device=dev)[:, None]
        base = logprobs(model, s)
        for name, c in conds.items():
            with intervention(model, c, a.seed):
                lp = logprobs(model, s)
            tot[name] += [float((base.exp() * (base - lp)).sum()), float(lp.gather(1, y).sum()), len(y)]
    for name, (kl, lp, n) in tot.items():
        ref = tot["none"][1] / tot["none"][2]
        m["conditions"][name]["normal"] = {"kl": kl / n, "logprob": lp / n, "logprob_change": lp / n - ref, "loss_change_relative": (ref - lp / n) / -ref, "positions": int(n)}
    lap("step3_normal")

    # step 4: selection, examples
    rate = lambda name: (m["conditions"][name]["heldout"]["rate"], m["conditions"][name]["normal"]["kl"], conds[name]["k"])
    ranked = sorted((name for name in conds if re.fullmatch(r"(attr|act)\d+", name)), key=rate)
    ok = [name for name in ranked if m["conditions"][name]["normal"]["kl"] < a.kl_max]
    m["selected"] = ok[0] if ok else None
    if ok:
        dump(out / "edit_loop.json", {"name": f"loop_{ok[0]}", "zero": conds[ok[0]]["zero"]})
    ex = {"condition": ok[0] if ok else ranked[0] if ranked else None, "selected": bool(ok), "stopped_looping": None, "still_loops": None}
    text = lambda ids: tok.decode(ids, skip_special_tokens=False)
    for r, h0, h1 in zip(B, held["none"], held[ex["condition"]] if ex["condition"] else []):
        key = "still_loops" if h1["flag"] else "stopped_looping" if h0["flag"] else None
        if key and ex[key] is None:
            ex[key] = {"problem_index": r["idx"], "restart": r["restart"], "text_before": text(r["ctx"][-300:] + r["gen"][:r["restart"]])[-300:], "none": {"end": h0["end"], "flag": h0["flag"], "text": text(h0["tokens"])},
                       "edit": {"end": h1["end"], "flag": h1["flag"], "text": text(h1["tokens"])}}
    dump(out / "examples.json", ex)

    flags = {k: v["pass"] for k, v in m["controls"].items()}
    failed = [k for k, v in flags.items() if v is False]
    m.update(status=f"controls failed: {failed}" if failed else "done", wall_s=round(time.time() - t0, 1), control_flags=flags)
    if not a.dry_run:
        m["gpu_max_memory_gb"] = torch.cuda.max_memory_allocated() / 2 ** 30
    lap("step4_selection")
    print(json.dumps({"selected": m["selected"], "controls": flags, "seconds": m["seconds"], "loops": {k: m["loops"][k] for k in ("rows", "looped")},
                      "conditions": {k: {"heldout": v["heldout"]["rate"], "kl": v["normal"]["kl"]} for k, v in m["conditions"].items()}}, indent=1), flush=True)
    assert not failed, f"controls failed: {failed} (see metrics.json)"


if __name__ == "__main__":
    main()
