---
name: theory
description: Score the team's fixed forecasts, collect the direct facts (offline tests of mechanisms' causes), find the numbers both no-theory readers got wrong, write rival pairs only about those, each pair with one shared direct test on stored data (one statistic, disjoint ranges for the two rivals), and let only mechanisms that hold a direct test (90 % interval inside the range, n of 50 or more) forecast, and only holders that forecast something the readers do not design cells. One round runs studies/theory/lib/forecast.py round twice: the first run scores (once per number, only forecasts written before the result), writes direct_facts.json, surprises.md, direct_tests.md (plans for the top untested carried mechanisms and one per rival pair) and stops; subagents run the tests offline and add rows to results/refuted.json or direct_tested.json; the second run has the holders and two readers forecast the open work, lists holders that forecast nothing new, and turns the others' pairs into blind-forecast cells. Use when the user asks for a theory, what the results mean together, which result nobody expected, and after every fifth closed result. Writes studies/theory/results/wide/round-<nn>/ and updates studies/theory/README.md.
---

# Theory round (version 14: one shared test per rival pair)

Why this order: in rounds 9 to 12 forecast gain ranked mechanisms whose causes then failed a direct test (5 of the top 6
failed their own claim, 1 held only against a weak null; README "Direct tests"). So a mechanism now earns the right to
forecast by holding a direct test of its cause; forecasts, scores, refutations and surprises stay the record.

Version 14 rules (round 13: pairs tested on different numbers both held; holds on n 21 to 42; no holder forecast new):
1. A rival pair gets one shared test: one statistic on one set of stored rows, disjoint ranges for a and b and the
   null's range, fixed in advance (checked in code: sent back once, then the pair is dropped). A value in neither
   rival's range refutes both; one row per rival.
2. A verdict of holds needs the 90 % interval wholly inside the rival's range (carried plan: past the threshold) and n
   of at least 50 rows; otherwise the row is `undecided`, with the n needed.
3. A holder with no forecast apart from both readers' 90 % intervals is listed in the round's README as "holds its
   test, forecasts nothing new" (`holders.json`) and designs no cell; only the others design their pair's cell.

## What a round is

1. `standing`: score every outstanding forecast, cell and route of the `--from` folders against the results posted
   since (each folder once). Carried: total gain above 0 on numbers from 3 or more distinct board items, never a
   mechanism in `graveyard.json` or `refuted.json`. Graveyard: -2 nats or less on 2 or more items.
2. Direct facts (`direct_facts.json`): every row of `results/refuted.json` and `results/direct_tested.json` (claim,
   verdict, deciding number, result id). Proposers and planners get them first; every new mechanism must agree with all.
3. `surprises`: every scored number outside both readers' 90 % intervals, most surprising first (`surprises.md`).
4. Proposals with one shared test per pair: one blind job per top-6 surprise writes two rival mechanisms (why the
   readers were wrong, forecasts of the open targets, and the pair's differences on targets or one new cell) and the
   pair's test (rule 1) with a null stronger than random where one exists (the base matrix's own top directions,
   another model's directions). The top 5 untested carried mechanisms (none with a forecast a `measured.json` row missed)
   get a plan too; a planner names the posted result instead when one already decides the claim. All in `direct_tests.md`.
5. Run the direct tests: one subagent per plan, spec committed first, offline only, then a row
   `{mechanism, claim, result, verdict: holds|refuted|undecided, measured, added}` per mechanism in `direct_tested.json`
   (refuted ones also in `refuted.json`; rule 2). The round command stops here until every mechanism has a row; `--go`
   continues with who holds now.
6. Rerun the same command: only mechanisms that hold a direct test forecast the open targets (beside the two readers);
   rule 3 picks the holders that design: each gets its pair's cell and one no-reward route, checked against open work
   (an open item's answer becomes a free target) and forecast blind; then `experiments.md`.

## The coordinator's job

Post the `work` item, run the command, commit `targets.json`, `surprises.md` and `direct_tests.md` at once, run the
direct tests, rerun, and commit `forecasts.json` and `mechanisms.json` the moment they exist (before any of their
numbers post), then the rest. Read `standing.md`, `surprises.md`,
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
