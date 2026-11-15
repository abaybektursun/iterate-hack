# Forecasts, run-05

Board snapshot 2026-11-15T16:32:52 UTC, written 2026-11-15T16:43:58 UTC. 25 targets; forecasters reader-1, reader-2, r5-m03-rival, r6-account-rival, r6-m06, r7-m05, r7-m08, r7-m11, f2-m01, f2-m02, f2-m03, f2-m04, f2-m05, f2-m06.


Lens of the mechanisms: weight space: the RL weight change, its top directions, scaling and transplanting it


## f2-m01

The top-8 singular directions per matrix of the RL change act as a signed termination dial spread over all layers and both module families: adding them at size s raises, monotonically in s, the chance an answer closes with a boxed result before the cap (negative s lengthens and unboxes), and modestly raises correctness on problems already finished; past 1.5x it closes unfinished hard solutions on guesses. Random rank-8 edits and Think-SFT's directions carry no dial.

Rests on: result-6f1bb7, result-51a0e7, result-95a4dc, result-39497c, result-3387ce. Forecasts 17 of 25 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t01 | 365 | [341, 389] | 350 [322, 380] | 350 [320, 382] |  | disagree: readers discount code to ~40% of the gap, but the dial gave the same ~60-67% share for both Math and Code deltas wherever they were tested. |
| t02 | 383 | [358, 406] | 357 [324, 392] | 362 [328, 395] |  | disagree: readers take about half the code gap, while the dial at 1.5x closed nearly the whole gap on both math sets. |
| t03 | 366 | [336, 394] | 345 [300, 385] | 352 [308, 390] |  | disagree: readers keep the drop but start from a low 1.5x; the dial puts 2x near the 1x level, about 15 above them. |
| t04 | 316 | [301, 331] | 318 [301, 336] | 315 [297, 333] |  | agree: no dial in random directions gives the readers' base-level number. |
| t05 | 350 | [327, 372] | 338 [312, 366] | 334 [310, 360] |  | disagree: readers expect a small transfer, but finishing was written by every reasoning reward's directions on a foreign domain (Code top-8 on math +14). |
| t06 | 52 | [45, 59] | 52 [44, 60] | 53 [43, 62] |  | agree: the same vote-gap share gives the readers' 52-53. |
| t07 | 47 | [41, 53] | 47 [41, 53] | 48 [41, 55] |  | agree: the dial's finishing-plus-lower-precision split lands on the readers' 47-48. |
| t12 | 233 | [219, 247] | 234 [214, 252] | 233 [218, 247] |  | agree: with finishing unchanged the format effect is small, as the readers say. |
| t13 | 203 | [188, 218] | 205 [182, 225] | 207 [190, 222] |  | agree: readers' 205-207 is what an unchanged termination rate gives. |
| t16 | 0.9 | [-3.5, 5.5] | 1.2 [-6, 8.5] | 0.9 [-3.8, 5.5] |  | agree: the mechanism gives the readers' near-zero difference. |
| t17 | -1.2 | [-5.7, 3.3] | -0.6 [-8.5, 7] | 0 [-5, 5] |  | agree: readers already put it at about zero to slightly negative. |
| t20 | 71.3 | [69, 73.8] | 71.3 [68.5, 74.5] | 71.3 [68, 74.8] |  | agree: three of four samples fix the mean at the readers' 71.3. |
| t21 | 79 | [75, 83] | 79 [74, 84] | 79 [74, 84] |  | agree: same as the readers. |
| t22 | 249 | [240, 258] | 248 [238, 258] | 248 [238, 257] |  | agree: readers' 248 is the dial's in-between vote gain. |
| t23 | 464 | [456, 472] | 466 [456, 475] | 465 [455, 474] |  | agree: near the readers' 465-466. |
| t24 | 245 | [236, 254] | 247 [236, 258] | 248 [239, 257] |  | agree: readers' 247-248 is within noise of this. |
| t25 | 80 | [73, 87] | 81 [73, 89] | 82 [74, 90] |  | agree: matches the readers' 81-82 within noise. |

## f2-m02

The RL change beyond its top-8 directions is a dense per-step error reducer: it lowers the base's chance of writing a slip or misreading at each step and makes right answers consistent across samples, but carries no termination drive, so alone it lengthens answers and raises cap hits. Edits holding only top-8 directions match RL per sample by finishing more, yet trail RL under voting and in domains where per-step correctness, not finishing, limits the score.

Rests on: result-284db5, result-51a0e7, result-faf15a, result-95a4dc, result-855858. Forecasts 14 of 25 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t01 | 360 | [336, 384] | 350 [322, 380] | 350 [320, 382] |  | disagree: readers' 350 underrates the top-8 share seen for both Math and Code deltas, though this mechanism keeps it below the full math share. |
| t02 | 374 | [350, 398] | 357 [324, 392] | 362 [328, 395] |  | disagree: readers stop near 360; finishing at 1.5x should add more, but without the bulk it stays short of RL. |
| t03 | 362 | [332, 390] | 345 [300, 385] | 352 [308, 390] |  | agree: close to the readers' 345-352 within the interval, the drop shape is shared. |
| t04 | 316 | [301, 331] | 318 [301, 336] | 315 [297, 333] |  | agree: base Code cue level as the readers say. |
| t05 | 344 | [322, 366] | 338 [312, 366] | 334 [310, 360] |  | agree: readers' 334-338 is within this interval; the mechanism adds a little for transferable finishing. |
| t06 | 51 | [44, 58] | 52 [44, 60] | 53 [43, 62] |  | agree: the vote shortfall gives the readers' 52-53. |
| t07 | 48 | [42, 54] | 47 [41, 53] | 48 [41, 55] |  | agree: same as the readers. |
| t08 | 417 | [411, 423] | 417 [410, 424] | 417 [410, 425] |  | agree: readers' 417. |
| t09 | 423 | [415, 430] | 424 [416, 431] | 424 [416, 432] |  | agree: readers' 424. |
| t10 | 434 | [428, 440] | 435 [428, 442] | 434 [426, 442] |  | agree: readers' 434-435. |
| t20 | 71.3 | [69, 73.8] | 71.3 [68.5, 74.5] | 71.3 [68, 74.8] |  | agree: fixed by the posted samples. |
| t21 | 79 | [75, 83] | 79 [74, 84] | 79 [74, 84] |  | agree: same. |
| t22 | 248 | [239, 257] | 248 [238, 258] | 248 [238, 257] |  | agree: readers' 248. |
| t23 | 465 | [457, 473] | 466 [456, 475] | 465 [455, 474] |  | agree: readers' 465-466. |

