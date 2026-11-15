---
name: devin
description: Hand side work to Devin, a second coding agent with a free model and your own login, through tools/devin.py, so the research never waits for it. Use whenever a task is off the path to your next result - a code change named by a row of meta/FAILURES.md or by a meta review, a chore on a tool or the site, the analysis script that must be ready when a GPU job ends, the cleanup before a work item closes - and for an independent read of a script, a number or a diff before it is posted or merged. Do not use it for the hypothesis, the spec, the reading of raw outputs, the claim, or anything that needs a GPU.
---

# Devin

Devin does the work you would otherwise do later or never. You do not wait for it: start it, go on with the
research, and read what it did at your next pause (a job just submitted, a job running).

It costs none of your Claude or Codex usage, runs the free model `swe-2-high`, and has read nothing you have read,
which is what makes its review independent.

## Commands

```
python3 tools/devin.py ask "<question>"        read-only, in your checkout; waits, prints the answer (about 1 min)
python3 tools/devin.py run <name> "<task>"     a change, in the background, on branch devin/<name> in its own
                                               worktree, cut from your HEAD; returns at once
python3 tools/devin.py wait <name>             blocks until the run ends, then prints the report and the commits
python3 tools/devin.py ls | show <name> | rm <name>
```

Claude Code: start `wait <name>` with `run_in_background`, and the report arrives by itself. Codex: run `ls` after
every job. `--file <path>` reads a long question or task from a file.

## What to hand over

| When | Command | The task |
|---|---|---|
| A row of `meta/FAILURES.md` names a code change | `run` | the row's change, and "delete the row in the same commit" |
| A meta review names its one change | `run` | the change; you measure `before.txt` meanwhile, since your checkout is untouched |
| You just submitted a GPU job | `run` | the analysis script for the job's output, tested on the smoke run's files, so the number is posted minutes after the job ends |
| Before a number goes on the board | `ask` | "Read `<script>` and `<metrics.json>`. Find the bug that would make `<number>` wrong." |
| Before a diff to shared code is merged | `ask` | "Review `git diff main...<branch>` for bugs. Name file and line." |
| Before a work item closes | `run` | the study's `README.md` index, deleting scratch files |
| A question about code you have not read | `ask` | the question; only the answer enters your context |

Devin's review of `tools/devin.py` itself took 53 s and found four real bugs. A one-line fix with its check and
commit took 40 s.

## Writing the task

Devin starts with `AGENTS.md` and your task, and nothing else: no conversation, no board, no memory. So a task
names the files by path, the change, the command that checks it, and what done looks like. One change per run. A
task you could not check in a minute is too big: split it.

## Taking the result

1. Devin's report is a claim. Read `git diff HEAD...devin/<name>` and run the check yourself.
2. `git merge devin/<name>`, then `python3 tools/devin.py rm <name>`.
3. Do not hand Devin a file you are editing: two writers never edit the same file.
4. Before you close your work item, `ls` shows no run of yours: merge or `rm` each one.

## Limits

- The tool tells Devin to start no job, spend nothing, post nothing to the board and push nothing. You own the
  work item and you post.
- `swe-2-high` is free in the CLI until 2026-11-30 (docs.devin.ai). Any other `--model` spends your Devin credits.
- Devin's cloud sessions are not used: they are not free, and they would need GitHub access to this repository.
- Setup: `devin auth status` prints "Logged in". If not, README, Setup step 9.
