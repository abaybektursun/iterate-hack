"""Spread and rank tests between two arms of one experiment folder (laptop, no model).

    python3 studies/explore/analysis/spread_test.py runs/explore/ahc014/swe2-spread-02 single fnf [out.json]

Reads <arm>-s<seed>/metrics.json (best_val, best_test; a missing or invalid test score counts as 0). Prints and
optionally writes, for arms A and B:
- spread: one-sided Brown-Forsythe permutation test, spread(A) > spread(B). Each run's absolute deviation from its
  own arm's median is computed once; the statistic is mean deviation of A minus that of B; p is the share of all
  splits of the pooled deviations (924 for 6 vs 6) with a statistic at least as large.
- rank: exact one-sided Mann-Whitney, B > A, on validation and on test scores (all splits enumerated, ties as 0.5).
- per arm: scores, mean, SD (n-1), worst run, share of runs below 0.50.
"""
import itertools
import json
import pathlib
import statistics
import sys


def perm_p(a, b, stat):
    """Share of all splits of a+b into len(a) and len(b) whose stat is >= the observed one."""
    pool, obs, hit, n = a + b, stat(a, b), 0, 0
    for idx in itertools.combinations(range(len(pool)), len(a)):
        s = set(idx)
        x, y = [pool[i] for i in idx], [pool[i] for i in range(len(pool)) if i not in s]
        hit += stat(x, y) >= obs - 1e-12
        n += 1
    return obs, hit / n, n


def spread(a, b):
    da = [abs(v - statistics.median(a)) for v in a]
    db = [abs(v - statistics.median(b)) for v in b]
    return perm_p(da, db, lambda x, y: statistics.mean(x) - statistics.mean(y))


def u(x, y):
    return sum((i > j) + 0.5 * (i == j) for i in x for j in y)


def load(d, arm):
    runs = []
    for p in sorted((p for p in d.glob(f"{arm}-s*") if p.is_dir()), key=lambda p: int(p.name.rsplit("-s", 1)[1])):
        m = json.loads((p / "metrics.json").read_text())
        runs.append({"seed": m["seed"], "val": m["best_val"], "test": m.get("best_test") or 0.0})
    return runs


if __name__ == "__main__":
    d, a, b = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3]
    out = {"folder": str(d), "runs": {}, "arms": {}}
    for arm in (a, b):
        runs = load(d, arm)
        v = [r["val"] for r in runs]
        out["runs"][arm] = runs
        out["arms"][arm] = {"n": len(v), "mean": statistics.mean(v), "sd": statistics.stdev(v), "worst": min(v),
                            "below_0.50": sum(x < 0.5 for x in v), "test_mean": statistics.mean(r["test"] for r in runs)}
    va, vb = ([r["val"] for r in out["runs"][x]] for x in (a, b))
    ta, tb = ([r["test"] for r in out["runs"][x]] for x in (a, b))
    diff, p, n = spread(va, vb)
    out[f"spread {a}>{b}"] = {"mean_abs_dev_diff": diff, "p": p, "splits": n,
                              "method": "Brown-Forsythe permutation, one-sided, abs. deviation from own median"}
    for name, x, y in (("val", va, vb), ("test", ta, tb)):
        obs, pr, _ = perm_p(y, x, u)
        out[f"rank {name} {b}>{a}"] = {"U": obs, "of": len(x) * len(y), "p": pr}
    print(json.dumps({k: v for k, v in out.items() if k != "runs"}, indent=1))
    if len(sys.argv) > 4:
        pathlib.Path(sys.argv[4]).write_text(json.dumps(out, indent=1))
