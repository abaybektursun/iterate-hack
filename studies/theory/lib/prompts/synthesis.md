Use only the Read and Write tools, only on files in the current directory.

Files here:
- facts.json: every direct fact the team has: an offline test of one claim about the model, with its verdict (holds,
  refuted or undecided), the measured number (its 90 % interval and n are in the text) and the board result id. Fact
  ids F01 ... are fixed; the order of the list is arbitrary. Read every fact.
- results.md: the title and what lines of every board result of the last 24 hours (the newest experiments, among them
  the edits of the base with RL's 8 top directions per matrix: inputs, outputs, pairs, layer bands, hosts).
- DIRECTION.md: the team's research direction.
- data.md: the team's stored data (README rows naming results/ and data/ paths, and the files and folders under them).
- jobs.md: the GPU job files, their flags (no others exist) and how to run them.

Rival mechanisms written about one surprise at a time have lost to the null. Write instead ONE account of all the
facts together.

1. "account": the shortest single account, at most 6 sentences (a JSON list of sentences), of what the RL weight
   change is and why the untrained base, changed only at inference (prompt, sampling, votes, edits), reaches the
   share of RL's gain that it does. Plain technical English, concrete nouns, numbers where they decide.
2. "marks": for EVERY fact id, {"fact": "F07", "mark": "explained" | "not addressed" | "contradicts", "why": "<one
   line>"}. A refuted fact is explained when the account says why the refuted claim was false. Where a fact goes
   against the account, mark it "contradicts" and name in why which sentence of the account it goes against. Do not
   hide a contradiction behind "not addressed".
3. "worst": the 3 fact ids the account explains worst.
4. "consequences": three new consequences of the account that no fact covers, ids c1, c2, c3. Each is ONE statistic
   computed offline on stored files that exist (paths exactly as data.md lists them), with a range fixed now:
   {"id": "c1", "claim": "<what the statistic measures and why the account puts it in its range>", "why_new": "<why no
   fact or listed result already decides it>", "statistic": "<the one number and its unit>", "files": ["studies/..."],
   "rows": "<which rows enter>", "n": <rows the statistic is computed on, at least 50>, "computation": "<step by step,
   with the 90 % bootstrap interval>", "null": "<the strongest null that exists for this statistic: the base's own
   resample, a random edit of the same norm, another model's directions; random only when nothing stronger exists>",
   "ranges": {"account": [low, high], "null": [low, high]}}. The two ranges must not overlap or touch: the account
   holds only by beating the null. Verdict, applied by the test runner: the consequence holds only if the
   statistic's 90 % interval lies wholly inside the account's range and n is at least 50; inside the null's range or
   between, it is refuted or undecided. Pick statistics where a false account would most likely fail.
5. "cell": one consequence that needs a GPU run: {"readout": "...", "unit": "...", "command": "<command line of a job
   file of jobs.md with its flags only>", "value": <predicted>, "low": <90 % low>, "high": <90 % high>,
   "gpu_minutes": <at most 120 on one L40S>, "why": "<which sentence of the account gives the number>"}. Never put
   git in a command ($$(git rev-parse HEAD) or rev-parse): job machines have no .git folder. Where a job takes
   --commit, write --commit COMMIT_SHA. The cell must not repeat a listed result.

Write account.json, one JSON object:
{"account": ["...", "..."], "marks": [{"fact": "F01", "mark": "explained", "why": "..."}], "worst": ["F03", "F11", "F20"],
 "consequences": [{"id": "c1", "claim": "...", "why_new": "...", "statistic": "...", "files": ["studies/..."], "rows": "...", "n": 120,
                   "computation": "...", "null": "...", "ranges": {"account": [0.6, 1.0], "null": [0.3, 0.5]}}, ...],
 "cell": {"readout": "...", "unit": "...", "command": "...", "value": 180, "low": 170, "high": 190, "gpu_minutes": 40, "why": "..."}}

Write only account.json. Reply with the account.
