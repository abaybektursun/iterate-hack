"""Day-1 #1 readout (specs/DAY1_hard328_2026-11-14.md): the 328 clean harder problems, four cells at T 1.0 / top-p 1.0 beside
the three RLN-3 cells at T 0.6 / top-p 0.95, all rescored with grader v3; plus the 50-problem reproduction check against T1.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_hard328 [--check-only]

Run from the repository root. Inputs (not committed): runs/<job-id>/answers.jsonl and metrics.json (`uv run tools/gpu.py get
<job-id>`), and the S3 files copied to runs/s3/<key> (`aws s3 cp s3://pg-lineage-769063704696/results/rlneurons/<key> ...`).
Writes results/day1_hard328/readout.json and a run folder results/day1_hard328/<arm>-01/{run.json,metrics.json,examples.json}
for the check and each new T 1.0 cell. The base-cue and RL-plain T 1.0 jobs already have run folders in results/day1/
(analysis/day1_rows.py); the readout names them instead of copying them.
"""
from __future__ import annotations

import argparse
import itertools
import json
import pathlib
import shutil

from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

STUDY = pathlib.Path(__file__).resolve().parents[1]
RUNS = pathlib.Path("runs")
OUT = STUDY / "results" / "day1_hard328"
RUNNER = "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell"

# arm -> (job id, run_cell arguments, git commit, run folder written by another script or None); submitted with
# uv run tools/gpu.py submit h100 --hours 2 -- "<RUNNER> <arguments> --commit <commit>"
JOBS = {
    "base_plain_T1": ("abaybektursun-1114-132922-7ba0", "--model base --prompt plain --set hard328 --temperature 1.0 --top-p 1.0 --seed 50000000",
                      "5236c1ab742c59e6653fa38e265c037a88855a27", None),
    "base_cue_T1": ("abaybektursun-1114-151534-e72c", "--model base --prompt cue --set hard328 --temperature 1.0 --top-p 1.0 --seed 3000000",
                    "5e5d9344b7baf660ebb46b3ee35ad524a93d3cc1", "studies/rlneurons/results/day1/hard328_base_cue_t10-01"),
    "rl_plain_T1": ("abaybektursun-1114-151540-86ef", "--model rl --prompt plain --set hard328 --temperature 1.0 --top-p 1.0 --seed 3000000",
                    "5e5d9344b7baf660ebb46b3ee35ad524a93d3cc1", "studies/rlneurons/results/day1/hard328_rl_plain_t10-01"),
    "rl_cue_T1": ("abaybektursun-1114-132929-a32d", "--model rl --prompt cue --set hard328 --temperature 1.0 --top-p 1.0 --seed 50000000",
                  "5236c1ab742c59e6653fa38e265c037a88855a27", None),
}
CHECK = ("abaybektursun-1114-132917-7f81", "--model base --prompt cue --set math500 --temperature 1.0 --top-p 1.0 --seed 41000000 --n 50",
         "5236c1ab742c59e6653fa38e265c037a88855a27")
# T 0.6 / top-p 0.95 cells of RLN-3 (seed 3,000,000 + index) and the counts the spec says they must reproduce (right v3, cap hits)
T06 = {"base_plain_T0.6": ("r3/base-01/out/P_hard.jsonl", 107, 137),
       "base_cue_T0.6": ("r3/base-01/out/F_hard.jsonl", 119, 173),
       "rl_plain_T0.6": ("r3/s2800-01/out/P_hard.jsonl", 204, 64)}
T1_FILE = "r4/base_rl-02/out/T1.jsonl"
DIFFS = [("rl_plain_T1", "base_cue_T1"), ("rl_cue_T1", "base_cue_T1"), ("base_cue_T1", "base_cue_T0.6")]


def rows_by_index(path, keep):
    out = {}
    for line in open(path):
        r = json.loads(line)
        assert r["problem_index"] not in out, (path, r["problem_index"])
        out[r["problem_index"]] = r
    assert set(keep) <= set(out), (path, len(set(keep) - set(out)), "problems missing")
    return {i: out[i] for i in keep}


