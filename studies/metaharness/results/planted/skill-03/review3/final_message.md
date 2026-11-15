I ran the meta review. The one change cuts each gapmap cell job from 66 s to 50 s (1 run on each side) with the same table. The entry is in `meta/dana.md`, the raw files are in `meta/reviews/dana/20261115-0422/`, and both commits are pushed.

**Direction:** the work is still answering follow-up questions about the last result instead of working on the mission.
- The tokens batch found that RL generates 761 more tokens per problem than the cued base (interval 495 to 1,020).
- The exception is the base's longest quartile, where RL uses 1,658 fewer. That is where the base hits the 16,384 cap.
- So stopping the base's looping answers there is a no-reward route to equal tokens, which is what mission point 3 asks for. Nobody has claimed it.
- The next planned run is the tokens_both_right batch instead.
- bench-rng tested nothing in the mission and ran a 3rd time. Its rates move more between runs than between generators, so it measures noise.

**Last entry's checks:**
- 0 failed cell jobs this time.
- The subject cell's settings were edited by hand again (table format "csv", 2 digits). The pre-launch check passes them because they are legal values. But 2 digits goes against the spec's own requirement of 4 digits.

**Turnaround:** the slowest stage is still the jobs themselves (median 4 min, down from 5). Each job spent 18-22 s installing scipy, pandas and matplotlib, which the code never imports; it only uses numpy. I removed them from `studies/gapmap/jobs/run_cell.sh` and reran the same cell:

| measure | before | after |
|---|---|---|
| install time, tokens overall | 22 s | 7 s |
| job time, start to done | 66 s | 50 s |
| overall table (must not change) | 760.948 [495.14, 1019.8781] | identical |

**Two things to know:**
- `gpu.py submit` refuses to launch while any files are uncommitted. To run the "after" job I had to stash the review folder for a moment, so the change and the review went in as two commits rather than the one the skill asks for.
- These choices are yours, and I didn't change any of them:
  - whether to drop bench-rng, the table-format setting and the per-batch digits setting;
  - whether to put numpy in the runner image so the remaining 7 s install goes away (still listed in `meta/FAILURES.md`).