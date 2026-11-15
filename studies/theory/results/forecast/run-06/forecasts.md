# Forecasts, run-06

Board snapshot 2026-11-15T16:32:52 UTC, written 2026-11-15T16:44:05 UTC. 31 targets; forecasters reader-1, reader-2, r5-m03-rival, r6-account-rival, r6-m06, r7-m05, r7-m08, r7-m11, f2-m01, f2-m02, f2-m03, f2-m04, f2-m05, f2-m06.


Lens of the mechanisms: training data and objective: what Think-SFT imitation, RL reward and pretraining each put into the model, exposure of problems


## f2-m01

Think-SFT imitates teacher traces in which every stated value is derived and the answer comes only after the work, so it rarely asserts a guess: a sample cut at the cap is unfinished work, not a stall. More budget turns about a quarter of cut samples into right answers on hard sets and more on easy ones; late wrong answers scatter, so the vote keeps gaining. The habit sits in the weights, so the template changes little.

Rests on: result-c8b994, result-02da9f, result-fc7efc, result-818c20, result-0c1eef. Forecasts 16 of 31 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t06 | 51.5 | [43, 60] | 52 [43, 60] | 51 [43, 59] |  | agree: the edit lacks the imitation habit, so the readers' interpolation toward RL's vote holds. |
| t07 | 47.5 | [40, 55] | 46.5 [39, 54] | 48 [41, 55] |  | agree: the mechanism adds nothing to the edit beyond the readers' finishing-plus-precision reading. |
| t12 | 233 | [217, 249] | 232 [215, 248] | 233 [216, 249] |  | agree: the template does not change the habit, so the score stays level with the cue run. |
| t13 | 204 | [187, 220] | 202 [183, 219] | 204 [187, 221] |  | agree: the readers already take the cue run's 16k number with a slight cut for length. |
| t14 | 466 | [457, 475] | 462 [451, 472] | 463 [452, 473] |  | disagree: the readers add only a few points for 32k; on MATH-500 the cut samples are continuable work on easier problems and convert at a higher rate than hard328's 25 %. |
| t15 | 458.5 | [447, 469] | 458 [446, 468] | 459 [447, 469] |  | agree: same habit, same cut, same score as the cue singles. |
| t16 | 1 | [-5, 6.5] | 0.6 [-4.5, 5.5] | 0.9 [-6, 7.5] |  | agree: a near-zero paired difference is what the readers give. |
| t17 | -1 | [-7.5, 5] | -1.5 [-7.5, 4] | -0.9 [-7.5, 6] |  | agree: same small negative as the readers. |
| t21 | 453.5 | [447, 460] | 452 [446, 458] | 454 [447, 461] |  | agree: the mechanism implies the same slow plateau the readers forecast. |
| t25 | 456 | [449, 463] | 454 [448, 461] | 457 [449, 464] |  | agree: plateau near 456, as the readers say. |
| t26 | 71.3 | [69, 73.7] | 71.3 [69, 73.6] | 71.3 [68.8, 73.8] |  | agree: the arithmetic is the same as the readers'. |
| t27 | 79 | [75, 83] | 79 [75, 83] | 79 [75, 83] |  | agree: a small vote gain, as the readers say. |
| t28 | 247 | [238, 256] | 248 [240, 256] | 246 [237, 255] |  | agree: half the habit gives half the vote gain, the readers' number. |
| t29 | 466.5 | [457, 475] | 467 [458, 475] | 466 [457, 475] |  | agree: little room for the habit to matter on MATH-500. |
| t30 | 249 | [240, 258] | 246 [238, 254] | 246 [236, 256] |  | disagree: the readers expect late wrong answers to vote against right ones; under this mechanism those answers scatter, so the vote gains a little more than they say. |
| t31 | 84 | [76, 92] | 81 [73, 89] | 81 [72, 89] |  | disagree: with almost half the samples cut, finishing them helps the vote more than the readers' +6, because the late wrong answers do not agree with each other. |

## f2-m02

Olmo 3's pretraining and midtraining mix already contains long first-person reasoning traces, so the base holds a complete deliberative register. The cue, a self-opened draw and the first ~100 RL steps only select it. Early RL also sharpens slightly inside the register (about 2 points). So the cue adds nothing to a checkpoint that already opens itself, and it carries a fixed 55-78 % share of RL's gain across math, code and general questions.

Rests on: result-fad48d, result-3a3af3, result-59ed1a, result-1a80e9, result-32b7a8. Forecasts 19 of 31 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t01 | 349 | [323, 375] | 348 [325, 372] | 350 [322, 378] |  | agree: the register account adds nothing on the size of the code edit beyond the readers' discount. |
| t02 | 357 | [328, 386] | 355 [328, 382] | 360 [328, 391] |  | agree: nothing in the register account changes the readers' number. |
| t03 | 348 | [310, 384] | 345 [308, 378] | 351 [310, 388] |  | agree: same reasoning as the readers. |
| t04 | 314 | [297, 331] | 315 [298, 332] | 314 [297, 332] |  | agree: random edits are flat, as the readers say. |
| t05 | 338 | [313, 363] | 336 [312, 360] | 340 [314, 366] |  | agree: the readers' half-transfer estimate fits a shared register. |
| t08 | 420 | [413, 427] | 416 [409, 423] | 416 [409, 423] |  | disagree: the readers shrink 418 toward the cued base, but the cue cell (427) is a second draw of the same register and pulls the mean up, not down. |
| t09 | 424 | [417, 431] | 424 [416, 431] | 423 [415, 430] |  | agree: the pooled reading also gives about 424, the readers' number. |
| t10 | 434 | [427, 441] | 434 [427, 441] | 434 [427, 441] |  | agree: same level as the readers. |
| t11 | 1.9 | [0.3, 3.5] | 1.1 [-0.7, 2.9] | 1.1 [-0.8, 3] |  | disagree: the readers give step 100 only +1.1; early RL also sharpens inside the register, and the step-100 cue cell shows its level is above 416. |
| t16 | 0.5 | [-5, 6] | 0.6 [-4.5, 5.5] | 0.9 [-6, 7.5] |  | agree: both prompts select the same register, so the readers' near-zero holds. |
| t17 | -1 | [-7.5, 5] | -1.5 [-7.5, 4] | -0.9 [-7.5, 6] |  | agree: near zero, as the readers say. |
| t18 | 449 | [442, 456] | 448 [442, 454] | 450 [443, 457] |  | agree: the register account gives the readers' slow vote curve. |
| t19 | 450 | [443, 457] | 449 [443, 455] | 451 [444, 458] |  | agree: same curve as the readers. |
| t20 | 452 | [445, 459] | 451 [445, 457] | 453 [446, 460] |  | agree: same curve as the readers. |
| t21 | 453 | [446, 460] | 452 [446, 458] | 454 [447, 461] |  | agree: same curve as the readers. |
| t22 | 454 | [447, 461] | 453 [447, 459] | 455 [448, 462] |  | agree: same curve as the readers. |
| t23 | 455 | [448, 462] | 453 [447, 460] | 456 [448, 463] |  | agree: same curve as the readers. |
| t24 | 455 | [448, 462] | 454 [448, 460] | 456 [449, 463] |  | agree: same curve as the readers. |
| t25 | 456 | [449, 463] | 454 [448, 461] | 457 [449, 464] |  | agree: same curve as the readers. |

## f2-m03

An outcome reward pays only for a gradable final answer, so its consistent gradient piles into a few singular directions that make the model complete the task in the rewarded form (boxed answer, final code block) before the cap; the rest of the update is diffuse. In-domain, the top-8 directions at 1.5x reproduce nearly all of RL's gain over the cued base. Another reward's directions give about half, random rank-8 gives nothing, and 2x commits too early.

