# Forecasts, round-20

Board snapshot 2026-11-16T01:54:42 UTC, written 2026-11-16T02:01:59 UTC. 2 targets; forecasters reader-1, reader-2, round-20/account-1, round-20/adversary-1, round-20/account-2, round-20/adversary-2, round-20/account-3, round-20/adversary-3.


Engine 19 open forecasts: each account-k forecasts as its account; adversary-k is a covariate-only forecaster blind to the account. Adversary forecasts a judge found to be the account's claim by construction are left out: none.


## t01 (work-4bfe4e): How many of the 328 hard problems the Olmo 3 base model answers correctly with the opening cue when edited by RL-Math's top-8 directions restricted to one shared 64-dimensional residual subspace per side (reading and writing), norm matched to the 1.5x edit.

Unit: right answers of 328. Cell: {"model": "Olmo 3 base + RL-Math top-8 directions edit restricted to one common residual subspace per side (wsp_edit glob), m = 64, norm matched to the 1.5x edit", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "not stated", "samples": "not stated", "grader": "not stated"}

> m = 64 and m = 8, norm matched to the 1.5x edit), hard328 cue, 2 cells

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 190 | [173, 206] | The 64-dim shared subspace keeps about 77% of the edit's squared norm (result-ce52f8), and projecting the kept components does not break the input-output pairing, so the score should land most of the way from base/random (about 159-164) to the full 1.5x edit (203). |
| reader-2 | 190 | [170, 207] | Full 1.5x top-8 edit scores 203 and random/base about 159-164; a shared 64-dim subspace keeps about 77% of the edit's norm (result-ce52f8) and mostly keeps the pairing that matters (result-aba970), so I expect most but not all of the +40 gain. |
| round-20/account-1 | 197 | [184, 209] | Account S3 (the gain is in the rank and lies in Math 3.1's top-8 subspace; another edit helps only as far as it lies there): m=64 keeps 0.757/0.780 of the squared norm (result-ce52f8), so the norm-matched edit holds sqrt(0.77)=0.88 of the 1.5x edit (about a 1.3x dial on the dial of result-6f1bb7: 1x 192, 1.5x 203, 2x 190), giving near RL's ~200 (S2: 200.25) less a few points, well above random 159-167 and cued base 164. |
| round-20/adversary-1 | 191 | [176, 205] | At s_eff 1.31, linear interpolation in kept share between the full-share curve (about 198 at kept 1) and the rank-1 2x cell (184 at kept 0.42) gives 184 + (0.77 - 0.42)/0.58 x 14, about 192; subtracting about 1 for the norm-matched leftover of 0.23 (unstructured equal-norm edits sit 1-6 below base) gives 191. |
| round-20/account-2 | 195 | [182, 207] | Account S1/S4/S5 (the gain lives in few paired directions on the base's shared step-by-step input/output place and saturates at RL's level): the common m=64 subspace keeps 0.76/0.78 of the top-8 edit (result-ce52f8, RL readers share one subspace result-c9ee85) with pairs intact, so norm-matched it acts like the full edit at ~1.7x, between top-8 1.5x 203, 2x 190 and k=64 200 (result-306787, result-51a0e7), well above random 159/base 164. |
| round-20/adversary-2 | 196 | [183, 209] | Kept share 0.768 gives a scale of 1.5 x sqrt(0.768) = 1.32x, which interpolates to 198.9 on the stored dial curve (fit A). The same share interpolates to 194.2 between the 1/3-share band mean of 177.7 and the full 1.5x edit's 203 (fit B). The average is 196. |
| round-20/account-3 | 195 | [182, 207] | Account S1/S5 (the low-rank core read from a step-by-step subspace and written forward; top-8 over all layers at 1x-2x gives c about 1, count 164+39c): the m=64 shared subspace keeps 0.76/0.78 of the edit (result-ce52f8), and norm matching scales that kept part to about 1.7x, so c is about 0.8 against the 1.5x edit's 203-207 and 2x's 190 (result-306787, day1_3 top8x1.5 cell). |
| round-20/adversary-3 | 198 | [185, 210] | Linear interpolation of the stored dial curve between scale 1 (192) and 1.5 (203) at the effective scale 1.5*sqrt(0.764) = 1.31 gives 198.8; with partial edits sitting near or above the along-edit interpolation at high kept share, this rounds to 198. |

## t02 (work-4bfe4e): How many of the 328 hard problems the Olmo 3 base model answers correctly with the opening cue when edited by RL-Math's top-8 directions restricted to one shared 8-dimensional residual subspace per side (reading and writing), norm matched to the 1.5x edit.

Unit: right answers of 328. Cell: {"model": "Olmo 3 base + RL-Math top-8 directions edit restricted to one common residual subspace per side (wsp_edit glob), m = 8, norm matched to the 1.5x edit", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "not stated", "samples": "not stated", "grader": "not stated"}

> m = 64 and m = 8, norm matched to the 1.5x edit), hard328 cue, 2 cells

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 177 | [158, 194] | The 8-dim subspace keeps only about 40% of the norm, and that part is scaled up about 1.6x in amplitude to match; it likely carries mostly direction 1, which alone scores about 183 (result-aba970), so I put it between random (159) and direction 1 alone, with downside risk from the overscaling. |
| reader-2 | 176 | [153, 198] | An 8-dim shared subspace keeps only about 40% of the norm and distorts the input-output pairs, so I expect something like direction 1 alone (183) or directions 3-8 alone (170), well short of 203 but likely above random (159). |
| round-20/account-1 | 184 | [169, 198] | Account S3 (rank, not norm, carries the gain; one direction per matrix gives half, 181 at 1x): m=8 keeps only 0.398/0.416 of the squared norm (result-ce52f8), so the norm-matched edit holds about 0.63 of the 1.5x edit (about a 0.95x dial, 192 at 1x in result-6f1bb7) with the rest rescaled off-direction, giving roughly the half-to-three-quarter gain over cued base 164 seen for Math 3.0's partly overlapping edit (182). |
| round-20/adversary-1 | 180 | [163, 197] | The nearest stored cells in (kept share, s_eff) are the rank-1 pair (interpolated 182.5 at s_eff 0.95) and the three layer bands (mean 178 at kept 0.33, s_eff 0.86); averaging them gives about 181, and subtracting about 1-2 for the norm-matched leftover of 0.59 gives 180. |
| round-20/account-2 | 180 | [166, 194] | Account S5 (top-1 gives about half, 181, and drops at 3x, 168): m=8 keeps only 0.40/0.42 of the edit (result-ce52f8), mostly the dominant direction-1 content (39% of top-8 energy, result-aba970), and norm matching scales it ~1.6x to an effective ~2.4x, so it lands near direction 1 at 2x 184 / 3x 168 (result-306787) rather than the full 203. |
| round-20/adversary-2 | 185 | [170, 200] | Kept share 0.407 gives a scale of 1.5 x sqrt(0.407) = 0.96x, which interpolates to 190.8 on the stored dial curve (fit A). The same share interpolates to 180.5 on the share fit (fit B). The average is 185, which also matches the 178-184 range of the stored smaller edits. |
| round-20/account-3 | 179 | [163, 194] | Account S5 (a single part gives c about 0.5, and one piece pushed to 3x turns negative): m=8 keeps only 0.40/0.42 (result-ce52f8), so norm matching runs the shared core at about 2.4x, like one direction per matrix at 2x and 3x (184 and 168, result-306787), which gives about 164+39*0.4. |
| round-20/adversary-3 | 187 | [172, 202] | Interpolating the dial curve at effective scale 0.95 gives 190, pulled 3 toward the 178-184 range of stored partial edits with similarly small kept shares (none of which reached 190), giving 187. |
