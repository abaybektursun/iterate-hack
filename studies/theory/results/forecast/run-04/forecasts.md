# Forecasts, run-04

Board snapshot 2026-11-15T16:32:52 UTC, written 2026-11-15T16:43:39 UTC. 31 targets; forecasters reader-1, reader-2, r5-m03-rival, r6-account-rival, r6-m06, r7-m05, r7-m08, r7-m11, f2-m01, f2-m02, f2-m03, f2-m04, f2-m05, f2-m06.


Lens of the mechanisms: sampling: temperature, top-p, entropy of the next-token distribution, what a vote over samples adds


## f2-m01

At T 1.0 / top-p 1.0 the cued base's wrong final answers are spread over many values (high answer-level entropy), while its right answers coincide. A plurality vote therefore picks the right value even when it is drawn in only 25-40 % of samples, and each added sample keeps resolving such problems until only near-zero-p problems remain. Long late answers (past 16k tokens) are also scattered when wrong, so finishing them adds right votes without creating wrong majorities.

Rests on: result-40ed3b, result-5c961a, result-e41d94, result-818c20, result-5251c9. Forecasts 17 of 31 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t06 | 53 | [45, 61] | 52 [44, 60] | 52 [43, 61] |  | agree: the mechanism gives the readers' 52 within a point. |
| t07 | 46.5 | [40, 53] | 47 [40, 54] | 46 [39, 53] |  | agree: no vote is involved, so the readers' 46-47 stands. |
| t16 | 450 | [445, 455] | 449 [443, 455] | 449 [443, 455] |  | agree: the readers' 449 is the same tie-breaking step. |
| t17 | 450 | [445, 456] | 450 [443, 456] | 449 [443, 456] |  | agree: same as the readers' 449-450. |
| t18 | 453 | [447, 459] | 452 [445, 458] | 451 [445, 457] |  | agree: close to the readers' 451-452. |
| t19 | 454 | [448, 460] | 452 [446, 459] | 451 [445, 458] |  | agree: within 2 of the readers' 451-452. |
| t20 | 455.5 | [450, 461] | 454 [447, 460] | 452 [446, 459] |  | agree: the readers' 452-454 sit inside the interval, slightly lower. |
| t21 | 456 | [450, 462] | 454 [447, 461] | 452 [446, 459] |  | disagree: readers put a plateau at 452-454 from correlated failures, but correlation only sets the zero-p floor, not the tie set that keeps resolving. |
| t22 | 457 | [451, 463] | 455 [448, 461] | 453 [446, 460] |  | disagree: readers plateau at 453-455; scattered wrong answers keep feeding the vote. |
| t23 | 457.5 | [452, 463] | 455 [448, 462] | 453 [446, 460] |  | disagree: readers stop at 453-455; the mechanism keeps the slow rise to about 457. |
| t24 | 79 | [75, 83] | 79 [73, 85] | 79 [72, 86] |  | agree: same as the readers' 79. |
| t25 | 71 | [63, 79] | 71 [63, 79] | 71 [62, 80] |  | agree: readers' 71. |
| t26 | 231 | [220, 242] | 231 [220, 242] | 231 [219, 243] |  | agree: readers' 231. |
| t27 | 231 | [220, 242] | 231 [220, 242] | 231 [219, 243] |  | agree: readers' 231. |
| t28 | 248 | [238, 258] | 246 [236, 257] | 245 [233, 256] |  | agree: readers' 245-246 are inside, the mechanism leans 2 higher. |
| t30 | 250 | [241, 259] | 244 [234, 254] | 245 [234, 256] |  | disagree: readers take the 240-244 branch, which assumes late wrong answers agree; drifted long answers end on scattered values. |
| t31 | 83 | [75, 91] | 80 [72, 88] | 82 [74, 90] |  | agree: readers' 80-82, the mechanism slightly higher. |

## f2-m02

Vote gains come in parity steps. At even k many problems end in exact ties (36 of 500 at k=4) broken by the lowest sample index, i.e. by one random draw, so an even k adds little over the odd k before it, while an odd k breaks most 2-2 and 1-1-1-1 ties with one more draw. The curve over k is therefore a zigzag rising about 1.5 problems per odd step, with flat or slightly lower even steps.

Rests on: result-40ed3b, result-5c961a, result-e41d94. Forecasts 16 of 31 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t16 | 450 | [446, 454] | 449 [443, 455] | 449 [443, 455] |  | agree: readers' 449. |
| t17 | 449 | [445, 453] | 450 [443, 456] | 449 [443, 456] |  | agree: readers' 449-450. |
| t18 | 453 | [448, 458] | 452 [445, 458] | 451 [445, 457] |  | agree: readers' 451-452, one higher by parity. |
| t19 | 451 | [446, 456] | 452 [446, 459] | 451 [445, 458] |  | agree: readers' 451-452. |
| t20 | 454 | [449, 459] | 454 [447, 460] | 452 [446, 459] |  | agree: readers' 452-454. |
| t21 | 453 | [448, 458] | 454 [447, 461] | 452 [446, 459] |  | agree: readers' 452-454. |
| t22 | 455 | [450, 460] | 455 [448, 461] | 453 [446, 460] |  | agree: readers' 453-455. |
| t23 | 454 | [449, 459] | 455 [448, 462] | 453 [446, 460] |  | agree: readers' 453-455. |
| t24 | 79 | [75, 82] | 79 [73, 85] | 79 [72, 86] |  | agree: readers' 79. |
| t06 | 51 | [43, 59] | 52 [44, 60] | 52 [43, 61] |  | agree: readers' 52. |
| t28 | 245 | [235, 255] | 246 [236, 257] | 245 [233, 256] |  | agree: readers' 245-246. |
| t30 | 244 | [235, 253] | 244 [234, 254] | 245 [234, 256] |  | agree: readers' 244-245. |
| t31 | 81 | [73, 89] | 80 [72, 88] | 82 [74, 90] |  | agree: readers' 80-82. |
| t25 | 71 | [63, 79] | 71 [63, 79] | 71 [62, 80] |  | agree: readers' 71. |
| t26 | 231 | [220, 242] | 231 [220, 242] | 231 [219, 243] |  | agree: readers' 231. |
| t27 | 231 | [220, 242] | 231 [220, 242] | 231 [219, 243] |  | agree: readers' 231. |

## f2-m03

Under T 1.0 stopping is a sampled event: at each position the model draws a commit/stop token with a small hazard, so the cap-hit share is a survival probability. RL's top-8 directions add a near-constant logit to that hazard (cap hits 96, 77, 46, 25, 5 along the dial); dose multiplies it. Where the base fails by not stopping (short code tasks, fresh contests) the dial converts unfinished samples, at precision below the base's finished answers.

