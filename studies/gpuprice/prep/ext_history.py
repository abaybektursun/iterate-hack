"""Earlier history for fastgpu_daily and gpurentalprices, from the collectors' own public git histories.

Run from the repository root:
    runs/gpuprice/.venv/bin/python -I -B studies/gpuprice/prep/ext_history.py

The pack ships fastgpu_daily from 2026-09-08 and gpurentalprices from 2026-08-04. Older commits of the two
upstream repositories (both CC BY 4.0) hold earlier days. This script
  1. downloads the pinned upstream files into runs/gpuprice/ext/raw/ (every commit is dated on or before the
     forecast origin 2026-11-06, and rows or snapshot files dated after it are dropped before anything is written),
  2. maps them to the pack's rental_observations columns with the pack's own maps
     (rental_observations_mappings/) and rules (BUILD_rental_panels.md),
  3. proves the mapping: the same mapping on the days the pack ships is compared with the pack row by row and
     with daily_statistics.csv,
  4. writes runs/gpuprice/ext/rental_observations_ext.parquet with only the days before the pack's first day of
     each collector, and runs/gpuprice/ext/ext_report.json. A collector whose event-series medians are not
     reproduced on at least 99 % of the overlap rows is not written.

Sources and attribution:
  FastGPU GPU cloud pricing dataset (https://fastgpu.co/dataset), CC BY 4.0,
    https://huggingface.co/datasets/fastgpu/cloud-gpu-prices
  GPU rental price data by gpurentalprices.com (https://gpurentalprices.com), licensed under CC BY 4.0,
    https://github.com/adriannutiu/gpu-rental-prices
"""
import collections
import csv
import hashlib
import io
import json
import pathlib
import tarfile
import urllib.request

import duckdb
import pandas as pd

CUTOFF = "2026-11-06"  # forecast origin; nothing dated after it may be written to disk
PACK = pathlib.Path("runs/gpuprice/pack/gpu-price-pack-v0.1.1-handover")
EXT = pathlib.Path("runs/gpuprice/ext")
RAW = EXT / "raw"
EVENT = pathlib.Path("studies/gpuprice/data/event_series_v1.csv")

# Pinned upstream versions: (commit, commit date UTC, role).
# "ext" holds the days before the pack's first day; "overlap" is the last commit on or before the origin.
FASTGPU = {
    "ext": ("3747aa6580a14e936b06221ce6b9b18e95e53608", "2026-10-08T07:30:45Z"),
    "overlap": ("e608bd3f660fe0ca061734afa73cb700e588c702", "2026-11-06T07:30:44Z"),
}
GITHUB = {
    "ext": ("c4e232d024dffb3c0363a101d4609a9ed9f38bc0", "2026-10-02T13:05:32Z"),
    "overlap": ("54ab7cd6eca39473a602721f0d31534589e283d1", "2026-11-06T14:32:53Z"),
}
PACK_FIRST = {"fastgpu_daily": "2026-09-08", "gpurentalprices": "2026-08-04"}

# The publisher's errata as the pack applied them (BUILD_rental_panels.md, section 3, gpurentalprices).
# (action, provider, first day, last day, gpus or None for all, kinds or None for all)
ERRATA = [
    (0, "reclassify-spot", "vultr", "2026-07-05", "2026-07-17", ["b200", "h100-sxm"], ["on-demand"]),
    (1, "exclude", "vultr", "2026-07-09", "2026-07-17", None, None),
    (6, "exclude", "aws", "2026-09-27", "2026-09-27", None, None),
    (7, "exclude", "aws", "2026-07-07", "2026-09-26", None, None),
    (8, "reclassify-spot", "together", "2026-09-03", "2026-10-02", ["h100"], ["on-demand"]),
    (9, "reclassify-spot", "together", "2026-09-03", "2026-10-02", ["h200"], ["on-demand"]),
    (10, "reclassify-spot", "together", "2026-09-03", "2026-10-02", ["b200"], ["on-demand"]),
    (11, "reclassify-spot", "together", "2026-09-25", "2026-10-02", ["b300"], ["on-demand"]),
    (12, "reclassify-marketplace", "lium", "2026-10-05", "9999-12-31", None, ["secure"]),
]  # errata 2 to 5 name RunPod, which the filter rule drops anyway
# Errata 8 to 11: the build note gives 2026-10-05 as the last day, but the pack's rows carry the Together
# reclassification only to 2026-10-02 (its rows of 3 to 5 October are on_demand). The pack's rows decide.

