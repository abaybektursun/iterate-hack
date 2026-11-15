"""Direct test s100vote of round-15/account-2/c2: the vote-over-4 gain of RL step 100 plain on MATH-500
(specs/SPEC_direct_s100vote.md).

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.theory.analysis.direct_s100vote

G = 100 * mean over problems (vote right - mean single-sample right), percentage points. The vote is the team's
(day1_vote.vote; order-averaged = selector.tie_random, result-f941b8). Context: the same G for the cued base and final RL.
Writes studies/theory/results/direct/s100vote-01/.
"""
import itertools
import json
import pathlib

import numpy as np

from studies.rlneurons.analysis import day1_vote as V
from studies.rlneurons.analysis import frontier as F
from studies.rlneurons.analysis import selector as SEL

ROOT = pathlib.Path(__file__).resolve().parents[3]
RES = ROOT / "studies" / "rlneurons" / "results"
OUT = ROOT / "studies" / "theory" / "results" / "direct" / "s100vote-01"
N, K, B = 500, 4, 10000
RANGE, NULL_RANGE, NULL = (5.0, 10.0), (1.0, 4.5), 2.8


def step100():
    """{problem: [rows of samples 0-3]}: sample 0 from s0100_plain-01, samples 1-3 from s0100_plain_s123-01."""
    rows = [dict(r, sample=0, attempt=0) for r in json.load(open(RES / "ckptcue/s0100_plain-01/per_problem.json"))]
    rows += [json.loads(x) for x in open(RES / "ckptcue/s0100_plain_s123-01/rows.jsonl")]
    keys = sorted((r["problem_index"], r["sample"]) for r in rows)
    assert keys == [(p, s) for p in range(N) for s in range(K)], "step-100 rows incomplete"
    assert all(r["attempt"] == 0 for r in rows)
    by = {}
    for r in sorted(rows, key=lambda r: (r["problem_index"], r["sample"])):
        by.setdefault(r["problem_index"], []).append(r)
    return by


def first_attempts(folder):
    _, ch = F.load(RES / folder)
    return {i: [c[0] for c in cs] for i, cs in ch.items()}


def gain(by):
    idx = sorted(by)
    assert len(idx) == N
    single = np.array([np.mean([r["score_v3"] for r in by[i]]) for i in idx])
    plain = np.array([V.vote(by[i])["score"] for i in idx], float)
    exp = np.array([SEL.tie_random(by[i]) for i in idx])
    orders = np.array([[V.vote([by[i][k] for k in o])["score"] for i in idx] for o in itertools.permutations(range(K))], float)
    assert np.allclose(orders.mean(0), exp), "order mean differs from the random tie-break expectation"
    boot = np.random.default_rng(0).integers(0, N, (B, N))
    out = {}
    for name, v in (("order_averaged", exp), ("plain_stored_order", plain)):
        d = 100 * (v - single)
        out[name] = {"G_points": float(d.mean()), "ci90": [float(x) for x in np.percentile(d[boot].mean(1), [5, 95])],
                     "vote_right_of_500": float(v.sum())}
    # Not in the spec, added after reading rows: the part of G from problems with no wrong extracted answer, where the vote
    # gains only because rows without an answer (mostly cap hits) cast no vote.
    nowrong = np.array([all(r["score_v3"] == 1 or r["extracted_v3"] is None for r in by[i]) for i in idx])
    out["order_averaged"]["G_points_from_problems_without_wrong_answer"] = float(100 * ((exp - single) * nowrong).sum() / N)
    out["single_mean_right_of_500"] = float(single.sum())
    out["single_right_per_sample"] = [int(sum(by[i][s]["score_v3"] for i in idx)) for s in range(K)]
    out["ties_for_first"] = int(sum(V.vote(by[i])["tie"] for i in idx))
    out["no_answer_in_any_sample"] = int(sum(V.vote(by[i])["winner"] is None for i in idx))
    out["cap_hits"] = int(sum(r["cap_hit"] for i in idx for r in by[i]))
    out["cap_hits_with_extracted_answer"] = int(sum(r["cap_hit"] and r["extracted_v3"] is not None for i in idx for r in by[i]))
    out["rows_without_extracted_answer"] = int(sum(r["extracted_v3"] is None for i in idx for r in by[i]))
    return out, single, exp


