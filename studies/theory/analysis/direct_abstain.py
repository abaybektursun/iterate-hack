"""Direct test of run-08/f2-m06, a cap hit casts no vote (specs/SPEC_direct_abstain.md).

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.theory.analysis.direct_abstain

Hard328, 4-sample vote: samples 1-3 of a stored 16,384-cap run plus the model's cap-32,768 row as the 4th vote. Set A: the
4th row abstains if it is longer than 16,384 tokens. Set B: it votes its 32,768 answer. Null A': B with every converted row
(longer than 16,384, finished, with an answer) that is wrong abstaining. Think-SFT + cue decides; RL plain is the contrast;
the 4-sample cap-32,768 run of work-dc9359 (branch cap32vote) is a secondary reading. Writes studies/theory/results/direct/abstain-01/.
"""
import collections
import json
import math
import pathlib
import subprocess

import numpy as np

from studies.rlneurons.lib import rln4_lib as R

ROOT = pathlib.Path(__file__).resolve().parents[3]
RES = ROOT / "studies" / "rlneurons" / "results"
OUT = ROOT / "studies" / "theory" / "results" / "direct" / "abstain-01"
OLD, NEW, B = 16384, 32768, 10000
CAP32VOTE = ("b0ca348", "studies/rlneurons/results/cap32vote/hard328_sft1_cue_s4-01/rows.jsonl")
ARMS = {"sft_cue": (RES / "cap32/rows-01/sft_cue.jsonl", RES / "thinkvote/hard328_sft1_cue_s4-01/rows.jsonl", (230, 207)),
        "rl_plain": (RES / "cap32/rows-01/rl_plain.jsonl", RES / "day1_3/hard328_rl_plain_s4r2-01/rows.jsonl", (195, 193))}


def jl(path):
    return [json.loads(line) for line in open(path)]


def vote(rows, tie="shortest"):
    """rows: dicts with ans, right, n (tokens); ans None abstains. Grouping as day1_vote.vote (agree on norm_v3 against the
    group's first member). Ties (frozen rule): the group whose shortest member is shortest. Sensitivity only: "order", the
    first group in row order (day1_vote's rule); "mean", the mean right over the tied groups (a random tie-break's expectation).
    Returns (right, winner answer, tie)."""
    groups = []
    for r in rows:
        if r["ans"] is None:
            continue
        x = R.norm_v3(r["ans"])
        g = next((g for g in groups if R.agree(R.norm_v3(g[0]["ans"]), x)), None)
        groups.append([r]) if g is None else g.append(r)
    if not groups:
        return 0, None, False
    top = max(len(g) for g in groups)
    tied = [g for g in groups if len(g) == top]
    if tie == "mean":
        return float(np.mean([g[0]["right"] for g in tied])), None, len(tied) > 1
    if tie == "shortest":
        tied.sort(key=lambda g: min(r["n"] for r in g))
    return tied[0][0]["right"], tied[0][0]["ans"], len(tied) > 1


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None]
    p, d = k / n, 1 + z * z / n
    c, h = (p + z * z / (2 * n)) / d, z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 4), round(c + h, 4)]


def boot(cols, f):
    """Percentile intervals (95 and 90) of f over resamples of the problems; cols are per-problem arrays."""
    rng = np.random.default_rng(0)
    n = len(cols[0])
    vals = []
    for _ in range(B):
        i = rng.integers(0, n, n)
        vals.append(f(*[c[i] for c in cols]))
    vals = np.array(vals, dtype=float)
    return {"ci95": [round(float(np.nanpercentile(vals, 2.5)), 4), round(float(np.nanpercentile(vals, 97.5)), 4)],
            "ci90": [round(float(np.nanpercentile(vals, 5)), 4), round(float(np.nanpercentile(vals, 95)), 4)]}


