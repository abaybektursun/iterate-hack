# SPEC1: simulate the median from the listings (written 2026-11-14, before the run)

Question: does a forecast built from the individual posted prices beat the strongest starter baseline
(`last_value_empirical`, +0.126 pooled skill on `results/baselines/event37-01`)?

Each target is the median of the day's listings (rows of `rental_observations`, key provider, region, SKU). A
recompute from the rows matches `daily_statistics.csv` on all 3,293 series-days of the event set.

Method (`jobs/sim_median.py`), for one series, origin t, horizon h, using rows dated on or before t only:
1. Listings and prices on the last observed day on or before t.
2. Every historical window (s, s+h) with both days observed and s+h <= t gives, for the listings present at s,
   the outcome of each (log price change, or exit), and the entrants at s+h (price as a ratio to the median at s).
3. 2,000 draws: pick one window; give every current listing an outcome drawn with replacement from that window's
   outcomes; add that window's number of entrants at ratios drawn from it; take the median.
4. q10, q50, q90 of the 2,000 medians.
Drawing a whole window keeps the days on which many listings move together.

Scope: the 33 fastgpu_daily and gpurentalprices series. The 4 afhubbard series (272 rows per provider and day, 1
to 3 snapshots a day) keep `last_value_empirical`.

Scoring: the starter `scorer.py`, same 37 series, 30 daily origins 2026-10-01 to 2026-10-30, horizons 1, 3, 7
(3,109 cells), skill against flat last value.

Hypothesis: pooled skill above +0.126. Refuted if it is +0.126 or lower. Also reported: share of truths inside
[q10, q90] (baseline 0.55 to 0.69, target 0.80).

Control: the same draws with step 3 replaced by "apply the window's change of the median itself", which removes
the listing-level state and should fall back to about the baseline.
