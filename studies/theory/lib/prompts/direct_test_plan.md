Use only the Read and Write tools, only on files in the current directory.

Files here:
- mechanism.json: a mechanism that forecast the team's new numbers well (statement, the board items it rests on, the
  known numbers nearest to contradicting it, its forecast record). Forecast gain does not confirm its cause: three top
  mechanisms forecast well and failed a direct test of their cause (direct_facts.json).
- others.json: the other top mechanisms (id, statement).
- direct_facts.json: every direct test so far (mechanism, claim, verdict, deciding number, result id).
- results.md: every board result's id, title and score lines.
- data.md: the team's stored data: README rows naming results/ and data/ paths, and the folders and files under them.

Write a plan for one direct offline test of this mechanism's cause:
- "claim": the one claim that follows from this mechanism's stated cause and from none of the others' (one sentence).
- "why_only_this": why the others do not imply it.
- "files": the stored paths (exactly as data.md lists them, relative to the repository root) whose rows decide it.
- "computation": what to compute from those files, step by step, so that another agent can run it without asking.
- "refuted_if": the observation that would refute the claim. "threshold": the number fixed now that decides it.
- "null": the comparison the claim must beat, stronger than random where one exists (the base matrix's own top
  directions, another model's directions, a second base sample).
No GPU run: the test must be decidable from stored files. If a posted result in results.md already decides the claim,
write {"claim": "...", "decided_by": {"result": "<id>", "number": "<the deciding number>", "verdict": "holds" or
"refuted"}} instead of a plan.

Write plan.json, one JSON object:
{"claim": "...", "why_only_this": "...", "files": ["studies/.../rows.jsonl"], "computation": "...", "refuted_if": "...",
 "threshold": "...", "null": "..."}

Write only plan.json. Reply with the claim.
