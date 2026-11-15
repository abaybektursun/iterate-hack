"""TiRex-2 (NX-AI/TiRex-2, Apache-2.0) quantile forecasts for the gpuprice development origins. GPU job.

uv run tools/gpu.py submit h100 --hours 0.3 -- 'pip install -q tirex-2 && python studies/gpuprice/jobs/fm_tirex2.py'
Same input, contexts and output file layout as fm_chronos2.py ($OUT_DIR/fm_tirex2.csv), with the model's 9
quantile levels 0.1 .. 0.9. Setups: alone (each series), lst_alone (each listing present on the last observed
day), lst_group (the listings of one series as one multivariate target).
"""
import argparse, os, time
import numpy as np, pandas as pd, torch
from tirex2 import TimeseriesType, load_model

ap = argparse.ArgumentParser()
ap.add_argument("--panel", default="studies/gpuprice/data/fm_panel_v1.csv")
ap.add_argument("--origin-start", default="2026-10-01"); ap.add_argument("--origin-end", default="2026-10-30")
a = ap.parse_args()
assert a.origin_end <= "2026-10-30", "origins after 2026-10-30 are the locked test set"
HORIZONS = (1, 3, 7)

model = load_model("NX-AI/TiRex-2", device="cuda")
Q = [round(float(q), 6) for q in model.quantiles]
print("quantiles", Q, flush=True)
assert Q == [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

panel = pd.read_csv(a.panel, keep_default_na=False)
panel["d"] = pd.to_datetime(panel.d); panel["p"] = panel.p.astype(float)
assert panel.d.max() <= pd.Timestamp("2026-10-30")
wide = {s: g.pivot(index="d", columns="listing", values="p").asfreq("D") for s, g in panel.groupby("series_id")}
assert len(wide) == 37

rows = []
def run(setup, keys, arrays):
    """arrays: per input, (n_variates, history); keys: per input, a list of (series_id, listing) per variate."""
    ts = [TimeseriesType(target=torch.tensor(x, dtype=torch.float32), past_covariates=None, future_covariates=None) for x in arrays]
    out = model.forecast(ts, prediction_length=max(HORIZONS), output_type="numpy")
    assert len(out) == len(keys)
    for k, q in zip(keys, out):                          # (n_variates, 9, prediction_length)
        assert q.shape == (len(k), len(Q), max(HORIZONS)) and np.isfinite(q).all()
        for (sid, lst), qv in zip(k, q):
            for h in HORIZONS:
                rows.append((setup, sid, lst, t.date().isoformat(), h, *qv[:, h - 1]))

t0 = time.time()
for t in pd.date_range(a.origin_start, a.origin_end):
    ctx = {s: w.loc[:t] for s, w in wide.items()}       # rule 1: nothing after the origin
    sids = sorted(ctx)
    run("alone", [[(s, "")] for s in sids], [ctx[s][[""]].values.T for s in sids])
    la_keys, la_in, lg_keys, lg_in = [], [], [], []
    for s in sids:
        w = ctx[s].drop(columns="")
        if w.shape[1] == 0:
            continue                                     # afhubbard: series level only
        w = w.loc[:w.dropna(how="all").index[-1]]       # ends at the last observed day
        w = w.loc[:, w.iloc[-1].notna()]                 # listings present on that day
        ks = [(s, c) for c in w.columns]
        lg_keys.append(ks); lg_in.append(w.values.T)
        la_keys += [[k] for k in ks]; la_in += [w[[c]].values.T for c in w.columns]
    run("lst_group", lg_keys, lg_in)
    run("lst_alone", la_keys, la_in)
    print(t.date(), len(rows), "rows", round(time.time() - t0), "s", flush=True)

out = pd.DataFrame(rows, columns=["setup", "series_id", "listing", "origin_date", "horizon_days"] + [f"q{q:g}" for q in Q])
out.to_csv(os.path.join(os.environ["OUT_DIR"], "fm_tirex2.csv"), index=False, float_format="%.6g")
print("wrote", len(out), "rows", out.groupby("setup").size().to_dict())
