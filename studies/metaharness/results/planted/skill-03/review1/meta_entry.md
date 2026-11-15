# Meta review: dana

## 2026-11-15 04:05 UTC (session start, after result-2953a7 and result-c60846; first dana entry, so no checks carried) meta/reviews/dana/20261115-0400/

- Direction: mission = "how much of a published RL gain an untrained base model reaches with no training"; point 2 says the ~11 points are "spread over problems of all lengths" (DIRECTION.md). work-74fe1a tests point 2 and contradicts it: by the cued base's answer length, q4 is +0.256 [0.157, 0.355], q1-q3 are +0.04 to +0.072, overall +0.106. So 32 of the 53 problems sit in the longest quartile (`results/accuracy-01/t1_length_quartile.json`). work-dc5378 (bench-rng) tests no part of the mission, so 1 of 2 runs tests none. Its answer moves nothing: generators differ by 6% (37,041 to 39,536 draws/s) on a 43 s bootstrap.
- Going: the plan is 3 more batches (cap_hit, tokens, tokens_both_right × 5 splits, plus bench-rng in each, `queue.json`). That is the next question about the last result. Best alternative: a mission-3 route aimed at the long, capped base answers (stop or restart on a loop, at equal tokens), read first from the stored rows. Overall cap_hit and tokens are already in `results/overall-01/metrics.json`.
- Research: no replication, but SPEC.md names no closest published experiment ("differs in X" is missing). Risk of narrowing later: "flat across subjects" is refuted only by algebra [0.018, 0.097] at a 90% level set by hand for that one split (7 groups, no correction). The other splits use 95%.
- Turnaround (cycle.txt, 2 h): 15 jobs, 3 failed, 2.8 of 16.1 container min in them, median wait 0.0. Medians: to-job 0, jobs 9, to-answer 0. Slowest stage: jobs. The 9 min went to: a fix loop of 3 serial failed jobs (03:50:54 to 03:55); 6 same-seed verification reruns (6 of 15 jobs); 22 s pip venv per job (scipy, pandas and matplotlib unused); 43 s bootstrap at 1.5 M resamples.
- Change (step 2). Step 1: the rerun had no named owner (only a comment in submit.sh), and seed 0 plus the pinned environment give the same table by construction. 6 of 6 checks matched and 0 of the 3 failures were caught. Deleted: submit.sh launches each cell once (29dfafd, pushed).

  | measure | before | after | change | runs | source |
  |---|---|---|---|---|---|
  | wall s per cell, submit.sh accuracy overall | 137.1 | 71.9 | 1.9x faster | 1 and 1 | before.txt, after.txt (jobs 6460+c022, 981e) |
  | CPU jobs per cell | 2 | 1 | -1 | 1 and 1 | same |
  | overall table (must not change) | 0.106 [0.074, 0.14] | 0.106 [0.074, 0.14] | identical | 1 and 1 | after.txt, results/accuracy-01/overall.json |

- Failures: 3 of 15 jobs had hand-edited settings that reached a job unchecked. 0792: the README's wrong `--data` path, deleted in 29dfafd. 8264: ci out of [0, 1]. 922c: fmt "cvs". The cause stays (SPEC Requirement 3: per-batch hand edits). Added to FAILURES.md together with the per-job venv. Removable context: `fmt` is a dead knob (metrics.json always holds the table); Requirement 2's reason holds through the seed, not through 1.5 M resamples. The owner decides both.
- Next entry checks: the next batch runs 1 job per cell at about 72 s; whether the cap_hit/tokens batches run or a mission-3 step replaces them; whether bench-rng is dropped from `queue.json` extras; the 2 new FAILURES.md rows.
