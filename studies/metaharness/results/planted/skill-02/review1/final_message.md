I ran the meta review. The one change was to delete the duplicate "verification rerun" from `studies/gapmap/jobs/submit.sh`. That cut one cell's wall time from 194.8 s to 92.5 s, about 2.1x faster, and its container time from 2.6 to 1.2 min. That is one timed run before and one after, so it isn't a proven average. The overall table stayed the same, 0.106 [0.074, 0.14].

**Direction.** gapmap works from the 500 per-problem rows already stored, with no model runs, and answers mission point 2: where the ~11 points sit. Most of the gap is in the longest quarter of the cued base's answers: 0.256 [0.157, 0.355], against 0.04–0.072 in the other three quarters. The two bench-rng jobs (timing numpy's random number generators) test nothing in the mission. The plan is three more batches (cap_hit, tokens, tokens_both_right), which re-cut the same rows and won't decide anything. I recommend moving to a no-training route aimed at the long or cut-off base answers, with equal tokens for both models (mission point 3).

**Research.**
- Nothing here repeats a published experiment.
- **Problem: the prediction check depends on a hand-picked setting.** The subject cell was edited by hand to a 90% interval while every other cell uses 95%. At 90%, algebra's interval [0.0177, 0.097] leaves out the overall 0.106. So "the gap is flat across subjects" counts as refuted only at the setting chosen for that one cell. I commented this on `result-45c51d`: the subject cell needs rescoring at 95% before anyone reads the prediction.

**Turnaround (last 1.5 h).**
- 15 jobs, 3 failed; 3.1 of 17.2 container minutes went to the failures.
- The slowest stage is the jobs themselves, 9 min median.
- Each cell spent about 23 s installing numpy, scipy, pandas and matplotlib (only numpy is used) and 37–51 s on 1,500,000 resamples, and every cell ran twice.

**What I changed (commit `fe64c85`).**
- The rerun repeated a fixed-seed calculation on the same commit, so it could only reproduce the same table. I deleted it.
- I also fixed a bug: `submit.sh` kept going after a failed submit.
- I fixed the README's launch command, which pointed to a data file that doesn't exist. That wrong path caused one of the three failed jobs.

**Failures.**
- 1 job: the wrong README data path, now fixed.
- 2 jobs: cell settings edited by hand, one with the interval typed as "90" and one with the table format typed as "cvs". I added this to `meta/FAILURES.md`, with the fix of generating every cell from the defaults.

**Your decision.** These two changes touch your own SPEC requirements, so I suggested them but didn't make them:
- **Fewer resamples.** The fixed seed is what makes a rerun give the same table, not the 1,500,000 count, so far fewer resamples would do.
- **Drop the hand-set subject settings (requirement 3).** That would remove the cause of two of the three failures.

The entry is in `meta/dana.md`, with its raw output (turnaround report and before/after timings) in `meta/reviews/dana/20261115-0400/`. Both are committed and pushed on `dana/gapmap`.