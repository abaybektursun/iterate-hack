# Risk-coverage, hard328 (n = 328, 4 samples, attempt 0, T 1.0 / top-p 1.0, grader v3)

Precision = right over kept samples, %. Coverage = kept samples over all samples. Intervals: bootstrap over problems.

## Precision at matched coverage, signal `length`

| Coverage | Think-SFT + cue | RL plain | base + cue | Think-SFT - RL, points [95 %] | RL - base, points [95 %] |
|---|---|---|---|---|---|
| 0.05 | 98.5 | 100.0 | 97.0 | -1.5 [-4.5, +0.0] | +3.0 [+0.0, +7.6] |
| 0.10 | 98.5 | 99.2 | 97.7 | -0.8 [-3.8, +2.3] | +1.5 [-0.8, +5.3] |
| 0.15 | 98.5 | 99.5 | 95.4 | -1.0 [-4.1, +1.0] | +4.1 [+1.0, +7.6] |
| 0.20 | 98.5 | 99.6 | 94.7 | -1.1 [-3.8, +0.4] | +5.0 [+2.3, +8.8] |
| 0.25 | 98.2 | 99.4 | 93.0 | -1.2 [-3.0, +0.6] | +6.4 [+3.4, +10.1] |
| 0.30 | 98.5 | 99.0 | 91.4 | -0.5 [-2.3, +1.0] | +7.6 [+4.6, +11.4] |
| 0.35 | 98.0 | 98.0 | 89.1 | +0.0 [-2.0, +2.4] | +8.9 [+5.4, +12.0] |
| 0.40 | 97.7 | 97.1 | 87.2 | +0.6 [-1.1, +3.4] | +9.9 [+5.9, +13.0] |
| 0.45 | 96.3 | 95.1 | 84.9 | +1.2 [-1.2, +4.4] | +10.2 [+6.8, +13.6] |
| 0.50 | 94.8 | 93.0 | 82.3 | +1.8 [-0.8, +5.5] | +10.7 [+7.3, +13.9] |
| 0.55 | 94.0 | 90.3 | 80.1 | +3.7 [+0.6, +7.1] | +10.2 [+7.5, +14.0] |
| 0.60 | 93.0 | 87.3 | 76.1 | +5.7 [+2.2, +9.9] | +11.2 [+7.8, +14.4] |
| 0.65 | 91.1 | 83.0 | 71.9 | +8.1 [+4.6, +11.7] | +11.1 [+7.9, +14.7] |
| 0.70 | 88.8 | 79.4 | 67.5 | +9.4 [+6.3, +12.3] | +11.9 [+8.6, +14.8] |
| 0.75 | 85.0 | 76.1 | 63.9 | +8.8 [+6.4, +12.5] | +12.2 [+9.1, +15.4] |

## Precision at matched coverage, signal `agreement_length`

| Coverage | Think-SFT + cue | RL plain | base + cue | Think-SFT - RL, points [95 %] | RL - base, points [95 %] |
|---|---|---|---|---|---|
| 0.05 | 100.0 | 100.0 | 100.0 | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] |
| 0.10 | 100.0 | 100.0 | 100.0 | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +1.5] |
| 0.15 | 100.0 | 100.0 | 99.0 | +0.0 [+0.0, +0.0] | +1.0 [+0.0, +4.1] |
| 0.20 | 99.6 | 100.0 | 98.5 | -0.4 [-1.1, +0.0] | +1.5 [+0.0, +4.6] |
| 0.25 | 99.7 | 100.0 | 98.8 | -0.3 [-1.2, +0.0] | +1.2 [+0.0, +3.7] |
| 0.30 | 99.5 | 100.0 | 98.7 | -0.5 [-2.3, +0.0] | +1.3 [+0.0, +4.1] |
| 0.35 | 99.3 | 100.0 | 98.3 | -0.7 [-2.6, +0.0] | +1.7 [+0.0, +4.8] |
| 0.40 | 98.7 | 99.8 | 97.9 | -1.1 [-2.7, +1.5] | +1.9 [-0.6, +5.0] |
| 0.45 | 98.1 | 97.8 | 95.3 | +0.3 [-2.2, +6.1] | +2.5 [-1.0, +6.4] |
| 0.50 | 98.3 | 93.9 | 90.7 | +4.4 [-0.3, +7.9] | +3.2 [-0.2, +10.7] |
| 0.55 | 97.9 | 93.4 | 83.9 | +4.6 [+1.7, +8.0] | +9.4 [+2.5, +15.5] |
| 0.60 | 96.8 | 91.7 | 78.1 | +5.1 [+2.3, +8.9] | +13.6 [+8.0, +17.3] |
| 0.65 | 94.3 | 87.7 | 73.3 | +6.6 [+3.0, +10.0] | +14.4 [+10.6, +18.6] |
| 0.70 | 90.0 | 83.3 | 68.3 | +6.6 [+3.4, +9.9] | +15.0 [+11.3, +19.0] |
| 0.75 | 85.0 | 79.0 | 64.1 | +6.0 [+3.4, +10.2] | +14.8 [+11.6, +18.6] |

