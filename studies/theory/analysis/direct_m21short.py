"""Direct test m21short-01: shared test of rival pair round-14/s4. Spec: studies/theory/specs/SPEC_direct_m21short.md.

S = share of m21's right answers (base + 1.0 x Code-RL top-8, plain, MATH-500 first 250) with n_generated <= L, where
L is the median generated tokens of the plain base's (T3) right, not cut off answers on the same problems.

Usage: uv run python studies/theory/analysis/direct_m21short.py <m21 answers.jsonl>
(the raw file of job abaybektursun-1115-103050-eae1; a copy is in ../iterate-hack-cells-r9b/runs/).
Writes studies/theory/results/direct/m21short-01/metrics.json and examples.json.
"""
import json
import sys
from pathlib import Path

import numpy as np

M21 = Path(sys.argv[1])
T13 = Path("studies/rlneurons/results/rln4/t1_t3_items-01/per_problem.json")
CELL = Path("studies/theory/results/experiments/cell-r9-m21-01/per_problem.json")
OUT = Path("studies/theory/results/direct/m21short-01")
B = 10000
RANGES = {"a": [0.0, 0.12], "b": [0.15, 0.36], "null": [0.41, 0.60]}

# m21: first row per problem 0-249
first = {}
for line in open(M21):
    r = json.loads(line)
    if r["problem_index"] < 250 and r["problem_index"] not in first:
        first[r["problem_index"]] = r
assert sorted(first) == list(range(250))
m_right = np.array([first[i]["score_v3"] == 1 and first[i]["cap_hit"] is not True for i in range(250)])
m_len = np.array([first[i]["n_generated"] for i in range(250)])

# plain base T3
t3 = {p["problem_index"]: p for p in json.load(open(T13)) if p["problem_index"] < 250}
assert sorted(t3) == list(range(250))
t_right = np.array([t3[i]["t3_right"] == 1 and not t3[i]["t3_cap_hit"] for i in range(250)])
t_len = np.array([t3[i]["t3_generated_tokens"] for i in range(250)])

# instrument checks: posted counts (result-ac7104) and the committed per-problem file
assert sum(first[i]["score_v3"] == 1 for i in range(250)) == 157
assert sum(first[i]["n_generated"] <= 1000 and not first[i]["cap_hit"] and first[i]["score_v3"] != 1
           for i in range(250)) == 60
assert sum(t3[i]["t3_right"] == 1 for i in range(250)) == 107
cell = {p["problem_index"]: p for p in json.load(open(CELL))}
for i in range(250):  # n_generated counts the stop token; n_new does not, and a cap hit has no stop token
    r = first[i]
    assert cell[i]["n_new"] == r["n_new"] and cell[i]["score_v3"] == r["score_v3"]
    assert r["n_generated"] - r["n_new"] == (0 if r["cap_hit"] else 1)


def stat(idx, right, lens):
    """L from the T3 right rows in idx; S over the rows of (right, lens) in idx."""
    L = np.median(t_len[idx][t_right[idx]])
    keep = right[idx]
    return float(np.mean(lens[idx][keep] <= L)), float(L)


ALL = np.arange(250)
S, L = stat(ALL, m_right, m_len)
S_self, _ = stat(ALL, t_right, t_len)  # failing input: the plain base against its own median must give about 0.5
assert RANGES["null"][0] <= S_self <= RANGES["null"][1], S_self

rng = np.random.default_rng(0)
draws = np.array([stat(rng.integers(0, 250, 250), m_right, m_len)[0] for _ in range(B)])
lo, hi = (float(x) for x in np.percentile(draws, [5, 95]))
rng = np.random.default_rng(0)
draws_self = np.array([stat(rng.integers(0, 250, 250), t_right, t_len)[0] for _ in range(B)])
lo_s, hi_s = (float(x) for x in np.percentile(draws_self, [5, 95]))


def place(lo, hi, r):
    if r[0] <= lo and hi <= r[1]:
        return "inside"
    if hi < r[0] or lo > r[1]:
        return "outside"
    return "straddles"


pa, pb = place(lo, hi, RANGES["a"]), place(lo, hi, RANGES["b"])
n = int(m_right.sum())
if pa == "inside" and n >= 50:
    verdict = {"round-14/s4-a": "holds", "round-14/s4-b": "refuted"}
elif pb == "inside" and n >= 50:
    verdict = {"round-14/s4-a": "refuted", "round-14/s4-b": "holds"}
else:
    verdict = {"round-14/s4-a": "refuted" if pa == "outside" else "undecided",
               "round-14/s4-b": "refuted" if pb == "outside" else "undecided"}

short = [i for i in range(250) if m_right[i] and m_len[i] <= L]
long_ = [i for i in range(250) if m_right[i] and m_len[i] > L]
OUT.mkdir(parents=True, exist_ok=True)
metrics = {
    "statistic": "S = share of m21 right rows (first row per problem 0-249, score_v3 1, not cap hit) with n_generated <= L",
    "S": round(S, 4), "ci90": [round(lo, 4), round(hi, 4)], "n": n, "n_counted": len(short),
    "L_tokens": L, "n_t3_right_not_capped": int(t_right.sum()),
    "m21_right_median_tokens": float(np.median(m_len[m_right])),
    "null": 0.5, "null_check_plain_base_self": {"S": round(S_self, 4), "ci90": [round(lo_s, 4), round(hi_s, 4)]},
    "ranges": RANGES, "placement": {"a": pa, "b": pb}, "verdict": verdict,
    "bootstrap": "10,000 resamples of problems 0-249 with replacement, numpy default_rng(0), L and S recomputed per draw",
    "inputs": {"m21": "runs/abaybektursun-1115-103050-eae1/answers.jsonl (job abaybektursun-1115-103050-eae1)",
               "t3": str(T13)},
    "checks": "m21 right 157 and quick wrong 60 (result-ac7104), T3 right 107; n_new and score_v3 equal the committed "
              "cell-r9-m21-01/per_problem.json on all 250 rows, n_generated = n_new + 1 (stop token; 0 for cap hits); "
              "plain base against its own median inside the null range",
    "raw_rows_read": "Read 10 short right m21 rows (problems 3, 13, 29, 54, 90, 117, 162, 199, 229, 243): 5 are short "
                     "'Okay, let's see' deliberations, 4 are direct worked solutions in the plain base's style, 1 echoes "
                     "the prompt then deliberates. Over all 65 short right rows 39 open with 'Okay' in the first 240 "
                     "characters, against 14 of the plain base's 53 right rows at or below L.",
}
keys = ["problem_index", "unique_id", "n_generated", "cap_hit", "score_v3", "extracted_v3", "gold"]
ex = {"counts": {**{k: first[short[0]][k] for k in keys}, "text_start": first[short[0]]["text"][:600],
                 "t3_generated_tokens": int(t_len[short[0]])},
      "does_not_count": {**{k: first[long_[0]][k] for k in keys}, "text_start": first[long_[0]]["text"][:600],
                         "t3_generated_tokens": int(t_len[long_[0]])},
      "L_tokens": L}
json.dump(metrics, open(OUT / "metrics.json", "w"), indent=1)
json.dump(ex, open(OUT / "examples.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(metrics, indent=1))
print("short right rows:", short)
