# Synthesis tests, round-15

Disagreements between the accounts first (the judge's), then each account's three new consequences. Run each with one subagent: spec committed first, offline on stored rows only, script under `studies/theory/analysis/`, outputs under `studies/theory/results/direct/<name>-01/`, n and the 90 % bootstrap interval, then one row per mechanism named here through `forecast.py add-rows`. Verdict rule (version 14): a mechanism holds only if the statistic's 90 % interval lies wholly inside its range (for a carried plan: wholly on the holding side of the threshold) and the statistic rests on at least 50 rows; otherwise the row is `undecided`, with the n that would decide it. For a rival pair's shared test, a value in neither rival's range refutes both; write one row per rival. A value in no account's range refutes every account the test names.


## round-15/d1 (disagreement)

- About: Whether the 1.5x top-8 RL-Math edit, a weight change that matches RL's total on hard328, also wins the problems the cued base cannot solve in 4 samples (where RL's extra wins sit), or only re-weights the base toward problems it already reaches.
- account-1: S2/S6 (and its c3): the pairs carry one shared graded shift that makes the base's scattered slips rarer on problems it can already solve, not RL's problem-specific solves. So on problems outside the base's 4-sample reach the edit lifts the base only a little and captures a minority of RL's advantage there.
- account-2: S2/S5 (and its c3): the edit is a weight change that lowers the per-step slip rate the way RL does. Because that lower rate compounds over long chains, it wins the base-0-of-4 hard328 problems about as often as RL plain does (edit minus RL in [-0.08, 0.08]), so it captures most or all of RL's advantage there.
- Claim: On hard328 problems where the cued base has 0 right among its 4 attempt-0 samples, the 1.5x top-8 edit's per-sample lift over a fresh cued-base sample, as a fraction of RL plain's lift over the same fresh base sample, is 0.6 or more if account-2 holds and 0.10-0.45 if account-1 holds.
- Statistic: S = (E - B) / (R - B), the share of RL plain's per-sample advantage over a fresh cued-base sample that the edit captures on base-0-of-4 problems (unitless ratio of mean per-sample right rates)
- Files: `studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01`, `studies/rlneurons/results/day1_3/hard328_top8x1.5_cue_s4-01`, `studies/rlneurons/results/day1_3/hard328_rl_plain_s4r2-01`, `studies/rlneurons/results/cap32/base_cue-01`
- Rows: hard328 problems with 0 of 4 right (grader v3) among the cued base's attempt-0 samples 0-3 in hard328_base_cue_s4r2-01 (restarts excluded). On these: the edit's 4 samples, RL plain's 4 attempt-0 samples, and the independent cued-base sample in cap32/base_cue-01 scored at a 16,384-token cut (a sample capped at 16,384 counts as not right). Drop a problem if any of the 9 rows is missing, or if its cap32 text sha256 equals one of its s4r2 samples 0-3 (the sample would not be fresh). (n 108)
- Computation: 1) Select the problems with 0 right among the cued base's attempt-0 samples 0-3 (about 108 of 328, since 220 are solved at least once). 2) Per problem: e = right edit samples / 4, r = right RL samples / 4, b = 1 if the fresh cap32 base sample, cut at 16,384, is right. 3) E, R and B are the means of e, r and b over the selected problems. The fresh B removes the selection bias of picking problems on the base's own 0-of-4. 4) S = (E - B) / (R - B). 5) 90 % interval: resample the selected problems with replacement 10,000 times, recompute S each time (the same draw for E, R and B), and take the 5th and 95th percentiles. Report R - B with its own interval. If that interval includes 0 the test is void, not decided.
- Null: The edit as a base resample: on these problems the edit's rate equals a fresh cued-base sample's (E = B, as a random rank-8 1.5x edit does), so S is about 0.
- Ranges fixed in advance: account-1 [0.1, 0.45], account-2 [0.6, 1.4], null [-0.15, 0.08]
- Mechanism round-15/account-1/d1: not run yet
- Mechanism round-15/account-2/d1: not run yet


