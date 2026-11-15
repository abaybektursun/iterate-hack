"""Slip-hazard law (specs/SPEC_hazard.md, board idea-7928c0): P(right) = exp(-h_j L_i), i.e. the item model
-log p_ij = exp(-(a_j + b_i)) ("hazard link"), against the Rasch logit model of analysis/axis.py, on the per-problem 0/1
vectors of every arm. Hazard ratio of an arm against a reference: HR = exp(-(a_arm - a_ref)).

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.hazard fit|transfer|predict|score

  fit       results/hazard/math500-01/{readout.json,table.json,table.md,examples.json,run.json}: link test (H1), hazard ratios
            and their constancy over difficulty (H2), theta (H2b), chain length (H4a), over-dispersion and vote (H4b)
  transfer  results/hazard/transfer-01/readout.json (H3: leave-one-arm-out, MATH-500 -> hard328, both links)
  predict   results/hazard/predict-01/predictions.json (filed once, refuses to overwrite)
  score     results/hazard/scored-01/readout.json (the filed hazard and logit predictions against OBSERVED)
"""
from __future__ import annotations

import argparse
import datetime
import json
import math
import subprocess

import numpy as np

from studies.rlneurons.analysis import axis as X
from studies.rlneurons.analysis import rate as R

OUT = X.STUDY / "results" / "hazard"
LINKS = ("logit", "hazard")
GRID = (0.01, 0.03, 0.1, 0.3, 1.0, 3.0)                 # the ridge grid of axis.heldout
ZLO, ZHI = -4.0, 15.0
BOOT = 2000
# arms compared with the pooled base + cue samples in the difficulty-group test; none of them is used to form the groups
METHODS = {"rl_plain": R.RL4, "rl_cue": ["rl_cue"], "theta0.25_cue": ["theta0.25_cue"], "theta0.5_cue": ["theta0.5_cue"],
           "theta0.75_cue": ["theta0.75_cue"], "sft1_cue": ["sft1_cue"], "code_cue": ["code_cue"]}
HELD = set(R.BASE4) | {n for v in METHODS.values() for n in v}


# ---------- the two links ----------
def prob(z, link):
    if link == "mirror":                                # post hoc: the hazard link with right and wrong exchanged, 1 - p = exp(-exp(z))
        return 1 - prob(-z, "hazard")
    return R.sig(z) if link == "logit" else np.exp(-np.exp(-np.clip(z, ZLO, ZHI)))


def score(z, link):
    """d log-likelihood / dz of a right cell and of a wrong cell."""
    if link == "mirror":
        s1, s0 = score(-z, "hazard")
        return -s0, -s1
    if link == "logit":
        p = R.sig(z)
        return 1 - p, -p
    m = np.exp(-np.clip(z, ZLO, ZHI))
    return m, -m / np.expm1(m)


def cell_ll(z, y, link):
    if link == "mirror":
        return cell_ll(-z, 1 - y, "hazard")
    if link == "logit":
        return -(np.logaddexp(0, -z) * y + np.logaddexp(0, z) * (1 - y))
    m = np.exp(-np.clip(z, ZLO, ZHI))
    return -m * y + np.log(-np.expm1(-m)) * (1 - y)


def fit(Y, W, lam, link, steps=400):
    """(a, b): arm abilities and item parameters, ridge lam on b. Logit: axis.fit. Hazard: the same Adam loop with the hazard residual."""
    if link == "logit":
        P = X.fit(Y, W, lam, steps=steps)
        return P[0], P[1]
    P = [np.zeros(Y.shape[0]), np.zeros(Y.shape[1])]
    Y0 = np.where(W > 0, Y, 0.0)
    m, v = [np.zeros_like(p) for p in P], [np.zeros_like(p) for p in P]
    for t in range(1, steps + 1):
        s1, s0 = score(P[0][:, None] + P[1][None, :], link)
        G = -W * (Y0 * s1 + (1 - Y0) * s0)
        G = [G.sum(1), G.sum(0) + lam * P[1]]
        for k in range(2):
            m[k] = 0.9 * m[k] + 0.1 * G[k]
            v[k] = 0.999 * v[k] + 0.001 * G[k] ** 2
            P[k] = P[k] - 0.1 * (m[k] / (1 - 0.9 ** t)) / ((v[k] / (1 - 0.999 ** t)) ** 0.5 + 1e-8)
    return P


def full(Y, lam, link, steps=400):
    return fit(Y, (~np.isnan(Y)).astype(float), lam, link, steps)


def solve(w1, w0, b, link):
    """Maximum-likelihood a for rows of weights: w1 (B, n) right cells and w0 (B, n) wrong cells per problem. Bisection on the score."""
    lo, hi = np.full(len(w1), -15.0), np.full(len(w1), 15.0)
    for _ in range(40):
        mid = (lo + hi) / 2
        s1, s0 = score(mid[:, None] + b[None, :], link)
        up = (w1 * s1 + w0 * s0).sum(1) > 0
        lo, hi = np.where(up, mid, lo), np.where(up, hi, mid)
    return (lo + hi) / 2


def ability(y, b, link, w=None):
    """ML ability of the pooled 0/1 vectors y ((n,) or (k, n), nan = no score) given b. w: (B, n) bootstrap counts -> (B,)."""
    y = np.atleast_2d(y)
    cnt, tot = (~np.isnan(y)).sum(0).astype(float), np.nansum(y, 0)
    if w is None:
        return float(solve(tot[None], (cnt - tot)[None], b, link)[0])
    return solve(w * tot, w * (cnt - tot), b, link)


