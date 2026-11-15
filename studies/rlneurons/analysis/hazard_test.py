"""Planted-data checks of analysis/hazard.py (specs/SPEC_hazard.md, "Planted tests").

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.hazard_test
"""
import numpy as np

from studies.rlneurons.analysis import hazard as H
from studies.rlneurons.analysis import rate as R


def matrix(link, a, b, rng):
    return (rng.random((len(a), len(b))) < H.prob(a[:, None] + b[None, :], link)).astype(float)


def main():
    rng = np.random.default_rng(0)
    # 1. wide ability range, 36 x 500: each link must be recognised
    for link in H.LINKS:
        r = H.link_test(matrix(link, np.linspace(-2.5, 4, 36), rng.normal(0, 1.5, 500), rng), sims=30)[0]
        print(f"1. planted {link}, 36 x 500, wide abilities: verdict {r['verdict']}, T {r['T_hazard_minus_logit']}, power {r['power_at_this_size']}")
        assert r["verdict"] == link, r
    # 2. 4 x 100: the test must not pick a link
    for link in H.LINKS:
        r = H.link_test(matrix(link, np.linspace(0, 2, 4), rng.normal(0, 1.5, 100), rng), sims=100)[0]
        print(f"2. planted {link}, 4 x 100: verdict {r['verdict']}, T {r['T_hazard_minus_logit']}, power {r['power_at_this_size']}")
        assert r["verdict"] == "cannot tell", r
    # 4, 5 on a matrix simulated from the hazard model fitted to the real one (same arms, same names)
    V, ind = R.load("math500")
    lam = {"logit": 0.3, "hazard": 1.0}
    a, b = H.full(np.vstack([V[n] for n in ind]), lam["hazard"], "hazard")
    Z = dict(zip(ind, matrix("hazard", a, b, rng)))
    hard = b < np.percentile(b, 33)
    ab = a[ind.index("base_cue_s0")]
    Z["rl_cue"] = (rng.random(500) < H.prob(ab + np.where(hard, -np.log(0.2), 0.0) + b, "hazard")).astype(float)     # HR 0.2 on the hardest third only
    fitp = lambda: {l: (lambda P: H.prob(P[0][:, None] + P[1][None, :], l))(H.full(np.vstack([Z[n] for n in ind]), lam[l], l)) for l in H.LINKS}
    c = H.constancy(Z, ind, lam, fitp())["hazard"]
    print("4. constant arms (hazard truth), hard minus easy against the null:", {m: (c[m]["hard_minus_easy"], c[m]["null_constant_shift"]["p2.5"], c[m]["null_constant_shift"]["p97.5"]) for m in H.METHODS})
    assert c["rl_cue"]["outside_null95"], c["rl_cue"]
    assert sum(c[m]["outside_null95"] for m in H.METHODS if m != "rl_cue") <= 1, "constant arms must sit inside their null"
    # 5. shared failures inside one family must show as over-dispersion
    Z = dict(zip(ind, matrix("hazard", a, b, rng)))
    shared = rng.random(500) < 0.3
    for n in R.BASE4:
        Z[n] = np.where(shared, Z["base_cue_s0"], Z[n])
    Z["base_vote4"] = (np.vstack([Z[n] for n in R.BASE4]).sum(0) >= 2).astype(float)
    Z["rl_vote4"] = (np.vstack([Z[n] for n in R.RL4]).sum(0) >= 2).astype(float)
    d = H.dispersion(Z, ind, lam, fitp())["hazard"]
    print("5. D:", {f: (d[f]["D"], d[f]["D_null_independent_cells"]["p95"], d[f]["zero_of_4_minus_binomial"]) for f in d})
    assert d["base_cue"]["over_dispersed"] and not d["rl_plain"]["over_dispersed"], d
    print("planted checks pass")


if __name__ == "__main__":
    main()
