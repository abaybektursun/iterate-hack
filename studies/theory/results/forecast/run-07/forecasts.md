# Forecasts, run-07

Board snapshot 2026-11-15T16:32:52 UTC, written 2026-11-15T16:42:39 UTC. 24 targets; forecasters reader-1, reader-2, r5-m03-rival, r6-account-rival, r6-m06, r7-m05, r7-m08, r7-m11, f2-m01, f2-m02, f2-m03, f2-m04, f2-m05, f2-m06.


Lens of the mechanisms: problem structure: difficulty, domain, answer type, length of the needed derivation


## f2-m01

Each problem needs a derivation of a given length; past the 16,384 cap the answer is cut and scores zero. Extra budget or a finishing weight edit only converts cut answers into finished ones, and a converted answer is right at the rate the model reaches on problems that long and hard: about 25-30 % on hard328, about 45 % on MATH-500's long tail, under 20 % on fresh2026 contest problems. Finished short answers are untouched.

Rests on: result-c8b994, result-0c1eef, result-6f1bb7, result-2fe32f, result-5251c9. Forecasts 12 of 24 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t06 | 50 | [43, 57] | 52 [44, 61] | 53 [45, 61] |  | agree: close to the readers' 52-53, shaded down because fresh2026's converted cut answers are rarely right. |
| t07 | 45 | [40, 50] | 47.5 [42, 53] | 47.5 [42, 53] |  | disagree: readers carry the hard328 match with RL over, but fresh2026 problems need longer derivations, so the cut answers the edit converts are right about 20 % of the time, not hard328's 30 %. |
| t12 | 231 | [217, 245] | 231 [214, 247] | 235 [212, 256] |  | agree: the native template does not change how long the needed derivations are, so it gives the readers' ~230. |
| t13 | 204 | [190, 218] | 205 [186, 222] | 200 [172, 226] |  | agree: the mechanism gives the cue cell's 16k count, as the readers say. |
| t14 | 468 | [460, 476] | 465 [454, 475] | 465 [452, 476] |  | agree: slightly above the readers' 465 because MATH-500's long tail converts at a higher rate than hard328. |
| t15 | 459 | [450, 468] | 460 [448, 470] | 460 [445, 472] |  | agree: same as the readers' 460. |
| t18 | 79 | [74, 84] | 79 [73, 85] | 79 [73, 85] |  | agree: gives the readers' 79. |
| t19 | 71.3 | [69.2, 73.4] | 71.3 [69.3, 73.5] | 71.3 [68.8, 73.8] |  | agree: arithmetic on known samples, as the readers. |
| t20 | 247 | [239, 255] | 247 [237, 257] | 247 [239, 256] |  | agree: gives the readers' 247. |
| t21 | 230.5 | [226.5, 234.5] | 229.5 [225, 234.5] | 231 [227, 235] |  | agree: same arithmetic as the readers. |
| t23 | 246 | [237, 255] | 244 [235, 254] | 247 [237, 257] |  | agree: matches the readers' 244-247. |
| t24 | 81 | [74, 88] | 81 [72, 90] | 80 [72, 88] |  | agree: the readers' 80-81. |

## f2-m02

An RL run's top weight directions write a habit for its own domain's answers. For Math-RL that habit is to deliberate, check, and finish with one boxed answer; for Code-RL it is to reason, then finish with one final python block that passes the tests. In its own domain the top-8 edit carries about two thirds of RL's gain at 1x and nearly all of it at 1.5x. On another domain it carries about half as much.

Rests on: result-284db5, result-6f1bb7, result-95a4dc, result-59ed1a, result-a7c052. Forecasts 12 of 24 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t01 | 368 | [348, 388] | 348 [325, 372] | 352 [326, 378] |  | disagree: readers apply Code top-8's cross-domain share on math (a third) to code itself; on its own domain the edit carries about twice that share, as Math top-8 does on math. |
| t02 | 377 | [355, 399] | 356 [330, 382] | 360 [332, 386] |  | disagree: the readers' 356-360 is the cross-domain share; in-domain 1.5x closed 90-100 % of Math-RL's gap on both math sets. |
| t03 | 365 | [338, 392] | 347 [312, 378] | 350 [316, 380] |  | disagree: the dip from 1.5x is the same as the readers', but it starts from the higher in-domain level. |
| t04 | 315 | [301, 329] | 318 [300, 336] | 315 [298, 332] |  | agree: base 317 plus noise, as the readers. |
| t05 | 344 | [324, 364] | 338 [314, 362] | 333 [310, 358] |  | disagree: Math directions carry the shared deliberate-and-finish part, which the Math cue shows is fully worth having on code (326), so a little above the readers' 333-338. |
| t06 | 54 | [46, 62] | 52 [44, 61] | 53 [45, 61] |  | agree: the readers' 52-53 equally follow from the in-domain match. |
| t07 | 49 | [44, 54] | 47.5 [42, 53] | 47.5 [42, 53] |  | agree: near the readers' 47.5, a little higher because the edit is in its own domain. |
| t08 | 416.5 | [410.5, 422.5] | 416.5 [410, 423] | 416 [410, 422] |  | agree: the readers' regression of 418. |
| t09 | 423 | [417, 429] | 422.5 [415, 430] | 424 [418, 430] |  | agree: as the readers. |
| t10 | 434 | [428, 440] | 434 [427, 441] | 434 [428, 440] |  | agree: as the readers. |
| t11 | 1.2 | [-0.3, 2.7] | 1.2 [-0.4, 2.9] | 1.1 [-0.3, 2.5] |  | agree: same arithmetic. |
| t22 | 467 | [458, 476] | 467 [457, 476] | 466 [455, 476] |  | agree: the readers' 466-467. |

