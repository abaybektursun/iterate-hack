Use only the Read and Write tools, only on files in the current directory.

Files here:
- accounts.json: accounts of the same facts written blind by separate writers ($names): each a short account of what
  the RL weight change is and why the base reaches the share of RL's gain that it does, a mark per fact, its worst
  facts and three new consequences (statistics on stored files with ranges).
- facts.json: the direct facts the accounts mark (ids F01 ...).
- data.md: the team's stored data (README rows naming results/ and data/ paths, and the files and folders under them).

List where the accounts disagree with each other: a claim one account makes that another denies or puts at a
different number, or a fact one marks explained and another marks contradicts. Those disagreements are the most
valuable tests, because at least one account must lose each.

For each disagreement give ONE statistic computed offline on stored files (paths exactly as data.md lists them) that
decides it, and the range each account it separates implies, fixed now; a statistic one of the accounts' own
consequences already uses is fine. Every account range must be disjoint from the null's range, and at least two
account ranges must be disjoint from each other. Leave out accounts that imply nothing about it. n is at least 50.

Write disagreements.json, one JSON object, most decisive disagreement first:
{"disagreements": [{"id": "d1", "about": "<one sentence>", "positions": {"account-1": "...", "account-2": "..."}, "facts": ["F04"],
                    "test": {"claim": "...", "statistic": "<the one number and its unit>", "files": ["studies/..."], "rows": "...", "n": 120,
                             "computation": "<step by step, with the 90 % bootstrap interval>", "null": "<the strongest null>",
                             "ranges": {"account-1": [0.6, 1.0], "account-2": [0.0, 0.2], "null": [0.3, 0.5]}}}]}

At most 4 disagreements. Write only disagreements.json. Reply with one line per disagreement.
