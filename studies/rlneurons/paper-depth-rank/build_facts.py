"""The verified data layer of the short paper on the rank and depth split of the RL weight update ("direction 1 finishes,
directions 2-8 add right answers; layers 0-10 add right answers, layers 22-31 finish").

    uv run --no-project --with numpy python studies/rlneurons/paper-depth-rank/build_facts.py

Reads only files in git: the per-problem rows of the run folders (results/day1_3, results/xreward/{dial15_s4_vs_base_cue-01,depth3})
and the rows frozen by prep_rows.py (data/math, data/code: cells whose rows were only in runs/). Every number is recomputed
from rows, then asserted against the stored readouts (depth3/readout.json, edits/readout.json, code_dial and code_depth
readout.json). Board text is compared, not asserted: `board_checks` lists each board number with the recomputed one.
Writes, next to this file:
  facts.json          cells, changes from the cued base, the headline contrasts (a)-(e), edit sizes, pre-registration, checks
  problem_table.json  per cell and problem: right rate and cut-off rate (mean over the cell's samples), for the figure
facts.json `transitions` (added last, so every earlier key is unchanged): per cell, the 3 x 3 table of base outcome by cell
outcome, each cell sample paired with the base sample of the same seed; nulls from base vs base; additivity of the rank split.
New cells (direction 1 at 1.5x, more seeds of directions 2-8) enter only `transitions`, from NEW_ROWS when their files exist.

Conventions: per problem, a cell's rate = mean over its samples (first attempt only). A - B = mean over problems of
(rate_A - rate_B), in points (x 100 / n problems; x 3.28 = problems on hard328, x 5.38 on Code). Interval: paired bootstrap over
problems, 10,000 resamples, numpy default_rng(0) for every interval (so all intervals of one n share resamples), percentiles
2.5/97.5 (95 %) and 0.5/99.5 (99 %). "Cut off" = cap_hit (the answer reached 16,384 generated tokens). "Finished wrong" = not cut
off and scored wrong (hard328: score_v3 0; Code: passed false, including answers with no code block). Tokens = n_new.
"""
import json
import pathlib

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
RES = STUDY / "results"
X = RES / "xreward"
D3 = X / "depth3"
NB = X / "normband"
B = 10000
CHECKS, BOARD = [], []


def rel(p):
    return str(pathlib.Path(p).resolve().relative_to(ROOT))


def r2(x):
    return None if x is None else round(float(x), 2)


def check(name, got, want, tol=0.0):
    assert abs(got - want) <= tol + 1e-9, f"{name}: recomputed {got}, stored {want} (tolerance {tol})"
    CHECKS.append({"name": name, "recomputed": r2(got), "stored": want, "tolerance": tol})


def board(item, what, board_value, recomputed, tol):
    BOARD.append({"item": item, "what": what, "board": board_value, "recomputed": r2(recomputed),
                  "agrees": bool(abs(board_value - recomputed) <= tol), "tolerance": tol})


# ---------------------------------------------------------------- cells: {"src", "samples", "p": {problem: [sample dicts]}}
def read(path):
    return [json.loads(l) for l in pathlib.Path(path).read_text().splitlines()]


def math_cell(parts):
    """parts: [(path, sample or None = take r["sample"])] -> cell; sample dict {s right, c cut off, t tokens}."""
    by = {}
    for path, s in parts:
        for r in read(path):
            if r.get("attempt", 0) != 0:
                continue
            k = r["sample"] if s is None else s
            assert r["seed"] == 3000000 + 10000 * k + r["problem_index"], (path, r["problem_index"])
            by.setdefault(r["problem_index"], {})[k] = {"s": int(r["score_v3"]), "c": bool(r["cap_hit"]), "t": r["n_new"]}
    ks = sorted(next(iter(by.values())))
    assert len(by) == 328 and all(sorted(v) == ks for v in by.values()), parts
    return {"src": [rel(p) for p, _ in parts], "samples": ks, "p": {p: [v[k] for k in ks] for p, v in sorted(by.items())}}


def code_cell(name):
    path = HERE / "data" / "code" / f"{name}.jsonl"
    rows = read(path)
    return {"src": [rel(path)], "samples": [0], "p": {r["uid"]: [{"s": int(r["passed"]), "c": bool(r["cap_hit"]), "t": r["n_new"],
                                                                  "nb": r["mode"] == "none"}] for r in rows}}


def load_math():
    s0 = D3 / "sample0_rows"
    run = lambda c, s: (D3 / f"{c}_s{s}-01" / "rows.jsonl", None)
    fz = lambda c: (HERE / "data" / "math" / f"{c}.jsonl", 0)
    return {
        "base_cue": math_cell([(RES / "day1_3/hard328_base_cue_s4r2-01/rows.jsonl", None)]),
        "all8": math_cell([(X / "dial15_s4_vs_base_cue-01/rows.jsonl", None)]),
        "L0-10": math_cell([(s0 / "top8x1.5_L0-10_math31.jsonl", None)] + [run("top8x1.5_L0-10_math31", s) for s in (1, 2, 3)]),
        "L11-21": math_cell([(s0 / "top8x1.5_L11-21_math31.jsonl", None), run("top8x1.5_L11-21_math31", 1)]),
        "L22-31": math_cell([(s0 / "top8x1.5_L22-31_math31.jsonl", None), run("top8x1.5_L22-31_math31", 1)]),
        "d2-8": math_cell([(NB / "top8x1.5_d2-8_math31_s0-01/rows.jsonl", None), run("top8x1.5_d2-8_math31", 1)]),
        "rand_L0-10": math_cell([run("rand8x1.5_L0-10_math31", 1)]),
        "rand8x1.5": math_cell([(s0 / "rand8x1.5_math31.jsonl", None)]),
        **{c: math_cell([fz(c)]) for c in ("top1x1", "top1x2", "top1x3", "top8x0.5", "top8x1", "top8x2", "top8x3",
                                           "rand8x1", "rand8x2", "rand8x3", "base_cue_rerun", "top8x1.5_rerun")},
        "top1x1.5": math_cell([(NB / f"top1x1.5_math31_s{s}-01/rows.jsonl", None) for s in (0, 1)]),
        "L22-31x3.0": math_cell([(NB / f"top8x3_L22-31_math31_s{s}-01/rows.jsonl", None) for s in (0, 1)]),
        "L22-31x4.5": math_cell([(NB / "top8x4.5_L22-31_math31_s1-01/rows.jsonl", None)]),
        "L0-10x0.2": math_cell([(NB / "top8x0.2_L0-10_math31_s1-01/rows.jsonl", None)]),
    }


MATH_LABEL = {"base_cue": "base + cue", "all8": "top-8 directions x1.5, all layers", "L0-10": "top-8 x1.5, layers 0-10",
              "L11-21": "top-8 x1.5, layers 11-21", "L22-31": "top-8 x1.5, layers 22-31", "d2-8": "directions 2-8 x1.5, all layers",
              "rand_L0-10": "random rank-8 x1.5, layers 0-10 (singular values of the L0-10 edit)",
              "rand8x1.5": "random rank-8 x1.5, all layers", "top1x1": "direction 1 only x1", "top1x2": "direction 1 only x2",
              "top1x3": "direction 1 only x3", "top8x0.5": "top-8 x0.5", "top8x1": "top-8 x1", "top8x2": "top-8 x2", "top8x3": "top-8 x3",
              "rand8x1": "random rank-8 x1", "rand8x2": "random rank-8 x2", "rand8x3": "random rank-8 x3",
              "base_cue_rerun": "base + cue, a second job with the seeds of sample 0 (job 1114-151534-e72c)",
              "top8x1.5_rerun": "top-8 x1.5, a second job with the seeds of sample 0 (job 1115-031229-5991)",
              "top1x1.5": "direction 1 only x1.5", "L22-31x3.0": "top-8 x3.0, layers 22-31 (2x the band cell)",
              "L22-31x4.5": "top-8 x4.5, layers 22-31 (3x the band cell; broken: ' which ' loops)",
              "L0-10x0.2": "top-8 x0.2, layers 0-10 (0.133x the band cell)"}
CODE_LABEL = {"base_cue": "base + Code cue", "rl_plain": "RL-Zero-Code 3.1, plain", "rand8x1.5": "random rank-8 x1.5 (norm of Code's x1.5)",
              "top8x1": "Code top-8 x1", "top8x1.5": "Code top-8 x1.5, all layers", "top8x2": "Code top-8 x2",
              "math_top8x1.5": "RL-Math top-8 x1.5 on code", "L0-10": "Code top-8 x1.5, layers 0-10",
              "L11-21": "Code top-8 x1.5, layers 11-21", "L22-31": "Code top-8 x1.5, layers 22-31"}


# ---------------------------------------------------------------- statistics
def rate(c, key, samples=None):
    """per-problem mean over the chosen samples; key: s right, c cut off, fw finished wrong, t tokens."""
    idx = [c["samples"].index(s) for s in (samples or c["samples"])]
    f = {"s": lambda x: x["s"], "c": lambda x: x["c"], "fw": lambda x: (not x["c"]) and x["s"] == 0, "t": lambda x: x["t"]}[key]
    return np.array([np.mean([float(f(v[i])) for i in idx]) for _, v in sorted(c["p"].items())])


def boot(d):
    m = d[np.random.default_rng(0).integers(0, len(d), (B, len(d)))].mean(1)
    return [r2(x) for x in np.percentile(m, [2.5, 97.5])], [r2(x) for x in np.percentile(m, [0.5, 99.5])]


def diff(A, Bc, key, sa=None, sb=None):
    assert sorted(A["p"]) == sorted(Bc["p"])
    scale = 1.0 if key == "t" else 100.0
    d = scale * (rate(A, key, sa) - rate(Bc, key, sb))
    ci95, ci99 = boot(d)
    n = len(d)
    out = {"value": r2(d.mean()), "ci95": ci95, "ci99": ci99, "n": n, "unit": "tokens per answer" if key == "t" else "points"}
    if key != "t":
        out["problems"] = r2(d.mean() * n / 100)
    out["samples_A"], out["samples_B"] = sa or A["samples"], sb or Bc["samples"]
    return out


