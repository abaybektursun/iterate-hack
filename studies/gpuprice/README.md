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

## Submission

- Forecast: `results/submission/forecast_2026-11-06.csv` (111 rows: 37 series, horizons 1, 3, 7, origin 2026-11-06).
  It is candidate 2 (`specs/SPEC3.md`). Candidate 1 (`specs/SPEC2.md`) is kept beside it as
  `results/submission/forecast_2026-11-06_candidate1.csv`.
- Reproduce: `bash studies/gpuprice/jobs/reproduce.sh` from the repository root (pack download, one Chronos-2
  inference job, post-processing, simulator, average, then candidate 2: the daily-maximum member and the replay of
  the 37 stored `claude-fable-5-2` responses in `results/llm2/event_fable_adj.jsonl`, each checked against the
  prompt rebuilt from the pack). With the stored inference output
  (`CHRONOS_CSV=runs/abaybektursun-1114-201131-4739/fm2_chronos2.csv`) it rewrites both files unchanged. No API
  key is needed; without `--replay` the model is called again and its answers may differ.
- Findings: `FINDINGS.md`.

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
| `jobs/eval.sh`, `results/ledger/` | Hill-climb harness and its record: one JSON per iteration. |
| `jobs/fm_*`, `jobs/fm2_*` | Foundation-model arm: listing panel, Chronos-2 inference job, post-processing to the median (`fm2_post.py` is the current one; `data/fm2_panel_v2.csv.gz` runs to 2026-11-06). |
| `jobs/sim2_own.py` | Own-history listing simulator. |
| `jobs/ft_*`, `jobs/pfn_*`, `jobs/tab_*`, `jobs/llm_*` | Fine-tuning, synthetic-prior network, TabPFN and LLM arms (not in the candidate). |
| `prep/ext_history.py`, `prep/ext_scaleway_fx.py`, `data/ext_ecb_eurusd_v1.csv` | 30 extra days per collector from pinned upstream commits; ECB EUR/USD to 2026-11-06 and the Scaleway test. |
| `specs/SPEC2.md`, `results/spec2/locked-01/` | The candidate, fixed before its run on the locked origins, and that run. |
| `prep/intraday.py`, `data/fm2_intraday_v2.csv.gz` | The day's maximum price and snapshot share of each `fastgpu_daily` listing, from the pack (`v1`: maximum only, used by `fm2-19`). Read by `fm2_post.py --intraday --exit-frac`. |
| `jobs/llm2_context.py`, `llm2_run.py`, `llm2_score.py` | LLM adjuster: one plain completion per series and origin (hosted API, no tools) that adjusts a base forecast; context cut at the origin (`llm2_context.py test` plants later rows); cache, cost cap, replay. Raw responses: `runs/gpuprice/llm2/` (not committed), event origin: `results/llm2/event_fable_adj.jsonl`. `results/llm2/base_cells_*.csv.gz`: candidate 1's scored cells shown to the model (target day on or before the origin only). |
| `specs/SPEC3.md`, `results/spec3/locked-01/` | Candidate 2, fixed before its run on the locked origins (their second use), and that run. |
| `jobs/loc_qavg.py`, `results/local/` | Average of per-listing quantile files (LoRA seeds, base) and the run folders of the local-GPU arms; weights and quantile files in `runs/gpuprice/local/` (not committed), environment `runs/gpuprice/.venv-gpu`. |
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

## Hill-climb and the candidate

`jobs/eval.sh` scores a forecast on the development origins (2026-10-01 to 2026-10-30, 3,109 cells) and writes one
entry per iteration into `results/ledger/` (name, hypothesis, pooled skill, per horizon, coverage), failures
included. Main entries, pooled skill against last value (1 / 3 / 7 days):

