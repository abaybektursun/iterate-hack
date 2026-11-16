# Open forecasts, round-19 (engine 19)

Written 2026-11-16T01:38:21 UTC; board snapshot 2026-11-16T01:30:56 UTC. 4 targets from the open work items; 3 accounts, each against one covariate-only adversary (blind to the account, no RL sample or RL-derived edit as a predictor; a judge rejects a forecast that is the account's claim by construction), and the two no-theory readers. Gap = |account - adversary| / the wider 90 % interval. Deciding: the two 90 % intervals do not overlap; weak: they overlap. If a side is right, the measured value lies inside its own 90 % interval with chance 90 % by definition; "adv. right: in acc." is the chance it lies inside the account's interval if the adversary's forecast is right, "acc. right: in adv." the reverse (normal, sd = width / 3.29). The board item named decides the target.

| rank | target | deciding item | class | best pair | account | adversary | gap (widths) | reader-1 | reader-2 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | t01: How many of the 328 hard problems does the cued Olmo 3 base get right when the RL-Math 8-direction edit is restricted to | work-4bfe4e | deciding | account-1 | 198 [185, 210] | 160 [146, 175] | 1.31 | 191 [174, 206] | 188 [168, 205] |
| 2 | t02: How many of the 328 hard problems does the cued Olmo 3 base get right when the RL-Math 8-direction edit is restricted to | work-4bfe4e | weak | account-1 | 183 [166, 199] | 159 [143, 175] | 0.727 | 179 [160, 198] | 174 [153, 194] |
| 3 | t03: How many of the 328 hard problems does the untrained Olmo 3 base with the opening cue get right by plurality vote over 8 | work-e340a2 | weak | account-1 | 200 [191, 209] | 203 [195, 211] | 0.167 | 200 [192, 209] | 200 [192, 208] |
| 4 | t04: On the 328 hard problems, for the untrained Olmo 3 base with the opening cue, how many more problems does a plurality vo | work-e340a2 | weak | account-1 | 11.5 [5, 18] | 14 [5, 23] | 0.139 | 10 [3, 17] | 10 [4, 16] |

## t01 (work-4bfe4e): How many of the 328 hard problems does the cued Olmo 3 base get right when the RL-Math 8-direction edit is restricted to one shared 64-dimensional residual subspace per side (read and write), norm matched to the 1.5x edit?

Unit: right answers of 328. Cell: {"model": "Olmo-3-1025-7B base + the dial (RL-Math top-8 directions) restricted to one common residual subspace per side, m = 64, norm matched to the 1.5x edit (wsp_edit glob)", "prompt": "opening cue", "set": "hard328", "n": 328, "sampling": "not stated", "samples": "not stated", "grader": "not stated"}

| pair | account | adversary | gap (widths) | class | adv. right: in acc. | acc. right: in adv. |
|---|---|---|---|---|---|---|
| 1 | 198 [185, 210] | 160 [146, 175] | 1.31 | deciding | 0.002 | 0.001 |
| 2 | 198 [186, 208] | 162 [147, 177] | 1.2 | deciding | 0.004 | 0.001 |
| 3 | 197 [183, 210] | 162 [151, 174] | 1.296 | deciding | 0.001 | 0.003 |

- account-1: Account S1/S6 (an edit holding RL's own pairs at 1.25-1.5x lands near RL per sample): the m=64 restriction keeps 0.76/0.78 of the top-8 edit (result-ce52f8), so after norm matching it carries ~1.3x of the true pairs, which puts it between the 1x edit (192, result-284db5) and the 1.5x edit (203, result-306787), a little below RL's 206.
- account-2: Account S2-S3 (the effect is RL's paired top-8 directions, read from an input subspace shared across layers, and base + 1.5x those directions is RL) says keeping 76-78 % of the paired edit in one common 64-dim subspace per side (result-ce52f8) at the same norm should stay close to the full 1.5x dial at 203/328 (result-6f1bb7), just under it, as the k=64 cell at 200 and the explore ranks 2-8 1.5x cells (194-204 doubled) suggest.
- account-3: Account S6 (effect set by which true RL pairs the edit contains, not by its norm, peak near 1.5x): the m=64 shared subspace keeps 0.76-0.78 of the top-8 edit's squared norm with its pairing (result-ce52f8), so norm-matched it acts nearly like the 1.5x dial (203/328, result-6f1bb7) and well above the 1x dial (192) and random (159).
- adversary-1: A norm-matched 1.5x edit sits in the flat region of the random-edit curve, so it gets the random-edit mean of about 160, with single-sample spread.
- adversary-2: Norm-matched edit forecast at the random-edit/base level (mean of 159, 164, 159.5 and the 158-167 random band, about 162), interval = observed random/seed spread plus one-sample noise, widened for the concentrated 64-dim subspace.
- adversary-3: The norm-1.5x edit gets base 164 plus the random-edit norm slope (flat; random edits average 161.2), so about 162, with one-sample seed noise of about 4-5 problems setting the interval.
- reader-1: 191 [174, 206]: m=64 keeps ~77% of the top-8 edit's norm (result-ce52f8), so I expect most of the full edit's 203 to survive, well above base 164 / random 159.
- reader-2: 188 [168, 205]: Between random/base (~159-164) and the full 1.5x RL edit (203); a 64-dim shared subspace keeps ~77% of the edit's norm and its pairing, so most of the gain likely survives.


## t02 (work-4bfe4e): How many of the 328 hard problems does the cued Olmo 3 base get right when the RL-Math 8-direction edit is restricted to one shared 8-dimensional residual subspace per side (read and write), norm matched to the 1.5x edit?

Unit: right answers of 328. Cell: {"model": "Olmo-3-1025-7B base + the dial (RL-Math top-8 directions) restricted to one common residual subspace per side, m = 8, norm matched to the 1.5x edit (wsp_edit glob)", "prompt": "opening cue", "set": "hard328", "n": 328, "sampling": "not stated", "samples": "not stated", "grader": "not stated"}

| pair | account | adversary | gap (widths) | class | adv. right: in acc. | acc. right: in adv. |
|---|---|---|---|---|---|---|
| 1 | 183 [166, 199] | 159 [143, 175] | 0.727 | weak | 0.236 | 0.213 |
| 2 | 185 [167, 202] | 161 [145, 177] | 0.686 | weak | 0.269 | 0.226 |
| 3 | 180 [160, 198] | 160 [146, 174] | 0.526 | weak | 0.5 | 0.3 |

- account-1: Account S1 (only RL's exact pairs act; shifted or random pairs stay at the base, 158-163 in result-0d54f3): at m=8 only 0.40/0.42 of the edit survives (result-ce52f8), so norm matching gives ~0.95x of the true pairs plus a larger shared-subspace distortion, which should fall short of the 1x edit's 192 and the 1-direction edit's 181, while staying above the base's 164.
- account-2: Account S2-S3: the 8 common dimensions keep only ~40 % of the paired edit (result-ce52f8, against 7.5-14.5 % for random), and the norm matching inflates that part, so the cell should land between the rank-1 edit (181 at 1x in result-51a0e7; explore top1x1.5 cells 178-190 doubled) and the full dial's 203, well above the random/unpaired level of 158-164 (result-0d54f3).
- account-3: Account S2/S6 (direction 1 and the shared late component are a finish dial that cuts cap hits but adds little accuracy, and accuracy falls when it is pushed past 2x): m=8 keeps only 0.40/0.42 of the pairs (result-ce52f8), and norm matching scales that part up about 1.6x, so the cell should land near the direction-1 edits (k=1 181, result-51a0e7; stored top1x1.5 cells 190 and 178 of 328) and below the full dial (203).
- adversary-1: Same random-edit mean of about 160 at matched norm, with the low end a little wider because the same norm is packed into an 8-dimensional shared subspace.
- adversary-2: Same random-edit/base level as t01, nudged one problem lower and widened a little on the low side because the whole 1.5x norm sits in an 8-dim residual subspace shared by every layer.
- adversary-3: Same base-plus-flat-random-slope value as m = 64, moved down 2 and widened downward because the same norm is packed into 8 residual dimensions.
- reader-1: 179 [160, 198]: m=8 keeps ~40% of the norm, roughly direction 1's share, which alone gave 183; norm-matching over-amplifies that subspace, so I put it between random 159 and 203, near direction 1 alone.
- reader-2: 174 [153, 194]: 8 shared dims keep only ~40% of the edit and distort the pairs (mis-paired edits score like random 159), but low-rank finishing may survive, roughly like direction 1 alone (183) or less.


## t03 (work-e340a2): How many of the 328 hard problems does the untrained Olmo 3 base with the opening cue get right by plurality vote over 8 samples per problem?

Unit: right answers of 328. Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "opening cue", "set": "the 328 (hard328)", "n": 328, "sampling": "not stated (samples 6 and 7 at seed 3060000)", "samples": 8, "grader": "not stated"}

| pair | account | adversary | gap (widths) | class | adv. right: in acc. | acc. right: in adv. |
|---|---|---|---|---|---|---|
| 1 | 200 [191, 209] | 203 [195, 211] | 0.167 | weak | 0.885 | 0.797 |
| 2 | 201 [194, 208] | 202 [194, 210] | 0.062 | weak | 0.841 | 0.933 |
| 3 | 201 [193, 209] | 201 [192, 210] | 0.0 | weak | 0.856 | 0.936 |

- account-1: Account S5 (the vote gains on hard328 only through scattered wrong answers, and most misses have no right sample, so about 9 points stay out of inference reach): the stored curve 159.5/188.5/197 at k=1/4/6 (result-c065a6) extrapolates log-linearly to 202 at k=8, trimmed for saturation because 107 of 131 wrong problems have no right sample among 6.
- account-2: Account S5-S6 (votes help the base through scattered slips, but most of RL's vote wins on hard328 have no right base sample) means the cued-base vote curve keeps rising but flattens: 188.5 at 4 and 197 at 6 (result-c065a6), and a posterior-predictive simulation on the stored explore rows (day1_3/hard328_base_cue_s4r2) gives about +4 for 6 to 8, so about 201.
- account-3: Account S4-S5 (votes only help where the base already writes a right sample, and wrong answers scatter): the base-cue vote curve on the 328 is 159.5 at 1, 188.5 at 4 and 197 at 6 (result-c065a6), and 107 of the 131 misses have no right sample in 6, so samples 7-8 add about 2 problems each, giving about 201, still below RL's 224.
- adversary-1: vote(k)=159.5+20.9 ln k fits the 1, 4, 6 points exactly and gives 203 at k=8, which is 197 plus about 6 from the two extra samples; the interval comes from tie-breaking and per-sample noise.
- adversary-2: The slope is about 21 per unit ln k from k=1 to 6; flattened to about 17 that gives 17 x ln(8/6) = +5 over 197, so about 202, with plus or minus 8 for the two new samples and tie handling.
- adversary-3: 197 + 0.485 x (197 - 188.5) = 201, the 6->8 step scaled from the base's MATH-500 vote curve.
- reader-1: 200 [192, 209]: The base's vote curve on the 328 is 159.5/188.5/197 at k=1/4/6 (result-c065a6), still rising about 4 per sample, so k=8 should land a few problems above 197.
- reader-2: 200 [192, 208]: Vote over 6 gave 197 (188.5 at 4) and the curve flattens because most wrong problems have no right sample, so 8 samples adds about 3.


## t04 (work-e340a2): On the 328 hard problems, for the untrained Olmo 3 base with the opening cue, how many more problems does a plurality vote over 8 samples get right than a vote over 4 samples?

Unit: right answers of 328, vote over 8 minus vote over 4. Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "opening cue", "set": "the 328 (hard328)", "n": 328, "sampling": "not stated (samples 6 and 7 at seed 3060000)", "samples": "8 vs 4", "grader": "not stated"}

| pair | account | adversary | gap (widths) | class | adv. right: in acc. | acc. right: in adv. |
|---|---|---|---|---|---|---|
| 1 | 11.5 [5, 18] | 14 [5, 23] | 0.139 | weak | 0.718 | 0.948 |
| 2 | 12.5 [7, 18] | 12 [5, 19] | 0.036 | weak | 0.801 | 0.962 |
| 3 | 12 [5, 20] | 12 [6, 18] | 0.0 | weak | 0.958 | 0.812 |

- account-1: Account S5 saturation applied to result-c065a6: vote over 4 is 188.5 and the log-linear step of ~14 per doubling of k (29 over k=1 to 4, 8.5 over k=4 to 6) is shrunk by the base having no right sample on most missed problems (knowledge-b19faf: 7 % per-sample rate on 0-of-4 problems), giving about +11.5.
- account-2: Same account S5-S6 vote curve: the vote over 8 at about 201 minus the vote over 4 at 188.5 (result-c065a6), with the stored explore-row simulation giving roughly +12 from 4 to 8 samples.
- account-3: Account S4 (vote turns sometimes-right into right), with gains shrinking as the base's reach saturates (S5; knowledge-b19faf: 7% per-sample rate on 0-of-4 problems): about 201 for the vote over 8 minus 188.5 for the vote over 4 (result-c065a6) gives about +12.
- adversary-1: 203 from the log-k fit minus 188.5 for the vote over 4 gives about 14; the wide interval covers which 4-sample vote is used and the tie-breaking noise.
- adversary-2: Vote over 8 (about 202) minus a vote-over-4 point of about 190 (votek's 188.5, with room for the stored-order 192) gives about 12; the interval covers which k=4 tie rule is used and the noise from the new samples.
- adversary-3: 1.485 x 8.5 = 12.6 if the vote over 4 is averaged over subsets, 9 if it is samples 0-3 (192), so 12 with an interval covering both readings.
- reader-1: 10 [3, 17]: Vote over 8 (~200) minus vote over 4 (188.5 subset mean, or 192 in stored order) gives roughly 8-12.
- reader-2: 10 [4, 16]: Vote over 4 is 188.5-192 depending on which four, against about 200 at 8.


## Adversaries' rules

- adversary-1: Edited-model accuracy at a stated edit norm follows the base plus the flat random-edit curve: on hard328 with the cue (T 1.0, one sample, seed 3000000) the base scores 164 and random rank-8 edits at sizes -1 to 3 (incl. two draws at 1.5x) score 152-167, mean about 160 with sd about 4, so any norm-matched 1.5x edit whose content I may not use gets about 160 with an interval of single-sample noise plus allowance for subspace structure (m smaller = more concentrated edit = slightly wider low tail); vote-over-k accuracy of the untrained cued base follows a log-k curve fitted to its own board points on the 328 (159.5 at 1, 188.5 at 4, 197 at 6, which fit vote(k)=159.5+20.9 ln k exactly) and checked on the stored explore-half rows (vote over 4 of samples 0-3 = 94 of 164, x2 = 188), with interval width from tie-breaking noise measured on those rows (plus or minus 5 on the half) and per-sample noise.
- adversary-2: Accuracy of any edited base model comes from the untrained cued base's single-sample level on hard328 plus the spread of random weight edits at the stated norm (random rank-8 edits at sizes -1 to 3 score 158-167 of 328 with seed noise of about 5), so an edit whose content I may not use is forecast at the random-edit/base level with an interval covering that spread plus one-sample noise and some extra room for a norm concentrated in an m-dimensional subspace (m/d = 64/4096 or 8/4096); vote-over-k counts of the cued base come from its own vote curve on the 328 (159.5 at k=1, 188.5 at k=4, 197 at k=6, rising roughly linearly in ln k at about 21 problems per unit ln k, flattening the way MATH-500's curve did), extrapolated to k=8, and a vote-8 minus vote-4 gap is that extrapolation minus the k=4 point.
- adversary-3: Base-model vote targets follow the cued base's own vote-over-k curve on the 328 (vote over 4 = 188.5 and over 6 = 197, result-c065a6), extended to k = 8 with the shape of the cued base's vote curve on MATH-500 computed from the stored 12-sample rows (explore half, mean over random k-subsets: 446.9 at 4, 456.6 at 6, 461.3 at 8, so the 6->8 step is 0.485 of the 4->6 step and the 8-4 gap is 1.485 times it), with intervals set by seed noise (one-sample seeds differ by up to 9 problems). An edit's accuracy at a given edit norm follows the cued base's one-sample score plus the slope in edit norm fitted on the random rank-8 edits of the same norm family on hard328 (sizes -1 to 3: 159, 158, 159, 167, 163 against base 164, i.e. flat, slope about 0); the subspace dimension m (chance overlap m/4096) is used only to widen the interval downward for the smaller m, since a fixed norm packed into fewer residual dimensions can damage outputs; nothing about the RL change enters.

