# Meta review: dana

## 2026-11-15 04:26 UTC (after result-51dceb and result-0b9f0d) meta/reviews/dana/20261115-0422/

- Checks from 04:18: 0 failed cell jobs (6 of 6 tokens jobs done, cycle.txt). The next step was the tokens batch, not the mission-3 cap route. bench-rng and fmt are still there: bench-rng ran a 3rd time (PCG64 35,577/s; 39,536, 36,643 before), and the tokens subject cell was hand-set to fmt "csv", digits 2 (5cf8474, 1015d62). Both pass `--check`, since they are legal values. Digits 2 goes against Req. 2 (4 digits). The venv row: changed below.
- Direction: mission point 3 asks for a route "at equal generated tokens". tokens answers part of it: RL uses +761 [495, 1020] tokens more than the cued base overall. By the base's answer length, q1-q3 are +1,071 to +1,999 and q4 is -1,658 [-2,451, -868] (`results/tokens-01/t1_length_quartile.json`). So RL spends fewer tokens only where the base hits the cap. A loop stop for the base in q4 would free tokens that RL spends elsewhere. That route is still unclaimed. Planned next: tokens_both_right (`queue.json`). bench-rng tests no part of the mission (1 of 2 runs).
- Research: no replication. SPEC still names no closest published experiment.
- Turnaround (cycle.txt, 0.25 h): 16 jobs, 3 failed (all before 04:18), 3.3 of 17.1 container min in them, median wait 0.1. Medians: to-job 0, jobs 4 (5 before), to-answer 0. tokens work: jobs 3 min, 0 fixes. Slowest stage: jobs. Each job spends 18-22 s of 45-66 s building a venv (5 job logs, before.txt). scipy, pandas and matplotlib are never imported (cell.py and bench_rng.py import only numpy).
- Change (step 2). Step 1: the pin's reason (Req. 2, same table on rerun) covers only numpy. Deleted the 3 unused packages from run_cell.sh (3995576, pushed).

  | measure | before | after | change | runs | source |
  |---|---|---|---|---|---|
  | venv s, tokens overall | 22 | 7 | -15 s | 1 and 1 | before.txt (bd26), after.txt (21f7) |
  | job s, start to done | 66 | 50 | 1.3x faster | 1 and 1 | same |
  | overall table (must not change) | 760.948 [495.14, 1019.8781] | same | identical | 1 and 1 | after.txt |

- Failures: none since 04:18. Side failure: `gpu.py submit` refuses a dirty tree, so the review folder had to be stashed to launch (a run folder cannot be written before the job it measures). The FAILURES.md venv row stays, now 7 s per job. Removable: bench-rng (3 runs, noise > spread), `fmt`, per-batch `digits`. The owner decides.
- Next entry checks: venv s per job stays near 7; whether the mission-3 loop-stop route is claimed before tokens_both_right runs; bench-rng, fmt and digits 2.

## 2026-11-15 04:18 UTC (after result-47bc5b and result-984cbd) meta/reviews/dana/20261115-0413/

- Checks from 04:05: 1 job per cell held (cap_hit cells 61-72 s wall). The cap_hit batch ran as queued; no mission-3 step replaced it. bench-rng ran again: its rates moved 7% between runs (PCG64 39,536 to 36,643/s), more than the 3% spread between generators, so it measures noise. It is still in `queue.json` extras. FAILURES.md: the hand-edit row came back, the venv row is unchanged.
- Direction: cap_hit tests mission point 2. By the cued base's answer length, q4 is -0.168 [-0.246, -0.093] and q1-q3 are 0.000 (`results/cap_hit-01/t1_length_quartile.json`). So the q4 accuracy gap (+0.256) sits where the base hits the 16,384 cap and RL does not. This points to a mission-3 route (stop or restart a looping base answer, at equal tokens). It is a better next step than the tokens batches. 1 of 2 runs (bench-rng) tests no part of the mission.
- Research: subject intervals are 90% in accuracy and 99% in cap_hit, both set by hand (SPEC Req. 3). Digits are 4 and 3, which goes against Req. 2's reason (tables compared to 4 digits). At 99%, algebra and number theory give [0, 0] (no cap hits). There is still no closest published experiment in SPEC.
- Turnaround (cycle.txt): cap_hit work had to-job 0, jobs 5, to-answer 0. Slowest stage: jobs. 8 jobs, 2 failed (9325 ci 99, de4a digits "3"), and the fix loop took 3 min (20:07:22 to 20:10:20). The median queue wait was 0.0. This is the same class as 04:05 (4 of 23 gapmap jobs).
- Change (step 4). Steps 1-2: Req. 3 (Dana) allows hand edits for small groups, and only the owner can drop it. fmt is dead. Made: submit.sh runs `make_cells.py --check` before launch. It rejects all 4 broken cell files in git history (6398a08, 86ebbc7, 195cdc7, 9115de5) and accepts both committed ones (56a8633, pushed).

  | measure | before | after | change | runs | source |
  |---|---|---|---|---|---|
  | s from submit to error, broken subject cell (ci 99) | 67.3 | 0.07 | about 960x faster, 0 jobs | 1 and 1 | before.txt (job 59c4), after.txt |
  | s per good cell (must not change) | 61-72 | 61.2 | same | 6 and 1 | cycle.txt, after.txt (job ffa6) |
  | cap_hit subject table (must not change) | results/cap_hit-01/subject.json | runs/ffa6 | identical | 1 and 1 | after.txt |

- Failures: 2 failed jobs, both hand-edited cells. The cause is removed (they are checked before launch), so I deleted that FAILURES.md row. The venv row stays (22 s per job). Removable: `fmt`, per-batch `digits`, bench-rng. The owner decides.
- Next entry checks: 0 failed cell jobs; whether the next step is the mission-3 cap route or the tokens batch; whether bench-rng and fmt are gone; the venv row.

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
