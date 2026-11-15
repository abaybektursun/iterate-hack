"""Context of one (series, origin) for the LLM adjuster arm (llm2): text built only from rows dated on or before the origin.

  runs/gpuprice/.venv/bin/python -I -B studies/gpuprice/jobs/llm2_context.py test     # leak test: planted post-origin rows change nothing
  runs/gpuprice/.venv/bin/python -I -B studies/gpuprice/jobs/llm2_context.py show <series_id> <origin> [<base forecast> <cells,cells>]

Inputs: the median history (runs/gpuprice/event/history_2026-11-06.csv), the listing panel (data/fm2_panel_v2.csv.gz), the
base forecast and its scored cells (defaults: runs/gpuprice/evals/ens-05-avg-fm217-sim215/, the development origins; the
locked and event origins name their own files, see llm2_run.py). Leak rule, enforced in build(): every frame is cut to
date <= origin (cells: target_date <= origin) before any text is made, and the text is checked for later dates.
"""
import datetime as dt, pathlib, sys
import numpy as np, pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import fm2_lib

R = "runs/gpuprice"
BASE = f"{R}/evals/ens-05-avg-fm217-sim215"
HORIZONS = (1, 3, 7)
LAST_DEV, EVENT = dt.date(2026, 10, 30), dt.date(2026, 11, 6)   # load() allows origins to LAST_DEV unless told otherwise, never past EVENT
LOCKED_CELLS = f"{R}/spec2/cells_candidate.csv"
MAX_LISTINGS = 24


def load(base=f"{BASE}/forecast.csv", cells=(f"{BASE}/cells.csv",), last_origin=LAST_DEV):
    """All inputs as frames with a python date column `d` (cells: also `target`). base: the forecast to adjust; cells: scorer
    per-cell files of that forecaster (its record); last_origin: the latest origin build() accepts."""
    assert last_origin <= EVENT
    cell_files = cells
    hist = pd.read_csv(f"{R}/event/history_2026-11-06.csv", usecols=["series_id", "date", "value", "n_obs"])
    hist["d"] = pd.to_datetime(hist.date).dt.date
    panel = fm2_lib.load("studies/gpuprice/data/fm2_panel_v2.csv.gz")
    panel["d"] = panel.d.dt.date
    cells = pd.concat([pd.read_csv(f) for f in cell_files], ignore_index=True)
    assert not cells.duplicated(["series_id", "origin_date", "horizon_days"]).any()
    cells = cells[cells.status == "scored"]
    cells["d"] = pd.to_datetime(cells.origin_date).dt.date
    cells["target"] = pd.to_datetime(cells.target_date).dt.date
    fc = pd.read_csv(base)
    cat = pd.read_csv("studies/gpuprice/data/event_series_v1.csv").set_index("series_id")
    return {"hist": hist, "panel": panel, "cells": cells, "fc": fc, "cat": cat, "last_origin": last_origin}


def fmt(x):
    return f"{x:.4f}".rstrip("0").rstrip(".")


def runs(days, val):
    """'10-01..10-12 4.264 | 10-13 4.3': consecutive days with the same text merged."""
    out, start, prev = [], days[0], days[0]
    for d in days[1:] + [None]:
        if d is None or val[d] != val[start]:
            out.append((f"{start:%m-%d}" if prev == start else f"{start:%m-%d}..{prev:%m-%d}") + f" {val[start]}")
            start = d
        prev = d
    return " | ".join(out)


def window(t, n):
    return [t - dt.timedelta(days=i) for i in range(n - 1, -1, -1)]


