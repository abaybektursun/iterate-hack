# SPEC xreward: what do RL runs with different rewards write into the same base? (idea-ac4e14, work-4fa42e)

Written 2026-11-15 before the run. Weights only in Part 1; generation in Part 2.

## Question

Seven released RL-Zero models share the base `allenai/Olmo-3-1025-7B`: Math 3.1, Code 3.1, Math 3.0, Code 3.0, IF, General, Mix.
With the cue on MATH-500 (n 500, T 1.0, v3; result-edceef, result-4b0d5f) they score Math 3.1 457, Code 3.1 450, Math 3.0 448,
Mix 440, General 429, Code 3.0 411, IF 377, against base 410. WSP-1 (result-e2482e) found the top-8 subspaces of the Math 3.1 and
Code 3.1 differences overlap far above a random subspace, and also overlap with Think-SFT's on the input side.

Do the RL differences share a low-rank subspace per matrix, and does that subspace separate the models that gain on math from
those that do not?

## Part 1: overlap table (jobs/xreward_overlap.py, one job, about 10 minutes)

Per layer matrix (q, k, v, o, gate, up, down; 224 matrices) and per difference d = model - base, the top 8 left (output) and right
(input) singular vectors, by `wsp_delta_anatomy.spectrum`. Differences: the seven RL models, Think-SFT, and the base matrix itself
(`base_w`, as a reference for "the difference follows the base's own largest directions").

For every pair (a, b): cos; overlap_left = ||Ua^T Ub||_F^2 / 8, overlap_right the same with V; and for the ordered pair, the share
of a's squared norm inside b's subspace: cap_left = ||Ub^T da||^2 / ||da||^2, cap_right, cap_both = ||Ub^T da Vb||^2 / ||da||^2.

References: random 8-dimensional subspace, overlap 8 / dimension (0.002 for 4,096), stated analytically and checked in the selftest;
Think-SFT (fine-tuning without RL); `base_w`; ceiling Math 3.0 against Math 3.1 (same reward, two releases).

Hypotheses, each with the observation that refutes it:

- X1. RL differences share a subspace beyond what any fine-tune shares: mean overlap (left and right) of RL-RL pairs is above the
  mean of RL-Think-SFT pairs. Refuted if the RL-RL mean is at or below the RL-SFT mean on both sides.
- X2. The shared subspace is not the base's own largest directions: RL-RL overlap is above RL-`base_w` overlap. Refuted otherwise.
- X3. Overlap follows the math gain: among the six other RL models, overlap with Math 3.1 ranks them as their cue score does
  (Code 3.1, Math 3.0, Mix, General, Code 3.0, IF). Refuted if the Spearman correlation of overlap with the cue score is below 0.5.
  If X1 holds and X3 is refuted, the shared subspace is what RL writes whatever it rewards, and it does not carry the math gain.

## Part 2: edits (after Part 1, spec amended here before running)

Chosen from the Part 1 table. Scored with the cue on hard328 (base 164, RL 206) and MATH-500, never on plain rows alone (Think-SFT
scores 91 of 100 plain with a difference orthogonal to RL). Controls: matched random rank-8, Think-SFT top-8, effective scale after
BF16 rounding.
