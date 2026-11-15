# Round 12 (engine 11): score the results posted since round 11

Written before the round (2026-11-15, about 20:40 UTC, abaybektursun). Engine version 11 unchanged
(`lib/forecast.py round`, `.claude/skills/theory/SKILL.md` version 11). No GPU jobs.

## Why

Round 11 (board snapshot 20:05:26 UTC) scored only 6 new numbers. Since then these results posted: result-dd9239 and
result-0a0a5a (Think-SFT in its own chat format, hard328 and MATH-500), result-ac7104 (round-09 cells m21 and m18:
Code-RL's 8 directions on math, 60 quick wrong of 250; a 0.125 blend, 316 of 500; rows in
`results/wide/round-09/measured.json`), result-42cc6c (M(2) at cap 32,768: 245 of 328), result-6776d8 (RL's 8
directions on Think-SFT; Math + Code directions on the base), result-1c9e40 (vote over k of 12 base samples), plus
result-851e4e, result-fc6c6a, result-c85311 (no new model measurements). On m21, both readers (25 [10, 45] and
18 [8, 32]) and 8 more forecasters were below the measured 60; only run-05/f2-m06 (45 [28, 64]) held it.

## Command

```
uv run studies/theory/lib/forecast.py round studies/theory/results/wide/round-12 --from studies/theory/results/wide/round-11 studies/theory/results/wide/round-10 studies/theory/results/wide/round-09 studies/theory/results/forecast/run-0{2,3,4,5,6,7,8} studies/theory/results/forecast/cells-01
```

## Hypotheses (each with the observation that refutes it)

- Z1 (new numbers): at least 12 numbers scored in `standing/` from results posted after 20:05:26 UTC, from at least 4
  distinct result ids. Refuted at 11 or fewer numbers, or 3 or fewer distinct results.
- Z2 (a mechanism generalizes): at least one carried mechanism has total gain above 0 on numbers from 8 or more
  distinct results (`standing.json`, `forecast.items`). Refuted when every carried mechanism has 7 or fewer.
- Z3 (new surprises): at least 2 surprises in `surprises.md` that were not in round 11's `surprises.md` (a new
  (result, value) pair). Refuted at 1 or 0.
- Z4 (m21 gets a real rival pair): the m21 surprise (result-ac7104, 60 of 250) is among the proposed surprises, and its
  rival pair, after the duplicate judge (carried stand-ins allowed), has disjoint 90 % intervals in the blind
  forecasts (`cell_forecasts.json` or `forecasts.json`, not the proposal's own numbers) on the cell or target it
  names. Refuted when m21 gets no pair, the pair is dropped, or the blind intervals overlap.
- Z5 (speed): `standing` to `experiments.md` under 25 minutes of running (`run.json` and the log). Refuted at 25 or
  more.

## What is checked after the round

- Each scored forecast's written time against its result's posting time (forecasts written after their result are
  listed as offenders), and whether any number is scored twice in one mechanism's record.

## Limits

- A surprise is relative to the readers of the folder that forecast it.
- Numbers posted between a folder's snapshot and the time its forecasts were written are scored by the engine
  (`find_measured` uses the snapshot time); the forecasters did not see them, but the record rule "measured after
  the forecast" is not checked by the code.
