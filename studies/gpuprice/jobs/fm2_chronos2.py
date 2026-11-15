"""Round 2: Chronos-2 (amazon/chronos-2, Apache-2.0) quantile functions per listing, zero-shot. GPU job.

uv run tools/gpu.py submit h100 --hours 0.5 -- 'bash studies/gpuprice/jobs/fm2_chronos2.sh --origins dev,event'
(the class cpu also works, on Modal, when the GPU queues are full: about 10 times slower)
Reads studies/gpuprice/data/fm2_panel_v2.csv.gz and, for origin t, only its rows dated on or before t.
Writes $OUT_DIR/fm2_chronos2.csv: setup, series_id, unit, origin_date, horizon_days, one column per native quantile level.
Every unit is forecast alone (round 1: group attention added nothing). The context is a daily calendar grid that
ends at the unit's series' last observed day on or before t; a day without a row is NaN. Setups:
  ser, ser_long   the 37 series values; _long adds the 30 extra days of prep/ext_history.py
  lst, lst_long   each listing (provider|region|sku) of the fastgpu_daily and gpurentalprices series that is present
                  on the last observed day (lst = round 1's lst_alone)
  chn, chn_long   the same with chains (a listing identity that survives a key change, see fm2_panel.py)
  chn_cov         chn_long with a past covariate: observed days since the unit's price last changed
  afh             each listing of the 4 afhubbard series
studies/gpuprice/jobs/fm2_post.py turns this file into forecasts on the laptop (no model there).
"""
import argparse, os, sys, time
import numpy as np, pandas as pd, torch
from chronos import Chronos2Pipeline
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fm2_lib

ap = argparse.ArgumentParser()
ap.add_argument("--panel", default="studies/gpuprice/data/fm2_panel_v2.csv.gz")
ap.add_argument("--origins", default="dev,event")
ap.add_argument("--max-context", type=int, default=400)
ap.add_argument("--setups", default="ser,ser_long,lst,lst_long,chn,chn_long,chn_cov,afh")
ap.add_argument("--model", default="amazon/chronos-2", help="or a folder saved by ft_chronos2.py --save")
a = ap.parse_args()
ORIG = fm2_lib.origins(a.origins)
H = fm2_lib.HORIZONS

pipe = Chronos2Pipeline.from_pretrained(a.model, device_map="cuda" if torch.cuda.is_available() else "cpu")
Q = [float(q) for q in pipe.quantiles]
print("native quantiles", Q, flush=True)

rows = fm2_lib.load(a.panel)
afh = rows.series_id.str.startswith("afhubbard.")
W = {"ser": fm2_lib.wide(rows[rows.listing == ""], "listing", False), "ser_long": fm2_lib.wide(rows[rows.listing == ""], "listing", True),
     "lst": fm2_lib.wide(rows[(rows.listing != "") & ~afh], "listing", False), "lst_long": fm2_lib.wide(rows[(rows.listing != "") & ~afh], "listing", True),
     "chn": fm2_lib.wide(rows[(rows.listing != "") & ~afh], "chain", False), "chn_long": fm2_lib.wide(rows[(rows.listing != "") & ~afh], "chain", True),
     "afh": fm2_lib.wide(rows[(rows.listing != "") & afh], "listing", False)}
W["chn_cov"] = W["chn_long"]
W = {k: W[k] for k in a.setups.split(",")}


def since_change(x):
    """Observed days since the price last changed (0 on the day of a change or of the first row); NaN where x is NaN."""
    out = np.full(len(x), np.nan); n, prev = 0, np.nan
    for i, v in enumerate(x):
        if np.isfinite(v):
            n = n + 1 if v == prev else 0
            out[i] = n; prev = v
    return out


out = []
t0 = time.time()
for o in ORIG:
    t = pd.Timestamp(o)
    for setup, ws in W.items():
        keys, inputs = [], []
        for s, w in ws.items():
            w = w.loc[:t]                                    # rule 1: nothing after the origin
            w = w.loc[:w.dropna(how="all").index[-1]]       # ends at the last observed day
            w = w.loc[:, w.iloc[-1].notna()].iloc[-a.max_context:]   # units present on that day
            for c in w.columns:
                x = w[c].values
                keys.append((s, c))
                inputs.append({"target": x, "past_covariates": {"since": since_change(x)}} if setup == "chn_cov" else x)
        qs, _ = pipe.predict_quantiles(inputs, prediction_length=max(H), quantile_levels=Q, batch_size=512)
        assert len(qs) == len(keys)
        for (s, c), q in zip(keys, qs):
            q = q.float().cpu().numpy()
            assert q.shape == (1, max(H), len(Q)) and np.isfinite(q).all()
            for h in H:
                out.append((setup, s, c, o, h, *q[0, h - 1]))
    print(o, len(out), "rows", round(time.time() - t0), "s", flush=True)

out = pd.DataFrame(out, columns=["setup", "series_id", "unit", "origin_date", "horizon_days"] + [f"q{q:g}" for q in Q])
out.to_csv(os.path.join(os.environ["OUT_DIR"], "fm2_chronos2.csv"), index=False, float_format="%.6g")
print("wrote", len(out), "rows", out.groupby("setup").size().to_dict())