def score(rows, gold):
    """Per problem: v3 score, cap hit, rule-A loop (recomputed on the text), generated tokens."""
    res = {}
    for i, r in rows.items():
        assert r["gold"] == gold[i], (i, r["gold"], gold[i])
        g = R.grade_v3(gold[i], r["text"])
        if "score_v3" in r:
            assert r["score_v3"] == g["score_v3"], (i, "stored v3 score differs from the rescore")
        res[i] = {"v3": g["score_v3"], "extracted_v3": g["extracted_v3"], "cap": int(r["cap_hit"]),
                  "loop_A": int(R.onset_lines(r["text"]) is not None), "tokens": r["n_new"]}
    return res


def summary(sc):
    n = len(sc)
    return {"n": n, "right_v3": sum(s["v3"] for s in sc.values()), "cap_hits": sum(s["cap"] for s in sc.values()),
            "loops_A": sum(s["loop_A"] for s in sc.values()), "mean_generated_tokens": round(sum(s["tokens"] for s in sc.values()) / n, 1)}


def write_run(name, job, args, commit, rows, sc, hours):
    d = OUT / f"{name}-01"
    assert not d.exists(), f"{d} exists: a rerun gets the next number"
    d.mkdir(parents=True)
    (d / "run.json").write_text(json.dumps({"job_id": job, "commit": commit, "command": f"{RUNNER} {args} --commit {commit}",
                                            "runner": f"uv run tools/gpu.py submit h100 --hours {hours}",
                                            "raw_answers": f"runs/{job}/answers.jsonl (uv run tools/gpu.py get {job})"}, indent=1) + "\n")
    shutil.copy(RUNS / job / "metrics.json", d / "metrics.json")
    (d / "examples.json").write_text(json.dumps(examples(rows, sc), indent=1) + "\n")
    return f"studies/rlneurons/results/{OUT.name}/{d.name}"


def check():
    job, args, commit = CHECK
    m = json.loads((RUNS / job / "metrics.json").read_text())
    assert m["status"] == "done" and m["counts"]["n"] == 50, (m["status"], m.get("counts"))
    gold = {int(p["index"]): p["answer"] for p in json.loads((STUDY / "data" / "rln4" / "math500.json").read_text())}
    rows = rows_by_index(RUNS / job / "answers.jsonl", range(50))
    sc = score(rows, gold)
    ours = summary(sc)
    t1 = summary(score(rows_by_index(RUNS / "s3" / T1_FILE, range(50)), gold))
    ok = abs(ours["right_v3"] - t1["right_v3"]) <= 6 and abs(ours["cap_hits"] - t1["cap_hits"]) <= 4
    return {"job": job, "args": args, "ours": ours, "T1_first50": t1, "rule": "right within 6 and cap hits within 4", "pass": ok}, (job, args, commit, rows, sc)


