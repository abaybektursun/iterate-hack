# Meta review: dana

## 2026-11-15 04:27 UTC (after result-94edb8 and result-5eef04) meta/reviews/dana/20261115-0421/

- Last entry's checks: (1) tokens ran with 0 failed of 6 jobs (cycle.txt). The bad settings were fixed in git 1 s after the cells (21c55f5, 8ada24c), before any job launched, so the check works. (2) Requirement 3 is still in SPEC.md, and bench-rng still runs (fbde). (3) There is still no route claim.
- Direction: DIRECTION.md point 3 asks for "the cheapest route ... that uses no reward, at equal generated tokens". tokens overall: T2 uses +761 [495, 1020] tokens per problem more than T1. That is the token budget a cued-base route may spend. t1 quartiles (q1-q3 positive, q4 -1658) are regression to the mean by construction, as cap_hit q4 was. 3 of 3 batches describe the gap and 0 test a route. Planned next: tokens_both_right, a 4th description. Better: a restart on the cued base's capped answers, with a budget of 761 tokens per problem.
- Research: no replication. The tokens batch partly repeats rows already stored (rln4 notes.md section 3: medians and AUC 0.83 of length).
- Turnaround (cycle.txt, 0.25 h): 15 jobs, 2 failed (both from the last entry), 2.2 of 17.2 container min in the failures (previous 2.2 of 13.2), median wait 0.1 min (0.0). Medians: to-job 0, jobs 3 (6), to-answer 0 (0). Slowest stage: jobs. Each tokens job: 15-24 s building a venv (median 20 s), then a 29-44 s bootstrap (before.txt). The image already holds the same numpy, scipy, pandas and matplotlib pins (requirements.txt, infra/runner.py:28), and cell.py imports only numpy.
- Change (step 2; step 1: the venv's reason, "no cell inherits another job's packages", cannot apply, because every job starts in a fresh container of the image): deleted the venv and pip install from run_cell.sh, and added an assert on numpy 2.5.4 (604a713, pushed). This removes the gapmap row from meta/FAILURES.md.

  | measure | before | after | change | runs | source |
  |---|---|---|---|---|---|
  | s from job start to bootstrap start | 16 (15-24 over 6 jobs) | 0 | -16 s | 1 and 1 (6 for range) | before.txt, after.txt |
  | job run s, tokens overall | 45 | 44 | same: bootstrap 28.9 -> 43.1 s, CPU noise | 1 and 1 | jobs c99f, f035 |
  | tokens overall table (must not change) | 760.948 [495.14, 1019.8781] | identical | same | 1 and 1 | tokens-01/overall.json, runs/f035 |

- Failures: none new. Carried: submit.sh fails with a bare `KeyError: ''` when the job id is empty (a dirty tree). It came close again this review, and stashing avoided it. The bootstrap now takes 29-44 s of a 44 s job. Its 1,500,000 resamples come from Requirement 2 (Dana). Same seed gives the same table at any count, so the count is not what makes a rerun reproducible. Deleting it is Dana's call.
- Next entry checks: job run s over a full batch without the venv, against 0.8-1.2 min for tokens (cycle.txt); whether Dana deletes Requirement 2's count, Requirement 3 and bench-rng; whether a restart route claim is on the board before tokens_both_right runs.

## 2026-11-15 04:13 UTC (after result-909ef8 and result-db9806) meta/reviews/dana/20261115-0413/

- Last entry's checks: (1) cap_hit ran at 1 job per cell: yes, apart from subject, which took 3 jobs (run.json, cycle.txt). (2) Requirement 3 is still in SPEC.md and cell.py still checked nothing before the bootstrap: the class came back (5bd9 ci 99, ebb6 digits "3"). (3) No route claim yet.
- Direction: mission point 3 asks for a route to the ~11 points. cap_hit shows where it is. All cap-hit differences sit in the cued base's longest quartile: q4 -0.168 [-0.246, -0.093], q1-q3 0. This is true by construction (an answer that hits the cap is a longest answer), so the t1_length_quartile cell of cap_hit adds no information. accuracy q4 is +0.256. Next as planned: the tokens and tokens_both_right batches. Better: a route claim for the cued base's capped answers, e.g. a restart (Day 1 item 3) at equal tokens. The batches only describe the gap further. bench-rng tests no part of the mission, and its rate moved 36% between two runs of the same code (56408 to 36872/s, PCG64), so it measures runner noise.
- Research: no replication. Every cell reads stored rows. Two cells can be read off the data without a run: cap_hit by t1 quartile (above) and the 0-width intervals.
- Turnaround (cycle.txt, 0.25 h): 11 jobs, 2 failed, 2.2 of 13.2 container min in the failures (previous entry: 3 failed of 15, 3.1 of 15.6). Median wait 0.0 min. Medians: to-job 0, jobs 6 (previous 9), to-answer 0 (previous 1). Slowest stage: jobs. The 2 failures ran one after another and added 2.7 min of wall time to the subject cell (commit at 20:06:18, good launch at 20:09:02). Each failure was raised only after the 21 s install and the 40 s bootstrap.
- Change (step 3. Step 1: Requirement 3 names Dana and gives a reason, but small groups justify a wider interval, not hand-set digits or table format. Step 2: deleting it is Dana's call, asked below): `make_cells.py --check` validates ci, digits, fmt, n_boot, metric and split on the laptop, and submit.sh runs it before it launches any job (13597f4, pushed).

  | measure | before | after | change | runs | source |
  |---|---|---|---|---|---|
  | time to find a bad cell setting | 1.1 min/job, after install + bootstrap | 0.1 s, 0 jobs | ~600x faster | 2 and 2 | before.txt, after.txt |
  | cap_hit overall table (must not change) | -0.042 [-0.062, -0.022] | -0.042 [-0.062, -0.022] | same | 1 and 1 | jobs 8b8e, a713 |

- Failures: (1) 5bd9, ebb6: the hand-edit class. Its row is deleted from meta/FAILURES.md; the check lands in 13597f4. (2) `gpu.py submit` refuses a dirty tree, so an uncommitted meta run folder blocks a job, and submit.sh then fails with a bare `KeyError: ''` from `wait`. That cost one try in this review. Not fixed yet: submit.sh should exit when the job id is empty.
- Next entry checks: whether tokens runs with 0 failed jobs; whether Dana deletes Requirement 3 and the bench-rng extra; whether a route claim (restart on capped cued-base answers) is on the board.

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
