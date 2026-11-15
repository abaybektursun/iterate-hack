"""r5-m02 prediction 1: base+cue, Levels 1-3, median over problems of the
within-problem mean ln(n_new of finished-wrong / median n_new of right siblings).
refuted_by: statistic >= 0."""
import json
import math
import os
import subprocess

import numpy as np

ROWS = "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"
POOL = "studies/rlneurons/results/anatomy/math500-01/pool_k_le3.json"
K_FIELD = "base_k"
LEVELS = {1, 2, 3}


def locate(path):
    """Use the committed file; if missing, fetch it from git into runs/theory-tests/."""
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

    keep = {p["index"] for p in pool if p[K_FIELD] in {1, 2, 3} and p["level"] in LEVELS}

    by_prob = {}
    for r in rows:
        if r["attempt"] != 0 or r["problem_index"] not in keep:
            continue
        if r["cap_hit"]:
            continue  # cap-hit rows dropped entirely
        if r["score_v3"] == 1:
            by_prob.setdefault(r["problem_index"], {"right": [], "wrong": []})["right"].append(r)
        elif r["score_v3"] == 0:
            by_prob.setdefault(r["problem_index"], {"right": [], "wrong": []})["wrong"].append(r)

    values = []
    pooled_ri = []
    example = None
    for pi in sorted(by_prob):
        g = by_prob[pi]
        if not g["right"] or not g["wrong"]:
            continue
        m = float(np.median([r["n_new"] for r in g["right"]]))
        ri = [math.log(r["n_new"] / m) for r in g["wrong"]]
        values.append(float(np.mean(ri)))
        pooled_ri.extend(ri)
        if example is None:
            example = g["wrong"][0]

    if not values:
        fail("no problem passes the filters (needs a right and a finished-wrong attempt-0 row)")

    stat = float(np.median(values))  # even count: mean of two middle values
    alt = float(np.median(pooled_ri))  # alt: median over pooled finished-wrong rows
    print(f"# problems used: {len(values)}, finished-wrong rows: {len(pooled_ri)}")
    print(json.dumps({"measured": stat, "refuted_by_met": bool(stat >= 0), "alt_measured": alt,
                      "not_computable": None, "example_row": example}))


main()
