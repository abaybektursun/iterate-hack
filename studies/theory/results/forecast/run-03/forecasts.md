# Forecasts, run-03

Board snapshot 2026-11-15T16:32:52 UTC, written 2026-11-15T16:44:38 UTC. 23 targets; forecasters reader-1, reader-2, r5-m03-rival, r6-account-rival, r6-m06, r7-m05, r7-m08, r7-m11, f2-m01, f2-m02, f2-m03, f2-m04, f2-m05, f2-m06.


Lens of the mechanisms: when and how the model stops: token cap, loops, end-of-text, answer markers


## f2-m01

A sample that hits the token cap casts no vote, so the cap acts as a free precision filter that discards long, low-precision answers. A vote gains most over one sample when many wrong answers are cut this way (cued base, Think-SFT) and least when a change makes the model finish (top-8 edit, RL delta on Think-SFT, longer cap), because finished guesses then compete with right answers. An odd number of votes removes tie losses.

Rests on: result-818c20, result-95a4dc, result-5251c9, result-5c961a, result-5d032f, result-cbe0bc. Forecasts 12 of 23 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t06 | 49.5 | [43, 56] | 52 [43, 61] | 51 [43, 59] |  | disagree: the readers give the edit a vote gain like RL's, but the edit finishes more than RL, so it has fewer cap-hit abstentions and its finished guesses dilute the vote, as on the 328 (214 vs 221). |
| t07 | 45.5 | [39, 52] | 46 [39, 53] | 44 [37, 51] |  | agree: the mechanism gives the readers' number of about 45 for single samples, where the vote's filter does not act. |
| t12 | 230 | [214, 246] | 226 [207, 244] | 232 [215, 248] |  | agree: the readers' 226-232 is the raw-template 32k number, which the mechanism carries over. |
| t13 | 203 | [187, 219] | 200 [180, 218] | 205 [186, 222] |  | agree: the readers' 200-205 is the raw run minus a few longer answers, as here. |
| t14 | 463 | [454, 472] | 461 [450, 471] | 463 [452, 474] |  | agree: the readers' 461-463 comes from the same cap-hit conversion. |
| t16 | 456 | [450, 462] | 453 [446, 460] | 453 [445, 461] |  | disagree: the readers extrapolate a flattening curve from 446; they miss that the 36 ties at k=4 (tie-breaking alone gave up to 453) mostly go away at odd k. |
| t17 | 457 | [451, 463] | 454 [447, 461] | 455 [447, 463] |  | agree: the readers also put the k=12 vote 1-2 problems above k=9; the mechanism starts about 2 higher because of the tie effect. |
| t18 | 79 | [75, 83] | 79 [74, 85] | 79 [74, 84] |  | agree: the readers' 79 is vote over 3 plus a small fourth-sample gain. |
| t19 | 71.3 | [68.5, 74.2] | 71.3 [68.5, 74.3] | 71.3 [68.5, 74.2] |  | agree: the readers' 71.3 is the mean of the known samples. |
| t20 | 249 | [241, 257] | 250 [241, 258] | 247 [239, 256] |  | agree: the readers' 247-250 already scales the vote gain by how much less a=2 abstains. |
| t22 | 245 | [237, 253] | 248 [240, 256] | 247 [237, 257] |  | agree: the mechanism gives about the readers' 247, slightly lower because late wrong answers now vote. |
| t23 | 80 | [73, 87] | 81 [74, 88] | 80 [73, 87] |  | agree: the readers' 80-81 matches the net of new votes and dilution. |

## f2-m02

RL's top singular weight directions raise the model's per-token hazard of committing to an answer and ending, in proportion to their size. In-domain directions therefore turn unfinished answers into finished ones and lengthen premature short ones. Overall right-of-finished stays roughly flat, because fixes on problems already finished offset guesses on converted cap hits. Past about 1.5x the hazard closes hard problems with guesses. The full RL delta added to Think-SFT acts the same way.

Rests on: result-6f1bb7, result-51a0e7, result-95a4dc, result-1b6bf2, result-3387ce, result-39497c. Forecasts 13 of 23 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t01 | 366 | [338, 394] | 352 [324, 380] | 356 [326, 386] |  | disagree: the readers take a weaker transfer to code, but these are Code-RL's own directions on code, and the dial closed most of the gap on both math sets at 1x. |
| t02 | 378 | [350, 406] | 360 [328, 392] | 363 [330, 396] |  | disagree: the readers stop at about 55-70 % of the gap; the dial matched RL at 1.5x on two math sets, and nothing here says code finishing is different. |
| t03 | 360 | [326, 394] | 350 [305, 388] | 352 [308, 390] |  | agree: the readers also put 2x below 1.5x; the mechanism's level is higher only because its 1.5x is higher. |
| t04 | 315 | [301, 329] | 316 [300, 333] | 316 [299, 334] |  | agree: random edits are flat, as the readers say. |
| t05 | 343 | [317, 369] | 338 [312, 366] | 340 [312, 370] |  | agree: the readers' partial gain to about 340 matches a cross-domain finishing push. |
| t06 | 51 | [43, 59] | 52 [43, 61] | 51 [43, 59] |  | agree: the readers' 51-52 matches. |
| t07 | 46.5 | [40, 53] | 46 [39, 53] | 44 [37, 51] |  | agree: the readers' 44-46 matches the conversion arithmetic. |
| t18 | 79 | [75, 83] | 79 [74, 85] | 79 [74, 84] |  | agree: same arithmetic as the readers. |
| t19 | 71.3 | [68.5, 74.2] | 71.3 [68.5, 74.3] | 71.3 [68.5, 74.2] |  | agree: the readers' mean of the three. |
| t20 | 249 | [241, 257] | 250 [241, 258] | 247 [239, 256] |  | agree: the readers' 247-250 already accounts for fewer abstentions. |
| t21 | 466 | [458, 474] | 466 [457, 474] | 465 [455, 474] |  | agree: the readers put a=2 level with a=1. |
| t22 | 246 | [238, 254] | 248 [240, 256] | 247 [237, 257] |  | agree: the readers' 247 is the same partial gain. |
| t23 | 80.5 | [73, 88] | 81 [74, 88] | 80 [73, 87] |  | agree: the readers' 80-81. |

## f2-m03

