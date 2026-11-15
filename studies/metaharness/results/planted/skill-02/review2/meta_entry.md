# Meta review: dana

## 2026-11-15 04:15 UTC (after work-824cfe and work-8276a3 closed) meta/reviews/dana/20261115-0415/

- Last entry's checks: wall per cell 80-91 s (after.txt) against 92.5 s. The cap_hit batch ran (8 jobs); tokens and tokens_both_right are still planned, no point-3 route started. The subject cell was not rescored at 0.95: it was hand-set again, to 0.99 (433cd8c). Rescored here: at 0.95, accuracy algebra [0.0144, 0.1056] excludes 0.106, so "flat across subjects" is refuted at the spec's own level, by 0.0004 (results/subject_ci95-01/).
- Direction: mission point 3 asks for "the cheapest route to those points that uses no reward, at equal generated tokens". cap_hit shows where to aim: the cued base hits the cap 4.2 points more often (-0.042 [-0.062, -0.022]), all of it in its longest quartile (q4 -0.168, q1-q3 0.0; cap_hit-01/t1_length_quartile.json). Of 8 jobs, 0 test point 3, and bench-rng (run 2 times, PCG64 37576 then 42645/s, 13% apart on the same code) tests nothing. Better next step than 2 more re-cuts: restart or a 4-sample vote on the base's capped answers at equal tokens (DIRECTION Day 1 item 3).
- Research: no replication. The SPEC rule "differs when the interval excludes the overall value" flags groups with no events: cap_hit algebra and number_theory have interval [0, 0]. These are degenerate groups, not effects.
- Turnaround (cycle.txt, 0.5 h; cap_hit work item): to-job 0, jobs 6, to-answer 0 (before: 0, 9, 1). 8 jobs, 2 failed, 2.4 of 8.9 container min (before: 15, 3, 3.1 of 17.2). Median wait 0.0. Slowest stage: jobs. Both failures were the hand-edited subject cell (ci 99, digits "3"), the same class as 6ebb and 7f9b.
- Change (step 2; step 1: SPEC requirement 3, Dana's. It hand-set the subject level "because groups are small", but small groups already widen their own intervals, and a level changed per batch breaks requirement 2's comparison between batches): deleted prep/make_cells.py, cells/<batch>.json and the csv writer. cell.py builds every cell from queue.json (22075ac). FAILURES row removed.

  | measure | before | after | change | runs | source |
  |---|---|---|---|---|---|
  | jobs per committed subject cell | 3 and 3 (accuracy, cap_hit) | 1 and 1 | 3x fewer | 2 batches each | before.txt, after.txt |
  | failed cell jobs | 4 of 26 | 0 of 3 | none failed | 26 and 3 | cycle.txt, after.txt |
  | cap_hit overall (must not change) | -0.042 [-0.062, -0.022] | same | none | 1 and 1 | job c107 vs f707 |

- Failures: 3 gpu.py submits were refused because the untracked review folder made the tree dirty. Row added to FAILURES.md with its fix. Carried, not made: 1,500,000 resamples and the unused scipy/pandas/matplotlib installs (requirement 2 and run_cell.sh), bench-rng in queue.json extras (one job per batch, tests no part of the mission).
- Next entry checks: whether the next step is a point-3 route on the capped base answers or the tokens batches; whether any subject cell failed; whether bench-rng is out of queue.json.

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
