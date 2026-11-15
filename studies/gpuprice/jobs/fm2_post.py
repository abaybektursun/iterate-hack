"""Round 2: turns the per-listing Chronos-2 quantile functions of fm2_chronos2.py into one forecast file. Laptop, no model.

runs/gpuprice/.venv/bin/python -I -B studies/gpuprice/jobs/fm2_post.py --quantiles runs/<job-id>/fm2_chronos2.csv \
    --origins dev --out runs/gpuprice/fm2/<name>.csv [options]
For a series, origin t and horizon h, with panel rows dated on or before t only:
  1. Units (listings, or chains with --setup chn*) present on the last observed day L <= t. Each has the model's
     quantile function for h days ahead (21 levels, linear between levels, constant outside 0.01 and 0.99).
  2. D simulations. Each unit's price is its quantile function read at a uniform number u:
       --dep indep   one u per unit (round 1, fm-07)
       --dep prov    one u per provider
       --dep copula  u comes from the unit's own history: a past window (s, s+g), g = h + (t - L), is drawn with
                     weight exp(-age / tau); u is the rank of the unit's own price ratio over that window among its
                     ratios over all windows (ties: uniform inside the tied block). Units move together as they did
                     in that window; each unit's marginal stays the model's. A unit absent in the window gets its own u.
  3. --snap F  a simulated price closer to the unit's last price than F times its smallest past daily move is set to
     the last price (a posted price does not move by a fraction of its smallest step). Units that never moved are
     left as the model gives them.
  3b. --hurdle  the unit keeps its last price with the probability its own history gives: of its past g-day
     windows (weights exp(-age / tau)), the weighted share with no price change, with half a pseudo-window of each
     kind. Otherwise its price is read from the model's quantile function. With --dep copula the unit stays if it
     stayed in the drawn window. The model decides how far a price moves, the unit's history how often.
     --hurdle-h 1 applies it at horizon 1 only (1,3: at horizons 1 and 3).
  3c. --replay P  linear pool at the unit: with probability P the unit repeats its own price ratio of the drawn
     window (if it was present at both ends), otherwise its price is the model's (after 3 and 3b).
  4. --scaleway  Scaleway units: USD price = EUR price x ECB rate of the last business day before the target day.
     EUR price = last USD price / the rate that priced it. The rate is known when that business day is <= t, else a
     driftless random walk from the last rate dated <= t with the daily volatility of the rates dated <= t.
  5. --turnover own|pool  a simulation also draws a past window: a unit leaves if it left in that window (own; pool,
     or a unit absent at the window's start: with the window's share of leavers) and the window's entrants are added
     (--enter ratio: at their ratio to the median at s, as sim_median.py; abs: at their posted price, only those
     absent today). With --dep copula the same window drives ranks and turnover.
  6. The forecast is the q10, q50, q90 of the simulated medians.
Any per-listing quantile file works (round 1's fm_chronos2.csv, a fine-tuned model's file): columns setup,
series_id, unit or listing, origin_date, horizon_days, q<level>...; setup lst_alone is read as lst, alone as ser.
afhubbard: --afh ser uses the model's quantiles of the series (round 1); --afh lst simulates its listings (steps 1-3, 6).
"""
import argparse, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fm2_lib

ap = argparse.ArgumentParser()
ap.add_argument("--quantiles", required=True, nargs="+", help="one or more fm2_chronos2.csv (jobs split by origin)"); ap.add_argument("--out", required=True)
ap.add_argument("--panel", default="studies/gpuprice/data/fm2_panel_v2.csv.gz")
ap.add_argument("--fx", default="studies/gpuprice/data/ext_ecb_eurusd_v1.csv")
ap.add_argument("--origins", default="dev")
ap.add_argument("--setup", default="lst", choices=["lst", "lst_long", "chn", "chn_long", "chn_cov"])
ap.add_argument("--ser", default="ser", choices=["ser", "ser_long"])
ap.add_argument("--afh", default="ser", choices=["ser", "lst"])
ap.add_argument("--dep", default="indep", choices=["indep", "prov", "copula"])
ap.add_argument("--dep-h1", default="", help="dependence at horizon 1 if it differs from --dep")
ap.add_argument("--hurdle", action="store_true"); ap.add_argument("--hurdle-h", default="1,3,7")
ap.add_argument("--replay", type=float, default=0)
ap.add_argument("--snap", type=float, default=0); ap.add_argument("--scaleway", action="store_true")
ap.add_argument("--turnover", default="", choices=["", "own", "pool"]); ap.add_argument("--enter", default="ratio", choices=["ratio", "abs"])
ap.add_argument("--turnover-only", default="", help="apply --turnover only to series whose id contains this text")
ap.add_argument("--tau", type=float, default=14); ap.add_argument("--draws", type=int, default=2000)
ap.add_argument("--seed", type=int, default=0)
a = ap.parse_args()
ORIG = fm2_lib.origins(a.origins)
H, QS = fm2_lib.HORIZONS, [0.1, 0.5, 0.9]
D = a.draws
rng = np.random.default_rng(a.seed)

