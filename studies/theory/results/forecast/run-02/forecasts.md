# Forecasts, run-02

Board snapshot 2026-11-15T14:53:16 UTC. 17 targets; forecasters reader-1, reader-2, r5-m03-rival, r6-account-rival, r6-m06, r7-m05, r7-m08, r7-m11, f2-m01, f2-m02, f2-m03, f2-m04, f2-m05, f2-m06.


## f2-m01

The autobench agent works under a fixed generation time per experiment, so it buys votes by shortening each sample (its best config: 10 samples at about 1,100 tokens each). Most MATH-500 problems are solved in under 2,000 tokens, so short samples plus a vote score well on dev100, but hard328 solutions need 6,000-14,000 tokens and short samples never reach them. For the base, each doubling of the token budget past 8,000 buys fewer problems.

Rests on: result-fa480f, result-5e17a6, result-1b6bf2, result-51fd20. Forecasts 10 of 17 targets. Outside both readers' intervals:

| target | value | 90 % interval | reader-1 | reader-2 | why the readers are wrong |
|---|---|---|---|---|---|
| t14 | 338 | [325, 351] | 362 | 356 | They treat the config as a full-length cue vote (~90 %), but its dev score of 86 with 10 samples at 1,111 tokens each shows short, budget-capped samples, and the dev maximum is inflated by selection. |
| t15 | 120 | [80, 160] | 190 | 197 | They score the agent's config like the swarm's 4-sample vote (192), but a vote cannot add answers that no short sample reaches on problems needing 6k-14k tokens. |
| t05 | 153 | [144, 162] | 168 | 172 | They add 8-10 for the doubled cap, but the base's returns shrink with each doubling (8k to 16k bought only 12), so 16k to 32k buys ~2. |

## f2-m02

The cued base's wrong answers on a problem rarely share a value: slips are per-sample chance events that land on scattered numbers, while right answers coincide. A plurality vote therefore wins a problem once the right share exceeds the largest wrong-value share, far below one half, and keeps converting such problems as samples are added, with no plateau by 12. The loss is in ties, which odd sample counts and more samples dissolve.

Rests on: result-5d032f, result-60d899, result-cbe0bc, result-c495fe. Forecasts 10 of 17 targets. Outside both readers' intervals:

| target | value | 90 % interval | reader-1 | reader-2 | why the readers are wrong |
|---|---|---|---|---|---|
| t03 | 463 | [457, 469] | 454 | 454 | They let the vote plateau below pass@4 (467), but with scattered wrong values a problem is won once its right share beats the largest wrong-value share, so 5 more samples convert most problems the base solves 1-2 times in 4. |
| t04 | 466 | [460, 472] | 456 | 456 | They add only ~2 from 9 to 12 votes, but under value dispersion the vote keeps tracking pass@k and passes 463. |
| t13 | 94 | [91, 97] | 89 | 89 | They read the maximum as noise creep from 86, but a vote over dispersed samples is worth ~93 on dev100 by itself once the agent keeps full-length samples. |

## f2-m03

The top singular directions of the RL-Math difference set when the base stops, not whether its reasoning is right: their dose sets the cap-hit rate, while right answers per finished answer stay near the base's 0.65; RL's correctness lives in the remainder of the difference. Past dose 1, extra finishes on problems the base cannot solve are guesses, so accuracy is flat from 1x to 2x, and on MATH-500, with few cap hits, the dial adds little.

Rests on: result-6f1bb7, result-51a0e7, result-284db5, result-1b6bf2. Forecasts 10 of 17 targets. Outside both readers' intervals:

| target | value | 90 % interval | reader-1 | reader-2 | why the readers are wrong |
|---|---|---|---|---|---|
| t10 | 186 | [179, 193] | 197 | 196 | They regress the 203 only to ~196, but a stop-only dial is flat between 1x and 2x, and the 1x and 2x cells were themselves on a favourable seed. |
| t11 | 205 | [197, 213] | 219 | 220 | They add RL's vote gain to a ~196 mean, but the single mean is ~186, and an edit with base-level precision per finished answer gains no more under the vote than RL does. |
| t12 | 426 | [416, 436] | 444 | 440 | They interpolate toward the theta cue cells (441-453), which carry RL's whole difference, but the 8 directions carry only the stopping, and MATH-500 has only 27 cap hits to finish. |

## f2-m04

