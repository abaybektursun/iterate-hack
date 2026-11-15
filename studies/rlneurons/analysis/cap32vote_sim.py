"""cap32vote offline simulation (specs/SPEC_cap32vote.md): what the vote over 4 of Think-SFT + cue would be at a cap of 32,768
tokens, from the stored 16,384-cap rows and the one-sample cap32 run (results/cap32/readout.json: of 93 answers past 16,384,
91 finish and 23 are right, 1,747 more tokens per problem). No model is run.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.cap32vote_sim

Every stored cap hit is redrawn: it stays a cap hit with probability 2/93, finishes right with probability p, else finishes
wrong. Two models of p and two of the wrong answers, DRAWS draws each:
  p uniform    p = 23/93 for every cap hit.
  p problem    p = c * (r + 0.5) / (f + 1), r right and f finished among the problem's other three stored samples; c is set on
               hard328 so that the mean p over its cap hits is 23/93, and the same c is used on fresh2026.
  wrong distinct  every late wrong answer is a value of its own (casts a vote no other sample shares).
  wrong agree     every late wrong answer of a problem is one value: the problem's most frequent stored wrong answer if it has one.
  wrong measured  a late wrong answer repeats, with probability q, one wrong answer the problem already has (drawn among its wrong
                  finished samples, stored or late), else it is a value of its own. q = the share of agreeing pairs among the
                  pairs of finished wrong stored samples of one problem, per set. This is the model of the prediction.
A late right answer joins the problem's stored right answers. A finished late answer has 16,384 + 5,936 tokens (the cap32
mean), one that stays cut 32,768. The vote is day1_vote.vote; the rules with tokens are frontier.replay on FRONTIER_DRAWS draws.
Writes results/cap32vote/sim-01/readout.json and readout.md.
"""
from __future__ import annotations

import functools
import json
import pathlib

import numpy as np

from studies.rlneurons.analysis import day1_vote as V
from studies.rlneurons.analysis import frontier as F
from studies.rlneurons.lib import rln4_lib as R

RES = pathlib.Path(__file__).resolve().parents[1] / "results"
OUT = RES / "cap32vote" / "sim-01"
SETS = {"hard328": RES / "thinkvote" / "hard328_sft1_cue_s4-01", "fresh2026": RES / "fresh" / "sft1_cue_s4-01"}
RL_VOTE = {"hard328": RES / "day1_3" / "hard328_rl_plain_s4r2-01" / "readout.json", "fresh2026": RES / "fresh" / "rl_plain_s4-01" / "readout.json"}
OLD, NEW, DRAWS, FRONTIER_DRAWS = 16384, 32768, 400, 12
RULES = ("single", "vote2", "seq3", "seq4", "vote4")

R.agree = functools.lru_cache(maxsize=None)(R.agree)          # the same pairs of answers recur in every draw


def restart1(chains: list) -> dict:
    """One sample; after a cap hit, one more sample, whose answer is taken (the 16,384-cap rival of continuing to 32,768)."""
    a, b = chains[0][0], chains[1][0]
    if not a["cap_hit"]:
        return {"answer": a["id"], "tokens": a["n_new"], "drawn": 1, "ran_out": False}
    return {"answer": b["id"] if b["extracted_v3"] is not None else None, "tokens": a["n_new"] + b["n_new"], "drawn": 2, "ran_out": False}


def summary(per: dict) -> dict:
    return {m: {"right": int(sum(p["s0"])), "right_24": round(float(sum(p["s"])), 1), "tokens": round(float(np.mean(p["t0"])), 0)} for m, p in per.items()}


