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
- incumbent_account.json: every earlier account of the chain with its measured shares per cell, its state, its
  replication and its rival's result (an empty list when there is none). Improve on them: keep what their measured
  shares support, change what they refute.

The account must span the team's experiments, not one cell. A cell is one comparison on stored rows: a base side
and an RL side on the same problems and settings. A gap problem of a cell is one the RL side gets right and the base
side gets wrong (state how right and wrong are read, which grader, and how cap hits and missing rows count). Apply one
list of parts to at least 3 cells that differ in at least two of: problem set (MATH-500, the clean harder 328),
sampling (T 0.6, T 1.0), model pair (cued base against final RL; the plain base; intermediate RL checkpoints such as
step 100 and step 400; Code-RL; the 3.0 models; weight blends), as far as inventory.md lists readable rows for them.

A null cell is required: the same rules applied to the cued base against a second, independent sample of the cued
base (inventory.md lists such rows: a fresh base sample, a random-direction weight cell, other seeds). Two samples of
one model also differ, so a part counts as caused by RL only where its share in a model cell exceeds its share in the
null cell. State every share of a model cell twice: as the share and, in "vs_null", as its difference from the null
cell's share; the statement says which parts exceed the null. Report every gap gross and net: in each cell, one
prediction with role "net" gives the count of RL-only problems minus the count of base-only problems.

A budget that a board item already gives for some cell is a claim, not a fact: its labels were made by hand and
your rules may split the same problems differently. List it in "known_claim" with the cell, the shares and the item
id, and apply your own rules to that cell as computed numbers with role "fit" (one per part and for unassigned); fits
are computed and reported but not scored. Your predictions are the shares in cells where no board item gives the
budget. Derive them from the account: for each predicted cell write one sentence ("moves") saying which shares move
against the null cell and the claimed cell, in which direction, and why the mechanisms imply it; the board's number
is context only. A share that only repeats a known number earns nothing: the readers with no theory read the same
items.

One evidence set: a rule that splits the gap by the base's other rows (for example reliability against capability:
the base solves the problem in other samples, or never) uses the same number of independent base rows in every cell,
taken the same way, from rows that exist for every cell you predict. Fix it once in "evidence" (the rows, how many per
problem, the grader version). When a side has only grader v1 scores, the recipe regrades its answers with the study's
grader v3 (the test scripts can import it).

A share that is 0 by construction in a cell (a rule that cannot fire there, for example a loop rule where no loops
are flagged) is declared "by_construction": true with value, low and high 0: it is neither scored nor counted.

Then split the gap problems into parts. Each part is a mechanism with a rule that a script can apply to the stored
rows of one problem, so that it decides whether that problem belongs to the part. The rules are applied in the order
of the list: a problem goes to the first part whose rule takes it, and a problem no rule takes goes to "unassigned".
So the shares sum to 1 in every cell by construction. The same parts and rules
apply to every cell. Parts may be carried mechanisms. A mechanism from graveyard.json may be used
only with a stated reason why the test that refuted it does not apply here (in its "mechanism" text).

Write result.json:

{"name": "$theory",
 "statement": "<one paragraph: the account of the gap, part by part, with the shares you predict>",
 "cells": [{"name": "<short name>", "gap": "<files from inventory.md, models, problem set, sampling, how right and wrong are read>",
            "null": false, "moves": "<for a predicted cell: which shares move against the null and the claimed cell, which way, and why>"}],
 "known_claim": [{"cell": "<a cell name>", "shares": {"<part name>": 0.25, "unassigned": 0.03}, "item": "result-xxxxxx"}],
 "evidence": {"rows": "<the base rows behind every rule that reads other samples, from inventory.md>", "n": 4, "grader": "v3"},
 "parts": [{"name": "<short name>", "mechanism": "<one sentence>", "rule": "<the test on one problem's stored rows>"}],
 "scope": "<what the account covers; a cell of the list above may be left out only by naming the rows that are missing>",
 "parent": "<a graveyard or carried theory's name if this account revises it, else null>",
 "imports": [{"source": "<an external.md source id, exactly as written>", "finding": "...", "how": "..."}],
 "explains": [{"item": "result-xxxxxx", "quote": "<verbatim from the item, 3 to 15 words>", "how": "<one sentence>"}],
 "conflicts": [{"item": "result-xxxxxx", "quote": "<verbatim>", "how": "<why it does not fit>"}],
 "rival": "<the strongest different budget of the same gap, and the number that separates the two>",
 "predictions": [
  {"role": "share", "cell": "<a predicted or the null cell's name>", "part": "<a part's name, or unassigned>", "experiment": "<share of this cell's gap problems in this part>",
   "recipe": "<the cell's gap definition and the whole ordered list of rules, then the share of this part>", "unit": "fraction of gap problems",
   "value": 0.31, "low": 0.22, "high": 0.40, "vs_null": 0.12, "refuted_by": "<a condition on the computed number>", "gpu_minutes": 0},
  {"role": "fit", "cell": "<a claimed cell's name>", "part": "...", "experiment": "...", "recipe": "...", "unit": "fraction of gap problems",
   "value": 0.5, "low": 0.4, "high": 0.6, "refuted_by": "none: a fit", "gpu_minutes": 0},
  {"role": "net", "cell": "<a cell's name>", "experiment": "<RL-only minus base-only problems, with both gross counts>", "recipe": "...",
   "unit": "problems", "value": 40, "low": 30, "high": 50, "refuted_by": "...", "gpu_minutes": 0},
  {"role": "cross", "cell": "<a cell's name>", "part": "<a part's name>", "experiment": "<a number already in stored rows that the account implies about this part>",
   "recipe": "<files and computation>", "unit": "...", "value": 12, "low": 8, "high": 16, "refuted_by": "...", "gpu_minutes": 0},
  {"experiment": "<the base-only intervention that would recover the largest part still open: model, prompt, sampling, set>",
   "unit": "right of 500", "value": 447, "low": 440, "high": 455, "refuted_by": "...", "gpu_minutes": 30}]}

Rules:
- Exactly one null cell ("null": true) and at least 2 predicted model cells (no claimed budget). In the null cell and
  in each predicted cell one share prediction for every part and one for "unassigned", summing to 1; in each claimed
  cell the same as fits. At least 6 share predictions in the predicted model cells that are not 0 by construction.
  Every share of a model cell has "vs_null". Every cell has one "net" prediction. Every offline prediction names its
  cell. Each share or fit recipe states the cell's gap definition, the evidence set and the whole ordered list of
  rules, so that it can be computed alone.
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
