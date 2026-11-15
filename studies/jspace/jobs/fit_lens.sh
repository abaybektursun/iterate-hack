#!/bin/bash
# Installs the reference J-lens code at a pinned commit, then runs fit_lens.py with the given arguments.
set -euo pipefail
pip install -q "git+https://github.com/anthropics/jacobian-lens@581d398613e5602a5af361e1c34d3a92ea82ba8e"
python -m studies.jspace.jobs.fit_lens "$@"
