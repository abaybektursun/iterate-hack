# Round 14 (engine 14): each rival pair gets one shared offline test with disjoint ranges

Written before the round (2026-11-15, about 22:35 UTC, abaybektursun). Board work-ca83dd. Engine version 14
(`lib/forecast.py round`, `.claude/skills/theory/SKILL.md` version 14, code commit ab7bba4 merged with main at
7355be3), on branch `theory` (main is frozen; nothing goes to main). No GPU jobs; no model forward pass on the laptop.

## Why

In round 13 the two rivals of a pair were tested on different numbers, so both rivals of pair s4 held; several holds
rested on n of 21 to 42; no holder forecast an open target differently from both no-theory readers. Engine 14 gives
each pair one statistic on one set of stored rows with three disjoint ranges (a, b, null; checked in code since
ab7bba4), requires n of 50 or more and the 90 % interval wholly inside a range for a hold, and lets only holders that
forecast something new design cells.

## Command

```
uv run studies/theory/lib/forecast.py round studies/theory/results/wide/round-14 --from studies/theory/results/wide/round-13 studies/theory/results/wide/round-12 studies/theory/results/wide/round-11 studies/theory/results/wide/round-10 studies/theory/results/wide/round-09 studies/theory/results/forecast/run-0{2,3,4,5,6,7,8} studies/theory/results/forecast/cells-01
```

Run in the background to the gate (log `runs/round14.log`), run each pair's shared test and each carried plan (one
opus subagent per plan, at most 6 at once, offline on stored rows), then the same command again past the gate.

## Hypotheses (each with the observation that refutes it)

- H1 (a pair is decided): at least one pair is decided with n of 50 or more: one rival's 90 % interval lies wholly
  inside its range, and that range is apart from the null's range (so the rival beats the null). Refuted when every
  pair is undecided or both rivals are refuted.
- H2 (shared tests separate): no pair has both rivals holding (impossible by construction with disjoint ranges; a
  pair with both holding means a test was run on two different sets of rows). Refuted by any pair with two holds.
- H3 (holders forecast something new): at least one holder forecasts an open target with a 90 % interval outside both
  readers' 90 % intervals (`holders.json`). Refuted when every holder is listed as "holds its test, forecasts nothing
  new".
- H4 (speed to the gate): `standing` to the gate under 20 minutes of running and of wall clock (log times). Refuted at
  20 or more on either.
- H5 (plans are runnable): at least 2 of 3 plans can be computed from files in the repository as written (no rows only
  in a Modal Volume, no proxy). Refuted when more than 1 in 3 end undecided for lack of rows.

## What is checked after the round

- Minutes per stage (log times): standing, surprises, targets, carried plans, proposals, duplicate judge, direct
  tests, forecasts, holders, cells.
- Each pair: statistic, ranges a, b and null, measured value with 90 % interval and n, verdict.
- Each holder and whether it forecasts anything outside both readers' intervals.

## Limits

- A direct test on stored data tests the claim the plan wrote, not every part of the mechanism's cause.
- A surprise is relative to the readers of the folder that forecast it.
- A ranking is the forecasters' own numbers until the cell has run; no cell is run in this round.
