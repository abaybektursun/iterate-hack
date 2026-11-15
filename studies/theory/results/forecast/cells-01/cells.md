# Cells designed by the theories, cells-01

Written 2026-11-15T17:17:11 UTC (board read 2026-11-15T16:57:53 UTC). Plan `specs/SPEC_cells01.md`. Families: run-03 (6), run-04 (6), run-05 (6), run-06 (6), run-07 (6), run-08 (6), round-07 (8); 46 forecasters (each reader is its own family). Separation = pairs of forecasters from different families whose 90 % intervals do not overlap, summed over the cell's readouts.

- C1: 44 cells proposed, 41 after merging (needs 20 and 10): holds.
- C2: 3 merged cells have 3 or more such pairs (needs 5): refuted.
- C3: 6 base-only readouts have a forecast above the best known base count (m07-r1, m22-r1, m25-r1, m34-r1, m37-r1, m41-r1): holds.

## Every merged cell

| cell | model | prompt | set | n | base only | GPU minutes | separation | per minute |
|---|---|---|---|---|---|---|---|---|
| m20 | Olmo-3-1025-7B base (untrained) | plain | fresh2026 (136 competition problems published in 2026) | 136: all | yes | 50 | 3 | 0.06 |
| m29 | Olmo-3-1025-7B base + top 8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Math - base) at 2x (wsp_edit top-k recipe as in the xreward dial, stochastic rounding, seed 0) | cue | MATH-500 | 500 (all) |  | 110 | 5 | 0.0455 |
| m33 | Olmo-3-1025-7B base + top 8 singular directions per matrix of (RL-Math 3.1 - base) at 2.0x, stochastic rounding, seed 0 (edit written by jobs/wsp_edit.py) | Code cue (the 12-token cue of SPEC_code1, as prefix ids) | HumanEval+ and MBPP+ | all 538 problems of the code harness |  | 95 | 4 | 0.0421 |
| m06 | Olmo-3.1-7B-RL-Zero-Math checkpoint step 100 (revision step_0100 0a45720c) | plain | hard328 | 164: the first 164 problems of hard328 (--n 164) |  | 70 | 1 | 0.0143 |
| m01 | allenai/Olmo-3.1-7B-RL-Zero-Math (final, step 2800), unedited (run_cell --model rl) | plain | hard328 | 200: the first 200 problems of hard328 (--n 200) |  | 105 | 0 | 0 |
| m02 | Think-SFT + 2.0 x (RL-Math 3.1 - base), every tensor, written by delta_sum (host think_sft, donor rl_math, alpha 2.0, seed 0), bf16 directory /tmp/theta | cue | hard328 | 200: the first 200 problems of hard328 (--n 200) |  | 105 | 0 | 0 |
| m03 | RL-Math 3.1 minus its top 8 singular directions per matrix (wsp_edit, other rl_math, k 8), bf16 directory /tmp/theta | cue | hard328 | 160: the first 160 problems of hard328 (--n 160) |  | 90 | 0 | 0 |
| m04 | Think-SFT + 0.25 x (RL-Math 3.1 - base), every tensor, written by delta_sum (host think_sft, donor rl_math, alpha 0.25, seed 0), bf16 directory /tmp/theta | cue | math500 | 250: the first 250 MATH-500 problems (--n 250) |  | 112 | 0 | 0 |
| m05 | base Olmo-3-1025-7B + 2.5 x the top 8 singular directions per matrix of (RL-Math 3.1 - base) (wsp_edit, other rl_math, k 8, scale 2.5), bf16 directory /tmp/theta | cue | hard328 | 164: the first 164 problems of hard328 (--n 164) |  | 65 | 0 | 0 |
| m07 | Olmo-3-1025-7B base (untrained) | cue | hard328 | 60: the first 60 problems of hard328 (--n 60) | yes | 113 | 0 | 0 |
| m08 | Olmo-3-1025-7B base (untrained) | cue | math500 | 167: every third MATH-500 problem, indices 0, 3, ..., 498 (--shard 0/3) | yes | 100 | 0 | 0 |
| m09 | Olmo-3-1025-7B base + 2.0 x top-8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Math - base), every layer matrix (wsp_edit top-k recipe, the finish-dial edit at size 2), bf16 stochastic rounding, seed 0 | cue | math500 | 500, all problems |  | 110 | 0 | 0 |
| m10 | Olmo-3.1-7B-RL-Zero-Code (written as base + 1.0 x (Code-RL - base) with nearest rounding, the exact endpoint) | cue | hard328 | 240: the first 240 problems of hard328 (--n 240) |  | 101 | 0 | 0 |
| m11 | allenai/Olmo-3-7B-Think-SFT | cue (raw template) | hard328 | 120: the first 120 problems of hard328 (--n 120) |  | 62 | 0 | 0 |
| m12 | base + 2.0 x top-8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Math - base), stochastic bf16 rounding, seed 0 | cue | hard328 | 120: the first 120 problems of hard328 (--n 120) |  | 108 | 0 | 0 |
| m13 | Olmo-3-1025-7B base + top-8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Math - base) at 1x, stochastic bf16 rounding, seed 0 (jobs/wsp_edit.py top-k recipe) | cue | MATH-500 | first 300 problems (indices 0-299) |  | 75 | 0 | 0 |
| m14 | Olmo-3.1-7B-RL-Zero-Math minus its own top-8 singular directions per matrix (RL - base with the top 8 removed, added to base), stochastic bf16 rounding, seed 0 (jobs/wsp_edit.py remainder recipe) | cue | MATH-500 | first 300 problems (indices 0-299) |  | 80 | 0 | 0 |
| m15 | Olmo-3-1025-7B base + top-8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Code - base) at 1.5x, stochastic bf16 rounding, seed 0 | cue (math opening cue) | MATH-500 | first 300 problems (indices 0-299) |  | 70 | 0 | 0 |
| m16 | Olmo-3-1025-7B base + top-8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Math step_0100 @0a45720c - base), scaled about 9x to the norm of the final checkpoint's top-8 edit, stochastic bf16 rounding, seed 0 | cue | hard328 | 164 problems: shard 0/2 (indices 0, 2, 4, ...) |  | 90 | 0 | 0 |
| m17 | allenai/Olmo-3-7B-Think-SFT + 1.0 x (Olmo-3.1-7B-RL-Zero-Math - base), full delta, written by jobs/delta_sum.py (host think_sft, donor rl_math, alpha 1.0, seed 0) | cue (raw template, as in the transplant cells) | hard328 | 110 problems: shard 0/3 (indices 0, 3, 6, ...); shard 0/6 (indices 0, 6, ..., 324, 55 problems) is a subset |  | 105 | 0 | 0 |
| m18 | Olmo-3-1025-7B base + 0.125 x (Olmo-3.1-7B-RL-Zero-Math - base), merged in bf16 with round-to-nearest (jobs/merge_weights.py) | plain | MATH-500 | first 300 problems (indices 0-299) |  | 70 | 0 | 0 |
| m19 | allenai/Olmo-3-7B-Think-SFT served from a path (wsp_edit --recipe interp --other think_sft --alpha 1.0, as in the relay job) | cue (raw template, run_cell --prompt cue) | MATH-500 | 300: the first 300 problems (--n 300) |  | 95 | 0 | 0 |
| m21 | Olmo-3-1025-7B base + top 8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Code - base) at 1.5x (wsp_edit top-k recipe, as in the code-dial cells of result-a1bf75) | cue (math cue) | MATH-500 | 500: all |  | 110 | 0 | 0 |
| m22 | Olmo-3-1025-7B base (untrained) | cue | hard72 (the 72 harder problems in the RL training prompts) | 72: all | yes | 115 | 0 | 0 |
| m23 | allenai/Olmo-3-7B-Think-SFT + 3.0 x (Olmo-3.1-7B-RL-Zero-Math - Olmo-3-1025-7B base), all tensors, bf16 (delta_sum.py) | cue | fresh2026 | 136: all |  | 95 | 0 | 0 |
| m24 | Olmo-3-1025-7B base + top 8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Math - base) at 1.0x (wsp_edit top-k recipe, the edit of result-284db5) | cue | fresh2026 | 136: all |  | 90 | 0 | 0 |
| m25 | Olmo-3-1025-7B base (untrained) | cue | MATH-500 | 500 (all) | yes | 110 | 0 | 0 |
| m26 | Olmo-3-1025-7B base + top 8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Code - base) at 1.5x (wsp_edit top-k recipe as in the xreward/code_dial edits, stochastic rounding, seed 0) | cue (math) | MATH-500 | 500 (all) |  | 110 | 0 | 0 |
| m27 | Olmo-3.1-7B-RL-Zero-Math checkpoint step_0100 (rev 0a45720c; the run_cell model name used for the ckptcue step-100 cells) | plain | MATH-500 | 125 (the first 125 problems, --n 125) |  | 95 | 0 | 0 |
| m28 | Olmo-3-1025-7B base (untrained) | plain | hard328 (contest problems, integer answers mostly) | 100 (the first 100 problems, --n 100) | yes | 85 | 0 | 0 |
| m30 | Olmo-3-1025-7B base + top 8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Math - base) at 1x (wsp_edit top-k recipe, stochastic rounding, seed 0) | cue | fresh2026 | 136 (all) |  | 85 | 0 | 0 |
| m31 | allenai/Olmo-3.1-7B-RL-Zero-Math branch step_0400 (rev 897c0ce4), unedited | plain | hard328 | first 200 problems of the clean 328 (--n 200) |  | 85 | 0 | 0 |
| m32 | Olmo-3-1025-7B base + top 8 singular directions per matrix of (RL-Math 3.1 - base) at 1.0x (0.074 % of weight norm), stochastic rounding, seed 0 (edit written by jobs/wsp_edit.py) | cue | fresh2026 | all 136 problems |  | 90 | 0 | 0 |
| m34 | Olmo-3-1025-7B base, untrained | cue | hard328 | 82 problems: shard 0/4 (indices 0, 4, 8, ..., 324) | yes | 100 | 0 | 0 |
| m35 | Olmo-3-1025-7B base + top-8 singular directions per layer matrix of (Olmo-3.1 RL-Zero-Math - base) at 1x (the WSP-1 top8 edit, 0.07 % of weight norm), bf16 stochastic rounding, seed 0 | plain (no cue) | hard328 | 200: problems 0-199 of hard328 (--n 200) |  | 100 | 0 | 0 |
| m36 | allenai/Olmo-3-1025-7B (untrained base) | cue | math500 | 500, all problems | yes | 100 | 0 | 0 |
| m37 | allenai/Olmo-3-1025-7B (untrained base), context-contrast decoding: softmax(3 * logit(with problem) - 2 * logit(problem text deleted, same answer prefix)), i.e. --alpha 2 (result-a497ff used alpha 1, softmax(2l - l_noprob)) | cue; each request = the stored cued-base answer of a wrongstep item cut at the token before its located wrong step | the 51 located wrong-step items of studies/rlneurons/results/wrongstep/math500-01 (MATH-500, cued base, job abaybektursun-1114-153825-208b) | 51 items; readout on the 35 items labelled misread (14) or slip (21) | yes | 60 | 0 | 0 |
| m38 | allenai/Olmo-3-7B-RL-Zero-Math (3.0 release, main @ dee26a40, as in the reward5 cells) | cue | hard328 | 150: problems 0-149 of hard328 (--n 150) |  | 65 | 0 | 0 |
| m39 | allenai/Olmo-3.1-7B-RL-Zero-Code, written as base + 1.0 x (Code-RL 3.1 - base) by merge_weights (endpoint exact) | cue | hard328 | 164: shard 0/2 (problems 0, 2, 4, ...); readout on the shard problems where the cued base is right in 0 of its 4 stored samples (about 60) |  | 75 | 0 | 0 |
| m40 | allenai/Olmo-3-7B-Think-SFT (written by wsp_edit --recipe interp --other think_sft --alpha 1.0, as in the relay job) | cue (raw template, as in wsp1/full500/sft1_cue-01) | math500 | 500, all problems; readout on W = problems the cued base solves 4 of 4 (day1_3 math500_base_cue-01, attempt 0) whose stored sft1_cue-01 answer is finished and v3-wrong |  | 95 | 0 | 0 |
| m41 | allenai/Olmo-3-1025-7B (untrained base) | cue + 3 solved examples written by the cued base in context (run_cell --shots with the base-written draw-2 json of shots1b), so the prompt context differs from the stored cued samples | math500 | 494 (MATH-500 without the example problems); readout on G = problems where at least two of the four stored cued samples (day1_3 math500_base_cue-01, attempt 0) are finished wrong answers that agree under rln4_lib.agree (about 40) | yes | 110 | 0 | 0 |

