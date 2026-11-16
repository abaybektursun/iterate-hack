# Forecasts, round-19

Board snapshot 2026-11-16T01:30:56 UTC, written 2026-11-16T01:38:21 UTC. 4 targets; forecasters reader-1, reader-2, round-19/account-1, round-19/adversary-1, round-19/account-2, round-19/adversary-2, round-19/account-3, round-19/adversary-3.


Engine 19 open forecasts: each account-k forecasts as its account; adversary-k is a covariate-only forecaster blind to the account. Adversary forecasts a judge found to be the account's claim by construction are left out: none.


## t01 (work-4bfe4e): How many of the 328 hard problems does the cued Olmo 3 base get right when the RL-Math 8-direction edit is restricted to one shared 64-dimensional residual subspace per side (read and write), norm matched to the 1.5x edit?

Unit: right answers of 328. Cell: {"model": "Olmo-3-1025-7B base + the dial (RL-Math top-8 directions) restricted to one common residual subspace per side, m = 64, norm matched to the 1.5x edit (wsp_edit glob)", "prompt": "opening cue", "set": "hard328", "n": 328, "sampling": "not stated", "samples": "not stated", "grader": "not stated"}

> The dial restricted to one common residual subspace per side (wsp_edit glob, m = 64 and m = 8, norm matched to the 1.5x edit), hard328 cue, 2 cells

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 191 | [174, 206] | m=64 keeps ~77% of the top-8 edit's norm (result-ce52f8), so I expect most of the full edit's 203 to survive, well above base 164 / random 159. |
| reader-2 | 188 | [168, 205] | Between random/base (~159-164) and the full 1.5x RL edit (203); a 64-dim shared subspace keeps ~77% of the edit's norm and its pairing, so most of the gain likely survives. |
| round-19/account-1 | 198 | [185, 210] | Account S1/S6 (an edit holding RL's own pairs at 1.25-1.5x lands near RL per sample): the m=64 restriction keeps 0.76/0.78 of the top-8 edit (result-ce52f8), so after norm matching it carries ~1.3x of the true pairs, which puts it between the 1x edit (192, result-284db5) and the 1.5x edit (203, result-306787), a little below RL's 206. |
| round-19/adversary-1 | 160 | [146, 175] | A norm-matched 1.5x edit sits in the flat region of the random-edit curve, so it gets the random-edit mean of about 160, with single-sample spread. |
| round-19/account-2 | 198 | [186, 208] | Account S2-S3 (the effect is RL's paired top-8 directions, read from an input subspace shared across layers, and base + 1.5x those directions is RL) says keeping 76-78 % of the paired edit in one common 64-dim subspace per side (result-ce52f8) at the same norm should stay close to the full 1.5x dial at 203/328 (result-6f1bb7), just under it, as the k=64 cell at 200 and the explore ranks 2-8 1.5x cells (194-204 doubled) suggest. |
| round-19/adversary-2 | 162 | [147, 177] | Norm-matched edit forecast at the random-edit/base level (mean of 159, 164, 159.5 and the 158-167 random band, about 162), interval = observed random/seed spread plus one-sample noise, widened for the concentrated 64-dim subspace. |
| round-19/account-3 | 197 | [183, 210] | Account S6 (effect set by which true RL pairs the edit contains, not by its norm, peak near 1.5x): the m=64 shared subspace keeps 0.76-0.78 of the top-8 edit's squared norm with its pairing (result-ce52f8), so norm-matched it acts nearly like the 1.5x dial (203/328, result-6f1bb7) and well above the 1x dial (192) and random (159). |
| round-19/adversary-3 | 162 | [151, 174] | The norm-1.5x edit gets base 164 plus the random-edit norm slope (flat; random edits average 161.2), so about 162, with one-sample seed noise of about 4-5 problems setting the interval. |

## t02 (work-4bfe4e): How many of the 328 hard problems does the cued Olmo 3 base get right when the RL-Math 8-direction edit is restricted to one shared 8-dimensional residual subspace per side (read and write), norm matched to the 1.5x edit?

Unit: right answers of 328. Cell: {"model": "Olmo-3-1025-7B base + the dial (RL-Math top-8 directions) restricted to one common residual subspace per side, m = 8, norm matched to the 1.5x edit (wsp_edit glob)", "prompt": "opening cue", "set": "hard328", "n": 328, "sampling": "not stated", "samples": "not stated", "grader": "not stated"}

> The dial restricted to one common residual subspace per side (wsp_edit glob, m = 64 and m = 8, norm matched to the 1.5x edit), hard328 cue, 2 cells

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 179 | [160, 198] | m=8 keeps ~40% of the norm, roughly direction 1's share, which alone gave 183; norm-matching over-amplifies that subspace, so I put it between random 159 and 203, near direction 1 alone. |
| reader-2 | 174 | [153, 194] | 8 shared dims keep only ~40% of the edit and distort the pairs (mis-paired edits score like random 159), but low-rank finishing may survive, roughly like direction 1 alone (183) or less. |
| round-19/account-1 | 183 | [166, 199] | Account S1 (only RL's exact pairs act; shifted or random pairs stay at the base, 158-163 in result-0d54f3): at m=8 only 0.40/0.42 of the edit survives (result-ce52f8), so norm matching gives ~0.95x of the true pairs plus a larger shared-subspace distortion, which should fall short of the 1x edit's 192 and the 1-direction edit's 181, while staying above the base's 164. |
| round-19/adversary-1 | 159 | [143, 175] | Same random-edit mean of about 160 at matched norm, with the low end a little wider because the same norm is packed into an 8-dimensional shared subspace. |
| round-19/account-2 | 185 | [167, 202] | Account S2-S3: the 8 common dimensions keep only ~40 % of the paired edit (result-ce52f8, against 7.5-14.5 % for random), and the norm matching inflates that part, so the cell should land between the rank-1 edit (181 at 1x in result-51a0e7; explore top1x1.5 cells 178-190 doubled) and the full dial's 203, well above the random/unpaired level of 158-164 (result-0d54f3). |
| round-19/adversary-2 | 161 | [145, 177] | Same random-edit/base level as t01, nudged one problem lower and widened a little on the low side because the whole 1.5x norm sits in an 8-dim residual subspace shared by every layer. |
| round-19/account-3 | 180 | [160, 198] | Account S2/S6 (direction 1 and the shared late component are a finish dial that cuts cap hits but adds little accuracy, and accuracy falls when it is pushed past 2x): m=8 keeps only 0.40/0.42 of the pairs (result-ce52f8), and norm matching scales that part up about 1.6x, so the cell should land near the direction-1 edits (k=1 181, result-51a0e7; stored top1x1.5 cells 190 and 178 of 328) and below the full dial (203). |
| round-19/adversary-3 | 160 | [146, 174] | Same base-plus-flat-random-slope value as m = 64, moved down 2 and widened downward because the same norm is packed into 8 residual dimensions. |

## t03 (work-e340a2): How many of the 328 hard problems does the untrained Olmo 3 base with the opening cue get right by plurality vote over 8 samples per problem?

Unit: right answers of 328. Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "opening cue", "set": "the 328 (hard328)", "n": 328, "sampling": "not stated (samples 6 and 7 at seed 3060000)", "samples": 8, "grader": "not stated"}

> tests W1 (vote over 8 in [185, 199])

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 200 | [192, 209] | The base's vote curve on the 328 is 159.5/188.5/197 at k=1/4/6 (result-c065a6), still rising about 4 per sample, so k=8 should land a few problems above 197. |
| reader-2 | 200 | [192, 208] | Vote over 6 gave 197 (188.5 at 4) and the curve flattens because most wrong problems have no right sample, so 8 samples adds about 3. |
| round-19/account-1 | 200 | [191, 209] | Account S5 (the vote gains on hard328 only through scattered wrong answers, and most misses have no right sample, so about 9 points stay out of inference reach): the stored curve 159.5/188.5/197 at k=1/4/6 (result-c065a6) extrapolates log-linearly to 202 at k=8, trimmed for saturation because 107 of 131 wrong problems have no right sample among 6. |
| round-19/adversary-1 | 203 | [195, 211] | vote(k)=159.5+20.9 ln k fits the 1, 4, 6 points exactly and gives 203 at k=8, which is 197 plus about 6 from the two extra samples; the interval comes from tie-breaking and per-sample noise. |
| round-19/account-2 | 201 | [194, 208] | Account S5-S6 (votes help the base through scattered slips, but most of RL's vote wins on hard328 have no right base sample) means the cued-base vote curve keeps rising but flattens: 188.5 at 4 and 197 at 6 (result-c065a6), and a posterior-predictive simulation on the stored explore rows (day1_3/hard328_base_cue_s4r2) gives about +4 for 6 to 8, so about 201. |
| round-19/adversary-2 | 202 | [194, 210] | The slope is about 21 per unit ln k from k=1 to 6; flattened to about 17 that gives 17 x ln(8/6) = +5 over 197, so about 202, with plus or minus 8 for the two new samples and tie handling. |
| round-19/account-3 | 201 | [193, 209] | Account S4-S5 (votes only help where the base already writes a right sample, and wrong answers scatter): the base-cue vote curve on the 328 is 159.5 at 1, 188.5 at 4 and 197 at 6 (result-c065a6), and 107 of the 131 misses have no right sample in 6, so samples 7-8 add about 2 problems each, giving about 201, still below RL's 224. |
| round-19/adversary-3 | 201 | [192, 210] | 197 + 0.485 x (197 - 188.5) = 201, the 6->8 step scaled from the base's MATH-500 vote curve. |

## t04 (work-e340a2): On the 328 hard problems, for the untrained Olmo 3 base with the opening cue, how many more problems does a plurality vote over 8 samples get right than a vote over 4 samples?

Unit: right answers of 328, vote over 8 minus vote over 4. Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "opening cue", "set": "the 328 (hard328)", "n": 328, "sampling": "not stated (samples 6 and 7 at seed 3060000)", "samples": "8 vs 4", "grader": "not stated"}

> W2 (8 minus 4 at least 6)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 10 | [3, 17] | Vote over 8 (~200) minus vote over 4 (188.5 subset mean, or 192 in stored order) gives roughly 8-12. |
| reader-2 | 10 | [4, 16] | Vote over 4 is 188.5-192 depending on which four, against about 200 at 8. |
| round-19/account-1 | 11.5 | [5, 18] | Account S5 saturation applied to result-c065a6: vote over 4 is 188.5 and the log-linear step of ~14 per doubling of k (29 over k=1 to 4, 8.5 over k=4 to 6) is shrunk by the base having no right sample on most missed problems (knowledge-b19faf: 7 % per-sample rate on 0-of-4 problems), giving about +11.5. |
| round-19/adversary-1 | 14 | [5, 23] | 203 from the log-k fit minus 188.5 for the vote over 4 gives about 14; the wide interval covers which 4-sample vote is used and the tie-breaking noise. |
| round-19/account-2 | 12.5 | [7, 18] | Same account S5-S6 vote curve: the vote over 8 at about 201 minus the vote over 4 at 188.5 (result-c065a6), with the stored explore-row simulation giving roughly +12 from 4 to 8 samples. |
| round-19/adversary-2 | 12 | [5, 19] | Vote over 8 (about 202) minus a vote-over-4 point of about 190 (votek's 188.5, with room for the stored-order 192) gives about 12; the interval covers which k=4 tie rule is used and the noise from the new samples. |
| round-19/account-3 | 12 | [5, 20] | Account S4 (vote turns sometimes-right into right), with gains shrinking as the base's reach saturates (S5; knowledge-b19faf: 7% per-sample rate on 0-of-4 problems): about 201 for the vote over 8 minus 188.5 for the vote over 4 (result-c065a6) gives about +12. |
| round-19/adversary-3 | 12 | [6, 18] | 1.485 x 8.5 = 12.6 if the vote over 4 is averaged over subsets, 9 if it is samples 0-3 (192), so 12 with an interval covering both readings. |
