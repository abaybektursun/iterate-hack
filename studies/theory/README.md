# theory

Question: which theories connect the team's experiments, measured by how well they predict results they have not seen?

A round is run with the `theory` skill (`.claude/skills/theory/SKILL.md`), which holds the procedure. Subagents propose
theories from the board items before a cutoff time. Each theory is scored by how much it improves a predictor's guesses of
the numbers posted after the cutoff, against the same predictor without the theory.

## Files

| Path | What |
|---|---|
| `specs/SPEC_round02.md` | Plan of round 02, written before the run: the new score, the reversal control, hypotheses H1-H3. |
| `lib/check.py` | The mechanical steps: `dump` splits the board at the cutoff, `check` verifies every quote against its board item, `score` compares each theory's predictions with the two no-theory predictors (round 01's score). Usage in its docstring. |
| `lib/v2.py` | Round 02's check and score: each theory's own claims, divergent wins and losses against the two no-theory agents, the reversal control, targets of `exposed.json` left out. Writes `metrics_v2.json`. Usage in its docstring. |
| `results/engine/round-<nn>/` | One round: `run.json`, `before.jsonl`, `after.jsonl`, `targets.jsonl`, `targets_blind.jsonl` (targets without values), `theories/`, `predictions/`, `examples.json`; round 01 also `metrics.json` and `predictions_measured.json`. |
| `results/engine/round-02/` (new files) | `external.md` (25 published findings, by mechanism), `theories.sha256` (theory files fixed before the claims), `claims/<theory>.jsonl` (each author's value and interval per target; `.rev.jsonl` the reversal's), `reversed/` (the reversed theories), `reviews/` (refutation search, novelty, verdict), `exposed.json` (items left out of the score and why), `metrics_v2.json`. |

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
this table has no control yet. A round-01 author later copied its git status lines, and none held a result number
(`round-02/exposed.json`, key `round_01_agents`), so this table was not exposed through commit subjects.

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

## Round 02 (2026-11-15, cutoff 11-14 23:42 UTC)

`results/engine/round-02/`, plan `specs/SPEC_round02.md`. Same cutoff as round 01. 60 board items before the cutoff, 25
held out, 68 targets from 15 held-out items. The 7 targets of result-5d032f are left out (`exposed.json`), so 61 targets
are scored. 16 theories: the 6 of round 01 unchanged (`theories/r1-*.json`, byte-identical to round 01's files) and 10
new from 5 generators (all, surprises, across, external, revise; `theories/r2-*.json`), each importing at least one
published mechanism from `external.md` (25 findings). 2 no-theory agents (opus), 5 reversals, 3 reviews. 17 new
subagents plus the 3 round-01 generators resumed (`run.json`).

**Result: 5 of 16 theories pass the new score, each with a net above its reversal's (every reversal's net is -2 or
lower), but each rests on only 2 to 5 divergent claims, and all 3 passers that were reviewed were refuted (r1-all-1) or
judged weak (r2-all-2, r2-across-2)** (`metrics_v2.json`, `reviews/`). A claim is divergent when both no-theory agents'
numbers lie outside its interval. Sorted as `v2.py score` prints them (by net):

| Theory | Claims | Divergent win, loss | Non-divergent inside, outside | State | Reversal win, loss | Review |
|---|---|---|---|---|---|---|
| r2-all-2 | 8 | 2, 0 | 4, 2 | passes | 0, 6 | weak |
| r1-all-1 | 12 | 2, 1 | 3, 6 | passes | 1, 6 | refuted |
| r1-all-2 | 13 | 3, 2 | 3, 5 | passes | 0, 5 | not reviewed |
| r1-surprises-2 | 19 | 3, 2 | 11, 3 | passes | 1, 11 | not reviewed |
| r2-across-2 | 15 | 3, 2 | 5, 5 | passes | 6, 8 | weak |
| r2-revise-1 | 10 | 1, 0 | 3, 6 | fails | | |
| r1-across-1 | 13 | 2, 2 | 5, 4 | fails | | |
| r1-across-2 | 16 | 1, 1 | 9, 5 | fails | | |
| r1-surprises-1 | 8 | 0, 0 | 6, 2 | fails | | |
| r2-across-1 | 6 | 1, 1 | 4, 0 | fails | | |
| r2-external-1 | 5 | 1, 1 | 3, 0 | fails | | |
| r2-revise-2 | 2 | 0, 0 | 0, 2 | fails | | |
| r2-all-1 | 5 | 0, 1 | 2, 2 | fails | | |
| r2-external-2 | 6 | 1, 2 | 2, 1 | fails | | |
| r2-surprises-1 | 4 | 0, 1 | 1, 2 | fails | | |
| r2-surprises-2 | 9 | 0, 1 | 5, 3 | fails | | |

