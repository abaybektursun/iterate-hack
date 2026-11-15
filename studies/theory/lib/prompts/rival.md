Use only the Read and Write tools, only on files in the current directory.

theory.json is a theory that survived its own tests. tests.json lists those tests: for each, the experiment, the
recipe that computed it from stored per-problem rows, the unit, the measured value, and the theory's prediction
(value, low, high: a 90 % interval). Your job is to write the strongest rival to this theory and the tests that
decide between the two. Files here:
- before.jsonl: the team's board items (results and knowledge) up to a cutoff, one JSON object per line (id, kind,
  at, who, text).
- inventory.md: the per-problem row files the team has stored, how to fetch each, whether it is readable now, and
  the fields of a row. You cannot open the rows; you know them only from this file.
- external.md: published mechanisms, each headed `### <source id> — <title, year>`.

The rival is a different mechanism that gives every measured value in tests.json as well as the theory does and
fits the items in before.jsonl. Take the theory's own "rival" field only if it really is the strongest; usually a
simpler or better-measured mechanism exists (a length effect, a sampling effect, a grader effect, a published
mechanism from external.md). A rival that restates the theory in other words is no rival. When theory.json has
"parts", it is an account (a budget of a gap): the rival is a different budget of the same gap, with other parts, another
order of the rules or other shares, and its tests are numbers the two budgets give differently.

Then choose 2 to 4 offline tests on which the two mechanisms give different numbers. You predict each from the
rival. A separate agent will predict the same tests from the theory alone, the recipes will be computed once, and
on each test the prediction closer to the computed value (by log density) wins. Choose tests where the rival is
right and the theory is wrong; a test on which both give the same number decides nothing.

Write rival.json:

{"statement": "<one sentence: the rival mechanism>",
 "why_strongest": "<why it explains the measured values in tests.json as well as the theory>",
 "tests": [
  {"experiment": "<what is computed>", "recipe": "<files and computation, see below>", "unit": "fraction of problems",
   "value": 0.31, "low": 0.25, "high": 0.37,
   "theory_should_say": "<one sentence: the number the theory's mechanism implies, and why it differs from yours>"}]}

Rules:
- A recipe names files from inventory.md marked readable now, the filters, the statistic, and how cap hits, ties and
  missing rows count, precise enough that two people would compute the same number. It states only the computation,
  never the expected result or either mechanism. Someone will implement it literally and run it once.
- The quantity is not one of the tests in tests.json, and no board item reports it.
- value, low and high are your 90 % interval for the computed number: the interval is scored as a normal
  distribution (mean value, sd (high - low) / 3.29), so too wide earns little and too narrow loses when it misses.

Write only rival.json. Reply with the rival's statement.
