"""Synthetic sticky-price listings: the prior of the prior-data fitted network (pfn_train.py). numpy only.

Every number below was chosen after reading the rows of studies/gpuprice/data/fm_panel_v1.csv dated on or before
2026-09-30 (208 listings; print them with `python pfn_sim.py --real <panel>`), never a later row:
  - 80 % of the listings never change; the pooled change rate is 0.08 per listing-day;
  - Verda (27 listings) is flat for 40 days, then moves on 37 to 48 % of the days in steps of 1 % whose sign
    persists (91 % up)                                                                    -> type tick
  - Scaleway (5) moves on 68 % of the days by sd 0.2 % a day, flat over weekends, all listings together (a EUR
    price times the ECB rate)                                                             -> type fx
  - sfcompute moves on 89 % of the days by sd 10 % around a level; spheron hops between 4 prices
                                                                                          -> types market, discrete
  - AWS spot drifts smoothly with flat spells; GCP steps 5 % every 7 days                 -> types trend, sticky
  - sticky listings: jumps are two-sided, median |log change| 1 %, 11 % of them below 0.5 %; prices 0.07 to 16 USD
    with 2 to 4 decimals                                                                  -> types sticky, menu
Types rw, ou and smooth are the generic series (TempoPFN: a step-only prior is worse than seasonal naive).

sample(rng, n) returns, per series: x (60 days of log price relative to the last observed price, 0 where missing),
m (1 = observed), y (log change from the last observed price to the days 1, 3 and 7 after the origin), type index.
The origin is the last of the 60 days; up to 3 days before it may be missing (a collector outage), as on the
real grid.
"""
import numpy as np

CTX, HORIZONS, BURN = 60, (1, 3, 7), 40
N = BURN + CTX + max(HORIZONS)
TYPES = ("const", "sticky", "menu", "tick", "fx", "market", "discrete", "trend", "rw", "ou", "smooth")
WEIGHTS = dict(const=.10, sticky=.12, menu=.10, tick=.12, fx=.07, market=.06, discrete=.04, trend=.06,
               rw=.13, ou=.10, smooth=.10)
GENERIC, DAILY = ("rw", "ou", "smooth"), ("tick", "fx", "market", "discrete", "trend")


def logu(rng, lo, hi, n, width=1.0):
    """Log-uniform on [lo, hi]; width scales the log range about its centre (the prior-width ablation)."""
    c, h = (np.log(lo) + np.log(hi)) / 2, (np.log(hi) - np.log(lo)) / 2 * width
    return np.exp(rng.uniform(c - h, c + h, n))


def markov_on(rng, n, p_on, p_off):
    on = rng.random(n) < p_on / (p_on + p_off)
    out = np.empty((n, N), bool)
    for t in range(N):
        on = np.where(on, rng.random(n) >= p_off, rng.random(n) < p_on)
        out[:, t] = on
    return out


def const(rng, n, w):
    return np.zeros((n, N))


def sticky(rng, n, w):
    """Poisson price changes, two-sided, sizes around a per-listing scale; 25 % change only on a fixed period."""
    lam, s, up = logu(rng, .003, .3, n, w), logu(rng, .005, .3, n, w), rng.random(n)
    per = np.where(rng.random(n) < .25, np.where(rng.random(n) < .5, 7, rng.integers(2, 15, n)), 1)
    lam = np.where(per > 1, rng.uniform(.4, 1, n), lam)
    ph = rng.integers(0, 14, n)
    t = np.arange(N)[None]
    ch = (rng.random((n, N)) < lam[:, None]) & ((t + ph[:, None]) % per[:, None] == 0)
    sign = np.where(rng.random((n, N)) < up[:, None], 1, -1)
    return np.cumsum(ch * sign * s[:, None] * np.exp(.4 * rng.standard_normal((n, N))), 1)


def menu(rng, n, w):
    """Menu cost: a latent cost follows a random walk with a regime-switching drift; the price resets to it when
    the gap exceeds a band. Jumps are about one band wide, so there is no mass near zero."""
    sd, band = logu(rng, .001, .03, n, w), logu(rng, .005, .25, n, w)
    mu = rng.standard_normal(n) * sd * rng.uniform(0, 1.5, n)
    c, p, out = np.zeros(n), np.zeros(n), np.empty((n, N))
    for t in range(N):
        sw = rng.random(n) < .03
        mu = np.where(sw, rng.standard_normal(n) * sd * rng.uniform(0, 1.5, n), mu)
        c = c + mu + sd * rng.standard_normal(n)
        p = np.where(np.abs(c - p) > band, c, p)
        out[:, t] = p
    return out


