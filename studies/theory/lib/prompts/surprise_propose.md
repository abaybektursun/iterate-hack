Use only the Read and Write tools, only on files in the current directory.

Files here:
- DIRECTION.md: the team's research direction.
- board.jsonl: every result and knowledge item the team has posted, one JSON object per line (id, kind, at, who,
  text).
- work.md: the open work items with their comments: the jobs that are running now.
- direct_facts.json: direct offline tests of earlier mechanisms' causes (mechanism, claim, verdict holds or refuted,
  deciding number, result id). These are the firmest facts the team has; read them first.
- data.md: the team's stored data (README rows naming results/ and data/ paths, and the folders and files under them).
- surprise.json: one number the team measured that both no-theory readers got wrong: what it is, its unit and cell,
  the measured value and the board item that posted it, the two readers' forecasts (value and 90 % interval), every
  forecast made of it, and z (how many of the nearer reader's standard deviations the measured value lies away).
- right.json: the mechanisms that had the measured value inside their interval (it may be empty).
- targets.json: numbers the open jobs will report. Nobody has seen them yet.
- facts.json: numbers computed from stored per-problem rows. graveyard.json: theories that failed and why.
- jobs.md: the GPU job files, their flags (no others exist) and how to run them.
- refuted.json: mechanisms whose forecasts scored well but whose stated cause a direct test refuted (claim, result,
  measured number). Where one bears on this surprise, explain why its forecasts were right although its cause is false:
  what correlate of the true cause it captured. That is where a better mechanism is.

Write two rival mechanisms, a and b, that each explain why the readers were wrong on this number: what the model does
that the readers' reading of the board missed. The two must give different causes, so that they forecast different
numbers somewhere.

Rules for each mechanism:
- It must be consistent with every row of direct_facts.json (say in readers_wrong how, where one bears on it).
- "direct_test": its own direct test on stored data, decidable offline without a GPU run: {"claim": "<the one claim that
  follows from this mechanism's cause and not from its rival's>", "files": ["<stored paths exactly as data.md lists them>"],
  "computation": "<what to compute from them, step by step>", "refuted_if": "...", "threshold": "<a number fixed now>",
  "null": "<the comparison the claim must beat, stronger than random where one exists: for example the base matrix's own
  top directions, or another model's directions>"}. Or, when a posted result already decides the claim,
  {"claim": "...", "decided_by": {"result": "<board id>", "number": "...", "verdict": "holds" or "refuted"}}. A
  mechanism without a runnable direct test is dropped.
- "statement": at most 80 words, plain technical English. "readers_wrong": one or two sentences: why the readers'
  forecasts missed the measured value, from the mechanism.
- "rests_on": 2 or more ids of board.jsonl items whose numbers it explains, the surprise's item among them.
- "holds_against": the two known numbers nearest to contradicting it, each {"item": "<board.jsonl id>"} or
  {"fact": <index in facts.json, from 0>}, with "value" and "why" (why the mechanism still holds).
- "forecasts": forecasts of at least a third of the targets in targets.json, each {id, value, low, high, reason}: a
  value and a 90 % interval in the target's unit and one line of derivation. Leave out targets it says nothing about.
  Each forecast is scored against the two readers by the density it gives the measured value; a measured value
  outside your interval earns at most 0.

The pair must be testable: on 2 or more targets the 90 % intervals of a and b must not overlap, or name one new
"cell" on which they do not overlap: {"cell": {"model", "prompt", "set", "n", "sampling", "samples", "grader", "cap"},
"job": "<file of jobs.md>", "command": "<command line with the flags of jobs.md only>", "readout": "...", "unit": "...",
"why": "...", "gpu_minutes": <at most 120 on one L40S>, "a": {"value", "low", "high"}, "b": {"value", "low", "high"}}.
Never put git in a command ($$(git rev-parse HEAD) or rev-parse): job machines have no .git folder. Where a job takes
--commit, write --commit COMMIT_SHA; the coordinator replaces it with the pushed commit's full sha when submitting.
A cell must not repeat an open work item, a target or a board result. Use "cell": null when the targets suffice.

Write rivals.json, one JSON object:
{"rivals": [{"id": "a", "statement": "...", "readers_wrong": "...", "rests_on": ["result-..."], "holds_against": [...],
             "forecasts": [{"id": "t01", "value": 312, "low": 295, "high": 330, "reason": "..."}],
             "direct_test": {"claim": "...", "files": ["studies/..."], "computation": "...", "refuted_if": "...", "threshold": "...", "null": "..."}},
            {"id": "b", ...}],
 "cell": null}

Write only rivals.json. Reply with one line per mechanism.
