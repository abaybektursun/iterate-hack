"""Day-1 #3 readout (specs/SPEC_day1_3.md): the single, restart, vote and pass@k rows of one run_cell run made with --samples k
--restarts r. Grader v3 scores as written by run_cell (score_v3, extracted_v3); the vote groups answers with rln4_lib.agree.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_vote \
        --run runs/<job-id> --out studies/rlneurons/results/day1_3/<arm>-<nn> [--minus <readout.json of another run>]

  --run    a directory with answers.jsonl and metrics.json (uv run tools/gpu.py get <job-id> gives runs/<job-id>/).
  --out    a new run folder: readout.json, examples.json, run.json (commit, job id, config), metrics.json (copy).
  --minus  adds, per row, this run minus that run in points with a paired bootstrap interval (same problems required).

Tokens per problem = every generated token (n_new) of every attempt the row uses, over the number of problems.
Fail loud: an unfinished run (a missing sample or a cap hit without its restart) is an assertion error, not a partial row.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil

from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

BOOT = 5000


def vote(rows: list) -> dict:
    """Plurality vote over the rows of one problem, in sample order. A row with no extracted answer casts no vote. A row joins
    the first group whose first member's answer agrees with its own (R.agree on norm_v3 of both), else starts a group. The
    largest group wins; among equally large groups, the one whose first member has the lowest sample number. The vote's score
    is the v3 score of the winning group's first member; with no group the vote has no answer and scores 0."""
    groups = []
    for k, r in enumerate(rows):
        if r["extracted_v3"] is None:
            continue
        x = R.norm_v3(r["extracted_v3"])
        g = next((g for g in groups if R.agree(R.norm_v3(rows[g[0]]["extracted_v3"]), x)), None)
        if g is None:
            groups.append([k])
        else:
            g.append(k)
    if not groups:
        return {"winner": None, "score": 0, "votes": 0, "tie": False, "groups": []}
    top = max(len(g) for g in groups)
    tied = [g for g in groups if len(g) == top]
    return {"winner": tied[0][0], "score": rows[tied[0][0]]["score_v3"], "votes": top, "tie": len(tied) > 1, "groups": groups}


def chains(rows: list, n_problems: int, samples: int, restarts: int) -> dict:
    """{problem index: [attempts of sample 0, attempts of sample 1, ...]}, each list in attempt order. Asserts the run is complete:
    every problem has every sample, attempts are 0..k, every attempt before the last hit the cap, and the last attempt either
    finished or is attempt number `restarts`."""
    by = {}
    for r in rows:
        key = (r["problem_index"], r["sample"], r["attempt"])
        assert key not in by, f"two rows for problem, sample, attempt {key}"
        by[key] = r
    idxs = sorted({k[0] for k in by})
    assert len(idxs) == n_problems, f"{len(idxs)} problems in the rows, {n_problems} planned"
    out = {}
    for i in idxs:
        out[i] = []
        for s in range(samples):
            ch = []
            while (i, s, len(ch)) in by:
                ch.append(by[(i, s, len(ch))])
            assert ch, f"problem {i} sample {s}: no row (unfinished run)"
            assert all(r["cap_hit"] for r in ch[:-1]), f"problem {i} sample {s}: a restart follows a finished attempt"
            assert not ch[-1]["cap_hit"] or len(ch) == restarts + 1, f"problem {i} sample {s}: cap hit without its restart (unfinished run)"
            out[i].append(ch)
    assert sum(len(ch) for v in out.values() for ch in v) == len(rows), "rows outside the planned samples and attempts"
    return out


def row(scores: list, tokens: int) -> dict:
    k, n = int(sum(scores)), len(scores)
    return {"right": k, "n": n, "percent": 100 * k / n, "wilson95": S.wilson(k, n), "tokens_per_problem": tokens / n}


def tail(r: dict) -> dict:
    return {"sample": r["sample"], "attempt": r["attempt"], "seed": r["seed"], "cap_hit": r["cap_hit"], "n_new": r["n_new"],
            "extracted_v3": r["extracted_v3"], "score_v3": r["score_v3"], "text_chars": len(r["text"]), "text_last_2000": r["text"][-2000:]}


