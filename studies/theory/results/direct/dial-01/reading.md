# Ten raw answers of the deciding group (hard328, edit 1.5x sample 1 on problems where base sample 0 finished wrong)

Read by hand from `runs/abaybektursun-1115-055641-b417/answers.jsonl` (last 1,300 characters each). Picked by a fixed shuffle
(seed 1) of the 96 problems where base sample 0 finished wrong: the first 7 the edit got right, the first 3 it got wrong.

| Problem | Gold | Edit | Base s0 | Base s1-3 right | Reading |
|---|---|---|---|---|---|
| 293 | 74 | 74 | 72 | 3 of 3 | Derived (roots, diagonal, area). Base s0 was a slip on a problem the base usually solves. |
| 66 | 721 | 721 | 673 | 2 of 3 | Assumes a = b without proof (the right extremal case), then derives 657/64. Heuristic, right. |
| 181 | 63 | 63 | 45 + 20 sqrt 2 | 0 of 3 | Diagonal midpoints: H - 26 = 37. Short, valid; the base never solves it. |
| 261 | 9 | 9 | 6 | 3 of 3 | Derived by cases gcd = 2 and gcd = 5. |
| 155 | 4 | 4 | none | 1 of 3 | Checks that {2,4,6,8} hits all 12 dominoes; "no smaller set" asserted, not shown. |
| 300 | 2302 | 2302 | 3022 | 1 of 3 | Full enumeration of 15 numbers, median read off. |
| 267 | 19133 | 19133 | 11449 | 2 of 3 | Divisor equation, tests two solutions, picks the smaller. |
| 175 | 6300 | 150 | 225 | 0 of 3 | Sets up a sum, then "after evaluating ... the final answer is 150": asserted, not computed. |
| 81 | 315 | 144 | 24 | 0 of 3 | "12 x 12 = 144" with no count: asserted. |
| 258 | a b / 2 | 0 | (b^2 - a^2)/8 | 0 of 3 | The stored prompt lacks the definitions of a, b, q (broken item); no model can solve it. |

- The grader is right on all 10. The 7 right answers are derivations (2 with one step asserted), not lucky guesses.
- 2 of the 7 are problems the base solves in 3 of its other 3 samples: on base-finished-wrong problems part of every arm's
  rate is regression to the mean, which is why the comparison is the second base sample (22.9 %), not 0.
- The 2 genuine wrong answers box an asserted number after an unfinished argument, as at 2x (README "The finish dial").
