"""Expected best of K independent runs of each arm, from stored final scores (laptop, no model).

    python3 studies/explore/analysis/best_of_k.py studies/explore/results/ahc014/swe2-seeds-01/summary.json

Reads summary.json with runs[arm] = [{"val": final best validation score}, ...]. For every arm prints the mean of
one run and the exact mean of the maximum over all subsets of K of its runs, K = 1 .. number of runs. Answers "how
many independent runs of arm A does one run of arm B equal": the smallest K whose expected best reaches B's mean.
K independent runs cost K times the submissions of one run.
"""
import itertools
import json
import statistics
import sys

runs = {a: [r["val"] for r in v] for a, v in json.load(open(sys.argv[1]))["runs"].items()}
out = {}
for arm, v in runs.items():
    out[arm] = [statistics.mean(max(c) for c in itertools.combinations(v, k)) for k in range(1, len(v) + 1)]
    print(f"{arm:9s} n={len(v)} best of K=1..{len(v)}: {[round(x, 3) for x in out[arm]]}")
for a in runs:
    for b in runs:
        if a != b:
            k = next((i + 1 for i, x in enumerate(out[a]) if x >= out[b][0]), None)
            print(f"one {b} run ({out[b][0]:.3f}) = best of {k if k else '> ' + str(len(runs[a]))} {a} runs")