def tick(rng, n, w):
    """Dynamic pricing in ticks (Verda): flat spells, then moves on most days by a fixed step whose sign persists."""
    on = markov_on(rng, n, logu(rng, .005, .2, n, w), logu(rng, .005, .2, n, w))
    act, rho, tau = rng.uniform(.3, 1, n), rng.uniform(.5, .98, n), logu(rng, .003, .03, n, w)
    sign, x, out = np.where(rng.random(n) < .5, 1, -1), np.zeros(n), np.empty((n, N))
    for t in range(N):
        ch = on[:, t] & (rng.random(n) < act)
        sign = np.where(ch & (rng.random(n) >= rho), -sign, sign)
        k = np.where(rng.random(n) < .15, rng.integers(2, 5, n), 1)
        x = x + ch * sign * k * tau * np.exp(.05 * rng.standard_normal(n))
        out[:, t] = x
    return out


def fx(rng, n, w):
    """A fixed foreign price times a daily exchange rate (Scaleway): small random walk, flat on 2 days of 7."""
    sd = logu(rng, .001, .01, n, w)
    e = rng.standard_t(5, (n, N)) * sd[:, None] / 1.29
    wk = (np.arange(N)[None] + rng.integers(0, 7, n)[:, None]) % 7
    e = np.where((wk < 2) & (rng.random(n) < .8)[:, None], 0, e)
    return np.cumsum(e, 1)


def market(rng, n, w):
    """A marketplace price (sfcompute): mean reversion around a slow level, some unchanged days, some spikes."""
    s, phi, stay, spike = logu(rng, .01, .2, n, w), rng.uniform(0, .95, n), rng.uniform(0, .5, n), rng.uniform(0, .1, n)
    msd = s * rng.uniform(0, .3, n)
    m, d, p, out = np.zeros(n), np.zeros(n), np.zeros(n), np.empty((n, N))
    for t in range(N):
        m = m + msd * rng.standard_normal(n)
        d = phi * d + s * rng.standard_normal(n)
        sp = (rng.random(n) < spike) * np.where(rng.random(n) < .5, 1, -1) * rng.uniform(.1, .5, n)
        p = np.where(rng.random(n) < stay, p, m + d + sp)
        out[:, t] = p
    return out


def discrete(rng, n, w):
    """Hops between 2 to 6 posted prices (spheron)."""
    k, spread, stay = rng.integers(2, 7, n), logu(rng, .01, .3, n, w), rng.uniform(.2, .95, n)
    lev = rng.uniform(-.5, .5, (n, 6)) * spread[:, None]
    wt = rng.dirichlet(np.ones(6), n) * (np.arange(6)[None] < k[:, None])
    cdf = np.cumsum(wt / wt.sum(1, keepdims=True), 1)
    i, out = np.zeros(n, int), np.empty((n, N))
    for t in range(N):
        j = np.minimum((rng.random(n)[:, None] > cdf).sum(1), k - 1)
        i = np.where(rng.random(n) < stay, i, j)
        out[:, t] = lev[np.arange(n), i]
    return out


def trend(rng, n, w):
    """A smoothly drifting price with flat spells (AWS spot): AR(1) daily changes."""
    on = markov_on(rng, n, logu(rng, .02, .3, n, w), logu(rng, .02, .3, n, w)) | (rng.random(n) < .3)[:, None]
    phi, s = rng.uniform(.5, .98, n), logu(rng, .0005, .01, n, w)
    v, x, out = np.zeros(n), np.zeros(n), np.empty((n, N))
    for t in range(N):
        v = phi * v + s * rng.standard_normal(n)
        x = x + on[:, t] * v
        out[:, t] = x
    return out


def rw(rng, n, w):
    sd = logu(rng, .0005, .1, n, w)
    e = np.where((rng.random(n) < .5)[:, None], rng.standard_normal((n, N)), rng.standard_t(5, (n, N)) / 1.29)
    return np.cumsum(sd[:, None] * (e + .2 * rng.standard_normal(n)[:, None]), 1)


def ou(rng, n, w):
    phi, s = rng.uniform(.3, .99, n), logu(rng, .0005, .1, n, w)
    x, out = s * rng.standard_normal(n) / np.sqrt(1 - phi ** 2), np.empty((n, N))
    for t in range(N):
        x = phi * x + s * rng.standard_normal(n)
        out[:, t] = x
    return out


