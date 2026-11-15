"""Readout of the tinkerpair study (laptop, no model): writes results/readout.json and prints the tables.

    python -m studies.tinkerpair.analysis.readout

Reads every results/<experiment>/<arm>-<nn>/ named in CELLS. Per training arm and checkpoint: plain and cued accuracy on
MATH-500 with Wilson intervals, the cue's gain with a paired bootstrap interval, the cue's log-probability and the
share of plain answers with "Okay" in their first 30 characters (the measure of board result-32b7a8). Then the cue's
share of the RL gain and the vote arm against the grader arm. A cell whose folder is absent is left out.
"""
import json
import os

import numpy as np

from studies.rlneurons.lib import n13_score as S
from studies.tinkerpair.lib import tk

RES = f"{tk.STUDY}/results"
STEPS = [0, 5, 10, 20, 30, 40]
STAGE1 = {"plain": "stage1/base_plain-01", "cue": "stage1/base_cue-01"}
HARD = {"base_cue": "hard328/base_cue-01", "grader_plain": "hard328/grader_s040_plain-01", "vote_plain": "hard328/vote_s040_plain-01"}


def cell(rel: str):
    """Scores per problem (mean over samples, in index order), metrics and the 'Okay' share, or None when absent."""
    if not os.path.exists(f"{RES}/{rel}/per_problem.json"):
        return None
    rows = json.load(open(f"{RES}/{rel}/per_problem.json"))
    idx = sorted({r["index"] for r in rows})
    x = np.array([np.mean([r["score"] for r in rows if r["index"] == i]) for i in idx])
    m = json.load(open(f"{RES}/{rel}/metrics.json"))
    return {"rel": rel, "x": x, "right": m["right"], "n": m["n"], "pct": m["accuracy_pct"], "wilson": m["wilson95_pct"],
            "cap_hits": m["cap_hits"], "tokens": m["tokens_per_answer"],
            "okay_share": float(np.mean(["Okay" in r["opening"][:30] for r in rows]))}


def diff(a, b):
    """a minus b in points with the paired bootstrap 95 % interval (5,000 resamples)."""
    return {"points": float(100 * (a["x"].mean() - b["x"].mean())), "ci95": S.paired_bootstrap(a["x"], b["x"], n_boot=5000)}


def share(num_a, num_b, den_a, den_b, n_boot=5000, seed=0):
    """(num_a - num_b) / (den_a - den_b) with a paired bootstrap interval over problems. Undefined (share None) when the
    denominator, the RL gain, is not positive."""
    if den_a.mean() <= den_b.mean():
        return {"share": None, "rl_gain_points": float(100 * (den_a.mean() - den_b.mean()))}
    rng = np.random.default_rng(seed)
    i = rng.integers(0, len(num_a), size=(n_boot, len(num_a)))
    num, den = num_a[i].mean(1) - num_b[i].mean(1), den_a[i].mean(1) - den_b[i].mean(1)
    r = num[den > 0] / den[den > 0]
    return {"share": float((num_a.mean() - num_b.mean()) / (den_a.mean() - den_b.mean())),
            "ci95": (float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5))), "resamples_with_positive_gain": int((den > 0).sum())}


def pub(c):
    return None if c is None else {k: v for k, v in c.items() if k != "x"}


def logprob(name: str):
    p = f"{RES}/cue_logprob/{name}-01/metrics.json"
    return json.load(open(p))["mean_sum_logprob"] if os.path.exists(p) else None


def main():
    out = {"stage1": {}, "arms": {}, "hard328": {}}
    s1 = {k: cell(v) for k, v in STAGE1.items()}
    out["stage1"] = {k: pub(v) for k, v in s1.items()}
    if all(s1.values()):
        out["stage1"]["cue_minus_plain"] = diff(s1["cue"], s1["plain"])
    final = {}
    for arm in ("grader", "vote"):
        rows = []
        for s in STEPS:
            name = "base" if s == 0 else f"{arm}_s{s:03d}"
            p, c = cell(f"traj/{name}_plain-01"), cell(f"traj/{name}_cue-01")
            if p is None and c is None:
                continue
            rows.append({"step": s, "plain": pub(p), "cue": pub(c), "cue_gain": diff(c, p) if p and c else None,
                         "cue_sum_logprob": logprob(name)})
            if p is not None:
                final[arm] = (s, p, c)
        out["arms"][arm] = rows
        steps_file = f"{RES}/rl/{arm}-01/steps.jsonl"
        if os.path.exists(steps_file):
            st = [json.loads(line) for line in open(steps_file)]
            out["arms"][arm + "_training"] = {"steps": len(st), "sampled_tokens": sum(x["sampled_tokens"] for x in st),
                                               "grader_accuracy_first": st[0]["grader_accuracy"], "grader_accuracy_last": st[-1]["grader_accuracy"],
                                               "vote_agreement_first": st[0]["vote_agreement"], "vote_agreement_last": st[-1]["vote_agreement"]}
    b_p, b_c = cell("traj/base_plain-01"), cell("traj/base_cue-01")
    if "grader" in final and b_p and b_c:
        s, p, c = final["grader"]
        out["rl_gain"] = {"step": s, "rl_plain_minus_base_plain": diff(p, b_p), "rl_plain_minus_base_cue": diff(p, b_c),
                          "cue_share_of_rl_gain": share(b_c["x"], b_p["x"], p["x"], b_p["x"])}
    if "grader" in final and "vote" in final and final["grader"][0] == final["vote"][0]:
        out["vote_minus_grader_plain"] = {"step": final["vote"][0], **diff(final["vote"][1], final["grader"][1])}
    out["hard328"] = {k: pub(cell(v)) for k, v in HARD.items()}
    tk.dump(f"{RES}/readout.json", out)

    def f(c):
        return "         -" if c is None else f"{c['right']:>4}/{c['n']:<4} {c['pct']:5.1f}"
    print("stage 1 (cap 16,384):", {k: f(v) for k, v in s1.items()}, out["stage1"].get("cue_minus_plain"))
    for arm in ("grader", "vote"):
        print(f"\n{arm} arm, MATH-500, cap 4,096\n step  plain             cue               cue gain [95 %]        cue logprob  'Okay' share plain")
        for r in out["arms"][arm]:
            g = r["cue_gain"]
            gs = "-" if g is None else f"{g['points']:+5.1f} [{g['ci95'][0]:+.1f}, {g['ci95'][1]:+.1f}]"
            lp = "-" if r["cue_sum_logprob"] is None else f"{r['cue_sum_logprob']:.2f}"
            ok = "-" if r["plain"] is None else f"{r['plain']['okay_share']:.2f}"
            print(f" {r['step']:>4}  {f(r['plain'])}  {f(r['cue'])}  {gs:<22} {lp:>10}  {ok}")
    for k in ("rl_gain", "vote_minus_grader_plain"):
        if k in out:
            print(f"\n{k}: {json.dumps(out[k])}")
    print("\nhard328:", {k: f(v) for k, v in out["hard328"].items()})


if __name__ == "__main__":
    main()