## f2-m03

MATH-500 errors split by problem. A slip is a per-step chance error that independent samples rarely repeat. A misreading is set up by how the problem is worded, so the same problem draws it again and again, and that wrong value keeps a stable plurality. A vote fixes slips but not misread problems, so it saturates below pass@k. Early RL steps remove slips, and later steps remove misreadings.

Rests on: result-c495fe, result-faf15a, result-40ed3b, result-e41d94, result-fad48d. Forecasts 12 of 24 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t16 | 452 | [447, 457] | 455 [447, 462] | 453 [447, 459] |  | agree: just under the readers' 453-455, since misread problems cap the vote. |
| t17 | 453 | [448, 458] | 456 [448, 464] | 455 [449, 461] |  | agree: plateau as the readers say, starting from a slightly lower level. |
| t08 | 416 | [410, 422] | 416.5 [410, 423] | 416 [410, 422] |  | agree: gives the readers' ~416. |
| t09 | 423 | [417, 429] | 422.5 [415, 430] | 424 [418, 430] |  | agree: as the readers. |
| t10 | 434 | [428, 440] | 434 [427, 441] | 434 [428, 440] |  | agree: as the readers. |
| t11 | 1.1 | [-0.4, 2.6] | 1.2 [-0.4, 2.9] | 1.1 [-0.3, 2.5] |  | agree: same as the readers. |
| t14 | 465 | [456, 474] | 465 [454, 475] | 465 [452, 476] |  | agree: the readers' 465. |
| t15 | 460 | [450, 470] | 460 [448, 470] | 460 [445, 472] |  | agree: the readers' 460. |
| t18 | 79 | [74, 84] | 79 [73, 85] | 79 [73, 85] |  | agree: as the readers. |
| t19 | 71.3 | [69.2, 73.4] | 71.3 [69.3, 73.5] | 71.3 [68.8, 73.8] |  | agree: as the readers. |
| t21 | 230.5 | [226.5, 234.5] | 229.5 [225, 234.5] | 231 [227, 235] |  | agree: as the readers. |
| t22 | 466 | [457, 475] | 467 [457, 476] | 466 [455, 476] |  | agree: as the readers. |

## f2-m04

Answer type sets what voting and grading can recover. Contest answers are integers from a wide range, so wrong answers scatter and a right answer with modest per-sample probability wins the plurality. MATH-500 answers are often expressions. There Think-SFT writes the gold on the line after 'Answer:', and v3 misses it in about 4 answers per sample. Its native template still ends on an 'Answer:' line, so that undercount stays.

Rests on: result-818c20, result-5251c9, result-5c961a, knowledge-499152. Forecasts 12 of 24 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t14 | 464 | [455, 473] | 465 [454, 475] | 465 [452, 476] |  | agree: the readers' 465, and the undercount they cite stays. |
| t15 | 458 | [449, 467] | 460 [448, 470] | 460 [445, 472] |  | agree: the readers' 460. |
| t12 | 232 | [218, 246] | 231 [214, 247] | 235 [212, 256] |  | agree: as the readers. |
| t13 | 203 | [189, 217] | 205 [186, 222] | 200 [172, 226] |  | agree: as the readers. |
| t18 | 79 | [74, 85] | 79 [73, 85] | 79 [73, 85] |  | agree: as the readers. |
| t20 | 248 | [240, 256] | 247 [237, 257] | 247 [239, 256] |  | agree: the readers' 247. |
| t23 | 247 | [238, 256] | 244 [235, 254] | 247 [237, 257] |  | agree: the readers' 244-247. |
| t24 | 82 | [74, 90] | 81 [72, 90] | 80 [72, 88] |  | agree: the readers' 80-81. |
| t06 | 53 | [45, 61] | 52 [44, 61] | 53 [45, 61] |  | agree: the readers' 52-53. |
| t16 | 454 | [448, 460] | 455 [447, 462] | 453 [447, 459] |  | agree: the readers' 453-455. |
| t17 | 455 | [449, 461] | 456 [448, 464] | 455 [449, 461] |  | agree: as the readers. |
| t22 | 466 | [457, 475] | 467 [457, 476] | 466 [455, 476] |  | agree: as the readers. |

## f2-m05

Too large a finishing dose makes the model stop before its derivation is complete. The cost grows with how long a derivation the problem needs: on hard328's long problems a 2x edit commits early and right answers fall, while short problems finish well within the shortened span. Over-dosing therefore costs little on MATH-500 and on short code tasks. The cost of a cut answer, by contrast, belongs to the opposite end of the length range.

Rests on: result-6f1bb7, result-51a0e7, result-3387ce, result-1b6bf2, result-59ed1a. Forecasts 12 of 24 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t01 | 350 | [328, 372] | 348 [325, 372] | 352 [326, 378] |  | agree: the readers' 348-352. |
| t02 | 358 | [334, 382] | 356 [330, 382] | 360 [332, 386] |  | agree: the readers' 356-360. |
| t03 | 355 | [330, 380] | 347 [312, 378] | 350 [316, 380] |  | agree: close to the readers' 347-350, with a smaller dip because code derivations are short. |
| t04 | 316 | [301, 331] | 318 [300, 336] | 315 [298, 332] |  | agree: as the readers. |
| t05 | 335 | [313, 357] | 338 [314, 362] | 333 [310, 358] |  | agree: the readers' 333-338. |
| t22 | 467 | [459, 475] | 467 [457, 476] | 466 [455, 476] |  | agree: as the readers. |
| t20 | 247 | [239, 255] | 247 [237, 257] | 247 [239, 256] |  | agree: as the readers. |
| t21 | 230.5 | [226.5, 234.5] | 229.5 [225, 234.5] | 231 [227, 235] |  | agree: as the readers. |
| t18 | 79 | [74, 84] | 79 [73, 85] | 79 [73, 85] |  | agree: as the readers. |
| t19 | 71.3 | [69.2, 73.4] | 71.3 [69.3, 73.5] | 71.3 [68.8, 73.8] |  | agree: as the readers. |
| t06 | 52 | [44, 60] | 52 [44, 61] | 53 [45, 61] |  | agree: the readers' 52-53. |
| t07 | 47 | [42, 52] | 47.5 [42, 53] | 47.5 [42, 53] |  | agree: the readers' 47.5. |

