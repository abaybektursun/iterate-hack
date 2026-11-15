# explore: strategies against exploration collapse in autoresearch agents (idea-35c9d8)

Private control experiment on branch `ali/explore` (not announced; not merged to main until the pilot holds).

Question: at a matched budget, do fork-and-flush (arXiv 2610.07447) or forgetting (2610.20563) beat a single
long run and best-of-K parallel runs, and do they reach more approach basins? Agents are gpt-5.4-mini through
the OpenAI API; the scorer runs on the laptop CPU in milliseconds. No GPU.

Prior work: Fork-and-Flush Table 1 (13 tasks, normalized mean 0.78 vs single 0.47 vs best-of-4 0.54);
Forgetting Table 1 (4 tasks, team with forgetting beats 4 parallel on all 4). No paper found that triggers
branching from an online basin signal (survey 2026-11-14). Public reimplementation: github.com/yikerman/fork-and-flush.

## Layout

| Path | What it is |
|---|---|
| `lib/loop.py` | One chat call (OpenAI, or Cognition for `swe-*` models), one scored submission, one JSONL log row; tokens and USD per call; 6 scoring slots shared by all runs on the machine, single-thread BLAS. The model sees the starting program's score and never its remaining budget. |
| `lib/strategies.py` | single, parallel (best of K), fnf, forget, fnf_keep, basin, randflush, tree (DGM parent rule), and the assign-01 arms: fnf_assign (ours), single_list, rebase, fnf_undirected, halving. Each only chooses chat history and start program. |
| `jobs/run_strategy.py` | One strategy run on one task: `python3 -m studies.explore.jobs.run_strategy --task circles26 --strategy fnf --budget 30 --seed 0 --model gpt-5.4-mini --out runs/explore/circles26/<exp>/<arm>-s<seed>` |
| `analysis/compare.py` | Arms side by side: final best per seed, runs above the starter, best after the same USD spend (the smallest total of any run), optimizer share (pilot-02 regex), best-so-far curves. |
| `analysis/export_results.py` | Copies an experiment's small files from `runs/` to `results/<task>/<experiment>/` (compare.json, runs.json, assignments, examples). |
| `analysis/best_of_k.py` | Expected best of K independent stored runs of each arm, and how many runs of one arm equal one run of another. |
| `analysis/spread_test.py` | Two arms of one experiment folder: one-sided Brown-Forsythe permutation test on spread (all splits), exact one-sided rank-sum on validation and test, SD, worst run. Reproduces the swe2-seeds-01 numbers (p 0.0422, 0.197, 0.066). |
| `analysis/page/build.py` | The results page (private artifact https://claude.ai/artifact/XQwm42PhgcxWjtro4WXN1E): `python3 studies/explore/analysis/page/build.py <out.html>`; template in `analysis/page/template.html`. |
| `tasks/circles26/` | 26 circles in the unit square, maximize the sum of radii; scorer checks validity (tol 1e-9). Starter 2.54138; best published about 2.636. |
| `tasks/ahc014/` | AtCoder Heuristic Contest 014 (RectJoin) from Frontier-CS algorithmic problem 159, the task both papers report. Python program, 3 s per case (hard 4 s). Score: mean V / V_ref over cases 1-5 (test: 6-10), checked by the Frontier-CS checker `data/chk.cc` (commit in `data/SOURCE_COMMIT`). Starter (no operations) 0.2217. |

Raw logs and programs stay in `runs/explore/` (not committed).

## Results

**Environment bug (found 2026-11-15 with SWE-2):** until commit after 892e7e1, submitted programs ran on the
laptop's `/usr/bin/python3`, which has no numpy or scipy, although the circles26 spec allows both. Every result
below is therefore a **pure-Python** run. Effect: 6 of 1,066 circles submissions (pilot-02, main-01) and 4 of 101
(main-02) imported numpy/scipy, all invalid; those were the attempts at the optimizer approach. ahc014: 0 of 270
imported them (unaffected). Programs now run in `runs/explore/.venv` (numpy 2.5.4, scipy 1.18.1), checked at start.

### ahc014/swe2-spread-02: is single less reliable than fnf? Fresh runs say not shown (SWE-2, 6 runs per arm, 0 USD)

Plan written before the runs: `specs/spread-ahc014-swe2.md` (fresh seeds 6-11; the seeds-01 runs produced the
hypothesis and are not used). `results/ahc014/swe2-spread-02/summary.json` (from `analysis/spread_test.py`);
examples: best single-s9 s0012 (0.655), invalid fnf-s10 s0001. Rerun: `swe2-spread-01` died on Devin's free-model
rate limit at 13-19 of 40 tries per run and is not used; same seeds and arms, code plus a60ebc4.

| Arm | Validation, 6 fresh runs | Mean | SD | Worst | Held-out test mean |
|---|---|---|---|---|---|
| single | 0.573 0.510 0.541 0.655 0.593 0.596 | 0.578 | 0.050 | 0.510 | 0.563 |
| fnf | 0.578 0.578 0.528 0.629 0.560 0.577 | 0.575 | 0.033 | 0.528 | 0.566 |

- **The planned test fails:** spread single > fnf, Brown-Forsythe permutation p = 0.154 (needed p < 0.05). The
  direction repeats (SD 0.050 vs 0.033) at less than half the first batch's gap (0.082 vs 0.024).
- Means are equal: single 0.578, fnf 0.575; rank-sum fnf > single p = 0.59 (validation), 0.47 (test). No run of
  either arm is below 0.50, so there is no stuck run to examine; the seeds-01 gap came mostly from single-s2 (0.409).
- All 24 runs pooled (descriptive, not a test, because 12 of them produced the hypothesis): single mean 0.562
  SD 0.067 worst 0.409; fnf mean 0.583 SD 0.029 worst 0.528; fnf > single rank-sum p = 0.28.
- Reading: with SWE-2 at 40 submissions on ahc014, one chat and Fork-and-Flush are not distinguishable in mean,
  and the reliability difference is not established. 1 stuck run in 12 single runs, 0 in 12 fnf runs.

### ahc014/swe2-seeds-01: seeds test, single vs parallel vs fnf (SWE-2, 6 runs per arm, 0 USD)

Plan written before the runs: `specs/seeds-ahc014-swe2.md`. Seed 0 from swe2-01 pooled with seeds 1-5.
`results/ahc014/swe2-seeds-01/summary.json`; examples: best fnf-s4 s0037, stuck single-s2 s0037, invalid fnf-s4.

| Arm | Validation, 6 runs | Mean | SD | Held-out test mean (invalid = 0) |
|---|---|---|---|---|
| single | 0.561 0.637 0.409 0.606 0.499 0.567 | 0.546 | 0.082 | 0.532 |
| parallel (best of 4) | 0.595 0.538 0.574 0.580 0.569 0.602 | 0.577 | 0.023 | 0.368 (2 of 6 best programs fail on test) |
| fnf | 0.625 0.612 0.587 0.558 0.582 0.584 | 0.592 | 0.024 | 0.567 |

- **The planned test fails:** fnf > single on validation, exact one-sided rank-sum U = 24/36, p = 0.197 (needed
  p < 0.05). fnf > parallel p = 0.155. The prediction is refuted at 6 runs per arm, although the means are in
  the predicted order (fnf 0.592 > parallel 0.577 > single 0.546).
- On held-out test cases (reported, not the planned test): fnf > parallel p = 0.031, fnf > single p = 0.066.
  Two parallel best programs fail on test: s1 exceeds 4 s under load (alone: 0.522), s3 crashes on case 6.
- Found after looking, so a lead, not a result: single runs vary much more (SD 0.082 vs 0.024; Brown-Forsythe
  permutation p = 0.042 vs fnf, 0.046 vs parallel). Their worst run is 0.409 against 0.558 for fnf and 0.538 for parallel.
- That worst run shows the anchoring the papers describe. single-s2 adopted at try 2 a move set in which every
  45-degree rectangle is a square, and kept it for 38 more tries (case 1: 22 tilted squares, 0 tilted non-squares,
  54 moves). In fnf-s4 a fresh branch at the opening fork allowed tilted rectangles with unequal sides
  (0.388 -> 0.522) and became the leader (case 1: 28 tilted non-squares, 100 moves).
- Weak point: the 4 s per-case limit with programs that run for 3 s by their own clock is tight when 15 runs
  share the laptop; scoring is less exact under load.

### ahc014/swe2-01 (SWE-2 via Devin CLI, 1 seed, 40 submissions, commit 78b1352, 0 USD; judge 0.04 USD)

`results/ahc014/swe2-01/compare.json`; examples: best fnf-s0 s0030 0.6246, invalid (checker: a corner without a dot).

| single | parallel | fnf_keep | fnf | forget | basin | randflush |
|---|---|---|---|---|---|---|
| 0.561 | 0.595 | 0.613 | **0.625** | 0.606 | 0.571 | 0.573 |

- Single lowest again, fnf highest; the flush alone (fnf vs fnf_keep) is +0.012 here against +0.037 with
  gpt-5.4-mini. One seed: the seeds test (`specs/seeds-ahc014-swe2.md`) checks single / parallel / fnf.
- The task-neutral judge now over-splits: 14 basins in 40 submissions (`basin-s0_basins.json`), so the 4-in-a-row
  rule fired once; basin (1 flush) and randflush (1 flush) are the same arm in practice (0.571 vs 0.573). The
  basin trigger is not tested until the judge's granularity is calibrated (it lumped all 40 into one basin before).

### circles26/ksweep-01 (agent-count sweep of assigned methods, gpt-5.4-mini, 1 seed per cell, 40 submissions, 2.4 USD)

Spec `specs/ksweep-circles26-assign.md` (written before the runs). Files `results/circles26/ksweep-01/`; examples:
best assign-k8-s0 s0038 2.624157, invalid parallel-k8-s0. K=4 fnf_assign is assign-01/assign_mini-s0.

| K | parallel (K independent chats) | fnf_assign (K branches per fork, one method each) | Gap |
|---|---|---|---|
| 2 | 2.159 | 2.541 | +0.382 |
| 4 | 2.452 | 2.628 | +0.176 |
| 8 | 2.182 | 2.624 | +0.442 |

- Prediction held at all three K: fnf_assign > parallel, and parallel stays below the starter 2.54138 at every K.
- fnf_assign at K=2 does not beat the starter (2.541289): its lists of 2 named local search and a "hybrid
  optimizer", and 5 of 40 programs used an optimizer (29/40 at K=4, 14/40 at K=8). The arm needs a list wide enough
  to contain the method that works; 4 and 8 give the same score.
- At K=8 each branch gets 1 submission and 7 of 24 were invalid; the gain came from the leader refining the best
  branch (2.548 -> 2.624).
- Weak points: 1 seed per cell; parallel's valid share is 0.25-0.38 at K=4 and 8.

Best of K stored runs (`analysis/best_of_k.py`, no new runs), ahc014 SWE-2, 6 runs per arm, 40 submissions each:
one fnf run (mean 0.591) equals the expected best of 2 independent single runs (0.595, 80 submissions) and of 3
parallel-of-4 runs (0.595); best of 3 single runs is 0.613. circles26 gpt-5.4-mini: 30 finished runs without
assignment (1,120 submissions, all strategies) have a best of 2.546; one fnf_assign run reaches 2.628.

### assign-01 (gpt-5.4-mini, 1 seed, 40 submissions, numpy/scipy available, 2026-11-15; each run's commit is in runs.json)

Question: a flush clears the chat, but the fresh chat samples from the same model. Does telling each fresh branch
which method to use (`fnf_assign`: before each fork one call lists 4 methods, one per branch) beat the published
strategies? Prediction: on circles26 the assigned arms end above the starter 2.54138 with more optimizer programs;
refuted if they end at or below fnf. On ahc014: refuted if they end at or below forget's 0.439 (main-01).
Files: `results/circles26/assign-01/`, `results/ahc014/assign-01/` (compare.json, runs.json with each run's command
and commit, `*_assignments.json` with the listed methods, examples). Raw: `runs/explore/<task>/assign-01/`.
The list calls are extra to the 40 submissions (3 per run, 0.004-0.026 USD per run).

**circles26** (starter 2.54138, best published about 2.636; 3.9 USD). Examples: best assign_sol-s0 s0019 2.635983,
invalid fnf-s0 s0000 (overlap).

| Arm | Best | Optimizer code | Valid | USD |
|---|---|---|---|---|
| single | 2.045 | 0/40 | 0.97 | 0.90 |
| single_list (same lists shown to one chat, "pick one") | 2.246 | 0/40 | 0.72 | 0.61 |
| fnf | 2.535 | 1/40 | 0.53 | 0.30 |
| rebase (chat kept, best program re-shown every 10) | 2.541 | 1/40 | 0.95 | 0.45 |
| fnf_assign, list by gpt-5.4-mini | 2.628 | 29/40 | 0.70 | 0.78 |
| fnf_assign, list by gpt-6.1-sol | 2.636 | 39/40 | 0.68 | 0.86 |

- Prediction held: both assigned arms beat the starter (first at submission 3 and 1); the strong list reaches the
  best published packing at submission 20. No other arm beats the starter (rebase's 2.541421 is a jitter of the
  starter grid), also now that numpy and scipy are available.
- The model knows the method and does not choose it: gpt-5.4-mini's own first list contains a scipy optimizer.
  Shown the same lists in one chat and asked to pick, it wrote a hand-made template 40 of 40 times.
- rebase 2.541 vs fnf 2.535: on this task the flush adds nothing over re-showing the best program.
- Weak points: 1 seed (fnf ranged 2.19-2.54 over 5 seeds in main-01); the optimizer is a known answer for this
  task; assigned arms lose 30 % of submissions to 60 s timeouts and shape errors; assign_mini's best program has no
  test score (the rerun at close did not return a score).

**ahc014** (starter 0.2217; 2.6 USD). Examples: best assign_mini-s0 s0031 0.3714, invalid assign_sol-s0 s0000
(checker: no dot at a used corner). Earlier arms are main-01 (pure Python, which did not affect this task).

| Arm | Best (val) | Test | Valid | USD |
|---|---|---|---|---|
| forget (main-01) | 0.439 | | | |
| fnf_assign, list by gpt-5.4-mini | 0.371 | 0.381 | 0.80 | 0.62 |
| basin (main-01) | 0.362 | | | |
| forget_assign, list by gpt-5.4-mini (forget + one listed method per agent at each epoch) | 0.324 | 0.318 | 0.63 | 0.60 |
| fnf (main-01) | 0.296 | | | |
| fnf_undirected (branches told what was tried, no method named; SwarmResearch 2607.02807) | 0.295 | 0.280 | 0.78 | 0.66 |
| halving (8 chats, drop half at 25/50/75 %; 2607.18235) | 0.294 | 0.281 | 0.70 | 0.65 |
| fnf_assign, list by gpt-6.1-sol | 0.242 | 0.226 | 0.45 | 0.67 |
| single (main-01) | 0.240 | | | |

- Prediction refuted: no assigned arm beats forget (0.371 vs 0.439).
- fnf, fnf_undirected, halving and parallel (main-01) all stop at 0.294-0.296, the score of greedy rectangle
  completion. assign_mini left it twice, each time on the first submission of an assigned branch (f1b2 0.368,
  f2b2 0.371).
- The strong list hurt: gpt-6.1-sol listed beam search, MCTS, large-neighbourhood search; gpt-5.4-mini's programs
  for them were invalid or made no move (18 of 40 valid, 12 of those at the starter score). A list is only useful
  if the agent can implement it.
- forget_assign 0.324 < forget 0.439 (prediction: above 0.439; refuted). Each of the 16 assigned methods got 2-3
  submissions (4 agents share 10 per epoch), and 15 of 40 programs were invalid: assignment replaced forget's
  refinement of one shared program with 16 fresh implementations.
- Weak points: 1 seed; forget and basin were not rerun in this experiment.

Literature checked 2026-11-15 (two subagent surveys with tools/exa.py, numbers not re-verified at the papers): no
paper found uses Fork-and-Flush or Forgetting as a baseline, and none combines fork, flush and one listed method
per fresh branch. Closest: SwarmResearch 2607.02807 (orchestrator told not to prescribe ideas), LEVI and
HoliDivEvolve 2610.38407 (diverse seeds once at the start), Anthropic's weak-to-strong researcher blog (a pool of
specific ideas did worse than loose directions).

