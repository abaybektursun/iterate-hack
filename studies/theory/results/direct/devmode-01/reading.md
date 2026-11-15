# Reading, devmode-01

The plan's input (per-sample dev100 rows of the kept autobench method) sits only in frustea's Modal Volume
`autobench-runs` and was not read. The 10 rows below are the first 10 vote-wrong problems of the null, the cued base's
12 samples at T 1.0, cap 16,384 (`studies/rlneurons/results/votek/math500_base_cue-01/rows.jsonl`); its vote over 12
reproduces 466/500 (result-1c9e40), and 94/100 on dev100 (6 wrong, so the null uses all 34 wrong problems of 500).
Columns: problem, gold, g (largest wrong group / answer-bearing samples), answer-bearing n, samples over 4,096 tokens,
cap hits.

- 9: gold 4, g 0.333, n_ans 6, over 4,096: 12/12, cap hits 6; answers 5, 2, <length>, <length>, <length>, <length>, 4, 8, <length>, 4, 5, <length>
- 11: gold \frac{3}{56}, g 0.111, n_ans 9, over 4,096: 11/12, cap hits 3; answers \dfrac{171}{56}, \dfrac{1}{7}, \dfrac{3}{56}, \dfrac{3}{28}, <length>, \frac{8}{63}, 0, <length>, <length>, \dfrac{19}{147}, \dfrac{1}{9}, \dfrac{25}{196}
- 18: gold 28, g 0.5, n_ans 12, over 4,096: 12/12, cap hits 0; answers 56, 124, 32, 56, The angle  x  measures 64 degrees., 56, 56, 56, 32, 62^{\circ}, 56, 28
- 20: gold 6+9i, g 0.636, n_ans 11, over 4,096: 5/12, cap hits 1; answers 117 + 41i, 117 + 41i, 6 + 9i, 6 + 9i, 117 + 41i, 117 + 41i, 6 + 9i, <length>, 117 + 41i, 6 + 9i, 117 + 41i, 117 + 41i
- 26: gold 144, g 0.25, n_ans 8, over 4,096: 12/12, cap hits 4; answers <length>, 288, 151200, <length>, <length>, 144, 96, <length>, 288, 48, 480, 864
- 43: gold 70 \sqrt{2}, g 0.4, n_ans 5, over 4,096: 12/12, cap hits 7; answers <length>, 10(2\sqrt{5} + \sqrt{34}), <length>, <length>, 103, 10(2\sqrt{5} + \sqrt{34}), 106.57, <length>, <length>, <length>, <length>, 70\sqrt{2}
- 96: gold 1 \pm \sqrt{19}, g 0.167, n_ans 6, over 4,096: 12/12, cap hits 6; answers <length>, <length>, 1, 4, 1, <length>, <length>, 11, 13, 5.5, 16, 1 + \sqrt{19}, 1 - \sqrt{19}, <length>, <length>
- 100: gold 145^\circ, g 0.25, n_ans 8, over 4,096: 12/12, cap hits 4; answers <length>, 70, <length>, 145, 105, 70, 145, <length>, 115, <length>, 160, 75
- 101: gold 850, g 0.143, n_ans 7, over 4,096: 12/12, cap hits 5; answers 20, 1660, 5, <length>, <length>, 1700, <length>, 425, <length>, 3230, <length>, 850
- 103: gold (3,4], g 0.333, n_ans 3, over 4,096: 11/12, cap hits 8; answers <length>, <length>, (1, 2) \cup (3, 4), <length>, <length>, [1, 2), 1 + \sqrt{5}, <length>, <length>, <length>, <length>, None

What they show: wrong answers mostly scatter (g 0.11-0.40 on 8 of 10); two problems (18: 56 six times; 20: 117 + 41i
seven times) lose to one shared wrong value. G_cue = 0.40 [0.34, 0.46] over 34 problems, so b needs G_plain >= 0.52
from the plain T 0.6 rows. Instrument: R of the null against itself is 1.0 (refuted under the rule), as it must be.
