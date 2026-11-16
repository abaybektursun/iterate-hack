# cap32vote, fresh2026, n = 136: Think-SFT + cue, 4 samples, each answer scored at 16,384 and at 32,768 tokens

| group | cap | single, the 4 samples | single, mean | vote over 4 | pass@4 | cap hits | precision of finished | tokens per sample |
|---|---|---|---|---|---|---|---|---|
| all | 16,384 | [53, 61, 64, 58] | 59.0 | 73 | 76 | 260 (47.8 %) | 81.3 % (231 of 284) | 13,084 |
| all | 32,768 | [69, 70, 74, 68] | 70.2 | 75 | 87 | 1 (0.2 %) | 51.8 % (281 of 543) | 15,900 |
| all | RL plain, 16,384 (stored) | | 50.5 | 57 | | | | |
| published (AIME 2026 + HMMT Feb 2026, 59) | 16,384 |  | 22.8 | 29 | 30 |  | | |
| published (AIME 2026 + HMMT Feb 2026, 59) | 32,768 |  | 28.0 | 31 | 36 |  | | |
| published (AIME 2026 + HMMT Feb 2026, 59) | RL plain, 16,384 (stored) | | 17.8 | 22 | | | | |
| transcribed (HMMT Feb Guts + HMMT Nov, 77) | 16,384 |  | 36.2 | 44 | 46 |  | | |
| transcribed (HMMT Feb Guts + HMMT Nov, 77) | 32,768 |  | 42.2 | 44 | 51 |  | | |
| transcribed (HMMT Feb Guts + HMMT Nov, 77) | RL plain, 16,384 (stored) | | 32.8 | 35 | | | | |

