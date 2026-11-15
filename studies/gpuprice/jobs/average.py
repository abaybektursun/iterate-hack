"""Quantile average of forecast files with the same cells: python average.py <out.csv> <a.csv> <b.csv> [...]"""
import sys
import pandas as pd

K, Q = ["series_id", "origin_date", "horizon_days"], ["q10", "q50", "q90"]
out, files = sys.argv[1], sys.argv[2:]
frames = [pd.read_csv(f)[K + Q].set_index(K) for f in files]
for f in frames[1:]:
    assert f.index.sort_values().equals(frames[0].index.sort_values()), "the files do not hold the same cells"
avg = sum(f.loc[frames[0].index] for f in frames) / len(frames)
assert (avg.q10 > 0).all() and (avg.q10 <= avg.q50).all() and (avg.q50 <= avg.q90).all()
avg.round(6).reset_index().to_csv(out, index=False)
print(f"wrote {len(avg)} rows, {avg.index.get_level_values(0).nunique()} series -> {out}")
