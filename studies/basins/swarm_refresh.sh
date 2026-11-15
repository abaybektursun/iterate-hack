#!/bin/bash
# The swarm map end to end, from the repository root, every Python step in run.sh's environment. Paid judge steps
# (gpt-6.1-sol) run only when their output is missing, so after a failure the same command resumes where it stopped:
#   bash studies/basins/swarm_refresh.sh <HHMM, UTC of the snapshot> <results folder> [judge folder with directions.json]
#   bash studies/basins/swarm_refresh.sh 0408 studies/basins/results/swarm/main-03 runs/swarm/judge-2136
# DRY=1 prints the steps that would run instead of running them.
set -euo pipefail
T=$1; OUT=$2; DIRS=${3:-runs/swarm/judge-2136}; M=gpt-6.1-sol
S=runs/swarm/board-$T.json; J=runs/swarm/judge-$T
py() { bash studies/basins/run.sh "$@"; }
step() { echo "== $*"; [ -n "${DRY:-}" ] || "$@"; }
lines() { [ -f "$1" ] && wc -l < "$1" | tr -d ' ' || echo 0; }

[ -f "$S" ] || step uv run studies/basins/prep/swarm_export.py "$S"
[ -f "$J/coverage.jsonl" ] || step py studies.basins.analysis.swarm_judge "$S" "$J" --model $M --reuse-directions "$DIRS" --steps coverage
if [ "$(lines "$J/partitions.jsonl")" -lt 2 ] || [ ! -f "$J/triplets.jsonl" ]; then
  step py studies.basins.analysis.swarm_judge "$S" "$J" --model $M --reuse "$J" --steps partitions,triplets --repair-ids
fi
[ -f "$J/scores.json" ] || step py studies.basins.analysis.swarm_scores "$J" --model $M
[ -f "$J/lineage.json" ] || step py studies.basins.analysis.swarm_lineage "$J" --model $M --snapshot "$S"
step py studies.basins.analysis.swarm_analyze "$J" "$OUT"
step py studies.basins.analysis.swarm_page "$OUT" $M
