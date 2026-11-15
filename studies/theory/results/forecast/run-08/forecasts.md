# Forecasts, run-08

Board snapshot 2026-11-15T16:32:52 UTC, written 2026-11-15T16:42:48 UTC. 23 targets; forecasters reader-1, reader-2, r5-m03-rival, r6-account-rival, r6-m06, r7-m05, r7-m08, r7-m11, f2-m01, f2-m02, f2-m03, f2-m04, f2-m05, f2-m06.


Lens of the mechanisms: the grader and the measurement itself: extraction, equivalence, seeds, set composition, what a count hides


## f2-m01

Each one-sample count is one seed's draw: the model branches at forks with fixed per-problem probabilities, so a cell has a sampling SD of about 5-6 problems on MATH-500, 7-9 on hard328 and 3 on fresh2026, plus small runner drift. A stored sample 0 is an unselected draw, so a 4-sample mean is that value shrunk slightly toward the cell's structural prior (neighbouring checkpoints, cue effect).

Rests on: result-5c961a, result-c8b994, result-460e0a, result-882fa7, result-fad48d. Forecasts 13 of 23 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t04 | 316 | [301, 331] | 316 [299, 333] | 315 [297, 333] |  | agree: the readers also put the control at the base cue plus seed noise. |
| t07 | 48 | [43, 53] | 47.5 [42, 53] | 48 [41, 55] |  | agree: same anchor on RL's 50.5 shaded slightly down. |
| t08 | 416.5 | [411, 422] | 416 [409, 423] | 416 [408, 424] |  | agree: shrinking 418 slightly is what the readers do; my interval is a little narrower because 3 of 4 draws average the noise. |
| t09 | 424 | [418, 430] | 423 [415, 430] | 423 [414, 431] |  | agree: within one problem of the readers' 423. |
| t10 | 434.5 | [429, 440] | 434 [427, 441] | 434 [426, 442] |  | agree: the readers shrink 436 the same way. |
| t11 | 1.2 | [-0.2, 2.6] | 1.1 [-0.5, 2.8] | 1.1 [-0.7, 2.9] |  | agree: the readers compute the same difference. |
| t12 | 231 | [218, 244] | 231 [214, 247] | 232 [214, 248] |  | agree: same anchor. |
| t13 | 207 | [195, 219] | 206 [188, 223] | 205 [186, 222] |  | agree: same anchor. |
| t14 | 465 | [456, 474] | 464 [452, 475] | 465 [452, 476] |  | agree: matches the readers' 464-465. |
| t15 | 460 | [451, 469] | 460 [447, 472] | 459 [445, 470] |  | agree: matches the readers. |
| t18 | 71 | [65, 77] | 71 [62, 80] | 71 [62, 80] |  | agree: same value; tighter interval because the three seeds already spread by only 6. |
| t20 | 248 | [240, 256] | 248 [238, 258] | 247 [237, 257] |  | agree: same as the readers. |
| t21 | 466 | [458, 474] | 466 [456, 475] | 465 [455, 474] |  | agree: same anchor. |

## f2-m02

A count 'at 16,384' rescored from a 32k run is a different measurement from a native 16k run: rows longer than 16,384 count wrong, while a native run lets grader v3 credit a box already written inside a truncated row (RL 69 % of capped rows, base 17 %, Think-SFT rarely). So 32k-minus-16k is extension finishes only, and models that box mid-reasoning lose a few problems when rescored.

Rests on: result-c8b994, result-0c1eef, knowledge-16c62a, result-a497ff. Forecasts 12 of 23 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t12 | 231 | [219, 243] | 231 [214, 247] | 232 [214, 248] |  | agree: the readers anchor on 230 as well. |
| t13 | 208 | [197, 219] | 206 [188, 223] | 205 [186, 222] |  | agree: the readers give 205-206, inside my range. |
| t14 | 467 | [459, 475] | 464 [452, 475] | 465 [452, 476] |  | agree: close to the readers' 464-465; I add a few more for extension finishes. |
| t15 | 460 | [452, 468] | 460 [447, 472] | 459 [445, 470] |  | agree: matches the readers. |
| t22 | 245 | [236, 254] | 246 [236, 256] | 246 [236, 256] |  | agree: the readers' 246. |
| t23 | 79 | [72, 86] | 79 [71, 87] | 80 [72, 88] |  | agree: the readers' 79-80. |
| t18 | 71 | [64, 78] | 71 [62, 80] | 71 [62, 80] |  | agree: same anchor. |
| t19 | 79 | [73, 85] | 78 [72, 85] | 79 [72, 86] |  | agree: same as readers. |
| t20 | 248 | [239, 257] | 248 [238, 258] | 247 [237, 257] |  | agree: the readers' 247-248. |
| t21 | 466 | [457, 475] | 466 [456, 475] | 465 [455, 474] |  | agree: same anchor. |
| t06 | 53 | [46, 60] | 52 [44, 60] | 53 [44, 62] |  | agree: the readers' 52-53. |
| t07 | 48 | [43, 53] | 47.5 [42, 53] | 48 [41, 55] |  | agree: the readers' 47.5-48. |

## f2-m03

The RL-direction edits add to a count mostly by converting cap hits into finished answers; the count hides the split: gain = cap hits removed x right rate on converted rows + a smaller rise in finished precision. hard328 gives the dial 77 cap hits to convert; short HumanEval+/MBPP+ answers rarely reach the cap, so the same edits move few problems there, and past 1.5x only the precision loss remains.

