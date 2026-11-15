"""The RL-written examples of shots1 (data/shots1/rl.json) in front of the cued base on the 328 harder problems, paired with the
cued base without examples (results/day1_hard328, job abaybektursun-1114-151534-e72c). T 1.0 / top-p 1.0, seed 3000000, v3.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.shots_hard328

Inputs in runs/<job>/ (uv run tools/gpu.py get <job>). Writes results/shots1b/hard328_rl-01/ (run.json, metrics.json, readout.json,
examples.json).
"""
import json
import pathlib
import shutil

from studies.rlneurons.lib import n13_score as S

STUDY = pathlib.Path(__file__).resolve().parents[1]
JOB, BASE = "abaybektursun-1114-195404-351b", "abaybektursun-1114-151534-e72c"
OUT = STUDY / "results" / "shots1b" / "hard328_rl-01"


def load(job):
    return {r["problem_index"]: r for r in map(json.loads, open(f"runs/{job}/answers.jsonl"))}


def cell(rows, idx, job):
    fin = [i for i in idx if not rows[i]["cap_hit"]]
    return {"job_id": job, "right_v3": sum(rows[i]["score_v3"] for i in idx), "cap_hits": len(idx) - len(fin), "finished": len(fin),
            "finished_right": sum(rows[i]["score_v3"] for i in fin), "mean_generated_tokens": round(sum(rows[i]["n_new"] for i in idx) / len(idx), 1)}


a, b = load(JOB), load(BASE)
idx = sorted(a)
assert sorted(b) == idx and len(idx) == 328
va, vb = [a[i]["score_v3"] for i in idx], [b[i]["score_v3"] for i in idx]
lo, hi = S.paired_bootstrap(va, vb, n_boot=10000, seed=0)
m = json.loads(pathlib.Path(f"runs/{JOB}/metrics.json").read_text())
assert m["status"] == "done" and m["config"]["shots_arm"] == "rl" and m["config"]["set"] == "hard328"
OUT.mkdir(parents=True)
shutil.copy(f"runs/{JOB}/metrics.json", OUT / "metrics.json")
(OUT / "run.json").write_text(json.dumps({"job_id": JOB, "commit": m["commit"], "config": m["config"],
                                          "raw_answers": f"runs/{JOB}/answers.jsonl (uv run tools/gpu.py get {JOB})"}, indent=1) + "\n")
out = {"set": "hard328", "n": 328, "cells": {"shots_rl": cell(a, idx, JOB), "base_cue": cell(b, idx, BASE)},
       "shots_rl minus base_cue": {"points": round(100 * (sum(va) - sum(vb)) / 328, 2), "ci95": [round(lo, 2), round(hi, 2)]},
       "both_right": sum(x and y for x, y in zip(va, vb)), "only_shots": sum(x and not y for x, y in zip(va, vb)),
       "only_base": sum(y and not x for x, y in zip(va, vb))}
(OUT / "readout.json").write_text(json.dumps(out, indent=1) + "\n")
ex = lambda i: {"problem_index": i, "gold": a[i]["gold"], "extracted_v3": a[i]["extracted_v3"], "score_v3": a[i]["score_v3"],
                "n_new": a[i]["n_new"], "prompt_tail": a[i]["prompt"][-400:], "answer_tail": a[i]["text"][-800:]}
(OUT / "examples.json").write_text(json.dumps({"right": ex(next(i for i in idx if a[i]["score_v3"])),
                                               "wrong": ex(next(i for i in idx if not a[i]["score_v3"] and not a[i]["cap_hit"]))}, indent=1) + "\n")
print(json.dumps(out, indent=1))
