"""k=2: median over paired finished problems of ln(max(n_new_A,1)/max(n_new_B,1)), A = RL step 100 plain, B = base cue."""
import json
import math
import pathlib
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable

ROOT = pathlib.Path.cwd()
BUCKET = "s3://pg-lineage-769063704696/results/"
KEYS = {"A": "rlneurons/r3/s0400_s0100-01/out/s0100/P_math500.jsonl",
        "B": "rlneurons/r3/base-01/out/F_math500.jsonl"}


def fetch(key):
    p = ROOT / "runs/theory-tests" / key.replace("rlneurons/", "", 1)
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["aws", "s3", "cp", BUCKET + key, str(p), "--profile", "iterate-ecr", "--quiet"], check=True)
    return p


def kept(path):
    """per problem_index, the row with the smallest sample; first in file order on ties."""
    out = {}
    for line in open(path):
        if not line.strip():
            continue
        r = json.loads(line)
        i = r["problem_index"]
        if i not in out or r["sample"] < out[i]["sample"]:
            out[i] = r
    return out


def median(xs):
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def lr(a, b):
    return math.log(max(a["n_new"], 1) / max(b["n_new"], 1))


def stat(pairs):
    return median([lr(a, b) for a, b in pairs])


def main():
    try:
        A, B = kept(fetch(KEYS["A"])), kept(fetch(KEYS["B"]))
    except Exception as e:  # file not readable
        not_computable(f"row file not readable: {e}")
        return
    for rows in (A, B):
        for r in rows.values():
            for f in ("n_new", "cap_hit", "sample", "problem_index"):
                if f not in r:
                    not_computable(f"field {f} missing")
                    return
    common = sorted(set(A) & set(B))
    S = [i for i in common if A[i]["cap_hit"] is False and B[i]["cap_hit"] is False]
    if not S:
        not_computable("paired set S is empty")
        return
    pairs = [(A[i], B[i]) for i in S]
    measured = stat(pairs)
    # alt reading: "finished" = finish_reason == "stop" in both files (instead of cap_hit false)
    S2 = [i for i in common if A[i].get("finish_reason") == "stop" and B[i].get("finish_reason") == "stop"]
    alt = stat([(A[i], B[i]) for i in S2]) if S2 else None
    ex = {k: v for k, v in A[S[0]].items() if k not in ("text", "prefill_ids", "answer_tokens")}
    report(measured, len(pairs), bootstrap(stat, pairs), "bootstrap", refuted_by_met=False, alt_measured=alt,
           example_row=ex)


main()
