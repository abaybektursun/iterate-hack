"""signed1 readout (specs/SPEC_signed1.md): the signed-trained models, cue, on the 328 harder problems, each paired with the
cued base (results/day1_hard328, job abaybektursun-1114-151534-e72c). T 1.0 / top-p 1.0, seed 3000000, grader v3.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.signed1 <arm>=<train job>:<cell job> ...

Inputs in runs/<job>/ (uv run tools/gpu.py get <job>): train.json of the train job, answers.jsonl and metrics.json of the cell.
Writes results/signed1/<arm>-01/ (run.json, metrics.json, train.json without the per-step list, examples.json) and
results/signed1/readout.json.
"""
import json
import pathlib
import shutil
import sys

from studies.rlneurons.lib import n13_score as S

STUDY = pathlib.Path(__file__).resolve().parents[1]
BASE = "abaybektursun-1114-151534-e72c"
OUT = STUDY / "results" / "signed1"


def load(job):
    return {r["problem_index"]: r for r in map(json.loads, open(f"runs/{job}/answers.jsonl"))}


def cell(rows, idx):
    fin = [i for i in idx if not rows[i]["cap_hit"]]
    return {"right_v3": sum(rows[i]["score_v3"] for i in idx), "cap_hits": len(idx) - len(fin), "finished_right": sum(rows[i]["score_v3"] for i in fin),
            "mean_generated_tokens": round(sum(rows[i]["n_new"] for i in idx) / len(idx), 1)}


b = load(BASE)
idx = sorted(b)
assert len(idx) == 328
vb = [b[i]["score_v3"] for i in idx]
out = {"spec": "studies/rlneurons/specs/SPEC_signed1.md", "set": "hard328", "n": 328, "cells": {"base_cue": {"job_id": BASE, **cell(b, idx)}}}
for arg in sys.argv[1:]:
    arm, jobs = arg.split("=")
    train_job, job = jobs.split(":")
    a = load(job)
    assert sorted(a) == idx
    m = json.loads(pathlib.Path(f"runs/{job}/metrics.json").read_text())
    t = json.loads(pathlib.Path(f"runs/{train_job}/train.json").read_text())
    assert m["status"] == "done" and m["config"]["set"] == "hard328" and t["arm"] == arm and t["job_id"] == train_job
    va = [a[i]["score_v3"] for i in idx]
    lo, hi = S.paired_bootstrap(va, vb, n_boot=10000, seed=0)
    steps = t.pop("steps")
    half = len(steps) // 2
    gap = lambda s: sum(x["nll_negative"] - x["nll_positive"] for x in s) / len(s)
    d = OUT / f"{arm}-01"
    d.mkdir(parents=True)
    shutil.copy(f"runs/{job}/metrics.json", d / "metrics.json")
    (d / "train.json").write_text(json.dumps(t, indent=1) + "\n")
    (d / "run.json").write_text(json.dumps({"job_id": job, "train_job_id": train_job, "commit": m["commit"], "config": m["config"],
                                            "raw_answers": f"runs/{job}/answers.jsonl (uv run tools/gpu.py get {job})"}, indent=1) + "\n")
    ex = lambda i: {"problem_index": i, "gold": a[i]["gold"], "extracted_v3": a[i]["extracted_v3"], "score_v3": a[i]["score_v3"],
                    "n_new": a[i]["n_new"], "prompt_tail": a[i]["prompt"][-400:], "answer_tail": a[i]["text"][-800:]}
    (d / "examples.json").write_text(json.dumps({"right": ex(next(i for i in idx if a[i]["score_v3"])),
                                                 "wrong": ex(next(i for i in idx if not a[i]["score_v3"] and not a[i]["cap_hit"]))}, indent=1) + "\n")
    out["cells"][f"signed_{arm}_cue"] = {
        "job_id": job, "train_job_id": train_job, **cell(a, idx),
        "minus_base_cue": {"points": round(100 * (sum(va) - sum(vb)) / 328, 2), "ci95": [round(lo, 2), round(hi, 2)]},
        "only_signed": sum(x and not y for x, y in zip(va, vb)), "only_base": sum(y and not x for x, y in zip(va, vb)),
        "nll_negative_minus_positive": {"first_half": round(gap(steps[:half]), 4), "second_half": round(gap(steps[half:]), 4)},
        "cos_merged_rl": t["merge"]["all_targets"]["cos_merged_rl"], "rel_norm_merged": t["merge"]["all_targets"]["rel_norm_merged"]}
(OUT / "readout.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out, indent=1))
