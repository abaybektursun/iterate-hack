"""Day-1 #4b readout (specs/DAY1_wdiff328_2026-11-14.md): Code-RL, theta(0.25) and theta(0.5) with the cue on the 328 harder problems
at T 1.0 / top-p 1.0, beside the four T 1.0 cells of Day-1 #1 (base plain, base cue, RL plain, RL cue); grader v3.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_wdiff328 [--hand <arm>]

Run from the repository root. Inputs (not committed): runs/<job-id>/ for the 7 jobs (`uv run tools/gpu.py get <job-id>`:
answers.jsonl, metrics.json, merge.json). Writes results/day1_wdiff328/readout.json and a run folder results/day1_wdiff328/<arm>-01/
per new cell. --hand <arm> prints the 20 finished answers scored wrong that the hand read uses (numpy seed 0); findings are HAND.
"""
from __future__ import annotations

import argparse
import itertools
import json
import pathlib

import numpy as np

from studies.rlneurons.analysis.day1_hard328 import JOBS as OLD, rows_by_index, score, summary
from studies.rlneurons.analysis.day1_wdiff import diff, merged, write_run

STUDY = pathlib.Path(__file__).resolve().parents[1]
RUNS = pathlib.Path("runs")
OUT = STUDY / "results" / "day1_wdiff328"
SET = "--set hard328 --temperature 1.0 --top-p 1.0"
COMMIT = "e7b86c89e9eac2651759dd30766f233c9fa78206"
# arm -> (job id, command without --commit); submitted as uv run tools/gpu.py submit h100 --hours 2.5 -- "<command> --commit <COMMIT>"
NEW = {
    "code1_cue": ("abaybektursun-1114-181216-a619", merged("code", 1, "cue", 71000000, "nearest", SET)),
    "theta0.25_cue": ("abaybektursun-1114-181222-a5f4", merged("rl", 0.25, "cue", 72000000, "stochastic", SET)),
    "theta0.5_cue": ("abaybektursun-1114-181228-34ad", merged("rl", 0.5, "cue", 73000000, "stochastic", SET)),
}
BASE, RL = "base_cue_T1", "rl_plain_T1"
# hand read: arm -> [(problem index, gold, what the model wrote)] of the 20 drawn answers that are in fact right
HAND = {"code1_cue": [], "theta0.25_cue": [], "theta0.5_cue": []}


def clean_set():
    hard = json.loads((STUDY / "data" / "rln3" / "hard.json").read_text())
    flags = json.loads((STUDY / "results" / "rln3" / "rln3_overlap.json").read_text())["sets"]["hard"]["flags"]
    clean = sorted(int(i) for i, f in flags.items() if f["flag"] == "none")
    assert len(clean) == 328
    return clean, {i: hard[i]["answer"] for i in clean}, {i: hard[i]["source"] for i in clean}


def load(job, clean):
    m = json.loads((RUNS / job / "metrics.json").read_text())
    assert m["status"] == "done" and m["counts"]["n"] == 328 and m["job_id"] == job, (job, m["status"], m["counts"])
    return m, rows_by_index(RUNS / job / "answers.jsonl", clean)


