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
