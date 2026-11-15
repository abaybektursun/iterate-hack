"""Exchange-rate table (specs/SPEC_rate.md): every MATH-500 arm as one ability shift in logits on the Rasch axis of
analysis/axis.py, its tokens per problem and training signal; transfer of a shift to the 328 harder problems; predictions for
cells that had not finished when they were filed.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.rate predict|transfer|table|score

  predict   results/rate/predict-01/predictions.json (run once, before the held-out results are read; refuses to overwrite)
  transfer  results/rate/transfer-01/readout.json (leave-one-arm-out, MATH-500 -> hard328)
  table     results/rate/math500-01/{table.json,table.md,readout.json}
  score     results/rate/predict-01/scored.json from predictions.json and the observed counts in OBSERVED
"""
from __future__ import annotations

import argparse
import datetime
import itertools
import json
import subprocess

import numpy as np

from studies.rlneurons.analysis import axis as X

OUT = X.STUDY / "results" / "rate"
LAM = {"math500": 0.3, "hard328": 0.1}          # the ridges axis.py selected (readout.json item_model_all_arms.ridge)
BOOT, SEED = 2000, 0
BASE4 = [f"base_cue_s{s}" for s in range(4)]
RL4 = [f"rl_plain_s{s}" for s in range(4)]
# test arm -> its vectors on MATH-500 (pooled) ; the same name is its vector on hard328
BOTH = {"rl_plain": RL4, "rl_cue": ["rl_cue"], "theta0.25_cue": ["theta0.25_cue"], "theta0.5_cue": ["theta0.5_cue"], "code_cue": ["code_cue"]}
sig = lambda z: 1 / (1 + np.exp(-z))
lg = lambda p: float(np.log(p / (1 - p)))


def load(name):
    """{arm: 0/1 vector with nan where the arm has no score}, the single-sample arm names, and the same-seed rerun on hard328."""
    d = json.loads((X.OUT / f"{name}-01" / "vectors.json").read_text())
    V = {n: np.array([np.nan if x is None else x for x in v], float) for n, v in d["arms"].items()}
    if name == "hard328":
        V["base_cue_rerun"] = np.array(d["reruns"]["base_cue_rerun_s0"]["scores"], float)
    return V, [n for n in V if n not in X.PARTS]


def day1_3(model):
    """Restart and vote-after-restart vectors of a Day-1 #3 run, and the votes over every subset of k = 2, 3 of its 4 samples."""
    from studies.rlneurons.analysis import day1_vote as D
    f = X.STUDY / "results" / "day1_3" / f"math500_{model}-01"
    pp = json.loads((f / "readout.json").read_text())["per_problem"]
    V = {"restart": np.array(pp["restart"], float)[None], "vote4_restart": np.array(pp["vote_after_restart"], float)[None]}
    rows = [json.loads(l) for l in (f / "rows.jsonl").read_text().splitlines()]
    att0 = {(r["problem_index"], r["sample"]): r for r in rows if r["attempt"] == 0}
    n = 1 + max(i for i, _ in att0)
    tok = {"single": sum(att0[i, 0]["n_new"] for i in range(n)) / n, "all_samples": sum(r["n_new"] for r in att0.values()) / n / 4}
    for k in (2, 3, 4):
        V[f"vote{k}"] = np.array([[D.vote([att0[i, s] for s in c])["score"] for i in range(n)] for c in itertools.combinations(range(4), k)], float)
    assert V["vote4"].sum() == np.array(pp["vote"]).sum()
    return V, tok


def difficulties(rows, lam):
    Y = np.vstack(rows)
    return X.fit(Y, (~np.isnan(Y)).astype(float), lam)[1]


def solve(cnt, target, b):
    """a with sum_i cnt_i sigmoid(a + b_i) = target; cnt (n,) or (B, n), target scalar or (B,). Bisection, 50 steps."""
    cnt, target = np.atleast_2d(cnt), np.atleast_1d(target).astype(float)
    lo, hi = np.full(len(target), -15.0), np.full(len(target), 15.0)
    for _ in range(50):
        mid = (lo + hi) / 2
        up = (cnt * sig(mid[:, None] + b[None, :])).sum(1) < target
        lo, hi = np.where(up, mid, lo), np.where(up, hi, mid)
    return (lo + hi) / 2


