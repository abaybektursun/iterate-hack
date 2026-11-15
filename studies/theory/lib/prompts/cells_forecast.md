Use only the Read and Write tools, only on files in the current directory.

Files here:
- DIRECTION.md: the team's research direction.
- board.jsonl: every result and knowledge item the team has posted, one JSON object per line (id, kind, at, who,
  text).
- known.json: numbers already measured or about to be: "targets" of the team's running jobs, "facts" computed from
  stored per-problem rows.
- cells.json: GPU cells nobody has run. Each has an id, the exact run (model or edit, prompt, set, n, sampling,
  samples, grader, cap) and one or more readouts (id, what is counted, unit). A readout of a cell that changes only
  the untrained base may show "best_base": the best count of right answers a base-only cell has reached on those
  problems, with its board item.
- routes.json: no-reward routes nobody has run (it may be empty): a change to the untrained base alone or to
  Think-SFT, its tokens per problem, its command and the same procedure on RL-Zero-Math. Each has readouts (id, arm,
  set, n, what is counted); a route readout shows "best_base": the best known count without reward at the same or
  fewer tokens per problem. Forecast every readout of routes.json as well.
$theory
For every readout, forecast the number the cell will give: a value and a 90 % interval (low, high). The forecast is
scored as a normal distribution (mean value, sd (high - low) / 3.29) by the density it gives the measured value,
against the mixture of two forecasters with no theory. Too wide earns little. Too narrow loses when it misses, and a measured value outside your interval earns at most 0. Use
the base rates the board reports for the nearest models, sets and settings. Give the value in the readout's unit.

Write forecasts.json, one JSON object:
{"forecasts": [{$key"readout": "m01-r1", "value": 312, "low": 295, "high": 330,
                "reason": "<one sentence: where the number comes from>"}]}
with $every.$nothing

Write only forecasts.json. Reply with the number of forecasts.