def readout(rows: list, n_problems: int, samples: int, restarts: int) -> tuple:
    ch = chains(rows, n_problems, samples, restarts)
    idxs = sorted(ch)
    first = {i: [c[0] for c in ch[i]] for i in idxs}                  # attempt 0 of every sample
    last = {i: [c[-1] for c in ch[i]] for i in idxs}                  # the restart rule's answer of every sample
    tok0 = {i: [c[0]["n_new"] for c in ch[i]] for i in idxs}
    tok = {i: [sum(r["n_new"] for r in c) for c in ch[i]] for i in idxs}
    v0 = {i: vote(first[i]) for i in idxs}
    v1 = {i: vote(last[i]) for i in idxs}
    per = {"single": [first[i][0]["score_v3"] for i in idxs], "restart": [last[i][0]["score_v3"] for i in idxs],
           "vote": [v0[i]["score"] for i in idxs], "pass_at_k": [int(any(r["score_v3"] for r in first[i])) for i in idxs],
           "vote_after_restart": [v1[i]["score"] for i in idxs],
           "pass_at_k_after_restart": [int(any(r["score_v3"] for r in last[i])) for i in idxs]}
    all0, all1 = sum(sum(tok0[i]) for i in idxs), sum(sum(tok[i]) for i in idxs)
    tokens = {"single": sum(tok0[i][0] for i in idxs), "restart": sum(tok[i][0] for i in idxs), "vote": all0, "pass_at_k": all0,
              "vote_after_restart": all1, "pass_at_k_after_restart": all1}
    hist = {}
    for i in idxs:
        hist[len(ch[i][0])] = hist.get(len(ch[i][0]), 0) + 1
    res = {"grader": "v3 (rln4_lib.grade_v3, as written by run_cell)", "samples": samples, "restarts": restarts, "problem_indices": idxs,
           "rows": {k: row(per[k], tokens[k]) for k in per},
           "each_sample": {"single_right": [sum(first[i][s]["score_v3"] for i in idxs) for s in range(samples)],
                           "restart_right": [sum(last[i][s]["score_v3"] for i in idxs) for s in range(samples)],
                           "cap_hits_attempt_0": [sum(first[i][s]["cap_hit"] for i in idxs) for s in range(samples)]},
           "restart_sample_0": {"attempts_hist": hist, "final_cap_hits": sum(last[i][0]["cap_hit"] for i in idxs),
                                "final_cap_hits_right": sum(last[i][0]["cap_hit"] and last[i][0]["score_v3"] for i in idxs)},
           "vote_stats": {"ties_for_first": sum(v0[i]["tie"] for i in idxs), "no_answer_in_any_sample": sum(v0[i]["winner"] is None for i in idxs),
                          "votes_of_winner_hist": {str(k): sum(v0[i]["votes"] == k for i in idxs) for k in range(samples + 1)},
                          "samples_without_answer": sum(r["extracted_v3"] is None for i in idxs for r in first[i])},
           "differences_points": {f"{k} - single": {"points": 100 * (sum(per[k]) - sum(per["single"])) / len(idxs),
                                                    "interval95": S.paired_bootstrap(per[k], per["single"], BOOT)}
                                  for k in ("restart", "vote", "vote_after_restart")},
           "per_problem": per}

    def example(name, votes, picked, want):
        i = next((i for i in sorted(idxs, key=lambda i: -len(picked(i))) if per[name][idxs.index(i)] == want), None)   # most attempts first
        if i is None:
            return None
        return {"problem_index": i, "gold": first[i][0]["gold"], "prompt": first[i][0]["prompt"], "score": want,
                "vote": {k: votes[i][k] for k in ("winner", "votes", "tie", "groups")} if votes else None,
                "attempts": [tail(r) for r in picked(i)]}

    ex = {"vote": {"right": example("vote", v0, lambda i: first[i], 1), "wrong": example("vote", v0, lambda i: first[i], 0)},
          "restart": {"right": example("restart", None, lambda i: ch[i][0], 1), "wrong": example("restart", None, lambda i: ch[i][0], 0)}}
    return res, ex


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--minus", default=None)
    a = ap.parse_args()
    run, out = pathlib.Path(a.run), pathlib.Path(a.out)
    assert not out.exists(), f"{out} exists: a rerun gets the next number"
    m = json.loads((run / "metrics.json").read_text())
    assert m["status"] == "done", f"the run's status is {m['status']!r}, not done"
    cfg = m["config"]
    rows = [json.loads(l) for l in (run / "answers.jsonl").read_text().splitlines()]
    res, ex = readout(rows, cfg["n_problems"], cfg["samples"], cfg["restarts"])
    res = {"run": {k: cfg[k] for k in ("model", "prompt", "set", "temperature", "top_p", "max_tokens", "seed", "seed_rule")}, **res}
    if a.minus:
        other = json.loads(pathlib.Path(a.minus).read_text())
        assert other["problem_indices"] == res["problem_indices"], "the two runs are not on the same problems"
        res["minus"] = {"readout": a.minus, "run": other["run"],
                        "differences_points": {k: {"points": res["rows"][k]["percent"] - other["rows"][k]["percent"],
                                                   "interval95": S.paired_bootstrap(res["per_problem"][k], other["per_problem"][k], BOOT)}
                                               for k in res["rows"]}}
    out.mkdir(parents=True)
    shutil.copy(run / "metrics.json", out / "metrics.json")
    (out / "run.json").write_text(json.dumps({"commit": m["commit"], "job_id": m["job_id"], "config": cfg, "source": str(run)}, indent=1) + "\n")
    (out / "readout.json").write_text(json.dumps(res, indent=1) + "\n")
    (out / "examples.json").write_text(json.dumps(ex, indent=1) + "\n")
    for k, r in res["rows"].items():
        print(f"{k:24s} {r['right']:4d} of {r['n']}  {r['percent']:5.1f} %  [{r['wilson95'][0]:.1f}, {r['wilson95'][1]:.1f}]  "
              f"{r['tokens_per_problem']:9.0f} tokens/problem")
    print(json.dumps({k: res[k] for k in ("each_sample", "restart_sample_0", "vote_stats", "differences_points")}, indent=1))
    if a.minus:
        print(json.dumps(res["minus"], indent=1))


if __name__ == "__main__":
    main()
