"""r5-m02 prediction 3: base+cue, Levels 1-3, pooled share of finished-wrong
attempt-0 rows whose n_new is strictly below the n_new of every right sibling.
refuted_by: statistic < 0.35."""
import json
import os
import subprocess

import numpy as np

ROWS = "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"
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


def main():
    try:
        rows = [json.loads(l) for l in open(locate(ROWS)) if l.strip()]
        pool = json.load(open(locate(POOL)))["problems"]
    except Exception as e:  # noqa: BLE001
        fail(f"cannot read input files: {e!r}")

    keep = {p["index"] for p in pool if p["base_k"] in {1, 2, 3} and p["level"] in {1, 2, 3}}

    by_prob = {}
    for r in rows:
        if r["attempt"] != 0 or r["problem_index"] not in keep or r["cap_hit"]:
            continue
        g = by_prob.setdefault(r["problem_index"], {"right": [], "wrong": []})
        if r["score_v3"] == 1:
            g["right"].append(r)
        elif r["score_v3"] == 0:
            g["wrong"].append(r)

    n = 0
    hits = 0
    alt_hits = 0
    example = None
    for pi in sorted(by_prob):
        g = by_prob[pi]
        if not g["right"]:
            continue
        right_n = [r["n_new"] for r in g["right"]]
        med = float(np.median(right_n))
        for r in g["wrong"]:
            n += 1
            if all(r["n_new"] < x for x in right_n):  # tie with any right row: not a hit
                hits += 1
            if r["n_new"] < med:
                alt_hits += 1
            if example is None:
                example = r

    if n == 0:
        fail("no finished-wrong row in a kept problem with a right attempt-0 row")

    stat = hits / n
    alt = alt_hits / n  # alt: strictly below the median of the right siblings
    print(f"# finished-wrong rows: {n}, hits: {hits}")
    print(json.dumps({"measured": stat, "refuted_by_met": bool(stat < 0.35), "alt_measured": alt,
                      "not_computable": None, "example_row": example}))


main()
