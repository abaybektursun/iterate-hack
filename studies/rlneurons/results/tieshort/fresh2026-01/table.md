# Vote ties to the shortest finished sample, fresh2026, n = 136, stored 16,384 draws, 4 samples, T 1.0 / top-p 1.0, grader v3

Rule: `selector.RULES["tie_short"]`. Differences: rule minus plain vote, problems (points [95 %], paired bootstrap over problems, 5,000 resamples).

| Model | plain vote, stored order | rule, stored order | fixed / broken | difference, stored order | plain vote, 24 orders | rule, 24 orders | difference, 24 orders | rule with lengths shuffled |
|---|---|---|---|---|---|---|---|---|
| Think-SFT + cue | 75 | 76 | 1 / 0 | +1 (+0.7 [+0.0, +2.2]) | 75.5 | 76.0 | +0.5 (+0.4 [-0.7, +1.8]) | 76.0 |
| RL plain | 57 | 60 | 4 / 1 | +3 (+2.2 [-0.7, +5.9]) | 55.8 | 60.3 | +4.58 (+3.4 [+0.7, +6.4]) | 56.8 |
| base + cue | 38 | 38 | 2 / 2 | +0 (+0.0 [-2.9, +2.9]) | 38.8 | 38.0 | -0.83 (-0.6 [-2.8, +1.6]) | 39.4 |

Ties for first in the plain vote (stored order) and right answers inside them:

| Model | ties | lowest sample (plain vote) | shortest (rule) | longest (control) | random, expected | lengths shuffled | shortest tied group right | other tied groups right | ties with no finished tied group | shapes |
|---|---|---|---|---|---|---|---|---|---|---|
| Think-SFT + cue | 6 | 1 | 2 | 2 | 1.5 | 2.0 | 2 of 6 | 1 of 6 | 0 | 2 groups of 1: 6 |
| RL plain | 42 | 4 | 7 | 2 | 2.8 | 3.8 | 7 of 38 | 2 of 98 | 4 | 2 groups of 1: 2, 2 groups of 2: 3, 3 groups of 1: 10, 4 groups of 1: 27 |
| base + cue | 46 | 3 | 3 | 7 | 3.8 | 4.4 | 3 of 45 | 8 of 84 | 1 | 2 groups of 1: 20, 3 groups of 1: 13, 4 groups of 1: 13 |

Sequential vote, stop when two agree, at most 4 (means over the 24 draw orders):

| Model | `seq4` right | `seq4_short` right | difference | tokens per problem | vote over 4 tokens |
|---|---|---|---|---|---|
| Think-SFT + cue | 75.5 | 76.0 | +0.5 (+0.4 [-0.7, +1.8]) | 42,901 | 52,170 |
| RL plain | 55.8 | 60.3 | +4.58 (+3.4 [+0.7, +6.4]) | 38,151 | 48,331 |
| base + cue | 38.8 | 38.0 | -0.83 (-0.6 [-2.8, +1.6]) | 46,617 | 51,158 |

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
| 32768 | 75 | 81 | 36 | 2 | 8 | 2.8 | 8 of 36 | 1 of 99 |
| 16384 | 73 | 75 | 16 | 3 | 5 | 2.2 | 5 of 10 | 0 of 12 |
