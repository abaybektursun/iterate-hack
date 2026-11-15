"""codecopy-01: shared direct test of rival pair round-14/s6 (spec: studies/theory/specs/SPEC_direct_codecopy.md).

    cd <checkout holding runs/> && uv run --no-project --with numpy python <worktree>/studies/theory/analysis/direct_codecopy.py

Reads runs/<job>/answers.jsonl (538 problems, one sample per cell) from the current directory; writes
studies/theory/results/direct/codecopy-01/ in the worktree holding this script.
"""
import json
import pathlib

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
RES = ROOT / "studies/rlneurons/results"
OUT = ROOT / "studies/theory/results/direct/codecopy-01"
CELLS = {  # name: committed cell folder (its run.json names the job)
    "base_cue": "code1/base_cue-01",
    "rl_51": "code1/rl_plain-01", "rl_52": "xreward/code_hosts_s52/rl_plain-01", "rl_53": "xreward/code_hosts_s53/rl_plain-01",
    "top8x1_51": "xreward/code_dial/code_top8_code31-01", "top8x1_52": "xreward/code_hosts_s52/code_top8_code31-01",
    "top8x1_53": "xreward/code_hosts_s53/code_top8_code31-01", "top8x1.5_51": "xreward/code_dial/code_top8x1.5_code31-01",
    "top8x2_51": "xreward/code_dial/code_top8x2_code31-01",
    "base_plain": "code1/base_plain-01", "base_mathcue": "code1/base_mathcue-01", "rand8x1.5": "xreward/code_dial/code_rand8x1.5_code31-01",
}
RL = ["rl_51", "rl_52", "rl_53"]
EDIT = ["top8x1_51", "top8x1_52", "top8x1_53", "top8x1.5_51", "top8x2_51"]
NULL = ["base_plain", "base_mathcue", "rand8x1.5"]
RANGES = {"a": (0.70, 1.0), "b": (0.0, 0.34), "null": (0.38, 0.66)}
B = 10000


def job(cell):
    return json.load(open(RES / CELLS[cell] / "run.json"))["job_id"]


def posted(cell):
    return json.load(open(RES / CELLS[cell] / "metrics.json"))["counts"]["all"]["passed"]


def load(j):
    rows = [json.loads(line) for line in open(pathlib.Path("runs") / j / "answers.jsonl")]
    return {r["uid"]: r for r in rows}


def count_matches(rows, cell):
    return sum(r["passed"] for r in rows.values()) == posted(cell)


rows = {c: load(job(c)) for c in CELLS}
uids = sorted(rows["base_cue"])
assert len(uids) == 538 and all(sorted(rows[c]) == uids for c in rows)

# Instrument check: every cell reproduces its posted count; a wrong file must not.
for c in CELLS:
    assert count_matches(rows[c], c), (c, posted(c))
assert not count_matches(rows["rl_52"], "top8x1_52"), "count check passed on the wrong file"



def ok(r):
    """The plan's pass: all tests passed, no cap hit, a code block."""
    return bool(r["passed"]) and not r["cap_hit"] and r["mode"] != "none"


def readout(passfn):
    P = {c: np.array([passfn(rows[c][u]) for u in uids]) for c in CELLS}
    rl_fails = sum(~P[c] for c in RL)
    L = np.where(P["base_cue"] & (rl_fails >= 2))[0]
    e = np.mean([P[c][L] for c in EDIT], axis=0)
    z = np.mean([P[c][L] for c in NULL], axis=0)
    idx = np.random.default_rng(0).integers(0, len(L), size=(B, len(L)))
    ci = [float(x) for x in np.percentile(e[idx].mean(1), [5, 95])]
    ci0 = [float(x) for x in np.percentile(z[idx].mean(1), [5, 95])]
    return P, rl_fails, L, e, z, ci, ci0


P, rl_fails, L, e, z, ci, ci0 = readout(ok)
S, S0 = e.mean(), z.mean()
n = 5 * len(L)
_, _, L_raw, e_raw, _, ci_raw, _ = readout(lambda r: bool(r["passed"]))


