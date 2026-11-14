"""Day-1 #4 readout (specs/DAY1_wdiff_2026-11-14.md): MATH-500 at T 1.0 / top-p 1.0 along theta(a) = base + a * (RL - base), the
Code-RL model and the random control of matched norm, beside T1 (base cue), T2 (RL plain) and T3 (base plain); grader v3.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_wdiff [--check-only | --hand <arm>]

Run from the repository root. Inputs (not committed): runs/<job-id>/ (`uv run tools/gpu.py get <job-id>`: answers.jsonl,
metrics.json, merge.json) and T1, T2, T3 in runs/s3/<key> (`aws s3 cp s3://pg-lineage-769063704696/results/rlneurons/<key> ...`).
Writes results/day1_wdiff/readout.json, results/day1_wdiff/merge_stats.json (the statistics-only job, without the per-tensor rows)
and a run folder results/day1_wdiff/<arm>-01/ per new cell and the check. --hand <arm> prints the 20 finished answers scored wrong
that the hand read uses (numpy seed 0); its findings are HAND below.
"""
from __future__ import annotations

import argparse
import itertools
import json
import pathlib
import shutil

import numpy as np

from studies.rlneurons.analysis.day1_hard328 import examples, rows_by_index, score, summary
from studies.rlneurons.lib import n13_score as S

STUDY = pathlib.Path(__file__).resolve().parents[1]
RUNS = pathlib.Path("runs")
OUT = STUDY / "results" / "day1_wdiff"
SETUP, PY = "bash studies/rlneurons/jobs/setup_vllm.sh && ", "/opt/rln-vllm/bin/python -m studies.rlneurons.jobs."
CELL = "--set math500 --temperature 1.0 --top-p 1.0"


def merged(other, a, prompt, seed, rounding):
    """The command of a cell on a merged model (without --commit). rm -rf: Modal reuses a container, /tmp included."""
    kind = "--random" if a == "random" else f"--alpha {a}"
    label = f"{other}_random" if a == "random" else f"{'theta' if other == 'rl' else other}{a}"
    return (f"{SETUP}rm -rf /tmp/theta && {PY}merge_weights --other {other} {kind} --rounding {rounding} --dir /tmp/theta && {PY}run_cell --model-path /tmp/theta "
            f"--model-label {label} --prompt {prompt} {CELL} --seed {seed}")


# arm -> (job id, commit, command without --commit, a on the RL line or None, hours); submitted as
# uv run tools/gpu.py submit h100 --hours <hours> -- "<command> --commit <commit>"
A, B = "6cc0fd79cdda7ff1347b71ac546cf148ba362d64", "f16189ab350d89a1e1debb9799817a9d47292a14"
CELLS = {
    "theta0.5_cue": ("abaybektursun-1114-152855-683b", A, merged("rl", 0.5, "cue", 61000000, "stochastic"), 0.5, 2.5),
    "random_cue": ("abaybektursun-1114-153047-6429", B, merged("rl", "random", "cue", 69000000, "nearest"), None, 2.5),
    "code_plain": ("abaybektursun-1114-153052-5013", B, merged("code", 1, "plain", 67000000, "nearest"), None, 2.5),
    "theta1.5_cue": ("abaybektursun-1114-153057-45e7", B, merged("rl", 1.5, "cue", 63000000, "stochastic"), 1.5, 2.5),
    "theta0.25_cue": ("abaybektursun-1114-153102-b029", B, merged("rl", 0.25, "cue", 60000000, "stochastic"), 0.25, 2.5),
    "theta0.75_cue": ("abaybektursun-1114-153106-af79", B, merged("rl", 0.75, "cue", 62000000, "stochastic"), 0.75, 2.5),
    "rl_cue": ("abaybektursun-1114-153110-e985", B, f"{SETUP}{PY}run_cell --model rl --prompt cue {CELL} --seed 66000000", 1.0, 2.5),
}
CHECK = ("abaybektursun-1114-152849-c7c6", A, merged("rl", 1, "plain", 45000000, "nearest") + " --n 50", 0.5)
STATS = "abaybektursun-1114-152416-de10"                 # merge_weights --other rl / --other code, statistics only
COS = "abaybektursun-1114-153037-ebe8"                   # merge_weights --other code --cos-with-rl
OLD = {"T1_base_cue": ("r4/base_rl-02/out/T1.jsonl", 410, 27, 41000000, 0.0),
       "T2_rl_plain": ("r4/modal_t2-01/t2/T2.jsonl", 463, 6, 45000000, 1.0),
       "T3_base_plain": ("r4/modal_t3-01/t3/T3.jsonl", 224, 8, 47000000, 0.0)}
CUE_ROW = ["T1_base_cue", "theta0.25_cue", "theta0.5_cue", "theta0.75_cue", "rl_cue", "theta1.25_cue", "theta1.5_cue"]
# hand read: arm -> [(problem index, gold, what the model wrote)] of the 20 drawn answers that are in fact right
HAND = {}


