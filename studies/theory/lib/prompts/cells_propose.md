Use only the Read and Write tools, only on files in the current directory.

Files here:
- DIRECTION.md: the team's research direction.
- board.jsonl: every result and knowledge item the team has posted, one JSON object per line (id, kind, at, who,
  text).
- mechanisms.json: your family of mechanisms (family name, the family of causes they come from, and per mechanism its
  id and statement).$theories
- all_mechanisms.json: every mechanism of every family (id, family, statement). The alternatives come from here.
- known.json: what is already measured or about to be: "targets" are numbers the team's running jobs report (some
  have posted since), "facts" are numbers computed from stored per-problem rows. A new cell must not repeat one.
- jobs.md: the GPU job files of studies/rlneurons/jobs/ as the study's README describes them, how to run them, and
  each file's command-line flags. A cell must run with these job files and flags as they are: no new code, and no
  model that no job supports.

When the team's theories forecast the numbers of its open GPU jobs, they do not separate: those cells were made for
other questions, so every mechanism gives about the same number. Your task: design the cells that would tell the
mechanisms apart.

For each mechanism in mechanisms.json, design one new GPU cell whose result the mechanism gets right and a named,
different mechanism from all_mechanisms.json (preferably from another family) gets wrong. Derive both numbers from
the two mechanisms as written and from the board's numbers for the nearest measured cells.

Rules:
- "cell": the exact run: "model" (a model a job supports, or the edit: which weights, which directions, which
  scale), "prompt", "set", "n" (number of problems, and which ones), "sampling" (temperature, top-p, min-p, seed
  rule), "samples" (per problem, and restarts), "grader", "cap" (token cap).
- "job": the job file in studies/rlneurons/jobs/ that runs it, and "command": the command line as far as jobs.md lets
  you write it (several commands joined with " && " when the cell needs a merge or an edit first).
- Never put git in a command ($(git rev-parse HEAD) or rev-parse): job machines have no .git folder. Where a job takes
  --commit, write --commit COMMIT_SHA; the coordinator replaces it with the pushed commit's full sha when submitting.
- "readout": a number computable from the job's output rows (for example right answers with grader v3, cap hits,
  mean generated tokens, right answers among a named subset), and "unit".
- "value", "low", "high": your mechanism's number and its 90 % interval in that unit. "against": the id of the other
  mechanism; "against_value": the number it gives, outside your interval; "why": one or two sentences on why the two
  mechanisms give different numbers here.
- "gpu_minutes": your estimate on one L40S 48 GB GPU. A 500-problem MATH-500 cell, one sample, cap 16,384, takes
  about 100 minutes there; longer answers, more samples or a merge cost more. Prefer cells of 100 to 200 problems. At
  most 120 minutes.
- "base_only": true when the cell changes only the untrained base (prompt, sampling, decoding, selection; no RL
  weights, no directions or deltas taken from any trained model). For a base_only cell the readout is the number of
  right answers, and "best_base" is {"value": ..., "item": "<board item id>", "note": "..."}: the best count of right
  answers any base-only cell reached on the same problems with the same number of samples (scaled from a larger set
  when the board has no count on these problems; say so in the note). Otherwise "best_base": null.
- Do not repeat a cell or a number in known.json or on the board; a cell may extend one (another scale, another set,
  another cap, a subset).

Write cells.json, one JSON object:
{"cells": [{"mechanism": "<id>", "cell": {"model": "...", "prompt": "...", "set": "...", "n": "...", "sampling": "...",
            "samples": "...", "grader": "...", "cap": "..."},
            "job": "run_cell.py", "command": "...", "readout": "...", "unit": "...",
            "value": 120, "low": 110, "high": 130, "against": "<id>", "against_value": 95, "why": "...",
            "gpu_minutes": 40, "base_only": false, "best_base": null}]}
with exactly one cell per mechanism of mechanisms.json.

Write only cells.json. Reply with the number of cells.
