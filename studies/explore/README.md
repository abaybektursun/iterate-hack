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
| `lib/strategies.py` | single, parallel (best of K), fnf, forget, tree (DGM parent rule). Each only chooses chat history and start program. |
| `jobs/run_strategy.py` | One strategy run on one task: `python3 -m studies.explore.jobs.run_strategy --task circles26 --strategy fnf --budget 30 --seed 0 --model gpt-5.4-mini --out runs/explore/circles26/<exp>/<arm>-s<seed>` |
| `analysis/compare.py` | Arms side by side: final best per seed, runs above the starter, best after the same USD spend (the smallest total of any run), optimizer share (pilot-02 regex), best-so-far curves. |
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
