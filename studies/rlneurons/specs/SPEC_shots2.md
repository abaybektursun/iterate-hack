# SPEC shots2: in-context improvement loop with no RL text and no reward (board work-eb10d7)

Written 2026-11-15 04:45 UTC, before any run. Follows shots1 (result-6d422d): three answers written by Math-RL in the base's
context give +5.6 points on MATH-500; three right answers written by the base itself give +1.4 [-2.0, 4.8].

## Question

Can the base build, from its own answers and with no answer key, a context that helps as RL's answers do? The loop
(`jobs/shots_loop.py`): round g samples 4 answers per pool problem with the examples of generation g in the prompt
(generation 0: none). The examples of generation g + 1 are the 3 pool problems where at least 3 of 4 finished samples agree,
taking for each the longest agreeing answer of at most 3,000 tokens, and keeping the 3 problems with the longest such answer.
Length is the label-free stand-in for what RL's answers have (RL median 3,148 generated tokens against 1,812 for the base).
Pool: the first 36 problems of the harder set that are outside the 328 (overlap flag not "none"). T 1.0 / top-p 1.0, cue,
cap 8,192 in the loop. 3 rounds give generations 1, 2, 3.

## Cells after the loop

`run_cell --shots` with generation 1 and generation 3 on MATH-500 (n 500: no example is a MATH-500 problem), T 1.0 / top-p 1.0,
cap 16,384, seed 71000000, against base cue 410 and the shots1 arms. The better of the two once on the 328 (seed 3000000),
against base cue 164, RL-written examples (shots1, running), theta 0.25 182, RL 206.

## Hypotheses and what refutes them

- H1, long agreed own answers help: generation 1 minus base cue >= +3 points on MATH-500, interval above 0. Refuted if the
  interval contains 0. This is also the length control of shots1: if H1 holds, shots1's gain needs no RL text.
- H2, the loop compounds: generation 3 minus generation 1 > 0 with an interval above 0, and the share right on the pool rises
  from round 0 to round 2. Refuted if generation 3 is within 2 points of generation 1.
- H3, failure by drift: answers get longer each round while the share right on the pool falls (examples picked for length
  ramble). Seen in metrics.json rounds: mean generated tokens up, right share down, cap hits up.

The pool's gold answers are used only to report the share right per round and whether each picked example is right.
