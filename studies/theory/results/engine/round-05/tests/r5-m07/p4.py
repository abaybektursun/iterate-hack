"""r5-m07 prediction 4: share of step-100 finished (cap_hit false) plain T 0.6 answers with a line
that, after str.lstrip(), starts with 'Answer:' (lines = text.split('\\n')). Refuted if < 0.15."""
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


def has_answer_line(text):
    return any(ln.lstrip().startswith("Answer:") for ln in text.split("\n"))


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

finished = [r for r in rows if r["cap_hit"] is False]
if not finished:
    out(None, False, None, "no finished (cap_hit false) rows", None)

counted = [r for r in finished if has_answer_line(r["text"])]
measured = len(counted) / len(finished)

# alt reading: 'states the result on an Answer: line' = the stored grader-v1 extraction mode
# is 'answer_line' (the answer was actually taken from such a line)
alt = None
if all("mode" in r for r in finished):
    alt = sum(1 for r in finished if r["mode"] == "answer_line") / len(finished)

example = counted[0] if counted else finished[0]
out(measured, measured < 0.15, alt, None, example)
