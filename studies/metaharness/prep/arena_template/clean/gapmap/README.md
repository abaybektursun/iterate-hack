# gapmap: where the RL model still differs from the cued base on MATH-500

`DIRECTION.md` point 2: about 11 points remain between the base with the opening cue (T1) and the RL model (T2) at
T 1.0. This study maps where that difference sits, from the 500 per-problem rows already stored
(`studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json`, grader v3). No model runs: every cell is a paired
bootstrap over problems, run as a job on the CPU class of the team runner (never on a laptop: `specs/SPEC.md`,
Requirements). Plan: `specs/SPEC.md`.

## Files

| Path | What it is |
|---|---|
| `specs/SPEC.md` | The question, the four metrics, the splits, the prediction and what refutes it, the owner's requirements. |
| `queue.json` | What the study runs: the batches (one metric each), the splits of every batch, extra cells, default settings. |
| `prep/make_cells.py` | Writes `cells/<batch>.json` from `queue.json`. |
| `cells/<batch>.json` | The cells of one batch, one entry per cell with its settings. |
| `jobs/submit.sh` | Launches one cell on the runner, waits, copies the output to `runs/<job id>/`. |
| `jobs/run_cell.sh` | What the job runs: `cell.py` in the runner image. |
| `jobs/cell.py` | The cell: metric, split, paired bootstrap, interval, table. |
| `results/overall-01/` | The overall difference of all four metrics with 95% intervals (`metrics.json`, `run.json`). |
| `results/<batch>-NN/` | One batch: one file per cell and `run.json` with the job ids. |

## How to run

One batch at a time, from the repository root:

```
python3 studies/gapmap/prep/make_cells.py <batch>
bash studies/gapmap/jobs/submit.sh <batch> <cell>
```

Commit `cells/<batch>.json` and push before the first launch (a job runs a pushed commit). Then copy each cell's
`runs/<job id>/metrics.json` to `results/<batch>-NN/<cell>.json`, write `run.json`, commit, and close the work item
with the numbers.

## Numbers

- Overall, T2 minus T1, 500 problems, 95% interval, 1,500,000 resamples, seed 0 (`results/overall-01/metrics.json`):
OVERALL_LINES
- Batches: see `results/<batch>-NN/`.
