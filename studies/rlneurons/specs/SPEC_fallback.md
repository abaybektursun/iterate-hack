# SPEC fallback: late answers as fallback votes

Board idea-016ff5, work-32dfa8. Branch `fallback` (main is frozen). Written before `analysis/fallback.py` has produced any
number. Laptop only, no model run. Inputs: the committed rows of result-dd26fe
(`results/cap32vote/{hard328,fresh2026}_sft1_cue_s4-01/rows.jsonl`: Think-SFT + cue, 4 samples, cap 32,768, T 1.0 / top-p
1.0, grader v3, every answer also graded cut at 16,384) and, for the script switch only, the texts in
`runs/cap32vote_{hard328,fresh}_s4/answers.jsonl` (not in git).

## Question

At cap 32,768 one sample gains +6.7 points on hard328 over the same answer cut at 16,384, but the vote over 4 gains +1.8
[-0.9, +4.9] (238 to 244): answers that finish after token 16,384 are right 99 times of 362 (fresh2026 50 of 259), and they
tie or outvote one early right answer (vote right to wrong on 9 problems, wrong to right on 15; fresh2026 4 and 6). Does a
label-free rule that uses late answers only when no early answer exists beat both the plain 32,768 vote and the 16,384-cut
vote?

## What is already known (nothing below is blind on hard328)

- hard328 is the development set: its votes (244, 238), flips (9 / 15) and late precision are posted, and the post hoc
  "ties to the shortest" rule was found on it (252) and did not replicate on independent draws (result-3e4a54, branch
  `tieshort`). No number on hard328 is a test.
- fresh2026: the plain vote (75), the 16,384-cut vote (73), the flips (4 / 6), late precision (50 of 259) and the post hoc
  tie rule (81) are posted. So R1 minus the cut vote lies in [0, +6] and R1 minus the plain vote in [-6, +4] problems in
  the stored order before anything is run. Not known: which of the flips fall on problems with no early answer, any rule
  below, any 24-order mean.
- The plain vote gives a tie to the group seen first in draw order; the stored order can be lucky by several problems
  (result-3e4a54). Every number here is the mean over the 24 draw orders; the stored order is a secondary column.

## Definitions

A sample is late when `n_new` > 16,384, else early. Its 16,384 ballot is `extracted_v3_16` (the finished answer of an early
sample; for a late sample whatever grader v3 extracts from the text cut at 16,384, mostly nothing), scored `score_v3_16`.
Its 32,768 ballot is `extracted_v3`, scored `score_v3`. Votes are `day1_vote.vote` (groups by `rln4_lib.agree`, largest
group, ties to the group seen first in draw order). The 16,384 boundary is fixed, not tuned. No rule reads a score or gold.

- R4 (control) plain 32,768 vote: `vote` over the 32,768 ballots.
- R5 (control) 16,384-cut vote: `vote` over the 16,384 ballots.
- R1 fallback: R5's answer when the 16,384 view has any ballot; else R4's answer.
- R2 half weight: 32,768 ballots, an early sample counts 1, a late sample 0.5; largest total weight, ties to the group seen
  first.
