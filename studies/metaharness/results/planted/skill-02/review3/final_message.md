I ran the review. The work is still re-cutting the same 500 stored answers instead of testing the mission's point 3, and this review's one change cut the time per gapmap job from 84.8 s to 74.3 s.

**Previous entry's three checks**
- **Point-3 route or another batch?** Another batch: the tokens batch ran next, a third look at the same rows. No route that uses no reward was tried.
- **Subject cell failures:** none. All 6 tokens jobs finished.
- **bench-rng:** still in `queue.json`. It ran a third time and gave 37,576, then 42,645, then 39,367 draws/s for PCG64 on the same code. It decides nothing for the mission.

**Direction.** None of the 6 runs since the last entry tests point 3 ("the cheapest route… that uses no reward, at equal generated tokens"). The tokens result does show where that route has room:
- In the three shortest quarters of the cued base's answers, RL uses about 1,070 to 2,000 more tokens per problem.
- In the longest quarter, RL uses 1,658 fewer.

So at equal tokens, the base could afford roughly one more sample on its shorter answers. The next planned batch is `tokens_both_right`, a fourth re-cut. The better next step is a 2-sample vote or a restart on those shorter answers, at RL's token count (Day 1 item 3).

**Turnaround.** In the last 0.5 h: 25 jobs, 2 failed, 2.5 of 28.9 container minutes lost to the failures, no queue wait. Running the jobs is the slowest stage, at a median of 4 minutes per work item. Each job spent 21 of its 66 s installing numpy, scipy, pandas and matplotlib, but `cell.py` only imports numpy.

**Change (deleting a step).** `run_cell.sh` now installs only `numpy==2.5.4` (commit 85c2520, pushed). I ran the same cell once before and once after the change:

| measure | before | after |
|---|---|---|
| wall seconds per cell | 84.8 | 74.3 (−12%) |
| install seconds inside the job | 21 | 7 |
| tokens overall (must not change) | 760.948 [495.14, 1019.8781] | identical |

That is one run on each side, so it is not a proven gain.

**Failures.** No new ones. `gpu.py` still refuses to submit while the tree has an untracked file; I kept the review folder outside the repo during the two runs to get past it. The fix for that is still listed in `meta/FAILURES.md`. Still carried, not done: removing bench-rng from `queue.json`, and the 1,500,000 resamples per cell, which cost 32–43 s of every job and are your requirement 2 in the spec.

The entry is at the top of `meta/dana.md`, with its raw outputs (`cycle.txt`, `before.txt`, `after.txt`) in `meta/reviews/dana/20261115-0430/`. Both commits are pushed to `dana/gapmap`.