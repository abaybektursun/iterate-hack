# Round 04: version 4, computed tests on stored rows as the main test

Written before the run (2026-11-15). Code: `lib/round.py` at commit bb43116 (version 4). Reason for the redesign:
`results/engine/round-03/diagnosis.md`. Cutoff: one second after the newest item round 03 held out, so every item an
earlier round scored on is evidence. The held-out items after it are used only to remove survivors (two strikes).

## What changed from round 03

1. Main test: each theory states at least 3 offline predictions with an exact recipe on stored per-problem rows, fixed
   (sha256) before any row is read. Scripts compute them for every theory. Two blind readers with no theory predict the
   same quantities from the recipes alone. States: refuted (a refuting condition met, or two predictions outside their
   intervals), survives (at least 2 computed, none refuted, total log gain above 0), no gain, untested.
2. Diversity by construction: one blind agent lists 12 pairwise different mechanisms, given every earlier theory and
   why it failed (`graveyard.json`, 32 entries); 12 blind agents each develop one, and may abandon it.
3. External findings are given as mechanisms only, with no sentence about the team's models.
4. The inventory names the fetch command that works for each row file (S3 profile, Modal volume).

## Hypotheses

- H1 (diversity): the developed theories hold at least 6 different mechanisms, grouped by the diagnosis agent with the
  rule "one experiment could separate them". Round 03 had 2 among 10. Refuted below 6.
- H2 (the test runs): at least half of all offline predictions return a number. Round 03: 0 of 3. Refuted below half.
- H3 (the test can fail a theory): at least one theory is refuted by its own computed predictions. If none is, the
  predictions are too safe and the test confirms nothing.
- H4 (a theory survives): at least one theory survives the computed tests with a total gain above 0 and is not judged
  refuted or published by its review. Refuted if none: the report then says the engine has produced no surviving
  theory in four rounds.

## Known limits, fixed before the run

- The agent that writes a test script can open the row files; it is told to write the script from the recipe before
  running anything, and the script is run once by round.py.
- The two no-theory readers behave almost as one reader (round 03: centres differ by a median 1.8 %).
- A theory has 3 to 4 offline predictions, so a total gain above 0 can rest on one prediction. The table prints every
  computed prediction; a survivor is reported with its number of computed tests.
