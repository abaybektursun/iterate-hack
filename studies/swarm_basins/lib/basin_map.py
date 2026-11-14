"""Basin maps from triplet judgments (Bespoke Labs / Fork-and-Flush method, arXiv 2610.07447), laptop, no model.

A triplet (a, b, c) means "a is closer to b than to c". t-STE puts the items in 2D so that held-out triplets are
predicted; basins are k-means clusters of the 2D map, k from 3 to 8 by silhouette score.
"""
import numpy as np
from scipy.optimize import minimize
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score


def tste_loss(flat, T, n, dim=2, reg=1e-3):
    """t-STE (van der Maaten & Weinberger 2012) loss and gradient, alpha=1. T: rows (a, b, c), a closer to b.
    Same math as exp/strategy_analyze.py on branch ali/strategy-basins; gradient checked in selftest.py."""
    X = flat.reshape(n, dim)
    a, b, c = X[T[:, 0]], X[T[:, 1]], X[T[:, 2]]
    dab, dac = a - b, a - c
    kab = 1 / (1 + (dab ** 2).sum(1))
    kac = 1 / (1 + (dac ** 2).sum(1))
    p = kab / (kab + kac)
    loss = -np.log(p + 1e-12).sum() + reg * (X ** 2).sum()
    gab = (-kab * (1 - p))[:, None] * 2 * dab  # d log p / d a, through d2ab
    gac = (kac * (1 - p))[:, None] * 2 * dac
    G = np.zeros_like(X)
    np.add.at(G, T[:, 0], -(gab + gac))
    np.add.at(G, T[:, 1], gab)
    np.add.at(G, T[:, 2], gac)
    return loss, G.ravel() + 2 * reg * flat


def tste(n, trips, dim=2, seed=0, reg=1e-3):
    """2D t-STE map of n items from triplets."""
    T = np.asarray(trips)
    x0 = np.random.default_rng(seed).normal(scale=1e-2, size=n * dim)
    fit = minimize(tste_loss, x0, args=(T, n, dim, reg), jac=True, method="L-BFGS-B", options={"maxiter": 3000})
    return fit.x.reshape(n, dim)


def agreement(X, trips):
    """Share of triplets the map predicts: d(a, b) < d(a, c)."""
    T = np.asarray(trips)
    return float((((X[T[:, 0]] - X[T[:, 1]]) ** 2).sum(1) < ((X[T[:, 0]] - X[T[:, 2]]) ** 2).sum(1)).mean())


def label_agreement(labels, trips):
    """Share of triplets predicted by 'b shares a's label and c does not' (ties count 1/2). The baseline for a
    map that only encodes author or kind."""
    L = np.asarray(labels)
    T = np.asarray(trips)
    sb, sc = L[T[:, 1]] == L[T[:, 0]], L[T[:, 2]] == L[T[:, 0]]
    return float(np.where(sb == sc, 0.5, sb.astype(float)).mean())


def heldout(n, trips, seed=0, frac=0.9):
    """Fit on frac of the triplets, return (agreement on the rest, the held-out triplets)."""
    T = np.asarray(trips)
    perm = np.random.default_rng(seed).permutation(len(T))
    cut = int(frac * len(T))
    X = tste(n, T[perm[:cut]], seed=seed)
    return agreement(X, T[perm[cut:]]), T[perm[cut:]]


def by_size(raw):
    """Relabel clusters so basin 0 is the largest."""
    order = np.argsort(-np.bincount(raw))
    remap = np.empty(len(order), int)
    remap[order] = np.arange(len(order))
    return remap[raw]


def cluster(n, trips, k, dim=5, seed=0):
    """k-means with a given k on a 5D t-STE fit. The 2D fit is for drawing only: on planted 5-cluster data with
    150 triplets per item, k-means recovers the clusters at ARI 0.69 in 2D and 0.94 in 5D (selftest.py).
    k is not chosen from the triplets: silhouette, held-out triplet prediction and subsample stability all chose
    2-3 on planted data with 5 or 7 clusters. k comes from the judge's partition instead (analysis/run.py)."""
    X = tste(n, trips, dim=dim, seed=seed, reg=1e-2)
    return by_size(KMeans(n_clusters=k, n_init=20, random_state=seed).fit(X).labels_)


def label_null(labels, trips, reps=1000, seed=0):
    """label_agreement of real labels vs the same labels permuted over items: does a partition predict the
    triplet judgments better than a partition of the same sizes at random?"""
    rng = np.random.default_rng(seed)
    real = label_agreement(labels, trips)
    null = np.array([label_agreement(rng.permutation(labels), trips) for _ in range(reps)])
    return {"real": real, "null_mean": float(null.mean()), "null_p95": float(np.percentile(null, 95)),
            "p_above": float((null >= real).mean())}


def entropy_share(labels, k):
    """exp(entropy) / k: 1 when posts spread evenly over all basins, 1/k when all sit in one."""
    c = np.bincount(labels, minlength=k).astype(float)
    p = c[c > 0] / c.sum()
    return float(np.exp(-(p * np.log(p)).sum()) / k)


def switch_rate(seq):
    """Share of consecutive posts in a sequence that change basin."""
    seq = list(seq)
    return float(np.mean([a != b for a, b in zip(seq, seq[1:])])) if len(seq) > 1 else float("nan")


def switch_null(seqs, reps=2000, seed=0):
    """Pooled switch rate of the real time order vs the same posts shuffled in time within each sequence.
    A real rate below the null's 5th percentile means the posters stay in a basin longer than chance."""
    rng = np.random.default_rng(seed)
    seqs = [list(s) for s in seqs if len(s) > 1]

    def pooled(ss):
        pairs = [(a != b) for s in ss for a, b in zip(s, s[1:])]
        return float(np.mean(pairs)) if pairs else float("nan")

    real = pooled(seqs)
    null = np.array([pooled([list(rng.permutation(s)) for s in seqs]) for _ in range(reps)])
    return {"real": real, "null_mean": float(null.mean()), "null_p05": float(np.percentile(null, 5)),
            "null_p95": float(np.percentile(null, 95)), "p_below": float((null <= real).mean()),
            "n_sequences": len(seqs), "n_steps": sum(len(s) - 1 for s in seqs)}
