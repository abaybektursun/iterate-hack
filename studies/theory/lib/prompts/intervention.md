The intervention. The JSON object you write also has the key "intervention": the one change to the untrained base
model that the mechanism implies should raise its right answers in one cell of the team's chart. A cell is one
problem set, prompt, sampling setting, token cap, grader version, and number of samples and seeds, as DIRECTION.md
and inventory.md name them (a chart line reads like "base MATH-500 378/500 | cue, T 0.6 / top-p 1.0"). Allowed
changes: the prompt or a prefilled opening, the sampling settings, the decoding (stopping, restarts, the cap), and
selection or voting among samples of the base. Not allowed: any training or fine-tuning, the RL model's weights,
and any direction or difference taken from RL weights. The change must not be one that before.jsonl or facts.json
already reports a measured number for.

"intervention": {"change": "<what is changed against the cell's usual setting, exactly>",
                 "model": "<the base checkpoint, as inventory.md or before.jsonl names it>",
                 "cell": {"set": "MATH-500", "prompt": "<the prompt and any prefilled tokens>", "sampling": "T 1.0 / top-p 1.0",
                          "cap": 16384, "grader": "v3", "samples": 1, "seeds": "<seed rule>"},
                 "count": "<what is counted: right answers over which problems, by which grader, how cap hits count>",
                 "unit": "right of 500", "value": 420, "low": 405, "high": 435,
                 "best_known": {"value": 410, "item": "<the before.jsonl item id that states it, or \"facts.json\">",
                                "setting": "<the base-only setting that scored it>"},
                 "gpu_minutes": 30,
                 "why": "<one sentence: what in the mechanism implies this change and this number>"}

- value, low and high are your 90 % interval for the count, scored like every other prediction.
- best_known is the highest count of right answers of the untrained base (any prompt, sampling or selection; no RL
  weights) that before.jsonl or facts.json states for the same problem set, cap and grader, in the same unit.
- gpu_minutes is your estimate of the minutes on one H100. Prefer a change that runs in 30 minutes or less: the
  coordinator runs only those. Stored samples may be reused where the count says how.
- If the mechanism implies no such change, write "intervention": null and "no_intervention": "<one sentence: why>".