def arm(name):
    p4, p3, (want32, want16) = ARMS[name]
    fourth = {r["problem_index"]: r for r in jl(p4)}
    assert len(fourth) == 328
    assert sum(r["score_v3"] for r in fourth.values()) == want32, name
    assert sum(r["score_v3"] for r in fourth.values() if r["n_new"] <= OLD) == want16, name
    rest = collections.defaultdict(dict)
    for r in jl(p3):
        if r["attempt"] == 0 and r["sample"] in (1, 2, 3):
            rest[r["problem_index"]][r["sample"]] = r
    assert set(rest) == set(fourth) and all(len(v) == 3 for v in rest.values())
    idx = sorted(fourth)
    nat = lambda r: {"ans": r["extracted_v3"], "right": r["score_v3"], "n": r["n_new"], "who": f"s{r['sample']}"}
    out = {k: [] for k in ("A", "B", "Ap", "r16", "r32")}
    flips, ups, conv_wrong_agree, s1_wrong_agree, rows_out = [], [], [], [], []
    sens = {k: collections.Counter() for k in ("order, 4th row first", "order, 4th row last", "mean (random tie-break)")}
    for i in idx:
        f, s = fourth[i], [nat(rest[i][k]) for k in (1, 2, 3)]
        has = f["extracted_v3"] is not None
        conv = has and not f["cap_hit"] and f["n_new"] > OLD
        a4 = {"ans": f["extracted_v3"] if has and f["n_new"] <= OLD else None, "right": f["score_v3"], "n": f["n_new"], "who": "c32"}
        b4 = {**a4, "ans": f["extracted_v3"] if has and not f["cap_hit"] else None}
        ap4 = {**b4, "ans": None if conv and not f["score_v3"] else b4["ans"]}
        (va, wa, ta), (vb, wb, tb), (vp, _, _) = vote(s + [a4]), vote(s + [b4]), vote(s + [ap4])
        out["A"].append(va), out["B"].append(vb), out["Ap"].append(vp)
        for k, (order, tie) in zip(sens, ((lambda x: [x] + s, "order"), (lambda x: s + [x], "order"), (lambda x: s + [x], "mean"))):
            a_, b_, p_ = (vote(order(x), tie)[0] for x in (a4, b4, ap4))
            sens[k].update({"VA": a_, "VB": b_, "VAprime": p_, "D": max(a_ - b_, 0), "U": max(b_ - a_, 0)})
        out["r16"].append(f["score_v3"] if f["n_new"] <= OLD else 0), out["r32"].append(f["score_v3"])
        rec = {"problem_index": i, "gold": f["gold"], "converted": conv, "c32_answer": f["extracted_v3"], "c32_right": f["score_v3"],
               "c32_tokens": f["n_new"], "samples_1_3": [[x["ans"], x["right"], x["n"]] for x in s], "vote_A": va, "vote_B": vb,
               "vote_Aprime": vp, "winner_A": wa, "winner_B": wb, "tie_A": ta, "tie_B": tb}
        rows_out.append(rec)
        if va and not vb:
            flips.append({**rec, "how": "tie-break" if tb else "plurality", "tail": f.get("tail", "")[-400:]})
        if vb and not va:
            ups.append({**rec, "how": "tie-break" if tb else "plurality", "tail": f.get("tail", "")[-400:]})
        if conv and not f["score_v3"]:
            x = R.norm_v3(f["extracted_v3"])
            conv_wrong_agree.append(any(y["ans"] is not None and R.agree(R.norm_v3(y["ans"]), x) for y in s))
        s1 = rest[i][1]
        if not s1["cap_hit"] and s1["extracted_v3"] is not None and not s1["score_v3"]:
            x = R.norm_v3(s1["extracted_v3"])
            s1_wrong_agree.append(any(rest[i][k]["extracted_v3"] is not None and R.agree(R.norm_v3(rest[i][k]["extracted_v3"]), x) for k in (2, 3)))
    A, Bv, Ap, r16, r32 = (np.array(out[k]) for k in ("A", "B", "Ap", "r16", "r32"))
    G1, VA, VB, VAp = int(r32.sum() - r16.sum()), int(A.sum()), int(Bv.sum()), int(Ap.sum())
    ratio = lambda a, b, x, y: (b.sum() - a.sum()) / (y.sum() - x.sum()) if y.sum() != x.sum() else np.nan
    res = {"n": len(idx), "G1": G1, "right_4th_row_32k": int(r32.sum()), "right_4th_row_16k": int(r16.sum()),
           "converted_rows": int(sum(r["converted"] for r in rows_out)), "converted_right": int(sum(r["converted"] and r["c32_right"] for r in rows_out)),
           "VA": VA, "VB": VB, "VAprime": VAp, "vote_gain_VB_minus_VA": VB - VA, "ceiling_gain_VAprime_minus_VA": VAp - VA,
           "cost_VAprime_minus_VB": VAp - VB, "U": len(ups), "D": len(flips),
           "ratio_vote_gain_over_G1": round((VB - VA) / G1, 4) if G1 else None,
           "boot": {"VB_minus_VA": boot([A, Bv], lambda a, b: b.sum() - a.sum()),
                    "ratio": boot([A, Bv, r16, r32], ratio),
                    "VAprime_minus_VB": boot([Bv, Ap], lambda b, p: p.sum() - b.sum())},
           "agree_converted_wrong_with_samples_1_3": {"k": int(sum(conv_wrong_agree)), "n": len(conv_wrong_agree),
                                                      "wilson95": wilson(sum(conv_wrong_agree), len(conv_wrong_agree))},
           "agree_sample1_finished_wrong_with_samples_2_3": {"k": int(sum(s1_wrong_agree)), "n": len(s1_wrong_agree),
                                                             "wilson95": wilson(sum(s1_wrong_agree), len(s1_wrong_agree))},
           "tie_rule_sensitivity (not deciding)": {k: {m: round(float(v), 2) for m, v in c.items()} for k, c in sens.items()},
           "D_problems": [{k: v for k, v in r.items() if k != "tail"} for r in flips], "U_problems": [r["problem_index"] for r in ups]}
    return res, rows_out, flips, ups


