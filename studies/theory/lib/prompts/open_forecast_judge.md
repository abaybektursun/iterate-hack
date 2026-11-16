Use only the Read and Write tools, only on files in the current directory.

Files here:
- targets.json: numbers the team's open work items will report. Each target has an id, the cell, the unit and what
  is counted.
- account.json: an account of what the RL weight change does ("account", sentences) and its forecast of every target
  (value, 90 % interval, derivation).
- adversary.json: a covariate-only forecaster's rule and its forecast of every target (value, 90 % interval,
  predictors, derivation). It wrote them without seeing the account.

The covariate-only forecaster may use every stored outcome as DATA (counts, accuracies, lengths of any stored cell,
RL-trained models and edits built from an RL weight change included) with plain covariates (edit norm or scale, kept
share, rank k, layers, module type, subspace dimension, difficulty, sample count, token cap): fits, interpolation,
nearest stored cell. It may not rest a forecast on a claim about what the RL change does or why (a mechanism).

For every target, decide whether the covariate-only forecast is the account's claim BY CONSTRUCTION:
- its derivation rests on a mechanism claim about the RL change ("RL's directions carry the gain", "later layers
  amplify RL's pairs", "direction 1 is a finishing dial", "the edit acts like RL"), not on stored numbers and a
  covariate; or
- the forecast's quantity is the account's claimed quantity renamed, so its value lands where the account's does
  because it is the same claim, not because a fit to stored numbers gives it.
A stored outcome used as a number (a count, an edit norm, a share, a rank) is allowed even when it comes from an RL
model or an RL-derived edit, and even when its value falls inside the account's interval. Decide from the predictors
and derivation, not from how close the two numbers are.

Write judge.json, one JSON object:
{"verdicts": [{"id": "t01", "by_construction": false, "why": "<one line: which predictor or renaming, or why it is a
plain covariate>"}]}
with every id of targets.json exactly once.

Write only judge.json. Reply with the number of targets judged by construction.
