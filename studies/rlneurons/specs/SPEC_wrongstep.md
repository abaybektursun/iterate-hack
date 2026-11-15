# Do the RL models make the base's own wrong steps less likely? (work-40ec05)

Written 2026-11-15 05:45 UTC, after the job was submitted and before any of its output was read. Branch `critic`.

## Question

The cued base leaves 2.6 times more first wrong steps per 1,000 tokens in finished answers than RL (0.038 against 0.015,
result-855858), and five of ten sibling models gain on MATH-500 with the cue while others do not (result-edceef). If the gain is
a lower chance of writing the specific wrong step, a model that gains should give the base's located wrong steps a lower
probability than the base does, beyond its general dislike of base text, and a model that does not gain should not.

## Measurement

Items: the 60 judged finished-wrong samples of the cued base on MATH-500 (`results/anatomy/judge-01/labels.json`, kind "base":
21 slip, 17 wrong plan, 14 misread, 8 format), each with the judge's quote of the first wrong step. `jobs/score_tokens.py
--labels` scores each whole answer under base, Math 3.1, Code 3.1, the five Olmo 3 models, theta(0.25) and the random
difference, and stores the quote's token span.

Per item and model: R = sum over the span of r_m = log p_m - log p_base. Control: the mean of R over 200 spans of the same
token length drawn uniformly from the same answer without overlap with the wrong step (seed 0). D_m = R(wrong step) -
R(control), in nats per span; mean over items with a bootstrap interval (5,000 resamples of items). exp(mean D_m) is the
factor by which model m is less likely than the base to write the wrong step, relative to other text of the same answer.

Also reported: the base's own log-probability of the span against its control spans (was the wrong step an unlikely
sample?), D by the judge's label, and D restricted to the first 5 tokens of the span (where the step begins).

Instrument checks: the random difference must give D within its interval of 0; theta(0.25) must have the sign of Math 3.1
and a smaller size.

## Predictions (each with what refutes it)

- W1 Math 3.1: mean D < 0, interval below 0. Refuted if the interval includes 0: Math-RL does not single out the base's wrong steps.
- W2 The models that gain with the cue (Math 3.1, Code 3.1, Math 3.0, Mix 3.0) have lower mean D than those that do not
  (Code 3.0, IF 3.0). Refuted if Code 3.0 or IF 3.0 has a mean D below the mean of the four.
- W3 Size: exp(mean D) for Math 3.1 is between 1/1.5 and 1/4 (the observed ratio of first wrong steps is 1/2.6). Refuted outside.
- W4 The base's own log-probability of the wrong step is lower than that of its control spans (interval below 0): a wrong
  step is an unlikely sample. Refuted if the interval includes 0.

Limits known before the run: 60 items; the quote marks where the judge saw the error, which can be after the token that
caused it; judges were the team's own subagents (kappa 0.88, result-855858).
