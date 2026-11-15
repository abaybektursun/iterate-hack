"""r6-m10 p3: step 100 accuracy with the cue (D) minus plain (A), grader v3, cap_hit counts 0, empty extraction 0, on
problems present in both files."""
import json
import pathlib
import subprocess

from studies.rlneurons.lib import rln4_lib
from studies.theory.lib.noise import bootstrap, report, not_computable

S3 = "s3://pg-lineage-769063704696/results/rlneurons/"
FILES = {"A": "r3/s0400_s0100-01/out/s0100/P_math500.jsonl", "D": "r3/s0400_s0100-01/out/s0100/F_math500.jsonl"}


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


def score(r):
    if r["cap_hit"]:
        return 0
    g = rln4_lib.grade_v3(r["gold"], r["text"])
    ext = g["extracted_v3"]
    if ext is None or not str(ext).strip():
        return 0
    return int(g["score_v3"])


def main():
    try:
        A, D = kept(fetch(FILES["A"])), kept(fetch(FILES["D"]))
    except Exception as e:
        return not_computable(f"row file not readable: {e!r}")
    for rows in (A, D):
        for r in rows.values():
            for f in ("text", "gold", "cap_hit", "sample"):
                if f not in r:
                    return not_computable(f"field {f} missing")
    sA = {i: score(r) for i, r in A.items()}
    sD = {i: score(r) for i, r in D.items()}
    P = sorted(i for i in A if i in D)
    if not P:
        return not_computable("no problem present in both files")
    problems = [(sD[i], sA[i]) for i in P]

    def stat(sample):
        n = len(sample)
        return sum(d for d, _ in sample) / n - sum(a for _, a in sample) / n

    m = stat(problems)
    # Other reading ("all 500 problems"): each file's mean over all its own kept rows, unpaired (D has 420, A 500).
    alt = sum(sD.values()) / len(sD) - sum(sA.values()) / len(sA)
    ex = {k: v for k, v in D[P[0]].items() if k not in ("text", "prefill_ids", "answer_tokens")}
    ex["text_tail"] = D[P[0]]["text"][-300:]
    ex["score_v3_capped"] = sD[P[0]]
    report(m, len(P), bootstrap(stat, problems), "bootstrap", refuted_by_met=abs(m) > 0.045,
           alt_measured=alt, example_row=ex)


main()
