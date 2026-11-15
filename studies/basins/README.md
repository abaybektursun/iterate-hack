# basins: idea and strategy basins (idea-1d9755, idea-65a86d)

Two experiments that use the same instrument: an LLM judge places items in 2D by *method* (triplet judgments "is
B or C closer to A?", t-STE), and groups them into basins. Method from Fork-and-Flush (arXiv 2610.07447) and the
Bespoke Labs post "How models explore ideas" (2026-11-10).

1. **strategy** (idea-65a86d): sampled MATH-500 solutions of the cued base vs RL-Zero-Math. Question: does RL use
   fewer strategies per problem, and what share of RL's correct answers lie in strategies the base never used
   (new capability vs sharpening)? Prior: Lee et al. 2606.29985 Table 2 (Cov@16 drops 10-34% after GRPO,
   Qwen2.5-3B/7B). Not yet measured for the Olmo 3 pair. Status: code ready, no GPU run yet.
2. **swarm** (idea-1d9755, work-4dfcf9): the team's board items. Question: how many idea basins does the swarm
   visit, and which plausible directions does it never visit? Status: first map done (main-01).

All code runs from the repository root with the root on `PYTHONPATH`.

## Layout

| Path | What it is |
|---|---|
| `jobs/strategy_gen.py` | GPU. k samples per problem from one model (base + cue, or RL plain), T 1.0 / top-p 1.0, cap 16,384, 42 MATH-500 problems (6 per subject, seed 0). Inputs: `studies/rlneurons/data/rln4/`. Grade: rlneurons grader v3. |
| `jobs/strategy_judge.py` | GPU. Judge `Qwen/Qwen3-30B-A3B-Instruct-2507-FP8` (rev 5a5a776). Blind method summaries, R=3 shuffled partitions, triplets in both orders, two controls (duplicates must share a group; two problems must not). |
| `analysis/strategy_analyze.py` | Laptop. Strategy counts rarefied to equal size, base 0-15 vs RL 0-15 with base and RL half-splits as nulls, Cov-like count on correct samples, RL-only share, shuffle ARI, t-STE held-out accuracy vs shuffled-id null. |
| `analysis/strategy_page.py` | Laptop. One self-contained HTML page with a map per problem. |
| `lib/embed.py` | t-STE, held-out triplet accuracy, bootstrap intervals (both experiments). |
| `prep/swarm_export.py` | Laptop, read-only. Every board item (open and closed) and comment, via the `new` index. |
| `analysis/swarm_judge.py` | Laptop. OpenAI judge (`--backend claude` only with the person's consent): possible directions from DIRECTION.md, partitions, triplets, per-direction coverage, planted-copy control. |
| `analysis/swarm_analyze.py` | Laptop. Basins, coverage, moves, t-STE map and checks. |
| `analysis/swarm_scores.py` | Laptop, one judge call (~0.01 USD). Scored configurations from result posts; each row's quote must be in the post. |
| `analysis/swarm_lineage.py` | Laptop, one judge call (~0.06 USD). Idea tree: earlier items each item builds on, labelled variation / combination / refinement / result_of / claims / critique; ids teammates named are kept. |
| `analysis/swarm_page.py` | Laptop. The swarm map page with replay and leaderboard. |
| `analysis/swarm_landscape.py` | Laptop. The same map as one full-screen 3D surface (page "Basin Atlas Landscape", WebGL 2, no library): each judge group is a basin whose depth grows with its board items, each possible direction is a pin that disappears when a board item works on it, replay in board order. Reads `summary.json` and `map.json`, writes `swarm_landscape.html` (board text, not committed). Basin centres are the map centroids pushed at least 0.245 apart; item offsets are shrunk by 0.45. Names on the picture come from `SHORT` in the file; the panel shows the judge's names. |

## Run (strategy)

```
# smoke: 2 problems, k=4
uv run tools/gpu.py submit h100 --hours 1 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.basins.jobs.strategy_gen --model base --k 4 --n-problems 2 && /opt/rln-vllm/bin/python -m studies.basins.jobs.strategy_gen --model rl --k 4 --n-problems 2"
uv run tools/gpu.py submit h100 --hours 1 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.basins.jobs.strategy_judge --gen /runs/<gen-job-id> --n-controls 2"
# full: --k 32 on both models (2,688 samples), then the judge on that job
uv run tools/gpu.py get <judge-job-id>
bash studies/basins/run.sh studies.basins.analysis.strategy_analyze --judge runs/<judge-job-id> --out studies/basins/results/strategy/main-01
python3 studies/basins/analysis/strategy_page.py studies/basins/results/strategy/main-01
```

Tested on planted data only (laptop): base 4 strategies vs RL 2 gives main 2.0, nulls 0.0, RL-only share 0.0,
t-STE held-out 1.0 vs 0.52 shuffled. A judge that lumps everything into one group fails the two-problem control.

## Results

### swarm/main-01 (board snapshot 2026-11-14 21:36 UTC, 42 items; judge gpt-6.1-sol)

Artifacts: `results/swarm/main-01/summary.json`, `run.json` (commands). The map page is
https://claude.ai/artifact/AABRqx5XZzFrPzBbgaYeYy (private); `map.json` and the page hold teammates' board text and
stay in `runs/` and `results/` uncommitted (rebuild with the commands in `run.json`).

- 12 of 20 possible directions (judge's list from DIRECTION.md alone) are pursued by at least one board item; both
  board orders agree on all 20. Untouched: verifier-free branch search, draft-critique-revise, entropy-adaptive
  sampling schedules, fixed few-shot demos, structured reasoning prompts, layer-localized weight-difference edits,
  training-free context compaction, alternative truncation rules (min-p, top-k, typical).
- 9 basins (judge groups), all visited; 12 of 42 items (29 %) are in the two tooling/infrastructure basins.
  33 moves between basins by the same person, 13 to a basin new for that person.
- Instrument: t-STE held-out triplet accuracy 0.85 vs 0.51 on shuffled ids (Bespoke reports 0.89); triplets
  consistent across the two orders 714/766; partition ARI across orders 0.84; planted copies (ctl-1, ctl-2 of
  work-0b7cb3) share the original's group in both orders and are its nearest map neighbours. Weak point: k-means
  on the 2D map (k=3 by silhouette) agrees poorly with the judge's 9 groups (ARI 0.13), so basins come from the
  judge's grouping, not from map clusters.
- Leaderboard (9 configurations from 5 result posts, as posted, grader v3 ranked): best base with one sample 82.0 %
  (cue, T 1.0), cue + restart 82.8 % (more tokens), RL at T 1.0 92.6 %; gap 10.6 points.
- Judge choice: gpt-5.4-mini is not usable here (triplets consistent across orders 359/767, near chance; its
  partition returned duplicate ids). gpt-6.1-sol costs about 1.1 USD per full map.

### swarm/main-02 (board snapshot 2026-11-14 22:48 UTC, 72 items; judge gpt-6.1-sol, same 20 directions as main-01)

Artifacts: `results/swarm/main-02/summary.json`, `run.json`. Page: same link as main-01 (version 5).

- Still 12 of 20 directions pursued (both orders agree 20/20); the same 8 untouched. The 30 new items went to
  weight and neuron interventions (11 items), mechanistic readouts (11), coordination and process (10).
- 21 of 72 items (29 %) are in the two tooling/coordination basins, as in main-01.
- Instrument: t-STE held-out 0.80 vs 0.48 shuffled; order consistency 1016/1120; partition ARI 0.95; both planted
  copies share the original's group in both orders, one is 12th nearest on the map (map placement is looser).
- Leaderboard now split by benchmark: MATH-500 best one-sample base 82.0 vs RL 92.6; hard-328 base+cue 50.0 vs RL 62.8.
- Idea tree (`swarm_lineage.py`, ~0.06 USD): 100 links (refinement 55, result_of 21, claims 9, variation 5,
  combination 2, critique 2, named-only 6); the judge also found 33 of the 39 links teammates wrote as ids. 22 roots,
  longest chain 7, 29 items with two or more parents, 25 links cross basins. The best one-sample base result
  (result-c36598, 82.0 %) is a root: posted from work done before the swarm started, so no swarm lineage beats it yet.

### swarm/main-03 (board snapshot 2026-11-15 04:08 UTC, 218 items; judge gpt-6.1-sol, same 20 directions as main-01)

Artifacts: `results/swarm/main-03/summary.json`, `run.json` (commands, retries, judge tokens: 104 calls, 2.78 M prompt
and 0.20 M completion tokens). Page: https://claude.ai/artifact/QuKMCQvQDbiF88Anc5m8Xb (Basin Atlas Live, private;
holds teammates' board text). `map.json` and `swarm_map.html` stay uncommitted, as for main-01 and main-02.

- 16 of 20 directions pursued (both orders agree 20/20), up from 12. Charted since main-02: fixed few-shot
  demonstrations, draft-critique-revise, alternative truncation rules (min-p), layer-localized weight-difference
  edits. Still untouched: structured reasoning prompts, entropy-adaptive sampling schedules, training-free context
  compaction, verifier-free branch search.
- 12 basins, all visited; largest 15 % (spectral neuron and localized interventions, 32 items); 10.8 effective
  basins. 50 of 218 items (23 %) are in the two tooling/coordination basins; 20 items in two basins are the gpuprice
  project, which shares the board. The basin holding the best base row (prompt cues, demonstrations and revision)
  has 7 items and 5 of the 20 directions.
- 144 moves between basins by the same person, 22 to a basin new for that person (85 % go back).
- Instrument: t-STE held-out 0.73 vs 0.52 shuffled (main-02 0.80 vs 0.48); order consistency 2572/2878; partition
  ARI 0.82 (main-02 0.95); both planted copies (of result-0018d3) share the original's group in both orders, but are
  18th and 20th nearest on the map: placement is looser at 218 items. k-means vs judge groups ARI 0.24.
- Idea tree: 450 links (refinement 175, result_of 133, claims 33, critique 30, variation 26, combination 11,
  named-only 42); the judge found 132 of the 174 links teammates wrote as ids. 25 roots, longest chain 13, 151 links
  cross basins. Most built on: work-02efb7 (25 children), result-5d032f (15).
- Leaderboard: `summary.json`'s `best_base_pct` (95.1) and `best_base_one_sample_pct` (92.0) are wrong as headlines:
  they come from an 82-problem RL-length quartile and from Think-SFT on the first 100 problems, which the scores
  judge labelled base; `rl_reference_pct` 96.4 is a pass@4 oracle. Restricted to full sets, one sample per problem,
  no oracle/vote/restart/superseded rows, with other checkpoints and weight edits apart (55 of 136 rows): best
  untrained base 87.5 % (cue + 3 Math-RL-written solved examples, n=497, result-6d422d), cue alone 82.0 %, RL 92.6 %;
  best other checkpoint Think-SFT + cue 90.8 %.
- Pipeline changes for this run: `swarm_judge.py --repair-ids` (one mistyped id in a partition answer is mapped to
  the one missing id of the same kind and logged; anything else still stops the run); `swarm_scores.py` reads
  thousands separators and drops, with a list in `scores_dropped.json`, rows whose score is not in their quote
  (here 50 gpuprice skill values).
