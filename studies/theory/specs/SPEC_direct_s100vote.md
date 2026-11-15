# SPEC: direct test s100vote, the vote gain of RL step 100 (round-15/account-2/c2)

Board work-00e944 (idea work-4948a7). Theory round 15, plan `studies/theory/results/wide/round-15/synthesis_tests.md`,
section `round-15/account-2/c2`. Written and pushed before any step-100 vote was computed. Stored rows only: no GPU
job, no forward pass, no tokenizer.

## The claim

Account-2 says RL step 100 has learned only the opening (S2), not the lower slip rate. So its wrong answers scatter
like the cued base's, and a vote over its 4 samples gains as much over one sample as the cued base's vote does
(+7.1 points), not as little as final RL's (+2.8).

## Prior results checked

`tools/recall.py` and the board: result-6832a8 and result-fad48d give step 100 plain single-sample counts only
(418, 411, 422, 419 of 500); no posted result gives a vote over the step-100 samples. Nothing decides this test.

## Rows

All 500 MATH-500 problems, RL step 100 plain (`allenai/Olmo-3.1-7B-RL-Zero-Math` revision step_0100), T 1.0,
top-p 1.0, cap 16,384, grader v3 as written by run_cell (`score_v3`, `extracted_v3`):

- sample 0: `studies/rlneurons/results/ckptcue/s0100_plain-01/per_problem.json` (seed 45000000 + index)
- samples 1-3: `studies/rlneurons/results/ckptcue/s0100_plain_s123-01/rows.jsonl` (seeds 45010000, 45020000,
  45030000 + index; attempt 0; no restarts)

n = 500. The script asserts every (problem, sample) pair exists once and the per-sample counts equal 418/411/422/419.

## Statistic

Per problem i:

1. single_i = mean of the 4 samples' `score_v3`.
2. vote_i, order-averaged (deciding): the team's vote of result-f941b8, `selector.tie_random`, i.e. the plurality
   vote of `day1_vote.vote` (answers grouped by `rln4_lib.agree` on `norm_v3`; a row with no extracted answer casts no
   vote) with a uniformly random choice among the largest groups; this equals the mean over the 24 sample orders.
   The script asserts the equality with the 24-order mean on every problem.
3. vote_i, plain rule (reported, not deciding): `day1_vote.vote` in the stored order 0, 1, 2, 3 (a tie goes to the
   group seen first).

G = 100 * mean_i (vote_i - single_i), in percentage points (points of 500 divided by 5). 90 % interval: the 5th and
95th percentiles of G over 10,000 bootstrap resamples of the 500 problems (numpy default_rng(0)).

Rows that hit the cap but carry an extracted answer vote, as in the team's vote; the script reports how many there
are.

## Context (same code, stored rows, not deciding)

- Cued base: `studies/rlneurons/results/day1_3/math500_base_cue-01`, attempt 0 of samples 0-3. Plan's value +7.1.
- Final RL plain: `studies/rlneurons/results/day1_3/math500_rl-01`, attempt 0 of samples 0-3. Plan's value +2.8.

The script reproduces the posted order-averaged votes (base 448.2, RL 474.3, result-f941b8) before reporting.

## Null and ranges (fixed in advance by the plan)

- Null: step 100 already carries final RL's lower slip rate, so its vote gain equals final RL's own, +2.8 points
  (vote 474 vs mean single 460). Null range [1.0, 4.5].
- Account-2 range [5.0, 10.0].

## Verdict rule (engine 14)

- holds: the 90 % interval lies wholly inside [5.0, 10.0] and n >= 50.
- refuted: the 90 % interval lies wholly outside [5.0, 10.0].
- undecided otherwise; then state the n at which the interval half-width (scaling as 1/sqrt(n)) would fit inside or
  outside the range.

Also report where G falls relative to the null range [1.0, 4.5].

## Outputs

`studies/theory/results/direct/s100vote-01/`: `metrics.json` (G with 90 % interval, n, null value, plain-rule G,
context gains, vote and single totals, ties, cap hits), `examples.json` (one problem where the vote is right and the
mean single sample is lower, one where the vote is wrong and the mean single sample is higher, with the 4 extracted
answers), `rows.json`. Script `studies/theory/analysis/direct_s100vote.py`.
