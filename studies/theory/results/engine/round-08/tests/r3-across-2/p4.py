"""r3-across-2 prediction 4: RL plain hold-on rate, T 1.0 (T2) / T 0.6 top-p 0.95 (n13 s3gate-03 rl generations).

All rows of both files, no cap filter. Rate = total case-sensitive \\b(Wait|Hmm)\\b matches / total characters of
text x 10,000, pooled. Statistic = rate(T2) / rate(n13 RL). Refuted if the ratio is above 1.2 or below 0.83.
"""
import json
import os
import re
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable

D = "runs/theory-tests/r3-across-2"
FILES = {
    "T2": ("s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t2-01/t2/T2.jsonl", f"{D}/T2.jsonl"),
    "n13": ("s3://pg-lineage-769063704696/results/next_n13/s3gate-03/out/rl/rl/math500/generations.jsonl",
            f"{D}/n13_rl_math500_generations.jsonl"),
}
PAT = re.compile(r"\b(Wait|Hmm)\b")


def load(key):
    uri, path = FILES[key]
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        r = subprocess.run(["aws", "s3", "cp", uri, path, "--profile", "iterate-ecr"], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if r.returncode != 0 and os.path.exists(path):
            os.remove(path)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def pid(r):
    for k in ("problem_index", "idx", "unique_id"):
        if k in r:
            return r[k]
    return None


def main():
    t2 = load("T2")
    if t2 is None:
        return not_computable("T2.jsonl not readable")
    n13 = load("n13")
    if n13 is None:
        return not_computable("s3://pg-lineage-769063704696/results/next_n13/s3gate-03/out/rl/rl/math500/generations.jsonl"
                              " is not readable (403 Forbidden / AccessDenied for the iterate-ecr profile)")
    if not n13:
        return not_computable("n13 RL generations file is empty")
    if any(not isinstance(r.get("text"), str) for r in t2):
        return not_computable("T2 row lacks text")
    if any(not isinstance(r.get("text"), str) for r in n13):
        return not_computable("n13 RL generations rows lack a text field")

    # resampling unit: the problem. T2 keyed by problem_index; n13 by its problem key if present
    n13_keyed = all(pid(r) is not None for r in n13)
    by = {}
    for r in t2:
        by.setdefault(("p", r["problem_index"]), ([], []))[0].append(r)
    if n13_keyed:
        # match on problem_index when both carry it, else on unique_id when both carry it, else separate keys
        if all("problem_index" in r for r in n13):
            for r in n13:
                by.setdefault(("p", r["problem_index"]), ([], []))[1].append(r)
        elif all("unique_id" in r for r in n13):
            uid2pi = {r["unique_id"]: r["problem_index"] for r in t2 if "unique_id" in r}
            for r in n13:
                key = ("p", uid2pi[r["unique_id"]]) if r["unique_id"] in uid2pi else ("u", r["unique_id"])
                by.setdefault(key, ([], []))[1].append(r)
        else:
            for r in n13:
                by.setdefault(("i", pid(r)), ([], []))[1].append(r)
    else:
        for i, r in enumerate(n13):
            by.setdefault(("row", i), ([], []))[1].append(r)
    problems = list(by.values())

    def rate(rows):
        chars = sum(len(r["text"]) for r in rows)
        hits = sum(len(PAT.findall(r["text"])) for r in rows)
        return float("nan") if chars == 0 else hits / chars * 10000

    def stat(sample):
        a = rate([r for p in sample for r in p[0]])
        b = rate([r for p in sample for r in p[1]])
        if a != a or b != b or b == 0:
            return float("nan")
        return a / b

    measured = stat(problems)

    # other reading: one row per problem in n13 (sample 0 / first row) when it holds several samples per problem
    alt = None
    if any(len(p[1]) > 1 for p in problems):
        def first(rows):
            s0 = [r for r in rows if r.get("sample", 0) == 0]
            return (s0 or rows)[:1]
        alt = stat([(p[0], first(p[1])) for p in problems])

    n13_problems = sum(1 for p in problems if p[1])
    print(json.dumps({"groups": {"T2 rows": len(t2), "n13 RL rows": len(n13), "n13 RL problems": n13_problems}}))
    ex = dict(n13[0])
    ex["text"] = ex["text"][:300]
    report(measured, min(len(t2), n13_problems), bootstrap(stat, problems), "bootstrap",
           refuted_by_met=(measured == measured and (measured > 1.2 or measured < 0.83)), alt_measured=alt,
           example_row={k: v for k, v in ex.items() if not isinstance(v, list) or len(v) < 20})


if __name__ == "__main__":
    main()
