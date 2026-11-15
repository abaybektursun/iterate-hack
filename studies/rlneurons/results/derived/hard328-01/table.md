Instrument: planted positives A 15/15, B 15/15; planted negatives A 15/15, B 15/15; kappa A/B 0.80 (379/420); kappa hand/A 0.60 (25/30); hand/B 0.49; tail against full text 38/40, kappa 0.84; quote found 420/450. Instrument ok: True. Cost 7.37 USD.

Judge A (claude-sonnet-5-5), long finished answers, hard328:

| Model | Stratum | Rows | Derived | Asserted | Unclear | Asserted, % [95 %] |
|---|---|---|---|---|---|---|
| Think-SFT + cue | wrong | 80 | 51 | 29 | 0 | 36.2 [24.4, 48.6] |
| Think-SFT + cue | right | 60 | 55 | 5 | 0 | 8.3 [1.9, 15.7] |
| RL plain | wrong | 80 | 22 | 58 | 0 | 72.5 [63.1, 81.3] |
| RL plain | right | 60 | 47 | 13 | 0 | 21.7 [11.1, 33.9] |
| base + cue | wrong | 80 | 27 | 53 | 0 | 66.2 [54.6, 77.2] |
| base + cue | right | 60 | 48 | 12 | 0 | 20.0 [10.4, 30.6] |

- rl - think, wrong: 36.2 [23.3, 49.1] points
- rl - think, right: 13.3 [1.1, 26.8] points
- rl - base, wrong: 6.2 [-6.7, 19.1] points
- rl - base, right: 1.7 [-13.4, 16.5] points
- base - think, wrong: 30.0 [14.7, 45.6] points

Judge B (claude-haiku-5-5), long finished answers, hard328:

| Model | Stratum | Rows | Derived | Asserted | Unclear | Asserted, % [95 %] |
|---|---|---|---|---|---|---|
| Think-SFT + cue | wrong | 80 | 46 | 34 | 0 | 42.5 [30.1, 55.4] |
| Think-SFT + cue | right | 60 | 50 | 10 | 0 | 16.7 [7.1, 27.2] |
| RL plain | wrong | 80 | 22 | 58 | 0 | 72.5 [62.5, 82.1] |
| RL plain | right | 60 | 47 | 13 | 0 | 21.7 [11.8, 33.3] |
| base + cue | wrong | 80 | 27 | 53 | 0 | 66.2 [54.9, 77.3] |
| base + cue | right | 60 | 49 | 11 | 0 | 18.3 [8.9, 29.3] |

- rl - think, wrong: 30.0 [15.0, 44.8] points
- rl - think, right: 5.0 [-6.5, 18.0] points
- rl - base, wrong: 6.2 [-8.0, 19.8] points
- rl - base, right: 3.3 [-10.4, 17.0] points
- base - think, wrong: 23.8 [7.8, 39.8] points

H1 held: False; refuted: True.

H2, right rate of asserted and of derived long finished answers (judge A, weighted to the pool):

| Model | Asserted share of long finished, % | Right, asserted % | Right, derived % | Derived - asserted |
|---|---|---|---|---|
| Think-SFT + cue | 15.2 [9.4, 21.6] | 41.4 [13.4, 62.5] | 81.5 [75.3, 86.9] | 40.1 [18.4, 68.6] |
| RL plain | 51.8 [43.3, 60.3] | 17.0 [9.0, 25.6] | 66.1 [56.5, 75.2] | 49.1 [34.7, 62.6] |
| base + cue | 51.7 [42.3, 60.5] | 12.2 [6.1, 18.9] | 52.1 [42.3, 62.6] | 39.9 [26.6, 53.0] |

Judge B on all 642 long finished RL answers: DERIVED 207/323 right, 64.1 [56.7, 70.5] %; ASSERTED 54/319 right, 16.9 [11.6, 22.8] %; UNCLEAR 0/0 right, nan [nan, nan] %

Asserted share by length (judge A):

| Model | Stratum | 8,000 to 12,000 | 12,000 to the cap |
|---|---|---|---|
| Think-SFT + cue | wrong | 4/25, 16.0 [3.2, 33.3] | 25/55, 45.5 [30.6, 59.6] |
| Think-SFT + cue | right | 3/28, 10.7 [0.0, 22.6] | 2/32, 6.2 [0.0, 16.2] |
| RL plain | wrong | 15/22, 68.2 [50.0, 85.7] | 43/58, 74.1 [63.2, 84.6] |
| RL plain | right | 7/44, 15.9 [6.1, 28.6] | 6/16, 37.5 [11.1, 64.7] |
| base + cue | wrong | 8/25, 32.0 [12.5, 51.6] | 45/55, 81.8 [69.8, 91.9] |
| base + cue | right | 4/40, 10.0 [2.2, 20.9] | 8/20, 40.0 [18.8, 61.9] |

RL long wrong answers, problems where all four Think-SFT samples hit the cap (48) against the others: A_sample think_capped_4_of_4: 23/30, 76.7 [62.1, 90.0]; A_sample elsewhere: 35/50, 70.0 [56.5, 82.5]; B_all_rl_wrong think_capped_4_of_4: 111/133, 83.5 [76.6, 89.8]; B_all_rl_wrong elsewhere: 154/248, 62.1 [54.7, 69.6]

H3 (judge B flag on RL's 1,312 samples; descriptive): all answered: coverage 97.3 %, precision 62.7 %. Dropping the 319 flagged answers (54 of them right): coverage 72.9 %, precision 78.0 [73.9, 81.6] %; length alone at the same coverage 77.4 [73.0, 81.1] %; difference 0.5 [-1.4, 2.6] points. Held: False. Judge A, weighted: coverage 71.9 %, precision 78.8 % against 78.4 %.
