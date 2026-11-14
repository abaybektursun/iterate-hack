#!/bin/bash
# Installs the study's engine into the team runner's container at job start: the versions of the study's Modal app
# (jobs/modal_rln4_k.py): vLLM 0.32.0 and math-verify 0.9.0, then transformers 5.19.0 / tokenizers 0.23.3 over vLLM's
# choice, and gcc, which Triton needs to compile a C stub at engine start. uv installs into the system Python.
# run_cell.py checks the four versions before it loads a model.
set -euo pipefail
t0=$(date +%s)
apt-get update -qq && apt-get install -y -qq gcc > /dev/null
pip install -q uv==0.13.8
uv pip install --system -q vllm==0.32.0 math-verify==0.9.0
uv pip install --system -q transformers==5.19.0 tokenizers==0.23.3
echo "setup_vllm.sh: $(( $(date +%s) - t0 )) s"
