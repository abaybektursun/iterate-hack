# Direct test r16a2c2 (round-16/account-2/c2), written before any computation

Plan: `studies/theory/results/wide/round-16/synthesis_tests.json`, "name": "round-16/account-2/c2".
Script: `studies/theory/analysis/direct_r16a2c2.py`. Output: `studies/theory/results/direct/r16a2c2-01/`.

## Statistic

D = N(E,R) - N(B,R), with N(X,R) = A(X,R) / sqrt(A(X,X) * A(R,R)). Unitless.
A(X,Y) is the pooled share of same-problem pairs of finished wrong answers that agree: cross pairs between two
models, within (unordered) pairs for one model. E = base + 1.5x top-8 with cue
(`studies/rlneurons/results/day1_3/hard328_top8x1.5_cue_s4-01`), R = RL plain
(`studies/rlneurons/results/day1_3/hard328_rl_plain_s4r2-01`), B = cued base
(`studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01`).

Finished wrong answer: attempt-0 sample 0-3 row with `score_v3 == 0`, `cap_hit` false, `finish_reason != "length"`
(16,384 cap), and a non-empty `extracted_v3`. Two answers agree when math-verify 0.9.0 judges them equal
(`studies.rlneurons.lib.rln4_lib.agree`, which calls `n13_score.grade`; checked in both orders, agree if either
order says equal; the count of pairs where the two orders differ is reported).

## Rows

hard328 problems where each of E, R and B has at least 1 finished wrong answer. Within pairs come from the problems
among these where the model has at least 2. Planned n 90. Fewer than 50 problems: undecided.

## Adversary's value (computed first)

Covariate alternative: accuracy, not RL's directions. T = Think-SFT + cue
(`studies/rlneurons/results/thinkvote/hard328_sft1_cue_s4-01`, 209.0 of 328 per sample). Same rule for finished
wrong answers. Rows: problems where T, R and B each have at least 1. D_T = N(T,R) - N(B,R) on those rows, pooled.
If fewer than 50 problems qualify: problems where T and R each have at least 1, with B's pooled A's from the
consequence's own rows. The adversary expects about 0.13.

## Interval

Bootstrap over problems (the unit), 10,000 resamples, `numpy.random.default_rng(16)`; all five A's and D recomputed
per resample from per-problem pair counts; 90 % interval = 5th-95th percentile.

## Null (plan step 6)

Same D with E replaced by the base's samples 2-3 and B by the base's samples 0-1, both against RL, own rows (problems
where base 2-3, base 0-1 and R each have at least 1 finished wrong answer), same bootstrap. Null range [-0.07, 0.06].
Reported, not a mechanism row.

## Ranges (fixed in the plan)

- account-2 (round-16/account-2/c2): [0.08, 0.6]
- account-3 (round-16/account-3/deny-account-2-c2): [-0.10, 0.07]
- null: [-0.07, 0.06]

## Rule (verdict16)

Per mechanism: holds only if the 90 % interval lies wholly inside the range, n >= 50 and the interval excludes the
adversary's value; inside the range but containing the adversary's value: "not separated"; wholly outside the range:
"refuted"; else "undecided".
