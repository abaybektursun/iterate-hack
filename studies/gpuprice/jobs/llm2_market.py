"""Builds studies/gpuprice/data/ext_market_v1.csv: daily closes of four listed companies tied to GPU supply and rental.

  runs/gpuprice/.venv/bin/python -I -B studies/gpuprice/jobs/llm2_market.py

Source: the public Yahoo Finance chart endpoint (free, no key), fixed window 2026-07-01 .. 2026-11-06, interval 1 day.
NVDA and AMD make the GPUs; CRWV (CoreWeave) and NBIS (Nebius) rent them and are listings in the series.
Rows: date (exchange trading day, New York), ticker, close (USD, unadjusted). No row dated after 2026-11-06 is stored.
"""
import datetime as dt, json, urllib.request, zoneinfo

TICKERS, FIRST, LAST = ("NVDA", "AMD", "CRWV", "NBIS"), dt.date(2026, 7, 1), dt.date(2026, 11, 6)
NY = zoneinfo.ZoneInfo("America/New_York")
stamp = lambda d, h: int(dt.datetime(d.year, d.month, d.day, h, tzinfo=dt.timezone.utc).timestamp())
rows = []
for t in TICKERS:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?period1={stamp(FIRST, 0)}&period2={stamp(LAST, 23)}&interval=1d"
    r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30))["chart"]["result"][0]
    for ts, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]):
        d = dt.datetime.fromtimestamp(ts, NY).date()
        assert c is not None and FIRST <= d <= LAST, (t, d, c)
        rows.append((str(d), t, round(c, 2)))
assert len(rows) > 4 * 80 and max(r[0] for r in rows) <= str(LAST)
with open("studies/gpuprice/data/ext_market_v1.csv", "w") as f:
    f.write("date,ticker,close\n" + "".join(f"{d},{t},{c}\n" for d, t, c in sorted(rows)))
print(f"wrote {len(rows)} rows, {min(r[0] for r in rows)} to {max(r[0] for r in rows)}")