Rests on: result-6f1bb7, result-51a0e7, result-c8b994, result-0c1eef, result-3387ce. Forecasts 19 of 31 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t01 | 358 | [335, 381] | 350 [325, 376] | 350 [325, 376] |  | disagree: readers assume a smaller share on code, but code answers are short, so a raised stop hazard converts more of them than on hard math. |
| t02 | 368 | [344, 392] | 357 [330, 384] | 357 [328, 386] |  | disagree: readers' 357 caps the gain at math's 1x share; the hazard keeps paying on short outputs. |
| t03 | 362 | [334, 390] | 350 [314, 384] | 350 [312, 384] |  | disagree: readers copy math's 2x fall-back to 350, which came from stopping long solutions early. |
| t04 | 318 | [303, 333] | 318 [302, 335] | 318 [299, 337] |  | agree: readers' 318. |
| t05 | 350 | [326, 374] | 347 [318, 376] | 340 [310, 368] |  | agree: readers' 340-347, the mechanism slightly higher. |
| t06 | 51 | [43, 59] | 52 [44, 60] | 52 [43, 61] |  | agree: readers' 52. |
| t07 | 44 | [37, 51] | 47 [40, 54] | 46 [39, 53] |  | disagree: readers assume RL-level precision carries over; the edit only finishes, and RL's fresh2026 lead is partly precision (42.8 % vs 36 %). |
| t12 | 231 | [216, 246] | 231 [214, 247] | 232 [215, 248] |  | agree: readers' 231-232. |
| t13 | 207 | [191, 223] | 209 [191, 227] | 204 [185, 221] |  | agree: readers' 204-209. |
| t14 | 466 | [456, 476] | 466 [455, 477] | 464 [452, 475] |  | agree: readers' 464-466. |
| t15 | 459 | [448, 469] | 460 [449, 470] | 457 [444, 468] |  | agree: readers' 457-460. |
| t24 | 79 | [75, 83] | 79 [73, 85] | 79 [72, 86] |  | agree: readers' 79. |
| t25 | 71 | [63, 79] | 71 [63, 79] | 71 [62, 80] |  | agree: readers' 71. |
| t26 | 231 | [220, 242] | 231 [220, 242] | 231 [219, 243] |  | agree: readers' 231. |
| t27 | 231 | [220, 242] | 231 [220, 242] | 231 [219, 243] |  | agree: readers' 231. |
| t28 | 246 | [236, 256] | 246 [236, 257] | 245 [233, 256] |  | agree: readers' 245-246. |
| t29 | 469 | [460, 478] | 468 [459, 477] | 466 [455, 476] |  | agree: readers' 466-468. |
| t30 | 248 | [239, 257] | 244 [234, 254] | 245 [234, 256] |  | agree: readers' 244-245, the mechanism a little higher. |
| t31 | 84 | [76, 92] | 80 [72, 88] | 82 [74, 90] |  | agree: readers' 80-82, slightly higher. |

## f2-m04

A T 1.0 run is a set of independent per-problem Bernoulli draws: the run-to-run spread of a count is sqrt(sum p(1-p)), about 5-6 problems on MATH-500 and 6 on hard328 for these models, and the seed adds nothing systematic. A stored first sample is one such draw, so a 4-sample mean is 1/4 that draw plus 3/4 the model's mean, and adding one sample to a vote moves only the few problems it can flip.

Rests on: result-fad48d, result-5c961a, result-3387ce, result-40ed3b. Forecasts 17 of 31 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t04 | 318 | [305, 331] | 318 [302, 335] | 318 [299, 337] |  | agree: same center, narrower because the spread is binomial. |
| t07 | 46.5 | [40.5, 52.5] | 47 [40, 54] | 46 [39, 53] |  | agree: readers' 46-47. |
| t08 | 416.5 | [410, 423] | 416 [408, 424] | 415 [408, 422] |  | agree: readers' 415-416, interval narrower. |
| t09 | 424 | [417.5, 430.5] | 423 [415, 431] | 422 [414, 430] |  | agree: readers' 422-423. |
| t10 | 434.5 | [428, 441] | 434 [426, 441] | 434 [427, 441] |  | agree: readers' 434. |
| t11 | 1.2 | [-0.1, 2.5] | 1.1 [-0.8, 3] | 0.9 [-0.6, 2.4] |  | agree: readers' 0.9-1.1. |
| t12 | 231 | [218, 244] | 231 [214, 247] | 232 [215, 248] |  | agree: readers' 231-232. |
| t13 | 207 | [193, 221] | 209 [191, 227] | 204 [185, 221] |  | agree: readers' 204-209. |
| t14 | 465 | [457, 473] | 466 [455, 477] | 464 [452, 475] |  | agree: readers' 464-466. |
| t15 | 459 | [450, 468] | 460 [449, 470] | 457 [444, 468] |  | agree: readers' 457-460. |
| t16 | 449.5 | [446, 453] | 449 [443, 455] | 449 [443, 455] |  | agree: readers' 449, narrower. |
| t20 | 454 | [449, 459] | 454 [447, 460] | 452 [446, 459] |  | agree: readers' 452-454. |
| t24 | 79 | [76, 82] | 79 [73, 85] | 79 [72, 86] |  | agree: readers' 79, narrower. |
| t25 | 71 | [64, 78] | 71 [63, 79] | 71 [62, 80] |  | agree: readers' 71. |
| t26 | 231.5 | [221, 242] | 231 [220, 242] | 231 [219, 243] |  | agree: readers' 231. |
| t27 | 231.5 | [221, 242] | 231 [220, 242] | 231 [219, 243] |  | agree: readers' 231. |
| t29 | 468 | [460, 476] | 468 [459, 477] | 466 [455, 476] |  | agree: readers' 466-468. |

## f2-m05

Long untruncated T 1.0 generations drift off-distribution (script switches into Chinese, restarted working) at a rate set by how far the prompt template is from the model's training format. Drifted continuations are almost never right (1 of 24 finish right). Think-SFT in its own ChatML <think> format samples a sharper, on-distribution next-token distribution, so fewer long answers drift, and its trained Answer line removes v3 undercounts; raw-template cue runs keep the drift.

Rests on: result-997be4, result-c8b994, result-818c20. Forecasts 16 of 31 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t08 | 416 | [409, 423] | 416 [408, 424] | 415 [408, 422] |  | agree: readers' 415-416. |
| t09 | 423 | [416, 430] | 423 [415, 431] | 422 [414, 430] |  | agree: readers' 422-423. |
| t10 | 434 | [427, 441] | 434 [426, 441] | 434 [427, 441] |  | agree: readers' 434. |
| t11 | 1.1 | [-0.4, 2.6] | 1.1 [-0.8, 3] | 0.9 [-0.6, 2.4] |  | agree: readers' 0.9-1.1. |
| t12 | 238 | [224, 252] | 231 [214, 247] | 232 [215, 248] |  | disagree: readers assume the native format equals the raw one; the raw template's drift cost ~7 problems at 32k. |
| t13 | 209 | [195, 223] | 209 [191, 227] | 204 [185, 221] |  | agree: readers' 204-209. |
| t14 | 468 | [459, 477] | 466 [455, 477] | 464 [452, 475] |  | agree: readers' 464-466, slightly higher. |
| t15 | 462 | [453, 471] | 460 [449, 470] | 457 [444, 468] |  | disagree: readers copy the raw-template singles, which carry a ~4-problem format undercount. |
| t24 | 79 | [75, 83] | 79 [73, 85] | 79 [72, 86] |  | agree: readers' 79. |
| t25 | 71 | [63, 79] | 71 [63, 79] | 71 [62, 80] |  | agree: readers' 71. |
| t26 | 231 | [220, 242] | 231 [220, 242] | 231 [219, 243] |  | agree: readers' 231. |
| t27 | 231 | [220, 242] | 231 [220, 242] | 231 [219, 243] |  | agree: readers' 231. |
| t28 | 246 | [236, 256] | 246 [236, 257] | 245 [233, 256] |  | agree: readers' 245-246. |
| t29 | 468 | [459, 477] | 468 [459, 477] | 466 [455, 476] |  | agree: readers' 466-468. |
| t30 | 244 | [235, 253] | 244 [234, 254] | 245 [234, 256] |  | agree: readers' 244-245. |
| t31 | 79 | [71, 87] | 80 [72, 88] | 82 [74, 90] |  | agree: readers' 80-82, slightly lower. |

