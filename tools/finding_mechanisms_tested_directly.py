"""The theory engine's mechanisms, each checked directly on stored data before it may forecast: 6 of 17 hold in round 13.

The page of one finding, served at /finding/mechanisms-tested-directly (view.py serves every tools/finding_<slug>.py)
and reached from its tile on /findings, which ICON draws. It is the third page about the team's theory engine
(.claude/skills/theory/SKILL.md, studies/theory/README.md): tools/finding_theories_on_trial.py scores theories on their
predictions of numbers computed from stored rows, tools/finding_forecasts_before_results.py scores them on numbers that
running jobs had not reported yet, and this page shows the explanations tested directly. A mechanism is a one-sentence
cause proposed to explain the results; a direct test is a check of that cause on answers and weights already stored,
with the passing threshold fixed before looking. From engine 13 on only a mechanism that holds its direct test
forecasts.

The picture is one lit plate. Every mechanism with a direct test in the record (studies/theory/results/
direct_tested.json and refuted.json) is one dot with a short plain label (TESTS). Round 13's 17 are full size; the 8
tested outside round 13 are small. The one control has three states: Proposed (the dots together, before testing),
Tested (they travel into Hold, Refuted and Undecided, the counts counting with them) and By family (grouped by the
engine's six families of causes, so the reader sees which kinds of explanation hold). A click on a dot shows its claim in
the record's own words, the test, the measured number against the threshold, and the board item. Address:
/finding/mechanisms-tested-directly#<proposed|family, or nothing for Tested>/<panel or mechanism id with ":" for "/">.
The rules are in .claude/skills/finding-page/SKILL.md; the looks are those of tools/architecture.py
(.claude/skills/site-ui/SKILL.md).

    uv run tools/finding_mechanisms_tested_directly.py           checks ROWS and COMMIT against the record files
    uv run tools/finding_mechanisms_tested_directly.py --write   rewrites ROWS and COMMIT from them

A new direct test: once its row is in direct_tested.json or refuted.json on main, add the mechanism to TESTS (a label of
at most 6 words, its test folder, the deciding number's keys in that folder's readout, the rule in plain words, and a
family when the engine's files name none), run --write, then the check. Both modes run git and tools/board.py (the time
each result was posted: the record's own times mix UTC and local time). The deployed site ships only tools/*.py, so the
page reads nothing from studies/ at run time: ROWS is the copy.
"""
import glob
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

R = "studies/theory/results/"
FILES = [R + "direct_tested.json", R + "refuted.json", R + "wide/round-13/direct_tests.json"]

TITLE = "Mechanisms tested directly"  # the name on its tile on /findings and in the browser tab
PROBLEM = "Do our agents' proposed causes survive a direct check on stored data?"

DATA = {
    "sources": {
        "record": R + "direct_tested.json (holds, refuted, undecided) and " + R + "refuted.json (refuted)",
        "round 13": R + "wide/round-13/direct_tests.json (the 17 plans: 5 carried, 12 rivals), direct_tests.md, "
                    "forecasts.json; studies/theory/README.md, section Round 13",
        "tests": R + "direct/<test>/readout.json (the deciding number of each test); specs: studies/theory/specs/SPEC_direct_*.md",
        "families": R + "wide/*/standing.json and mechanisms.json, forecast/*/mechanisms.json (the six families of "
                    "studies/theory/lib/forecast.py, LENSES)",
        "times": "tools/board.py: when each test's result was posted (a work item: when it was closed)",
        "labels": "TESTS below, written for this page",
    },
}

# The six families of causes of studies/theory/lib/forecast.py (LENSES), in the order of the picture, with a plain gloss.
FAMILIES = [
    ["weights", "Weights", "the RL weight change"],
    ["sampling", "Sampling", "temperature, votes"],
    ["stopping", "Stopping", "cut off, answer format"],
    ["training", "Training", "what training put in"],
    ["grader", "Grader", "the measurement itself"],
    ["problems", "Problems", "difficulty, solution length"],
]

# One entry per mechanism with a direct test, written for this page from the test's readout, spec and README section:
#   [label (at most 6 words), test folder under results/direct/ or "", family when the engine's files name none or "",
#    gauge or None, the rule in plain words, a caveat or ""]
#   gauge: [file in the folder, key path of the deciding number, key path of its interval or "" (a path that ends in a
#           [value, [low, high]] or [value, low, high] list needs none), scale, threshold, the side where the claim
#           survives ("above" or "below"), what the number is, unit, interval level]
TESTS = {
    "round-10/weights-m03": [
        "Think-SFT shares RL's input directions", "host-01", "",
        ["readout.json", "T.by_matrix.value", "T.by_matrix.ci90", 1, 2.0, "above",
         "Think-SFT's weight change inside RL-Math's top-8 input directions, over chance", "times chance", "90 %"],
        "Refuted if the interval's upper end is below 2 times chance; holds if its lower end is 2 or more. To be "
        "distinctive it also needed 1.5 times every structured null.",
        "Holds, not distinctive: only 1.33 times the base matrix's own top-8 directions (1.5 needed), and Think-SFT "
        "sits almost as much in Code-RL's and Math 3.0's directions."],
    "round-09/grader-m01": [
        "Cue adds nothing at RL step 100", "cue100-01", "",
        ["readout.json", "deciding.D_per_500", "deciding.ci95", 1, 0, "below",
         "cue minus plain at RL step 100, MATH-500", "problems of 500", "95 %"],
        "Refuted if the whole 95 % interval of the difference lies above 0 and a label permutation gives p below 0.05.",
        "Refuted only just: 2.5 % of the bootstrap differences are at or below 0."],
    "run-08/f2-m06": [
        "A cut-off answer casts no vote", "abstain-01", "",
        ["readout.json", "sft_cue.D", "", 1, 2, "above",
         "problems the 4-sample vote had right that letting cut-off answers finish turns wrong, Think-SFT + cue",
         "problems of 328", ""],
        "The claim needs 2 or more such problems. Refuted below 2.", ""],
    "round-09/training-m01": [
        "Template moves answers, not drift", "template-01", "",
        ["readout.json", "deciding.D_native_minus_cue32_drifted_pts.point", "deciding.D_native_minus_cue32_drifted_pts.ci95",
         1, -2.0, "above", "drift, Think-SFT's own template minus the raw template with the cue", "points", "95 %"],
        "Refuted if the difference is −2 points or less, its 95 % upper end is below 0 and it is larger than the "
        "scatter between seeds (2.7 points).",
        "Weak hold: one sample per template, and the interval allows a 7-point drop."],
    "round-10/weights-m06": [
        "Direction 1 adds only finishes", "rank1-01", "",
        ["readout.json", "primary.top1.E_pts", "primary.top1.E_ci95", 1, 5.0, "below",
         "extra right answers of the rank-1 edit over a second base sample, on base finished-wrong problems", "points",
         "95 %"],
        "Refuted if the 95 % lower end is +5 points or more, or if directions 2 to 8 do not beat direction 1. Holds "
        "only if the rank-1 gain is below half the gain of directions 2 to 8.",
        "Undecided: no refuting threshold met, but the rank-1 gain (+7.2) is not below half of the +9.3 of "
        "directions 2 to 8."],
    "run-08/f2-m02": [
        "Grader credits boxes before the cut", "capbox-01", "",
        ["readout.json", "primary_attempt0.per_model.rl_plain.share", "primary_attempt0.per_model.rl_plain.wilson95",
         100, 10, "above", "RL's answers cut off at 16,384 tokens that the grader still credits", "%", "95 %"],
        "Holds if the share is 10 % or more and above Think-SFT's; refuted if the 95 % upper end is below 10 %.",
        "Undecided: the share is 6.1 %, but its interval, 3.0 to 12.1 %, still reaches 10 %."],
    "round-13/s4-a": [
        "Code directions add right programs", "codepass-01", "weights",
        ["readout.json", "ratio_dM_over_dC", "ratio_90", 1, 0.5, "below",
         "Math's gain in pass rate of finished programs over Code's gain", "ratio", "90 %"],
        "Holds if Code's top-8 directions raise the pass rate by 3 points or more over a random edit (measured +7.0) "
        "and Math's gain is below half of Code's, on point estimates.",
        "Holds on point estimates only: the ratio's interval, −0.46 to 0.62, contains the 0.54 of its rival s4-b."],
    "round-13/s4-b": [
        "Edit sharpens the base's own programs", "sharpen-01", "weights",
        ["readout.json", "D", "D_ci90", 1, -0.10, "above",
         "share of extra passes on problems the base solves under another prompt, edit minus random edit", "share",
         "90 %"],
        "Refuted if the difference is below −0.10.",
        "Only fails to refute: its rival s4-a does not forbid a difference near 0, so this test cannot tell the two "
        "apart."],
    "round-13/s3-a": [
        "Vote wins when wrong answers split", "votesplit-01", "sampling",
        ["readout.json", "S_a", "S_a_ci90", 1, 0.5, "above",
         "problems gained by the vote over 12 that are right in under half of the 12 samples", "share", "90 %"],
        "Refuted if the share is below 0.50, or if merging each problem's wrong answers into one value keeps 80 % of "
        "the gains.",
        "21 problems only, and the interval's lower end, 0.476, is below 0.50. 3 of the 14 win because most samples "
        "are cut off and cast no vote."],
    "round-13/s3-b": [
        "Ties pull the 4-sample vote down", "votetie-01", "sampling",
        ["readout.json", "S_b", "S_b_ci90", 1, 0.6, "above",
         "problems gained by the vote over 12 that were ties with the right answer at 4 samples", "share", "90 %"],
        "Refuted if the share is below 0.60, or less than 0.20 above the same share among problems the larger vote "
        "does not fix.", ""],
    "round-13/s1-a": [
        "4,096-token cap removes right answers", "karpcap-01", "stopping",
        ["readout.json", "L_prime", "L_prime_ci90", 1, 0.45, "above",
         "problems the agent's method loses whose right base answers are all longer than 4,096 tokens", "share", "90 %"],
        "Holds if the share is 0.45 or more and at least 0.20 above the same share on problems the method gets right "
        "(measured 0.173).",
        "Holds on a proxy: the method's own 12 samples per problem are not stored where the team can read them, so the "
        "test used the lengths of the cued base's answers. 42 problems."],
    "round-13/s1-b": [
        "Short wrong answers agree", "karpagree-01", "sampling",
        ["readout.json", "A_K_minus_A_B", "A_K_minus_A_B_ci90", 1, 0.10, "above",
         "how much more the method's wrong answer agrees with the base's wrong answers than they agree with each other",
         "share", "90 %"],
        "Holds if the agreement excess is 0.10 or more and the cap explains at most 35 % of the lost problems "
        "(measured 71 %).", ""],
    "round-13/s2-a": [
        "Code directions flip half the openings", "m21open-01", "weights",
        ["readout.json", "a.plan_rule.s_Q", "a.plan_rule.s_Q_ci90", 1, 0.40, "above",
         "quick wrong answers of the Code-RL edit that are answer-first replies", "share", "90 %"],
        "Refuted if the share is below 0.40.", ""],
    "round-13/s2-b": [
        "Code habit commits too early", "m21hard-01", "training",
        ["readout.json", "b.r_N_minus_r_Q", "b.ci90", 1, 0.10, "above",
         "how much easier the edit's quick wrong problems are than the plain base's, in base solve rate", "share",
         "90 %"],
        "Refuted if the difference in solve rate is below 0.10.", ""],
    "round-13/s6-a": [
        "Code edit repairs answer format", "codecontract-01", "stopping",
        ["readout.json", "S_top8", "S_top8_90", 1, 0.5, "above",
         "share of the edit's code fixes that are format failures (cut off, no block, no function)", "share", "90 %"],
        "Holds if the share is 0.50 or more, above a random edit's, and format failures are fixed twice as often as "
        "logic failures.", ""],
    "round-13/s6-b": [
        "Code gap is per-sample slips", "codereliab-01", "sampling",
        ["readout.json", "top8_Q", "top8_Q_90", 1, 0.6, "above",
         "share of the edit's code fixes that a base-like cell passes in another sample", "share", "90 %"],
        "Holds if the share is 0.60 or more and its lower end is more than 0.10 above the share among all base "
        "failures (0.48).",
        "The random cell shares seed and prompt with the edit; with the Math-cue cell alone the share is 0.56, below "
        "the plan's 0.60."],
    "round-13/s5-a": [
        "Cap and time budget set ceiling", "devcut-01", "stopping", None,
        "Refuted if the agent's vote losses on its 100 development problems are not mostly samples cut at 4,096 "
        "tokens or never run (D below 0.15).",
        "Not computed: the agent's per-sample rows are in a Modal Volume the team cannot read."],
    "round-13/s5-b": [
        "Plain wrong answers share one value", "devmode-01", "sampling", None,
        "Refuted if the plain prompt's wrong answers share one value less than 1.3 times as often as the cued base's.",
        "Not computed: the agent's per-sample rows are in a Modal Volume the team cannot read."],
    "r5-m03-rival": [
        "Edit is an incomplete switch", "", "weights", None,
        "The mechanism predicted that the edit's short answers are about 50 % right.", ""],
    "run-05/f2-m06": [
        "bf16 merge under-applies the edit", "", "", None,
        "The mechanism predicted that the written 1x change is smaller than the intended one.", ""],
    "run-06/f2-m03": [
        "Gradable reward concentrates the change", "reward-01", "",
        ["readout.json", "P.point", "P.ci90", 1, 0.5, "below",
         "where General-RL's concentration sits between Think-SFT (0) and RL with a gradable answer (1)", "fraction",
         "90 %"],
        "Refuted if the interval's lower end is 0.5 or more.",
        "The rule was fixed after the summary means had been seen."],
    "run-05/f2-m01": [
        "Edit only finishes, adds no skill", "dial-01", "",
        ["readout.json", "hard328.groups.FW.D_edit_minus_base2_pts", "", 1, 0, "below",
         "extra right answers of the top-8 edit over a second base sample, on base finished-wrong problems",
         "points", "90 %"],
        "Refuted if the 90 % interval lies above 0 on the 328 harder problems: the edit adds right answers, not only "
        "finishes.", ""],
    "run-02/f2-m01": [
        "Votes are bought with short answers", "short-01", "problems",
        ["readout.json", "P1_hard328_S2000.value", "P1_hard328_S2000.interval", 100, 20, "below",
         "solved harder problems with a right answer of 2,000 tokens or fewer", "%", "90 %"],
        "Refuted if the interval's lower end is 20 % or more.", ""],
    "run-03/f2-m04": [
        "Math edit swaps code for boxes", "ending-01", "",
        ["readout.json", "differences_fnb.math15-rand15", "", 1, 8, "above",
         "finished code answers with no code block, Math edit minus random edit", "answers of 538", "90 %"],
        "Refuted if the interval's upper end is below +8.", ""],
    "run-05/f2-m03": [
        "Directions act as text drives them", "drive-01", "",
        ["metrics.json", "R_math.value", "R_math.90", 1, 0.85, "below",
         "how strongly code text drives Math's top-8 directions, over math text", "ratio", "90 %"],
        "Refuted above 0.85; the mechanism predicted about 0.54.", ""],
}

