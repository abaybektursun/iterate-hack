"""Shared embedding code for the basins study: t-STE from triplets, its held-out accuracy, bootstrap intervals."""
import numpy as np
from scipy.optimize import minimize


def tste(n, trips, dim=2, seed=0, reg=1e-3):
    """t-STE (van der Maaten & Weinberger 2012), alpha=1. trips: rows (a, b, c) meaning a is closer to b than to c."""
    T = np.asarray(trips)
    x0 = np.random.default_rng(seed).normal(scale=1e-2, size=n * dim)

    def f(flat):
        X = flat.reshape(n, dim)
        a, b, c = X[T[:, 0]], X[T[:, 1]], X[T[:, 2]]
        dab, dac = a - b, a - c
        kab = 1 / (1 + (dab ** 2).sum(1))
        kac = 1 / (1 + (dac ** 2).sum(1))
        p = kab / (kab + kac)
        loss = -np.log(p + 1e-12).sum() + reg * (X ** 2).sum()
        gab = (-kab * (1 - p))[:, None] * 2 * dab  # d logp / d a, through d2ab
        gac = (kac * (1 - p))[:, None] * 2 * dac
        G = np.zeros_like(X)
        np.add.at(G, T[:, 0], -(gab + gac))
        np.add.at(G, T[:, 1], gab)
        np.add.at(G, T[:, 2], gac)
        return loss, G.ravel() + 2 * reg * flat

    return minimize(f, x0, jac=True, method="L-BFGS-B", options={"maxiter": 2000}).x.reshape(n, dim)


def tste_acc(X, trips):
    T = np.asarray(trips)
    return float((((X[T[:, 0]] - X[T[:, 1]]) ** 2).sum(1) < ((X[T[:, 0]] - X[T[:, 2]]) ** 2).sum(1)).mean())


def boot_ci(v, rng, reps=5000):
    v = np.asarray(v, float)
    v = v[~np.isnan(v)]
    means = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(reps)]
    return [float(v.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5)), int(len(v))]
