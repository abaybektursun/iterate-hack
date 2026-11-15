# Cells and routes, round-11

Written 2026-11-15T20:22:55 UTC. Plan `specs/SPEC_engine_v11.md`. Families: training (7), weights (6), run-02 (2), problems (1), stopping (4), sampling (6), grader (6), s2 (1), s4 (1), s6 (1); 37 forecasters (each reader is its own family). 0 cells or routes dropped (cells.json "dropped"); 0 turned into targets on the open work item that answers them (cells.json "converted"). Separation = readouts whose forecasters split into a low and a high side (every low interval below every high interval) with 2 or more families on each side.

Left out of the ranking (record at or below -2 nats): none.

- Routes: 0 of 2 have a median forecast above the stored subset count of the row at the nearest tokens (none); 0 have no baseline.
- Cells: 0 of 2 have a readout that splits with 2 or more families on each side (none).

## Every merged cell

| cell | model | prompt | set | n | base only | GPU minutes | separation | per minute |
|---|---|---|---|---|---|---|---|---|
| r11-m01 | base Olmo-3-1025-7B (untrained) | plain | hard328 | 328 |  | 45 | 0 | 0 |
| r11-m02 | base Olmo-3-1025-7B (untrained) | plain (no cue, no opening text) | math500 | 100 |  | 110 | 0 | 0 |

## List A: top 10 by separation per GPU minute

### r11-m01: base Olmo-3-1025-7B (untrained); plain; hard328, n 328

