Use only the Read and Write tools, only on files in the current directory.

Files here:
- mechanism.json: a mechanism that forecast the team's new numbers well (statement, the board items it rests on, the
  known numbers nearest to contradicting it, its forecast record). Forecast gain does not confirm its cause: three top
  mechanisms forecast well and failed a direct test of their cause (refuted.json).
- others.json: the other top mechanisms (id, statement).
- refuted.json: the earlier direct tests that refuted a mechanism's cause (claim, result, measured number).
- data.md: the team's stored data: README rows naming results/ and data/ paths, and the folders and files under them.

Write a plan for one direct offline test of this mechanism's cause:
- "claim": the one claim that follows from this mechanism's stated cause and from none of the others' (one sentence).
- "why_only_this": why the others do not imply it.
- "files": the stored paths (exactly as data.md lists them, relative to the repository root) whose rows decide it.
- "computation": what to compute from those files, step by step, so that another agent can run it without asking.
- "refuted_if": the observation that would refute the claim. "threshold": the number fixed now that decides it.
No GPU run: the test must be decidable from stored files.

Write plan.json, one JSON object:
{"claim": "...", "why_only_this": "...", "files": ["studies/.../rows.jsonl"], "computation": "...", "refuted_if": "...",
 "threshold": "..."}

Write only plan.json. Reply with the claim.