A capped sample gives no answer, so in a plurality vote it abstains instead of adding a wrong value. Think-SFT's vote sits near its pass@4 because its unsolved samples run to the cap rather than box a guess. Anything that makes it finish, a 32k cap or the RL difference, turns abstentions into mostly wrong, scattered answers that tie or outvote lone right samples: single scores rise, vote gains shrink.

Rests on: result-818c20, result-c8b994, result-5251c9, result-3387ce. Forecasts 10 of 17 targets. Outside both readers' intervals:

| target | value | 90 % interval | reader-1 | reader-2 | why the readers are wrong |
|---|---|---|---|---|---|
| t16 | 238 | [229, 247] | 252 | 250 | They let the vote rise with pass@4, but at 16k the vote (241) was almost pass@4 (244) only because unsolved samples abstained by capping. |
| t17 | 72 | [64, 80] | 85 | 84 | They add ~10 for finished cap hits, but on fresh2026 the abstentions are what lift Think-SFT's vote, and finishing them mostly adds wrong votes. |
| t08 | 236 | [227, 245] | 248 | 249 | They add +15-20 for the vote, but at a=2 the model abstains far less, so it loses Think-SFT's near-pass@4 filter, and the new seeds regress from the coefficient picked on the 328. |

## f2-m05

The RL-Math difference carries RL's habit of ending a long unsolved attempt with an asserted, underived number (per 1,312 hard328 samples RL finishes long and wrong 381 times, the base 281). Added to another model it turns unfinished attempts into such guesses and cuts slower derivations short. On new problems, where RL's finished precision is 43 %, the guesses are wrong, so gains measured on hard328 shrink or reverse; on MATH-500 it is neutral.

Rests on: result-fc7efc, result-02da9f, result-5251c9, result-bce075. Forecasts 9 of 17 targets. Outside both readers' intervals:

| target | value | 90 % interval | reader-1 | reader-2 | why the readers are wrong |
|---|---|---|---|---|---|
| t07 | 56 | [49, 63] | 66 | 66 | They carry over hard328's +7 points, but on new problems the RL difference turns Think-SFT's productive long attempts into asserted answers whose precision is about 43 %, so the mean falls below 60. |
| t06 | 63 | [55, 71] | 76 | 77 | They assume finishing helps the vote, but the transplant's new finishes on 2026 problems are asserted numbers that are rarely right. |
| t10 | 187 | [180, 194] | 197 | 196 | They read the 203 as mostly signal, but what the edit adds past 1x is asserted answers on problems the base cannot solve, so a 4-seed mean drops to the 1x level. |

## f2-m06

Think-SFT's difference from the base carries long derivation; the RL-Math difference carries a controller that stops once an answer is derived. The two are orthogonal (cosine -0.00001), so their sum acts as both, but inside Think-SFT's long traces the controller is diluted and needs a = 2 to reach RL's stopping strength. At a = 2 the model derives like Think-SFT and finishes like RL on any set and seed, so gains are largest where Think-SFT caps most.

Rests on: result-3387ce, result-e2482e, result-818c20, result-5251c9, result-c8b994. Forecasts 10 of 17 targets. Outside both readers' intervals:

| target | value | 90 % interval | reader-1 | reader-2 | why the readers are wrong |
|---|---|---|---|---|---|
| t09 | 476 | [468, 484] | 465 | 465 | They put a=2 at a=1's plateau, but the stronger controller turns Think-SFT's remaining cap hits and unboxed gold lines into boxed finishes, worth ~8-9 more. |
| t07 | 78 | [70, 86] | 66 | 66 | They shrink the hard328 gain, but the gain scales with how often Think-SFT caps, which is highest on fresh2026. |
| t08 | 261 | [252, 270] | 248 | 249 | They shrink the vote gain for lower precision, but additive modules keep Think-SFT's derivations, so precision stays high with RL's coverage. |

## t01 (work-480b1f): How many of the 500 MATH-500 problems the RL-Zero-Math step-100 checkpoint answers right with the plain prompt, one sample at T 1.0 / top-p 1.0, grader v3 (full 500-problem rerun).

Unit: right answers of 500. Cell: {"model": "Olmo-3.1 RL-Zero-Math, released checkpoint step_0100 (pinned)", "prompt": "plain", "set": "MATH-500", "n": 500, "sampling": "T 1.0 / top-p 1.0, token cap not stated, seed 45000000", "samples": 1, "grader": "v3"}

