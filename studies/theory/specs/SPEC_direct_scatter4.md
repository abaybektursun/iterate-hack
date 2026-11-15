# Direct test scatter4-01: run-08/f2-m05 (theory round 14, carried plan)

Plan: `studies/theory/results/wide/round-14/jobs/plan-run-08-f2-m05.json`. Board work item: work-bc42f2.

## Claim

On MATH-500 problems where the cued base gets 2 to 10 of its 12 stored samples right, the vote over 4 is right more
often because the finished wrong answers scatter across different strings. With abstentions held fixed, the exact
vote-over-4 accuracy with the real wrong answers beats the same vote with every finished wrong answer merged into one
answer by at least 0.05 per problem.

## Does an earlier result decide it?

No. votesplit-01 (result-4c9189) used the same rows and a merged-wrong null, but its statistic is different: the
share of the 21 problems that the vote over 12 gains over the vote over samples 0-3 which have the right answer in
under half the samples (0.667), and the merged null kept 8 of 21 gains. That counts problems, for one fixed subset,
over k = 12. This plan asks for the mean per-problem gap over all 495 four-sample subsets on the 2-10 band. votesplit-01
points the same way (13 of 21 gains need wrong answers to split) but does not give D.

## Files and rows

- `studies/rlneurons/results/votek/math500_base_cue-01/rows.jsonl`: 6,000 rows, 500 problems x 12 samples (sample
  0-11), cued base, T 1.0 / top-p 1.0, cap 16,384, grader v3 (`score_v3`), the rows of result-1c9e40.
- Vote code: `studies/rlneurons/analysis/votek.py` (`agree_table`, `vote`), the team's vote, as reused by
  `studies/theory/analysis/direct_vote13.py`.

## Changes from the plan (written before computing)

1. One file instead of three. The plan lists votek-01, votek-02 and day1_3/math500_base_cue-01. votek-01's rows.jsonl
   already holds all 12 samples per problem (its first 4 samples are the day1_3 job abaybektursun-1114-153825-208b);
   votek-02 has no rows file. Sample order is the stored `sample` 0-11, so day1_3 samples come first, as the plan says.
2. Answer key. The plan's string normaliser (strip whitespace, `\boxed{}`, `\left/\right`, `\!`, trailing period) is
   replaced by the team's answer equality: `rln4_lib.agree` on `norm_v3`, grouped as in `votek.vote` (a sample joins
   the first group whose first member agrees with it). Groups are formed once over the 12 samples in sample order, and
   each sample's key is its group. Every right sample (`score_v3 == 1`) gets the key RIGHT, as in the plan. Reason: the
   caller asked to reuse the team's vote code path; it reproduces the posted 466.
3. Instrument check: the team's `votek.vote` over all 12 samples must give exactly 466 (and samples 0-3 give 446), as
   asserted in direct_vote13.py. Also reported: the plan-rule scatter arm over all 12 samples (cap hits abstain, keys as
   above); the plan allows a difference of at most 2 from 466. If it differs by more than 2, the plan-rule abstention
   is reported but the team rule (only missing answers abstain) becomes the primary arm. Planted failure: the S arm
   with each wrong sample given its own distinct key must give D >= the real D, and the M arm with the S tie rule
   must equal the S arm on problems with at most one finished wrong sample (checked per problem).
4. Abstention. Primary: the plan's rule, a sample abstains if `cap_hit` is true or `extracted_v3` is None (58 cap hits
   carry an extracted answer). Secondary: the team's rule, only `extracted_v3 is None` abstains.
5. hard328: `studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01` stores 4 to 12 rows per problem (191 of 328
   have 4); 12 samples per problem are not stored, so the hard328 D is not computed.

## Computation

1. Keys as above. Band: r = number of right samples in 2..10 of 12. n = number of band problems (must be >= 50).
2. For each band problem, all C(12,4) = 495 four-sample subsets (sample order kept). Vote S: plurality among the
   non-abstaining keys; ties go to the tied key whose earliest sample in the subset has the lowest order; all four
   abstain gives wrong. Score 1 if the winner is RIGHT. Vote M: the same with every finished wrong key replaced by
   one key WRONG. V4_S, V4_M = mean over 495 subsets.
3. d = V4_S - V4_M per problem; D = mean of d over band problems.
4. 90 % interval: percentile bootstrap over band problems, 10,000 resamples, numpy default_rng(0).
5. Descriptive: share of finished wrong samples whose key appears at least twice among the problem's 12 samples (the
   mechanism says about 0.25); D for r in 2..4 and 5..10; D for r in {1, 11}; D with the tie rule using a random
   sample order (one fixed permutation per problem, default_rng(1)); D under the team abstention rule.

## Null

The merged-wrong vote M on the same problems, samples, abstentions and tie rule. Abstention, cap, length and
difficulty mechanisms predict D = 0.

## Threshold (copied from the plan) and verdict rule

Threshold: D = 0.05 (mean per-problem gain in vote-over-4 accuracy, scatter arm minus merged-wrong arm, on problems
with 2-10 of 12 right; n >= 50 problems).

- Holds: n >= 50 and the lower end of the 90 % interval of D is at least 0.05.
- Refuted: the upper end of the 90 % interval is below 0.05.
- Otherwise undecided, with the n that would decide it.
