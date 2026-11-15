"""Readout of jobs/steer_gen.py (specs/SPEC3_steer.md): reads answers.jsonl of one or more run folders (the arm `none` must be
in one of them) and writes metrics.json and examples.json to the result folder.

    PYTHONPATH=. python3 -m studies.jspace.analysis.steer_analyze --runs runs/<job-id> [runs/<job-id> ...] --out <result folder>
        [--partial runs/<job-id> ...] [--t1 runs/diag_t1t2/T1.jsonl] [--stored <rows.jsonl of stored unsteered samples>] [--items <per_problem.json>] [--target 1.41]

Per arm: right of n (grader v3), cap hits, rule-A loops, answers that end without a final answer, tails flagged as unrelated
words (day1_wdiff.word_salad, a crude flag), generated tokens, written hold-on words per 1,000 tokens. Against
`none`, paired over problems: difference in points with a 95 % percentile interval (bootstrap over problems, 2,000 resamples),
answers gained and lost in total and by subject, identical answers. --partial: runs listed here may be unfinished (a job that ran out of time; the
rest of its arm comes from a second job started with --pick). --t1: the stored T1 rows, for the count of answers
identical to them. --stored: rows of earlier unsteered cells at the same setting (studies/rlneurons/results/day1_3/
math500_base_cue-01/rows.jsonl: four samples per problem, attempt 0 used); each arm is also compared with the per-problem mean of
those samples, which carries less sampling noise than the one `none` sample. --items: studies/rlneurons/results/rln4/
t1_t2_items-01/per_problem.json, for gained and lost answers by group (both models right in T1 and T2, RL only, ...). --target: the hold-on rate ratio against `none` that the strength rule of the spec interpolates to
(log-linear in strength between the two neighbouring strengths of each steering site and of the bias arms).
First divergence: every arm shares its sampling noise with `none`, so an answer equals the `none` answer up to the first
position where the arm changed the next-token distribution enough; reported are the median character offset of that position
and how often the arm's first differing word is a hold-on word.
Examples: per arm the shortest answer scored right and the shortest finished answer scored wrong, in full.
Needs numpy only. Fail loud: no try/except.
"""
import argparse
import collections
import json
import math
import pathlib
import re

import numpy as np

from studies.jspace.lib import steer as ST
from studies.rlneurons.analysis.day1_wdiff import word_salad

RNG = np.random.default_rng(0)
B = 2000


def boot_diff(a, b):
    d = np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)
    s = d[RNG.integers(0, len(d), size=(B, len(d)))].mean(1)
    return {"points": 100 * float(d.mean()), "ci95": [100 * float(np.percentile(s, 2.5)), 100 * float(np.percentile(s, 97.5))]}


def subject(row):
    return row["unique_id"].split("/")[1]


FIRST_HOLD = re.compile(r"\W*(?:[Ww]ait|[Hh]mm+)\b")


def first_divergence(arm_text, none_text):
    """(character offset of the start of the first differing word, is the arm's word there a hold-on word), or None if one text
    is a prefix of the other."""
    n = min(len(arm_text), len(none_text))
    i = next((k for k in range(n) if arm_text[k] != none_text[k]), n)
    if i == n:
        return None
    while i > 0 and arm_text[i - 1].isalnum():
        i -= 1
    return i, bool(FIRST_HOLD.match(arm_text[i:i + 12]))


