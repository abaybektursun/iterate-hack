# Forecast runs 03-08: mechanisms searched by lens

Written before the runs (2026-11-15, abaybektursun). Code: `lib/forecast.py make --propose 6 --lens "<text>"`,
prompt `lib/prompts/forecast_propose.md`. Everything else as in `SPEC_forecast02.md`.

## Why

In run-02 one job wrote 6 mechanisms; they covered a narrow part of the space (4 of 6 are about stopping, capped samples
or long unfinished attempts), and the rule that each must lie outside both readers' intervals on 3 targets gave 2 of 7 right
disagreements. Run 03-08 scales the search: six jobs, each told one family of causes (a lens), 36 mechanisms in all,
and no forced disagreement.

## What runs

Six `make` runs at the same time, separate processes, one lens each:

| run | lens |
|---|---|
| run-03 | when and how the model stops: token cap, loops, end-of-text, answer markers |
| run-04 | sampling: temperature, top-p, entropy of the next-token distribution, what a vote over samples adds |
| run-05 | weight space: the RL weight change, its top directions, scaling and transplanting it |
| run-06 | training data and objective: what Think-SFT imitation, RL reward and pretraining each put into the model, exposure of problems |
| run-07 | problem structure: difficulty, domain, answer type, length of the needed derivation |
| run-08 | the grader and the measurement itself: extraction, equivalence, seeds, set composition, what a count hides |

```
uv run studies/theory/lib/forecast.py make studies/theory/results/forecast/run-0N --propose 6 --lens "<lens>"
uv run studies/theory/lib/forecast.py score studies/theory/results/forecast/run-0N
```

Each run rebuilds its own targets from the open work items and its own two readers (they may differ between runs).
The proposing job sees the board, the targets, both readers' forecasts, round 07's `facts.json` and `graveyard.json`,
and its lens. Code checks per mechanism: statement at most 80 words; at least 2 board item ids in `rests_on`;
forecasts for at least half the targets with low <= value <= high; every forecast has `vs_readers` starting with
"agree" or "disagree" and a reason. Pairwise difference and "not a failed theory" are left to the prompt. A failing
draft is sent back once; a second failure stops that run (0 of its 6 pass). Scoring as before: log density against
the equal mixture of that run's two readers, clipped to [-3, 3] nats.

## Hypotheses

- L1 (the checks can be met): at least 30 of 36 mechanisms pass the checks. Refuted at 29 or fewer (a stopped run
  counts 0 of 6).
- L2 (some mechanism beats no theory): at least 3 mechanisms have a mean gain above 0 nats over 5 or more scored
  targets. Refuted when, with every target posted that will post, fewer than 3 do. Not decided while fewer than 3
  mechanisms have 5 scored targets.
- L3 (the lenses matter): the best mechanism by mean gain, among those with 5 or more scored targets, comes from a
  lens other than weight space (run-05). Refuted when it comes from run-05.

## Limits

- The best of 36 is selected on these same targets, so its gain is biased upward by the selection. Before any claim
  about it, it must be re-scored on targets that post later (a later run's targets), with no change to its text.
- The six runs read the board at slightly different times, so their targets and readers differ; gains are compared
  across runs only as gains against each run's own readers.
- Mechanisms within one run come from one job, so their errors are correlated; few targets (about 15-20 per run,
  many from the same work items) make a gain on 5 to 10 targets weak evidence.
- Targets whose result posts during `make` stay unscored.
