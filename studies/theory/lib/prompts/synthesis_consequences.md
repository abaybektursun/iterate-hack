4. "consequences": three or four new consequences of the account that no fact covers, ids c1, c2, ... Each has a
   "kind":
   - "weights" (AT LEAST 2): ONE statistic computed from the weights tables in rows/weights/ alone (for example an
     overlap, a share, a norm, a gain of one matrix on another's directions, compared across modules, layers or the
     models the tables hold), with "tables": [<table names of the Weights section of rows/MANIFEST.md>], "rows": <which
     matrices enter>, "n": <TEST matrices it will be computed on, at least $min_n_weights; the test half has about as many
     matrices of each module as the explore half> and the bootstrap resampling MATRICES. It is tested on the 112 test
     matrices. Stored sampling rows no longer separate accounts of the RL change from plain covariates (round 17: 7 of 9
     dropped); the weights are where accounts have differed.
   - "rows" (AT MOST 2): ONE statistic on stored cells of rows/MANIFEST.md, all of one set, as below.
   For each, BEFORE you fix its range:
   a. Compute the statistic on the explore rows (or explore matrices) here, with a 90 % bootstrap interval that resamples
      problems (pids) or matrices, 2000 resamples. Write it as "explore": {"value": v, "interval": [low, high], "n": <rows
      or matrices it is computed on>}.
   b. Compute the alternative an adversary would offer (rows: accuracy, length, cap hits or difficulty alone; regression
      to the mean on a selected subset; a construction artifact; weights: the size of the change alone, the module or
      layer alone, the base matrix's own spectrum, the share any low-rank change of that size would have, chance overlap
      in that dimension) on the same explore data. If its value lies inside your explore interval OR inside your range,
      the consequence is dropped before any test: pick a statistic where your account and such an alternative differ by
      more than your range.
   c. Fix the range the TEST half must fall in: it must contain your explore value, and its width may be at most
      $range_width times your explore interval's width times sqrt(n explore / n test) (the code checks this).
   {"id": "c1", "kind": "weights" | "rows", "claim": "<what the statistic measures and why the account puts it in its
   range>", "why_new": "<why no fact or listed result already decides it>", "statistic": "<the one number and its unit>",
   for kind weights: "tables": ["anatomy", ...]; for kind rows: "set": "hard328" |
   "math500" | "fresh2026" | "code" | "dev100", "cells": ["<cell names exactly as rows/MANIFEST.md lists them>"],
   "rows": "<which rows enter>", "n": <rows of the test half it will be computed on, at least 50>, "computation":
   "<step by step, so a test runner can repeat it on the test half, with the 90 % bootstrap interval over problems>",
   "explore": {"value": ..., "interval": [..., ...], "n": ...}, "null": "<the strongest null that exists for this
   statistic: the base's own resample, a random edit of the same norm, another model's rows; random only when nothing
   stronger exists>", "ranges": {"account": [low, high], "null": [low, high]}}.
   The account and null ranges must not overlap or touch. Before the test, an adversary who never sees your account,
   only the statistic, cells or tables, rows, computation and your range (and the same explore data), writes the
   strongest alternative that predicts your range without your account, and the test runner computes that
   alternative's value on the test half first. If the adversary's explore value lies inside your explore interval or
   inside your range, the consequence is dropped untested. Verdict on the test half: holds only if the test's 90 %
   interval lies wholly inside your range, n is at least 50 rows ($min_n_weights test matrices for kind weights) and the
   interval excludes the adversary's test-half value; inside the range but containing it is "not separated"; wholly
   outside is refuted. One measurement earns one credit: no two consequences may use the same set of cells or the same
   set of tables, and a number a board result already shows is rejected.
   Do not build a statistic or a row filter on the "deliberative opening" flag of result-1f98b0 (t3open): it misreads
   answers that echo prompt text ($$, = or "Answer" before "Okay"). A statistic that classifies openings in any way
   needs "validation": read the openings of 20 explore rows yourself and report how many your rule classifies right
   (and only use the rule if it gets at least 18).
5. "weights_cell": ONE computation from the model weights alone (no generation) that is in no committed table, where
   your account and the strongest alternative to it predict different numbers: {"statistic": "<the one number and its
   unit>", "models": "<the models whose weights enter: base, RL-Math 3.0 / 3.1 and their checkpoints, RL-Code, IF-RL,
   General-RL, Think-SFT, Think>", "matrices": "<which matrices: modules, layers, all 224>", "computation": "<step by
   step from the weights: which differences, which SVD or projection, which average>", "value": <your predicted value>,
   "low": <90 % low>, "high": <90 % high>, "why": "<which sentence of the account gives the number, and what the
   alternative would predict instead>"}. A blind adversary (it sees the computation, not your account) predicts the same
   number; cells are ranked by the gap between the two predictions in interval widths, so a narrow interval far from
   what the size of the change or chance alone gives ranks first. The engine runs none of them.

Add these two keys to account.json beside account, marks and worst:
"consequences": [{"id": "c1", "claim": "...", "why_new": "...", "statistic": "...", "set": "hard328", "cells": ["rlneurons/day1_3/hard328_base_cue_s4r2-01"],
                   "rows": "...", "n": 150, "computation": "...", "explore": {"value": 0.21, "interval": [0.15, 0.27], "n": 152},
                   "null": "...", "ranges": {"account": [0.10, 0.32], "null": [-0.05, 0.05]}, "kind": "rows"},
                  {"id": "c2", "kind": "weights", "tables": ["cap"], "rows": "...", "n": 56, ...}, ...],
 "weights_cell": {"statistic": "...", "models": "...", "matrices": "...", "computation": "...", "value": 0.3, "low": 0.25, "high": 0.35, "why": "..."}

