You work in the repository at the current directory, on a laptop. Allowed: Read, Grep, Glob, Write, and Bash for
reading and listing files and for fetching row files (git, `aws s3 cp`, `modal volume get`) into runs/theory-tests/,
which git ignores. Never run a model forward pass, start a GPU job or download model weights. Write only into $out.

$out/theory.json is a theory. $out/offline.json lists its offline predictions, each with k, experiment, recipe,
value, low, high and refuted_by. $inventory lists the team's row files.

For each offline prediction write one Python script, $out/tests/$theory/p<k>.py, that implements the recipe as
written: the files, the filters, the statistic, how ties and cap hits are counted. Where the recipe is ambiguous,
implement its most literal reading as the main number, and compute the most likely other reading as alt_measured.
Code the prediction's refuted_by condition as written, applied to the main number.

You may open the row files to learn their format (field names, a few rows). Do not compute the recipe's statistic,
or anything close to it, yourself, and do not run your scripts: the pipeline runs each script exactly once after you
finish and records what it prints. This keeps the recipe fixed before anyone sees the number.

A script runs as `python3 <script>` from the repository root, uses the standard library only (subprocess for aws or
git is fine), fetches any file it needs into runs/theory-tests/ when missing, and prints as its last line one JSON
object:
{"measured": <number>, "refuted_by_met": <true or false>, "alt_measured": <number or null>, "example_row": <one input row the statistic used, as a JSON object>}

If a recipe cannot be computed from the stored files (a file or field does not exist), the script prints
{"measured": null, "refuted_by_met": false, "alt_measured": null, "example_row": null} and the note says why.

Then write $out/notes.json: [{"k": 1, "note": "<files used, the ambiguities and the other reading, anything that could make the number wrong>"}], one entry per prediction.

Reply with the scripts' paths.