# Written by --write from the record files, one mechanism per line in the order the results were posted:
#   [id, verdict, kind in round 13 ("carried", "rival" or "" for a test outside round 13), family, "file" or "page"
#    (who named the family), posted (UTC), board item, claim, measured (both as the record holds them), test folder,
#    gauge [value, low, high] or None]
ROWS = [
    ['r5-m03-rival', 'refuted', '', 'weights', 'page', '2026-11-15T17:56:01', 'result-d02d46', 'the top-8 edit is an incomplete switch per sample: short answers are the unswitched base and about 50 % right', 'short answers 82.9 % right (predicted about 50 %), share 17.8 % (predicted 10-15 %)', '', None],
    ['run-05/f2-m06', 'refuted', '', 'weights', 'file', '2026-11-15T20:57:44', 'result-c2edfb', 'weight edits merged in bf16 are under-applied: small changes below half a unit in the last place are lost, so 1x lands smaller than intended', 'projection of the written 1x change on the intended addition 0.99996 (1.5x: 0.99998)', '', None],
    ['run-06/f2-m03', 'refuted', '', 'training', 'file', '2026-11-15T21:06:46', 'result-82eb02', 'an outcome reward pays only for a gradable final answer, so its gradient piles into a few singular directions; the rest of the update is diffuse', 'RL-Zero-General (LM-judge reward, no gradable answer) top-8 share 0.127 vs Math 3.0 0.135, Think-SFT 0.030: P = 0.685 [0.609, 0.765] (refuted if lower bound >= 0.5), n 224 matrices', 'reward-01', [0.6851, 0.6093, 0.7654]],
    ['run-05/f2-m01', 'refuted', '', 'weights', 'file', '2026-11-15T21:09:10', 'result-124593', 'the top-8 RL-Math directions are a signed termination dial: they add finished answers, not right answers on problems the base already finishes', "hard328, edit 1.5x on problems where a cued-base sample finished wrong: 36.4 % right vs 22.9 % for a second base sample, +13.5 points [9.7, 17.3] (RL +12.3); only 26 % of the edit's gain sits on base cap hits; at -1x finished answers 51.5 % vs base 70.0 % right", 'dial-01', [13.468, 9.7397, 17.3333]],
    ['run-02/f2-m01', 'refuted', '', 'problems', 'page', '2026-11-15T21:18:06', 'result-ebf7a4', 'hard328 solutions need 6,000-14,000 tokens and short samples never reach them: under 20 % of the hard328 problems the cued base solves have a right sample of 2,000 tokens or fewer', 'hard328: 72 of 220 solved problems, 32.7 % [27.7, 38.2] (refuted if lower bound >= 20 %); median right length 3,921 tokens [3,541, 4,390]; MATH-500 control 67.5 % [63.9, 71.1] of 474', 'short-01', [32.73, 27.73, 38.18]],
    ['run-03/f2-m04', 'refuted', '', 'stopping', 'file', '2026-11-15T21:19:27', 'result-6e4536', "on code, the RL-Math edit at 1x to 1.5x adds at least 8 finished answers with no code block, because Math's directions push a boxed ending that displaces the final python block", 'HumanEval+/MBPP+ 538, edit 1.5x: finished no-block 6 vs random rank-8 1.5x 23, -17 [-26, -8] (refuted if upper end < +8); vs cued base 12, -6 [-13, 1]; 0 of 538 answers hold \\boxed; no Math-alone 1x code cell', 'ending-01', [-17, -26.0, -8.0]],
    ['round-10/weights-m03', 'holds', '', 'weights', 'file', '2026-11-15T21:19:47', 'result-3abd6f', "Think-SFT's own weight change lies along RL-Math 3.1's top-8 input directions at least 2x more than a random rank-8 subspace (sharpened: and 1.5x more than the top-8 input subspaces of IF-RL, General-RL and the base matrix)", "share of Think-SFT's change in Math 3.1's top-8 input subspace 4.80x chance [4.55, 5.08], n 224 matrices; over IF 2.23x [2.12, 2.34], General 1.99x [1.89, 2.08], base matrix 1.33x [1.28, 1.39]: holds, not distinctive (shared with Code 3.1 and Math 3.0, and predicted by run-05/f2-m03 too)", 'host-01', [4.8044, 4.5521, 5.082]],
    ['round-09/grader-m01', 'refuted', 'carried', 'grader', 'file', '2026-11-15T21:40:52', 'result-6ecd35', 'At RL step 100 the cue adds nothing beyond seed scatter on MATH-500: pooled paired cue-minus-plain difference is zero', 'D +8.5 problems/500, 95% [+0.24, +16.75], 90% [+1.25, +15.5], n 500 problems x 4 samples per arm; permutation p 0.044 (null |D| 95th pct 8.0); seed-folder null +0.7/+1.3', 'cue100-01', [8.5, 0.2438, 16.75]],
    ['run-08/f2-m06', 'refuted', 'carried', 'grader', 'file', '2026-11-15T21:43:25', 'result-3605ba', "On hard328, letting Think-SFT's 16,384 cap hits finish (cap-32k row) as the 4th vote flips >=2 vote-right problems wrong, vote gain < half of the 23 single gain, and VB < abstention null VA'", "D = 0 of 328 (threshold 2); (VB-VA)/G1 = 0.22, 95 % [0.05, 0.40]; VB 245 = abstention null VA' 245 (VA 240)", 'abstain-01', [0, None, None]],
    ['round-10/weights-m06', 'undecided', 'carried', 'weights', 'file', '2026-11-15T21:43:44', 'result-efc74d', 'On hard328 base-finished-wrong problems the rank-1 edit is right no more often than a second base sample, while directions 2-8 at 1.5x are right clearly more often', 'undecided by the frozen rule (does not hold): E_top1 +7.2 pts 95% [0.7, 13.6], E_d28 +9.3 [3.0, 15.8], G +2.1 [-6.1, 10.5], n 190 pairs / 139 problems; second base sample 21.8% right, random rank-8 +0.4', 'rank1-01', [7.193, 0.6597, 13.5804]],
    ['round-09/training-m01', 'holds', 'carried', 'training', 'file', '2026-11-15T21:44:15', 'result-ab26c4', "Think-SFT's own ChatML <think> template does not make it drift less on hard328 (first 16,384 tokens): drifted share equals raw template + cue within raw-cue seed scatter", 'D = -1.8 pts (57 vs 63 of 328), 95% [-7.3, +3.7], 90% [-6.4, +2.7], n 328; null S_max 2.7 pts over 4 raw-cue samples', 'template-01', [-1.8293, -7.3171, 3.6585]],
    ['run-08/f2-m02', 'undecided', 'carried', 'grader', 'file', '2026-11-15T21:44:44', 'result-a9b0bc', "in native 16,384-cap hard328 runs grader v3 credits a right answer to at least 10 % of RL plain's cap-hit rows, more than Think-SFT's share", 'undecided by the frozen rule (does not hold): RL C/H 0.061 (7/114), Wilson 95 % [0.030, 0.121]; Think-SFT 0.037 (14/378); RL - Think-SFT +2.4 pts 95 % [-2.4, 8.1]; with restart rows 9/171, Wilson upper 0.097', 'capbox-01', [6.1404, 3.0059, 12.1343]],
    ['round-13/s4-a', 'holds', 'rival', 'weights', 'page', '2026-11-15T21:56:15', 'result-d15c5e', "Code's 1.5x top-8 directions raise the pass rate among finished-with-block code answers above random 1.5x by at least 3 pts; Math's 1.5x directions raise it by less than half that", 'dC +7.0 pts [3.7, 10.3], dM +1.5 [-2.2, 5.1], dM/dC 0.21 [-0.46, 0.62], 90 % bootstrap, n 538; null random 67.8 % (331/488), rival b ratio 0.54 not excluded (point-only hold)', 'codepass-01', [0.2098, -0.4589, 0.6172]],
    ['round-13/s4-b', 'holds', 'rival', 'weights', 'page', '2026-11-15T21:56:19', 'result-63cacd', "Code 1.5x extra passes over the cued base fall in the base's plain-or-Math-cue solved set as often as a random rank-8 1.5x edit's extra passes", 'D = f_E - f_R = +0.055, 90% [-0.029, 0.139] (refuted if < -0.10), n 538 (113 and 63 extra passes); null random f_R 0.635, f_E 0.690; base-failure floor 0.43; |U| 378', 'sharpen-01', [0.0553, -0.0285, 0.1391]],
    ['round-13/s3-a', 'holds', 'rival', 'sampling', 'page', '2026-11-15T21:56:51', 'result-4c9189', 'Most problems the vote over 12 gains over the vote over samples 0-3 have the right answer in under half of the 12 samples (wrong answers split)', 'S_a 0.667 [0.476, 0.810] 90%, n=21 gained problems (MATH-500, cued base); merged-wrong null keeps 8/21 = 0.381 of G (refuted if >= 0.80); without 3 cap-hit-driven wins 11/21 = 0.524', 'votesplit-01', [0.667, 0.476, 0.81]],
    ['round-13/s3-b', 'refuted', 'rival', 'sampling', 'page', '2026-11-15T21:56:51', 'result-4c9189', 'Most gained problems were ties at k=4 with the right answer in a tied top group and right in at least half of 12', 'S_b 0.095 [0.000, 0.190] 90%, n=21 (refuted if < 0.60); null (unfixed k=4 failures with a right sample) 0.143, n=7; diff -0.048 [-0.286, 0.143]', 'votetie-01', [0.095, 0.0, 0.19]],
    ['round-13/s1-a', 'holds', 'rival', 'stopping', 'page', '2026-11-15T21:58:02', 'result-4b64da', 'On hard328 problems the Karpathy method (plain, T 0.6, 12 votes, cap 4,096) loses while the cued base solves them (k>=2/4), every right base route is longer than the 4,096 cap far more often than on matched won problems (proxy for the 12-sample cap-hit share, which is not stored)', "L' 0.714 [0.595, 0.833] n=42 lost problems vs null N' 0.173 [0.120, 0.226] n=133 matched won problems; L'-N' 0.541 [0.414, 0.665] 90%", 'karpcap-01', [0.7143, 0.5952, 0.8333]],
    ['round-13/s1-b', 'refuted', 'rival', 'sampling', 'page', '2026-11-15T21:58:02', 'result-4b64da', 'Those hard328 losses come from agreeing short finished wrong answers with few cap hits', "C' 0.714 [0.595, 0.833] > 0.35; A_K-A_B 0.064 [-0.130, 0.236] < 0.10, n=42 (39 vs 12 pairs); null cued-base wrong-answer agreement 0.167", 'karpagree-01', [0.0641, -0.1296, 0.2361]],
    ['round-13/s2-a', 'refuted', 'rival', 'weights', 'page', '2026-11-15T21:58:23', 'result-cc7288', "m21's quick wrong answers are plain-base answer-first replies (s_Q >= 0.40 and >= s_N - 0.15)", 's_Q 0.25 [0.17, 0.35] n 60 (floor 0.40); null plain base s_N 0.21 n 105; gap 0.04 [-0.07, 0.15]', 'm21open-01', [0.25, 0.1667, 0.35]],
    ['round-13/s2-b', 'refuted', 'rival', 'training', 'page', '2026-11-15T21:58:23', 'result-cc7288', "m21's quick wrong answers sit on harder problems than the plain base's (r_N - r_Q >= 0.10)", 'r_N - r_Q 0.005 [-0.066, 0.075], n 60 vs 105; r_Q 0.833, r_N 0.838; all 250 0.814; m21 long wrong answers 0.40 (instrument can fail)', 'm21hard-01', [0.0048, -0.0655, 0.075]],
    ['round-13/s6-a', 'refuted', 'rival', 'stopping', 'page', '2026-11-15T22:00:13', 'result-04f363', 'Base code failures fixed by Code top-8 1x are enriched for answer-contract failures beyond random rank-8 fixes', 'S_top8 0.43 [0.35, 0.51] n 100 fixes (refuted below 0.50); S_top8-S_rand [-0.02, 0.15]; r_c/r_l 1.53 [1.21, 1.93] (needed 2.0); null random rank-8 1.5x S_rand 0.37 n 63', 'codecontract-01', [0.43, 0.3495, 0.5102]],
    ['round-13/s6-b', 'holds', 'rival', 'sampling', 'page', '2026-11-15T22:00:13', 'result-04f363', 'Base code failures fixed by Code top-8 1x are mostly problems the base passes in other stored base-like samples', 'Q_top8 0.75 [0.68, 0.82] n 100 fixes; Q_top8-Q_base [0.21, 0.33] 90%; null Q_base 0.48 (106/221); RL-Code fixes Q 0.74 n 116; Math-cue cell alone Q_top8 0.56 vs 0.35', 'codereliab-01', [0.75, 0.6774, 0.8198]],
    ['round-13/s5-a', 'undecided', 'rival', 'stopping', 'page', '2026-11-15T22:03:41', 'result-cfe997', "In the kept autobench method's dev100 runs, the vote-wrong problems are those whose samples were cut at 4,096 tokens or left unrun by the time budget, more than difficulty explains", "undecided, not computable: the kept method's per-sample dev100 rows are only in frustea's Modal Volume; instrument on cued-base rows cut at 4,096: D 0.73 [0.50, 0.91] n=14", 'devcut-01', None],
    ['round-13/s5-b', 'undecided', 'rival', 'sampling', 'page', '2026-11-15T22:03:41', 'result-cfe997', "The kept autobench method's vote-wrong dev100 problems are lost to one shared wrong value, more concentrated than the cued base's 12-sample votes", "undecided, not computable: per-sample dev100 rows only in frustea's Modal Volume; null ready: cued base G_cue 0.40 [0.34, 0.46] n=34 vote-wrong of 500, so the claim needs G_plain >= 0.52", 'devmode-01', None],
    ['run-05/f2-m03', 'refuted', '', 'weights', 'file', '2026-11-15T22:16:01', 'work-c51f89', "a direction of the RL change acts only as far as the text drives its input subspace, so Math 3.1's top-8 directions transfer to code (0.54 of Code's own effect) because code text drives them about half as much as math text", "drive of Math 3.1's top-8 input subspace on 538 base code answers over 328 math answers: 0.869 [0.861, 0.877]; random rank-8 control 0.990; normalized 0.878; reverse (Code dirs) 0.686 vs predicted 0.45-0.47", 'drive-01', [0.8688, 0.8607, 0.8772]],
]
COMMIT = '5125892'  # the last commit of the record files when ROWS was written


