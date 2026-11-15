Use only the Read and Write tools, only on files in the current directory.

theory.json is a theory about a research team's results. before.jsonl holds the team's board items up to a cutoff,
one JSON object per line (id, kind, at, who, text). targets_blind.jsonl holds measurements made after the cutoff,
each {id, what, unit}, without their outcomes.

You are the theory's advocate. Take its mechanism as true, as written, and say what it implies about the targets.

$rule

Each claim is a value and a 90 % interval [low, high]. How a claim is scored: the interval is read as a normal
distribution (mean value, sd (high - low) / 3.29). The claim gains the log of the probability density it gives the
measured value, minus the log of the density that two careful readers with no theory gave it, capped at 3 nats either
way. A narrow interval in the right place gains; a narrow interval in the wrong place loses; a wide interval earns
nothing. A measured value outside the claim's own interval earns at most 0.

Write claims.jsonl, one line per claim:
{"id": "t07", "value": 440, "low": 425, "high": 455, "why": "<one sentence: the step from the mechanism to this number>"}

Write only claims.jsonl. Reply with the number of claims.
