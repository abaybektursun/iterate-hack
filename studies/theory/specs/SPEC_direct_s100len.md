# Direct test s100len (theory round 15, `round-15/account-3/c3`)

Written before the statistic was computed. Offline, stored rows only.

## Claim

Account-3 says RL step 100 is only the mode selection the cue makes, without the later finishing and lengthening of
final RL. So on MATH-500 problems both arms solve, step 100's right answers are as long as the cued base's right
answers, while final RL's are longer.

## Statistic

Geometric mean over problems of (median generated tokens of the step-100 plain right samples / median generated
tokens of the cued-base right samples).

## Rows

- Step 100 plain, T 1.0 / top-p 1.0, 4 samples: sample 0 from `studies/rlneurons/results/ckptcue/s0100_plain-01/per_problem.json`,
  samples 1 to 3 from `studies/rlneurons/results/ckptcue/s0100_plain_s123-01/rows.jsonl` (no restarts in either job).
- Cued base, T 1.0 / top-p 1.0: `studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl`, attempt 0, samples 0 to 3.
- Context (null arm): final RL-Zero-Math plain, T 1.0 / top-p 1.0: `studies/rlneurons/results/day1_3/math500_rl-01/rows.jsonl`,
  attempt 0, samples 0 to 3.
- Right = `score_v3 == 1` (grader v3, as stored).
- Problems kept: at least 1 right sample in the step-100 arm and at least 1 in the cued-base arm (the plan expects n 430).
  The final-RL ratio uses problems with at least 1 right in final RL and in the cued base.

## Token counter

All three arms come from `studies/rlneurons/jobs/run_cell.py` (record function `rln4_gen.record`), same tokenizer
(`allenai/Olmo-3.1-7B-RL-Zero-Math` 364820b0). `n_new` = sampled tokens before the stop id, excluding the cue's 3
prefilled tokens. Sample 0 of step 100 stores only `n_generated` = `len(out_ids)`, which is `n_new + 1` for a finished
answer (the stop id) and `n_new` for a cap hit; the script uses `n_generated - 1` for finished rows and `n_generated`
for cap hits, so every arm is on the `n_new` counter. The cue's 3 prefilled tokens are not counted in the cued arm.

## Computation

1. Per problem and arm: median `n_new` of the right samples.
2. r_i = ln(step100_median / base_median).
3. Statistic = exp(mean r_i).
4. Bootstrap over problems, 10,000 resamples, seed 0; 90 % interval = 5th to 95th percentile of exp(mean r).
5. Null value: the same ratio with final RL's 4 attempt-0 samples in place of step 100.

## Ranges fixed in advance

- account-3: [0.88, 1.10]
- null (final RL-like lengthening): [1.15, 1.60]

## Verdict rule (engine 14)

- holds: the 90 % interval lies wholly inside [0.88, 1.10] and n >= 50.
- refuted: the 90 % interval lies wholly outside [0.88, 1.10].
- undecided otherwise; state the n that would decide.
- Report where the value falls relative to the null range [1.15, 1.60].

## Outputs

`studies/theory/results/direct/s100len-01/`: `metrics.json`, `examples.json` (one right answer per arm on the same
problem), `rows.json`. Script: `studies/theory/analysis/direct_s100len.py`.
