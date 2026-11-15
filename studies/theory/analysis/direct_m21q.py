"""Direct tests m21open-01 (round-13/s2-a) and m21hard-01 (round-13/s2-b). Spec: studies/theory/specs/SPEC_direct_m21q.md.

Usage: python3 studies/theory/analysis/direct_m21q.py runs/abaybektursun-1115-103050-eae1/answers.jsonl
Writes readout.json in studies/theory/results/direct/m21open-01/ and m21hard-01/; examples.json, reading.md and
run.json there are written by hand from the rows this script prints.
"""
import json
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

M21 = Path(sys.argv[1])
T13 = Path("studies/rlneurons/results/rln4/t1_t3_items-01/per_problem.json")
CUE = Path("studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl")
CELL = Path("studies/theory/results/experiments/cell-r9-m21-01/per_problem.json")
OUT_A = Path("studies/theory/results/direct/m21open-01")
OUT_B = Path("studies/theory/results/direct/m21hard-01")
B = 10000

DELIB = ["Okay", "Let me", "Let's", "I need", "First", "Step"]


def af_pos(s):
    """Position of the first answer-first marker in s (plan's rule), or None."""
    pos = [s.find(m) for m in ("Answer:", "\\boxed") if m in s]
    t = s.strip().strip("$").strip()
    if t[:1].isdigit() or t.startswith(("-", "\\frac", "(")):
        pos.append(s.find(t[:1]) if t else 0)
    return min(pos) if pos else None


def af(s):
    return af_pos(s) is not None


def af_strict(s):
    p = af_pos(s)
    return p is not None and not any(w in s[:p] for w in DELIB)


def share(rows, f):
    return sum(f(s) for s in rows) / len(rows)


def boot(xs, ys, stat):
    rng = random.Random(0)
    vals = sorted(stat([rng.choice(xs) for _ in xs], [rng.choice(ys) for _ in ys]) for _ in range(B))
    return [round(vals[int(0.05 * B)], 4), round(vals[int(0.95 * B) - 1], 4)]


def boot1(xs, stat):
    rng = random.Random(0)
    vals = sorted(stat([rng.choice(xs) for _ in xs]) for _ in range(B))
    return [round(vals[int(0.05 * B)], 4), round(vals[int(0.95 * B) - 1], 4)]


rows = [json.loads(l) for l in open(M21)]
assert len(rows) == 250 and all(r["attempt"] == 0 for r in rows)
Q = sorted((r for r in rows if r["n_generated"] <= 1000 and not r["cap_hit"] and r["score_v3"] != 1),
           key=lambda r: r["problem_index"])
assert len(Q) == 60
cell = {p["problem_index"]: p["quick_wrong"] for p in json.load(open(CELL))}
assert {r["problem_index"] for r in Q} == {i for i, v in cell.items() if v == 1}

T = [p for p in json.load(open(T13)) if p["problem_index"] < 250]
N = [p for p in T if p["t3_generated_tokens"] <= 1000 and not p["t3_cap_hit"] and not p["t3_right"]]
assert len(N) == 105
CTRL = [p for p in T if p["t3_right"] and p["t3_generated_tokens"] > 1000]

q_txt = [r["text"][:240] for r in Q]
n_txt = [p["t3_start"][:240] for p in N]
c_txt = [p["t3_start"][:240] for p in CTRL]

diff = lambda a, b, f: share(a, f) - share(b, f)
a_out = {"n_Q": len(Q), "n_N": len(N), "Q_empty": sum(not s.strip() for s in q_txt),
         "N_empty": sum(not s.strip() for s in n_txt)}
for name, f in (("plan_rule", af), ("strict_rule", af_strict)):
    a_out[name] = {
        "s_Q": round(share(q_txt, f), 4), "s_Q_ci90": boot1(q_txt, lambda x: share(x, f)),
        "s_N": round(share(n_txt, f), 4),
        "s_Q_minus_s_N": round(diff(q_txt, n_txt, f), 4),
        "ci90": boot(q_txt, n_txt, lambda x, y: diff(x, y, f)),
        "s_Q_nonempty": round(share([s for s in q_txt if s.strip()], f), 4),
        "control_long_right_T3_af_share": round(share(c_txt, f), 4), "n_control": len(c_txt),
    }

