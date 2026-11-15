# signed1: signed self-training with no reward

Written 2026-11-15 before any run. Board: idea-0d55a4, work-d9a824.

## Question

Positives-only fine-tuning of the base on its own voted answers gave no gain on the 328 (arms V and U of
`specs/SELFDISTILL_2026-11-15.md`: cue 167 and 168 against base cue 164). RL differs from that in one more way than the reward:
its update is signed. A sample below the problem's mean return is made less likely. This run tests the missing cell of the 2x2
{vote, key} x {positives only, signed}: does a signed update, with agreement among the base's own 4 samples as the return, move
the base toward RL on the 328?

## Arms (`data/signed/arms-v1.json`, built by `jobs/signed_data.py` from MATH-500 job abaybektursun-1114-153825-208b, base cue, T 1.0, 4 samples)

- P (no reward): return 1 for a finished sample in the plurality group, else 0. 138 problems with unequal returns, 552 samples.
- G (ceiling, uses the answer key): return = grader v3 score. 150 problems, 600 samples.

Advantage a = return minus the problem's mean return. P's return equals the key's score on 515 of 552 samples.

## Training (`jobs/signed_train.py`)

LoRA rank 16, alpha 32, lr 1e-4, clip 1.0, as in the vote-distillation run; one epoch; one step per problem;
loss = sum_i a_i * (NLL_i / tokens_i) / sum_i |a_i|. Hyperparameters are fixed here and not tuned on the 328.

## Measurement

Merged model, cue, T 1.0 / top-p 1.0, cap 16,384, grader v3, seed 3000000, one sample, the 328 (`run_cell --set hard328`).
Paired bootstrap against base cue job abaybektursun-1114-151534-e72c (164/328).

## Hypotheses and what refutes each

- H1 (the sign carries the gain): P cue on the 328 is above base cue with a 95% interval above 0, and above V and U (167, 168).
  Refuted if P is within the interval of 164, or below it.
- H2 (the reward's information matters, not the sign): G gains and P does not. Refuted if both gain or neither does.
- H3 (the update is not RL's direction): cosine of the merged difference with RL minus base is near 0 for both arms, as it was
  for V and U. Reported from `train.json`, decides nothing alone.
- Instrument check: over the epoch, mean per-token NLL of the negative samples must rise relative to the positive ones
  (`nll_negative` minus `nll_positive`, second half against first half). If it does not, the update did nothing and no cell is run.
  The 3 greedy generations after training must still be text that starts with the cue; if the model is broken, the result is
  "one epoch at this step size breaks the model", and one rerun at lr 3e-5 is allowed.

## Order

1. Smoke: `signed_train --arm P --n 4`, read the log.
2. Train P and G in parallel (about 3.0M and 3.5M target tokens).
3. Instrument check, then the two cue cells on the 328.
4. Readout with examples in `results/signed1/`, README section, board.

## Amendment after training, before any cell (2026-11-15)

The instrument check as written cannot decide. Each problem is seen once, so `nll_negative - nll_positive` before a step is
measured on a problem the adapter has not trained on, and with 34 problems per quarter it moves by more than any trend: P
0.20, 0.05, 0.14, 0.04 nats per token by quarter; G 0.17, 0.09, 0.04, 0.11 (train jobs 17cc, 116e). It does not rise. Read as
written, the check says the update did not learn to separate right from wrong samples on new problems. The model did change:
merged relative norm 0.0048 (P) and 0.0052 (G), greedy generations differ and stay coherent, cosine with RL minus base 0.001
and 0.003. Deviation from the order: both cue cells on the 328 are run anyway, because the 328 is the deciding number; the
failed check is reported beside it.
