# Round 07: first round on version 7.1 (no account, base-only changes, ranked experiments)

Written before the run (2026-11-15, abaybektursun). Code: `lib/round.py` at main 87d2d4f (version 7.1). Cutoff
2026-11-15T09:09:43, one second after the newest item round 06 held out. `--from round-06` carries the two promoted
rivals (r5-m03-rival, r5-m10-rival). No account (`--with-account` not given): in round 06 the account stages took 68
of 125 minutes and the account lost to a one-axis rival for the second time.

Command:

```
sh studies/theory/jobs/round.sh studies/theory/results/engine/round-07 --version 7 --cutoff 2026-11-15T09:09:43 \
  --skip gpuprice --skip "theory round" --skip "theory skill" --skip "Theory engine" \
  --from studies/theory/results/engine/round-06
```

## Why

Round 06's review of its own survivors (comment on result-8b0706): both rest on one separating duel test, one of them on
22 problems, and neither implies a change to the untrained base. Version 7.1 asks half of the mechanisms for a change
to the base alone at about the same generated tokens, lets a duel be won only on 2 separating tests, and ranks the open
GPU experiments. This round tests whether those changes give theories the team can use.

## Hypotheses

- G1 (time): the round ends within 75 minutes of wall time (round 06: 125). Refuted at 75 or more.
- G2 (mechanisms hold against the board): at most 3 of 12 developers abandon their mechanism (round 06: 6 of 12).
  Refuted at 4 or more.
- G3 (the duel separates): at least one duel has 2 or more separating tests (round 06, re-scored: 0 of 3 duels).
  Refuted at 0: the rival then still writes tests on which both sides say the same.
- G4 (a usable change): `experiments.md` holds at least one change to the untrained base alone, from a theory that is
  not refuted, whose predicted count of right answers on MATH-500 at T 1.0 / top-p 1.0 is above the best count known at
  the same number of samples (one sample: 411 of 500, result-3a3af3; four samples: 453, result-cbe0bc). Refuted if every
  such prediction is at or below the best known count. I expect this to fail: rounds 05 and 06 named no such change.
- G5 (carried theories): at least one of the two carried theories wins a duel on 2 separating tests. Refuted if both
  are refuted, lose, or stay not separated: after two rounds they are then dropped from the next round.

## What is reported whatever the outcome

The minutes per stage, the number of abandoned mechanisms with their reasons, each duel's separating tests with the
size of the smallest group, and the top entries of `experiments.md` with both sides' predictions.

## Limits

Those of SPEC_round04.md and SPEC_round04_duel.md. One run. The measured GPU experiment of round 05 (411 of 500) lies
after the cutoff, so it is a held-out target of this round and not an input.
