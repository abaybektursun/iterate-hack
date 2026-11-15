"""cleanneurons Part I, items 1 to 6 (specs/SPEC1.md): what the neurons of an edit file do, next to the same number of random
neurons per layer (the reference). One H100, both models in bf16, on the team runner:

    uv run tools/gpu.py submit h100 --hours 1 -- "python -m studies.cleanneurons.jobs.describe_neurons --commit $(git rev-parse HEAD) --edit <repo path of the edit file> --loops /runs/<Part L job id>/loops.json"
    smoke: add  --smoke   (4 answers per cell, 3 looped rows per half, 64 selected neurons, 600 generated tokens)
    Without --loops the job does items 1, 2, 3 and 6 on the stored answers only (neurons.json, contexts.json, metrics.json) and
    records in metrics.json "skipped" that items 4 and 5 were left out.

Inputs
  --edit    an edit file (SPEC1 "Edit file"); the selected neurons are those under `zero` and `copy_neurons`.
  --loops   Part L's loops.json, {"detector": {"version", ...}, "rows"}. The loop detector, the sampling with per-row noise,
            the KV cache and the hooks are those of lib/loops.py; the detector version is the one in the file (2: periods up
            to 600 tokens, window max(240, period)). A row without an `onset` did not loop and is skipped. Every other row
            needs: problem_index, ids (token ids: prompt, the context Part L continued, its continuation), n_prompt (tokens of
            the prompt; positions from there on are scored), n_context (tokens before the first sampled one; the noise step
            of ids[i] is i - n_context), onset (index into ids of the first token of the first loop cycle), period, half
            ("A" ranking, "B" held out). Each (onset, period) must be what lib/loops.scan finds on ids[n_context:].
  T1.jsonl, T2.jsonl in --inputs (asserted against rlneurons/data/rln5/map_inputs.json), the Part T row rule, rln5_map.build.

A neuron's activation is a = silu(gate_proj(x)) * up_proj(x), the input of down_proj (forward pre-hook). Scored positions of a
sequence: n_prompt .. len - 2 (every input token after the prompt that has a next token). "Normal text" is the stored answers.
The two poles of a neuron are separate units: "+" is max(a, 0), "-" is max(-a, 0).

Outputs in --out (default $OUT_DIR); neurons, contexts and traces hold one unit per line:
  neurons.json      items 1, 3, 6. Per neuron: set (selected / reference), layer, neuron; pos and neg: p50, p90, p99, p99.9, max of
                    the pole over all scored positions, share_beyond_p97 (share of positions where the pole exceeds the p97 of |a|
                    over all neurons of its layer, from --sub positions per sequence); mean_abs, normal_mean, normal_sd;
                    promoted, suppressed: the 15 tokens with the largest and smallest lm_head . (norm.weight *
                    post_feedforward_layernorm.weight * down_proj[:, n]), as [token, value] (for the "-" pole the two swap; both
                    norms' input-dependent scales and the effect through later layers are ignored); rl: cosine and norm ratio
                    (RL / base) of the gate, up and down vectors, mean |a| in both models on the same text, gain (RL / base),
                    act_corr (correlation of a between the two models over positions), and pos and neg: the same quantiles,
                    maximum and share_beyond_p97 for the RL model's a on the same text (against the base's layer p97).
  contexts.json     item 2. Per neuron pole: first10 and heldout10 (the 20 positions with the largest pole activation, one per
                    answer where possible, ranks alternating between the two lists) and random10 (one random scored position in
                    the answer of each heldout10 context). A context: text (60 tokens before, <<the token>>, 20 after),
                    activation (a, signed, base), activation_rl (the RL model's a of the same neuron at the same position),
                    next_token, source (T1, T2, loop), problem_index, position, onset_offset (loop rows).
  onset_trace.json  item 4. offsets -200 .. +400 from the loop onset (offset 0 reads the first token of the first cycle; the
                    repeated text starts one period later); per set, at the loop onsets ("loop") and at the middle of each
                    stored answer ("normal", the matched control): mean over neurons of the mean a, of the mean |a|, of z and of
                    |z|, where z = (mean a - normal_mean) / normal_sd; per neuron: trace (mean a over looped rows) and windows
                    (mean a in [-200, -50), [-50, 0), [0, period), [period, 2 periods)). Periods differ a hundredfold between
                    rows, so everything is also stored in units of the row's own period: "period" per set and period_trace
                    per neuron, 40 bins per period from -1 to +2 periods (period_offsets: the bin centres).
  dose.json         item 5. The half B rows restarted 300 tokens before the onset and continued --steps tokens at T 0.6 / top-p 1.0
                    with the set's activations multiplied by a factor (0, 0.5, 1, 2 for the selected set; --ref-factors for the
                    reference). Token = argmax(logits / T + Gumbel noise of (noise seed, problem index, step)), the noise of
                    lib/loops.py, so factor 1 with Part L's seed repeats the stored continuation (same_as_stored). A row loops
                    when the detector fires; its generation ends there. Per condition: loops, n, loop_rate, stopped, and per
                    row the detector's flag, the tokens and the decoded tail.
                    Controls: factor 1 run twice gives the same tokens; the other KV cache gives the same first tokens.
  metrics.json      config, commit, job id, counts, timings, the headline numbers, the controls.

The job writes every file, then fails if a control failed. --dry-run uses random 4-layer Olmo3 models (hidden 16, width 64, no
weights, no GPU); without --edit it writes a synthetic edit file into --out, with `--loops synthetic` a synthetic loops.json
(without --loops it takes the path without loops); its answers are synthetic, or with --inputs <dir> the real T1 / T2 rows and
tokenizer. Fail loud: no try/except, no fallback.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import time

import numpy as np
import torch

from studies.cleanneurons.lib import loops as L
from studies.rlneurons.jobs import rln5_map as M5
from studies.rlneurons.lib import n13_score as S

N_MIN, N_MAX = 500, 3000                              # n_new of an eligible stored answer (Part T row rule)
OFF_LO, OFF_HI = -200, 400                            # onset trace in tokens
PER_LO, PER_HI, BINS = -1, 2, 40                      # onset trace in units of the row's period: -1 .. +2 periods, 40 bins per period
RESTART, TEMP = 300, 0.6                              # dose
QUANT = (("p50", 0.5), ("p90", 0.9), ("p99", 0.99), ("p99.9", 0.999))
N_CTX, BEFORE, AFTER, N_OUT = 20, 60, 20, 15
LOOP_KEYS = ("problem_index", "ids", "n_prompt", "n_context", "onset", "period", "half")
MEM_GB = 24                                           # the two activation records [positions, neurons] in float16
CACHE_STEPS, CACHE_FIRST, CACHE_MIN = 48, 8, 0.75     # cache control: tokens compared, and the agreement asked of the first 8


def r4(x):
    return float(f"{float(x):.4g}")


def rl4(t):
    return [r4(v) for v in t.tolist()]


def dump_lines(path, head, key, rows):
    """A JSON object: head, then head[key] = rows with one row per line."""
    tmp = pathlib.Path(str(path) + ".tmp")
    tmp.write_text(json.dumps(head, indent=1, allow_nan=False)[:-2] + f',\n "{key}": [\n'
                   + ",\n".join(json.dumps(r, allow_nan=False) for r in rows) + "\n ]\n}\n")
    tmp.replace(path)


# ------------------------------------------------------------------------------------------------ inputs
def read_edit(path, n_layers, W):
    e = json.loads(pathlib.Path(path).read_text())
    sel = {}
    for key in ("zero", "copy_neurons"):
        for l, ns in e.get(key, {}).items():
            if ns:
                sel.setdefault(int(l), set()).update(int(n) for n in ns)
    assert sel, f"{path}: no neuron under zero or copy_neurons; keys found: {sorted(e)}"
    assert all(0 <= l < n_layers and all(0 <= n < W for n in ns) for l, ns in sel.items()), f"{path}: a neuron outside {n_layers} x {W}"
    return e.get("name"), {l: sorted(sel[l]) for l in sorted(sel)}


def subsample(sel, n, seed):
    flat = [(l, x) for l, ns in sel.items() for x in ns]
    keep = sorted(flat[i] for i in np.random.default_rng([seed, 1]).choice(len(flat), n, replace=False))
    return {l: [x for k, x in keep if k == l] for l in sorted({k for k, _ in keep})}


def reference(sel, W, seed):
    """The same number of neurons per layer, drawn uniformly from the layer's other neurons."""
    assert all(2 * len(ns) <= W for ns in sel.values()), "a layer has more selected neurons than others to draw from"
    return {l: sorted(np.random.default_rng([seed, l]).choice(np.setdiff1d(np.arange(W), ns), len(ns), replace=False).tolist())
            for l, ns in sel.items()}


