# Direct test m2abstain-01: run-02/f2-m04 (theory round 14, carried plan)

Written before computing. Plan: `studies/theory/results/wide/round-14/jobs/plan-run-02-f2-m04.json` (read from the
iterate-hack-theory checkout; not yet on origin/theory). Board work item: work-08da7a.

## Claim

Adding the RL difference to Think-SFT (M(2) = Think-SFT + 2 x (RL-Math - base)) turns the cap-hit companions of a lone
right sample into finished wrong answers, so on problems with exactly one right sample out of three, the M(2) vote is
right at least 0.15 less often than Think-SFT's vote, whose companions abstain.

## Earlier results checked

- abstain-01 (run-08/f2-m06, result-3605ba) tests whether letting Think-SFT's own cap hits finish inside a 4-sample vote
  flips right votes. It holds only Think-SFT rows and never conditions on lone-right problems or compares M(2), so it
  does not decide this claim.
- result-c5dafe and result-42cc6c post M(2) single and vote counts (hard328 vote over 3: 246/328), not the lone-right
  vote rate. Nothing on the board decides D.

## Files and rows (all committed, studies/rlneurons/results/)

| Arm | Folder | Rows kept |
| --- | --- | --- |
| Think-SFT + cue, cap 16,384, hard328 | `thinkvote/hard328_sft1_cue_s4-01` | samples 0, 1, 2 (null: 1, 2, 3) |
| Think-SFT + cue, cap 16,384, fresh2026 | `fresh/sft1_cue_s4-01` | samples 0, 1, 2 (null: 1, 2, 3) |
| M(2), cue, cap 16,384, hard328 | `transplant/hard328-02` (arm `sft1_rl20`) | seeds 3,000,000 / 3,100,000 / 3,200,000 + index |
| M(2), cue, cap 16,384, fresh2026 | `transplant/fresh2026-02` (arm `sft1_rl20`) | seeds 7,000,000 / 7,010,000 / 7,020,000 + index |
| Think-SFT + cue, cap 32,768 (budget route, reported only) | `cap32vote/hard328_sft1_cue_s4-01`, `cap32vote/fresh2026_sft1_cue_s4-01` | samples 0, 1, 2 |

n before the lone-right filter: 328 + 136 = 464 problems per arm.

## Computation (plan steps 1-9)

1. Vote per problem and arm over 3 samples. A sample with no extracted answer casts no vote. The other samples are
   grouped; the top group wins; with m tied top groups the vote scores 1/m if the right group is among them, else 0.
   All abstain: 0.
2. L_arm = problems (hard328 + fresh2026 pooled) with exactly 1 of the arm's 3 samples right (score_v3 = 1).
3. VR_arm = mean vote score over L_arm. D = VR_ThinkSFT(0,1,2) - VR_M2.
4. 90 % interval: 10,000 bootstrap resamples, numpy default_rng(0), each arm's L resampled independently (unit:
   problem), 5th and 95th percentiles.
5. Null: D_null = VR_ThinkSFT(0,1,2) - VR_ThinkSFT(1,2,3), same bootstrap (the resample of L_ThinkSFT(0,1,2) is shared,
   so D - D_null = VR_ThinkSFT(1,2,3) - VR_M2 per resample).
6. Mediation (reported): over the two non-right samples of each lone-right problem, share with no answer, share with the
   stored cap_hit flag, share finished wrong, share of problems whose two companions give the same wrong answer.
7. Budget route (reported): D_32k = VR_ThinkSFT_cap32(0,1,2) - VR_M2.

## Threshold and verdict (frozen, copied from the plan)

Threshold D = 0.15. Holds if min(n_ThinkSFT, n_M2) >= 50, the 90 % interval of D lies wholly above 0.15, and the 90 %
interval of D - D_null lies wholly above 0. Refuted if the 90 % interval of D lies wholly below 0.15. Undecided
otherwise, or if either n < 50 (then report the n that would decide it).

## Changes from the plan, fixed before computing

1. Transplant rows all carry `sample = 0`; the sample is told apart by the seed (seed - problem_index). hard328-02 already
   holds all three hard328 M(2) samples (seeds 3.0M, 3.1M, 3.2M); hard328-01's two are the same rows (asserted equal).
   fresh2026-02 holds four fresh2026 M(2) seeds (7.00M, 7.01M, 7.02M, 7.03M); the first three are used, and
   fresh2026-01's rows for 7.00M and 7.02M are asserted equal to fresh2026-02's.
2. "Cap hit" in the plan is "16,384 tokens reached with no boxed answer". The abstention test is therefore
   `extracted_v3 is None`, the same rule as the team's posted vote (`studies/rlneurons/analysis/day1_vote.py`). Rows with
   the stored `cap_hit` flag that wrote an answer before the cut vote (55 Think-SFT hard328 rows over 4 samples, 39 M(2)
   hard328 rows).
3. Grouping uses the grader's equivalence on norm_v3 (`rln4_lib.agree`, as in day1_vote.vote) in place of plain string
   equality after norm_v3, so the vote with day1_vote's first-member tie rule must reproduce the posted M(2) hard328 vote
   over 3, 246/328. That reproduction is the instrument check.

## Instrument checks (run before the readout; the script stops if one fails)

- Per-sample right counts reproduce the posted numbers: M(2) hard328 234, 229, 237; M(2) fresh2026 69, 75, 70;
  Think-SFT hard328 212, 212, 211, 201; Think-SFT fresh2026 65, 59, 56, 60.
- M(2) hard328 vote over 3 with day1_vote.vote = 246 (result-c5dafe).
- A synthetic lone-right problem whose two companions agree on one wrong answer scores 0; one whose companions abstain
  scores 1; one with three different finished answers scores 1/3.
- D computed with Think-SFT(0,1,2) in place of M(2) is exactly 0.

## Outputs

`studies/theory/analysis/direct_m2abstain.py` writes `studies/theory/results/direct/m2abstain-01/` metrics.json,
examples.json, rows.json.
