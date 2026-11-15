"""Long answers or hard problems? Think-SFT + cue against RL plain on hard328, stratified by difficulty
(specs/SPEC_riskcov.md, addendum 1; laptop, no GPU; the stored rows of analysis/riskcov.py).

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.riskcov_strat \
        --out studies/rlneurons/results/riskcov/hard328_strat-01 [--think-run runs/<joined>] [--rl-run runs/<job>]

  --out                  a new run folder: run.json, readout.json, table.md, examples.json.
  --think-run, --rl-run  job folders with answers.jsonl: adds the end of the text to the examples.

Stratifiers: `base` = the cued base's right samples on the problem (0 to 4); `loo` = for sample s, the right samples among the
other three of Think-SFT and the other three of RL (0 to 6). Intervals: one set of bootstrap resamples of the problems for all.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

import numpy as np

from studies.rlneurons.analysis import riskcov as RC

STRATA = {"base": {"0": (0, 0), "1-2": (1, 2), "3-4": (3, 4), "0-2": (0, 2), "all": (0, 4)},
          "loo": {"0": (0, 0), "1-3": (1, 3), "4-6": (4, 6), "all": (0, 6)}}
ENDS = {"base": ("0", "3-4"), "loo": ("0", "4-6")}                    # hardest and easiest stratum
CELLS = {**{f"{lo}-{hi}": (lo, hi) for lo, hi in zip(RC.BINS[:-1], RC.BINS[1:])}, "short": (0, 8000), "long": (8000, 16384), "all": (0, 16384)}
LONG = 8000


def stratifiers(arr: dict) -> dict:
    """Per problem x sample: the base's right count on the problem, and the leave-one-out count of Think-SFT and RL."""
    t, r = arr["think"]["right"], arr["rl"]["right"]
    return {"base": np.repeat(arr["base"]["right"].sum(1)[:, None], 4, 1), "loo": (t.sum(1) + r.sum(1))[:, None] - t - r}


def band(x) -> list:
    return [float(v) for v in np.nanpercentile(x, (2.5, 97.5))]


def matched(t: dict, r: dict, M, tie, boots) -> list:
    """Precision at matched coverage under `length` among the samples of mask M (coverage = kept over M's samples), Think-SFT
    minus RL with a paired interval, and the tokens of the last kept sample of each model."""
    k = {"think": RC.keys(t, "length", tie), "rl": RC.keys(r, "length", tie)}
    a = {"think": t, "rl": r}
    grid = [c for c in RC.GRID if c <= min(x["ans"][M].mean() for x in a.values())]
    pt = {m: RC.precision_at(k[m][M], a[m]["right"][M], grid) for m in a}
    bs = {m: np.array([RC.precision_at(k[m][i][M[i]], a[m]["right"][i][M[i]], grid, clip=True) for i in boots]) for m in a}
    tok = {m: np.sort(np.where(a[m]["ans"], a[m]["n_new"], 10**9)[M]) for m in a}
    return [{"coverage": c, "samples": int(M.sum()), "think": float(pt["think"][j]), "rl": float(pt["rl"][j]),
             "points": float(100 * (pt["think"][j] - pt["rl"][j])), "interval95": band(100 * (bs["think"] - bs["rl"])[:, j]),
             "last_kept_tokens": {m: int(tok[m][round(c * M.sum()) - 1]) for m in a}} for j, c in enumerate(grid)]


def cell(t: dict, r: dict, Mt, Mr, W) -> dict:
    """Precision of the samples of masks Mt (Think-SFT) and Mr (RL) and the difference; `boot` holds the resampled differences."""
    out, b = {}, {}
    for m, a, M in (("think", t, Mt), ("rl", r, Mr)):
        f, k = M.sum(1), (M & a["right"]).sum(1)
        out[m] = {"right": int(k.sum()), "samples": int(f.sum()), "precision": float(k.sum() / f.sum()) if f.sum() else None}
        with np.errstate(invalid="ignore", divide="ignore"):
            b[m] = (W @ k) / (W @ f)
    ok = out["think"]["samples"] and out["rl"]["samples"]
    out["boot"] = 100 * (b["think"] - b["rl"])
    out["points"] = 100 * (out["think"]["precision"] - out["rl"]["precision"]) if ok else None
    out["interval95"] = band(out["boot"]) if ok else None
    return out


def finished(a: dict, S, lo_hi, cell_name: str):
    lo, hi = lo_hi
    c_lo, c_hi = CELLS[cell_name]
    return a["ans"] & ~a["cap"] & (S >= lo) & (S <= hi) & (a["n_new"] > c_lo) & (a["n_new"] <= c_hi)


