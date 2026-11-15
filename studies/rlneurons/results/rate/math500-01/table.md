| Method | Right | Shift, logits [95 %] | Tokens per problem | Signal | Logits per 1,000 extra tokens |
|---|---|---|---|---|---|
| RL plain, vote over 4 after restart | 475 of 500 | +2.46 [+2.03, +2.92] | 19,864 | RL reward (weights) | 0.055 (+0.83 over its own single sample, 15,177 extra) |
| RL plain, vote over 4 samples | 474 of 500 | +2.40 [+1.95, +2.84] | 18,747 | RL reward (weights) | 0.054 (+0.76 over its own single sample, 14,060 extra) |
| RL plain, vote over 3 samples (mean of the 4 subsets) | 468.5 of 500 | +2.07 [+1.71, +2.43] | 14,060 | RL reward (weights) | 0.046 (+0.43 over its own single sample, 9,374 extra) |
| RL-Zero-Math 3.1 plain, sample 2 | 464 of 500 | +1.83 [+1.36, +2.29] | 4,741 | RL reward (weights) |  |
| RL-Zero-Math 3.1 plain, sample 1 | 462 of 500 | +1.73 [+1.25, +2.24] | 4,588 | RL reward (weights) |  |
| RL plain, vote over 2 samples (mean of the 6 subsets) | 459.7 of 500 | +1.62 [+1.28, +1.95] | 9,374 | RL reward (weights) | -0.003 (-0.01 over its own single sample, 4,687 extra) |
| RL-Zero-Math 3.1 plain, sample 3 | 458 of 500 | +1.55 [+1.12, +1.99] | 4,743 | RL reward (weights) |  |
| RL plain, restart up to 2 | 458 of 500 | +1.55 [+1.13, +1.94] | 4,899 | RL reward (weights) | 0.383 (+0.09 over its own single sample, 224 extra) |
| RL-Zero-Math 3.1, cue | 457 of 500 | +1.50 [+1.06, +1.94] | 4,696 | RL reward (weights) |  |
| RL-Zero-Math 3.1 plain, sample 0 | 456 of 500 | +1.46 [+1.07, +1.86] | 4,675 | RL reward (weights) |  |
| Olmo-3-7B-Think-SFT, cue | 454 of 500 | +1.38 [+0.91, +1.87] | 4,888 | SFT data |  |
| base + 1.5 (RL - base), cue | 453 of 500 | +1.34 [+0.90, +1.78] | 4,862 | RL reward (weights) |  |
| base + cue, vote over 4, ties to the shortest finished answer | 453 of 500 | +1.34 [+1.01, +1.71] | 16,034 | none | 0.102 (+1.22 over its own single sample, 12,025 extra) |
| base + 0.5 (RL - base), cue | 452 of 500 | +1.30 [+0.87, +1.75] | 4,626 | RL reward (weights) |  |
| base + 0.75 (RL - base), cue | 451 of 500 | +1.26 [+0.81, +1.70] | 4,654 | RL reward (weights) |  |
| base + 1.25 (RL - base), cue | 450 of 500 | +1.22 [+0.81, +1.65] | 4,852 | RL reward (weights) |  |
| RL-Zero-Code 3.1, cue | 450 of 500 | +1.22 [+0.79, +1.66] | 3,336 | RL reward (weights) |  |
| base + cue, vote over 4 after restart | 450 of 500 | +1.22 [+0.90, +1.58] | 19,697 | none | 0.071 (+1.11 over its own single sample, 15,689 extra) |
| Olmo-3-7B-RL-Zero-Math (3.0), cue | 448 of 500 | +1.15 [+0.69, +1.58] | 4,527 | RL reward (weights) |  |
| base + cue, vote over 4 samples | 446 of 500 | +1.08 [+0.79, +1.40] | 16,034 | none | 0.080 (+0.96 over its own single sample, 12,025 extra) |
| base + 0.5 (RL - base), plain | 443 of 500 | +0.98 [+0.58, +1.40] | 4,536 | RL reward (weights) |  |
| Olmo-3-7B-RL-Zero-Math (3.0), plain | 443 of 500 | +0.98 [+0.56, +1.37] | 4,506 | RL reward (weights) |  |
| base + cue, vote over 3 samples (mean of the 4 subsets) | 441.5 of 500 | +0.93 [+0.66, +1.19] | 12,025 | none | 0.101 (+0.81 over its own single sample, 8,017 extra) |
| base + 0.25 (RL - base), cue | 441 of 500 | +0.91 [+0.52, +1.28] | 4,036 | RL reward (weights) |  |
| Olmo-3-7B-RL-Zero-Mix (3.0), cue | 440 of 500 | +0.88 [+0.48, +1.31] | 5,203 | RL reward (weights) |  |
| Olmo-3-7B-Think-SFT, plain | 440 of 500 | +0.88 [+0.40, +1.36] | 4,492 | SFT data |  |
| base + cue + 3 solved problems written by Math-RL in context (n 497) | 435 of 497 | +0.81 [+0.43, +1.20] | 4,379 | RL reward (RL text in context) |  |
| Olmo-3-7B-RL-Zero-General (3.0), cue | 429 of 500 | +0.56 [+0.17, +0.95] | 3,839 | RL reward (weights) |  |
| base + top 8 singular directions per matrix of the RL delta, plain | 427 of 500 | +0.51 [+0.05, +0.97] | 3,962 | RL reward (weights) |  |
| base + cue, vote over 2 samples (mean of the 6 subsets) | 418.5 of 500 | +0.30 [+0.10, +0.48] | 8,017 | none | 0.045 (+0.18 over its own single sample, 4,008 extra) |
| base + cue, sample 3 | 418 of 500 | +0.28 [-0.09, +0.70] | 4,156 | none |  |
| base + random difference of the RL norm, cue (control) | 417 of 500 | +0.26 [-0.11, +0.63] | 3,944 | none (control) |  |
| base + cue + 3 solved problems written by the cued base in context (n 497) | 414 of 497 | +0.26 [-0.12, +0.62] | 3,365 | own samples (in context) |  |
| base + cue + 3 solved problems written by Code-RL in context (n 497) | 412 of 497 | +0.21 [-0.15, +0.61] | 3,815 | RL reward (RL text in context) |  |
| base + cue, restart up to 2 | 413 of 500 | +0.17 [+0.06, +0.31] | 4,852 | none | 0.164 (+0.17 over its own single sample, 1,044 extra) |
| Olmo-3-7B-RL-Zero-Code (3.0), cue | 411 of 500 | +0.13 [-0.26, +0.53] | 3,069 | RL reward (weights) |  |
| base + cue, sample 2 | 410 of 500 | +0.10 [-0.26, +0.48] | 3,926 | none |  |
| base + cue, sample 1 | 409 of 500 | +0.08 [-0.27, +0.43] | 4,144 | none |  |
| base + cue, sample 0 | 405 of 500 | +0.00 [+0.00, +0.00] | 3,808 | none |  |
| base + 0.25 (RL - base), plain | 405 of 500 | +0.00 [-0.38, +0.38] | 3,653 | RL reward (weights) |  |
| RL-Zero-Code 3.1, plain | 390 of 500 | -0.29 [-0.70, +0.09] | 3,066 | RL reward (weights) |  |
| Olmo-3-7B-RL-Zero-If (3.0), cue | 377 of 500 | -0.51 [-0.88, -0.17] | 2,667 | RL reward (weights) |  |
| Olmo-3-7B-RL-Zero-Mix (3.0), plain | 372 of 500 | -0.59 [-0.97, -0.20] | 4,228 | RL reward (weights) |  |
| Olmo-3-7B-RL-Zero-Code (3.0), plain | 360 of 500 | -0.77 [-1.12, -0.42] | 2,630 | RL reward (weights) |  |
| Olmo-3-7B-RL-Zero-General (3.0), plain | 323 of 500 | -1.27 [-1.63, -0.92] | 2,303 | RL reward (weights) |  |
| base + random rank-8 directions, plain (control) | 197 of 500 | -2.67 [-3.04, -2.34] | 1,968 | none (control) |  |
| Olmo-3-7B-RL-Zero-If (3.0), plain | 55 of 500 | -4.65 [-5.05, -4.28] | 39 | RL reward (weights) |  |
