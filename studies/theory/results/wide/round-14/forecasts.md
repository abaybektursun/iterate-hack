# Forecasts, round-14

Board snapshot 2026-11-15T22:32:36 UTC, written 2026-11-15T22:53:29 UTC. 19 targets; forecasters reader-1, reader-2, round-09/training-m01, round-09/stopping-m04, run-08/f2-m05, round-14/s3-b.


- round-09/training-m01 (training, carried): Think-SFT imitated teacher traces inside its ChatML template, opened by <think> and closed by a final answer after the thinking block. Where and how it states the answer is learned conditional on that template. On the raw template with the cue it reasons as well but sometimes misplaces the final answer (on the line after 'Answer:'), which v3 misses. Its own template restores the trained ending: more MATH-500 answers counted, unchanged reasoning length and cap behaviour on hard328.

- round-09/stopping-m04 (stopping, carried): On a hard set part of every model's answers would end past 16,384 tokens, and a cut answer scores zero. A change that leaves the length distribution in place (100 RL steps, the cue on a checkpoint, a new seed or more samples) can move only the precision of finished answers. Step 100 writes cued-base lengths at T 1.0 (4,120 vs 4,008 tokens), so on hard problems it keeps the cued base's cap hits and adds a few right answers.

- run-08/f2-m05 (grader, carried): Majority vote counts answer strings: the base's wrong answers scatter (only about a quarter repeat), so the right answer is the plurality once per-sample success exceeds about 0.3, and even k leaves ties that a fixed rule breaks about half right. Vote over k therefore rises toward the number of problems whose right answer is the modal string, well below pass@k, with odd k gaining from fewer ties and returns shrinking fast after k = 4.

- round-14/s3-b (s3): At T 0.6 the plain base's long hard328 attempts fall into repetition loops that never end at any cap. Only short attempts finish, so the 12-vote counts short answers alone, and problems needing a long derivation are lost to the temperature regime, not to the 4,096 cap. The vote lifts a weak T 0.6 single sample (107/328) by about 30. A larger cap would recover almost nothing; T 1.0 would.

## t01 (work-3d4e90): How many of the 328 hard problems Think-SFT gets right with its own chat format at its released setting (T 0.6, top-p 0.95, cap 32,768), one sample, grader v3.

Unit: right answers of 328. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "own chat format", "set": "hard328", "n": 328, "sampling": "T 0.6 / top-p 0.95, cap 32,768 (released generation_config.json), seed paired with the T 1.0 native cell", "samples": 1, "grader": "v3"}

> Think-SFT at its released sampling setting (generation_config.json: T 0.6 / top-p 0.95, own chat format, cap 32,768), never run here: hard328 and MATH-500, v3, 1 sample

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 230 | [215, 244] | Think-SFT in its own format at cap 32,768 scored 232 at T 1.0 (result-dd9239), and its cue samples at 32,768 average 232.8; T 0.6 / top-p 0.95 should be about the same for a distilled reasoner, with a small risk of more loops. |
| reader-2 | 230 | [213, 245] | Paired T 1.0 own-format cell at cap 32,768 scored 232/328 (result-dd9239); the released T 0.6 setting should land close, with some risk of more loops. |
| round-09/training-m01 | 234 | [218, 249] | The theory says Think-SFT's own template brings back its trained ending and leaves reasoning length and cap behaviour on hard328 unchanged, so I anchor on the own-format T 1.0 cell at cap 32,768 (232/328, result-dd9239); the theory says nothing about temperature, so the T 0.6 change only widens the interval. |
| round-09/stopping-m04 | 229 | [215, 242] | Theory: a cut answer scores zero, and at cap 32,768 Think-SFT's own format almost always finishes (232 at T 1.0, paired seed). The theory's T 0.6 clause says loops that depend on the opening add cap hits, which offsets the precision gain from the lower temperature, so the count stays near 232 and slightly below it. |
| run-08/f2-m05 | - |  | theory says nothing |
| round-14/s3-b | 212 | [194, 229] | T 0.6 makes part of Think-SFT's long traces loop to the cap; the 32k cap recovers little, so it lands below the cue's 230 at 32k and T 1.0. |

