# SPEC3: candidate 2 and a declared second look at the locked origins

Written 2026-11-15 04:55 UTC, before any run of candidate 2 on origins 2026-10-31..2026-11-05.

## Why a second candidate

After SPEC2 two new inputs were found on the 30 development origins (2026-10-01..2026-10-30, 3,109 cells):

1. The pack's `fastgpu_daily` rows hold the day's maximum price and the number of snapshots beside the day's minimum
   that the series is built from (`prep/intraday.py`, `data/fm2_intraday_v2.csv.gz`). `fm2-20` = `fm2-17` plus
   `fm2_post.py --intraday ... --exit-frac 0.25 --draws 8000`: +0.306 against +0.291, difference +0.015 [0.008, 0.024].
2. A hosted LLM with no tools (`claude-fable-5-2`, training data to June 2026, before every origin) that adjusts
   candidate 1's quantiles from a context dated on or before the origin (`jobs/llm2_*.py`), with the band kept at
   least as wide as candidate 1's: `llm2-03` +0.313 against +0.298, difference +0.015 [0.008, 0.024]; on the 24
   origins not used to choose the rule +0.015 [0.007, 0.025].

## Candidate 2 (fixed)

Quantile average, equal weights, of
- A: `fm2_post.py --hurdle --hurdle-h 1 --scaleway --turnover own --enter abs --intraday studies/gpuprice/data/fm2_intraday_v2.csv.gz --exit-frac 0.25 --draws 8000`
  (seed 0) on the zero-shot Chronos-2 quantile file of the origin (the stored files of SPEC2);
- B: candidate 1 (average of `fm2-17` and `sim2-15`) adjusted by `claude-fable-5-2`, variant `adj`, effort low, rule
  `--wide`. The context of origin D holds only rows dated on or before D; candidate 1's past errors are shown only
  for cells whose target day is on or before D.

Development score: +0.316 (candidate 1: +0.298).

## The look

The locked origins were used once, by SPEC2 (candidate 1: +0.252, last_value_empirical +0.089, 357 cells). This is
the second look and is reported as such. One run, no change to candidate 2 after it.

- H1: candidate 2 beats candidate 1 on the 357 locked cells (pooled skill). Refuted if candidate 2 <= candidate 1.
- H2: A alone beats `fm2-17` alone (+0.270). Refuted if not. Expected small: on these origins verda is far from
  the median of the two series that carry most of the loss.
- H3: B alone beats candidate 1. Refuted if not.

Decision rule: candidate 2 replaces candidate 1 in the submission if its locked pooled skill is at least candidate
1's. Otherwise candidate 1 stays and the development gain is reported as not confirmed.

## Leak rules

As SPEC2. In addition: no model call with a tool; the LLM's raw responses for the event origin are committed, so
the reproduce command replays them without an API call.
