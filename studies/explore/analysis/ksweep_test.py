"""Agent-count sweep test: fnf against parallel at each K (laptop, no model). Plan: specs/ksweep-ahc014-swe2.md.

    python3 studies/explore/analysis/ksweep_test.py runs/explore/ahc014/swe2-ksweep-02 \
        studies/explore/results/ahc014/swe2-seeds-01/summary.json [out.json]

New cells are read from <folder>/<arm>-k<K>-s<seed>/metrics.json; the K=4 cell from the seeds-test summary (6 + 6
runs). For validation and for held-out test scores (invalid = 0): mean, SD, worst per cell, gap(K) = mean fnf - mean
parallel, and a one-sided stratified permutation test: labels are permuted within each K, the statistic is the sum
over K of gap(K), every split is enumerated. Reported over all K and over the new cells alone (K != 4).
"""
import itertools
import json
import pathlib
import re
import statistics
import sys


def gaps(a, b):
    """All values of mean(x) - mean(y) over splits of a+b into len(a) and len(b); the observed split first."""
    pool, out = a + b, []
    for idx in itertools.combinations(range(len(pool)), len(a)):
        s = set(idx)
        x, y = [pool[i] for i in idx], [pool[i] for i in range(len(pool)) if i not in s]
        out.append(statistics.mean(x) - statistics.mean(y))
    return out


def stratified(cells):
    """cells: list of (fnf values, parallel values). Exact one-sided p for the sum of the per-cell gaps."""
    per = [gaps(f, p) for f, p in cells]
    obs = sum(g[0] for g in per)
    hit = n = 0
    for combo in itertools.product(*per):
        hit += sum(combo) >= obs - 1e-12
        n += 1
    return obs, hit / n, n


if __name__ == "__main__":
    d, k4 = pathlib.Path(sys.argv[1]), json.loads(pathlib.Path(sys.argv[2]).read_text())["runs"]
    runs = {4: {a: [{"seed": r["seed"], "val": r["val"], "test": r["test"] or 0.0} for r in k4[a]] for a in ("fnf", "parallel")}}
    for p in sorted(x for x in d.iterdir() if x.is_dir()):
        arm, k, seed = re.fullmatch(r"(\w+)-k(\d+)-s(\d+)", p.name).groups()
        m = json.loads((p / "metrics.json").read_text())
        runs.setdefault(int(k), {}).setdefault(arm, []).append({"seed": int(seed), "val": m["best_val"], "test": m.get("best_test") or 0.0})
    out = {"folder": str(d), "k4_from": sys.argv[2], "runs": {str(k): v for k, v in sorted(runs.items())}, "cells": {}}
    for key in ("val", "test"):
        cells = {}
        for k in sorted(runs):
            f, p = ([r[key] for r in runs[k][a]] for a in ("fnf", "parallel"))
            cells[k] = (f, p)
            out["cells"][f"{key} K={k}"] = {"gap": statistics.mean(f) - statistics.mean(p),
                                            **{a: {"n": len(v), "mean": statistics.mean(v), "sd": statistics.stdev(v), "worst": min(v)}
                                               for a, v in (("fnf", f), ("parallel", p))}}
        for name, ks in (("all K", sorted(cells)), ("new cells only", [k for k in sorted(cells) if k != 4])):
            obs, pv, n = stratified([cells[k] for k in ks])
            out[f"{key} stratified fnf>parallel, {name}"] = {"K": ks, "sum_of_gaps": obs, "p": pv, "splits": n}
    print(json.dumps({k: v for k, v in out.items() if k != "runs"}, indent=1))
    if len(sys.argv) > 3:
        pathlib.Path(sys.argv[3]).write_text(json.dumps(out, indent=1))