## t02 (work-3d4e90): How many of the 500 MATH-500 problems Think-SFT gets right with its own chat format at its released setting (T 0.6, top-p 0.95, cap 32,768), one sample, grader v3.

Unit: right answers of 500. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "own chat format", "set": "MATH-500", "n": 500, "sampling": "T 0.6 / top-p 0.95, cap 32,768 (released generation_config.json), seed paired with the T 1.0 native cell", "samples": 1, "grader": "v3"}

> Think-SFT at its released sampling setting (generation_config.json: T 0.6 / top-p 0.95, own chat format, cap 32,768), never run here: hard328 and MATH-500, v3, 1 sample

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 472 | [463, 480] | Own format at cap 32,768 scored 474 on MATH-500 at T 1.0 (result-0a0a5a); I expect T 0.6 to land within a few problems of that. |
| reader-2 | 472 | [462, 481] | Own-format T 1.0 cap-32,768 cell scored 474/500 (result-0a0a5a); cue samples at 16k were 457-462, and T 0.6 is the model's released setting. |
| round-09/training-m01 | 474 | [463, 484] | The theory says the own template gets more MATH-500 answers counted, so I anchor on the own-format cell at cap 32,768 (474/500, result-0a0a5a, above the 457-462 cue samples); T 0.6 is not covered by the theory, so the interval is wider. |
| round-09/stopping-m04 | 473 | [464, 481] | Same clauses: at cap 32,768 on MATH-500 there are almost no cut answers (474 with 0 cap hits at T 1.0). At T 0.6 a few looped cap hits trade against finished-answer precision, so the count stays near 474. |
| run-08/f2-m05 | - |  | theory says nothing |
| round-14/s3-b | 452 | [439, 465] | MATH-500 routes are mostly short, so few loops matter: near the 454 of T 1.0 at 16k, slightly lower. |

## t03 (work-08efcc): How far the base edit with RL-Math's 8 input directions and random output directions at 1.5x moves the layer-24 residual stream on stored base answers, teacher-forced, compared with the full and random 1.5x edits.

Unit: residual-stream shift at layer 24. Cell: {"model": "Olmo-3-1025-7B base + RL-Math input directions with random output directions, 1.5x", "prompt": "not stated", "set": "stored base answers, teacher-forced", "n": "not stated", "sampling": "none (teacher-forced, no generation)", "samples": "not stated", "grader": "none (residual-stream shift at layer 24)"}

> Residual-stream shift of the three partial edits (RL inputs only, RL outputs only, pairs shifted)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 1.5 | [0.3, 5] | The full 1.5x edit shifts layer 24 by about 9.3 and a random edit by about 0.1 (result-98de28). RL input directions are driven about 10x more than random ones, but random outputs should not compound across layers, so I put this near ten times the random shift. |
| reader-2 | 1.5 | [0.4, 5] | RL inputs read the base strongly (drive 8-11x random), so each layer writes as much as the full edit, but random outputs should lose the cross-layer compounding behind the full 1.5x edit's 9.3 (random 1.5x about 0.1). |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| run-08/f2-m05 | - |  | theory says nothing |
| round-14/s3-b | - |  | no forecast |

## t04 (work-08efcc): How far the base edit with RL-Math's 8 output directions and random input directions at 1.5x moves the layer-24 residual stream on stored base answers, teacher-forced, compared with the full and random 1.5x edits.

Unit: residual-stream shift at layer 24. Cell: {"model": "Olmo-3-1025-7B base + RL-Math output directions with random input directions, 1.5x", "prompt": "not stated", "set": "stored base answers, teacher-forced", "n": "not stated", "sampling": "none (teacher-forced, no generation)", "samples": "not stated", "grader": "none (residual-stream shift at layer 24)"}

