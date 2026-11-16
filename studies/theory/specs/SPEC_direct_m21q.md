# Direct tests m21open-01 and m21hard-01: what are m21's 60 quick wrong answers?

Round 13, pair s2 (`studies/theory/results/wide/round-13/jobs/rivals-s2.json` in the theory worktree). Both plans read
the same rows, so one script runs both. Board work-16161e.

## The surprise

Round-09 cell m21 (base Olmo-3-1025-7B + 1.0 x top-8 directions of RL-Zero-Code minus base, plain prompt, MATH-500
first 250, T 1.0) had 60 quick wrong answers (n_generated <= 1,000, not a cap hit, v3 score not 1), result-ac7104.
The readers forecast 18-25.

## The two rivals and what each predicts for both numbers

- a (round-13/s2-a, "partial opening switch"): on math text Code's directions flip only about half the samples into
  deliberation; the rest stay plain-base answer-first, and those give the quick wrongs. Predicts s_Q (answer-first
  share of Q) near s_N (the plain base's own quick wrongs), and r_Q near r_N.
- b (round-13/s2-b, "code-commit policy"): Code's directions switch nearly every sample into deliberation and add an
  early-commit habit; the quick wrongs are short deliberative attempts on medium problems. Predicts s_Q far below
  s_N, and r_N - r_Q >= 0.10.

Plan a's number (s_Q) follows from a and is opposed by b; plan b's number (r_N - r_Q) follows from b and is opposed by
a. Each plan is one rival's own test; the other rival predicts the failing side.

Dependence on refuted r5-m03-rival: no. That claim ("the top-8 Math edit is an incomplete per-sample switch; short
answers are the unswitched base and about 50 % right") was refuted by result-d02d46 (Math top-8 1x with the cue:
short answers 82.9 % right). Rival a is the same kind of mechanism moved to Code's directions under the plain prompt,
where no cue sets the opening. Plan a does not use the refuted 50 % figure or any Math-cell number: it measures the
opening text of m21's own quick wrong rows. The refutation does not transfer, because the cue was what fixed the
opening in d02d46's cell. (For context only: in m21, 61 quick right vs 60 quick wrong, metrics.json.)

## Files

- Q rows: `runs/abaybektursun-1115-103050-eae1/answers.jsonl` (m21's raw rows, 250, field `text`; copied from the
  Modal output of job abaybektursun-1115-103050-eae1; not committed). The committed
  `studies/theory/results/experiments/cell-r9-m21-01/per_problem.json` has the same 250 rows without text; the script
  asserts that its quick_wrong flags match Q.
- N rows: `studies/rlneurons/results/rln4/t1_t3_items-01/per_problem.json`, problems 0-249, T3 = base, plain prompt,
  T 1.0 / top-p 1.0, field `t3_start` (first 240 characters of the answer).
- Cued-base solve rates: `studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl`.

## Computation

Q = m21 rows with n_generated <= 1000, cap_hit false, score_v3 != 1 (60 rows, checked before writing).
N = T3 rows, problems 0-249, t3_generated_tokens <= 1000, t3_cap_hit false, t3_right 0 (105 rows, checked before
writing).

Plan a. Per row take the first 240 characters (m21: `text[:240]`; T3: `t3_start`). Answer-first (AF) if it contains
`Answer:` or `\boxed`, or if after stripping whitespace and `$` it starts with a digit, `-`, `\frac` or `(`. Otherwise
not AF. s_Q, s_N = AF shares. Statistic s_Q - s_N, 90 % bootstrap (10,000 resamples of Q rows and N rows,
independently, seed 0); the floor test uses s_Q's own 90 % interval for the report only, the verdict uses point values.

Change from the plan, with reason: the plain prompt ends with `Remember to put your answer on its own line after
"Answer:"`, so a deliberative reply that first echoes or finishes that sentence can contain `Answer:` in its first 240
characters. A stricter rule is frozen now: AF_strict = AF and none of `Okay`, `Let me`, `Let's`, `I need`, `First`,
`Step` occurs before the first AF marker. I read 10 Q rows and 10 N rows by eye against the plan's rule. If 2 or more
of those 20 are misclassified by the plan's rule, the verdict uses AF_strict; otherwise it uses the plan's rule. Both
are reported. Empty replies (m21 has 10 among Q, n_generated 1) are not AF under both rules, as the plan's rule says;
the share with empties left out is reported as a side number only.

Plan b. Per problem, k/4 = cued-base solve rate over samples 0-3 of rows.jsonl (attempt 0, first row per sample;
right = score_v3 == 1 and not cap_hit). r_Q, r_N = mean k/4 over Q's and N's problems. Statistic r_N - r_Q, 90 %
bootstrap over problems (Q and N resampled independently, 10,000, seed 0).

## Refuting observations (frozen)

- m21open-01 (rival a) refuted if s_Q < s_N - 0.15, or s_Q < 0.40.
- m21hard-01 (rival b) refuted if r_N - r_Q < 0.10.

## Nulls

- a: the plain base's own quick wrong rows N on the same 250 problems, not a random split. Expected from the T3 wrong
  example (`**Answer: $120$`) to be mostly AF.
- b: the same N, scored for cued-base difficulty; fact 1 put Math top-8 plain's quick wrongs at 0.818.

## Instrument checks

- The AF rule must call N (plain base quick wrongs) mostly AF and the plain base's long right answers (T3 right,
  > 1,000 tokens, problems 0-249) mostly not AF; if not, the rule is broken and the verdict for a is undecided.
- For b, a planted check: r over the cued base's own solved-by-all problems must be 1.0 and r over random problems
  must equal the overall mean within the bootstrap noise.

## Seen before writing

Field names of the three files; |Q| = 60 with 10 empty texts; |N| = 105; the prompt text of m21; the first row of each
file. No AF share and no solve rate was computed.