def contrast(A, Bc, sa=None, sb=None, keys=("s", "c", "fw", "t")):
    names = {"s": "right", "c": "cut_off", "fw": "finished_wrong", "t": "tokens"}
    return {names[k]: diff(A, Bc, k, sa, sb) for k in keys}


def sub(c, samples):
    """the same cell restricted to some of its samples"""
    idx = [c["samples"].index(s) for s in samples]
    return {"src": c["src"], "samples": list(samples), "p": {p: [v[i] for i in idx] for p, v in c["p"].items()}}


def stats(c, label):
    n = len(c["p"])
    per = lambda f: [int(sum(f(v[i]) for v in c["p"].values())) for i in range(len(c["samples"]))]
    right, cut = per(lambda x: x["s"]), per(lambda x: x["c"])
    fw = per(lambda x: (not x["c"]) and x["s"] == 0)
    toks = [x["t"] for v in c["p"].values() for x in v]
    out = {"label": label, "source": c["src"], "n_problems": n, "samples": c["samples"], "n_samples": len(c["samples"]),
           "right_per_sample": right, "right_mean": r2(np.mean(right)), "right_pct": r2(100 * np.mean(right) / n),
           "cut_off_per_sample": cut, "cut_off_mean": r2(np.mean(cut)), "finished_wrong_per_sample": fw, "finished_wrong_mean": r2(np.mean(fw)),
           "tokens_per_answer": r2(np.mean(toks)), "right_of_finished_pct": r2(100 * sum(right) / (n * len(right) - sum(cut))),
           "cut_off_but_right": int(sum(x["s"] for v in c["p"].values() for x in v if x["c"]))}
    if "nb" in next(iter(c["p"].values()))[0]:
        out["no_code_block"] = int(sum(x["nb"] for v in c["p"].values() for x in v))
        out["no_code_block_finished"] = int(sum(x["nb"] and not x["c"] for v in c["p"].values() for x in v))
    return out


# ---------------------------------------------------------------- edit sizes
def edit_sizes():
    ed = json.loads((X / "edits/readout.json").read_text())["cells"]
    fz = json.loads((HERE / "data/edit_totals.json").read_text())
    xs = json.loads((RES / "xshift/run-01/metrics.json").read_text())
    base_rms = xs["base"]["rms"]
    keep = ("add_norm", "written_norm", "add_rel", "ref_norm", "n_edited")
    rows = {}
    m_ed = {"all8": "top8x1.5_math31", "L0-10": "top8x1.5_L0-10_math31", "L11-21": "top8x1.5_L11-21_math31", "L22-31": "top8x1.5_L22-31_math31",
            "rand8x1.5": "rand8x1.5_math31", "top1x1": "top1_math31", "top1x2": "top1x2_math31", "top1x3": "top1x3_math31",
            "top8x0.5": "top8x0.5_math31", "top8x1": "top8_math31", "top8x2": "top8x2_math31", "top8x3": "top8x3_math31",
            "rand8x1": "rand8_math31", "rand8x2": "rand8x2_math31", "rand8x3": "rand8x3_math31"}
    for cell, k in m_ed.items():
        e = ed[k]["edit"]
        rows[f"math {cell}"] = {"weight": {f: r2(e[f]) if f != "add_rel" else float(f"{e[f]:.3g}") for f in keep},
                                "weight_source": rel(X / "edits/readout.json") + f" cells.{k}.edit"}
    for cell, folder in (("d2-8", "top8x1.5_d2-8_math31_s1-01"), ("rand_L0-10", "rand8x1.5_L0-10_math31_s1-01")):
        e = json.loads((D3 / folder / "run.json").read_text())["edit"]
        rows[f"math {cell}"] = {"weight": {f: (r2(e[f]) if f != "add_rel" else float(f"{e[f]:.3g}")) for f in keep if f in e},
                                "weight_source": rel(D3 / folder / "run.json") + " edit"}
        check(f"edit add_norm math {cell}: run.json = frozen edit.json", e["add_norm"], fz[f"math {cell}"]["add_norm"], 1e-9)
    for cell in ("all8", "L0-10", "L11-21", "L22-31", "rand8x1.5", "top1x1"):
        k = {"all8": "top8x1.5"}.get(cell, cell)
        if f"math {k}" in fz:
            check(f"edit add_norm math {cell}: edits/readout = frozen edit.json", rows[f"math {cell}"]["weight"]["add_norm"], r2(fz[f"math {k}"]["add_norm"]), 0.006)
    for cell in CODE_LABEL:
        if f"code {cell}" in fz:
            e = fz[f"code {cell}"]
            rows[f"code {cell}"] = {"weight": {f: (r2(e[f]) if f != "add_rel" else float(f"{e[f]:.3g}")) for f in keep},
                                    "weight_source": rel(HERE / "data/edit_totals.json") + f" (runs/{e['job']}/edit.json totals)"}
    for cell, k in m_ed.items():
        if k in xs["edits"]:
            r = xs["edits"][k]["shift"]["all"]["rms"]
            rows[f"math {cell}"]["activation_rms_shift"] = {"layer24": r2(r[24]), "layer31": r2(r[31]), "base_rms_layer24": r2(base_rms[24]),
                                                            "base_rms_layer31": r2(base_rms[31])}
    rd = json.loads((RES / "xshift/run-01/readout.json").read_text())["edits"]
    check("xshift layer-24 rms, L22-31 (board result-98de28: 0.83)", xs["edits"]["top8x1.5_L22-31_math31"]["shift"]["all"]["rms"][24],
          rd["top8x1.5_L22-31_math31"]["rms_shift"], 1e-9)
    return {"what": "size of each edit. weight: add_norm = Frobenius norm of the intended weight change summed over edited matrices "
                    "(sqrt of the sum of squares); written_norm = the change actually written after stochastic BF16 rounding (rounding "
                    "noise included); add_rel = add_norm / ref_norm (norm of the edited base matrices). activation_rms_shift: RMS over 6,144 "
                    "positions of 48 stored base answers of (edited - base) residual stream at the output of layer 24 and of layer 31 "
                    "(0-based; before the final norm), float32, results/xshift/run-01/metrics.json; not measured for d2-8, rand_L0-10 or any Code cell.",
            "cells": rows,
            "norm_matched_cells": {
                "rand_L0-10 vs L0-10": "exactly matched (same singular values, random directions): add_norm 1.06 both",
                "rand8x1.5 vs all8 (math)": "matched: 1.90 both; Code rand8x1.5 matched to Code x1.5: 1.64",
                "bands": "not matched by design: each band is its own top-8 at x1.5. Math add_norm L0-10 1.06, L11-21 1.03, L22-31 1.20 "
                         "(late band largest); Code 0.97, 0.94, 0.94",
                "late band": "no cell matches the late band to another band's size explicitly, no random late-band cell, no late band at "
                             "another multiplier"}}


# ---------------------------------------------------------------- transitions (base outcome -> cell outcome, same seed)
# cells that enter only `transitions`: every rows file matching a pattern (relative to the study) is read; the sample comes from
# the seed (3,000,000 + 10,000 s + i). Missing files are skipped: the cell appears when its rows are frozen or committed.
NEW_ROWS = {
    "top1x1.5": ["results/xreward/*/top1x1.5_math31_s*-01/rows.jsonl", "results/xreward/*/top8x1.5_d1_math31_s*-01/rows.jsonl",
                 "paper-depth-rank/data/math/top1x1.5*.jsonl"],
    "d2-8_all_seeds": ["results/xreward/*/top8x1.5_d2-8_math31_s*-01/rows.jsonl", "paper-depth-rank/data/math/d2-8*.jsonl"],
}
OUT3 = ("R", "FW", "C")   # right (score 1, including the rare right-but-cut-off answer), finished wrong, cut off and wrong


def any_rows(patterns):
    paths = sorted({p for pat in patterns for p in STUDY.glob(pat)})
    if not paths:
        return None
    by = {}
    for path in paths:
        for r in read(path):
            if r.get("attempt", 0) != 0:
                continue
            s = (r["seed"] - 3000000 - r["problem_index"]) // 10000
            assert s not in by.get(r["problem_index"], {}), (path, r["problem_index"], s)
            by.setdefault(r["problem_index"], {})[s] = {"s": int(r["score_v3"]), "c": bool(r["cap_hit"]), "t": r["n_new"]}
    ks = sorted(next(iter(by.values())))
    assert len(by) == 328 and all(sorted(v) == ks for v in by.values()), paths
    return {"src": [rel(p) for p in paths], "samples": ks, "p": {p: [v[k] for k in ks] for p, v in sorted(by.items())}}


def outcome(x):
    return "R" if x["s"] == 1 else ("C" if x["c"] else "FW")


def tables(A, Bc, pairs):
    """pairs: [(sample of A, sample of B)] -> per problem, per (base outcome, cell outcome): mean count over the pairs [n, 3, 3]."""
    ps = sorted(A["p"])
    assert ps == sorted(Bc["p"])
    T = np.zeros((len(ps), 3, 3))
    for i, p in enumerate(ps):
        for sa, sb in pairs:
            a, b = A["p"][p][A["samples"].index(sa)], Bc["p"][p][Bc["samples"].index(sb)]
            T[i, OUT3.index(outcome(b)), OUT3.index(outcome(a))] += 1 / len(pairs)
    return T


def summarize(T):
    """from per-problem tables: (a) gains by base outcome, (b) losses by cell outcome, (c) net through finishing / among finished."""
    R, FW, C = 0, 1, 2
    q = {"gained_right_from_cut_off": T[:, C, R], "gained_right_from_finished_wrong": T[:, FW, R],
         "lost_right_to_cut_off": T[:, R, C], "lost_right_to_finished_wrong": T[:, R, FW],
         "base_cut_off_now_finished_wrong": T[:, C, FW], "base_finished_wrong_now_cut_off": T[:, FW, C]}
    q["net_right_through_finishing (C->R minus R->C)"] = q["gained_right_from_cut_off"] - q["lost_right_to_cut_off"]
    q["net_right_among_finished (FW->R minus R->FW)"] = q["gained_right_from_finished_wrong"] - q["lost_right_to_finished_wrong"]
    q["net_right_total"] = q["net_right_through_finishing (C->R minus R->C)"] + q["net_right_among_finished (FW->R minus R->FW)"]
    q["problems_changing_outcome"] = T.sum((1, 2)) - np.einsum("pii->p", T)
    return q


