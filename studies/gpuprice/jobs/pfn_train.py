"""Prior-data fitted network for one listing's price: trained ONLY on the synthetic listings of pfn_sim.py, then
applied zero-shot to the real listings. Modal job (cpu class or a GPU); the laptop never runs it.

uv run tools/gpu.py submit cpu --hours 1 -- 'python studies/gpuprice/jobs/pfn_train.py --steps 4000'
Options: --weights "rw=0,ou=0,smooth=0" (prior ablations: a type's weight in pfn_sim.WEIGHTS), --prior-width,
--width, --layers, --batch, --seed, --ckpts (fractions of --steps at which the real listings are forecast),
--load <model.pt> (no training), --panel/--origin-start/--origin-end/--final (the event origin).

Input: the 60 days that end at the origin, log price relative to the last observed price, a mask for missing days.
Output: 21 quantile levels (0.01, 0.05 ... 0.95, 0.99) of the log change from the last observed price to the days
1, 3, 7 after the origin, trained with pinball loss on asinh(1000 * log change) (a monotone map, so quantiles are
kept, and a 0.2 % mover weighs as much as a 10 % mover).

Writes to $OUT_DIR:
  pfn_q_s<step>.csv   same columns as fm_chronos2.csv (setup alone = the 37 series themselves, lst_alone = each
                      listing present on the series' last observed day), for studies/gpuprice/jobs/fm_post.py
  sanity.json         per checkpoint and prior type, on 4,000 fresh synthetic series each: pinball loss (q10, q50,
                      q90, log units) of the network and of flat last value, and the skill
  train.json, model.pt
"""
import argparse, json, math, os, sys, time
import numpy as np, pandas as pd, torch, torch.nn as nn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pfn_sim as S

ap = argparse.ArgumentParser()
ap.add_argument("--steps", type=int, default=4000); ap.add_argument("--batch", type=int, default=256)
ap.add_argument("--width", type=int, default=192); ap.add_argument("--layers", type=int, default=4)
ap.add_argument("--lr", type=float, default=1e-3); ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--weights", default=""); ap.add_argument("--prior-width", type=float, default=1.0)
ap.add_argument("--ckpts", default="0.125,0.25,0.5,1"); ap.add_argument("--load")
ap.add_argument("--panel", default="studies/gpuprice/data/fm_panel_v1.csv")
ap.add_argument("--origin-start", default="2026-10-01"); ap.add_argument("--origin-end", default="2026-10-30")
ap.add_argument("--final", action="store_true", help="allow origins after 2026-10-30 (the event forecast only)")
a = ap.parse_args()
assert a.final or a.origin_end <= "2026-10-30", "origins after 2026-10-30 are the locked test set"
OUT = os.environ["OUT_DIR"]
dev = "cuda" if torch.cuda.is_available() else "cpu"
torch.manual_seed(a.seed)
W = dict(S.WEIGHTS)
for kv in filter(None, a.weights.split(",")):
    k, v = kv.split("="); assert k in W, k; W[k] = float(v)
Q = [0.01] + [round(i / 20, 2) for i in range(1, 20)] + [0.99]
QT = torch.tensor(Q, device=dev)
H = S.HORIZONS


class Net(nn.Module):
    def __init__(s, d, layers):
        super().__init__()
        s.inp = nn.Linear(6, d)
        s.pos = nn.Parameter(torch.randn(S.CTX + 1, d) * .02)
        s.cls = nn.Parameter(torch.zeros(d))
        layer = nn.TransformerEncoderLayer(d, 4, 4 * d, dropout=0.0, batch_first=True, norm_first=True, activation="gelu")
        s.enc = nn.TransformerEncoder(layer, layers, enable_nested_tensor=False)
        s.out = nn.Sequential(nn.LayerNorm(d), nn.Linear(d, d), nn.GELU(), nn.Linear(d, len(H) * len(Q)))

    def forward(s, x, m):
        """x: (B, 60) log price relative to the last observed price (0 where missing); m: (B, 60) 1 = observed."""
        both = m[:, 1:] * m[:, :-1]
        dd = nn.functional.pad((x[:, 1:] - x[:, :-1]) * both, (1, 0))
        both = nn.functional.pad(both, (1, 0))
        ch = (dd.abs() > 1e-7).float()
        f = torch.stack([m, x.clamp(-3, 3), torch.asinh(1000 * x) / 5, torch.asinh(1000 * dd) / 5, ch, both - ch], -1)
        z = torch.cat([s.cls.expand(len(x), 1, -1), s.inp(f)], 1) + s.pos
        return s.out(s.enc(z)[:, 0]).view(len(x), len(H), len(Q))          # asinh(1000 * log change)


def pinball(pred, y, q):
    e = y.unsqueeze(-1) - pred
    return torch.maximum(q * e, (q - 1) * e).mean()


def batch(rng, n, weights):
    return [torch.from_numpy(v).to(dev) for v in S.sample(rng, n, weights, a.prior_width)[:3]]


@torch.no_grad()
def predict(x, m):
    """(n, 3, 21) quantiles of the log change, non-decreasing."""
    net.eval()
    out = [net(torch.from_numpy(x[i:i + 2048]).to(dev), torch.from_numpy(m[i:i + 2048]).to(dev)) for i in range(0, len(x), 2048)]
    net.train()
    return np.sort(np.sinh(torch.cat(out).double().cpu().numpy()) / 1000, -1)