Rests on: result-6f1bb7, result-51a0e7, result-2fe32f, result-284db5. Forecasts 13 of 23 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t01 | 338 | [320, 356] | 350 [325, 376] | 350 [325, 375] |  | disagree: the readers carry the two-thirds gap closure from hard328, where it was mostly cap-hit conversion; code has little of that to convert. |
| t02 | 342 | [322, 362] | 360 [331, 388] | 358 [330, 386] |  | disagree: the readers expect about half of the 84-problem gap; the cap-hit part of the dial is missing on short code answers. |
| t03 | 330 | [308, 352] | 350 [312, 385] | 345 [305, 380] |  | disagree: same direction as the readers (below 1.5x), but from a lower peak. |
| t04 | 316 | [302, 330] | 316 [299, 333] | 315 [297, 333] |  | agree: the readers put it at the base level too. |
| t05 | 326 | [308, 344] | 343 [315, 370] | 338 [314, 362] |  | disagree: the readers credit LiveCodeBench-style transfer; on this set the edit's main lever (finishing) has little to act on. |
| t06 | 52 | [45, 59] | 52 [44, 60] | 53 [44, 62] |  | agree: the readers' 52-53. |
| t07 | 47 | [42, 52] | 47.5 [42, 53] | 48 [41, 55] |  | agree: slightly below the readers' 47.5-48, well inside their range. |
| t12 | 231 | [219, 243] | 231 [214, 247] | 232 [214, 248] |  | agree: same anchor. |
| t14 | 467 | [459, 475] | 464 [452, 475] | 465 [452, 476] |  | agree: a few above the readers, inside their range. |
| t20 | 249 | [240, 258] | 248 [238, 258] | 247 [237, 257] |  | agree: the readers' 247-248. |
| t21 | 465 | [456, 474] | 466 [456, 475] | 465 [455, 474] |  | agree: matches the readers. |
| t22 | 244 | [235, 253] | 246 [236, 256] | 246 [236, 256] |  | agree: near the readers' 246. |
| t23 | 79 | [72, 86] | 79 [71, 87] | 80 [72, 88] |  | agree: the readers' 79-80. |

## f2-m04

Grader v3 and the code harness score only what they extract where they look: a final 'Answer:' line or box for math, a code block for code. A template or weight edit that moves where the final answer is written changes the count without changing solving: Think-SFT on the raw template sometimes puts it on the line after 'Answer:' (about 4 lost per 500); Math-RL directions carry a boxed ending a code extractor misses.

Rests on: result-818c20, result-1a80e9, knowledge-781efc, result-fdc8da. Forecasts 13 of 23 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t14 | 468 | [459, 477] | 464 [452, 475] | 465 [452, 476] |  | agree: a few above the readers' 464-465, inside their intervals; they leave out the extraction recovery. |
| t15 | 462 | [453, 471] | 460 [447, 472] | 459 [445, 470] |  | agree: a little above the readers' 459-460. |
| t12 | 232 | [220, 244] | 231 [214, 247] | 232 [214, 248] |  | agree: the readers' 231-232. |
| t13 | 207 | [195, 219] | 206 [188, 223] | 205 [186, 222] |  | agree: the readers' 205-206. |
| t21 | 467 | [458, 476] | 466 [456, 475] | 465 [455, 474] |  | agree: the readers' 465-466. |
| t05 | 330 | [312, 348] | 343 [315, 370] | 338 [314, 362] |  | disagree: the readers count Math-RL's code transfer but miss that its answer format, like RL's boxes under the spec grader of result-1a80e9, is partly unreadable to this extractor. |
| t01 | 350 | [326, 374] | 350 [325, 376] | 350 [325, 375] |  | agree: the extraction mechanism gives the readers' number. |
| t02 | 358 | [332, 384] | 360 [331, 388] | 358 [330, 386] |  | agree: no extraction change from Code directions. |
| t03 | 346 | [310, 380] | 350 [312, 385] | 345 [305, 380] |  | agree: the readers' 345-350. |
| t04 | 316 | [300, 332] | 316 [299, 333] | 315 [297, 333] |  | agree: base level. |
| t08 | 416 | [410, 422] | 416 [409, 423] | 416 [408, 424] |  | agree: no extraction shift. |
| t09 | 424 | [418, 430] | 423 [415, 430] | 423 [414, 431] |  | agree: matches the readers. |
| t10 | 434 | [428, 440] | 434 [427, 441] | 434 [426, 442] |  | agree: matches the readers. |

## f2-m05

Majority vote counts answer strings: the base's wrong answers scatter (only about a quarter repeat), so the right answer is the plurality once per-sample success exceeds about 0.3, and even k leaves ties that a fixed rule breaks about half right. Vote over k therefore rises toward the number of problems whose right answer is the modal string, well below pass@k, with odd k gaining from fewer ties and returns shrinking fast after k = 4.

Rests on: result-5c961a, knowledge-dab63f, result-c637b2, result-0b676d. Forecasts 12 of 23 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t16 | 454 | [448, 460] | 454 [447, 461] | 454 [446, 461] |  | agree: the readers' 454. |
| t17 | 456 | [450, 462] | 456 [448, 463] | 456 [448, 463] |  | agree: the readers' 456. |
| t06 | 53 | [46, 60] | 52 [44, 60] | 53 [44, 62] |  | agree: the readers' 52-53. |
| t19 | 78.5 | [73, 84] | 78 [72, 85] | 79 [72, 86] |  | agree: the readers' 78-79. |
| t20 | 248 | [240, 256] | 248 [238, 258] | 247 [237, 257] |  | agree: matches the readers. |
| t22 | 243 | [235, 251] | 246 [236, 256] | 246 [236, 256] |  | agree: a little below the readers' 246, inside their range. |
| t23 | 78 | [71, 85] | 79 [71, 87] | 80 [72, 88] |  | agree: just under the readers' 79-80. |
| t07 | 48 | [43, 53] | 47.5 [42, 53] | 48 [41, 55] |  | agree: same anchor. |
| t18 | 71 | [65, 77] | 71 [62, 80] | 71 [62, 80] |  | agree: same anchor. |
| t21 | 466 | [458, 474] | 466 [456, 475] | 465 [455, 474] |  | agree: same anchor. |
| t12 | 231 | [219, 243] | 231 [214, 247] | 232 [214, 248] |  | agree: same anchor. |
| t14 | 465 | [456, 474] | 464 [452, 475] | 465 [452, 476] |  | agree: same anchor. |

