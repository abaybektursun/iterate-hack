#!/usr/bin/env bash
# One gapmap cell inside a runner job. The runner image holds numpy (requirements.txt), so there is no setup.
#   bash studies/gapmap/jobs/run_cell.sh <batch> <cell> [--data <per_problem.json>]
set -euo pipefail
batch=$1
cell=$2
shift 2
echo "[run_cell] $(date -u +%T) start: batch $batch, cell $cell"
python studies/gapmap/jobs/cell.py --cells "studies/gapmap/cells/$batch.json" --cell "$cell" "$@"
echo "[run_cell] $(date -u +%T) done"
