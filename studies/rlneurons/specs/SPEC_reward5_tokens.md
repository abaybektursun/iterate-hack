# Reward content test, step 2: do RL models of different rewards change the same tokens? (idea-46b68c, work-069eca)

Written 2026-11-15 02:50 UTC, before the scoring job. Branch `reward5`. Step 1 is `specs/SPEC_reward5.md`.

## Question

Code-RL 3.1 and Math-RL 3.1 reach nearly the same MATH-500 score with the cue (450 and 457 of 500, base 410) while their weight
differences from the base have cosine 0.014. Equal scores do not show equal behaviour. Do the two models change the base
model's next-token distribution at the same positions and towards the same tokens?

## Measurement

`jobs/score_tokens.py` scores one fixed set of answers under every model: the 500 first answers (sample 0, attempt 0) of the
cued base on MATH-500 at T 1.0 / top-p 1.0, job `abaybektursun-1114-153825-208b` (405 right, v3). For each answer position t
and model m it stores log p_m(stored token), the most probable token of m and the entropy. r_m(t) = log p_m - log p_base.

Models: base; Math-RL 3.1 (`rl`); Code-RL 3.1 (`code`); the five Olmo 3 RL-Zero models (`math30`, `code30`, `if30`,
`general30`, `mix30`); theta(0.25) = base + 0.25 (RL - base), stochastic rounding; the random matched-norm difference (the model of
the 417 cell: `merge_weights --other rl --random --rounding nearest`, seed 0).

Statistics (`analysis/reward5_tokens.py`), each with a bootstrap over the 500 answers:

1. Pearson and Spearman correlation of r_m with r_math31 over all positions.
2. D = the 10 % of positions with the lowest r_math31 (the tokens Math-RL 3.1 makes least likely relative to the base; 2603.22117
   Sec 3.2 replaces these and reaches the RL score). Share of D where r_m < -0.5. Null: the same share over all positions.
3. At the positions where Math-RL 3.1's most probable token differs from the base's: the share where m's most probable token
   equals Math-RL 3.1's, against the share where it equals the base's.

Instrument checks (must come out as stated, or no statistic is reported): theta(0.25) is on the Math-RL line, so its
correlation with r_math31 must be the highest of all models and above 0.5; the random difference must be the lowest. Ceiling
for an independent run of the same reward: math30 against math31.

## Predictions (each with what refutes it)

- S1 corr(r_code31, r_math31) is at least half of corr(r_math30, r_math31) and its interval lies above the random model's.
  Refuted if its interval overlaps the random model's: the two models reach the same score by different token changes.
- S2 On statistic 3, code31 picks Math-RL 3.1's token more often than the base's token. Refuted if the share for the base's
  token is higher.
- S3 if30 is closer to the random model than to code31 on statistic 1 (the IF reward does not grade reasoning). Refuted if
  corr(r_if30, r_math31) is within the interval of corr(r_code31, r_math31) or above it.

Cost: one GPU job, about 10 models x 5 minutes, about 4 USD.
