# Meta review: dana

## 2026-11-15 04:00 UTC (after work-5a5ef5 closed as result-58b069, gapmap accuracy) meta/reviews/dana/20261115-0354/

- First entry for dana, so no check is carried. Direction: mission = "how much of a published RL gain an untrained base model reaches with no training"; deliverable = "the best configuration of either model on the 328" (DIRECTION.md). The one step since then, gapmap accuracy, tests point 2 and contradicts its text "spread over problems of all lengths": T2 minus T1 is 0.256 [0.157, 0.355] in the longest quartile of the cued base's answers, against 0.04 to 0.072 in q1 to q3 (125 problems each, `studies/gapmap/results/accuracy-01/t1_length_quartile.json`). Planned next: 3 more descriptive batches (cap_hit, tokens, tokens_both_right; 12 cells). None of them tests point 3. Better next step: a no-reward route aimed at the cued base's longest quartile (loops and cap hits), with RL given the same procedure.
- Research: no replication and no GPU run. SPEC names no published experiment beside it. Part of this was already readable from stored rows: 27 of the base's 90 wrong answers at T 1.0 are cap hits (meta/sameraslan.md line 5). Prediction: the long-quartile half holds. The flat-subject half is refuted, but only by algebra, at both 90% ([0.0179, 0.0965]) and 95% ([0.0147, 0.1044] against overall 0.106; job 302e). With 7 groups, one exclusion is close to chance.
- Turnaround (cycle.txt, 1 h): 4 jobs, 0 failed, 3.2 container min, median queue wait 0.1 min. Medians: to-job 0, jobs 2, to-answer 0 min. Slowest stage: jobs, and inside each job, 40-42 s of a 0.7-0.8 min run was the bootstrap at 1,500,000 resamples.
- Change (step 2, then 3). Step 1: SPEC requirement 2 (Dana) needs 1.5 M resamples so that "a rerun gives the same table to the last digit". The fixed seed alone gives that at any count, so the count only sets Monte Carlo error. The 4th digit is far below the interval width (0.07 to 0.29). Made: `queue.json` n_boot 1,500,000 -> 20,000 for the next batches (00a98b5). accuracy-01 is left as posted.

  | measure | before | after | change | runs | source |
  |---|---|---|---|---|---|
  | bootstrap seconds per cell | 40.2-42.3 | 0.5-0.6 | ~70x faster | 4 and 4 | before.txt, after.txt |
  | job run minutes per cell | 0.7-0.8 | 0.1 | 7x | 4 and 4 | cycle.txt, `gpu.py ls` |
  | largest move of an interval end (must stay < 0.003) | - | 0.0029 (geometry high, 90%) | within | 4 cells, 17 groups | before.txt, after.txt |
  | groups whose interval excludes 0.106 (must not change) | algebra, t1 q4 | algebra, t1 q4 | unchanged | 17 groups | same |

- Failures: none. Dead code found: `cell.py` `kind: bench` imports `studies.gapmap.jobs.bench_rng`, which does not exist. Not deleted in this entry.
- Next entry checks: whether the 12 descriptive cells were deleted or run, and if run, their bootstrap seconds against 0.6; whether a point-3 route on the cued base's longest quartile is claimed; whether the bench branch is gone.
