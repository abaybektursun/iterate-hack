# SPEC round 20: engine 20, accounts, adversaries and readers forecast held-out stored cells

Board work-3ef8bd. Branch `theory` only (main is frozen). Written before the run. No GPU job, no model forward pass on
the laptop: every job is a headless `claude -p` text job.

## Question

Does any account of the RL weight change forecast stored cells it was not shown better than both a covariate
forecaster that may use every stored count as data (RL models and RL-derived edits included, no mechanism) and the two
no-theory readers? 62 test cells of `data/split_cells_v1.json` (28 xreward edit cells, 34 sampling or vote cells) are
withheld from every writer and forecast from their descriptions; their counts are already stored, so the score is
immediate. Round 19's open targets are scored as their results post (work-e340a2 posted result-6fbdaa at 01:42 UTC,
after the 01:38:33 forecast commit; work-4bfe4e is polled until 02:41 UTC).

## Run

```
PYTHONUNBUFFERED=1 uv run studies/theory/lib/forecast.py synthesis studies/theory/results/wide/round-20 --from studies/theory/results/wide/round-19 studies/theory/results/wide/round-18 studies/theory/results/wide/round-17 studies/theory/results/wide/round-16 studies/theory/results/wide/round-15 studies/theory/results/wide/round-14 studies/theory/results/wide/round-13 studies/theory/results/wide/round-12 studies/theory/results/wide/round-11 studies/theory/results/wide/round-10 studies/theory/results/wide/round-09 studies/theory/results/forecast/run-0{2,3,4,5,6,7,8} studies/theory/results/forecast/cells-01
```

Stages: standing (scores round 19's open forecasts against posted results), direct facts (minus facts naming a test
cell), explore copy (minus test cells' rows), three accounts beside targets_open (board titles, DIRECTION and data.md
lines filtered by cell), blind markers, open_forecasts of the open work, heldout (3 accounts, 3 adversaries, 2 readers,
3 judges; scored at once), synthesis.md. Leak check: run.json `leak_check` (account transcripts naming a test cell,
inputs stating one, withheld rows in the explore copy) must be empty; the coordinator also greps the account
transcripts for every test folder name.

## Hypotheses and the observations that refute them

- H1: the best account (ranked by the smaller of its two summed gains) gains at least 1 nat over its adversary AND at
  least 1 nat over the readers' mixture, summed over the held-out cells (n = 62 cells, at least 8 required). Refuted if
  its summed gain over either is below 1 nat, or a reader's summed gain over the mixture is equal or higher than the
  account's.
- H2: the adversary, now allowed RL-edit counts as data, gains more over the readers than in round 19's open forecasts
  could show: its summed gain over the readers' mixture on the held-out cells is above 0. Refuted by: 0 or below.
- H3: on the 28 edit cells alone, the best account's summed gain over its adversary is above 0 (accounts are about the
  RL change, so edits are where a mechanism should help). Refuted by: 0 or below.
- H4: the judges reject fewer than a third of the adversary's held-out forecasts. Refuted by: a third or more.
- H5: no account transcript names a test cell (folder, leaf folder, job id or label), and no writer input states a test
  cell's count. Refuted by: any hit (the round's held-out scores then do not count).
- H6 (round 19's targets): on t03 (vote over 8) and t04 (8 minus 4), each account gains less than 0.5 nat over the
  readers (all forecasts there were within 0.17 widths of each other). Refuted by: an account gaining 0.5 nat or more
  on either.

## What is fixed in advance

The cell split (`data/split_cells_v1.json`, committed in 6d86fb4 before any forecast), each test cell's measured value
(right answers per sample, grader v3, `counts.correct_v3 / samples` of its metrics.json), the density rule (normal,
sd = max(width / 3.29, 0.01 max(|value|, 1)); gain over readers: against their equal mixture, clipped to [-3, 3], at
most 0 outside the forecaster's own interval; gain over adversary: clip3 of the log-density difference), and that an
account "adds something" only with positive summed gain over both. For round 19's open targets only results posted
after 2026-11-16T01:38:33Z count, verified at the artifact; one not posted by 02:41 UTC stays open.
