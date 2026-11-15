# Experiments run 01 (version 7): rank the open GPU experiments of round 05 and account run 03

Written before the run (2026-11-15). Code: `lib/round.py` at 505bd86 (branch theory-v7). Stages `cross_predict` and
`experiments`, run by name on `results/engine/round-05` (3 pairs of theory and rival) and `results/account/run-03`
(the account and its rival). They write only `experiments/`, `experiments.json` and `experiments.md` in each folder.

## Why

Every number the engine has produced comes from rows the team already stored, and every review ends "weak" or
"partly published". A mechanism fixed before its test is tested most cleanly by a new experiment. Each side of a
pair now states the change to the untrained base that its mechanism implies (prompt, sampling, decoding, selection
among samples; no training, no RL weights), with a predicted count, and predicts the other side's experiments blind.
The list is ranked by how far the two predictions are apart per GPU minute. The coordinator runs the top one.

## Hypotheses

- E1 (something worth running): at least one experiment has a separation of 2 nats or more and costs 30 GPU minutes
  or less. Refuted otherwise: the pairs then disagree about nothing a short run can measure.
- E2 (a lever): at least one intervention predicts a count above the best known base-only count of its cell by more
  than the cell's rerun spread (4 of 500 on MATH-500), with the other side's centre outside its interval. I expect
  this to fail: the smoke run's interventions were votes over more samples, +3 over a known 453.
- E3 (not already run): the top entry of each list is not on the board as a result. Checked by hand against the
  newest board items before anything is run.

## After the ranking

The top entry by separation per GPU minute that passes E3 is posted as an `idea` with both predictions, then run
(AWS PG tool of the parent repository first, then vast.ai; never the laptop, not Modal), recorded in
`experiments_measured.json` of its folder and posted as a `result`. If E1 fails nothing is run and that is reported.