# fastgpu relabelled gcp B200 from on-demand to reserved on every day of its file between the commits of
# 2026-10-08 and 2026-11-06 (31 of 31 shared days; the pack has the later label). Applied to the older commit.
FASTGPU_RELABEL = {("gcp", "B200", "on-demand"): "reserved"}

COLUMNS = [
    "obs_id", "source_id", "instrument_class", "source_url", "licence_id", "snapshot_ts_utc", "dt", "provider",
    "provider_raw", "provider_segment", "gpu_model", "gpu_model_raw", "gpu_memory_gb", "gpu_count", "sku_raw",
    "region_raw", "region_canonical", "country", "pricing_tier", "pricing_tier_raw", "usd_per_hour_instance",
    "usd_per_gpu_hour", "price_basis", "usd_per_gpu_hour_avg", "usd_per_gpu_hour_max", "n_observations",
    "quality_flag", "available", "availability_raw", "collector", "collector_version", "fetched_at", "extra_json",
]
# Columns compared row by row with the pack (everything that decides a statistic, plus the raw identity).
CMP = ["dt", "provider", "provider_raw", "provider_segment", "gpu_model", "gpu_model_raw", "instrument_class",
       "pricing_tier", "pricing_tier_raw", "region_raw", "sku_raw", "usd_per_gpu_hour"]


def http_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "python-urllib"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def fetch_fastgpu(sha):
    """gpu-prices-daily.csv at one commit; rows after the cutoff are dropped before the file is written."""
    d = RAW / "fastgpu" / sha
    f = d / "gpu-prices-daily.csv"
    if not f.exists():
        base = f"https://huggingface.co/datasets/fastgpu/cloud-gpu-prices/resolve/{sha}/"
        lines = http_get(base + "gpu-prices-daily.csv").decode().splitlines()
        assert lines[0].startswith("day,provider,gpu_model,offer_type,region,min_price_usd_hr"), lines[0]
        kept = [lines[0]] + [ln for ln in lines[1:] if ln[:10] <= CUTOFF]
        readme = http_get(base + "README.md")
        d.mkdir(parents=True, exist_ok=True)
        (d / "README.md").write_bytes(readme)
        f.write_text("\n".join(kept) + "\n")
        print(f"fastgpu {sha[:12]}: {len(lines) - 1} rows upstream, {len(lines) - len(kept)} after {CUTOFF} dropped")
    rows = list(csv.DictReader(open(f)))
    assert max(r["day"] for r in rows) <= CUTOFF
    return rows


def fetch_github(sha):
    """The repository tarball at one commit; only LICENSE, README.md and snapshots dated to the cutoff are kept."""
    d = RAW / "gpurentalprices" / sha
    if not d.exists():
        blob = http_get(f"https://codeload.github.com/adriannutiu/gpu-rental-prices/tar.gz/{sha}")
        keep = {}
        with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tar:
            for m in tar.getmembers():
                if not m.isfile():
                    continue
                rel = m.name.split("/", 1)[1]
                if rel in ("LICENSE", "README.md", "CITATION.cff"):
                    keep[rel] = tar.extractfile(m).read()
                elif rel.startswith("data/snapshots/") and rel.endswith(".json"):
                    if pathlib.PurePosixPath(rel).stem <= CUTOFF:
                        keep[rel] = tar.extractfile(m).read()
        for rel, data in keep.items():
            p = d / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
    snaps = {}
    for p in sorted((d / "data" / "snapshots").glob("*.json")):
        j = json.loads(p.read_text())
        assert j["date"] == p.stem and j["date"] <= CUTOFF, p
        snaps[p.stem] = j
    return snaps