Whether tokens past a cap add right answers depends on whether a model's long answers are still deriving or already guessing. Think-SFT, trained by imitation, keeps deriving until it stops, so its capped answers are unfinished work that finishes right about a quarter of the time. The base and RL close long answers with asserted numbers, so a longer cap gains them little. In its native <think> format Think-SFT thinks longer, which moves more right answers past 16,384.

Rests on: result-c8b994, result-0c1eef, result-02da9f, result-fc7efc, result-527fbb, result-b006f5. Forecasts 12 of 23 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t12 | 235 | [219, 251] | 226 [207, 244] | 232 [215, 248] |  | disagree: the readers copy the raw run's 230; they miss that the native format lengthens productive thinking, which pays off only when the cap is raised. |
| t13 | 200 | [184, 216] | 200 [180, 218] | 205 [186, 222] |  | agree: the readers also take a few off the raw run's 207 for longer native thinking. |
| t14 | 465 | [456, 474] | 461 [450, 471] | 463 [452, 474] |  | agree: the readers' 461-463, slightly higher here because the cut answers are productive. |
| t15 | 457 | [446, 467] | 456 [443, 467] | 458 [444, 469] |  | agree: the readers' 456-458. |
| t16 | 455 | [449, 461] | 453 [446, 460] | 453 [445, 461] |  | agree: close to the readers' 453, a little higher for odd k. |
| t17 | 456 | [450, 462] | 454 [447, 461] | 455 [447, 463] |  | agree: the readers' 454-455. |
| t18 | 79 | [75, 83] | 79 [74, 85] | 79 [74, 84] |  | agree: same as the readers. |
| t19 | 71.3 | [68.5, 74.2] | 71.3 [68.5, 74.3] | 71.3 [68.5, 74.2] |  | agree: same as the readers. |
| t20 | 249 | [241, 257] | 250 [241, 258] | 247 [239, 256] |  | agree: the readers' 247-250. |
| t21 | 466 | [458, 474] | 466 [457, 474] | 465 [455, 474] |  | agree: the readers' 465-466. |
| t22 | 248 | [240, 256] | 248 [240, 256] | 247 [237, 257] |  | agree: the readers' 247-248. |
| t23 | 82 | [75, 89] | 81 [74, 88] | 80 [73, 87] |  | disagree: the readers scale the gain from the 328; fresh2026 has a larger share of cut, still-deriving answers, so the 32k vote gains more there. |

## f2-m04

Graded accuracy depends on how a model ends its answer: whether the last thing written is the gradable marker (a boxed value, an Answer: line, the final python block). Under the raw template Think-SFT sometimes ends with the gold on a line v3 does not read. RL directions install one terminal marker. The native Think-SFT format ends with a post-think summary that restates the answer. Math directions push a boxed ending that competes with the final code block.

Rests on: result-818c20, result-284db5, result-6f1bb7, result-c57b51, knowledge-499152, result-59ed1a. Forecasts 13 of 23 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t14 | 467 | [459, 475] | 461 [450, 471] | 463 [452, 474] |  | disagree: the readers carry over the raw-template level; they miss that 16 of Think-SFT's 74 raw-template finished-wrong answers state the gold in a form v3 misses, and the native summary ending fixes most of these. |
| t15 | 461 | [451, 470] | 456 [443, 467] | 458 [444, 469] |  | disagree: about 3 above the readers' 456-458, from the same marker repair. |
| t12 | 233 | [217, 249] | 226 [207, 244] | 232 [215, 248] |  | agree: close to the readers' 226-232; the repair matters little on integer answers. |
| t13 | 205 | [189, 221] | 200 [180, 218] | 205 [186, 222] |  | agree: the readers' 200-205. |
| t21 | 468 | [460, 476] | 466 [457, 474] | 465 [455, 474] |  | agree: about the readers' 465-466, one or two higher from the format. |
| t01 | 362 | [335, 389] | 352 [324, 380] | 356 [326, 386] |  | agree: close to the readers' 352-356, a little higher for the ending repair. |
| t02 | 372 | [344, 400] | 360 [328, 392] | 363 [330, 396] |  | disagree: about 10 above the readers, because in-domain directions at 1.5x fix the ending on nearly every answer. |
| t03 | 356 | [322, 390] | 350 [305, 388] | 352 [308, 390] |  | agree: the readers' 350-352. |
| t04 | 315 | [301, 329] | 316 [300, 333] | 316 [299, 334] |  | agree: random edits are flat. |
| t05 | 335 | [310, 360] | 338 [312, 366] | 340 [312, 370] |  | disagree: slightly under the readers' 338-340, because a boxed ending competes with the code block the grader takes. |
| t06 | 51 | [43, 59] | 52 [43, 61] | 51 [43, 59] |  | agree: the readers' 51-52. |
| t07 | 46 | [39, 53] | 46 [39, 53] | 44 [37, 51] |  | agree: the readers' 44-46. |
| t20 | 249 | [241, 257] | 250 [241, 258] | 247 [239, 256] |  | agree: the readers' 247-250. |

## f2-m05

A trace can degenerate before it ends, into word strings, a switch to Chinese script or repeated windows, and a degenerate trace almost never ends right. The hazard of this grows with edit size (word strings at 2-3x) and with tokens already generated (median first script switch near token 13,600). So oversized edits, and the late part of very long Think-SFT traces, lose answers. A smaller edit or a shorter trace keeps them. At T 1.0 classic loops are absent.

