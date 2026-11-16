# SPEC direct r16a1c2: m21's right rate by opening type on cued-solved problems (round 16, account-1/c2)

Written before any number is computed. Plan: `studies/theory/results/wide/round-16/synthesis_tests.md`,
section `round-16/account-1/c2` (also `synthesis_tests.json`).

## Rows

MATH-500 problems 0-249 whose cued-base T1 answer is right under grader v3 (`t1_right == 1` in
`studies/rlneurons/results/rln4/t1_t3_items-01/per_problem.json`). Planned n about 205; the real count is used.

## Inputs

- m21 (base + 1.0 x Code-RL top-8 pairs, plain prompt, T 1.0, one sample per problem): raw completions of job
  `abaybektursun-1115-103050-eae1` (`runs/abaybektursun-1115-103050-eae1/answers.jsonl`, not committed; a copy is in
  `../iterate-hack-cells-r9b/runs/`). Right = stored `score_v3 == 1`, checked against
  `studies/theory/results/experiments/cell-r9-m21-01/per_problem.json`.
- T1 / T3: `t1_t3_items-01/per_problem.json` (`t1_right`, `t3_right`, `t3_start` = first 240 characters of T3).
- Cued base, 4 attempt-0 samples per problem: `studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl`.

## Flag rule (result-1f98b0)

`flagged()` imported from `studies/theory/analysis/direct_t3open.py`: case-sensitive
`\b(Okay|Alright|Hmm|Let me|Let's|I need to)\b` in the first 240 characters, matching before the first `$`, `=`, `\(`
or `\[` (or no such marker).

## Adversary's value (computed first)

On the kept rows, flag the T3 answer (`t3_start`), not the m21 answer.
G_alt = mean(t3_right | T3 flagged) - mean(t3_right | T3 unflagged). m21 rows are not read for this number.
Expected by the adversary: about 0.48.

## Statistic

Flag each m21 completion's first 240 characters. G = mean(m21 right | flagged) - mean(m21 right | unflagged), as a
fraction. n = number of kept rows (both groups together). 90 % interval: 10,000 bootstrap resamples of the kept rows
(problems), numpy `default_rng(16)`, 5th-95th percentile of G.

Null G0 (reported, not a verdict input): the same contrast with each row's m21 right replaced by the cued base's
per-problem right rate over its 4 attempt-0 samples, same bootstrap.

## Ranges fixed in advance

- account-1 (`round-16/account-1/c2`): [0.20, 0.65]
- account-2 (`round-16/account-2/deny-account-1-c2`): [-0.10, 0.17]
- null: [-0.06, 0.12]

## Verdict rule (verdict16)

For each mechanism: holds if the 90 % interval lies wholly inside its range, n >= 50 and the interval excludes the
adversary's value; inside the range but containing the adversary's value: not separated; wholly outside the range:
refuted; else undecided.

## Outputs

`studies/theory/results/direct/r16a1c2-01/`: metrics.json, examples.json, run.json, rows.json.
Script: `studies/theory/analysis/direct_r16a1c2.py`.
