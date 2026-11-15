"""One axis or several? (specs/SPEC_axis.md, board idea-1c8b73): do the partial routes toward the RL model fix the same
problems? Per-problem 0/1 vectors of every arm (grader v3, T 1.0 / top-p 1.0); pair overlap and oracle union against the
rest-score-stratified null and the same-config pairs; Rasch against Rasch plus one bilinear term, held out; the floor.

    uv run --no-project --with numpy python -m studies.rlneurons.analysis.axis --extract [--runs runs]
    uv run --no-project --with numpy python -m studies.rlneurons.analysis.axis

Run from the repository root. --extract reads the committed per-problem files (this commit and the pinned commits of the
branches in REF) and, for cells whose raw rows are not committed, runs/<job id>/answers.jsonl (`uv run tools/gpu.py get
<job id>`), checks each right count against the committed metrics and writes results/axis/<set>-01/vectors.json and
manifest.json. Without --extract it reads only those two files and writes readout.json and run.json beside them.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import pathlib
import subprocess

import numpy as np

STUDY = pathlib.Path(__file__).resolve().parents[1]
OUT = STUDY / "results" / "axis"
RES = "studies/rlneurons/results/"
REF = {"reward5": "9d07eba38e6c3f96dd152001bf207ab71c006d9d", "shots": "238d2340b3a04c00b85a05805bbec92ca394d082",
       "wsp1": "70dd2b4861f47d6a22decc5c0d895695057061ff", "lit": "81d74c2a0b91b41c770540804e642760fd5fee4e"}
J = "abaybektursun-1114-"

# arm -> (kind, source, run folder under results/ (its metrics.json gives the committed right count), commit ref, family, prompt, what)
#   kind "rows": committed rows.jsonl, source = (path, sample); "answers": runs/<job>/answers.jsonl; "pp": committed per_problem.json
#   at ref; "sel": committed selector readout, source = (path, rule), a derived arm.
M500 = {f"base_cue_s{s}": ("rows", (RES + "day1_3/math500_base_cue-01/rows.jsonl", s), "day1_3/math500_base_cue-01", None, "base_cue", "cue",
                           f"base + cue, sample {s}") for s in range(4)}
M500 |= {f"rl_plain_s{s}": ("rows", (RES + "day1_3/math500_rl-01/rows.jsonl", s), "day1_3/math500_rl-01", None, "rl_plain", "plain",
                            f"RL-Zero-Math 3.1 plain, sample {s}") for s in range(4)}
M500 |= {n: ("answers", J + j, f"day1_wdiff/{n}-01", None, n, n.split("_")[1], w) for n, j, w in [
    ("theta0.25_cue", "153102-b029", "base + 0.25 (RL - base), cue"), ("theta0.5_cue", "152855-683b", "base + 0.5 (RL - base), cue"),
    ("theta0.75_cue", "153106-af79", "base + 0.75 (RL - base), cue"), ("theta1.25_cue", "163851-0cec", "base + 1.25 (RL - base), cue"),
    ("theta1.5_cue", "153057-45e7", "base + 1.5 (RL - base), cue"), ("rl_cue", "153110-e985", "RL-Zero-Math 3.1, cue"),
    ("code_cue", "162452-0203", "RL-Zero-Code 3.1, cue"), ("code_plain", "153052-5013", "RL-Zero-Code 3.1, plain"),
    ("random_cue", "153047-6429", "base + random difference of the RL norm, cue (control)"),
    ("theta0.25_plain", "163704-ffca", "base + 0.25 (RL - base), plain"), ("theta0.5_plain", "163658-8118", "base + 0.5 (RL - base), plain")]}
M500 |= {n: ("answers", J + j, f"reward5/{n}-01", "reward5", n, n.split("_")[1], f"Olmo-3-7B-RL-Zero-{n.split('30')[0].capitalize()} (3.0), {n.split('_')[1]}")
         for n, j in [("if30_cue", "182707-731c"), ("general30_cue", "182712-3556"), ("mix30_cue", "182718-612b"), ("math30_cue", "182724-87aa"),
                      ("code30_cue", "182730-9523"), ("if30_plain", "182735-bcca"), ("general30_plain", "182742-9129"),
                      ("mix30_plain", "182748-3300"), ("math30_plain", "182754-7238"), ("code30_plain", "182800-3331")]}
M500 |= {f"shots_{n}": ("answers", J + j, f"shots1/{n}-01", "shots", f"shots_{n}", "cue", f"base + cue + 3 solved problems written by {w} in context (n 497)")
         for n, j, w in [("base", "183855-e840", "the cued base"), ("code", "183907-d9d6", "Code-RL"), ("rl", "183901-fd89", "Math-RL")]}
M500 |= {n: ("pp", RES + f"wsp1/full500/{n}-01/per_problem.json", f"wsp1/full500/{n}-01", "wsp1", n, n.split("_")[1], w) for n, w in [
    ("top8_plain", "base + top 8 singular directions per matrix of the RL delta, plain"),
    ("rand8_plain", "base + random rank-8 directions, plain (control)"),
    ("sft1_cue", "Olmo-3-7B-Think-SFT, cue"), ("sft1_plain", "Olmo-3-7B-Think-SFT, plain")]}
M500 |= {n: ("sel", (RES + f"selector/math500_{m}-01/readout.json", r), f"selector/math500_{m}-01", None, f, "cue" if m == "base_cue" else "plain", w)
         for n, m, r, f, w in [("base_vote4", "base_cue", "vote", "base_cue", "plurality vote over the 4 base + cue samples"),
                               ("base_tie_short", "base_cue", "tie_short", "base_cue", "vote, ties to the shortest finished answer"),
                               ("rl_vote4", "rl", "vote", "rl_plain", "plurality vote over the 4 RL samples")]}
H328 = {n: ("answers", J + j, f"{d}/{r}-01", None, n, n.split("_")[-1], w) for n, j, d, r, w in [
    ("base_cue", "151534-e72c", "day1", "hard328_base_cue_t10", "base + cue"), ("rl_plain", "151540-86ef", "day1", "hard328_rl_plain_t10", "RL plain"),
    ("base_plain", "132922-7ba0", "day1_hard328", "base_plain_T1", "base plain"), ("rl_cue", "132929-a32d", "day1_hard328", "rl_cue_T1", "RL cue"),
    ("theta0.25_cue", "181222-a5f4", "day1_wdiff328", "theta0.25_cue", "base + 0.25 (RL - base), cue"),
    ("theta0.5_cue", "181228-34ad", "day1_wdiff328", "theta0.5_cue", "base + 0.5 (RL - base), cue"),
    ("code_cue", "181216-a619", "day1_wdiff328", "code1_cue", "RL-Zero-Code 3.1, cue")]}
SETS = {"math500": M500, "hard328": H328}
MASK = {"shots_base": [0, 1, 2], "shots_code": [0, 1, 2], "shots_rl": [0, 1, 2]}     # the three problems used as examples
PARTS = {"base_vote4": [f"base_cue_s{s}" for s in range(4)], "base_tie_short": [f"base_cue_s{s}" for s in range(4)],
         "rl_vote4": [f"rl_plain_s{s}" for s in range(4)]}
# same-seed reruns of a cell above: name -> (arm it repeats, kind, source, ref)
RERUN = {"math500": {"check_t1_n50": ("base_cue_s0", "answers", J + "132917-7f81", None), "check_t1_n10": ("base_cue_s0", "answers", J + "151028-ec3c", None)},
         "hard328": {"base_cue_rerun_s0": ("base_cue", "tsv", RES + "day1_length_rules/hard328_base-01/per_problem.tsv", "lit")}}
EXCLUDED = {
    "base plain T3 (224), T1 (410), T2 (463) of RLN-4": "raw rows in the owner's S3 (r4/), not committed and not in runs/; the Day-1 #3 samples replace T1 and T2",
    "base + cue at T 0.6 (354, 378)": "other sampling setting; the spec fixes T 1.0 / top-p 1.0",
    "min-p / top-p cells (day1_minp, frustea)": "only totals committed; raw rows in frustea's Modal workspace",
    "self-review cells (day1_critique, frustea)": "only totals committed; raw rows in frustea's Modal workspace",
    "length rules on MATH-500 and hard328 (sameraslan)": "selectors over the base samples; per-problem file gives sample 0 only (used as the same-seed rerun on hard328)",
    "hard328 4-sample rows (sameraslan)": "per-sample scores not committed; raw rows in sameraslan's Modal workspace",
    "metaharness shard reruns (sameraslan)": "only totals and wall times committed, no per-problem scores",
    "wsp1 screen100 cells": "first 100 problems only",
    "theta1 plain check (n 50), restart rows": "n 50; restart differs from single on cap hits only",
    "cleanneurons loop-neuron cell (sameraslan)": "T 0.6 / top-p 0.95 and no per-problem file",
    "shots second draw, selfdistill, hard328 shots": "not finished or not committed when this ran",
}
CANDIDATES = [("theta0.5_cue", "sft1_cue"), ("theta0.5_cue", "shots_rl"), ("sft1_cue", "shots_rl"), ("theta0.25_cue", "sft1_cue"),
              ("code_cue", "sft1_cue"), ("math30_cue", "sft1_cue"), ("theta0.5_cue", "code_cue")]
STACK_ARMS = ["theta0.25_cue", "theta0.5_cue", "sft1_cue", "shots_rl", "code_cue", "math30_cue"]
RL_ARMS = [f"rl_plain_s{s}" for s in range(4)] + ["rl_cue", "rl_vote4"]
NO_RL = [f"base_cue_s{s}" for s in range(4)] + ["base_vote4", "base_tie_short", "shots_base", "random_cue", "rand8_plain", "sft1_cue", "sft1_plain",
                                                 "base_cue", "base_plain"]   # arms that use no RL weights and no RL output


# ---------- extraction ----------
def show(ref, path):
    return subprocess.run(["git", "show", f"{ref or 'HEAD'}:{path}"], check=True, capture_output=True).stdout


def read_arm(kind, src, ref, runs):
    """-> ({problem index: 0/1}, path, sha256, {problem index: unique_id} or None)."""
    if kind == "answers":
        p = runs / src / "answers.jsonl"
        raw = p.read_bytes()
        rows = [json.loads(line) for line in raw.splitlines()]
        rows = [r for r in rows if r["sample"] == 0 and not r.get("attempt")]
        return {r["problem_index"]: r["score_v3"] for r in rows}, f"runs/{src}/answers.jsonl", hashlib.sha256(raw).hexdigest(), {r["problem_index"]: r["unique_id"] for r in rows}
    path = src if isinstance(src, str) else src[0]
    raw = show(REF.get(ref), path)
    sha = hashlib.sha256(raw).hexdigest()
    if kind == "rows":
        rows = [json.loads(line) for line in raw.splitlines()]
        return {r["problem_index"]: r["score_v3"] for r in rows if r["sample"] == src[1] and r["attempt"] == 0}, path, sha, None
    if kind == "pp":
        return {r["problem_index"]: r["score_v3"] for r in json.loads(raw)}, path, sha, None
    if kind == "sel":
        d = json.loads(raw)
        return dict(zip(d["problem_indices"], d["per_problem"][src[1]])), path, sha, None
    if kind == "tsv":                                   # column "single" = "<score> <tokens> <sample>*" of sample 0
        lines = [ln.split("\t") for ln in raw.decode().splitlines()[1:]]
        return {int(c[1]): int(c[3].split()[0]) for c in lines}, path, sha, None
    raise ValueError(kind)


def committed_right(kind, src, folder, ref):
    if kind == "sel":
        return json.loads(show(None, src[0]))["rows"][src[1]]["right"]
    if kind == "rows":                                  # README "Right in samples 0 to 3" (Day-1 #3)
        return {"base_cue": [405, 409, 410, 418], "rl": [456, 462, 464, 458]}[folder.split("math500_")[1][:-3]][src[1]]
    m = json.loads(show(REF.get(ref), RES + folder + "/metrics.json"))
    return m["right_v3"] if kind == "pp" else m["counts"]["correct_v3"]


def extract(runs):
    head = subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    for name, arms in SETS.items():
        got, man, uid = {}, {}, {}
        for arm, (kind, src, folder, ref, family, prompt, what) in arms.items():
            sc, path, sha, u = read_arm(kind, src, ref, runs)
            uid = uid or u or {}
            right, want = sum(sc.values()), committed_right(kind, src, folder, ref)
            assert want is None or right == want, (arm, right, want)
            run = json.loads(show(REF.get(ref), RES + folder + "/run.json")) if kind != "sel" else {}
            got[arm] = sc
            man[arm] = {"what": what, "family": family, "prompt": prompt, "derived_from": PARTS.get(arm), "job_id": run.get("job_id") or run.get("job_ids"),
                        "run_folder": RES + folder, "source": path, "source_commit": REF.get(ref) or head, "sha256": sha, "grader": "v3 (score_v3 of run_cell)",
                        "right": right, "n": len(sc) - len(MASK.get(arm, [])), "right_unmasked": right, "matches_committed_metrics": want is not None}
        idx = sorted(next(iter(got.values())))
        assert all(sorted(sc) == idx for sc in got.values()), "arms disagree on the problem set"
        vec = {arm: [None if i in MASK.get(arm, []) else sc[i] for i in idx] for arm, sc in got.items()}
        for arm in MASK:
            if arm in vec:
                man[arm]["right"] = sum(v for v in vec[arm] if v is not None)
        rer = {}
        for r, (of, kind, src, ref) in RERUN[name].items():
            sc, path, sha, _ = read_arm(kind, src, ref, runs)
            rer[r] = {"repeats": of, "source": path, "sha256": sha, "source_commit": REF.get(ref) or head, "problem_indices": sorted(sc), "scores": [sc[i] for i in sorted(sc)]}
        out = OUT / f"{name}-01"
        out.mkdir(parents=True, exist_ok=True)
        (out / "vectors.json").write_text(json.dumps({"set": name, "grader": "v3", "problem_indices": idx, "unique_ids": [uid.get(i) for i in idx],
                                                      "arms": vec, "reruns": rer}, separators=(",", ":")) + "\n")
        (out / "manifest.json").write_text(json.dumps({"set": name, "n_problems": len(idx), "arms": man, "excluded": EXCLUDED}, indent=1) + "\n")
        print(name, len(idx), "problems,", len(vec), "arms:", {a: m["right"] for a, m in man.items()})


# ---------- pair statistics ----------
def raw_pair(Y, names, parts, A, B, ref=None):
    """Counts of two arms and the moments of "right under both" when B is permuted among problems of equal rest score.
    Y: arms x problems, nan = not run. Rest score: share right among the independent arms other than A, B and what they derive from."""
    a, b = Y[names.index(A)], Y[names.index(B)]
    out_arms = set(parts.get(A, [A])) | set(parts.get(B, [B])) | {A, B} | set(parts)
    rest = np.nanmean(Y[[i for i, n in enumerate(names) if n not in out_arms]], axis=0)
    s = np.unique(np.round(rest, 6), return_inverse=True)[1]
    ok = ~np.isnan(a) & ~np.isnan(b)

    def moments(keep):
        n, x, y = (np.bincount(s[keep], weights=w, minlength=s.max() + 1) for w in (None, a[keep], b[keep]))
        m = n > 1
        return (x[n > 0] * y[n > 0] / n[n > 0]).sum(), (x[m] * y[m] * (n[m] - x[m]) * (n[m] - y[m]) / (n[m] ** 2 * (n[m] - 1))).sum()
    mean, var = moments(ok)
    r = {"n": int(ok.sum()), "right_a": float(a[ok].sum()), "right_b": float(b[ok].sum()), "both": float((a[ok] * b[ok]).sum()), "mean": mean, "var": var}
    if ref and ref not in (A, B):
        w = ok & (Y[names.index(ref)] == 0)             # the problems the reference gets wrong
        fm, fv = moments(w)
        r |= {"fixed_a": float(a[w].sum()), "fixed_b": float(b[w].sum()), "fixed_both": float((a[w] * b[w]).sum()), "fixed_mean": fm, "fixed_var": fv}
    return r


def pair_table(Y, names, parts, pairs, ref=None, p=None, sims=200, seed=0):
    """Union and overlap of each pair against the stratified null. The rest score measures difficulty with error, which leaves the
    stratified null biased toward "alike" (planted one-axis data: about -1.5 problems); with p (arms x problems success
    probabilities of the fitted one-axis model, rows in the order of the independent arms) the bias and the spread of the
    excess are taken from `sims` matrices drawn from p and passed through the same statistic. Pairs with a derived arm are not
    simulated and keep the uncorrected null."""
    ind = [n for n in names if n not in parts]
    rows = [names.index(n) for n in ind]
    sim = {}
    if p is not None:
        rng = np.random.default_rng(seed)
        todo = [(a, b) for a, b in pairs if a in ind and b in ind]
        acc = {q: [] for q in todo}
        for _ in range(sims):
            Z = Y.copy()
            Z[rows] = np.where(np.isnan(Y[rows]), np.nan, (rng.random(p.shape) < p).astype(float))
            for q in todo:
                r = raw_pair(Z, names, parts, *q, ref)
                acc[q].append((r["mean"] - r["both"], r.get("fixed_both", 0) - r.get("fixed_mean", 0)))
        sim = {q: np.array(v) for q, v in acc.items()}
    out = []
    for A, B in pairs:
        r = raw_pair(Y, names, parts, A, B, ref)
        raw = r["mean"] - r["both"]
        bias, sd = (sim[A, B][:, 0].mean(), sim[A, B][:, 0].std()) if (A, B) in sim else (0.0, r["var"] ** 0.5)
        union = r["right_a"] + r["right_b"] - r["both"]
        o = {"a": A, "b": B, "n": r["n"], "right_a": int(r["right_a"]), "right_b": int(r["right_b"]), "union": int(union),
             "union_minus_best": int(union - max(r["right_a"], r["right_b"])), "excess_uncorrected": round(raw, 2), "null_bias": round(bias, 2),
             "excess": round(raw - bias, 2), "null_sd": round(sd, 2), "z": round((raw - bias) / sd, 2) if sd else None, "bias_corrected": (A, B) in sim}
        if "fixed_both" in r:
            fb, fsd = (sim[A, B][:, 1].mean(), sim[A, B][:, 1].std()) if (A, B) in sim else (0.0, r["fixed_var"] ** 0.5)
            un = r["fixed_a"] + r["fixed_b"] - r["fixed_both"]
            exp = r["fixed_mean"] + fb                  # expected overlap of the fixed sets under one axis
            o |= {"fixed_a": int(r["fixed_a"]), "fixed_b": int(r["fixed_b"]), "fixed_both": int(r["fixed_both"]), "fixed_both_null": round(exp, 2),
                  "jaccard": round(r["fixed_both"] / un, 3) if un else None,
                  "jaccard_null": round(exp / (r["fixed_a"] + r["fixed_b"] - exp), 3) if r["fixed_a"] + r["fixed_b"] - exp else None,
                  "fixed_z": round((r["fixed_both"] - exp) / fsd, 2) if fsd else None}
        out.append(o)
    return out


def zsummary(rows):
    z = np.array([r["z"] for r in rows if r["z"] is not None])
    e = np.array([r["excess"] for r in rows if r["z"] is not None])
    return {"pairs": len(z), "z_mean": round(float(z.mean()), 2), "z_sd": round(float(z.std()), 2), "z_min": float(z.min()), "z_max": float(z.max()),
            "share_abs_z_over_3": round(float((abs(z) > 3).mean()), 3), "excess_mean": round(float(e.mean()), 2), "excess_min": float(e.min()), "excess_max": float(e.max())}


# ---------- item model ----------
def fit(Y, W, lam_b, lam_uv=None, steps=400, seed=0):
    """Rasch logit = a_j + b_i (+ u_i v_j when lam_uv is given), ridge on b, u, v; Adam on the full matrix. W: 1 = cell used."""
    rng = np.random.default_rng(seed)
    nj, ni = Y.shape
    two = lam_uv is not None
    P = [np.zeros(nj), np.zeros(ni), rng.normal(0, 0.1, ni) * two, rng.normal(0, 0.1, nj) * two]
    Y0 = np.where(W > 0, Y, 0.0)
    m, v = [np.zeros_like(p) for p in P], [np.zeros_like(p) for p in P]
    for t in range(1, steps + 1):
        a, b, u, vv = P
        z = a[:, None] + b[None, :] + np.outer(vv, u)
        R = W * (1 / (1 + np.exp(-z)) - Y0)
        G = [R.sum(1), R.sum(0) + lam_b * b, (R.T @ vv + lam_uv * u) if two else np.zeros(ni), (R @ u + lam_uv * vv) if two else np.zeros(nj)]
        for k in range(4):
            m[k] = 0.9 * m[k] + 0.1 * G[k]
            v[k] = 0.999 * v[k] + 0.001 * G[k] ** 2
            P[k] = P[k] - 0.1 * (m[k] / (1 - 0.9 ** t)) / ((v[k] / (1 - 0.999 ** t)) ** 0.5 + 1e-8)
    return P


def logit(P):
    return P[0][:, None] + P[1][None, :] + np.outer(P[3], P[2])


def heldout(Y, obs, folds=5, seed=0, grid_b=(0.01, 0.03, 0.1, 0.3, 1.0, 3.0), grid_uv=(0.3, 1.0, 3.0, 10.0)):
    """Held-out log-likelihood per cell (nats) of the 1-D and the 2-D model; ridge strengths picked per model on the same folds."""
    rng = np.random.default_rng(seed)
    fold = rng.integers(0, folds, Y.shape)
    Yz = np.where(obs, Y, 0.0)

    def ll(lam_b, lam_uv):
        tot = 0.0
        for f in range(folds):
            z = logit(fit(Y, (obs & (fold != f)).astype(float), lam_b, lam_uv))
            te = obs & (fold == f)
            tot += -(np.logaddexp(0, -z) * Yz + np.logaddexp(0, z) * (1 - Yz))[te].sum()
        return tot / obs.sum()
    one = {lam: ll(lam, None) for lam in grid_b}
    lb = max(one, key=one.get)
    two = {lam: ll(lb, lam) for lam in grid_uv}
    return {"ll_1d": one[lb], "ll_2d": max(two.values()), "gain": max(two.values()) - one[lb], "lam_b": lb, "lam_uv": max(two, key=two.get),
            "gain_by_ridge": {str(lam): round(v - one[lb], 6) for lam, v in two.items()}}


def rasch_p(Y, lam_b):
    """Success probabilities of the one-axis model fitted to every observed cell."""
    return 1 / (1 + np.exp(-logit(fit(Y, (~np.isnan(Y)).astype(float), lam_b))))


def item_model(Y, names, sims=20, shuffles=5, seed=0):
    obs = ~np.isnan(Y)
    real = heldout(Y, obs)
    rng = np.random.default_rng(seed)
    p = rasch_p(Y, real["lam_b"])
    null = [heldout(np.where(obs, (rng.random(Y.shape) < p).astype(float), np.nan), obs)["gain"] for _ in range(sims)]
    shuf = []
    for _ in range(shuffles):                           # arm labels shuffled within each problem
        Z = Y.copy()
        for i in range(Y.shape[1]):
            o = obs[:, i]
            Z[o, i] = rng.permutation(Y[o, i])
        shuf.append(heldout(Z, obs))
    P = fit(Y, obs.astype(float), real["lam_b"], real["lam_uv"])
    marg = float(np.nanmean(Y))
    base_ll = float(np.nanmean(Y) * np.log(marg) + (1 - np.nanmean(Y)) * np.log(1 - marg))
    sign = np.sign(P[3][np.argmax(abs(P[3]))])
    return {"arms": len(names), "cells": int(obs.sum()), "ll_per_cell_constant": round(base_ll, 5), "ll_per_cell_1d": round(real["ll_1d"], 5),
            "ll_per_cell_2d": round(real["ll_2d"], 5), "gain_2d": round(real["gain"], 7), "ridge": [real["lam_b"], real["lam_uv"]],
            "gain_2d_by_ridge_on_the_bilinear_term": real["gain_by_ridge"],
            "null_gain_rasch_sim": {"n": sims, "mean": round(float(np.mean(null)), 7), "p95": round(float(np.percentile(null, 95)), 7), "max": round(float(max(null)), 7)},
            "shuffled_arm_labels": {"n": shuffles, "ll_per_cell_1d": round(float(np.mean([s["ll_1d"] for s in shuf])), 5),
                                    "gain_2d_mean": round(float(np.mean([s["gain"] for s in shuf])), 7), "gain_2d_max": round(float(max(s["gain"] for s in shuf)), 7)},
            "second_axis_detected": bool(real["gain"] > max(np.percentile(null, 95), 1e-4)),   # 1e-4: at the strongest ridge the 2-D model equals the 1-D one
            "loadings_positive_negative": [int((P[3] * sign > 0.05).sum()), int((P[3] * sign < -0.05).sum())],
            "ability_1d": {n: round(float(x), 2) for n, x in zip(names, fit(Y, obs.astype(float), real["lam_b"])[0])},
            "loading_2d": {n: round(float(x * sign), 2) for n, x in sorted(zip(names, P[3]), key=lambda t: -t[1] * sign)}}


def vote_prediction(A, names, ind, p, arms, edges=(0, 0.1, 0.3, 0.5, 0.7, 0.85, 0.95, 1.0)):
    """One-axis prediction of a vote over 4 samples of an arm that has one sample. g(p) = share of problems the stored vote gets
    right among problems whose per-sample success probability under the fitted Rasch model is p (bins `edges`), from the base + cue
    and the RL families; prediction = sum over problems of g(p of the arm). Checked by predicting each family's vote from the other's g."""
    fams = {"base_cue": "base_vote4", "rl_plain": "rl_vote4"}
    pf = {f: p[[ind.index(f"{f}_s{s}") for s in range(4)]].mean(0) for f in fams}
    vf = {f: A[names.index(v)] for f, v in fams.items()}

    def g(train):
        pp, vv = np.concatenate([pf[f] for f in train]), np.concatenate([vf[f] for f in train])
        b = np.digitize(pp, edges[1:-1])
        share = np.array([vv[b == k].mean() if (b == k).any() else np.nan for k in range(len(edges) - 1)])
        return lambda q: float(np.nansum(share[np.digitize(q, edges[1:-1])]))
    both = g(list(fams))
    return {"check_other_family": {f: {"predicted": round(g([o for o in fams if o != f])(pf[f]), 1), "observed": int(vf[f].sum())} for f in fams},
            "predicted_vote4": {a: {"single": int(np.nansum(A[names.index(a)])), "vote4_predicted": round(both(p[ind.index(a)]), 1)} for a in arms}}


# ---------- readout ----------
def analyse(name):
    d = json.loads((OUT / f"{name}-01" / "vectors.json").read_text())
    man = json.loads((OUT / f"{name}-01" / "manifest.json").read_text())["arms"]
    names = list(d["arms"])
    A = np.array([[np.nan if x is None else x for x in d["arms"][n]] for n in names], float)
    ind = [n for n in names if n not in PARTS]
    Y = A[[names.index(n) for n in ind]]
    ref = "base_cue_s0" if name == "math500" else "base_cue"
    fam = {n: man[n]["family"] for n in names}
    im = item_model(Y, ind)
    p = rasch_p(Y, im["ridge"][0])
    every = list(itertools.combinations(ind, 2))
    extra = [(a, "base_vote4") for a in STACK_ARMS] + [("base_vote4", "rl_plain_s0")] if name == "math500" else []
    T = {(r["a"], r["b"]): r for r in pair_table(A, names, PARTS, every + extra, ref, p)}
    P = lambda a, b: T[a, b] if (a, b) in T else T[b, a]
    out = {"set": name, "n_problems": A.shape[1], "reference": ref, "right": {n: int(np.nansum(A[names.index(n)])) for n in names},
           "null": "B permuted among problems of equal rest score (exact hypergeometric moments), bias and sd from 200 matrices drawn from the fitted Rasch model; "
                   "the spec's 8 equal-count strata and 2,000 permutations failed planted check 1 (z mean -0.98) and were replaced before any real pair was computed"}
    same = [T[q] for q in every if fam[q[0]] == fam[q[1]]]
    diff = [T[q] for q in every if fam[q[0]] != fam[q[1]]]
    out["same_config_pairs"] = {"summary": zsummary(same) if same else None, "pairs": same}
    out["different_arm_pairs"] = {"summary": zsummary(diff), "most_complementary": sorted(diff, key=lambda r: -r["z"])[:10],
                                  "most_alike": sorted(diff, key=lambda r: r["z"])[:10]}
    out["pair_z_matrix"] = {"arms": ind, "z": [[None if a == b else P(a, b)["z"] for b in ind] for a in ind]}
    rer = {}
    for r, v in d["reruns"].items():
        pos = [d["problem_indices"].index(i) for i in v["problem_indices"]]
        first = A[names.index(v["repeats"])][pos]
        rer[r] = {"repeats": v["repeats"], "n": len(pos), "right_first": int(first.sum()), "right_rerun": int(sum(v["scores"])),
                  "problems_scored_differently": int((first != np.array(v["scores"])).sum()),
                  "union": int(np.maximum(first, np.array(v["scores"])).sum())}
    out["same_seed_reruns"] = rer
    solved = np.nansum(A, axis=0)
    rl = [i for i, n in enumerate(names) if fam[n] in ("rl_plain", "rl_cue")]
    nonrl = [i for i in range(len(names)) if i not in rl]
    floor = np.where(solved == 0)[0]
    only = np.where((np.nansum(A[rl], axis=0) > 0) & (np.nansum(A[nonrl], axis=0) == 0))[0]
    ids = lambda ix: {"problem_indices": [d["problem_indices"][i] for i in ix], "unique_ids": [d["unique_ids"][i] for i in ix]}
    out["floor"] = {"arms": len(names), "no_arm_solves": len(floor), "no_arm_solves_ids": ids(floor),
                    "only_rl_solves": len(only), "only_rl_ids": ids(only), "only_rl_right_count_of_rl_arms": [int(np.nansum(A[rl][:, i])) for i in only],
                    "rl_arms": [names[i] for i in rl],
                    "no_arm_without_rl_weights_or_output_solves": int((np.nansum(A[[i for i, n in enumerate(names) if n in NO_RL]], axis=0) == 0).sum()),
                    "arms_without_rl": [n for n in names if n in NO_RL],
                    "solved_by_at_most_2_arms": int((solved <= 2).sum()), "every_arm_solves": int((np.nanmin(A, axis=0) == 1).sum())}
    out["item_model_all_arms"] = im
    if name == "math500":
        out["candidate_pairs"] = [P(a, b) for a, b in CANDIDATES]
        out["with_base_vote4"] = [P(a, "base_vote4") for a in STACK_ARMS]
        out["with_rl_sample0"] = [P(a, "rl_plain_s0") for a in STACK_ARMS + ["base_vote4"]]
        routes = [n for n in ind if fam[n] not in ("rl_plain", "rl_cue") and "theta1." not in n]
        out["largest_unions_of_two_non_rl_arms"] = sorted((P(a, b) for a, b in itertools.combinations(routes, 2)), key=lambda r: -r["union"])[:10]
        out["oracle_union_of_all_non_rl_single_arms"] = {"arms": len(routes), "right": int(np.nanmax(A[[names.index(n) for n in routes]], axis=0).sum())}
        out["pass_at_4"] = {f: int(np.nanmax(A[[names.index(f"{f}_s{s}") for s in range(4)]], axis=0).sum()) for f in ("base_cue", "rl_plain")}
        out["one_axis_vote_prediction"] = vote_prediction(A, names, ind, p, STACK_ARMS + ["rl_cue", "theta0.75_cue"])
        cue = [n for n in ind if man[n]["prompt"] == "cue"]
        out["item_model_cue_arms"] = item_model(Y[[ind.index(n) for n in cue]], cue)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract", action="store_true")
    ap.add_argument("--runs", default="runs")
    a = ap.parse_args()
    if a.extract:
        return extract(pathlib.Path(a.runs))
    head = subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    for name in SETS:
        r = analyse(name)
        out = OUT / f"{name}-01"
        (out / "readout.json").write_text(json.dumps(r, indent=1) + "\n")
        (out / "run.json").write_text(json.dumps({"commit": head, "job_id": None, "gpu": "none (laptop, numpy)", "spec": "studies/rlneurons/specs/SPEC_axis.md",
                                                  "command": ["uv run --no-project --with numpy python -m studies.rlneurons.analysis.axis --extract --runs <runs>",
                                                              "uv run --no-project --with numpy python -m studies.rlneurons.analysis.axis"],
                                                  "inputs": f"{RES}axis/{name}-01/manifest.json (path, commit, sha256, job id of every arm)"}, indent=1) + "\n")
        print(name, json.dumps({k: r[k] for k in ("right", "same_seed_reruns")}))
    examples()


def examples():
    """One floor problem (no arm right) and one problem the reference misses and both arms of the first candidate pair fix, with the
    stored extracted answers of the committed Day-1 #3 rows."""
    d = json.loads((OUT / "math500-01" / "vectors.json").read_text())
    r = json.loads((OUT / "math500-01" / "readout.json").read_text())
    rows = {m: [json.loads(line) for line in (STUDY / "results" / "day1_3" / f"math500_{m}-01" / "rows.jsonl").read_text().splitlines()] for m in ("base_cue", "rl")}
    a, b = CANDIDATES[0]
    fixed = next(i for i, (x, y, z) in enumerate(zip(d["arms"]["base_cue_s0"], d["arms"][a], d["arms"][b])) if (x, y, z) == (0, 1, 1))
    ex = {}
    for key, i in (("floor_scored_wrong_by_every_arm", r["floor"]["no_arm_solves_ids"]["problem_indices"][0]), (f"fixed_by_{a}_and_{b}", fixed)):
        ex[key] = {"problem_index": i, "unique_id": d["unique_ids"][d["problem_indices"].index(i)], "scores": {n: v[d["problem_indices"].index(i)] for n, v in d["arms"].items()},
                   "day1_3_rows": {m: [{k: x[k] for k in ("sample", "seed", "n_new", "cap_hit", "extracted_v3", "score_v3", "gold")} for x in rr
                                       if x["problem_index"] == i and x["attempt"] == 0] for m, rr in rows.items()}}
    (OUT / "math500-01" / "examples.json").write_text(json.dumps(ex, indent=1) + "\n")


if __name__ == "__main__":
    main()