> s0100 plain partial 405/478 (base cue 397 on those). Full cell 6a2f running.

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 420 | [408, 432] | Partial 405/478 plus about 15 of the remaining 22 harder problems (base cue got 13 of them), with rerun noise because the full rerun is a new sample. |
| reader-2 | 418 | [405, 431] | Partial 405/478 plus ~13 of the 22 held-back (longer) problems, as the base cue got 13/22 on them, with ~7-problem rerun noise on a new box. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 419 | [410, 428] | 405/478 plus ~13 of the 22 long problems that were cut, rerun noise ~6. |
| f2-m02 | - |  | no forecast |
| f2-m03 | 420 | [411, 429] | Step 100 already finishes like the cued base; 405/478 plus ~14 of 22. |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | 421 | [412, 430] | Step 100 has part of the controller: 405/478 plus ~15 of 22. |

## t02 (work-480b1f): At RL-Zero-Math step 100 on MATH-500 (one sample, T 1.0 / top-p 1.0, grader v3), the score with the opening cue minus the score with the plain prompt, in percentage points.

Unit: points (cue minus plain, of 500). Cell: {"model": "Olmo-3.1 RL-Zero-Math, released checkpoint step_0100 (pinned)", "prompt": "cue minus plain", "set": "MATH-500", "n": 500, "sampling": "T 1.0 / top-p 1.0, token cap not stated, seed 45000000", "samples": 1, "grader": "v3"}

> the cue's gain at each released checkpoint

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 1.4 | [-1.8, 4.6] | Step-100 cue 427 minus an expected plain score of about 420, giving about 7 problems = 1.4 percentage points; step 400 showed the cue adding nothing. |
| reader-2 | 1.8 | [-1, 4.6] | Step-100 cue 427 minus a forecast plain ~418 = ~9 problems = 1.8 points; noise comes from the plain rerun. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t03 (work-60f040): How many of the 500 MATH-500 problems the untrained base with the opening cue gets right by majority vote over 9 samples at T 1.0, grader v3.

Unit: right answers of 500. Cell: {"model": "untrained base (cued base)", "prompt": "opening cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0, top-p not stated, token cap not stated (same cell as the stored 4 samples)", "samples": 9, "grader": "v3, majority vote over 9 samples"}

> vote over 9 = 456 [449, 462] of 500 (result-c637b2)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 454 | [447, 461] | Vote over 4 is 446 and pass@4 is 467; Wang's majority curve adds about 2.5 points from 4 to 8 votes, and 9 votes have fewer ties. |
| reader-2 | 454 | [447, 461] | Vote over 4 = 446, with diminishing vote gains (Wang maj@4 to maj@8 +2.5 pts) and pass@4 467, so the vote over 9 lands around 454. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 456 | [449, 462] | The rival's closing sentence predicts that a base-only vote over more cued samples recovers part of the open sharpening share, giving 456/500 (interval 449-462 as filed in result-c637b2), up from the stored vote over 4 of 446. |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | 449 | [443, 455] | The theory places the cued base's misread and slip steps near the mode of its generic-problem prior, so extra samples tend to repeat them rather than outvote them; the vote should then level off just above the stored vote over 4 (446, 450 after restart) instead of climbing to 456. |
| r7-m08 | 453 | [445, 461] | The theory's no_intervention clause says selecting among base samples can't reproduce the veto, because the vetoed slips and misreads are high-probability under the base; so the vote should level off a few points above the stored vote over 4 (446-450) and stay below RL's single sample (456-463), with the extra samples mainly removing the ties of an even-sized vote. |
| r7-m11 | 452 | [445, 459] | The theory's scope is the cued base on MATH-500 at T 1.0 with grader v3, and it says wrong answers drawn under the same opening agree with each other. So adding more cued samples mostly adds to the same wrong groups, and the vote should level off: a few problems above the vote over 4 (446) and short of pass@4 (467) and the independent-slip curve, below the account's 456. |
| f2-m01 | 456 | [450, 462] | Full-length samples are not budget-limited; going from 4 to 9 votes follows Wang's maj@4 to maj@8 step (+2.5 points) above 446. |
| f2-m02 | 463 | [457, 469] | The 4-sample vote (446) loses 36 tied problems; 9 odd votes resolve most ties, and problems with a 1-2 of 4 solve rate win against scattered wrong values. |
| f2-m03 | - |  | no forecast |
| f2-m04 | 457 | [451, 463] | MATH-500 has few cap hits, so the vote grows normally: ~+11 from 4 to 9. |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t04 (work-60f040): How many of the 500 MATH-500 problems the untrained base with the opening cue gets right by majority vote over 12 samples at T 1.0, grader v3.

