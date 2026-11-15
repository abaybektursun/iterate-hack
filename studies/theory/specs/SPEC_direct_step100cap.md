# SPEC: direct test of round-09/stopping-m04, "RL step 100 is capped as often as the cued base"

Board work-80b573. Theory round 14 carried plan: `studies/theory/results/wide/round-14/jobs/plan-round-09-stopping-m04.json`
(theory checkout, not yet on origin/theory). Written before any row-level number below was computed. Stored rows
only: no GPU job, no forward pass.

## The claim

At T 1.0 / top-p 1.0 on MATH-500, RL step 100 (plain prompt) cuts answers at the 16,384-token cap as often as the
cued base does on the same problems: its per-problem cap-hit rate is not lower than the cued base's by 1 point or
more, while final RL's clearly is.

## What was seen before writing

result-32b7a8 posts cap hits at T 0.6 / top-p 0.95, sample 0 only (cued base 119, step 100 103, step 2,800 19): a
different temperature, so it does not decide this T 1.0 claim. result-6832a8 posts accuracy, not cap hits. The
metrics.json files of the six folders carry total cap-hit counts (`counts.cap_hits`), which were seen while finding
the row files: s0100 sample 0: 24 of 500; s0100 samples 1-3: 61 of 1,500; base + cue: 166 over 2,137 rows (all
attempts); final RL: 44 over 2,041 rows (all attempts). Attempt-0 totals were counted while checking the row format
(base + cue 90, final RL 32, step 400 7 + 40). No paired difference or interval was computed before this spec.

## Files and rows

| Arm | Folders (under `studies/rlneurons/results/`) | Rows | Samples per problem |
|---|---|---|---|
| A, step 100 plain | `ckptcue/s0100_plain-01/per_problem.json` (sample 0), `ckptcue/s0100_plain_s123-01/rows.jsonl` (samples 1-3) | 2,000 | 4 |
| B, cued base | `day1_3/math500_base_cue-01/rows.jsonl`, attempt 0 only | 2,000 | 4 (samples 0-3) |
| C, final RL plain (positive control) | `day1_3/math500_rl-01/rows.jsonl`, attempt 0 only | 2,000 | 4 |
| E, step 400 plain | `ckptcue/s0400_plain-01/per_problem.json`, `ckptcue/s0400_plain_s123-01/rows.jsonl` | 2,000 | 4 |

All six runs: MATH-500, T 1.0, top-p 1.0, max_tokens 16,384 (checked in each metrics.json `config`).

## Changes from the plan (made before computing)

1. Restart rows. The two `day1_3` runs drew up to two restarts after a cap hit (`attempt` 1 and 2; 137 and 41 extra
   rows). A restart is a new draw taken only because attempt 0 hit the cap, so counting it would add cap hits that
   the step-100 and step-400 runs (no restarts) cannot have. Arms B and C use attempt 0 only: 4 rows per problem.
2. Field names. `per_problem.json` has no `finish_reason`; it has `cap_hit` and `n_generated`. The cap rule is
   `cap_hit` true, or finish reason `length`, or generated tokens (`n_new` / `n_generated`) >= 16,384, for every arm.
   In the rows.jsonl files `cap_hit`, `finish_reason == "length"` and `n_new >= 16384` agree on every row.
3. Sample index. `per_problem.json` rows are sample 0 (seed 45,000,000; the s123 run seeds samples 1-3 at
   45,010,000 + ...). "A's first 2 samples" in step 7 of the plan = samples 0 and 1.

## Computation

1. Instrument check, before the readout: for each folder, the count of cap hits over all its rows must equal
   `counts.cap_hits` in its metrics.json (24, 61, 166, 44, 7, 40), and each arm must have exactly 4 attempt-0 rows
   for each of the 500 problems. Stop if either fails. Planted checks: D of B against itself must be exactly 0; D
   of an arm with every row capped against B must be 100 - 100 * mean h_B.
2. h_X(i) = share of arm X's 4 attempt-0 samples on problem i that hit the cap.
3. Statistic: D = 100 * mean_i [h_A(i) - h_B(i)], points, n = 500 problems.
4. Interval: 90 % percentile bootstrap over problems, 10,000 resamples, `numpy.random.default_rng(0)`; the same
   resample indices for every paired difference.
5. D_C = C - B and D_E = E - B, each with its 90 % interval.
6. Null: D_null = 100 * mean_i [h_B{0,1}(i) - h_B{2,3}(i)] with its 90 % interval; size-matched D_2 = A samples
   {0,1} against B samples {2,3}.
7. Descriptions only: right share (score_v3) among finished (not capped) rows of A and B; total cap-hit counts of
   A, B, C, E.

## Threshold (copied from the plan)

-1.0 percentage points of cap-hit rate (step 100 minus cued base, paired over 500 problems, 90 % bootstrap
interval). Holds only if the whole interval is above -1.0 and final RL's difference has its whole interval below
-1.0.

## Verdict rule (engine 14, carried plan)

- Instrument check: if D_C's 90 % interval does not lie wholly below -1.0, the verdict is `undecided`.
- Otherwise `holds` if D's 90 % interval lies wholly above -1.0 and n >= 50.
- `refuted` if D's 90 % interval lies wholly at or below -1.0.
- `undecided` in every other case, with the n that would decide it.

Refuted if: step 100 cuts clearly fewer answers than the cued base (D's interval wholly at or below -1.0) while
final RL's interval also lies below -1.0.

## Outputs

`studies/theory/analysis/direct_step100cap.py` writes `studies/theory/results/direct/step100cap-01/metrics.json`,
`examples.json` and `rows.json`. Run: `uv run python studies/theory/analysis/direct_step100cap.py`.
