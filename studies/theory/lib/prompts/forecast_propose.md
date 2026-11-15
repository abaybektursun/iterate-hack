Use only the Read and Write tools, only on files in the current directory.

Files here:
- DIRECTION.md: the team's research direction.
- board.jsonl: every result and knowledge item the team has posted, one JSON object per line (id, kind, at, who,
  text).
- work.md: the open work items with their comments: the jobs that are running now.
- targets.json: numbers these jobs will report. Nobody has seen them yet. Each target has an id, the work item, the
  exact cell (model, prompt, set, n, sampling, samples, grader), the unit and one sentence on what is counted.
- readers.json: two forecasters with no theory, {"reader-1": [...], "reader-2": [...]}, each a list of
  {id, value, low, high, reason} with a 90 % interval per target.
- facts.json: numbers the team computed from stored per-problem rows (experiment, recipe, measured value, n, interval).
- graveyard.json: theories that failed earlier, with the reason each failed.

Write $n mechanisms that explain the board's numbers and forecast the targets. A mechanism says what the model does
(how it allocates tokens, when it stops, which errors it makes, what an edit or a prompt changes in its behaviour),
not only which number comes out.

Lens: every mechanism comes from this family of causes: $lens
Search widely inside it: the $n mechanisms should cover different parts of the family, not variations of one idea.

Rules:
- The $n mechanisms are pairwise different: no two rest on the same cause.
- None restates a theory in graveyard.json.
- "statement": at most 80 words, plain technical English.
- "rests_on": 2 or more ids of items in board.jsonl whose numbers the mechanism explains.
- "forecasts": a forecast for at least half of the targets, each {id, value, low, high, reason}: value and a 90 %
  interval in the target's unit, and one line of derivation from the mechanism. Leave out targets the mechanism
  says nothing about.
- On every forecast add "vs_readers": one sentence that starts with "agree" or "disagree" and says why: where the
  mechanism gives the readers' number, say so; where it gives another number, say what the readers miss. Disagree
  only where the mechanism implies it: agreeing earns about 0, a right disagreement earns most, a wrong one
  loses most.
- Each forecast is scored as a normal distribution (mean value, sd (high - low) / 3.29) by the density it gives the
  measured value, against the mixture of the two readers. Too wide earns little. Too narrow loses when it misses.

Write mechanisms.json, one JSON object:
{"mechanisms": [{"id": "f2-m01", "statement": "...", "rests_on": ["result-xxxxxx", "result-yyyyyy"],
                 "forecasts": [{"id": "t01", "value": 312, "low": 295, "high": 330, "reason": "...",
                                "vs_readers": "disagree: ..."}]}]}
Ids f2-m01, f2-m02, ... in order.

Write only mechanisms.json. Reply with the number of mechanisms.