## Area: mean precision over the grid up to the common coverage 0.752

| Signal | Think-SFT + cue | RL plain | base + cue | Think-SFT - RL, points [95 %] |
|---|---|---|---|---|
| finished | 87.3 | 65.9 | 63.6 | +21.5 [+17.2, +25.9] |
| length | 95.3 | 93.1 | 84.8 | +2.2 [+0.6, +4.2] |
| agreement | 96.6 | 91.8 | 89.4 | +4.9 [+2.4, +8.1] |
| agreement_length | 97.1 | 95.1 | 89.7 | +2.0 [+0.8, +3.7] |
| finished_length | 95.3 | 93.1 | 84.8 | +2.2 [+0.6, +4.2] |
| shuffled | 83.6 | 62.0 | 61.6 | +21.6 [+17.0, +26.1] |

## Finished answered samples by generated tokens, fixed, all problems

| Bin | Think-SFT + cue: right / samples, % | RL plain: right / samples, % | base + cue: right / samples, % |
|---|---|---|---|
| 1 | 74 / 75, 98.7 (0-2000) | 59 / 59, 100.0 (0-2000) | 171 / 177, 96.6 (0-2000) |
| 2 | 170 / 173, 98.3 (2000-4000) | 185 / 186, 99.5 (2000-4000) | 169 / 191, 88.5 (2000-4000) |
| 3 | 283 / 292, 96.9 (4000-8000) | 288 / 310, 92.9 (4000-8000) | 161 / 221, 72.9 (4000-8000) |
| 4 | 160 / 193, 82.9 (8000-12000) | 174 / 286, 60.8 (8000-12000) | 88 / 164, 53.7 (8000-12000) |
| 5 | 135 / 198, 68.2 (12000-16384) | 87 / 356, 24.4 (12000-16384) | 41 / 246, 16.7 (12000-16384) |

## Finished answered samples by generated tokens, quartiles, all problems

| Bin | Think-SFT + cue: right / samples, % | RL plain: right / samples, % | base + cue: right / samples, % |
|---|---|---|---|
| 1 | 229 / 233, 98.3 (0-3756) | 298 / 300, 99.3 (0-4483) | 236 / 250, 94.4 (0-2676) |
| 2 | 228 / 233, 97.9 (3756-6573) | 269 / 299, 90.0 (4483-8733) | 206 / 250, 82.4 (2676-6007) |
| 3 | 201 / 232, 86.6 (6573-11343) | 152 / 299, 50.8 (8733-12614) | 146 / 249, 58.6 (6007-11856) |
| 4 | 164 / 233, 70.4 (11343-16384) | 74 / 299, 24.7 (12614-16384) | 42 / 250, 16.8 (11856-16384) |

## Finished answered samples by generated tokens, fixed, the 267 problems where all three models have a finished answered sample

