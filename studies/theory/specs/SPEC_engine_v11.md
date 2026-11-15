# Engine version 11: score first, theories only where the readers were wrong

Written before the code and before round 11 (2026-11-15, abaybektursun). Code: `lib/forecast.py`, `lib/cells.py`;
skill `.claude/skills/theory/SKILL.md` (version 11).

## Why (round 10, `results/wide/round-10/`, README "Round 10 (engine 10, two tracks)")

- 24 of 36 new mechanisms were duplicates. 0 of 39 cells split with 2 families on each side; even with one family per
  side only 3 of 69 readouts have two forecasters with disjoint intervals. Six families that read the same board
  explain differently but forecast the same numbers.
- 6 of 7 no-reward routes repeated an open work item (work-dc9359). Route margins were 0.4 to 2.7 right answers on
  subsets whose standard deviation is 3 to 4, against a baseline scaled from the full set.
- What worked in ten rounds: forecasts fixed before results, the score, refutations (run-08/f2-m03 at -12.27 nats;
  both readers refuted on result-9ce8ed), and numbers nobody forecast (run-01 t14).

## What changes

1. `forecast.py round` scores first. `standing`: every outstanding forecast, cell and route of the `--from` folders
   against results posted since, each folder once; carry and graveyard rules as in version 10. `surprises`: every
   scored number outside both readers' 90 % intervals, most surprising first (distance from the nearer reader's
   centre in that reader's sd), marked when it lies outside every forecaster's interval; `surprises.md` with the
   result id, the measured value and the forecasts. Then `targets_open`, and `forecast` by the two readers and the
   carried mechanisms only.
2. `propose` runs only when there are surprises: one blind job per surprise (the 6 most surprising, at once), given
   the board, the surprise, the mechanisms that had it inside their interval, the open targets, `facts.json`, the
   graveyard and the job flags. It writes 2 rival mechanisms that each say why the readers were wrong on that number,
   hold against the 2 known numbers nearest to contradicting them, and forecast the open targets; the pair must differ
   (disjoint intervals) on 2 or more open targets or on one new cell it names. The duplicate judge stays.
3. Cells: only the cells the rival pairs name. Before forecasting, one blind job checks every cell and route against
   the open work items, `known.json` and the posted results: one an open item already answers becomes a target on that
   item (its readouts join `targets.json` and their forecasts `forecasts.json`, scored next round); one a posted result
   answers is dropped with the result id.
4. Routes (one per rival pair): the margin is in standard deviations of the subset count measured from the stored
   per-problem rows of that subset (`studies/rlneurons/results/table/hard328-02/table.json`), against the row of the
   route's model at the nearest token count; sd = sqrt(n p (1 - p)) of that subset count. MATH-500 is dropped as a
   readout for models above 90 % there (Think-SFT, RL); a readout with no stored rows for its subset is "no baseline"
   and not ranked.
5. SKILL.md version 11, at most 126 lines; `--deep` and the version-10 proposing (`--propose-wide`) stay as options.

## Hypotheses for round 11

- X1 (new numbers): at least 15 numbers scored from results posted after round 10's forecasts (19:20 UTC), among
  them the hard328 rows of work-dc9359. Refuted at 14 or fewer, or when no work-dc9359 hard328 number is scored.
- X2 (surprises exist): at least 3 scored numbers outside both readers' intervals. Refuted at 2 or fewer.
- X3 (rivals differ): at least 2 rival pairs name an open target or a cell on which their 90 % intervals are disjoint
  (after the duplicate judge). Refuted at 1 or 0.
- X4 (speed): from `standing` to `experiments.md` under 30 minutes (`run.json` minutes). Refuted at 30 or more.

## Limits

- A surprise depends on the readers of the folder that forecast it; the same number forecast by several runs is kept
  once, at its largest distance.
- Route baselines exist only for hard328 rows in `table.json`; Think-SFT at cap 32,768 is not in it.
