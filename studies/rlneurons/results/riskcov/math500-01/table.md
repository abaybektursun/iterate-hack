# Risk-coverage, math500 (n = 500, 4 samples, attempt 0, T 1.0 / top-p 1.0, grader v3)

Precision = right over kept samples, %. Coverage = kept samples over all samples. Intervals: bootstrap over problems.

## Precision at matched coverage, signal `length`

| Coverage | Think-SFT + cue | RL plain | base + cue | Think-SFT - RL, points [95 %] | RL - base, points [95 %] |
|---|---|---|---|---|---|
| 0.05 | 99.0 | 99.0 | 98.0 | +0.0 [-3.0, +3.0] | +1.0 [-2.0, +5.0] |
| 0.10 | 98.5 | 99.5 | 96.0 | -1.0 [-3.5, +1.0] | +3.5 [+0.5, +7.5] |
| 0.15 | 98.0 | 99.7 | 95.7 | -1.7 [-3.3, +0.3] | +4.0 [+1.7, +7.0] |
| 0.20 | 98.5 | 99.8 | 95.5 | -1.3 [-2.8, +0.0] | +4.3 [+2.0, +6.8] |
| 0.25 | 98.8 | 99.8 | 95.6 | -1.0 [-2.4, +0.0] | +4.2 [+2.2, +6.2] |
| 0.30 | 98.7 | 99.8 | 96.0 | -1.2 [-2.2, -0.2] | +3.8 [+2.2, +5.7] |
| 0.35 | 98.7 | 99.9 | 95.9 | -1.1 [-2.1, -0.3] | +4.0 [+2.4, +5.6] |
| 0.40 | 98.8 | 99.9 | 96.0 | -1.1 [-2.1, -0.4] | +3.9 [+2.5, +5.5] |
| 0.45 | 98.7 | 99.9 | 96.1 | -1.2 [-2.2, -0.3] | +3.8 [+2.4, +5.1] |
| 0.50 | 98.8 | 99.9 | 96.3 | -1.1 [-2.0, -0.3] | +3.6 [+2.4, +4.9] |
| 0.55 | 98.9 | 99.9 | 96.1 | -1.0 [-1.8, -0.4] | +3.8 [+2.5, +5.1] |
| 0.60 | 98.8 | 99.8 | 95.9 | -1.0 [-1.8, -0.2] | +3.8 [+2.7, +5.2] |
| 0.65 | 98.8 | 99.7 | 95.5 | -0.8 [-1.6, -0.2] | +4.2 [+3.0, +5.5] |
| 0.70 | 98.9 | 99.6 | 95.2 | -0.7 [-1.4, -0.1] | +4.4 [+3.3, +6.0] |
| 0.75 | 98.7 | 99.4 | 94.2 | -0.7 [-1.5, +0.1] | +5.2 [+3.9, +6.9] |
| 0.80 | 98.7 | 99.0 | 92.9 | -0.3 [-1.2, +0.4] | +6.1 [+4.7, +8.0] |
| 0.85 | 98.3 | 98.7 | 91.2 | -0.4 [-1.3, +0.6] | +7.5 [+5.7, +9.2] |
| 0.90 | 97.8 | 97.6 | 89.3 | +0.2 [-0.8, +1.2] | +8.3 [+6.8, +10.2] |
| 0.95 | 96.5 | 95.6 | 86.4 | +0.9 [-0.4, +2.1] | +9.2 [+7.5, +10.8] |

## Precision at matched coverage, signal `agreement_length`

