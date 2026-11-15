# SPEC: direct test of round-15/account-2/c3 (edit0of4-01)

Board work-a8b82d (idea work-4948a7). Written before the statistic was computed. Stored rows only: no GPU job, no
forward pass. Plan: `studies/theory/results/wide/round-15/synthesis_tests.md`, section `round-15/account-2/c3` (entry
of the same name in `synthesis_tests.json`; context `account-2.json`).

## The claim (from the plan)

The 1.5x top-8 edit is a weight change that lowers the slip rate the way RL does, so on hard328 problems where the cued
base has no right answer in its 4 attempt-0 samples, the edit is right per sample as often as RL plain: edit rate minus
RL rate lies in [-0.08, 0.08]. If the edit were only a resample of the base, it would sit near the base's own fresh rate
there, about 0.2 below RL.

## Statistic

D = E - R: mean over the selected problems of (edit right of 4 / 4 - RL plain right of 4 / 4), in probability units.

## Rows

Selection (same rule as the judge's test d1, `SPEC_direct_editreach.md` on branch syn-editreach): hard328 problems with 0
right (grader v3, `score_v3`) among the cued base's attempt-0 samples 0-3 in
`studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl`; restarts (attempt > 0) do not enter the
selection. On these problems:

- edit: samples 0-3 (all attempt 0) of `day1_3/hard328_top8x1.5_cue_s4-01/rows.jsonl` (job abaybektursun-1115-055641-b417);
- RL plain: attempt-0 samples 0-3 of `day1_3/hard328_rl_plain_s4r2-01/rows.jsonl` (job abaybektursun-1114-200505-5ff2).

A problem is dropped if any of its 8 edit/RL rows is missing. The plan expects n of about 110.

## Computation

1. Select the problems as above.
2. Per problem: e = right edit samples / 4, r = right RL attempt-0 samples / 4 (`score_v3`; a cap hit counts as wrong
   since it has no extracted answer, as stored).
3. E, R = means over problems; D = E - R.
4. 90 % interval: paired bootstrap over problems, 10,000 resamples (numpy default_rng(0)), 5th and 95th percentiles of D.

## Null value (same rows)

The edit as a base resample: its rate equals the cued base's own fresh-sample rate. Per problem, b = right / count over
the base's fresh samples on that problem:

- every restart row (attempt 1 or 2, any sample) of `hard328_base_cue_s4r2-01` (a different seed, so fresh);
- the cap32 base-cue sample (`studies/rlneurons/results/cap32/rows-02/base_cue.jsonl`, job cap32_base_cue_joined, max
  32,768 tokens) scored at a 16,384-token cut: right only if `score_v3` is 1, `n_new` <= 16,384 and not `cap_hit`. It
  shares the seed of s4r2 sample 0, so it enters only if its full text (from
  `../iterate-hack-shots/runs/cap32_base_cue_joined/answers.jsonl`) differs from each of the problem's four s4r2
  attempt-0 texts (`runs/abaybektursun-1114-200457-e8e6/answers.jsonl`, not in git).

Null value D0 = mean of (b - r) over the selected problems that have at least one fresh base sample, with its own 90 %
bootstrap interval. Restarts exist only after a cap hit, so b leans toward problems where the base runs long; this is
stated as a caveat, not corrected.

## Comparison with d1

Also report E and R on the d1 subset (problems whose cap32 sample is fresh, as d1 drops the others), so the two tests'
E and R can be compared. D on all selected problems is the statistic for the verdict.

## Frozen ranges (from the plan)

- account-2: [-0.08, 0.08]
- null: [-0.35, -0.12]

## Verdict rule (engine 14)

Holds only if the 90 % interval of D lies wholly inside account-2's range and n >= 50; refuted if the 90 % interval lies
wholly outside it; otherwise undecided (state the n that would decide, scaling the interval width by 1/sqrt(n)). Also
report where D falls relative to the null range.

## Instrument checks

Each rows.jsonl reproduces its metrics.json right count per attempt-0 sample; a selection fed the edit's rows in place of
the base's must not give the same problem set.

## Outputs

`studies/theory/results/direct/edit0of4-01/`: `metrics.json`, `examples.json` (one edit row scored right and one wrong on
the selected problems, real input and output), `rows.json`. Script: `studies/theory/analysis/direct_edit0of4.py`.
