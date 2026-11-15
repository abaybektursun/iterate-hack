Use only the Read and Write tools, only on files in the current directory.

before.jsonl holds a research team's board items up to a cutoff, one JSON object per line (id, kind, at, who, text).
inventory.md lists the per-problem row files the team has stored and what a row holds. tests_blind.jsonl holds
computations someone will run on those rows, each {id, experiment, recipe, unit}; nobody has run them yet.

For every entry, predict the number the recipe will give, as a careful reader with no theory: use what before.jsonl
reports about the same models and settings, base rates, and the plain reading of the items. Give a 90 % interval: the
computed value should fall inside it 9 times out of 10. The interval is scored as a normal distribution (mean value,
sd (high - low) / 3.29) by the probability it gives the computed value: too wide earns little, too narrow loses when
it misses.

Write predictions.jsonl, one line per entry, every entry exactly once, ids copied exactly:
{"id": "r4-m01:p1", "value": 0.42, "low": 0.30, "high": 0.55}

Write only predictions.jsonl. Reply with the number of lines.