def smooth(rng, n, w):
    """A smooth path: three sinusoids with random periods (5 to 120 days), half of the series with white noise."""
    t = np.arange(N)[None, None]
    per, amp = logu(rng, 5, 120, (n, 3)), logu(rng, .002, .2, n, w)[:, None] * rng.random((n, 3))
    x = (amp[:, :, None] * np.sin(2 * np.pi * (t / per[:, :, None] + rng.random((n, 3, 1))))).sum(1)
    return x + (rng.random(n) < .5)[:, None] * amp.max(1, keepdims=True) * rng.uniform(0, .2, (n, 1)) * rng.standard_normal((n, N))


GEN = dict(const=const, sticky=sticky, menu=menu, tick=tick, fx=fx, market=market, discrete=discrete, trend=trend,
           rw=rw, ou=ou, smooth=smooth)


def prices(rng, n, weights=WEIGHTS, width=1.0):
    """(n, N) posted prices in USD and the type index of each series."""
    p = np.array([weights[k] for k in TYPES], float)
    ty = rng.choice(len(TYPES), n, p=p / p.sum())
    X = np.empty((n, N))
    for i, k in enumerate(TYPES):
        if (ty == i).any():
            X[ty == i] = GEN[k](rng, int((ty == i).sum()), width)
    level = logu(rng, .05, 20, n)
    dec = rng.choice([2, 3, 4, 6], n, p=[.35, .35, .2, .1])
    P = level[:, None] * np.exp(X - X[:, [BURN]])
    P = np.maximum(np.round(P * 10.0 ** dec[:, None]) / 10.0 ** dec[:, None], 10.0 ** -dec[:, None])
    return P, ty


def sample(rng, n, weights=WEIGHTS, width=1.0):
    P, ty = prices(rng, n, weights, width)
    y = np.log(P)
    o = BURN + CTX - 1                                                    # index of the origin day
    gap = np.where(rng.random(n) < .15, rng.integers(1, 4, n), 0)        # missing days that end at the origin
    hist = np.where(rng.random(n) < .4, CTX, rng.integers(2, CTX + 1, n))  # days since the listing's first row
    last = o - gap
    idx = np.arange(o - CTX + 1, o + 1)[None]
    m = (idx <= last[:, None]) & (idx > (last - hist)[:, None])
    m &= ~((rng.random((n, CTX)) < (rng.uniform(0, .2, n) * (rng.random(n) < .3))[:, None]) & (idx != last[:, None]))
    ylast = y[np.arange(n), last][:, None]
    x = np.where(m, y[:, o - CTX + 1:o + 1] - ylast, 0)
    tgt = y[:, [o + h for h in HORIZONS]] - ylast
    return x.astype(np.float32), m.astype(np.float32), tgt.astype(np.float32), ty


def stats(P):
    """Per-series change rate, and the pooled |log change| of the changes, of a (series, days) price array with nan."""
    r = np.diff(np.log(P), axis=1)
    ok, ch = np.isfinite(r), np.abs(r) > 1e-9
    rate = (ch & ok).sum(1) / np.maximum(ok.sum(1), 1)
    return rate[ok.sum(1) >= 10], np.abs(r[ch & ok])


def show(name, rate, jumps):
    print(f"{name}: {len(rate)} series; never change {np.mean(rate == 0):.3f}; rate in (0,.05] (.05,.2] (.2,.6] (.6,1]:",
          (np.histogram(rate[rate > 0], [0, .05, .2, .6, 1.0001])[0] / len(rate)).round(3),
          f"pooled rate {rate.mean():.3f}; |log change| q5 q25 q50 q75 q95:",
          np.quantile(jumps, [.05, .25, .5, .75, .95]).round(4) if len(jumps) else "none")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--real", help="fm_panel_v1.csv: print the same statistics of the real listings to 2026-09-30")
    a = ap.parse_args()
    rng = np.random.default_rng(0)
    P, ty = prices(rng, 20000)
    show("prior", *stats(P[:, BURN:BURN + CTX]))
    for i, k in enumerate(TYPES):
        show(k, *stats(P[ty == i][:, BURN:BURN + CTX]))
    if a.real:
        import pandas as pd
        p = pd.read_csv(a.real, keep_default_na=False)
        p = p[(p.listing != "") & (p.d <= "2026-09-30")]                 # the prior sees nothing later
        p["d"] = pd.to_datetime(p.d)
        for src, g in p.groupby(p.series_id.str.split(".").str[0]):
            W = pd.concat({k: x.set_index("d").p.asfreq("D") for k, x in g.groupby(["series_id", "listing"])}, axis=1)
            show("real " + src, *stats(W.values.T))
