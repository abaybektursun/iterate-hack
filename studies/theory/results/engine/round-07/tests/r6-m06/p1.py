"""r6-m06 p1: pooled rate of sampled p < 0.01 tokens, RL plain (86ef) over base cue (e72c), on hard328 problems
both models finished (cap_hit false in both)."""
import json
import os
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable

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
    """Smallest attempt per problem_index; first in file order if there is no attempt field."""
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
    common = sorted(set(base) & set(rl))
    finished = [p for p in common if base[p].get("cap_hit") is False and rl[p].get("cap_hit") is False]
    pairs = [(base[p], rl[p]) for p in finished if usable(base[p]) and usable(rl[p])]
    if not pairs:
        not_computable("no problem left after the filters")
        return

    def stat(sample):
        tb = sum(b[FIELD] for b, _ in sample); gb = sum(b["n_generated"] for b, _ in sample)
        tr = sum(r[FIELD] for _, r in sample); gr = sum(r["n_generated"] for _, r in sample)
        if tb == 0 or gb == 0 or gr == 0:
            return float("nan")
        return (tr / gr) / (tb / gb)

    def stat_mean(sample):  # alt reading: mean of per-row rates, ratio of means
        rb = sum(b[FIELD] / b["n_generated"] for b, _ in sample) / len(sample)
        rr = sum(r[FIELD] / r["n_generated"] for _, r in sample) / len(sample)
        return float("nan") if rb == 0 else rr / rb

    m = stat(pairs)
    b0, r0 = pairs[0]
    ex = {k: v for k, v in r0.items() if k not in ("text", "prompt")}
    report(m, len(pairs), bootstrap(stat, pairs), "bootstrap", refuted_by_met=(m < 0.80 or m > 1.50),
           alt_measured=stat_mean(pairs), example_row=ex)


main()
