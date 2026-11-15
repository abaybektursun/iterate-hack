"""TabPFN-TS method with open weights, run locally: quantile forecasts for the gpuprice development origins.

uv run tools/gpu.py submit cpu --hours 0.6 -- 'bash studies/gpuprice/jobs/tab_pfn.sh --origin-start 2026-10-01 --origin-end 2026-10-06'
Package `tabpfn` 10.0.0 (Apache-2.0), weights Prior-Labs/TabPFN-v2-reg `tabpfn-v2-regressor.ckpt` (Prior Labs
License 1.1 = Apache 2.0 plus an attribution clause, not gated; "Built with PriorLabs-TabPFN"). The later models
(v2.5 to v3.5, the default of the package `tabpfn-time-series`) are gated and non-commercial, and that package's
default engine is a hosted API, so neither is used: the method (Hoo et al., arXiv 2501.02945: a time series as a
regression table of time features -> value) is written out here on TabPFNRegressor. No row leaves the job.
Reads studies/gpuprice/data/fm_panel_v1.csv (no row after 2026-10-30), writes $OUT_DIR/tab_pfn.csv in the layout
of fm_chronos2.py (setup, series_id, listing, origin_date, horizon_days, one column per quantile level), which
studies/gpuprice/jobs/fm_post.py turns into forecasts. Setups:
  alone      each of the 37 series: observed days as rows, features running day index, year and the sin/cos of
             day of week, of month, of year, week of year, month (the package's RunningIndexFeature and
             CalendarFeature; its AutoSeasonalFeature is left out), target the price
  lst_alone  the same per listing present on the last observed day of its series
  lst_feat   per listing and horizon h, one row per observed day d: target price(d) - price(d - h); features known
             at d - h: price, days since the listing's last price change, price / series median; plus the running
             day index and day of week of d. Forecast = last price + predicted change.
A target with one distinct value is not sent to the model: the forecast is that value (TabPFNRegressor.fit does
the same, `is_constant_target_`). The number of such cases is printed.
"""
import argparse, os, time
import numpy as np, pandas as pd
from tabpfn import TabPFNRegressor
from tabpfn.constants import ModelVersion

ap = argparse.ArgumentParser()
ap.add_argument("--panel", default="studies/gpuprice/data/fm_panel_v1.csv")
ap.add_argument("--origin-start", default="2026-10-01"); ap.add_argument("--origin-end", default="2026-10-30")
ap.add_argument("--setups", default="alone,lst_alone,lst_feat")
a = ap.parse_args()
assert a.origin_end <= "2026-10-30", "origins after 2026-10-30 are the locked test set"
HORIZONS = (1, 3, 7)
Q = [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
SETUPS = a.setups.split(",")

panel = pd.read_csv(a.panel, keep_default_na=False)
panel["d"] = pd.to_datetime(panel.d); panel["p"] = panel.p.astype(float)
assert panel.d.max() <= pd.Timestamp("2026-10-30")
wide = {s: g.pivot(index="d", columns="listing", values="p").asfreq("D") for s, g in panel.groupby("series_id")}
assert len(wide) == 37

n = {"fit": 0, "constant": 0}
def predict(X, y, Xt):
    """Quantiles (len(Xt), len(Q)) of the target at the rows Xt, from the table (X, y)."""
    if len(np.unique(y)) == 1:
        n["constant"] += 1
        return np.full((len(Xt), len(Q)), y[0])
    n["fit"] += 1
    m = TabPFNRegressor.create_default_for_version(ModelVersion.V2).fit(X, y)
    q = np.stack(m.predict(Xt, output_type="quantiles", quantiles=Q), 1)
    assert q.shape == (len(Xt), len(Q)) and np.isfinite(q).all()
    return q

def cal(days, d0):
    """The package's running index and calendar features for daily data."""
    c = [(days - d0).days, days.year]
    for v, period in ((days.dayofweek, 7), (days.day - 1, 30.5), (days.dayofyear - 1, 365),
                      (days.isocalendar().week.values.astype(int) - 1, 52), (days.month - 1, 12)):
        c += [np.sin(2 * np.pi * v / (period - 1)), np.cos(2 * np.pi * v / (period - 1))]
    return np.column_stack(c).astype(float)

def plain(x, t):
    """x: prices on a daily grid that ends on or before the origin t. -> {h: quantiles of the price at t + h}"""
    o = x.dropna()
    q = predict(cal(o.index, o.index[0]), o.values, cal(pd.DatetimeIndex([t + pd.Timedelta(days=h) for h in HORIZONS]), o.index[0]))
    return dict(zip(HORIZONS, q))

def feat(x, med, t):
    """x: a listing's prices, med: its series' values, both on the same daily grid that ends at t."""
    f = x.ffill().values; obs = x.notna().values; r = f / med.ffill().values
    i = np.arange(len(f)); dow = x.index.dayofweek.values
    changed = np.r_[False, (f[1:] != f[:-1]) & np.isfinite(f[1:]) & np.isfinite(f[:-1])]
    first = np.flatnonzero(obs)[0]
    since = i - np.maximum.accumulate(np.where(changed, i, first))   # days since the last change (or the first row)
    out = {}
    for h in HORIZONS:
        d = np.flatnonzero(obs & (i - h >= first))
        col = lambda day, b, w: np.column_stack([day, np.sin(2 * np.pi * w / 7), np.cos(2 * np.pi * w / 7), f[b], since[b], r[b]])
        Xt = col(np.array([i[-1] + h]), np.array([i[-1]]), np.array([(dow[-1] + h) % 7]))
        if len(d) == 0:
            n["constant"] += 1; out[h] = np.full(len(Q), f[-1])  # no h-day pair yet: no change is the only value
        else:
            out[h] = f[-1] + predict(col(d, d - h, dow[d]), f[d] - f[d - h], Xt)[0]
    return out

rows, t0 = [], time.time()
for t in pd.date_range(a.origin_start, a.origin_end):
    ctx = {s: w.loc[:t] for s, w in wide.items()}       # rule 1: nothing after the origin
    for s in sorted(ctx):
        res = []
        if "alone" in SETUPS:
            res.append(("alone", "", plain(ctx[s][""], t)))
        w = ctx[s].drop(columns="")
        if w.shape[1]:                                   # afhubbard: series level only
            w = w.loc[:, w.loc[:w.dropna(how="all").index[-1]].iloc[-1].notna()]   # listings present on the last observed day
            for c in w.columns:
                if "lst_alone" in SETUPS:
                    res.append(("lst_alone", c, plain(w[c], t)))
                if "lst_feat" in SETUPS:
                    res.append(("lst_feat", c, feat(w[c], ctx[s][""], t)))
        rows += [(k, s, c, t.date().isoformat(), h, *q[h]) for k, c, q in res for h in HORIZONS]
    print(t.date(), len(rows), "rows", n, round(time.time() - t0), "s", flush=True)

out = pd.DataFrame(rows, columns=["setup", "series_id", "listing", "origin_date", "horizon_days"] + [f"q{q:g}" for q in Q])
out.to_csv(os.path.join(os.environ["OUT_DIR"], "tab_pfn.csv"), index=False, float_format="%.6g")
print("wrote", len(out), "rows", out.groupby("setup").size().to_dict(), n)
