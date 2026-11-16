# Direct test r16a1c1 (theory round 16, round-16/account-1/c1)

Written before any number was computed. Plan: section `## round-16/account-1/c1` of
`studies/theory/results/wide/round-16/synthesis_tests.md` (branch `theory`). Offline: stored rows only.

## Statistic

D1 = mean over problems of (c - u), a fraction of samples (0-1). c = right rate (grader v3) of the 4 RL step-100 cue
samples; u = right rate of the step-100 plain samples that do not open deliberatively.

## Rows

MATH-500 problems where at least 1 of the 4 step-100 plain samples does not open deliberatively. Planned n 70.
Plain sample 0: `studies/rlneurons/results/ckptcue/s0100_plain-01/per_problem.json`; samples 1-3:
`studies/rlneurons/results/ckptcue/s0100_plain_s123-01/rows.jsonl`. Cue sample 0: `s0100_cue-01/per_problem.json`;
samples 1-3: `s0100_cue_s123-01/rows.jsonl`. Grades are `score_v3` of these committed files.

Flag rule (plan's wording): deliberative = the first 240 characters of the completion hold Okay, Hmm, Let me, Let's,
Wait, First or Alright (case-sensitive, word boundaries) before any equation ($, =, `\(`, `\[`) or 'Answer'. The
committed rows store only the first 30 characters of each completion, so the 240-character openings are read from the
raw answers: `runs/abaybektursun-1115-064532-6a2f/answers.jsonl` (sample 0, worktree `iterate-hack-ckpt`) and
`runs/abaybektursun-1115-102945-9b20/answers.jsonl` (samples 1-3, copied from the Modal Volume with `gpu.py get`).
Each raw row's `score_v3` must equal the committed grade (asserted). Sensitivity line only: the word list of the
result-1f98b0 code (`direct_t3open.py`: Okay, Alright, Hmm, Let me, Let's, I need to; no 'Answer' stop).

## Interval

10,000 bootstrap resamples of problems, numpy `default_rng(16)`, 5th to 95th percentile. Null D0 = mean(c - o) on the
problems that also have >= 1 flagged plain sample, o = right rate of the flagged plain samples, same bootstrap.

## Ranges (fixed in the plan)

account-1 (round-16/account-1/c1) [0.15, 0.75]; account-2 (round-16/account-2/deny-account-1-c1) [-0.10, 0.12];
null [-0.08, 0.08].

## Adversary's value (computed first)

1) Qualifying problems from the plain openings only (no grade read). 2) Flag base T3 openings (`t3_start`) in
`studies/rlneurons/results/rln4/t1_t3_items-01/per_problem.json` with the same rule. 3) On qualifying problems with
an unflagged T3, g_base = mean(T1 right - T3 right); if fewer than 30, all 500 problems with an unflagged T3.
4) s = mean over the same problems of (step-100 cue right rate over 4 samples - base T1 right); if the subset was too
small, s = 0.031. 5) Adversary value = g_base + s.

## Rule (verdict16)

Per mechanism: holds only if the 90 % interval lies wholly inside the range, n >= 50 and the interval excludes the
adversary's value; inside the range but containing it: not separated; wholly outside: refuted; else undecided.

Script: `studies/theory/analysis/direct_r16a1c1.py`. Output: `studies/theory/results/direct/r16a1c1-01/`.