## f2-m06

A cap hit casts no vote: a model that runs out of tokens abstains instead of guessing, so its vote approaches pass@k (Think-SFT 241 against 244), while a model that finishes long and wrong spends votes on scattered wrong answers (RL 221 against 240). Turning abstentions into finishes (larger cap, RL directions, transplant) raises single-sample counts more than vote counts, because most converted rows are wrong and dilute the right minority.

Rests on: result-818c20, result-fc7efc, result-95a4dc, result-5251c9. Forecasts 12 of 23 targets:

| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |
|---|---|---|---|---|---|---|
| t22 | 242 | [234, 250] | 246 [236, 256] | 246 [236, 256] |  | disagree: the readers add the single-sample cap gain to the vote; once cap hits stop abstaining, the vote's near-pass@4 property weakens, so it stays near 241 (the offline simulation's 240). |
| t23 | 77 | [71, 83] | 79 [71, 87] | 80 [72, 88] |  | disagree: the readers carry hard328's +7 per sample into the vote; the vote gains less than singles when abstentions become guesses. |
| t20 | 249 | [240, 257] | 248 [238, 258] | 247 [237, 257] |  | agree: the readers' 247-248 already scale the vote gain by cap rate. |
| t19 | 79 | [73, 85] | 78 [72, 85] | 79 [72, 86] |  | agree: the readers' 78-79. |
| t06 | 52.5 | [46, 59] | 52 [44, 60] | 53 [44, 62] |  | agree: the readers' 52-53. |
| t07 | 48 | [43, 53] | 47.5 [42, 53] | 48 [41, 55] |  | agree: same anchor. |
| t16 | 454 | [448, 460] | 454 [447, 461] | 454 [446, 461] |  | agree: the readers' 454. |
| t17 | 456 | [450, 462] | 456 [448, 463] | 456 [448, 463] |  | agree: the readers' 456. |
| t18 | 71 | [65, 77] | 71 [62, 80] | 71 [62, 80] |  | agree: same anchor. |
| t12 | 231 | [219, 243] | 231 [214, 247] | 232 [214, 248] |  | agree: same anchor. |
| t13 | 207 | [195, 219] | 206 [188, 223] | 205 [186, 222] |  | agree: same anchor. |
| t15 | 460 | [451, 469] | 460 [447, 472] | 459 [445, 470] |  | agree: same anchor. |

## t01 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems the untrained Olmo 3 base passes with the Code cue at T 1.0 after adding Code-RL 3.1's 8 top weight-change directions at 1x size.

Unit: problems passed of 538. Cell: {"model": "Olmo 3 base + top-8 directions of (Olmo-3.1 RL-Zero-Code - base) at 1x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p and token cap not stated", "samples": "not stated", "grader": "not stated"}

> base + Code 3.1's 8 directions at 1x, 1.5x, 2x, random at 1.5x, and Math 3.1's at 1.5x

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 350 | [325, 376] | Base+Code cue 317 vs RL-Code 401; on hard328 the Math dial at 1x closed about two thirds of the gap, so I assume roughly 40-60% of the 84-problem code gap here. |
| reader-2 | 350 | [325, 375] | Base+Code cue 317, RL-Code 401; Math top-8 at 1x closed about 2/3 of the hard328 gap (164->192 of 206), so about half to two thirds of the 84-problem code gap. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | 338 | [320, 356] | Few code cap hits to convert; only the finished-precision part (about +15 % of finished-wrong fixed on hard328, less for Code directions at 1x) remains: about +20 over 317. |
| f2-m04 | 350 | [326, 374] | Code directions keep the code-block ending; no extraction change, so the count follows solving. |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t02 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems the untrained Olmo 3 base passes with the Code cue at T 1.0 after adding Code-RL 3.1's 8 top weight-change directions at 1.5x size.

Unit: problems passed of 538. Cell: {"model": "Olmo 3 base + top-8 directions of (Olmo-3.1 RL-Zero-Code - base) at 1.5x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p and token cap not stated", "samples": "not stated", "grader": "not stated"}

> base + Code 3.1's 8 directions at 1x, 1.5x, 2x, random at 1.5x, and Math 3.1's at 1.5x

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 360 | [331, 388] | On hard328, 1.5x was the peak of the Math dial and level with RL's single sample, but transfer to code is less certain, so this is about 50% of the gap with a wide interval. |
| reader-2 | 358 | [330, 386] | At 1.5x the Math dial reached RL level on hard328 (203/206); code effect is assumed weaker and less cap-limited, so about 50% of the gap. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | 342 | [322, 362] | 1.5x adds a little more precision; no cap hits to remove. |
| f2-m04 | 358 | [332, 384] | As t01. |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t03 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems the untrained Olmo 3 base passes with the Code cue at T 1.0 after adding Code-RL 3.1's 8 top weight-change directions at 2x size.

Unit: problems passed of 538. Cell: {"model": "Olmo 3 base + top-8 directions of (Olmo-3.1 RL-Zero-Code - base) at 2x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p and token cap not stated", "samples": "not stated", "grader": "not stated"}

> base + Code 3.1's 8 directions at 1x, 1.5x, 2x, random at 1.5x, and Math 3.1's at 1.5x

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 350 | [312, 385] | On hard328, 2x fell back from 1.5x (190 vs 203) as answers got cut short and decayed, and a code-RL extrapolation paper shows a drop past 1.5x, so this is below 1.5x with more spread. |
| reader-2 | 345 | [305, 380] | At 2x the Math dial fell back (190 vs 203) and word-salad tails start, so below 1.5x with a wider downside. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | 330 | [308, 352] | At 2x hard328 precision fell to 0.59 while conversions were mostly wrong; with nothing to convert on code, only that loss shows. |
| f2-m04 | 346 | [310, 380] | As t01; decay at 2x may garble some endings. |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t04 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems the untrained Olmo 3 base passes with the Code cue at T 1.0 after adding a random rank-8 weight edit at 1.5x size (control).