# ---------- H1: which link ----------
def folds(Y):
    return np.random.default_rng(0).integers(0, 5, Y.shape)          # the folds of axis.heldout


def cv_ll(Y, obs, fold, lam, link, steps=400):
    """Log-likelihood of every observed cell under the model fitted without the cell's fold."""
    L = np.zeros(Y.shape)
    Yz = np.where(obs, Y, 0.0)
    for f in range(5):
        a, b = fit(Y, (obs & (fold != f)).astype(float), lam, link, steps)
        te = obs & (fold == f)
        L[te] = cell_ll(a[:, None] + b[None, :], Yz, link)[te]
    return L


def draw(p, obs, rng):
    return np.where(obs, (rng.random(p.shape) < p).astype(float), np.nan)


def verdict(T, null_logit, null_hazard):
    above, below = T > np.percentile(null_logit, 95), T < np.percentile(null_hazard, 5)
    return {(True, False): "hazard", (False, True): "logit", (False, False): "cannot tell", (True, True): "neither"}[bool(above), bool(below)]


def link_test(Y, sims=200, seed=0, grid=GRID):
    """Held-out log-likelihood per cell of the two links (ridge per link from the grid), T = hazard - logit, and T on matrices
    simulated from each fitted model with the ridges fixed."""
    obs, fold = ~np.isnan(Y), folds(Y)
    n = obs.sum()
    by = {l: {lam: cv_ll(Y, obs, fold, lam, l) for lam in grid} for l in LINKS}
    lam = {l: max(by[l], key=lambda k: by[l][k].sum()) for l in LINKS}
    L = {l: by[l][lam[l]] for l in LINKS}
    D = L["hazard"] - L["logit"]
    per_fold = np.array([D[obs & (fold == f)].sum() / (obs & (fold == f)).sum() for f in range(5)])
    solved = np.nansum(Y, 0)
    info = (solved > 0) & (solved < obs.sum(0))
    P = {l: full(Y, lam[l], l) for l in LINKS}
    p = {l: prob(P[l][0][:, None] + P[l][1][None, :], l) for l in LINKS}
    rng = np.random.default_rng(seed)
    null = {l: [] for l in LINKS}
    for truth in LINKS:
        for _ in range(sims):
            Z = draw(p[truth], obs, rng)
            null[truth].append(float((cv_ll(Z, obs, fold, lam["hazard"], "hazard") - cv_ll(Z, obs, fold, lam["logit"], "logit"))[obs].sum() / n))
    T = float(D[obs].sum() / n)
    q = lambda v: {"mean": round(float(np.mean(v)), 6), "p5": round(float(np.percentile(v, 5)), 6), "p95": round(float(np.percentile(v, 95)), 6), "min": round(float(min(v)), 6), "max": round(float(max(v)), 6)}
    power = {"hazard_truth_selected": round(float(np.mean(np.array(null["hazard"]) > np.percentile(null["logit"], 95))), 3),
             "logit_truth_selected": round(float(np.mean(np.array(null["logit"]) < np.percentile(null["hazard"], 5))), 3)}
    return {"arms": Y.shape[0], "problems": Y.shape[1], "cells": int(n), "ridge": lam,
            "ll_per_cell": {l: round(float(L[l][obs].sum() / n), 5) for l in LINKS},
            "ll_per_cell_by_ridge": {l: {str(k): round(float(v[obs].sum() / n), 5) for k, v in by[l].items()} for l in LINKS},
            "T_hazard_minus_logit": round(T, 6), "T_per_fold": [round(float(x), 6) for x in per_fold],
            "T_standard_error_over_folds": round(float(per_fold.std(ddof=1) / 5 ** 0.5), 6),
            "informative_problems": int(info.sum()), "T_informative_problems_per_cell": round(float(D[:, info][obs[:, info]].sum() / obs[:, info].sum()), 6),
            "T_uninformative_problems_per_cell": round(float(D[:, ~info][obs[:, ~info]].sum() / max(1, obs[:, ~info].sum())), 6),
            "sims": sims, "T_null_logit_truth": q(null["logit"]), "T_null_hazard_truth": q(null["hazard"]),
            "verdict": verdict(T, null["logit"], null["hazard"]) if min(power.values()) >= 0.8 else "cannot tell", "power_at_this_size": power}, lam, P, p


def mirror_check(Y, lam_logit, p_logit, sims=50, seed=1):
    """Post hoc (not in the spec): held-out fit of the mirrored hazard link, log(-log(1 - p)) = a + b, against logit, with the
    logit-simulated null. Tells whether the data lean away from the hazard link past the logit link."""
    obs, fold = ~np.isnan(Y), folds(Y)
    by = {lam: float(cv_ll(Y, obs, fold, lam, "mirror")[obs].sum() / obs.sum()) for lam in GRID}
    lam = max(by, key=by.get)
    T = lambda Z: float((cv_ll(Z, obs, fold, lam, "mirror") - cv_ll(Z, obs, fold, lam_logit, "logit"))[obs].sum() / obs.sum())
    rng = np.random.default_rng(seed)
    null = [T(draw(p_logit, obs, rng)) for _ in range(sims)]
    return {"ridge": lam, "ll_per_cell": round(by[lam], 5), "T_mirror_minus_logit": round(T(Y), 6), "sims": sims,
            "T_null_logit_truth": {"mean": round(float(np.mean(null)), 6), "p5": round(float(np.percentile(null, 5)), 6), "p95": round(float(np.percentile(null, 95)), 6)}}


