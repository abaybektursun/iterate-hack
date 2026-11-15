# SPEC2: planted-waste test of the meta harness

Written 2026-11-15, before any review run. Replaces Part C of `SPEC1.md`.

## Question

How good is the meta harness at finding inefficiencies in the swarm's work and removing them? "Meta harness" is the
`team-meta-review` skill with `tools/cycle.py` and the entries it writes to `meta/<name>.md`. A fix counts only when
it removes waste or a repeated mistake. Compute is held fixed: the same job class (Modal CPU, 4 cores), the same limit
of 8 jobs at a time, the same cells, in every window of every arm.

## Design in one paragraph

A small research problem is run through the team's real tools (board, `gpu.py`, the runner) in a private copy of the
repository, with six known inefficiencies planted in it. A fresh agent reviews the work and makes one change. The same
kind of work is then run again on the changed repository, and reviewed again, three rounds in all. One arm's agent is
told to run the skill; the other arm's agent is the same model with a plain instruction and no skill, no `cycle.py`
and no earlier entries. After every round the job records say how much of the compute produced an answer.

## The research problem (the arena study `gapmap`)

`DIRECTION.md` point 2: about 11 points remain between the cued base (T1) and the RL model (T2) at T 1.0. `gapmap`
maps where that difference sits, from the 500 stored per-problem rows
(`studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json`). A batch is one metric (T2 minus T1 per problem):
`accuracy`, `cap_hit`, `tokens`, `tokens_both_right`. Every batch has four required cells, one per split (subject,
level 5, quartile of the RL answer's length, quartile of the cued base answer's length). A cell is one CPU job: a paired
bootstrap over problems, 1,500,000 resamples, seed 0, 23 to 43 s of computing in the pilot. Window k of an arena runs
batch k, so every window is new work of the same shape and size. The arena study's files are in
`prep/arena_template/` (`planted/` and the `clean/` overlay).

## The worker

`prep/worker.py` is a fixed program that does what the arena's repository tells an agent to do: the cells come from
`queue.json` through `prep/make_cells.py`, every launch uses the launch line of the study README, the launcher and the
job are `jobs/submit.sh` and `jobs/run_cell.sh` at that commit. A change a review makes to those files changes what
the next window does. The worker posts a work item per batch on the arena's board, comments on every failure, commits
results and closes the item with the numbers, as `AGENTS.md` asks. What it brings itself is the same in every planted
arena: it gives the `subject` cell its own settings, types two of them wrongly (a different pair in every window), and
corrects one per failed launch.

## Plants (the answer key: `grader/answer_key_v1.json`)

| id | class | where the cause is | what it costs per window (pilot) |
|---|---|---|---|
| P1 | setup repeated inside every job | `jobs/run_cell.sh` builds a venv and installs four packages the image already has | 15 to 25 s in every job |
| P2 | fix loop | `jobs/cell.py` uses three settings only after the bootstrap; nothing runs the smallest setting first | 2 failed jobs, each a full run |
| P3 | check job repeating an earlier one with the same seed | `jobs/submit.sh` launches every cell twice | one more full job per cell |
| P4 | a run whose answer is already stored | `queue.json` has the split `overall`; its table is in `results/overall-01/` and the README | 2 jobs |
| P5 | compute outside the mission | `queue.json` has the extra cell `bench-rng` (speed of numpy's bit generators), with its own work item | 2 jobs |
| P6 | an instruction that makes agents do the wrong thing | the README launch line passes a `--data` path that does not exist | the first job of every window fails |

Two clean windows per arm have none of the six (the `clean/` overlay). The reviewing agents never see the key, the
rubric, this spec or `studies/metaharness/`: the arena's repository has one root commit without them, and its remote
is a local bare repository.

Two classes of the task's list are not planted. "A runnable item left unclaimed while agents do tooling" costs agent
time only, and a scripted worker's idle time is whatever the script says, so its removal could not be measured. "A run
whose answer `recall.py` returns" is planted as P4 with the answer in the repository instead of the team memory,
because posts on a test board are not sent to the memory (`board.py`, `not team.TEST`).

## Arenas (`lib/arena.py`)

One arena per replicate, so no review sees another replicate:
- its own repository and local remote, user `dana`, branch `dana/gapmap`;
- its own board, messages and events: a moto server (local DynamoDB and S3) with the table `iterate-board-test` and
  the team bucket, reached through `AWS_ENDPOINT_URL_*` with `ITERATE_TEST=1`. The tools are unchanged and
  `tools/selftest.py` passes against it. Nothing reaches the live board or the shared test table;
- its own Modal environment `mh-<id>` in sameraslan's workspace, with `infra/runner.py` deployed, so `cycle.py` and
  `gpu.py ls` list only that arena's jobs.

Changes to the arena's copy of the repository, both arms: `studies/metaharness/` removed; `tools/gpu.py` `state()` asks
again when Modal's API call fails (it reported a running job as "died: ConnectionError: Deadline exceeded" in the
first pilot window). Plain arm only: `.claude/skills/team-meta-review/`, `tools/cycle.py` and `meta/` removed, with
every line that names them in `AGENTS.md`, `README.md`, `tools/*.py` and the session-start hook.

