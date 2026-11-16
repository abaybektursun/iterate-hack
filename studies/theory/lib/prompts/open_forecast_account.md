Work only inside the current directory: Read, Write, Glob, Grep and Bash on files here. Never name a path outside it
(no absolute paths, no `..`, no home folder): a run that does is stopped.

Files here:
- account.json: one account of the RL weight change and of the share of RL's gain the untrained base reaches at
  inference ("account", a list of sentences), with its marks of the team's direct facts. You forecast AS THIS ACCOUNT.
- targets.json: numbers the team's open work items will report when they finish. Nobody has seen them yet. Each
  target has an id, the work item, the cell (model, prompt, set, n, sampling, samples, grader), the unit and what is
  counted.
- work.md: the open work items with their comments (each starts with "## <item id>").
- board.jsonl: every result and knowledge item posted so far, one JSON object per line (id, kind, at, who, text).
- facts.json: the team's direct facts (offline tests with their measured numbers and board result ids).
- rows/: the stored problem rows (EXPLORE HALF ONLY) and the per-matrix weights tables (explore matrices only);
  rows/MANIFEST.md lists every cell and table.
- DIRECTION.md: the team's research direction.

Use Bash with python3 (standard library only) to read the rows and compute where it helps.

For every target, forecast the number the work item will report, derived from the account: a value and a 90 %
interval (low, high), and one sentence of derivation that names the sentence of the account and the stored numbers
(board item ids or cells) that give the number.

How it is scored: as a normal distribution (mean value, sd (high - low) / 3.29) by its density at the measured value,
against a covariate-only forecaster who may use the stored rows and plain covariates (accuracy, length, difficulty,
edit norm, module type) but no claim about what the RL directions do, and against two forecasters with no theory.
The account gains only where what it says about the RL change moves the number away from what those covariates give.
Too wide earns little; a measured value outside your interval loses. Give the value in the target's unit.

Write forecasts.json, one JSON object:
{"forecasts": [{"id": "t01", "value": 312, "low": 295, "high": 330,
                "derivation": "<one sentence: which sentence of the account and which stored numbers give it>"}]}
with every id of targets.json exactly once.

Write only forecasts.json (scratch scripts may stay here). Reply with the number of forecasts.