# ---------- H2: is the shift the same at every difficulty ----------
def groups(Yrest, lam, link):
    """Three groups of problems (0 hardest) holding equal thirds of the wrong cells of the arms in Yrest, sorted by their b."""
    b = full(Yrest, lam, link)[1]
    wrong = (Yrest == 0).sum(0)
    order = np.argsort(b, kind="stable")
    cum = np.cumsum(wrong[order])
    g = np.empty(len(b), int)
    g[order] = np.minimum(2, (3 * (cum - wrong[order] / 2) / cum[-1]).astype(int))
    return b, g


def group_shifts(y, ref, b, g, link, boot=False):
    """Shift of y against ref (ability difference, b fixed) inside each group; with boot, also (BOOT,) draws per group."""
    out, draws = [], []
    for k in range(3):
        m = g == k
        yk, rk = np.atleast_2d(y)[:, m], np.atleast_2d(ref)[:, m]
        out.append(ability(yk, b[m], link) - ability(rk, b[m], link))
        if boot:
            w = R.boot(int(m.sum()))[:BOOT]
            draws.append(ability(yk, b[m], link, w) - ability(rk, b[m], link, w))
    return (np.array(out), np.array(draws)) if boot else np.array(out)


def constancy(V, ind, lam, p, sims=100, seed=0):
    """Per method and link: the shift per difficulty group, hardest minus easiest, and that statistic on matrices simulated
    from the link's fitted model (where the shift is constant by construction)."""
    rest = [n for n in ind if n not in HELD]
    rng = np.random.default_rng(seed)
    out = {}
    for link in LINKS:
        b, g = groups(np.vstack([V[n] for n in rest]), lam[link], link)
        ref = np.vstack([V[n] for n in R.BASE4])
        null = {m: [] for m in METHODS}
        obs = ~np.isnan(np.vstack([V[n] for n in ind]))
        for _ in range(sims):
            Z = dict(zip(ind, draw(p[link], obs, rng)))
            bs, gs = groups(np.vstack([Z[n] for n in rest]), lam[link], link)
            zref = np.vstack([Z[n] for n in R.BASE4])
            for m, arms in METHODS.items():
                s = group_shifts(np.vstack([Z[n] for n in arms]), zref, bs, gs, link)
                null[m].append(s[0] - s[2])
        res = {"groups": {"problems": [int((g == k).sum()) for k in range(3)], "wrong_cells_of_the_rest_arms": [int((np.vstack([V[n] for n in rest])[:, g == k] == 0).sum()) for k in range(3)],
                          "rest_arms": len(rest), "pooled_base_right_share": [round(float(np.nanmean(ref[:, g == k])), 3) for k in range(3)]}}
        for m, arms in METHODS.items():
            s, d = group_shifts(np.vstack([V[n] for n in arms]), ref, b, g, link, boot=True)
            lo, hi = np.percentile(null[m], [2.5, 97.5])
            stat = float(s[0] - s[2])
            res[m] = {"shift_hard_mid_easy": [round(float(x), 3) for x in s],
                      "shift_interval95": [[round(float(x), 3) for x in np.percentile(d[k], [2.5, 97.5])] for k in range(3)],
                      "hard_minus_easy": round(stat, 3), "hard_minus_easy_boot95": [round(float(x), 3) for x in np.percentile(d[0] - d[2], [2.5, 97.5])],
                      "null_constant_shift": {"mean": round(float(np.mean(null[m])), 3), "p2.5": round(float(lo), 3), "p97.5": round(float(hi), 3), "sims": sims},
                      "outside_null95": bool(stat < lo or stat > hi)}
            if link == "hazard":
                res[m]["hazard_ratio_hard_mid_easy"] = [round(float(np.exp(-x)), 3) for x in s]
        out[link] = res
    return out


