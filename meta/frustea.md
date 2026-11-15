# Meta review: frustea (earlier entry, 02:10 UTC, is meta/8038263+frustea.md on branch minp)

## 2026-11-15 03:05 UTC (closed work-180a48 min-p, work-70152d critique-revision)

- Direction: both items were untouched basins on the idea map and test the mission's sentence directly (a no-reward route, same
  procedure on RL). Both are null: no truncation rule beats T 1.0 untruncated; self-review fixes no math. Next best step for the
  mission is not another sampling/prompt null but the 4-sample vote line (result-5d032f, +8.2 base), which already gains points.
- Research: closest tables named before each run (2407.01082 T2, 2506.13681; 2310.01798 T3-4). The critique result is the
  published one; ours adds the RL-Zero row (0 of 35 fixed) and a v3 artifact ("answer is correct." read as an answer).
- Previous entry's check: to-answer 2 and 3 min; no job died on argument parsing again.
- Turnaround (`cycle.py --hours 1.2`): 19 jobs, 5 failed or cancelled, 4.5 of 209.7 container min in them; median wait 0.1;
  per item to-job 1-2, jobs 54 / 41, to-answer 2 / 3 min. Slowest stage: jobs (16k-cap tails; shards cut critique wall to ~8 min
  for 6 of 8 shards, 2 lost 9 min to a cold setup_vllm.sh, the FAILURES.md row).
- Change (step 2, delete a failure class): infra/runner.py now calls runs.reload() at job start, so inputs put on iterate-runs
  after a container started are visible.

  | measure | before | after | runs | source |
  |---|---|---|---|---|
  | jobs failing on a just-uploaded input | 1 of 1 | 0 of 9 | 1 and 9 | jobs 8926 vs 7f41 + 8 shards |
- Next entry checks: setup_vllm.sh seconds per job (536 s seen on shards 2498, 5774).
