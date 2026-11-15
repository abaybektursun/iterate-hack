# Token frontier, fresh2026, n = 136, T 1.0 / top-p 1.0, grader v3

Right: stored draw order. Right (24): mean over the 24 draw orders. Tokens: generated tokens per problem, stored order.

| Configuration | Model | Right | Percent [95 %] | Right (24) | Tokens per problem | Training signal |
|---|---|---|---|---|---|---|
| one sample (`single`) | base + cue | 28 | 20.6 [14.6, 28.1] | 29.5 | 12,790 | none |
| one sample, sampled again after a cap hit (up to 2 times) (`restart`) | base + cue | 28 | 20.6 [14.6, 28.1] | 29.5 | 12,790 | none |
| vote over 2, ties to the shortest finished sample (`vote2_short`) | base + cue | 30 | 22.1 [15.9, 29.7] | 32.5 | 25,310 | none |
| one sample, abandoned at 8,000 tokens and drawn again (`R8000`) | base + cue | 29 | 21.3 [15.3, 28.9] | 30.5 | 28,617 | none |
| one sample, abandoned at 12,000 tokens and drawn again (`R12000`) | base + cue | 30 | 22.1 [15.9, 29.7] | 31.3 | 30,287 | none |
| sequential vote: stop when two agree, at most 3 samples (`seq3`) | base + cue | 34 | 25.0 [18.5, 32.9] | 36.2 | 36,313 | none |
| sequential vote, at most 4, each sample restarted after a cap hit (`seq4_restart`) | base + cue | 38 | 27.9 [21.1, 36.0] | 38.8 | 46,047 | none |
| sequential vote, at most 4, restarts, ties to the shortest (`seq4_restart_short`) | base + cue | 38 | 27.9 [21.1, 36.0] | 38.0 | 46,047 | none |
| draw 2; if they differ draw 2 more; vote, ties to the shortest (`seq_2then4_short`) | base + cue | 38 | 27.9 [21.1, 36.0] | 38.0 | 47,626 | none |
| vote over 4 after restart, ties to the shortest (`vote4_restart_short`) | base + cue | 38 | 27.9 [21.1, 36.0] | 38.0 | 51,158 | none |
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

## Base rule against one RL sample (24-order means; paired bootstrap, 5,000 resamples)

| Base rule | Base right (24) | minus RL single, points [95 %] | Tokens, multiple of one RL sample [95 %] | RL under the same rule (24) | RL minus base, points [95 %] |
|---|---|---|---|---|---|
| `single` | 29.5 | -15.4 [-20.0, -11.4] | 1.06 [1.03, 1.09] | 50.5 | +15.4 [+11.4, +20.0] |
| `restart` | 29.5 | -15.4 [-20.0, -11.4] | 1.06 [1.03, 1.09] | 50.5 | +15.4 [+11.4, +20.0] |
| `vote2_short` | 32.5 | -13.2 [-17.6, -9.1] | 2.12 [2.06, 2.18] | 55.5 | +16.9 [+12.3, +22.1] |
| `R8000` | 30.5 | -14.7 [-19.5, -10.2] | 2.38 [2.25, 2.50] | 52.2 | +15.9 [+11.3, +21.0] |
| `R12000` | 31.3 | -14.1 [-18.9, -9.8] | 2.57 [2.38, 2.76] | 54.8 | +17.3 [+12.1, +23.0] |
| `seq3` | 36.2 | -10.5 [-14.9, -6.4] | 3.04 [2.95, 3.14] | 54.9 | +13.7 [+9.3, +18.6] |
| `seq4_restart` | 38.8 | -8.6 [-13.4, -4.2] | 3.86 [3.70, 4.01] | 55.8 | +12.4 [+7.5, +17.8] |
| `seq4_restart_short` | 38.0 | -9.2 [-14.2, -4.4] | 3.86 [3.70, 4.01] | 60.3 | +16.4 [+10.0, +23.0] |
| `seq_2then4_short` | 38.0 | -9.2 [-14.2, -4.4] | 3.97 [3.82, 4.11] | 60.3 | +16.4 [+10.0, +23.0] |
| `vote4_restart_short` | 38.0 | -9.2 [-14.2, -4.4] | 4.23 [4.12, 4.35] | 60.3 | +16.4 [+10.0, +23.0] |