def verdict(r):
    lo, hi = RANGES[r]
    if n < 50:
        return "undecided"
    if lo <= ci[0] and ci[1] <= hi:
        return "holds"
    if ci[1] < lo or ci[0] > hi:
        return "refuted"
    return "undecided"


v = {r: verdict(r) for r in ("a", "b")}
if "holds" in v.values():  # an interval wholly in one rival's range refutes the other
    v = {r: ("holds" if v[r] == "holds" else "refuted") for r in v}

metrics = {
    "statistic": "mean over L of the pass rate of 5 Code top-8 edit samples (1x at 51M/52M/53M, 1.5x, 2x; Code cue)",
    "L_size": int(len(L)), "n_rows": n, "S": float(S), "ci90": ci,
    "null": {"value": float(S0), "ci90": ci0, "cells": NULL},
    "ranges": RANGES, "verdict": v,
    "per_cell_on_L": {c: float(P[c][L].mean()) for c in EDIT + NULL + RL + ["base_cue"]},
    "edit_minus_null": float(S - S0),
    "e_histogram": {f"{k}/5": int((np.round(e * 5) == k).sum()) for k in range(6)},
    "rl_fail_count_on_L": {"2of3": int((rl_fails[L] == 2).sum()), "3of3": int((rl_fails[L] == 3).sum())},
    "posted_counts_reproduced": {c: posted(c) for c in CELLS},
    "bootstrap": {"resamples": B, "unit": "problem in L", "rng": "numpy default_rng(0)", "percentiles": [5, 95]},
    "raw_passed_reading": {"L_size": int(len(L_raw)), "S": float(e_raw.mean()), "ci90": ci_raw,
                           "note": "stored passed field alone (3 passed rows hit the cap); not the plan's rule"},
    "inputs": {c: f"runs/{job(c)}/answers.jsonl" for c in CELLS},
    "raw_rows_read": ("10 problems in L read (HumanEval/55, 65, 141, 151, 77; Mbpp/109, 123, 133, 14, 125 before the cap "
                      "amendment): every edit and RL-Code failure is a finished block that fails a test (wrong fib base case, "
                      "wrong rotation count, find_Volume renamed find_volume), not a cap hit or missing block. The edit "
                      "fails and passes on different problems than RL-Code (HumanEval/65: RL 1 of 3, edit 5 of 5; "
                      "HumanEval/55: RL 1 of 3, edit 0 of 5), so its rate on L sits at a base resample's, not RL-Code's."),
}


def show(i, label):
    u = uids[i]
    return {"label": label, "uid": u, "e": float(np.mean([P[c][i] for c in EDIT])),
            "cells": {c: {"passed": rows[c][u]["passed"], "cap_hit": rows[c][u]["cap_hit"], "mode": rows[c][u]["mode"],
                          "n_new": rows[c][u]["n_new"], "code_head": rows[c][u]["code"][:300],
                          "stderr_tail": rows[c][u]["stderr_tail"][-200:], "pass_plan_rule": ok(rows[c][u])}
                      for c in ["base_cue"] + RL + EDIT}}


hi_i = L[np.argmax(e)]
lo_i = L[np.argmin(e)]
examples = [show(hi_i, "in L, edit samples pass (counts toward S as passes)"),
            show(lo_i, "in L, edit samples fail (counts toward S as fails)")]

OUT.mkdir(parents=True, exist_ok=True)
json.dump(metrics, open(OUT / "metrics.json", "w"), indent=1)
json.dump(examples, open(OUT / "examples.json", "w"), indent=1)
print(json.dumps({k: metrics[k] for k in ["L_size", "n_rows", "S", "ci90", "null", "verdict", "per_cell_on_L",
                                          "e_histogram", "rl_fail_count_on_L"]}, indent=1))
for i in L[:10]:
    print(uids[i], "rl", [int(P[c][i]) for c in RL], "edit", [int(P[c][i]) for c in EDIT], "null", [int(P[c][i]) for c in NULL])
