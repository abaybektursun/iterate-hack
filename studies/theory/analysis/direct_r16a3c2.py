"""Direct test r16a3c2 (theory round 16, round-16/account-3/c2). Spec: studies/theory/specs/SPEC_direct_r16a3c2.md.

D_m21 = mean(m21 right - T3 right), grader v3, on problems 0-249 where both answers are non-deliberative (flag rule of
result-1f98b0). The adversary's value (T3 flag only, every m21 row counted) is computed first.
Run from the worktree root (needs runs/abaybektursun-1115-103050-eae1/answers.jsonl, the m21 job's raw rows):
PYTHONPATH=. uv run --no-project --with numpy --with math-verify==0.9.0 --with antlr4-python3-runtime==4.11 \
    python studies/theory/analysis/direct_r16a3c2.py
"""
import hashlib
import json
import re
from pathlib import Path

import numpy as np

from studies.theory.analysis.direct_t3open import flagged

T13 = Path("studies/rlneurons/results/rln4/t1_t3_items-01/per_problem.json")
CELL = Path("studies/theory/results/experiments/cell-r9-m21-01/per_problem.json")
RAW = Path("runs/abaybektursun-1115-103050-eae1/answers.jsonl")
RAW_SHA = "2900bc85a4e971128dfe4132d017bb5825ff9888a6a4fdfbe00b8334e3da29d4"
OUT = Path("studies/theory/results/direct/r16a3c2-01")
OPENER_WORD = re.compile(r"\b(Okay|Hmm|Alright)\b")
RANGES = {"round-16/account-3/c2": [0.1, 0.4], "null": [-0.07, 0.07]}


def ci90(d):
    rng = np.random.default_rng(16)
    d = np.asarray(d, dtype=float)
    means = d[rng.integers(0, len(d), size=(10_000, len(d)))].mean(axis=1)
    return [float(np.percentile(means, 5)), float(np.percentile(means, 95))]


