---
name: theory
description: Score the team's fixed forecasts against the results posted since, plan a direct offline test of each top mechanism's distinctive claim, find the numbers both no-theory readers got wrong, and write theories only about those. One round runs studies/theory/lib/forecast.py round - it scores every outstanding forecast, cell and route of earlier rounds (once per number, only forecasts written before the result), carries mechanisms with a positive gain on numbers from 3 or more results and buries the losers and those whose cause a direct test refuted, writes direct_tests.md (one test plan per top untested mechanism, run by subagents offline), lists the surprises in surprises.md, has the readers and carried mechanisms forecast the open work, and for each top surprise one blind job writes two rival mechanisms that must disagree on an open target or a new cell; their cells and one no-reward route per pair are checked against open work, forecast blind and ranked. Use when the user asks for a theory, what the results mean together, which result nobody expected, and after every fifth closed result. Writes studies/theory/results/wide/round-<nn>/ and updates studies/theory/README.md.
---

# Theory round (version 12, score first, direct tests)

What ten rounds showed: the engine's value is forecasts fixed before results, the score, refutations (run-08/f2-m03 at
-12.27 nats; both readers refuted on result-9ce8ed) and surprises (run-01 t14: a number nobody forecast). Mechanisms
written from the same board forecast the same numbers: in round 10, 24 of 36 new ones were duplicates and 0 of 39
designed cells split two families from two others. So a round now scores first and writes theories only where the
readers were wrong (`specs/SPEC_engine_v11.md`).

## What a round is

1. `standing`: score every outstanding forecast, cell and route of the `--from` folders against the results posted
   since (each folder once). Carried: total gain above 0 on numbers from 3 or more distinct board items. Graveyard:
   -2 nats or less on 2 or more items. The rest are dropped.
2. `direct_tests` (version 12): for each of the top 5 carried mechanisms with no row in `results/refuted.json` or
   `results/direct_tested.json`, one blind job writes `direct_tests.md`: the one claim only its cause makes, the stored
   files that decide it, the refuting observation and a threshold. Run each plan with one subagent: spec committed
   first, offline only, then a row `{mechanism, claim, result, verdict: holds|refuted, added}` in `direct_tested.json`
   (or a row in `refuted.json`). A refuted cause buries the mechanism; "holds" is marked in `standing.md`. In rounds
   09-12 three direct tests found more than the forecasting did.
3. `surprises`: every scored number outside both readers' 90 % intervals, most surprising first (z: distance from the
   nearer reader's centre in that reader's sd), marked when it lies outside every forecaster's interval
   (`surprises.md`, `surprises.json`, with the result id and every forecast).
4. `targets_open`, `forecast`: the numbers the open work items will report, forecast by the two readers and the
   carried mechanisms.
5. `propose` (only with surprises): one blind job per surprise (the 6 most surprising, at once) writes two rival
   mechanisms, each saying why the readers were wrong (`readers_wrong`), resting on 2 or more board items, holding
   against the 2 known numbers nearest to contradicting it, and forecasting a third of the open targets or more. The
   pair must have disjoint intervals on 2 or more targets or on one new cell it names (`pairs.json`). The duplicate
   judge only reports restatements (`duplicates.json`): a rival may restate an older mechanism; what counts is whether
   the two differ.
6. `cells`: the pairs' cells and one no-reward route per pair. One blind job checks each against open work and
   posted results: one an open item answers becomes a target on that item (its forecasts join `forecasts.json`,
   scored next round for free); one a posted result answers is dropped. Everyone forecasts the rest blind; a pair's
   cell is ranked only when the two rivals' own blind intervals do not overlap, else listed as "pair does not differ
   blind".
7. `experiments`: lists A (cells by separating readouts per GPU minute), C (routes by margin) and the free targets.

## The coordinator's job

Post the `work` item, run the command, commit `targets.json`, `forecasts.json`, `mechanisms.json` and `surprises.md`
the moment they exist (before any of their numbers post), then the rest. Read `standing.md`, `surprises.md`,
`pairs.json` and `experiments.md`; post the surprises as one `knowledge` item; run the top entries. Write no mechanism,
forecast, cell or route, and edit no job output. Work in your own worktree, `git pull origin main` first.

## The command

`W=studies/theory/results/wide/round-<nn>` (next free number). `--from` names the previous rounds and every forecast
run or cells folder whose forecasts are still outstanding.

```
uv run studies/theory/lib/forecast.py round $W --from <previous rounds> <forecast runs> <cells folders>
```

