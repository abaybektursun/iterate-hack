"""Builds the committed input of the foundation-model jobs: studies/gpuprice/data/fm_panel_v1.csv.

runs/gpuprice/.venv/bin/python -I -B studies/gpuprice/jobs/fm_panel.py --pack <pack> \
    --history runs/gpuprice/event/history_2026-11-06.csv --series studies/gpuprice/data/event_series_v1.csv \
    --out studies/gpuprice/data/fm_panel_v1.csv
Rows: series_id, d, listing, p. listing '' is the series value itself (all 37 series); other rows are the listings
(provider|region|sku) of the fastgpu_daily and gpurentalprices series. Only rows dated on or before --last
(default 2026-10-30, the last development origin), so a job that reads this file cannot see a later price.
Data: GPU price pack v0.1.1-handover, CC BY 4.0, see studies/gpuprice/ATTRIBUTION.md.
"""
import argparse
import duckdb, pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--pack", required=True); ap.add_argument("--history", required=True)
ap.add_argument("--series", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--last", default="2026-10-30")
a = ap.parse_args()
ev = pd.read_csv(a.series)
con = duckdb.connect(); con.register("ev", ev)
lst = con.sql(f"""
  select ev.series_id, cast(o.dt::date as varchar) as d,
         o.provider || '|' || coalesce(o.region_raw, '') || '|' || coalesce(o.sku_raw, '') as listing,
         o.usd_per_gpu_hour as p
  from read_parquet('{a.pack}/rental_observations/*/*/*.parquet', hive_partitioning=false) o
  join ev on o.source_id = ev.source_id and o.instrument_class = ev.instrument_class
         and o.gpu_model = ev.gpu_model and o.pricing_tier = ev.pricing_tier
  where ev.source_id in ('fastgpu_daily', 'gpurentalprices') and o.dt::date <= date '{a.last}'""").df()
assert not lst.duplicated(["series_id", "d", "listing"]).any(), "listing key is not unique per day"
assert (lst.listing != "").all()
h = pd.read_csv(a.history, usecols=["series_id", "date", "value", "is_filled"])
h = h[h.series_id.isin(ev.series_id) & (h.date <= a.last)]
assert h.is_filled.eq(0).all() and h.series_id.nunique() == 37
ser = pd.DataFrame({"series_id": h.series_id, "d": h.date, "listing": "", "p": h.value})
# the series value must be the median of its listings, or the listing-level arm models another quantity
chk = lst.groupby(["series_id", "d"]).p.median().rename("m").reset_index().merge(ser, on=["series_id", "d"], how="outer", indicator=True)
chk = chk[chk.series_id.isin(lst.series_id.unique())]
print("series-days:", chk._merge.value_counts().to_dict(), "max |median of listings - series value|:", (chk.m - chk.p).abs().max())
out = pd.concat([ser, lst]).sort_values(["series_id", "listing", "d"])
out["p"] = out.p.round(6)
out.to_csv(a.out, index=False)
print(len(ser), "series rows,", len(lst), "listing rows,", lst.groupby("series_id").listing.nunique().describe().to_dict(), "->", a.out)
