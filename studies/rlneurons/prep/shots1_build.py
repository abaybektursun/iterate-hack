"""Builds data/shots1/{base,rl,code}.json: 3 solved MATH-500 problems as one text, to put in front of each prompt (run_cell --shots).
The 3 problems are the first 3 by index that all three source cells answered right (grader v3) and finished. The arms hold the same
3 problems and differ only in which model wrote the answers. Each example is the row's prompt + its answer (opening cue included)
+ "\n\n". Needs the three jobs' rows in runs/ (uv run tools/gpu.py get <job>).

    python3 studies/rlneurons/prep/shots1_build.py
"""
import json
import pathlib

STUDY = pathlib.Path(__file__).resolve().parents[1]
JOBS = {"base": "abaybektursun-1114-151028-ec3c",   # base, cue, T 1.0, problems 0-9 (results/day1/check_t1_n10-01)
        "rl": "abaybektursun-1114-153110-e985",     # Math-RL 3.1, cue, T 1.0 (results/day1_wdiff/rl_cue-01)
        "code": "abaybektursun-1114-162452-0203"}   # Code-RL 3.1, cue, T 1.0 (results/day1_wdiff/code_cue-01)
SEP = "\n\n"

rows = {k: {r["problem_index"]: r for r in map(json.loads, open(STUDY.parents[1] / "runs" / j / "answers.jsonl"))} for k, j in JOBS.items()}
ok = [i for i in sorted(rows["base"]) if all(rows[k][i]["score_v3"] == 1 and not rows[k][i]["cap_hit"] for k in JOBS)]
picked = ok[:3]
assert len(picked) == 3
for k, j in JOBS.items():
    ex = [rows[k][i] for i in picked]
    out = {"arm": k, "source_job": j, "problem_indices": picked, "answer_tokens": [r["n_answer_tokens"] for r in ex],
           "text": "".join(r["prompt"] + r["text"] + SEP for r in ex)}
    (STUDY / "data" / "shots1" / f"{k}.json").write_text(json.dumps(out, indent=1) + "\n")
    print(k, picked, out["answer_tokens"], len(out["text"]))
