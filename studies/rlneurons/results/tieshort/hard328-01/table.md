# Vote ties to the shortest finished sample, hard328, n = 328, stored 16,384 draws, 4 samples, T 1.0 / top-p 1.0, grader v3

Rule: `selector.RULES["tie_short"]`. Differences: rule minus plain vote, problems (points [95 %], paired bootstrap over problems, 5,000 resamples).

| Model | plain vote, stored order | rule, stored order | fixed / broken | difference, stored order | plain vote, 24 orders | rule, 24 orders | difference, 24 orders | rule with lengths shuffled |
|---|---|---|---|---|---|---|---|---|
| Think-SFT + cue | 241 | 239 | 1 / 3 | -2 (-0.6 [-1.8, +0.6]) | 238.9 | 239.0 | +0.08 (+0.0 [-0.8, +0.8]) | 238.4 |
| RL plain | 221 | 222 | 6 / 5 | +1 (+0.3 [-1.5, +2.1]) | 215.9 | 222.0 | +6.08 (+1.9 [+0.3, +3.5]) | 217.0 |
| base + cue | 192 | 191 | 4 / 5 | -1 (-0.3 [-2.1, +1.5]) | 184.6 | 190.5 | +5.92 (+1.8 [+0.3, +3.5]) | 186.0 |

Ties for first in the plain vote (stored order) and right answers inside them:

| Model | ties | lowest sample (plain vote) | shortest (rule) | longest (control) | random, expected | lengths shuffled | shortest tied group right | other tied groups right | ties with no finished tied group | shapes |
|---|---|---|---|---|---|---|---|---|---|---|
| Think-SFT + cue | 16 | 5 | 3 | 2 | 2.9 | 2.4 | 3 of 14 | 4 of 21 | 2 | 2 groups of 1: 9, 2 groups of 2: 2, 3 groups of 1: 3, 4 groups of 1: 2 |
| RL plain | 64 | 12 | 13 | 7 | 6.9 | 8.0 | 13 of 63 | 9 of 146 | 1 | 2 groups of 1: 6, 2 groups of 2: 10, 3 groups of 1: 13, 4 groups of 1: 35 |
| base + cue | 85 | 17 | 16 | 6 | 9.6 | 11.0 | 15 of 84 | 10 of 153 | 1 | 2 groups of 1: 32, 2 groups of 2: 5, 3 groups of 1: 27, 4 groups of 1: 21 |

Sequential vote, stop when two agree, at most 4 (means over the 24 draw orders):

| Model | `seq4` right | `seq4_short` right | difference | tokens per problem | vote over 4 tokens |
|---|---|---|---|---|---|
| Think-SFT + cue | 238.9 | 239.5 | +0.58 (+0.2 [-0.5, +1.0]) | 30,837 | 40,410 |
| RL plain | 215.9 | 222.0 | +6.08 (+1.9 [+0.5, +3.4]) | 26,680 | 37,299 |
| base + cue | 184.6 | 190.5 | +5.92 (+1.8 [+0.4, +3.4]) | 31,510 | 36,902 |

Pooled over hard328 + fresh2026 (n = 464), rule minus plain vote:

| | 24 orders | stored order |
|---|---|---|
| Think-SFT + cue | +0.58 (+0.1 [-0.5, +0.8]) | -1 (-0.2 [-1.1, +0.7]) |
| RL plain | +10.67 (+2.3 [+0.9, +3.7]) | +4 (+0.9 [-0.9, +2.6]) |
| base + cue | +5.08 (+1.1 [-0.2, +2.5]) | -1 (-0.2 [-1.7, +1.3]) |
| think minus rl | -10.08 (-2.2 [-3.8, -0.6]) | -5 (-1.1 [-3.0, +0.9]) |
| think minus base | -4.5 (-1.0 [-2.5, +0.5]) | +0 (+0.0 [-1.7, +1.7]) |

The post hoc lead (result-dd26fe), reproduced from `results/cap32vote/` rows (Think-SFT + cue, other draws of the same problems):

| view | plain vote | rule | ties | lowest sample right | shortest right | random, expected | shortest tied group right | other tied groups right |
|---|---|---|---|---|---|---|---|---|
| 32768 | 244 | 252 | 34 | 4 | 12 | 5.2 | 12 of 34 | 3 of 86 |
| 16384 | 238 | 246 | 22 | 4 | 12 | 5.8 | 12 of 21 | 1 of 28 |
