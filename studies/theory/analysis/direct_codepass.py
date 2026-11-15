"""Direct test of round-13/s4-a, pass rate among finished answers with a code block (specs/SPEC_direct_codepass.md).

    cd <checkout holding runs/> && uv run --no-project --with numpy python <worktree>/studies/theory/analysis/direct_codepass.py

Reads runs/<job>/answers.jsonl (538 problems, one sample per cell) from the current directory. F = no cap hit and a code
block. r = passed among F / |F|; dC, dM = r(edit) - r(random 1.5x) in points; 90 % paired bootstrap over problems.
Planted control: Math's pass column replaced by Code's must give ratio 1.0 and verdict refuted.
Writes studies/theory/results/direct/codepass-01/.
"""
import json
import pathlib
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / "studies" / "theory" / "results" / "direct" / "codepass-01"
JOBS = {"random": "abaybektursun-1115-101457-ef2c", "code": "abaybektursun-1115-101434-4511",
        "math": "abaybektursun-1115-101508-33f0", "base": "abaybektursun-1114-170304-c03c"}
B, RNG = 10000, np.random.default_rng(0)


def load(job):
    rows = [json.loads(line) for line in open(pathlib.Path("runs") / job / "answers.jsonl")]
    return {r["uid"]: r for r in rows}


rows = {k: load(j) for k, j in JOBS.items()}
uids = sorted(rows["random"])
assert len(uids) == 538 and all(sorted(rows[k]) == uids for k in rows)
P = {k: np.array([rows[k][u]["passed"] for u in uids], int) for k in rows}
F = {k: np.array([(not rows[k][u]["cap_hit"]) and rows[k][u]["mode"] != "none" for u in uids], int) for k in rows}
assert all(((P[k] == 1) <= (F[k] == 1)).all() for k in ("random", "code", "math")), "a pass outside F"  # base: 2 cap-hit passes, left out of its r
IDX = RNG.integers(0, 538, (B, 538))


def rates(p, f, idx=None):
    """r in points for the full set (idx None) or for each bootstrap draw."""
    if idx is None:
        return 100 * (p * f).sum() / f.sum()
    return 100 * (p * f)[idx].sum(1) / f[idx].sum(1)


def q90(x):
    return [float(np.quantile(x, 0.05)), float(np.quantile(x, 0.95))]


def readout(Pm, F):
    r = {k: rates(Pm[k], F[k]) for k in ("random", "code", "math", "base")}
    rb = {k: rates(Pm[k], F[k], IDX) for k in ("random", "code", "math")}
    dC, dM = r["code"] - r["random"], r["math"] - r["random"]
    dCb, dMb = rb["code"] - rb["random"], rb["math"] - rb["random"]
    point = dC >= 3.0 and dM < 0.5 * dC
    ints = bool(q90(dCb)[0] > 0 and q90(dMb - 0.5 * dCb)[1] < 0)
    verdict = ("holds" if ints else "holds (point only)") if point else "refuted"
    return {"rate_pts": {k: float(v) for k, v in r.items()},
            "F": {k: int(F[k].sum()) for k in r}, "passed_in_F": {k: int((Pm[k] * F[k]).sum()) for k in r},
            "dC_pts": float(dC), "dC_90": q90(dCb), "dM_pts": float(dM), "dM_90": q90(dMb),
            "ratio_dM_over_dC": float(dM / dC), "ratio_90": q90(dMb / dCb),
            "dM_minus_half_dC_90": q90(dMb - 0.5 * dCb), "verdict": verdict}


main = readout(P, F)
planted = readout({**P, "math": P["code"]}, {**F, "math": F["code"]})  # Math := Code: must give ratio 1.0, refuted
assert abs(planted["ratio_dM_over_dC"] - 1.0) < 1e-9 and planted["verdict"] == "refuted"

# Secondary: problems in F of both the edit and random (removes the selection effect of finishing harder problems).
both = {}
for k in ("code", "math"):
    m = F[k] * F["random"]
    rb_e, rb_r = rates(P[k], m, IDX), rates(P["random"], m, IDX)
    both[k] = {"n": int(m.sum()), "edit_pts": float(rates(P[k], m)), "random_pts": float(rates(P["random"], m)),
               "d_pts": float(rates(P[k], m) - rates(P["random"], m)), "d_90": q90(rb_e - rb_r)}
# Recovered answers: in F under the edit but not under random; their pass rate vs random's own r.
rec = {k: {"n": int((F[k] * (1 - F["random"])).sum()), "passed": int((P[k] * F[k] * (1 - F["random"])).sum())} for k in ("code", "math")}

OUT.mkdir(parents=True, exist_ok=False)
out = {"n_problems": 538, "rule": "holds iff dC >= 3.0 pts and dM < 0.5 dC (point); intervals 90 % paired bootstrap, 10,000 draws",
       "null": {"random_rate_pts": main["rate_pts"]["random"], "rival_b_ratio": 0.54},
       **main, "both_finished": both, "recovered_vs_random": rec,
       "planted_control_math_equals_code": {"ratio": planted["ratio_dM_over_dC"], "verdict": planted["verdict"]}}
(OUT / "readout.json").write_text(json.dumps(out, indent=1))


def item(k, u):
    r = rows[k][u]
    return {"cell": k, "job": JOBS[k], "uid": u, "prompt": r["prompt"], "text_tail": r["text"][-1500:], "code": r["code"],
            "cap_hit": r["cap_hit"], "mode": r["mode"], "passed": r["passed"], "exit": r["exit"], "stderr_tail": r["stderr_tail"],
            "random_same_problem": {"cap_hit": rows["random"][u]["cap_hit"], "mode": rows["random"][u]["mode"], "passed": rows["random"][u]["passed"]}}


# Supports: Code passes where random finished with a block and failed. Against: Math passes where random finished and failed.
sup = next(u for u in uids if P["code"][uids.index(u)] and F["random"][uids.index(u)] and not P["random"][uids.index(u)])
aga = next(u for u in uids if P["math"][uids.index(u)] and F["random"][uids.index(u)] and not P["random"][uids.index(u)])
(OUT / "examples.json").write_text(json.dumps({"supports": item("code", sup), "against": item("math", aga)}, indent=1))
commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
(OUT / "run.json").write_text(json.dumps({"commit": commit, "command": " ".join(["python"] + sys.argv), "input_jobs": JOBS,
                                          "inputs": "runs/<job>/answers.jsonl (gpu.py get copies, not committed)"}, indent=1))
print(json.dumps(out, indent=1))
