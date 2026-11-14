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