| group | difference | problems | points [95 %] |
|---|---|---|---|
| all | single, 32768 minus 16384 | +11.2 | +8.3 [+5.5, +11.4] |
| all | vote4, 32768 minus 16384 | +2.0 | +1.5 [-2.9, +5.9] |
| all | seq4 (24 orders), 32768 minus 16384 | +3.6 | +2.6 [-1.3, +6.6] |
| all | vote4_short (ties to the shortest; not in the spec), 32768 minus 16384 | +6.0 | +4.4 [+0.0, +8.8] |
| all | vote4_short at 32768 minus vote4 at 16384 | +8.0 | +5.9 [+1.5, +11.0] |
| all | vote4_short at 32768 minus RL vote4 (stored 16384) | +24.0 | +17.6 [+11.0, +25.0] |
| all | single at 32768 minus restart1 at 16384 (24 orders) | +4.5 | +3.3 [+0.7, +6.2] |
| all | single at 32768 minus vote2 at 16384 (24 orders) | +4.5 | +3.3 [+0.7, +6.2] |
| all | vote4 at 32768 minus RL vote4 (stored 16384) | +18.0 | +13.2 [+6.6, +19.9] |
| all | vote4 at 16384 minus RL vote4 (stored 16384) | +16.0 | +11.8 [+5.2, +18.4] |
| all | single at 32768 minus RL single (stored 16384) | +19.8 | +14.5 [+9.9, +19.3] |
| published (AIME 2026 + HMMT Feb 2026, 59) | single, 32768 minus 16384 | +5.2 | +8.9 [+4.7, +13.6] |
| published (AIME 2026 + HMMT Feb 2026, 59) | vote4, 32768 minus 16384 | +2.0 | +3.4 [-3.4, +10.2] |
| published (AIME 2026 + HMMT Feb 2026, 59) | seq4 (24 orders), 32768 minus 16384 | +2.2 | +3.8 [-1.3, +9.8] |
| published (AIME 2026 + HMMT Feb 2026, 59) | vote4_short (ties to the shortest; not in the spec), 32768 minus 16384 | +4.0 | +6.8 [+1.7, +13.6] |
| published (AIME 2026 + HMMT Feb 2026, 59) | vote4_short at 32768 minus vote4 at 16384 | +4.0 | +6.8 [+1.7, +13.6] |
| published (AIME 2026 + HMMT Feb 2026, 59) | vote4_short at 32768 minus RL vote4 (stored 16384) | +11.0 | +18.6 [+8.5, +30.5] |
| published (AIME 2026 + HMMT Feb 2026, 59) | single at 32768 minus restart1 at 16384 (24 orders) | +2.3 | +4.0 [-0.1, +8.6] |
| published (AIME 2026 + HMMT Feb 2026, 59) | single at 32768 minus vote2 at 16384 (24 orders) | +2.0 | +3.4 [-0.6, +7.9] |
| published (AIME 2026 + HMMT Feb 2026, 59) | vote4 at 32768 minus RL vote4 (stored 16384) | +9.0 | +15.2 [+3.4, +27.1] |
| published (AIME 2026 + HMMT Feb 2026, 59) | vote4 at 16384 minus RL vote4 (stored 16384) | +7.0 | +11.9 [+0.0, +23.7] |
| published (AIME 2026 + HMMT Feb 2026, 59) | single at 32768 minus RL single (stored 16384) | +10.2 | +17.4 [+9.8, +25.9] |
| transcribed (HMMT Feb Guts + HMMT Nov, 77) | single, 32768 minus 16384 | +6.0 | +7.8 [+3.9, +12.0] |
| transcribed (HMMT Feb Guts + HMMT Nov, 77) | vote4, 32768 minus 16384 | +0.0 | +0.0 [-6.5, +6.5] |
| transcribed (HMMT Feb Guts + HMMT Nov, 77) | seq4 (24 orders), 32768 minus 16384 | +1.3 | +1.7 [-4.0, +7.4] |
| transcribed (HMMT Feb Guts + HMMT Nov, 77) | vote4_short (ties to the shortest; not in the spec), 32768 minus 16384 | +2.0 | +2.6 [-3.9, +9.1] |
| transcribed (HMMT Feb Guts + HMMT Nov, 77) | vote4_short at 32768 minus vote4 at 16384 | +4.0 | +5.2 [-1.3, +13.0] |
| transcribed (HMMT Feb Guts + HMMT Nov, 77) | vote4_short at 32768 minus RL vote4 (stored 16384) | +13.0 | +16.9 [+7.8, +26.0] |
| transcribed (HMMT Feb Guts + HMMT Nov, 77) | single at 32768 minus restart1 at 16384 (24 orders) | +2.2 | +2.8 [-0.7, +6.7] |
| transcribed (HMMT Feb Guts + HMMT Nov, 77) | single at 32768 minus vote2 at 16384 (24 orders) | +2.5 | +3.2 [-0.3, +7.1] |
| transcribed (HMMT Feb Guts + HMMT Nov, 77) | vote4 at 32768 minus RL vote4 (stored 16384) | +9.0 | +11.7 [+3.9, +19.5] |
| transcribed (HMMT Feb Guts + HMMT Nov, 77) | vote4 at 16384 minus RL vote4 (stored 16384) | +9.0 | +11.7 [+3.9, +20.8] |
| transcribed (HMMT Feb Guts + HMMT Nov, 77) | single at 32768 minus RL single (stored 16384) | +9.5 | +12.3 [+7.1, +17.9] |

