# gpuprice: quantile forecasts of GPU rental prices (Hackathon Track 2, Pacific)

Track 2 of the AI Research Hackathon, "Recursive Self-Improvement by Pacific: An AI Scientist for GPU Value".
Task as the data pack's starter kit states it: for each daily price series (USD per GPU-hour, posted prices, none
paid), forecast q10, q50, q90 at horizons 1, 3, 7 and 30 days from one origin date. Score: pinball loss, reported
as skill = 1 - loss / loss of the flat last-value forecast.

**Not yet read: the track's full brief** (linked on the event's resources page, not in the Drive folder). The
pack says the brief, not the pack, fixes the scored series, the origin, the ranking aggregate and what to submit.
Everything under "Event set" below is the pack's default and must be checked against the brief.

## Layout

| Path | What it is |
|---|---|
| `prep/get_pack.sh` | Downloads the pack zip from the organisers' Drive folder into `runs/gpuprice/` (not committed), checks the zip SHA-256 and the pack's `MANIFEST.sha256`, builds `runs/gpuprice/.venv` (duckdb, pandas, numpy, pyarrow) and runs the starter demo into `runs/gpuprice/demo/`. 285 MB, about 4 minutes download, 24 s demo. |
| `analysis/readout.py` | Turns a folder of scorer reports into one run folder: `run.json`, `metrics.json` (overall and per horizon), `examples.json` (the cell with the largest gain and the largest loss against last value, with truth and quantiles). |
| `data/event_series_v1.csv` | The 37 series of the event set (below), from the starter's catalog at 2026-11-06. |
| `results/baselines/starter-01/` | The starter demo reproduced: cutoff 2026-10-24, 97 headline series. |
| `results/baselines/event37-01/` | Starter baselines on the event set: 30 daily origins. |
| `ATTRIBUTION.md` | The pack's attribution file. It must stay with any work that uses the pack. |

The pack: `runs/gpuprice/pack/gpu-price-pack-v0.1.1-handover/` (v0.1.1-handover, data to 2026-11-06 23:59:59 UTC,
zip SHA-256 `f0b52af2...3b7c7c`). Read its `DATA.md` and `starter/README.md`; the scorer, the series builder and
the four baselines are in `starter/` and are used unchanged. Run them with `python -I -B` so nothing is written
into the pack.

## Event set

- Origin 2026-11-06. Truth window 2026-11-07 to 2026-11-13, so horizons 1, 3 and 7 are scored; horizon 30
  (2026-12-06) is not.
- AWS spot series have no November truth (the archive's November file is due 1 December). They are 80 of the 97
  headline series of the starter demo, so the demo's +0.20 does not describe the event.
- That leaves the `daily_statistics` series. At 2026-11-06 the starter's default gates mark 37 of them `headline`
  (`data/event_series_v1.csv`): 20 fastgpu_daily (60 days of history), 13 gpurentalprices (89 days), 4 afhubbard
  (234 days). 555 more are `extended` and can be scored if the brief says so.

Built with:
`build_series.py --pack <pack> --cutoff 2026-11-06 --as-of 2026-11-06 --out runs/gpuprice/event/history_2026-11-06.csv --catalog runs/gpuprice/event/catalog_2026-11-06.csv`

## Numbers

Pinball loss in USD per GPU-hour, mean over q10/q50/q90; skill against flat last value.

| Run | Series, origins, cells | Method | Pinball | Last value | Skill pooled | Median of series | In [q10, q90] |
|---|---|---|---|---|---|---|---|
| `starter-01` frozen | 97 headline, origin 2026-10-24, 291 cells (h 1, 3, 7) | drift | 0.0573 | 0.0717 | +0.200 | +0.147 | 0.73 |
| `starter-01` frozen | same | last_value_empirical | 0.0569 | 0.0717 | +0.207 | +0.147 | |
| `starter-01` backtest | 97 headline, 15 weekly origins 2026-07-15 to 2026-10-24, 5,325 cells | drift | 0.1019 | 0.1233 | +0.173 | +0.187 | |
| `event37-01` backtest | 37 event series, 30 daily origins 2026-10-01 to 2026-10-30, 3,109 cells (h 1, 3, 7) | last_value_empirical | 0.0293 | 0.0335 | **+0.126** | +0.117 | |
| `event37-01` backtest | same | drift | 0.0297 | 0.0335 | +0.114 | +0.116 | 0.69 / 0.62 / 0.55 at h 1 / 3 / 7 |

The starter rows match the pack's own README (+0.20 and +0.17). The number to beat is **+0.126 pooled** on the
event set (strongest starter baseline). Its intervals are too narrow: 55 to 69 % of truths fall inside
[q10, q90] against a target of 80 %, and 22 to 25 % fall above q90.

Limits of `event37-01`: the 30 origins overlap (a 7-day target is shared by neighbouring origins), so the cells
are not independent; every truth is inside the pack, so it is development feedback only.

## Data traps (pack `DATA.md`, section numbers)

- A median moves when the provider mix changes, with no provider changing a price (§3). Per-provider rows are in
  `rental_observations/`.
- Rate-card medians move in steps; a series that does not move has zero baseline loss and no skill.
- gpurentalprices has six missing days in October and November (§6.11); tanod rewrites past days (§6.5);
  fastgpu is a rolling 60 days (§6.10).
- Never pool across `source_id`: the same provider is in several collectors (§2.2).
- External data is allowed only if public, free and dated before the origin (§9). Vast.ai, RunPod, eBay, Reddit,
  gpulist.ai, cloud-gpus.com, SkyPilot, dstack and the Ornn, Silicon Data and SemiAnalysis dashboards are barred
  (§7, §9).
