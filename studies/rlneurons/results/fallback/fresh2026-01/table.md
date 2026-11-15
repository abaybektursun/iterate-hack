# Late answers as fallback votes, fresh2026, n = 136: Think-SFT + cue, 4 samples, cap 32,768 (rule fixed on hard328: R2)

Right: mean over the 24 draw orders; stored order next to it. Differences: problems (points [95 %]), paired bootstrap over problems, 5,000 resamples.

| rule | right, 24 orders | right, stored order | minus plain 32,768 vote, 24 orders | minus 16,384-cut vote, 24 orders | stored order, against plain: fixed / broken |
|---|---|---|---|---|---|
| `R2` late answers count half a vote | 77.8 | 77 | +2.0 (+1.5 [+0.0, +3.4]) | +5.6 (+4.1 [+0.8, +7.8]) | 2 / 0 |
| `R4` control: plain vote at 32,768 | 75.8 | 75 |  |  |  |
| `R5` control: vote over the answers cut at 16,384 | 72.2 | 73 |  |  |  |
| `R6` planted control: fallback with the late flags permuted inside the problem | 73.9 |  | -1.9 (-1.4 [-3.0, +0.1]) |  |  |

H1: {"rule": "R2", "held": false, "power_stated_before_scoring": {"n": 136, "draws": 2000, "minus_plain_32768": 0.428, "minus_cut_16384": 0.546, "both": 0.191}}

Pooled with the development set (descriptive only): {"n": 464, "R2 minus R4, 24 orders": {"problems": 6.5, "points": 1.4, "interval95": [0.57, 2.33]}, "R2 minus R5, 24 orders": {"problems": 15.58, "points": 3.36, "interval95": [1.65, 5.14]}}

## H2: late answers by a script switch before token 16,384

| late answers | switched: right | not switched: right | problems with both kinds | within problem, points [95 %] | flags permuted inside problems |
|---|---|---|---|---|---|
| 260 | 12 of 82 | 38 of 178 | 39 | -0.4 [-14.1, 12.8] | -0.8 |

## H3: early and late finished answers

| | count | right |
|---|---|---|
| early finished answers | 284 | 231 |
| late finished answers | 259 | 50 |
| late finished ballot, problem has a 16,384 ballot | 136 | |
| - agrees with a 16,384 ballot | 45 | 23 |
| - disagrees with every 16,384 ballot | 91 | late right 4; a 16,384 ballot right 29; none right 58 |
| late finished ballot, problem has no 16,384 ballot (21 problems) | 82 | 14 |

## Sequential rules (generated tokens per problem)

| rule | right, 24 orders | tokens, 24 orders | right, stored order | tokens, stored order |
|---|---|---|---|---|
| `single_32` | 70.2 | 15,900 | 69 | 16,210 |
| `seq4_16` | 72.2 | 43,509 | 73 | 44,221 |
| `seq4_32` | 75.8 | 47,519 | 75 | 48,359 |
| `seqfb_resume` | 76.7 | 47,017 | 78 | 47,674 |
| `seqfb_online` | 76.7 | 50,309 | 78 | 51,393 |
| `seq4_half` | 77.8 | 53,980 | 77 | 54,652 |

- seqfb_resume minus seq4_32: +0.9 (+0.7 [-1.9, +3.6])
- seqfb_resume minus seq4_16: +4.5 (+3.3 [+0.7, +6.6])
- seqfb_online minus seq4_32: +0.9 (+0.7 [-1.9, +3.6])
- seqfb_online minus seq4_16: +4.5 (+3.3 [+0.7, +6.6])
- seq4_half minus seq4_32: +2.0 (+1.5 [+0.0, +3.4])
- seq4_half minus seq4_16: +5.6 (+4.1 [+0.8, +7.8])
