# SPEC: direct test of round-10/weights-m06, "direction 1 adds finishes, directions 2-8 add right answers"

Board work-2843ca. Written before any number of the readout below was computed. Stored rows only: no GPU job, no
forward pass, no weights.

## The claim

Mechanism `round-10/weights-m06` (plan in `studies/theory/results/wide/round-13/direct_tests.json`): within the
top-8 singular directions per matrix of (RL-Math 3.1 - base), direction 1 carries the format and stop part (fewer cap
hits), directions 2-8 carry the part that raises right answers on problems the model already finishes. Tested
consequence: on hard328 problems where a cued-base sample finished wrong (no cap hit, graded wrong), the rank-1 edit
(direction 1 per matrix, 1x; posted 181/328, 51 cap hits) is right no more often than a second cued-base sample,
while the directions-2-8 edit at 1.5x (posted 183/328, 69 cap hits) is right clearly more often.

## Why only this mechanism

From the plan: no other carried mechanism splits the RL delta by singular direction. The sampling mechanisms
(round-09/grader-m01, run-08/f2-m01) predict only regression to the mean on selected problems, the same for every
edit; the second base sample removes it. The cap and grader mechanisms say nothing about base-finished-wrong
problems. The difficulty-mix mechanisms (round-09/grader-m04, round-10/problems-m04) give no reason why direction 1
should have no right-answer gain while directions 2-8 have one; under them an edit that lifts the total by 17 also
raises the right rate on finished-wrong problems in rough proportion.

Rival not named in the plan: a dose account (smaller edit, smaller effect). TOP1 at 1x is a smaller edit than D28
at 1.5x, so G > 0 alone does not single out this mechanism. The part that does is E_top1 near 0 although TOP1 lifts
the total from 164 to 181. TOP1 at 2x (184/328) is reported as a dose reference; it does not enter the verdict.

## Changes to the plan's computation, and why

1. Selector seed. The plan's selector (`day1/hard328_base_cue_t10-01`, job abaybektursun-1114-151534-e72c) uses
   seeds 3000000 + index. TOP1, TOP1 2x, top-8 1.5x and both random edits use the same seeds; D28 uses
   3010000 + index. A shared seed makes the edit row correlated with the selector row (measured before writing:
   median shared text prefix with the selector is 206 characters for TOP1, 1056 for random rank-8 with 174 of 328
   rows sharing at least 1000 characters, 17 for D28). Conditioning on the selector being wrong then pushes a
   shared-seed edit row toward wrong, which favours the claim for TOP1 and not for D28. Fix: the primary selectors
   are the base samples whose seeds no edit uses, day1_3 `hard328_base_cue_s4r2-01` samples 2 and 3 (seeds
   3020000 and 3030000), pooled. The plan's original selector is reported as a secondary readout.
2. Second base. For selector k in {2, 3}: the other three day1_3 base samples (attempt 0), all on seeds different
   from the selector. b_i,k = mean right over them. Plan step 2 (drop a same-draw second sample) is met by
   construction: no second-base sample shares the selector's seed. The day1 t10 run and day1_3 sample 0 share seed
   3000000 but are not the same draw (same answer and same length on 42 of 328), so in the secondary readout
   with the t10 selector, day1_3 sample 0 is dropped and samples 1-3 are the second base.
3. Pooling. Pairs (selector k, problem i in S_k) pooled over k in {2, 3}; bootstrap by problem (cluster): each
   resampled problem brings all its pairs. 10,000 resamples, numpy default_rng(seed=0), percentile intervals; E_top1,
   E_d28 and G computed on the same resample. The plan's 95 % intervals decide; 90 % intervals are also reported.
4. Right indicator. right = (score_v3 == 1 and cap_hit is false), the same rule for base and edit rows (the plan
   counted capped edit rows as wrong; applying it to base rows too keeps the comparison symmetric). The same numbers
   with the stored score_v3 are reported as a check.

The refuting observation and the thresholds are the plan's, unchanged.

## Files

- Base: `studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl` (attempt 0, 4 samples, 161/160/152/160
  right at attempt 0); plan's selector: `runs/abaybektursun-1114-151534-e72c/answers.jsonl` (164 right, 77 cap hits).
- TOP1: `runs/abaybektursun-1115-000358-d11a/answers.jsonl` (`xreward/edits/top1_math31-01`, 181/51).
- D28: `studies/rlneurons/results/xreward/depth3/top8x1.5_d2-8_math31_s1-01/rows.jsonl` (183/69); text in
  `runs/abaybektursun-1115-122847-824c` and `runs/abaybektursun-1115-122859-b197`.
- References: top-8 1.5x `runs/abaybektursun-1115-031229-5991` (203/25); random rank-8 1x
  `runs/abaybektursun-1114-221040-5f1e` (158/67); random rank-8 1.5x `runs/abaybektursun-1115-090241-0229`
  (159/74); TOP1 2x `runs/abaybektursun-1115-105247-1603` (184/23).
- Every run's right and cap-hit counts are checked against these posted numbers before anything else; a mismatch
  stops the script.

## Computation

1. S_k = problems where base sample k finished (no cap hit, extracted answer non-empty) and score_v3 == 0.
2. For each pair (k, i): b = b_i,k; t = TOP1 right; d = D28 right. E_top1 = 100 mean(t - b), E_d28 = 100 mean(d - b),
   G = E_d28 - E_top1, in points. Same for top-8 1.5x (positive control, result-124593 gave +13.5 with the 4-sample
   dial cell), random rank-8 1x and 1.5x (nulls, expected near 0), TOP1 2x (dose reference).
3. Robustness (plan step 7): each base draw (t10, day1_3 samples 0-3) as selector in turn; every other base draw
   on a different seed is second base; per selector E_top1, E_d28, G, with a flag for edits sharing the selector's
   seed.
4. Context: right / finished over all 328 problems for base (5 draws), TOP1, D28; TOP1 rows with no `\boxed`.

## Verdict rule (frozen, from the plan)

- Refuted if the 95 % lower bound of E_top1 >= +5.0 points (the rank-1 edit itself adds right answers).
- Refuted if the 95 % upper bound of G <= 0.0 points (directions 2-8 do not beat direction 1).
- Holds if neither happens and E_top1 (point) < 0.5 E_d28 (point).
- Otherwise undecided (counts as not holding).

## Instrument checks

- Positive control: top-8 1.5x must give a clearly positive excess (about +13.5).
- Null: random rank-8 at 1x and 1.5x must give an excess whose 95 % interval contains 0.
- Planted check: replacing the TOP1 rows by a copy of the second-base rows must give E_top1 = 0 exactly; replacing
  them by all-right rows must give E_top1 = 100 (1 - mean b) and refute.

## What was seen before writing

Posted totals of every cell; recount of the right and cap-hit totals of the plan's selector (164/77), TOP1
(181/51), D28 (183/69); attempt-0 totals of the 4 base samples; shared text-prefix lengths between the selector and
each edit row; t10 against day1_3 sample 0 identity (42 of 328). No E value, no S set and no per-group rate.
