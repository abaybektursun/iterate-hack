"""Builds the fine-tuning panel of the ft arm: studies/gpuprice/data/ft_panel_<cutoff>.parquet. Laptop, no model.

runs/gpuprice/.venv/bin/python -I -B studies/gpuprice/jobs/ft_panel.py --pack <pack> \
    --ext runs/gpuprice/ext/rental_observations_ext.parquet --cutoff 2026-09-30 \
    --out studies/gpuprice/data/ft_panel_2026-09-30.parquet
One row per listing and day: source_id, listing, d, p (USD per GPU-hour). A listing is one posted offer line of one
collector: instrument_class|gpu_model|pricing_tier|provider|region_raw|sku_raw|gpu_count. All GPU models of all
collectors, not only the 37 event series. A day with several snapshots keeps the last snapshot (lowest price on a
tie). Only rows dated on or before --cutoff, so a model trained on this file has seen no later price.
Data: GPU price pack v0.1.1-handover, CC BY 4.0, see studies/gpuprice/ATTRIBUTION.md; --ext is the collectors'
earlier history from their pinned git commits (prep/ext_history.py).
"""
import argparse
import duckdb

ap = argparse.ArgumentParser()
ap.add_argument("--pack", required=True); ap.add_argument("--ext", required=True)
ap.add_argument("--cutoff", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()
con = duckdb.connect()
con.sql(f"""create table l as
  with o as (select * from read_parquet('{a.pack}/rental_observations/*/*/*.parquet', hive_partitioning=false)
             union all by name select * from read_parquet('{a.ext}')),
  k as (select source_id, dt::date as d, snapshot_ts_utc as ts, usd_per_gpu_hour as p,
               concat_ws('|', instrument_class, gpu_model, pricing_tier, provider, coalesce(region_raw, ''),
                         coalesce(sku_raw, ''), coalesce(gpu_count::varchar, '')) as listing
        from o where dt::date <= date '{a.cutoff}' and usd_per_gpu_hour > 0)
  select source_id, listing, d, cast(round(min(p), 6) as float) as p
  from (select *, max(ts) over (partition by source_id, listing, d) as mts from k) where ts = mts
  group by all order by source_id, listing, d""")
n, last = con.sql("select count(*), max(d) from l").fetchall()[0]
assert str(last) <= a.cutoff and n > 0
con.sql(f"copy l to '{a.out}' (format parquet, compression zstd, compression_level 19)")
print(con.sql("""select source_id, count(*) as "rows", count(distinct listing) as listings, min(d) as first, max(d) as last
                 from l group by 1 order by 1""").df().to_string(index=False))
print(n, "rows ->", a.out)
