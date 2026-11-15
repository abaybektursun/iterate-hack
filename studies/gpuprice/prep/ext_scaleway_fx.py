"""ECB EUR/USD reference rate, and the test of Scaleway's posted USD price = fixed EUR price x lagged rate.

Run from the repository root:
    runs/gpuprice/.venv/bin/python -I -B studies/gpuprice/prep/ext_scaleway_fx.py

1. Writes studies/gpuprice/data/ext_ecb_eurusd_v1.csv (2026-06-01 to 2026-11-06, ECB data API) and its sidecar
   ext_ecb_eurusd_v1.json (source URL, retrieval time, sha256). An existing file is never overwritten: data/ is
   frozen, a changed input is a new version.
2. From the pack's own gpurentalprices rows of provider scaleway, for each listing: the implied EUR price
   (USD price / rate) under four rate dates, and how constant it is. Writes runs/gpuprice/ext/scaleway_fx.json.

Rate dates tried for a price posted on day d (the rate exists on TARGET business days only):
  lag 0: the last rate dated on or before d        lag 1: the last rate dated before d
  lag 2: the rate one business day before lag 1    lag 3: one more business day back

Source: European Central Bank, euro foreign exchange reference rates, series EXR.D.USD.EUR.SP00.A
(US dollar per euro, fixed about 14:15 CET, published about 16:00 CET). The ECB allows free use if it is cited
as the source (https://www.ecb.europa.eu/services/disclaimer/html/index.en.html, "Copyright").
"""
import csv
import datetime
import hashlib
import io
import json
import pathlib
import urllib.request

import duckdb
import numpy as np
import pandas as pd

START, CUTOFF = "2026-06-01", "2026-11-06"
URL = ("https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A"
       f"?startPeriod={START}&endPeriod={CUTOFF}&format=csvdata")
DATA = pathlib.Path("studies/gpuprice/data")
PACK = pathlib.Path("runs/gpuprice/pack/gpu-price-pack-v0.1.1-handover")
EXT = pathlib.Path("runs/gpuprice/ext")
EVENT = DATA / "event_series_v1.csv"


def get_ecb():
    f = DATA / "ext_ecb_eurusd_v1.csv"
    if not f.exists():
        req = urllib.request.Request(URL, headers={"User-Agent": "python-urllib", "Accept": "text/csv"})
        with urllib.request.urlopen(req, timeout=120) as r:
            raw = r.read().decode()
        rows = [(x["TIME_PERIOD"], x["OBS_VALUE"]) for x in csv.DictReader(io.StringIO(raw))]
        rows = sorted(r for r in rows if START <= r[0] <= CUTOFF)
        assert rows and rows[-1][0] <= CUTOFF and all(float(v) > 0 for _, v in rows)
        text = "date,usd_per_eur\n" + "".join(f"{d},{v}\n" for d, v in rows)
        f.write_text(text)
        (DATA / "ext_ecb_eurusd_v1.json").write_text(json.dumps({
            "file": f.name, "series": "EXR.D.USD.EUR.SP00.A",
            "title": "ECB euro foreign exchange reference rate, US dollar per euro, daily",
            "source_url": URL, "retrieved_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "rows": len(rows), "first_date": rows[0][0], "last_date": rows[-1][0],
            "sha256": hashlib.sha256(text.encode()).hexdigest(),
            "terms": "https://www.ecb.europa.eu/services/disclaimer/html/index.en.html (free use, ECB cited as source)",
            "attribution": "Source: European Central Bank, euro foreign exchange reference rates",
        }, indent=1) + "\n")
    fx = pd.read_csv(f, parse_dates=["date"]).set_index("date")["usd_per_eur"]
    assert str(fx.index.max().date()) <= CUTOFF
    return fx


def rate_for(fx, days, lag):
    """The rate a price posted on each day would use under one lag rule (see the module docstring)."""
    idx = fx.index
    pos = idx.searchsorted(days, side="right" if lag == 0 else "left") - 1  # last rate <= d, or < d
    pos = pos - max(lag - 1, 0)
    return pd.Series(fx.values[pos], index=days), pd.Series(idx[pos], index=days)


