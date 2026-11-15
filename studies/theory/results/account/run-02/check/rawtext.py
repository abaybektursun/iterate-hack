"""Raw-text check of two gap problems per part, and whether the hard328 capability problems are solved by the base
in any other stored cell. Run from the repository root after budget.py:
python3 studies/theory/results/account/run-02/check/rawtext.py  (writes check/rawtext.out.txt)
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
RUNS = ROOT / "runs/account-check"
OUT = Path(__file__).resolve().parent
assign = json.load(open(OUT / "assign.json"))


def first_by(name, key, keep=lambda r: True):
    d = {}
    for line in open(RUNS / name):
        r = json.loads(line)
        if keep(r) and r[key] not in d:
            d[r[key]] = r
    return d


s0 = lambda r: r["sample"] == 0
bF = first_by("base_F_math500.jsonl", "problem_index", s0)
s4 = first_by("s0400_P_math500.jsonl", "problem_index", s0)
e72c = first_by("e72c.jsonl", "problem_index")
a619 = first_by("a619.jsonl", "problem_index")
hard_uid = {k: first_by(f"{k}.jsonl", "unique_id") for k in ["base_F_hard", "base_P_hard", "base_CF_hard", "base_CP_hard"]}
b7ba0 = first_by("7ba0.jsonl", "problem_index")
day13 = {}
for line in open(ROOT / "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"):
    r = json.loads(line)
    if r["attempt"] == 0:
        day13.setdefault(r["problem_index"], []).append((r["sample"], r["score_v3"], r["extracted_v3"], r["cap_hit"]))

out = []


def show(cell, part, i, B, rl, extra=""):
    t = B["text"] or ""
    out.append(f"\n##### {cell} / {part} / problem {i} ({B.get('unique_id')})")
    out.append(f"gold {B['gold']!r}; base extracted {B.get('extracted')!r} (v1 score {B.get('score')}, v3 {B.get('score_v3')}), "
               f"n_new {B['n_new']}, cap_hit {B['cap_hit']}, finish {B['finish_reason']}, chars {len(t)}")
    out.append(f"RL side extracted {rl.get('extracted')!r} (v1 {rl.get('score')}, v3 {rl.get('score_v3')}), n_new {rl['n_new']}, cap_hit {rl['cap_hit']}")
    if extra:
        out.append(extra)
    if part == "loop":
        out.append("base text, chars 12,000 to 12,600:\n" + t[12000:12600])
    out.append("base text, last 900 chars:\n" + t[-900:])


cell = "math500-s0400-T06"
for part in ["loop", "reliability"]:
    for i in sorted(int(k) for k, v in assign[cell].items() if v == part)[:2]:
        show(cell, part, i, bF[i], s4[i], f"E (day1_3 cue T 1.0 attempt 0: sample, score_v3, extracted_v3, cap_hit): {day13.get(i)}")

cell = "hard328-code-T1"


def hard_other(i):
    B = e72c[i]
    parts = [f"e72c cue T1.0 v1/v2/v3 {B.get('score')}/{B.get('score_v2')}/{B.get('score_v3')} extracted {B.get('extracted_v3')!r}"]
    r = b7ba0.get(i)
    parts.append(f"7ba0 plain T1.0 v1/v3 {r and r.get('score')}/{r and r.get('score_v3')} extracted {r and r.get('extracted_v3')!r}")
    for k, d in hard_uid.items():
        r = d.get(B["unique_id"])
        parts.append(f"{k} T0.6 v1 {r and r.get('score')} extracted {r and r.get('extracted')!r}" if r else f"{k}: no row")
    return "; ".join(parts)


for part in ["capability", "budget"]:
    for i in sorted(int(k) for k, v in assign[cell].items() if v == part)[:2]:
        show(cell, part, i, e72c[i], a619[i], "other base rows: " + hard_other(i))

out.append("\n##### hard328 capability problems: base grade in every other stored base cell on this set")
for i in sorted(int(k) for k, v in assign[cell].items() if v == "capability"):
    out.append(f"problem {i} gold {e72c[i]['gold']!r}: " + hard_other(i))

text = "\n".join(out)
print(text)
(OUT / "rawtext.out.txt").write_text(text + "\n")
