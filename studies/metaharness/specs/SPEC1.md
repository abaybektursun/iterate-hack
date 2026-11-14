# SPEC1: how much the meta harness improves the research

Written 2026-11-14, before any run. Board: work-0efbc5.

## Question

The meta harness is the layer above the research swarm: the `team-meta-review` skill (review, then one change to code
or infrastructure), its instrument `tools/cycle.py`, and the entries in `meta/<name>.md`. Does it make the swarm turn a
question into a correct, mission-relevant answer faster and with less waste, and by how much?

## Closest published work

Found with 16 Exa searches on 2026-11-14; a subagent read the methods and evaluation sections of each (METR: abstract
and introduction only). None is stored with `tools/paper.py` yet, so these are leads for the design and support no claim.

- No paper reports decision-to-first-job minutes or time-to-posted-answer with and without a meta-review step.
- Sibyl-AutoResearch (2605.22343) has the same mechanism (harness changes from recurring process failures) and
  states it is not a controlled comparison: 8 hand-audited events, median latency 1 iteration. Differs: no control.
- AutoResearch at Production Scale (2609.30541): staged introduction of a pre-run fixer and a critic, observational;
  18 % of iterations failed on infrastructure. Differs: no replay, no matched unit of work. Part A is this design.
- Meta-Harness (2603.28052) and Darwin Gödel Machine (2505.22954) ablate the meta loop at a matched budget (same
  proposer, scores-only or fixed meta agent) and score on held-out tasks. Part D is this design; SICA (2504.15228)
  reports high run-to-run variance, so one run per arm supports nothing.
- METR's developer trial (2507.09089): measured time was 19 % slower while self-estimates said 20 % faster. So every
  number here comes from timestamps, none from an agent's or a person's estimate.

## Unit of work

The task mix changes during the day, so raw turnaround compares different work. The fixed unit is the **standard
cell**: one `studies/rlneurons/jobs/run_cell.py` cell on the 328 harder problems (one model, one prompt arm, one
sampling setting), from the claim on the board to the posted number. Day 1 runs it many times.

An **intervention** is the commit named under "Change" in a `meta/<name>.md` entry, with its commit time.

## Metrics

All are recomputed from the raw records (board table, `events/`, `traces/<who>/jobs.json`, job logs, git), never copied
from the meta-review entries, because the entries are written by the layer under test.

| | Metric | Unit | Source |
|---|---|---|---|
| M1 | Turnaround per work item with jobs, split into to-job, jobs, to-answer | minutes | board table, jobs.json |
| M2 | Inside a job: queue wait, setup, model load, generation | minutes | job log timestamps |
| M3 | Wasted compute: container minutes in failed or cancelled jobs | share, with minutes | jobs.json |
| M4 | Mission share: GPU jobs whose work item tests a part of the mission sentence | jobs of jobs | board, DIRECTION.md |
| M5 | Cost of a standard cell | wall minutes and USD | jobs.json, Modal price |
| M6 | Yield: closed results per hour and per USD, whole team | count | board table, jobs.json |
| M7 | Fix latency: first record of a fault to the commit that removes its cause | minutes | job logs, git |

State of the records on 2026-11-14 21:45 UTC: 542 events, 18 GPU submits, 7 closed work items, 2 interventions (one a
skill rename, one named and not landed). Job end times are in each person's Modal Dict; the team store has them only
after `uv run tools/traces.py push` (one `jobs.json` so far, from 20:40). Part A needs a push from every person first.

M4 needs a label per work item (mission, tooling, other). A blind judge sees only DIRECTION.md and the item text. A
person labels 20 items by hand first; the judge is used only if it agrees on at least 18.

## Part A: scorecard of the interventions (no GPU, existing records)

Each meta-review entry ends with "next entry checks", which is a prediction stated before the outcome. For each
intervention: the targeted metric in the window before, the same metric in the window after, and hit or miss.

- Control inside the same window: the stages the change did not target. Everything gets faster as the team warms up,
  so the targeted stage has to fall by more than the untargeted ones.
- Second control: people whose agents ran no meta-review in that window, same wall-clock hours.
- Misses and changes that were named and not made are rows of the table.

Hypothesis A: the targeted stage falls after its intervention by more than the untargeted stages. Refuted if the falls
are equal, or if the targeted stage does not fall.

## Part B: replay of each change (causal, small GPU cost)

For each intervention that changed code or infrastructure, run the same job at the commit before and the commit after:
the first 64 problems of the 328, base with cue, T 1.0 / top-p 1.0, fixed seeds, 3 repeats per side, repeats
interleaved in time. Record M2 and M5 for each.

- The rows of both sides must be identical (seeds are per problem index). A change that alters a row is reported as a
  correctness failure, whatever its speed.
- The 3 repeats give the run-to-run spread (queue wait and container start vary). A change counts when the two sides
  do not overlap.
- Stacking the changes in order gives the cost of a standard cell at the start of the session and now.

Hypothesis B: each change cuts M5 beyond the repeat spread. Refuted for a change whose sides overlap.

## Part C: planted faults (is the review a working instrument?)

A review that reports "slowest stage" has to find a fault that is known to be there. On a separate board table (the
one `tools/selftest.py` uses) and with real CPU jobs, build 8 one-hour windows:

1. setup repeated in every job (a 90 s install at job start),
2. a fix loop (three failed submits, each with a one-line change),
3. two agents working one question without a claim,
4. a run whose answer `tools/recall.py` returns from a stored paper finding,
5. GPU jobs for a work item outside the mission,
6. a runnable Day-1 item left unclaimed for 50 minutes,
7. and 8. two clean windows with none of these.

A fresh agent runs the review on each window, 3 times, without being told what was planted. Scored by a fixed rubric:
the fault named (yes or no), the proposed change removes its cause (yes or no), false alarms on the clean windows.

Baseline: the same model on the same windows with the plain instruction "review how the last hour of work went and
make one improvement", without the skill and without `cycle.py`. This separates the harness from the model.

Hypothesis C: the skill finds more planted faults than the plain instruction and raises no alarm on the clean windows.
Refuted if detection is equal, or if a clean window gets a change.

## Part D (only if time): two swarms on one question queue

Two arms of 3 headless agents each, same model, same token budget, 90 minutes, the same queue of 8 offline questions
whose answers are deterministic computations over stored rows (so each answer can be checked). Arm ON has the full
harness; arm OFF has the board only. Metrics: correct answers per hour, duplicated work, tokens per correct answer.
At least 3 runs per arm; with fewer, report the runs as examples and make no claim.

## What the demo shows

1. Figure 1: session time on x, minutes per work item stacked by stage on y, one vertical line per intervention with
   its label; under it, the wasted-compute share and the mission share over the same axis.
2. Figure 2: per intervention, the cost of the replay cell before and after, with the 3 repeats as dots.
3. Table 1: planted faults found, skill against plain instruction, with the false alarms.

## Threats

- Time: the team speeds up without any review. Handled by the untargeted stages (A) and by the replay (B).
- Few interventions: a session has under ten. Parts A and B report every one; no average is claimed below five.
- Selection: the review picks the slowest stage, which would regress toward the mean anyway. The replay is immune,
  the scorecard is not.
- The review grades itself. All metrics are recomputed from raw records, and Part C uses faults it did not choose.

## Layout

`analysis/scorecard.py` (Part A, reads the team store), `jobs/replay.sh` (Part B), `prep/plant.py` and
`grader/rubric_v1.md` (Part C), `results/<part>/<arm>-<nn>/`.
