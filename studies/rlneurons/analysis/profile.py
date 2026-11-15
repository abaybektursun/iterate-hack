"""Do supervised fine-tuning and RL have opposite difficulty profiles? (specs/SPEC_profile.md, board idea-095c0d)
Error reduction of each arm against the pooled base + cue samples by difficulty bin, with difficulty defined without the
arms compared; the profile contrast of Think-SFT against RL with a same-arm and a one-axis noise floor; 2PL against Rasch
held out; unions; predictions for Think-SFT on hard328.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.profile fit|predict|score [--runs runs]

  fit      results/profile/math500-01/{readout.json,table.md,examples.json,run.json}
  predict  results/profile/predict-01/predictions.json (filed once, refuses to overwrite)
  score    results/profile/scored-01/readout.json (the filed predictions against OBSERVED)
"""
from __future__ import annotations

import argparse
import collections
import datetime
import itertools
import json
import pathlib

import numpy as np

from studies.rlneurons.analysis import axis as X
from studies.rlneurons.analysis import hazard as H
from studies.rlneurons.analysis import rate as R

OUT = X.STUDY / "results" / "profile"
LAM = R.LAM["math500"]
ARMS = {"rl_plain": R.RL4, "rl_cue": ["rl_cue"], "sft1_cue": ["sft1_cue"], "sft1_plain": ["sft1_plain"], "code_cue": ["code_cue"],
        "theta0.25_cue": ["theta0.25_cue"], "theta0.5_cue": ["theta0.5_cue"], "theta0.75_cue": ["theta0.75_cue"],
        "top8_plain": ["top8_plain"], "math30_cue": ["math30_cue"]} | {n: [n] for n in R.RL4}
WHAT = {"rl_plain": "RL plain, 4 samples pooled", "rl_cue": "RL, cue", "sft1_cue": "Think-SFT, cue", "sft1_plain": "Think-SFT, plain", "code_cue": "Code-RL 3.1, cue",
        "theta0.25_cue": "base + 0.25 (RL - base), cue", "theta0.5_cue": "base + 0.5 (RL - base), cue", "theta0.75_cue": "base + 0.75 (RL - base), cue",
        "top8_plain": "base + top 8 RL directions, plain", "math30_cue": "RL-Zero-Math 3.0, cue"} | {n: f"RL plain, sample {n[-1]}" for n in R.RL4}
HELD = set(R.BASE4) | {n for v in ARMS.values() for n in v}          # never used to define difficulty
BASE_LIKE = ["random_cue", "shots_base"]                             # base weights, cue, not the reference
BINS = {"level": ["level 5", "level 4", "level 3", "level 1-2"], "rest": ["hardest", "middle", "easiest"], "base": ["0-1 of 4", "2-3 of 4", "4 of 4"]}
sig = R.sig


def meta():
    return json.loads((X.STUDY / "data" / "profile" / "math500_meta_v1.json").read_text())


def err(V, names):
    """Wrong share per problem of the pooled vectors."""
    return 1 - np.nanmean(np.vstack([V[n] for n in names]), 0)


