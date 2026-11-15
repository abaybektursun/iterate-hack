"""r4-m10 prediction 3: paired cap-hit rate difference, RL step 400 minus base, plain prompt, clean harder 328, T 0.6 / top-p 0.95.

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
    "A": (S3 + "s0400_s0100-01/out/s0400/P_hard.jsonl", os.path.join(DATA, "s0400_P_hard.jsonl")),
    "B": (S3 + "base-01/out/P_hard.jsonl", os.path.join(DATA, "base_P_hard.jsonl")),
}
OVERLAP = os.path.join(ROOT, "studies", "rlneurons", "results", "rln3", "rln3_overlap.json")
HARD = os.path.join(ROOT, "studies", "rlneurons", "data", "rln3", "hard.json")
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


def first_sample0(rows, name, key):
    """sample == 0 only; first row in file order per key (unique_id for the main number, problem_index for alt)."""
    keep = {}
    for r in rows:
        if "sample" not in r or key not in r:
            not_computable(f"file {name} has rows without 'sample' or '{key}'")
        if r["sample"] != 0:
            continue
        if r[key] not in keep:
            keep[r[key]] = r
    return keep


def clean_list():
    """The clean list: rln3_overlap.json sets.hard.flags entries with flag == 'none'. The flags are keyed by the hard set's
    'index' string; studies/rlneurons/data/rln3/hard.json maps that index to the problem's unique_id."""
    if not os.path.exists(OVERLAP):
        not_computable(f"clean list {OVERLAP} not found")
    flags = json.load(open(OVERLAP))["sets"]["hard"]["flags"]
    clean_idx = [k for k, f in flags.items() if f.get("flag") == "none"]
    hard = json.load(open(HARD))
    by_index = {str(h["index"]): h["unique_id"] for h in hard}
    missing = [k for k in clean_idx if k not in by_index]
    if missing:
        not_computable(f"clean-list keys without a unique_id in hard.json: {missing[:5]}")
    return {by_index[k] for k in clean_idx}, {int(k) for k in clean_idx}


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
    clean_uid, clean_pi = clean_list()
    rows_a, rows_b = fetch("A"), fetch("B")
    A = first_sample0(rows_a, "A", "unique_id")
    B = first_sample0(rows_b, "B", "unique_id")
    S = sorted(clean_uid & set(A) & set(B))
    if not S:
        out({"measured": None, "refuted_by_met": True, "alt_measured": None, "not_computable": None, "example_row": None})
    ca = sum(is_cap(A[u], "A") for u in S)
    cb = sum(is_cap(B[u], "B") for u in S)
    measured = ca / len(S) - cb / len(S)
    # alt: match the clean list by problem_index == int(flag key) instead of by unique_id
    A2 = first_sample0(rows_a, "A", "problem_index")
    B2 = first_sample0(rows_b, "B", "problem_index")
    S2 = sorted(clean_pi & set(A2) & set(B2))
    alt = (sum(is_cap(A2[i], "A") for i in S2) - sum(is_cap(B2[i], "B") for i in S2)) / len(S2) if S2 else None
    ex = next((A[u] for u in S if is_cap(A[u], "A")), A[S[0]])
    out({"measured": measured, "refuted_by_met": measured < REFUTE_BELOW, "alt_measured": alt, "not_computable": None,
         "example_row": slim(ex)},
        {"n_clean": len(clean_uid), "n_S": len(S), "cap_A": ca, "cap_B": cb, "n_A": len(A), "n_B": len(B), "n_S_alt": len(S2)})


main()