## f2-m06

A problem set's hardness distribution sets how much any change can move it. fresh2026 is bimodal: most problems are beyond every 7B model's reach, and a thin middle band decides every comparison. hard328 has a wider middle band. So on fresh2026, vote gains, edit gains and the gains from a longer cap all shrink toward the size of that middle band, and they compress the differences between models.

Rests on: result-5251c9, result-389164, knowledge-dab63f, result-527fbb. Forecasts 12 of 24 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t06 | 51 | [44, 58] | 52 [44, 61] | 53 [45, 61] |  | agree: near the readers' 52-53. |
| t07 | 46.5 | [41.5, 51.5] | 47.5 [42, 53] | 47.5 [42, 53] |  | agree: the readers' 47.5. |
| t18 | 79 | [74, 84] | 79 [73, 85] | 79 [73, 85] |  | agree: as the readers. |
| t19 | 71.3 | [69.2, 73.4] | 71.3 [69.3, 73.5] | 71.3 [68.8, 73.8] |  | agree: as the readers. |
| t24 | 79 | [72, 86] | 81 [72, 90] | 80 [72, 88] |  | agree: slightly under the readers' 80-81, since most cut answers sit beyond reach. |
| t20 | 247 | [239, 255] | 247 [237, 257] | 247 [239, 256] |  | agree: as the readers. |
| t21 | 230.5 | [226.5, 234.5] | 229.5 [225, 234.5] | 231 [227, 235] |  | agree: as the readers. |
| t23 | 245 | [236, 254] | 244 [235, 254] | 247 [237, 257] |  | agree: as the readers. |
| t12 | 231 | [217, 245] | 231 [214, 247] | 235 [212, 256] |  | agree: as the readers. |
| t13 | 203 | [189, 217] | 205 [186, 222] | 200 [172, 226] |  | agree: as the readers. |
| t16 | 454 | [448, 460] | 455 [447, 462] | 453 [447, 459] |  | agree: as the readers. |
| t17 | 455 | [449, 461] | 456 [448, 464] | 455 [449, 461] |  | agree: as the readers. |

## t01 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems the base model with Code-RL 3.1's 8 top weight directions added at 1x size passes, with the Code cue at T 1.0.

Unit: problems passed of 538. Cell: {"model": "Olmo-3-1025-7B base + top 8 directions per matrix of (Olmo-3.1 RL-Zero-Code - base) at 1x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": "not stated", "grader": "not stated"}

