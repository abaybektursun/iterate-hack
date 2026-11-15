You work in the repository at the current directory, read-only. Allowed: the Read, Grep and Glob tools, and Bash only
for ls, cat, head, git ls-files, git log, git show and aws s3 ls. Write exactly one file, $out/inventory.md, and
nothing else.

Task: list every per-problem row file the team has stored: files with one row per problem (or per problem and sample)
of a model's generations or their grades, from which a person could compute a new statistic on a laptop. Look at:
- committed files under studies/*/results/ (`git ls-files studies`);
- S3 keys and Modal Volume paths named in studies/*/README.md and README.md (check that an S3 key exists with
  `aws s3 ls`).

List only files and keys that existed before the cutoff $cutoff: for a committed file, its first commit
(`git log --diff-filter=A --format=%aI -- <path>`) is before the cutoff; for a key or Volume path, a README version
committed before the cutoff names it.

One line per file or key. Files that differ only in a seed, an arm or a run number share one line with a glob:

- <path or key> | <how to fetch: git, `aws s3 cp ...`, `modal volume get ...`> | <model> | <prompt: cue or plain> | <sampling: T, top-p, max tokens> | <benchmark and n> | <samples per problem> | <row fields, e.g. right/wrong per grader version, generated tokens, cap hit, loop flag, answer text present or not>

Rules:
- No accuracies, counts of right answers, differences, gains or any other result numbers in this file: only what
  exists and what a row holds. Agents who must not see results read this file. Settings (T, top-p, n, samples per
  problem, max tokens) are fine.
- Open one row of each file to name its fields. Compute nothing from the rows.

Reply with the number of lines.
