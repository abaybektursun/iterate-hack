"""Independent recomputation of the r6-account budgets, written from the rules in theories/r6-account.json only.

Run from the repository root: python3 studies/theory/results/account/run-02/check/budget.py
Inputs: committed rows in studies/rlneurons/results/ and row files fetched to runs/account-check/ (S3 and Modal
commands in run-02/run.json). Writes check/budget.out.txt (this printout) and check/assign.json (part per gap problem).
"""
import json
import random
import zlib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
RUNS = ROOT / "runs/account-check"
OUT = Path(__file__).resolve().parent
PARTS = ["loop", "budget", "answer-statement", "reliability", "capability", "unassigned"]


def jl(path):
    return [json.loads(line) for line in open(path)]


def first_by(rows, key, keep=lambda r: True):
    d = {}
    for r in rows:
        if keep(r) and r.get(key) is not None and r[key] not in d:
            d[r[key]] = r
    return d


def is_cap(r):
    return r["cap_hit"] is True or (r.get("cap_hit") is None and r.get("finish_reason") == "length")


def rule_a(text):
    if not text:
        return False
    starts = [0] + [i + 1 for i, c in enumerate(text) if c == "\n"]
    for p in starts:
        if len(text) - p < 8000:
            continue
        w = text[p:p + 8000].encode("utf-8")
        if len(zlib.compress(w)) / len(w) < 0.10:
            return True
    return False


def norm(s):
    for t in ["$", "*", "#", "\\left", "\\right"]:
        s = s.replace(t, "")
    s = "".join(s.split())
    return s.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")


def answer_statement(text, gold):
    if text is None:
        return True
    g = norm(gold)
    lines = [norm(x) for x in text.split("\n")]
    no_marker = not any("\\boxed{" in x for x in lines) and not any(x.startswith("Answer:") for x in lines)
    gold_boxed = any("\\boxed{" + g + "}" in x for x in lines)
    gold_line = any(x in ("Answer:" + g, "Answer:" + g + ".") for x in lines)
    return no_marker or gold_boxed or gold_line


def assign(cap, text, gold, ev):
    """cap: base row is a cap hit; ev: list of 0/1 evidence grades (E). Returns the first part that takes it."""
    if cap and rule_a(text):
        return "loop"
    if cap:
        return "budget"
    if answer_statement(text, gold):
        return "answer-statement"
    if sum(ev) >= 1:
        return "reliability"
    if len(ev) >= 1:
        return "capability"
    return "unassigned"


def right(r, field):
    return 1 if r is not None and r.get(field) == 1 else 0


# ---- evidence sources
day13 = jl(ROOT / "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl")
E_math = {}  # problem_index -> list of grades in file order (attempt 0, samples 0-3, first row per sample)
seen = set()
for r in day13:
    if r["attempt"] == 0 and r["sample"] in (0, 1, 2, 3) and (r["problem_index"], r["sample"]) not in seen:
        seen.add((r["problem_index"], r["sample"]))
        E_math.setdefault(r["problem_index"], []).append(right(r, "score_v3"))

F_hard = first_by(jl(RUNS / "base_F_hard.jsonl"), "unique_id")
P_hard = first_by(jl(RUNS / "base_P_hard.jsonl"), "unique_id")
b7ba0 = first_by(jl(RUNS / "7ba0.jsonl"), "problem_index")


def E_hard(B):
    ev = []
    if B["unique_id"] in F_hard:
        ev.append(right(F_hard[B["unique_id"]], "score"))
    if B["unique_id"] in P_hard:
        ev.append(right(P_hard[B["unique_id"]], "score"))
    if B["problem_index"] in b7ba0:
        ev.append(right(b7ba0[B["problem_index"]], "score_v3"))
    return ev


# ---- cells: list of (problem_index, cap, text, gold, E) for gap problems, plus base-only count
pp = {r["problem_index"]: r for r in json.load(open(ROOT / "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"))}
T1 = first_by(jl(RUNS / "T1.jsonl"), "problem_index")
th = first_by(jl(RUNS / "683b.jsonl"), "problem_index")
cells = {}

g, bo = [], 0
for i, r in pp.items():
    if r["t1_right"] is None or r["t2_right"] is None:
        continue
    B = T1.get(i)
    if r["t2_right"] == 1 and r["t1_right"] == 0:
        g.append((i, r["t1_cap_hit"] is True, B and B["text"], B and B["gold"], E_math.get(i, [])))
    bo += r["t2_right"] == 0 and r["t1_right"] == 1
