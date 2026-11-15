# Engine version 9: the wide round is the default

Written before the code and before round 09 (2026-11-15, abaybektursun). Code: `lib/forecast.py`, `lib/cells.py`,
`lib/round.py`; skill `.claude/skills/theory/SKILL.md` (version 9).

## Why

- Round 08 (`results/engine/round-08/`, 106 minutes, 58 jobs): 0 of 37 theory forecasts outside both readers'
  intervals, 8 of 12 mechanisms abandoned, 1 duel with 2 separating tests. The develop, stored-row test and duel
  stages have given no theory the team can use for five rounds.
- Forecast runs 03 to 08 (six families of 6 mechanisms, about 12 minutes in parallel), scored on 5 new numbers: 3
  mechanisms 5 of 5 inside with +4.4 to +5.6 nats, one 0 of 5 at -12.27. Wide, cheap search plus new numbers
  separates mechanisms.
- The score paid for misses: round 08's r8-m12 p1 measured 3.24, outside its own interval [0.5, 1.3], and gained
  +3.00 nats because the readers were further away; run-07/f2-m02 has +5.21 nats with 2 of 5 inside.
- `results/forecast/cells-01/`: of 41 designed cells, 4 separate any two families; 3 of the top 4 commands named
  flags that do not exist.

## What changes

1. Score. Wherever a log gain is computed against a measured value (round.py `gain_rows`: tests, held-out claims,
   forecasts; `score_duel`; `gpu_tests`; forecast and cell scores), a prediction whose measured value lies outside
   its own 90 % interval gains at most 0: `min(gain, 0)`. Losses are unchanged. In a duel or GPU test the gain of one
   side is minus the other's, so a side that misses gets at most 0 and the other side's loss is capped the same way.
   Forecast runs 01 to 08 are re-scored with this rule on their stored measured values (`forecast.py score <run>
   --rescore`, no model job), into new `scores-<UTC time>.*` files.
2. The default round is `forecast.py round <folder> --from <previous folders...>` (the smaller of the two options:
   it reuses `open_targets`, `run_forecasters`, `score_forecasts` and `cells` of `forecast.py`; round.py stays as the
   `--deep` tool). Stages, each skipped when its output exists:
   - `standing`: scores every `--from` folder's `forecasts.json` against the items posted after its snapshot, and its
     cells against its `measured.json`; a mechanism's record is its rows from those scores plus its record in the
     previous round's `standing.json`. Carried: total gain above 0 on 3 or more scored numbers. Graveyard: at or
     below -2 nats on 3 or more. The rest are not carried.
   - `targets_open`: the numbers the open work items will report (one job).
   - `forecast`: two readers and each carried mechanism forecast every open target, blind.
   - `propose`: six family jobs at once (the six lenses of `SPEC_forecast03.md`), 6 mechanisms each, with the
     readers' forecasts, the board, `facts.json` and the graveyard; each mechanism names in `holds_against` the two
     known numbers nearest to contradicting it and why it holds.
   - `cells`: each mechanism designs one cell, everyone forecasts every cell, ranked (as cells-01).
   - `experiments`: `cells.md` lists A and B are the ranked list to run.
   `--deep`: round.py's develop, tests, duels and review, only for carried mechanisms with a positive forecast gain
   (`round.py ... --mechanisms-from <wide round>` writes them as round.py's `mechanisms.json`).
3. Cells: `jobs.md` gives each job file's flag list, extracted in code from its `add_argument` lines (a job with no
   flags of its own takes the flags of the job modules it imports, as `run_fresh.py` runs `run_cell.py`). A
   proposed or merged cell whose command names a job file or flag that does not exist is sent back once; if it still
   does, the cell is dropped and the reason recorded in `cells.json` (`dropped`).
4. The forecast proposer gets `facts.json` (it did) and must fill `holds_against` with 2 entries, each a board item id
   or a facts.json index, the number and why the mechanism holds; checked in code.
5. SKILL.md is rewritten around the wide round and is shorter than version 8.

## Hypotheses for round 09 (the first version-9 round)

- V1 (the wide round is fast): from the first stage to `cells.md` written, under 40 minutes wall time (from
  `run.json` and file times). Refuted at 40 minutes or more, a stop that needs a person included.
- V2 (designed cells separate families): at least 8 merged cells have at least one pair of forecasters from
  different families (readers count as their own families) whose 90 % intervals do not overlap. Refuted at 7 or fewer.
- V3 (commands run): every command of the top 10 cells of list A passes the flag check (job files and flags exist).
  Refuted when any of the ten names a job file or flag that does not exist (checked again by hand on the ten).

## Limits

- The flag check does not check flag values (`--model s0100` with `--model` choices `rl`, `base`, ... passes).
- The re-score uses the measured values stored in the newest score file of each run; results posted after that file
  are not added.
