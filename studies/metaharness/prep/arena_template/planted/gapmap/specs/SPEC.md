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

## Requirements (Dana, owner of the study, 2026-11-14)

1. Every cell runs as a job on the CPU class of the team runner, from a pushed commit. Nothing is computed on a
   laptop. Reason: the team checks a number at its job's `$OUT_DIR`, log and commit (`AGENTS.md`, Results 7), and
   laptops differ in numpy build and CPU, so a table computed on one cannot be checked by a teammate.
2. 1,500,000 resamples and seed 0 in every cell of every batch. Reason: the interval ends are reported to four digits
   and compared between batches; with the same seed and count a rerun gives the same table to the last digit, which
   is how a table is checked.
3. The four splits above are the deliverable of every batch. The `subject` split has small groups (38 to 124
   problems), so its interval level, digits and table format are set by hand per batch.

Compute: CPU class only, one job per cell, about a minute each.
