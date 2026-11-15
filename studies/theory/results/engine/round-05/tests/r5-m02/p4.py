"""r5-m02 prediction 4: RL plain, problems of pool_k_le3 with rl_k in {1,2,3}
(any level), median over problems of the within-problem mean
ln(n_new of finished-wrong / median n_new of right siblings).
refuted_by: statistic <= 0."""
import json
import math
import os
import subprocess

import numpy as np

ROWS = "studies/rlneurons/results/day1_3/math500_rl-01/rows.jsonl"
POOL = "studies/rlneurons/results/anatomy/math500-01/pool_k_le3.json"


def locate(path):
    if os.path.exists(path):
        return path
    dst = os.path.join("runs/theory-tests", path)
    if not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        data = subprocess.run(["git", "show", "HEAD:" + path], capture_output=True, check=True).stdout
        with open(dst, "wb") as f:
            f.write(data)
    return dst


def fail(reason):
    print(json.dumps({"measured": None, "refuted_by_met": False, "alt_measured": None,
                      "not_computable": reason, "example_row": None}))
    raise SystemExit(0)


def group(rows, keep):
    by_prob = {}
    for r in rows:
        if r["attempt"] != 0 or (keep is not None and r["problem_index"] not in keep):
            continue
        if r["cap_hit"]:
            continue
        g = by_prob.setdefault(r["problem_index"], {"right": [], "wrong": []})
        if r["score_v3"] == 1:
            g["right"].append(r)
        elif r["score_v3"] == 0:
            g["wrong"].append(r)
    return by_prob


def problem_values(by_prob):
    values = []
    example = None
    for pi in sorted(by_prob):
        g = by_prob[pi]
        if not g["right"] or not g["wrong"]:
            continue
        m = float(np.median([r["n_new"] for r in g["right"]]))
        values.append(float(np.mean([math.log(r["n_new"] / m) for r in g["wrong"]])))
        if example is None:
            example = g["wrong"][0]
    return values, example


def main():
    try:
        rows = [json.loads(l) for l in open(locate(ROWS)) if l.strip()]
        pool = json.load(open(locate(POOL)))["problems"]
    except Exception as e:  # noqa: BLE001
        fail(f"cannot read input files: {e!r}")

    keep = {p["index"] for p in pool if p["rl_k"] in {1, 2, 3}}
    values, example = problem_values(group(rows, keep))
    if not values:
        fail("no problem passes the filters (needs a right and a finished-wrong attempt-0 row)")
    stat = float(np.median(values))

    # alt: all 500 MATH-500 problems, rl_k recomputed from the RL attempt-0 rows
    # (score_v3 == 1 count of 4, cap hits count as not right), not limited to the
    # base_k <= 3 pool.
    k_all = {}
    for r in rows:
        if r["attempt"] == 0:
            k_all[r["problem_index"]] = k_all.get(r["problem_index"], 0) + (1 if r["score_v3"] == 1 else 0)
    keep_alt = {pi for pi, k in k_all.items() if k in {1, 2, 3}}
    alt_values, _ = problem_values(group(rows, keep_alt))
    alt = float(np.median(alt_values)) if alt_values else None

    print(f"# problems used: {len(values)} (alt: {len(alt_values)})")
    print(json.dumps({"measured": stat, "refuted_by_met": bool(stat <= 0), "alt_measured": alt,
                      "not_computable": None, "example_row": example}))


main()