## List A: top 10 by separation per GPU minute

### m20: Olmo-3-1025-7B base (untrained); plain; fresh2026 (136 competition problems published in 2026), n 136: all (base only)

GPU minutes 50 (proposers' guess). Separation 3 pairs, 0.06 per minute. Job `run_fresh.py`.

Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "plain", "set": "fresh2026 (136 competition problems published in 2026)", "n": "136: all", "sampling": "T 1.0, top-p 1.0, min-p 0; seed 93,000,000 + problem index", "samples": "1 per problem, no restarts", "grader": "v3", "cap": "16,384 (frozen4 default)"}

Command: `uv run tools/gpu.py submit l40s --hours 1.5 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_fresh --model base --prompt plain --set fresh2026 --temperature 1.0 --top-p 1.0 --seed 93000000 --commit $(git rev-parse HEAD)"`


#### m20-r1: right answers with grader v3 (metrics.json right_v3) (problems of 136)

Best known base count given to the forecasters: 29.5 (result-5251c9; base + cue, one sample, mean of 4 samples on the same 136 problems (vote over 4 is 38); no other base-only cell exists on fresh2026). Highest forecast: run-07/f2-m06 16 (-13.5).

- proposed by run-06/f2-m02 (c20): 2 [0, 5]; says run-07/f2-m06 gives 14 (its blind forecast: 16). f2-m02 fixes the cue's share of RL's gain at 55-78 %; on fresh2026 the cued base gets 29.5 and RL 50.5 per sample (result-5251c9), and share = (29.5 - p)/(50.5 - p) >= 0.55 forces the plain base to p <= 4. run-07/f2-m06 says fresh2026's thin middle band compresses every gain, the cue's included, so the plain base sits nearer the cued base than on hard328 (76 of 164 there, ratio 0.46): about half of 29.5.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 14 | [7, 22] |  |
| reader-2 | reader-2 | 13 | [6, 21] |  |
| run-06/f2-m02 | run-06 | 3 | [0, 8] | run-07/f2-m06 |
| run-06/f2-m06 | run-06 | 2 | [0, 7] | run-07/f2-m06, run-08/f2-m01 |
| run-07/f2-m06 | run-07 | 16 | [9, 23] | run-06/f2-m02, run-06/f2-m06 |
| run-08/f2-m01 | run-08 | 14 | [8, 20] | run-06/f2-m06 |

Theory says nothing: run-03/f2-m01, run-03/f2-m02, run-03/f2-m03, run-03/f2-m04, run-03/f2-m05, run-03/f2-m06, run-04/f2-m01, run-04/f2-m02, run-04/f2-m03, run-04/f2-m04, run-04/f2-m05, run-04/f2-m06, run-05/f2-m01, run-05/f2-m02, run-05/f2-m03, run-05/f2-m04, run-05/f2-m05, run-05/f2-m06, run-06/f2-m01, run-06/f2-m03, run-06/f2-m04, run-06/f2-m05, run-07/f2-m01, run-07/f2-m02, run-07/f2-m03, run-07/f2-m04, run-07/f2-m05, run-08/f2-m02, run-08/f2-m03, run-08/f2-m04, run-08/f2-m05, run-08/f2-m06, r5-m03-rival, r6-account-rival, r6-m06, r7-m05, r7-m07, r7-m08, r7-m09, r7-m11.


### m29: Olmo-3-1025-7B base + top 8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Math - base) at 2x (wsp_edit top-k recipe as in the xreward dial, stochastic rounding, seed 0); cue; MATH-500, n 500 (all)