Rests on: result-6f1bb7, result-4b0d5f, result-997be4, result-3387ce, result-44b4df, result-dadeec. Forecasts 14 of 23 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t01 | 362 | [335, 389] | 352 [324, 380] | 356 [326, 386] |  | agree: close to the readers' 352-356. |
| t02 | 372 | [344, 400] | 360 [328, 392] | 363 [330, 396] |  | disagree: about 10 above the readers, who widen the downside at 1.5x; degeneration starts only past that size, and short code answers give it little room. |
| t03 | 350 | [312, 388] | 350 [305, 388] | 352 [308, 390] |  | agree: the readers' 350-352 also has 2x falling back. |
| t04 | 315 | [301, 329] | 316 [300, 333] | 316 [299, 334] |  | agree: flat at the base cue level, as the readers say. |
| t05 | 340 | [314, 366] | 338 [312, 366] | 340 [312, 370] |  | agree: the readers' 338-340. |
| t07 | 45 | [38, 52] | 46 [39, 53] | 44 [37, 51] |  | agree: the readers' 44-46. |
| t12 | 228 | [212, 244] | 226 [207, 244] | 232 [215, 248] |  | agree: the readers' 226-232; drift caps the 32k gain at the raw run's level. |
| t13 | 203 | [187, 219] | 200 [180, 218] | 205 [186, 222] |  | agree: the readers' 200-205. |
| t18 | 78.5 | [74, 83] | 79 [74, 85] | 79 [74, 84] |  | agree: the readers' 79. |
| t19 | 71 | [68, 74] | 71.3 [68.5, 74.3] | 71.3 [68.5, 74.2] |  | agree: the readers' 71.3. |
| t20 | 247 | [239, 255] | 250 [241, 258] | 247 [239, 256] |  | agree: the readers' 247-250. |
| t21 | 464 | [455, 473] | 466 [457, 474] | 465 [455, 474] |  | agree: the readers' 465-466. |
| t22 | 243 | [235, 251] | 248 [240, 256] | 247 [237, 257] |  | disagree: a few under the readers' 247-248, because the late finishes are partly drifted traces that cast wrong votes. |
| t23 | 78 | [71, 85] | 81 [74, 88] | 80 [73, 87] |  | agree: close to the readers' 80-81, slightly lower for drift. |

## f2-m06

Early RL (step 100) installs the deliberative 'Okay' opening on most answers but not all. Answers that miss it fall into the base's terse register and stop before checking, and this premature stop costs accuracy. The cue removes these premature stops: a small gain at step 100, none at step 400, where the opening is near universal. So step-100 plain sits about one point above the cued base. A finishing policy arrives only in later steps.

Rests on: result-fad48d, result-32b7a8, result-3a3af3, result-c36598, knowledge-9e4147. Forecasts 13 of 23 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t08 | 417 | [410, 424] | 415 [408, 422] | 418 [409, 427] |  | agree: the readers' 415-418. |
| t09 | 424 | [417, 431] | 422.5 [415, 430] | 425 [416, 434] |  | agree: the readers' 422.5-425. |
| t10 | 434.5 | [428, 441] | 434 [427, 441] | 435 [426, 444] |  | agree: the readers' 434-435. |
| t11 | 1.3 | [-0.2, 2.8] | 0.9 [-0.7, 2.5] | 1.5 [-0.4, 3.4] |  | agree: the readers' 0.9-1.5. |
| t12 | 230 | [214, 246] | 226 [207, 244] | 232 [215, 248] |  | agree: the readers' 226-232. |
| t13 | 204 | [188, 220] | 200 [180, 218] | 205 [186, 222] |  | agree: the readers' 200-205. |
| t14 | 463 | [454, 472] | 461 [450, 471] | 463 [452, 474] |  | agree: the readers' 461-463. |
| t15 | 457 | [446, 467] | 456 [443, 467] | 458 [444, 469] |  | agree: the readers' 456-458. |
| t16 | 455 | [449, 461] | 453 [446, 460] | 453 [445, 461] |  | agree: near the readers' 453, slightly higher for odd k. |
| t17 | 456 | [450, 462] | 454 [447, 461] | 455 [447, 463] |  | agree: the readers' 454-455. |
| t04 | 315 | [301, 329] | 316 [300, 333] | 316 [299, 334] |  | agree: the readers' 316. |
| t06 | 51 | [43, 59] | 52 [43, 61] | 51 [43, 59] |  | agree: the readers' 51-52. |
| t07 | 45.5 | [39, 52] | 46 [39, 53] | 44 [37, 51] |  | agree: the readers' 44-46. |

## t01 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems does the Olmo 3 base model with Code-RL 3.1's 8 top weight directions added at 1x size pass, with the Code cue at T 1.0?

Unit: problems passed of 538. Cell: {"model": "Olmo-3-1025-7B base + top 8 directions of (RL-Code 3.1 - base) at 1x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": "not stated", "grader": "not stated"}

> base + Code 3.1's 8 directions at 1x, 1.5x, 2x

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 352 | [324, 380] | Base+Code cue 317, RL-Code 401; Math top-8 at 1x closed about two thirds of the hard328 gap (164->192 vs 206), so roughly 60% of the 84-problem code gap is assumed, with ~11-problem sampling noise. |
| reader-2 | 356 | [326, 386] | Base Code cue 317 vs RL-Code 401; on hard328 the Math top-8 edit at 1x closed about two thirds of the gap (192 of 164->206), assumed weaker on code, where cap hits matter less. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 366 | [338, 394] | In-domain Code directions at 1x install Code-RL's finishing; Math's directions at 1x closed 67 % of the hard328 gap. Taking about 58 % of the 84-problem code gap gives 366. |
| f2-m03 | - |  | no forecast |
| f2-m04 | 362 | [335, 389] | Code-RL directions install ending on one final python block; the base code cue's lost answers include missing or non-final code blocks; partial gain of the 84-problem gap. |
| f2-m05 | 362 | [335, 389] | At 1x there is no degeneration; the in-domain edit keeps most of its finishing gain. |
| f2-m06 | - |  | no forecast |

## t02 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems does the Olmo 3 base model with Code-RL 3.1's 8 top weight directions added at 1.5x size pass, with the Code cue at T 1.0?

Unit: problems passed of 538. Cell: {"model": "Olmo-3-1025-7B base + top 8 directions of (RL-Code 3.1 - base) at 1.5x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": "not stated", "grader": "not stated"}

> base + Code 3.1's 8 directions at 1x, 1.5x, 2x

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 360 | [328, 392] | On hard328 the 1.5x dial matched RL (203, then 200.25 over 4 samples); code gain from Code directions likely somewhat weaker than math, so ~70% of the 317->401 gap. |
| reader-2 | 363 | [330, 396] | At 1.5x the math dial matched RL (203 / 200.25 vs 206 / 200), so roughly 55% of the 84-problem code gap with wide uncertainty about transfer to code. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 378 | [350, 406] | At 1.5x the math dial reached RL on hard328 (200.25 vs 200) and MATH-500 (456 vs 457); some of the code gain is tests passed, not finishing, so about 73 % of the gap. |
| f2-m03 | - |  | no forecast |
| f2-m04 | 372 | [344, 400] | At 1.5x the terminal-block habit is fully installed (unboxed answers 22 -> 1 on hard328 with Math directions). |
| f2-m05 | 372 | [344, 400] | 1.5x is still below the size where word strings appear (they began past 1.5x on math), and code answers are short (about 4,100 tokens), so there is little exposure. |
| f2-m06 | - |  | no forecast |

