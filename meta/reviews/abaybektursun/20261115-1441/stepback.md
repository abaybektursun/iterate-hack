# Step-back 2 (loop cycle 8), 2026-11-15 14:41 UTC

Read: the entries since step-back 1 in meta/abaybektursun.md (loop cycles 5 to 7 and four by other sessions), the loop
record, cycle.txt of this folder. The laptop restarted near 14:35 UTC; this cycle ran 3 h 16 min after cycle 7.

## Target number per cycle (Team line of cycle.py, last 4 h)

| cycle | UTC | median / upper quartile, min | items | results per hour |
|---|---|---|---|---|
| 4 | 08:10 | 31 / 100 | 45 | 16.2 |
| 5 | 09:14 | 43 / 124 | 34 | 11.5 |
| 6 | 10:18 | 142 / 210 | 22 | 8.2 |
| 7 | 11:20 | 92 / 210 | 23 | 7.2 |
| 8 | 14:41 | 73 / 131 | 10 | 3.2 |

Both parts of the target are worse than at step-back 1. Fewer items close (45 -> 10 per 4 h), and each takes longer.
Cause in the records, not in the reviews: Modal credit ran out (17 jobs in this window against 105 at 10:18, median
wait 0.1 min), the work moved to vast.ai and AWS L40S where a cell takes 1 to 2 h, and the restart stopped every
session.

## 1. Which changes moved the number, and what they have in common

| change | measured effect | score |
|---|---|---|
| cycle.py reads vast.ai records (cycle 5) | 0 -> 43 jobs listed; 13 of 15 have run minutes now | no effect on the target |
| cycle.py reads AWS records (cycle 6) | 0 -> 2 real jobs listed at 14:47 (aws_listed_1447.txt) | works; no effect on the target |
| stale row deleted from meta/FAILURES.md (cycle 7) | 1 -> 0 | no effect |
| account stage out of the default theory round (theory session, 11:45) | 125 -> 55 min per round, 1 run each; theories with a computed test 9 -> 10 (round-07 run.json, metrics_v4.json) | helped |

None of the loop's three changes moved the target: all three repaired the measure. The one change that cut minutes
deleted a stage of a pipeline and was made by the pipeline's owner. Same pattern as step-back 1: a change helps when
it deletes a wait or a stage and its maker owns the code.

## 2. What the skill kept naming and never fixed

- Minutes per cell: sharding is on main since result-77ca14, and no sharded job is in the 4 h listing (0 commands
  with "shard"). The jobs stage of abaybektursun's items was 129 min at cycle 7.
- GPU capacity: now a question of credits, the person's decision.
- Reviews written by other sessions: 4 since step-back 1 (08:20, 08:45, 09:45, 11:45), because AGENTS.md rule 8 asks
  for them. Waits for the person.

## 3. The skill edit of cycle 4, by its own measure and by the target

| measure | cycles 1 to 4 | cycles 5 to 8 | source |
|---|---|---|---|
| proposals that reached an owner | 1 of 9 carried in entries | 0 of 3 ideas commented or claimed in 6.5 h | board.py show idea-24bba3, idea-019309, idea-06a103 |
| target, 4 h median | 31 min | 43, 142, 92, 73 min | loop record |

The edit beat neither. By the loop's rule it is reverted: the Rules section has its sentence of before 213bd18 again.
The target comparison says nothing about the edit (the cause above is compute); its own measure, 0 of 3, does.
What did reach an owner: one direct message with the exact need (cycle 6, the AWS tool's session), answered in
minutes, 1 of 1. Candidate for step-back 3; not edited in now.

## 4. Which section produced nothing, and the one edit

Section 2 (Research): 0 changes from it in 32 entries, over 8 loop cycles; the loop did not run it in cycles 5 to 7.
Its lines in entries record a published table beside a run (7 entries), which AGENTS.md "Working with the team" rule 2
already asks for before the run. Deleted. Sections 3 and 4 become 2 and 3.

Skill: 131 lines before, 120 after. Measured over cycles 9 to 12: the 4 h target against cycles 5 to 8, and whether
any entry replicates a published experiment (0 found in cycles 5 to 8).

## Stop rule

Step-backs in a row with no loop change that helped the target: 1 (this one). The loop stops at 3.