| Coverage | Think-SFT + cue | RL plain | base + cue | Think-SFT - RL, points [95 %] | RL - base, points [95 %] |
|---|---|---|---|---|---|
| 0.05 | 100.0 | 100.0 | 100.0 | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] |
| 0.10 | 100.0 | 100.0 | 100.0 | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +1.5] |
| 0.15 | 100.0 | 100.0 | 99.7 | +0.0 [+0.0, +0.0] | +0.3 [+0.0, +1.0] |
| 0.20 | 100.0 | 100.0 | 99.8 | +0.0 [+0.0, +0.0] | +0.2 [+0.0, +0.7] |
| 0.25 | 100.0 | 100.0 | 99.8 | +0.0 [+0.0, +0.0] | +0.2 [+0.0, +0.6] |
| 0.30 | 100.0 | 100.0 | 99.8 | +0.0 [+0.0, +0.0] | +0.2 [+0.0, +0.5] |
| 0.35 | 100.0 | 100.0 | 99.9 | +0.0 [+0.0, +0.0] | +0.1 [+0.0, +0.4] |
| 0.40 | 100.0 | 100.0 | 99.9 | +0.0 [+0.0, +0.0] | +0.1 [+0.0, +0.4] |
| 0.45 | 100.0 | 100.0 | 99.8 | +0.0 [+0.0, +0.0] | +0.2 [+0.0, +0.6] |
| 0.50 | 100.0 | 100.0 | 99.8 | +0.0 [+0.0, +0.0] | +0.2 [+0.0, +0.5] |
| 0.55 | 100.0 | 100.0 | 99.6 | +0.0 [+0.0, +0.0] | +0.4 [+0.0, +0.9] |
| 0.60 | 100.0 | 100.0 | 99.6 | +0.0 [+0.0, +0.0] | +0.4 [+0.0, +1.3] |
| 0.65 | 100.0 | 100.0 | 99.4 | +0.0 [+0.0, +0.0] | +0.6 [+0.0, +1.5] |
| 0.70 | 99.9 | 100.0 | 99.4 | -0.1 [-0.2, +0.0] | +0.6 [+0.0, +1.6] |
| 0.75 | 99.9 | 100.0 | 99.3 | -0.1 [-0.4, +0.0] | +0.7 [+0.0, +1.7] |
| 0.80 | 99.8 | 100.0 | 98.8 | -0.2 [-0.7, +0.1] | +1.2 [+0.2, +2.7] |
| 0.85 | 99.8 | 99.5 | 95.3 | +0.2 [-0.6, +0.9] | +4.2 [+1.6, +7.0] |
| 0.90 | 99.4 | 99.2 | 90.8 | +0.2 [-0.7, +1.2] | +8.4 [+5.9, +10.7] |
| 0.95 | 96.7 | 96.6 | 86.4 | +0.2 [-1.2, +1.6] | +10.2 [+8.3, +11.7] |

## Area: mean precision over the grid up to the common coverage 0.953

| Signal | Think-SFT + cue | RL plain | base + cue | Think-SFT - RL, points [95 %] |
|---|---|---|---|---|
| finished | 97.0 | 93.8 | 87.5 | +3.2 [+1.2, +5.6] |
| length | 98.5 | 99.3 | 94.6 | -0.8 [-1.7, +0.1] |
| agreement | 99.7 | 99.5 | 98.1 | +0.2 [-0.3, +0.7] |
| agreement_length | 99.8 | 99.8 | 98.3 | +0.0 [-0.2, +0.2] |
| finished_length | 98.5 | 99.3 | 94.6 | -0.8 [-1.7, +0.1] |
| shuffled | 95.9 | 92.9 | 86.7 | +3.0 [+0.7, +5.3] |

## Finished answered samples by generated tokens, fixed, all problems

| Bin | Think-SFT + cue: right / samples, % | RL plain: right / samples, % | base + cue: right / samples, % |
|---|---|---|---|
| 1 | 543 / 550, 98.7 (0-2000) | 576 / 577, 99.8 (0-2000) | 975 / 1012, 96.3 (0-2000) |
| 2 | 561 / 566, 99.1 (2000-4000) | 604 / 606, 99.7 (2000-4000) | 337 / 364, 92.6 (2000-4000) |
| 3 | 495 / 505, 98.0 (4000-8000) | 441 / 456, 96.7 (4000-8000) | 188 / 245, 76.7 (4000-8000) |
| 4 | 164 / 183, 89.6 (8000-12000) | 170 / 213, 79.8 (8000-12000) | 99 / 164, 60.4 (8000-12000) |
| 5 | 70 / 91, 76.9 (12000-16384) | 46 / 116, 39.7 (12000-16384) | 42 / 106, 39.6 (12000-16384) |

## Finished answered samples by generated tokens, quartiles, all problems