> base + Code 3.1's 8 directions at 1x, 1.5x, 2x, random at 1.5x, and Math 3.1's at 1.5x, on HumanEval+ and MBPP+ (538 problems, Code cue, T 1.0

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 348 | [325, 372] | Base Code cue 317 and RL-Code 401; on hard328 the 1x top-8 edit closed about 2/3 of the gap for its own reward, so a code edit at 1x should close somewhat less than that on code (~40%). |
| reader-2 | 352 | [326, 378] | Base Code cue 317 vs RL-Code 401; on hard328 Math top-8 at 1x closed about two thirds of the gap and Code top-8 a third, so Code's own directions on code should close roughly 40% of 84. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 368 | [348, 388] | In-domain 1x carries ~2/3 of the gap (Math on hard328: 28 of 42); 317 + 0.6 x 84 = 368. |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | 350 | [328, 372] | Code answers are short (~4k tokens); the 1x gain follows the readers' cross-domain scaling. |
| f2-m06 | - |  | no forecast |

## t02 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems the base model with Code-RL 3.1's 8 top weight directions added at 1.5x size passes, with the Code cue at T 1.0.

Unit: problems passed of 538. Cell: {"model": "Olmo-3-1025-7B base + top 8 directions per matrix of (Olmo-3.1 RL-Zero-Code - base) at 1.5x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": "not stated", "grader": "not stated"}

> base + Code 3.1's 8 directions at 1x, 1.5x, 2x, random at 1.5x, and Math 3.1's at 1.5x, on HumanEval+ and MBPP+ (538 problems, Code cue, T 1.0

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 356 | [330, 382] | On math the 1.5x edit was the peak of the dial (203 on hard328, 456 vs RL 457 on MATH-500), so it should be the best Code size, still short of RL-Code's 401. |
| reader-2 | 360 | [332, 386] | On hard328 the 1.5x size added about +11 over 1x with cap hits falling further; on code the gain should be similar but smaller. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 377 | [355, 399] | In-domain 1.5x reached RL on both math sets; allowing for code being less studied, ~70 % of the 84-problem gap: 317 + 60. |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | 358 | [334, 382] | 1.5x adds a few over 1x. |
| f2-m06 | - |  | no forecast |

## t03 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems the base model with Code-RL 3.1's 8 top weight directions added at 2x size passes, with the Code cue at T 1.0.

Unit: problems passed of 538. Cell: {"model": "Olmo-3-1025-7B base + top 8 directions per matrix of (Olmo-3.1 RL-Zero-Code - base) at 2x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": "not stated", "grader": "not stated"}

> base + Code 3.1's 8 directions at 1x, 1.5x, 2x, random at 1.5x, and Math 3.1's at 1.5x, on HumanEval+ and MBPP+ (538 problems, Code cue, T 1.0

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 347 | [312, 378] | At 2x on math right answers fell back below 1.5x (190 vs 203) as answers over-finish, so slightly below the 1.5x cell, with a wider downside. |
| reader-2 | 350 | [316, 380] | On hard328 the 2x size fell back below 1.5x (190 vs 203) as answers stopped too early, so expect a dip from the 1.5x cell on code. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 365 | [338, 392] | 2x finishes too early, as on hard328 (190 vs 203), so it drops about 12 below 1.5x. |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | 355 | [330, 380] | Short code derivations finish inside 2x's shorter span, so it costs only ~3 against 1.5x, not hard328's 13. |
| f2-m06 | - |  | no forecast |

## t04 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems the base model with a random rank-8 weight edit at 1.5x size (control) passes, with the Code cue at T 1.0.

Unit: problems passed of 538. Cell: {"model": "Olmo-3-1025-7B base + random rank-8 edit at 1.5x (control)", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": "not stated", "grader": "not stated"}

> base + Code 3.1's 8 directions at 1x, 1.5x, 2x, random at 1.5x, and Math 3.1's at 1.5x, on HumanEval+ and MBPP+ (538 problems, Code cue, T 1.0

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 318 | [300, 336] | The random rank-8 edit is flat at every size on math (158-167 vs base 164), so expect the cued base's 317 plus sampling noise. |
| reader-2 | 315 | [298, 332] | Random rank-8 edits were flat at or just below base at every size on hard328 (158-167 vs 164), so this should land at base cue 317 plus sample noise. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 315 | [301, 329] | A random rank-8 edit carries no domain habit; on math it is flat to -1.5 points. |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | 316 | [301, 331] | Random edit: no dose effect. |
| f2-m06 | - |  | no forecast |

## t05 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems the base model with Math-RL 3.1's 8 top weight directions added at 1.5x size passes, with the Code cue at T 1.0.

Unit: problems passed of 538. Cell: {"model": "Olmo-3-1025-7B base + top 8 directions per matrix of (Olmo-3.1 RL-Zero-Math - base) at 1.5x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": "not stated", "grader": "not stated"}

> base + Code 3.1's 8 directions at 1x, 1.5x, 2x, random at 1.5x, and Math 3.1's at 1.5x, on HumanEval+ and MBPP+ (538 problems, Code cue, T 1.0

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 338 | [314, 362] | Math-RL transfers to code (LiveCodeBench 21.9% vs base 10.1%, Math cue 326 on this set), so a partial gain over 317, below Code's own directions. |
| reader-2 | 333 | [310, 358] | Math-RL transfers to code (Math cue 326 on code, Math RL scores well on LiveCodeBench) and Math directions write finishing, but they are not code-specific, so a modest gain over 317. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 344 | [324, 364] | Cross-domain carries ~half of an in-domain 1.5x edit (~90 %): 317 + 0.33 x 84 ≈ 345. |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | 335 | [313, 357] | Math dose 1.5x on short code: modest gain, no over-dose cost. |
| f2-m06 | - |  | no forecast |

## t06 (work-16773f): How many of the 136 fresh2026 contest problems the base model plus 1.5 times RL-Math's top 8 weight directions gets right with the cue under a majority vote over 4 samples (RL's vote: 57).

Unit: right answers of 136 (vote over 4). Cell: {"model": "Olmo-3-1025-7B base + 1.5 x top 8 directions per matrix of (RL-Math - base)", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> is it level with RL (57 vote, 50.5 single) where its size was not chosen?

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 52 | [44, 61] | The 1.5x edit matched RL per sample on hard328 (200.25 vs 200) but lagged under the vote (214 vs 221), so slightly under RL's fresh2026 vote of 57. |
| reader-2 | 53 | [45, 61] | The 1.5x edit matched RL's single sample on hard328 but trailed under the vote (214 vs 221); RL's fresh2026 vote is 57 and the base's 38. |
| r5-m03-rival | 54 | [46, 62] | The theory says the top-8 edit puts each sample on a weak dose of RL's own policy, and with the cue nearly every sample is RL-like. So the vote should sit just under RL's 57, shaded down by the gap the 1.5x edit showed on hard328 (vote 214 against RL's 221, about -2 points or -3 of 136). |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 50 | [43, 57] | Single ~45 (below) plus a vote gain of ~5, smaller than the base's +8.5 because the edit commits on hopeless problems. |
| f2-m02 | 54 | [46, 62] | Math edit in its own domain equals RL per sample; its vote trails RL's by ~3, as on hard328 (214 vs 221). |
| f2-m03 | - |  | no forecast |
| f2-m04 | 53 | [45, 61] | Edit single ~47.5, plus a vote gain of ~6 on scattered integer answers. |
| f2-m05 | 52 | [44, 60] | 1.5x is under the over-dose point even for long fresh problems. |
| f2-m06 | 51 | [44, 58] | Edit single ~46.5 plus a vote gain of ~5 from the thin middle band. |

## t07 (work-16773f): The mean number of the 136 fresh2026 contest problems that one sample of the base model plus 1.5 times RL-Math's top 8 weight directions gets right with the cue, averaged over 4 samples (RL single: 50.5).

Unit: mean right answers of 136 per sample (mean of 4 samples). Cell: {"model": "Olmo-3-1025-7B base + 1.5 x top 8 directions per matrix of (RL-Math - base)", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> is it level with RL (57 vote, 50.5 single) where its size was not chosen?

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 47.5 | [42, 53] | The edit's single samples equal RL's on hard328 and MATH-500, and RL's single on fresh2026 is 50.5; shaded down a little on a set where it was not chosen. |
| reader-2 | 47.5 | [42, 53] | The edit equals RL's single-sample rate on hard328 and MATH-500; on fresh2026 RL's single is 50.5 and the base's 29.5, so a little under RL. |
| r5-m03-rival | 49 | [43, 55] | The theory says the edit gives RL-like answers (cued, so no plain-base share) that fail only on hard problems. So the mean single sample should track RL's 50.5, as the 1.5x edit did on hard328 (200.25 against 200.0), shaded slightly down for the 'weak dose' and well above the cued base's 29.5. |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 45 | [40, 50] | Base 29.5 with ~55 cut answers per sample; the edit finishes ~35 more at ~20 % right (+7) and lifts already-finished answers by ~14 % (+4), plus ~4.5 from RL-like checking. |
| f2-m02 | 49 | [44, 54] | In-domain 1.5x matched RL per sample on hard328 and MATH-500; RL single 50.5. |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | 47 | [42, 52] | 1.5x is under the over-dose point; close to RL, shaded down for fresh2026's longest problems. |
| f2-m06 | 46.5 | [41.5, 51.5] | The middle band is shared with RL; the edit reaches most of it. |

## t08 (work-f8ecb6): The mean number of the 500 MATH-500 problems the RL-Zero-Math step-100 checkpoint gets right with the plain prompt at T 1.0, averaged over 4 samples (grader v3).

Unit: mean right answers of 500 per sample (mean of 4 samples). Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math checkpoint step 100", "prompt": "plain", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": 4, "grader": "v3"}

> 3 more samples of step-100 plain, step-100 cue, step-400 plain (MATH-500, T 1.0, v3)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 416.5 | [410, 423] | Stored sample 0 is 418; the three new samples are regressed slightly toward ~416, with a per-sample sd of about 5 problems. |
| reader-2 | 416 | [410, 422] | Sample 0 is 418, plus 3 new samples with per-sample SD about 6-7 and slight regression toward the cued base's 410. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 416.5 | [410.5, 422.5] | Step 100 is an in-domain early RL policy; stored 418 regressed. |
| f2-m03 | 416 | [410, 422] | Step 100 has removed some slips (finished-answer error 4.6 points lower at T 0.6); stored 418 regressed. |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t09 (work-f8ecb6): The mean number of the 500 MATH-500 problems the RL-Zero-Math step-100 checkpoint gets right with the opening cue at T 1.0, averaged over 4 samples (grader v3).

Unit: mean right answers of 500 per sample (mean of 4 samples). Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math checkpoint step 100", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": 4, "grader": "v3"}

> 3 more samples of step-100 plain, step-100 cue, step-400 plain (MATH-500, T 1.0, v3)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 422.5 | [415, 430] | Stored cue sample 0 is 427; new samples regressed toward ~421, since the cue's effect on step 100 is +1.8 [-1.2, 4.8]. |
| reader-2 | 424 | [418, 430] | Sample 0 is 427, plus 3 new samples with slight regression. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 423 | [417, 429] | Stored 427, cue effect +1.8 regressed. |
| f2-m03 | 423 | [417, 429] | Cue adds the opening on top; stored 427 regressed. |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t10 (work-f8ecb6): The mean number of the 500 MATH-500 problems the RL-Zero-Math step-400 checkpoint gets right with the plain prompt at T 1.0, averaged over 4 samples (grader v3).

Unit: mean right answers of 500 per sample (mean of 4 samples). Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math checkpoint step 400", "prompt": "plain", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": 4, "grader": "v3"}

> 3 more samples of step-100 plain, step-100 cue, step-400 plain (MATH-500, T 1.0, v3)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 434 | [427, 441] | Stored sample 0 is 436 (step 400 cue 431); the new samples are regressed toward ~433. |
| reader-2 | 434 | [428, 440] | Sample 0 is 436, plus 3 new samples with slight regression. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 434 | [428, 440] | Stored 436 regressed. |
| f2-m03 | 434 | [428, 440] | Step 400 also starts on misreadings; stored 436 regressed. |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t11 (work-f8ecb6): The difference in MATH-500 accuracy points between the RL-Zero-Math step-100 checkpoint with the plain prompt and the untrained base with the cue, at T 1.0 over 4 samples each (grader v3).

Unit: points (step-100 plain minus cued base, 4 samples each). Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math step 100 vs untrained Olmo-3-1025-7B base", "prompt": "plain (step 100) vs cue (base)", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": 4, "grader": "v3"}

> so the step-100 vs cued-base difference has a 4-sample interval

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 1.2 | [-0.4, 2.9] | Expected step-100 plain mean ~416.5 against the cued base's stored 4-sample mean of 410.5, divided by 5 to give points. |
| reader-2 | 1.1 | [-0.3, 2.5] | Step-100 mean of about 416 minus the cued base's stored 4-sample mean of 410.5 (1642/2000), in points of 500. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 1.2 | [-0.3, 2.7] | (416.5 - 410.5) / 5. |
| f2-m03 | 1.1 | [-0.4, 2.6] | Slip removal worth ~6 problems over the cued base's 410.5. |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t12 (work-8b2ec9): How many of the 328 harder problems Think-SFT gets right in its own ChatML chat format with <think>, at T 1.0 with a 32,768-token cap, one sample (grader v3).

Unit: right answers of 328. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "own ChatML chat template with <think>", "set": "hard328", "n": 328, "sampling": "T 1.0; top-p not stated; token cap 32,768", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 231 | [214, 247] | Paired with the raw-template cue cell at cap 32k (230); its native training format should neither help nor hurt by much. |
| reader-2 | 235 | [212, 256] | With the cue at cap 32k Think-SFT scored 230; its own training format should help somewhat, though its thinking traces may run longer. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 231 | [217, 245] | At 32k nearly all of Think-SFT's cut answers finish (91 of 93 in the cue run), 25 % right, as in the raw-template cue cell's 230. |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | 232 | [218, 246] | hard328 answers are mostly integers, so there is no undercount; equal to the cue cell's 230. |
| f2-m05 | - |  | no forecast |
| f2-m06 | 231 | [217, 245] | Same middle band as the cue cell's 230. |

## t13 (work-8b2ec9): How many of the 328 harder problems Think-SFT gets right in its own ChatML chat format with <think>, at T 1.0, one sample, counting only answers finished within 16,384 tokens (grader v3).

Unit: right answers of 328. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "own ChatML chat template with <think>", "set": "hard328", "n": 328, "sampling": "T 1.0; top-p not stated; generated at cap 32,768, counted at cap 16,384", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 205 | [186, 222] | Paired with the cue cell counted at 16k (207); native thinking may run longer, so a few more answers could be cut. |
| reader-2 | 200 | [172, 226] | With the cue Think-SFT scored 207 counted at 16k; native <think> traces are probably longer, so more cap hits at 16k. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 204 | [190, 218] | Same answers counted at 16k lose the ~90 long answers, as in the cue run (207). |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | 203 | [189, 217] | 16k count of the same answers. |
| f2-m05 | - |  | no forecast |
| f2-m06 | 203 | [189, 217] | 16k count, as the cue cell's 207 minus ~4. |

## t14 (work-8b2ec9): How many of the 500 MATH-500 problems Think-SFT gets right in its own ChatML chat format with <think>, at T 1.0 with a 32,768-token cap, one sample (grader v3).

Unit: right answers of 500. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "own ChatML chat template with <think>", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; token cap 32,768", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 465 | [454, 475] | Think-SFT cue singles score 457-462 at 16k, plus a small gain from the 32k cap; v3 undercounts this model by about 4. |
| reader-2 | 465 | [452, 476] | With the cue Think-SFT singles are 454-462 at 16k; the native format plus the 32k cap should add a few. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 468 | [460, 476] | 16k count ~459 plus ~23 of ~25 cut answers finishing at ~45 % right (+10). |
| f2-m02 | - |  | no forecast |
| f2-m03 | 465 | [456, 474] | Think-SFT's remaining errors are mostly misreads plus cut answers; 32k fixes some cut ones. |
| f2-m04 | 464 | [455, 473] | True ~468, minus the ~4 v3 undercount that the native 'Answer:' line keeps. |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t15 (work-8b2ec9): How many of the 500 MATH-500 problems Think-SFT gets right in its own ChatML chat format with <think>, at T 1.0, one sample, counting only answers finished within 16,384 tokens (grader v3).

Unit: right answers of 500. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "own ChatML chat template with <think>", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; generated at cap 32,768, counted at cap 16,384", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 460 | [448, 470] | Same answers counted at 16k should sit at the Think-SFT cue singles of 457-462. |
| reader-2 | 460 | [445, 472] | The same answers counted at 16k lose the few long ones; MATH-500 answers are mostly short. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 459 | [450, 468] | Equals the cue singles at 16k (457-462); native format does not shorten derivations. |
| f2-m02 | - |  | no forecast |
| f2-m03 | 460 | [450, 470] | Equals the cue singles. |
| f2-m04 | 458 | [449, 467] | Cue singles 457-462 with the same undercount. |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t16 (work-60f040): How many of the 500 MATH-500 problems the untrained base with the opening cue gets right under a majority vote over 9 samples at T 1.0 (grader v3).

Unit: right answers of 500 (vote over 9). Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": 9, "grader": "v3"}

> vote over 9 = 456 [449, 462] of 500 (result-c637b2)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 455 | [447, 462] | Vote over 4 is 446 and pass@4 467; Wang's majority curve gains ~2.5 points from 4 to 8 votes; the theory predicted 456 [449, 462]. |
| reader-2 | 453 | [447, 459] | Vote over 4 is 446 and pass@4 467; Wang's majority curve adds about 1.5-2.5 points from 4 to 8-9 votes. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 456 | [448, 463] | The rival account's last sentence says a base-only vote over more samples recovers part of the sharpening share (the largest open part at T 1.0) and gives 456/500 for the vote over 9; the interval is widened a little around the filed [449, 462] because the stored vote over 4 is 446 and pass@4 is 467. |
| r6-m06 | 452 | [442, 461] | The theory's claim that the cued base's wrong steps come from the head of its own distribution (result-faf15a, result-b30f15) means the same errors keep coming back across samples, so the vote levels off a little above the stored vote over 4 (446, 450 after restart) and stays below the 456 that a closing gap would need. |
| r7-m05 | 450 | [443, 457] | The theory puts the cued base's misreads and slips (about 58 % of its errors) near the mode of its distribution, where more samples repeat them instead of outvoting them, so the vote should level off just above the board's vote over 4 of 446 (450 after restart) and not climb to the 456 of result-c637b2. |
| r7-m08 | 451 | [444, 458] | The theory's no_intervention says the base's remaining errors are steps the base itself rates as likely (-0.53 vs -0.63 nats/token), so they recur across samples and voting can't remove them. More samples should therefore leave the vote close to the measured vote over 4 (446, 450 after restart), with only a small rise. |
| r7-m11 | 451 | [445, 457] | The theory says wrong answers drawn under the one shared cue opening agree with each other, so extra samples under that opening keep adding to the same wrong groups; the vote should therefore gain less going from 4 to 9 samples than the independent-slip forecast of 456 (result-c637b2), giving about 5 problems over the stored vote of 446. |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | 452 | [447, 457] | Vote@4 446 with ~12 of 36 ties right; nine samples settle ties at about half (+6), and misread problems stay wrong, so 452. |
| f2-m04 | 454 | [448, 460] | Expression answers group less cleanly, so the gain over 4 votes is ~8. |
| f2-m05 | - |  | no forecast |
| f2-m06 | 454 | [448, 460] | MATH-500's middle band is ~40 problems, and four votes already take most of it. |

## t17 (work-60f040): How many of the 500 MATH-500 problems the untrained base with the opening cue gets right under a majority vote over 12 samples at T 1.0 (grader v3).

Unit: right answers of 500 (vote over 12). Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": 12, "grader": "v3"}

> Vote over k = 1..12 samples of the untrained cued base on MATH-500

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 456 | [448, 464] | The vote flattens past 9 samples, so expect at most a point above the vote over 9. |
| reader-2 | 455 | [449, 461] | The vote curve flattens past 9 samples, so expect 1-2 problems above the vote over 9. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 457 | [449, 465] | Same sharpening clause: extending the vote from 9 to 12 base samples recovers slightly more of the resample-type gap than the theory's 456 for 9, with diminishing returns along the one difficulty axis, so it adds about 1 problem. |
| r6-m06 | 453 | [443, 462] | Same head-error mechanism: the errors keep coming back across samples, so going from 9 to 12 samples adds about one problem on the plateau above the stored vote over 4 (446). |
| r7-m05 | 451 | [444, 458] | Same part of the theory (misread and slip steps sit near the mode, so extra samples repeat them): going from 9 to 12 votes should add about one problem over the plateau near 446-450. |
| r7-m08 | 452 | [445, 459] | Same no_intervention argument: the base's slips are high-probability under the base, so selection among base samples levels off near the vote-over-4 value of 446-450, and 12 samples add at most about 1 more than 9. |
| r7-m11 | 452 | [446, 458] | Under the same mechanism (agreeing wrong groups under one opening cap the vote), the vote levels off: 12 samples add at most about 1 problem over 9, still below the independent-slip curve and short of RL's one-sample 456-463. |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | 453 | [448, 458] | Plateau: 3 more samples fix at most 1-2 slip-only problems. |
| f2-m04 | 455 | [449, 461] | Plateau. |
| f2-m05 | - |  | no forecast |
| f2-m06 | 455 | [449, 461] | Plateau. |

## t18 (work-8b4030): How many of the 136 fresh2026 contest problems Think-SFT plus twice the RL-Math weight change gets right under a majority vote over 4 samples.

Unit: right answers of 136 (vote over 4). Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> fresh2026 (136 problems, 4 samples, seeds of SPEC_fresh)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 79 | [73, 85] | Vote over 3 is 78; adding a 4th sample moved Think-SFT's vote by +1 (74 to 75). |
| reader-2 | 79 | [73, 85] | The vote over 3 is already 78 (Think-SFT 74 over 3 rose to 75 over 4), so the fourth sample adds about 1. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 79 | [74, 84] | Vote over 3 is 78; a 4th sample adds about 1 at a=2's cut rate. |
| f2-m02 | - |  | no forecast |
| f2-m03 | 79 | [74, 84] | Vote over 3 is 78, and a 4th sample settles about one tie. |
| f2-m04 | 79 | [74, 85] | Integer answers scatter, so a 4th sample adds about one plurality win to 78. |
| f2-m05 | 79 | [74, 84] | Vote over 3 is 78. |
| f2-m06 | 79 | [74, 84] | Middle band nearly used up at three votes (78). |

## t19 (work-8b4030): The mean number of the 136 fresh2026 contest problems that one sample of Think-SFT plus twice the RL-Math weight change gets right, averaged over all 4 samples (three already read 69, 70, 75).

Unit: mean right answers of 136 per sample (mean of 4 samples). Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> fresh2026 (136 problems, 4 samples, seeds of SPEC_fresh)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 71.3 | [69.3, 73.5] | Three samples (69, 70, 75) are known; the 4th is expected at ~71 with a per-sample sd of about 3. |
| reader-2 | 71.3 | [68.8, 73.8] | Three samples are known (69, 70, 75); the fourth should be about 71 with SD about 5, giving a mean of (214+x)/4. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 71.3 | [69.2, 73.4] | Known 69, 70, 75; the 4th sample ~71. |
| f2-m02 | - |  | no forecast |
| f2-m03 | 71.3 | [69.2, 73.4] | Known samples 69, 70, 75. |
| f2-m04 | - |  | no forecast |
| f2-m05 | 71.3 | [69.2, 73.4] | Known 69, 70, 75. |
| f2-m06 | 71.3 | [69.2, 73.4] | Known samples. |

## t20 (work-8b4030): How many of the 328 harder problems Think-SFT plus twice the RL-Math weight change gets right under a majority vote over 4 samples.

Unit: right answers of 328 (vote over 4). Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated", "samples": 4, "grader": "not stated"}

> hard328 samples 3-4 for the vote over 4

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 247 | [237, 257] | Singles average ~230; the vote gain should fall between RL's (+21) and Think-SFT's (+32) because a=2 has fewer cap hits and lower precision, and on fresh2026 its vote gain was about half of Think-SFT's. |
| reader-2 | 247 | [239, 256] | Single samples average about 231; the vote gains less than Think-SFT's +32 because fewer samples abstain at the cap, but more than RL's +21. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 247 | [239, 255] | Singles ~231; a=2's lower cut rate (~13 %) puts its vote gain between RL's +21 and Think-SFT's +32. |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | 248 | [240, 256] | Integer answers let a=2's ~70 %-precision samples win most pluralities: singles 231 + ~17. |
| f2-m05 | 247 | [239, 255] | a=2 is the dose peak on hard328; singles 231 plus a vote gain of ~16. |
| f2-m06 | 247 | [239, 255] | hard328's wider middle band gives a=2 a vote gain of ~16. |

## t21 (work-8b4030): The mean number of the 328 harder problems that one sample of Think-SFT plus twice the RL-Math weight change gets right, averaged over 4 samples (the first two scored 234 and 229).

Unit: mean right answers of 328 per sample (mean of 4 samples). Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated", "samples": 4, "grader": "not stated"}

> hard328 samples 3-4 for the vote over 4

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 229.5 | [225, 234.5] | Two samples are known (234, 229); the two new seeds are expected at ~228 with a per-sample sd of about 5. |
| reader-2 | 231 | [227, 235] | The first two samples scored 234 and 229; two new samples with per-sample SD about 5. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 230.5 | [226.5, 234.5] | Two known (234, 229), two new ~230. |
| f2-m02 | - |  | no forecast |
| f2-m03 | 230.5 | [226.5, 234.5] | Known samples 234, 229. |
| f2-m04 | - |  | no forecast |
| f2-m05 | 230.5 | [226.5, 234.5] | Known 234, 229. |
| f2-m06 | 230.5 | [226.5, 234.5] | Known 234, 229. |

## t22 (work-8b4030): How many of the 500 MATH-500 problems Think-SFT plus twice the RL-Math weight change gets right in one sample.

Unit: right answers of 500. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "MATH-500", "n": 500, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> MATH-500 1 sample

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 467 | [457, 476] | a=1 scored 467 on MATH-500 and Think-SFT cue singles score 457-462; a=2 should sit at about the same level. |
| reader-2 | 466 | [455, 476] | At a=1 the cell scored 467 on MATH-500; at a=2 the score on easy problems should stay near that. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 467 | [458, 476] | MATH-500 is near ceiling for an in-domain stack; a=1 gave 467. |
| f2-m03 | 466 | [457, 475] | The RL change at a=2 removes slips already removed at a=1; misreads remain, so the score stays near 467. |
| f2-m04 | 466 | [457, 475] | Think-SFT stack keeps the 'Answer:' format, so the undercount stays; a=1 gave 467. |
| f2-m05 | 467 | [459, 475] | MATH-500 is short, so a=2's early stops cost nothing there; same as a=1's 467. |
| f2-m06 | - |  | no forecast |

## t23 (work-dc9359): How many of the 328 harder problems Think-SFT with the cue gets right under a majority vote over 4 samples when answers may run to 32,768 tokens.

Unit: right answers of 328 (vote over 4). Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "token cap 32,768; T and top-p not stated", "samples": 4, "grader": "not stated"}

> Think-SFT + cue vote over 4 at token cap 32,768 on hard328 (samples 1-3 new, sample 0 = the cap32 run)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 244 | [235, 254] | The 16k vote is 241 and the offline simulation said 240 [232, 248]; late answers at 32k add a few right ones (single +7 points), but they are only ~25% right. |
| reader-2 | 247 | [237, 257] | The 16k vote is 241 and sample 0 at 32k scored 230 (vs 207 at 16k); the offline simulation said 240 unless late wrong answers disagree (254). |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 246 | [237, 255] | Late answers convert at ~25 % on hard problems; wrong late answers scatter, so the vote gains ~5 over 241. |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | 247 | [238, 256] | Late wrong integer answers rarely agree with each other, so they seldom outvote a right one; ~6 over 241. |
| f2-m05 | - |  | no forecast |
| f2-m06 | 245 | [236, 254] | Vote ≈ pass@4 already (241 vs 244); 32k adds a few middle-band problems. |

## t24 (work-dc9359): How many of the 136 fresh2026 contest problems Think-SFT with the cue gets right under a majority vote over 4 samples when answers may run to 32,768 tokens.

Unit: right answers of 136 (vote over 4). Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "token cap 32,768; T and top-p not stated", "samples": 4, "grader": "not stated"}

> and fresh2026 (4 samples), each answer scored at 16,384 and 32,768 from the same text

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 81 | [72, 90] | The 16k vote is 75 with 46% cap hits on fresh2026; finishing those cut answers at ~20-25% precision should add several problems to the vote. |
| reader-2 | 80 | [72, 88] | The 16k vote is 75 with 46% cap hits; at 32k many cut answers finish, and about a quarter of those are right. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 81 | [74, 88] | Fresh2026 has ~62 cut answers per sample, converting at ~15 % (+9 per sample); the vote gains about 6 over 75. |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | 82 | [74, 90] | Same scatter on contest integers: late answers add right pluralities without new wrong majorities. |
| f2-m05 | - |  | no forecast |
| f2-m06 | 79 | [72, 86] | Late answers on fresh2026 come mostly from beyond-reach problems; gain ~4 over 75. |