## f2-m06

Adding RL-direction weight to a model concentrates its answer-level distribution: samples of one problem agree more, right or wrong. Higher dose therefore raises single-sample accuracy where answers are short but shrinks what a vote adds (vote/single 1.21 base, 1.07 for the 1.5x edit, 1.09 for Think-SFT + 2x on fresh2026). On short exact outputs such as code, concentration has no truncation cost, so code accuracy does not fall back at 2x as math did.

Rests on: result-95a4dc, result-5251c9, result-5c961a, result-3387ce. Forecasts 16 of 31 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t01 | 345 | [323, 367] | 350 [325, 376] | 350 [325, 376] |  | agree: readers' 350. |
| t02 | 356 | [333, 379] | 357 [330, 384] | 357 [328, 386] |  | agree: readers' 357. |
| t03 | 358 | [330, 386] | 350 [314, 384] | 350 [312, 384] |  | disagree: readers carry math's 2x fall-back to code, where answers are too short for truncation to cost. |
| t04 | 317 | [302, 332] | 318 [302, 335] | 318 [299, 337] |  | agree: readers' 318. |
| t05 | 338 | [314, 362] | 347 [318, 376] | 340 [310, 368] |  | agree: readers' 340-347. |
| t06 | 50 | [42, 58] | 52 [44, 60] | 52 [43, 61] |  | agree: readers' 52, slightly lower. |
| t07 | 46 | [39, 53] | 47 [40, 54] | 46 [39, 53] |  | agree: readers' 46-47. |
| t16 | 450 | [444, 456] | 449 [443, 455] | 449 [443, 455] |  | agree: readers' 449. |
| t20 | 455 | [449, 461] | 454 [447, 460] | 452 [446, 459] |  | agree: readers' 452-454. |
| t23 | 457 | [451, 463] | 455 [448, 462] | 453 [446, 460] |  | disagree: readers flatten at 453-455; the base's diffuse answers keep resolving. |
| t24 | 79 | [75, 82] | 79 [73, 85] | 79 [72, 86] |  | agree: readers' 79. |
| t25 | 71 | [63, 79] | 71 [63, 79] | 71 [62, 80] |  | agree: readers' 71. |
| t28 | 243 | [233, 253] | 246 [236, 257] | 245 [233, 256] |  | agree: readers' 245-246, slightly lower. |
| t29 | 468 | [459, 477] | 468 [459, 477] | 466 [455, 476] |  | agree: readers' 466-468. |
| t30 | 246 | [237, 255] | 244 [234, 254] | 245 [234, 256] |  | agree: readers' 244-245. |
| t31 | 81 | [73, 89] | 80 [72, 88] | 82 [74, 90] |  | agree: readers' 80-82. |

## t01 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems the base model plus Code-RL 3.1's 8 top weight directions at 1x size passes, with the Code cue at T 1.0.

Unit: problems passed of 538. Cell: {"model": "base + Code 3.1's 8 directions (top-8 singular directions per matrix of RL-Zero-Code 3.1 minus base) at 1x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": "not stated", "grader": "not stated"}

> Code 3.1's 8 directions at 1x, 1.5x, 2x

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 350 | [325, 376] | Base Code cue 317 vs RL-Code 401; Math top-8 at 1x closed about two thirds of the cued gap on hard328 (192 vs 164/206), so roughly half to two thirds of 84 here. |
| reader-2 | 350 | [325, 376] | Base Code cue 317, RL-Code 401; on math the top-8 at 1x closed about two thirds of the hard328 gap, so I assume a smaller share on code, where the cue already gives 53-58%. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | 358 | [335, 381] | The cued base on code fails largely by not ending the program and stopping; Code top-8 raises the stop hazard and recovers ~half of the 84-problem Code-RL gap. |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | 345 | [323, 367] | 1x Code directions concentrate the base's code samples on its modal program; about a third of the Code-RL gap. |

## t02 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems the base model plus Code-RL 3.1's 8 top weight directions at 1.5x size passes, with the Code cue at T 1.0.

Unit: problems passed of 538. Cell: {"model": "base + Code 3.1's 8 directions at 1.5x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": "not stated", "grader": "not stated"}

> Code 3.1's 8 directions at 1x, 1.5x, 2x

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 357 | [330, 384] | 1.5x was the peak of the math dial (203 vs 192 at 1x, MATH-500 456 vs RL 457), so a bit above 1x, with doubt about transfer to code. |
| reader-2 | 357 | [328, 386] | On math, 1.5x was the peak of the finish dial (203 vs 192 at 1x on hard328), so a little above 1x on code. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | 368 | [344, 392] | 1.5x raises the hazard further; on math it reached RL's level, here ~60 % of the gap. |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | 356 | [333, 379] | More dose, more concentration on the modal program. |

## t03 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems the base model plus Code-RL 3.1's 8 top weight directions at 2x size passes, with the Code cue at T 1.0.

Unit: problems passed of 538. Cell: {"model": "base + Code 3.1's 8 directions at 2x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": "not stated", "grader": "not stated"}

> Code 3.1's 8 directions at 1x, 1.5x, 2x

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 350 | [314, 384] | On math, 2x fell back from 1.5x (190 vs 203) as answers get cut short; the same small drop with wider uncertainty. |
| reader-2 | 350 | [312, 384] | On math, 2x fell back below 1.5x (190 vs 203) as answers shortened and word salad began, so it should land near 1x with a wider spread. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | 362 | [334, 390] | 2x cut math answers short because math solutions are long; code solutions are short, so premature stops cost little. |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | 358 | [330, 386] | Concentration keeps paying at 2x on short outputs; math's drop came from cutting long solutions. |

## t04 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems the base model plus a random rank-8 weight edit at 1.5x size (control) passes, with the Code cue at T 1.0.

Unit: problems passed of 538. Cell: {"model": "base + random rank-8 edit at 1.5x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": "not stated", "grader": "not stated"}

> random at 1.5x

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 318 | [302, 335] | The random rank-8 edit is flat at every size on math (158-167 vs base 164; 159 at 1.5x), so expect base cue 317 plus sampling noise. |
| reader-2 | 318 | [299, 337] | The random rank-8 edit is flat at every size on math (158-167 vs base 164), so I expect it near the base Code cue score of 317, give or take sampling noise. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | 318 | [303, 333] | Random rank-8 does not move the stop hazard (flat cap hits on math). |
| f2-m04 | 318 | [305, 331] | Random edit = base 317; binomial spread on 538 with heterogeneous p is ~8. |
| f2-m05 | - |  | no forecast |
| f2-m06 | 317 | [302, 332] | Random edit does not concentrate anything. |

## t05 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems the base model plus Math-RL 3.1's 8 top weight directions at 1.5x size passes, with the Code cue at T 1.0.

Unit: problems passed of 538. Cell: {"model": "base + Math 3.1's 8 directions (top-8 per matrix of RL-Zero-Math 3.1 minus base) at 1.5x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": "not stated", "grader": "not stated"}

> Math 3.1's at 1.5x, on HumanEval+ and MBPP+

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 347 | [318, 376] | RL gains cross domains (Code-RL 3.1 gives the full math gain; Math-RL nearly matches Code-RL on LiveCodeBench), so Math directions should give most of what Code directions give. |
| reader-2 | 340 | [310, 368] | Math-RL transfers to code (LiveCodeBench 21.9 vs Code-RL 24.3) and Code top-8 helped math, so the Math top-8 at 1.5x should give a partial gain over 317. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | 350 | [326, 374] | Math top-8 also raises the stop hazard (it is a finishing direction), close to Code's own. |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | 338 | [314, 362] | Math directions concentrate math-style answers; partial transfer to code. |

