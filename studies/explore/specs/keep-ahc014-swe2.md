# Fork without flush at 2 and 8 agents: is the win over a swarm from the flush or from sharing? (written before the runs, 2026-11-15 09:05 UTC)

swe2-ksweep-02: fnf beats parallel at K = 2 and 8 (new cells alone p = 0.010). parallel agents never see each
other's programs; fnf restarts every branch from the best program AND gives it a fresh chat. fnf_keep does the
first without the second: same forks (0/33/66 %), same K, same submissions per branch, each branch starts from the
best program but keeps the leader's chat history (the opening fork is identical to fnf: there is no history yet).

- New runs: fnf_keep at K=2 (--branch-steps 4) and K=8 (--branch-steps 1), seeds 1-3, 6 runs, budget 40,
  devin:swe-2-medium, ahc014, in runs/explore/ahc014/swe2-keep-01. Compared with the fnf and parallel runs of
  swe2-ksweep-02 (same K, seeds, budget; already seen: parallel 0.528 / 0.575, fnf 0.612 / 0.605).
- Measure: final best validation score per run. Test: one-sided stratified permutation over K = 2 and 8 (labels
  permuted within K, 400 splits, smallest p 0.0025), as in analysis/ksweep_test.py.
- Test 1, sharing: fnf_keep > parallel. Prediction: p < 0.05 (sharing the best program alone beats a swarm).
- Test 2, flush: fnf > fnf_keep. Prediction: p >= 0.05 (the fresh chat adds nothing detectable here; in swe2-01,
  one seed at K=4, fnf_keep 0.613 vs fnf 0.625).
- Reading: test 1 passes and test 2 does not -> the win over a swarm is from sharing the best program.
  Test 2 passes -> the flush matters. Neither passes -> undecided at this size; report the share
  (mean fnf_keep - mean parallel) / (mean fnf - mean parallel) per K either way.
- Also reported: SD and worst run per cell, held-out test scores (invalid = 0).
- Limits: 3 runs per cell, one task, one model; a gap below about 0.05 between fnf and fnf_keep cannot be seen.
- Cost: 0 USD (free model); about 1 hour with rate-limit waits.
