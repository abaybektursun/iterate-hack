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

## 2026-11-15 01:20 UTC

- Previous checks: run.sh is the only basins laptop entry (README commands use it); GPU access now works (Modal card fixed by Modal); no testbed spec (owner chose the strategy run instead).
- Direction: mission = cheapest no-reward route to the ~11 points, deliverable a scored config on the 328. Since 23:05: swarm map refresh, idea tree, leaderboard split (measure the swarm, test no part of the sentence); 4 smoke jobs + 1 run for strategy basins (base+cue vs RL strategy sets on MATH-500), which tests where RL's points come from (strategies the base never samples), not a route. Best mission-side alternative: none claimed by me; teammates hold the route search. Kept because the owner's deliverable is the presentation.
- Research: closest published = Lee et al. 2606.29985 Table 2 (Cov@16 after GRPO, Qwen2.5); this differs in model (Olmo 3 RL-Zero), base with cue, and RL-only share of correct answers. Run cut to 21 problems x 16 samples (~1.6 USD) on owner's budget.
- Turnaround (cycle.py --hours 12): 5 jobs, median wait 0.0 min, 13.2 container min, 6.1 (46%) in 2 failed jobs; work-ff64d5 to-job 112+ min, slowest stage = waiting on Modal billing (a person).
- Failures: both failed jobs = vLLM JIT kernels needing nvcc (FlashInfer sampler 152501-615c; DeepGEMM 153448-dce3); class: engine environment set separately in each script.
- Change (step 3; steps 1-2: the two env lines had no reason to exist twice): studies/basins/lib/engine.enter() is the one place gen and judge set the vLLM environment.
- Next entry checks: judge job on this commit starts without an nvcc error; failed-job share of container minutes.
## 2026-11-14 23:05 UTC (first entry)

- Direction: DIRECTION.md mission is the no-reward route to the ~11 points (cue base vs RL). My runs since 21:19: swarm maps main-01/02 (result-47286f, work-4dfcf9 closed 23:00) test no part of that sentence; they measure the swarm. The one study that does (strategy basins, idea-65a86d) is blocked: 0 GPU jobs, Modal refuses every GPU class without a card. Next step (owner's choice): a CPU testbed comparing anti-collapse strategies (fork-and-flush, forgetting, archive tree). Best mission-side alternative: strategy basins on GPU; not chosen because no GPU access.
- Research: Lee et al. 2606.29985 Table 2 already answers "RL has fewer strategies" (Qwen); strategy study was narrowed to Olmo + RL-only share before any run. Swarm map reuses Bespoke/Fork-and-Flush method on a new object (a multi-person board).
- Turnaround (cycle.py --hours 2): 0 jobs, work-4dfcf9 total 101 min, no job stage. Slowest stage: waiting on a person (payment method). Judge cost about 1.1 USD per map; gpt-5.4-mini was near chance (359/767 order-consistent), so not a cheaper path.
- Failures: (1) uv picked Python 3.15 for numpy/scipy and one analysis call hung 5 min; class: environment entered in many command lines. (2) force-push of a rebased branch denied; pushed as ali/basins instead.
- Change (step 3, simplify; steps 1-2: the long uv line had no reason to be retyped per call): studies/basins/run.sh is the one entry point (Python 3.12, requirements.txt pins); README commands use it. Swarm analysis via run.sh: 33 s.
- Next entry checks: no basins command outside run.sh; GPU access state; testbed spec written before any agent run.
