# Token frontier, math500, n = 500, T 1.0 / top-p 1.0, grader v3

The `--base` slot of analysis/frontier.py holds Think-SFT with the cue (no restarts: its `restart` rules equal the no-restart rules); labels edited after the run, numbers untouched. readout.json and per_problem.json keep the key "base".

Right: stored draw order. Right (24): mean over the 24 draw orders. Tokens: generated tokens per problem, stored order.

| Configuration | Model | Right | Percent [95 %] | Right (24) | Tokens per problem | Training signal |
|---|---|---|---|---|---|---|
| one sample (`single`) | Think-SFT + cue | 461 | 92.2 [89.5, 94.2] | 460.2 | 4,900 | SFT data (no reward) |
| one sample, sampled again after a cap hit (up to 2 times) (`restart`) | Think-SFT + cue | 461 | 92.2 [89.5, 94.2] | 460.2 | 4,900 | SFT data (no reward) |
| one sample, abandoned at 12,000 tokens and drawn again (`R12000`) | Think-SFT + cue | 469 | 93.8 [91.3, 95.6] | 469.5 | 6,874 | SFT data (no reward) |
| one sample, abandoned at 8,000 tokens and drawn again (`R8000`) | Think-SFT + cue | 466 | 93.2 [90.6, 95.1] | 465.4 | 7,945 | SFT data (no reward) |
| vote over 2 (`vote2`) | Think-SFT + cue | 470 | 94.0 [91.6, 95.8] | 469.4 | 9,821 | SFT data (no reward) |
| vote over 2, ties to the shortest finished sample (`vote2_short`) | Think-SFT + cue | 473 | 94.6 [92.3, 96.3] | 474.1 | 9,821 | SFT data (no reward) |
| sequential vote, at most 4; a finished answer of at most 2,000 tokens is accepted at once (`seq4_stop2000`) | Think-SFT + cue | 481 | 96.2 [94.1, 97.6] | 479.8 | 10,908 | SFT data (no reward) |
| sequential vote: stop when two agree, at most 3 samples (`seq3`) | Think-SFT + cue | 479 | 95.8 [93.7, 97.2] | 478.5 | 10,937 | SFT data (no reward) |
| sequential vote, at most 4; a finished answer of at most 1,000 tokens is accepted at once (`seq4_stop1000`) | Think-SFT + cue | 481 | 96.2 [94.1, 97.6] | 480.0 | 11,417 | SFT data (no reward) |
| sequential vote: stop when two agree, at most 4 samples (`seq4`) | Think-SFT + cue | 481 | 96.2 [94.1, 97.6] | 480.8 | 11,521 | SFT data (no reward) |
| sequential vote, at most 4, ties to the shortest finished sample (`seq4_short`) | Think-SFT + cue | 481 | 96.2 [94.1, 97.6] | 480.5 | 11,521 | SFT data (no reward) |
| sequential vote, at most 4, each sample restarted after a cap hit (`seq4_restart`) | Think-SFT + cue | 481 | 96.2 [94.1, 97.6] | 480.8 | 11,521 | SFT data (no reward) |
| sequential vote, at most 4, restarts, ties to the shortest (`seq4_restart_short`) | Think-SFT + cue | 481 | 96.2 [94.1, 97.6] | 480.5 | 11,521 | SFT data (no reward) |
| sequential vote, at most 4, samples abandoned at 12,000 tokens (`seq4_L12000`) | Think-SFT + cue | 475 | 95.0 [92.7, 96.6] | 476.0 | 11,741 | SFT data (no reward) |
| draw 2; if they differ draw 2 more; vote (`seq_2then4`) | Think-SFT + cue | 481 | 96.2 [94.1, 97.6] | 480.8 | 12,026 | SFT data (no reward) |
| draw 2; if they differ draw 2 more; vote, ties to the shortest (`seq_2then4_short`) | Think-SFT + cue | 481 | 96.2 [94.1, 97.6] | 480.8 | 12,026 | SFT data (no reward) |
| sequential vote, at most 4, samples abandoned at 8,000 tokens (`seq4_L8000`) | Think-SFT + cue | 470 | 94.0 [91.6, 95.8] | 470.5 | 12,048 | SFT data (no reward) |
| vote over 3 (`vote3`) | Think-SFT + cue | 479 | 95.8 [93.7, 97.2] | 478.5 | 14,774 | SFT data (no reward) |
| vote over 3, ties to the shortest finished sample (`vote3_short`) | Think-SFT + cue | 479 | 95.8 [93.7, 97.2] | 479.1 | 14,774 | SFT data (no reward) |
| 4 in parallel, all stop when two finished answers agree (`par4_m2`) | Think-SFT + cue | 481 | 96.2 [94.1, 97.6] | 481.2 | 16,553 | SFT data (no reward) |
| vote over 4 (`vote4`) | Think-SFT + cue | 481 | 96.2 [94.1, 97.6] | 480.8 | 19,503 | SFT data (no reward) |
| vote over 4, ties to the shortest finished sample (`vote4_short`) | Think-SFT + cue | 481 | 96.2 [94.1, 97.6] | 481.0 | 19,503 | SFT data (no reward) |
| vote over 4 after restart (`vote4_restart`) | Think-SFT + cue | 481 | 96.2 [94.1, 97.6] | 480.8 | 19,503 | SFT data (no reward) |
| vote over 4 after restart, ties to the shortest (`vote4_restart_short`) | Think-SFT + cue | 481 | 96.2 [94.1, 97.6] | 481.0 | 19,503 | SFT data (no reward) |
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

