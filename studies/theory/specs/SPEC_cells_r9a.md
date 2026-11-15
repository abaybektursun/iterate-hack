# SPEC cells r9a: round-09 cells m11 and m13

Written before the runs. Board work-739554. The cells, their readouts and all forecasts are fixed in
`results/wide/round-09/cells.md` and `cells.json` (entries m11, m13); this file copies the two most opposed forecasts of each and
changes nothing.

Neither cell is stored: `studies/rlneurons/results/xreward/edits/readout.json` has `top8xm1_math31` (size -1) on hard328 only
(118/328, 96 cap hits) and `top64_math31` at size 1 only (200/328); no board result or open work item covers size -1 on MATH-500 or
top-64 at size 2.

Models (from `wsp_edit`'s table, as in the stored edit cells `top8xm1_math31-01/run.json`, `top64_math31-01/run.json`): base
`allenai/Olmo-3-1025-7B` @ `a81bae42`, other `allenai/Olmo-3.1-7B-RL-Zero-Math` @ `364820b0` (key `rl_math` = key `math31`).
Edit: per matrix, the top-k singular directions of (other - base), times the scale, added to the base, stochastic BF16 rounding
seed 0. Sampling for both: 1 sample per problem, no restarts, T 1.0 / top-p 1.0 / min-p 0, cap 16,384 generated tokens, the
3-token opening cue, grader v3. Seeds are seed + problem index, so a shard gives the same rows as the whole run.

## m11

base - 1.0 x top-8 directions; cue; MATH-500, all 500; seed 41,000,000 + index (the seeds of the stored cued-base T1 cell
`studies/rlneurons/results/day1_3/math500_base_cue-01`, attempt 0 sample 0: 27 cap hits). Command (cells.md), run as 2 shards
(`--shard 0/2`, `--shard 1/2`):

    bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe top8 --other rl_math --scale -1.0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label top8x-1_math31 --prompt cue --set math500 --temperature 1.0 --top-p 1.0 --seed 41000000 --commit $(git rev-parse HEAD)

Readout `m11-r1`: cap hits among the 500 answers (`metrics.json` `cap_hits`, summed over the shards), of 500.

| forecaster | value | 90 % interval | refuted by |
|---|---|---|---|
| round-09/stopping-m03 (stopping follows the size of the added singular values, not their sign: -1 cuts cap hits like +1) | 16 | [8, 26] | 27 or more cap hits, or 7 or fewer |
| run-07/f2-m02 (highest centre, tied with reader-1 42 [28, 60]; signed dial: size -1 lengthens answers) | 42 | [28, 58] | 27 or fewer cap hits, or 59 or more |

Also reported: right answers v3 of 500, generated tokens per problem, answers with no boxed answer.

## m13

base + 2.0 x top-64 directions; cue; hard328 shard 0/2 (problems 0, 2, ..., 326; 164 problems); seed 3,000,000 + index (the
seeds of the whole xreward dial). Command (cells.md):

    bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe top8 --other rl_math --k 64 --scale 2.0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label top64x2_math31 --prompt cue --set hard328 --temperature 1.0 --top-p 1.0 --seed 3000000 --shard 0/2 --commit $(git rev-parse HEAD)

Readout `m13-r1`: right answers v3 of the 164 shard-0/2 problems (`metrics.json` `correct_v3`).

| forecaster | value | 90 % interval | refuted by |
|---|---|---|---|
| round-09/stopping-m03 (total top-subspace energy: top-64 at 2x is like top-8 at about 3.1x, past degeneration) | 58 | [40, 80] | 81 or more right, or 39 or fewer |
| round-09/weights-m02 (highest centre) | 100 | [91, 108] | 90 or fewer right, or 109 or more |

Also reported: cap hits, generated tokens per problem, and whether answers decay into word strings as top-8 at 3x did.

## Runbook

1. Each job runs a 2-problem, 256-token smoke run of the same edited model first (`--n 2 --max-tokens 256 --out $OUT_DIR/smoke`);
   check that it writes rows before waiting on the main run.
2. Compute: AWS through `ih` once; on a quota or slot failure, vast.ai, one box per job (m11 shard 0/2, m11 shard 1/2, m13).
3. Intervals: 90 % bootstrap over problems (10,000 resamples, seed 0). Read 10 raw answers per cell before writing an explanation.
4. Outputs: `results/experiments/cell-r9-m11-01/`, `results/experiments/cell-r9-m13-01/` (`run.json`, `metrics.json`,
   `per_problem.json`, `examples.json`); one row per readout in `results/wide/round-09/measured.json`.
