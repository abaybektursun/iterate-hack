"""Scores the LLM adjuster arm (llm2) against ens-05 on the same cells, and writes full forecast files.

  P="runs/gpuprice/.venv/bin/python -I -B studies/gpuprice/jobs/llm2_score.py"
  $P score <variant[-tag]> <model> [--mix 0.5] [--wide] [--origins pilot|heldout|all]     paired comparison on the cells the model answered
  $P write <variant> <model> <out.csv> [--mix 0.5] [--wide] [--base <forecast.csv>]   reads no truth               ens-05 schema; cells without an answer keep ens-05

--base, --cells: the forecast that was adjusted and its scored cells (defaults: ens-05 on the development origins).
Cells: (series, origin, horizon) of every cached response (runs/gpuprice/llm2/<variant>/<model>.jsonl) that ens-05's cells.csv
scored. Loss: pinball, mean over q10/q50/q90, USD per GPU-hour (the scorer's formula; checked against cells.csv on ens-05).
Skill: 1 - loss / loss of the flat last value, pooled. Interval: 2,000 bootstrap resamples of (series, origin) blocks, and of
series (the origins of one series overlap, so the series interval is the honest one).
--mix w: quantile average w * LLM + (1 - w) * ens-05. --wide: q10 = the lower of the two q10, q90 = the higher of the two q90
(the LLM may move q50 and widen the band, never narrow it). --origins heldout: the 24 development origins outside the pilot;
--mix and --wide were chosen on the pilot, so the held-out origins are their test.
Variants adj, echo: the stated quantiles, sorted. Variant prob: the quantiles of the three-point distribution the model
states (see prob_quantiles); average it with ens-05 by --mix 0.5.
"""
import argparse, json, sys
import numpy as np, pandas as pd

BASE = "runs/gpuprice/evals/ens-05-avg-fm217-sim215"
KEY = ["series_id", "origin_date", "horizon_days"]
QS = (("q10", 0.1), ("q50", 0.5), ("q90", 0.9))
PILOT = ["2026-10-01", "2026-10-07", "2026-10-13", "2026-10-19", "2026-10-25", "2026-10-30"]


def pinball(y, q, tau):
    return np.maximum(tau * (y - q), (tau - 1) * (y - q))


def loss(df, cols=("q10", "q50", "q90")):
    return sum(pinball(df.y, df[c], t) for c, (_, t) in zip(cols, QS)) / 3


def prob_quantiles(d, m0, base):
    """Three-point distribution: P(lower) at level_if_lower, the rest at the last value, P(higher) at level_if_higher -> q10, q50, q90."""
    pl, ph = min(max(d["p_lower"], 0), 1), min(max(d["p_higher"], 0), 1)
    lo, hi = min(d["level_if_lower"], m0), max(d["level_if_higher"], m0)
    out = []
    for tau in (0.1, 0.5, 0.9):
        out.append(lo if tau < pl else hi if tau > 1 - ph else m0)
    return out


def answers(variant, model):
    rows = []
    for line in open(f"runs/gpuprice/llm2/{variant}/{model}.jsonl"):
        r = json.loads(line)
        d = json.loads(r["raw"])
        for h in (1, 3, 7):
            x = d[f"h{h}"]
            q = prob_quantiles(x, r["last_value"], r["base"][str(h)]) if variant.startswith("prob") else sorted(x[k] for k, _ in QS)
            assert all(r["last_value"] / 5 < v < r["last_value"] * 5 for v in q), (r["series_id"], r["origin_date"], q)
            rows.append((r["series_id"], r["origin_date"], h, *q, d["reason"]))
    a = pd.DataFrame(rows, columns=KEY + ["a10", "a50", "a90", "reason"])
    assert not a.duplicated(KEY).any()
    return a


def combine(f, mix, wide):
    """In place: columns a10/a50/a90 (LLM) and q10/q50/q90 (ens-05) -> a10/a50/a90 of the forecast that is scored."""
    for k, _ in QS:
        f["a" + k[1:]] = mix * f["a" + k[1:]] + (1 - mix) * f[k]
    if wide:
        f["a10"] = np.minimum(f.a10, f.q10); f["a90"] = np.maximum(f.a90, f.q90)
        f["a50"] = f.a50.clip(f.a10, f.a90)


def table(variant, model, mix, wide=False, cells=f"{BASE}/cells.csv"):
    c = pd.read_csv(cells)
    c = c[c.status == "scored"]
    assert np.allclose(loss(c), c.loss, atol=1e-9), "pinball formula differs from the scorer"
    c = c.merge(answers(variant, model), on=KEY)
    combine(c, mix, wide)
    c["aloss"] = loss(c, ("a10", "a50", "a90"))
    c["changed"] = (np.abs(c[["a10", "a50", "a90"]].values - c[["q10", "q50", "q90"]].values) > 1e-5).any(axis=1)
    return c


