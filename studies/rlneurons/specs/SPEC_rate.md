# SPEC_rate: exchange-rate table of methods in logits, with held-out predictions

Board: idea-31636e, work-c45b70. Builds on result-5da8a9 (`specs/SPEC_axis.md`): every MATH-500 arm lies on one Rasch
difficulty axis. Laptop only, no GPU. Written before any number below was computed and before any held-out result was read.

## Questions

1. What is each method's ability shift in logits against base + cue sample 0 on MATH-500, and what does it cost (generated
   tokens per problem; training signal: none / own samples / SFT data / RL reward)?
2. Does a shift measured on MATH-500 predict the method's score on the 328 harder problems better than "same point gain"?
3. Can the table predict cells that are running now?

## Method

- Inputs: `results/axis/{math500,hard328}-01/vectors.json` (0/1 per arm and problem, grader v3), `manifest.json`, the
  Day-1 #3 `rows.jsonl` and `readout.json` (restart, vote-after-restart vectors; votes over k = 2, 3 samples recomputed with
  `day1_vote.vote`), each run's `metrics.json` for tokens.
- Item difficulties b_i: `axis.fit` on the single-sample arms of a set (36 on MATH-500, ridge 0.3; 7 on hard328, ridge 0.1:
  the ridges `axis.py` selected). Ability of any 0/1 vector y given b: the a that solves sum_i sigmoid(a + b_i) = sum_i y_i
  over the problems y has (maximum likelihood with b fixed). Derived arms (votes, restart) get an ability the same way.
- Shift of an arm = its ability minus the ability of the reference. Table: reference base + cue sample 0. Transfer and
  predictions: reference = the pooled four base + cue samples on MATH-500 (less noise) and the pooled two base + cue runs on
  hard328 (164 and the same-seed rerun 160).
- Interval of a shift: paired bootstrap over problems (2,000 resamples, seed 0, b fixed), 95 % in the table.
- Noise floor: the sd of the abilities of the four same-config samples (base + cue, RL plain).
- Logits per 1,000 extra tokens (test-time methods only: restart, vote k = 2, 3, 4, vote after restart, tie_short) =
  shift / (tokens per problem minus the tokens of one sample) x 1,000, within the base and within RL.
- Theta sweep: shift against theta (0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, cue); a line through theta 0 and 1 is the linear
  prediction; the random-difference control is reported on the same scale.

## Transfer test (MATH-500 -> hard328)

Arms on both sets with per-problem vectors: RL plain, RL cue, theta 0.25 cue, theta 0.5 cue, Code-RL cue (5 test arms;
base + cue is the reference; base plain has no MATH-500 vector at T 1.0). Leave one arm out: fit b on the 328 without the
held-out arm, compute the base ability there, and predict the held-out arm's right count of 328 by five rules:

- L1 Rasch logit: sum_i sigmoid(a_base328 + d + b_i), d = the arm's MATH-500 shift.
- Lc Rasch logit, calibrated: the same with c d, c = least-squares slope of hard328 shift on MATH-500 shift over the other
  test arms (one number: the exchange rate between the two sets' logit scales, which differ because 7 arms resolve item
  difficulty less well than 36).
- M marginal logit: logit(acc328) = logit(base acc328) + logit(acc500) - logit(base acc500). No item model.
- P point: base328 + 328 x (acc500 - base acc500).
- R relative error: err328 = base err328 x err500 / base err500.

Score: mean absolute error in problems over the 5 arms, against the rerun noise (164 against 160 for the same cell, 4
problems; binomial sd of one cell about 6 to 7).

Hypothesis H1: logit transfer (L1 or Lc, whichever is better is NOT allowed: the claim is about Lc, the rule used for the
filed predictions) has a lower mean absolute error than P. Refuted if the error of Lc is not lower than the error of P.
H2: Lc is better than M (the item model adds something beyond the logit of the total). Refuted if Lc is not better than M.
H3: ability is linear in theta between 0 and 1. Refuted if theta 0.5 is more than 2 noise-floor sd off the line.
A wrong prediction is reported as a result.

Planted test (`analysis/rate_test.py`, must pass before the real transfer numbers are read): (1) simulated arms from a known
1-D model on two sets of different difficulty: Lc must recover the held-out counts within sampling noise and beat P;
(2) one arm with a planted set-specific effect (+1.2 logits on the first set, 0 on the second) must show a transfer error
above 3 sd of the sampling noise.

## Predictions filed before the results are read

Rule Lc with c fitted on all 5 test arms; P and R are filed beside it as baselines. 80 % interval: 2,000 draws, each with a
bootstrap of the MATH-500 problems (shift), a bootstrap of the 328 (reference ability), c drawn from its leave-one-out
values, and a Bernoulli draw of the cell.

| Cell | Shift used |
|---|---|
| hard328 base + cue, vote over 4 after restart | MATH-500 vote-after-restart ability minus pooled base samples |
| hard328 RL plain, vote over 4 after restart | the same within RL, applied to the hard328 RL plain ability |
| hard328 RL-written shots (base + cue) | shots_rl minus pooled base |
| hard328 top-8 directions, cue | top8_plain minus pooled base (no cue cell on MATH-500; upper end widened to theta 0.5 cue) |
| hard328 vote-distillation V cue, V plain | no MATH-500 shift exists (trained on MATH-500). Category prior: half the vote-over-4 shift, interval from shift 0 to the full vote shift |
| hard328 unfiltered control U cue, U plain | category prior: shift 0, interval from -0.3 to +0.3 logits |
| MATH-500 shots, second draw of the 3 examples (3 arms) | shift of the first draw (same ability); interval = two-draw sampling noise x 1.25 |
| MATH-500 Think-SFT cue, vote over 4 | on file from `axis.py`: 471.5 +/- 7; second value: sft1_cue ability + base vote shift |

The V/U rows are not derived from a measured shift and are marked so. Any cell whose number was seen before the commit that
files the prediction is marked "seen, not a prediction". Seen so far: the text of work-1a972a says an earlier hard328 RL run
without restarts "had 246 of 328" (result-1dedfe; not opened).

## Outputs

`results/rate/math500-01/` (table.json, table.md, run.json, readout.json), `results/rate/transfer-01/` (readout.json,
run.json), `results/rate/predict-01/` (predictions.json with the commit and time filed, run.json; scores added in
`scored.json` when the cells finish).