def gold():
    return {int(p["index"]): p["answer"] for p in json.loads((STUDY / "data" / "rln4" / "math500.json").read_text())}


def load_job(job, n):
    m = json.loads((RUNS / job / "metrics.json").read_text())
    assert m["status"] == "done" and m["counts"]["n"] == n and m["job_id"] == job, (job, m["status"], m.get("counts"))
    return m, rows_by_index(RUNS / job / "answers.jsonl", range(n))


def write_run(arm, job, commit, cmd, hours, rows, sc):
    d = OUT / f"{arm}-01"
    assert not d.exists(), f"{d} exists: a rerun gets the next number"
    d.mkdir(parents=True)
    (d / "run.json").write_text(json.dumps({"job_id": job, "commit": commit, "command": f"{cmd} --commit {commit}",
                                            "runner": f"uv run tools/gpu.py submit h100 --hours {hours}",
                                            "raw_answers": f"runs/{job}/answers.jsonl (uv run tools/gpu.py get {job})"}, indent=1) + "\n")
    shutil.copy(RUNS / job / "metrics.json", d / "metrics.json")
    if (RUNS / job / "merge.json").exists():
        m = json.loads((RUNS / job / "merge.json").read_text())
        m.pop("tensors")
        (d / "merge.json").write_text(json.dumps(m, indent=1) + "\n")
    (d / "examples.json").write_text(json.dumps(examples(rows, sc), indent=1) + "\n")
    return f"studies/rlneurons/results/{OUT.name}/{d.name}"


def check():
    job, commit, cmd, hours = CHECK
    g = gold()
    m, rows = load_job(job, 50)
    sc = score(rows, g)
    ours = summary(sc)
    t2_rows = rows_by_index(RUNS / "s3" / OLD["T2_rl_plain"][0], range(50))
    t2 = summary(score(t2_rows, g))
    mg = json.loads((RUNS / job / "merge.json").read_text())
    ok = abs(ours["right_v3"] - t2["right_v3"]) <= 6 and abs(ours["cap_hits"] - t2["cap_hits"]) <= 4
    res = {"job": job, "command": cmd, "ours": ours, "T2_first50": t2, "rule": "right within 6 and cap hits within 4", "pass": ok,
           "merge_identity": mg["identity"], "identical_texts_vs_T2": sum(rows[i]["text"] == t2_rows[i]["text"] for i in range(50))}
    return res, (job, commit, cmd, hours, rows, sc)


def hand(arm):
    job = CELLS[arm][0]
    g = gold()
    _, rows = load_job(job, 500)
    sc = score(rows, g)
    wrong = sorted(i for i in sc if sc[i]["v3"] == 0 and not sc[i]["cap"])
    pick = sorted(np.random.default_rng(0).choice(wrong, size=min(20, len(wrong)), replace=False).tolist())
    for i in pick:
        print(f"=== {arm} problem {i} gold {g[i]!r} extracted_v3 {sc[i]['extracted_v3']!r} tokens {rows[i]['n_new']}")
        print(rows[i]["text"][-700:])
    print(f"{arm}: {len(wrong)} finished wrong; drawn {pick}")