# ---------- table ----------
def table(V, ind, b):
    """Every row of the rate table: logit shift and hazard ratio against the pooled 4 base + cue samples."""
    rate = {r["arm"]: r for r in json.loads((R.OUT / "math500-01" / "table.json").read_text())}
    fam = {"base_cue": (np.vstack([V[n] for n in R.BASE4]), R.day1_3("base_cue")[0]), "rl_plain": (np.vstack([V[n] for n in R.RL4]), R.day1_3("rl")[0])}
    vec = {n: V[n] for n in ind} | {"base_cue_tie_short": V["base_tie_short"], "base_cue_pooled4": fam["base_cue"][0], "rl_plain_pooled4": fam["rl_plain"][0]}
    for f, (_, D) in fam.items():
        vec |= {f"{f}_restart": D["restart"], f"{f}_vote4_restart": D["vote4_restart"]} | {f"{f}_vote{k}": D[f"vote{k}"] for k in (2, 3, 4)}
    W = R.boot(500)
    rows = []
    ab = {l: {n: (ability(y, b[l], l), ability(y, b[l], l, W)) for n, y in vec.items()} for l in LINKS}
    for n, y in vec.items():
        row = {"arm": n, "what": rate[n]["what"] if n in rate else n.replace("_pooled4", ", 4 samples pooled"), "right": round(R.acc(y) * 500, 1),
               "tokens_per_problem": rate[n]["tokens_per_problem"] if n in rate else None}
        for l in LINKS:
            d, dB = ab[l][n][0] - ab[l]["base_cue_pooled4"][0], ab[l][n][1] - ab[l]["base_cue_pooled4"][1]
            if l == "logit":
                row |= {"shift_logits": round(d, 3), "shift_logits_interval95": [round(float(x), 3) for x in np.percentile(dB, [2.5, 97.5])]}
            else:
                row |= {"log_hazard_ratio": round(-d, 3), "hazard_ratio": round(math.exp(-d), 3),
                        "hazard_ratio_interval95": [round(float(x), 3) for x in np.percentile(np.exp(-dB), [2.5, 97.5])]}
        own = next((f for f in fam if n.startswith(f + "_") and ("vote" in n or "restart" in n or "tie" in n)), None)
        if own:
            ref = f"{own}_s0" if n.endswith("_restart") and "vote" not in n else f"{own}_pooled4"
            dB = ab["hazard"][n][1] - ab["hazard"][ref][1]
            row |= {"hazard_ratio_vs_own_single": round(math.exp(-(ab["hazard"][n][0] - ab["hazard"][ref][0])), 3),
                    "hazard_ratio_vs_own_single_interval95": [round(float(x), 3) for x in np.percentile(np.exp(-dB), [2.5, 97.5])]}
        rows.append(row)
    rows.sort(key=lambda r: r["hazard_ratio"])
    md = ["| Method | Right of 500 | Hazard ratio against base + cue [95 %] | Hazard ratio against its own single sample [95 %] | Logit shift [95 %] | Tokens per problem |", "|---|---|---|---|---|---|"]
    for r in rows:
        own = f"{r['hazard_ratio_vs_own_single']:.2f} [{r['hazard_ratio_vs_own_single_interval95'][0]:.2f}, {r['hazard_ratio_vs_own_single_interval95'][1]:.2f}]" if "hazard_ratio_vs_own_single" in r else ""
        md.append(f"| {r['what']} | {r['right']:g} | {r['hazard_ratio']:.2f} [{r['hazard_ratio_interval95'][0]:.2f}, {r['hazard_ratio_interval95'][1]:.2f}] | {own} | "
                  f"{r['shift_logits']:+.2f} [{r['shift_logits_interval95'][0]:+.2f}, {r['shift_logits_interval95'][1]:+.2f}] | {r['tokens_per_problem'] or ''} |")
    return rows, md, ab


def theta(ab):
    out = {}
    for l in LINKS:
        a = {n: v[0] for n, v in ab[l].items()}
        a0, a1 = a["base_cue_pooled4"], a["rl_cue"]
        floor = float(np.std([a[n] for n in R.BASE4], ddof=1))
        pts = {t: a[f"theta{t}_cue"] - a0 for t in (0.25, 0.5, 0.75, 1.25, 1.5)} | {1.0: a1 - a0}
        out[l] = {"noise_floor_sd_of_4_base_samples": round(floor, 3),
                  "shift_by_theta": {str(t): {"shift": round(s, 3), "share_of_theta_1": round(s / (a1 - a0), 3), "minus_linear": round(s - t * (a1 - a0), 3)} for t, s in sorted(pts.items())},
                  "theta_0.5_off_the_line_in_noise_sd": round((pts[0.5] - 0.5 * (a1 - a0)) / floor, 1), "theta_0.25_off_the_line_in_noise_sd": round((pts[0.25] - 0.25 * (a1 - a0)) / floor, 1)}
        if l == "hazard":
            out[l]["hazard_ratio_by_theta"] = {str(t): round(math.exp(-s), 3) for t, s in sorted(pts.items())}
    return out


# ---------- H4 ----------
def ranks(x):
    u, inv, cnt = np.unique(x, return_inverse=True, return_counts=True)
    return (np.cumsum(cnt) - (cnt - 1) / 2)[inv]


def spearman(x, y):
    return float(np.corrcoef(ranks(x), ranks(y))[0, 1])


def day1_rows(model):
    rows = [json.loads(l) for l in (X.STUDY / "results" / "day1_3" / f"math500_{model}-01" / "rows.jsonl").read_text().splitlines()]
    return [r for r in rows if r["attempt"] == 0]


def chain_length(V, ind, lam, seed=0):
    """-b_i (log of the fitted work, hazard link, b fitted without the family's own samples) against the log mean tokens of the family's right answers."""
    rng = np.random.default_rng(seed)
    out = {}
    for model, fam in (("base_cue", R.BASE4), ("rl", R.RL4)):
        rest = np.vstack([V[n] for n in ind if n not in fam])
        b = full(rest, lam, "hazard")[1]
        tok = np.full(500, np.nan)
        rows = day1_rows(model)
        for i in range(500):
            t = [r["n_new"] for r in rows if r["problem_index"] == i and r["score_v3"] == 1]
            if t:
                tok[i] = np.mean(t)
        ok = ~np.isnan(tok)
        x, y = np.log(tok[ok]), -b[ok]
        rho = spearman(x, y)
        null = np.array([spearman(rng.permutation(x), y) for _ in range(2000)])
        share = np.nanmean(rest, 0)
        inf = ok & (share > 0) & (share < 1)
        xi, yi = np.log(tok[inf]), -b[inf]
        slope = lambda xx, yy: float(np.polyfit(xx, yy, 1)[0])
        bs = [slope(xi[j], yi[j]) for j in (rng.integers(0, len(xi), len(xi)) for _ in range(2000))]
        a = ability(np.vstack([V[n] for n in fam]), b, "hazard")
        per1k = np.exp(-(a + b[inf])) / (tok[inf] / 1000)           # implied slips per 1,000 tokens of a right answer
        out[model] = {"problems_with_a_right_sample": int(ok.sum()), "spearman": round(rho, 3), "shuffled_null_p2.5_p97.5": [round(float(v), 3) for v in np.percentile(null, [2.5, 97.5])],
                      "outside_shuffled_null": bool(rho > np.percentile(null, 97.5) or rho < np.percentile(null, 2.5)),
                      "informative_problems": int(inf.sum()), "slope_of_log_work_on_log_tokens": round(slope(xi, yi), 3), "slope_interval95": [round(float(v), 3) for v in np.percentile(bs, [2.5, 97.5])],
                      "implied_slips_per_1000_tokens_by_token_tercile_short_to_long": [round(float(np.median(per1k[q])), 4) for q in np.array_split(np.argsort(tok[inf]), 3)],
                      "median_tokens_by_token_tercile": [round(float(np.median(tok[inf][q]))) for q in np.array_split(np.argsort(tok[inf]), 3)],
                      "fitted_work_ratio_longest_over_shortest_tercile": round(float(np.exp(np.mean(yi[np.array_split(np.argsort(xi), 3)[2]]) - np.mean(yi[np.array_split(np.argsort(xi), 3)[0]]))), 2)}
    return out


