# Meta review: dana

## 2026-11-15 04:00 UTC (after work-f7b2b7 closed as result-783a1d, gapmap tokens) meta/reviews/dana/20261115-0400/

- Last entry: none (first entry in `meta/dana.md`), so no checks carried.
- Direction: mission = "how much of a published RL gain an untrained base model reaches with no training"; point 3 = "the cheapest route to those points that uses no reward, at equal generated tokens" (DIRECTION.md). gapmap maps point 2, which DIRECTION already states ("spread over problems of all lengths"). Its 4 jobs since the study began (tokens batch) test no part of point 3: 0 of 4. The plan is the 3 batches still queued (`queue.json`: accuracy, cap_hit, tokens_both_right). `cap_hit` split by T1 length quartile follows from its own definition (all 27 T1 cap hits are at 16,384 tokens, the top quartile). Best alternative: run only the `accuracy` batch, the one that decides the SPEC prediction, then a no-reward route on the 16 "cap hit, no loop" problems of the 65 (`rlneurons/results/rln4/t1_t2_items-01/notes.md` §2) at equal tokens with RL given the same procedure.
- Research: no replication, no published table needed for a bootstrap over stored rows. The "where" question is already partly answered by hand labels in notes.md §2 (16 cap hits, 14 misreads, 14 slips, 8 form or grader of 65). The SPEC does not cite them.
- Turnaround (cycle.txt, 1 h): 4 jobs, 0 failed or cancelled, 3.3 container min, median queue wait 0.1 min; medians to-job 0, jobs 2, to-answer 0. Slowest stage: jobs. Of a 0.9 min job, 46.1 s was the bootstrap (before.txt, job 796d).
- Cause: SPEC requirement 2 set 1,500,000 resamples so that "a rerun gives the same table to the last digit". The fixed seed gives that at any count, so the count had no reason behind it. Change (step 2; step 1 found the reason did not hold): `queue.json` n_boot 1,500,000 -> 10,000, and SPEC requirement 2 cut to "one fixed seed and count". The posted tokens-01 and overall-01 numbers keep their 1,500,000.

  | measure | before | after | change | runs | source |
  |---|---|---|---|---|---|
  | bootstrap seconds, tokens/subject cell | 46.1 | 0.3 | 150x faster | 1 and 1 | jobs 796d, f0d2 logs |
  | job run minutes | 0.9 | 0.1 | 9x faster | 1 and 1 | cycle.txt, after.txt |
  | point estimates, 7 groups (must not change) | e.g. 1116.95 | identical | none | 1 and 1 | logs |
  | interval ends (Monte Carlo noise) | e.g. precalc low 36.81 | 17.28; max shift 19.5 tokens, at most 1.9% of width | same verdicts vs 0 and vs overall 760.9 | 1 and 1 | logs |

- Failures: none in jobs. Latent: `jobs/cell.py` imports `studies.gapmap.jobs.bench_rng` for kind "bench", and that module does not exist. It is not used yet. The next entry deletes the branch if no cell uses it.
- Next entry checks: the accuracy batch runs at n_boot 10,000 and decides the SPEC prediction; whether cap_hit and tokens_both_right were deleted from the queue; a work item exists on point 3 (a route on the 16 cap-hit problems); the bench_rng branch is gone.