def boot_sum(v):
    m = v[np.random.default_rng(0).integers(0, len(v), (B, len(v)))].sum(1)
    return [r2(x) for x in np.percentile(m, [2.5, 97.5])]


def transition_block(A, Bc, pairs, null_q=None):
    T = tables(A, Bc, pairs)
    q = summarize(T)
    out = {"pairs (cell sample, base sample)": pairs,
           "table_problems (rows: base R/FW/C, cols: cell R/FW/C; mean over pairs)": [[r2(x) for x in row] for row in T.sum(0)],
           "counts_problems": {k: {"value": r2(v.sum()), "ci95": boot_sum(v)} for k, v in q.items()}}
    if null_q is not None:
        out["excess_over_base_vs_base_problems"] = {k: {"value": r2((v - null_q[k]).sum()), "ci95": boot_sum(v - null_q[k])} for k, v in q.items()}
    return out, q


def transitions(M, C):
    base, b = M["base_cue"], C["base_cue"]
    new = {k: c for k, c in ((k, any_rows(p)) for k, p in NEW_ROWS.items()) if c is not None}
    allm = {**{k: M[k] for k in ("all8", "top1x1", "top1x2", "top1x3", "d2-8", "L0-10", "L11-21", "L22-31", "rand_L0-10", "rand8x1.5")}, **new,
            **{k: M[k] for k in ("L22-31x3.0", "L22-31x4.5", "L0-10x0.2")}}
    ordered = [(a, c) for a in base["samples"] for c in base["samples"] if a != c]
    nullT = tables(base, base, ordered)
    null_q = summarize(nullT)
    null, _ = transition_block(base, base, ordered)
    rerun, _ = transition_block(M["base_cue_rerun"], base, [(0, 0)])
    out = {"what": "per problem and seed: the base outcome (sample with the same seed) and the cell outcome, each R (right, score 1), FW "
                   "(finished wrong) or C (cut off at 16,384 and wrong). Counts in problems of 328 (Code 538), averaged over the cell's "
                   "samples, each paired with the base sample of the same seed. 95 % intervals: paired bootstrap over problems of the "
                   "sum, 10,000 resamples, default_rng(0). net_right_total = cell right - base right on the paired samples. "
                   "excess_over_base_vs_base: cell count minus the base-vs-base count of the same problem, bootstrapped together.",
           "hard328_null_base_vs_base": {"what": "base sample a as 'cell' against base sample b, all 12 ordered pairs of samples 0-3 "
                                                 "(different seeds): the churn between two samples of the same model; symmetric, so net = 0",
                                         **null},
           "hard328_null_same_seed_rerun": {"what": "base job e72c (seeds of sample 0) against sample 0 of the 4-sample job: same seeds, "
                                                    "different job", **rerun},
           "hard328": {}, "code": {}}
    for k, c in allm.items():
        pairs = [(s, s) for s in c["samples"]]
        blk, _ = transition_block(c, base, pairs, null_q)
        out["hard328"][k] = {"label": MATH_LABEL.get(k, {"top1x1.5": "direction 1 only x1.5",
                                                         "d2-8_all_seeds": "directions 2-8 x1.5, every seed found"}.get(k)),
                             "source": c["src"], **blk}
    for k, c in C.items():
        if k != "base_cue":
            out["code"][k] = {"label": CODE_LABEL[k], **transition_block(c, b, [(0, 0)])[0]}
    out["code_null"] = "no second base sample on Code: no base-vs-base null. The random x1.5 cell (an edit that moves nothing) is the nearest proxy."

    # (e) additivity on right answers: all8 - base vs (d1 - base) + (d2-8 - base); interaction = all8 - d1 - d2-8 + base, per problem
    add = {"what": "per problem rates (mean over each cell's samples); interaction = (all8 - base) - (d1 - base) - (d2-8 - base), points; "
                   "0 = additive. Scale mismatch: all8 and d2-8 are at 1.5x; direction 1 exists at 1x, 2x, 3x (and 1.5x when its rows exist).",
           "variants": {}}
    d28 = new.get("d2-8_all_seeds", M["d2-8"])
    for d1 in [k for k in ("top1x1", "top1x1.5", "top1x2") if k in allm]:
        cs = {"all8": M["all8"], "d1": allm[d1], "d2-8": d28, "base": base}
        common = sorted(set.intersection(*(set(c["samples"]) for c in cs.values())))
        for mode, smp in (("pooled", None), (f"seed-matched samples {common}", common)):
            if smp == []:
                continue
            v = {}
            for key, nm in (("s", "right"), ("c", "cut_off")):
                r = {n: rate(c, key, smp) for n, c in cs.items()}
                inter = 100 * (r["all8"] - r["d1"] - r["d2-8"] + r["base"])
                ci95, ci99 = boot(inter)
                v[nm] = {"all8_minus_base": r2(100 * (r["all8"] - r["base"]).mean()), "d1_minus_base": r2(100 * (r["d1"] - r["base"]).mean()),
                         "d2-8_minus_base": r2(100 * (r["d2-8"] - r["base"]).mean()),
                         "interaction": {"value": r2(inter.mean()), "ci95": ci95, "ci99": ci99}}
            add["variants"][f"{d1}, {mode}"] = {"samples": {n: c["samples"] if smp is None else smp for n, c in cs.items()}, **v}
    out["e_additivity"] = add
    return out


# ---------------------------------------------------------------- normband: rank at matched scale 1.5x, band size (SPEC_normband)
def share(num, den, sa=None):
    """ratio of mean(num) / mean(den) over problems, bootstrap over the same resamples (default_rng(0))."""
    idx = np.random.default_rng(0).integers(0, len(num), (B, len(num)))
    m = num[idx].mean(1) / den[idx].mean(1)
    return {"value": r2(num.mean() / den.mean()), "ci95": [r2(x) for x in np.percentile(m, [2.5, 97.5])],
            "ci99": [r2(x) for x in np.percentile(m, [0.5, 99.5])]}