Claims are counted on the 61 scored targets only. Candidate = wins >= 2 and wins > losses; passes = net (wins - losses)
above the reversal's net.

Hypotheses of the spec:

- H1, the new score separates theories: not refuted. 5 candidates, each net above its reversal's (r2-all-2 +2 vs -6,
  r1-all-1 +1 vs -5, r1-all-2 +1 vs -5, r1-surprises-2 +1 vs -10, r2-across-2 +1 vs -2). But a net of +1 or +2 is one or
  two targets, and r2-across-2's reversal scored 6 wins, more than the theory's 3.
- H2, imports yield passing theories whose import carries a win: not refuted by the spec's rule, on one theory only.
  r2-across-2's review says no: its 3 wins come from result-904bbf's additivity, a fitted map and 2404.16792; its import
  2610.37719 drives t37, t38 and t47, none divergent (`reviews/r2-across-2.json`, `import_carries_win`). r2-all-2's review
  says yes: t51 rests on 2512.12895 and t09 on 2007.14966; it adds that without the imports t51 is a sign guess inside
  noise (-1.2 points [-4.6, 2.2]) and t09 follows from a grader format fact with no import (knowledge-499152)
  (`reviews/r2-all-2.json`).
- H3, round-01 all-2 and across-2 are candidates: half refuted. r1-all-2 is a candidate (3 wins, 2 losses) and passes;
  r1-across-2 is not (1 win, 1 loss).

What round 02 showed about the engine:

1. Commit subjects leak results. Claude Code gives every subagent a git status block with the 5 newest commit subjects.
   One subject (d1f0136) held the 7 numbers of result-5d032f, and the nulls and new generators had it in context. The
   r2-all author reported it. Those 7 targets are left out of the score (`exposed.json`, read by `v2.py`). A headless
   run from an empty directory has no such block (tested by the coordinator).
2. The interval rule discards closeness. r1-all-2 claimed 370 [340, 400] for t40, measured 405, nulls 300 and 290: the
   claim was 35 off and the nulls 105 and 115 off, and it counts as a loss.
3. The control is not matched. The author of a theory wrote its claims; a fresh agent wrote its reversal's claims.
4. Round 02's passes are not an independent test. It scored the same held-out items as round 01, and the score was
   changed after round 01's numbers had been seen by the coordinator.
5. Five of the ten new theories import 2610.37719, and four of them (r2-across-2, r2-all-1, r2-external-1, r2-revise-1)
   predict the same DARE drop on the MLP delta at keep 0.01 %: 340 [220, 405], 20 [0, 120], 40 [0, 200] and 40
   [0, 150] right of 500. That is one prediction, not four.
6. The reviews, not the score, did the deciding: all 3 reviewed passers were refuted or judged weak (`reviews/`).
7. Forward predictions work. idea-0b2ad8 (P1, posted 02:24 UTC) was measured by another agent's experiment,
   result-e45bf4 (03:17 UTC, 53 minutes later), and refuted r1-all-1 by its own refutation rule.

Examples (`examples.json`), r1-all-2 on the plain prompt, MATH-500 n=500, T 1.0, v3: a divergent win on t41 (base +
0.5*(RL - base): measured 443, claim 432 [415, 450], nulls 400 and 380) and a divergent loss on t40 (base +
0.25*(RL - base): measured 405, claim 370 [340, 400], nulls 300 and 290).

## Theories

Standing after round 02. Full text in `results/engine/round-02/theories/<name>.json` (`r1-*` are round 01's files,
unchanged). Score columns from `round-02/metrics_v2.json`; verdicts from `round-02/reviews/`.

