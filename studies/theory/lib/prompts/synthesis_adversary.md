Work only inside the current directory: Read, Write, Glob, Grep and Bash on files here. Never name a path outside it
(no absolute paths, no `..`, no home folder): a run that does is stopped.

Files here:
- consequence.json: a statistic on the team's stored rows (set, cells, rows, n, computation) and the range [low, high]
  that someone's account predicts for it on the TEST half of the problems. You do not see the account or its reasons.
- rows/: the stored rows, EXPLORE HALF ONLY (every set was split once by a hash of the problem id; the test half is
  not here). rows/MANIFEST.md lists every cell: its file here, cell name, set and row count. JSON lines with `pid`.
- facts.json: the team's direct facts (offline tests with their measured numbers and board result ids).
- results.md: the title and what lines of every board result of the last 24 hours.
- all_results.md: the id, title and score lines of every board result.
- data.md: the team's stored data as the READMEs describe it (what each results folder holds).

Use Bash with python3 (standard library only) to read the rows and compute.

You are the adversary. Your job is to show that the predicted range is reached without the account. Write the
strongest alternative that predicts the statistic's value from something the account does not need:
- a covariate: accuracy (how many samples are right per problem), answer or response length, cap hits, problem
  difficulty or level, the number of samples, a known difference between the models compared;
- regression to the mean: a subset selected on one noisy measurement, measured again;
- a construction artifact: the statistic or its null comes out in that range by how it is built (a null that fails by
  construction, a grader or extraction rule, ties, abstentions, a shared seed);
- other: anything else that predicts the range without the account.
Compute the statistic itself on the explore rows, then pick the alternative whose value on the explore rows comes
closest to it. Give a computation of the alternative's value that a test runner repeats on the test half before
computing the statistic: step by step, from stored cells of rows/MANIFEST.md (cell names exactly as listed), for
example "take model B's mean gain at each per-problem right count k, weight it by model A's distribution of k". The
value must be one number on the statistic's scale. Report its value on the explore rows as explore_value.

Also check whether a board result (all_results.md, results.md) or a fact already shows this statistic's number on these
rows; if one does, name it in already_shown (the consequence then earns no credit). Name one only if it reports the
same statistic on the same rows, not a related number.

Write adversary.json, one JSON object:
{"kind": "covariate" | "regression to the mean" | "construction artifact" | "other", "alternative": "<the
alternative and why it predicts the statistic>", "cells": ["<cell names of rows/MANIFEST.md>"], "computation": "<step by
step, ending in one number on the statistic's scale>", "explore_value": <the alternative's value on the explore rows>,
"explore_statistic": <the statistic itself on the explore rows>, "already_shown": null or {"result": "result-xxxxxx",
"number": "<the number it shows>"}}
Write only adversary.json (scratch scripts may stay here). Reply with the alternative in one line.
