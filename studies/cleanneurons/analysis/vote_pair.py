"""cleanneurons Part G: the edited model against the unedited model, sample by sample and by vote over 4 samples (laptop).

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.cleanneurons.analysis.vote_pair \
        --unedited runs/<job> --edited runs/<job> --edit <edit json> --out <readout json> \
        [--check-vote <readout.json of day1_vote on the edited run>] [<name>=<unedited dir>:<edited dir> ...]

  --unedited, --edited  run_cell directories (answers.jsonl, metrics.json) made with --samples 4 --restarts 2, same prompt,
                        sampling setting and seed, so sample s of problem i has the same seed in both runs.
  --edit                the edit file of the edited run (recorded in the output only).
  --check-vote          asserts that the edited run's attempt-0 vote equals the `vote` row of that day1_vote readout.
  <name>=<u>:<e>        extra single-sample pairs (one row per problem in each run), added to the pooled difference.

Only attempt 0 of each sample is read. A run stopped by its time limit can lack restarts of cap hits, so restart rows are
never used. The script asserts that every (problem, sample) has exactly one attempt-0 row in both runs.
Per sample: right (score_v3), cap hits, rule-A loops, generated tokens per problem, and edited minus unedited in points with a
paired bootstrap interval. Pooled: per problem, the mean over samples of edited minus unedited; bootstrap over problems
(5,000 resamples, seed 0, 95 % percentile interval, n13_score.paired_bootstrap). The vote uses day1_vote.vote.
"""
from __future__ import annotations

import argparse
import json
import pathlib

from studies.rlneurons.analysis import day1_vote as V
from studies.rlneurons.lib import n13_score as S

BOOT = 5000
N = 500
K = 4


def attempt0(d: str, samples: int) -> tuple:
    """{problem: [attempt-0 row of sample 0, ..., sample samples-1]} and the run's metrics.json."""
    m = json.loads((pathlib.Path(d) / "metrics.json").read_text())
    assert m["config"]["samples"] == samples, (d, m["config"]["samples"], samples)
    by = {}
    for line in (pathlib.Path(d) / "answers.jsonl").read_text().splitlines():
        r = json.loads(line)
        if r["attempt"] != 0:
            continue
        key = (r["problem_index"], r["sample"])
        assert key not in by, f"{d}: two attempt-0 rows for problem, sample {key}"
        by[key] = r
    assert len(by) == N * samples, f"{d}: {len(by)} attempt-0 rows, {N * samples} planned"
    out = {i: [by[(i, s)] for s in range(samples)] for i in range(N)}
    return out, m


def cell(rows: list) -> dict:
    return {"right_v3": sum(r["score_v3"] for r in rows), "cap_hits": sum(r["cap_hit"] for r in rows),
            "loops_rule_A": sum(r["loop_A"] for r in rows), "tokens_per_problem": sum(r["n_new"] for r in rows) / len(rows)}


def same_problems(u: dict, e: dict) -> None:
    for i in range(N):
        for a, b in zip(u[i], e[i]):
            assert a["seed"] == b["seed"] and a["gold"] == b["gold"], f"problem {i}: seeds or gold differ between the runs"


def pooled(diffs: list) -> dict:
    """diffs: per problem, a list of edited minus unedited (one per draw)."""
    mean = [sum(d) / len(d) for d in diffs]
    zero = [0.0] * len(mean)
    return {"draws": len(diffs[0]), "points": 100 * sum(mean) / len(mean), "interval95": S.paired_bootstrap(mean, zero, BOOT)}


