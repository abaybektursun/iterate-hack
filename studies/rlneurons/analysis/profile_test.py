"""Planted-data checks of analysis/profile.py (specs/SPEC_profile.md).

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.profile_test
"""
import numpy as np

from studies.rlneurons.analysis import axis as X
from studies.rlneurons.analysis import profile as P
from studies.rlneurons.analysis import rate as R


def main():
    rng = np.random.default_rng(0)
    V, ind = R.load("math500")
    m = P.meta()
    Y = np.vstack([V[n] for n in ind])
    obs = ~np.isnan(Y)
    a, b = X.fit(Y, obs.astype(float), P.LAM)[:2]
    draw = lambda z: dict(zip(ind, np.where(obs, (rng.random(z.shape) < R.sig(z)).astype(float), np.nan)))
    W = R.boot(500)

    def run(Z):
        p = X.rasch_p(np.vstack([Z[n] for n in ind]), P.LAM)
        h = P.h1(Z, ind, P.designs(Z, ind, m["level"]), m["level"], W, p, sims=100)
        return h, P.h2(Z, ind, p, sims=10)

    # 1. one axis (Rasch at the fitted abilities): no 2PL gain, C inside the one-axis range
    h, t = run(draw(a[:, None] + b[None, :]))
    print("1. Rasch: 2PL gain", t["gain"], "null p95", t["null_gain_rasch_sim"]["p95"], "| C", {d: (x["C_sft1_cue_vs_rl_plain"], x["outside_one_axis_null95"]) for d, x in h.items()})
    assert t["gain"] < 5e-4 and sum(x["outside_one_axis_null95"] for x in h.values()) <= 1, (t["gain"], h)
    # 2. planted 2PL, g of sd 0.3: detected, and the fitted g follow the planted ones
    g = rng.normal(0, 0.3, len(ind))
    Z = draw(a[:, None] + (1 + g)[:, None] * b[None, :])
    t = P.h2(Z, ind, X.rasch_p(np.vstack([Z[n] for n in ind]), P.LAM), sims=10)
    r = float(np.corrcoef(g, [t["g"][n]["g"] for n in ind])[0, 1])
    print("2. planted 2PL (sd 0.3): gain", t["gain"], "null p95", t["null_gain_rasch_sim"]["p95"], "detected", t["detected"], "| corr of fitted and planted g", round(r, 2))
    assert t["detected"] and r > 0.7, (t, r)
    # 3. an arm of RL's ability that also fails 5 % of all problems whatever their difficulty: C must be negative and outside
    Z = draw(a[:, None] + b[None, :])
    Z["sft1_cue"] = ((rng.random(500) < R.sig(np.mean([a[ind.index(n)] for n in R.RL4]) + 0.5 + b)) & (rng.random(500) > 0.05)).astype(float)
    p = X.rasch_p(np.vstack([Z[n] for n in ind]), P.LAM)
    h = P.h1(Z, ind, P.designs(Z, ind, m["level"]), m["level"], W, p, sims=100)
    print("3. planted difficulty-free failures (5 %):", {d: (x["C_sft1_cue_vs_rl_plain"], x["one_axis_null"]["p2.5"], x["outside_one_axis_null95"]) for d, x in h.items()})
    assert all(x["C_sft1_cue_vs_rl_plain"] < 0 for x in h.values()) and sum(x["outside_one_axis_null95"] for x in h.values()) >= 2, h
    print("all planted checks pass")


if __name__ == "__main__":
    main()