## t06 (work-16773f): How many of the 136 fresh2026 contest problems the base model plus 1.5 times RL-Math's top 8 weight directions gets right with the cue under a majority vote over 4 samples (RL's vote: 57).

Unit: right answers of 136 under vote over 4. Cell: {"model": "base + 1.5 x top 8 directions of RL-Math - base", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> is it level with RL (57 vote, 50.5 single)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 52 | [44, 60] | The 1.5x edit matched RL's single-sample score on hard328 but trailed under the vote (214 vs 221); RL vote on fresh2026 is 57, base 38. |
| reader-2 | 52 | [43, 61] | The edit matched RL single on hard328 but fell 7 short of RL's vote there; on the harder fresh set (RL vote 57, base cue 38) I place it a bit below RL. |
| r5-m03-rival | 53 | [45, 61] | Theory: with the cue the top-8 edit puts nearly every sample on a weak dose of RL's own policy, so the vote sits just below RL's 57, as on hard328 where the 1.5x edit's vote was 214 against RL's 221; well above the cued base's 38. |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 53 | [45, 61] | Edit singles near 46-47 on fresh2026; scattered wrong answers give a vote/single ratio of about 1.13, as RL's. |
| f2-m02 | 51 | [43, 59] | Even k=4 vote loses tie problems to sample-0 breaking; ratio to singles ~1.1. |
| f2-m03 | 51 | [43, 59] | Vote over the singles below, ratio ~1.15. |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | 50 | [42, 58] | Edit's vote/single ~1.08 (as on hard328) on singles ~46. |

## t07 (work-16773f): The mean number of the 136 fresh2026 contest problems that one sample of the base model plus 1.5 times RL-Math's top 8 weight directions gets right with the cue, averaged over 4 samples (RL's single: 50.5).

Unit: mean right answers of 136 per single sample (mean of 4). Cell: {"model": "base + 1.5 x top 8 directions of RL-Math - base", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> is it level with RL (57 vote, 50.5 single)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 47 | [40, 54] | Single-sample parity with RL on hard328 (200.25 vs 200) and MATH-500, shaded down for the harder 2026 set (RL 50.5, base 29.5). |
| reader-2 | 46 | [39, 53] | RL single 50.5 and base cue 29.5; I expect the edit slightly below RL on these harder post-cutoff problems. |
| r5-m03-rival | 48.5 | [42, 55] | Theory: the edit is a weak dose of RL's policy (few quick wrong answers, errors only on hard problems), so one sample lands near RL's 50.5, slightly under it, as the 1.5x edit matched RL on hard328 singles (200.25 vs 200) and MATH-500 (456 vs 457). |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 46.5 | [40, 53] | Scatter of wrong answers does not act on a single sample; the edit's single rate is RL's shaded for the harder set. |
| f2-m02 | - |  | no forecast |
| f2-m03 | 44 | [37, 51] | Base caps 40 % -> ~15 % under the edit; converted caps on these hard problems are right ~17 % of the time, finished ones gain ~14 %: 29.5 + 6 + 4 + small. |
| f2-m04 | 46.5 | [40.5, 52.5] | Mean of 4 draws has small noise; the center is the readers' prior. |
| f2-m05 | - |  | no forecast |
| f2-m06 | 46 | [39, 53] | Single rate near RL's, shaded for the harder set. |

## t08 (work-f8ecb6): The mean number of MATH-500 problems (of 500) the RL step-100 checkpoint gets right with the plain prompt at T 1.0, averaged over 4 samples, grader v3.

Unit: mean right answers of 500 per sample (3 new samples plus stored sample 0). Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math checkpoint step 100", "prompt": "plain", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": 4, "grader": "v3"}

> 3 more samples of step-100 plain, step-100 cue, step-400 plain (MATH-500, T 1.0, v3)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 416 | [408, 424] | Stored sample 0 is 418; a 4-sample mean pulls slightly back, as base cue samples range 405-418. |
| reader-2 | 415 | [408, 422] | The stored sample is 418; I shrink the 3 new samples toward about 414 (sample spread like the cued base's 405-418). |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | 416.5 | [410, 423] | 0.25 x 418 + 0.75 x model mean ~416 (sd 4), new-sample noise 5.5/sqrt(3). |
| f2-m05 | 416 | [409, 423] | RL checkpoints rarely drift (script switches 12 of 1,312 for RL); stored draw plus regression. |
| f2-m06 | - |  | no forecast |

## t09 (work-f8ecb6): The mean number of MATH-500 problems (of 500) the RL step-100 checkpoint gets right with the opening cue at T 1.0, averaged over 4 samples, grader v3.

Unit: mean right answers of 500 per sample (3 new samples plus stored sample 0). Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math checkpoint step 100", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": 4, "grader": "v3"}

> 3 more samples of step-100 plain, step-100 cue, step-400 plain (MATH-500, T 1.0, v3)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 423 | [415, 431] | Stored step-100 cue sample is 427, the cue effect on step 100 is +1.8 [-1.2, 4.8], and the mean regresses slightly. |
| reader-2 | 422 | [414, 430] | The stored step-100 cue sample is 427, and the cue added about +1.8 at step 100; I regress the new samples toward about 421. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | 424 | [417.5, 430.5] | 0.25 x 427 + 0.75 x ~423. |
| f2-m05 | 423 | [416, 430] | No drift change from the cue at step 100. |
| f2-m06 | - |  | no forecast |

## t10 (work-f8ecb6): The mean number of MATH-500 problems (of 500) the RL step-400 checkpoint gets right with the plain prompt at T 1.0, averaged over 4 samples, grader v3.

Unit: mean right answers of 500 per sample (3 new samples plus stored sample 0). Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math checkpoint step 400", "prompt": "plain", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": 4, "grader": "v3"}

> 3 more samples of step-100 plain, step-100 cue, step-400 plain (MATH-500, T 1.0, v3)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 434 | [426, 441] | Stored step-400 plain sample is 436; the mean of 4 should land near it. |
| reader-2 | 434 | [427, 441] | The stored step-400 plain sample is 436, with mild regression for the 3 new samples. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | 434.5 | [428, 441] | 0.25 x 436 + 0.75 x ~434. |
| f2-m05 | 434 | [427, 441] | No drift on MATH-500 lengths. |
| f2-m06 | - |  | no forecast |

## t11 (work-f8ecb6): The difference in MATH-500 accuracy points between the RL step-100 checkpoint with the plain prompt and the untrained base with the cue, at T 1.0, over 4 samples each, grader v3.

Unit: difference in points (step-100 plain minus cued base, 4 samples each). Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math step 100 (plain) vs untrained base Olmo-3-1025-7B with cue", "prompt": "plain (step 100) vs cue (base)", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": 4, "grader": "v3"}

> so the step-100 vs cued-base difference has a 4-sample interval

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 1.1 | [-0.8, 3] | Step-100 plain mean of about 416 against the cued base's 4-sample mean of 410.5 gives about +1.1 points. |
| reader-2 | 0.9 | [-0.6, 2.4] | Step-100 plain mean of about 415 against the cued base's 4-sample mean of 410.5, a difference of about 0.9 points. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | 1.2 | [-0.1, 2.5] | (416.5 - 410.5)/5 points; sd of the difference ~0.8 points. |
| f2-m05 | 1.1 | [-0.4, 2.6] | Difference of means 416 vs 410.5. |
| f2-m06 | - |  | no forecast |

