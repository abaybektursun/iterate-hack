# Vote over 4 as the expectation over the tie-break, math500, n = 500, T 1.0 / top-p 1.0, grader v3

Posted = `day1_vote.vote` in the stored sample order (a tie goes to the group seen first). Order mean, min, max = over the 24 orders of the 4 samples. Expected = `selector.tie_random` (uniformly random choice among the largest groups). Ties = problems with a tie for first, stored order.

| Vote | posted (stored order) | order mean | expected, random tie-break | min to max over orders | ties | ties right: stored, expected, min to max |
|---|---|---|---|---|---|---|
| base + cue | 446 | 448.2 | 448.2 | 446 to 450 | 36 | 5, 7.2, 5 to 9 |
| RL plain | 474 | 474.3 | 474.3 | 474 to 475 | 16 | 3, 3.3, 3 to 4 |
| Think-SFT + cue | 481 | 480.8 | 480.8 | 480 to 482 | 6 | 2, 1.8, 1 to 3 |
| RL plain, vote after restart | 475 | 476.1 | 476.1 | 475 to 477 | 14 | 2, 3.1, 2 to 4 |
| base + cue, vote after restart | 450 | 452.1 | 452.1 | 450 to 456 | 37 | 6, 8.1, 6 to 12 |

Contrasts in points [95 %], paired bootstrap over problems, 5,000 resamples, the posted resamples; order-averaged = on the per-problem expected scores.

| Contrast | posted in | stored order (as posted) | order-averaged | change | more than the posted half-width | conclusion flips |
|---|---|---|---|---|---|---|
| Think-SFT + cue minus RL plain | result-818c20 | +1.4 [-0.4, +3.2] | +1.3 [-0.3, +2.9] | -0.1 | no (1.8) | no |
| RL plain minus base + cue | README Day-1 #3 | +5.6 [+3.6, +7.8] | +5.2 [+3.4, +7.2] | -0.4 | no (2.1) | no |
| Think-SFT + cue minus base + cue |  | +7.0 [+4.8, +9.4] | +6.5 [+4.4, +8.8] | -0.5 | no (2.3) | no |
| RL plain, vote after restart minus base + cue, vote after restart |  | +5.0 [+3.0, +7.0] | +4.8 [+3.1, +6.6] | -0.2 | no (2.0) | no |