def main():
    c32 = json.loads((RES / "cap32" / "readout.json").read_text())["cells"]["sft_cue"]
    late, fin, right = c32["answers_longer_than_16384"], c32["of_them_finished"], c32["of_them_right"]
    extra = (c32["tokens_per_problem_at_32768"] - c32["tokens_per_problem_at_16384"]) * 328
    n_fin = OLD + round((extra - (late - fin) * OLD) / fin)   # tokens of a late answer that finishes
    p_cut, p_right = (late - fin) / late, right / late
    res = {"spec": "studies/rlneurons/specs/SPEC_cap32vote.md", "inputs": {"cap32": c32, **{k: str(v.relative_to(RES.parent.parent.parent)) for k, v in SETS.items()}},
           "rates": {"stays_cut": p_cut, "finishes_right": p_right, "tokens_of_a_finished_late_answer": n_fin}, "draws": DRAWS, "sets": {}}
    scale = None
    for name, folder in SETS.items():
        rows = [json.loads(x) for x in (folder / "rows.jsonl").read_text().splitlines()]
        ch = V.chains(rows, len({r["problem_index"] for r in rows}), 4, 0)
        idxs = sorted(ch)
        first = {i: [c[0] for c in ch[i]] for i in idxs}
        rl = json.loads(RL_VOTE[name].read_text())
        assert rl["problem_indices"] == idxs
        caps = [(i, s) for i in idxs for s in range(4) if first[i][s]["cap_hit"]]
        w = {}
        for i, s in caps:
            oth = [r for k, r in enumerate(first[i]) if k != s]
            w[i, s] = (sum(r["score_v3"] for r in oth if not r["cap_hit"]) + 0.5) / (sum(not r["cap_hit"] for r in oth) + 1)
        if scale is None:                                     # hard328 comes first: c such that the mean p is 23/93
            lo, hi = 0.0, 10.0
            for _ in range(60):
                scale = (lo + hi) / 2
                lo, hi = (scale, hi) if np.mean([min(scale * x, 1 - p_cut) for x in w.values()]) < p_right else (lo, scale)
        P = {"uniform": {k: p_right for k in caps}, "problem": {k: min(scale * w[k], 1 - p_cut) for k in caps}}
        stored_right = {i: next((r["extracted_v3"] for r in first[i] if r["score_v3"] and not r["cap_hit"]), first[i][0]["gold"]) for i in idxs}
        wrong = {}
        for i in idxs:
            g = [g for g in V.vote(first[i])["groups"] if not first[i][g[0]]["score_v3"] and not first[i][g[0]]["cap_hit"]]
            wrong[i] = first[i][max(g, key=len)[0]]["extracted_v3"] if g else f"99{i:04d}"
        pairs = [R.agree(R.norm_v3(a["extracted_v3"]), R.norm_v3(b["extracted_v3"])) for i in idxs for k, a in enumerate(first[i]) for b in first[i][k + 1:]
                 if not (a["cap_hit"] or b["cap_hit"] or a["score_v3"] or b["score_v3"]) and a["extracted_v3"] is not None and b["extracted_v3"] is not None]
        q_agree = float(np.mean(pairs))
        v16 = [V.vote(first[i])["score"] for i in idxs]
        out = {"n": len(idxs), "samples_cut_at_16384": len(caps), "wrong_pairs_stored": len(pairs), "wrong_pairs_agree_share": q_agree, "p_problem_scale": scale, "p_problem_mean": float(np.mean(list(P["problem"].values()))),
               "stored_16384": {"single_each": [sum(first[i][s]["score_v3"] for i in idxs) for s in range(4)], "vote4": sum(v16),
                                "rules": summary(F.replay(ch, {**{m: F.RULES[m] for m in RULES}, "restart1": restart1})),
                                "rl_vote4": int(sum(rl["per_problem"]["vote"]))}, "models": {}}
        rng = np.random.default_rng(0)
        pooled = {"single": [], "vote4": []}
        for pm in P:
            for wm in ("distinct", "agree", "measured"):
                singles, votes, front = [], [], []
                for d in range(DRAWS):
                    sim = {i: [dict(r) for r in first[i]] for i in idxs}
                    for i, s in caps:
                        u = rng.random()
                        if u < p_cut:
                            sim[i][s]["n_new"] = NEW
                        elif u < p_cut + P[pm][i, s]:
                            sim[i][s].update(n_new=n_fin, cap_hit=False, extracted_v3=stored_right[i], score_v3=1)
                        else:
                            x = wrong[i] if wm == "agree" else f"98{i:04d}{s}"
                            had = [r["extracted_v3"] for k, r in enumerate(sim[i]) if not r["cap_hit"] and not r["score_v3"] and r["extracted_v3"] is not None
                                   and (k < s or not first[i][k]["cap_hit"])]
                            if wm == "measured" and had and rng.random() < q_agree:
                                x = had[rng.integers(len(had))]
                            sim[i][s].update(n_new=n_fin, cap_hit=False, extracted_v3=x, score_v3=0)
                    singles.append(np.mean([sum(sim[i][s]["score_v3"] for i in idxs) for s in range(4)]))
                    votes.append(sum(V.vote(sim[i])["score"] for i in idxs))
                    if d < FRONTIER_DRAWS:
                        front.append(summary(F.replay({i: [[r] for r in sim[i]] for i in idxs}, {m: F.RULES[m] for m in RULES})))
                q = lambda x: {"mean": round(float(np.mean(x)), 1), "interval95": [round(float(np.percentile(x, 2.5)), 1), round(float(np.percentile(x, 97.5)), 1)]}
                out["models"][f"p {pm}, wrong {wm}"] = {
                    "single_mean_of_4": q(singles), "vote4": q(votes), "vote4_minus_16384_problems": q(np.array(votes) - sum(v16)),
                    "rules": {m: {k: round(float(np.mean([f[m][k] for f in front])), 1) for k in ("right", "right_24", "tokens")} for m in RULES}}
                if wm == "measured":
                    pooled["single"] += singles
                    pooled["vote4"] += votes
        out["prediction"] = {k: {"mean": round(float(np.mean(v)), 1), "interval95": [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]} for k, v in pooled.items()}
        res["sets"][name] = out
    OUT.mkdir(parents=True)
    (OUT / "readout.json").write_text(json.dumps(res, indent=1) + "\n")
    md = ["# cap32vote simulation: the vote over 4 of Think-SFT + cue at cap 32,768, from stored rows (no model run)", ""]
    for name, o in res["sets"].items():
        s = o["stored_16384"]
        md += [f"## {name}, n = {o['n']}: {o['samples_cut_at_16384']} of {4 * o['n']} stored samples cut at 16,384", "",
               f"Stored at 16,384: singles {s['single_each']}, vote over 4 = {s['vote4']} (RL plain vote {s['rl_vote4']}). "
               f"{100 * o['wrong_pairs_agree_share']:.1f} % of its {o['wrong_pairs_stored']} pairs of finished wrong samples agree. "
               f"Prediction at 32,768 (the two `wrong measured` models pooled): single {o['prediction']['single']['mean']} {[round(x, 1) for x in o['prediction']['single']['interval95']]}, "
               f"vote over 4 {o['prediction']['vote4']['mean']} {[round(x, 1) for x in o['prediction']['vote4']['interval95']]}.", "",
               "| model | single, mean of 4 [95 %] | vote over 4 [95 %] | vote gain over 16,384, problems [95 %] |", "|---|---|---|---|"]
        md += [f"| {k} | {m['single_mean_of_4']['mean']} {m['single_mean_of_4']['interval95']} | {m['vote4']['mean']} {m['vote4']['interval95']} | "
               f"{m['vote4_minus_16384_problems']['mean']} {m['vote4_minus_16384_problems']['interval95']} |" for k, m in o["models"].items()]
        md += ["", "| rule | cap | right (stored order) | right (24 orders) | tokens per problem |", "|---|---|---|---|---|"]
        md += [f"| `{m}` | 16,384 (stored) | {r['right']} | {r['right_24']} | {r['tokens']:,.0f} |" for m, r in s["rules"].items()]
        for k, m in o["models"].items():
            md += [f"| `{r}` | 32,768, {k} ({FRONTIER_DRAWS} draws) | {x['right']} | {x['right_24']} | {x['tokens']:,.0f} |" for r, x in m["rules"].items()]
        md.append("")
    (OUT / "readout.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