### circles26/swe2-01 (SWE-2 via Devin CLI, 1 seed, numpy/scipy available, stopped at 7-9 of 40 by the owner)

`results/circles26/swe2-01/summary.json`; examples: best single-s0 s0003 2.635971, invalid forget-s0 (crash).
`devin:swe-2-medium` (Devin Pro plan, free model; no token counts).

- Every arm reaches the best published sum (about 2.635-2.636) within 9 submissions, a single chat included
  (single 2.63597 at submission 4; fnf 2.63590 at 4; basin 2.63598 at 6; parallel 2.63097, forget 2.63304 so far).
- 49 of 49 programs call a numerical optimizer (pilot-02 regex), against 5 of 800 for gpt-5.4-mini in main-01.
  SWE-2 starts in the optimizer basin, so there is no anchoring to undo: circles26 separates strategies only for
  the weak model. Caveat: the gpt-5.4-mini runs had no numpy/scipy (see the environment bug above).

### ahc014/main-01 (1 seed, 40 submissions, gpt-5.4-mini, pure Python, commit 892e7e1, about 4.6 USD)

`results/ahc014/main-01/compare.json`; examples: best forget-s0 s0022 0.4388 (adds 45-degree rectangles), invalid
forget-s0 (checker: overlapped rectangles). Starter (no operations) 0.2217.