## f2-m03

Each direction of an RL change acts only as far as the processed text drives its input (right) singular vectors: Math-RL's top-8 input subspaces are excited 8-11x above random by math-solution text and Code-RL's 6-9x, so an edit works in full on any problem set of its own domain and transfers to another domain in proportion to input-subspace overlap (Math with Code about 0.22-0.26, giving roughly half the in-domain effect).

Rests on: result-a7c052, result-9d979a, result-284db5, result-6f1bb7, result-95a4dc. Forecasts 15 of 25 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t01 | 365 | [341, 389] | 350 [322, 380] | 350 [320, 382] |  | disagree: readers assume weaker effect on code, but code is the Code delta's own domain; only cross-domain edits lose gain (Code top-8 on math got half). |
| t02 | 385 | [360, 408] | 357 [324, 392] | 362 [328, 395] |  | disagree: readers apply a domain discount that the gating account reserves for foreign-domain edits. |
| t03 | 370 | [340, 397] | 345 [300, 385] | 352 [308, 390] |  | disagree: same shape as the readers but from a higher in-domain 1.5x level. |
| t04 | 316 | [301, 331] | 318 [301, 336] | 315 [297, 333] |  | agree: base level. |
| t05 | 350 | [328, 372] | 338 [312, 366] | 334 [310, 360] |  | disagree: readers put transfer near 20 problems; the measured cross-domain ratio of half, applied to a ~66-problem in-domain gain, gives ~33. |
| t06 | 52 | [45, 59] | 52 [44, 60] | 53 [43, 62] |  | agree: same as readers. |
| t07 | 48 | [42, 54] | 47 [41, 53] | 48 [41, 55] |  | agree: readers' 47-48. |
| t08 | 417 | [411, 423] | 417 [410, 424] | 417 [410, 425] |  | agree: readers' 417. |
| t09 | 423 | [415, 430] | 424 [416, 431] | 424 [416, 432] |  | agree: readers' 424. |
| t10 | 434 | [428, 440] | 435 [428, 442] | 434 [426, 442] |  | agree: readers' 434-435. |
| t11 | 1.3 | [-0.2, 2.8] | 1.3 [-0.5, 3.1] | 1.3 [-0.3, 2.9] |  | agree: readers' 1.3. |
| t20 | 71.3 | [69, 73.8] | 71.3 [68.5, 74.5] | 71.3 [68, 74.8] |  | agree: fixed by posted samples. |
| t21 | 79 | [75, 83] | 79 [74, 84] | 79 [74, 84] |  | agree: same. |
| t22 | 249 | [240, 258] | 248 [238, 258] | 248 [238, 257] |  | agree: readers' 248. |
| t23 | 465 | [457, 473] | 466 [456, 475] | 465 [455, 474] |  | agree: readers' 465-466. |

## f2-m04

RL writes its weight change in stages: the first 100 steps move weights along the reasoning-register directions that the cue's opening also drives (step-100 change about 0.03% of weight norm, activations nearly unchanged), giving the cue's gain plus a little precision; the finishing directions and the dense error-reducing remainder accumulate between steps 400 and 2,800. So a cue on an early checkpoint is redundant, and anything built from the final weights carries the late parts.

Rests on: result-fad48d, result-32b7a8, knowledge-87618d, knowledge-9c5052, result-284db5. Forecasts 14 of 25 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t08 | 417 | [411, 423] | 417 [410, 424] | 417 [410, 425] |  | agree: readers' 417. |
| t09 | 420 | [413, 427] | 424 [416, 431] | 424 [416, 432] |  | disagree: readers keep part of sample 0's +9 cue lead, but a cue on a checkpoint whose register is written is redundant, so the new samples regress to plain. |
| t10 | 434 | [428, 440] | 435 [428, 442] | 434 [426, 442] |  | agree: readers' 434-435. |
| t11 | 1.3 | [-0.2, 2.8] | 1.3 [-0.5, 3.1] | 1.3 [-0.3, 2.9] |  | agree: readers' 1.3. |
| t06 | 52 | [45, 59] | 52 [44, 60] | 53 [43, 62] |  | agree: readers' 52-53. |
| t07 | 48 | [42, 54] | 47 [41, 53] | 48 [41, 55] |  | agree: readers' 47-48. |
| t18 | 452 | [446, 458] | 453 [446, 459] | 453 [446, 460] |  | agree: readers' 453. |
| t19 | 454 | [448, 460] | 455 [448, 461] | 455 [447, 462] |  | agree: readers' 455. |
| t20 | 71.3 | [69, 73.8] | 71.3 [68.5, 74.5] | 71.3 [68, 74.8] |  | agree: fixed by posted samples. |
| t21 | 79 | [75, 83] | 79 [74, 84] | 79 [74, 84] |  | agree: same. |
| t22 | 249 | [240, 258] | 248 [238, 258] | 248 [238, 257] |  | agree: readers' 248. |
| t23 | 465 | [457, 473] | 466 [456, 475] | 465 [455, 474] |  | agree: readers' 465-466. |
| t24 | 246 | [237, 255] | 247 [236, 258] | 248 [239, 257] |  | agree: readers' 247-248. |
| t25 | 80 | [73, 87] | 81 [73, 89] | 82 [74, 90] |  | agree: readers' 81-82 within noise. |

## f2-m05

Imitation (Think-SFT) and RL weight changes are orthogonal (cosine -0.00001) and read different input subspaces, so their effects superpose: Think-SFT supplies high precision on finished answers but no termination drive and runs long; adding a(RL - base) adds RL's finishing push without disturbing SFT's precision, costing only on newly finished hard problems. Prompt format changes how the SFT part is engaged, not finishing, so Think-SFT's cap hits follow the token budget.

