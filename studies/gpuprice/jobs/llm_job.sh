#!/bin/bash
# The LLM arm's GPU job: the rlneurons vLLM venv, then llm_run.py with the arguments given.
#   uv run tools/gpu.py submit h100 --hours 0.75 -- 'bash studies/gpuprice/jobs/llm_job.sh --model w4a16 --context ... --variants sample'
# The 4-bit MoE kernel compiles with NVRTC at load and needs libnvrtc-builtins on the loader path (job e574 failed without it).
set -euo pipefail
bash studies/rlneurons/jobs/setup_vllm.sh
lib=$(find /opt/rln-vllm -name 'libnvrtc-builtins.so.13.0' | head -1)
[ -n "$lib" ] || { echo "libnvrtc-builtins.so.13.0 is not in the venv"; exit 1; }
export LD_LIBRARY_PATH="$(dirname "$lib"):${LD_LIBRARY_PATH:-}"
export VLLM_USE_FLASHINFER_SAMPLER=0
/opt/rln-vllm/bin/python studies/gpuprice/jobs/llm_run.py "$@"
