#!/usr/bin/env bash
# One command for the submitted forecast (origin 2026-11-06, horizons 1, 3, 7, 37 series; specs/SPEC2.md).
# Run from the repository root: bash studies/gpuprice/jobs/reproduce.sh
# Inputs: the pack (downloaded and checked by prep/get_pack.sh), the committed listing panel built from it
# (data/fm2_panel_v2.csv.gz, jobs/fm2_panel.py) and the ECB EUR/USD rates to 2026-11-06 (data/ext_ecb_eurusd_v1.csv).
# Step 2 is the only model inference: amazon/chronos-2 zero-shot, about 2 minutes on one H100 through the team
# runner. Without the runner, run `bash studies/gpuprice/jobs/fm2_chronos2.sh --origins event` on any machine with
# OUT_DIR set and pass its fm2_chronos2.csv as CHRONOS_CSV.
set -euo pipefail
R=runs/gpuprice; P=$R/pack/gpu-price-pack-v0.1.1-handover; PY="$R/.venv/bin/python -I -B"; O=$R/submission
[ -d $P ] || bash studies/gpuprice/prep/get_pack.sh
mkdir -p $O
if [ -z "${CHRONOS_CSV:-}" ]; then
  JOB=$(uv run tools/gpu.py submit h100 --hours 0.3 -- 'bash studies/gpuprice/jobs/fm2_chronos2.sh --origins event' | tail -1)
  uv run tools/gpu.py wait "$JOB" > /dev/null
  uv run tools/gpu.py get "$JOB" > /dev/null
  CHRONOS_CSV=runs/$JOB/fm2_chronos2.csv
fi
$PY studies/gpuprice/jobs/fm2_post.py --quantiles "$CHRONOS_CSV" --origins event --out $O/fm2-17.csv \
    --hurdle --hurdle-h 1 --scaleway --turnover own --enter abs
$PY studies/gpuprice/jobs/sim2_own.py --pack $P --series studies/gpuprice/data/event_series_v1.csv \
    --origin-start 2026-11-06 --origin-end 2026-11-06 --out $O/sim2-15.csv --tau 14 --shrink 0.2 --abs-enter 2 --afh
$PY studies/gpuprice/jobs/average.py studies/gpuprice/results/submission/forecast_2026-11-06.csv $O/fm2-17.csv $O/sim2-15.csv
