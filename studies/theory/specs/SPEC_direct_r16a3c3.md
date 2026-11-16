# SPEC direct r16a3c3 (round-16/account-3/c3)

Written before any computation. Plan: `studies/theory/results/wide/round-16/synthesis_tests.md`, section
`## round-16/account-3/c3`.

## Input

`studies/theory/data/direct_host/cap_v1.json` (job abaybektursun-1114-221259-0871, k = 8). 224 rows, one per layer
matrix (32 layers x q, k, v, o, gate, up, down). `cap_left(a>b) = ||U_b^T d_a||^2/||d_a||^2` (output side),
`cap_right(a>b) = ||d_a V_b||^2/||d_a||^2` (input side), d = model - base, U_b, V_b the top-8 singular vectors of b.

## Adversary's value (computed first)

Reference subspace: the RL-Zero-General top-8 entry, key `general30` (the file has no other General entry; the
fallbacks IF-RL and Code 3.0 are not needed). For each matrix,
q_alt = (cap_left(code31>general30) / cap_right(code31>general30)) / (cap_left(think_sft>general30) / cap_right(think_sft>general30)).
Q_alt = median of q_alt over the 224 matrices. Adversary's expected value 2.5.

## Statistic

q = (cap_left(code31>math31) / cap_right(code31>math31)) / (cap_left(think_sft>math31) / cap_right(think_sft>math31)).
Q_C = median of q over the 224 matrices, unitless. n = 224 (unit: matrix). 90 % interval: 5th-95th percentile of the
median over 10,000 resamples of matrices with replacement, numpy default_rng(16).

## Ranges (fixed in the plan)

- account-3 (mechanism round-16/account-3/c3): [1.4, 8.0]
- null: [0.8, 1.2]

## Verdict rule (verdict16)

Holds only if the 90 % interval lies wholly inside the range, n >= 50 and the interval excludes the adversary's value;
inside the range but containing the adversary's value: not separated; wholly outside the range: refuted; else
undecided.

## Outputs

`studies/theory/results/direct/r16a3c3-01/`: metrics.json, examples.json, run.json, rows.json.
Script: `studies/theory/analysis/direct_r16a3c3.py`.