> Residual-stream shift of the three partial edits (RL inputs only, RL outputs only, pairs shifted)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 0.2 | [0.06, 0.8] | With random input directions the base barely drives the edit, so the injected change is near the random edit's (about 0.1 at 1.5x) even though the outputs are RL's directions. |
| reader-2 | 0.15 | [0.06, 0.8] | Random input directions read the base about as weakly as the random edit (0.066 at 1x, about 0.1 at 1.5x), so the shift should stay near random. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| run-08/f2-m05 | - |  | theory says nothing |
| round-14/s3-b | - |  | no forecast |

## t05 (work-08efcc): How far the base edit with RL-Math's 8 directions but input-output pairs shifted by one at 1.5x moves the layer-24 residual stream on stored base answers, teacher-forced, compared with the full and random 1.5x edits.

Unit: residual-stream shift at layer 24. Cell: {"model": "Olmo-3-1025-7B base + RL-Math 8 directions with input-output pairs shifted by one, 1.5x", "prompt": "not stated", "set": "stored base answers, teacher-forced", "n": "not stated", "sampling": "none (teacher-forced, no generation)", "samples": "not stated", "grader": "none (residual-stream shift at layer 24)"}

> Residual-stream shift of the three partial edits (RL inputs only, RL outputs only, pairs shifted)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 5 | [1, 11] | RL inputs give full drive, and the RL output subspace still lines up with the next layer's inputs, so a large share of the full edit's 9.3 shift is plausible even though the behaviour matched random (160/64). |
| reader-2 | 6.5 | [2.5, 10.5] | Shifting the pairs keeps both subspaces and the per-layer write norm (singular values times input reads), so the shift should approach the full 1.5x edit's 9.3 even though the score matched random. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| run-08/f2-m05 | - |  | theory says nothing |
| round-14/s3-b | - |  | no forecast |

## t06 (work-989736): How many of the 328 hard problems the released Olmo-3-7B-Think plus twice the RL-Zero-Math weight change gets right with the cue at T 1.0, cap 16,384, one sample.

Unit: right answers of 328. Cell: {"model": "Olmo-3-7B-Think + 2 x (RL-Math - base)", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "T 1.0, top-p not stated, cap 16,384, seed 3,000,000", "samples": 1, "grader": "not stated"}

> Olmo-3-7B-Think (released final Think model: SFT, DPO, then RLVR) + 2 x (RL-Math - base) on hard328, cue, T 1.0, cap 16,384

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 222 | [200, 240] | Adding 2x the RL delta lifted Think-SFT by about 7 points through fewer cap hits (result-3387ce, c5dafe); on an RLVR-trained host I expect a smaller gain over a host near 212. |
| reader-2 | 225 | [205, 243] | On Think-SFT, 2x the RL delta added about 22 (209 to 232) by cutting cap hits; on the already RL-trained Think host I expect a smaller gain on top of about 214. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| run-08/f2-m05 | - |  | theory says nothing |
| round-14/s3-b | - |  | no forecast |

## t07 (work-989736): How many of the 328 hard problems the released Olmo-3-7B-Think model alone gets right with the cue at T 1.0, cap 16,384, one sample.

Unit: right answers of 328. Cell: {"model": "Olmo-3-7B-Think (released final Think model)", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "T 1.0, top-p not stated, cap 16,384, seed 3,000,000", "samples": 1, "grader": "not stated"}

> against that host alone (never run here), 1 sample each, seed 3,000,000

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 212 | [190, 232] | Think-SFT with the cue scores about 209 at cap 16,384; the final Think model is somewhat stronger on AIME but writes long answers, so cap hits at 16,384 should hold it near the SFT level. |
| reader-2 | 214 | [192, 235] | Think-SFT with the cue scores 209 mean at cap 16k; the final Think model has slightly better AIME on its model card but similar cap-hit exposure at 16,384. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| run-08/f2-m05 | - |  | theory says nothing |
| round-14/s3-b | - |  | no forecast |

