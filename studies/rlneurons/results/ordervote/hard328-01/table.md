# Vote over 4 as the expectation over the tie-break, hard328, n = 328, T 1.0 / top-p 1.0, grader v3

Posted = `day1_vote.vote` in the stored sample order (a tie goes to the group seen first). Order mean, min, max = over the 24 orders of the 4 samples. Expected = `selector.tie_random` (uniformly random choice among the largest groups). Ties = problems with a tie for first, stored order.

| Vote | posted (stored order) | order mean | expected, random tie-break | min to max over orders | ties | ties right: stored, expected, min to max |
|---|---|---|---|---|---|---|
| base + cue | 192 | 184.6 | 184.6 | 180 to 192 | 85 | 17, 9.6, 5 to 17 |
| RL plain | 221 | 215.9 | 215.9 | 211 to 222 | 64 | 12, 6.9, 2 to 13 |
| Think-SFT + cue | 241 | 238.9 | 238.9 | 237 to 241 | 16 | 5, 2.9, 1 to 5 |
| base + 1.5 x top-8 RL directions + cue | 214 | 216.2 | 216.2 | 214 to 218 | 55 | 3, 5.2, 3 to 7 |
| RL plain, vote after restart | 224 | 218.2 | 218.2 | 215 to 224 | 54 | 11, 5.2, 2 to 11 |
| base + cue, vote after restart | 195 | 190.8 | 190.8 | 185 to 195 | 90 | 14, 9.8, 4 to 14 |
| Think-SFT + cue, cap 32,768 | 244 | 245.2 | 245.2 | 244 to 248 | 34 | 4, 5.2, 4 to 8 |
| Think-SFT + cue, the same answers cut at 16,384 | 238 | 239.8 | 239.8 | 237 to 243 | 22 | 4, 5.8, 3 to 9 |
| mixed vote, 2rl+2think (mean over combinations) | 228.1 |  | 227.4 | 214 to 237 (first-seen ties, over combinations and rotations) | 66.4 |  |
| mixed vote, 2rl+2base (mean over combinations) | 207.6 |  | 206.6 | 193 to 221 (first-seen ties, over combinations and rotations) | 82.6 |  |
| mixed vote, 2think+2base (mean over combinations) | 220.8 |  | 220.6 | 210 to 233 (first-seen ties, over combinations and rotations) | 53.3 |  |
| mixed vote, 4rl+4think (mean over combinations) | 239 |  | 237.8 | 238 to 240 (first-seen ties, over combinations and rotations) | 35 |  |
| mixed vote, 4think+4base (mean over combinations) | 238 |  | 235.4 | 237 to 239 (first-seen ties, over combinations and rotations) | 53 |  |

Contrasts in points [95 %], paired bootstrap over problems, 5,000 resamples, the posted resamples; order-averaged = on the per-problem expected scores.

| Contrast | posted in | stored order (as posted) | order-averaged | change | more than the posted half-width | conclusion flips |
|---|---|---|---|---|---|---|
| Think-SFT + cue minus RL plain | result-818c20 | +6.1 [+3.0, +9.5] | +7.0 [+3.9, +10.2] | +0.9 | no (3.2) | no |
| RL plain minus base + cue | result-5c961a | +8.8 [+5.2, +12.8] | +9.6 [+6.3, +13.0] | +0.7 | no (3.8) | no |
| Think-SFT + cue minus base + cue |  | +14.9 [+10.7, +19.5] | +16.6 [+12.5, +20.8] | +1.6 | no (4.4) | no |
| RL plain, vote after restart minus base + cue, vote after restart | result-5c961a | +8.8 [+5.5, +12.5] | +8.4 [+5.2, +11.6] | -0.5 | no (3.5) | no |
| mix|2rl+2think minus RL plain | result-0033d7 | +2.2 [+0.3, +4.2] | +3.5 [+1.9, +5.2] | +1.3 | no (1.9) | no |
| mix|2rl+2think minus Think-SFT + cue | result-0033d7 | -3.9 [-6.2, -1.8] | -3.5 [-5.5, -1.5] | +0.4 | no (2.2) | no |
| base + 1.5 x top-8 RL directions + cue minus RL plain | result-95a4dc | -2.1 [-5.2, +0.6] | +0.1 [-2.3, +2.4] | +2.2 | no (2.9) | no |
| base + 1.5 x top-8 RL directions + cue minus base + cue | result-95a4dc | +6.7 [+3.4, +10.4] | +9.7 [+6.5, +13.1] | +2.9 | no (3.5) | no |
| Think-SFT + cue, cap 32,768 minus Think-SFT + cue, the same answers cut at 16,384 | result-dd26fe | +1.8 [-0.9, +4.9] | +1.7 [-0.6, +4.1] | -0.2 | no (2.9) | no |
| Think-SFT + cue, the same answers cut at 16,384 minus RL plain | result-dd26fe audit, same cap | +5.2 [+1.8, +8.5] | +7.3 [+4.3, +10.2] | +2.1 | no (3.4) | no |
| Think-SFT + cue, cap 32,768 minus RL plain | result-dd26fe, unequal caps | +7.0 [+3.7, +10.4] | +8.9 [+5.9, +12.1] | +1.9 | no (3.4) | no |