| Bin | Think-SFT + cue: right / samples, % | RL plain: right / samples, % | base + cue: right / samples, % |
|---|---|---|---|
| 1 | 74 / 75, 98.7 (0-2000) | 59 / 59, 100.0 (0-2000) | 171 / 177, 96.6 (0-2000) |
| 2 | 170 / 173, 98.3 (2000-4000) | 185 / 186, 99.5 (2000-4000) | 169 / 191, 88.5 (2000-4000) |
| 3 | 283 / 292, 96.9 (4000-8000) | 287 / 308, 93.2 (4000-8000) | 160 / 214, 74.8 (4000-8000) |
| 4 | 154 / 185, 83.2 (8000-12000) | 165 / 248, 66.5 (8000-12000) | 86 / 153, 56.2 (8000-12000) |
| 5 | 123 / 182, 67.6 (12000-16384) | 73 / 216, 33.8 (12000-16384) | 40 / 181, 22.1 (12000-16384) |

## Finished answered samples by generated tokens, quartiles, the 267 problems where all three models have a finished answered sample

| Bin | Think-SFT + cue: right / samples, % | RL plain: right / samples, % | base + cue: right / samples, % |
|---|---|---|---|
| 1 | 223 / 227, 98.2 (0-3706) | 254 / 255, 99.6 (0-4130) | 217 / 229, 94.8 (0-2482) |
| 2 | 222 / 227, 97.8 (3706-6400) | 241 / 254, 94.9 (4130-7234) | 194 / 229, 84.7 (2482-5409) |
| 3 | 197 / 226, 87.2 (6400-10910) | 184 / 254, 72.4 (7234-11354) | 149 / 229, 65.1 (5409-10800) |
| 4 | 162 / 227, 71.4 (10910-16384) | 90 / 254, 35.4 (11354-16384) | 66 / 229, 28.8 (10800-16384) |

## Problems by Think-SFT cap hits (k of 4): RL plain on finished answered samples

| k | Problems | Right / samples | Precision | Expected from base strata | Observed - expected, points [95 %] | Expected, problems outside the row | Observed - expected, points [95 %] | Cap rate | base + cue precision |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 187 | 649 / 736 | 88.2 | 85.7 | +2.5 [+0.7, +4.2] | 80.9 | +7.2 [-0.6, +15.9] | 1.5 | 79.8 |
| 1 | 32 | 74 / 114 | 64.9 | 61.8 | +3.1 [-6.9, +13.5] | 61.6 | +3.4 [-8.9, +16.0] | 10.9 | 51.5 |
| 2 | 29 | 31 / 97 | 32.0 | 33.2 | -1.2 [-10.6, +8.3] | 33.3 | -1.4 [-12.9, +10.6] | 16.4 | 14.5 |
| 3 | 32 | 26 / 103 | 25.2 | 25.2 | +0.0 [-10.9, +12.5] | 24.5 | +0.7 [-13.1, +16.5] | 19.5 | 13.5 |
| 4 | 48 | 13 / 147 | 8.8 | 22.8 | -14.0 [-20.5, -7.5] | 29.2 | -20.4 [-29.6, -11.2] | 23.4 | 3.8 |
| >=1 | 141 | 144 / 461 | 31.2 | 35.2 | -3.9 [-6.9, -1.0] | 48.9 | -17.6 [-31.0, -4.5] | 18.3 | 23.6 |

## Problems by Think-SFT cap hits (k of 4): base + cue on finished answered samples

| k | Problems | Right / samples | Precision | Expected from base strata | Observed - expected, points [95 %] | Expected, problems outside the row | Observed - expected, points [95 %] | Cap rate | base + cue precision |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 187 | 560 / 702 | 79.8 | 80.0 | -0.2 [-0.7, +0.2] | 78.7 | +1.0 [-2.1, +3.3] | 4.1 | 79.8 |
| 1 | 32 | 50 / 97 | 51.5 | 50.6 | +0.9 [-1.4, +3.8] | 50.3 | +1.2 [-1.8, +4.7] | 24.2 | 51.5 |
| 2 | 29 | 10 / 69 | 14.5 | 15.3 | -0.8 [-2.9, +1.1] | 15.6 | -1.1 [-3.8, +1.3] | 37.9 | 14.5 |
| 3 | 32 | 7 / 52 | 13.5 | 10.6 | +2.8 [-0.7, +7.3] | 10.4 | +3.0 [-0.8, +7.9] | 57.0 | 13.5 |
| 4 | 48 | 3 / 79 | 3.8 | 3.9 | -0.1 [-2.4, +1.8] | 3.9 | -0.1 [-2.7, +2.0] | 55.7 | 3.8 |
| >=1 | 141 | 70 / 297 | 23.6 | 23.0 | +0.6 [-0.4, +1.6] | 22.3 | +1.3 [-0.4, +3.1] | 45.2 | 23.6 |