Rests on: result-6f1bb7, result-95a4dc, result-284db5, result-39497c, result-51a0e7. Forecasts 16 of 31 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t01 | 366 | [341, 391] | 348 [325, 372] | 350 [322, 378] |  | disagree: the readers cut the share heavily for code, but Code-RL's own directions write its own finishing and code-block format, so the share should match math's. |
| t02 | 378 | [352, 404] | 355 [328, 382] | 360 [328, 391] |  | disagree: the readers assume a weak peak on code; in its own domain the 1.5x edit matched RL on two sets, so it should close most of the code gap. |
| t03 | 365 | [330, 398] | 345 [308, 378] | 351 [310, 388] |  | disagree: 2x falls back to about the 1x level, which this mechanism puts well above the readers' 1x. |
| t04 | 314 | [297, 331] | 315 [298, 332] | 314 [297, 332] |  | agree: random directions carry no finishing, so the readers' number holds. |
| t05 | 345 | [320, 370] | 336 [312, 360] | 340 [314, 366] |  | disagree: the readers use half of a smaller in-domain gain; half of this mechanism's larger code gain is a few points higher. |
| t06 | 53 | [45, 61] | 52 [43, 60] | 51 [43, 59] |  | agree: the readers' interpolation toward RL's vote matches. |
| t07 | 49 | [42, 56] | 46.5 [39, 54] | 48 [41, 55] |  | disagree: the readers stop short of RL; the edit matched RL single on two sets where its size was not chosen, so it should nearly match it here too. |
| t08 | 417 | [410, 424] | 416 [409, 423] | 416 [409, 423] |  | agree: the low-rank account adds nothing beyond the stored sample. |
| t09 | 424 | [416, 431] | 424 [416, 431] | 423 [415, 430] |  | agree: same as the readers. |
| t10 | 434 | [427, 441] | 434 [427, 441] | 434 [427, 441] |  | agree: same as the readers. |
| t11 | 1.2 | [-0.7, 3] | 1.1 [-0.7, 2.9] | 1.1 [-0.8, 3] |  | agree: same as the readers. |
| t26 | 71.3 | [69, 73.7] | 71.3 [69, 73.6] | 71.3 [68.8, 73.8] |  | agree: arithmetic as the readers. |
| t27 | 79 | [75, 83] | 79 [75, 83] | 79 [75, 83] |  | agree: same as the readers. |
| t28 | 247 | [238, 256] | 248 [240, 256] | 246 [237, 255] |  | agree: same as the readers. |
| t29 | 466.5 | [457, 475] | 467 [458, 475] | 466 [457, 475] |  | agree: same as the readers. |
| t30 | 246 | [237, 256] | 246 [238, 254] | 246 [236, 256] |  | agree: this mechanism says nothing beyond the readers' number here. |

## f2-m04

On problems the base can solve, its errors are mostly per-sample slips, drawn by chance and independently at each step. Its remaining errors are misreadings and wrong plans that are set by what pretraining taught about each problem and recur across samples. Majority voting removes the slips by about 5-7 samples and then flattens at the number of problems where the base's modal answer is right, a few below pass@4, however many more samples are drawn.

Rests on: result-c495fe, result-afc423, result-5d032f, result-60d899, result-faf15a. Forecasts 16 of 31 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t18 | 450 | [444, 456] | 448 [442, 454] | 450 [443, 457] |  | agree: the readers' 448-450 already includes the tie-break gain. |
| t19 | 452 | [445, 458] | 449 [443, 455] | 451 [444, 458] |  | agree: within a problem of the readers' 450. |
| t20 | 454 | [448, 460] | 451 [445, 457] | 453 [446, 460] |  | disagree: the readers' curve rises evenly; independent slips are cleared early, so the curve is higher at k=7 and flatter afterwards. |
| t21 | 455 | [449, 461] | 452 [446, 458] | 454 [447, 461] |  | agree: close to the readers' 452-454. |
| t22 | 456 | [450, 462] | 453 [447, 459] | 455 [448, 462] |  | agree: the readers give 453-455; the same plateau. |
| t23 | 457 | [450, 463] | 453 [447, 460] | 456 [448, 463] |  | agree: within the readers' range. |
| t24 | 457 | [451, 463] | 454 [448, 460] | 456 [449, 463] |  | agree: same plateau as the readers. |
| t25 | 458 | [451, 464] | 454 [448, 461] | 457 [449, 464] |  | agree: within a point or two of the readers. |
| t06 | 52 | [44, 60] | 52 [43, 60] | 51 [43, 59] |  | agree: same as the readers. |
| t07 | 47.5 | [40, 55] | 46.5 [39, 54] | 48 [41, 55] |  | agree: same as the readers. |
| t26 | 71.3 | [69, 73.7] | 71.3 [69, 73.6] | 71.3 [68.8, 73.8] |  | agree: arithmetic as the readers. |
| t27 | 79 | [75, 83] | 79 [75, 83] | 79 [75, 83] |  | agree: same as the readers. |
| t28 | 247 | [238, 256] | 248 [240, 256] | 246 [237, 255] |  | agree: same as the readers. |
| t29 | 466.5 | [457, 475] | 467 [458, 475] | 466 [457, 475] |  | agree: same as the readers. |
| t30 | 246 | [237, 255] | 246 [238, 254] | 246 [236, 256] |  | agree: same as the readers. |
| t31 | 81 | [73, 89] | 81 [73, 89] | 81 [72, 89] |  | agree: same as the readers. |

## f2-m05

Imitation and reward write different things. Think-SFT's update, orthogonal to RL's (cosine about 0), supplies derivation quality. RL-Math's update, shaped by a reward that scores unfinished rollouts as failures, supplies pressure to finish. Added to Think-SFT, each unit of the RL change finishes more cut samples at lower precision (88 % falling toward 72 %), so right answers peak near 2x and the vote's gain shrinks to about half of Think-SFT's.

Rests on: result-3387ce, result-e2482e, result-818c20, result-5251c9. Forecasts 16 of 31 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t02 | 357 | [328, 386] | 355 [328, 382] | 360 [328, 391] |  | agree: the readers' weak peak fits. |
| t03 | 348 | [310, 384] | 345 [308, 378] | 351 [310, 388] |  | agree: same fall-back as the readers. |
| t06 | 51.5 | [43, 60] | 52 [43, 60] | 51 [43, 59] |  | agree: same as the readers. |
| t07 | 47.5 | [40, 55] | 46.5 [39, 54] | 48 [41, 55] |  | agree: same as the readers. |
| t12 | 233 | [217, 249] | 232 [215, 248] | 233 [216, 249] |  | agree: no finishing pressure added, so the score is the cue run's. |
| t13 | 204 | [187, 220] | 202 [183, 219] | 204 [187, 221] |  | agree: same as the readers. |
| t14 | 463 | [452, 473] | 462 [451, 472] | 463 [452, 473] |  | agree: same as the readers. |
| t15 | 459 | [447, 469] | 458 [446, 468] | 459 [447, 469] |  | agree: same as the readers. |
| t16 | 0.8 | [-5.5, 7] | 0.6 [-4.5, 5.5] | 0.9 [-6, 7.5] |  | agree: same as the readers. |
| t17 | -1.2 | [-7.5, 5] | -1.5 [-7.5, 4] | -0.9 [-7.5, 6] |  | agree: same as the readers. |
| t26 | 71.5 | [69, 74] | 71.3 [69, 73.6] | 71.3 [68.8, 73.8] |  | agree: the arithmetic of the known samples dominates. |
| t27 | 79 | [75, 83] | 79 [75, 83] | 79 [75, 83] |  | agree: same as the readers. |
| t28 | 248 | [239, 257] | 248 [240, 256] | 246 [237, 255] |  | agree: the half-gain the readers use is what the precision trade implies. |
| t29 | 466 | [457, 475] | 467 [458, 475] | 466 [457, 475] |  | agree: same as the readers. |
| t30 | 246 | [237, 255] | 246 [238, 254] | 246 [236, 256] |  | agree: same as the readers. |
| t31 | 81 | [73, 89] | 81 [73, 89] | 81 [72, 89] |  | agree: same as the readers. |

## f2-m06

