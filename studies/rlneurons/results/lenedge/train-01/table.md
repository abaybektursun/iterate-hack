# Length edge: training assistant turns of allenai/Dolci-Think-SFT-7B against Think-SFT's generated answers

2,268,178 rows, 2,368,984 assistant turns. A turn is the assistant message's content, thinking and answer together. Token lengths: the 118,463 assistant turns of a fixed 5 % of rows chosen by a hash of the row id (tokenizer of allenai/Olmo-3-7B-Think-SFT); they hold 1.103 billion tokens, so all turns hold about 22.1 billion. Chinese counts: all turns.

## Tokens per assistant turn (the 5 % sample)

| Group | Turns | Mean | 50th | 90th | 99th | 99.9th | Max | at least 8,000 | 12,000 | 13,589 | 16,384 | 32,768 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 118,463 | 9,313 | 5,698 | 23,558 | 30,365 | 32,372 | 33,293 | 44.81 % | 36.66 % | 32.65 % | 23.64 % | 0.03 % |
| math subset | 37,523 | 19,061 | 18,703 | 27,483 | 31,395 | 32,663 | 33,230 | 97.64 % | 87.74 % | 79.97 % | 60.42 % | 0.06 % |
| math subset or keyword | 42,944 | 18,152 | 17,665 | 27,262 | 31,345 | 32,663 | 33,293 | 93.38 % | 82.21 % | 74.50 % | 55.90 % | 0.06 % |
| not math (neither) | 75,519 | 4,286 | 1,741 | 12,605 | 26,048 | 31,608 | 32,969 | 17.19 % | 10.76 % | 8.85 % | 5.29 % | 0.02 % |
| allenai/SYNTHETIC-2-SFT-cn-fltrd-final-ngram-filtered-chinese-filtered | 5,166 | 8,063 | 6,464 | 17,304 | 29,169 | 32,173 | 33,228 | 41.41 % | 22.07 % | 17.02 % | 11.42 % | 0.02 % |
| allenai/aya-100k-r1-format-filtered-keyword-filtered-filter-datecutoff-ngram-filtered | 4,967 | 1,658 | 1,233 | 3,374 | 6,421 | 9,724 | 12,367 | 0.28 % | 0.02 % | 0.00 % | 0.00 % | 0.00 % |
| allenai/coconot-r1-format-domain-filtered-keyword-filtered-filter-datecutoff-chinese-filtered | 560 | 857 | 748 | 1,299 | 2,811 | 5,089 | 5,812 | 0.00 % | 0.00 % | 0.00 % | 0.00 % | 0.00 % |
| allenai/nemotron-post-training-dataset-subset-ngram-filtered-no-tool-calls | 5,672 | 12,926 | 11,954 | 24,917 | 31,333 | 32,645 | 32,767 | 65.94 % | 49.82 % | 44.09 % | 34.80 % | 0.00 % |
| allenai/oasst1-r1-format-filtered-keyword-filtered-filter-datecutoff-chinese-filtered | 509 | 1,014 | 965 | 1,802 | 4,238 | 6,404 | 6,454 | 0.00 % | 0.00 % | 0.00 % | 0.00 % | 0.00 % |
| allenai/persona-precise-if-r1-final-content-filtered-chinese-filtered | 11,099 | 1,399 | 876 | 3,052 | 7,634 | 13,074 | 18,802 | 0.78 % | 0.16 % | 0.07 % | 0.01 % | 0.00 % |
| allenai/tablegpt_r1-format-filtered-keyword-filtered-filter-datecutoff | 227 | 1,335 | 882 | 2,821 | 7,091 | 10,533 | 11,497 | 0.44 % | 0.00 % | 0.00 % | 0.00 % | 0.00 % |
| allenai/tulu_v3.9_wildchat_100k_english-r1-final-content-filtered | 5,239 | 1,124 | 720 | 2,307 | 7,478 | 11,365 | 18,935 | 0.76 % | 0.04 % | 0.02 % | 0.02 % | 0.00 % |
| allenai/wildchat-r1-p2-repetition-filter | 4,236 | 1,122 | 700 | 2,358 | 7,175 | 11,113 | 16,658 | 0.66 % | 0.07 % | 0.05 % | 0.05 % | 0.00 % |
| allenai/wildguardmix-r1-v2-all-filtered-ngram-filtered-chinese-filtered | 1,959 | 705 | 611 | 1,047 | 2,184 | 5,093 | 7,035 | 0.00 % | 0.00 % | 0.00 % | 0.00 % | 0.00 % |
| allenai/wildjailbreak-r1-v2-format-filtered-keyword-filtered-filter-datecutoff-final-content-filtered | 2,068 | 592 | 558 | 838 | 1,130 | 1,524 | 1,738 | 0.00 % | 0.00 % | 0.00 % | 0.00 % | 0.00 % |
| saumyamalik/OpenThoughts3-full-filtered-code-subsampled-decontam-v2 | 4,358 | 17,028 | 15,919 | 25,632 | 31,574 | 32,868 | 33,293 | 94.86 % | 84.86 % | 74.92 % | 41.44 % | 0.30 % |
| saumyamalik/OpenThoughts3-full-filtered-math-decontam-v2 | 37,523 | 19,061 | 18,703 | 27,483 | 31,395 | 32,663 | 33,230 | 97.64 % | 87.74 % | 79.97 % | 60.42 % | 0.06 % |
| saumyamalik/OpenThoughts3-full-filtered-science-decontam-v2 | 4,946 | 8,685 | 7,562 | 16,039 | 26,234 | 30,982 | 32,842 | 47.21 % | 26.04 % | 19.31 % | 8.69 % | 0.04 % |
| saumyamalik/correct-python-sft-187k-x16-thoughts-filtered-decontam-v2 | 23,270 | 4,175 | 2,814 | 9,344 | 18,547 | 25,782 | 31,330 | 14.06 % | 5.29 % | 3.62 % | 1.75 % | 0.00 % |
| saumyamalik/if_qwq_reasoning_verified_filtered_decontam_v2 | 6,664 | 3,058 | 1,442 | 7,907 | 19,002 | 26,788 | 33,195 | 9.84 % | 4.58 % | 3.20 % | 1.77 % | 0.03 % |

