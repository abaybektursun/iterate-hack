"""r4-m07 offline prediction 1: share of RL wrong finished samples (attempt 0) whose
normalised answer is in the base's wrong-answer set on the same problem (MATH-500, Day-1 #3)."""
import json
import os
from collections import defaultdict

BASE = "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"
RL = "studies/rlneurons/results/day1_3/math500_rl-01/rows.jsonl"


def out(d):
    print(json.dumps(d))


def nc(reason):
    out({"measured": None, "refuted_by_met": False, "alt_measured": None,
         "not_computable": reason, "example_row": None})


def norm(s):
    if s is None:
        return ""
    s = "".join(s.split())          # delete all whitespace
    s = s.strip("$")                # strip leading/trailing '$'
    s = s.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")
    s = s.replace("\\left", "").replace("\\right", "")
    if s.endswith("."):
        s = s[:-1]                  # delete one trailing '.'
    return s


def load(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def wrong_rows(rows):
    res = []
    for r in rows:
        if r.get("attempt") != 0:
            continue
        if r.get("cap_hit") is not False:
            continue
        a = norm(r.get("extracted_v3"))
        if a == "":
            continue
        if r.get("score_v3") == 0:
            res.append((r, a))
    return res


def main():
    for p in (BASE, RL):
        if not os.path.exists(p):
            return nc("file missing: " + p)
    base = load(BASE)
    rl = load(RL)
    for rows in (base, rl):
        for k in ("problem_index", "attempt", "cap_hit", "extracted_v3", "score_v3"):
            if any(k not in r for r in rows):
                return nc("field missing: " + k)
    W = defaultdict(set)
    for r, a in wrong_rows(base):
        W[r["problem_index"]].add(a)
    rlw = wrong_rows(rl)
    den = len(rlw)
    if den == 0:
        return nc("no RL wrong finished rows (denominator 0)")
    num = 0
    example = None
    per_p = defaultdict(lambda: [0, 0])
    for r, a in rlw:
        hit = a in W.get(r["problem_index"], set())
        num += int(hit)
        per_p[r["problem_index"]][0] += int(hit)
        per_p[r["problem_index"]][1] += 1
        if example is None and hit:
            example = r
    if example is None:
        example = rlw[0][0]
    measured = num / den
    # alt: macro average over problems with >= 1 RL wrong finished row
    alt = sum(n / d for n, d in per_p.values()) / len(per_p)
    out({"measured": measured, "refuted_by_met": measured < 0.36, "alt_measured": alt,
         "not_computable": None, "example_row": example,
         "numerator": num, "denominator": den})


main()
