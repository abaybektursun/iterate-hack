# Forecasts, run-01

Board snapshot 2026-11-15T14:45:56 UTC. 20 targets; forecasters reader-1, reader-2, r5-m03-rival, r6-account-rival, r6-m06, r7-m05, r7-m08, r7-m11.


## t01 (work-480b1f): How many of the 500 MATH-500 problems the Olmo-3.1 RL-Zero-Math step-100 checkpoint answers right with the plain prompt, one sample at T 1.0 / top-p 1.0, graded by grader v3.

Unit: right answers of 500. Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math checkpoint step_0100", "prompt": "plain", "set": "MATH-500", "n": 500, "sampling": "T 1.0 / top-p 1.0, token cap not stated, seed 45000000", "samples": 1, "grader": "v3"}

> s0100 plain was cut at 478/500 by the AWS time limit (exit 137)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 423 | [410, 436] | Interim 405 of 478 (84.7 %) scaled to 500 is about 424; this is a new sample on a new box, so I use binomial noise around the step-400 plain 436 and the spec's 428. |
| reader-2 | 421 | [408, 433] | Interim 405 of 478 (84.7 %) with the unfinished problems likely the long, harder ones; between base cue 410 and step-400 plain 436, spec predicted 428. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |

## t02 (work-480b1f): At the Olmo-3.1 RL-Zero-Math step-100 checkpoint on MATH-500 (one sample, T 1.0 / top-p 1.0, grader v3), the right-answer count with the opening cue (427) minus the count with the plain prompt.

Unit: difference in right answers of 500 (cue minus plain). Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math checkpoint step_0100", "prompt": "cue minus plain", "set": "MATH-500", "n": 500, "sampling": "T 1.0 / top-p 1.0, token cap not stated", "samples": 1, "grader": "v3"}

> the cue's gain at each released checkpoint

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 4 | [-10, 18] | Cue cell 427 minus about 423 plain; the cue added -5 at step 400 and the spec predicted +0.5, and the noise of two single samples is about 8 problems. |
| reader-2 | 6 | [-7, 19] | 427 cue minus a plain forecast of about 421; the cue added nothing at step 400 (431 vs 436) and step 100 already opens with Okay on 478/500. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |

## t03 (work-60f040): How many of the 500 MATH-500 problems the untrained Olmo 3 base with the opening cue gets right by majority vote over 9 samples at T 1.0, graded by grader v3.

Unit: right answers of 500. Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "opening cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0 / top-p 1.0 (same cell as the stored 4 samples), token cap not stated", "samples": 9, "grader": "v3, majority vote (tie rule not stated)"}

> vote over 9 = 456 [449, 462] of 500 (result-c637b2)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 454 | [445, 462] | Vote over 4 is 446-450; Wang et al.'s majority curve (88.5 at 4, 91 at 8) suggests +2 to +3 points at 9, and pass@4 is 467; slightly below the theory's 456 because the grouping rule is uncertain. |
| reader-2 | 453 | [446, 460] | Vote over 4 is 446 (450 with restart), pass@4 467; Wang's majority curve gives about +2.5 points from 4 to 8 votes; theory predicted 456. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 456 | [449, 462] | The rival's closing sentence says a base-only vote over more samples recovers part of the sharpening share and predicts 456/500 (interval 449-462 from result-c637b2), up from the vote-over-4 baseline of 446. |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | 453 | [445, 461] | Inside the theory's scope cell (cued base, MATH-500, T 1.0, v3): misreads and slips depend on the path, so siblings are mostly right (afc423: 39 of 48), and a vote recovers them; wrong plans depend on the problem and repeat, which caps the vote. That puts vote-9 a little above the board's vote-4 of 446 (subsets 435-446), below pass@4 467, near Wang's majority@8 of about 91 %. |
| r7-m08 | 453 | [446, 460] | The theory's no_intervention clause says selection among base samples is the only veto the base can do on its own, measured at 446-450 for a vote over 4, and its no-new-path logic means problems the base never solves stay lost; so a vote over 9 adds only a few reliability problems above 446 and stays under pass@4 467 (Wang's maj@8 curve puts this near 91 %). |
| r7-m11 | 451 | [444, 458] | The theory's statement says wrong samples drawn under the one shared cue agree with each other and keep the vote below the independent-slip prediction (about 10 problems short at k=4, result-e41d94); more samples under the same opening do not break those wrong groups, so vote over 9 rises only a little above the 4-vote 446 and stays under the independent account's 456 (result-c637b2). |