def normband(M):
    base, all8, d1, d28 = M["base_cue"], M["all8"], M["top1x1.5"], M["d2-8"]
    nb = json.loads((NB / "readout.json").read_text())["cells"]
    checks = []

    def chk(name, got, want, tol=0.0):
        assert abs(got - want) <= tol + 1e-9, f"{name}: recomputed {got}, stored {want}"
        checks.append({"name": name, "recomputed": r2(got), "stored": want, "tolerance": tol})
    for k, rk in (("top1x1.5", "top1x1.5_math31"), ("d2-8", "top8x1.5_d2-8_math31"), ("L22-31x3.0", "top8x3_L22-31_math31"),
                  ("L22-31x4.5", "top8x4.5_L22-31_math31"), ("L0-10x0.2", "top8x0.2_L0-10_math31"), ("base_cue", "base_cue"),
                  ("all8", "top8x1.5_math31"), ("L22-31", "top8x1.5_L22-31_math31"), ("L0-10", "top8x1.5_L0-10_math31")):
        st = stats(M[k], "")
        assert st["samples"] == sorted(nb[rk]["samples"]), (k, nb[rk]["samples"])
        order = [nb[rk]["samples"].index(s) for s in st["samples"]]
        for i, s in enumerate(st["samples"]):
            chk(f"{k} sample {s} right (normband/readout.json)", st["right_per_sample"][i], nb[rk]["right"][order[i]])
            chk(f"{k} sample {s} cap hits (normband/readout.json)", st["cut_off_per_sample"][i], nb[rk]["cap_hits"][order[i]])
        if "minus_base_cue" in nb[rk]:
            for key, nm in (("s", "right"), ("c", "cap")):
                dd = diff(M[k], base, key)
                chk(f"{k} - base {nm} points (normband/readout.json)", dd["value"], nb[rk]["minus_base_cue"][nm]["points"], 0.006)
                chk(f"{k} - base {nm} 95 % low (normband/readout.json; other resamples)", dd["ci95"][0], nb[rk]["minus_base_cue"][nm]["interval95"][0], 0.4)

    # ---- rank at matched scale 1.5x
    def rank(smp):
        cs = {"base": base, "all8": all8, "d1": d1, "d2-8": d28}
        r = {n: {k: rate(c, k, smp) for k in ("s", "c")} for n, c in cs.items()}
        con = lambda a, b_: contrast(cs[a], cs[b_], smp, smp, keys=("s", "c"))
        out = {"samples": smp or {n: c["samples"] for n, c in cs.items()},
               "d1 - base": con("d1", "base"), "d2-8 - base": con("d2-8", "base"), "d1 - d2-8": con("d1", "d2-8"),
               "all8 - d1 (what directions 2-8 add on top)": con("all8", "d1"),
               "all8 - d2-8 (what direction 1 adds on top)": con("all8", "d2-8"), "all8 - base": con("all8", "base")}
        g = {n: r[n]["s"] - r["base"]["s"] for n in ("all8", "d1", "d2-8")}
        out["share of all8's right-answer gain: d1 alone"] = share(g["d1"], g["all8"])
        out["share of all8's right-answer gain: d2-8 alone"] = share(g["d2-8"], g["all8"])
        out["share of all8's right-answer gain: d1 + d2-8"] = share(g["d1"] + g["d2-8"], g["all8"])
        for k, nm in (("s", "right"), ("c", "cut_off")):
            inter = 100 * (r["d1"][k] + r["d2-8"][k] - r["all8"][k] - r["base"][k])
            ci95, ci99 = boot(inter)
            out[f"additivity {nm}: d1 + d2-8 - all8 - base (0 = additive; > 0 = parts sum to more than the whole)"] = {
                "value": r2(inter.mean()), "ci95": ci95, "ci99": ci99, "problems": r2(inter.mean() * 3.28)}
        return out
    R = {"what": "all cells at x1.5, all layers; contrasts in points of 328 with 95 % and 99 % intervals; shares are ratios of mean "
                 "gains over base with bootstrap intervals of the ratio (same resamples)",
         "pooled (base 0-3, all8 0-3, d1 0-1, d2-8 0-1)": rank(None), "seed-matched (samples 0-1 of every cell)": rank([0, 1])}

    # ---- band size
    S = {"what": "SPEC_normband: the late band at 2x and 3x its x1.5 scale, the early band at 0.133x; one sample each (sample 1)",
         "L22-31x3.0 - base": {"pooled (base 0-3)": contrast(M["L22-31x3.0"], base), "seed-matched (sample 1)": contrast(M["L22-31x3.0"], base, [1], [1])},
         "L22-31x3.0 - L22-31x1.5": {"pooled (L22-31 samples 0-1)": contrast(M["L22-31x3.0"], M["L22-31"]),
                                     "seed-matched (sample 1)": contrast(M["L22-31x3.0"], M["L22-31"], [1], [1])},
         "L22-31x4.5 - base": {"pooled (base 0-3)": contrast(M["L22-31x4.5"], base)},
         "L0-10x0.2 - base": {"pooled (base 0-3)": contrast(M["L0-10x0.2"], base), "seed-matched (sample 1)": contrast(M["L0-10x0.2"], base, [1], [1])},
         "L0-10x0.2 - L0-10x1.5 (seed-matched sample 1)": contrast(M["L0-10x0.2"], M["L0-10"], [1], [1]),
         "edit_add_norm": {k: r2(json.loads((NB / f / "run.json").read_text())["edit"]["add_norm"]) for k, f in
                           (("L22-31x3.0", "top8x3_L22-31_math31_s1-01"), ("L22-31x4.5", "top8x4.5_L22-31_math31_s1-01"),
                            ("L0-10x0.2", "top8x0.2_L0-10_math31_s1-01"), ("top1x1.5 s1", "top1x1.5_math31_s1-01"),
                            ("d2-8 s0", "top8x1.5_d2-8_math31_s0-01"))}}
    dg = json.loads((HERE / "data/degenerate.json").read_text())
    nbw = {"L22-31x4.5": ("top8x4.5_L22-31_math31", "1"), "L22-31x3.0": ("top8x3_L22-31_math31", "1"), "L0-10x0.2": ("top8x0.2_L0-10_math31", "1"),
           "top1x1.5": ("top1x1.5_math31", "0"), "d2-8": ("top8x1.5_d2-8_math31", "0")}
    for cell, (rk, s) in nbw.items():
        chk(f"{cell} sample {s} ' which ' rule (normband/readout.json which_loop_rows)", dg["cells"][cell][s]["readout_which_rule"], nb[rk]["which_loop_rows"][s])
    S["degenerate_answers"] = {"rule": dg["rule"], "second_rule": "the readout's: ' which ' is more than 5 % of the words",
                               "source": rel(HERE / "data/degenerate.json") + " (prep_degenerate.py, from the raw texts in runs/)",
                               "per_cell_sample": {c: {s: {"degenerate": x["degenerate"], "of_them_right": x["degenerate_right"],
                                                           "of_them_cut_off": x["degenerate_cut_off"], "which_rule": x["readout_which_rule"]}
                                                       for s, x in ss.items()} for c, ss in dg["cells"].items()}}

    # ---- SPEC_normband predictions
    a2c = sub(M["L22-31x3.0"], [1])                                  # P4 and board e18bd8 were about sample 1, the only one then
    a3, a2, bb = contrast(M["L22-31x4.5"], base), contrast(a2c, base), contrast(M["L0-10x0.2"], base)
    a3l0 = contrast(M["L22-31x4.5"], M["L0-10"])
    p5c = contrast(d1, base)["cut_off"]
    p5r = contrast(d1, d28, [0, 1], [0, 1])["right"]
    st = {k: stats(M[k], "") for k in ("L22-31x4.5", "L22-31")}
    st["L22-31x3.0"] = stats(a2c, "")
    pre = {"spec": "studies/rlneurons/specs/SPEC_normband.md: written 20:49:37 UTC (cdfdf3f); amendment 1 at 20:55:56 UTC (0587e9f), after "
                   "three unscored smoke runs at 9.0, 4.5, 3.0 and before the band jobs (submitted 20:56:25-20:57:33 UTC); amendment 2 (rank "
                   "cells, P5 filed by the coordinator) at 20:58:26 UTC (45dd332), 19 s before the first rank job (20:58:45 UTC). One sample "
                   "per band cell; A6 (9.0) was never scored; A3 (4.5) is broken (right 102 < 150), so by the decision rule A2 (3.0) decides.",
           "P1 (A3 = L22-31 x4.5): right - base < +3 points and cap hits < 56; refuted if >= +5 with an interval excluding 0": {
               "numbers": {"right": a3["right"]["value"], "ci95": a3["right"]["ci95"], "cap_hits": st["L22-31x4.5"]["cut_off_mean"]},
               "outcome": "right part held (-18 points), cap part not held (71 >= 56); not refuted; the cell is broken"},
           "P2: A3 - L0-10 x1.5 right interval below 0": {"numbers": [a3l0["right"]["value"], a3l0["right"]["ci95"]],
                                                          "outcome": "held" if a3l0["right"]["ci95"][1] < 0 else "refuted"},
           "P3 (B = L0-10 x0.2): right - base > 0 and cap - base >= -2 points; refuted if cap - base <= -4 with interval excluding 0": {
               "numbers": {"right": [bb["right"]["value"], bb["right"]["ci95"]], "cut_off": [bb["cut_off"]["value"], bb["cut_off"]["ci95"]]},
               "outcome": ("not held (right not above 0), not refuted" if bb["right"]["value"] <= 0 else "held")
               if not (bb["cut_off"]["value"] <= -4 and bb["cut_off"]["ci95"][1] < 0) else "refuted"},
           "P4 (A2 = L22-31 x3.0): right - base < +3 points and cap hits below L22-31 x1.5 (56)": {
               "numbers": {"right": [a2["right"]["value"], a2["right"]["ci95"]], "cap_hits": st["L22-31x3.0"]["cut_off_mean"]},
               "outcome": "held" if a2["right"]["value"] < 3 and st["L22-31x3.0"]["cut_off_mean"] < st["L22-31"]["cut_off_mean"] else "not held"},
           "P5: d1 x1.5 cap - base < -8 points (samples 0-1 pooled) and d1 right - d2-8 right (samples 0-1 paired) < -2; refuted if within 2 points or above": {
               "numbers": {"cut_off": [p5c["value"], p5c["ci95"]], "d1 - d2-8 right": [p5r["value"], p5r["ci95"]]},
               "outcome": "cap part held; right part " + ("held" if p5r["value"] < -2 else "refuted (within 2 points)")}}
    bd = []
    for what, bv, got, tol in (("L22-31x3.0 right", 155, stats(a2c, "")["right_mean"], 0),
                               ("L22-31x3.0 cap hits", 26, stats(a2c, "")["cut_off_mean"], 0),
                               ("L22-31x3.0 - base right", -1.1, a2["right"]["value"], 0.05), ("L22-31x3.0 - base cap", -13.9, a2["cut_off"]["value"], 0.05),
                               ("L22-31x4.5 right", 102, st["L22-31x4.5"]["right_mean"], 0), ("L22-31x4.5 cap hits", 71, st["L22-31x4.5"]["cut_off_mean"], 0),
                               ("L0-10x0.2 right", 156, stats(M["L0-10x0.2"], "")["right_mean"], 0), ("L0-10x0.2 - base right", -0.8, bb["right"]["value"], 0.05),
                               ("L0-10x0.2 - base cap", 2.6, bb["cut_off"]["value"], 0.05), ("d1 x1.5 right total of 656", 366, sum(stats(d1, "")["right_per_sample"]), 0),
                               ("d1 x1.5 - base right", 7.5, contrast(d1, base)["right"]["value"], 0.05), ("d1 - d2-8 right", -2.0, p5r["value"], 0.05)):
        bd.append({"item": "result-e18bd8", "what": what, "board": bv, "recomputed": r2(got), "agrees": bool(abs(bv - got) <= tol), "tolerance": tol})
    return {"checks_against_readout": checks, "board_checks_e18bd8": bd, "rank_matched_scale_1.5": R, "band_size": S, "preregistration_SPEC_normband": pre,
            "changed_existing_values": "d2-8 gained sample 0 (normband): hard328_cells.d2-8, problem_table hard328 d2-8 and points, "
                                       "transitions.hard328.d2-8 and d2-8_all_seeds, transitions.e_additivity. The headline (a), (b), "
                                       "preregistration R1/R2 and board checks keep d2-8 sample 1 (their labels say sample 1)."}


# ---------------------------------------------------------------- review: reviewers' questions
def count_intervals(x):
    if isinstance(x, dict):
        return ("ci95" in x) + sum(count_intervals(v) for v in x.values())
    if isinstance(x, list):
        return sum(count_intervals(v) for v in x)
    return 0


