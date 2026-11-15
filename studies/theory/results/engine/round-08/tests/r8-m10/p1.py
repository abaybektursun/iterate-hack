"""r8-m10 prediction 1: within-problem long-minus-short precision contrast on hard328, Think-SFT cue minus RL plain."""
import json
import os
from collections import OrderedDict

from studies.theory.lib.noise import bootstrap, report, not_computable

T_PATH = "studies/rlneurons/results/thinkvote/hard328_sft1_cue_s4-01/rows.jsonl"
R_PATH = "studies/rlneurons/results/day1_3/hard328_rl_plain_s4r2-01/rows.jsonl"


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


def finished(r):
    return r.get("cap_hit") is not True and r.get("finish_reason") != "length"


def right(r):
    return r.get("score_v3") == 1


def d_for(rows):
    """d for one problem's rows of one model, or None if the problem lacks an S or an L row."""
    S = [r for r in rows if finished(r) and r["n_new"] < 8000]
    L = [r for r in rows if finished(r) and r["n_new"] >= 12000]
    if not S or not L:
        return None
    return sum(map(right, L)) / len(L) - sum(map(right, S)) / len(S)


def mean_or_zero(xs):
    return sum(xs) / len(xs) if xs else 0.0


def stat(problems):
    dT = [d for d in (d_for(t) for t, _ in problems) if d is not None]
    dR = [d for d in (d_for(r) for _, r in problems) if d is not None]
    return mean_or_zero(dT) - mean_or_zero(dR)


def stat_shared(problems):
    """Other reading: only problems kept for both models."""
    dT, dR = [], []
    for t, r in problems:
        a, b = d_for(t), d_for(r)
        if a is not None and b is not None:
            dT.append(a)
            dR.append(b)
    return mean_or_zero(dT) - mean_or_zero(dR)


def main():
    for p in (T_PATH, R_PATH):
        if not os.path.exists(p):
            not_computable(f"file not readable: {p}")
            return
    T, R = load(T_PATH), load(R_PATH)
    for rows in (T, R):
        for r in rows:
            if "n_new" not in r or r["n_new"] is None:
                not_computable("a row lacks n_new")
                return
    byT, byR = {}, {}
    for r in T:
        byT.setdefault(r["problem_index"], []).append(r)
    for r in R:
        byR.setdefault(r["problem_index"], []).append(r)
    pids = sorted(set(byT) | set(byR))
    problems = [(byT.get(p, []), byR.get(p, [])) for p in pids]

    keptT = [p for p, (t, _) in zip(pids, problems) if d_for(t) is not None]
    keptR = [p for p, (_, r) in zip(pids, problems) if d_for(r) is not None]
    shared = sorted(set(keptT) & set(keptR))
    print(json.dumps({"groups": {"Think-SFT kept problems": len(keptT), "RL kept problems": len(keptR),
                                 "kept by both": len(shared)}}))

    measured = stat(problems)
    alt = stat_shared(problems) if shared else None
    n = min(len(keptT), len(keptR))
    refuted = measured < 0.02 or len(keptT) < 5 or len(keptR) < 5
    example = None
    if keptT:
        rows = byT[keptT[0]]
        example = next((r for r in rows if finished(r) and r["n_new"] >= 12000), rows[0])
    interval = bootstrap(stat, problems)
    report(measured, n, interval, "bootstrap", refuted_by_met=refuted, alt_measured=alt, example_row=example)


main()
