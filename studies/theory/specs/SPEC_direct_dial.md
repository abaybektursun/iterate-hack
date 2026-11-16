# SPEC: direct test of run-05/f2-m01, "the top-8 RL directions are a signed termination dial"

Board work-1645c5. Written before any number below was computed. Stored rows only: no GPU job, no forward pass.

## The claim

Mechanism `run-05/f2-m01` (`studies/theory/results/forecast/run-05/mechanisms.json`, +7.05 nats over 8 results in
`studies/theory/results/wide/round-12/standing_v11_2.md`): adding the top-8 singular directions per matrix of
(RL-Math - base) makes the model finish (fewer cap hits), subtracting them makes it finish less. The distinctive
claim tested here: the edit's gain is finishing, not added reasoning skill. (The statement also allows "a modest
rise in correctness on problems already finished"; this test measures how large that rise is against the right
null, a second sample of the cued base.)

## Consequence that the cell counts do not test

Condition on the outcome of one cued-base sample on a problem: finished-right (FR), finished-wrong (FW), cap hit
(CH; `cap_hit` true). If the edit only adds finishing, then on FW problems (the base finished and was wrong, so
finishing was not what it lacked) the edit is right no more often than a second, independent base sample on the
same problems. Its gain over the second base sample sits in the CH group. Conditioning on one base sample makes the
group easier or harder than its label says (regression to the mean), so the null is the second base sample given
the first sample's outcome, never the first sample's own score.

## Readout

For each set, each group g in {FR, FW, CH}, each arm A in {edit 1.5x, second base sample, RL plain}:
rate_A(g) = right answers of A on problems in g / number of A samples there, pooled over the choice of the
conditioning base sample i (every i in 0..3, each problem counted once per i). Comparison samples are always on a
different seed from the conditioning sample: base j != i; on hard328, where edit, base and RL share seeds
3000000 + 10000 s + index, edit and RL samples k != i. MATH-500: the edit has one sample (seed 3000000 + index),
base and RL four on other seeds (41,000,000 and 45,000,000), so every edit and RL sample is used.

Numbers: D_A(g) = rate_A(g) - rate_base2(g), in points; share of the edit's total gain over the second base sample
that sits in FW: n_FW D_edit(FW) / sum_g n_g D_edit(g). n (problem-sample pairs) and a 90 % bootstrap interval over
problems (10,000 resamples of the 328 or 500 problems, the whole per-problem block resampled) for every number.

Signed side, -1x: hard328 one sample (seed 3000000, job abaybektursun-1115-031209-1273, raw rows on the Modal
volume, copied to the results folder without text); MATH-500 250 odd problems (seed 41,000,000, cell-r9-m11-01,
`studies/theory/results/experiments/cell-r9-m11-01/per_problem.json`). Readouts: right per finished answer at -1x
and in the base samples; on the problems where the -1x sample finished, the -1x right rate against the right rate of
the finished base samples (all four) on the same problems; and the share of -1x finished-wrong answers whose
extracted text holds the gold answer string (format failures of the unboxed "Answer:" line, not reasoning).

## Verdict rule (frozen)

- Pure dial: the 90 % interval of D_edit(FW) contains 0 on hard328 and its upper end is below half of D_RL(FW).
- Adds skill: the 90 % interval of D_edit(FW) lies above 0 on hard328 (MATH-500 reported, same rule, second reading).
- Undecided: anything else.
- Pure dial also predicts D_edit(CH) > 0 (interval above 0) and FW share of the gain below 0.5. A FW share of 0.5
  or more means finishing is not the main source of the edit's gain.
- Signed side, pure dial predicts: on problems where -1x finishes, its right rate is within the 90 % interval of the
  base's finished right rate on the same problems. Below it: -1x also removes right answers from finished problems.
- Refutes "no added skill" (and goes to `studies/theory/results/refuted.json`): Adds skill on hard328.

## Files

- Inputs, hard328: `studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl` (attempt 0),
  `.../hard328_top8x1.5_cue_s4-01/rows.jsonl`, `.../hard328_rl_plain_s4r2-01/rows.jsonl`.
- Inputs, MATH-500: `studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl` (attempt 0),
  `.../math500_rl-01/rows.jsonl`, `studies/rlneurons/results/xreward/dial15_math500-01/rows.jsonl`.
- Raw answers for reading: `runs/abaybektursun-1115-055641-b417/answers.jsonl` (hard328 edit),
  `runs/abaybektursun-1115-031209-1273/answers.jsonl` (hard328 -1x).
- Script: `studies/theory/analysis/direct_dial.py`. Outputs: `studies/theory/results/direct/dial-01/`
  (`readout.json`, `examples.json` with one item right and one wrong of the deciding group, `m1x_hard328_rows.jsonl`,
  `run.json`, `reading.md` with the 10 raw answers read by hand).
