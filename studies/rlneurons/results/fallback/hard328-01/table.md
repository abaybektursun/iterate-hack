# Late answers as fallback votes, hard328, n = 328: Think-SFT + cue, 4 samples, cap 32,768 (development set; chosen: R2)

Right: mean over the 24 draw orders; stored order next to it. Differences: problems (points [95 %]), paired bootstrap over problems, 5,000 resamples.

| rule | right, 24 orders | right, stored order | minus plain 32,768 vote, 24 orders | minus 16,384-cut vote, 24 orders | stored order, against plain: fixed / broken |
|---|---|---|---|---|---|
| `R1` fallback: the 16,384 vote; late answers only when it has no ballot | 244.8 | 243 | -0.5 (-0.1 [-2.3, +1.9]) | +5.0 (+1.5 [+0.5, +2.8]) | 9 / 10 |
| `R2` late answers count half a vote | 249.8 | 249 | +4.5 (+1.4 [+0.4, +2.5]) | +10.0 (+3.0 [+1.1, +5.1]) | 6 / 1 |
| `R3` fallback, late answers that switched script before 16,384 dropped | 245.2 | 244 | +0.0 (+0.0 [-2.1, +2.1]) | +5.5 (+1.7 [+0.5, +3.0]) | 10 / 10 |
| `R4` control: plain vote at 32,768 | 245.2 | 244 |  |  |  |
| `R5` control: vote over the answers cut at 16,384 | 239.8 | 238 |  |  |  |
| `R6` planted control: fallback with the late flags permuted inside the problem | 241.0 |  | -4.2 (-1.3 [-2.3, -0.3]) |  |  |

Power on fresh2026 (136 problems drawn from these 328, 2,000 draws): {"n": 136, "draws": 2000, "minus_plain_32768": 0.428, "minus_cut_16384": 0.546, "both": 0.191}

## H2: late answers by a script switch before token 16,384

| late answers | switched: right | not switched: right | problems with both kinds | within problem, points [95 %] | flags permuted inside problems |
|---|---|---|---|---|---|
| 368 | 20 of 119 | 79 of 249 | 60 | -12.2 [-22.2, -3.1] | 0.6 |

## H3: early and late finished answers

| | count | right |
|---|---|---|
| early finished answers | 944 | 832 |
| late finished answers | 362 | 96 |
| late finished ballot, problem has a 16,384 ballot | 192 | |
| - agrees with a 16,384 ballot | 87 | 51 |
| - disagrees with every 16,384 ballot | 105 | late right 13; a 16,384 ballot right 46; none right 46 |
| late finished ballot, problem has no 16,384 ballot (30 problems) | 118 | 17 |

## Sequential rules (generated tokens per problem)

| rule | right, 24 orders | tokens, 24 orders | right, stored order | tokens, stored order |
|---|---|---|---|---|
| `single_32` | 232.8 | 11,650 | 230 | 11,795 |
| `seq4_16` | 239.8 | 30,807 | 237 | 30,730 |
| `seq4_32` | 245.2 | 31,732 | 244 | 32,032 |
| `seqfb_resume` | 244.8 | 33,118 | 242 | 33,040 |
| `seqfb_online` | 244.8 | 34,863 | 242 | 34,828 |
| `seq4_half` | 249.8 | 36,659 | 249 | 36,659 |

- seqfb_resume minus seq4_32: -0.5 (-0.1 [-2.3, +1.9])
- seqfb_resume minus seq4_16: +5.0 (+1.5 [+0.5, +2.8])
- seqfb_online minus seq4_32: -0.5 (-0.1 [-2.3, +1.9])
- seqfb_online minus seq4_16: +5.0 (+1.5 [+0.5, +2.8])
- seq4_half minus seq4_32: +4.5 (+1.4 [+0.4, +2.5])
- seq4_half minus seq4_16: +10.0 (+3.0 [+1.1, +5.1])
