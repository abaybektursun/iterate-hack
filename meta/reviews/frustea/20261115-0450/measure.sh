#!/bin/bash
# bash meta/reviews/frustea/20261115-0450/measure.sh  (from the repository root, worktree ali/basins)
# Hand-typed invocations and failed exits of the main-03 refresh, read from runs/swarm/judge-0408.log, and the
# stage times from file modification times (UTC). Then the sha256 of the committed main-03 summary.json.
L=runs/swarm/judge-0408.log
echo "invocations after the first (lines starting ---): $(grep -c '^---' $L)"
echo "exit lines: $(grep -c '^exit ' $L), of them nonzero: $(grep -c '^exit [1-9]' $L)"
grep -E '^(---|exit )|AssertionError|ModuleNotFoundError|usage:' $L | cut -c1-150
TZ=UTC stat -f '%Sm %N' -t '%H:%M:%S' runs/swarm/board-0408.json runs/swarm/judge-0408/coverage.jsonl runs/swarm/judge-0408/calls/partition-0.fail1.out runs/swarm/judge-0408/calls/partition-0.fail2.out runs/swarm/judge-0408/partitions.jsonl runs/swarm/judge-0408/triplets.jsonl runs/swarm/judge-0408/scores.json runs/swarm/judge-0408/lineage.json studies/basins/results/swarm/main-03/summary.json
shasum -a 256 studies/basins/results/swarm/main-03/summary.json
