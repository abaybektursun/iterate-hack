# Agent-count sweep: does fnf beat a parallel swarm at every number of agents? (written before the runs, 2026-11-15 04:50 UTC)

Objection to answer: "a single agent getting stuck is expected; that is why people run swarms." So the fair
baseline for fnf with K branches is a swarm of K independent agents at the same total number of submissions.

- Arms: parallel (K independent chats, round robin, best of all) and fnf (forks at 0/33/66 %, K fresh
  branches per fork). K in {2, 4, 8}. Total budget 40 submissions in every cell. Each fork costs 8 submissions
  at every K: --branch-steps 4 (K=2), 2 (K=4, the default), 1 (K=8); so fnf spends 24 on branches and 16 on
  the leader at every K. K=1 parallel is the single arm (reported for reference, not in the test).
- Model devin:swe-2-medium, task ahc014, validation cases 1-5.
- Runs: K=2 and K=8 are new, seeds 1-3 per cell (12 runs), in runs/explore/ahc014/swe2-ksweep-01. K=4 uses
  the 6 + 6 runs already made (swe2-01 seed 0, swe2-seeds-01 seeds 1-5); their numbers are known:
  fnf 0.592 vs parallel 0.577.
- Measure: final best validation score per run; gap(K) = mean fnf - mean parallel.
- Test: one-sided stratified permutation test, labels permuted within each K, statistic = sum over K of
  gap(K), exact (20 x 924 x 20 splits). Prediction: gap > 0 at K = 2, 4 and 8, and pooled p < 0.05.
  Refuted if any gap(K) <= 0 or pooled p >= 0.05. Since K=4 is already seen, also report the test on the new
  cells alone (K=2 and K=8, 400 splits, smallest possible p = 0.0025).
- Also reported: gap as a function of K (does a larger swarm close it?), SD and worst run per cell, held-out
  test scores (cases 6-10, invalid = 0).
- Limits: three values of K, one task, one model; 3 runs per new cell detects only a large gap. It cannot
  show the order for every N, only that it does or does not hold at 2, 4, 8.
- Cost: 0 USD (free model).

Note added after the runs (2026-11-15 08:40 UTC): `swe2-ksweep-01` was killed at 0 tries (the spread test before
it had died on Devin's rate limit). The sweep ran once, in `runs/explore/ahc014/swe2-ksweep-02`, with commit
a60ebc4. Result: `results/ahc014/swe2-ksweep-02/summary.json`.
