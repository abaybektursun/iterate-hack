"""xreward lengths readout: answer lengths, budget curves and two-pass cascades from the stored rows of the rank-8 edit cells
(analysis/xreward_edits.py), 328 harder problems, cue, T 1.0 / top-p 1.0, grader v3. No new generation.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.xreward_lengths

Run from the repository root. Inputs (not committed): runs/<job-id>/answers.jsonl of every cell in CELLS (`uv run tools/gpu.py get`).
Writes results/xreward/lengths-01/readout.json; fails if the folder exists.

1. Lengths: quantiles of n_generated over finished answers (no cap hit), the same paired on problems that the base and the cell
   both finish with the median paired ratio, and the position of the first \\boxed as a fraction of the answer's characters.
2. Budget curve: right(C) = problems with score_v3 == 1 and n_generated <= C; tokens spent = mean of min(n_generated, C).
3. Cascade A -> B at C: a problem that A finishes within C tokens keeps A's answer; every other problem takes B's stored answer
   in full (tokens = C + B's n_generated, so B keeps its own 16,384 cap).

Prediction, written before the numbers: the paired median length moves under 10 % while the 90th percentile falls; the cascade
top64 -> top8x2 scores 205 to 210. Refuted if all quantiles shrink in proportion or the cascade is under 200. Boring if the
rand8 restart does as well as the top8x2 restart.

Caveat: seeds are per problem, so truncating a stored run at C equals a run with cap C only up to sampling determinism. Treat
every number at C < 16,384 as an estimate. rl_cue_T1 was sampled with seed base 50,000,000, the other cells with 3,000,000.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

from studies.rlneurons.analysis.day1_hard328 import rows_by_index, score
from studies.rlneurons.analysis.day1_wdiff import diff
from studies.rlneurons.analysis.day1_wdiff328 import clean_set
from studies.rlneurons.analysis.xreward_edits import NEW, REFS

STUDY = pathlib.Path(__file__).resolve().parents[1]
RUNS = pathlib.Path("runs")
OUT = STUDY / "results" / "xreward" / "lengths-01"
CELLS = ["base_cue_T1", "rand8_math31", "top1_math31", "top8_math31", "top64_math31", "top8x2_math31", "bulk_math31", "rbulk_math31",
         "rl_plain_T1", "rl_cue_T1"]
BASE, RL, CAP = "base_cue_T1", "rl_plain_T1", 16384
GRID = [2000, 4000, 6000, 8000, 10000, 12000, 14000, CAP]
FIRST, SECOND = ["base_cue_T1", "top8_math31", "top64_math31"], ["top8x2_math31", "rand8_math31", "rl_cue_T1"]
KNOWN = {"base_cue_T1": 164, "top8_math31": 192, "top64_math31": 200, "top8x2_math31": 190, "rl_plain_T1": 206}   # README, xreward


def quantiles(x):
    return {f"p{q}": round(float(v), 3) for q, v in zip((10, 25, 50, 75, 90), np.percentile(x, (10, 25, 50, 75, 90)))}


def main():
    assert not OUT.exists(), f"{OUT} exists: a rerun gets the next number"
    clean, gold, _ = clean_set()
    rows = {a: rows_by_index(RUNS / (REFS[a] if a in REFS else NEW[a][0]) / "answers.jsonl", clean) for a in CELLS}
    sc = {a: score(rows[a], gold) for a in CELLS}                      # rescoring with grader v3 asserts the stored score_v3
    n = {a: {i: rows[a][i]["n_generated"] for i in clean} for a in CELLS}
    done = {a: [i for i in clean if not rows[a][i]["cap_hit"]] for a in CELLS}
    for a in CELLS:
        assert all(rows[a][i]["max_tokens"] == CAP and n[a][i] <= CAP for i in clean), a

    lengths = {}
    for a in CELLS:
        both = [i for i in done[a] if not rows[BASE][i]["cap_hit"]]
        boxed = [rows[a][i]["text"].find("\\boxed") / len(rows[a][i]["text"]) for i in done[a] if "\\boxed" in rows[a][i]["text"]]
        lengths[a] = {"finished": len(done[a]), "tokens": quantiles([n[a][i] for i in done[a]]),
                      "paired_with_base": {"n": len(both), "base": quantiles([n[BASE][i] for i in both]), "cell": quantiles([n[a][i] for i in both]),
                                           "median_ratio_cell_over_base": round(float(np.median([n[a][i] / n[BASE][i] for i in both])), 3)},
                      "first_boxed": {"finished_with_boxed": len(boxed), "position_fraction_of_chars": quantiles(boxed)}}

    budget = {a: {str(C): {"right": sum(sc[a][i]["v3"] == 1 and n[a][i] <= C for i in clean),
                           "mean_tokens": round(float(np.mean([min(n[a][i], C) for i in clean])), 1)} for C in GRID} for a in CELLS}
    for a, want in KNOWN.items():
        assert budget[a][str(CAP)]["right"] == want, (a, budget[a][str(CAP)]["right"], want)

    cascade, examples = {}, []
    for A in FIRST:
        for B in SECOND:
            for C in GRID:
                keep = {i: not rows[A][i]["cap_hit"] and n[A][i] <= C for i in clean}
                v = {"casc": {i: {"v3": sc[A if keep[i] else B][i]["v3"]} for i in clean}, RL: sc[RL]}
                cascade[f"{A} -> {B} at {C}"] = {
                    "right": sum(s["v3"] for s in v["casc"].values()), "second_pass_problems": sum(not k for k in keep.values()),
                    "mean_tokens": round(float(np.mean([n[A][i] if keep[i] else C + n[B][i] for i in clean])), 1),
                    "minus_rl_plain_T1": diff(v, "casc", RL, clean)}
    A, B = "top64_math31", "top8x2_math31"
    for i in [i for i in clean if rows[A][i]["cap_hit"] and sc[A][i]["v3"] == 0 and sc[B][i]["v3"] == 1][:2]:
        examples.append({"problem_index": i, "gold": gold[i], "first_pass": A, "first_pass_tokens": n[A][i], "first_pass_tail": rows[A][i]["text"][-600:],
                         "second_pass": B, "second_pass_tokens": n[B][i], "second_pass_extracted_v3": sc[B][i]["extracted_v3"],
                         "second_pass_tail": rows[B][i]["text"][-1200:]})
    wrong = next(i for i in clean if rows[A][i]["cap_hit"] and sc[B][i]["v3"] == 0 and not rows[B][i]["cap_hit"])
    examples.append({"problem_index": wrong, "gold": gold[wrong], "first_pass": A, "second_pass": B, "second_pass_tokens": n[B][wrong], "score_v3": 0,
                     "second_pass_extracted_v3": sc[B][wrong]["extracted_v3"], "second_pass_tail": rows[B][wrong]["text"][-1200:]})

    OUT.mkdir(parents=True)
    (OUT / "readout.json").write_text(json.dumps({
        "n": len(clean), "grader": "v3", "cap": CAP, "jobs": {a: REFS[a] if a in REFS else NEW[a][0] for a in CELLS},
        "caveat": "stored runs truncated at C, not runs with cap C; rl_cue_T1 has seed base 50,000,000, the others 3,000,000",
        "lengths": lengths, "budget_curves": budget, "cascade": cascade, "bootstrap": "paired, 5,000 resamples, seed 0, 95 % percentile",
        "examples_cascade_top64_then_top8x2": examples}, indent=1) + "\n")

    for a in CELLS:
        L = lengths[a]
        print(f"{a:>14} finished {L['finished']:>3} tokens {list(L['tokens'].values())} | paired n {L['paired_with_base']['n']} base {list(L['paired_with_base']['base'].values())} "
              f"cell {list(L['paired_with_base']['cell'].values())} ratio {L['paired_with_base']['median_ratio_cell_over_base']} | boxed at {list(L['first_boxed']['position_fraction_of_chars'].values())}")
    for a in CELLS:
        print(f"{a:>14} " + "  ".join(f"{C}: {b['right']} / {b['mean_tokens']:.0f}" for C, b in budget[a].items()))
    for k, c in cascade.items():
        print(f"{k:>45}  right {c['right']}  second pass {c['second_pass_problems']:>3}  tokens {c['mean_tokens']:.0f}  minus RL {c['minus_rl_plain_T1']}")


if __name__ == "__main__":
    main()