def ability(y, b, w=None):
    """Maximum-likelihood ability of the pooled 0/1 vectors y ((n,) or (k, n), nan = no score) given item difficulties b.
    w: (B, n) bootstrap counts of the problems -> (B,) abilities; None -> one float."""
    y = np.atleast_2d(y)
    cnt, tot = (~np.isnan(y)).sum(0).astype(float), np.nansum(y, 0)
    if w is None:
        return float(solve(cnt, tot.sum(), b)[0])
    return solve(w * cnt, (w * tot).sum(1), b)


def acc(y):
    return float(np.nanmean(np.atleast_2d(y)))


def boot(n, seed=SEED):
    return np.random.default_rng(seed).multinomial(n, np.full(n, 1 / n), BOOT).astype(float)


def rules(acc5, ref5, ref3, n3):
    """The three rules that use totals only: marginal logit, point, relative error. Right count of n3."""
    return {"M": n3 * float(sig(lg(ref3) + lg(acc5) - lg(ref5))), "P": n3 * (ref3 + acc5 - ref5), "R": n3 * (1 - (1 - ref3) * (1 - acc5) / (1 - ref5))}


def transfer(b5, S5, S3, extra3, lam3):
    """Leave-one-arm-out transfer. S5, S3: {arm: pooled vectors on set 1, set 2}, both with the key "ref"; extra3: other set-2
    vectors used only in the difficulty fit. Returns one row per test arm (observed count on set 2 and the five predictions)."""
    arms = [a for a in S5 if a != "ref"]
    d5 = {a: ability(S5[a], b5) - ability(S5["ref"], b5) for a in arms}
    n3 = np.atleast_2d(S3["ref"]).shape[1]
    out = {}
    for j in arms:
        b3 = difficulties([S3[a] for a in S3 if a != j] + extra3, lam3)
        a_ref = ability(S3["ref"], b3)
        oth = [a for a in arms if a != j]
        d3 = np.array([ability(S3[a], b3) - a_ref for a in oth])
        x = np.array([d5[a] for a in oth])
        c = float(x @ d3 / (x @ x))
        out[j] = {"observed": acc(S3[j]) * n3, "d_set1": d5[j], "c": c, "L1": float(sig(a_ref + d5[j] + b3).sum()), "Lc": float(sig(a_ref + c * d5[j] + b3).sum()),
                  **rules(acc(S5[j]), acc(S5["ref"]), acc(S3["ref"]), n3)}
    mae = {r: float(np.mean([abs(v[r] - v["observed"]) for v in out.values()])) for r in ("L1", "Lc", "M", "P", "R")}
    return out, mae


def real_sets():
    V5, ind5 = load("math500")
    V3, ind3 = load("hard328")
    b5 = difficulties([V5[n] for n in ind5], LAM["math500"])
    S5 = {"ref": np.vstack([V5[n] for n in BASE4])} | {a: np.vstack([V5[n] for n in v]) for a, v in BOTH.items()}
    S3 = {"ref": np.vstack([V3["base_cue"], V3["base_cue_rerun"]])} | {a: V3[a] for a in BOTH}
    return V5, ind5, V3, b5, S5, S3


