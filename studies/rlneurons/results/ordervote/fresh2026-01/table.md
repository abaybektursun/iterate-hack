# Vote over 4 as the expectation over the tie-break, fresh2026, n = 136, T 1.0 / top-p 1.0, grader v3

Posted = `day1_vote.vote` in the stored sample order (a tie goes to the group seen first). Order mean, min, max = over the 24 orders of the 4 samples. Expected = `selector.tie_random` (uniformly random choice among the largest groups). Ties = problems with a tie for first, stored order.

| Vote | posted (stored order) | order mean | expected, random tie-break | min to max over orders | ties | ties right: stored, expected, min to max |
|---|---|---|---|---|---|---|
| Think-SFT + cue | 75 | 75.5 | 75.5 | 74 to 77 | 6 | 1, 1.5, 0 to 3 |
| RL plain | 57 | 55.8 | 55.8 | 55 to 57 | 42 | 4, 2.8, 2 to 4 |
| base + cue | 38 | 38.8 | 38.8 | 35 to 43 | 46 | 3, 3.8, 0 to 8 |
| Think-SFT + cue, cap 32,768 | 75 | 75.8 | 75.8 | 73 to 78 | 36 | 2, 2.8, 0 to 5 |
| Think-SFT + cue, the same answers cut at 16,384 | 73 | 72.2 | 72.2 | 70 to 74 | 16 | 3, 2.2, 0 to 4 |

Contrasts in points [95 %], paired bootstrap over problems, 5,000 resamples, the posted resamples; order-averaged = on the per-problem expected scores.

| Contrast | posted in | stored order (as posted) | order-averaged | change | more than the posted half-width | conclusion flips |
|---|---|---|---|---|---|---|
| Think-SFT + cue minus RL plain | result-5251c9 | +13.2 [+7.4, +19.1] | +14.5 [+8.5, +20.6] | +1.3 | no (5.9) | no |
| Think-SFT + cue minus base + cue | result-5251c9 | +27.2 [+19.9, +35.3] | +27.0 [+20.0, +34.4] | -0.2 | no (7.7) | no |
| RL plain minus base + cue | result-5251c9 | +14.0 [+8.1, +19.9] | +12.4 [+7.5, +17.9] | -1.5 | no (5.9) | no |
| Think-SFT + cue, cap 32,768 minus Think-SFT + cue, the same answers cut at 16,384 | result-dd26fe | +1.5 [-2.9, +5.9] | +2.6 [-1.3, +6.6] | +1.2 | no (4.4) | no |
| Think-SFT + cue, the same answers cut at 16,384 minus RL plain | result-dd26fe audit, same cap | +11.8 [+5.1, +18.4] | +12.1 [+5.7, +18.4] | +0.3 | no (6.6) | no |
| Think-SFT + cue, cap 32,768 minus RL plain | result-dd26fe, unequal caps | +13.2 [+6.6, +19.9] | +14.7 [+8.8, +21.0] | +1.5 | no (6.6) | no |
