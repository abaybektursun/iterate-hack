"""Planted-data checks of analysis/rate.py (specs/SPEC_rate.md): arms from a known one-axis model on two sets of different
difficulty must transfer within sampling noise by the calibrated logit rule and better than by "same point gain"; an arm with
a set-specific effect must show a transfer error.

    uv run --no-project --with numpy python -m studies.rlneurons.analysis.rate_test
"""
import numpy as np

from studies.rlneurons.analysis import rate as R

SHIFTS = {"t0": 0.6, "t1": 0.9, "t2": 1.0, "t3": 1.3, "t4": 1.5}


def planted(seed, specific=1.2):
    """Set 1: 500 problems, 30 background arms, 4 reference samples, the 5 test arms and one arm `planted` whose shift of
    `specific` logits exists on set 1 only. Set 2: 328 harder problems (difficulty mean 2.2 logits lower), 2 reference samples."""
    rng = np.random.default_rng(seed)
    b1, b2 = rng.normal(0, 2.5, 500), rng.normal(-2.2, 2.5, 328)
    draw = lambda a, b, k=1: (rng.random((k, len(b))) < R.sig(a + b)).astype(float)
    S5 = {"ref": draw(2.0, b1, 4)} | {a: draw(2.0 + d, b1) for a, d in SHIFTS.items()} | {"planted": draw(2.0 + specific, b1)}
    S3 = {"ref": draw(2.0, b2, 2)} | {a: draw(2.0 + d, b2) for a, d in SHIFTS.items()} | {"planted": draw(2.0, b2)}
    back = [draw(a, b1) for a in rng.normal(2.5, 0.8, 30)]
    b5 = R.difficulties(list(S5.values()) + back, R.LAM["math500"])
    extra = [draw(-0.5, b2)]
    clean = lambda S: {a: v for a, v in S.items() if a != "planted"}       # the planted arm would bias c for the clean arms
    return R.transfer(b5, clean(S5), clean(S3), extra, R.LAM["hard328"])[0] | {"planted": R.transfer(b5, S5, S3, extra, R.LAM["hard328"])[0]["planted"]}


def main():
    err = {r: [] for r in ("L1", "Lc", "M", "P", "R")}
    plant = []
    for seed in range(20):
        rows = planted(seed)
        for r in err:
            err[r] += [rows[a][r] - rows[a]["observed"] for a in SHIFTS]
        plant.append(rows["planted"]["Lc"] - rows["planted"]["observed"])
    mae = {r: round(float(np.mean(np.abs(v))), 2) for r, v in err.items()}
    sd = float(np.std(err["Lc"]))
    print("clean arms, 20 seeds x 5 arms, mean absolute error in problems of 328:", mae, "| Lc bias", round(float(np.mean(err["Lc"])), 2), "sd", round(sd, 2))
    print("planted arm (set-specific +1.2 logits): mean Lc error", round(float(np.mean(plant)), 1), "problems =", round(float(np.mean(plant)) / sd, 1), "sd")
    assert mae["Lc"] < mae["P"] and mae["Lc"] < 10, "calibrated logit transfer must recover a planted one-axis model and beat point transfer"
    assert np.mean(plant) > 3 * sd, "a set-specific effect must show as a transfer error"
    print("planted checks pass")


if __name__ == "__main__":
    main()
