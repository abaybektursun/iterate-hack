# Direct test r16a3c2 (theory round 16, round-16/account-3/c2)

Plan: `studies/theory/results/wide/round-16/synthesis_tests.md`, section `## round-16/account-3/c2` (branch `theory`).
Written before any number was computed.

## Claim (account-3)

An m21 answer (base + Code-RL top-8 at 1x, plain prompt, T 1.0) that does not open deliberatively is still right more
often than the plain base's (T3) non-deliberative answer to the same problem.

## Statistic

D_m21 = mean over problems of (m21 right - T3 right), grader v3, as a fraction (0-1), on problems where both answers are
non-deliberative.

## Rows

Problems 0-249 of MATH-500 where both the m21 completion and the T3 answer are non-deliberative. Planned n 65.

- T3: `studies/rlneurons/results/rln4/t1_t3_items-01/per_problem.json` (`t3_start`, its first 240 characters;
  `t3_right`, grader v3).
- m21 right: `studies/theory/results/experiments/cell-r9-m21-01/per_problem.json` (`score_v3`).
- m21 opening text: the job's raw `answers.jsonl` (job abaybektursun-1115-103050-eae1, `runs/` folder, not committed;
  sha256 2900bc85a4e971128dfe4132d017bb5825ff9888a6a4fdfbe00b8334e3da29d4), field `text`, first 240 characters.
  The script asserts its `score_v3` equals the committed per_problem.json.

Flag rule (result-1f98b0, as in `studies/theory/analysis/direct_t3open.py`, imported, not copied): an answer is
deliberative when the case-sensitive regex `\b(Okay|Alright|Hmm|Let me|Let's|I need to)\b` matches in its first 240
characters before the first `$`, `=`, `\(` or `\[`. Non-deliberative = not flagged.

## Computation

1. Join m21 rows to T3 rows by problem index (0-249).
2. Flag both answers on their first 240 characters.
3. Keep problems where both are non-deliberative.
4. D_m21 = mean(m21 right - T3 right).
5. 90 % interval: 10,000 bootstrap resamples of problems, numpy `default_rng(16)`, 5th-95th percentile.
6. Also report the accuracy-only value: on the T3-non-deliberative problems, all m21 rows minus T3 (equals the adversary's value).
   If fewer than 50 problems qualify, the verdict is undecided.

## Ranges (fixed in the plan)

- account-3 (round-16/account-3/c2): [0.1, 0.4]
- null (switch null, D about 0): [-0.07, 0.07]

## Adversary (covariate), computed first

Alternative: m21 is simply more accurate than T3 on the problems where T3 answers non-deliberatively; requiring m21 to be
non-deliberative too adds nothing. Computation: keep problems 0-249 whose T3 answer is non-deliberative (T3 flag only, m21's
opening ignored); A = mean(m21 right) - mean(T3 right) on that set, grader v3. Predicted D_m21 = A. Fallback if the flag
rule cannot be applied: (157 - 107) / 250 = 0.20.

## Verdict rule (verdict16)

For each mechanism: holds only if the 90 % interval lies wholly inside that mechanism's range, n >= 50 and the interval
excludes the adversary's value; inside the range but containing the adversary's value: not separated; wholly outside the
range: refuted; else undecided.

## Outputs

`studies/theory/results/direct/r16a3c2-01/`: metrics.json, examples.json, run.json, rows.json.
Script: `studies/theory/analysis/direct_r16a3c2.py`.
