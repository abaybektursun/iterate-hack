# Token frontier, math500, n = 500, T 1.0 / top-p 1.0, grader v3

Right: stored draw order. Right (24): mean over the 24 draw orders. Tokens: generated tokens per problem, stored order.

| Configuration | Model | Right | Percent [95 %] | Right (24) | Tokens per problem | Training signal |
|---|---|---|---|---|---|---|
| one sample (`single`) | base + cue | 405 | 81.0 [77.3, 84.2] | 410.5 | 3,808 | none |
| one sample, sampled again after a cap hit (up to 2 times) (`restart`) | base + cue | 413 | 82.6 [79.0, 85.7] | 418.0 | 4,852 | none |
| one sample, abandoned at 12,000 tokens and drawn again (`R12000`) | base + cue | 422 | 84.4 [81.0, 87.3] | 423.9 | 5,425 | none |
| one sample, abandoned at 8,000 tokens and drawn again (`R8000`) | base + cue | 428 | 85.6 [82.3, 88.4] | 424.0 | 6,116 | none |
| vote over 2 (`vote2`) | base + cue | 417 | 83.4 [79.9, 86.4] | 418.8 | 7,952 | none |
| vote over 2, ties to the shortest finished sample (`vote2_short`) | base + cue | 423 | 84.6 [81.2, 87.5] | 428.7 | 7,952 | none |
| sequential vote: stop when two agree, at most 3 samples (`seq3`) | base + cue | 439 | 87.8 [84.6, 90.4] | 442.2 | 10,042 | none |
| sequential vote, at most 4, samples abandoned at 8,000 tokens (`seq4_L8000`) | base + cue | 450 | 90.0 [87.1, 92.3] | 444.6 | 10,283 | none |
| sequential vote, at most 4; a finished answer of at most 2,000 tokens is accepted at once (`seq4_stop2000`) | base + cue | 438 | 87.6 [84.4, 90.2] | 439.5 | 10,495 | none |
| sequential vote, at most 4; a finished answer of at most 1,000 tokens is accepted at once (`seq4_stop1000`) | base + cue | 443 | 88.6 [85.5, 91.1] | 441.7 | 10,942 | none |
| sequential vote, at most 4, samples abandoned at 12,000 tokens (`seq4_L12000`) | base + cue | 450 | 90.0 [87.1, 92.3] | 450.0 | 10,986 | none |
| sequential vote: stop when two agree, at most 4 samples (`seq4`) | base + cue | 446 | 89.2 [86.2, 91.6] | 448.2 | 11,369 | none |
| sequential vote, at most 4, ties to the shortest finished sample (`seq4_short`) | base + cue | 451 | 90.2 [87.3, 92.5] | 452.0 | 11,369 | none |
| vote over 3 (`vote3`) | base + cue | 439 | 87.8 [84.6, 90.4] | 442.2 | 11,878 | none |
| vote over 3, ties to the shortest finished sample (`vote3_short`) | base + cue | 444 | 88.8 [85.7, 91.3] | 446.5 | 11,878 | none |
| draw 2; if they differ draw 2 more; vote (`seq_2then4`) | base + cue | 446 | 89.2 [86.2, 91.6] | 448.2 | 12,086 | none |
| draw 2; if they differ draw 2 more; vote, ties to the shortest (`seq_2then4_short`) | base + cue | 452 | 90.4 [87.5, 92.7] | 452.7 | 12,086 | none |
| 4 in parallel, all stop when two finished answers agree (`par4_m2`) | base + cue | 447 | 89.4 [86.4, 91.8] | 448.2 | 13,403 | none |
| sequential vote, at most 4, each sample restarted after a cap hit (`seq4_restart`) | base + cue | 449 | 89.8 [86.8, 92.2] | 452.1 | 14,644 | none |
| sequential vote, at most 4, restarts, ties to the shortest (`seq4_restart_short`) | base + cue | 451 | 90.2 [87.3, 92.5] | 453.0 | 14,644 | none |
| vote over 4 (`vote4`) | base + cue | 446 | 89.2 [86.2, 91.6] | 448.2 | 16,034 | none |
| vote over 4, ties to the shortest finished sample (`vote4_short`) | base + cue | 453 | 90.6 [87.7, 92.9] | 453.0 | 16,034 | none |
| vote over 4 after restart (`vote4_restart`) | base + cue | 450 | 90.0 [87.1, 92.3] | 452.1 | 19,697 | none |
| vote over 4 after restart, ties to the shortest (`vote4_restart_short`) | base + cue | 454 | 90.8 [87.9, 93.0] | 454.0 | 19,697 | none |
| one sample (`single`) | RL plain | 456 | 91.2 [88.4, 93.4] | 460.0 | 4,675 | RL reward (weights) |
| one sample, sampled again after a cap hit (up to 2 times) (`restart`) | RL plain | 458 | 91.6 [88.8, 93.7] | 463.0 | 4,899 | RL reward (weights) |
| one sample, abandoned at 12,000 tokens and drawn again (`R12000`) | RL plain | 464 | 92.8 [90.2, 94.8] | 466.2 | 6,155 | RL reward (weights) |
| one sample, abandoned at 8,000 tokens and drawn again (`R8000`) | RL plain | 462 | 92.4 [89.7, 94.4] | 464.2 | 7,542 | RL reward (weights) |
| vote over 2 (`vote2`) | RL plain | 456 | 91.2 [88.4, 93.4] | 461.1 | 9,263 | RL reward (weights) |
| vote over 2, ties to the shortest finished sample (`vote2_short`) | RL plain | 463 | 92.6 [90.0, 94.6] | 468.0 | 9,263 | RL reward (weights) |
| sequential vote: stop when two agree, at most 3 samples (`seq3`) | RL plain | 468 | 93.6 [91.1, 95.4] | 470.4 | 10,543 | RL reward (weights) |
| sequential vote, at most 4; a finished answer of at most 2,000 tokens is accepted at once (`seq4_stop2000`) | RL plain | 474 | 94.8 [92.5, 96.4] | 474.1 | 10,661 | RL reward (weights) |
| sequential vote, at most 4; a finished answer of at most 1,000 tokens is accepted at once (`seq4_stop1000`) | RL plain | 474 | 94.8 [92.5, 96.4] | 474.0 | 11,036 | RL reward (weights) |
| sequential vote: stop when two agree, at most 4 samples (`seq4`) | RL plain | 474 | 94.8 [92.5, 96.4] | 474.3 | 11,098 | RL reward (weights) |
| sequential vote, at most 4, ties to the shortest finished sample (`seq4_short`) | RL plain | 475 | 95.0 [92.7, 96.6] | 474.5 | 11,098 | RL reward (weights) |
| sequential vote, at most 4, samples abandoned at 12,000 tokens (`seq4_L12000`) | RL plain | 471 | 94.2 [91.8, 95.9] | 472.8 | 11,261 | RL reward (weights) |
| sequential vote, at most 4, samples abandoned at 8,000 tokens (`seq4_L8000`) | RL plain | 466 | 93.2 [90.6, 95.1] | 467.0 | 11,613 | RL reward (weights) |
| draw 2; if they differ draw 2 more; vote (`seq_2then4`) | RL plain | 474 | 94.8 [92.5, 96.4] | 474.3 | 11,751 | RL reward (weights) |
| draw 2; if they differ draw 2 more; vote, ties to the shortest (`seq_2then4_short`) | RL plain | 475 | 95.0 [92.7, 96.6] | 474.8 | 11,751 | RL reward (weights) |
| sequential vote, at most 4, each sample restarted after a cap hit (`seq4_restart`) | RL plain | 475 | 95.0 [92.7, 96.6] | 476.1 | 11,803 | RL reward (weights) |
| sequential vote, at most 4, restarts, ties to the shortest (`seq4_restart_short`) | RL plain | 475 | 95.0 [92.7, 96.6] | 475.0 | 11,803 | RL reward (weights) |
| vote over 3 (`vote3`) | RL plain | 468 | 93.6 [91.1, 95.4] | 470.4 | 14,004 | RL reward (weights) |
| vote over 3, ties to the shortest finished sample (`vote3_short`) | RL plain | 472 | 94.4 [92.0, 96.1] | 472.7 | 14,004 | RL reward (weights) |
| 4 in parallel, all stop when two finished answers agree (`par4_m2`) | RL plain | 473 | 94.6 [92.3, 96.3] | 473.8 | 16,553 | RL reward (weights) |
| vote over 4 (`vote4`) | RL plain | 474 | 94.8 [92.5, 96.4] | 474.3 | 18,747 | RL reward (weights) |
| vote over 4, ties to the shortest finished sample (`vote4_short`) | RL plain | 475 | 95.0 [92.7, 96.6] | 475.0 | 18,747 | RL reward (weights) |
| vote over 4 after restart (`vote4_restart`) | RL plain | 475 | 95.0 [92.7, 96.6] | 476.1 | 19,864 | RL reward (weights) |
| vote over 4 after restart, ties to the shortest (`vote4_restart_short`) | RL plain | 475 | 95.0 [92.7, 96.6] | 475.0 | 19,864 | RL reward (weights) |
| RL-Zero-Math 3.1, cue | other arm, one sample | 457 | 91.4 | | 4,696 | RL reward (weights) |
| Olmo-3-7B-Think-SFT, cue | other arm, one sample | 454 | 90.8 | | 4,888 | SFT data |
| base + 1.5 (RL - base), cue | other arm, one sample | 453 | 90.6 | | 4,862 | RL reward (weights) |
| base + 0.5 (RL - base), cue | other arm, one sample | 452 | 90.4 | | 4,626 | RL reward (weights) |
| base + 0.75 (RL - base), cue | other arm, one sample | 451 | 90.2 | | 4,654 | RL reward (weights) |
| base + 1.25 (RL - base), cue | other arm, one sample | 450 | 90.0 | | 4,852 | RL reward (weights) |
| RL-Zero-Code 3.1, cue | other arm, one sample | 450 | 90.0 | | 3,336 | RL reward (weights) |
| Olmo-3-7B-RL-Zero-Math (3.0), cue | other arm, one sample | 448 | 89.6 | | 4,527 | RL reward (weights) |
| base + 0.5 (RL - base), plain | other arm, one sample | 443 | 88.6 | | 4,536 | RL reward (weights) |
| Olmo-3-7B-RL-Zero-Math (3.0), plain | other arm, one sample | 443 | 88.6 | | 4,506 | RL reward (weights) |
| base + 0.25 (RL - base), cue | other arm, one sample | 441 | 88.2 | | 4,036 | RL reward (weights) |
| Olmo-3-7B-RL-Zero-Mix (3.0), cue | other arm, one sample | 440 | 88.0 | | 5,203 | RL reward (weights) |
| Olmo-3-7B-Think-SFT, plain | other arm, one sample | 440 | 88.0 | | 4,492 | SFT data |
| base + cue + 3 solved problems written by Math-RL in context (n 497) | other arm, one sample | 435 | 87.5 | | 4,379 | RL reward (RL text in context) |
| Olmo-3-7B-RL-Zero-General (3.0), cue | other arm, one sample | 429 | 85.8 | | 3,839 | RL reward (weights) |
| base + top 8 singular directions per matrix of the RL delta, plain | other arm, one sample | 427 | 85.4 | | 3,962 | RL reward (weights) |
| base + random difference of the RL norm, cue (control) | other arm, one sample | 417 | 83.4 | | 3,944 | none (control) |
| base + cue + 3 solved problems written by the cued base in context (n 497) | other arm, one sample | 414 | 83.3 | | 3,365 | own samples (in context) |
| base + cue + 3 solved problems written by Code-RL in context (n 497) | other arm, one sample | 412 | 82.9 | | 3,815 | RL reward (RL text in context) |
| Olmo-3-7B-RL-Zero-Code (3.0), cue | other arm, one sample | 411 | 82.2 | | 3,069 | RL reward (weights) |
| base + 0.25 (RL - base), plain | other arm, one sample | 405 | 81.0 | | 3,653 | RL reward (weights) |
| RL-Zero-Code 3.1, plain | other arm, one sample | 390 | 78.0 | | 3,066 | RL reward (weights) |
| Olmo-3-7B-RL-Zero-If (3.0), cue | other arm, one sample | 377 | 75.4 | | 2,667 | RL reward (weights) |
| Olmo-3-7B-RL-Zero-Mix (3.0), plain | other arm, one sample | 372 | 74.4 | | 4,228 | RL reward (weights) |
| Olmo-3-7B-RL-Zero-Code (3.0), plain | other arm, one sample | 360 | 72.0 | | 2,630 | RL reward (weights) |
| Olmo-3-7B-RL-Zero-General (3.0), plain | other arm, one sample | 323 | 64.6 | | 2,303 | RL reward (weights) |
| base + random rank-8 directions, plain (control) | other arm, one sample | 197 | 39.4 | | 1,968 | none (control) |
| Olmo-3-7B-RL-Zero-If (3.0), plain | other arm, one sample | 55 | 11.0 | | 39 | RL reward (weights) |

