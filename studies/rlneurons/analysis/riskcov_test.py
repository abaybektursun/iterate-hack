"""Planted cases for analysis/riskcov.py (specs/SPEC_riskcov.md, instrument checks 2 to 4, and of addendum 1), on RL's stored hard328 rows.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.riskcov_test
"""
import numpy as np

from studies.rlneurons.analysis import riskcov as RC
from studies.rlneurons.analysis import riskcov_strat as ST


def planted_strata(rl: dict, base: dict):
    """Addendum 1: on RL's lengths, right drawn from a rate that depends on problem and model only (difficulty only), then on
    model and long only (length only). The within-problem slope difference must cover 0 in the first and exclude 0 in the second."""
    rng = np.random.default_rng(2)
    n = len(rl["idx"])
    W = np.array([np.bincount(i, minlength=n) for i in rng.integers(0, n, (RC.BOOT, n))], float)
    fin = rl["ans"] & ~rl["cap"]
    long = rl["n_new"] > ST.LONG
    draw = lambda rate: {**rl, "right": fin & (rng.random(fin.shape) < rate)}
    lead = lambda t, r, c: ST.cell(t, r, fin & (long == c), fin & (long == c), W)
    slope = lambda t, r: ST.slopes(t, r, fin, fin, W, lambda x: (x > ST.LONG) * 1.0)["think - rl"]
    q = np.repeat((base["right"].sum(1)[:, None] + 0.5) / 5, 4, 1)   # the problem's rate, from the base's right count
    t, r = draw(q + 0.6 * (1 - q)), draw(q)
    raw, s = ST.contrast(lead(t, r, True), lead(t, r, False)), slope(t, r)
    assert raw["interval95"][0] > 0, f"difficulty only: the raw lead is not larger in long answers, the confound is not planted: {raw}"
    assert s["interval95"][0] < 0 < s["interval95"][1], f"difficulty only: the within-problem slope difference excludes 0: {s}"
    t, r = draw(np.where(long, 0.7, 0.95)), draw(np.where(long, 0.3, 0.95))
    s = slope(t, r)
    assert s["interval95"][0] > 20, f"length only: the within-problem slope difference misses the planted +40 points: {s}"


def main():
    by = RC.load(RC.RES / RC.SETS["hard328"]["rl"])
    rl = RC.arrays(by)
    rng = np.random.default_rng(1)

    # 2. planted perfect abstention: every wrong sample loses its answer
    planted = {**rl, "ans": rl["right"].copy()}
    # 3. shuffled lengths: n_new permuted among the answered samples
    shuffled = {**rl, "n_new": rl["n_new"].copy()}
    shuffled["n_new"][rl["ans"]] = rng.permutation(rl["n_new"][rl["ans"]])
    # 4. planted informative signal: n_new = 1 for right, 2 for wrong
    oracle = {**rl, "n_new": np.where(rl["right"], 1, 2)}

    cv = RC.curves({"think": planted, "rl": shuffled, "base": oracle}, np.random.default_rng(0))
    share = rl["right"].mean()
    for sig in RC.SIGNALS:
        m = cv["signals"][sig]["models"]["think"]
        assert abs(m["answered_share"] - share) < 1e-12
        got = [p for p in m["precision"] if p is not None]
        assert len(got) == sum(c <= share for c in RC.GRID) and all(p == 1 for p in got), f"planted abstention, {sig}: {m['precision']}"

    m = cv["signals"]["length"]["models"]["rl"]
    overall = rl["right"].sum() / rl["ans"].sum()
    inside = [lo <= overall <= hi for lo, hi, p in zip(*m["band95"], m["precision"]) if p is not None]
    assert len(inside) >= 15 and all(inside), f"shuffled lengths are not flat: {m['precision']} against {overall}"

    m = cv["signals"]["length"]["models"]["base"]
    for c, p in zip(RC.GRID, m["precision"]):
        assert p is None or (p == 1) == (c <= share), f"oracle lengths: precision {p} at coverage {c}, right share {share}"
    # the real lengths must not be flat (the test above can fail): RL's shortest 30 % are more precise than all its answers
    real = RC.curves({"think": rl, "rl": rl, "base": rl}, np.random.default_rng(0))["signals"]["length"]["models"]["rl"]
    assert real["band95"][0][RC.GRID.index(0.3)] > overall, "the real length curve is flat too: the flatness test cannot fail"

    # the cut: nothing survives L = 0 (strict abstains everywhere, fallback is the plain vote); L = cap is the plain vote
    for rows, v in zip(by.values(), rl["vote"]):
        assert RC.cut_vote(rows, 0, False) == 0 and RC.cut_vote(rows, 0, True) == v and RC.cut_vote(rows, 16384, False) == v
    t = RC.transition(rl["sample"], rl["sample"])
    assert sum(t.values()) == rl["sample"].size and all(v == 0 for k, v in t.items() if k.split(" / ")[0] != k.split(" / ")[1])
    c = {"a_1": {"right": 5, "L": 1, "variant": "strict"}, "b_2": {"right": 5, "L": 2, "variant": "strict"}, "c_2": {"right": 5, "L": 2, "variant": "fallback"},
         "d_9": {"right": 4, "L": 9, "variant": "fallback"}, "plain": {"right": 9}}
    assert RC.choose(c) == "c_2"
    planted_strata(rl, RC.arrays(RC.load(RC.RES / RC.SETS["hard328"]["base"])))
    print("riskcov_test: all planted cases pass")


if __name__ == "__main__":
    main()
