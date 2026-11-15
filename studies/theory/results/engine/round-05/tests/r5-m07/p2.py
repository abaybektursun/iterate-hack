"""r5-m07 prediction 2: within step-100 plain T 0.6 answers, cap-hit rate of answers whose
text.lstrip() starts with 'line' (group A) minus that of all other kept rows (group B).
Refuted if measured < 0.02 or either group has fewer than 20 rows."""
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
                continue
            kept[pi] = r
            order.append(pi)
    return [kept[p] for p in order]


def diff(rows, pred):
    a = [r for r in rows if pred(r["text"])]
    b = [r for r in rows if not pred(r["text"])]
    if len(a) < 20 or len(b) < 20:
        return None, a, b
    ra = sum(1 for r in a if r["cap_hit"] is True) / len(a)
    rb = sum(1 for r in b if r["cap_hit"] is True) / len(b)
    return ra - rb, a, b


err = fetch()
if err:
    out(None, False, None, err, None)
try:
    rows = load_kept()
except (KeyError, ValueError) as e:
    out(None, False, None, f"file not readable as expected: {e!r}", None)
for r in rows:
    if not isinstance(r.get("text"), str) or "cap_hit" not in r:
        out(None, False, None, "row without text string or cap_hit field", None)

main, a, b = diff(rows, lambda t: t.lstrip().startswith("line"))
# alt reading: group A = answers opening with the full cue 'line!\n\nOkay' after lstrip
alt, _, _ = diff(rows, lambda t: t.lstrip().startswith("line!\n\nOkay"))

if main is None:
    # refuted_by: either group has fewer than 20 rows -> refuted without a number
    out(None, True, None, None, None)

example = next((r for r in a if r["cap_hit"] is True), a[0])
out(main, main < 0.02, alt, None, example)
