# Meta review: dana

## 2026-11-15 04:08 UTC (session start, after work-ea7a31 and work-404f9b closed) meta/reviews/dana/20261115-0400/

- Last entry's checks: none, first entry of dana.
- Direction: mission "how much of a published RL gain an untrained base model reaches with no training", point 2 "about 11 points remain" (DIRECTION.md). gapmap re-cuts the 500 stored rows (no model run) and answers where they sit: T2-T1 accuracy 0.256 [0.157, 0.355] in the cued base's longest quartile against 0.04-0.072 in q1-q3 (results/accuracy-01/t1_length_quartile.json). bench-rng (2 jobs) tests no part of the mission. Planned next: the cap_hit, tokens, tokens_both_right batches, 3 more re-cuts of the same rows. Better next step: a no-reward route aimed at the long/capped base answers at equal tokens (point 3), which these batches do not decide.
- Research: no replication; paired bootstrap is the conventional method. Prediction check is set by a hand-picked level: subject uses ci 0.9 (cells/accuracy.json, commit 87227e5), others 0.95; at 0.9 algebra [0.0177, 0.097] excludes the overall 0.106, so "flat across subjects" reads refuted only under the level picked for that one cell.
- Turnaround (cycle.txt, 1.5 h): 15 jobs, 3 failed, 3.1 of 17.2 container min in them, median wait 0.0; medians to-job 0, jobs 9, to-answer 1. Slowest stage: jobs. Each cell = about 23 s pip install of numpy, scipy, pandas, matplotlib (only numpy imported) + 37-51 s bootstrap of 1,500,000 resamples, run twice by submit.sh's same-seed "verification rerun".
- Change (step 2; step 1: the rerun has no named owner in SPEC.md and a seeded bootstrap on one commit and image can only repeat itself, as before.txt shows): deleted the rerun from jobs/submit.sh (fe64c85). It also no longer continues after a failed submit (function inside $(...) ignored set -e).

  | measure | before | after | change | runs | source |
  |---|---|---|---|---|---|
  | wall s per cell, submit.sh accuracy overall | 194.8 | 92.5 | 2.1x faster | 1 and 1 | before.txt, after.txt |
  | container min per cell | 2.6 (1.4+1.2) | 1.2 | -54% | 1 and 1 | jobs fc61 acb1, cb6e |
  | overall table (must not change) | 0.106 [0.074, 0.14] | same | none | 1 and 1 | runs/<id>/metrics.json vs results/accuracy-01/overall.json |

- Failures: 30e7 wrong --data path copied from README "How to run": line fixed in fe64c85. 6ebb (ci 90) and 7f9b (fmt "cvs"): hand-edited cell settings, row added to meta/FAILURES.md. Carried, named not made (owner's SPEC requirements 2-3): 1,500,000 resamples (the seed, not the count, makes a table repeat) and the unused pip installs.
- Next entry checks: next gapmap cell wall time against 92.5 s; whether the 3 remaining batches ran or the work moved to a point-3 route; subject re-scored at 0.95 or SPEC rule 3 dropped.