- R3 fallback + script: as R1, but in the fallback stage late samples whose text switched script before token 16,384 cast
  no ballot (`drift.signs` unchanged: first episode's `detect_tok` <= 16,384, as in `drift_read.second_half`); if no ballot
  is left, R4's answer.
- R6 (planted control) R1 with the late flags permuted among the four samples of each problem (50 permutations per draw
  order; a sample flagged early casts its 32,768 ballot in the first stage). It reads no real length, so it must not beat
  the plain vote: expected at or slightly below R4 (its first stage is a vote over fewer samples).

Choice. The rule with the most right answers on hard328 among R1, R2, R3, by the 24-order mean; a draw (within 0.05
problems) goes to the earlier rule in that order. The choice, its dev numbers and the power are added to this file as
"Amendment 1" and pushed before fresh2026 is scored. fresh2026 is then scored once, with `--fixed chosen.json`.

## Checks before any rule (`analysis/fallback_test.py`)

- From the rows, stored order: R4 244 and R5 238 on hard328, 75 and 73 on fresh2026; flips right to wrong / wrong to right
  9 / 15 and 4 / 6; late finished answers right 99 of 362 and 50 of 259; `seq4` 245.2 at 31,732 and 239.8 at 30,807 tokens
  (24 orders), one sample 232.8 at 11,650 on hard328.
- Planted, late answers always wrong: R1 equals R5 on every problem and every order (problems with no 16,384 ballot score
  0 under both). Planted, late answers always right: R1 scores 1 on every problem with no 16,384 ballot and at least one
  late answer, and never below R4 there.
- Hand-built problems for R2 (one early answer beats one late; beats three different late; ties two agreeing late) and R3
  (a non-switched late answer beats two agreeing switched ones; all switched gives R4).
- Switch detector: sample 0 of hard328 must give the drift study's 24 switched of 93 late answers, 1 right, 22 of 69.

## Hypotheses

H1. The chosen rule beats both the plain 32,768 vote and the 16,384-cut vote on fresh2026 (n = 136). Test: paired
bootstrap over problems (`n13_score.paired_bootstrap`, 5,000 resamples, seed 0) of the per-problem 24-order means, rule
minus R4 and rule minus R5. Refuted if either 95 % interval covers 0. Power is computed on hard328 before scoring (2,000
draws of 136 problems from the 328, the same two intervals with 1,000 resamples each; power = share of draws where both
exclude 0) and written in Amendment 1. If it is under 50 %, a null on fresh2026 is uninformative, and the pooled hard328 +
fresh2026 estimate is reported as descriptive only (hard328 chose the rule).
- Prediction, hard328 (dev): R1 248 [244, 251] in both columns; R1 minus R5 +10 problems with an interval above 0; R1 minus
  R4 +4 with an interval that covers 0; R2 and R3 within 2 problems of R1; R6 within 3 problems below R4.
- Prediction, fresh2026: rule 77 [75, 79]; minus R5 +4 problems (+2.9 points), interval above 0; minus R4 +2 (+1.5 points),
  interval covers 0. So I predict H1 refuted on the plain-vote leg for lack of power, with a positive point estimate.
  The mechanism would be refuted (not only H1) if the rule is below R4 or equal to R5.

H2. Among late answers, those that switched script before token 16,384 are right less often than those that did not, on
the same problems. Test: problems with at least one late answer of each kind; per problem, share right among switched
minus share right among not switched; mean over problems, bootstrap over problems (5,000, seed 0); hard328, fresh2026 and
pooled. Control: flags permuted among the late answers of each problem (200 permutations) must give about 0. Refuted if the
pooled interval covers 0.
- Prediction: raw, switched right at most 10 %, not switched 25 to 35 % (hard328) and 15 to 25 % (fresh2026); within
  problem -15 points pooled, interval below 0. The drift study's one-sample value was 1 of 24 against 22 of 69, not
  matched within problem; its within-problem tests at earlier tokens were null, so a null here is plausible.

H3 (mechanism table, descriptive). Per set: precision of early finished answers and of late finished answers (posted:
88.1 % and 27 % on hard328, 81.3 % and 19 % on fresh2026). For each late finished answer with a ballot on a problem that
has an early ballot: does it agree with one? Counted: agrees (and right), disagrees with every early ballot (late right;
an early ballot right; none right).
- Prediction: about 25 % of such late answers agree with an early ballot and those are right 85 % of the time (redundant
  votes); of those that disagree fewer than 10 % are right, and an early ballot is right in 40 to 50 %. Refuting the
  mechanism: disagreeing late answers right as often as the early ballots they oppose.

Token accounting. Two sequential versions of R1, each over the 24 draw orders, tokens = every generated token:
- `seqfb_resume`: `frontier.RULES["seq4"]` on the 16,384 view (draw 2, then 1, then 1, stop when two agree; a sample stops
  at 16,384). If that ends with no ballot, the stopped samples are resumed in the same plan on the 32,768 view (a resumed
  sample costs `n_new` - 16,384 more) and the 32,768 ballots of the resumed samples vote.
- `seqfb_online` (no resuming): one sample at a time, at most 4. A sample that reaches 16,384 is stopped there if an early
  ballot already exists, else it runs on. Stop when two early ballots agree. Answer: vote of the early ballots, else of the
  late ones.
Compared with result-dd26fe's points on hard328: one 32,768 sample 232.8 at 11,650; `seq4` at 16,384 239.8 at 30,807;
`seq4` at 32,768 245.2 at 31,732. Prediction: `seqfb_resume` 247 [243, 251] at 33,000 to 35,000 tokens on hard328: a
few problems above `seq4` at 32,768 for a few thousand tokens more, not separated from it.

## Outputs

`results/fallback/{hard328,fresh2026}-01/`: `run.json`, `readout.json`, `table.md`, `rows.jsonl` (per sample: lengths,
early / late, switch token), `examples.json` (one problem the rule fixes and one it breaks against the plain vote, with the
four answers, lengths and flags); `hard328-01/chosen.json`. A `score:` line only for fresh2026 and only if H1 holds.

## Amendment 1 (after the hard328 development run, before fresh2026 is scored)

Development run `results/fallback/hard328-01/` (24-order means; stored order in brackets):

| rule | right | minus plain vote R4, points [95 %] | minus cut vote R5, points [95 %] |
|---|---|---|---|
| R1 fallback | 244.8 (243) | -0.5 problems, -0.1 [-2.3, +1.9] | +5.0, +1.5 [+0.5, +2.8] |
| R2 half weight | 249.8 (249) | +4.5, +1.4 [+0.4, +2.5] | +10.0, +3.0 [+1.1, +5.1] |
| R3 fallback + script | 245.2 (244) | 0.0, 0.0 [-2.1, +2.1] | +5.5, +1.7 [+0.5, +3.0] |
| R4 plain 32,768 vote | 245.2 (244) | | |
| R5 16,384-cut vote | 239.8 (238) | | |
| R6 flags permuted | 241.0 | -4.2, -1.3 [-2.3, -0.3] | |

- Chosen: R2 (half weight). It is the rule scored on fresh2026.
- My dev predictions were wrong for R1: predicted 248 and +4 over the plain vote; observed 244.8 and -0.5. The strict
  fallback throws away late answers that side with one of two disagreeing early answers or outvote one early wrong answer
  (stored order: it fixes 9 problems against the plain vote and breaks 10). R2 keeps those and fixes 6, breaks 1.
- Correction to the task's and result-dd26fe's wording: "99 right of 362" joins two counts. 99 is the right count of all
  368 late answers on hard328; of the 362 finished late answers 96 are right (832 + 96 = 928 of 1,306). fresh2026: 50 right
  of 259 finished and of 260 late. The checks assert both.
- Power on fresh2026 (2,000 draws of 136 problems from the 328, R2's per-problem differences): interval above 0 against
  the plain vote in 42.8 % of draws, against the cut vote in 54.6 %, both in 19.1 %. That is under 50 %: a null on
  fresh2026 will be uninformative, and H1 is expected to fail on power alone. The pooled hard328 + fresh2026 estimate will
  be reported as descriptive only.
- Prediction for the single fresh2026 score, R2, 24-order mean: 77.5 [75, 80] of 136; minus R4 +2 problems (+1.5 points),
  interval covers 0; minus R5 +4 problems (+3 points), lower bound within 1 point of 0. H1 refuted on at least one leg.
  The mechanism (not only H1) is refuted if R2 is below R4 or below R5 in the 24-order mean.
- Added for the token accounting because the chosen rule is not a fallback: `seq4_half`, R2 drawn in `seq4`'s plan (2, 1,
  1; every sample to the end; stop after a batch when a group weighs 2; else R2 over the drawn samples). hard328: 249.8 at
  36,659 tokens against `seq4` at 32,768 245.2 at 31,732 (+1.4 points [+0.4, +2.5] for 16 % more tokens); `seqfb_resume`
  244.8 at 33,118 and `seqfb_online` 244.8 at 34,863 are below `seq4` at 32,768 at more tokens (prediction 247: wrong).
  The first, uncommitted dev run had no `seq4_half`; it was deleted and rerun as `hard328-01` with identical other numbers.
- H2 and H3 on hard328 (dev): switched 20 of 119 right, not switched 79 of 249; within problem (60 problems) -12.2 points
  [-22.2, -3.1], permuted flags +0.6. Late finished ballots on problems with a 16,384 ballot: 87 of 192 agree with one (51
  right), 105 disagree (late right 13, a 16,384 ballot right 46, none right 46); on the 30 problems with no 16,384 ballot
  17 of 118 late ballots are right. Prediction "25 % agree, 85 % of those right" was wrong (45 %, 59 %).
