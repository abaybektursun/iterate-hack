"""Fine-tunes Chronos-2 (amazon/chronos-2, Apache-2.0) on listing-level price series and forecasts the development
origins in the fm-07 setup. GPU job, see ft_chronos2.sh.

Training data: studies/gpuprice/data/ft_panel_<cutoff>.parquet (ft_panel.py: every listing of every collector, no
row after --cutoff), optionally with synthetic sticky-price series. --cutoff must be before the first origin, so
the fine-tuned weights have seen no price of a forecast origin or target (development: 2026-09-30; the event
forecast would use 2026-11-06 with a panel built to that day).
Validation (--val-days 14): training series end at cutoff - 14 days; the validation windows are the last 7 days
before the cutoff and the 7 days before those, on the fastgpu_daily and gpurentalprices listings; the checkpoint
with the lowest validation loss is kept (early stopping after --patience evaluations without improvement).
--val-days 0 trains on everything up to the cutoff for exactly --steps steps.
Forecasts: every --curve-every steps (0 = zero-shot weights) and for the final weights, the same contexts as
fm_chronos2.py setups `alone` (37 series) and `lst_alone` (each listing present on the last observed day), written
as $OUT_DIR/ft_q_<step|final>.csv in the format fm_post.py reads. $OUT_DIR/ft_log.json holds the trainer's log.
"""
import argparse, json, os, time
import numpy as np, pandas as pd, torch
from chronos import Chronos2Pipeline
from transformers import EarlyStoppingCallback, TrainerCallback

ap = argparse.ArgumentParser()
ap.add_argument("--mode", required=True, choices=["none", "lora", "full"])
ap.add_argument("--cutoff", default="2026-09-30")
ap.add_argument("--ft-panel", default=None, help="default studies/gpuprice/data/ft_panel_<cutoff>.parquet")
ap.add_argument("--steps", type=int, default=1000); ap.add_argument("--lr", type=float, default=None)
ap.add_argument("--batch", type=int, default=256); ap.add_argument("--val-days", type=int, default=14, choices=[0, 7, 14])
ap.add_argument("--patience", type=int, default=5); ap.add_argument("--curve-every", type=int, default=100)
ap.add_argument("--synthetic", type=int, default=0, help="number of synthetic sticky-price series added")
ap.add_argument("--real", type=int, default=1, help="0 = train on synthetic series only")
ap.add_argument("--small-share", type=float, default=0.33,
                help="share of the real training series that are not afhubbard, reached by repeating them")
ap.add_argument("--panel", default="studies/gpuprice/data/fm_panel_v1.csv")
ap.add_argument("--origin-start", default="2026-10-01"); ap.add_argument("--origin-end", default="2026-10-30")
ap.add_argument("--seed", type=int, default=0)
a = ap.parse_args()
assert a.origin_end <= "2026-10-30", "origins after 2026-10-30 are the locked test set"
assert a.cutoff < a.origin_start, "the fine-tuning data must end before the first forecast origin"
OUT = os.environ["OUT_DIR"]
HORIZONS = (1, 3, 7); H = max(HORIZONS); MIN_PAST = 14; MIN_LEN = MIN_PAST + H
rng = np.random.default_rng(a.seed)

# ---- forecast contexts: the same as fm_chronos2.py `alone` and `lst_alone` -------------------------------------
panel = pd.read_csv(a.panel, keep_default_na=False)
panel["d"] = pd.to_datetime(panel.d); panel["p"] = panel.p.astype(float)
assert panel.d.max() <= pd.Timestamp("2026-10-30")
wide = {s: g.pivot(index="d", columns="listing", values="p").asfreq("D") for s, g in panel.groupby("series_id")}
assert len(wide) == 37
keys, ctxs = [], []
for t in pd.date_range(a.origin_start, a.origin_end):
    for s in sorted(wide):
        w = wide[s].loc[:t]                                   # nothing after the origin
        assert np.isfinite(w[""].values).sum() >= 10
        keys.append(("alone", s, "", t.date().isoformat())); ctxs.append(w[""].values)
        w = w.drop(columns="")
        if w.shape[1] == 0:
            continue                                          # afhubbard: series level only
        w = w.loc[:w.dropna(how="all").index[-1]]             # ends at the last observed day
        for c in w.columns[w.iloc[-1].notna()]:               # listings present on that day
            keys.append(("lst_alone", s, c, t.date().isoformat())); ctxs.append(w[c].values)
print(len(ctxs), "forecast contexts", flush=True)

def forecast(model, tag):
    pipe = Chronos2Pipeline(model=model)
    Q = [float(q) for q in pipe.quantiles]
    was_training = model.training
    model.eval()
    qs, _ = pipe.predict_quantiles(ctxs, prediction_length=H, quantile_levels=Q, batch_size=1024)
    model.train(was_training)
    assert len(qs) == len(keys)
    rows = []
    for k, q in zip(keys, qs):
        q = q.float().cpu().numpy()
        assert q.shape == (1, H, len(Q)) and np.isfinite(q).all()
        rows += [(*k, h, *q[0, h - 1]) for h in HORIZONS]
    out = pd.DataFrame(rows, columns=["setup", "series_id", "listing", "origin_date", "horizon_days"] + [f"q{q:g}" for q in Q])
    out.to_csv(os.path.join(OUT, f"ft_q_{tag}.csv"), index=False, float_format="%.6g")
    print("forecast", tag, len(out), "rows", flush=True)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"        # the cpu job class works for small settings
