"""Direct test of run-02/f2-m04 (specs/SPEC_direct_m2abstain.md): on problems with exactly 1 right sample of 3, the
vote of M(2) = Think-SFT + 2 x (RL-Math - base) is right at least 0.15 less often than Think-SFT's.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.theory.analysis.direct_m2abstain

Writes studies/theory/results/direct/m2abstain-01/metrics.json and examples.json.
"""
import json
import pathlib

import numpy as np

from studies.rlneurons.analysis.day1_vote import vote as team_vote
from studies.rlneurons.lib import rln4_lib as R

ROOT = pathlib.Path(__file__).resolve().parents[3]
RES = ROOT / "studies" / "rlneurons" / "results"
OUT = ROOT / "studies" / "theory" / "results" / "direct" / "m2abstain-01"
B, THRESHOLD, N_MIN = 10000, 0.15, 50


def jl(path):
    return [json.loads(line) for line in open(path)]


def by_sample(rows, key):
    """{problem_index: {key(row): row}}"""
    out = {}
    for r in rows:
        k = key(r)
        assert k not in out.setdefault(r["problem_index"], {})
        out[r["problem_index"]][k] = r
    return out


def think(folder):
    return by_sample(jl(RES / folder / "rows.jsonl"), lambda r: r["sample"])


def m2(folder, base):
    """M(2) rows of a transplant folder keyed by sample number = (seed - index - base) / step"""
    return by_sample([r for r in jl(RES / folder / "rows.jsonl") if r["arm"] == "sft1_rl20"],
                     lambda r: r["seed"] - r["problem_index"] - base)


def triples(per_problem, keys):
    return {i: [s[k] for k in keys] for i, s in per_problem.items()}


def vote_score(rows):
    """Plurality vote; no extracted answer abstains; groups by rln4_lib.agree on norm_v3 (as day1_vote.vote); m tied top
    groups score 1/m if the right group is among them, else 0; all abstain scores 0."""
    groups = []
    for r in rows:
        if r["extracted_v3"] is None:
            continue
        x = R.norm_v3(r["extracted_v3"])
        g = next((g for g in groups if R.agree(R.norm_v3(g[0]["extracted_v3"]), x)), None)
        if g is None:
            groups.append([r])
        else:
            g.append(r)
    if not groups:
        return 0.0
    for g in groups:
        assert len({r["score_v3"] for r in g}) == 1, g
    top = max(len(g) for g in groups)
    tied = [g for g in groups if len(g) == top]
    return sum(g[0]["score_v3"] for g in tied) / len(tied)


def lone(tr):
    """{problem: (vote score, rows)} for problems with exactly 1 right sample of 3"""
    return {p: (vote_score(rs), rs) for p, rs in tr.items() if sum(r["score_v3"] for r in rs) == 1}


def boot(sets, rng):
    """10,000 resamples of each set independently; returns {name: array of resampled means}"""
    return {k: np.array([v[rng.integers(0, len(v), len(v))].mean() for _ in range(B)]) for k, v in sets.items()}


def ci(x):
    return [round(float(np.percentile(x, 5)), 4), round(float(np.percentile(x, 95)), 4)]


def mediation(L):
    comp = [[r for r in rs if not r["score_v3"]] for _, rs in L.values()]
    assert all(len(c) == 2 for c in comp)
    flat = [r for c in comp for r in c]
    agree_wrong = sum(all(r["extracted_v3"] is not None for r in c)
                      and R.agree(R.norm_v3(c[0]["extracted_v3"]), R.norm_v3(c[1]["extracted_v3"])) for c in comp)
    return {"companions": len(flat),
            "no_answer_share": round(sum(r["extracted_v3"] is None for r in flat) / len(flat), 4),
            "stored_cap_hit_share": round(sum(r["cap_hit"] for r in flat) / len(flat), 4),
            "finished_wrong_share": round(sum(r["extracted_v3"] is not None for r in flat) / len(flat), 4),
            "problems_two_companions_same_wrong_answer_share": round(agree_wrong / len(comp), 4)}


RAW_ROWS_READ = ("First 10 M(2) lone-right problems (fresh2026 9-77): 6 have both companions with no answer at 16,384 tokens and the "
                 "lone right sample wins (1.0); 4 have one companion with a finished wrong answer, a 1-1 tie (0.5), never an outvote; "
                 "2 of those 4 wrong answers were written right at the 16,384 cut (stored cap_hit true, 412026 and 1456).")