No model's score depends on having seen the test problems. RL's training prompts were filtered to problems the base fails, Think-SFT's data matches the test sets in only a handful of prompts, and every gain holds on 2026 problems. So each arm's share of the base-to-RL gap belongs to its weights, not to the set: shares measured on hard328 carry over to fresh2026 once rescaled to the base and RL levels there.

Rests on: result-066c9b, result-5251c9, result-d484cb, result-f6a8bc. Forecasts 16 of 31 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t06 | 52.5 | [44, 61] | 52 [43, 60] | 51 [43, 59] |  | agree: the readers use the same share. |
| t07 | 50 | [43, 57] | 46.5 [39, 54] | 48 [41, 55] |  | disagree: the readers assume fresh2026 loses part of the share; with no exposure effect the share carries over whole, so the edit lands at RL's single. |
| t12 | 233 | [217, 249] | 232 [215, 248] | 233 [216, 249] |  | agree: same as the readers. |
| t13 | 204 | [187, 220] | 202 [183, 219] | 204 [187, 221] |  | agree: same as the readers. |
| t14 | 463 | [452, 473] | 462 [451, 472] | 463 [452, 473] |  | agree: same as the readers. |
| t15 | 459 | [447, 469] | 458 [446, 468] | 459 [447, 469] |  | agree: same as the readers. |
| t16 | 0.8 | [-5.5, 7] | 0.6 [-4.5, 5.5] | 0.9 [-6, 7.5] |  | agree: same as the readers. |
| t17 | -1.2 | [-7.5, 5] | -1.5 [-7.5, 4] | -0.9 [-7.5, 6] |  | agree: same as the readers. |
| t22 | 454.5 | [447, 461] | 453 [447, 459] | 455 [448, 462] |  | agree: same as the readers. |
| t25 | 456 | [449, 463] | 454 [448, 461] | 457 [449, 464] |  | agree: same as the readers. |
| t26 | 71.3 | [69, 73.7] | 71.3 [69, 73.6] | 71.3 [68.8, 73.8] |  | agree: arithmetic as the readers. |
| t27 | 79 | [75, 83] | 79 [75, 83] | 79 [75, 83] |  | agree: same as the readers. |
| t28 | 247 | [238, 256] | 248 [240, 256] | 246 [237, 255] |  | agree: the readers use the same ratio. |
| t29 | 466.5 | [457, 475] | 467 [458, 475] | 466 [457, 475] |  | agree: same as the readers. |
| t30 | 246 | [237, 255] | 246 [238, 254] | 246 [236, 256] |  | agree: same as the readers. |
| t31 | 83 | [75, 91] | 81 [73, 89] | 81 [72, 89] |  | disagree: scaling the hard328 cap gain by fresh2026's larger cut share gives a slightly larger vote gain than the readers' +6. |

## t01 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems does the Olmo 3 base plus Code-RL 3.1's top 8 weight directions per matrix at 1x size pass with the Code cue at T 1.0?

Unit: problems passed of 538. Cell: {"model": "Olmo-3-1025-7B base + top 8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Code - base) at 1x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": "not stated", "grader": "not stated"}