def hand(arm):
    clean, gold, _ = clean_set()
    _, rows = load(NEW[arm][0], clean)
    sc = score(rows, gold)
    wrong = sorted(i for i in sc if sc[i]["v3"] == 0 and not sc[i]["cap"])
    pick = sorted(np.random.default_rng(0).choice(wrong, size=min(20, len(wrong)), replace=False).tolist())
    for i in pick:
        print(f"=== {arm} problem {i} gold {gold[i]!r} extracted_v3 {sc[i]['extracted_v3']!r} tokens {rows[i]['n_new']}")
        print(rows[i]["text"][-700:])
    print(f"{arm}: {len(wrong)} finished wrong; drawn {pick}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hand")
    a = ap.parse_args()
    if a.hand:
        return hand(a.hand)
    clean, gold, source = clean_set()
    old_folders = {k: v["run_folder"] for k, v in json.loads((STUDY / "results" / "day1_hard328" / "readout.json").read_text())["cells"].items()}
    rows, sc, cells = {}, {}, {}
    for arm, (job, args, commit, _) in OLD.items():
        m, rows[arm] = load(job, clean)
        assert m["commit"] == commit and f"--seed {m['config']['seed']}" in args, (arm, m["config"])
        sc[arm] = score(rows[arm], gold)
        cells[arm] = {**summary(sc[arm]), "seed_base": m["config"]["seed"], "job_id": job, "answers": f"runs/{job}/answers.jsonl",
                      "run_folder": old_folders[arm]}
    OUT.mkdir(parents=True, exist_ok=True)
    for arm, (job, cmd) in NEW.items():
        m, rows[arm] = load(job, clean)
        c = m["config"]
        assert m["commit"] == COMMIT and c["set"] == "hard328" and c["prompt"] == "cue" and c["temperature"] == c["top_p"] == 1.0, (arm, c)
        assert f"--seed {c['seed']}" in cmd and f"--model-label {c['model_label']} " in cmd, (arm, c)
        assert all(r["seed"] == c["seed"] + i for i, r in rows[arm].items()), arm
        sc[arm] = score(rows[arm], gold)
        mg = json.loads((RUNS / job / "merge.json").read_text())
        assert f"--other {mg['args']['other']} " in cmd and f"--rounding {mg['args']['rounding']} " in cmd and mg["args"]["alpha"] == float(cmd.split("--alpha ")[1].split()[0]), (arm, mg["args"])
        eff = next(iter(mg["points"].values()))
        cells[arm] = {**summary(sc[arm]), "seed_base": c["seed"], "job_id": job, "answers": f"runs/{job}/answers.jsonl",
                      "s3_answers": f"s3://pg-lineage-769063704696/results/rlneurons/r5/day1_wdiff328-01/{job}/answers.jsonl",
                      "alpha": mg["args"]["alpha"], "rounding": mg["args"]["rounding"], "effective_a": eff["effective_a"],
                      "merge_identity": mg["identity"], "tokens_per_s": m["counts"]["tokens_per_s"],
                      "run_folder": write_run(arm, job, COMMIT, cmd, 2.5, rows[arm], sc[arm], out=OUT),
                      "hand_read_right_of_20": HAND[arm], "right_corrected": None}
        cells[arm]["right_corrected"] = cells[arm]["right_v3"] + len(HAND[arm])
    assert cells["code1_cue"]["merge_identity"]["exact"] == cells["code1_cue"]["merge_identity"]["tensors"] == 355

    identical = {f"{x} | {y}": sum(rows[x][i]["text"] == rows[y][i]["text"] != "" for i in clean) for x, y in itertools.combinations(sorted(rows), 2)}
    assert not any(identical.values()), {k: v for k, v in identical.items() if v}
    pairs = [(x, y) for x in NEW for y in (BASE, RL)] + [("code1_cue", "theta0.5_cue"), (RL, BASE)]
    diffs = {f"{x} minus {y}": diff(sc, x, y, clean) for x, y in pairs}
    diffs[f"{RL} minus code1_cue"] = diff(sc, RL, "code1_cue", clean)
    sources = sorted(set(source.values()))
    per_source = {arm: {s: sum(sc[arm][i]["v3"] for i in clean if source[i] == s) for s in sources} for arm in sc}
    per_source["n"] = {s: sum(source[i] == s for i in clean) for s in sources}
    churn = {arm: {"fixed_of_base_cue_wrong": sum(sc[BASE][i]["v3"] == 0 and sc[arm][i]["v3"] == 1 for i in clean),
                   "lost_of_base_cue_right": sum(sc[BASE][i]["v3"] == 1 and sc[arm][i]["v3"] == 0 for i in clean)}
             for arm in [*NEW, RL, "rl_cue_T1"]}
    churn["base_cue_wrong"], churn["base_cue_right"] = 328 - cells[BASE]["right_v3"], cells[BASE]["right_v3"]

    q1 = diffs[f"{RL} minus code1_cue"]
    cap = [cells[k]["cap_hits"] for k in (BASE, "theta0.25_cue", "theta0.5_cue")]
    rl_caps = [cells[RL]["cap_hits"], cells["rl_cue_T1"]["cap_hits"]]
    rises = [y - x for x, y in zip(cap, cap[1:])] + [r - cap[-1] for r in rl_caps]
    pred = {
        "Q1": {"text": "RL plain minus Code-RL cue: refuted if the interval's lower end is above 5 points", "diff": q1,
               "interval_includes_0": q1["ci95"][0] <= 0 <= q1["ci95"][1], "status": "refuted" if q1["ci95"][0] > 5 else "held"},
        "Q2": {"text": "theta(0.5) cue >= 190 of 328", "right": cells["theta0.5_cue"]["right_v3"]},
        "Q3": {"text": "theta(0.25) cue >= 185 of 328", "right": cells["theta0.25_cue"]["right_v3"]},
        "Q4": {"text": "cap hits base cue > theta(0.25) > theta(0.5) > RL (plain 20, cue 25); refuted by any rise larger than 10",
               "cap_hits": dict(zip([BASE, "theta0.25_cue", "theta0.5_cue", RL, "rl_cue_T1"], cap + rl_caps)), "rises": rises,
               "status": "refuted" if max(rises) > 10 else ("held" if max(rises) < 0 else "not refuted (a rise of at most 10)")},
    }
    for k, bar in (("Q2", 190), ("Q3", 185)):
        pred[k]["status"] = "held" if pred[k]["right"] >= bar else "refuted"

    res = {"spec": "studies/rlneurons/specs/DAY1_wdiff328_2026-11-14.md", "grader": "rln4_lib.grade_v3", "n": 328, "cells": cells,
           "per_source_right_v3": per_source, "differences": diffs, "bootstrap": "paired, 5,000 resamples, seed 0, 95 % percentile",
           "fixed_lost_vs_base_cue": churn, "identical_nonempty_texts": identical, "predictions": pred}
    (OUT / "readout.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: res[k] for k in ("cells", "per_source_right_v3", "differences", "fixed_lost_vs_base_cue", "predictions")}, indent=1))


if __name__ == "__main__":
    main()
