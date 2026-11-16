# template-01: 10 raw hard328 rows read by hand

Own = Think-SFT in its own ChatML `<think>` template (native/hard328-01); cue = raw template with the cue, cap 32,768
(cap32/sft_cue-01). Signs on the first 16,384 generated tokens (drift.py). Token positions are re-tokenized positions.

| # | Cell, problem | Tokens, v3 | Sign | What the text shows |
|---|---|---|---|---|
| 1 | own 29 | 14,685, wrong (59 vs 244) | switch at token 14,164 | "可能仍然存在问题，但 according to the problem's example..." Chinese mixed into English late in a confused count. Real drift in the own template. |
| 2 | own 62 | 19,424, wrong (503 vs 371) | switch at 15,327 | "故, the total我们想要的概率是 1 - ..." Chinese words woven into English reasoning. Real drift. |
| 3 | cue 61 | 25,469, wrong (87 vs 113) | switch at 15,941 | "等于：", "所以 this term becomes..." Chinese connectives in long algebra; the own template on the same problem finishes in 11,266 tokens, right. |
| 4 | cue 79 | 11,243, right | repeat at 10,446 (4 windows) | Verbatim restatement of the problem ("the remainder when the product ... is divided by 1000"). Not drift: a false positive of the repeat sign. |
| 5 | own 73 | 16,865, wrong (69 vs 197) | repeat at 169 (12 windows) | Restates the problem statement word for word at the start. Benign repeat; the row runs long and ends wrong anyway. |
| 6 | cue 73 | 16,116, wrong (287 vs 197) | switch at 15,432 | "Thus 这矛盾, hence 错误", "34和1是Human": Chinese and garbled words. Same problem drifts in both templates, by different signs. |
| 7 | own 152 | 12,185, right | repeat at 11,159 (22 windows) | Loops on the prompt's instruction: "in form Answer: $Answer (without quotes) where $Answer is the answer to the problem in form Answer: ..." Real repetition, still right. |
| 8 | own 156 | 9,855, right | repeat at 8,189 (35 windows) | A sign table "(1,2): + (2,3): + (3,4): - ..." written twice. Benign repeat. |
| 9 | cue 75 | 6,484, right | repeat at 1,139 (52 windows) | Restates the problem ("Among the 900 residents of Aimeville..."). Benign repeat. |
| 10 | own 61 | 11,266, right | none | Clean English to "Final Answer: m + n = 100 + 13 = 113", then \boxed{113}. Against the claim on this problem: the cue row (#3) drifted here. |

What they show: the script switch reads as real drift in both templates, the same kind (Chinese words mixed into English,
late, after 14,000 tokens), and it shows up in the own template too (#1, #2). The 50-token repeat sign is mixed: one real
loop (#7), four benign restatements of the problem or a table (#4, #5, #8, #9). It fires about as often in both cells
(27 and 27 rows), so it adds noise to both sides rather than a bias. The switch sign alone gives the same reading as the
union (own 32, cue 38 rows; thinkvote samples 34 to 44).
