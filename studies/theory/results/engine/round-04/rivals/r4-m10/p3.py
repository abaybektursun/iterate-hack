"""p3: ratio of median n_new of finished answers, RL step 100 over base, plain MATH-500."""
import json
import os
import subprocess

A_S3 = "s3://pg-lineage-769063704696/results/rlneurons/r3/s0400_s0100-01/out/s0100/P_math500.jsonl"
A_LOCAL = "runs/theory-tests/s0100_P_math500.jsonl"
B_S3 = "s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/P_math500.jsonl"
B_LOCAL = "runs/theory-tests/base01_P_math500.jsonl"


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


def finished(r):
    c = r.get("cap_hit")
    if c is None:
        return r.get("finish_reason") == "stop"
    return c is False


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    if n == 0:
        return None
    if n % 2 == 1:
        return float(xs[n // 2])
    return (xs[n // 2 - 1] + xs[n // 2]) / 2.0


def lengths(rows, S, nonempty=False):
    out_ = []
    for p in S:
        r = rows[p]
        if not finished(r):
            continue
        v = r.get("n_new")
        if v is None:
            continue
        if nonempty and (not isinstance(r.get("text"), str) or r.get("text") == "" or v == 0):
            continue
        out_.append(v)
    return out_


def main():
    for s3, local in ((A_S3, A_LOCAL), (B_S3, B_LOCAL)):
        err = fetch(s3, local)
        if err:
            return nc(err)
    A = load_kept(A_LOCAL)
    B = load_kept(B_LOCAL)
    S = [p for p in A if p in B]
    if not S:
        return nc("set S (problems in both files) is empty")
    la, lb = lengths(A, S), lengths(B, S)
    ma, mb = median(la), median(lb)
    if ma is None or mb is None:
        return nc("a file has no finished rows with n_new in S")
    if mb == 0:
        return nc("base median length is 0; ratio undefined")
    measured = ma / mb
    # alt: drop empty answers (text empty or n_new == 0), which the stored files hold as 'stop' rows
    la2, lb2 = lengths(A, S, True), lengths(B, S, True)
    ma2, mb2 = median(la2), median(lb2)
    alt = (ma2 / mb2) if (ma2 is not None and mb2) else None
    ex_p = next((p for p in S if finished(A[p]) and A[p].get("n_new") is not None), S[0])
    ex = {k: v for k, v in A[ex_p].items() if k not in ("prefill_ids", "answer_tokens")}
    if isinstance(ex.get("text"), str):
        ex["text"] = ex["text"][:200]
    out({"measured": measured, "refuted_by_met": False, "alt_measured": alt,
         "not_computable": None, "example_row": ex})


main()
