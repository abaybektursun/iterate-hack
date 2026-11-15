Use only the Read and Write tools, only on files in the current directory.

Files here:
- DIRECTION.md: the team's research direction.
- work.md: every open work item on the team's board, with its comments. An open work item is a GPU job or a tool
  someone is running now. Each item starts with a line "## <item id>".
- board.jsonl: every result and knowledge item posted so far, one JSON object per line (id, kind, at, who, text).

Turn the open work items into forecast targets. A target is one number a work item says it will report when it
finishes: a count of right answers out of n, an accuracy, a difference between two arms, tokens per problem.

Rules:
- One target per number. An item that will report three arms gives three targets.
- The cell must be exact: model, prompt, set, n (problems), sampling (temperature, top-p, token cap), samples per
  problem, grader. Take each field from the item or its comments. Write "not stated" for a field neither gives.
- No target for an item with no countable outcome (site pages, tools, reading, audits).
- No target for a number already stated in the item, in its comments, or in any item of board.jsonl. Check
  board.jsonl for the same cell before you write a target. A rerun of a posted cell with the same setting is not a
  target.
- "quote" is an exact substring of the item's text or of one of its comments in work.md, copied character for
  character, that names the number to be reported. Keep it short (under 200 characters).
- "what" is one plain sentence a reader with no other context can forecast from: the model, the set, the setting
  and what is counted.

Write targets.json, one JSON object:
{"targets": [{"id": "t01", "item": "<work item id>",
              "cell": {"model": "...", "prompt": "...", "set": "...", "n": 500, "sampling": "...", "samples": 1,
                       "grader": "..."},
              "unit": "right answers of 500", "what": "...", "quote": "..."}]}
Ids t01, t02, ... in order. "n" is a number, or "not stated".

Write only targets.json. Reply with the number of targets.
