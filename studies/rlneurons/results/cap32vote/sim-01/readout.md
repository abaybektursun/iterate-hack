# cap32vote simulation: the vote over 4 of Think-SFT + cue at cap 32,768, from stored rows (no model run)

## hard328, n = 328: 378 of 1312 stored samples cut at 16,384

Stored at 16,384: singles [212, 212, 211, 201], vote over 4 = 241 (RL plain vote 221). 63.8 % of its 69 pairs of finished wrong samples agree. Prediction at 32,768 (the two `wrong measured` models pooled): single 229.0 [224.5, 233.2], vote over 4 239.5 [232.0, 248.0].

| model | single, mean of 4 [95 %] | vote over 4 [95 %] | vote gain over 16,384, problems [95 %] |
|---|---|---|---|
| p uniform, wrong distinct | 228.9 [225.2, 233.0] | 256.2 [248.0, 265.0] | 15.2 [7.0, 24.0] |
| p uniform, wrong agree | 228.9 [225.0, 233.8] | 232.6 [226.0, 240.0] | -8.4 [-15.0, -1.0] |
| p uniform, wrong measured | 228.9 [224.2, 233.2] | 238.9 [232.0, 247.0] | -2.1 [-9.0, 6.0] |
| p problem, wrong distinct | 228.8 [225.0, 232.5] | 254.2 [246.0, 262.0] | 13.2 [5.0, 21.0] |
| p problem, wrong agree | 228.9 [225.2, 233.0] | 234.3 [228.0, 241.0] | -6.7 [-13.0, 0.0] |
| p problem, wrong measured | 229.1 [225.2, 233.2] | 240.1 [233.0, 248.0] | -0.9 [-8.0, 7.0] |

| rule | cap | right (stored order) | right (24 orders) | tokens per problem |
|---|---|---|---|---|
| `single` | 16,384 (stored) | 212 | 209.0 | 10,137 |
| `vote2` | 16,384 (stored) | 227 | 221.8 | 20,301 |
| `seq3` | 16,384 (stored) | 241 | 233.2 | 26,269 |
| `seq4` | 16,384 (stored) | 241 | 238.9 | 30,904 |
| `vote4` | 16,384 (stored) | 241 | 238.9 | 40,410 |
| `restart1` | 16,384 (stored) | 230 | 222.0 | 14,330 |
| `single` | 32,768, p uniform, wrong distinct (12 draws) | 230.5 | 228.7 | 11,822 |
| `vote2` | 32,768, p uniform, wrong distinct (12 draws) | 231.2 | 230.1 | 23,777 |
| `seq3` | 32,768, p uniform, wrong distinct (12 draws) | 248.9 | 244.5 | 30,885 |
| `seq4` | 32,768, p uniform, wrong distinct (12 draws) | 256.6 | 254.8 | 35,938 |
| `vote4` | 32,768, p uniform, wrong distinct (12 draws) | 256.7 | 254.8 | 47,527 |
| `single` | 32,768, p uniform, wrong agree (12 draws) | 229.6 | 227.8 | 11,804 |
| `vote2` | 32,768, p uniform, wrong agree (12 draws) | 230.3 | 229.1 | 23,750 |
| `seq3` | 32,768, p uniform, wrong agree (12 draws) | 233.8 | 230.5 | 27,800 |
| `seq4` | 32,768, p uniform, wrong agree (12 draws) | 232.8 | 230.4 | 28,054 |
| `vote4` | 32,768, p uniform, wrong agree (12 draws) | 232.9 | 230.4 | 47,487 |
| `single` | 32,768, p uniform, wrong measured (12 draws) | 230.9 | 228.4 | 11,817 |
| `vote2` | 32,768, p uniform, wrong measured (12 draws) | 231.5 | 229.6 | 23,753 |
| `seq3` | 32,768, p uniform, wrong measured (12 draws) | 238.6 | 235.5 | 29,051 |
| `seq4` | 32,768, p uniform, wrong measured (12 draws) | 238.2 | 236.5 | 30,652 |
| `vote4` | 32,768, p uniform, wrong measured (12 draws) | 237.8 | 236.5 | 47,490 |
| `single` | 32,768, p problem, wrong distinct (12 draws) | 232.6 | 229.4 | 11,807 |
| `vote2` | 32,768, p problem, wrong distinct (12 draws) | 233.2 | 230.6 | 23,756 |
| `seq3` | 32,768, p problem, wrong distinct (12 draws) | 249.2 | 244.4 | 30,597 |
| `seq4` | 32,768, p problem, wrong distinct (12 draws) | 255.6 | 253.3 | 35,525 |
| `vote4` | 32,768, p problem, wrong distinct (12 draws) | 255.6 | 253.3 | 47,495 |
| `single` | 32,768, p problem, wrong agree (12 draws) | 231.7 | 229.5 | 11,812 |
| `vote2` | 32,768, p problem, wrong agree (12 draws) | 232.1 | 230.8 | 23,745 |
| `seq3` | 32,768, p problem, wrong agree (12 draws) | 233.6 | 232.6 | 27,473 |
| `seq4` | 32,768, p problem, wrong agree (12 draws) | 233.7 | 232.9 | 27,684 |
| `vote4` | 32,768, p problem, wrong agree (12 draws) | 234.9 | 232.9 | 47,503 |
| `single` | 32,768, p problem, wrong measured (12 draws) | 234.2 | 229.3 | 11,815 |
| `vote2` | 32,768, p problem, wrong measured (12 draws) | 234.8 | 230.6 | 23,758 |
| `seq3` | 32,768, p problem, wrong measured (12 draws) | 241.2 | 236.7 | 28,700 |
| `seq4` | 32,768, p problem, wrong measured (12 draws) | 240.8 | 238.2 | 30,260 |
| `vote4` | 32,768, p problem, wrong measured (12 draws) | 241.2 | 238.2 | 47,509 |

