Use only the Read and Write tools, only on files in the current directory.

Files here:
- new.json: mechanisms proposed this round, each with an id, its family and its statement, in the order proposed.
- earlier.json: mechanisms of earlier rounds (id, statement) and theories in the graveyard (id, statement, why they
  failed).

Find every new mechanism that restates an earlier mechanism, a graveyard entry, or a new mechanism listed before it:
the same cause acting the same way, even in other words or with other numbers. Two mechanisms about the same
experiment with different causes are not duplicates. When unsure, it is not a duplicate.

Write duplicates.json, one JSON object:
{"pairs": [{"new": "<id from new.json>", "earlier": "<id from earlier.json, or an id listed before it in new.json>",
            "reason": "<one line: the shared cause>"}]}
with one pair per duplicate new mechanism (an empty list when there is none).

Write only duplicates.json. Reply with the number of pairs.
