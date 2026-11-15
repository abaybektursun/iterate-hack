"""r6-m10 p2: median over S of ln(max(n_new_A,1)/max(n_new_B,1)); A = step 100 plain, B = base cue; S = problems with a
kept row in both files and cap_hit false in both. No grading."""
import json
import math
import pathlib
import subprocess

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
    out = {}
    for line in open(p):
        if not line.strip():
            continue
        r = json.loads(line)
        i = r["problem_index"]
        if i not in out or r["sample"] < out[i]["sample"]:
            out[i] = r
    return out


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def main():
    try:
        A, B = kept(fetch(FILES["A"])), kept(fetch(FILES["B"]))
    except Exception as e:
        return not_computable(f"row file not readable: {e!r}")
    for rows in (A, B):
        for r in rows.values():
            for f in ("n_new", "cap_hit", "sample"):
                if f not in r:
                    return not_computable(f"field {f} missing")
    S = sorted(i for i in A if i in B and not A[i]["cap_hit"] and not B[i]["cap_hit"])
    if not S:
        return not_computable("paired set S is empty")
    problems = [(A[i]["n_new"], B[i]["n_new"]) for i in S]

    def stat(sample):
        return median([math.log(max(a, 1) / max(b, 1)) for a, b in sample])

    m = stat(problems)
    # Other reading: length as n_generated (n_new plus the stop token, as stored) instead of n_new.
    alt = None
    if all("n_generated" in A[i] and "n_generated" in B[i] for i in S):
        alt = median([math.log(max(A[i]["n_generated"], 1) / max(B[i]["n_generated"], 1)) for i in S])
    ex = {k: v for k, v in A[S[0]].items() if k not in ("text", "prefill_ids", "answer_tokens")}
    report(m, len(S), bootstrap(stat, problems), "bootstrap", refuted_by_met=(m > 0.35 or m < -0.25),
           alt_measured=alt, example_row=ex)


main()