## t03 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems does the Olmo 3 base model with Code-RL 3.1's 8 top weight directions added at 2x size pass, with the Code cue at T 1.0?

Unit: problems passed of 538. Cell: {"model": "Olmo-3-1025-7B base + top 8 directions of (RL-Code 3.1 - base) at 2x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": "not stated", "grader": "not stated"}

> base + Code 3.1's 8 directions at 1x, 1.5x, 2x

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 350 | [305, 388] | At 2x the math dial fell back (190 vs 203) as cap hits vanish and precision drops; same shape assumed on code with wider risk of degradation. |
| reader-2 | 352 | [308, 390] | At 2x the math dial fell back (190 vs 203 at 1.5x, word-salad starting), so slightly below 1.5x with a wider downside. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 360 | [326, 394] | At 2x the hazard closes hard problems with guesses (hard328: 203 -> 190), so it falls back about as far below 1.5x. |
| f2-m03 | - |  | no forecast |
| f2-m04 | 356 | [322, 390] | At 2x answers end early with a block before the code is right; it falls back from 1.5x. |
| f2-m05 | 350 | [312, 388] | At 2x some traces turn into word strings (hard328: 203 -> 190), and short code answers limit the damage: about 20 below 1.5x. |
| f2-m06 | - |  | no forecast |

## t04 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems does the Olmo 3 base model with a random rank-8 weight edit at 1.5x size (control) pass, with the Code cue at T 1.0?

Unit: problems passed of 538. Cell: {"model": "Olmo-3-1025-7B base + random rank-8 edit at 1.5x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": "not stated", "grader": "not stated"}

> random at 1.5x

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 316 | [300, 333] | Random rank-8 edits are flat at every size on hard328 (158-167 vs base 164), so expect the base+Code cue 317 within sampling noise. |
| reader-2 | 316 | [299, 334] | Random rank-8 edits are flat at the base level in every math cell, so the base Code cue 317 plus one-sample noise. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 315 | [301, 329] | A random rank-8 edit does not touch the stop hazard (cap hits flat at 67-79 at every size on hard328), so the base code cue's 317 within noise. |
| f2-m03 | - |  | no forecast |
| f2-m04 | 315 | [301, 329] | A random edit does not change how answers end; base code cue 317. |
| f2-m05 | 315 | [301, 329] | A random rank-8 edit at 1.5x is too small to degenerate the model (flat on hard328 at sizes up to 3). |
| f2-m06 | 315 | [301, 329] | A random edit leaves the code cue's opening unchanged; base code cue 317. |

## t05 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems does the Olmo 3 base model with Math-RL 3.1's 8 top weight directions added at 1.5x size pass, with the Code cue at T 1.0?

Unit: problems passed of 538. Cell: {"model": "Olmo-3-1025-7B base + top 8 directions of (RL-Math 3.1 - base) at 1.5x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": "not stated", "grader": "not stated"}

> Math 3.1's at 1.5x, on HumanEval+ and MBPP+

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 338 | [312, 366] | Math cue works on code (326 vs 317) and Math-RL transfers to code (LiveCodeBench 21.9 vs Code-RL 24.3), and Code top-8 on math gave about half of Math top-8's gain, so expect a partial gain. |
| reader-2 | 340 | [312, 370] | Math-RL transfers partly to code (Math cue 326 on base, Math-RL on LCB 21.9 vs Code-RL 24.3), so a partial gain over 317. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 343 | [317, 369] | Math directions also carry finishing (Math, Code and IF directions all cut cap hits), but they fit code less well; Code top-8 on math gave half of Math top-8's gain, so take the mirror image. |
| f2-m03 | - |  | no forecast |
| f2-m04 | 335 | [310, 360] | Math directions bring deliberation that helps code (Math cue 326), but also push a boxed final answer that can displace the final python block, which the grader reads. |
| f2-m05 | 340 | [314, 366] | Math directions at 1.5x do not degenerate the model; partial cross-domain gain. |
| f2-m06 | - |  | no forecast |

## t06 (work-16773f): How many of the 136 fresh2026 contest problems does the Olmo 3 base plus 1.5 times the top 8 RL-Math weight directions, with the cue, get right under a majority vote over 4 samples?

Unit: right answers of 136 (vote over 4). Cell: {"model": "Olmo-3-1025-7B base + 1.5 x top 8 directions of (RL-Math - base)", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "seeds of SPEC_fresh; temperature, top-p and token cap not stated", "samples": 4, "grader": "not stated"}

> is it level with RL (57 vote, 50.5 single)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 52 | [43, 61] | On hard328 the 1.5x edit's vote was 214 vs RL 221 and base 192; on fresh2026 RL vote 57, base cue vote 38, so slightly below RL. |
| reader-2 | 51 | [43, 59] | Edit matched RL single on hard328 but trailed RL's vote (214 vs 221), so a vote a few below RL's 57, with base cue at 38. |
| r5-m03-rival | 54 | [46, 61] | Theory: the top-8 edit puts most samples on a weak dose of RL's own policy, so its vote sits just under RL's vote of 57, as on hard328 (edit vote 214 vs RL 221, -2 pts), well above the cued base's 38. |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 49.5 | [43, 56] | Edit single about 45.5 with cap hits cut to about a third of the base's; on the 328 its vote gain was 65 % of RL's (13.75 vs 21), so 0.65 x RL's fresh gain of 6.5 adds about 4. |
| f2-m02 | 51 | [43, 59] | The edit finishes more than RL with similar precision; vote a little under RL's 57. |
| f2-m03 | - |  | no forecast |
| f2-m04 | 51 | [43, 59] | On fresh2026 the edit boxes every finished answer, as RL does; its vote sits a few under RL's 57. |
| f2-m05 | - |  | no forecast |
| f2-m06 | 51 | [43, 59] | The 8 directions write the 'Okay' opening (430 of 500 on MATH-500) and some finishing; vote a few under RL's 57. |