def cmd_transfer():
    V5, ind5, V3, b5, S5, S3 = real_sets()
    rows, mae = transfer(b5, S5, S3, [V3["base_plain"]], LAM["hard328"])
    r = lambda x: round(float(x), 2)
    b3 = difficulties([S3[a] for a in S3] + [V3["base_plain"]], LAM["hard328"])
    pb = sig(ability(S3["ref"], b3) + b3)
    out = {"test_arms": len(rows), "reference": "pooled base + cue (4 samples on MATH-500: 410.5 of 500; 2 runs on hard328: 162 of 328)",
           "rerun_noise_problems": abs(float(np.nansum(V3["base_cue"]) - np.nansum(V3["base_cue_rerun"]))),
           "binomial_sd_one_cell": r(np.sqrt((pb * (1 - pb)).sum())),
           "mean_abs_error_problems": {k: r(v) for k, v in mae.items()}, "rows": {a: {k: r(v) for k, v in row.items()} for a, row in rows.items()},
           "rules": "L1 Rasch logit; Lc Rasch logit x c (c fitted on the other test arms); M marginal logit; P same point gain; R same relative error"}
    (OUT / "transfer-01").mkdir(parents=True, exist_ok=True)
    (OUT / "transfer-01" / "readout.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


PARTIAL = ("origin/claude/swarm-literature-review-60a281", X.RES + "day1_3/hard328_partial246_rl_plain_s4r0-01/readout.json")


def cmd_predict(nn):
    """nn 1: the cells running when the study started. nn 2: two finished cells found afterwards and not yet opened (result-1dedfe)."""
    path = OUT / f"predict-0{nn}" / "predictions.json"
    assert not path.exists(), "predictions are filed once"
    V5, ind5, V3, b5, S5, S3 = real_sets()
    rng = np.random.default_rng(SEED)
    b3 = difficulties([S3[a] for a in S3] + [V3["base_plain"]], LAM["hard328"])
    a5 = lambda y, w=None: ability(y, b5, w)
    d5 = np.array([a5(S5[a]) - a5(S5["ref"]) for a in BOTH])
    d3 = np.array([ability(S3[a], b3) - ability(S3["ref"], b3) for a in BOTH])
    c = float(d5 @ d3 / (d5 @ d5))
    c_loo = [float(np.delete(d5, k) @ np.delete(d3, k) / (np.delete(d5, k) @ np.delete(d5, k))) for k in range(len(d5))]
    W5 = boot(500)
    DB, tokB = day1_3("base_cue")
    DR, tokR = day1_3("rl")
    base, rl = S5["ref"], S5["rl_plain"]

    def cell328(name, ref3, d, dB, acc5, ref5, status="prediction", note="", idx=slice(None)):
        """Rule Lc on hard328: reference vectors ref3 on the 328, MATH-500 shift d with its draws dB (BOOT,)."""
        a_ref, cnt = ability(ref3, b3), (~np.isnan(np.atleast_2d(ref3))).sum(0).astype(float)
        p_ref = sig(a_ref + b3)
        a_refB = solve(np.tile(cnt, (BOOT, 1)), (rng.random((BOOT, int(cnt.max()), 328)) < p_ref).sum((1, 2)), b3)   # parametric redraw of the reference
        cB = rng.choice(c_loo, BOOT)
        draws = (rng.random((BOOT, 328)) < sig(a_refB[:, None] + (cB * dB)[:, None] + b3[None, :]))[:, idx].sum(1)
        n = len(b3[idx])
        base_rules = rules(acc5, ref5, acc(np.atleast_2d(ref3)[:, idx]), n) if acc5 is not None else {}
        if n < 328:
            return {"cell": name, "set": "hard328 subset", "n": n, "status": status, "note": note, "shift_math500_logits": round(float(d), 3),
                    "predicted_right": round(float(sig(a_ref + c * d + b3)[idx].sum()), 1), "interval80": [float(np.percentile(draws, 10)), float(np.percentile(draws, 90))],
                    "reference_right_subset": round(acc(np.atleast_2d(ref3)[:, idx]) * n, 1), "baseline_point": round(base_rules["P"], 1),
                    "baseline_relative_error": round(base_rules["R"], 1), "baseline_marginal_logit": round(base_rules["M"], 1)}
        return {"cell": name, "set": "hard328", "n": 328, "status": status, "note": note, "shift_math500_logits": round(float(d), 3),
                "predicted_right": round(float(sig(a_ref + c * d + b3).sum()), 1), "interval80": [float(np.percentile(draws, 10)), float(np.percentile(draws, 90))],
                "L1_uncalibrated": round(float(sig(a_ref + d + b3).sum()), 1), "reference_right_328": round(acc(ref3) * 328, 1),
                "baseline_point": round(base_rules["P"], 1) if base_rules else None, "baseline_relative_error": round(base_rules["R"], 1) if base_rules else None,
                "baseline_marginal_logit": round(base_rules["M"], 1) if base_rules else None}

    sh = lambda y, ref: (a5(y) - a5(ref), a5(y, W5) - a5(ref, W5))
    cells = []
    if nn == 2:
        ids = json.loads((X.OUT / "hard328-01" / "vectors.json").read_text())["problem_indices"]
        sub = set(json.loads(X.show(*PARTIAL))["problem_indices"])
        idx = np.array([i in sub for i in ids])
        d, dB = sh(DB["vote4"], base)
        cells.append(cell328("base + cue, vote over 4, no restart (sameraslan's run, result-1dedfe)", S3["ref"], d, dB, acc(DB["vote4"]), acc(base)))
        d, dB = sh(DR["vote4"], rl)
        cells.append(cell328(f"RL plain, vote over 4, no restart, on the {idx.sum()} problems that finished (result-1dedfe)", V3["rl_plain"], d, dB, acc(DR["vote4"]), acc(rl), idx=idx))
    if nn == 1:
        d, dB = sh(DB["vote4_restart"], base)
        cells.append(cell328("base + cue, vote over 4 after restart", S3["ref"], d, dB, acc(DB["vote4_restart"]), acc(base)))
        d, dB = sh(DR["vote4_restart"], rl)
        cells.append(cell328("RL plain, vote over 4 after restart", V3["rl_plain"], d, dB, acc(DR["vote4_restart"]), acc(rl),
                             note="the text of work-1a972a, read before filing, says an earlier hard328 RL run without restarts had 246 of 328 (result-1dedfe, not opened); the prediction is the rule's output, not adjusted"))
        d, dB = sh(V5["shots_rl"], base)
        cells.append(cell328("base + cue + 3 RL-written solved problems (shots_rl)", S3["ref"], d, dB, acc(V5["shots_rl"]), acc(base)))
        d, dB = sh(V5["top8_plain"], base)
        d_hi = a5(V5["theta0.5_cue"]) - a5(base)
        dB = dB + (rng.random(BOOT) < 0.5) * rng.random(BOOT) * max(0.0, d_hi - d)
        cells.append(cell328("base + top 8 directions, cue", S3["ref"], d, dB, acc(V5["top8_plain"]), acc(base),
                             note="shift of top8_plain (no cue cell on MATH-500); upper end widened to the theta 0.5 cue shift"))
        dv, _ = sh(DB["vote4"], base)
        for arm in ("V cue", "V plain"):
            cells.append(cell328(f"vote distillation {arm}", S3["ref"], dv / 2, rng.uniform(0, dv, BOOT), None, None, "category prior, not a measured shift",
                                 "trained on MATH-500, so no MATH-500 shift; prior: half the vote-over-4 shift, between 0 and the full vote shift"))
        for arm in ("U cue", "U plain"):
            cells.append(cell328(f"unfiltered self-training control {arm}", S3["ref"], 0.0, rng.uniform(-0.3, 0.3, BOOT), None, None, "category prior, not a measured shift",
                                 "prior: no shift, between -0.3 and +0.3 logits"))
        for arm in ("shots_base", "shots_code", "shots_rl"):
            y = V5[arm]
            m = ~np.isnan(y)
            p = sig(a5(y) + b5[m])
            half = 1.2816 * 1.25 * float(np.sqrt(2 * (p * (1 - p)).sum()))
            cells.append({"cell": f"{arm}, second draw of the 3 examples", "set": "math500", "n": int(m.sum()), "status": "prediction", "note": "same ability as the first draw; predicted rate applies if the second draw masks other problems",
                          "predicted_right": float(np.nansum(y)), "predicted_rate": round(float(np.nanmean(y)), 4),
                          "interval80": [round(float(np.nansum(y)) - half, 1), round(float(np.nansum(y)) + half, 1)], "baseline_point": float(np.nansum(y))})
        d, dB = sh(DB["vote4"], base)
        aS, aSB = a5(V5["sft1_cue"]), a5(V5["sft1_cue"], W5)
        draws = (rng.random((BOOT, 500)) < sig((aSB + dB)[:, None] + b5[None, :])).sum(1)
        cells.append({"cell": "Think-SFT cue, vote over 4", "set": "math500", "n": 500, "status": "prediction",
                      "note": "on file from axis.py (one_axis_vote_prediction): 471.5 +/- 7; this row: sft1_cue ability + the base vote-over-4 shift in logits",
                      "on_file_axis": 471.5, "on_file_axis_interval": [464.5, 478.5], "shift_math500_logits": round(float(d), 3),
                      "predicted_right": round(float(sig(aS + d + b5).sum()), 1), "interval80": [float(np.percentile(draws, 10)), float(np.percentile(draws, 90))],
                      "baseline_point": round(float(np.nansum(V5["sft1_cue"]) + 500 * (acc(DB["vote4"]) - acc(base))), 1),
                      "baseline_relative_error": round(500 * (1 - (1 - acc(V5["sft1_cue"])) * (1 - acc(DB["vote4"])) / (1 - acc(base))), 1)})
    out = {"filed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "code_commit_parent": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip(),
           "commit": "the commit that adds this file (see run.json)", "rule": "Lc: sum_i sigmoid(a_ref328 + c d + b_i); specs/SPEC_rate.md",
           "c": round(c, 3), "c_leave_one_out": [round(x, 3) for x in c_loo],
           "calibration_arms": {a: {"shift_math500": round(float(x), 3), "shift_hard328": round(float(y), 3)} for a, x, y in zip(BOTH, d5, d3)}, "cells": cells}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))