def example(u: dict, e: dict, want_edited_more: bool) -> dict:
    """The problem with the largest gap in samples right, in the asked direction; the first sample where the scores differ."""
    gap = {i: sum(r["score_v3"] for r in e[i]) - sum(r["score_v3"] for r in u[i]) for i in range(N)}
    i = max(range(N), key=lambda i: gap[i] if want_edited_more else -gap[i])
    assert (gap[i] > 0) if want_edited_more else (gap[i] < 0), "no problem with that direction"
    s = next(s for s in range(K) if u[i][s]["score_v3"] != e[i][s]["score_v3"])
    return {"problem_index": i, "gold": u[i][0]["gold"],
            "samples_right": {"unedited": sum(r["score_v3"] for r in u[i]), "edited": sum(r["score_v3"] for r in e[i])},
            "scores_by_sample": {"unedited": [r["score_v3"] for r in u[i]], "edited": [r["score_v3"] for r in e[i]]},
            "shown_sample": s,
            "unedited": {"extracted_v3": u[i][s]["extracted_v3"], "n_new": u[i][s]["n_new"], "cap_hit": u[i][s]["cap_hit"],
                         "loop_A": u[i][s]["loop_A"], "text_last_300": u[i][s]["text"][-300:]},
            "edited": {"extracted_v3": e[i][s]["extracted_v3"], "n_new": e[i][s]["n_new"], "cap_hit": e[i][s]["cap_hit"],
                       "loop_A": e[i][s]["loop_A"], "text_last_300": e[i][s]["text"][-300:]}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--unedited", required=True)
    ap.add_argument("--edited", required=True)
    ap.add_argument("--edit", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--check-vote", default=None)
    ap.add_argument("extra", nargs="*")
    a = ap.parse_args()
    assert pathlib.Path(a.edit).exists(), a.edit
    u, mu = attempt0(a.unedited, K)
    e, me = attempt0(a.edited, K)
    same_problems(u, e)
    for k in ("model", "prompt", "set", "temperature", "top_p", "max_tokens", "seed", "seed_rule"):
        assert mu["config"][k] == me["config"][k], f"config {k} differs: {mu['config'][k]} and {me['config'][k]}"

    per_sample = []
    for s in range(K):
        us, es = [u[i][s] for i in range(N)], [e[i][s] for i in range(N)]
        x, y = [r["score_v3"] for r in es], [r["score_v3"] for r in us]
        per_sample.append({"sample": s, "unedited": cell(us), "edited": cell(es), "points_edited_minus_unedited": 100 * (sum(x) - sum(y)) / N,
                           "interval95": S.paired_bootstrap(x, y, BOOT)})
    diffs4 = [[e[i][s]["score_v3"] - u[i][s]["score_v3"] for s in range(K)] for i in range(N)]
    pools = {"4 samples": pooled(diffs4)}

    extras, diffs_all = {}, [list(d) for d in diffs4]
    for spec in a.extra:
        name, dirs = spec.split("=", 1)
        du, de = dirs.split(":")
        xu, mxu = attempt0(du, 1)
        xe, mxe = attempt0(de, 1)
        same_problems(xu, xe)
        a1, b1 = [xe[i][0] for i in range(N)], [xu[i][0] for i in range(N)]
        x, y = [r["score_v3"] for r in a1], [r["score_v3"] for r in b1]
        extras[name] = {"unedited": {"dir": du, "job_id": mxu["job_id"], **cell(b1)}, "edited": {"dir": de, "job_id": mxe["job_id"], **cell(a1)},
                        "points_edited_minus_unedited": 100 * (sum(x) - sum(y)) / N, "interval95": S.paired_bootstrap(x, y, BOOT)}
        for i in range(N):
            diffs_all[i].append(x[i] - y[i])
    if extras:
        pools["4 samples + " + " + ".join(extras)] = pooled(diffs_all)

    hist = {name: [sum(sum(r["score_v3"] for r in R[i]) == k for i in range(N)) for k in range(K + 1)] for name, R in (("unedited", u), ("edited", e))}
    votes = {}
    for name, R in (("unedited", u), ("edited", e)):
        per = [V.vote(R[i])["score"] for i in range(N)]
        votes[name] = {"per_problem": per, **V.row(per, sum(r["n_new"] for i in range(N) for r in R[i]))}
    vote = {k: {x: y for x, y in v.items() if x != "per_problem"} for k, v in votes.items()}
    vote["points_edited_minus_unedited"] = vote["edited"]["percent"] - vote["unedited"]["percent"]
    vote["interval95"] = S.paired_bootstrap(votes["edited"]["per_problem"], votes["unedited"]["per_problem"], BOOT)

    if a.check_vote:
        ref = json.loads(pathlib.Path(a.check_vote).read_text())
        assert ref["problem_indices"] == list(range(N)), "the check readout is not on problems 0..499"
        assert ref["per_problem"]["vote"] == votes["edited"]["per_problem"], "edited attempt-0 vote differs from the check readout, per problem"
        assert abs(ref["rows"]["vote"]["tokens_per_problem"] - vote["edited"]["tokens_per_problem"]) < 1e-9, "vote tokens differ from the check readout"
        vote["check"] = {"readout": a.check_vote, "right": ref["rows"]["vote"]["right"], "tokens_per_problem": ref["rows"]["vote"]["tokens_per_problem"],
                         "result": "equal per problem and in tokens"}

    res = {"note": ("The unedited run was stopped by its 4-hour time limit. Every problem has attempt 0 of all 4 samples, but the "
                    "restarts of cap hits are incomplete. So this readout uses attempt 0 only, in both runs."),
           "setting": {k: me["config"][k] for k in ("model", "prompt", "set", "temperature", "top_p", "max_tokens", "seed", "seed_rule")},
           "grader": "v3 (score_v3 as written by run_cell)",
           "runs": {"unedited": {"dir": a.unedited, "job_id": mu["job_id"], "commit": mu["commit"], "status": mu["status"]},
                    "edited": {"dir": a.edited, "job_id": me["job_id"], "commit": me["commit"], "status": me["status"], "edit_file": a.edit}},
           "per_sample": per_sample,
           "singles_right": {"unedited": [p["unedited"]["right_v3"] for p in per_sample], "edited": [p["edited"]["right_v3"] for p in per_sample]},
           "extra_pairs": extras,
           "pooled_points_edited_minus_unedited": pools,
           "samples_right_of_4_histogram": {"index": "number of problems right in 0, 1, 2, 3, 4 of the 4 samples", **hist},
           "vote_over_4_attempt0_samples": vote,
           "examples": {"edited_right_more_often": example(u, e, True), "unedited_right_more_often": example(u, e, False)}}
    pathlib.Path(a.out).write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: res[k] for k in ("singles_right", "pooled_points_edited_minus_unedited", "samples_right_of_4_histogram", "vote_over_4_attempt0_samples")}, indent=1))
    print(json.dumps([{k: p[k] for k in ("sample", "points_edited_minus_unedited", "interval95")} | {"cap": [p["unedited"]["cap_hits"], p["edited"]["cap_hits"]],
                      "loops": [p["unedited"]["loops_rule_A"], p["edited"]["loops_rule_A"]],
                      "tok": [round(p["unedited"]["tokens_per_problem"]), round(p["edited"]["tokens_per_problem"])]} for p in per_sample]))
    print(json.dumps({k: {x: y for x, y in v.items() if x not in ("dir",)} for k, v in extras.items()}, indent=1))


if __name__ == "__main__":
    main()
