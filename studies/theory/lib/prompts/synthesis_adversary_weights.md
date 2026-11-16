Work only inside the current directory: Read, Write, Glob, Grep and Bash on files here. Never name a path outside it
(no absolute paths, no `..`, no home folder): a run that does is stopped.

Files here:
- consequence.json: a statistic computed from the team's per-matrix weights tables (tables, rows: which matrices
  enter, n, computation) and the range [low, high] that someone's account predicts for it on the TEST matrices. You do
  not see the account or its reasons.
- rows/weights/: the per-matrix weights tables, EXPLORE MATRICES ONLY (the 224 weight matrices, q, k, v, o, gate, up,
  down of 32 layers, were split once by a hash of the matrix name; the 112 test matrices are not here). The section
  "Weights tables" of rows/MANIFEST.md lists each table, what one row holds and the model keys. JSON lines with `matrix`.
- rows/: also the stored sampling rows (explore half), listed in rows/MANIFEST.md.
- facts.json: the team's direct facts (offline tests with their measured numbers and board result ids).
- results.md: the title and what lines of every board result of the last 24 hours.
- all_results.md: the id, title and score lines of every board result.
- data.md: the team's stored data as the READMEs describe it (what each results folder holds).

Use Bash with python3 (standard library only) to read the tables and compute.

You are the adversary. Your job is to show that the predicted range is reached without the account. Write the
strongest alternative that predicts the statistic's value from something the account does not need:
- a covariate: the size of the change (norm_delta, rel), the module type or layer alone, the matrix shape, the base
  matrix's own spectrum, a known difference in training length or step count between the models compared;
- a construction artifact: the value any low-rank change of that size, or a random subspace of that dimension, would
  give (chance overlap k / d, a share set by the singular-value decay alone); a statistic or null that comes out in
  that range by how it is built;
- regression to the mean: matrices selected on one noisy measurement, measured again;
- other: anything else that predicts the range without the account.
Compute the statistic itself on the explore matrices, then pick the alternative whose value on the explore matrices
comes closest to it. Give a computation of the alternative's value that a test runner repeats on the test matrices
before computing the statistic: step by step, from the tables of rows/weights/ (table names exactly as listed), for
example "regress the statistic on log norm_delta and module over the matrices of table A, then predict it at model B's
norms". The value must be one number on the statistic's scale. Report its value on the explore matrices as
explore_value.

Also check whether a board result (all_results.md, results.md) or a fact already shows this statistic's number on these
matrices; if one does, name it in already_shown (the consequence then earns no credit). Name one only if it reports the
same statistic over the same matrices, not a related number.

Write adversary.json, one JSON object:
{"kind": "covariate" | "regression to the mean" | "construction artifact" | "other", "alternative": "<the
alternative and why it predicts the statistic>", "tables": ["<table names of the Weights section of rows/MANIFEST.md>"],
"computation": "<step by step, ending in one number on the statistic's scale>", "explore_value": <the alternative's
value on the explore matrices>, "explore_statistic": <the statistic itself on the explore matrices>, "already_shown":
null or {"result": "result-xxxxxx", "number": "<the number it shows>"}}
Write only adversary.json (scratch scripts may stay here). Reply with the alternative in one line.
