# SPEC round 18: engine 18, accounts tested on weight statistics of held-out matrices

Board work-021070. Branch `theory` only (main is frozen). Written before the run.

## Question

Do accounts of the RL weight change, now required to give at least 2 consequences on the committed per-matrix weights
tables (anatomy, top8_share, cap, xlisten), measured on the 112 explore matrices of `data/split_matrices_v1.json` and
tested on the 112 test matrices against a blind adversary's value, separate from plain alternatives (size of the
change, module, layer, chance overlap, the base's own spectrum) where 17 rounds of sampling-row consequences did not?

## Run

```
PYTHONUNBUFFERED=1 uv run studies/theory/lib/forecast.py synthesis studies/theory/results/wide/round-18 --from studies/theory/results/wide/round-17 studies/theory/results/wide/round-16 studies/theory/results/wide/round-15 studies/theory/results/wide/round-14 studies/theory/results/wide/round-13 studies/theory/results/wide/round-12 studies/theory/results/wide/round-11 studies/theory/results/wide/round-10 studies/theory/results/wide/round-09 studies/theory/results/forecast/run-0{2,3,4,5,6,7,8} studies/theory/results/forecast/cells-01
```

Then one offline test per surviving consequence (subagents, opus, at most 9 at once; weights tests load
`rows.weights(table, "test")` only; adversary's test value first; 90 % bootstrap over test matrices, 2000 resamples),
rows through `forecast.py add-rows`, rerun for `synthesis.md`.

## Hypotheses and the observations that refute them

- H1: at least 3 `weights` consequences survive the tightened drop rule (adversary's explore value outside both the
  account's explore interval and its range). Refuted by: 2 or fewer survive.
- H2: at least 2 `weights` consequences hold on the test matrices (90 % interval inside the range, n >= 25, interval
  excludes the adversary's test value). Refuted by: 1 or 0 hold.
- H3: `weights` consequences survive the drop rule at a higher rate than round 17's sampling-row consequences (2 of 9).
  Refuted by: survival rate of weights consequences at or below 2 / 9.
- H4: the top cell of `weights_cells.md` has the account's and the adversary's predictions at least 2 interval widths
  apart (|difference| / wider 90 % interval >= 2). Refuted by: a gap under 2.
- H5: a matrix split leaks little: for every tested weights consequence, the test value lies within the explore
  interval widened by sqrt(2). Refuted by: a test value outside it in more than one test.
- H6: the round (start to `synthesis.md`) takes at most 75 minutes. Refuted by: more than 75.

## Job (top weights cell only)

Submit one weights-only job (`ih submit l40s-small --hours 1`, at most 30 GPU minutes, no generation, a pushed commit of
`theory`) only if the top cell's predictions are at least 2 interval widths apart, an existing rlneurons weights-only job
computes it with existing flags, and `ih ls` shows at most 5 running jobs. Otherwise list the cell and run nothing.

## Outputs

`results/wide/round-18/`: account, marks, adversary, plan files, `weights_cells.md`, `synthesis.md`, `run.json`,
`round18.log`; tests in `specs/SPEC_direct_r18<a><c>.md`, `analysis/direct_r18<a><c>.py`, `results/direct/r18<a><c>-01/`.
