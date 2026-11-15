"""r8-m10 prediction 2: MATH-500, precision of finished answers with n_new >= 8000, Think-SFT cue minus RL plain."""
import json
import os
from collections import OrderedDict

from studies.theory.lib.noise import bootstrap, report, not_computable

T_PATH = "studies/rlneurons/results/thinkvote/math500_sft1_cue_s4-01/rows.jsonl"
R_PATH = "studies/rlneurons/results/day1_3/math500_rl-01/rows.jsonl"


def load(path):
    """attempt == 0 (missing = 0), then first row per (problem_index, sample) in file order."""
    out = OrderedDict()
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            att = r.get("attempt")
            if att is None:
                att = 0
            if att != 0:
                continue
            key = (r["problem_index"], r["sample"])
            if key not in out:
                out[key] = r
    return list(out.values())


def keep(r):
    return r.get("cap_hit") is not True and r.get("finish_reason") != "length" and r["n_new"] >= 8000


def right(r):
    return r.get("score_v3") == 1


def prec(rows):
    k = [r for r in rows if keep(r)]
    return (sum(map(right, k)) / len(k)) if k else None


def stat(problems):
    a = prec([r for t, _ in problems for r in t])
    b = prec([r for _, rr in problems for r in rr])
    if a is None or b is None:
        return 0.0
    return a - b


def stat_paired(problems):
    """Other reading: only problems where both models have at least one kept row."""
    sub = [(t, r) for t, r in problems if any(map(keep, t)) and any(map(keep, r))]
    return stat(sub) if sub else 0.0


def main():
    for p in (T_PATH, R_PATH):
        if not os.path.exists(p):
            not_computable(f"file not readable: {p}")
            return
    T, R = load(T_PATH), load(R_PATH)
    for rows in (T, R):
        for r in rows:
            if r.get("n_new") is None:
                not_computable("a row lacks n_new")
                return
    byT, byR = {}, {}
    for r in T:
        byT.setdefault(r["problem_index"], []).append(r)
    for r in R:
        byR.setdefault(r["problem_index"], []).append(r)
    pids = sorted(set(byT) | set(byR))
    problems = [(byT.get(p, []), byR.get(p, [])) for p in pids]

    kT = [r for r in T if keep(r)]
    kR = [r for r in R if keep(r)]
    print(json.dumps({"groups": {"Think-SFT kept rows": len(kT), "RL kept rows": len(kR),
                                 "Think-SFT problems with kept rows": len({r["problem_index"] for r in kT}),
                                 "RL problems with kept rows": len({r["problem_index"] for r in kR})}}))
    if not kT or not kR:
        # an empty group: the recipe's "fewer than 20 kept rows" refutes
        from studies.theory.lib.noise import refuted_without_number
        refuted_without_number()
        return
    measured = prec(kT) - prec(kR)
    has_paired = any(any(map(keep, t)) and any(map(keep, r)) for t, r in problems)
    alt = stat_paired(problems) if has_paired else None
    refuted = measured < 0.0 or len(kT) < 20 or len(kR) < 20
    report(measured, min(len(kT), len(kR)), bootstrap(stat, problems), "bootstrap",
           refuted_by_met=refuted, alt_measured=alt, example_row=kT[0])


main()
