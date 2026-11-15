# Round 04, rival stages (version 5): each survivor against the strongest rival mechanism

Written before the run (2026-11-15), after round 04's version-4 stages ended and before any rival file exists.
Code: `lib/round.py`, stages `rival`, `defend`, `duel_test`, `score_duel` (commit named in `run.json` of the run).
The stages add new files under `results/engine/round-04/rivals/` and `metrics_v5.json`; no file of the version-4 run
changes.

## Why

Round 04's three survivors (r4-m10, r4-m01, r4-m08) beat two readers with no theory. That null is weak: the readers
have no mechanism at all. Each review then called its survivor "weak" and named a different mechanism that gives the
same computed numbers, with measurements on stored rows that separate the two. Nobody computed them, so the last word
on every survivor was an opinion. Version 5 computes them.

## What runs

For each survivor:

1. `rival`: a blind agent (headless, empty directory, Read and Write only) gets the theory, its computed tests, the
   items before the cutoff, the inventory and the external findings. It writes the strongest different mechanism that
   gives every computed number equally well, and 2 to 4 offline tests where the two mechanisms give different
   numbers, each with an exact recipe on stored rows and the rival's own prediction (value, low, high).
2. `defend`: a fresh blind agent gets only the theory and each test's recipe and unit. It states the theory's
   prediction (value, low, high). It never sees the rival's mechanism or numbers.
3. `duel_test`: scripts written before any row is read, run once, in the environment that has the grader's packages.
4. `score_duel`: per computed test, gain = log density of the theory's prediction minus log density of the rival's
   at the computed value (same sd rule as version 4, clipped to [-3, 3] nats). `beats rival`: 2 or more computed and
   total above 0. `loses to rival`: 2 or more computed and total at or below 0. Otherwise `not tested against rival`.

The rival chooses the tests. That is intended: a theory should hold on the tests its strongest opponent picks. The
rival sees no row file, so it cannot pick a test whose answer it knows.

## Hypotheses

- D1 (the stage runs): at least 2 of the 3 survivors get 2 or more computed rival tests. Refuted below 2.
- D2 (the tests separate): on at least half of the computed tests the gain is at least 1 nat in size. Refuted below
  half: the rival then writes tests on which the two mechanisms say the same.
- D3 (the tests test the theory as its own advocate reads it): on at least half of the tests, the defender's value
  lies on the side of the rival's value that the rival's `theory_should_say` sentence names. Refuted below half: the
  rival then argues against a reading of the theory that the theory's advocate does not hold.
- D4 (outcome, stated to be checked): r4-m10 loses to a rival of the kind its review named (early RL makes answers
  longer, so more reach the cap, with no change of entropy needed); r4-m08 loses to a difficulty rival; r4-m01 is not
  decided (total within 1 nat of 0). Any other outcome refutes D4 and is reported as such.

## Known limits

- One rival per survivor. A theory that beats one rival has not beaten every rival.
- The defender is a model reading the theory. Where the theory is vague, the defender's interval is wide and the test
  decides little; that shows as a small gain, not as a win.
- The test writer can open the row files, as in version 4. Round 04's survivors' version-4 numbers are recomputed
  independently in `results/engine/round-04/replication/`.
