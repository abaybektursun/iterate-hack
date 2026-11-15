"""Average of per-listing quantile files (fm2_chronos2.csv of several models or seeds), level by level, for fm2_post.py.

runs/gpuprice/.venv/bin/python -I -B studies/gpuprice/jobs/loc_qavg.py <out.csv> <a.csv> <b.csv> [...]
The files must hold the same rows (setup, series_id, unit, origin_date, horizon_days); rows of setups missing from a
file are dropped. The mean of quantile functions at each level is the Vincentized average of the distributions.
"""
import sys
import pandas as pd

K = ["setup", "series_id", "unit", "origin_date", "horizon_days"]
out, files = sys.argv[1], sys.argv[2:]
fr = [pd.read_csv(f, keep_default_na=False).set_index(K) for f in files]
setups = set.intersection(*(set(f.index.get_level_values(0)) for f in fr))
fr = [f[f.index.get_level_values(0).isin(setups)] for f in fr]
for f in fr[1:]:
    assert f.index.sort_values().equals(fr[0].index.sort_values()), "the files do not hold the same rows"
avg = sum(f.loc[fr[0].index] for f in fr) / len(fr)
avg.reset_index().to_csv(out, index=False, float_format="%.6g")
print(f"wrote {len(avg)} rows, mean of {len(fr)} files -> {out}")
