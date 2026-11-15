# Direct test wrongagree-01: rival pair round-14/s5 (a: scattered slips, b: one attractor per problem)

Plan: `studies/theory/results/wide/round-14/jobs/rivals-s5.json`, field `test`. Surprise: the cued base's vote over 12
on MATH-500 is 466 of 500 (result-1c9e40). Board item work-0cf63d. Written before computing.

## Claim

On contested MATH-500 problems, the cued base's wrong answers (12 stored T 1.0 samples) either scatter (rival a: pooled
pairwise agreement low but above chance) or concentrate on one attractor value per problem (rival b: high agreement).

## Files and rows

- `studies/rlneurons/results/votek/math500_base_cue-01/rows.jsonl` (6,000 rows, 500 problems x 12 samples, all
  attempt 0), `studies/rlneurons/results/votek/math500_base_cue-02/` (no rows.jsonl: it holds only metrics, examples,
  run.json), `studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl` (2,137 rows, the same seeds).
- Pooled in that order; keep attempt 0 (or no attempt field) and the first row per (problem_index, sample), samples
  0-11. The first folder covers every (problem, sample), so all kept rows come from votek/math500_base_cue-01.
- Answer-bearing: cap_hit not true, finish_reason != "length", extracted_v3 non-empty after strip(). Right:
  answer-bearing and score_v3 == 1. Wrong: answer-bearing and score_v3 == 0.
- Contested set P: at least 1 right and at least 2 wrong answer-bearing samples among the 12. Plan expects about 120.

## Computation

1. For each p in P, all unordered pairs of its wrong answers; a pair agrees when `rln4_lib.agree(norm_v3(x),
   norm_v3(y))`, the comparison the team vote uses (`studies/rlneurons/analysis/votek.py` `agree_table`).
2. Statistic = sum of agreeing pairs / sum of pairs over P.
3. 90 % interval: percentile bootstrap over problems of P, recompute the pooled ratio.
4. Null: for each p, draw one other contested problem q whose gold has the same type (integer or not), pair each wrong
   answer of p with each wrong answer of q, pool agreement over P; average over 200 draws.

## Frozen ranges (copied from the plan)

a [0.07, 0.3], b [0.42, 1.0], null [0.0, 0.05]. n >= 50 problems required.

## Verdict rule (engine 14, rival pair)

- 90 % interval wholly inside one rival's range: that rival holds, the other is refuted.
- Interval wholly outside both ranges: both refuted.
- Interval straddling a range boundary: undecided for the rival(s) whose range it touches; a rival whose range the
  interval does not touch is refuted. n < 50: both undecided.

## Instrument checks (before the readout)

1. The team vote (`votek.vote` with `agree_table`) on the same kept rows reproduces result-1c9e40: 446 (samples 0-3)
   and 466 (samples 0-11). Stop if not.
2. Planted inputs: every wrong answer of each problem set to one string must give 1.0; every wrong answer replaced by a
   distinct non-matching string must give 0.0.

## Changes from the plan (noted before computing)

- Bootstrap: 10,000 resamples with numpy default_rng(0), as the direct-test brief requires; the plan said 2,000.
- Gold type: the plan points to "the normalisation in facts.json r7-m09". No facts.json holds it; the function is
  `is_int` in `studies/theory/results/engine/round-07/tests/r7-m09/p2.py` (strip $ and spaces, unwrap a whole \boxed{},
  drop thousands commas, integer if it matches -?\d+). That function is used.
- Null draws use numpy default_rng(1), separate from the bootstrap generator.

## Outputs

`studies/theory/analysis/direct_wrongagree.py` writes `studies/theory/results/direct/wrongagree-01/`: metrics.json,
examples.json, rows.json (one row each for round-14/s5-a and round-14/s5-b).
