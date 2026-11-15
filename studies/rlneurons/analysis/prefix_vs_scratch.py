"""Is the answer already lost before the judged wrong step? Right rate of continuations from the prefix (results/wrongstep/prefix-01)
against the right rate of the same model from the start of the same problem, within the same token budget.

    uv run --no-project --with numpy python -m studies.rlneurons.analysis.prefix_vs_scratch

Run from the repository root. From-scratch rows: results/day1_3/math500_{base_cue,rl}-01/rows.jsonl (4 samples, cap 16,384). A
from-scratch sample counts as right only if it is right and no longer than prefix tokens + the continuation cap; the base's judged
sample (wrong by selection) is left out. Prefix lengths come from runs/<job>/answers.jsonl of the base arm (not committed) and are
saved in the output. Writes results/wrongstep/prefix_vs_scratch-01/metrics.json. Paired bootstrap over prefixes, 5,000 resamples, seed 0.
"""
import collections
import json
import pathlib

import numpy as np

RES = pathlib.Path(__file__).resolve().parents[1] / "results"
PRE = RES / "wrongstep" / "prefix-01"
OUT = RES / "wrongstep" / "prefix_vs_scratch-01"


def rows(cell):
    d = collections.defaultdict(dict)
    for line in open(RES / "day1_3" / cell / "rows.jsonl"):
        r = json.loads(line)
        if r["attempt"] == 0:
            d[r["problem_index"]][r["sample"]] = r
    return d


def main():
    per = json.loads((PRE / "per_prefix.json").read_text())
    run = json.loads((PRE / "run.json").read_text())
    cap = json.loads((PRE / "metrics.json").read_text())["config"]["base"]["cap"]
    label, items = per["label"], sorted(per["label"])
    n_prefix = {}
    for j in run["arms"]["base"]:
        for line in open(pathlib.Path("runs") / j / "answers.jsonl"):
            r = json.loads(line)
            n_prefix[r["item"]] = r["n_prefix_tokens"]
    scratch = {"base": rows("math500_base_cue-01"), "rl": rows("math500_rl-01")}
    rng = np.random.default_rng(0)
    res = {"continuation_cap": cap, "n_prefix_tokens": n_prefix, "groups": {}}
    for group in ("all", "misread", "slip", "wrong_plan"):
        its = [i for i in items if group in ("all", label[i])]
        bs = rng.integers(0, len(its), (5000, len(its)))
        g = {"prefixes": len(its)}
        for arm in ("base", "rl"):
            s = []
            for i in its:
                q, k = (int(x) for x in i.split(":"))
                s.append(np.mean([r["score_v3"] and r["n_new"] <= n_prefix[i] + cap for smp, r in scratch[arm][q].items() if arm == "rl" or smp != k]))
            d = np.array([np.mean(per[arm][i]) for i in its]) - np.array(s)
            b = d[bs].mean(1) * 100
            g[arm] = {"from_scratch_within_budget_percent": round(float(np.mean(s) * 100), 1), "from_prefix_percent": round(float(np.mean([np.mean(per[arm][i]) for i in its]) * 100), 1),
                      "prefix_minus_scratch_points": round(float(d.mean() * 100), 1), "ci95": [round(float(np.percentile(b, 2.5)), 1), round(float(np.percentile(b, 97.5)), 1)]}
        res["groups"][group] = g
    assert not OUT.exists(), f"{OUT} exists: a rerun gets the next number"
    OUT.mkdir(parents=True)
    (OUT / "metrics.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res["groups"], indent=1))


if __name__ == "__main__":
    main()