## round-15/account-1/c1 (consequence)

- Why no fact covers it: F24 gives only Think-SFT's capture (4.80x chance) and says the >=2x property is 'shared' with Code 3.1; no fact or result gives Code 3.1's capture relative to Think-SFT's in the same subspace.
- Claim: If on-policy RL under any reward concentrates in the inputs the base's own text drives (S1), Code-RL 3.1's change must sit in RL-Math 3.1's top-8 input subspace far more than off-policy Think-SFT's diffuse change does. If each reward wrote its own subspace, Code's capture would be no higher than Think-SFT's.
- Statistic: median over matrices of cap_right(Code 3.1 change, Math 3.1 top-8 input subspace) / cap_right(Think-SFT change, same subspace), a ratio (unitless)
- Files: `studies/theory/data/direct_host/cap_v1.json`
- Rows: all 224 layer matrices (32 layers x q,k,v,o,gate,up,down), entries cap_right of Code 3.1 and of Think-SFT against the RL-Math 3.1 top-8 right (input) subspace (n 224)
- Computation: 1) For each matrix read cap_right for Code 3.1 and for Think-SFT against the Math 3.1 top-8 input subspace. 2) Per matrix ratio r = Code / Think-SFT. 3) Statistic = median of r over the 224 matrices. 4) 90 % interval: resample the 224 matrices with replacement 10,000 times, take the median each time, report the 5th and 95th percentiles.
- Null: Another model's change in the same subspace: Think-SFT's own capture, so ratio about 1 if concentration is reward-specific and Code's change is as unrelated to Math's inputs as a diffuse fine-tune
- Ranges fixed in advance: account-1 [2.0, 60.0], null [0.5, 1.5]
- Mechanism round-15/account-1/c1: not run yet


## round-15/account-1/c2 (consequence)

- Why no fact covers it: F03 and result-82eb02 compare mean top-8 shares across models only. No fact or result relates the per-matrix concentration pattern of one reward to another's.
- Claim: If concentration is set by which base inputs the model's own samples drive (S1), the matrices where Math-RL concentrates most should also be the ones where an unrelated on-policy reward (IF) concentrates most, beyond what they share with off-policy Think-SFT.
- Statistic: Spearman rho(Math 3.1, IF) minus Spearman rho(Math 3.1, Think-SFT) of per-matrix top-8 share after each module family's median is subtracted (difference of correlations, unitless)
- Files: `studies/theory/data/direct_reward/top8_share_v1.json`
- Rows: all 224 matrices; keys RL-Zero-Math 3.1, RL-Zero-IF and Think-SFT (n 224)
- Computation: 1) For each key, subtract from each matrix's top-8 share the median share of its module family (q,k,v,o,gate,up,down) over 32 layers, which removes shape effects. 2) Spearman rho over the 224 matrices of Math 3.1 vs IF residuals, and of Math 3.1 vs Think-SFT residuals. 3) Statistic = difference. 4) 90 % interval: resample matrices with replacement 10,000 times (the same draw for both rhos), recompute the difference, take the 5th and 95th percentiles.
- Null: Another model's directions: Think-SFT's per-matrix pattern shares as much with Math-RL as IF-RL does, so the difference is about 0 (concentration pattern reward- or training-agnostic)
- Ranges fixed in advance: account-1 [0.15, 1.0], null [-0.1, 0.1]
- Mechanism round-15/account-1/c2: not run yet


## round-15/account-1/c3 (consequence)

