# Direct test r16a3c1 (theory round 16, round-16/account-3/c1)

Written before any number is computed. Plan: `studies/theory/results/wide/round-16/synthesis_tests.md`, section
`## round-16/account-3/c1`.

## Statistic

D = mean over problems of (right rate of the problem's non-deliberative step-100 plain samples minus right of the plain
base's T3 answer), grader v3, a fraction (0-1).

## Rows

MATH-500 problems where the T3 answer (base, plain prompt, T 1.0) is non-deliberative and at least 1 of the 4 step-100
plain samples is non-deliberative. Planned n 60.

Non-deliberative (flag rule of result-1f98b0 as the plan writes it): the first 240 characters of the answer hold none of
Okay / Hmm / Let me / Let's / Wait / First / Alright (case-sensitive, word boundaries) before the first equation
(`$`, `=`, `\(`, `\[`, as in `studies/theory/analysis/direct_t3open.py`) or the word `Answer`. The implemented rule of
result-1f98b0 (`direct_t3open.flagged`: Okay|Alright|Hmm|Let me|Let's|I need to, no `Answer` boundary) is reported as a
sensitivity check, not used for the verdict.

## Inputs

- T3: `studies/rlneurons/results/rln4/t1_t3_items-01/per_problem.json` (`t3_right`, `t3_start` = first 240 characters).
- Step-100 plain sample 0: grades from `studies/rlneurons/results/ckptcue/s0100_plain-01/per_problem.json`.
- Step-100 plain samples 1-3: grades from `studies/rlneurons/results/ckptcue/s0100_plain_s123-01/rows.jsonl`
  (attempt 0).
- The committed step-100 rows store only the first 30 characters of each answer. The first 240 characters come from
  the raw answers: sample 0 `runs/abaybektursun-1115-064532-6a2f/answers.jsonl` (worktree `iterate-hack-ckpt`),
  samples 1-3 `runs/abaybektursun-1115-102945-9b20/answers.jsonl` (copied from the Modal Volume with `gpu.py get`). The
  script checks that the first 30 characters of each raw answer equal the committed `opening`.

## Adversary's value (computed first)

On the same rows (chosen by the flags only), a_i = (number of v3-right step-100 samples among all 4) / 4, t_i = T3
right; D_alt = mean over rows of (a_i - t_i). This is also the plan's accuracy-only value.

## Computation

u_i = right rate of the problem's non-deliberative step-100 samples; D = mean(u_i - t_i). 90 % interval: 10,000
resamples of problems with replacement, numpy default_rng(16), 5th-95th percentile of D. If fewer than 50 problems
qualify, the verdict is undecided.

## Ranges (fixed in the plan)

- account-3 (round-16/account-3/c1): [0.10, 0.38]
- null (switch account): [-0.08, 0.06]

## Verdict rule (verdict16)

For each mechanism: holds only if the 90 % interval lies wholly inside the mechanism's range, n >= 50 and the interval
excludes the adversary's value; inside the range but containing the adversary's value: not separated; wholly outside
the range: refuted; else undecided.

## Outputs

`studies/theory/results/direct/r16a3c1-01/`: `metrics.json`, `examples.json`, `run.json`, `rows.json`.
Script: `studies/theory/analysis/direct_r16a3c1.py`.
