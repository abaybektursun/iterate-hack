# min-p truncation on MATH-500 (board work-180a48), written 2026-11-15 ~02:05 UTC before any run

Untouched direction on the swarm's idea-basin map: "alternative sampling truncation rules". Every sampling row so far
uses temperature + top-p. min-p (Nguyen et al., arXiv 2407.01082) drops each token whose probability after temperature
is below min_p times the top token's probability. vLLM applies temperature first, then min-p.

## Question

At T 1.0 / top-p 1.0 the base with the opening cue scores 410/500 (v3, seed 41000000, 27 cap hits;
results/day1_wdiff/readout.json `T1_base_cue`). Does removing the low-probability tail with min-p 0.1 raise it, and does
min-p let the base run hotter (T 1.5) without derailing? RL gets the same procedure.

## Arms (MATH-500, n = 500, cue prompt, top-p 1.0, cap 16,384, grader v3, one sample, one seed)

| arm | model | T | min-p | seed | baseline it is read against |
|---|---|---|---|---|---|
| base_mp0.1_T1 | base | 1.0 | 0.1 | 41000000 | T1_base_cue 410/500 (same seed rule, min-p 0) |
| base_mp0.1_T1.5 | base | 1.5 | 0.1 | 41000000 | same |
| rl_mp0.1_T1 | rl | 1.0 | 0.1 | 66000000 | rl_cue-01 457/500 (same seed) |

Seeds equal the baselines' so that the only change is min-p; the RNG stream still diverges at the first truncated
token, so the comparison is paired by problem, not by sample.

## Predictions and refutations

1. base_mp0.1_T1 >= 420/500 (+2 points), from fewer slips on low-probability tokens. Refuted if <= 410.
2. base_mp0.1_T1.5 within 10 of base_mp0.1_T1 (min-p keeps T 1.5 coherent; GSM8K in 2407.01082 Table 2 keeps 18 of
   31 points at T 1.5 while pure temperature goes to 0). Refuted if it falls below 390, or if cap hits exceed 60.
3. RL moves less than base (RL's distribution is already sharp). Refuted if RL gains more points than base.
4. Gap read: if base_mp0.1_T1 - 410 > rl_mp0.1_T1 - 457, min-p closes part of the RL gap at equal procedure.

## Instrument check (smoke, n = 20, before the full runs)

Rows now carry `n_tok_p_lt_1e2` / `n_tok_p_lt_1e3`: the count of sampled tokens whose raw probability (vLLM
raw_logprobs, before truncation; at T 1.0 equal to the sampling distribution) is below 1e-2 / 1e-3. With min-p 0.1
at T 1.0, a token below 1e-2 needs a top token below 0.1, so the count must drop by an order of magnitude against
min-p 0. If the min-p 0.1 smoke shows the same rate as the min-p 0 smoke, min-p is not active and nothing is run.

## Code

`jobs/run_cell.py --min-p` (default 0 keeps every earlier cell unchanged); `jobs/rln4_gen.py` VllmEngine.add merges
the per-request sampling over BASE_SAMPLING so it may set min_p. Results: `results/day1_minp/<arm>-01/`.
