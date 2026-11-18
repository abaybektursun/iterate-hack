# Do the strategies matter for a frontier model? gpt-6.2-sol on ahc014 (written before the runs, 2026-11-17)

Every strategy comparison of this study used gpt-5.4-mini or SWE-2. In label/pilot-01 one call of gpt-6.2-sol
reached 0.75-0.77 on ahc014 from two programs at 0.55-0.57.

- Arms: single, fnf (K=4, forks at 0/33/66 %), forget (team of 4, flush every 10). 40 submissions, 1 seed, the
  usual starter (0.2217), `jobs/run_strategy.py` unchanged. Runs in `runs/explore/ahc014/sol62-01`.
- Measures: best validation score after each submission, final best, held-out test score of the best program,
  the submission at which each arm last improved, USD.
- Prediction (the anchoring account): the single chat stops improving before submission 20 and ends at least 0.02
  below the better of fnf and forget.
- Refuted (the bitter-lesson account) if the single chat ends within 0.02 of, or above, both flush arms, or still
  sets a new best after submission 30.
- Limits: 1 seed per arm; SWE-2 single runs on this task ranged 0.41-0.64 over 6 seeds, so a gap of a few
  hundredths decides nothing and only a large gap or a clear plateau is informative.
- Cost estimate: about 15 USD (the single chat is the most expensive: its context grows every turn).
