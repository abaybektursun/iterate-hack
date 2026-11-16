# Direct test r17a1c2 (theory round 17, round-17/account-1/c2)

Written before any number is computed. Plan: `studies/theory/results/wide/round-17/synthesis_tests.md`, section
`## round-17/account-1/c2`.

## Claim

On MATH-500 the 1.5x top-8 edit is RL's own low-rank change (S1). One sample of the edit with the cue (accuracy 0.940)
follows RL's 4-sample per-problem rate more closely than one sample of Think-SFT with the cue (accuracy 0.920-0.940,
averaged over its 4 single samples). The account puts the gap at 0.02-0.54.

## Statistic

D2 = Pearson r(edit single-sample right, RL 4-sample rate) - mean over s=0..3 of Pearson r(Think-SFT sample s right,
RL 4-sample rate), across MATH-500 problems (correlation difference, unitless).

## Cells (set math500, TEST half only)

- edit: `rlneurons/xreward/dial15_math500-01` (one row per problem)
- RL: `rlneurons/day1_3/math500_rl-01` (attempt 0, samples 0-3)
- Think-SFT: `rlneurons/thinkvote/math500_sft1_cue_s4-01` (attempt 0, samples 0-3, used one sample at a time)
- null only: `rlneurons/day1_3/math500_base_cue-01` (attempt 0, samples 0-3)

Every cell is loaded with `rows.load("math500", cell, "test")`. Never the explore half, never the raw files.
Problems: present in all three main cells (edit row; RL samples 0-3; Think-SFT samples 0-3). n counts problems
(planned 250).

## Adversary's value (computed first, on the test half)

1) Problems as above. 2) rate_RL(p) = mean score_v3 of RL attempt-0 samples 0-3. 3) r1 = mean over the 6 pairs (a<b)
of RL samples 0-3 of Pearson r(score_v3 of sample a, score_v3 of sample b) across problems. 4) clone =
2*r1/sqrt(1+3*r1). 5) ct = (1/4)*sum_s Pearson r(Think-SFT sample s score_v3, rate_RL). 6) Adversary value =
clone - ct. Explore value 0.069.

## Computation

1) rate_RL(p) = mean score_v3 of RL attempt-0 samples 0-3. 2) e(p) = edit score_v3 (0/1). 3) t_s(p) = Think-SFT sample
s score_v3, s = 0..3. 4) D2 = corr(e, rate_RL) - (1/4) * sum_s corr(t_s, rate_RL), Pearson over problems.
5) 90 % interval: 2000 bootstrap resamples of problem ids with replacement (numpy default_rng(17)), recompute D2,
5th and 95th percentiles. A resample where any correlation is undefined (a constant vector) is skipped and counted.

## Null (accuracy alone, reported, cheap)

Fit the least-squares line corr ~ accuracy over the 8 single non-edit samples (cued base samples 0-3 of
`rlneurons/day1_3/math500_base_cue-01` and Think-SFT samples 0-3; each corr = Pearson r of that sample's score_v3 with
rate_RL), predict it at the edit's accuracy, subtract Think-SFT's mean correlation. Explore value 0.007.

## Ranges (fixed in the plan)

- account-1 (round-17/account-1/c2): [0.02, 0.54]
- null: [-0.2, 0.015]

## Verdict rule (verdict16)

Holds only if the 90 % interval lies wholly inside [0.02, 0.54], n >= 50 and the interval excludes the adversary's
test value; inside the range but containing the adversary's value: not separated; wholly outside the range: refuted;
else undecided.

## Outputs

`studies/theory/results/direct/r17a1c2-01/`: `run.json`, `metrics.json`, `examples.json` (one problem where edit and
RL agree, one where they disagree, with raw rows), `rows.json`. Script: `studies/theory/analysis/direct_r17a1c2.py`.
