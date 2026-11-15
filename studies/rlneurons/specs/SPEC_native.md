# native: Think-SFT in its own chat format

Written 2026-11-15 before any run. Board: the work item names this file.

## Question

Every Think-SFT row on the board (cue 212 to 219 of 328 at cap 16,384, 230 at cap 32,768, vote over 4 = 241) prompts the model
with the study's raw template and the base's three-token opening cue. The model was trained on chat-format traces: its
tokenizer's template (allenai/Olmo-3-7B-Think-SFT, revision 6ff857587e040d6d523a3d5f3a56e918f5401d66) wraps the user turn in
`<|im_start|>` markers with a system line and opens the answer with `<|im_start|>assistant\n<think>`. No row uses that format.
Is the cue row the model's best single-sample row, or does its own format score higher?

## Measurement

`run_cell --prompt native --native-tokenizer allenai/Olmo-3-7B-Think-SFT@6ff857587e040d6d523a3d5f3a56e918f5401d66`: the user
message is the study's template text with the problem (same words as every other row), rendered by the model's chat template
with the generation prompt. Generation stops at the stop id or at `<|im_end|>`. Model directory as in the cue rows
(`wsp_edit --recipe interp --other think_sft --alpha 1.0`). T 1.0 / top-p 1.0, grader v3 on the whole text, one sample,
cap 32,768, scored also at 16,384 from the same answers (`analysis/cap32.py`). hard328 seed 3000000; MATH-500 seed 182000000.

Compared with Think-SFT cue at the same cap from `results/cap32/` (230 at 32,768, 207 at 16,384), paired by problem.

## Hypotheses and what refutes each

- H1 (own format is better): native minus cue on the 328 at cap 32,768 is at least +10 problems with a paired 95 % interval
  above 0. Refuted otherwise.
- H2 (the cue carries Think-SFT's score): native is at least 10 problems below cue with the interval below 0. Then the base's
  cue beats the format the model was trained in.
- Neither: the two formats are within the interval; the cue is not needed for Think-SFT and the rows stand.
- Instrument: the smoke's rows must show the chat markers in `prompt`, text after `<think>`, and a finished answer ending at
  the stop id or `<|im_end|>` (`ended_im_end`), with the grader reading the final answer after the thinking part.

## Order

Smoke `--n 8` on MATH-500, read the rows. Then hard328 in 4 shards and MATH-500 in 4 shards. Readout, README, board.
