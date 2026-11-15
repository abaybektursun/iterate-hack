# Cells designed by the theories, round-09

Written 2026-11-15T18:25:15 UTC (board read 2026-11-15T18:03:05 UTC). Plan `specs/SPEC_engine_v9.md`. Families: training (7), run-02 (2), weights (9), problems (7), stopping (8), sampling (7), grader (6); 48 forecasters (each reader is its own family). 0 cells dropped by the flag check (cells.json "dropped"). Separation = pairs of forecasters from different families whose 90 % intervals do not overlap, summed over the cell's readouts.

- C1: 46 cells proposed, 39 after merging (needs 20 and 10): holds.
- C2: 4 merged cells have 3 or more such pairs (needs 5): refuted.
- C3: 0 base-only readouts have a forecast above the best known base count (none): refuted.

## Every merged cell

| cell | model | prompt | set | n | base only | GPU minutes | separation | per minute |
|---|---|---|---|---|---|---|---|---|
| m11 | base - 1.0 x top-8 singular directions per matrix of (RL-Math 3.1 - base) (wsp_edit recipe top8, scale -1, stochastic rounding) | cue | math500 | 500 (all) |  | 105 | 10 | 0.0952 |
| m13 | base + 2.0 x top-64 singular directions per matrix of (RL-Math 3.1 - base) (wsp_edit recipe top8 with --k 64, scale 2, stochastic rounding) | cue | hard328 | 164: shard 0/2 (problems 0, 2, ..., 326) |  | 80 | 7 | 0.0875 |
| m21 | base Olmo-3-1025-7B + 1.0 x the top 8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Code - base), stochastic bf16 rounding seed 0 | plain | MATH-500 | first 250 problems (--n 250) |  | 55 | 3 | 0.0545 |
| m05 | untrained base Olmo-3-1025-7B | plain (no cue) | math500 | 100: the first 100 problems (--n 100) | yes | 90 | 3 | 0.0333 |
| m18 | base + 0.125 x (RL-Math 3.1 - base), whole difference, stochastic bf16 rounding (merge_weights --alpha 0.125 --rounding stochastic) | plain | math500 | 500 (all) |  | 90 | 2 | 0.0222 |
| m14 | base + 3.0 x top-8 singular directions per matrix of (RL-Math 3.1 - base), MLP matrices only (wsp_edit recipe top8, --mods mlp, scale 3, stochastic rounding) | cue | hard328 | 164: shard 0/2 |  | 75 | 1 | 0.0133 |
| m06 | RL-Math 3.1 minus its top-1 singular direction per matrix (wsp_edit recipe bulk with --k 1: RL - top-1 component of (RL - base)), stochastic rounding | cue | hard328 | 164: even-index problems 0, 2, ..., 326 (--shard 0/2) |  | 85 | 1 | 0.0118 |
| m29 | base + 4.0 x top-1 singular direction per matrix of (RL-Math 3.1 - base) (wsp_edit --recipe top8 --k 1 --scale 4.0, stochastic rounding, seed 0) | cue | hard328 | 164: hard328 shard 0/2 (problems 0, 2, ..., 326) |  | 90 | 1 | 0.0111 |
| m01 | base + 1.5 x top-8 singular directions per matrix of (RL-Code 3.1 - base), all layers, stochastic rounding (wsp_edit recipe top8, --other rl_code) | cue | math500 | 250: even-index problems 0, 2, ..., 498 (--shard 0/2) |  | 65 | 0 | 0 |
| m02 | allenai/Olmo-3-7B-Think-SFT, written as base + 1.0 x (Think-SFT - base) with nearest rounding (wsp_edit recipe interp, as in the relay jobs) | cue (the base's raw prompt asking for the answer on its own line after 'Answer:', plus the 3-token opening cue); not Think-SFT's ChatML template | math500 | 400: the first 400 problems (--n 400) |  | 105 | 0 | 0 |
| m03 | Think-SFT + 1.0 x (RL-Math 3.1 - base) (delta_sum --host think_sft --donor rl_math --alpha 1.0) | cue | hard328 | 328: all problems of hard328 (no --shard / --n), so that both the even-index half (shard 0/2, problems 0, 2, ..., 326) and the first 140 problems (0..139) are covered with their own per-problem seeds |  | 115 | 0 | 0 |
| m04 | Olmo-3.1-7B-RL-Zero-Math step_0100 (rev 0a45720c), written as base + 1.0 x (step 100 - base) with nearest rounding (wsp_edit recipe interp; --other name of the step-100 checkpoint in wsp_edit's model table) | plain | hard328 | 164: odd-index problems 1, 3, ..., 327 (--shard 1/2); extends target t01 (first 164) to an interleaved half |  | 85 | 0 | 0 |
| m07 | base + 1.5 x the late-MLP-only edit of RL-Math 3.1 (wsp_edit recipe late3: top-3 directions of the late-layer MLP matrices, 24 terms), stochastic rounding | cue | hard328 | 164: even-index problems 0, 2, ..., 326 (--shard 0/2) |  | 85 | 0 | 0 |
| m08 | untrained base allenai/Olmo-3-1025-7B (run_cell --model base) | cue (the 3-token opening cue of frozen4.json) | hard328 | 164: the even-index half of hard328, problems 0, 2, 4, ..., 326 (--shard 0/2) | yes | 70 | 0 | 0 |
| m09 | Think-SFT + 2 x (RL-Math 3.1 - base): delta_sum --host think_sft --donor rl_math --alpha 2 (all tensors, bf16), written to /tmp/theta | cue (base cue on the raw template, as in the stored Think-SFT cue cells) | fresh2026 (136 competition problems published in 2026: AIME, HMMT Feb and Nov) | 136, all problems |  | 108 | 0 | 0 |
| m10 | base + 1.5 x top-8 singular directions per matrix of (RL-Code 3.1 - base), all layers, all modules, stochastic bf16 rounding (wsp_edit recipe top8, other rl_code, scale 1.5) | cue | hard328 | 164: shard 0/2 (problems 0, 2, 4, ..., 326) |  | 70 | 0 | 0 |
| m12 | base + 0.0625 x (RL-Math 3.1 - base), whole difference, stochastic bf16 rounding (merge_weights --alpha 0.0625 --rounding stochastic) | plain | math500 | 500 (all) |  | 85 | 0 | 0 |
| m15 | base + 3.0 x top-3 singular directions of the late-layer MLP matrices of (RL-Math 3.1 - base) (wsp_edit recipe late3, 24 terms, scale 3, stochastic rounding) | cue | hard328 | 164: shard 0/2 |  | 70 | 0 | 0 |
| m16 | Think-SFT (allenai/Olmo-3-7B-Think-SFT) + 2.0 x (RL-Math 3.1 - base), whole difference (delta_sum --host think_sft --donor rl --alpha 2) | cue | fresh2026 | 136 (all) |  | 85 | 0 | 0 |
| m17 | base + 9.0 x top-8 singular directions per matrix of (RL-Math 3.1 step-100 checkpoint - base), i.e. step-100's top-8 at about the norm of the final top-8 (wsp_edit recipe top8, other = the step_0100 checkpoint, scale 9, stochastic rounding) | cue | hard328 | 164: shard 0/2 |  | 75 | 0 | 0 |
| m19 | base Olmo-3-1025-7B + 1.5 x the top 8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Code - base), all layers and modules, stochastic bf16 rounding seed 0 (the edit of result-a1bf75's 1.5x code cell, now scored on math) | cue (Math opening cue of frozen4.json) | MATH-500 | 500 (all problems) |  | 105 | 0 | 0 |
| m20 | Olmo-3.1-7B-RL-Zero-Math (rl, main = step 2,800, frozen4 revision) | plain | hard328 | first 164 problems of hard328 (--n 164) |  | 85 | 0 | 0 |
| m22 | Olmo-3.1-7B-RL-Zero-Math checkpoint step_0400 (revision 897c0ce4), written as a model directory by wsp_edit --recipe interp at alpha 1.0 (interpolation at 1 = the checkpoint itself) | plain | hard328 | 164 problems: shard 1/2 of hard328 (odd indices 1, 3, ..., 327) |  | 85 | 0 | 0 |
| m23 | allenai/Olmo-3-7B-Think-SFT, written by wsp_edit --recipe interp --other think_sft --alpha 1.0 (as in the relay jobs) | cue | hard328 | first 164 problems of hard328 (--n 164) |  | 95 | 0 | 0 |
| m24 | base Olmo-3-1025-7B + 2.0 x the top 8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Math - base), stochastic bf16 rounding seed 0 (the 2x dial edit of result-6f1bb7) | cue | fresh2026 | 136 (all problems of fresh2026_v1.json) |  | 85 | 0 | 0 |
| m25 | base + 2.0 x (RL-Math 3.1 - base), whole difference, stochastic bf16 rounding (merge_weights --other rl --alpha 2.0) | cue | hard328 | 164: hard328 shard 0/2 (problems 0, 2, 4, ..., 326) |  | 85 | 0 | 0 |
| m26 | base + 3.0 x top-8 singular directions per matrix of (RL-Math 3.1 - base) (wsp_edit --recipe top8 --scale 3.0, stochastic rounding, seed 0) | cue | hard328 | 164: hard328 shard 0/2 (problems 0, 2, ..., 326) |  | 80 | 0 | 0 |
| m27 | Olmo-3.1-7B-RL-Zero-Math (run_cell --model rl) | plain | hard328 | 164: hard328 shard 0/2 (problems 0, 2, ..., 326) |  | 115 | 0 | 0 |
| m28 | Think-SFT + 1.5 x (RL-Math 3.1 - base) (delta_sum --host think_sft --donor rl_math --alpha 1.5) | cue | hard328 | 164 generated: hard328 shard 0/2; scored on the named subset: those of the 164 whose stored Think-SFT + cue sample 0 at seed 3000000 (results/thinkvote/hard328_sft1_cue_s4-01, attempt 0, sample 0; 89 cap hits on all 328) is a cap hit, about 45 problems |  | 95 | 0 | 0 |
| m30 | allenai/Olmo-3-7B-Think-SFT as released (wsp_edit --recipe interp --other think_sft --alpha 1.0 --rounding nearest) | cue | hard328 | 110: hard328 shard 0/3 (problems 0, 3, 6, ..., 327) |  | 95 | 0 | 0 |
| m31 | Olmo-3.1-7B-RL-Zero-Code = base + 1.0 x (Code-RL 3.1 - base), nearest rounding (merge_weights --other code --alpha 1.0) | plain | hard328 | 164: hard328 shard 0/2 (problems 0, 2, ..., 326) |  | 70 | 0 | 0 |
| m32 | base Olmo-3-1025-7B + 2.0 x the top 8 singular directions per matrix of (RL-Math 3.1 - base), stochastic bf16 rounding, seed 0 (wsp_edit recipe top8) | cue | fresh2026 (136 competition problems published in 2026) | 136, all problems |  | 85 | 0 | 0 |
| m33 | base + 0.25 x (RL-Math 3.1 - base) merged with NEAREST bf16 rounding (merge_weights --rounding nearest; the stored theta0.25 cells used stochastic rounding) | plain | MATH-500 | 200, the first 200 problems (--n 200) |  | 50 | 0 | 0 |
| m34 | base + 1.0 x the top 8 singular directions per matrix of (RL-Math 3.1 - base), stochastic rounding, seed 0 (wsp_edit recipe top8) | plain | hard328 | 164, shard 0/2 of hard328 (problems 0, 2, 4, ...) |  | 85 | 0 | 0 |
| m35 | untrained base Olmo-3-1025-7B | cue | hard328 | 164, shard 0/2 of hard328 (problems 0, 2, 4, ...); readout on the subset of these with 0 right among attempt 0 of the 4 stored samples of hard328_base_cue_s4r2-01 (result-5c961a), about 61 problems | yes | 78 | 0 | 0 |
| m36 | untrained base Olmo-3-1025-7B (no edit) | cue + the same 3 Math-RL-written solved examples in context as draw 1 of result-6d422d / result-5227b9 (the draw that gave 432/494), passed with run_cell --shots | MATH-500 | 497 generated (the 3 example problems left out); readout on the 494 problems that are no arm's example (as in result-5227b9) | yes | 105 | 0 | 0 |
| m37 | base + 1.5 x top 8 singular directions per matrix of (RL-Math 3.1 - base), MLP matrices only (gate, up, down), stochastic BF16 rounding, seed 0 | cue | MATH-500 | 500 (all) |  | 100 | 0 | 0 |
| m38 | Olmo-3.1-7B-RL-Zero-Math (final, step 2,800) | plain | fresh2026 | 136 (all) |  | 85 | 0 | 0 |
| m39 | RL-Math 3.1 minus its top 8 singular directions per matrix (wsp_edit recipe bulk; 190/328 right, 90 cap hits at 16,384 in result-284db5) | cue | hard328 | 47: shard 0/7 (indices 0, 7, 14, ..., 322) |  | 108 | 0 | 0 |

## List A: top 10 by separation per GPU minute

### m11: base - 1.0 x top-8 singular directions per matrix of (RL-Math 3.1 - base) (wsp_edit recipe top8, scale -1, stochastic rounding); cue; math500, n 500 (all)

GPU minutes 105 (proposers' guess). Separation 10 pairs, 0.0952 per minute. Job `run_cell.py`.

Cell: {"model": "base - 1.0 x top-8 singular directions per matrix of (RL-Math 3.1 - base) (wsp_edit recipe top8, scale -1, stochastic rounding)", "prompt": "cue", "set": "math500", "n": "500 (all)", "sampling": "T 1.0 / top-p 1.0 / min-p 0, seed 41000000 + problem index (the seeds of the stored cued-base T1 cell, 27 cap hits)", "samples": "1 per problem, 0 restarts", "grader": "v3", "cap": "16,384 generated tokens"}

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe top8 --other rl_math --scale -1.0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label top8x-1_math31 --prompt cue --set math500 --temperature 1.0 --top-p 1.0 --seed 41000000 --commit $(git rev-parse HEAD)`


#### m11-r1: cap hits among the 500 MATH-500 answers (metrics.json cap_hits) (cap hits of 500)

- proposed by run-05/f2-m01 (c11): 40 [30, 52]; says round-09/stopping-m03 gives 15 (its blind forecast: 16). f2-m01 makes the 8 directions a signed dial, so at size -1 MATH-500 cap hits rise above the cued base's 27 (hard328 went 77 -> 96, and negative size lengthens answers). stopping-m03 says stopping follows the root of the summed squared singular values an edit adds, which does not depend on sign, so -1 acts like +1 and cuts cap hits by about the same factor as +1 did on hard328 (0.6x): about 15.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 42 | [28, 60] | round-09/stopping-m03 |
| reader-2 | reader-2 | 40 | [28, 55] | round-09/stopping-m03 |
| run-06/f2-m03 | training | 40 | [30, 54] | round-09/stopping-m03 |
| round-09/training-m05 | training | 40 | [30, 54] | round-09/stopping-m03 |
| run-05/f2-m01 | weights | 40 | [29, 53] | round-09/stopping-m03 |
| round-09/weights-m01 | weights | 38 | [27, 50] | round-09/stopping-m03 |
| round-09/weights-m02 | weights | 37 | [27, 49] | round-09/stopping-m03 |
| round-09/weights-m06 | weights | 38 | [27, 50] | round-09/stopping-m03 |
| run-07/f2-m02 | problems | 42 | [28, 58] | round-09/stopping-m03 |
| round-09/problems-m06 | problems | 40 | [27, 55] | round-09/stopping-m03 |
| run-03/f2-m02 | stopping | 36 | [26, 48] |  |
| round-09/stopping-m02 | stopping | 36 | [26, 48] |  |
| round-09/stopping-m03 | stopping | 16 | [8, 26] | reader-1, reader-2, run-06/f2-m03, round-09/training-m05, run-05/f2-m01, round-09/weights-m01, round-09/weights-m02, round-09/weights-m06, run-07/f2-m02, round-09/problems-m06 |
| run-04/f2-m03 | sampling | 38 | [26, 52] |  |
| round-09/grader-m03 | grader | 36 | [25, 49] |  |

Theory says nothing: round-09/training-m01, round-09/training-m02, round-09/training-m03, round-09/training-m04, round-09/training-m06, run-02/f2-m01, run-02/f2-m04, run-05/f2-m03, run-05/f2-m06, round-09/weights-m03, round-09/weights-m04, round-09/weights-m05, round-09/problems-m01, round-09/problems-m02, round-09/problems-m03, round-09/problems-m04, round-09/problems-m05, run-03/f2-m05, round-09/stopping-m01, round-09/stopping-m04, round-09/stopping-m05, round-09/stopping-m06, round-09/sampling-m01, round-09/sampling-m02, round-09/sampling-m03, round-09/sampling-m04, round-09/sampling-m05, round-09/sampling-m06, round-09/grader-m01, round-09/grader-m02, round-09/grader-m04, round-09/grader-m05, round-09/grader-m06.


### m13: base + 2.0 x top-64 singular directions per matrix of (RL-Math 3.1 - base) (wsp_edit recipe top8 with --k 64, scale 2, stochastic rounding); cue; hard328, n 164: shard 0/2 (problems 0, 2, ..., 326)

GPU minutes 80 (proposers' guess). Separation 7 pairs, 0.0875 per minute. Job `run_cell.py`.

Cell: {"model": "base + 2.0 x top-64 singular directions per matrix of (RL-Math 3.1 - base) (wsp_edit recipe top8 with --k 64, scale 2, stochastic rounding)", "prompt": "cue", "set": "hard328", "n": "164: shard 0/2 (problems 0, 2, ..., 326)", "sampling": "T 1.0 / top-p 1.0 / min-p 0, seed 3000000 + problem index", "samples": "1 per problem, 0 restarts", "grader": "v3", "cap": "16,384 generated tokens"}

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe top8 --other rl_math --k 64 --scale 2.0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label top64x2_math31 --prompt cue --set hard328 --temperature 1.0 --top-p 1.0 --seed 3000000 --shard 0/2 --commit $(git rev-parse HEAD)`


#### m13-r1: right answers of the 164 shard-0/2 problems, grader v3 (right answers of 164)

- proposed by round-09/weights-m01 (c13): 93 [84, 103]; says round-09/stopping-m03 gives 58 (its blind forecast: 58). weights-m01 ties both finishing and breakdown to the size of the top direction, so top-64 at 2x behaves like top-8 at 2x and top-1 at 2x (190 and 184 of 328): about 93 of 164, over-committing but not broken. stopping-m03 uses total top-subspace energy: top-64 at 1x is 0.115 % of the weight norm against 0.074 % for top-8, so 2x is like top-8 at ~3.1x. That is past its degeneration level, like top-8 at 3x (117/328): about 58.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 90 | [72, 104] |  |
| reader-2 | reader-2 | 92 | [78, 104] |  |
| run-06/f2-m03 | training | 95 | [83, 106] | round-09/stopping-m03 |
| run-05/f2-m01 | weights | 94 | [84, 103] | round-09/stopping-m03 |
| round-09/weights-m01 | weights | 95 | [85, 104] | round-09/stopping-m03 |
| round-09/weights-m02 | weights | 100 | [91, 108] | round-09/stopping-m03 |
| round-09/weights-m06 | weights | 96 | [86, 105] | round-09/stopping-m03 |
| round-09/problems-m02 | problems | 92 | [78, 105] |  |
| round-09/problems-m05 | problems | 95 | [82, 106] | round-09/stopping-m03 |
| round-09/problems-m06 | problems | 88 | [74, 102] |  |
| run-03/f2-m02 | stopping | 90 | [78, 101] |  |
| run-03/f2-m05 | stopping | 70 | [45, 92] |  |
| round-09/stopping-m02 | stopping | 96 | [84, 106] |  |
| round-09/stopping-m03 | stopping | 58 | [40, 80] | run-06/f2-m03, run-05/f2-m01, round-09/weights-m01, round-09/weights-m02, round-09/weights-m06, round-09/problems-m05, round-09/grader-m03 |
| run-04/f2-m03 | sampling | 90 | [74, 104] |  |
| round-09/sampling-m04 | sampling | 84 | [60, 102] |  |
| round-09/grader-m03 | grader | 97 | [82, 108] | round-09/stopping-m03 |

Theory says nothing: round-09/training-m01, round-09/training-m02, round-09/training-m03, round-09/training-m04, round-09/training-m05, round-09/training-m06, run-02/f2-m01, run-02/f2-m04, run-05/f2-m03, run-05/f2-m06, round-09/weights-m03, round-09/weights-m04, round-09/weights-m05, run-07/f2-m02, round-09/problems-m01, round-09/problems-m03, round-09/problems-m04, round-09/stopping-m01, round-09/stopping-m04, round-09/stopping-m05, round-09/stopping-m06, round-09/sampling-m01, round-09/sampling-m02, round-09/sampling-m03, round-09/sampling-m05, round-09/sampling-m06, round-09/grader-m01, round-09/grader-m02, round-09/grader-m04, round-09/grader-m05, round-09/grader-m06.


### m21: base Olmo-3-1025-7B + 1.0 x the top 8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Code - base), stochastic bf16 rounding seed 0; plain; MATH-500, n first 250 problems (--n 250)

GPU minutes 55 (proposers' guess). Separation 3 pairs, 0.0545 per minute. Job `run_cell.py`.

Cell: {"model": "base Olmo-3-1025-7B + 1.0 x the top 8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Code - base), stochastic bf16 rounding seed 0", "prompt": "plain", "set": "MATH-500", "n": "first 250 problems (--n 250)", "sampling": "T 1.0 / top-p 1.0 / min-p 0; seed 64000000 + problem index", "samples": "1 per problem, 0 restarts", "grader": "v3", "cap": "16,384"}

Command: `uv run tools/gpu.py submit h100 --hours 1.5 -- "bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe top8 --other rl_code --scale 1.0 --rounding stochastic --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label top8x1_code31_plain --prompt plain --set math500 --n 250 --temperature 1.0 --top-p 1.0 --seed 64000000 --commit $(git rev-parse HEAD)"`


#### m21-r1: quick wrong answers: rows with n_generated <= 1,000, not a cap hit, and v3 score not 1 (no extracted answer counts wrong), from answers.jsonl (answers of 250)

- proposed by round-09/problems-m03 (c22): 11 [5, 19]; says run-05/f2-m03 gives 41 (its blind forecast: 40). m03 says any edit that installs the deliberative register (Code-RL's late directions also read Okay/Wait) lengthens the terse short answers on easy problems, leaving short wrong answers near the Math top-8 plain level (about 15 per 500, so about 8 per 250, plus a little for a weaker install). The input-overlap rival gives a cross-domain edit about half the in-domain effect, so the short-wrong count lands halfway between plain base (about 75 per 250) and Math top-8 (8): about 41.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 25 | [10, 45] |  |
| reader-2 | reader-2 | 18 | [8, 32] |  |
| run-06/f2-m03 | training | 25 | [10, 45] |  |
| run-05/f2-m03 | weights | 40 | [24, 58] | run-03/f2-m02 |
| run-05/f2-m06 | weights | 45 | [28, 64] | run-03/f2-m02, round-09/stopping-m06 |
| run-07/f2-m02 | problems | 27 | [14, 40] |  |
| round-09/problems-m03 | problems | 20 | [10, 32] |  |
| run-03/f2-m02 | stopping | 14 | [7, 23] | run-05/f2-m03, run-05/f2-m06 |
| round-09/stopping-m06 | stopping | 15 | [8, 24] | run-05/f2-m06 |
| run-04/f2-m03 | sampling | 18 | [7, 32] |  |
| round-09/sampling-m03 | sampling | 20 | [8, 35] |  |

Theory says nothing: round-09/training-m01, round-09/training-m02, round-09/training-m03, round-09/training-m04, round-09/training-m05, round-09/training-m06, run-02/f2-m01, run-02/f2-m04, run-05/f2-m01, round-09/weights-m01, round-09/weights-m02, round-09/weights-m03, round-09/weights-m04, round-09/weights-m05, round-09/weights-m06, round-09/problems-m01, round-09/problems-m02, round-09/problems-m04, round-09/problems-m05, round-09/problems-m06, run-03/f2-m05, round-09/stopping-m01, round-09/stopping-m02, round-09/stopping-m03, round-09/stopping-m04, round-09/stopping-m05, round-09/sampling-m01, round-09/sampling-m02, round-09/sampling-m04, round-09/sampling-m05, round-09/sampling-m06, round-09/grader-m01, round-09/grader-m02, round-09/grader-m03, round-09/grader-m04, round-09/grader-m05, round-09/grader-m06.


### m05: untrained base Olmo-3-1025-7B; plain (no cue); math500, n 100: the first 100 problems (--n 100) (base only)

GPU minutes 90 (proposers' guess). Separation 3 pairs, 0.0333 per minute. Job `run_cell.py`.

Cell: {"model": "untrained base Olmo-3-1025-7B", "prompt": "plain (no cue)", "set": "math500", "n": "100: the first 100 problems (--n 100)", "sampling": "T 1.0 / top-p 1.0 / min-p 0, seed 41000000 + problem index, sample offsets as run_cell --samples assigns", "samples": "8 per problem, no restarts; plurality vote over the 8 (rln4_lib.agree grouping, ties to the lowest sample)", "grader": "v3 on the voted answer", "cap": "16,384 generated tokens"}

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt plain --set math500 --temperature 1.0 --top-p 1.0 --seed 41000000 --n 100 --samples 8 --commit $(git rev-parse HEAD)`


#### m05-r1: right answers of the plurality vote over 8 samples, grader v3 (right answers of 100)

Best known base count given to the forecasters: 90 (result-5d032f; No base-only cell has 8 samples on these problems; nearest is the cued base vote over 4 after restart, 450 of 500 (result-5d032f, audited as the honest best in result-e78dfe), scaled to 100 problems: 90. That is 4 samples, not 8, and all 500 problems, not the first 100.). Highest forecast: round-09/problems-m03 72 (-18).

- proposed by round-09/training-m04 (c05): 80 [72, 88]; says round-09/stopping-m06 gives 45 (its blind forecast: 62). training-m04 says the cue picks the register but does not move each problem's modal value, so a vote over enough plain samples converges to the same mode as the cued vote (about 89 of these 100). At k = 8 it reaches about 80. stopping-m06 says terse plain samples end right after their first result and are wrong on any problem that needs a longer derivation. Their vote is capped near the problems plain usually gets right, about 45 (plain single is 34 here).

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 62 | [48, 76] |  |
| reader-2 | reader-2 | 62 | [48, 75] |  |
| round-09/training-m04 | training | 52 | [38, 66] |  |
| run-02/f2-m01 | run-02 | 60 | [47, 72] |  |
| round-09/problems-m01 | problems | 70 | [56, 82] | round-09/stopping-m01 |
| round-09/problems-m03 | problems | 72 | [58, 84] | round-09/stopping-m01 |
| round-09/stopping-m01 | stopping | 42 | [32, 52] | round-09/problems-m01, round-09/problems-m03, round-09/sampling-m02 |
| round-09/stopping-m06 | stopping | 62 | [50, 74] |  |
| round-09/sampling-m02 | sampling | 66 | [54, 76] | round-09/stopping-m01 |
| round-09/sampling-m06 | sampling | 58 | [46, 69] |  |
| round-09/grader-m02 | grader | 56 | [44, 67] |  |
| round-09/grader-m05 | grader | 54 | [42, 65] |  |

Theory says nothing: run-06/f2-m03, round-09/training-m01, round-09/training-m02, round-09/training-m03, round-09/training-m05, round-09/training-m06, run-02/f2-m04, run-05/f2-m03, run-05/f2-m01, run-05/f2-m06, round-09/weights-m01, round-09/weights-m02, round-09/weights-m03, round-09/weights-m04, round-09/weights-m05, round-09/weights-m06, run-07/f2-m02, round-09/problems-m02, round-09/problems-m04, round-09/problems-m05, round-09/problems-m06, run-03/f2-m02, run-03/f2-m05, round-09/stopping-m02, round-09/stopping-m03, round-09/stopping-m04, round-09/stopping-m05, run-04/f2-m03, round-09/sampling-m01, round-09/sampling-m03, round-09/sampling-m04, round-09/sampling-m05, round-09/grader-m01, round-09/grader-m03, round-09/grader-m04, round-09/grader-m06.


### m18: base + 0.125 x (RL-Math 3.1 - base), whole difference, stochastic bf16 rounding (merge_weights --alpha 0.125 --rounding stochastic); plain; math500, n 500 (all)

GPU minutes 90 (proposers' guess). Separation 2 pairs, 0.0222 per minute. Job `run_cell.py`.

Cell: {"model": "base + 0.125 x (RL-Math 3.1 - base), whole difference, stochastic bf16 rounding (merge_weights --alpha 0.125 --rounding stochastic)", "prompt": "plain", "set": "math500", "n": "500 (all)", "sampling": "T 1.0 / top-p 1.0 / min-p 0, seed 61000000 + problem index", "samples": "1 per problem, 0 restarts", "grader": "v3", "cap": "16,384 generated tokens"}

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.merge_weights --other rl --alpha 0.125 --rounding stochastic --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label theta0.125 --prompt plain --set math500 --temperature 1.0 --top-p 1.0 --seed 61000000 --commit $(git rev-parse HEAD)`


#### m18-r1: right answers of 500, grader v3 (right answers of 500)

- proposed by round-09/weights-m06 (c18): 345 [328, 362]; says run-05/f2-m06 gives 316 (its blind forecast: 300). weights-m06: stochastic rounding is unbiased, so a = 0.125 gets the nominal dose. On the fitted plain curve 224 + 239(1 - exp(-a/0.177)) that is about 345. f2-m06 thresholds small entries, so 0.125 acts like ~0.04 on the effective-size curve fitted through 0.25 -> 0.12: about 316.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 355 | [315, 392] |  |
| reader-2 | reader-2 | 362 | [320, 400] |  |
| run-05/f2-m06 | weights | 300 | [260, 340] | round-09/problems-m03 |
| round-09/weights-m06 | weights | 365 | [330, 400] |  |
| round-09/problems-m03 | problems | 395 | [365, 420] | run-05/f2-m06, round-09/sampling-m03 |
| run-03/f2-m02 | stopping | 330 | [280, 375] |  |
| round-09/stopping-m06 | stopping | 345 | [295, 390] |  |
| round-09/sampling-m03 | sampling | 308 | [272, 342] | round-09/problems-m03 |

Theory says nothing: run-06/f2-m03, round-09/training-m01, round-09/training-m02, round-09/training-m03, round-09/training-m04, round-09/training-m05, round-09/training-m06, run-02/f2-m01, run-02/f2-m04, run-05/f2-m03, run-05/f2-m01, round-09/weights-m01, round-09/weights-m02, round-09/weights-m03, round-09/weights-m04, round-09/weights-m05, run-07/f2-m02, round-09/problems-m01, round-09/problems-m02, round-09/problems-m04, round-09/problems-m05, round-09/problems-m06, run-03/f2-m05, round-09/stopping-m01, round-09/stopping-m02, round-09/stopping-m03, round-09/stopping-m04, round-09/stopping-m05, run-04/f2-m03, round-09/sampling-m01, round-09/sampling-m02, round-09/sampling-m04, round-09/sampling-m05, round-09/sampling-m06, round-09/grader-m01, round-09/grader-m02, round-09/grader-m03, round-09/grader-m04, round-09/grader-m05, round-09/grader-m06.


### m14: base + 3.0 x top-8 singular directions per matrix of (RL-Math 3.1 - base), MLP matrices only (wsp_edit recipe top8, --mods mlp, scale 3, stochastic rounding); cue; hard328, n 164: shard 0/2

GPU minutes 75 (proposers' guess). Separation 1 pairs, 0.0133 per minute. Job `run_cell.py`.

Cell: {"model": "base + 3.0 x top-8 singular directions per matrix of (RL-Math 3.1 - base), MLP matrices only (wsp_edit recipe top8, --mods mlp, scale 3, stochastic rounding)", "prompt": "cue", "set": "hard328", "n": "164: shard 0/2", "sampling": "T 1.0 / top-p 1.0 / min-p 0, seed 3000000 + problem index", "samples": "1 per problem, 0 restarts", "grader": "v3", "cap": "16,384 generated tokens"}

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe top8 --other rl_math --mods mlp --scale 3.0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label top8x3_mlp_math31 --prompt cue --set hard328 --temperature 1.0 --top-p 1.0 --seed 3000000 --shard 0/2 --commit $(git rev-parse HEAD)`


#### m14-r1: right answers of the 164 shard-0/2 problems, grader v3 (right answers of 164)

- proposed by round-09/weights-m02 (c14): 97 [88, 107]; says round-09/weights-m01 gives 70 (its blind forecast: 62). weights-m02 treats a part as the whole scaled by its share. MLP-only at 1x (181) sits like the whole edit at ~0.6x, so MLP-only at 3x acts like the whole at ~1.8x, between 200.25 (1.5x) and 190 (2x) of 328: about 97 here. weights-m01 says the top direction of each matrix at 3x breaks generation whatever else is added, so this cell decays like top-1 3x (168, 67 unboxed) or top-8 3x (117): about 70.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 80 | [55, 100] |  |
| reader-2 | reader-2 | 85 | [65, 100] |  |
| run-06/f2-m03 | training | 82 | [62, 100] |  |
| run-05/f2-m01 | weights | 85 | [68, 100] |  |
| round-09/weights-m01 | weights | 62 | [42, 82] |  |
| round-09/weights-m02 | weights | 97 | [87, 106] | run-03/f2-m05 |
| round-09/problems-m06 | problems | 80 | [62, 98] |  |
| run-03/f2-m02 | stopping | 85 | [70, 98] |  |
| run-03/f2-m05 | stopping | 65 | [45, 85] | round-09/weights-m02 |
| round-09/stopping-m02 | stopping | 92 | [80, 102] |  |
| round-09/stopping-m03 | stopping | 90 | [78, 100] |  |
| run-04/f2-m03 | sampling | 92 | [78, 104] |  |
| round-09/sampling-m04 | sampling | 92 | [76, 105] |  |
| round-09/grader-m03 | grader | 90 | [76, 102] |  |

Theory says nothing: round-09/training-m01, round-09/training-m02, round-09/training-m03, round-09/training-m04, round-09/training-m05, round-09/training-m06, run-02/f2-m01, run-02/f2-m04, run-05/f2-m03, run-05/f2-m06, round-09/weights-m03, round-09/weights-m04, round-09/weights-m05, round-09/weights-m06, run-07/f2-m02, round-09/problems-m01, round-09/problems-m02, round-09/problems-m03, round-09/problems-m04, round-09/problems-m05, round-09/stopping-m01, round-09/stopping-m04, round-09/stopping-m05, round-09/stopping-m06, round-09/sampling-m01, round-09/sampling-m02, round-09/sampling-m03, round-09/sampling-m05, round-09/sampling-m06, round-09/grader-m01, round-09/grader-m02, round-09/grader-m04, round-09/grader-m05, round-09/grader-m06.


### m06: RL-Math 3.1 minus its top-1 singular direction per matrix (wsp_edit recipe bulk with --k 1: RL - top-1 component of (RL - base)), stochastic rounding; cue; hard328, n 164: even-index problems 0, 2, ..., 326 (--shard 0/2)

GPU minutes 85 (proposers' guess). Separation 1 pairs, 0.0118 per minute. Job `run_cell.py`.

Cell: {"model": "RL-Math 3.1 minus its top-1 singular direction per matrix (wsp_edit recipe bulk with --k 1: RL - top-1 component of (RL - base)), stochastic rounding", "prompt": "cue", "set": "hard328", "n": "164: even-index problems 0, 2, ..., 326 (--shard 0/2)", "sampling": "T 1.0 / top-p 1.0 / min-p 0, seed 3000000 + problem index", "samples": "1 per problem, no restarts", "grader": "v3", "cap": "16,384 generated tokens"}

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe bulk --other rl_math --k 1 --scale 1.0 --rounding stochastic --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label rl_minus_top1 --prompt cue --set hard328 --temperature 1.0 --top-p 1.0 --seed 3000000 --shard 0/2 --commit $(git rev-parse HEAD)`


#### m06-r1: cap hits (finish reason length at 16,384 tokens) (cap hits of 164)

- proposed by round-09/training-m05 (c06): 15 [8, 23]; says round-09/weights-m01 gives 40 (its blind forecast: 30). training-m05 puts the boxed-answer form in the top direction and the stopping decision in the next seven, so removing only the top direction leaves RL's stopping. Cap hits stay near RL's (about 20 of 328, plus perturbation, like RL minus random rank-8 at 33), about 15 here. weights-m01 puts the commit-and-stop readout mainly in the top direction, so removing it behaves like removing all eight (90 of 328): about 40 here.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 32 | [18, 48] |  |
| reader-2 | reader-2 | 27 | [15, 40] |  |
| round-09/training-m05 | training | 20 | [12, 30] |  |
| run-05/f2-m01 | weights | 20 | [12, 28] |  |
| round-09/weights-m01 | weights | 30 | [19, 41] |  |
| round-09/weights-m02 | weights | 22 | [14, 31] |  |
| run-07/f2-m02 | problems | 32 | [18, 46] |  |
| run-03/f2-m02 | stopping | 30 | [20, 40] |  |
| round-09/stopping-m02 | stopping | 28 | [18, 38] |  |
| round-09/stopping-m03 | stopping | 13 | [7, 20] | run-04/f2-m03 |
| run-04/f2-m03 | sampling | 38 | [24, 52] | round-09/stopping-m03 |
| round-09/grader-m03 | grader | 21 | [12, 33] |  |

Theory says nothing: run-06/f2-m03, round-09/training-m01, round-09/training-m02, round-09/training-m03, round-09/training-m04, round-09/training-m06, run-02/f2-m01, run-02/f2-m04, run-05/f2-m03, run-05/f2-m06, round-09/weights-m03, round-09/weights-m04, round-09/weights-m05, round-09/weights-m06, round-09/problems-m01, round-09/problems-m02, round-09/problems-m03, round-09/problems-m04, round-09/problems-m05, round-09/problems-m06, run-03/f2-m05, round-09/stopping-m01, round-09/stopping-m04, round-09/stopping-m05, round-09/stopping-m06, round-09/sampling-m01, round-09/sampling-m02, round-09/sampling-m03, round-09/sampling-m04, round-09/sampling-m05, round-09/sampling-m06, round-09/grader-m01, round-09/grader-m02, round-09/grader-m04, round-09/grader-m05, round-09/grader-m06.


### m29: base + 4.0 x top-1 singular direction per matrix of (RL-Math 3.1 - base) (wsp_edit --recipe top8 --k 1 --scale 4.0, stochastic rounding, seed 0); cue; hard328, n 164: hard328 shard 0/2 (problems 0, 2, ..., 326)

GPU minutes 90 (proposers' guess). Separation 1 pairs, 0.0111 per minute. Job `run_cell.py`.

Cell: {"model": "base + 4.0 x top-1 singular direction per matrix of (RL-Math 3.1 - base) (wsp_edit --recipe top8 --k 1 --scale 4.0, stochastic rounding, seed 0)", "prompt": "cue", "set": "hard328", "n": "164: hard328 shard 0/2 (problems 0, 2, ..., 326)", "sampling": "T 1.0 / top-p 1.0 / min-p 0, seed 3000000 + problem index", "samples": "1 per problem, no restarts", "grader": "v3", "cap": "16,384"}

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe top8 --other rl_math --k 1 --scale 4.0 --rounding stochastic --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label top1x4 --prompt cue --set hard328 --temperature 1.0 --top-p 1.0 --seed 3000000 --shard 0/2 --commit $(git rev-parse HEAD)`


#### m29-r1: right answers with grader v3 among the 164 shard-0/2 problems (cap hits count wrong) (right answers of 164)

- proposed by round-09/stopping-m03 (c30): 88 [76, 100]; says round-09/weights-m01 gives 50 (its blind forecast: 55). In m03 only the added energy counts: one direction at s acts like eight at about 0.53 s, so top-1 at 4x is top-8 near 2.1x (190/328, 5 cap hits). That is still below the degeneration level, which sits near the top-8 3x energy. Shading this for the measured top-1 3x shortfall (168 against about 200) gives about 88 of 164. weights-m01 makes breakdown depend on the size of the top direction itself, which breaks near 3x however many directions are added. At 4x the model decays into word strings, at or below the top-8 3x cell (117/328, about 58 per half).
- proposed by round-09/sampling-m04 (c38): 75 [65, 85]; says round-09/weights-m01 gives 56 (its blind forecast: 55). sampling-m04 puts the breakdown threshold on the edit's total logit shift: one direction at 1x acts like eight at 0.5x (51 vs 50 cap hits), so top-1 at 4x carries about the shift of top-8 at 2x (190 right, coherent), below top-8 at 3x (117, word strings); it continues the top-1 trend 181, 184, 168 at 1x-3x to about 150/328, 75 of 164. weights-m01 says about 3x on the top direction breaks generation whether 1 or 8 directions are scaled, so 4x is past breakdown, like top-8 at 3x: about 113/328, 56 of 164.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 70 | [50, 88] |  |
| reader-2 | reader-2 | 75 | [55, 92] |  |
| round-09/training-m05 | training | 70 | [55, 85] |  |
| run-05/f2-m01 | weights | 70 | [50, 90] |  |
| round-09/weights-m01 | weights | 55 | [33, 77] | round-09/stopping-m03 |
| round-09/weights-m02 | weights | 95 | [84, 105] |  |
| round-09/weights-m06 | weights | 65 | [45, 85] |  |
| round-09/problems-m06 | problems | 70 | [55, 85] |  |
| run-03/f2-m02 | stopping | 85 | [70, 98] |  |
| run-03/f2-m05 | stopping | 65 | [45, 85] |  |
| round-09/stopping-m02 | stopping | 88 | [75, 100] |  |
| round-09/stopping-m03 | stopping | 93 | [80, 104] | round-09/weights-m01 |
| run-04/f2-m03 | sampling | 75 | [60, 90] |  |
| round-09/sampling-m04 | sampling | 72 | [55, 88] |  |
| round-09/grader-m03 | grader | 80 | [62, 94] |  |

Theory says nothing: run-06/f2-m03, round-09/training-m01, round-09/training-m02, round-09/training-m03, round-09/training-m04, round-09/training-m06, run-02/f2-m01, run-02/f2-m04, run-05/f2-m03, run-05/f2-m06, round-09/weights-m03, round-09/weights-m04, round-09/weights-m05, run-07/f2-m02, round-09/problems-m01, round-09/problems-m02, round-09/problems-m03, round-09/problems-m04, round-09/problems-m05, round-09/stopping-m01, round-09/stopping-m04, round-09/stopping-m05, round-09/stopping-m06, round-09/sampling-m01, round-09/sampling-m02, round-09/sampling-m03, round-09/sampling-m05, round-09/sampling-m06, round-09/grader-m01, round-09/grader-m02, round-09/grader-m04, round-09/grader-m05, round-09/grader-m06.


### m01: base + 1.5 x top-8 singular directions per matrix of (RL-Code 3.1 - base), all layers, stochastic rounding (wsp_edit recipe top8, --other rl_code); cue; math500, n 250: even-index problems 0, 2, ..., 498 (--shard 0/2)

GPU minutes 65 (proposers' guess). Separation 0 pairs, 0 per minute. Job `run_cell.py`.

Cell: {"model": "base + 1.5 x top-8 singular directions per matrix of (RL-Code 3.1 - base), all layers, stochastic rounding (wsp_edit recipe top8, --other rl_code)", "prompt": "cue", "set": "math500", "n": "250: even-index problems 0, 2, ..., 498 (--shard 0/2)", "sampling": "T 1.0 / top-p 1.0 / min-p 0, seed 41000000 + problem index (the seeds of the stored cued-base cell T1)", "samples": "1 per problem, no restarts", "grader": "v3", "cap": "16,384 generated tokens"}

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe top8 --other rl_code --scale 1.5 --rounding stochastic --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label code_top8x1.5 --prompt cue --set math500 --temperature 1.0 --top-p 1.0 --seed 41000000 --shard 0/2 --commit $(git rev-parse HEAD)`


#### m01-r1: right answers with grader v3 among the 250 problems (cap hits count wrong) (right answers of 250)

- proposed by run-06/f2-m03 (c01): 218 [211, 225]; says round-09/problems-m02 gives 206 (its blind forecast: nothing). f2-m03 says another reward's top-8 directions give about half of the in-domain gain: cued base about 205 of these 250, Math top-8 at 1.5x about 228 and RL about 231, so the cell lands near 218. problems-m02 says finishing directions help only where cut text is unfinished sound work, and the base's cut answers are stalled (4 of 64 right). The base has only about 13 cap hits here, so it predicts about one extra right answer, 206.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 220 | [208, 231] |  |
| reader-2 | reader-2 | 221 | [210, 231] |  |
| run-06/f2-m03 | training | 217 | [207, 227] |  |
| run-05/f2-m03 | weights | 216 | [206, 226] |  |
| run-05/f2-m01 | weights | 219 | [209, 229] |  |
| run-05/f2-m06 | weights | 216 | [205, 227] |  |
| round-09/weights-m01 | weights | 219 | [209, 228] |  |
| round-09/weights-m02 | weights | 218 | [208, 228] |  |
| round-09/weights-m06 | weights | 218 | [208, 228] |  |
| run-07/f2-m02 | problems | 216 | [206, 226] |  |
| run-03/f2-m02 | stopping | 214 | [203, 225] |  |
| run-04/f2-m03 | sampling | 214 | [204, 224] |  |
| round-09/sampling-m04 | sampling | 220 | [209, 230] |  |
| round-09/grader-m03 | grader | 221 | [211, 230] |  |

Theory says nothing: round-09/training-m01, round-09/training-m02, round-09/training-m03, round-09/training-m04, round-09/training-m05, round-09/training-m06, run-02/f2-m01, run-02/f2-m04, round-09/weights-m03, round-09/weights-m04, round-09/weights-m05, round-09/problems-m01, round-09/problems-m02, round-09/problems-m03, round-09/problems-m04, round-09/problems-m05, round-09/problems-m06, run-03/f2-m05, round-09/stopping-m01, round-09/stopping-m02, round-09/stopping-m03, round-09/stopping-m04, round-09/stopping-m05, round-09/stopping-m06, round-09/sampling-m01, round-09/sampling-m02, round-09/sampling-m03, round-09/sampling-m05, round-09/sampling-m06, round-09/grader-m01, round-09/grader-m02, round-09/grader-m04, round-09/grader-m05, round-09/grader-m06.


### m02: allenai/Olmo-3-7B-Think-SFT, written as base + 1.0 x (Think-SFT - base) with nearest rounding (wsp_edit recipe interp, as in the relay jobs); cue (the base's raw prompt asking for the answer on its own line after 'Answer:', plus the 3-token opening cue); not Think-SFT's ChatML template; math500, n 400: the first 400 problems (--n 400)

GPU minutes 105 (proposers' guess). Separation 0 pairs, 0 per minute. Job `run_cell.py`.

Cell: {"model": "allenai/Olmo-3-7B-Think-SFT, written as base + 1.0 x (Think-SFT - base) with nearest rounding (wsp_edit recipe interp, as in the relay jobs)", "prompt": "cue (the base's raw prompt asking for the answer on its own line after 'Answer:', plus the 3-token opening cue); not Think-SFT's ChatML template", "set": "math500", "n": "400: the first 400 problems (--n 400)", "sampling": "T 0.6 / top-p 0.95 / min-p 0, seed 1000000 + problem index", "samples": "1 per problem, no restarts", "grader": "v3 (rows also carry v1 and v2)", "cap": "16,384 generated tokens"}

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe interp --other think_sft --alpha 1.0 --rounding nearest --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label think_sft --prompt cue --set math500 --temperature 0.6 --top-p 0.95 --seed 1000000 --n 400 --commit $(git rev-parse HEAD)`


#### m02-r1: finished answers (not cap hits) that v3 scores wrong and whose first non-empty line after the last 'Answer:' marker equals the gold answer under math-verify (the misplaced-answer form) (answers of 400)

- proposed by round-09/training-m01 (c02): 3 [1, 7]; says round-09/weights-m04 gives 0 (its blind forecast: nothing). training-m01 says Think-SFT's way of stating the answer depends on its own template, so on the raw prompt it sometimes puts the answer on the line after 'Answer:', where v3 misses it. That was 16 of 2,000 samples at T 1.0 (result-818c20), about 3 per 400 at any sampling setting. weights-m04 says prompt or template changes leave Think-SFT's precision unchanged, so its wrong finished answers are real errors and none is a misplaced right answer.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 3 | [0, 8] |  |
| reader-2 | reader-2 | 11 | [4, 20] |  |
| round-09/training-m01 | training | 4 | [1, 8] |  |

Theory says nothing: run-06/f2-m03, round-09/training-m02, round-09/training-m03, round-09/training-m04, round-09/training-m05, round-09/training-m06, run-02/f2-m01, run-02/f2-m04, run-05/f2-m03, run-05/f2-m01, run-05/f2-m06, round-09/weights-m01, round-09/weights-m02, round-09/weights-m03, round-09/weights-m04, round-09/weights-m05, round-09/weights-m06, run-07/f2-m02, round-09/problems-m01, round-09/problems-m02, round-09/problems-m03, round-09/problems-m04, round-09/problems-m05, round-09/problems-m06, run-03/f2-m02, run-03/f2-m05, round-09/stopping-m01, round-09/stopping-m02, round-09/stopping-m03, round-09/stopping-m04, round-09/stopping-m05, round-09/stopping-m06, run-04/f2-m03, round-09/sampling-m01, round-09/sampling-m02, round-09/sampling-m03, round-09/sampling-m04, round-09/sampling-m05, round-09/sampling-m06, round-09/grader-m01, round-09/grader-m02, round-09/grader-m03, round-09/grader-m04, round-09/grader-m05, round-09/grader-m06.


## List B: base-only cells, top 10 by the highest forecast of right answers minus the best known base count

### m35: untrained base Olmo-3-1025-7B; cue; hard328, n 164, shard 0/2 of hard328 (problems 0, 2, 4, ...); readout on the subset of these with 0 right among attempt 0 of the 4 stored samples of hard328_base_cue_s4r2-01 (result-5c961a), about 61 problems (base only)

GPU minutes 78 (proposers' guess). Separation 0 pairs, 0 per minute. Job `run_cell.py`.

Cell: {"model": "untrained base Olmo-3-1025-7B", "prompt": "cue", "set": "hard328", "n": "164, shard 0/2 of hard328 (problems 0, 2, 4, ...); readout on the subset of these with 0 right among attempt 0 of the 4 stored samples of hard328_base_cue_s4r2-01 (result-5c961a), about 61 problems", "sampling": "T 1.0 / top-p 1.0 / min-p 0; new seeds, problem i seeded 3700000 + i", "samples": "1 per problem, no restarts", "grader": "v3", "cap": "16,384 generated tokens"}

Command: `uv run tools/gpu.py submit h100 --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set hard328 --temperature 1.0 --top-p 1.0 --seed 3700000 --shard 0/2 --commit $(git rev-parse HEAD)"`


#### m35-r1: right answers with grader v3 among the shard's problems where the base's 4 stored attempt-0 samples (results/day1_3/hard328_base_cue_s4r2-01 rows) are all wrong (right answers of the about 61 stored 0-of-4 problems in the shard)

Best known base count given to the forecasters: 6 (result-82b4dc; No board count exists on this subset. The stored base samples of s4r2-01 score 0 on it by construction; 6 is an estimate for the other stored one-sample base cue cell (job e72c, 164/328) on these about 61 problems (block rate about 0.1). With restarts (more samples) the base reaches 44 of the 123 0-of-4 problems on the whole 328.). Highest forecast: reader-1 6 (+0).

- proposed by round-09/sampling-m06 (c40): 6 [2, 10]; says round-09/sampling-m01 gives 14 (its blind forecast: 5). On hard328 the base has 123 problems at 0 of 4 where a spread of p_i matching sampling-m01's count noise (Beta with mean 0.48, variance about 0.055) expects about 55. sampling-m06 reads the excess as a true near-zero block, so fresh samples there solve about (55 x 0.2 + 68 x 0.02)/123 = 0.10 per problem, 6 of 61. sampling-m01 treats each stored 0 as one draw of a fixed p_i; its implied spread gives E[p | 0 of 4] = 1.70/7.54 = 0.23, 14 of 61.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 6 | [2, 11] |  |
| reader-2 | reader-2 | 5 | [1, 10] |  |
| round-09/training-m04 | training | 5 | [2, 9] |  |
| round-09/problems-m01 | problems | 4 | [1, 9] |  |
| round-09/problems-m05 | problems | 4 | [0, 9] |  |
| round-09/stopping-m04 | stopping | 6 | [2, 11] |  |
| round-09/sampling-m01 | sampling | 5 | [1, 10] |  |
| round-09/sampling-m06 | sampling | 3 | [0, 7] |  |
| round-09/grader-m01 | grader | 6 | [2, 11] |  |

Theory says nothing: run-06/f2-m03, round-09/training-m01, round-09/training-m02, round-09/training-m03, round-09/training-m05, round-09/training-m06, run-02/f2-m01, run-02/f2-m04, run-05/f2-m03, run-05/f2-m01, run-05/f2-m06, round-09/weights-m01, round-09/weights-m02, round-09/weights-m03, round-09/weights-m04, round-09/weights-m05, round-09/weights-m06, run-07/f2-m02, round-09/problems-m02, round-09/problems-m03, round-09/problems-m04, round-09/problems-m06, run-03/f2-m02, run-03/f2-m05, round-09/stopping-m01, round-09/stopping-m02, round-09/stopping-m03, round-09/stopping-m05, round-09/stopping-m06, run-04/f2-m03, round-09/sampling-m02, round-09/sampling-m03, round-09/sampling-m04, round-09/sampling-m05, round-09/grader-m02, round-09/grader-m03, round-09/grader-m04, round-09/grader-m05, round-09/grader-m06.


### m36: untrained base Olmo-3-1025-7B (no edit); cue + the same 3 Math-RL-written solved examples in context as draw 1 of result-6d422d / result-5227b9 (the draw that gave 432/494), passed with run_cell --shots; MATH-500, n 497 generated (the 3 example problems left out); readout on the 494 problems that are no arm's example (as in result-5227b9) (base only)

GPU minutes 105 (proposers' guess). Separation 0 pairs, 0 per minute. Job `run_cell.py`.

Cell: {"model": "untrained base Olmo-3-1025-7B (no edit)", "prompt": "cue + the same 3 Math-RL-written solved examples in context as draw 1 of result-6d422d / result-5227b9 (the draw that gave 432/494), passed with run_cell --shots", "set": "MATH-500", "n": "497 generated (the 3 example problems left out); readout on the 494 problems that are no arm's example (as in result-5227b9)", "sampling": "T 1.0 / top-p 1.0 / min-p 0; new seed rule 65000000 + problem index (not the stored draw-1 seeds)", "samples": "1 per problem, no restarts", "grader": "v3", "cap": "16,384 generated tokens"}

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --shots studies/rlneurons/results/shots1b/rl_draw1.json --set math500 --temperature 1.0 --top-p 1.0 --seed 65000000 --commit $(git rev-parse HEAD)`


#### m36-r1: right answers with grader v3 among the 494 problems of result-5227b9 (right answers of 494)

Best known base count given to the forecasters: 432 (result-5227b9; Math-RL-written examples draw 1, cue, one sample, 432 of the same 494 problems (435/497 in result-6d422d); every other base-only one-sample cell on MATH-500 is lower (self-opened 411/500, logit bias 421/500, in-process unsteered 430/500, which scales to about 425 of 494).). Highest forecast: reader-1 420 (-12).

- proposed by round-09/grader-m01 (c41): 408 [398, 418]; says round-09/sampling-m01 gives 432 (its blind forecast: 420). m01 says the 432 was a notable first draw above its model's mean and pools the 3-example prompt with its near-identical cells (other example draws 401-411, no examples 404), so a new seed lands near 408. sampling-m01 treats the draw-1 prompt as its own arm and a 28-problem gap between draws as far beyond 5-7 problems of draw noise, so its arm mean stays at the measured 432.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 420 | [405, 435] |  |
| reader-2 | reader-2 | 418 | [403, 434] |  |
| round-09/sampling-m01 | sampling | 420 | [408, 432] |  |
| round-09/grader-m01 | grader | 411 | [398, 425] |  |

Theory says nothing: run-06/f2-m03, round-09/training-m01, round-09/training-m02, round-09/training-m03, round-09/training-m04, round-09/training-m05, round-09/training-m06, run-02/f2-m01, run-02/f2-m04, run-05/f2-m03, run-05/f2-m01, run-05/f2-m06, round-09/weights-m01, round-09/weights-m02, round-09/weights-m03, round-09/weights-m04, round-09/weights-m05, round-09/weights-m06, run-07/f2-m02, round-09/problems-m01, round-09/problems-m02, round-09/problems-m03, round-09/problems-m04, round-09/problems-m05, round-09/problems-m06, run-03/f2-m02, run-03/f2-m05, round-09/stopping-m01, round-09/stopping-m02, round-09/stopping-m03, round-09/stopping-m04, round-09/stopping-m05, round-09/stopping-m06, run-04/f2-m03, round-09/sampling-m02, round-09/sampling-m03, round-09/sampling-m04, round-09/sampling-m05, round-09/sampling-m06, round-09/grader-m02, round-09/grader-m03, round-09/grader-m04, round-09/grader-m05, round-09/grader-m06.


### m05: untrained base Olmo-3-1025-7B; plain (no cue); math500, n 100: the first 100 problems (--n 100) (base only)

GPU minutes 90 (proposers' guess). Separation 3 pairs, 0.0333 per minute. Job `run_cell.py`.

Cell: {"model": "untrained base Olmo-3-1025-7B", "prompt": "plain (no cue)", "set": "math500", "n": "100: the first 100 problems (--n 100)", "sampling": "T 1.0 / top-p 1.0 / min-p 0, seed 41000000 + problem index, sample offsets as run_cell --samples assigns", "samples": "8 per problem, no restarts; plurality vote over the 8 (rln4_lib.agree grouping, ties to the lowest sample)", "grader": "v3 on the voted answer", "cap": "16,384 generated tokens"}

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt plain --set math500 --temperature 1.0 --top-p 1.0 --seed 41000000 --n 100 --samples 8 --commit $(git rev-parse HEAD)`


#### m05-r1: right answers of the plurality vote over 8 samples, grader v3 (right answers of 100)

Best known base count given to the forecasters: 90 (result-5d032f; No base-only cell has 8 samples on these problems; nearest is the cued base vote over 4 after restart, 450 of 500 (result-5d032f, audited as the honest best in result-e78dfe), scaled to 100 problems: 90. That is 4 samples, not 8, and all 500 problems, not the first 100.). Highest forecast: round-09/problems-m03 72 (-18).

- proposed by round-09/training-m04 (c05): 80 [72, 88]; says round-09/stopping-m06 gives 45 (its blind forecast: 62). training-m04 says the cue picks the register but does not move each problem's modal value, so a vote over enough plain samples converges to the same mode as the cued vote (about 89 of these 100). At k = 8 it reaches about 80. stopping-m06 says terse plain samples end right after their first result and are wrong on any problem that needs a longer derivation. Their vote is capped near the problems plain usually gets right, about 45 (plain single is 34 here).

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 62 | [48, 76] |  |
| reader-2 | reader-2 | 62 | [48, 75] |  |
| round-09/training-m04 | training | 52 | [38, 66] |  |
| run-02/f2-m01 | run-02 | 60 | [47, 72] |  |
| round-09/problems-m01 | problems | 70 | [56, 82] | round-09/stopping-m01 |
| round-09/problems-m03 | problems | 72 | [58, 84] | round-09/stopping-m01 |
| round-09/stopping-m01 | stopping | 42 | [32, 52] | round-09/problems-m01, round-09/problems-m03, round-09/sampling-m02 |
| round-09/stopping-m06 | stopping | 62 | [50, 74] |  |
| round-09/sampling-m02 | sampling | 66 | [54, 76] | round-09/stopping-m01 |
| round-09/sampling-m06 | sampling | 58 | [46, 69] |  |
| round-09/grader-m02 | grader | 56 | [44, 67] |  |
| round-09/grader-m05 | grader | 54 | [42, 65] |  |

Theory says nothing: run-06/f2-m03, round-09/training-m01, round-09/training-m02, round-09/training-m03, round-09/training-m05, round-09/training-m06, run-02/f2-m04, run-05/f2-m03, run-05/f2-m01, run-05/f2-m06, round-09/weights-m01, round-09/weights-m02, round-09/weights-m03, round-09/weights-m04, round-09/weights-m05, round-09/weights-m06, run-07/f2-m02, round-09/problems-m02, round-09/problems-m04, round-09/problems-m05, round-09/problems-m06, run-03/f2-m02, run-03/f2-m05, round-09/stopping-m02, round-09/stopping-m03, round-09/stopping-m04, round-09/stopping-m05, run-04/f2-m03, round-09/sampling-m01, round-09/sampling-m03, round-09/sampling-m04, round-09/sampling-m05, round-09/grader-m01, round-09/grader-m03, round-09/grader-m04, round-09/grader-m06.


### m08: untrained base allenai/Olmo-3-1025-7B (run_cell --model base); cue (the 3-token opening cue of frozen4.json); hard328, n 164: the even-index half of hard328, problems 0, 2, 4, ..., 326 (--shard 0/2) (base only)

GPU minutes 70 (proposers' guess). Separation 0 pairs, 0 per minute. Job `run_cell.py`.

Cell: {"model": "untrained base allenai/Olmo-3-1025-7B (run_cell --model base)", "prompt": "cue (the 3-token opening cue of frozen4.json)", "set": "hard328", "n": "164: the even-index half of hard328, problems 0, 2, 4, ..., 326 (--shard 0/2)", "sampling": "T 1.0 / top-p 1.0 / min-p 0; seed 33000000 + problem index (new seeds, not the stored 3000000 rows)", "samples": "8 per problem, 0 restarts", "grader": "v3, plurality vote over the 8 samples (capped samples cast no vote), equal answers grouped with rln4_lib.agree, ties to the lowest sample", "cap": "2,048 generated tokens (--max-tokens 2048)"}

Command: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set hard328 --shard 0/2 --temperature 1.0 --top-p 1.0 --seed 33000000 --samples 8 --restarts 0 --max-tokens 2048 --commit $(git rev-parse HEAD)" && uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_vote --run runs/<job> --out studies/rlneurons/results/day1_3/hard328_base_cue_cap2k_s8-01`


#### m08-r1: right answers (grader v3) of the plurality vote over 8 samples on the 164 problems (right answers of 164)

Best known base count given to the forecasters: 100 (result-389164; No base-only cell has 8 samples on hard328, and no count exists for this half. Best base-only count on hard328: 199/328, vote over 4 after restarts (up to 12 generations per problem) with ties to the shortest. Scaled to the 164 even-index problems: 99.5. The plain 4-sample vote, 192/328 (result-5c961a), scales to 96.). Highest forecast: round-09/stopping-m01 62 (-38).

- proposed by run-02/f2-m01 (c08): 42 [32, 54]; says round-09/stopping-m01 gives 72 (its blind forecast: 62). f2-m01 says hard328 solutions need 6,000-14,000 tokens, so 2,048-token samples reach only the problems with short solutions. One stored base sample has about 50 of 328 right within 2k and 81 within 4k (result-1b6bf2), and a vote can only collect those: about 42 of 164. stopping-m01 says a longer cap turns abstentions into mostly wrong late answers, so a vote gains far less from more cap than one sample does. From cap 2k to 16k one sample gains about 55 on this half (about 25 to 80.5); the 16k vote is about 100 (192/328 at 4 samples, result-5c961a). If the vote gains at most half of the single's 55, it must already be about 72 or more at 2k.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 46 | [32, 62] |  |
| reader-2 | reader-2 | 50 | [35, 68] |  |
| round-09/training-m04 | training | 45 | [32, 58] |  |
| run-02/f2-m01 | run-02 | 48 | [35, 60] |  |
| run-02/f2-m04 | run-02 | 50 | [37, 62] |  |
| round-09/problems-m01 | problems | 54 | [40, 68] |  |
| round-09/problems-m02 | problems | 52 | [38, 66] |  |
| round-09/stopping-m01 | stopping | 62 | [48, 76] |  |
| round-09/sampling-m02 | sampling | 45 | [32, 57] |  |
| round-09/sampling-m06 | sampling | 40 | [28, 52] |  |
| round-09/grader-m02 | grader | 46 | [33, 60] |  |
| round-09/grader-m05 | grader | 44 | [31, 57] |  |

Theory says nothing: run-06/f2-m03, round-09/training-m01, round-09/training-m02, round-09/training-m03, round-09/training-m05, round-09/training-m06, run-05/f2-m03, run-05/f2-m01, run-05/f2-m06, round-09/weights-m01, round-09/weights-m02, round-09/weights-m03, round-09/weights-m04, round-09/weights-m05, round-09/weights-m06, run-07/f2-m02, round-09/problems-m03, round-09/problems-m04, round-09/problems-m05, round-09/problems-m06, run-03/f2-m02, run-03/f2-m05, round-09/stopping-m02, round-09/stopping-m03, round-09/stopping-m04, round-09/stopping-m05, round-09/stopping-m06, run-04/f2-m03, round-09/sampling-m01, round-09/sampling-m03, round-09/sampling-m04, round-09/sampling-m05, round-09/grader-m01, round-09/grader-m03, round-09/grader-m04, round-09/grader-m06.

