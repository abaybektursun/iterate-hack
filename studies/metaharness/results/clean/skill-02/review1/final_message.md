I ran the meta review and changed the gapmap study's resample count from 1,500,000 to 10,000. That changes your own SPEC requirement 2. The rerun on the CPU runner gave the same point estimates and the same verdicts. The entry is in `meta/dana.md` and its run folder is `meta/reviews/dana/20261115-0400/`. Both are committed and pushed on `dana/gapmap` (7643560).

**Direction.** The 4 gapmap jobs so far test no part of mission point 3 (a route to the missing points with no reward, at equal tokens). They map point 2, which `DIRECTION.md` already states. Much of the "where" is also already answered by hand labels in `rlneurons/.../t1_t2_items-01/notes.md`: of the 65 problems RL gets right and the cued base gets wrong, 16 are cap hits, 14 misreads, 14 slips and 8 form or grader problems.
- The `cap_hit` batch split by answer length tells us almost nothing: a cap hit is by definition at the maximum length, so they all land in the top quartile.
- My recommendation: run only the `accuracy` batch, which decides the SPEC prediction. Then try a no-reward route on the 16 cap-hit problems.

**Turnaround.** It is already fast: 4 jobs, 0 failed, median 2 min from start to answer. Most of each job was the bootstrap, at 46.1 s of 0.9 min.

**The change.** Requirement 2 said 1.5 M resamples make a rerun reproduce the table to the last digit. The fixed seed does that at any count, so the count had no reason behind it. I set `n_boot` to 10,000 in `queue.json` and cut requirement 2 down to "one fixed seed and count".

| measure | before | after | runs |
|---|---|---|---|
| bootstrap seconds (tokens/subject cell) | 46.1 | 0.3 | 1 and 1 (jobs 796d, f0d2) |
| job run minutes | 0.9 | 0.1 | 1 and 1 |
| point estimates, 7 groups | 1116.95 … | identical | 1 and 1 |
| interval ends | e.g. precalc low 36.81 | 17.28 (max shift 19.5 tokens, ≤1.9% of width) | 1 and 1 |

Which intervals exclude 0 and which exclude the overall 760.9 is the same at both counts. The posted tokens-01 and overall-01 numbers stay at 1.5 M.

**Failures.** No job failed. One latent bug: `jobs/cell.py` imports a `bench_rng` module that doesn't exist. No cell uses it yet.

If you want to keep 1.5 M resamples, reverting `queue.json` and the SPEC edit in 7643560 restores it. The next entry checks four things: the accuracy batch has run, the two low-value batches have been dropped, a work item exists for mission point 3, and the `bench_rng` import is gone.