## Chinese in assistant turns (flagged: more than 20 Chinese characters; English prompt: the user turn before holds at most 20)

| Group | Turns | Flagged | English-prompt turns | of them flagged | with a non-Latin episode | First Chinese character: share of the turn before it, quartiles | its token, quartiles | first inside the thinking | Chinese share of the turn's characters: median, max |
|---|---|---|---|---|---|---|---|---|---|
| all | 2,368,984 | 269,096 (11.359 %) | 2,365,585 | 266,162 (11.251 %) | 359,236 (15.186 %) | 0.651 / 0.777 / 0.864 | 12,753 / 17,493 / 21,219 | 264,454 | 0.41 %, 97.83 % |
| math subset | 752,997 | 197,543 (26.234 %) | 752,997 | 197,543 (26.234 %) | 217,866 (28.933 %) | 0.718 / 0.809 / 0.88 | 15,803 / 19,282 / 22,200 | 197,485 | 0.42 %, 38.86 % |
| math subset or keyword | 864,609 | 205,103 (23.722 %) | 864,576 | 205,071 (23.719 %) | 226,840 (26.237 %) | 0.711 / 0.806 / 0.878 | 15,462 / 19,109 / 22,098 | 204,963 | 0.42 %, 56.48 % |
| not math (neither) | 1,504,375 | 63,993 (4.254 %) | 1,501,009 | 61,091 (4.070 %) | 132,396 (8.820 %) | 0.432 / 0.609 / 0.748 | 6,369 / 10,844 / 13,788 | 59,491 | 0.36 %, 97.83 % |
| allenai/SYNTHETIC-2-SFT-cn-fltrd-final-ngram-filtered-chinese-filtered | 104,569 | 131 (0.125 %) | 104,495 | 94 (0.090 %) | 425 (0.407 %) | 0.029 / 0.115 / 0.841 | 290 / 1,119 / 7,078 | 73 | 0.40 %, 4.84 % |
| allenai/aya-100k-r1-format-filtered-keyword-filtered-filter-datecutoff-ngram-filtered | 98,597 | 5,671 (5.752 %) | 96,560 | 3,641 (3.771 %) | 47,392 (49.080 %) | 0.006 / 0.01 / 0.017 | 3 / 6 / 13 | 2,899 | 55.85 %, 87.83 % |
| allenai/coconot-r1-format-domain-filtered-keyword-filtered-filter-datecutoff-chinese-filtered | 10,227 | 15 (0.147 %) | 10,227 | 15 (0.147 %) | 86 (0.841 %) | 0.055 / 0.18 / 0.462 | 70 / 269 / 369 | 10 | 1.02 %, 2.99 % |
| allenai/nemotron-post-training-dataset-subset-ngram-filtered-no-tool-calls | 113,777 | 42 (0.037 %) | 113,767 | 39 (0.034 %) | 967 (0.850 %) | 0.416 / 0.645 / 0.871 | 7,768 / 10,715 / 16,901 | 38 | 0.06 %, 3.42 % |
| allenai/oasst1-r1-format-filtered-keyword-filtered-filter-datecutoff-chinese-filtered | 9,295 | 9 (0.097 %) | 9,294 | 8 (0.086 %) | 957 (10.297 %) | 0.187 / 0.409 / 0.92 | 84 / 199 / 296 | 4 | 3.34 %, 58.06 % |
| allenai/persona-precise-if-r1-final-content-filtered-chinese-filtered | 223,123 | 126 (0.056 %) | 223,123 | 126 (0.056 %) | 641 (0.287 %) | 0.21 / 0.442 / 0.76 | 236 / 430 / 1,415 | 82 | 1.38 %, 5.00 % |
| allenai/tablegpt_r1-format-filtered-keyword-filtered-filter-datecutoff | 4,981 | 4 (0.080 %) | 4,971 | 1 (0.020 %) | 11 (0.221 %) | 0.439 / 0.439 / 0.439 | 2,147 / 2,147 / 2,147 | 1 | 0.45 %, 0.45 % |
| allenai/tulu_v3.9_wildchat_100k_english-r1-final-content-filtered | 101,259 | 1,336 (1.319 %) | 100,762 | 1,031 (1.023 %) | 4,731 (4.695 %) | 0.0 / 0.002 / 0.044 | 0 / 3 / 19 | 919 | 36.27 %, 97.83 % |
| allenai/wildchat-r1-p2-repetition-filter | 80,106 | 1,114 (1.391 %) | 79,693 | 851 (1.068 %) | 3,781 (4.744 %) | 0.0 / 0.002 / 0.034 | 0 / 3 / 14 | 772 | 38.77 %, 96.43 % |
| allenai/wildguardmix-r1-v2-all-filtered-ngram-filtered-chinese-filtered | 38,315 | 20 (0.052 %) | 38,304 | 13 (0.034 %) | 110 (0.287 %) | 0.016 / 0.21 / 0.63 | 15 / 258 / 360 | 6 | 0.94 %, 2.90 % |
| allenai/wildjailbreak-r1-v2-format-filtered-keyword-filtered-filter-datecutoff-final-content-filtered | 41,100 | 2 (0.005 %) | 41,100 | 2 (0.005 %) | 10 (0.024 %) | 0.658 / 0.752 / 0.845 | 976 / 1,643 / 2,310 | 0 | 2.44 %, 3.91 % |
| saumyamalik/OpenThoughts3-full-filtered-code-subsampled-decontam-v2 | 88,900 | 44,424 (49.971 %) | 88,841 | 44,365 (49.938 %) | 48,262 (54.324 %) | 0.49 / 0.617 / 0.739 | 8,899 / 11,715 / 14,385 | 44,269 | 0.30 %, 35.59 % |
| saumyamalik/OpenThoughts3-full-filtered-math-decontam-v2 | 752,997 | 197,543 (26.234 %) | 752,997 | 197,543 (26.234 %) | 217,866 (28.933 %) | 0.718 / 0.809 / 0.88 | 15,803 / 19,282 / 22,200 | 197,485 | 0.42 %, 38.86 % |
| saumyamalik/OpenThoughts3-full-filtered-science-decontam-v2 | 99,269 | 8,721 (8.785 %) | 99,205 | 8,657 (8.726 %) | 11,720 (11.814 %) | 0.438 / 0.696 / 0.832 | 5,314 / 10,117 / 14,315 | 8,499 | 0.50 %, 66.92 % |
| saumyamalik/correct-python-sft-187k-x16-thoughts-filtered-decontam-v2 | 466,677 | 7,828 (1.677 %) | 466,653 | 7,804 (1.672 %) | 11,140 (2.387 %) | 0.57 / 0.689 / 0.793 | 9,431 / 11,685 / 13,910 | 7,676 | 0.21 %, 5.00 % |
| saumyamalik/if_qwq_reasoning_verified_filtered_decontam_v2 | 135,792 | 2,110 (1.554 %) | 135,593 | 1,972 (1.454 %) | 11,137 (8.214 %) | 0.333 / 0.692 / 0.852 | 503 / 7,279 / 14,252 | 1,721 | 0.60 %, 4.99 % |