def designs(V, ind, level):
    """name -> list of (group index per problem, 0 = hardest; reference arm names). D-base has two splits of the base samples."""
    rest = [n for n in ind if n not in HELD]
    half = lambda s: np.minimum(2, np.nansum(np.vstack([V[n] for n in s + BASE_LIKE]), 0).astype(int) // 2)       # 0-1, 2-3, 4 right
    return {"level": [(np.array([{5: 0, 4: 1, 3: 2}.get(x, 3) for x in level]), R.BASE4)],
            "rest": [(H.groups(np.vstack([V[n] for n in rest]), LAM, "logit")[1], R.BASE4)],
            "base": [(half(R.BASE4[2:]), R.BASE4[:2]), (half(R.BASE4[:2]), R.BASE4[2:])]}


def wrong(V, names, design, w=None):
    """Wrong cells per sample in each bin, (K,), or (B, K) for bootstrap counts w; names None = the design's reference."""
    K = 1 + max(int(g.max()) for g, _ in design)
    tot = 0
    for g, ref in design:
        e = err(V, ref if names is None else names) * np.eye(K)[g].T                    # (K, n)
        tot = tot + (e.sum(1) if w is None else w @ e.T)
    return tot / len(design)


def contrast(wa, wb):
    """C: log wrong ratio A / B in the hardest bin minus the same in the easiest bin; < 0 = A relatively better on hard."""
    r = np.log((wa + 0.5) / (wb + 0.5))
    return r[..., 0] - r[..., -1]


def table(V, D, W):
    out = {}
    for d, design in D.items():
        ref, refB = wrong(V, None, design), wrong(V, None, design, W)
        rows = {"problems": [round(float(np.mean([(g == k).sum() for g, _ in design])), 1) for k in range(len(ref))], "reference_wrong": [round(float(x), 2) for x in ref]}
        for a, names in ARMS.items():
            w, wB = wrong(V, names, design), wrong(V, names, design, W)
            rows[a] = {"wrong": [round(float(x), 2) for x in w], "error_reduction": [round(float(x), 3) for x in 1 - w / ref],
                       "error_reduction_interval95": [[round(float(x), 3) for x in np.percentile(1 - wB[:, k] / refB[:, k], [2.5, 97.5])] for k in range(len(ref))]}
        out[d] = rows
    return out


def simulate(V, ind, p, rng, plant=None, k=1):
    """One matrix from the fitted Rasch model, as {arm: vector}. plant = (logits per problem): sft1_cue is drawn from them instead;
    k = number of sft1_cue samples (stacked under the names sft1_cue, sft1_cue#1, ...)."""
    obs = ~np.isnan(np.vstack([V[n] for n in ind]))
    Z = dict(zip(ind, H.draw(p, obs, rng)))
    q = p[ind.index("sft1_cue")] if plant is None else sig(plant)
    S = (rng.random((k, len(q))) < q).astype(float)
    return Z | {"sft1_cue": S[0]}, S


def h1(V, ind, D, level, W, p, sims=200, seed=0):
    """Profile contrast of Think-SFT cue against pooled RL plain, its bootstrap interval, and the two noise floors."""
    rng = np.random.default_rng(seed)
    null, ndiff = {d: [] for d in D}, {d: [] for d in D}
    for _ in range(sims):
        Z, _ = simulate(V, ind, p, rng)
        for d, design in designs(Z, ind, level).items():
            ws, wr = wrong(Z, ["sft1_cue"], design), wrong(Z, R.RL4, design)
            null[d].append(contrast(ws, wr))
            ndiff[d].append(ws - wr)
    out = {}
    for d, design in D.items():
        a, b = (lambda *w: wrong(V, ["sft1_cue"], design, *w)), (lambda *w: wrong(V, R.RL4, design, *w))
        c, cB = float(contrast(a(), b())), contrast(a(W), b(W))
        lo, hi = np.percentile(null[d], [2.5, 97.5])
        row = {"C_sft1_cue_vs_rl_plain": round(c, 3), "boot95": [round(float(x), 3) for x in np.percentile(cB, [2.5, 97.5])],
               "wrong_hardest_easiest": {"sft1_cue": [round(float(a()[k]), 2) for k in (0, -1)], "rl_plain": [round(float(b()[k]), 2) for k in (0, -1)],
                                         "reference": [round(float(wrong(V, None, design)[k]), 2) for k in (0, -1)]},
               "one_axis_null": {"mean": round(float(np.mean(null[d])), 3), "p2.5": round(float(lo), 3), "p97.5": round(float(hi), 3), "sd": round(float(np.std(null[d])), 3), "sims": sims},
               "outside_one_axis_null95": bool(c < lo or c > hi), "z_against_one_axis_null": round(float((c - np.mean(null[d])) / np.std(null[d])), 2),
               "wrong_sft1_cue_minus_rl_plain_by_bin": parts(a() - b(), np.array(ndiff[d]))}
        if d != "base":                 # D-base uses the base samples for its bins
            floor = {f: [round(float(contrast(wrong(V, [s], design), wrong(V, [t for t in fam if t != s], design))), 3) for s in fam] for f, fam in (("rl_plain", R.RL4), ("base_cue", R.BASE4))}
            row |= {"same_arm_one_sample_vs_other_three": floor, "exceeds_all_same_arm": bool(abs(c) > max(abs(x) for v in floor.values() for x in v))}
        out[d] = row
    return out


def parts(diff, null):
    """Per bin: Think-SFT cue wrong minus RL wrong per sample, the one-axis range, z, and the Think-SFT samples needed for |z| = 1.96
    at this difference (variance of the difference = RL's four samples + Think-SFT's k: sd_1^2 (0.2 + 0.8 / k))."""
    out = []
    for k in range(len(diff)):
        sd, mu = float(np.std(null[:, k])), float(np.mean(null[:, k]))
        need = (diff[k] - mu) ** 2 / 1.96 ** 2 / sd ** 2 - 0.2
        out.append({"difference": round(float(diff[k]), 2), "one_axis_p2.5_p97.5": [round(float(x), 2) for x in np.percentile(null[:, k], [2.5, 97.5])],
                    "z": round((float(diff[k]) - mu) / sd, 2), "think_sft_samples_needed": (int(np.ceil(0.8 / need)) if need > 0 else "more than any (RL's 4 samples limit it)")})
    return out


def caps(level):
    """Wrong cells per sample by level bin, split into cap hits (16,384 tokens, no answer) and finished answers."""
    g = np.array([{5: 0, 4: 1, 3: 2}.get(x, 3) for x in level])
    arms = {}
    for name, model in (("base + cue, 4 samples", "base_cue"), ("RL plain, 4 samples", "rl")):
        w, c = np.zeros((4, 500), bool), np.zeros((4, 500), bool)
        for r in H.day1_rows(model):
            w[r["sample"], r["problem_index"]], c[r["sample"], r["problem_index"]] = r["score_v3"] == 0, r["cap_hit"]
        arms[name] = (w, c)
    for name, cell in (("Think-SFT, cue", "sft1_cue"), ("Think-SFT, plain", "sft1_plain"), ("base + top 8 RL directions, plain", "top8_plain")):
        pp = json.loads((X.STUDY / "results" / "wsp1" / "full500" / f"{cell}-01" / "per_problem.json").read_text())
        arms[name] = (np.array([[r["score_v3"] == 0 for r in pp]]), np.array([[r["cap_hit"] for r in pp]]))
    return {"bins": BINS["level"]} | {name: {"wrong": [round(float(w[:, g == k].sum() / len(w)), 2) for k in range(4)],
                                             "wrong_cap_hit": [round(float((w & c)[:, g == k].sum() / len(w)), 2) for k in range(4)],
                                             "wrong_finished": [round(float((w & ~c)[:, g == k].sum() / len(w)), 2) for k in range(4)]} for name, (w, c) in arms.items()}


# ---------- H2: 2PL ----------
def fit2(Y, W, lam_b, lam_g, steps=400):
    """2PL: logit = a_j + (1 + g_j) b_i, ridge on b and g; the Adam loop of axis.fit."""
    P = [np.zeros(Y.shape[0]), np.zeros(Y.shape[1]), np.zeros(Y.shape[0])]
    Y0 = np.where(W > 0, Y, 0.0)
    m, v = [np.zeros_like(x) for x in P], [np.zeros_like(x) for x in P]
    for t in range(1, steps + 1):
        a, b, g = P
        Rz = W * (sig(a[:, None] + (1 + g)[:, None] * b[None, :]) - Y0)
        G = [Rz.sum(1), ((1 + g)[:, None] * Rz).sum(0) + lam_b * b, (Rz * b[None, :]).sum(1) + lam_g * g]
        for k in range(3):
            m[k] = 0.9 * m[k] + 0.1 * G[k]
            v[k] = 0.999 * v[k] + 0.001 * G[k] ** 2
            P[k] = P[k] - 0.1 * (m[k] / (1 - 0.9 ** t)) / ((v[k] / (1 - 0.999 ** t)) ** 0.5 + 1e-8)
    return P


def gain2(Y, grid=(3.0, 10.0, 30.0, 100.0, 300.0), steps=400):
    """Held-out log-likelihood per cell, 2PL minus Rasch, on the folds of axis.heldout; ridge on g picked on the same folds."""
    obs, fold = ~np.isnan(Y), H.folds(Y)
    Yz = np.where(obs, Y, 0.0)
    ll = lambda z, te: -(np.logaddexp(0, -z) * Yz + np.logaddexp(0, z) * (1 - Yz))[te].sum()
    one, two = 0.0, {lam: 0.0 for lam in grid}
    for f in range(5):
        tr, te = (obs & (fold != f)).astype(float), obs & (fold == f)
        one += ll(X.logit(X.fit(Y, tr, LAM)), te)
        for lam in grid:
            a, b, g = fit2(Y, tr, LAM, lam, steps)
            two[lam] += ll(a[:, None] + (1 + g)[:, None] * b[None, :], te)
    best = max(two, key=two.get)
    return {"ll_rasch": one / obs.sum(), "ll_2pl": two[best] / obs.sum(), "gain": (two[best] - one) / obs.sum(), "lam_g": best,
            "gain_by_ridge": {str(lam): round((x - one) / obs.sum(), 6) for lam, x in two.items()}}


def h2(V, ind, p, sims=20, seed=0):
    Y = np.vstack([V[n] for n in ind])
    obs = ~np.isnan(Y)
    real = gain2(Y)
    rng = np.random.default_rng(seed)
    null, gnull = [], []
    for _ in range(sims):
        Z = H.draw(p, obs, rng)
        null.append(gain2(Z)["gain"])
        gnull.append(fit2(Z, obs.astype(float), LAM, real["lam_g"])[2])
    g = fit2(Y, obs.astype(float), LAM, real["lam_g"])[2]
    sd = np.std(gnull, 0)
    fam = {"RL 3.1 (4 plain samples, cue)": R.RL4 + ["rl_cue"], "Think-SFT (cue, plain)": ["sft1_cue", "sft1_plain"], "base + cue (4 samples)": R.BASE4}
    mean = lambda G, names: float(np.mean([G[ind.index(n)] for n in names]))
    diff = lambda G: mean(G, fam["RL 3.1 (4 plain samples, cue)"]) - mean(G, fam["Think-SFT (cue, plain)"])
    return {"cells": int(obs.sum()), "ll_per_cell_rasch": round(real["ll_rasch"], 5), "ll_per_cell_2pl": round(real["ll_2pl"], 5), "gain": round(real["gain"], 6),
            "ridge_g": real["lam_g"], "gain_by_ridge_on_g": real["gain_by_ridge"],
            "gain_when_steps_are_doubled": round(gain2(Y, grid=(real["lam_g"],), steps=800)["gain"], 6),
            "null_gain_rasch_sim": {"n": sims, "mean": round(float(np.mean(null)), 6), "p95": round(float(np.percentile(null, 95)), 6), "max": round(float(max(null)), 6)},
            "detected": bool(real["gain"] > np.percentile(null, 95)),
            "g": {n: {"g": round(float(x), 3), "z_against_rasch_sims": round(float((x - m) / s), 2)} for n, x, m, s in sorted(zip(ind, g, np.mean(gnull, 0), sd), key=lambda t: -t[1])},
            "g_mean_by_family": {f: round(mean(g, names), 3) for f, names in fam.items()},
            "g_rl_minus_sft": {"value": round(diff(g), 3), "rasch_sims_p2.5_p97.5": [round(float(x), 3) for x in np.percentile([diff(G) for G in gnull], [2.5, 97.5])]}}


# ---------- H3: unions and power ----------
def unions(V):
    u = lambda a, b: int(np.nansum(np.maximum(V[a], V[b])))
    sr = [u("sft1_cue", s) for s in R.RL4]
    rr = [u(a, b) for a, b in itertools.combinations(R.RL4, 2)]
    sb = [u("sft1_cue", s) for s in R.BASE4]
    rb = [u(a, b) for a in R.RL4 for b in R.BASE4]
    return {"sft1_cue_with_one_rl_sample": sr, "two_rl_samples": rr, "gain_over_two_rl_samples": round(float(np.mean(sr) - np.mean(rr)), 2),
            "sft1_cue_with_one_base_sample": sb, "one_rl_sample_with_one_base_sample_mean": round(float(np.mean(rb)), 2),
            "all_four_rl_samples": int(np.nansum(np.max(np.vstack([V[s] for s in R.RL4]), 0))),
            "three_rl_samples_plus_sft1_cue_mean": round(float(np.mean([np.nansum(np.max(np.vstack([V[s] for s in c] + [V["sft1_cue"]]), 0)) for c in itertools.combinations(R.RL4, 3)])), 2)}


def power(V, ind, D, level, p, sims=200, seed=1):
    """Plant the observed per-group logit shifts of Think-SFT cue (D-rest groups) on a simulated arm and count how often C
    (k samples of the arm against 4 RL samples) leaves the one-axis 95 % range of the same k."""
    rng = np.random.default_rng(seed)
    g = D["rest"][0][0]
    rest = [n for n in ind if n not in HELD]
    b = H.groups(np.vstack([V[n] for n in rest]), LAM, "logit")[0]
    shift = H.group_shifts(V["sft1_cue"], np.vstack([V[n] for n in R.BASE4]), b, g, "logit")
    Pfit = X.fit(np.vstack([V[n] for n in ind]), (~np.isnan(np.vstack([V[n] for n in ind]))).astype(float), LAM)
    plant = np.mean([Pfit[0][ind.index(n)] for n in R.BASE4]) + Pfit[1] + shift[g]
    ks, C = (1, 2, 4, 8), {}
    for tag, pl in (("null", None), ("planted", plant)):
        C[tag] = {d: {k: [] for k in ks} for d in D}
        for _ in range(sims):
            Z, S = simulate(V, ind, p, rng, pl, max(ks))
            for d, design in designs(Z, ind, level).items():
                rl = wrong(Z, R.RL4, design)
                for k in ks:
                    Zk = Z | {f"s{j}": S[j] for j in range(k)}
                    C[tag][d][k].append(float(contrast(wrong(Zk, [f"s{j}" for j in range(k)], design), rl)))
    out = {"planted_logit_shift_hard_mid_easy": [round(float(x), 3) for x in shift], "planted_expected_right": round(float(sig(plant).sum()), 1), "sims": sims}
    for d in D:
        out[d] = {str(k): {"null_p2.5_p97.5": [round(float(x), 3) for x in np.percentile(C["null"][d][k], [2.5, 97.5])], "planted_mean_C": round(float(np.mean(C["planted"][d][k])), 3),
                           "power": round(float(np.mean((np.array(C["planted"][d][k]) < np.percentile(C["null"][d][k], 2.5)) | (np.array(C["planted"][d][k]) > np.percentile(C["null"][d][k], 97.5)))), 3)} for k in ks}
    return out


# ---------- step 0, (d), (e) ----------
def earlier_readings(V, ind):
    """The planner's count (hardest 50, easiest 200) under a ranking that uses every arm and under one that leaves the compared arms out."""
    out = {"hazard_section": {l: json.loads((H.OUT / "math500-01" / "readout.json").read_text())["H2_constancy_over_difficulty"][l]["sft1_cue"] for l in H.LINKS}}
    for tag, names in (("all_36_arms (circular)", ind), ("arms_left_out (D-rest ranking)", [n for n in ind if n not in HELD])):
        order = np.argsort(X.fit(np.vstack([V[n] for n in names]), (~np.isnan(np.vstack([V[n] for n in names]))).astype(float), LAM)[1], kind="stable")
        out[tag] = {f"{w} {k}": {a: round(float(err(V, v)[idx].sum()), 2) for a, v in (("base", R.BASE4), ("rl_plain", R.RL4), ("sft1_cue", ["sft1_cue"]))}
                    for w, k, idx in (("hardest", 50, order[:50]), ("easiest", 200, order[-200:]))}
    return out


def rows_of(V, ind, D, m, runs):
    """(d) what the stored rows show: Think-SFT cue's errors on easy problems and the hard problems it solves that all 4 RL samples miss;
    (e) subject and level of the problems where Think-SFT cue and RL differ."""
    pp = {r["problem_index"]: r for r in json.loads((X.STUDY / "results" / "wsp1" / "full500" / "sft1_cue-01" / "per_problem.json").read_text())}
    rl = collections.defaultdict(list)
    for r in H.day1_rows("rl"):
        rl[r["problem_index"]].append(r)
    cue = {r["problem_index"]: r for r in map(json.loads, (pathlib.Path(runs) / (X.J + "153110-e985") / "answers.jsonl").read_text().splitlines())} if runs else {}
    s, k = V["sft1_cue"], np.vstack([V[n] for n in R.RL4]).sum(0)
    lev, sub, g = np.array(m["level"]), np.array(m["subject"]), D["rest"][0][0]
    rest_share = np.nanmean(np.vstack([V[n] for n in ind if n not in HELD]), 0)
    row = lambda i: {"problem_index": int(i), "unique_id": m["unique_ids"][i], "level": int(lev[i]), "subject": sub[i], "rest_group": BINS["rest"][g[i]],
                     "share_of_left_out_arms_right": round(float(rest_share[i]), 2), "base_right_of_4": int(np.vstack([V[n] for n in R.BASE4])[:, i].sum()), "rl_right_of_4": int(k[i]),
                     "sft1_cue": {"score_v3": int(s[i]), "cap_hit": pp[i]["cap_hit"], "n_generated": pp[i]["n_generated"]}, "gold": rl[i][0]["gold"],
                     "rl_plain_extracted_v3": [r["extracted_v3"] for r in rl[i]], "rl_plain_cap_hits": sum(r["cap_hit"] for r in rl[i])}
    wrongs = np.flatnonzero(s == 0)
    easy = [i for i in wrongs if lev[i] <= 2 or g[i] == 2]
    hard_solved = sorted(np.flatnonzero((s == 1) & (k == 0)), key=lambda i: rest_share[i])
    tok = lambda idx: round(float(np.mean([pp[i]["n_generated"] for i in idx])), 0) if len(idx) else None
    cap = lambda idx: [int(sum(pp[i]["cap_hit"] for i in idx)), len(idx)]
    sft_only, rl_only = (s == 1) & (k <= 1), (s == 0) & (k >= 3)
    tab = lambda mask, key: dict(sorted(collections.Counter(key[mask].tolist()).items()))
    return {"raw_text_of_sft1_cue": "not readable: job sameraslan-1114-185940-514f is in the Modal Volume of workspace sameraslan; per_problem.json has score, cap hit and tokens only",
            "sft1_cue_errors": {"all": len(wrongs), "cap_hits [n, of]": cap(wrongs), "mean_tokens": tok(wrongs), "mean_tokens_of_right_answers": tok(np.flatnonzero(s == 1)),
                                "on_easy_problems (level 1-2 or easiest rest group)": {"n": len(easy), "cap_hits [n, of]": cap(easy), "mean_tokens": tok(easy),
                                                                                       "rl_right_of_4_on_them": dict(sorted(collections.Counter(int(k[i]) for i in easy).items())),
                                                                                       "base_right_of_4_on_them": dict(sorted(collections.Counter(int(np.vstack([V[n] for n in R.BASE4])[:, i].sum()) for i in easy).items()))},
                                "on_other_problems": {"n": len(wrongs) - len(easy), "cap_hits [n, of]": cap([i for i in wrongs if i not in easy])}},
            "easy_errors": [row(i) for i in easy],
            "solved_by_sft1_cue_missed_by_all_4_rl_samples": {"n": len(hard_solved), "rl_cue_right_on_them": int(sum(V["rl_cue"][i] for i in hard_solved)),
                                                               "sft1_plain_right_on_them": int(sum(V["sft1_plain"][i] for i in hard_solved)),
                                                               "share_of_left_out_arms_right_mean": round(float(np.mean(rest_share[hard_solved])), 2),
                                                               "rows": [row(i) | ({"rl_cue_extracted_v3": cue[i]["extracted_v3"]} if i in cue else {}) for i in hard_solved]},
            "missed_by_sft1_cue_solved_by_all_4_rl_samples": {"n": int(((s == 0) & (k == 4)).sum()), "share_of_left_out_arms_right_mean": round(float(np.mean(rest_share[(s == 0) & (k == 4)])), 2)},
            "where_they_differ": {"definition": "SFT only = Think-SFT cue right and RL right in at most 1 of 4 samples; RL only = Think-SFT cue wrong and RL right in at least 3 of 4",
                                  "sft_only": {"n": int(sft_only.sum()), "by_level": tab(sft_only, lev), "by_subject": tab(sft_only, sub)},
                                  "rl_only": {"n": int(rl_only.sum()), "by_level": tab(rl_only, lev), "by_subject": tab(rl_only, sub)},
                                  "all_problems": {"by_level": tab(np.ones(500, bool), lev), "by_subject": tab(np.ones(500, bool), sub)}}}


def run_json(folder, cmd, inputs):
    (folder / "run.json").write_text(json.dumps({"commit": H.head(), "commit_note": "HEAD when it ran; analysis/profile.py is committed in the commit that adds this file",
                                                 "command": f"uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.profile {cmd}",
                                                 "job_id": None, "gpu": "none (laptop, numpy)", "spec": "studies/rlneurons/specs/SPEC_profile.md", "inputs": inputs}, indent=1) + "\n")


def markdown(T, h):
    md = []
    for d, rows in T.items():
        md += [f"Difficulty {d}: error reduction against the reference base + cue samples [95 %], wrong cells per sample in brackets", "",
               "| Arm | " + " | ".join(f"{b} ({n:g} problems)" for b, n in zip(BINS[d], rows["problems"])) + " |", "|---|" + "---|" * len(BINS[d]),
               "| base + cue (reference), wrong | " + " | ".join(f"{x:g}" for x in rows["reference_wrong"]) + " |"]
        for a in ARMS:
            r = rows[a]
            md.append(f"| {WHAT[a]} | " + " | ".join(f"{100 * e:.0f} % [{100 * lo:.0f}, {100 * hi:.0f}] ({w:g})" for e, (lo, hi), w in zip(r["error_reduction"], r["error_reduction_interval95"], r["wrong"])) + " |")
        x = h[d]
        md += ["", f"C(Think-SFT cue, RL plain pooled) = {x['C_sft1_cue_vs_rl_plain']:+.2f} [{x['boot95'][0]:+.2f}, {x['boot95'][1]:+.2f}]; one-axis range "
                   f"[{x['one_axis_null']['p2.5']:+.2f}, {x['one_axis_null']['p97.5']:+.2f}]" + (f"; same-arm: RL {x['same_arm_one_sample_vs_other_three']['rl_plain']}, base {x['same_arm_one_sample_vs_other_three']['base_cue']}" if d != "base" else ""), ""]
    return md


def cap_markdown(c):
    md = ["Wrong cells per sample by level: all = cap hits + finished wrong", "", "| Arm | " + " | ".join(c["bins"]) + " |", "|---|---|---|---|---|"]
    for name, r in c.items():
        if name != "bins":
            md.append(f"| {name} | " + " | ".join(f"{w:g} = {x:g} + {f:g}" for w, x, f in zip(r["wrong"], r["wrong_cap_hit"], r["wrong_finished"])) + " |")
    return md


def cmd_fit(runs):
    V, ind = R.load("math500")
    m = meta()
    D = designs(V, ind, m["level"])
    W = R.boot(500)
    p = X.rasch_p(np.vstack([V[n] for n in ind]), LAM)
    T, h = table(V, D, W), h1(V, ind, D, m["level"], W, p)
    b, g = H.groups(np.vstack([V[n] for n in ind if n not in HELD]), LAM, "logit")
    shifts = {a: [round(float(x), 3) for x in H.group_shifts(np.vstack([V[n] for n in names]), np.vstack([V[n] for n in R.BASE4]), b, g, "logit")] for a, names in ARMS.items()}
    ex = rows_of(V, ind, D, m, runs)
    readout = {"set": "math500", "difficulty": {"rest_arms": [n for n in ind if n not in HELD], "base_like_arms": BASE_LIKE, "bins": BINS},
               "earlier_readings": earlier_readings(V, ind), "table": T, "cap_hits_by_level": caps(m["level"]), "logit_shift_by_rest_group_hard_mid_easy": shifts, "H1_profile_contrast": h,
               "H2_2pl": h2(V, ind, p), "H3_unions": unions(V), "H3_power": power(V, ind, D, m["level"], p),
               "rows": {k: v for k, v in ex.items() if k not in ("easy_errors",) and k != "solved_by_sft1_cue_missed_by_all_4_rl_samples"}
               | {"solved_by_sft1_cue_missed_by_all_4_rl_samples": {k: v for k, v in ex["solved_by_sft1_cue_missed_by_all_4_rl_samples"].items() if k != "rows"}}}
    out = OUT / "math500-01"
    out.mkdir(parents=True, exist_ok=True)
    (out / "readout.json").write_text(json.dumps(readout, indent=1) + "\n")
    (out / "table.md").write_text("\n".join(markdown(T, h) + cap_markdown(readout["cap_hits_by_level"])) + "\n")
    (out / "examples.json").write_text(json.dumps({"note": ex["raw_text_of_sft1_cue"], "sft1_cue_wrong_on_easy_problems": ex["easy_errors"],
                                                   "sft1_cue_right_all_4_rl_samples_wrong": ex["solved_by_sft1_cue_missed_by_all_4_rl_samples"]["rows"]}, indent=1) + "\n")
    run_json(out, "fit", "results/axis/math500-01/vectors.json; data/profile/math500_meta_v1.json; results/wsp1/full500/sft1_cue-01/per_problem.json; results/day1_3/math500_rl-01/rows.jsonl; results/hazard/math500-01/readout.json; runs/abaybektursun-1114-153110-e985/answers.jsonl")
    print(json.dumps({k: v for k, v in readout.items() if k != "table"}, indent=1))
    print("\n".join(markdown(T, h)))


# ---------- predictions for Think-SFT on hard328 ----------
def profile_rule(y5, V5, ind5, ref3, b3, boot=False):
    """Right count on hard328: the arm's logit shift per D-rest group on MATH-500, applied to each hard328 problem by the group its
    reference probability falls in. With boot, also BOOT draws (bootstrap of the group shifts, binomial draw of the cells)."""
    b, g = H.groups(np.vstack([V5[n] for n in ind5 if n not in HELD]), LAM, "logit")
    ref5 = np.vstack([V5[n] for n in R.BASE4])
    p5 = sig(R.ability(ref5, b) + b)
    edges = [(p5[g == k].max() + p5[g == k + 1].min()) / 2 for k in range(2)]
    z3 = R.ability(ref3, b3) + b3
    g3 = np.digitize(sig(z3), edges)
    if not boot:
        s = H.group_shifts(y5, ref5, b, g, "logit")
        return float(sig(z3 + s[g3]).sum()), {"shift_hard_mid_easy": [round(float(x), 3) for x in s], "edges_reference_probability": [round(float(x), 3) for x in edges],
                                              "hard328_problems_per_group": [int((g3 == k).sum()) for k in range(3)]}
    s, sB = H.group_shifts(y5, ref5, b, g, "logit", boot=True)
    return (np.random.default_rng(0).random((H.BOOT, len(z3))) < sig(z3[None, :] + sB.T[:, g3])).sum(1)


def predict_cells():
    V5, ind5, V3, b5, S5, S3 = R.real_sets()
    lam3 = R.LAM["hard328"]
    extra = [V3["base_plain"]]
    check, _ = R.transfer(b5, S5, S3, extra, lam3)
    for a in R.BOTH:                                   # the profile rule on the 5 arms measured on both sets, the arm left out of b3
        b3 = R.difficulties([S3[x] for x in S3 if x != a] + extra, lam3)
        check[a]["profile"] = profile_rule(S5[a], V5, ind5, S3["ref"], b3)[0]
    mae = {r: round(float(np.mean([abs(v[r] - v["observed"]) for v in check.values()])), 2) for r in ("Lc", "L1", "P", "profile")}
    bias = float(np.mean([v["profile"] - v["observed"] for v in check.values()]))          # the profile rule overshoots the 5 known arms
    b3 = R.difficulties(list(S3.values()) + extra, lam3)
    a_ref = R.ability(S3["ref"], b3)
    d5 = np.array([R.ability(S5[a], b5) - R.ability(S5["ref"], b5) for a in R.BOTH])
    d3 = np.array([R.ability(S3[a], b3) - a_ref for a in R.BOTH])
    c = float(d5 @ d3 / (d5 @ d5))
    W5, rng = R.boot(500), np.random.default_rng(0)
    cells = []
    for arm, what in (("sft1_cue", "hard328 Think-SFT, cue, one sample"), ("sft1_plain", "hard328 Think-SFT, plain, one sample")):
        d, dB = R.ability(V5[arm], b5) - R.ability(S5["ref"], b5), R.ability(V5[arm], b5, W5) - R.ability(S5["ref"], b5, W5)
        lc = (rng.random((R.BOOT, 328)) < sig(a_ref + c * dB[:, None] + b3[None, :])).sum(1)
        prof, info = profile_rule(V5[arm], V5, ind5, S3["ref"], b3)
        pB = profile_rule(V5[arm], V5, ind5, S3["ref"], b3, boot=True)
        cells.append({"cell": what, "arm": arm, "n": 328, "right_math500": int(np.nansum(V5[arm])), "shift_logits_math500": round(float(d), 3),
                      "Lc": round(float(sig(a_ref + c * d + b3).sum()), 1), "Lc_interval80": [float(x) for x in np.percentile(lc, [10, 90])],
                      "L1": round(float(sig(a_ref + d + b3).sum()), 1), "P": round(328 * (R.acc(S3["ref"]) + R.acc(V5[arm]) - R.acc(S5["ref"])), 1),
                      "profile": round(prof, 1), "profile_interval80": [float(x) for x in np.percentile(pB, [10, 90])],
                      "profile_corrected": round(prof - bias, 1), "profile_corrected_interval80": [float(x) for x in np.percentile(pB - bias, [10, 90])], "profile_rule": info})
    return {"reference_right_hard328": round(R.acc(S3["ref"]) * 328, 1), "c": round(c, 3),
            "check_on_the_5_arms_measured_on_both_sets": {"rows": {a: {k: round(float(v[k]), 1) for k in ("observed", "Lc", "L1", "P", "profile")} for a, v in check.items()}, "mean_abs_error": mae,
                                                          "profile_mean_signed_error": round(bias, 2)},
            "cells": cells}


def cmd_predict():
    path = OUT / "predict-01" / "predictions.json"
    assert not path.exists(), "predictions are filed once"
    out = {"filed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "code_commit_parent": H.head(),
           "rules": "Lc, L1, P: analysis/rate.py with the arm held out of the calibration; profile: specs/SPEC_profile.md (logit shift per D-rest group of MATH-500, applied by reference probability)",
           "author_guess_before_opening": {"hard328 Think-SFT, cue, one sample": 200, "hard328 Think-SFT, plain, one sample": 195,
                                           "why": "on MATH-500 level 5 Think-SFT cue has 23 wrong against RL's 21 to 30 per sample, 15 of the 23 cap hits; so near RL's 205 on the 328, less for longer answers"},
           "seen": "not seen: work-9ecc56 was read by its title only (board ls); no result, comment, job log or run folder of the Think-SFT hard328 cells was opened before filing"} | predict_cells()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=1) + "\n")
    run_json(path.parent, "predict", "results/axis/{math500,hard328}-01/vectors.json")
    print(json.dumps(out, indent=1))


