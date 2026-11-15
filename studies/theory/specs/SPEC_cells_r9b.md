# Cells m21 and m18 of theory round-09

Written before any row of either cell exists. Cell definitions, readout ids and every forecast are fixed in
`studies/theory/results/wide/round-09/cells.md` and `cells.json` (entries m21 and m18); nothing here changes them.
Board: work-ef61c7.

Neither cell is on the board or in `studies/rlneurons/`: the Code 3.1 top-8 edit was scored on hard328 with the cue
(`xreward/edits/top8_code31-01/`, 178/328) and on code (`xreward/code_dial/`), never on MATH-500 with the plain prompt; the
weight blends exist at a = 0.25, 0.5, 1 plain (`day1_wdiff/`), not at 0.125.

## Cell m21

Model: untrained base `allenai/Olmo-3-1025-7B` + 1.0 x the top 8 singular directions per matrix of
(Olmo-3.1-7B-RL-Zero-Code - base), stochastic BF16 rounding, seed 0 (`wsp_edit --recipe top8 --other rl_code --scale 1.0
--rounding stochastic --seed 0`, the recipe of `xreward/edits/top8_code31-01/run.json`). Plain prompt, MATH-500 first 250
problems (`--n 250`), T 1.0 / top-p 1.0 / min-p 0, seed 64,000,000 + problem index, 1 sample, cap 16,384, grader v3.

Readout `m21-r1`: quick wrong answers = rows with n_new (generated tokens) <= 1,000, not a cap hit, and v3 score not 1 (no
extracted answer counts wrong), of 250.

Two most opposed forecasts (intervals do not overlap):

- run-05/f2-m06 (weights): 45 [28, 64]. Refuted if the count is below 28 or above 64.
- run-03/f2-m02 (stopping): 14 [7, 23]. Refuted if the count is below 7 or above 23.

The other forecasts (readers 25 [10, 45] and 18 [8, 32]; run-05/f2-m03 40 [24, 58]; round-09/stopping-m06 15 [8, 24]; and five
more) are scored the same way: a forecast holds when the count is inside its 90 % interval.

## Cell m18

Model: base + 0.125 x (RL-Math 3.1 - base), whole difference, stochastic BF16 rounding (`merge_weights --other rl --alpha 0.125
--rounding stochastic`, the recipe of `day1_wdiff/theta0.25_plain-01/run.json` at another alpha). Plain prompt, MATH-500 all 500,
T 1.0 / top-p 1.0 / min-p 0, seed 61,000,000 + problem index (as fixed in cells.md), 1 sample, cap 16,384, grader v3.

Readout `m18-r1`: right answers of 500, grader v3.

Two most opposed forecasts:

- round-09/problems-m03 (problems): 395 [365, 420]. Refuted if the count is below 365 or above 420.
- run-05/f2-m06 (weights): 300 [260, 340]. Refuted if the count is below 260 or above 340.

Also opposed to problems-m03: round-09/sampling-m03 308 [272, 342]. Readers 355 [315, 392] and 362 [320, 400].
References on the same problems and prompt: base plain 224 (a = 0), theta 0.25 plain 405, theta 0.5 plain 443.

## Readouts and outputs

For each cell: the readout count with a 90 % bootstrap interval (10,000 resamples of problems), right answers, cap hits,
generated tokens per problem, finished answers with no extracted answer, and which forecasters' intervals hold the count.
Outputs `studies/theory/results/experiments/cell-r9-m21-01/` and `cell-r9-m18-01/`: `run.json` (job ids, commit, command),
`metrics.json`, `per_problem.json`, `examples.json` (one right and one wrong answer, real text). Readout code
`studies/theory/analysis/cells_r9b.py`. One row per readout appended to `results/wide/round-09/measured.json`.

## Runbook

1. Smoke: each command with `--n 4 --max-tokens 256` into `$OUT_DIR/smoke` before the full run, in the same job; check rows.
2. m21 on one box; m18 as `--shard k/2` on two boxes; join the m18 shards with `studies/rlneurons/analysis/shard_join.py`.
3. Read 10 raw answers per cell before explaining a number.