## fresh2026, n = 136: 248 of 544 stored samples cut at 16,384

Stored at 16,384: singles [65, 59, 56, 60], vote over 4 = 75 (RL plain vote 57). 75.0 % of its 36 pairs of finished wrong samples agree. Prediction at 32,768 (the two `wrong measured` models pooled): single 74.5 [71.2, 78.0], vote over 4 77.0 [71.0, 83.0].

| model | single, mean of 4 [95 %] | vote over 4 [95 %] | vote gain over 16,384, problems [95 %] |
|---|---|---|---|
| p uniform, wrong distinct | 74.8 [71.5, 78.8] | 90.1 [84.0, 96.0] | 15.1 [9.0, 21.0] |
| p uniform, wrong agree | 74.8 [71.5, 78.0] | 74.4 [69.0, 80.0] | -0.6 [-6.0, 5.0] |
| p uniform, wrong measured | 74.9 [71.5, 78.2] | 77.2 [72.0, 83.0] | 2.2 [-3.0, 8.0] |
| p problem, wrong distinct | 74.2 [71.2, 77.5] | 87.4 [81.0, 93.0] | 12.4 [6.0, 18.0] |
| p problem, wrong agree | 74.3 [71.2, 77.8] | 74.7 [70.0, 80.0] | -0.3 [-5.0, 5.0] |
| p problem, wrong measured | 74.1 [71.0, 77.2] | 76.8 [71.0, 83.0] | 1.8 [-4.0, 8.0] |

| rule | cap | right (stored order) | right (24 orders) | tokens per problem |
|---|---|---|---|---|
| `single` | 16,384 (stored) | 65 | 60.0 | 12,876 |
| `vote2` | 16,384 (stored) | 69 | 68.1 | 25,999 |
| `seq3` | 16,384 (stored) | 71 | 72.5 | 34,718 |
| `seq4` | 16,384 (stored) | 75 | 75.5 | 42,251 |
| `vote4` | 16,384 (stored) | 75 | 75.5 | 52,170 |
| `restart1` | 16,384 (stored) | 69 | 68.0 | 19,944 |
| `single` | 32,768, p uniform, wrong distinct (12 draws) | 78.4 | 74.3 | 15,641 |
| `vote2` | 32,768, p uniform, wrong distinct (12 draws) | 78.9 | 74.8 | 31,461 |
| `seq3` | 32,768, p uniform, wrong distinct (12 draws) | 82.9 | 81.4 | 42,324 |
| `seq4` | 32,768, p uniform, wrong distinct (12 draws) | 87.9 | 88.0 | 50,862 |
| `vote4` | 32,768, p uniform, wrong distinct (12 draws) | 87.9 | 88.0 | 63,462 |
| `single` | 32,768, p uniform, wrong agree (12 draws) | 79.7 | 75.7 | 15,654 |
| `vote2` | 32,768, p uniform, wrong agree (12 draws) | 80.1 | 76.1 | 31,416 |
| `seq3` | 32,768, p uniform, wrong agree (12 draws) | 76.1 | 74.5 | 36,921 |
| `seq4` | 32,768, p uniform, wrong agree (12 draws) | 74.5 | 74.1 | 37,382 |
| `vote4` | 32,768, p uniform, wrong agree (12 draws) | 75.6 | 74.1 | 63,385 |
| `single` | 32,768, p uniform, wrong measured (12 draws) | 79.7 | 74.9 | 15,609 |
| `vote2` | 32,768, p uniform, wrong measured (12 draws) | 79.8 | 75.3 | 31,390 |
| `seq3` | 32,768, p uniform, wrong measured (12 draws) | 78.1 | 75.7 | 38,279 |
| `seq4` | 32,768, p uniform, wrong measured (12 draws) | 77.0 | 75.5 | 40,239 |
| `vote4` | 32,768, p uniform, wrong measured (12 draws) | 77.3 | 75.5 | 63,315 |
| `single` | 32,768, p problem, wrong distinct (12 draws) | 78.0 | 74.1 | 15,660 |
| `vote2` | 32,768, p problem, wrong distinct (12 draws) | 78.2 | 74.5 | 31,441 |
| `seq3` | 32,768, p problem, wrong distinct (12 draws) | 82.4 | 81.1 | 41,873 |
| `seq4` | 32,768, p problem, wrong distinct (12 draws) | 87.6 | 86.9 | 50,330 |
| `vote4` | 32,768, p problem, wrong distinct (12 draws) | 87.6 | 86.9 | 63,411 |
| `single` | 32,768, p problem, wrong agree (12 draws) | 77.3 | 74.7 | 15,673 |
| `vote2` | 32,768, p problem, wrong agree (12 draws) | 77.6 | 75.0 | 31,460 |
| `seq3` | 32,768, p problem, wrong agree (12 draws) | 73.4 | 74.0 | 36,117 |
| `seq4` | 32,768, p problem, wrong agree (12 draws) | 73.1 | 73.5 | 36,413 |
| `vote4` | 32,768, p problem, wrong agree (12 draws) | 74.3 | 73.5 | 63,411 |
| `single` | 32,768, p problem, wrong measured (12 draws) | 78.5 | 74.1 | 15,635 |
| `vote2` | 32,768, p problem, wrong measured (12 draws) | 78.8 | 74.6 | 31,492 |
| `seq3` | 32,768, p problem, wrong measured (12 draws) | 75.9 | 76.0 | 38,217 |
| `seq4` | 32,768, p problem, wrong measured (12 draws) | 76.6 | 76.2 | 39,734 |
| `vote4` | 32,768, p problem, wrong measured (12 draws) | 77.2 | 76.2 | 63,385 |
