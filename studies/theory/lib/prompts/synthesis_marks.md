Use only the Read and Write tools, only on files in the current directory.

Files here:
- account.json: one account (at most 6 sentences) of what the RL weight change is and why the untrained base, changed
  only at inference, reaches the share of RL's gain that it does. It was written by someone else.
- facts.json: every direct fact the team has: an offline test of one claim about the model, with its verdict (holds,
  refuted or undecided), the measured number and the board result id. Fact ids F01 ... are fixed.

Mark every fact against the account as written, not against what its writer might have meant. For EVERY fact id write
{"fact": "F07", "mark": "explained" | "not addressed" | "contradicts", "why": "<one line>"}:
- explained: a sentence of the account implies the fact's verdict and its number's direction and rough size (a refuted
  fact is explained when the account implies why the claim was false);
- contradicts: the fact goes against a sentence of the account (a number on the other side, a mechanism the account
  rules out, a refuted claim the account asserts); name that sentence in why;
- not addressed: the account implies nothing about it.
Be strict: an account that is vague about a fact does not explain it; a fact that only fits after reading the account
generously is not addressed.

Write marks.json, one JSON object: {"marks": [{"fact": "F01", "mark": "explained", "why": "..."}, ...]}
Write only marks.json. Reply with the counts of each mark and the facts marked contradicts.