| Bin | Think-SFT + cue: right / samples, % | RL plain: right / samples, % | base + cue: right / samples, % |
|---|---|---|---|
| 1 | 468 / 474, 98.7 (0-1753) | 491 / 492, 99.8 (0-1818) | 454 / 473, 96.0 (0-884) |
| 2 | 469 / 475, 98.7 (1753-3314) | 492 / 492, 100.0 (1818-3123) | 456 / 473, 96.4 (884-1807) |
| 3 | 468 / 472, 99.2 (3314-5810) | 485 / 492, 98.6 (3123-6158) | 438 / 472, 92.8 (1807-4430) |
| 4 | 428 / 474, 90.3 (5810-16384) | 369 / 492, 75.0 (6158-16384) | 293 / 473, 61.9 (4430-16384) |

## Finished answered samples by generated tokens, fixed, the 491 problems where all three models have a finished answered sample

| Bin | Think-SFT + cue: right / samples, % | RL plain: right / samples, % | base + cue: right / samples, % |
|---|---|---|---|
| 1 | 543 / 550, 98.7 (0-2000) | 576 / 577, 99.8 (0-2000) | 975 / 1012, 96.3 (0-2000) |
| 2 | 561 / 566, 99.1 (2000-4000) | 604 / 606, 99.7 (2000-4000) | 337 / 364, 92.6 (2000-4000) |
| 3 | 495 / 505, 98.0 (4000-8000) | 441 / 456, 96.7 (4000-8000) | 188 / 245, 76.7 (4000-8000) |
| 4 | 164 / 183, 89.6 (8000-12000) | 169 / 209, 80.9 (8000-12000) | 99 / 163, 60.7 (8000-12000) |
| 5 | 67 / 88, 76.1 (12000-16384) | 44 / 100, 44.0 (12000-16384) | 41 / 100, 41.0 (12000-16384) |

## Finished answered samples by generated tokens, quartiles, the 491 problems where all three models have a finished answered sample

| Bin | Think-SFT + cue: right / samples, % | RL plain: right / samples, % | base + cue: right / samples, % |
|---|---|---|---|
| 1 | 467 / 473, 98.7 (0-1750) | 486 / 487, 99.8 (0-1805) | 453 / 472, 96.0 (0-878) |
| 2 | 467 / 473, 98.7 (1750-3301) | 487 / 487, 100.0 (1805-3072) | 453 / 470, 96.4 (878-1790) |
| 3 | 469 / 473, 99.2 (3301-5796) | 481 / 487, 98.8 (3072-6042) | 438 / 472, 92.8 (1790-4380) |
| 4 | 427 / 473, 90.3 (5796-16384) | 380 / 487, 78.0 (6042-16384) | 296 / 470, 63.0 (4380-16384) |

## Problems by Think-SFT cap hits (k of 4): RL plain on finished answered samples

| k | Problems | Right / samples | Precision | Expected from base strata | Observed - expected, points [95 %] | Expected, problems outside the row | Observed - expected, points [95 %] | Cap rate | base + cue precision |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 448 | 1721 / 1783 | 96.5 | 95.5 | +1.0 [+0.4, +1.5] | 92.9 | +3.6 [+0.4, +7.6] | 0.5 | 89.0 |
| 1 | 31 | 95 / 119 | 79.8 | 86.7 | -6.8 [-12.7, -1.1] | 87.7 | -7.8 [-15.1, -1.2] | 4.0 | 74.8 |
| 2 | 7 | 16 / 26 | 61.5 | 65.7 | -4.2 [-20.5, +9.6] | 66.4 | -4.9 [-24.1, +11.2] | 7.1 | 45.5 |
| 3 | 8 | 5 / 25 | 20.0 | 31.8 | -11.8 [-29.5, +8.9] | 35.3 | -15.3 [-38.0, +10.7] | 21.9 | 0.0 |
| 4 | 6 | 0 / 15 | 0.0 | 37.5 | -37.5 [-57.2, -22.0] | 41.5 | -41.5 [-60.7, -25.3] | 37.5 | 14.3 |
| >=1 | 52 | 116 / 185 | 62.7 | 72.3 | -9.6 [-14.8, -4.3] | 81.8 | -19.1 [-29.8, -9.2] | 11.1 | 61.4 |

## Problems by Think-SFT cap hits (k of 4): base + cue on finished answered samples