## Generated answers against training turns, by length bin

Generated: Think-SFT + cue, hard328, 4 samples, cap 32,768 (`results/cap32vote/hard328_sft1_cue_s4-01/rows.jsonl`, 1,312 samples): finished answers whose length falls in the bin. Training (the 5 % sample): S = share of assistant turns with at least the bin's lower edge of tokens; flagged = English-prompt turns that end in the bin and hold more than 20 Chinese characters.

| Tokens | Generated: right / finished, precision | Generated: with Chinese | Training S, all | Training S, math subset | Training turns ending in the bin, all | of them flagged (English prompt) | math subset: flagged |
|---|---|---|---|---|---|---|---|
| 0 to 2,000 | 68 / 68, 100.0 % | 0 (0.0 %) | 100.00 % | 100.00 % | 40,764 | 290 (0.713 %) | 0 (0.000 %) |
| 2,000 to 4,000 | 189 / 191, 99.0 % | 0 (0.0 %) | 65.59 % | 100.00 % | 12,420 | 102 (0.824 %) | 0 (0.000 %) |
| 4,000 to 6,000 | 165 / 167, 98.8 % | 1 (0.6 %) | 55.10 % | 99.87 % | 6,913 | 33 (0.478 %) | 0 (0.000 %) |
| 6,000 to 8,000 | 120 / 127, 94.5 % | 0 (0.0 %) | 49.27 % | 99.39 % | 5,285 | 23 (0.436 %) | 2 (0.303 %) |
| 8,000 to 10,000 | 83 / 96, 86.5 % | 0 (0.0 %) | 44.81 % | 97.64 % | 4,719 | 50 (1.060 %) | 1 (0.076 %) |
| 10,000 to 12,000 | 81 / 94, 86.2 % | 3 (3.2 %) | 40.82 % | 94.13 % | 4,928 | 141 (2.861 %) | 32 (1.334 %) |
| 12,000 to 14,000 | 65 / 80, 81.2 % | 6 (7.5 %) | 36.66 % | 87.74 % | 6,165 | 461 (7.478 %) | 150 (3.908 %) |
| 14,000 to 16,384 | 61 / 121, 50.4 % | 28 (23.1 %) | 31.46 % | 77.51 % | 9,270 | 1,559 (16.820 %) | 700 (10.915 %) |
| 16,384 to 20,000 | 54 / 130, 41.5 % | 61 (46.9 %) | 23.64 % | 60.42 % | 8,000 | 1,261 (15.764 %) | 835 (13.820 %) |
| 20,000 to 24,000 | 28 / 137, 20.4 % | 98 (71.5 %) | 16.88 % | 44.31 % | 9,103 | 2,907 (31.938 %) | 2,347 (31.850 %) |
| 24,000 to 28,000 | 11 / 70, 15.7 % | 62 (88.6 %) | 9.20 % | 24.68 % | 7,196 | 3,919 (54.461 %) | 3,488 (56.504 %) |
| 28,000 to 32,768 | 3 / 25, 12.0 % | 24 (96.0 %) | 3.12 % | 8.22 % | 3,660 | 2,565 (70.101 %) | 2,337 (76.273 %) |

