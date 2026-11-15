Use only the Read and Write tools, only on files in the current directory.

mine.json is $side. A different mechanism, which you are not shown, explains the same board items and has
proposed the experiments in open.json, each {id, experiment, unit, gpu_minutes}; a change to the base model also has
"best_known", the best count of right answers the untrained base has on that set, with the board item that states
it. Nobody has run these experiments. Files here:
- DIRECTION.md: the team's research direction.
- before.jsonl: the team's board items (results and knowledge) up to a cutoff, one JSON object per line (id, kind,
  at, who, text).
- inventory.md: the per-problem row files the team has stored and the fields of a row.
- facts.json: numbers earlier rounds computed from stored rows: experiment, recipe, measured value, n, 90 %
  interval. These numbers are known.

For every entry of open.json, state the number the experiment will give if the mechanism in mine.json is right.
Work from that mechanism as written, with the base rates the items report for the same models and settings. Give a
90 % interval: it is scored as a normal distribution (mean value, sd (high - low) / 3.29) by the probability it
gives the measured value, against the other mechanism's prediction, so too wide earns little and too narrow loses
when it misses, and a measured value outside your interval earns at most 0. Where the mechanism implies little, give your best value with an honest interval.

Write cross.json, one JSON object:
{"predictions": [{"id": "<an id from open.json>", "value": 0.42, "low": 0.30, "high": 0.55,
                  "why": "<one sentence: what in the mechanism gives this number>"}]}
with every id of open.json exactly once (an empty list when open.json is empty).

$ask

Write only cross.json. Reply with the number of predictions.
