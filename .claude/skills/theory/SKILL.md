---
name: theory
description: Score the team's fixed forecasts, collect the direct facts (offline tests of mechanisms' causes), put every direct fact into three single accounts written in parallel, which measure their consequences on the explore half of the stored rows and are tested on the test half against an adversary's alternative (forecast.py synthesis), find the numbers both no-theory readers got wrong, write rival pairs only about those, each pair with one shared direct test on stored data (one statistic, disjoint ranges for the two rivals), and let only mechanisms that hold a direct test (90 % interval inside the range, n of 50 or more) forecast, and only holders that forecast something the readers do not design cells. One round runs studies/theory/lib/forecast.py round twice: the first run scores (once per number, only forecasts written before the result), writes direct_facts.json, surprises.md, direct_tests.md (plans for the top untested carried mechanisms and one per rival pair) and stops; subagents run the tests offline and add rows to results/refuted.json or direct_tested.json; the second run has the holders and two readers forecast the open work, lists holders that forecast nothing new, and turns the others' pairs into blind-forecast cells. Use when the user asks for a theory, what the results mean together, which result nobody expected, and after every fifth closed result. Writes studies/theory/results/wide/round-<nn>/ and updates studies/theory/README.md.
---

# Theory round (version 20: accounts, adversaries and readers forecast held-out stored cells, scored at once)

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

Version 16 rules (round 15: 6 of 9 consequences held, but an audit, knowledge-ab9881, found 3 of 4 designs faulty):
1. Accounts are written in sequence; account k sees the earlier ones and denies at least 2 of their consequences with
   its own range on the same test (disjoint); denied consequences are tested first. Run with `PYTHONUNBUFFERED=1`.
2. One blind adversary per consequence (sees only statistic, files, rows, computation, range) writes the strongest
   alternative reaching that range without the account (covariate, regression to the mean, construction artifact);
   the test computes its value first. `holds` needs the 90 % interval inside the range AND excluding that value, else
   `not separated` (`add-rows` recomputes every verdict). One measurement, one credit: two consequences of one account
   on the same files, or a number a board result already shows, are rejected. Fact marks come from one blind marker per
   account (`marks-<account>.json`), not the account's own; the score uses them.

Version 17 rules (round 16: 0 of 9 held, 6 of 9 adversary values missed the measured interval: writers could not read
the rows, and reading all rows would let them fit the answer): 1. `data/split_v1.json` splits every set's problem ids
once (sha256 of `<set>:<id>`) into explore and test halves; `lib/rows.py` loads one half of a stored cell. 2. Three
accounts (parallel, each from a different third of the facts) and the adversaries run with Bash in a folder holding
the explore half only (a tool call naming an outside path stops the round); each consequence states its explore value
and interval, and its test range contains that value, at most 2.5 explore interval widths wide. 3. A consequence whose
adversary's explore value lies inside that interval is dropped untested. 4. Tests load only the test half
(`rows.load(set, cell, "test")`); verdict16 decides. No sequence, no denials.

Version 18 rules (round 17: 7 of 9 sampling-row consequences matched a plain covariate; 13 to 17 ran ~60 such tests;
what separated accounts were weight computations and edits): 1. A consequence is dropped untested when the adversary's
explore value lies inside the account's range, not only inside its explore interval. 2. `data/split_matrices_v1.json`
splits the 224 weight matrices once (sha256 of the name) into 112 explore and 112 test; `rows.weights(table, half)`
loads the per-matrix tables (`rows.WEIGHTS`: anatomy, top8_share, cap, xlisten); writers see explore matrices only.
3. Each account gives at least 2 `weights` consequences (n >= 25 test matrices, bootstrap over matrices) and at most 2 on
sampling rows, and one weights-only computation in no table (`weights_cell`, replacing the GPU cell); a blind adversary
predicts it too, and `weights_cells.md` ranks them by the gap in interval widths. The engine runs none.