## t04 (work-60f040): How many of the 500 MATH-500 problems the untrained Olmo 3 base with the opening cue gets right by majority vote over 12 samples at T 1.0, graded by grader v3.

Unit: right answers of 500. Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "opening cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0 / top-p 1.0 (same cell as the stored 4 samples), token cap not stated", "samples": 12, "grader": "v3, majority vote (tie rule not stated)"}

> Vote over k = 1..12 samples of the untrained cued base on MATH-500

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 456 | [447, 464] | The vote curve flattens past 9 samples (Wang et al.: 91 at 8, 93 at 16), so about 1-2 more problems than vote over 9. |
| reader-2 | 455 | [447, 462] | Small further gain over vote of 9 as the vote saturates below pass@k (~470). |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 458 | [450, 466] | Same sharpening part as t03: the vote recovers the base's 1-2-of-k problems with diminishing returns, so 12 samples add about 2 over the theory's 456 for 9 (pass@4 467 is the ceiling scale). |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | 455 | [447, 463] | Same mechanism as t03: votes keep recovering errors that depend on the path, with shrinking returns, while wrong plans that depend on the problem stay. So vote-12 sits about 2 above vote-9, consistent with Wang's majority@8-16 curve (91-93 %) and the base's 446 at vote-4. |
| r7-m08 | 455 | [447, 462] | Same no_intervention clause: base-side selection only gets back problems where the base already has a right path, so the vote flattens out; 12 samples add about 2 more than 9, still below pass@4 467. |
| r7-m11 | 452 | [445, 459] | Same mechanism: under the fixed cue the vote plateaus near the base's 446-450 at k=4 because agreeing wrong groups keep outvoting the right answer, so going from 9 to 12 samples adds at most about 1 problem. |

## t05 (work-ceccc0): How many of the 328 harder problems the untrained Olmo 3 base with the opening cue answers right with the token cap raised to 32,768, one sample at T 1.0, grader v3.

Unit: right answers of 328. Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "opening cue", "set": "hard328", "n": 328, "sampling": "T 1.0, top-p not stated, token cap 32,768, seed 3000000", "samples": 1, "grader": "v3"}

> Base cue cell was lost with its vast.ai box during the restart; rerunning as 4 shards on AWS L40S.

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 167 | [155, 180] | Base cue at 16k is 155-168 on this seed; its 77 cap hits are mostly failures to solve (forced commit right on 0-2, long answers right about 8 %), so the cap gives only a few more problems, unlike Think-SFT's +23. |
| reader-2 | 167 | [154, 180] | Base cue single samples at 16k are 158-164 with ~77 cap hits; extra tokens recover a few (restart gave +3.4 pts, RL +2, base cap hits are mostly unsolved). |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 169 | [156, 182] | The theory says the cued base's cap hits are just the hard, long end of the one difficulty axis, so a longer cap lets it finish them only at its own low rate for that difficulty (about +8 problems on ~70 cap hits, base long answers right ~15%), added to the board's 16k single-sample base of 155-164 (mean ~161) at seed 3000000. |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |

## t06 (work-ceccc0): For the untrained Olmo 3 base with the cue on the 328 harder problems (one sample, T 1.0, grader v3), how many points the score at a 32,768-token cap exceeds the score of the same answers counted at 16,384 tokens.

Unit: points (score at cap 32,768 minus score at 16,384, same run). Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "opening cue", "set": "hard328", "n": 328, "sampling": "T 1.0, top-p not stated, cap 32,768 vs the same answers counted at 16,384, seed 3000000", "samples": 1, "grader": "v3"}

> each new cell also gives its own score at 16,384 (right with <= 16,384 tokens), so the comparison is inside one run

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 5 | [1, 11] | About 77 base cap hits; maybe half finish in the extra tokens at a low right rate (tokens 8k-16k bought 12 problems); RL gained 2 and Think-SFT 23. |
| reader-2 | 6 | [1, 12] | About 75 cap-hit answers can continue; base long answers are right ~15 % of the time and many keep rambling, so a handful flip right. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 2.5 | [0.6, 5.5] | Cap hits are the hard end of the difficulty axis rather than an unfinished-but-right policy gap, so the extra 16k tokens convert only ~8 of ~70 base cap hits at its matched-difficulty solve rate: about 2.5 percentage points (between RL's +0.6 and Think-SFT's +7.0 in result-c8b994). |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |

