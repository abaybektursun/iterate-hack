"""r4-m07 offline prediction 2: on attractor problems (a normalised base wrong answer appears
>= 2 times among base attempt-0 rows), share of RL wrong finished samples equal to the base's
modal wrong value(s) (MATH-500, Day-1 #3)."""
import json
import os
from collections import Counter, defaultdict

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
    s = "".join(s.split())
    s = s.strip("$")
    s = s.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")
    s = s.replace("\\left", "").replace("\\right", "")
    if s.endswith("."):
        s = s[:-1]
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
    C = defaultdict(Counter)
    for r, a in wrong_rows(base):
        C[r["problem_index"]][a] += 1
    M = {}
    for p, c in C.items():
        mx = max(c.values())
        if mx >= 2:
            M[p] = {s for s, n in c.items() if n == mx}
    num = den = 0
    example = None
    per_p = defaultdict(lambda: [0, 0])
    for r, a in wrong_rows(rl):
        p = r["problem_index"]
        if p not in M:
            continue
        den += 1
        hit = a in M[p]
        num += int(hit)
        per_p[p][0] += int(hit)
        per_p[p][1] += 1
        if example is None and hit:
            example = r
        if example is None:
            example_fallback = r
    if den == 0:
        measured = 0.0
        alt = None
    else:
        measured = num / den
        alt = sum(n / d for n, d in per_p.values()) / len(per_p)
        if example is None:
            example = example_fallback
    out({"measured": measured, "refuted_by_met": measured < 0.50, "alt_measured": alt,
         "not_computable": None, "example_row": example,
         "numerator": num, "denominator": den, "n_attractor_problems": len(M)})


main()