| k | Problems | Right / samples | Precision | Expected from base strata | Observed - expected, points [95 %] | Expected, problems outside the row | Observed - expected, points [95 %] | Cap rate | base + cue precision |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 448 | 1547 / 1738 | 89.0 | 89.1 | -0.1 [-0.3, +0.0] | 89.4 | -0.4 [-2.5, +0.8] | 2.2 | 89.0 |
| 1 | 31 | 83 / 111 | 74.8 | 73.8 | +1.0 [-1.3, +3.7] | 73.6 | +1.2 [-1.4, +4.2] | 9.7 | 74.8 |
| 2 | 7 | 10 / 22 | 45.5 | 42.2 | +3.2 [-2.8, +14.6] | 42.0 | +3.5 [-2.9, +16.2] | 21.4 | 45.5 |
| 3 | 8 | 0 / 13 | 0.0 | 0.0 | +0.0 [+0.0, +0.0] | 0.0 | +0.0 [+0.0, +0.0] | 53.1 | 0.0 |
| 4 | 6 | 1 / 7 | 14.3 | 13.5 | +0.8 [-1.2, +3.1] | 13.5 | +0.8 [-1.4, +3.3] | 66.7 | 14.3 |
| >=1 | 52 | 94 / 153 | 61.4 | 60.2 | +1.2 [-0.5, +3.4] | 59.9 | +1.5 [-0.6, +4.0] | 24.5 | 61.4 |

## Problems by RL cap hits (k of 4): Think-SFT + cue on finished answered samples

| k | Problems | Right / samples | Precision | Expected from base strata | Observed - expected, points [95 %] | Expected, problems outside the row | Observed - expected, points [95 %] | Cap rate | base + cue precision |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 481 | 1792 / 1851 | 96.8 | 97.1 | -0.3 [-0.5, +0.0] | 98.7 | -1.9 [-13.7, +0.8] | 3.2 | 87.5 |
| 1 | 12 | 32 / 35 | 91.4 | 87.1 | +4.3 [-9.0, +15.6] | 86.5 | +4.9 [-10.2, +18.3] | 27.1 | 58.6 |
| 2 | 1 | 0 / 0 |  |  |  |  |  | 100.0 | 33.3 |
| 3 | 6 | 9 / 9 | 100.0 | 64.1 | +35.9 [+20.3, +53.1] | 59.4 | +40.6 [+23.2, +58.1] | 62.5 | 0.0 |
| 4 | 0 | 0 / 0 |  |  |  |  |  |  | 0.0 |
| >=1 | 19 | 41 / 44 | 93.2 | 82.4 | +10.8 [-0.9, +21.9] | 79.8 | +13.3 [-1.1, +28.8] | 42.1 | 48.6 |

## Problems by RL cap hits (k of 4): base + cue on finished answered samples

| k | Problems | Right / samples | Precision | Expected from base strata | Observed - expected, points [95 %] | Expected, problems outside the row | Observed - expected, points [95 %] | Cap rate | base + cue precision |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 481 | 1623 / 1854 | 87.5 | 87.6 | -0.1 [-0.2, +0.0] | 88.0 | -0.4 [-11.5, +2.6] | 2.8 | 87.5 |
| 1 | 12 | 17 / 29 | 58.6 | 54.5 | +4.1 [-2.5, +14.9] | 54.2 | +4.5 [-2.7, +16.0] | 37.5 | 58.6 |
| 2 | 1 | 1 / 3 | 33.3 | 31.6 | +1.8 [-3.0, +5.1] | 31.5 | +1.8 [-3.3, +5.3] | 25.0 | 33.3 |
| 3 | 6 | 0 / 5 | 0.0 | 0.0 | +0.0 [+0.0, +0.0] | 0.0 | +0.0 [+0.0, +0.0] | 75.0 | 0.0 |
| 4 | 0 | 0 / 0 |  |  |  |  |  |  | 0.0 |
| >=1 | 19 | 18 / 37 | 48.6 | 45.3 | +3.3 [-1.7, +10.9] | 44.9 | +3.7 [-1.9, +12.2] | 48.7 | 48.6 |

## Outcomes, single (4 sample pairs per problem, summed): Think-SFT + cue (rows) against RL plain (columns)

| | abstained | wrong | right |
|---|---|---|---|
| abstained | 3 | 46 | 29 |
| wrong | 0 | 36 | 45 |
| right | 4 | 71 | 1766 |