## t07 (work-8b4030): Mean number right per sample (over 4 samples) of the 136 post-cutoff fresh2026 problems for the weight-edited model Think-SFT + 2 x (RL-Math minus base).

Unit: mean right answers per sample of 136. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> on fresh2026 (136 problems, 4 samples, seeds of SPEC_fresh)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 50 | [36, 65] | The a=2 transplant was about 10 % above Think-SFT on hard328 (with selection on that set), applied to my estimate of about 46 for Think-SFT cue on fresh2026. |
| reader-2 | 58 | [42, 73] | No fresh2026 base rate posted; post-cutoff AIME/HMMT assumed ~40 % for Think-SFT and the a=2 transplant adds ~3 points as on hard328 (232 vs 209). |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |

## t08 (work-8b4030): How many of the 328 harder problems Think-SFT + 2 x (RL-Math minus base) gets right by majority vote over 4 samples (two new samples added to the two posted seeds, 234 and 229).

Unit: right answers of 328. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated", "samples": 4, "grader": "not stated, majority vote over 4"}

> hard328 samples 3-4 for the vote over 4

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 247 | [237, 257] | Single samples 234 and 229; with fewer cap hits than Think-SFT (54 vs 94) the vote gain should sit between RL's +21 and Think-SFT's +32. |
| reader-2 | 248 | [238, 258] | Samples 234 and 229; with fewer cap hits than Think-SFT its vote gain looks more like RL's (+21) than Think-SFT's (+32), above Think-SFT's 241 vote. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |

## t09 (work-8b4030): How many of the 500 MATH-500 problems Think-SFT + 2 x (RL-Math minus base) answers right in one sample.

Unit: right answers of 500. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "MATH-500", "n": 500, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> MATH-500 1 sample

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 465 | [455, 474] | Think-SFT single 454-462 and a=1 transplant 467 on MATH-500; a=2 should be near those. |
| reader-2 | 466 | [456, 474] | a=1 scored 467 on MATH-500; Think-SFT single 457-462, RL 456-463; a=2 roughly flat with small degradation risk. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |

## t10 (work-ab0f72): Mean number right per sample (over 4 samples) of the 328 harder problems for the base plus the 8 top RL-Math directions per matrix at 1.5x, with the cue at T 1.0, grader v3.

Unit: mean right answers per sample of 328. Cell: {"model": "Olmo-3-1025-7B base + top 8 singular directions per matrix of (RL-Math - base) at 1.5x", "prompt": "opening cue", "set": "hard328", "n": 328, "sampling": "T 1.0, top-p not stated, token cap not stated", "samples": 4, "grader": "v3"}

> hard328 with 4 samples (single-sample mean, vote over 4 vs base 192, RL 221)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 197 | [188, 206] | Sizes 1 and 2 gave 192 and 190, and 203 at 1.5 was picked from seven sizes, so I expect regression toward about 197. |
| reader-2 | 197 | [188, 206] | The single 203 was the best of seven sizes (1x 192, 2x 190), so expect regression toward ~197 over four samples. |
| r5-m03-rival | 195 | [186, 204] | Theory: the top-8 edit puts the base on a weak dose of RL's own policy (longer, checked answers, errors only on hard problems); with the cue removing the plain-base register and 1.5x strengthening the dose, the per-sample mean sits just under RL's 200 single-sample mean, shrunk from the selected 203 seed toward the 192 at 1x. |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |

## t11 (work-ab0f72): How many of the 328 harder problems the base plus the 8 top RL-Math directions per matrix at 1.5x gets right by majority vote over 4 samples, cue, T 1.0, grader v3.

Unit: right answers of 328. Cell: {"model": "Olmo-3-1025-7B base + top 8 singular directions per matrix of (RL-Math - base) at 1.5x", "prompt": "opening cue", "set": "hard328", "n": 328, "sampling": "T 1.0, top-p not stated, token cap not stated", "samples": 4, "grader": "v3, majority vote over 4"}