## Think-SFT rule against one RL sample (24-order means; paired bootstrap, 5,000 resamples)

| Think-SFT rule | Think-SFT right (24) | minus RL single, points [95 %] | Tokens, multiple of one RL sample [95 %] | RL under the same rule (24) | RL minus Think-SFT, points [95 %] |
|---|---|---|---|---|---|
| `single` | 460.2 | +0.1 [-1.3, +1.4] | 1.04 [1.01, 1.07] | 460.0 | -0.1 [-1.4, +1.3] |
| `restart` | 460.2 | +0.1 [-1.3, +1.4] | 1.04 [1.01, 1.07] | 463.0 | +0.6 [-0.8, +1.8] |
| `R12000` | 469.5 | +1.9 [+0.5, +3.3] | 1.47 [1.34, 1.60] | 466.2 | -0.7 [-2.0, +0.6] |
| `R8000` | 465.4 | +1.1 [-0.2, +2.4] | 1.69 [1.57, 1.81] | 464.2 | -0.2 [-1.7, +1.1] |
| `vote2` | 469.4 | +1.9 [+0.5, +3.3] | 2.08 [2.02, 2.14] | 461.1 | -1.7 [-3.1, -0.3] |
| `vote2_short` | 474.1 | +2.8 [+1.3, +4.3] | 2.08 [2.02, 2.14] | 468.0 | -1.2 [-2.7, +0.2] |
| `seq3` | 478.5 | +3.7 [+2.3, +5.2] | 2.31 [2.22, 2.40] | 470.4 | -1.6 [-3.0, -0.2] |
| `seq4_stop2000` | 479.8 | +4.0 [+2.3, +5.6] | 2.32 [2.19, 2.45] | 474.1 | -1.1 [-2.7, +0.5] |
| `seq4_stop1000` | 480.0 | +4.0 [+2.4, +5.7] | 2.41 [2.28, 2.53] | 474.0 | -1.2 [-2.8, +0.4] |
| `seq4` | 480.8 | +4.2 [+2.6, +5.8] | 2.44 [2.31, 2.56] | 474.3 | -1.3 [-2.9, +0.3] |
| `seq4_short` | 480.5 | +4.1 [+2.5, +5.8] | 2.44 [2.31, 2.56] | 474.5 | -1.2 [-2.8, +0.4] |
| `seq4_restart` | 480.8 | +4.2 [+2.6, +5.8] | 2.44 [2.31, 2.56] | 476.1 | -0.9 [-2.5, +0.6] |
| `seq4_restart_short` | 480.5 | +4.1 [+2.5, +5.8] | 2.44 [2.31, 2.56] | 475.0 | -1.1 [-2.8, +0.5] |
| `seq4_L12000` | 476.0 | +3.2 [+1.8, +4.6] | 2.51 [2.39, 2.63] | 472.8 | -0.7 [-2.0, +0.7] |
| `seq_2then4` | 480.8 | +4.2 [+2.6, +5.8] | 2.54 [2.41, 2.68] | 474.3 | -1.3 [-2.9, +0.3] |
| `seq_2then4_short` | 480.8 | +4.2 [+2.6, +5.9] | 2.54 [2.41, 2.68] | 474.8 | -1.2 [-2.8, +0.4] |
| `seq4_L8000` | 470.5 | +2.1 [+0.8, +3.4] | 2.55 [2.46, 2.65] | 467.0 | -0.7 [-2.1, +0.7] |
| `vote3` | 478.5 | +3.7 [+2.3, +5.2] | 3.12 [3.03, 3.21] | 470.4 | -1.6 [-3.0, -0.2] |
| `vote3_short` | 479.1 | +3.8 [+2.3, +5.4] | 3.12 [3.03, 3.21] | 472.7 | -1.3 [-2.8, +0.1] |
| `par4_m2` | 481.2 | +4.2 [+2.6, +5.9] | 3.53 [3.42, 3.64] | 473.8 | -1.5 [-3.2, +0.2] |
| `vote4` | 480.8 | +4.2 [+2.6, +5.8] | 4.16 [4.04, 4.28] | 474.3 | -1.3 [-2.9, +0.3] |
| `vote4_short` | 481.0 | +4.2 [+2.6, +5.9] | 4.16 [4.04, 4.28] | 475.0 | -1.2 [-2.8, +0.4] |
| `vote4_restart` | 480.8 | +4.2 [+2.6, +5.8] | 4.16 [4.04, 4.28] | 476.1 | -0.9 [-2.5, +0.6] |
| `vote4_restart_short` | 481.0 | +4.2 [+2.6, +5.9] | 4.16 [4.04, 4.28] | 475.0 | -1.2 [-3.0, +0.4] |