def build(D, sid, origin, days_median=60, days_listing=21, parts=("listings", "other", "record")):
    """-> dict(text, last_value, base {h: (q10, q50, q90)}). `origin` is a date. Nothing dated after it is read."""
    t = origin
    assert t <= D["last_origin"] <= EVENT, "origin outside the allowed window"
    hist, panel, cells = D["hist"], D["panel"], D["cells"]
    hist = hist[hist.d <= t]; panel = panel[panel.d <= t]; cells = cells[(cells.target <= t) & (cells.d <= t)]   # the leak cut
    assert hist.d.max() <= t and panel.d.max() <= t and (cells.empty or cells.target.max() <= t)
    c = D["cat"].loc[sid]
    h = hist[hist.series_id == sid].set_index("d").value
    m0, last_day = float(h.iloc[-1]), h.index[-1]

    def median_line(s, n):
        w = [d for d in window(t, n) if d >= s.index[0]]
        return f"{w[0]} to {t}: " + runs(w, {d: (fmt(s[d]) if d in s.index else "no data") for d in w})

    out = [f"Series: daily median of the posted rental prices (USD per GPU-hour) of all listings of the GPU {c.gpu_model} "
           f"(pricing tier {c.pricing_tier}, segment {c.instrument_class}) collected by the price tracker {c.source_id}. "
           f"Posted prices, not paid prices. A listing is one provider (or provider and region or SKU).",
           f"Median, {median_line(h, days_median)}"]

    if "listings" in parts:
        g = panel[(panel.series_id == sid) & (panel.listing != "") & (panel.ext == 0)]
        win = window(t, days_listing)
        g = g[g.d >= win[0]]
        have = set(h.index)
        tab = g.pivot(index="listing", columns="d", values="p")
        last = tab.ffill(axis=1).iloc[:, -1]
        n_all = len(tab)
        keep = (last - m0).abs().sort_values().index[:MAX_LISTINGS]
        tab = tab.loc[keep].assign(_l=last[keep]).sort_values("_l").drop(columns="_l")
        lines = []
        for name, row in tab.iterrows():
            val = {d: ("no data" if d not in have else "-" if d not in row.index or np.isnan(row[d]) else fmt(row[d])) for d in win}
            lines.append(" / ".join(x for x in name.split("|") if x) + ": " + runs(win, val))
        note = "" if n_all <= MAX_LISTINGS else f" Only the {MAX_LISTINGS} listings nearest the median are shown, of {n_all}."
        out.append(f"Price of each listing, {win[0]} to {t} (a range holds one unchanged price; \"-\" = listing absent; "
                   f"\"no data\" = the tracker collected nothing that day), sorted by price.{note}\n" + "\n".join(lines))

    if "other" in parts:
        cat = D["cat"]
        twin = cat[(cat.gpu_model == c.gpu_model) & (cat.pricing_tier == c.pricing_tier) & (cat.source_id != c.source_id)
                   & cat.source_id.isin(("fastgpu_daily", "gpurentalprices"))]
        for osid, o in twin.iterrows():
            oh = hist[hist.series_id == osid].set_index("d").value
            out.append(f"The same GPU and tier in another tracker ({o.source_id}, segment {o.instrument_class}; its listing set differs), "
                       f"median, {median_line(oh, 30)}")

    base = {}
    f = D["fc"][(D["fc"].series_id == sid) & (D["fc"].origin_date == str(t))].set_index("horizon_days")
    for k in HORIZONS:
        base[k] = tuple(float(f.loc[k, q]) for q in ("q10", "q50", "q90"))

    if "record" in parts:
        p = cells[cells.series_id == sid].sort_values(["target", "horizon_days"])
        if len(p):
            pos = np.where(p.y < p.q10, "below q10", np.where(p.y > p.q90, "above q90", "inside"))
            moved = int((p.y != p.baseline_q50).sum())
            lines = [f"origin {r.d:%m-%d} +{r.horizon_days}d (target {r.target:%m-%d}): last {fmt(r.baseline_q50)}, forecast "
                     f"{fmt(r.q10)} / {fmt(r.q50)} / {fmt(r.q90)}, actual {fmt(r.y)} ({w})" for r, w in zip(p.itertuples(), pos)][-15:]
            out.append(f"Record of the base forecast on this series, all {len(p)} forecasts whose target date has passed: actual inside "
                       f"[q10, q90] {(pos == 'inside').mean():.0%}, below q10 {(pos == 'below q10').mean():.0%}, above q90 "
                       f"{(pos == 'above q90').mean():.0%}; the median differed from the last value in {moved} of {len(p)}. "
                       f"The latest {len(lines)}:\n" + "\n".join(lines))
        else:
            out.append("Record of the base forecast on this series: none yet.")

    out.append(f"Today is {t:%A} {t}. The latest median is {fmt(m0)}" + (f" (from {last_day})" if last_day != t else "") + ".\n"
               "Base forecast (q10 / q50 / q90):\n" + "\n".join(
                   f"+{k}d ({t + dt.timedelta(days=k):%A}): {base[k][0]:.6f} / {base[k][1]:.6f} / {base[k][2]:.6f}" for k in HORIZONS))
    text = "\n\n".join(out)
    for k in range(1, 60):                                   # no later date may appear in any form the text uses
        later = t + dt.timedelta(days=k)
        assert str(later) not in text and f"{later:%m-%d}" not in text.replace(str(t.year) + "-", ""), f"a date after {t} is in the context"
    return {"text": text, "last_value": m0, "base": base}