def verdict(ci, n):
    lo, hi = ci
    if RANGE[0] <= lo and hi <= RANGE[1] and n >= 50:
        return "holds"
    if hi < RANGE[0] or lo > RANGE[1]:
        return "refuted"
    return "undecided"


def item(by, p, single, exp):
    return {"problem_index": p, "gold": by[p][1]["gold"], "mean_single_right": float(single[p]), "vote_right_order_averaged": float(exp[p]),
            "vote_right_plain": V.vote(by[p])["score"],
            "samples": [{k: r[k] for k in ("sample", "extracted_v3", "score_v3", "cap_hit")} for r in by[p]]}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    s100 = step100()
    g, single, exp = gain(s100)
    assert g["single_right_per_sample"] == [418, 411, 422, 419], g["single_right_per_sample"]
    base, _, _ = gain(first_attempts("day1_3/math500_base_cue-01"))
    rl, _, _ = gain(first_attempts("day1_3/math500_rl-01"))
    assert abs(base["order_averaged"]["vote_right_of_500"] - 448.2) < 0.06 and abs(rl["order_averaged"]["vote_right_of_500"] - 474.3) < 0.06
    assert base["plain_stored_order"]["vote_right_of_500"] == 446 and rl["plain_stored_order"]["vote_right_of_500"] == 474

    G, ci = g["order_averaged"]["G_points"], g["order_averaged"]["ci90"]
    v = verdict(ci, N)
    half = (ci[1] - ci[0]) / 2
    metrics = {
        "spec": "studies/theory/specs/SPEC_direct_s100vote.md", "mechanism": "round-15/account-2/c2",
        "statistic": "G = 100 * mean over problems (vote-over-4 right - mean single-sample right), percentage points; vote order-averaged (random tie-break)",
        "n": N, "G_points": G, "ci90": ci, "bootstrap": f"{B} resamples of problems, default_rng(0), 5th-95th percentile",
        "step100": g, "context_cued_base": base, "context_final_rl": rl,
        "null_value": NULL, "null_range": list(NULL_RANGE), "account_range": list(RANGE),
        "G_vs_null_range": "inside" if NULL_RANGE[0] <= G <= NULL_RANGE[1] else ("above" if G > NULL_RANGE[1] else "below"),
        "ci90_overlaps_null_range": bool(ci[0] <= NULL_RANGE[1] and ci[1] >= NULL_RANGE[0]),
        "verdict": v, "verdict_rule": "holds if the 90 % interval lies wholly inside [5.0, 10.0] and n >= 50; refuted if wholly outside; else undecided",
        "ci90_half_width": half,
    }
    json.dump(metrics, open(OUT / "metrics.json", "w"), indent=1)

    win = next(p for p in range(N) if exp[p] == 1 and single[p] <= 0.5)
    lose = next(p for p in range(N) if exp[p] == 0 and single[p] >= 0.25)
    json.dump({"vote_wins": item(s100, win, single, exp), "vote_loses": item(s100, lose, single, exp)}, open(OUT / "examples.json", "w"), indent=1)

    diff = exp - single
    for p in sorted(range(N), key=lambda p: (-abs(diff[p]), p))[:14]:
        print(p, "gold", s100[p][1]["gold"], "| vote", round(exp[p], 2), "single", single[p], "|",
              [(r["extracted_v3"], r["score_v3"], int(r["cap_hit"])) for r in s100[p]])
    print(json.dumps({k: metrics[k] for k in ("G_points", "ci90", "G_vs_null_range", "verdict")}, indent=1))
    for name, x in (("step100", g), ("base", base), ("rl", rl)):
        print(name, {k: x[k] for k in ("order_averaged", "plain_stored_order", "single_mean_right_of_500", "ties_for_first",
                                         "cap_hits", "cap_hits_with_extracted_answer")})


if __name__ == "__main__":
    main()
