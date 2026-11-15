#!/usr/bin/env bash
# GPU job: bash studies/gpuprice/jobs/fm_chronos2.sh [arguments of fm_chronos2.py]
set -euo pipefail
pip install -q "chronos-forecasting>=2.0"
pip list 2>/dev/null | grep -i -E "^(chronos|torch|transformers) "
python studies/gpuprice/jobs/fm_chronos2.py "$@"