def contrast(x: dict, y: dict) -> dict:
    """x's lead minus y's lead, from the same resamples."""
    if x["points"] is None or y["points"] is None:
        return {"points": None, "interval95": None}
    return {"points": x["points"] - y["points"], "interval95": band(x["boot"] - y["boot"])}


def slopes(t: dict, r: dict, Mt, Mr, W, x_of) -> dict:
    """Problem x model fixed effects: per model the slope of right on x (a function of n_new) among the samples of its mask after
    removing each problem's mean, and Think-SFT's slope minus RL's. `problems` = those where the model's x varies."""
    out, b = {}, {}
    for m, a, M in (("think", t, Mt), ("rl", r, Mr)):
        n = np.maximum(M.sum(1, keepdims=True), 1)
        x, y = x_of(a["n_new"]) * M, a["right"] * M
        dx, dy = (x - x.sum(1, keepdims=True) / n) * M, (y - y.sum(1, keepdims=True) / n) * M
        sxy, sxx = (dx * dy).sum(1), (dx * dx).sum(1)
        out[m] = {"slope_points": float(100 * sxy.sum() / sxx.sum()), "problems": int((sxx > 1e-9).sum())}
        b[m] = 100 * (W @ sxy) / (W @ sxx)
        out[m]["interval95"] = band(b[m])
    out["think - rl"] = {"points": out["think"]["slope_points"] - out["rl"]["slope_points"], "interval95": band(b["think"] - b["rl"])}
    return out


def within(t: dict, r: dict, W) -> dict:
    """Matched cells: per problem and cell (short, long) where both models have a finished answered sample, Think-SFT's precision
    minus RL's, weight n_t n_r / (n_t + n_r). `long - short`: per problem with both cells, weight = the smaller of its two weights."""
    d, w = {}, {}
    for c in ("short", "long"):
        Mt, Mr = (finished(a, np.zeros_like(a["n_new"]), (0, 0), c) for a in (t, r))
        nt, nr = Mt.sum(1), Mr.sum(1)
        w[c] = nt * nr / np.maximum(nt + nr, 1)
        d[c] = (Mt & t["right"]).sum(1) / np.maximum(nt, 1) - (Mr & r["right"]).sum(1) / np.maximum(nr, 1)
    both = np.minimum(w["short"], w["long"])
    est = lambda wt, x: {"problems": int((wt > 0).sum()), "points": float(100 * (wt * x).sum() / wt.sum()), "interval95": band(100 * (W @ (wt * x)) / (W @ wt))}
    return {"short": est(w["short"], d["short"]), "long": est(w["long"], d["long"]), "long - short": est(both, d["long"] - d["short"]),
            "short, problems with both cells": est(both, d["short"]), "long, problems with both cells": est(both, d["long"])}


def mix(arr: dict, S, tie, coverage=0.5) -> dict:
    """The samples each model keeps at `coverage` under `length` on all problems: share and precision per base stratum."""
    out = {}
    for m in ("think", "rl"):
        a = arr[m]
        kept = np.zeros(a["n_new"].size, bool)
        kept[np.argsort(RC.keys(a, "length", tie).ravel(), kind="stable")[:round(coverage * kept.size)]] = True
        kept = kept.reshape(a["n_new"].shape)
        out[m] = {"kept": int(kept.sum()), "last_kept_tokens": int(a["n_new"][kept].max()),
                  "strata": {s: {"kept": int((kept & (S >= lo) & (S <= hi)).sum()), "share": float((kept & (S >= lo) & (S <= hi)).sum() / kept.sum()),
                                 "precision": float(a["right"][kept & (S >= lo) & (S <= hi)].mean())} for s, (lo, hi) in STRATA["base"].items()}}
    return out


