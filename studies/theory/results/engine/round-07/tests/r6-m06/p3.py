"""r6-m06 p3: on hard328 problems the base cue (e72c) finished wrong and RL plain (86ef) finished, mean log tail-rate
change (RL - base) on RL-fixed problems minus that on unfixed problems."""
import json
import math
import os
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

BUCKET = "s3://pg-lineage-769063704696/results/rlneurons/r5/day1_hard328-01"
JOBS = {"base": "abaybektursun-1114-151534-e72c", "rl": "abaybektursun-1114-151540-86ef"}
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


def usable(r):
    t, g = r.get(FIELD), r.get("n_generated")
    return t is not None and g is not None and g != 0


def d_of(b, r):
    return math.log((r[FIELD] + 0.5) / r["n_generated"]) - math.log((b[FIELD] + 0.5) / b["n_generated"])


def fixed(pair):
    return pair[1].get("score_v3") == 1


def stat(sample):
    F = [d_of(b, r) for b, r in sample if fixed((b, r))]
    U = [d_of(b, r) for b, r in sample if not fixed((b, r))]
    if not F or not U:
        return float("nan")
    return sum(F) / len(F) - sum(U) / len(U)


def main():
    try:
        raw = {m: fetch(j) for m, j in JOBS.items()}
    except Exception as e:  # noqa: BLE001
        not_computable(f"row file not readable: {e}")
        return
    for m, rows in raw.items():
        if not any(FIELD in r for r in rows):
            not_computable(f"field {FIELD} does not exist in any of the {len(rows)} rows of {JOBS[m]} answers.jsonl")
            return
    base, rl = one_per_problem(raw["base"]), one_per_problem(raw["rl"])
    pairs = []
    for p in sorted(set(base) & set(rl)):
        b, r = base[p], rl[p]
        if b.get("cap_hit") is False and b.get("score_v3") != 1 and r.get("cap_hit") is False \
                and usable(b) and usable(r):
            pairs.append((b, r))
    nF = sum(1 for x in pairs if fixed(x))
    nU = len(pairs) - nF
    print(json.dumps({"groups": {"fixed": nF, "unfixed": nU}}))
    if nF == 0 or nU == 0:
        refuted_without_number()
        return
    m = stat(pairs)

    # alt reading: medians instead of means of d
    def med(xs):
        xs = sorted(xs); n = len(xs)
        return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2
    alt = med([d_of(b, r) for b, r in pairs if fixed((b, r))]) - med([d_of(b, r) for b, r in pairs if not fixed((b, r))])
    ex = {k: v for k, v in pairs[0][1].items() if k not in ("text", "prompt")}
    report(m, min(nF, nU), bootstrap(stat, pairs), "bootstrap", refuted_by_met=(m < -0.25 or m > 0.25),
           alt_measured=alt, example_row=ex)


main()
