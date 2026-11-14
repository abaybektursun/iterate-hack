"""sim2: replay each listing's OWN historical h-day outcome on today's listings, windows weighted by recency.

python -I -B studies/gpuprice/jobs/sim2_own.py --pack <pack> --series studies/gpuprice/data/event_series_v1.csv \
    --origin-start 2026-10-01 --origin-end 2026-10-30 --out <forecast.csv> [options]

For a series, origin t, horizon h, with rows dated on or before t only:
1. Today's listings are those of the last observed day L <= t. The gap to forecast is g = h + (t - L) days
   (--no-gap uses g = h as SPEC1 did).
2. Every past window (s, s+g) with both days observed and s+g <= t is one scenario with weight
   exp(-(t - (s+g)) / tau). In it, a listing that was present at s repeats its own outcome (price ratio, or exit).
   A listing that was absent at s draws an outcome from its provider's listings in that window, or from all
   listings of the window if the provider had none (--pool draws every listing from the window, as SPEC1).
   The window's entrants are added at their ratio to the median at s.
3. q10, q50, q90 are the weighted quantiles of the scenario medians.
Optional layers, all fitted at origin t on forecasts whose target date is <= t (rolling, see --mix and --cal).
Writes rows only for fastgpu_daily and gpurentalprices. Laptop, no GPU.
"""
import argparse, datetime as dt, zlib
import duckdb, numpy as np, pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--pack", required=True); ap.add_argument("--series", required=True)
ap.add_argument("--origin-start", required=True); ap.add_argument("--origin-end", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--tau", type=float, default=0, help="recency e-folding time of the window weights in days; 0 = uniform")
ap.add_argument("--pool", action="store_true", help="ablation: every listing draws from the window's pool (SPEC1)")
ap.add_argument("--no-gap", action="store_true", help="ablation: ignore the days between the last observed day and t")
ap.add_argument("--reps", type=int, default=20, help="draws per window when some listing needs a random outcome")
ap.add_argument("--shrink", type=float, default=0, help="probability that a listing takes an outcome of the same window drawn from all "
                "series of its collector and class, instead of its own")
ap.add_argument("--abs-enter", type=int, default=0, help="a window's entrant enters at its own posted price. 1: only if it is "
                "absent today. 2: a listing first seen after s always enters (arrival of a new listing), a returning "
                "one only if absent today. Default 0, as SPEC1: every entrant, at its ratio to the median at s")
ap.add_argument("--afh", action="store_true", help="also forecast the afhubbard series, from the median's own g-day changes "
                "over all past windows, uniform weights (no listing model: 1 to 3 snapshots a day)")
ap.add_argument("--mix", type=float, default=0, help="weight of the median's own change scenarios (control) added to the replay scenarios")
ap.add_argument("--cal", action="store_true", help="rolling calibration of q10 and q90 offsets on past pooled errors")
ap.add_argument("--burn", type=int, default=21, help="days of origins before --origin-start computed for --cal")
a = ap.parse_args()
HORIZONS, SOURCES, QS = (1, 3, 7), ("fastgpu_daily", "gpurentalprices"), (0.1, 0.5, 0.9)
t0, t1 = dt.date.fromisoformat(a.origin_start), dt.date.fromisoformat(a.origin_end)

ev_all = pd.read_csv(a.series)
ev = ev_all[ev_all.source_id.isin(SOURCES)]
con = duckdb.connect(); con.register("ev", ev); con.register("ev_afh", ev_all[ev_all.source_id == "afhubbard"])
obs = con.sql(f"""
  select ev.series_id, o.dt::date as d, o.provider,
         o.provider || '|' || coalesce(o.region_raw, '') || '|' || coalesce(o.sku_raw, '') as listing,
         o.usd_per_gpu_hour as p
  from read_parquet('{a.pack}/rental_observations/*/*/*.parquet', hive_partitioning=false) o
  join ev on o.source_id = ev.source_id and o.instrument_class = ev.instrument_class
         and o.gpu_model = ev.gpu_model and o.pricing_tier = ev.pricing_tier
  where o.dt::date <= date '{t1}'""").df()
assert not obs.duplicated(["series_id", "d", "listing"]).any(), "listing key is not unique per day"
obs["d"] = pd.to_datetime(obs.d).dt.date



def wquant(v, w, qs):
    o = np.argsort(v); v, w = v[o], w[o] / w.sum()
    return list(np.interp(qs, np.cumsum(w) - w / 2, v))                 # linear between scenario midpoints


def scenarios(P, prov, med, days, t, h, group):
    """Scenario medians and weights for one series, origin t, horizon h. P: days x listings, nan = absent."""
    li = max(i for i, d in enumerate(days) if d <= t)
    m0 = med[li]; g = h if a.no_gap else h + (t - days[li]).days
    cur = ~np.isnan(P[li]); now = P[li, cur]; cprov = prov[cur]
    first = np.argmax(~np.isnan(P), axis=0)                              # row of each listing's first appearance
    idx = {d: i for i, d in enumerate(days[:li + 1])}
    vals, wts, dmed = [], [], []
    for si in range(li + 1):
        ei = idx.get(days[si] + dt.timedelta(days=g))
        if ei is None:
            continue
        w = np.exp(-(t - days[ei]).days / a.tau) if a.tau else 1.0
        at_s = ~np.isnan(P[si]); ratio = P[ei] / P[si]                   # nan = absent at s, or left by s+g
        own = ratio[cur]; need = ~at_s[cur]
        if a.pool:
            need = np.ones(cur.sum(), bool)
        enter = m0 * P[ei, ~at_s & ~np.isnan(P[ei])] / med[si]
        if a.abs_enter:
            new = first > si                                              # not seen on or before day s
            enter = P[ei, ~at_s & ~np.isnan(P[ei]) & (~cur | new if a.abs_enter == 2 else ~cur)]
        pools = [ratio[at_s & (prov == p)] if not a.pool and (at_s & (prov == p)).any() else ratio[at_s] for p in cprov[need]]
        reps = a.reps if need.any() or a.shrink else 1
        big = group_pool(group, days[si], days[ei]) if a.shrink else None
        for _ in range(reps):
            r = own.copy()
            r[need] = [rng.choice(q) for q in pools]
            if a.shrink:
                sw = rng.random(len(r)) < a.shrink
                r[sw] = rng.choice(big, size=sw.sum())
            new = np.concatenate([(now * r)[~np.isnan(r)], enter])
            vals.append(np.median(new) if len(new) else m0); wts.append(w / reps)
        dmed.append((m0 * med[ei] / med[si], w))
    return m0, np.array(vals), np.array(wts), dmed


series = {}                                                             # series_id -> (group, days, P, providers)
for sid, g_ in obs.groupby("series_id"):
    M = g_.pivot(index="d", columns="listing", values="p").sort_index()
    e = ev[ev.series_id == sid].iloc[0]
    series[sid] = ((e.source_id, e.instrument_class), list(M.index), M.values, np.array([c.split("|")[0] for c in M.columns]))
cache = {}


def group_pool(group, ds, de):
    """Price ratios (nan = exit) from day ds to day de of every listing of every series of one collector and class."""
    k = (group, ds, de)
    if k not in cache:
        out = []
        for g2, days, P, _ in series.values():
            if g2 == group and ds in days and de in days:
                i, j = days.index(ds), days.index(de)
                out.append((P[j] / P[i])[~np.isnan(P[i])])
        cache[k] = np.concatenate(out)
    return cache[k]


first = t0 - dt.timedelta(days=a.burn) if a.cal else t0
origins = pd.date_range(first, t1).date
rows = []
for sid, (group, days, P, prov) in series.items():
    med = np.nanmedian(P, axis=1)
    for t in origins:
        if days[0] > t:
            continue
        for h in HORIZONS:
            rng = np.random.default_rng(zlib.crc32(f"{sid}|{t}|{h}".encode()))   # same draws for an origin run alone or in a range
            m0, v, w, dmed = scenarios(P, prov, med, days, t, h, group)
            if len(dmed) < 5:
                q = [m0, m0, m0]
            else:
                if a.mix:
                    dv, dw = np.array(dmed).T
                    v = np.concatenate([v, dv]); w = np.concatenate([w / w.sum() * (1 - a.mix), dw / dw.sum() * a.mix])
                q = wquant(v, w, QS)
            rows.append((sid, t, h, m0, *q, len(dmed)))
if a.afh:
    afh = con.sql(f"""
      select ev_afh.series_id, o.dt::date as d, median(o.usd_per_gpu_hour) as m
      from read_parquet('{a.pack}/rental_observations/*/*/*.parquet', hive_partitioning=false) o
      join ev_afh on o.source_id = ev_afh.source_id and o.instrument_class = ev_afh.instrument_class
             and o.gpu_model = ev_afh.gpu_model and o.pricing_tier = ev_afh.pricing_tier
      where o.dt::date <= date '{t1}' group by all""").df()
    afh["d"] = pd.to_datetime(afh.d).dt.date
    for sid, x in afh.groupby("series_id"):
        m = dict(zip(x.d, x.m))
        for t in origins:
            past = sorted(d for d in m if d <= t)
            for h in HORIZONS:
                g = h + (t - past[-1]).days; m0 = m[past[-1]]
                v = np.array([m0 * m[s + dt.timedelta(days=g)] / m[s] for s in past if s + dt.timedelta(days=g) in m and s + dt.timedelta(days=g) <= t])
                q = wquant(v, np.ones(len(v)), QS) if len(v) >= 5 else [m0, m0, m0]
                rows.append((sid, t, h, m0, *q, len(v)))
f = pd.DataFrame(rows, columns=["series_id", "origin_date", "horizon_days", "last", "q10", "q50", "q90", "n_windows"])

if a.cal:
    # Rolling calibration. At origin t, for each horizon and each side, pick the multiplier k of the offset
    # (q - q50) that minimises the pooled pinball loss of all series' past forecasts whose target date is <= t.
    # The truth of a past forecast is the series median on its target date, from rows dated <= t.
    truth = {(s, d): float(np.median(x.values)) for (s, d), x in obs.groupby(["series_id", "d"]).p}
    f["target"] = [o + dt.timedelta(days=int(h)) for o, h in zip(f.origin_date, f.horizon_days)]
    f["y"] = [truth.get(k, np.nan) for k in zip(f.series_id, f.target)]
    KS = np.round(np.arange(0.0, 4.01, 0.25), 2)
    for t in pd.date_range(t0, t1).date:
        for h in HORIZONS:
            cur = (f.origin_date == t) & (f.horizon_days == h)
            past = f[(f.horizon_days == h) & (f.target <= t) & f.y.notna()]
            if len(past) < 100:
                continue
            for col, q in (("q10", 0.1), ("q90", 0.9)):
                off = (past[col] - past.q50).values; e = past.y.values - past.q50.values
                loss = [np.mean(np.maximum(q * (e - k * off), (q - 1) * (e - k * off))) for k in KS]
                k = KS[int(np.argmin(loss))]
                f.loc[cur, col + "_cal"] = f.loc[cur, "q50"] + k * (f.loc[cur, col] - f.loc[cur, "q50"])
    for col in ("q10", "q90"):
        f[col] = f[col + "_cal"].fillna(f[col])

f = f[(f.origin_date >= t0) & (f.origin_date <= t1)]
f[["q10", "q50", "q90"]] = f[["q10", "q50", "q90"]].round(6)
f[["series_id", "origin_date", "horizon_days", "q10", "q50", "q90", "n_windows"]].to_csv(a.out, index=False)
print(f"wrote {len(f)} rows, {f.series_id.nunique()} series, {f.origin_date.nunique()} origins -> {a.out}")
