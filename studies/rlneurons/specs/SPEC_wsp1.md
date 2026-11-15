# WSP-1: anatomy of three weight deltas on the Olmo 3 base, then a no-reward delta scaled into the base

Written 2026-11-14 before any run. Board: work-f374ef, idea-d59a98, idea-2eb58d. The a-sweep of the RL delta itself
(base + a*(RL - base), Code-RL and random controls, scored on MATH-500) is work-d36669 on branch `wdiff` and is not repeated here.

## Question

The cued base scores 410 of 500 on MATH-500 at T 1.0 and the RL model 463 (README "Established numbers"). Two parts:

1. Interpretability, weights only: what did RL write into the weights, and does a delta made with no reward point the same way?
2. Score: does base + a*(Think-SFT - base), a delta made by imitation only, raise the cued base above 410?

## Models (Hugging Face API, 2026-11-14; all 355 tensors, BF16, same shapes)

| Key | Repo | Revision | Made by |
|---|---|---|---|
| `base` | `allenai/Olmo-3-1025-7B` | `a81bae42db3975be1671e27b9c9a56da1a9f980f` | pretraining |
| `rl_math` | `allenai/Olmo-3.1-7B-RL-Zero-Math` | `364820b002fc8e81d11a81c7fc9dd6b49c83cd05` | RL, math reward, step 2,800 |
| `rl_code` | `allenai/Olmo-3.1-7B-RL-Zero-Code` | `1ca3bb30f0e51b7ef05f7d0fefcf0e6b14eefc90` | RL, code reward |
| `think_sft` | `allenai/Olmo-3-7B-Think-SFT` | `6ff857587e040d6d523a3d5f3a56e918f5401d66` | SFT on reasoning traces, no reward |

A delta is `model - base`, computed per tensor in float32 (exact for two BF16 tensors).

## Part 1: `jobs/wsp_delta_anatomy.py` (one H100 job, no forward pass through the model)

Per tensor and per delta: Frobenius norm of the delta and of the base tensor, their ratio, the share of entries that are
bitwise equal to the base. Per 2-D tensor in the layers (q, k, v, o, gate, up, down; not the embeddings): all singular values
of the delta (share of squared norm in the top 1 and top 8, stable rank = squared norm / top singular value squared), and
the top 8 left and right singular vectors.

Per pair of deltas and per tensor: cosine (Frobenius inner product over the two norms); for 2-D layer tensors the overlap of
the top-8 left subspaces, `||U1^T U2||_F^2 / 8`, and the same for the right subspaces.

Readout: for each layer's `mlp.down_proj` and `self_attn.o_proj` (the two tensors that write to the residual stream), the
top 3 left singular vectors `u` of each delta, both signs, multiplied by the base `lm_head`: the 15 tokens with the highest
logit, decoded with the RL tokenizer. Also the rank of the three cue tokens (ids 1584, 2268, 33413) in each readout.

Null, computed in the same job by the same code: for one tensor of each shape, a Gaussian delta with the RL delta's norm
gives the null cosine, null top-1 and top-8 share, null stable rank, null subspace overlap and a null readout.

Instrument check (`--selftest`, laptop, synthetic 64 x 48 tensors, no weights): a planted rank-1 delta must return top-1
share above 0.99; two equal deltas cosine 1 and overlap 1; two independent Gaussian deltas |cosine| below 0.1; a delta
planted along one unembedding row must read out that token first. The job refuses to run if the selftest fails.

Output, `results/wsp1/anatomy-<nn>/`: `run.json`, `metrics.json` (per tensor), `summary.json` (means by module type and by
layer, the nulls), `readout.json`.

### Hypotheses, each with the observation that refutes it

- H1, shared direction with no reward: cosine(rl_math, think_sft) is above the null in most layer tensors. Refuted if its
  mean over the 224 layer matrices is below 5 times the null's standard deviation.
- H2, RL deltas share a task-general part: mean cosine(rl_math, rl_code) is larger than mean cosine(rl_math, think_sft).
  Refuted if it is not.
- H3, RL change is concentrated: some layer matrix of rl_math has top-8 share above 0.5 (Wang et al. 2610.06851 App. D.4:
  55.9 % in two modes of their own LoRA update). Refuted if the largest top-8 share is below 3 times the null's.
- H4, the RL delta reads as the cue: a cue token is among the top 15 tokens of a top-3 direction of rl_math in layers
  24 to 31, and in no null readout. Refuted if no cue token appears.

## Part 2: scaled Think-SFT delta (after Part 1; uses the merge step of work-d36669 when it is pushed)

