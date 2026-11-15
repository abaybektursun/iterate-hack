# Token frontier, fresh2026, n = 136, T 1.0 / top-p 1.0, grader v3

Right: stored draw order. Right (24): mean over the 24 draw orders. Tokens: generated tokens per problem, stored order.

| Configuration | Model | Right | Percent [95 %] | Right (24) | Tokens per problem | Training signal |
|---|---|---|---|---|---|---|
| one sample (`single`) | Think-SFT + cue | 65 | 47.8 [39.6, 56.1] | 60.0 | 12,876 | imitation of traces, no reward |
| one sample, sampled again after a cap hit (up to 2 times) (`restart`) | Think-SFT + cue | 65 | 47.8 [39.6, 56.1] | 60.0 | 12,876 | imitation of traces, no reward |
| vote over 2, ties to the shortest finished sample (`vote2_short`) | Think-SFT + cue | 68 | 50.0 [41.7, 58.3] | 68.5 | 25,999 | imitation of traces, no reward |
| one sample, abandoned at 8,000 tokens and drawn again (`R8000`) | Think-SFT + cue | 63 | 46.3 [38.2, 54.7] | 60.8 | 31,913 | imitation of traces, no reward |
| one sample, abandoned at 12,000 tokens and drawn again (`R12000`) | Think-SFT + cue | 68 | 50.0 [41.7, 58.3] | 64.9 | 32,570 | imitation of traces, no reward |
| sequential vote: stop when two agree, at most 3 samples (`seq3`) | Think-SFT + cue | 71 | 52.2 [43.9, 60.4] | 72.5 | 34,718 | imitation of traces, no reward |
| sequential vote, at most 4, each sample restarted after a cap hit (`seq4_restart`) | Think-SFT + cue | 75 | 55.1 [46.8, 63.2] | 75.5 | 42,251 | imitation of traces, no reward |
| sequential vote, at most 4, restarts, ties to the shortest (`seq4_restart_short`) | Think-SFT + cue | 76 | 55.9 [47.5, 64.0] | 76.0 | 42,251 | imitation of traces, no reward |
| draw 2; if they differ draw 2 more; vote, ties to the shortest (`seq_2then4_short`) | Think-SFT + cue | 76 | 55.9 [47.5, 64.0] | 76.0 | 43,364 | imitation of traces, no reward |
| vote over 4 after restart, ties to the shortest (`vote4_restart_short`) | Think-SFT + cue | 76 | 55.9 [47.5, 64.0] | 76.0 | 52,170 | imitation of traces, no reward |
| one sample (`single`) | RL plain | 49 | 36.0 [28.4, 44.4] | 50.5 | 12,033 | RL reward (weights) |
| one sample, sampled again after a cap hit (up to 2 times) (`restart`) | RL plain | 49 | 36.0 [28.4, 44.4] | 50.5 | 12,033 | RL reward (weights) |
| vote over 2, ties to the shortest finished sample (`vote2_short`) | RL plain | 58 | 42.6 [34.6, 51.0] | 55.5 | 24,334 | RL reward (weights) |
| one sample, abandoned at 12,000 tokens and drawn again (`R12000`) | RL plain | 57 | 41.9 [34.0, 50.3] | 54.8 | 28,555 | RL reward (weights) |
| one sample, abandoned at 8,000 tokens and drawn again (`R8000`) | RL plain | 53 | 39.0 [31.2, 47.4] | 52.2 | 30,473 | RL reward (weights) |
| sequential vote: stop when two agree, at most 3 samples (`seq3`) | RL plain | 56 | 41.2 [33.3, 49.6] | 54.9 | 32,394 | RL reward (weights) |
| sequential vote, at most 4, each sample restarted after a cap hit (`seq4_restart`) | RL plain | 57 | 41.9 [34.0, 50.3] | 55.8 | 37,443 | RL reward (weights) |
| sequential vote, at most 4, restarts, ties to the shortest (`seq4_restart_short`) | RL plain | 60 | 44.1 [36.0, 52.5] | 60.3 | 37,443 | RL reward (weights) |
| draw 2; if they differ draw 2 more; vote, ties to the shortest (`seq_2then4_short`) | RL plain | 60 | 44.1 [36.0, 52.5] | 60.3 | 40,351 | RL reward (weights) |
| vote over 4 after restart, ties to the shortest (`vote4_restart_short`) | RL plain | 60 | 44.1 [36.0, 52.5] | 60.3 | 48,331 | RL reward (weights) |

## Think-SFT rule against one RL sample (24-order means; paired bootstrap, 5,000 resamples)

| Think-SFT rule | Think-SFT right (24) | minus RL single, points [95 %] | Tokens, multiple of one RL sample [95 %] | RL under the same rule (24) | RL minus Think-SFT, points [95 %] |
|---|---|---|---|---|---|
| `single` | 60.0 | +7.0 [+3.1, +11.0] | 1.08 [1.05, 1.11] | 50.5 | -7.0 [-11.0, -3.1] |
| `restart` | 60.0 | +7.0 [+3.1, +11.0] | 1.08 [1.05, 1.11] | 50.5 | -7.0 [-11.0, -3.1] |
| `vote2_short` | 68.5 | +13.2 [+8.6, +18.0] | 2.16 [2.11, 2.21] | 55.5 | -9.6 [-14.2, -4.9] |
| `R8000` | 60.8 | +7.5 [+3.7, +11.8] | 2.64 [2.54, 2.75] | 52.2 | -6.3 [-10.8, -2.2] |
| `R12000` | 64.9 | +10.6 [+6.2, +15.3] | 2.73 [2.54, 2.92] | 54.8 | -7.4 [-12.3, -2.7] |
| `seq3` | 72.5 | +16.2 [+11.0, +21.3] | 2.91 [2.79, 3.02] | 54.9 | -12.9 [-18.1, -7.7] |
| `seq4_restart` | 75.5 | +18.4 [+12.7, +24.1] | 3.55 [3.35, 3.74] | 55.8 | -14.5 [-20.6, -8.5] |
| `seq4_restart_short` | 76.0 | +18.8 [+12.9, +24.6] | 3.55 [3.35, 3.74] | 60.3 | -11.5 [-17.6, -5.6] |
| `seq_2then4_short` | 76.0 | +18.8 [+12.9, +24.6] | 3.66 [3.47, 3.84] | 60.3 | -11.5 [-17.6, -5.6] |
| `vote4_restart_short` | 76.0 | +18.8 [+12.9, +24.6] | 4.32 [4.21, 4.43] | 60.3 | -11.5 [-17.6, -5.6] |