def analyse(arr: dict, rng) -> dict:
    t, r = arr["think"], arr["rl"]
    n = len(t["idx"])
    tie = rng.random((n, 4))                                           # the tie order of riskcov.curves (same seed, same first draw)
    boots = rng.integers(0, n, (RC.BOOT, n))
    W = np.array([np.bincount(i, minlength=n) for i in boots], float)
    S = stratifiers(arr)
    res = {"n": n, "bootstrap": RC.BOOT, "long_over_tokens": LONG, "mix_at_coverage_0.50": mix(arr, S["base"], tie), "strata": {}}
    for name, strata in STRATA.items():
        d = {"problems_or_samples": {}, "matched_coverage": {}, "cells": {}, "long - short": {}, "hardest - easiest": {}}
        for s, (lo, hi) in strata.items():
            M = (S[name] >= lo) & (S[name] <= hi)
            d["problems_or_samples"][s] = {"samples": int(M.sum()), "problems_with_a_sample": int(M.any(1).sum()),
                                           **{f"{m}_{k}": int((arr[m][k] & M).sum()) for m in ("think", "rl") for k in ("ans", "cap", "right")}}
            d["matched_coverage"][s] = matched(t, r, M, tie, boots)
            d["cells"][s] = {c: cell(t, r, finished(t, S[name], (lo, hi), c), finished(r, S[name], (lo, hi), c), W) for c in CELLS}
            d["long - short"][s] = contrast(d["cells"][s]["long"], d["cells"][s]["short"])
        hard, easy = ENDS[name]
        d["hardest - easiest"] = {c: contrast(d["cells"][hard][c], d["cells"][easy][c]) for c in ("short", "long", "all")}
        res["strata"][name] = d
    fin = lambda a, lo_hi: finished(a, S["base"], lo_hi, "all")
    res["slopes_problem_x_model_fixed_effects"] = {
        x: {s: slopes(t, r, fin(t, lh), fin(r, lh), W, f) for s, lh in STRATA["base"].items()}
        for x, f in (("long", lambda n_new: (n_new > LONG) * 1.0), ("per_1000_tokens", lambda n_new: n_new / 1000))}
    res["matched_cells_within_problem"] = within(t, r, W)
    for d in res["strata"].values():                                   # the resampled differences are not written
        for cs in d["cells"].values():
            for c in cs.values():
                del c["boot"]
    return res


def markdown(res: dict) -> str:
    iv = lambda d: "" if d["points"] is None else f"{d['points']:+.1f} [{d['interval95'][0]:+.1f}, {d['interval95'][1]:+.1f}]"
    pc = lambda c: f"{c['right']} / {c['samples']}" + ("" if c["precision"] is None else f", {100 * c['precision']:.1f}")
    o = [f"# Long answers or hard problems? Think-SFT + cue against RL plain, hard328 (n = {res['n']}, 4 samples, attempt 0, T 1.0 / top-p 1.0, grader v3)", "",
         "Stratifier `base`: the cued base's right samples on the problem (0 to 4). Stratifier `loo`: per sample s, the right samples among the other three of "
         "Think-SFT and the other three of RL (0 to 6). Differences are Think-SFT minus RL in points, 95 % intervals from "
         f"{res['bootstrap']} resamples of the problems. Long = over {res['long_over_tokens']} tokens.", "",
         "## The samples kept at coverage 0.50 under `length`, all problems, by base stratum", "",
         "| Model | Last kept, tokens | " + " | ".join(f"base {s}: kept, share %, precision %" for s in ("0", "1-2", "3-4")) + " |", "|---|---|---|---|---|"]
    for m, d in res["mix_at_coverage_0.50"].items():
        o.append(f"| {RC.LABEL[m]} | {d['last_kept_tokens']} | " + " | ".join(f"{d['strata'][s]['kept']}, {100 * d['strata'][s]['share']:.1f}, {100 * d['strata'][s]['precision']:.1f}" for s in ("0", "1-2", "3-4")) + " |")
    for name, d in res["strata"].items():
        for s, rows in d["matched_coverage"].items():
            p = d["problems_or_samples"][s]
            o += ["", f"## Precision at matched coverage under `length`, {name} {s} ({p['samples']} samples per model on {p['problems_with_a_sample']} problems; "
                      f"answered Think-SFT {p['think_ans']}, RL {p['rl_ans']}; right {p['think_right']}, {p['rl_right']})", "",
                  "| Coverage | Think-SFT + cue | RL plain | Think-SFT - RL [95 %] | Last kept, tokens: Think-SFT | RL |", "|---|---|---|---|---|---|"]
            o += [f"| {x['coverage']:.2f} | {100 * x['think']:.1f} | {100 * x['rl']:.1f} | {iv(x)} | {x['last_kept_tokens']['think']} | {x['last_kept_tokens']['rl']} |" for x in rows]
        o += ["", f"## Finished answered samples by tokens inside each stratum of `{name}` (right / samples, %; Think-SFT - RL [95 %])", "",
              "| Stratum | Tokens | Think-SFT + cue | RL plain | Think-SFT - RL [95 %] |", "|---|---|---|---|---|"]
        o += [f"| {s} | {c} | {pc(x['think'])} | {pc(x['rl'])} | {iv(x)} |" for s, cs in d["cells"].items() for c, x in cs.items()]
        o += ["", f"## Contrasts of the lead, `{name}`", "", "| Contrast | Points [95 %] |", "|---|---|"]
        o += [f"| stratum {s}: lead in long answers minus lead in short answers | {iv(x)} |" for s, x in d["long - short"].items()]
        o += [f"| {c} answers: lead in stratum {ENDS[name][0]} minus lead in stratum {ENDS[name][1]} | {iv(x)} |" for c, x in d["hardest - easiest"].items()]
    for x, d in res["slopes_problem_x_model_fixed_effects"].items():
        o += ["", f"## Within problem: slope of right on {x}, problem x model fixed effects, finished answered samples (points; by base stratum)", "",
              "| base stratum | Think-SFT + cue [95 %] (problems that carry it) | RL plain [95 %] (problems) | Think-SFT - RL [95 %] |", "|---|---|---|---|"]
        f = lambda v: f"{v['slope_points']:+.1f} [{v['interval95'][0]:+.1f}, {v['interval95'][1]:+.1f}] ({v['problems']})"
        o += [f"| {s} | {f(v['think'])} | {f(v['rl'])} | {iv(v['think - rl'])} |" for s, v in d.items()]
    o += ["", "## Within problem: matched cells (both models have a finished answered sample in the cell of the problem)", "", "| Cell | Problems | Think-SFT - RL [95 %] |", "|---|---|---|"]
    o += [f"| {c} | {x['problems']} | {iv(x)} |" for c, x in res["matched_cells_within_problem"].items()]
    return "\n".join(o) + "\n"


