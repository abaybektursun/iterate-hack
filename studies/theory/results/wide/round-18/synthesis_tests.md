# Synthesis tests, round-18 (version 17)

Run each test that is neither rejected nor dropped with one subagent: spec committed first, offline, on the TEST half only: load every cell with `rows.load(set, cell, "test")` and every weights table with `rows.weights(table, "test")` (`studies/theory/lib/rows.py`; never the explore half, never the raw files), script under `studies/theory/analysis/`, outputs under `studies/theory/results/direct/<name>-01/`. Compute the adversary's value FIRST, from the adversary's computation on the test half; then the statistic, its n and 90 % bootstrap interval (resampling problems; for kind weights, resampling test matrices); then one row per mechanism named here, with `interval`, `range`, `adversary` (the test-half value), `n` and `kind`, through `forecast.py add-rows`, which recomputes the verdict: holds only if the interval lies wholly inside the range, n >= 50 (kind weights: n >= 25 test matrices) and the interval excludes the adversary's value; inside the range but containing it: `not separated`; wholly outside: refuted; else undecided. Read no other test's output of this round.


## round-18/account-1/c1 (dropped on the explore half)

- Dropped: adversary's explore value 0.2127 lies inside the account's explore interval [0.21, 0.339]
- Why no fact covers it: result-ad95af reports only RL's gain over random (1.67x mean); no fact or result places RL's written directions on the scale from random to the base's own top-8 directions
- Claim: For each writer matrix (o, down), f = (rl.next - rand.next) / (basew.next - rand.next) places RL-Math 3.1's 8 written directions between random directions (0) and the base matrix's own top-8 directions (1), by how strongly the next layer's q, k, v, gate and up read them. Sentence 2 says RL amplifies a circuit the base already reads, but one far smaller than its dominant directions, so the median f is well above 0 and well below 1 (about a quarter of the way).
- Statistic: median over writer matrices of f = (rl.next - rand.next) / (basew.next - rand.next), unitless
- Kind: weights; tables: `xlisten` (test matrices: `rows.weights(table, "test")`)
- Matrices: all test-half rows of xlisten (o and down writers, layers 0-30) (n 28 test matrices)
- Computation: 1) For each xlisten row compute f = (rl.next - rand.next) / (basew.next - rand.next). 2) Statistic = median of f over the rows. 3) 90 % interval: 2000 bootstrap resamples of the rows (matrices) with replacement, the median of f in each, 5th and 95th percentiles.
- Null: random written directions of the same matrices give f = 0 by construction; the base-spectrum alternative (RL writes along the base matrix's own top directions) gives f = 1
- Explore half (the account's own measurement): 0.259 [0.21, 0.339], n 34
- Ranges fixed for the test half: account-1 [0.13, 0.45], null [-0.08, 0.08]
- Adversary (covariate): Writer module type alone sets f. Down writers come out near 0.34 and o writers near 0.21 on the explore matrices, whatever the RL delta holds. The median over a test half is then fixed by its mix of o and down rows. Next-layer readers amplify any structured direction of a writer partway between random and the base's own top-8, and how far depends on the writer type, not on what RL learned.
- Adversary's value on the explore half: 0.2127
- Adversary's value, computed first on the test half: 1) Over the explore rows of xlisten, compute f = (rl.next - rand.next) / (basew.next - rand.next) per row. Take its median within each writer type: o = 0.2127 (19 rows), down = 0.3388 (15 rows). These are fixed constants. 2) For each test row of xlisten, give the predicted value 0.2127 if writer == 'o' and 0.3388 if writer == 'down'. Use no other field of the row. 3) The alternative's value is the median of these predicted values over the test rows: 0.2127 if o rows are the majority, 0.3388 if down rows are, and 0.2758 if the counts are equal. (tables: `xlisten`)


## round-18/account-1/c2 (dropped on the explore half)

- Dropped: adversary's explore value 3.014 lies inside the account's explore interval [2.37, 3.19]
- Why no fact covers it: F51 and F32 use the final Math 3.1 subspace and Think-SFT; no fact or result uses the step-100 subspaces, or compares a Math checkpoint with a General checkpoint
- Claim: Code-RL 3.1's final change lies in RL-Math 3.1's step-100 top-8 input subspace far more than in General-RL 3.0's step-100 top-8 input subspace. Sentences 2-3 say the input side of RL's pairs is the base's deliberation-text subspace, already found in the first 100 steps of a reasoning reward. General's step-100 change is a larger share of its final change (0.35 vs 0.12 of the final norm), so size alone would favor General.
- Statistic: median over matrices of cap_right(code31>math31_s100) / cap_right(code31>general30_s100), unitless
- Kind: weights; tables: `cap` (test matrices: `rows.weights(table, "test")`)
- Matrices: all test-half rows of cap (q, k, v, o, gate, up, down of all layers) (n 112 test matrices)
- Computation: 1) For each cap row, r = cap['code31>math31_s100']['cap_right'] / cap['code31>general30_s100']['cap_right']. 2) Statistic = median of r over rows. 3) 90 % interval: 2000 bootstrap resamples of matrices with replacement, the median in each, 5th and 95th percentiles.
- Null: any early RL subspace of rank 8 captures Code's change equally (ratio 1); size alone (General's step-100 change is 3x further along) predicts at most 1; base spectrum predicts about 1
- Explore half (the account's own measurement): 2.76 [2.37, 3.19], n 112
- Ranges fixed for the test half: account-1 [1.9, 3.8], null [0.6, 1.4]
- Adversary (other): Host receptivity, not anything about Code 3.1: the math31_s100 delta's top-8 right subspace just catches more of any model's change than the general30_s100 subspace does. So the ratio is set by the two hosts, whatever the source. Measure it with the two other sources in the cap table (math30 and think_sft) and Code 3.1 is not needed. Per matrix, the geometric mean of their ratios gives a median of 3.01 on the explore matrices; the statistic itself is 2.76, and both fall inside [1.9, 3.8].
- Adversary's value on the explore half: 3.014
- Adversary's value, computed first on the test half: 1) For each cap row, rm = cap['math30>math31_s100']['cap_right'] / cap['math30>general30_s100']['cap_right'] and rt = cap['think_sft>math31_s100']['cap_right'] / cap['think_sft>general30_s100']['cap_right']. 2) g = sqrt(rm * rt) per row. 3) Prediction = median of g over all rows (q, k, v, o, gate, up, down of all layers). Explore: 3.014. (tables: `cap`)


## round-18/account-1/c3 (dropped on the explore half)

- Dropped: adversary's explore value 0.1762 lies inside the account's explore interval [0.089, 0.307]
- Why no fact covers it: F24 and F62 correlate only final models with IF and Think-SFT; no fact or result compares the step-100 and final similarity of the concentration pattern
- Claim: The per-matrix pattern of top-8 share (each module's median removed) is more alike across the reasoning-reward runs (Math 3.0, Math 3.1, Code 3.1) at step 100 than in the final models. Sentences 3-4 say the first 100 steps write one shared opening switch whatever the reasoning reward, while later steps write a graded part per run and domain. Smaller step-100 changes are noisier, so size alone predicts lower similarity at step 100, not higher.
- Statistic: mean over the 3 pairs (math30,math31), (math31,code31), (math30,code31) of [Spearman rho of the step-100 residual top-8 shares - Spearman rho of the final residual top-8 shares], unitless
- Kind: weights; tables: `top8_share` (test matrices: `rows.weights(table, "test")`)
- Matrices: all test-half rows of top8_share (n 112 test matrices)
- Computation: 1) For each key k in math30, math31, code31, math30_s100, math31_s100, code31_s100: residual = top8_share[k] minus the median of top8_share[k] over the rows of the same module (q,k,v,o,gate,up,down) in the matrix set used. 2) For each pair (a,b): d = Spearman(resid[a_s100], resid[b_s100]) - Spearman(resid[a], resid[b]). 3) Statistic = mean of the 3 d. 4) 90 % interval: 2000 bootstrap resamples of matrices with replacement, recomputing the module medians and the Spearman rhos in each, 5th and 95th percentiles.
- Null: step-100 and final patterns are equally alike (0); same difference for non-reasoning pairs (Math 3.1 with General 3.0: -0.06; with IF 3.0: -0.21); size/noise predicts below 0
- Explore half (the account's own measurement): 0.193 [0.089, 0.307], n 112
- Ranges fixed for the test half: account-1 [0.06, 0.45], null [-0.3, 0.03]
- Adversary (covariate): At step 100 the deltas are tiny (norms ~0.01-0.05, 5-8x below final) and a matrix's top-8 share is set mostly by the size of its change: on the explore matrices the module-median-removed top-8 share at step 100 has Spearman 0.76-0.83 with the matrix's own module-median-removed log delta norm (versus 0.08-0.54 for the final models). So the step-100 cross-model share correlation is just the cross-model correlation of step-100 change sizes (which matrices move most in the first 100 steps), not any shared concentration mechanism. Replacing the step-100 shares by the step-100 log norms in the statistic predicts its value: 0.176 vs the actual 0.192 on explore.
- Adversary's value on the explore half: 0.1762
- Adversary's value, computed first on the test half: 1) Over the rows of top8_share in the matrix set, for each key k in math30, math31, code31: resid_share[k] = top8_share[k] minus the median of top8_share[k] over rows of the same module (q,k,v,o,gate,up,down). 2) For each key k_s100 in math30_s100, math31_s100, code31_s100: resid_norm[k_s100] = log(norm[k_s100]) minus the median of log(norm[k_s100]) over rows of the same module (norm is the 'norm' field of the same top8_share row). 3) For each pair (a,b) in (math30,math31), (math31,code31), (math30,code31): d_alt = Spearman(resid_norm[a_s100], resid_norm[b_s100]) - Spearman(resid_share[a], resid_share[b]) (ranks with average ties). 4) Alternative value = mean of the 3 d_alt. (tables: `top8_share`)


## round-18/account-2/c1 (dropped on the explore half)

- Dropped: adversary's explore value 4.178 lies inside the account's explore interval [3.66, 4.94]
- Why no fact covers it: F51 and result-105d5c compare Code with Think-SFT inside Math 3.1's subspace. No fact or result compares the capture of one change by two different RL runs' subspaces (Math 3.1 vs General 3.0).
- Claim: How much more of Code-RL 3.1's change falls in Math-RL 3.1's top-8 input subspace than in General-RL 3.0's. S1 says the input sides are shared by RL on graded reasoning text (math, code) and not by LM-judge chat RL, so the ratio is far above 1 and far above what any reasoning-text change (Think-SFT) shows.
- Statistic: median over matrices of cap_right(code31>math31) / cap_right(code31>general30), a ratio
- Kind: weights; tables: `cap` (test matrices: `rows.weights(table, "test")`)
- Matrices: all test matrices of the cap table (q, k, v, o, gate, up, down) (n 112 test matrices)
- Computation: For each test matrix compute r = cap['code31>math31']['cap_right'] / cap['code31>general30']['cap_right']. Statistic = median of r. 90 % interval: 2000 bootstrap resamples of matrices (with replacement), median each, 5th and 95th percentiles.
- Null: The same ratio for Think-SFT's change, cap_right(think_sft>math31)/cap_right(think_sft>general30) = 2.04 [1.92, 2.15] on explore, i.e. Math 3.1's input subspace takes any reasoning-text change ~2x better; chance subspaces give 1. Alternatives checked on explore: base-spectrum level cap_right(code31>general30)/cap_right(code31>base_w) = 1.08; Think-SFT math31/base_w ~1.5.
- Explore half (the account's own measurement): 4.25 [3.66, 4.94], n 112
- Ranges fixed for the test half: account-2 [3.0, 6.0], null [1.0, 2.6]
- Adversary (other): Generic host effect, not a code31-math31 link: general30's top-8 input subspace sits off-axis from the changes made by any verifiable-reward RL run, while those runs' own top-8 subspaces catch about 4x more of each other's changes whichever pair is used. Swap the pair for one that leaves out both code31's change and math31's subspace: Math 3.0's change, captured by Code 3.1's top-8 input subspace and by General's. That ratio comes out at about the same value (4.18 on explore, against 4.25). Code31's change in math30 or mix30 gives 4.51 and 4.37 too, so the value is set by the general30 denominator and the reasoning-RL host family, not by anything specific to math31 and code31.
- Adversary's value on the explore half: 4.178
- Adversary's value, computed first on the test half: 1) Use the rows of table cap (the test matrices). 2) For each matrix compute r_alt = cap['math30>code31']['cap_right'] / cap['math30>general30']['cap_right']. 3) Take the median of r_alt over the matrices. That median is the predicted value of the median of cap_right(code31>math31) / cap_right(code31>general30). (tables: `cap`)


## round-18/account-2/c2 (dropped on the explore half)

- Dropped: adversary's explore value 0.4923 lies inside the account's explore interval [0.35, 0.626]
- Why no fact covers it: F24 compares Math 3.1 with IF and Think-SFT, and F62 compares Code with Think-SFT and IF. The Math 3.1-Code 3.1 vs Math 3.1-General 3.0 contrast is in no fact or result.
- Claim: Which matrices concentrate their change: the family-median-removed per-matrix top-8 share pattern of Math-RL 3.1 tracks Code-RL 3.1 much more than General-RL 3.0. S1/S5 say concentration in general comes from on-policy RL, but where it sits follows the shared reasoning pairs, which Code shares and the LM-judge run does not.
- Statistic: D = Spearman rho(Math31, Code31) - Spearman rho(Math31, General30) of family-median-removed top-8 shares, unitless
- Kind: weights; tables: `top8_share` (test matrices: `rows.weights(table, "test")`)
- Matrices: all test matrices of the top8_share table (n 112 test matrices)
- Computation: On the test matrices, for each key k in {math31, code31, general30} take top8_share[k] minus the median of top8_share[k] over the test matrices of the same module. Compute Spearman rho between the math31 and code31 residuals and between the math31 and general30 residuals; D = difference. 90 % interval: 2000 bootstrap resamples of matrices (medians recomputed within each resample), 5th/95th percentiles.
- Null: D = 0 (General-RL concentrates in the same matrices as Code, as its equal overall top-8 share in F03 might suggest). Alternatives computed on explore: layer depth alone (product of each pattern's rho with layer) 0.057; base spectrum alone (via rho with base_w) -0.054; a common reasoning-text pattern routed through Think-SFT 0.24.
- Explore half (the account's own measurement): 0.467 [0.35, 0.626], n 112
- Ranges fixed for the test half: account-2 [0.3, 0.9], null [-0.15, 0.15]
- Adversary (covariate): Depth profile plus change size: Math 3.1 and Code 3.1 come from the same 3.1 pipeline and change by similar amounts, so their top-8 shares have the same smooth curve over depth. General 3.0's curve over depth is different. Inside each module family, a model that knows only module, a quadratic in layer and log norm_delta already gives rho(math31,code31) of about 0.89 against rho(math31,general30) of about 0.40. That puts D near 0.49 with no reference to the account's mechanism.
- Adversary's value on the explore half: 0.4923
- Adversary's value, computed first on the test half: 1) For each key k in {math31, code31, general30}, fit by OLS over the 112 explore rows of top8_share: top8_share[k] ~ module dummies (q,k,v,o,gate,up,down, no intercept) + (layer/31) + (layer/31)^2 + ln(norm[k]). 2) Apply these coefficients to each test row of top8_share (its module, its layer, its norm[k]) to get the fitted share fit_k. 3) For each k, subtract from fit_k its median over the test matrices of the same module. 4) D_alt = Spearman(math31 residual, code31 residual) - Spearman(math31 residual, general30 residual). One number. On explore, where the fit is in-sample, D_alt = 0.492. Layer quadratic alone gives 0.519. (tables: `top8_share`)


## round-18/account-2/c3 (dropped on the explore half)

- Dropped: adversary's explore value 0.5224 lies inside the account's explore interval [0.479, 0.587]
- Why no fact covers it: result-ad95af reports the mean gain over random (1.67x). No fact states the per-writer ratio to the base's own top-8 directions, and no consequence has tested it.
- Claim: How strongly the next layer of the base reads RL-Math's 8 written directions, relative to the base matrix's own top-8 directions. S1 says RL writes new pairs, not the base's dominant directions, which the base reads above random but at about half the gain of its own top directions.
- Statistic: median over writer matrices of rl.next / basew.next, a ratio
- Kind: weights; tables: `xlisten` (test matrices: `rows.weights(table, "test")`)
- Matrices: all test writer matrices (o and down) of the xlisten table (n 28 test matrices)
- Computation: For each test writer row compute r = rl['next'] / basew['next']. Statistic = median of r. 90 % interval: 2000 bootstrap resamples of writer matrices, median each, 5th/95th percentiles.
- Null: RL amplifies the base's own dominant directions (as a dial on the base spectrum would), so the ratio is ~1. Alternative checked on explore: random directions give rand.next/basew.next = 0.35.
- Explore half (the account's own measurement): 0.503 [0.479, 0.587], n 34
- Ranges fixed for the test half: account-2 [0.4, 0.68], null [0.9, 1.1]
- Adversary (covariate): The base matrix's own anisotropy sets the ratio: any 8 written directions that are not the base's top-8 get a gain of roughly 1 + alpha*(basew.next - 1), where alpha is one fixed shrinkage constant (0.2656, fit once on the explore writers). The ratio rl/basew then is (1 + alpha*(basew-1))/basew, a value fixed by how strongly the next-layer readers favor the base's own top directions, i.e. by basew.next alone. Writers with large basew.next get small ratios and writers with basew near 1 get ratios near 1, without any claim about what RL writes. This gives 0.522 on explore, against the statistic's 0.503.
- Adversary's value on the explore half: 0.5224096810487324
- Adversary's value, computed first on the test half: 1) Fix alpha = 0.26556886780040767, the median over the 34 explore writer rows of xlisten of (rl.next - 1)/(basew.next - 1). 2) For each test writer row (o and down) of xlisten, compute r_hat = (1 + alpha*(basew['next'] - 1)) / basew['next'], using basew.next only. 3) The prediction is the median of r_hat over the test writer rows (n 28). Explore: the same median over the 34 explore rows = 0.5224. (tables: `xlisten`)


## round-18/account-3/c1 (dropped on the explore half)

- Dropped: adversary's explore value 8.203 lies inside the account's range [6.5, 14.5]
- Why no fact covers it: F51 and result-105d5c use cap_right with Code over Think-SFT, and result-9d979a uses subspace overlaps; no fact or result uses the joint (cap_both) capture of one RL change in another reward's pairs, or Math pairs against General pairs.
- Claim: Code-RL 3.1's change falls into RL-Math 3.1's top-8 singular pairs (left and right together) about 11x more than into RL-Zero-General's pairs, because Math and Code RL strengthen the same step-by-step deliberation mode and an LM-judge chat reward does not use it (S2, S6). An RL run that merely starts from the same base would give a ratio near 1.
- Statistic: median over matrices of cap_both(code31>math31) / cap_both(code31>general30), a dimensionless ratio
- Kind: weights; tables: `cap` (test matrices: `rows.weights(table, "test")`)
- Matrices: all test matrices (q, k, v, o, gate, up, down, every layer) in cap.jsonl (n 112 test matrices)
- Computation: 1) For each test matrix, read cap['code31>math31']['cap_both'] and cap['code31>general30']['cap_both']. 2) Take their ratio per matrix. 3) Statistic = median of the ratios over matrices. 4) 90 % interval: 2000 bootstrap resamples of matrices with replacement, median each time, 5th and 95th percentiles.
- Null: Any RL run's top-8 pairs from the same base capture Code-RL's change equally (shared optimizer and base structure), so the ratio is about 1. Explore checks: Think-SFT's change in the same two pair sets gives 2.57; Code in IF/General gives 0.36; norm ratio Math/General 2.07; top-8 share ratio 0.99.
- Explore half (the account's own measurement): 10.79 [8.99, 12.27], n 112
- Ranges fixed for the test half: account-3 [6.5, 14.5], null [0.5, 3.5]
- Adversary (construction artifact): cap_both is built from the same left and right top-8 subspaces as cap_left and cap_right; if the change's input and output sides are captured independently, cap_both ~ cap_left * cap_right, so the ratio of two-sided captures is just the product of the one-sided capture ratios (left ~2x, right ~4x for Math 3.1 vs General 3.0 targets). Multiplying two modest one-sided excesses gives a ~8-11x two-sided ratio by construction, without any claim about paired input-output directions.
- Adversary's value on the explore half: 8.203
- Adversary's value, computed first on the test half: 1) For each matrix of table cap, read cap['code31>math31'] and cap['code31>general30'] cap_left and cap_right. 2) Per matrix compute (cap_left(code31>math31) * cap_right(code31>math31)) / (cap_left(code31>general30) * cap_right(code31>general30)). 3) Take the median over the matrices. That median is the predicted value of the statistic. (tables: `cap`)


## round-18/account-3/c2 (dropped on the explore half)

- Dropped: adversary's explore value 1.223 lies inside the account's explore interval [1.155, 1.269]
- Why no fact covers it: No fact or result relates the full-delta cosine (anatomy pair cos) to the top-8 block capture; the board shows overlaps and cap ratios only separately.
- Claim: What RL-Math and Code-RL changes have in common sits in Math's top-8 singular block: the full-matrix cosine of the two changes is about as large as the top-8 block alone can carry, R = cos / sqrt(cap_both(code31>math31) x top8_share(math31)) near 1.2, because the shared deliberation mode is carried by the few strengthened directions (S1, S2). A shared component spread across directions would need R near 26.
- Statistic: median over matrices of R = cos(rl_math, rl_code) / sqrt(cap_both(code31>math31) * top8_share(rl_math)), dimensionless
- Kind: weights; tables: `anatomy`, `cap` (test matrices: `rows.weights(table, "test")`)
- Matrices: all test matrices present in both anatomy.jsonl and cap.jsonl (all 112) (n 112 test matrices)
- Computation: 1) For each test matrix, take c = anatomy pair['rl_math-rl_code']['cos'], s = anatomy delta['rl_math']['top8_share'], b = cap['code31>math31']['cap_both']. 2) R = c / sqrt(b * s). 3) Statistic = median of R over matrices. 4) 90 % interval: 2000 bootstrap resamples of matrices, median each time, 5th and 95th percentiles.
- Null: The shared component is diffuse, i.e. it falls into Math's top-8 block only at chance (64/(d_out*d_in)): R_null = c / sqrt(64/(d_out*d_in) * s), median 25.98 [23.30, 28.07] on explore; using the base matrix's own top-8 block instead of Math's gives 7.34 [6.33, 8.30]; Think-SFT's version of R gives 0.09.
- Explore half (the account's own measurement): 1.221 [1.155, 1.269], n 112
- Ranges fixed for the test half: account-3 [1.08, 1.36], null [5.0, 60.0]
- Adversary (covariate): Module type alone sets R. Per-matrix R depends strongly on module (explore medians: q 0.479, k 0.733, v 1.202, o 1.223, down 1.289, up 1.617, gate 1.677), and the median over a set of matrices is just the module value at the middle of the module mix. In both halves, q+k+v together make up just under half the matrices (explore 47, test 49 of 112), so the median falls on the o/v/down plateau near 1.22 whatever the account says about how rl_math and rl_code share directions.
- Adversary's value on the explore half: 1.2228
- Adversary's value, computed first on the test half: 1) Fixed module constants, fitted on the explore matrices as the median of cos(rl_math-rl_code)/sqrt(cap_both(code31>math31)*top8_share(rl_math)) per module: q 0.479, k 0.733, v 1.202, o 1.223, down 1.289, up 1.617, gate 1.677. 2) For each test matrix in both anatomy and cap (all 112), read only its `module` field and give it its module's constant. Do not use cos, cap or top8_share of the test matrices. 3) Take the median of these 112 assigned values. Test module counts are q 17, k 16, v 16, o 13, up 15, down 17, gate 18. In sorted order q+k+v fill ranks 1-49 and o fills ranks 50-62, so ranks 56 and 57 are both o, giving 1.223. (tables: `anatomy`, `cap`)


