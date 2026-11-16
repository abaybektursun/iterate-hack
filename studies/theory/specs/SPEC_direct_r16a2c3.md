# Direct test r16a2c3: round-16/account-2/c3 against its adversary

Written before any number was computed. Plan: section `## round-16/account-2/c3` of
`studies/theory/results/wide/round-16/synthesis_tests.md` (branch `theory`); the statistic's definition is c2's
(`## round-16/account-2/c2`, steps 1-6). Script: `studies/theory/analysis/direct_r16a2c3.py`. Outputs:
`studies/theory/results/direct/r16a2c3-01/`.

## Models and files (fresh2026, 136 problems, attempt 0, samples 0-3, T 1.0, cap 16,384)

- E, the edit (base + 1.5x top-8 of RL-Zero-Math 3.1, cue): the four one-sample runs listed in
  `studies/rlneurons/results/mixvote/fresh2026_top8x1.5-01/run.json` (`runs/ih-1115-150237-83a4`, `-155322-598b`,
  `-155844-4392`, `-155905-0426`, `answers.jsonl`; not in git). Sample index = (seed - 7000000 - problem_index) / 10000.
- R, RL plain: `studies/rlneurons/results/fresh/rl_plain_s4-01/rows.jsonl`.
- B, cued base: `studies/rlneurons/results/fresh/base_cue_s4-01/rows.jsonl`.
- S, Think-SFT + cue (adversary only): `studies/rlneurons/results/fresh/sft1_cue_s4-01/rows.jsonl`.

## Definitions

- Finished wrong answer: score_v3 = 0, cap_hit false, finish_reason not "length", extracted_v3 present and non-empty.
- Two answers agree when math-verify 0.9.0 judges them equal: `rln4_lib.agree(norm_v3(x), norm_v3(y))` (the team
  grader's equivalence test), with the pair put in sorted string order so the result does not depend on the order.
- A(X,Y), cross: agreeing pairs / all pairs over (finished wrong X) x (finished wrong Y) on the same problem, pooled
  over the rows. A(X,X), within: agreeing unordered pairs / all unordered pairs among X's finished wrong answers, pooled
  over the rows where X has at least 2.
- N(X,R) = A(X,R) / sqrt(A(X,X) * A(R,R)).
- Statistic: D_fresh = N(E,R) - N(B,R). Unitless.

## Rows

fresh2026 problems where E, R and B each have at least 1 finished wrong answer (planned n 85). Within pairs only from
problems among these where that model has at least 2.

## Bootstrap

10,000 resamples of problems with replacement, numpy default_rng(16); recompute all five A's and D in each; 90 %
interval = 5th-95th percentile. Null value (plan step 6): the same D with E replaced by B's samples 2-3 and B by B's
samples 0-1, each against R, on the same rows, same bootstrap.

## Adversary's value (computed first)

Strength covariate: D_alt = N(S,R) - N(B,R) with Think-SFT + cue (S) in place of the edit. Rows: problems where S, R, B
and E each have at least 1 finished wrong answer (the plan's "add the edit as a 4th condition"). Same A's, same N, same
bootstrap (default_rng(16)); the point value is the adversary's value. Expected about 0.2.

## Ranges fixed in advance

- account-2 (round-16/account-2/c3): [0.08, 0.6]
- account-3 (round-16/account-3/deny-account-2-c3): [-0.1, 0.07]
- null: [-0.07, 0.06]

## Rule (verdict16)

For each mechanism: holds only if the 90 % interval lies wholly inside its range, n >= 50 and the interval excludes the
adversary's value; inside the range but containing the adversary's value: not separated; wholly outside the range:
refuted; else undecided.

## Checks

Planted inputs: all wrong answers set to one string gives every A = 1; distinct strings give cross A = 0. Ten raw rows
that enter the statistic are read and described in metrics.json.
