"""cleanneurons Part I, items 1 to 6 (specs/SPEC1.md): what the neurons of an edit file do, next to the same number of random
neurons per layer (the reference). One H100, both models in bf16, on the team runner:

    uv run tools/gpu.py submit h100 --hours 1 -- "python -m studies.cleanneurons.jobs.describe_neurons --commit $(git rev-parse HEAD) --edit <repo path of the edit file> --loops /runs/<Part L job id>/loops.json"
    smoke: add  --smoke   (4 answers per cell, 3 looped rows per half, 64 selected neurons, 260 generated tokens)
    Without --loops the job does items 1, 2, 3 and 6 on the stored answers only (neurons.json, contexts.json, metrics.json) and
    records in metrics.json "skipped" that items 4 and 5 were left out.

Inputs
  --edit    an edit file (SPEC1 "Edit file"); the selected neurons are those under `zero` and `copy_neurons`.
  --loops   Part L's loops.json: a list of rows, or {"rows": [...]}. A row without an `onset` did not loop and is skipped. Every
            other row needs: problem_index, ids (token ids: prompt, the context Part L continued, its continuation), n_prompt
            (tokens of the prompt; positions from there on are scored), n_context (tokens before the first sampled one; the
            noise step of ids[i] is i - n_context), onset (index into ids of the first token of the first loop cycle), period,
            half ("A" ranking, "B" held out).
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
                    (mean a in [-200, -50), [-50, 0), [0, period), [period, 400]).
  dose.json         item 5. The half B rows restarted 300 tokens before the onset and continued --steps tokens at T 0.6 / top-p 1.0
                    with the set's activations multiplied by a factor (0, 0.5, 1, 2 for the selected set; --ref-factors for the
                    reference). Token = argmax(logits / T + Gumbel noise of (noise seed, problem index, step)), the noise of
                    lib/loops.py, so factor 1 with Part L's seed repeats the stored continuation (same_as_stored). A row loops
                    when the detector's rule holds at some end position of its tokens; its generation ends within 32 tokens
                    of that. Per condition: loops, n, loop_rate, stopped, and per row the detector's verdict, the tokens and
                    the decoded tail.
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

from studies.rlneurons.jobs import rln5_map as M5
from studies.rlneurons.lib import n13_score as S

N_MIN, N_MAX = 500, 3000                              # n_new of an eligible stored answer (Part T row rule)
WIN, NEED, P_MIN, P_MAX = 240, 228, 2, 120            # loop detector: 95 % of the last 240 tokens, period 2..120
OFF_LO, OFF_HI = -200, 400                            # onset trace
RESTART, TEMP = 300, 0.6                              # dose
QUANT = (("p50", 0.5), ("p90", 0.9), ("p99", 0.99), ("p99.9", 0.999))
N_CTX, BEFORE, AFTER, N_OUT = 20, 60, 20, 15
LOOP_KEYS = ("problem_index", "ids", "n_prompt", "n_context", "onset", "period", "half")
MEM_GB = 24                                           # the two activation records [positions, neurons] in float16
CACHE_STEPS, CACHE_FIRST, CACHE_MIN = 48, 8, 0.75     # cache control: tokens compared, and the agreement asked of the first 8
CHUNK, CHECK = 1024, 32                               # dose: the context enters the cache in chunks; tokens between loop checks


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


# ------------------------------------------------------------------------------------------------ loop detector
def loop_scan(tok):
    """The loop detector of SPEC1 Part L on generated token ids. The rule at an end position n: tok[i] == tok[i - p] for at least
    95 % of the 240 tokens before n, for a period p in 2..120 with i - p inside tok. Returns (n, p, onset) for the first n at which
    the rule holds (the smallest such p), or None. Onset: the 240-window is moved back from n while it keeps 95 %; its first
    matching position s is the first repeated token, and the first cycle starts at s - p, the onset."""
    t, best = np.asarray(tok), None
    for p in range(P_MIN, min(P_MAX, len(t) - WIN) + 1):
        c = np.concatenate([[0], np.zeros(p, dtype=np.int64), np.cumsum(t[p:] == t[:-p])])    # c[i]: matches among tok[:i]
        ok = np.flatnonzero(c[WIN + p:] - c[p:len(t) - WIN + 1] >= NEED)                      # end positions WIN + p + ok
        if len(ok) and (best is None or WIN + p + ok[0] < best[0]):
            best = (int(WIN + p + ok[0]), p, c)
    if best is None:
        return None
    n, p, c = best
    j = n - WIN
    while j > p and c[j - 1 + WIN] - c[j - 1] >= NEED:
        j -= 1
    return n, p, j + int(np.argmax(np.diff(c[j:n + 1]))) - p


def detector_selfcheck():
    g = np.random.default_rng(0)
    planted = np.concatenate([g.integers(0, 50_000, 500), np.tile(g.integers(0, 50_000, 37), 12)])
    assert loop_scan(planted) == (500 + 37 + NEED, 37, 500), loop_scan(planted)                 # a planted loop: flag, period, onset
    assert loop_scan(planted[:700]) is None and loop_scan(g.integers(0, 50_000, 1000)) is None  # 200 looped tokens; no loop
    assert loop_scan(np.concatenate([planted, g.integers(0, 50_000, 300)])) == (765, 37, 500)   # a loop that ends is still flagged


# ------------------------------------------------------------------------------------------------ inputs
def read_edit(path, L, W):
    e = json.loads(pathlib.Path(path).read_text())
    sel = {}
    for key in ("zero", "copy_neurons"):
        for l, ns in e.get(key, {}).items():
            if ns:
                sel.setdefault(int(l), set()).update(int(n) for n in ns)
    assert sel, f"{path}: no neuron under zero or copy_neurons; keys found: {sorted(e)}"
    assert all(0 <= l < L and all(0 <= n < W for n in ns) for l, ns in sel.items()), f"{path}: a neuron outside {L} x {W}"
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
    """The looped rows of loops.json as sequences {idx, src, ids, n_prompt, n_context, onset, period, half}."""
    d = json.loads(pathlib.Path(path).read_text())
    assert isinstance(d, list) or "rows" in d, f"{path}: neither a list nor an object with 'rows'; keys found: {sorted(d)}"
    rows = d if isinstance(d, list) else d["rows"]
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
    return sorted(out, key=lambda s: s["idx"]), len(rows) - len(looped)


def check_onsets(loops):
    """Each stored onset o with period p against the definition (loop_scan): s = o + p is the first repeated token, so
    ids[s] == ids[s - p], ids[s - 1] != ids[s - 1 - p], and at least 90 % of the WIN tokens from s repeat the token p before. An
    onset counted from another position, or one period late, fails this. Also reported: the onset this job's detector finds on
    ids[n_context:]."""
    rep = []
    for s in loops:
        t, o, p = np.asarray(s["ids"]), s["onset"], s["period"]
        m = t[o + p:o + p + WIN] == t[o:o + WIN][:len(t) - o - p]
        got = loop_scan(s["ids"][s["n_context"]:])
        rep.append({"problem_index": s["idx"], "onset": o, "period": p, "detector_onset": got and got[2] + s["n_context"], "detector_period": got and got[1],
                    "ok": bool(len(m) and m[0] and t[o + p - 1] != t[o - 1] and m.mean() >= 0.9)})
    n, bad = sum(r["ok"] for r in rep), [r for r in rep if not r["ok"]]
    assert n >= 0.9 * len(rep), (f"{len(bad)} of {len(rep)} looped rows: onset and period of loops.json do not mark the first loop cycle "
                                 f"(onset = index into ids of the first token of the first cycle): {bad[:4]}")
    return {"rows": len(rep), "ok": n, "not_ok": bad,
            "detector_same_onset_and_period": sum((r["detector_onset"], r["detector_period"]) == (r["onset"], r["period"]) for r in rep)}


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


def tiny_pair(L, W, vocab):
    """Random Olmo3 models (the class of the real ones: sliding-window and full layers, post-norm MLP). 'RL' is the base plus noise."""
    from transformers import Olmo3Config, Olmo3ForCausalLM
    cfg = Olmo3Config(vocab_size=vocab, hidden_size=16, intermediate_size=W, num_hidden_layers=L, num_attention_heads=2, sliding_window=256,
                      pad_token_id=None, eos_token_id=1, initializer_range=0.3)
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
    """Without --edit: a synthetic edit file. --loops synthetic: a loops.json (seven planted loops and a row that did not loop)."""
    g = np.random.default_rng(1)
    if not a.edit:
        a.edit = str(out / "dry_edit.json")
        M5.dump(a.edit, {"name": "dry", "zero": {"0": [1, 5, 9], "2": [3, 4]}, "copy_neurons": {"3": [7], "1": []}})
    if a.loops == "synthetic":
        rows = [{"problem_index": 99, "looped": False}]
        for i in range(7):
            pre, p = int(g.integers(400, 900)), int(g.integers(5, 40))
            ids = g.integers(2, vocab, 20 + pre).tolist() + np.tile(g.integers(2, vocab, p), 600 // p).tolist()
            rows.append({"problem_index": 100 + i, "ids": ids, "n_prompt": 20, "n_context": 20 + pre // 3, "onset": 20 + pre, "period": p,
                         "half": "AB"[i % 2]})
        a.loops = str(out / "dry_loops.json")
        M5.dump(a.loops, {"rows": rows})


# ------------------------------------------------------------------------------------------------ model
def layout(m):
    """The modules this job reads; (layers, neurons per layer). Olmo3: the MLP's output passes post_feedforward_layernorm."""
    x = torch.linspace(-3, 3, 13)
    for l in m.model.layers:
        assert torch.allclose(l.mlp.act_fn(x), torch.nn.functional.silu(x)), "the MLP's activation is not SiLU"
        for n in ("gate_proj", "up_proj", "down_proj"):
            assert isinstance(getattr(l.mlp, n), torch.nn.Linear) and getattr(l.mlp, n).bias is None, n
        assert l.post_feedforward_layernorm.weight.shape == m.model.norm.weight.shape == (m.lm_head.weight.shape[1],)
    return len(m.model.layers), m.model.layers[0].mlp.down_proj.in_features


