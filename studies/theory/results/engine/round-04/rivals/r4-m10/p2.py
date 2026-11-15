"""p2: paired cap-hit rate difference at RL step 400, cue (F) minus plain (P), MATH-500."""
import json
import os
import subprocess

BASE = "s3://pg-lineage-769063704696/results/rlneurons/r3/s0400_s0100-01/out/s0400/"
A_S3, A_LOCAL = BASE + "F_math500.jsonl", "runs/theory-tests/s0400_F_math500.jsonl"
B_S3, B_LOCAL = BASE + "P_math500.jsonl", "runs/theory-tests/s0400_P_math500.jsonl"


def out(d):
    print(json.dumps(d))


def nc(reason):
    out({"measured": None, "refuted_by_met": False, "alt_measured": None,
         "not_computable": reason, "example_row": None})


def fetch(s3, local):
    if not os.path.exists(local):
        os.makedirs(os.path.dirname(local), exist_ok=True)
        r = subprocess.run(["aws", "s3", "cp", s3, local, "--profile", "iterate-ecr", "--only-show-errors"],
                           capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(local):
            return f"fetch failed for {s3}: {r.stderr.strip()[:300]}"
    return None


def load_kept(local):
    kept = {}
    with open(local) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("sample") != 0:
                continue
            pi = r.get("problem_index")
            if pi in kept:
                continue
            kept[pi] = r
    return kept


def is_cap(r):
    # cap_hit true, or cap_hit missing (absent or null) and finish_reason == 'length'
    c = r.get("cap_hit")
    if c is None:
        return r.get("finish_reason") == "length"
    return c is True


def is_len(r):
    return r.get("finish_reason") == "length"


def main():
    for s3, local in ((A_S3, A_LOCAL), (B_S3, B_LOCAL)):
        err = fetch(s3, local)
        if err:
            return nc(err)
    A = load_kept(A_LOCAL)
    B = load_kept(B_LOCAL)
    S = [p for p in A if p in B]
    if not S:
        return nc("set S (problems in both A and B) is empty")
    n = len(S)
    ca = sum(1 for p in S if is_cap(A[p]))
    cb = sum(1 for p in S if is_cap(B[p]))
    measured = ca / n - cb / n
    # alt: cap hit defined by finish_reason == 'length' alone
    la = sum(1 for p in S if is_len(A[p]))
    lb = sum(1 for p in S if is_len(B[p]))
    alt = la / n - lb / n
    ex_p = next((p for p in S if is_cap(A[p])), S[0])
    ex = {k: v for k, v in A[ex_p].items() if k not in ("prefill_ids", "answer_tokens")}
    if isinstance(ex.get("text"), str):
        ex["text"] = ex["text"][:200]
    out({"measured": measured, "refuted_by_met": False, "alt_measured": alt,
         "not_computable": None, "example_row": ex})


main()
