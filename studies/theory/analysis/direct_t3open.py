"""Direct test t3open (theory round 15, round-15/account-3/c1). Spec: studies/theory/specs/SPEC_direct_t3open.md.

Mean of (T3 plain right - T1 cued right) on MATH-500 problems whose T3 answer opens deliberatively.
Run: python3 studies/theory/analysis/direct_t3open.py
"""
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ROWS = ROOT / "studies/rlneurons/results/rln4/t1_t3_items-01/per_problem.json"
OUT = ROOT / "studies/theory/results/direct/t3open-01"
OPENER = re.compile(r"\b(Okay|Alright|Hmm|Let me|Let's|I need to)\b")
EQUATION = re.compile(r"[$=]|\\\(|\\\[")
RANGE_A3 = (-0.15, 0.10)
RANGE_NULL = (-0.65, -0.22)


def flagged(start):
    s = start[:240]
    m = OPENER.search(s)
    if m is None:
        return False
    e = EQUATION.search(s)
    return e is None or m.start() < e.start()


def mean(xs):
    return sum(xs) / len(xs)


def boot(ds, n_boot=10_000, seed=0):
    rng = random.Random(seed)
    means = sorted(mean(rng.choices(ds, k=len(ds))) for _ in range(n_boot))
    return [means[int(0.05 * n_boot)], means[int(0.95 * n_boot) - 1]]


def main():
    rows = json.loads(ROWS.read_text())
    assert len(rows) == 500
    flag = [r for r in rows if flagged(r["t3_start"])]
    rest = [r for r in rows if not flagged(r["t3_start"])]
    d_flag = [r["t3_right"] - r["t1_right"] for r in flag]
    d_rest = [r["t3_right"] - r["t1_right"] for r in rest]
    stat, ci = mean(d_flag), boot(d_flag)
    null, null_ci = mean(d_rest), boot(d_rest)
    n = len(flag)
    if n >= 50 and RANGE_A3[0] <= ci[0] and ci[1] <= RANGE_A3[1]:
        verdict = "holds"
    elif ci[1] < RANGE_A3[0] or ci[0] > RANGE_A3[1]:
        verdict = "refuted"
    else:
        verdict = "undecided"
    metrics = {
        "test": "t3open", "mechanism": "round-15/account-3/c1",
        "statistic": "mean over flagged problems of (T3 plain right - T1 cued right), grader v3, fraction of problems",
        "value": stat, "ci90": ci, "n": n,
        "share_flagged": n / len(rows),
        "flagged_t3_right": sum(r["t3_right"] for r in flag), "flagged_t1_right": sum(r["t1_right"] for r in flag),
        "null_value_unflagged": null, "null_ci90": null_ci, "n_unflagged": len(rest),
        "unflagged_t3_right": sum(r["t3_right"] for r in rest), "unflagged_t1_right": sum(r["t1_right"] for r in rest),
        "overall_t3_minus_t1": mean([r["t3_right"] - r["t1_right"] for r in rows]),
        "range_account3": RANGE_A3, "range_null": RANGE_NULL, "verdict": verdict,
        "flag_rule": "case-sensitive \\b(Okay|Alright|Hmm|Let me|Let's|I need to)\\b in t3_start[:240], before the first $, =, \\( or \\[",
        "bootstrap": "10,000 resamples of problems, seed 0, 5th to 95th percentile",
        "rows": str(ROWS.relative_to(ROOT)),
    }
    keys = ["problem_index", "t3_right", "t1_right", "t3_extracted_v3", "t1_extracted_v3", "t3_start", "t1_start"]
    right = next(r for r in flag if r["t3_right"] == 1)
    wrong = next(r for r in flag if r["t3_right"] == 0)
    examples = {"note": "flagged rows (T3 opens deliberatively); right and wrong refer to T3 under grader v3",
                "right": {k: right[k] for k in keys}, "wrong": {k: wrong[k] for k in keys}}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=1) + "\n")
    (OUT / "examples.json").write_text(json.dumps(examples, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps(metrics, indent=1))


if __name__ == "__main__":
    main()
