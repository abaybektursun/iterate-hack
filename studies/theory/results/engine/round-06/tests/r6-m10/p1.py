"""r6-m10 p1: paired finished-answer error rate, step 100 plain (A) minus base cue (B), grader v3, on S = problems
with a kept row in both files and cap_hit false in both."""
import json
import pathlib
import subprocess

from studies.rlneurons.lib import rln4_lib
from studies.theory.lib.noise import bootstrap, report, not_computable

S3 = "s3://pg-lineage-769063704696/results/rlneurons/"
FILES = {"A": "r3/s0400_s0100-01/out/s0100/P_math500.jsonl", "B": "r3/base-01/out/F_math500.jsonl"}


def fetch(key):
    p = pathlib.Path("runs/theory-tests") / key
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["aws", "s3", "cp", S3 + key, str(p), "--profile", "iterate-ecr", "--only-show-errors"], check=True)
    return p


def kept(p):
    """Per problem_index the row with the smallest sample; first in file order on ties."""
    out = {}
    for line in open(p):
        if not line.strip():
            continue
        r = json.loads(line)
        i = r["problem_index"]
        if i not in out or r["sample"] < out[i]["sample"]:
            out[i] = r
    return out


def v3(r):
    g = rln4_lib.grade_v3(r["gold"], r["text"])
    ext = g["extracted_v3"]
    if ext is None or not str(ext).strip():
        return 0
    return int(g["score_v3"])


def main():
    try:
        A, B = kept(fetch(FILES["A"])), kept(fetch(FILES["B"]))
    except Exception as e:  # file not readable
        return not_computable(f"row file not readable: {e!r}")
    for rows in (A, B):
        for r in rows.values():
            for f in ("text", "gold", "cap_hit", "sample"):
                if f not in r:
                    return not_computable(f"field {f} missing")
    sA = {i: v3(r) for i, r in A.items()}
    sB = {i: v3(r) for i, r in B.items()}
    S = sorted(i for i in A if i in B and not A[i]["cap_hit"] and not B[i]["cap_hit"])
    if not S:
        return not_computable("paired set S is empty")
    problems = [(sA[i], sB[i]) for i in S]

    def stat(sample):
        n = len(sample)
        return sum(1 for a, _ in sample if a == 0) / n - sum(1 for _, b in sample if b == 0) / n

    m = stat(problems)
    # Other reading: each file's own finished-answer error rate (all its kept cap_hit-false rows), unpaired.
    fa = [sA[i] for i in A if not A[i]["cap_hit"]]
    fb = [sB[i] for i in B if not B[i]["cap_hit"]]
    alt = sum(1 for x in fa if x == 0) / len(fa) - sum(1 for x in fb if x == 0) / len(fb)
    ex = {k: v for k, v in A[S[0]].items() if k not in ("text", "prefill_ids", "answer_tokens")}
    ex["text_tail"] = A[S[0]]["text"][-300:]
    ex["score_v3"] = sA[S[0]]
    report(m, len(S), bootstrap(stat, problems), "bootstrap", refuted_by_met=(m < -0.03 or m > 0.04),
           alt_measured=alt, example_row=ex)


main()