Rests on: result-e2482e, result-3387ce, result-9d979a, result-818c20, result-c8b994. Forecasts 14 of 25 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t12 | 234 | [220, 248] | 234 [214, 252] | 233 [218, 247] |  | agree: readers' 233-234. |
| t13 | 203 | [188, 218] | 205 [182, 225] | 207 [190, 222] |  | agree: readers' 205-207. |
| t14 | 462 | [453, 471] | 463 [451, 473] | 462 [452, 471] |  | agree: readers' 462-463. |
| t15 | 459 | [449, 468] | 459 [446, 470] | 459 [449, 469] |  | agree: readers' 459. |
| t16 | 1.2 | [-3.5, 6] | 1.2 [-6, 8.5] | 0.9 [-3.8, 5.5] |  | agree: readers' ~1. |
| t17 | -1 | [-5.5, 3.5] | -0.6 [-8.5, 7] | 0 [-5, 5] |  | agree: readers' 0 to -0.6. |
| t20 | 71.3 | [69, 73.8] | 71.3 [68.5, 74.5] | 71.3 [68, 74.8] |  | agree: fixed by posted samples. |
| t21 | 79 | [75, 83] | 79 [74, 84] | 79 [74, 84] |  | agree: same. |
| t22 | 250 | [241, 259] | 248 [238, 258] | 248 [238, 257] |  | agree: readers' 248 within noise. |
| t23 | 465 | [457, 473] | 466 [456, 475] | 465 [455, 474] |  | agree: readers' 465-466. |
| t24 | 246 | [237, 255] | 247 [236, 258] | 248 [239, 257] |  | agree: readers' 247-248. |
| t25 | 80 | [73, 87] | 81 [73, 89] | 82 [74, 90] |  | agree: readers' 81-82 within noise. |
| t06 | 52 | [45, 59] | 52 [44, 60] | 53 [43, 62] |  | agree: readers' 52-53. |
| t07 | 48 | [42, 54] | 47 [41, 53] | 48 [41, 55] |  | agree: readers' 47-48. |

## f2-m06

Weight edits merged in bf16 are realized only where an entry's change exceeds half a unit in the last place of that weight, so small edits are thresholded onto small-magnitude weights and their effective size grows faster than nominal size (a=0.25 acts like about 0.12; top-8 at nominal 1.5 acts like RL's own top-8 share). Smaller deltas such as Code-RL's lose more at 1x and peak at a larger nominal size; trained checkpoints carry no such loss.

Rests on: result-c9b27e, result-6f1bb7, result-4b0d5f, result-17e25e, result-8c92fc. Forecasts 14 of 25 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t01 | 356 | [333, 380] | 350 [322, 380] | 350 [320, 382] |  | agree: readers' 350 is inside this interval; the extra rounding loss at 1x keeps it near them. |
| t02 | 381 | [356, 404] | 357 [324, 392] | 362 [328, 395] |  | disagree: readers stop at ~360; once rounding stops eating the edit, the dial delivers most of the gap, as on math. |
| t03 | 378 | [350, 402] | 345 [300, 385] | 352 [308, 390] |  | disagree: readers copy math's drop at 2x, but the smaller code delta reaches overshoot only at a larger nominal size. |
| t04 | 316 | [301, 331] | 318 [301, 336] | 315 [297, 333] |  | agree: base level. |
| t05 | 345 | [323, 367] | 338 [312, 366] | 334 [310, 360] |  | agree: readers' 334-338 lies inside this interval. |
| t06 | 52 | [45, 59] | 52 [44, 60] | 53 [43, 62] |  | agree: readers' 52-53. |
| t07 | 48 | [42, 54] | 47 [41, 53] | 48 [41, 55] |  | agree: readers' 47-48. |
| t08 | 417 | [411, 423] | 417 [410, 424] | 417 [410, 425] |  | agree: readers' 417. |
| t09 | 423 | [415, 430] | 424 [416, 431] | 424 [416, 432] |  | agree: readers' 424. |
| t10 | 434 | [428, 440] | 435 [428, 442] | 434 [426, 442] |  | agree: readers' 434-435. |
| t20 | 71.3 | [69, 73.8] | 71.3 [68.5, 74.5] | 71.3 [68, 74.8] |  | agree: fixed by posted samples. |
| t21 | 79 | [75, 83] | 79 [74, 84] | 79 [74, 84] |  | agree: same. |
| t22 | 248 | [239, 257] | 248 [238, 258] | 248 [238, 257] |  | agree: readers' 248. |
| t23 | 465 | [457, 473] | 466 [456, 475] | 465 [455, 474] |  | agree: readers' 465-466. |

## t01 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems does the Olmo 3 base pass with Code-RL 3.1's top 8 weight directions per matrix added at 1x size, using the Code cue at T 1.0?

Unit: problems passed of 538. Cell: {"model": "Olmo-3-1025-7B base + top-8 directions per matrix of Olmo-3.1 RL-Zero-Code delta at 1x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p and token cap not stated", "samples": "not stated", "grader": "not stated"}

> base + Code 3.1's 8 directions at 1x, 1.5x, 2x

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 350 | [322, 380] | Base+Code cue 317, RL-Code 401; on math the 8 directions at 1x closed about two thirds of the hard328 gap (164->192 vs 206), assumed weaker on code tasks. |
| reader-2 | 350 | [320, 382] | Base Code cue 317 vs RL-Code 401; on math the top-8 at 1x closed about two thirds of the gap (164->192 of 206), so about 60% of the 84-problem code gap with extra uncertainty for a new domain. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 365 | [341, 389] | On math, own-reward top-8 at 1x gave 67% (Math, 28/42) and 61% (Code on math, 14/23) of the full delta's gain; 317 + 0.57*84. |
| f2-m02 | 360 | [336, 384] | Top-8 alone gives finishing but not the dense error reducer; on math that was ~2/3 of the gain at 1x; code's equal-token gap is less a finishing gap, so a bit lower: 317 + 0.51*84. |
| f2-m03 | 365 | [341, 389] | In-domain: code text drives Code-RL's input subspace as math text drives Math's, so the math in-domain share at 1x (~0.6-0.67) applies: 317 + 0.57*84. |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | 356 | [333, 380] | Code-RL's change is smaller (0.109% vs 0.13% rel norm), so more of its top-8 is rounded away at 1x: a little under math's 1x share. |

## t02 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems does the Olmo 3 base pass with Code-RL 3.1's top 8 weight directions per matrix added at 1.5x size, using the Code cue at T 1.0?

Unit: problems passed of 538. Cell: {"model": "Olmo-3-1025-7B base + top-8 directions per matrix of Olmo-3.1 RL-Zero-Code delta at 1.5x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p and token cap not stated", "samples": "not stated", "grader": "not stated"}

