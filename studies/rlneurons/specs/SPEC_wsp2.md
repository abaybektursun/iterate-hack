# WSP-2: a hand-written weight edit, built without the RL weights and without reward

Written 2026-11-15 05:40 UTC before any run. Follows WSP-1 (`specs/SPEC_wsp1.md`): there the edit was copied from the
RL-trained weights. Here the edit is written from a stated goal and the base model's own activations only.

## Question

Can a weight edit that uses no RL weights, no reward and no answers make the plain base behave like the cued base, and does
it go past the cue? References on the first 100 MATH-500 problems, T 1.0, plain prompt, seed base 80,000,000
(`results/wsp1/screen100/`): base 34, base with the prefilled cue 82 (seed base 81,000,000), `top8` (copied from RL) 88,
RL 96.

## The edit ("cue program"), `jobs/wsp_handedit.py`

Goal, in words: when the answer is about to start, write the opening cue ` line!\n\nOkay` (ids 1584, 2268, 33413).

One tensor changes: `model.layers.31.mlp.down_proj.weight` W (4096 x 11008), the last MLP's write into the residual stream.

- Keys. For cue position i = 0, 1, 2: k_i = the mean, over the calibration prompts, of the input to `down_proj` (11,008
  numbers) at the last position of [plain prompt ids + the first i cue ids]. Calibration prompts: MATH-500 problems 100 to
  227 (128 prompts, questions only). The scored problems 0 to 99 are never used.
- Background. C = the second-moment matrix of the same input over every position of the calibration prompts and of 64
  tokens the base itself writes after the prefilled cue (greedy, questions only). C_reg = C + 0.01 mean(diag C) I.
- Values. u_i = the unit vector of (unembedding row of cue token i minus the mean unembedding row).
- Edit. dW = sum_i a_i u_i (C_reg^-1 k_i)^T / (k_i^T C_reg^-1 k_i), so that dW k_i = a_i u_i and dW moves other inputs as
  little as the background allows (the rank-one key-value edit of ROME, used here for a behaviour). Each a_i is found by
  bisection as the smallest scale at which the mean probability of cue token i in context i reaches 0.95 on the
  calibration prompts, positions edited in order 0, 1, 2 with the earlier ones in place.
- The tensor is written as BF16 and the checks below read that written tensor.

Checks, reported in `handedit.json`, on held-out prompts (problems 228 to 291, 64 prompts): the probability of each cue
token in its context before and after; and the mean KL(base || edited) of the next-token distribution over the positions of
64 tokens of the base's own cued continuation. The job stops if a held-out cue probability is below 0.5 or that KL is
above 0.5 nats.

Control, same job with `--control`: the same keys and scales with random unit vectors as values (seed 0). It has the same
size and touches the same inputs and carries no goal.

Instrument check (`--selftest`, synthetic, no weights): on a planted linear model, dW k_i equals a_i u_i within 1e-4; an
input drawn from the background moves by less than 5 % of that; bisection recovers a planted threshold; the control has the
same Frobenius norm within 1 %.

## Cells

`cueprog` and `cueprog_rand` (control), plain prompt, first 100 MATH-500 problems, T 1.0, top-p 1.0, seed base 80,000,000,
through `run_cell.py --model-path`. Each reports right of 100, cap hits, median tokens, and the share of answers whose
first 80 characters contain `Okay`.

## Hypotheses and refuters

- H1, the hand-written edit reproduces the cue: `cueprog` is at least 72 right (within 10 of the cued base) and at least
  90 % of its answers open with the cue. Refuted if it is below 60 or the control is within 10 of it.
- H2, it goes past the cue: refuted unless `cueprog` is above 92 (10 above the cued base). Expected to be refuted: the edit
  only starts the answer the way the cue does. Closest published: Wang et al. 2610.06851 App. D.5, a one-matrix edit that
  raises cue probability to 0.95 scores 0.78 on MATH-500.

A cell that passes H1 is rerun on all 500 before any claim.
