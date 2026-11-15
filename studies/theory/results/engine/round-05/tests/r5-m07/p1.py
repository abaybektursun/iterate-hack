"""r5-m07 prediction 1: share of step-100 plain MATH-500 answers (T 0.6 / top-p 0.95)
whose text.lstrip() starts with 'line'. Refuted if measured < 0.35."""
import json
import os
import subprocess
import sys

S3 = "s3://pg-lineage-769063704696/results/rlneurons/r3/s0400_s0100-01/out/s0100/P_math500.jsonl"
LOCAL = "runs/theory-tests/s0100_P_math500.jsonl"


def out(measured, refuted, alt, nc, ex):
    print(json.dumps({"measured": measured, "refuted_by_met": refuted, "alt_measured": alt,
                      "not_computable": nc, "example_row": ex}))
    sys.exit(0)


def fetch():
    if os.path.exists(LOCAL) and os.path.getsize(LOCAL) > 0:
        return None
    os.makedirs(os.path.dirname(LOCAL), exist_ok=True)
    r = subprocess.run(["aws", "s3", "cp", S3, LOCAL, "--profile", "iterate-ecr"],
                       capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(LOCAL):
        return f"fetch of {S3} failed: {r.stderr.strip()[:300]}"
    return None


def load_kept():
    kept = {}
    order = []
    with open(LOCAL) as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if r["sample"] != 0:
                continue
            pi = r["problem_index"]
            if pi in kept:
                continue  # first row in file order wins
            kept[pi] = r
            order.append(pi)
    return [kept[p] for p in order]


err = fetch()
if err:
    out(None, False, None, err, None)
try:
    rows = load_kept()
except (KeyError, ValueError) as e:
    out(None, False, None, f"file not readable as expected: {e!r}", None)

for r in rows:
    if "text" not in r or not isinstance(r["text"], str):
        out(None, False, None, "row without a text string", None)

if not rows:
    out(None, False, None, "no rows with sample == 0", None)

n = len(rows)
passing = [r for r in rows if r["text"].lstrip().startswith("line")]
measured = len(passing) / n

# alt reading: the opening is the full RL cue ' line!\n\nOkay' (after lstrip), not just its first 4 chars
alt_pass = [r for r in rows if r["text"].lstrip().startswith("line!\n\nOkay")]
alt = len(alt_pass) / n

example = passing[0] if passing else rows[0]
out(measured, measured < 0.35, alt, None, example)