> base + Code 3.1's 8 directions at 1x, 1.5x, 2x

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 357 | [324, 392] | On math 1.5x matched RL (203/200 vs 206, 456 vs 457 MATH-500); on code the share is expected lower, so about half to two thirds of the 84-problem gap. |
| reader-2 | 362 | [328, 395] | On math, 1.5x top-8 matched RL (203/200.25 vs 206/200; 456 vs 457); code probably transfers less, so about 55% of the 317->401 gap. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 383 | [358, 406] | 1.5x closed 93-100% of the gap on hard328 and MATH-500; allow some loss on a new domain: 317 + 0.79*84. |
| f2-m02 | 374 | [350, 398] | 1.5x saturates finishing; the missing bulk caps it about 25 below RL-Code 401. |
| f2-m03 | 385 | [360, 408] | In-domain 1.5x closed ~95% on math; allow a margin: 317 + 0.81*84. |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | 381 | [356, 404] | At 1.5x most entries clear the threshold; effective size near 1.25, about 0.76 of the 84-problem gap. |

## t03 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems does the Olmo 3 base pass with Code-RL 3.1's top 8 weight directions per matrix added at 2x size, using the Code cue at T 1.0?

Unit: problems passed of 538. Cell: {"model": "Olmo-3-1025-7B base + top-8 directions per matrix of Olmo-3.1 RL-Zero-Code delta at 2x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p and token cap not stated", "samples": "not stated", "grader": "not stated"}

> base + Code 3.1's 8 directions at 1x, 1.5x, 2x

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 345 | [300, 385] | On math 2x fell back from 1.5x (190 vs 203) as cap hits vanish and precision drops; same shape assumed on code. |
| reader-2 | 352 | [308, 390] | On math, 2x lost ground to 1.5x (190 vs 203, with almost no cap hits and lower precision), so a small drop from 1.5x with a wider downside. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 366 | [336, 394] | At 2x the dial overshoots (cap hits 46->5 on math, precision 0.65->0.59, right 203->190), so fall back to about the 1x level. |
| f2-m02 | 362 | [332, 390] | 2x over-finishes with no added per-step accuracy, so it drops back toward 1x. |
| f2-m03 | 370 | [340, 397] | In-domain 2x overshoots as on math (203->190 from 1.5x to 2x). |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | 378 | [350, 402] | Code's effective size at nominal 2x is like math's ~1.7x, still near the peak, so no drop from 1.5x. |

## t04 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems does the Olmo 3 base pass with a random weight edit at 1.5x size (control for the Code-RL directions), using the Code cue at T 1.0?

Unit: problems passed of 538. Cell: {"model": "Olmo-3-1025-7B base + random (rank-8) edit at 1.5x, size-matched control", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p and token cap not stated", "samples": "not stated", "grader": "not stated"}

> random at 1.5x

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 318 | [301, 336] | Random rank-8 edits stayed flat at every size on math (158-167 vs base 164; 159 at 1.5x), so this should be near base+Code cue 317 plus sampling noise. |
| reader-2 | 315 | [297, 333] | Random rank-8 edits were flat at every size on math (158-167 vs base 164), so the base Code cue 317 with sampling noise of about 11 problems. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 316 | [301, 331] | Random rank-8 edits are flat at every size (158-167 vs base 164 on math), so base Code cue 317 plus seed noise. |
| f2-m02 | 316 | [301, 331] | Random rank-8 carries neither finishing nor error reduction. |
| f2-m03 | 316 | [301, 331] | A random input subspace is not driven by code text beyond chance. |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | 316 | [301, 331] | Random rank-8 realized the same way but has no function: flat at base. |

## t05 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems does the Olmo 3 base pass with Math-RL 3.1's top 8 weight directions per matrix added at 1.5x size, using the Code cue at T 1.0?

Unit: problems passed of 538. Cell: {"model": "Olmo-3-1025-7B base + top-8 directions per matrix of Olmo-3.1 RL-Zero-Math delta at 1.5x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p and token cap not stated", "samples": "not stated", "grader": "not stated"}

> and Math 3.1's at 1.5x, on HumanEval+ and MBPP+

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 338 | [312, 366] | Math-RL also helps code (LCB 21.9 vs base 10.1, Math cue 326 on this set) and Code top-8 helped math (178 vs 164), so a partial transfer above 317. |
| reader-2 | 334 | [310, 360] | Off-domain directions help some (Code top-8 gave +14 on hard328; Math cue on code 326; Math RL transfers to LiveCodeBench), so a modest gain over 317. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 350 | [327, 372] | Math, Code and IF directions all wrote finishing on math; Math's dial at 1.5x on code gives its finishing share, about 40% of the code gap. |
| f2-m02 | 344 | [322, 366] | Math top-8 brings finishing to code but no code-specific error reduction; partial gain. |
| f2-m03 | 350 | [328, 372] | Math's top-8 on code text: about half of an in-domain 1.5x gain (overlap 0.22-0.26; Code top-8 on math gave 14 vs Math's 28): 317 + 0.5*66. |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | 345 | [323, 367] | Math's larger top-8 survives rounding at 1.5x; foreign domain gives a partial gain. |

## t06 (work-16773f): On the 136 fresh2026 contest problems, how many does the base plus 1.5x the top 8 RL-Math directions (with the cue) get right under a majority vote over 4 samples?

