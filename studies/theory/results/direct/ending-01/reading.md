# 10 raw answers of the deciding group (finished, no code block)

All 6 of the RL-Math 1.5x edit's finished no-block answers, and 4 of the random 1.5x edit's 23.

Math edit, 6 of 6. None holds `\boxed` (0 of 538 answers in this cell do). The causes:
- HumanEval/79 (780 tokens): code written after a bare `CODE` line, no fence; the base passed this problem.
- HumanEval/81 (7,703 tokens): stops on "So code would look like:" before writing the code (end of sequence, not the cap).
- Mbpp/266 (459): `&```pythondef lateralsurface_cube(5): ...``` ` on one line; the fence is malformed and the code wrong.
- Mbpp/639 (5,770): stops mid-reasoning about an unclear problem statement.
- Mbpp/760 (441): one backtick `` `python `` opens the block, three close it; the code is right, the grader finds no block.
- Mbpp/91 (2,801): ends with a numbered summary of the approach and no code.

Random edit, 4 of 23: HumanEval/148 is degenerate text (random words); HumanEval/45 writes `python` and `CODE` lines with
no fence; HumanEval/47 stops mid-reasoning; HumanEval/51 code without a fence, ending in `**`.

Reading: the no-block failures under every edit are broken fences and answers that stop before the code. None is a boxed
math ending in place of the code block, which is what run-03/f2-m04's cause predicts for Math's directions.
