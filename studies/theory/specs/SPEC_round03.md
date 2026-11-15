# Round 03: version 3 on held-out items no earlier round used

Written before the run (2026-11-15). Code: `lib/round.py` at commit 397e64c. Cutoff 2026-11-15T02:59:00 UTC (first written as 02:57; moved before any model call because round 02 had held out
result-5d032f, the Day-1 #3 vote cells, and `standing` requires every item round 02 held out to be evidence now): the
held-out items are the results posted from 02:59 UTC on (the weight-difference cells on the 328, the
self-review and selector results, the WSP-1 screen, the J-lens workspace tests, and what is posted until the run starts).
No earlier round scored on them. Everything rounds 01 and 02 held out is now evidence.

## What changed from round 02

1. Every blind model call is a headless run in an empty directory with only its input files (no git status, no project
   instructions, tools Read and Write only).
2. Score: each claim is a normal density from its 90 % interval; gain = log density at the measured value minus the log
   of the two no-theory readers' mixture, clipped to [-3, 3] nats. Candidate: the 90 % bootstrap interval of a theory's
   total gain is above 0. Passes: its total is also above its reversal's.
3. Fresh advocates write the claims of every theory and of every reversal from the same inputs.
4. Each theory carries at least two offline predictions with a recipe, computed in the round from stored per-problem rows
   (`inventory.md`, stage `test`). A prediction that meets its own refuting condition marks the theory refuted.
5. Each generator gets a different part of the external findings. The four round-02 passers not refuted by review are
   carried forward (r1-all-2, r1-surprises-2, r2-all-2, r2-across-2).

## Hypotheses

- H1: at least one theory is a candidate and beats its reversal on the new items. Refuted if none does.
- H2: round 02's passes were not an accident of the reused items: at least one of the four carried theories has a total
  gain above 0 here. Refuted if all four are at or below 0.
- H3: generators can write computable recipes from the inventory: at least half of the offline predictions of the tested
  theories return a number. Refuted otherwise.
- H4: at least one theory stands after its offline tests and its review. Refuted if every tested theory is refuted,
  published or weak; then the round reports that the engine still produces no theory worth a GPU run.

## Known limits, fixed before the run

- The gain rewards a confident advocate where the no-theory readers are wide; the reversal corrects this only in part,
  because the theory's advocate chooses the targets.
- `inventory`, `test` and `review` run inside the repository. The coordinator reads `inventory.md` for result numbers
  before `generate` uses it.
- The test agent can open the row files while it writes the scripts.
