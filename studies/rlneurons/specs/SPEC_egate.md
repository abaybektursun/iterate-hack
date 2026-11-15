# Entropy-gated temperature: where does low temperature help, and where does it loop? (board idea-069f19, work-deec92)

Written 2026-11-15 04:58 UTC, before any job of this spec ran. Branch `egate`.

## Question

The cued base is more accurate at T 0.6 when it finishes (378 right at T 0.6 against 361 to 364 at T 1.0 on the same 402
MATH-500 problems, board knowledge-13cff3), but at T 0.6 it hits the cap on 98 of 500 problems, mostly in repetition loops; at
T 1.0 it hits it on 27. Min-p 0.1 at T 1.0 shows the same pair: 404 right of 442 finished against 410 of 473, and 58 cap hits
(result-44b4df). Both rules sharpen every position. Do the accuracy and the loops come from different positions, so that a rule
can keep one without the other?

## Method

`lib/egate.py` is a vLLM logits processor. Each request runs at T 1.0 / top-p 1.0. At each position the processor computes the
entropy H (nats) of the next-token distribution at temperature 1 and divides the logits by `t_low` only on one side of a
threshold h0. h0 is the 80th percentile of H over the positions of 50 MATH-500 problems sampled at T 1.0 for 2,000 tokens each
(measured inside the screen job, before the arms; the 80 % follows the 'forking tokens' share of 2506.01939 and ReSET 2606.13233).

Arms, all base + cue, grader v3, cap 16,384, seed 61,000,000 + index (calibration 61,900,000 + index):

| Arm | Sharpened positions | t_low |
|---|---|---|
| t1 | none (T 1.0 through the same code) | |
| hi6, hi3, hi1 | H > h0 (the top 20 %) | 0.6, 0.3, 0.1 |
| lo6, lo3 | H <= h0 (the other 80 %) | 0.6, 0.3 |
| all6 | all (constant T 0.6 through the same code) | 0.6 |
| rnd6 | random positions, the same share as hi6 | 0.6 |

## Hypotheses, each with the observation that refutes it

Stage 1 is read on cap hits of 100 (first 100 MATH-500 problems, one sample). M = (cap hits of t1 + cap hits of all6) / 2.

- H-confident (ours): loops come from sharpening confident positions, where the rare tail tokens are the exits from a repeated
  block. Predicts cap hits lo6 >= M and hi6 < M. Refuted if hi6 >= M.
- H-branch (2512.12895, Prop. 3.1): loops start at uncertain branch points, where sharpening picks the easy repeat action.
  Predicts hi6 >= M and lo6 < M. Refuted if lo6 >= M.
- Both refuted (hi6 >= M and lo6 >= M): each regime alone is enough to loop. Neither refuted in that sense but both under M:
  loops need both regimes sharpened; then either gate avoids them.
- Instrument checks, which must hold or the screen is not read: all6 has at least 8 more cap hits of 100 than t1 (the stored
  cells have 98 and 27 of 500); t1 is within 8 right of the stored T 1.0 first-100 counts (job -153825-208b); the processor's
  share of sharpened positions is 0 for t1, 1 for all6, and within 0.10 to 0.35 for hi6 and rnd6 (the calibration is on the
  first 2,000 tokens, the arms run to 16,384).
- rnd6 is the control for hi6: the same share of positions, chosen blind. An effect of hi6 that rnd6 also shows is an effect of
  mild sharpening anywhere, not of the forks.

Accuracy cannot be read at n = 100 (one arm's standard error is about 4 points). Stage 1 only selects.

## Stage 2 (chosen by this rule, fixed now)

Among hi6, hi3, hi1, lo6, lo3: keep the arms whose cap hits are at most t1's + 4. Of those take the one with the most right
answers (ties: the higher t_low). If none is kept, stop: the result is that no entropy gate separates the two effects.
The chosen arm then runs on all 500 MATH-500 problems, 4 samples (seed 61,000,000 + 10,000 s + index), with the stage-1 h0.
Reference: the four stored T 1.0 samples of job -153825-208b (1,642 right of 2,000, attempt 0, v3). Readout: mean right per
sample, paired difference in points with a 95 % bootstrap over problems (5,000 resamples, seed 0), cap hits, rule-A loops, tokens
per problem.

- Prediction: the chosen arm is at least 2 points above T 1.0 with an interval above 0, at no more than 1.1 times the tokens.
  Refuted if the interval includes 0 or the gain is under 2 points.

## Stage 3: the 328, once

Only if the stage-2 interval is above 0. The chosen arm, base + cue and RL plain-through-cue as in the reference cells, one
sample, seed 61,000,000 + index, against base cue 164 and RL 206 of 328 (jobs -151534-e72c, -151540-86ef). RL runs the same
rule (cue prompt, since egate_cell always uses the cue; RL cue reference 205). Prediction: base above 164 by at least 8
problems; RL within 6 of 205.

## Cost

One rented RTX PRO 6000 (vast.ai, 1.49 USD/h). Stage 1 about 5 M generated tokens, stage 2 about 8 M, stage 3 about 6 M.
