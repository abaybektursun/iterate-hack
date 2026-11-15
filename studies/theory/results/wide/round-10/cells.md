# Cells designed by the theories, round-10

Written 2026-11-15T19:44:35 UTC (board read 2026-11-15T19:20:30 UTC). Plan `specs/SPEC_engine_v10.md`. Families: training (6), weights (11), run-02 (2), problems (6), stopping (5), sampling (6), grader (6); 44 forecasters (each reader is its own family). 0 cells or routes dropped by the flag check (cells.json "dropped"). Separation = readouts whose forecasters split into a low and a high side (every low interval below every high interval) with 2 or more families on each side.

Left out of the ranking (record at or below -2 nats): none.

- W1: 6 of 7 no-reward routes have a median forecast above the best known count at equal tokens (r10-n01, r10-n02, r10-n04, r10-n05, r10-n06, r10-n07; needs 4): holds.
- W3: 0 of 39 cells have a readout that splits with 2 or more families on each side (none; needs 5): refuted.

## Every merged cell

| cell | model | prompt | set | n | base only | GPU minutes | separation | per minute |
|---|---|---|---|---|---|---|---|---|
| r10-m01 | Olmo-3-1025-7B base + 1.5 x top-8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Code - base), all layers and modules, stochastic rounding, seed 0 (wsp_edit recipe top8, other rl_code, k 8, scale 1.5) | cue (pair1 prompt + frozen4.json prefill ' line!\n\nOkay') | hard328 | 328: all of hard328 (problems 0-327), covering shard 0/2 (problems 0, 2, ..., 326; 164) and the first 200 problems (0-199); each readout states its problems |  | 95 | 0 | 0 |
| r10-m02 | Olmo-3-1025-7B base + 1.5 x top-8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Math - base), applied only in layers 22-31 (last third), all module families, stochastic rounding, seed 0 | plain (no cue prefilled) | math500 | 100: the first 100 MATH-500 problems (the WSP-1 screen problems) |  | 30 | 0 | 0 |
| r10-m03 | Olmo-3-1025-7B base (untrained) | plain (no cue prefilled) | math500 | 100: the first 100 MATH-500 problems | yes | 80 | 0 | 0 |
| r10-m04 | Olmo-3-1025-7B base + 2.0 x top-1 singular direction per matrix of (Olmo-3.1-7B-RL-Zero-Math - base), all layers and modules, stochastic rounding, seed 0 | cue (frozen4.json prefill) | hard328 | 164: shard 0/2 of hard328 (problems 0, 2, 4, ..., 326) |  | 75 | 0 | 0 |
| r10-m05 | Olmo-3.1-7B-RL-Zero-Math step 100 (revision step_0100 0a45720c), rebuilt as base + 1.0 x (step100 - base) with nearest rounding (endpoint exact) | plain | hard328 | 164: shard 0/2 of hard328 (problems 0, 2, 4, ..., 326) |  | 75 | 0 | 0 |
| r10-m06 | Olmo-3-7B-Think-SFT + 2.0 x (Olmo-3.1-7B-RL-Zero-Math - base), M(2), bf16, seed 0 | cue (frozen4.json prefill) | fresh2026 | 136: all fresh2026 problems (AIME 2026, HMMT Feb and Nov 2026) |  | 75 | 0 | 0 |
| r10-m07 | Olmo-3-1025-7B base - 1.5 x top-8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Math - base) (signed size -1.5), all layers, stochastic bf16 rounding, seed 0 | cue | fresh2026 (136 competition problems from 2026) | 136, all |  | 100 | 0 | 0 |
| r10-m08 | Olmo-3-1025-7B base + 0.5 x top-8 singular directions per matrix of (RL-Math 3.1 - base), written with round-to-nearest bf16 (--rounding nearest) | cue | hard328 | 200: the first 200 problems (--n 200) |  | 105 | 0 | 0 |
| r10-m09 | Olmo-3-1025-7B base + 1.0 x top-8 singular directions per matrix of (RL-Math 3.1 - base), stochastic bf16 rounding, seed 0 | plain (no cue) | hard328 | 200: the first 200 problems (--n 200) |  | 101 | 0 | 0 |
| r10-m10 | Olmo-3-1025-7B base + 1.5 x the top-1 singular direction per matrix of (RL-Math 3.1 - base) (--k 1), stochastic bf16 rounding, seed 0 | cue | hard328 | 200: the first 200 problems (--n 200) |  | 93 | 0 | 0 |
| r10-m11 | Olmo-3-7B-Think-SFT + 2.0 x (Olmo-3.1-7B-RL-Zero-Math - Olmo-3-1025-7B base), the full difference (delta_sum host think_sft, donor rl_math, alpha 2.0, seed 0) | cue (base cue prefilled, RL tokenizer, pair1 prompt, as the stored Think-SFT fresh2026 cells) | fresh2026 | 136 (all problems) |  | 90 | 0 | 0 |
| r10-m12 | Olmo-3-1025-7B base + 1.5 x top-8 singular directions per matrix of (RL-Math 3.1 - base), written with round-to-nearest bf16 (--rounding nearest) | cue | hard328 | 200: the first 200 problems (--n 200) |  | 98 | 0 | 0 |
| r10-m13 | Olmo-3-1025-7B base + 3.0 x top-8 singular directions per matrix of (RL-Math 3.1 - base), stochastic bf16 rounding, seed 0 | cue | math500 | 200: the first 200 problems of MATH-500 (--n 200) |  | 80 | 0 | 0 |
| r10-m14 | Olmo-3-7B-Think-SFT + 1.0 x (Olmo-3.1-7B-RL-Zero-Math - Olmo-3-1025-7B), full difference (delta_sum host think_sft, donor rl_math, alpha 1) | cue | fresh2026 | 136, all |  | 97 | 0 | 0 |
| r10-m15 | Olmo-3-1025-7B base + 1.5 x top-8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Code - base), stochastic bf16 rounding, seed 0 | cue | fresh2026 | 136, all |  | 78 | 0 | 0 |
| r10-m16 | Olmo-3-1025-7B base + 3.0 x the top-1 singular direction per matrix of (RL-Math 3.1 - base) (--k 1), stochastic bf16 rounding, seed 0 | cue | math500 | 200: the first 200 problems of MATH-500 (--n 200) |  | 48 | 0 | 0 |
| r10-m17 | Olmo-3-1025-7B base (untrained, no edit) | cue (frozen4.json prefill ' line!\n\nOkay') | hard328 | 110 problems: shard 0/3 of hard328 (indices 0, 3, 6, ..., 327), spread evenly over the easier and harder halves | yes | 70 | 0 | 0 |
| r10-m18 | allenai/Olmo-3-7B-Think-SFT (as released, no edit) | base pair1 prompt with the cue prefilled as opening text (' line!\n\nOkay', frozen4.json prefill_text), as in the Think-SFT cue cells | math500 | 250 problems: shard 0/2 of MATH-500 (even indices 0, 2, ..., 498) |  | 105 | 0 | 0 |
| r10-m19 | Olmo-3-1025-7B base + 1.5 x top-8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Code - base), all layers, all matrices, stochastic rounding seed 0 (wsp_edit recipe top8, other rl_code, scale 1.5) | cue (pair1 prompt + frozen4 prefill ' line!\n\nOkay') | MATH-500 | 500 (all problems, index 0-499) |  | 90 | 0 | 0 |
| r10-m20 | Olmo-3.1-7B-RL-Zero-Code (released weights, run_code_cell --model rl_code) | plain (RL-Zero-Code template, no prefix ids) | HumanEval+ and MBPP+ (538 problems after the grader check, as result-59ed1a) | 538 (all) |  | 95 | 0 | 0 |
| r10-m21 | Olmo-3.1-7B-RL-Zero-Math minus its top-8 singular directions per matrix (wsp_edit recipe bulk, other rl_math, k 8, stochastic rounding seed 0), the same edit as the hard328 cell of result-284db5 (190 right, 90 cap hits) | cue | MATH-500 | 250 (first 250 problems, index 0-249) |  | 65 | 0 | 0 |
| r10-m22 | Olmo-3-1025-7B base + 1.5 x top-8 singular directions per matrix of (RL-Math 3.1 - base), a new rounding draw (wsp_edit recipe top8, other rl_math, scale 1.5, stochastic rounding seed 1) | cue | hard328 | 164: shard 0/2 of hard328 (problems 0, 2, 4, ..., 326) |  | 75 | 0 | 0 |
| r10-m23 | Olmo-3-1025-7B base + 1.5 x top-8 singular directions per matrix of (RL-Math 3.1 - base), all layers, stochastic rounding (wsp_edit recipe top8, scale 1.5) | cue | hard328 | all 328 problems |  | 65 | 0 | 0 |
| r10-m24 | Olmo-3-1025-7B base + 3.0 x top-8 singular directions per matrix of (RL-Math 3.1 - base), all layers, stochastic rounding (wsp_edit recipe top8, scale 3.0) | cue | MATH-500 | 167 problems: shard 0/3 (indices 0, 3, 6, ..., 498) |  | 55 | 0 | 0 |
| r10-m25 | Olmo-3-1025-7B base + 1.0 x top-8 singular directions per matrix of (RL-Math 3.1 - base), all layers, stochastic rounding (wsp_edit recipe top8, scale 1.0; the edit whose plain answers open 'Okay' in 430 of 500) | cue | MATH-500 | 200 problems: first 400, shard 0/2 (indices 0, 2, ..., 398) |  | 60 | 0 | 0 |
| r10-m26 | allenai/Olmo-3-7B-Think-SFT (no edit) | pair1 prompt (as run_cell), opening text prefilled ' line!\n\n<think>\nOkay': the base cue with an open think block, so the model has a </think> boundary to close | hard328 | 164 problems: shard 0/2 (indices 0, 2, ..., 326) |  | 90 | 0 | 0 |
| r10-m27 | Olmo-3-1025-7B base - 1.0 x top-8 singular directions per matrix of (RL-Code 3.1 - base), all layers, stochastic rounding (wsp_edit recipe top8, other rl_code, scale -1.0) | cue | hard328 | 164 problems: shard 0/2 (indices 0, 2, ..., 326) |  | 95 | 0 | 0 |
| r10-m28 | Olmo-3-1025-7B base + 1.0x the top-8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Math - base), all layers, all matrices (wsp_edit --recipe top8 --scale 1.0, stochastic rounding, seed 0) | plain (no cue) | MATH-500 | 200: the first 200 problems (indices 0-199) |  | 55 | 0 | 0 |
| r10-m29 | Olmo-3-1025-7B base (untrained) | cue | MATH-500 | 500 (all); readout on the 33 problems with 0 of 4 right in the stored Day-1 #3 base cue rows (results/day1_3/math500_base_cue-01/rows.jsonl, attempt 0, samples 0-3) | yes | 100 | 0 | 0 |
| r10-m30 | Olmo-3-1025-7B base + 1.0x the top-8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Math - base) (wsp_edit --recipe top8 --scale 1.0, stochastic rounding, seed 0) | cue | fresh2026 (136 contest problems published in 2026) | 136 (all) |  | 80 | 0 | 0 |
| r10-m31 | allenai/Olmo-3-7B-Think-SFT (no reward), as free_cell runs it (RL tokenizer, pair1 prompt) | plain (no cue, no opening text, no ChatML template) | hard328 | 164: the first 164 problems |  | 95 | 0 | 0 |
| r10-m32 | allenai/Olmo-3-7B-Think-SFT (no reward), rebuilt by wsp_edit --recipe interp --other think_sft --alpha 1.0 (the relay's Think-SFT directory) | cue | fresh2026 | 68: the first 68 problems of fresh2026_v1.json |  | 90 | 0 | 0 |
| r10-m33 | Olmo-3.1-7B-RL-Zero-Math (frozen4.json revision) | plain | hard328 | 164: the first 164 problems |  | 80 | 0 | 0 |
| r10-m34 | Olmo-3-1025-7B base + 1.0x the top-8 singular directions per matrix of (RL-Math 3.1 - base), all layers, stochastic rounding, seed 0 (wsp_edit recipe top8) | cue | fresh2026 | all 136 problems |  | 85 | 0 | 0 |
| r10-m35 | Olmo-3-1025-7B base (untrained) | cue | fresh2026 | all 136 problems | yes | 115 | 0 | 0 |
| r10-m36 | Olmo-3-1025-7B base + 1.5x the top-1 singular direction per matrix of (RL-Math 3.1 - base), all layers, stochastic rounding, seed 0 (wsp_edit recipe top8, k 1) | cue | fresh2026 | all 136 problems |  | 85 | 0 | 0 |
| r10-m37 | allenai/Olmo-3-7B-Think-SFT, written as base + 1.0 x (Think-SFT - base) with nearest rounding (wsp_edit recipe interp), run through run_cell as in the relay study | cue (raw pair1 prompt, cue prefilled) | math500 | first 400 problems (indices 0-399) |  | 115 | 0 | 0 |
| r10-m38 | Olmo-3-1025-7B base (untrained) | cue + the 3 Math-RL-written solved examples of draw 1 (result-6d422d / result-5227b9: MATH-500 problems 0, 1, 2) in context, via run_cell --shots | math500 | first 280 problems the job keeps after leaving out the 3 example problems (MATH-500 indices 3-282) | yes | 115 | 0 | 0 |
| r10-m39 | allenai/Olmo-3-7B-Think-SFT, written as base + 1.0 x (Think-SFT - base) with nearest rounding (wsp_edit recipe interp), run through run_cell | cue (raw pair1 prompt, cue prefilled) | hard328 | shard 0/2: problems 0, 2, 4, ... (164 problems); readout on the ~45 of them in the 90-problem floor list of result-5da8a9 (studies/rlneurons/results/axis/hard328-01/readout.json) |  | 118 | 0 | 0 |

## List A: top 10 by separation per GPU minute

### r10-m01: Olmo-3-1025-7B base + 1.5 x top-8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Code - base), all layers and modules, stochastic rounding, seed 0 (wsp_edit recipe top8, other rl_code, k 8, scale 1.5); cue (pair1 prompt + frozen4.json prefill ' line!\n\nOkay'); hard328, n 328: all of hard328 (problems 0-327), covering shard 0/2 (problems 0, 2, ..., 326; 164) and the first 200 problems (0-199); each readout states its problems

GPU minutes 95 (proposers' guess). Separation 0 readouts split with 2 or more families on each side, 0 per minute. Job `run_cell.py`.

Cell: {"model": "Olmo-3-1025-7B base + 1.5 x top-8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Code - base), all layers and modules, stochastic rounding, seed 0 (wsp_edit recipe top8, other rl_code, k 8, scale 1.5)", "prompt": "cue (pair1 prompt + frozen4.json prefill ' line!\\n\\nOkay')", "set": "hard328", "n": "328: all of hard328 (problems 0-327), covering shard 0/2 (problems 0, 2, ..., 326; 164) and the first 200 problems (0-199); each readout states its problems", "sampling": "T 1.0, top-p 1.0, min-p 0; seed 3000000 + problem index", "samples": "1 per problem, no restarts", "grader": "v3", "cap": "16,384 generated tokens"}

Command: `uv run tools/gpu.py submit l40s --hours 4 -- "bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe top8 --other rl_code --k 8 --scale 1.5 --rounding stochastic --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label code_top8x1.5 --prompt cue --set hard328 --temperature 1.0 --top-p 1.0 --seed 3000000 --commit $(git rev-parse HEAD)"`


#### r10-m01-r1: right answers with grader v3 (cap hits counted wrong) among the 164 problems of shard 0/2 (problems 0, 2, 4, ..., 326) (right answers of 164)

- proposed by run-06/f2-m03 (c01): 93 [86, 100]; says round-10/problems-m06 gives 83 (its blind forecast: 88). f2-m03 says another reward's top-8 directions carry about half of RL's in-domain gain at full dose: on this half of hard328, cued base about 82 and RL about 103, so about 93 (Code top-8 at 1x already gave 178/328, about 89 here). problems-m06 says Code's finishing is calibrated to about 4k-token code answers, so a larger dose stops long hard328 derivations even earlier and falls below the 1x cell, to about 83.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 91 | [80, 102] |  |
| reader-2 | reader-2 | 92 | [82, 102] |  |
| run-06/f2-m03 | training | 92.5 | [84, 101] |  |
| run-05/f2-m03 | weights | 91 | [82, 100] |  |
| run-05/f2-m01 | weights | 95 | [85, 104] |  |
| run-05/f2-m06 | weights | 92 | [83, 101] |  |
| round-10/weights-m05 | weights | 90 | [81, 99] |  |
| run-07/f2-m02 | problems | 92 | [81, 103] |  |
| round-09/problems-m05 | problems | 89 | [78, 100] |  |
| round-10/problems-m06 | problems | 88 | [77, 99] |  |
| run-03/f2-m02 | stopping | 92 | [82, 101] |  |
| round-10/stopping-m04 | stopping | 91 | [81, 100] |  |
| run-04/f2-m03 | sampling | 90 | [80, 101] |  |
| run-08/f2-m01 | grader | 91 | [80, 102] |  |
| round-09/grader-m04 | grader | 90 | [79, 101] |  |
| round-09/grader-m03 | grader | 91 | [80, 102] |  |
| round-09/grader-m01 | grader | 91 | [80, 102] |  |

Theory says nothing: round-09/training-m06, round-09/training-m04, round-09/training-m05, round-09/training-m03, round-10/training-m05, run-05/f2-m04, round-09/weights-m01, round-09/weights-m04, round-09/weights-m06, round-10/weights-m01, round-10/weights-m03, round-10/weights-m06, run-02/f2-m01, run-02/f2-m04, round-10/problems-m03, round-10/problems-m04, round-10/problems-m05, run-03/f2-m05, round-09/stopping-m04, round-10/stopping-m03, round-09/sampling-m03, run-04/f2-m04, round-09/sampling-m05, round-09/sampling-m06, round-09/sampling-m01, round-09/grader-m06, round-10/grader-m06.


#### r10-m01-r2: cap hits (finish reason length at 16,384 tokens) among the 164 problems of shard 0/2 (problems 0, 2, 4, ..., 326) (cap hits of 164)

- proposed by round-10/problems-m06 (c25): 10 [5, 16]; says run-05/f2-m03 gives 25 (its blind forecast: 24). problems-m06 says Code-RL's finishing is calibrated to about 4k-token answers. On long hard328 derivations its directions stop earlier than Math's: at 1x Code already cut cap hits to 41 (Math 46), and at 1.5x it goes below Math's 25 of 328, to about 20 (10 per shard). f2-m03 says a cross-domain edit acts in proportion to input-subspace overlap, about half the in-domain effect: half of Math 1.5x's -52 cap hits gives about 51 of 328, 25 per shard.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 12 | [5, 20] |  |
| reader-2 | reader-2 | 13 | [7, 20] |  |
| run-06/f2-m03 | training | 13 | [6, 21] |  |
| run-05/f2-m03 | weights | 24 | [16, 32] |  |
| run-05/f2-m01 | weights | 13 | [7, 20] |  |
| run-05/f2-m06 | weights | 14 | [8, 21] |  |
| round-10/weights-m05 | weights | 14 | [8, 21] |  |
| run-07/f2-m02 | problems | 18 | [9, 28] |  |
| round-09/problems-m05 | problems | 14 | [6, 23] |  |
| round-10/problems-m06 | problems | 9 | [4, 16] |  |
| run-03/f2-m02 | stopping | 14 | [8, 21] |  |
| round-10/stopping-m04 | stopping | 13 | [7, 20] |  |
| run-04/f2-m03 | sampling | 11 | [5, 18] |  |
| run-08/f2-m01 | grader | 13 | [6, 21] |  |
| round-09/grader-m01 | grader | 13 | [6, 21] |  |

Theory says nothing: round-09/training-m06, round-09/training-m04, round-09/training-m05, round-09/training-m03, round-10/training-m05, run-05/f2-m04, round-09/weights-m01, round-09/weights-m04, round-09/weights-m06, round-10/weights-m01, round-10/weights-m03, round-10/weights-m06, run-02/f2-m01, run-02/f2-m04, round-10/problems-m03, round-10/problems-m04, round-10/problems-m05, run-03/f2-m05, round-09/stopping-m04, round-10/stopping-m03, round-09/sampling-m03, run-04/f2-m04, round-09/sampling-m05, round-09/sampling-m06, round-09/sampling-m01, round-09/grader-m04, round-09/grader-m03, round-09/grader-m06, round-10/grader-m06.


#### r10-m01-r3: cap hits (finish reason length at 16,384 tokens) among the first 200 problems of hard328 (problems 0-199) (cap hits of 200)

- proposed by run-05/f2-m03 (c07): 36 [27, 45]; says round-10/stopping-m04 gives 14 (its blind forecast: 20). f2-m03 lets Code's directions act on math text only through the 0.22-0.26 input overlap, so they give half of Math 1.5x's in-domain cap-hit cut (77 to 18 on all 328, x0.757 for the first 200 where the cued base has about 58). stopping-m04 says any reward's directions write the same commit readout, which Code 1x already showed (41 cap hits, fewer than Math 1x's 46), so Code at 1.5x finishes like Math at 1.5x.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 18 | [9, 28] |  |
| reader-2 | reader-2 | 19 | [11, 28] |  |
| run-06/f2-m03 | training | 20 | [11, 30] |  |
| run-05/f2-m03 | weights | 38 | [27, 49] | round-10/problems-m06, run-04/f2-m03 |
| run-05/f2-m01 | weights | 20 | [12, 29] |  |
| run-05/f2-m06 | weights | 22 | [13, 31] |  |
| round-10/weights-m05 | weights | 22 | [13, 31] |  |
| run-07/f2-m02 | problems | 27 | [16, 39] |  |
| round-09/problems-m05 | problems | 20 | [11, 30] |  |
| round-10/problems-m06 | problems | 13 | [6, 21] | run-05/f2-m03 |
| run-03/f2-m02 | stopping | 21 | [13, 30] |  |
| round-10/stopping-m04 | stopping | 20 | [12, 29] |  |
| run-04/f2-m03 | sampling | 16 | [9, 25] | run-05/f2-m03 |
| run-08/f2-m01 | grader | 19 | [10, 29] |  |
| round-09/grader-m04 | grader | 20 | [11, 30] |  |
| round-09/grader-m01 | grader | 19 | [10, 29] |  |

Theory says nothing: round-09/training-m06, round-09/training-m04, round-09/training-m05, round-09/training-m03, round-10/training-m05, run-05/f2-m04, round-09/weights-m01, round-09/weights-m04, round-09/weights-m06, round-10/weights-m01, round-10/weights-m03, round-10/weights-m06, run-02/f2-m01, run-02/f2-m04, round-10/problems-m03, round-10/problems-m04, round-10/problems-m05, run-03/f2-m05, round-09/stopping-m04, round-10/stopping-m03, round-09/sampling-m03, run-04/f2-m04, round-09/sampling-m05, round-09/sampling-m06, round-09/sampling-m01, round-09/grader-m03, round-09/grader-m06, round-10/grader-m06.


### r10-m02: Olmo-3-1025-7B base + 1.5 x top-8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Math - base), applied only in layers 22-31 (last third), all module families, stochastic rounding, seed 0; plain (no cue prefilled); math500, n 100: the first 100 MATH-500 problems (the WSP-1 screen problems)

GPU minutes 30 (proposers' guess). Separation 0 readouts split with 2 or more families on each side, 0 per minute. Job `run_cell.py`.

Cell: {"model": "Olmo-3-1025-7B base + 1.5 x top-8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Math - base), applied only in layers 22-31 (last third), all module families, stochastic rounding, seed 0", "prompt": "plain (no cue prefilled)", "set": "math500", "n": "100: the first 100 MATH-500 problems (the WSP-1 screen problems)", "sampling": "T 1.0, top-p 1.0, min-p 0; seed 41000000 + problem index", "samples": "1 per problem, no restarts", "grader": "v3", "cap": "16,384 generated tokens"}

Command: `uv run tools/gpu.py submit l40s --hours 1 -- "bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe top8 --other rl_math --scale 1.5 --layers 22,23,24,25,26,27,28,29,30,31 --rounding stochastic --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label top8x1.5_L22-31 --prompt plain --set math500 --n 100 --temperature 1.0 --top-p 1.0 --seed 41000000 --commit $(git rev-parse HEAD)"`


#### r10-m02-r1: right answers with grader v3 (cap hits counted wrong) of the first 100 MATH-500 problems (right answers of 100)

- proposed by round-09/training-m06 (c02): 83 [75, 90]; says run-05/f2-m01 gives 52 (its blind forecast: nothing). training-m06 gives the last third one distinct job, writing the opening cue. With a plain prompt that job is not redundant, so the late-third edit should open answers with the cue and score at the prefilled-cue level on these 100: cue 82, one-matrix layer-31 hand edit 85, full top-8 plain 88. f2-m01 spreads the dial evenly over all layers and gives late layers no special cue role, so a third of the layers gives about a third of the plain gain: 34 + (88 - 34)/3, about 52.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 52 | [33, 80] |  |
| reader-2 | reader-2 | 60 | [35, 87] |  |
| round-09/training-m06 | training | 80 | [62, 92] |  |
| round-10/problems-m03 | problems | 60 | [36, 84] |  |
| run-03/f2-m02 | stopping | 60 | [38, 82] |  |
| round-10/stopping-m04 | stopping | 68 | [45, 88] |  |
| round-09/sampling-m03 | sampling | 57 | [37, 77] |  |
| run-08/f2-m01 | grader | 55 | [33, 77] |  |
| round-09/grader-m03 | grader | 47 | [32, 64] |  |
| round-09/grader-m01 | grader | 55 | [33, 77] |  |

Theory says nothing: run-06/f2-m03, round-09/training-m04, round-09/training-m05, round-09/training-m03, round-10/training-m05, run-05/f2-m03, run-05/f2-m01, run-05/f2-m06, run-05/f2-m04, round-09/weights-m01, round-09/weights-m04, round-09/weights-m06, round-10/weights-m01, round-10/weights-m03, round-10/weights-m05, round-10/weights-m06, run-02/f2-m01, run-02/f2-m04, run-07/f2-m02, round-09/problems-m05, round-10/problems-m04, round-10/problems-m05, round-10/problems-m06, run-03/f2-m05, round-09/stopping-m04, round-10/stopping-m03, run-04/f2-m04, run-04/f2-m03, round-09/sampling-m05, round-09/sampling-m06, round-09/sampling-m01, round-09/grader-m04, round-09/grader-m06, round-10/grader-m06.


### r10-m03: Olmo-3-1025-7B base (untrained); plain (no cue prefilled); math500, n 100: the first 100 MATH-500 problems (base only)

GPU minutes 80 (proposers' guess). Separation 0 readouts split with 2 or more families on each side, 0 per minute. Job `run_cell.py`.

Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "plain (no cue prefilled)", "set": "math500", "n": "100: the first 100 MATH-500 problems", "sampling": "T 1.0, top-p 1.0, min-p 0; sample s of problem i has seed 41000000 + 10000 s + i", "samples": "8 per problem, no restarts", "grader": "v3, plurality vote over the 8 samples (answers grouped with rln4_lib.agree, cap hits and no-answer samples abstain, ties to the lowest sample index)", "cap": "16,384 generated tokens"}

Command: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt plain --set math500 --n 100 --temperature 1.0 --top-p 1.0 --seed 41000000 --samples 8 --commit $(git rev-parse HEAD)"`


#### r10-m03-r1: right answers under the plurality vote over 8 plain samples (grader v3) of the first 100 MATH-500 problems (right answers of 100)

Best known base count given to the forecasters: 90 (result-5d032f; No base-only cell on the board has 8 samples on these 100 problems. Used the best 4-sample base count, vote over 4 after restart, 450/500 on all of MATH-500, scaled to 100. For reference, the prefilled-cue single sample on these first 100 is 82 (result-d2933e).). Highest forecast: round-09/training-m04 72 (-18).

- proposed by round-09/training-m04 (c03): 85 [78, 91]; says round-09/sampling-m03 gives 52 (its blind forecast: 65). training-m04 says the cue picks the register but does not move each problem's modal final value, and a vote converges to that mode. So eight plain samples should vote to about the cued vote's level on these easy problems (cued vote over 4 is 446/500, about 89 per 100), although one plain sample scores only 34 here. sampling-m03 says at T 1.0 most plain base samples (about 400 of 500) open outside the deliberative register, and those openings have much lower accuracy. Votes over such draws stay far below the cued vote, at about 52.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 60 | [46, 74] |  |
| reader-2 | reader-2 | 56 | [42, 69] |  |
| round-09/training-m04 | training | 72 | [55, 88] |  |
| run-02/f2-m01 | run-02 | 63 | [50, 75] |  |
| run-02/f2-m04 | run-02 | 58 | [46, 70] |  |
| round-10/problems-m03 | problems | 48 | [36, 60] |  |
| round-10/problems-m05 | problems | 56 | [43, 69] |  |
| round-09/stopping-m04 | stopping | 58 | [46, 70] |  |
| round-09/sampling-m03 | sampling | 65 | [52, 78] |  |
| round-09/sampling-m06 | sampling | 60 | [47, 73] |  |
| round-10/grader-m06 | grader | 55 | [42, 68] |  |

Theory says nothing: run-06/f2-m03, round-09/training-m06, round-09/training-m05, round-09/training-m03, round-10/training-m05, run-05/f2-m03, run-05/f2-m01, run-05/f2-m06, run-05/f2-m04, round-09/weights-m01, round-09/weights-m04, round-09/weights-m06, round-10/weights-m01, round-10/weights-m03, round-10/weights-m05, round-10/weights-m06, run-07/f2-m02, round-09/problems-m05, round-10/problems-m04, round-10/problems-m06, run-03/f2-m02, run-03/f2-m05, round-10/stopping-m03, round-10/stopping-m04, run-04/f2-m04, run-04/f2-m03, round-09/sampling-m05, round-09/sampling-m01, run-08/f2-m01, round-09/grader-m04, round-09/grader-m03, round-09/grader-m06, round-09/grader-m01.


### r10-m04: Olmo-3-1025-7B base + 2.0 x top-1 singular direction per matrix of (Olmo-3.1-7B-RL-Zero-Math - base), all layers and modules, stochastic rounding, seed 0; cue (frozen4.json prefill); hard328, n 164: shard 0/2 of hard328 (problems 0, 2, 4, ..., 326)

GPU minutes 75 (proposers' guess). Separation 0 readouts split with 2 or more families on each side, 0 per minute. Job `run_cell.py`.

Cell: {"model": "Olmo-3-1025-7B base + 2.0 x top-1 singular direction per matrix of (Olmo-3.1-7B-RL-Zero-Math - base), all layers and modules, stochastic rounding, seed 0", "prompt": "cue (frozen4.json prefill)", "set": "hard328", "n": "164: shard 0/2 of hard328 (problems 0, 2, 4, ..., 326)", "sampling": "T 1.0, top-p 1.0, min-p 0; seed 3000000 + problem index", "samples": "1 per problem, no restarts", "grader": "v3", "cap": "16,384 generated tokens"}

Command: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe top8 --k 1 --other rl_math --scale 2.0 --rounding stochastic --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label top1x2 --prompt cue --set hard328 --shard 0/2 --temperature 1.0 --top-p 1.0 --seed 3000000 --commit $(git rev-parse HEAD)"`


#### r10-m04-r1: cap hits (finish reason length at 16,384 tokens) among the 164 problems of shard 0/2 (cap hits of 164)

- proposed by round-09/training-m05 (c04): 23 [16, 30]; says round-09/weights-m01 gives 5 (its blind forecast: 9). training-m05 puts the stopping decision in directions 2-8 and answer form in direction 1, so doubling direction 1 leaves cap hits near the top-1 at 1x level: 51/328, about 25 on this half (base about 38). weights-m01 says the size of the top direction alone sets how often the model finishes, and about 2x over-commits whether 1 or 8 directions are scaled. Top-1 at 2x should then finish almost everything, as 8 directions at 2x did (5/328), so about 3-6 here.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 12 | [6, 19] |  |
| reader-2 | reader-2 | 12 | [7, 17] |  |
| round-09/training-m05 | training | 18 | [9, 28] |  |
| round-09/weights-m01 | weights | 9 | [3, 16] |  |
| round-10/weights-m01 | weights | 12 | [6, 19] |  |
| round-10/weights-m06 | weights | 12 | [6, 18] |  |
| round-09/problems-m05 | problems | 12 | [6, 19] |  |
| run-03/f2-m02 | stopping | 12 | [6, 19] |  |
| round-10/stopping-m04 | stopping | 11 | [5, 18] |  |
| run-04/f2-m04 | sampling | 12 | [6, 18] |  |
| run-04/f2-m03 | sampling | 12 | [6, 18] |  |
| round-09/sampling-m01 | sampling | 12 | [6, 18] |  |
| run-08/f2-m01 | grader | 12 | [6, 19] |  |
| round-09/grader-m01 | grader | 12 | [6, 19] |  |

Theory says nothing: run-06/f2-m03, round-09/training-m06, round-09/training-m04, round-09/training-m03, round-10/training-m05, run-05/f2-m03, run-05/f2-m01, run-05/f2-m06, run-05/f2-m04, round-09/weights-m04, round-09/weights-m06, round-10/weights-m03, round-10/weights-m05, run-02/f2-m01, run-02/f2-m04, run-07/f2-m02, round-10/problems-m03, round-10/problems-m04, round-10/problems-m05, round-10/problems-m06, run-03/f2-m05, round-09/stopping-m04, round-10/stopping-m03, round-09/sampling-m03, round-09/sampling-m05, round-09/sampling-m06, round-09/grader-m04, round-09/grader-m03, round-09/grader-m06, round-10/grader-m06.


### r10-m05: Olmo-3.1-7B-RL-Zero-Math step 100 (revision step_0100 0a45720c), rebuilt as base + 1.0 x (step100 - base) with nearest rounding (endpoint exact); plain; hard328, n 164: shard 0/2 of hard328 (problems 0, 2, 4, ..., 326)

GPU minutes 75 (proposers' guess). Separation 0 readouts split with 2 or more families on each side, 0 per minute. Job `run_cell.py`.

Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math step 100 (revision step_0100 0a45720c), rebuilt as base + 1.0 x (step100 - base) with nearest rounding (endpoint exact)", "prompt": "plain", "set": "hard328", "n": "164: shard 0/2 of hard328 (problems 0, 2, 4, ..., 326)", "sampling": "T 1.0, top-p 1.0, min-p 0; seed 3000000 + problem index (the seeds of the cued-base row e72c)", "samples": "1 per problem, no restarts", "grader": "v3", "cap": "16,384 generated tokens"}

Command: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe interp --other rl_math_step100 --alpha 1.0 --rounding nearest --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label rl_step100 --prompt plain --set hard328 --shard 0/2 --temperature 1.0 --top-p 1.0 --seed 3000000 --commit $(git rev-parse HEAD)"`


#### r10-m05-r1: right answers with grader v3 (cap hits counted wrong) among the 164 problems of shard 0/2 (right answers of 164)

- proposed by round-09/training-m03 (c05): 84 [77, 92]; says round-09/sampling-m03 gives 72 (its blind forecast: 82). training-m03 says step 100 has moved only problems the base solves sometimes, so on hard problems step-100 plain equals the cued base: about 82 on this half (164/328), plus at most a few. sampling-m03 says at T 1.0 a share of step-100 plain answers (117 of 500 on MATH-500) opens outside the 'Okay' register, and the gap between openings widens on harder problems (plain base 76 against cue 164 on the 328). Step-100 plain then falls below the cued base, to about 72.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 86 | [75, 97] |  |
| reader-2 | reader-2 | 85 | [75, 95] |  |
| round-09/training-m03 | training | 82 | [72, 92] |  |
| run-05/f2-m06 | weights | 84 | [75, 93] |  |
| run-05/f2-m04 | weights | 85 | [76, 94] |  |
| round-09/weights-m06 | weights | 84 | [75, 93] |  |
| round-09/problems-m05 | problems | 84 | [74, 94] |  |
| round-10/problems-m04 | problems | 85 | [75, 95] |  |
| round-09/stopping-m04 | stopping | 86 | [77, 95] |  |
| round-09/sampling-m03 | sampling | 82 | [71, 93] |  |
| run-04/f2-m04 | sampling | 84 | [74, 95] |  |
| round-09/sampling-m01 | sampling | 84 | [74, 95] |  |
| run-08/f2-m01 | grader | 85 | [74, 96] |  |
| round-09/grader-m04 | grader | 83 | [72, 94] |  |
| round-09/grader-m01 | grader | 85 | [75, 95] |  |

Theory says nothing: run-06/f2-m03, round-09/training-m06, round-09/training-m04, round-09/training-m05, round-10/training-m05, run-05/f2-m03, run-05/f2-m01, round-09/weights-m01, round-09/weights-m04, round-10/weights-m01, round-10/weights-m03, round-10/weights-m05, round-10/weights-m06, run-02/f2-m01, run-02/f2-m04, run-07/f2-m02, round-10/problems-m03, round-10/problems-m05, round-10/problems-m06, run-03/f2-m02, run-03/f2-m05, round-10/stopping-m03, round-10/stopping-m04, run-04/f2-m03, round-09/sampling-m05, round-09/sampling-m06, round-09/grader-m03, round-09/grader-m06, round-10/grader-m06.


### r10-m06: Olmo-3-7B-Think-SFT + 2.0 x (Olmo-3.1-7B-RL-Zero-Math - base), M(2), bf16, seed 0; cue (frozen4.json prefill); fresh2026, n 136: all fresh2026 problems (AIME 2026, HMMT Feb and Nov 2026)

GPU minutes 75 (proposers' guess). Separation 0 readouts split with 2 or more families on each side, 0 per minute. Job `run_fresh.py`.

Cell: {"model": "Olmo-3-7B-Think-SFT + 2.0 x (Olmo-3.1-7B-RL-Zero-Math - base), M(2), bf16, seed 0", "prompt": "cue (frozen4.json prefill)", "set": "fresh2026", "n": "136: all fresh2026 problems (AIME 2026, HMMT Feb and Nov 2026)", "sampling": "T 1.0, top-p 1.0, min-p 0; seed 3000000 + problem index", "samples": "1 per problem, no restarts", "grader": "v3", "cap": "16,384 generated tokens"}

Command: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.delta_sum --host think_sft --donor rl_math --alpha 2.0 --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_fresh --model-path /tmp/theta --model-label sft_plus_2rl --prompt cue --set fresh2026 --temperature 1.0 --top-p 1.0 --seed 3000000 --commit $(git rev-parse HEAD)"`


#### r10-m06-r1: right answers with grader v3 (cap hits counted wrong) of the 136 fresh2026 problems (right answers of 136)

- proposed by round-10/training-m05 (c06): 70 [62, 78]; says round-09/problems-m05 gives 51 (its blind forecast: 68). training-m05 says imitation supplies whole solution routines for contest problems and the RL difference adds only closing. M(2) should keep Think-SFT's routines (60.0 per sample on fresh2026, 46 % cap hits) and close about half of its cut work, as on hard328 (cap hits 94.5 to 44, +22.5 right), for about 70. problems-m05 says RL weights add finishing and fewer slips but no plans, so on contest sets a model carrying the RL difference tracks RL. Its forced closings become guesses like RL's (43 % precision), so about RL's 50.5.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 66 | [56, 77] |  |
| reader-2 | reader-2 | 66 | [56, 77] |  |
| round-10/training-m05 | training | 69 | [59, 79] |  |
| round-09/weights-m04 | weights | 63 | [53, 73] |  |
| round-10/weights-m03 | weights | 67 | [58, 76] |  |
| run-02/f2-m04 | run-02 | 68 | [57, 79] |  |
| round-09/problems-m05 | problems | 68 | [58, 78] |  |
| round-10/problems-m05 | problems | 66 | [56, 76] |  |
| run-03/f2-m02 | stopping | 65 | [55, 76] |  |
| run-03/f2-m05 | stopping | 64 | [54, 75] |  |
| run-04/f2-m03 | sampling | 68 | [58, 78] |  |
| run-08/f2-m01 | grader | 66 | [55, 77] |  |
| round-09/grader-m04 | grader | 63 | [52, 74] |  |
| round-09/grader-m03 | grader | 65 | [54, 76] |  |
| round-09/grader-m01 | grader | 66 | [55, 77] |  |

Theory says nothing: run-06/f2-m03, round-09/training-m06, round-09/training-m04, round-09/training-m05, round-09/training-m03, run-05/f2-m03, run-05/f2-m01, run-05/f2-m06, run-05/f2-m04, round-09/weights-m01, round-09/weights-m06, round-10/weights-m01, round-10/weights-m05, round-10/weights-m06, run-02/f2-m01, run-07/f2-m02, round-10/problems-m03, round-10/problems-m04, round-10/problems-m06, round-09/stopping-m04, round-10/stopping-m03, round-10/stopping-m04, round-09/sampling-m03, run-04/f2-m04, round-09/sampling-m05, round-09/sampling-m06, round-09/sampling-m01, round-09/grader-m06, round-10/grader-m06.


### r10-m07: Olmo-3-1025-7B base - 1.5 x top-8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Math - base) (signed size -1.5), all layers, stochastic bf16 rounding, seed 0; cue; fresh2026 (136 competition problems from 2026), n 136, all

GPU minutes 100 (proposers' guess). Separation 0 readouts split with 2 or more families on each side, 0 per minute. Job `run_fresh.py`.

Cell: {"model": "Olmo-3-1025-7B base - 1.5 x top-8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Math - base) (signed size -1.5), all layers, stochastic bf16 rounding, seed 0", "prompt": "cue", "set": "fresh2026 (136 competition problems from 2026)", "n": "136, all", "sampling": "T 1.0, top-p 1.0, min-p 0, seed 93000000 + problem index", "samples": "1 per problem, no restarts", "grader": "v3", "cap": "16,384 generated tokens"}

Command: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe top8 --other rl_math --k 8 --scale -1.5 --rounding stochastic --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_fresh --model-path /tmp/theta --model-label math_top8xm1.5 --prompt cue --set fresh2026 --temperature 1.0 --top-p 1.0 --seed 93000000 --commit $(git rev-parse HEAD)"`


#### r10-m07-r1: cap hits (finish reason length) among the 136 rows of answers.jsonl (cap hits of 136)

- proposed by run-05/f2-m01 (c08): 75 [63, 87]; says round-10/stopping-m04 gives 59 (its blind forecast: 64). f2-m01's dial is monotone in signed size: -1 raised hard328 cap hits by 25 % (77 to 96), so -1.5 raises the cued base's 54.8 fresh2026 cap hits by about 37 %. stopping-m04 says subtraction turns boxed endings into unboxed ones far more than into cap hits (at -1 unboxed rose 23 to 61 while cap hits rose only 19), so cap hits rise only a little, about 8 %.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 68 | [55, 82] |  |
| reader-2 | reader-2 | 70 | [57, 84] |  |
| run-06/f2-m03 | training | 72 | [58, 86] |  |
| round-09/training-m05 | training | 72 | [58, 86] |  |
| run-05/f2-m03 | weights | 70 | [58, 82] |  |
| run-05/f2-m01 | weights | 72 | [60, 84] |  |
| round-09/weights-m01 | weights | 68 | [56, 80] |  |
| round-10/weights-m01 | weights | 76 | [63, 89] |  |
| run-07/f2-m02 | problems | 72 | [58, 86] |  |
| round-09/problems-m05 | problems | 70 | [57, 84] |  |
| run-03/f2-m02 | stopping | 75 | [62, 88] |  |
| run-03/f2-m05 | stopping | 74 | [60, 88] |  |
| round-10/stopping-m04 | stopping | 64 | [52, 77] |  |
| run-04/f2-m03 | sampling | 68 | [56, 80] |  |
| run-08/f2-m01 | grader | 68 | [54, 82] |  |
| round-09/grader-m04 | grader | 68 | [54, 82] |  |
| round-09/grader-m01 | grader | 68 | [54, 82] |  |

Theory says nothing: round-09/training-m06, round-09/training-m04, round-09/training-m03, round-10/training-m05, run-05/f2-m06, run-05/f2-m04, round-09/weights-m04, round-09/weights-m06, round-10/weights-m03, round-10/weights-m05, round-10/weights-m06, run-02/f2-m01, run-02/f2-m04, round-10/problems-m03, round-10/problems-m04, round-10/problems-m05, round-10/problems-m06, round-09/stopping-m04, round-10/stopping-m03, round-09/sampling-m03, run-04/f2-m04, round-09/sampling-m05, round-09/sampling-m06, round-09/sampling-m01, round-09/grader-m03, round-09/grader-m06, round-10/grader-m06.


### r10-m08: Olmo-3-1025-7B base + 0.5 x top-8 singular directions per matrix of (RL-Math 3.1 - base), written with round-to-nearest bf16 (--rounding nearest); cue; hard328, n 200: the first 200 problems (--n 200)

GPU minutes 105 (proposers' guess). Separation 0 readouts split with 2 or more families on each side, 0 per minute. Job `run_cell.py`.

Cell: {"model": "Olmo-3-1025-7B base + 0.5 x top-8 singular directions per matrix of (RL-Math 3.1 - base), written with round-to-nearest bf16 (--rounding nearest)", "prompt": "cue", "set": "hard328", "n": "200: the first 200 problems (--n 200)", "sampling": "T 1.0, top-p 1.0, min-p 0, seed 3000000 + problem index", "samples": "1 per problem, no restarts", "grader": "v3", "cap": "16,384 generated tokens"}

Command: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe top8 --other rl_math --k 8 --scale 0.5 --rounding nearest --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label math_top8x0.5_nearest --prompt cue --set hard328 --n 200 --temperature 1.0 --top-p 1.0 --seed 3000000 --commit $(git rev-parse HEAD)"`


#### r10-m08-r1: cap hits (finish reason length) among the 200 rows of answers.jsonl (cap hits of 200)

- proposed by run-05/f2-m06 (c09): 53 [44, 62]; says round-09/grader-m03 gives 38 (its blind forecast: nothing). At 0.5x the entries of a rank-8 edit are mostly under half a bf16 ulp. f2-m06 says round-to-nearest drops them except on small weights, so the edit acts like about 0.12x: cap hits stay near the cued base's 58 on these 200 (77 to 70 on all 328, x0.757). grader-m03 reads a partial edit as the edit null plus its nominal share of the gain, which is the stored 0.5x cell (50 of 328, so 38 of 200).

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 47 | [34, 61] |  |
| reader-2 | reader-2 | 46 | [34, 58] |  |
| run-06/f2-m03 | training | 45 | [32, 60] |  |
| round-09/training-m05 | training | 45 | [32, 60] |  |
| run-05/f2-m01 | weights | 40 | [30, 50] |  |
| run-05/f2-m06 | weights | 47 | [37, 57] |  |
| round-09/weights-m01 | weights | 40 | [30, 50] |  |
| round-09/weights-m06 | weights | 50 | [40, 60] |  |
| round-10/weights-m01 | weights | 44 | [34, 54] |  |
| run-07/f2-m02 | problems | 47 | [34, 60] |  |
| round-09/problems-m05 | problems | 46 | [33, 60] |  |
| run-03/f2-m02 | stopping | 48 | [35, 61] |  |
| round-10/stopping-m04 | stopping | 49 | [36, 62] |  |
| run-04/f2-m03 | sampling | 47 | [35, 59] |  |
| run-08/f2-m01 | grader | 48 | [35, 62] |  |
| round-09/grader-m04 | grader | 50 | [37, 63] |  |
| round-09/grader-m01 | grader | 48 | [35, 62] |  |

Theory says nothing: round-09/training-m06, round-09/training-m04, round-09/training-m03, round-10/training-m05, run-05/f2-m03, run-05/f2-m04, round-09/weights-m04, round-10/weights-m03, round-10/weights-m05, round-10/weights-m06, run-02/f2-m01, run-02/f2-m04, round-10/problems-m03, round-10/problems-m04, round-10/problems-m05, round-10/problems-m06, run-03/f2-m05, round-09/stopping-m04, round-10/stopping-m03, round-09/sampling-m03, run-04/f2-m04, round-09/sampling-m05, round-09/sampling-m06, round-09/sampling-m01, round-09/grader-m03, round-09/grader-m06, round-10/grader-m06.


### r10-m09: Olmo-3-1025-7B base + 1.0 x top-8 singular directions per matrix of (RL-Math 3.1 - base), stochastic bf16 rounding, seed 0; plain (no cue); hard328, n 200: the first 200 problems (--n 200)

GPU minutes 101 (proposers' guess). Separation 0 readouts split with 2 or more families on each side, 0 per minute. Job `run_cell.py`.

Cell: {"model": "Olmo-3-1025-7B base + 1.0 x top-8 singular directions per matrix of (RL-Math 3.1 - base), stochastic bf16 rounding, seed 0", "prompt": "plain (no cue)", "set": "hard328", "n": "200: the first 200 problems (--n 200)", "sampling": "T 1.0, top-p 1.0, min-p 0, seed 3000000 + problem index", "samples": "1 per problem, no restarts", "grader": "v3", "cap": "16,384 generated tokens"}

Command: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe top8 --other rl_math --k 8 --scale 1.0 --rounding stochastic --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label math_top8x1_plain --prompt plain --set hard328 --n 200 --temperature 1.0 --top-p 1.0 --seed 3000000 --commit $(git rev-parse HEAD)"`


#### r10-m09-r1: right answers with grader v3 among the 200 rows (right answers of 200)

- proposed by run-05/f2-m04 (c10): 97 [87, 107]; says round-09/training-m04 gives 83 (its blind forecast: nothing). f2-m04 says an edit built from the final weights carries both the opening register (the part the cue gives) and the late finishing, so the prompt hardly matters: plain is close to the cued top-8 1x cell (192 of 328, so 101.5 of these 200), as on MATH-500, where plain is about 0.97 of cued. training-m04 has the plain prompt sample a terse register whose share of the cued score shrinks on harder sets, by the base's factor 0.85 from MATH-500 to hard328, giving about 0.82 x 101.5.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 97 | [84, 110] |  |
| reader-2 | reader-2 | 100 | [88, 112] |  |
| run-06/f2-m03 | training | 100 | [88, 112] |  |
| run-05/f2-m01 | weights | 100 | [87, 113] |  |
| round-09/weights-m06 | weights | 98 | [85, 111] |  |
| round-10/weights-m06 | weights | 98 | [85, 111] |  |
| run-07/f2-m02 | problems | 98 | [86, 110] |  |
| round-09/problems-m05 | problems | 96 | [84, 108] |  |
| round-10/problems-m03 | problems | 96 | [84, 108] |  |
| round-10/problems-m04 | problems | 95 | [83, 107] |  |
| run-03/f2-m02 | stopping | 96 | [84, 108] |  |
| round-10/stopping-m04 | stopping | 97 | [85, 109] |  |
| round-09/sampling-m03 | sampling | 89 | [77, 101] |  |
| run-08/f2-m01 | grader | 96 | [83, 109] |  |
| round-09/grader-m04 | grader | 92 | [79, 105] |  |
| round-09/grader-m03 | grader | 97 | [84, 110] |  |
| round-09/grader-m01 | grader | 96 | [83, 109] |  |

Theory says nothing: round-09/training-m06, round-09/training-m04, round-09/training-m05, round-09/training-m03, round-10/training-m05, run-05/f2-m03, run-05/f2-m06, run-05/f2-m04, round-09/weights-m01, round-09/weights-m04, round-10/weights-m01, round-10/weights-m03, round-10/weights-m05, run-02/f2-m01, run-02/f2-m04, round-10/problems-m05, round-10/problems-m06, run-03/f2-m05, round-09/stopping-m04, round-10/stopping-m03, run-04/f2-m04, run-04/f2-m03, round-09/sampling-m05, round-09/sampling-m06, round-09/sampling-m01, round-09/grader-m06, round-10/grader-m06.


### r10-m10: Olmo-3-1025-7B base + 1.5 x the top-1 singular direction per matrix of (RL-Math 3.1 - base) (--k 1), stochastic bf16 rounding, seed 0; cue; hard328, n 200: the first 200 problems (--n 200)

GPU minutes 93 (proposers' guess). Separation 0 readouts split with 2 or more families on each side, 0 per minute. Job `run_cell.py`.

Cell: {"model": "Olmo-3-1025-7B base + 1.5 x the top-1 singular direction per matrix of (RL-Math 3.1 - base) (--k 1), stochastic bf16 rounding, seed 0", "prompt": "cue", "set": "hard328", "n": "200: the first 200 problems (--n 200)", "sampling": "T 1.0, top-p 1.0, min-p 0, seed 3000000 + problem index", "samples": "1 per problem, no restarts", "grader": "v3", "cap": "16,384 generated tokens"}

Command: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe top8 --other rl_math --k 1 --scale 1.5 --rounding stochastic --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label math_top1x1.5 --prompt cue --set hard328 --n 200 --temperature 1.0 --top-p 1.0 --seed 3000000 --commit $(git rev-parse HEAD)"`


#### r10-m10-r1: cap hits (finish reason length) among the 200 rows of answers.jsonl (cap hits of 200)

- proposed by round-09/weights-m01 (c11): 17 [10, 25]; says round-09/training-m05 gives 39 (its blind forecast: 36). weights-m01 puts the stop readout in the top direction, so finishing follows its size whatever the rank: top-1 at 1.5x finishes like top-8 at 1.5x (18 to 25 of 328, so about 17 of 200; top-1 1x 51 against top-8 1x 46 already agree). training-m05 says one direction cuts cap hits only partly and scaling it changes answer form rather than stopping, so top-1 at 1.5x stays near top-1 at 1x (51 of 328, so 39 of 200).

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 26 | [16, 37] |  |
| reader-2 | reader-2 | 26 | [17, 35] |  |
| round-09/training-m05 | training | 36 | [25, 47] |  |
| round-09/weights-m01 | weights | 22 | [13, 31] |  |
| round-10/weights-m01 | weights | 30 | [20, 40] |  |
| round-10/weights-m06 | weights | 27 | [18, 36] |  |
| round-09/problems-m05 | problems | 27 | [18, 37] |  |
| run-03/f2-m02 | stopping | 27 | [18, 37] |  |
| round-10/stopping-m04 | stopping | 26 | [17, 36] |  |
| run-04/f2-m03 | sampling | 27 | [18, 37] |  |
| run-08/f2-m01 | grader | 26 | [16, 37] |  |
| round-09/grader-m04 | grader | 27 | [17, 38] |  |
| round-09/grader-m01 | grader | 26 | [16, 37] |  |

Theory says nothing: run-06/f2-m03, round-09/training-m06, round-09/training-m04, round-09/training-m03, round-10/training-m05, run-05/f2-m03, run-05/f2-m01, run-05/f2-m06, run-05/f2-m04, round-09/weights-m04, round-09/weights-m06, round-10/weights-m03, round-10/weights-m05, run-02/f2-m01, run-02/f2-m04, run-07/f2-m02, round-10/problems-m03, round-10/problems-m04, round-10/problems-m05, round-10/problems-m06, run-03/f2-m05, round-09/stopping-m04, round-10/stopping-m03, round-09/sampling-m03, run-04/f2-m04, round-09/sampling-m05, round-09/sampling-m06, round-09/sampling-m01, round-09/grader-m03, round-09/grader-m06, round-10/grader-m06.


## List B: base-only cells, top 10 by the highest forecast of right answers minus the best known base count

### r10-m35: Olmo-3-1025-7B base (untrained); cue; fresh2026, n all 136 problems (base only)

GPU minutes 115 (proposers' guess). Separation 0 readouts split with 2 or more families on each side, 0 per minute. Job `run_fresh.py`.

Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "cue", "set": "fresh2026", "n": "all 136 problems", "sampling": "T 1.0, top-p 1.0, min-p 0; problem i seed 94000000 + i", "samples": "1 per problem, no restarts", "grader": "v3", "cap": "32,768 (the readout also uses the same answers cut at 16,384)"}

Command: `uv run tools/gpu.py submit l40s --hours 2.5 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_fresh --model base --prompt cue --set fresh2026 --temperature 1.0 --top-p 1.0 --max-tokens 32768 --seed 94000000 --commit $(git rev-parse HEAD)"`


#### r10-m35-r1: right answers (v3) among answers with more than 16,384 generated tokens, i.e. the cap-32,768 count minus the same answers scored at a 16,384 cap (right answers (of the ~55 answers past 16,384 tokens))

Best known base count given to the forecasters: 2 (result-0c1eef; No base-only cell has a count on these items (fresh2026 answers past 16,384 tokens at cap 32,768). Scaled from the only base cap raise, hard328 base cue: 4 right of the 64 answers past 16,384 (6.25 %), times the ~55 fresh2026 cap hits, times the 36/65 precision ratio, about 2 (3.4 unscaled).). Highest forecast: round-09/stopping-m04 3 (+1).

- proposed by round-09/grader-m04 (c38): 2 [0, 5]; says round-09/sampling-m05 gives 9 (its blind forecast: 2). grader-m04: past 16k the base's answers are unfinished or guessed, and fresh2026 is harder than hard328, so the yield per abstention is below hard328's 4 of 64 (result-0c1eef); scaled by the base's finished precision (36 % on fresh against about 65 % on hard328) about 3.5 % of the ~55 cap hits (40.3 % of 136), so 2. sampling-m05 says the cut samples come out right at the rate of the base's long finished answers at that difficulty, 16.7 % on hard328 (41 of 246 over 12k tokens), so 55 x 0.167 = 9.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 2.5 | [0, 6] |  |
| reader-2 | reader-2 | 2.5 | [0, 6] |  |
| run-02/f2-m01 | run-02 | 2.5 | [0, 6] |  |
| run-02/f2-m04 | run-02 | 2.5 | [0, 6] |  |
| round-09/problems-m05 | problems | 1 | [0, 4] |  |
| round-10/problems-m05 | problems | 1 | [0, 4] |  |
| run-03/f2-m05 | stopping | 2 | [0, 6] |  |
| round-09/stopping-m04 | stopping | 3 | [0, 7] |  |
| run-04/f2-m03 | sampling | 3 | [0, 7] |  |
| round-09/sampling-m05 | sampling | 2 | [0, 5] |  |
| round-09/grader-m04 | grader | 2 | [0, 5] |  |
| round-09/grader-m06 | grader | 3 | [0, 7] |  |
| round-10/grader-m06 | grader | 2 | [0, 5] |  |

Theory says nothing: run-06/f2-m03, round-09/training-m06, round-09/training-m04, round-09/training-m05, round-09/training-m03, round-10/training-m05, run-05/f2-m03, run-05/f2-m01, run-05/f2-m06, run-05/f2-m04, round-09/weights-m01, round-09/weights-m04, round-09/weights-m06, round-10/weights-m01, round-10/weights-m03, round-10/weights-m05, round-10/weights-m06, run-07/f2-m02, round-10/problems-m03, round-10/problems-m04, round-10/problems-m06, run-03/f2-m02, round-10/stopping-m03, round-10/stopping-m04, round-09/sampling-m03, run-04/f2-m04, round-09/sampling-m06, round-09/sampling-m01, run-08/f2-m01, round-09/grader-m03, round-09/grader-m01.


### r10-m29: Olmo-3-1025-7B base (untrained); cue; MATH-500, n 500 (all); readout on the 33 problems with 0 of 4 right in the stored Day-1 #3 base cue rows (results/day1_3/math500_base_cue-01/rows.jsonl, attempt 0, samples 0-3) (base only)

GPU minutes 100 (proposers' guess). Separation 0 readouts split with 2 or more families on each side, 0 per minute. Job `run_cell.py`.

Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "cue", "set": "MATH-500", "n": "500 (all); readout on the 33 problems with 0 of 4 right in the stored Day-1 #3 base cue rows (results/day1_3/math500_base_cue-01/rows.jsonl, attempt 0, samples 0-3)", "sampling": "T 1.0, top-p 1.0, min-p 0; new seed 71000000 + problem index (no stored row uses it)", "samples": "1 per problem, no restarts", "grader": "v3, cap hits wrong", "cap": "16,384 generated tokens"}

Command: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set math500 --temperature 1.0 --top-p 1.0 --seed 71000000 --commit $(git rev-parse HEAD)"`


#### r10-m29-r1: right answers (grader v3, cap hits wrong) among the 33 base-0-of-4 problems (right answers of 33)

Best known base count given to the forecasters: 9 (result-07f566; Estimate, no committed per-cell count on these 33 problems: the four Day-1 #3 samples have 0 by construction; the per-sample rate of other base samples (0.237 on 17 of them, about half on the other 16) gives about 5.8 per single cell, and the maximum over the about ten stored single-sample base-only MATH-500 cells (T1, min-p, steering, self-opened, shots) is about 9.). Highest forecast: reader-1 6 (-3).

- proposed by run-04/f2-m04 (c32): 6 [2, 10]; says round-09/sampling-m06 gives 1 (its blind forecast: 3.5). f2-m04 treats 0 of 4 as four Bernoulli draws at a small but real p_i: fresh base samples solve the 17 RL-solved 0-of-4 problems at 0.237 per sample (result-07f566) and the other 16 at about half that, so 17 x 0.237 + 16 x 0.11 = 5.8. m06 calls these 33 (against 0.5 expected) a block the base almost never samples right, so about 0.03 per sample, 1 of 33.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 6 | [2, 10] |  |
| reader-2 | reader-2 | 6 | [2, 10] |  |
| round-09/training-m04 | training | 5 | [1, 10] |  |
| round-10/problems-m05 | problems | 5 | [1, 9] |  |
| round-09/stopping-m04 | stopping | 6 | [2, 10] |  |
| run-04/f2-m04 | sampling | 5 | [2, 9] |  |
| round-09/sampling-m06 | sampling | 3.5 | [1, 7] |  |
| round-09/sampling-m01 | sampling | 5 | [2, 9] |  |
| run-08/f2-m01 | grader | 6 | [2, 10] |  |
| round-09/grader-m04 | grader | 6 | [2, 10] |  |
| round-09/grader-m01 | grader | 6 | [2, 10] |  |
| round-10/grader-m06 | grader | 5 | [1, 9] |  |

Theory says nothing: run-06/f2-m03, round-09/training-m06, round-09/training-m05, round-09/training-m03, round-10/training-m05, run-05/f2-m03, run-05/f2-m01, run-05/f2-m06, run-05/f2-m04, round-09/weights-m01, round-09/weights-m04, round-09/weights-m06, round-10/weights-m01, round-10/weights-m03, round-10/weights-m05, round-10/weights-m06, run-02/f2-m01, run-02/f2-m04, run-07/f2-m02, round-09/problems-m05, round-10/problems-m03, round-10/problems-m04, round-10/problems-m06, run-03/f2-m02, run-03/f2-m05, round-10/stopping-m03, round-10/stopping-m04, round-09/sampling-m03, run-04/f2-m03, round-09/sampling-m05, round-09/grader-m03, round-09/grader-m06.


### r10-m38: Olmo-3-1025-7B base (untrained); cue + the 3 Math-RL-written solved examples of draw 1 (result-6d422d / result-5227b9: MATH-500 problems 0, 1, 2) in context, via run_cell --shots; math500, n first 280 problems the job keeps after leaving out the 3 example problems (MATH-500 indices 3-282) (base only)

GPU minutes 115 (proposers' guess). Separation 0 readouts split with 2 or more families on each side, 0 per minute. Job `run_cell.py`.

Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "cue + the 3 Math-RL-written solved examples of draw 1 (result-6d422d / result-5227b9: MATH-500 problems 0, 1, 2) in context, via run_cell --shots", "set": "math500", "n": "first 280 problems the job keeps after leaving out the 3 example problems (MATH-500 indices 3-282)", "sampling": "T 1.0, top-p 1.0, min-p 0; new seed rule: problem i seed 47000000 + i (draw 1 ran on other seeds)", "samples": "1 per problem, no restarts", "grader": "v3", "cap": "16,384"}

Command: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set math500 --shots <draw-1 Math-RL examples json of result-5227b9, branch shots> --n 280 --temperature 1.0 --top-p 1.0 --seed 47000000 --commit $(git rev-parse HEAD)"`


#### r10-m38-r1: right answers with grader v3 on the 280 problems (cap hits count wrong) (right answers of 280)

Best known base count given to the forecasters: 245 (result-6d422d; Best one-sample base-only count on MATH-500 is the same Math-RL-written examples draw, 435 of 497 (432 of 494 in result-5227b9). No count exists on exactly these 280 problems, so it is scaled: 435/497 x 280 = 245.). Highest forecast: reader-1 238 (-7).

- proposed by round-09/grader-m01 (c41): 231 [221, 240]; says run-08/f2-m01 gives 243 (its blind forecast: 236). grader-m01: draw 1 (432 of 494) is a first-run cell picked as notable, so new seeds regress to the pooled level of the near-identical examples-in-context cells (none 404, base-written 411 and 403, Code-written 409, RL-written draw 2 401): about 407/494 = 0.824, x 280 = 231. f2-m01 treats the stored 432 as an unselected draw of that prompt's fixed per-problem probabilities, shrunk only slightly toward its prior (to ~428/494 = 0.866): 0.866 x 280 = 243.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 238 | [225, 250] |  |
| reader-2 | reader-2 | 237 | [226, 247] |  |
| round-09/training-m04 | training | 233 | [221, 245] |  |
| run-04/f2-m04 | sampling | 238 | [226, 250] |  |
| round-09/sampling-m01 | sampling | 238 | [226, 250] |  |
| run-08/f2-m01 | grader | 236 | [224, 248] |  |
| round-09/grader-m01 | grader | 234 | [222, 246] |  |

Theory says nothing: run-06/f2-m03, round-09/training-m06, round-09/training-m05, round-09/training-m03, round-10/training-m05, run-05/f2-m03, run-05/f2-m01, run-05/f2-m06, run-05/f2-m04, round-09/weights-m01, round-09/weights-m04, round-09/weights-m06, round-10/weights-m01, round-10/weights-m03, round-10/weights-m05, round-10/weights-m06, run-02/f2-m01, run-02/f2-m04, run-07/f2-m02, round-09/problems-m05, round-10/problems-m03, round-10/problems-m04, round-10/problems-m05, round-10/problems-m06, run-03/f2-m02, run-03/f2-m05, round-09/stopping-m04, round-10/stopping-m03, round-10/stopping-m04, round-09/sampling-m03, run-04/f2-m03, round-09/sampling-m05, round-09/sampling-m06, round-09/grader-m04, round-09/grader-m03, round-09/grader-m06, round-10/grader-m06.


### r10-m17: Olmo-3-1025-7B base (untrained, no edit); cue (frozen4.json prefill ' line!\n\nOkay'); hard328, n 110 problems: shard 0/3 of hard328 (indices 0, 3, 6, ..., 327), spread evenly over the easier and harder halves (base only)

GPU minutes 70 (proposers' guess). Separation 0 readouts split with 2 or more families on each side, 0 per minute. Job `run_cell.py`.

Cell: {"model": "Olmo-3-1025-7B base (untrained, no edit)", "prompt": "cue (frozen4.json prefill ' line!\\n\\nOkay')", "set": "hard328", "n": "110 problems: shard 0/3 of hard328 (indices 0, 3, 6, ..., 327), spread evenly over the easier and harder halves", "sampling": "T 1.0, top-p 1.0, min-p 0; seed 95000000, sample s of problem i uses seed + 10000*s + i (run_cell rule)", "samples": "12 per problem, no restarts", "grader": "v3; plurality vote over the 12 extracted answers grouped with rln4_lib.agree, capped samples abstain, ties to the lowest sample index", "cap": "2,048 generated tokens"}

Command: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set hard328 --shard 0/3 --temperature 1.0 --top-p 1.0 --max-tokens 2048 --samples 12 --restarts 0 --seed 95000000 --commit $(git rev-parse HEAD)"`


#### r10-m17-r1: Right answers (grader v3) of the plurality vote over 12 samples on the 110 problems, computed from answers.jsonl; a sample that hits the 2,048 cap gives no answer (right answers of 110)

Best known base count given to the forecasters: 47 (result-6e7b64; Best base-only count with 12 samples on hard328: the Karpathy-loop method (plain prompt, T 0.6, 12 samples capped at 4,096, vote) got 139 of 328. Scaled to the 110 shard problems: 139 x 110/328 = 46.6. No base-only cell has a count on exactly these 110 problems.). Highest forecast: round-09/sampling-m05 37 (-10).

- proposed by run-02/f2-m01 (c18): 28 [20, 36]; says round-09/training-m04 gives 50 (its blind forecast: 34). f2-m01 says hard328 solutions take 6,000-14,000 tokens, so 2,048-token samples reach only the short-solution problems: roughly RL-length quartile Q1 plus a few from Q2, about 85 of 328 (the base is right within 4k on 81 of 328 per sample, result-1b6bf2; the 12-sample vote at 4k reached 139, result-6e7b64). So the vote stays near 28 of 110 however many samples are added. training-m04 fixes each problem's distribution over final values in pretraining, regardless of answer length, so the cap only censors samples: the finished short samples converge on the same mode as the full-length vote (192 of 328 over 4 samples, about 66 of 110), losing only the problems where no sample finishes, which gives about 50.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 31 | [20, 43] |  |
| reader-2 | reader-2 | 36 | [27, 45] |  |
| round-09/training-m04 | training | 34 | [24, 44] |  |
| run-02/f2-m01 | run-02 | 27 | [16, 38] |  |
| run-02/f2-m04 | run-02 | 31 | [19, 43] |  |
| round-10/problems-m05 | problems | 36 | [26, 47] |  |
| round-09/stopping-m04 | stopping | 36 | [26, 46] |  |
| round-09/sampling-m05 | sampling | 37 | [28, 47] |  |
| round-09/sampling-m06 | sampling | 37 | [28, 47] |  |
| round-09/grader-m04 | grader | 32 | [21, 44] |  |
| round-09/grader-m06 | grader | 33 | [22, 45] |  |
| round-10/grader-m06 | grader | 33 | [22, 45] |  |

Theory says nothing: run-06/f2-m03, round-09/training-m06, round-09/training-m05, round-09/training-m03, round-10/training-m05, run-05/f2-m03, run-05/f2-m01, run-05/f2-m06, run-05/f2-m04, round-09/weights-m01, round-09/weights-m04, round-09/weights-m06, round-10/weights-m01, round-10/weights-m03, round-10/weights-m05, round-10/weights-m06, run-07/f2-m02, round-09/problems-m05, round-10/problems-m03, round-10/problems-m04, round-10/problems-m06, run-03/f2-m02, run-03/f2-m05, round-10/stopping-m03, round-10/stopping-m04, round-09/sampling-m03, run-04/f2-m04, run-04/f2-m03, round-09/sampling-m01, run-08/f2-m01, round-09/grader-m03, round-09/grader-m01.


### r10-m03: Olmo-3-1025-7B base (untrained); plain (no cue prefilled); math500, n 100: the first 100 MATH-500 problems (base only)

GPU minutes 80 (proposers' guess). Separation 0 readouts split with 2 or more families on each side, 0 per minute. Job `run_cell.py`.

Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "plain (no cue prefilled)", "set": "math500", "n": "100: the first 100 MATH-500 problems", "sampling": "T 1.0, top-p 1.0, min-p 0; sample s of problem i has seed 41000000 + 10000 s + i", "samples": "8 per problem, no restarts", "grader": "v3, plurality vote over the 8 samples (answers grouped with rln4_lib.agree, cap hits and no-answer samples abstain, ties to the lowest sample index)", "cap": "16,384 generated tokens"}

Command: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt plain --set math500 --n 100 --temperature 1.0 --top-p 1.0 --seed 41000000 --samples 8 --commit $(git rev-parse HEAD)"`


#### r10-m03-r1: right answers under the plurality vote over 8 plain samples (grader v3) of the first 100 MATH-500 problems (right answers of 100)

Best known base count given to the forecasters: 90 (result-5d032f; No base-only cell on the board has 8 samples on these 100 problems. Used the best 4-sample base count, vote over 4 after restart, 450/500 on all of MATH-500, scaled to 100. For reference, the prefilled-cue single sample on these first 100 is 82 (result-d2933e).). Highest forecast: round-09/training-m04 72 (-18).

- proposed by round-09/training-m04 (c03): 85 [78, 91]; says round-09/sampling-m03 gives 52 (its blind forecast: 65). training-m04 says the cue picks the register but does not move each problem's modal final value, and a vote converges to that mode. So eight plain samples should vote to about the cued vote's level on these easy problems (cued vote over 4 is 446/500, about 89 per 100), although one plain sample scores only 34 here. sampling-m03 says at T 1.0 most plain base samples (about 400 of 500) open outside the deliberative register, and those openings have much lower accuracy. Votes over such draws stay far below the cued vote, at about 52.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 60 | [46, 74] |  |
| reader-2 | reader-2 | 56 | [42, 69] |  |
| round-09/training-m04 | training | 72 | [55, 88] |  |
| run-02/f2-m01 | run-02 | 63 | [50, 75] |  |
| run-02/f2-m04 | run-02 | 58 | [46, 70] |  |
| round-10/problems-m03 | problems | 48 | [36, 60] |  |
| round-10/problems-m05 | problems | 56 | [43, 69] |  |
| round-09/stopping-m04 | stopping | 58 | [46, 70] |  |
| round-09/sampling-m03 | sampling | 65 | [52, 78] |  |
| round-09/sampling-m06 | sampling | 60 | [47, 73] |  |
| round-10/grader-m06 | grader | 55 | [42, 68] |  |

Theory says nothing: run-06/f2-m03, round-09/training-m06, round-09/training-m05, round-09/training-m03, round-10/training-m05, run-05/f2-m03, run-05/f2-m01, run-05/f2-m06, run-05/f2-m04, round-09/weights-m01, round-09/weights-m04, round-09/weights-m06, round-10/weights-m01, round-10/weights-m03, round-10/weights-m05, round-10/weights-m06, run-07/f2-m02, round-09/problems-m05, round-10/problems-m04, round-10/problems-m06, run-03/f2-m02, run-03/f2-m05, round-10/stopping-m03, round-10/stopping-m04, run-04/f2-m04, run-04/f2-m03, round-09/sampling-m05, round-09/sampling-m01, run-08/f2-m01, round-09/grader-m04, round-09/grader-m03, round-09/grader-m06, round-09/grader-m01.


## List C: no-reward routes by the median forecast minus the best known count at equal tokens per problem

### r10-n01 (training, round-10/training-m05): Think-SFT with the cue at T 1.0 / top-p 1.0 and the cap raised to 32,768, three samples per problem; the answer is a sequential vote (samples 0 and 1, stop if they agree, else add sample 2, plurality, ties to the shortest finished sample), and tokens count only the samples the vote reads.

Model think_sft, 26500 tokens per problem, 235 GPU minutes (proposer's guess). Score 2.7.

Why, by the gap's parts: hard328 one-sample gap, cued base 161 to RL 207 (about 60 problems gross, shares from result-f39ba8's hard328 row): capability about .27 (~16 problems), which Think-SFT's imitated competition routines supply (one Think-SFT sample at cap 16,384 already 212 > RL 207); budget about .27 (~16), which the 32,768 cap gives back without a reward (Think-SFT 207 -> 230 on the same answers, result-c8b994); reliability about .43 (~26), which the vote over 2-3 samples recovers in part (Think-SFT vote +29 at 16,384). Answer statement (~2) is left alone. MATH-500: the gap is mostly reliability (.63), covered by the vote. Think-SFT's teacher traces put whole solution routines for competition problems into the model, so it beats RL on hard328 without any reward; what it lacks is closing, which RL's difference supplies but which a longer budget plus agreement between samples also supplies at no reward.

Command: `uv run tools/gpu.py submit l40s --hours 4 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model think_sft --opening-text $' line!\n\nOkay' --set hard328 --shard 0/5 --temperature 1.0 --top-p 1.0 --max-tokens 32768 --samples 3 --seed 71000000 --commit $(git rev-parse HEAD) && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model think_sft --opening-text $' line!\n\nOkay' --set math500 --shard 0/10 --temperature 1.0 --top-p 1.0 --max-tokens 32768 --samples 3 --seed 72000000 --commit $(git rev-parse HEAD)"`

RL arm: `uv run tools/gpu.py submit l40s --hours 4 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model rl --opening-text $' line!\n\nOkay' --set hard328 --shard 0/5 --temperature 1.0 --top-p 1.0 --max-tokens 32768 --samples 3 --seed 71000000 --commit $(git rev-parse HEAD) && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model rl --opening-text $' line!\n\nOkay' --set math500 --shard 0/10 --temperature 1.0 --top-p 1.0 --max-tokens 32768 --samples 3 --seed 72000000 --commit $(git rev-parse HEAD)"`


#### r10-n01-r1: route on hard328, hard328 --shard 0/5 (problems 0, 5, 10, ...; 66), Think-SFT cue cap 32,768, sequential vote over up to 3 samples, grader v3 (of 66)

Proposer 49 [44, 54]. Median forecast 49; best known 46.3 (result-c8b994: 230 of 328 at 11795 tokens per problem (Think-SFT cue, cap 32,768, T 1.0 / top-p 1.0), scaled to 66 problems); gain 2.7.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 49.5 | [43, 56] |
| reader-2 | reader-2 | 49 | [44, 54] |
| round-10/training-m05 | training | 49 | [43, 55] |
| run-02/f2-m04 | run-02 | 47.5 | [41, 54] |
| round-09/problems-m05 | problems | 50 | [44, 56] |
| round-10/problems-m05 | problems | 49 | [43, 55] |
| run-03/f2-m05 | stopping | 49 | [43, 55] |
| round-09/stopping-m04 | stopping | 50 | [44, 56] |
| round-10/stopping-m03 | stopping | 51 | [45, 57] |
| run-04/f2-m04 | sampling | 49 | [43, 55] |
| round-09/sampling-m05 | sampling | 49.5 | [44, 55] |
| round-09/sampling-m06 | sampling | 48.5 | [43, 54] |
| round-09/sampling-m01 | sampling | 49 | [43, 55] |
| round-09/grader-m04 | grader | 49 | [43, 55] |
| round-09/grader-m06 | grader | 50 | [44, 56] |
| round-10/grader-m06 | grader | 49 | [43, 55] |

#### r10-n01-r2: route on MATH-500, MATH-500 --shard 0/10 (problems 0, 10, 20, ...; 50), Think-SFT cue cap 32,768, sequential vote over up to 3 samples, grader v3 (of 50)

Proposer 48 [46, 50]. Median forecast 48; best known 48.1 (result-818c20: 481 of 500 at 19503 tokens per problem (Think-SFT, cue, T 1.0 / top-p 1.0, vote over 4, no restart), scaled to 50 problems); gain -0.1.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 48 | [45, 50] |
| reader-2 | reader-2 | 48 | [46, 50] |
| round-10/training-m05 | training | 48 | [45, 50] |
| run-02/f2-m04 | run-02 | 48 | [45, 50] |
| round-10/problems-m05 | problems | 48 | [45, 50] |
| run-03/f2-m05 | stopping | 48 | [45, 50] |
| round-09/stopping-m04 | stopping | 48 | [45, 50] |
| round-10/stopping-m03 | stopping | 48 | [45, 50] |
| run-04/f2-m04 | sampling | 48 | [45.5, 50] |
| round-09/sampling-m05 | sampling | 48 | [45.5, 50] |
| round-09/sampling-m06 | sampling | 48 | [45.5, 50] |
| round-09/sampling-m01 | sampling | 48 | [45.5, 50] |
| round-09/grader-m06 | grader | 48 | [45.5, 50] |
| round-10/grader-m06 | grader | 48 | [45.5, 50] |

#### r10-n01-r3: rl on hard328, hard328 --shard 0/5 (66), RL-Zero-Math with the same opening, cap and sequential vote, grader v3 (of 66)

Proposer 45 [40, 50]. Median forecast 43.75.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 44 | [38, 50] |
| reader-2 | reader-2 | 44.5 | [39, 50] |
| round-10/training-m05 | training | 44 | [38, 50] |
| run-02/f2-m04 | run-02 | 43 | [36, 50] |
| round-09/problems-m05 | problems | 43 | [37, 49] |
| round-10/problems-m05 | problems | 44 | [38, 50] |
| round-09/stopping-m04 | stopping | 44 | [38, 50] |
| run-04/f2-m04 | sampling | 43.5 | [37.5, 49.5] |
| round-09/sampling-m05 | sampling | 43 | [37, 49] |
| round-09/sampling-m06 | sampling | 43 | [37, 49] |
| round-09/sampling-m01 | sampling | 43.5 | [37.5, 49.5] |
| round-09/grader-m04 | grader | 43 | [37, 49] |
| round-09/grader-m06 | grader | 44 | [38, 50] |
| round-10/grader-m06 | grader | 44 | [38, 50] |

#### r10-n01-r4: rl on MATH-500, MATH-500 --shard 0/10 (50), RL-Zero-Math with the same opening, cap and sequential vote, grader v3 (of 50)

Proposer 47 [45, 49]. Median forecast 47.15.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 47 | [44, 50] |
| reader-2 | reader-2 | 47.5 | [45, 50] |
| round-10/training-m05 | training | 47 | [44, 50] |
| run-02/f2-m04 | run-02 | 47.4 | [44, 50] |
| round-10/problems-m05 | problems | 47 | [44, 50] |
| round-09/stopping-m04 | stopping | 47 | [44, 50] |
| run-04/f2-m04 | sampling | 47.3 | [44.5, 50] |
| round-09/sampling-m05 | sampling | 47.3 | [44.5, 50] |
| round-09/sampling-m06 | sampling | 47.3 | [44.5, 50] |
| round-09/sampling-m01 | sampling | 47.3 | [44.5, 50] |
| round-09/grader-m06 | grader | 47 | [44, 50] |
| round-10/grader-m06 | grader | 47 | [44, 50] |

### r10-n07 (grader, round-09/grader-m06): Think-SFT with the cue, cap raised from 16,384 to 32,768, two samples per problem, kept by a fixed selection rule: if both finish and agree take that answer, if one hits the cap take the finished one, if both finish and differ take the shorter (rule fixed before any scoring).

Model think_sft, 23600 tokens per problem, 220 GPU minutes (proposer's guess). Score 1.5.

Why, by the gap's parts: Budget (cap hit): about a quarter of the gap (result-f39ba8: .25 of 65 on MATH-500 T 1.0, about 16 answers; .27 on hard328). Think-SFT turns about one in four of its cap hits into right answers at 32k (207 -> 230 on hard328), and the finished-over-cap-hit rule recovers more when one of two samples runs out. Reliability (.63 of the gap, about 41 answers on MATH-500): the second sample with the shorter-finished tie rule wins back part of the problems the model solves in some samples (wrong samples run about 2,300 tokens longer). Capability (about .09-.27) is not touched. A capped count scores unfinished work as wrong, and Think-SFT has the largest share of unfinished-work cap hits (about one in four, against one in ten for RL), so a higher cap plus a rule that keeps the finished sample should help Think-SFT most. Two samples rather than four keeps the cost under the 241-at-30,904 vote, and stays below the pass@4 ceiling where extra samples stop adding (round-10/grader-m06).

Command: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model think_sft --opening-text $' line!\n\nOkay' --set hard328 --shard 0/4 --max-tokens 32768 --samples 2 --temperature 1.0 --top-p 1.0 --seed 3000000 --commit $(git rev-parse HEAD)" && uv run tools/gpu.py submit l40s --hours 1 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model think_sft --opening-text $' line!\n\nOkay' --set math500 --shard 0/10 --max-tokens 32768 --samples 2 --temperature 1.0 --top-p 1.0 --seed 41000000 --commit $(git rev-parse HEAD)"`

RL arm: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model rl --opening-text $' line!\n\nOkay' --set hard328 --shard 0/4 --max-tokens 32768 --samples 2 --temperature 1.0 --top-p 1.0 --seed 3000000 --commit $(git rev-parse HEAD)" && uv run tools/gpu.py submit l40s --hours 1 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model rl --opening-text $' line!\n\nOkay' --set math500 --shard 0/10 --max-tokens 32768 --samples 2 --temperature 1.0 --top-p 1.0 --seed 41000000 --commit $(git rev-parse HEAD)"`


#### r10-n07-r1: route on hard328, --shard 0/4 of hard328 (problems 0, 4, 8, ...; 82), right with v3 after the two-sample selection rule; full-set equivalent about 236 of 328 against 230 at 11,795 tokens (best Think-SFT row at <= 23,600 tokens) (of 82)

Proposer 59 [52, 65]. Median forecast 59; best known 57.5 (result-c8b994: 230 of 328 at 11795 tokens per problem (Think-SFT cue, cap 32,768, T 1.0 / top-p 1.0), scaled to 82 problems); gain 1.5.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 59.5 | [52, 66] |
| reader-2 | reader-2 | 60 | [54, 66] |
| round-10/training-m05 | training | 59 | [53, 65] |
| run-02/f2-m04 | run-02 | 59 | [52, 65] |
| round-09/problems-m05 | problems | 59 | [53, 65] |
| round-10/problems-m05 | problems | 59 | [53, 65] |
| run-03/f2-m05 | stopping | 59 | [52, 65] |
| round-09/stopping-m04 | stopping | 60 | [53, 66] |
| round-10/stopping-m03 | stopping | 61 | [54, 67] |
| run-04/f2-m04 | sampling | 59.5 | [53, 66] |
| round-09/sampling-m05 | sampling | 59.5 | [53, 66] |
| round-09/sampling-m06 | sampling | 59 | [52.5, 65.5] |
| round-09/sampling-m01 | sampling | 59.5 | [53, 66] |
| round-09/grader-m04 | grader | 59 | [53, 65] |
| round-09/grader-m06 | grader | 59 | [53, 65] |
| round-10/grader-m06 | grader | 59 | [53, 65] |

#### r10-n07-r2: route on MATH-500, --shard 0/10 of MATH-500 (problems 0, 10, 20, ...; 50), right with v3 after the two-sample selection rule (of 50)

Proposer 47 [44, 49]. Median forecast 47.5; best known 48.1 (result-818c20: 481 of 500 at 19503 tokens per problem (Think-SFT, cue, T 1.0 / top-p 1.0, vote over 4, no restart), scaled to 50 problems); gain -0.6.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 47.5 | [45, 50] |
| reader-2 | reader-2 | 47.5 | [45, 50] |
| round-10/training-m05 | training | 48 | [45, 50] |
| run-02/f2-m04 | run-02 | 47.5 | [44, 50] |
| round-10/problems-m05 | problems | 47 | [44, 50] |
| run-03/f2-m05 | stopping | 47 | [44, 50] |
| round-09/stopping-m04 | stopping | 47 | [44, 50] |
| round-10/stopping-m03 | stopping | 47 | [44, 50] |
| run-04/f2-m04 | sampling | 47.5 | [45, 50] |
| round-09/sampling-m05 | sampling | 47.5 | [45, 50] |
| round-09/sampling-m06 | sampling | 47.5 | [45, 50] |
| round-09/sampling-m01 | sampling | 47.5 | [45, 50] |
| round-09/grader-m06 | grader | 48 | [45.5, 50] |
| round-10/grader-m06 | grader | 48 | [45.5, 50] |

#### r10-n07-r3: rl on hard328, RL-Zero-Math, same procedure (cue opening, cap 32,768, two samples, same selection rule), --shard 0/4 of hard328, 82 problems, v3 (of 82)

Proposer 54 [47, 60]. Median forecast 51.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 52.5 | [45, 59] |
| reader-2 | reader-2 | 52 | [46, 58] |
| round-10/training-m05 | training | 51 | [45, 57] |
| run-02/f2-m04 | run-02 | 51 | [44, 58] |
| round-09/problems-m05 | problems | 51 | [45, 57] |
| round-10/problems-m05 | problems | 51 | [45, 57] |
| round-09/stopping-m04 | stopping | 51.5 | [45, 58] |
| run-04/f2-m04 | sampling | 51 | [45, 57] |
| round-09/sampling-m05 | sampling | 50.5 | [44.5, 56.5] |
| round-09/sampling-m06 | sampling | 50.5 | [44.5, 56.5] |
| round-09/sampling-m01 | sampling | 51 | [45, 57] |
| round-09/grader-m04 | grader | 51 | [45, 57] |
| round-09/grader-m06 | grader | 51 | [45, 57] |
| round-10/grader-m06 | grader | 51 | [45, 57] |

#### r10-n07-r4: rl on MATH-500, RL-Zero-Math, same procedure, --shard 0/10 of MATH-500, 50 problems, v3 (of 50)

Proposer 47 [44, 49]. Median forecast 46.8.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 46.5 | [43, 49] |
| reader-2 | reader-2 | 46.5 | [44, 49] |
| round-10/training-m05 | training | 47 | [44, 50] |
| run-02/f2-m04 | run-02 | 46.5 | [43, 49] |
| round-10/problems-m05 | problems | 46 | [43, 49] |
| round-09/stopping-m04 | stopping | 46.5 | [43, 49] |
| run-04/f2-m04 | sampling | 46.8 | [44, 49.5] |
| round-09/sampling-m05 | sampling | 46.8 | [44, 49.5] |
| round-09/sampling-m06 | sampling | 46.8 | [44, 49.5] |
| round-09/sampling-m01 | sampling | 46.8 | [44, 49.5] |
| round-09/grader-m06 | grader | 47 | [44, 50] |
| round-10/grader-m06 | grader | 47 | [44, 50] |

### r10-n06 (sampling, round-09/sampling-m05): Think-SFT with the cue at T 1.0 / top-p 1.0 and the cap raised to 32,768, two samples per problem, keeping the shared answer if they agree, otherwise the sample that finished (not a cap hit), otherwise sample 0; rule computed afterwards from answers.jsonl.

Model think_sft, 23600 tokens per problem, 200 GPU minutes (proposer's guess). Score 1.4.

Why, by the gap's parts: Budget (cap hit): about a quarter of the gap (.25 on MATH-500 T 1.0, .27 on hard328), about 12 of the 46 hard328 problems between one cued-base sample (161) and one RL sample (207). The raised cap alone gave Think-SFT +23 on hard328 (207 to 230), and the finished-over-cut rule picks up a further ~5-8 where sample 0 is still cut at 32,768 and sample 1 finishes. Reliability (right in another draw): .43-.63 of the gap; a second draw only wins the cases where the two samples disagree and exactly one finished, so about 2-4 problems from it. Ending is a sampled event and the cap cuts the long tail. Think-SFT's cut answers are unfinished work that comes out right at a high rate once it finishes, so a longer cap plus a second draw that prefers a finished sample turns cap hits into right answers more cheaply than a full vote over 4.

Command: `uv run tools/gpu.py submit l40s --hours 3 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model think_sft --opening-text $' line\!\n\nOkay' --set hard328 --shard 0/6 --temperature 1.0 --top-p 1.0 --max-tokens 32768 --samples 2 --seed 71000000 --commit $(git rev-parse HEAD) && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model think_sft --opening-text $' line\!\n\nOkay' --set math500 --shard 0/10 --temperature 1.0 --top-p 1.0 --max-tokens 32768 --samples 2 --seed 72000000 --commit $(git rev-parse HEAD)"`

RL arm: `uv run tools/gpu.py submit l40s --hours 3 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model rl --set hard328 --shard 0/6 --temperature 1.0 --top-p 1.0 --max-tokens 32768 --samples 2 --seed 71000000 --commit $(git rev-parse HEAD) && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model rl --set math500 --shard 0/10 --temperature 1.0 --top-p 1.0 --max-tokens 32768 --samples 2 --seed 72000000 --commit $(git rev-parse HEAD)"`


#### r10-n06-r1: route on hard328, --shard 0/6 (problems 0, 6, ..., 324) = 55; two-sample agree / finished / sample-0 rule, grader v3 (all-328 equivalent about 238 at 23,600 tokens, against 230 at 11,795 and 241 at 30,904) (of 55)

Proposer 40 [34, 45]. Median forecast 40; best known 38.6 (result-c8b994: 230 of 328 at 11795 tokens per problem (Think-SFT cue, cap 32,768, T 1.0 / top-p 1.0), scaled to 55 problems); gain 1.4.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 40 | [34, 46] |
| reader-2 | reader-2 | 40 | [35, 45] |
| round-10/training-m05 | training | 40 | [35, 45] |
| run-02/f2-m04 | run-02 | 39.5 | [34, 45] |
| round-09/problems-m05 | problems | 40 | [35, 45] |
| round-10/problems-m05 | problems | 40 | [35, 45] |
| run-03/f2-m05 | stopping | 39.5 | [34.5, 44.5] |
| round-09/stopping-m04 | stopping | 40 | [35, 45] |
| round-10/stopping-m03 | stopping | 41 | [36, 46] |
| run-04/f2-m04 | sampling | 39.5 | [34.5, 44.5] |
| round-09/sampling-m05 | sampling | 39.5 | [34.5, 44.5] |
| round-09/sampling-m06 | sampling | 39 | [34, 44] |
| round-09/sampling-m01 | sampling | 39.5 | [34.5, 44.5] |
| round-09/grader-m04 | grader | 40 | [35, 45] |
| round-09/grader-m06 | grader | 40 | [35, 45] |
| round-10/grader-m06 | grader | 40 | [35, 45] |

#### r10-n06-r2: route on MATH-500, --shard 0/10 (problems 0, 10, ..., 490) = 50; same rule, grader v3 (of 50)

Proposer 47 [44, 50]. Median forecast 47.5; best known 48.1 (result-818c20: 481 of 500 at 19503 tokens per problem (Think-SFT, cue, T 1.0 / top-p 1.0, vote over 4, no restart), scaled to 50 problems); gain -0.6.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 47.5 | [45, 50] |
| reader-2 | reader-2 | 47.5 | [45, 50] |
| round-10/training-m05 | training | 48 | [45, 50] |
| run-02/f2-m04 | run-02 | 47.5 | [44, 50] |
| round-10/problems-m05 | problems | 47 | [44, 50] |
| run-03/f2-m05 | stopping | 47 | [44, 50] |
| round-09/stopping-m04 | stopping | 47 | [44, 50] |
| round-10/stopping-m03 | stopping | 47 | [44, 50] |
| run-04/f2-m04 | sampling | 47.5 | [45, 50] |
| round-09/sampling-m05 | sampling | 47.5 | [45, 50] |
| round-09/sampling-m06 | sampling | 47.5 | [45, 50] |
| round-09/sampling-m01 | sampling | 47.5 | [45, 50] |
| round-09/grader-m06 | grader | 48 | [45.5, 50] |
| round-10/grader-m06 | grader | 48 | [45.5, 50] |

#### r10-n06-r3: rl on hard328, RL-Zero-Math plain, same flags, --shard 0/6 = 55; same rule, grader v3 (of 55)

Proposer 35 [30, 40]. Median forecast 34.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 35 | [29, 41] |
| reader-2 | reader-2 | 35 | [30, 40] |
| round-10/training-m05 | training | 34 | [29, 40] |
| run-02/f2-m04 | run-02 | 34 | [28, 40] |
| round-09/problems-m05 | problems | 34 | [29, 39] |
| round-10/problems-m05 | problems | 34 | [29, 39] |
| round-09/stopping-m04 | stopping | 34.5 | [29, 40] |
| run-04/f2-m04 | sampling | 34 | [29, 39] |
| round-09/sampling-m05 | sampling | 33.5 | [28.5, 38.5] |
| round-09/sampling-m06 | sampling | 33.5 | [28.5, 38.5] |
| round-09/sampling-m01 | sampling | 34 | [29, 39] |
| round-09/grader-m04 | grader | 34 | [29, 40] |
| round-09/grader-m06 | grader | 34 | [29, 40] |
| round-10/grader-m06 | grader | 34 | [29, 40] |

#### r10-n06-r4: rl on MATH-500, RL-Zero-Math plain, same flags, --shard 0/10 = 50; same rule, grader v3 (of 50)

Proposer 46 [43, 49]. Median forecast 46.7.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 46.5 | [43, 49] |
| reader-2 | reader-2 | 46.5 | [44, 49] |
| round-10/training-m05 | training | 47 | [43, 50] |
| run-02/f2-m04 | run-02 | 46.5 | [43, 49] |
| round-10/problems-m05 | problems | 46 | [43, 49] |
| round-09/stopping-m04 | stopping | 46.5 | [43, 49] |
| run-04/f2-m04 | sampling | 46.7 | [44, 49.5] |
| round-09/sampling-m05 | sampling | 46.7 | [44, 49.5] |
| round-09/sampling-m06 | sampling | 46.7 | [44, 49.5] |
| round-09/sampling-m01 | sampling | 46.7 | [44, 49.5] |
| round-09/grader-m06 | grader | 47 | [44, 50] |
| round-10/grader-m06 | grader | 47 | [44, 50] |

### r10-n05 (stopping, round-10/stopping-m03): Think-SFT keeps the base's cue but gets the </think> boundary it was trained to stop at: the opening becomes ' line!\n\n<think>\nOkay' and one prompt line asks for reasoning inside <think></think> and then only the final answer. One sample, T 1.0 / top-p 1.0, cap 16,384, no vote.

Model think_sft, 9000 tokens per problem, 210 GPU minutes (proposer's guess). Score 0.5.

Why, by the gap's parts: Budget: Think-SFT + cue hits the cap on 89 of 328 hard problems, and its cut answers are unfinished work it would close (at cap 32,768, 91 of 93 finish and 23 are right, result-c8b994). If the boundary ends answers before 16,384, up to about 23 answers on hard328 come back (I forecast 10 to 15) and about 5 on MATH-500 (24 of its 46 MATH-500 errors are cap hits, result-bf6124). Answer statement: a single short final answer after </think> takes away the lines after 'Answer:' that grader v3 rejects (16 of 74 finished-wrong answers end on a line equal to the gold, result-818c20). That is up to about 4 per 500 on MATH-500 and about 0 on hard328. Loop: 0, since T 1.0 has no loops. Reliability and capability: unchanged, because precision on finished answers stays the same. Think-SFT was trained to end its reasoning at </think> and then write one short answer and end-of-text. With the base's raw cue there is no such boundary, so after solving it keeps re-checking until the cap and the answer scores zero. Putting the boundary back makes it stop where it was trained to stop, with the same precision on finished answers.

Command: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model think_sft --prompt-suffix ' Reason inside <think> </think>; after </think> write only the final answer as \\boxed{} and stop.' --opening-text $' line!\n\n<think>\nOkay' --set hard328 --shard 0/2 --temperature 1.0 --top-p 1.0 --max-tokens 16384 --samples 1 --seed 3000000 --commit $(git rev-parse HEAD)" && uv run tools/gpu.py submit l40s --hours 1 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model think_sft --prompt-suffix ' Reason inside <think> </think>; after </think> write only the final answer as \\boxed{} and stop.' --opening-text $' line!\n\n<think>\nOkay' --set math500 --shard 0/5 --temperature 1.0 --top-p 1.0 --max-tokens 16384 --samples 1 --seed 41000000 --commit $(git rev-parse HEAD)"`

RL arm: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model rl --prompt-suffix ' Reason inside <think> </think>; after </think> write only the final answer as \\boxed{} and stop.' --opening-text $' line!\n\n<think>\nOkay' --set hard328 --shard 0/2 --temperature 1.0 --top-p 1.0 --max-tokens 16384 --samples 1 --seed 3000000 --commit $(git rev-parse HEAD)" && uv run tools/gpu.py submit l40s --hours 1 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model rl --prompt-suffix ' Reason inside <think> </think>; after </think> write only the final answer as \\boxed{} and stop.' --opening-text $' line!\n\n<think>\nOkay' --set math500 --shard 0/5 --temperature 1.0 --top-p 1.0 --max-tokens 16384 --samples 1 --seed 41000000 --commit $(git rev-parse HEAD)"`


#### r10-n05-r1: route on hard328, right answers with grader v3 on hard328 --shard 0/2 (problems 0, 2, 4, ...; 164), one Think-SFT sample with the </think> boundary opening, cap hits counted wrong. Comparison: Think-SFT + cue one sample, 212 of 328 at 10,137 tokens (about 106 of 164). (of 164)

Proposer 111 [99, 120]. Median forecast 104; best known 103.5 (result-c8b994: 207 of 328 at 10048 tokens per problem (Think-SFT cue, same answers counted at cap 16,384); no row at or below these tokens: the cheapest row, scaled to 164 problems); gain 0.5.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 100 | [85, 113] |
| reader-2 | reader-2 | 104 | [92, 116] |
| round-10/training-m05 | training | 104 | [92, 116] |
| round-09/weights-m04 | weights | 106 | [95, 117] |
| run-02/f2-m04 | run-02 | 107 | [95, 119] |
| round-09/problems-m05 | problems | 104 | [92, 116] |
| round-10/stopping-m03 | stopping | 112 | [100, 124] |
| round-09/sampling-m03 | sampling | 104 | [92, 116] |
| run-04/f2-m04 | sampling | 104 | [92, 116] |
| round-09/sampling-m01 | sampling | 104 | [92, 116] |
| run-08/f2-m01 | grader | 103 | [88, 116] |
| round-09/grader-m04 | grader | 105 | [92, 117] |
| round-09/grader-m01 | grader | 103 | [88, 116] |

#### r10-n05-r2: route on MATH-500, right answers with grader v3 on MATH-500 --shard 0/5 (problems 0, 5, 10, ...; 100), one Think-SFT sample with the boundary opening. Comparison: Think-SFT + cue one sample, 461 of 500 at 4,900 tokens (about 92 of 100). (of 100)

Proposer 93 [88, 97]. Median forecast 92; best known 92.2 (result-818c20: 461 of 500 at 4900 tokens per problem (Think-SFT, cue, T 1.0 / top-p 1.0, one sample (sample 0 of 4)), scaled to 100 problems); gain -0.2.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 91 | [84, 96] |
| reader-2 | reader-2 | 91 | [85, 96] |
| round-10/training-m05 | training | 92 | [87, 97] |
| round-09/weights-m04 | weights | 92 | [86, 97] |
| run-02/f2-m04 | run-02 | 92.5 | [88, 97] |
| round-10/stopping-m03 | stopping | 93 | [88, 97] |
| round-09/sampling-m03 | sampling | 92 | [86.5, 97] |
| run-04/f2-m04 | sampling | 92 | [86.5, 97] |
| round-09/sampling-m01 | sampling | 92 | [86.5, 97] |
| run-08/f2-m01 | grader | 91 | [85, 96] |
| round-09/grader-m01 | grader | 91 | [85, 96] |

#### r10-n05-r3: rl on hard328, right answers with grader v3 on hard328 --shard 0/2 (164), RL-Zero-Math with the same prompt line and opening, one sample. Comparison: RL plain one sample, 190 to 209 of 328 (about 100 of 164). (of 164)

Proposer 99 [88, 109]. Median forecast 98.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 97 | [85, 108] |
| reader-2 | reader-2 | 97 | [85, 108] |
| round-10/training-m05 | training | 98 | [86, 110] |
| round-09/problems-m05 | problems | 98 | [87, 109] |
| round-09/sampling-m03 | sampling | 99 | [87, 111] |
| run-04/f2-m04 | sampling | 99 | [87, 111] |
| round-09/sampling-m01 | sampling | 99 | [87, 111] |
| run-08/f2-m01 | grader | 98 | [86, 110] |
| round-09/grader-m04 | grader | 99 | [87, 111] |
| round-09/grader-m01 | grader | 98 | [86, 110] |

#### r10-n05-r4: rl on MATH-500, right answers with grader v3 on MATH-500 --shard 0/5 (100), RL-Zero-Math with the same prompt line and opening, one sample. Comparison: RL plain, 463 of 500 (about 92 of 100). (of 100)

Proposer 91 [85, 96]. Median forecast 91.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 91 | [85, 96] |
| reader-2 | reader-2 | 91 | [85, 96] |
| round-10/training-m05 | training | 92 | [87, 97] |
| round-09/sampling-m03 | sampling | 91 | [85.5, 96] |
| run-04/f2-m04 | sampling | 91 | [85.5, 96] |
| round-09/sampling-m01 | sampling | 91 | [85.5, 96] |
| run-08/f2-m01 | grader | 91 | [86, 96] |
| round-09/grader-m01 | grader | 91 | [86, 96] |

### r10-n02 (weights, round-09/weights-m04): Think-SFT with the cue, cap raised from 16,384 to 32,768 tokens, 3 samples at T 1.0 / top-p 1.0, majority vote (no majority: the first finished sample), so that budget does the finishing the RL delta would do and the vote handles reliability.

Model think_sft, 35400 tokens per problem, 230 GPU minutes (proposer's guess). Score 0.4.

Why, by the gap's parts: Budget (cap hits, about 25 % of the cued-base gap: about 12 of the 46-problem one-sample hard328 gap, about 16 of 65 on MATH-500), handled by the doubled cap on Think-SFT's sound but cut work (+23 one-sample on hard328, result-c8b994). Reliability (43-63 %: about 20 on hard328, about 40 on MATH-500), handled by the 3-sample vote. Part of capability (27 % on hard328, about 12), handled by Think-SFT's imitation coverage, which no reward produced. On Think-SFT the RL difference only finishes long work that is sound but cut off, and its gain is capped by how much cut work was sound. Prompt changes do not move that finishing rate, so the reward-free stand-in for the finishing operator is more budget for exactly that work, and a vote then handles the reliability part.

Command: `uv run tools/gpu.py submit l40s --hours 2.5 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model think_sft --opening-text $' line!\n\nOkay' --set hard328 --shard 0/8 --temperature 1.0 --top-p 1.0 --max-tokens 32768 --samples 3 --seed 71000000 --commit $(git rev-parse HEAD) && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model think_sft --opening-text $' line!\n\nOkay' --set math500 --shard 0/10 --temperature 1.0 --top-p 1.0 --max-tokens 32768 --samples 3 --seed 72000000 --commit $(git rev-parse HEAD)"`

RL arm: `uv run tools/gpu.py submit l40s --hours 2.5 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model rl --opening-text $' line!\n\nOkay' --set hard328 --shard 0/8 --temperature 1.0 --top-p 1.0 --max-tokens 32768 --samples 3 --seed 71000000 --commit $(git rev-parse HEAD) && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model rl --opening-text $' line!\n\nOkay' --set math500 --shard 0/10 --temperature 1.0 --top-p 1.0 --max-tokens 32768 --samples 3 --seed 72000000 --commit $(git rev-parse HEAD)"`


#### r10-n02-r1: route on hard328, --shard 0/8 = 41 problems, majority vote over 3 samples at cap 32,768, grader v3 (about 249/328 scaled) (of 41)

Proposer 31 [26, 35]. Median forecast 30.5; best known 30.1 (result-818c20: 241 of 328 at 30904 tokens per problem (Think-SFT, cue, T 1.0 / top-p 1.0, sequential vote up to 4 (chosen on MATH-500)), scaled to 41 problems); gain 0.4.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 30.5 | [25, 36] |
| reader-2 | reader-2 | 30.5 | [26, 35] |
| round-10/training-m05 | training | 31 | [27, 35] |
| run-02/f2-m04 | run-02 | 29.5 | [24, 35] |
| round-09/problems-m05 | problems | 31 | [26, 36] |
| round-10/problems-m05 | problems | 31 | [26, 36] |
| run-03/f2-m05 | stopping | 30 | [25, 35] |
| round-09/stopping-m04 | stopping | 31 | [26, 36] |
| round-10/stopping-m03 | stopping | 32 | [27, 36] |
| run-04/f2-m04 | sampling | 30.3 | [26, 34.5] |
| round-09/sampling-m05 | sampling | 30.5 | [26, 35] |
| round-09/sampling-m06 | sampling | 30 | [25.5, 34] |
| round-09/sampling-m01 | sampling | 30.3 | [26, 34.5] |
| round-09/grader-m04 | grader | 30.5 | [26, 35] |
| round-09/grader-m06 | grader | 31 | [26, 36] |
| round-10/grader-m06 | grader | 30.5 | [26, 35] |

#### r10-n02-r2: route on MATH-500, --shard 0/10 = 50 problems, majority vote over 3 samples at cap 32,768, grader v3 (of 50)

Proposer 48 [45, 50]. Median forecast 48; best known 48.1 (result-818c20: 481 of 500 at 19503 tokens per problem (Think-SFT, cue, T 1.0 / top-p 1.0, vote over 4, no restart), scaled to 50 problems); gain -0.1.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 48 | [45, 50] |
| reader-2 | reader-2 | 48 | [46, 50] |
| round-10/training-m05 | training | 48 | [45, 50] |
| run-02/f2-m04 | run-02 | 48 | [45, 50] |
| round-10/problems-m05 | problems | 48 | [45, 50] |
| run-03/f2-m05 | stopping | 48 | [45, 50] |
| round-09/stopping-m04 | stopping | 48 | [45, 50] |
| round-10/stopping-m03 | stopping | 48 | [45, 50] |
| run-04/f2-m04 | sampling | 48 | [45.5, 50] |
| round-09/sampling-m05 | sampling | 48 | [45.5, 50] |
| round-09/sampling-m06 | sampling | 48 | [45.5, 50] |
| round-09/sampling-m01 | sampling | 48 | [45.5, 50] |
| round-09/grader-m06 | grader | 48 | [45.5, 50] |
| round-10/grader-m06 | grader | 48 | [45.5, 50] |

#### r10-n02-r3: rl on hard328, --shard 0/8 = 41 problems, RL-Zero-Math same procedure, vote over 3, grader v3 (of 41)

Proposer 28 [23, 33]. Median forecast 27.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 27.5 | [22, 33] |
| reader-2 | reader-2 | 27.5 | [23, 32] |
| round-10/training-m05 | training | 27 | [22, 32] |
| run-02/f2-m04 | run-02 | 27 | [21, 33] |
| round-09/problems-m05 | problems | 27 | [22, 32] |
| round-10/problems-m05 | problems | 28 | [23, 33] |
| round-09/stopping-m04 | stopping | 27.5 | [23, 32] |
| run-04/f2-m04 | sampling | 27 | [23, 31] |
| round-09/sampling-m05 | sampling | 26.5 | [22.5, 30.5] |
| round-09/sampling-m06 | sampling | 26.5 | [22.5, 30.5] |
| round-09/sampling-m01 | sampling | 27 | [23, 31] |
| round-09/grader-m04 | grader | 27 | [22, 32] |
| round-09/grader-m06 | grader | 27 | [23, 32] |
| round-10/grader-m06 | grader | 27 | [23, 32] |

#### r10-n02-r4: rl on MATH-500, --shard 0/10 = 50 problems, RL-Zero-Math same procedure, vote over 3, grader v3 (of 50)

Proposer 47 [44, 49]. Median forecast 47.15.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 47 | [44, 50] |
| reader-2 | reader-2 | 47.5 | [45, 50] |
| round-10/training-m05 | training | 47 | [44, 50] |
| run-02/f2-m04 | run-02 | 47.4 | [44, 50] |
| round-10/problems-m05 | problems | 47 | [44, 50] |
| round-09/stopping-m04 | stopping | 47 | [44, 50] |
| run-04/f2-m04 | sampling | 47.3 | [44.5, 50] |
| round-09/sampling-m05 | sampling | 47.3 | [44.5, 50] |
| round-09/sampling-m06 | sampling | 47.3 | [44.5, 50] |
| round-09/sampling-m01 | sampling | 47.3 | [44.5, 50] |
| round-09/grader-m06 | grader | 47 | [44, 50] |
| round-10/grader-m06 | grader | 47 | [44, 50] |

### r10-n04 (problems, round-10/problems-m05): Think-SFT (no reward) with the cue, token cap raised to 32,768, three samples per problem scored by a sequential vote (take samples 1 and 2 if their answers agree, else add sample 3; plurality, ties to the shortest finished sample).

Model think_sft, 35400 tokens per problem, 225 GPU minutes (proposer's guess). Score 0.4.

Why, by the gap's parts: Capability: the base never solves about 79 hard328 problems even after restarts, and Think-SFT's wider reach covers part of that (one sample 212 against the base's 161). Budget (cap hit; 0.21 to 0.27 of the gross gap in result-f39ba8): on hard328, raising Think-SFT's cap from 16,384 to 32,768 adds about 23 (207 to 230), and on MATH-500 about 1 to 3. Reliability (0.43 to 0.67 of the gap): the vote adds about 15 to 20 on hard328 (vote over 4 at cap 16k gave 212 to 241) and about 15 on MATH-500 (461 to 481). Full-set forecast about 247 of 328 at about 35,400 generated tokens, against 241 for the best known row at 30,904 to 40,410 tokens. Weight edits and votes only reweight paths the host already has, so their gains stop near the host's pass@k; a host with more reach (Think-SFT) raises that ceiling. A longer cap lets its long contest derivations finish, and the vote then turns its reach into right answers.

Command: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe interp --other think_sft --alpha 1.0 --rounding nearest --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label think_sft --prompt cue --set hard328 --shard 0/8 --temperature 1.0 --top-p 1.0 --max-tokens 32768 --samples 3 --seed 71000000 --commit $(git rev-parse HEAD)" && uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe interp --other think_sft --alpha 1.0 --rounding nearest --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label think_sft --prompt cue --set math500 --n 100 --temperature 1.0 --top-p 1.0 --max-tokens 32768 --samples 3 --seed 73000000 --commit $(git rev-parse HEAD)"`

RL arm: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model rl --prompt plain --set hard328 --shard 0/8 --temperature 1.0 --top-p 1.0 --max-tokens 32768 --samples 3 --seed 71000000 --commit $(git rev-parse HEAD)" && uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model rl --prompt plain --set math500 --n 100 --temperature 1.0 --top-p 1.0 --max-tokens 32768 --samples 3 --seed 73000000 --commit $(git rev-parse HEAD)"`


#### r10-n04-r1: route on hard328, hard328 --shard 0/8 (problems 0, 8, 16, ..., 41 problems), Think-SFT cue, cap 32,768, sequential vote of up to 3 samples, grader v3 (of 41)

Proposer 31 [26, 35]. Median forecast 30.5; best known 30.1 (result-818c20: 241 of 328 at 30904 tokens per problem (Think-SFT, cue, T 1.0 / top-p 1.0, sequential vote up to 4 (chosen on MATH-500)), scaled to 41 problems); gain 0.4.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 30.5 | [25, 36] |
| reader-2 | reader-2 | 30.5 | [26, 35] |
| round-10/training-m05 | training | 31 | [27, 35] |
| run-02/f2-m04 | run-02 | 29.5 | [24, 35] |
| round-09/problems-m05 | problems | 31 | [26, 36] |
| round-10/problems-m05 | problems | 31 | [26, 36] |
| run-03/f2-m05 | stopping | 30 | [25, 35] |
| round-09/stopping-m04 | stopping | 31 | [26, 36] |
| round-10/stopping-m03 | stopping | 32 | [27, 36] |
| run-04/f2-m04 | sampling | 30.5 | [26, 35] |
| round-09/sampling-m05 | sampling | 30.5 | [26, 35] |
| round-09/sampling-m06 | sampling | 30 | [25.5, 34.5] |
| round-09/sampling-m01 | sampling | 30.5 | [26, 35] |
| round-09/grader-m04 | grader | 30.5 | [26, 35] |
| round-09/grader-m06 | grader | 31 | [26, 36] |
| round-10/grader-m06 | grader | 30.5 | [26, 35] |

#### r10-n04-r2: route on MATH-500, MATH-500 first 100 problems (--n 100), Think-SFT cue, cap 32,768, sequential vote of up to 3 samples, grader v3 (of 100)

Proposer 96 [92, 99]. Median forecast 96; best known 96.2 (result-818c20: 481 of 500 at 19503 tokens per problem (Think-SFT, cue, T 1.0 / top-p 1.0, vote over 4, no restart), scaled to 100 problems); gain -0.2.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 97 | [93, 100] |
| reader-2 | reader-2 | 96 | [93, 99] |
| round-10/training-m05 | training | 96 | [92, 99] |
| run-02/f2-m04 | run-02 | 96 | [92, 99] |
| round-10/problems-m05 | problems | 96 | [92, 99] |
| run-03/f2-m05 | stopping | 95.5 | [91, 99] |
| round-09/stopping-m04 | stopping | 96 | [92, 99] |
| round-10/stopping-m03 | stopping | 96.5 | [93, 99] |
| run-04/f2-m04 | sampling | 96 | [93, 98.5] |
| round-09/sampling-m05 | sampling | 96 | [93, 98.5] |
| round-09/sampling-m06 | sampling | 96 | [93, 98.5] |
| round-09/sampling-m01 | sampling | 96 | [93, 98.5] |
| round-09/grader-m06 | grader | 96 | [93, 99] |
| round-10/grader-m06 | grader | 96 | [93, 99] |

#### r10-n04-r3: rl on hard328, hard328 --shard 0/8 (41 problems), RL-Zero-Math plain, cap 32,768, same sequential vote of up to 3 samples, grader v3 (of 41)

Proposer 28 [23, 32]. Median forecast 27.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 27.5 | [22, 33] |
| reader-2 | reader-2 | 27.5 | [23, 32] |
| round-10/training-m05 | training | 27 | [22, 32] |
| run-02/f2-m04 | run-02 | 27 | [21, 33] |
| round-09/problems-m05 | problems | 27 | [22, 32] |
| round-10/problems-m05 | problems | 28 | [23, 33] |
| round-09/stopping-m04 | stopping | 27.5 | [23, 32] |
| run-04/f2-m04 | sampling | 27 | [23, 31] |
| round-09/sampling-m05 | sampling | 27 | [23, 31] |
| round-09/sampling-m06 | sampling | 26.5 | [22.5, 30.5] |
| round-09/sampling-m01 | sampling | 27 | [23, 31] |
| round-09/grader-m04 | grader | 27 | [22, 32] |
| round-09/grader-m06 | grader | 27 | [22, 32] |
| round-10/grader-m06 | grader | 27 | [22, 32] |

#### r10-n04-r4: rl on MATH-500, MATH-500 first 100 problems, RL-Zero-Math plain, cap 32,768, same sequential vote of up to 3 samples, grader v3 (of 100)

Proposer 95 [91, 98]. Median forecast 97.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 97 | [94, 100] |
| reader-2 | reader-2 | 96.5 | [94, 99] |
| round-10/training-m05 | training | 97 | [93, 100] |
| run-02/f2-m04 | run-02 | 97 | [94, 99] |
| round-10/problems-m05 | problems | 97 | [94, 100] |
| round-09/stopping-m04 | stopping | 97 | [94, 99] |
| run-04/f2-m04 | sampling | 96.5 | [93.5, 99] |
| round-09/sampling-m05 | sampling | 96.5 | [93.5, 99] |
| round-09/sampling-m06 | sampling | 96.5 | [93.5, 99] |
| round-09/sampling-m01 | sampling | 96.5 | [93.5, 99] |
| round-09/grader-m06 | grader | 97 | [94, 100] |
| round-10/grader-m06 | grader | 97 | [94, 100] |

### r10-n03 (run-02, run-02/f2-m04): Think-SFT with the cue, 3 samples per problem with the cap lowered to 12,288 tokens, plurality vote over finished boxed answers only (capped samples abstain), ties to the shortest finished sample; no answer if all 3 are capped.

Model think_sft, 25500 tokens per problem, 225 GPU minutes (proposer's guess). Score -0.8.

Why, by the gap's parts: Reliability, the largest part (result-f39ba8: .43 of the hard328 gap, .63 at MATH-500 T 1.0, about 20 of the ~46 one-sample hard328 problems and ~40 of 65 on MATH-500). The vote wins these because a lone right sample is no longer outvoted when the other samples hit the cap and abstain. Budget (.25 to .27, ~12 hard328 problems) is given up on purpose: the lower cap turns long unsolved runs into cheap abstentions instead of buying them back. Capability (.27 on hard328, ~12) and answer statement (.03) are left to what Think-SFT already has without any reward. Think-SFT's unsolved samples run to the cap rather than box a guess, so in a plurality vote they abstain, and its vote sits near pass@k. That means the cap can be lowered: the tokens burned on unsolved samples shrink and the abstentions stay, so the vote's gain is kept at fewer tokens. Raising the cap (32k) does the opposite and turns abstentions into scattered wrong answers.

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe interp --other think_sft --alpha 1.0 --rounding nearest --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label think_sft --prompt cue --set hard328 --shard 0/8 --temperature 1.0 --top-p 1.0 --max-tokens 12288 --samples 3 --seed 3000000 --commit $(git rev-parse HEAD) && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label think_sft --prompt cue --set math500 --shard 0/6 --temperature 1.0 --top-p 1.0 --max-tokens 12288 --samples 3 --seed 41000000 --commit $(git rev-parse HEAD)`

RL arm: `bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model rl --prompt plain --set hard328 --shard 0/8 --temperature 1.0 --top-p 1.0 --max-tokens 12288 --samples 3 --seed 3000000 --commit $(git rev-parse HEAD) && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model rl --prompt plain --set math500 --shard 0/6 --temperature 1.0 --top-p 1.0 --max-tokens 12288 --samples 3 --seed 45000000 --commit $(git rev-parse HEAD)`


#### r10-n03-r1: route on hard328, --shard 0/8 of hard328 (problems 0, 8, 16, ...; 41), grader v3, after the abstaining plurality vote over 3 samples at cap 12,288; median is about 233/328 scaled, against the best known think_sft row at no more tokens (230 of 328 at 11,795) (of 41)

Proposer 29 [25, 33]. Median forecast 28; best known 28.8 (result-c8b994: 230 of 328 at 11795 tokens per problem (Think-SFT cue, cap 32,768, T 1.0 / top-p 1.0), scaled to 41 problems); gain -0.8.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 28 | [23, 33] |
| reader-2 | reader-2 | 28 | [23, 33] |
| round-10/training-m05 | training | 28 | [23, 33] |
| run-02/f2-m01 | run-02 | 26 | [20, 32] |
| run-02/f2-m04 | run-02 | 27.5 | [22, 33] |
| round-09/problems-m05 | problems | 28 | [23, 33] |
| round-10/problems-m05 | problems | 28 | [23, 33] |
| run-03/f2-m05 | stopping | 28.5 | [23.5, 33.5] |
| round-09/stopping-m04 | stopping | 28 | [23, 33] |
| round-10/stopping-m03 | stopping | 27 | [22, 32] |
| run-04/f2-m04 | sampling | 28 | [23.5, 32.5] |
| round-09/sampling-m05 | sampling | 26 | [21.5, 30.5] |
| round-09/sampling-m06 | sampling | 27.5 | [23, 32] |
| round-09/sampling-m01 | sampling | 28 | [23.5, 32.5] |
| round-09/grader-m04 | grader | 28 | [23, 33] |
| round-09/grader-m06 | grader | 28 | [23, 33] |
| round-10/grader-m06 | grader | 28.5 | [24, 33] |

#### r10-n03-r2: route on MATH-500, --shard 0/6 of MATH-500 (84 problems), grader v3, same vote rule (of 84)

Proposer 80 [77, 83]. Median forecast 80; best known 80.8 (result-818c20: 481 of 500 at 19503 tokens per problem (Think-SFT, cue, T 1.0 / top-p 1.0, vote over 4, no restart), scaled to 84 problems); gain -0.8.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 80 | [76, 83] |
| reader-2 | reader-2 | 80 | [76, 83] |
| round-10/training-m05 | training | 79 | [75, 83] |
| run-02/f2-m01 | run-02 | 80.5 | [77, 83] |
| run-02/f2-m04 | run-02 | 81 | [77, 84] |
| round-10/problems-m05 | problems | 80 | [76, 83] |
| run-03/f2-m05 | stopping | 80 | [76, 83] |
| round-09/stopping-m04 | stopping | 80 | [76, 83] |
| round-10/stopping-m03 | stopping | 79 | [75, 83] |
| run-04/f2-m04 | sampling | 80 | [77, 83] |
| round-09/sampling-m05 | sampling | 79.5 | [76, 83] |
| round-09/sampling-m06 | sampling | 80 | [77, 83] |
| round-09/sampling-m01 | sampling | 80 | [77, 83] |
| round-09/grader-m06 | grader | 80 | [76, 83] |
| round-10/grader-m06 | grader | 80 | [77, 83] |

#### r10-n03-r3: rl on hard328, RL-Zero-Math plain, --shard 0/8 of hard328 (41), grader v3, same cap, 3 samples, same abstaining vote (of 41)

Proposer 27 [23, 31]. Median forecast 26.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 26 | [21, 31] |
| reader-2 | reader-2 | 26 | [21, 31] |
| round-10/training-m05 | training | 26 | [21, 31] |
| run-02/f2-m01 | run-02 | 25.5 | [20, 31] |
| run-02/f2-m04 | run-02 | 26.5 | [21, 32] |
| round-09/problems-m05 | problems | 27 | [22, 32] |
| round-10/problems-m05 | problems | 27 | [22, 32] |
| round-09/stopping-m04 | stopping | 26.5 | [22, 31] |
| run-04/f2-m04 | sampling | 25.5 | [21, 30] |
| round-09/sampling-m05 | sampling | 24.5 | [20, 29] |
| round-09/sampling-m06 | sampling | 25 | [20.5, 29.5] |
| round-09/sampling-m01 | sampling | 25.5 | [21, 30] |
| round-09/grader-m04 | grader | 26 | [21, 31] |
| round-09/grader-m06 | grader | 26 | [21, 31] |
| round-10/grader-m06 | grader | 26.5 | [22, 31] |

#### r10-n03-r4: rl on MATH-500, RL-Zero-Math plain, --shard 0/6 of MATH-500 (84), grader v3, same vote rule (of 84)

Proposer 79 [75, 82]. Median forecast 79.5.

| forecaster | family | value | 90 % interval |
|---|---|---|---|
| reader-1 | reader-1 | 79.5 | [76, 83] |
| reader-2 | reader-2 | 79.5 | [76, 83] |
| round-10/training-m05 | training | 79 | [75, 83] |
| run-02/f2-m01 | run-02 | 79.5 | [76, 83] |
| run-02/f2-m04 | run-02 | 79.5 | [76, 83] |
| round-10/problems-m05 | problems | 79 | [75, 83] |
| round-09/stopping-m04 | stopping | 79.5 | [76, 83] |
| run-04/f2-m04 | sampling | 79 | [75.5, 82] |
| round-09/sampling-m05 | sampling | 78.5 | [75, 82] |
| round-09/sampling-m06 | sampling | 79 | [75.5, 82] |
| round-09/sampling-m01 | sampling | 79 | [75.5, 82] |
| round-09/grader-m06 | grader | 79.5 | [76, 83] |
| round-10/grader-m06 | grader | 79.5 | [76, 83] |
