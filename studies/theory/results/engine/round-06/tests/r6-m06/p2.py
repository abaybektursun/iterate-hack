"""r6-m06 p2: base cue (e72c) on hard328, wrong/right pooled tail rate within n_generated quartiles,
weighted by the number of wrong rows per quartile."""
import json
import os
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable

BUCKET = "s3://pg-lineage-769063704696/results/rlneurons/r5/day1_hard328-01"
BASE_JOB = "abaybektursun-1114-151534-e72c"
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


def slim(r):
    return {k: v for k, v in r.items() if k not in ("text", "prompt")}


def is_right(r):
    return r.get("score_v3") == 1


def quartile_parts(sample):
    rows = sorted(sample, key=lambda r: (r["n_generated"], r["problem_index"]))
    n = len(rows)
    out = []
    for q in range(4):
        qs = [r for i, r in enumerate(rows) if (4 * i) // n == q]
        w = [r for r in qs if not is_right(r)]
        rt = [r for r in qs if is_right(r)]
        if not w or not rt:
            continue
        rr = sum(r[TAIL] for r in rt) / sum(r["n_generated"] for r in rt)
        if rr == 0:
            continue
        rw = sum(r[TAIL] for r in w) / sum(r["n_generated"] for r in w)
        out.append((len(w), rw / rr))
    return out


def stat(sample):
    parts = quartile_parts(sample)
    if not parts:
        return float("nan")
    return sum(nw * x for nw, x in parts) / sum(nw for nw, _ in parts)


def stat_unweighted(sample):
    parts = quartile_parts(sample)
    if not parts:
        return None
    return sum(x for _, x in parts) / len(parts)


def main():
    try:
        rows = load(fetch(BASE_JOB))
    except Exception as e:  # noqa: BLE001
        not_computable(f"row file not readable: {e!r}")
        return
    if not any(TAIL in r for r in rows):
        not_computable(f"field {TAIL} does not exist in any of the {len(rows)} rows of e72c answers.jsonl "
                       f"(the day1_hard328-01 jobs predate the min-p change that added it)")
        return
    if not any("score_v3" in r for r in rows):
        not_computable("field score_v3 does not exist in e72c answers.jsonl")
        return
    kept = [r for _, r in sorted(one_per_problem(rows).items())
            if r.get("cap_hit") is False and r.get(TAIL) is not None
            and r.get("n_generated") is not None and r["n_generated"] > 0]
    if not kept:
        not_computable("no row left after the filters")
        return
    if not quartile_parts(kept):
        not_computable("every quartile was skipped (no wrong rows, no right rows, or rR == 0); the weighted "
                       "mean is 0/0")
        return
    measured = stat(kept)
    report(measured, len(kept), bootstrap(stat, kept), "bootstrap", refuted_by_met=measured > 1.40,
           alt_measured=stat_unweighted(kept), example_row=slim(kept[0]))


main()
