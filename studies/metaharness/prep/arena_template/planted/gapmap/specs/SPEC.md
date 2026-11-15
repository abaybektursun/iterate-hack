# gapmap SPEC (written before the first batch)

Question: on MATH-500 at T 1.0, where does the RL model (T2) differ from the base with the opening cue (T1)? The
overall gap is 53 problems of 500 (10.6 points, `studies/rlneurons/results/rln4/t1_t2_items-01/notes.md`). The mission
(`DIRECTION.md` point 3) looks for the cheapest route to those points, so the route should start where the gap is.

Four batches, one metric each, T2 minus T1 per problem: `accuracy` (right under grader v3), `cap_hit` (the answer hit
the 16,384-token cap), `tokens` (generated tokens), `tokens_both_right` (generated tokens on the 398 problems both
models solve).

Splits of every batch: by subject (7), by level 5 against levels 1 to 4, by quartile of the RL answer's length, by
quartile of the cued base answer's length.

Method: paired bootstrap over problems, 1,500,000 resamples, seed 0, percentile interval. A group is reported as
different from the overall value only when its interval excludes the overall point estimate.

Prediction: the accuracy gap is concentrated in the longest quartile of the cued base's answers (cap hits), and is
flat across subjects. Refuted if the top quartile's interval includes the overall gap, or if one subject's interval
excludes it.

Compute: CPU class only, one job per cell, about a minute each.
