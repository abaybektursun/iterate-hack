# SPEC: direct test of round-09/grader-m01, "at RL step 100 the cue adds nothing beyond seed scatter"

Board work-6b73e9. Theory round 13 plan: `studies/theory/results/wide/round-13/direct_tests.json` (entry
`round-09/grader-m01`, branch `theory`). Written before the readout below was computed. Stored rows only: no GPU
job, no forward pass.

## The claim

Mechanism `round-09/grader-m01`: each posted single cell is one seeded draw; new seeds on the same weights scatter
by 5-7 problems per 500, and multi-sample means regress to the pooled level of near-identical cells. Step-100 plain
pools with step-100 cue (same opening policy). Tested consequence: on MATH-500, pooling all stored samples per arm
(4 plain, 4 cue), the paired per-problem cue-minus-plain difference D at RL step 100 is not reliably above 0, so the
9-problem single-cell gap (427 vs 418, sample 0 of each arm) is a draw difference, not a cue effect.

## Why only this mechanism

From the plan: run-08/f2-m01 shares the seed-scatter idea but shrinks each cell toward a prior that includes a cue
effect, so it expects a positive gap to remain after pooling. round-09/grader-m04 expects the cue to keep moving
easy-to-mid problems, which make up most of MATH-500. The template, direction, cap, vote and strata mechanisms
(training-m01, f2-m05, weights-m06, problems-m04, f2-m02, f2-m06, grader-m06) imply no zero cue effect at step 100.
Only grader-m01 predicts D = 0.

## What was seen before writing

result-6832a8 (ckptcue3, `studies/rlneurons/results/ckptcue/readout3.json`) already posts the pooled totals (plain
1670/2000, cue 1704/2000; per sample plain 418, 411, 422, 419 and cue 427, 423, 423, 431) and the per-problem
paired difference "cue on step 100: +1.70 points [0.00, +3.35]", a 95 % percentile interval from 5,000 resamples.
That interval's lower end sits exactly on the threshold (0.0 is not > 0.0), and no permutation p was posted, so the
posted result does not decide the rule by itself. This test recomputes D with the plan's 10,000 resamples, seed 0,
adds the permutation null and the second-sample null. No row-level number was computed before this spec.

## Files

- `studies/rlneurons/results/ckptcue/s0100_plain-01/per_problem.json` (sample 0, seed 45,000,000, job
  abaybektursun-1115-064532-6a2f)
- `studies/rlneurons/results/ckptcue/s0100_plain_s123-01/rows.jsonl` (samples 1-3, seed 45,010,000, job
  abaybektursun-1115-102945-9b20)
- `studies/rlneurons/results/ckptcue/s0100_cue-01/per_problem.json` (sample 0, seed 41,000,000, job
  abaybektursun-1115-032509-fc06)
- `studies/rlneurons/results/ckptcue/s0100_cue_s123-01/rows.jsonl` (samples 1-3, seed 41,010,000, job
  abaybektursun-1115-102956-6e9a)
- Positive control: `studies/rlneurons/results/ckptcue/s0400_plain-01/per_problem.json` and
  `s0400_plain_s123-01/rows.jsonl` (step 400 plain, 4 samples).
- Check: `studies/rlneurons/results/ckptcue/readout3.json`.

Right = stored `score_v3` (grader v3), not regraded.

## Computation

1. Load every row; keep problem index (0-499), sample id, score_v3. PLAIN = the two plain folders, CUE = the two
   cue folders. Keep problems with the same k >= 2 samples in both arms (expected: all 500 with k = 4); report drops.
2. Check: per-sample right counts equal readout3.json, totals equal 1670 and 1704. Stop if any is off by more than 2.
3. pc_i, pp_i = mean right over CUE and PLAIN samples of problem i; d_i = pc_i - pp_i; D = 500 * mean d_i, in
   problems per 500.
4. Paired bootstrap over problems: 10,000 resamples, `numpy.random.default_rng(0)`; 95 % (the plan's level) and
   90 % percentile intervals.
5. Null A: per problem, pool the 8 samples and reassign 4 to CUE and 4 to PLAIN at random, independently per
   problem; 10,000 times with `default_rng(1)`; two-sided p = share of |D_perm| >= |D|.
6. Null B (second sample of the same weights). (a) As the plan says, folder against folder within each arm (sample 0
   against the mean of samples 1-3), and between arms with one folder each, per 500. (b) Change from the plan: the
   folders hold 1 and 3 samples, so a folder-against-folder difference mixes a 1-sample and a 3-sample mean and is
   not on the scale of either the 9-problem single-cell gap or D. Added: every single-sample pair, within arm (6
   plain pairs, 6 cue pairs: |difference| in right counts) and between arms (16 pairs: cue minus plain). Reported:
   the 16 between-arm differences, their mean (equals D by construction), and the 12 within-arm absolute
   differences and their maximum.
7. Descriptive only: D on problems where 0 < pc_i + pp_i < 2 (not both arms all-right or all-wrong).
8. Instrument check (positive control, added): the same D, bootstrap and permutation for step 400 plain minus step
   100 plain (posted +4.05 points [+2.40, +5.70]). The rule must refute there (lower 95 % bound > 0 and p < 0.05);
   if it does not, the instrument cannot detect a real 20-problem gap and the verdict is reported as undecided.

## Refuting observation and frozen threshold (unchanged from the plan)

Refuted if the lower end of the paired 95 % bootstrap interval of D is > 0.0 problems per 500 AND the permutation
two-sided p < 0.05. Otherwise the claim holds and the 9-problem single-cell gap counts as seed scatter.

## Null stronger than random

Null A keeps each problem's difficulty and the step-100 weights fixed and permutes only the prompt label, so it
asks whether the cue moves any problem beyond resampling. Null B is a second draw of the same weights and prompt.

## Outputs

`studies/theory/analysis/direct_cue100.py` writes `studies/theory/results/direct/cue100-01/`: `readout.json`,
`examples.json` (one problem that supports the claim: cue and plain tie; one against: cue right where plain is
wrong in most samples), `reading.md` (10 raw rows read by hand), `run.json`.
