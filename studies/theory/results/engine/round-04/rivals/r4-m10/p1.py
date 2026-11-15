"""p1: share of RL step-100 plain MATH-500 answers with 'Okay' in the first 30 characters."""
import json
import os
import subprocess

S3 = "s3://pg-lineage-769063704696/results/rlneurons/r3/s0400_s0100-01/out/s0100/P_math500.jsonl"
LOCAL = "runs/theory-tests/s0100_P_math500.jsonl"


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
    order = []
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
            order.append(pi)
    return [kept[p] for p in order]


def main():
    err = fetch(S3, LOCAL)
    if err:
        return nc(err)
    rows = load_kept(LOCAL)
    if not rows:
        return nc("no rows with sample == 0")
    n = len(rows)
    match = 0
    alt_match = 0
    example = None
    for r in rows:
        t = r.get("text")
        if not isinstance(t, str) or t == "":
            continue
        # literal: 'Okay' wholly inside text[:30]
        if "Okay" in t[:30]:
            match += 1
            if example is None:
                example = r
        # alt: 'Okay' starts at a character index < 30 (may extend past char 30)
        idx = t.find("Okay")
        if 0 <= idx < 30:
            alt_match += 1
    if example is None:
        example = rows[0]
    measured = match / n
    alt = alt_match / n
    ex = {k: v for k, v in example.items() if k not in ("prefill_ids", "answer_tokens")}
    if isinstance(ex.get("text"), str):
        ex["text"] = ex["text"][:200]
    out({"measured": measured, "refuted_by_met": False, "alt_measured": alt,
         "not_computable": None, "example_row": ex})


main()