## t08 (work-989736): On the 328 hard problems with the cue at T 1.0, cap 16,384, one sample each, how many points Olmo-3-7B-Think plus twice the RL-Zero-Math weight change scores above Olmo-3-7B-Think alone.

Unit: points (difference in right answers of 328, as a percentage). Cell: {"model": "Olmo-3-7B-Think + 2 x (RL-Math - base) minus Olmo-3-7B-Think alone", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "T 1.0, top-p not stated, cap 16,384, seed 3,000,000", "samples": 1, "grader": "not stated"}

> Does a host already trained with reward still gain from the RL-Zero delta

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 3 | [-4, 10] | The delta gave +7.4 points on Think-SFT; a host that already had RL should gain less, and the result could be zero or negative. |
| reader-2 | 3.5 | [-2.5, 9.5] | Difference of t06 and t07 on paired seeds: a smaller effect than Think-SFT's +7.4 points, plus about 2.5 points of single-sample noise. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| run-08/f2-m05 | - |  | theory says nothing |
| round-14/s3-b | - |  | no forecast |

## t09 (work-3b97a7): How many of 538 HumanEval+ and MBPP+ problems Think-SFT with the Code cue passes when its stored answers are regraded with an extraction rule that also accepts an unopened code block.

Unit: passed of 538. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0 / top-p 1.0 (stored answers of work-8ea654, no new generation)", "samples": 1, "grader": "code tests with the second extraction rule accepting an unopened code block"}

> Regrade the Code pair with a second extraction rule that also accepts Think-SFT's unopened code block

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 362 | [344, 378] | 301 passed plus most of the 97 unopened-block programs, assuming they pass at about the 70% rate of Think-SFT's fenced answers (result-9d38d9). |
| reader-2 | 365 | [347, 381] | 301 passed plus about 70% of the 97 unopened-but-complete programs (the pass rate among its fenced answers was 301/432). |
| round-09/training-m01 | 366 | [345, 385] | The theory says that off its trained template Think-SFT 'reasons as well but misplaces the final answer', so the 97 programs with no opening fence (result-9d38d9) should pass at about the fenced rate of 301/432 (70 %): 301 + about 65. |
| round-09/stopping-m04 | - |  | theory says nothing |
| run-08/f2-m05 | - |  | theory says nothing |
| round-14/s3-b | - |  | no forecast |

## t10 (work-3b97a7): How many of 538 HumanEval+ and MBPP+ problems Think-SFT with the Math cue passes when its stored answers are regraded with an extraction rule that also accepts an unopened code block.

Unit: passed of 538. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "Math cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0 / top-p 1.0 (stored answers of work-8ea654, no new generation)", "samples": 1, "grader": "code tests with the second extraction rule accepting an unopened code block"}

> Regrade the Code pair with a second extraction rule that also accepts Think-SFT's unopened code block

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 328 | [298, 355] | 270 passed under the Math cue; it likely has as many or more unopened blocks, so I add about 50-60 passes at a rate near 65%. |
| reader-2 | 345 | [315, 375] | The Math cue had more unscored answers (270 passed); accepting the unopened block should recover a similar or larger share, moving it toward the Code-cue regrade. |
| round-09/training-m01 | 335 | [300, 370] | Same misplacement account: the Math cue's 31-problem deficit against the Code cue (270 vs 301) should be mostly format, recovered at about the 70 % fenced pass rate; the count of unfenced answers is not posted, so the interval is wide. |
| round-09/stopping-m04 | - |  | theory says nothing |
| run-08/f2-m05 | - |  | theory says nothing |
| round-14/s3-b | - |  | no forecast |

## t11 (work-3b97a7): How many of 538 HumanEval+ and MBPP+ problems the untrained base with the Code cue passes when its stored answers are regraded with an extraction rule that also accepts an unopened code block.