SIGNAL = {"base_cue": "none", "shots_base": "own samples (in context)", "shots_rl": "RL reward (RL text in context)", "shots_code": "RL reward (RL text in context)",
          "random_cue": "none (control)", "rand8_plain": "none (control)", "sft1_cue": "SFT data", "sft1_plain": "SFT data"}      # every other family: RL reward (weights)


def tokens(name, arm):
    """Mean generated tokens per problem of a single-sample arm, from the metrics.json of its run folder (at its commit)."""
    kind, src, folder, ref = X.SETS[name][arm][:4]
    if kind == "rows":
        rows = [json.loads(l) for l in (X.STUDY.parents[1] / src[0]).read_text().splitlines()]
        t = [r["n_new"] for r in rows if r["attempt"] == 0 and r["sample"] == src[1]]
        return sum(t) / len(t)
    m = json.loads(X.show(X.REF.get(ref), X.RES + folder + "/metrics.json"))
    return m["counts"]["mean_generated_tokens"] if "counts" in m else m["mean_generated_tokens"]


def cmd_table():
    V5, ind5 = load("math500")
    man = json.loads((X.OUT / "math500-01" / "manifest.json").read_text())["arms"]
    b5 = difficulties([V5[n] for n in ind5], LAM["math500"])
    W = boot(500)
    fam = {"base_cue": (np.vstack([V5[n] for n in BASE4]), *day1_3("base_cue"), "base_cue"), "rl_plain": (np.vstack([V5[n] for n in RL4]), *day1_3("rl"), "rl")}
    s0, s0B = ability(V5["base_cue_s0"], b5), ability(V5["base_cue_s0"], b5, W)
    rows = []

    def add(arm, what, y, tok, signal, family=None, test_time=False):
        a, aB = ability(y, b5), ability(y, b5, W)
        row = {"arm": arm, "what": what, "right": round(acc(y) * int((~np.isnan(np.atleast_2d(y)[0])).sum()), 1), "n": int((~np.isnan(np.atleast_2d(y)[0])).sum()),
               "ability": round(a, 3), "shift_logits": round(a - s0, 3), "interval95": [round(float(x), 3) for x in np.percentile(aB - s0B, [2.5, 97.5])],
               "tokens_per_problem": round(tok), "signal": signal}
        if test_time:
            pool, _, tk, _ = fam[family]
            if arm.endswith("_restart") and "vote" not in arm:          # the restart row uses sample 0 only: compare with sample 0
                pool, tk = pool[0], {"all_samples": tk["single"]}
            d, dB, extra = a - ability(pool, b5), aB - ability(pool, b5, W), tok - tk["all_samples"]
            row |= {"shift_vs_own_single_logits": round(d, 3), "shift_vs_own_single_interval95": [round(float(x), 3) for x in np.percentile(dB, [2.5, 97.5])],
                    "extra_tokens": round(extra), "logits_per_1000_extra_tokens": round(1000 * d / extra, 4),
                    "points_vs_own_single": round(100 * (acc(y) - acc(pool)), 2)}
        rows.append(row)

    for n in ind5:
        add(n, man[n]["what"], V5[n], tokens("math500", n), SIGNAL.get(man[n]["family"], "RL reward (weights)"))
    for f, (pool, D, tk, model) in fam.items():
        label, sg = ("base + cue", "none") if f == "base_cue" else ("RL plain", "RL reward (weights)")
        ro = json.loads((X.STUDY / "results" / "day1_3" / f"math500_{model}-01" / "readout.json").read_text())["rows"]
        add(f"{f}_restart", f"{label}, restart up to 2", D["restart"], ro["restart"]["tokens_per_problem"], sg, f, True)
        for k in (2, 3, 4):
            add(f"{f}_vote{k}", f"{label}, vote over {k} samples" + ("" if k == 4 else f" (mean of the {len(D[f'vote{k}'])} subsets)"), D[f"vote{k}"], k * tk["all_samples"], sg, f, True)
        add(f"{f}_vote4_restart", f"{label}, vote over 4 after restart", D["vote4_restart"], ro["vote_after_restart"]["tokens_per_problem"], sg, f, True)
    add("base_cue_tie_short", "base + cue, vote over 4, ties to the shortest finished answer", V5["base_tie_short"], 4 * fam["base_cue"][2]["all_samples"], "none", "base_cue", True)
    rows.sort(key=lambda r: -r["shift_logits"])
    R = {r["arm"]: r for r in rows}
    floor = {f: round(float(np.std([R[n]["ability"] for n in names], ddof=1)), 3) for f, names in (("base_cue", BASE4), ("rl_plain", RL4))}
    a0, a1 = ability(fam["base_cue"][0], b5), R["rl_cue"]["ability"]
    theta = {t: R[f"theta{t}_cue"]["ability"] for t in (0.25, 0.5, 0.75, 1.25, 1.5)} | {0.0: a0, 1.0: a1}
    sd1 = float(np.mean([np.std(ability(V5[n], b5, W)) for n in ("theta0.25_cue", "theta0.5_cue", "theta0.75_cue")]))
    readout = {"reference": "base + cue sample 0 (405 of 500)", "ability_base_cue_s0": round(s0, 3), "ability_base_cue_pooled_4": round(a0, 3),
               "noise_floor_sd_of_4_same_config_samples_logits": floor, "bootstrap_sd_of_one_single_sample_ability_logits": round(sd1, 3),
               "theta_sweep_cue": {str(t): {"ability": round(a, 3), "shift_vs_pooled_base": round(a - a0, 3), "linear_0_to_1": round(t * (a1 - a0), 3),
                                            "minus_linear": round(a - a0 - t * (a1 - a0), 3)} for t, a in sorted(theta.items())},
               "random_difference_control_shift_vs_pooled_base": round(R["random_cue"]["ability"] - a0, 3),
               "H3_theta_0.5_off_the_line_in_noise_sd": round((theta[0.5] - a0 - 0.5 * (a1 - a0)) / floor["base_cue"], 1)}
    md = ["| Method | Right | Shift, logits [95 %] | Tokens per problem | Signal | Logits per 1,000 extra tokens |", "|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['what']} | {r['right']:g} of {r['n']} | {r['shift_logits']:+.2f} [{r['interval95'][0]:+.2f}, {r['interval95'][1]:+.2f}] | {r['tokens_per_problem']:,} | {r['signal']} | "
                  + (f"{r['logits_per_1000_extra_tokens']:.3f} ({r['shift_vs_own_single_logits']:+.2f} over its own single sample, {r['extra_tokens']:,} extra)" if "extra_tokens" in r else "") + " |")
    out = OUT / "math500-01"
    out.mkdir(parents=True, exist_ok=True)
    (out / "table.json").write_text(json.dumps(rows, indent=1))
    (out / "table.md").write_text("\n".join(md) + "\n")
    (out / "readout.json").write_text(json.dumps(readout, indent=1))
    print("\n".join(md))
    print(json.dumps(readout, indent=1))


