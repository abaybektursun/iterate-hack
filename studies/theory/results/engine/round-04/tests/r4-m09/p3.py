"""r4-m09 p3: MATH-500, cap-hit rate of Code-RL cue answers (0203), first row per problem_index, denominator 500."""
import json
import os
import subprocess
import sys

DIR = "runs/theory-tests/r4m09"


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


path = fetch_modal("abaybektursun-1114-162452-0203")
if not os.path.exists(path):
    out(None, False, None, "iterate-runs:abaybektursun-1114-162452-0203/answers.jsonl could not be fetched", None)
rows = first_rows(path)
if not rows:
    out(None, False, None, "0203 answers.jsonl is empty", None)
if "cap_hit" not in next(iter(rows.values())):
    out(None, False, None, "cap_hit field missing in 0203 rows", None)

# only indices 0..499 are the 500 MATH-500 problems
kept = {i: r for i, r in rows.items() if isinstance(i, int) and 0 <= i < 500}
hits = sum(1 for r in kept.values() if r.get("cap_hit") is True)
measured = hits / 500
alt = hits / len(kept) if kept else None  # alt: denominator = problems present
example = strip(next((r for r in kept.values() if r.get("cap_hit") is True), next(iter(kept.values()))))
out(measured, measured > 0.026, alt, None, example)
