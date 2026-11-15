"""Chronos-2 (amazon/chronos-2, Apache-2.0) quantile forecasts for the gpuprice development origins. GPU job.

uv run tools/gpu.py submit h100 --hours 0.3 -- 'bash studies/gpuprice/jobs/fm_chronos2.sh'
Reads studies/gpuprice/data/fm_panel_v1.csv (no row after 2026-10-30) and writes $OUT_DIR/fm_chronos2.csv:
setup, series_id, listing, origin_date, horizon_days, then one column per native quantile level of the model.
Each context is a daily calendar grid that ends at the origin; a day without a row is NaN. Setups:
  alone      each of the 37 series by itself
  group      the 37 series in one group (cross_learning=True)
  cov        a series with, as a past covariate, the other collector's series of the same GPU model and tier
  lst_alone  each listing present on the last observed day, by itself
  lst_group  the listings of one series as one multivariate target (they share a group)
studies/gpuprice/jobs/fm_post.py turns this file into forecasts on the laptop (no model there).
"""
import argparse, os, time
import numpy as np, pandas as pd, torch
from chronos import Chronos2Pipeline

ap = argparse.ArgumentParser()
ap.add_argument("--panel", default="studies/gpuprice/data/fm_panel_v1.csv")
ap.add_argument("--series", default="studies/gpuprice/data/event_series_v1.csv")
ap.add_argument("--origin-start", default="2026-10-01"); ap.add_argument("--origin-end", default="2026-10-30")
a = ap.parse_args()
assert a.origin_end <= "2026-10-30", "origins after 2026-10-30 are the locked test set"
HORIZONS = (1, 3, 7)

pipe = Chronos2Pipeline.from_pretrained("amazon/chronos-2", device_map="cuda")
Q = [float(q) for q in pipe.quantiles]
print("native quantiles", Q, flush=True)

panel = pd.read_csv(a.panel, keep_default_na=False)
panel["d"] = pd.to_datetime(panel.d); panel["p"] = panel.p.astype(float)
assert panel.d.max() <= pd.Timestamp("2026-10-30")
ev = pd.read_csv(a.series)
# one frame per series: calendar days x listings ('' = the series value), NaN where there is no row
wide = {s: g.pivot(index="d", columns="listing", values="p").asfreq("D") for s, g in panel.groupby("series_id")}
assert len(wide) == 37
other = {}  # series -> the other collector's series of the same GPU model and tier (first by name)
for r in ev.itertuples():
    c = ev[(ev.gpu_model == r.gpu_model) & (ev.pricing_tier == r.pricing_tier) & (ev.source_id != r.source_id)]
    if len(c):
        other[r.series_id] = sorted(c.series_id)[0]
print(len(other), "series have a counterpart", flush=True)

rows = []
def run(setup, keys, inputs, **kw):
    """keys: per input, a list of (series_id, listing), one per variate."""
    qs, _ = pipe.predict_quantiles(inputs, prediction_length=max(HORIZONS), quantile_levels=Q, **kw)
    assert len(qs) == len(keys)
    for k, q in zip(keys, qs):
        q = q.float().cpu().numpy()                      # (n_variates, prediction_length, len(Q))
        assert q.shape == (len(k), max(HORIZONS), len(Q)) and np.isfinite(q).all()
        for (sid, lst), qv in zip(k, q):
            for h in HORIZONS:
                rows.append((setup, sid, lst, t.date().isoformat(), h, *qv[h - 1]))

t0 = time.time()
for t in pd.date_range(a.origin_start, a.origin_end):
    ctx = {s: w.loc[:t] for s, w in wide.items()}       # rule 1: nothing after the origin
    sids = sorted(ctx)
    ser = [ctx[s][""].values for s in sids]
    assert all(np.isfinite(x).sum() >= 10 for x in ser)
    run("alone", [[(s, "")] for s in sids], ser, batch_size=256)
    run("group", [[(s, "")] for s in sids], ser, batch_size=256, cross_learning=True)
    cs = [s for s in sids if s in other]
    cov = [{"target": ctx[s][""].values,
            "past_covariates": {"other": ctx[other[s]][""].reindex(ctx[s].index).values}} for s in cs]
    run("cov", [[(s, "")] for s in cs], cov, batch_size=256)
    la_keys, la_in = [], []
    for s in sids:
        w = ctx[s].drop(columns="")
        if w.shape[1] == 0:
            continue                                     # afhubbard: series level only
        w = w.loc[:w.dropna(how="all").index[-1]]       # ends at the last observed day
        w = w.loc[:, w.iloc[-1].notna()]                 # listings present on that day
        ks = [(s, c) for c in w.columns]
        run("lst_group", [ks], [w.values.T], batch_size=256)
        la_keys += [[k] for k in ks]; la_in += [w[c].values for c in w.columns]
    run("lst_alone", la_keys, la_in, batch_size=256)
    print(t.date(), len(rows), "rows", round(time.time() - t0), "s", flush=True)

out = pd.DataFrame(rows, columns=["setup", "series_id", "listing", "origin_date", "horizon_days"] + [f"q{q:g}" for q in Q])
out.to_csv(os.path.join(os.environ["OUT_DIR"], "fm_chronos2.csv"), index=False, float_format="%.6g")
print("wrote", len(out), "rows", out.groupby("setup").size().to_dict())