| rule (all problems) | cap | right (stored order) | right (24 orders) | tokens per problem (stored order) | tokens (24 orders) |
|---|---|---|---|---|---|
| `single` | 16,384 | 53 | 59.0 | 13,242 | 13,084 |
| `single` | 32,768 | 69 | 70.2 | 16,210 | 15,900 |
| `vote2` | 16,384 | 64 | 65.8 | 26,429 | 26,168 |
| `vote2` | 32,768 | 69 | 70.3 | 31,941 | 31,800 |
| `seq3` | 16,384 | 71 | 69.7 | 35,893 | 35,421 |
| `seq3` | 32,768 | 75 | 74.7 | 42,030 | 40,995 |
| `seq4` | 16,384 | 73 | 72.2 | 44,221 | 43,509 |
| `seq4` | 32,768 | 75 | 75.8 | 48,359 | 47,519 |
| `vote4` | 16,384 | 73 | 72.2 | 52,336 | 52,336 |
| `vote4` | 32,768 | 75 | 75.8 | 63,601 | 63,601 |
| `seq4_short` | 16,384 | 75 | 75.0 | 44,221 | 43,509 |
| `seq4_short` | 32,768 | 81 | 80.0 | 48,359 | 47,519 |
| `vote4_short` | 16,384 | 75 | 75.0 | 52,336 | 52,336 |
| `vote4_short` | 32,768 | 81 | 81.0 | 63,601 | 63,601 |
| `restart1` | 16,384 | 63 | 65.8 | 21,599 | 20,641 |
| `restart1` | 32,768 | 69 | 70.2 | 16,210 | 15,951 |
| `gate12000` | 16,384 | 73 | 71.8 | 40,048 | 39,053 |
| `gate12000` | 32,768 | 76 | 76.2 | 44,538 | 43,598 |

Post hoc, not in the spec (added after the hard328 rows were read): the rules `seq4_short`, `vote4_short` and `gate12000` and every difference that names them.

Late answers (more than 16,384 tokens): {"more_than_16384_tokens": 260, "finished": 259, "right": 50, "finished_wrong": 209, "finished_without_extracted_answer": 1, "still_cut_at_32768": 1, "per_sample": [72, 63, 60, 65], "right_per_sample": [18, 10, 12, 10], "wrong_pairs_of_one_problem": 230, "wrong_pairs_agree": 30, "wrong_pairs_agree_percent": 13.0, "with_more_than_20_chinese_characters": 196, "still_cut_with_more_than_20_chinese_characters": 1, "right_with_more_than_20_chinese_characters": 27, "loop_A": 0, "still_cut_loop_A": 0, "median_tokens_of_finished": 21978.0, "vote_changed": {"wrong to right": 6, "right to wrong": 4, "right to wrong problems": [49, 81, 99, 127], "wrong to right problems": [19, 29, 52, 68, 74, 116]}}

Stored 16,384 run: {"folder": "studies/rlneurons/results/fresh/sft1_cue_s4-01", "single_each": [65, 59, 56, 60], "vote4": 75, "cap_hits": 248, "finished_rows_with_the_same_tokens_and_answer_as_the_16384_view": 0, "finished_rows_in_the_16384_view": 284}

Predictions: {"vote4_32": {"predicted": 77.0, "interval": [71, 83], "observed": 75, "inside": true}, "single_32": {"predicted": 74.5, "interval": [71.2, 78.0], "observed": 70.25, "inside": false}, "cap_hit_percent_32": {"predicted": 1.0, "interval": [null, null], "observed": 0.18, "inside": null}, "precision_percent_32": {"predicted": 55, "interval": [47, 63], "observed": 51.75, "inside": true}, "late_wrong_pairs_agree_percent": {"predicted": 75, "interval": [null, null], "observed": 13.0, "inside": null}, "single_32_tokens": {"predicted": 15600, "interval": [null, null], "observed": 15900, "inside": null}}

Hypotheses: {"H1 vote4 at 32768 >= 250 on hard328, and its gain over the 16384 vote has an interval above 0": null, "H2 vote gain in points smaller than single gain": {"vote": 1.47, "single": 8.27, "held": true}, "H3 single gain in points (compare the two sets)": {"problems": 11.25, "points": 8.27, "interval95": [5.51, 11.4]}, "H4 one sample at 32768 above restart1 at 16384 (stored rows)": {"single_32": 70.25, "tokens": 15900, "restart1_stored": 68.0, "held": true, "restart1_same_answers": {"right": 63, "right_24": 65.8, "tokens": 21599, "tokens_24": 20641}, "paired": {"problems": 4.5, "points": 3.31, "interval95": [0.67, 6.25]}}, "H4b seq4 at 32768 not above seq4 at 16384": {"paired": {"problems": 3.58, "points": 2.63, "interval95": [-1.29, 6.62]}, "held": true}}