def record(model, seqs, cols, dev, dt, n_sub=0, seed=0):
    """a of the neurons cols[l] (columns in layer order) at every scored position of every sequence: [positions, neurons]. With
    n_sub: also |a| of every neuron of each layer at n_sub random scored positions per sequence. One pass of the backbone per
    sequence, no cache, no logits."""
    layers, cur, got = model.model.layers, {}, {}
    sub = [[] for _ in layers]

    def mk(l):
        def hook(_, args):
            x = args[0][0, cur["lo"]:]
            got[l] = x[:, cols[l]].to(dt)
            if n_sub:
                sub[l].append(x[cur["sub"]].abs().to(dt))
        return hook

    hooks = [layers[l].mlp.down_proj.register_forward_pre_hook(mk(l)) for l in range(len(layers))]
    g, out = torch.Generator().manual_seed(seed), []
    for s in seqs:
        n = len(s["ids"]) - 1 - s["n_prompt"]
        cur.update(lo=s["n_prompt"], sub=torch.randperm(n, generator=g)[:n_sub].to(dev))
        model.model(input_ids=torch.tensor(s["ids"][:-1], device=dev)[None], use_cache=False)
        out.append(torch.cat([got[l] for l in range(len(layers))], 1))
    for h in hooks:
        h.remove()
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
    in the windows [OFF_LO, -50), [-50, 0), [0, period), [period, OFF_HI]."""
    n, K = OFF_HI - OFF_LO + 1, A.shape[1]
    tot, tot_abs, cnt = torch.zeros(n, K, device=A.device), torch.zeros(n, K, device=A.device), torch.zeros(n, device=A.device)
    win, wcnt = torch.zeros(4, K, device=A.device), torch.zeros(4, device=A.device)
    for s, m, o, p in events:
        lo, hi = max(o + OFF_LO, 0), min(o + OFF_HI + 1, m)
        x, j = A[s + lo:s + hi].float(), lo - o - OFF_LO
        tot[j:j + len(x)] += x
        tot_abs[j:j + len(x)] += x.abs()
        cnt[j:j + len(x)] += 1
        for w, (b, e) in enumerate(((OFF_LO, -50), (-50, 0), (0, p), (p, OFF_HI + 1))):
            b, e = max(o + b, 0), min(o + e, m)
            if e > b:
                win[w] += A[s + b:s + e].float().mean(0)
                wcnt[w] += 1
    c = cnt.clamp(min=1)[:, None]
    return (tot / c).cpu(), (tot_abs / c).cpu(), cnt.cpu(), (win / wcnt.clamp(min=1)[:, None]).cpu(), wcnt.cpu()


# ------------------------------------------------------------------------------------------------ dose: free-running generation
def plan(lengths, steps, batch, budget):
    """Batches of row indices, longest contexts first: at most `batch` rows and rows x (longest context + steps) <= budget."""
    order, out = sorted(range(len(lengths)), key=lambda i: (-lengths[i], i)), []
    while order:
        b = max(1, min(batch, budget // (lengths[order[0]] + steps)))
        out.append(order[:b])
        order = order[b:]
    return out


def scale(model, cols, f):
    """Forward pre-hooks on down_proj: the activations of the neurons cols[l] are multiplied by f. Returns the hooks."""
    def mk(idx):
        def hook(_, args):
            args[0][..., idx] *= f
        return hook
    return [model.model.layers[l].mlp.down_proj.register_forward_pre_hook(mk(idx)) for l, idx in enumerate(cols) if len(idx)]


def generate(model, rows, batches, steps, seed, dev, stop_id, cache):
    """Continues each row's context (rows: {key, ctx, step0}) by up to `steps` tokens: token = argmax(logits / TEMP + Gumbel noise),
    the noise of a row at its t-th token drawn from a generator seeded with (seed, key, step0 + t), so it is the same in every
    condition and batch. Left padding, KV cache ('static': transformers' StaticCache, allocated once; 'dynamic': DynamicCache).
    A row ends at the stop token, which is left out, or at the first multiple of CHECK tokens at which loop_scan flags it (the
    flag does not depend on later tokens). Per row: (tokens, stopped)."""
    from transformers import DynamicCache, StaticCache
    g, out = torch.Generator(device=dev), [None] * len(rows)
    assert all(0 <= r["key"] < 1000 and 0 <= r["step0"] and r["step0"] + steps <= 100_000 for r in rows), "noise seed out of range"
    for idx in batches:
        ctx = [rows[i]["ctx"] for i in idx]
        T, B = max(map(len, ctx)), len(idx)
        x = torch.full((B, T), stop_id, dtype=torch.long, device=dev)
        mask = torch.ones((B, T + steps), dtype=torch.long, device=dev)
        for b, c in enumerate(ctx):
            x[b, T - len(c):] = torch.tensor(c, dtype=torch.long, device=dev)
            mask[b, :T - len(c)] = 0
        kv = StaticCache(config=model.config, max_cache_len=T + steps) if cache == "static" else DynamicCache(config=model.config)
        gen, live, end, stop = torch.zeros((B, steps), dtype=torch.long, device=dev), list(range(B)), [steps] * B, set()
        for t in range(steps):
            n0 = T + t - x.shape[1]                                             # cached positions; x: the context, then the last token
            for c in range(0, x.shape[1], CHUNK):
                e = min(c + CHUNK, x.shape[1])
                h = model.model(input_ids=x[:, c:e], attention_mask=mask[:, :n0 + e], past_key_values=kv, use_cache=True).last_hidden_state[:, -1]
            z = model.lm_head(h).float() / TEMP
            assert torch.isfinite(z).all(), "non-finite logits"
            for b in live:
                r = rows[idx[b]]
                g.manual_seed((seed * 1000 + r["key"]) * 100_000 + r["step0"] + t)
                z[b] -= torch.log(-torch.log(torch.rand(z.shape[1], generator=g, device=dev).clamp_min(1e-30)))
            x = z.argmax(-1, keepdim=True)
            gen[:, t] = x[:, 0]
            new = x[:, 0].tolist()
            for b in list(live):
                if new[b] == stop_id:
                    end[b] = t
                    stop.add(b)
                    live.remove(b)
                elif (t + 1) % CHECK == 0 and loop_scan(gen[b, :t + 1].tolist()) is not None:
                    end[b] = t + 1
                    live.remove(b)
            if not live:
                break
        for b, i in enumerate(idx):
            out[i] = (gen[b, :end[b]].tolist(), b in stop)
        del kv
        if dev == "cuda":
            torch.cuda.empty_cache()
    return out


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
    ap.add_argument("--steps", type=int, default=800, help="dose: generated tokens")
    ap.add_argument("--batch", type=int, default=16, help="dose: rows per batch")
    ap.add_argument("--batch-tokens", type=int, default=64_000, help="dose: rows x (longest context + steps) per batch (0.52 MB of KV cache per token)")
    ap.add_argument("--factors", default="0,0.5,1,2", help="dose: write factors of the selected set (1 is always run, twice)")
    ap.add_argument("--ref-factors", default="0,2", help="dose: write factors of the reference set")
    ap.add_argument("--cache", default="static", choices=("static", "dynamic"))
    ap.add_argument("--seed", type=int, default=0, help="reference neurons, subsamples, random contexts")
    ap.add_argument("--noise-seed", type=int, default=0, help="dose: sampling noise")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        a.rows, a.loop_rows, a.max_neurons, a.steps = 4, 3, 64, 260
    t0, tm = time.time(), {}
    assert a.out, "no --out and no $OUT_DIR"
    assert re.fullmatch(r"[0-9a-f]{40}", a.commit), f"--commit {a.commit!r} is not a full git sha"
    assert a.dry_run or a.edit, "--edit is required"
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / "metrics.json").exists(), f"{out}/metrics.json exists: one fresh directory per run"
    detector_selfcheck()
    fz = json.loads((M5.D4 / "frozen4.json").read_text())
    L, W = (4, 64) if a.dry_run else (32, 11008)

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
    name, sel = read_edit(a.edit, L, W)
    n_edit = sum(map(len, sel.values()))
    if a.max_neurons and n_edit > a.max_neurons:
        sel = subsample(sel, a.max_neurons, a.seed)
    ref = reference(sel, W, a.seed)
    cols = [sel.get(l, []) + ref.get(l, []) for l in range(L)]
    U = [(s, l, n) for l in range(L) for s, d in (("selected", sel), ("reference", ref)) for n in d.get(l, [])]
    is_sel = torch.tensor([u[0] == "selected" for u in U])
    loops, held, loops_info = [], [], None
    if a.loops:
        loops, not_looped = read_loops(a.loops)
        loops_info = {"sha256": M5.sha(a.loops), "rows_not_looped": not_looped, "onset_check": check_onsets(loops)}
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
        base, rl = tiny_pair(L, W, vocab)
        m["models"] = {"dry_run": True, "class": type(base).__name__}
    else:
        dev, dt = "cuda", torch.float16
        m["gpu"] = torch.cuda.get_device_name(0)
        base, ib = M5.load(fz, "base", dev)
        rl, ir = M5.load(fz, "rl", dev)
        m["models"], vocab = {"base": ib, "rl": ir}, ib["vocab_size"]
        assert vocab == ir["vocab_size"]
    assert layout(base) == layout(rl) == (L, W) and max(stop_id, max(max(s["ids"]) for s in seqs)) < vocab
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
    win, wcnt = tr["loop"][3], tr["loop"][4]
    wn = ("before", "just_before", "first_cycle", "later")
    units = [{"set": s, "layer": l, "neuron": n, "normal_mean": r4(mu[k]), "normal_sd": r4(sd[k]), "windows": dict(zip(wn, rl4(win[:, k]))),
              "trace": rl4(tr["loop"][0][:, k])} for k, (s, l, n) in enumerate(U)]
    zw = (win - mu) / sd
    onset_sum = {s: {w: {"mean_z": r4(zw[i, mask].mean()), "mean_abs_z": r4(zw[i, mask].abs().mean())} for i, w in enumerate(wn)}
                 for s, mask in (("selected", is_sel), ("reference", ~is_sel))}
    head = {"what": "SPEC1 Part I item 4; fields in the docstring of jobs/describe_neurons.py", "edit": name,
            "note": "offset 0 is the position that reads the first token of the first loop cycle (the position at offset -1 wrote it); the "
                    "repeated text starts at offset = period. z = (mean a - normal_mean) / normal_sd per neuron, normal text = the stored answers. "
                    "'normal' aligns the same window on the middle of each stored answer (the matched control).",
            "offsets": list(range(OFF_LO, OFF_HI + 1)), "windows": {"before": [OFF_LO, -50], "just_before": [-50, 0], "first_cycle": "[0, period)",
                                                                    "later": f"[period, {OFF_HI}]", "rows_per_window": [int(c) for c in wcnt]},
            "rows": [{"problem_index": s["idx"], "onset": s["onset"], "period": s["period"], "half": s["half"], "tokens": len(s["ids"])} for s in loops],
            "median_period": p_med, "window_summary": onset_sum, "sets": sets}
    dump_lines(out / "onset_trace.json", head, "neurons", units)
    del A
    tm["onset_trace_s"] = time.time() - t

    # item 5: dose.json
    t = time.time()
    rows = [{"key": s["idx"], "restart": (r := max(s["onset"] - RESTART, s["n_context"])), "ctx": s["ids"][:r], "step0": r - s["n_context"],
             "stored": s["ids"][r:r + a.steps]} for s in held]
    batches = plan([len(r["ctx"]) for r in rows], a.steps, a.batch, a.batch_tokens)
    setcols = {"selected": [c[:len(c) // 2] for c in colsT], "reference": [c[len(c) // 2:] for c in colsT]}
    res, dose, n_tok = {}, [], 0
    for cname, s, f in conds:
        tc = time.time()
        hooks = scale(base, setcols[s], f)
        res[cname] = generate(base, rows, batches, a.steps, a.noise_seed, dev, stop_id, a.cache)
        if cname == "selected_x1":
            other = "dynamic" if a.cache == "static" else "static"
            alt = generate(base, rows, batches[:1], min(a.steps, CACHE_STEPS), a.noise_seed, dev, stop_id, other)
        for h in hooks:
            h.remove()
        per = []
        for r, (toks, stopped), (one, _) in zip(rows, res[cname], res["selected_x1"]):
            lt = loop_scan(toks)
            diff, n = [i for i, (x, y) in enumerate(zip(toks, one)) if x != y], min(len(toks), len(r["stored"]))
            per.append({"problem_index": r["key"], "looped": lt is not None, "flagged_at": lt and lt[0], "period": lt and lt[1], "onset_step": lt and lt[2],
                        "generated": len(toks),
                        "stopped": stopped, "same_as_x1_until": diff[0] if diff else min(len(toks), len(one)),
                        "same_as_stored": n > 0 and toks[:n] == r["stored"][:n], "tail": tok.decode(toks[-120:]), "tokens": toks})
        k = sum(p["looped"] for p in per)
        dose.append({"name": cname, "set": s, "factor": f, "loops": k, "n": len(per), "loop_rate": k / len(per), "stopped": sum(p["stopped"] for p in per),
                     "same_as_stored": sum(p["same_as_stored"] for p in per), "seconds": time.time() - tc, "rows": per})
        n_tok += sum(p["generated"] for p in per)
        print(f"{M5.utc()} dose {cname}: {k} of {len(per)} rows loop, {dose[-1]['stopped']} stopped, {time.time() - tc:.0f} s", flush=True)
    same = [x == y for x, y in zip(res["selected_x1"], res["selected_x1_repeat"])]
    first = [(res["selected_x1"][i][0][:CACHE_FIRST], alt[i][0][:CACHE_FIRST]) for i in batches[0]]
    agree = float(np.mean([x == y for p, q in first for x, y in zip(p, q)] + [len(p) == len(q) for p, q in first]))
    ctrl = {"same_noise": {"what": "factor 1 run twice: rows with identical tokens", "rows_identical": sum(same), "n": len(same), "pass": all(same)},
            "cache": {"what": f"the first batch at factor 1 with the {other} cache: share of the first {CACHE_FIRST} tokens equal to the {a.cache} run's",
                      "rows": len(first), "share": agree, "rows_identical_all_steps": sum(alt[i] == (res["selected_x1"][i][0][:len(alt[i][0])], alt[i][1])
                                                                                          for i in batches[0]), "steps": min(a.steps, CACHE_STEPS),
                      "pass": agree >= CACHE_MIN}}
    head = {"what": "SPEC1 Part I item 5; fields in the docstring of jobs/describe_neurons.py", "edit": name,
            "note": "factor f multiplies the set's activations at every position, the context included; the MLP's output then passes "
                    "post_feedforward_layernorm, which rescales it. same_as_stored: the row's tokens equal the continuation stored in loops.json "
                    "as far as both go (expected at factor 1 when --noise-seed is Part L's seed: same model, context and noise).",
            "config": {"restart_before_onset": RESTART, "steps": a.steps, "temperature": TEMP, "top_p": 1.0, "noise_seed": a.noise_seed, "cache": a.cache,
                       "batches": [len(b) for b in batches], "detector": {"window": WIN, "matches": NEED, "periods": [P_MIN, P_MAX]}},
            "rows": [{"problem_index": r["key"], "restart": r["restart"], "noise_step0": r["step0"], "context_tokens": len(r["ctx"])} for r in rows],
            "controls": ctrl, "summary": [{k: c[k] for k in ("name", "set", "factor", "loops", "n", "loop_rate", "stopped", "same_as_stored")} for c in dose]}
    dump_lines(out / "dose.json", head, "conditions", dose)
    tm["dose_s"] = time.time() - t
    tm["dose_tokens_per_s"] = n_tok / tm["dose_s"]

    m.update(dose=head["summary"], onset_windows=onset_sum)
    finish({k: v["pass"] for k, v in ctrl.items()})


if __name__ == "__main__":
    main()
