# Agent-count sweep for assigned methods on circles26 (written before the runs, 2026-11-15 05:10 UTC)

Objection to answer: "a swarm already fixes a stuck agent". Companion of `ksweep-ahc014-swe2.md` (fnf vs parallel,
SWE-2, ahc014) for our arm on the task where it won (assign-01).

- Arms: parallel (K independent chats, best of all) and fnf_assign (forks at 0/33/66 %, K fresh branches per fork,
  one listed method per branch, list by gpt-5.4-mini). K in {2, 4, 8}. 40 submissions in every cell; each fork
  costs 8 submissions at every K (--branch-steps 4, 2, 1), as in the ahc014 sweep.
- Model gpt-5.4-mini, task circles26, numpy/scipy available, 1 seed per cell.
- Runs: 5 new in `runs/explore/circles26/ksweep-01` (parallel K=2, 4, 8; fnf_assign K=2, 8). fnf_assign K=4 is
  assign-01/assign_mini-s0 (2.628). The earlier parallel K=4 runs (main-01) had no numpy, so K=4 is rerun.
- Measure: final best validation score; starter 2.54138.
- Prediction: fnf_assign > parallel at K = 2, 4 and 8, and parallel stays at or below the starter at every K.
  Refuted if parallel matches or beats fnf_assign at any K.
- Second measure, no new runs (`analysis/best_of_k.py`): the expected best of K independent stored runs of a
  baseline arm, against the mean of one run of another arm (how many baseline runs one run is worth).
- Limits: 1 seed per cell; at K=8 a branch gets 1 submission, so that cell also tests branch depth; a list of 8
  methods may be worse than a list of 4.
- Cost: about 2.4 USD.
