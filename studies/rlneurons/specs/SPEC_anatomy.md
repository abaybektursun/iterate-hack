# SPEC anatomy: is the RL gain a reliability shift or new problems? (idea-9e3dff, board work-5b7270)

Written 2026-11-15 before the analysis script existed. Offline, no GPU. What was known when this was written: the Day-1 #3
rows (base with cue 1,642 right of 2,000 samples, RL 1,840, pass@4 467 and 482) and a planner's unverified count ("86 of the
198-sample gap sits in problems the base solves 3/4 and RL 4/4; base errors 250 finished-wrong, 89 cap hits, 19 no answer").

## Question

RL plain has 198 more right samples than the cued base on MATH-500 (4 samples per problem, T 1.0 / top-p 1.0, grader v3).
Is that gain a reliability shift (problems the base solves in some samples, RL in all) or new problems (problems the base
does not solve)?

## Inputs

Attempt 0 of samples 0 to 3, both models: `results/day1_3/math500_base_cue-01/rows.jsonl` and `math500_rl-01/rows.jsonl`
(scores, tokens, cap hits) and `runs/abaybektursun-1114-153825-208b/answers.jsonl`, `runs/abaybektursun-1114-183640-e828/
answers.jsonl` (text). Subject, level and the reference solution: `data/anatomy/math500_meta.json` (HuggingFaceH4/MATH-500,
same order and unique_id as `data/rln4/math500.json`, which carries neither level nor solution).

## Definitions

- b_i, r_i: right samples of 4 on problem i for the base and for RL. Gap = sum_i (r_i - b_i), in samples.
- Share of the gap in a cell (b, r) = n(b, r) (r - b) / gap. Cells with r < b have a negative share; shares sum to 1.
- Error type of a wrong sample: cap hit (16,384 tokens); no answer (finished, grader v3 extracted nothing); finished-wrong.

## What sampling noise alone predicts (computed before reading the data)

Four samples cannot tell a problem with solve probability 0.2 from one with 0: P(0 of 4 | p = 0.2) = 0.41. So the cells of
the joint table are not classes of problems. Two nulls and two checks:

1. Homogeneous null: every problem has the model's mean solve probability (base 0.821, RL 0.920), samples independent.
   Then b_i is Binomial(4, 0.821): 0/4 0.1 %, 1/4 1.9 %, 2/4 13.0 %, 3/4 39.6 %, 4/4 45.4 %, and the (3, 4) cell holds
   500 x 0.396 x 0.716 = 142 problems. Under this null there are no "never solved" problems and split halves are
   uncorrelated. The script prints this expected table next to the observed one.
2. Held-out sample (the main instrument): class a problem by 3 of its samples (j right of 3), score the fourth; average over
   the 4 choices of the held-out sample. The held-out rate is an unbiased estimate of the solve probability of the problems
   in that class, free of the selection that makes "0 of 4" look like "never". The same for halves: class by samples 0-1,
   score samples 2-3, averaged over the 3 ways to pair the samples and both directions.
3. Held-out gap decomposition: class problems by the base's k of 2 on one half; on the other half count base right, RL
   right and their difference. The shares of this held-out gap per class are the answer to the question; the in-sample cell
   shares of the 5 x 5 table are reported beside them and are expected to overstate the k = 0 class (selection on noise).

## Hypotheses, each with the observation that refutes it

- H1, reliability shift: most of the gap sits in problems the base solves in some samples. Refuted if under 30 % of the
  in-sample gap sits in problems with b >= 2, or if under 30 % of the held-out gap sits in the classes with base k >= 1 of 2.
- H2, new problems: most of the gap sits in problems the base does not solve. Refuted if under 30 % of the in-sample gap
  sits in b = 0, or if the base's held-out solve rate on its "0 of 3" class is above 25 % (then that class is not "never").
- H3, real bimodality in the base: the base's per-problem solve probability is spread out, not one value. Refuted if the
  held-out rate after 0 of 3 is within 10 points of the rate after 3 of 3 (the homogeneous null predicts equal rates).
- H4, the gap is in hard problems: the gap per problem rises with level. Refuted if level 5 holds a share of the gap no
  larger than its share of problems (134 of 500 = 27 %), by a bootstrap interval over problems.
