# Seen against unseen: readout (`analysis/seen.py`, spec `specs/SPEC_seen.md`)

Percent right with grader v3, 4 samples per problem, T 1.0 / top-p 1.0; 95 % bootstrap interval over problems. Unseen =
family means of the 130 unseen problems weighted by the seen set's family shares. Tokens = generated tokens per answer.

## all 72 (unseen families: {'aime': 68, 'amc23': 28, 'olympiadbench': 34}, weights {'aime': 0.722, 'amc23': 0.167, 'olympiadbench': 0.111})

| Arm | Per sample: seen | unseen | seen - unseen | Vote over 4: seen | unseen | seen - unseen | Tokens: seen | unseen |
|---|---|---|---|---|---|---|---|---|
| base, cue | 20.8 | 40.0 | -19.1 [-28.7, -9.2] | 30.6 | 52.7 | -22.1 [-35.8, -8.1] | 12,952 | 10,541 |
| RL, plain | 37.5 | 55.5 | -18.0 [-29.6, -5.9] | 45.8 | 64.2 | -18.3 [-32.5, -3.6] | 12,097 | 10,344 |
| Code-RL, cue | 30.6 | 51.4 | -20.9 [-32.7, -9.0] | 34.7 | 57.9 | -23.2 [-37.1, -8.8] | 11,068 | 9,195 |
| Think-SFT, cue | 46.2 | 62.0 | -15.9 [-28.1, -3.3] | 63.9 | 72.7 | -8.8 [-22.5, 4.8] | 13,107 | 11,145 |

| Control | Per sample: RL - control, seen | unseen | D | Vote over 4: RL - control, seen | unseen | D |
|---|---|---|---|---|---|---|
| Code-RL, cue | 6.9 [0.7, 13.2] | 4.0 [-0.6, 8.6] | 2.9 [-4.8, 10.6] | 11.1 [1.4, 20.8] | 6.2 [-0.6, 13.4] | 4.9 [-7.3, 17.2] |
| base, cue | 16.7 [10.4, 22.9] | 15.5 [11.1, 20.0] | 1.2 [-6.4, 8.8] | 15.3 [5.6, 25.0] | 11.5 [5.2, 18.3] | 3.8 [-7.8, 15.8] |
| Think-SFT, cue | -8.7 [-14.6, -2.8] | -6.6 [-10.9, -2.6] | -2.1 [-9.1, 5.0] | -18.1 [-27.8, -6.9] | -8.5 [-14.3, -3.7] | -9.5 [-21.0, 2.3] |

## exact 43 (unseen families: {'aime': 68}, weights {'aime': 1.0})

| Arm | Per sample: seen | unseen | seen - unseen | Vote over 4: seen | unseen | seen - unseen | Tokens: seen | unseen |
|---|---|---|---|---|---|---|---|---|
| base, cue | 13.4 | 30.5 | -17.1 [-27.9, -6.3] | 18.6 | 41.2 | -22.6 [-38.4, -5.9] | 13,439 | 11,668 |
| RL, plain | 32.6 | 47.1 | -14.5 [-28.7, 0.6] | 41.9 | 57.4 | -15.5 [-33.2, 3.1] | 12,735 | 11,163 |
| Code-RL, cue | 22.7 | 40.4 | -17.8 [-31.3, -3.9] | 25.6 | 47.1 | -21.5 [-38.4, -4.0] | 11,817 | 10,312 |
| Think-SFT, cue | 41.9 | 54.4 | -12.6 [-28.5, 2.8] | 60.5 | 66.2 | -5.7 [-24.1, 13.0] | 13,800 | 12,178 |

| Control | Per sample: RL - control, seen | unseen | D | Vote over 4: RL - control, seen | unseen | D |
|---|---|---|---|---|---|---|
| Code-RL, cue | 9.9 [4.1, 16.3] | 6.6 [0.7, 12.5] | 3.3 [-5.0, 12.3] | 16.3 [7.0, 27.9] | 10.3 [1.5, 19.1] | 6.0 [-7.7, 20.8] |
| base, cue | 19.2 [11.1, 28.5] | 16.5 [11.0, 22.4] | 2.6 [-7.2, 13.5] | 23.3 [11.6, 37.2] | 16.2 [8.8, 25.0] | 7.1 [-7.9, 22.5] |
| Think-SFT, cue | -9.3 [-17.4, -1.2] | -7.3 [-12.9, -2.2] | -1.9 [-11.6, 8.4] | -18.6 [-32.6, -4.7] | -8.8 [-16.2, -2.9] | -9.8 [-24.4, 5.0] |

## near 29 (unseen families: {'aime': 68, 'amc23': 28, 'olympiadbench': 34}, weights {'aime': 0.31, 'amc23': 0.414, 'olympiadbench': 0.276})

| Arm | Per sample: seen | unseen | seen - unseen | Vote over 4: seen | unseen | seen - unseen | Tokens: seen | unseen |
|---|---|---|---|---|---|---|---|---|
| base, cue | 31.9 | 54.0 | -22.1 [-36.0, -7.6] | 48.3 | 69.7 | -21.4 [-40.1, -1.9] | 12,230 | 8,870 |
| RL, plain | 44.8 | 67.9 | -23.1 [-38.8, -7.3] | 51.7 | 74.2 | -22.5 [-41.8, -2.7] | 11,150 | 9,131 |
| Code-RL, cue | 42.2 | 67.7 | -25.4 [-42.3, -8.4] | 48.3 | 74.0 | -25.7 [-44.9, -6.2] | 9,957 | 7,539 |
| Think-SFT, cue | 52.6 | 73.3 | -20.8 [-37.5, -4.2] | 69.0 | 82.3 | -13.4 [-31.5, 3.5] | 12,079 | 9,613 |

| Control | Per sample: RL - control, seen | unseen | D | Vote over 4: RL - control, seen | unseen | D |
|---|---|---|---|---|---|---|
| Code-RL, cue | 2.6 [-9.5, 14.7] | 0.2 [-4.4, 4.5] | 2.3 [-10.9, 15.1] | 3.5 [-13.8, 20.7] | 0.2 [-6.1, 6.3] | 3.2 [-16.6, 22.4] |
| base, cue | 12.9 [4.3, 21.6] | 14.0 [9.7, 18.4] | -1.0 [-10.6, 8.7] | 3.5 [-10.3, 20.7] | 4.5 [-2.3, 11.1] | -1.1 [-18.1, 15.7] |
| Think-SFT, cue | -7.8 [-15.5, 0.0] | -5.4 [-9.0, -2.1] | -2.3 [-10.7, 6.4] | -17.2 [-34.5, 0.0] | -8.1 [-14.1, -2.8] | -9.1 [-27.2, 8.7] |
