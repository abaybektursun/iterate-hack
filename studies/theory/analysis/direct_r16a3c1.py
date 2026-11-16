"""Direct test r16a3c1 (theory round 16, round-16/account-3/c1). Spec: studies/theory/specs/SPEC_direct_r16a3c1.md.

D = mean over problems of (right rate of the problem's non-deliberative step-100 plain samples - T3 right), on problems
where T3 is non-deliberative and at least one of the 4 step-100 plain samples is. The adversary's value (all 4 samples,
whatever their opening) is computed first.
Run from the worktree root (needs the raw answers under runs/, see the spec):
PYTHONPATH=. uv run --no-project --with numpy --with math-verify==0.9.0 --with antlr4-python3-runtime==4.11 python studies/theory/analysis/direct_r16a3c1.py
"""
import json
import re
import subprocess
from pathlib import Path

import numpy as np

from studies.theory.analysis.direct_t3open import EQUATION, flagged as flagged_t3open

ROOT = Path(__file__).resolve().parents[3]
CK = ROOT / "studies/rlneurons/results/ckptcue"
T3_ROWS = ROOT / "studies/rlneurons/results/rln4/t1_t3_items-01/per_problem.json"
RAW0 = Path("/Users/abaybektursun/projects/iterate-hack-ckpt/runs/abaybektursun-1115-064532-6a2f/answers.jsonl")
RAW123 = ROOT / "runs/abaybektursun-1115-102945-9b20/answers.jsonl"
OUT = ROOT / "studies/theory/results/direct/r16a3c1-01"
OPENER = re.compile(r"\b(Okay|Hmm|Let me|Let's|Wait|First|Alright)\b")
BOUNDARY = re.compile(EQUATION.pattern + r"|\bAnswer\b")
RANGES = {"round-16/account-3/c1": [0.1, 0.38], "null": [-0.08, 0.06]}


def deliberative(text):
    s = text[:240]
    m = OPENER.search(s)
    if m is None:
        return False
    b = BOUNDARY.search(s)
    return b is None or m.start() < b.start()


def load_step100():
    """{problem: [(sample, right, text) for samples 0-3]} from committed grades and raw texts."""
    raw = {}
    for line in open(RAW0):
        r = json.loads(line)
        raw[(int(r["problem_index"]), 0)] = r
    for line in open(RAW123):
        r = json.loads(line)
        i = int(r["problem_index"])
        s = (int(r["seed"]) - 45000000 - i) // 10000
        assert s in (1, 2, 3) and int(r["attempt"]) == 0
        raw[(i, s)] = r
    assert len(raw) == 2000
    graded = [(int(r["problem_index"]), 0, int(r["score_v3"]), r["opening"])
              for r in json.loads((CK / "s0100_plain-01/per_problem.json").read_text())]
    graded += [(int(r["problem_index"]), int(r["sample"]), int(r["score_v3"]), r["opening"])
               for r in map(json.loads, open(CK / "s0100_plain_s123-01/rows.jsonl")) if int(r["attempt"]) == 0]
    assert len(graded) == 2000
    out = {}
    for i, s, right, opening in graded:
        r = raw[(i, s)]
        assert r["text"][:30] == opening and int(r["score_v3"]) == right, (i, s)
        out.setdefault(i, []).append((s, right, r["text"], r))
    return out


def boot(d, seed=16, n_boot=10_000):
    rng = np.random.default_rng(seed)
    d = np.asarray(d, float)
    means = d[rng.integers(0, len(d), size=(n_boot, len(d)))].mean(axis=1)
    return [float(np.percentile(means, 5)), float(np.percentile(means, 95))]


def verdict16(ci, rng, adv, n):
    inside = rng[0] <= ci[0] and ci[1] <= rng[1]
    if inside and n >= 50 and not (ci[0] <= adv <= ci[1]):
        return "holds"
    if inside:
        return "not separated"
    if ci[1] < rng[0] or ci[0] > rng[1]:
        return "refuted"
    return "undecided"


def select(t3, s100, delib):
    rows = []
    for t in t3:
        i = int(t["problem_index"])
        if delib(t["t3_start"]):
            continue
        quick = [x for x in s100[i] if not delib(x[2])]
        if quick:
            rows.append((i, int(t["t3_right"]), s100[i], quick))
    return rows