- H5, cap hits are a separate failure: on problems where a base sample hits the cap, RL finishes and is right at the same
  rate as on other base-wrong problems. Refuted if RL's right rate on the same problems differs by over 15 points between
  base cap-hit samples and base finished-wrong samples.
- H6, slips dominate the base's finished-wrong answers: the judge labels over half of them "computation slip". Refuted if
  under a third are slips. Prior (result-5e17a6, one reader, 65 RL-only problems of one sample): 14 slips, 14 misread,
  9 wrong method among the 37 with a wrong finished answer.

## Analyses (`analysis/anatomy.py`, results in `results/anatomy/math500-01/`)

a. 5 x 5 joint table of b and r, share of the gap per cell, the homogeneous-null table, the held-out tables above.
   `pool_k_le3.json`: every problem with b <= 3, with b and r (for the prefix hand-off study).
b. Gap by subject (7) and level (5): problems, base and RL right samples, gap per problem with a bootstrap interval over
   problems (5,000 resamples, seed 0), share of the gap against share of problems.
c. Base error types, and for each wrong base sample what RL does on the same problem (RL's 4 samples: right, finished-wrong,
   cap hit, no answer). The same in reverse for RL's wrong samples.
d. Tokens: right against wrong samples per model; within problems that have both right and wrong samples of one model, the
   paired difference in mean tokens (wrong minus right), cap hits included and excluded.
e. Where a wrong sample leaves its right sibling (base problems with 1 <= b <= 3, finished-wrong samples only). Proxy,
   fixed here: the first number in the wrong sample (a digit string of 2 or more characters, or a decimal) that occurs in no
   right sibling of the same problem and not in the problem statement; its character offset over the length of the wrong
   sample is the divergence position. Control for the proxy: a right sample scored against its right siblings the same way
   (a number absent from the siblings also appears in right answers, so the wrong-sample position must be read against this).
   Check: 15 pairs read by hand, the reader blind to the proxy's position, giving the first wrong step as a quote; the proxy
   counts as confirmed on a pair if it is within 15 % of the answer's length of the quoted step. The proxy is reported as
   usable only if 10 of 15 are confirmed.

## Slip against wrong plan (`analysis/anatomy_judge.py`, results in `results/anatomy/judge-01/`)

Items: 60 finished-wrong base samples and 30 finished-wrong RL samples, drawn at random (seed 0, at most one per problem per
model), plus 30 controls. The judge sees the problem, the gold answer, the reference solution, the answer under judgment and,
when one exists, the shortest right sample of the same model on the same problem. It does not see which model wrote the
answer. Labels (one per item):

- `slip`: the method would give the gold answer; an arithmetic, algebra, sign, counting or copying error changes the result.
- `wrong_plan`: the method or the concept is wrong, or the solution is abandoned or guessed; carried out without error it
  would still not give the gold answer.
- `misread`: the answer solves a different problem than the one stated (a condition dropped or changed, the wrong quantity
  reported).
- `format`: the work reaches the gold value; the final stated answer differs in form or is garbled.
- `mismatch`: the answer is about a different problem altogether.
- `unclear`.

The judge also quotes the first wrong step; its character offset gives a second measurement for analysis e.

Controls (the instrument is broken until these come out right): 15 shuffled pairs (a finished answer to another problem;
must be `mismatch`, pass at 13 of 15) and 15 planted slips (a right sample whose last arithmetic step `a op b = c` has c
equal to the final answer; c is replaced by a wrong value from that step to the end; must be `slip`, pass at 12 of 15).
Two independent passes over all 120 items, in different random batches; agreement = share of items with the same label and
Cohen's kappa, on the 90 real items. A share is reported per pass and for the items where both passes agree.

Judge backend: AGENTS.md Compute rule 7 sends plain LLM inference to a hosted provider. The only provider code in the repo
is the OpenAI call of `studies/basins/analysis/swarm_judge.py`; the `OPENAI_API_KEY` on this machine is rejected by the API
(invalid key) and no key file exists. So the judges are Claude Code subagents (the agent's own model) with the rubric above
as a fixed written prompt; no GPU is used. This is stated with the result.

## Limits known in advance

- Four samples: the latent solve probability of one problem is not measured, only class means.
- One judge model, the same family as the agent; a second model family has not read the labels.
- The judge study covers finished-wrong answers only; cap hits and no-answer samples are counted in c, not labeled.
