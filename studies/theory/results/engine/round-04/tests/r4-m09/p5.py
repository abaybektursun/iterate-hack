"""r4-m09 p5: hard328, Code-RL cue (a619) accuracy on problems where the base cue (e72c) finished without a cap hit and was wrong."""
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


pb = fetch_s3("day1_hard328-01", "abaybektursun-1114-151534-e72c")
pc = fetch_s3("day1_wdiff328-01", "abaybektursun-1114-181216-a619")
for p in (pb, pc):
    if not os.path.exists(p):
        out(None, False, None, "%s could not be fetched" % p, None)
base = first_rows(pb)
code = first_rows(pc)
for name, t in (("e72c", base), ("a619", code)):
    if t:
        r0 = next(iter(t.values()))
        for fld in ("cap_hit", "score_v3"):
            if fld not in r0:
                out(None, False, None, "%s field missing in %s rows" % (fld, name), None)

sel = [i for i, r in base.items() if r.get("cap_hit") is False and r.get("score_v3") == 0]
if not sel:
    out(None, False, None, "no e72c problems with cap_hit == false and score_v3 == 0", None)

right = sum(1 for i in sel if i in code and code[i].get("score_v3") == 1)
measured = right / len(sel)
present = [i for i in sel if i in code]
alt = (right / len(present)) if present else None  # alt: a619-missing problems dropped from denominator
example = next((strip(code[i]) for i in sel if i in code), None)
out(measured, measured > 0.26, alt, None, example)
