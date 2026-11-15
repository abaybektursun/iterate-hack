# Token frontier, hard328, n = 328, T 1.0 / top-p 1.0, grader v3

Right: stored draw order. Right (24): mean over the 24 draw orders. Tokens: generated tokens per problem, stored order.

| Configuration | Model | Right | Percent [95 %] | Right (24) | Tokens per problem | Training signal |
|---|---|---|---|---|---|---|
| one sample (`single`) | base + cue | 161 | 49.1 [43.7, 54.5] | 158.5 | 9,074 | none |
| one sample, sampled again after a cap hit (up to 2 times) (`restart`) | base + cue | 172 | 52.4 [47.0, 57.8] | 167.0 | 13,665 | none |
| vote over 2, ties to the shortest finished sample (`vote2_short`) | base + cue | 170 | 51.8 [46.4, 57.2] | 169.8 | 18,316 | none |
| one sample, abandoned at 8,000 tokens and drawn again (`R8000`) | base + cue | 163 | 49.7 [44.3, 55.1] | 162.0 | 18,937 | none |
| one sample, abandoned at 12,000 tokens and drawn again (`R12000`) | base + cue | 170 | 51.8 [46.4, 57.2] | 168.9 | 19,713 | none |
| sequential vote: stop when two agree, at most 3 samples (`seq3`) | base + cue | 183 | 55.8 [50.4, 61.1] | 178.8 | 25,601 | none |
| draw 2; if they differ draw 2 more; vote, ties to the shortest (`seq_2then4_short`) | base + cue | 191 | 58.2 [52.8, 63.4] | 190.5 | 32,776 | none |
| sequential vote, at most 4, each sample restarted after a cap hit (`seq4_restart`) | base + cue | 194 | 59.1 [53.8, 64.3] | 190.8 | 46,317 | none |
| sequential vote, at most 4, restarts, ties to the shortest (`seq4_restart_short`) | base + cue | 198 | 60.4 [55.0, 65.5] | 198.5 | 46,317 | none |
| vote over 4 after restart, ties to the shortest (`vote4_restart_short`) | base + cue | 199 | 60.7 [55.3, 65.8] | 199.0 | 55,306 | none |
| one sample (`single`) | RL plain | 207 | 63.1 [57.8, 68.2] | 200.0 | 9,437 | RL reward (weights) |
| one sample, sampled again after a cap hit (up to 2 times) (`restart`) | RL plain | 213 | 64.9 [59.6, 69.9] | 204.5 | 11,484 | RL reward (weights) |
| one sample, abandoned at 12,000 tokens and drawn again (`R12000`) | RL plain | 215 | 65.5 [60.3, 70.5] | 213.2 | 18,361 | RL reward (weights) |
| vote over 2, ties to the shortest finished sample (`vote2_short`) | RL plain | 212 | 64.6 [59.3, 69.6] | 210.3 | 18,689 | RL reward (weights) |
| one sample, abandoned at 8,000 tokens and drawn again (`R8000`) | RL plain | 204 | 62.2 [56.8, 67.3] | 204.2 | 22,170 | RL reward (weights) |
| sequential vote: stop when two agree, at most 3 samples (`seq3`) | RL plain | 216 | 65.9 [60.6, 70.8] | 212.7 | 23,613 | RL reward (weights) |
| draw 2; if they differ draw 2 more; vote, ties to the shortest (`seq_2then4_short`) | RL plain | 223 | 68.0 [62.8, 72.8] | 222.0 | 28,610 | RL reward (weights) |
| sequential vote, at most 4, each sample restarted after a cap hit (`seq4_restart`) | RL plain | 224 | 68.3 [63.1, 73.1] | 218.2 | 31,326 | RL reward (weights) |
| sequential vote, at most 4, restarts, ties to the shortest (`seq4_restart_short`) | RL plain | 222 | 67.7 [62.4, 72.5] | 220.5 | 31,326 | RL reward (weights) |
| vote over 4 after restart, ties to the shortest (`vote4_restart_short`) | RL plain | 220 | 67.1 [61.8, 71.9] | 220.0 | 44,108 | RL reward (weights) |

## Base rule against one RL sample (24-order means; paired bootstrap, 5,000 resamples)

| Base rule | Base right (24) | minus RL single, points [95 %] | Tokens, multiple of one RL sample [95 %] | RL under the same rule (24) | RL minus base, points [95 %] |
|---|---|---|---|---|---|
| `single` | 158.5 | -12.7 [-15.5, -10.1] | 0.99 [0.96, 1.02] | 200.0 | +12.7 [+10.1, +15.5] |
| `restart` | 167.0 | -10.1 [-12.7, -7.6] | 1.48 [1.40, 1.57] | 204.5 | +11.4 [+8.9, +14.1] |
| `vote2_short` | 169.8 | -9.2 [-11.9, -6.6] | 1.98 [1.93, 2.03] | 210.3 | +12.4 [+9.6, +15.3] |
| `R8000` | 162.0 | -11.6 [-14.5, -8.8] | 2.05 [1.94, 2.17] | 204.2 | +12.9 [+9.9, +16.0] |
| `R12000` | 168.9 | -9.5 [-12.2, -6.8] | 2.15 [1.99, 2.30] | 213.2 | +13.5 [+10.4, +16.8] |
| `seq3` | 178.8 | -6.5 [-9.3, -3.9] | 2.74 [2.65, 2.83] | 212.7 | +10.3 [+7.4, +13.4] |
| `seq_2then4_short` | 190.5 | -2.9 [-6.0, +0.0] | 3.51 [3.36, 3.64] | 222.0 | +9.6 [+6.0, +13.4] |
| `seq4_restart` | 190.8 | -2.8 [-5.7, -0.1] | 5.02 [4.64, 5.39] | 218.2 | +8.4 [+5.2, +11.6] |
| `seq4_restart_short` | 198.5 | -0.5 [-3.4, +2.4] | 5.02 [4.64, 5.39] | 220.5 | +6.7 [+3.4, +10.2] |
| `vote4_restart_short` | 199.0 | -0.3 [-3.3, +2.5] | 5.93 [5.60, 6.27] | 220.0 | +6.4 [+3.0, +10.1] |
