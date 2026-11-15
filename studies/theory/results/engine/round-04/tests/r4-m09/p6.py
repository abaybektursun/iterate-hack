"""r4-m09 p6: hard328, cap-hit rate of Code-RL cue answers (a619), first row per problem_index, denominator 328."""
import json
import os
import subprocess
import sys

DIR = "runs/theory-tests/r4m09"
BUCKET = "s3://pg-lineage-769063704696/results/rlneurons/r5/"


def out(measured, met, alt, nc, ex):
    print(json.dumps({"measured": measured, "refuted_by_met": met, "alt_measured": alt,
                      "not_computable": nc, "example_row": ex}))
    sys.exit(0)


def fetch_s3(prefix, job):
    path = os.path.join(DIR, job, "answers.jsonl")
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", BUCKET + prefix + "/" + job + "/answers.jsonl", path,
                        "--profile", "iterate-ecr", "--only-show-errors"],
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


pc = fetch_s3("day1_wdiff328-01", "abaybektursun-1114-181216-a619")
if not os.path.exists(pc):
    out(None, False, None, "%s could not be fetched" % pc, None)
rows = first_rows(pc)
if not rows:
    out(None, False, None, "a619 answers.jsonl is empty", None)
if "cap_hit" not in next(iter(rows.values())):
    out(None, False, None, "cap_hit field missing in a619 rows", None)

hits = sum(1 for r in rows.values() if r.get("cap_hit") is True)
measured = hits / 328
alt = hits / len(rows)  # alt: denominator = distinct problems present
example = strip(next((r for r in rows.values() if r.get("cap_hit") is True), next(iter(rows.values()))))
out(measured, measured > 0.125, alt, None, example)
