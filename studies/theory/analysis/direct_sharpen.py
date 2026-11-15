# /// script
# dependencies = ["numpy"]
# ///
"""Direct test of round-13/s4-b (SPEC_direct_sharpen.md): do Code top-8 1.5x's extra passes over the cued base
land in the base's own solved set (plain or Math cue) as often as a random rank-8 1.5x edit's extra passes?

Run from the repository root after `uv run tools/gpu.py get <job>` for the five jobs:
  uv run studies/theory/analysis/direct_sharpen.py
"""
import json
import subprocess
from pathlib import Path

import numpy as np

JOBS = {
    "base_cue": "abaybektursun-1114-170304-c03c",
    "base_plain": "abaybektursun-1114-170258-388e",
    "base_mathcue": "abaybektursun-1114-170309-b137",
    "code15": "abaybektursun-1115-101434-4511",
    "rand15": "abaybektursun-1115-101457-ef2c",
}
RUNS = Path("/Users/abaybektursun/projects/iterate-hack/runs")
OUT = Path("studies/theory/results/direct/sharpen-01")


def load(job):
    return {r["uid"]: r for r in map(json.loads, open(RUNS / job / "answers.jsonl"))}


rows = {k: load(j) for k, j in JOBS.items()}
uids = sorted(rows["base_cue"])
for k in rows:
    assert sorted(rows[k]) == uids, k
P = {k: np.array([bool(rows[k][u]["passed"]) for u in uids]) for k in rows}
# committed pass counts must match the rows
assert [int(P[k].sum()) for k in JOBS] == [317, 222, 326, 399, 331], [int(P[k].sum()) for k in JOBS]

U = P["base_plain"] | P["base_mathcue"]
fail = ~P["base_cue"]


def f(gain, w):
    g = gain & fail
    return (w * (g & U)).sum() / (w * g).sum()


def stats(w):
    fE, fR = f(P["code15"], w), f(P["rand15"], w)
    return fE, fR, fE - fR, (w * (fail & U)).sum() / (w * fail).sum()


ones = np.ones(len(uids))
fE, fR, D, floor = stats(ones)
rng = np.random.default_rng(0)
boot = []
for _ in range(10000):
    w = np.bincount(rng.integers(0, len(uids), len(uids)), minlength=len(uids)).astype(float)
    boot.append(stats(w))
boot = np.array(boot)
ci = lambda i: [float(np.percentile(boot[:, i], 5)), float(np.percentile(boot[:, i], 95))]

GE, GR = P["code15"] & fail, P["rand15"] & fail
planted = f(P["base_mathcue"], ones)  # in U by construction
verdict = "undecided (null saturated)" if fR > 0.90 else ("refuted" if D < -0.10 else "holds")
readout = {
    "n_problems": len(uids),
    "U": int(U.sum()),
    "base_cue_fail": int(fail.sum()),
    "base_cue_fail_in_U": int((fail & U).sum()),
    "G_E": int(GE.sum()), "G_E_in_U": int((GE & U).sum()),
    "G_R": int(GR.sum()), "G_R_in_U": int((GR & U).sum()),
    "G_E_and_G_R": int((GE & GR).sum()),
    "f_E": float(fE), "f_E_ci90": ci(0),
    "f_R_null": float(fR), "f_R_ci90": ci(1),
    "D": float(D), "D_ci90": ci(2),
    "floor_random_cue_failure_in_U": float(floor),
    "planted_base_mathcue_f": float(planted),
    "threshold": "refuted if D < -0.10; undecided if f_R > 0.90",
    "ci_contains_threshold": bool(ci(2)[0] < -0.10 < ci(2)[1]),
    "verdict": verdict,
}
OUT.mkdir(parents=True, exist_ok=True)
json.dump(readout, open(OUT / "readout.json", "w"), indent=1)
json.dump({u: {k: bool(P[k][i]) for k in JOBS} for i, u in enumerate(uids)}, open(OUT / "per_problem.json", "w"))


def ex(u, why):
    r = rows["code15"][u]
    return {"uid": u, "why": why, "prompt": r["prompt"][-600:], "code15_output_tail": r["text"][-1200:],
            "code15_passed": bool(r["passed"]), "base_cue_passed": bool(rows["base_cue"][u]["passed"]),
            "base_plain_passed": bool(rows["base_plain"][u]["passed"]),
            "base_mathcue_passed": bool(rows["base_mathcue"][u]["passed"])}


sup = [u for i, u in enumerate(uids) if GE[i] and U[i]][0]
ag = [u for i, u in enumerate(uids) if GE[i] and not U[i]][0]
json.dump([ex(sup, "Code 1.5x extra pass inside U: the base solves it under another prompt (supports sharpening)"),
           ex(ag, "Code 1.5x extra pass outside U: no base prompt solved it (goes against sharpening)")],
          open(OUT / "examples.json", "w"), indent=1)

commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
json.dump({"spec": "studies/theory/specs/SPEC_direct_sharpen.md", "commit_of_spec": commit,
           "command": "uv run studies/theory/analysis/direct_sharpen.py",
           "inputs": {k: f"runs/{j}/answers.jsonl (Modal volume, uv run tools/gpu.py get)" for k, j in JOBS.items()},
           "bootstrap": "10,000 resamples of the 538 problems, numpy default_rng(0), 90 % percentile interval",
           "board": "work-8e9805"}, open(OUT / "run.json", "w"), indent=1)
print(json.dumps(readout, indent=1))
for i, u in enumerate(uids):
    if GE[i] or GR[i]:
        print(u, {k: int(P[k][i]) for k in JOBS}, "U" if U[i] else "-")