Unit: problems passed of 538. Cell: {"model": "Olmo 3 base + random rank-8 edit at 1.5x (control)", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p and token cap not stated", "samples": "not stated", "grader": "not stated"}

> base + Code 3.1's 8 directions at 1x, 1.5x, 2x, random at 1.5x, and Math 3.1's at 1.5x

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 316 | [299, 333] | The random rank-8 edit was flat at base level on every size tested on hard328, so this is base+Code cue 317 plus sampling noise. |
| reader-2 | 315 | [297, 333] | Random rank-8 edits are flat at the base level (hard328 158-167 vs 164), so about the base+Code cue 317 with single-sample noise. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 316 | [301, 331] | Random rank-8 is flat at base level on hard328 (158-167 at every size); code count = base cue 317 plus one seed of noise. |
| f2-m02 | - |  | no forecast |
| f2-m03 | 316 | [302, 330] | Random rank-8 neither converts cap hits nor changes precision. |
| f2-m04 | 316 | [300, 332] | A random edit does not move the answer format. |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t05 (work-df5e0a): How many of the 538 HumanEval+ and MBPP+ problems the untrained Olmo 3 base passes with the Code cue at T 1.0 after adding Math-RL 3.1's 8 top weight-change directions at 1.5x size.

Unit: problems passed of 538. Cell: {"model": "Olmo 3 base + top-8 directions of (Olmo-3.1 RL-Zero-Math - base) at 1.5x", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p and token cap not stated", "samples": "not stated", "grader": "not stated"}

> base + Code 3.1's 8 directions at 1x, 1.5x, 2x, random at 1.5x, and Math 3.1's at 1.5x

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 343 | [315, 370] | Math-RL also helps code (it scores near Code-RL on LiveCodeBench) and the Math cue matches the Code cue, but other-reward directions gained less on hard328, so it should land between random and Code 1.5x. |
| reader-2 | 338 | [314, 362] | Math-RL transfers to code (LCB 21.9 vs Code-RL 24.3) and Math directions write the cue (Math cue 326) plus finishing, so between base cue and the Code-direction cell. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | 326 | [308, 344] | Math directions mainly convert cap hits and write the deliberative opening, which the Code cue already supplies; little left on code. |
| f2-m04 | 330 | [312, 348] | Math directions write the deliberative opening and a boxed final; part of the answers end without a code block the harness reads. |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t06 (work-16773f): How many of the 136 fresh2026 contest problems the base plus 1.5 times the top 8 RL-Math weight-change directions gets right with the cue under a majority vote over 4 samples.

Unit: right answers of 136 under vote over 4. Cell: {"model": "Olmo 3 base + 1.5 x top 8 directions of (RL-Math - base)", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> is it level with RL (57 vote, 50.5 single) where its size was not chosen?

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 52 | [44, 60] | On hard328 the 1.5x edit matched RL's single sample but trailed RL's vote by 7 problems; RL's vote on fresh2026 is 57, so about 52. |
| reader-2 | 53 | [44, 62] | On hard328 the 1.5x edit matched RL's single (200.25 vs 200) but its vote was 7 below RL's (214 vs 221); RL's fresh vote is 57. |
| r5-m03-rival | 53 | [46, 60] | Theory: the top-8 edit puts most answers (85-90 %) on a weak dose of RL's own policy, so under the vote it lands just below RL (57) and well above the cued base (38), as on hard328 where the 1.5x edit's vote was 214 against RL's 221. |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 53 | [46, 60] | Native 16k cells; the edit boxes like RL, so it keeps RL-like credit on capped rows; RL vote 57. |
| f2-m03 | 52 | [45, 59] | Fresh base caps 40 %: many conversions but at low right rates on 2026 contest problems; vote gain smaller than RL's. |
| f2-m04 | - |  | no forecast |
| f2-m05 | 53 | [46, 60] | Edit's vote gain on hard328 (+14) was 2/3 of RL's (+21); RL fresh +6.5 over 50.5. |
| f2-m06 | 52.5 | [46, 59] | The edit abstains less than RL (cap hits 14-22 vs 24-35 on hard328), so its vote gain is smaller than RL's +6.5. |

## t07 (work-16773f): Mean number of the 136 fresh2026 contest problems the base plus 1.5 times the top 8 RL-Math weight-change directions gets right with the cue, averaged over 4 single samples.

Unit: mean right answers per sample of 136. Cell: {"model": "Olmo 3 base + 1.5 x top 8 directions of (RL-Math - base)", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> is it level with RL (57 vote, 50.5 single) where its size was not chosen?

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 47.5 | [42, 53] | The edit matched RL's single sample on hard328 (200.25 vs 200) and on MATH-500; RL averages 50.5 on fresh2026, shaded down a little for the harder, unchosen set. |
| reader-2 | 48 | [41, 55] | The edit matched RL's single samples on hard328; RL's fresh single is 50.5, minus a little for the harder 2026 set. |
| r5-m03-rival | 47.5 | [41, 54] | Theory: a weak dose of RL's policy on most samples, with the cue covering the rest, puts single-sample accuracy a little under RL's 50.5 and far above the cued base's 29.5 (on hard328 the 1.5x edit was level with RL at 200.25 vs 200). |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 48 | [43, 53] | The edit equals RL per sample on hard328 (200.25 vs 200); RL fresh single 50.5; a 4-sample mean has SD about 1.7 plus model uncertainty. |
| f2-m02 | 48 | [43, 53] | As t06 for single samples; RL single 50.5. |
| f2-m03 | 47 | [42, 52] | Base single 29.5 with 55 caps; edit finishes about 85 % at about 40 % precision. |
| f2-m04 | - |  | no forecast |
| f2-m05 | 48 | [43, 53] | Single samples: no vote, mean per-sample rate near RL's. |
| f2-m06 | 48 | [43, 53] | Single samples: abstention does not matter; edit equals RL per sample. |

## t08 (work-f8ecb6): Mean number of the 500 MATH-500 problems the RL-Zero-Math step-100 checkpoint gets right with the plain prompt at T 1.0 (grader v3), averaged over 4 samples.

Unit: mean right answers per sample of 500 (3 new samples + stored sample 0). Cell: {"model": "Olmo-3.1 RL-Zero-Math checkpoint step 100", "prompt": "plain", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and token cap not stated", "samples": 4, "grader": "v3"}

> 3 more samples of step-100 plain, step-100 cue, step-400 plain (MATH-500, T 1.0, v3)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 416 | [409, 423] | Stored sample 0 is 418; I pull it slightly toward the mean because single samples of a cell spread by about 5-10 problems. |
| reader-2 | 416 | [408, 424] | Stored sample 0 = 418, shrunk slightly toward the mean the way base-cue samples spread from 405 to 418. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 416.5 | [411, 422] | Mean of stored 418 and 3 new draws at a true rate near 416 (SD of the 3-mean about 3.5). |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | 416 | [410, 422] | Step-100 answers box (only 4.5 % use the 'Answer:' line), so v3 reads them as in sample 0. |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t09 (work-f8ecb6): Mean number of the 500 MATH-500 problems the RL-Zero-Math step-100 checkpoint gets right with the opening cue at T 1.0 (grader v3), averaged over 4 samples.

Unit: mean right answers per sample of 500 (3 new samples + stored sample 0). Cell: {"model": "Olmo-3.1 RL-Zero-Math checkpoint step 100", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and token cap not stated", "samples": 4, "grader": "v3"}

> 3 more samples of step-100 plain, step-100 cue, step-400 plain (MATH-500, T 1.0, v3)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 423 | [415, 430] | Stored step-100 cue sample is 427, pulled slightly toward the plain cell since the cue effect at step 100 was +1.8 [-1.2, 4.8]. |
| reader-2 | 423 | [414, 431] | Stored sample 0 = 427, shrunk; the cue on step 100 adds +1.8 [-1.2, 4.8]. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 424 | [418, 430] | Stored 427 and plain 418 plus the +1.8-point cue effect agree near 425; small shrink. |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | 424 | [418, 430] | Cue does not change the boxed ending at step 100. |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t10 (work-f8ecb6): Mean number of the 500 MATH-500 problems the RL-Zero-Math step-400 checkpoint gets right with the plain prompt at T 1.0 (grader v3), averaged over 4 samples.

Unit: mean right answers per sample of 500 (3 new samples + stored sample 0). Cell: {"model": "Olmo-3.1 RL-Zero-Math checkpoint step 400", "prompt": "plain", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and token cap not stated", "samples": 4, "grader": "v3"}

> 3 more samples of step-100 plain, step-100 cue, step-400 plain (MATH-500, T 1.0, v3)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 434 | [427, 441] | Stored step-400 plain sample is 436, shaded slightly for regression to the mean across 4 samples. |
| reader-2 | 434 | [426, 442] | Stored sample 0 = 436, shrunk slightly. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 434.5 | [429, 440] | Stored 436; step 400 cue 431 with cue effect -1.0 implies a plain rate near 434-435. |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | 434 | [428, 440] | Step 400 boxes like RL. |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t11 (work-f8ecb6): Difference in MATH-500 accuracy points between the RL step-100 checkpoint with the plain prompt and the untrained base with the cue at T 1.0 (grader v3), over 4 samples each.

Unit: points (step 100 plain minus cued base, 4-sample mean). Cell: {"model": "Olmo-3.1 RL-Zero-Math step 100 vs untrained Olmo 3 base", "prompt": "plain (step 100) vs cue (base)", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and token cap not stated", "samples": 4, "grader": "v3"}

> so the step-100 vs cued-base difference has a 4-sample interval

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 1.1 | [-0.5, 2.8] | My step-100 plain 4-sample mean of about 416 minus the cued base's 4-sample mean of 410.5, divided by 5 to get points. |
| reader-2 | 1.1 | [-0.7, 2.9] | Step-100 plain mean of about 416 minus the cued base's 4-sample mean of 410.5, divided by 5. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 1.2 | [-0.2, 2.6] | (416.5 - 410.5)/5; the base side's 4 samples are fixed, so only step 100's 3 new draws add noise. |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | - |  | no forecast |
| f2-m06 | - |  | no forecast |

## t12 (work-8b2ec9): How many of the 328 harder problems Think-SFT gets right in its own ChatML chat format with <think>, at T 1.0 with a 32,768-token cap, one sample, grader v3.

Unit: right answers of 328. Cell: {"model": "Olmo-3-7B-Think-SFT", "prompt": "native ChatML template with <think> (no base cue)", "set": "hard328", "n": 328, "sampling": "T 1.0, token cap 32,768; top-p not stated", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 231 | [214, 247] | The raw template plus cue scored 230 at a 32k cap; the native ChatML <think> format is the format it was trained on, so I expect about the same with wide format uncertainty. |
| reader-2 | 232 | [214, 248] | Think-SFT with the cue at cap 32k scored 230; its native format is what it was trained on, so about level or slightly better. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 231 | [218, 244] | Cue at cap 32k scored 230 on one seed; native format is its training format, seed SD about 8. |
| f2-m02 | 231 | [219, 243] | Cut Think-SFT answers are unfinished work: 91 of 93 finish past 16k, about 25 % right; native format behaves like the cue run (230). |
| f2-m03 | 231 | [219, 243] | At 32k, Think-SFT's cap hits convert at about 25 %: as in the cue run (230). |
| f2-m04 | 232 | [220, 244] | hard328 answers are mostly integers, so the misplaced-line loss is about 1-2 at most. |
| f2-m05 | 231 | [219, 243] | Single sample at 32k: cue run 230. |
| f2-m06 | 231 | [219, 243] | Single sample: converted abstentions add about 23 rights, as in the cue run. |

## t13 (work-8b2ec9): How many of the 328 harder problems Think-SFT gets right in its own ChatML chat format with <think> at T 1.0, one sample, counting only answers finished within 16,384 tokens (grader v3).

Unit: right answers of 328. Cell: {"model": "Olmo-3-7B-Think-SFT", "prompt": "native ChatML template with <think> (no base cue)", "set": "hard328", "n": 328, "sampling": "T 1.0, generated at cap 32,768, scored at 16,384; top-p not stated", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 206 | [188, 223] | The cue run at a 32k cap counted at 16k gave 207, and native thinking may run slightly longer and get cut more often. |
| reader-2 | 205 | [186, 222] | The cue run counted at 16k gave 207; native thinking may run longer and lose a little more at 16k. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 207 | [195, 219] | The 32k cue run counted at 16k gave 207; one more seed. |
| f2-m02 | 208 | [197, 219] | t12 minus the ~23 extension finishes; Think-SFT puts its answer after the reasoning, so it loses almost no in-cap box credit (cue run: 207 vs native mean 209). |
| f2-m03 | - |  | no forecast |
| f2-m04 | 207 | [195, 219] | As t12 counted at 16k. |
| f2-m05 | - |  | no forecast |
| f2-m06 | 207 | [195, 219] | Counted at 16k: cut answers are abstentions, so it matches the cue run's 207. |

## t14 (work-8b2ec9): How many of the 500 MATH-500 problems Think-SFT gets right in its own ChatML chat format with <think>, at T 1.0 with a 32,768-token cap, one sample, grader v3.

Unit: right answers of 500. Cell: {"model": "Olmo-3-7B-Think-SFT", "prompt": "native ChatML template with <think> (no base cue)", "set": "MATH-500", "n": 500, "sampling": "T 1.0, token cap 32,768; top-p not stated", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 464 | [452, 475] | Think-SFT cue singles on MATH-500 are 454-462, and on MATH-500 the 32k cap adds little because few answers run past 16k. |
| reader-2 | 465 | [452, 476] | Think-SFT cue singles are 454-462 at 16k; the 32k cap and native format add a few. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 465 | [456, 474] | Think-SFT cue singles 457-462 plus a few cap-hit conversions at 32k; seed SD about 5. |
| f2-m02 | 467 | [459, 475] | About 25 MATH-500 cap hits at 16k; most finish at 32k, roughly 30 % right: +7 over the ~460 base rate. |
| f2-m03 | 467 | [459, 475] | About 25 MATH-500 cap hits, about 30 % right after conversion: +7. |
| f2-m04 | 468 | [459, 477] | ~459.5 base rate + ~4 recovered extraction (native summary ends on an 'Answer:' line, smoke 7/8) + a few cap conversions at 32k. |
| f2-m05 | 465 | [456, 474] | Single sample; cue singles 457-462 plus a few at 32k. |
| f2-m06 | - |  | no forecast |

## t15 (work-8b2ec9): How many of the 500 MATH-500 problems Think-SFT gets right in its own ChatML chat format with <think> at T 1.0, one sample, counting only answers finished within 16,384 tokens (grader v3).

Unit: right answers of 500. Cell: {"model": "Olmo-3-7B-Think-SFT", "prompt": "native ChatML template with <think> (no base cue)", "set": "MATH-500", "n": 500, "sampling": "T 1.0, generated at cap 32,768, scored at 16,384; top-p not stated", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 460 | [447, 472] | Same as the 32k cell minus the few MATH-500 answers that run past 16,384 tokens. |
| reader-2 | 459 | [445, 470] | Close to the cue singles at 16k (454-462). |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 460 | [451, 469] | Same answers minus those finishing past 16,384. |
| f2-m02 | 460 | [452, 468] | Rescored at 16k: same as native Think-SFT singles, since its capped rows hold almost no box to lose. |
| f2-m03 | - |  | no forecast |
| f2-m04 | 462 | [453, 471] | Same extraction gain, minus the answers finishing past 16k. |
| f2-m05 | - |  | no forecast |
| f2-m06 | 460 | [451, 469] | Single sample at 16k, Think-SFT's MATH-500 rate. |

## t16 (work-60f040): How many of the 500 MATH-500 problems the untrained cued base gets right at T 1.0 (grader v3) when the answer is the majority vote over 9 samples.

Unit: right answers of 500 under vote over 9. Cell: {"model": "untrained Olmo 3 base", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and token cap not stated", "samples": 9, "grader": "v3, majority vote"}

> tests the theory prediction never run, vote over 9 = 456 [449, 462] of 500

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 454 | [447, 461] | Vote over 4 is 446 with pass@4 at 467; Wang's majority curve gains about 2.5 points from 4 to 8 votes, and returns shrink beyond that. |
| reader-2 | 454 | [446, 461] | Vote over 4 = 446, pass@4 467; Wang's majority vote gains 2.5 points from 4 to 8, less the vote shortfall the hazard result found. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 456 | [449, 462] | The rival's last sentence says a base-only vote over more samples recovers part of the sharpening share, predicted at 456/500 (the [449, 462] interval is the one on file for vote over 9, against 446 for the stored vote over 4). |
| r6-m06 | 449 | [442, 456] | The theory says the cued base's wrong steps come from the head of its own distribution, so its wrong answers repeat across samples; the vote should then level off near the stored vote over 4 (446, singles 405-418), only a few problems higher, and stay below the 456 that result-c637b2 predicted. |
| r7-m05 | 453 | [446, 460] | The theory covers this cell (cued base, MATH-500, T 1.0, v3): its slip/misread steps sit at the mode only given the path, so siblings mostly get them right (39 of 48) and votes remove them, while wrong plans (problem-conditioned) and base 0-of-4 problems stay; so the vote keeps climbing from the 4-vote 446 toward pass@4 467 but levels off below it, about 453 at 9. |
| r7-m08 | 452 | [445, 459] | The theory's no_intervention clause says selection among base samples is the only base-side veto and it is already measured (vote over 4, 446-450), because the vetoed steps are likely under the base; so I expect more votes to give only a small gain over that plateau, not RL's 456-463. |
| r7-m11 | 452 | [445, 459] | The statement says wrong answers drawn under the shared cue land on the same values, so more cued samples keep the agreeing wrong groups and the vote stays below the independent-slip forecast of 456 (result-c637b2); starting from the 4-vote of 446 and pass@4 of 467 (result-5d032f), odd k removes most ties but not the context-fixed wrong pluralities, giving about 452. |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | 454 | [448, 460] | From 4-sample classes: 4/4 about 370 kept, 3/4 about 44, 2/4 about 27, 1/4 about 10, 0/4 about 2 gives 453; shard 3 at 85.7 % per sample hints the new draws run slightly high. |
| f2-m06 | 454 | [448, 460] | Base cue has about 27 cap hits per sample on MATH-500, all on the hardest problems; abstention matters little here. |

## t17 (work-60f040): How many of the 500 MATH-500 problems the untrained cued base gets right at T 1.0 (grader v3) when the answer is the majority vote over 12 samples.

Unit: right answers of 500 under vote over 12. Cell: {"model": "untrained Olmo 3 base", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and token cap not stated", "samples": 12, "grader": "v3, majority vote"}

> Vote over k = 1..12 samples of the untrained cued base on MATH-500

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 456 | [448, 463] | A small further gain over vote-9 as the vote levels off below pass@k; the base gets 0 of 4 on 33 problems. |
| reader-2 | 456 | [448, 463] | Small further gain over vote 9 as the curve flattens (Wang maj@8 91 -> maj@16 93). |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | 457 | [449, 464] | Same part of the theory: sharpening is the resample-type gap that more base votes recover, so vote over 12 should sit near the predicted 456 plateau, at most a point or so higher. |
| r6-m06 | 450 | [443, 457] | By the same head-error mechanism, going from 9 to 12 samples adds about one problem over the vote over 4 (446), because the base's wrong answers are likely tokens it keeps sampling, not rare draws that more votes would wash out. |
| r7-m05 | 455 | [447, 462] | Same part of the theory: votes keep removing path-specific slips and misreads, but the problem-conditioned wrong plans set a ceiling, so going from 9 to 12 samples adds only about 2 over the 9-vote estimate. |
| r7-m08 | 453 | [446, 461] | Same no_intervention clause: majority vote can't veto steps the base itself rates as likely, so going from 9 to 12 samples should add at most a point or two over the 446-450 plateau. |
| r7-m11 | 453 | [446, 460] | Same mechanism: wrong values set by the shared prompt plus opening repeat in every added cued sample, so going from 9 to 12 votes buys at most a problem or two (a plateau below the independent prediction) rather than reaching pass@4-like levels. |
| f2-m01 | - |  | no forecast |
| f2-m02 | - |  | no forecast |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | 456 | [450, 462] | Three more samples resolve a few more low-p problems; even k adds a few ties back. |
| f2-m06 | 456 | [450, 462] | As t16. |

## t18 (work-8b4030): How many of the 136 fresh2026 contest problems the Think-SFT + 2 x (RL-Math - base) transplant gets right in its remaining fourth sample (sample 1).

Unit: right answers of 136 (sample 1, the fourth sample). Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 1, "grader": "not stated"}

> Sample 1 rerun (first box dropped to a crawl)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 71 | [62, 80] | The other three a=2 samples on fresh2026 scored 69, 70 and 75. |
| reader-2 | 71 | [62, 80] | The other three samples at a=2 were 69, 70 and 75. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 71 | [65, 77] | Other three seeds 69, 70, 75 (mean 71.3, SD about 3); the rerun on a new box changes only batch composition. |
| f2-m02 | 71 | [64, 78] | Native 16k cell like its three siblings; no rescoring artifact. |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | 71 | [65, 77] | Single sample: rate of the three siblings. |
| f2-m06 | 71 | [65, 77] | Single sample at the siblings' rate. |

## t19 (work-8b4030): How many of the 136 fresh2026 contest problems the Think-SFT + 2 x (RL-Math - base) transplant gets right under a majority vote over 4 samples.

Unit: right answers of 136 under vote over 4. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> Think-SFT + 2 x (RL-Math - base) on fresh2026 (136 problems, 4 samples, seeds of SPEC_fresh)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 78 | [72, 85] | Vote over 3 was 78, and a fourth sample barely moved Think-SFT's vote (74 to 75). |
| reader-2 | 79 | [72, 86] | Vote over 3 = 78; a fourth sample adds about 0 to 2. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 79 | [73, 85] | Native 16k cells; vote over 3 = 78. |
| f2-m03 | - |  | no forecast |
| f2-m04 | - |  | no forecast |
| f2-m05 | 78.5 | [73, 84] | A fourth sample turns some 2-1 splits into 2-2 ties broken half right; net 0 to +1 over vote-3 78. |
| f2-m06 | 79 | [73, 85] | a=2 on fresh still abstains on 34 % of samples; a fourth sample adds about one. |

## t20 (work-8b4030): How many of the 328 harder problems the Think-SFT + 2 x (RL-Math - base) transplant gets right under a majority vote over 4 samples.

Unit: right answers of 328 under vote over 4. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated (samples 3-4 at seeds 3,200,000 and 3,300,000)", "samples": 4, "grader": "not stated"}

> hard328 samples 3-4 for the vote over 4

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 248 | [238, 258] | Singles average about 231; the vote adds less than Think-SFT's +32 because a=2 hits the cap less, so roughly +15 to +20. |
| reader-2 | 247 | [237, 257] | Singles about 232; the vote gain is about half of Think-SFT's +32 because a=2 finishes more often (on fresh2026 the vote-3 gain was +7 against +14). |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 248 | [240, 256] | Singles 234 and 229 plus two seeds near 231; vote adds about 17. |
| f2-m02 | 248 | [239, 257] | Native 16k samples; a=2 carries RL's mid-reasoning boxing, so its capped rows keep some v3 credit, as in the stored 234/229. |
| f2-m03 | 249 | [240, 258] | a=2 has already converted half of Think-SFT's caps (94.5 to 44), so its vote gain is between Think-SFT's +32 and RL's +21. |
| f2-m04 | - |  | no forecast |
| f2-m05 | 248 | [240, 256] | Singles about 231; vote adds about 17, between RL's and Think-SFT's gains. |
| f2-m06 | 249 | [240, 257] | a=2 keeps 44 caps (vs Think-SFT 94.5, RL 20) at 72 % precision: vote gain about +18 over a 231 single. |

## t21 (work-8b4030): How many of the 500 MATH-500 problems the Think-SFT + 2 x (RL-Math - base) transplant gets right in one sample.

Unit: right answers of 500. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "MATH-500", "n": 500, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> MATH-500 1 sample

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 466 | [456, 475] | a=1 scored 467 on MATH-500 and Think-SFT cue singles are 454-462; a=2 adds finishing but costs some precision. |
| reader-2 | 465 | [455, 474] | a=1 scored 467 on MATH-500 and Think-SFT cue singles are about 458; a=2 is about the same. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | 466 | [458, 474] | a=1 scored 467; a=2 is one seed of a similar cell. |
| f2-m02 | 466 | [457, 475] | Native 16k MATH-500 cell; a=1 467. |
| f2-m03 | 465 | [456, 474] | Few MATH-500 caps left to convert past a=1; precision falls a little. |
| f2-m04 | 467 | [458, 476] | The RL delta adds RL's boxed ending, which removes Think-SFT's misplaced-line loss and offsets a little precision loss. |
| f2-m05 | 466 | [458, 474] | Single sample, a=1 467. |
| f2-m06 | - |  | no forecast |

## t22 (work-dc9359): How many of the 328 harder problems Think-SFT with the cue gets right under a majority vote over 4 samples generated with a 32,768-token cap.

Unit: right answers of 328 under vote over 4. Cell: {"model": "Olmo-3-7B-Think-SFT", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "token cap 32,768; T and top-p not stated", "samples": 4, "grader": "not stated"}

> Think-SFT + cue vote over 4 at token cap 32,768 on hard328

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 246 | [236, 256] | The 16k vote is 241 and singles rise from 207 to 230 at 32k, but late answers are often wrong (the offline simulation says 240, or 254 if the late wrong answers disagree). |
| reader-2 | 246 | [236, 256] | Vote at 16k = 241; the 32k cap gives 23 more right per sample but mostly wrong extra finishes; the simulation says 240-254. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 245 | [236, 254] | Scored at 32k: extension finishes add right answers to some samples; the mechanism says nothing extra about the vote. |
| f2-m03 | 244 | [235, 253] | Conversions at 32k add rights (23 per sample) but mostly wrong finishes. |
| f2-m04 | - |  | no forecast |
| f2-m05 | 243 | [235, 251] | Long wrong finishes scatter, but where they meet one right answer they make ties; gains and tie losses about cancel against 241. |
| f2-m06 | 242 | [234, 250] | At 32k about 70 of Think-SFT's ~95 cap hits per sample become wrong finishes; problems its vote won by abstention now face wrong votes, offsetting the 23 new rights per sample. |

## t23 (work-dc9359): How many of the 136 fresh2026 contest problems Think-SFT with the cue gets right under a majority vote over 4 samples generated with a 32,768-token cap.

Unit: right answers of 136 under vote over 4. Cell: {"model": "Olmo-3-7B-Think-SFT", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "token cap 32,768; T and top-p not stated", "samples": 4, "grader": "not stated"}

> fresh2026 (4 samples), each answer scored at 16,384 and 32,768 from the same text

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 79 | [71, 87] | The 16k vote is 75 with 46% cap hits; the 32k cap turns some cut answers into right ones, as on hard328 (+7 points per sample). |
| reader-2 | 80 | [72, 88] | Vote at 16k = 75 with 46% cap hits; the longer cap finishes some of them right, as on hard328. |
| r5-m03-rival | - |  | theory says nothing |
| r6-account-rival | - |  | theory says nothing |
| r6-m06 | - |  | theory says nothing |
| r7-m05 | - |  | theory says nothing |
| r7-m08 | - |  | theory says nothing |
| r7-m11 | - |  | theory says nothing |
| f2-m01 | - |  | no forecast |
| f2-m02 | 79 | [72, 86] | Fresh cap hits 46 %, cut answers unfinished, some right at 32k. |
| f2-m03 | 79 | [72, 86] | 46 % cap hits; conversions at about 20 % right. |
| f2-m04 | - |  | no forecast |
| f2-m05 | 78 | [71, 85] | As t22 on fresh: new right finishes partly lost to ties. |
| f2-m06 | 77 | [71, 83] | Fresh cap hits are 46 % of samples, so even more abstentions turn into mostly wrong votes; new rights are partly cancelled. |
