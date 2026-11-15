# SPEC axis: one axis or several? (board idea-1c8b73, work-1aa34c)

Written before any overlap, fit or union was computed. No GPU.

## Question

Do the partial routes toward the RL model (cue, weight blend theta, other-reward RL checkpoints, Code-RL, top-8 singular
directions, Think-SFT, solved examples in context, vote) fix the same MATH-500 problems or different ones? If every arm moves
problems along one difficulty axis, a stack of two arms gains only what a second sample of one arm gains. If they fix different
problems, a stack should beat each arm alone and we name the stack.

## Data

One 0/1 vector per arm, grader v3 (`score_v3` as written by `run_cell`), T 1.0 / top-p 1.0, one sample per problem, attempt 0.
MATH-500 (n = 500) is the main set; hard328 (n = 328) is analysed separately. An arm enters only with its job id, config and
grader version; its right count must equal the `correct_v3` of its committed `metrics.json` (or the committed readout).
Sources: committed `rows.jsonl` / `per_problem.json` / selector `readout.json`, and for the cells whose raw rows are not
committed, `runs/<job id>/answers.jsonl` (`uv run tools/gpu.py get <job id>`); `analysis/axis.py --extract` writes the vectors
and a manifest with path and sha256 to `results/axis/<set>-01/`. Excluded arms are listed with the reason in the manifest.

Independent arms: single samples (the four stored samples of base + cue and of RL plain count as four arms each).
Derived arms (vote over 4, tie_short) are functions of the base samples: used in the unions and the floor, not in the item
model or the overlap null.

## Definitions

- Reference: base + cue, sample 0 (405 of 500). "A fixes problem i": reference wrong, A right.
- Rest score of a problem for a pair (A, B): the fraction of the other independent arms that are right on it (arms of the same
  model family as A or B stay in; A and B do not). Problems are put in 8 strata by rest score (equal-count bins).
- Stratified null for a pair: B's outcomes permuted among the problems of each stratum, 2,000 permutations, seed 0. It keeps
  both arms' accuracy at every difficulty level and removes any item-level relation beyond difficulty. This is the
  Mantel-Haenszel test of item response theory with the rest score as the difficulty measure.
- Same-config pairs: the 6 pairs among the four base + cue samples and the 6 among the four RL samples (different seeds,
  same config), and the same-seed reruns (first 50 / 100 MATH-500 problems of base + cue, hard328 base + cue sample 0 by a
  second person). They show what two samples of ONE arm do under every statistic below: the noise floor.
- Excess union of (A, B): observed number right under A or B, minus the mean of the stratified null, in problems.
  z = excess / null sd. Positive: A and B fail on different problems more than difficulty explains (complementary).
  Negative: they fail on the same problems (a shared sub-axis).

## Hypotheses and the observations that refute them

- H1 (one axis). For pairs of different arms, the excess union is inside the range of the same-config pairs.
  Refuted if any pre-named candidate pair (below) has z > 3 and an excess of at least 5 problems (1.0 point), with the 12
  same-config pairs showing no such value. If same-config pairs themselves show |z| > 3, the null is miscalibrated and no
  verdict is drawn from it.
- H2 (item model). A Rasch model, logit P(arm j right on problem i) = a_j + b_i, predicts held-out cells as well as the
  model with one bilinear term added, a_j + b_i + u_i v_j ("2-D"). Refuted if the 2-D held-out log-likelihood gain per cell
  (5-fold over cells, same folds, ridge strength chosen per model from the same grid) exceeds the 95th percentile of the gain
  on 20 data sets simulated from the fitted Rasch model. Also reported: the same gain on data with arm labels shuffled within
  each problem (no arm structure at all), as the floor of the gain.
- H3 (stack bound). For every candidate stack the oracle union is at most 5 problems above the stratified-null union, and no
  further above the best single arm than the union of two RL samples is above one RL sample. Refuted by a larger excess.
- H4 (floor). Problems no arm solves, RL's vote included, are fewer than 10 of 500; problems only RL arms (RL plain samples,
  RL cue, RL vote) solve are fewer than 5. Refuted by larger counts (then RL has problems of its own that no route reaches).
