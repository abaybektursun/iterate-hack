"""r4-m07 offline prediction 4: among problems where the base 4-sample vote is wrong and the
base does NOT repeat a wrong value (includes all-cap-hit / unanswered problems), fraction where
the RL vote is right."""
import json
import os
from collections import Counter, defaultdict

D = "studies/rlneurons/results/day1_3/"
BASE = D + "math500_base_cue-01/rows.jsonl"
BASE_RO = D + "math500_base_cue-01/readout.json"
RL_RO = D + "math500_rl-01/readout.json"


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


def attractors(base):
    C = defaultdict(Counter)
    for r in base:
        if r.get("attempt") != 0 or r.get("cap_hit") is not False:
            continue
        a = norm(r.get("extracted_v3"))
        if a == "" or r.get("score_v3") != 0:
            continue
        C[r["problem_index"]][a] += 1
    return {p for p, c in C.items() if max(c.values()) >= 2}


def per_problem(path, proc):
    d = json.load(open(path))
    pp = d.get("per_problem")
    if pp is None or proc not in pp:
        return None
    vals = pp[proc]
    if isinstance(vals, dict):
        return {int(k): v for k, v in vals.items()}
    idx = d.get("problem_indices")
    if idx is None or len(idx) != len(vals):
        return None
    return dict(zip(idx, vals))


def rate(attr, b, r, want_attr):
    A = [p for p in sorted(b) if p in r and b[p] == 0 and ((p in attr) == want_attr)]
    if not A:
        return None, 0, 0, None
    k = sum(1 for p in A if r[p] == 1)
    return k / len(A), k, len(A), A[0]


def main():
    for p in (BASE, BASE_RO, RL_RO):
        if not os.path.exists(p):
            return nc("file missing: " + p)
    base = load(BASE)
    for k in ("problem_index", "attempt", "cap_hit", "extracted_v3", "score_v3"):
        if any(k not in r for r in base):
            return nc("field missing: " + k)
    attr = attractors(base)
    b = per_problem(BASE_RO, "vote")
    r = per_problem(RL_RO, "vote")
    if b is None or r is None:
        return nc("readout per_problem 'vote' missing or not aligned with problem_indices")
    measured, k, n, p0 = rate(attr, b, r, False)
    if measured is None:
        return nc("set B is empty (no base-vote-wrong non-attractor problems); fraction undefined")
    alt = None
    b2 = per_problem(BASE_RO, "vote_after_restart")
    r2 = per_problem(RL_RO, "vote_after_restart")
    if b2 is not None and r2 is not None:
        alt = rate(attr, b2, r2, False)[0]
    ex = {"problem_index": p0, "base_vote": b[p0], "rl_vote": r[p0], "attractor": False}
    out({"measured": measured, "refuted_by_met": measured < 0.55, "alt_measured": alt,
         "not_computable": None, "example_row": ex, "numerator": k, "denominator": n})


main()
