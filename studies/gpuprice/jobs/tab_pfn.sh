#!/usr/bin/env bash
# CPU or GPU job: bash studies/gpuprice/jobs/tab_pfn.sh [arguments of tab_pfn.py]
set -euo pipefail
export TABPFN_DISABLE_TELEMETRY=1
pip install -q "tabpfn==10.0.0"
pip list 2>/dev/null | grep -i -E "^(tabpfn|torch|scikit-learn) "
python studies/gpuprice/jobs/tab_pfn.py "$@"
