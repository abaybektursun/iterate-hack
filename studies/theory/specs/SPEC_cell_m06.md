# cell m06: RL-Zero-Math step 100, plain prompt, first 164 problems of hard328

Written 2026-11-15 before the job. Board idea-e9dfd5. Cell designed in `results/forecast/cells-01/cells.md` (entry m06,
main 8d36a7b); the forecasts below are copied from there and were fixed before any row.

## Cell

- Model: `allenai/Olmo-3.1-7B-RL-Zero-Math` at revision `0a45720ccbf23c0aa255a28119787538a48dd56b` (branch step_0100),
  downloaded in the job to `/tmp/s0100` and passed with `--model-path`, as in the ckptcue cell s0100_plain
  (`studies/rlneurons/results/ckptcue/s0100_plain-01/run.json`, job abaybektursun-1115-064532-6a2f). RL tokenizer from
  `data/rln4/frozen4.json`, as for every run_cell job.
- Prompt plain (pair1 template, no prefilled tokens). Set hard328, the first 164 problems in the set's stored order
  (`--n 164`; hard.json indices 0 to 233). One sample, no restarts.
- T 1.0 / top-p 1.0 / min-p 0, seed 3000000 + hard.json index (the seed of sample 0 in the stored hard328 cells
  `results/day1_3/hard328_*_s4r2-01`). Cap 16,384 generated tokens. Grader v3 (`rln4_lib.grade_v3`). `jobs/run_cell.py`
  unchanged.

Command (vast.ai or `ih submit l40s-small`):

```
PIP_BREAK_SYSTEM_PACKAGES=1 bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -c "from huggingface_hub import snapshot_download; snapshot_download('allenai/Olmo-3.1-7B-RL-Zero-Math', revision='0a45720ccbf23c0aa255a28119787538a48dd56b', local_dir='/tmp/s0100', allow_patterns=['*.json','*.safetensors','*.jinja','*.txt'])" && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/s0100 --model-label s0100 --prompt plain --set hard328 --temperature 1.0 --top-p 1.0 --seed 3000000 --n 164 --commit <sha>
```

Smoke first: the same command with `--n 4`, read the rows.

## Readout (the quantity the forecasts are about)

m06-r1: quick finished-wrong answers = rows that are not cap hits, are graded wrong by v3 and have at most 2,000
generated tokens, counted over the 164 problems. Also reported: right answers (v3) of 164, cap hits, mean generated
tokens per problem, 'Okay' in the first 30 characters, and a 90 % bootstrap interval (problems resampled, 10,000 draws,
seed 0) for the right count and for r1.

## Forecasts (copied from cells.md, m06-r1, problems of 164)

| forecaster | value | 90 % interval | refuted when the measured r1 is |
|---|---|---|---|
| run-03/f2-m06 (step 100's misses of the 'Okay' opening fall into the base's terse register and stop early) | 26 | [15, 38] | below 15 or above 38 |
| run-06/f2-m02 (step 100 selects the deliberative register, answers behave like the cued base's) | 6 | [2, 12] | below 2 or above 12 |
| run-05/f2-m04 | 8 | [3, 16] | below 3 or above 16 |
| reader-1 (no theory) | 20 | [9, 34] | below 9 or above 34 |
| reader-2 (no theory) | 22 | [10, 36] | below 10 or above 36 |

The two theory intervals do not overlap: a count of 13 or 14 refutes both; 12 or less refutes run-03/f2-m06; 15 or
more refutes run-06/f2-m02.

## References on the same 164 problems (stored rows, sample 0, same seeds, v3)

From `studies/rlneurons/results/day1_3/<cell>/rows.jsonl`, computed before the job:

| cell | right | cap hits | tokens per problem | quick finished-wrong (r1) |
|---|---|---|---|---|
| base + cue (hard328_base_cue_s4r2-01) | 65 | 53 | 10,677 | 1 |
| final RL, plain (hard328_rl_plain_s4r2-01) | 84 | 26 | 10,286 | 0 |

## Instrument checks

- Identity: on MATH-500 at T 1.0 step 100 plain opened with 'Okay' in the first 30 characters on 383 of 500; a base
  model loaded by mistake gives far fewer, the final model more. Report the count on these 164.
- The readout counts a row only when `finish_reason` is "stop" and `cap_hit` is false; check that cap hits are rows with
  exactly 16,384 generated tokens.
- Read 10 raw answers (the r1 rows first) before explaining the number.

## Outputs

`results/experiments/cell-m06-01/`: `run.json` (job id, commit, command), `metrics.json`, `per_problem.json`,
`examples.json` (one right, one wrong, real text). Analysis `analysis/cell_m06.py`. Measured value appended to
`results/forecast/cells-01/measured.json`.