Version 19 rules (rounds 17-18: 18 of 18 consequences dropped or not separated; once account and adversary both see a
statistic on the explore half, the adversary fits it, so only an unseen condition separates them): 1. `synthesis` adds
`open_forecasts`: targets_open (beside the accounts) lists open work that will post a number; each account, one
covariate-only adversary per account (blind to it; stored rows and covariates only, never an RL sample or RL-derived
edit as predictor) and both readers forecast each target; a judge per pair rejects adversary forecasts that are the
account's claim by construction. 2. `open_forecasts.md` ranks targets by gap in interval widths (deciding: no overlap).
Commit `forecasts.json` at once. 3. The next round's standing scores them; its `synthesis.md` ranks accounts by gain
over their adversary (nats). 4. Explore-half consequence tests only with `--with-row-tests`.

Version 20 rules (round 19: 1 of 4 open targets deciding, results post hours later): 1. The adversary may use stored
outcomes of RL models and RL-derived edits as data (counts, edit norms, shares, ranks), never a mechanism claim; the
judge rejects only that. 2. `data/split_cells_v1.json` (`rows.py split-cells`) splits the stored run_cell folders of
studies/rlneurons/results (xreward edits, sampling and vote cells; one group per shared job) by a hash of the folder
name; writers get explore cells' counts and rows only, and facts, board items and README lines that name a test cell or
state its count are removed (`leaks()`); run.json's `leak_check` scans the account transcripts. 3. Stage `heldout`:
accounts, adversaries and readers forecast the test cells from their descriptions; scored at once (`heldout.md`). 4.
Accounts rank by gain over their adversary AND the readers; "adds something" needs both positive.

## What a round is

1. `standing`: score every outstanding forecast, cell and route of the `--from` folders against the results posted
   since (each folder once). Carried: total gain above 0 on numbers from 3 or more distinct board items, never a
   mechanism in `graveyard.json` or `refuted.json`. Graveyard: -2 nats or less on 2 or more items.
2. Direct facts (`direct_facts.json`): every row of `results/refuted.json` and `results/direct_tested.json` (claim,
   verdict, deciding number, result id). Proposers and planners get them first; every new mechanism must agree with all.
3. Synthesis (version 17, `forecast.py synthesis $W [--from ...]`, `prompts/synthesis*.md`; rules above): three jobs, each with
   the facts in its own order and the last 24 hours of board titles, write one account (at most 6 sentences) of the RL
   change and of the base's share of RL's gain, mark every fact explained, not addressed or contradicts, name their 3
   worst, and give three new consequences (one statistic on stored files, n >= 50, a range apart from the null's) and
   one GPU cell (cell checker). Failing a check after one send-back drops the account. Markers and adversaries run;
   subagents run every test of `synthesis_tests.md` offline, `add-rows` records them, and the rerun's `synthesis.md`
   ranks the accounts by consequences and denials held minus the marker's contradictions.
4. `surprises`: every scored number outside both readers' 90 % intervals, most surprising first (`surprises.md`).
5. Proposals with one shared test per pair: one blind job per top-6 surprise writes two rival mechanisms (why the
   readers were wrong, forecasts of the open targets, and the pair's differences on targets or one new cell) and the
   pair's test (rule 1) with a null stronger than random where one exists (the base matrix's own top directions,
   another model's directions). The top 5 untested carried mechanisms (none with a forecast a `measured.json` row missed)
   get a plan too; a planner names the posted result instead when one already decides the claim. All in `direct_tests.md`.
6. Run the direct tests: one subagent per plan, spec committed first, offline only, then a row
   `{mechanism, claim, result, verdict: holds|refuted|undecided, measured, added}` per mechanism in `direct_tested.json`
   (refuted ones also in `refuted.json`; rule 2). The round command stops here until every mechanism has a row; `--go`
   continues with who holds now.
7. Rerun the same command: only mechanisms that hold a direct test forecast the open targets (beside the two readers);
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
