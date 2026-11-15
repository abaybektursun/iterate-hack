You are grading wrong answers to math problems. Each item gives a problem, its gold answer, a reference solution, one
ANSWER UNDER JUDGMENT whose final answer was scored wrong, and sometimes a CORRECT ANSWER to the same problem for comparison.
Read the whole answer under judgment, find the first step where it goes wrong, and give exactly one label:

- slip: the method would give the gold answer; an arithmetic, algebra, sign, counting or copying error changes the result.
- wrong_plan: the method or the concept is wrong, or the solution is abandoned or guessed; carried out without error it
  would still not give the gold answer.
- misread: the answer solves a different problem than the one stated (a condition dropped or changed, the wrong quantity
  reported), and solves that other problem consistently.
- format: the work reaches the gold value; the final stated answer differs in form or is garbled.
- mismatch: the answer under judgment is about a different problem altogether, not this one.
- unclear: none of the above can be decided.

For every item also copy, character for character, the first wrong step from the answer under judgment (40 to 150
characters, one line of the answer, no ellipsis, no rewording). For format, mismatch and unclear the quote may be "".
Write your labels as a JSON list, one object per item, in the order of the file:
[{"id": "<item id>", "label": "<one of the six>", "quote": "<verbatim>", "reason": "<one sentence>"}]
Judge every item on its own. Do not use any tool except reading the batch file and writing the labels file.
