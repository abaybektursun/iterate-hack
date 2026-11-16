"""Several samples per model from one Code pair regrade (jobs/regrade_code.py; specs/SPEC_code_think.md amendment 3).

    python -m studies.rlneurons.analysis.code_regrade_means <rule> <job id> <new folder under results/code_think/>

Cells are named <model>_s<seed prefix>. Writes run.json and readout.json: passed of 538 per cell under v1 and the rule, the
per-model mean, and each pair of models by paired bootstrap over problems of the per-problem mean pass (5,000 resamples, seed 0).
"""
from __future__ import annotations

import collections
import itertools
import json
import pathlib
import sys

import numpy as np

STUDY = pathlib.Path(__file__).resolve().parents[1]


def main():
    k, job, name = sys.argv[1:4]
    run = pathlib.Path("runs") / job
    out = STUDY / "results" / "code_think" / name
    out.mkdir(parents=True)
    cells = {c.name: {r["uid"]: r for r in map(json.loads, open(c / f"answers_{k}.jsonl"))} for c in sorted(run.iterdir()) if c.is_dir()}
    uids = sorted(next(iter(cells.values())))
    assert all(sorted(rows) == uids for rows in cells.values()) and len(uids) == 538
    models = collections.defaultdict(list)
    for c in cells:
        models[c.rsplit("_s", 1)[0]].append(c)
    mean = {m: np.array([np.mean([cells[c][u][f"passed_{k}"] for c in cs]) for u in uids]) for m, cs in models.items()}
    ro = {"rule": k, "job_id": job, "instrument_check": json.loads((run / "check.json").read_text()),
          "cells": {c: {"seed": rows[uids[0]]["seed"] - rows[uids[0]]["idx"], "passed_v1": sum(r["passed"] for r in rows.values()),
                        f"passed_{k}": sum(r[f"passed_{k}"] for r in rows.values())} for c, rows in cells.items()},
          "models": {m: {"cells": cs, f"mean_passed_{k}": float(mean[m].sum())} for m, cs in models.items()}, "differences_points": {}}
    idx = np.random.default_rng(0).integers(0, 538, (5000, 538))
    for a, b in itertools.combinations(models, 2):
        d = mean[a] - mean[b]
        ro["differences_points"][f"{a} - {b}"] = {"points": 100 * d.mean(), "bootstrap95": np.percentile(100 * d[idx].mean(1), [2.5, 97.5]).tolist()}
    (out / "readout.json").write_text(json.dumps(ro, indent=1))
    (out / "run.json").write_text(json.dumps({"job_id": job, "command": " ".join(sys.argv)}, indent=1))
    print(json.dumps(ro, indent=1))


if __name__ == "__main__":
    main()