> hard328 with 4 samples (single-sample mean, vote over 4 vs base 192, RL 221)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 219 | [207, 230] | Single mean about 197 plus a vote gain of about 22 (base +33, RL +21; the edit has RL-like cap hits). |
| reader-2 | 220 | [208, 230] | Single mean ~197 plus an RL-like vote gain of ~+22 since cap hits are low (25). |
| r5-m03-rival | 216 | [206, 226] | Same weak-RL-dose reading: answers behave like RL's (few cap hits, 25 at 1.5x), so the vote adds about RL's +21 over its single mean rather than the base's +31, giving ~195+21, below RL's vote of 221. |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |

## t12 (work-ab0f72): How many of the 500 MATH-500 problems the base plus the 8 top RL-Math directions per matrix at 1.5x answers right in one sample with the cue at T 1.0, grader v3.

Unit: right answers of 500. Cell: {"model": "Olmo-3-1025-7B base + top 8 singular directions per matrix of (RL-Math - base) at 1.5x", "prompt": "opening cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0, top-p not stated, token cap not stated", "samples": 1, "grader": "v3"}

> MATH-500 one sample (base cue 410, RL 457)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 440 | [427, 453] | Top-8 at 1x plain scored 427; adding the cue and the 1.5x size moves it toward the theta blends' 441-457 cue cells, with RL cue at 457. |
| reader-2 | 445 | [433, 456] | Between base cue 410 and RL cue 457; hard328 effect sits near theta0.5 (452 on MATH-500) and top8 plain 1x gave 427. |
| r5-m03-rival | 455 | [445, 465] | Theory's mixture on top8 plain 427 = ~12.5% plain-base answers at ~50% right plus ~87.5% RL-like answers at ~90.5% right; the cue turns all answers RL-like (~453), and the stronger 1.5x dose adds a little, near RL cue 457 and theta-1.5 cue 453. |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |

## t13 (work-ce7583): How many of the 400 held-out MATH-500 problems the final configuration found by one headless autobench agent over 40 experiments on dev100 gets right with the untrained Olmo 3 base.

Unit: right answers of 400. Cell: {"model": "Olmo 3 base (untrained), configuration chosen by the autobench agent", "prompt": "chosen by the agent (started from the plain prompt)", "set": "math400 (MATH-500 minus the 100 dev problems)", "n": 400, "sampling": "chosen by the agent, not stated", "samples": "not stated", "grader": "not stated"}

> then finals on math400 and hard328 against the swarm cue config

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 350 | [325, 368] | The agent's dev best was 86/100 with a 10-sample vote (swarm cue 84 on dev); a 10-sample cued vote would score about 89-91 % on the full set, minus some dev overfitting and the time-budget token limit. |
| reader-2 | 340 | [318, 360] | Agent best 86/100 on dev100 midway (cue config scores 84 there, 81.5 % on the other 400); expect ~85 % held out after dev overfitting. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |

## t14 (work-ce7583): How many of the 328 harder problems the final configuration found by one headless autobench agent over 40 experiments on dev100 gets right with the untrained Olmo 3 base.

Unit: right answers of 328. Cell: {"model": "Olmo 3 base (untrained), configuration chosen by the autobench agent", "prompt": "chosen by the agent (started from the plain prompt)", "set": "hard328", "n": 328, "sampling": "chosen by the agent, not stated", "samples": "not stated", "grader": "not stated"}

> then finals on math400 and hard328 against the swarm cue config

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 190 | [162, 210] | Base cue vote over 4 on hard328 is 192 (single 158-164); a dev-chosen vote config under a token budget probably lands near that, with wide doubt about the agent's prompt and cap. |
| reader-2 | 170 | [140, 200] | Swarm cue single ~160, vote 192; a short-answer vote config tuned on MATH dev likely transfers partially to hard problems. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |

## t15 (work-7c069c): Mean number right per sample (over 4 samples) of the 136 post-cutoff fresh2026 problems for Think-SFT with the opening cue, grader v3.

Unit: mean right answers per sample of 136. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "opening cue", "set": "fresh2026_v1 (AIME 2026, HMMT Feb + Nov 2026)", "n": 136, "sampling": "not stated", "samples": 4, "grader": "v3"}

> then Think-SFT cue / RL plain / base cue, 4 samples, vote.

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 46 | [33, 60] | Think-SFT is slightly above RL on the hard328 single sample and leads on hard, long problems; I estimate about 50 % on AIME 2026, about 28 % on HMMT Feb and about 50 % on HMMT Nov under the 16k cap. |
| reader-2 | 54 | [39, 69] | No fresh-set rate posted; Think-SFT about 1.4x the cued base on hard problems, assumed ~40 % on post-cutoff AIME/HMMT at a 16k cap. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |

