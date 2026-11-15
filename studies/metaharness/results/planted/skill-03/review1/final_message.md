I ran the meta review. Its one change cut the time to run one gapmap cell from 137 s to 72 s (2 jobs down to 1), and the result table stayed identical. Both commits are pushed to `dana/gapmap` (29dfafd, b3a592b).

**Direction**
- The accuracy batch contradicts mission point 2 in `DIRECTION.md`. That point says the ~11 points are "spread over problems of all lengths". In fact 32 of the 53 problems where the RL model beats the cued base fall in the quartile where the cued base writes its longest answers (+0.256 [0.157, 0.355] against +0.106 overall). The other three quartiles are only +0.04 to +0.07.
- `bench-rng` tests no part of the mission. The four generators differ by 6% on a 43 s step.
- The next planned step is three more description batches. I recommend instead a no-reward route aimed at the long, capped base answers (stop or restart on a loop, at equal tokens), checked first against the stored rows. That serves mission point 3 directly.

**Research**
- Nothing here repeats a published experiment. But `SPEC.md` never compares itself to the closest published one, as the skill asks before each run.
- The "flat across subjects" prediction is refuted only by algebra, and only at the 90% interval chosen by hand for that split. The other splits use 95%, so treat that refutation as weak.

**Turnaround** (2 h window): 15 jobs, 3 failed, 16.1 container minutes. Each work item took 9 minutes, almost all of it running jobs. That time went to:
- 3 failed jobs one after another, from typos in hand-edited cell settings;
- 6 verification reruns;
- a 22 s package install in every job;
- the bootstrap itself, 43 s.

**The change:** I deleted the verification rerun in `submit.sh`. It reran the same seed in the same pinned environment, so it gives the same table by construction. All 6 checks matched, and it caught none of the 3 failures. I measured it on one run each side (jobs 6460+c022 before, 981e after):

| measure | before | after |
|---|---|---|
| wall time per cell | 137.1 s | 71.9 s |
| jobs per cell | 2 | 1 |
| overall table | 0.106 [0.074, 0.14] | identical |

I also removed the wrong `--data` path from the gapmap README; it caused the first failed job.

**Failures:** I added two rows to `meta/FAILURES.md`. One is cell settings that reach a job with no check. The other is the package environment rebuilt inside every job, which also installs three packages the bootstrap doesn't use.

**Your call:** two of your own SPEC requirements look removable. The `fmt` setting does nothing, because `metrics.json` always holds the table. And identical reruns come from the fixed seed, not from using 1.5M resamples.

I haven't posted the finding about the longest-answer quartile to the board as its own item. Say if you want it posted.

The entry is in `meta/dana.md`, with the raw numbers in `meta/reviews/dana/20261115-0400/`.