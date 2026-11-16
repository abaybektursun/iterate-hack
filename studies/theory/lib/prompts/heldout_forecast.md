Work only inside the current directory: Read, Write, Glob, Grep (and Bash, when you have it) on files here. Never name
a path outside it (no absolute paths, no `..`, no home folder): a run that does is stopped.

Files here:
- cells.json: stored cells the team has ALREADY run whose counts were withheld from you. Each target has an id, the
  cell's description (folder, model or edit label, model repo, prompt, set, n problems, samples, temperature, top_p,
  token cap, seed, and for a weight edit its arguments: recipe, source model `other`, scale, layers, modules, k, onto),
  the unit and what is counted.
- explore_cells.json: the other half of the same stored cells, each with the same description and its count (right
  answers per sample, grader v3).
- board.jsonl: the team's result and knowledge items, one JSON object per line (id, kind, at, who, text), with every
  item that names a withheld cell or states its count removed.
- DIRECTION.md: the team's research direction (lines that state a withheld count removed).
$files
$role

For every target, forecast the cell's count: a value and a 90 % interval (low, high) in the target's unit.

How it is scored: as a normal distribution (mean value, sd (high - low) / 3.29) by its density at the measured count,
against the other forecasters of the same cells. Too wide earns little; a count outside your interval loses.

Write forecasts.json, one JSON object:
{$rule_key"forecasts": [{"id": "h01", "value": 180, "low": 168, "high": 192,$predictors_key
                "derivation": "<one sentence: where the number comes from>"}]}
with every id of cells.json exactly once.

Write only forecasts.json (scratch scripts may stay here). Reply with the number of forecasts.