## t12 (work-8b2ec9): How many of the 328 harder problems Think-SFT gets right in its own ChatML <think> chat format at T 1.0 with a 32,768-token cap, one sample, grader v3 (raw template + cue gave 230).

Unit: right answers of 328. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "Think-SFT's own ChatML template with <think> (no base cue)", "set": "hard328", "n": 328, "sampling": "T 1.0; top-p not stated; cap 32,768", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 231 | [214, 247] | Raw template + cue gave 230 at cap 32k; the native chat format, which the model was trained on, should be about the same or a bit better. |
| reader-2 | 232 | [215, 248] | With the raw template plus cue at 32k it scored 230; its native ChatML format should be about equal, and one sample varies by roughly ±9. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | 231 | [216, 246] | Think-SFT's stop hazard is set by its weights, not the template; 32k finishes its cut answers as in the cue run (230). |
| f2-m04 | 231 | [218, 244] | One draw around the cue run's 230; spread ~8 with cap-hit variance. |
| f2-m05 | 238 | [224, 252] | In the raw cue run 24 of 93 cut answers had switched script and finished right 1 of 24 vs 22 of 69; native format avoids most switches, so ~+7 over 230. |
| f2-m06 | - |  | no forecast |

## t13 (work-8b2ec9): How many of the 328 harder problems Think-SFT gets right in its own ChatML <think> chat format at T 1.0 when the same answers are counted at a 16,384-token cap, one sample, grader v3 (raw template + cue gave 207).

Unit: right answers of 328. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "Think-SFT's own ChatML template with <think> (no base cue)", "set": "hard328", "n": 328, "sampling": "T 1.0; top-p not stated; same answers scored at cap 16,384", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 209 | [191, 227] | The cue run's 16k count was 207, 23 below its 32k count; expect a similar long tail in the native format. |
| reader-2 | 204 | [185, 221] | The cue run scored 207 at 16k; native thinking may run longer, so slightly fewer answers finish under 16k. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | 207 | [191, 223] | Same survival curve at 16k as the cue run (207). |
| f2-m04 | 207 | [193, 221] | One draw around 207. |
| f2-m05 | 209 | [195, 223] | Switches start at a median 13,589 tokens, so little changes under 16k. |
| f2-m06 | - |  | no forecast |

## t14 (work-8b2ec9): How many of the 500 MATH-500 problems Think-SFT gets right in its own ChatML <think> chat format at T 1.0 with a 32,768-token cap, one sample, grader v3.

Unit: right answers of 500. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "Think-SFT's own ChatML template with <think> (no base cue)", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; cap 32,768", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 466 | [455, 477] | Think-SFT cue singles score 454-462 at 16k; the 32k cap recovers some of its roughly 25 cap hits. |
| reader-2 | 464 | [452, 475] | Think-SFT cue singles are 454-462 at 16k, and the 32k cap adds a few more finished answers. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | 466 | [456, 476] | ~25 cap hits at 16k; most finish under 32k, about a third right. |
| f2-m04 | 465 | [457, 473] | One draw; p is high on MATH-500 so the spread is ~5. |
| f2-m05 | 468 | [459, 477] | Native Answer line plus 32k finishing; fewer drifted long answers. |
| f2-m06 | - |  | no forecast |

## t15 (work-8b2ec9): How many of the 500 MATH-500 problems Think-SFT gets right in its own ChatML <think> chat format at T 1.0 when the same answers are counted at a 16,384-token cap, one sample, grader v3.

Unit: right answers of 500. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "Think-SFT's own ChatML template with <think> (no base cue)", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; same answers scored at cap 16,384", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 460 | [449, 470] | Matches the stored Think-SFT 16k singles (454-462). |
| reader-2 | 457 | [444, 468] | Same as the cue singles range of 454-462 at the 16k cap. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | 459 | [448, 469] | 16k count equals the stored singles' range. |
| f2-m04 | 459 | [450, 468] | One draw within the stored 454-462. |
| f2-m05 | 462 | [453, 471] | 16 of 74 finished-wrong cue answers had the gold on the line after 'Answer:' (v3 undercount ~4); the trained format fixes it. |
| f2-m06 | - |  | no forecast |

## t16 (work-60f040): How many of the 500 MATH-500 problems the untrained cued base gets right under a majority vote over 5 samples at T 1.0, grader v3 (vote over 4 is 446).

