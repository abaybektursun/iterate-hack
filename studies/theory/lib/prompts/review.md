You work in the repository at the current directory. Allowed: Read, Grep, Glob; Write only into $out; Bash only for
`python3 tools/recall.py "<query>"`, `python3 tools/exa.py search "<query>"`, `python3 tools/exa.py fetch <url>`,
`uv run tools/board.py ls ...`, `uv run tools/board.py show <id>` (read-only board commands: never post, comment, vote
or close), git log, git show, ls and cat.

You review one theory of a theory round. Files:
- $round/theories/$theory.json: the theory.
- $round/metrics_v3.json, entry "$theory": its advocate's claims about held-out numbers, each with the measured
  value, the two no-theory readers' intervals and the gain in nats; its total gain, interval and its reversal's total.
- $round/tests/$theory.json: its offline predictions, computed once from stored row files by a script written before
  the run (the file may be absent).
- $round/before.jsonl and $round/after.jsonl: board items before and after the cutoff; $round/targets.jsonl: the
  held-out numbers.

Do four things:
1. Refutation. Find the result that contradicts the theory most strongly: in after.jsonl, on the board
   (`board.py ls result knowledge --new --n 60`, `board.py show <id>`), and at the artifact in git when an item names
   one. Check the theory's scope honestly: does it exclude this result?
2. The gains. Look at its largest gains and losses. Which came from the mechanism, and which could a reader have
   reached without it? Does the theory's rival explain the held-out numbers as well?
3. Novelty. Search with `tools/recall.py` and `tools/exa.py search`, at least three phrasings of the mechanism in the
   field's terms. Read the nearest paper's text (fetch), not only its abstract.
4. Imports. Does an imported published finding carry one of its winning claims?

Write $out/review.json:
{"refutation": {"item": "<id, or 'none found'>", "quote": "<verbatim from that item>", "excluded_by_scope": true or false, "note": "<what you read and why it contradicts; if none found, the items you read>"},
 "wins_judgement": "<which gains the mechanism earned and which a reader without it would have made>",
 "rival": "<does the rival explain the held-out numbers as well; which targets separate the two>",
 "novelty": {"nearest": "<nearest published claim>", "url": "<url>", "difference": "<one sentence: what the theory says that the paper does not>", "status": "new or partly published or published"},
 "import_carries_gain": {"yes_no": "yes or no", "which": "<which import carries which winning claim, or why none does>"},
 "verdict": "<stands, refuted, published or weak>: <one sentence>"}

Reply with the verdict.
