# Spread test: are single runs less reliable than fnf? (written before the runs, 2026-11-15 04:40 UTC)

Lead from the seeds test (ahc014/swe2-seeds-01, found after looking): single runs spread 3.5x wider than fnf
(SD 0.082 vs 0.024, Brown-Forsythe permutation p = 0.042), worst run 0.409 vs 0.558. Those 12 runs produced the
hypothesis, so they are NOT used to test it. This test uses fresh runs only.

- Arms: single, fnf. Model devin:swe-2-medium, task ahc014, budget 40, code as in swe2-seeds-01.
- Seeds 6-11, 6 runs per arm, in runs/explore/ahc014/swe2-spread-01.
- Primary test: spread of the final best validation score, single > fnf, one-sided Brown-Forsythe permutation
  (absolute deviations from each arm's median; all 924 splits). Prediction: p < 0.05.
  Refuted if p >= 0.05 or the single SD is not above the fnf SD.
- Secondary (reported either way): worst run per arm; share of runs below 0.50; means and the rank-sum test
  fnf > single; held-out test scores (cases 6-10, invalid = 0); for any single run below 0.50, whether it kept
  one approach from early on (move-type counts on case 1, as for single-s2).
- Cost: 0 USD (free model); laptop kept awake with caffeinate.
