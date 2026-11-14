# swarm_basins: which research basins the agent swarm explores

Does the swarm explore many research approaches, or hill-climb inside one? It maps every board item into
basins and tracks coverage and switching over time against shuffled nulls. Plan and hypotheses: `specs/SPEC.md`.

Run from the repository root with the root on `PYTHONPATH`. It needs the AWS profile `iterate-ecr`
(README, Setup step 2) and `ANTHROPIC_API_KEY`.

| Path | What it is |
|---|---|
| `specs/SPEC.md` | Question, hypotheses H1 to H3 with what refutes each, instrument conditions, known limits. |
| `lib/basin_map.py` | t-STE loss and fit, held-out agreement, label baselines, 5D clustering, label and switch-rate nulls. |
| `analysis/selftest.py` | Instrument checks on planted data: gradient, cluster recovery, coin-flip judge, switch null. `python -m studies.swarm_basins.analysis.selftest` |
| `analysis/run.py` | The pipeline: board scan, LLM partition (3 times), triplet judgments in both orders, checks, coverage. `uv run studies/swarm_basins/analysis/run.py --arm live` (`--dry` makes no API calls). |
| `results/swarm/<arm>-<nn>/` | One run: `run.json`, `metrics.json`, `map.json` (items with 2D position and basin, timeline), `examples.json`. |
| `runs/swarm_basins/judgments.jsonl` | Judge answer cache, at the repository root, not committed. |

## Numbers

| Number | Value | Artifact |
|---|---|---|
| Planted 5 clusters, 150 triplets per item: ARI of k-means on the 5D fit | 0.935 (2D fit: 0.631) | `analysis/selftest.py` output, commit 159fdb0 |
| Coin-flip judge: held-out triplet agreement | 0.523 (chance 0.5) | same |
