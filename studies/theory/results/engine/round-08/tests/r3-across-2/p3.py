"""r3-across-2 prediction 3: cued base hold-on rate, T 1.0 (T1) / T 0.6 top-p 0.95 (F_math500 sample 0), cap_hit false only.

Rate = total case-sensitive \\b(Wait|Hmm)\\b matches / total characters of text x 10,000, pooled over kept rows.
Statistic = rate(T1) / rate(F sample 0). Refuted if the ratio is below 1.08.
"""
import json
import os
import re
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable

D = "runs/theory-tests/r3-across-2"
FILES = {
    "T1": ("s3://pg-lineage-769063704696/results/rlneurons/r4/base_rl-02/out/T1.jsonl", f"{D}/T1.jsonl"),
    "F": ("s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/F_math500.jsonl", f"{D}/F_math500.jsonl"),
}
PAT = re.compile(r"\b(Wait|Hmm)\b")


def load(key):
    uri, path = FILES[key]
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", uri, path, "--profile", "iterate-ecr"], check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    t1, fm = load("T1"), load("F")
    if t1 is None or fm is None:
        return not_computable("row file not readable: " + ("T1.jsonl" if t1 is None else "F_math500.jsonl"))
    for rows, name in ((t1, "T1"), (fm, "F_math500")):
        for r in rows:
            if "text" not in r or "cap_hit" not in r or "problem_index" not in r:
                return not_computable(f"{name} row lacks text, cap_hit or problem_index")
    if any("sample" not in r for r in fm):
        return not_computable("F_math500 row lacks sample")
    fm = [r for r in fm if r["sample"] == 0]

    def kept(rows):
        return [r for r in rows if r["cap_hit"] is False]

    t1k, fmk = kept(t1), kept(fm)

    # one entry per problem: (list of kept T1 rows, list of kept F rows); problems from the union of both files
    by = {}
    for r in t1k:
        by.setdefault(r["problem_index"], ([], []))[0].append(r)
    for r in fmk:
        by.setdefault(r["problem_index"], ([], []))[1].append(r)
    # include problems whose rows were all dropped (cap hits) so the resampling unit is the problem set
    for r in t1 + fm:
        by.setdefault(r["problem_index"], ([], []))
    problems = [by[k] for k in sorted(by)]

    def rate(rows):
        chars = sum(len(r["text"]) for r in rows)
        hits = sum(len(PAT.findall(r["text"])) for r in rows)
        return float("nan") if chars == 0 else hits / chars * 10000

    def stat(sample):
        a = rate([r for p in sample for r in p[0]])
        b = rate([r for p in sample for r in p[1]])
        if b != b or a != a or b == 0:
            return float("nan")
        return a / b

    measured = stat(problems)

    # other reading: only problems finished (cap_hit false) in both files
    both = [p for p in problems if p[0] and p[1]]
    alt = stat(both) if both else None

    print(json.dumps({"groups": {"T1 kept (cap_hit false)": len(t1k), "F_math500 sample 0 kept (cap_hit false)": len(fmk)}}))
    ex = dict(fmk[0])
    ex["text"] = ex["text"][:300]
    for k in ("prefill_ids",):
        ex.pop(k, None)
    report(measured, min(len(t1k), len(fmk)), bootstrap(stat, problems), "bootstrap",
           refuted_by_met=(measured == measured and measured < 1.08), alt_measured=alt, example_row=ex)


if __name__ == "__main__":
    main()