## Review runs (`prep/review.py`)

A review run is `claude -p "<prompt>"` in the arena's repository: a new headless Claude Code session, model
`claude-opus-5-5`, with the arena's project files and hooks, no user-level settings, memory, skills or MCP servers,
tools Bash, Read, Edit, Write, Glob, Grep and Skill, at most 90 turns and 40 minutes.

- Skill arm: "Run the team-meta-review skill."
- Plain arm: "Review how the last hour of work went and make one improvement."

Per arena: window 0, review 1, window 1, review 2, window 2, review 3, window 3. A review starts within a minute of
its window's end. A change the session leaves uncommitted is committed for it and recorded.

Runs: 3 planted arenas per arm (9 review runs per arm), 2 clean arenas per arm (window, review, window).

## Measures

Headline, per window, from Modal's start and end records (`grader/score_window.py`):
**waste share = 1 - (bootstrap seconds of the first successful job of each required cell) / (all container seconds)**.
It needs no knowledge of the plants and falls for any change that removes compute that produces no answer. Reported
before the first review and after each round, per arm, with every replicate shown. Next to it: container minutes,
turnaround minutes (work item posted to closed), and answers kept (the 4 required tables equal to
`data/gapmap_reference_v1.json`, which comes from a clean arena). A change that loses or alters an answer is reported
as such and is not counted as waste removed.

Per review run (`grader/rubric_v2.md`): plants named, plants changed, plants removed in the next window, plants that
recur later; other claims; session minutes, turns, USD, job minutes spent by the review.

Clean windows: false alarms (a planted class named as present), and the effect of the review's change on the next
window.

The instrument is checked first: the grader must report all six plants present on a planted pilot window and none on a
clean pilot window, before any review run.

## Hypotheses

- H1 (finds): a skill review names more of the plants present than a plain review. Refuted if the mean number named
  per review run is equal or lower in the skill arm.
- H2 (learns): at equal compute the waste share falls with each skill round. Refuted if the mean waste share after
  round 3 is not below the one before round 1 by more than the spread of the three replicates before round 1, or if a
  removed plant recurs.
- H3 (harness, not model): after round 3 the skill arm's waste share is below the plain arm's. Refuted if the plain
  arm's is equal or lower, or if the two arms' replicate ranges overlap.
- H4 (no false alarm): a skill review of a clean window names none of the six classes and its change neither raises
  the next window's waste share by more than 5 points nor alters an answer. Refuted by either.

Prediction, stated before the runs: both arms name P2 and P6 (failed jobs are loud). The skill arm names P1 and P3
more often, because the skill's section 3 lists "setup repeated inside every job" and asks for the job logs, and P5
more often, because its section 1 counts runs that test no part of the mission. The skill's rule of one change per
entry caps it at three plants removed in three rounds; a plain review that changes several things at once could
remove more, which would refute H3.

With fewer than 3 finished arenas in an arm, the arm's numbers are reported as examples and no claim is made.

## Threats

- The worker is scripted. Its waste is real container time on real jobs, but it responds to a review only through the
  files it runs. A review that fixes a cause somewhere the worker does not read gets no credit; every such case is
  listed with the review's diff.
- One change per round. With six plants and three rounds, the waste share after round 3 depends on which plant a
  review picks first. The per-plant table shows the order.
- Small n: 3 arenas per arm. Ranges are shown, no test is run.
- The skill arm keeps `meta/` with the five real entries of 2026-11-14; they are part of the harness under test.
- Job times vary between Modal containers (bootstrap 23 to 43 s for the same work in the pilot), so the waste share of
  an unchanged repository moves by a few points between windows. The clean arenas give that floor and its spread.

## Layout

`prep/arena_template/` (the arena study), `lib/arena.py`, `prep/build.py`, `prep/worker.py`, `prep/review.py`,
`prep/run_arena.py` (one arena from window 0 to the last window), `grader/answer_key_v1.json`, `grader/rubric_v2.md`,
`grader/score_window.py`, `analysis/planted_readout.py`, `data/gapmap_overall_v1/`, `data/gapmap_reference_v1.json`,
`results/planted/<arm>-<nn>/` and `results/clean/<arm>-<nn>/` (each: `run.json`, `metrics.json`, the windows' scores,
every review's entry, final message and diff), `results/planted/summary-01/` (the table and the chart).
