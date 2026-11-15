"""Planted checks of analysis/seen.py (specs/SPEC_seen.md "Checks").

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.seen_test

Planted D = +20 points must give an interval that excludes 0; planted D = 0 an interval that includes 0; a seen set that is
only easier for every arm (pretraining exposure) must give D near 0 and a positive seen - unseen for the base.
"""
import numpy as np

from studies.rlneurons.analysis import seen


def planted(extra_rl_seen, easier_seen, seed):
    rng = np.random.default_rng(seed)
    meta = seen.sets()
    val = {a: {} for a in ("base", "rl", "code")}
    for i, (g, _) in meta.items():
        p = {"base": 0.4, "rl": 0.5, "code": 0.4}
        for a in p:
            q = p[a] + (easier_seen if g != "unseen" else 0) + (extra_rl_seen if a == "rl" and g != "unseen" else 0)
            val[a][i] = rng.binomial(4, q) / 4
    return seen.stats(val, [i for i, (g, _) in meta.items() if g != "unseen"], meta, boot=2000)


def main():
    lo, hi = planted(0.20, 0.0, 1)["D(code)"]["interval95"]
    assert lo > 0 and lo < 20 < hi, (lo, hi)
    lo, hi = planted(0.0, 0.0, 2)["D(code)"]["interval95"]
    assert lo < 0 < hi, (lo, hi)
    s = planted(0.0, 0.25, 3)
    assert s["D(code)"]["interval95"][0] < 0 < s["D(code)"]["interval95"][1] and s["base seen - unseen"]["interval95"][0] > 0, s
    width = np.mean([np.diff(planted(0.0, 0.0, k)["D(code)"]["interval95"])[0] for k in range(4, 8)]) / 2
    print(f"seen_test passed; D interval half-width on planted rows {width:.1f} points")


if __name__ == "__main__":
    main()
