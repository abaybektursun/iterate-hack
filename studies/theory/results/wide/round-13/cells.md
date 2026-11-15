# Cells and routes, round-13

Written 2026-11-15T22:10:07 UTC. Plan `specs/SPEC_engine_v11.md`. Families: weights (1), training (1), s1 (1), s3 (1), s4 (2), s6 (1); 9 forecasters (each reader is its own family). 0 cells or routes dropped (cells.json "dropped"); 0 turned into targets on the open work item that answers them (cells.json "converted"). Separation = readouts whose forecasters split into a low and a high side (every low interval below every high interval) with 2 or more families on each side.

Left out of the ranking (record at or below -2 nats): none.

- Routes: 1 of 1 have a median forecast above the stored subset count of the row at the nearest tokens (r13-n01); 0 have no baseline.
- Cells: 0 of 0 have a readout that splits with 2 or more families on each side (none).

## Every merged cell

| cell | model | prompt | set | n | base only | GPU minutes | separation | per minute |
|---|---|---|---|---|---|---|---|---|

## List A: top 10 by separation per GPU minute

## List B: base-only cells, top 10 by the highest forecast of right answers minus the best known base count

## List C: no-reward routes by the margin of the median forecast over the stored subset count of the row at the nearest tokens, in sd

### r13-n01 (s4, round-13/s4-b): Cued untrained base at T 1.0 / top-p 1.0 with min-p 0.05 truncation, 4 samples per problem, plurality vote over the finished answers (cap hits cast no vote).

Model base, 35500 tokens per problem, 230 GPU minutes (proposer's guess). Margin +0.31 sd.

Why, by the gap's parts: Wins back part of the reliability part (base right in other samples: 0.43-0.63 of the gap in result-f39ba8, about 13-18 of the 29-answer hard328 vote gap 221 vs 192) and a little of the answer-statement and budget parts (0.03 and 0.25-0.27: tail-token drift, garbled final lines and cap hits; about 1-3 of 328). It cannot reach the capability part (0.27 on hard328, about 8 of 328; 26 of the 36 problems RL's vote wins have no right base sample). Expected net gain over the stored vote over 4: about +4 of 328, or +0.5 to +1 on the 41-problem shard. s4-b says the reward's gain is sharpening the base onto its own most likely complete answer, capped by what the base can already write (pass@k); min-p removes low-probability tail tokens inside each sample, and the vote picks the base's modal complete answer across samples, both without reward and without the loops that a lower temperature causes.

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set hard328 --shard 0/8 --temperature 1.0 --top-p 1.0 --min-p 0.05 --samples 4 --seed 3000000 --commit COMMIT_SHA && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set math500 --shard 0/5 --temperature 1.0 --top-p 1.0 --min-p 0.05 --samples 4 --seed 41000000 --commit COMMIT_SHA`

RL arm: `bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model rl --prompt plain --set hard328 --shard 0/8 --temperature 1.0 --top-p 1.0 --min-p 0.05 --samples 4 --seed 3000000 --commit COMMIT_SHA`


#### r13-n01-r1: route on hard328 (0/8), right answers of 41 with grader v3 after the plurality vote over 4 min-p samples (stored base vote over 4 at 36,902 tokens: 192/328, about 24.0 of 41) (of 41)

Proposer 25 [21, 29]. Median forecast 23; stored 22 of 41 (sd 3.19; base + cue, vote over 4, 36902 tokens; studies/rlneurons/results/table/hard328-02/table.json base|vote4 (day1_3/hard328_base_cue_s4r2-01)); margin 0.31 sd.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 23 | [18, 28] |
| reader-2 | reader-2 | 23 | [18, 28] |
| round-13/s1-a | s1 | 21 | [16.5, 25.5] |
| round-13/s3-a | s3 | 22.5 | [17.5, 27.5] |
| round-13/s4-a | s4 | 23 | [18, 28] |
| round-13/s4-b | s4 | 23 | [18, 28] |
| round-13/s6-b | s6 | 23 | [19, 27] |

#### r13-n01-r2: rl on hard328 (0/8), right answers of 41 with grader v3 after the plurality vote over 4 min-p samples of RL plain (stored RL vote over 4: 221/328, about 27.6 of 41) (of 41)

Proposer 28 [24, 32]. Median forecast 26; no baseline.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 26 | [21, 31] |
| reader-2 | reader-2 | 26 | [21, 31] |
| round-13/s1-a | s1 | 26 | [21.5, 30.5] |
| round-13/s4-a | s4 | 26 | [22, 30] |
| round-13/s4-b | s4 | 26 | [22, 30] |

#### r13-n01-r3: route on MATH-500 (0/5), right answers of 100 with grader v3 after the plurality vote over 4 min-p samples (stored base vote over 4: 446/500, about 89.2 of 100) (of 100)

Proposer 90 [85, 94]. Median forecast 89; no baseline.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 89 | [84, 94] |
| reader-2 | reader-2 | 90 | [85, 94] |
| round-13/s1-a | s1 | 88 | [83, 93] |
| round-13/s3-a | s3 | 89.5 | [85, 94] |
| round-13/s4-a | s4 | 89 | [85, 93] |
| round-13/s4-b | s4 | 89 | [85, 93] |
| round-13/s6-b | s6 | 90 | [86, 94] |

## Rival pairs' cells forecast blind by the two rivals

none
