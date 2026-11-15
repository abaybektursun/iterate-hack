#!/bin/bash
# Installs the study's engine at job start into its own venv, /opt/rln-vllm, so the runner's system packages
# (requirements.txt) stay unchanged for later jobs in a reused container. Versions as in the study's Modal app
# (jobs/modal_rln4_k.py): vLLM 0.32.0 and math-verify 0.9.0, then transformers 5.19.0 / tokenizers 0.23.3 over vLLM's
# choice; gcc, which Triton needs to compile a C stub at engine start. Run the job with /opt/rln-vllm/bin/python.
# run_cell.py checks the four versions before it loads a model.
set -euo pipefail
t0=$(date +%s)
command -v gcc > /dev/null || (apt-get update -qq && apt-get install -y -qq gcc > /dev/null)
PIP_BREAK_SYSTEM_PACKAGES=1 pip install -q uv==0.13.8     # vast.ai's image marks the system Python as externally managed
uv venv -q --allow-existing --python "$(command -v python3)" /opt/rln-vllm
uv pip install -q --python /opt/rln-vllm/bin/python vllm==0.32.0 math-verify==0.9.0
uv pip install -q --python /opt/rln-vllm/bin/python transformers==5.19.0 tokenizers==0.23.3
echo "setup_vllm.sh: $(( $(date +%s) - t0 )) s"
