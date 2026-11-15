| Method | Right of 500 | Hazard ratio against base + cue [95 %] | Hazard ratio against its own single sample [95 %] | Logit shift [95 %] | Tokens per problem |
|---|---|---|---|---|---|
| RL plain, vote over 4 after restart | 475 | 0.19 [0.13, 0.26] | 0.57 [0.43, 0.71] | +2.35 [+1.99, +2.78] | 19864 |
| RL plain, vote over 4 samples | 474 | 0.20 [0.14, 0.28] | 0.60 [0.46, 0.74] | +2.28 [+1.91, +2.70] | 18747 |
| RL plain, vote over 3 samples (mean of the 4 subsets) | 468.5 | 0.25 [0.19, 0.32] | 0.76 [0.65, 0.86] | +1.95 [+1.68, +2.27] | 14060 |
| RL-Zero-Math 3.1 plain, sample 2 | 464 | 0.29 [0.21, 0.39] |  | +1.71 [+1.34, +2.13] | 4741 |
| RL-Zero-Math 3.1 plain, sample 1 | 462 | 0.30 [0.22, 0.41] |  | +1.61 [+1.21, +2.04] | 4588 |
| rl_plain, 4 samples pooled | 460 | 0.33 [0.28, 0.40] |  | +1.52 [+1.30, +1.75] |  |
| RL plain, vote over 2 samples (mean of the 6 subsets) | 459.7 | 0.34 [0.27, 0.41] | 1.01 [0.92, 1.10] | +1.50 [+1.26, +1.77] | 9374 |
| RL-Zero-Math 3.1 plain, sample 3 | 458 | 0.35 [0.27, 0.46] |  | +1.43 [+1.08, +1.82] | 4743 |
| RL plain, restart up to 2 | 458 | 0.36 [0.27, 0.47] | 0.94 [0.85, 1.00] | +1.43 [+1.09, +1.79] | 4899 |
| RL-Zero-Math 3.1, cue | 457 | 0.37 [0.27, 0.48] |  | +1.39 [+1.01, +1.78] | 4696 |
| Olmo-3-7B-Think-SFT, cue | 454 | 0.37 [0.27, 0.49] |  | +1.26 [+0.85, +1.71] | 4888 |
| RL-Zero-Math 3.1 plain, sample 0 | 456 | 0.39 [0.29, 0.50] |  | +1.34 [+1.03, +1.72] | 4675 |
| base + 1.5 (RL - base), cue | 453 | 0.41 [0.31, 0.52] |  | +1.22 [+0.88, +1.60] | 4862 |
| base + cue, vote over 4, ties to the shortest finished answer | 453 | 0.42 [0.34, 0.51] | 0.42 [0.34, 0.51] | +1.22 [+0.96, +1.53] | 16034 |
| base + 0.5 (RL - base), cue | 452 | 0.43 [0.32, 0.55] |  | +1.18 [+0.84, +1.55] | 4626 |
| base + 0.75 (RL - base), cue | 451 | 0.43 [0.32, 0.57] |  | +1.15 [+0.78, +1.52] | 4654 |
| RL-Zero-Code 3.1, cue | 450 | 0.44 [0.32, 0.57] |  | +1.11 [+0.74, +1.52] | 3336 |
| base + 1.25 (RL - base), cue | 450 | 0.45 [0.33, 0.59] |  | +1.11 [+0.77, +1.52] | 4852 |
| base + cue, vote over 4 after restart | 450 | 0.45 [0.35, 0.55] | 0.45 [0.35, 0.55] | +1.11 [+0.85, +1.43] | 19697 |
| Olmo-3-7B-RL-Zero-Math (3.0), cue | 448 | 0.46 [0.34, 0.60] |  | +1.03 [+0.66, +1.44] | 4527 |
| Olmo-3-7B-Think-SFT, plain | 440 | 0.47 [0.34, 0.64] |  | +0.77 [+0.34, +1.22] | 4492 |
| base + cue, vote over 4 samples | 446 | 0.51 [0.42, 0.61] | 0.51 [0.42, 0.61] | +0.96 [+0.74, +1.24] | 16034 |
| base + 0.5 (RL - base), plain | 443 | 0.52 [0.40, 0.67] |  | +0.86 [+0.52, +1.22] | 4536 |
| Olmo-3-7B-RL-Zero-Math (3.0), plain | 443 | 0.54 [0.41, 0.70] |  | +0.86 [+0.51, +1.23] | 4506 |
| base + 0.25 (RL - base), cue | 441 | 0.56 [0.44, 0.73] |  | +0.80 [+0.46, +1.13] | 4036 |
| base + cue, vote over 3 samples (mean of the 4 subsets) | 441.5 | 0.57 [0.50, 0.64] | 0.57 [0.50, 0.64] | +0.81 [+0.65, +0.99] | 12025 |
| Olmo-3-7B-RL-Zero-Mix (3.0), cue | 440 | 0.57 [0.43, 0.74] |  | +0.77 [+0.43, +1.13] | 5203 |
| base + cue + 3 solved problems written by Math-RL in context (n 497) | 437.6 | 0.59 [0.46, 0.74] |  | +0.70 [+0.39, +1.04] | 4379 |
| base + top 8 singular directions per matrix of the RL delta, plain | 427 | 0.65 [0.48, 0.87] |  | +0.39 [+0.02, +0.80] | 3962 |
| Olmo-3-7B-RL-Zero-General (3.0), cue | 429 | 0.71 [0.55, 0.90] |  | +0.45 [+0.14, +0.79] | 3839 |
| base + random difference of the RL norm, cue (control) | 417 | 0.85 [0.66, 1.09] |  | +0.15 [-0.17, +0.46] | 3944 |
| base + cue, sample 3 | 418 | 0.86 [0.70, 1.04] |  | +0.17 [-0.07, +0.45] | 4156 |
| base + cue, vote over 2 samples (mean of the 6 subsets) | 418.5 | 0.87 [0.80, 0.94] | 0.87 [0.80, 0.94] | +0.18 [+0.07, +0.30] | 8017 |
| base + cue + 3 solved problems written by the cued base in context (n 497) | 416.5 | 0.88 [0.68, 1.13] |  | +0.14 [-0.16, +0.47] | 3365 |
| base + cue + 3 solved problems written by Code-RL in context (n 497) | 414.5 | 0.92 [0.71, 1.17] |  | +0.10 [-0.20, +0.41] | 3815 |
| base + cue, restart up to 2 | 413 | 0.95 [0.78, 1.15] | 0.86 [0.77, 0.95] | +0.06 [-0.19, +0.32] | 4852 |
| Olmo-3-7B-RL-Zero-Code (3.0), cue | 411 | 0.95 [0.74, 1.22] |  | +0.01 [-0.27, +0.36] | 3069 |
| base_cue, 4 samples pooled | 410.5 | 1.00 [1.00, 1.00] |  | +0.00 [+0.00, +0.00] |  |
| base + 0.25 (RL - base), plain | 405 | 1.00 [0.77, 1.30] |  | -0.12 [-0.43, +0.22] | 3653 |
| base + cue, sample 1 | 409 | 1.03 [0.86, 1.22] |  | -0.03 [-0.24, +0.19] | 4144 |
| base + cue, sample 2 | 410 | 1.03 [0.85, 1.23] |  | -0.01 [-0.23, +0.24] | 3926 |
| base + cue, sample 0 | 405 | 1.10 [0.92, 1.30] |  | -0.12 [-0.34, +0.11] | 3808 |
| RL-Zero-Code 3.1, plain | 390 | 1.19 [0.92, 1.55] |  | -0.40 [-0.73, -0.07] | 3066 |
| Olmo-3-7B-RL-Zero-If (3.0), cue | 377 | 1.54 [1.23, 1.93] |  | -0.63 [-0.90, -0.35] | 2667 |
| Olmo-3-7B-RL-Zero-Mix (3.0), plain | 372 | 1.59 [1.25, 2.03] |  | -0.71 [-1.00, -0.40] | 4228 |
| Olmo-3-7B-RL-Zero-Code (3.0), plain | 360 | 1.99 [1.60, 2.46] |  | -0.89 [-1.16, -0.62] | 2630 |
| Olmo-3-7B-RL-Zero-General (3.0), plain | 323 | 2.63 [2.09, 3.29] |  | -1.39 [-1.65, -1.10] | 2303 |
| base + random rank-8 directions, plain (control) | 197 | 7.11 [5.71, 9.01] |  | -2.79 [-3.05, -2.53] | 1968 |
| Olmo-3-7B-RL-Zero-If (3.0), plain | 55 | 27.05 [22.67, 32.95] |  | -4.77 [-5.12, -4.46] | 39 |