## t16 (work-7c069c): How many of the 136 post-cutoff fresh2026 problems Think-SFT with the opening cue gets right by majority vote over 4 samples, grader v3.

Unit: right answers of 136. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "opening cue", "set": "fresh2026_v1 (AIME 2026, HMMT Feb + Nov 2026)", "n": 136, "sampling": "not stated", "samples": 4, "grader": "v3, majority vote over 4"}

> then Think-SFT cue / RL plain / base cue, 4 samples, vote.

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 52 | [38, 66] | Think-SFT's vote is near pass@4 because it abstains by hitting the cap (hard328 single 209 to vote 241); scaled to the lower fresh accuracy, that is about +6. |
| reader-2 | 64 | [48, 80] | Think-SFT's vote gains a lot because it abstains via cap hits (hard328 +10 pts); a smaller gain is assumed on the harder fresh set. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |

## t17 (work-7c069c): Mean number right per sample (over 4 samples) of the 136 post-cutoff fresh2026 problems for Olmo-3.1 RL-Zero-Math with the plain prompt, grader v3.

Unit: mean right answers per sample of 136. Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math", "prompt": "plain", "set": "fresh2026_v1 (AIME 2026, HMMT Feb + Nov 2026)", "n": 136, "sampling": "not stated", "samples": 4, "grader": "v3"}

> then Think-SFT cue / RL plain / base cue, 4 samples, vote.

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 39 | [28, 51] | RL beats the cued base by 12 points on AIME-like problems (Wang AIME24 35 vs 23); I estimate about 35 % on AIME, 18 % on HMMT Feb and 40 % on HMMT Nov. |
| reader-2 | 47 | [33, 61] | RL ~1.3x the cued base on hard sets (AIME24 35 vs 23 in Wang); assumed ~35 % on fresh2026. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |

## t18 (work-7c069c): How many of the 136 post-cutoff fresh2026 problems Olmo-3.1 RL-Zero-Math with the plain prompt gets right by majority vote over 4 samples, grader v3.

Unit: right answers of 136. Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math", "prompt": "plain", "set": "fresh2026_v1 (AIME 2026, HMMT Feb + Nov 2026)", "n": 136, "sampling": "not stated", "samples": 4, "grader": "v3, majority vote over 4"}

> then Think-SFT cue / RL plain / base cue, 4 samples, vote.

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 43 | [31, 55] | RL's vote gain is modest (hard328 +21 of 328, about 6 points); scaled to fresh2026 that is about +4. |
| reader-2 | 54 | [39, 69] | RL's vote gain on hard328 was +6 pts per 100; about +7 problems assumed here. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |

## t19 (work-7c069c): Mean number right per sample (over 4 samples) of the 136 post-cutoff fresh2026 problems for the untrained Olmo 3 base with the opening cue, grader v3.

Unit: mean right answers per sample of 136. Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "opening cue", "set": "fresh2026_v1 (AIME 2026, HMMT Feb + Nov 2026)", "n": 136, "sampling": "not stated", "samples": 4, "grader": "v3"}

> then Think-SFT cue / RL plain / base cue, 4 samples, vote.

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 27 | [18, 37] | The base cue smoke got 3 of 10 AIME 2026; I estimate about 22 % on AIME, 11 % on HMMT Feb and 30 % on HMMT Nov. |
| reader-2 | 34 | [22, 47] | Smoke run gave 3/10 on AIME 2026; HMMT Feb is harder and Nov easier, so ~25 % overall. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |

## t20 (work-7c069c): How many of the 136 post-cutoff fresh2026 problems the untrained Olmo 3 base with the opening cue gets right by majority vote over 4 samples, grader v3.

Unit: right answers of 136. Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "opening cue", "set": "fresh2026_v1 (AIME 2026, HMMT Feb + Nov 2026)", "n": 136, "sampling": "not stated", "samples": 4, "grader": "v3, majority vote over 4"}

> then Think-SFT cue / RL plain / base cue, 4 samples, vote.

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 32 | [21, 43] | The base gains the most from voting (hard328 +33, MATH-500 +36-41), so I add about 5 at this accuracy. |
| reader-2 | 40 | [26, 54] | Vote helps less at low per-sample accuracy; about +6 over the single-sample mean. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