## Rule chosen per token budget (5 folds: chosen on 4, scored on the 5th)

| Model | Budget | Chosen on all | Chosen per fold | Held-out right (24) | Held-out tokens |
|---|---|---|---|---|---|
| base | 5,000 | `single` | single, single, single, single, single | 460.2 | 4,876 |
| base | 7,500 | `R12000` | R12000, R12000, R12000, R12000, R12000 | 469.5 | 6,885 |
| base | 10,000 | `vote2_short` | vote2_short, vote2_short, vote2_short, vote2_short, vote2_short | 474.1 | 9,751 |
| base | 12,500 | `seq_2then4_short` | seq_2then4_short, seq4, seq_2then4_short, seq_2then4_short, seq4 | 480.4 | 11,669 |
| base | 15,000 | `seq_2then4_short` | seq_2then4_short, seq4, seq_2then4_short, seq_2then4_short, seq4 | 480.4 | 11,669 |
| base | 17,500 | `seq_2then4_short` | seq_2then4_short, seq4, seq_2then4_short, seq_2then4_short, seq4 | 480.4 | 11,669 |
| base | 20,000 | `vote4_short` | vote4_short, seq4, vote4_short, vote4_short, seq4 | 480.2 | 16,072 |
| rl | 5,000 | `restart` | restart, restart, single, single, restart | 462.8 | 4,909 |
| rl | 7,500 | `R12000` | R12000, R12000, R12000, R12000, R12000 | 466.2 | 6,225 |
| rl | 10,000 | `vote2_short` | vote2_short, vote2_short, vote2_short, vote2_short, vote2_short | 468.0 | 9,374 |
| rl | 12,500 | `seq4_restart` | seq4_restart, seq4_short, seq4_restart, seq4_restart, seq4_restart | 474.3 | 11,625 |
| rl | 15,000 | `seq4_restart` | seq4_restart, seq4_short, seq4_restart, seq4_restart, seq4_restart | 474.3 | 11,625 |
| rl | 17,500 | `seq4_restart` | seq4_restart, seq4_short, seq4_restart, seq4_restart, seq4_restart | 474.3 | 11,625 |
| rl | 20,000 | `seq4_restart` | seq4_restart, seq4_short, seq4_restart, seq4_restart, seq4_restart | 474.3 | 11,625 |
