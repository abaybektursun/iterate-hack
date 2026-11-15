# sharpen-01: 10 raw rows read

Rows are from the five `answers.jsonl` files (see run.json). State per arm: PASS, WRONG (finished, code block,
failed tests), CAP (hit the 16,384-token cap). Arms: cued base (cue), base plain (pl), base Math cue (mc), Code
top-8 1.5x (c15), random rank-8 1.5x (r15). "U" = solved by pl or mc.

Five extra passes of Code 1.5x outside U, five inside U (random draw, seed 1):

1. HumanEval/64, outside U: cue/pl/mc WRONG, c15 PASS, r15 WRONG. Base fails an exact-match assertion; c15 checks standard vowels first and then a special case (the task's final-'y' rule). New relative to the three base samples.
2. HumanEval/118, outside U: cue/pl/mc WRONG, c15 and r15 PASS. The random edit also solves it, so a second base-like draw can; U from one sample misses it.
3. Mbpp/239, outside U: cue/pl/mc all CAP, r15 CAP, c15 PASS in 8,912 tokens with a DP. The only gain here is finishing.
4. HumanEval/26, outside U: cue/pl/mc WRONG (assertion fails), c15 PASS. Short answers (931 vs 1,794 tokens); the task asks to drop every element that occurs more than once, a docstring easy to misread.
5. Mbpp/788, outside U: base `(lst[0], *lst[1:], s)` fails on an empty list; c15 `tuple(lst + [s])` passes. An easy problem the base gets wrong by a slip.
6. Mbpp/608, in U (pl PASS): cue index error in a Bell-number DP; c15 writes a correct recurrence.
7. Mbpp/63, in U (pl PASS): cue code is right but its output keeps the template line `CODE`, which raises NameError. A format slip, not a reasoning failure.
8. Mbpp/478, in U (pl PASS): cue CAP at 16,384 tokens; c15 finishes in 7,156 and passes.
9. Mbpp/11, in U (pl PASS): cue removes all occurrences when there are two; c15 removes first and last.
10. HumanEval/162, in U (pl, mc, r15 PASS): cue forgets `import hashlib`; c15 imports it.

What they show: most extra passes, inside or outside U, are easy problems the cued base missed by a slip (missing
import, template residue, edge case) or by not finishing. Outside-U rows include problems the random edit also
solves (118), so a single sample per prompt underestimates the base's solved set for both arms equally. Of the 61
problems only Code 1.5x adds (not random), 41 (0.67) are in U, the same rate as random's extra passes (0.63).
Failure modes of the cued base on Code's extra passes: outside U 31 WRONG, 4 CAP; inside U 71 WRONG, 7 CAP.
