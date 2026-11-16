Use only the Read and Write tools, only on files in the current directory.

Files here:
- targets.json: numbers the team's open work items will report. Each target has an id, the cell, the unit and what
  is counted.
- account.json: an account of what the RL weight change does ("account", sentences) and its forecast of every target
  (value, 90 % interval, derivation).
- adversary.json: a covariate-only forecaster's rule and its forecast of every target (value, 90 % interval,
  predictors, derivation). It wrote them without seeing the account.

The covariate-only forecaster may use stored numbers of the untrained base, of models trained without RL and of random
edits, and plain covariates (accuracy, length, cap hits, difficulty, sample count, token cap, edit norm, module type,
layer, subspace dimension). It may not use a model that embodies the account's claim.

For every target, decide whether the covariate-only forecast is the account's claim BY CONSTRUCTION:
- a predictor is a sample, accuracy, length or count of an RL-trained model (RL-Zero-Math, RL-Math, RL-Code, IF-RL,
  General-RL, the Think model's RL step), or the outcome of an edit built from an RL weight change or its directions
  (the dial, top-k edits, transplants, swaps, pairings, subspace restrictions); or
- the forecast's quantity is the account's claimed quantity renamed (for example "the edit behaves like one more RL
  draw" where the account says the edit is RL's change), so its value lands where the account's does because it is
  the same quantity, not because a covariate predicts it.
A plain covariate is allowed even when its value happens to fall inside the account's interval. Decide from the
predictors and derivation, not from how close the two numbers are.

Write judge.json, one JSON object:
{"verdicts": [{"id": "t01", "by_construction": false, "why": "<one line: which predictor or renaming, or why it is a
plain covariate>"}]}
with every id of targets.json exactly once.

Write only judge.json. Reply with the number of targets judged by construction.
