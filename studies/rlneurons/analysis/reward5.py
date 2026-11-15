"""Reward content test, step 1 readout (specs/SPEC_reward5.md): the five Olmo 3 RL-Zero models (IF, General, Mix, Math, Code) on
MATH-500 at T 1.0 / top-p 1.0, cue and plain, grader v3, beside the cells of results/day1_wdiff (base cue T1, base plain T3,
RL 3.1 plain T2 and cue, Code-RL 3.1 cue and plain).

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.reward5

Run from the repository root. Inputs (not committed): runs/<job-id>/ of every job in CELLS and of the three day1_wdiff jobs in
OLD_JOBS (`uv run tools/gpu.py get <job-id>`), and T1, T2, T3 in runs/s3/ (see analysis/day1_wdiff.py). Writes
results/reward5/readout.json and one run folder results/reward5/<arm>-01/ per cell.
"""
from __future__ import annotations

import itertools
import json
import pathlib

from studies.rlneurons.analysis import day1_wdiff as W
from studies.rlneurons.analysis.day1_hard328 import rows_by_index, score, summary

OUT = W.STUDY / "results" / "reward5"
COMMIT = "3b4ab2a20f6c1c53113c7bde48fa20157e4c3649"
KEYS = ("if30", "general30", "mix30", "math30", "code30")
JOBS = {"if30_cue": "abaybektursun-1114-182707-731c", "general30_cue": "abaybektursun-1114-182712-3556", "mix30_cue": "abaybektursun-1114-182718-612b",
        "math30_cue": "abaybektursun-1114-182724-87aa", "code30_cue": "abaybektursun-1114-182730-9523", "if30_plain": "abaybektursun-1114-182735-bcca",
        "general30_plain": "abaybektursun-1114-182742-9129", "mix30_plain": "abaybektursun-1114-182748-3300", "math30_plain": "abaybektursun-1114-182754-7238",
        "code30_plain": "abaybektursun-1114-182800-3331"}
SEEDS = {f"{k}_{p}": 91000000 + 1000000 * (i + 5 * (p == "plain")) for p in ("cue", "plain") for i, k in enumerate(KEYS)}
OLD_JOBS = {"code31_cue": "abaybektursun-1114-162452-0203", "code31_plain": "abaybektursun-1114-153052-5013", "math31_cue": "abaybektursun-1114-153110-e985"}
OLD_S3 = {"base_cue": "T1_base_cue", "math31_plain": "T2_rl_plain", "base_plain": "T3_base_plain"}


def main():
    W.OUT = OUT                                                   # write_run writes below W.OUT
    OUT.mkdir(parents=True, exist_ok=True)
    g, idx = W.gold(), range(500)
    rows, sc, cells = {}, {}, {}
    for arm, name in OLD_S3.items():
        key, want_right, want_cap, _, _ = W.OLD[name]
        rows[arm] = rows_by_index(W.RUNS / "s3" / key, idx)
        sc[arm] = score(rows[arm], g)
        cells[arm] = {**summary(sc[arm]), "from": f"results/day1_wdiff/readout.json cell {name}"}
        assert (cells[arm]["right_v3"], cells[arm]["cap_hits"]) == (want_right, want_cap), (arm, cells[arm])
    for arm, job in OLD_JOBS.items():
        _, rows[arm] = W.load_job(job, 500)
        sc[arm] = score(rows[arm], g)
        cells[arm] = {**summary(sc[arm]), "job_id": job, "from": "results/day1_wdiff"}
    for arm, job in JOBS.items():
        other, prompt = arm.split("_")
        m, rows[arm] = W.load_job(job, 500)
        assert m["commit"] == COMMIT and m["config"]["seed"] == SEEDS[arm] and m["config"]["prompt"] == prompt and m["config"]["model_label"] == other, (arm, m["config"])
        assert all(r["seed"] == SEEDS[arm] + i for i, r in rows[arm].items()), arm
        mg = json.loads((W.RUNS / job / "merge.json").read_text())
        assert mg["args"]["other"] == other and mg["identity"]["exact"] == mg["identity"]["tensors"] == 355, (arm, mg["args"], mg["identity"])
        sc[arm] = score(rows[arm], g)
        cmd = W.merged(other, 1, prompt, SEEDS[arm], "nearest")
        cells[arm] = {**summary(sc[arm]), "seed_base": SEEDS[arm], "job_id": job, "model": mg["other"],
                      "frac_changed": mg["overall"]["frac_changed"], "rel_norm": mg["overall"]["rel_norm"],
                      "word_salad_tails": sum(W.word_salad(rows[arm][i]["text"]) for i in idx),
                      "run_folder": W.write_run(arm, job, COMMIT, cmd, 2.5, rows[arm], sc[arm])}
    same = {f"{x} | {y}": sum(rows[x][i]["text"] == rows[y][i]["text"] != "" for i in idx) for x, y in itertools.combinations(sorted(rows), 2)}
    assert not any(same.values()), {k: v for k, v in same.items() if v}          # an identical non-empty text means a reused seed
    pairs = [(f"{k}_cue", "base_cue") for k in KEYS] + [(f"{k}_cue", "math30_cue") for k in KEYS if k != "math30"]
    pairs += [(f"{k}_plain", "math30_plain") for k in KEYS if k != "math30"] + [(f"{k}_plain", "base_plain") for k in KEYS]
    pairs += [(f"{k}_cue", f"{k}_plain") for k in KEYS] + [("math31_cue", "math30_cue"), ("code31_cue", "code30_cue"), ("code31_cue", "base_cue"), ("math31_cue", "base_cue")]
    diffs = {f"{x} minus {y}": W.diff(sc, x, y, idx) for x, y in pairs}
    res = {"spec": "studies/rlneurons/specs/SPEC_reward5.md", "grader": "rln4_lib.grade_v3", "n": 500, "cells": cells, "differences": diffs,
           "bootstrap": "paired, 5,000 resamples, seed 0, 95 % percentile"}
    (OUT / "readout.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({a: {k: c[k] for k in ("right_v3", "cap_hits", "mean_generated_tokens")} for a, c in cells.items()}, indent=1))
    print(json.dumps(diffs, indent=1))


if __name__ == "__main__":
    main()
