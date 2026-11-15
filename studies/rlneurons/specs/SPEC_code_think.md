# Think-SFT on the Code pair (written 2026-11-15 18:50 UTC, before any job)

Board: follows "Code pair" (`specs/SPEC_code1.md`; HumanEval+ 163 + MBPP+ 375 = 538 scored problems: RL-Code 3.1 plain 401,
base plain 222, base + Code cue 317, base + Math cue 326) and result-818c20 / result-5251c9 (Think-SFT + cue is ahead of
RL-Zero-Math on the 328 and on fresh2026).

Question: is a model trained on reasoning traces with no reward (allenai/Olmo-3-7B-Think-SFT) also ahead of, level with, or
behind the RL model of the domain on code? On math it is 2.7 to 7.0 points ahead of RL-Math on one sample. If it is level
with RL-Code here, "imitation reaches RL" holds on a second domain; if it stays near the cued base, the math result is
about its math training traces.

Cells (one sample each, T 1.0 / top-p 1.0, seed 51000000, the seeds, template, cap and test harness of "Code pair";
`wsp_edit --recipe interp --other think_sft --alpha 1.0 --rounding nearest --seed 0` writes the Think-SFT weights bit for
bit, then `jobs/run_code_cell.py --model-path /tmp/theta`):

1. `sft1_codecue`: prefix ids of the Code cue, [439,6982,304,279,10137,13,358,3987,420,8779,2268,33413].
2. `sft1_mathcue`: prefix ids of the Math cue, [1584,2268,33413].

Readout: `analysis/code1_readout.py` with the four stored cells as references; paired bootstrap against RL-Code and against
the base with the same cue.

Predictions, each with the observation that refutes it:

1. Think-SFT + Code cue passes between 330 and 395 of 538 (point 360): above the cued base, below RL-Code. Refuted outside.
2. It is below RL-Code: the paired 95 % interval of Think-SFT + Code cue minus RL-Code (401) is below 0. Refuted if the
   interval includes 0 or is above it.
3. The two cues differ by under 3 points on Think-SFT (base: Math cue 326, Code cue 317, -1.7 [-5.8, 2.8]). Refuted at 3
   points or more with an interval that excludes 0.

Not controlled: overlap of HumanEval / MBPP with the Think-SFT training data (its code sources are scanned for the math
sets only); one sample per cell.

## Amendment 1 (2026-11-15 22:40 UTC, after the two cells, before any regrade)

Seen in the rows: 97 of the 106 Think-SFT + Code cue answers with no fenced block (Math cue: 124 of 128) end their reasoning
with `</think>` and write a line `python`, the program and a closing fence, with no opening fence. `code_lib.extract` runs the
whole text for them, which fails. The first table stands as graded; this adds a second grading for every cell.

Rule `code_lib.extract_v2` (new function; `extract` and `BLOCK` unchanged): as `extract` when a closed fenced block exists.
Otherwise the text after the last line that is only `python` (or `py`), up to the next fence or the end, without a last line
that is only `CODE`. Applied to all five cells by `jobs/regrade_code_v2.py`; rows with a closed block keep their outcome.

Instrument check inside the job, on all 538 problems: the reference program in the unopened form must pass under `extract_v2`
and fail under `extract`; the planted wrong program in that form must fail under `extract_v2`.

Predictions under v2:

4. Think-SFT + Code cue passes 355 to 385 of 538 (point 369). Refuted outside.
5. It is above base + Code cue under v2: the paired 95 % interval is above 0. Refuted if it includes 0.
6. It stays below RL-Code under v2: interval below 0. Refuted if it includes 0.
7. Base and RL-Code change by at most 5 problems each. Refuted at 6 or more.
