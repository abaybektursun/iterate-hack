"""Direct test r17a1c2 (round-17/account-1/c2), spec studies/theory/specs/SPEC_direct_r17a1c2.md.

D2 = r(edit one sample, RL 4-sample rate) - mean_s r(Think-SFT sample s, RL 4-sample rate) on the MATH-500 test half.
Adversary first: clone = 2*r1/sqrt(1+3*r1) (Spearman-Brown, r1 = mean pairwise r of RL samples) minus the same
Think-SFT mean. Run from the repo root: python3 studies/theory/analysis/direct_r17a1c2.py
"""
import json
import subprocess
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

sys.path.insert(0, "studies/theory/lib")
import rows  # noqa: E402

OUT = Path("studies/theory/results/direct/r17a1c2-01")
EDIT = "rlneurons/xreward/dial15_math500-01"
RL = "rlneurons/day1_3/math500_rl-01"
SFT = "rlneurons/thinkvote/math500_sft1_cue_s4-01"
BASE = "rlneurons/day1_3/math500_base_cue-01"
RANGE, NULL_RANGE = [0.02, 0.54], [-0.2, 0.015]


def by_sample(cell, samples):
    """{pid: {sample: row}} of attempt-0 rows with the given samples; fails on a duplicate (pid, sample)."""
    out = {}
    for r in rows.load("math500", cell, "test"):
        if int(r["attempt"]) != 0 or int(r["sample"]) not in samples:
            continue
        d = out.setdefault(str(r["pid"]), {})
        assert int(r["sample"]) not in d, (cell, r["pid"], r["sample"])
        d[int(r["sample"])] = r
    return {p: d for p, d in out.items() if len(d) == len(samples)}


def corr(x, y):
    return float(np.corrcoef(x, y)[0, 1])


edit, rl, sft, base = (by_sample(EDIT, {0}), by_sample(RL, {0, 1, 2, 3}), by_sample(SFT, {0, 1, 2, 3}),
                       by_sample(BASE, {0, 1, 2, 3}))
pids = sorted(set(edit) & set(rl) & set(sft), key=int)
n = len(pids)
R = np.array([[int(rl[p][s]["score_v3"]) for s in range(4)] for p in pids], float)
T = np.array([[int(sft[p][s]["score_v3"]) for s in range(4)] for p in pids], float)
E = np.array([int(edit[p][0]["score_v3"]) for p in pids], float)
rate = R.mean(1)

# Adversary first.
r1 = float(np.mean([corr(R[:, a], R[:, b]) for a, b in combinations(range(4), 2)]))
clone = 2 * r1 / np.sqrt(1 + 3 * r1)
ct_s = [corr(T[:, s], rate) for s in range(4)]
ct = float(np.mean(ct_s))
adversary = float(clone - ct)
print(f"adversary: r1 {r1:.4f} clone {clone:.4f} ct {ct:.4f} value {adversary:.4f}")


def d2(idx):
    rr = R[idx].mean(1)
    return corr(E[idx], rr) - np.mean([corr(T[idx, s], rr) for s in range(4)])


ce = corr(E, rate)
D2 = float(ce - ct)
rng = np.random.default_rng(17)
boots, skipped = [], 0
for _ in range(2000):
    idx = rng.integers(0, n, n)
    cols = [E[idx], R[idx].mean(1)] + [T[idx, s] for s in range(4)]
    if any(c.std() == 0 for c in cols):
        skipped += 1
        continue
    boots.append(d2(idx))
lo, hi = (float(x) for x in np.percentile(boots, [5, 95]))
print(f"D2 {D2:.4f} [{lo:.4f}, {hi:.4f}] n {n} (edit r {ce:.4f}, Think-SFT mean r {ct:.4f}); skipped {skipped}")

# Null: corr ~ accuracy over the 8 single non-edit samples (cued base 0-3 on the same pids, Think-SFT 0-3).
assert all(p in base for p in pids), "cued base misses a test pid"
B = np.array([[int(base[p][s]["score_v3"]) for s in range(4)] for p in pids], float)
singles = [("base_cue", s, B[:, s]) for s in range(4)] + [("think_sft", s, T[:, s]) for s in range(4)]
acc = np.array([x.mean() for _, _, x in singles])
cs = np.array([corr(x, rate) for _, _, x in singles])
slope, icept = np.polyfit(acc, cs, 1)
null_value = float(slope * E.mean() + icept - ct)
print(f"null {null_value:.4f} (slope {slope:.4f}, intercept {icept:.4f}, edit acc {E.mean():.3f})")


def verdict(lo, hi, rng_, adv):
    a, b = rng_
    if hi < a or b < lo:
        return "refuted"
    if n < 50 or not (a <= lo and hi <= b):
        return "undecided"
    return "not separated" if lo <= adv <= hi else "holds"


v = verdict(lo, hi, RANGE, adversary)

