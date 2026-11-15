# tinkerpair: a second model pair, with our own RL, on Tinker

Written 2026-11-15 before any model call. Board work-09d814.

## Question

On the Olmo pair the opening cue takes the untrained base most of the way to AI2's RL model, and AI2 released only
three RL checkpoints. Here we run the RL ourselves on a second base model, so every checkpoint exists.

- Q1. At each RL checkpoint, what are the plain accuracy, the cued accuracy and the probability the model gives to the
  cue opening by itself? Is the first part of the RL gain the part the cue already gives the base?
- Q2. With the same loop and the same sampled tokens, does a reward that uses no gold answer (agreement with the
  plurality answer of the problem's own samples) reach the gain of the grader reward?

Model: `Qwen/Qwen3.5-9B-Base` on Tinker (Thinking Machines), LoRA. Tinker serves no Olmo model, so the Olmo pair cannot
be rerun there.

## What is already published (read 2026-11-15)

- Q1 at the end points only. 2610.24663 Table 3: on Qwen3-4B-Base a one-token opening recovers 35 % of the RL gain on
  AIME (10.00 -> 13.23, RL 19.32). 2610.06851 App. D Fig. 14: RL trained with the cue forced reaches plain RL's
  step-300 accuracy in 100 steps; Fig. 16 gives opening probabilities before and after RL. Neither scores plain and
  cued prompts or the opening probability at intermediate checkpoints of plain RL. Our Olmo result-32b7a8: at RL step
  100, 478 of 500 plain answers have "Okay" in their first 30 characters (base 193).
- Q2 without token matching. TTRL 2504.16084: plurality-vote reward takes Qwen2.5-7B base from 60.5 to 80.5 on
  MATH-500. 2511.04902 Table 1: vote 73.6 against labelled 73.8 at 7B, 63.8 against 64.4 at 3B, collapse to 0.0 at
  0.5B. So Q2 here is a replication inside one loop at equal sampled tokens, not a new claim.

## Fixed conditions

- Prompt: `studies/rlneurons/lib/n13_score.TEMPLATE["pair1"]` as raw text, no chat template (a base model).
- Cue: the text of the Olmo pair's cue, `" line!\n\nOkay"`, encoded apart and placed after the prompt's ids. It is not
  tuned on this model. The answer that is graded is the cue followed by the continuation.
- Sampling: T 1.0, top-p 1.0, stop at the end-of-text token. Grader v3 (`rln4_lib.grade_v3`).
- Scored sets: MATH-500 (500) for every choice; hard328 once, at the end, for the configurations named below.
- Training problems: `data/train_v1.json`, 2,560 of AI2's Dolci-RL-Zero-Math-7B prompts (revision `93b5e49`),
  duplicates removed, the 87 prompts that overlap MATH-500 or the 400 harder problems removed, shuffled with seed 0.
- RL: LoRA rank 32, Adam lr 4e-5 (the Tinker cookbook's `rl_loop` default for this model), loss
  `importance_sampling`, 32 problems x 8 samples per step, plain prompt, cap 4,096, advantage = reward minus the mean
  reward of the problem's 8 samples, 40 steps, checkpoints after steps 5, 10, 20, 30, 40. Seed 2,000,000.
- The pilot (below) may change groups, cap and steps to fit the credit. A change is written here with its date before
  any checkpoint is scored.

## Cells

1. Stage 1, base: plain and cue on MATH-500, cap 16,384 (the Olmo harness's cap), seed 1,000,000, 1 sample.
2. RL, grader reward (`rl/grader-01`): checkpoints 5, 10, 20, 30, 40. Each scored plain and cued on MATH-500, cap
   4,096, with the base rescored at cap 4,096 as step 0.
3. RL, vote reward (`rl/vote-01`): same steps, same scoring.
4. Cue log-probability: for the base and every checkpoint, the mean over the 500 MATH-500 prompts of the summed
   log-probability of the cue's tokens after the prompt (`compute_logprobs`), and the share of plain answers that
   have "Okay" in their first 30 characters.
5. hard328, once: base cue, final grader checkpoint plain, final vote checkpoint plain, cap 16,384.

## Hypotheses, each with its refuter

- H1, the cue transfers. Base cue minus base plain on MATH-500 is positive. Refuted when the paired 95 % interval
  includes 0. Prediction: plain 55 [40, 70], cue 70 [58, 82] percent.
- H2, RL installs the opening first. (a) The cue's log-probability rises from the base to the first checkpoint whose
  plain accuracy is above the base's interval. (b) At the final grader checkpoint the cue's gain (cued minus plain,
  same checkpoint) is at most half of its gain on the base. Refuted for (a) when the log-probability does not rise
  by more than its spread over two base readings; for (b) when the final gain's interval lies above half the base
  gain. A base cue gain of 0 (H1 refuted) leaves H2 untestable here; then the opening the RL model converges to is
  reported instead and forced on the base as a second cue in one extra cell.
- H3, the vote reward matches the grader reward. Final plain accuracy, vote minus grader, is inside [-3, +3] points.
  Refuted when the paired interval excludes that band. Collapse is named separately: vote agreement of the training
  samples rises while their grader accuracy falls below its step-0 value.
- Prediction for the RL gain: final grader checkpoint plain 75 [62, 86] percent; cue share of the gain (base cue minus
  base plain over final RL plain minus base plain) 60 % [30, 100].

## Instrument checks, before any score is read

- G1 stop and prompt: 8 MATH-500 problems, plain and cue; the end-of-text stop ends answers, a cap hit is reported as
  "length", the cued continuation starts after the cue's ids.
- G2 grader negative control: the stage-1 cue cell rescored with golds shifted by one problem (`--derange`, 100
  problems) must score at most 3 of 100.
- G3 loop: `--reward planted` (reward 1 when the first sampled token is a fixed token the base emits first with
  probability between 0.05 and 0.6), cap 8, 8 steps: that share must rise by at least 20 points. A loop that cannot move a planted
  target is broken.
- G4 reward isolation: `reward_vote` takes the texts only; the grader accuracy of the vote arm is logged, never used.

## Cost

Listed prices per million tokens for this model: prefill 0.30, sample 0.807, train 1.463 USD. Stage 1 about 3 M
sampled tokens, 3 USD. One RL arm: 40 steps x 256 samples x about 1,500 tokens = 15 M sampled and trained, about 35
USD. Checkpoint scoring: 12 cells x 500 x about 1,500 = 9 M per arm, 8 USD. hard328 3 USD. Total about 95 USD.

## Runbook

1. `python -m studies.tinkerpair.prep.build_train <train.parquet>` (done, sha256 `f67127d7...62ff`).
2. G1, G3; stage 1; G2.
3. `jobs/rl.py --reward grader` and `--reward vote` in parallel.
4. `jobs/eval_cell.py` per checkpoint and prompt; `jobs/cue_logprob.py` per checkpoint.
5. `analysis/readout.py` writes `results/readout.json`; README; board result; finding page when H2 gives a curve
   worth showing.
