# Promoted-rival run 01 (version 6.2): the mechanism that won round 04 meets a fresh rival

Written before the run (2026-11-15). Code: `lib/round.py` at 537adb7. Folder: `results/promoted/run-01/`, from
`results/engine/round-04` (cutoff 2026-11-15T04:29:33; `external.md` and `inventory.md` copied from
`results/account/run-02`). Stages: split, standing, score_tests, rival, defend, rival2, defend, duel_test,
score_duel, replicate, review. No new theories are developed; the untested theories are not tested here (round 05
does that).

## Why

Round 04's rival stages ended with one mechanism standing: RL-Zero-Math's first 100 steps install the opening that
the cue forces in the base, with no per-token sharpening, and T 0.6 cap hits follow that opening (`r4-m10-rival`,
+7.81 nats over r4-m10 on 6 tests, 2 of them wins the other side did not expect). Version 5.2 carries such a winner
as the theory and writes a fresh rival against it. This is the first run of that path. It also runs the check that
the board item idea-035a30 names and nobody has run, if the fresh rival asks for it.

## Hypotheses

- P1 (the path runs): `standing` carries `r4-m10-rival` with its 6 computed tests, a fresh rival is written against
  it, and at least 2 rival tests are computed. Refuted otherwise.
- P2 (the tests separate): after the second turn, at least 2 computed tests have the defender's centre outside the
  rival's interval. Round 04: 2 of 16 over three theories.
- P3 (outcome): `r4-m10-rival` is not beaten (total above -2 nats). If it loses, the winner is the new standing
  mechanism and is posted in its place.
- P4 (replication): every duel test with a gain of 1 nat or more in size is recomputed equal within 1 %.
