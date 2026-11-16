"""Direct test r16a1c2 (theory round 16, round-16/account-1/c2). Spec: studies/theory/specs/SPEC_direct_r16a1c2.md.

G = right rate (v3) of deliberative-opening m21 answers minus that of non-deliberative ones, on MATH-500 problems
0-249 whose cued-base T1 answer is right. The adversary's value (same contrast on the plain base's T3 answers) first.

Run from the worktree root:
PYTHONPATH=. uv run --no-project --with numpy --with math-verify==0.9.0 --with antlr4-python3-runtime==4.11 \
  python studies/theory/analysis/direct_r16a1c2.py ../iterate-hack-cells-r9b/runs/abaybektursun-1115-103050-eae1/answers.jsonl
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

from studies.theory.analysis.direct_t3open import OPENER, flagged

M21 = Path(sys.argv[1])
T13 = Path("studies/rlneurons/results/rln4/t1_t3_items-01/per_problem.json")
CUE = Path("studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl")
CELL = Path("studies/theory/results/experiments/cell-r9-m21-01/per_problem.json")
OUT = Path("studies/theory/results/direct/r16a1c2-01")
B = 10_000
RANGES = {"round-16/account-1/c2": [0.2, 0.65], "round-16/account-2/deny-account-1-c2": [-0.1, 0.17]}
NULL_RANGE = [-0.06, 0.12]


def gap(right, flag):
    return right[flag].mean() - right[~flag].mean()


def boot(right, flag, rng):
    n = len(right)
    gs = np.empty(B)
    for b in range(B):
        i = rng.integers(0, n, n)
        gs[b] = gap(right[i], flag[i])
    return [float(np.percentile(gs, 5)), float(np.percentile(gs, 95))]


def verdict16(lo, hi, rng_, n, adv):
    """Same rule as forecast.verdict16."""
    if hi < rng_[0] or rng_[1] < lo:
        return "refuted"
    if n < 50 or not (rng_[0] <= lo and hi <= rng_[1]):
        return "undecided"
    return "not separated" if lo <= adv <= hi else "holds"


t13 = {r["problem_index"]: r for r in json.load(open(T13)) if r["problem_index"] < 250}
assert sorted(t13) == list(range(250))
keep = [i for i in range(250) if t13[i]["t1_right"] == 1]
n = len(keep)

# 1) adversary's value: the flag rule on the plain base's T3 answers, m21 not read
t3_right = np.array([t13[i]["t3_right"] for i in keep], dtype=float)
t3_flag = np.array([flagged(t13[i]["t3_start"]) for i in keep])
adv = float(gap(t3_right, t3_flag))
print(f"adversary G_alt = {adv:.4f}  (n {n}, T3 flagged {t3_flag.sum()}: {t3_right[t3_flag].mean():.3f}, "
      f"unflagged {(~t3_flag).sum()}: {t3_right[~t3_flag].mean():.3f})")

# 2) m21 rows, checked against the committed per-problem file
m21 = {}
for line in open(M21):
    r = json.loads(line)
    assert r["attempt"] == 0 and r["problem_index"] not in m21
    m21[r["problem_index"]] = r
assert sorted(m21) == list(range(250))
cell = {r["problem_index"]: r for r in json.load(open(CELL))}
assert all(cell[i]["score_v3"] == m21[i]["score_v3"] and cell[i]["n_new"] == m21[i]["n_new"] for i in range(250))
seeds = [m21[i]["seed"] for i in range(250)]
assert len(set(seeds)) == 250

m_right = np.array([m21[i]["score_v3"] for i in keep], dtype=float)
m_flag = np.array([flagged(m21[i]["text"]) for i in keep])
G = float(gap(m_right, m_flag))
rng = np.random.default_rng(16)
ci = boot(m_right, m_flag, rng)

# 3) null G0: cued base's 4-sample right rate per problem in place of m21 right, same flags
cue = defaultdict(list)
for line in open(CUE):
    r = json.loads(line)
    if r["attempt"] == 0 and r["sample"] < 4 and r["problem_index"] < 250:
        cue[r["problem_index"]].append(r["score_v3"])
assert all(len(cue[i]) == 4 for i in keep)
c_rate = np.array([np.mean(cue[i]) for i in keep])
G0 = float(gap(c_rate, m_flag))
ci0 = boot(c_rate, m_flag, np.random.default_rng(16))

verdicts = {m: verdict16(ci[0], ci[1], r, n, adv) for m, r in RANGES.items()}
print(f"G = {G:.4f} [{ci[0]:.4f}, {ci[1]:.4f}] n {n}; flagged {m_flag.sum()} right {m_right[m_flag].mean():.3f}, "
      f"unflagged {(~m_flag).sum()} right {m_right[~m_flag].mean():.3f}")
print(f"G0 = {G0:.4f} [{ci0[0]:.4f}, {ci0[1]:.4f}]")
print(verdicts)

empty = [i for i in keep if m21[i]["text"].strip() == ""]
caps = [i for i in keep if m21[i]["cap_hit"]]
no_ext = [i for i in keep if m21[i]["extracted_v3"] is None]
late = [i for i in keep if not flagged(m21[i]["text"]) and OPENER.search(m21[i]["text"][:240])]
ne = np.array([i not in empty for i in keep])
G_ne = float(gap(m_right[ne], m_flag[ne]))
ci_ne = boot(m_right[ne], m_flag[ne], np.random.default_rng(16))
print(f"without empty texts: G = {G_ne:.4f} [{ci_ne[0]:.4f}, {ci_ne[1]:.4f}] n {int(ne.sum())}; "
      f"unflagged with an opener after an equation marker: {len(late)}, right {sum(m21[i]['score_v3'] for i in late)}")
metrics = {
    "test": "r16a1c2", "mechanism": "round-16/account-1/c2",
    "statistic": "G = mean(m21 right v3 | m21 opens deliberatively) - mean(m21 right v3 | not), MATH-500 problems "
                 "0-249 with cued-base T1 right, fraction",
    "adversary": {
        "value": adv,
        "how": "same rows; result-1f98b0 flag (direct_t3open.flagged) on t3_start (first 240 chars of the plain base "
               "T3 answer); mean(t3_right | flagged) - mean(t3_right | unflagged); m21 not read",
        "t3_flagged": int(t3_flag.sum()), "t3_flagged_right": float(t3_right[t3_flag].mean()),
        "t3_unflagged": int((~t3_flag).sum()), "t3_unflagged_right": float(t3_right[~t3_flag].mean()),
        "expected_by_adversary": 0.48,
    },
    "value": G, "ci90": ci, "n": n,
    "m21_flagged": int(m_flag.sum()), "m21_flagged_right": float(m_right[m_flag].mean()),
    "m21_unflagged": int((~m_flag).sum()), "m21_unflagged_right": float(m_right[~m_flag].mean()),
    "null_G0": G0, "null_G0_ci90": ci0, "null_range": NULL_RANGE,
    "ranges": RANGES, "verdicts": verdicts,
    "bootstrap": "10,000 resamples of the kept problems, numpy default_rng(16), 5th-95th percentile; G0 same seed",
    "flag_rule": "direct_t3open.flagged: case-sensitive \\b(Okay|Alright|Hmm|Let me|Let's|I need to)\\b in the first "
                 "240 chars, before the first $, =, \\( or \\[",
    "right": "stored score_v3 == 1 (cap-hit answers counted as stored)",
    "checks": {"m21_empty_text_in_rows": empty, "m21_cap_hit_in_rows": caps,
               "m21_no_extraction_in_rows": len(no_ext), "m21_unique_seeds": True,
               "m21_matches_cell_per_problem": True,
               "unflagged_with_opener_after_equation_marker": late},
    "sensitivity_without_empty_texts": {"value": G_ne, "ci90": ci_ne, "n": int(ne.sum())},
    "raw_rows_read": "First 10 kept rows (problems 0,1,2,3,5,6,7,8,10,12) read. No cap hits, unique seeds. m21 text "
                     "usually continues the prompt line first ('.', ' (Answer: X).', ' in the form $Answer$.') and "
                     "then opens 'Okay, so I need to...' or 'Let's solve...'; flagged ones are long reasoning "
                     "(600-4600 tokens). Unflagged: 0 = direct worked solution ('To convert...'), wrong; 2 = garbled "
                     "text, wrong; 12 = 'Okay' after an echoed '$Answer$', so unflagged by the marker rule though "
                     "deliberative, right. Over all kept rows: 10 unflagged answers are empty (1 token, all wrong) and "
                     "11 unflagged answers have an opener after an echoed '$' (8 right), so the unflagged group mixes "
                     "empty, garbled, direct and a few deliberative answers.",
    "departures": [] if n == 205 else [f"n is {n}, plan said about 205 (all T1-right problems 0-249 used)"],
    "inputs": {"m21_raw": "runs/abaybektursun-1115-103050-eae1/answers.jsonl (not committed)", "t1_t3": str(T13),
               "cue": str(CUE), "cell": str(CELL)},
}
keys = ["problem_index", "unique_id", "seed", "score_v3", "extracted_v3", "gold", "n_new", "cap_hit"]
ex_f = next(i for i in keep if flagged(m21[i]["text"]) and m21[i]["score_v3"] == 1)
ex_u = next(i for i in keep if not flagged(m21[i]["text"]) and m21[i]["score_v3"] == 0)
examples = {
    "note": "m21 rows on T1-right problems: one counted as flagged (deliberative opening) and right, one counted as "
            "unflagged and wrong; input = prompt, output = text",
    "flagged_right": {**{k: m21[ex_f][k] for k in keys}, "prompt": m21[ex_f]["prompt"], "text": m21[ex_f]["text"]},
    "unflagged_wrong": {**{k: m21[ex_u][k] for k in keys}, "prompt": m21[ex_u]["prompt"], "text": m21[ex_u]["text"]},
}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "metrics.json").write_text(json.dumps(metrics, indent=1) + "\n")
(OUT / "examples.json").write_text(json.dumps(examples, indent=1, ensure_ascii=False) + "\n")
for i in keep[:10]:
    print(i, m21[i]["score_v3"], flagged(m21[i]["text"]), m21[i]["n_new"], m21[i]["cap_hit"], repr(m21[i]["text"][:160]))