| Ledger entry | What | Pooled | 1 / 3 / 7 days |
|---|---|---|---|
| `it00-lve` | starter `last_value_empirical` | +0.126 | +0.101 / +0.138 / +0.127 |
| `fm-01` | `amazon/chronos-2` zero-shot on each median series | +0.132 | -0.087 / +0.102 / +0.207 |
| `fm-07` | the same model on each listing, median over independent draws | +0.272 | +0.099 / +0.249 / +0.331 |
| `sim2-15` | each listing replays its own h-day outcomes, recency 14 days, entrants (`jobs/sim2_own.py`) | +0.271 | +0.175 / +0.241 / +0.313 |
| `fm2-17` | `fm-07` + h=1 hurdle + Scaleway ECB rule + returning entrants (`jobs/fm2_post.py`) | +0.291 | +0.181 / +0.241 / +0.347 |
| `ft-05`, `ft-07` | `fm-07` with a LoRA trained on 8,000 synthetic sticky-price series only, two seeds | +0.295, +0.292 | |
| `ft-02`, `ft-03`, `ft-06` | LoRA or full fine-tune on the real listings (to 2026-09-30) | +0.241 to +0.265 | |
| `pfn-02` | 4.8M-parameter network trained only on simulated listings (`jobs/pfn_sim.py`, `pfn_train.py`) | +0.267 | +0.173 / +0.240 / +0.307 |
| `tab-01` | TabPFN v2 regressor per listing | +0.192 | |
| `llm-01` to `llm-04` | 80B open-weights LLM (`RedHatAI/Qwen3-Next-80B-A3B-Instruct-quantized.w4a16`) reading the listing table, 92 cells (10 series, 5 origins, 3 and 7 days): one number +0.015, stated quantiles +0.074, probabilities +0.058, reason-then-answer +0.128; same cells: `it00-lve` +0.106, `it01-sim` +0.180, `ens-04` +0.264. `results/llm/`. | | |
| `ens-05` | candidate 1: quantile average of `fm2-17` and `sim2-15` | +0.298 | +0.185 / +0.264 / +0.347 |
| `fm2-19` | `fm2-17` + the day's maximum price of each `fastgpu_daily` listing (`--intraday`) | +0.305 | +0.201 / +0.256 / +0.360 |
| `fm2-20` | `fm2-19` + exit signal from the snapshot share (`--exit-frac 0.25`), 8,000 draws | +0.306 | +0.213 / +0.252 / +0.360 |
| `llm2-01` | `claude-fable-5-2` (no tools, training data to June 2026) adjusts `ens-05`, 1,110 calls | +0.309 | |
| `llm2-03` | the same with the band never narrower than `ens-05`'s (rule chosen on 6 pilot origins; the other 24: +0.015, +0.007 to +0.025) | +0.313 | +0.209 / +0.278 / +0.360 |
| `loc-01` to `loc-11` | Chronos-2 arms on the laptop's RTX 4090 (`results/local/`, about 1.3 min per arm: LoRA 40 s, inference 83 s; the same LoRA took 65 min on Modal's cpu class). Synthetic-only LoRA inside the fm2 pipeline with `--intraday`: +0.312 (five seeds +0.305 to +0.316); half base, half 5-seed LoRA mean (`loc-09`): +0.318; averaged with `sim2-15`: +0.304 to +0.306; 10x synthetic data: no gain. Not in the submission: found after SPEC3 was fixed | +0.318 best | +0.210 / +0.276 / +0.371 |
| `llm2-04` | `gpt-6-astra` (knowledge cutoff 30 April 2026, no tools) adjusts `ens-05`: replicates `llm2-03` with a second provider's model (+0.015, +0.008 to +0.023; 24 held-out origins +0.016) | +0.313 | |
| `llm2-05` | `gpt-6.1-sol` (cutoff 30 April 2026, no tools) adjusts candidate 2 (`ens-06`), with the day's maximum and snapshot share in its context. +0.037 over `ens-06` (+0.010 to +0.072), but origin 2026-10-01 carries most of it: without that origin +0.012 (+0.002 to +0.024), 24 held-out origins +0.014 (+0.002 to +0.027). Daily closes of NVDA, AMD, CRWV, NBIS in the context (`data/ext_market_v1.csv`): no gain on 627 pilot cells. Not in the submission: found after SPEC3 | +0.354 | +0.314 / +0.306 / +0.390 |
| `ens-06` | **candidate 2**: quantile average of `fm2-20` and `llm2-03` | **+0.316** | +0.217 / +0.272 / +0.367 |