Unit: right answers of 500 under vote over 5. Cell: {"model": "untrained base Olmo-3-1025-7B", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and token cap not stated (same cell as the stored 4)", "samples": 5, "grader": "v3"}

> Vote over k = 1..12 samples of the untrained cued base on MATH-500 (8 new samples, T 1.0, v3, same cell as the stored 4)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 449 | [443, 455] | Vote over 4 is 446; an odd k cuts ties, and Wang's majority curve gains about 2 points from k=4 to 8 on our scale. |
| reader-2 | 449 | [443, 455] | Vote over 4 is 446 with 36 ties; a 5th sample breaks some ties toward the right answer. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 449 | [443, 455] | The rival says the open part at T 1.0 is mostly sharpening that a base-only vote partly recovers (456 at 9 votes); interpolating from the stored vote over 4 (446) toward that endpoint, an odd fifth vote breaks ties and adds about 3. |
| r6-m06 | 449 | [442, 456] | Statement: the cued base's wrong steps come from the head of its own distribution, so its wrong answers recur across samples and voting adds little; starting from the stored vote over 4 (446) and single samples (~410), an odd k=5 adds about 3. |
| r7-m05 | 448 | [441, 455] | In-scope cell (cued base, MATH-500, T 1.0, v3): the theory says misreads and slips sit near the mode of the base's generic prior, so resampling repeats them (the explained 6 of 11 slips are repeated on a check). That keeps vote gains small past the stored vote-over-4 of 446, and an odd k adds about 2. |
| r7-m08 | 446 | [440, 452] | The theory's no_intervention clause says the vetoed steps are high-probability under the base, so selecting among base samples only reaches the measured vote-over-4 level (446-450); adding a fifth sample keeps it near 446. |
| r7-m11 | 448 | [443, 454] | In scope (cued base, MATH-500, T 1.0, v3). The theory says wrong answers drawn under the shared cue agree with each other, so the vote stays below the independent-slip prediction; a fifth sample breaks only a few of vote-4's 36 ties, giving about 2 over 446. |
| f2-m01 | 450 | [445, 455] | A fifth draw breaks 2-2 and 1-1-1-1 ties toward the coinciding right answer: about +4 over 446. |
| f2-m02 | 450 | [446, 454] | k=5 breaks most of the 36 ties: +4 over 446. |
| f2-m03 | - |  | no forecast |
| f2-m04 | 449.5 | [446, 453] | One added sample can flip only the ~36 tie and ~20 2-1-1 problems; expected +3.5. |
| f2-m05 | - |  | no forecast |
| f2-m06 | 450 | [444, 456] | The untrained base is diffuse, so its vote keeps gaining. |

## t17 (work-60f040): How many of the 500 MATH-500 problems the untrained cued base gets right under a majority vote over 6 samples at T 1.0, grader v3.

Unit: right answers of 500 under vote over 6. Cell: {"model": "untrained base Olmo-3-1025-7B", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and token cap not stated (same cell as the stored 4)", "samples": 6, "grader": "v3"}

> Vote over k = 1..12 samples of the untrained cued base on MATH-500 (8 new samples, T 1.0, v3, same cell as the stored 4)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 450 | [443, 456] | Majority-vote curve between 446 at k=4 and about 454 at k=8; even k loses a little to ties. |
| reader-2 | 449 | [443, 456] | An even k brings ties back, so roughly level with vote over 5. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 450 | [444, 457] | Same base-only vote curve from the rival (446 at k=4 rising to 456 at k=9), placed one step on at k=6; an even k gains little because ties fall to the lowest-numbered sample. |
| r6-m06 | 450 | [443, 457] | Head-of-distribution errors (statement, result-faf15a: the wrong step has log-prob -0.53 vs -0.63 for control text) are repeated, not random, so the vote curve flattens just above 446. |
| r7-m05 | 449 | [442, 456] | Mode-level errors repeat across samples (theory statement and its NMT import), so the vote curve stays flat near the vote-over-4 446; even k loses a little to ties. |
| r7-m08 | 447 | [441, 453] | Same clause: no base-only rule reproduces the veto, so the vote stays at the vote-over-4 plateau of 446-450 and does not climb toward RL. |
| r7-m11 | 448 | [442, 454] | Even k brings ties back. The agreeing wrong groups (part of the 21 problems between pass@4 467 and vote 446) still hold, so vote 6 stays level with vote 5. |
| f2-m01 | 450 | [445, 456] | Even k re-creates some ties; net level with k=5. |
| f2-m02 | 449 | [445, 453] | Even k: 3-3 and 2-2-1-1 ties return, broken by sample 0. |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t18 (work-60f040): How many of the 500 MATH-500 problems the untrained cued base gets right under a majority vote over 7 samples at T 1.0, grader v3.

Unit: right answers of 500 under vote over 7. Cell: {"model": "untrained base Olmo-3-1025-7B", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and token cap not stated (same cell as the stored 4)", "samples": 7, "grader": "v3"}

> Vote over k = 1..12 samples of the untrained cued base on MATH-500 (8 new samples, T 1.0, v3, same cell as the stored 4)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 452 | [445, 458] | Interpolated on the vote-k curve; Wang's maj@8 is about 2.5 points above maj@4. |
| reader-2 | 451 | [445, 457] | A slow rise: Wang et al.'s majority curve gains about +2.5 points from 4 to 8 samples, damped here by correlated failures. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 453 | [446, 459] | Rival's base-only vote curve (446 at k=4, 456 at k=9), placed at k=7, about two thirds of the way along. |
| r6-m06 | 452 | [445, 459] | Same mechanism: correlated head errors limit the vote to small gains over vote-4 446, well below the base's pass@4 of 467. |
| r7-m05 | 451 | [444, 458] | Generic-prior misreads and slips stay correlated across samples, so each added sample lifts the vote only slightly from 446, well short of pass@4 467. |
| r7-m08 | 448 | [442, 454] | Same clause: wrong steps the base rates as likely recur across samples, so more votes add only slips that resampling fixes; the vote stays near the 446-450 plateau. |
| r7-m11 | 450 | [444, 456] | Odd k removes ties, but under the theory the agreeing wrong groups grow along with the right ones, so the gain flattens at about 4 over 446. |
| f2-m01 | 453 | [447, 459] | More draws keep resolving problems with p 0.25-0.4 whose wrong answers scatter. |
| f2-m02 | 453 | [448, 458] | Odd step: ties resolved again, +3 over k=6. |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t19 (work-60f040): How many of the 500 MATH-500 problems the untrained cued base gets right under a majority vote over 8 samples at T 1.0, grader v3.

Unit: right answers of 500 under vote over 8. Cell: {"model": "untrained base Olmo-3-1025-7B", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and token cap not stated (same cell as the stored 4)", "samples": 8, "grader": "v3"}

> Vote over k = 1..12 samples of the untrained cued base on MATH-500 (8 new samples, T 1.0, v3, same cell as the stored 4)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 452 | [446, 459] | About 1.5 points above vote over 4, limited by about 33 problems where the base gets 0 of 4. |
| reader-2 | 451 | [445, 458] | Plateau on the way to the pass@4 ceiling of 467; correlated failures limit the gain. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 454 | [447, 460] | Rival's base-only vote curve, placed at k=8 just below the k=9 point of 456; this matches the shape of Wang's majority@8. |
| r6-m06 | 452 | [445, 459] | Head-of-distribution errors make wrong answers agree across samples, so the curve plateaus near 452 at k=8 (even k also loses some ties). |
| r7-m05 | 451 | [444, 458] | Plateau implied by the mode-not-tail claim (the hazard fit also shows the vote 10 problems below the independent-slip prediction); about 5 over vote-over-4 446, pulled up a little by the high new shard (857 of 1,000). |
| r7-m08 | 449 | [443, 455] | Same clause: selection among base samples is capped near 446-450 because the vetoed misreads are high-probability base continuations; small slip-driven gains only. |
| r7-m11 | 450 | [444, 456] | Under the theory the shared-context wrong values keep the vote flat at about vote 7's level, against Wang's independent-like gain of +2.5 points from 4 to 8. |
| f2-m01 | 454 | [448, 460] | Continued resolution of low-p but plural-right problems. |
| f2-m02 | 451 | [446, 456] | Even step drops back slightly below k=7. |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t20 (work-60f040): How many of the 500 MATH-500 problems the untrained cued base gets right under a majority vote over 9 samples at T 1.0, grader v3 (theory prediction 456 [449, 462]; one RL sample 456-463).

Unit: right answers of 500 under vote over 9. Cell: {"model": "untrained base Olmo-3-1025-7B", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and token cap not stated (same cell as the stored 4)", "samples": 9, "grader": "v3"}

> vote over 9 = 456 [449, 462] of 500 (result-c637b2)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 454 | [447, 460] | The curve flattens near 454-456; the theory predicted 456 [449, 462]. |
| reader-2 | 452 | [446, 459] | Plateau slightly below the theory's 456; the board shows 9-10 problems below the independent-slip prediction. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 456 | [449, 462] | The rival states it directly: a base-only vote over more samples recovers part of the sharpening share, predicted 456/500, with interval [449, 462] (result-c637b2). |
| r6-m06 | 453 | [446, 460] | Errors drawn from the head give a plateau a little below the account's 456 for vote over 9; each extra sample repeats the base's likely wrong answers. |
| r7-m05 | 453 | [446, 460] | Under the theory the errors are at the mode, so the vote saturates below the independent-sampling prediction of 456 [449, 462]: 453, about 7 over 446. |
| r7-m08 | 449 | [443, 456] | Same clause puts base selection at 446-450 with no way to reproduce the veto, so the forecast sits below the 456 that result-c637b2 predicted and below RL's single sample. |
| r7-m11 | 451 | [445, 457] | The theory says the agreeing wrong groups keep vote 9 about 5 below the independent-slip prediction of 456 (result-c637b2), much as vote 4 fell 10 below its independent prediction (result-e41d94). |
| f2-m01 | 455.5 | [450, 461] | About 10 of the ~21 problems pass@4 has over vote@4 are recoverable by k=9 because their wrong answers do not agree. |
| f2-m02 | 454 | [449, 459] | Odd step, +1.5 over k=7 on the zigzag. |
| f2-m03 | - |  | no forecast |
| f2-m04 | 454 | [449, 459] | Five new draws on a fixed problem set; vote noise small. |
| f2-m05 | - |  | no forecast |
| f2-m06 | 455 | [449, 461] | Diffuse base answers: gains continue to k=9. |

## t21 (work-60f040): How many of the 500 MATH-500 problems the untrained cued base gets right under a majority vote over 10 samples at T 1.0, grader v3.

Unit: right answers of 500 under vote over 10. Cell: {"model": "untrained base Olmo-3-1025-7B", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and token cap not stated (same cell as the stored 4)", "samples": 10, "grader": "v3"}

> Vote over k = 1..12 samples of the untrained cued base on MATH-500 (8 new samples, T 1.0, v3, same cell as the stored 4)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 454 | [447, 461] | The plateau of the vote-k curve, with pass@4 at 467 as a ceiling region. |
| reader-2 | 452 | [446, 459] | Plateau around 452. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 456 | [449, 463] | Rival's vote curve levels off past k=9 (456), because only sharpening and slip problems gain and reach problems (base 0 of n) do not, so k=10 adds about nothing. |
| r6-m06 | 453 | [446, 460] | Plateau set by systematic head-of-distribution errors (statement); about +7 over vote-4 446. |
| r7-m05 | 453 | [446, 460] | Plateau from errors near the mode of the generic prior; even-k ties keep it level with k=9. |
| r7-m08 | 450 | [443, 456] | Same clause: the plateau is at the top of the 446-450 range, below Code 3.1 and RL, because the base's likely wrong steps survive voting. |
| r7-m11 | 451 | [445, 457] | The plateau from shared-context wrong-value agreement, with even-k ties; about the same as vote 9. |
| f2-m01 | 456 | [450, 462] | Curve still rising: scattered wrong answers never form a stable rival plurality. |
| f2-m02 | 453 | [448, 458] | Even step flat to slightly below k=9. |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t22 (work-60f040): How many of the 500 MATH-500 problems the untrained cued base gets right under a majority vote over 11 samples at T 1.0, grader v3.

Unit: right answers of 500 under vote over 11. Cell: {"model": "untrained base Olmo-3-1025-7B", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and token cap not stated (same cell as the stored 4)", "samples": 11, "grader": "v3"}

> Vote over k = 1..12 samples of the untrained cued base on MATH-500 (8 new samples, T 1.0, v3, same cell as the stored 4)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 455 | [448, 461] | Slow gains past k=9 on the plateau. |
| reader-2 | 453 | [446, 460] | Plateau around 452-454. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 457 | [450, 463] | Rival's vote curve levels off past its predicted 456 at k=9; at k=11 an odd vote adds about 1 from the remaining sharpening problems. |
| r6-m06 | 454 | [447, 461] | Plateau from head errors: problems the base gets wrong in a likely way stay wrong as k grows; small further gain at k=11. |
| r7-m05 | 454 | [447, 461] | Plateau from the mode-level errors the theory claims; small increments past k=9, capped well below pass@4 467. |
| r7-m08 | 450 | [443, 457] | Same clause: the vote plateaus at about 450; misread items, where the base's wrong step is the likely one, stay wrong under any vote of base samples. |
| r7-m11 | 452 | [445, 458] | Plateau: the 33 problems the base misses 0 of 4 and the problems where agreeing wrong groups beat the right answer cap the vote near 452, well under pass@4 467. |
| f2-m01 | 457 | [451, 463] | One more odd draw resolves remaining 1-1 ties toward the right value. |
| f2-m02 | 455 | [450, 460] | Odd step peak. |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t23 (work-60f040): How many of the 500 MATH-500 problems the untrained cued base gets right under a majority vote over all 12 samples at T 1.0, grader v3.

Unit: right answers of 500 under vote over 12. Cell: {"model": "untrained base Olmo-3-1025-7B", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and token cap not stated (same cell as the stored 4)", "samples": 12, "grader": "v3"}

> Vote over k = 1..12 samples of the untrained cued base on MATH-500 (8 new samples, T 1.0, v3, same cell as the stored 4)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 455 | [448, 462] | Plateau; Wang's majority curve gains about 1-2 points from 8 to 16 samples. |
| reader-2 | 453 | [446, 460] | Plateau around 453; Wang et al. show only about 2 points more from 8 to 16 samples. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 457 | [450, 464] | Rival's vote curve levels off near 456-457: the reach share (base never right, about 0.1 of the gap) stays out of reach of any vote, so k=12 is close to k=9 to 11. |
| r6-m06 | 454 | [446, 461] | Head-of-distribution errors cap the vote near 454 at k=12, below one RL sample's 456-463, since the base's majority wrong answers do not wash out. |
| r7-m05 | 454 | [447, 461] | Plateau: the theory's correlated, mode-level misreads and slips leave the 12-sample vote about 8 above vote-over-4 446, level with the best known 454. |
| r7-m08 | 450 | [443, 457] | Same clause: vote over 12 stays on the 446-450 plateau because the veto is in the weights, and a base-only selection rule cannot single out the vetoed steps. |
| r7-m11 | 452 | [445, 458] | The plateau holds at k=12: under the theory, wrong groups that agree under the cue stop more samples from reaching the independent ceiling. |
| f2-m01 | 457.5 | [452, 463] | Approaches the mode-right ceiling (~460) below pass@12. |
| f2-m02 | 454 | [449, 459] | Even step, one below k=11. |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | 457 | [451, 463] | The base is the least concentrated arm, so its vote has the most headroom left at k=12. |

## t24 (work-8b4030): How many of the 136 fresh2026 contest problems Think-SFT plus twice the RL-Math weight change gets right under a majority vote over 4 samples (vote over 3 was 78).

Unit: right answers of 136 under vote over 4. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> fresh2026 (136 problems, 4 samples, seeds of SPEC_fresh)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 79 | [73, 85] | Vote over 3 was 78; Think-SFT's vote went from 74 to 75 when a fourth sample was added. |
| reader-2 | 79 | [72, 86] | Vote over 3 was 78; for Think-SFT a 4th sample added about 1 (74 to 75). |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 79 | [75, 83] | A 4th sample to a vote over 3 (78) flips only a few problems. |
| f2-m02 | 79 | [75, 82] | Going from 3 to 4 samples creates 2-2 ties broken by sample 0; net about +1 over 78 (as Think-SFT 74 -> 75). |
| f2-m03 | 79 | [75, 83] | One more sample on a vote over 3 at 78. |
| f2-m04 | 79 | [76, 82] | A 4th sample flips only a handful of problems of a vote over 3 at 78. |
| f2-m05 | 79 | [75, 83] | Raw template, drift unchanged; one more sample on 78. |
| f2-m06 | 79 | [75, 82] | a=2 is concentrated; a 4th sample adds about 1. |

## t25 (work-8b4030): How many of the 136 fresh2026 contest problems one sample (sample 1, the rerun) of Think-SFT plus twice the RL-Math weight change gets right (the other three samples got 69, 70, 75).

Unit: right answers of 136. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh, sample 1)", "samples": 1, "grader": "not stated"}

> fresh2026 sample 1, then hard328 seed 3,200,000, one job

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 71 | [63, 79] | Mean of the other three samples (69, 70, 75) with single-sample noise. |
| reader-2 | 71 | [62, 80] | The other three samples scored 69, 70 and 75, mean 71.3. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 71 | [63, 79] | Single sample; the mechanism adds nothing beyond the other three (69, 70, 75). |
| f2-m02 | 71 | [63, 79] | Single sample: no vote parity; mean of the other three. |
| f2-m03 | 71 | [63, 79] | a=2 hazard fixed; single sample like the other three. |
| f2-m04 | 71 | [64, 78] | Mean 71.3 of three draws; binomial sd ~4. |
| f2-m05 | 71 | [63, 79] | Same drift as the other three samples. |
| f2-m06 | 71 | [63, 79] | Single sample at the others' mean. |

## t26 (work-8b4030): How many of the 328 harder problems one sample (seed 3,200,000) of Think-SFT plus twice the RL-Math weight change gets right (earlier seeds: 234 and 229).

Unit: right answers of 328. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated (seed 3,200,000)", "samples": 1, "grader": "not stated"}

> hard328 a=2 seeds 3,200,000 and 3,300,000

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 231 | [220, 242] | Earlier a=2 seeds scored 234 and 229. |
| reader-2 | 231 | [219, 243] | Earlier seeds scored 234 and 229, with about ±9 seed noise per sample. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 231 | [220, 242] | Single sample at the two earlier seeds' mean. |
| f2-m02 | 231 | [220, 242] | Single sample: no vote; seed mean. |
| f2-m03 | 231 | [220, 242] | Cap hits ~44 at a=2 as before; seed mean. |
| f2-m04 | 231.5 | [221, 242] | Mean of 234 and 229; single-draw sd ~6 plus mean uncertainty. |
| f2-m05 | 231 | [220, 242] | Same template and dose as earlier seeds. |
| f2-m06 | - |  | no forecast |

## t27 (work-8b4030): How many of the 328 harder problems one sample (seed 3,300,000) of Think-SFT plus twice the RL-Math weight change gets right (earlier seeds: 234 and 229).

Unit: right answers of 328. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated (seed 3,300,000)", "samples": 1, "grader": "not stated"}

> hard328 a=2 seeds 3,200,000 and 3,300,000

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 231 | [220, 242] | Earlier a=2 seeds scored 234 and 229. |
| reader-2 | 231 | [219, 243] | Earlier seeds scored 234 and 229, with about ±9 seed noise per sample. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 231 | [220, 242] | Single sample at the two earlier seeds' mean. |
| f2-m02 | 231 | [220, 242] | Single sample: no vote; seed mean. |
| f2-m03 | 231 | [220, 242] | Same hazard, seed mean. |
| f2-m04 | 231.5 | [221, 242] | Same as t26. |
| f2-m05 | 231 | [220, 242] | Same template and dose as earlier seeds. |
| f2-m06 | - |  | no forecast |

## t28 (work-8b4030): How many of the 328 harder problems Think-SFT plus twice the RL-Math weight change gets right under a majority vote over 4 samples (Think-SFT alone: 241; RL: 221).

Unit: right answers of 328 under vote over 4. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated", "samples": 4, "grader": "not stated"}

> hard328 samples 3-4 for the vote over 4

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 246 | [236, 257] | Singles average about 231; the vote gain is smaller than Think-SFT's +32 because a=2 finishes more often with lower precision, so about +15. |
| reader-2 | 245 | [233, 256] | Singles average about 231.5; with fewer cap hits than Think-SFT, the vote gain should be about half of Think-SFT's +32 (on fresh2026: +6.7 vs +15). |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 248 | [238, 258] | Singles ~231.5; a=2's extra finished wrong answers are scattered, so the vote still gains about +16. |
| f2-m02 | 245 | [235, 255] | Even k=4: ties broken by sample 0 cost a few problems against pass@4. |
| f2-m03 | 246 | [236, 256] | a=2 finishes more with lower precision, so the vote adds about half of Think-SFT's +32. |
| f2-m04 | - |  | no forecast |
| f2-m05 | 246 | [236, 256] | RL delta shortens answers so fewer reach the drift zone; vote adds ~+15. |
| f2-m06 | 243 | [233, 253] | Vote/single ~1.05 for a concentrated a=2 model on singles ~231.5. |

## t29 (work-8b4030): How many of the 500 MATH-500 problems one sample of Think-SFT plus twice the RL-Math weight change gets right (a=1 gave 467).

Unit: right answers of 500. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "MATH-500", "n": 500, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> MATH-500 1 sample

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 468 | [459, 477] | a=1 gave 467 on MATH-500; a=2 helped on hard328 but MATH-500 is near ceiling. |
| reader-2 | 466 | [455, 476] | a=1 scored 467 and Think-SFT 454-462; a=2 keeps MATH-500 about level. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | 469 | [460, 478] | Few MATH-500 cap hits left to convert; a=2 slightly above a=1's 467. |
| f2-m04 | 468 | [460, 476] | One draw near a=1's 467; spread ~5. |
| f2-m05 | 468 | [459, 477] | MATH-500 answers rarely reach the drift zone. |
| f2-m06 | 468 | [459, 477] | Concentration raises short-answer accuracy a little over a=1's 467. |

## t30 (work-dc9359): How many of the 328 harder problems Think-SFT with the cue gets right under a majority vote over 4 samples with a 32,768-token cap (vote at cap 16,384: 241; simulation 240 [232, 248]).

Unit: right answers of 328 under vote over 4. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "T not stated; top-p not stated; token cap 32,768", "samples": 4, "grader": "not stated"}

> Think-SFT + cue vote over 4 at token cap 32,768 on hard328

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 244 | [234, 254] | Vote at 16k is 241 and the simulation says 240-254; late answers are mostly wrong (23 of 93 right), so the gain is small. |
| reader-2 | 245 | [234, 256] | The 16k vote was 241 and the simulation says 240; each sample gains about 7 points at 32k, and late wrong answers likely disagree with each other, so slightly higher. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 250 | [241, 259] | At 32k the cut answers finish (+23 right per sample); late wrong answers disagree with each other, so newly right late answers win problems that had no finished right sample: the simulation's 254 branch, shaded. |
| f2-m02 | 244 | [235, 253] | More finished answers at 32k mean more 2-2 ties at k=4, broken by one random draw; gain small. |
| f2-m03 | 248 | [239, 257] | At 32k Think-SFT's low stop hazard has room: 91 of 93 cut answers finish, ~25 % right; the vote gains a few problems where no 16k sample finished. |
| f2-m04 | - |  | no forecast |
| f2-m05 | 244 | [235, 253] | Raw-template cue answers that run past 16k have often drifted and finish wrong; the vote gains little. |
| f2-m06 | 246 | [237, 255] | Think-SFT stays diffuse enough that finished late answers add a few problems. |

## t31 (work-dc9359): How many of the 136 fresh2026 contest problems Think-SFT with the cue gets right under a majority vote over 4 samples with a 32,768-token cap (at cap 16,384 its vote was 75).

Unit: right answers of 136 under vote over 4. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "T not stated; top-p not stated; token cap 32,768", "samples": 4, "grader": "not stated"}

> fresh2026 (4 samples), each answer scored at 16,384 and 32,768

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 80 | [72, 88] | Vote at 16k is 75 with 46% cap hits on fresh2026; a doubled cap finishes many of them at about 25% right, so a few more problems. |
| reader-2 | 82 | [74, 90] | The 16k vote was 75, with 46% cap hits on fresh2026; the 32k cap converts some of those, as on hard328 (+7 points per sample). |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 83 | [75, 91] | 46 % cap hits at 16k finish at 32k at ~20 % right; scattered wrong values rarely beat them. |
| f2-m02 | 81 | [73, 89] | Converted cap hits add right votes; even-k ties absorb part. |
| f2-m03 | 84 | [76, 92] | 46 % cap hits at 16k on fresh2026: many more unfinished samples to convert than on hard328. |
| f2-m04 | - |  | no forecast |
| f2-m05 | 79 | [71, 87] | Fresh2026 cut answers are long and drifted (104 of 544 switch); few finish right. |
| f2-m06 | 81 | [73, 89] | Diffuse Think-SFT samples on fresh2026; converted caps add a few votes. |
