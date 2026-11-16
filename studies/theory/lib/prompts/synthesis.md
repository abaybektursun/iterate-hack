Work only inside the current directory: Read, Write, Glob, Grep and Bash on files here. Never name a path outside it
(no absolute paths, no `..`, no home folder): a run that does is stopped.

Files here:
- rows/: the team's stored problem rows, EXPLORE HALF ONLY. Every problem set (hard328, math500, fresh2026, code; dev100
  is a subset of math500) was split once by a hash of the problem id into an explore half and a test half. You see only
  the explore half; any test of a consequence runs later on the test half, which no writer sees. rows/MANIFEST.md lists
  every cell (one run of one model setting on one set): its file here, its cell name, its set and row count. Each file
  is JSON lines, one row per sample (or per problem), with `pid` the problem id; cells of the same set share pids.
- rows/weights/: the team's committed per-matrix tables of the weights studies (statistics of the model weights
  alone, no generation: norms, top-8 shares, overlaps and capture of one model's change by another's top directions,
  how strongly the next layer reads RL's written directions), for the EXPLORE MATRICES ONLY: the 224 weight matrices
  (q, k, v, o, gate, up, down of 32 layers) were split once by a hash of the matrix name into 112 explore and 112 test
  matrices. The section "Weights tables" of rows/MANIFEST.md lists each table, what one row holds and the model keys.
  Each row has `matrix` (the parameter name), `module` (or `writer`) and `layer`.
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
${consequences}Write account.json, one JSON object:
{"account": ["...", "..."], "marks": [{"fact": "F01", "mark": "explained", "why": "..."}], "worst": ["F03", "F11", "F20"]}

Write only account.json (scratch scripts may stay in this directory). Reply with the account.
