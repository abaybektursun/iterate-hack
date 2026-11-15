"""Label-free selectors over the four stored samples of one run_cell --samples 4 run (specs/SPEC_selector.md, idea-664670).
Eleven fixed rules against the plurality vote of analysis/day1_vote.py, and `cv_pick`: the best rule of four folds scored on
the fifth. A rule sees n_new, cap_hit, extracted_v3, mode_v3, text, answer_prob, mean_logprob; score_v3 only scores its choice.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.selector \
        --run runs/<job-id> --out studies/rlneurons/results/selector/<arm>-<nn>

Tokens per problem = n_new of attempt 0 of all four samples; short1 also gets 4 x the shortest finished sample.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

from studies.rlneurons.analysis import day1_vote as V
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

BOOT, FOLDS, INF = 5000, 5, float("inf")
R_CAP = 16384   # a problem whose four samples all hit the cap costs 4 x the cap under early stop


def length(r):
    return INF if r["cap_hit"] else r["n_new"]


def aprob(r):
    return r["answer_prob"] or 0.0


def clean(r):
    b = R._boxes(r["text"])
    return int(not r["cap_hit"] and r["mode_v3"] == "boxed" and bool(b) and b[-1][1] >= len(r["text"]) - 200)


def restated(r):
    return r["text"].count(r["extracted_v3"].strip("$ ."))


def tie(key):
    """Plurality; among the largest groups the one with the highest key(rows, group); then the lowest sample."""
    def rule(rows, groups):
        top = max(len(g) for g in groups)
        return max((g for g in groups if len(g) == top), key=lambda g: (key(rows, g), -g[0]))[0]
    return rule


def weighted(w):
    def rule(rows, groups):
        return max(groups, key=lambda g: (sum(w(rows[k]) for k in g), -g[0]))[0]
    return rule


def drop_cap(rows, groups):
    kept = [[k for k in g if not rows[k]["cap_hit"]] for g in groups]
    kept = [g for g in kept if g] or groups
    return max(kept, key=lambda g: (len(g), -g[0]))[0]


def best(key, ok=lambda r: True):
    """The answered sample with the highest key among those that pass ok; with none, the plain vote."""
    def rule(rows, groups):
        ks = [k for g in groups for k in g if ok(rows[k])]
        return max(ks, key=lambda k: (key(rows[k]), -k)) if ks else RULES["vote"](rows, groups)
    return rule


RULES = {
    "vote": tie(lambda rows, g: 0),
    "tie_short": tie(lambda rows, g: -min(length(rows[k]) for k in g)),
    "tie_aprob": tie(lambda rows, g: max(aprob(rows[k]) for k in g)),
    "tie_mlp": tie(lambda rows, g: max(rows[k]["mean_logprob"] for k in g)),
    "tie_clean": tie(lambda rows, g: sum(clean(rows[k]) for k in g)),
    "tie_restate": tie(lambda rows, g: max(restated(rows[k]) for k in g)),
    "drop_cap": drop_cap,
    "w_invlen": weighted(lambda r: 1 / r["n_new"]),
    "w_aprob": weighted(aprob),
    "short1": best(lambda r: -r["n_new"], lambda r: not r["cap_hit"]),
    "max_aprob": best(aprob),
    "max_mlp": best(lambda r: r["mean_logprob"]),
}


# Controls for the tie-break rules, added after the first scoring; not candidates, not in cv_pick.
CONTROLS = {"tie_long": tie(lambda rows, g: max(-1 if rows[k]["cap_hit"] else rows[k]["n_new"] for k in g))}


def tie_random(rows) -> float:
    """Expected score of the plurality vote with a uniformly random choice among the largest groups."""
    groups = V.vote(rows)["groups"]
    if not groups:
        return 0.0
    tied = [g for g in groups if len(g) == max(len(g) for g in groups)]
    return sum(rows[g[0]]["score_v3"] for g in tied) / len(tied)


def pick(rows, rule):
    """(chosen sample or None, its v3 score) of one problem's four attempt-0 rows."""
    groups = V.vote(rows)["groups"]
    if not groups:
        return None, 0
    k = rule(rows, groups)
    return k, rows[k]["score_v3"]


def cv_pick(per: dict, folds: int = FOLDS) -> tuple:
    """per = {rule: 0/1 per problem}. For each fold: the rule with the most right on the other folds (a draw keeps the earlier
    rule), scored on the fold. Returns (0/1 per problem, the rule chosen for each fold)."""
    names, n = list(per), len(next(iter(per.values())))
    out, chosen = [0] * n, []
    for f in range(folds):
        train = [j for j in range(n) if j % folds != f]
        name = max(names, key=lambda m: (sum(per[m][j] for j in train), -names.index(m)))
        chosen.append(name)
        for j in range(f, n, folds):
            out[j] = per[name][j]
    return out, chosen


