# SPEC cell m20: the untrained base with the plain prompt on fresh2026

Written before the run. Board idea-e9dfd5, work item work-a68dfd. The cell and its forecasts are fixed in
`results/forecast/cells-01/cells.md` (entry m20, main `8d36a7b`); this file copies them and does not change them.

## The cell

| field | value |
|---|---|
| model | `--model base` of `studies/rlneurons/jobs/run_cell.py`: `allenai/Olmo-3-1025-7B` @ `a81bae42db3975be1671e27b9c9a56da1a9f980f` (the name and revision the base-cue fresh2026 cells recorded in `studies/rlneurons/results/fresh/base_cue_s4-01/run.json`) |
| prompt | plain: the pair1 prompt, no opening cue (`--prompt plain`) |
| set | fresh2026: `studies/rlneurons/data/fresh/fresh2026_v1.json`, 136 problems, sha256 `dcf571ea...d7d7` (checked by `run_fresh.py`) |
| sampling | T 1.0, top-p 1.0, min-p 0, 1 sample per problem, no restarts |
| seed | 93,000,000 + problem index (the seed of the cell in cells.md; the seed rule of `run_cell` is the one the fresh2026 cells used) |
| cap | 16,384 generated tokens (frozen4 default) |
| grader | v3 (as computed by `run_cell`) |

Command (the cells.md command, sent to AWS through `ih` instead of Modal; a 4-problem, 256-token smoke run goes first in the same
job and writes to `$OUT_DIR/smoke`):

    bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_fresh --model base --prompt plain --set fresh2026 --temperature 1.0 --top-p 1.0 --seed 93000000 --commit $(git rev-parse HEAD)

## Readout

m20-r1: right answers with grader v3 (`metrics.json` `counts.correct_v3`), problems of 136. Also reported: cap hits, mean
generated tokens per problem, a 90 % bootstrap interval over problems (10,000 resamples, seed 0).

Reference counts on the same 136 problems: base + cue 28, 28, 32, 30 per sample (mean 29.5); RL-Zero-Math plain 49, 50, 53, 50
(result-5251c9).

## The forecasts (copied from cells.md, 90 % intervals)

Group A, training-data mechanisms (run-06 family). The cue's share of RL's gain is fixed at 55-78 %, so
(29.5 - p) / (50.5 - p) >= 0.55 forces the plain base to p <= 4.

| forecaster | value | 90 % interval |
|---|---|---|
| run-06/f2-m02 | 3 | [0, 8] |
| run-06/f2-m06 | 2 | [0, 7] |

Refuted by: a count above 8 (outside both intervals). A count of 8 refutes run-06/f2-m06 only.

Group B, a problem-structure mechanism and a grader mechanism. run-07/f2-m06: fresh2026's thin middle band compresses every
gain, the cue's included, so the plain base sits nearer the cued base than on hard328 (ratio 0.46 there): about half of 29.5.

| forecaster | value | 90 % interval |
|---|---|---|
| run-07/f2-m06 | 16 | [9, 23] |
| run-08/f2-m01 | 14 | [8, 20] |

Refuted by: a count below 8 (outside both intervals). A count of 8 refutes run-07/f2-m06 only. A count above 23 refutes both.

No-theory readers: reader-1 14 [7, 22], reader-2 13 [6, 21].

Each forecaster is scored against its own interval; the separating pairs are (run-06/f2-m02, run-07/f2-m06),
(run-06/f2-m06, run-07/f2-m06), (run-06/f2-m06, run-08/f2-m01).

## Outputs

`results/experiments/cell-m20-01/`: `run.json` (commit, command, job id), `metrics.json` (the job's counts plus the interval),
`per_problem.json` (one row per problem: index, id, gold, extracted answer, score, tokens, cap hit), `examples.json` (one right
and one wrong answer, real prompt and completion). Written by `analysis/cell_m20.py` from the job's `answers.jsonl`. The
count also goes to `results/forecast/cells-01/measured.json`. Before any explanation, 10 raw answers are read: how many open
in the cue's style ("Okay") on their own, how many hit the cap.