def main():
    assert hashlib.sha256(RAW.read_bytes()).hexdigest() == RAW_SHA
    t3 = {r["problem_index"]: r for r in json.loads(T13.read_text()) if r["problem_index"] < 250}
    cell = {r["problem_index"]: r for r in json.loads(CELL.read_text())}
    raw = {r["problem_index"]: r for r in map(json.loads, RAW.read_text().splitlines())}
    assert sorted(t3) == sorted(cell) == sorted(raw) == list(range(250))
    assert all(raw[i]["score_v3"] == cell[i]["score_v3"] for i in range(250)), "raw rows disagree with per_problem.json"
    assert sum(cell[i]["score_v3"] for i in range(250)) == 157 and sum(t3[i]["t3_right"] for i in range(250)) == 107

    # 1) adversary's value first: T3 flag only, m21 opening ignored
    t3_nd = [i for i in range(250) if not flagged(t3[i]["t3_start"])]
    adv = float(np.mean([cell[i]["score_v3"] for i in t3_nd]) - np.mean([t3[i]["t3_right"] for i in t3_nd]))
    print("adversary A =", round(adv, 4), "n", len(t3_nd))

    # 2) the statistic: both non-deliberative
    both = [i for i in t3_nd if not flagged(raw[i]["text"])]
    d = [cell[i]["score_v3"] - t3[i]["t3_right"] for i in both]
    stat, ci, n = float(np.mean(d)), ci90(d), len(both)
    print("D_m21 =", round(stat, 4), ci, "n", n)

    m21_delib_on_t3nd = [i for i in t3_nd if flagged(raw[i]["text"])]
    d_other = [cell[i]["score_v3"] - t3[i]["t3_right"] for i in m21_delib_on_t3nd]
    empty_t3 = [i for i in both if t3[i]["t3_start"] == ""]
    # raw-row reading (step d): rows that enter as non-deliberative only through a rule artifact or an empty answer
    late_opener = [i for i in both if OPENER_WORD.search(raw[i]["text"][:240])]
    m21_empty = [i for i in both if raw[i]["text"].strip() == ""]
    rest = [i for i in both if i not in late_opener + m21_empty + empty_t3]
    reading = {
        "seen": "10 rows read (problems 2-30). No cap hits, all m21 finish 'stop', 76 distinct seeds. Problem 12: m21 opens "
                "' in the form $Answer$.\\n\\nOkay, let's try...', non-deliberative only because a $ precedes 'Okay'. "
                "Problem 22: m21 text empty (0 new tokens), counted wrong. Problem 2: m21 drifts off-topic, no answer.",
        "m21_okay_hmm_alright_after_equation_sign": {"n": len(late_opener), "problems": late_opener,
                                                     "sum_diff": sum(cell[i]["score_v3"] - t3[i]["t3_right"] for i in late_opener)},
        "m21_empty_text": {"n": len(m21_empty), "problems": m21_empty,
                           "sum_diff": sum(cell[i]["score_v3"] - t3[i]["t3_right"] for i in m21_empty)},
        "t3_empty_start": {"n": len(empty_t3), "problems": empty_t3,
                           "sum_diff": sum(cell[i]["score_v3"] - t3[i]["t3_right"] for i in empty_t3)},
        "sensitivity_without_these": {"n": len(rest), "value": float(np.mean([cell[i]["score_v3"] - t3[i]["t3_right"] for i in rest]))},
        "note": f"post hoc check, not the plan's statistic: {len(both) - len(rest)} of the {len(both)} rows (one side empty, or m21 "
                f"opens with Okay/Hmm/Alright after a leading equation sign) carry a net "
                f"{sum(d) - sum(cell[i]['score_v3'] - t3[i]['t3_right'] for i in rest):+d} of the {sum(d):+d}",
    }
    metrics = {
        "test": "r16a3c2", "mechanism": "round-16/account-3/c2",
        "statistic": "mean over problems 0-249 with both answers non-deliberative of (m21 right - T3 right), grader v3, fraction",
        "adversary": {"value": adv, "n": len(t3_nd),
                      "computation": "T3 flag only (flagged() of direct_t3open.py on t3_start[:240]); on the T3-non-deliberative "
                                     "problems, mean(m21 score_v3) - mean(t3_right), every m21 row counted whatever its opening",
                      "m21_right": sum(cell[i]["score_v3"] for i in t3_nd), "t3_right": sum(t3[i]["t3_right"] for i in t3_nd)},
        "value": stat, "ci90": ci, "n": n, "n_planned": 65,
        "m21_right": sum(cell[i]["score_v3"] for i in both), "t3_right": sum(t3[i]["t3_right"] for i in both),
        "accuracy_only_value": adv,
        "complement_m21_deliberative_on_t3_nondeliberative": {"value": float(np.mean(d_other)), "n": len(d_other)},
        "n_t3_empty_start_in_set": len(empty_t3),
        "m21_cap_hits_in_set": sum(raw[i]["cap_hit"] for i in both),
        "t3_cap_hits_in_set": sum(t3[i]["t3_cap_hit"] for i in both),
        "m21_empty_extraction_in_set": sum(not raw[i]["extracted_v3"] for i in both),
        "raw_reading": reading,
        "departures": "n 76, not the planned 65 (same rule and files; the plan's count was an estimate). m21 opening text read from the "
                      "job's raw answers.jsonl, since the committed per_problem.json has no text. No other departure.",
        "ranges": RANGES,
        "flag_rule": "flagged() imported from studies/theory/analysis/direct_t3open.py: case-sensitive "
                     "\\b(Okay|Alright|Hmm|Let me|Let's|I need to)\\b in the first 240 characters before the first $, =, \\( or \\[",
        "bootstrap": "10,000 resamples of problems, numpy default_rng(16), 5th-95th percentile",
        "inputs": {"t3": str(T13), "m21_scores": str(CELL), "m21_text": f"{RAW} (sha256 {RAW_SHA}, not committed)"},
        "both_set": both,
    }
    keys_t3 = ["t3_start", "t3_extracted_v3", "t3_right", "t3_cap_hit"]

    def ex(i):
        return {"problem_index": i, "input": raw[i]["prompt"], "gold": raw[i]["gold"],
                "m21_output_first_1500": raw[i]["text"][:1500], "m21_extracted_v3": raw[i]["extracted_v3"],
                "m21_score_v3": raw[i]["score_v3"], **{k: t3[i][k] for k in keys_t3},
                "difference": raw[i]["score_v3"] - t3[i]["t3_right"]}

    pos = next(i for i in both if cell[i]["score_v3"] - t3[i]["t3_right"] == 1)
    zero = next(i for i in both if cell[i]["score_v3"] - t3[i]["t3_right"] <= 0)
    examples = {"note": "both rows enter the statistic; one counted +1 (m21 right, T3 wrong), one counted 0 or -1",
                "counted_plus_one": ex(pos), "counted_zero_or_minus": ex(zero)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=1, ensure_ascii=False) + "\n")
    (OUT / "examples.json").write_text(json.dumps(examples, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in metrics.items() if k != "both_set"}, indent=1))


if __name__ == "__main__":
    main()
