# Direct test editvote (round-15/account-3/c2)

Written before the computation. Plan: `studies/theory/results/wide/round-15/synthesis_tests.md`, section
`round-15/account-3/c2`. Board: work-5ccea7 (idea work-4948a7).

## Claim

The 1.5x top-8 edit is RL's re-weighting of the base distribution, so its wrong answers split like RL's and its
vote over 4 on hard328 matches RL plain's vote over 4, not the base's vote.

## Statistic

100 * (edit votes right - RL plain votes right) / 328, in points. Edit = base + 1.5 x the top-8 RL-Math
directions, cue prompt.

## Rows

All 328 hard328 problems; attempt 0 of samples 0-3 in each run (RL plain and base have restarts; the restarts do
not count). Cap hits have no extracted answer and cast no vote. Grader: the stored v3 scores.

- edit: `studies/rlneurons/results/day1_3/hard328_top8x1.5_cue_s4-01/rows.jsonl`
- RL plain: `studies/rlneurons/results/day1_3/hard328_rl_plain_s4r2-01/rows.jsonl`
- null arm, base + cue: `studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl`

## Computation

The vote is `studies/rlneurons/analysis/day1_vote.vote` (plurality over extracted answers, grouped by
`R.agree` on v3-normalised answers), imported, not copied. Two tie rules:

1. Order-averaged (the plan's rule, primary): a tie among the largest groups is broken uniformly at random,
   scored as its exact expectation (`selector.tie_random`, the limit of the plan's 200 tie draws; the rule of
   result-f941b8).
2. Plain (stored order): the tie goes to the group seen first in sample order (the rule of result-95a4dc).

Per problem d_i = edit score - RL score. Statistic = 100 * mean(d_i). Paired bootstrap over the 328 problems,
10,000 resamples, numpy seed 0; the 90 % interval is the 5th to 95th percentile. The same for the null
(base + cue in place of the edit) and for edit minus base.

## Posted numbers the script must reproduce (it stops if not)

- Plain rule: edit 214, RL 221, base 192 of 328; edit minus RL -2.1 points (result-95a4dc, 95 % interval
  [-5.2, 0.6]).
- Order-averaged: RL 215.9, base 184.6 (result-f941b8, comment on result-818c20); edit minus RL +0.1 points
  [-2.3, 2.4] 95 % (result-f941b8). The edit's order-averaged count was not posted.

The posted numbers decide the point value; this test adds only the 90 % paired interval.

## Null and ranges (fixed in advance by the plan)

Null: a vote over the cued base's 4 attempt-0 samples against RL's vote (plain rule 192 - 221 = -8.8 points).
Ranges: account-3 [-5.0, 5.0], null [-14.0, -6.0].

## Verdict rule (engine 14)

On the primary (order-averaged) statistic: holds only if the 90 % interval lies wholly inside [-5.0, 5.0] and
n >= 50; refuted if the 90 % interval lies wholly outside [-5.0, 5.0]; otherwise undecided, with the n that would
decide (interval half-width scaled by sqrt(328 / n)). The plain-rule verdict is reported beside it. Where the value
falls relative to the null range [-14.0, -6.0] is reported.

## Outputs

`studies/theory/results/direct/editvote-01/`: `metrics.json`, `examples.json` (one problem the edit's vote wins
and RL's loses, one the reverse, with the real answers), `rows.json`.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.theory.analysis.direct_editvote
