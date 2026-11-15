I made one change: `studies/gapmap/jobs/submit.sh` now launches each cell once instead of twice. That should roughly halve the wall time of each remaining batch. It's committed and pushed as `f6cdc45` on `dana/gapmap`. I only syntax-checked it with `bash -n`; it hasn't run a job yet.

**How the last hour went:** two batches (accuracy and cap_hit) finished in about 6–8 minutes each. That was 12 cells and 24 jobs on the CPU class.

**What I changed and why:** after each job, `submit.sh` ran a second job with the same seed and checked that the two tables matched. That check can't fail: the bootstrap gives the same result every time with seed 0 (SPEC, Requirement 2). In the `runs/` folder, all 10 split cells repeated their tables exactly. So the rerun doubled the number of jobs and each cell's wall time without being able to catch anything. A teammate can still check any table by rerunning the commit recorded in `run.json`.

**Expected gain:** each batch was about 4 rounds of jobs at roughly 75 s each (environment ~20 s plus bootstrap ~40 s). Now it should be 2 rounds, about 2.5 minutes saved per batch, with half the job count. That matters for the two batches still to run, `tokens` and `tokens_both_right`.

**Other problems I noticed but didn't fix:**
- **bench-rng:** this extra cell runs in every batch even though it isn't in the SPEC. Its timings vary a lot, about 37k/s in one batch and 42k/s in the next. Each batch posts it as another board result, which clutters the board. Removing it from `queue.json` `extras` would be the next cleanup.
- **subject cell:** its settings get edited by hand in two separate commits each batch, and it launches alone before the other cells. Launching all six cells together would save one more round per batch.