"""Builds the committed input of the round-2 foundation-model jobs: studies/gpuprice/data/fm2_panel_v2.csv.gz.

runs/gpuprice/.venv/bin/python -I -B studies/gpuprice/jobs/fm2_panel.py \
    --pack runs/gpuprice/pack/gpu-price-pack-v0.1.1-handover --ext runs/gpuprice/ext/rental_observations_ext.parquet \
    --history runs/gpuprice/event/history_2026-11-06.csv --series studies/gpuprice/data/event_series_v1.csv \
    --out studies/gpuprice/data/fm2_panel_v2.csv.gz

Differences from fm_panel_v1.csv:
  - rows to 2026-11-06 (--last), so the event origin can be forecast; every reader must cut at its origin;
  - the 30 extra days per collector of prep/ext_history.py (ext = 1); the series value of an extra day is the median
    of its listings;
  - the listings (provider|region|sku) of the 4 afhubbard series, one price per listing and day (median over the
    day's 1 to 3 snapshots);
  - chain: a listing identity that survives a key change. If, between two consecutive observed days of a series,
    exactly one listing of a provider disappears and exactly one listing of that provider that was never seen
    before appears, the new listing continues the chain of the old one (Scaleway's key gained a region on
    2026-10-18). Uses rows up to the day of the change only.
  - run-length rows: series_id, listing, chain, ext, d0, d1, p = the listing had price p on every observed day of
    the series from d0 to d1 (days on which the collector has no row for the series are skipped, not broken).
    listing '' is the series value itself; its runs hold calendar-consecutive days only, so they list the observed
    days of the series.
Data: GPU price pack v0.1.1-handover, CC BY 4.0, see studies/gpuprice/ATTRIBUTION.md.
"""
import argparse
import duckdb, numpy as np, pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--pack", required=True); ap.add_argument("--ext", required=True); ap.add_argument("--history", required=True)
ap.add_argument("--series", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--last", default="2026-11-06")
a = ap.parse_args()
ev = pd.read_csv(a.series)
con = duckdb.connect(); con.register("ev", ev)
SEL = """select ev.series_id, cast(o.dt::date as varchar) as d, o.provider,
         o.provider || '|' || coalesce(o.region_raw, '') || '|' || coalesce(o.sku_raw, '') as listing,
         o.usd_per_gpu_hour as p, {ext} as ext
  from {src} o join ev on o.source_id = ev.source_id and o.instrument_class = ev.instrument_class
         and o.gpu_model = ev.gpu_model and o.pricing_tier = ev.pricing_tier
  where o.dt::date <= date '{last}'"""
pack = con.sql(SEL.format(ext=0, last=a.last, src=f"read_parquet('{a.pack}/rental_observations/*/*/*.parquet', hive_partitioning=false)")).df()
ext = con.sql(SEL.format(ext=1, last=a.last, src=f"read_parquet('{a.ext}')")).df()
afh = pack.series_id.str.startswith("afhubbard.")
assert not pack[~afh].duplicated(["series_id", "d", "listing"]).any(), "listing key is not unique per day"
assert not ext.duplicated(["series_id", "d", "listing"]).any() and not ext.series_id.str.startswith("afhubbard.").any()
assert ext.groupby("series_id").d.max().lt(pack.groupby("series_id").d.min().reindex(ext.series_id.unique())).all(), "extra days overlap the pack"
a_l = pack[afh].groupby(["series_id", "d", "provider", "listing", "ext"], as_index=False).p.median()
lst = pd.concat([ext, pack[~afh], a_l], ignore_index=True)

h = pd.read_csv(a.history, usecols=["series_id", "date", "value", "is_filled"])
h = h[h.series_id.isin(ev.series_id) & (h.date <= a.last)]
assert h.is_filled.eq(0).all() and h.series_id.nunique() == 37
ser = pd.DataFrame({"series_id": h.series_id, "d": h.date, "listing": "", "p": h.value, "ext": 0})
chk = lst.groupby(["series_id", "d", "ext"]).p.median().rename("m").reset_index().merge(ser[["series_id", "d", "p"]], on=["series_id", "d"], how="outer", indicator=True)
old = chk[chk.ext == 1]
assert (old._merge == "left_only").all()
ser = pd.concat([ser, pd.DataFrame({"series_id": old.series_id, "d": old.d, "listing": "", "p": old.m.round(4), "ext": 1})])
chk = chk[chk.ext != 1]
chk["dev"] = (chk.m - chk.p).abs()
chk["afh"] = chk.series_id.str.startswith("afhubbard.")
print("series-days:", chk._merge.value_counts().to_dict())
print("max |median of listings - series value|:", chk.groupby("afh").dev.max().to_dict(),
      "share of afhubbard days above 1e-4:", round((chk[chk.afh].dev > 1e-4).mean(), 4))

# chains
lst["chain"] = lst.listing
for sid, g in lst.groupby("series_id"):
    days = sorted(g.d.unique()); by = {d: x for d, x in g.groupby("d")}
    seen = set(by[days[0]].listing); chain = {l: l for l in seen}
    for s, e in zip(days[:-1], days[1:]):
        ps, pe = by[s], by[e]
        gone = ps[~ps.listing.isin(pe.listing)]; new = pe[~pe.listing.isin(seen)]
        for prov, n in new.groupby("provider"):
            o = gone[gone.provider == prov]
            chain[n.listing.iloc[0]] = chain[o.listing.iloc[0]] if len(n) == 1 and len(o) == 1 else n.listing.iloc[0]
            for l in n.listing.iloc[1:]:
                chain[l] = l
        seen |= set(pe.listing)
    lst.loc[g.index, "chain"] = g.listing.map(chain)
assert not lst.duplicated(["series_id", "d", "chain"]).any(), "two listings of one chain on one day"
print("listings:", lst.groupby("series_id").listing.nunique().sum(), "chains:", lst.groupby("series_id").chain.nunique().sum())

# run-length rows over the observed days of each series
ser["chain"] = ""
rows = pd.concat([ser, lst[ser.columns]], ignore_index=True)
rows["p"] = rows.p.round(6)
out = []
for sid, g in rows.groupby("series_id"):
    pos = {d: i for i, d in enumerate(sorted(g.d.unique()))}
    g = g.assign(i=g.d.map(pos))
    cal = g.listing == ""                                   # series rows break at a calendar gap: they define the observed days
    g.loc[cal, "i"] = (pd.to_datetime(g.d[cal]) - pd.Timestamp("2026-01-01")).dt.days
    g = g.sort_values(["listing", "i"])
    new = (g.listing != g.listing.shift()) | (g.i != g.i.shift() + 1) | (g.p != g.p.shift()) | (g.ext != g.ext.shift()) | (g.chain != g.chain.shift())
    r = g.groupby(new.cumsum()).agg(series_id=("series_id", "first"), listing=("listing", "first"), chain=("chain", "first"),
                                    ext=("ext", "first"), d0=("d", "first"), d1=("d", "last"), p=("p", "first"), n=("d", "size"))
    out.append(r)
out = pd.concat(out, ignore_index=True)
assert out.n.sum() == len(rows)
out.drop(columns="n").to_csv(a.out, index=False)
print(len(rows), "listing-days ->", len(out), "run rows ->", a.out, "last day", rows.d.max())
