"""p1: cap-hit rate of RL step 400, plain prompt, MATH-500 (T 0.6 / top-p 0.95)."""
import json
import os
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable

S3 = "s3://pg-lineage-769063704696/results/rlneurons/r3/s0400_s0100-01/out/s0400/P_math500.jsonl"
LOCAL = "runs/theory-tests/r3/s0400_s0100-01_out_s0400_P_math500.jsonl"


def fetch(s3, local):
    if not os.path.exists(local):
        os.makedirs(os.path.dirname(local), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", s3, local, "--profile", "iterate-ecr", "--only-show-errors"], check=True)


def load_kept(path):
    """Rows with sample == 0; first row in file order per problem_index."""
    kept, seen = [], set()
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("sample") != 0:
                continue
            pi = r.get("problem_index")
            if pi in seen:
                continue
            seen.add(pi)
            kept.append(r)
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
        fetch(S3, LOCAL)
    except Exception as e:
        not_computable(f"cannot fetch {S3}: {e}")
        return
    rows = load_kept(LOCAL)
    if not rows:
        not_computable("no rows with sample == 0 in the file")
        return

    def stat(sample):
        return sum(cap(r) for r in sample) / len(sample)

    def stat_alt(sample):
        return sum(cap_alt(r) for r in sample) / len(sample)

    m = stat(rows)
    report(m, len(rows), bootstrap(stat, rows), "bootstrap", refuted_by_met=False,
           alt_measured=stat_alt(rows), example_row=slim(rows[0]))


if __name__ == "__main__":
    main()
