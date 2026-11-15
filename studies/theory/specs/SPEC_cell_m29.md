# Cell m29: base + top-8 RL-Math directions at 2x, cue, MATH-500 (board idea-e9dfd5, work-290625)

Written before the run. The forecasts are copied from `results/forecast/cells-01/cells.md` (entry m29, main 8d36a7b) and are
not changed here.

## The cell

- Model: allenai/Olmo-3-1025-7B (rev a81bae42) + 2.0 x the top 8 singular directions per matrix of
  (allenai/Olmo-3.1-7B-RL-Zero-Math rev 364820b0 - base), written by `studies/rlneurons/jobs/wsp_edit.py --recipe top8
  --other math31 --scale 2 --rounding stochastic --seed 0 --dir /tmp/theta` (the edit of the hard328 2x cell
  `rlneurons/results/xreward/edits/top8x2_math31-01/`; the proposer's `--recipe topk --other rl_math --k 8` names do not
  exist in `wsp_edit.py`).
- Prompt: the opening cue (prefix ids 1584, 2268, 33413), set MATH-500, all 500 problems, 1 sample, no restarts.
- Sampling: T 1.0, top-p 1.0, min-p 0, cap 16,384 new tokens, grader v3 (as written by `run_cell.py`).
- Seed: 3000000 (problem i gets 3000000 + i), the seed of the 1.5x MATH-500 cell (`rlneurons/results/xreward/dial15_math500-01/`,
  456 of 500, job abaybektursun-1115-055652-3a2d). cells.md writes 105000000; 3000000 is used so that the only change against
  the 1.5x cell is the scale and the two cells pair problem by problem with the same sampling seeds.
- Command: `bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m
  studies.rlneurons.jobs.wsp_edit --recipe top8 --other math31 --scale 2 --rounding stochastic --seed 0 --dir /tmp/theta &&
  /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label top8x2_math31 --prompt cue
  --set math500 --temperature 1.0 --top-p 1.0 --seed 3000000 --commit <sha>`.
- Smoke run first: the same command with `--n 4 --max-tokens 1024`; it must write rows to `answers.jsonl`.

## Forecasts (right answers of 500, grader v3)

| Group | Forecasters | Value [90 %] | Refuted by |
|---|---|---|---|
| A: 2x commits too early, the hard328 loss carries over | run-07/f2-m01 | 423 [410, 436] | a count above 436 |
| B: 2x stays near 1.5x on short problems | run-04/f2-m06 455 [443, 466], run-05/f2-m01 449 [438, 459], run-05/f2-m02 455 [444, 465], run-08/f2-m01 450 [439, 461], r5-m03-rival 449 [438, 459] | 449 to 455 | a count below 438 (the lowest lower bound of the five; each member is refuted below its own lower bound) |

The no-theory readers: reader-1 445 [431, 458], reader-2 448 [434, 460]. A count of exactly 437 refutes both groups; no count
supports both.

## Readout

`analysis/cell_m29.py` reads the job's `answers.jsonl` and writes `results/experiments/cell-m29-01/`:

- `metrics.json`: right (v3) of 500 with a 90 % bootstrap interval (10,000 resamples of problems, seed 0); cap hits; mean generated
  tokens per problem; answers without an extracted answer; the paired difference against the 1.5x cell (456, same seeds), in
  problems of 500 with a 90 % paired bootstrap interval; the problems right at 1.5x and wrong at 2x and the reverse.
- `per_problem.json`: problem index, right v3, generated tokens, cap hit, extracted answer, gold.
- `examples.json`: one right and one wrong answer, real prompt and completion text.
- `run.json`: commit, command, job id, box.

Before explaining the count, read 10 wrong answers in full: whether they end in a cap hit, decay into repeated or function-word
text, finish with a wrong boxed answer, or stop without a box.
