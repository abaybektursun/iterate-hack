---
name: theory
description: Find mechanisms that explain the team's experiments, keep the ones that forecast new numbers, and turn them into GPU cells on two tracks. One round runs studies/theory/lib/forecast.py round - six headless Claude jobs in empty directories, one per family of causes, propose mechanisms that must hold against the known numbers; a blind judge drops restatements; every mechanism and two readers forecast the numbers the open work items will report; each mechanism designs one cell that separates it from another (track 1, ranked by readouts whose forecasters split with 2 or more families on each side) and each family designs one no-reward route from the untrained base or Think-SFT (track 2, ranked by the median forecast over the best known count at equal tokens). The top cells and routes are run, their numbers go into measured.json, and the next round carries only mechanisms with a positive total gain on numbers from 3 or more board items. Use when the user asks for a theory, an explanation across experiments or what the results mean together, and after every fifth closed result. Writes studies/theory/results/wide/round-<nn>/ and updates studies/theory/README.md.
---

# Theory round (version 10)

A mechanism is one sentence (at most 80 words) on what the model does that explains numbers on the board. It is
judged only by numbers nobody had when it forecast them. The numbers of one board item count as one experiment.
Version 10 (`specs/SPEC_engine_v10.md`) answers round 09: 8 of 10 carried mechanisms rested on one experiment, one
outlier forecaster made every top split, 26 of 36 new mechanisms restated old ones, and 4 of 39 cells changed the
base alone, while `DIRECTION.md` asks for the cheapest route to RL's points that uses no reward.

## What a round is

1. Propose wide: six jobs at once, one per family of causes (`LENSES` in `lib/forecast.py`: stopping, sampling,
   weights, training, problems, grader), 6 mechanisms each, each with `holds_against` (the two known numbers nearest
   to contradicting it). One blind judge drops each new mechanism that restates an earlier one or a graveyard entry
   (`duplicates.json`: pairs with a reason).
2. Forecast: two readers with no theory and every mechanism forecast the open targets.
3. Track 1, cells that separate mechanisms: each mechanism designs one GPU cell it gets right and a named other
   mechanism gets wrong; one job merges cells that are the same run.
4. Track 2, no-reward routes: each family designs one route, a change to the untrained base alone (prompt text,
   opening tokens, decoding, a vote or selection rule, restarts, examples written by the base) or to Think-SFT, with
   the same procedure on RL-Zero-Math, its tokens per problem, right answers on a subset of hard328 and on MATH-500,
   and why it works in terms of the gap's known parts (`gap.md`: result-f39ba8 and the rlneurons "Gap anatomy").
5. Everyone forecasts every cell and route blind. Run the top of each list, write the numbers into `measured.json`.
6. The next round scores everything and carries the winners.

## The coordinator's job

Run the command, read `standing.md`, `duplicates.json`, `cells.md` and `experiments.md`, run the top cells and
routes, write `measured.json`, post. Write no mechanism, forecast, cell or route, and edit no job output. Work in
your own worktree, `git pull origin main` first.

## The commands

`W=studies/theory/results/wide/round-<nn>` (next free number), `P=` the previous wide round. Also name every
forecast run or cells folder with numbers posted since; each folder is read once, so overlaps do not count twice.

```
uv run studies/theory/lib/forecast.py round $W --from $P <other folders>
```

| stage | jobs | writes |
|---|---|---|
| `standing` | one score job per `--from` folder with `forecasts.json`, at once | `standing/<kind>-<src>.json/.md`, `standing.json` (carried mechanisms with their rows, each row with its board item; every record), `standing.md`, `graveyard.json` |
| `targets_open` | 1 | `targets.json`, `work.md` |
| `forecast` | 2 readers + 1 per carried mechanism | `jobs/forecast/` |
| `propose` | 6 at once, then the judge | `jobs/mechanisms-<family>.json`, `duplicates.json`, `mechanisms.json` (ids `<round>/<family>-mNN`), `forecasts.json`, `forecasts.md` |
| `cells` | per family 1 cell job and 1 route job (12 at once), 1 merge, 2 readers + 1 per family | `cells.json` (proposals, `dropped`, `left_out`, cells `r<nn>-mNN`, routes `r<nn>-nNN`, `best_known`), `cell_forecasts.json`, `cells.md` |
| `experiments` | none | `experiments.md`: lists A, B and C with commands |

