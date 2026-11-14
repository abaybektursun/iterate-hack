"""Instrument checks for the basin map (laptop, no model). Each check is an input that should make the map fail or
pass, with a known answer.

    python -m studies.swarm_basins.analysis.selftest

1. Gradient: the t-STE gradient matches finite differences.
2. Planted basins: 120 items in 5 known clusters in 8D, triplets from true distances with 15% flipped, 150
   appearances per item. The map must predict held-out triplets at >= 0.70 (true positions: ~0.85), k-means
   with k = 5 on the 5D fit must recover the clusters (adjusted Rand >= 0.85), and the true labels must predict
   the triplets better than permuted labels.
3. Coin-flip judge: the same triplets with each answer replaced by a coin flip must give held-out agreement
   near 0.5 (<= 0.56), and the true labels must no longer beat permuted labels.
4. Switch null: a sequence that stays in each basin for runs of 6 must test as sticky (p_below < 0.05); a
   sequence in random order must not.
"""
import numpy as np
from scipy.optimize import approx_fprime
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

from studies.swarm_basins.lib import basin_map as bm


def planted(n=120, k=5, flip=0.15, per_item=30, seed=0):
    rng = np.random.default_rng(seed)
    centers = rng.normal(scale=6, size=(k, 8))
    truth = rng.integers(0, k, n)
    P = centers[truth] + rng.normal(size=(n, 8))
    trips = []
    for a in range(n):
        for _ in range(per_item // 3):
            b, c = rng.choice([i for i in range(n) if i != a], 2, replace=False)
            closer_b = ((P[a] - P[b]) ** 2).sum() < ((P[a] - P[c]) ** 2).sum()
            if rng.random() < flip:
                closer_b = not closer_b
            trips.append((a, b, c) if closer_b else (a, c, b))
    return truth, np.array(trips)


def main():
    # 1. gradient
    rng = np.random.default_rng(1)
    T = np.array([(0, 1, 2), (1, 3, 0), (2, 0, 3), (3, 2, 1)])
    x = rng.normal(size=8)
    _, G = bm.tste_loss(x, T, 4)
    num = approx_fprime(x, lambda f: bm.tste_loss(f, T, 4)[0], 1e-6)
    err = float(np.abs(G - num).max())
    print(f"1. gradient max abs error vs finite differences: {err:.2e}")
    assert err < 1e-4, err

    # 2. planted basins, 150 triplet appearances per item, k given
    truth, trips = planted(per_item=150)
    acc, _ = bm.heldout(len(truth), trips)
    ari = adjusted_rand_score(truth, bm.cluster(len(truth), trips, 5))
    ari2 = adjusted_rand_score(truth, bm.by_size(KMeans(5, n_init=20, random_state=0).fit(bm.tste(len(truth), trips)).labels_))
    ln = bm.label_null(truth, trips)
    print(f"2. planted: held-out agreement {acc:.3f}; ARI 5D {ari:.3f}, 2D {ari2:.3f}; true labels predict "
          f"{ln['real']:.3f} of triplets vs {ln['null_mean']:.3f} for permuted labels (p={ln['p_above']:.3f})")
    assert acc >= 0.70 and ari >= 0.85 and ln["p_above"] < 0.01, (acc, ari, ln)

    # 3. coin-flip judge: each answer replaced by a random one
    flip = np.random.default_rng(2).random(len(trips)) < 0.5
    shuffled = np.where(flip[:, None], trips[:, [0, 2, 1]], trips)
    acc_null, _ = bm.heldout(len(truth), shuffled)
    ln0 = bm.label_null(truth, shuffled)
    print(f"3. coin-flip judge: held-out agreement {acc_null:.3f} (should be ~0.5); true labels predict "
          f"{ln0['real']:.3f} vs null {ln0['null_mean']:.3f} (p={ln0['p_above']:.3f}, should be large)")
    assert acc_null <= 0.56 and ln0["p_above"] > 0.05, (acc_null, ln0)

    # 4. switch null
    sticky = [[b for b in range(5) for _ in range(6)] for _ in range(4)]
    rng = np.random.default_rng(3)
    random_order = [list(rng.integers(0, 5, 30)) for _ in range(4)]
    s1, s2 = bm.switch_null(sticky), bm.switch_null(random_order)
    print(f"4. switch null: sticky real {s1['real']:.2f} vs null {s1['null_mean']:.2f} p={s1['p_below']:.3f}; "
          f"random real {s2['real']:.2f} vs null {s2['null_mean']:.2f} p={s2['p_below']:.3f}")
    assert s1["p_below"] < 0.05 and s2["p_below"] > 0.05

    print("all instrument checks passed")


if __name__ == "__main__":
    main()
