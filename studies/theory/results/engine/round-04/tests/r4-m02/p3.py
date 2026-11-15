"""r4-m02 prediction 3: mean within-problem Spearman correlation of n_new with score_v3, cued base.

Recipe: studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl; keep attempt == 0 and
cap_hit == false; drop null/missing score_v3; group by problem_index; keep problems with at least one
score_v3 == 1 and one score_v3 == 0 (among kept rows); per problem Spearman(n_new, score_v3) with
average ranks for ties; skip a problem if all its n_new are equal; statistic = unweighted mean.
refuted_by: computed mean above -0.19.
alt_measured: the same per-problem correlations averaged with weights = number of kept rows in the problem.
"""
import json
import math
import os
import subprocess
import sys
from collections import defaultdict

REL = "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"
CACHE = "runs/theory-tests/day1_3_math500_base_cue-01_rows.jsonl"


def out(d):
    print(json.dumps(d))
    sys.exit(0)


def nc(reason):
    out({"measured": None, "refuted_by_met": False, "alt_measured": None,
         "not_computable": reason, "example_row": None})


def path():
    if os.path.exists(REL):
        return REL
    if os.path.exists(CACHE):
        return CACHE
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    try:
        data = subprocess.run(["git", "show", "HEAD:" + REL], check=True,
                              capture_output=True).stdout
    except Exception as e:  # noqa
        nc("file not readable: %s (%s)" % (REL, e))
    with open(CACHE, "wb") as f:
        f.write(data)
    return CACHE


def avg_ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        r = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = r
        i = j + 1
    return ranks


def pearson(a, b):
    n = len(a)
    ma = sum(a) / n
    mb = sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va == 0 or vb == 0:
        return None
    return cov / math.sqrt(va * vb)


def main():
    groups = defaultdict(list)
    with open(path()) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            for k in ("attempt", "cap_hit", "problem_index", "n_new"):
                if k not in r:
                    nc("field %s missing in rows" % k)
            if r["attempt"] != 0:
                continue
            if r["cap_hit"] is not False:
                continue
            if r.get("score_v3") is None:
                continue
            groups[r["problem_index"]].append(r)

    rhos = []
    weights = []
    example = None
    n_mixed = 0
    n_skipped = 0
    for pi in sorted(groups):
        rows = groups[pi]
        if not (any(r["score_v3"] == 1 for r in rows) and any(r["score_v3"] == 0 for r in rows)):
            continue
        n_mixed += 1
        ns = [r["n_new"] for r in rows]
        if len(set(ns)) == 1:
            n_skipped += 1
            continue
        sc = [float(r["score_v3"]) for r in rows]
        rho = pearson(avg_ranks(ns), avg_ranks(sc))
        if rho is None:
            n_skipped += 1
            continue
        rhos.append(rho)
        weights.append(len(rows))
        if example is None:
            example = rows[0]
    print("mixed_problems=%d used=%d skipped=%d" % (n_mixed, len(rhos), n_skipped), file=sys.stderr)
    if not rhos:
        nc("no problem with both a right and a wrong finished attempt-0 row and unequal n_new")
    measured = sum(rhos) / len(rhos)
    alt = sum(w * r for w, r in zip(weights, rhos)) / sum(weights)
    out({"measured": measured, "refuted_by_met": measured > -0.19, "alt_measured": alt,
         "not_computable": None, "example_row": example})


if __name__ == "__main__":
    main()
