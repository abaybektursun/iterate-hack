"""shots1 readout (specs/SPEC_shots1.md): the cued base on MATH-500 at T 1.0 / top-p 1.0 with 3 solved examples in front of each
prompt, the arms differing in who wrote the 3 answers, beside base cue (T1), theta 0.25 cue and RL cue. Grader v3. The 3 example
problems are left out of every count.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.shots1 <name> <arm>=<job> ...

<name> is the readout's folder under results/ (shots1: arms base, rl, code; shots2: those three, the second draw base_b, rl_b
and the loop's generations, specs/SPEC_shots2.md). <arm> is a file of data/shots1/ or data/shots2/. Every example that is a
MATH-500 problem, of any arm in the readout, is left out of every count. Run from the repository root. Inputs (not committed): runs/<job-id>/ (`uv run tools/gpu.py get <job-id>`) and T1 in
runs/s3/r4/base_rl-02/out/T1.jsonl. Writes results/<name>/readout.json and a run folder results/<name>/<arm>-01/ per cell that has none yet in results/shots1/.
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
OLD = {"T1_base_cue": "s3/r4/base_rl-02/out/T1.jsonl",
       "theta0.25_cue": "abaybektursun-1114-153102-b029/answers.jsonl",
       "rl_cue": "abaybektursun-1114-153110-e985/answers.jsonl"}
PAIRS1 = [("shots_rl", "T1_base_cue"), ("shots_base", "T1_base_cue"), ("shots_code", "T1_base_cue"), ("shots_rl", "shots_base"),
          ("shots_code", "shots_rl"), ("shots_rl", "theta0.25_cue"), ("shots_rl", "rl_cue")]


def shots_file(arm):
    return next(f for f in (STUDY / "data" / d / f"{arm}.json" for d in ("shots1", "shots2")) if f.exists())


def main():
    name, jobs = sys.argv[1], dict(x.split("=") for x in sys.argv[2:])
    OUT = STUDY / "results" / name
    files = {arm: json.loads(shots_file(arm).read_text()) for arm in jobs}
    probs = json.loads((STUDY / "data" / "rln4" / "math500.json").read_text())
    left_out = sorted({i for f in files.values() if "source_set" not in f for i in f["problem_indices"]})   # MATH-500 examples
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
            if (STUDY / "results" / "shots1" / d.name).exists() and name != "shots1":
                continue                         # the cell's run folder is in results/shots1/
            assert not d.exists(), f"{d} exists: a rerun gets the next number"
            d.mkdir(parents=True)
            m = json.loads((RUNS / cells[k]["job_id"] / "metrics.json").read_text())
            (d / "run.json").write_text(json.dumps({"job_id": cells[k]["job_id"], "commit": m["commit"], "config": m["config"],
                                                    "raw_answers": f"runs/{cells[k]['job_id']}/answers.jsonl (uv run tools/gpu.py get)"}, indent=1) + "\n")
            shutil.copy(RUNS / cells[k]["job_id"] / "metrics.json", d / "metrics.json")
            (d / "examples.json").write_text(json.dumps(examples(rows[k], sc[k]), indent=1) + "\n")
    arms = [f"shots_{a}" for a in jobs]
    pairs = PAIRS1 if name == "shots1" else [(x, y) for x in arms for y in OLD] + [(x, y) for i, x in enumerate(arms) for y in arms[i + 1:]]
    for x, y in pairs:
        vx, vy = [sc[x][i]["v3"] for i in idx], [sc[y][i]["v3"] for i in idx]
        lo, hi = S.paired_bootstrap(vx, vy, n_boot=10000, seed=0)
        out["differences"][f"{x} minus {y}"] = {"points": round(100 * (sum(vx) - sum(vy)) / len(idx), 2), "ci95": [round(lo, 2), round(hi, 2)]}
    OUT.mkdir(exist_ok=True)
    (OUT / "readout.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"cells": out["cells"], "differences": out["differences"]}, indent=1))


if __name__ == "__main__":
    main()
