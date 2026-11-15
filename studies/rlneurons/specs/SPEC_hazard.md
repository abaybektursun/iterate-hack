# SPEC_hazard: a slip-hazard law for the RL gain

Board: idea-7928c0, work-26c268. Builds on result-afc423 (reliability shift), result-5da8a9 (one axis), result-855858 (fewer
wrong steps per token), result-17e25e (logit shifts, transfer). Laptop only, numpy. Written before any number below was
computed.

## The law

An answer is a chain of steps, each with a small chance of an unrecovered slip. For problem i with required work L_i and a
method j with hazard h_j per unit of work, P(right) = exp(-h_j L_i). A method acts by multiplying h by one factor on every
problem. As an item model: -log p_ij = exp(-(a_j + b_i)), i.e. log(-log p_ij) = -(a_j + b_i) (the "hazard link"; the
complementary log-log link applied to failure). h_j = exp(-a_j), L_i = exp(-b_i). The hazard ratio of method j against a
reference is HR = exp(-(a_j - a_ref)); HR < 1 is fewer slips. The competing model is Rasch: logit p_ij = a_j + b_i.
Both have one parameter per arm and one per problem.

## Inputs

`results/axis/{math500,hard328}-01/vectors.json` (36 single-sample arms x 500; 7 x 328, grader v3), the Day-1 #3 rows
(`results/day1_3/math500_{base_cue,rl}-01/rows.jsonl`: 4 samples, `n_new` tokens, attempt 0) and vote vectors through
`rate.day1_3`, `results/rate/math500-01/table.json` (tokens per problem). Loaders and the logit fit are imported from
`analysis/axis.py` and `analysis/rate.py`.

## Fit

- Logit: `axis.fit` unchanged. Hazard link: the same Adam loop, ridge on b, steps and learning rate, with the residual of the
  hazard link (z clipped to [-4, 15]). Check: doubling the steps changes the held-out log-likelihood by less than 1e-4 nats
  per cell for either link; otherwise the steps are raised for both.
- Ridge on b chosen per link from the grid of `axis.heldout` (0.01 to 3) on the same 5 folds (`default_rng(0).integers(0, 5,
  Y.shape)`), so each link gets its best ridge and the same number of parameters.
- Problems solved by every arm (or by none) carry no information about the link: both models put b at the value the ridge
  allows and predict p near 1 (or 0). They stay in the matrix for both models, with the same ridge grid. The comparison is
  also reported on the informative problems only (at least one arm right and one wrong), fitted on the same matrix.
- Ability of a pooled 0/1 vector (votes, restarts, 4 samples) given b: the maximum-likelihood a under the link (bisection on
  the score; for the logit link this is the equation `rate.solve` solves). Intervals: bootstrap over problems, 2,000
  resamples, seed 0, b fixed.

## Hypotheses, each with the observation that refutes it

H1 (link). The hazard link fits held-out cells better than the logit link. Statistic T = held-out log-likelihood per cell,
hazard minus logit, 5 folds over all observed cells. Nulls: T on 200 matrices simulated from the fitted logit model and on
200 from the fitted hazard model (ridge fixed at the value chosen on the real matrix; same folds). Verdict rule, fixed here:
"hazard" if T is above the 95th percentile of the logit-simulated T and not below the 5th percentile of the
hazard-simulated T; "logit" if the mirror holds; "cannot tell" if T is inside both; "neither" if outside both. Also
reported: the per-fold differences (sign and sd), and the same T in-sample. Power = the share of hazard-simulated matrices
whose T is above the 95th percentile of the logit-simulated ones (and the mirror). H1 is refuted if the verdict is not
"hazard", or if T is not larger than 2 standard errors of the 5 fold differences. If power is below 0.8 in both directions
the result is "the two links are not separable with 36 arms x 500 problems", reported as a null.

H2 (constant hazard ratio). Each method's shift against the pooled 4 base + cue samples is the same at every difficulty.
Problems are sorted by b fitted without the base samples and without the method's own vectors and cut into three groups
that hold equal thirds of those other arms' wrong cells (so neither compared arm sets the groups). Within a group the
abilities of the method and of the reference are fitted with b fixed; the statistic is the shift in the hardest group minus
the shift in the easiest, under each link. Noise in b biases this statistic, so it is compared with its distribution on
100 matrices simulated from the same link's fitted model. H2 is refuted for RL (4 pooled RL plain samples; primary) if the
hazard-link statistic lies outside the central 95 % of the hazard-simulated statistic. The same test under the logit link
says whether the odds ratio is constant instead. Reported for RL plain, RL cue, theta 0.25 / 0.5 / 0.75, Think-SFT cue,
Code-RL cue, base vote 4, RL vote 4 (against the RL samples).
Table: HR of every arm of the rate table against pooled base + cue, with 95 % interval and tokens per problem; vote k = 2,
3, 4 within each family.