def review(M, facts_so_far):
    RV = HERE / "data" / "review"
    base = M["base_cue"]

    def one(name, sample0=True):
        rows = read(RV / f"{name}.jsonl")
        return {"src": [rel(RV / f"{name}.jsonl")], "samples": [0],
                "p": {r["problem_index"]: [{"s": int(r["score_v3"]), "c": bool(r["cap_hit"]), "t": r["n_new"]}] for r in rows}}
    rl = math_cell([(RES / "day1_3/hard328_rl_plain_s4r2-01/rows.jsonl", None)])
    rlc, bulk, rbulk = one("rl_cue"), one("bulk"), one("rbulk")
    cc = lambda c, lab: {**{k: stats(c, lab)[k] for k in ("label", "source", "n_samples", "right_per_sample", "right_mean", "cut_off_mean",
                                                            "tokens_per_answer")}, "minus_base": contrast(c, base)}
    out = {}
    out["1_rl_model"] = {"rl_plain": cc(rl, "allenai/Olmo-3.1-7B-RL-Zero-Math @ 364820b0, plain prompt, seeds 3,000,000 + 10,000 s + i"),
                         "rl_cue": cc(rlc, "RL-Zero-Math with the cue, one sample, seeds 50,000,000 + i (not the base's seeds; pairing over problems only)"),
                         "all8_x1.0_reference": cc(M["top8x1"], MATH_LABEL["top8x1"])}

    en = json.loads((RV / "energy.json").read_text())
    def rng(d):
        v = np.array(sorted(d.values()))
        return {"min": r2(100 * v.min()), "median": r2(100 * np.median(v)), "max": r2(100 * v.max()), "n_matrices": len(v)}
    nbn = lambda f: json.loads((NB / f / "run.json").read_text())["edit"]["add_norm"]
    d1n, d28n, a8n = nbn("top1x1.5_math31_s1-01"), nbn("top8x1.5_d2-8_math31_s0-01"), json.loads((X / "edits/readout.json").read_text())["cells"]["top8x1.5_math31"]["edit"]["add_norm"]
    assert abs(d1n ** 2 + d28n ** 2 - a8n ** 2) < 1e-3 * a8n ** 2
    out["2_energy"] = {"what": "share of ||RL-Math - base||_F^2 in the top-k singular directions of each of the 224 layer matrices (top_sq / d_sq "
                               "of wsp_edit's edit.json; total = summed over matrices before the ratio)",
                       "direction_1_pct": {"total": r2(100 * en["top1"]["total_share"]), **rng(en["top1"]["per_matrix_share"])},
                       "directions_1_8_pct": {"total": r2(100 * en["top8"]["total_share"]), **rng(en["top8"]["per_matrix_share"])},
                       "directions_2_8_pct_total": r2(100 * (en["top8"]["total_share"] - en["top1"]["total_share"])),
                       "weight_norm_at_x1.5": {"direction_1": r2(d1n), "directions_2_8": r2(d28n), "all_8": r2(a8n),
                                               "note": "Frobenius norm of the intended addition summed over the 224 matrices; d1^2 + d2-8^2 = all8^2 (orthogonal)"},
                       "source": rel(RV / "energy.json")}
    out["3_bulk"] = {"what": "bulk = RL-Zero-Math with its top-8 singular directions per layer matrix REMOVED (layer matrices = RL - d_8, "
                             "every other tensor = RL; wsp_edit recipe bulk). It keeps 90.2 % of the RL change's squared norm. It is not a "
                             "same-norm slice: add_norm 1.27 is the norm of the part removed from RL. rbulk = RL minus a random rank-8 of the same "
                             "singular values (its control). Cue, one sample, seeds 3,000,000 + i.",
                     "bulk": cc(bulk, "RL-Math minus its top-8 directions, cue"), "rbulk": cc(rbulk, "RL-Math minus a random rank-8, cue"),
                     "bulk_minus_rbulk": contrast(bulk, rbulk), "bulk_minus_rl_plain": contrast(bulk, rl)}

    xs = json.loads((RES / "xshift/run-01/metrics.json").read_text())["edits"]
    out["4_activation_rms_shift"] = {"what": "RMS over 6,144 positions of (edited - base) residual at the output of layer 24 and 31 (0-based), "
                                             "results/xshift/run-01/metrics.json; base RMS 41.2 and 84.1",
                                     **{k: {"layer24": r2(xs[x]["shift"]["all"]["rms"][24]), "layer31": r2(xs[x]["shift"]["all"]["rms"][31])}
                                        for k, x in (("all8 x1.5", "top8x1.5_math31"), ("L0-10 x1.5", "top8x1.5_L0-10_math31"),
                                                     ("L11-21 x1.5", "top8x1.5_L11-21_math31"), ("L22-31 x1.5", "top8x1.5_L22-31_math31"),
                                                     ("random all layers x1.5", "rand8x1.5_math31"), ("direction 1 x1", "top1_math31"),
                                                     ("direction 1 x2", "top1x2_math31"))},
                                     "not_recorded": "direction 1 at x1.5, directions 2-8, L22-31 at x3.0, L0-10 at x0.2"}
    main_cells = ("all8", "top1x1.5", "d2-8", "L0-10", "L11-21", "L22-31", "L22-31x3.0", "L0-10x0.2", "rand_L0-10", "rand8x1.5", "top1x1")
    out["5_tokens"] = {"base_tokens_per_answer": stats(base, "")["tokens_per_answer"],
                       **{k: {"samples": M[k]["samples"], "tokens_per_answer": stats(M[k], "")["tokens_per_answer"],
                              "minus_base": diff(M[k], base, "t")} for k in main_cells}}
    rk = facts_so_far["normband"]["rank_matched_scale_1.5"]
    out["6_rank_x1.5"] = {m: {k: rk[m][k] for k in ("d1 - d2-8", "all8 - d1 (what directions 2-8 add on top)", "share of all8's right-answer gain: d1 alone",
                                                    "share of all8's right-answer gain: d2-8 alone", "share of all8's right-answer gain: d1 + d2-8")}
                          for m in rk if m != "what"}

    cr = json.loads((RV / "cut_right.json").read_text())
    three = {}
    for k in ("base_cue",) + main_cells:
        xs_ = [x for v in M[k]["p"].values() for x in v]
        n_s = len(M[k]["samples"])
        rf = sum(x["s"] == 1 and not x["c"] for x in xs_) / n_s
        wf = sum(x["s"] == 0 and not x["c"] for x in xs_) / n_s
        co = sum(x["c"] for x in xs_) / n_s
        cor = sum(x["c"] and x["s"] == 1 for x in xs_)
        three[k] = {"samples": n_s, "right_and_finished": r2(rf), "wrong_and_finished": r2(wf), "cut_off_any_score": r2(co),
                    "cut_off_but_scored_right_total": cor, "right_among_finished_pct": r2(100 * rf / (rf + wf))}
        if k in cr:
            assert len(cr[k]) == cor, (k, len(cr[k]), cor)
    allcr = [x for v in cr.values() for x in v]
    out["7_cut_off_but_right"] = {
        "explanation": "the grader (v3) scores the last boxed answer anywhere in the text. In every such answer of the main cells' raw texts "
                       f"({len(allcr)} answers) a \\boxed{{}} with the right value was written before the limit (last \\boxed at "
                       f"{min(x['last_boxed_at_fraction_of_text'] for x in allcr):.2f}-{max(x['last_boxed_at_fraction_of_text'] for x in allcr):.2f} "
                       "of the text), and the model did not stop: it restarted the solution ('To solve the problem, ...') or kept checking "
                       "('Wait, ...') until 16,384 tokens. finish_reason is 'length' for all.",
        "all_have_a_boxed_answer": all(x["n_boxed"] >= 1 for x in allcr), "all_finish_reason_length": all(x["finish_reason"] == "length" for x in allcr),
        "per_cell_three_way_per_sample": three, "raw": rel(RV / "cut_right.json")}

    pairs = [(a, b) for i, a in enumerate(base["samples"]) for b in base["samples"][i + 1:]]
    ds, d3 = [], []
    for a, b in pairs:
        ds.append(np.mean([v[a]["s"] != v[b]["s"] for v in base["p"].values()]))
        d3.append(np.mean([outcome(v[a]) != outcome(v[b]) for v in base["p"].values()]))
    out["8_base_vs_base"] = {"pairs": pairs, "score_differs_pct": {"mean": r2(100 * np.mean(ds)), "range": [r2(100 * min(ds)), r2(100 * max(ds))]},
                             "three_way_outcome_differs_pct": {"mean": r2(100 * np.mean(d3)), "range": [r2(100 * min(d3)), r2(100 * max(d3))]},
                             "note": "two samples of the cued base on the same 328 problems, different seeds"}
    out["9_interval_count"] = {"dicts_with_ci95_in_facts_before_review": count_intervals(facts_so_far)}
    first6 = ("top1x1.5_math31_s0-01", "top1x1.5_math31_s1-01", "top8x0.2_L0-10_math31_s1-01", "top8x1.5_d2-8_math31_s0-01",
              "top8x3_L22-31_math31_s1-01", "top8x4.5_L22-31_math31_s1-01")          # the cells of amendments 1-2
    started = {f: json.loads((NB / f / "metrics.json").read_text())["started_utc"] for f in first6}
    submitted = {f: json.loads((NB / f / "run.json").read_text())["job_ids"][0] for f in started}
    out["10_normband_timing"] = {
        "commits (git log, UTC)": {"cdfdf3f spec, P1-P4 for A6 (9.0), B, A3": "20:49:37", "0587e9f amendment 1 after 3 unscored smoke runs (9.0 loops; 4.5 1 of 8 "
                                   "drifts; 3.0 coherent): P1, P2 moved to 4.5 and P4 to 3.0": "20:55:56", "45dd332 amendment 2: rank cells, P5": "20:58:26"},
        "first_job_of_each_cell (job id = submit time, US Central)": submitted, "started_utc (run folder metrics.json)": started,
        "reading": "the band jobs (4.5, 0.2, 3.0) were submitted 20:56:25-20:57:33 UTC, after amendment 1 and before amendment 2; P5 was "
                   "committed after those band jobs had started and 19 s before the first rank job (20:58:45). P1-P4 were amended after the "
                   "smoke runs had shown which scales break the model.",
        "outcomes": {k: v["outcome"] for k, v in facts_so_far["normband"]["preregistration_SPEC_normband"].items() if isinstance(v, dict)}}
    nbr = json.loads((NB / "readout.json").read_text())["cells"]
    out["11_intervals_own_bootstrap"] = {
        k: {"right": facts_so_far["hard328_cells"][k]["minus_base"]["right"], "cut_off": facts_so_far["hard328_cells"][k]["minus_base"]["cut_off"],
            "readout_json": nbr.get(rk_, {}).get("minus_base_cue") or json.loads((D3 / "readout.json").read_text())["cells"][rk_]["minus_base_cue"]}
        for k, rk_ in (("L22-31x3.0", "top8x3_L22-31_math31"), ("rand8x1.5", "rand8x1.5_math31"))}
    return out


