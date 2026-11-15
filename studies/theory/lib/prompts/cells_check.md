Use only the Read and Write tools, only on files in the current directory.

Files here:
- board.jsonl: every result and knowledge item the team has posted (id, kind, at, who, text).
- work.md: the open work items with their comments: the jobs running now, each under a heading "## <work id>".
- known.json: numbers already measured or about to be: "targets" (numbers open jobs will report) and "facts".
- candidates.json: proposed GPU cells and no-reward routes, each with an id, the run (or the route and its command)
  and its readouts.

For each candidate, decide whether its readouts are already answered: by an open work item that will report them
(the same model or change, set, sampling and samples, so that its report gives the readout's number), or by a posted
result that already reports them. A candidate that only resembles an item, or differs in model, edit, scale, prompt,
set, sampling, samples or cap, is not answered.

Write answered.json, one JSON object:
{"answered": [{"id": "<candidate id>", "kind": "open" or "posted", "item": "<work id or board item id>",
               "quote": "<exact words copied from that item's text that show it answers the readouts>"}]}
listing only the answered candidates (an empty list when none is).

Write only answered.json. Reply with the number of answered candidates.
