# Direct test r16a1c3 (round-16/account-1/c3), written before any computation

Plan: `results/wide/round-16/synthesis_tests.json`, name `round-16/account-1/c3` (owner account-1).

Claim (account-1): where the RL change concentrates is set by which matrices step-by-step text drives, not by the
reward; Code-RL 3.1's per-matrix top-8 share pattern, family medians removed, follows Think-SFT's and not IF-RL's.

Data: `studies/theory/data/direct_reward/top8_share_v1.json` (job abaybektursun-1114-221259-0871). Keys used:
`code31` (Code-RL 3.1), `math31` (Math-RL 3.1, adversary only), `think_sft` (Think-SFT), `if30` (IF-RL; the file
holds only the 3.0 IF run, the same key result-caa23d used).

Rows: all 224 layer matrices (32 layers x 7 families q, k, v, o, gate, up, down). Unit: one matrix.

Preprocessing: within each module family, subtract that family's median top-8 share, per key.

Statistic: D3 = Spearman rho(code31, think_sft) - Spearman rho(code31, if30) over the 224 residuals (unitless).
Interval: 10,000 bootstrap resamples of matrices with replacement (the same draw for both rhos),
`numpy.random.default_rng(16)`, 5th-95th percentile.

Ranges (fixed by the plan): account-1 [0.15, 1.0]; null [-0.1, 0.1].

Adversary (covariate; computed first): Code 3.1 is Math 3.1 plus noise unrelated to Think-SFT and IF.
D_M = rho(math31, think_sft) - rho(math31, if30) (should reproduce result-caa23d, 0.604);
r_CM = rho(code31, math31); adversary value = r_CM x D_M. All on the same 224 residuals.

Rule (verdict16): holds only if the 90 % interval lies wholly inside [0.15, 1.0], n >= 50 and the interval excludes
the adversary's value; inside the range but containing the adversary's value: not separated; wholly outside the
range: refuted; else undecided.

Outputs: `studies/theory/results/direct/r16a1c3-01/` (metrics.json, examples.json, run.json, rows.json).
Script: `studies/theory/analysis/direct_r16a1c3.py`.
