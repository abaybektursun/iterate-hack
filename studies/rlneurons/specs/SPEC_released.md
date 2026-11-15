# released: Think-SFT at the sampling setting it was released with

Written 2026-11-15 before any run. Board: the work item names this file.

## Question

The model's own `generation_config.json` (allenai/Olmo-3-7B-Think-SFT, revision 6ff857587e040d6d523a3d5f3a56e918f5401d66) sets
temperature 0.6, top-p 0.95, at most 32,768 new tokens, and its card uses the chat template. Every Think-SFT row of this study
samples at T 1.0 / top-p 1.0, the setting AI2 used for the RL model. Two of the three differences are measured and change
little or help: the chat format ties the cue (`results/native/`), the cap of 32,768 adds 23 to 28 problems (`results/cap32/`).
The third, the sampling setting, is not measured. Does Think-SFT score higher at its own setting?

## Measurement

`run_cell --prompt native --native-tokenizer <as in SPEC_native.md> --temperature 0.6 --top-p 0.95 --max-tokens 32768`,
grader v3, one sample. hard328 seed 3000000, MATH-500 seed 182000000: the seeds of `results/native/`, so each problem is
paired with the T 1.0 cell of the same format (232 of 328, 474 of 500 at 32,768). Scored also at 16,384 from the same answers.

## Hypotheses and what refutes each

- H1 (the released setting is better): on the 328 at 32,768, T 0.6 minus T 1.0 is at least +8 problems with the paired 95 %
  interval above 0. Refuted otherwise.
- H2 (loops return, as for the base at T 0.6): cap hits or the runner's loop count rise and the score falls by 8 or more.
- Neither: within the interval; T 1.0 rows stand as Think-SFT's rows.
- The mission compares models under identical conditions: a Think-SFT gain at T 0.6 is set beside RL at T 0.6 from stored
  rows where they exist, and stated as not matched where they do not.

## Order

MATH-500 and hard328 at once, 2 to 4 shards each on AWS L40S (the pipeline is that of `results/native/`, smoke passed there;
only two sampling numbers change). Readout `analysis/released.py`, README, board.