## Problems by RL cap hits (k of 4): Think-SFT + cue on finished answered samples

| k | Problems | Right / samples | Precision | Expected from base strata | Observed - expected, points [95 %] | Expected, problems outside the row | Observed - expected, points [95 %] | Cap rate | base + cue precision |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 261 | 754 / 841 | 89.7 | 90.3 | -0.6 [-1.8, +0.4] | 90.2 | -0.5 [-12.4, +16.3] | 19.2 | 69.5 |
| 1 | 36 | 45 / 52 | 86.5 | 76.1 | +10.4 [-2.6, +23.0] | 74.6 | +11.9 [-3.1, +27.7] | 63.9 | 23.8 |
| 2 | 17 | 10 / 21 | 47.6 | 51.7 | -4.1 [-38.8, +23.0] | 52.3 | -4.7 [-43.0, +25.7] | 69.1 | 0.0 |
| 3 | 12 | 11 / 13 | 84.6 | 77.4 | +7.2 [-21.5, +26.6] | 76.6 | +8.0 [-22.2, +28.1] | 72.9 | 33.3 |
| 4 | 2 | 2 / 4 | 50.0 | 51.7 | -1.7 [-58.8, +21.3] | 51.8 | -1.8 [-59.2, +22.0] | 50.0 | 0.0 |
| >=1 | 67 | 68 / 90 | 75.6 | 69.5 | +6.0 [-4.4, +15.7] | 66.9 | +8.6 [-5.7, +22.6] | 66.4 | 19.5 |

## Problems by RL cap hits (k of 4): base + cue on finished answered samples

| k | Problems | Right / samples | Precision | Expected from base strata | Observed - expected, points [95 %] | Expected, problems outside the row | Observed - expected, points [95 %] | Cap rate | base + cue precision |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 261 | 605 / 871 | 69.5 | 69.6 | -0.2 [-0.5, +0.1] | 69.9 | -0.5 [-7.2, +1.9] | 14.6 | 69.5 |
| 1 | 36 | 19 / 80 | 23.8 | 23.2 | +0.5 [-1.7, +3.4] | 23.2 | +0.5 [-2.2, +3.7] | 43.8 | 23.8 |
| 2 | 17 | 0 / 28 | 0.0 | 0.0 | +0.0 [+0.0, +0.0] | 0.0 | +0.0 [+0.0, +0.0] | 55.9 | 0.0 |
| 3 | 12 | 6 / 18 | 33.3 | 27.9 | +5.4 [-2.9, +18.9] | 27.2 | +6.1 [-3.1, +20.8] | 56.2 | 33.3 |
| 4 | 2 | 0 / 2 | 0.0 | 0.0 | +0.0 [+0.0, +0.0] | 0.0 | +0.0 [+0.0, +0.0] | 75.0 | 0.0 |
| >=1 | 67 | 25 / 128 | 19.5 | 18.4 | +1.1 [-0.7, +3.0] | 18.1 | +1.4 [-0.7, +3.9] | 50.0 | 19.5 |

## Outcomes, single (4 sample pairs per problem, summed): Think-SFT + cue (rows) against RL plain (columns)

| | abstained | wrong | right |
|---|---|---|---|
| abstained | 26 | 248 | 52 |
| wrong | 2 | 121 | 27 |
| right | 8 | 107 | 721 |

## Outcomes, single (4 sample pairs per problem, summed): Think-SFT + cue (rows) against base + cue (columns)

| | abstained | wrong | right |
|---|---|---|---|
| abstained | 160 | 144 | 22 |
| wrong | 26 | 102 | 22 |
| right | 78 | 168 | 590 |

