# Direct test logodds-01: round-10/weights-m01 (theory round 14, carried plan)

Plan: studies/theory/results/wide/round-14/jobs/plan-round-10-weights-m01.json (read from the iterate-hack-theory
checkout; not on origin/theory when this test started).

## Claim

On hard328, the 1.5x top-8 RL-Math edit cuts each problem's cap-hit odds by about the same factor, so problems the base
often runs to the cap keep a larger share of their cap hits than problems it seldom runs to the cap:
Q = ln(e_HI/b_HI) - ln(e_LO/b_LO) > 0.3. A fixed fraction of cap hits removed everywhere (round-10/problems-m04) gives
Q = 0.

## Files and rows

- Base: studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl. Only rows with `attempt == 0` (the
  first attempt, before any restart). 328 problems x 4 samples = 1312 rows.
- Edit: studies/rlneurons/results/day1_3/hard328_top8x1.5_cue_s4-01/rows.jsonl (restarts 0, all rows attempt 0).
  1312 rows.
- Cap-hit flag: field `cap_hit`. In both files `cap_hit == True` exactly when `finish_reason == "length"` and
  `n_new >= 16384` (checked on all 2624 rows before writing this spec).

## Computation

1. Assert 328 problems x 4 samples in each file, one row per (problem, sample).
2. Strata from base samples 0 and 1: k = cap hits among them. HI = k = 2, LO = k = 0.
3. b_S = (cap hits in base samples 2 and 3 over S + 0.5) / (2|S| + 1);
   e_S = (cap hits in all 4 edit samples over S + 0.5) / (4|S| + 1).
4. Q = ln(e_HI/b_HI) - ln(e_LO/b_LO). Also L_S = logit(e_S) - logit(b_S), D = L_HI - L_LO, share kept e_S/b_S.
5. Bootstrap: 10,000 resamples of the 328 problems with replacement, each problem's 4 base and 4 edit samples kept
   together; strata and rates recomputed in each resample. 5th and 95th percentiles of Q and D.
6. n = |HI| + |LO|.
7. Noise null: Q_null = ln(b3_HI/b2_HI) - ln(b3_LO/b2_LO), base sample 3 as the "edit", base sample 2 as the base,
   +0.5 / (|S| + 1) smoothing, same strata, same bootstrap.

## Null and threshold (frozen, copied from the plan)

- Main null: fixed-fraction law, Q = 0. Noise null: Q_null interval, expected to cover 0.
- Threshold Q = 0.3. Holds if n >= 50 and the 90 % interval of Q lies wholly above 0.3; refuted if it lies wholly
  below 0.3; otherwise undecided (report the n that would decide it).

## Instrument check (must fail on a wrong field)

Reproduce the posted counts from the same rows before the readout: base attempt-0 cap hits per sample
[71, 66, 81, 68] (mean 71.5; posted base 71.5 in result-6f7ca3), edit cap hits 76 in total, per sample
[20, 14, 20, 22] (the edit folder's metrics.json `cap_hits` = 76 and readout.json `cap_hits_attempt_0`). Using all base
rows (restarted attempts included) instead of attempt 0 gives 498, which must fail this check.

## Changes from the plan (noted before computing)

1. The plan says the edit count should be "about 25 per sample", stop if off by more than 5. The plan's file gives
   19.0 per sample (76 / 4). The 25 is the 1-sample run studies/rlneurons/results/xreward/edits/top8x1.5_math31-01
   (25 of 328), a different run. The field is not in doubt (three indicators agree, and the count matches the
   folder's own metrics.json exactly), so the test proceeds on the plan's file. The plan's predicted Q of about 0.6
   used c of about -1.2 from 71.5 to 25; with 19 the fixed-log-odds prediction is larger, not smaller.
2. Bootstrap seed: the brief fixes numpy default_rng(0); the plan names seed 20261115. The verdict uses
   default_rng(0); the interval with seed 20261115 is also reported in metrics.json as a check.

## Verdict rule (engine 14, carried plan)

Holds only if the 90 % interval of Q lies wholly above 0.3 and n >= 50; refuted if wholly below 0.3; otherwise
undecided, with the n that would decide it.