RULES = ("Lc", "L1", "P", "profile", "profile_corrected")
# cell -> (observed right of 328, where it was read); filled in after predict-01 was pushed
OBSERVED = {}


def cmd_score():
    d = json.loads((OUT / "predict-01" / "predictions.json").read_text())
    rows = []
    for c in d["cells"]:
        row = {"cell": c["cell"], "filed_utc": d["filed_utc"]} | {k: c[k] for k in ("Lc", "L1", "P", "profile", "profile_corrected", "Lc_interval80", "profile_interval80", "profile_corrected_interval80")}
        if c["cell"] in OBSERVED:
            obs, src = OBSERVED[c["cell"]]
            row |= {"observed": obs, "source": src, "error": {k: round(c[k] - obs, 1) for k in RULES} | {"author_guess": d["author_guess_before_opening"][c["cell"]] - obs},
                    "inside_interval80": {k: bool(c[k + "_interval80"][0] <= obs <= c[k + "_interval80"][1]) for k in ("Lc", "profile", "profile_corrected")}}
        rows.append(row)
    done = [r for r in rows if "observed" in r]
    out = {"scored": len(done), "not_finished": len(rows) - len(done),
           "mean_abs_error": {k: round(float(np.mean([abs(r["error"][k]) for r in done])), 2) for k in RULES + ("author_guess",)} if done else None, "cells": rows}
    (OUT / "scored-01").mkdir(parents=True, exist_ok=True)
    (OUT / "scored-01" / "readout.json").write_text(json.dumps(out, indent=1) + "\n")
    run_json(OUT / "scored-01", "score", "results/profile/predict-01/predictions.json; OBSERVED in analysis/profile.py")
    print(json.dumps(out, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["fit", "predict", "score"])
    ap.add_argument("--runs", default="runs", help="folder of gpu.py get copies (RL cue answers for the examples); '' to skip")
    a = ap.parse_args()
    {"fit": lambda: cmd_fit(a.runs), "predict": cmd_predict, "score": cmd_score}[a.cmd]()


if __name__ == "__main__":
    main()
