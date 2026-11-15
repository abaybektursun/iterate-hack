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

## Amendment 1 (before the scored runs): A6 breaks the model; the late cells are 4.5 and 3.0

Smoke runs (sample 1 seeds, `--n`, short caps, not scored): scale 9.0 on L22-31 (job abaybektursun-1115-144958-ed3a, n 4, 512
tokens): 4 of 4 answers are loops of "which which x x". Scale 4.5 (abaybektursun-1115-145226-386e, n 8, 1,024 tokens): 7 of 8
coherent math, 1 drifts into non-words ("pritiku vh such thisi tora ano"). Scale 3.0 (abaybektursun-1115-145240-18fc): 8 of 8
coherent. So the late band cannot be raised to the early band's layer-24 shift (7.55x) without breaking the model. Scored cells,
in order:

| Cell | Arguments | Multiplier | Layer-24 RMS shift (linear) |
|---|---|---|---|
| A3 `top8x4.5_L22-31_math31` | `--layers 22-31 --scale 4.5` | 3 (largest that stays mostly coherent) | 2.48 |
| B `top8x0.2_L0-10_math31` | `--layers 0-10 --scale 0.2` | 0.133 | 0.83 |
| A2 `top8x3_L22-31_math31` | `--layers 22-31 --scale 3.0` | 2 (intermediate) | 1.65 |

P1, P2 now apply to A3, P4 to A2 (between L22-31 at 1.5 and A3). The decision rule reads A3 in place of A6; if A3 is broken (right
< 150 or cap hits > 100), A2 decides. Weight size of A3: add_norm 3.61 (squared 13.0) against L0-10 at 1.5: 1.06 (1.13), 11.5 times.

## Amendment 2 (before these runs): rank cells, so that all 8 = direction 1 + directions 2-8 at equal scale and seeds

Requested by the coordinator after the band jobs were submitted. Existing: direction 1 alone (`top8 --k 1`) only at 1, 2, 3
(sample 0: 181/51, 184/23, 168/10 right/cap hits, `results/xreward/edits/top1*_math31-01/`); directions 2-8 at 1.5 (`top8 --skip 1
--scale 1.5`) only sample 1 (183/69, `results/xreward/depth3/top8x1.5_d2-8_math31_s1-01/`). All layers, same settings as above.

| Cell | Arguments | Sample (seed) |
|---|---|---|
| R1 `top1x1.5_math31` | `--recipe top8 --k 1 --scale 1.5` | 1 (3010000), pairs with directions 2-8 sample 1 |
| R2 `top1x1.5_math31` | same | 0 (3000000) |
| R3 `top8x1.5_d2-8_math31` | `--recipe top8 --skip 1 --scale 1.5` | 0 (3000000) |

- P5 (filed by the coordinator). Direction 1 at 1.5 finishes more than it adds right answers: top1x1.5 cap hits minus base < -8
  points (R1 and R2 pooled), and top1x1.5 right minus directions 2-8 right (samples 0 and 1, paired) < -2 points. Refuted if
  direction 1 at 1.5 is within 2 points of directions 2-8 in right answers, or above.
- My forecast from the direction-1 dial (1x 181, 2x 184 right; 51, 23 cap hits): top1x1.5 about 182 right and 35 cap hits per
  sample, so the right-answer part of P5 is at risk (directions 2-8 had 183). Directions 2-8 sample 0: 180 to 186 right, 60 to 75 cap hits.

## Amendment 3 (before these runs): review cells for result-e18bd8

Requested by a hostile review. Same settings (hard328, T 1.0 / top-p 1.0, cap 16,384, grader v3, two shards per sample).

| Cell | Arguments | Prompt | Sample (seed) | Pairs with |
|---|---|---|---|---|
| S1 `top8x3_L22-31_math31` | `--recipe top8 --layers 22-31 --scale 3.0` | cue | 0 (3000000) | its sample 1; base cue samples 0 and 1 |
| S2 `top1x1.5_math31_plain` | `--recipe top8 --k 1 --scale 1.5` | plain | 1 (3010000) | S2b, S3 |
| S3 `top8x1.5_d2-8_math31_plain` | `--recipe top8 --skip 1 --scale 1.5` | plain | 1 (3010000) | S2b, S2 |
| S2b `base_plain` | `run_cell --model base`, no edit | plain | 1 (3010000) | S2, S3 |

No plain base on this seed scheme exists: the only plain base run on hard328 (`results/day1_hard328/base_plain_T1-01/`) has seed
50000000 and no committed rows, so S2b is added.

- P6 (S1). Right minus base (same seeds, samples 0 and 1 of both) has an interval including 0, and cap hits fall by at least 8
  points. Refuted if S1 alone adds >= +4 points right over the base.
- P7 (S2, S3, objection: the cue already supplies what direction 1 adds). Without the cue, direction 1 adds more right answers over
  the plain base than directions 2-8 do: S2 minus S3 >= +3 points right. If so, the rank result of e18bd8 is specific to the cue.
  Refuted if S3 adds at least as many right answers as S2 (S2 minus S3 <= 0).
- Budget: 8 jobs, about 0.4 H100-hour each, about 14 USD.
