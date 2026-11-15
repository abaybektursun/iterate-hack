Use only the Read and Write tools, only on files in the current directory.

Files here:
- proposals.json: GPU cells proposed by several agents, each with an id (c01, ...), the cell (model, prompt, set, n,
  sampling, samples, grader, cap), the job file, the command, a readout and its unit.

Several proposals may be the same run with different readouts, or nearly the same run. Merge them so that each GPU
run appears once.

Rules:
- Merge proposals that are the same run apart from the readout: same model or edit, same prompt, same set, same
  sampling. They may differ in n, samples or cap; the merged cell then takes the largest, and each readout says
  which problems and samples it is computed on, so that every proposal's number keeps its meaning.
- Do not merge different models, edits, scales, prompts, sets or sampling settings.
- Inside a merged cell, proposals whose readouts are the same quantity on the same problems share one readout;
  different quantities get separate readouts.
- Every proposal id appears in exactly one readout's "from".
- "job" and "command": one job file and the command that runs the merged cell (from the proposals' commands).

Write merged.json, one JSON object:
{"cells": [{"id": "m01", "cell": {"model": "...", "prompt": "...", "set": "...", "n": "...", "sampling": "...",
            "samples": "...", "grader": "...", "cap": "..."}, "job": "run_cell.py", "command": "...",
            "readouts": [{"id": "m01-r1", "readout": "...", "unit": "...", "from": ["c03", "c17"]}]}]}
Ids m01, m02, ... in order; readout ids <cell id>-r1, -r2, ...

Write only merged.json. Reply with the number of merged cells.