def test():
    """Plants rows dated after the origin (price 777.777) in every input and requires byte-identical contexts: a development
    origin with the default files, a locked origin and the event origin with their own base forecast and cells."""
    dev = f"{BASE}/cells.csv"
    for name, t, kw in (("dev", dt.date(2026, 10, 13), {}),
                        ("locked", dt.date(2026, 11, 2), dict(base=f"{R}/spec2/candidate.csv", cells=(dev, LOCKED_CELLS), last_origin=dt.date(2026, 11, 5))),
                        ("event", EVENT, dict(base="studies/gpuprice/results/submission/forecast_2026-11-06.csv", cells=(dev, LOCKED_CELLS), last_origin=EVENT))):
        test_one(name, load(**kw), t)


def test_one(name, D, t):
    sid = "fastgpu_daily.neocloud_rate_card.B300.on_demand.median"
    clean = build(D, sid, t)["text"]
    P = dict(D)
    for k in ("hist", "panel", "cells"):
        x = D[k]
        late = x[(x.series_id == sid) & ((x.target if k == "cells" else x.d) > t)]
        assert len(late) or t == EVENT, f"{k}: no post-origin row to drop"     # the real files hold later rows (none after the event origin)
        plant = x[x.series_id == sid].tail(3).copy()
        plant["d"] = [t + dt.timedelta(days=i) for i in (1, 2, 3)]
        for col in ("value", "p", "y"):
            if col in plant:
                plant[col] = 777.777
        if k == "cells":
            plant["target"] = plant["d"] + dt.timedelta(days=1); plant["d"] = t      # origin in range (the origin itself), target after it
            plant["horizon_days"] = [91, 92, 93]
        P[k] = pd.concat([x, plant], ignore_index=True)
    planted = build(P, sid, t)["text"]
    assert planted == clean and "777.777" not in planted, "a post-origin row reached the context"
    try:
        build(D, sid, D["last_origin"] + dt.timedelta(days=1))
    except AssertionError as e:
        print(f"{name}: rejects origin {D['last_origin'] + dt.timedelta(days=1)}:", e)
    else:
        raise SystemExit("late origin accepted")
    print(f"{name}: leak test passed at origin {t}: planted rows dropped, context identical ({len(clean)} characters)")


if __name__ == "__main__":
    if sys.argv[1] == "test":
        test()
    else:
        t = dt.date.fromisoformat(sys.argv[3])
        D = load(sys.argv[4], tuple(sys.argv[5].split(",")), t) if len(sys.argv) > 4 else load()
        print(build(D, sys.argv[2], t)["text"])
