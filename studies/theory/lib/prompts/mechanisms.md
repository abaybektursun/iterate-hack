Use only the Read and Write tools, only on files in the current directory.

You propose candidate mechanisms for a research team. Files here:
- DIRECTION.md: the team's research direction.
- before.jsonl: the team's board items (results and knowledge) up to a cutoff, one JSON object per line (id, kind,
  at, who, text).
- external.md: published mechanisms, each headed `### <source id> — <title, year>`, with the setting where each was
  measured.
- inventory.md: the per-problem row files the team has stored, what a row holds, and whether it is readable now.
- graveyard.json: every theory of earlier rounds, with its state and, for the ones that failed, the reason in one line.
  Most of them failed. Read it first: do not propose them again.

Write mechanisms.json: a JSON list of exactly $n candidate mechanisms, each

{"id": "m01",
 "mechanism": "<one sentence: what in the models causes what, concretely>",
 "starts_from": "<the board item ids, and the one observation this mechanism is built to explain>",
 "import": "<a source id from an external.md heading, or null>",
 "differs_from": "<the nearest other candidates and graveyard entries, and what this one says differently>",
 "first_test": "<the offline computation on files in inventory.md that would most quickly show it wrong>"}

Rules:
- The $n must be pairwise different mechanisms, not different wordings. Two candidates are the same if no single
  experiment could separate them. Check every pair before you write.
- None may restate a graveyard entry. A revision is allowed only when it names the entry and the result that refuted
  it, and changes the mechanism, not the wording.
- At least a third start from an observation that no graveyard theory explained.
- At least a third use an import from a line of work that no graveyard theory used.
- Spread them over different parts of the evidence: sampling behaviour (temperature, truncation, loops, length),
  weight differences, interpretability readouts, item-level structure across problems (which problems are solved by
  which model), differences between RL releases and rewards, grader and format effects. No part gets more than a
  third of the candidates.
- Each must be specific enough that a computation on the stored rows could show it wrong. A mechanism that predicts
  nothing different from the obvious reading of the items is not worth a slot.
- Prefer a mechanism that is surprising and could be wrong over a safe one.

Write only mechanisms.json. Reply with the $n mechanism sentences.
