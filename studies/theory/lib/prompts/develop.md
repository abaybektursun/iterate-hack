Use only the Read and Write tools, only on files in the current directory.

mechanism.json holds one candidate mechanism. Develop it into a testable theory, or abandon it. Files here:
- DIRECTION.md: the team's research direction.
- before.jsonl: the team's board items (results and knowledge) up to a cutoff, one JSON object per line (id, kind,
  at, who, text).
- inventory.md: the per-problem row files the team has stored, how to fetch each, whether it is readable now, and
  the fields of a row. You cannot open the rows; you know them only from this file.
- external.md: published mechanisms, each headed `### <source id> — <title, year>`.
- facts.json: numbers earlier rounds computed from stored rows: experiment, recipe, measured value, n, 90 %
  interval, which theory or rival asked for it, and whether an independent recomputation reproduced it. These numbers are known:
  explain them, do not predict them.

First read the evidence against the mechanism. If items in before.jsonl already contradict it, abandon it: write
result.json as {"abandon": "<the reason, with item ids and verbatim quotes>"}. Abandoning a contradicted mechanism is a
good outcome; a theory built on a contradicted mechanism wastes everyone's tests.

Otherwise write result.json as the theory:

{"name": "$theory",
 "statement": "<one sentence: the mechanism>",
 "scope": "<models, settings and benchmarks it covers, and what it does not cover>",
 "parent": "<a graveyard theory's name if this revises one, else null>",
 "imports": [{"source": "<an external.md source id, exactly as written>", "finding": "...", "how": "<what it does in the mechanism>"}],
 "explains": [{"item": "result-xxxxxx", "quote": "<verbatim from the item, 3 to 15 words>", "how": "<one sentence>"}],
 "conflicts": [{"item": "result-xxxxxx", "quote": "<verbatim>", "how": "<why it does not fit>"}],
 "rival": "<the strongest other explanation of the same items, and the observation that separates the two>",
 "predictions": [
  {"experiment": "<offline: what is computed>", "recipe": "<files and computation, see below>", "unit": "fraction of problems",
   "value": 0.31, "low": 0.25, "high": 0.37, "refuted_by": "<a condition on the computed number, e.g. measured below 0.22>", "gpu_minutes": 0},
  {"experiment": "<a GPU experiment no item reports, exact setting>", "unit": "right of 500", "value": 447, "low": 440, "high": 455,
   "refuted_by": "<the observation that refutes the theory>", "gpu_minutes": 30}]}

Rules:
- "imports" may be an empty list and "parent" may be null.
- Every quote is copied character for character from that item's text in before.jsonl, 3 to 15 words. A script
  checks each quote and rejects the theory on any mismatch. At least 3 entries in "explains". "conflicts" lists the
  items that do not fit; leave it empty only if you looked and found none, and then say so in "scope".
- At least 3 OFFLINE predictions: "gpu_minutes": 0 and a "recipe" that names files from inventory.md marked readable
  now, the filters, the statistic, and how cap hits, ties and missing rows count, precise enough that two people
  would compute the same number. The quantity must be one that no board item reports and that is not in
  facts.json. The recipe states only the
  computation, never the expected result or the theory.
- The offline predictions are about different quantities. Two predictions that one fact makes both right or both
  wrong (the same contrast on another file or another checkpoint) count as one: state the contrast once, and spend
  the others on the mechanism's cause and on a case where the mechanism says the effect should not appear.
- At least 1 offline prediction tests the mechanism, not only the phenomenon: a quantity for which the nearest other
  explanation of the same phenomenon gives a different number. Name that explanation and its number in the
  prediction's "experiment" (for example: a theory that says cap hits rise because entropy drops predicts how far
  the rows' mean log-probability rises; a length-growth explanation of the same cap hits predicts no change).
- At least 1 GPU prediction, on an experiment that runs in under 60 GPU minutes.
- Every prediction has value, low and high (a 90 % interval) and refuted_by. For an offline prediction refuted_by is
  a condition on the computed number that a script can check.
- Choose predictions where the mechanism says something a careful reader of the items would not guess. Two readers
  with no theory will predict the same quantities from the same items; your theory gains only where it beats them.
  Someone will implement each recipe literally and run it once; a wrong prediction refutes the theory.

$intervention
Write only result.json. Reply with the statement, or with "abandon" and the reason.