def main():
    t3 = json.loads(T3_ROWS.read_text())
    assert len(t3) == 500
    s100 = load_step100()
    rows = select(t3, s100, deliberative)
    n = len(rows)

    # Adversary's value first: same rows, all 4 step-100 samples whatever their opening.
    adv_d = [sum(x[1] for x in samples) / 4 - t for _, t, samples, _ in rows]
    adversary = float(np.mean(adv_d))
    print("adversary D_alt", adversary, "n", n)

    d = [sum(x[1] for x in quick) / len(quick) - t for _, t, _, quick in rows]
    stat, ci = float(np.mean(d)), boot(d)
    print("D", stat, ci)

    # Sensitivity checks (not used for the verdict).
    rows_t3open = select(t3, s100, flagged_t3open)
    d_t3open = [sum(x[1] for x in q) / len(q) - t for _, t, _, q in rows_t3open]
    rows_strict = select(t3, s100, lambda s: OPENER.search(s[:240]) is not None)
    d_strict = [sum(x[1] for x in q) / len(q) - t for _, t, _, q in rows_strict]
    adv_strict = float(np.mean([sum(x[1] for x in s) / 4 - t for _, t, s, _ in rows_strict]))
    nonempty = []
    for i, t, _, quick in rows:
        q = [x for x in quick if x[2].strip()]
        if q:
            nonempty.append(sum(x[1] for x in q) / len(q) - t)
    quick_samples = [x for _, _, _, q in rows for x in q]
    slow_samples = [x for _, _, s, q in rows for x in s if x not in q]

    verdicts = {m: verdict16(ci, r, adversary, n) for m, r in RANGES.items()}
    metrics = {
        "test": "r16a3c1", "mechanism": "round-16/account-3/c1",
        "statistic": "D = mean over problems of (right rate of non-deliberative step-100 plain samples - T3 right), v3, fraction",
        "adversary": {"value": adversary,
                      "how": "same rows (chosen by the flags only); a_i = v3-right step-100 samples among all 4 / 4; D_alt = mean(a_i - t_i). Equals the plan's accuracy-only value."},
        "value": stat, "ci90": ci, "n": n, "n_planned": 60,
        "t3_right_on_rows": sum(t for _, t, _, _ in rows),
        "step100_right_rate_all4_on_rows": float(np.mean([sum(x[1] for x in s) / 4 for _, _, s, _ in rows])),
        "step100_right_rate_quick_on_rows": float(np.mean([sum(x[1] for x in q) / len(q) for _, _, _, q in rows])),
        "quick_samples_on_rows": len(quick_samples), "quick_right": sum(x[1] for x in quick_samples),
        "quick_empty": sum(1 for x in quick_samples if not x[2].strip()),
        "quick_cap_hit": sum(1 for x in quick_samples if x[3]["cap_hit"] is True),
        "quick_with_opener_after_boundary_in_240": sum(1 for x in quick_samples if OPENER.search(x[2][:240])),
        "quick_with_opener_anywhere": sum(1 for x in quick_samples if OPENER.search(x[2])),
        "deliberative_samples_on_rows": len(slow_samples), "deliberative_right": sum(x[1] for x in slow_samples),
        "t3_nondeliberative_problems": sum(1 for t in t3 if not deliberative(t["t3_start"])),
        "step100_nondeliberative_samples_all500": sum(1 for v in s100.values() for x in v if not deliberative(x[2])),
        "sensitivity_t3open_rule": {"rule": "direct_t3open.flagged (Okay|Alright|Hmm|Let me|Let's|I need to, no Answer boundary)",
                                    "n": len(rows_t3open), "value": float(np.mean(d_t3open)), "ci90": boot(d_t3open)},
        "sensitivity_no_opener_in_240": {"rule": "non-deliberative only if no opener word anywhere in text[:240] (no boundary)",
                                         "n": len(rows_strict), "value": float(np.mean(d_strict)), "ci90": boot(d_strict),
                                         "adversary_same_rows": adv_strict},
        "sensitivity_drop_empty_quick": {"n": len(nonempty), "value": float(np.mean(nonempty)), "ci90": boot(nonempty)},
        "raw_rows_read": (
            "10 rows that enter the statistic (problems 5, 12, 15, 16, 17, 19, 21, 23, 34, 36; first non-deliberative "
            "sample each) read in full at the start and end. Every plain answer opens by continuing the prompt's "
            "instruction text (' (do not write \"$Answer: 122$\"...', ' line, the answer is valid for $365$ days'). In 7 "
            "of the 10 the model then writes 'Okay, let's see...' and deliberates; it counts as non-deliberative only "
            "because that echoed instruction holds a $, = or the word Answer before 'Okay'. Over all rows, 86 of the 151 "
            "non-deliberative samples have an opener word within their first 240 characters (after the boundary), 121 "
            "anywhere. Problem 5 sample 0 is an empty answer (n_new 0, scored wrong; 6 empty among the 151). 4 of 151 "
            "hit the 16,384-token cap (problem 21 among them, wrong). No duplicated seeds (2,000 distinct problem-sample "
            "keys). So D mostly measures samples whose echoed instruction holds an equation sign, not samples that skip "
            "deliberation; the stricter rule (no opener word in 240 characters) gives 0.167 [0.020, 0.314], n 51."),
        "ranges": RANGES, "verdicts": verdicts,
        "flag_rule": "deliberative if case-sensitive \\b(Okay|Hmm|Let me|Let's|Wait|First|Alright)\\b in text[:240] before the first $, =, \\(, \\[ or \\bAnswer\\b",
        "bootstrap": "10,000 resamples of problems, numpy default_rng(16), 5th-95th percentile",
        "departures": [
            "Committed step-100 rows store only 30 characters; the first 240 characters were read from the raw answers (sample 0: iterate-hack-ckpt/runs/abaybektursun-1115-064532-6a2f, samples 1-3: Modal Volume via gpu.py get abaybektursun-1115-102945-9b20). First 30 characters and v3 grades checked equal to the committed rows on all 2,000 samples.",
            "The flag uses the plan's word list (Okay/Hmm/Let me/Let's/Wait/First/Alright) with an 'Answer' boundary; result-1f98b0's code used Okay|Alright|Hmm|Let me|Let's|I need to. That rule is reported as a sensitivity check.",
        ],
    }
    OUT.mkdir(parents=True, exist_ok=True)

    def ex(i, t, sample):
        tr = next(x for x in t3 if int(x["problem_index"]) == i)
        return {"problem_index": i, "gold": sample[3]["gold"],
                "t3": {"right": t, "extracted_v3": tr["t3_extracted_v3"], "start": tr["t3_start"]},
                "step100_quick_sample": {"sample": sample[0], "right": sample[1], "extracted_v3": sample[3]["extracted_v3"],
                                         "first_240": sample[2][:240], "last_300": sample[2][-300:], "n_new": sample[3]["n_new"]}}
    right = next((i, t, x) for i, t, _, q in rows for x in q if x[1] == 1 and t == 0)
    wrong = next((i, t, x) for i, t, _, q in rows for x in q if x[1] == 0)
    examples = {"note": "Rows of the statistic. 'right': a non-deliberative step-100 sample scored right (T3 wrong, u-t > 0); 'wrong': one scored wrong.",
                "right": ex(*right), "wrong": ex(*wrong)}
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=1) + "\n")
    (OUT / "examples.json").write_text(json.dumps(examples, indent=1, ensure_ascii=False) + "\n")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    (OUT / "run.json").write_text(json.dumps({
        "commit": commit, "where": "laptop, stored rows only, no model forward pass",
        "command": "PYTHONPATH=. uv run --no-project --with numpy --with math-verify==0.9.0 --with antlr4-python3-runtime==4.11 python studies/theory/analysis/direct_r16a3c1.py",
        "inputs": [str(T3_ROWS.relative_to(ROOT)), "studies/rlneurons/results/ckptcue/s0100_plain-01/per_problem.json",
                   "studies/rlneurons/results/ckptcue/s0100_plain_s123-01/rows.jsonl", str(RAW0),
                   "runs/abaybektursun-1115-102945-9b20/answers.jsonl (Modal Volume, gpu.py get)"]}, indent=1) + "\n")
    # Dump 10 raw rows that enter the statistic for reading.
    for i, t, _, q in rows[:10]:
        for x in q[:1]:
            print("----", i, "t3", t, "s", x[0], "right", x[1], "cap", x[3]["cap_hit"], "n_new", x[3]["n_new"])
            print(repr(x[2][:240]))
            print("... END:", repr(x[2][-150:]))
    print(json.dumps({k: metrics[k] for k in ["value", "ci90", "n", "verdicts"]}, indent=1))


if __name__ == "__main__":
    main()
