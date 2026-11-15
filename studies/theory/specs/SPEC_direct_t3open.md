# Direct test t3open (theory round 15, `round-15/account-3/c1`)

Written before the statistic was computed. Plan: `studies/theory/results/wide/round-15/synthesis_tests.md`, section
`round-15/account-3/c1`.

## Claim (account-3)

Plain-prompt base answers that happen to open deliberatively are already in the cue's mode, so on the same problems
they are right about as often as the cued base's answer. A prompt only selects a mode the weights hold. If the cue
added something beyond choosing the mode, those answers would sit near the plain rate instead.

## Rows

`studies/rlneurons/results/rln4/t1_t3_items-01/per_problem.json`: 500 MATH-500 problems, one sample per cell, grader v3.

- T3: untrained base (Olmo-3 7B base), plain prompt, T 1.0 / top-p 1.0 (224 of 500 right).
- T1: the same base with the cue, same sampling (410 of 500 right).

## Flag rule "opens deliberatively" (fixed before any outcome was read)

Only `t3_start` (the first 240 characters of the T3 answer) is read. The answer is flagged when the case-sensitive
regex `\b(Okay|Alright|Hmm|Let me|Let's|I need to)\b` matches in the first 240 characters and the match starts before
the first equation marker, where an equation marker is the first `$`, `=`, `\(` or `\[` in those 240 characters. With
no equation marker, any match counts. Counting starts only (no outcomes): 174 answers contain an opener, 149 have it
before the first equation marker, so n = 149 flagged.

## Statistic

For flagged problems, d_i = t3_right_i - t1_right_i (grader v3, stored in the rows). Statistic = mean d_i, in
fraction of problems. 90 % interval: 10,000 bootstrap resamples of the flagged problems (seed 0), 5th to 95th
percentile. Also reported: the share of the 500 that are flagged, T3 and T1 right counts on the flagged set.

## Null

Opening irrelevant: the same mean of d_i on the unflagged problems (overall T3 - T1 is -0.372). Also reported with a
bootstrap interval.

## Ranges fixed in advance

account-3 [-0.15, 0.10]; null [-0.65, -0.22].

## Verdict rule (engine 14)

Holds only if the 90 % interval lies wholly inside [-0.15, 0.10] and n >= 50; refuted if the 90 % interval lies
wholly outside it; otherwise undecided, with the n that would decide stated (interval half-width scaled by
sqrt(n / n_needed)). Where the value falls relative to the null range is reported.

## Known confound (stated in advance)

Flagging is by T3's own output, so it selects problems; an answer that opens deliberatively may also be on an easier
problem. The unflagged null computed on other problems shares this confound in the other direction. T1 right on the
flagged set is the within-problem control.

## Outputs

`studies/theory/analysis/direct_t3open.py` writes `studies/theory/results/direct/t3open-01/metrics.json`,
`examples.json` (one flagged row with T3 right and one with T3 wrong, real starts and answers) and later `rows.json`.
