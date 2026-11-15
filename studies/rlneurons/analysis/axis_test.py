"""Planted-data checks of analysis/axis.py (specs/SPEC_axis.md, "Instrument checks"): one axis must come out one axis, a planted
second axis must be detected, identical arms must show as alike. Result on the committed code (seeds fixed): see the README section.

    uv run --no-project --with numpy python -m studies.rlneurons.analysis.axis_test
"""
import itertools

import numpy as np

from studies.rlneurons.analysis import axis as X

NJ, NI = 30, 500


def planted(second, seed):
    """30 arms x 500 problems; abilities and difficulties spread like the real MATH-500 arms. second: logits that arms 0-14 gain on
    problems 0-149 and arms 15-29 on problems 150-299."""
    rng = np.random.default_rng(seed)
    z = rng.normal(2.5, 0.8, NJ)[:, None] + rng.normal(0, 2.5, NI)[None, :]
    z[:15, :150] += second
    z[15:, 150:300] += second
    return (rng.random((NJ, NI)) < 1 / (1 + np.exp(-z))).astype(float)


def pairs(Y, names, im):
    return {(r["a"], r["b"]): r for r in X.pair_table(Y, names, {}, list(itertools.combinations(names, 2)), p=X.rasch_p(Y, im["ridge"][0]), sims=100)}


def main():
    names = [f"arm{j:02d}" for j in range(NJ)]
    group = lambda n: int(n[3:]) < 15

    Y = planted(0.0, 1)
    im = X.item_model(Y, names)
    z = np.array([r["z"] for r in pairs(Y, names, im).values()])
    print(f"one axis: pair z mean {z.mean():.2f} sd {z.std():.2f}, share |z| > 3 {(abs(z) > 3).mean():.3f}; 2-D gain {im['gain_2d']} "
          f"vs null p95 {im['null_gain_rasch_sim']['p95']}")
    assert abs(z.mean()) < 0.3 and (abs(z) > 3).mean() < 0.02, "one axis: the pair null is miscalibrated"
    assert not im["second_axis_detected"], "one axis: a second axis was reported"

    for second, seed in ((1.5, 2), (4.0, 4)):
        Y = planted(second, seed)
        im = X.item_model(Y, names)
        pr = pairs(Y, names, im)
        cross = np.array([(r["z"], r["excess"]) for (a, b), r in pr.items() if group(a) != group(b)])
        within = np.array([(r["z"], r["excess"]) for (a, b), r in pr.items() if group(a) == group(b)])
        load = np.array([im["loading_2d"][n] for n in names])
        split = sorted([(load[:15] > 0).mean(), (load[15:] > 0).mean()])
        print(f"second axis of {second} logits: cross-group z mean {cross[:, 0].mean():.2f} (excess {cross[:, 1].mean():.1f} problems), within-group z mean "
              f"{within[:, 0].mean():.2f} (excess {within[:, 1].mean():.1f}); 2-D gain {im['gain_2d']} vs null p95 {im['null_gain_rasch_sim']['p95']}; "
              f"share of positive loadings in the two groups {split}")
        assert im["second_axis_detected"], "second axis not detected by the item model"
        assert cross[:, 0].mean() - within[:, 0].mean() > 1, "cross-group pairs are not more complementary than within-group pairs"
        assert split[0] < 0.1 and split[1] > 0.9, "loadings do not separate the groups"
        if second == 4.0:
            assert cross[:, 0].mean() > 1.5 and cross[:, 1].mean() > 3, "strong second axis: cross-group pairs show no excess"

    Y = planted(0.0, 3)
    Y[1] = Y[0]
    r = X.pair_table(Y, names, {}, [(names[0], names[1])])[0]
    print(f"identical arms: excess {r['excess']}, z {r['z']}")
    assert r["z"] < -5, "identical arms are not flagged as alike"
    print("ok")


if __name__ == "__main__":
    main()
