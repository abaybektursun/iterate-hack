"""Turns the quantile file of a foundation-model job into forecast files, one per variant. Laptop, no model.

runs/gpuprice/.venv/bin/python -I -B studies/gpuprice/jobs/fm_post.py --quantiles runs/<job-id>/fm_chronos2.csv \
    --panel studies/gpuprice/data/fm_panel_v1.csv --out-dir runs/gpuprice/fm/<tag>
Variants (each <out-dir>/<variant>.csv, columns series_id, origin_date, horizon_days, q10, q50, q90):
  alone, group, cov          the model's q10/q50/q90 of the series (cov: series without a counterpart use alone)
  spread_<setup>             q50 = last value; q10, q90 = last value + the model's (q10 - q50), (q90 - q50)
  sim_<lst setup>_<indep|shared>[_c]
        each listing's quantile function is read at a uniform draw (indep: one draw per listing; shared: one per
        simulation), the median over listings is taken per simulation, and q10/q50/q90 are read from 2,000
        simulations. _c: each listing's function is first shifted so that its median is its last price.
        Only listings present on the last observed day; the 4 afhubbard series use alone.
"""
import argparse, os
import numpy as np, pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--quantiles", required=True); ap.add_argument("--panel", required=True)
ap.add_argument("--out-dir", required=True); ap.add_argument("--draws", type=int, default=2000)
a = ap.parse_args()
os.makedirs(a.out_dir, exist_ok=True)
KEY = ["series_id", "origin_date", "horizon_days"]

f = pd.read_csv(a.quantiles, keep_default_na=False)
qcols = [c for c in f.columns if c.startswith("q")]
L = np.array([float(c[1:]) for c in qcols])
f[qcols] = np.sort(f[qcols].values.astype(float), axis=1)      # a quantile function must not decrease
panel = pd.read_csv(a.panel, keep_default_na=False).rename(columns={"d": "t", "p": "last"})
panel["t"] = pd.to_datetime(panel.t); panel = panel.sort_values("t")

def last(df):  # last price on or before each origin, per (series, listing)
    o = df[KEY[:2] + ["listing"]].drop_duplicates()
    o = o.assign(t=pd.to_datetime(o.origin_date)).sort_values("t")
    m = pd.merge_asof(o, panel, on="t", by=["series_id", "listing"]).drop(columns="t")
    assert m["last"].notna().all()
    return df.merge(m, on=KEY[:2] + ["listing"])

def write(name, df):
    df = df[KEY + ["q10", "q50", "q90"]].round(6)
    assert not df.duplicated(KEY).any() and (df.q10 <= df.q50).all() and (df.q50 <= df.q90).all()
    df.to_csv(f"{a.out_dir}/{name}.csv", index=False); print(name, len(df), "rows")

ser = {s: g.rename(columns={"q0.1": "q10", "q0.5": "q50", "q0.9": "q90"}) for s, g in f[f.listing == ""].groupby("setup")}
if "cov" in ser:
    rest = ser["alone"].merge(ser["cov"][KEY], on=KEY, how="left", indicator=True)
    ser["cov"] = pd.concat([ser["cov"], rest[rest._merge == "left_only"]])
for s, g in ser.items():
    write(s, g)
    g = last(g)
    write(f"spread_{s}", g.assign(q10=g["last"] + g.q10 - g.q50, q90=g["last"] + g.q90 - g.q50, q50=g["last"]))

rng = np.random.default_rng(0)
afh = ser["alone"][ser["alone"].series_id.str.startswith("afhubbard.")]
for s, g in f[f.listing != ""].groupby("setup"):
    g = last(g)
    out = {k: [] for k in ("indep", "shared", "indep_c", "shared_c")}
    for key, x in g.groupby(KEY):
        qf = x[qcols].values                                       # (listings, levels)
        n = len(qf)
        shift = (x["last"].values - np.array([np.interp(0.5, L, r) for r in qf]))[:, None]
        for dep in ("indep", "shared"):
            u = rng.uniform(size=(n, a.draws)) if dep == "indep" else np.repeat(rng.uniform(size=(1, a.draws)), n, 0)
            draws = np.stack([np.interp(u[i], L, qf[i]) for i in range(n)])   # constant outside [0.01, 0.99]
            out[dep].append((*key, *np.quantile(np.median(draws, 0), [0.1, 0.5, 0.9])))
            out[dep + "_c"].append((*key, *np.quantile(np.median(draws + shift, 0), [0.1, 0.5, 0.9])))
    for k, r in out.items():
        write(f"sim_{s}_{k}", pd.concat([pd.DataFrame(r, columns=KEY + ["q10", "q50", "q90"]), afh]))