def read_loops(path):
    """Part L's loops.json, {"detector": {"version", ...}, "rows"}: the detector version and the looped rows as sequences
    {idx, src, ids, n_prompt, n_context, onset, period, half}."""
    d = json.loads(pathlib.Path(path).read_text())
    assert isinstance(d, dict) and "rows" in d and "version" in d.get("detector", {}), \
        f"{path}: not {{'detector': {{'version', ...}}, 'rows'}}; found: {sorted(d) if isinstance(d, dict) else type(d).__name__}, detector {d.get('detector') if isinstance(d, dict) else None}"
    assert d["detector"]["version"] in L.PMAX_OF, d["detector"]
    rows = d["rows"]
    looped = [r for r in rows if r.get("onset") is not None]
    assert looped, f"{path}: no row with an onset; keys of the first row: {sorted(rows[0]) if rows else 'no rows'}"
    out = []
    for r in looped:
        miss = [k for k in LOOP_KEYS if k not in r]
        assert not miss, f"{path}: a looped row lacks {miss}; keys found: {sorted(r)}"
        s = {"idx": int(r["problem_index"]), "src": "loop", "ids": [int(i) for i in r["ids"]], "half": r["half"],
             **{k: int(r[k]) for k in ("n_prompt", "n_context", "onset", "period")}}
        assert s["half"] in ("A", "B") and 0 <= s["idx"] < 1000, (s["idx"], s["half"])
        assert 0 < s["n_prompt"] <= s["n_context"] <= s["onset"] < len(s["ids"]) - 1, f"row {s['idx']}: n_prompt <= n_context <= onset < tokens fails"
        out.append(s)
    assert len({s["idx"] for s in out}) == len(out), "a problem index twice"
    return d["detector"]["version"], sorted(out, key=lambda s: s["idx"]), len(rows) - len(looped)


def check_onsets(loops):
    """Each stored (onset, period) against the shared detector (lib/loops.scan, the version of loops.json) run on the row's
    sampled tokens ids[n_context:], which is how Part L found them. An onset counted from another position or one period late,
    or tokens cut before the detector fires, fail this."""
    rep = []
    for s in loops:
        got = L.scan(s["ids"][s["n_context"]:])
        rep.append({"problem_index": s["idx"], "onset": s["onset"], "period": s["period"], "tokens_after_onset": len(s["ids"]) - s["onset"],
                    "detector_onset": got and got[2] + s["n_context"], "detector_period": got and got[1]})
        rep[-1]["ok"] = (rep[-1]["detector_onset"], rep[-1]["detector_period"]) == (s["onset"], s["period"])
    n, bad, per = sum(r["ok"] for r in rep), [r for r in rep if not r["ok"]], [r["period"] for r in rep]
    assert n >= 0.9 * len(rep), (f"{len(bad)} of {len(rep)} looped rows: lib/loops.scan (version {L.VERSION}) on ids[n_context:] does not give the "
                                 f"onset and period of loops.json (onset = index into ids of the first token of the first cycle): {bad[:4]}")
    return {"rows": len(rep), "ok": n, "not_ok": bad, "periods": {"min": min(per), "median": float(np.median(per)), "max": max(per)}}


