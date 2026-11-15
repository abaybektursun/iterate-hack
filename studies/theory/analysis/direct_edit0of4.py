"""Direct test round-15/account-2/c3 (edit0of4-01). Spec: studies/theory/specs/SPEC_direct_edit0of4.md.

D = edit per-sample right rate - RL plain per-sample right rate on hard328 problems where the cued base has 0 of 4 right
(attempt-0 samples 0-3, grader v3). Null value: the base's fresh-sample rate (restarts + cap32 cut at 16,384) - RL rate.

Run from the repository root of a checkout that also holds runs/ (the raw answers.jsonl files, not in git):
    python3 studies/theory/analysis/direct_edit0of4.py --runs ../iterate-hack/runs --cap32 ../iterate-hack-shots/runs
"""
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

D13 = Path("studies/rlneurons/results/day1_3")
CELLS = {"base": "hard328_base_cue_s4r2-01", "edit": "hard328_top8x1.5_cue_s4-01", "rl": "hard328_rl_plain_s4r2-01"}
JOBS = {"base": "abaybektursun-1114-200457-e8e6", "edit": "abaybektursun-1115-055641-b417",
        "rl": "abaybektursun-1114-200505-5ff2"}
CAP32_ROWS = Path("studies/rlneurons/results/cap32/rows-02/base_cue.jsonl")
OUT = Path("studies/theory/results/direct/edit0of4-01")
CUT = 16384
ACC2 = (-0.08, 0.08)
NULL = (-0.35, -0.12)


def jl(p):
    return [json.loads(l) for l in open(p)]


def sha(t):
    return hashlib.sha256(t.encode()).hexdigest()


def select(rows):
    """Problems with 0 right among attempt-0 samples 0-3 (all four present)."""
    by = defaultdict(dict)
    for x in rows:
        if x["attempt"] == 0:
            by[x["problem_index"]][x["sample"]] = x["score_v3"]
    return sorted(p for p, s in by.items() if sorted(s) == [0, 1, 2, 3] and sum(s.values()) == 0)


def a0_rate(rows, probs):
    by = defaultdict(dict)
    for x in rows:
        if x["attempt"] == 0:
            by[x["problem_index"]][x["sample"]] = x["score_v3"]
    return {p: sum(by[p].values()) / 4 for p in probs if sorted(by[p]) == [0, 1, 2, 3]}


def boot(vals, rng, n=10000):
    vals = np.asarray(vals, float)
    idx = rng.integers(0, len(vals), size=(n, len(vals)))
    m = vals[idx].mean(1)
    return [float(np.percentile(m, 5)), float(np.percentile(m, 95))]


