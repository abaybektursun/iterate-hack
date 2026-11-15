Use only the Read and Write tools, only on files in the current directory.

Files here:
- DIRECTION.md: the team's research direction.
- board.jsonl: every result and knowledge item the team has posted, one JSON object per line (id, kind, at, who,
  text).
- work.md: the open work items with their comments: the jobs that are running now.
- targets.json: numbers these jobs will report. Nobody has seen them yet. Each target has an id, the work item, the
  exact cell (model, prompt, set, n, sampling, samples, grader), the unit and one sentence on what is counted.
$theory
For every target, forecast the number the job will report: a value and a 90 % interval (low, high). The forecast is
scored as a normal distribution (mean value, sd (high - low) / 3.29) by the density it gives the measured value,
against the mixture of two forecasters with no theory. Too wide earns little. Too narrow loses when it misses. Use the
base rates the board reports for the same models, sets and settings. Give the value in the target's unit.

Write forecasts.json, one JSON object:
{"forecasts": [{"id": "t01", "value": 312, "low": 295, "high": 330,
                "reason": "<one sentence: where the number comes from>"}]}
with every id of targets.json exactly once.$nothing

Write only forecasts.json. Reply with the number of forecasts.
