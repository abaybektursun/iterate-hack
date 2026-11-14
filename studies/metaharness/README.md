# metaharness: how much the meta-review layer improves the research

Measures whether the `team-meta-review` skill, `tools/cycle.py` and the `meta/<name>.md` entries make the swarm answer
questions faster and with less waste. Plan: `specs/SPEC1.md`. Parts A and B have run; C and D have not.

## Files

| Path | What it is |
|---|---|
| `specs/SPEC1.md` | The plan: metrics M1 to M7, Parts A to D, threats, closest published work. |
| `data/interventions_v1.json` | The five meta-review entries of 2026-11-14: slowest stage, change, made or not. |
| `analysis/scorecard.py` | Part A. Stage minutes per work item with GPU jobs, from the board table, events and job records. |
| `jobs/shard_cell.py` | Shard k of N of an rlneurons cell through the unchanged `run_cell.py` (the change the 21:21 entry named). |
| `analysis/replay.py` | Part B readout: minutes, counts and row comparison per arm, from the jobs' own records. |
| `analysis/replay_extra.py` | Part B: the record of a job cancelled in the queue, and the paired v3 scores of two arms. |

Run, from the repository root (the replay scripts need `uv run tools/gpu.py get <job>` for each job first):

```
uv run --with boto3 --with modal python -m studies.metaharness.analysis.scorecard
uv run --with modal --with boto3 python -m studies.metaharness.analysis.replay --arm whole_h200=<job> --arm shard4_h100=<4 jobs> --reference whole_h200 --committed whole_h100=studies/rlneurons/results/day1/hard328_base_cue_t10-01/metrics.json
uv run --with modal --with boto3 python -m studies.metaharness.analysis.replay_extra --cancelled whole_b200=<job> --paired shard4_h100=<4 jobs> whole_h200=<job>
```

Raw answers are in sameraslan's Modal Volume `iterate-runs` under the job ids in each `run.json`.

## Numbers

### Part A: what the session's records show (`results/scorecard/all-01/metrics.json`, read 22:49 UTC)

- 21 work items, 5 with GPU jobs. 28 jobs, 13 of them with no end time (7 of abaybektursun's, whose `jobs.json` in the
  team store is from 20:40 UTC; a `traces.py push` fills them).
- Day-1 #1 (work-d8aa69): 55.9 min from the idea to the claim, 0.0 to the first job, 50.9 run (median of 3 jobs),
  2.5 to the answer, 59.3 claim to close.
- No meta-review entry has work items with jobs on both sides, so Hypothesis A is not testable yet.
- Of the 5 entries, 2 made a change (A1: claim Day-1 #1 and #2, skill rename; A3: Exa warning hook). The two changes
  aimed at the job stage (A2 sharding, A4 the b200 class) were recommended and not made.

### Part B: the named changes applied to one cell (`results/replay/summary-01/metrics.json`)

Cell: hard328, base with cue, T 1.0 / top-p 1.0, seed 3000000, 328 problems, grader v3, commit d34f868. One run per arm.

| Arm | Change from entry | Cell minutes | GPU minutes | Generation min | Right of 328 | Cap hits | Artifact |
|---|---|---|---|---|---|---|---|
| whole, H100 | none (the Day-1 run, abaybektursun's job e72c) | 51.5 | 51.5 | 50.7 | 164 | 77 | `studies/rlneurons/results/day1/hard328_base_cue_t10-01/` |
| 4 shards, H100 | A2 (21:21), predicted about 4x | 15.6 | 60.2 | 13.2 | 155 | 64 | `results/replay/shard4_h100-01/` |
| whole, B200 | A4 (22:13) | never started: 51.4 min in the queue, cancelled | 0 | | | | `results/replay/whole_b200-01/` |
| whole, H200 | none: Modal gave the h100 class an H200 | 38.6 | 38.6 | 36.5 | 168 | 74 | `results/replay/whole_h200-01/` |

- Sharding cut the cell from 51.5 to 15.6 minutes (3.3 times; generation 3.8 times) for 17 % more GPU minutes.
  The 51.5 is the script's wall time and leaves out about 0.5 min of `setup_vllm.sh`; the 15.6 is the longest shard's
  whole container time.
- The entry's claim "rows do not change" is refuted: 8 of 328 answers have the same text as the whole H200 run.
  Sampling at T 1.0 depends on what else is in the batch, on the GPU, or on both; this run cannot separate them.
- Accuracy: 155 sharded against 168 whole (H200), paired: both right 135, sharded only 20, whole only 33, exact sign
  test p = 0.098 (`results/replay/paired-01/metrics.json`). Against the whole H100 run (164) only the counts exist.
  Open: a second whole H100 run in one workspace gives the run-to-run spread that this difference has to exceed.
- The H200 has 56,679 KV blocks against 29,067 on the H100 and ran the whole cell 1.3 times faster, which is the
  mechanism entry A4 named. Its 12.3 min of queue came from this study's own four shards holding the H100 slots.
- Each arm's `examples.json` holds one answer scored right and one scored wrong, with prompt and text.