def verdict(lo, hi, n, rng_):
    if rng_[0] <= lo and hi <= rng_[1] and n >= 50:
        return "holds"
    if hi < rng_[0] or lo > rng_[1]:
        return "refuted"
    return "undecided"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--cap32", required=True)
    a = ap.parse_args()

    rows = {k: jl(D13 / v / "rows.jsonl") for k, v in CELLS.items()}
    # Instrument check: each rows.jsonl reproduces its metrics.json right count.
    for k, v in CELLS.items():
        m = json.load(open(D13 / v / "metrics.json"))["counts"]
        got = sum(x["score_v3"] for x in rows[k])
        assert got == m["correct_v3"] and len(rows[k]) == m["n"], (k, got, m["correct_v3"])

    probs = select(rows["base"])
    # Wrong-cell check: selecting on the edit's rows must give a different set.
    assert select(rows["edit"]) != probs
    e = a0_rate(rows["edit"], probs)
    r = a0_rate(rows["rl"], probs)
    probs = [p for p in probs if p in e and p in r]
    n = len(probs)
    d = [e[p] - r[p] for p in probs]
    E = float(np.mean([e[p] for p in probs]))
    R = float(np.mean([r[p] for p in probs]))
    D = E - R
    ci = boot(d, np.random.default_rng(0))

    # Null: base fresh samples per problem.
    base_txt = defaultdict(set)
    for x in jl(Path(a.runs) / JOBS["base"] / "answers.jsonl"):
        if x["attempt"] == 0:
            base_txt[x["problem_index"]].add(sha(x["text"]))
    cap_txt = {x["problem_index"]: sha(x["text"]) for x in jl(Path(a.cap32) / "cap32_base_cue_joined" / "answers.jsonl")}
    cap = {x["problem_index"]: x for x in jl(CAP32_ROWS)}
    fresh = defaultdict(list)
    for x in rows["base"]:
        if x["attempt"] > 0:
            fresh[x["problem_index"]].append(x["score_v3"])
    cap_fresh = {p for p in probs if cap_txt[p] not in base_txt[p]}
    for p in cap_fresh:
        c = cap[p]
        fresh[p].append(int(c["score_v3"] == 1 and c["n_new"] <= CUT and not c["cap_hit"]))
    null_probs = [p for p in probs if fresh[p]]
    b = {p: float(np.mean(fresh[p])) for p in null_probs}
    d0 = [b[p] - r[p] for p in null_probs]
    D0 = float(np.mean(d0))
    ci0 = boot(d0, np.random.default_rng(1))

    # d1 subset: problems whose cap32 sample is fresh.
    sub = [p for p in probs if p in cap_fresh]
    E1 = float(np.mean([e[p] for p in sub]))
    R1 = float(np.mean([r[p] for p in sub]))
    B1 = float(np.mean([cap[p]["score_v3"] == 1 and cap[p]["n_new"] <= CUT and not cap[p]["cap_hit"] for p in sub]))

    # Post-hoc sensitivity (not in the spec): also drop problems where a base restart is right (gives the plan's ~108-110).
    rr = {x["problem_index"] for x in rows["base"] if x["attempt"] > 0 and x["score_v3"] == 1}
    strict = [p for p in probs if p not in rr]
    d_s = [e[p] - r[p] for p in strict]
    sens = {"rule": "0 right in all base attempts (restarts too)", "n": len(strict), "D": float(np.mean(d_s)),
            "ci90": boot(d_s, np.random.default_rng(2)), "E": float(np.mean([e[p] for p in strict])),
            "R": float(np.mean([r[p] for p in strict]))}

    v = verdict(ci[0], ci[1], n, ACC2)
    half = (ci[1] - ci[0]) / 2
    # n that would decide: interval half-width scaled by sqrt(n / n_new) must fit the distance from D to the nearer edge.
    gap = min(abs(D - ACC2[0]), abs(D - ACC2[1]))
    n_decide = int(np.ceil(n * (half / gap) ** 2)) if gap > 0 else None
    where_null = "inside" if NULL[0] <= D <= NULL[1] else ("above" if D > NULL[1] else "below")
    met = {
        "test": "round-15/account-2/c3", "statistic": "E - R (edit minus RL plain per-sample right rate)",
        "D": D, "ci90": ci, "n_problems": n, "E": E, "R": R,
        "null_value": D0, "null_ci90": ci0, "null_n_problems": len(null_probs),
        "null_fresh_samples": int(sum(len(fresh[p]) for p in null_probs)),
        "null_base_fresh_rate": float(np.mean(list(b.values()))),
        "cap32_fresh_problems": len(cap_fresh),
        "d1_subset": {"n": len(sub), "E": E1, "R": R1, "B_cap32_cut16384": B1, "E_minus_R": E1 - R1},
        "sensitivity_posthoc": sens,
        "ranges": {"account-2": ACC2, "null": NULL}, "verdict": v,
        "D_vs_null_range": where_null, "n_that_would_decide": n_decide if v == "undecided" else None,
        "edit_rate_hist": {str(k): sum(1 for p in probs if e[p] == k / 4) for k in range(5)},
        "rl_rate_hist": {str(k): sum(1 for p in probs if r[p] == k / 4) for k in range(5)},
        "problems": probs,
        "notes": ["hard328 problem_index runs 0-399; d1 (syn-editreach, direct_editreach.py) loops over range(328) and "
                  "so selects 102 of these 121 problems; on its 102 this script's rows give E 0.1299, R 0.1495, as d1.",
                  "Restart rows exist only after a cap hit, so the null's fresh base rate leans toward long-running "
                  "problems."],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump(met, open(OUT / "metrics.json", "w"), indent=1)

    edit_ans = {(x["problem_index"], x["sample"]): x for x in jl(Path(a.runs) / JOBS["edit"] / "answers.jsonl")}
    pick = {}
    for p in probs:
        for s in range(4):
            x = edit_ans[(p, s)]
            pick.setdefault(x["score_v3"], x)
    keys = ["problem_index", "sample", "unique_id", "prompt", "text", "extracted_v3", "gold", "score_v3", "n_new",
            "cap_hit"]
    ex = {"right": {k: pick[1][k] for k in keys}, "wrong": {k: pick[0][k] for k in keys},
          "note": "edit (base + 1.5x top-8 RL-Math directions, cue) samples on problems where the cued base has 0 of 4"}
    json.dump(ex, open(OUT / "examples.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in met.items() if k != "problems"}, indent=1))


if __name__ == "__main__":
    main()