Unit: right answers of 136 (vote over 4). Cell: {"model": "Olmo-3-1025-7B base + 1.5 x top-8 directions of (RL-Math 3.1 - base)", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> is it level with RL (57 vote, 50.5 single)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 52 | [44, 60] | The 1.5x edit matched RL's single samples on hard328 but trailed RL's vote by 7 (214 vs 221); RL's fresh vote is 57, so a little below it. |
| reader-2 | 53 | [43, 62] | On hard328 the 1.5x edit matched RL single but trailed its vote by 7 (214 vs 221); fresh2026 RL vote is 57 and base vote 38. |
| r5-m03-rival | 54 | [47, 61] | Theory: the top-8 edit puts the base on a weak dose of RL's own policy (with the cue, no plain-base share), so the vote should sit just under RL's 57, as the 1.5x edit's hard328 vote did (214 vs RL 221). |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 52 | [45, 59] | On hard328 the 1.5x vote closed 76% of the base-to-RL vote gap (192->214 vs 221); 38 + 0.76*19. |
| f2-m02 | 51 | [44, 58] | Without the bulk, right answers are less consistent across samples: on hard328 the edit's vote trailed RL's by 7 at equal singles; scale to fresh: 57 - 6. |
| f2-m03 | 52 | [45, 59] | fresh2026 is math text, so the edit acts as on hard328: 76% of the vote gap. |
| f2-m04 | 52 | [45, 59] | The edit is taken from the final weights, so it carries the late finishing directions; vote as on hard328 (76% of gap). |
| f2-m05 | 52 | [45, 59] | Cue and edit superpose (opening from the cue, finishing from the edit); vote gap share as on hard328. |
| f2-m06 | 52 | [45, 59] | Same realized edit as on hard328 (same tensors, same rounding), so the same 76% vote-gap share. |

## t07 (work-16773f): On the 136 fresh2026 contest problems, how many does the base plus 1.5x the top 8 RL-Math directions (with the cue) get right per single sample, averaged over 4 samples?

Unit: mean right answers of 136 per single sample. Cell: {"model": "Olmo-3-1025-7B base + 1.5 x top-8 directions of (RL-Math 3.1 - base)", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> is it level with RL (57 vote, 50.5 single)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 47 | [41, 53] | The edit equalled RL per sample on hard328 (200.25 vs 200.0); RL's fresh single is 50.5 and base+cue 29.5, shrunk slightly because the size was chosen on the 328. |
| reader-2 | 48 | [41, 55] | The edit matched RL single on hard328 and MATH-500; RL single on fresh2026 is 50.5 and base 29.5, minus a little because the size was chosen on the 328. |
| r5-m03-rival | 49 | [44, 54.5] | Theory: answers follow a weak dose of RL's policy, so one sample should be about level with RL's 50.5 of 136, slightly below, as the 1.5x edit matched RL per sample on hard328 (200.25 vs 200). |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 47 | [41, 53] | Edit matched RL per sample on hard328 and MATH-500; fresh base caps 40% are cut, but newly finished hard problems are right less often, so a little under RL's 50.5. |
| f2-m02 | 48 | [42, 54] | Per sample the edit matched RL by finishing; fresh precision a little lower without the bulk. |
| f2-m03 | 48 | [42, 54] | In-domain held-out set: edit about equals RL's 50.5 per sample, minus a little for the size chosen on the 328. |
| f2-m04 | 48 | [42, 54] | Late finishing directions at 1.5x matched RL per sample on two sets. |
| f2-m05 | 48 | [42, 54] | Superposed finishing reaches RL-level single on held-out math, minus selection shrinkage. |
| f2-m06 | 48 | [42, 54] | Same realized edit matched RL per sample on two sets; slight shrink on new problems. |

## t08 (work-f8ecb6): Averaged over 4 samples (posted sample 0 plus 3 new), how many of the 500 MATH-500 problems does the RL-Zero-Math step-100 checkpoint get right with the plain prompt at T 1.0, grader v3?

Unit: mean right answers of 500 over 4 samples. Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math step 100", "prompt": "plain", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and token cap not stated", "samples": 4, "grader": "v3"}

> ckptcue3: 3 more samples of step-100 plain, step-100 cue, step-400 plain (MATH-500, T 1.0, v3)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 417 | [410, 424] | Posted sample 0 is 418; 3 new samples pulled slightly toward the cued-base level, with a per-sample sd of about 6. |
| reader-2 | 417 | [410, 425] | Sample 0 = 418; 3 new samples carry seed noise of about 5 problems each, centred near the observed value. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 417 | [411, 423] | The bulk error reducer arrives late (activation divergence mostly after step 100), so step 100 sits near sample 0's 418. |
| f2-m03 | 417 | [411, 423] | Step-100 change lies in the same text-driven reasoning subspace as the final model's (nearest neighbour its own family); sample 0 418. |
| f2-m04 | 417 | [411, 423] | Step 100 = register stage; sample 0 418, per-sample sd ~6. |
| f2-m05 | - |  | no forecast |
| f2-m06 | 417 | [411, 423] | Real checkpoint, no merge rounding: sample 0 418 with seed noise. |

## t09 (work-f8ecb6): Averaged over 4 samples (posted sample 0 plus 3 new), how many of the 500 MATH-500 problems does the RL-Zero-Math step-100 checkpoint get right with the opening cue at T 1.0, grader v3?

Unit: mean right answers of 500 over 4 samples. Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math step 100", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and token cap not stated", "samples": 4, "grader": "v3"}

> ckptcue3: 3 more samples of step-100 plain, step-100 cue, step-400 plain (MATH-500, T 1.0, v3)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 424 | [416, 431] | Posted cue sample 427 and the cue adds +1.8 [-1.2, 4.8] on step 100, so 3 new samples are expected near 423. |
| reader-2 | 424 | [416, 432] | Sample 0 = 427, pulled slightly toward step-100 plain because the cue added only +1.8 [-1.2, 4.8]. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 423 | [415, 430] | Sample 0 427 regresses toward plain; the cue adds no error reduction. |
| f2-m03 | 423 | [415, 430] | The cue drives the same input subspace the step-100 change already uses, so it adds little: regress 427 toward plain. |
| f2-m04 | 420 | [413, 427] | The register is already installed at step 100, so the cue adds ~0: new samples near plain ~417, mean with 427 about 420. |
| f2-m05 | - |  | no forecast |
| f2-m06 | 423 | [415, 430] | Real checkpoint; sample 0 427 regresses toward plain. |

## t10 (work-f8ecb6): Averaged over 4 samples (posted sample 0 plus 3 new), how many of the 500 MATH-500 problems does the RL-Zero-Math step-400 checkpoint get right with the plain prompt at T 1.0, grader v3?

Unit: mean right answers of 500 over 4 samples. Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math step 400", "prompt": "plain", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and token cap not stated", "samples": 4, "grader": "v3"}

> ckptcue3: 3 more samples of step-100 plain, step-100 cue, step-400 plain (MATH-500, T 1.0, v3)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 435 | [428, 442] | Posted step-400 plain sample is 436; mean of 4 with a little regression. |
| reader-2 | 434 | [426, 442] | Sample 0 = 436 with slight regression; seed noise of about 5 problems per sample. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 434 | [428, 440] | Step 400 holds part of the bulk; sample 0 436 with regression. |
| f2-m03 | 434 | [428, 440] | Sample 0 436 with slight regression. |
| f2-m04 | 434 | [428, 440] | Step 400 holds part of the late stage (+3.6 over step 100); sample 0 436 with regression. |
| f2-m05 | - |  | no forecast |
| f2-m06 | 434 | [428, 440] | Real checkpoint; sample 0 436 with regression. |

## t11 (work-f8ecb6): On MATH-500 at T 1.0 with grader v3, by how many points does the RL step-100 checkpoint with the plain prompt beat the untrained base with the opening cue, averaged over 4 samples each?

