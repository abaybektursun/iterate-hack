# Screen decoding rules on the base's located wrong steps (follows work-40ec05)

Written 2026-11-15 05:55 UTC, before the job. Branch `critic`.

## Idea

`results/wrongstep/math500-01`: relative to other text of the same answer, Math-RL 3.1 is 0.49 times as likely as the base to
write the base's located wrong step, and the wrong step is not an unlikely sample under the base. A decoding rule that changes
no weight and uses no reward can be screened the same way before any generation: compute the rule's next-token distribution
on the stored wrong answers and ask whether it lowers the wrong step more than control text. A screen costs one forward job
for all rules; a generation cell costs one job per rule.

## Rules (all computed from the base model only, on the 51 located items)

| Label | Next-token distribution |
|---|---|
| `base` | the base with the study's prompt and cue |
| `t0.6` | softmax(logits / 0.6) |
| `noprob` | the base with the same template and an empty problem, then the cue and the same answer text |
| `cad0.5`, `cad1` | softmax((1 + a) logits_base - a logits_noprob), a = 0.5 and 1 (context-aware decoding, Shi et al. 2023, here the context is the problem) |
| `twice` | the base with the problem stated twice in the template ("... Read the problem again: ...") |

Statistic: D as in `specs/SPEC_wrongstep.md` (rule minus base over the wrong step, minus the same over 200 control spans),
`analysis/wrongstep.py` unchanged, run folder `results/wrongstep/rules-01/`.

## Predictions (each with what refutes it)

- S1 `t0.6`: mean D > 0 (sharpening raises a step the base already finds likely). Refuted if its interval is below 0.
- S2 `cad1`: mean D < 0 with the interval below 0, strongest for the `misread` items. Refuted if the interval includes 0.
- S3 `twice`: mean D < 0 for the `misread` items (n 14). Refuted if their mean D >= 0.

Decision: a rule whose interval is below 0 with exp(mean D) <= 0.7 gets one MATH-500 cell (cue, T 1.0, v3), scored against base
cue 410. Known weakness of the screen: Code 3.0 has D = -0.32 and no gain, theta(0.25) D = -0.10 and +6.2 points, so the screen
can pass a rule that does not gain and miss one that does.
