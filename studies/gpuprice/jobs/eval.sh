#!/usr/bin/env bash
# Score one forecast file on the development origins and write one ledger entry.
# bash studies/gpuprice/jobs/eval.sh <forecast.csv> <name> "<one line: what changed and why>"
# The forecast holds rows for origins 2026-10-01..2026-10-30, horizons 1, 3, 7, any subset of the 37 event series;
# a missing cell is scored as flat last value, as at the event. Writes results/ledger/<name>.json (refuses to
# overwrite) and runs/gpuprice/evals/<name>/.
set -euo pipefail
F="${1:?forecast csv}"; N="${2:?name}"; NOTE="${3:?note}"
R=$PWD/runs/gpuprice; S=$R/pack/gpu-price-pack-v0.1.1-handover/starter; PY="$R/.venv/bin/python -I -B"
L=studies/gpuprice/results/ledger/$N.json; O=$R/evals/$N
[ -e "$L" ] && { echo "ledger entry $L exists: pick a new name"; exit 1; }
mkdir -p "$O" studies/gpuprice/results/ledger
$PY -c "
import pandas as pd, sys
f = pd.read_csv(sys.argv[1]); f = f[(f.origin_date >= '2026-10-01') & (f.origin_date <= '2026-10-30')]
assert len(f), 'no row on the development origins'
f.to_csv(sys.argv[2], index=False)" "$F" "$O/forecast.csv"
$PY $S/scorer.py --forecast "$O/forecast.csv" --truth $R/event/history_2026-11-06.csv --history $R/event/history_2026-11-06.csv \
    --catalog $R/event/catalog_2026-11-06.csv --tier headline --horizons 1,3,7 --missing-as-baseline \
    --out "$O/report.json" --per-cell "$O/cells.csv" > /dev/null
$PY -c "
import json, subprocess, sys, datetime
r = json.load(open(sys.argv[1])); o = r['overall']
e = {'name': sys.argv[3], 'note': sys.argv[4], 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
     'commit': subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], text=True).strip(),
     'origins': '2026-10-01..2026-10-30', 'cells': r['cells'], 'skill_pooled': o['skill_pooled'],
     'pinball': o['pinball'], 'last_value_pinball': o['baseline_pinball'],
     'skill_median_of_series': o['skill_median_of_series'], 'skill_geomean': o['skill_geomean'],
     'by_horizon': {h: {'skill_pooled': v['skill_pooled'], 'in_band': v['coverage']['within_q10_q90']} for h, v in r['by_horizon'].items()},
     'in_band': o['coverage']['within_q10_q90']}
json.dump(e, open(sys.argv[2], 'w'), indent=1)
print(e['name'], 'pooled', e['skill_pooled'], {h: v['skill_pooled'] for h, v in e['by_horizon'].items()}, 'in-band', round(e['in_band'], 3), 'cells', e['cells']['scored'])
" "$O/report.json" "$L" "$N" "$NOTE"