GPU minutes 45 (proposers' guess). Separation 0 readouts split with 2 or more families on each side, 0 per minute. Job `jobs/run_cell.py`.

Cell: {"model": "base Olmo-3-1025-7B (untrained)", "prompt": "plain", "set": "hard328", "n": 328, "sampling": "T 0.6, top-p 1.0, seed 3000000", "samples": 1, "grader": "v3", "cap": 4096}

Command: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt plain --set hard328 --temperature 0.6 --top-p 1.0 --max-tokens 4096 --seed 3000000 --commit $(git rev-parse HEAD)"`


#### r11-m01-r1: right answers of 328 under grader v3 (cap hits counted wrong), one sample of the autobench method's own sampling (plain, T 0.6, cap 4,096); compare with the plain T 0.6 single sample at 16,384 (107, result-099916) (right answers of 328)

- proposed by run-02/f2-m01 (c01): 66 [52, 82]; says round-09/training-m04 gives 98 (its blind forecast: 96). Mechanism a says the 4,096 cap removes about half of the base's right hard328 answers whatever the register, so the score falls well below 107. Mechanism b says plain-register answers are short and the cap rarely binds, so the score stays near 107. This separates cap against register as the cause of the vote's 139.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 90 | [76, 104] |  |
| reader-2 | reader-2 | 90 | [78, 102] |  |
| round-09/training-m04 | training | 96 | [82, 110] |  |
| run-02/f2-m01 | run-02 | 84 | [70, 98] |  |
| round-09/stopping-m01 | stopping | 94 | [80, 108] |  |
| round-09/stopping-m04 | stopping | 90 | [76, 104] |  |
| run-03/f2-m05 | stopping | 98 | [84, 110] |  |
| round-09/sampling-m03 | sampling | 88 | [74, 102] |  |
| run-04/f2-m04 | sampling | 88 | [74, 102] |  |
| round-09/sampling-m05 | sampling | 90 | [76, 104] |  |
| run-04/f2-m03 | sampling | 88 | [74, 102] |  |
| round-09/sampling-m01 | sampling | 88 | [73, 103] |  |
| round-09/grader-m04 | grader | 84 | [68, 100] |  |
| round-09/grader-m01 | grader | 85 | [68, 102] |  |
| round-09/grader-m06 | grader | 92 | [77, 106] |  |
| run-08/f2-m01 | grader | 85 | [70, 100] |  |

Theory says nothing: run-06/f2-m03, round-09/training-m06, round-09/training-m05, round-09/training-m03, round-09/training-m01, round-09/training-m02, run-05/f2-m01, run-05/f2-m03, run-05/f2-m06, run-05/f2-m04, round-09/weights-m06, round-09/weights-m04, run-02/f2-m04, run-07/f2-m02, run-03/f2-m02, round-09/sampling-m06, round-09/grader-m02, round-09/grader-m05, round-11/s2-b, round-11/s4-b, round-11/s6-b.


### r11-m02: base Olmo-3-1025-7B (untrained); plain (no cue, no opening text); math500, n 100

GPU minutes 110 (proposers' guess). Separation 0 readouts split with 2 or more families on each side, 0 per minute. Job `studies/theory/jobs/free_cell.py`.

Cell: {"model": "base Olmo-3-1025-7B (untrained)", "prompt": "plain (no cue, no opening text)", "set": "math500", "n": 100, "sampling": "T 0.6 / top-p 1.0, seed 71000000", "samples": 6, "grader": "v3, plurality vote over 6", "cap": "8,192 generated tokens; the same answers also scored with every answer longer than 4,096 tokens counted as no answer"}

Command: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model base --set math500 --n 100 --temperature 0.6 --top-p 1.0 --samples 6 --max-tokens 8192 --seed 71000000 --commit $(git rev-parse HEAD)"`


#### r11-m02-r1: From answers.jsonl: vote-over-6 right answers at cap 8,192 minus vote-over-6 right answers when every sample with more than 4,096 generated tokens is treated as giving no answer (same text, paired by problem). (right answers of 100 (difference, 8,192 view minus 4,096 view))

- proposed by run-02/f2-m01 (c02): 4 [2.5, 8]; says round-09/training-m04 gives 0.5 (its blind forecast: 1). Mechanism a says the 4,096 cap removes complete long solutions, so raising it lifts the vote. Mechanism b says long plain T 0.6 samples are loops or repeated wrong values, so the vote barely moves.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 1 | [-1, 3] |  |
| reader-2 | reader-2 | 1 | [-1, 3.5] |  |
| round-09/training-m04 | training | 1 | [-1, 3] |  |
| run-02/f2-m01 | run-02 | 1 | [-1, 4] |  |
| run-02/f2-m04 | run-02 | 0.5 | [-2, 3] |  |
| round-09/stopping-m01 | stopping | 0.5 | [-1.5, 3] |  |
| round-09/stopping-m04 | stopping | 1 | [-1, 3.5] |  |
| run-03/f2-m05 | stopping | 0.5 | [-1, 2.5] |  |
| round-09/sampling-m03 | sampling | 1 | [-1.5, 4] |  |
| run-04/f2-m04 | sampling | 1 | [-1.5, 4] |  |
| round-09/sampling-m06 | sampling | 1 | [-1.5, 4] |  |
| round-09/sampling-m05 | sampling | 1 | [-1, 4] |  |
| run-04/f2-m03 | sampling | 1 | [-1.5, 4] |  |
| round-09/grader-m06 | grader | 1 | [-1, 3.5] |  |
| round-09/grader-m02 | grader | 0.5 | [-1.5, 3] |  |
| round-09/grader-m05 | grader | 1 | [-1.5, 3.5] |  |

Theory says nothing: run-06/f2-m03, round-09/training-m06, round-09/training-m05, round-09/training-m03, round-09/training-m01, round-09/training-m02, run-05/f2-m01, run-05/f2-m03, run-05/f2-m06, run-05/f2-m04, round-09/weights-m06, round-09/weights-m04, run-07/f2-m02, run-03/f2-m02, round-09/sampling-m01, round-09/grader-m04, round-09/grader-m01, run-08/f2-m01, round-11/s2-b, round-11/s4-b, round-11/s6-b.


## List B: base-only cells, top 10 by the highest forecast of right answers minus the best known base count

## List C: no-reward routes by the margin of the median forecast over the stored subset count of the row at the nearest tokens, in sd

### r11-n01 (s1, round-09/training-m04): Think-SFT with the cue at T 1.0 and the full 16,384 cap, sequential vote of up to 5 samples: stop when the first two answers agree, else keep drawing until a value has 3 votes or 5 samples are used; answer = plurality (ties to the earliest), tokens counted for the drawn samples only.

Model think_sft, 31000 tokens per problem, 200 GPU minutes (proposer's guess). Margin -0.21 sd.

Why, by the gap's parts: Reliability: hard328 share about .43 of the ~42-problem base-to-RL gap (about 18 right answers; .63-.67 on MATH-500), the problems where the model's modal value is right but single samples miss it; the vote recovers most of these, and the extra draws go only to problems whose first two answers split (the 2-2 ties of vote-over-4). Budget (about .27, ~11): kept rather than won, because the full 16,384 cap stays on every sample and no sample is shortened. Answer statement (~.03, ~1): partly, since a malformed final line rarely becomes the mode. Capability (about .27, ~11): not reachable, because the vote cannot exceed problems whose mode is right. Pretraining fixes each problem's distribution over final values and a vote converges to its mode, so the vote's ceiling is the set of modal-right problems and extra samples only resolve near-ties. Spending samples where the first two disagree, and stopping at a 3-vote majority, should give about vote-over-5 accuracy at roughly 3 samples' tokens.

Command: `uv run tools/gpu.py submit l40s --hours 4 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model think_sft --opening-text $' line!\n\nOkay' --set hard328 --shard 0/8 --temperature 1.0 --top-p 1.0 --samples 5 --seed 71000000 --commit $(git rev-parse HEAD)"`

RL arm: `uv run tools/gpu.py submit l40s --hours 4 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model rl --opening-text $' line!\n\nOkay' --set hard328 --shard 0/8 --temperature 1.0 --top-p 1.0 --samples 5 --seed 71000000 --commit $(git rev-parse HEAD)"`


#### r11-n01-r1: route on hard328 (0/8), right answers of 41 (grader v3) after the sequential up-to-5 vote, Think-SFT + cue; compare with think|seq4_restart (238.9/328 at 30,837 tokens, about 29.9 of 41) (of 41)

Proposer 30.5 [27, 34]. Median forecast 33.5; stored 34 of 41 (sd 2.41; Think-SFT + cue, sequential vote, at most 4, restarts, ties to the shortest (mean of 24 orders) (no restart rows: restart = none), 30837 tokens; studies/rlneurons/results/table/hard328-02/table.json think|seq4_restart_short (thinkvote/hard328_sft1_cue_s4-01)); margin -0.21 sd.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 34 | [30, 38] |
| reader-2 | reader-2 | 33.5 | [30, 37] |
| round-09/training-m02 | training | 33.5 | [30, 37] |
| run-02/f2-m04 | run-02 | 34.5 | [30.5, 38.5] |
| round-09/stopping-m01 | stopping | 34 | [30.5, 37.5] |
| round-09/stopping-m04 | stopping | 33.5 | [30, 37] |
| run-04/f2-m04 | sampling | 33 | [29.5, 36.5] |
| round-09/sampling-m06 | sampling | 33.5 | [30, 37] |
| round-09/sampling-m01 | sampling | 33 | [29.5, 36.5] |
| round-09/grader-m04 | grader | 33.5 | [30, 37] |
| round-09/grader-m01 | grader | 33.3 | [29.8, 36.8] |
| run-08/f2-m01 | grader | 33.6 | [30, 37.2] |
| round-09/grader-m02 | grader | 34.5 | [31, 37.5] |
| round-09/grader-m05 | grader | 34 | [30.5, 37.5] |

#### r11-n01-r2: rl on hard328 (0/8), right answers of 41 (grader v3) after the same sequential up-to-5 vote, RL-Zero-Math + cue (of 41)

Proposer 28 [24, 31]. Median forecast 30.25; no baseline.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 30 | [26, 34] |
| reader-2 | reader-2 | 29.5 | [25.5, 33.5] |
| run-06/f2-m03 | training | 30 | [26, 34] |
| round-09/training-m02 | training | 30 | [26, 34] |
| run-05/f2-m04 | weights | 31 | [26, 36] |
| run-02/f2-m04 | run-02 | 30.5 | [26.5, 34.5] |
| run-03/f2-m02 | stopping | 30 | [26.5, 33.5] |
| round-09/stopping-m01 | stopping | 30 | [26.5, 33.5] |
| round-09/stopping-m04 | stopping | 30.5 | [27, 34] |
| run-04/f2-m04 | sampling | 30 | [26, 34] |
| round-09/sampling-m06 | sampling | 30 | [26, 34] |
| round-09/sampling-m01 | sampling | 30 | [26, 34] |
| round-09/grader-m04 | grader | 31 | [27, 35] |
| round-09/grader-m01 | grader | 31 | [27, 35] |
| run-08/f2-m01 | grader | 31 | [27, 35] |
| round-09/grader-m02 | grader | 30.5 | [26.5, 34.5] |
| round-09/grader-m05 | grader | 31 | [27, 35] |
| round-11/s4-b | s4 | 31 | [27, 35] |

### r11-n02 (s5, round-09/training-m04): Think-SFT with the cue sampled at T 1.0 / top-p 1.0 with min-p 0.05 (tail tokens cut), 3 samples per problem at cap 16,384, majority vote over the 3 (ties to the first sample).

Model think_sft, 28800 tokens per problem, 190 GPU minutes (proposer's guess). Margin -0.28 sd.

Why, by the gap's parts: Reliability (about 0.43-0.63 of the gap; on hard328 about 15-20 of the 42-problem one-sample gap are problems the model solves in some samples): min-p plus the vote converts sometimes-solved problems to their right modal value with 3 samples instead of 4-8. Answer statement (about 0.03 of the gap, 1-2 problems): tail draws that garble the final line or drift into another script are cut. Budget (about 0.25, up to about 10 problems) is only partly touched: fewer drifting samples run to the cap. Capability (about 0.27 on hard328) is not won back: the vote cannot move a wrong mode. Pretraining (and SFT on top of it) fixes each problem's distribution over final values and a vote converges to its mode, with samples beyond about eight only resolving ties; cutting the low-probability tail with min-p moves each sample's draw toward that mode, so a 3-sample vote should reach nearly the 4-sample vote's ceiling at three quarters of its tokens.

Command: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model think_sft --opening-text $' line!\n\nOkay' --set hard328 --shard 0/5 --temperature 1.0 --top-p 1.0 --min-p 0.05 --max-tokens 16384 --samples 3 --seed 3400000 --commit $(git rev-parse HEAD)"`

RL arm: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model rl --opening-text $' line!\n\nOkay' --set hard328 --shard 0/5 --temperature 1.0 --top-p 1.0 --min-p 0.05 --max-tokens 16384 --samples 3 --seed 3400000 --commit $(git rev-parse HEAD)"`


#### r11-n02-r1: route on hard328 (0/5), right answers of 66 with grader v3 after the majority vote over 3 samples (ties to the first sample); best known at nearest tokens: Think-SFT + cue sequential vote at most 4, 238.9 of 328 at 30,837 tokens, about 48.1 of 66 (of 66)

Proposer 49 [44, 53]. Median forecast 48; stored 49 of 66 (sd 3.55; Think-SFT + cue, sequential vote, at most 4, restarts, ties to the shortest (mean of 24 orders) (no restart rows: restart = none), 30837 tokens; studies/rlneurons/results/table/hard328-02/table.json think|seq4_restart_short (thinkvote/hard328_sft1_cue_s4-01)); margin -0.28 sd.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 48 | [43, 53] |
| reader-2 | reader-2 | 48.5 | [44, 53] |
| round-09/training-m02 | training | 46 | [41, 51] |
| run-02/f2-m04 | run-02 | 47.5 | [42, 53] |
| round-09/stopping-m01 | stopping | 48 | [43.5, 52.5] |
| round-09/stopping-m04 | stopping | 47.5 | [42.5, 52.5] |
| run-03/f2-m05 | stopping | 48.5 | [43.5, 53] |
| run-04/f2-m04 | sampling | 48 | [43, 53] |
| round-09/sampling-m06 | sampling | 47.5 | [42.5, 52.5] |
| round-09/sampling-m01 | sampling | 48 | [43, 53] |
| round-09/grader-m04 | grader | 48 | [43.5, 52.5] |
| round-09/grader-m01 | grader | 48.3 | [43.5, 53] |
| run-08/f2-m01 | grader | 48.5 | [44, 53] |
| round-09/grader-m02 | grader | 48 | [43.5, 52.5] |
| round-09/grader-m05 | grader | 48.5 | [44, 53] |

#### r11-n02-r2: rl on hard328 (0/5), right answers of 66 with grader v3 after the same majority vote over 3 samples, RL-Zero-Math with the same cue, min-p 0.05, cap and seeds (of 66)

Proposer 43 [38, 48]. Median forecast 44; no baseline.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 44 | [39, 49] |
| reader-2 | reader-2 | 44 | [39.5, 48.5] |
| run-06/f2-m03 | training | 43 | [38, 48] |
| round-09/training-m02 | training | 43 | [38, 48] |
| run-05/f2-m04 | weights | 45 | [39, 51] |
| run-02/f2-m04 | run-02 | 44 | [39, 49] |
| run-03/f2-m02 | stopping | 43.5 | [39, 48] |
| round-09/stopping-m01 | stopping | 44 | [39.5, 48.5] |
| round-09/stopping-m04 | stopping | 44 | [39.5, 48.5] |
| run-04/f2-m04 | sampling | 44 | [39, 49] |
| round-09/sampling-m06 | sampling | 43.5 | [38.5, 48.5] |
| round-09/sampling-m01 | sampling | 44 | [39, 49] |
| round-09/grader-m04 | grader | 44.5 | [39.5, 49.5] |
| round-09/grader-m01 | grader | 44.5 | [39.5, 49.5] |
| run-08/f2-m01 | grader | 44.5 | [39.5, 49.5] |
| round-09/grader-m02 | grader | 44 | [39, 49] |
| round-09/grader-m05 | grader | 44.5 | [39.5, 49.5] |
| round-11/s4-b | s4 | 45 | [40, 50] |
