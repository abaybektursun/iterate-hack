# Direct test diffmix-01: round-09/grader-m04 (theory round 14, carried plan)

Plan: studies/theory/results/wide/round-14/jobs/plan-round-09-grader-m04.json (copied here; written before computing).

## Claim

Within MATH-500, the base's plain prompt keeps a smaller share of the cued base's right count on harder problems:
plain-right / cue-right is lower on levels 4-5 than on levels 1-2, by more than a second cued sample's ratio falls
over the same strata.

## Files and rows

- studies/rlneurons/results/rln4/t1_t3_items-01/per_problem.json: 500 rows; `t3_right` (base, plain, T 1.0) and
  `t1_right` (base, cue, T 1.0), grader v3. Check totals T3 224, T1 410.
- studies/rlneurons/data/anatomy/math500_meta.json: `rows`, 500 entries with `index`, `unique_id`, `level` (1-5).
- studies/rlneurons/data/rln4/math500.json: 500 problems with `index`, `unique_id` (the order T1/T3 used).
- studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl: base, cue, T 1.0, 4 samples per problem, grader v3
  (`score_v3`), 2,137 rows including restart attempts.

## Computation

1. Load per_problem.json; assert 500 rows, sum t3_right = 224, sum t1_right = 410.
2. per_problem.json has no unique_id, so join on `problem_index` = meta `index`; assert meta `unique_id` equals
   data/rln4/math500.json `unique_id` at every index (500 of 500).
3. Strata by level only: E = levels 1-2 (133 problems), H = levels 4-5 (262 problems); level 3 left out. Each stratum
   needs >= 50 T1-right problems, else undecided.
4. rho_s = (T3-right count in s) / (T1-right count in s); D_plain = rho_H - rho_E.
5. Null C2: day1_3 rows with sample = 0 and attempt = 0 (the first attempt, no restart, so it is one plain sample like
   T1; its total must reproduce readout.json each_sample.single_right[0] = 405). C2 is not the same generation as T1:
   it agrees with T1 on 441 of 500 problems (checked before computing), so sample 0 is used, as the plan says.
   rho'_s = (C2-right in s) / (T1-right in s); D_null = rho'_H - rho'_E.
6. Statistic: Delta = D_plain - D_null.
7. 90 % interval: paired bootstrap over problems, resampling problems with replacement within each stratum,
   10,000 resamples, numpy default_rng(0); 5th and 95th percentiles.
8. Report rho_E, rho_H, rho'_E, rho'_H, D_plain, D_null, Delta [90 % interval], stratum sizes and T1-right counts.

## Null

A second cued-base sample (C2) scored as a ratio against T1 in the same strata: the fall in retention that comes only
from sample-to-sample scatter of the cued base on hard items. Null value of Delta: 0 (plain falls no faster than C2).

## Threshold (frozen, from the plan)

Delta = -0.05. Holds only if the 90 % upper bound < -0.05 with at least 50 T1-right problems per stratum; refuted if
the 90 % lower bound >= -0.05; otherwise undecided.

## Verdict rule (engine 14)

Holds only if the 90 % interval lies wholly on the holding side of the threshold (upper bound < -0.05) and n >= 50
(T1-right problems per stratum); refuted if wholly at or above -0.05; otherwise undecided, with the n that would decide.

## Changes from the plan (noted before computing)

- Join on index (no unique_id in per_problem.json), with an assert that meta and data/rln4/math500.json agree on
  unique_id at every index.
- C2 is "sample index 0" read as the attempt-0 row of sample 0 (rows.jsonl also holds restart attempts 1-2 for
  capped samples; those are not used).
- Instrument check that must fail on a wrong input: the T3/T1 totals (224/410) and C2's total (405) must reproduce
  the posted counts; a deliberately shifted join (levels rolled by one index) must break the meta/data unique_id
  assert.