Share of the base-to-RL gap closed under the vote, % [95 %] (interval of the ratio; denominators: stored 221 - 192, order-averaged 215.9 - 184.6):

| Row of the configuration table | right, posted | right, order-averaged | share, posted | share, order-averaged | change | more than the posted half-width | reward-trained weights |
|---|---|---|---|---|---|---|---|
| base + cue, vote over 4 | 192 | 184.6 | 0 [0, 0] | 0 [0, 0] | +0 | no (0) | no |
| base + cue, vote over 4 after restart | 195 | 190.8 | 10 [-8, 29] | 20 [6, 36] | +9 | no (19) | no |
| base + cue, vote over 4, ties to the shortest | 191 | 190.5 | -3 [-29, 17] | 19 [3, 38] | +22 | no (23) | no |
| base + cue, vote over 4 after restart, ties to the shortest | 199 | 199 | 24 [0, 50] | 46 [24, 73] | +22 | no (25) | no |
| base + cue, sequential vote, at most 3 (mean of 24 orders) | 178.8 | 178.8 | -46 [-98, -21] | -19 [-37, -8] | +27 | no (38) | no |
| base + cue, sequential vote, at most 4, restarts (mean of 24 orders) | 190.8 | 190.8 | -4 [-33, 14] | 20 [6, 36] | +24 | yes (23) | no |
| base + cue, sequential vote, at most 4, restarts, ties to the shortest (mean of 24 orders) | 198.5 | 198.5 | 22 [-2, 47] | 44 [24, 71] | +22 | no (24) | no |
| RL plain, vote over 4 | 221 | 215.9 | 100 [100, 100] | 100 [100, 100] | -0 | yes (0) | yes |
| RL plain, vote over 4 after restart | 224 | 218.2 | 110 [92, 140] | 107 [94, 127] | -3 | no (24) | yes |
| RL plain, vote over 4, ties to the shortest | 222 | 222 | 103 [82, 132] | 119 [103, 143] | +16 | no (25) | yes |
| RL plain, vote over 4 after restart, ties to the shortest | 220 | 220 | 97 [74, 126] | 113 [94, 140] | +16 | no (26) | yes |
| RL plain, sequential vote, at most 3 (mean of 24 orders) | 212.7 | 212.7 | 71 [52, 88] | 90 [82, 97] | +18 | yes (18) | yes |
| RL plain, sequential vote, at most 4, restarts (mean of 24 orders) | 218.2 | 218.2 | 91 [69, 118] | 107 [94, 127] | +17 | no (25) | yes |
| RL plain, sequential vote, at most 4, restarts, ties to the shortest (mean of 24 orders) | 220.5 | 220.5 | 98 [77, 126] | 115 [98, 140] | +16 | no (24) | yes |
| Think-SFT + cue, vote over 4 | 241 | 238.9 | 169 [128, 250] | 173 [137, 238] | +4 | no (61) | no |
| Think-SFT + cue, vote over 4, ties to the shortest | 239 | 239 | 162 [122, 242] | 174 [137, 240] | +12 | no (60) | no |
| Think-SFT + cue, vote over 4 after restart, ties to the shortest (no restart rows: restart = none) | 239 | 239 | 162 [122, 242] | 174 [137, 240] | +12 | no (60) | no |
| Think-SFT + cue, sequential vote, at most 3 (mean of 24 orders) | 233.2 | 233.2 | 142 [107, 208] | 155 [122, 210] | +13 | no (50) | no |
| Think-SFT + cue, sequential vote, at most 4, restarts (mean of 24 orders) (no restart rows: restart = none) | 238.9 | 238.9 | 162 [122, 239] | 173 [137, 238] | +12 | no (58) | no |
| Think-SFT + cue, sequential vote, at most 4, restarts, ties to the shortest (mean of 24 orders) (no restart rows: restart = none) | 239.5 | 239.5 | 164 [124, 244] | 175 [139, 241] | +11 | no (60) | no |
| mixed vote, 2 RL plain + 2 Think-SFT + cue (mean over combinations) | 228.1 | 227.4 | 124 [103, 167] | 137 [117, 172] | +12 | no (32) | partly |
| mixed vote, 2 RL plain + 2 base + cue (mean over combinations) | 207.6 | 206.6 | 54 [37, 68] | 70 [61, 81] | +17 | yes (15) | partly |
| mixed vote, 2 Think-SFT + cue + 2 base + cue (mean over combinations) | 220.8 | 220.6 | 99 [75, 143] | 115 [91, 155] | +15 | no (34) | no |
| mixed vote, 4 RL plain + 4 Think-SFT + cue (mean over combinations) | 239 | 237.8 | 162 [131, 230] | 170 [141, 222] | +8 | no (50) | partly |
| mixed vote, 4 Think-SFT + cue + 4 base + cue (mean over combinations) | 238 | 235.4 | 159 [120, 237] | 162 [128, 225] | +4 | no (59) | no |
| base + 1.5 x top-8 RL directions + cue, vote over 4 new draws | 214 | 216.2 | 76 [45, 110] | 101 [78, 130] | +25 | no (33) | partly (RL-derived directions) |
