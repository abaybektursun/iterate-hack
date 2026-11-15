#!/usr/bin/env bash
# Launch one gapmap cell on the team runner (CPU class), wait for it and copy its output to runs/<job id>/.
#   bash studies/gapmap/jobs/submit.sh <batch> <cell> [--data <per_problem.json>]
# Exits 1 when the job fails, after printing the end of its log.
set -euo pipefail
batch=$1
cell=$2
shift 2
command="bash studies/gapmap/jobs/run_cell.sh $batch $cell $*"

launch() {
  local job state
  job=$(uv run --quiet tools/gpu.py submit cpu --hours 0.5 -- "$command" | head -1)
  echo "$1 job $job" >&2
  state=$(uv run --quiet tools/gpu.py wait "$job")
  if [ "$(echo "$state" | head -1)" != "done" ]; then
    echo "$state" >&2
    echo "$1 job $job failed" >&2
    return 1
  fi
  uv run --quiet tools/gpu.py get "$job" >/dev/null 2>&1
  echo "$job"
}

first=$(launch cell)

# Verification rerun: the same cell with the same seed, to confirm the number before it is posted.
second=$(launch check)
python3 - "$first" "$second" <<'PY'
import json, sys
tables = [json.load(open(f"runs/{job}/metrics.json"))["table"] for job in sys.argv[1:3]]
if "t2_minus_t1" in tables[0][0]:  # a bootstrap table repeats exactly; the timings of bench-rng do not
    assert tables[0] == tables[1], "the verification rerun gave a different table"
print(f"check ok: {sys.argv[2]} repeats {sys.argv[1]}")
PY
echo "result runs/$first/metrics.json"
