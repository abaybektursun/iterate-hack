Outcome of every generated sample, hard328, attempt 0 of 4 samples, 1,312 samples per model. % of samples [95 %, bootstrap over problems].

Judge A, the judged strata weighted to their pools:

| Outcome | Think-SFT + cue | RL plain | base + cue |
|---|---|---|---|
| long right, derived | 20.6 [17.3, 24.1] | 15.6 [12.2, 19.1] | 7.9 [6.0, 9.7] |
| long right, asserted | 1.9 [0.4, 3.7] | 4.3 [2.1, 6.9] | 2.0 [1.0, 3.1] |
| long wrong, derived | 4.7 [3.2, 6.3] | 8.0 [5.3, 10.9] | 7.2 [4.8, 9.9] |
| long wrong, asserted | 2.7 [1.6, 3.8] | 21.1 [16.9, 25.1] | 14.2 [11.1, 17.4] |
| short right | 40.2 [35.1, 45.2] | 40.5 [35.6, 45.8] | 38.2 [33.4, 42.9] |
| short wrong | 1.0 [0.4, 1.8] | 1.8 [0.9, 2.7] | 6.7 [5.3, 8.2] |
| cap hit | 28.8 [24.6, 33.2] | 8.7 [6.6, 10.8] | 21.8 [18.4, 25.2] |
| no answer | 0.2 [0.0, 0.5] | 0.1 [0.0, 0.2] | 2.1 [1.4, 2.8] |

Judge B, the judged strata weighted to their pools:

| Outcome | Think-SFT + cue | RL plain | base + cue |
|---|---|---|---|
| long right, derived | 18.7 [15.2, 22.6] | 15.6 [12.3, 18.9] | 8.0 [6.2, 9.9] |
| long right, asserted | 3.7 [1.5, 6.4] | 4.3 [2.3, 6.7] | 1.8 [0.8, 3.0] |
| long wrong, derived | 4.2 [2.8, 5.8] | 8.0 [5.1, 11.3] | 7.2 [4.8, 9.9] |
| long wrong, asserted | 3.1 [2.0, 4.4] | 21.1 [17.0, 25.2] | 14.2 [11.2, 17.4] |
| short right | 40.2 [35.1, 45.2] | 40.5 [35.6, 45.8] | 38.2 [33.4, 42.9] |
| short wrong | 1.0 [0.4, 1.8] | 1.8 [0.9, 2.7] | 6.7 [5.3, 8.2] |
| cap hit | 28.8 [24.6, 33.2] | 8.7 [6.6, 10.8] | 21.8 [18.4, 25.2] |
| no answer | 0.2 [0.0, 0.5] | 0.1 [0.0, 0.2] | 2.1 [1.4, 2.8] |

Counts: Think-SFT + cue: long finished right 295, long finished wrong 96, short right 527, short wrong 13, cap hit 378, no answer 3, cap hit with a boxed value 55, cap hit scored right 14; RL plain: long finished right 261, long finished wrong 381, short right 532, short wrong 23, cap hit 114, no answer 1, cap hit with a boxed value 79, cap hit scored right 7; base + cue: long finished right 129, long finished wrong 281, short right 501, short wrong 88, cap hit 286, no answer 27, cap hit with a boxed value 49, cap hit scored right 4.

Judge B on all 642 long finished RL answers, counted: long right, derived 207, 15.8 [13.0, 18.7] %; long right, asserted 54, 4.1 [2.7, 5.7] %; long wrong, derived 116, 8.8 [7.0, 11.1] %; long wrong, asserted 265, 20.2 [17.0, 23.5] %. Judge B labelled only the 140 sampled rows of the base and of Think-SFT.

Asserted wrong answers per sample, paired differences in points, with the exact split (pool term: how often the model finishes long and wrong; share term: how often such an answer is asserted):

| Judge | Pair | Difference | Pool term | Share term |
|---|---|---|---|---|
| A | rl - base | 6.9 [3.1, 10.6] | 5.0 [2.9, 7.6] | 1.8 [-2.0, 5.6] |
| A | rl - think | 18.4 [14.6, 22.3] | 7.9 [5.0, 11.0] | 10.5 [6.5, 14.8] |
| B | rl - base | 6.9 [3.1, 10.8] | 5.0 [2.9, 7.6] | 1.8 [-2.3, 5.7] |
| B | rl - think | 17.9 [14.0, 21.8] | 9.2 [6.1, 12.5] | 8.7 [4.2, 13.3] |
| B, RL counted on its whole pool | rl - base | 6.0 [2.8, 9.4] | | |
| B, RL counted on its whole pool | rl - think | 17.1 [14.0, 20.2] | | |

Cap-hit rate, points: rl - base -13.1 [-16.3, -10.2]; rl - think -20.1 [-24.0, -16.5]. H4 held: True. H5 held: True.

Problems split by the base's cap hits (counts of samples):

| Group | Problems | Model | Cap hit | Long finished wrong | Long finished right |
|---|---|---|---|---|---|
| base hits the cap on none of 4 | 191 | Think-SFT + cue | 40 | 47 | 163 |
| base hits the cap on none of 4 | 191 | RL plain | 11 | 90 | 144 |
| base hits the cap on none of 4 | 191 | base + cue | 0 | 105 | 97 |
| base hits the cap on 1 to 4 of 4 | 137 | Think-SFT + cue | 338 | 49 | 132 |
| base hits the cap on 1 to 4 of 4 | 137 | RL plain | 103 | 291 | 117 |
| base hits the cap on 1 to 4 of 4 | 137 | base + cue | 286 | 176 | 32 |

RL's long wrong answers that judge B labels asserted (whole pool): base hits the cap on none of 4: 41; base hits the cap on 1 to 4 of 4: 224.
