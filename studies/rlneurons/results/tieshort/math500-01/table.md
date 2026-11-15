# Vote ties to the shortest finished sample, math500, n = 500, stored 16,384 draws, 4 samples, T 1.0 / top-p 1.0, grader v3

Rule: `selector.RULES["tie_short"]`. Differences: rule minus plain vote, problems (points [95 %], paired bootstrap over problems, 5,000 resamples).

| Model | plain vote, stored order | rule, stored order | fixed / broken | difference, stored order | plain vote, 24 orders | rule, 24 orders | difference, 24 orders | rule with lengths shuffled |
|---|---|---|---|---|---|---|---|---|
| Think-SFT + cue | 481 | 481 | 0 / 0 | +0 (+0.0 [+0.0, +0.0]) | 480.8 | 481.0 | +0.25 (+0.1 [-0.3, +0.4]) | 480.9 |
| RL plain | 474 | 475 | 1 / 0 | +1 (+0.2 [+0.0, +0.6]) | 474.3 | 475.0 | +0.67 (+0.1 [-0.3, +0.6]) | 475.1 |
| base + cue | 446 | 453 | 7 / 0 | +7 (+1.4 [+0.4, +2.4]) | 448.2 | 453.0 | +4.75 (+0.9 [+0.1, +1.9]) | 448.5 |

Ties for first in the plain vote (stored order) and right answers inside them:

| Model | ties | lowest sample (plain vote) | shortest (rule) | longest (control) | random, expected | lengths shuffled | shortest tied group right | other tied groups right | ties with no finished tied group | shapes |
|---|---|---|---|---|---|---|---|---|---|---|
| Think-SFT + cue | 6 | 2 | 2 | 2 | 1.8 | 1.9 | 2 of 6 | 2 of 8 | 0 | 2 groups of 1: 2, 2 groups of 2: 3, 4 groups of 1: 1 |
| RL plain | 16 | 3 | 4 | 5 | 3.3 | 4.1 | 4 of 16 | 4 of 39 | 0 | 2 groups of 2: 4, 3 groups of 1: 1, 4 groups of 1: 11 |
| base + cue | 36 | 5 | 12 | 5 | 7.2 | 7.5 | 12 of 36 | 8 of 72 | 0 | 2 groups of 1: 10, 2 groups of 2: 4, 3 groups of 1: 8, 4 groups of 1: 14 |

Sequential vote, stop when two agree, at most 4 (means over the 24 draw orders):

| Model | `seq4` right | `seq4_short` right | difference | tokens per problem | vote over 4 tokens |
|---|---|---|---|---|---|
| Think-SFT + cue | 480.8 | 480.5 | -0.25 (-0.1 [-0.1, +0.0]) | 11,420 | 19,503 |
| RL plain | 474.3 | 474.5 | +0.17 (+0.0 [-0.2, +0.3]) | 11,080 | 18,747 |
| base + cue | 448.2 | 452.0 | +3.75 (+0.8 [-0.1, +1.7]) | 11,256 | 16,034 |

Pooled over hard328 + fresh2026 (n = 464), rule minus plain vote:

| | 24 orders | stored order |
|---|---|---|
| Think-SFT + cue | +0.58 (+0.1 [-0.5, +0.8]) | -1 (-0.2 [-1.1, +0.7]) |
| RL plain | +10.67 (+2.3 [+0.9, +3.7]) | +4 (+0.9 [-0.9, +2.6]) |
| base + cue | +5.08 (+1.1 [-0.2, +2.5]) | -1 (-0.2 [-1.7, +1.3]) |
| think minus rl | -10.08 (-2.2 [-3.8, -0.6]) | -5 (-1.1 [-3.0, +0.9]) |
| think minus base | -4.5 (-1.0 [-2.5, +0.5]) | +0 (+0.0 [-1.7, +1.7]) |