# Plan b: cued-base solve rate per problem over samples 0-3.
first = {}
for l in open(CUE):
    r = json.loads(l)
    if r["attempt"] == 0 and r["sample"] < 4 and (r["problem_index"], r["sample"]) not in first:
        first[(r["problem_index"], r["sample"])] = r
k = defaultdict(int)
for (i, s), r in first.items():
    k[i] += int(r["score_v3"] == 1 and not r["cap_hit"])
assert all((i, s) in first for i in range(250) for s in range(4))
rate = {i: k[i] / 4 for i in range(250)}
rq = [rate[r["problem_index"]] for r in Q]
rn = [rate[p["problem_index"]] for p in N]
mean = lambda x: sum(x) / len(x)
allr = [rate[i] for i in range(250)]
solved_all = [x for x in allr if x == 1.0]
rng = random.Random(1)
rand60 = [rate[i] for i in rng.sample(range(250), 60)]
b_out = {"n_Q": len(rq), "n_N": len(rn), "r_Q": round(mean(rq), 4), "r_N": round(mean(rn), 4),
         "r_N_minus_r_Q": round(mean(rn) - mean(rq), 4), "ci90": boot(rq, rn, lambda x, y: mean(y) - mean(x)),
         "r_all_250": round(mean(allr), 4), "check_solved_by_all_mean": mean(solved_all),
         "check_random60_mean": round(mean(rand60), 4),
         "overlap_Q_N_problems": len({r["problem_index"] for r in Q} & {p["problem_index"] for p in N})}

okay = lambda x: "Okay" in x
a_out["side_okay_share"] = {"Q": round(share(q_txt, okay), 4), "N": round(share(n_txt, okay), 4),
                            "control_long_right_T3": round(share(c_txt, okay), 4)}
LW = [rate[r["problem_index"]] for r in rows if r["n_generated"] > 1000 and r["score_v3"] != 1]
b_out["check_m21_long_wrong_mean"] = round(mean(LW), 4)
b_out["check_m21_long_wrong_n"] = len(LW)
print(json.dumps({"a": a_out, "b": b_out}, indent=1))
print("\n=== 10 Q rows (every 6th) ===")
for r in Q[::6]:
    print(r["problem_index"], "AF" if af(r["text"][:240]) else "--", "S" if af_strict(r["text"][:240]) else "-",
          r["n_generated"], repr(r["extracted_v3"])[:30], "gold", r["gold"][:20], "|", repr(r["text"][:200]))
print("\n=== 10 N rows (every 10th) ===")
for p in N[::10][:10]:
    s = p["t3_start"][:240]
    print(p["problem_index"], "AF" if af(s) else "--", "S" if af_strict(s) else "-", p["t3_generated_tokens"],
          repr(p["t3_extracted_v3"])[:30], "|", repr(s[:200]))

OUT_A.mkdir(parents=True, exist_ok=True)
OUT_B.mkdir(parents=True, exist_ok=True)
pr = a_out["plan_rule"]
a_out["verdict"] = "refuted" if (pr["s_Q"] < 0.40 or pr["s_Q"] < pr["s_N"] - 0.15) else "holds"
a_out["rule"] = "refuted if s_Q < s_N - 0.15 or s_Q < 0.40 (plan rule; strict rule gives the same shares)"
b_out["verdict"] = "refuted" if b_out["r_N_minus_r_Q"] < 0.10 else "holds"
b_out["rule"] = "refuted if r_N - r_Q < 0.10"
json.dump({"a": a_out, "q_rows": [{"problem_index": r["problem_index"], "n_generated": r["n_generated"],
                                   "af": af(t), "af_strict": af_strict(t), "start": t} for r, t in zip(Q, q_txt)]},
          open(OUT_A / "readout.json", "w"), indent=1)
json.dump({"b": b_out, "q": {r["problem_index"]: rate[r["problem_index"]] for r in Q},
           "n": {p["problem_index"]: rate[p["problem_index"]] for p in N}}, open(OUT_B / "readout.json", "w"), indent=1)
