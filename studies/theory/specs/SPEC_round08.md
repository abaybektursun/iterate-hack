# Round 08: first round on version 8 (theories forecast the open GPU numbers)

Written before the run (2026-11-15, abaybektursun). Code: `lib/round.py` at the commit of this file (version 8; one
change after the builder's 99d9068: a survivor whose review says "weak" is carried, because only a carried theory can
earn forecast gain). Cutoff 2026-11-15T14:15:27, one second after round 07's result. `--from round-07`.

```
sh studies/theory/jobs/round.sh studies/theory/results/engine/round-08 --version 8 --cutoff 2026-11-15T14:15:27 \
  --skip gpuprice --skip "theory round" --skip "theory skill" --skip "Theory engine" \
  --from studies/theory/results/engine/round-07
```

## Why

Round 07's theories had a number for 0 to 4 of 20 open targets (forecast run 01). The one that did forecast beat both
no-theory readers on a new cell (455 against 456 measured). Version 8 writes mechanisms with the open targets and fixes
every theory's forecasts before the stored-row tests.

## Hypotheses

- K1: at least 12 open targets are found. Refuted below 12.
- K2: at least 6 developed theories carry forecasts for a third of the targets or more. Refuted below 6.
- K3: on at least 5 targets, two theories' forecasts differ by more than both of their intervals. Refuted below 5: the
  theories then all say what the readers say and the open work cannot tell them apart.
- K4 (scored in round 09): at least one theory has a positive forecast gain over 3 or more scored targets. I expect
  this to hold for r5-m03-rival if it is carried and to fail for most new theories.
- K5: the round ends within 75 minutes (round 07: 55).

## Limits

One run. Forecasters and readers read the same board. Targets come from the open work items of one afternoon.