Cells: cue arm, MATH-500, T 1.0, top-p 1.0, seed 41000000 (the T1 seeds, so each cell pairs with T1's 410 by problem).
Scales: a = 1 (the delta as released), a = 0.5, and a_n = the scale at which the Think-SFT delta has the RL delta's total
norm (from Part 1). Both tokenizers stay the RL tokenizer, as in every cell of the study.

Refuted (no gain from an imitation delta) if no scale is above 410 by more than 17 problems (two standard errors of one
500-problem cell, 3.4 points). Each cell reports right of 500, cap hits, median tokens of right answers, and the count of
the 65 RL-only problems of `results/rln4/t1_t2_items-01/` it solves, by failure type.

Caveat stated with every number: Think-SFT was trained on solutions written by other models. It uses no reward; it does use
labelled traces.

## Amendment, 2026-11-14 23:55 UTC, after Part 1 and before any Part 2 run

Part 1 result (`results/wsp1/anatomy-01/`): H1 refuted (cosine of the Think-SFT delta with the RL-Math delta is -0.00001, and
the Think-SFT delta is 100 times larger), so the norm-matched scale a_n = 0.0097 is a random direction at RL's norm; that arm
is dropped (the random control of work-d36669 covers it). The RL-Math delta has 11.8 % of its squared norm in 8 directions per
matrix, and its late-MLP directions read as `Okay / consider / Wait / perhaps`. Part 2 now asks first whether those few
directions cause the RL gain.

`jobs/wsp_edit.py` writes an edited model directory for `run_cell.py --model-path` (rounding to BF16 by
`merge_weights.to_bf16`, stochastic, because most entries of a rank-8 part are below one BF16 unit in the last place).
Recipes, all relative to the base; "layer matrices" are the 224 q, k, v, o, gate, up, down tensors:

| Label | Weights | Asks |
|---|---|---|
| `top8` | base + the top 8 singular directions of each layer matrix's RL-Math delta; every other tensor = base | do 8 directions per matrix carry the gain? |
| `bulk` | RL-Math minus those top 8 directions (other tensors = RL-Math) | is the rest enough without them? |
| `rand8` | base + a rank-8 matrix per layer matrix with the same 8 singular values and random orthonormal vectors (seed 0) | matched control for `top8`: same norm, same rounding noise, no RL information |
| `late3` | base + the top 3 directions of `mlp.down_proj` in layers 24 to 31 only (24 rank-1 terms) | do the read-out directions alone change behaviour? |
| `sft1` | Think-SFT as released (a = 1, through the same path) | no-reward score arm |
| `sft05` | base + 0.5 (Think-SFT - base) | no-reward score arm |

Cells: the first 100 MATH-500 problems, T 1.0, top-p 1.0, one sample. Plain prompt, seed base 80,000,000: `base`, `rl`
(references on the same problems and seeds), `top8`, `bulk`, `rand8`, `late3`, `sft1`. Cue prompt, seed base 81,000,000:
`base` (reference), `sft1`, `sft05`. One cell has a standard error of about 5 points at n = 100; the plain base and RL differ
by 48 points on the 500 (224 against 463), which is what the dissection reads against.

Refuters. "The top 8 directions carry the gain" is refuted if `top8` plain is within 10 points of `rand8` plain, or if
`bulk` plain is within 10 points of `rl` plain while `top8` is not above `rand8`. "The read-out directions act alone" is
refuted if `late3` is within 10 points of `base` plain and its share of answers that open with the cue's `Okay` does not
differ from the base's. "An imitation delta raises the cued base" is refuted if neither `sft1` nor `sft05` with the cue is
above the cued base reference by more than 10 points. A cell that passes at n = 100 is rerun on all 500 before any claim.

Each cell also reports cap hits, median generated tokens, and the share of answers whose first 20 tokens contain `Okay`.

## Amendment 2, 2026-11-15 03:05 UTC, after the n = 100 screen and before the reruns

Screen (first 100 MATH-500 problems, T 1.0, right of 100): plain `base` 34, `rl` 96, `top8` 88, `bulk` 91, `rand8` 36,
`late3` 41, `sft1` 91; cue `base` 82, `sft1` 92, `sft05` 88. Read: 8 directions per matrix (9.8 % of the delta's squared
norm) are sufficient (88 against the matched control's 36) and not necessary (the rest alone gives 91); the 24 late-MLP
terms alone do little; Think-SFT as released is within 5 of RL.

Reruns on all 500 (rule of the first amendment), T 1.0, top-p 1.0, one sample: `top8` plain, seed base 180,000,000;
`sft1` cue, 181,000,000; `sft1` plain, 182,000,000. Compared by problem with T1 (410), T2 (463), T3 (224) and the
weight-difference line of `results/day1_wdiff/`.

New screens, plain, first 100, seed base 80,000,000 (same references): `top1` = `--recipe top8 --k 1` (one direction per
matrix), and `bulk64` = `--recipe bulk --k 64` (RL minus its top 64 directions per matrix). Predictions: `top1` is at
least 20 above `rand8` (36) if one direction per matrix is enough to switch the behaviour; `bulk64` is within 10 of `rl`
(96) if the change is spread over many more than 64 directions. Each is refuted by the opposite reading.

## Amendment 3, 2026-11-15 03:40 UTC

Reruns on all 500 (right of 500): `top8` plain 427, `sft1` cue 454, `sft1` plain 440. Added before it runs: `rand8` plain on
all 500, seed base 183,000,000, so that the matched control of `top8` exists at n = 500 as well. Prediction: within 5
points of the plain base (T3, 224 of 500); refuted if it is more than 10 points above it.

## Amendment 4, 2026-11-15 03:55 UTC: is the no-reward (Think-SFT) change also concentrated?

Full-500 result so far: `sft1` cue 454, +8.8 points over T1 [5.4, 12.4] and -1.8 against T2 [-4.2, 0.6]. New screens, first
100 problems, same seeds and references as the first screen: `sfttop8` and `sfttop64` plain (base + the top 8 or 64 singular
directions per layer matrix of the Think-SFT delta; `--recipe top8 --other think_sft --k 8|64`), `sft025` plain and cue
(base + 0.25 of the Think-SFT delta). Prediction from Part 1 (top-8 share 0.030 against RL's 0.118, no cue token in any
readout): the Think-SFT change is not concentrated, so `sfttop8` plain stays within 10 points of the plain base (34);
refuted if it is 20 or more above `rand8` (36). For comparison, a quarter of the RL delta gives 405 of 500 plain
(`results/day1_wdiff/`); `sft025` plain tests whether a quarter of the imitation delta does the same.