| single | parallel | fnf_keep (fork, no flush) | fnf | basin (ours) | forget | randflush |
|---|---|---|---|---|---|---|
| 0.240 (1.29 USD) | 0.295 | 0.259 | 0.296 | 0.362 | 0.439 | stopped at 30 |

- Every arm with a flush beats every arm without one: forget 0.439, basin 0.362, fnf 0.296 vs fnf_keep 0.259,
  single 0.240; fnf vs fnf_keep (+0.037) is the effect of the flush alone. One seed: a hint, not a result.
- Weak point: the judge put all 40 basin-run submissions into one basin ("greedy rectangle completion", see
  `basin-s0_basins.json`), so its 5 flushes were set by the window, not by a basin change. The judge is too coarse
  for this task; the post-hoc labels must be checked against code before any basin claim.

### circles26/main-02 (1 seed, new arms, pure Python)

basin-s0 2.457 (3 flushes, 6 basins), fnf_keep-s0 2.420, randflush stopped at 21 of 40. Same-seed main-01 arms:
single 2.514, parallel 2.474, forget 2.386, fnf 2.187. One seed of a task where no arm beats the starter: no
conclusion. `results/circles26/main-02/compare.json`.

### circles26/main-01 (4 arms x 5 seeds x 40 submissions, gpt-5.4-mini, commit 58c7edf, 6.37 USD)