def stored(a, fz):
    """The Part T rows: per cell the answers with N_MIN <= n_new <= N_MAX that are not cap hits and re-tokenize to within 1 % of
    n_new, sorted by problem index, --rows of them evenly spaced, as rln5_map.build sequences. Asserts as in rln5_map.main."""
    frozen = json.loads((M5.D5 / "map_inputs.json").read_text())
    assert M5.sha(M5.D4 / "math500.json") == fz["sha256"]["math500.json"]
    math = json.loads((M5.D4 / "math500.json").read_text())
    assert all(int(p["index"]) == i for i, p in enumerate(math))
    n13 = json.loads((M5.D4 / "prompt_ids.json").read_text())
    assert n13["pair"] == "pair1"
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"]))
    assert tok.decode(fz["prefill_ids"]) == fz["prefill_text"]
    seqs = []
    for c in M5.CELLS:
        p, f = pathlib.Path(a.inputs) / f"{c}.jsonl", frozen["files"][f"{c}.jsonl"]
        assert p.stat().st_size == f["bytes"] and M5.sha(p) == f["sha256"], f"{p} differs from data/rln5/map_inputs.json"
        rows = sorted((json.loads(l) for l in p.read_text().splitlines()), key=lambda r: r["problem_index"])
        assert [r["problem_index"] for r in rows] == list(range(500)) and all(r["cell"] == c and r["sampling"] == fz["cells"][c][2] for r in rows)
        built = [M5.build(tok, fz, r, math[r["problem_index"]], n13["ids"][r["problem_index"]])
                 for r in rows if N_MIN <= r["n_new"] <= N_MAX and not r["cap_hit"]]
        seqs += [{**s, "src": c} for s in evenly([s for s in built if abs(s["retok_diff"]) <= M5.TOL * s["n_new"]], a.rows)]
    return seqs, tok, frozen["files"]


def evenly(seqs, n):
    if len(seqs) <= n:
        return seqs
    pick = np.linspace(0, len(seqs) - 1, n).round().astype(int)
    assert len(set(pick.tolist())) == n
    return [seqs[i] for i in pick]


# ------------------------------------------------------------------------------------------------ --dry-run stand-ins
class FakeTok:
    def decode(self, ids, **_):
        return "".join(f" t{i}" for i in ids)


def tiny_pair(n_layers, W, vocab):
    """Random Olmo3 models (the class of the real ones: sliding-window and full layers, post-norm MLP). 'RL' is the base plus noise."""
    from transformers import Olmo3Config, Olmo3ForCausalLM
    cfg = Olmo3Config(vocab_size=vocab, hidden_size=16, intermediate_size=W, num_hidden_layers=n_layers, num_attention_heads=2, sliding_window=256,
                      pad_token_id=0, eos_token_id=1, initializer_range=0.3)
    torch.manual_seed(0)
    base, rl = Olmo3ForCausalLM(cfg).eval(), Olmo3ForCausalLM(cfg).eval()
    rl.load_state_dict(base.state_dict())
    for p in rl.parameters():
        p.data += 0.2 * p.data.std() * torch.randn(p.shape)
    return base, rl


def synthetic_rows(a, vocab):
    """Stored answers with random ids; some are too short, too long or cap hits."""
    g, seqs = np.random.default_rng(0), []
    for c in M5.CELLS:
        rows = [(i, int(g.integers(300, 3600)), i % 5 == 4) for i in range(14)]
        seqs += [{"idx": i, "src": c, "ids": g.integers(2, vocab, 20 + n).tolist() + [1], "n_prompt": 20}
                 for i, n, cap in evenly([r for r in rows if N_MIN <= r[1] <= N_MAX and not r[2]], a.rows)]
    return seqs


