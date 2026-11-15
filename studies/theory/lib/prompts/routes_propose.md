Use only the Read and Write tools, only on files in the current directory.

Files here:
- DIRECTION.md: the team's research direction: the cheapest route to RL's points that uses no reward.
- board.jsonl: every result and knowledge item the team has posted, one JSON object per line (id, kind, at, who,
  text).
- mechanisms.json: your family of mechanisms (family name, the family of causes, and per mechanism its id and
  statement).
- gap.md: what is known about the gap in right answers between the cued untrained base and RL-Zero-Math: result-f39ba8
  (the gap sorted into loop, budget, answer statement, reliability and capability) and the gap anatomy of the
  rlneurons study.
- best_known.json: the best counts reached without reward on hard328 (328 problems) and MATH-500 (500), per model
  (base or think_sft), each with its tokens per problem (all samples) and board item. A route is judged against the
  best row of its own model at the same or fewer tokens.
- known.json: numbers already measured or about to be.
- jobs.md: the GPU job files, their flags (no others exist) and how to run them. studies/theory/jobs/free_cell.py takes
  free prompt text, free opening text and free decoding settings; studies/rlneurons/jobs/run_cell.py takes the cue,
  solved examples (--shots), min-p and restarts. A vote or selection rule is computed afterwards from the job's rows.

Design one no-reward route: the change, from one mechanism of mechanisms.json, that should win right answers back
from the gap most cheaply. Allowed: a change to the untrained base alone (prompt text, opening tokens, decoding
settings, a selection or vote rule over samples, a restart rule, examples written by the base itself) or to Think-SFT.
Not allowed: RL weights, directions or deltas taken from any reward-trained model, any reward, any training.
Run the same procedure on RL-Zero-Math for comparison.

Rules:
- "mechanism": the id of the mechanism behind the route. "gap_parts": which known parts of the gap (gap.md) the
  route wins back and about how many right answers each part allows. "why": one or two sentences from the mechanism.
- "change": the route in one sentence. "model": "base" or "think_sft".
- "command": the command line for the route (several joined with " && "), with job files and flags of jobs.md only;
  "rl_command": the same procedure with the RL model (free_cell.py --model rl, or run_cell.py --model rl).
- "tokens": generated tokens per problem summed over all samples, your estimate. "gpu_minutes": on one L40S 48 GB,
  both commands, at most 240 (a 500-problem MATH-500 cell, one sample, cap 16,384, takes about 100 minutes).
- "readouts": exactly four, right answers with grader v3 (after the vote or selection rule, if any): the route on a
  stated subset of hard328 ("n" problems, say which in "readout": all 328, or for example --shard 0/2 = 164) and on
  MATH-500 (n up to 500), and the RL arm on the same two. Each with "value", "low", "high" (your 90 % interval).
- Prefer a route whose median forecast beats the best known count at equal tokens; do not repeat a row of
  best_known.json or the board.

Write route.json, one JSON object:
{"route": {"mechanism": "<id>", "change": "...", "model": "base", "gap_parts": "...", "why": "...", "command": "...",
           "rl_command": "...", "tokens": 9000, "gpu_minutes": 90,
           "readouts": [{"arm": "route", "set": "hard328", "n": 164, "readout": "...", "value": 90, "low": 80, "high": 100},
                        {"arm": "route", "set": "MATH-500", "n": 500, "readout": "...", "value": 420, "low": 405, "high": 435},
                        {"arm": "rl", "set": "hard328", "n": 164, "readout": "...", "value": 100, "low": 90, "high": 110},
                        {"arm": "rl", "set": "MATH-500", "n": 500, "readout": "...", "value": 440, "low": 425, "high": 452}]}}

Write only route.json. Reply with one line: the route.
