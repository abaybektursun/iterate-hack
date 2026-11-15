# Engine version 10: two tracks, distinct experiments, robust separation

Written before the code and before round 10 (2026-11-15, abaybektursun). Code: `lib/forecast.py`, `lib/cells.py`,
`jobs/free_cell.py`; skill `.claude/skills/theory/SKILL.md` (version 10).

## Why (round 09, `results/wide/round-09/`, README "Round 09")

- 8 of 10 carried mechanisms are scored only on result-a1bf75 (the code dial: 5 linked numbers of one experiment).
- One forecaster, round-09/stopping-m03 (already at -4.47 nats), is one side of all 17 separating pairs of the two
  top cells (m11, m13).
- 26 of 36 new mechanisms restate older ones; 2 restate graveyard entries.
- 26 of 39 cells edit RL weights; 4 change the base alone. `DIRECTION.md` asks for the cheapest route to RL's points
  that uses no reward.
- Cell ids restart at m01 in every run (round-09 m06 is not cells-01 m06); `standing` counts rows twice when `--from`
  names overlapping folders; flag values such as `--mods mlp` are not checked.

## What changes

1. Carry rule: carried only with a total gain above 0 on numbers from 3 or more distinct board items (the result id
   that posted each measured number; a cell number counts as its `measured.json` item, or the cell's readout id when
   it has none). Graveyard: at or below -2 nats on 2 or more distinct items. The summary reports scored numbers and
   distinct items.
2. Separation: forecasters whose record is at or below -2 nats are left out; a readout separates when its forecasters
   split into a low side and a high side (every low interval below every high interval) with 2 or more families on
   each side. A cell's separation = the number of separating readouts; list A ranks by that per GPU minute.
3. Second track, "no-reward routes": each family job also proposes one route: a change to the untrained base alone
   (prompt text, opening tokens, decoding settings, selection or vote rule, restart rule, examples written by the
   base) or to Think-SFT, with the same procedure on RL-Zero-Math for comparison. It states tokens per problem,
   forecasts right answers on a stated subset of hard328 and on MATH-500 (and the RL arm on both), and says why it
   should work in terms of the gap's known parts (`gap.md`: result-f39ba8 and the "Gap anatomy" section of
   `studies/rlneurons/README.md`). Every forecaster forecasts every route. Ranked by the median forecast minus the
   best known count of the same model at equal or fewer tokens per problem, from a table built in code from the
   board's `score:` lines (base rows, and Think-SFT rows; rows that name an RL model or delta left out; set, count, n,
   tokens, item; scaled to the subset size).
4. Job for routes: no existing job takes free prompt text, opening text and a repetition penalty (`run_cell.py`:
   prompt `plain`/`cue`, shots, min-p, restarts; `prefix_cell.py`: stored prefixes; `selfopen_gen.py`: fixed
   procedure). New `studies/theory/jobs/free_cell.py` imports run_cell's sets, rln4_gen's engine and row record and
   rln4_lib's grader v3 (no copy, no rlneurons edits). Flags: `--model base|rl|think_sft`, `--prompt-suffix`,
   `--opening-text`, `--temperature`, `--top-p`, `--min-p`, `--repetition-penalty`, `--max-tokens`, `--samples`,
   `--seed`, `--set`, `--n`, `--shard`, `--out`, `--dry-run`, `--commit`. A vote or selection rule is computed from its
   rows. Tested only by argument parsing and the dry path (canned answers, no model); it has not run on a GPU.
5. Housekeeping: one blind judge job lists new mechanisms that restate an earlier mechanism or a graveyard entry
   (pairs with a one-line reason); the newer one is dropped before forecasting and listed in `duplicates.json`. Cell ids
   carry the round (`r10-m05`, routes `r10-n01`). `standing` reads each folder once. The flag check rejects values
   outside a flag's `choices` (already in version 9) and now also checks `free_cell.py`.
6. SKILL.md: version 10, two tracks, at most its present 128 lines.

## Hypotheses for round 10

- W1 (routes beat the best known base): at least 4 route cells have a median forecast above the best known count
  at equal tokens on at least one of their two readouts. Refuted at 3 or fewer.
- W2 (the judge does not empty the round): at most 10 of 36 new mechanisms are dropped as duplicates. Refuted at 11
  or more.
- W3 (robust separation): at least 5 cells have a separating readout with 2 or more families on each side, after
  forecasters at or below -2 nats are left out. Refuted at 4 or fewer.
- W4 (speed): the round, from `standing` to `experiments.md`, takes under 45 minutes (`run.json` minutes). Refuted at
  45 or more.

## Limits

- The best known table is only as good as the `score:` lines: a row's tokens are the poster's mean per problem, and
  a hard328 subset count is the full-set count scaled by size, not a measured subset count.
- A route's tokens per problem are the proposer's estimate until it runs.
- `free_cell.py` has run only on the laptop's dry path.
