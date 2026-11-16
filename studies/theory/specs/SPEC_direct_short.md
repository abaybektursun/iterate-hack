# Direct test of run-02/f2-m01: do hard328 solutions need long samples?

Written 2026-11-15 before any number below was computed (only the first 8 rows of the hard328 file had been seen). Board
work-4c1119. Offline, stored rows only, no GPU, no forward pass.

## The mechanism

run-02/f2-m01 (`results/forecast/run-02/mechanisms.json`; -1.77 nats over 9 results in round-12 `standing.md`, not carried):
"The autobench agent works under a fixed generation time per experiment, so it buys votes by shortening each sample (its
best config: 10 samples at about 1,100 tokens each). Most MATH-500 problems are solved in under 2,000 tokens, so short
samples plus a vote score well on dev100, but hard328 solutions need 6,000-14,000 tokens and short samples never reach
them."

Engine 12's plan (round-12 copy, `direct_tests.md`, not committed): "under 20 % of the hard328 problems the cued base solves
have a right sample of 2,000 tokens or fewer".

## Does the claim follow from this cause alone?

The cause says right answers to hard328 problems are long (6,000-14,000 tokens), so a sample of 2,000 tokens or fewer
rarely holds one. The other top mechanisms say nothing about the base's solution lengths:
- "directions act as far as the text drives their inputs" (run-05/f2-m03): about RL weight directions; silent on the base.
- "an added RL change depends on its host" (round-10/weights-m03): about weight edits on Think-SFT; silent on the base.
- "accuracy depends on how the answer ends" (run-03/f2-m04): about the answer marker; it predicts nothing about which
  lengths are right.
So the claim is this mechanism's alone; a refutation buries its stated cause, a hold does not support any rival.

The plan's claim on hard328 alone is weak: a share below 20 % could hold on every set if the base rarely writes short
answers at all. The mechanism makes a contrast, so the test adds its MATH-500 half ("most MATH-500 problems are solved in
under 2,000 tokens") as the matched control. That control is also the instrument check: the same readout must give a high
share there, or it cannot tell the two sets apart.

Already posted, not deciding: result-6e7b64 (autobench's final method, 12 samples at T 0.6 capped at 4,096 tokens, vote:
139/328 on hard328, against 160 for one cue sample) and result-2c2cae (47 of 328 first base answers end under 2,000 tokens;
how many are right is not posted). Neither gives the share of solved problems with a short right sample.

## Data (committed rows, grader v3 as stored)

- `studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl`: base + cue, hard328, T 1.0 / top-p 1.0, cap
  16,384, 4 samples per problem, a cap hit resampled up to 2 times (1,731 rows).
- `studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl`: the same on MATH-500 (2,137 rows).

Every row counts (restart attempts too: each is a fresh sample; a right row is never a cap hit). Length = `n_new`.

## Readouts (`analysis/direct_short.py`)

Solved problem: at least one row with `score_v3 == 1`. For a cut c, `S(c)` = share of solved problems with at least one
right row of `n_new <= c`. Intervals: 90 % percentile bootstrap over solved problems, 10,000 draws, seed 0.

- P1 (primary, decides): `S(2000)` on hard328.
- C1 (control, the mechanism's other half): `S(2000)` on MATH-500.
- Secondary, no verdict: `S(1100)` and `S(4096)` on both sets (1,100: the mechanism's sample length; 4,096: autobench's
  actual cap); share of right rows with `n_new <= 2000`; median `n_new` of right rows (the mechanism says 6,000-14,000 on
  hard328, bootstrap over problems); on hard328 problems with a short right row, the share of all their rows that are right
  (are short right answers on problems the base finds easy).

## Decision rule, fixed now

- Holds: P1's upper 90 % bound below 20 % and C1's lower bound above 50 %.
- Refuted: P1's lower bound at 20 % or more, or C1's upper bound below 50 %.
- Otherwise undecidable.

Refuting observation: 20 % or more of the problems the cued base solves on hard328 have a right sample of 2,000 tokens or
fewer (lower bound), i.e. short samples do reach hard328 solutions.

## Outputs

`studies/theory/results/direct/short-01/`: `readout.json` (every number with n and interval), `examples.json` (one solved
hard328 problem with a short right row, one with none; each with the problem text and all its rows), `reading.md` (10 raw
rows of the deciding group: hard328 right rows of 2,000 tokens or fewer, with problem text; the answer texts are not
stored in the committed rows), `run.json`.
