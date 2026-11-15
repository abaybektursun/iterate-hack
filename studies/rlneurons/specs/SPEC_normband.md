# SPEC normband: is "late layers only finish" a depth effect or a small-edit effect? (follows result-6f7ca3)

Written 2026-11-15 before any run.

## The objection

result-6f7ca3 (SPEC_depth3.md): top-8 Math 3.1 directions at 1.5 on hard328 (cue): layers 0-10 only +7.6 points right
[5.3, 10.0]; layers 22-31 only +1.5 [-1.1, 4.1] and -4.7 cap hits. result-98de28: the L22-31 edit shifts the layer-24 residual
by 0.83 RMS, the L0-10 edit by 6.23. So "late layers only finish" may mean "a small edit only finishes".

## Size, two ways

1. Weight size: the sum of squared Frobenius norms of the applied float32 rank-8 additions in the band (`add_norm` of wsp_edit's
   `edit.json` totals, squared). At 1.5: L0-10 1.062, L22-31 1.202 (`results/xreward/depth3/*/run.json`). The late band is
   already 13 % larger. A weight-matched late cell is scale 1.5 x 1.062 / 1.202 = 1.33 (multiplier 0.88); a weight-matched early
   cell is scale 1.70 (multiplier 1.13). Both are within 13 % of cells already run, so the weight form of the objection is answered
   by the existing cells without a GPU: at more weight change, the late band adds no right answers.
2. Activation size: RMS shift of the layer-24 residual over 6,144 positions of 48 stored base answers (`results/xshift/run-01/readout.json`,
   `rms_shift`): L0-10 6.226, L22-31 0.825, ratio 7.55. This is the form of the objection the runs below test. Assumption: the shift
   grows about linearly with --scale (xshift: Math sizes 0.5 to 3 point the same way, cosine 0.93-0.99). Caveat: layer 24 sees only
   layers 22-24 of the late edit, so this ratio overstates the late band's deficit; matching it is the strict test.

The activation-matched late multiplier is 7.55 (scale 11.3): above 6, so it is capped at 6 (scale 9.0) and an intermediate cell at
3 (scale 4.5) is added.

## Cells

hard328 (n 328), cue, T 1.0 / top-p 1.0, cap 16,384, grader v3, `wsp_edit --recipe top8 --other math31 --rounding stochastic --seed 0`
then `run_cell`, sample 1 (`--seed 3010000`: problem i has seed 3010000 + i), as two jobs `--shard k/2`, joined by
`analysis/shard_join.join`. Pairs with sample 1 of the depth3 cells. In order of priority:

| Cell | Arguments | Multiplier of the 1.5 band cell | Layer-24 RMS shift (linear) |
|---|---|---|---|
| A6 `top8x9_L22-31_math31` | `--layers 22-31 --scale 9.0` | 6 (capped; full match 7.55) | 4.95 |
| B `top8x0.2_L0-10_math31` | `--layers 0-10 --scale 0.2` | 0.133 (= 1 / 7.55) | 0.83 |
| A3 `top8x4.5_L22-31_math31` | `--layers 22-31 --scale 4.5` | 3 (intermediate) | 2.48 |

One sample each: 6 jobs, about 0.5 H100-hour each, about 12 USD.

References (committed rows): base + cue, 4 samples (`results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl`, 158.5 right, 71.5 cap
hits); L0-10 at 1.5, 4 samples (183.5, 92.0); L22-31 at 1.5, 2 samples (163.5, 56.0) (`results/xreward/depth3/`).

## Hypotheses and predictions

D (depth): early layers add right answers, late layers only finish, at any size. S (size): any band adds right answers once the
edit is large enough.

- P1 (D). A6 adds no right answers: A6 minus base < +3 points (right <= 168 of 328), and cuts cap hits (A6 cap hits < 56).
  Refuted if A6 minus base >= +5 points with an interval that excludes 0 (that is S's prediction: about +7, like L0-10).
- P2 (D). A6 is below L0-10 at 1.5 in right answers: A6 minus L0-10 (4 samples) has an interval below 0. Refuted if the interval
  includes 0.
- P3 (D). B still adds more right answers than it cuts cap hits: B right minus base > 0 and B cap hits minus base >= -2 points.
  S predicts the reverse (like L22-31 at 1.5: cap hits down about 5 points, right +1). Refuted if B cap hits minus base <= -4
  points with an interval that excludes 0. One sample resolves about 5 points, so a small B effect is expected and P3 is weak.
- P4 (D). A3 between L22-31 at 1.5 and A6: right minus base < +3 points, cap hits below L22-31 at 1.5.

## Decision rule

Depth wins if P1 and P2 hold. Size wins if A6 or A3 adds >= +5 points right with an interval excluding 0. If A6 breaks the model
(right < 150 or cap hits > 100), A6 is read as "too large", and A3 decides alone. Anything else: inconclusive, and a second sample
of the deciding cell is the next step.

## Analysis

`analysis/normband_readout.py` -> `results/xreward/normband/readout.json` and one run folder per cell: right answers, cap hits,
and paired differences over the 328 problems against base (4 samples), L0-10 at 1.5 (4) and L22-31 at 1.5 (2), with 95 % intervals
from 10,000 bootstrap resamples of the problems (the diff of depth3_readout).
