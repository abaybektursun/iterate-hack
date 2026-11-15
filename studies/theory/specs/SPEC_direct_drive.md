# Direct test of run-05/f2-m03 across domains: does code text drive Math's top-8 input subspace about half as much as math text?

Written 2026-11-15 before the job ran. Board work-c51f89, follows result-0b3807 (`SPEC_direct_input.md`, part (b)).

## The mechanism and its rival

- run-05/f2-m03: each direction of an RL change acts only as far as the processed text drives its input (right) singular
  vectors; an edit transfers to another domain in proportion to input-subspace drive.
- run-05/f2-m01 (rival): the top-8 directions are a signed finishing dial that acts the same on every text.

Measured transfer (HumanEval+ and MBPP+, 538 problems, Code cue, one sample, result-a1bf75): random rank-8 at 1.5x 331, Math
3.1 top-8 at 1.5x 368, Code 3.1 top-8 at 1.5x 399. Transfer ratio (368 - 331) / (399 - 331) = 0.54. The other way
(result-ac7104, MATH-500 first 250, plain): Code 3.1 top-8 lifts right 107 -> 157 against Math top-8 217, (157 - 107) /
(217 - 107) = 0.45; quick wrong 105 -> 60 against 9, 0.47.

## Claim tested

drive(Math 3.1 top-8 | code text) / drive(Math 3.1 top-8 | math text) is about 0.54.

## Measurement

Drive of a text, as trace-01 (`studies/rlneurons/jobs/xreward_trace.py`, result-a7c052): teacher forcing of the base model
`allenai/Olmo-3-1025-7B` on the base's own answer; at each answer position, for each of the 96 matrices (up, gate, q; 32
layers), `r = ||diag(s) V^T x|| / ||W_base x||`, with s, V the top-8 singular values and input vectors of (donor - base) for that
matrix. Band means over 4 layer bands (0-8, 8-16, 16-24, 24-32), stored in float16 as trace-01 does. Per answer
`D = mean over positions of the mean over 3 matrices and 4 bands`. Answers are cut to their first 6,000 tokens. Positions are
the answer positions only (opening cue included, prompt excluded), as in trace-01.

Conditions (the same vectors as trace-01, built by the same functions): math31 (allenai/Olmo-3.1-7B-RL-Zero-Math), code31
(allenai/Olmo-3.1-7B-RL-Zero-Code), if30, and rand0..2 (math31's s with a random orthonormal V of the same matrix; the seeds are
the matrix names, so the random subspaces are the ones of trace-01).

Texts:
- Code text: the 538 stored base Code-cue answers (job abaybektursun-1114-170304-c03c, seed 51000000, T 1.0 / top-p 1.0;
  sha256 3b18494b...6457), rendered with the Code model's chat template and tokenizer exactly as `run_code_cell.py` did. Rows
  whose re-tokenized length differs from n_new by more than 1 % are left out and listed.
- Math text: the 328 base + cue hard328 answers of trace-01 (job abaybektursun-1115-005830-2145, stored per-position r).
  The new job also re-traces 16 of these math answers (spread over length) to check that the stored values reproduce on the
  new hardware.

Job: `studies/theory/jobs/drive_trace.py` (imports the trace functions from `xreward_trace.py`; that file is not changed). Inputs
committed in `studies/theory/data/drive/` (gzip). Analysis: `studies/theory/analysis/direct_drive.py`, numpy.

## Readout

Primary: `R_math = mean_p D_math31(code text p) / mean_q D_math31(math text q)`, 90 % percentile bootstrap (2,000 resamples,
seed 0; each resample draws code texts and math texts independently with replacement and recomputes both means).

Control (matched null: text length and token statistics alone): `R_rand`, the same ratio for the mean of rand0..2. Also
`R_math / R_rand` with its bootstrap interval (drive of the Math subspace beyond what any rank-8 subspace of the same matrices
gets from the change of text).

Secondary (no verdict): `R_code = mean D_code31(math text) / mean D_code31(code text)`, which f2-m03 puts near 0.45 to 0.54
(the reverse transfer), and `R_code / R_rand^-1`. Also by band and by matrix, and the share of code answers that are cap hits.

## Verdict rule (fixed now)

- R_math in [0.40, 0.70]: supports f2-m03.
- R_math above 0.85: refutes f2-m03 (f2-m01's prediction, near 1).
- Otherwise (below 0.40 or in (0.70, 0.85]): undecided.
- If `R_math / R_rand` falls in a different band than R_math, the verdict is undecided: the ratio then comes from text
  statistics that move every rank-8 subspace, not from the Math subspace.
The rule uses the point estimate; the interval is reported next to it.

## Instrument checks

1. The trace selftest of `xreward_trace.py` (analytic r for x inside V; r = 0 for x orthogonal to V) passes on the GPU.
2. The 16 re-traced math answers reproduce trace-01's per-answer D (math31 and rand mean) within 1 % each.
3. Code prompts re-render to the stored prompt text exactly; the opening cue decodes to the stored prefix text.
4. Every code row is used or listed as left out; counts per benchmark reported.

## Outputs

`studies/theory/results/direct/drive-01/`: `run.json` (commit, command, job id), `metrics.json` (every number above with n and
intervals), `rows.json` (per code text: uid, n positions, cap hit, passed, D for every condition), `examples.json` (two code
texts, one high and one low drive, with their heads). Raw job output stays in `runs/<job id>/` (not committed).