- Why no fact covers it: F19/F20 test this only on code. No fact or listed result splits the hard328 edit rows by RL's per-problem outcome.
- Claim: If the 1.5x top-8 edit carries RL's shared shift but not its problem-specific choices (S6), then on hard328 problems where RL solves none of 4 samples the edit keeps at least most of the base's right answers, as F20 found on code. If the edit copied RL's outcomes, it would lose them.
- Statistic: edit right samples / base right samples on hard328 problems with RL 0 of 4 right (ratio, unitless)
- Files: `studies/rlneurons/results/day1_3/hard328_top8x1.5_cue_s4-01`, `studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01`, `studies/rlneurons/results/day1_3/hard328_rl_plain_s4r2-01`
- Rows: problems whose RL plain attempt-0 samples 0-3 are all wrong (grader v3); on them the 4 edit samples and the base's attempt-0 samples 0-3 (restarts excluded); problems missing any of the 12 rows dropped (n 280)
- Computation: 1) From RL rows pick problems with 0 of 4 right (attempt 0). 2) On those, E = right edit samples and B = right base samples (attempt 0, samples 0-3), both grader v3. 3) Statistic = E / B. 4) 90 % interval: resample the selected problems with replacement 10,000 times, recompute E/B, take the 5th and 95th percentiles. n = 4 x number of selected problems (edit rows).
- Null: The edit copies RL's outcomes per problem (fully or for two thirds of samples), so edit right samples on RL-0/4 problems fall to at most half the base's
- Ranges fixed in advance: account-1 [0.75, 4.0], null [0.0, 0.5]
- Mechanism round-15/account-1/c3: not run yet


## round-15/account-2/c1 (consequence)

- Why no fact covers it: F37 measured this on MATH-500 with 12 samples; F23/F42 measured MATH-500 agreement only. No fact or result gives the merged-wrong vote contrast on hard328, where wrong answers could plausibly concentrate on shared traps.
- Claim: On hard328 the cued base's finished wrong answers also scatter, so the vote over its 4 samples with the real wrong answers is right clearly more often than the same vote with every finished wrong answer of a problem merged into one value. S4 says vote gains come from independent one-off slips, so D lies in [0.06, 0.40]; if hard-problem wrongs shared one attractor, D would be about 0.
- Statistic: D = mean over problems of P(vote of 4 right | real answers) - P(vote of 4 right | finished wrong answers merged), in probability units
- Files: `studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01`
- Rows: hard328 problems whose 4 attempt-0 samples (samples 0-3, no restarts) hold at least 1 right and at least 1 finished wrong answer under grader v3; cap-hit samples abstain (n 110)
- Computation: 1) Read attempt 0 of samples 0-3 per problem; label right, finished wrong (with its extracted answer) or cap hit. 2) Keep problems with >=1 right and >=1 finished wrong. 3) Real vote: plurality over finished answers, ties broken evenly (expected value of a random tie break). 4) Merged vote: replace every finished wrong value of the problem by one token, vote again the same way. 5) D = mean(real - merged). 6) 90 % interval: 10,000 bootstrap resamples of problems, 5th and 95th percentiles.
- Null: Merged-wrong vote (the base's wrong answers on a problem share one attractor value), where D = 0 exactly; the strongest null for this statistic.
- Ranges fixed in advance: account-2 [0.06, 0.4], null [-0.03, 0.03]
- Mechanism round-15/account-2/c1: not run yet


## round-15/account-2/c2 (consequence)

- Why no fact covers it: F07/F38 and result-6832a8 give step 100's single-sample score and cap hits only; no fact or result computes a vote over step-100 samples.
- Claim: RL step 100 has learned only the opening (S2), not the lower slip rate, so its wrong answers scatter like the cued base's and a vote over its 4 samples gains as much over one sample as the cued base's vote does (+7.1 points), not as little as final RL's (+2.8).
- Statistic: Vote-over-4 right minus mean single-sample right for RL step 100 plain, in points of 500 (percentage points)
- Files: `studies/rlneurons/results/ckptcue/s0100_plain-01`, `studies/rlneurons/results/ckptcue/s0100_plain_s123-01`
- Rows: all 500 MATH-500 problems, the 4 step-100 plain samples (sample 0 from s0100_plain-01, samples 1-3 from s0100_plain_s123-01), T 1.0, grader v3 (n 500)
- Computation: 1) Per problem, the 4 samples' extracted answers and v3 grades. 2) Vote: plurality over finished answers, ties broken evenly (expected value). 3) Single: mean right of the 4 samples. 4) G = 100 * mean over problems (vote right - single right). 5) 90 % interval: 10,000 bootstrap resamples of problems.
- Null: Final RL's own vote gain (results/day1_3/math500_rl-01: vote 474 vs mean single 460, +2.8 points), i.e. step 100 already carrying RL's lowered slip rate.
- Ranges fixed in advance: account-2 [5.0, 10.0], null [1.0, 4.5]
- Mechanism round-15/account-2/c2: not run yet


