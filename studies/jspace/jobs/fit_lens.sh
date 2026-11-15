#!/bin/bash
# Installs the reference J-lens code at a pinned commit, then runs fit_lens.py with the given arguments.
set -euo pipefail
# the runner image has no git, so the pinned commit is installed from its archive
pip install -q "https://github.com/anthropics/jacobian-lens/archive/581d398613e5602a5af361e1c34d3a92ea82ba8e.zip"
python -m studies.jspace.jobs.fit_lens "$@"