def readout(first: dict, rules: dict = RULES) -> dict:
    """first = {problem index: its four attempt-0 rows in sample order}."""
    idxs = sorted(first)
    picks = {m: [pick(first[i], rule) for i in idxs] for m, rule in rules.items()}
    per = {m: [p[1] for p in picks[m]] for m in rules}
    per["cv_pick"], chosen = cv_pick(per)
    ctrl = {m: [pick(first[i], rule)[1] for i in idxs] for m, rule in CONTROLS.items()}
    oracle = [int(any(r["score_v3"] for r in first[i])) for i in idxs]
    n, tok = len(idxs), sum(r["n_new"] for i in idxs for r in first[i])
    ties = [j for j, i in enumerate(idxs) if V.vote(first[i])["tie"]]

    def row(m):
        x, v = {**per, **ctrl}[m], per["vote"]
        k = sum(x)
        out = {"right": k, "n": n, "percent": 100 * k / n, "wilson95": S.wilson(k, n), "tokens_per_problem": tok / n,
               "minus_vote_points": 100 * (k - sum(v)) / n, "minus_vote_interval95": S.paired_bootstrap(x, v, BOOT),
               "wrong_to_right": sum(a > b for a, b in zip(x, v)), "right_to_wrong": sum(a < b for a, b in zip(x, v)),
               "right_in_vote_ties": sum(x[j] for j in ties)}
        if m == "short1":
            out["tokens_per_problem_early_stop"] = 4 * sum(min(min(length(r) for r in first[i]), R_CAP) for i in idxs) / n
        return out

    return {"grader": "v3 (score_v3 as written by run_cell)", "problem_indices": idxs, "folds": FOLDS, "cv_chosen_per_fold": chosen,
            "vote_ties": len(ties), "pass_at_4": {"right": sum(oracle), "n": n, "wilson95": S.wilson(sum(oracle), n)},
            "rows": {m: row(m) for m in per}, "per_problem": per,
            "controls": {"tie_random_expected_right": sum(tie_random(first[i]) for i in idxs),
                         "tie_random_expected_right_in_vote_ties": sum(tie_random(first[idxs[j]]) for j in ties),
                         **{m: row(m) for m in ctrl}},
            "picks": {m: [p[0] for p in picks[m]] for m in rules}}


def load(run: pathlib.Path) -> tuple:
    m = json.loads((run / "metrics.json").read_text())
    assert m["status"] == "done", f"the run's status is {m['status']!r}, not done"
    rows = [json.loads(l) for l in (run / "answers.jsonl").read_text().splitlines()]
    ch = V.chains(rows, m["config"]["n_problems"], m["config"]["samples"], m["config"]["restarts"])
    assert m["config"]["samples"] == 4, "the rules are specified for four samples"
    return m, {i: [c[0] for c in ch[i]] for i in ch}


def example(first, res, m, want):
    """A problem where rule m and the vote differ and m scores `want`: every sample's signals and last 600 characters."""
    idxs = res["problem_indices"]
    j = next((j for j in range(len(idxs)) if res["per_problem"][m][j] == want and res["per_problem"]["vote"][j] != want), None)
    if j is None:
        return None
    rows = first[idxs[j]]
    return {"problem_index": idxs[j], "gold": rows[0]["gold"], "prompt": rows[0]["prompt"], "rule": m, "rule_pick": res["picks"][m][j],
            "vote_pick": res["picks"]["vote"][j], "rule_score": want,
            "samples": [{"sample": r["sample"], "n_new": r["n_new"], "cap_hit": r["cap_hit"], "extracted_v3": r["extracted_v3"],
                         "score_v3": r["score_v3"], "answer_prob": r["answer_prob"], "mean_logprob": r["mean_logprob"],
                         "clean": clean(r), "text_last_600": r["text"][-600:]} for r in rows]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    run, out = pathlib.Path(a.run), pathlib.Path(a.out)
    assert not out.exists(), f"{out} exists: a rerun gets the next number"
    m, first = load(run)
    res = readout(first)
    top = max((k for k in RULES if k != "vote"), key=lambda k: res["rows"][k]["right"])
    ex = {"best_rule": top, "fixed_by_rule": example(first, res, top, 1), "broken_by_rule": example(first, res, top, 0)}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    out.mkdir(parents=True)
    (out / "run.json").write_text(json.dumps({"commit": commit, "command": " ".join(sys.argv), "source_job": m["job_id"],
                                              "source_commit": m["commit"], "config": m["config"]}, indent=1) + "\n")
    (out / "readout.json").write_text(json.dumps(res, indent=1) + "\n")
    (out / "examples.json").write_text(json.dumps(ex, indent=1) + "\n")
    print(f"pass@4 {res['pass_at_4']['right']} of {res['pass_at_4']['n']}; vote ties {res['vote_ties']}; cv chose {res['cv_chosen_per_fold']}")
    for k, r in res["rows"].items():
        print(f"{k:12s} {r['right']:4d}  {r['percent']:5.1f} % [{r['wilson95'][0]:.1f}, {r['wilson95'][1]:.1f}]  vs vote {r['minus_vote_points']:+.1f} "
              f"[{r['minus_vote_interval95'][0]:+.1f}, {r['minus_vote_interval95'][1]:+.1f}]  +{r['wrong_to_right']} -{r['right_to_wrong']}  "
              f"ties right {r['right_in_vote_ties']}  {r['tokens_per_problem']:.0f} tok" + (f" (early stop {r['tokens_per_problem_early_stop']:.0f})" if k == "short1" else ""))
    c = res["controls"]
    print(f"controls: random tie-break expects {c['tie_random_expected_right']:.1f} right ({c['tie_random_expected_right_in_vote_ties']:.1f} in the ties); "
          f"tie_long {c['tie_long']['right']} ({c['tie_long']['right_in_vote_ties']} in the ties)")


if __name__ == "__main__":
    main()