def synthetic_files(a, out, vocab):
    """Without --edit: a synthetic edit file. --loops synthetic: a loops.json in Part L's format: a row that did not loop and seven
    planted loops with periods 7 .. 574 (context and loop from disjoint id ranges, so the onset is the planted one), each cut
    300 tokens after the detector fires."""
    g = np.random.default_rng(1)
    if not a.edit:
        a.edit = str(out / "dry_edit.json")
        M5.dump(a.edit, {"name": "dry", "zero": {"0": [1, 5, 9], "2": [3, 4]}, "copy_neurons": {"3": [7], "1": []}})
    if a.loops == "synthetic":
        rows = [{"problem_index": 99, "looped": False}]
        for i, p in enumerate((7, 23, 300, 37, 574, 120, 61)):
            pre, n = int(g.integers(400, 900)), 2 * p + L.win(p) + 300
            ids = g.integers(2, vocab // 2, 20 + pre).tolist() + np.tile(g.integers(vocab // 2, vocab, p), n // p + 1)[:n].tolist()
            rows.append({"problem_index": 100 + i, "ids": ids, "n_prompt": 20, "n_context": 20 + pre // 3, "onset": 20 + pre, "period": p,
                         "half": "AB"[i % 2]})
        a.loops = str(out / "dry_loops.json")
        M5.dump(a.loops, {"detector": L.describe(), "rows": rows})


# ------------------------------------------------------------------------------------------------ model
def record(model, seqs, cols, dev, dt, n_sub=0, seed=0):
    """a of the neurons cols[l] (columns in layer order) at every scored position of every sequence: [positions, neurons]. With
    n_sub: also |a| of every neuron of each layer at n_sub random scored positions per sequence. One pass of the backbone per
    sequence, no cache, no logits."""
    g, out, sub = torch.Generator().manual_seed(seed), [], [[] for _ in cols]
    with L.capture(model) as acts:
        for s in seqs:
            lo = s["n_prompt"]
            some = torch.randperm(len(s["ids"]) - 1 - lo, generator=g)[:n_sub].to(dev)
            model.model(input_ids=torch.tensor(s["ids"][:-1], device=dev)[None], use_cache=False)
            out.append(torch.cat([x[0][lo:, cols[l]].to(dt) for l, x in enumerate(acts)], 1))
            for l, x in enumerate(acts if n_sub else []):
                sub[l].append(x[0][lo:][some].abs().to(dt))
    return torch.cat(out), [torch.cat(x) for x in sub] if n_sub else None


def weights(base, rl, cols):
    """Per neuron, in column order: cosine and norm ratio (RL / base) of its gate, up and down vectors; the N_OUT largest and
    smallest values of lm_head . (norm.weight * post_feedforward_layernorm.weight * down_proj[:, n]) with their token ids."""
    out = {k: [] for k in ("cos_gate", "cos_up", "cos_down", "norm_ratio_gate", "norm_ratio_up", "norm_ratio_down", "top_v", "top_i", "bot_v", "bot_i")}
    E, g = base.lm_head.weight.float(), base.model.norm.weight.float()
    for l, idx in enumerate(cols):
        if not len(idx):
            continue
        vec = lambda m: (m.gate_proj.weight[idx].float(), m.up_proj.weight[idx].float(), m.down_proj.weight[:, idx].T.float())
        vb, vr = vec(base.model.layers[l].mlp), vec(rl.model.layers[l].mlp)
        for name, b, r in zip(("gate", "up", "down"), vb, vr):
            out["cos_" + name].append(torch.nn.functional.cosine_similarity(b, r, dim=1))
            out["norm_ratio_" + name].append(r.norm(dim=1) / b.norm(dim=1))
        d = vb[2] * (g * base.model.layers[l].post_feedforward_layernorm.weight.float())
        for j in range(0, len(idx), 512):
            lg = d[j:j + 512] @ E.T
            for key, t in (("top", lg.topk(N_OUT, 1)), ("bot", (-lg).topk(N_OUT, 1))):
                out[key + "_v"].append(t.values if key == "top" else -t.values)
                out[key + "_i"].append(t.indices)
    return {k: torch.cat(v).cpu() for k, v in out.items()}


# ------------------------------------------------------------------------------------------------ statistics of the record
def unit_stats(A, thr, n_norm, chunk=256):
    """Per column of A: the quantiles and maximum of each pole, the share of positions where the pole exceeds thr (the layer's p97
    of |a|), the mean |a|, and the mean and sd on normal text (the first n_norm positions)."""
    P, out = A.shape[0], {}
    for j in range(0, A.shape[1], chunk):
        x, t = A[:, j:j + chunk].float(), thr[j:j + chunk]
        s = x.sort(0).values
        r = {"mean_abs": x.abs().mean(0), "normal_mean": x[:n_norm].mean(0), "normal_sd": x[:n_norm].std(0),
             "pos_max": s[-1].clamp(min=0), "neg_max": (-s[0]).clamp(min=0),
             "pos_share_beyond_p97": (x > t).float().mean(0), "neg_share_beyond_p97": (x < -t).float().mean(0)}
        for name, q in QUANT:
            i = round(q * (P - 1))
            r["pos_" + name], r["neg_" + name] = s[i].clamp(min=0), (-s[P - 1 - i]).clamp(min=0)
        for k, v in r.items():
            out.setdefault(k, []).append(v.cpu())
    return {k: torch.cat(v) for k, v in out.items()}


def compare(A, B, chunk=256):
    """Per column: mean |a| in A (base) and in B (RL), and the correlation of the two over positions."""
    out = {"mean_abs_base": [], "mean_abs_rl": [], "act_corr": []}
    for j in range(0, A.shape[1], chunk):
        x, y = A[:, j:j + chunk].float(), B[:, j:j + chunk].float()
        xc, yc = x - x.mean(0), y - y.mean(0)
        out["mean_abs_base"].append(x.abs().mean(0).cpu())
        out["mean_abs_rl"].append(y.abs().mean(0).cpu())
        out["act_corr"].append(((xc * yc).sum(0) / (xc.norm(dim=0) * yc.norm(dim=0)).clamp(min=1e-12)).cpu())
    return {k: torch.cat(v) for k, v in out.items()}


def candidates(A, start, sign, chunk=256):
    """For the pole sign * a, per column: each answer's best position (value, row of A), then the 2 * N_CTX best rows overall."""
    best = [(sign * A[s:e].float()).max(0) for s, e in zip(start[:-1], start[1:])]
    av, ap = torch.stack([b.values for b in best]), torch.stack([b.indices + int(s) for b, s in zip(best, start[:-1])])
    top = [(sign * A[:, j:j + chunk].float()).topk(min(2 * N_CTX, A.shape[0]), 0) for j in range(0, A.shape[1], chunk)]
    tv, tp = torch.cat([t.values for t in top], 1), torch.cat([t.indices for t in top], 1)
    return [t.T.cpu().tolist() for t in (av, ap, tv, tp)]


def pick(av, ap, tv, tp):
    """Up to N_CTX (value, row) with a positive value, largest first: one per answer, then the best remaining rows."""
    best = sorted(((v, p) for v, p in zip(av, ap) if v > 0), reverse=True)[:N_CTX]
    used = {p for _, p in best}
    for v, p in zip(tv, tp):
        if len(best) >= N_CTX:
            break
        if v > 0 and p not in used:
            best.append((v, p))
            used.add(p)
    return sorted(best, reverse=True)


def traces(A, events):
    """events: (first row of the sequence in A, its scored positions, the onset as a scored position, the period). Per column:
    the mean of a and of |a| at each offset OFF_LO..OFF_HI over the events that have it, the events per offset, and the mean of a
    in the windows [OFF_LO, -50), [-50, 0), [0, period), [period, 2 periods)."""
    n, K = OFF_HI - OFF_LO + 1, A.shape[1]
    tot, tot_abs, cnt = torch.zeros(n, K, device=A.device), torch.zeros(n, K, device=A.device), torch.zeros(n, device=A.device)
    win, wcnt = torch.zeros(4, K, device=A.device), torch.zeros(4, device=A.device)
    for s, m, o, p in events:
        lo, hi = max(o + OFF_LO, 0), min(o + OFF_HI + 1, m)
        x, j = A[s + lo:s + hi].float(), lo - o - OFF_LO
        tot[j:j + len(x)] += x
        tot_abs[j:j + len(x)] += x.abs()
        cnt[j:j + len(x)] += 1
        for w, (b, e) in enumerate(((OFF_LO, -50), (-50, 0), (0, p), (p, 2 * p))):
            b, e = max(o + b, 0), min(o + e, m)
            if e > b:
                win[w] += A[s + b:s + e].float().mean(0)
                wcnt[w] += 1
    c = cnt.clamp(min=1)[:, None]
    return (tot / c).cpu(), (tot_abs / c).cpu(), cnt.cpu(), (win / wcnt.clamp(min=1)[:, None]).cpu(), wcnt.cpu()


def period_traces(A, events):
    """The same events in units of each event's own period: BINS bins per period from PER_LO to PER_HI periods around the onset
    (the token at offset d falls in bin floor(d * BINS / period)). Per column the mean over events of the event's mean a, and of
    its mean |a|, in the bin; and the events per bin (a period under BINS tokens leaves bins without a token)."""
    n, K = (PER_HI - PER_LO) * BINS, A.shape[1]
    tot, tot_abs, cnt = torch.zeros(n, K, device=A.device), torch.zeros(n, K, device=A.device), torch.zeros(n, device=A.device)
    for s, m, o, p in events:
        lo, hi = max(o + PER_LO * p, 0), min(o + PER_HI * p, m)
        if hi <= lo:
            continue
        b = (torch.arange(lo - o, hi - o, device=A.device) * BINS).div(p, rounding_mode="floor") - PER_LO * BINS
        x, k = A[s + lo:s + hi].float(), torch.bincount(b, minlength=n).float()
        have = k > 0
        tot[have] += torch.zeros(n, K, device=A.device).index_add_(0, b, x)[have] / k[have, None]
        tot_abs[have] += torch.zeros(n, K, device=A.device).index_add_(0, b, x.abs())[have] / k[have, None]
        cnt += have
    c = cnt.clamp(min=1)[:, None]
    return (tot / c).cpu(), (tot_abs / c).cpu(), cnt.cpu()


# ------------------------------------------------------------------------------------------------ dose
def scale(model, sets, f):
    """Context manager: the activations of the neurons sets = {layer: [neuron, ...]} are multiplied by f before down_proj.
    lib/loops.zero is the case f = 0; this is the same hook with another factor."""
    vec = {l: k + f * (1 - k) for l, k in L.keep_vectors(model, sets).items()}
    return L.hooks(model, lambda l, a: a * vec[l] if l in vec else None)


# ------------------------------------------------------------------------------------------------ main
@torch.inference_mode()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edit", help="repo path of the edit file")
    ap.add_argument("--loops", help="Part L's loops.json: /runs/<job id>/loops.json or a repo path; without it items 4 and 5 are skipped")
    ap.add_argument("--inputs", default=None, help="directory of T1.jsonl and T2.jsonl (default /runs/inputs/rln5; --dry-run: synthetic rows)")
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--commit", required=True, help="the submitted commit: $(git rev-parse HEAD), expanded on the laptop")
    ap.add_argument("--rows", type=int, default=40, help="stored answers per cell")
    ap.add_argument("--loop-rows", type=int, default=None, help="only the first n looped rows of each half")
    ap.add_argument("--max-neurons", type=int, default=None, help="a random subset of the selected neurons of this size")
    ap.add_argument("--sub", type=int, default=32, help="positions per sequence for each layer's p97 of |a|")
    ap.add_argument("--steps", type=int, default=1600, help="dose: tokens after the restart (a loop of period p is flagged p + max(240, p) after its onset)")
    ap.add_argument("--batch", type=int, default=16, help="dose: rows per batch at most; 1 pads nothing")
    ap.add_argument("--kv-gb", type=float, default=40.0, help="dose: KV cache per batch at most")
    ap.add_argument("--chunk", type=int, default=1024, help="dose: context tokens per forward pass")
    ap.add_argument("--factors", default="0,0.5,1,2", help="dose: write factors of the selected set (1 is always run, twice)")
    ap.add_argument("--ref-factors", default="0,2", help="dose: write factors of the reference set")
    ap.add_argument("--cache", default="buffer", choices=("buffer", "dynamic"), help="dose: lib/loops.new_cache")
    ap.add_argument("--seed", type=int, default=0, help="reference neurons, subsamples, random contexts")
    ap.add_argument("--noise-seed", type=int, default=0, help="dose: sampling noise")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        a.rows, a.loop_rows, a.max_neurons, a.steps = 4, 3, 64, 600
    t0, tm = time.time(), {}
    assert a.out, "no --out and no $OUT_DIR"
    assert re.fullmatch(r"[0-9a-f]{40}", a.commit), f"--commit {a.commit!r} is not a full git sha"
    assert a.dry_run or a.edit, "--edit is required"
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / "metrics.json").exists(), f"{out}/metrics.json exists: one fresh directory per run"
    fz = json.loads((M5.D4 / "frozen4.json").read_text())
    n_layers, W = (4, 64) if a.dry_run else (32, 11008)

    # inputs: the stored answers, the neurons, the looped rows
    if a.dry_run and not a.inputs:
        vocab, stop_id, tok, inputs = 128, 1, FakeTok(), {"dry_run": True}
        normal = synthetic_rows(a, vocab)
    else:
        a.inputs = a.inputs or "/runs/inputs/rln5"
        normal, tok, inputs = stored(a, fz)
        vocab, stop_id = len(tok), S.STOP_ID
    if a.dry_run:
        synthetic_files(a, out, vocab)
    name, sel = read_edit(a.edit, n_layers, W)
    n_edit = sum(map(len, sel.values()))
    if a.max_neurons and n_edit > a.max_neurons:
        sel = subsample(sel, a.max_neurons, a.seed)
    ref = reference(sel, W, a.seed)
    cols = [sel.get(l, []) + ref.get(l, []) for l in range(n_layers)]
    U = [(s, l, n) for l in range(n_layers) for s, d in (("selected", sel), ("reference", ref)) for n in d.get(l, [])]
    is_sel = torch.tensor([u[0] == "selected" for u in U])
    loops, held, loops_info = [], [], None
    if a.loops:
        assert L.selfcheck()
        version, loops, not_looped = read_loops(a.loops)
        L.set_version(version)                           # the detector that found the loops also judges the dose
        loops_info = {"sha256": M5.sha(a.loops), "detector": L.describe(), "rows_not_looped": not_looped, "onset_check": check_onsets(loops)}
        if a.loop_rows:
            loops = [s for h in "AB" for s in [s for s in loops if s["half"] == h][:a.loop_rows]]
        held = [s for s in loops if s["half"] == "B"]
        assert held, "no looped row in half B"
        loops_info.update(used=len(loops), half_A=len(loops) - len(held), half_B=len(held))
    skipped = {} if loops else {"item 4 (onset_trace.json)": "no --loops: there is no loop onset to align on",
                                "item 5 (dose.json)": "no --loops: there are no held-out looped rows to restart"}
    seqs = normal + loops
    n_pos = [len(s["ids"]) - 1 - s["n_prompt"] for s in seqs]
    start = np.concatenate([[0], np.cumsum(n_pos)]).astype(np.int64)
    P, K, n_norm = int(start[-1]), len(U), int(start[len(normal)])
    assert min(n_pos) > 0 and 4 * P * K <= MEM_GB * 2 ** 30, f"{P} positions x {K} neurons: over {MEM_GB} GB for two records; use --max-neurons"
    factors, ref_factors = ([float(x) for x in s.split(",") if x] for s in (a.factors, a.ref_factors))
    conds = [("selected_x1", "selected", 1.0), ("selected_x1_repeat", "selected", 1.0)]
    conds += [(f"{s}_x{f:g}", s, f) for s, fs in (("selected", factors), ("reference", ref_factors)) for f in fs if f != 1]

    m = {"status": "loading", "config": {**vars(a), "out": str(out)}, "commit": a.commit, "job_id": os.environ.get("JOB_ID"), "started_utc": M5.utc(),
         "edit": {"name": name, "sha256": M5.sha(a.edit), "neurons_in_file": n_edit, "selected": len(U) // 2, "reference": len(U) // 2,
                  "per_layer": {str(l): len(ns) for l, ns in sel.items()}},
         "loops": loops_info, "skipped": skipped, "inputs": inputs, "counts": {"answers": {c: sum(s["src"] == c for s in seqs) for c in ("T1", "T2", "loop")}, "positions": P,
                                      "positions_normal_text": n_norm, "neurons": K},
         "torch": torch.__version__, "units": "activations in the model's units; cosines and shares as stated"}
    M5.dump(out / "metrics.json", m)
    print(json.dumps({k: m[k] for k in ("edit", "loops", "skipped", "counts")}, indent=1), flush=True)

    def finish(controls):
        m.update(status="done", wall_s=time.time() - t0, controls=controls)
        if not a.dry_run:
            m["gpu_max_memory_gb"] = torch.cuda.max_memory_allocated() / 2 ** 30
        M5.dump(out / "metrics.json", m)
        keys = ("controls", "skipped", "dose", "onset_windows", "base_vs_rl", "timings", "wall_s")
        print(json.dumps({k: m[k] for k in keys if k in m}, indent=1), flush=True)
        failed = [k for k, v in controls.items() if not v]
        assert not failed, f"controls failed: {failed} (see dose.json)"

    if a.dry_run:
        dev, dt = "cpu", torch.float32
        base, rl = tiny_pair(n_layers, W, vocab)
        m["models"] = {"dry_run": True, "class": type(base).__name__}
    else:
        dev, dt = "cuda", torch.float16
        m["gpu"] = torch.cuda.get_device_name(0)
        base, ib = M5.load(fz, "base", dev)
        rl, ir = M5.load(fz, "rl", dev)
        m["models"], vocab = {"base": ib, "rl": ir}, ib["vocab_size"]
        assert vocab == ir["vocab_size"]
    for mdl in (base, rl):                             # the modules this job reads; Olmo3: the MLP's output passes post_feedforward_layernorm
        assert L.check_model(mdl) == (n_layers, W) and all(l.post_feedforward_layernorm.weight.shape == mdl.model.norm.weight.shape
                                                          == (mdl.lm_head.weight.shape[1],) for l in mdl.model.layers)
    pad_id = base.config.pad_token_id
    assert pad_id is not None and max(stop_id, max(max(s["ids"]) for s in seqs)) < vocab
    tm["load_s"] = time.time() - t0
    m.update(status="running", timings=tm)
    M5.dump(out / "metrics.json", m)
    colsT = [torch.tensor(c, dtype=torch.long, device=dev) for c in cols]
    u_layer = torch.tensor([u[1] for u in U])

    # items 3 and 6 (weights), then the activation records of both models
    t = time.time()
    wt = weights(base, rl, colsT)
    A, sub = record(base, seqs, colsT, dev, dt, a.sub, a.seed)
    assert A.shape == (P, K) and torch.isfinite(A).all()
    p97 = [float(v.flatten().float().kthvalue(int(0.97 * (v.numel() - 1)) + 1).values) for v in sub]
    del sub
    A_rl, _ = record(rl, seqs, colsT, dev, dt)
    assert torch.isfinite(A_rl).all()
    cmp = compare(A, A_rl)
    del rl
    tm["record_s"] = time.time() - t
    print(f"{M5.utc()} record: {P} positions x {K} neurons, both models, {tm['record_s']:.0f} s", flush=True)

    # item 1 (quantiles), item 3 (tokens), item 6: neurons.json
    t = time.time()
    thr = torch.tensor(p97, device=dev)[u_layer.to(dev)]
    st, st_rl = unit_stats(A, thr, n_norm), unit_stats(A_rl, thr, n_norm)
    poles_of = lambda d, k: {pole: {q: r4(d[f"{pole}_{q}"][k]) for q in [q for q, _ in QUANT] + ["max", "share_beyond_p97"]} for pole in ("pos", "neg")}
    dec = lambda i: tok.decode([int(i)])
    units = []
    for k, (s, l, n) in enumerate(U):
        u = {"set": s, "layer": l, "neuron": n, **poles_of(st, k)}
        u.update({q: r4(st[q][k]) for q in ("mean_abs", "normal_mean", "normal_sd")})
        u["promoted"] = [[dec(i), r4(v)] for i, v in zip(wt["top_i"][k], wt["top_v"][k])]
        u["suppressed"] = [[dec(i), r4(v)] for i, v in zip(wt["bot_i"][k], wt["bot_v"][k])]
        u["rl"] = {**{q: r4(wt[q][k]) for q in wt if q[:3] in ("cos", "nor")}, **{q: r4(cmp[q][k]) for q in cmp},
                   "gain": r4(cmp["mean_abs_rl"][k] / cmp["mean_abs_base"][k].clamp(min=1e-12)), **poles_of(st_rl, k)}
        units.append(u)
    head = {"what": "SPEC1 Part I items 1, 3, 6; fields in the docstring of jobs/describe_neurons.py", "edit": name, "positions": P,
            "positions_normal_text": n_norm, "layer_p97_abs": [r4(v) for v in p97],
            "output_note": "promoted / suppressed: lm_head . (norm.weight * post_feedforward_layernorm.weight * down_proj[:, n]); the two "
                           "norms' input-dependent scales and later layers are ignored; for the '-' pole the two lists swap",
            "rl_note": "rl.pos / rl.neg: the RL model's a of the same neuron on the same text; share_beyond_p97 against the base's layer p97"}
    dump_lines(out / "neurons.json", head, "neurons", units)

    # item 2: contexts.json
    g, poles, rnd = np.random.default_rng([a.seed, 2]), [], []
    where = lambda p: (i := int(np.searchsorted(start, p, side="right")) - 1, seqs[i]["n_prompt"] + int(p - start[i]))
    for sign, pole in ((1, "+"), (-1, "-")):
        for k, cand in enumerate(zip(*candidates(A, start, sign))):
            best = pick(*cand)
            ans = [where(p)[0] for _, p in best[1::2]]
            ans += g.integers(len(seqs), size=N_CTX // 2 - len(ans)).tolist()
            rows = [int(start[i] + g.integers(n_pos[i])) for i in ans]
            poles.append((k, sign, pole, best, sum(v > 0 for v in cand[0])))
            rnd.append(rows)
    at = lambda M, rows, ks: M[torch.tensor(rows, dtype=torch.long, device=dev), torch.tensor(ks, dtype=torch.long, device=dev)].float().cpu().tolist()
    rnd_a, rnd_rl = (at(M, rnd, [[p[0]] for p in poles]) for M in (A, A_rl))
    top_rl = iter(at(A_rl, [p for q in poles for _, p in q[3]], [q[0] for q in poles for _ in q[3]]))
    del A_rl

    def context(p, act, act_rl, rank=None):
        i, pos = where(p)
        s, ids = seqs[i], seqs[i]["ids"]
        c = {"text": tok.decode(ids[max(pos - BEFORE, 0):pos]) + "<<" + tok.decode(ids[pos:pos + 1]) + ">>" + tok.decode(ids[pos + 1:pos + 1 + AFTER]),
             "activation": r4(act), "activation_rl": r4(act_rl), "next_token": tok.decode(ids[pos + 1:pos + 2]), "source": s["src"], "problem_index": s["idx"], "position": pos,
             "onset_offset": pos - s["onset"] if s["src"] == "loop" else None}
        return c if rank is None else {"rank": rank, **c}

    ctx = []
    for (k, sign, pole, best, firing), rows, acts, acts_rl in zip(poles, rnd, rnd_a, rnd_rl):
        top = [context(p, sign * v, next(top_rl), r) for r, (v, p) in enumerate(best)]
        ctx.append({"set": U[k][0], "layer": U[k][1], "neuron": U[k][2], "pole": pole, "answers_firing": firing,
                    "first10": top[0::2], "heldout10": top[1::2], "random10": [context(p, v, w) for p, v, w in zip(rows, acts, acts_rl)]})
    head = {"what": "SPEC1 Part I item 2; fields in the docstring of jobs/describe_neurons.py", "edit": name,
            "format": f"text = {BEFORE} tokens before + <<the token>> + {AFTER} tokens after; activation is the base's a (signed) at the token, "
                      "activation_rl the RL model's a of the same neuron there (the top contexts are chosen by the base's activation, so RL's "
                      "is lower there by selection alone: read it against the reference neurons); "
                      "random10 holds one random scored position from the answer of each heldout10 context (random answers when fewer)",
            "answers": len(seqs)}
    dump_lines(out / "contexts.json", head, "poles", ctx)
    tm["stats_contexts_s"] = time.time() - t
    med = lambda v, mask: None if torch.isnan(x := v[mask].nanmedian()) else r4(x)             # ratios: over the neurons whose base value is > 0
    ratio = lambda q: torch.where(st[q] > 0, st_rl[q] / st[q].clamp(min=1e-12), torch.nan)
    rlq = {**{q: wt[q] for q in wt if q[:3] in ("cos", "nor")}, "act_corr": cmp["act_corr"], "gain": cmp["mean_abs_rl"] / cmp["mean_abs_base"].clamp(min=1e-12),
           **{f"{pole}_{q}_rl_over_base": ratio(f"{pole}_{q}") for pole in ("pos", "neg") for q in ("p99", "max")}}
    m["base_vs_rl"] = {s: {"median_" + q: med(v, mask) for q, v in rlq.items()} for s, mask in (("selected", is_sel), ("reference", ~is_sel))}
    if not loops:
        return finish({})

    # item 4: onset_trace.json
    t = time.time()
    p_med = int(np.median([s["period"] for s in loops]))
    ev = {"loop": [(int(start[len(normal) + i]), n_pos[len(normal) + i], s["onset"] - s["n_prompt"], s["period"]) for i, s in enumerate(loops)],
          "normal": [(int(start[i]), n_pos[i], n_pos[i] // 2, p_med) for i in range(len(normal))]}
    mu, sd = st["normal_mean"], st["normal_sd"].clamp(min=1e-6)
    tr, sets = {}, {}
    for kind, e in ev.items():
        tr[kind] = traces(A, e)
        mean, mean_abs, cnt = tr[kind][:3]
        z = (mean - mu) / sd
        for s, mask in (("selected", is_sel), ("reference", ~is_sel)):
            sets.setdefault(s, {"neurons": int(mask.sum())})[kind] = {
                "events": len(e), "events_per_offset": [int(c) for c in cnt], "mean_a": rl4(mean[:, mask].mean(1)),
                "mean_abs_a": rl4(mean_abs[:, mask].mean(1)), "mean_z": rl4(z[:, mask].mean(1)), "mean_abs_z": rl4(z[:, mask].abs().mean(1))}
        ptr = period_traces(A, e)                         # the same in units of the row's period
        z = (ptr[0] - mu) / sd
        for s, mask in (("selected", is_sel), ("reference", ~is_sel)):
            sets[s][kind]["period"] = {"events_per_bin": [int(c) for c in ptr[2]], "mean_a": rl4(ptr[0][:, mask].mean(1)),
                                       "mean_abs_a": rl4(ptr[1][:, mask].mean(1)), "mean_z": rl4(z[:, mask].mean(1)), "mean_abs_z": rl4(z[:, mask].abs().mean(1))}
        if kind == "loop":
            ploop = ptr[0]
    win, wcnt = tr["loop"][3], tr["loop"][4]
    wn = ("before", "just_before", "first_cycle", "second_cycle")
    units = [{"set": s, "layer": l, "neuron": n, "normal_mean": r4(mu[k]), "normal_sd": r4(sd[k]), "windows": dict(zip(wn, rl4(win[:, k]))),
              "trace": rl4(tr["loop"][0][:, k]), "period_trace": rl4(ploop[:, k])} for k, (s, l, n) in enumerate(U)]
    zw = (win - mu) / sd
    onset_sum = {s: {w: {"mean_z": r4(zw[i, mask].mean()), "mean_abs_z": r4(zw[i, mask].abs().mean())} for i, w in enumerate(wn)}
                 for s, mask in (("selected", is_sel), ("reference", ~is_sel))}
    head = {"what": "SPEC1 Part I item 4; fields in the docstring of jobs/describe_neurons.py", "edit": name,
            "note": "offset 0 is the position that reads the first token of the first loop cycle (the position at offset -1 wrote it); the "
                    "repeated text starts at offset = period. z = (mean a - normal_mean) / normal_sd per neuron, normal text = the stored answers. "
                    "'normal' aligns the same window on the middle of each stored answer, with the median period (the matched control). "
                    "'period' and period_trace: the same in units of the row's own period, bin b holding the tokens at offsets "
                    f"[b, b + 1) * period / {BINS}; period_offsets gives each bin's centre in periods.",
            "detector": L.describe(), "offsets": list(range(OFF_LO, OFF_HI + 1)),
            "period_offsets": [round((b + 0.5) / BINS, 4) for b in range(PER_LO * BINS, PER_HI * BINS)],
            "windows": {"before": [OFF_LO, -50], "just_before": [-50, 0], "first_cycle": "[0, period)", "second_cycle": "[period, 2 periods)",
                        "rows_per_window": [int(c) for c in wcnt]},
            "rows": [{"problem_index": s["idx"], "onset": s["onset"], "period": s["period"], "half": s["half"], "tokens": len(s["ids"])} for s in loops],
            "median_period": p_med, "window_summary": onset_sum, "sets": sets}
    dump_lines(out / "onset_trace.json", head, "neurons", units)
    del A
    tm["onset_trace_s"] = time.time() - t

    # item 5: dose.json (sampling, noise, KV cache and detector of lib/loops.py)
    t = time.time()
    rows = [{"key": s["idx"], "restart": (r := max(s["onset"] - RESTART, s["n_context"])), "ctx": s["ids"][:r], "step0": r - s["n_context"],
             "stored": s["ids"][r:r + a.steps]} for s in held]
    gen = {"temp": TEMP, "seed": a.noise_seed, "stop_id": stop_id, "pad_id": pad_id, "chunk": a.chunk, "tail": 0}
    budget = int(a.kv_gb * 2 ** 30)
    batches = L.plan([len(r["ctx"]) for r in rows], a.steps, a.batch, budget, lambda n: L.kv_bytes(base, n, a.chunk))   # as generate_rows plans
    other = "dynamic" if a.cache == "buffer" else "buffer"
    res, dose, n_tok = {}, [], 0
    for cname, s, f in conds:
        tc = time.time()
        with scale(base, {"selected": sel, "reference": ref}[s], f):
            res[cname] = L.generate_rows(base, rows, a.steps, batch=a.batch, kv_budget=budget, cache=a.cache, **gen)
            if cname == "selected_x1":
                b0 = [rows[i] for i in batches[0]]
                alt = L.generate(base, [r["ctx"] for r in b0], [r["key"] for r in b0], [r["step0"] for r in b0], min(a.steps, CACHE_STEPS),
                                 cache=other, **gen)
        per = []
        for r, g_, one in zip(rows, res[cname], res["selected_x1"]):
            toks, flag = g_["tokens"], g_["flag"] or {}
            diff, n = [i for i, (x, y) in enumerate(zip(toks, one["tokens"])) if x != y], min(len(toks), len(r["stored"]))
            per.append({"problem_index": r["key"], "looped": g_["flag"] is not None, "flagged_at": flag.get("n"), "period": flag.get("period"),
                        "onset_step": flag.get("onset"), "generated": len(toks), "end": g_["end"], "stopped": g_["end"] == "stop",
                        "same_as_x1_until": diff[0] if diff else min(len(toks), len(one["tokens"])),
                        "same_as_stored": n > 0 and toks[:n] == r["stored"][:n], "tail": tok.decode(toks[-120:]), "tokens": toks})
        k = sum(p["looped"] for p in per)
        dose.append({"name": cname, "set": s, "factor": f, "loops": k, "n": len(per), "loop_rate": k / len(per), "stopped": sum(p["stopped"] for p in per),
                     "same_as_stored": sum(p["same_as_stored"] for p in per), "seconds": time.time() - tc, "rows": per})
        n_tok += sum(p["generated"] for p in per)
        print(f"{M5.utc()} dose {cname}: {k} of {len(per)} rows loop, {dose[-1]['stopped']} stopped, {time.time() - tc:.0f} s", flush=True)
    same = [x == y for x, y in zip(res["selected_x1"], res["selected_x1_repeat"])]
    first = [(res["selected_x1"][i]["tokens"], x["tokens"]) for i, x in zip(batches[0], alt)]
    agree = float(np.mean([x == y for p, q in first for x, y in zip(p[:CACHE_FIRST], q[:CACHE_FIRST])] + [len(p[:CACHE_FIRST]) == len(q[:CACHE_FIRST]) for p, q in first]))
    ctrl = {"same_noise": {"what": "factor 1 run twice: rows with identical tokens", "rows_identical": sum(same), "n": len(same), "pass": all(same)},
            "cache": {"what": f"the first batch at factor 1 with the {other} cache: share of the first {CACHE_FIRST} tokens equal to the {a.cache} run's",
                      "rows": len(first), "share": agree, "rows_identical_all_steps": sum(q == p[:len(q)] for p, q in first),
                      "steps": min(a.steps, CACHE_STEPS), "pass": agree >= CACHE_MIN}}
    head = {"what": "SPEC1 Part I item 5; fields in the docstring of jobs/describe_neurons.py", "edit": name,
            "note": "factor f multiplies the set's activations at every position, the context included; the MLP's output then passes "
                    "post_feedforward_layernorm, which rescales it. A row ends at the stop token, when the detector flags it (looped), or after "
                    "the steps. same_as_stored: the row's tokens equal the continuation stored in loops.json as far as both go (expected at "
                    "factor 1 when --noise-seed is Part L's seed: same model, context and noise).",
            "config": {"restart_before_onset": RESTART, "steps": a.steps, "temperature": TEMP, "top_p": 1.0, "noise_seed": a.noise_seed, "cache": a.cache,
                       "batches": [len(b) for b in batches], "detector": L.describe()},
            "rows": [{"problem_index": r["key"], "restart": r["restart"], "noise_step0": r["step0"], "context_tokens": len(r["ctx"])} for r in rows],
            "controls": ctrl, "summary": [{k: c[k] for k in ("name", "set", "factor", "loops", "n", "loop_rate", "stopped", "same_as_stored")} for c in dose]}
    dump_lines(out / "dose.json", head, "conditions", dose)
    tm["dose_s"] = time.time() - t
    tm["dose_tokens_per_s"] = n_tok / tm["dose_s"]

    m.update(dose=head["summary"], onset_windows=onset_sum)
    finish({k: v["pass"] for k, v in ctrl.items()})


if __name__ == "__main__":
    main()
