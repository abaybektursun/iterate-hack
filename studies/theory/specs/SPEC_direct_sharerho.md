# SPEC: direct test sharerho, round-15/account-1/c2

Board work-69dcc2 (idea work-4948a7). Theory round 15, plan section `round-15/account-1/c2` of
`studies/theory/results/wide/round-15/synthesis_tests.md`. Written before the statistic was computed. Stored rows
only: no GPU job, no forward pass, no weights.

## The claim

Account-1 (S1): concentration is set by which base inputs the model's own samples drive. Consequence: the matrices
where Math-RL concentrates its weight change most (high top-8 share) should also be the ones where an unrelated
on-policy reward (IF) concentrates most, beyond what Math-RL shares with off-policy Think-SFT.

## Prior results checked

result-82eb02 and reward-01 (`studies/theory/README.md`, "Direct tests") give only the mean top-8 share over the 224
matrices per model (Math 3.1 0.118, IF 0.206, Think-SFT 0.030). `tools/recall.py` finds no per-matrix correlation
between rewards. No posted number decides this statistic.

## Rows

`studies/theory/data/direct_reward/top8_share_v1.json`: 224 rows (32 layers x 7 module families q, k, v, o, gate,
up, down), field `top8_share` = share of the squared singular values of (model - base) in the top 8. Keys used:
`math31` (RL-Zero-Math 3.1), `if30` (RL-Zero-IF, the only IF key stored), `think_sft` (Think-SFT). n = 224 matrices.

## Computation

1. For each key, subtract from each matrix's top-8 share the median share of its module family over the 32 layers.
2. Spearman rho over the 224 matrices of Math 3.1 vs IF residuals (rho_IF) and of Math 3.1 vs Think-SFT residuals
   (rho_SFT).
3. Statistic D = rho_IF - rho_SFT (unitless).
4. 90 % interval: resample matrices with replacement 10,000 times (seed 0, the same draw for both rhos), recompute D,
   5th and 95th percentiles. Family medians are not recomputed inside the resample (residuals fixed at step 1).
5. Secondary: each rho alone with its interval; the same rhos on raw shares (no centring); rho(IF, Think-SFT).

## Null

Think-SFT's per-matrix pattern shares as much with Math-RL as IF-RL does: D about 0. Null range [-0.1, 0.1].

## Ranges fixed in advance

account-1 [0.15, 1.0]; null [-0.1, 0.1].

## Verdict rule (engine 14)

Holds only if the 90 % interval lies wholly inside [0.15, 1.0] and n >= 50. Refuted if the 90 % interval lies wholly
outside [0.15, 1.0]. Otherwise undecided, with the n that would decide (interval half-width scaled by sqrt(224/n)).
Also report where D falls relative to the null range.

## Outputs

`studies/theory/results/direct/sharerho-01/`: `metrics.json`, `examples.json` (two real rows), `run.json`,
`rows.json`. Script `studies/theory/analysis/direct_sharerho.py`.
