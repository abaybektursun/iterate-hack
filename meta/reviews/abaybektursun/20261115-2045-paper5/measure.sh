#!/bin/bash
# bash meta/reviews/abaybektursun/20261115-2045-paper5/measure.sh  (run with a tracked file modified, so no job can be submitted)
# Submits the exact command of failed job abaybektursun-1115-140534-0f14 (single-quoted, so $(git rev-parse HEAD) reaches
# the container, which has no git) and prints which check refuses it. The resubmitted, expanded command must still pass
# the command check (it then stops only at the dirty-tree check).
cd "$(git rev-parse --show-toplevel)"
BAD='bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.delta_sum --host think_sft --donor rl_math --alpha 2.0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label sft1_rl20 --prompt cue --set hard328 --temperature 1.0 --top-p 1.0 --max-tokens 32768 --seed 3010000 --shard 0/4 --commit $(git rev-parse HEAD)'
GOOD="${BAD%\$(git rev-parse HEAD)}ca5adf4fab31c89c5577b89aa47d92fe81af5453"
test -n "$(git status --porcelain --untracked-files=no)" || { echo "tree is clean: refusing to run (it would submit)"; exit 1; }
for name in BAD GOOD; do
  echo "== $name"; uv run --quiet tools/gpu.py submit h100 -- "${!name}" 2>&1 | grep -E "AssertionError|^[a-z]+-1115" ; echo "exit ${PIPESTATUS[0]}"
done