def secondary():
    """4-sample cap-32,768 run (all four rows convert): vote over the 16,384 view (*_16 fields) against the 32,768 fields."""
    text = subprocess.run(["git", "show", ":".join(CAP32VOTE)], cwd=ROOT, check=True, capture_output=True, text=True).stdout
    by = collections.defaultdict(list)
    for line in text.splitlines():
        r = json.loads(line)
        by[r["problem_index"]].append(r)
    assert len(by) == 328 and all(len(v) == 4 for v in by.values())
    A, Bv, Ap, D, U = [], [], [], 0, 0
    s16 = s32 = 0
    order = collections.Counter()
    for i in sorted(by):
        rs = sorted(by[i], key=lambda r: r["sample"])
        a = [{"ans": r["extracted_v3_16"] if not r["cap_hit_16"] else None, "right": r["score_v3_16"], "n": r["n_new_16"]} for r in rs]
        # a cut row (cap hit at 16,384) abstains in the plan's rule even when v3 found a box in the cut text
        b = [{"ans": r["extracted_v3"] if not r["cap_hit"] else None, "right": r["score_v3"], "n": r["n_new"]} for r in rs]
        p = [{**x, "ans": None if (r["n_new"] > OLD and not r["cap_hit"] and not r["score_v3"]) else x["ans"]} for x, r in zip(b, rs)]
        va, vb, vp = vote(a)[0], vote(b)[0], vote(p)[0]
        oa, ob, op = vote(a, "order")[0], vote(b, "order")[0], vote(p, "order")[0]
        order.update({"VA4": oa, "VB4": ob, "VA4prime": op, "D4": oa and not ob, "U4": ob and not oa})
        A.append(va), Bv.append(vb), Ap.append(vp)
        D += va and not vb
        U += vb and not va
        s16 += sum(r["score_v3"] for r in rs if r["n_new"] <= OLD)
        s32 += sum(r["score_v3"] for r in rs)
    A, Bv, Ap = np.array(A), np.array(Bv), np.array(Ap)
    return {"source": f"git {CAP32VOTE[0]}:{CAP32VOTE[1]}", "single_gain_mean_of_4": (s32 - s16) / 4, "VA4": int(A.sum()), "VB4": int(Bv.sum()),
            "VA4prime": int(Ap.sum()), "D4": int(D), "U4": int(U), "ratio": round((Bv.sum() - A.sum()) / ((s32 - s16) / 4), 4),
            "boot_VB4_minus_VA4": boot([A, Bv], lambda a, b: b.sum() - a.sum()),
            "boot_VA4prime_minus_VB4": boot([Bv, Ap], lambda b, p: p.sum() - b.sum()),
            "ties_in_sample_order (day1_vote's rule)": {k: int(v) for k, v in order.items()},
            "note": "16,384 view: rows longer than 16,384 abstain (cap hit), unlike work-dc9359's posted 238, which credits a box found in the cut text"}