def dispersion_stat(K, p):
    return float(((K - 4 * p) ** 2).sum() / (4 * p * (1 - p)).sum())


def family_p(Z, ind, fam, lam, link):
    """Per-problem success probability of a family's samples: b from the other arms, a from the family's pooled samples."""
    b = full(np.vstack([Z[n] for n in ind if n not in fam]), lam, link)[1]
    return prob(ability(np.vstack([Z[n] for n in fam]), b, link) + b, link)


def dispersion(V, ind, lam, p, sims=200, seed=0):
    rng = np.random.default_rng(seed)
    votes = {"base_cue": V["base_vote4"], "rl_plain": V["rl_vote4"]}
    fams = {"base_cue": R.BASE4, "rl_plain": R.RL4}
    K = {f: np.vstack([V[n] for n in arms]).sum(0) for f, arms in fams.items()}
    g = np.array([np.concatenate([votes[f][K[f] == k] for f in fams]).mean() for k in range(5)])      # share of votes right at k right samples
    binom = lambda q: np.array([math.comb(4, k) * q ** k * (1 - q) ** (4 - k) for k in range(5)])    # (5, n)
    obs = ~np.isnan(np.vstack([V[n] for n in ind]))
    out = {"vote_right_share_by_right_samples_0_to_4": [round(float(x), 3) for x in g]}
    for link in LINKS:
        res = {}
        null = {f: [] for f in fams}

        def stats(k, q, vote_right):
            """D, problems with 0 of 4 right minus the binomial expectation, vote right minus the independent-slip prediction."""
            B = binom(q)
            return dispersion_stat(k, q), float((k == 0).sum() - B[0].sum()), float(vote_right - (B.T @ g).sum()), B
        for _ in range(sims):
            Z = dict(zip(ind, draw(p[link], obs, rng)))
            for f, arms in fams.items():
                k = np.vstack([Z[n] for n in arms]).sum(0)
                null[f].append(stats(k, family_p(Z, ind, arms, lam[link], link), g[k.astype(int)].sum())[:3])
        for f, arms in fams.items():
            D, zero, vote, B = stats(K[f], family_p(V, ind, arms, lam[link], link), votes[f].sum())
            nl = np.array(null[f])
            res[f] = {"D": round(D, 3), "D_null_independent_cells": {"mean": round(float(nl[:, 0].mean()), 3), "p95": round(float(np.percentile(nl[:, 0], 95)), 3), "max": round(float(nl[:, 0].max()), 3), "sims": sims},
                      "over_dispersed": bool(D > np.percentile(nl[:, 0], 95)),
                      "problems_by_right_samples_0_to_4": {"observed": [int((K[f] == k).sum()) for k in range(5)], "binomial_at_fitted_p": [round(float(x), 1) for x in B.sum(1)]},
                      "zero_of_4_minus_binomial": {"observed": round(zero, 1), "null_mean": round(float(nl[:, 1].mean()), 1), "null_p95": round(float(np.percentile(nl[:, 1], 95)), 1), "above_null95": bool(zero > np.percentile(nl[:, 1], 95))},
                      "vote4": {"observed": int(votes[f].sum()), "predicted_independent_slips": round(float(votes[f].sum() - vote), 1), "observed_minus_predicted": round(vote, 1),
                                "null_mean": round(float(nl[:, 2].mean()), 1), "null_p5": round(float(np.percentile(nl[:, 2], 5)), 1), "null_sd": round(float(nl[:, 2].std()), 1),
                                "below_null5": bool(vote < np.percentile(nl[:, 2], 5))}}
        out[link] = res
    return out


def examples(V, ind, lam):
    q = family_p(V, ind, R.BASE4, lam, "hazard")
    K = np.vstack([V[n] for n in R.BASE4]).sum(0)
    fits = int(np.argmin(np.where(K == 3, abs(q - 0.75), 9)))
    off = int(np.argmax(np.where(K == 0, q, -1)))
    rows = day1_rows("base_cue")
    return {key: {"problem_index": i, "p_fitted_from_the_other_32_arms": round(float(q[i]), 3), "right_of_4": int(K[i]),
                  "share_of_other_arms_right": round(float(np.nanmean([V[n][i] for n in ind if n not in R.BASE4])), 3),
                  "rows": [{k: r[k] for k in ("sample", "n_new", "cap_hit", "extracted_v3", "score_v3", "gold")} for r in rows if r["problem_index"] == i]}
            for key, i in (("binomial_fits_base_3_of_4_at_p_0.75", fits), ("binomial_fails_base_0_of_4_at_the_highest_p", off))}