## t07 (work-16773f): Averaged over 4 single samples, how many of the 136 fresh2026 contest problems does the Olmo 3 base plus 1.5 times the top 8 RL-Math weight directions, with the cue, get right?

Unit: mean right answers of 136 per single sample (mean over 4 samples). Cell: {"model": "Olmo-3-1025-7B base + 1.5 x top 8 directions of (RL-Math - base)", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "seeds of SPEC_fresh; temperature, top-p and token cap not stated", "samples": 4, "grader": "not stated"}

> is it level with RL (57 vote, 50.5 single)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 46 | [39, 53] | On hard328 the 1.5x edit's single-sample mean equalled RL (200.25 vs 200.0); fresh2026 RL single 50.5, base cue 29.5, edit expected a bit below RL on this harder set. |
| reader-2 | 44 | [37, 51] | Edit cuts cap hits toward RL's level with precision between the base (36%) and RL (44%) on fresh2026, so about 44 against RL 50.5 and base 29.5. |
| r5-m03-rival | 49 | [43, 55] | Theory: with the cue, nearly every sample takes RL's way of answering at a weak dose, so a single sample comes in level with or slightly under RL's 50.5, as the 1.5x edit matched RL on hard328 (200.25 vs 200) and on MATH-500 (456 vs 457). |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 45.5 | [39, 52] | Single samples: the edit converts most of the base's 40 % cap hits into finished answers at a lower precision, ending a few problems under RL's 50.5. |
| f2-m02 | 46.5 | [40, 53] | Fresh cap hits of 40 % fall to about 10 %; converted answers are right less often, and precision on problems already finished rises toward RL's. |
| f2-m03 | - |  | no forecast |
| f2-m04 | 46 | [39, 53] | Single samples a few under RL's 50.5; the format is RL-like, and the gap comes from precision. |
| f2-m05 | 45 | [38, 52] | Fresh answers are long, so the 1.5x edit's small degeneration risk shows up more than on MATH-500; a few under RL's 50.5. |
| f2-m06 | 45.5 | [39, 52] | Opening plus partial finishing; a few under RL's 50.5. |

## t08 (work-f8ecb6): Averaged over 4 samples (the stored one plus 3 new), how many of the 500 MATH-500 problems does the step-100 RL-Zero-Math checkpoint get right with the plain prompt at T 1.0, grader v3?

Unit: mean right answers of 500 over 4 samples. Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math step 100 checkpoint", "prompt": "plain", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": 4, "grader": "v3"}

> 3 more samples of step-100 plain, step-100 cue, step-400 plain (MATH-500, T 1.0, v3)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 415 | [408, 422] | Stored step-100 plain sample 418 plus three new samples regressing slightly toward a ~414 true rate (per-sample spread about +-6 as in base cue 405-418). |
| reader-2 | 418 | [409, 427] | Stored step-100 plain sample is 418; the 4-sample mean stays near it, with about 5 problems of sd from the new samples and hardware. |
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
| f2-m06 | 417 | [410, 424] | 383 of 500 step-100 plain answers open with Okay at T 1.0; the other 117 stop early in the terse register. True rate about 417, near the stored 418. |

## t09 (work-f8ecb6): Averaged over 4 samples (the stored one plus 3 new), how many of the 500 MATH-500 problems does the step-100 RL-Zero-Math checkpoint get right with the opening cue at T 1.0, grader v3?

Unit: mean right answers of 500 over 4 samples. Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math step 100 checkpoint", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": 4, "grader": "v3"}

> 3 more samples of step-100 plain, step-100 cue, step-400 plain (MATH-500, T 1.0, v3)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 422.5 | [415, 430] | Stored step-100 cue 427 likely a high draw (cue effect +1.8 [-1.2, 4.8]); three new samples around 421. |
| reader-2 | 425 | [416, 434] | Stored step-100 cue sample is 427, pulled slightly toward step-100 plain (418) because the cue effect is +1.8 [-1.2, 4.8]. |
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
| f2-m06 | 424 | [417, 431] | The cue removes the premature stops of the 117 non-opened answers: plain plus about 7, and the stored 427 regresses slightly. |

## t10 (work-f8ecb6): Averaged over 4 samples (the stored one plus 3 new), how many of the 500 MATH-500 problems does the step-400 RL-Zero-Math checkpoint get right with the plain prompt at T 1.0, grader v3?

Unit: mean right answers of 500 over 4 samples. Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math step 400 checkpoint", "prompt": "plain", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": 4, "grader": "v3"}

> 3 more samples of step-100 plain, step-100 cue, step-400 plain (MATH-500, T 1.0, v3)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 434 | [427, 441] | Stored step-400 plain 436 averaged with three new samples around 433. |
| reader-2 | 435 | [426, 444] | Stored step-400 plain sample is 436; the mean of 4 stays near it. |
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
| f2-m06 | 434.5 | [428, 441] | At step 400 the opening is near universal and finishing has started; the stored 436 regresses slightly. |

## t11 (work-f8ecb6): Over 4 samples each on MATH-500 at T 1.0 (grader v3), by how many points does the step-100 RL-Zero-Math checkpoint with the plain prompt beat (or trail) the untrained base with the opening cue?

Unit: points, step-100 plain minus cued base, mean over 4 samples each. Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math step 100 (plain) vs Olmo-3-1025-7B base (cue)", "prompt": "plain for step 100; cue for the base", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; token cap not stated", "samples": 4, "grader": "v3"}

> so the step-100 vs cued-base difference has a 4-sample interval

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 0.9 | [-0.7, 2.5] | Step-100 plain 4-sample mean ~415 minus cued base 4-sample mean 410.5 of 500, in points. |
| reader-2 | 1.5 | [-0.4, 3.4] | Step-100 4-sample mean of about 418 minus the cued base's 4-sample mean of 410.5, in percentage points of 500. |
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
| f2-m06 | 1.3 | [-0.2, 2.8] | (417 - 410.5) / 5: step 100 equals the cued base on opened answers and is a little stronger per step, minus its premature stops. |

## t12 (work-8b2ec9): How many of the 328 harder problems does Think-SFT get right in its own ChatML-with-<think> chat format, one sample at T 1.0 with a 32,768-token cap, grader v3?

