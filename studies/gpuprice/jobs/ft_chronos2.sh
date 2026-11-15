#!/usr/bin/env bash
# GPU job: bash studies/gpuprice/jobs/ft_chronos2.sh <arguments of ft_chronos2.py>
#   uv run tools/gpu.py submit h100 --hours 0.3 -- 'bash studies/gpuprice/jobs/ft_chronos2.sh --mode lora --steps 1000'
set -euo pipefail
pip install -q "chronos-forecasting[extras]>=2.3" pyarrow
pip list 2>/dev/null | grep -i -E "^(chronos|torch|transformers|peft) "
python studies/gpuprice/jobs/ft_chronos2.py "$@"