def load_maps():
    m = PACK / "rental_observations_mappings"
    prov, gpu = {}, {}
    for r in csv.DictReader(open(m / "provider_map.csv")):
        prov[(r["source_id"], r["provider_raw"])] = (r["provider"], r["provider_segment"], r["action"])
    for r in csv.DictReader(open(m / "gpu_model_map.csv")):
        if r["source_id"] not in PACK_FIRST:
            continue
        k = (r["source_id"], r["gpu_model_raw"])
        v = (r["gpu_model"], r["gpu_basis"])
        assert gpu.setdefault(k, v) == v, f"gpu_model_map is not a function of gpu_model_raw: {k}"
    tier = {r["tier_raw"]: r["pricing_tier"] for r in csv.DictReader(open(m / "pricing_tier_map.csv"))}
    return prov, gpu, tier


def instrument_class(segment, tier):
    if segment == "marketplace":
        return "marketplace_ask"
    spot = tier == "spot"
    if segment == "hyperscaler":
        return "hyperscaler_spot" if spot else "hyperscaler_list"
    assert segment == "neocloud", segment
    return "neocloud_spot" if spot else "neocloud_rate_card"


def md5(*parts):
    return hashlib.md5("|".join("" if p is None else str(p) for p in parts).encode()).hexdigest()


def map_fastgpu(rows, sha, maps, unmapped, relabel_old):
    prov, gpu, tier = maps
    out = []
    url = f"https://huggingface.co/datasets/fastgpu/cloud-gpu-prices/resolve/{sha}/gpu-prices-daily.csv"
    for r in rows:
        praw = r["provider"]
        if "vast" in praw.lower() or "runpod" in praw.lower():  # the pack's filter rule
            continue
        pk, gk = ("fastgpu_daily", praw), ("fastgpu_daily", r["gpu_model"])
        if pk not in prov or gk not in gpu or r["offer_type"] not in tier:
            unmapped[("fastgpu_daily", praw if pk not in prov else "", r["gpu_model"] if gk not in gpu else "")] += 1
            continue
        provider, segment, action = prov[pk]
        assert action == "keep", pk
        model, basis = gpu[gk]
        extra = {"gpu_basis": basis}
        relabel = FASTGPU_RELABEL.get((praw, r["gpu_model"], r["offer_type"])) if relabel_old else None
        if relabel:
            extra["offer_type_at_commit"] = r["offer_type"]
            r = dict(r, offer_type=relabel)
        t = tier[r["offer_type"]]
        region = r["region"] or None
        out.append({
            "obs_id": md5("ext", "fastgpu_daily", r["day"], praw, r["gpu_model"], r["offer_type"], region),
            "source_id": "fastgpu_daily", "instrument_class": instrument_class(segment, t), "source_url": url,
            "licence_id": "CC-BY-4.0", "snapshot_ts_utc": pd.Timestamp(r["day"]), "dt": r["day"],
            "provider": provider, "provider_raw": praw, "provider_segment": segment, "gpu_model": model,
            "gpu_model_raw": r["gpu_model"], "gpu_memory_gb": None, "gpu_count": None, "sku_raw": None,
            "region_raw": region, "region_canonical": None, "country": None, "pricing_tier": t,
            "pricing_tier_raw": r["offer_type"], "usd_per_hour_instance": None,
            "usd_per_gpu_hour": float(r["min_price_usd_hr"]), "price_basis": "daily_min_per_provider_gpu_region",
            "usd_per_gpu_hour_avg": float(r["avg_price_usd_hr"]), "usd_per_gpu_hour_max": float(r["max_price_usd_hr"]),
            "n_observations": int(r["observations"]), "quality_flag": "ok", "available": None,
            "availability_raw": None, "collector": "fastgpu.co", "collector_version": f"hf@{sha[:12]}",
            "fetched_at": pd.NaT, "extra_json": json.dumps(extra, separators=(",", ":")),
        })
    return out