def sanity():
    """Per prior type, fresh series (default prior width): can the instrument fail? const must give no gain."""
    out, i3 = {}, [Q.index(.1), Q.index(.5), Q.index(.9)]
    for k in S.TYPES:
        x, m, y, _ = S.sample(np.random.default_rng(10_000 + S.TYPES.index(k)), 4000, {t: float(t == k) for t in S.TYPES})
        q, e0 = predict(x, m)[:, :, i3], y[:, :, None].astype(float)
        e = e0 - q
        lv = np.array([.1, .5, .9])
        net_l, base_l = np.maximum(lv * e, (lv - 1) * e).mean((0, 2)), np.maximum(lv * e0, (lv - 1) * e0).mean((0, 2)) * np.ones(3)
        out[k] = {f"h{h}": {"pinball_net": float(net_l[j]), "pinball_last_value": float(base_l[j]),
                            "skill": float(1 - net_l[j] / base_l[j]) if base_l[j] > 0 else None,
                            "in_band": float(((e0[:, j, 0] >= q[:, j, 0]) & (e0[:, j, 0] <= q[:, j, 2])).mean())}
                  for j, h in enumerate(H)}
    return out


panel = pd.read_csv(a.panel, keep_default_na=False)
panel["d"] = pd.to_datetime(panel.d); panel["p"] = panel.p.astype(float)
assert a.final or panel.d.max() <= pd.Timestamp("2026-10-30")
wide = {s: g.pivot(index="d", columns="listing", values="p").asfreq("D") for s, g in panel.groupby("series_id")}
assert len(wide) == 37


def real_inputs():
    """One row per (setup, series, listing, origin): the 60 calendar days that end at the origin, nothing later."""
    keys, xs, ms, lasts = [], [], [], []
    for t in pd.date_range(a.origin_start, a.origin_end):
        grid = pd.date_range(t - pd.Timedelta(days=S.CTX - 1), t)
        for sid, w in wide.items():
            w = w.loc[:t]
            for setup, cols in (("alone", [""]), ("lst_alone", [c for c in w.columns if c != ""])):
                if not cols:
                    continue                                              # afhubbard: series level only
                v = w[cols]
                v = v.loc[:v.dropna(how="all").index[-1]]                # ends at the last observed day
                v = v.loc[:, v.iloc[-1].notna()]                          # listings present on that day
                g = v.reindex(grid)
                for c in v.columns:
                    p = g[c].values; last = v[c].values[-1]; ok = np.isfinite(p)
                    keys.append((setup, sid, c, t.date().isoformat())); lasts.append(last)
                    xs.append(np.where(ok, np.log(np.where(ok, p, 1) / last), 0)); ms.append(ok)
    return keys, np.array(xs, np.float32), np.array(ms, np.float32), np.array(lasts)


def forecast(step):
    q = predict(RX, RM)
    assert np.isfinite(q).all()
    rows = [(*k, h, *(l * np.exp(q[i, j]))) for i, (k, l) in enumerate(zip(RK, RL)) for j, h in enumerate(H)]
    out = pd.DataFrame(rows, columns=["setup", "series_id", "listing", "origin_date", "horizon_days"] + [f"q{v:g}" for v in Q])
    out.to_csv(f"{OUT}/pfn_q_s{step}.csv", index=False, float_format="%.6g")
    print("wrote", len(out), "rows", out.groupby("setup").size().to_dict(), flush=True)


RK, RX, RM, RL = real_inputs()
print(len(RK), "real inputs; observed days per input:", np.quantile(RM.sum(1), [0, .25, .5, .75, 1]), flush=True)
net = Net(a.width, a.layers).to(dev)
npar = sum(p.numel() for p in net.parameters())
print(dev, "parameters", npar, "threads", torch.get_num_threads(), "weights", W, flush=True)
log = {"args": vars(a), "device": dev, "parameters": npar, "weights": W, "loss": [], "sanity": {}}
if a.load:
    net.load_state_dict(torch.load(a.load, map_location=dev))
    log["sanity"]["loaded"] = sanity(); forecast("loaded")
else:
    opt = torch.optim.AdamW(net.parameters(), lr=a.lr, weight_decay=.01)
    warm = max(1, a.steps // 20)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min((s + 1) / warm, .5 * (1 + math.cos(math.pi * min(1, s / a.steps)))))
    ck = sorted({max(1, round(float(c) * a.steps)) for c in a.ckpts.split(",")})
    rng, t0, run = np.random.default_rng(a.seed), time.time(), 0.0
    for step in range(1, a.steps + 1):
        x, m, y = batch(rng, a.batch, W)
        loss = pinball(net(x, m), torch.asinh(1000 * y), QT)
        opt.zero_grad(); loss.backward()
        nn.utils.clip_grad_norm_(net.parameters(), 1.0)
        opt.step(); sched.step()
        run = loss.item() if step == 1 else .98 * run + .02 * loss.item()
        if step % 100 == 0 or step in ck:
            log["loss"].append((step, run, round(time.time() - t0)))
            print(step, "loss", round(run, 4), round(time.time() - t0), "s", flush=True)
        if step in ck:
            log["sanity"][step] = sanity()
            print("sanity h7 skill", {k: v["h7"]["skill"] and round(v["h7"]["skill"], 3) for k, v in log["sanity"][step].items()},
                  "const pinball", log["sanity"][step]["const"]["h7"]["pinball_net"], flush=True)
            forecast(step)
            torch.save(net.state_dict(), f"{OUT}/model.pt")
            json.dump(log, open(f"{OUT}/train.json", "w"), indent=1)
    log["train_seconds"] = round(time.time() - t0); log["series_seen"] = a.steps * a.batch
json.dump(log["sanity"], open(f"{OUT}/sanity.json", "w"), indent=1)
json.dump(log, open(f"{OUT}/train.json", "w"), indent=1)