print("device", DEVICE, flush=True)
pipe = Chronos2Pipeline.from_pretrained("amazon/chronos-2", device_map=DEVICE)
forecast(pipe.model, 0)
if a.mode == "none":
    raise SystemExit(0)

# ---- training series -------------------------------------------------------------------------------------------
def segments(g, end):
    """Daily grids (NaN = no row) of one listing up to `end`, split where more than 7 days are missing."""
    g = g[g.d <= end]
    s = g.set_index("d").p
    cut = [0, *(np.flatnonzero(np.diff(s.index.values) > np.timedelta64(7, "D")) + 1), len(s)]
    return [s.iloc[i:j].asfreq("D").values.astype(np.float32) for i, j in zip(cut, cut[1:]) if j > i]

def synthetic(n):
    """Sticky posted prices: a step function with a change rate per series between 0.003 and 1 per day and
    two-sided jumps with little mass near zero; 15 % of the series move every day (random walk in logs)."""
    out = []
    for _ in range(n):
        T = int(rng.integers(40, 260)); p0 = np.exp(rng.normal(0.5, 1.0))
        if rng.random() < 0.15:
            step = rng.normal(0, 10 ** rng.uniform(-2.5, -1), T)
        else:
            change = rng.random(T) < 10 ** rng.uniform(-2.5, 0)
            sign = np.where(rng.random(T) < rng.uniform(0.2, 0.8), -1.0, 1.0)
            step = change * sign * (0.3 + rng.exponential(1.0, T)) * 10 ** rng.uniform(-2, -0.7)
        x = np.round(p0 * np.exp(np.cumsum(step)), int(rng.choice([2, 4]))).astype(np.float32)
        x[rng.random(T) < rng.choice([0.0, 0.05])] = np.nan
        out.append(np.maximum(x, 0.01))
    return out

cutoff = pd.Timestamp(a.cutoff); train_end = cutoff - pd.Timedelta(days=a.val_days)
train, val = [], []
if a.real:
    ft = pd.read_parquet(a.ft_panel or f"studies/gpuprice/data/ft_panel_{a.cutoff}.parquet")
    ft["d"] = pd.to_datetime(ft.d)
    assert ft.d.max() <= cutoff, "the fine-tuning panel has rows after the cutoff"
    big, small = [], []
    for (src, _), g in ft.groupby(["source_id", "listing"], sort=True):
        (big if src == "afhubbard" else small).extend(x for x in segments(g, train_end) if len(x) >= MIN_LEN)
        if src in ("fastgpu_daily", "gpurentalprices"):
            for k in range(a.val_days // 7):                 # windows ending at the cutoff and 7 days earlier
                end = cutoff - pd.Timedelta(days=7 * k)
                x = segments(g, end)
                if x and g.d[g.d <= end].max() == end and len(x[-1]) >= MIN_LEN:
                    val.append(x[-1])
    rep = max(1, round(a.small_share / (1 - a.small_share) * len(big) / len(small)))
    train = big + small * rep
    print(f"real training series: afhubbard {len(big)}, other collectors {len(small)} x {rep}; "
          f"days {sum(map(len, big)) + sum(map(len, small))}; ends {train_end.date()}; validation windows {len(val)}", flush=True)
if a.synthetic:
    train += synthetic(a.synthetic)
    print("synthetic series:", a.synthetic, flush=True)
assert train

# ---- fine-tune -------------------------------------------------------------------------------------------------
log = []
class Curve(TrainerCallback):
    def on_step_end(self, args, state, control, model=None, **kw):
        if a.curve_every and state.global_step % a.curve_every == 0 and state.global_step < a.steps:
            forecast(model, state.global_step)
    def on_log(self, args, state, control, logs=None, **kw):
        log.append({"step": state.global_step, **logs}); print(log[-1], flush=True)

lr = a.lr or {"lora": 1e-4, "full": 1e-5}[a.mode]          # the values of the package's quickstart notebook
kw = dict(eval_steps=a.curve_every, save_steps=a.curve_every, save_total_limit=2) if val else {}
t0 = time.time()
tuned = pipe.fit(train, prediction_length=H, validation_inputs=val or None, finetune_mode=a.mode, learning_rate=lr,
                 num_steps=a.steps, batch_size=a.batch, min_past=MIN_PAST, output_dir="/tmp/ft_chronos2",
                 callbacks=[Curve()] + ([EarlyStoppingCallback(early_stopping_patience=a.patience)] if val else []),
                 logging_steps=min(50, a.steps), seed=a.seed, **kw)
print("fine-tuning took", round(time.time() - t0), "s", flush=True)
if a.mode == "lora":
    assert type(tuned.model).__name__.startswith("Peft"), "peft missing: fit fell back to full fine-tuning"
forecast(tuned.model, "final")
json.dump({"args": vars(a), "lr": lr, "train_series": len(train), "validation_windows": len(val),
           "train_seconds": round(time.time() - t0), "log": log}, open(os.path.join(OUT, "ft_log.json"), "w"), indent=1)
