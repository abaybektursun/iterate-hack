# Direct tests devcut-01 (round-13/s5-a) and devmode-01 (round-13/s5-b)

Surprise (round 13, rank 5): the single autobench agent's best dev100 score after 40 experiments was 84 of 100
(result-6e7b64; karpathy-01 `metrics.json` shows 86 for experiment 10, 84.0 is the mean of the kept method over
7 seeds), the readers forecast 89 [86, 93]. Board work-ab9ae3.

## Claims and why each follows from its own rival only

- **devcut-01 (s5-a).** In the kept method's dev100 runs, the vote-wrong (seed, problem) pairs have more samples cut
  at 4,096 tokens or left unrun by the 360 s budget than difficulty-matched vote-right pairs. Rival b says the
  wrong pairs are lost to a shared wrong mode and puts no length requirement on them, so b predicts D near 0.
- **devmode-01 (s5-b).** On the vote-wrong pairs the largest wrong-answer group holds a large share of the
  answer-bearing samples, more than in the cued base's own 12-sample votes. Rival a says the wrong pairs are lost
  to cut and unrun samples; a predicts few answer-bearing samples and no special concentration (R near 1).

Plan a does **not** depend on the refuted run-02/f2-m01 claim (hard328 solutions need 6,000-14,000 tokens;
refuted by result-ebf7a4). It needs only that on the ~16 wrong pairs per run the samples are cut at 4,096 or
unrun; that is compatible with 67.5 % of solved MATH-500 problems having a right sample of 2,000 tokens or fewer.

## Files

- Kept method: `studies/autobench/results/math500-loop/karpathy-01/solve.py` (12 samples, T 0.6, top-p 0.95,
  first pass 1,536 tokens, continuation to 4,096, guesses of truncated samples at half a vote).
- Per-run aggregates only: `karpathy-01/metrics.json` `rows` (finish counts stop/length/time per run).
  `finals-01/*.json` hold one winning answer per problem (math400, hard328), no per-sample rows.
- Per-sample dev100 rows of the kept method: only in the Modal Volume `autobench-runs` of frustea
  (`karpathy/<nnn>/`), not committed and not reachable from this workspace. Asked frustea on `@frustea` at 22:01 UTC.
- Null for b: `studies/rlneurons/results/votek/math500_base_cue-01/rows.jsonl` (cued base, T 1.0, 12 samples,
  cap 16,384), dev100 indices from `studies/autobench/data/dev100-v1.json`.

## Computation (as planned; unchanged)

a) Per (seed, problem): c = (cut + unrun) / 12, cut = finish `length` at the final 4,096 limit, unrun = finish
`time` or absent. r = right / answer-bearing samples. W = vote-wrong pairs; M = vote-right pairs with r <= 0.75.
D = mean c(W) - mean c(M), 90 % interval from 2,000 bootstraps over problems.
b) Per vote-wrong pair: g = largest wrong group (rln4_lib.agree, first-member rule, sample order) / answer-bearing
samples. G_plain = mean g; G_cue the same on votek rows over dev100 vote-wrong problems (all 500 if fewer than 10).
R = G_plain / G_cue, 90 % interval from 2,000 bootstraps over problems.

## Refuting observations (frozen thresholds from the plans)

- devcut-01 refuted if D < 0.15 or fewer than half of W pairs have c >= 0.25.
- devmode-01 refuted if G_plain < 0.40 or R < 1.3.

## Rule when the inputs are missing

If the per-sample dev100 rows are not reachable before the 22:30 UTC freeze, neither D nor G_plain can be
computed and no committed file bounds them (the run-level counts allow any split of cut samples between W and M).
Then both verdicts are **undecided**, which counts as not holding. The script still computes G_cue (the null of b)
and runs the instruments on the votek rows so the test can be finished in one command once the rows arrive.

## Instrument checks

- b: R computed with votek rows on both sides must be 1.0 and so refuted (R < 1.3).
- a: on votek rows with every sample over 4,096 generated tokens treated as cut (and none unrun), D is computed
  as a control of the code path; it is reported, not used for the verdict.

## Seen before writing

The run-level finish counts of all 40 experiments (kept-method family: about 450 requests ending at a token limit,
first pass at 1,536 and continuations together, and about 90 requests ended by the budget, per run of about
1,700 requests), the finals' per-problem winning answers, and the first rows of votek. No per-sample
dev100 row was seen.
