# Forecast run 01: theories forecast the open GPU work before it reports

Written before the run (2026-11-15 14:45 UTC, abaybektursun). Code: `lib/forecast.py` with prompts
`lib/prompts/forecast_targets.md`, `forecast.md`, `forecast_score.md`; it imports the headless job runner and the
log density from `lib/round.py` (version 7.1) and uses the models round.py gives its jobs.

## Why

Seven rounds tested theories on stored per-problem rows. No theory stands, and round 07's tests used groups of 6 to
55 problems, too small to separate theories (`results/engine/round-07/`, board result-5115c5). The team's open GPU
work items will report new numbers on 136 to 500 problems. Each theory, and two readers with no theory, forecast those
numbers before they post. When they post, each forecast is scored against the readers.

## What runs

```
uv run studies/theory/lib/forecast.py make studies/theory/results/forecast/run-01
uv run studies/theory/lib/forecast.py score studies/theory/results/forecast/run-01
```

`make`:

1. Reads every open `work` item with its comments (`board.py show`), and every `result` and `knowledge` item on the
   board up to now (as round.py's `split` reads them).
2. One headless job (`forecast_targets`) turns the open items into targets: one per number an item says it will
   report, with the item id, the exact cell (model, prompt, set, n, sampling, samples, grader), the unit and a quote
   of the item text. No target for an item with no countable outcome, or for a number already stated in the item,
   its comments or any posted result. Code checks that each quote is in its item's text.
3. Forecasters, each a blind headless job with the board items and the targets, give value, low, high (90 %
   interval) and one line of reason per target:
   - `reader-1`, `reader-2`: no theory.
   - one job per theory not refuted in round 07 (`metrics_v4.json`), at most 6: the survivor r5-m03-rival first,
     then the rest by total gain, highest first. At this writing: r5-m03-rival, r6-account-rival, r6-m06, r7-m05,
     r7-m08, r7-m11 (r7-m07 and r7-m09 are cut by the cap). Each gets its theory's file and must derive each number
     from the theory or answer "theory says nothing" for that target.
4. Writes `targets.json`, `forecasts.json`, `forecasts.md`, `run.json` (commit, command, UTC time). Fails if the
   folder exists.

`score`: one headless job reads the board items posted after the run's time and gives, per target, the measured value
with the item id and a quote, or "not posted yet". Code scores each forecast by the engine's rule: a normal density
with sd = max((high - low) / 3.29, 0.01 * max(|value|, 1)), gain = log density of the forecast minus log density of
the equal mixture of the two readers, at the measured value, clipped to [-3, 3] nats. Writes `scores.json` and
`scores.md`. A target whose measured value is outside every forecaster's interval is flagged.

## Hypotheses

- F1 (the open work gives targets): `make` writes at least 8 targets from the open work items. Refuted at 7 or fewer.
- F2 (a theory forecasts better than no theory): at least one theory forecaster has a mean gain above 0 nats over at
  least 5 scored targets. Refuted when every theory forecaster with 5 or more scored targets has a mean gain of 0 or
  below. I expect it to be refuted: no theory passed its offline tests in rounds 06 and 07. Not decided while no
  theory forecaster has 5 scored targets.
- F3 (a surprise): at least one measured value falls outside every forecaster's 90 % interval. Refuted when all
  scored targets fall inside at least one interval, once at least 5 targets are scored.

## Limits

- All forecasters read the same board text, so their errors are correlated; the two readers are one model run twice.
- One run, one set of targets. A gain on 5 to 10 targets is weak evidence.
- A theory forecaster that answers "theory says nothing" on a target is not scored on it.
- Targets come from one model's reading of the work items; a target whose cell does not match what the item later
  reports is scored "not posted yet" by the score job and stays unscored.
- The forecasts are written while some jobs run. A target whose result posts before `make` finishes is not a
  forecast: `score` only reads items posted after the run's time, so such a target stays unscored.
