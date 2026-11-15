"""Direct test hostcap (round-15/account-1/c1): median over matrices of
cap_right(Code 3.1 change, Math 3.1 top-8 input subspace) / cap_right(Think-SFT change, same subspace).
Spec: studies/theory/specs/SPEC_direct_hostcap.md. Run: python3 studies/theory/analysis/direct_hostcap.py"""
import json
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
INP = ROOT / "studies/theory/data/direct_host/cap_v1.json"
OUT = ROOT / "studies/theory/results/direct/hostcap-01"
ACCOUNT = [2.0, 60.0]
NULL = [0.5, 1.5]
B = 10000


def boot_median(x, rng):
    idx = rng.integers(0, len(x), size=(B, len(x)))
    meds = np.median(x[idx], axis=1)
    return [float(np.percentile(meds, 5)), float(np.percentile(meds, 95))]


def ratio(rows, a, b, target):
    num = np.array([r["cap"][f"{a}>{target}"]["cap_right"] for r in rows])
    den = np.array([r["cap"][f"{b}>{target}"]["cap_right"] for r in rows])
    return num, den, num / den


def main():
    d = json.loads(INP.read_text())
    rows = d["rows"]
    assert len(rows) == 224, len(rows)
    rng = np.random.default_rng(0)

    code, think, r = ratio(rows, "code31", "think_sft", "math31")
    value = float(np.median(r))
    ci = boot_median(r, rng)
    n = len(r)

    if ACCOUNT[0] <= ci[0] and ci[1] <= ACCOUNT[1] and n >= 50:
        verdict = "holds"
    elif ci[1] < ACCOUNT[0] or ci[0] > ACCOUNT[1]:
        verdict = "refuted"
    else:
        verdict = "undecided"

    by_module = {}
    for m in sorted({x["module"] for x in rows}):
        sel = np.array([x["module"] == m for x in rows])
        by_module[m] = {"n": int(sel.sum()), "median_ratio": float(np.median(r[sel]))}

    other_targets = {}
    for t in ["math30", "base_w", "if30", "general30"]:
        _, _, rt = ratio(rows, "code31", "think_sft", t)
        other_targets[t] = {"median_ratio": float(np.median(rt)), "ci90": boot_median(rt, rng)}

    metrics = {
        "mechanism": "round-15/account-1/c1",
        "spec": "studies/theory/specs/SPEC_direct_hostcap.md",
        "input": str(INP.relative_to(ROOT)),
        "statistic": "median over matrices of cap_right(code31>math31) / cap_right(think_sft>math31)",
        "value": value,
        "ci90": ci,
        "bootstrap": f"percentile, {B} resamples over matrices, numpy seed 0",
        "n_matrices": n,
        "null_value": 1.0,
        "null_range": NULL,
        "account_range": ACCOUNT,
        "verdict": verdict,
        "value_vs_null_range": "inside" if NULL[0] <= value <= NULL[1] else ("above" if value > NULL[1] else "below"),
        "secondary": {
            "ratio_of_means": float(code.mean() / think.mean()),
            "mean_cap_right_code31_in_math31": float(code.mean()),
            "mean_cap_right_think_sft_in_math31": float(think.mean()),
            "n_ratio_above_1": int((r > 1).sum()),
            "n_ratio_above_2": int((r >= 2).sum()),
            "ratio_quantiles_5_25_75_95": [float(q) for q in np.percentile(r, [5, 25, 75, 95])],
            "median_ratio_by_module": by_module,
            "median_ratio_other_targets_code31_over_think_sft": other_targets,
        },
    }
    OUT.mkdir(parents=True, exist_ok=False)
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=1) + "\n")

    order = np.argsort(r)
    picks = {"median_matrix": int(order[n // 2]), "largest_ratio_matrix": int(order[-1])}
    examples = []
    for label, i in picks.items():
        x = rows[i]
        examples.append({
            "label": label, "name": x["name"], "module": x["module"], "layer": x["layer"], "shape": x["shape"],
            "cap_right_code31>math31": x["cap"]["code31>math31"]["cap_right"],
            "cap_right_think_sft>math31": x["cap"]["think_sft>math31"]["cap_right"],
            "ratio": float(r[i]),
        })
    (OUT / "examples.json").write_text(json.dumps(examples, indent=1) + "\n")

    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True)
    run = {"commit": commit.stdout.strip(), "command": "python3 studies/theory/analysis/direct_hostcap.py",
           "job": f"offline; rows from job {d['job']}"}
    (OUT / "run.json").write_text(json.dumps(run, indent=1) + "\n")
    print(json.dumps(metrics, indent=1))


if __name__ == "__main__":
    main()
