#!/usr/bin/env bash
# One gapmap cell inside a runner job.
#   bash studies/gapmap/jobs/run_cell.sh <batch> <cell> [--data <per_problem.json>]
set -euo pipefail
batch=$1
cell=$2
shift 2
echo "[run_cell] $(date -u +%T) start: batch $batch, cell $cell"

# The pinned environment of the bootstrap, built new for every job so that no cell inherits another job's packages.
venv=$(mktemp -d)/venv
python -m venv "$venv"
"$venv/bin/pip" install --quiet --no-cache-dir --disable-pip-version-check numpy==2.5.4 scipy==1.18.1 pandas==3.1.1 matplotlib==3.11.2
echo "[run_cell] $(date -u +%T) environment ready"

"$venv/bin/python" studies/gapmap/jobs/cell.py --cells "studies/gapmap/cells/$batch.json" --cell "$cell" "$@"
echo "[run_cell] $(date -u +%T) done"
