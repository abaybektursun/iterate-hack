"""Paired comparison of two finals on one set, from their per-problem grades.

    python3 studies/autobench/analysis/paired.py <a graded.json> <b graded.json>

Prints right of n for each, the difference a minus b in points, and its 95 % interval from a paired bootstrap over
problems (10,000 resamples, seed 0). The grades are the runner's graded.json (index, right, extracted), copied from
the Volume autobench-runs into results/math500-loop/finals-01/.
"""
import json
import random
import sys


def main():
    a, b = ({r["index"]: r["right"] for r in json.load(open(path))} for path in sys.argv[1:3])
    assert a.keys() == b.keys(), "the two files grade different problems"
    diffs = [a[i] - b[i] for i in sorted(a)]
    n, rng = len(diffs), random.Random(0)
    means = sorted(sum(rng.choices(diffs, k=n)) / n for _ in range(10000))
    print(f"{sys.argv[1]}: {sum(a.values())} of {n}; {sys.argv[2]}: {sum(b.values())} of {n}; "
          f"difference {100 * sum(diffs) / n:+.1f} points [{100 * means[249]:+.1f}, {100 * means[9749]:+.1f}]; "
          f"only first right {sum(d == 1 for d in diffs)}, only second right {sum(d == -1 for d in diffs)}")


if __name__ == "__main__":
    main()