## Outcomes, vote (problems): Think-SFT + cue (rows) against RL plain (columns)

| | abstained | wrong | right |
|---|---|---|---|
| abstained | 0 | 26 | 4 |
| wrong | 0 | 55 | 2 |
| right | 0 | 26 | 215 |

## Outcomes, vote (problems): Think-SFT + cue (rows) against base + cue (columns)

| | abstained | wrong | right |
|---|---|---|---|
| abstained | 3 | 25 | 2 |
| wrong | 2 | 52 | 3 |
| right | 7 | 47 | 187 |

## The 26 problems where Think-SFT's vote is right and RL's is not (reverse: 6)

| Samples on these problems | 0-2000 | 2000-4000 | 4000-8000 | 8000-12000 | 12000-16384 | abstained / wrong / right |
|---|---|---|---|---|---|---|
| Think-SFT + cue, right samples by tokens | 0 | 0 | 4 | 14 | 35 | 40 / 11 / 53 |
| RL plain, wrong samples by tokens | 0 | 0 | 1 | 21 | 58 | 11 / 80 / 13 |

RL has a right sample on 13 of them.

## Vote after dropping samples longer than L tokens

| Model | Rule | Right | Wrong | Abstained | Tokens as run | Tokens, stopped at L |
|---|---|---|---|---|---|---|
| Think-SFT + cue | plain | 241 | 57 | 30 | 40410 | 40410 |
| Think-SFT + cue | strict_2000 | 30 | 1 | 297 | 40410 | 7884 |
| Think-SFT + cue | strict_3000 | 68 | 1 | 259 | 40410 | 11543 |
| Think-SFT + cue | strict_4000 | 91 | 2 | 235 | 40410 | 14909 |
| Think-SFT + cue | strict_6000 | 130 | 4 | 194 | 40410 | 20791 |
| Think-SFT + cue | strict_8000 | 157 | 5 | 166 | 40410 | 25804 |
| Think-SFT + cue | strict_10000 | 179 | 9 | 140 | 40410 | 30228 |
| Think-SFT + cue | strict_12000 | 204 | 16 | 108 | 40410 | 34042 |
| Think-SFT + cue | strict_14000 | 228 | 23 | 77 | 40410 | 37258 |
| Think-SFT + cue | strict_16000 | 237 | 40 | 51 | 40410 | 39957 |
| Think-SFT + cue | fallback_2000 | 241 | 57 | 30 | 40410 | 40150 |
| Think-SFT + cue | fallback_3000 | 241 | 57 | 30 | 40410 | 39850 |
| Think-SFT + cue | fallback_4000 (chosen on MATH-500) | 240 | 58 | 30 | 40410 | 39782 |
| Think-SFT + cue | fallback_6000 | 240 | 58 | 30 | 40410 | 39576 |
| Think-SFT + cue | fallback_8000 | 239 | 59 | 30 | 40410 | 39436 |
| Think-SFT + cue | fallback_10000 | 239 | 59 | 30 | 40410 | 39309 |
| Think-SFT + cue | fallback_12000 | 239 | 59 | 30 | 40410 | 39156 |
| Think-SFT + cue | fallback_14000 | 243 | 55 | 30 | 40410 | 39346 |
| Think-SFT + cue | fallback_16000 | 240 | 58 | 30 | 40410 | 40195 |
| RL plain | plain | 221 | 107 | 0 | 37299 | 37299 |
| RL plain | strict_2000 | 28 | 0 | 300 | 37299 | 7923 |
| RL plain | strict_3000 | 53 | 0 | 275 | 37299 | 11615 |
| RL plain | strict_4000 | 89 | 0 | 239 | 37299 | 15025 |
| RL plain | strict_6000 | 129 | 2 | 197 | 37299 | 20934 |
| RL plain | strict_8000 | 158 | 10 | 160 | 37299 | 25939 |
| RL plain | strict_10000 | 189 | 26 | 113 | 37299 | 30167 |
| RL plain | strict_12000 | 210 | 59 | 59 | 37299 | 33541 |
| RL plain | strict_14000 | 220 | 91 | 17 | 37299 | 35855 |
| RL plain | strict_16000 | 223 | 101 | 4 | 37299 | 37151 |
| RL plain | fallback_2000 | 221 | 107 | 0 | 37299 | 37159 |
| RL plain | fallback_3000 | 221 | 107 | 0 | 37299 | 37018 |
| RL plain | fallback_4000 | 221 | 107 | 0 | 37299 | 36894 |
| RL plain | fallback_6000 | 221 | 107 | 0 | 37299 | 36677 |
| RL plain | fallback_8000 | 221 | 107 | 0 | 37299 | 36329 |
| RL plain | fallback_10000 | 220 | 108 | 0 | 37299 | 35873 |
| RL plain | fallback_12000 | 222 | 106 | 0 | 37299 | 35669 |
| RL plain | fallback_14000 | 223 | 105 | 0 | 37299 | 36251 |
| RL plain | fallback_16000 (chosen on MATH-500) | 224 | 104 | 0 | 37299 | 37168 |
| base + cue | plain | 192 | 124 | 12 | 36902 | 36902 |
| base + cue | strict_2000 | 70 | 2 | 256 | 36902 | 7614 |
| base + cue | strict_3000 | 97 | 6 | 225 | 36902 | 10896 |
| base + cue | strict_4000 | 121 | 10 | 197 | 36902 | 13894 |
| base + cue | strict_6000 | 144 | 24 | 160 | 36902 | 19181 |
| base + cue | strict_8000 | 161 | 41 | 126 | 36902 | 23757 |
| base + cue | strict_10000 | 172 | 49 | 107 | 36902 | 27842 |
| base + cue | strict_12000 | 182 | 61 | 85 | 36902 | 31415 |
| base + cue | strict_14000 | 186 | 92 | 50 | 36902 | 34355 |
| base + cue | strict_16000 | 189 | 120 | 19 | 36902 | 36556 |
| base + cue | fallback_2000 | 191 | 125 | 12 | 36902 | 36116 |
| base + cue | fallback_3000 | 190 | 126 | 12 | 36902 | 35563 |
| base + cue | fallback_4000 | 187 | 129 | 12 | 36902 | 35288 |
| base + cue | fallback_6000 | 185 | 131 | 12 | 36902 | 34540 |
| base + cue | fallback_8000 | 184 | 132 | 12 | 36902 | 34098 |
| base + cue | fallback_10000 | 186 | 130 | 12 | 36902 | 34591 |
| base + cue | fallback_12000 (chosen on MATH-500) | 189 | 127 | 12 | 36902 | 35124 |
| base + cue | fallback_14000 | 191 | 125 | 12 | 36902 | 35607 |
| base + cue | fallback_16000 | 191 | 125 | 12 | 36902 | 36642 |

