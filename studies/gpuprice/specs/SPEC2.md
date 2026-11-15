# SPEC2: the candidate and its one run on the locked origins (written 2026-11-15 02:25 UTC, before the run)

Candidate, fixed here (ledger `ens-05-avg-fm217-sim215`, +0.298 pooled on the development origins):
the average, quantile by quantile, of

1. `fm2-17`: `amazon/chronos-2` zero-shot on each listing alone, independent draws, median over the listings of
   the series, with three rules on top: at h=1 a listing moves only with its own historical change rate (hurdle),
   Scaleway listings follow the ECB rate, and listings seen before return at their posted price.
   `fm2_post.py --hurdle --hurdle-h 1 --scaleway --turnover own --enter abs`.
2. `sim2-15`: each listing replays its own h-day outcomes, 14-day recency weights, 20 % pooled outcomes, entrants.
   `sim2_own.py --tau 14 --shrink 0.2 --abs-enter 2 --afh`.

Not in the candidate, and why: the LoRA on synthetic series (+0.02 on Chronos alone, +0.001 in the average,
inside the +-0.01 seed noise, and it adds a training step to the reproduce command); the replay pool of fm2-18
(its gain is on origins before 10-16 only); the synthetic-prior network and TabPFN (no gain in the average).

Locked origins: 2026-10-31 to 2026-11-05, horizons 1 (6 origins) and 3 (4 origins); 7 days has no truth in the
pack. They were used once before, for SPEC1 (`results/spec1/late-01/`): 357 cells, `last_value_empirical` +0.089,
SPEC1 +0.061. No forecaster since then was run or tuned on them; `fm2_lib.origins` refuses them unless asked by
name. This is their second and last use.

Hypothesis: the candidate's pooled skill on the 357 cells is above `last_value_empirical` (+0.089). Refuted if it
is +0.089 or lower. Also reported, same cells: each member alone, h=1 and h=3 separately, in-band coverage, and the
bootstrap interval over series of the difference to `last_value_empirical`. Whatever the outcome, the candidate is
not changed after this run; the number goes into the findings as the unseen-origin result.