def map_github(snaps, sha, maps, unmapped):
    prov, gpu, tier = maps
    out = []
    for day, snap in snaps.items():
        ts = pd.Timestamp(snap["generated_at"]).tz_convert(None)
        for i, o in enumerate(snap["offers"]):
            praw = o["provider"]
            if "vast" in praw.lower() or "runpod" in praw.lower():  # the pack's filter rule
                continue
            kind, applied, excluded = o["kind"], None, False
            for n, action, p, d0, d1, gpus, kinds in ERRATA:
                if p != praw or not d0 <= day <= d1:
                    continue
                if (gpus is not None and o["gpu"] not in gpus) or (kinds is not None and o["kind"] not in kinds):
                    continue
                if action == "exclude":
                    excluded = True
                else:
                    kind, applied = action.split("-", 1)[1], f"errata#{n}:{action}"
            if excluded:
                continue
            pk, gk = ("gpurentalprices", praw), ("gpurentalprices", o["gpu"])
            if pk not in prov or gk not in gpu or kind not in tier:
                unmapped[("gpurentalprices", praw if pk not in prov else "", o["gpu"] if gk not in gpu else "")] += 1
                continue
            provider, segment, action = prov[pk]
            assert action == "keep", pk
            model, basis = gpu[gk]
            t = tier[kind]
            cls = "marketplace_ask" if kind == "marketplace" else instrument_class(segment, t)
            avail = o.get("availability")
            extra = {"instance": o.get("instance"), "commitment": o.get("commitment"),
                     "min_gpus": None if o.get("min_gpus") is None else str(o["min_gpus"]),
                     "rate_basis": o.get("rate_basis"), "stock_level": o.get("stock_level"),
                     "kind_effective": kind, "errata_applied": applied, "snapshot_file": f"{day}.json",
                     "gpu_basis": basis}
            out.append({
                "obs_id": md5("ext", "gpurentalprices", day, i, praw, o["gpu"], o["kind"], o["usd_hr"]),
                "source_id": "gpurentalprices", "instrument_class": cls, "source_url": o["source_url"],
                "licence_id": "CC-BY-4.0", "snapshot_ts_utc": ts, "dt": day, "provider": provider,
                "provider_raw": praw, "provider_segment": segment, "gpu_model": model, "gpu_model_raw": o["gpu"],
                "gpu_memory_gb": o["vram_gb"], "gpu_count": None, "sku_raw": o.get("instance"),
                "region_raw": o.get("region"), "region_canonical": None, "country": None, "pricing_tier": t,
                "pricing_tier_raw": o["kind"], "usd_per_hour_instance": None, "usd_per_gpu_hour": float(o["usd_hr"]),
                "price_basis": "as_listed_per_gpu", "usd_per_gpu_hour_avg": None, "usd_per_gpu_hour_max": None,
                "n_observations": None, "quality_flag": "ok",
                "available": {"in-stock": True, "out-of-stock": False}.get(avail), "availability_raw": avail,
                "collector": "gpurentalprices.com", "collector_version": f"github@{sha[:12]}",
                "fetched_at": pd.Timestamp(o["fetched_at"]).tz_convert(None),
                "extra_json": json.dumps(extra, separators=(",", ":")),
            })
    return out


def frame(rows):
    df = pd.DataFrame(rows, columns=COLUMNS)
    df["dt"] = pd.to_datetime(df["dt"]).dt.date
    for c in ("gpu_memory_gb", "gpu_count", "n_observations"):
        df[c] = df[c].astype("Int32")
    for c in ("usd_per_hour_instance", "usd_per_gpu_hour_avg", "usd_per_gpu_hour_max"):
        df[c] = df[c].astype("float64")
    df["available"] = df["available"].astype("boolean")
    for c in ("sku_raw", "region_raw", "region_canonical", "country", "availability_raw"):
        df[c] = df[c].astype("string")  # VARCHAR in the Parquet file even when every value is null
    for c in ("snapshot_ts_utc", "fetched_at"):
        df[c] = pd.to_datetime(df[c])
    return df


def stats(con, table):
    """daily_statistics.csv recomputed with the pack's definition (BUILD_rental_panels.md, section 4)."""
    return con.execute(f"""
        select cast(dt as varchar) date, source_id, gpu_model, pricing_tier, instrument_class,
               count(*) n_obs, count(distinct provider) n_providers,
               round(quantile_cont(usd_per_gpu_hour, 0.5), 4) median, round(quantile_cont(usd_per_gpu_hour, 0.25), 4) p25,
               round(quantile_cont(usd_per_gpu_hour, 0.75), 4) p75, round(min(usd_per_gpu_hour), 4) mn
        from {table} where gpu_model <> 'other' group by all""").df()