GPU minutes 110 (proposers' guess). Separation 5 pairs, 0.0455 per minute. Job `run_cell.py`.

Cell: {"model": "Olmo-3-1025-7B base + top 8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Math - base) at 2x (wsp_edit top-k recipe as in the xreward dial, stochastic rounding, seed 0)", "prompt": "cue", "set": "MATH-500", "n": "500 (all)", "sampling": "T 1.0, top-p 1.0, min-p 0; problem i seeded 105000000 + i", "samples": "1 per problem, no restarts", "grader": "v3", "cap": "16,384"}

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe topk --other rl_math --k 8 --scale 2.0 --rounding stochastic --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label top8x2_math31 --prompt cue --set math500 --temperature 1.0 --top-p 1.0 --seed 105000000 --commit $(git rev-parse HEAD)`


#### m29-r1: Right answers with grader v3 (metrics.json right_v3) (problems of 500)

- proposed by run-07/f2-m05 (c29): 450 [442, 458]; says run-06/f2-m03 gives 436 (its blind forecast: 445). f2-m05: an over-dose's cost grows with derivation length; MATH-500 problems are short and finish within the shortened span, so 2x stays near 1.5x (456), ~450. run-06/f2-m03 says 2x commits too early, without a length condition; scaling the hard328 loss from 1.5x to 2x (203 to 190, -4 points) to MATH-500 gives ~436.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 445 | [431, 458] |  |
| reader-2 | reader-2 | 448 | [434, 460] |  |
| run-03/f2-m02 | run-03 | 447 | [436, 458] |  |
| run-03/f2-m05 | run-03 | 440 | [425, 453] |  |
| run-04/f2-m03 | run-04 | 448 | [435, 460] |  |
| run-04/f2-m06 | run-04 | 455 | [443, 466] | run-07/f2-m01 |
| run-05/f2-m01 | run-05 | 449 | [438, 460] | run-07/f2-m01 |
| run-05/f2-m02 | run-05 | 455 | [444, 465] | run-07/f2-m01 |
| run-05/f2-m06 | run-05 | 448 | [436, 459] |  |
| run-06/f2-m03 | run-06 | 445 | [434, 455] |  |
| run-07/f2-m01 | run-07 | 423 | [410, 436] | run-04/f2-m06, run-05/f2-m01, run-05/f2-m02, run-08/f2-m01, r5-m03-rival |
| run-07/f2-m05 | run-07 | 452 | [442, 462] |  |
| run-08/f2-m01 | run-08 | 450 | [439, 461] | run-07/f2-m01 |
| run-08/f2-m03 | run-08 | 448 | [436, 459] |  |
| r5-m03-rival | round-07 | 449 | [438, 459] | run-07/f2-m01 |

Theory says nothing: run-03/f2-m01, run-03/f2-m03, run-03/f2-m04, run-03/f2-m06, run-04/f2-m01, run-04/f2-m02, run-04/f2-m04, run-04/f2-m05, run-05/f2-m03, run-05/f2-m04, run-05/f2-m05, run-06/f2-m01, run-06/f2-m02, run-06/f2-m04, run-06/f2-m05, run-06/f2-m06, run-07/f2-m02, run-07/f2-m03, run-07/f2-m04, run-07/f2-m06, run-08/f2-m02, run-08/f2-m04, run-08/f2-m05, run-08/f2-m06, r6-account-rival, r6-m06, r7-m05, r7-m07, r7-m08, r7-m09, r7-m11.


### m33: Olmo-3-1025-7B base + top 8 singular directions per matrix of (RL-Math 3.1 - base) at 2.0x, stochastic rounding, seed 0 (edit written by jobs/wsp_edit.py); Code cue (the 12-token cue of SPEC_code1, as prefix ids); HumanEval+ and MBPP+, n all 538 problems of the code harness

GPU minutes 95 (proposers' guess). Separation 4 pairs, 0.0421 per minute. Job `run_code_cell.py`.

Cell: {"model": "Olmo-3-1025-7B base + top 8 singular directions per matrix of (RL-Math 3.1 - base) at 2.0x, stochastic rounding, seed 0 (edit written by jobs/wsp_edit.py)", "prompt": "Code cue (the 12-token cue of SPEC_code1, as prefix ids)", "set": "HumanEval+ and MBPP+", "n": "all 538 problems of the code harness", "sampling": "T 1.0, top-p 1.0, min-p 0; seed 51000000 + problem index (the code-dial seeds)", "samples": "1 per problem, no restarts", "grader": "code harness (last python code block, EvalPlus tests)", "cap": "harness default 16,384"}

Command: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe topk --other rl_math --k 8 --scale 2.0 --rounding stochastic --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_code_cell --model-path /tmp/theta --model-label math_top8x2.0 --prefix-ids '<Code cue ids of SPEC_code1>' --temperature 1.0 --top-p 1.0 --seed 51000000 --commit $(git rev-parse HEAD)"`


#### m33-r1: answers with no python code block for the extractor (not cap hits; harness extraction empty) (answers of 538)

- proposed by run-08/f2-m04 (c34): 45 [32, 62]; says run-05/f2-m03 gives 17 (its blind forecast: 8). f2-m04 says Math-RL directions carry a boxed ending that the code extractor misses, so a larger Math dose leaves more answers without a final code block than the cued base's 34. run-05/f2-m03 says the Math edit acts on code like a half-strength Code edit (input-subspace overlap 0.22-0.26), and the Code edit cut answers with no code block from 34 to 0 at 2x, so about half that drop: 17.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 12 | [3, 30] |  |
| reader-2 | reader-2 | 15 | [3, 35] |  |
| run-03/f2-m04 | run-03 | 35 | [15, 60] | run-04/f2-m03, run-04/f2-m06 |
| run-04/f2-m03 | run-04 | 3 | [0, 10] | run-03/f2-m04, run-08/f2-m04 |
| run-04/f2-m06 | run-04 | 4 | [0, 12] | run-03/f2-m04, run-08/f2-m04 |
| run-05/f2-m01 | run-05 | 8 | [2, 20] |  |
| run-05/f2-m03 | run-05 | 8 | [2, 18] |  |
| run-06/f2-m03 | run-06 | 14 | [4, 30] |  |
| run-07/f2-m02 | run-07 | 25 | [8, 45] |  |
| run-07/f2-m05 | run-07 | 12 | [4, 25] |  |
| run-08/f2-m04 | run-08 | 38 | [18, 62] | run-04/f2-m03, run-04/f2-m06 |

Theory says nothing: run-03/f2-m01, run-03/f2-m02, run-03/f2-m03, run-03/f2-m05, run-03/f2-m06, run-04/f2-m01, run-04/f2-m02, run-04/f2-m04, run-04/f2-m05, run-05/f2-m02, run-05/f2-m04, run-05/f2-m05, run-05/f2-m06, run-06/f2-m01, run-06/f2-m02, run-06/f2-m04, run-06/f2-m05, run-06/f2-m06, run-07/f2-m01, run-07/f2-m03, run-07/f2-m04, run-07/f2-m06, run-08/f2-m01, run-08/f2-m02, run-08/f2-m03, run-08/f2-m05, run-08/f2-m06, r5-m03-rival, r6-account-rival, r6-m06, r7-m05, r7-m07, r7-m08, r7-m09, r7-m11.


### m06: Olmo-3.1-7B-RL-Zero-Math checkpoint step 100 (revision step_0100 0a45720c); plain; hard328, n 164: the first 164 problems of hard328 (--n 164)

GPU minutes 70 (proposers' guess). Separation 1 pairs, 0.0143 per minute. Job `run_cell.py`.

Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math checkpoint step 100 (revision step_0100 0a45720c)", "prompt": "plain", "set": "hard328", "n": "164: the first 164 problems of hard328 (--n 164)", "sampling": "T 1.0, top-p 1.0, min-p 0, seed 3000000 + problem index", "samples": "1, no restarts", "grader": "v3", "cap": "16,384 generated tokens (default)"}

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model s0100 --prompt plain --set hard328 --temperature 1.0 --top-p 1.0 --seed 3000000 --n 164 --commit $(git rev-parse HEAD)`


#### m06-r1: quick finished-wrong answers: rows that are not cap hits, are graded wrong by v3 and have at most 2,000 generated tokens (problems of 164)

- proposed by run-03/f2-m06 (c06): 30 [22, 38]; says run-06/f2-m02 gives 7 (its blind forecast: 6). At T 1.0, step 100 opens with 'Okay' on 383 of 500 MATH-500 answers, so about 23 % miss the opening (about 38 of 164). m06 says these misses fall into the base's terse register and stop before checking. On hard328 that register is wrong about 70 % of the time (plain base 76 of 328), mostly in short answers: about 27, plus about 4 quick wrong answers among the opened ones, for about 30. run-06/f2-m02 has step 100 select the deliberative register and sharpen slightly inside it, so its answers behave like the cued base's. The cued base has few quick wrong answers on hard328, about 5 to 8 per 164: about 7.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 20 | [9, 34] |  |
| reader-2 | reader-2 | 22 | [10, 36] |  |
| run-03/f2-m06 | run-03 | 26 | [15, 38] | run-06/f2-m02 |
| run-05/f2-m04 | run-05 | 8 | [3, 16] |  |
| run-06/f2-m02 | run-06 | 6 | [2, 12] | run-03/f2-m06 |

Theory says nothing: run-03/f2-m01, run-03/f2-m02, run-03/f2-m03, run-03/f2-m04, run-03/f2-m05, run-04/f2-m01, run-04/f2-m02, run-04/f2-m03, run-04/f2-m04, run-04/f2-m05, run-04/f2-m06, run-05/f2-m01, run-05/f2-m02, run-05/f2-m03, run-05/f2-m05, run-05/f2-m06, run-06/f2-m01, run-06/f2-m03, run-06/f2-m04, run-06/f2-m05, run-06/f2-m06, run-07/f2-m01, run-07/f2-m02, run-07/f2-m03, run-07/f2-m04, run-07/f2-m05, run-07/f2-m06, run-08/f2-m01, run-08/f2-m02, run-08/f2-m03, run-08/f2-m04, run-08/f2-m05, run-08/f2-m06, r5-m03-rival, r6-account-rival, r6-m06, r7-m05, r7-m07, r7-m08, r7-m09, r7-m11.


### m01: allenai/Olmo-3.1-7B-RL-Zero-Math (final, step 2800), unedited (run_cell --model rl); plain; hard328, n 200: the first 200 problems of hard328 (--n 200)

GPU minutes 105 (proposers' guess). Separation 0 pairs, 0 per minute. Job `run_cell.py`.

Cell: {"model": "allenai/Olmo-3.1-7B-RL-Zero-Math (final, step 2800), unedited (run_cell --model rl)", "prompt": "plain", "set": "hard328", "n": "200: the first 200 problems of hard328 (--n 200)", "sampling": "T 1.0, top-p 1.0, min-p 0; problem i sample s seeded by run_cell from --seed 3000000 + i (sample 0 = the single-sample seed 3000000 + i)", "samples": "3 per problem, no restarts", "grader": "v3; vote = plurality of extracted v3 answers grouped with rln4_lib.agree, cap hits cast no vote, ties to the lowest sample", "cap": "8,192 generated tokens, native (--max-tokens 8192)"}

Command: `uv run tools/gpu.py submit l40s --hours 3 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model rl --prompt plain --set hard328 --n 200 --samples 3 --max-tokens 8192 --temperature 1.0 --top-p 1.0 --seed 3000000 --commit $(git rev-parse HEAD)"`


#### m01-r1: right answers (v3) under the plurality vote over the 3 samples (cap hits abstain), on the first 130 problems (0-129) (problems of 130)

- proposed by run-03/f2-m01 (c01): 69 [63, 75]; says run-04/f2-m06 gives 60 (its blind forecast: 63). At an 8,192 cap about half of RL's hard328 answers (median length 7,718) are cut. Under m01 these are its long, low-precision answers (RL is right on 24 % of answers over 12k). Cut answers cast no vote, and finished answers under 8k are right about 85 % of the time (about 140 of 164 per sample), so the vote rises toward pass@3 over the short answers: about 1.25 x the single-sample count of about 55.5 (42.7 % of 130). run-04/f2-m06 ties the vote's gain to the full RL dose's answer concentration, not to the cap, so the vote keeps RL's ratio of about 1.08 (221/200 on hard328): 55.5 x 1.08 = 60.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 67 | [52, 82] |  |
| reader-2 | reader-2 | 56 | [43, 70] |  |
| run-03/f2-m01 | run-03 | 72 | [60, 84] |  |
| run-03/f2-m03 | run-03 | 70 | [58, 82] |  |
| run-04/f2-m01 | run-04 | 72 | [61, 83] |  |
| run-04/f2-m02 | run-04 | 69 | [58, 79] |  |
| run-04/f2-m04 | run-04 | 68 | [58, 78] |  |
| run-04/f2-m06 | run-04 | 63 | [53, 73] |  |
| run-05/f2-m02 | run-05 | 66 | [56, 76] |  |
| run-06/f2-m04 | run-06 | 62 | [52, 72] |  |
| run-07/f2-m01 | run-07 | 68 | [56, 80] |  |
| run-07/f2-m04 | run-07 | 71 | [59, 83] |  |
| run-08/f2-m05 | run-08 | 72 | [63, 81] |  |
| run-08/f2-m06 | run-08 | 75 | [65, 84] |  |

Theory says nothing: run-03/f2-m02, run-03/f2-m04, run-03/f2-m05, run-03/f2-m06, run-04/f2-m03, run-04/f2-m05, run-05/f2-m01, run-05/f2-m03, run-05/f2-m04, run-05/f2-m05, run-05/f2-m06, run-06/f2-m01, run-06/f2-m02, run-06/f2-m03, run-06/f2-m05, run-06/f2-m06, run-07/f2-m02, run-07/f2-m03, run-07/f2-m05, run-07/f2-m06, run-08/f2-m01, run-08/f2-m02, run-08/f2-m03, run-08/f2-m04, r5-m03-rival, r6-account-rival, r6-m06, r7-m05, r7-m07, r7-m08, r7-m09, r7-m11.


#### m01-r2: right answers (v3) among sample-0 rows that hit the 8,192 cap (finish reason length) in answers.jsonl, on problems 0-199 (sample 0 only) (problems of 200)

- proposed by run-08/f2-m02 (c32): 19 [10, 30]; says run-07/f2-m01 gives 0 (its blind forecast: 3). f2-m02 says a native cap lets v3 credit a box RL has already written inside a truncated row (69 % of RL's capped rows hold a box; about a quarter of capped RL rows scored right in the 4,000-token prefix run), so of the about 95 RL rows cut at 8,192 about 20 % count right. run-07/f2-m01 says an answer cut at the cap scores zero, so capped rows add no right answers.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 13 | [4, 25] |  |
| reader-2 | reader-2 | 13 | [4, 27] |  |
| run-07/f2-m01 | run-07 | 3 | [0, 10] |  |
| run-08/f2-m02 | run-08 | 22 | [10, 36] |  |

Theory says nothing: run-03/f2-m01, run-03/f2-m02, run-03/f2-m03, run-03/f2-m04, run-03/f2-m05, run-03/f2-m06, run-04/f2-m01, run-04/f2-m02, run-04/f2-m03, run-04/f2-m04, run-04/f2-m05, run-04/f2-m06, run-05/f2-m01, run-05/f2-m02, run-05/f2-m03, run-05/f2-m04, run-05/f2-m05, run-05/f2-m06, run-06/f2-m01, run-06/f2-m02, run-06/f2-m03, run-06/f2-m04, run-06/f2-m05, run-06/f2-m06, run-07/f2-m02, run-07/f2-m03, run-07/f2-m04, run-07/f2-m05, run-07/f2-m06, run-08/f2-m01, run-08/f2-m03, run-08/f2-m04, run-08/f2-m05, run-08/f2-m06, r5-m03-rival, r6-account-rival, r6-m06, r7-m05, r7-m07, r7-m08, r7-m09, r7-m11.


### m02: Think-SFT + 2.0 x (RL-Math 3.1 - base), every tensor, written by delta_sum (host think_sft, donor rl_math, alpha 2.0, seed 0), bf16 directory /tmp/theta; cue; hard328, n 200: the first 200 problems of hard328 (--n 200)

GPU minutes 105 (proposers' guess). Separation 0 pairs, 0 per minute. Job `run_cell.py`.

Cell: {"model": "Think-SFT + 2.0 x (RL-Math 3.1 - base), every tensor, written by delta_sum (host think_sft, donor rl_math, alpha 2.0, seed 0), bf16 directory /tmp/theta", "prompt": "cue", "set": "hard328", "n": "200: the first 200 problems of hard328 (--n 200)", "sampling": "T 1.0, top-p 1.0, min-p 0, seed 3000000 + problem index", "samples": "1, no restarts", "grader": "v3", "cap": "32,768 generated tokens (--max-tokens 32768); the same answers are also counted at 16,384 (an answer longer than 16,384 counts wrong there)"}

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.delta_sum --host think_sft --donor rl_math --alpha 2.0 --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label sft_plus_2rl --prompt cue --set hard328 --temperature 1.0 --top-p 1.0 --max-tokens 32768 --seed 3000000 --n 200 --commit $(git rev-parse HEAD)`


#### m02-r1: right answers (v3) among answers that finish between 16,385 and 32,768 generated tokens = right at cap 32,768 minus right counted at 16,384, from the same rows (problems of 200)

- proposed by run-03/f2-m02 (c02): 3 [0, 6]; says run-05/f2-m05 gives 8 (its blind forecast: 9). At 16k, a = 2 leaves 54 of 328 cap hits, about 33 of these 200 problems. m02 says the RL delta acts on Think-SFT as a finishing hazard that, past 1.5x, closes hard problems with guesses. Answers still running past 16k therefore end like RL's long answers, right about 10 % of the time (RL 2 of 20, base 4 of 64): about 3. run-05/f2-m05 has the RL part superpose without disturbing SFT's precision, with SFT cap hits following the token budget. The extension then converts at Think-SFT's own rate, 23 of 93 (25 %): about 8.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 6 | [2, 12] |  |
| reader-2 | reader-2 | 6 | [2, 12] |  |
| run-03/f2-m02 | run-03 | 5 | [1, 10] |  |
| run-03/f2-m03 | run-03 | 7 | [2, 12] |  |
| run-03/f2-m05 | run-03 | 4 | [1, 9] |  |
| run-04/f2-m03 | run-04 | 8 | [3, 14] |  |
| run-04/f2-m05 | run-04 | 6 | [2, 11] |  |
| run-05/f2-m01 | run-05 | 6 | [2, 12] |  |
| run-05/f2-m02 | run-05 | 9 | [3, 15] |  |
| run-05/f2-m05 | run-05 | 9 | [3, 15] |  |
| run-06/f2-m01 | run-06 | 8 | [3, 14] |  |
| run-06/f2-m05 | run-06 | 5 | [1.5, 10] |  |
| run-07/f2-m01 | run-07 | 9 | [4, 15] |  |
| run-07/f2-m05 | run-07 | 6 | [2, 11] |  |
| run-08/f2-m02 | run-08 | 7 | [2, 13] |  |
| r6-account-rival | round-07 | 6 | [2, 12] |  |

Theory says nothing: run-03/f2-m01, run-03/f2-m04, run-03/f2-m06, run-04/f2-m01, run-04/f2-m02, run-04/f2-m04, run-04/f2-m06, run-05/f2-m03, run-05/f2-m04, run-05/f2-m06, run-06/f2-m02, run-06/f2-m03, run-06/f2-m04, run-06/f2-m06, run-07/f2-m02, run-07/f2-m03, run-07/f2-m04, run-07/f2-m06, run-08/f2-m01, run-08/f2-m03, run-08/f2-m04, run-08/f2-m05, run-08/f2-m06, r5-m03-rival, r6-m06, r7-m05, r7-m07, r7-m08, r7-m09, r7-m11.


### m03: RL-Math 3.1 minus its top 8 singular directions per matrix (wsp_edit, other rl_math, k 8), bf16 directory /tmp/theta; cue; hard328, n 160: the first 160 problems of hard328 (--n 160)

GPU minutes 90 (proposers' guess). Separation 0 pairs, 0 per minute. Job `run_cell.py`.

Cell: {"model": "RL-Math 3.1 minus its top 8 singular directions per matrix (wsp_edit, other rl_math, k 8), bf16 directory /tmp/theta", "prompt": "cue", "set": "hard328", "n": "160: the first 160 problems of hard328 (--n 160)", "sampling": "T 1.0, top-p 1.0, min-p 0, seed 3000000 + problem index", "samples": "1, no restarts", "grader": "v3", "cap": "32,768 generated tokens; the same answers are also counted at 16,384"}

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe minus_topk --other rl_math --k 8 --rounding stochastic --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label rl_minus_top8 --prompt cue --set hard328 --temperature 1.0 --top-p 1.0 --max-tokens 32768 --seed 3000000 --n 160 --commit $(git rev-parse HEAD)`


#### m03-r1: right answers (v3) among answers that finish between 16,385 and 32,768 generated tokens = right at 32,768 minus right counted at 16,384, from the same rows (problems of 160)

- proposed by run-03/f2-m03 (c03): 3 [0, 6]; says run-05/f2-m02 gives 11 (its blind forecast: 6). RL minus its top 8 had 90 cap hits on the 328 at 16k (result-284db5), about 44 of these 160 problems. m03 says RL-made weights, like the base, close long answers with asserted numbers. Their long answers then finish right at the RL and base rate past 16k (2 of 20 and 4 of 64, about 8 %): about 3. run-05/f2-m02 says this remainder is a dense per-step error reducer with no termination drive, so its cap hits are unfinished careful derivations. These convert like Think-SFT's unfinished work, about 25 %: about 11.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 4 | [1, 9] |  |
| reader-2 | reader-2 | 6 | [2, 13] |  |
| run-03/f2-m02 | run-03 | 5 | [1, 11] |  |
| run-03/f2-m03 | run-03 | 3 | [0, 7] |  |
| run-03/f2-m05 | run-03 | 2 | [0, 6] |  |
| run-04/f2-m03 | run-04 | 4 | [1, 9] |  |
| run-05/f2-m01 | run-05 | 4 | [1, 9] |  |
| run-05/f2-m02 | run-05 | 6 | [2, 12] |  |
| run-06/f2-m03 | run-06 | 8 | [3, 14] |  |
| run-07/f2-m01 | run-07 | 11 | [5, 18] |  |
| run-08/f2-m02 | run-08 | 6 | [1, 12] |  |
| r6-account-rival | round-07 | 4 | [0, 9] |  |

Theory says nothing: run-03/f2-m01, run-03/f2-m04, run-03/f2-m06, run-04/f2-m01, run-04/f2-m02, run-04/f2-m04, run-04/f2-m05, run-04/f2-m06, run-05/f2-m03, run-05/f2-m04, run-05/f2-m05, run-05/f2-m06, run-06/f2-m01, run-06/f2-m02, run-06/f2-m04, run-06/f2-m05, run-06/f2-m06, run-07/f2-m02, run-07/f2-m03, run-07/f2-m04, run-07/f2-m05, run-07/f2-m06, run-08/f2-m01, run-08/f2-m03, run-08/f2-m04, run-08/f2-m05, run-08/f2-m06, r5-m03-rival, r6-m06, r7-m05, r7-m07, r7-m08, r7-m09, r7-m11.


### m04: Think-SFT + 0.25 x (RL-Math 3.1 - base), every tensor, written by delta_sum (host think_sft, donor rl_math, alpha 0.25, seed 0), bf16 directory /tmp/theta; cue; math500, n 250: the first 250 MATH-500 problems (--n 250)

GPU minutes 112 (proposers' guess). Separation 0 pairs, 0 per minute. Job `run_cell.py`.

Cell: {"model": "Think-SFT + 0.25 x (RL-Math 3.1 - base), every tensor, written by delta_sum (host think_sft, donor rl_math, alpha 0.25, seed 0), bf16 directory /tmp/theta", "prompt": "cue", "set": "math500", "n": "250: the first 250 MATH-500 problems (--n 250)", "sampling": "T 1.0, top-p 1.0, min-p 0; seed 41000000 + problem index, samples seeded by run_cell", "samples": "2 per problem (500 rows), no restarts", "grader": "v3", "cap": "16,384 generated tokens (frozen4 default)"}

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.delta_sum --host think_sft --donor rl_math --alpha 0.25 --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label sft_plus_0.25rl --prompt cue --set math500 --temperature 1.0 --top-p 1.0 --seed 41000000 --n 250 --samples 2 --commit $(git rev-parse HEAD)`


#### m04-r1: finished rows (no cap hit) graded wrong by v3 whose last non-empty line, with spaces and $ removed, equals the gold string normalized the same way (the 'gold on the line after Answer:' undercount), counted over all 500 rows (rows of 500)

- proposed by run-03/f2-m04 (c04): 1 [0, 3]; says run-07/f2-m04 gives 4 (its blind forecast: 4). Raw-template Think-SFT ends with the gold on a line v3 does not read in about 4 answers per 500-row sample (16 of its 74 finished wrong answers over 4 samples). m04 says RL directions install one terminal marker. A quarter of the delta already moves about 72 % of RL's format on the base (theta 0.25 format share 0.72), which leaves about 0.28 x 4, or about 1. run-07/f2-m04 attributes the undercount to the answer type (expressions) and Think-SFT's 'Answer:' ending, which this small delta does not touch, so about 4 remain.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 3 | [0, 8] |  |
| reader-2 | reader-2 | 3 | [0, 8] |  |
| run-03/f2-m04 | run-03 | 2 | [0, 5] |  |
| run-04/f2-m05 | run-04 | 4 | [1, 8] |  |
| run-05/f2-m01 | run-05 | 3 | [0.5, 7] |  |
| run-05/f2-m05 | run-05 | 4 | [1, 8] |  |
| run-05/f2-m06 | run-05 | 4 | [1, 8] |  |
| run-06/f2-m03 | run-06 | 2 | [0, 5] |  |
| run-07/f2-m04 | run-07 | 4 | [1, 8] |  |
| run-08/f2-m04 | run-08 | 3 | [0, 7] |  |
| r7-m09 | round-07 | 4 | [1, 8] |  |

Theory says nothing: run-03/f2-m01, run-03/f2-m02, run-03/f2-m03, run-03/f2-m05, run-03/f2-m06, run-04/f2-m01, run-04/f2-m02, run-04/f2-m03, run-04/f2-m04, run-04/f2-m06, run-05/f2-m02, run-05/f2-m03, run-05/f2-m04, run-06/f2-m01, run-06/f2-m02, run-06/f2-m04, run-06/f2-m05, run-06/f2-m06, run-07/f2-m01, run-07/f2-m02, run-07/f2-m03, run-07/f2-m05, run-07/f2-m06, run-08/f2-m01, run-08/f2-m02, run-08/f2-m03, run-08/f2-m05, run-08/f2-m06, r5-m03-rival, r6-account-rival, r6-m06, r7-m05, r7-m07, r7-m08, r7-m11.


### m05: base Olmo-3-1025-7B + 2.5 x the top 8 singular directions per matrix of (RL-Math 3.1 - base) (wsp_edit, other rl_math, k 8, scale 2.5), bf16 directory /tmp/theta; cue; hard328, n 164: the first 164 problems of hard328 (--n 164)

GPU minutes 65 (proposers' guess). Separation 0 pairs, 0 per minute. Job `run_cell.py`.

Cell: {"model": "base Olmo-3-1025-7B + 2.5 x the top 8 singular directions per matrix of (RL-Math 3.1 - base) (wsp_edit, other rl_math, k 8, scale 2.5), bf16 directory /tmp/theta", "prompt": "cue", "set": "hard328", "n": "164: the first 164 problems of hard328 (--n 164)", "sampling": "T 1.0, top-p 1.0, min-p 0, seed 3000000 + problem index", "samples": "1, no restarts", "grader": "v3", "cap": "16,384 generated tokens (default)"}

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe topk --other rl_math --k 8 --scale 2.5 --rounding stochastic --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label top8x2.5 --prompt cue --set hard328 --temperature 1.0 --top-p 1.0 --seed 3000000 --n 164 --commit $(git rev-parse HEAD)`


#### m05-r1: right answers with grader v3 (problems of 164)

- proposed by run-03/f2-m05 (c05): 77 [68, 85]; says run-05/f2-m01 gives 88 (its blind forecast: 80). On the dial, 2x gives 190 of 328 and 3x gives 117 with word strings (result-6f1bb7). m05 says the hazard of degeneration grows with edit size from 2x to 3x, so 2.5x sits about midway in the collapse: about 154 of 328, or 77 of 164 (scaled by 164/328). run-05/f2-m01 has no degeneration term: past 1.5x the dial only closes unfinished hard problems on guesses, so the decline keeps the 1.5x-to-2x slope (-13 per 0.5x): about 177 of 328, or 88 of 164.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 76 | [55, 96] |  |
| reader-2 | reader-2 | 82 | [60, 101] |  |
| run-03/f2-m02 | run-03 | 84 | [68, 100] |  |
| run-03/f2-m05 | run-03 | 72 | [55, 89] |  |
| run-04/f2-m03 | run-04 | 79 | [62, 96] |  |
| run-05/f2-m01 | run-05 | 80 | [62, 96] |  |
| run-05/f2-m06 | run-05 | 82 | [64, 98] |  |
| run-06/f2-m03 | run-06 | 72 | [55, 90] |  |
| run-07/f2-m05 | run-07 | 72 | [55, 90] |  |
| run-08/f2-m01 | run-08 | 81 | [66, 96] |  |
| run-08/f2-m03 | run-08 | 79 | [62, 96] |  |

Theory says nothing: run-03/f2-m01, run-03/f2-m03, run-03/f2-m04, run-03/f2-m06, run-04/f2-m01, run-04/f2-m02, run-04/f2-m04, run-04/f2-m05, run-04/f2-m06, run-05/f2-m02, run-05/f2-m03, run-05/f2-m04, run-05/f2-m05, run-06/f2-m01, run-06/f2-m02, run-06/f2-m04, run-06/f2-m05, run-06/f2-m06, run-07/f2-m01, run-07/f2-m02, run-07/f2-m03, run-07/f2-m04, run-07/f2-m06, run-08/f2-m02, run-08/f2-m04, run-08/f2-m05, run-08/f2-m06, r5-m03-rival, r6-account-rival, r6-m06, r7-m05, r7-m07, r7-m08, r7-m09, r7-m11.


### m07: Olmo-3-1025-7B base (untrained); cue; hard328, n 60: the first 60 problems of hard328 (--n 60) (base only)

GPU minutes 113 (proposers' guess). Separation 0 pairs, 0 per minute. Job `run_cell.py`.

Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "cue", "set": "hard328", "n": "60: the first 60 problems of hard328 (--n 60)", "sampling": "T 1.0, top-p 1.0, min-p 0; seed 3500000 + index (new seeds, disjoint from the stored seed-3000000 rows)", "samples": "4 per problem, no restarts; voted together with the 4 stored attempt-0 samples of the same 60 problems (job e8e6, results/day1_3/hard328_base_cue_s4r2-01)", "grader": "v3", "cap": "16,384"}

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set hard328 --temperature 1.0 --top-p 1.0 --seed 3500000 --n 60 --samples 4 --restarts 0 --commit $(git rev-parse HEAD)`


#### m07-r1: right answers of 60 under a plurality vote over 8 samples (the 4 new + the 4 stored attempt-0 samples), answers grouped with rln4_lib.agree, cap hits cast no vote, ties to the lowest sample index (right answers of 60)

Best known base count given to the forecasters: 36.4 (result-389164; No base-only cell has 8 samples on these problems. Best base on the 328 is vote over 4 after restart with ties to the shortest, 199/328 (4 samples plus restarts), scaled to 60 problems: 36.4.). Highest forecast: run-04/f2-m01 38 (+1.6).

- proposed by run-04/f2-m01 (c07): 37.1 [35.5, 39.5]; says r7-m11 gives 35 (its blind forecast: nothing). f2-m01 has wrong answers scattering, so samples 5-8 keep turning problems with p of 0.25-0.4 into plurality wins: 192 at k=4 rises toward 203 of 328 (pass@4 207), i.e. 37.1 of 60. r7-m11 has the shared prompt and opening produce agreeing wrong groups that grow with k, so the 8-vote stays at the 4-vote's 192/328 (35.0 of 60) or below.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 36.5 | [29, 44] |  |
| reader-2 | reader-2 | 36 | [30, 42] |  |
| run-03/f2-m01 | run-03 | 36 | [30, 42] |  |
| run-04/f2-m01 | run-04 | 38 | [32, 44] |  |
| run-04/f2-m02 | run-04 | 36 | [30, 42] |  |
| run-04/f2-m04 | run-04 | 37 | [31, 43] |  |
| run-04/f2-m06 | run-04 | 37 | [31, 43] |  |
| run-06/f2-m04 | run-06 | 35.5 | [31, 40] |  |
| run-07/f2-m04 | run-07 | 38 | [32, 44] |  |
| run-07/f2-m06 | run-07 | 37 | [31, 43] |  |
| run-08/f2-m05 | run-08 | 36 | [31, 41] |  |
| run-08/f2-m06 | run-08 | 37 | [32, 43] |  |

Theory says nothing: run-03/f2-m02, run-03/f2-m03, run-03/f2-m04, run-03/f2-m05, run-03/f2-m06, run-04/f2-m03, run-04/f2-m05, run-05/f2-m01, run-05/f2-m02, run-05/f2-m03, run-05/f2-m04, run-05/f2-m05, run-05/f2-m06, run-06/f2-m01, run-06/f2-m02, run-06/f2-m03, run-06/f2-m05, run-06/f2-m06, run-07/f2-m01, run-07/f2-m02, run-07/f2-m03, run-07/f2-m05, run-08/f2-m01, run-08/f2-m02, run-08/f2-m03, run-08/f2-m04, r5-m03-rival, r6-account-rival, r6-m06, r7-m05, r7-m07, r7-m08, r7-m09, r7-m11.


## List B: base-only cells, top 10 by the highest forecast of right answers minus the best known base count

### m41: allenai/Olmo-3-1025-7B (untrained base); cue + 3 solved examples written by the cued base in context (run_cell --shots with the base-written draw-2 json of shots1b), so the prompt context differs from the stored cued samples; math500, n 494 (MATH-500 without the example problems); readout on G = problems where at least two of the four stored cued samples (day1_3 math500_base_cue-01, attempt 0) are finished wrong answers that agree under rln4_lib.agree (about 40) (base only)

GPU minutes 110 (proposers' guess). Separation 0 pairs, 0 per minute. Job `run_cell.py`.

Cell: {"model": "allenai/Olmo-3-1025-7B (untrained base)", "prompt": "cue + 3 solved examples written by the cued base in context (run_cell --shots with the base-written draw-2 json of shots1b), so the prompt context differs from the stored cued samples", "set": "math500", "n": "494 (MATH-500 without the example problems); readout on G = problems where at least two of the four stored cued samples (day1_3 math500_base_cue-01, attempt 0) are finished wrong answers that agree under rln4_lib.agree (about 40)", "sampling": "T 1.0, top-p 1.0, min-p 0; problem i seeded 7,000,000 + i", "samples": "1 per problem, no restarts", "grader": "v3", "cap": "16,384 generated tokens"}

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set math500 --shots <shots1b base-written draw-2 json> --temperature 1.0 --top-p 1.0 --seed 7000000 --commit $(git rev-parse HEAD)`


#### m41-r1: right answers (v3, cap hits wrong) on the problems of G (right of |G| (about 40))

Best known base count given to the forecasters: 9 (result-882fa7; no board count exists on G. Estimate: the cued base's mean right rate on G (about 0.2; at most 0.5 by construction) times |G| of about 40 gives 8. Scaled by the best one-sample base cell (430 against the cue's 410, result-882fa7), that is about 9.). Highest forecast: r7-m11 13 (+4).

- proposed by r7-m11 (c44): 15 [9, 21]; says run-07/f2-m03 gives 7 (its blind forecast: 6). r7-m11 ties the agreeing wrong value to the shared prompt-plus-opening context, so a sample drawn under a different context escapes it and is right about 0.35-0.4 of the time on G. f2-m03 ties the repeated wrong value to the problem's wording, so any context draws it again and the new sample stays at the cued right rate on G (~0.18).

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 8 | [3, 14] |  |
| reader-2 | reader-2 | 8 | [3, 14] |  |
| run-04/f2-m04 | run-04 | 8 | [3, 13] |  |
| run-06/f2-m04 | run-06 | 7.5 | [3, 13] |  |
| run-07/f2-m03 | run-07 | 6 | [2, 11] |  |
| run-08/f2-m05 | run-08 | 8 | [4, 13] |  |
| r7-m11 | round-07 | 13 | [7, 19] |  |

Theory says nothing: run-03/f2-m01, run-03/f2-m02, run-03/f2-m03, run-03/f2-m04, run-03/f2-m05, run-03/f2-m06, run-04/f2-m01, run-04/f2-m02, run-04/f2-m03, run-04/f2-m05, run-04/f2-m06, run-05/f2-m01, run-05/f2-m02, run-05/f2-m03, run-05/f2-m04, run-05/f2-m05, run-05/f2-m06, run-06/f2-m01, run-06/f2-m02, run-06/f2-m03, run-06/f2-m05, run-06/f2-m06, run-07/f2-m01, run-07/f2-m02, run-07/f2-m04, run-07/f2-m05, run-07/f2-m06, run-08/f2-m01, run-08/f2-m02, run-08/f2-m03, run-08/f2-m04, run-08/f2-m06, r5-m03-rival, r6-account-rival, r6-m06, r7-m05, r7-m07, r7-m08, r7-m09.


### m22: Olmo-3-1025-7B base (untrained); cue; hard72 (the 72 harder problems in the RL training prompts), n 72: all (base only)

GPU minutes 115 (proposers' guess). Separation 0 pairs, 0 per minute. Job `run_cell.py`.

Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "cue", "set": "hard72 (the 72 harder problems in the RL training prompts)", "n": "72: all", "sampling": "T 1.0, top-p 1.0, min-p 0; seed 3,700,000 + problem index (new seeds)", "samples": "3 new per problem, no restarts; combined with the 4 stored base + cue samples of these problems (studies/rlneurons/results/seen/, attempt 0) for 7 votes", "grader": "v3, answers grouped with rln4_lib.agree", "cap": "16,384"}

Command: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set hard72 --temperature 1.0 --top-p 1.0 --seed 3700000 --samples 3 --commit $(git rev-parse HEAD)"`


#### m22-r1: right answers of the plurality vote over 7 samples per problem (3 new rows + 4 stored attempt-0 rows; cap hits cast no vote; ties to the lowest sample) (problems of 72)

Best known base count given to the forecasters: 18 (result-5c961a; No base-only count with 7 samples exists on hard72. Scaled: base + cue vote over 4 on hard328 is 192 against 160.5 per sample (ratio 1.20), applied to the 15 per sample on the 72 (result-066c9b), gives about 18). Highest forecast: run-07/f2-m04 21 (+3).

- proposed by run-06/f2-m04 (c22): 20 [17, 23]; says run-04/f2-m01 gives 25 (its blind forecast: 20). The cued base gets 15 of these 72 per sample (20.8 %, result-066c9b), and on hard sets pass@4 is about 1.45 times one sample, about 22. f2-m04 says the vote has removed the slips by 5-7 samples and then sits at the modal-right count, a few below pass@4: about 20. run-04/f2-m01 says the base's wrong answers scatter, so a right answer drawn in only a quarter of samples still wins and each added sample keeps resolving problems: by 7 votes it passes pass@4, about 25.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 18 | [12, 24] |  |
| reader-2 | reader-2 | 19 | [13, 25] |  |
| run-03/f2-m01 | run-03 | 20 | [15, 25] |  |
| run-04/f2-m01 | run-04 | 20 | [14, 26] |  |
| run-04/f2-m02 | run-04 | 18.5 | [13, 24] |  |
| run-04/f2-m04 | run-04 | 19 | [13, 25] |  |
| run-04/f2-m06 | run-04 | 19 | [13, 25] |  |
| run-06/f2-m04 | run-06 | 19 | [14, 24] |  |
| run-07/f2-m04 | run-07 | 21 | [15, 27] |  |
| run-08/f2-m05 | run-08 | 16 | [11, 21] |  |
| run-08/f2-m06 | run-08 | 18 | [13, 24] |  |

Theory says nothing: run-03/f2-m02, run-03/f2-m03, run-03/f2-m04, run-03/f2-m05, run-03/f2-m06, run-04/f2-m03, run-04/f2-m05, run-05/f2-m01, run-05/f2-m02, run-05/f2-m03, run-05/f2-m04, run-05/f2-m05, run-05/f2-m06, run-06/f2-m01, run-06/f2-m02, run-06/f2-m03, run-06/f2-m05, run-06/f2-m06, run-07/f2-m01, run-07/f2-m02, run-07/f2-m03, run-07/f2-m05, run-07/f2-m06, run-08/f2-m01, run-08/f2-m02, run-08/f2-m03, run-08/f2-m04, r5-m03-rival, r6-account-rival, r6-m06, r7-m05, r7-m07, r7-m08, r7-m09, r7-m11.


### m37: allenai/Olmo-3-1025-7B (untrained base), context-contrast decoding: softmax(3 * logit(with problem) - 2 * logit(problem text deleted, same answer prefix)), i.e. --alpha 2 (result-a497ff used alpha 1, softmax(2l - l_noprob)); cue; each request = the stored cued-base answer of a wrongstep item cut at the token before its located wrong step; the 51 located wrong-step items of studies/rlneurons/results/wrongstep/math500-01 (MATH-500, cued base, job abaybektursun-1114-153825-208b), n 51 items; readout on the 35 items labelled misread (14) or slip (21) (base only)

GPU minutes 60 (proposers' guess). Separation 0 pairs, 0 per minute. Job `prefix_cell.py`.

Cell: {"model": "allenai/Olmo-3-1025-7B (untrained base), context-contrast decoding: softmax(3 * logit(with problem) - 2 * logit(problem text deleted, same answer prefix)), i.e. --alpha 2 (result-a497ff used alpha 1, softmax(2l - l_noprob))", "prompt": "cue; each request = the stored cued-base answer of a wrongstep item cut at the token before its located wrong step", "set": "the 51 located wrong-step items of studies/rlneurons/results/wrongstep/math500-01 (MATH-500, cued base, job abaybektursun-1114-153825-208b)", "n": "51 items; readout on the 35 items labelled misread (14) or slip (21)", "sampling": "T 1.0, top-p 1.0, min-p 0; seeds 5,000,000 + 10*item + k", "samples": "4 continuations per item (--k 4), no restarts", "grader": "v3 on prefix + continuation", "cap": "4,000 new tokens per continuation"}

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.prefix_cell --rows /runs/abaybektursun-1114-153825-208b/answers.jsonl --labels studies/rlneurons/results/wrongstep/math500-01/items.json --model base --alpha 2.0 --k 4 --cap 4000 --seed 5000000`


#### m37-r1: right continuations (v3, cap hits wrong unless a gradable answer is present, as in result-a497ff) among the 140 continuations of the misread- and slip-labelled items (right of 140)

Best known base count given to the forecasters: 65 (result-a497ff; no count exists on these 140 continuations. Scaled from the alpha-1 problem-contrast arm (6 continuations per item, cap 4,000): misreads 36 of 84, slips unchanged at the base's 49 % of 126. Times 4/6, that is 24 + 41 = 65 of 140.). Highest forecast: r7-m05 68 (+3).

- proposed by r7-m05 (c40): 74 [62, 86]; says run-07/f2-m03 gives 56 (its blind forecast: 59). r7-m05 says misreads and slips are the problem-free prior's continuation, so a stronger contrast against the problem-free context lowers both: misreads rise from 32 % (no contrast) past alpha 1's 43 % to about 50 %, and slips rise from 49 % to about 55 %. f2-m03 says a misreading is set up by the problem's wording, which the contrast amplifies, so misreads stay at or below 0.32 * 56 and slips stay at their chance rate (0.49 * 84). That gives about 56.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 60 | [46, 74] |  |
| reader-2 | reader-2 | 61 | [46, 75] |  |
| run-06/f2-m04 | run-06 | 59 | [47, 71] |  |
| run-07/f2-m03 | run-07 | 59 | [48, 70] |  |
| r7-m05 | round-07 | 68 | [54, 82] |  |

Theory says nothing: run-03/f2-m01, run-03/f2-m02, run-03/f2-m03, run-03/f2-m04, run-03/f2-m05, run-03/f2-m06, run-04/f2-m01, run-04/f2-m02, run-04/f2-m03, run-04/f2-m04, run-04/f2-m05, run-04/f2-m06, run-05/f2-m01, run-05/f2-m02, run-05/f2-m03, run-05/f2-m04, run-05/f2-m05, run-05/f2-m06, run-06/f2-m01, run-06/f2-m02, run-06/f2-m03, run-06/f2-m05, run-06/f2-m06, run-07/f2-m01, run-07/f2-m02, run-07/f2-m04, run-07/f2-m05, run-07/f2-m06, run-08/f2-m01, run-08/f2-m02, run-08/f2-m03, run-08/f2-m04, run-08/f2-m05, run-08/f2-m06, r5-m03-rival, r6-account-rival, r6-m06, r7-m07, r7-m08, r7-m09, r7-m11.


### m34: Olmo-3-1025-7B base, untrained; cue; hard328, n 82 problems: shard 0/4 (indices 0, 4, 8, ..., 324) (base only)

GPU minutes 100 (proposers' guess). Separation 0 pairs, 0 per minute. Job `run_cell.py`.

Cell: {"model": "Olmo-3-1025-7B base, untrained", "prompt": "cue", "set": "hard328", "n": "82 problems: shard 0/4 (indices 0, 4, 8, ..., 324)", "sampling": "T 1.0, top-p 1.0, min-p 0; seed 3100000 + problem index (new seeds, independent of the stored 4)", "samples": "3 new per problem, no restarts; read together with the 4 stored attempt-0 samples of hard328_base_cue_s4r2-01", "grader": "v3; vote by plurality with rln4_lib.agree, ties to the lowest sample", "cap": "16,384 generated tokens"}

Command: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set hard328 --shard 0/4 --samples 3 --temperature 1.0 --top-p 1.0 --seed 3100000 --commit $(git rev-parse HEAD)"`


#### m34-r1: right answers of the 82 under a vote over 7 (3 new samples + the 4 stored attempt-0 samples), grader v3 (problems of 82)

Best known base count given to the forecasters: 49.75 (result-389164; No base-only cell has 7 samples on hard328; best base-only count is 199/328 (vote over 4 after restart, ties to the shortest), scaled to 82 problems.). Highest forecast: run-04/f2-m01 52 (+2.25).

- proposed by run-08/f2-m05 (c35): 50 [46.5, 53]; says run-04/f2-m01 gives 55 (its blind forecast: 52). f2-m05: the vote rises toward the number of problems whose right answer is the modal string, well below pass@k, and returns shrink fast after k = 4 (vote over 4 is 192/328 = 48 of 82, pass@4 207/328 = 52), so odd k = 7 adds about 2 from broken ties. run-04/f2-m01 says scattered wrong answers let each added sample keep resolving problems with p of 0.25-0.4 until only near-zero-p problems remain, so the vote over 7 climbs to about pass@7 less the near-zero problems, about 55.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 49.5 | [42, 57] |  |
| reader-2 | reader-2 | 49 | [42, 56] |  |
| run-03/f2-m01 | run-03 | 50 | [44, 56] |  |
| run-04/f2-m01 | run-04 | 52 | [46, 58] |  |
| run-04/f2-m02 | run-04 | 49 | [43, 55] |  |
| run-04/f2-m04 | run-04 | 50 | [44, 56] |  |
| run-04/f2-m06 | run-04 | 50 | [44, 56] |  |
| run-06/f2-m04 | run-06 | 50 | [45, 55] |  |
| run-07/f2-m04 | run-07 | 52 | [46, 58] |  |
| run-07/f2-m06 | run-07 | 51 | [45, 57] |  |
| run-08/f2-m05 | run-08 | 49 | [44, 55] |  |
| run-08/f2-m06 | run-08 | 51 | [45, 57] |  |

Theory says nothing: run-03/f2-m02, run-03/f2-m03, run-03/f2-m04, run-03/f2-m05, run-03/f2-m06, run-04/f2-m03, run-04/f2-m05, run-05/f2-m01, run-05/f2-m02, run-05/f2-m03, run-05/f2-m04, run-05/f2-m05, run-05/f2-m06, run-06/f2-m01, run-06/f2-m02, run-06/f2-m03, run-06/f2-m05, run-06/f2-m06, run-07/f2-m01, run-07/f2-m02, run-07/f2-m03, run-07/f2-m05, run-08/f2-m01, run-08/f2-m02, run-08/f2-m03, run-08/f2-m04, r5-m03-rival, r6-account-rival, r6-m06, r7-m05, r7-m07, r7-m08, r7-m09, r7-m11.


### m07: Olmo-3-1025-7B base (untrained); cue; hard328, n 60: the first 60 problems of hard328 (--n 60) (base only)

GPU minutes 113 (proposers' guess). Separation 0 pairs, 0 per minute. Job `run_cell.py`.

Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "cue", "set": "hard328", "n": "60: the first 60 problems of hard328 (--n 60)", "sampling": "T 1.0, top-p 1.0, min-p 0; seed 3500000 + index (new seeds, disjoint from the stored seed-3000000 rows)", "samples": "4 per problem, no restarts; voted together with the 4 stored attempt-0 samples of the same 60 problems (job e8e6, results/day1_3/hard328_base_cue_s4r2-01)", "grader": "v3", "cap": "16,384"}

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set hard328 --temperature 1.0 --top-p 1.0 --seed 3500000 --n 60 --samples 4 --restarts 0 --commit $(git rev-parse HEAD)`


#### m07-r1: right answers of 60 under a plurality vote over 8 samples (the 4 new + the 4 stored attempt-0 samples), answers grouped with rln4_lib.agree, cap hits cast no vote, ties to the lowest sample index (right answers of 60)

Best known base count given to the forecasters: 36.4 (result-389164; No base-only cell has 8 samples on these problems. Best base on the 328 is vote over 4 after restart with ties to the shortest, 199/328 (4 samples plus restarts), scaled to 60 problems: 36.4.). Highest forecast: run-04/f2-m01 38 (+1.6).

- proposed by run-04/f2-m01 (c07): 37.1 [35.5, 39.5]; says r7-m11 gives 35 (its blind forecast: nothing). f2-m01 has wrong answers scattering, so samples 5-8 keep turning problems with p of 0.25-0.4 into plurality wins: 192 at k=4 rises toward 203 of 328 (pass@4 207), i.e. 37.1 of 60. r7-m11 has the shared prompt and opening produce agreeing wrong groups that grow with k, so the 8-vote stays at the 4-vote's 192/328 (35.0 of 60) or below.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 36.5 | [29, 44] |  |
| reader-2 | reader-2 | 36 | [30, 42] |  |
| run-03/f2-m01 | run-03 | 36 | [30, 42] |  |
| run-04/f2-m01 | run-04 | 38 | [32, 44] |  |
| run-04/f2-m02 | run-04 | 36 | [30, 42] |  |
| run-04/f2-m04 | run-04 | 37 | [31, 43] |  |
| run-04/f2-m06 | run-04 | 37 | [31, 43] |  |
| run-06/f2-m04 | run-06 | 35.5 | [31, 40] |  |
| run-07/f2-m04 | run-07 | 38 | [32, 44] |  |
| run-07/f2-m06 | run-07 | 37 | [31, 43] |  |
| run-08/f2-m05 | run-08 | 36 | [31, 41] |  |
| run-08/f2-m06 | run-08 | 37 | [32, 43] |  |

Theory says nothing: run-03/f2-m02, run-03/f2-m03, run-03/f2-m04, run-03/f2-m05, run-03/f2-m06, run-04/f2-m03, run-04/f2-m05, run-05/f2-m01, run-05/f2-m02, run-05/f2-m03, run-05/f2-m04, run-05/f2-m05, run-05/f2-m06, run-06/f2-m01, run-06/f2-m02, run-06/f2-m03, run-06/f2-m05, run-06/f2-m06, run-07/f2-m01, run-07/f2-m02, run-07/f2-m03, run-07/f2-m05, run-08/f2-m01, run-08/f2-m02, run-08/f2-m03, run-08/f2-m04, r5-m03-rival, r6-account-rival, r6-m06, r7-m05, r7-m07, r7-m08, r7-m09, r7-m11.


### m25: Olmo-3-1025-7B base (untrained); cue; MATH-500, n 500 (all) (base only)

GPU minutes 110 (proposers' guess). Separation 0 pairs, 0 per minute. Job `run_cell.py`.

Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "cue", "set": "MATH-500", "n": "500 (all)", "sampling": "T 1.0, top-p 1.0, min-p 0; problem i seeded 101000000 + i", "samples": "1 per problem, no restarts", "grader": "v3", "cap": "32,768 generated tokens (each answer also scored as if cut at 16,384)"}

Command: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set math500 --temperature 1.0 --top-p 1.0 --max-tokens 32768 --seed 101000000 --commit $(git rev-parse HEAD)"`


#### m25-r1: Right answers (grader v3) among answers longer than 16,384 generated tokens, i.e. the problems a 16,384 cap would have cut, counted from answers.jsonl (n_generated > 16384, score_v3 == 1) (problems of 500)

Best known base count given to the forecasters: 10 (result-0c1eef; No base-only cell has a count of right answers past 16,384 on MATH-500. Closest base-only cap-32,768 cell is hard328 (4 right of 64 long answers); the T1 cell's 27 cap hits at 16,384 bound the count at 27. Value given is this cell's own forecast, since no comparable count exists; best whole-set base-only count with one sample is 414/500 (result-e870a1).). Highest forecast: run-07/f2-m01 11 (+1).

- proposed by run-07/f2-m01 (c25): 10 [6, 15]; says run-03/f2-m03 gives 2 (its blind forecast: 3). f2-m01 says a converted cut answer is right at the rate the model reaches on MATH-500's long tail, about 45 %, so ~22-27 cut answers (T1 had 27 cap hits) give ~10 right. run-03/f2-m03 says the base closes long answers with asserted numbers, so extra budget gains it little: at its measured hard328 rate (4 right of 64 finished past 16,384, result-0c1eef) that is ~1.5-2.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 3 | [0, 7] |  |
| reader-2 | reader-2 | 4 | [1, 9] |  |
| run-03/f2-m03 | run-03 | 3 | [0, 7] |  |
| run-04/f2-m01 | run-04 | 6 | [2, 11] |  |
| run-04/f2-m05 | run-04 | 4 | [1, 9] |  |
| run-07/f2-m01 | run-07 | 11 | [6, 17] |  |
| run-08/f2-m02 | run-08 | 3 | [0, 7] |  |
| r6-account-rival | round-07 | 3 | [0, 8] |  |

Theory says nothing: run-03/f2-m01, run-03/f2-m02, run-03/f2-m04, run-03/f2-m05, run-03/f2-m06, run-04/f2-m02, run-04/f2-m03, run-04/f2-m04, run-04/f2-m06, run-05/f2-m01, run-05/f2-m02, run-05/f2-m03, run-05/f2-m04, run-05/f2-m05, run-05/f2-m06, run-06/f2-m01, run-06/f2-m02, run-06/f2-m03, run-06/f2-m04, run-06/f2-m05, run-06/f2-m06, run-07/f2-m02, run-07/f2-m03, run-07/f2-m04, run-07/f2-m05, run-07/f2-m06, run-08/f2-m01, run-08/f2-m03, run-08/f2-m04, run-08/f2-m05, run-08/f2-m06, r5-m03-rival, r6-m06, r7-m05, r7-m07, r7-m08, r7-m09, r7-m11.


### m08: Olmo-3-1025-7B base (untrained); cue; math500, n 167: every third MATH-500 problem, indices 0, 3, ..., 498 (--shard 0/3) (base only)

GPU minutes 100 (proposers' guess). Separation 0 pairs, 0 per minute. Job `run_cell.py`.

Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "cue", "set": "math500", "n": "167: every third MATH-500 problem, indices 0, 3, ..., 498 (--shard 0/3)", "sampling": "T 1.0, top-p 1.0, min-p 0; seed 81000000 + index (new seeds)", "samples": "3 per problem, no restarts", "grader": "v3", "cap": "16,384"}

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set math500 --temperature 1.0 --top-p 1.0 --seed 81000000 --shard 0/3 --samples 3 --restarts 0 --commit $(git rev-parse HEAD)`


#### m08-r1: right answers of 167 under a plurality vote over the 3 samples (rln4_lib.agree grouping, cap hits cast no vote, ties to the lowest sample index) (right answers of 167)

Best known base count given to the forecasters: 151.6 (result-40ed3b; No base-only cell has 3 samples. Best base on MATH-500 is 454/500 (vote over 4 after restart, ties to the shortest; 4 samples plus restarts), scaled to these 167 problems: 151.6. The plain 4-vote, 446/500, scales to 149.0.). Highest forecast: run-04/f2-m02 149 (-2.6).

- proposed by run-04/f2-m02 (c08): 149 [146.5, 151.5]; says run-06/f2-m04 gives 146.3 (its blind forecast: 145). In f2-m02 an even k only adds a random tie-break to the odd k before it, so a 3-vote is already at the 4-vote's level (446/500 = 149.0 of 167). In run-06/f2-m04 slips are removed smoothly up to 5-7 samples, so the 3-vote sits about 8/500 under the 4-vote (438/500 = 146.3 of 167).

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 147 | [140, 154] |  |
| reader-2 | reader-2 | 146 | [139, 153] |  |
| run-03/f2-m01 | run-03 | 148 | [141, 155] |  |
| run-04/f2-m01 | run-04 | 148 | [142, 154] |  |
| run-04/f2-m02 | run-04 | 149 | [143, 154] |  |
| run-04/f2-m04 | run-04 | 147 | [141, 153] |  |
| run-06/f2-m04 | run-06 | 145 | [139, 151] |  |
| run-07/f2-m03 | run-07 | 147 | [141, 152] |  |
| run-07/f2-m04 | run-07 | 146 | [140, 152] |  |
| run-08/f2-m05 | run-08 | 147.5 | [142, 153] |  |
| run-08/f2-m06 | run-08 | 147 | [141, 153] |  |
| r7-m11 | round-07 | 146 | [140, 151] |  |

Theory says nothing: run-03/f2-m02, run-03/f2-m03, run-03/f2-m04, run-03/f2-m05, run-03/f2-m06, run-04/f2-m03, run-04/f2-m05, run-04/f2-m06, run-05/f2-m01, run-05/f2-m02, run-05/f2-m03, run-05/f2-m04, run-05/f2-m05, run-05/f2-m06, run-06/f2-m01, run-06/f2-m02, run-06/f2-m03, run-06/f2-m05, run-06/f2-m06, run-07/f2-m01, run-07/f2-m02, run-07/f2-m05, run-07/f2-m06, run-08/f2-m01, run-08/f2-m02, run-08/f2-m03, run-08/f2-m04, r5-m03-rival, r6-account-rival, r6-m06, r7-m05, r7-m07, r7-m08, r7-m09.


### m20: Olmo-3-1025-7B base (untrained); plain; fresh2026 (136 competition problems published in 2026), n 136: all (base only)

GPU minutes 50 (proposers' guess). Separation 3 pairs, 0.06 per minute. Job `run_fresh.py`.

Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "plain", "set": "fresh2026 (136 competition problems published in 2026)", "n": "136: all", "sampling": "T 1.0, top-p 1.0, min-p 0; seed 93,000,000 + problem index", "samples": "1 per problem, no restarts", "grader": "v3", "cap": "16,384 (frozen4 default)"}

Command: `uv run tools/gpu.py submit l40s --hours 1.5 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_fresh --model base --prompt plain --set fresh2026 --temperature 1.0 --top-p 1.0 --seed 93000000 --commit $(git rev-parse HEAD)"`


#### m20-r1: right answers with grader v3 (metrics.json right_v3) (problems of 136)

Best known base count given to the forecasters: 29.5 (result-5251c9; base + cue, one sample, mean of 4 samples on the same 136 problems (vote over 4 is 38); no other base-only cell exists on fresh2026). Highest forecast: run-07/f2-m06 16 (-13.5).

- proposed by run-06/f2-m02 (c20): 2 [0, 5]; says run-07/f2-m06 gives 14 (its blind forecast: 16). f2-m02 fixes the cue's share of RL's gain at 55-78 %; on fresh2026 the cued base gets 29.5 and RL 50.5 per sample (result-5251c9), and share = (29.5 - p)/(50.5 - p) >= 0.55 forces the plain base to p <= 4. run-07/f2-m06 says fresh2026's thin middle band compresses every gain, the cue's included, so the plain base sits nearer the cued base than on hard328 (76 of 164 there, ratio 0.46): about half of 29.5.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 14 | [7, 22] |  |
| reader-2 | reader-2 | 13 | [6, 21] |  |
| run-06/f2-m02 | run-06 | 3 | [0, 8] | run-07/f2-m06 |
| run-06/f2-m06 | run-06 | 2 | [0, 7] | run-07/f2-m06, run-08/f2-m01 |
| run-07/f2-m06 | run-07 | 16 | [9, 23] | run-06/f2-m02, run-06/f2-m06 |
| run-08/f2-m01 | run-08 | 14 | [8, 20] | run-06/f2-m06 |

Theory says nothing: run-03/f2-m01, run-03/f2-m02, run-03/f2-m03, run-03/f2-m04, run-03/f2-m05, run-03/f2-m06, run-04/f2-m01, run-04/f2-m02, run-04/f2-m03, run-04/f2-m04, run-04/f2-m05, run-04/f2-m06, run-05/f2-m01, run-05/f2-m02, run-05/f2-m03, run-05/f2-m04, run-05/f2-m05, run-05/f2-m06, run-06/f2-m01, run-06/f2-m03, run-06/f2-m04, run-06/f2-m05, run-07/f2-m01, run-07/f2-m02, run-07/f2-m03, run-07/f2-m04, run-07/f2-m05, run-08/f2-m02, run-08/f2-m03, run-08/f2-m04, run-08/f2-m05, run-08/f2-m06, r5-m03-rival, r6-account-rival, r6-m06, r7-m05, r7-m07, r7-m08, r7-m09, r7-m11.


### m36: allenai/Olmo-3-1025-7B (untrained base); cue; math500, n 500, all problems (base only)

GPU minutes 100 (proposers' guess). Separation 0 pairs, 0 per minute. Job `run_cell.py`.

Cell: {"model": "allenai/Olmo-3-1025-7B (untrained base)", "prompt": "cue", "set": "math500", "n": "500, all problems", "sampling": "T 1.0, top-p 1.0, min-p 0.01 (cuts only tokens below 1 % of the top token's probability); problem i seeded 41,000,000 + i", "samples": "1 per problem, no restarts", "grader": "v3", "cap": "16,384 generated tokens"}

Command: `bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set math500 --temperature 1.0 --top-p 1.0 --min-p 0.01 --seed 41000000 --commit $(git rev-parse HEAD)`


#### m36-r1: right answers with grader v3 (metrics.json; cap hits wrong) (right of 500)

Best known base count given to the forecasters: 430 (result-882fa7; best one-sample base-only count on all 500 MATH-500 problems: cue, T 1.0, no steering, in-process eager vLLM (its author reads it as a high draw; the next best are 421 with a logit bias, same item, and 415 for the T 0.6 loop-neuron edit, result-932df7)). Highest forecast: reader-1 410 (-20).

- proposed by r6-m06 (c39): 409 [397, 421]; says run-06/f2-m04 gives 424 (its blind forecast: nothing). r6-m06 puts the base's wrong steps in the head of its distribution, so cutting the deep tail leaves the score at the untruncated cue level (405-418, mean 410.5), minus a little for loops. f2-m04 makes the base's errors chance slips drawn independently at each step. A cut that removes low-probability draws then removes about half of the ~31 slip-type wrong answers (35 % of ~90), giving about +15 before a small loop cost.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 410 | [398, 422] |  |
| reader-2 | reader-2 | 410 | [396, 424] |  |
| run-04/f2-m04 | run-04 | 410 | [400, 420] |  |
| run-08/f2-m01 | run-08 | 410 | [400, 420] |  |
| r6-m06 | round-07 | 409 | [396, 421] |  |

Theory says nothing: run-03/f2-m01, run-03/f2-m02, run-03/f2-m03, run-03/f2-m04, run-03/f2-m05, run-03/f2-m06, run-04/f2-m01, run-04/f2-m02, run-04/f2-m03, run-04/f2-m05, run-04/f2-m06, run-05/f2-m01, run-05/f2-m02, run-05/f2-m03, run-05/f2-m04, run-05/f2-m05, run-05/f2-m06, run-06/f2-m01, run-06/f2-m02, run-06/f2-m03, run-06/f2-m04, run-06/f2-m05, run-06/f2-m06, run-07/f2-m01, run-07/f2-m02, run-07/f2-m03, run-07/f2-m04, run-07/f2-m05, run-07/f2-m06, run-08/f2-m02, run-08/f2-m03, run-08/f2-m04, run-08/f2-m05, run-08/f2-m06, r5-m03-rival, r6-account-rival, r7-m05, r7-m07, r7-m08, r7-m09, r7-m11.


### m28: Olmo-3-1025-7B base (untrained); plain; hard328 (contest problems, integer answers mostly), n 100 (the first 100 problems, --n 100) (base only)

GPU minutes 85 (proposers' guess). Separation 0 pairs, 0 per minute. Job `run_cell.py`.

Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "plain", "set": "hard328 (contest problems, integer answers mostly)", "n": "100 (the first 100 problems, --n 100)", "sampling": "T 1.0, top-p 1.0, min-p 0; problem i seeded 104000000 + i", "samples": "4 per problem, no restarts", "grader": "v3; vote = plurality over extracted answers (rln4_lib.agree), samples with no answer abstain, ties to the lowest sample", "cap": "16,384"}

Command: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt plain --set hard328 --temperature 1.0 --top-p 1.0 --seed 104000000 --n 100 --samples 4 --restarts 0 --commit $(git rev-parse HEAD)" && uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_vote --run runs/<job> --out studies/rlneurons/results/day1_3/hard328_base_plain_first100-01`


#### m28-r1: Right answers under the vote over 4, grader v3 (problems of 100)

Best known base count given to the forecasters: 59 (result-5c961a; Best base-only count with 4 samples on hard328: base + cue, vote over 4 after restart, 195 of 328 (192 without restart). Scaled to 100 problems (195 x 100/328 = 59.5); the board has no count on the first 100 alone.). Highest forecast: run-06/f2-m02 33 (-26).

- proposed by run-07/f2-m04 (c28): 32 [26, 38]; says run-03/f2-m01 gives 24 (its blind forecast: 27). Plain base single on hard328 is 76/328 (~23 of 100) and it seldom hits the cap (4,928 tokens per answer). f2-m04: contest answers are wide-range integers, so wrong answers scatter and a right answer at modest per-sample probability wins, giving a vote/single ratio at least the cued base's (1.19-1.29), ~32. run-03/f2-m01: the vote's gain comes from the cap discarding wrong answers; a model that finishes casts its guesses as votes, so the plain base gains least, ~24.

| forecaster | family | value | 90 % interval | does not overlap with |
|---|---|---|---|---|
| reader-1 | reader-1 | 29 | [20, 39] |  |
| reader-2 | reader-2 | 31 | [21, 42] |  |
| run-03/f2-m01 | run-03 | 27 | [20, 35] |  |
| run-04/f2-m02 | run-04 | 29 | [20, 38] |  |
| run-04/f2-m06 | run-04 | 28 | [20, 36] |  |
| run-06/f2-m02 | run-06 | 33 | [25, 42] |  |
| run-06/f2-m04 | run-06 | 31 | [23, 39] |  |
| run-07/f2-m04 | run-07 | 32 | [24, 40] |  |
| run-07/f2-m06 | run-07 | 31 | [23, 39] |  |
| run-08/f2-m05 | run-08 | 25 | [18, 33] |  |
| run-08/f2-m06 | run-08 | 24 | [17, 32] |  |

Theory says nothing: run-03/f2-m02, run-03/f2-m03, run-03/f2-m04, run-03/f2-m05, run-03/f2-m06, run-04/f2-m01, run-04/f2-m03, run-04/f2-m04, run-04/f2-m05, run-05/f2-m01, run-05/f2-m02, run-05/f2-m03, run-05/f2-m04, run-05/f2-m05, run-05/f2-m06, run-06/f2-m01, run-06/f2-m03, run-06/f2-m05, run-06/f2-m06, run-07/f2-m01, run-07/f2-m02, run-07/f2-m03, run-07/f2-m05, run-08/f2-m01, run-08/f2-m02, run-08/f2-m03, run-08/f2-m04, r5-m03-rival, r6-account-rival, r6-m06, r7-m05, r7-m07, r7-m08, r7-m09, r7-m11.


## Checked by hand (2026-11-15, after the run; no cell dropped)

Only 4 of 41 merged cells have any pair of forecasters from different families with intervals that do not overlap
(m20, m29, m33, m06); every other cell has separation 0, so list A below rank 4 is ordered by ties.

| cell | board already answers it? | command as written |
|---|---|---|
| m20 base, plain, fresh2026 136, 1 sample | No: the fresh2026 jobs ran the base with the cue only (result-5251c9: 29.5 per sample). Open. | runs (`run_fresh.py --model base --prompt plain`) |
| m29 base + RL-Math top 8 at 2x, cue, MATH-500 | No: 2x ran on hard328 only (190 of 328, below 203 at 1.5x); MATH-500 has 1.5x only (456, result-95a4dc). Open. | `wsp_edit --recipe topk` does not exist: the recipe is `top8` (`--recipe top8 --scale 2.0`) |
| m33 base + RL-Math top 8 at 2x on HumanEval+ / MBPP+, answers with no code block | Mostly: Math's directions at 1.5x leave 6 of 538 without a code block, Code's at 2x 0 (result-a1bf75, README "The dial on a second model pair"); the proposer's 45 [32, 62] runs against that trend. | `--recipe topk` -> `top8`; the cue ids are a placeholder |
| m06 RL step 100, plain, first 164 of hard328, quick finished-wrong answers | No: step 100 ran on MATH-500 only (418 plain, README "Released RL checkpoints"). Open. | `--model s0100` is not a choice of `run_cell.py` (base, rl): download revision `step_0100` and pass `--model-path`, as the ckptcue cells did |
| m01 RL plain, hard328 first 200, 3 samples, cap 8,192 (separation 0) | No such cell on the board. | runs |

Base-only list B: every "best known base count" is the proposer's scaled estimate, not a measured count at the same
number of samples, and every top forecast lies inside both readers' intervals. m41 (3 base-written examples in
context): the board already reports that the shots gain does not survive a second draw or the 328 (result-6d422d,
result-5227b9). m37 (problem-contrast decoding at alpha 2): alpha 1 added no right answers (+1.6 points [-4.2, 7.8],
result-a497ff). m22 (base vote over 7 on hard72): open.