Unit: difference in points (step-100 plain minus cued base), 4 samples. Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math step 100 (plain) vs Olmo-3-1025-7B base (cue)", "prompt": "plain vs cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and token cap not stated", "samples": 4, "grader": "v3"}

> so the step-100 vs cued-base difference has a 4-sample interval

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 1.3 | [-0.5, 3.1] | Step-100 plain 4-sample mean of about 417 minus the cued base's 4-sample mean of 410.5, in points of 500. |
| reader-2 | 1.3 | [-0.3, 2.9] | Step-100 plain mean about 417 minus the cued base's 4-sample mean of 410.5, divided by 5 points per problem. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | 1.3 | [-0.2, 2.8] | Step-100 plain ~417 minus cued base 410.5 over 5 problems per point. |
| f2-m04 | 1.3 | [-0.2, 2.8] | Step 100 = cued base plus a little precision: (417 - 410.5)/5. |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t12 (work-8b2ec9): How many of the 328 harder problems does Think-SFT get right in its own ChatML <think> chat format (no base cue) at T 1.0 with a 32,768-token cap, one sample, grader v3?

Unit: right answers of 328. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "Think-SFT's own ChatML chat template with <think>", "set": "hard328", "n": 328, "sampling": "T 1.0, token cap 32,768; top-p not stated", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 234 | [214, 252] | Raw template + cue gives 230 at cap 32,768; the native ChatML <think> format it was trained on should be similar or slightly better. |
| reader-2 | 233 | [218, 247] | Think-SFT with the raw template and cue scores 230 at cap 32k; its native format should be similar or slightly better (smoke 7/8 right). |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 233 | [219, 247] | Think-SFT has no dial directions; native format cannot change its finishing, so at 32k it equals the raw+cue run (230) plus a little. |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | 234 | [220, 248] | Native format engages the SFT part fully but adds no finishing; at 32k nearly all its work finishes: raw 230 plus a small format gain. |
| f2-m06 | - |  | no forecast |

## t13 (work-8b2ec9): How many of the 328 harder problems does Think-SFT get right in its own ChatML <think> chat format at T 1.0 when the same answers are scored at a 16,384-token cap, one sample, grader v3?

Unit: right answers of 328. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "Think-SFT's own ChatML chat template with <think>", "set": "hard328", "n": 328, "sampling": "T 1.0, same answers scored at token cap 16,384; top-p not stated", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 205 | [182, 225] | Raw + cue gives 207 at 16,384; the native format may think longer, so a few more cap hits at 16k. |
| reader-2 | 207 | [190, 222] | Cue run at 16k from the same answers gave 207; native thinking may run a little longer, so more answers get cut. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 203 | [188, 218] | Same answers at 16k: cap hits stay at Think-SFT's ~29% level without a dial, maybe a few more from longer native thinking. |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | 203 | [188, 218] | At 16k cap hits stay at Think-SFT's level (no RL push), possibly a few more if native traces run longer. |
| f2-m06 | - |  | no forecast |

## t14 (work-8b2ec9): How many of the 500 MATH-500 problems does Think-SFT get right in its own ChatML <think> chat format (no base cue) at T 1.0 with a 32,768-token cap, one sample, grader v3?

Unit: right answers of 500. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "Think-SFT's own ChatML chat template with <think>", "set": "MATH-500", "n": 500, "sampling": "T 1.0, token cap 32,768; top-p not stated", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 463 | [451, 473] | Think-SFT + cue singles are 454-462 on MATH-500; the 32k cap and native boxed answers may add a couple of points. |
| reader-2 | 462 | [452, 471] | Think-SFT cue single samples score 454-462 on MATH-500, and the 32k cap adds little there. |
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
| f2-m05 | 462 | [453, 471] | MATH-500 answers mostly finish under 32k; SFT precision unchanged by format: cue singles 454-462 plus native answer-line credit. |
| f2-m06 | - |  | no forecast |

## t15 (work-8b2ec9): How many of the 500 MATH-500 problems does Think-SFT get right in its own ChatML <think> chat format at T 1.0 when the same answers are scored at a 16,384-token cap, one sample, grader v3?

Unit: right answers of 500. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "Think-SFT's own ChatML chat template with <think>", "set": "MATH-500", "n": 500, "sampling": "T 1.0, same answers scored at token cap 16,384; top-p not stated", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 459 | [446, 470] | Same answers cut at 16,384 lose a few long ones relative to 32k. |
| reader-2 | 459 | [449, 469] | Same answers at 16k lose a few long ones; Think-SFT cue singles at 16k score 454-462. |
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
| f2-m05 | 459 | [449, 468] | Same answers at 16k lose a few long ones. |
| f2-m06 | - |  | no forecast |

## t16 (work-8b2ec9): On the 328 harder problems at T 1.0 with a 32,768-token cap, by how many points does Think-SFT in its own ChatML <think> format beat Think-SFT with the raw template and the base's cue (230 of 328)?

Unit: difference in points (native format minus raw template + cue), paired. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "own ChatML template with <think> vs raw template + base cue (230)", "set": "hard328", "n": 328, "sampling": "T 1.0, token cap 32,768; top-p not stated", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 1.2 | [-6, 8.5] | Native minus cue (230) at 32k: format effect is small and uncertain; one-sample seed noise on 328 is about 3 points. |
| reader-2 | 0.9 | [-3.8, 5.5] | About 233 native vs 230 cue, as points of 328, with paired single-sample noise of about 2.7 points. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 0.9 | [-3.5, 5.5] | Native minus raw at 32k: no change in finishing, small format effect. |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | 1.2 | [-3.5, 6] | Format affects only the SFT part; small difference at 32k. |
| f2-m06 | - |  | no forecast |

## t17 (work-8b2ec9): On the 328 harder problems at T 1.0 scored at a 16,384-token cap, by how many points does Think-SFT in its own ChatML <think> format beat Think-SFT with the raw template and the base's cue (207 of 328)?

Unit: difference in points (native format minus raw template + cue), paired. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "own ChatML template with <think> vs raw template + base cue (207)", "set": "hard328", "n": 328, "sampling": "T 1.0, scored at token cap 16,384; top-p not stated", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | -0.6 | [-8.5, 7] | Native minus cue (207) at 16k: about equal, possibly slightly lower from longer native thinking. |
| reader-2 | 0 | [-5, 5] | About 207 native vs 207 cue at 16k; native may think longer, which offsets any format gain. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | -1.2 | [-5.7, 3.3] | At 16k a format without a stop drive can only add cap hits, so slightly negative. |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | -1 | [-5.5, 3.5] | No finishing push at 16k; longer native thinking costs slightly. |
| f2-m06 | - |  | no forecast |