def skills(c):
    b = c.baseline_loss.sum()
    return 1 - c.aloss.sum() / b, 1 - c.loss.sum() / b


def boot(c, by, n=2000, seed=0):
    g = c.groupby(by)[["aloss", "loss", "baseline_loss"]].sum().values
    rng = np.random.default_rng(seed)
    s = g[rng.integers(0, len(g), (n, len(g)))].sum(axis=1)
    d = (s[:, 1] - s[:, 0]) / s[:, 2]
    return np.quantile(d, [0.025, 0.975])


def score(variant, model, mix, origins, wide, cells):
    c = table(variant, model, mix, wide, cells)
    if origins != "all":
        c = c[c.origin_date.isin(PILOT) == (origins == "pilot")]
    sa, sb = skills(c)
    lo, hi = boot(c, ["series_id", "origin_date"]); slo, shi = boot(c, ["series_id"])
    print(f"{variant} {model} mix {mix}{' wide' if wide else ''} origins {origins}: {len(c)} cells, {c.groupby(['series_id', 'origin_date']).ngroups} series-origins, {c.origin_date.nunique()} origins")
    print(f"  pinball adjusted {c.aloss.mean():.5f}, base {c.loss.mean():.5f}, last value {c.baseline_loss.mean():.5f} USD/GPU-hour")
    print(f"  skill adjusted {sa:+.4f}, base {sb:+.4f}, difference {sa - sb:+.4f}  95% [{lo:+.4f}, {hi:+.4f}] series-origin blocks, [{slo:+.4f}, {shi:+.4f}] series blocks")
    for h, g in c.groupby("horizon_days"):
        a, b = skills(g)
        print(f"  +{h}d: {len(g)} cells, adjusted {a:+.4f}, base {b:+.4f}, difference {a - b:+.4f}")
    ch = c[c.changed]
    d = ch.loss - ch.aloss
    print(f"  changed {len(ch)} of {len(c)} cells ({len(ch) / len(c):.0%}); of those better {(d > 1e-9).sum()}, worse {(d < -1e-9).sum()}, same {(d.abs() <= 1e-9).sum()}; "
          f"max |adjusted - base loss| on unchanged cells {(c[~c.changed].aloss - c[~c.changed].loss).abs().max():.2e}")
    cov = lambda lo_, hi_: ((c[lo_] <= c.y) & (c.y <= c[hi_])).mean()
    print(f"  inside [q10, q90]: adjusted {cov('a10', 'a90'):.2f}, base {cov('q10', 'q90'):.2f}")
    s = c.groupby("series_id")[["aloss", "loss", "baseline_loss"]].sum()
    s["gain"] = s.loss - s.aloss
    tot = s.gain.sum()
    print(f"  loss saved {tot:+.4f} USD summed; series better {(s.gain > 1e-9).sum()}, worse {(s.gain < -1e-9).sum()}; without the best series the difference is "
          f"{(tot - s.gain.max()) / (s.baseline_loss.sum() - s.baseline_loss[s.gain.idxmax()]):+.4f}")
    s = s.sort_values("gain")
    for sid, r in pd.concat([s.head(4), s.tail(4)]).iterrows():
        print(f"    {sid}: {r.gain:+.4f}")
    o = c.groupby("origin_date")[["aloss", "loss", "baseline_loss"]].sum()
    print("  by origin, difference:", {k[5:]: round((r.loss - r.aloss) / r.baseline_loss, 3) for k, r in o.iterrows()})
    return c


def write(variant, model, out, mix, wide, base):
    f = pd.read_csv(base)
    a = answers(variant, model)
    f = f.merge(a, on=KEY, how="left")
    has = f.a10.notna()
    g = f[has].copy()
    combine(g, mix, wide)
    for k, _ in QS:
        f.loc[has, k] = g["a" + k[1:]]
    f = f[KEY + ["q10", "q50", "q90"]]
    assert (f.q10 > 0).all() and (f.q10 <= f.q50 + 1e-12).all() and (f.q50 <= f.q90 + 1e-12).all() and f.origin_date.max() <= "2026-11-06"
    f.round(6).to_csv(out, index=False)
    print(f"wrote {len(f)} rows, {has.sum()} adjusted -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["score", "write"]); ap.add_argument("variant"); ap.add_argument("model"); ap.add_argument("out", nargs="?")
    ap.add_argument("--mix", type=float, default=1.0); ap.add_argument("--origins", default="all", choices=["all", "pilot", "heldout"])
    ap.add_argument("--wide", action="store_true")
    ap.add_argument("--base", default=f"{BASE}/forecast.csv"); ap.add_argument("--cells", default=f"{BASE}/cells.csv")
    a = ap.parse_args()
    if a.cmd == "score":
        score(a.variant, a.model, a.mix, a.origins, a.wide, a.cells)
    else:
        write(a.variant, a.model, a.out, a.mix, a.wide, a.base)