Unit: right answers of 500. Cell: {"model": "untrained base (cued base)", "prompt": "opening cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0, top-p not stated, token cap not stated (same cell as the stored 4 samples)", "samples": 12, "grader": "v3, majority vote over 12 samples"}

> Vote over k = 1..12 samples of the untrained cued base on MATH-500

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 456 | [449, 463] | Vote keeps rising slowly past 9 samples (Wang majority@8 91 %, @16 93 %), so about 2 more than the vote over 9. |
| reader-2 | 456 | [448, 463] | A small further gain over the vote over 9 as the vote curve plateaus below pass@k. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 457 | [450, 463] | Same base-only vote clause of the rival: sharpening problems (base right 1-2 of 3) are on one difficulty axis, so going from 9 to 12 votes adds at most about one more problem beyond the predicted 456 plateau, while reach problems (kB = 0, ~0.1 of the gap) stay unrecovered. |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | 450 | [444, 456] | Same mode claim: the near-mode misread and slip errors recur across samples, so going from 9 to 12 votes adds at most about a problem over the plateau near the vote over 4 (446). |
| r7-m08 | 455 | [447, 463] | Same no_intervention clause: the base keeps re-sampling its likely wrong steps, so 12 samples add only about 2 problems over the vote over 9 and still sit at or below RL's single sample (456-463), well short of base pass@4 (467). |
| r7-m11 | 453 | [446, 460] | Same part of the theory: wrong groups set by the opening grow along with the right group as samples are added, so going from 9 to 12 cued samples adds about one problem. |
| f2-m01 | 458 | [452, 464] | About 2 more problems than the 9-vote as the curve flattens. |
| f2-m02 | 466 | [460, 472] | The vote follows pass@k growth (pass@4 467, pass@12 ~480) at a fixed lag. |
| f2-m03 | - |  | no forecast |
| f2-m04 | 459 | [453, 465] | +2 over the 9-vote. |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t05 (work-ceccc0): How many of the 328 harder problems the untrained base with the opening cue answers right with the token cap raised to 32,768, one sample at T 1.0, seed 3000000, grader v3.

Unit: right answers of 328. Cell: {"model": "untrained base", "prompt": "opening cue", "set": "hard328", "n": 328, "sampling": "T 1.0, top-p not stated, token cap 32,768, seed 3000000", "samples": 1, "grader": "v3"}

> Base cue cell was lost with its vast.ai box during the restart; rerunning as 4 shards on AWS L40S.

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 168 | [155, 181] | Base cue single is 158-164 at 16k with 77 cap hits; a 32k cap lets roughly 8-10 of those finish right (Think-SFT gained 23, RL 2). |
| reader-2 | 172 | [160, 184] | Base cue 164 at 16k (155-168 across reruns) plus ~8-10 of 77 cap hits finishing right at 32k; base cap hits are mostly failures to solve, so it gains less than Think-SFT (+23) but more than RL (+2). |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 153 | [144, 162] | The 16k level of this sharded rerun is ~151-155 (earlier 4-shard replay 155; cap32 runs came in low at 16k), and the second 16k tokens buy ~2. |
| f2-m02 | - |  | no forecast |
| f2-m03 | 162 | [153, 171] | A longer cap is a stop change at base precision: ~+4 over the base's 16k level of ~158. |
| f2-m04 | 163 | [154, 172] | Single-sample cell: finishing ~70 caps at ~10 % precision adds ~5 to ~158. |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t06 (work-8b4030): How many of the 136 fresh2026 competition problems the transplant model Think-SFT + 2 x (RL-Math - base) gets right by majority vote over 4 samples.

Unit: right answers of 136. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated, majority vote over 4 samples"}

