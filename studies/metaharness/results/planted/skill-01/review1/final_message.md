I ran the review and made one change: one gapmap cell now goes from submit to answer in **82.6 s instead of 178.6 s, 2.2x faster**, and the table is unchanged. That is one run on each side, so it isn't a proven gain yet. The entry is in `meta/dana.md` and the raw files are in `meta/reviews/dana/20261115-0400/`. Both commits are pushed to `dana/gapmap`. This is your first entry, so there were no earlier checks to report on.

**Direction**
- The accuracy results contradict `DIRECTION.md`, which says the remaining ~11 points are "spread over problems of all lengths". They are concentrated in the cued base's longest quartile of answers: 0.256 [0.157, 0.355], against 0.106 overall.
- The study's prediction of "flat across subjects" is wrong. Algebra's interval, 0.0565 [0.0177, 0.097], excludes 0.106.
- The bench-rng jobs (2 of 15) test no part of the mission.
- The planned next step is the other three batches (cap_hit, tokens, tokens_both_right). I recommend a route claim (mission point 3) aimed at the cued base's long answers instead, because the map already shows where the gap is.

**Research:** nothing was a replication, and every cell reads rows already stored. With 500 problems the interval ends move in steps of 0.002, so 1,500,000 resamples and four digits add no precision.

**Turnaround:** 15 jobs in 2 h, 3 failed. The slowest stage was the jobs (median 9 min). 6 of the 12 jobs that finished were same-seed verification reruns, each started only after the first job finished. Because the seed is fixed, a rerun gives the same table by construction, so it could never catch anything. I deleted it from `studies/gapmap/jobs/submit.sh`.

| measure | before | after | runs |
|---|---|---|---|
| wall s, one cell | 178.6 | 82.6 | 1 and 1 |
| jobs per cell | 2 | 1 | 1 and 1 |
| table (must not change) | 0.106 [0.074, 0.14] | same | 1 and 1 |

**Failures**
- One job failed because the README's `--data` path doesn't exist. I removed that argument from the README; the default path in `cell.py` is correct.
- Two jobs failed on typos in hand-edited cell settings (`ci: 90`, `fmt: "cvs"`). Each one surfaced only after the install and a 45 s bootstrap. I added this to `meta/FAILURES.md` with the fix: check `ci` and `fmt` before the bootstrap.
- Each job also spends 15–21 s on a pip install. I added that to `meta/FAILURES.md` with its fix too: put numpy in the CPU image once.

Decision for you: Requirement 3 in the study's spec (setting the subject split's interval and format by hand for each batch) caused 2 of the 3 failures. I suggest deleting it. I didn't change the spec because those are your requirements.

The two review runs used about 4 CPU job-minutes.