# cell name in a predictions.json -> (observed right, where it was read), filled in after the prediction's commit was pushed
SW = "origin/claude/swarm-literature-review-60a281:studies/rlneurons/results/day1_3/"
OBSERVED = {
    "base + cue, vote over 4, no restart (sameraslan's run, result-1dedfe)": (179, SW + "hard328_base_cue_s4r0-01/readout.json rows.vote"),
    "RL plain, vote over 4, no restart, on the 246 problems that finished (result-1dedfe)": (161, SW + "hard328_partial246_rl_plain_s4r0-01/readout.json rows.vote"),
    "shots_rl, second draw of the 3 examples": (404, "job abaybektursun-1114-195350-bc00 (shots1/rl_b.json), done; score_v3 of answers.jsonl without problems 3, 5, 6 (406 of 500 with them)"),
    "shots_base, second draw of the 3 examples": (405, "job abaybektursun-1114-195357-6936 (shots1/base_b.json), done; score_v3 of answers.jsonl without problems 3, 5, 6 (408 of 500 with them)"),
}


def cmd_score():
    rows = []
    for nn in (1, 2):
        d = json.loads((OUT / f"predict-0{nn}" / "predictions.json").read_text())
        for c in d["cells"]:
            row = {"cell": c["cell"], "set": c["set"], "filed": f"predict-0{nn}", "filed_utc": d["filed_utc"], "status": c["status"], "predicted_right": c["predicted_right"], "interval80": c["interval80"]}
            if c["cell"] in OBSERVED:
                obs, src = OBSERVED[c["cell"]]
                row |= {"observed": obs, "source": src, "error": round(c["predicted_right"] - obs, 1), "inside_interval80": bool(c["interval80"][0] <= obs <= c["interval80"][1]),
                        "error_baselines": {k: round(c[k] - obs, 1) for k in ("baseline_point", "baseline_relative_error", "baseline_marginal_logit", "L1_uncalibrated", "on_file_axis") if c.get(k) is not None}}
            else:
                row["observed"] = None
            rows.append(row)
    done = [r for r in rows if r["observed"] is not None]
    mae = lambda rs, k: round(float(np.mean([abs(r["error"] if k == "Lc_filed" else r["error_baselines"][k]) for r in rs])), 2)
    hard = [r for r in done if r["set"].startswith("hard328")]
    out = {"scored": len(done), "not_finished": len(rows) - len(done), "inside_interval80": sum(r["inside_interval80"] for r in done),
           "hard328_transfer_cells": {"n": len(hard), "mean_abs_error": {k: mae(hard, k) for k in ("Lc_filed", "baseline_point", "baseline_relative_error", "baseline_marginal_logit")}},
           "math500_second_draw_cells": {"n": len(done) - len(hard), "mean_abs_error": {"filed (same as the first draw)": mae([r for r in done if r not in hard], "Lc_filed")}},
           "cells": rows}
    (OUT / "scored-01").mkdir(parents=True, exist_ok=True)
    (OUT / "scored-01" / "readout.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != "cells"}, indent=1))
    for r in rows:
        print(r["cell"], "|", r["predicted_right"], r["interval80"], "| observed", r["observed"], r.get("error"), r.get("inside_interval80"), r.get("error_baselines"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["predict", "predict2", "transfer", "table", "score"])
    {"predict": lambda: cmd_predict(1), "predict2": lambda: cmd_predict(2), "transfer": cmd_transfer, "table": cmd_table, "score": cmd_score}[ap.parse_args().cmd]()


if __name__ == "__main__":
    main()
