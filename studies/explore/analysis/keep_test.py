"""Fork without flush against fnf and parallel at K = 2 and 8 (laptop, no model). Plan: specs/keep-ahc014-swe2.md.

    python3 studies/explore/analysis/keep_test.py runs/explore/ahc014/swe2-keep-01 runs/explore/ahc014/swe2-ksweep-02 [out.json]

Reads <folder>/<arm>-k<K>-s<seed>/metrics.json from both folders. For validation and held-out test scores
(invalid = 0): per-cell mean, SD, worst; the share (fnf_keep - parallel) / (fnf - parallel) of the cell means; and
the two planned one-sided stratified permutation tests over K (labels permuted within K, every split enumerated,
analysis/ksweep_test.py): fnf_keep > parallel (sharing) and fnf > fnf_keep (flush).
"""
import json
import pathlib
import re
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from ksweep_test import stratified  # noqa: E402

if __name__ == "__main__":
    runs = {}
    for d in (pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])):
        for p in sorted(x for x in d.iterdir() if x.is_dir()):
            arm, k, seed = re.fullmatch(r"(\w+)-k(\d+)-s(\d+)", p.name).groups()
            m = json.loads((p / "metrics.json").read_text())
            runs.setdefault(k, {}).setdefault(arm, []).append({"seed": int(seed), "val": m["best_val"], "test": m.get("best_test") or 0.0})
    out = {"folders": sys.argv[1:3], "runs": runs, "cells": {}}
    for key in ("val", "test"):
        v = {k: {a: [r[key] for r in rs] for a, rs in arms.items()} for k, arms in runs.items()}
        for k in sorted(v, key=int):
            mean = {a: statistics.mean(x) for a, x in v[k].items()}
            out["cells"][f"{key} K={k}"] = {
                "share_of_fnf_gap": (mean["fnf_keep"] - mean["parallel"]) / (mean["fnf"] - mean["parallel"]),
                **{a: {"n": len(x), "mean": mean[a], "sd": statistics.stdev(x), "worst": min(x)} for a, x in v[k].items()}}
        for name, hi, lo in (("sharing: fnf_keep>parallel", "fnf_keep", "parallel"), ("flush: fnf>fnf_keep", "fnf", "fnf_keep")):
            obs, p, n = stratified([(v[k][hi], v[k][lo]) for k in sorted(v, key=int)])
            out[f"{key} {name}"] = {"sum_of_gaps": obs, "p": p, "splits": n}
    print(json.dumps({k: x for k, x in out.items() if k != "runs"}, indent=1))
    if len(sys.argv) > 3:
        pathlib.Path(sys.argv[3]).write_text(json.dumps(out, indent=1))