> fresh2026 (136 problems, 4 samples, seeds of SPEC_fresh)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 76 | [65, 87] | Think-SFT vote 75 and RL 57 on fresh2026; a=2 raises singles but lowers finished-answer precision, so the vote gains less than the single sample does. |
| reader-2 | 77 | [68, 86] | Think-SFT vote 75 at 46% cap hits; a=2 cuts cap hits but lowers precision, so the single rises to ~66 while the vote gain over the single shrinks. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 78 | [70, 86] | Singles ~66 plus a vote gain of ~+12 from coinciding right answers. |
| f2-m03 | 73 | [65, 81] | Singles up ~4, vote gain shrinks: about Think-SFT's 75. |
| f2-m04 | 70 | [62, 78] | Fewer abstentions on fresh problems dilute the vote: below Think-SFT's 75. |
| f2-m05 | 63 | [55, 71] | Asserted wrong values replace abstentions and fewer right derivations survive: the vote falls below Think-SFT's 75. |
| f2-m06 | 86 | [78, 94] | Singles ~78 at high precision; the vote adds ~8. |

## t07 (work-8b4030): The mean single-sample number of right answers (over 4 samples) of Think-SFT + 2 x (RL-Math - base) on the 136 fresh2026 problems, against references Think-SFT 60.0 and RL 50.5.

Unit: mean right answers of 136 per sample. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated, mean of single-sample scores over 4 samples"}

> Fresh references: Think-SFT 60.0, RL 50.5 of 136.

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 66 | [57, 75] | Think-SFT single 60.0 plus a hard328-like a=2 gain of about +7 points (cap hits 46 % leave room to finish). |
| reader-2 | 66 | [58, 74] | Think-SFT single 60.0 plus a shrunken version of a=2's +6.9-point hard328 gain (a was chosen on hard328, so I regressed the gain toward zero). |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | 64 | [57, 71] | Finishing more of Think-SFT's 46 % capped samples at reduced precision adds ~4. |
| f2-m04 | 67 | [60, 74] | Singles do rise: Think-SFT 60 plus ~7 from finishing. |
| f2-m05 | 56 | [49, 63] | On 2026 problems the transplant cuts Think-SFT's long derivations into RL-style assertions (precision ~43 %), losing more right answers than it adds. |
| f2-m06 | 78 | [70, 86] | Fresh2026 is where Think-SFT caps most (46 %); stopping like RL with Think-SFT's derivations adds ~18 at its finished precision. |

## t08 (work-8b4030): How many of the 328 harder problems Think-SFT + 2 x (RL-Math - base) gets right by majority vote over 4 samples (2 earlier samples plus 2 new ones).

Unit: right answers of 328. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated; new samples 3-4 at seeds 3,200,000 and 3,300,000", "samples": 4, "grader": "not stated, majority vote over 4 samples"}

> hard328 samples 3-4 for the vote over 4

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 248 | [238, 258] | a=2 singles 234 and 229; the vote gain is smaller than Think-SFT's +32 because precision falls to about 72 %, so about +17. |
| reader-2 | 249 | [240, 258] | Singles 234/229, with a vote gain (+15-20) between RL's +21 and Think-SFT's near-pass@4 regime, reduced by lower precision. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 251 | [242, 260] | Singles ~230 plus a vote gain of ~+21, as for RL. |
| f2-m03 | 244 | [235, 253] | a=2 on Think-SFT mostly adds finishing; the vote gain shrinks as precision falls toward 0.8. |
| f2-m04 | 236 | [227, 245] | New-seed singles ~228; with caps cut from 94.5 to ~54 per sample the vote gain falls to ~+8. |
| f2-m05 | 241 | [232, 250] | hard328 sits near the transplant's training distribution; new seeds ~228 plus a reduced vote gain. |
| f2-m06 | 261 | [252, 270] | Singles replicate (~231) and precision stays ~85 %, so the vote gains like Think-SFT's own (+30). |

## t09 (work-8b4030): How many of the 500 MATH-500 problems Think-SFT + 2 x (RL-Math - base) answers right with one sample.

Unit: right answers of 500. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "MATH-500", "n": 500, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> MATH-500 1 sample

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 465 | [455, 474] | a=1 scored 467 on MATH-500 and Think-SFT/RL singles are 454-463; a=2 should sit near that plateau. |
| reader-2 | 465 | [455, 474] | a=1 scored 467 on MATH-500 and Think-SFT/RL singles are 454-463; a=2 should land near the same ceiling. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | 463 | [456, 470] | MATH-500 has few cap hits for extra stopping dose to convert; a=2 sits at a=1's level or just below. |
| f2-m04 | - |  | no forecast |
| f2-m05 | 462 | [455, 469] | MATH-500 problems are solvable, so assertions rarely occur: about a=1's level or slightly below. |
| f2-m06 | 476 | [468, 484] | a=1 already 467; at full controller strength Think-SFT's 25 MATH-500 cap hits and its v3-rejected answer lines (~4 per sample) become boxed finishes. |