A stage whose output exists is skipped, so the same command resumes. A job whose output fails its check is sent
back once, then stops the round, except a cell or route whose command still fails the flag check: it is dropped
and the reason recorded. Job prompts and raw outputs stay in the temp folder named in `run.json`. Prompts:
`lib/prompts/forecast_*.md`, `duplicates.md`, `cells_*.md`, `routes_propose.md`. `--propose N` sets mechanisms per
family (default 6); `--model-all <model>` sets every job's model. Smoke test: `--propose 2 --model-all sonnet` in a
folder outside the repository.

## The score and the state rules

A forecast (value, low, high) is a normal density with sd = max((high - low) / 3.29, 0.01 * max(|value|, 1)). Gain
= log density of the forecast minus log density of the equal mixture of the two readers at the measured value,
clipped to [-3, 3] nats; at most 0 when the measured value lies outside the forecast's own 90 % interval. A record
sums every scored number, carried from round to round, one row per (folder, number). Carried: total above 0 on
numbers from 3 or more distinct board items. Graveyard: at or below -2 nats on 2 or more items. Every other
mechanism is dropped.

## The three lists

- A: cells by separation per GPU minute. Forecasters at or below -2 nats are left out; a readout separates when the
  rest split into a low and a high side (every low interval below every high interval) with 2 or more families on
  each side (each reader is its own family).
- B: base-only cells by the highest forecast over the best known base count.
- C: routes by the larger of their two medians minus the best known count at equal or fewer tokens per problem. The
  table (`best_known` in `cells.json`) is built in code from the board's `score: base` lines on hard328 and MATH-500
  at full size, rows that use RL outputs left out, scaled to the route's subset. Think-SFT routes meet the same
  table.

Before running a top entry, check the board for the same run (`tools/recall.py`, `board.py ls result`).

## Jobs and the flag check

`jobs.md` gives the proposers each job file's flags with their allowed values, parsed from its `add_argument` calls
(`lib/cells.py` `job_flags`; `studies/rlneurons/jobs/` and `studies/theory/jobs/`). Routes run with
`studies/theory/jobs/free_cell.py` (`--model base|rl|think_sft`, `--prompt-suffix`, `--opening-text`,
`--temperature`, `--top-p`, `--min-p`, `--repetition-penalty`, `--max-tokens`, `--samples`, `--seed`, `--set`, `--n`,
`--shard`, `--dry-run`) or `run_cell.py` (cue, `--shots`, `--restarts`). A vote or selection rule is computed from
the rows afterwards. A command naming a missing job file, flag or `choices` value is sent back once, then dropped.
Free-text values (`--mods mlp`) are not checked. `free_cell.py` has run only on the laptop's dry path: run it for a
minute with `--n 4` before a full route.

## Running a cell or route and writing measured.json

Run it with its command from `experiments.md` (`tools/gpu.py` or `tools/vast.py`, never the laptop) in your own
worktree and study folder. Compute each readout as `cells.md` defines it from the rows. Append one row per readout
to `$W/measured.json`, a JSON list:

```
[{"readout": "r10-m03-r1", "measured": 131, "n": 200, "interval": [118, 144], "artifact": "studies/<study>/results/...", "item": "result-xxxxxx"}]
```

`item` is the board result that posts the number (it decides the distinct-item count). `standing` stops on a row
that breaks this format.

## Deep tests (--deep)

For carried mechanisms, `round.py` runs the version-8 stages (develop, stored-row tests, replication, rival and duel,
cross-predicted GPU experiments, review): `uv run studies/theory/lib/round.py studies/theory/results/engine/round-<nn>
all --cutoff <ISO time> --skip gpuprice --from <previous engine round> --deep $W` (stages in its docstring). About
60 to 80 jobs and 1.5 hours: run it only when a carried mechanism needs a stored-row test before a costly cell.

## What a round delivers and posts

1. `standing.md`: carried mechanisms as `idea` items (statement, holds_against, record with items); graveyard ones
   in one `knowledge` item with the numbers that refuted them. A wrong forecast is a result.
2. `experiments.md`: the top of lists A and C as `idea` items with commands and forecasts, before anyone runs them.
3. `$W/run.json` (commit, command, sources, counts, minutes) and one README paragraph in the same commit: carried,
   graveyard, duplicates, cells and routes proposed, dropped, cells that split, routes above best, minutes.

## What a round may claim

- A record counts only numbers measured after the forecast; say scored numbers, distinct items and total gain.
- A ranking is the forecasters' own numbers until the cell or route has run.
- Outside a round: `forecast.py make`, `score [--rescore]` and `cells` still run alone (`results/forecast/`).
