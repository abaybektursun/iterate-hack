# Direct test rlfail-01: round-15/account-1/c3 (theory round 15, new consequence)

Plan: section `round-15/account-1/c3` of `studies/theory/results/wide/round-15/synthesis_tests.md` (same entry in
`synthesis_tests.json`; context `account-1.json`). Board work item: work-1fde65 (idea work-4948a7). Written and pushed
before the statistic was computed.

## Claim

If the 1.5x top-8 edit carries RL's shared shift but not its problem-specific choices (S6), then on hard328 problems
where RL plain gets none of its 4 samples right, the edit keeps at least most of the cued base's right answers (as F20
found on code). If the edit copied RL's per-problem outcomes, it would lose them.

## Does an earlier result decide it?

No. result-95a4dc gives the edit's totals (200.25 mean per sample, 214 under the vote) and says "edit alone right on 8,
RL alone on 15" under the vote over 4; it does not split per-sample right answers by RL's per-problem outcome.
result-124593 (dial-01) splits by the base's outcome, not RL's. result-366377 and codecopy-01 test the same idea on
code only (F20). `tools/recall.py` returned nothing that gives this ratio on hard328.

## Files and rows

- Edit: `studies/rlneurons/results/day1_3/hard328_top8x1.5_cue_s4-01/rows.jsonl` (job abaybektursun-1115-055641-b417),
  base + 1.5x top-8 RL-Math directions, cue, T 1.0 / top-p 1.0, cap 16,384, 328 problems x 4 samples, attempt 0 only.
- Base: `studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl` (job abaybektursun-1114-200457-e8e6),
  cued base, attempt 0, samples 0-3 (restart attempts 1-2 excluded).
- RL: `studies/rlneurons/results/day1_3/hard328_rl_plain_s4r2-01/rows.jsonl` (job abaybektursun-1114-200505-5ff2),
  RL-Zero-Math plain prompt, attempt 0, samples 0-3 (restarts excluded).
- Grade: stored `score_v3` (grader v3), unchanged.
- Raw text for reading rows and for examples.json: `runs/<job>/answers.jsonl` in the main checkout (not committed).

## Computation

1. For each run, keep attempt-0 rows; assert each of the 328 problems has exactly samples 0-3 (problems missing any of
   the 12 rows are dropped; none expected).
2. Select problems with RL right in 0 of 4 (attempt 0). Let P be their number.
3. E = sum of the edit's right samples over P problems (4 per problem); B = the same for the base (attempt 0, samples 0-3).
4. Statistic R = E / B (unitless).
5. 90 % interval: percentile bootstrap over the P selected problems, 10,000 resamples, numpy default_rng(0), recompute
   E/B in each, 5th and 95th percentiles.
6. n = 4 x P (edit rows). Test needs n >= 50.
7. Null value on these rows: the edit copying RL's outcomes in full gives E = RL's right samples on these problems = 0,
   so R = 0; copying two thirds of samples gives R = 1/3. Both lie in the null range [0.0, 0.5].
8. Descriptive (not part of the verdict): E/B on problems where RL has 1-4 of 4 right and on all 328; P counts of
   problems where base and edit have at least one right; cap hits of edit and base on the selected problems.

## Ranges fixed in advance

- account-1: [0.75, 4.0]
- null: [0.0, 0.5]

## Verdict rule (engine 14)

- holds: the 90 % interval lies wholly inside [0.75, 4.0] and n >= 50.
- refuted: the 90 % interval lies wholly outside [0.75, 4.0].
- otherwise undecided; state the n that would decide (interval half-width scaled by sqrt(n)).
- Report where R and its interval fall relative to the null range [0.0, 0.5].

## Instrument checks

- Totals over all 328 must reproduce the stored metrics: edit 801 right of 1312, base attempt-0 634, RL attempt-0 800.
- Planted failure: replace the edit's right flags with RL's own right flags; R must be exactly 0 (inside the null range).

## Outputs

`studies/theory/results/direct/rlfail-01/`: `metrics.json`, `examples.json` (one edit row entering the statistic
scored right and one scored wrong, with prompt and answer tail), `run.json`, `rows.json`.
