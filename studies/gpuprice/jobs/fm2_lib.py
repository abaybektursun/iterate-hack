"""Shared by the round-2 foundation-model files: reads fm2_panel_v2.csv.gz and checks origins."""
import numpy as np, pandas as pd

DEV = [d.date().isoformat() for d in pd.date_range("2026-10-01", "2026-10-30")]
EVENT = "2026-11-06"
HORIZONS = (1, 3, 7)


LOCKED = ["2026-10-31", "2026-11-01", "2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05"]


def origins(spec):
    """'dev', 'event', 'dev,event' or explicit dates. Origins 2026-10-31..2026-11-05 are the locked test set."""
    out = []
    for s in spec.split(","):
        out += DEV if s == "dev" else [EVENT] if s == "event" else LOCKED if s == "locked" else [s]
    ok = DEV + [EVENT] + (LOCKED if "locked" in spec.split(",") else [])  # the locked set only by its name (specs/SPEC2.md)
    assert all(o in ok for o in out), "only the development origins and 2026-11-06 may be forecast"
    return out


def load(path):
    """Daily rows series_id, listing, chain, ext, d (Timestamp), p, from the run-length panel."""
    r = pd.read_csv(path, keep_default_na=False)
    r["d0"] = pd.to_datetime(r.d0); r["d1"] = pd.to_datetime(r.d1); r["p"] = r.p.astype(float); r["ext"] = r.ext.astype(int)
    out = []
    for sid, g in r.groupby("series_id"):
        s = g[g.listing == ""]
        days = np.sort(np.concatenate([pd.date_range(a, b).values for a, b in zip(s.d0, s.d1)]))   # observed days
        lo, hi = np.searchsorted(days, g.d0.values), np.searchsorted(days, g.d1.values, side="right")
        n = hi - lo
        assert (n > 0).all()
        x = g.loc[g.index.repeat(n), ["series_id", "listing", "chain", "ext", "p"]].reset_index(drop=True)
        x["d"] = np.concatenate([days[i:j] for i, j in zip(lo, hi)])
        out.append(x)
    return pd.concat(out, ignore_index=True)


def wide(rows, unit, long):
    """series_id -> frame calendar days x units (listing or chain) of one series; NaN = no row. '' = the series value."""
    if not long:
        rows = rows[rows.ext == 0]
    return {s: g.pivot(index="d", columns=unit, values="p").asfreq("D") for s, g in rows.groupby("series_id")}
