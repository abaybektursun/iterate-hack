# Direct test r17a3c2: mechanism round-17/account-3/c2 (edit length vs RL-Code length on code)

Plan: section "## round-17/account-3/c2" of `studies/theory/results/wide/round-17/synthesis_tests.md`. Board item
work-20d77d. Written and pushed before computing anything on the test half.

## Claim

RL's 8 paired directions carry RL's derivation style; an edit of the same norm in random directions does not. So on
code problems that both pass, the Code-RL top-8 1.5x edit's passing answers are about as long as RL-Code's (ratio
0.855-1.035), while the random rank-8 1.5x edit stays near base length (about 0.67).

## Statistic

Geometric mean over problems of (n_new of the Code top-8 1.5x passing answer / median n_new of RL-Code's passing
answers over 3 seeds). A ratio with no unit.

## Cells (set `code`, TEST half only, loaded with `rows.load("code", <cell>, "test")`)

- edit: `rlneurons/xreward/code_depth/code_top8x1.5_code31`
- RL-Code seeds: `rlneurons/code1/rl_plain` (s51), `rlneurons/xreward/code_hosts_s52/rl_plain`,
  `rlneurons/xreward/code_hosts_s53/rl_plain`
- random-edit null: `rlneurons/xreward/code_depth/code_rand8x1.5_code31` in place of the edit

## Rows

Every row (one per problem per cell) with passed true. Problems where the edit passes and at least one of the 3
RL-Code seeds passes (plan expects n about 198 on the test half).

## Computation

1. For each pid, edit length = n_new of the code_top8x1.5_code31 row if passed. RL length = median n_new over the
   passed rows of the three rl_plain cells (mean of the two middle values when even).
2. Keep pids with both.
3. Statistic = exp(mean of ln(edit / RL)).
4. 90 % interval: 2000 bootstrap resamples of all pids of the test half with replacement (fixed seed 0), recompute
   steps 2-3, 5th and 95th percentiles.

The same computation with the random edit's cell gives the null value.

## Adversary (construction artifact), computed FIRST on the test half

1. Load the three RL-Code cells, one row per pid each.
2. For each seed i and each pid where seed i's row has passed true: take the n_new of the other two seeds' rows that
   passed. If none, skip. Otherwise reference = their median (mean of the two when both passed, the single value when
   one passed). Record ln(n_new_i / reference).
3. Pool the records over all three seeds and all pids.
4. Adversary value = exp(mean of the pooled logs).

Adversary's value on the explore half: 0.9808.

## Frozen ranges (copied from the plan)

account-3 [0.855, 1.035]; null [0.58, 0.8]. n >= 50 problems required.

## Verdict rule (verdict16 of studies/theory/lib/forecast.py)

- 90 % interval wholly outside [0.855, 1.035]: refuted.
- n < 50 or interval not wholly inside the range: undecided.
- Interval inside the range and containing the adversary's test value: not separated.
- Interval inside the range and excluding the adversary's test value: holds.

## Outputs

`studies/theory/results/direct/r17a3c2-01/`: run.json, metrics.json, examples.json, rows.json.
Script: `studies/theory/analysis/direct_r17a3c2.py`.
