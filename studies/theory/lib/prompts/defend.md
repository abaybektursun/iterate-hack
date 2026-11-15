Use only the Read and Write tools, only on files in the current directory.

theory.json is a theory: one mechanism, the board items it explains, and its predictions. tests.json lists offline
computations someone will run once on stored per-problem rows, each {k, experiment, recipe, unit}; nobody has run
them yet. Files here:
- before.jsonl: the team's board items (results and knowledge) up to a cutoff, one JSON object per line (id, kind,
  at, who, text).
- inventory.md: the per-problem row files the team has stored and the fields of a row.
- facts.json: numbers earlier rounds computed from stored rows: experiment, recipe, measured value, n, 90 %
  interval, which theory or rival asked for it, and whether an independent recomputation reproduced it. These numbers are known:
  where a test asks for one of them, or for something that follows from them, use them.

For every entry, state the number the recipe will give if the theory's mechanism is right. Work from the mechanism
as written: what it implies for this quantity, with the base rates the items report for the same models and
settings. Give a 90 % interval: the interval is scored as a normal distribution (mean value, sd (high - low) / 3.29)
by the probability it gives the computed value, against another prediction of the same number, so too wide earns
little and too narrow loses when it misses. Where the mechanism implies little about a quantity, give your best value
with an honest interval.

Write defend.json, a JSON list with one entry per test, every k exactly once:
[{"k": 1, "value": 0.42, "low": 0.30, "high": 0.55, "why": "<one sentence: what in the mechanism gives this number>"}]

Write only defend.json. Reply with the number of entries.
