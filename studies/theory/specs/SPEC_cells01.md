# Cells 01: the theories design the GPU cells that tell them apart

Written before the run (2026-11-15, abaybektursun). Code: `lib/forecast.py cells <folder> --from <forecast run
folders...>`, prompts `lib/prompts/cells_propose.md`, `cells_merge.md`, `cells_forecast.md`. Output
`results/forecast/cells-01/`.

## Why

In forecast runs 03-08 the 36 mechanisms forecast the team's open GPU numbers, and no open target has two families
(lenses) whose 90 % intervals do not overlap: the open cells were made to answer other questions, not to tell these
mechanisms apart. Forcing disagreement on the same cells (run-02) gave mostly wrong forecasts. So the mechanisms
should choose the cells.

## What runs

```
uv run studies/theory/lib/forecast.py cells studies/theory/results/forecast/cells-01 --from studies/theory/results/forecast/run-0{3,4,5,6,7,8}
```

Families: one per `--from` run (its 6 mechanisms, family name = run folder name) and one for round 07's theories that
are not refuted in `metrics_v4.json` (8 theories; round 08 is skipped). Every job is round.py's blind job (`claude -p`
in an empty directory, Read and Write only).

1. Propose: one job per family, 7 at once. Inputs: `DIRECTION.md`; the board (every result and knowledge item);
   the family's mechanisms (statement, rests_on; theory files for round 07); every mechanism of every family (id,
   family, statement) as the possible alternatives; `known.json`: the targets of the `--from` runs (open or since
   measured) and round 07's `facts.json`; `jobs.md`: the rows of `studies/rlneurons/README.md` that describe a job
   file, its "How to run" section, and the `add_argument` lines of each `studies/rlneurons/jobs/*.py` (flags only, no
   code). For each of its mechanisms the job writes one new cell the mechanism gets right and a named other mechanism
   gets wrong: model or edit, prompt, set, n, sampling, samples, grader, cap; the job file and the command as far as
   it can give it; a readout computable from the rows; its value with a 90 % interval; the alternative's value
   (outside that interval); GPU minutes on one L40S 48 GB (100 minutes for 500 MATH-500 problems at cap 16,384; 100
   to 200 problems preferred; at most 120); `base_only` when the cell changes only the untrained base (no RL weights
   or directions from them), with the best known base-only count for the same problems and samples (board item id).
   Code checks: one cell per mechanism, alternative is another listed mechanism, numbers ordered, alternative's value
   outside the interval, minutes in (0, 120], job file exists, `base_only` cells have a best count with a board id.
2. Merge: one job groups cells that are the same run apart from the readout (same model or edit, prompt, set,
   sampling). Code checks that every proposed cell is in exactly one merged cell; the proposers' predictions are
   attached by code from the proposals, not copied by the job.
3. Forecast: one fresh job per family (a forecast per mechanism per readout, "theory says nothing" allowed) and two
   readers with no theory (every readout), all blind: they see the merged cells without the proposers' values,
   intervals, alternatives and reasons. `base_only` cells show the best known base count.
4. Rank in code. A forecaster is one mechanism or one reader; each reader is its own family. Separation of a cell =
   the number of pairs of forecasters from different families whose intervals do not overlap, summed over the cell's
   readouts; list A sorts by separation per GPU minute. List B (`base_only` cells) sorts by the highest forecast of
   right answers minus the best known base count.

Writes `cells.json` (proposals and merged cells), `cell_forecasts.json`, `cells.md` (top 10 of each list: the cell,
the command, every forecaster's number, the pairs that do not overlap), `run.json`.

## Hypotheses

- C1 (mechanisms can design cells): at least 20 cells proposed and at least 10 after merging. Refuted at 19 or fewer
  proposed (a stopped family job counts 0) or 9 or fewer merged.
- C2 (designed cells separate where open cells did not): at least 5 merged cells have 3 or more pairs of forecasters
  from different families with intervals that do not overlap. Refuted at 4 or fewer.
- C3 (some designed change to the base beats the best known base): at least 1 `base_only` cell has a forecast (any
  forecaster) above the best known base count at the same number of samples. Refuted when none does.

## Limits

- Forecasters share one board, so their errors are correlated; separation between forecasts is not evidence for
  either side until the cell runs.
- GPU minutes are the proposers' guesses; the ratio in list A inherits their error.
- A family job forecasts cells its own family proposed, blind to the numbers but not to the fact that its family
  wanted the cell; its forecasts may lean toward the proposer's side.
- The merge job may group cells too loosely or too tightly; every proposal and its prediction is kept in `cells.json`.
- Whether the board already answers a cell is checked by hand for the top 5 (`tools/recall.py`, `board.py ls result`)
  and flagged in `cells.md`; no cell is dropped.
- No cell runs in this work; C2 and C3 concern forecasts, not measurements.