## Base rule against one RL sample (24-order means; paired bootstrap, 5,000 resamples)

| Base rule | Base right (24) | minus RL single, points [95 %] | Tokens, multiple of one RL sample [95 %] | RL under the same rule (24) | RL minus base, points [95 %] |
|---|---|---|---|---|---|
| `single` | 410.5 | -9.9 [-11.6, -8.3] | 0.86 [0.82, 0.89] | 460.0 | +9.9 [+8.3, +11.6] |
| `restart` | 418.0 | -8.4 [-10.1, -6.8] | 1.05 [0.97, 1.14] | 463.0 | +9.0 [+7.4, +10.7] |
| `R12000` | 423.9 | -7.2 [-9.0, -5.5] | 1.22 [1.10, 1.34] | 466.2 | +8.4 [+6.7, +10.2] |
| `R8000` | 424.0 | -7.2 [-9.0, -5.4] | 1.37 [1.25, 1.49] | 464.2 | +8.0 [+6.3, +9.9] |
| `vote2` | 418.8 | -8.2 [-9.9, -6.7] | 1.71 [1.64, 1.78] | 461.1 | +8.4 [+6.9, +10.1] |
| `vote2_short` | 428.7 | -6.3 [-8.0, -4.5] | 1.71 [1.64, 1.78] | 468.0 | +7.9 [+6.0, +9.7] |
| `seq3` | 442.2 | -3.6 [-5.1, -2.0] | 2.13 [2.02, 2.24] | 470.4 | +5.7 [+4.0, +7.4] |
| `seq4_stop2000` | 439.5 | -4.1 [-5.8, -2.4] | 2.22 [2.05, 2.38] | 474.1 | +6.9 [+5.0, +8.9] |
| `seq4_L8000` | 444.6 | -3.1 [-4.8, -1.4] | 2.23 [2.12, 2.34] | 467.0 | +4.5 [+2.8, +6.3] |
| `seq4_stop1000` | 441.7 | -3.7 [-5.5, -1.9] | 2.32 [2.16, 2.48] | 474.0 | +6.5 [+4.5, +8.5] |
| `seq4_L12000` | 450.0 | -2.0 [-3.7, -0.3] | 2.35 [2.21, 2.48] | 472.8 | +4.5 [+2.8, +6.4] |
| `seq4` | 448.2 | -2.4 [-4.0, -0.7] | 2.40 [2.25, 2.56] | 474.3 | +5.2 [+3.4, +7.2] |
| `seq4_short` | 452.0 | -1.6 [-3.3, +0.2] | 2.40 [2.25, 2.56] | 474.5 | +4.5 [+2.6, +6.5] |
| `seq_2then4` | 448.2 | -2.4 [-4.0, -0.7] | 2.55 [2.40, 2.71] | 474.3 | +5.2 [+3.4, +7.2] |
| `seq_2then4_short` | 452.7 | -1.5 [-3.2, +0.3] | 2.55 [2.40, 2.71] | 474.8 | +4.4 [+2.5, +6.4] |
| `vote3` | 442.2 | -3.6 [-5.1, -2.0] | 2.57 [2.46, 2.67] | 470.4 | +5.7 [+4.0, +7.4] |
| `vote3_short` | 446.5 | -2.7 [-4.3, -1.1] | 2.57 [2.46, 2.67] | 472.7 | +5.2 [+3.5, +7.1] |
| `par4_m2` | 448.2 | -2.4 [-4.1, -0.7] | 2.86 [2.72, 3.00] | 473.8 | +5.1 [+3.2, +7.1] |
| `seq4_restart` | 452.1 | -1.6 [-3.2, +0.1] | 3.03 [2.67, 3.40] | 476.1 | +4.8 [+3.1, +6.6] |
| `seq4_restart_short` | 453.0 | -1.4 [-3.1, +0.3] | 3.03 [2.67, 3.40] | 475.0 | +4.4 [+2.7, +6.2] |
| `vote4` | 448.2 | -2.4 [-4.0, -0.7] | 3.42 [3.28, 3.56] | 474.3 | +5.2 [+3.4, +7.2] |
| `vote4_short` | 453.0 | -1.4 [-3.2, +0.4] | 3.42 [3.28, 3.56] | 475.0 | +4.4 [+2.4, +6.4] |
| `vote4_restart` | 452.1 | -1.6 [-3.2, +0.1] | 4.20 [3.87, 4.56] | 476.1 | +4.8 [+3.1, +6.6] |
| `vote4_restart_short` | 454.0 | -1.2 [-3.0, +0.6] | 4.20 [3.87, 4.56] | 475.0 | +4.2 [+2.4, +6.0] |

