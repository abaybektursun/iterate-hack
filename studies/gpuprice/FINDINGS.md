# Findings: forecast the listings, not the median

Track 2, Pacific, "An AI Scientist for GPU Value". Direction C. Every number below has its artifact path in
`README.md`; pooled skill is 1 - pinball loss / pinball loss of the flat last value, quantiles 0.1, 0.5, 0.9.

## Question

A posted GPU rental "price" in the pack is the daily median over 3 to 17 providers' rate cards. Is the median
better forecast as a series of its own, or as a function of the individual listings behind it?

## Method

An agent swarm ran the work: each arm stated a hypothesis and the number that would refute it, ran it, and wrote
one ledger entry per iteration (`results/ledger/`, 87 entries, failures included). Arms were scored on 30
development origins (2026-10-01 to 2026-10-30, 3,109 cells, 37 series, horizons 1, 3, 7 days). Six later origins
(2026-10-31 to 2026-11-05) were locked: the candidate was written down in `specs/SPEC2.md` first and then run on
them once.

The submitted forecast (`results/submission/forecast_2026-11-06.csv`, one command: `jobs/reproduce.sh`) is the
quantile average of two forecasters that both work on the listings:

1. `amazon/chronos-2`, zero-shot, on each listing's price series; independent draws from the per-listing
   quantile functions; the median over the listings per draw. Three rules on top: at 1 day a listing moves only
   at its own historical change rate; Scaleway listings follow the ECB EUR/USD rate; listings seen before return
   at their posted price.
2. A simulator with no model: each listing replays its own past h-day outcomes (change, exit), recent windows
   weighted more, with entrants.

Target declared: 37 `daily_statistics` series (`data/event_series_v1.csv`), each one collector, instrument class,
GPU model and pricing tier; posted prices, none paid. External data: ECB EUR/USD reference rates to 2026-11-06
(the brief allows data dated on or before 6 November; the pack's DATA.md says before the origin: the 7 and 9
November Scaleway forecasts use the 6 November rate).

## Results

| | Development, 3,109 cells | Locked origins, 357 cells (1 and 3 days) |
|---|---|---|
| `last_value_empirical` (strongest starter baseline) | +0.126 | +0.089 |
| `drift` (the brief's baseline) | +0.114 | |
| Submitted candidate | +0.298 | **+0.252** |

Locked origins: difference to the baseline +0.164, 95 % interval +0.079 to +0.249 (bootstrap over the 37 series);
better on 26 series, worse on 11; better on 6 of 6 origins. 1 day +0.184 against +0.123; 3 days +0.305 against
+0.063. Share of truths inside [q10, q90]: 0.85 and 0.80 (target 0.80). The 7-day horizon has no truth on the
locked origins; its development number is +0.347 against +0.127.

Limits. The origins overlap, so cells are not independent; the interval resamples series only. Seed and
checkpoint noise is about +-0.01 pooled. The history is 60 to 234 days. One marketplace series with 3 listings
that turn over daily is forecast poorly by every listing-level method.

## What the system learned across iterations

1. **The level of the forecast matters more than the model.** `amazon/chronos-2` on the 37 median series: +0.132.
   The same weights on each listing, with the median computed over draws: +0.272. TiRex-2 (+0.137 to +0.226) and
   TabPFN (+0.103 to +0.192) move the same way. A median of sticky prices has a discrete set of next values (the
   neighbouring listings' prices), which a model of the median series cannot see.
2. **A first version did not survive unseen origins.** The first listing simulator scored +0.197 in development
   and then lost to the baseline at 1 day on the locked origins (+0.055 against +0.123). The fix came from the
   listings: each listing replays its own history (+0.223), and entrants return at their posted price (+0.267).
3. **Providers are not alike.** To 30 September, 80 % of listings never change. Verda moves on 37 to 48 % of days
   in 1 % steps, 91 % upward. Scaleway's USD price is a fixed EUR price times the previous business day's ECB
   rate (exact on 95 % of days). CoreWeave, Hyperstack, Modal and Together did not change once.
4. **Synthetic prices teach the model more than the real ones.** A LoRA of Chronos-2 on 8,000 simulated
   step-function series, no real price: +0.295 and +0.292 on two seeds against +0.271 zero-shot. The same LoRA on
   the real listings: +0.252; full fine-tune +0.241. A 4.8M-parameter network trained from scratch on simulated
   listings only: +0.267, level with the 120M-parameter model. Neither is in the candidate: in the average the
   gain is +0.001.
5. **Negative results.** An 80B open-weights LLM reading the whole provider table repeats the last value in 90 %
   of its samples (+0.015 against +0.264 for the ensemble on the same 92 cells); asked to reason first it reads
   the table correctly and reaches +0.128, level with the starter baseline (+0.106). Rolling calibration multipliers,
   conformal-style widening, longer context (+30 days), cross-collector covariates and a third ensemble member
   each gave nothing or lost.

## For someone pricing GPU capacity

- A change in a posted median over a week is mostly a change in which providers are listed and which of the
  middle two or three reprice, not a market-wide move. Read the listing table, not the median.
- One-week uncertainty of the median, as the width of [q10, q90] relative to the price in the submitted forecast:
  median 5.9 %, a quarter of the series at 10 % or more.
- Rate cards are not hedged against currency: a EUR-priced provider moves the USD median with the exchange rate.

Not addressed: resale values and the 2 to 3 year view.
