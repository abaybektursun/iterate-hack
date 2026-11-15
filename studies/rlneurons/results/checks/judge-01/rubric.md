You are labeling short excerpts of step-by-step answers to math problems. Each item gives the problem and an excerpt of one
answer. One word or phrase of the excerpt is marked between >>> and <<< (for example >>>Wait<<<). Decide what the text
right after the marked word does, and give exactly one label:

- fix: a specific earlier statement (a number, an expression, a count, a sign, the reading of the problem) was wrong, and
  the text after the mark corrects it; the answer goes on with the corrected version.
- switch: the text after the mark changes the method or the reading of the problem, or drops the current line of work,
  without correcting one specific wrong statement.
- confirm: the text after the mark tests or re-derives an earlier statement (substitutes back, recounts, uses a second
  method) and keeps it unchanged.
- filler: nothing is re-examined: the text continues with the next step, restates, or thinks aloud.

Judge only from the excerpt. Write your labels as a JSON list, one object per item, in the order of the file:
[{"id": "<item id>", "label": "<fix|switch|confirm|filler>", "reason": "<one sentence>"}]
Judge every item on its own. Do not use any tool except reading the batch file and writing the labels file.
