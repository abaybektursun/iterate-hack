# SPEC: direct test of run-08/f2-m06, "a cap hit casts no vote"

Board work-37a3db. Theory round 13 (`studies/theory/results/wide/round-13/direct_tests.json`, entry run-08/f2-m06).
Written before any vote below was computed. Stored rows only: no GPU job, no forward pass, no tokenizer.

## The claim

Mechanism run-08/f2-m06: a row that hits the token cap casts no vote, so it abstains instead of adding a wrong
answer. Turning cap hits into finished answers (a larger cap) raises the single-sample count more than the vote
count, because most converted rows are wrong and vote against a right minority.

Tested consequence: on hard328, take a 4-sample Think-SFT + cue vote in which the 4th vote is Think-SFT's cap-32,768
row. Scored at 16,384 (set A) a row longer than 16,384 tokens abstains; scored at 32,768 (set B) it votes its answer.
The mechanism predicts that set B loses at least 2 problems that set A had right (D >= 2), that the vote gain
VB - VA is less than half of the single-row gain G1 (about 23), and that B scores below the abstention null A'.

## Why only this mechanism

From the plan: round-09/grader-m06 and run-08/f2-m02 are about how many cap hits turn right when the cap is raised and
how a rescored count differs from a native one; as accounts of votes they reduce to yield only, which is null A'
(converted wrong rows add nothing and take nothing). The other carried mechanisms (seed scatter, template, edit
directions, problem strata) say nothing about a finished wrong answer taking a right vote away.

Plan check, written here before computing: the ceiling account also predicts a small vote gain (the 16,384 vote is
241 of 328 against pass@4 244), so the ratio test alone does not separate the two; the parts that separate them are
D >= 2 and VB < VA'. Those are close to arithmetic once a converted wrong answer agrees with another wrong answer in
samples 1-3; with ties broken toward the shortest finished sample a converted row (always > 16,384 tokens) never
wins a tie against a native row, so a flip needs such an agreement. Step 7 measures how often that agreement happens
against a second-sample base rate.

## Files

- 4th vote, Think-SFT: `studies/rlneurons/results/cap32/rows-01/sft_cue.jsonl` (328 rows, job
  abaybektursun-1115-005756-309b; checked before writing: 230 right at 32,768, 207 when rows over 16,384 count as
  cap hits, 93 rows over 16,384, 2 cap hits at 32,768, 2 rows with no extracted answer).
- Samples 1-3, Think-SFT: `studies/rlneurons/results/thinkvote/hard328_sft1_cue_s4-01/rows.jsonl` (cap 16,384,
  attempt 0 only exists; sample 0 dropped, it is seed 3000000 like the cap32 row).
- RL contrast: `studies/rlneurons/results/cap32/rows-01/rl_plain.jsonl` (195 at 32,768, 193 at 16,384) and samples
  1-3, attempt 0, of `studies/rlneurons/results/day1_3/hard328_rl_plain_s4r2-01/rows.jsonl`.
- Secondary, not deciding: the 4-sample cap-32,768 run of work-dc9359, branch `cap32vote` commit b0ca348,
  `studies/rlneurons/results/cap32vote/hard328_sft1_cue_s4-01/rows.jsonl` (each row with its 32,768 fields and its
  16,384 view in the `*_16` fields, cut and regraded by `analysis/cap32vote.py`). All 4 votes convert there.

## Computation

1. Load the rows; assert 230 / 207 for the Think-SFT cap32 row set, 195 / 193 for RL; the thinkvote single counts
   212, 212, 211, 201.
2. Per problem, votes: samples 1-3 (their stored `extracted_v3`, `score_v3`; a row with no extracted answer
   abstains) plus the 4th vote. Set A: the cap32 row abstains if n_new > 16,384 or it has no answer. Set B: it
   abstains only if it hit the cap at 32,768 or has no answer. Null A': as B, but a converted row (n_new > 16,384,
   finished, with an answer) that v3 grades wrong abstains.
3. Vote rule: answers grouped as in `studies/rlneurons/analysis/day1_vote.py` (a row joins the first group whose first
   member agrees under `rln4_lib.agree`, the grader's math-verify 0.9.0 equivalence; else it starts a group). The
   largest group wins. Ties go to the group whose shortest member is shortest (fewest n_new). The vote is right if
   the winning group's first member has score_v3 1. All abstain: wrong. (Plan change: the plan said "exact
   normalized string" as the fallback; agree() already covers it, as in the team's posted votes.)
4. G1 = right(4th row at 32k) - right(4th row at 16k). VA, VB, VA'. U = wrong in A, right in B. D = right in A,
   wrong in B. For every D problem: the converted answer, samples 1-3 answers, plurality or tie-break.
5. Bootstrap over the 328 problems, 10,000 resamples, numpy default_rng(0): VB - VA, (VB - VA)/G1 (G1 recomputed on
   the same resample), VA' - VB. 95 % percentile intervals (the plan's level) and 90 %.
6. Scatter base rate (step 7 of the plan): among converted rows graded wrong, the share whose answer agrees with
   any of samples 1-3; against: among sample-1 rows that finished (no cap hit) wrong, the share whose answer agrees
   with sample 2 or 3. Wilson 95 % intervals.
7. Steps 1-5 for RL plain, as contrast.
8. Secondary: the 4-sample run, vote over the 4 rows' `*_16` fields (A4) against their 32,768 fields (B4), and A4'
   (B4 with every converted wrong row abstaining); D4, U4, single gain = mean over the 4 samples. Same vote rule.

## Refuting observation and frozen threshold (from the plan, unchanged)

Holds only if, for Think-SFT: D >= 2, the upper end of the 95 % interval of (VB - VA)/G1 is < 0.5, and VB < VA'.
Otherwise refuted (D <= 1, or the ratio's upper end >= 0.5, or VB >= VA').

The plan also names "the 95 % lower bound of the ratio >= 0.5" as a refuting case; the holding rule above is
stricter (upper end < 0.5), and an upper end >= 0.5 with a lower end < 0.5 is counted as not holding.

## Null

A' (the same samples with each wrong converted row abstaining): the yield/ceiling account, D = 0 by construction,
gain VA' - VA. Stronger than random: same rows, same problems, only the vote of the wrong converted rows changes.
Scatter control: a second Think-SFT sample (sample 1 against samples 2-3) for how often a wrong answer agrees with
another wrong answer. Cross-model: RL plain with its 20 converted rows.

## Seen before writing

The row counts in Files; the thinkvote readout (vote 241, pass@4 244, singles 212/212/211/201); work-dc9359's comment
that the 4-sample vote at 32,768 is 244 against 238 in its 16,384 view (+1.8 points [-0.9, 4.9]), with no flip count
and no abstention null. No vote of the sets A, B, A' was computed.
