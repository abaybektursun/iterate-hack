# Meta review: dana

## 2026-11-15 04:06 UTC (session start, after result-7fbde6 and result-8e27df) meta/reviews/dana/20261115-0400/

- Last entry's checks: none. This is dana's first entry.
- Direction: mission point 2 (DIRECTION.md) says "about 11 points remain ... spread over problems of all lengths". gapmap accuracy-01 tests that sentence and contradicts it: the longest quartile of the cued-base answers has 0.256 [0.157, 0.355], and that interval excludes the overall 0.106 (result-7fbde6). The SPEC's "flat across subjects" is also refuted: algebra 0.0565 [0.0177, 0.097] excludes 0.106 (90% interval). That is a wrong prediction, reported as one. 2 of the 15 jobs (bench-rng, result-8e27df) test no part of the mission. Next step as planned: the cap_hit, tokens and tokens_both_right batches. Better step: a route claim (mission point 3) aimed at the long answers of the cued base, because the map already says where the gap sits.
- Research: no replication. The cells only read stored rows (rln4 per_problem.json), which is the right source. With 500 items the interval ends move in steps of 0.002, so the 4 digits and 1,500,000 resamples (SPEC Requirement 2) add no precision.
- Turnaround (cycle.txt, 2 h): 15 jobs, 3 failed, 3.1 of 15.6 container min in the failures, median wait 0.0 min. Medians: to-job 0, jobs 9, to-answer 1 min. Slowest stage: jobs. Where those minutes went: 6 of the 12 done jobs were same-seed verification reruns from submit.sh, started only after the first job ended. Each job spends 15-21 s on a pip install and 29-46 s on the bootstrap (logs of 5fab and 5e89).
- Change (step 2; step 1: no person or reason is named for the rerun in 1a10464, and Requirement 2 already makes a same-seed rerun identical by construction, so a rerun cannot fail): deleted the rerun from studies/gapmap/jobs/submit.sh (12f5a20, pushed).

  | measure | before | after | change | runs | source |
  |---|---|---|---|---|---|
  | wall s, submit.sh accuracy overall | 178.6 | 82.6 | 2.2x faster | 1 and 1 | before.txt, after.txt |
  | jobs per cell | 2 | 1 | -1 | 1 and 1 | jobs 6bd2+eef6, 5e89 |
  | table (must not change) | 0.106 [0.074, 0.14] | 0.106 [0.074, 0.14] | same | 1 and 1 | runs/<job>/metrics.json |

- Failures: (1) 2046: the README's `--data` path did not exist. Fixed by deleting the argument from the README (12f5a20); the default in cell.py is correct. (2) 8bc8 (ci 90) and dd18 (fmt "cvs"): cell settings edited by hand per batch (Requirement 3). Each was caught only after the install and the 45 s bootstrap. Added a row to meta/FAILURES.md. The gapmap pip install is the same class as the existing vLLM row; added a row for it too.
- Next entry checks: whether the cap_hit, tokens and tokens_both_right batches run at 1 job per cell; whether Dana deletes Requirement 3, or cell.py checks ci and fmt before the bootstrap; whether a route claim targets the cued base's long answers.
