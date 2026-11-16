Work only inside the current directory: Read, Write, Glob, Grep and Bash on files here. Never name a path outside it
(no absolute paths, no `..`, no home folder): a run that does is stopped.

Files here:
- rows/: the team's stored problem rows, EXPLORE HALF ONLY. Every problem set (hard328, math500, fresh2026, code; dev100
  is a subset of math500) was split once by a hash of the problem id into an explore half and a test half. You see only
  the explore half; your consequences are tested later on the test half, which no writer sees. rows/MANIFEST.md lists
  every cell (one run of one model setting on one set): its file here, its cell name, its set and row count. Each file
  is JSON lines, one row per sample (or per problem), with `pid` the problem id; cells of the same set share pids.
- facts.json: every direct fact the team has: an offline test of one claim about the model, with its verdict (holds,
  refuted or undecided), the measured number (its 90 % interval and n are in the text) and the board result id. Fact
  ids F01 ... are fixed. Start from facts $start (listed first): build the account on them, then read every other
  fact and change the account where they require it.
- results.md: the title and what lines of every board result of the last 24 hours.
- DIRECTION.md: the team's research direction.
- data.md: the team's stored data as the READMEs describe it (what each results folder holds; use it to understand
  the cells, but compute only from rows/).
- jobs.md: the GPU job files, their flags (no others exist) and how to run them.

Use Bash with python3 (standard library only: json, statistics, random) to read the rows and compute.

Write ONE account of all the facts together.

1. "account": the shortest single account, at most 6 sentences (a JSON list of sentences), of what the RL weight
   change is and why the untrained base, changed only at inference (prompt, sampling, votes, edits), reaches the
   share of RL's gain that it does. Plain technical English, concrete nouns, numbers where they decide.
2. "marks": for EVERY fact id, {"fact": "F07", "mark": "explained" | "not addressed" | "contradicts", "why": "<one
   line>"}. A refuted fact is explained when the account says why the refuted claim was false. Where a fact goes
   against the account, mark it "contradicts" and name in why which sentence of the account it goes against.
3. "worst": the 3 fact ids the account explains worst.
4. "consequences": three new consequences of the account that no fact covers, ids c1, c2, c3. Each is ONE statistic
   on stored cells of rows/MANIFEST.md, all of one set. For each, BEFORE you fix its range:
   a. Compute the statistic on the explore rows here, with a 90 % bootstrap interval that resamples problems (pids),
      2000 resamples. Write it as "explore": {"value": v, "interval": [low, high], "n": <rows it is computed on>}.
   b. Compute the alternative an adversary would offer (accuracy, length, cap hits or difficulty alone; regression to
      the mean on a selected subset; a construction artifact) on the same explore rows. If its value lies inside your
      explore interval, the consequence is dropped before any test: pick a statistic where your account and such an
      alternative differ on the explore rows.
   c. Fix the range the TEST half must fall in: it must contain your explore value, and its width may be at most
      $range_width times your explore interval's width times sqrt(n explore / n test) (the code checks this). The test
      half has about as many problems as the explore half, so its n is about your explore n.
   {"id": "c1", "claim": "<what the statistic measures and why the account puts it in its range>", "why_new": "<why no
   fact or listed result already decides it>", "statistic": "<the one number and its unit>", "set": "hard328" |
   "math500" | "fresh2026" | "code" | "dev100", "cells": ["<cell names exactly as rows/MANIFEST.md lists them>"],
   "rows": "<which rows enter>", "n": <rows of the test half it will be computed on, at least 50>, "computation":
   "<step by step, so a test runner can repeat it on the test half, with the 90 % bootstrap interval over problems>",
   "explore": {"value": ..., "interval": [..., ...], "n": ...}, "null": "<the strongest null that exists for this
   statistic: the base's own resample, a random edit of the same norm, another model's rows; random only when nothing
   stronger exists>", "ranges": {"account": [low, high], "null": [low, high]}}.
   The account and null ranges must not overlap or touch. Before the test, an adversary who never sees your account,
   only the statistic, cells, rows, computation and your range (and the same explore rows), writes the strongest
   alternative that predicts your range without your account, and the test runner computes that alternative's value
   on the test half first. Verdict on the test half: holds only if the test's 90 % interval lies wholly inside your
   range, n is at least 50 and the interval excludes the adversary's test-half value; inside the range but containing
   it is "not separated"; wholly outside is refuted. One measurement earns one credit: no two consequences may use
   the same set of cells, and a number a board result already shows is rejected.
   Do not build a statistic or a row filter on the "deliberative opening" flag of result-1f98b0 (t3open): it misreads
   answers that echo prompt text ($$, = or "Answer" before "Okay"). A statistic that classifies openings in any way
   needs "validation": read the openings of 20 explore rows yourself and report how many your rule classifies right
   (and only use the rule if it gets at least 18).
5. "cell": one consequence that needs a GPU run: {"readout": "...", "unit": "...", "command": "<command line of a job
   file of jobs.md with its flags only>", "value": <predicted>, "low": <90 % low>, "high": <90 % high>,
   "gpu_minutes": <at most 120 on one L40S>, "why": "<which sentence of the account gives the number>"}. Never put
   git in a command ($$(git rev-parse HEAD) or rev-parse): job machines have no .git folder. Where a job takes
   --commit, write --commit COMMIT_SHA. The cell must not repeat a listed result.

Write account.json, one JSON object:
{"account": ["...", "..."], "marks": [{"fact": "F01", "mark": "explained", "why": "..."}], "worst": ["F03", "F11", "F20"],
 "consequences": [{"id": "c1", "claim": "...", "why_new": "...", "statistic": "...", "set": "hard328", "cells": ["rlneurons/day1_3/hard328_base_cue_s4r2-01"],
                   "rows": "...", "n": 150, "computation": "...", "explore": {"value": 0.21, "interval": [0.15, 0.27], "n": 152},
                   "null": "...", "ranges": {"account": [0.10, 0.32], "null": [-0.05, 0.05]}}, ...],
 "cell": {"readout": "...", "unit": "...", "command": "...", "value": 180, "low": 170, "high": 190, "gpu_minutes": 40, "why": "..."}}

Write only account.json (scratch scripts may stay in this directory). Reply with the account.