f = pd.concat([pd.read_csv(p, keep_default_na=False) for p in a.quantiles], ignore_index=True)
f = f.rename(columns={"listing": "unit"})                           # round-1 and fine-tune files name the unit 'listing'
f["setup"] = f.setup.replace({"lst_alone": "lst", "alone": "ser"})
assert not f.duplicated(["setup", "series_id", "unit", "origin_date", "horizon_days"]).any()
qcols = [c for c in f.columns if c.startswith("q")]
LV = np.array([float(c[1:]) for c in qcols])
f = f[f.origin_date.isin(ORIG)]
assert set(f.origin_date) == set(ORIG), "the quantile files do not hold every origin asked for"
f[qcols] = np.sort(f[qcols].values.astype(float), axis=1)          # a quantile function must not decrease
QF = {s: {k: g for k, g in x.groupby(["series_id", "origin_date", "horizon_days"])} for s, x in f.groupby("setup")}

rows = fm2_lib.load(a.panel)
rows = rows[rows.d <= max(ORIG)]
long = a.setup in ("lst_long", "chn_long", "chn_cov")
unit = "chain" if a.setup.startswith("chn") else "listing"
lst = rows[rows.listing != ""]
isafh = lst.series_id.str.startswith("afhubbard.")
W = fm2_lib.wide(lst[~isafh], unit, long)
if a.afh == "lst":
    W.update(fm2_lib.wide(lst[isafh], "listing", False))
fx = pd.read_csv(a.fx, parse_dates=["date"]).set_index("date").usd_per_eur


def rate_day(day):
    """The ECB business day whose rate prices `day`: the last weekday before it."""
    b = day - pd.Timedelta(days=1)
    while b.weekday() >= 5:
        b -= pd.Timedelta(days=1)
    return b


def scaleway(last, L, t, h):
    """D simulated USD prices of a Scaleway unit on t + h."""
    known = fx.loc[:t]                                              # rule 1: rates dated on or before the origin
    eur = last / known.loc[:rate_day(L)].iloc[-1]
    b = rate_day(t + pd.Timedelta(days=h))
    if b <= known.index[-1]:
        return np.full(D, eur * known.loc[:b].iloc[-1])
    n = np.busday_count(known.index[-1].date(), b.date())           # business days from the last known rate to b
    sd = np.log(known).diff().std()
    return eur * known.iloc[-1] * np.exp(sd * np.sqrt(n) * rng.standard_normal(D))