def instrument():
    """The vote function on the stored 4-sample 16,384 Think-SFT run, with day1_vote's tie rule, must give its posted vote (241)."""
    by = collections.defaultdict(list)
    for r in jl(ARMS["sft_cue"][1]):
        by[r["problem_index"]].append({"ans": r["extracted_v3"], "right": r["score_v3"], "n": r["n_new"]})
    got = int(sum(vote(v, "order")[0] for v in by.values()))
    assert got == 241, got
    return {"thinkvote_4_sample_vote_order_ties": got, "posted": 241, "with_shortest_ties": int(sum(vote(v)[0] for v in by.values()))}


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    inst = instrument()
    sft, sft_rows, flips, ups = arm("sft_cue")
    rl, _, _, _ = arm("rl_plain")
    sec = secondary()
    hi = sft["boot"]["ratio"]["ci95"][1]
    checks = {"D_at_least_2": sft["D"] >= 2, "ratio_ci95_upper_below_half": hi < 0.5, "VB_below_VAprime": sft["VB"] < sft["VAprime"]}
    verdict = "holds" if all(checks.values()) else "refuted"
    readout = {"spec": "studies/theory/specs/SPEC_direct_abstain.md", "mechanism": "run-08/f2-m06", "set": "hard328",
               "deciding": "Think-SFT + cue: D, the 95 % upper end of (VB - VA)/G1, VB against VA'", "checks": checks, "verdict": verdict, "instrument": inst,
               "sft_cue": sft, "rl_plain_contrast": rl, "secondary_4_sample_cap32vote": sec}
    (OUT / "readout.json").write_text(json.dumps(readout, indent=1) + "\n")
    (OUT / "sft_vote_rows.jsonl").write_text("".join(json.dumps(r) + "\n" for r in sft_rows))
    prob = {p["index"]: p["problem"] for p in json.loads((ROOT / "studies/rlneurons/data/rln3/hard.json").read_text())}
    tail = {r["problem_index"]: r["tail"] for r in jl(ARMS["sft_cue"][0])}
    tie = next(r for r in sft_rows if r["converted"] and not r["c32_right"] and r["vote_A"] and r["tie_B"])
    ex = {"supports (no D problem exists; the nearest: a wrong converted row ties the one right native vote in B, so it flips "
          "under a random or order tie-break, not under the frozen shortest-sample rule)": {**tie, "problem": prob[tie["problem_index"]], "c32_tail": tail[tie["problem_index"]]},
          "goes against (a U problem: samples 1-3 all abstain and the converted row alone makes the vote right)":
          {**ups[0], "problem": prob[ups[0]["problem_index"]], "c32_tail": tail[ups[0]["problem_index"]]}}
    assert not flips, "a D problem exists: put it in examples as the supporting item"
    (OUT / "examples.json").write_text(json.dumps(ex, indent=1) + "\n")
    print(json.dumps({k: v for k, v in readout.items() if k != "sft_cue"} | {"sft": {k: v for k, v in sft.items() if k != "D_problems"}}, indent=1))


if __name__ == "__main__":
    main()
