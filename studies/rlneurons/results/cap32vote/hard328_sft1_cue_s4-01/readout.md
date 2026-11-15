# cap32vote, hard328, n = 328: Think-SFT + cue, 4 samples, each answer scored at 16,384 and at 32,768 tokens

| group | cap | single, the 4 samples | single, mean | vote over 4 | pass@4 | cap hits | precision of finished | tokens per sample |
|---|---|---|---|---|---|---|---|---|
| all | 16,384 | [211, 212, 211, 209] | 210.8 | 238 | 248 | 368 (28.1 %) | 88.1 % (832 of 944) | 10,042 |
| all | 32,768 | [230, 234, 235, 232] | 232.8 | 244 | 266 | 6 (0.5 %) | 71.1 % (928 of 1306) | 11,650 |
| all | RL plain, 16,384 (stored) | | 200.0 | 221 | | | | |
| not in Think-SFT's training data (322) | 16,384 |  | 205.0 | 232 | 242 |  | | |
| not in Think-SFT's training data (322) | 32,768 |  | 226.8 | 238 | 260 |  | | |
| not in Think-SFT's training data (322) | RL plain, 16,384 (stored) | | 194.2 | 215 | | | | |

| group | difference | problems | points [95 %] |
|---|---|---|---|
| all | single, 32768 minus 16384 | +22.0 | +6.7 [+5.0, +8.5] |
| all | vote4, 32768 minus 16384 | +6.0 | +1.8 [-0.9, +4.9] |
| all | seq4 (24 orders), 32768 minus 16384 | +5.5 | +1.7 [-0.6, +4.1] |
| all | vote4_short (ties to the shortest; not in the spec), 32768 minus 16384 | +6.0 | +1.8 [-0.3, +4.0] |
| all | vote4_short at 32768 minus vote4 at 16384 | +14.0 | +4.3 [+1.8, +7.0] |
| all | vote4_short at 32768 minus RL vote4 (stored 16384) | +31.0 | +9.4 [+6.1, +13.1] |
| all | single at 32768 minus restart1 at 16384 (24 orders) | +7.8 | +2.4 [+0.9, +4.0] |
| all | single at 32768 minus vote2 at 16384 (24 orders) | +9.0 | +2.7 [+1.3, +4.3] |
| all | vote4 at 32768 minus RL vote4 (stored 16384) | +23.0 | +7.0 [+3.7, +10.4] |
| all | vote4 at 16384 minus RL vote4 (stored 16384) | +17.0 | +5.2 [+1.8, +8.5] |
| all | single at 32768 minus RL single (stored 16384) | +32.8 | +10.0 [+7.6, +12.4] |
| not in Think-SFT's training data (322) | single, 32768 minus 16384 | +21.8 | +6.8 [+5.0, +8.5] |
| not in Think-SFT's training data (322) | vote4, 32768 minus 16384 | +6.0 | +1.9 [-1.2, +5.0] |
| not in Think-SFT's training data (322) | seq4 (24 orders), 32768 minus 16384 | +5.5 | +1.7 [-0.6, +4.2] |
| not in Think-SFT's training data (322) | vote4_short (ties to the shortest; not in the spec), 32768 minus 16384 | +6.0 | +1.9 [-0.3, +4.0] |
| not in Think-SFT's training data (322) | vote4_short at 32768 minus vote4 at 16384 | +14.0 | +4.3 [+1.9, +7.1] |
| not in Think-SFT's training data (322) | vote4_short at 32768 minus RL vote4 (stored 16384) | +31.0 | +9.6 [+6.2, +13.0] |
| not in Think-SFT's training data (322) | single at 32768 minus restart1 at 16384 (24 orders) | +7.8 | +2.4 [+0.9, +4.0] |
| not in Think-SFT's training data (322) | single at 32768 minus vote2 at 16384 (24 orders) | +8.8 | +2.7 [+1.2, +4.3] |
| not in Think-SFT's training data (322) | vote4 at 32768 minus RL vote4 (stored 16384) | +23.0 | +7.1 [+3.7, +10.6] |
| not in Think-SFT's training data (322) | vote4 at 16384 minus RL vote4 (stored 16384) | +17.0 | +5.3 [+1.9, +9.0] |
| not in Think-SFT's training data (322) | single at 32768 minus RL single (stored 16384) | +32.5 | +10.1 [+7.6, +12.6] |