## round-15/account-2/c3 (consequence)

- Why no fact covers it: result-95a4dc matches edit and RL on totals; F04/F26 split by one base sample's outcome. No fact or result compares edit and RL on the problems outside the base's 4-sample reach.
- Claim: The 1.5x top-8 edit is a weight change that lowers the slip rate the way RL does (S1, S2, S5), so on hard328 problems where the cued base has no right answer in 4 samples it is right per sample as often as RL plain: the edit-minus-RL rate lies in [-0.08, 0.08]. If the edit were only a resample of the base, it would sit near the base's own rate there and about 0.2 below RL.
- Statistic: Edit per-sample right rate minus RL plain per-sample right rate on base-0-of-4 hard328 problems, in probability units
- Files: `studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01`, `studies/rlneurons/results/day1_3/hard328_top8x1.5_cue_s4-01`, `studies/rlneurons/results/day1_3/hard328_rl_plain_s4r2-01`
- Rows: hard328 problems with 0 right among the cued base's attempt-0 samples 0-3; for each, the edit's 4 samples and RL plain's 4 attempt-0 samples (n 110)
- Computation: 1) Select problems with 0 of 4 right for the cued base (attempt 0). 2) Per problem, edit rate = right of the edit's 4 samples / 4; RL rate = right of RL's 4 attempt-0 samples / 4. 3) D = mean over problems (edit - RL). 4) 90 % interval: 10,000 bootstrap resamples of problems. 5) Null value on the same rows: base cue rate from the base's restart attempts and the independent 32k-cap base cue run scored at 16,384 (results/cap32/base_cue-01) minus the RL rate.
- Null: The edit as a base resample: its rate on these problems equals the cued base's own fresh-sample rate (near 0.05), giving D about -0.2.
- Ranges fixed in advance: account-2 [-0.08, 0.08], null [-0.35, -0.12]
- Mechanism round-15/account-2/c3: not run yet


## round-15/account-3/c1 (consequence)

- Why no fact covers it: The self-opened draw (result-3a3af3) selects openings by resampling 32 draws; no fact or result compares the base's natural, unselected deliberative plain openings with the cued answer on the same problems.
- Claim: The plain-prompt base answers that happen to open deliberatively ('Okay', 'Alright', 'Hmm', 'Let me', 'Let's', 'I need to' within the first 240 characters) are already in the cue's mode. On the same problems they should be right about as often as the cued base's answer (S2, S4: a prompt only selects a mode the weights hold). If the cue added something beyond choosing the mode, those answers would sit near the plain rate instead.
- Statistic: mean over problems of (T3 plain right - T1 cued right) on problems whose T3 answer opens deliberatively, in fraction of problems
- Files: `studies/rlneurons/results/rln4/t1_t3_items-01`
- Rows: per_problem.json rows (500 MATH-500 problems) whose T3 first 240 characters contain one of the deliberative openers listed in the claim (case-sensitive, matched before any equation) (n 120)
- Computation: 1) Load per_problem.json and flag deliberative T3 openings by the fixed word list. 2) For flagged problems, d_i = T3_right_i - T1_right_i under grader v3. 3) The statistic is the mean of d_i. 4) Bootstrap: resample flagged problems 10,000 times; the 90 % interval runs from the 5th to the 95th percentile. 5) Compute the same mean on the unflagged problems as the null. The test fails if fewer than 50 problems are flagged.
- Null: Opening irrelevant (the cue adds more than mode selection): flagged answers do as well as plain answers do elsewhere, i.e. the same T3-T1 difference computed on the unflagged problems (the overall T3-T1 is -0.37).
- Ranges fixed in advance: account-3 [-0.15, 0.1], null [-0.65, -0.22]
- Mechanism round-15/account-3/c1: not run yet


