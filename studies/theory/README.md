# theory

Question: which theories connect the team's experiments, measured by how well they predict results they have not seen?

A round is run with the `theory` skill (`.claude/skills/theory/SKILL.md`), which holds the procedure. Subagents propose
theories from the board items before a cutoff time. Each theory is scored by how much it improves a predictor's guesses of
the numbers posted after the cutoff, against the same predictor without the theory.

## Files

| Path | What |
|---|---|
| `lib/check.py` | The mechanical steps: `dump` splits the board at the cutoff, `check` verifies every quote against its board item, `score` compares each theory's predictions with the two no-theory predictors. Usage in its docstring. |
| `results/engine/round-<nn>/` | One round: `run.json`, `before.jsonl`, `after.jsonl`, `targets.jsonl`, `theories/`, `predictions/`, `metrics.json`, `examples.json`. |

## Round 01 (2026-11-15, cutoff 11-14 23:42 UTC)

`results/engine/round-01/`. 60 board items before the cutoff, 21 held out, 58 targets from 13 held-out items, 6 theories
from 3 generators, 1 planted theory (`all-1` with every effect reversed), 9 predictors. 14 subagents.

**Result: no theory beat the null, and the backtest did not discriminate.** Noise (null-1 against null-2) is 3. The planted
theory scored like the real ones (`metrics.json`):

| Theory | closer, farther vs null-1 | vs null-2 | Beats the null |
|---|---|---|---|
| all-1 | 24, 17 | 18, 15 | no |
| across-1 | 21, 14 | 19, 17 | no |
| across-2 | 23, 17 | 22, 20 | no |
| planted | 22, 14 | 23, 21 | no |
| all-2 | 22, 20 | 18, 21 | no |
| surprises-2 | 15, 22 | 17, 22 | no |
| surprises-1 | 21, 21 | 16, 24 | no |

Cause, read from the predictions: about 16 of the 58 targets (the weight-difference cells of result-9b6af3 and
result-4b0d5f) are numbers a theory speaks about. On the others (GPU repeatability, opener counts, neuron statistics,
Code-pair facts) all nine predictors give nearly the same number and the count is predictor noise. On those 16 targets
alone the planted theory still scores best (9, 1 and 11, 3), so restricting the targets does not repair the count.
Each predictor took about 25 s for 58 numbers. Steps 8 and 9 of the skill were not run for any theory.

**The theories' own predictions that the held-out items had measured** (`predictions_measured.json`; matched by hand
by the coordinator after scoring, not a step of the skill in this round): 5 of 7 inside their interval, and 6 of 7
closer to the measured value than both no-theory predictors. The planted theory has no prediction among them, so
this table has no control yet.

| Theory | Experiment (MATH-500, T 1.0, v3, n=500) | Predicted | Measured | | null-1, null-2 |
|---|---|---|---|---|---|
| all-2 | base + 0.25*(RL - base), plain | 375 [330, 415] | 405 | inside | 300, 300 |
| all-2 | base + 0.5*(RL - base), plain | 432 [415, 450] | 443 | inside | 430, 420 |
| all-2 | base + 0.5*(RL - base), cue minus plain | 3 [-10, 15] | 9 | inside | 20, 25 |
| all-2 | Code-RL, plain | 320 [270, 375] | 390 | outside | 270, 300 |
| across-2 | base + 0.5*(RL - base), cue | 447 [436, 457] | 452 | inside | 450, 445 |
| surprises-1 | Code-RL, plain | 340 [280, 400] | 390 | inside | 270, 300 |
| surprises-1 | Code-RL, cue | 410 [390, 432] | 450 | outside | 400, 400 |

Examples (`examples.json`): all-2's predictor on t49 (measured 405: it said 380, the nulls 300 and 300) and on t48
(base + 1.5*(RL - base), cue, measured 453: it said 400, the nulls 440 and 440).

## Theories

All are candidates: none has beaten the null. Full text in `results/engine/round-01/theories/<name>.json`. Open forward
predictions are in idea-0b2ad8, posted before their runs.

| Theory | Statement | Round | Predictions already measured | Status | Open forward predictions (idea-0b2ad8) |
|---|---|---|---|---|---|
| all-1 | The cued base and RL have about the same per-step skill; the gap is the base degrading as its own solution grows. | 01 | none | open | P1, P2, P3 |
| all-2 | Most of the RL gain is one answer-mode switch stored along a diffuse direction of the weight difference, so accuracy saturates quickly in a. | 01 | 3 inside, 1 outside | open | P4 |
| across-1 | The base's loops are early-to-mid-layer copying of its own text; RL weakens it in layers 0-15. | 01 | none | open | P6 |
| across-2 | RL's lead is a learned token-budget controller, trained because 3.1 scores truncated rollouts as failures. | 01 | 1 inside | open | P3, P6 |
| surprises-1 | The gain is a general reasoning-mode shift (which the cue, Code-RL and 3.0 share) plus stopping calibration that only 3.1 has. | 01 | 1 inside, 1 outside | open | P3 |
| surprises-2 | The working part of the weight difference is low-rank; the rest is noise. | 01 | none | open | P5 |
| planted | Control: all-1 reversed (the gap is uniform per-step skill). | 01 | none | control | P1, P2, P3 |
