Use only the Read and Write tools, only on files in the current directory.

Files here:
- consequence.json: a statistic computed offline on the team's stored files (files, rows, n, computation) and the range
  [low, high] that someone's account predicts for it. You do not see the account or its reasons.
- facts.json: the team's direct facts (offline tests with their measured numbers and board result ids).
- results.md: the title and what lines of every board result of the last 24 hours.
- all_results.md: the id, title and score lines of every board result.
- data.md: the team's stored data (README rows naming results/ and data/ paths, and the files and folders under them).

You are the adversary. Your job is to show that the predicted range is reached without the account. Write the
strongest alternative that predicts a value inside that range from something the account does not need:
- a covariate: accuracy (how many samples are right per problem), answer or response length, cap hits, problem
  difficulty or level, the number of samples, a known difference between the models compared;
- regression to the mean: a subset selected on one noisy measurement, measured again;
- a construction artifact: the statistic or its null comes out in that range by how it is built (a null that fails by
  construction, a grader or extraction rule, ties, abstentions, a shared seed);
- other: anything else that predicts the range without the account.
Pick the alternative most likely to land inside the range. Give a computation of the alternative's predicted value for
this statistic that a test runner can do on stored rows before computing the statistic itself: step by step, with the
exact files (paths exactly as data.md lists them, or the consequence's own files), for example "take model B's mean
gain at each per-problem right count k, weight it by model A's distribution of k". The value must be one number on
the statistic's scale.

Also check whether a board result (all_results.md, results.md) or a fact already shows this statistic's number on these
rows; if one does, name it in already_shown (the consequence then earns no credit). Name one only if it reports the
same statistic on the same rows, not a related number.

Write adversary.json, one JSON object:
{"kind": "covariate" | "regression to the mean" | "construction artifact" | "other", "alternative": "<the
alternative and why it predicts a value inside the range>", "files": ["studies/..."], "computation": "<step by step,
ending in one number on the statistic's scale>", "expected": <your guess of that number>, "already_shown": null or
{"result": "result-xxxxxx", "number": "<the number it shows>"}}
Write only adversary.json. Reply with the alternative in one line.
