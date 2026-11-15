"""p2: paired change in cap-hit rate, RL step 100 minus RL step 400, plain prompt, MATH-500 (T 0.6 / top-p 0.95)."""
import json
import os
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable

A_S3 = "s3://pg-lineage-769063704696/results/rlneurons/r3/s0400_s0100-01/out/s0100/P_math500.jsonl"
A_LOCAL = "runs/theory-tests/r3/s0400_s0100-01_out_s0100_P_math500.jsonl"
B_S3 = "s3://pg-lineage-769063704696/results/rlneurons/r3/s0400_s0100-01/out/s0400/P_math500.jsonl"
B_LOCAL = "runs/theory-tests/r3/s0400_s0100-01_out_s0400_P_math500.jsonl"


def fetch(s3, local):
    if not os.path.exists(local):
        os.makedirs(os.path.dirname(local), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", s3, local, "--profile", "iterate-ecr", "--only-show-errors"], check=True)


def load_kept(path):
    """Rows with sample == 0; first row in file order per problem_index. Returns dict problem_index -> row."""
    kept = {}
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("sample") != 0:
                continue
            pi = r.get("problem_index")
            if pi in kept:
                continue
            kept[pi] = r
    return kept


def cap(r):
    """Main: cap_hit true, or cap_hit missing/null and finish_reason == 'length'."""
    c = r.get("cap_hit")
    if c is True:
        return 1
    if c is None and r.get("finish_reason") == "length":
        return 1
    return 0


def cap_alt(r):
    """Other reading: cap_hit true or finish_reason == 'length' (either flag)."""
    return 1 if (r.get("cap_hit") is True or r.get("finish_reason") == "length") else 0


def slim(r):
    return {k: v for k, v in r.items() if k != "text"}


def main():
    try:
        fetch(A_S3, A_LOCAL)
        fetch(B_S3, B_LOCAL)
    except Exception as e:
        not_computable(f"cannot fetch a row file: {e}")
        return
    a, b = load_kept(A_LOCAL), load_kept(B_LOCAL)
    S = [pi for pi in a if pi in b]  # A's file order
    if not S:
        not_computable("no problem_index present in both files")
        return
    pairs = [(a[pi], b[pi]) for pi in S]

    def stat(sample):
        return sum(cap(x) for x, _ in sample) / len(sample) - sum(cap(y) for _, y in sample) / len(sample)

    def stat_alt(sample):
        return sum(cap_alt(x) for x, _ in sample) / len(sample) - sum(cap_alt(y) for _, y in sample) / len(sample)

    m = stat(pairs)
    report(m, len(pairs), bootstrap(stat, pairs), "bootstrap", refuted_by_met=False,
           alt_measured=stat_alt(pairs), example_row={"A": slim(pairs[0][0]), "B": slim(pairs[0][1])})


if __name__ == "__main__":
    main()