def main():
    fx = get_ecb()
    con = duckdb.connect()
    event = pd.read_csv(EVENT)
    rows = con.execute(f"""
        select dt, gpu_model, gpu_model_raw, usd_per_gpu_hour usd, fetched_at
        from read_parquet('{PACK}/rental_observations/source_id=gpurentalprices/*/*.parquet', hive_partitioning=false)
        where provider = 'scaleway' and pricing_tier = 'on_demand' and instrument_class = 'neocloud_rate_card'
        order by gpu_model, dt""").df()
    rows["dt"] = pd.to_datetime(rows["dt"])
    in_event = set(event[(event.source_id == "gpurentalprices") & (event.pricing_tier == "on_demand")].gpu_model)
    out = {"fx_file": "studies/gpuprice/data/ext_ecb_eurusd_v1.csv", "fx_rows": len(fx),
           "fx_last_date": str(fx.index.max().date()), "listings": []}
    for model, x in rows.groupby("gpu_model"):
        assert x["dt"].is_unique, model
        days = pd.DatetimeIndex(x["dt"])
        usd = pd.Series(x["usd"].values, index=days)
        rec = {"gpu_model": model, "in_event_series": model in in_event, "days": len(x),
               "first_day": str(days.min().date()), "last_day": str(days.max().date()),
               "usd_min": float(usd.min()), "usd_max": float(usd.max()), "usd_distinct": int(usd.nunique()),
               "fetch_hour_utc_median": float(pd.to_datetime(x["fetched_at"]).dt.hour.median()), "lags": {}}
        for lag in (0, 1, 2, 3):
            r, _ = rate_for(fx, days, lag)
            eur = usd / r
            mode = eur.round(3).mode().iloc[0]
            # one-step test: does yesterday's implied EUR price times today's rule rate give today's USD price?
            pred = eur.shift(1) * r
            err = (pred / usd - 1).abs().dropna()
            flat = (usd.shift(1) / usd - 1).abs().dropna()
            rec["lags"][lag] = {
                "eur_median": round(float(eur.median()), 4), "eur_min": round(float(eur.min()), 4),
                "eur_max": round(float(eur.max()), 4), "eur_cv_pct": round(float(100 * eur.std() / eur.mean()), 4),
                "eur_distinct_3dp": int(eur.round(3).nunique()),
                "share_days_within_0.05pct_of_mode": round(float(((eur / mode - 1).abs() < 5e-4).mean()), 4),
                "one_step_abs_err_pct_mean": round(float(100 * err.mean()), 4),
                "one_step_exact_share": round(float((err < 5e-4).mean()), 4),
                "dlog_corr": round(float(np.corrcoef(np.log(usd).diff().dropna(), np.log(r).diff().dropna())[0, 1]), 4),
            }
        rec["flat_last_value_abs_err_pct_mean"] = round(float(100 * flat.mean()), 4)
        rec["best_lag_by_cv"] = min(rec["lags"], key=lambda k: rec["lags"][k]["eur_cv_pct"])
        # the EUR price path under the best lag: the days on which the implied EUR price changed
        r, rd = rate_for(fx, days, rec["best_lag_by_cv"])
        eur = (usd / r).round(3)
        chg = eur[eur.diff().abs() > 0.002]
        rec["eur_steps_under_best_lag"] = [{"day": str(d.date()), "eur": float(v)} for d, v in chg.items()]
        rec["last_rows"] = [{"day": str(d.date()), "usd": float(usd[d]), "rate_date": str(rd[d].date()),
                             "rate": float(r[d]), "implied_eur": float(eur[d])} for d in days[-5:]]
        out["listings"].append(rec)
        print(model, "event" if rec["in_event_series"] else "not event", f"{len(x)} days, USD {usd.min()} to {usd.max()}")
        for lag, v in rec["lags"].items():
            print(f"  lag {lag}: EUR {v['eur_min']} to {v['eur_max']}, CV {v['eur_cv_pct']} %, distinct {v['eur_distinct_3dp']}, "
                  f"within 0.05 % of mode {v['share_days_within_0.05pct_of_mode']}, one-step error "
                  f"{v['one_step_abs_err_pct_mean']} % (exact {v['one_step_exact_share']}), dlog corr {v['dlog_corr']}")
        print(f"  flat last value one-step error {rec['flat_last_value_abs_err_pct_mean']} %; EUR steps:",
              rec["eur_steps_under_best_lag"][:8])
    # rate dates the scored days would need under lag 1
    need = {}
    for d in ("2026-11-07", "2026-11-09", "2026-11-13"):
        t = pd.Timestamp(d)
        prev = t - pd.Timedelta(days=1)
        while prev.weekday() >= 5:
            prev -= pd.Timedelta(days=1)
        need[d] = {"weekday": t.day_name(), "lag1_rate_date": str(prev.date()),
                   "in_file": bool(prev in fx.index), "known_at_origin": str(prev.date()) <= CUTOFF}
    out["rate_date_needed_under_lag_1"] = need
    print(need)
    EXT.mkdir(parents=True, exist_ok=True)
    (EXT / "scaleway_fx.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
