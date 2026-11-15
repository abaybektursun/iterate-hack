"""r6-m06 p1: paired tail-rate ratio on hard328, RL plain (86ef) over base cue (e72c), pooled
sum n_tok_p_lt_1e2 / sum n_generated over problems both models finished (cap_hit false in both)."""
import json
import os
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable

BUCKET = "s3://pg-lineage-769063704696/results/rlneurons/r5/day1_hard328-01"
BASE_JOB = "abaybektursun-1114-151534-e72c"
RL_JOB = "abaybektursun-1114-151540-86ef"
TAIL = "n_tok_p_lt_1e2"


def fetch(job):
    path = os.path.join("runs", "theory-tests", job, "answers.jsonl")
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", f"{BUCKET}/{job}/answers.jsonl", path, "--profile", "iterate-ecr",
                        "--only-show-errors"], check=True)
    return path


def load(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def one_per_problem(rows):
    """Smallest attempt per problem_index (first in file order among equal attempts); first in file order if
    the file has no attempt field."""
    has_attempt = any("attempt" in r for r in rows)
    kept = {}
    for r in rows:
        p = r["problem_index"]
        if p not in kept:
            kept[p] = r
        elif has_attempt:
            a_new, a_old = r.get("attempt"), kept[p].get("attempt")
            if a_new is not None and (a_old is None or a_new < a_old):
                kept[p] = r
    return kept


def usable(r):
    return r.get(TAIL) is not None and r.get("n_generated") is not None and r["n_generated"] != 0


def slim(r):
    return {k: v for k, v in r.items() if k not in ("text", "prompt")}


def main():
    try:
        base_rows, rl_rows = load(fetch(BASE_JOB)), load(fetch(RL_JOB))
    except Exception as e:  # noqa: BLE001
        not_computable(f"row file not readable: {e!r}")
        return
    for name, rows in (("e72c", base_rows), ("86ef", rl_rows)):
        if not any(TAIL in r for r in rows):
            not_computable(f"field {TAIL} does not exist in any of the {len(rows)} rows of {name} answers.jsonl "
                           f"(the day1_hard328-01 jobs predate the min-p change that added it)")
            return
        if not any("n_generated" in r for r in rows):
            not_computable(f"field n_generated does not exist in {name} answers.jsonl")
            return
    base, rl = one_per_problem(base_rows), one_per_problem(rl_rows)
    pairs = []
    for p in sorted(set(base) & set(rl)):
        b, r = base[p], rl[p]
        if b.get("cap_hit") is not False or r.get("cap_hit") is not False:
            continue
        if not (usable(b) and usable(r)):
            continue
        pairs.append((b, r))
    if not pairs:
        not_computable("no problem left after the filters; the pooled rates are 0/0")
        return

    def ratio(sample, denom="n_generated"):
        rb = sum(b[TAIL] for b, _ in sample) / sum(b[denom] for b, _ in sample)
        rr = sum(r[TAIL] for _, r in sample) / sum(r[denom] for _, r in sample)
        return rr / rb if rb > 0 else float("inf")

    measured = ratio(pairs)
    alt = None
    if all(b.get("n_new") and r.get("n_new") for b, r in pairs):
        alt = ratio(pairs, "n_new")
    report(measured, len(pairs), bootstrap(ratio, pairs), "bootstrap",
           refuted_by_met=(measured < 0.80 or measured > 1.50), alt_measured=alt,
           example_row={"base_e72c": slim(pairs[0][0]), "rl_86ef": slim(pairs[0][1])})


main()