def simulate(sid, w, o, h, setup, dep, turnover):
    t = pd.Timestamp(o)
    w = w.loc[:t]
    w = w.loc[w.notna().any(axis=1)]                                # observed days
    days = w.index; L = days[-1]; P = w.values
    cur = ~np.isnan(P[-1]); now = P[-1, cur]; n = cur.sum()
    q = QF[setup][(sid, o, h)].set_index("unit").reindex(w.columns[cur])
    assert q[qcols[0]].notna().all(), f"no quantile function for a unit of {sid} at {o}"
    qf = q[qcols].values
    m0 = np.median(now); g = h + (t - L).days
    U = rng.uniform(size=(n, D))
    prov = np.array([c.split("|")[0] for c in w.columns])

    win = None
    hurdle = a.hurdle and str(h) in a.hurdle_h.split(",")
    if dep == "copula" or turnover or hurdle or a.replay:
        idx = {d: i for i, d in enumerate(days)}
        se = [(i, idx[d + pd.Timedelta(days=g)]) for i, d in enumerate(days) if d + pd.Timedelta(days=g) in idx]
        if len(se) >= 5:
            si, ei = np.array(se).T
            wt = np.exp(-(t - days[ei]).days.values / a.tau); wt = wt / wt.sum()
            win = rng.choice(len(si), size=D, p=wt)                 # the window of each simulation
            R = P[ei][:, cur] / P[si][:, cur]                       # windows x units; NaN = absent at either end
            ok = ~np.isnan(R)
    if dep == "prov":
        _, inv = np.unique(prov[cur], return_inverse=True)
        U = rng.uniform(size=(inv.max() + 1, D))[inv]
    if dep == "copula" and win is not None:
        lo = np.zeros(R.shape); hi = np.ones(R.shape)
        for j in range(n):
            r = R[ok[:, j], j]; ww = wt[ok[:, j]]
            if len(r):
                lo[ok[:, j], j] = [(ww[r < x]).sum() for x in r]; hi[ok[:, j], j] = [(ww[r <= x]).sum() for x in r]
                lo[ok[:, j], j] /= ww.sum(); hi[ok[:, j], j] /= ww.sum()
        U = lo[win].T + U * (hi[win].T - lo[win].T)                 # absent in the window: lo 0, hi 1, so U itself
    X = np.stack([np.interp(U[j], LV, qf[j]) for j in range(n)])   # units x simulations

    if hurdle and win is not None:
        wk = wt[:, None] * ok
        nw = ok.sum(0)                                               # own windows of each unit
        stay_w = (wk * (R == 1)).sum(0) / np.where(nw, wk.sum(0), 1) * nw
        p_stay = (stay_w + 0.5) / (nw + 1)
        S = rng.uniform(size=(n, D)) < p_stay[:, None]
        if dep == "copula":
            S = np.where(ok[win].T, (R == 1)[win].T, S)
        X = np.where(S, now[:, None], X)
    if a.snap:
        for j, c in enumerate(np.flatnonzero(cur)):
            x = P[:, c]; x = x[~np.isnan(x)]
            mv = np.abs(x[1:] / x[:-1] - 1); mv = mv[mv > 0]
            if len(mv):
                X[j, np.abs(X[j] / now[j] - 1) < a.snap * mv.min()] = now[j]
    if a.replay and win is not None:
        B = (rng.uniform(size=(n, D)) < a.replay) & ok[win].T
        X = np.where(B, now[:, None] * np.where(ok, R, 1)[win].T, X)
    if a.scaleway:
        for j in np.flatnonzero(prov[cur] == "scaleway"):
            X[j] = scaleway(now[j], L, t, h)

    if turnover and win is not None:
        at_s = ~np.isnan(P[si]); at_e = ~np.isnan(P[ei])
        left = at_s & ~at_e
        share = left.sum(1) / at_s.sum(1)                            # window's share of leavers
        own = left[:, cur][win].T                                    # units x simulations
        rnd = rng.uniform(size=(n, D)) < share[win][None, :]
        out = rnd if turnover == "pool" else np.where(at_s[:, cur][win].T, own, rnd)
        X = np.where(out, np.nan, X)
        ent = ~at_s & at_e
        if a.enter == "abs":
            E = np.where(ent & ~cur[None, :], P[ei], np.nan)
        else:
            med_s = np.nanmedian(P[si], axis=1)
            E = np.where(ent, m0 * P[ei] / med_s[:, None], np.nan)
        E = E[:, ~np.isnan(E).all(0)]
        X = np.concatenate([X, E[win].T])
    sim = np.where(np.isnan(X).all(0), m0, np.nanmedian(np.where(np.isnan(X).all(0), m0, X), axis=0))
    return np.quantile(sim, QS)


out = []
for sid in sorted(set(f.series_id)):
    for o in ORIG:
        if sid not in W:
            for h in H:
                q = QF[a.ser][(sid, o, h)]
                out.append((sid, o, h, *q[["q0.1", "q0.5", "q0.9"]].values[0]))
            continue
        if W[sid].loc[:pd.Timestamp(o)].notna().any(axis=1).sum() == 0:
            continue
        isa = sid.startswith("afhubbard.")
        for h in H:
            dep = a.dep_h1 if (h == 1 and a.dep_h1) else a.dep
            turn = "" if isa or a.turnover_only not in sid else a.turnover
            out.append((sid, o, h, *simulate(sid, W[sid], o, h, "afh" if isa else a.setup, "indep" if isa else dep, turn)))
out = pd.DataFrame(out, columns=["series_id", "origin_date", "horizon_days", "q10", "q50", "q90"]).round(6)
assert not out.duplicated(["series_id", "origin_date", "horizon_days"]).any() and (out.q10 <= out.q50).all() and (out.q50 <= out.q90).all()
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
out.to_csv(a.out, index=False)
print("wrote", len(out), "rows,", out.series_id.nunique(), "series,", out.origin_date.nunique(), "origins ->", a.out)
