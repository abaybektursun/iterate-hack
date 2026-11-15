"""r4-m10 prediction 1: paired cap-hit rate difference, RL step 100 minus base, plain MATH-500, T 0.6 / top-p 0.95.

Run from the repository root: python3 <this script>. Standard library only (aws via subprocess).
"""
import json
import os
import subprocess
import sys

ROOT = os.getcwd()
DATA = os.path.join(ROOT, "runs", "theory-tests", "r4m10")
S3 = "s3://pg-lineage-769063704696/results/rlneurons/r3/"
FILES = {
    "A": (S3 + "s0400_s0100-01/out/s0100/P_math500.jsonl", os.path.join(DATA, "s0100_P_math500.jsonl")),
    "B": (S3 + "base-01/out/P_math500.jsonl", os.path.join(DATA, "base_P_math500.jsonl")),
}
REFUTE_BELOW = 0.0


def out(d, details=None):
    if details:
        print(json.dumps({"details": details}, ensure_ascii=False))
    print(json.dumps(d, ensure_ascii=False))
    sys.exit(0)


def not_computable(reason):
    out({"measured": None, "refuted_by_met": False, "alt_measured": None, "not_computable": reason, "example_row": None})


def fetch(name):
    uri, path = FILES[name]
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        r = subprocess.run(["aws", "s3", "cp", uri, path, "--profile", "iterate-ecr", "--only-show-errors"],
                           capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(path):
            not_computable(f"could not fetch {uri}: {r.stderr.strip()[:300]}")
    rows = []
    with open(path) as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def first_sample0(rows, name):
    """sample == 0 only; first row in file order per problem_index."""
    keep = {}
    for r in rows:
        if "sample" not in r or "problem_index" not in r:
            not_computable(f"file {name} has rows without 'sample' or 'problem_index'")
        if r["sample"] != 0:
            continue
        if r["problem_index"] not in keep:
            keep[r["problem_index"]] = r
    return keep


def is_cap(r, name):
    if "cap_hit" in r and r["cap_hit"] is not None:
        return r["cap_hit"] is True
    if "finish_reason" not in r:
        not_computable(f"file {name}: a row has neither cap_hit nor finish_reason")
    return r["finish_reason"] == "length"


def slim(r):
    d = {k: v for k, v in r.items() if k not in ("text", "prefill_ids")}
    d["text_len"] = len(r.get("text") or "")
    return d


def main():
    A = first_sample0(fetch("A"), "A")
    B = first_sample0(fetch("B"), "B")
    S = sorted(set(A) & set(B))
    if not S:
        out({"measured": None, "refuted_by_met": True, "alt_measured": None, "not_computable": None, "example_row": None})
    ca = sum(is_cap(A[i], "A") for i in S)
    cb = sum(is_cap(B[i], "B") for i in S)
    measured = ca / len(S) - cb / len(S)
    # alt: unpaired reading - each file's cap-hit rate over all its own sample-0 problems (no intersection)
    alt = sum(is_cap(r, "A") for r in A.values()) / len(A) - sum(is_cap(r, "B") for r in B.values()) / len(B)
    ex = next((A[i] for i in S if is_cap(A[i], "A")), A[S[0]])
    out({"measured": measured, "refuted_by_met": measured < REFUTE_BELOW, "alt_measured": alt, "not_computable": None,
         "example_row": slim(ex)},
        {"n_S": len(S), "cap_A": ca, "cap_B": cb, "n_A": len(A), "n_B": len(B)})


main()