> base + Code 3.1's 8 directions at 1x, 1.5x, 2x, random at 1.5x, and Math 3.1's at 1.5x, on HumanEval+ and MBPP+ (538 problems, Code cue, T 1.0

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 348 | [325, 372] | Base + Code cue is 317 and RL-Code 401; Math top-8 at 1x closed about 2/3 of the RL gap on hard328, discounted for code, where the cue already gives most of the gain. |
| reader-2 | 350 | [322, 378] | Base Code cue 317, RL-Code 401; on math the 1x top-8 edit closed about two thirds of the hard328 gap (164->192 of 206), applied to the 84-problem code gap with a discount for code being less cap-limited. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 349 | [323, 375] | The Code cue already selects the register; the RL directions add only what lies beyond it. |
| f2-m03 | 366 | [341, 391] | Math top-8 at 1x closed 67 % of the hard328 gap; the same share of the 84-problem code gap gives 317 + 56. |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t02 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems does the Olmo 3 base plus Code-RL 3.1's top 8 weight directions per matrix at 1.5x size pass with the Code cue at T 1.0?

Unit: problems passed of 538. Cell: {"model": "Olmo-3-1025-7B base + top 8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Code - base) at 1.5x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": "not stated", "grader": "not stated"}

> base + Code 3.1's 8 directions at 1x, 1.5x, 2x, random at 1.5x, and Math 3.1's at 1.5x, on HumanEval+ and MBPP+ (538 problems, Code cue, T 1.0

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 355 | [328, 382] | On hard328 1.5x was the peak of the Math dial (203 vs 192 at 1x); assumed a similar small rise over 1x on the code pair. |
| reader-2 | 360 | [328, 391] | On math 1.5x was the peak of the dial (203 vs RL 206 on hard328, 456 vs 457 on MATH-500); assume a similar but weaker peak on code. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 357 | [328, 386] | Same as 1x plus a small rise, as on the math dial. |
| f2-m03 | 378 | [352, 404] | At 1.5x the math dial closed 93-100 % of the gap (hard328 200.25 vs 200; MATH-500 456 vs 457); allowing for some code skill outside 8 directions, about 73 % of 84. |
| f2-m04 | - |  | no forecast |
| f2-m05 | 357 | [328, 386] | Finishing pressure helps code less than math because code answers are shorter. |
| f2-m06 | - |  | no forecast |

## t03 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems does the Olmo 3 base plus Code-RL 3.1's top 8 weight directions per matrix at 2x size pass with the Code cue at T 1.0?

Unit: problems passed of 538. Cell: {"model": "Olmo-3-1025-7B base + top 8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Code - base) at 2x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": "not stated", "grader": "not stated"}

> base + Code 3.1's 8 directions at 1x, 1.5x, 2x, random at 1.5x, and Math 3.1's at 1.5x, on HumanEval+ and MBPP+ (538 problems, Code cue, T 1.0

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 345 | [308, 378] | At 2x the Math dial fell back (190 vs 203) as answers end too early; wider interval for possible decay. |
| reader-2 | 351 | [310, 388] | On math 2x removed almost all cap hits but right answers fell back (190 vs 203), so 2x lands below 1.5x, with a wider interval for possible breakage. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 348 | [310, 384] | Past the peak, early commitment costs, as on hard328. |
| f2-m03 | 365 | [330, 398] | At 2x the math dial fell back to the 1x level (190 vs 192) through early commitment; same here. |
| f2-m04 | - |  | no forecast |
| f2-m05 | 348 | [310, 384] | Too much finishing pressure costs precision, as at a=3-4 on Think-SFT. |
| f2-m06 | - |  | no forecast |

## t04 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems does the Olmo 3 base plus a random rank-8 weight edit at 1.5x size (control) pass with the Code cue at T 1.0?

Unit: problems passed of 538. Cell: {"model": "Olmo-3-1025-7B base + random rank-8 edit at 1.5x (control)", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": "not stated", "grader": "not stated"}

> base + Code 3.1's 8 directions at 1x, 1.5x, 2x, random at 1.5x, and Math 3.1's at 1.5x, on HumanEval+ and MBPP+ (538 problems, Code cue, T 1.0

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 315 | [298, 332] | Random rank-8 edits were flat to slightly below base on hard328 (158-167 vs 164); base + Code cue is 317, sampling sd about 11. |
| reader-2 | 314 | [297, 332] | Random rank-8 edits are flat at or slightly below base on every math cell (158-167 vs 164), so this is the Code-cue base 317 minus a little, plus single-sample noise. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 314 | [297, 331] | A random edit neither selects nor sharpens the register, so it gives the Code-cue base's 317 minus a little. |
| f2-m03 | 314 | [297, 331] | Random rank-8 edits were flat at every size (158-167 vs 164). |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t05 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems does the Olmo 3 base plus Math-RL 3.1's top 8 weight directions per matrix at 1.5x size pass with the Code cue at T 1.0?

Unit: problems passed of 538. Cell: {"model": "Olmo-3-1025-7B base + top 8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Math - base) at 1.5x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": "not stated", "grader": "not stated"}

> base + Code 3.1's 8 directions at 1x, 1.5x, 2x, random at 1.5x, and Math 3.1's at 1.5x, on HumanEval+ and MBPP+ (538 problems, Code cue, T 1.0

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 336 | [312, 360] | Cross-domain top-8 gave about half the in-domain gain (Code top-8 on hard328 178 vs Math 192), and Math-RL also gains on code benchmarks. |
| reader-2 | 340 | [314, 366] | Cross-reward directions transfer about half (Code top-8 on math 178 vs Math's 192), Math-RL is strong on code (LiveCodeBench 21.9 vs 24.3) and the Math cue already scores 326 on code. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 338 | [313, 363] | The Math cue works on code as well as the Code cue, so the register is shared; Math directions add some finishing. |
| f2-m03 | 345 | [320, 370] | Cross-reward directions give about half the in-domain gain (Code top-8 on math 178 vs Math 192); half of the 1.5x code gain is about +28. |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t06 (work-16773f): How many of the 136 fresh2026 competition problems does the Olmo 3 base plus 1.5x the top 8 RL-Math weight directions, with the cue, get right under a majority vote over 4 samples?

Unit: right answers of 136 (vote over 4). Cell: {"model": "Olmo-3-1025-7B base + 1.5 x top 8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Math - base)", "prompt": "opening cue", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> is it level with RL (57 vote, 50.5 single) where its size was not chosen?

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 52 | [43, 60] | The 1.5x edit matched RL single but trailed RL's vote on hard328 (214 vs 221); on fresh2026 the vote is base 38 and RL 57, so the edit should land near 52. |
| reader-2 | 51 | [43, 59] | On hard328 the edit's vote reached 214, about 76% of the way from the base's vote (192) to RL's (221); applied to fresh2026's base vote 38 and RL vote 57. |
| r5-m03-rival | 52 | [44, 60] | Theory: the top-8 Math edit puts most samples on RL's own policy, so the 1.5x edit sits near RL (vote 57 on fresh2026) but a little below it, as on hard328 where its vote was 214 against RL's 221; this scales to about 52 of 136. |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 51.5 | [43, 60] | The edit adds finishing without the derivation habit, so its vote gain stays small, as on hard328 (214 vs 221). |
| f2-m02 | - |  | no forecast |
| f2-m03 | 53 | [45, 61] | The edit matched RL's single but trailed its vote on hard328 (214 vs 221), so it lands just under RL's 57. |
| f2-m04 | 52 | [44, 60] | The edit lowers slips and misreadings less than RL does, so its vote gain over its single is RL-like but smaller. |
| f2-m05 | 51.5 | [43, 60] | Finishing pressure without the imitation's precision: the vote lands between base and RL. |
| f2-m06 | 52.5 | [44, 61] | The edit's vote closed 76 % of the base-to-RL vote gap on hard328 (192 to 214 of 221); 38 + 0.76 x 19. |

## t07 (work-16773f): What is the mean number of right answers out of 136 per single sample (averaged over 4 samples) for the Olmo 3 base plus 1.5x the top 8 RL-Math weight directions, with the cue, on fresh2026?

Unit: mean right answers of 136 per single sample (mean of 4). Cell: {"model": "Olmo-3-1025-7B base + 1.5 x top 8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Math - base)", "prompt": "opening cue", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> is it level with RL (57 vote, 50.5 single) where its size was not chosen?

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 46.5 | [39, 54] | Fewer cap hits with finished-answer precision between base (36%) and RL (43%) on fresh2026; base single 29.5, RL 50.5. |
| reader-2 | 48 | [41, 55] | On hard328 the edit's single-sample mean matched RL (200.25 vs 200.0); on fresh2026 assume about 90% of the 29.5->50.5 gap is closed. |
| r5-m03-rival | 48 | [41, 55] | Theory: the edit switches each sample into RL's policy (with the cue, the plain-base share drops out), so one sample sits near RL's 50.5 on fresh2026, as the 1.5x edit matched RL on hard328 (200.25 vs 200) and MATH-500 (456 vs 457); a little below RL on these hardest problems. |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 47.5 | [40, 55] | Finishing more answers at near-base precision gives a single-sample score close to RL's 50.5, a little below. |
| f2-m02 | - |  | no forecast |
| f2-m03 | 49 | [42, 56] | The 1.5x edit matched RL's single on hard328 and MATH-500; on fresh2026 it should come close to RL's 50.5. |
| f2-m04 | 47.5 | [40, 55] | Single samples carry both slips and misreadings; between base 29.5 and RL 50.5. |
| f2-m05 | 47.5 | [40, 55] | Finishes about as often as RL at slightly lower precision. |
| f2-m06 | 50 | [43, 57] | The edit's single closed 100 % of the gap on hard328 (200.25 vs RL 200.0 vs base 158.5) and on MATH-500; carried over, fresh2026 gives RL's 50.5. |

## t08 (work-f8ecb6): Averaged over 4 samples, how many of the 500 MATH-500 problems does the step-100 checkpoint of Olmo-3.1 RL-Zero-Math get right with the plain prompt at T 1.0 under grader v3?

Unit: mean right answers of 500 per sample (stored sample 0 plus 3 new). Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math step 100 checkpoint", "prompt": "plain", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": 4, "grader": "v3"}

> 3 more samples of step-100 plain, step-100 cue, step-400 plain (MATH-500, T 1.0, v3)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 416 | [409, 423] | Stored sample 0 is 418; new samples regress slightly; cued-base samples spread 405-418. |
| reader-2 | 416 | [409, 423] | Stored sample 0 is 418; three new samples pull it toward the true rate, which is slightly lower (the cued base's samples spread 405-418). |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 420 | [413, 427] | Step 100 already opens itself, so its plain (418) and cue (427) cells are nearly two draws of one model; the pooled level is about 421, minus a bit for the non-opening answers. |
| f2-m03 | 417 | [410, 424] | At step 100 the finishing directions have barely formed (0.03 % of weight norm), so the score sits near the stored 418. |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t09 (work-f8ecb6): Averaged over 4 samples, how many of the 500 MATH-500 problems does the step-100 checkpoint of Olmo-3.1 RL-Zero-Math get right with the opening cue at T 1.0 under grader v3?

Unit: mean right answers of 500 per sample (stored sample 0 plus 3 new). Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math step 100 checkpoint", "prompt": "opening cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": 4, "grader": "v3"}

> 3 more samples of step-100 plain, step-100 cue, step-400 plain (MATH-500, T 1.0, v3)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 424 | [416, 431] | Stored sample 0 is 427, with slight regression toward the plain step-100 level. |
| reader-2 | 423 | [415, 430] | Stored cue sample 427 pulled back toward the mean; the cue added +1.8 points [-1.2, 4.8] at step 100. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 424 | [417, 431] | Pooled step-100 level about 421 plus the small cue effect on the ~23 % of answers that do not open themselves. |
| f2-m03 | 424 | [416, 431] | Stored 427 with regression. |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t10 (work-f8ecb6): Averaged over 4 samples, how many of the 500 MATH-500 problems does the step-400 checkpoint of Olmo-3.1 RL-Zero-Math get right with the plain prompt at T 1.0 under grader v3?

Unit: mean right answers of 500 per sample (stored sample 0 plus 3 new). Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math step 400 checkpoint", "prompt": "plain", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": 4, "grader": "v3"}

> 3 more samples of step-100 plain, step-100 cue, step-400 plain (MATH-500, T 1.0, v3)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 434 | [427, 441] | Stored sample 0 is 436; single samples vary by about 6 problems. |
| reader-2 | 434 | [427, 441] | Stored step-400 plain sample 436 with slight shrinkage; between step 100 (418) and final RL (456-463). |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 434 | [427, 441] | At step 400 the cue changes nothing (-1.0), so plain 436 and cue 431 pool to about 434. |
| f2-m03 | 434 | [427, 441] | Stored 436 with regression; directions still growing. |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t11 (work-f8ecb6): Over 4 samples each on MATH-500 at T 1.0 with grader v3, by how many percentage points does the plain step-100 RL-Zero-Math checkpoint beat (or trail) the untrained base with the opening cue?

Unit: percentage points (step-100 plain minus cued base, 4 samples each). Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math step 100 checkpoint (plain) vs Olmo-3-1025-7B base (opening cue)", "prompt": "plain (step 100) vs opening cue (base)", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": 4, "grader": "v3"}

> so the step-100 vs cued-base difference has a 4-sample interval

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 1.1 | [-0.7, 2.9] | Step-100 plain mean of about 416 vs the cued base's 4-sample mean of 410.5. |
| reader-2 | 1.1 | [-0.8, 3] | Step-100 4-sample mean of about 416/500 (83.2%) against the cued base's stored 4-sample mean of 410.5 (82.1%). |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 1.9 | [0.3, 3.5] | Step 100 is the cued base's register plus about 2 points of sharpening (finished-answer accuracy +4.6 at T 0.6): (420 - 410.5)/5. |
| f2-m03 | 1.2 | [-0.7, 3] | Step 100 adds little finishing over the cue. |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t12 (work-8b2ec9): How many of the 328 harder problems does Think-SFT get right in its own ChatML <think> chat format at T 1.0 with a 32,768-token cap, one sample, grader v3?

Unit: right answers of 328. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "own ChatML chat template with <think> (no base cue)", "set": "hard328", "n": 328, "sampling": "T 1.0; top-p not stated; cap 32,768", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 232 | [215, 248] | Think-SFT's own chat format should be about level with the cue run's 230 at a 32k cap; the native format may help a little. |
| reader-2 | 233 | [216, 249] | The raw-template + cue run scored 230 at cap 32,768; the native ChatML format is what the model was trained on, so it should be about level or slightly better. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 233 | [217, 249] | The derivation habit lives in the weights, so the native template gives the cue run's 230 at 32k plus a little from being in-distribution. |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | 233 | [217, 249] | No RL change in this cell, so the cap behaviour equals the cue run's. |
| f2-m06 | 233 | [217, 249] | 6 of 328 overlap; exposure plays no part, so the score is the cue run's. |

## t13 (work-8b2ec9): How many of the 328 harder problems does Think-SFT get right in its own ChatML <think> chat format at T 1.0 when the same answers are scored at a 16,384-token cap, one sample, grader v3?

Unit: right answers of 328. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "own ChatML chat template with <think> (no base cue)", "set": "hard328", "n": 328, "sampling": "T 1.0; top-p not stated; generated at cap 32,768, scored at 16,384", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 202 | [183, 219] | The cue run scored 207 at 16k; the native <think> format may reason longer, so more answers get cut at 16k. |
| reader-2 | 204 | [187, 221] | The cue run scored 207 at 16,384; native <think> traces may run a bit longer, so slightly more answers get cut. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 204 | [187, 220] | Same answers at 16k: the cut samples are unfinished work that scores 0, as in the cue run's 207. |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | 204 | [187, 220] | Same answers at 16k; cut samples count 0. |
| f2-m06 | 204 | [187, 220] | Same answers at 16k. |

## t14 (work-8b2ec9): How many of the 500 MATH-500 problems does Think-SFT get right in its own ChatML <think> chat format at T 1.0 with a 32,768-token cap, one sample, grader v3?

Unit: right answers of 500. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "own ChatML chat template with <think> (no base cue)", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; cap 32,768", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 462 | [451, 472] | Think-SFT cue singles score 454-462 at 16k; a 32k cap adds a few. |
| reader-2 | 463 | [452, 473] | Think-SFT cue singles score 454-462 at a 16,384 cap; at 32,768 some of its roughly 25 cap hits finish, and the native format is about level. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 466 | [457, 475] | About 22-25 cut MATH-500 samples are unfinished derivations on easier problems; at 32k about 40 % of them finish right, so roughly +8 over the 16k score. |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | 463 | [452, 473] | Few MATH-500 samples are cut; 32k adds a few. |
| f2-m06 | 463 | [452, 473] | 29 MATH-500 overlaps give no extra; 32k adds a few. |

## t15 (work-8b2ec9): How many of the 500 MATH-500 problems does Think-SFT get right in its own ChatML <think> chat format at T 1.0 when the same answers are scored at a 16,384-token cap, one sample, grader v3?

Unit: right answers of 500. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "own ChatML chat template with <think> (no base cue)", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; generated at cap 32,768, scored at 16,384", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 458 | [446, 468] | Same answers scored at 16k; close to the stored cue singles. |
| reader-2 | 459 | [447, 469] | The same answers scored at 16,384 should fall in the cue singles' range of 454-462. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 458.5 | [447, 469] | At 16k the native run should match the cue singles (454-462). |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | 459 | [447, 469] | Cue singles' range. |
| f2-m06 | 459 | [447, 469] | Cue singles' range. |

## t16 (work-8b2ec9): On the 328 harder problems at T 1.0 with a 32,768-token cap, how many percentage points does Think-SFT in its own ChatML <think> format score above or below Think-SFT with the raw template and cue (230 of 328), paired by problem?

Unit: percentage points (native format minus cue run at 230/328). Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "own ChatML <think> template vs raw template + base cue", "set": "hard328", "n": 328, "sampling": "T 1.0; top-p not stated; cap 32,768", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 0.6 | [-4.5, 5.5] | Native about 232 vs the cue run's 230 of 328; paired single-sample noise is about 3 points. |
| reader-2 | 0.9 | [-6, 7.5] | Paired single-sample difference against 230/328; seed noise is about 2 points and the format effect is unknown, centred slightly positive. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 1 | [-5, 6.5] | Native minus cue at 32k is near zero because the template does not touch the derivation habit. |
| f2-m02 | 0.5 | [-5, 6] | The cue and the native template select the same register in Think-SFT, so the paired difference is near zero. |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | 0.8 | [-5.5, 7] | The template does not change the update. |
| f2-m06 | 0.8 | [-5.5, 7] | Paired difference near zero. |

## t17 (work-8b2ec9): On the 328 harder problems at T 1.0 scored at a 16,384-token cap, how many percentage points does Think-SFT in its own ChatML <think> format score above or below Think-SFT with the raw template and cue (207 of 328), paired by problem?

Unit: percentage points (native format minus cue run at 207/328). Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "own ChatML <think> template vs raw template + base cue", "set": "hard328", "n": 328, "sampling": "T 1.0; top-p not stated; generated at cap 32,768, scored at 16,384", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | -1.5 | [-7.5, 4] | Native about 202 vs 207 at 16k, from longer native reasoning. |
| reader-2 | -0.9 | [-7.5, 6] | Paired difference against 207/328 at 16,384; native traces may be cut slightly more often. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | -1 | [-7.5, 5] | At 16k, native traces may run slightly longer, so a few more get cut. |
| f2-m02 | -1 | [-7.5, 5] | Same register; any difference comes from trace length at the 16k cut. |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | -1.2 | [-7.5, 5] | Slightly more cuts at 16k. |
| f2-m06 | -1.2 | [-7.5, 5] | Paired difference near zero, slightly negative from cuts. |

## t18 (work-60f040): How many of the 500 MATH-500 problems does the untrained Olmo 3 base with the opening cue get right at T 1.0 under a majority vote over 5 samples (grader v3)?

Unit: right answers of 500 (majority vote over 5). Cell: {"model": "Olmo-3-1025-7B base", "prompt": "opening cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0, same cell as the stored 4 samples; top-p and cap not stated", "samples": 5, "grader": "v3"}

> Vote over k = 1..12 samples of the untrained cued base on MATH-500

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 448 | [442, 454] | The stored vote over 4 is 446 and pass@4 is 467; the vote curve flattens, as in Wang's majority@k. |
| reader-2 | 450 | [443, 457] | Vote over 4 is 446 and over 4 after restart 450; an odd k breaks ties, so k=5 is about +4. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 449 | [442, 456] | Rival's claim that a base-only vote over more samples recovers part of the sharpening share, reaching 456 at 9 samples, interpolated from the stored vote over 4 (446): k=5 adds about a third of the 4-to-9 gain. |
| r6-m06 | 449 | [442, 456] | The theory's in-scope cell (cued base, MATH-500, T 1.0, untruncated, v3) puts single samples at 405-418. Head-drawn errors vary from sample to sample but don't vanish, so votes keep climbing slowly from the stored vote over 4 of 446 (pass@4 467). Vote over 5 is about +3. |
| r7-m05 | 448 | [441, 455] | Cued base MATH-500 T 1.0 is the theory's scope; it says misreads/slips sit near the mode and get rewritten when the model tries again (6 of 11 slips repeated), so vote gains flatten fast: one sample past the stored vote over 4 (446) adds about 2. |
| r7-m08 | 450 | [443, 456] | no_intervention: selection among base samples is the only base-side veto (vote over 4 = 446); more samples veto more of the base's chance slips/misreads, so vote over 5 adds a few problems above 446. |
| r7-m11 | 448 | [441, 455] | Statement: under the one shared cue, wrong samples of the cued base land on the same value, so extra cued samples join existing wrong groups and the vote climbs only slowly from the stored vote over 4 (446, pass@4 467); a fifth sample adds about 2. |
| f2-m01 | - |  | no forecast |
| f2-m02 | 449 | [442, 456] | Selecting the register is already done; votes only remove the rest of the sampling noise. |
| f2-m03 | - |  | no forecast |
| f2-m04 | 450 | [444, 456] | An odd fifth sample breaks the 2-2 ties left by chance slips: about +4 over 446. |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t19 (work-60f040): How many of the 500 MATH-500 problems does the untrained Olmo 3 base with the opening cue get right at T 1.0 under a majority vote over 6 samples (grader v3)?

Unit: right answers of 500 (majority vote over 6). Cell: {"model": "Olmo-3-1025-7B base", "prompt": "opening cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0, same cell as the stored 4 samples; top-p and cap not stated", "samples": 6, "grader": "v3"}

> Vote over k = 1..12 samples of the untrained cued base on MATH-500

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 449 | [443, 455] | Even k adds ties; gains are slow above 446. |
| reader-2 | 451 | [444, 458] | The vote curve flattens (Wang majority@4->@8: +2.5 points); pass@4 is 467 and 33 problems are 0 of 4. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 450 | [443, 457] | Same sharpening-recovery curve from 446 (k=4) to the theory's 456 (k=9); even k loses a little to ties, so k=6 sits only slightly above k=5. |
| r6-m06 | 449 | [442, 457] | Same theory base level (405-418 per sample, errors drawn from the head) with the stored vote over 4 of 446. An even k loses some problems to tie-breaks, so this is about the same as vote over 5. |
| r7-m05 | 448 | [441, 456] | Same plateau from mode-sitting errors; an even k adds ties, so it stays level with k=5 near the stored 446 vote over 4. |
| r7-m08 | 450 | [443, 457] | Same base-side veto by selection as in no_intervention, starting from vote over 4 = 446; an even k adds ties, so it stays level with k=5. |
| r7-m11 | 449 | [442, 456] | Same mechanism: agreeing wrong groups under the fixed opening keep the vote well below the independent-slip curve (Wang maj@8 is +2.5 pts over maj@4), so +3 over 446 at k=6. |
| f2-m01 | - |  | no forecast |
| f2-m02 | 450 | [443, 457] | Slow rise from 446. |
| f2-m03 | - |  | no forecast |
| f2-m04 | 452 | [445, 458] | Slips are independent, so problems at 2/4-3/4 keep converting. |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t20 (work-60f040): How many of the 500 MATH-500 problems does the untrained Olmo 3 base with the opening cue get right at T 1.0 under a majority vote over 7 samples (grader v3)?

Unit: right answers of 500 (majority vote over 7). Cell: {"model": "Olmo-3-1025-7B base", "prompt": "opening cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0, same cell as the stored 4 samples; top-p and cap not stated", "samples": 7, "grader": "v3"}

> Vote over k = 1..12 samples of the untrained cued base on MATH-500

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 451 | [445, 457] | Slow vote growth toward a plateau near 455-460. |
| reader-2 | 453 | [446, 460] | Interpolated on a slowly rising vote curve between 446 at k=4 and a plateau near 457. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 453 | [446, 460] | Same sharpening-recovery curve toward the theory's 456 at k=9; k=7 is about 70 % of the way from 446. |
| r6-m06 | 451 | [444, 458] | Same theory base level and stored vote over 4 of 446. Diminishing gains, like the cued Olmo majority curve on the board (88.5 % at 4, 91 % at 8), put 7 votes about +5. |
| r7-m05 | 451 | [444, 458] | Errors near the mode are correlated across samples (the theory's mode claim), so the vote saturates near 450-453 rather than climbing to the independent-slip value; the board's vote is 10 problems under the independent prediction. |
| r7-m08 | 452 | [445, 458] | Selection vetoes the base's reliability errors (statement; f39ba8 reliability share 0.63), so the vote keeps climbing slowly from 446. |
| r7-m11 | 450 | [443, 457] | Wrong values set by the shared prompt-plus-opening context repeat across samples, so the vote nears a plateau about 4 above 446 and well below pass@4 467. |
| f2-m01 | - |  | no forecast |
| f2-m02 | 452 | [445, 459] | Slow rise toward a plateau. |
| f2-m03 | - |  | no forecast |
| f2-m04 | 454 | [448, 460] | By 7 samples most slip-only problems have a right majority. |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t21 (work-60f040): How many of the 500 MATH-500 problems does the untrained Olmo 3 base with the opening cue get right at T 1.0 under a majority vote over 8 samples (grader v3)?

Unit: right answers of 500 (majority vote over 8). Cell: {"model": "Olmo-3-1025-7B base", "prompt": "opening cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0, same cell as the stored 4 samples; top-p and cap not stated", "samples": 8, "grader": "v3"}

> Vote over k = 1..12 samples of the untrained cued base on MATH-500

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 452 | [446, 458] | Wang's +2.5 points from 4 to 8 votes, compressed here because the base starts higher. |
| reader-2 | 454 | [447, 461] | Wang's majority@8 is about 2.5 points above @4, but the vote runs about 10 below the independent-slip prediction, so somewhat less than that here. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 454 | [447, 461] | Same sharpening-recovery curve toward the theory's 456 at k=9; k=8 is just below the k=9 value because of even-k ties. |
| r6-m06 | 452 | [445, 459] | Same theory base level and stored vote over 4 of 446. The majority curve gains about 2.5 points from 4 to 8, damped because the base solves 33 problems in 0 of 4 samples. |
| r7-m05 | 451 | [444, 458] | Plateau set by the theory's mode-sitting misreads/slips; even k, no gain over k=7. |
| r7-m08 | 452 | [445, 459] | Selection-veto climb from 446; the 33 problems with 0 of 4 base right are where a veto cannot create a path (prediction 3), so gains flatten. |
| r7-m11 | 451 | [444, 458] | Plateau implied by context-fixed agreeing wrong groups: k=8 is about 5 above the vote over 4, short of the independent-slip gain of about 12. |
| f2-m01 | 453.5 | [447, 460] | The base lacks the habit: its wrong answers include asserted guesses, so its vote flattens well below what Think-SFT's vote reaches. |
| f2-m02 | 453 | [446, 460] | Slow rise toward a plateau. |
| f2-m03 | - |  | no forecast |
| f2-m04 | 455 | [449, 461] | Near the plateau set by problems with a repeated misreading. |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t22 (work-60f040): How many of the 500 MATH-500 problems does the untrained Olmo 3 base with the opening cue get right at T 1.0 under a majority vote over 9 samples (grader v3)?

Unit: right answers of 500 (majority vote over 9). Cell: {"model": "Olmo-3-1025-7B base", "prompt": "opening cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0, same cell as the stored 4 samples; top-p and cap not stated", "samples": 9, "grader": "v3"}

> vote over 9 = 456 [449, 462] of 500

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 453 | [447, 459] | Near the bottom of the theory's 449-462 prediction; the vote has run below the independent-slip prediction. |
| reader-2 | 455 | [448, 462] | Close to the theory's forecast of 456 [449, 462]; the curve is flattening. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 456 | [449, 462] | The rival states directly that the base-only vote over more samples gives 456/500 (filed as vote over 9 = 456 [449, 462]). |
| r6-m06 | 453 | [446, 460] | Head-drawn errors still vary across samples, so votes keep climbing slowly from 446 at 4 samples. That puts vote over 9 near 453, a little under the earlier forecast of 456. |
| r7-m05 | 452 | [445, 459] | The theory's correlated, mode-level errors cap the vote a little under the 456 the account predicted for vote over 9; the plateau sits near 452. |
| r7-m08 | 453 | [446, 460] | Selection veto saturates below RL's single sample because 'installs no replacement tokens': problems with no base path stay wrong, so this lands near the low end of 456 [449, 462]. |
| r7-m11 | 451 | [444, 459] | Agreeing wrong groups under one opening cap the vote, so k=9 lands near 451, the low half of the 456 [449, 462] that independent-slip voting predicts. |
| f2-m01 | - |  | no forecast |
| f2-m02 | 454 | [447, 461] | Plateau region. |
| f2-m03 | - |  | no forecast |
| f2-m04 | 456 | [450, 462] | Plateau: the theory's 456 for vote over 9. |
| f2-m05 | - |  | no forecast |
| f2-m06 | 454.5 | [447, 461] | The 9 flagged MATH-500 problems give no recall bonus; the vote follows the plateau. |

## t23 (work-60f040): How many of the 500 MATH-500 problems does the untrained Olmo 3 base with the opening cue get right at T 1.0 under a majority vote over 10 samples (grader v3)?

Unit: right answers of 500 (majority vote over 10). Cell: {"model": "Olmo-3-1025-7B base", "prompt": "opening cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0, same cell as the stored 4 samples; top-p and cap not stated", "samples": 10, "grader": "v3"}

> Vote over k = 1..12 samples of the untrained cued base on MATH-500

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 453 | [447, 460] | Plateau; 33 problems had the base wrong on all 4 samples. |
| reader-2 | 456 | [448, 463] | Plateau region; even k can lose a little to ties. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 456 | [449, 463] | Past k=9 the theory's sharpening recovery is only partial, so the curve levels off at the theory's 456 (even k gets no gain from ties). |
| r6-m06 | 453 | [446, 461] | Same theory base level and the vote curve from 446 at 4 samples, nearly flat by 10. Even-k tie-breaks keep it level with vote over 9. |
| r7-m05 | 452 | [445, 459] | Plateau from mode-level errors that resampling repeats; even k, level with k=9. |
| r7-m08 | 453 | [446, 460] | Plateau from the selection veto: the reliability problems are mostly fixed by k=9, and the capability problems (0/4 base) stay unreachable. |
| r7-m11 | 452 | [444, 460] | Under the theory, more same-opening samples mostly add to wrong groups that are already there, so the vote stays near its plateau of about 452. |
| f2-m01 | - |  | no forecast |
| f2-m02 | 455 | [448, 462] | Plateau region. |
| f2-m03 | - |  | no forecast |
| f2-m04 | 457 | [450, 463] | Plateau; even k adds ties. |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t24 (work-60f040): How many of the 500 MATH-500 problems does the untrained Olmo 3 base with the opening cue get right at T 1.0 under a majority vote over 11 samples (grader v3)?

Unit: right answers of 500 (majority vote over 11). Cell: {"model": "Olmo-3-1025-7B base", "prompt": "opening cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0, same cell as the stored 4 samples; top-p and cap not stated", "samples": 11, "grader": "v3"}

> Vote over k = 1..12 samples of the untrained cued base on MATH-500

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 454 | [448, 460] | Plateau near 455. |
| reader-2 | 456 | [449, 463] | Plateau about 10 below pass@4; problems the base never solves cap the vote. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 457 | [450, 464] | Levelling sharpening-recovery curve: one point above the theory's 456 at k=9; reach problems (kB=0, share about 0.1) stay out of reach. |
| r6-m06 | 454 | [447, 461] | Same theory base level and the vote curve from 446, flattening toward the base's pass@k ceiling (467 at 4). |
| r7-m05 | 453 | [446, 460] | Saturation implied by the mode claim: a slow +1 over k=9, well under pass@4 467. |
| r7-m08 | 454 | [447, 461] | Plateau of the base-side veto (selection) below RL single 456-463, because a veto adds no new solution routes. |
| r7-m11 | 452 | [444, 460] | Context-fixed wrong values keep the vote flat past k of about 8, so k=11 stays about 452. |
| f2-m01 | - |  | no forecast |
| f2-m02 | 455 | [448, 462] | Plateau region. |
| f2-m03 | - |  | no forecast |
| f2-m04 | 457 | [451, 463] | Plateau about 10 below pass@4, set by the 33 problems at 0 of 4 and repeated wrong values. |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t25 (work-60f040): How many of the 500 MATH-500 problems does the untrained Olmo 3 base with the opening cue get right at T 1.0 under a majority vote over 12 samples (grader v3)?

Unit: right answers of 500 (majority vote over 12). Cell: {"model": "Olmo-3-1025-7B base", "prompt": "opening cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0, same cell as the stored 4 samples; top-p and cap not stated", "samples": 12, "grader": "v3"}

> Vote over k = 1..12 samples of the untrained cued base on MATH-500

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 454 | [448, 461] | Plateau near 455. |
| reader-2 | 457 | [449, 464] | Plateau; Wang's majority@16 is only about 2 points above @8. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 457 | [450, 464] | Curve flat after the theory's 456 at k=9: only part of sharpening can be recovered, and reach and budget problems stay lost to a base-only vote. |
| r6-m06 | 455 | [447, 462] | Same theory base level and the vote curve from 446 at 4 samples. It plateaus around 455, below one RL sample (456-463). |
| r7-m05 | 453 | [446, 460] | Plateau from mode-level misreads/slips; even k, level with k=11. |
| r7-m08 | 454 | [447, 461] | Plateau of the base-side veto (selection) about 8 problems above vote over 4 = 446, capped by the base's no-path problems (prediction 3). |
| r7-m11 | 453 | [445, 461] | The cap from agreeing wrong groups (the mechanism's explanation of the vote shortfall in result-e41d94) holds k=12 about 7 above the vote over 4, below the independent prediction. |
| f2-m01 | 456 | [449, 463] | The plateau is set by problems where the base asserts a repeated wrong value; extra samples add little. |
| f2-m02 | 456 | [449, 463] | Plateau region. |
| f2-m03 | - |  | no forecast |
| f2-m04 | 458 | [451, 464] | Plateau; the new samples ran at 85.7 % on the finished shard, slightly above the stored ones, which lifts the plateau a point. |
| f2-m05 | - |  | no forecast |
| f2-m06 | 456 | [449, 463] | Plateau. |

## t26 (work-8b4030): Averaged over its 4 samples (three already at 69, 70, 75), how many of the 136 fresh2026 problems does Think-SFT plus twice the RL-Math weight change get right per sample?

Unit: mean right answers of 136 per single sample (mean of 4). Cell: {"model": "allenai/Olmo-3-7B-Think-SFT + 2 x (Olmo-3.1-7B-RL-Zero-Math - Olmo-3-1025-7B base)", "prompt": "not stated", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> fresh2026 (136 problems, 4 samples, seeds of SPEC_fresh)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 71.3 | [69, 73.6] | Three samples are known (69, 70, 75); a fourth near 71 gives a mean near 71.3. |
| reader-2 | 71.3 | [68.8, 73.8] | Three samples are known (69, 70, 75); the fourth is forecast at about 71 ± 6, and the mean moves by a quarter of that. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 71.3 | [69, 73.7] | Three samples are known; the fourth is one more draw of the same model. |
| f2-m02 | - |  | no forecast |
| f2-m03 | 71.3 | [69, 73.7] | Three samples known; the fourth is one more draw. |
| f2-m04 | 71.3 | [69, 73.7] | Fourth sample is one more independent draw. |
| f2-m05 | 71.5 | [69, 74] | a=2 cuts cap hits (63 to 47 %) at a precision cost; the fourth sample is like the other three. |
| f2-m06 | 71.3 | [69, 73.7] | Three samples known. |

## t27 (work-8b4030): How many of the 136 fresh2026 problems does Think-SFT plus twice the RL-Math weight change get right under a majority vote over 4 samples?

Unit: right answers of 136 (vote over 4). Cell: {"model": "allenai/Olmo-3-7B-Think-SFT + 2 x (Olmo-3.1-7B-RL-Zero-Math - Olmo-3-1025-7B base)", "prompt": "not stated", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> fresh2026 (136 problems, 4 samples, seeds of SPEC_fresh)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 79 | [75, 83] | The vote over 3 was 78; Think-SFT gained only 1 going from vote-3 to vote-4. |
| reader-2 | 79 | [75, 83] | Vote over 3 is 78; a fourth sample moves the vote by about 1 (Think-SFT went 74 to 75). |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 79 | [75, 83] | The RL change makes the transplant finish more answers with less of the derivation habit, so a fourth vote adds about 1. |
| f2-m02 | - |  | no forecast |
| f2-m03 | 79 | [75, 83] | One more vote adds about 1. |
| f2-m04 | 79 | [75, 83] | One more sample converts a few slip-only 1-1-1 splits and adds some ties. |
| f2-m05 | 79 | [75, 83] | Lower precision gives a small vote gain per added sample. |
| f2-m06 | 79 | [75, 83] | One more vote adds about 1. |

## t28 (work-8b4030): How many of the 328 harder problems does Think-SFT plus twice the RL-Math weight change get right under a majority vote over 4 samples (two stored samples at 234 and 229 plus two new ones)?

Unit: right answers of 328 (vote over 4). Cell: {"model": "allenai/Olmo-3-7B-Think-SFT + 2 x (Olmo-3.1-7B-RL-Zero-Math - Olmo-3-1025-7B base)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated (new samples at seeds 3,200,000 and 3,300,000)", "samples": 4, "grader": "not stated"}

> hard328 samples 3-4 for the vote over 4

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 248 | [240, 256] | Singles are about 231; its vote gain should be about half of Think-SFT's +32, because it finishes more answers and more of them wrong. |
| reader-2 | 246 | [237, 255] | Singles 234 and 229; with fewer cap hits than Think-SFT the vote gain is about 5 points (as on fresh2026, 71 -> 78), not Think-SFT's +32. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 247 | [238, 256] | The transplant keeps part of the habit (precision ~81 %, 44 cap hits), so its vote gain is about half of Think-SFT's +32. |
| f2-m02 | - |  | no forecast |
| f2-m03 | 247 | [238, 256] | The full RL change brings its finishing directions, so the transplant finishes more and its vote gain is smaller than Think-SFT's. |
| f2-m04 | 247 | [238, 256] | Half of Think-SFT's vote gain, since the transplant finishes more wrong answers that recur. |
| f2-m05 | 248 | [239, 257] | Precision about 81 % with 44 cap hits: vote gain about half of Think-SFT's +32 on singles of about 231. |
| f2-m06 | 247 | [238, 256] | On fresh2026 the transplant's vote gain was half of Think-SFT's; the same share on hard328 gives singles 231 + 16. |

## t29 (work-8b4030): How many of the 500 MATH-500 problems does Think-SFT plus twice the RL-Math weight change get right in one sample?

Unit: right answers of 500. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT + 2 x (Olmo-3.1-7B-RL-Zero-Math - Olmo-3-1025-7B base)", "prompt": "not stated", "set": "MATH-500", "n": 500, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> MATH-500 1 sample

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 467 | [458, 475] | a=1 scored 467 on MATH-500; Think-SFT singles 457-462. |
| reader-2 | 466 | [457, 475] | a=1 scored 467 on MATH-500 and Think-SFT cue singles 454-462; a=2 peaked on hard328, so it lands about level with a=1. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 466.5 | [457, 475] | On MATH-500 few samples are cut, so the transplant scores like a=1 (467). |
| f2-m02 | - |  | no forecast |
| f2-m03 | 466.5 | [457, 475] | On MATH-500 finishing is not the limit, so a=2 is about level with a=1 (467). |
| f2-m04 | 466.5 | [457, 475] | Single sample, level with a=1. |
| f2-m05 | 466 | [457, 475] | MATH-500 is rarely cap-limited for Think-SFT, so more finishing pressure adds little over a=1 (467). |
| f2-m06 | 466.5 | [457, 475] | Level with a=1. |

## t30 (work-dc9359): How many of the 328 harder problems does Think-SFT with the cue get right under a majority vote over 4 samples when the token cap is 32,768?

Unit: right answers of 328 (vote over 4). Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "opening cue", "set": "hard328", "n": 328, "sampling": "not stated; token cap 32,768", "samples": 4, "grader": "not stated"}

> Think-SFT + cue vote over 4 at token cap 32,768 on hard328

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 246 | [238, 254] | The 16k vote is 241 and the 32k single is 230 (vs 207); answers that finish late add some right votes, but wrong late answers also vote now. |
| reader-2 | 246 | [236, 256] | The 16k vote is 241, the 32k single is 230 vs 207 at 16k, and the spec's simulation gives 240-254; answers that hit the cap now finish and cast votes, some of them right. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 249 | [240, 258] | At 32k cut samples finish, about 25 % right; late wrong answers are derived and rarely agree, so problems that had no vote gain about 8-10 and lose about 2 to late wrong pluralities. |
| f2-m02 | - |  | no forecast |
| f2-m03 | 246 | [237, 256] | Without RL's finishing directions, extra budget is the only way Think-SFT finishes; the readers' account of it holds. |
| f2-m04 | 246 | [237, 255] | Late answers bring both right answers and new wrong votes; net a few above 241. |
| f2-m05 | 246 | [237, 255] | A larger budget finishes cut samples the way the RL change does, but keeps imitation precision on them only partly. |
| f2-m06 | 246 | [237, 255] | Spec simulation and the 32k single. |

## t31 (work-dc9359): How many of the 136 fresh2026 problems does Think-SFT with the cue get right under a majority vote over 4 samples when the token cap is 32,768?

Unit: right answers of 136 (vote over 4). Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "opening cue", "set": "fresh2026", "n": 136, "sampling": "not stated; token cap 32,768", "samples": 4, "grader": "not stated"}

> fresh2026 (4 samples), each answer scored at 16,384 and 32,768

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 81 | [73, 89] | The 16k vote is 75 with 46% cap hits; at 32k, about a fifth of cut answers finish right, as on hard328. |
| reader-2 | 81 | [72, 89] | The 16k vote is 75 with 46% cap hits; doubling the cap finishes most of those (on hard328, +23 right of 93 cut), so the vote gains about 6. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 84 | [76, 92] | 46 % cap hits at 16k are unfinished work; at 32k about 20-25 % of them finish right, which lifts singles by about 10 and the vote by about 9 over 75. |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | 81 | [73, 89] | Finishing cut samples adds right votes on problems with no answer at 16k. |
| f2-m05 | 81 | [73, 89] | Same trade on fresh2026. |
| f2-m06 | 83 | [75, 91] | On hard328 32k lifted Think-SFT's single by 7 points with 29 % cut; fresh2026 has 46 % cut and the same habit, so about 1.5 times the gain carries to the vote. |
