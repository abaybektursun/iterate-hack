# Account run 02 (version 6.1): the account must predict budgets nobody tabulated

Written before the run (2026-11-15). Code: `lib/round.py` at 856971b. Folder: `results/account/run-02/`, from
`results/account/run-01` (same cutoff 2026-11-15T04:29:33; `external.md` and `inventory.md` copied unchanged).

## What run 01 showed

The account chose the one cell whose budget the board already gives (MATH-500, T 1.0, cued base against RL, 65 gap
problems) and restated it: its five share predictions equal both no-theory readers' to three digits. State `no gain`,
-1.30 nats, 9 of 9 computed (`results/account/run-01/metrics_v4.json`). An agent asked for an account that can be
wrong makes it safe by making it narrow.

## What changed

One list of parts, applied to at least 3 cells that differ in problem set, sampling or model pair. A budget the
board already gives is input (`known`), not a prediction. Predictions are the shares in cells with no budget on the
board, at least 6 in at least 2 cells, each with one sentence on which shares move against the known cell and why.
The run-01 account with its measured shares is given as the incumbent.

## Hypotheses

- B1 (spans): the account predicts shares in at least 2 cells that no board item tabulates, and the readers' centres
  differ from the account's value by more than 2 % on at least half of those share predictions. Refuted otherwise:
  the numbers were guessable without the account.
- B2 (computable): at least three quarters of its offline predictions return a number.
- B3 (the transfer is right): the account survives its own tests by the version-5.2 rule. I expect this to fail on
  at least one cell; the measured budgets of the new cells are the result either way.
- B4 (useful): at least one new cell's measured budget differs from the known cell's by a share change of 0.15 or
  more in some part, with intervals that do not overlap. Refuted if every cell has the known cell's budget within
  noise: then the budget does not depend on set, temperature or checkpoint, which is itself reported.
