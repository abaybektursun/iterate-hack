# Direct test m21short-01: shared test of rival pair round-14/s4

Plan: `studies/theory/results/wide/round-14/jobs/rivals-s4.json`, field `test` (written by the round-14 coordinator in
the theory worktree; not yet on origin/theory when this spec was written). Board work-d1a1ed.

## Claim

Surprise: round-09 m21-r1, 60 quick wrong answers of 250 from base + 1.0 x Code-RL top-8 directions on MATH-500 plain
(result-ac7104).

- s4-a: Code's top-8 directions push every sample that starts working on the problem into full Math-like deliberation;
  only non-solution openings stay plain-base. So almost no right answer stays plain-short: S about 0.03-0.10.
- s4-b: the edit is an all-or-none per-sample lottery with s about 0.47 at 1x; about 0.36 of m21's right answers are
  untouched plain-base answers, half of them below the plain base's median: S about 0.18-0.28.

## Statistic

S = fraction of m21 right rows with n_generated <= L, where L is the median generated tokens of the plain base's (T3)
right, not cut off answers on problems 0-249.

## Files and rows

- m21: `runs/abaybektursun-1115-103050-eae1/answers.jsonl` (local copy in the cells-r9b worktree; job
  abaybektursun-1115-103050-eae1). First row per problem_index 0-249, kept if score_v3 == 1 and cap_hit is not true.
  Plan expects 157 rows.
- Plain base T3: `studies/rlneurons/results/rln4/t1_t3_items-01/per_problem.json`, problem_index 0-249 with t3_right
  == 1 and t3_cap_hit false; field t3_generated_tokens. Used only to set L.

## Computation

1. L = median of the kept T3 generated tokens (mean of the two middle values for an even count).
2. S = (kept m21 rows with n_generated <= L) / (kept m21 rows).
3. 90 % interval: 10,000 bootstrap draws resampling problems 0-249 with replacement (numpy default_rng(0)), recomputing
   L and S in each draw; 5th and 95th percentiles.

## Null

No edit: a plain-base draw against its own median gives 0.50 by construction, spread at n 157 about [0.43, 0.57].

## Frozen ranges (copied from the plan)

a [0.0, 0.12], b [0.15, 0.36], null [0.41, 0.60].

## Verdict rule (engine 14, rival pair)

An interval wholly in one rival's range holds that rival and refutes the other. An interval in neither range (wholly
outside both) refutes both. An interval straddling a range boundary is undecided for the rival(s) it touches. n >= 50
required to hold.

## Instrument checks before the readout

- Reproduce the posted counts from the same rows: m21 right 157/250 and quick wrong 60 (result-ac7104); plain base T3
  right 107 on problems 0-249 (result-ac7104 "right 107"). Stop if they do not reproduce.
- answers.jsonl n_generated equals n_new in the committed `cell-r9-m21-01/per_problem.json` for every kept row.
- Failing input: run the same S code on the plain base's own right rows against their own L; it must give about 0.50
  (inside the null range) and not a value in a or b.

## Changes from the plan

- T3 right and not cut off is 106 rows on problems 0-249, not "about 107": one T3 right row is a cap hit. Checked
  before computing L; L itself was printed during this check (1069 tokens), before any m21 statistic was computed.
- The first run of the check "n_generated equals n_new of per_problem.json" failed on 246 of 250 rows: n_generated =
  n_new + 1 (the stop token). The T3 lengths (`rln4_t1_t3_items.py`, field `tokens` = `n_generated`) use n_generated
  too, so S uses n_generated on both sides as the plan says. The check is now: n_new equals the committed n_new, and
  n_generated - n_new is 1, or 0 for a cap hit. Changed before S was computed.
- Duplicate note: the round-14 duplicate judge called s4-b a restatement of r5-m03-rival (refuted, result-d02d46).
  That refutation measured Math's top-8 edit (short answers 82.9 % right, predicted 50 %), not Code's. It does not
  decide s4-b, which claims s about 0.47 for Code; the shared test is run regardless.