def _get(obj, path):  # a value by a dotted key path; a number in the path indexes a list
    for k in path.split("."):
        obj = obj[int(k)] if isinstance(obj, list) else obj[k]
    return obj


def _gauge(test, spec):
    """[value, low, high] of a test's deciding number, scaled, from its readout; None when the readout has none."""
    if not spec:
        return None
    f, pk, ik, scale = spec[:4]
    r = json.load(open(f"{R}direct/{test}/{f}"))
    v = _get(r, pk)
    if v is None:
        return None
    if isinstance(v, list):
        v, lo, hi = (v[0], *v[1]) if isinstance(v[1], list) else v
    else:
        lo, hi = _get(r, ik) if ik else (None, None)
    return [None if x is None else round(x * scale, 4) for x in (v, lo, hi)]


def _families():  # {mechanism id: family} where the engine's files name one of the six
    six, out = {f[0] for f in FAMILIES}, {}
    for p in sorted(glob.glob(R + "wide/*/standing.json") + glob.glob(R + "wide/*/mechanisms.json")
                    + glob.glob(R + "forecast/*/mechanisms.json")):
        stack = [json.load(open(p))]
        while stack:
            o = stack.pop()
            if isinstance(o, dict):
                if isinstance(o.get("id"), str) and o.get("family") in six:
                    assert out.setdefault(o["id"], o["family"]) == o["family"], (o["id"], p)
                stack.extend(o.values())
            elif isinstance(o, list):
                stack.extend(o)
    return out


def _posted(item):  # when a board item was posted (a work item: when it was closed), from board.py show
    out = subprocess.run(["uv", "run", "tools/board.py", "show", item], capture_output=True, text=True, check=True).stdout
    pat = r"closed by \S+ at (\S+)Z" if item.startswith("work-") else r" at (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)Z"
    return re.search(pat, out.splitlines()[0]).group(1)


def _build():
    tested, refuted = json.load(open(FILES[0])), json.load(open(FILES[1]))
    plans = {p["mechanism"]: p for p in json.load(open(FILES[2]))}
    ids = {x["mechanism"] for x in tested}
    rec = list(tested)
    for x in refuted:  # a refuted row that is also in direct_tested.json must say the same
        if x["mechanism"] in ids:
            t = next(y for y in tested if y["mechanism"] == x["mechanism"])
            assert t["verdict"] == "refuted" and t["result"] == x["result"], x["mechanism"]
        else:
            rec.append({**x, "verdict": "refuted"})
    assert len({x["mechanism"] for x in rec}) == len(rec), "a mechanism appears twice in the record"
    assert set(plans) <= {x["mechanism"] for x in rec}, "a round-13 plan has no row in the record"
    missing = sorted({x["mechanism"] for x in rec} - set(TESTS))
    assert not missing, f"add these mechanisms to TESTS: {missing}"
    items = sorted({x["result"] for x in rec})
    with ThreadPoolExecutor(8) as pool:
        times = dict(zip(items, pool.map(_posted, items)))
    fam, rows = _families(), []
    for x in rec:
        m, t = x["mechanism"], TESTS[x["mechanism"]]
        assert (m in fam) != bool(t[2]), f"{m}: the family must come from the files or from TESTS, not both"
        kind = "" if m not in plans else "carried" if plans[m]["kind"] == "carried" else "rival"
        when = times[x["result"]]
        assert x["verdict"] in ("holds", "refuted", "undecided"), m
        rows.append([m, x["verdict"], kind, fam.get(m) or t[2], "file" if m in fam else "page", when, x["result"],
                     x["claim"], x["measured"], t[1], _gauge(t[1], t[3])])
    rows.sort(key=lambda r: (r[5], r[0]))
    commit = subprocess.run(["git", "log", "-1", "--format=%h", "--", *FILES[:2]], capture_output=True, text=True,
                            check=True).stdout.strip()
    return rows, commit


