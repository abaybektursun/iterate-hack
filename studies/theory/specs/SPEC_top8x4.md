# SPEC top8x4-01: how many base + top-8 plain answers are short, and are they right on easy problems only?

Written 2026-11-15 before any new row exists. Work item work-22359d, idea idea-7ca1fe (the predictions are fixed there and
copied below unchanged). The thresholds that turn each prediction into a refuting observation are fixed here, before the
stored sample's readout was computed.

## Question

The theory r5-m03-rival says the top-8 edit of the RL-Math weight change is an incomplete switch per sample: most plain
answers of base + top-8 follow RL's policy, and 10-15 % stay in the plain base's short register, right about half the time
whatever the problem. The smooth-blend alternative says short answers are what the edited model writes on easy problems,
and they are right there. One stored sample per problem cannot separate the two: it needs several samples on the same
problem.

## Measurement

- Model: `allenai/Olmo-3-1025-7B` (revision `a81bae42db3975be1671e27b9c9a56da1a9f980f`) + 1x the top-8 singular directions per
  matrix of (`allenai/Olmo-3.1-7B-RL-Zero-Math` at `364820b002fc8e81d11a81c7fc9dd6b49c83cd05` minus base), written by
  `studies/rlneurons/jobs/wsp_edit.py --recipe top8 --other rl_math --rounding stochastic --seed 0` (names from
  `jobs/wsp_delta_anatomy.py` MODELS and `data/rln4/frozen4.json`). The same command as the stored cell
  `studies/rlneurons/results/wsp1/full500/top8_plain-01/` (job sameraslan-1114-185934-b0a9, H100). The edit statistics
  written to `edit.json` must equal the stored ones (`add_norm` 1.269214040907, `n_edited` 224) to within GPU float noise.
- Generation: `studies/rlneurons/jobs/run_cell.py --model-path /tmp/theta --model-label top8 --prompt plain --set math500
  --temperature 1.0 --top-p 1.0 --seed 187000000 --samples 3`, cap 16,384 (frozen4.json), sharded `--shard k/N`. Sample s of
  problem i has seed 187,000,000 + 10,000 s + i (s = 0, 1, 2); the stored sample used 180,000,000 + i, so no seed repeats.
  New samples are numbered 1, 2, 3 in the readout; the stored sample is sample 0.
- Grader v3 (`rln4_lib.grade_v3`, in the rows). Tokens: `n_generated` (the stored per-problem field; generated ids
  including the stop id).
- **Short sample**: `n_generated` <= 1,000. Long: > 1,000. Threshold sensitivity at 600 and 1,500.
- **Solve bin** of a problem: right answers of 4 of the cued base (base + cue, T 1.0 / top-p 1.0, grader v3), the stored rows
  `studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl`, attempt 0, samples 0-3 (job -153825-208b). Bins 0..4.

## Predictions on file (idea-7ca1fe)

- **P1, top-8 switch (r5-m03-rival)**: 10-15 % of samples are 1,000 tokens or shorter, about 50 % of them right, flat across the
  cued base's 0-4 of 4 solve bins, and short and long samples fall on the same problems.
- **P2, smooth blend**: short samples sit on easy problems and are 85 % or more right where the cued base solves 4 of 4.

Refuting observations (fixed here):

- P1 is refuted by any of: (a) the 90 % bootstrap interval of the short share lies entirely outside [10 %, 15 %]; (b) the 90 %
  interval of short-sample accuracy lies entirely outside [35 %, 65 %]; (c) short-sample accuracy in bin 4 is 85 % or more;
  (d) fewer than half of the problems with at least one short sample also have a long sample among their 4.
- P2 is refuted by either of: (a) short-sample accuracy in bin 4 is below 85 % (tested only if bin 4 holds at least 10 short
  samples); (b) short samples are not concentrated on easy problems: the share of short samples that fall in bin 4 is not
  above bin 4's share of all samples.
- The deciding number is short-sample accuracy in bin 4 (c for P1, a for P2), with its n.

## Readout (`analysis/top8x4.py`)

Bootstrap: 90 % percentile interval, problems resampled with replacement (all 4 samples of a problem move together), 5,000
resamples, numpy seed 0. Ratios (accuracy of short samples) are the ratio of sums within each resample.

1. Accuracy per sample: right of 500, cap hits, mean `n_generated`, short count (stored sample 0 and new samples 1-3).
2. Short share over all 2,000 samples with its interval.
3. Accuracy of short samples overall with n and interval; per solve bin 0-4 with n.
4. Accuracy of long samples per solve bin with n.
5. Share of all 500 problems that have both a short and a long sample among their 4; the same among problems with at least
   one short sample; distribution of the number of short samples per problem (0-4).
6. Share of short samples in bin 4 against bin 4's share of all samples.
7. Threshold rows at 600 and 1,500 tokens: short share, short accuracy, short accuracy in bin 4 and in bins 0-1.
8. Verdict lines for P1 (a-d) and P2 (a-b) as computed booleans.

The script runs on the stored sample alone (sample 0) before any new row is read, to check it.

## Outputs

`studies/theory/results/experiments/top8x4-01/`: `run.json` (commit, commands, job ids, GPU, edit statistics),
`metrics.json` (the readout above), `per_problem.json` (per problem: bin, and per sample score and tokens), `examples.json`
(one short right and one short wrong new sample: prompt, real text, gold, extracted answer, score, tokens). Raw rows stay in
`runs/<job-id>/` (not committed); their location goes in the README.

## Runbook

1. Commit and push the spec and the script; check the script on the stored sample.
2. Smoke: one job with `--n 3 --max-tokens 512`; check that `answers.jsonl` has 3 rows and `edit.json` matches the stored edit.
3. Full: `--samples 3 --shard k/N` jobs at once; `ih wait`, `ih get`.
4. Check every shard finished (`status` done, 1,500 rows in total, each (problem, sample) once), run the readout, read 10 short
   samples, write the README section, post the result.