def interpolate(points, target):
    """points: [(strength, ratio)] sorted by strength. The strength where the ratio crosses target, log-linear; None if it does not."""
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if min(y0, y1) <= target <= max(y0, y1) and y0 != y1 and min(y0, y1) > 0:
            w = (math.log(target) - math.log(y0)) / (math.log(y1) - math.log(y0))
            return float(math.exp(math.log(x0) + w * (math.log(x1) - math.log(x0))))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--t1")
    ap.add_argument("--partial", nargs="*", default=[], help="run folders of jobs that ran out of time: their finished rows are used")
    ap.add_argument("--stored")
    ap.add_argument("--items")
    ap.add_argument("--target", type=float, default=1.41)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows, jobs = collections.defaultdict(dict), []
    for run in a.runs:
        jm = json.loads((pathlib.Path(run) / "metrics.json").read_text())
        ck = json.loads((pathlib.Path(run) / "checks.json").read_text())
        assert (jm["status"] == "done" or run in a.partial) and ck["pass"], (run, jm["status"], ck["pass"])
        jobs.append({"run": run, "job_id": jm["job_id"], "commit": jm["commit"], "arms": list(jm["arms"]), "status": jm["status"], "wall_s": jm.get("wall_s"),
                     "max_tokens": jm["config"]["max_tokens"], "n_problems": jm["config"]["n_problems"], "seed": jm["config"]["seed"],
                     "block_norm_median": ck["block_norm_median"], "applied_vector_norm": {k: v["applied_vector_norm"] for k, v in jm["arms"].items()},
                     "generation_s": {k: v.get("generation_s") for k, v in jm["arms"].items()}, "pick": jm["config"].get("pick"), "checks": ck})
        for line in open(pathlib.Path(run) / "answers.jsonl"):
            r = json.loads(line)
            key = (r["problem_index"], r["sample"])
            assert key not in rows[r["arm"]], ("an arm is in two runs", r["arm"], key)
            rows[r["arm"]][key] = r
    assert "none" in rows, "no run holds the arm none"
    keys = sorted(rows["none"])
    assert all(sorted(v) == keys for v in rows.values()), {k: len(v) for k, v in rows.items()}
    t1 = {json.loads(l)["problem_index"]: json.loads(l) for l in open(a.t1)} if a.t1 else None
    none = [rows["none"][k] for k in keys]
    stored, stored_mean = None, None
    if a.stored:
        by = collections.defaultdict(list)
        for line in open(a.stored):
            r = json.loads(line)
            if r["attempt"] == 0:
                by[r["problem_index"]].append(r)
        assert all(len(by[k[0]]) == len(by[keys[0][0]]) for k in keys), "stored samples per problem differ"
        stored_mean = [float(np.mean([r["score_v3"] for r in by[k[0]]])) for k in keys]
        flat = [r for k in keys for r in by[k[0]]]
        stored = {"file": a.stored, "samples_per_problem": len(by[keys[0][0]]), "right_per_sample_mean": float(np.sum(stored_mean)),
                  "percent": 100 * float(np.mean(stored_mean)), "tokens_mean": float(np.mean([r["n_new"] for r in flat])),
                  "cap_hits_per_sample_mean": sum(r["cap_hit"] for r in flat) / len(by[keys[0][0]])}
    group = {int(r["problem_index"]): r["cell"] for r in json.load(open(a.items))} if a.items else None
    rate = lambda rs: 1000 * sum(r["hold_words"] for r in rs) / sum(r["n_new"] for r in rs)

    arms, examples = {}, {}
    for name in ["none"] + sorted(x for x in rows if x != "none"):
        rs = [rows[name][k] for k in keys]
        sc, sn = [r["score_v3"] for r in rs], [r["score_v3"] for r in none]
        fin = [r for r in rs if not r["cap_hit"]]
        gained = [r for r, n in zip(rs, none) if r["score_v3"] and not n["score_v3"]]
        lost = [r for r, n in zip(rs, none) if n["score_v3"] and not r["score_v3"]]
        both = [(r, n) for r, n in zip(rs, none) if not r["cap_hit"] and not n["cap_hit"]]
        e = {**ST.parse_arm(name), "n": len(rs), "right_v3": int(sum(sc)), "percent_v3": 100 * float(np.mean(sc)), "cap_hits": sum(r["cap_hit"] for r in rs),
             "loop_A": sum(r["loop_A"] for r in rs), "no_answer_found": sum(r["mode_v3"] == "none" for r in rs),
             "finished_without_answer": sum(r["mode_v3"] == "none" and not r["cap_hit"] for r in rs),
             "word_salad_tails": sum(word_salad(r["text"]) for r in rs), "mean_token_logprob": float(np.mean([r["mean_logprob"] for r in rs])),
             "tokens_mean": float(np.mean([r["n_new"] for r in rs])), "tokens_median": float(np.median([r["n_new"] for r in rs])),
             "hold_words_per_1k_tokens": rate(rs), "hold_words_per_answer_mean": float(np.mean([r["hold_words"] for r in rs])),
             "hold_rate_ratio_to_none": rate(rs) / rate(none),
             "hold_words_per_1k_tokens_right": rate([r for r in rs if r["score_v3"]]) if sum(sc) else None,
             "hold_words_per_1k_tokens_wrong": rate([r for r in rs if not r["score_v3"]]) if sum(sc) < len(sc) else None,
             "minus_none": boot_diff(sc, sn), "gained": len(gained), "lost": len(lost),
             "gained_by_subject": dict(collections.Counter(subject(r) for r in gained)), "lost_by_subject": dict(collections.Counter(subject(r) for r in lost)),
             "lost_that_hit_cap": sum(r["cap_hit"] for r in lost), "identical_to_none": sum(r["text"] == n["text"] for r, n in zip(rs, none)),
             "tokens_mean_both_finished": [float(np.mean([r["n_new"] for r, _ in both])), float(np.mean([n["n_new"] for _, n in both]))] if both else None,
             "n_both_finished": len(both)}
        div = [d for d in (first_divergence(r["text"], n["text"]) for r, n in zip(rs, none)) if d is not None]
        e["first_divergence"] = {"n": len(div), "median_char": float(np.median([d[0] for d in div])) if div else None,
                                 "first_word_is_hold_on": sum(d[1] for d in div)}
        if stored_mean is not None:
            e["minus_stored_mean"] = boot_diff(sc, stored_mean)
        if group is not None:
            e["gained_by_group"] = dict(collections.Counter(group[r["problem_index"]] for r in gained))
            e["lost_by_group"] = dict(collections.Counter(group[r["problem_index"]] for r in lost))
            e["right_by_group"] = {g: [int(sum(r["score_v3"] for r in rs if group[r["problem_index"]] == g)), sum(group[r["problem_index"]] == g for r in rs)]
                                   for g in sorted(set(group.values()))}
        if t1 is not None:
            e["identical_to_stored_T1"] = sum(r["sample"] == 0 and r["text"] == t1[r["problem_index"]]["text"] for r in rs)
        arms[name] = e
        pick = lambda cand: min(cand, key=lambda r: r["n_new"]) if cand else None
        keep = lambda r: None if r is None else {k: r[k] for k in ("arm", "problem_index", "unique_id", "seed", "prompt_n_tokens", "text", "gold", "extracted_v3",
                                                                    "mode_v3", "score_v3", "n_new", "cap_hit", "hold_words")}
        examples[name] = {"right": keep(pick([r for r in rs if r["score_v3"]])), "wrong": keep(pick([r for r in fin if not r["score_v3"]]))}

    # the strength rule of the spec: where the hold-on rate ratio crosses the target, per steering site and for the bias arms
    series = collections.defaultdict(list)
    for name, e in arms.items():
        if e["kind"] == "steer":
            series[f"steer:{e['dir']}:L{e['layer']}"].append((e["alpha"], e["hold_rate_ratio_to_none"]))
        elif e["kind"] == "bias":
            series[f"bias:{e['family']}"].append((e["nats"], e["hold_rate_ratio_to_none"]))
    dose = {k: {"points": sorted(v), "strength_at_target": interpolate(sorted(v), a.target)} for k, v in series.items()}
    json.dump({"jobs": jobs, "n_problems": len({k[0] for k in keys}), "n_rows_per_arm": len(keys), "target_ratio": a.target, "arms": arms, "dose": dose,
               "stored_unsteered": stored}, open(out / "metrics.json", "w"), indent=1)
    json.dump(examples, open(out / "examples.json", "w"), indent=1)
    for name, e in arms.items():
        print(f"{name:26s} {e['right_v3']:3d}/{e['n']} cap {e['cap_hits']:3d} loop {e['loop_A']:3d} tok {e['tokens_mean']:7.0f} hold/1k {e['hold_words_per_1k_tokens']:6.2f} "
              f"x{e['hold_rate_ratio_to_none']:.2f} diff {e['minus_none']['points']:+5.1f} [{e['minus_none']['ci95'][0]:+.1f}, {e['minus_none']['ci95'][1]:+.1f}] "
              f"+{e['gained']} -{e['lost']} same {e['identical_to_none']} noans {e['finished_without_answer']} salad {e['word_salad_tails']}")
    print(json.dumps({k: v["strength_at_target"] for k, v in dose.items()}))


if __name__ == "__main__":
    main()
