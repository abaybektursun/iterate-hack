---
name: theory
description: Find mechanisms that explain the team's experiments and keep the ones that forecast new numbers. One round runs studies/theory/lib/forecast.py round - six headless Claude jobs in empty directories, one per family of causes, propose mechanisms that must hold against the known numbers; every mechanism and two readers with no theory forecast the numbers the open work items will report; each mechanism designs one GPU cell that separates it from another, everyone forecasts every cell, and the cells are ranked by pairs of families whose intervals do not overlap per GPU minute. The top cells are run, their numbers go into measured.json, and the next round scores every forecast and carries only mechanisms with a positive total gain on 3 or more numbers. Use when the user asks for a theory, an explanation across experiments or what the results mean together, and after every fifth closed result. Writes studies/theory/results/wide/round-<nn>/ and updates studies/theory/README.md.
---

# Theory round (version 9)

A mechanism is one sentence (at most 80 words) on what the model does that explains numbers on the board. It is
judged only by numbers nobody had when it forecast them: the results of the team's open work items, and the cells
the mechanisms design to tell each other apart. Version 9 exists because the old stages (develop, stored-row
tests, duels, review) left no usable theory in rounds 01-08, while six cheap families of 6 mechanisms, scored on 5
new numbers, separated 3 mechanisms at +4.4 to +5.6 nats from one at -12.27 (`specs/SPEC_engine_v9.md`).

## What a round is

1. Propose wide: six jobs at once, one per family of causes (`LENSES` in `lib/forecast.py`: stopping, sampling,
   weights, training, problems, grader), 6 mechanisms each. Each mechanism rests on 2 or more board items and names
   in `holds_against` the two known numbers (board item or `facts.json` entry) nearest to contradicting it.
2. Forecast: two readers with no theory and every mechanism, carried or new, forecast the open targets.
3. Design cells: each mechanism designs one GPU cell it gets right and a named other mechanism gets wrong; one job
   merges cells that are the same run; every mechanism and both readers forecast every cell blind.
4. Run the top cells (`experiments.md`), write their numbers into `measured.json`.
5. Score: the next round's `standing` scores this round's forecasts against the results posted since, and its cells
   against `measured.json`.
6. Carry the winners: total gain above 0 on 3 or more scored numbers. At or below -2 nats on 3 or more: graveyard.
   Every other mechanism is dropped; the six families propose new ones.

## The coordinator's job

Run the command, read `standing.md`, `cells.md` and `experiments.md`, run the top cells, write `measured.json`,
post. Write no mechanism, forecast or cell, and edit no job output. Work in your own worktree, `git pull origin main`
first.

## The commands

`W=studies/theory/results/wide/round-<nn>` (next free number), `P=` the previous wide round.

```
uv run studies/theory/lib/forecast.py round $W --from $P
```

Round 09 (the first) starts from the forecast runs and cells-01:
`--from studies/theory/results/forecast/run-0{2,3,4,5,6,7,8} studies/theory/results/forecast/cells-01`.

| stage | jobs | writes |
|---|---|---|
| `standing` | one score job per `--from` folder with `forecasts.json`, at once | `standing/forecasts-<src>.json/.md`, `standing/cells-<src>.json/.md` (from `measured.json`), `standing.json` (carried mechanisms with their scored rows; every record), `standing.md` (ranked), `graveyard.json` |
| `targets_open` | 1 | `targets.json` (board snapshot time; one target per number an open work item will report), `work.md` |
| `forecast` | 2 readers + 1 per carried mechanism | `jobs/forecast/` |
| `propose` | 6, at once | `jobs/mechanisms-<family>.json`, then `mechanisms.json` (carried + new; ids `<round>/<family>-mNN`), `forecasts.json`, `forecasts.md` |
| `cells` | 1 per family, 1 merge, 2 readers + 1 per family | `cells.json` (proposals, `dropped`, merged cells ranked), `cell_forecasts.json`, `cells.md` |
| `experiments` | none | `experiments.md`: list A, top 10 cells by separation per GPU minute; list B, base-only cells by the highest forecast over the best known base count; each with its command |

