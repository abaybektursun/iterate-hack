Use only the Read and Write tools, only on files in the current directory.

Write one account of the team's whole question: how the gap in right answers between the cued Olmo 3 base and the
final RL-Zero-Math model is made up. The account is a budget: 3 to 6 parts, each a mechanism, with shares computed
from stored rows that add up to the gap. Files here:
- DIRECTION.md: the team's research direction.
- before.jsonl: the team's board items (results and knowledge) up to a cutoff, one JSON object per line (id, kind,
  at, who, text).
- graveyard.json: every theory of earlier rounds that failed, with the reason and the tests that decided it.
- carried/: the theories carried from earlier rounds, each with its computed tests (recipe and measured value).
- facts.json: every number computed from stored rows in the previous round (and the rounds it carried): experiment,
  recipe, unit, measured value, n and 90 % interval.
- inventory.md: the per-problem row files, how to fetch each, whether it is readable now, its rows, problems and
  samples per problem, and the fields of a row. You cannot open the rows; you know them only from this file.
- external.md: published mechanisms, each headed `### <source id> — <title, year>`.
- incumbent_account.json: the previous round's account with its measured shares and its rival's result, when there
  is one (an empty list otherwise). Improve on it: keep what its measured shares support, change what they refute.

Choose the gap: one stored cell or a few cells of the cued base and of the final RL model on the same problems and
settings (inventory.md says which rows exist and are readable now). A gap problem is one the RL model gets right and
the base gets wrong (state how right and wrong are read, which grader, and how cap hits and missing rows count).
Write the gap's definition in "gap".

Then split the gap problems into parts. Each part is a mechanism with a rule that a script can apply to the stored
rows of one problem, so that it decides whether that problem belongs to the part. The rules are applied in the order
of the list: a problem goes to the first part whose rule takes it, and a problem no rule takes goes to "unassigned".
So the shares sum to 1 by construction. Parts may be carried mechanisms. A mechanism from graveyard.json may be used
only with a stated reason why the test that refuted it does not apply here (in its "mechanism" text).

Write result.json:

{"name": "$theory",
 "statement": "<one paragraph: the account of the gap, part by part, with the shares you predict>",
 "gap": "<the cells (files from inventory.md), the problems, how right and wrong are read>",
 "parts": [{"name": "<short name>", "mechanism": "<one sentence>", "rule": "<the test on one problem's stored rows>"}],
 "scope": "<what the account covers and what it does not>",
 "parent": "<a graveyard or carried theory's name if this account revises it, else null>",
 "imports": [{"source": "<an external.md source id, exactly as written>", "finding": "...", "how": "..."}],
 "explains": [{"item": "result-xxxxxx", "quote": "<verbatim from the item, 3 to 15 words>", "how": "<one sentence>"}],
 "conflicts": [{"item": "result-xxxxxx", "quote": "<verbatim>", "how": "<why it does not fit>"}],
 "rival": "<the strongest different budget of the same gap, and the number that separates the two>",
 "predictions": [
  {"role": "share", "part": "<a part's name, or unassigned>", "experiment": "<share of the gap problems in this part>",
   "recipe": "<the gap definition and the whole ordered list of rules, then the share of this part>", "unit": "fraction of gap problems",
   "value": 0.31, "low": 0.22, "high": 0.40, "refuted_by": "<a condition on the computed number>", "gpu_minutes": 0},
  {"role": "cross", "part": "<a part's name>", "experiment": "<a number already in stored rows that the account implies about this part>",
   "recipe": "<files and computation>", "unit": "...", "value": 12, "low": 8, "high": 16, "refuted_by": "...", "gpu_minutes": 0},
  {"experiment": "<the base-only intervention that would recover the largest part still open: model, prompt, sampling, set>",
   "unit": "right of 500", "value": 447, "low": 440, "high": 455, "refuted_by": "...", "gpu_minutes": 30}]}

Rules:
- One share prediction for every part and one for "unassigned"; their values sum to 1. Each share recipe states the
  gap definition and the whole ordered list of rules, so that it can be computed alone.
- At least 2 cross-predictions: numbers the stored rows already hold that the account implies about a part and that
  a different budget would get wrong, for example how many problems of a part a stored intervention fixes (the cue,
  a restart on a cap hit, a vote, a weight blend, an intermediate checkpoint).
- At least 1 GPU prediction: the base-only intervention (no training) that the account says would recover the
  largest part still open, with the number of right answers it gives, on an experiment that runs in under 60 GPU
  minutes.
- Every recipe names files from inventory.md marked readable now, the filters, the statistic, and how cap hits, ties
  and missing rows count, precise enough that two people would compute the same number. It states only the
  computation, never the expected result or the account. Someone will implement each recipe literally and run it once.
- Every quote is copied character for character from that item's text in before.jsonl, 3 to 15 words. At least 3
  entries in "explains". A script checks each quote and rejects the account on any mismatch.
- "imports" may be empty and "parent" may be null. Every prediction has value, low and high (a 90 % interval) and
  refuted_by; the interval is scored as a normal distribution against two readers with no theory who predict the
  same quantities, so a share is worth stating exactly where the account knows something they do not.

Write only result.json. Reply with the gap and the parts with their predicted shares.