## Chosen cut against the plain vote over 4

| Model | Rule | Right | Plain vote | Difference, points [95 %] |
|---|---|---|---|---|
| Think-SFT + cue | fallback_4000 | 240 | 241 | -0.3 [-0.9, +0.0] |
| RL plain | fallback_16000 | 224 | 221 | +0.9 [+0.0, +2.1] |
| base + cue | fallback_12000 | 189 | 192 | -0.9 [-2.7, +0.6] |

## Score = right - lambda x wrong (problems)

| Model | Unit | Right | Wrong | Abstained | lambda 0 | lambda 0.5 | lambda 1 |
|---|---|---|---|---|---|---|---|
| Think-SFT + cue | single_mean_of_4 | 209.0 | 37.5 | 81.5 | 209.0 | 190.2 | 171.5 |
| Think-SFT + cue | vote | 241.0 | 57.0 | 30.0 | 241.0 | 212.5 | 184.0 |
| RL plain | single_mean_of_4 | 200.0 | 119.0 | 9.0 | 200.0 | 140.5 | 81.0 |
| RL plain | vote | 221.0 | 107.0 | 0.0 | 221.0 | 167.5 | 114.0 |
| base + cue | single_mean_of_4 | 158.5 | 103.5 | 66.0 | 158.5 | 106.8 | 55.0 |
| base + cue | vote | 192.0 | 124.0 | 12.0 | 192.0 | 130.0 | 68.0 |
