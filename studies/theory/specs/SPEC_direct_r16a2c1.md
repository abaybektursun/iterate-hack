# Direct test r16a2c1 (round-16/account-2/c1)

Written before any computation. Plan: `studies/theory/results/wide/round-16/synthesis_tests.md`, section
`## round-16/account-2/c1`.

## Claim (account-2)

The input side of RL's top-8 pairs is fixed by the base's activations, so any training on step-by-step text lands
there; the output side is chosen by the reward. Think-SFT should therefore sit in Math 3.1's top-8 subspace much
less on the output side than on the input side, relative to Math 3.0.

## Input

`studies/theory/data/direct_host/cap_v1.json` (job abaybektursun-1114-221259-0871, k = 8). Per matrix `cap["a>b"]`
holds cap_left = ||U_b^T d_a||^2/||d_a||^2 and cap_right = ||d_a V_b||^2/||d_a||^2, d_a = model a minus base,
U_b, V_b the top-8 left/right singular vectors of model b's change. Shape is [d_out, d_in].

## Rows

All 224 layer matrices (32 layers x q, k, v, o, gate, up, down); entries `think_sft>math31` and `math30>math31`.

## Statistic

q = [cap_left(TS>M31) / cap_right(TS>M31)] / [cap_left(M30>M31) / cap_right(M30>M31)] per matrix;
Q = median of q over the 224 matrices (unitless). 90 % interval: 10,000 bootstrap resamples of matrices with
replacement, numpy `default_rng(16)`, 5th-95th percentile of the resampled medians. Description only: the same Q with
Code 3.1 (`code31>math31`) in place of Think-SFT.

## Ranges (fixed in the plan)

- account-2 (round-16/account-2/c1): [0.05, 0.7]
- null: [0.85, 1.25]

## Adversary's value (computed first, without reading cap_left of Think-SFT)

Per matrix: d_out, d_in from the shape; cap_left_TS_alt = 8/d_out; r_TS_alt = (8/d_out)/cap_right(TS>M31);
r_M30 = cap_left(M30>M31)/cap_right(M30>M31); q_alt = r_TS_alt / r_M30; Q_alt = median over 224 matrices.
Plan's expectation: about 0.25.

## Rule (verdict16)

For each mechanism: holds only if the 90 % interval lies wholly inside its range, n >= 50 and the interval excludes
the adversary's value; inside the range but containing the adversary's value: not separated; wholly outside the
range: refuted; else undecided.

## Outputs

`studies/theory/results/direct/r16a2c1-01/`: metrics.json, examples.json, run.json, rows.json.
Script: `studies/theory/analysis/direct_r16a2c1.py`.
