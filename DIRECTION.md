# Research direction

This is the direction for every agent in this repository. Read it before choosing work.

## Pitch line

With no training, a three-token opening cue takes the Olmo 3 base model to 82 on MATH-500 at AI2's own sampling
setting, against 93 for the RL-trained model. Without the cue the base scores 64 at our first setting and 45 at
AI2's. The gap that RL has to explain is about 11 points.

## Mission

An agent swarm measures how much of a published RL gain an untrained base model reaches with no training. Any
change to how answers are generated or graded is made for both models, so the two are always compared under
identical conditions. Every configuration is chosen on MATH-500 and scored once on 328 harder problems absent from
the RL training set.

On AI2's Olmo 3.1 RL-Zero-Math:

1. The size of the gain depends on a sampling choice. RL scores about 93 at either setting. The untrained base with
   the opening cue scores 71 at T 0.6 / top-p 0.95, where it loops, and 82 at T 1.0 / top-p 1.0, where the loops
   disappear. Wang et al. (2610.06851, Table 6) report 77.9 for the cue under a different setting (T 0.6, cap 31,744,
   their grader); under our grader v1, the closest to theirs, our T 1.0 cell is 76 to 79 (board result-60d899).
2. About 11 points remain at AI2's setting, spread over problems of all lengths.
3. The swarm looks for the cheapest route to those points that uses no reward, at equal generated tokens and with
   RL given the same procedure, and reports the route or that it found none.

Deliverable: the best configuration of either model on the 328, with its score and tokens per problem. The same
harness then runs unchanged on the Code pair.

## Why this mission

- Practical result: it is an efficiency finding that already exists (18 of 29 points with no training), and the
  deliverable is a scored configuration on unseen hard problems.
- Lowest-hanging: every Day-1 row is inference on a Modal app that ran five cells last night for about 10 USD.
- Demo: a looping answer beside a finishing one, the two-setting table, and the swarm correcting its own numbers on
  screen.
- Interpretability: one side study aimed at the remaining 11 points, scaling the RL-minus-base weight difference
  with the Code-RL difference and a random difference as controls.

## Day 1

1. The 328 at T 1.0 on both models.
2. The base with cue at T 0.6 / top-p 1.0, to separate temperature from top-p.
3. Restart and four-sample vote rows on both models, with tokens per problem.
4. The weight-difference scaling study.

## Open, to state on the slide

- Harder set: the 328 is measured only for the base at 0.6.
- Sampling: temperature and top-p are not yet separated.
- Grader: a second model read all 96 v1/v3 disagreements of the Day-1 #3 rows: no wrong answer accepted (board
  result-0018d3). The 113 flips of the first table were then all read by a second model: 112 right, 1 wrong, offset by
  the 1 v3 error in the same cell (studies/rlneurons/results/rln4/grader_v3_read2/readout.json).
- RL training steps: the three RL jobs at 0.6 are still running, so the step-400 and first-release rows are
  unscored.
