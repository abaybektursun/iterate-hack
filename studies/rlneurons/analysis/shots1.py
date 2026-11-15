"""shots1 readout (specs/SPEC_shots1.md): the cued base on MATH-500 at T 1.0 / top-p 1.0 with 3 solved examples in front of each
prompt, the arms differing in who wrote the 3 answers, beside base cue (T1), theta 0.25 cue and RL cue. Grader v3. The 3 example
problems are left out of every count.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.shots1 base=<job> rl=<job> code=<job>

Run from the repository root. Inputs (not committed): runs/<job-id>/ (`uv run tools/gpu.py get <job-id>`) and T1 in
runs/s3/r4/base_rl-02/out/T1.jsonl. Writes results/shots1/readout.json and a run folder results/shots1/<arm>-01/ per cell.
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys

from studies.rlneurons.analysis.day1_hard328 import examples, rows_by_index, score, summary
from studies.rlneurons.lib import n13_score as S

STUDY = pathlib.Path(__file__).resolve().parents[1]
RUNS = pathlib.Path("runs")
OUT = STUDY / "results" / "shots1"
OLD = {"T1_base_cue": "s3/r4/base_rl-02/out/T1.jsonl",
       "theta0.25_cue": "abaybektursun-1114-153102-b029/answers.jsonl",
       "rl_cue": "abaybektursun-1114-153110-e985/answers.jsonl"}
PAIRS = [("shots_rl", "T1_base_cue"), ("shots_base", "T1_base_cue"), ("shots_code", "T1_base_cue"), ("shots_rl", "shots_base"),
         ("shots_code", "shots_rl"), ("shots_rl", "theta0.25_cue"), ("shots_rl", "rl_cue")]


def main():
    jobs = dict(x.split("=") for x in sys.argv[1:])
    assert set(jobs) == {"base", "rl", "code"}, jobs
    probs = json.loads((STUDY / "data" / "rln4" / "math500.json").read_text())
    left_out = json.loads((STUDY / "data" / "shots1" / "rl.json").read_text())["problem_indices"]
    idx = [int(p["index"]) for p in probs if int(p["index"]) not in left_out]
    gold = {int(p["index"]): p["answer"] for p in probs}
    rows = {k: rows_by_index(RUNS / f, idx) for k, f in OLD.items()}
    cells = {}
    for arm, job in jobs.items():
        m = json.loads((RUNS / job / "metrics.json").read_text())
        assert m["status"] == "done" and m["config"]["shots_arm"] == arm and m["counts"]["n"] == len(probs), (arm, job)
        rows[f"shots_{arm}"] = rows_by_index(RUNS / job / "answers.jsonl", idx)
        cells[f"shots_{arm}"] = {"job_id": job, "commit": m["commit"], "shots_tokens": m["config"]["shots_tokens"]}
    sc = {k: score(r, gold) for k, r in rows.items()}
    out = {"spec": "studies/rlneurons/specs/SPEC_shots1.md", "n": len(idx), "left_out": left_out, "cells": {}, "differences": {}}
    for k in sc:
        out["cells"][k] = {**summary(sc[k]), **cells.get(k, {})}
        if k in cells:
            out["cells"][k]["shot_stops"] = sum(r["shot_stop"] for r in rows[k].values())
            d = OUT / f"{k.removeprefix('shots_')}-01"
            assert not d.exists(), f"{d} exists: a rerun gets the next number"
            d.mkdir(parents=True)
            m = json.loads((RUNS / cells[k]["job_id"] / "metrics.json").read_text())
            (d / "run.json").write_text(json.dumps({"job_id": cells[k]["job_id"], "commit": m["commit"], "config": m["config"],
                                                    "raw_answers": f"runs/{cells[k]['job_id']}/answers.jsonl (uv run tools/gpu.py get)"}, indent=1) + "\n")
            shutil.copy(RUNS / cells[k]["job_id"] / "metrics.json", d / "metrics.json")
            (d / "examples.json").write_text(json.dumps(examples(rows[k], sc[k]), indent=1) + "\n")
    for x, y in PAIRS:
        vx, vy = [sc[x][i]["v3"] for i in idx], [sc[y][i]["v3"] for i in idx]
        lo, hi = S.paired_bootstrap(vx, vy, n_boot=10000, seed=0)
        out["differences"][f"{x} minus {y}"] = {"points": round(100 * (sum(vx) - sum(vy)) / len(idx), 2), "ci95": [round(lo, 2), round(hi, 2)]}
    (OUT / "readout.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"cells": out["cells"], "differences": out["differences"]}, indent=1))


if __name__ == "__main__":
    main()