# ---------------------------------------------------------------- no_cue: the rank cells without the cue (SPEC_normband amendment 3)
def no_cue(M):
    nbc = lambda f: math_cell([(NB / f / "rows.jsonl", None)])
    bp, d1p, d28p = nbc("base_plain_s1-01"), nbc("top1x1.5_math31_plain_s1-01"), nbc("top8x1.5_d2-8_math31_plain_s1-01")
    rl = math_cell([(RES / "day1_3/hard328_rl_plain_s4r2-01/rows.jsonl", None)])
    f50 = HERE / "data/nocue/base_plain_s50M.jsonl"
    b50 = {"src": [rel(f50)], "samples": [0], "p": {r["problem_index"]: [{"s": int(r["score_v3"]), "c": bool(r["cap_hit"]), "t": r["n_new"]}]
                                                     for r in read(f50)}}
    bc, d1c, d28c = M["base_cue"], M["top1x1.5"], M["d2-8"]
    nb = json.loads((NB / "readout.json").read_text())["cells"]
    checks = []
    for c, rk in ((bp, "base_plain"), (d1p, "top1x1.5_math31_plain"), (d28p, "top8x1.5_d2-8_math31_plain"), (M["L22-31x3.0"], "top8x3_L22-31_math31")):
        st = stats(c, "")
        assert st["samples"] == sorted(nb[rk]["samples"]), rk
        for i, s_ in enumerate(st["samples"]):
            j = nb[rk]["samples"].index(s_)
            for nm, got, want in (("right", st["right_per_sample"][i], nb[rk]["right"][j]), ("cap hits", st["cut_off_per_sample"][i], nb[rk]["cap_hits"][j])):
                assert got == want, (rk, s_, nm, got, want)
                checks.append({"name": f"{rk} sample {s_} {nm} (normband/readout.json)", "recomputed": got, "stored": want})
        assert abs(st["tokens_per_answer"] - nb[rk]["mean_tokens"]) < 0.06, rk

    def cell(c, label):
        st = stats(c, label)
        return {k: st[k] for k in ("label", "source", "samples", "right_per_sample", "right_mean", "cut_off_mean", "finished_wrong_mean",
                                   "tokens_per_answer", "right_of_finished_pct", "cut_off_but_right")}
    con = lambda a, b, sa=None, sb=None: contrast(a, b, sa, sb, keys=("s", "c", "t"))
    out = {"what": "hard328, same settings as the cued cells but the plain prompt (no ' line!\\n\\nOkay' prefix); all plain cells are sample 1 "
                   "(seeds 3,010,000 + i); points of 328 with 95 % and 99 % intervals (paired bootstrap, default_rng(0))",
           "cells": {"base_plain": cell(bp, "base, plain prompt"), "top1x1.5_plain": cell(d1p, "direction 1 only x1.5, plain"),
                     "d2-8_plain": cell(d28p, "directions 2-8 x1.5, plain"), "rl_plain": cell(rl, "RL-Zero-Math, plain, 4 samples"),
                     "base_plain_s50M (noise reference)": cell(b50, "base, plain, an earlier job: seeds 50,000,000 + i (job 1114-132922-7ba0)")},
           "checks_against_readout": checks}
    out["contrasts"] = {
        "d1_plain - base_plain": con(d1p, bp), "d2-8_plain - base_plain": con(d28p, bp), "d1_plain - d2-8_plain": con(d1p, d28p),
        "rl_plain - base_plain": {"pooled (RL samples 0-3 vs base plain sample 1)": con(rl, bp), "seed-matched (sample 1)": con(rl, bp, [1], [1])},
        "d2-8_plain - rl_plain": {"pooled (RL 0-3)": con(d28p, rl), "seed-matched (sample 1)": con(d28p, rl, [1], [1])},
        "d2-8_plain - d2-8_cued": {"pooled (cued samples 0-1)": con(d28p, d28c), "seed-matched (sample 1)": con(d28p, d28c, [1], [1])},
        "d2-8_plain - base_cued": {"pooled (cued base 0-3)": con(d28p, bc), "seed-matched (sample 1)": con(d28p, bc, [1], [1])},
        "d1_plain - base_cued": {"seed-matched (sample 1)": con(d1p, bc, [1], [1])},
        "base_plain_s50M - base_plain (two plain-base jobs, different seeds)": con(b50, bp)}
    inter = {}
    for nm, ep, ec in (("d2-8", d28p, d28c), ("d1", d1p, d1c)):
        for mode, sc in (("seed-matched (sample 1 of every cell)", [1]), ("pooled cued (cued edit 0-1, cued base 0-3)", None)):
            v = {}
            for key, kn in (("s", "right"), ("c", "cut_off")):
                d = 100 * ((rate(ep, key) - rate(bp, key)) - (rate(ec, key, sc) - rate(bc, key, sc)))
                ci95, ci99 = boot(d)
                v[kn] = {"value": r2(d.mean()), "ci95": ci95, "ci99": ci99}
            inter[f"{nm}: {mode}"] = v
    out["interaction (effect plain - effect cued)"] = inter

    op = json.loads((HERE / "data/nocue/openings.json").read_text())
    out["openings"] = {"rule": op["rule"], "source": rel(HERE / "data/nocue/openings.json"),
                       "per_cell": {c: {k: v[k] for k in ("n", "cue_opening", "okay_first", "answer_first", "empty_or_short", "cue_opening_right",
                                                         "first_three_words")} for c, v in op["cells"].items()}}
    # hostile: is the plain gain only over answers in which the plain base does not reason?
    pp = op["cells"]["base_plain"]["per_problem"]
    ps = sorted(bp["p"])
    reasons = np.array([pp[str(p)][1] == 1 for p in ps])            # the plain base opened with 'Okay' (it reasons)
    short = np.array([pp[str(p)][2] == 1 for p in ps])
    sub_ = {}
    for nm, ep in (("d2-8_plain", d28p), ("d1_plain", d1p)):
        d = 100 * (rate(ep, "s") - rate(bp, "s"))
        for gname, g in (("base_plain opened with 'Okay' (reasons)", reasons), ("base_plain did not open with 'Okay'", ~reasons),
                         ("base_plain answer under 20 words", short)):
            ci95, ci99 = boot(d[g])
            sub_[f"{nm} - base_plain on problems where {gname}"] = {"n_problems": int(g.sum()), "value": r2(d[g].mean()), "ci95": ci95,
                                                                     "gain_problems": r2(d[g].sum() / 100)}
    out["gain_by_base_plain_opening"] = sub_
    trans = {}
    for nm, ep in (("d2-8_plain", d28p), ("d1_plain", d1p)):
        trans[nm] = transition_block(ep, bp, [(1, 1)])[0]
    out["transitions_vs_base_plain"] = trans
    # P6 and P7 (SPEC_normband amendment 3: commit ec3eda0, 2026-11-15 22:08:13 UTC)
    p6 = con(M["L22-31x3.0"], bc, [0, 1], [0, 1])
    p7 = out["contrasts"]["d1_plain - d2-8_plain"]["right"]
    started = {f: json.loads((NB / f / "metrics.json").read_text())["started_utc"] for f in
               ("top8x3_L22-31_math31_s0-01", "base_plain_s1-01", "top1x1.5_math31_plain_s1-01", "top8x1.5_d2-8_math31_plain_s1-01")}
    jobs = {f: json.loads((NB / f / "run.json").read_text())["job_ids"] for f in started}
    out["preregistration_amendment_3"] = {
        "commit": "ec3eda0 at 22:08:13 UTC (16:08:13 -0600); first job submitted 16:12:31 -0600 = 22:12:31 UTC (job ids = submit time, "
                  "US Central): all 8 jobs after the commit", "jobs": jobs, "started_utc": started,
        "P6": {"text": "S1 (L22-31 x3.0). Right minus base (same seeds, samples 0 and 1 of both) has an interval including 0, and cap hits "
                       "fall by at least 8 points. Refuted if S1 alone adds >= +4 points right over the base.",
               "numbers": {"right": [p6["right"]["value"], p6["right"]["ci95"]], "cut_off": [p6["cut_off"]["value"], p6["cut_off"]["ci95"]],
                           "sample_0_alone_right_minus_base_sample_0": diff(M["L22-31x3.0"], bc, "s", [0], [0])["value"]},
               "outcome": "held" if p6["right"]["ci95"][0] <= 0 <= p6["right"]["ci95"][1] and p6["cut_off"]["value"] <= -8 else "not held"},
        "P7": {"text": "Without the cue, direction 1 adds more right answers over the plain base than directions 2-8 do: S2 minus S3 >= +3 "
                       "points right. Refuted if S3 adds at least as many right answers as S2 (S2 minus S3 <= 0).",
               "numbers": [p7["value"], p7["ci95"]], "outcome": "refuted" if p7["value"] <= 0 else ("held" if p7["value"] >= 3 else "neither")}}
    return out