def _tally(rows):
    """The headline counts, for the page and for the row on /findings: held, refuted, undecided and tested in round 13;
    the same over every mechanism in the record (*_all); and per family [held, tested] over the record."""
    r13 = [r for r in rows if r[2]]
    c = {"held": sum(r[1] == "holds" for r in r13), "refuted": sum(r[1] == "refuted" for r in r13),
         "undecided": sum(r[1] == "undecided" for r in r13), "tested": len(r13),
         "held_all": sum(r[1] == "holds" for r in rows), "refuted_all": sum(r[1] == "refuted" for r in rows),
         "undecided_all": sum(r[1] == "undecided" for r in rows), "tested_all": len(rows),
         "carried": sum(r[2] == "carried" for r in r13), "rivals": sum(r[2] == "rival" for r in r13),
         "family_from_files": sum(r[4] == "file" for r in rows),
         "families": {f[0]: [sum(r[3] == f[0] and r[1] == "holds" for r in rows), sum(r[3] == f[0] for r in rows)]
                      for f in FAMILIES}}
    assert c["held"] + c["refuted"] + c["undecided"] == c["tested"]
    return c


COUNTS = _tally(ROWS) if ROWS else {}
_c = COUNTS or {k: 0 for k in ("held", "refuted", "undecided", "tested", "held_all", "refuted_all", "undecided_all",
                                "tested_all", "carried", "rivals", "family_from_files")} | {"families": {}}
LINE = (f"Of {_c['tested']} proposed causes tested directly in round 13, {_c['held']} held, {_c['refuted']} were refuted "
        f"and {_c['undecided']} stayed undecided; the holds are weak evidence.")
_fam = ", ".join(f"{f[1].lower()} {_c['families'].get(f[0], [0, 0])[0]} of {_c['families'].get(f[0], [0, 0])[1]}"
                 for f in FAMILIES)