| rule (all problems) | cap | right (stored order) | right (24 orders) | tokens per problem (stored order) | tokens (24 orders) |
|---|---|---|---|---|---|
| `single` | 16,384 | 211 | 210.8 | 10,048 | 10,042 |
| `single` | 32,768 | 230 | 232.8 | 11,795 | 11,650 |
| `vote2` | 16,384 | 225 | 223.8 | 20,091 | 20,085 |
| `vote2` | 32,768 | 231 | 233.0 | 23,307 | 23,300 |
| `seq3` | 16,384 | 232 | 233.9 | 25,792 | 25,972 |
| `seq3` | 32,768 | 240 | 241.1 | 28,793 | 28,605 |
| `seq4` | 16,384 | 237 | 239.8 | 30,730 | 30,807 |
| `seq4` | 32,768 | 244 | 245.2 | 32,032 | 31,732 |
| `vote4` | 16,384 | 238 | 239.8 | 40,169 | 40,169 |
| `vote4` | 32,768 | 244 | 245.2 | 46,599 | 46,599 |
| `seq4_short` | 16,384 | 244 | 245.0 | 30,730 | 30,807 |
| `seq4_short` | 32,768 | 250 | 250.0 | 32,032 | 31,732 |
| `vote4_short` | 16,384 | 246 | 246.0 | 40,169 | 40,169 |
| `vote4_short` | 32,768 | 252 | 252.0 | 46,599 | 46,599 |
| `restart1` | 16,384 | 225 | 224.9 | 14,408 | 14,377 |
| `restart1` | 32,768 | 231 | 232.9 | 11,893 | 11,712 |
| `gate12000` | 16,384 | 238 | 239.9 | 25,635 | 25,674 |
| `gate12000` | 32,768 | 246 | 247.3 | 27,138 | 26,800 |

Late answers (more than 16,384 tokens): {"more_than_16384_tokens": 368, "finished": 362, "right": 99, "finished_wrong": 266, "finished_without_extracted_answer": 2, "still_cut_at_32768": 6, "per_sample": [93, 90, 93, 92], "right_per_sample": [23, 24, 27, 25], "wrong_pairs_of_one_problem": 261, "wrong_pairs_agree": 53, "wrong_pairs_agree_percent": 20.3, "with_more_than_20_chinese_characters": 249, "still_cut_with_more_than_20_chinese_characters": 4, "right_with_more_than_20_chinese_characters": 42, "loop_A": 5, "still_cut_loop_A": 3, "median_tokens_of_finished": 21529.0, "vote_changed": {"wrong to right": 15, "right to wrong": 9, "right to wrong problems": [76, 85, 88, 162, 168, 329, 360, 374, 386], "wrong to right problems": [65, 77, 80, 101, 107, 110, 115, 133, 187, 199, 207, 283, 308, 342, 368]}}

Stored 16,384 run: {"folder": "studies/rlneurons/results/thinkvote/hard328_sft1_cue_s4-01", "single_each": [212, 212, 211, 201], "vote4": 241, "cap_hits": 378, "finished_rows_with_the_same_tokens_and_answer_as_the_16384_view": 2, "finished_rows_in_the_16384_view": 944}

Predictions: {"vote4_32": {"predicted": 239.5, "interval": [232, 248], "observed": 244, "inside": true}, "single_32": {"predicted": 229.0, "interval": [224.5, 233.2], "observed": 232.75, "inside": true}, "cap_hit_percent_32": {"predicted": 0.6, "interval": [null, null], "observed": 0.46, "inside": null}, "precision_percent_32": {"predicted": 70, "interval": [62, 78], "observed": 71.06, "inside": true}, "late_wrong_pairs_agree_percent": {"predicted": 64, "interval": [null, null], "observed": 20.3, "inside": null}, "single_32_tokens": {"predicted": 11820, "interval": [null, null], "observed": 11650, "inside": null}, "seq4_32_right_24": {"predicted": 237, "interval": [null, null], "observed": 245.2, "inside": null}}

Hypotheses: {"H1 vote4 at 32768 >= 250 on hard328, and its gain over the 16384 vote has an interval above 0": {"vote4": 244, "gain": {"problems": 6.0, "points": 1.83, "interval95": [-0.91, 4.88]}, "held": false}, "H2 vote gain in points smaller than single gain": {"vote": 1.83, "single": 6.71, "held": true}, "H3 single gain in points (compare the two sets)": {"problems": 22.0, "points": 6.71, "interval95": [5.03, 8.54]}, "H4 one sample at 32768 above restart1 at 16384 (stored rows)": {"single_32": 232.75, "tokens": 11650, "restart1_stored": 222.0, "held": true, "restart1_same_answers": {"right": 225, "right_24": 224.9, "tokens": 14408, "tokens_24": 14377}, "paired": {"problems": 7.83, "points": 2.39, "interval95": [0.91, 3.96]}}, "H4b seq4 at 32768 not above seq4 at 16384": {"paired": {"problems": 5.5, "points": 1.68, "interval95": [-0.64, 4.12]}, "held": true}}