def examples(rows, sc):
    def item(i):
        r = rows[i]
        return {"problem_index": i, "gold": r["gold"], "extracted_v3": sc[i]["extracted_v3"], "score_v3": sc[i]["v3"],
                "cap_hit": bool(r["cap_hit"]), "n_new": r["n_new"], "prompt_tail": r["prompt"][-400:], "answer_tail": r["text"][-800:]}
    right = next(i for i in sorted(sc) if sc[i]["v3"] == 1)
    wrong = next(i for i in sorted(sc) if sc[i]["v3"] == 0 and not sc[i]["cap"])
    return {"right": item(right), "wrong": item(wrong)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args()
    chk, chk_run = check()
    print(json.dumps(chk, indent=1))
    if a.check_only:
        return
    assert chk["pass"], "reproduction check failed: no cell is scored"
    chk["run_folder"] = write_run("check_t1_n50", *chk_run, 0.5)

    hard = json.loads((STUDY / "data" / "rln3" / "hard.json").read_text())
    flags = json.loads((STUDY / "results" / "rln3" / "rln3_overlap.json").read_text())["sets"]["hard"]["flags"]
    clean = sorted(int(i) for i, f in flags.items() if f["flag"] == "none")
    assert len(clean) == 328
    gold = {i: hard[i]["answer"] for i in clean}
    source = {i: hard[i]["source"] for i in clean}

    rows, sc, cells = {}, {}, {}
    for arm, (job, args, commit, folder) in JOBS.items():
        m = json.loads((RUNS / job / "metrics.json").read_text())
        assert m["status"] == "done" and m["counts"]["n"] == 328, (arm, m["status"], m["counts"]["n"])
        assert m["job_id"] == job and m["commit"] == commit, (arm, m["job_id"], m["commit"])
        c = m["config"]
        assert f"--model {c['model']} --prompt {c['prompt']} --set {c['set']} --temperature {c['temperature']} --top-p {c['top_p']} --seed {c['seed']}" == args, (arm, c)
        rows[arm] = rows_by_index(RUNS / job / "answers.jsonl", clean)
        sc[arm] = score(rows[arm], gold)
        cells[arm] = {**summary(sc[arm]), "seed_base": c["seed"], "job_id": job, "answers": f"runs/{job}/answers.jsonl",
                      "run_folder": folder or write_run(arm, job, args, commit, rows[arm], sc[arm], 2)}
    for arm, (key, want_right, want_cap) in T06.items():
        rows[arm] = rows_by_index(RUNS / "s3" / key, clean)
        sc[arm] = score(rows[arm], gold)
        s = summary(sc[arm])
        cells[arm] = {**s, "seed_base": 3000000, "job_id": None, "answers": f"s3://pg-lineage-769063704696/results/rlneurons/{key}",
                      "expected": {"right_v3": want_right, "cap_hits": want_cap},
                      "reproduced": s["right_v3"] == want_right and s["cap_hits"] == want_cap}

    identical = {f"{x} | {y}": sum(rows[x][i]["text"] == rows[y][i]["text"] for i in clean) for x, y in itertools.combinations(sorted(rows), 2)}
    same_first100 = {f"{x} | {y}": sum(rows[x][i]["text"][:100] == rows[y][i]["text"][:100] for i in clean)
                     for x, y in itertools.combinations(sorted(rows), 2)}
    for x, y in DIFFS:
        pair = " | ".join(sorted((x, y)))
        assert identical[pair] == 0, (pair, identical[pair])
    diffs = {}
    for x, y in DIFFS:
        vx, vy = [sc[x][i]["v3"] for i in clean], [sc[y][i]["v3"] for i in clean]
        lo, hi = S.paired_bootstrap(vx, vy, n_boot=5000, seed=0)
        diffs[f"{x} minus {y}"] = {"points": round(100 * (sum(vx) - sum(vy)) / len(clean), 2), "ci95": [round(lo, 2), round(hi, 2)]}
    per_source = {arm: {s: sum(sc[arm][i]["v3"] for i in clean if source[i] == s) for s in sorted(set(source.values()))} for arm in sc}
    per_source["n"] = {s: sum(source[i] == s for i in clean) for s in sorted(set(source.values()))}

    bc, gain = cells["base_cue_T1"], diffs["base_cue_T1 minus base_cue_T0.6"]
    pred = {"text": "base cue T 1.0: under 60 cap hits of 328 and at least 8 points over T 0.6; refuted if cap hits > 120 or the gain's 95 % interval includes 0",
            "cap_hits": bc["cap_hits"], "gain_points": gain["points"], "gain_ci95": gain["ci95"],
            "held": bc["cap_hits"] < 60 and gain["points"] >= 8 and gain["ci95"][0] > 0,
            "refuted": bc["cap_hits"] > 120 or gain["ci95"][0] <= 0 <= gain["ci95"][1]}
    res = {"spec": "studies/rlneurons/specs/DAY1_hard328_2026-11-14.md", "grader": "rln4_lib.grade_v3", "n": len(clean), "check": chk,
           "cells": cells, "per_source_right_v3": per_source, "differences": diffs, "bootstrap": "paired, 5,000 resamples, seed 0, 95 % percentile",
           "identical_texts": identical, "same_first_100_chars": same_first100, "prediction": pred}
    (OUT / "readout.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: res[k] for k in ("cells", "differences", "prediction")}, indent=1))


if __name__ == "__main__":
    main()