- Expectation written here so it can be wrong: prompt format is a second axis. Plain-prompt arms of weak models fail by not
  finishing, cue arms do not; if the 2-D term is detected, its arm loadings v_j should split plain from cue arms. If instead
  they split by something else (reward type, weight edit vs context), that is the finding.

## Candidate stacks, named before computing

Pairs of single-sample arms: theta0.5 cue + Think-SFT cue; theta0.5 cue + RL-written shots; Think-SFT cue + RL-written shots;
theta0.25 cue + Think-SFT cue; Code-RL 3.1 cue + Think-SFT cue; Math 3.0 cue + Think-SFT cue; theta0.5 cue + Code-RL 3.1 cue;
each of these arms + base vote over 4 (oracle over the vote's answer and the arm's answer); each + RL plain sample 0 (does the
route still hold problems RL misses).

## Instrument checks (planted data, `analysis/axis_test.py`)

1. 30 arms x 500 problems generated from one axis (Rasch): the 2-D gain must be inside the simulated null, and pair z-scores
   must be standard normal (|mean| < 0.3, fewer than 2 % beyond |z| = 3).
2. A planted second axis (half the arms gain 1.5 logits on a random 30 % of problems, the other half on a disjoint 30 %): the
   2-D gain must exceed the null's 95th percentile, cross-group pairs must have mean z > 3, and the loadings must separate the
   two groups.
3. Two arms that are the same vector with 0 flips: excess union must be strongly negative.

## Verdict rule

- "One axis": H1 and H3 hold. Report the largest candidate excess X: stacking is predicted to add less than X points beyond
  what a second sample of the best arm adds; do not run a stack.
- "Complementary": a candidate pair refutes H1/H3. Name the pair and the exact GPU job that tests the stack.
- A union is an oracle (it needs the answer key to choose): it is the upper bound of any selector over the two answers,
  not a method. It is always stated as such.

## Limits known before the run

One sample per arm for all arms except base + cue and RL plain: a pair's excess mixes sampling noise into both members, which
the null accounts for only through the strata. Shots arms have n = 497 (problems 0, 1, 2 are the examples). hard328 has no
second sample of any arm except one same-seed rerun.

## Amendments after the planted checks, before any real pair or fit was computed

1. Null. With 8 equal-count strata the stratified null failed check 1 (one planted axis: pair z mean -0.98, 2.1 % beyond
   |z| = 3): the rest score measures difficulty with error, so the two arms stay positively related inside a stratum. Now: one
   stratum per distinct rest score, exact hypergeometric moments instead of 2,000 permutations, and the remaining bias (about
   -1.5 problems) and the sd are taken from 200 matrices drawn from the fitted Rasch model and passed through the same
   statistic. Check 1 then gives z mean 0.09, sd 0.94, 0.2 % beyond 3. Pairs with a derived arm (vote) cannot be simulated
   from 0/1 data and keep the uncorrected null: their excess is biased low by about 1.5 problems.
2. Power. A planted second axis of 1.5 logits on 30 % of the problems is detected by the item model (2-D gain 0.0032 nats per
   cell against a null at 0) and gives cross-group pairs a mean excess of only 1.8 problems (z 0.64); 4 logits gives 4.8
   problems (z 1.94). So no single pair of 500-problem vectors can reach the z > 3 of H1 for a realistic effect. H1 is judged
   instead by (a) the pooled contrast: under one axis the same-config pairs and the different-arm pairs both have mean z near
   0; under several axes the same-config pairs are more alike (mean z below the different-arm pairs by more than 1), and
   (b) for each candidate pair the upper bound excess + 2 sd, in problems, which is the X of the verdict.
3. 2-D detection needs a gain above the null's 95th percentile and above 1e-4 nats per cell (at the strongest ridge the 2-D
   model equals the 1-D model and both gains are 0 to 5 decimals). The ridge grid gained the value 10.
4. Check 2 asserts what the instrument can do: item model detects, loadings separate the groups, cross-group mean z exceeds
   within-group mean z by more than 1; at 4 logits cross-group mean z > 1.5 and mean excess > 3 problems.
