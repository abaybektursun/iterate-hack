# gpuprice: quantile forecasts of GPU rental prices (Hackathon Track 2, Pacific)

Track 2 of the AI Research Hackathon, "Recursive Self-Improvement by Pacific: An AI Scientist for GPU Value".
Task as the data pack's starter kit states it: for each daily price series (USD per GPU-hour, posted prices, none
paid), forecast q10, q50, q90 at horizons 1, 3, 7 and 30 days from one origin date. Score: pinball loss, reported
as skill = 1 - loss / loss of the flat last-value forecast.

The track brief (PDF "Track 2 - Pacific - AI Scientist for GPU Value - Brief", linked from https://iterate.inc/ai-research,
read in full 2026-11-14) fixes:

- Forecasts with `origin_date` 2026-11-06 at horizons 1, 3, 7 (targets 7, 9, 13 November), "for the posted rental
  series you choose". Target table: `daily_statistics.csv`. AWS spot and horizon 30 are not scored.
- Scoring on Sunday 15 November, `scorer.py` in frozen-cutoff mode; headline is pooled skill; mean, median,
  geometric-mean skill and coverage (target 0.8) are reported. "Cells you leave out are filled with the last-value
  baseline". The brief does not say which series form the scored set.
- Baseline to beat: `drift` ("Beat drift with calibrated intervals").
- Submit: the forecast CSV, one command that reproduces it from the pack and cited public data dated on or before
  6 November, and findings (question, method, evaluation, results with uncertainty, what the system learned across
  iterations; optional argued view on resale and rentals in 2-3 years).
- Judged on rigour (leak-free, honest uncertainty), useful economic insight, reproducibility, originality.
  "Leaderboard position alone will not win." "A self-improving system should show its gains on origins it had not
  seen when it changed itself."
- External data: "public, free to every team and dated before each forecast origin".

## Layout

| Path | What it is |
|---|---|
| `prep/get_pack.sh` | Downloads the pack zip from the organisers' Drive folder into `runs/gpuprice/` (not committed), checks the zip SHA-256 and the pack's `MANIFEST.sha256`, builds `runs/gpuprice/.venv` (duckdb, pandas, numpy, pyarrow) and runs the starter demo into `runs/gpuprice/demo/`. 285 MB, about 4 minutes download, 24 s demo. |
| `analysis/readout.py` | Turns a folder of scorer reports into one run folder: `run.json`, `metrics.json` (overall and per horizon), `examples.json` (the cell with the largest gain and the largest loss against last value, with truth and quantiles). |
| `data/event_series_v1.csv` | The 37 series of the event set (below), from the starter's catalog at 2026-11-06. |
| `results/baselines/starter-01/` | The starter demo reproduced: cutoff 2026-10-24, 97 headline series. |
| `results/baselines/event37-01/` | Starter baselines on the event set: 30 daily origins. |
| `specs/SPEC1.md` | Plan of the listing-level simulator, written before the run. |
| `jobs/sim_median.py` | SPEC1 forecaster: resamples each listing's historical h-day outcome (price change, exit, entry) and takes the median. `--control` resamples the median's own change. Laptop, 40 s. |
| `jobs/run_backtest.sh` | One command for the SPEC1 backtest: series build at 2026-11-06, `last_value_empirical`, simulator, merge (afhubbard keeps the baseline), scorer. `bash studies/gpuprice/jobs/run_backtest.sh runs/gpuprice/<dir> [--control]` gives 0.196504. |
| `results/spec1/sim-01/`, `results/spec1/control-01/` | SPEC1 and its control on the event set. |
| `results/spec1/late-01/` | SPEC1 unchanged and `last_value_empirical` on six later origins that no earlier run used. |
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
| `spec1/sim-01` | same 3,109 cells | listing simulator (33 series) + last_value_empirical (4 afhubbard) | 0.0270 | 0.0335 | **+0.197** | +0.209 | 0.66 / 0.62 / 0.60 |
| `spec1/control-01` | same | control: the median's own change, same windows | 0.0293 | 0.0335 | +0.125 | +0.133 | 0.71 / 0.65 / 0.58 |

SPEC1 held: the simulator is +0.070 pooled skill above `last_value_empirical` (95 % interval +0.038 to +0.098,
bootstrap over the 37 series; better on 26 of 37 series and 25 of 30 origins). By horizon: +0.092 / +0.180 /
+0.234 at 1 / 3 / 7 days against +0.101 / +0.138 / +0.127, so the gain is at 3 and 7 days and day 1 is slightly
worse. By collector: fastgpu_daily +0.215 against +0.105 (20 series), gpurentalprices +0.169 against +0.162 (13).
The control equals the baseline, so the gain comes from the listing-level state, not from the windows. The
intervals are still too narrow (0.60 to 0.66 inside against 0.80).

**Unseen origins (`results/spec1/late-01/`).** The simulator, unchanged, on the six origins 2026-10-31 to
2026-11-05, which no earlier run used (357 cells: 209 at 1 day, 148 at 3 days; 7 days has no truth): pooled skill
+0.061 against +0.089 for `last_value_empirical`. At 1 day the simulator is worse, +0.055 against +0.123
(difference -0.068, 95 % interval -0.111 to -0.008). At 3 days it ties, +0.065 against +0.063 (difference +0.003,
-0.037 to +0.042). So the 1-day loss seen on the October origins is real, the 3-day gain (+0.180 against +0.138
there) did not repeat on these 4 origins, and the 7-day gain is untested on unseen origins. The largest losses are
`gpurentalprices.marketplace_ask.H100_80GB.spot.median`, 3 listings that turn over daily, where the simulator's
interval is too narrow.

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
