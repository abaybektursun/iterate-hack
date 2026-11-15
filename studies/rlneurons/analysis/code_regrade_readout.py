"""Readout of a Code pair regrade (jobs/regrade_code.py; specs/SPEC_code_think.md amendments 1 and 2).

    python -m studies.rlneurons.analysis.code_regrade_readout <rule: v2 | v3> <job id>

Reads runs/<job id>/<cell>/answers_<rule>.jsonl and writes results/code_think/regrade_<rule>-01/: run.json, readout.json (passed
of 538 under v1 and under the rule, modes, each pair of cells by paired bootstrap, 5,000 resamples, seed 0) and examples.json
(for the first Think-SFT cell: the first rerun program that passed and the first that failed, with the answer's end and stderr).
"""
from __future__ import annotations

import itertools
import json
import pathlib
import sys

import numpy as np

STUDY = pathlib.Path(__file__).resolve().parents[1]


def main():
    k, job = sys.argv[1], sys.argv[2]
    run = pathlib.Path("runs") / job
    out = STUDY / "results" / "code_think" / f"regrade_{k}-01"
    out.mkdir(parents=True)
    cells = {c.name: {r["uid"]: r for r in map(json.loads, open(c / f"answers_{k}.jsonl"))} for c in sorted(run.iterdir()) if c.is_dir()}
    uids = sorted(next(iter(cells.values())))
    assert all(sorted(rows) == uids for rows in cells.values()) and len(uids) == 538
    ro = {"rule": k, "job_id": job, "instrument_check": json.loads((run / "check.json").read_text()),
          "cells": {c: json.loads((run / c / f"metrics_{k}.json").read_text()) for c in cells}, "differences_points": {}}
    rng = np.random.default_rng(0)
    idx = rng.integers(0, 538, (5000, 538))
    for a, b in itertools.combinations(cells, 2):
        d = np.array([float(cells[a][u][f"passed_{k}"]) - float(cells[b][u][f"passed_{k}"]) for u in uids])
        ro["differences_points"][f"{a} - {b}"] = {"points": 100 * d.mean(), "bootstrap95": np.percentile(100 * d[idx].mean(1), [2.5, 97.5]).tolist(),
                                                  "only_first": int((d > 0).sum()), "only_second": int((d < 0).sum())}
    (out / "readout.json").write_text(json.dumps(ro, indent=1))
    (out / "run.json").write_text(json.dumps({"job_id": job, "command": " ".join(sys.argv)}, indent=1))
    first = next(c for c in cells if c.startswith("sft1"))
    rerun = [r for r in cells[first].values() if f"code_{k}" in r]
    ex = {str(ok): {"cell": first, "uid": r["uid"], "answer_end": r["text"][-1500:], f"code_{k}": r[f"code_{k}"],
                    f"passed_{k}": r[f"passed_{k}"], f"stderr_tail_{k}": r[f"stderr_tail_{k}"]}
          for ok in (True, False) for r in [next(r for r in rerun if r[f"passed_{k}"] == ok)]}
    (out / "examples.json").write_text(json.dumps(ex, indent=1))
    print(json.dumps({c: m[f"passed_{k}"] for c, m in ro["cells"].items()}))
    for p, d in ro["differences_points"].items():
        print(p, round(d["points"], 1), [round(x, 1) for x in d["bootstrap95"]])


if __name__ == "__main__":
    main()
