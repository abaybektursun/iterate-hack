# SPEC ordervote: the vote headlines as an expectation over the tie-break

Board idea-49a7af, work-1621ff. Branch `ordervote` (main is frozen). Laptop, committed rows only, no GPU, no new samples.
Written and pushed before any contrast is computed.

## Problem

`analysis/day1_vote.py` `vote` gives a tie for first to the group seen first in sample order. The posted votes over 4 use the
one stored order. result-3e4a54 (branch `tieshort`) showed that this order is a lucky one for some models: on hard328 RL's
posted vote is 221 and its mean over the 24 orders of the 4 samples is 215.9 (2 to 13 of its 64 ties right; stored 12); the
cued base 192 against 184.6 (5 to 17 of 85; stored 17, the best order); Think-SFT 241 against 238.9 (16 ties). So the posted
contrasts under the vote (Think-SFT minus RL +6.1 points [3.0, 9.5]; RL minus base 8.8 [5.2, 12.8]; the shares of the gap
closed, e.g. 169 % [128, 250]) were computed in one order with unequal luck.

## What is computed

Score of a problem: its probability of being right under a uniformly random choice among the largest answer groups
(`analysis/selector.py` `tie_random`, already on main, reused unchanged): a number in [0, 1].

1. For every posted vote over 4: the posted value (stored order, `day1_vote.vote`), (a) the mean over the 24 orders of the 4
   samples, (b) the exact expectation (`tie_random`), the minimum and maximum over the 24 orders, the number of ties.
   Cells: base + cue, RL plain, Think-SFT + cue on MATH-500, hard328, fresh2026 (stored 16,384 draws); the vote after restart
   where restart rows exist (base and RL on hard328 and MATH-500); the mixed votes of the configuration table (expectation
   per combination, since a mix of 8 has 40,320 orders); the 1.5x top-8 edit, four samples on hard328 (214); the Think-SFT
   votes of result-dd26fe at cap 32,768 and cut at 16,384 (244 / 238, 75 / 73).
2. (a) against (b). In principle they are identical: tied groups have the same size, so each is equally likely to hold the
   earliest sample of a random order. This needs two things of the rows: the grouping does not depend on the order
   (`rln4_lib.agree` behaves as an equivalence on the answers of a problem) and all members of a group have the same score.
   The script reports the largest per-problem difference and names each problem where they differ.
3. Contrasts on the per-problem expected scores, paired bootstrap over problems (`n13_score.paired_bootstrap`, 5,000
   resamples, seed 0), each next to its posted stored-order value: Think-SFT minus RL, RL minus base, Think-SFT minus base on
   each set; vote after restart, RL minus base; the mixes and the edit against RL and the base; the cap contrasts of
   result-dd26fe (32,768 minus the same answers cut at 16,384; Think-SFT cut at 16,384 minus RL's stored 16,384 vote = the
   same-cap contrast of the audit comment; 32,768 minus RL's 16,384 vote, marked unequal caps). RL and the base have no
   4-sample rows at 32,768 (one sample each, `results/cap32/rows-0{1,2}/`), so no same-cap vote contrast at 32,768 exists.
4. Share of the base-to-RL gap closed under the vote, (x - base) / (RL - base), for every vote-family row of
   `results/table/hard328-02/table.json`: numerator and both denominators as means over the 24 orders (mixes: expectation),
   interval = percentile interval of the ratio over the table's resamples (`config_table.share`, `idx_matrix`). Posted shares
   are read from `table.json` and must be reproduced in the stored order first.

## Predictions (written before computing)

From the three known order means: Think-SFT minus RL on hard328 = (238.9 - 215.9) / 328 = +7.0 points; RL minus base =
(215.9 - 184.6) / 328 = +9.5 points. Refuted if either is outside +-1 point (these two are near-arithmetic; the open part is
below).

- P1. No conclusion flips: every contrast whose posted interval excludes 0 keeps an interval that excludes 0 on the same
  side. Refuted by one flip.
- P2. Think-SFT's share of the gap closed under the vote stays near its posted 169 %: the numerator and the denominator both
  grow, (238.9 - 184.6) / (215.9 - 184.6) = 173 %. Predicted 165 to 180 %, with an interval narrower than [128, 250] because
  the denominator is larger. Refuted outside 165 to 180 %.
- P3. The best rule on the untrained base (vote after restart, ties to the shortest, posted 24 % [0, 50]) rises, because the
  base's plain vote, the zero of the scale, drops by 7.4 problems: predicted 35 to 55 %. Refuted outside.
- P4. No posted contrast moves by more than its interval's half-width. Refuted by one that does.
- P5. fresh2026 and MATH-500 move by less than 1.5 points in every contrast (order means 75.5 / 55.8 / 38.8 and
  480.8 / 474.3 / 448.2 are within 1.2 and 2.2 problems of the posted votes).

## Checks, before any contrast

- Stored order reproduces every posted vote exactly: 241 / 221 / 192 (hard328), 481 / 474 / 446 (MATH-500), 75 / 57 / 38
  (fresh2026), after restart 224 / 195 and 475 / 450, cap 32,768 244 / 238 and 75 / 73, the edit 214, the mixes 228.1, 207.6,
  220.8, 239.0, 238.0, and the posted shares of `table.json`. The script stops otherwise.
- Order means reproduce result-3e4a54: 238.9 / 215.9 / 184.6, 75.5 / 55.8 / 38.8, 480.8 / 474.3 / 448.2.
- Posted contrasts reproduce in the stored order (6.1 [3.0, 9.5]; 8.8 [5.2, 12.8]; fresh 13.2 [7.4, 19.1], 27.2
  [19.9, 35.3], 14.0 [8.1, 19.9] with the draws of `fresh_read.py` as in `config_table.fresh`).
- Planted (`analysis/ordervote_test.py`): a set with no ties gives identical stored, 24-order and expected values; a set
  where every problem is a two-way tie with one right group gives exactly half in (a) and (b), while the stored order gives
  all or none.

## Instrument rule

`day1_vote.vote` is not changed: posted numbers depend on it. The order-averaged scorer is `selector.tie_random`, which is on
main; nothing is cherry-picked from `tieshort` and no file is copied. The chart keeps the posted stored-order values: this
result has no `score:` line.

## Outputs

`analysis/ordervote.py`, `analysis/ordervote_test.py`; `results/ordervote/{hard328,fresh2026,math500}-01/`: `run.json`,
`readout.json` (cells, contrasts, shares, per-problem expected scores), `table.md`, `examples.json` (a tied problem with its
four answers where the stored order is right and another order is wrong). README section "Vote headlines averaged over the
tie-break".

Not restated: votes whose rows are not committed (the 1.5x edit on fresh2026, 53 of 136: `results/mixvote/fresh2026_top8x1.5-01/`
has no rows), votes over other numbers of samples (M(2) over 3, 246; `votek`), and the sequential rules, which were already
posted as means over the 24 orders.
