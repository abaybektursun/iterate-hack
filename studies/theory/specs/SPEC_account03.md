# Account run 03 (version 6.2): the account against a base-against-base null, with replication

Written before the run (2026-11-15). Code: `lib/round.py` at 537adb7. Folder: `results/account/run-03/`, from
`results/account/run-02` (same cutoff 2026-11-15T04:29:33; `external.md` and `inventory.md` copied unchanged).

## What run 02 showed

The account's 18 shares in 3 new cells were computed and an independent recomputation gave the same 18 numbers
(`results/account/run-02/readout.md`). Four faults: (1) at T 1.0 the gap between the cued base and RL has the same
budget as the gap between the cued base and a fresh sample of itself, in every part, so a gross budget says little
about RL without that null; (2) the "known" budget was a board item's hand labels, and the account's own rules give
other shares on the same problems (0.031 / 0.662 against 0.154 / 0.538); (3) each cell used its own evidence rows, so
reliability against capability was not comparable; (4) 5 of 18 shares were 0 by construction and still scored.

## What changed

The account must hold a null cell (cued base against an independent cued-base sample), state every share also as its
difference from the null cell's share, report gross and net gap counts, fix one evidence set for all cells, apply its
own rules to the board's known cell as a fit (not scored), and declare shares that are 0 by construction (not
scored). A new stage `replicate` recomputes every decisive number and every share from the recipes alone; a number
that differs is left out of the state. The review runs for the account whatever its state.

## Hypotheses

- C1 (replicates): at least 9 of 10 recomputed numbers equal the first computation within 1 %. Refuted below: the
  recipes leave room for two readings.
- C2 (a part exceeds the null): in at least one model cell, at least one part's share differs from the null cell's
  share with 90 % intervals that do not overlap. From run 02 I expect the loop part at T 0.6 and nothing at T 1.0 on
  MATH-500. If no part differs in any cell, the report says the gross gap has the budget of resampling noise.
- C3 (the account predicts the differences): the account survives its own tests (version-5.2 rule), counting only
  shares not 0 by construction. Run 02's account was refuted by one share whose cell was graded v1; with one grader
  and one evidence set I expect it to survive. Refuted otherwise.
- C4 (net gap): the predicted net count (RL-only minus base-only problems) of each model cell is inside its interval
  in at least 2 of 3 cells.
