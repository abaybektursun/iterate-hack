# Direct test merge328-01 (round-15/account-2/c1)

Plan: `studies/theory/results/wide/round-15/synthesis_tests.md`, section `round-15/account-2/c1`. Board: work-b38c6b.
Same statistic as scatter4-01 (result-dd9b25, MATH-500, D 0.070 [0.060, 0.081], n 158), now on hard328 with 4 samples.

## Claim

On hard328 the cued base's finished wrong answers also scatter, so the vote over its 4 samples with the real wrong
answers is right clearly more often than the same vote with every finished wrong answer of a problem merged into one
value. account-2 (S4: vote gains come from independent one-off slips) puts D in [0.06, 0.40]. If hard-problem wrong
answers shared one attractor value, D would be about 0.

## Rows

`studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl`, attempt 0 of samples 0-3 (no restarts),
grader v3. Each sample is right (`score_v3 == 1`), finished wrong (an extracted answer, `score_v3 == 0`, not cap hit)
or abstaining (cap hit, or no extracted answer). Keep problems with at least 1 right and at least 1 finished wrong
sample. Plan's expected n: 110. If n < 50 the test cannot hold.

## Computation

1. Answer keys: all right samples share key R. Wrong answers are grouped by the team's agree table
   (`studies/rlneurons/analysis/votek.agree_table`, rln4_lib.agree on norm_v3): a sample joins the group of the first
   earlier sample whose answer agrees with it. Cap-hit samples abstain (primary, the plan's rule).
2. Real vote V_S: plurality over the non-abstaining keys of the 4 samples, ties broken at random, computed exactly as
   the mean over all 24 sample orders of "ties go to the key seen first" (`direct_scatter4.win`), i.e. the
   order-averaged vote of result-f941b8. V_S is the probability that the vote is right.
3. Merged vote V_M: the same, with every finished wrong key replaced by one key W.
4. D = mean over kept problems of (V_S - V_M), probability units.
5. 90 % interval: 10,000 bootstrap resamples of problems, numpy default_rng(0), 5th and 95th percentiles.

## Instrument checks (asserted before the number is read)

- The team vote (`votek.vote`, stored order, no cap abstention) over attempt-0 samples 0-3 gives 192 of 328
  (result-5c961a), and its order average gives 184.6 (result-f941b8).
- On every kept problem with at most one distinct finished wrong key, V_S - V_M = 0.
- Planted null: an S arm whose wrong samples all share one key gives D = 0 exactly.
- Giving every wrong sample its own key can only raise V_S.

## Null

Merged-wrong vote (the base's wrong answers on a problem share one attractor value): D = 0 exactly. Null range
[-0.03, 0.03].

## Ranges fixed in advance

account-2 [0.06, 0.40]; null [-0.03, 0.03].

## Verdict rule (engine 14)

Holds only if the 90 % interval lies wholly inside [0.06, 0.40] and n >= 50. Refuted if the 90 % interval lies wholly
outside [0.06, 0.40]. Otherwise undecided, with the n that would decide stated (interval half-width scaled by
sqrt(n / n_needed)). Also reported: where D falls relative to the null range.

Descriptive, not part of the verdict: D under the team abstention rule (cap-hit samples with an answer vote), counts
of problems with D > 0, = 0, < 0, and the share of finished wrong samples whose key repeats within the problem.

## Outputs

`studies/theory/results/direct/merge328-01/`: metrics.json, examples.json (one problem where merging changes the vote,
one where it does not, real answers), run.json, rows.json.

Script: `uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.theory.analysis.direct_merge328`
from the repository root.