## Outcomes, single (4 sample pairs per problem, summed): Think-SFT + cue (rows) against base + cue (columns)

| | abstained | wrong | right |
|---|---|---|---|
| abstained | 33 | 21 | 24 |
| wrong | 4 | 45 | 32 |
| right | 57 | 198 | 1586 |

## Outcomes, vote (problems): Think-SFT + cue (rows) against RL plain (columns)

| | abstained | wrong | right |
|---|---|---|---|
| abstained | 0 | 6 | 0 |
| wrong | 0 | 7 | 6 |
| right | 0 | 13 | 468 |

## Outcomes, vote (problems): Think-SFT + cue (rows) against base + cue (columns)

| | abstained | wrong | right |
|---|---|---|---|
| abstained | 2 | 4 | 0 |
| wrong | 0 | 11 | 2 |
| right | 2 | 35 | 444 |

## The 13 problems where Think-SFT's vote is right and RL's is not (reverse: 6)

| Samples on these problems | 0-2000 | 2000-4000 | 4000-8000 | 8000-12000 | 12000-16384 | abstained / wrong / right |
|---|---|---|---|---|---|---|
| Think-SFT + cue, right samples by tokens | 0 | 0 | 5 | 10 | 14 | 17 / 6 / 29 |
| RL plain, wrong samples by tokens | 0 | 0 | 1 | 11 | 31 | 1 / 43 / 8 |

RL has a right sample on 7 of them.

## Vote after dropping samples longer than L tokens