## round-18/account-3/c3 (dropped on the explore half)

- Dropped: adversary's explore value 0.583 lies inside the account's explore interval [0.35, 0.626]
- Why no fact covers it: F24 compares Math with IF and Think-SFT, F62 compares Code with Think-SFT and IF; no fact or result compares Math with Code against General.
- Claim: Across matrices, the pattern of where RL-Math 3.1 concentrates its change (top-8 share, each module family's median removed) follows Code-RL 3.1's pattern much more than RL-Zero-General's: D = rho(Math31, Code31) - rho(Math31, General30) about 0.47, because Math and Code strengthen the same deliberation mode in the same matrices (S2).
- Statistic: Spearman rho(Math31, Code31) minus Spearman rho(Math31, General30) of family-median-removed per-matrix top-8 shares, a difference of correlations
- Kind: weights; tables: `top8_share` (test matrices: `rows.weights(table, "test")`)
- Matrices: all test matrices in top8_share.jsonl (112) (n 112 test matrices)
- Computation: 1) For each key in (math31, code31, general30): per module family (q,k,v,o,gate,up,down), subtract the family median of top8_share[key] over the matrices in the sample. 2) Spearman rank correlation of residuals Math31 vs Code31, and Math31 vs General30, over matrices. 3) D = difference. 4) 90 % interval: 2000 bootstrap resamples of matrices, recompute medians and correlations each time, 5th and 95th percentiles.
- Null: Every RL run concentrates in the same matrices through shared base structure and module, so D is 0. The size-only alternative (the same D on per-matrix relative norm, norm/base norm) gives 0.066 [-0.049, 0.155] on explore.
- Explore half (the account's own measurement): 0.467 [0.35, 0.626], n 112
- Ranges fixed for the test half: account-3 [0.15, 0.82], null [-0.12, 0.12]
- Adversary (covariate): Training length / shared pipeline: the 3.1 Math and Code runs share a recipe and start, so their family-median-removed top-8 share patterns already line up after only 100 RL steps (the _s100 checkpoints), before any long task-specific training. General 3.0 comes from a different release. The difference D is therefore set by which pipeline and early steps the models share, not by what the full runs learn. The same statistic computed on the step-100 checkpoints (math31_s100, code31_s100, general30_s100) gives 0.58 on the explore matrices, inside [0.15, 0.82].
- Adversary's value on the explore half: 0.583
- Adversary's value, computed first on the test half: 1) From table top8_share, over the test matrices, take top8_share.math31_s100, top8_share.code31_s100 and top8_share.general30_s100. 2) For each of these keys, subtract from each matrix's value the median of that key over the matrices of the same module family (q,k,v,o,gate,up,down). 3) Spearman rho(math31_s100 residuals, code31_s100 residuals) minus Spearman rho(math31_s100 residuals, general30_s100 residuals), using average ranks for ties. 4) This difference is the predicted D for the full-length models (one number on the statistic's scale). (tables: `top8_share`)

