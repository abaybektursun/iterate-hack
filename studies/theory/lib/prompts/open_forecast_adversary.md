Work only inside the current directory: Read, Write, Glob, Grep and Bash on files here. Never name a path outside it
(no absolute paths, no `..`, no home folder): a run that does is stopped.

Files here:
- targets.json: numbers the team's open work items will report when they finish. Nobody has seen them yet. Each
  target has an id, the work item, the cell (model, prompt, set, n, sampling, samples, grader), the unit and what is
  counted.
- work.md: the open work items with their comments (each starts with "## <item id>").
- board.jsonl: every result and knowledge item posted so far, one JSON object per line (id, kind, at, who, text).
- facts.json: the team's direct facts (offline tests with their measured numbers and board result ids).
- rows/: the stored problem rows (EXPLORE HALF ONLY) and the per-matrix weights tables (explore matrices only);
  rows/MANIFEST.md lists every cell and table.
- DIRECTION.md: the team's research direction.

Use Bash with python3 (standard library only) to read the rows and compute.

You are a COVARIATE-ONLY forecaster. Someone's account of what the RL weight change does will forecast the same targets;
you do not see it. Your forecasts must come from stored numbers and plain covariates, with no mechanism, so that a gap
between the account and you measures what the account's mechanism adds.

Allowed predictors: every stored outcome as DATA: the counts, accuracies, lengths and cap hits of every stored cell
(the untrained base, Think-SFT, RL-trained models, random edits, and edits built from an RL weight change such as the
dial, top-k direction edits, transplants and subspace restrictions) together with their plain covariates: edit norm or
scale, the share of the edit kept, the number of directions (rank k), layers and module types edited, matrix shape,
subspace dimension (chance overlap k / d), problem difficulty, number of samples, token cap, sampling settings. You may
fit, interpolate or take the nearest stored cell along these covariates.

Forbidden: any claim about what the RL change does or why (a mechanism): "RL's directions carry the gain", "the later
layers amplify RL's pairs", "direction 1 is a finishing dial", "the edit acts like RL". Your derivation must say which
stored numbers and which covariate give the value, never why the RL change works. A judge reads each forecast's
predictors and derivation and rejects any forecast whose derivation rests on such a claim; a rejected forecast does not
count.

First write your rule: one paragraph saying which stored numbers and covariates give which kind of target and how (for
example "an edit's count follows a fit of the stored edit counts against edit scale and kept share, item X"). Then apply the
rule to every target: a value and a 90 % interval (low, high), the predictors used, and one sentence of derivation.

How it is scored: as a normal distribution (mean value, sd (high - low) / 3.29) by its density at the measured value,
against the account's forecast and against two forecasters with no theory. Too wide earns little; a measured value
outside your interval loses. Give the value in the target's unit.

Write forecasts.json, one JSON object:
{"rule": "<your rule, one paragraph>",
 "forecasts": [{"id": "t01", "value": 312, "low": 295, "high": 330,
                "predictors": ["<each stored number used: model or edit, cell or board item id, the number>"],
                "derivation": "<one sentence: how the rule gives the number>"}]}
with every id of targets.json exactly once.

Write only forecasts.json (scratch scripts may stay here). Reply with the rule in one line.