def head():
    return subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()


def run_json(folder, cmd, inputs):
    (folder / "run.json").write_text(json.dumps({"commit": head(), "commit_note": "HEAD when it ran; analysis/hazard.py is committed in the commit that adds this file",
                                                 "command": f"uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.hazard {cmd}",
                                                 "job_id": None, "gpu": "none (laptop, numpy)", "spec": "studies/rlneurons/specs/SPEC_hazard.md", "inputs": inputs}, indent=1) + "\n")


def cmd_fit():
    V, ind = R.load("math500")
    Y = np.vstack([V[n] for n in ind])
    obs = ~np.isnan(Y)
    lt, lam, P, p = link_test(Y)
    conv = {l: round(float((cv_ll(Y, obs, folds(Y), lam[l], l, steps=800) - cv_ll(Y, obs, folds(Y), lam[l], l))[obs].sum() / obs.sum()), 6) for l in LINKS}
    b = {l: P[l][1] for l in LINKS}
    rows, md, ab = table(V, ind, b)
    out = OUT / "math500-01"
    out.mkdir(parents=True, exist_ok=True)
    readout = {"set": "math500", "H1_link": lt | {"ll_change_per_cell_when_steps_are_doubled": conv, "post_hoc_mirror_link": mirror_check(Y, lam["logit"], p["logit"])},
               "H2_constancy_over_difficulty": constancy(V, ind, lam, p), "H2b_theta": theta(ab),
               "H4a_chain_length": chain_length(V, ind, lam["hazard"]), "H4b_independent_slips": dispersion(V, ind, lam, p),
               "first_wrong_steps_per_1000_tokens_result_855858": {"rl": 0.015, "base": 0.038, "ratio": round(0.015 / 0.038, 3)}}
    (out / "readout.json").write_text(json.dumps(readout, indent=1) + "\n")
    (out / "table.json").write_text(json.dumps(rows, indent=1) + "\n")
    (out / "table.md").write_text("\n".join(md) + "\n")
    (out / "examples.json").write_text(json.dumps(examples(V, ind, lam["hazard"]), indent=1) + "\n")
    run_json(out, "fit", "results/axis/math500-01/vectors.json; results/day1_3/math500_{base_cue,rl}-01/{rows.jsonl,readout.json}; results/rate/math500-01/table.json (tokens)")
    print(json.dumps(readout, indent=1))
    print("\n".join(md))


# ---------- H3: transfer ----------
def ridge(Y, link):
    obs, fold = ~np.isnan(Y), folds(Y)
    return max(GRID, key=lambda lam: cv_ll(Y, obs, fold, lam, link)[obs].sum())


def setup():
    """Both sets, the ridges per link, MATH-500 b per link, and the pooled vectors of the reference and of the 5 arms on both sets."""
    V5, ind5 = R.load("math500")
    V3, ind3 = R.load("hard328")
    lam5 = {l: ridge(np.vstack([V5[n] for n in ind5]), l) for l in LINKS}
    lam3 = {l: ridge(np.vstack([V3[n] for n in ind3 if n != "base_cue_rerun"]), l) for l in LINKS}
    b5 = {l: full(np.vstack([V5[n] for n in ind5]), lam5[l], l)[1] for l in LINKS}
    S5 = {"ref": np.vstack([V5[n] for n in R.BASE4])} | {a: np.vstack([V5[n] for n in v]) for a, v in R.BOTH.items()}
    S3 = {"ref": np.vstack([V3["base_cue"], V3["base_cue_rerun"]])} | {a: V3[a] for a in R.BOTH}
    return V5, V3, lam5, lam3, b5, S5, S3


def transfer(b5, S5, S3, extra3, lam3, link):
    """rate.transfer with a link: leave one arm out of the set-2 item fit and of the calibration of c."""
    arms = [a for a in S5 if a != "ref"]
    d5 = {a: ability(S5[a], b5, link) - ability(S5["ref"], b5, link) for a in arms}
    n3 = np.atleast_2d(S3["ref"]).shape[1]
    out = {}
    for j in arms:
        b3 = full(np.vstack([S3[a] for a in S3 if a != j] + extra3), lam3, link)[1]
        a_ref = ability(S3["ref"], b3, link)
        oth = [a for a in arms if a != j]
        d3 = np.array([ability(S3[a], b3, link) - a_ref for a in oth])
        x = np.array([d5[a] for a in oth])
        c = float(x @ d3 / (x @ x))
        r5, r3 = R.acc(S5["ref"]), R.acc(S3["ref"])
        out[j] = {"observed": R.acc(S3[j]) * n3, "shift_set1": d5[j], "c": c, "c1": float(prob(a_ref + d5[j] + b3, link).sum()), "cal": float(prob(a_ref + c * d5[j] + b3, link).sum()),
                  "P": n3 * (r3 + R.acc(S5[j]) - r5), "MH": n3 * r3 ** (math.log(R.acc(S5[j])) / math.log(r5))}
    mae = {r: float(np.mean([abs(v[r] - v["observed"]) for v in out.values()])) for r in ("c1", "cal", "P", "MH")}
    return out, mae