def n_to_decide(D, lo, hi, n):
    """lone-right n per arm at which the present D's 90 % interval (width scaling as 1/sqrt(n)) would clear 0.15"""
    half = (hi - lo) / 2
    need = abs(D - THRESHOLD)
    f = max((half / need) ** 2, N_MIN / min(n["think_012"], n["m2"]))
    share = {k: n[k] / 464 for k in ("think_012", "m2")}
    return {"scale_factor": round(f, 2), "lone_right_n": {k: int(np.ceil(n[k] * f)) for k in share},
            "problems_with_3_samples_per_arm": int(np.ceil(max(n[k] * f / share[k] for k in share))),
            "problems_for_n_50_only": int(np.ceil(N_MIN / min(share.values())))}


def slim(r):
    return {k: r[k] for k in ("problem_index", "sample", "seed", "n_new", "cap_hit", "extracted_v3", "score_v3", "gold") if k in r}


def main():
    # ---- load
    t_h, t_f = think("thinkvote/hard328_sft1_cue_s4-01"), think("fresh/sft1_cue_s4-01")
    c_h, c_f = think("cap32vote/hard328_sft1_cue_s4-01"), think("cap32vote/fresh2026_sft1_cue_s4-01")
    m_h = {p: {k // 100000: r for k, r in s.items()} for p, s in m2("transplant/hard328-02", 3000000).items()}
    m_f = {p: {k // 10000: r for k, r in s.items()} for p, s in m2("transplant/fresh2026-02", 7000000).items()}
    m_h1 = {p: {k // 100000: r for k, r in s.items()} for p, s in m2("transplant/hard328-01", 3000000).items()}
    m_f1 = {p: {k // 10000: r for k, r in s.items()} for p, s in m2("transplant/fresh2026-01", 7000000).items()}
    for big, small in ((m_h, m_h1), (m_f, m_f1)):
        assert set(big) == set(small)
        for p, s in small.items():
            for k, r in s.items():
                assert big[p][k] == r, (p, k)
    assert len(t_h) == len(m_h) == len(c_h) == 328 and len(t_f) == len(m_f) == len(c_f) == 136
    assert all(set(s) == {0, 1, 2} for s in m_h.values()) and all(set(s) == {0, 1, 2, 3} for s in m_f.values())
    assert all(set(s) == {0, 1, 2, 3} for d in (t_h, t_f, c_h, c_f) for s in d.values())

    # ---- instrument checks
    count = lambda d, k: sum(s[k]["score_v3"] for s in d.values())
    assert [count(m_h, k) for k in (0, 1, 2)] == [234, 229, 237]
    assert [count(m_f, k) for k in (0, 1, 2)] == [69, 75, 70]
    assert [count(t_h, k) for k in (0, 1, 2, 3)] == [212, 212, 211, 201]
    assert [count(t_f, k) for k in (0, 1, 2, 3)] == [65, 59, 56, 60]
    team = sum(team_vote([m_h[p][k] for k in (0, 1, 2)])["score"] for p in m_h)
    assert team == 246, team
    gold = {"gold": "7", "cap_hit": False, "n_new": 1}
    right, wrong5, wrong6, none = ({**gold, "extracted_v3": "7", "score_v3": 1}, {**gold, "extracted_v3": "5", "score_v3": 0},
                                   {**gold, "extracted_v3": "6", "score_v3": 0}, {**gold, "extracted_v3": None, "score_v3": 0, "cap_hit": True})
    assert vote_score([right, wrong5, wrong5]) == 0 and vote_score([right, none, none]) == 1
    assert abs(vote_score([right, wrong5, wrong6]) - 1 / 3) < 1e-12 and vote_score([none, none, none]) == 0

    # ---- triples, pooled over hard328 and fresh2026 (problem keys carry the set name)
    def pool(h, f, keys):
        return {**{("hard328", p): rs for p, rs in triples(h, keys).items()},
                **{("fresh2026", p): rs for p, rs in triples(f, keys).items()}}
    arms = {"think_012": pool(t_h, t_f, (0, 1, 2)), "think_123": pool(t_h, t_f, (1, 2, 3)),
            "m2": pool(m_h, m_f, (0, 1, 2)), "think_cap32_012": pool(c_h, c_f, (0, 1, 2))}
    L = {k: lone(v) for k, v in arms.items()}
    vr = {k: float(np.mean([s for s, _ in v.values()])) for k, v in L.items()}
    n = {k: len(v) for k, v in L.items()}

    rng = np.random.default_rng(0)
    bs = boot({k: np.array([s for s, _ in v.values()]) for k, v in L.items()}, rng)
    D = vr["think_012"] - vr["m2"]
    D_null = vr["think_012"] - vr["think_123"]
    D_bs = bs["think_012"] - bs["m2"]
    Dn_bs = bs["think_012"] - bs["think_123"]
    diff_bs = D_bs - Dn_bs
    D32_bs = bs["think_cap32_012"] - bs["m2"]
    lo, hi = ci(D_bs)
    if min(n["think_012"], n["m2"]) < N_MIN:
        verdict = "undecided"
    elif lo > THRESHOLD and ci(diff_bs)[0] > 0:
        verdict = "holds"
    elif hi < THRESHOLD:
        verdict = "refuted"
    else:
        verdict = "undecided"

    by_set = {k: {s: sum(1 for p in v if p[0] == s) for s in ("hard328", "fresh2026")} for k, v in L.items()}
    metrics = {
        "mechanism": "run-02/f2-m04",
        "statistic": "D = VR_ThinkSFT(0,1,2) - VR_M2: mean vote score (1/m tie credit) over problems with exactly 1 right of 3 samples, hard328 + fresh2026 pooled, cap 16,384, cue",
        "D": round(D, 4), "D_ci90": [lo, hi],
        "vote_rate_lone_right": {k: round(v, 4) for k, v in vr.items()},
        "vote_rate_ci90": {k: ci(v) for k, v in bs.items()},
        "n_lone_right": n, "n_lone_right_by_set": by_set,
        "vote_score_counts": {k: {str(round(x, 3)): sum(1 for v2 in v.values() if v2[0] == x) for x in sorted({v2[0] for v2 in v.values()})} for k, v in L.items()},
        "lone_right_share_of_464": {k: round(v / 464, 4) for k, v in n.items()},
        "null": {"D_null": round(D_null, 4), "D_null_ci90": ci(Dn_bs),
                 "D_minus_D_null": round(D - D_null, 4), "D_minus_D_null_ci90": ci(diff_bs)},
        "budget_route_reported_only": {"D_cap32": round(vr["think_cap32_012"] - vr["m2"], 4), "D_cap32_ci90": ci(D32_bs)},
        "mediation_reported_only": {k: mediation(v) for k, v in L.items()},
        "threshold": THRESHOLD, "n_min": N_MIN,
        "verdict_rule": "holds if min n >= 50, D 90 % interval wholly above 0.15 and D - D_null 90 % interval wholly above 0; refuted if D 90 % interval wholly below 0.15; else undecided",
        "verdict": verdict,
        "n_to_decide": n_to_decide(D, lo, hi, n),
        "raw_rows_read": RAW_ROWS_READ,
        "bootstrap": "10,000 resamples of problems, each arm's lone-right set resampled independently, numpy default_rng(0), 5th/95th percentiles",
        "instrument_checks": "passed: per-sample right counts 234/229/237, 69/75/70, 212/212/211/201, 65/59/56/60; M(2) hard328 vote over 3 with day1_vote tie rule 246/328; synthetic votes 0, 1, 1/3, 0",
        "inputs": ["studies/rlneurons/results/thinkvote/hard328_sft1_cue_s4-01/rows.jsonl", "studies/rlneurons/results/fresh/sft1_cue_s4-01/rows.jsonl",
                   "studies/rlneurons/results/transplant/hard328-02/rows.jsonl (sft1_rl20, seeds 3.0M/3.1M/3.2M)",
                   "studies/rlneurons/results/transplant/fresh2026-02/rows.jsonl (sft1_rl20, seeds 7.00M/7.01M/7.02M)",
                   "studies/rlneurons/results/cap32vote/hard328_sft1_cue_s4-01/rows.jsonl", "studies/rlneurons/results/cap32vote/fresh2026_sft1_cue_s4-01/rows.jsonl"],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=1) + "\n")

    def ex(arm, want):
        p = next(p for p in sorted(L[arm]) if L[arm][p][0] == want(L[arm]))
        return {"arm": arm, "set": p[0], "problem_index": p[1], "vote_score": L[arm][p][0], "rows": [slim(r) for r in L[arm][p][1]]}
    lowest = lambda d: min(v[0] for v in d.values())
    examples = {"note": "each arm: one lone-right problem whose vote is right (counts 1) and the one with the lowest vote score",
                "m2_vote_right": ex("m2", lambda d: 1.0), "m2_lowest_vote": ex("m2", lowest),
                "think_vote_right": ex("think_012", lambda d: 1.0), "think_lowest_vote": ex("think_012", lowest)}
    (OUT / "examples.json").write_text(json.dumps(examples, indent=1) + "\n")
    print(json.dumps({k: metrics[k] for k in ("D", "D_ci90", "vote_rate_lone_right", "n_lone_right", "null", "budget_route_reported_only", "verdict")}, indent=1))
    print(json.dumps(metrics["mediation_reported_only"], indent=1))


if __name__ == "__main__":
    main()