cells["math500-rl-T1"] = (g, bo)

g, bo = [], 0
for i, r in pp.items():
    if r["t1_right"] is None or i not in th or th[i].get("score_v3") is None:
        continue
    B = T1.get(i)
    if th[i]["score_v3"] == 1 and r["t1_right"] == 0:
        g.append((i, r["t1_cap_hit"] is True, B and B["text"], B and B["gold"], E_math.get(i, [])))
    bo += th[i]["score_v3"] != 1 and r["t1_right"] == 1
cells["math500-theta05-T1"] = (g, bo)

# Null cell, not in the account: the RL side is base + a random matched-norm difference with the cue (job 6429,
# result-9b6af3: in effect a fresh base sample). Same rules as math500-theta05-T1.
rnd = first_by(jl(RUNS / "6429.jsonl"), "problem_index")
g, bo = [], 0
for i, r in pp.items():
    if r["t1_right"] is None or i not in rnd or rnd[i].get("score_v3") is None:
        continue
    B = T1.get(i)
    if rnd[i]["score_v3"] == 1 and r["t1_right"] == 0:
        g.append((i, r["t1_cap_hit"] is True, B and B["text"], B and B["gold"], E_math.get(i, [])))
    bo += rnd[i]["score_v3"] != 1 and r["t1_right"] == 1
cells["null: math500-random-T1"] = (g, bo)

e72c = first_by(jl(RUNS / "e72c.jsonl"), "problem_index")
a619 = first_by(jl(RUNS / "a619.jsonl"), "problem_index")
g, bo = [], 0
for i in sorted(set(e72c) & set(a619)):
    B = e72c[i]
    if a619[i].get("score_v3") == 1 and B.get("score_v3") != 1:
        g.append((i, is_cap(B), B["text"], B["gold"], E_hard(B)))
    bo += a619[i].get("score_v3") != 1 and B.get("score_v3") == 1
cells["hard328-code-T1"] = (g, bo)

s0 = lambda r: r["sample"] == 0
bF = first_by(jl(RUNS / "base_F_math500.jsonl"), "problem_index", s0)
s4 = first_by(jl(RUNS / "s0400_P_math500.jsonl"), "problem_index", s0)
g, bo = [], 0
for i in sorted(set(bF) & set(s4)):
    B = bF[i]
    if s4[i].get("score") == 1 and B.get("score") != 1:
        g.append((i, is_cap(B), B["text"], B["gold"], E_math.get(i, [])))
    bo += s4[i].get("score") != 1 and B.get("score") == 1
cells["math500-s0400-T06"] = (g, bo)


# ---- shares with bootstrap
def boot(labels, part, n_boot=2000, seed=0):
    rng = random.Random(seed)
    n = len(labels)
    xs = sorted(sum(labels[rng.randrange(n)] == part for _ in range(n)) / n for _ in range(n_boot))
    return xs[int(0.05 * n_boot)], xs[int(0.95 * n_boot) - 1]


lines, assign_out = [], {}
emin = min(min(len(c[4]) for c in g) for g, _ in cells.values())
lines.append(f"smallest E over all gap problems of all cells: {emin}")
for version, cut in [("rules as written (full E)", None), (f"equal E: first {emin} rows of E", emin)]:
    lines.append(f"\n=== {version}")
    for name, (g, bo) in cells.items():
        labels = [assign(cap, text, gold, ev if cut is None else ev[:cut]) for _, cap, text, gold, ev in g]
        if cut is None:
            assign_out[name] = {str(i): lab for (i, *_), lab in zip(g, labels)}
            esz = Counter(len(c[4]) for c in g)
            lines.append(f"{name}: n gap {len(g)}, base-only {bo}, E rows per gap problem {dict(esz)}")
        else:
            lines.append(f"{name}: n gap {len(g)}")
        cnt = Counter(labels)
        for p in PARTS:
            lo, hi = boot(labels, p)
            lines.append(f"  {p:17s} {cnt[p]:3d}/{len(g)} = {cnt[p] / len(g):.3f}  90% [{lo:.3f}, {hi:.3f}]")

text = "\n".join(lines)
print(text)
(OUT / "budget.out.txt").write_text(text + "\n")
(OUT / "assign.json").write_text(json.dumps(assign_out, indent=1) + "\n")