def cmd_transfer():
    V5, V3, lam5, lam3, b5, S5, S3 = setup()
    r = lambda x: round(float(x), 2)
    res = {"reference": "pooled base + cue (4 samples on MATH-500: 410.5 of 500; 2 runs on hard328: 162 of 328)", "ridge_math500": lam5, "ridge_hard328": lam3,
           "rules": "cal: link shift x c (c fitted on the other test arms); c1: the same shift, c = 1; P: same point gain; MH: acc328 = ref328 ^ (log acc500 / log ref500), no item model",
           "rerun_noise_problems": 4.0, "binomial_sd_one_cell": 5.73}
    for link in LINKS:
        rows, mae = transfer(b5[link], S5, S3, [V3["base_plain"]], lam3[link], link)
        res[link] = {"mean_abs_error_problems": {k: r(v) for k, v in mae.items()}, "rows": {a: {k: r(v) for k, v in row.items()} for a, row in rows.items()}}
    rate = json.loads((R.OUT / "transfer-01" / "readout.json").read_text())["mean_abs_error_problems"]
    res["logit_reproduces_rate_transfer"] = {"rate_Lc": rate["Lc"], "rate_L1": rate["L1"], "here_cal": res["logit"]["mean_abs_error_problems"]["cal"], "here_c1": res["logit"]["mean_abs_error_problems"]["c1"]}
    assert lam5["logit"] == R.LAM["math500"] and lam3["logit"] == R.LAM["hard328"], (lam5, lam3)
    assert abs(res["logit"]["mean_abs_error_problems"]["cal"] - rate["Lc"]) < 0.05 and abs(res["logit"]["mean_abs_error_problems"]["c1"] - rate["L1"]) < 0.05, res["logit_reproduces_rate_transfer"]
    (OUT / "transfer-01").mkdir(parents=True, exist_ok=True)
    (OUT / "transfer-01" / "readout.json").write_text(json.dumps(res, indent=1) + "\n")
    run_json(OUT / "transfer-01", "transfer", "results/axis/{math500,hard328}-01/vectors.json; results/rate/transfer-01/readout.json (check)")
    print(json.dumps(res, indent=1))


# ---------- predictions ----------
def cmd_predict():
    path = OUT / "predict-01" / "predictions.json"
    assert not path.exists(), "predictions are filed once"
    V5, V3, lam5, lam3, b5, S5, S3 = setup()
    link, rng = "hazard", np.random.default_rng(0)
    b5, lam3 = b5[link], lam3[link]
    b3 = full(np.vstack([S3[a] for a in S3] + [V3["base_plain"]]), lam3, link)[1]
    W5 = R.boot(500)
    a5 = lambda y, w=None: ability(y, b5, link, w)
    sh = lambda y, ref: (a5(y) - a5(ref), a5(y, W5) - a5(ref, W5))
    d5 = np.array([a5(S5[a]) - a5(S5["ref"]) for a in R.BOTH])
    d3 = np.array([ability(S3[a], b3, link) - ability(S3["ref"], b3, link) for a in R.BOTH])
    c = float(d5 @ d3 / (d5 @ d5))
    c_loo = [float(np.delete(d5, k) @ np.delete(d3, k) / (np.delete(d5, k) @ np.delete(d5, k))) for k in range(len(d5))]
    DB, DR = R.day1_3("base_cue")[0], R.day1_3("rl")[0]
    base, rl = S5["ref"], S5["rl_plain"]

    def cell328(name, ref3, d, dB, acc5, ref5, status="prediction", idx=slice(None), note=""):
        ref3 = np.atleast_2d(ref3)
        a_ref = ability(ref3, b3, link)
        k = ref3.shape[0]
        tot = (rng.random((BOOT, k, 328)) < prob(a_ref + b3, link)).sum(1).astype(float)          # parametric redraw of the reference
        a_refB = solve(tot, k - tot, b3, link)
        draws = (rng.random((BOOT, 328)) < prob(a_refB[:, None] + (rng.choice(c_loo, BOOT) * dB)[:, None] + b3[None, :], link))[:, idx].sum(1)
        n, r3 = len(b3[idx]), R.acc(ref3[:, idx])
        return {"cell": name, "set": "hard328" if n == 328 else "hard328 subset", "n": n, "status": status, "note": note, "log_hazard_ratio_math500": round(float(-d), 3), "hazard_ratio_math500": round(math.exp(-d), 3),
                "predicted_right": round(float(prob(a_ref + c * d + b3, link)[idx].sum()), 1), "interval80": [float(np.percentile(draws, 10)), float(np.percentile(draws, 90))],
                "c1_same_hazard_ratio": round(float(prob(a_ref + d + b3, link)[idx].sum()), 1), "MH_no_item_model": round(n * r3 ** (math.log(acc5) / math.log(ref5)), 1),
                "baseline_point": round(n * (r3 + acc5 - ref5), 1), "reference_right": round(r3 * n, 1)}

    cells = []
    d, dB = sh(DB["vote4_restart"], base)
    cells.append(cell328("base + cue, vote over 4 after restart", S3["ref"], d, dB, R.acc(DB["vote4_restart"]), R.acc(base)))
    d, dB = sh(DR["vote4_restart"], rl)
    cells.append(cell328("RL plain, vote over 4 after restart", V3["rl_plain"], d, dB, R.acc(DR["vote4_restart"]), R.acc(rl)))
    d, dB = sh(V5["shots_rl"], base)
    cells.append(cell328("base + cue + 3 RL-written solved problems (shots_rl)", S3["ref"], d, dB, R.acc(V5["shots_rl"]), R.acc(base),
                         note="shift of the first draw of examples (435 of 497); the second draw had 404 (rate section), known when this was filed; the rule's output is not adjusted"))
    d, dB = sh(V5["top8_plain"], base)
    cells.append(cell328("base + top 8 directions, cue", S3["ref"], d, dB, R.acc(V5["top8_plain"]), R.acc(base), note="shift of top8_plain (no cue cell on MATH-500)"))
    known = "computed after the observation"
    ids = json.loads((X.OUT / "hard328-01" / "vectors.json").read_text())["problem_indices"]
    sub = set(json.loads(X.show(*R.PARTIAL))["problem_indices"])
    idx = np.array([i in sub for i in ids])
    d, dB = sh(DB["vote4"], base)
    cells.append(cell328("base + cue, vote over 4, no restart (sameraslan's run, result-1dedfe)", S3["ref"], d, dB, R.acc(DB["vote4"]), R.acc(base), known, note="observed 179, known to the author"))
    dv, dvB = d, dB
    d, dB = sh(DR["vote4"], rl)
    cells.append(cell328(f"RL plain, vote over 4, no restart, on the {idx.sum()} problems that finished (result-1dedfe)", V3["rl_plain"], d, dB, R.acc(DR["vote4"]), R.acc(rl), known, idx, "observed 161, known to the author"))
    aS, aSB = a5(V5["sft1_cue"]), a5(V5["sft1_cue"], W5)
    draws = (rng.random((BOOT, 500)) < prob((aSB + dvB)[:, None] + b5[None, :], link)).sum(1)
    cells.append({"cell": "Think-SFT cue, vote over 4", "set": "math500", "n": 500, "status": "prediction", "note": "hazard ability of sft1_cue plus the base vote-over-4 log hazard ratio",
                  "log_hazard_ratio_math500": round(float(-dv), 3), "hazard_ratio_math500": round(math.exp(-dv), 3), "predicted_right": round(float(prob(aS + dv + b5, link).sum()), 1),
                  "interval80": [float(np.percentile(draws, 10)), float(np.percentile(draws, 90))],
                  "MH_no_item_model": round(500 * R.acc(V5["sft1_cue"]) ** (math.log(R.acc(DB["vote4"])) / math.log(R.acc(base))), 1),
                  "baseline_point": round(float(np.nansum(V5["sft1_cue"]) + 500 * (R.acc(DB["vote4"]) - R.acc(base))), 1)})
    out = {"filed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "code_commit_parent": head(),
           "rule": "Hc: sum_i exp(-exp(-(a_ref328 + c d + b_i))), d = the MATH-500 hazard shift (minus log hazard ratio); specs/SPEC_hazard.md",
           "ridge_hard328": lam3, "c": round(c, 3), "c_leave_one_out": [round(x, 3) for x in c_loo],
           "calibration_arms": {a: {"log_hazard_ratio_math500": round(float(-x), 3), "log_hazard_ratio_hard328": round(float(-y), 3)} for a, x, y in zip(R.BOTH, d5, d3)},
           "logit_predictions_for_the_same_cells": "results/rate/predict-01/predictions.json, predict-02/predictions.json", "cells": cells}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=1) + "\n")
    run_json(path.parent, "predict", "results/axis/{math500,hard328}-01/vectors.json; results/day1_3/math500_{base_cue,rl}-01")
    print(json.dumps(out, indent=1))


