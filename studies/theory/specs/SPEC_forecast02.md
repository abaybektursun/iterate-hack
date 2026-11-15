# Forecast run 02: mechanisms written about the open targets

Written before the run (2026-11-15 14:55 UTC, abaybektursun). Code: `lib/forecast.py make --propose 6`, prompt
`lib/prompts/forecast_propose.md`. Everything else as in `SPEC_forecast01.md`.

## Why

In run-01 the engine's six unrefuted theories said nothing on 16 to 20 of the 20 targets
(`results/forecast/run-01/forecasts.md`), so they cannot be tested on what the team measures. Run-02 changes the
generation side: mechanisms are written about the open targets themselves, after the readers' forecasts are known,
and each must disagree with both readers on at least 3 targets.

## What runs

```
uv run studies/theory/lib/forecast.py make studies/theory/results/forecast/run-02 --propose 6
uv run studies/theory/lib/forecast.py score studies/theory/results/forecast/run-02
```

1. `make` reads the board again and extracts targets from the open work items, minus any number already posted
   (the fresh2026 numbers of result-5251c9 are posted). Nothing is copied from run-01.
2. reader-1 and reader-2 forecast every target, blind, as in run-01. The engine's theories forecast too.
3. One blind job (`forecast_propose`) gets the board items, the targets, both readers' forecasts, and `facts.json`
   and `graveyard.json` of round 07. It writes 6 mechanisms, pairwise different, none restating a failed theory.
   Each: a statement of at most 80 words about what the model does; 2 or more board item ids it rests on; a
   forecast (value, low, high, one line of derivation) for at least half of the targets; on at least 3 targets a
   centre outside both readers' intervals, with the reason the readers are wrong there.
4. Code checks: 6 mechanisms; statement at most 80 words; at least 2 item ids, each on the board; forecasts on at
   least half of the targets with low <= value <= high; at least 3 centres outside both readers' intervals, each with
   a reason. A failing draft is sent back once with the failed conditions; a second failure stops the run.
   Pairwise difference and "not a failed theory" are left to the prompt, not checked in code.
5. The mechanisms become forecasters `f2-m01` ... `f2-m06`, scored by the same rule (log density against the equal
   mixture of the two readers, clipped to [-3, 3] nats).

## Hypotheses

- P1 (the conditions can be met): at least 4 of 6 mechanisms pass the checks on the first or second draft. The
  draft is checked as a whole, so P1 is refuted when the run stops after the send-back (0 of 6 kept), or when fewer
  than 4 mechanisms pass on the first draft and the second fails.
- P2 (a mechanism forecasts better than no theory): at least one mechanism has a mean gain above 0 nats over 5 or
  more scored targets, its disagreeing targets included. Refuted when every mechanism with 5 or more scored targets
  has a mean gain of 0 or below. Not decided while none has 5 scored targets.
- P3 (disagreements are right): over all scored targets where a mechanism's centre lies outside both readers'
  intervals, the measured value lies inside the mechanism's interval in more than 1 of 4 cases. Refuted at 1 in 4
  or fewer, once at least 8 such disagreements are scored. I expect P3 to be refuted: a mechanism written to
  disagree is pushed away from base rates the readers already use.

## Limits

- The proposer sees the readers' forecasts, so its disagreements are chosen against them; this is the intent, and the
  readers did not see the mechanisms.
- All mechanisms come from one job, so their errors are correlated.
- One run; few targets. A gain on 5 to 10 targets is weak evidence.
- Targets whose result posts during `make` stay unscored: `score` reads only items posted after the snapshot.