## Rule chosen per token budget (5 folds: chosen on 4, scored on the 5th)

| Model | Budget | Chosen on all | Chosen per fold | Held-out right (24) | Held-out tokens |
|---|---|---|---|---|---|
| base | 5,000 | `restart` | restart, restart, single, single, restart | 416.5 | 4,589 |
| base | 7,500 | `R8000` | R8000, R12000, R12000, R12000, R8000 | 422.0 | 6,110 |
| base | 10,000 | `seq3` | seq3, seq3, vote2_short, vote2_short, seq3 | 438.0 | 9,382 |
| base | 12,500 | `seq_2then4_short` | seq_2then4_short, seq_2then4_short, seq_2then4_short, seq_2then4_short, seq4_short | 452.0 | 11,774 |
| base | 15,000 | `seq4_restart_short` | seq_2then4_short, seq4_restart_short, seq4_restart_short, seq4_restart_short, seq4_restart_short | 450.3 | 13,804 |
| base | 17,500 | `seq4_restart_short` | vote4_short, seq4_restart_short, seq4_restart_short, seq4_restart_short, seq4_restart_short | 450.5 | 14,597 |
| base | 20,000 | `vote4_restart_short` | vote4_short, vote4_restart_short, seq4_restart_short, seq4_restart_short, vote4_restart_short | 450.0 | 16,878 |
| rl | 5,000 | `restart` | restart, restart, single, single, restart | 462.8 | 4,909 |
| rl | 7,500 | `R12000` | R12000, R12000, R12000, R12000, R12000 | 466.2 | 6,225 |
| rl | 10,000 | `vote2_short` | vote2_short, vote2_short, vote2_short, vote2_short, vote2_short | 468.0 | 9,374 |
| rl | 12,500 | `seq4_restart` | seq4_restart, seq4_short, seq4_restart, seq4_restart, seq4_restart | 474.3 | 11,625 |
| rl | 15,000 | `seq4_restart` | seq4_restart, seq4_short, seq4_restart, seq4_restart, seq4_restart | 474.3 | 11,625 |
| rl | 17,500 | `seq4_restart` | seq4_restart, seq4_short, seq4_restart, seq4_restart, seq4_restart | 474.3 | 11,625 |
| rl | 20,000 | `seq4_restart` | seq4_restart, seq4_short, seq4_restart, seq4_restart, seq4_restart | 474.3 | 11,625 |
