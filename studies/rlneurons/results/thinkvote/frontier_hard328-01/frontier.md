# Token frontier, hard328, n = 328, T 1.0 / top-p 1.0, grader v3

The `--base` slot of analysis/frontier.py holds Think-SFT with the cue (no restarts: its `restart` rules equal the no-restart rules); labels edited after the run, numbers untouched. readout.json and per_problem.json keep the key "base".

Right: stored draw order. Right (24): mean over the 24 draw orders. Tokens: generated tokens per problem, stored order.

| Configuration | Model | Right | Percent [95 %] | Right (24) | Tokens per problem | Training signal |
|---|---|---|---|---|---|---|
| one sample (`single`) | Think-SFT + cue | 212 | 64.6 [59.3, 69.6] | 209.0 | 10,137 | SFT data (no reward) |
| one sample, sampled again after a cap hit (up to 2 times) (`restart`) | Think-SFT + cue | 212 | 64.6 [59.3, 69.6] | 209.0 | 10,137 | SFT data (no reward) |
| vote over 2, ties to the shortest finished sample (`vote2_short`) | Think-SFT + cue | 234 | 71.3 [66.2, 76.0] | 224.2 | 20,301 | SFT data (no reward) |
| one sample, abandoned at 8,000 tokens and drawn again (`R8000`) | Think-SFT + cue | 198 | 60.4 [55.0, 65.5] | 209.2 | 22,952 | SFT data (no reward) |
| one sample, abandoned at 12,000 tokens and drawn again (`R12000`) | Think-SFT + cue | 217 | 66.2 [60.9, 71.1] | 218.1 | 23,617 | SFT data (no reward) |
| sequential vote: stop when two agree, at most 3 samples (`seq3`) | Think-SFT + cue | 241 | 73.5 [68.4, 78.0] | 233.2 | 26,269 | SFT data (no reward) |
| sequential vote, at most 4, each sample restarted after a cap hit (`seq4_restart`) | Think-SFT + cue | 241 | 73.5 [68.4, 78.0] | 238.9 | 30,904 | SFT data (no reward) |
| sequential vote, at most 4, restarts, ties to the shortest (`seq4_restart_short`) | Think-SFT + cue | 240 | 73.2 [68.1, 77.7] | 239.5 | 30,904 | SFT data (no reward) |
| draw 2; if they differ draw 2 more; vote, ties to the shortest (`seq_2then4_short`) | Think-SFT + cue | 240 | 73.2 [68.1, 77.7] | 239.2 | 32,234 | SFT data (no reward) |
| vote over 4 after restart, ties to the shortest (`vote4_restart_short`) | Think-SFT + cue | 239 | 72.9 [67.8, 77.4] | 239.0 | 40,410 | SFT data (no reward) |
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

## Think-SFT rule against one RL sample (24-order means; paired bootstrap, 5,000 resamples)

| Think-SFT rule | Think-SFT right (24) | minus RL single, points [95 %] | Tokens, multiple of one RL sample [95 %] | RL under the same rule (24) | RL minus Think-SFT, points [95 %] |
|---|---|---|---|---|---|
| `single` | 209.0 | +2.7 [+0.4, +5.2] | 1.08 [1.06, 1.11] | 200.0 | -2.7 [-5.2, -0.4] |
| `restart` | 209.0 | +2.7 [+0.4, +5.2] | 1.08 [1.06, 1.11] | 204.5 | -1.4 [-3.8, +1.1] |
| `vote2_short` | 224.2 | +7.4 [+4.7, +10.0] | 2.17 [2.12, 2.21] | 210.3 | -4.2 [-6.9, -1.5] |
| `R8000` | 209.2 | +2.8 [+0.3, +5.3] | 2.45 [2.36, 2.55] | 204.2 | -1.5 [-4.0, +1.1] |
| `R12000` | 218.1 | +5.5 [+2.8, +8.2] | 2.52 [2.36, 2.67] | 213.2 | -1.5 [-4.6, +1.6] |
| `seq3` | 233.2 | +10.1 [+7.1, +13.0] | 2.80 [2.71, 2.89] | 212.7 | -6.2 [-9.2, -3.4] |
| `seq4_restart` | 238.9 | +11.9 [+8.7, +15.0] | 3.31 [3.15, 3.45] | 218.2 | -6.3 [-9.5, -3.3] |
| `seq4_restart_short` | 239.5 | +12.0 [+8.9, +15.2] | 3.31 [3.15, 3.45] | 220.5 | -5.8 [-9.0, -2.7] |
| `seq_2then4_short` | 239.2 | +11.9 [+8.8, +15.1] | 3.43 [3.28, 3.58] | 222.0 | -5.2 [-8.7, -2.0] |
| `vote4_restart_short` | 239.0 | +11.9 [+8.8, +15.0] | 4.33 [4.24, 4.42] | 220.0 | -5.8 [-9.1, -2.4] |
