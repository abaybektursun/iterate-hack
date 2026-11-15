Use only the Read and Write tools, only on files in the current directory.

Files here:
- targets.json: numbers that open work items were going to report. Each target has an id, the work item, the exact
  cell (model, prompt, set, n, sampling, samples, grader), the unit and one sentence on what is counted.
- posted.jsonl: the board items posted since, one JSON object per line (id, kind, at, who, text).

For every target, find the measured value in posted.jsonl. It counts only when the item reports the same cell: same
model, prompt, set, n, sampling and samples. A different n, set or setting is not the target's number. Give the value
in the target's unit (convert a percentage of n to a count when the unit is a count, and say so in the note).

Write measured.json, one JSON object:
{"measured": [{"id": "t01", "value": 318, "item": "<result item id>", "quote": "<exact substring of that item's text
               that states the number>", "note": "<one sentence: why this is the target's cell>"}]}
with every id of targets.json exactly once. When no item reports the target's cell, write
{"id": "t02", "value": null, "item": null, "quote": null, "note": "not posted yet"}.

Write only measured.json. Reply with the number of targets measured.
