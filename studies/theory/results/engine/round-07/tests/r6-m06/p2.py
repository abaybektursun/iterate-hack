"""r6-m06 p2: base cue (e72c) hard328, wrong/right pooled p < 0.01 token rate, wrong-count-weighted over
n_generated quartiles."""
import json
import os
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable

BUCKET = "s3://pg-lineage-769063704696/results/rlneurons/r5/day1_hard328-01"
JOB = "abaybektursun-1114-151534-e72c"
FIELD = "n_tok_p_lt_1e2"


def fetch(job):
    local = f"runs/theory-tests/r5/day1_hard328-01/{job}/answers.jsonl"
    if not os.path.exists(local):
        os.makedirs(os.path.dirname(local), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", f"{BUCKET}/{job}/answers.jsonl", local, "--profile", "iterate-ecr"],
                       check=True, stdout=subprocess.DEVNULL)
    with open(local) as f:
        return [json.loads(line) for line in f if line.strip()]


def one_per_problem(rows):
    kept = {}
    for i, r in enumerate(rows):
        p = r.get("problem_index")
        if p is None:
            continue
        a = r.get("attempt")
        key = (a if a is not None else float("inf"), i)
        if p not in kept or key < kept[p][0]:
            kept[p] = (key, r)
    return {p: v[1] for p, v in kept.items()}


def is_right(r):
    return r.get("score_v3") == 1


def stat_with(sample, weight_by_wrong=True):
    rows = sorted(sample, key=lambda r: (r["n_generated"], r["problem_index"]))
    N = len(rows)
    if N == 0:
        return float("nan")
    quart = [[] for _ in range(4)]
    for rank, r in enumerate(rows):
        quart[(4 * rank) // N].append(r)
    num = den = 0.0
    for q in quart:
        W = [r for r in q if not is_right(r)]
        R = [r for r in q if is_right(r)]
        if not W or not R:
            continue
        rR = sum(r[FIELD] for r in R) / sum(r["n_generated"] for r in R)
        if rR == 0:
            continue
        rW = sum(r[FIELD] for r in W) / sum(r["n_generated"] for r in W)
        w = len(W) if weight_by_wrong else 1
        num += w * rW / rR
        den += w
    return num / den if den else float("nan")


def main():
    try:
        raw = fetch(JOB)
    except Exception as e:  # noqa: BLE001
        not_computable(f"row file not readable: {e}")
        return
    if not any(FIELD in r for r in raw):
        not_computable(f"field {FIELD} does not exist in any of the {len(raw)} rows of {JOB} answers.jsonl")
        return
    kept = [r for r in one_per_problem(raw).values()
            if r.get("cap_hit") is False and r.get(FIELD) is not None
            and r.get("n_generated") is not None and r["n_generated"] > 0]
    if not kept:
        not_computable("no row left after the filters")
        return
    wrong = [r for r in kept if not is_right(r)]
    right = [r for r in kept if is_right(r)]
    print(json.dumps({"groups": {"wrong": len(wrong), "right": len(right)}}))

    def stat(sample):
        return stat_with(sample, True)

    m = stat(kept)
    # alt reading: ignore the length matching, a single pooled wrong/right ratio over all kept rows
    alt = float("nan")
    if wrong and right:
        rR = sum(r[FIELD] for r in right) / sum(r["n_generated"] for r in right)
        rW = sum(r[FIELD] for r in wrong) / sum(r["n_generated"] for r in wrong)
        alt = rW / rR if rR else float("nan")
    ex = {k: v for k, v in kept[0].items() if k not in ("text", "prompt")}
    report(m, min(len(wrong), len(right)), bootstrap(stat, kept), "bootstrap", refuted_by_met=(m > 1.40),
           alt_measured=alt, example_row=ex)


main()
