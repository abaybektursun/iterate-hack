# Generation test from the prefix before each located wrong step (work-d10ae6, follows SPEC_rulescreen.md)

Written 2026-11-15 06:00 UTC, before any generation of this test. Branch `critic`.

## Question

The screen (`results/wrongstep/rules-01`) says that contrasting the base's prediction with and without the problem in context
lowers the probability of the base's located wrong steps, and `results/wrongstep/math500-01` says Math-RL 3.1 is 0.49 times
as likely to write them. Do these lower probabilities turn into more right answers when the answer is continued from just
before the wrong step?

A whole MATH-500 cell has little power for this (the effect is on a minority of wrong samples; the 95 % interval of a cell
difference is about 3.4 points). Continuing from the prefix before each wrong step puts every generation where the effect should be.

## Design

Items: the 51 located wrong steps (`results/anatomy/judge-01/labels.json`, kind "base"). Prefix = the stored answer up to the
token before the wrong step. Each arm writes K = 6 continuations per prefix (306 per arm) at T 1.0 / top-p 1.0, at most 6,000 new
tokens, grader v3 on prefix + continuation. Job `jobs/prefix_cell.py` (transformers, its own sampling loop, the same for all arms).

| Arm | Model that continues | Rule |
|---|---|---|
| `base` | base | none (control) |
| `cad1` | base | softmax(2 logits - logits without the problem), every step |
| `rl` | Math-RL 3.1 | none |

Statistic: right continuations per prefix (0 to 6); arm minus `base`, in points, paired bootstrap over the 51 prefixes
(5,000 resamples). Also by the judge's label, and cap hits and tokens per continuation.

## Predictions (each with what refutes it)

- G0 (instrument) `base` continues to a right answer in fewer than half of the continuations (these prefixes are followed by a
  wrong step in the stored sample, and the base finds that step likely). If `base` is right in more than 70 %, the located step
  is not where the answer goes wrong and the test says little.
- G1 `rl` minus `base` > 0, interval above 0. Refuted if the interval includes 0: RL's lower probability of the step does not
  rescue a base prefix.
- G2 `cad1` minus `base` > 0, interval above 0, largest on the `misread` items. Refuted if the interval includes 0 or is below
  it. If cap hits of `cad1` exceed twice those of `base`, the rule breaks the text and that is reported as the result.

Decision: if G2 holds, one MATH-500 cell and then the 328 with the rule; if only G1 holds, the result is that the screen passed a
rule that does not help. Cost: about 5 GPU hours, about 20 USD.
