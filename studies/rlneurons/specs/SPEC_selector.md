# SPEC selector: a label-free rule over the four stored samples (idea-664670, board work-3095f1)

Written 2026-11-15 before any rule was scored. Offline, no GPU.

## Question

The cued base's plurality vote over 4 samples has 446 of 500 on MATH-500 and the oracle pass@4 has 467. Does a rule that
sees no answer key pick the right sample on some of the 21 problems between them? One RL sample has 456.

## Inputs

Attempt 0 of samples 0 to 3 of the Day-1 #3 jobs (`run_cell --samples 4 --restarts 2`, T 1.0 / top-p 1.0, grader v3):
`runs/abaybektursun-1114-153825-208b/answers.jsonl` (base with cue) and `runs/abaybektursun-1114-183640-e828/answers.jsonl`
(RL plain). Fields used: `n_new`, `cap_hit`, `extracted_v3`, `mode_v3`, `text`, and two confidence values that `run_cell`
stored at generation: `answer_prob` (probability of the answer's tokens where the answer is stated; computed on the v1
extraction, absent when v1 found no answer) and `mean_logprob` (mean log-probability of all generated tokens). `score_v3`
is read only to score a rule's choice, never to make it.

## What the 21 problems look like (read before the rules were written)

Base, vote wrong and pass@4 right: 21. 15 are ties for first that the lowest-sample rule lost (6 with four different
answers, 3 with three, 3 with two after cap hits, 3 ties of 2 against 2); 6 are a wrong answer with 2 or 3 votes against
one right sample (50, 80, 232, 381, 385, 403; 50 and 403 are the two the vote broke against sample 0). In the 15 ties the
right sample is the shortest finished one in 7 (11, 20, 71, 94, 189, 303, 352) and not in 8 (39, 100, 284, 327, 396, 444,
466, 491). Several wrong samples carry a visible defect: the
prompt's template copied as the answer (`$Answer (48)$`, `the answer to the problem.`), two boxes for two solutions, text
that continues after the answer. RL: 8 such problems, 4 ties.

These rules were written after reading those 21, so their MATH-500 numbers are optimistic. The 328 is the clean test.

## Candidate rules (fixed list, 11 rules; the plain vote is the baseline)

Groups are those of `day1_vote.vote` (`rln4_lib.agree`). "Finished" = not a cap hit. Every remaining tie goes to the
lowest sample number.

| Rule | Procedure | Hypothesis | Refuted if |
|---|---|---|---|
| `tie_short` | plurality; a tie goes to the group holding the shortest finished sample | within a problem short chains are right more often (Hassid 2505.17813) | at most as many ties right as the lowest-sample rule |
| `tie_aprob` | plurality; a tie goes to the group with the highest `answer_prob` | a confident final statement marks a right answer | same |
| `tie_mlp` | plurality; a tie goes to the group with the highest `mean_logprob` | sequence likelihood marks a right answer | same (prior: 2507.18122 Table 1 says it does not) |
| `tie_clean` | plurality; a tie goes to the group with the most clean samples (finished, boxed, the last box in the final 200 characters) | defective endings mark wrong answers | same |
| `tie_restate` | plurality; a tie goes to the group whose answer string occurs most often in one of its samples' text | a restated answer was checked | same |
| `drop_cap` | plurality without cap-hit samples | a cap-hit sample's extracted answer is an intermediate value | not above the vote |
| `w_invlen` | each sample votes with weight 1 / `n_new` | a short sample outweighs two long ones | not above the vote |
| `w_aprob` | each sample votes with weight `answer_prob` (0 when absent) | confidence-weighted vote | not above the vote |
| `short1` | the shortest finished sample that has an answer | Hassid's short-1@k | not above the vote |
| `max_aprob` | the sample with the highest `answer_prob` | best-of-n by confidence | not above the vote (prior: below one sample) |
| `max_mlp` | the answered sample with the highest `mean_logprob` | best-of-n by likelihood | not above the vote |

## Selection protocol

1. No rule has a free parameter; the list above is closed. Rules tried = 11.
2. Five folds by position in the sorted problem list (position mod 5). For each fold, the rule with the most right on the
   other four folds is chosen (the vote included; a draw keeps the earlier rule in the list, the vote first) and scored on
   the held-out fold. The sum over the five folds is the row `cv_pick`: the honest estimate of "choose the best of 12".
3. Decision: a rule goes to the 328 only if `cv_pick` on the base is above the vote and the paired 95 % interval of the
   chosen rule minus the vote excludes 0. Otherwise the result is null and nothing is scored on the 328.
4. RL gets the same rules and the same protocol on its own four samples.
5. Reported per rule and model: right of 500, Wilson 95 %, paired bootstrap against the vote (5,000 resamples, seed 0),
   problems changed (wrong to right, right to wrong), tokens per problem (all four samples; for `short1` also 4 x the
   shortest finished sample, the cost if the other three were stopped when the first finishes).

## Instrument test (`analysis/selector_test.py`)

Planted rows where each rule must pick a known sample, including cases where it must be wrong (the shortest sample is the
wrong one; the confident sample is the wrong one). A planted oracle rule must come out of `cv_pick` with pass@4, and a
rule that is best only on one fold must not be chosen for that fold.

## The 328

sameraslan's four-sample rows (work-140e13, result-1dedfe) are in his Modal Volume; git has only per-problem 0/1 vectors
and `n_new` (`results/day1_3/hard328_base_cue_s4r0-01/readout.json`, `results/day1_length_rules/hard328_base-01/
per_problem.tsv` on branch `claude/swarm-literature-review-60a281`), not the extracted answers or the text. A rule that
passes step 3 is reported with the command to score it once those `answers.jsonl` are copied; they are not rerun here.
