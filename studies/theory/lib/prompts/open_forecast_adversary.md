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
you do not see it. Your forecasts must come from plain covariates, so that a gap between the account and you measures
what the account adds.

Allowed predictors: stored rows and board numbers of the untrained base model (any prompt, cue, sampling setting, vote
or sample count), of Think-SFT and other models trained without RL, and of random weight edits of a stated norm; and
plain covariates: accuracy, answer length, cap hits, problem difficulty (the base's solve rate per problem), number of
samples, token cap, edit norm (as a number), module type and layer, matrix shape, the dimension of a subspace (chance
overlap k / d).

Forbidden predictors (you may read them, you may not use them in a forecast): anything that embodies a claim about what
the RL change does: a sample, an accuracy, a length or a count of any RL-trained model (RL-Zero-Math, RL-Math 3.0 /
3.1 and their checkpoints, RL-Code, IF-RL, General-RL, the Think model's DPO + RLVR step); the outcome of any edit built
from an RL weight change or its directions (the dial, top-k direction edits, transplants, swaps, pairings, subspace
restrictions of the RL change); any statement about what RL's directions do. A forecast that says "the edit acts like
RL" or "like another RL draw" uses the account's claim and is rejected. A judge reads each forecast's predictors and
derivation, and rejects any forecast that uses a forbidden predictor or is the account's claimed quantity renamed; a
rejected forecast does not count.

First write your rule: one paragraph saying which covariates give which kind of target and how (for example "an edit's
accuracy follows the base's accuracy plus a slope in edit norm fitted on the random edits of item X"). Then apply the
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