Unit: right answers of 328. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "Think-SFT's own ChatML chat template with <think>", "set": "hard328", "n": 328, "sampling": "T 1.0; top-p not stated; token cap 32,768", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 226 | [207, 244] | Paired raw-template cue run at cap 32,768 scored 230; native ChatML with <think> is an untested format, so similar with extra uncertainty. |
| reader-2 | 232 | [215, 248] | Raw-template Think-SFT + cue at cap 32,768 scored 230; its own chat format should be about the same or slightly better. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 230 | [214, 246] | Single sample: the native format, like the raw template, leaves Think-SFT abstaining by cap hit; at 32,768 most of these finish, as in the paired raw run (230). |
| f2-m02 | - |  | no forecast |
| f2-m03 | 235 | [219, 251] | In-distribution <think> traces run longer and keep deriving, so more of the cut answers finish right at 32k than the raw run's 23 of 93. |
| f2-m04 | 233 | [217, 249] | On hard328 marker misses are rarer (integer AIME-style golds); raw 230 plus about 2. |
| f2-m05 | 228 | [212, 244] | Past 16k many Think-SFT traces have switched script, and those finish right 1 of 24 times; the 32k gain is limited to traces that did not switch. |
| f2-m06 | 230 | [214, 246] | The native <think> template forces a deliberative opening as the cue does, so no premature stops: the raw-template 32k level. |

## t13 (work-8b2ec9): How many of the 328 harder problems does Think-SFT get right in its own ChatML-with-<think> chat format, one sample at T 1.0, when its answers are counted at a 16,384-token cap, grader v3?

Unit: right answers of 328. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "Think-SFT's own ChatML chat template with <think>", "set": "hard328", "n": 328, "sampling": "T 1.0; top-p not stated; generated at cap 32,768, scored at 16,384", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 200 | [180, 218] | Raw-template cue run counted at 16,384 was 207 (stored singles 201-219); native thinking may run longer and lose a few more to the cap. |
| reader-2 | 205 | [186, 222] | Raw template counted at 16,384 scored 207; native thinking may run longer, so slightly more cap hits. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 203 | [187, 219] | The same answers counted at 16,384: about 29 % abstain, as in the raw run (207). |
| f2-m02 | - |  | no forecast |
| f2-m03 | 200 | [184, 216] | Longer native thinking pushes more answers past 16,384, so counting at 16k loses a few more than the raw template's 207. |
| f2-m04 | 205 | [189, 221] | Raw 207 at 16k, minus longer native thinking, plus a small marker repair. |
| f2-m05 | 203 | [187, 219] | At 16k most traces have not yet drifted; raw-run level of 207 minus a few longer native traces. |
| f2-m06 | 204 | [188, 220] | Same answers at 16k, near the raw template's 207. |

## t14 (work-8b2ec9): How many of the 500 MATH-500 problems does Think-SFT get right in its own ChatML-with-<think> chat format, one sample at T 1.0 with a 32,768-token cap, grader v3?

Unit: right answers of 500. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "Think-SFT's own ChatML chat template with <think>", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; token cap 32,768", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 461 | [450, 471] | Think-SFT cue singles on MATH-500 are 454-462 at 16k; cap 32k adds a little, native template similar. |
| reader-2 | 463 | [452, 474] | Think-SFT + cue singles are 454-462 at 16k on MATH-500; 32k adds a few, and the native format looks clean in the smoke test (7 of 8). |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 463 | [454, 472] | Raw-template singles 454-462 at 16k, plus about a quarter of the 24 MATH-500 cap hits finishing right at 32k. |
| f2-m02 | - |  | no forecast |
| f2-m03 | 465 | [456, 474] | Singles 454-462 at 16k plus the MATH-500 cap hits, which are unfinished work that mostly finishes by 32k. |
| f2-m04 | 467 | [459, 475] | Raw singles about 458.5, plus about 5 from cap hits finishing at 32k, plus about 3 of the roughly 4 per sample that v3 missed (gold on the line after Answer:), recovered by the summary ending. |
| f2-m05 | - |  | no forecast |
| f2-m06 | 463 | [454, 472] | Opening equivalent to the cue; singles 454-462 plus cap-hit finishing at 32k. |

## t15 (work-8b2ec9): How many of the 500 MATH-500 problems does Think-SFT get right in its own ChatML-with-<think> chat format, one sample at T 1.0, when its answers are counted at a 16,384-token cap, grader v3?

Unit: right answers of 500. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "Think-SFT's own ChatML chat template with <think>", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; generated at cap 32,768, scored at 16,384", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 456 | [443, 467] | Same answers at 16,384 cap: in line with stored cue singles 454-462, minus a few longer native answers. |
| reader-2 | 458 | [444, 469] | Same answers counted at 16,384, about where the raw-template singles sit (454-462). |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | 457 | [446, 467] | Counted at 16k: native traces are longer, so a few right answers sit past the cut. |
| f2-m04 | 461 | [451, 470] | Same answers at 16k: lose the cap-hit gain, keep the marker repair. |
| f2-m05 | - |  | no forecast |
| f2-m06 | 457 | [446, 467] | Same answers at 16k. |

## t16 (work-60f040): How many of the 500 MATH-500 problems does the untrained Olmo 3 base with the opening cue get right under a majority vote over 9 samples at T 1.0, grader v3?

Unit: right answers of 500 (vote over 9). Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0, same cell as the stored 4 samples; top-p and token cap not stated", "samples": 9, "grader": "v3"}

