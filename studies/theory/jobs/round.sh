#!/bin/sh
# One theory round with the two independent opening jobs (inventory, external) at the same time.
# Usage: sh studies/theory/jobs/round.sh <round dir> <the options of round.py: --cutoff ... --skip ... --from ...>
# round.py `all` skips a stage whose output exists, so the last line runs the remaining stages in order.
set -e
R=$1; shift
uv run studies/theory/lib/round.py "$R" split standing "$@"
uv run studies/theory/lib/round.py "$R" inventory "$@" & A=$!
uv run studies/theory/lib/round.py "$R" external "$@" & B=$!
wait $A; wait $B
uv run studies/theory/lib/round.py "$R" all "$@"
