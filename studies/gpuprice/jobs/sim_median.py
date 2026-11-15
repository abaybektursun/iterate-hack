"""SPEC1: quantile forecasts of a median by resampling its listings' historical h-day outcomes.

python -I -B studies/gpuprice/jobs/sim_median.py --pack <pack> --series studies/gpuprice/data/event_series_v1.csv \
    --origin-start 2026-10-01 --origin-end 2026-10-30 --out <forecast.csv> [--control]
Writes rows only for the series it models (fastgpu_daily, gpurentalprices). Laptop, no GPU.
"""
import argparse, datetime as dt
import duckdb, numpy as np, pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--pack", required=True); ap.add_argument("--series", required=True)
ap.add_argument("--origin-start", required=True); ap.add_argument("--origin-end", required=True)
ap.add_argument("--out", required=True); ap.add_argument("--draws", type=int, default=2000)
ap.add_argument("--control", action="store_true", help="resample the median's own change, not the listings")
a = ap.parse_args()
HORIZONS, SOURCES = (1, 3, 7), ("fastgpu_daily", "gpurentalprices")

ev = pd.read_csv(a.series)
ev = ev[ev.source_id.isin(SOURCES)]
con = duckdb.connect(); con.register("ev", ev)
obs = con.sql(f"""
  select ev.series_id, o.dt::date as d,
         o.provider || '|' || coalesce(o.region_raw, '') || '|' || coalesce(o.sku_raw, '') as listing,
         o.usd_per_gpu_hour as p
  from read_parquet('{a.pack}/rental_observations/*/*/*.parquet', hive_partitioning=false) o
  join ev on o.source_id = ev.source_id and o.instrument_class = ev.instrument_class
         and o.gpu_model = ev.gpu_model and o.pricing_tier = ev.pricing_tier""").df()
assert not obs.duplicated(["series_id", "d", "listing"]).any(), "listing key is not unique per day"
obs["d"] = pd.to_datetime(obs.d).dt.date

rng = np.random.default_rng(0)
origins = pd.date_range(a.origin_start, a.origin_end).date
rows = []
for sid, g in obs.groupby("series_id"):
    days = {d: x.set_index("listing").p for d, x in g.groupby("d")}
    med = {d: float(np.median(s.values)) for d, s in days.items()}
    for t in origins:
        past = sorted(d for d in days if d <= t)
        now = days[past[-1]]; m0 = med[past[-1]]
        for h in HORIZONS:
            wins = []
            for s in past:
                e = s + dt.timedelta(days=h)
                if e > t or e not in days:
                    continue
                ps, pe = days[s], days[e]
                stay = np.log(pe.reindex(ps.index) / ps).values          # nan = the listing left
                enter = (pe[~pe.index.isin(ps.index)] / med[s]).values  # entrants, as a ratio to the old median
                wins.append((stay, enter, np.log(med[e] / med[s])))
            if len(wins) < 5:
                q = [m0, m0, m0]
            else:
                sims = np.empty(a.draws)
                for i, w in enumerate(rng.integers(len(wins), size=a.draws)):
                    stay, enter, dmed = wins[w]
                    if a.control:
                        sims[i] = m0 * np.exp(dmed); continue
                    out = rng.choice(stay, size=len(now))
                    new = now.values * np.exp(out)
                    new = np.concatenate([new[~np.isnan(new)], m0 * rng.choice(enter, size=len(enter))]) if len(enter) else new[~np.isnan(new)]
                    sims[i] = np.median(new) if len(new) else m0
                q = np.quantile(sims, [0.1, 0.5, 0.9])
            rows.append((sid, t, h, round(q[0], 6), round(q[1], 6), round(q[2], 6), len(wins)))
pd.DataFrame(rows, columns=["series_id", "origin_date", "horizon_days", "q10", "q50", "q90", "n_windows"]).to_csv(a.out, index=False)
print(f"wrote {len(rows)} rows, {obs.series_id.nunique()} series, {len(origins)} origins -> {a.out}")
