# SPEC direct reward-01: does a reward without a gradable final answer also concentrate the change in 8 directions?

Written 2026-11-15 before any number of this test was computed. Work item work-91a169. No GPU job, no forward pass:
stored per-matrix SVD rows only.

Disclosure: the committed summary `studies/rlneurons/results/xreward/overlap_steps-01/readout.json` (per-key mean top-8
share) was read while choosing this test, before the threshold below was fixed. The threshold is therefore not blind to
the point estimates; the intervals, the size-matched contrast and the per-layer counts were not seen.

## The mechanism and its distinctive claim

run-06/f2-m03 (first in `studies/theory/results/wide/round-12/standing_v11_2.md`, +7.51 nats over 8 results): "An outcome
reward pays only for a gradable final answer, so its consistent gradient piles into a few singular directions that make the
model complete the task in the rewarded form (boxed answer, final code block) before the cap; the rest of the update is
diffuse."

Shared with the rivals (not tested here): the top-8 directions change finishing, not correctness (run-05/f2-m01, a signed
finishing dial, claims no cause in training; run-05/f2-m03, directions act as far as the text drives their input singular
vectors).

Distinctive (tested here): the CAUSE of the concentration is that the reward pays only for a gradable final answer. Olmo 3
released a control for exactly this: `allenai/Olmo-3-7B-RL-Zero-General` was trained from the same base with the same RL
code and release as RL-Zero-Math, Code and IF, but on general chat prompts whose reward is a score from an LM judge (Qwen3
32B) of the whole response (model card; Dolci-RL-Zero-General-7B card: "The reward was derived by using an LM judge"). There
is no gradable final answer. Math (sympy check of the boxed answer), Code (test cases) and IF (constraint functions) all pay
for a gradable final output. Think-SFT (imitation, no reward) is a second contrast.

If the stated cause holds, General's change should be diffuse like the no-reward change, not concentrated like the
gradable-answer rewards.

## Readout

Input: per-matrix rows of job `abaybektursun-1114-221259-0871` (`studies/rlneurons/jobs/xreward_overlap.py --steps`,
H100, `metrics.json`, 224 matrices = 32 layers x {q, k, v, o, gate, up, down}). For each key k (a model minus the base in
float32; `base_w` is the base matrix itself) and matrix j: `top8_share` = sum of the 8 largest squared singular values /
sum of all squared singular values. The per-matrix table is extracted to `studies/theory/data/direct_reward/top8_share_v1.json`
(committed; the 10 MB source stays in `runs/`).

- S_k = mean of top8_share over the 224 matrices.
- G = mean of S over the three gradable-answer rewards of the same 3.0 release: math30, code30, if30.
- **P = (S_general30 - S_think_sft) / (G - S_think_sft)**: where General sits between the imitation change (0) and the
  gradable-answer rewards (1).
- Intervals: 90 % bootstrap over layers (resample the 32 layers with replacement, all 7 matrices of a drawn layer kept
  together, paired across keys), 10,000 draws, seed 0.
- Also reported: S for all 16 keys; S_general30 - S_math30 and - S_math31; a size-matched contrast, general30 (change
  0.114 % of weight norm) against code30 at step 100 (0.119 %); the step-100 to final change of S for each of the seven RL
  runs; the number of layers (of 32) where general30's layer mean exceeds math30's; and a noise floor, top8_share of an
  i.i.d. Gaussian matrix of each shape (numpy, seed 0).
- Saved examples: the matrix where general30's share most exceeds math30's, and the one where it falls furthest below.

## Decision (fixed here)

- **Cause refuted** (for the concentration): the 90 % lower bound of P is 0.5 or more, i.e. a reward with no gradable
  final answer concentrates its change at least halfway as much as the gradable-answer rewards do, measured from the
  imitation change.
- **Cause holds**: the 90 % upper bound of P is below 0.5.
- **Undecided**: otherwise.

## What each mechanism predicts for P

- run-06/f2-m03 (tested): P near 0, General's change diffuse.
- run-05/f2-m01 (signed finishing dial, no cause in training): no prediction; it says nothing about how training spreads a
  change over directions.
- run-05/f2-m03 (directions act as far as the text drives their inputs): no prediction about the spectrum of a training
  change.

So P is a readout only the tested mechanism forecasts.

## Supporting readout (stored counts, not part of the decision)

The functional half: General's top-8 directions at 1x on hard328 with the cue (result-6f1bb7, `xreward/edits/readout.json`
cell `top8_general30`): 164 right, 88 cap hits against the cued base's 164 and 77. Quoted, with the caveat that its edit
norm (0.65) is half of Math's (1.27).

## Limits known before the run

General's change is half the size of Math's (0.114 % vs 0.229 % of weight norm) and trained on other prompts; Think-SFT's is
100 times larger (24.8 %). The test separates "gradable final answer" from "sequence-level reward"; it does not test whether
any RL with a sequence-level reward concentrates.

## Runbook

```
uv run --no-project --with numpy python studies/theory/analysis/direct_reward.py extract runs/abaybektursun-1114-221259-0871/metrics.json
uv run --no-project --with numpy python studies/theory/analysis/direct_reward.py analyze
```
Outputs: `studies/theory/results/direct/reward-01/{readout.json, examples.json, run.json}`.