- spearman_survival_all_vs_precision: {"rho": 1.0, "p_permutation_two_sided": 0.0, "bins": 12}
- spearman_survival_math_vs_precision: {"rho": 1.0, "p_permutation_two_sided": 0.0, "bins": 12}
- spearman_survival_all_vs_generated_chinese_share: {"rho": -0.947, "p_permutation_two_sided": 0.0, "bins": 12}
- spearman_bin_index_vs_precision_baseline: {"rho": 1.0, "p_permutation_two_sided": 0.0, "bins": 12}
- first_bin_with_precision_under_90: {"tokens": [8000, 10000], "training_survival_all": 0.44808083536631693, "training_survival_math": 0.9763611651520401}
- first_bin_with_generated_chinese_over_10: {"tokens": [14000, 16384], "training_survival_all": 0.3146045600736095, "training_survival_math": 0.7750712896090398}

## First switch to a non-Latin script, by position (`drift.episodes`, the token of the 5th letter)

Per bin: answers or turns that reach the bin with no switch yet, and those whose first switch is inside it. Generated: `runs/drift_features` (hard328, cap 16,384, 4 samples; `cap32_sft`: one sample per problem at cap 32,768). Training: English-prompt assistant turns of the 5 % sample.

| Tokens | Think-SFT cap 16,384 | Think-SFT cap 32,768 | RL plain | base + cue | Training, all | Training, math subset |
|---|---|---|---|---|---|---|
| 0 to 2,000 | 7 / 1,312 (0.53 %) | 0 / 328 (0.00 %) | 1 / 1,312 (0.08 %) | 0 / 1,312 (0.00 %) | 3,643 / 118,285 (3.080 %) | 28 / 37,523 (0.07 %) |
| 2,000 to 4,000 | 9 / 1,228 (0.73 %) | 0 / 312 (0.00 %) | 2 / 1,252 (0.16 %) | 1 / 1,130 (0.09 %) | 165 / 76,152 (0.22 %) | 33 / 37,494 (0.09 %) |
| 4,000 to 6,000 | 3 / 1,047 (0.29 %) | 0 / 259 (0.00 %) | 2 / 1,064 (0.19 %) | 1 / 936 (0.11 %) | 185 / 64,621 (0.29 %) | 46 / 37,414 (0.12 %) |
| 6,000 to 8,000 | 5 / 872 (0.57 %) | 2 / 222 (0.90 %) | 0 / 887 (0.00 %) | 0 / 802 (0.00 %) | 248 / 57,898 (0.43 %) | 64 / 37,189 (0.17 %) |
| 8,000 to 10,000 | 7 / 754 (0.93 %) | 3 / 190 (1.58 %) | 0 / 753 (0.00 %) | 0 / 707 (0.00 %) | 480 / 52,516 (0.91 %) | 99 / 36,469 (0.27 %) |
| 10,000 to 12,000 | 20 / 657 (3.04 %) | 6 / 159 (3.77 %) | 1 / 620 (0.16 %) | 2 / 627 (0.32 %) | 912 / 47,438 (1.92 %) | 281 / 35,070 (0.80 %) |
| 12,000 to 14,000 | 35 / 537 (6.52 %) | 9 / 135 (6.67 %) | 3 / 467 (0.64 %) | 3 / 538 (0.56 %) | 1,320 / 41,828 (3.16 %) | 668 / 32,451 (2.06 %) |
| 14,000 to 16,384 | 70 / 419 (16.71 %) | 18 / 109 (16.51 %) | 3 / 283 (1.06 %) | 2 / 416 (0.48 %) | 1,772 / 34,964 (5.07 %) | 1,157 / 28,152 (4.11 %) |
| 16,384 to 20,000 | 0 / 276 (0.00 %) | 25 / 69 (36.23 %) | 0 / 71 (0.00 %) | 0 / 272 (0.00 %) | 3,162 / 25,765 (12.27 %) | 2,675 / 21,461 (12.46 %) |
| 20,000 to 24,000 | 0 / 0 (n/a) | 18 / 30 (60.00 %) | 0 / 0 (n/a) | 0 / 0 (n/a) | 3,905 / 16,087 (24.27 %) | 3,674 / 13,749 (26.72 %) |
| 24,000 to 28,000 | 0 / 0 (n/a) | 1 / 5 (20.00 %) | 0 / 0 (n/a) | 0 / 0 (n/a) | 1,940 / 6,266 (30.96 %) | 1,899 / 5,286 (35.93 %) |
| 28,000 to 32,768 | 0 / 0 (n/a) | 1 / 3 (33.33 %) | 0 / 0 (n/a) | 0 / 0 (n/a) | 288 / 1,282 (22.46 %) | 281 / 920 (30.54 %) |
