Use only the Read and Write tools, only on files in the current directory.

You propose theories for a research team. Files here:
- DIRECTION.md: the team's research direction.
- before.jsonl: the team's board items (results and knowledge) up to a cutoff, one JSON object per line (id, kind,
  at, who, text).
- inventory.md: the per-problem row files the team has stored and what a row holds.
- external.md: published findings, each headed `### <source id> — <title, year>`.
- standing/: theories from earlier rounds that still stand (the folder may be empty).
$extra_files
Your start: $start_description

Write the two best theories you can, as $name1.json and $name2.json, one JSON object each, in this form:

{"name": "$name1",
 "statement": "<one sentence: the mechanism>",
 "scope": "<models, settings and benchmarks it covers, and what it does not cover>",
 "parent": "<the name of a standing theory it revises, or null>",
 "imports": [{"source": "<a source id from an external.md heading, exactly as written>", "finding": "<the published finding>", "how": "<what it does in the mechanism>"}],
 "explains": [{"item": "result-xxxxxx", "quote": "<verbatim from the item, 3 to 15 words>", "how": "<one sentence>"}],
 "conflicts": [{"item": "result-xxxxxx", "quote": "<verbatim>", "how": "<why it does not fit>"}],
 "rival": "<the strongest other explanation of the same items, and the observation that separates the two>",
 "predictions": [
  {"experiment": "<a GPU experiment no item reports, exact setting>", "unit": "right of 500", "value": 447, "low": 440, "high": 455,
   "refuted_by": "<the observation that refutes the theory>", "gpu_minutes": 20},
  {"experiment": "<an offline computation no item reports>", "recipe": "<the exact files from inventory.md and the exact computation>",
   "unit": "fraction of problems", "value": 0.31, "low": 0.25, "high": 0.37, "refuted_by": "<...>", "gpu_minutes": 0}]}

A theory is accepted only if it is:
- New: not a standing theory reworded, not a published finding restated.
- Overarching: "explains" cites at least 5 quotes from at least 2 studies. A study is a separate line of work, for
  example sampling results and weight-difference results.
- Risky and exact: it implies numbers that differ from the guess a careful reader would make from the items alone. A
  theory that only restates the items gains nothing when it is scored.
- Accurate: every quote is copied character for character from that item's text in before.jsonl, 3 to 15 words. A
  script checks each quote and rejects the theory on any mismatch. "conflicts" lists the items that do not fit; leave
  it empty only if you looked and found none, and then say so in "scope".
- Testable: at least 3 predictions, each on an experiment no item reports, each with value, low and high (a 90 %
  interval), refuted_by and gpu_minutes. A GPU experiment runs in under 60 GPU minutes. At least 2 predictions are
  offline: computable from row files listed in inventory.md with no GPU, on a quantity no item in before.jsonl
  reports, with "gpu_minutes": 0 and a "recipe": the files, the filters, the statistic, how ties and cap hits are
  counted, precise enough that two people would compute the same number. Someone will implement the recipe
  literally, run it once, and check refuted_by against the result.
$imports_rule

How your theory will be scored: a separate agent who sees only your theory file states values and intervals for
held-out measurements the mechanism speaks about, and these are compared with readers who have no theory. Then your
offline predictions are computed. A clear mechanism with specific consequences is what scores.

Write only the two files. Reply with the two statements.