> vote over 9 = 456 [449, 462] of 500

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 453 | [446, 460] | Vote over 4 is 446 (450 after restart, pass@4 467); Wang's majority@4->@8 gains ~2.5 points, and an odd k avoids ties. |
| reader-2 | 453 | [445, 461] | Vote over 4 is 446 and pass@4 is 467; Wang's majority curve gives diminishing gains, so about +7 at k=9. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 455 | [448, 461] | The rival's last sentence says a base-only vote over more samples recovers part of the open sharpening share, predicted 456/500; I shade it toward the board's vote over 4 = 446 and pass@4 = 467, which put the vote over 9 at about 455. |
| r6-m06 | 452 | [444, 460] | The statement says the cued base's wrong steps come from the head of its own distribution, so its wrong answers are high-probability and come back across samples; voting over more samples then adds only a few points over the stored vote over 4 (446) and stays below RL's 463. |
| r7-m05 | 452 | [446, 458] | In scope (cued base, MATH-500, T 1.0, v3): the theory puts misread/slip errors near the mode of the base's distribution, so resampling repeats them and the vote levels off just above the stored vote over 4 (446) as odd k breaks ties, well under pass@4 467. |
| r7-m08 | 455 | [448, 462] | The theory's no_intervention part says selecting among base samples (vote over 4 = 446) cannot reproduce the veto of high-probability wrong steps, so voting over more samples recovers only the base's reliability problems, where the base is right in most samples (pass@4 467), and levels off near or just below RL's single sample (456-463): 9 votes give about 455. |
| r7-m11 | 450 | [444, 456] | The statement says wrong answers drawn under the one cue agree with each other, so extra same-opening samples grow the agreeing wrong groups along with the right ones; the vote then levels off a few problems above the stored 4-sample vote of 446 (pass@4 467) and below the independent-slip forecast of 456. |
| f2-m01 | 456 | [450, 462] | Vote over 4 is 446 with 36 tied problems; an odd k of 9 removes most tie losses, and with only about 5 % cap hits per sample nearly every problem gets 8-9 finished votes. |
| f2-m02 | - |  | no forecast |
| f2-m03 | 455 | [449, 461] | The base's errors are finished guesses or unproductive cap hits; more samples add votes but no new derivations: plateau near pass@4 (467) minus selection losses. |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | 455 | [449, 461] | Every cued sample opens deliberatively, so its errors are slips spread across samples that a larger vote removes: about +9 over the vote over 4. |

## t17 (work-60f040): How many of the 500 MATH-500 problems does the untrained Olmo 3 base with the opening cue get right under a majority vote over 12 samples at T 1.0, grader v3?

Unit: right answers of 500 (vote over 12). Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0, same cell as the stored 4 samples; top-p and token cap not stated", "samples": 12, "grader": "v3"}

> Vote over k = 1..12 samples of the untrained cued base on MATH-500

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 454 | [447, 461] | Vote curve flattens past 9 samples; about one more problem than vote over 9. |
| reader-2 | 455 | [447, 463] | A couple more problems than the vote over 9 as the vote curve flattens, bounded by a pass@k that rises slowly. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 457 | [450, 464] | Same sharpening clause: on one difficulty axis, voting over more base samples keeps recovering sharpening problems with diminishing returns past the predicted 456 at 9 samples, so 12 samples add about 1-2 more (Wang's majority@8 to @16 curve rises 91 to 93 %). |
| r6-m06 | 453 | [445, 461] | Same head-error mechanism as t16: the wrong modes recur, so the vote levels off and 12 samples add at most about 1 point over 9, staying below RL's 463. |
| r7-m05 | 453 | [446, 460] | Same mode claim: errors that recur across samples stop the vote from gaining much past k=9, so vote over 12 stays about level with vote over 9 (~452), a few points above vote over 4 (446). |
| r7-m08 | 457 | [449, 464] | Same no_intervention part: votes over base samples add only base-reachable points and level off, so 12 votes add about 2 over the vote over 9 and stay under RL's single-sample range (456-463) and pass@4 (467). |
| r7-m11 | 451 | [444, 457] | Same mechanism: the extra samples keep the same cue opening, so they do not break up the wrong groups that agree; going from 9 to 12 votes adds at most about one problem over the levelled-off value near 450, below what independent slips would give. |
| f2-m01 | 457 | [451, 463] | Even k brings back a few ties, so k=12 adds only about one problem over k=9. |
| f2-m02 | - |  | no forecast |
| f2-m03 | 456 | [450, 462] | One more problem than at k=9 as the plateau sets in. |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | 456 | [450, 462] | One more problem than at k=9. |

## t18 (work-8b4030): How many of the 136 fresh2026 contest problems does Think-SFT plus twice the RL-Math weight change get right under a majority vote over 4 samples?

Unit: right answers of 136 (vote over 4). Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "fresh2026", "n": 136, "sampling": "seeds of SPEC_fresh; temperature, top-p and token cap not stated", "samples": 4, "grader": "not stated"}

> on fresh2026 (136 problems, 4 samples, seeds of SPEC_fresh)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 79 | [74, 85] | Vote over 3 of the a=2 transplant is 78 (singles 69, 70, 75); a fourth sample changes the vote by a few problems. |
| reader-2 | 79 | [74, 84] | Vote over 3 of the a=2 transplant is already 78; the fourth sample adds about 1, as it did for Think-SFT (74 to 75). |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 79 | [75, 83] | a=2 still hits the cap on about a third of fresh samples, so the fourth vote mostly fills abstentions: vote over 3 (78) plus about 1. |
| f2-m02 | 79 | [75, 83] | a=2 has already cut Think-SFT's fresh cap hits (63 -> 47 %); the fourth sample adds about 1 to the vote over 3 of 78. |
| f2-m03 | 79 | [75, 83] | Vote over 3 is 78; the fourth sample adds about 1. |
| f2-m04 | - |  | no forecast |
| f2-m05 | 78.5 | [74, 83] | At a=2 the delta transplant is below the degenerating sizes (decline only at a=3-4); fourth sample adds little to the vote of 78. |
| f2-m06 | - |  | no forecast |

## t19 (work-8b4030): Averaged over all 4 single samples, how many of the 136 fresh2026 contest problems does Think-SFT plus twice the RL-Math weight change get right?

Unit: mean right answers of 136 per single sample (mean over 4 samples). Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "fresh2026", "n": 136, "sampling": "seeds of SPEC_fresh; temperature, top-p and token cap not stated", "samples": 4, "grader": "not stated"}

> on fresh2026 (136 problems, 4 samples, seeds of SPEC_fresh)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 71.3 | [68.5, 74.3] | Three known samples average 71.3; the fourth (rerun of sample 1) has SD ~4, so the mean of 4 moves by about 1. |
| reader-2 | 71.3 | [68.5, 74.2] | Three samples are known (69, 70, 75); the fourth is drawn near their mean of 71.3. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 71.3 | [68.5, 74.2] | Three samples are known (69, 70, 75); the rerun of sample 1 comes from the same distribution. |
| f2-m02 | 71.3 | [68.5, 74.2] | Known samples 69, 70, 75; the rerun is drawn near them. |
| f2-m03 | 71.3 | [68.5, 74.2] | Mean of the known 69, 70, 75. |
| f2-m04 | - |  | no forecast |
| f2-m05 | 71 | [68, 74] | Known samples 69, 70, 75; the rerun is drawn near them. |
| f2-m06 | - |  | no forecast |

