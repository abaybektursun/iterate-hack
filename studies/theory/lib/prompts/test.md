You work in the repository at the current directory, on a laptop. Allowed: Read, Grep, Glob, Write, and Bash for
reading and listing files and for fetching row files into runs/theory-tests/ (git ignores it). Never run a model
forward pass, start a GPU job or download model weights. Write only into $out.

$out/theory.json is a theory. $out/offline.json lists its offline predictions, each with k, experiment, recipe,
value, low, high and refuted_by. $inventory lists the team's row files with the exact fetch command for each: S3
needs `--profile $profile` (AWS_PROFILE is set to it), Modal Volume files come with `modal volume get`.

For each offline prediction write one Python script, $out/tests/$theory/p<k>.py, that implements the recipe as
written: the files, the filters, the statistic, how ties, cap hits and missing rows are counted. Where the recipe is
ambiguous, implement its most literal reading as the main number, and compute the most likely other reading as
alt_measured. Code the prediction's refuted_by condition as written, applied to the main number.

Write every script before you run anything. You may fetch the row files and open them to learn their format (field
names, a few rows), but do not compute the recipe's statistic, or anything close to it, yourself, and do not run your
scripts: the pipeline runs each script exactly once after you finish and records what it prints. This keeps the
recipe fixed before anyone sees the number.

A script runs as `PYTHONPATH=<repository root> $run_command <script>` from the repository root. It may import the
standard library, numpy, sympy (with its LaTeX parser, `sympy.parsing.latex.parse_latex`), math_verify (0.9.0) and the
team's graders, and nothing else (subprocess for aws, modal or git is fine). When a recipe grades an answer, import the
grader it names instead of writing your own: grader v3 is `from studies.rlneurons.lib import rln4_lib` (`grade_v3(gold,
text)`, `extract_v3`, `norm_v3`), its equivalence test is `from studies.rlneurons.lib import n13_score` (`grade`,
`extract`), grader v4 is `from studies.rlneurons.grader import repair_v4` (`grade_v4`). Read those files for the exact
signatures. The script fetches any file it needs into runs/theory-tests/ when missing, and prints as its last line one
JSON object:
{"measured": <number>, "refuted_by_met": <true or false>, "alt_measured": <number or null>, "not_computable": null, "example_row": <one input row the statistic used, as a JSON object>}

If the recipe cannot be computed from the stored files (a file is not readable, a field does not exist, the recipe
asks for something the rows do not hold), the script prints
{"measured": null, "refuted_by_met": false, "alt_measured": null, "not_computable": "<the reason>", "example_row": null}
Do not substitute another file or field to get a number.
If the recipe or refuted_by itself says a case counts as refuted without a number (for example an empty group),
the script prints {"measured": null, "refuted_by_met": true, "alt_measured": null, "not_computable": null, "example_row": null}.

Then write $out/tests/$theory/notes.json, next to the scripts: [{"k": 1, "note": "<files used, the ambiguities and the other reading, anything that could make the number wrong>"}], one entry per prediction.

Reply with the scripts' paths.