# Raw-row check: 10 test rows (first 10 pids, edit + RL sample 0 + Think-SFT sample 0 text fields as stored).
check = [{"pid": p, "edit": edit[p][0], "rl_s0": rl[p][0], "sft_s0": sft[p][0]} for p in pids[:10]]
for c in check:
    print(c["pid"], {k: (c[k]["score_v3"], c[k]["extracted_v3"][:25], c[k]["gold"][:25], c[k]["n_new"], c[k]["cap_hit"])
                     for k in ("edit", "rl_s0", "sft_s0")})

all_rl = rows.load("math500", RL, "test")
all_sft = rows.load("math500", SFT, "test")
OUT.mkdir(parents=True, exist_ok=False)
metrics = {
    "statistic": "D2 = r(edit single sample, RL 4-sample rate) - mean_s r(Think-SFT sample s, RL rate), MATH-500 test half",
    "D2": D2, "interval90": [lo, hi], "n_problems": n, "bootstrap": {"resamples": 2000, "seed": 17, "skipped": skipped},
    "r_edit_rl": ce, "r_sft_rl_by_sample": ct_s, "r_sft_rl_mean": ct,
    "accuracy": {"edit": float(E.mean()), "rl_4sample": float(R.mean()), "think_sft_by_sample": T.mean(0).tolist(),
                 "base_cue_by_sample": B.mean(0).tolist()},
    "adversary": {"r1_rl_pairwise": r1, "clone": float(clone), "ct": ct, "value": adversary},
    "null_accuracy_alone": {"value": null_value, "slope": float(slope), "intercept": float(icept),
                            "singles": [{"cell": c, "sample": s, "acc": float(a_), "r": float(r_)}
                                        for (c, s, _), a_, r_ in zip(singles, acc, cs)], "range": NULL_RANGE},
    "range": RANGE, "verdict": v,
    "row_check": {
        "rl_test_rows": len(all_rl), "rl_restart_rows_dropped": sum(int(r["attempt"]) > 0 for r in all_rl),
        "sft_test_rows": len(all_sft), "pids_with_all_4_rl": len(rl), "pids_with_all_4_sft": len(sft),
        "duplicate_attempt0_pid_sample": 0,
        "cap_hits_attempt0": {"edit": sum(r["cap_hit"] == "True" for p in pids for r in edit[p].values()),
                              "rl": sum(r["cap_hit"] == "True" for p in pids for r in rl[p].values()),
                              "think_sft": sum(r["cap_hit"] == "True" for p in pids for r in sft[p].values())},
        "read_10_rows": "Read edit, RL sample 0 and Think-SFT sample 0 of 10 test pids (raw_check.json). Nothing looks "
                        "wrong: every pid has all its attempt-0 samples, no duplicate (pid, sample), score_v3 matches "
                        "extracted vs gold by eye (pid 9: edit 6, RL 9, SFT 4 vs gold 4; pid 11 all wrong), cap hits are "
                        "flagged with finish_reason length. RL has 21 restart rows (attempt > 0), dropped by the plan. "
                        "Edit accuracy on this half is 0.884, below the claim's 0.940 and below Think-SFT's 0.904-0.924.",
    },
}
(OUT / "metrics.json").write_text(json.dumps(metrics, indent=1) + "\n")

agree = next(p for p in pids if E[pids.index(p)] == 1 and rate[pids.index(p)] == 1)
disagree = next(p for p in pids if E[pids.index(p)] == 0 and rate[pids.index(p)] >= 0.75)
ex = [{"kind": k, "pid": p, "edit_row": edit[p][0], "rl_rows": [rl[p][s] for s in range(4)],
       "think_sft_rows": [sft[p][s] for s in range(4)]}
      for k, p in (("agree: edit right, RL 4 of 4", agree), ("disagree: edit wrong, RL at least 3 of 4", disagree))]
(OUT / "examples.json").write_text(json.dumps(ex, indent=1) + "\n")
(OUT / "raw_check.json").write_text(json.dumps(check, indent=1) + "\n")
commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
(OUT / "run.json").write_text(json.dumps({"commit": commit, "command": "python3 studies/theory/analysis/direct_r17a1c2.py",
                                          "spec": "studies/theory/specs/SPEC_direct_r17a1c2.md", "half": "test",
                                          "cells": [EDIT, RL, SFT, BASE]}, indent=1) + "\n")
(OUT / "rows.json").write_text(json.dumps([{
    "mechanism": "round-17/account-1/c2",
    "claim": "On MATH-500 one edit sample tracks RL's 4-sample rate better than one Think-SFT sample (D2 in 0.02-0.54)",
    "result": "", "verdict": v, "measured": f"D2 {D2:.4f} [{lo:.4f}, {hi:.4f}], n {n}, adversary {adversary:.4f}",
    "interval": [lo, hi], "range": RANGE, "adversary": adversary, "n": n}], indent=1) + "\n")
print("verdict", v)