## round-15/account-3/c2 (consequence)

- Why no fact covers it: result-95a4dc and data.md report only the edit's single samples (207, 198, 199, 197) and its mean; no listed result or fact gives the edit's vote over 4 on hard328.
- Claim: The 1.5x top-8 edit is RL's re-weighting of the base distribution (S3, S4), so its wrong answers are split like RL's, and its vote over 4 should match RL's vote over 4 on hard328, not stay at the base's vote. If the edit only added finishing, its votes would gain like a base resample's and fall about 9 points short of RL's.
- Statistic: vote-over-4 right of 328 for base + 1.5x top-8 RL-Math directions minus RL plain's vote over 4, in points (percent of 328)
- Files: `studies/rlneurons/results/day1_3/hard328_top8x1.5_cue_s4-01`, `studies/rlneurons/results/day1_3/hard328_rl_plain_s4r2-01`, `studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01`
- Rows: all 328 problems; attempt 0 of samples 0-3 in each run (no restarts); cap hits abstain (n 328)
- Computation: 1) Per problem and arm, take the plurality of extracted finished answers over samples 0-3, with ties broken at random and averaged over 200 tie draws (as in result-f941b8); grade with v3. 2) Statistic = 100 * (edit votes right - RL votes right) / 328. 3) Paired bootstrap over problems, 10,000 resamples; the 90 % interval is the 5th to 95th percentile. 4) Null: the same quantity with the cued base's 4 attempt-0 samples in place of the edit (192 - 221 = -8.8 points).
- Null: The base's own resample: a vote over 4 cued-base samples (equivalently, a base-like random rank-8 edit at 1.5x, which result-39497c shows does nothing) against RL's vote, about -8.8 points.
- Ranges fixed in advance: account-3 [-5.0, 5.0], null [-14.0, -6.0]
- Mechanism round-15/account-3/c2: not run yet


## round-15/account-3/c3 (consequence)

- Why no fact covers it: Facts F07 and F38 and results fad48d and 6832a8 compare step 100 with the cue on score and cap hits only; no fact or result compares the lengths of right answers.
- Claim: RL step 100 is only the mode selection the cue makes, with the same cap-hit rate and none of the later finishing or lengthening (S4). So on problems both arms solve, step 100's right answers should be as long as the cued base's right answers, while final RL, which carries the finishing and lengthening, should not be.
- Statistic: geometric mean over problems of (median generated tokens of step-100 plain right samples / median generated tokens of cued-base right samples), as a ratio
- Files: `studies/rlneurons/results/ckptcue/s0100_plain-01`, `studies/rlneurons/results/ckptcue/s0100_plain_s123-01`, `studies/rlneurons/results/day1_3/math500_base_cue-01`, `studies/rlneurons/results/day1_3/math500_rl-01`
- Rows: MATH-500 problems with at least 1 right (v3) sample among the 4 step-100 plain samples and at least 1 among the 4 cued-base attempt-0 samples (n 430)
- Computation: 1) Per problem and arm, take the median generated tokens of the right samples. 2) r_i = ln(step100_median / base_median). 3) Statistic = exp(mean r_i). 4) Bootstrap over problems, 10,000 resamples; the 90 % interval is the 5th to 95th percentile of exp(mean r). 5) Null: the same ratio with final RL's 4 attempt-0 samples (math500_rl-01) in place of step 100.
- Null: Another model: final RL-Zero-Math against the cued base on the same problems, which carries the lengthening of short answers (result-1b6bf2) that step 100 should lack.
- Ranges fixed in advance: account-3 [0.88, 1.1], null [1.15, 1.6]
- Mechanism round-15/account-3/c3: not run yet

