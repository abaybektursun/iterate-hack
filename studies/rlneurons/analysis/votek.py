"""Vote over k samples of one cell, k = 1 to K (specs/SPEC_votek.md).

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.votek \
        --runs runs/<stored 4-sample job> runs/<shard>+runs/<shard>+... --out studies/rlneurons/results/votek/math500_base_cue-01

Run from the repository root. Each --runs entry is one cell: a run_cell folder (answers.jsonl, metrics.json) or its shards joined
with + (same config, no problem twice). Attempt 0 of every sample is used and
the samples of the runs are numbered in the order given. The vote is the rule of analysis/day1_vote.vote, computed from one
table per problem of which answers agree (rln4_lib.agree on norm_v3), so that a subset costs no grader call; the script asserts
that it equals day1_vote.vote on the first 4 samples of every problem. For each k: the mean over 200 random
subsets of k samples (kept in sample order; all samples for k = K) of right problems, with a bootstrap over problems (2,000
resamples) of that mean; at least one of k right; generated tokens per problem. Writes metrics.json, rows.jsonl (compact fields,
no text), examples.json and run.json.
"""
import argparse
import json
import pathlib

import numpy as np

from studies.rlneurons.analysis.day1_vote import COMPACT
from studies.rlneurons.lib import rln4_lib as R

SUBSETS = 200


def agree_table(rows):
    """same[i][j]: the answers of samples i and j agree; a sample with no answer agrees with nothing."""
    x = [None if r["extracted_v3"] is None else R.norm_v3(r["extracted_v3"]) for r in rows]
    return [[x[i] is not None and x[j] is not None and (i == j or R.agree(x[i], x[j])) for j in range(len(rows))] for i in range(len(rows))]


def vote(rows, same, sub):
    """day1_vote.vote over the samples `sub` (in order): a row joins the first group whose first member agrees with it."""
    groups = []
    for s in sub:
        if rows[s]["extracted_v3"] is None:
            continue
        g = next((g for g in groups if same[g[0]][s]), None)
        if g is None:
            groups.append([s])
        else:
            g.append(s)
    if not groups:
        return {"winner": None, "score": 0, "votes": 0}
    g = max(groups, key=len)                                                    # max keeps the first of equally large groups
    return {"winner": g[0], "score": rows[g[0]]["score_v3"], "votes": len(g)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    assert not out.exists(), f"{out} exists: a rerun gets the next number"
    per, cfgs, base = {}, [], 0
    keys = ("model", "prompt", "set", "temperature", "top_p", "max_tokens", "seed", "samples")
    for group in a.runs:                                                         # one cell; A+B+C = the shards of one cell
        seen, first = set(), None
        for run in map(pathlib.Path, group.split("+")):
            m = json.loads((run / "metrics.json").read_text())
            assert m["status"] == "done", (run, m["status"])
            c = {k: m["config"][k] for k in keys}
            first = first or c
            assert c == first, f"{run}: the shards of one cell differ in {c} vs {first}"
            cfgs.append({"run": str(run), "job_id": m.get("job_id"), "shard": m["config"].get("shard"), "commit": m["config"]["commit"], **c})
            for line in open(run / "answers.jsonl"):
                r = json.loads(line)
                if r["attempt"] == 0:
                    assert (r["problem_index"], r["sample"]) not in seen, f"{run}: problem {r['problem_index']} sample {r['sample']} is in two shards"
                    seen.add((r["problem_index"], r["sample"]))
                    per.setdefault(r["problem_index"], {})[base + r["sample"]] = r
        base += first["samples"]
    K = base
    probs = sorted(per)
    assert all(sorted(per[p]) == list(range(K)) for p in probs), "a problem lacks a sample"
    seeds = [per[p][s]["seed"] for p in probs for s in range(K)]
    assert len(set(seeds)) == len(seeds), "two samples share a seed"
    rows = {p: [per[p][s] for s in range(K)] for p in probs}
    same = {p: agree_table(rows[p]) for p in probs}
    from studies.rlneurons.analysis import day1_vote
    assert all(vote(rows[p], same[p], range(4))["score"] == day1_vote.vote(rows[p][:4])["score"] for p in probs), "the table vote differs from day1_vote.vote"
    rng = np.random.default_rng(0)
    bs = rng.integers(0, len(probs), (2000, len(probs)))
    res = {"problems": len(probs), "samples": K, "runs": cfgs, "k": {}}
    stored4 = sum(vote(rows[p], same[p], range(4))["score"] for p in probs)
    res["vote_over_first_4_in_order"] = stored4
    for k in range(1, K + 1):
        subsets = [sorted(rng.choice(K, k, replace=False).tolist()) for _ in range(SUBSETS)] if k < K else [list(range(K))]
        v = np.array([[vote(rows[p], same[p], sub)["score"] for p in probs] for sub in subsets], dtype=float)      # subsets x problems
        anyr = np.array([[max(per[p][s]["score_v3"] for s in sub) for p in probs] for sub in subsets], dtype=float)
        tok = np.mean([[sum(per[p][s]["n_new"] for s in sub) for p in probs] for sub in subsets])
        pm = v.mean(0)
        b = pm[bs].sum(1)
        res["k"][str(k)] = {"vote_right": round(float(pm.sum()), 1), "ci95": [round(float(np.percentile(b, 2.5)), 1), round(float(np.percentile(b, 97.5)), 1)],
                            "subset_min_max": [int(v.sum(1).min()), int(v.sum(1).max())], "any_right": round(float(anyr.mean(0).sum()), 1), "tokens_per_problem": round(float(tok))}
    full = {p: vote(rows[p], same[p], range(K)) for p in probs}
    right_count = {p: sum(per[p][s]["score_v3"] for s in range(K)) for p in probs}
    res["vote_all_wrong_by_right_samples"] = {str(c): sum(1 for p in probs if not full[p]["score"] and right_count[p] == c) for c in range(K + 1)}
    res["vote_all_wrong_with_majority_group"] = sum(1 for p in probs if not full[p]["score"] and full[p]["votes"] > K / 2)
    ex = []
    for want in (1, 0):
        p = next(p for p in probs if full[p]["score"] == want and full[p]["winner"] is not None)
        ex.append({"problem_index": p, "vote_score": want, "votes": full[p]["votes"], "gold": per[p][0]["gold"], "answers": [per[p][s]["extracted_v3"] for s in range(K)],
                   "scores": [per[p][s]["score_v3"] for s in range(K)], "winner_text_tail": per[p][full[p]["winner"]]["text"][-400:]})
    out.mkdir(parents=True)
    (out / "metrics.json").write_text(json.dumps(res, indent=1) + "\n")
    (out / "examples.json").write_text(json.dumps(ex, indent=1) + "\n")
    with open(out / "rows.jsonl", "w") as f:
        for p in probs:
            for s in range(K):
                f.write(json.dumps({k: (s if k == "sample" else per[p][s][k]) for k in COMPACT}) + "\n")
    (out / "run.json").write_text(json.dumps({"command": "python -m studies.rlneurons.analysis.votek --runs " + " ".join(a.runs) + " --out " + a.out, "runs": cfgs}, indent=1) + "\n")
    print(json.dumps({k: res[k] for k in res if k != "runs"}, indent=1))


if __name__ == "__main__":
    main()
