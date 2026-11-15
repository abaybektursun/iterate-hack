# Critic at decoding time: stop a failing sample early, with no weight change and no answer key (idea-eec971, work-5d5dc3)

Written 2026-11-15 04:55 UTC. Stage 0 was run before this text (it reads stored rows only); stage 1 and the offline policy
test are specified here before their job. Branch `critic`.

## Thesis

What is left of the RL gain on MATH-500 is reliability: the cued base has a right answer among 4 samples on 467 of 500, RL's
single answer is right on 456 (result-afc423: 81 % of the gap is in problems the base solves at least once in 4). A critic that
sees early that a sample will fail lets the base stop it and start again, at a small cost in tokens.

## Stage 0 (done): the ceiling, `analysis/critic_ceiling.py`, `results/critic/ceiling-01/metrics.json`

Stored 4-sample rows (`results/day1_3`), cued base, single 405 at 3,808 tokens. Stop-and-restart with a perfect critic that
looks once at 1,000 tokens: with the answer key 444 (2 samples at most) and 459 (4) at 3,958 and 4,013 tokens; with the
label-free target (stop unless the sample will agree with the plurality of the problem's 4 samples) 436 and 441 at 3,910 and
3,873 tokens. Stop rule (440 of 500 at <= 1.5x tokens) passed. The label-free flag equals correctness on 85.3 % of base samples.

## Stage 1: can the base's activations tell, early, which sample will fail?

Job `jobs/critic_acts.py`: the base model reads its own 2,000 stored samples (job `abaybektursun-1114-153825-208b`, attempt 0)
and stores the residual stream at layers 12, 20 and 28 at the last prompt token (position 0, before any sampled token) and after
250, 500, 1,000 and 2,000 answer tokens, plus the mean log-probability and mean entropy of the answer tokens so far.

Readout `analysis/critic_probe.py`: logistic regression on the standardized activations of one layer and checkpoint, 5 folds by
problem, L2 strength chosen inside the training folds. Targets: the label-free flag (training and test) and correctness (test only).

The number that decides: the within-problem AUROC. For every problem with both outcomes among its samples that reach the
checkpoint, the share of (good sample, bad sample) pairs that the probe orders correctly. A probe that only knows how hard the
problem is scores 0.5 here, and restarting cannot use problem difficulty.

Baselines, same statistic: mean log-probability so far, mean entropy so far. Instrument checks: at position 0 the activations
are the same for all samples of a problem, so the within-problem AUROC must be 0.5 exactly; a probe trained on labels shuffled
within problems must be at 0.5 within its interval.

## Offline policy test (same data, no new samples)

With each sample's held-out probe score at 1,000 tokens: stop a sample when its score is below a threshold and take the
problem's next stored sample, at most 4, the last always kept (as in stage 0). The threshold is chosen on the training folds to
maximize right answers subject to <= 1.3x tokens. Report right of 500 and tokens per problem, against single 405 and against the
same procedure with a random score (same stop rate).

## Predictions (each with what refutes it)

- C1 Within-problem AUROC for the label-free target at 1,000 tokens, best layer: >= 0.60 and at least 0.03 above the better of
  the two baselines. Refuted (and the study stops) otherwise.
- C2 The AUROC rises with the checkpoint (250 < 1,000 < 2,000). Refuted if 250 is within 0.02 of 2,000.
- C3 The offline policy reaches >= 420 of 500 at <= 1.3x tokens and beats the random score by its paired interval. Refuted otherwise.

Against it: result-f21d2e (no J-lens feature predicts a wrong base answer better than length, AUROC 0.831 across problems),
2608.17124 and 2605.09502 (correctness in activations is a readout). The within-problem statistic has not been reported for this pair.

Cost: one H100 job, about 15 minutes, about 2 USD.