# ---------------------------------------------------------------- main
def main():
    M = load_math()
    C = {k: code_cell(k) for k in CODE_LABEL}
    for c in C.values():
        assert sorted(c["p"]) == sorted(C["base_cue"]["p"]) and len(c["p"]) == 538
    base, b = M["base_cue"], C["base_cue"]

    # ---- checks against stored readouts
    ro = json.loads((D3 / "readout.json").read_text())["cells"]
    rmap = {"base_cue": "base_cue", "all8": "top8x1.5_math31", "L0-10": "top8x1.5_L0-10_math31", "L11-21": "top8x1.5_L11-21_math31",
            "L22-31": "top8x1.5_L22-31_math31", "d2-8": "top8x1.5_d2-8_math31", "rand_L0-10": "rand8x1.5_L0-10_math31", "rand8x1.5": "rand8x1.5_math31"}
    for k, rk in rmap.items():
        mk = sub(M[k], ro[rk]["samples"]) if k == "d2-8" else M[k]       # d2-8 gained sample 0 after depth3; depth3 read sample 1
        st = stats(mk, "")
        assert st["samples"] == ro[rk]["samples"], k
        for i, (g, w) in enumerate(zip(st["right_per_sample"], ro[rk]["right"])):
            check(f"hard328 {k} sample {st['samples'][i]} right (depth3/readout.json)", g, w)
        for i, (g, w) in enumerate(zip(st["cut_off_per_sample"], ro[rk]["cap_hits"])):
            check(f"hard328 {k} sample {st['samples'][i]} cap hits (depth3/readout.json)", g, w)
        if "minus_base_cue" in ro[rk]:
            for key, nm in (("s", "right"), ("c", "cap")):
                dd = diff(mk, base, key)
                st_ = ro[rk]["minus_base_cue"][nm]
                check(f"hard328 {k} - base {nm} points (depth3/readout.json)", dd["value"], st_["points"], 0.006)
                for j in (0, 1):
                    check(f"hard328 {k} - base {nm} 95 % end {j} (depth3/readout.json; other resamples)", dd["ci95"][j], st_["interval95"][j], 0.4)
    ed = json.loads((X / "edits/readout.json").read_text())["cells"]
    for k, ek in (("L0-10", "top8x1.5_L0-10_math31"), ("L11-21", "top8x1.5_L11-21_math31"), ("L22-31", "top8x1.5_L22-31_math31"), ("rand8x1.5", "rand8x1.5_math31")):
        st = stats({**M[k], "samples": [0], "p": {p: v[:1] for p, v in M[k]["p"].items()}}, "")
        check(f"hard328 {k} sample 0 right (edits/readout.json)", st["right_per_sample"][0], ed[ek]["right_v3"])
        check(f"hard328 {k} sample 0 cap hits (edits/readout.json)", st["cut_off_per_sample"][0], ed[ek]["cap_hits"])
        check(f"hard328 {k} sample 0 tokens (edits/readout.json)", st["tokens_per_answer"], ed[ek]["mean_generated_tokens"], 0.06)
    cro = {**json.loads((X / "code_dial/readout.json").read_text())["cells"], **json.loads((X / "code_depth/readout.json").read_text())["cells"]}
    cdiff = {**json.loads((X / "code_dial/readout.json").read_text())["differences"], **json.loads((X / "code_depth/readout.json").read_text())["differences"]}
    ckey = {"base_cue": "base_cue", "rl_plain": "rl_plain", "rand8x1.5": "code_rand8x1.5_code31", "top8x1": "code_top8_code31",
            "top8x1.5": "code_top8x1.5_code31", "top8x2": "code_top8x2_code31", "math_top8x1.5": "code_top8x1.5_math31",
            "L0-10": "code_top8x1.5_L0-10_code31", "L11-21": "code_top8x1.5_L11-21_code31", "L22-31": "code_top8x1.5_L22-31_code31"}
    for k, rk in ckey.items():
        st, a = stats(C[k], ""), cro[rk]["all"]
        check(f"Code {k} passed (readout)", st["right_per_sample"][0], a["passed"])
        check(f"Code {k} cap hits (readout)", st["cut_off_per_sample"][0], a["cap_hits"])
        check(f"Code {k} no code block (readout)", st["no_code_block"], a["no_block"])
        check(f"Code {k} tokens (readout)", st["tokens_per_answer"], a["tokens_per_problem"], 0.006)
        if f"base_cue - {rk}" in cdiff:
            dd, w = diff(C[k], b, "s"), cdiff[f"base_cue - {rk}"]
            check(f"Code {k} - base points (readout, sign flipped)", dd["value"], -w["points"], 0.006)
            check(f"Code {k} - base 95 % low (readout, 5,000 resamples)", dd["ci95"][0], -w["bootstrap95"][1], 0.5)

    # ---- cells
    cells_m = {k: {**stats(c, MATH_LABEL[k]), "minus_base": contrast(c, base) if k != "base_cue" else None} for k, c in M.items()}
    cells_c = {k: {**stats(c, CODE_LABEL[k]), "minus_base": contrast(c, b) if k != "base_cue" else None} for k, c in C.items()}

    # ---- headline contrasts
    H = {}
    d1s = sub(M["d2-8"], [1])
    H["a_d2-8_minus_base"] = {"pooled (d2-8 sample 1 vs base samples 0-3)": contrast(d1s, base),
                              "seed-matched (sample 1 vs base sample 1)": contrast(M["d2-8"], base, [1], [1])}
    H["b_all8_minus_d2-8 (what direction 1 adds)"] = {"pooled (all8 samples 0-3 vs d2-8 sample 1)": contrast(M["all8"], d1s),
                                                      "seed-matched (sample 1 vs sample 1)": contrast(M["all8"], M["d2-8"], [1], [1])}
    H["b2_direction1_only_minus_base (sample 0, no x1.5 cell exists)"] = {k: contrast(M[k], base) for k in ("top1x1", "top1x2", "top1x3")}
    H["c_L22-31_minus_base"] = {"pooled (samples 0-1 vs base 0-3)": contrast(M["L22-31"], base),
                                "fresh only (sample 1, run after the depth reading) vs base 0-3": contrast(M["L22-31"], base, [1]),
                                "seed-matched (samples 0-1 vs base 0-1)": contrast(M["L22-31"], base, [0, 1], [0, 1])}
    H["c2_L22-31_minus_L11-21"] = contrast(M["L22-31"], M["L11-21"])
    H["c3_L22-31_minus_all8 (share of the full effect)"] = contrast(M["L22-31"], M["all8"])
    H["c4_L22-31_minus_rand8x1.5_all_layers (no random late-band cell exists)"] = contrast(M["L22-31"], M["rand8x1.5"])
    H["d_L0-10_minus_rand_L0-10"] = {
        "pooled (L0-10 samples 0-3 vs random sample 1; random has 1 sample)": contrast(M["L0-10"], M["rand_L0-10"]),
        "as filed in SPEC_depth3 B3 (sample 1 vs sample 1)": contrast(M["L0-10"], M["rand_L0-10"], [1], [1]),
        "fresh only (L0-10 samples 1-3 vs random sample 1)": contrast(M["L0-10"], M["rand_L0-10"], [1, 2, 3])}
    H["d2_L0-10_minus_base"] = {"pooled": contrast(M["L0-10"], base),
                                "fresh only (samples 1-3, run after the depth reading) vs base 0-3": contrast(M["L0-10"], base, [1, 2, 3]),
                                "seed-matched fresh (samples 1-3 vs base 1-3)": contrast(M["L0-10"], base, [1, 2, 3], [1, 2, 3])}
    H["d3_L11-21_minus_base"] = {"pooled": contrast(M["L11-21"], base), "fresh only (sample 1)": contrast(M["L11-21"], base, [1])}
    H["e_code"] = {"L22-31 - base": contrast(C["L22-31"], b), "L0-10 - base": contrast(C["L0-10"], b), "L11-21 - base": contrast(C["L11-21"], b),
                   "L0-10 - random x1.5 all layers (no random L0-10 cell on Code)": contrast(C["L0-10"], C["rand8x1.5"]),
                   "L22-31 - random x1.5 all layers": contrast(C["L22-31"], C["rand8x1.5"]),
                   "L22-31 - L11-21": contrast(C["L22-31"], C["L11-21"]), "all8 - base": contrast(C["top8x1.5"], b),
                   "random x1.5 - base": contrast(C["rand8x1.5"], b), "all8 - RL-Code": contrast(C["top8x1.5"], C["rl_plain"]),
                   "note": "no directions 2-8 cell and no direction-1 cell exist on Code: contrasts (a) and (b) cannot be made there"}
    H["noise_floor_same_seed_reruns"] = {
        "base: job e72c - sample 0 of the 4-sample job (same seeds)": contrast(M["base_cue_rerun"], base, None, [0]),
        "all8: job 5991 - sample 0 of the 4-sample job (same seeds)": contrast(M["top8x1.5_rerun"], M["all8"], None, [0]),
        "note": "vLLM sampling with fixed per-request seeds is not reproducible across jobs: these are the differences between two jobs "
                "with identical seeds and settings; the band cells' sample 0 came from the edits jobs, the base reference is the 4-sample job"}

    # ---- pre-registered predictions of SPEC_depth3 (recomputed)
    v = lambda x: (x["value"], x["ci95"])
    l0b, l0r = contrast(M["L0-10"], base), contrast(M["L0-10"], M["rand_L0-10"], [1], [1])
    l22, l11 = contrast(M["L22-31"], base), contrast(M["L11-21"], base)
    d28 = stats(d1s, ""); d28a = contrast(d1s, M["all8"])
    rl = stats(M["rand_L0-10"], "")
    pre = {
        "B1 L0-10 add right (interval excludes 0)": [v(l0b["right"]), l0b["right"]["ci95"][0] > 0],
        "B2 L0-10 do not cut cap hits (upper end above 0)": [v(l0b["cut_off"]), l0b["cut_off"]["ci95"][1] > 0],
        "B3 L0-10 - random L0-10 (sample 1 each) excludes 0; random within 158.5+-12 right, 71.5+-15 cap":
            [v(l0r["right"]), l0r["right"]["ci95"][0] > 0 and abs(rl["right_mean"] - 158.5) <= 12 and abs(rl["cut_off_mean"] - 71.5) <= 15],
        "B4 L22-31 cut cap hits (excludes 0) and right includes 0": [[v(l22["cut_off"]), v(l22["right"])],
                                                                     l22["cut_off"]["ci95"][1] < 0 and l22["right"]["ci95"][0] <= 0 <= l22["right"]["ci95"][1]],
        "B5 L11-21 right above 0 and cap below 0": [[v(l11["right"]), v(l11["cut_off"])], l11["right"]["ci95"][0] > 0 and l11["cut_off"]["ci95"][1] < 0],
        "R1 d2-8 >= 180 right (refuted < 175) and cap hits >= 40 (refuted <= 25)": [[d28["right_mean"], d28["cut_off_mean"]],
                                                                                   d28["right_mean"] >= 175 and d28["cut_off_mean"] > 25],
        "R2 d2-8 below all8 in right, interval excludes 0": [v(d28a["right"]), d28a["right"]["ci95"][1] < 0]}
    prereg = {
        "spec": "studies/rlneurons/specs/SPEC_depth3.md, one commit 099dc65 at 2026-11-15 18:23:04 UTC; the new jobs started 18:27:55 to "
                "18:57:58 UTC (metrics.json started_utc of the run folders). The spec's own text: the depth reading was made after the "
                "one-sample run (result-306787, 18:00 UTC), and that sample 0 is pooled into B1, B2, B4, B5.",
        "predictions_recomputed": {k: {"numbers": n, "held": h} for k, (n, h) in pre.items()},
        "code_amendment_9": "SPEC_xreward amendment 9 (commit 397b273, 18:01 UTC, before the Code band jobs started 18:02 UTC): "
                            "L1 L0-10 >= 350 passed and >= 20 cap hits (refuted if <= 12 cap or < 340); L2 L22-31 <= 14 cap and <= 345 "
                            "passed (refuted if >= 360 or cap >= 22); L3 L11-21 >= 350 and <= 18 cap",
        "code_outcomes": {"L1": [cells_c["L0-10"]["right_mean"], cells_c["L0-10"]["cut_off_mean"], "refuted (cap 12 <= 12)"],
                          "L2": [cells_c["L22-31"]["right_mean"], cells_c["L22-31"]["cut_off_mean"], "refuted (cap 34 >= 22)"],
                          "L3": [cells_c["L11-21"]["right_mean"], cells_c["L11-21"]["cut_off_mean"], "held"]}}
    assert cells_c["L0-10"]["cut_off_mean"] <= 12 and cells_c["L22-31"]["cut_off_mean"] >= 22
    assert cells_c["L11-21"]["right_mean"] >= 350 and cells_c["L11-21"]["cut_off_mean"] <= 18
    assert all(h for _, h in pre.values()), {k: h for k, (_, h) in pre.items()}

    # ---- board text vs rows
    F = cells_m
    board("result-6f7ca3", "L0-10 right mean", 183.5, F["L0-10"]["right_mean"], 0.0)
    board("result-6f7ca3", "L0-10 cap mean", 92.0, F["L0-10"]["cut_off_mean"], 0.0)
    board("result-6f7ca3", "L0-10 - base right", 7.6, l0b["right"]["value"], 0.05)
    board("result-6f7ca3", "L0-10 - base cap", 6.2, l0b["cut_off"]["value"], 0.06)
    board("result-6f7ca3", "L11-21 right mean", 181.0, F["L11-21"]["right_mean"], 0.0)
    board("result-6f7ca3", "L11-21 cap mean", 45.0, F["L11-21"]["cut_off_mean"], 0.0)
    board("result-6f7ca3", "L22-31 right mean", 163.5, F["L22-31"]["right_mean"], 0.0)
    board("result-6f7ca3", "L22-31 cap mean", 56.0, F["L22-31"]["cut_off_mean"], 0.0)
    board("result-6f7ca3", "L22-31 - base right", 1.5, l22["right"]["value"], 0.05)
    board("result-6f7ca3", "L22-31 - base cap", -4.7, l22["cut_off"]["value"], 0.05)
    board("result-6f7ca3", "d2-8 right", 183, d28["right_mean"], 0)
    board("result-6f7ca3", "d2-8 cap", 69, d28["cut_off_mean"], 0)
    board("result-6f7ca3", "d2-8 - base right", 7.5, H["a_d2-8_minus_base"]["pooled (d2-8 sample 1 vs base samples 0-3)"]["right"]["value"], 0.05)
    board("result-6f7ca3", "d2-8 - all8 right", -5.3, d28a["right"]["value"], 0.05)
    board("result-6f7ca3", "random L0-10 right", 162, rl["right_mean"], 0)
    board("result-6f7ca3", "L0-10 - random L0-10 right ('beats it by'; sample 1 vs 1, pooled is +6.6)", 7.3, l0r["right"]["value"], 0.05)
    board("result-306787", "base right (sample-0 job e72c; the depth3 reference sample 0 is 161)", 164, cells_m["base_cue_rerun"]["right_mean"], 0)
    board("result-306787", "base cap (e72c; depth3 sample 0: 71)", 77, cells_m["base_cue_rerun"]["cut_off_mean"], 0)
    board("result-306787", "all layers right (job 5991; the 4-sample job's sample 0 is 207)", 203, cells_m["top8x1.5_rerun"]["right_mean"], 0)
    board("result-306787", "L0-10 tokens", 10166, stats({**M["L0-10"], "samples": [0], "p": {p: v[:1] for p, v in M["L0-10"]["p"].items()}}, "")["tokens_per_answer"], 0.5)
    board("result-306787", "top1 x1 right", 181, cells_m["top1x1"]["right_mean"], 0)
    board("result-306787", "top1 x2 cap", 23, cells_m["top1x2"]["cut_off_mean"], 0)
    board("result-306787", "top1 x3 cap", 10, cells_m["top1x3"]["cut_off_mean"], 0)
    board("result-306787 comment", "top1 x2 - base right (+6.1 [1.8, 10.4]; against base job e72c, 164; against the 4-sample base +7.8)", 6.1,
          contrast(M["top1x2"], M["base_cue_rerun"])["right"]["value"], 0.05)
    cc = cells_c
    for k, (p_, cap_) in {"base_cue": (317, 27), "rand8x1.5": (331, 27), "L0-10": (372, 12), "L11-21": (366, 6), "L22-31": (342, 34),
                          "top8x1.5": (399, 4), "rl_plain": (401, 8)}.items():
        board("result-51ccc6", f"Code {k} passed", p_, cc[k]["right_mean"], 0)
        board("result-51ccc6", f"Code {k} cap hits", cap_, cc[k]["cut_off_mean"], 0)
    board("result-51ccc6", "Code L22-31 - random right", 2.0, H["e_code"]["L22-31 - random x1.5 all layers"]["right"]["value"], 0.05)
    board("result-51ccc6", "math L22-31 - random right (+2.4, sample 0 only vs random 1x per 306787 comment)", 2.4,
          contrast(M["L22-31"], M["rand8x1"], [0])["right"]["value"], 0.05)
    board("result-a1bf75", "Code x1.5 - random right", 12.6, H["e_code"]["all8 - base"]["right"]["value"] - H["e_code"]["random x1.5 - base"]["right"]["value"], 0.05)
    board("result-a1bf75", "Code x1.5 - RL-Code right", -0.4, H["e_code"]["all8 - RL-Code"]["right"]["value"], 0.05)
    board("result-98de28", "L22-31 RMS shift at layer 24 (all layers 9.3)", 0.83,
          json.loads((RES / "xshift/run-01/metrics.json").read_text())["edits"]["top8x1.5_L22-31_math31"]["shift"]["all"]["rms"][24], 0.005)

    # ---- multiple comparisons
    n_pre = 7 + 3
    mc = {"preregistered_predictions": n_pre, "note": "7 in SPEC_depth3 (B1-B5, R1, R2: 11 interval tests inside them) + 3 on Code (amendment 9); "
          "the depth reading itself was chosen after looking at 3 bands x 2 outcomes on one sample (result-306787), and the rank reading "
          "after 3 direction-1 sizes; facts.json reports about 70 interval-bearing contrasts. Use the 99 % intervals for the 5 headline "
          "contrasts (a)-(e) (Bonferroni over 5 at 95 % is 99 %)."}

    sizes = edit_sizes()
    facts = {"conventions": __doc__.split("Conventions: ")[1].strip(),
             "settings": {"hard328": "328 hard MATH-family problems, base allenai/Olmo-3-1025-7B @ a81bae42 + cue (prefix ' line!\\n\\nOkay'), edits "
                                     "from allenai/Olmo-3.1-7B-RL-Zero-Math @ 364820b0 (wsp_edit --rounding stochastic --seed 0), T 1.0 / top-p 1.0, "
                                     "cap 16,384, grader v3; seed 3,000,000 + 10,000 s + problem index",
                          "code": "HumanEval+ (163) + MBPP+ (375) = 538, base + Code cue (' as shown in the prompt. I hope this helps!\\n\\nOkay'), "
                                  "edits from allenai/Olmo-3.1-7B-RL-Zero-Code @ 1ca3bb30, T 1.0 / top-p 1.0, cap 16,384, one sample, seed 51,000,000 + i"},
             "hard328_cells": cells_m, "code_cells": cells_c, "headline": H, "edit_sizes": sizes, "preregistration": prereg,
             "multiple_comparisons": mc, "board_checks": BOARD, "checks_against_readouts": CHECKS,
             "transitions": transitions(M, C), "normband": normband(M)}
    facts["review"] = review(M, facts)
    facts["no_cue"] = no_cue(M)
    (HERE / "facts.json").write_text(json.dumps(facts, indent=1) + "\n")

    table = {"what": "per cell and problem: right = mean of score_v3 (hard328) or passed (Code) over the cell's samples; cut_off = mean "
                     "of cap_hit; same problem order in every cell of a set",
             "hard328": {"problems": sorted(base["p"]), "cells": {k: {"samples": c["samples"], "right": [r2(x) for x in rate(c, "s")],
                                                                      "cut_off": [r2(x) for x in rate(c, "c")]} for k, c in M.items()}},
             "code": {"problems": sorted(b["p"]), "cells": {k: {"samples": c["samples"], "right": [int(x) for x in rate(c, "s")],
                                                                "cut_off": [int(x) for x in rate(c, "c")]} for k, c in C.items()}},
             "points": {"what": "change from the cued base (x: right, y: cut off), points with 95 % intervals",
                        **{f"hard328 {k}": {"x": v["minus_base"]["right"], "y": v["minus_base"]["cut_off"]} for k, v in cells_m.items() if v["minus_base"]},
                        **{f"code {k}": {"x": v["minus_base"]["right"], "y": v["minus_base"]["cut_off"]} for k, v in cells_c.items() if v["minus_base"]}}}
    (HERE / "problem_table.json").write_text(json.dumps(table) + "\n")

    f = lambda d: f"{d['value']:+6.2f} [{d['ci95'][0]:+.2f}, {d['ci95'][1]:+.2f}]"
    for nm, cs in (("hard328", cells_m), ("Code", cells_c)):
        print(nm)
        for k, v in cs.items():
            mb = v["minus_base"]
            print(f"  {k:15s} n{v['n_samples']} right {v['right_mean']:6.2f} cut {v['cut_off_mean']:6.2f} fw {v['finished_wrong_mean']:6.2f} tok {v['tokens_per_answer']:7.0f}"
                  + (f" | d right {f(mb['right'])} d cut {f(mb['cut_off'])}" if mb else ""))
    print(f"{len(CHECKS)} readout checks pass; board: {sum(x['agrees'] for x in BOARD)} of {len(BOARD)} agree")
    for x in BOARD:
        if not x["agrees"]:
            print("  BOARD MISMATCH", x)


if __name__ == "__main__":
    main()