## t20 (work-8b4030): How many of the 328 harder problems does Think-SFT plus twice the RL-Math weight change get right under a majority vote over 4 samples?

Unit: right answers of 328 (vote over 4). Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "4 seeds (two stored, plus 3,200,000 and 3,300,000); temperature, top-p and token cap not stated", "samples": 4, "grader": "not stated"}

> hard328 samples 3-4 for the vote over 4

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 250 | [241, 258] | Two stored singles 234 and 229; the vote adds ~21 (RL) to ~32 (Think-SFT) over the single mean, less than Think-SFT's because a=2 abstains less. |
| reader-2 | 247 | [239, 256] | Singles 234 and 229; the vote gain should be about half of Think-SFT's +32, since the transplant hits the cap less (as on fresh2026: +6.7 vs +13.7). |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 249 | [241, 257] | a=2 cap hits 54 against Think-SFT's 94: its vote gain over a 231 single lies between RL's +21 and Think-SFT's +32, held under pass@4. |
| f2-m02 | 249 | [241, 257] | a=2 raises Think-SFT's stop hazard (cap 94.5 -> 54) at precision about 85 %; the vote adds about 18 over a single of about 231. |
| f2-m03 | 249 | [241, 257] | The RL delta makes Think-SFT close some unfinished work early with guesses (right-of-finished 88 -> 85 %), so its vote gain is below Think-SFT's +32. |
| f2-m04 | 249 | [241, 257] | a=2 ends in a box; marker misses barely matter on integer golds; vote about 18 over a single of about 231. |
| f2-m05 | 247 | [239, 255] | a=2 is not degenerate; vote over 4 about 16 over a single of about 231. |
| f2-m06 | - |  | no forecast |

## t21 (work-8b4030): How many of the 500 MATH-500 problems does Think-SFT plus twice the RL-Math weight change get right in one sample?

Unit: right answers of 500. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "MATH-500", "n": 500, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> MATH-500 1 sample

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 466 | [457, 474] | Think-SFT + 1x RL delta scored 467 on MATH-500 and Think-SFT cue 454-462; a=2 assumed about level. |
| reader-2 | 465 | [455, 474] | a=1 scored 467 on MATH-500 and Think-SFT cue singles are 454-462, so a=2 lands about the same. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 466 | [458, 474] | On MATH-500 a=1 scored 467; at a=2 the extra hazard matters little because MATH-500 answers rarely reach the cap. |
| f2-m03 | 466 | [458, 474] | MATH-500 answers are short; a=2 is level with a=1's 467. |
| f2-m04 | 468 | [460, 476] | The RL delta installs a single boxed ending, removing Think-SFT's v3 misses; a=1 was 467, and a=2 keeps the boxed ending. |
| f2-m05 | 464 | [455, 473] | MATH-500 answers are short, so no drift; level with a=1's 467 minus noise. |
| f2-m06 | - |  | no forecast |

## t22 (work-dc9359): How many of the 328 harder problems does Think-SFT with the cue get right under a majority vote over 4 samples generated with a 32,768-token cap?

Unit: right answers of 328 (vote over 4). Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "temperature and top-p not stated; token cap 32,768", "samples": 4, "grader": "not stated"}

> Think-SFT + cue vote over 4 at token cap 32,768 on hard328

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 248 | [240, 256] | Vote over 4 at 16k is 241 (pass@4 244); cap 32k adds ~23 per single, but the vote was already near pass@4; the offline simulation gave 240-254. |
| reader-2 | 247 | [237, 257] | Vote at 16k is 241 and singles gain +23 at 32k; the offline simulation says 240 unless late wrong answers disagree (254), so in between. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 245 | [237, 253] | Doubling the cap removes the filter: late answers are right 23 of 93 times, so they add more wrong votes than right ones; the gain comes only from problems with no right 16k sample. |
| f2-m02 | 246 | [238, 254] | Think-SFT has no RL directions, so its stop hazard stays low and its capped answers are unfinished work that a longer cap lets finish; under the vote the gain is partly redundant. |
| f2-m03 | 248 | [240, 256] | Each sample gains about 7 points at 32k from unfinished work; under the vote, part of that gain falls on problems another sample already had. |
| f2-m04 | - |  | no forecast |
| f2-m05 | 243 | [235, 251] | The extra 16k tokens fall where script switching sits; the drifted late finishes are wrong and dilute the vote. |
| f2-m06 | - |  | no forecast |

## t23 (work-dc9359): How many fresh2026 contest problems does Think-SFT with the cue get right under a majority vote over 4 samples generated with a 32,768-token cap?

Unit: right answers of fresh2026 problems (vote over 4). Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "cue", "set": "fresh2026", "n": "not stated", "sampling": "temperature and top-p not stated; token cap 32,768", "samples": 4, "grader": "not stated"}

> fresh2026 (4 samples), each answer scored at 16,384 and 32,768

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 81 | [74, 88] | Vote over 4 at 16k is 75 of 136 with 46% cap hits; the longer cap lets some of these finish, about +6. |
| reader-2 | 80 | [73, 87] | Vote at 16k is 75 of 136 with 46% cap hits; longer caps finish some of them, as on hard328 (+7 points single), so a few more. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 80 | [73, 87] | On fresh2026, 46 % cap hits leave many problems with no finished vote at 16k; at 32k they get votes, offset by late wrong answers. |
| f2-m02 | 80.5 | [73, 88] | Same on fresh2026, where 46 % of samples were cut. |
| f2-m03 | 82 | [75, 89] | On fresh2026, 46 % of Think-SFT samples are cut, against 29 % on the 328, so there is more unfinished work to complete and many problems had no finished vote at 16k. |
| f2-m04 | - |  | no forecast |
| f2-m05 | 78 | [71, 85] | On fresh2026, 104 of 544 Think-SFT samples switch script; late finishes are low-yield, small vote gain over 75. |
| f2-m06 | - |  | no forecast |
