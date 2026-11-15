# SPEC: retest15, three round-15 consequences of account-2 under engine 16's adversary rule

Branch `syn-retest15` (from `theory`; main is frozen). Written and pushed before any number below was computed by this
test. Stored rows only: no GPU job, no forward pass, no weights. Inputs: the audit of round 15
(`results/direct/audit15-01/audit.md` and `metrics.json` on branch `audit15`) and the round-15 test scripts.

## Rule (engine 16, `verdict16` in `studies/theory/lib/forecast.py`)

Each row carries `interval` (90 %), `range` (the account's), `adversary` (a number) and `n`. Holds only if the interval
lies wholly inside the range, n >= 50 and the interval excludes the adversary's value; inside the range with the
adversary's value in the interval: `not separated`; wholly outside the range: `refuted`; else `undecided`. In the
script the adversary's value is computed first, the statistic second, and every verdict is checked with `verdict16`.

One script: `studies/theory/analysis/direct_retest15.py`, run from the worktree root. Outputs:
`studies/theory/results/direct/retest15-01/` (`metrics.json`, `examples.json`, `run.json`, `rows.json`). Raw texts
(for d1's freshness check and the examples) come from `runs/` of the main checkout and of `iterate-hack-shots`, not
in git.

## 1. s100vote (round-15/account-2/c2), range [5.0, 10.0] points

Rows and vote exactly as `analysis/direct_s100vote.py` (its loaders `step100` and `first_attempts` are imported):
MATH-500, attempt 0 of samples 0-3, grader v3, vote `selector.tie_random` (team plurality vote, random tie-break).

- Adversary (first): accuracy-matched null. For final RL plain (`day1_3/math500_rl-01`) compute per problem the gain
  g = 100 (vote - mean single) and the right count k (0-4); mean g at each k; apply these five means to step 100's
  distribution of k. The audit's value with its own vote is +6.24; this test recomputes it with the team vote.
- Statistic: G = 100 mean over 500 problems of (vote - mean single), 90 % interval from 10,000 bootstrap resamples of
  problems (numpy default_rng(0)), as posted (+7.18 [6.03, 8.37]).
- Also reported (not deciding): step 100's G minus the adversary's value, with the problems resampled jointly for
  step 100 and final RL (the same problem index in both; 10,000 resamples, default_rng(1)).

## 2. merge328 (round-15/account-2/c1), range [0.06, 0.40]

Rows, keys and vote exactly as `analysis/direct_merge328.py` (its `keys`, `v`, `merged` imported): cued base on hard328,
attempt 0 of samples 0-3; cap-hit samples and samples with no answer abstain; kept problems have >= 1 right and >= 1
finished (not cap-hit) wrong sample; D = mean over kept problems of V_S - V_M (V = vote right with random tie-break).

- Adversary (first): wrong answers are shared attractor values. Measured agreement a = share of same-problem pairs of
  finished wrong answers (extracted, score 0, not cap hit) that agree by `votek.agree_table`, over all 328 problems
  (the audit: 0.218 of 257). Model: on each kept problem, keep its number of right keys and of finished wrong answers;
  each wrong answer equals one shared value with probability q, else a value of its own; a pair agrees with
  probability q^2, so q = sqrt(a). The script checks that the simulated pair agreement over the kept problems' wrong
  pairs matches a within 0.01. D under the same vote and tie rule, mean over 2,000 simulations (default_rng(16)): the
  adversary's value.
- Second reference: D if every wrong answer has a value of its own (pair agreement 0); deterministic.
- Statistic: D with 10,000 bootstrap resamples of kept problems, default_rng(0), as posted (0.109 [0.078, 0.142], n 88).
- Also reported: the measured pair agreement among the kept problems' own wrong answers.

## 3. edit0of4 (round-15/account-2/c3) and d1 (editreach-02)

- Same-measurement check: read the input file constants of `analysis/direct_edit0of4.py` and
  `analysis/direct_editreach.py` (by `ast`, without running them) and compare; recompute both problem selections
  (edit0of4: the 121 hard328 problems the cued base gets 0 of 4; d1: those minus problems whose cap32 base text is
  not fresh) and compare with the stored lists in `edit0of4-01/metrics.json` and `editreach-02/metrics.json`. If the
  files are the same and d1's problems are a subset of edit0of4's, edit0of4 earns no separate credit: no row,
  "rejected, same measurement as d1".
- d1, account-2 range [0.60, 1.40]. S = (E - B) / (R - B): E, R per-sample right rates of the edit and RL plain on the
  selected problems (attempt 0, samples 0-3), B the fresh cap32 base sample right within 16,384 tokens.
  - Adversary (first): S expected from accuracy alone: the edit's and RL's lifts over the cued base on all 328 hard328
    problems (attempt-0 samples 0-3 per-sample right rates), S_acc = (acc_edit - acc_base) / (acc_rl - acc_base).
    If the edit's share of RL's lift on the base's 0-of-4 problems is the share of its overall lift, the account adds
    nothing.
  - Statistic: S with 10,000 bootstrap resamples of problems (default_rng(0), one draw for E, R and B), as posted
    (0.88 [0.69, 1.13], n 120).

## Refuting observations

Each consequence is refuted if its 90 % interval lies wholly outside its range, and is `not separated` (no credit) if
the interval contains the adversary's value. Expected from the audit, before this run: c2 not separated (adversary
about +6.2 inside [6.0, 8.4]); c1 and d1 unknown.

## Read raw rows

The script prints 10 raw stored rows (3 step-100 problems, 4 merge328 problems, 3 edit/RL rows); what they show goes
into `metrics.json` under `raw_rows_seen`.