## t10 (work-ab0f72): The mean single-sample number of right answers (over 4 samples) on the 328 harder problems of the base plus 8 RL-Math directions per matrix at 1.5x, with the cue at T 1.0, grader v3.

Unit: mean right answers of 328 per sample. Cell: {"model": "base + 8 top singular directions per matrix of (RL-Math - base) at 1.5x", "prompt": "opening cue", "set": "hard328", "n": 328, "sampling": "T 1.0, top-p not stated, token cap not stated", "samples": 4, "grader": "v3, mean of single-sample scores over 4 samples"}

> hard328 with 4 samples (single-sample mean

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 197 | [189, 205] | 203 at 1.5x was the best of seven sizes in one sample (192 at 1x, 190 at 2x), so the 4-sample mean regresses to about 197. |
| reader-2 | 196 | [188, 204] | 203 was the best of seven sizes; neighbours 1x 192 and 2x 190 suggest a true mean of ~196. |
| r5-m03-rival | 197 | [188, 206] | The theory says the top-8 edit puts the base on a weak dose of RL's own policy (longer answers, checking, few quick wrong answers), and the cue removes the plain-base register. A larger 1.5x dose should then bring the single-sample mean close to RL's 4-sample mean (200), between the 1x cell (192) and the one 1.5x sample (203, the best of 7 sizes, so likely to regress). |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | 186 | [179, 193] | Under a flat dial, 1.5x scores like 1x (192) and 2x (190); those single draws share a seed on which the base itself scored ~5 above its mean, so fresh seeds give ~186. |
| f2-m04 | - |  | no forecast |
| f2-m05 | 187 | [180, 194] | At 2x the edit finished all 77 base cap-hit problems with 14 right: added dose adds assertions, so the 4-seed mean sits at the 1x level. |
| f2-m06 | 193 | [186, 200] | On the base the controller lacks Think-SFT's derivations; 1.5x is near 1x's 192. |

## t11 (work-ab0f72): How many of the 328 harder problems the base plus 8 RL-Math directions per matrix at 1.5x gets right by majority vote over 4 samples, cue, T 1.0, grader v3 (base 192, RL 221).

Unit: right answers of 328. Cell: {"model": "base + 8 top singular directions per matrix of (RL-Math - base) at 1.5x", "prompt": "opening cue", "set": "hard328", "n": 328, "sampling": "T 1.0, top-p not stated, token cap not stated", "samples": 4, "grader": "v3, majority vote over 4 samples"}

> vote over 4 vs base 192, RL 221

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 219 | [208, 229] | Single mean about 197 plus an RL-like vote gain of about +22 (base +33, RL +21) because cap hits fall to about 25. |
| reader-2 | 220 | [209, 230] | Single mean ~196 plus an RL-like vote gain of ~+24, since the edit cuts cap hits (base +33 and RL +21 under the vote). |
| r5-m03-rival | 219 | [208, 230] | If the 1.5x edit with the cue gives RL-like answers (few cap hits, errors only on hard problems), the 4-sample vote should gain about what RL's does (200 -> 221, +21), not the cued base's larger +33 from many cap hits: 197 + ~22 = 219. |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 217 | [208, 226] | Single mean ~194 plus an RL-like vote gain (~+22), since the edit's wrong values are also scattered. |
| f2-m03 | 205 | [197, 213] | Single mean ~186 plus RL's vote gain (+19-21), as the edit leaves few cap-hit abstentions and base-level precision. |
| f2-m04 | 210 | [202, 218] | The base's +33 vote gain came from its 77 cap abstentions; with 25 left the edit gains like RL (+20) on a ~190 mean. |
| f2-m05 | 209 | [201, 217] | Mean ~187 plus a vote gain of ~+22, since asserted wrong values rarely agree. |
| f2-m06 | 215 | [207, 223] | Mean ~193 plus an RL-like vote gain. |

## t12 (work-ab0f72): How many of the 500 MATH-500 problems the base plus 8 RL-Math directions per matrix at 1.5x answers right with one sample, cue, T 1.0, grader v3 (base cue 410, RL 457).

Unit: right answers of 500. Cell: {"model": "base + 8 top singular directions per matrix of (RL-Math - base) at 1.5x", "prompt": "opening cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0, top-p not stated, token cap not stated", "samples": 1, "grader": "v3"}

> MATH-500 one sample (base cue 410, RL 457)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 444 | [432, 456] | Top-8 at 1x plain is 427 and theta cue cells are 441-453; with the cue and 1.5x it should land in the mid-440s. |
| reader-2 | 440 | [428, 452] | Between base cue 410 and RL 457: top-8 plain gave 427 and theta-0.25 cue 441; MATH-500 has few cap hits for the edit to remove. |
| r5-m03-rival | 452 | [440, 462] | Fit the theory's mixture to top8 plain 427/500: 12.5% plain-base answers right about half the time, so the RL-like answers are right about 90.5% of the time. With the cue every answer is RL-like, giving 0.905 x 500 = 452, in line with theta 1.5 cue at 453. |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 438 | [429, 447] | MATH-500 answers fit inside the 16k budget, so the edit's finishing adds only on the base's 27 cap hits, on top of top8's 427. |
| f2-m02 | - |  | no forecast |
| f2-m03 | 426 | [416, 436] | 8 directions alone gave 427 plain; the cue adds nothing to an installed opening, and finishing ~15 of 27 cap hits at ~0.4 precision is offset by guesses. |
| f2-m04 | - |  | no forecast |
| f2-m05 | 436 | [426, 446] | Few long unsolved attempts on MATH-500; the edit gives roughly top8's 427 plus a small cue and finish gain. |
| f2-m06 | 445 | [436, 454] | The controller boxes and finishes the cued base's answers: top8 427 plus cue and finishing. |

## t13 (work-ce7583): The best dev100 score (right of 100) the single headless autobench agent reaches after all 40 experiments starting from the plain prompt.

Unit: right answers of 100. Cell: {"model": "not stated", "prompt": "chosen by the agent, starting from the plain prompt", "set": "dev100 (MATH-500 dev split)", "n": 100, "sampling": "chosen by the agent (best at 15 of 40: 10 samples + vote); not stated for the final", "samples": "not stated", "grader": "not stated"}

> 40 experiments on dev100 from the plain prompt

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 89 | [86, 93] | Best was 86 after 15 of 40 experiments, and the maximum over 25 more noisy tries on dev100 usually creeps up by 2-4. |
| reader-2 | 89 | [86, 93] | Best-so-far was already 86 at 15 of 40 experiments and can only rise, with max-of-noise gains of a few points. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 87 | [86, 90] | 86 at 15 of 40 came from ~1,100-token samples; short samples saturate on dev100, so later tries add only 1-2. |
| f2-m02 | 94 | [91, 97] | On dev100 a vote over 10+ cue samples alone is worth ~93-94 (cue single 84), and the search keeps the best of 40. |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t14 (work-ce7583): How many of the 400 math400 problems the autobench agent's final configuration answers right in the final run.

Unit: right answers of 400. Cell: {"model": "not stated", "prompt": "the autobench agent's final configuration", "set": "math400", "n": 400, "sampling": "the agent's final configuration; not stated", "samples": "not stated", "grader": "not stated"}

> then finals on math400 and hard328 against the swarm cue config

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 362 | [345, 375] | A vote over about 10 cue samples is near 90-91 % on MATH-500 (vote over 4 is 89.2 %), minus some overfit to dev100. |
| reader-2 | 356 | [342, 368] | A 10-sample cue vote on MATH-500 is ~89-91%, dev100 runs ~2 points easy and the config was selected on dev, so ~89% of 400. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 338 | [325, 351] | Short-sample config is worth ~85.5 % on dev100 once selection is removed; dev100 runs ~2 points easy (cue 84 vs 82 %), so ~84.5 % of 400. |
| f2-m02 | 372 | [362, 382] | A ~10-sample vote on the other 400 converts most tied and low-rate problems: ~93 %. |
| f2-m03 | - |  | no forecast |
| f2-m04 | 356 | [344, 368] | Vote of cue-like samples on MATH problems, minus dev overfit. |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t15 (work-ce7583): How many of the 328 harder problems the autobench agent's final configuration answers right in the final run.

Unit: right answers of 328. Cell: {"model": "not stated", "prompt": "the autobench agent's final configuration", "set": "hard328", "n": 328, "sampling": "the agent's final configuration; not stated", "samples": "not stated", "grader": "not stated"}

> then finals on math400 and hard328 against the swarm cue config

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 190 | [165, 210] | Base cue vote over 4 is 192 on hard328; a bigger vote helps a little, but a token or time budget tuned on MATH-500 may cut long answers. |
| reader-2 | 197 | [180, 210] | Base cue vote over 4 on the 328 is 192 (pass@4 207), and a ~10-sample vote adds a few problems. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 120 | [80, 160] | One full base sample gets 81 hard328 problems within 4,000 tokens; at ~1,100-1,500 tokens per sample far fewer finish, and a vote over ~10 such samples gives ~120. |
| f2-m02 | 200 | [182, 218] | Base 4-vote 192 on hard328; ~10 dispersed samples add ~8. |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t16 (work-dc9359): How many of the 328 harder problems Think-SFT with the cue gets right by majority vote over 4 samples with the token cap at 32,768.

Unit: right answers of 328. Cell: {"model": "Think-SFT", "prompt": "opening cue", "set": "hard328", "n": 328, "sampling": "T not stated, top-p not stated, token cap 32,768", "samples": 4, "grader": "not stated, majority vote over 4 samples, scored at 32,768"}

> Think-SFT + cue vote over 4 at token cap 32,768 on hard328

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 252 | [242, 262] | 16k vote 241 is near pass@4 (244), and a 32k cap adds +23 right per sample, so pass@4 and the vote rise by about 10. |
| reader-2 | 250 | [240, 260] | 32k single 230 (mean ~228); with cap hits gone the vote no longer equals pass@4, so it gains ~+22 like RL's vote. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 251 | [242, 260] | Think-SFT's long answers are productive: +23 per sample at 32k, so pass@4 and the vote rise by ~10. |
| f2-m02 | 254 | [245, 263] | At 32k the newly finished wrong answers are scattered and do not outvote coinciding right ones, so the vote rises with pass@4. |
| f2-m03 | 250 | [241, 259] | Single +23 at 32k; vote gain +8-10. |
| f2-m04 | 238 | [229, 247] | At 32k, 68 of 91 newly finished answers are wrong; problems won at 16k by one right sample plus caps now tie or lose, roughly cancelling the new rights. |
| f2-m05 | 247 | [238, 257] | Think-SFT finishing at 32k derives rather than asserts (36 % asserted), so its vote still gains ~+6. |
| f2-m06 | 252 | [243, 261] | A longer cap without the controller: +23 per sample, vote +11. |

## t17 (work-dc9359): How many fresh2026 problems Think-SFT with the cue gets right by majority vote over 4 samples with the token cap at 32,768.

Unit: right answers of fresh2026 problems. Cell: {"model": "Think-SFT", "prompt": "opening cue", "set": "fresh2026", "n": "not stated", "sampling": "T not stated, top-p not stated, token cap 32,768", "samples": 4, "grader": "not stated, majority vote over 4 samples, scored at 32,768"}

> fresh2026 (4 samples)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 85 | [74, 96] | 16k vote 75 of 136 with 46 % cap hits; the 32k cap lets many of them finish at about 80 % precision, so about +10. |
| reader-2 | 84 | [74, 94] | 16k vote 75 / single 60 at 46% cap hits; at 32k most cap hits finish and ~20% are right, giving a single of ~72 and a vote of ~84. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 82 | [74, 90] | 46 % of samples are capped at 16k; at 32k ~20 % of them finish right, adding ~7 to the vote. |
| f2-m02 | 85 | [77, 93] | Single rises ~13 at 32k; dispersed wrong values keep the vote gain intact. |
| f2-m03 | - |  | no forecast |
| f2-m04 | 72 | [64, 80] | 46 % of fresh samples abstain at 16k, which is why the vote sits 15 above the single; converting them at ~20 % precision costs the vote about what it adds to singles. |
| f2-m05 | 78 | [70, 86] | Newly finished fresh answers are mostly derived but wrong; +3 to the vote. |
| f2-m06 | 84 | [76, 92] | Fresh caps finish at 32k; vote +9. |