_out = _c["tested_all"] - _c["tested"]
EXAMPLES = [["round-13:s3-a", "Example: the vote over 12 samples"], ["round-13:s3-b", "Example: its rival, refuted"]]
PANELS = [
    ["new", "What is new",
     "From engine 13 on, a mechanism (a one-sentence cause proposed to explain the results) may forecast only after it "
     "holds a direct test: a check of that cause on answers and weights already stored, with the passing threshold "
     "fixed before looking.",
     [f"Round 13 ran {_c['tested']} direct tests: {_c['carried']} carried mechanisms ranked high by forecast score and "
      f"{_c['rivals']} new rivals, two for each of 6 results that both readers with no theory got wrong.",
      "POPPER (Huang et al., ICML 2025, arXiv 2502.09858, abstract and Section 2) has language-model agents design and "
      "run falsification tests of a hypothesis's measurable implications, on existing or new data. Here the same idea "
      "is a gate: a cause that fails its test does not forecast.",
      ["Theories on trial: the same engine's theories, scored on their predictions ›", "/finding/theories-on-trial"],
      ["Forecasts before results: scored on numbers before the jobs reported them ›", "/finding/forecasts-before-results"]]],
    ["why", "Why it matters",
     "Forecast score had ranked mechanisms whose causes were false: the 5 top-scoring mechanisms of round 12 each "
     "failed a direct test of their own claim (board item result-ca2fbe).",
     [f"In round 13 the gate stopped {_c['refuted'] + _c['undecided']} of {_c['tested']} from forecasting: "
      f"{_c['refuted']} refuted, {_c['undecided']} undecided.",
      f"Over all {_c['tested_all']} mechanisms with a direct test so far, {_c['held_all']} hold, {_c['refuted_all']} "
      f"are refuted and {_c['undecided_all']} are undecided.",
      f"Held, by family of cause, over all {_c['tested_all']}: {_fam}."]],
    ["how", "How we know",
     "Every dot is one row of studies/theory/results/direct_tested.json or refuted.json. Each test's plan, null and "
     "threshold were committed before its data was read.",
     [f"Round 13's {_c['tested']} tests ran offline on stored rows: per-problem answers, per-sample votes, stored "
      "singular value tables of the weight changes. 9 plans needed a fix before computing (a shared seed, a "
      "double-counted denominator, a wrong field name).",
      f"The board item (result-1eacdd) and the README count 8 refuted in round 13. The record holds {_c['refuted']} "
      f"refuted rows among its {_c['tested']} plans ({_c['held']} + {_c['refuted']} + {_c['undecided']} = "
      f"{_c['tested']}); this page counts the record.",
      "Undecided means the test met no refuting threshold but missed the bar for holding, or its data could not be "
      "read. It does not count as holding.",
      f"The engine's files name the family of {_c['family_from_files']} of the {_c['tested_all']} mechanisms; this page "
      f"assigned the other {_c['tested_all'] - _c['family_from_files']} from their claims, using the engine's six "
      "families."]],
    ["limits", "What it does not show",
     "A mechanism that holds its direct test has not been shown to forecast better: in round 13 the holders forecast "
     "nothing on still-open targets that the two readers with no theory miss.",
     ["Only one holder's forecast differed from both readers: s4-b on target t04, 416 against 401 and 401. "
      "result-2a5195 had already measured 401.",
      "The tests ran on stored rows, some on proxies: s1-a's test used the cued base's answer lengths because the "
      "method's own samples are not readable, and s5-a and s5-b could not run at all.",
      "Every hold has a caveat: small samples (21 problems for s3-a, 42 for s1-a), a proxy, point estimates only, or "
      "a test that cannot tell two rivals apart. Open a blue dot to read it.",
      "Agents of one model family wrote the mechanisms, planned the tests and ran them."]],
    ["run", "How to reproduce it",
     "uv run tools/finding_mechanisms_tested_directly.py, from the repository root, rebuilds every dot from the record "
     "files and checks the copy on this page.",
     [f"Record: {FILES[0]} and {FILES[1]}, as of commit {COMMIT}. Round 13's plans: "
      "studies/theory/results/wide/round-13/direct_tests.md.",
      "Each test: studies/theory/results/direct/<test>/ (readout.json, reading.md) and its spec "
      "studies/theory/specs/SPEC_direct_<name>.md; the README section Direct tests describes each.",
      "The engine: studies/theory/lib/forecast.py and .claude/skills/theory/SKILL.md (version 13). Board items: "
      "result-1eacdd (round 13), result-ca2fbe (engine 13)."]],
]

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant: __TITLE__</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
/* The tokens and the light of tools/architecture.py: one lit plate, glass in a dark room, porcelain on a grey table
   with a cast shadow in place of the glow. The light comes from the upper left in both. Blue marks a mechanism that
   holds its direct test; a ring, one that was refuted; a dashed ring, one left undecided. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4;
  --tick: #8b97a1; --band: rgba(16, 24, 32, .075); --ring: #56636d; --grey: #a3adb5;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1; --bloom: 1;
    --tick: #66737e; --band: rgba(233, 239, 243, .07); --ring: #9aa7b2; --grey: #56626c;
  }
}
:root[data-theme="dark"] {
  --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
  --blue: #8fb1ff; --red: #ff6b7c;
  --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
  --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
  --glow: 1; --shadow: 0; --spec: 1; --bloom: 1;
  --tick: #66737e; --band: rgba(233, 239, 243, .07); --ring: #9aa7b2; --grey: #56626c;
}
* { box-sizing: border-box; }
html { background: var(--paper); }
body {
  margin: 0; color: var(--ink); background: var(--paper);
  font: 400 15px/1.5 "Archivo", ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif;
  font-variant-numeric: tabular-nums; -webkit-font-smoothing: antialiased;
}
button { font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; text-align: left; }
a { color: inherit; }
:focus-visible { outline: 2px solid var(--blue); outline-offset: 3px; border-radius: 3px; }
.page {
  display: grid; grid-template-columns: minmax(0, 1fr) minmax(320px, 27vw); grid-template-rows: auto minmax(0, 1fr);
  gap: 0; height: 100vh; min-height: 620px; max-width: 1840px; margin: 0 auto; padding: 20px 40px 28px;
}
.top { grid-column: 1 / -1; display: flex; align-items: center; gap: 26px; font-size: 13px; padding-bottom: 16px; border-bottom: 1px solid var(--rule); }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; margin: 0 6px 0 0; }
.top a { color: var(--mute); text-decoration: none; white-space: nowrap; transition: color .15s ease; }
.top a:hover { color: var(--ink); }
.top a[aria-current] { color: var(--ink); font-weight: 600; }

/* The picture: one plate with every mechanism, the counts and the one control */
.stage { min-height: 0; min-width: 0; display: flex; flex-direction: column; justify-content: center; padding: 8px 40px 0 0; }
svg { width: 100%; max-height: calc(100vh - 190px); display: block; overflow: visible; cursor: default; user-select: none; -webkit-user-select: none; }
svg:focus:not(:focus-visible) { outline: none; }
svg text { font-family: inherit; fill: var(--ink); font-stretch: 106%; }
svg * { pointer-events: none; }
.atmo { opacity: var(--glow); }
.shade { fill: var(--ink); opacity: calc(var(--shadow) * .17); }
.spec { opacity: var(--spec); }
.back { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: 1; }
.plate { fill: url(#body) var(--sheet); stroke: url(#rim) var(--ink); stroke-width: 1.7; }
.hair { stroke: var(--rule); stroke-width: 1; }
.big { font-weight: 660; letter-spacing: -.035em; font-stretch: 100%; }
.set { fill: var(--ink) !important; font-weight: 640; }
.lab { fill: var(--mute) !important; font-weight: 520; }
.lab0 { fill: var(--ink) !important; font-weight: 460; }
.m { stroke-width: 1.3; transition: opacity .25s ease; }
.m-n { fill: var(--grey); stroke: none; }
.m-h { fill: var(--blue); stroke: none; }
.m-r { fill: var(--sheet); stroke: var(--ring); }
.m-u { fill: none; stroke: var(--ring); stroke-dasharray: 2.2 1.9; }
.halo { fill: none; stroke: var(--blue); stroke-width: 1; opacity: 0; }
.selring { fill: none; stroke: var(--ink); stroke-width: 1.3; }
.burst { fill: none; stroke: var(--blue); }
.lb { font-weight: 500; }
.lb.r, .lb.u { fill: var(--mute) !important; }
.lb.o { fill: var(--faint) !important; font-weight: 450; }
.vc { font-weight: 640; letter-spacing: -.02em; font-stretch: 100%; }
.vn { font-weight: 600; }
.vs, .fs, .ps { fill: var(--mute) !important; font-weight: 500; }
.fh { font-weight: 660; font-stretch: 110%; }
.kt { fill: var(--mute) !important; font-weight: 520; }
.rp { fill: var(--mute) !important; font-weight: 500; transition: opacity .4s ease; }
.ctl { display: flex; align-items: center; gap: 12px; align-self: center; margin-top: 14px; }
.ctl .lbl { font-size: 13px; color: var(--mute); }
.switch { display: inline-flex; border: 1px solid var(--faint); border-radius: 999px; padding: 3px; }
.switch button { min-width: 40px; padding: 8px 16px; border-radius: 999px; font-weight: 600; font-size: 14.5px; text-align: center; white-space: nowrap; transition: background .15s ease, color .15s ease; }
.switch button:hover { color: var(--blue); }
.switch button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.switch button[aria-pressed="true"]:hover { color: var(--paper); }
.hint { align-self: center; margin: 10px 0 0; font-size: 13px; color: var(--mute); }

/* One drawn entrance, then only the slow sway and one replayed test at a time */
@keyframes draw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
@keyframes fade { from { opacity: 0; } }
.enter .draw { stroke-dasharray: 1; animation: draw 1.1s cubic-bezier(.6, 0, .2, 1) both; }
.enter .atmo, .enter .shade, .enter .spec, .enter .back { animation: fade 1.3s .15s both; }
.enter .read, .enter .key { animation: fade .7s .5s both; }

/* The words */
.side {
  min-width: 0; min-height: 0; overflow-y: auto; scrollbar-width: none;
  padding: clamp(20px, 7vh, 96px) 0 0 40px; border-left: 1px solid var(--rule);
}
.problem { margin: 0; color: var(--mute); font-size: clamp(16px, 1.25vw, 20px); line-height: 1.3; max-width: 26ch; }
.say { margin: 14px 0 0; font-size: clamp(25px, 2.15vw, 40px); line-height: 1.14; font-weight: 300; font-stretch: 102%; letter-spacing: -.016em; max-width: 17ch; }
.say b { font-weight: 620; white-space: nowrap; }
.pane { margin-top: clamp(22px, 4vh, 44px); padding-bottom: 24px; }
.more { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--rule); }
.more button { display: flex; width: 100%; justify-content: space-between; align-items: baseline; padding: 12px 0; border-bottom: 1px solid var(--rule); font-size: 17px; font-weight: 520; transition: color .15s ease; }
.more button span { color: var(--faint); font-size: 20px; line-height: 1; }
.more button:hover { color: var(--blue); }
.more.ex { margin-top: 18px; border-top: 0; }
.more.ex button { font-size: 15px; color: var(--mute); padding: 9px 0; }
.more.ex button:hover { color: var(--blue); }
.dhead { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding: 0 6px 12px 0; border-bottom: 1px solid var(--ink); }
.dhead h2 { margin: 0; font-size: 17px; font-weight: 660; font-stretch: 114%; letter-spacing: .008em; }
.close { font-size: 13px; color: var(--mute); }
.close:hover { color: var(--ink); }
.lead { margin: 18px 0 0; font-size: clamp(17px, 1.3vw, 21px); line-height: 1.36; font-weight: 380; max-width: 30ch; overflow-wrap: anywhere; }
.quote { margin: 10px 0 0; font-size: clamp(15.5px, 1.1vw, 18px); line-height: 1.42; font-weight: 380; max-width: 36ch; overflow-wrap: anywhere; }
.tag { margin: 12px 0 0; font-size: 13.5px; color: var(--mute); }
.tag b { color: var(--ink); font-weight: 640; }
.why { margin: 8px 0 0; font-size: 14px; line-height: 1.45; color: var(--mute); max-width: 44ch; overflow-wrap: anywhere; }
.why b { color: var(--ink); font-weight: 640; }
.case { margin: 16px 0 0; padding: 8px 0 8px 12px; border-left: 2px solid var(--blue); font-size: 14px; line-height: 1.45; max-width: 44ch; }
.facts { list-style: none; margin: 18px 0 0; padding: 0; font-size: 14.5px; color: var(--mute); max-width: 40ch; overflow-wrap: anywhere; }
.facts li { padding: 8px 0; border-top: 1px solid var(--rule); }
.facts a { color: var(--ink); text-decoration: none; }
.facts a:hover { color: var(--blue); }
h3 { margin: 22px 0 0; font-size: 14px; font-weight: 660; font-stretch: 110%; padding-bottom: 6px; border-bottom: 1px solid var(--rule); }
.gauge { width: 100%; max-width: 320px; height: auto; margin: 12px 0 0; max-height: none; }
.g-ax { stroke: var(--rule); stroke-width: 1; }
.g-pass { fill: var(--band); }
.g-thr { stroke: var(--ink); stroke-width: 1.4; }
.g-ci { stroke-width: 3; stroke-linecap: round; }
.g-ci.h { stroke: var(--blue); } .g-ci.r, .g-ci.u { stroke: var(--ring); }
.g-pt.h { fill: var(--blue); } .g-pt.r { fill: var(--sheet); stroke: var(--ring); stroke-width: 1.6; } .g-pt.u { fill: var(--sheet); stroke: var(--ring); stroke-width: 1.6; stroke-dasharray: 2 1.6; }
.g-t { fill: var(--mute) !important; font-weight: 520; }
.steps { display: flex; justify-content: space-between; margin-top: 16px; font-size: 13px; color: var(--mute); }
.steps button:hover { color: var(--ink); }
@media (max-width: 900px) {
  /* On a phone the order is: the problem, the finding, the picture, the depth. */
  .page { display: flex; flex-direction: column; height: auto; min-height: 0; padding: 16px 16px 40px; }
  .top { gap: 13px; padding-bottom: 12px; flex-wrap: wrap; }
  .name { font-stretch: 112%; margin-right: 0; }
  .side { display: contents; }
  .problem { order: 1; margin-top: 20px; max-width: none; }
  .say { order: 2; max-width: 22ch; }
  .stage { order: 3; margin-top: 22px; padding: 0; display: block; }
  .pane { order: 4; margin-top: 22px; }
  svg { max-height: none; }
  .ctl { flex-direction: column; gap: 8px; margin-top: 14px; }
  .switch { display: grid; grid-auto-flow: column; grid-auto-columns: minmax(0, 1fr); width: 100%; border-radius: 18px; }
  .switch button { min-width: 0; padding: 10px 0; font-size: 14px; border-radius: 14px; }
  .hint { text-align: center; }
}
@media (prefers-reduced-motion: reduce) {
  .enter * { animation: none !important; }
  .switch button, .more button, .top a, .m, .rp { transition: none; }
}
</style>
</head>
<body>
<div class="page">
  <header class="top">
    <h1 class="name">Invariant</h1>
    <a href="/">Board</a>
    <a href="/architecture">Design</a>
    <a href="/proof">Proof</a>
    <a href="/findings" aria-current="page">Findings</a>
  </header>
  <div class="stage" id="stage">
    <svg id="svg" role="img" tabindex="0"></svg>
    <div class="ctl">
      <span class="lbl" id="ctllbl">Show</span>
      <div class="switch" id="switch" role="group" aria-labelledby="ctllbl"></div>
    </div>
    <p class="hint">Click a cause, or press Enter on the picture, to see its claim and its test.</p>
  </div>
  <div class="side">
    <p class="problem" id="problem"></p>
    <p class="say" id="say"></p>
    <div class="pane" id="pane" aria-live="polite"></div>
  </div>
</div>
<script>
const C = __CONFIG__, $ = id => document.getElementById(id);
const still = matchMedia("(prefers-reduced-motion: reduce)"), narrow = matchMedia("(max-width: 900px)");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const RAD = Math.PI / 180, f = n => n.toFixed(1), mix = (a, b, q) => a + (b - a) * q;
const ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2, clamp = (v, a, b) => Math.min(b, Math.max(a, v));
/* A number as the readouts hold it, at a precision that keeps it readable, with a real minus sign. */
function fv(x) {
  if (x == null) return "none";
  const a = Math.abs(x);
  const s = a >= 100 ? Math.round(a).toLocaleString("en-US") : a >= 10 ? String(+a.toFixed(1)) : a === 0 ? "0" : String(+a.toPrecision(3));
  return (x < 0 ? "−" : "") + s;
}
const minus = s => String(s).replace(/(^|[\s(\[])-(?=\d)/g, "$1−");

/* The three states of the control. Tested is the page's first state; Proposed is where its dots start. */
const STATES = ["proposed", "tested", "family"], SNAME = ["Proposed", "Tested", "By family"];
const V3 = ["holds", "refuted", "undecided"], VK = { holds: "h", refuted: "r", undecided: "u" };
const VNAME = { h: "hold", r: "refuted", u: "undecided" };
const FAM = Object.fromEntries(C.families.map((x, k) => [x[0], { k, id: x[0], name: x[1], gloss: x[2] }]));

/* ROWS of tools/finding_mechanisms_tested_directly.py; the fields are named above ROWS there. */
const M = C.rows.map(([id, verdict, kind, fam, famsrc, at, result, claim, measured, test, gauge], i) => {
  const t = C.tests[id];
  return { i, id, key: id.replace("/", ":"), v: VK[verdict], verdict, kind, r13: !!kind, fam, famsrc, at, result, claim,
           measured, test, gauge, label: t[0], spec: t[1], rule: t[2], note: t[3] };
});
const MK = Object.fromEntries(M.map(m => [m.key, m]));
const VORD = { h: 0, u: 1, r: 2 };
const byTime = (a, b) => a.i - b.i;
const S = { s: 1, open: null, g: null, el: {}, shown: {}, last: 0, t0: -1e9, from: null, dirty: true, rp: null, rpNext: 0, rpAt: 0, started: false };

/* Geometry, in plate units (x right, y down; z toward the viewer). */
function geo() {
  return narrow.matches
    ? { w: 480, cx: 240, D: 2000, r: 22, deep: 30, blur: 12, phone: true, fs: 17.5, fl: 17.5, fc: 40, fh: 18.5, fk: 16,
        setX: 26, setY: 52, bigX: 22, bigY: 140, fb: 88, labX: 26, labY: [178, 202], top: 262, cols: [[30, 450]], pitch: 30,
        gap: 12, ghead: 62, ggap: 26, dot: 6.5, small: 4.6 }
    : { w: 1000, cx: 500, D: 2200, r: 30, deep: 40, blur: 16, phone: false, fs: 14, fl: 13.5, fc: 34, fh: 15, fk: 13,
        setX: 58, setY: 66, bigX: 52, bigY: 150, fb: 92, labX: 372, labY: [124, 146], top: 214, cols: [[62, 330], [362, 630], [662, 950]],
        pitch: 22, gap: 9, ghead: 50, ggap: 22, dot: 5.4, small: 3.8 };
}
const V = { c1: 1, s1: 0, c2: 1, s2: 0, px: 0, py: 0, tx: 0, ty: 0 };
function aim(yaw, pitch) { V.c1 = Math.cos(yaw * RAD); V.s1 = Math.sin(yaw * RAD); V.c2 = Math.cos(pitch * RAD); V.s2 = Math.sin(pitch * RAD); }
function proj(g, x, y, z) {
  const X = x - g.cx, Y = y - g.cy, x1 = X * V.c1 + z * V.s1, z1 = z * V.c1 - X * V.s1;
  const y1 = Y * V.c2 - z1 * V.s2, k = g.D / (g.D - (z1 * V.c2 + Y * V.s2));
  return [g.cx + x1 * k, g.cy + y1 * k];
}
function rounded(g, [x0, y0, x1, y1], r, z) {  // a rounded rectangle at depth z
  const p = [], corner = (cx, cy, a0) => { for (let i = 0; i <= 6; i++) p.push(proj(g, cx + r * Math.cos((a0 + 15 * i) * RAD), cy + r * Math.sin((a0 + 15 * i) * RAD), z)); };
  corner(x1 - r, y0 + r, -90); corner(x1 - r, y1 - r, 0); corner(x0 + r, y1 - r, 90); corner(x0 + r, y0 + r, 180);
  return "M" + p.map(q => f(q[0]) + " " + f(q[1])).join("L") + "Z";
}

/* The lists of each state. A list is [header, marks]; marks of round 13 come first, then those tested outside it. */
function lists(s) {
  const r13first = (a, b) => (b.r13 - a.r13) || byTime(a, b);
  if (s === 0) return [{ kind: "p", marks: M.slice().sort(byTime) }];
  if (s === 1) return ["h", "r", "u"].map(v => ({ kind: "v", v, marks: M.filter(m => m.v === v).sort(r13first) }));
  return C.families.map(x => ({ kind: "f", fam: x[0], marks: M.filter(m => m.fam === x[0]).sort((a, b) => VORD[a.v] - VORD[b.v] || r13first(a, b)) }))
    .filter(l => l.marks.length);
}
/* Which column each list goes in on a wide screen: one per verdict; families packed so the columns end near level. */
function columns(g, s, ls) {
  if (g.phone) return [ls];
  if (s === 1) return ls.map(l => [l]);
  if (s === 0) return [ls];
  const cols = [[], [], []], h = [0, 0, 0], need = l => g.ghead + l.marks.length * g.pitch;
  ls.slice().sort((a, b) => b.marks.length - a.marks.length).forEach(l => { const k = h.indexOf(Math.min(...h)); cols[k].push(l); h[k] += need(l) + g.ggap; });
  return cols.map(c => c.sort((a, b) => FAM[a.fam].k - FAM[b.fam].k));
}
/* The target of every mark and header in each state: L[s] = { P: [{x, y, r, la, st, a}], H: {id: {x, y, a}} }. */
function layouts(g) {
  const L = [];
  let bottom = 0;
  for (let s = 0; s < 3; s++) {
    const st = { P: [], H: {} }, ls = lists(s), cols = columns(g, s, ls);
    if (s === 0 && !g.phone) {  // the dots together, a loose disc in the middle of the field
      const cx = 500, cy = g.top + 165;
      M.slice().sort(byTime).forEach((m, k) => {
        const rr = 23 * Math.sqrt(k + .6), th = k * 2.39996;
        st.P[m.i] = { x: cx + rr * Math.cos(th), y: cy + rr * Math.sin(th) * .92, r: m.r13 ? g.dot : g.small, la: 0, st: "n", a: 1 };
      });
      st.H.ph = { x: cx, y: cy + 160, a: 1 };
      L.push(st);
      continue;
    }
    const tight = g.phone && s === 2, pitch = tight ? 26 : g.pitch, ghead = tight ? 50 : g.ghead, ggap = tight ? 16 : g.ggap;
    cols.forEach((col, ci) => {
      let y = g.top;
      const [x0, x1] = g.cols[ci];
      col.forEach(l => {
        const id = l.kind === "v" ? "v" + l.v : l.kind === "f" ? "f" + l.fam : "ph";
        st.H[id] = { x: x0, y, a: 1, x1 };
        y += l.kind === "p" ? ghead * .7 : ghead;
        l.marks.forEach((m, k) => {
          if (k && l.marks[k - 1].r13 && !m.r13 && l.kind === "v") y += g.gap;
          st.P[m.i] = { x: x0 + 8, y, r: m.r13 ? g.dot : g.small, la: 1, st: s === 0 ? "n" : m.v, a: 1 };
          y += pitch;
        });
        y += ggap;
      });
      bottom = Math.max(bottom, y);
    });
    L.push(st);
  }
  return { L, bottom };
}

const KEYS = [["h", "Holds"], ["r", "Refuted"], ["u", "Undecided"], ["o", "Tested in other rounds"]];
function build() {
  const g = S.g = geo(), svg = $("svg");
  const { L, bottom } = layouts(g);
  S.L = L;
  g.keyY = bottom + (g.phone ? 14 : 4);
  g.rpY = g.keyY + (g.phone ? 64 : 0);
  g.h = Math.max(g.phone ? 0 : 620, g.rpY + (g.phone ? 56 : 34));
  g.cy = g.h / 2;
  g.a = g.phone ? [6, 8, g.w - 6, g.h - 8] : [24, 18, 976, g.h - 14];
  const [ax0, ay0, ax1, ay1] = g.a, aw = ax1 - ax0, ah = ay1 - ay0;
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  const T = (cls, id, fs, extra = "") => `<text class="${cls}" id="${id}" font-size="${fs}"${extra}></text>`;
  svg.setAttribute("viewBox", `0 0 ${g.w} ${g.h}`);
  svg.innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".22" r=".95">${stop(0, "var(--glass-hi)")}${stop(.46, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1=".04" x2=".94" y2=".96">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.5, "var(--blue)", .2)}${stop(.72, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="spec">${stop(0, "#fff", .2)}${stop(1, "#fff", 0)}</radialGradient>` +
    `<filter id="soft" x="-20%" y="-20%" width="140%" height="150%"><feGaussianBlur stdDeviation="${g.blur}"/></filter></defs>` +
    `<ellipse class="atmo" cx="${g.cx}" cy="${g.cy}" rx="${f(aw * .8)}" ry="${f(ah * .9)}" fill="url(#atmo)"/>` +
    `<rect class="shade" x="${f(ax0 + aw * .012)}" y="${f(ay0 + ah * .03)}" width="${aw}" height="${ah}" rx="${g.r}" filter="url(#soft)"/>` +
    `<path class="back" id="back"/><path class="plate draw" id="plate" pathLength="1"/>` +
    `<ellipse class="spec" cx="${f(ax0 + aw * .3)}" cy="${f(ay0 + ah * .2)}" rx="${f(aw * .3)}" ry="${f(ah * .16)}" transform="rotate(-14 ${f(ax0 + aw * .3)} ${f(ay0 + ah * .2)})" fill="url(#spec)"/>` +
    `<g class="read">` + T("set", "set", g.fs) + T("big", "big", g.fb) + T("lab0", "bl0", g.fl + 2.5) + T("lab", "bl1", g.fl + 1.5) +
    `<path class="hair" id="hair"/>` +
    ["h", "r", "u"].map(v => T("vc", "vc" + v, g.fc) + T("vn", "vn" + v, g.fh + 1) + T("vs", "vs" + v, g.fl - .5)).join("") +
    C.families.map(x => T("fh", "ff" + x[0], g.fh) + T("fs", "fs" + x[0], g.fl - .5)).join("") +
    T("ps", "ph", g.fh, g.phone ? "" : ` text-anchor="middle"`) + `</g>` +
    `<g id="fg"><circle class="burst" id="bu" r="0"/>` + M.map(m => `<circle class="halo" id="ha${m.i}"/><circle class="m m-n" id="m${m.i}"/>`).join("") +
    `<circle class="selring" id="sel" r="0"/></g>` +
    `<g>` + M.map(m => T("lb" + (m.r13 ? "" : " o"), "lb" + m.i, g.fl)).join("") + `</g>` +
    `<g class="key">` + KEYS.map(([k, t], j) => `<circle class="m ${k === "o" ? "m-n" : "m-" + k}" id="kd${j}"/>` + T("kt", "kt" + j, g.fk)).join("") + `</g>` +
    T("rp", "rp", g.fk) + T("rp", "rp2", g.fk);
  S.el = {}; S.shown = {};
  svg.querySelectorAll("[id]").forEach(e => { S.el[e.id] = e; });
  M.forEach(m => { S.el["lb" + m.i].textContent = m.label; });
  KEYS.forEach(([, t], j) => { S.el["kt" + j].textContent = t; });
  S.from = null; S.dirty = true; S.cls = {};
}

/* Where each mark is in a change: from S.from to the targets of state S.s, starting at t0, 16 ms later per mark in reading
   order, over 0.7 s. */
const DUR = 700, STAG = 16;
function order(s) { return lists(s).flatMap(l => l.marks); }
function at(i, now) {
  const to = S.L[S.s].P[i];
  if (!S.from) return { ...to, p: 1 };
  const from = S.from[i], p = clamp((now - S.t0 - STAG * S.ord[i]) / DUR, 0, 1);
  if (p >= 1) return { ...to, p: 1 };
  const e = ease(p);
  return { x: mix(from.x, to.x, e), y: mix(from.y, to.y, e), r: mix(from.r, to.r, e), a: 1,
           la: to.la > from.la ? to.la * clamp((p - .75) / .25, 0, 1) : from.la * (1 - clamp(p / .3, 0, 1)), st: p < .5 ? from.st : to.st, p };
}
function snapshot(now) { return M.map(m => { const q = at(m.i, now); return { x: q.x, y: q.y, r: q.r, la: q.la, st: q.st }; }); }

const circ = (x, y, r) => [f(x), f(y), f(Math.max(0, r))];
function place(now) {
  const g = S.g, E = S.el, put = (el, q, dy = 0) => { el.setAttribute("x", f(q[0])); el.setAttribute("y", f(q[1] + dy)); };
  const text = (id, v) => { if (S.shown[id] !== v) E[id].textContent = S.shown[id] = v; };
  E.back.setAttribute("d", rounded(g, g.a, g.r, -g.deep));
  E.plate.setAttribute("d", rounded(g, g.a, g.r, 0));
  const z = 10, A = proj(g, 0, 0, z), B = proj(g, g.w, 0, z), Cc = proj(g, 0, g.h, z);
  const m6 = [(B[0] - A[0]) / g.w, (B[1] - A[1]) / g.w, (Cc[0] - A[0]) / g.h, (Cc[1] - A[1]) / g.h, A[0], A[1]];
  E.fg.setAttribute("transform", `matrix(${m6.map(v => v.toFixed(4)).join(" ")})`);
  const fp = (u, v) => [m6[0] * u + m6[2] * v + m6[4], m6[1] * u + m6[3] * v + m6[5]];
  // The headline: round 13's share that holds, and the record over every round.
  const c = C.counts;
  text("set", "Round 13 · direct tests on stored data");
  text("big", `${c.held} of ${c.tested}`);
  text("bl0", "proposed causes held their direct test.");
  text("bl1", `All rounds together: ${c.held_all} of ${c.tested_all}.`);
  put(E.set, fp(g.setX, g.setY)); put(E.big, fp(g.bigX, g.bigY));
  if (g.phone) { put(E.bl0, fp(g.labX, g.labY[0])); put(E.bl1, fp(g.labX, g.labY[1])); }
  else { put(E.bl0, fp(g.labX, g.labY[0])); put(E.bl1, fp(g.labX, g.labY[1])); }
  const h0 = fp(g.phone ? 26 : 58, g.top - (g.phone ? 34 : 36)), h1 = fp(g.phone ? 454 : 942, g.top - (g.phone ? 34 : 36));
  E.hair.setAttribute("d", `M${f(h0[0])} ${f(h0[1])}L${f(h1[0])} ${f(h1[1])}`);
  // The marks: moved only while they travel or the selection changes.
  const sel = S.open && MK[S.open] ? MK[S.open] : null, moving = S.from && now - S.t0 < DUR + STAG * M.length + 40;
  const Q = M.map(m => at(m.i, now));
  if (S.dirty || moving) {
    M.forEach((m, k) => {
      const q = Q[k], el = E["m" + m.i], cls = "m m-" + (q.st === "n" ? "n" : q.st), dim = sel && sel !== m ? .28 : 1;
      if (S.cls[k] !== cls) { el.setAttribute("class", cls); S.cls[k] = cls; }
      const [x, y, r] = circ(q.x, q.y, q.r);
      el.setAttribute("cx", x); el.setAttribute("cy", y); el.setAttribute("r", r);
      el.style.opacity = (m.r13 ? 1 : .62) * dim;
      const ha = E["ha" + m.i];
      ha.setAttribute("cx", x); ha.setAttribute("cy", y); ha.setAttribute("r", f(q.r + 3.2));
      ha.style.opacity = q.st === "h" && m.r13 ? (.35 * dim * getBloom()).toFixed(2) : 0;
    });
    if (sel) { const q = Q[sel.i]; E.sel.setAttribute("cx", f(q.x)); E.sel.setAttribute("cy", f(q.y)); E.sel.setAttribute("r", f(q.r + 5)); }
    else E.sel.setAttribute("r", 0);
    S.dirty = !!moving;
  }
  M.forEach((m, k) => {  // the labels stay upright: placed at their projected point
    const q = Q[k], el = E["lb" + m.i], a = q.la * (sel && sel !== m ? .3 : 1);
    if (a <= .01) { if (el.style.opacity !== "0") el.style.opacity = 0; return; }
    put(el, fp(q.x + 15, q.y), g.fl * .35);
    el.style.opacity = a.toFixed(2);
    el.setAttribute("class", "lb" + (m.r13 ? "" : " o") + (q.st === "r" ? " r" : q.st === "u" ? " u" : ""));
  });
  // The headers of the state: they come in with the marks, and each count counts the marks that have arrived.
  const prog = S.from ? Q.reduce((a, q) => a + q.p, 0) / M.length : 1, H = S.L[S.s].H;
  ["h", "r", "u"].forEach(v => {
    const hd = H["v" + v], ids = ["vc" + v, "vn" + v, "vs" + v];
    if (!hd) { ids.forEach(id => { E[id].style.opacity = 0; }); return; }
    const here = M.filter(m => m.v === v), n13 = here.filter(m => m.r13 && Q[m.i].p >= .5).length, no = here.filter(m => !m.r13 && Q[m.i].p >= .5).length;
    const tot = here.filter(m => !m.r13).length;
    text("vc" + v, String(n13)); text("vn" + v, VNAME[v]);
    text("vs" + v, tot ? `+${no} tested in other rounds` : "none in other rounds");
    const a = clamp(prog * 1.6 - .2, 0, 1).toFixed(2);
    put(E["vc" + v], fp(hd.x - 2, hd.y + (g.phone ? 4 : 2)));
    const w = (n13 >= 10 ? 1.15 : .6) * g.fc;
    put(E["vn" + v], fp(hd.x + w + 4, hd.y + (g.phone ? 4 : 2)));
    put(E["vs" + v], fp(hd.x, hd.y + (g.phone ? 30 : 22)));
    ids.forEach(id => { E[id].style.opacity = a; });
  });
  C.families.forEach(([id, name]) => {
    const hd = H["f" + id], e1 = E["ff" + id], e2 = E["fs" + id];
    if (!hd) { e1.style.opacity = e2.style.opacity = 0; return; }
    const here = M.filter(m => m.fam === id), held = here.filter(m => m.v === "h" && Q[m.i].p >= .5).length;
    text("ff" + id, name);
    text("fs" + id, `${held} of ${here.length} hold · ${FAM[id].gloss}`);
    put(e1, fp(hd.x, hd.y + 4)); put(e2, fp(hd.x, hd.y + (g.phone ? 28 : 22)));
    e1.style.opacity = e2.style.opacity = clamp(prog * 1.6 - .2, 0, 1).toFixed(2);
  });
  const ph = H.ph;
  if (ph) {
    text("ph", `${M.length} proposed causes: ${c.tested} tested in round 13, ${M.length - c.tested} in other rounds`);
    put(E.ph, fp(ph.x, ph.y + 4)); E.ph.style.opacity = clamp(prog * 1.6 - .2, 0, 1).toFixed(2);
  } else E.ph.style.opacity = 0;
  // The key, under the field.
  const ky = g.keyY, xs = g.phone ? [30, 150, 290, 30] : [62, 150, 250, 362], ys = g.phone ? [ky, ky, ky, ky + 30] : [ky, ky, ky, ky];
  KEYS.forEach((_, j) => {
    const q = fp(xs[j], ys[j]), d = E["kd" + j];
    d.setAttribute("cx", f(q[0])); d.setAttribute("cy", f(q[1])); d.setAttribute("r", j === 3 ? g.small * .95 : g.dot * .95);
    d.style.opacity = j === 3 ? .62 : 1;
    put(E["kt" + j], [q[0] + 11, q[1]], g.fk * .36);
  });
  replay(now, fp, Q);
}
function getBloom() { return parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--bloom")) || 1; }

/* The replay: about every 2.6 s, the next test in the order its result was posted lights its dot, and the line under
   the key names it. Stops while a mechanism is open. */
function replay(now, fp, Q) {
  const E = S.el, g = S.g;
  if (still.matches || S.open || now - S.t0 < DUR + 800) { E.bu.setAttribute("r", 0); E.rp.style.opacity = E.rp2.style.opacity = 0; return; }
  if (!S.rp && now > S.rpNext) S.rp = { m: M[S.rpAt++ % M.length], t0: now };
  if (!S.rp) return;
  const m = S.rp.m, t = clamp((now - S.rp.t0) / 1300, 0, 1), q = Q[m.i];
  E.bu.setAttribute("cx", f(q.x)); E.bu.setAttribute("cy", f(q.y));
  E.bu.setAttribute("r", f(q.r + 14 * ease(t)));
  E.bu.style.opacity = (1 - t).toFixed(2);
  E.bu.setAttribute("stroke-width", f(1.6 * (1 - t) + .3));
  const when = m.at.slice(11, 16), v = { h: "holds", r: "refuted", u: "undecided" }[m.v], what = `${m.label} · ${S.s === 0 ? "proposed" : v}`;
  const s1 = g.phone ? `Replay in posting order · ${when} UTC` : `Posted ${when} UTC · ${what}`, s2 = g.phone ? what : "";
  if (S.shown.rp !== s1) { E.rp.textContent = S.shown.rp = s1; }
  if (S.shown.rp2 !== s2) { E.rp2.textContent = S.shown.rp2 = s2; }
  put2(E.rp, fp(g.phone ? 30 : 942, g.rpY), g.fk * .36, g.phone ? "start" : "end");
  put2(E.rp2, fp(30, g.rpY + 24), g.fk * .36, "start");
  E.rp.style.opacity = E.rp2.style.opacity = .9;
  if (t >= 1) { S.rp = null; S.rpNext = now + 1300; }
}
function put2(el, q, dy, anchor) { el.setAttribute("x", f(q[0])); el.setAttribute("y", f(q[1] + dy)); el.setAttribute("text-anchor", anchor); }
function stopReplay() { S.rp = null; S.rpNext = performance.now() + 2200; if (S.el.bu) S.el.bu.setAttribute("r", "0"); }

/* Always on: the plate sways by a few degrees and leans toward the mouse. About 30 frames a second. With reduced motion
   the page shows one still frame per state. */
function frame(now) {
  requestAnimationFrame(frame);
  if (still.matches || now - S.last < 30) return;
  S.last = now;
  const t = now / 1000;
  V.px += (V.tx - V.px) * .1; V.py += (V.ty - V.py) * .1;
  aim(3.2 * Math.sin(t * .13) + 3 * V.px, 1.8 * Math.sin(t * .09) - 1.8 * V.py);
  place(now);
}
function setState(s, opts = {}) {
  const now = performance.now(), quick = still.matches || opts.instant;
  S.from = quick ? null : opts.from || snapshot(now);
  S.s = s;
  S.ord = []; order(s).forEach((m, k) => { S.ord[m.i] = k; });
  S.t0 = quick ? -1e9 : now + (opts.delay || 0);
  S.dirty = true;
  stopReplay();
  $("switch").querySelectorAll("button").forEach((b, k) => b.setAttribute("aria-pressed", k === s));
  const c = C.counts;
  $("svg").setAttribute("aria-label", `${SNAME[s]}: each dot is one proposed cause with a direct test. In round 13, ${c.held} of ${c.tested} held, ` +
    `${c.refuted} were refuted and ${c.undecided} stayed undecided. Arrow keys change the view; Enter opens a cause.`);
  if (still.matches) { aim(0, 0); place(now); }
}

/* The side column: the five panels and two examples, or one mechanism: its claim, its test, measured against the
   threshold, its caveat and its board item. */
function gaugeSvg(m) {
  const [v, lo, hi] = m.gauge, [, , , thr, side] = m.spec;
  const xs = [v, lo, hi, thr].filter(x => x != null);
  let a = Math.min(...xs), b = Math.max(...xs);
  if (a === b) { a -= 1; b += 1; }
  const pad = (b - a) * .14, X = x => 10 + 300 * (x - a + pad) / (b - a + 2 * pad), T = X(thr);
  let s = `<svg class="gauge" viewBox="0 0 320 64" aria-hidden="true">`;
  s += side === "above" ? `<rect class="g-pass" x="${f(T)}" y="18" width="${f(310 - T)}" height="22"/>` : `<rect class="g-pass" x="10" y="18" width="${f(T - 10)}" height="22"/>`;
  s += `<path class="g-ax" d="M10 40.5H310"/><path class="g-thr" d="M${f(T)} 12V46"/>`;
  s += `<text class="g-t" x="${f(T)}" y="60" font-size="12" text-anchor="middle">${esc(fv(thr))}</text>`;
  if (lo != null) s += `<path class="g-ci ${m.v}" d="M${f(X(lo))} 29H${f(X(hi))}"/>`;
  s += `<circle class="g-pt ${m.v}" cx="${f(X(v))}" cy="29" r="5"/>`;
  return s + `</svg>`;
}
function mechPane(m) {
  const v = { h: "Holds", r: "Refuted", u: "Undecided" }[m.v];
  const where = m.kind === "carried" ? "Round 13 · carried from an earlier round" : m.kind === "rival" ? "Round 13 · a new rival" : "Tested outside round 13";
  let h = `<div class="dhead"><h2>${esc(m.label)}</h2><button class="close" data-open="">Close</button></div>`;
  h += `<p class="tag">${where} · <b>${v}</b></p>`;
  h += `<h3>The claim, in the record's words</h3><p class="quote">${esc(minus(m.claim))}</p>`;
  h += `<h3>The test${m.test ? " (" + esc(m.test) + ")" : ""}</h3><p class="why">${esc(m.rule)}</p>`;
  if (m.gauge) {
    const [val, lo, hi] = m.gauge, [qty, unit, level] = m.spec;
    h += gaugeSvg(m);
    h += `<p class="why">${esc(qty[0].toUpperCase() + qty.slice(1))}: <b>${fv(val)}</b>${unit && unit !== "share" && unit !== "ratio" && unit !== "fraction" ? " " + esc(unit) : ""}` +
      (lo != null ? ` (${esc(level)} interval ${fv(lo)} to ${fv(hi)})` : "") + `. The line is the threshold; the shaded side is where the claim survives.</p>`;
  }
  h += `<h3>Measured, as recorded</h3><p class="why">${esc(minus(m.measured))}</p>`;
  if (m.note) h += `<p class="case">${esc(m.note)}</p>`;
  const fam = FAM[m.fam];
  h += `<ul class="facts"><li>Family of cause: ${esc(fam.name.toLowerCase())} (${m.famsrc === "file" ? "from the engine's files" : "assigned on this page from the claim"})</li>` +
    `<li>Mechanism ${esc(m.id)}</li>` +
    `<li>Board item <a href="/#${esc(m.result)}">${esc(m.result)}</a>, posted ${esc(m.at.slice(0, 10))} ${esc(m.at.slice(11, 16))} UTC</li></ul>`;
  return h + `<div class="steps"><button data-step="-1">‹ Previous cause</button><button data-step="1">Next cause ›</button></div>`;
}
function pane() {
  const p = C.panels.find(p => p[0] === S.open), m = S.open && MK[S.open];
  const fact = x => Array.isArray(x) ? `<li><a href="${esc(x[1])}">${esc(x[0])}</a></li>` : `<li>${esc(minus(x))}</li>`;
  $("pane").innerHTML = m ? `<div>${mechPane(m)}</div>` : p
    ? `<div class="dhead"><h2>${esc(p[1])}</h2><button class="close" data-open="">Close</button></div><p class="lead">${esc(p[2])}</p>` +
      `<ul class="facts">${p[3].map(fact).join("")}</ul>`
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${esc(p[1])}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>` +
      `<ul class="more ex">${C.examples.map(x => `<li><button data-open="${x[0]}">${esc(x[1])}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
  S.dirty = true;
}
/* The state and what is open are one value in the address: #<proposed|family>, then /<panel> or /<mechanism>. */
function address(push) {
  const parts = [S.s !== 1 ? STATES[S.s] : "", S.open || ""].filter(Boolean);
  const url = parts.length ? "#" + parts.join("/") : location.pathname;
  push ? history.pushState(null, "", url) : history.replaceState(null, "", url);
}
function fromHash(first) {
  const parts = decodeURIComponent(location.hash.slice(1)).split("/");
  const s = STATES.indexOf(parts[0]) >= 0 ? STATES.indexOf(parts[0]) : 1;
  const rest = parts.find(x => C.panels.some(p => p[0] === x) || MK[x]);
  S.open = rest || null;
  if (first === true) {
    // The first view: with no address the dots start together and travel into their groups once the picture is seen.
    const travel = !still.matches && s === 1 && !location.hash;
    setState(s, { instant: !travel, from: travel ? S.L[0].P.map(q => ({ ...q })) : null, delay: 1e9 });
    if (travel) watchEntrance(); else S.t0 = -1e9;
  } else if (s !== S.s) setState(s);
  pane();
  place(performance.now());
}
function watchEntrance() {
  const go = () => { if (S.started) return; S.started = true; S.t0 = performance.now() + 650; S.dirty = true; };
  if (!("IntersectionObserver" in window)) return go();
  const io = new IntersectionObserver(es => { if (es.some(e => e.isIntersecting)) { io.disconnect(); go(); } }, { threshold: .3 });
  io.observe($("svg"));
}
const show = () => { if (narrow.matches) $("pane").scrollIntoView({ behavior: still.matches ? "auto" : "smooth", block: "start" }); };
function open(key) {
  const was = S.open;
  S.open = key || null;
  if (key && MK[key]) stopReplay();
  address(true);
  pane();
  place(performance.now());
  const to = $("pane").querySelector(key ? ".close" : `[data-open="${was}"]`);
  if (to) to.focus({ preventScroll: true });
  else if (!key) $("svg").focus({ preventScroll: true });
}
function choose(s) {
  if (s === S.s) return;
  setState(s);
  pane();
  address(false);
}

/* The picture's control: click a dot or its label to open it. The point is mapped into plate units. */
const svg = $("svg");
function nearest(e) {
  const mi = S.el.fg.getScreenCTM().inverse(), u = mi.a * e.clientX + mi.c * e.clientY + mi.e, v = mi.b * e.clientX + mi.d * e.clientY + mi.f;
  const now = performance.now(), g = S.g;
  let best = null, bd = Infinity;
  M.forEach(m => {
    const q = at(m.i, now), wl = q.la > .5 ? S.el["lb" + m.i].getComputedTextLength() + 18 : 0;
    const du = u < q.x - 10 ? q.x - 10 - u : u > q.x + 10 + wl ? u - q.x - 10 - wl : 0, dv = Math.abs(v - q.y);
    const d = du * du + dv * dv;
    if (d < bd && du < 8 && dv < (wl ? g.pitch * .55 : 14)) { bd = d; best = m; }
  });
  return best;
}
svg.addEventListener("pointermove", e => { if (e.pointerType === "mouse") svg.style.cursor = nearest(e) ? "pointer" : "default"; });
svg.addEventListener("click", e => { const m = nearest(e); if (m) { open(m.key); show(); } });
document.addEventListener("click", e => {
  const b = e.target.closest("[data-state]"), o = e.target.closest("[data-open]"), st = e.target.closest("[data-step]");
  if (b) choose(Number(b.dataset.state));
  if (o) { open(o.dataset.open); if (o.dataset.open) show(); }
  if (st) {
    const L = order(S.s), k = L.indexOf(MK[S.open]), next = L[(k + Number(st.dataset.step) + L.length) % L.length];
    open(next.key);
    $("pane").querySelector(`[data-step="${st.dataset.step}"]`).focus({ preventScroll: true });
  }
});
document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.key === "Escape" && S.open) open("");
  if ((e.key === "ArrowRight" || e.key === "ArrowLeft") && !/INPUT|TEXTAREA/.test(document.activeElement.tagName)) {
    choose(clamp(S.s + (e.key === "ArrowRight" ? 1 : -1), 0, 2));
  }
  if (e.key === "Enter" && document.activeElement === svg) {  // the first example
    e.preventDefault();
    open(C.examples[0][0]);
    show();
  }
});
addEventListener("hashchange", fromHash);
addEventListener("popstate", fromHash);
narrow.addEventListener("change", () => { build(); setState(S.s, { instant: true }); place(performance.now()); });
still.addEventListener("change", () => { if (still.matches) { stopReplay(); setState(S.s, { instant: true }); aim(0, 0); place(performance.now()); } });
const stage = $("stage");
stage.addEventListener("pointermove", e => {
  if (e.pointerType !== "mouse" || still.matches) return;
  const b = stage.getBoundingClientRect();
  V.tx = 2 * (e.clientX - b.left) / b.width - 1; V.ty = 2 * (e.clientY - b.top) / b.height - 1;
});
stage.addEventListener("pointerleave", () => { V.tx = V.ty = 0; });

$("switch").innerHTML = SNAME.map((n, k) => `<button data-state="${k}">${n}</button>`).join("");
$("problem").textContent = C.problem;
$("say").innerHTML = esc(C.line).replace(/(?<![\w-])(\d+(?:[.,]\d+)*)(?= held| were| stayed)/g, "<b>$1</b>");
build();
aim(0, 0);
fromHash(true);
if (!still.matches) {
  svg.classList.add("enter");
  setTimeout(() => svg.classList.remove("enter"), 2200);
}
requestAnimationFrame(frame);
</script>
</body>
</html>
"""

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's own picture,
# reduced. A glass slab with three short columns of dots: lit dots that hold, rings that were refuted, dashed rings left
# undecided, in round 13's proportions. They drift a little.
ICON = r"""(kit, t, tilt) => {
  const top = 2.5, k = Number(t) || 0;
  let out = kit.slab(44, 38, 5);
  const cols = [[-24, 6, "h"], [0, 7, "r"], [24, 4, "u"]];
  cols.forEach(([u, n, v], c) => {
    for (let j = 0; j < n; j++) {
      const w = -24 + 7.4 * j + .7 * Math.sin(k * .8 + j + c * 2), d = kit.at(u, w, top), x = d[0].toFixed(1), y = d[1].toFixed(1);
      out += v === "h" ? `<circle cx="${x}" cy="${y}" r="3.1" fill="${kit.token.blue}"/>`
        : `<circle cx="${x}" cy="${y}" r="2.7" fill="none" stroke="${kit.token.ink}" stroke-width="1.1"${v === "u" ? ' stroke-dasharray="1.6 1.4"' : ""}/>`;
    }
  });
  return out;
}"""

PAGE = PAGE.replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({
    "problem": PROBLEM, "line": LINE, "panels": PANELS, "examples": EXAMPLES, "families": FAMILIES, "counts": _c,
    "rows": ROWS, "tests": {k: [v[0], v[3] and v[3][6:9] + [v[3][4], v[3][5]], v[4], v[5]] for k, v in TESTS.items()},
}, ensure_ascii=False).replace("</", "<\\/"))

if __name__ == "__main__":  # run from the repository root
    rows, commit = _build()
    if sys.argv[1:] == ["--write"]:
        src = open(__file__).read()
        body = "[\n" + "".join("    " + repr(r) + ",\n" for r in rows) + "]"
        start = src.index("\nROWS = ") + 1
        end = start + len("ROWS = []") if src.startswith("ROWS = []", start) else src.index("\n]", start) + 2
        src = src[:start] + "ROWS = " + body + src[end:]
        start = src.index("\nCOMMIT = ") + 1
        src = src[:start] + "COMMIT = " + repr(commit) + src[src.index("  #", start):]
        open(__file__, "w").write(src)
        sys.exit(f"wrote {len(rows)} mechanisms, commit {commit}")
    for a, b in zip(ROWS, rows):
        assert a == b, f"ROWS differs from the record files at {b[0]}: run with --write"
    assert len(ROWS) == len(rows), f"ROWS has {len(ROWS)} mechanisms, the record {len(rows)}: run with --write"
    assert COMMIT == commit, f"the record files changed since commit {COMMIT} (now {commit}): run with --write"
    plans = json.load(open(FILES[2]))
    assert {r[0] for r in ROWS if r[2]} == {p["mechanism"] for p in plans}, "round 13's dots are not its plans"
    lenses = re.search(r"LENSES = \{(.*?)\}", open("studies/theory/lib/forecast.py").read(), re.S).group(1)
    assert sorted(re.findall(r'"(\w+)":', lenses)) == sorted(f[0] for f in FAMILIES), "FAMILIES differ from LENSES"
    c = COUNTS
    print(f"ROWS and COMMIT match the record files. Round 13: {c['held']} of {c['tested']} hold, {c['refuted']} refuted, "
          f"{c['undecided']} undecided; all rounds: {c['held_all']} of {c['tested_all']} hold.")
