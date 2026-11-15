"""p1: Mantel-Haenszel rate ratio of right finishes per 1,000 alive tokens, late [12000,16384) vs early [4000,8000),
stratified by problem, cued base on hard328 (attempt 0, first row per (problem_index, sample))."""
import json
import os

from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

PATH = "studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl"
EARLY = (4000, 8000)
LATE = (12000, 16384)


def is_cap(r):
    ch = r.get("cap_hit")
    if ch is None:
        return r.get("finish_reason") == "length"
    return ch is True


def is_right(r):
    return r.get("score_v3") == 1 and not is_cap(r)


def mass(n, w):
    a, b = w
    return max(0, min(n, b) - a) / 1000.0


def event(r, n, w):
    a, b = w
    return 1 if (is_right(r) and a <= n < b) else 0


def strata(rows):
    by_p = {}
    for r in rows:
        n = r["n_new"]
        s = by_p.setdefault(r["problem_index"], [0, 0.0, 0, 0.0])
        s[0] += event(r, n, EARLY)
        s[1] += mass(n, EARLY)
        s[2] += event(r, n, LATE)
        s[3] += mass(n, LATE)
    out = []
    for p in sorted(by_p):
        E, ME, L, ML = by_p[p]
        if ME + ML == 0:
            continue
        out.append((p, E, ME, L, ML))
    return out


def num_den(sample):
    num = den = 0.0
    for (_, E, ME, L, ML) in sample:
        M = ME + ML
        num += L * ME / M
        den += E * ML / M
    return num, den


def stat(sample):
    num, den = num_den(sample)
    if den == 0:
        return float("inf")
    return num / den


def main():
    if not os.path.exists(PATH):
        not_computable(f"{PATH} not readable")
        return
    all_rows = []
    with open(PATH) as fh:
        for line in fh:
            line = line.strip()
            if line:
                all_rows.append(json.loads(line))
    for fld in ("problem_index", "sample", "attempt", "n_new"):
        if not all(fld in r for r in all_rows):
            not_computable(f"field {fld} missing in some rows")
            return

    kept, seen = [], set()
    for r in all_rows:
        if r.get("attempt") != 0:
            continue
        key = (r["problem_index"], r["sample"])
        if key in seen:
            continue
        seen.add(key)
        kept.append(r)

    st = strata(kept)
    if not st:
        refuted_without_number()
        return
    num, den = num_den(st)
    if den == 0:
        refuted_without_number()
        return
    measured = num / den

    # Alternative reading: every row (all attempts, restarts included) treated as its own trajectory, no dedup.
    st_alt = strata(all_rows)
    na, da = num_den(st_alt)
    alt = (na / da) if da else None

    interval = bootstrap(stat, st)
    print(json.dumps({"groups": {"problems_with_mass": len(st)}}))
    report(measured, len(st), interval, "bootstrap", refuted_by_met=False, alt_measured=alt, example_row=kept[0])


main()