# cell name -> (observed right, where it was read); filled in after predict-01 was pushed
OBSERVED = dict(R.OBSERVED)


def cmd_score():
    logit = {c["cell"]: c for nn in (1, 2) for c in json.loads((R.OUT / f"predict-0{nn}" / "predictions.json").read_text())["cells"]}
    filed = json.loads((OUT / "predict-01" / "predictions.json").read_text())
    rows = []
    for c in filed["cells"]:
        row = {"cell": c["cell"], "set": c["set"], "status": c["status"], "hazard_Hc": c["predicted_right"], "hazard_interval80": c["interval80"], "hazard_c1": c.get("c1_same_hazard_ratio"),
               "hazard_MH": c["MH_no_item_model"], "logit_Lc": logit[c["cell"]]["predicted_right"], "logit_interval80": logit[c["cell"]]["interval80"], "point": c["baseline_point"], "observed": None}
        if c["cell"] in OBSERVED:
            obs, src = OBSERVED[c["cell"]]
            row |= {"observed": obs, "source": src, "error": {k: round(row[k] - obs, 1) for k in ("hazard_Hc", "hazard_c1", "hazard_MH", "logit_Lc", "point") if row[k] is not None},
                    "inside_hazard_interval80": bool(c["interval80"][0] <= obs <= c["interval80"][1])}
        rows.append(row)
    done = [r for r in rows if r["observed"] is not None]
    blind = [r for r in done if r["status"] == "prediction"]
    mae = lambda rs: {k: round(float(np.mean([abs(r["error"][k]) for r in rs if k in r["error"]])), 2) for k in ("hazard_Hc", "hazard_c1", "hazard_MH", "logit_Lc", "point")} if rs else None
    out = {"filed_utc": filed["filed_utc"], "scored": len(done), "scored_filed_before_the_observation": len(blind), "not_finished": len(rows) - len(done),
           "mean_abs_error_problems_all_scored": mae(done), "mean_abs_error_problems_filed_before": mae(blind), "cells": rows}
    (OUT / "scored-01").mkdir(parents=True, exist_ok=True)
    (OUT / "scored-01" / "readout.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["fit", "transfer", "predict", "score"])
    {"fit": cmd_fit, "transfer": cmd_transfer, "predict": cmd_predict, "score": cmd_score}[ap.parse_args().cmd]()


if __name__ == "__main__":
    main()
