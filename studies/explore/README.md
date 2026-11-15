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
| `lib/loop.py` | One chat call (OpenAI), one scored submission, one JSONL log row; tokens and USD per call. |
| `lib/strategies.py` | single, parallel (best of K), fnf, forget, tree (DGM parent rule). Each only chooses chat history and start program. |
| `jobs/run_strategy.py` | One strategy run on one task: `python3 -m studies.explore.jobs.run_strategy --task circles26 --strategy fnf --budget 30 --seed 0 --model gpt-5.4-mini --out runs/explore/circles26/<exp>/<arm>-s<seed>` |
| `analysis/compare.py` | Arms side by side: final best per seed, best-so-far curve, valid share, cost. |
| `tasks/circles26/` | 26 circles in the unit square, maximize the sum of radii; scorer checks validity (tol 1e-9). Starter 2.54138; best published about 2.636. |

Raw logs and programs stay in `runs/explore/` (not committed).

## Results

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
