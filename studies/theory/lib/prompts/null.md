Use only the Read and Write tools, only on files in the current directory.

before.jsonl holds a research team's board items up to a cutoff, one JSON object per line (id, kind, at, who, text).
targets_blind.jsonl holds measurements the team made after the cutoff, each {id, what, unit}, without their outcomes.

For every target, predict the measured value from what before.jsonl shows, as a careful reader with no theory: use
the closest measured settings, the run-to-run noise the items report, and the trends across settings. Give a 90 %
interval: the measured value should fall inside it 9 times out of 10. The interval is scored as a normal distribution
(mean value, sd (high - low) / 3.29) by the probability it gives the measured value: too wide earns little, too narrow
loses when it misses.

Write predictions.jsonl, one line per target, every target exactly once:
{"id": "t01", "value": 447, "low": 430, "high": 460}

Write only predictions.jsonl. Reply with the number of lines.
