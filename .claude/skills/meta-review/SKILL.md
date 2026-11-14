---
name: meta-review
description: Review the direction of the research, how it is being done and how its infrastructure is used, not what it found. Every entry reports the experiment turnaround (tools/cycle.py) and makes one change that cuts its slowest stage. Use at the start of a session, after every closed result, after any run whose answer turned out to be published or already known, after every fifth GPU run, and when the user asks whether the work is on the right track or the compute is used well. Appends one short dated entry to meta/<your name>.md.
---

# Meta review

Four reviews, direction first. Each is answered from artifacts, timestamps and git, never from memory, and ends in one entry
of at most ten lines in `meta/<name>.md` (newest first; `<name>` is the part of your git email before the @, so two
people never edit the same file): what was observed with its numbers and sources, the cause, the one
change, and what the next entry checks. An entry that finds nothing wrong says what was checked. Read the previous entry first
and report on its "next entry checks" line.

## The order of every change (Elon Musk's five-step algorithm)

Every change a review proposes, to a study, a pipeline or a document, goes through these five steps in this order. The order
is the point: the common mistake is to speed up or automate a step that should not exist.

1. **Question every requirement.** Each requirement has a named person behind it and a reason; "it is what one does" is not a
   reason. A requirement from a smart person is the most dangerous, because nobody questions it.
2. **Delete the part or the step.** Remove runs, controls, rules, files and document sections. If nothing deleted ever has to
   be put back, not enough was deleted.
3. **Simplify and optimize**, only what survived step 2. Do not optimize a thing that should not exist.
4. **Speed up the cycle.** Shorten the time from question to answer, only after steps 1 to 3.
5. **Automate**, last. Automating a step that still has unquestioned requirements makes the waste permanent.

In each entry, name the step the proposed change belongs to. A change at step 3, 4 or 5 states what steps 1 and 2 found first.

## 1. Direction

Optimizing the path is not the same as checking where it leads. Before the other two reviews:

- Where did we start? Quote the mission and the deliverable as written in `DIRECTION.md`, not as remembered.
- Where did we go? The steps since the last entry, one line each from the board (`board.py ls --new`), the messages and `git log`: what each decided, and whether it moved
  toward the mission's sentence or followed up the previous result.
- Where are we going? The next step as planned. Is it the best next step for the mission, or only the next question about the
  last result? Name the best alternative and say why it is not chosen.
- Which part of the mission's sentence does each recent run test? Count the runs that test none. Has the work drifted to what
  is conventional or easy to measure, away from what only this work would show?
- Is the step in line with the goals and values the owner has stated (truth over the hoped result; no replications; small,
  cheap, decisive runs; the owner's own words on what the work is for)? Name any step that conflicts.

## 2. Research

- Did any run since the last entry reproduce a published experiment or re-derive a known method? Name the run, its cost, the
  paper and the table.
- Before each run, was it set beside the closest published experiment (models, data, metric, numbers), with "differs in X"
  written down?
- Was the strongest conventional method in the first run of the line, or the last?
- For each open step: what does it decide, and could its answer be read from a published table or from rows already stored?
- Is the next step the one the mission asks for, or the one that was easiest to build after the last one?
- What was told to the owner and later narrowed? What rule would have caught it?

## 3. Turnaround and infrastructure

The team's output is set by how fast a question becomes an answer on the board. Every entry reports the turnaround and
makes one change that cuts its slowest stage.

1. Run `uv run tools/cycle.py --hours <hours since the last entry>`. Copy into the entry: the median to-job, jobs and
   to-answer minutes, the slowest stage, the container minutes and the share in failed or cancelled jobs, the median queue
   wait. Set each beside the previous entry's number.
2. Find what the slowest stage was spent on, in the raw material: the job logs (`gpu.py logs <id>`) for the run minutes
   (installs, weight download, model load, the work itself), git timestamps of the spec, code, review and fix commits for
   to-job, the board and messages for to-answer.
3. Check the usual causes, each with its number:
   - setup repeated inside every job (pip installs, a vLLM build, weight downloads) that an image or the model cache could
     hold once;
   - fix loops: a job failed and was resubmitted with a small change, where a one-minute run on the smallest setting
     would have caught it;
   - jobs run one after another that could have run at the same time, while credits or GPU limits sat idle;
   - waiting on a person or another agent;
   - GPU class asked against obtained, estimate against actual, GPU-hours per answered question, runs that could have
     read stored rows.
4. Make the change in the same session: code or infrastructure, pushed. Naming it is not enough. It counts when the next
   entry's numbers show it.

## 4. Failures

Every error, bug and failed run in code or infrastructure since the last entry is a signal. For each one, name the class it
belongs to and remove the cause:

- change the code or the infrastructure so the class cannot happen (one place enters the environment, one helper writes rows,
  one script launches), or
- delete the instruction, note or file that caused it.

Never answer a failure by adding a rule, a reminder or a paragraph to a document: that pollutes the context every later
session has to read, and the cause is still there. A written rule is a last resort and counts as debt. `meta/FAILURES.md`
(one line per class, appended, never rewritten) lists only the classes whose cause is still in place, each with the code change that removes it; delete a row when the change
lands. At each review, also look for context that can be removed: rules that code now enforces, notes that repeat a script,
documents nobody needs to read to do the work.

## Rules

- Short. Every number with its file and key, or the command that gave it.
- One change per entry, and the change is to code, infrastructure or the removal of text, not new text. A change that was
  named and not made is carried to the next entry with the reason.
- Results and findings go on the board (`tools/board.py`). The entry holds only the review.