def examples(arr: dict, S, think_run, rl_run) -> dict:
    """One right and one wrong short finished answer on problems the base never solves: of each pool, the row of median length."""
    out, idx = {}, arr["think"]["idx"]
    for name, m, run, want in (("right", "think", think_run, True), ("wrong", "rl", rl_run, False)):
        a = arr[m]
        pool = np.argwhere(finished(a, S, (0, 0), "short") & (a["right"] == want))
        mid = np.median([a["n_new"][tuple(ps)] for ps in pool])
        p, s = min(map(tuple, pool), key=lambda ps: abs(a["n_new"][ps] - mid))
        out[name] = {"model": RC.LABEL[m], "pool": f"finished, at most {LONG} tokens, base right count 0, {'right' if want else 'wrong'}", "pool_size": len(pool),
                     "problem_index": idx[p], "sample": int(s), "n_new": int(a["n_new"][p, s]), "score_v3": int(a["right"][p, s]),
                     "base_right_samples": int(S[p, s]), "think_right_samples": int(arr["think"]["right"][p].sum()), "rl_right_samples": int(arr["rl"]["right"][p].sum())}
        if run:
            row = RC.texts(run)[idx[p], int(s)]
            out[name] |= RC.tail(row, 2000) | {"prompt": row["prompt"]}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--think-run")
    ap.add_argument("--rl-run")
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    assert not out.exists(), f"{out} exists: a rerun gets the next number"
    arr = {m: RC.arrays(RC.load(RC.RES / d)) for m, d in RC.SETS["hard328"].items()}
    assert arr["think"]["idx"] == arr["rl"]["idx"] == arr["base"]["idx"], "the three runs are not on the same problems"
    got = {m: int((arr[m]["vote"] == 2).sum()) for m in arr}
    assert got == RC.VOTE["hard328"], f"instrument check failed: vote over 4 gives {got}, posted {RC.VOTE['hard328']}"
    res = {"set": "hard328", "spec": RC.SPEC + ", addendum 1", "runs": RC.SETS["hard328"], "attempt": "0 only", **analyse(arr, np.random.default_rng(0))}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    out.mkdir(parents=True)
    (out / "run.json").write_text(json.dumps({"commit": commit, "command": "python -m studies.rlneurons.analysis.riskcov_strat " + " ".join(sys.argv[1:]), "job_id": None,
                                              "gpu": "none (laptop)", "spec": res["spec"], "bootstrap": {"resamples": RC.BOOT, "seed": 0}}, indent=1) + "\n")
    (out / "readout.json").write_text(json.dumps(res, indent=1) + "\n")
    (out / "table.md").write_text(markdown(res))
    (out / "examples.json").write_text(json.dumps(examples(arr, stratifiers(arr)["base"], a.think_run, a.rl_run), indent=1, ensure_ascii=False) + "\n")
    print((out / "table.md").read_text())


if __name__ == "__main__":
    main()
