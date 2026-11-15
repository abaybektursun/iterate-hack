"""Builds the text context of each (series, origin) for the LLM forecaster, on the laptop, from the pack.

runs/gpuprice/.venv/bin/python -I -B studies/gpuprice/jobs/llm_context.py --pack <pack> --history runs/gpuprice/event/history_2026-11-06.csv \
    --series <series_id,...|all> --origins 2026-10-01,2026-10-04,... --out studies/gpuprice/data/llm_context_<v>.jsonl

One JSON line per (series, origin): the context text (series definition, each listing's posted price over the last
21 days with unchanged runs compressed, the median over the last 42 days), the last median, and the target date
of each horizon. Leak rule: only rows dated on or before the origin are read into a context (asserted).
"""
import argparse, datetime as dt, json
import duckdb, numpy as np, pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--pack", required=True); ap.add_argument("--history", required=True)
ap.add_argument("--catalog", default="studies/gpuprice/data/event_series_v1.csv")
ap.add_argument("--series", required=True); ap.add_argument("--origins", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--days", type=int, default=21); ap.add_argument("--median-days", type=int, default=42)
a = ap.parse_args()
HORIZONS = (1, 3, 7)

ev = pd.read_csv(a.catalog)
ev = ev[ev.source_id.isin(("fastgpu_daily", "gpurentalprices"))]
if a.series != "all":
    want = a.series.split(",")
    assert set(want) <= set(ev.series_id), "unknown series"
    ev = ev[ev.series_id.isin(want)]
origins = [dt.date.fromisoformat(x) for x in a.origins.split(",")]
assert all(dt.date(2026, 10, 1) <= t <= dt.date(2026, 10, 30) for t in origins), "origin outside the development window"

con = duckdb.connect(); con.register("ev", ev)
obs = con.sql(f"""
  select ev.series_id, o.dt::date as d, o.provider, coalesce(o.region_raw, '') as region, coalesce(o.sku_raw, '') as sku,
         o.usd_per_gpu_hour as p
  from read_parquet('{a.pack}/rental_observations/*/*/*.parquet', hive_partitioning=false) o
  join ev on o.source_id = ev.source_id and o.instrument_class = ev.instrument_class
         and o.gpu_model = ev.gpu_model and o.pricing_tier = ev.pricing_tier""").df()
obs["d"] = pd.to_datetime(obs.d).dt.date
hist = pd.read_csv(a.history); hist = hist[hist.series_id.isin(ev.series_id)]
hist["d"] = pd.to_datetime(hist.date).dt.date


def fmt(x):
    return f"{x:.4f}".rstrip("0").rstrip(".")


def runs(days, val):
    """'10-01..10-12 4.264 | 10-13 4.3': consecutive calendar days with the same value merged. val: day -> text."""
    out, start, prev = [], days[0], days[0]
    for d in days[1:] + [None]:
        if d is None or val[d] != val[start]:
            span = f"{start:%m-%d}" if prev == start else f"{start:%m-%d}..{prev:%m-%d}"
            out.append(f"{span} {val[start]}")
            start = d
        prev = d
    return " | ".join(out)


n = 0
with open(a.out, "w") as f:
    for r in ev.itertuples():
        g = obs[obs.series_id == r.series_id]
        # the shortest listing name that is unique within a day: provider, then with region, then with SKU
        for cols in (["provider"], ["provider", "region"], ["provider", "region", "sku"]):
            if not g.duplicated(["d"] + cols).any():
                break
        else:
            raise AssertionError(f"{r.series_id}: listing key is not unique per day")
        g = g.assign(listing=g[cols].agg(lambda x: " / ".join(v for v in x if v), axis=1))
        h = hist[hist.series_id == r.series_id].set_index("d").value
        for t in origins:
            gp, hp = g[g.d <= t], h[h.index <= t]
            assert gp.d.max() <= t and hp.index.max() <= t
            m0, last_day = float(hp.iloc[-1]), hp.index[-1]
            win = [t - dt.timedelta(days=i) for i in range(a.days - 1, -1, -1)]
            have = set(gp.d)
            tab = gp[gp.d >= win[0]].pivot(index="listing", columns="d", values="p")
            lines = []
            for name, row in tab.sort_values(by=tab.columns[-1], na_position="last").iterrows():
                val = {d: ("no data" if d not in have else "-" if d not in row.index or np.isnan(row[d]) else fmt(row[d])) for d in win}
                lines.append(f"{name}: {runs(win, val)}")
            mwin = [t - dt.timedelta(days=i) for i in range(a.median_days - 1, -1, -1)]
            mwin = [d for d in mwin if d >= hp.index[0]]
            mval = {d: (fmt(hp[d]) if d in hp.index else "no data") for d in mwin}
            unit = {1: "provider", 2: "provider and region", 3: "provider, region and SKU"}[len(cols)]
            text = (
                f"Series: the daily median of the posted rental prices, in USD per GPU-hour, of all listings of the GPU {r.gpu_model} "
                f"(pricing tier: {r.pricing_tier}; market segment: {r.instrument_class}) collected by the price tracker {r.source_id}. "
                f"A listing is one {unit}. These are posted prices, not paid prices. The median moves when a listing changes its price, "
                f"and it also moves when a listing enters or leaves, with no price changed.\n\n"
                f"Price of each listing from {win[0]} to {t} (month-day ranges; a range holds one unchanged price; "
                f"\"-\" = the listing was absent; \"no data\" = the tracker collected nothing that day):\n" + "\n".join(lines) + "\n\n"
                f"Median of the listings from {mwin[0]} to {t}:\n{runs(mwin, mval)}\n\n"
                f"Today is {t:%A} {t}. The latest median is {fmt(m0)}" + (f" (from {last_day})" if last_day != t else "") + ".")
            assert not any(str(t + dt.timedelta(days=k)) in text or f"{t + dt.timedelta(days=k):%m-%d}" in text for k in range(1, 40)), "a later date is in the context"
            f.write(json.dumps({"series_id": r.series_id, "origin_date": str(t), "last_value": m0, "context": text,
                                "targets": {str(k): str(t + dt.timedelta(days=k)) for k in HORIZONS}}) + "\n")
            n += 1
print(f"wrote {n} contexts -> {a.out}")