H2b (theta). log HR is linear in theta between 0 and 1 where the logit shift was not (theta 0.25 had 57 % of the shift).
Refuted if log HR at theta 0.5 is off the line through theta 0 and theta 1 (RL cue) by more than 2 sd of the base noise
floor (sd of the 4 base samples' hazard abilities), as in SPEC_rate H3.

H3 (transfer). MATH-500 -> hard328, the 5 arms and the leave-one-arm-out procedure of SPEC_rate, with the hazard link.
Rules: Hc (hazard shift times c, c fitted on the other arms; the hazard twin of Lc and the rule used for the filed
predictions), H1 (c = 1: the law verbatim, same hazard ratio), MH (no item model: acc328 = ref328 ^ HR, HR = log acc500 /
log ref500). Check: the same code with the logit link reproduces Lc 5.07 and L1 5.99. H3 is refuted if the mean absolute
error of Hc is not below P (5.14 problems); a difference below 1 problem is a tie (rerun noise 4, binomial sd 5.7) and is
reported as "no better".

H4a (chain length). A problem's fitted work L_i = exp(-b_i) (hazard link, b fitted without that model's own 4 samples)
rises with the token length of its RIGHT answers (mean `n_new` of the right samples), within base + cue and within RL.
Statistic: Spearman correlation of -b_i with log mean right-answer tokens over problems with at least one right sample;
null: tokens shuffled across problems, 2,000 shuffles. Refuted if the correlation is inside the central 95 % of the
shuffles. Also reported: the slope of -b_i on log tokens over informative problems (the law with a per-token hazard that is
the same on every problem predicts slope 1; a slope above 1 means harder problems have a higher hazard per token, not only
more tokens), and RL's HR beside the ratio of located first wrong steps per token, 0.015 / 0.038 = 0.39 (result-855858).

H4b (independent slips). Given the problem, the 4 samples of one model fail independently: k_i right of 4 is binomial at
p_i, p_i from the hazard model with b fitted without that model's samples and a = the model's pooled ability. Statistic:
D = sum_i (k_i - 4 p_i)^2 / sum_i 4 p_i (1 - p_i). Noise in b inflates D, so the null is D on 200 matrices simulated from
the fitted hazard model (independent cells) and passed through the same steps. Refuted (failures are correlated within a
model beyond the common difficulty axis: wrong plans specific to the model) if D is above the 95th percentile of the
simulated D for base + cue or for RL. Vote check: predicted vote-over-4 right count = sum_i sum_k Bin(k; 4, p_i) g(k), g(k) =
the stored share of votes right among problems with k right samples (both families pooled); compared with the stored 446
(base) and 474 (RL); a stored vote more than 2 simulated sd below the prediction is correlated failure.

## Planted tests (`analysis/hazard_test.py`)

1. A matrix simulated from a hazard model with a wide ability range (arms from 5 % to 99 % right, 36 x 500) must give the
   verdict "hazard"; the same from a logit model must give "logit".
2. A matrix with 4 arms x 100 problems must give "cannot tell" from either model.
3. The power at the real size (36 x 500, the fitted abilities) is reported from the 200 + 200 simulations of H1, whatever
   it is.
4. H2: on hazard-simulated matrices the hazard-link statistic is centred on its own null; an arm planted with HR 0.2 on the
   hardest third and 1.0 elsewhere must fall outside the 95 % range.
5. H4b: four samples that share a per-problem failure (planted: with probability 0.3 all four are replaced by one draw)
   must give D above the 95th percentile.

## Predictions

Before reading the board for cells that finished after `results/rate/predict-0*` were filed, the hazard rule Hc (with H1 and
MH beside it) files its own numbers for the same cells in `results/hazard/predict-01/predictions.json`, in a pushed commit:
hard328 base + cue and RL plain vote over 4 after restart, hard328 shots_rl, hard328 top 8 cue, Think-SFT cue vote over 4
on MATH-500 (hazard ability of sft1_cue plus the base vote's log HR). The two cells of predict-02 (179 of 328, 161 of 246)
are already known to this author: the hazard numbers for them are marked "computed after the observation". Category-prior
cells (V, U) and the second shot draws do not depend on the link and are not refiled. Then both rules are scored where a
result exists.

## Outputs

`results/hazard/math500-01/` (`run.json`, `readout.json`, `table.json`, `table.md`, `examples.json`: the stored rows of one
problem the binomial fits and one it does not), `results/hazard/transfer-01/readout.json`, `results/hazard/predict-01/`,
`results/hazard/scored-01/readout.json`.
