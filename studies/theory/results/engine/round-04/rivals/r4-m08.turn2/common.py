import json, math, os
import numpy as np

BASE = "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"
RL = "studies/rlneurons/results/day1_3/math500_rl-01/rows.jsonl"


def load(path):
    if not os.path.exists(path):
        subprocess = __import__("subprocess")
        subprocess.run(["git", "checkout", "HEAD", "--", path], check=False)
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def group(rows, mode):
    """mode 'a0': attempt-0 rows per (problem, sample); duplicates kept as lists.
    mode 'last': row with the highest attempt per (problem, sample)."""
    g = {}
    for r in rows:
        key = (r["problem_index"], r["sample"])
        if mode == "a0":
            if r["attempt"] == 0:
                g.setdefault(key, []).append(r)
        else:
            if key not in g or r["attempt"] > g[key][0]["attempt"]:
                g[key] = [r]
    return g


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    if n == 0:
        return None
    if n % 2:
        return float(xs[n // 2])
    return (xs[n // 2 - 1] + xs[n // 2]) / 2.0


def cv(vals):
    a = np.array(vals, dtype=float)
    return float(a.std(ddof=0) / a.mean())


def compute_L(mode):
    """Returns (short_L, long_L, example_row)."""
    gb = group(load(BASE), mode)
    gr = group(load(RL), mode)
    probs = sorted({k[0] for k in gb} | {k[0] for k in gr})
    short_L, long_L, example = [], [], None
    for p in probs:
        ok = True
        vals = {}
        for name, g in (("base", gb), ("rl", gr)):
            vs = []
            for s in (0, 1, 2, 3):
                lst = g.get((p, s))
                # missing row (or ambiguous duplicate attempt-0 rows) excludes the problem
                if not lst or len(lst) != 1:
                    ok = False
                    break
                r = lst[0]
                if not (r["score_v3"] == 1 and r["cap_hit"] is False):
                    ok = False
                    break
                vs.append(r["n_new"])
            if not ok:
                break
            vals[name] = vs
        if not ok:
            continue
        cb, cr = cv(vals["base"]), cv(vals["rl"])
        if cb == 0 or cr == 0:
            continue
        L = math.log(cb / cr)
        if median(vals["base"]) <= 2000:
            short_L.append(L)
            if example is None:
                example = gb[(p, 0)][0]
        else:
            long_L.append(L)
    return short_L, long_L, example