A stage whose output exists is skipped, so the same command resumes a stopped round. A job whose output fails its
check is sent back once, then stops the round, except a cell whose command still fails the flag check: it is dropped
and the reason recorded. Job prompts and raw outputs are under the temp folder printed first and named in
`run.json`. Prompts: `lib/prompts/forecast_targets.md`, `forecast.md`, `forecast_propose.md`, `forecast_score.md`,
`cells_propose.md`, `cells_merge.md`, `cells_forecast.md`. `--propose N` sets mechanisms per family (default 6);
`--model-all <model>` overrides every job's model. Smoke test: `--propose 2 --model-all sonnet` in a folder outside
the repository.

## The score

A forecast (value, low, high) is a normal density with sd = max((high - low) / 3.29, 0.01 * max(|value|, 1)). Gain
= log density of the forecast minus log density of the equal mixture of the two readers at the measured value,
clipped to [-3, 3] nats. A forecast whose measured value lies outside its own 90 % interval gains at most 0
(version 9); losses are not capped. A mechanism's record is the sum over every scored number, carried from round to
round. The same cap holds in `round.py` (tests, held-out claims, duels, GPU tests: a side outside its own interval
gains at most 0 there too).

## Cells and the flag check

The proposer gets `jobs.md`: the job rows and "How to run" of `studies/rlneurons/README.md`, and per job file its
flags with their allowed values, parsed from its `add_argument` calls (`lib/cells.py` `job_flags`; a file with no
flags of its own takes those of the job modules it imports, as `run_fresh.py` takes `run_cell.py`'s). A proposed or
merged cell whose command names a job file, flag or `choices` value that does not exist is sent back once, then
dropped (`cells.json` `dropped`). The check does not catch a flag whose values are free text.

Separation of a cell = pairs of forecasters from different families (each reader is its own family) whose 90 %
intervals do not overlap, summed over its readouts. Before running a top cell, check the board for the same run
(`tools/recall.py`, `board.py ls result`).

## Running a cell and writing measured.json

Run a cell with its command from `experiments.md` (`tools/gpu.py` or `tools/vast.py`, never the laptop) in your own
worktree and study folder, as every GPU run (AGENTS.md). Compute each readout as `cells.md` defines it from the job's
rows. Then append one row per readout to `$W/measured.json`, a JSON list:

```
[{"readout": "m03-r1", "measured": 131, "n": 200, "interval": [118, 144], "artifact": "studies/<study>/results/...", "item": "result-xxxxxx"}]
```

`readout` is a readout id of `cells.json`, `measured` a number in the readout's unit, `interval` the measured 90 %
interval or null. `standing` stops on a row that breaks this. Post the number as a `result` with every forecaster's
interval beside it.

## Deep tests (--deep)

For mechanisms already carried with a positive forecast gain, `round.py` runs the version-8 stages (develop into a
theory with offline predictions, stored-row tests against two readers, replication, rival and duel, cross-predicted
GPU experiments, review) on them alone:

```
uv run studies/theory/lib/round.py studies/theory/results/engine/round-<nn> all --cutoff <ISO time> --skip gpuprice \
  --from <previous engine round> --deep $W
```

`--deep` replaces the `mechanisms` job with the wide round's carried mechanisms. The stages and their rules are in
`round.py`'s docstring; `--model-all sonnet --min-targets 3` smoke-tests it outside `studies/`. About 60 to 80 jobs
and 1.5 hours: run it only when a carried mechanism needs a stored-row test before a costly GPU cell.

## What a round delivers and posts

1. `standing.md`: every scored mechanism with scored numbers, inside, total gain, state. Post the carried ones as
   `idea` items (statement, holds_against, record) and the graveyard ones in one `knowledge` item with the numbers
   that refuted them. A wrong forecast is a result.
2. `experiments.md`: the top cell of list A as an `idea` with its command and the forecasts that do not overlap,
   before anyone runs it; run it when it costs at most 30 GPU minutes.
3. `$W/run.json` (commit, command, sources, counts, minutes) and one paragraph in `studies/theory/README.md` in the
   same commit: carried, graveyard, cells proposed, dropped, merged, cells with a non-overlapping pair, minutes.
   Close the `work` item with those numbers and the paths of `standing.md`, `cells.md` and `experiments.md`.

## What a round may claim

- A mechanism's record counts only numbers measured after its forecast was written. Say scored, inside and total gain.
- A cell separates mechanisms only after it is run: before that, the ranking is the mechanisms' own forecasts.
- Forecasts outside a round: `forecast.py make <folder> [--propose N --lens "<text>"]`, `score <folder>
  [--rescore]` and `cells <folder> --from <runs...>` still run alone (results under `results/forecast/`).
