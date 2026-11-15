"""r4-m02 prediction 1: pooled within-problem concordance of length with wrongness, cued base.

Recipe: studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl; keep attempt == 0 and
cap_hit == false; drop null/missing score_v3; group by problem_index; every pair (i right, j wrong);
pair value 1 if n_new_j > n_new_i, 0.5 if equal, 0 otherwise; statistic = sum / number of pairs.
refuted_by: computed fraction below 0.60.
alt_measured: ties counted as 0 (strict "wrong sample has more new tokens", as in the experiment text).
"""
import json
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

    total = 0.0
    total_strict = 0.0
    npairs = 0
    example = None
    for pi, rows in groups.items():
        right = [r for r in rows if r["score_v3"] == 1]
        wrong = [r for r in rows if r["score_v3"] == 0]
        for i in right:
            for j in wrong:
                npairs += 1
                if j["n_new"] > i["n_new"]:
                    total += 1.0
                    total_strict += 1.0
                elif j["n_new"] == i["n_new"]:
                    total += 0.5
                if example is None:
                    example = j
    if npairs == 0:
        nc("no (right, wrong) pairs among finished attempt-0 rows")
    measured = total / npairs
    alt = total_strict / npairs
    print("pairs=%d problems_with_pairs=%d" % (
        npairs, sum(1 for rows in groups.values()
                    if any(r["score_v3"] == 1 for r in rows) and any(r["score_v3"] == 0 for r in rows))),
          file=sys.stderr)
    out({"measured": measured, "refuted_by_met": measured < 0.60, "alt_measured": alt,
         "not_computable": None, "example_row": example})


if __name__ == "__main__":
    main()