def compare(con, name, mine, source_id, event):
    """Row-by-row and daily-statistics comparison of mapped upstream rows with the pack, on the days both have."""
    pack = con.execute(f"""select * from read_parquet('{PACK}/rental_observations/source_id={source_id}/*/*.parquet',
                           hive_partitioning=false)""").df()
    pack["dt"] = pd.to_datetime(pack["dt"]).dt.date
    days = sorted(set(mine["dt"]) & set(pack["dt"]))
    a = mine[mine["dt"].isin(days)]
    b = pack[pack["dt"].isin(days)]
    key = lambda df: collections.Counter(
        tuple(None if pd.isna(v) else (round(v, 6) if isinstance(v, float) else str(v)) for v in t)
        for t in df[CMP].itertuples(index=False))
    ca, cb = key(a), key(b)
    matched = sum((ca & cb).values())
    only_pack, only_mine = cb - ca, ca - cb
    by_day = collections.Counter()
    for t, n in list(only_pack.items()) + list(only_mine.items()):
        by_day[t[0]] += n
    # daily statistics, recomputed from my rows, against the pack's file
    con.register("mine_t", a)
    sa = stats(con, "mine_t")
    ds = con.execute(f"""select cast(date as varchar) date, source_id, gpu_model, pricing_tier, instrument_class, n_obs,
        n_providers, median_usd_per_gpu_hour median, p25_usd_per_gpu_hour p25, p75_usd_per_gpu_hour p75,
        min_usd_per_gpu_hour mn from read_csv('{PACK}/daily_statistics.csv', header=true)
        where source_id='{source_id}'""").df()
    ds = ds[ds["date"].isin([str(d) for d in days])]
    k = ["date", "source_id", "gpu_model", "pricing_tier", "instrument_class"]
    j = ds.merge(sa, on=k, how="outer", suffixes=("_pack", "_mine"), indicator=True)
    same_med = (j["_merge"] == "both") & ((j["median_pack"] - j["median_mine"]).abs() < 5e-5)
    same_all = same_med & (j["n_obs_pack"] == j["n_obs_mine"]) & (j["n_providers_pack"] == j["n_providers_mine"])
    for c in ("p25", "p75", "mn"):
        same_all &= (j[f"{c}_pack"] - j[f"{c}_mine"]).abs() < 5e-5
    ev = j.merge(event[["source_id", "gpu_model", "pricing_tier", "instrument_class", "series_id"]], how="inner",
                 on=["source_id", "gpu_model", "pricing_tier", "instrument_class"])
    ev = ev[ev["_merge"] != "right_only"]
    ev_same = (ev["_merge"] == "both") & ((ev["median_pack"] - ev["median_mine"]).abs() < 5e-5)
    ev_bad = ev[~ev_same][["date", "series_id", "median_pack", "median_mine", "n_obs_pack", "n_obs_mine"]]
    ev_rows = b.merge(event[["source_id", "gpu_model", "pricing_tier", "instrument_class"]], how="inner")
    ev_mine = a.merge(event[["source_id", "gpu_model", "pricing_tier", "instrument_class"]], how="inner")
    ev_matched = sum((key(ev_rows) & key(ev_mine)).values())
    rep = {
        "check": name, "source_id": source_id, "days": len(days), "first_day": str(days[0]), "last_day": str(days[-1]),
        "pack_rows": len(b), "mapped_rows": len(a), "rows_matched": matched,
        "row_match_rate": matched / len(b), "rows_only_in_pack": sum(only_pack.values()),
        "rows_only_in_mapped": sum(only_mine.values()),
        "event_pack_rows": len(ev_rows), "event_rows_matched": ev_matched,
        "event_row_match_rate": ev_matched / len(ev_rows),
        "stat_keys_pack": int((j["_merge"] != "right_only").sum()),
        "stat_keys_median_equal": int(same_med.sum()), "stat_keys_all_fields_equal": int(same_all.sum()),
        "event_series_days_pack": len(ev), "event_series_days_median_equal": int(ev_same.sum()),
        "event_median_match_rate": float(ev_same.mean()),
        "mismatch_rows_by_day": {str(d): n for d, n in sorted(by_day.items())},
        "mismatch_examples_only_in_pack": [list(t) for t in list(only_pack)[:8]],
        "mismatch_examples_only_in_mapped": [list(t) for t in list(only_mine)[:8]],
        "event_median_mismatches": ev_bad.sort_values(["date", "series_id"]).head(40).to_dict("records"),
    }
    print(f"{name}: {len(days)} days {days[0]} to {days[-1]}; rows matched {matched} of {len(b)} pack rows "
          f"({100 * rep['row_match_rate']:.2f} %), {rep['rows_only_in_mapped']} only in mapped; event rows "
          f"{ev_matched} of {len(ev_rows)} ({100 * rep['event_row_match_rate']:.2f} %); medians equal "
          f"{rep['stat_keys_median_equal']} of {rep['stat_keys_pack']} keys, event series-days "
          f"{rep['event_series_days_median_equal']} of {len(ev)}")
    return rep


