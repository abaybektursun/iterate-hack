"""Critic at decoding time, stage 0 (specs/SPEC_critic.md): what stop-and-restart reaches with a perfect critic, from the stored
4-sample rows (results/day1_3/math500_<arm>-01/rows.jsonl, attempt 0 only; MATH-500, T 1.0 / top-p 1.0, grader v3).

    uv run --no-project --with numpy python -m studies.rlneurons.analysis.critic_ceiling

Procedure scored: write a sample; a critic looks at it once, after `at` of it (a share of its final length, or a token count); if the
critic says stop, the sample is dropped having cost the tokens written so far, and the next sample starts; at most k samples, the
last is always kept. Critic "key" stops exactly the samples scored wrong (needs the answer key: the ceiling). Critic "plurality"
stops the samples whose answer is not the most common answer of the problem's 4 samples or that hit the cap (no answer key: the
best the label-free target can do). Averages over the 24 orders of the 4 samples. Writes results/critic/ceiling-01/metrics.json.
"""
from __future__ import annotations

import collections
import itertools
import json
import pathlib

import numpy as np

STUDY = pathlib.Path(__file__).resolve().parents[1]
OUT = STUDY / "results" / "critic" / "ceiling-01"


def load(arm):
    by = collections.defaultdict(dict)
    for line in open(STUDY / "results" / "day1_3" / f"math500_{arm}-01" / "rows.jsonl"):
        r = json.loads(line)
        if r["attempt"] == 0:
            by[r["problem_index"]][r["sample"]] = r
    assert len(by) == 500 and all(len(v) == 4 for v in by.values())
    return by


def plurality_flags(rows):
    """Per sample: True if finished and its extracted answer is the most common among the finished samples (ties: all tied count)."""
    ans = [None if r["cap_hit"] or r["extracted_v3"] is None else r["extracted_v3"] for r in rows]
    c = collections.Counter(a for a in ans if a is not None)
    top = max(c.values()) if c else 0
    return [a is not None and c[a] == top for a in ans]


def run(by, critic, k, at, unit):
    right, tokens, n = 0.0, 0.0, 0
    for rows4 in by.values():
        rows = [rows4[s] for s in range(4)]
        keep = [bool(r["score_v3"]) for r in rows] if critic == "key" else plurality_flags(rows)
        for order in itertools.permutations(range(4), k):
            n += 1
            for j, s in enumerate(order):
                r = rows[s]
                seen = r["n_new"] * at if unit == "share" else min(r["n_new"], at)
                decided = unit == "share" or r["n_new"] > at                 # a sample shorter than the checkpoint is never judged
                if j == k - 1 or keep[s] or not decided:
                    right += r["score_v3"]
                    tokens += r["n_new"]
                    break
                tokens += seen
    return {"right_of_500": round(500 * right / n, 1), "tokens_per_problem": round(tokens / n)}


def main():
    res = {}
    for arm in ("base_cue", "rl"):
        by = load(arm)
        one = [by[i][0] for i in by]
        res[arm] = {"single": {"right_of_500": sum(r["score_v3"] for r in one), "tokens_per_problem": round(np.mean([r["n_new"] for r in one]))},
                    "agreement_of_plurality_flag_with_correct": round(float(np.mean([f == bool(r["score_v3"]) for v in by.values()
                                                                                    for f, r in zip(plurality_flags([v[s] for s in range(4)]), [v[s] for s in range(4)])])), 4)}
        for critic in ("key", "plurality"):
            for k in (2, 3, 4):
                for unit, ats in (("share", (0.1, 0.25, 0.5, 1.0)), ("tokens", (500, 1000, 2000))):
                    for at in ats:
                        res[arm][f"{critic} k={k} at {at} {unit}"] = run(by, critic, k, at, unit)
    assert not OUT.exists(), f"{OUT} exists: a rerun gets the next number"
    OUT.mkdir(parents=True)
    (OUT / "metrics.json").write_text(json.dumps(res, indent=1) + "\n")
    (OUT / "run.json").write_text(json.dumps({"command": "python -m studies.rlneurons.analysis.critic_ceiling", "inputs": "results/day1_3/math500_{base_cue,rl}-01/rows.jsonl"}, indent=1) + "\n")
    for arm, v in res.items():
        print(arm, v["single"], "plurality flag = correct:", v["agreement_of_plurality_flag_with_correct"])
        for key, x in v.items():
            if " k=" in key and (" k=2 " in key or " k=4 " in key):
                print(f"  {key:34s} {x['right_of_500']:6.1f} {x['tokens_per_problem']:6d}")


if __name__ == "__main__":
    main()
