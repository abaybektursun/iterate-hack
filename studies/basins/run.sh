#!/bin/bash
# The one place the basins study's laptop scripts get their environment: Python 3.12 (wheels exist; 3.15 resolved
# slowly and hung once) and requirements.txt's numpy/scipy/scikit-learn pins. Run from the repository root:
#   bash studies/basins/run.sh studies.basins.analysis.swarm_analyze <args>
set -euo pipefail
exec uv run -q -p 3.12 --no-project --with numpy==2.5.4 --with scipy==1.18.1 --with scikit-learn==1.9.1 \
  --with math-verify==0.9.0 python -m "$@"
