# SPEC round 19: engine 19, accounts and covariate-only adversaries forecast the team's open work

Board work-7f9d79. Branch `theory` only (main is frozen). Written before the run. No GPU job, no model forward pass on
the laptop: every job is a headless `claude -p` text job.

## Question

Rounds 17 and 18 dropped or failed to separate 18 of 18 consequences: on a statistic both sides have seen, the adversary
fits it. Do accounts of the RL weight change separate from a covariate-only forecaster (stored rows, accuracy, length,
difficulty, edit norm, module type; no RL sample or RL-derived edit as predictor) on numbers neither has seen: the
open work items' weight-edit cells and new samples, which post within hours?

## Run

```
PYTHONUNBUFFERED=1 uv run studies/theory/lib/forecast.py synthesis studies/theory/results/wide/round-19 --from studies/theory/results/wide/round-18 studies/theory/results/wide/round-17 studies/theory/results/wide/round-16 studies/theory/results/wide/round-15 studies/theory/results/wide/round-14 studies/theory/results/wide/round-13 studies/theory/results/wide/round-12 studies/theory/results/wide/round-11 studies/theory/results/wide/round-10 studies/theory/results/wide/round-09 studies/theory/results/forecast/run-0{2,3,4,5,6,7,8} studies/theory/results/forecast/cells-01
```

Stages: standing, direct facts, explore copy, three accounts beside targets_open, blind markers, open_forecasts
(3 accounts, 3 adversaries, 2 readers, then 3 judges), synthesis.md. `forecasts.json`, `forecasts.md`,
`open_forecasts.md` / `.json` and `open_forecasts/` are committed and pushed the moment they exist. Then one board
`knowledge` item with the top 5 targets and one comment on each deciding work item.

## Hypotheses and the observations that refute them

- H1: at least 3 open targets have the best account and its adversary 1 interval width or more apart (|difference| /
  the wider 90 % interval >= 1). Refuted by: 2 or fewer.
- H2: at least 1 target is "deciding" (the account's and its adversary's 90 % intervals do not overlap). Refuted by: 0.
- H3: when the results post, the best account (highest summed gain over its adversary) gains at least 1 nat over its
  adversary summed over the scored targets (clip3 of the log-density difference per target). Refuted if the
  adversary's summed gain over the readers is higher than the account's on the same targets, or the best account's
  summed gain over its adversary is below 1 nat.
- H4: the judges reject fewer than a third of the adversary forecasts (the prompt's rule is followed). Refuted by: a
  third or more rejected.
- H5: the round, from start to the forecast commit, takes at most 30 minutes. Refuted by: more than 30.

## What is fixed in advance

The density rule (normal, sd = max(width / 3.29, 0.01 max(|value|, 1)), clip to [-3, 3] nats), the targets as the
targets_open job writes them, and that only results posted after the first commit or the written time of
`forecasts.md` count. Targets whose result has not posted when the round's README section is written are reported as
open, and scored by the next round's standing.
