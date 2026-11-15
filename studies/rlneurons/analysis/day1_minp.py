"""min-p readout (specs/SPEC_minp.md, board work-180a48): MATH-500, cue, top-p 1.0, grader v3, min-p 0.1 at T 1.0 and T 1.5 on the
base and at T 1.0 on RL, against the min-p 0 cells of the same seed.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_minp

Run from the repository root. Inputs (not committed): runs/<job-id>/answers.jsonl (`uv run tools/gpu.py get <job-id>`) for each arm
in ARMS, and the base+cue min-p 0 rows T1 in runs/s3/r4/base_rl-02/out/T1.jsonl
(`aws s3 cp --profile iterate-ecr s3://pg-lineage-769063704696/results/rlneurons/r4/base_rl-02/out/T1.jsonl ...`).
Writes results/day1_minp/readout.json and a run folder results/day1_minp/<arm>-01/ per arm (run.json, metrics.json, examples.json).
"""
from __future__ import annotations

import json
import pathlib

from studies.rlneurons.analysis.day1_hard328 import examples, rows_by_index, score, summary
from studies.rlneurons.lib import n13_score as S

STUDY = pathlib.Path(__file__).resolve().parents[1]
RUNS = pathlib.Path("runs")
OUT = STUDY / "results" / "day1_minp"
COMMIT = "2188884a3f4ec8467db01ef2beab9b6d3f96c812"
CMD = ("bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model {m} --prompt cue "
       "--set math500 --temperature {t} --top-p 1.0 --min-p 0.1 --seed {s} --commit " + COMMIT)
# arm: (job id, model, T, seed); filled in as the jobs are submitted
ARMS = {}
BASELINES = {"T1_base_cue": (RUNS / "s3" / "r4" / "base_rl-02" / "out" / "T1.jsonl", 410)}   # 410: readout of day1_wdiff
RL_CUE_MP0 = 457            # results/day1_wdiff/rl_cue-01/metrics.json correct_v3 (raw rows not available here: unpaired)


def tail_tokens(rows):
    n = sum(r["n_new"] for r in rows.values())
    return {"generated_tokens": n, "tok_p_lt_1e2_per_1k": round(1000 * sum(r.get("n_tok_p_lt_1e2", 0) for r in rows.values()) / n, 3),
            "tok_p_lt_1e3_per_1k": round(1000 * sum(r.get("n_tok_p_lt_1e3", 0) for r in rows.values()) / n, 3)}


def main():
    gold = {int(p["index"]): p["answer"] for p in json.loads((STUDY / "data" / "rln4" / "math500.json").read_text())}
    idx = sorted(gold)
    rows, sc, cells = {}, {}, {}
    for arm, (path, expect) in BASELINES.items():
        rows[arm] = rows_by_index(path, idx)
        sc[arm] = score(rows[arm], gold)
        cells[arm] = summary(sc[arm])
        assert cells[arm]["right_v3"] == expect, (arm, cells[arm]["right_v3"], expect)
    for arm, (job, m, t, s) in ARMS.items():
        mt = json.loads((RUNS / job / "metrics.json").read_text())
        assert mt["status"] == "done" and mt["counts"]["n"] == 500, (arm, mt["status"], mt.get("counts"))
        rows[arm] = rows_by_index(RUNS / job / "answers.jsonl", idx)
        sc[arm] = score(rows[arm], gold)
        cells[arm] = {**summary(sc[arm]), **tail_tokens(rows[arm]), "job_id": job}
        d = OUT / f"{arm}-01"
        assert not d.exists(), f"{d} exists: a rerun gets the next number"
        d.mkdir(parents=True)
        (d / "run.json").write_text(json.dumps({"job_id": job, "commit": COMMIT, "command": CMD.format(m=m, t=t, s=s),
                                                "runner": "uv run tools/gpu.py submit h100 --hours 1.5",
                                                "raw_answers": f"runs/{job}/answers.jsonl (uv run tools/gpu.py get {job})"}, indent=1) + "\n")
        (d / "metrics.json").write_text(json.dumps(mt, indent=1) + "\n")
        (d / "examples.json").write_text(json.dumps(examples(rows[arm], sc[arm]), indent=1) + "\n")
    diffs = {}
    for arm in ARMS:
        if ARMS[arm][1] == "base":
            vx, vy = [sc[arm][i]["v3"] for i in idx], [sc["T1_base_cue"][i]["v3"] for i in idx]
            lo, hi = S.paired_bootstrap(vx, vy, n_boot=5000, seed=0)
            diffs[f"{arm} minus T1_base_cue"] = {"points": round(100 * (sum(vx) - sum(vy)) / len(idx), 2), "ci95_paired": [round(lo, 2), round(hi, 2)]}
        else:
            diffs[f"{arm} minus rl_cue-01 (unpaired)"] = {"points": round(100 * (cells[arm]["right_v3"] - RL_CUE_MP0) / 500, 2)}
    readout = {"spec": "studies/rlneurons/specs/SPEC_minp.md", "grader": "v3", "n": 500, "cells": cells,
               "rl_cue_mp0_right_v3": RL_CUE_MP0, "diffs": diffs}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "readout.json").write_text(json.dumps(readout, indent=1) + "\n")
    print(json.dumps(readout, indent=1))


if __name__ == "__main__":
    main()
