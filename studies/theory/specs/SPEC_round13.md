# Round 13 (engine 13): new mechanisms must pass a direct offline test before they forecast

Written before the round (2026-11-15, about 21:26 UTC, abaybektursun). Board work-d758db. Engine version 13
(`lib/forecast.py round`, `.claude/skills/theory/SKILL.md` version 13, code commit e60eedb), first end-to-end run of
this flow. No GPU jobs; no model forward pass on the laptop.

## Why

In rounds 9 to 12, forecast gain ranked mechanisms whose causes then failed a direct test (README "Direct tests":
5 of the top 6 refuted, 1 held only against a weak null). Engine 13 makes every new rival bring a direct test on
stored data, stops at a gate until each plan has a row in `results/refuted.json` or `results/direct_tested.json`, and
lets only mechanisms that hold a test forecast the open work and design cells.

## Command

```
uv run studies/theory/lib/forecast.py round studies/theory/results/wide/round-13 --from studies/theory/results/wide/round-12 studies/theory/results/wide/round-11 studies/theory/results/wide/round-10 studies/theory/results/wide/round-09 studies/theory/results/forecast/run-0{2,3,4,5,6,7,8} studies/theory/results/forecast/cells-01
```

Run once to the gate (log `runs/round13.log`), run the direct tests (one subagent per plan, at most 6 at once), then
the same command again past the gate.

## Hypotheses (each with the observation that refutes it)

- R1 (new mechanisms hold): at least 2 of the new rival mechanisms hold their direct test against a null stronger than
  random (the base matrix's own top directions, another model's directions, a second base sample, or a matched
  control named in the plan). Refuted at 0 or 1 holding against such a null.
- R2 (speed to the gate): `standing` to the gate under 20 minutes of running (`run.json` "minutes" at the gate, and
  the log). Refuted at 20 or more.
- R3 (consistent with the direct facts): every new rival mechanism's statement agrees with every row of
  `direct_facts.json` (read by the coordinator, one row at a time). Refuted when any rival restates or depends on a
  claim a row refuted.
- R4 (plans are well posed): at least 2 of 3 direct-test plans pass the coordinator's check before running (the
  claim follows from its mechanism, not from its rival or a carried mechanism, and no posted result already decides
  it). Refuted when more than 1 of 3 fail the check.
- R5 (a cell from holders): at least one pair whose both rivals hold gives a cell ranked by disjoint blind intervals
  in `cell_forecasts.json`. Refuted when no pair has both rivals holding, or every such cell's blind intervals overlap.

## What is checked after the round

- Minutes per stage (log timestamps): standing, surprises, targets, direct-test plans, proposals, direct tests,
  forecasts, cells.
- Whether the holders' forecasts differ from both readers on any open target (disjoint 90 % intervals).

## Limits

- A direct test on stored data tests the claim the plan wrote, not every part of the mechanism's cause.
- A surprise is relative to the readers of the folder that forecast it.
- A ranking is the forecasters' own numbers until the cell has run; no cell is run in this round.