| Model | Rule | Right | Wrong | Abstained | Tokens as run | Tokens, stopped at L |
|---|---|---|---|---|---|---|
| Think-SFT + cue | plain | 481 | 13 | 6 | 19503 | 19503 |
| Think-SFT + cue | strict_2000 | 219 | 2 | 279 | 19503 | 7173 |
| Think-SFT + cue | strict_3000 | 302 | 3 | 195 | 19503 | 9717 |
| Think-SFT + cue | strict_4000 | 352 | 2 | 146 | 19503 | 11712 |
| Think-SFT + cue | strict_6000 | 404 | 4 | 92 | 19503 | 14476 |
| Think-SFT + cue | strict_8000 | 444 | 6 | 50 | 19503 | 16258 |
| Think-SFT + cue | strict_10000 | 463 | 10 | 27 | 19503 | 17508 |
| Think-SFT + cue | strict_12000 | 470 | 10 | 20 | 19503 | 18372 |
| Think-SFT + cue | strict_14000 | 475 | 12 | 13 | 19503 | 18988 |
| Think-SFT + cue | strict_16000 | 480 | 12 | 8 | 19503 | 19430 |
| Think-SFT + cue | fallback_2000 | 481 | 13 | 6 | 19503 | 18575 |
| Think-SFT + cue | fallback_3000 | 480 | 14 | 6 | 19503 | 18432 |
| Think-SFT + cue | fallback_4000 (chosen on MATH-500) | 482 | 12 | 6 | 19503 | 18336 |
| Think-SFT + cue | fallback_6000 | 481 | 13 | 6 | 19503 | 18565 |
| Think-SFT + cue | fallback_8000 | 480 | 14 | 6 | 19503 | 18435 |
| Think-SFT + cue | fallback_10000 | 480 | 14 | 6 | 19503 | 18599 |
| Think-SFT + cue | fallback_12000 | 480 | 14 | 6 | 19503 | 18964 |
| Think-SFT + cue | fallback_14000 | 481 | 13 | 6 | 19503 | 19224 |
| Think-SFT + cue | fallback_16000 | 481 | 13 | 6 | 19503 | 19454 |
| RL plain | plain | 474 | 26 | 0 | 18747 | 18747 |
| RL plain | strict_2000 | 197 | 0 | 303 | 18747 | 7277 |
| RL plain | strict_3000 | 289 | 0 | 211 | 18747 | 9705 |
| RL plain | strict_4000 | 347 | 2 | 151 | 18747 | 11551 |
| RL plain | strict_6000 | 404 | 3 | 93 | 18747 | 14198 |
| RL plain | strict_8000 | 445 | 5 | 50 | 18747 | 16004 |
| RL plain | strict_10000 | 463 | 7 | 30 | 18747 | 17202 |
| RL plain | strict_12000 | 469 | 19 | 12 | 18747 | 17980 |
| RL plain | strict_14000 | 474 | 19 | 7 | 18747 | 18466 |
| RL plain | strict_16000 | 475 | 25 | 0 | 18747 | 18721 |
| RL plain | fallback_2000 | 474 | 26 | 0 | 18747 | 18454 |
| RL plain | fallback_3000 | 474 | 26 | 0 | 18747 | 18308 |
| RL plain | fallback_4000 | 472 | 28 | 0 | 18747 | 17997 |
| RL plain | fallback_6000 | 473 | 27 | 0 | 18747 | 17913 |
| RL plain | fallback_8000 | 473 | 27 | 0 | 18747 | 17952 |
| RL plain | fallback_10000 | 473 | 27 | 0 | 18747 | 18152 |
| RL plain | fallback_12000 | 471 | 29 | 0 | 18747 | 18305 |
| RL plain | fallback_14000 | 474 | 26 | 0 | 18747 | 18562 |
| RL plain | fallback_16000 (chosen on MATH-500) | 475 | 25 | 0 | 18747 | 18721 |
| base + cue | plain | 446 | 50 | 4 | 16034 | 16034 |
| base + cue | strict_2000 | 316 | 12 | 172 | 16034 | 5958 |
| base + cue | strict_3000 | 362 | 16 | 122 | 16034 | 7663 |
| base + cue | strict_4000 | 390 | 16 | 94 | 16034 | 9001 |
| base + cue | strict_6000 | 420 | 23 | 57 | 16034 | 11103 |
| base + cue | strict_8000 | 436 | 26 | 38 | 16034 | 12716 |
| base + cue | strict_10000 | 448 | 31 | 21 | 16034 | 13941 |
| base + cue | strict_12000 | 449 | 37 | 14 | 16034 | 14847 |
| base + cue | strict_14000 | 447 | 45 | 8 | 16034 | 15495 |
| base + cue | strict_16000 | 446 | 48 | 6 | 16034 | 15962 |
| base + cue | fallback_2000 | 441 | 55 | 4 | 16034 | 14922 |
| base + cue | fallback_3000 | 441 | 55 | 4 | 16034 | 14500 |
| base + cue | fallback_4000 | 443 | 53 | 4 | 16034 | 14231 |
| base + cue | fallback_6000 | 444 | 52 | 4 | 16034 | 14077 |
| base + cue | fallback_8000 | 447 | 49 | 4 | 16034 | 14449 |
| base + cue | fallback_10000 | 450 | 46 | 4 | 16034 | 14765 |
| base + cue | fallback_12000 (chosen on MATH-500) | 450 | 46 | 4 | 16034 | 15262 |
| base + cue | fallback_14000 | 447 | 49 | 4 | 16034 | 15624 |
| base + cue | fallback_16000 | 446 | 50 | 4 | 16034 | 15978 |

## Chosen cut against the plain vote over 4

| Model | Rule | Right | Plain vote | Difference, points [95 %] |
|---|---|---|---|---|
| Think-SFT + cue | fallback_4000 | 482 | 481 | +0.2 [+0.0, +0.6] |
| RL plain | fallback_16000 | 475 | 474 | +0.2 [+0.0, +0.6] |
| base + cue | fallback_12000 | 450 | 446 | +0.8 [+0.2, +1.6] |

## Score = right - lambda x wrong (problems)

| Model | Unit | Right | Wrong | Abstained | lambda 0 | lambda 0.5 | lambda 1 |
|---|---|---|---|---|---|---|---|
| Think-SFT + cue | single_mean_of_4 | 460.2 | 20.2 | 19.5 | 460.2 | 450.1 | 440.0 |
| Think-SFT + cue | vote | 481.0 | 13.0 | 6.0 | 481.0 | 474.5 | 468.0 |
| RL plain | single_mean_of_4 | 460.0 | 38.2 | 1.8 | 460.0 | 440.9 | 421.8 |
| RL plain | vote | 474.0 | 26.0 | 0.0 | 474.0 | 461.0 | 448.0 |
| base + cue | single_mean_of_4 | 410.5 | 66.0 | 23.5 | 410.5 | 377.5 | 344.5 |
| base + cue | vote | 446.0 | 50.0 | 4.0 | 446.0 | 421.0 | 396.0 |