def main():
    maps = load_maps()
    event = pd.read_csv(EVENT)
    con = duckdb.connect()
    unmapped = collections.Counter()
    report = {"cutoff": CUTOFF, "pins": {"fastgpu": FASTGPU, "gpurentalprices": GITHUB}, "checks": []}

    fg = {k: frame(map_fastgpu(fetch_fastgpu(sha), sha, maps, unmapped, k == "ext")) for k, (sha, _) in FASTGPU.items()}
    gh = {k: frame(map_github(fetch_github(sha), sha, maps, unmapped)) for k, (sha, _) in GITHUB.items()}
    report["unmapped_rows"] = [{"source_id": s, "provider_raw": p, "gpu_model_raw": g, "rows": n}
                               for (s, p, g), n in sorted(unmapped.items())]
    print("unmapped (dropped) rows:", report["unmapped_rows"])

    out = []
    for source_id, sets in (("fastgpu_daily", fg), ("gpurentalprices", gh)):
        reps = [compare(con, f"{source_id} {k} commit against pack", df, source_id, event) for k, df in sets.items()]
        report["checks"] += reps
        first = pd.Timestamp(PACK_FIRST[source_id]).date()
        ext = sets["ext"][sets["ext"]["dt"] < first]
        ok = all(r["event_row_match_rate"] >= 0.99 and r["event_median_match_rate"] >= 0.99 for r in reps)
        report[source_id] = {"shipped": bool(ok), "ext_rows": len(ext), "ext_days": int(ext["dt"].nunique()),
                             "ext_first_day": str(ext["dt"].min()), "ext_last_day": str(ext["dt"].max())}
        print(source_id, report[source_id])
        if ok:
            out.append(ext)
        else:
            print(f"NOT SHIPPED: {source_id} does not reproduce the pack on 99 % of the event-series overlap")

    ext = pd.concat(out, ignore_index=True)
    assert ext["obs_id"].is_unique
    assert all(str(d) < PACK_FIRST[s] for s, d in ext.groupby("source_id")["dt"].max().items())
    assert not ext["provider"].str.contains("vast|runpod", case=False).any()
    EXT.mkdir(parents=True, exist_ok=True)
    ext.to_parquet(EXT / "rental_observations_ext.parquet", index=False)
    print("wrote", EXT / "rental_observations_ext.parquet", len(ext), "rows")

    # what the extension adds to each event series
    con.register("ext_t", ext)
    st = stats(con, "ext_t")
    gains = []
    for s in event.itertuples():
        x = st[(st.source_id == s.source_id) & (st.gpu_model == s.gpu_model) & (st.pricing_tier == s.pricing_tier)
               & (st.instrument_class == s.instrument_class)]
        gains.append({"series_id": s.series_id, "pack_first_date": s.first_date, "extra_days": len(x),
                      "extra_days_3_providers": int((x.n_providers >= 3).sum()),
                      "first_date_now": min([s.first_date] + list(x.date))})
    report["event_series_gain"] = gains
    st.sort_values(["source_id", "gpu_model", "pricing_tier", "instrument_class", "date"]).to_csv(
        EXT / "daily_statistics_ext.csv", index=False)
    (EXT / "ext_report.json").write_text(json.dumps(report, indent=1, default=str))
    print(pd.DataFrame(gains).to_string(index=False))


if __name__ == "__main__":
    main()