Unit: passed of 538. Cell: {"model": "Olmo-3-1025-7B base", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0 / top-p 1.0 (stored answers, no new generation)", "samples": 1, "grader": "code tests with the second extraction rule accepting an unopened code block"}

> Regrade the Code pair with a second extraction rule that also accepts Think-SFT's unopened code block

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 318 | [316, 323] | The base rarely writes the unopened-block format (34 answers have no block, mostly cap hits or other failures), so 317 should barely move. |
| reader-2 | 319 | [316, 326] | The base fenced 504 of 538 and rarely writes the unopened form, so only a few of its 34 no-block answers should be recovered from 317. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| run-08/f2-m05 | - |  | theory says nothing |
| round-14/s3-b | - |  | no forecast |

## t12 (work-3b97a7): How many of 538 HumanEval+ and MBPP+ problems RL-Zero-Code passes when its stored answers are regraded with an extraction rule that also accepts an unopened code block.

Unit: passed of 538. Cell: {"model": "Olmo-3.1-7B-RL-Zero-Code", "prompt": "plain", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0 / top-p 1.0 (stored answers, no new generation)", "samples": 1, "grader": "code tests with the second extraction rule accepting an unopened code block"}

> Regrade the Code pair with a second extraction rule that also accepts Think-SFT's unopened code block

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 401 | [399, 404] | RL-Code has only 8 answers without a code block, so the regrade should leave 401 nearly unchanged. |
| reader-2 | 401 | [400, 404] | RL-Code fenced 530 of 538 (8 no-block, 8 cap hits), so the regrade barely moves 401. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| run-08/f2-m05 | - |  | theory says nothing |
| round-14/s3-b | - |  | no forecast |

## t13 (work-b7857c): How many of the 328 hard problems the base plus RL-Math's first direction per matrix at 1.5x gets right with the plain prompt (no cue), T 1.0, one sample.

Unit: right answers of 328. Cell: {"model": "Olmo-3-1025-7B base + direction 1 per matrix of (RL-Math 3.1 - base) at 1.5x", "prompt": "plain (no cue)", "set": "hard328", "n": 328, "sampling": "T 1.0, cap 16,384, same seed as the plain base cell", "samples": 1, "grader": "v3"}

> direction 1 and directions 2-8 at 1.5 WITHOUT the cue (plain)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 105 | [72, 150] | The plain base scores 76 on hard328. Direction 1 mostly helps finishing and writes the cue only weakly (screen: top1 plain 42 vs base 34 of 100), so I expect a partial lift. |
| reader-2 | 105 | [78, 145] | Plain base scores 76 on hard328; direction 1 alone wrote little of the cue on the plain screen (42 vs 34 of 100 MATH-500), but it cuts cap hits, so modestly above plain. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| run-08/f2-m05 | - |  | theory says nothing |
| round-14/s3-b | - |  | no forecast |

## t14 (work-b7857c): How many of the 328 hard problems the base plus RL-Math's directions 2 to 8 per matrix at 1.5x gets right with the plain prompt (no cue), T 1.0, one sample.

Unit: right answers of 328. Cell: {"model": "Olmo-3-1025-7B base + directions 2-8 per matrix of (RL-Math 3.1 - base) at 1.5x", "prompt": "plain (no cue)", "set": "hard328", "n": 328, "sampling": "T 1.0, cap 16,384, same seed as the plain base cell", "samples": 1, "grader": "v3"}

> direction 1 and directions 2-8 at 1.5 WITHOUT the cue (plain)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 160 | [115, 192] | The top-8 directions write the cue on their own (top-8 1x plain gave 427 on MATH-500), and directions 2-8 at 1.5x with the cue score 183-196, so the plain version should end up somewhat below that. |
| reader-2 | 160 | [115, 192] | With the cue, directions 2-8 scored 183-196; the 8 directions write the cue themselves (plain top-8 427 vs cue 410 on MATH-500), so most of that should carry over without the cue. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| run-08/f2-m05 | - |  | theory says nothing |
| round-14/s3-b | - |  | no forecast |

## t15 (work-f33794): How many of the 328 hard problems the untrained base with the cue gets right by plurality vote over 6 samples per problem (compared with RL's one sample at 200-206).

Unit: right answers of 328. Cell: {"model": "Olmo-3-1025-7B base", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "not stated", "samples": 6, "grader": "not stated"}

> cued base, 2 new samples per problem first (vote over 6)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 196 | [183, 208] | The base vote over 4 on hard328 is 192 (179 on other rows), and pass@4 is about 207; on MATH-500 going from 4 to 6 votes added about 7, so I expect +3 to +6 here. |
| reader-2 | 197 | [189, 206] | Cued-base vote over 4 on hard328 is 192; on MATH-500 going from 4 to 6 samples added about 7 of 500, so a few more problems here. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | 197 | [190, 205] | Theory: more samples leave the length distribution in place, so they only sharpen the precision of finished answers, and the cued base's cap-hit problems stay at zero. The count therefore rises a little above the vote over 4 (192, or 195 after restart) and stays capped well below pass@4 (207). |
| run-08/f2-m05 | 198 | [190, 206] | Theory: scattered wrong answers let the right answer win the plurality once p > ~0.3, so going from vote over 4 (192 of 328) to 6 still gains, but the gain shrinks after k = 4 and even k still leaves ties. I scaled the MATH-500 step from k = 4 to 6 (+7.4 of 500) up for hard328's larger mid-p share; the result stays well below pass@4 (205-207). |
| round-14/s3-b | 184 | [175, 194] | T 1.0 has no loops, so the board's reading holds: vote@4 179 plus about 5 for 2 more samples. |

## t16 (work-ccac62): How many of the 328 hard problems RL-Zero-Math gets right by a vote over its 4 stored samples (cap 16,384) when ties go to the shortest answer.

Unit: right answers of 328. Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math", "prompt": "plain", "set": "hard328", "n": 328, "sampling": "stored draws, cap 16,384", "samples": 4, "grader": "not stated; vote with ties to the shortest answer"}

> Tie-to-shortest replication on stored 16,384 draws (Think-SFT + cue, RL, cued base; hard328, fresh2026, MATH-500)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 223 | [218, 228] | RL's vote over 4 is 221. Its short answers are more accurate than its long ones, so breaking ties toward the shortest answer should add a couple of problems. |
| reader-2 | 221 | [215, 227] | RL's plain vote over 4 on hard328 is 221; tie rules moved votes by 0-3 elsewhere (base 191 vs 192, RL MATH-500 475 vs 474). |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | 221 | [216, 226] | Theory: a tie rule changes neither the length distribution nor the cap hits, and cut answers already cast no vote. Ties-to-shortest only reselects among finished answers, so the count should equal RL's plain vote of 221 (the base's tie-short moved its vote by 1). |
| run-08/f2-m05 | 222 | [216, 228] | Theory: a fixed tie rule breaks even-k ties about half right, so tie-to-shortest should land at RL's plain vote over 4 on the 328 (221). The base showed this there (191 vs 192), and RL's long answers being right less often adds about +1. |
| round-14/s3-b | 215 | [206, 224] | T 1.0 RL has no loops; the tie to the shortest finished sample adds about +1 to vote@4 of about 214. |

## t17 (work-ccac62): How many of the 500 MATH-500 problems Think-SFT with the cue gets right by a vote over its 4 stored samples (cap 16,384) when ties go to the shortest answer.

Unit: right answers of 500. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "stored draws, cap 16,384", "samples": 4, "grader": "not stated; vote with ties to the shortest answer"}

> Tie-to-shortest replication on stored 16,384 draws (Think-SFT + cue, RL, cued base; hard328, fresh2026, MATH-500)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 482 | [478, 486] | Think-SFT's vote over 4 on MATH-500 is 481; the tie rule should move it by only 0-2 problems. |
| reader-2 | 481 | [476, 485] | Think-SFT cue vote over 4 on MATH-500 is 481; tie-to-shortest should change it by only a few problems. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | 481 | [477, 485] | Theory: a tie rule moves only precision among finished answers, so the count should equal Think-SFT's plain MATH-500 vote of 481. |
| run-08/f2-m05 | 481 | [477, 485] | Theory: a fixed tie rule is about half right on ties, so the count stays near Think-SFT's stored vote over 4 on MATH-500 (481). Its many cap hits cast no vote, which leaves few contested ties. |
| round-14/s3-b | 471 | [463, 478] | T 1.0, no loop regime; vote over 4 of about 471 plus 0-1 from the tie rule. |

## t18 (work-ccac62): How many of the 136 fresh 2026 contest problems RL-Zero-Math gets right by a vote over its 4 stored samples (cap 16,384) when ties go to the shortest answer.

Unit: right answers of 136. Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math", "prompt": "plain", "set": "fresh2026", "n": 136, "sampling": "stored draws, cap 16,384", "samples": 4, "grader": "not stated; vote with ties to the shortest answer"}

> Tie-to-shortest replication on stored 16,384 draws (Think-SFT + cue, RL, cued base; hard328, fresh2026, MATH-500)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 58 | [54, 62] | RL's vote over 4 on fresh2026 is 57; the shortest-answer tie rule should shift it by about one problem. |
| reader-2 | 57 | [53, 61] | RL's vote over 4 on fresh2026 is 57; a tie rule should move it by a couple of problems. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | 57 | [53, 61] | Theory: a tie rule moves only precision among finished answers and leaves the cap hits in place, so the count should equal RL's fresh2026 vote of 57. |
| run-08/f2-m05 | 58 | [53, 63] | Theory: ties are broken about half right whatever the rule, so the count stays near RL's stored vote over 4 on fresh2026 (57). Its wrong answers scatter, and ties-to-shortest may add about 1. |
| round-14/s3-b | 57 | [52, 62] | T 1.0, no loops; the tie rule leaves RL's vote of 57 unchanged. |

## t19 (work-ccac62): How many of the 136 fresh 2026 contest problems the untrained base with the cue gets right by a vote over its 4 stored samples (cap 16,384) when ties go to the shortest answer.

Unit: right answers of 136. Cell: {"model": "Olmo-3-1025-7B base", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "stored draws, cap 16,384", "samples": 4, "grader": "not stated; vote with ties to the shortest answer"}

> Tie-to-shortest replication on stored 16,384 draws (Think-SFT + cue, RL, cued base; hard328, fresh2026, MATH-500)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 39 | [35, 43] | The cued base's vote over 4 on fresh2026 is 38; the tie rule moved the base by -1 on hard328 and +7 in-sample on MATH-500. |
| reader-2 | 38 | [34, 42] | Cued base vote over 4 on fresh2026 is 38; frequent cap hits create ties, but the shortest-answer rule gave no net gain for the base on hard328. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | 38 | [35, 42] | Theory: the cued base's roughly 40 % cap hits cast no vote under any tie rule, so ties-to-shortest only reselects among finished answers. The count should equal its fresh2026 vote of 38. |
| run-08/f2-m05 | 38 | [34, 42] | Theory: the cued base's per-sample success on fresh2026 (~0.22) is mostly below the ~0.3 threshold, so many problems are split or tied, and a fixed tie rule breaks them about half right. The count stays near the stored vote over 4 (38), as tie_short did on hard328 (191 vs 192). |
| round-14/s3-b | 34 | [28, 40] | T 1.0 cued base, no loops; singles average 29.5, the vote adds about 4, ties to shortest about 0.5. |