`fm2-20` against `fm2-17`: +0.015, 95 % interval +0.008 to +0.024 (bootstrap over origins). `llm2-03` against
`ens-05`: +0.015, +0.008 to +0.024 (series-origin blocks). Other adjuster models on the 6 pilot origins (627
cells, `ens-05` +0.251): `claude-haiku-5-5` +0.255, `claude-sonnet-5-5` +0.248, `claude-fable-5-2` +0.265; an
echo control returned `ens-05` unchanged on 627 of 627 cells. LLM arm through SPEC3: $33.79 (Anthropic). Afterwards: OpenAI $55.33, Anthropic $41.30 in all.

Seed and checkpoint noise is about +-0.01 pooled (`ft-08` step curve, `pfn-02` checkpoints), so the averages
between +0.292 and +0.299 are not separated.

**Locked origins (`specs/SPEC2.md`, `results/spec2/locked-01/`).** The candidate was fixed in SPEC2 before this
run. On the six origins 2026-10-31 to 2026-11-05 (357 cells: 209 at 1 day, 148 at 3 days; no forecaster was run
or tuned on them after SPEC1's single run): candidate **+0.252** pooled against +0.089 for `last_value_empirical`;
difference +0.164, 95 % interval +0.079 to +0.249 (bootstrap over 37 series); better on 26 series, worse on 11,
better on 6 of 6 origins. 1 day: +0.184 against +0.123 (difference +0.061, +0.018 to +0.118). 3 days: +0.305
against +0.063 (difference +0.243, +0.108 to +0.354). Inside [q10, q90]: 0.85 and 0.80 (target 0.80). Members
alone: `fm2-17` +0.270, `sim2-15` +0.215. The 7-day horizon has no truth on these origins.

**Locked origins, second look (`specs/SPEC3.md`, `results/spec3/locked-01/`).** Candidate 2 was fixed in SPEC3
before this run; it is the second use of these origins and one scoring run. Candidate 2 **+0.283** against
candidate 1 +0.252: difference +0.030, 95 % interval +0.016 to +0.052 (bootstrap over 37 series); better on 27
series, worse on 8, better on 5 of 6 origins. 1 day +0.217 against +0.184; 3 days +0.333 against +0.305. Inside
[q10, q90]: 0.85. By the rule written in SPEC3, candidate 2 replaced candidate 1 in the submission. Members:
A (`fm2-20`) alone +0.298 against `fm2-17` +0.270 (difference +0.028, +0.008 to +0.068; H2 held); B (the LLM
adjustment of candidate 1) alone +0.256 against +0.252 (difference +0.004, -0.024 to +0.027, better on 8 series
and worse on 24: H3 not confirmed). A alone scored above candidate 2 on these origins; the submission stays the
average fixed in SPEC3, because choosing the member after seeing this run would be a choice made on the test set.

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

## Public page

https://gpu.invariant.team shows the main results. Source: `site/` (`index.html` reads `data.json`; `build.py` writes
`data.json` (generated, not committed) from `site/content.json`, `results/ledger/`, the locked metrics and the submission CSV, so a new ledger
entry appears without editing the page). Publish after every new result: `studies/gpuprice/site/deploy.sh`
(CloudFormation stack `gpuprice-site`, AWS profile `fuelos`, `site/template.yaml`: a private S3 bucket behind CloudFront).
