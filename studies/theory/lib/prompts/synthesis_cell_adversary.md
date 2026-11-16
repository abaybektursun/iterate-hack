Work only inside the current directory: Read, Write, Glob, Grep and Bash on files here. Never name a path outside it
(no absolute paths, no `..`, no home folder): a run that does is stopped.

Files here:
- cell.json: a computation from the model weights alone (no generation) that the team has not run: the statistic,
  the models whose weights enter, the matrices and the steps. Someone's account of the RL weight change predicts its
  value; you do not see the account or its prediction.
- rows/weights/: the team's committed per-matrix weights tables, EXPLORE MATRICES ONLY (112 of the 224 matrices); the
  section "Weights tables" of rows/MANIFEST.md lists each table, what one row holds and the model keys.
- rows/: also the stored sampling rows (explore half), listed in rows/MANIFEST.md.
- facts.json: the team's direct facts. results.md, all_results.md: the board's results. data.md: the stored data.

Use Bash with python3 (standard library only) to read the tables and compute.

Predict the number this computation will give, from the strongest plain alternative to any special account: the size
of each model's change, the module type and layer, the base matrix's own spectrum, chance overlap of random subspaces
of that dimension, the singular-value decay, and the nearest numbers the tables already hold (for example the same
statistic for other models or other modules). Calibrate on the tables where you can. Give a 90 % interval you would
bet on, no wider than you need.

Also check whether a committed table already holds this number (the same statistic for the same models and matrices);
if one does, name it in already_in_table.

Write prediction.json, one JSON object:
{"alternative": "<the plain account your number comes from>", "reason": "<which table values calibrate it, one
line>", "value": <predicted>, "low": <90 % low>, "high": <90 % high>, "already_in_table": null or {"table": "<table
name>", "number": "<the number it holds>"}}
Write only prediction.json (scratch scripts may stay here). Reply with the value in one line.
