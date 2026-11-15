"""Builds studies/gpuprice/data/fm2_intraday_v1.csv.gz: the daily maximum price of each fastgpu_daily listing.

runs/gpuprice/.venv/bin/python -I -B studies/gpuprice/prep/intraday.py \
    --pack runs/gpuprice/pack/gpu-price-pack-v0.1.1-handover --series studies/gpuprice/data/event_series_v1.csv \
    --out studies/gpuprice/data/fm2_intraday_v1.csv.gz
fastgpu_daily publishes, per provider, GPU and day, the minimum (usd_per_gpu_hour, the price the series is built
from), the average and the maximum (usd_per_gpu_hour_max) of the day's snapshots. The maximum of day d is dated d.
Rows: series_id, listing (provider|region|sku, the key of fm2_panel_v2), d, pmax. Rows dated after --last are not read.
Data: GPU price pack v0.1.1-handover, CC BY 4.0, see studies/gpuprice/ATTRIBUTION.md.
"""
import argparse
import duckdb, pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--pack", required=True); ap.add_argument("--series", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--last", default="2026-11-06")
a = ap.parse_args()
ev = pd.read_csv(a.series)
con = duckdb.connect(); con.register("ev", ev)
x = con.sql(f"""select ev.series_id, o.provider || '|' || coalesce(o.region_raw, '') || '|' || coalesce(o.sku_raw, '') as listing,
         cast(o.dt::date as varchar) as d, o.usd_per_gpu_hour as p, o.usd_per_gpu_hour_max as pmax
  from read_parquet('{a.pack}/rental_observations/*/*/*.parquet', hive_partitioning=false) o
  join ev on o.source_id = ev.source_id and o.instrument_class = ev.instrument_class
         and o.gpu_model = ev.gpu_model and o.pricing_tier = ev.pricing_tier
  where o.source_id = 'fastgpu_daily' and o.dt::date <= date '{a.last}' order by 1, 2, 3""").df()
assert not x.duplicated(["series_id", "listing", "d"]).any() and x.pmax.notna().all() and (x.pmax >= x.p - 1e-9).all()
assert x.d.max() <= a.last
x[["series_id", "listing", "d", "pmax"]].to_csv(a.out, index=False)
print("wrote", len(x), "rows,", x.series_id.nunique(), "series, days", x.d.min(), "to", x.d.max(), "| max > min on", round((x.pmax > x.p + 1e-9).mean(), 4), "of rows")
