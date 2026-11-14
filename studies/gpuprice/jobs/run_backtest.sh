#!/usr/bin/env bash
# Backtest of the SPEC1 simulator on the event set, from a pack unpacked by prep/get_pack.sh.
# Run from the repository root: bash studies/gpuprice/jobs/run_backtest.sh <out_dir> [--control]
# Then: python3 studies/gpuprice/analysis/readout.py <out_dir> studies/gpuprice/results/<experiment>/<arm>-<nn> "<command>"
set -euo pipefail
O="${1:?usage: run_backtest.sh <out_dir> [--control]}"; shift
R=$PWD/runs/gpuprice; P=$R/pack/gpu-price-pack-v0.1.1-handover; S=$P/starter
PY="$R/.venv/bin/python -I -B"; C=2026-11-06; A=2026-10-01; B=2026-10-30
mkdir -p "$O"
$PY $S/build_series.py --pack $P --cutoff $C --as-of $C --out "$O/history.csv" --catalog "$O/catalog.csv"
$PY $S/baselines.py --history "$O/history.csv" --origin-start $A --origin-end $B --origin-step 1 \
    --method last_value_empirical --catalog "$O/catalog.csv" --tier headline --out "$O/lve.csv"
$PY studies/gpuprice/jobs/sim_median.py --pack $P --series studies/gpuprice/data/event_series_v1.csv \
    --origin-start $A --origin-end $B --out "$O/sim.csv" "$@"
# the series the simulator does not model (afhubbard) keep last_value_empirical
$PY -c "
import pandas as pd, sys
o = sys.argv[1]; k = ['series_id', 'origin_date', 'horizon_days', 'q10', 'q50', 'q90']
s = pd.read_csv(o + '/sim.csv'); b = pd.read_csv(o + '/lve.csv')
pd.concat([s[k], b[~b.series_id.isin(s.series_id)][k]]).to_csv(o + '/forecast_sim.csv', index=False)" "$O"
$PY $S/scorer.py --forecast "$O/forecast_sim.csv" --truth "$O/history.csv" --history "$O/history.csv" \
    --catalog "$O/catalog.csv" --tier headline --horizons 1,3,7 --out "$O/report_sim.json" --per-cell "$O/cells_sim.csv"
