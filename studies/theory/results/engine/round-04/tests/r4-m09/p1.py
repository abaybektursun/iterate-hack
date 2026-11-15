"""r4-m09 p1: MATH-500, Code-RL cue (0203) accuracy on problems where the cued base (T1) hit the cap and was wrong."""
import json
import os
import subprocess
import sys

DIR = "runs/theory-tests/r4m09"
PER_PROBLEM = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"


def out(measured, met, alt, nc, ex):
    print(json.dumps({"measured": measured, "refuted_by_met": met, "alt_measured": alt,
                      "not_computable": nc, "example_row": ex}))
    sys.exit(0)


def fetch_modal(job):
    path = os.path.join(DIR, job, "answers.jsonl")
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(["modal", "volume", "get", "iterate-runs", job + "/answers.jsonl", path],
                       check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return path


def first_rows(path):
    rows = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r["problem_index"] not in rows:
                rows[r["problem_index"]] = r
    return rows


def strip(r):
    return {k: v for k, v in r.items() if k not in ("text", "prompt", "answer_tokens")}


try:
    pp = json.load(open(PER_PROBLEM))
except Exception as e:
    out(None, False, None, "per_problem.json not readable: %s" % e, None)

path = fetch_modal("abaybektursun-1114-162452-0203")
if not os.path.exists(path):
    out(None, False, None, "iterate-runs:abaybektursun-1114-162452-0203/answers.jsonl could not be fetched", None)
code = first_rows(path)
if code and "score_v3" not in next(iter(code.values())):
    out(None, False, None, "score_v3 field missing in 0203 rows", None)

sel = [p["problem_index"] for p in pp if p["t1_right"] == 0 and p["t1_cap_hit"] is True]
if not sel:
    out(None, False, None, "no problems with t1_right == 0 and t1_cap_hit == true", None)

right = 0
present = 0
right_present = 0
example = None
for i in sel:
    r = code.get(i)
    if r is None:
        continue  # missing row counts as wrong
    present += 1
    if r.get("score_v3") == 1:
        right += 1
        right_present += 1
    if example is None:
        example = strip(r)

measured = right / len(sel)
alt = (right_present / present) if present else None  # alt: missing rows dropped from the denominator
out(measured, measured < 0.40, alt, None, example)