## t18 (work-60f040): How many of the 500 MATH-500 problems does the untrained Olmo 3 base with the opening cue get right under a majority vote over 9 samples at T 1.0, grader v3?

Unit: right answers of 500 (vote over 9). Cell: {"model": "Olmo-3-1025-7B base", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and token cap not stated", "samples": 9, "grader": "v3"}

> vote over 9 = 456 [449, 462] of 500 (result-c637b2)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 453 | [446, 459] | Vote over 4 gives 446; Wang's majority curve gains about 2.5 points from 4 to 8; pass@4 467 bounds it from above. |
| reader-2 | 453 | [446, 460] | Vote over 4 = 446 (450 after restart); Wang's majority curve adds about 2.5 points from 4 to 8 samples, and votes ran below independence predictions. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 456 | [449, 462] | The rival's closing sentence says a base-only vote over more samples recovers part of the sharpening share and predicts 456/500 (the vote-over-9 number with interval [449, 462] carried from r6-account, result-c637b2). |
| r6-m06 | 452 | [444, 459] | In scope (cued base, MATH-500, T 1.0, v3): the theory says the base's wrong steps come from the head of its own distribution, so many errors repeat across samples, and voting gains only a few points over the stored vote over 4 (446, 450 after restart) from a single-sample level of 405-418; it stays a little below the 456 that result-c637b2 predicted. |
| r7-m05 | 453 | [446, 460] | In scope (cued base, MATH-500, T 1.0, v3): the theory puts misreads and slips near the mode of the base's prior, and redoing a step repeats them (result-855858), so some errors come back in every sample and voting levels off; going from the vote over 4 of 446 (result-5d032f) that suggests a gain of about 7, not the independent-sample 456. |
| r7-m08 | 451 | [445, 457] | The theory's no_intervention clause says the base rates its own misread/slip steps as likely, so no base-only rule can veto them and selection among base samples is capped near the measured vote over 4 (446-450); more samples add only a few points and stay below RL's 456-463. |
| r7-m11 | 452 | [446, 458] | The statement says wrong answers drawn under the one shared cue opening agree with each other, so on the 21 problems between pass@4 (467) and the vote over 4 (446) more cued samples keep feeding the same wrong group; the vote over 9 should rise only a little above 446 (odd k also removes ties) and stay below the 456 that independent slips would give (result-c637b2). |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | 452 | [446, 458] | The base lacks the late-stage weights; voting only reorders its own answers, so vote 9 adds ~6 over vote 4 (446) and stays under pass@4 467. |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t19 (work-60f040): How many of the 500 MATH-500 problems does the untrained Olmo 3 base with the opening cue get right under a majority vote over 12 samples at T 1.0, grader v3?

Unit: right answers of 500 (vote over 12). Cell: {"model": "Olmo-3-1025-7B base", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and token cap not stated", "samples": 12, "grader": "v3"}

> Vote over k = 1..12 samples of the untrained cued base on MATH-500

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 455 | [448, 461] | Vote over 12 adds about 2 problems over 9 as the gains flatten. |
| reader-2 | 455 | [447, 462] | Vote keeps plateauing toward pass@4 = 467 with diminishing returns beyond 9 samples. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 457 | [450, 463] | Same 'base-only vote recovers part of sharpening' clause (456 at 9 votes); with sharpening only partly recoverable and reach (kB=0) not at all, 3 more votes add about 1 problem on the plateau. |
| r6-m06 | 453 | [445, 461] | Same head-error mechanism: errors the base draws from its head repeat across samples, so the vote levels off after about 9 samples, and 12 samples add about 1 point over the vote over 9. |
| r7-m05 | 455 | [447, 462] | Same mode-error argument as t18: errors that recur across samples cap the vote, so k=12 adds only about 2 over k=9, starting from 446 at k=4 (the hazard fit puts the vote about 10 below the independent prediction, result-e41d94). |
| r7-m08 | 452 | [446, 458] | Same no_intervention clause: the base's wrong steps are high-probability, so voting over 12 base samples plateaus a couple of points above vote over 4 (446-450) and does not reach RL's veto-driven 456-463. |
| r7-m11 | 453 | [447, 459] | Same mechanism: wrong groups set by the context put a ceiling on the vote whatever k is, so going from 9 to 12 cued samples adds about one problem; it stays under the independent-slip curve, with 446 at k=4 as the anchor. |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | 454 | [448, 460] | Diminishing gains from 9 to 12 votes. |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t20 (work-8b4030): On the 136 fresh2026 contest problems, how many does Think-SFT plus twice the RL-Math weight change get right per single sample, averaged over all 4 samples?

Unit: mean right answers of 136 per single sample. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> Think-SFT + 2 x (RL-Math - base) on fresh2026 (136 problems, 4 samples, seeds of SPEC_fresh)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 71.3 | [68.5, 74.5] | 3 of 4 samples are already posted (69, 70, 75); the 4th is expected near 71 +- 5. |
| reader-2 | 71.3 | [68, 74.8] | Three samples of 69, 70 and 75 give a mean of 71.3; a fourth sample with SD of about 4 moves the mean by about 1. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 71.3 | [69, 73.8] | Three posted samples 69/70/75 (cap hits 47 vs Think-SFT 63: the RL delta carries the dial); fourth near the mean. |
| f2-m02 | 71.3 | [69, 73.8] | Posted 69/70/75; the full delta includes the bulk, which on top of Think-SFT changes precision little. |
| f2-m03 | 71.3 | [69, 73.8] | Think-SFT writes math-solution text, which drives RL-Math's input subspace as the base's text does, so the transplanted delta acts in full; posted 69/70/75. |
| f2-m04 | 71.3 | [69, 73.8] | Late-stage finishing transplanted onto Think-SFT; posted 69/70/75. |
| f2-m05 | 71.3 | [69, 73.8] | Superposed finishing on SFT precision; posted 69/70/75. |
| f2-m06 | 71.3 | [69, 73.8] | The delta re-rounded onto Think-SFT's different weights keeps a similar share, so a=2 acts like ~1.6; posted 69/70/75. |

## t21 (work-8b4030): On the 136 fresh2026 contest problems, how many does Think-SFT plus twice the RL-Math weight change get right under a majority vote over 4 samples?

Unit: right answers of 136 (vote over 4). Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> Think-SFT + 2 x (RL-Math - base) on fresh2026 (136 problems, 4 samples, seeds of SPEC_fresh)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 79 | [74, 84] | Vote over 3 is already 78; a 4th sample adds little. |
| reader-2 | 79 | [74, 84] | Vote over 3 = 78; for Think-SFT, a 4th vote added about 1. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 79 | [75, 83] | Vote over 3 = 78; with the dial the a=2 model finishes more, so a fourth vote adds about one. |
| f2-m02 | 79 | [75, 83] | Vote over 3 is 78; one more vote adds about 1. |
| f2-m03 | 79 | [75, 83] | Vote over 3 78 plus about one. |
| f2-m04 | 79 | [75, 83] | Vote over 3 78 plus about one. |
| f2-m05 | 79 | [75, 83] | Vote over 3 78 plus about one. |
| f2-m06 | 79 | [75, 83] | Vote over 3 78 plus about one. |

## t22 (work-8b4030): On the 328 harder problems, how many does Think-SFT plus twice the RL-Math weight change get right under a majority vote over 4 samples (two posted, two new)?

Unit: right answers of 328 (vote over 4). Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated", "samples": 4, "grader": "not stated"}

> hard328 samples 3-4 for the vote over 4

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 248 | [238, 258] | Singles 234/229; the vote gain sits between RL's +21 and Think-SFT's +32 since a=2 cap hits are fewer (54). |
| reader-2 | 248 | [238, 257] | Singles 234 and 229; Think-SFT's vote added 32 over its single mean, and RL/edit votes added 14-21; a=2 has fewer cap hits, so the gain is in between. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 249 | [240, 258] | Singles 234/229; the dial cuts abstentions (cap 54 vs 94.5), so wrong finished answers vote and the gain sits between RL's +21 and Think-SFT's +32. |
| f2-m02 | 248 | [239, 257] | Full delta carries the bulk's cross-sample consistency, so the vote gain is RL-like (+16 to +21) on singles near 231. |
| f2-m03 | 249 | [240, 258] | Same in-domain transplant on hard328: singles ~231 plus an RL-like vote gain. |
| f2-m04 | 249 | [240, 258] | Singles ~231; late finishing makes wrong answers vote, gain between RL's and Think-SFT's. |
| f2-m05 | 250 | [241, 259] | SFT precision is kept on old finishers, the added finishers are right ~30%; vote over singles ~231 gains ~19. |
| f2-m06 | 248 | [239, 257] | Singles ~231, RL-like vote gain. |

## t23 (work-8b4030): How many of the 500 MATH-500 problems does Think-SFT plus twice the RL-Math weight change get right in one sample?

Unit: right answers of 500. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "MATH-500", "n": 500, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> MATH-500 1 sample

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 466 | [456, 475] | a=1 scored 467 on MATH-500 and Think-SFT singles 454-462; a=2 was better on hard328, so near 466. |
| reader-2 | 465 | [455, 474] | a=1 scored 467 on MATH-500 and Think-SFT 457-462; a=2 sits near the ceiling with seed noise. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 464 | [456, 472] | MATH-500 has few Think-SFT cap hits (25), so a=2's extra finishing adds little over a=1's 467; slight precision loss. |
| f2-m02 | 465 | [457, 473] | a=1 467; a=2 adds finishing on few MATH-500 cap hits and slight overshoot. |
| f2-m03 | 465 | [457, 473] | In-domain; a=1 467, a=2 near the ceiling. |
| f2-m04 | 465 | [457, 473] | a=1 467; little room on MATH-500. |
| f2-m05 | 465 | [457, 473] | MATH-500 has few SFT cap hits, so the added push changes little: near a=1's 467. |
| f2-m06 | 465 | [457, 473] | Effective size ~1.6 sits below the a=3-4 decline; near a=1's 467. |

## t24 (work-dc9359): On the 328 harder problems, how many does Think-SFT with the cue get right under a majority vote over 4 samples when the token cap is 32,768?

Unit: right answers of 328 (vote over 4). Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "token cap 32,768; temperature and top-p not stated", "samples": 4, "grader": "not stated"}

> Think-SFT + cue vote over 4 at token cap 32,768 on hard328 (samples 1-3 new, sample 0 = the cap32 run)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 247 | [236, 258] | 16k vote is 241; the offline simulation says 240 unless late wrong answers disagree (254); hard-problem wrong answers usually differ. |
| reader-2 | 248 | [239, 257] | Vote at 16k = 241, near pass@4; at 32k single rises 207->230, and diverse late wrong answers should mostly not outvote, so a modest gain above the 240 simulation. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 245 | [236, 254] | Without a dial, Think-SFT's 16-32k completions are slow unfinished work right ~25% of the time; they mostly add scattered wrong votes, so a few above 241. |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | 246 | [237, 255] | Think-SFT has no late RL finishing stage; its extra 16-32k completions are mostly wrong and scattered, so a few votes over 241. |
| f2-m05 | 246 | [237, 255] | Without the RL push the 32k budget lets Think-SFT finish its own slow work (single 207->230), but late answers are 25% right and add scattered votes: a few over 241. |
| f2-m06 | - |  | no forecast |

## t25 (work-dc9359): On the 136 fresh2026 contest problems, how many does Think-SFT with the cue get right under a majority vote over 4 samples when the token cap is 32,768?

Unit: right answers of 136 (vote over 4). Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "token cap 32,768; temperature and top-p not stated", "samples": 4, "grader": "not stated"}

> and fresh2026 (4 samples), each answer scored at 16,384 and 32,768

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 81 | [73, 89] | 16k vote is 75 with 46% cap hits; at 32k many unfinished answers complete (hard328 singles +7 points), so a few more votes are right. |
| reader-2 | 82 | [74, 90] | Vote at 16k = 75 with 46% cap hits; at 32k many more answers finish at about 25% late precision, which adds several right answers. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 80 | [73, 87] | Fresh has 46% cap hits at 16k; the longer budget finishes many, adding about 5 right votes over 75. |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | 80 | [73, 87] | 46% cap hits at 16k; longer budget finishes many at low precision, about +5 over 75. |
| f2-m05 | 80 | [73, 87] | Fresh 46% cap hits at 16k; budget-driven finishing adds ~5 right votes. |
| f2-m06 | - |  | no forecast |