`results/circles26/main-01/compare.json`; examples (`examples.json`): best fnf-s2 s0036 2.541415, invalid
single-s3 s0000 (overlap).

| Arm | Final best per seed | Mean | Mean at 0.145 USD | Above starter | Optimizer code | USD per run |
|---|---|---|---|---|---|---|
| single | 2.514, 2.020, 2.387, 1.674, 2.106 | 2.140 | 2.109 | 0/5 | 0/200 | 0.62 |
| parallel (best of 4) | 2.474, 1.948, 2.346, 2.413, 2.528 | 2.342 | 2.297 | 0/5 | 1/200 | 0.25 |
| forget (team + 3 flushes) | 2.386, 2.494, 2.155, 2.480, 2.428 | 2.389 | 2.341 | 0/5 | 1/200 | 0.19 |
| fnf (forks at 0, 33, 66 %) | 2.187, 2.529, 2.541, 2.413, 2.517 | 2.438 | 2.396 | 1/5 | 3/200 | 0.23 |

- Same order as pilot-02, at matched submissions and at matched spend: fnf > forget > parallel > single. fnf vs
  single: rank-sum one-sided p = 0.028 (5 vs 5), so suggestive, not settled.
- The starter is still almost never beaten: the one run above it (fnf-s2, 2.541415 vs 2.541380) is a jitter of
  the starter grid. With gpt-5.4-mini the task is dominated by hand-placed layouts; numerical optimizers appear in
  5 of 800 submissions. The ranking is about how far each arm falls below the starter, not about finding a new
  basin. Single runs cost 2.5x more per run (one growing chat).

### circles26/pilot-02 (3 arms x 3 seeds x 30 submissions, gpt-5.4-mini, 2.19 USD for the 8 finished runs)

`results/circles26/pilot-02/summary.json`, examples in the same folder.

| Arm | Final best per seed | Mean | Submissions with optimizer code |
|---|---|---|---|
| single | 1.993, 1.580, 1.974 | 1.85 | 0 / 90 |
| parallel (best of 4) | 2.546, 2.426, 2.541 | 2.50 | 2 / 90 |
| fnf | 2.328, 2.494, 2.588 (crashed at 26) | 2.47 | 4 / 86 |

- Single runs never wrote an optimizer in 90 submissions and stalled early (seed 1: best at submission 2, none
  better in the next 28). The only clear gain over the starter (2.588 vs 2.541) came from fnf after a fork.
- Weak points: 3 seeds; almost every run ends at or below the starter, because the model is not told the
  starter's score and rewrites from scratch; "optimizer" is a regex on the code, not the basin judge; fnf lacks
  the paper's opening fork at 0%; the budget is matched on submissions, not tokens (single cost 1.21 USD for 3
  runs, fnf 0.30 for 2); fnf-s2 died on an API read timeout (network retries added after).