A stage whose output exists is skipped, so the same command resumes. A job whose output fails its check is sent back
once, then stops the round, except a cell or route whose command still fails the flag check: it is dropped and the
reason recorded. Job prompts and raw outputs stay in the temp folder named in `run.json`. Prompts:
`lib/prompts/forecast_*.md`, `surprise_propose.md`, `duplicates.md`, `cells_check.md`, `cells_forecast.md`,
`routes_propose.md`. `--surprises N` sets the number of rival pairs (default 6); `--model-all <model>` every job's
model. Smoke test: `--surprises 1 --model-all sonnet` in a folder outside the repository.

## The score

A forecast (value, low, high) is a normal density with sd = max((high - low) / 3.29, 0.01 * max(|value|, 1)). Gain
= log density of the forecast minus log density of the equal mixture of the two readers at the measured value,
clipped to [-3, 3] nats; at most 0 when the measured value lies outside the forecast's own 90 % interval. A record
is rebuilt each round from the `--from` folders alone. Three rules (11.1): a forecaster gets one score per measured
number (board item and value), on the forecast it wrote earliest; a forecast counts only if it was written before the
result was posted (written time: the earlier of the time `forecasts.md` or `cells.md` records and the first commit of
`forecasts.json` or `cell_forecasts.json`), others are listed in `standing.md` as written after the result; every row
of every `measured.json` is scored or listed with its reason. A target matches a result on its cell, not its seed,
unless the target names a seed.

Forecast gain does not confirm a cause; a direct test of the cause does (stage 2, `results/refuted.json`).

## Cells, routes and the flag check

- A cell splits when, with forecasters at -2 nats or below left out, the rest divide into a low and a high side
  (every low interval below every high interval) with 2 or more families on each side.
- A route is a change to the untrained base alone (prompt text, opening tokens, decoding, a vote or selection rule,
  restarts, examples written by the base) or to Think-SFT, with the same procedure on RL-Zero-Math. Its margin is
  (median forecast - stored count) / sd, where the stored count is the right answers on the route's own hard328
  subset of the `studies/rlneurons/results/table/hard328-02/table.json` row of its model at the nearest token count,
  and sd = sqrt(n p (1 - p)) of that count. No MATH-500 readout for models above 90 % there; no stored rows: "no
  baseline", not ranked.
- `jobs.md` gives each job file's flags and `choices`, parsed from its `add_argument` calls (`studies/rlneurons/jobs/`,
  `studies/theory/jobs/`). Routes run with `studies/theory/jobs/free_cell.py` (`--model base|rl|think_sft`,
  `--prompt-suffix`, `--opening-text`, `--temperature`, `--top-p`, `--min-p`, `--repetition-penalty`, `--max-tokens`,
  `--samples`, `--seed`, `--set`, `--n`, `--shard`) or `run_cell.py`; a vote is computed from the rows. A missing job
  file, flag or `choices` value is sent back once, then dropped; so is a command that runs git (job machines have no
  `.git`: write `--commit COMMIT_SHA` and replace it by hand); free-text values are not checked. `free_cell.py` has
  run only on the laptop's dry path: run it for a minute with `--n 4` first.

## Running a cell or route and writing measured.json

Run it from `experiments.md` (`tools/gpu.py` or `tools/vast.py`, never the laptop) in your own worktree and study
folder. Append one row per readout to `$W/measured.json`, a JSON list:

```
[{"readout": "r11-m01-r1", "measured": 131, "n": 200, "interval": [118, 144], "artifact": "studies/<study>/results/...", "item": "result-xxxxxx"}]
```

`item` is the board result that posts the number. `standing` stops on a row that breaks this format.

## Options

- `--propose-wide`: the version-10 round: six lens jobs (`LENSES`) of `--propose N` mechanisms each, the judge, a cell
  from every mechanism and a route from every family. It gave duplicates and no splits in round 10.
- `--deep`: `round.py ... --deep $W` runs the version-8 stages (develop, stored-row tests, replication, rival and
  duel, review) on the carried mechanisms; about 60 to 80 jobs and 1.5 hours (stages in its docstring).
- Outside a round: `forecast.py make`, `score [--rescore]` and `cells` still run alone (`results/forecast/`).

## What a round delivers and may claim

1. `standing.md`: carried mechanisms and the graveyard, with scored numbers, distinct results and total gain.
2. `surprises.md` as one `knowledge` item: each surprise with its number, both readers' forecasts and the result id.
3. `pairs.json` and `experiments.md`: where each rival pair differs; the top cell and route as `idea` items.
4. `$W/run.json` and one README section in the same commit as the round's files.

A record counts only numbers measured after the forecast. A surprise is relative to the readers of the folder that
forecast it. A ranking is the forecasters' own numbers until the cell or route has run.