| Theory | Statement | Round | Round-02 score (wins, losses, state) | Review | Status |
|---|---|---|---|---|---|
| r1-all-1 | The cued base has RL's per-step skill; the gap is the base degrading as its own long solution grows, which RL repaired by training truncated rollouts as failures. | 01 | 2, 1, passes | refuted | refuted |
| r1-all-2 | Most of the RL gain is one answer-mode switch (deliberate, box the answer, stop), stored redundantly along a diffuse direction, so any small unbiased fraction of the delta flips it. | 01 | 3, 2, passes | none | passes, not reviewed |
| r1-across-1 | The base's loops and cap hits come from early-to-mid-layer circuits that copy its own earlier text; RL's cap-hit gain weakens that pathway in layers 0-15. | 01 | 2, 2, fails | none | fails |
| r1-across-2 | RL's lead is a learned token-budget controller, trained because 3.1 scores truncated rollouts as failures; it is not new math skill. | 01 | 1, 1, fails | none | fails |
| r1-surprises-1 | The gain is a general deliberation shift that the cue, Code-RL and 3.0 share, plus stopping calibration that only 3.1 learned; the cued-base gap is the second part. | 01 | 0, 0, fails | none | fails |
| r1-surprises-2 | The working part of the weight change is low-rank and near-linear; the high-rank remainder, which holds most of its energy, is optimizer noise. | 01 | 3, 2, passes | none | passes, not reviewed |
| r2-all-1 | The delta acts through coherent signs along high-curvature directions, about 700 times a random direction; unbiased resampling keeps the gain, random signs remove it, SFT deltas break. | 02 | 0, 1, fails | none | fails |
| r2-all-2 | Base accuracy at a sampler setting depends on the per-token surprise of its text (too low: loops; too high: drift); the cue lowers entropy, so truncation hurts the cued base. | 02 | 2, 0, passes | weak | weak |
| r2-surprises-1 | Loops and slips are two ends of one axis, the per-token surprise of sampled text; the cue lowers entropy, RL sits far from both ends, and raising surprise cuts loops. | 02 | 0, 1, fails | none | fails |
| r2-surprises-2 | The base and optimizer set which entries move, and how far; the task is written only in the signs, which act on any math text and leave general text alone. | 02 | 0, 1, fails | none | fails |
| r2-across-1 | The weight change lowers next-token entropy only at the base's high-entropy fork tokens, so RL ignores temperature while the base loops when cooled and errs when heated. | 02 | 1, 1, fails | none | fails |
| r2-across-2 | The delta's effect sits in its coherent sign pattern, with hundreds to thousands of times a random direction's Fisher curvature; DARE fails near keep 0.01-0.05 %. | 02 | 3, 2, passes | weak | weak |
| r2-external-1 | The delta moves output 700 times more per unit energy than a random direction; DARE holds to keep 0.1 % and collapses near 0.01 %; random weight noise reduces loops. | 02 | 1, 1, fails | none | fails |
| r2-external-2 | One global temperature acts on two kinds of positions: low temperature starts loops at rare fork tokens, high temperature causes slips elsewhere; a per-position temperature would fix the base. | 02 | 1, 2, fails | none | fails |
| r2-revise-1 | Accuracy is carried by the dense sign pattern of many small entries; an edit recovers accuracy in proportion to the share of it kept; Code-RL gives no math gain. | 02 | 1, 0, fails | none | fails |
| r2-revise-2 | The cued base's gap is a weak error detector, not weaker per-step math: RL notices and re-derives errors more often, so a 4-sample vote closes about half the base's gap. | 02 | 0, 0, fails | none | fails |

Round-01 forward predictions of idea-0b2ad8 that have been measured (`round-02/reviews/r1-all-1.json`,
`forward_predictions_measured`):

- P1, base + 0.5*(RL - base), cue, T 1.0, hard 328, cap hits: measured 73 of 328, with 190 right (result-e45bf4;
  `studies/rlneurons/results/day1_wdiff328/readout.json`, cell `theta0.5_cue`). Outside r1-all-1's 45 [30, 60], inside
  the planted reversal's 72 [60, 85]. r1-all-1's own rule (refuted if cap hits stay at 70 or more while accuracy rises
  above 175) is met.
- P2, stored T 1.0 MATH-500 answers of cued base and RL cut at 4,096 generated tokens, RL minus cued base: -9.2 points
  [-13.0, -5.4] (base 337, RL 291 of 500). Inside r1-all-1's -7 [-14, 0], outside the planted reversal's +7 [0, 14]. Not
  a board item: the reviewer computed it from `studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json` as right
  and generated tokens <= 4,096, which counts wrong an answer that boxed its answer before token 4,096 but kept writing.
  It follows from RL writing longer answers (result-5e17a6) and does not separate the mechanisms.

P3 to P6 have no measurement in this record (P3: not measured by the team, per the same review).
