"""Reward content test, step 2 readout (specs/SPEC_reward5_tokens.md): per-token agreement of each model's change from the base
with Math-RL 3.1's change, on the 500 stored answers of the cued base.

    uv run --no-project --with numpy --with scipy python -m studies.rlneurons.analysis.reward5_tokens <job-id> [<job-id> ...]

Run from the repository root. Inputs (not committed): runs/<job-id>/ of the score_tokens jobs (`uv run tools/gpu.py get <job-id>`);
several jobs must have scored the same answers (tokens.npy is compared). Writes results/reward5/tokens-01/ (metrics.json, run.json,
examples.json). r_m = log p_m(stored token) - log p_base(stored token). Intervals: bootstrap over answers, 1,000 resamples, seed 0.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
from scipy.stats import rankdata

RUNS = pathlib.Path("runs")
OUT = pathlib.Path(__file__).resolve().parents[1] / "results" / "reward5" / "tokens-01"
REF, BASE = "math31", "base"


def main():
    jobs = sys.argv[1:]
    tokens = np.load(RUNS / jobs[0] / "tokens.npy")
    index = json.loads((RUNS / jobs[0] / "index.json").read_text())
    data, metrics = {}, {}
    for j in jobs:
        assert np.array_equal(np.load(RUNS / j / "tokens.npy"), tokens), j
        metrics[j] = json.loads((RUNS / j / "metrics.json").read_text())
        assert metrics[j]["status"] == "done", j
        for label in metrics[j]["models"]:
            assert label not in data or label == BASE, label
            data[label] = dict(np.load(RUNS / j / f"{label}.npz"))
    n = len(tokens)
    ans = np.repeat(np.arange(len(index)), [x["length"] for x in index])           # the answer of each position
    r = {m: d["lp_tok"] - data[BASE]["lp_tok"] for m, d in data.items() if m != BASE}
    low = r[REF] <= np.quantile(r[REF], 0.10)                                       # D of the spec
    moved = data[REF]["top"] != data[BASE]["top"]
    rk = {m: rankdata(v) for m, v in r.items()}
    rng = np.random.default_rng(0)
    starts = np.array([x["offset"] for x in index])
    lens = np.array([x["length"] for x in index])
    boots = [np.concatenate([np.arange(starts[a], starts[a] + lens[a]) for a in rng.integers(0, len(index), len(index))]) for _ in range(1000)]

    def stat(f):
        v = [f(b) for b in boots]
        return {"value": round(float(f(np.arange(n))), 4), "ci95": [round(float(np.percentile(v, 2.5)), 4), round(float(np.percentile(v, 97.5)), 4)]}

    res = {}
    for m in r:
        if m == REF:
            continue
        res[m] = {
            "pearson_r": stat(lambda b: np.corrcoef(r[m][b], r[REF][b])[0, 1]),
            "spearman_r": stat(lambda b: np.corrcoef(rk[m][b], rk[REF][b])[0, 1]),
            "share_r_below_-0.5_in_D": stat(lambda b: (r[m][b][low[b]] < -0.5).mean()),
            "share_r_below_-0.5_all": stat(lambda b: (r[m][b] < -0.5).mean()),
            "top_equals_math31_where_math31_differs_from_base": stat(lambda b: (data[m]["top"][b][moved[b]] == data[REF]["top"][b][moved[b]]).mean()),
            "top_equals_base_where_math31_differs_from_base": stat(lambda b: (data[m]["top"][b][moved[b]] == data[BASE]["top"][b][moved[b]]).mean()),
            "mean_abs_r": round(float(np.abs(r[m]).mean()), 4),
        }
    summary = {"spec": "studies/rlneurons/specs/SPEC_reward5_tokens.md", "jobs": jobs, "answers": len(index), "positions": int(n),
               "answers_with_stored_token_count": metrics[jobs[0]]["answers_with_stored_token_count"],
               "D_threshold_r_math31": round(float(np.quantile(r[REF], 0.10)), 4), "positions_math31_top_differs_from_base": int(moved.sum()),
               "mean_abs_r_math31": round(float(np.abs(r[REF]).mean()), 4), "models": {m: metrics[j]["models"][m] for j in jobs for m in metrics[j]["models"]},
               "agreement_with_math31": res}
    # two positions with their real numbers: one in D where code31 agrees (r < -0.5), one where it does not
    ex = []
    if "code31" in r:
        for want in (True, False):
            t = int(np.flatnonzero(low & ((r["code31"] < -0.5) == want))[0])
            ex.append({"code31_agrees": want, "problem_index": index[int(ans[t])]["problem_index"], "position_in_answer": t - int(starts[ans[t]]),
                       "stored_token_id": int(tokens[t]), "r": {m: round(float(v[t]), 3) for m, v in r.items()},
                       "top_token_id": {m: int(d["top"][t]) for m, d in data.items()}})
    assert not OUT.exists(), f"{OUT} exists: a rerun gets the next number"
    OUT.mkdir(parents=True)
    (OUT / "metrics.json").write_text(json.dumps(summary, indent=1) + "\n")
    (OUT / "examples.json").write_text(json.dumps(ex, indent=1) + "\n")
    (OUT / "run.json").write_text(json.dumps({"jobs": jobs, "command": "python -m studies.rlneurons.analysis.reward5_tokens " + " ".join(jobs),
                                              "raw": [f"runs/{j}/ (uv run tools/gpu.py get {j})" for j in jobs]}, indent=1) + "\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