def diff(sc, x, y, idx):
    vx, vy = [sc[x][i]["v3"] for i in idx], [sc[y][i]["v3"] for i in idx]
    lo, hi = S.paired_bootstrap(vx, vy, n_boot=5000, seed=0)
    return {"points": round(100 * (sum(vx) - sum(vy)) / len(idx), 2), "ci95": [round(lo, 2), round(hi, 2)]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-only", action="store_true")
    ap.add_argument("--hand")
    a = ap.parse_args()
    if a.hand:
        return hand(a.hand)
    chk, chk_run = check()
    print(json.dumps(chk, indent=1))
    if a.check_only:
        return
    assert chk["pass"] and chk["merge_identity"]["exact"] == chk["merge_identity"]["tensors"] == 355, "check failed: no cell is scored"
    OUT.mkdir(parents=True, exist_ok=True)
    chk["run_folder"] = write_run("check_theta1_plain_n50", *chk_run)

    stats = {}
    for other in ("rl", "code"):
        m = json.loads((RUNS / STATS / f"merge_{other}.json").read_text())
        m.pop("tensors")
        stats[other] = m
    cos = json.loads((RUNS / COS / "merge_code_cos.json").read_text())["cos_with_rl"]
    (OUT / "merge_stats.json").write_text(json.dumps({"job_id": STATS, **stats, "code_vs_rl": {"job_id": COS, "groups": cos}}, indent=1) + "\n")

    g = gold()
    idx = range(500)
    rows, sc, cells = {}, {}, {}
    for arm, (key, want_right, want_cap, seed, alpha) in OLD.items():
        rows[arm] = rows_by_index(RUNS / "s3" / key, idx)
        sc[arm] = score(rows[arm], g)
        s = summary(sc[arm])
        assert (s["right_v3"], s["cap_hits"]) == (want_right, want_cap), (arm, s)
        cells[arm] = {**s, "seed_base": seed, "job_id": None, "a": alpha, "answers": f"s3://pg-lineage-769063704696/results/rlneurons/{key}"}
    for arm, (job, commit, cmd, alpha, hours) in CELLS.items():
        m, rows[arm] = load_job(job, 500)
        assert m["commit"].startswith(commit) and f"--seed {m['config']['seed']}" in cmd and f"--prompt {m['config']['prompt']}" in cmd, (arm, m["config"])
        assert all(r["seed"] == m["config"]["seed"] + i for i, r in rows[arm].items()), arm
        sc[arm] = score(rows[arm], g)
        mg = json.loads((RUNS / job / "merge.json").read_text()) if (RUNS / job / "merge.json").exists() else None
        eff = next(iter(mg["points"].values())) if mg else None
        cells[arm] = {**summary(sc[arm]), "seed_base": m["config"]["seed"], "job_id": job, "a": alpha,
                      "effective_a": eff["effective_a"] if eff else None, "norm_ratio_after_rounding": eff["norm_ratio"] if eff else None,
                      "rounding": mg["args"]["rounding"] if mg else None, "answers": f"runs/{job}/answers.jsonl",
                      "run_folder": write_run(arm, job, commit, cmd, hours, rows[arm], sc[arm])}
        if arm in HAND:
            cells[arm]["hand_read_right_of_20"] = HAND[arm]
            cells[arm]["right_corrected"] = cells[arm]["right_v3"] + len(HAND[arm])

    identical = {f"{x} | {y}": sum(rows[x][i]["text"] == rows[y][i]["text"] for i in idx) for x, y in itertools.combinations(sorted(rows), 2)}
    assert not any(identical.values()), {k: v for k, v in identical.items() if v}
    pairs = [(f"theta{x}_cue", y) for x in ("0.25", "0.5", "0.75", "1.25", "1.5") for y in ("T1_base_cue", "T2_rl_plain")]
    row = [c for c in CUE_ROW if c in sc]
    pairs += [(y, x) for x, y in zip(row, row[1:])]
    pairs += [("random_cue", "T1_base_cue"), ("code_plain", "T2_rl_plain"), ("code_plain", "T1_base_cue"), ("code_cue", "T1_base_cue"),
              ("rl_cue", "T2_rl_plain"), ("theta0.25_plain", "T3_base_plain"), ("theta0.5_plain", "T3_base_plain"), ("code0.5_cue", "T1_base_cue")]
    diffs = {f"{x} minus {y}": diff(sc, x, y, idx) for x, y in dict.fromkeys(pairs) if x in sc and y in sc}

    def right(arm):
        return cells[arm]["right_v3"] if arm in cells else None

    def d(x, y):
        return diffs.get(f"{x} minus {y}")

    p1 = [c for c in CUE_ROW[:5] if c in sc]                       # T1 to RL cue
    steps = [d(y, x) for x, y in zip(p1, p1[1:])]
    p = {}
    p["P1"] = {"text": "cue row monotone from T1 to RL cue: no adjacent step with its 95 % interval entirely below 0", "steps": steps,
               "status": "refuted" if any(s["ci95"][1] < 0 for s in steps) else "held"}
    p["P2"] = {"text": "acc(0.5, cue) >= 437", "right": right("theta0.5_cue")}
    p["P3"] = {"text": "acc(1.5, cue) minus T2: interval includes 0 or lies below it", "diff": d("theta1.5_cue", "T2_rl_plain")}
    p["P4"] = {"text": "random cue minus T1: interval includes 0 or lies below it", "diff": d("random_cue", "T1_base_cue")}
    p["P5"] = {"text": "acc(Code, plain) >= 437", "right": right("code_plain")}
    p["P6"] = {"text": "acc(0.5, plain) >= 400", "right": right("theta0.5_plain")}
    for k in ("P2", "P5", "P6"):
        bar = 400 if k == "P6" else 437
        p[k]["status"] = "not tested" if p[k]["right"] is None else ("held" if p[k]["right"] >= bar else "refuted")
    for k in ("P3", "P4"):
        p[k]["status"] = "not tested" if p[k]["diff"] is None else ("refuted" if p[k]["diff"]["ci95"][0] > 0 else "held")

    res = {"spec": "studies/rlneurons/specs/DAY1_wdiff_2026-11-14.md", "grader": "rln4_lib.grade_v3", "n": 500, "check": chk,
           "cells": cells, "differences": diffs, "bootstrap": "paired, 5,000 resamples, seed 0, 95 % percentile",
           "identical_texts": identical, "predictions": p, "merge_stats": f"studies/rlneurons/results/{OUT.name}/merge_stats.json"}
    (OUT / "readout.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: res[k] for k in ("cells", "differences", "predictions")}, indent=1))


if __name__ == "__main__":
    main()
