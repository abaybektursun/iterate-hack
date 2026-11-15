# Step-back 3 (loop cycle 12), 2026-11-15 17:55 UTC

Read: the entries since step-back 2 in meta/abaybektursun.md (loop cycles 9 to 11 and two by other sessions, 16:15 and
17:05), the loop record, cycle.txt and stored_tars.txt of this folder.

## Target number per cycle (Team line of cycle.py, last 4 h)

| cycle | UTC | median / upper quartile, min | items | results per hour |
|---|---|---|---|---|
| 8 | 14:41 | 73 / 131 | 10 | 3.2 |
| 9 | 15:01 | 131 / 184 | 9 | 3.0 |
| 10 | 15:50 | 174 / 376 | 12 | 3.8 |
| 11 | 16:53 | 48 / 274 | 20 | 6.2 |
| 12 | 17:55 | 54 / 184 | 21 | 6.5 |

Last 8 h at 17:55: 54 / 163 min, 35 items, 5.4 per hour. The rate doubled since the outage (12:06 to 14:46 UTC) and
the median is back near 50 min. Most of that is the sessions running again; it is weak evidence for any change.

## 1. Which changes moved a number, and what they have in common

| change | measured effect | score |
|---|---|---|
| vast.py job uploads its outputs at its end (cycle 9) | ended jobs run with it: 6, all 6 in the team store (stored_tars.txt); before, 49 of 77 jobs had no copy and one cell was lost with its box | helped: the loss class is gone for jobs run with it |
| vast.py ls prints GPU use (cycle 9) | another session now reads idle boxes from it (messages 17:22: box 60806873 at GPU 0 % named) | helped, by use |
| idle time reset only by the owner (cycle 9) | test only | unknown |
| hook line when a checkout's tools are old (cycle 10) | active worktrees holding the upload 0 of 4 -> 9 of 10 in an hour, mixed with a direct message | helped, weak |

Common to those that helped, as at step-backs 1 and 2: each removed a failure or a wait in a shared tool, the loop
could make it alone, and the before number was already in records. New here: the cause was found by three read-only
subagents working from job records, transcripts and the board, not by the skill's sections.

## 2. What the skill kept naming and never fixed

- Sharding as one command. Sessions now shard by hand: 16 sharded vast.ai jobs since 15:50. One measured cell
  (MATH-500, 3 samples, 3 shards, jobs e8c2, c0c4, 75f7): 46.5, 62.6 and 57.2 min, so the answer after 62.6 min
  against about 166 min on one box. The one-command form costs credits and waits for the person.
- A checkout that never pulls: cap32run submitted 2 more jobs with the old vast.py (17:36, 17:54) after two direct
  messages. Since 15:05, 29 of 35 vast.ai jobs ran without the upload, most of them from that worktree. The hook line
  cannot reach a checkout that does not pull.
- Reviews by other sessions: 2 more (16:15, 17:05). AGENTS.md rule 8, the person's decision.

## 3. Which section produced nothing over the last four cycles

Section 1 (Direction): 0 changes in loop cycles 9 to 12, and 0 in any entry since the loop began. The loop does not
run it; other sessions do (both entries above start with it), and there it reports whether a result serves the
deliverable. By the loop's rule it should go. It is the skill's first stated purpose, so the loop does not delete it
alone: asked of the person.

## 4. The skill edit of cycle 8 (Research section deleted)

| measure | cycles 5 to 8 | cycles 9 to 12 | source |
|---|---|---|---|
| 4 h target, median min | 43, 142, 92, 73 | 131, 174, 48, 54 | loop record |
| results per hour | 11.5, 8.2, 7.2, 3.2 | 3.0, 3.8, 6.2, 6.5 | loop record |
| entries by other sessions that replicate a published experiment | 0 | 0 of 2 | entries 16:15, 17:05 |

Cycles 9 to 12 do not beat cycles 5 to 8 on the target (medians of the four: 92.5 against 82.5 min). The loop's rule
says revert. Not reverted: the same section would be deleted again at once by the rule "no change in eight cycles",
the comparison is set by the outage, and the edit's own measure did not move. The two rules conflict here; reported
to the person.

Skill edit at this step-back: none. 120 lines.

## Stop rule

Step-backs in a row with no loop change that helped: 0 (the upload helped, by its own measure, as the restart fix did
at step-back 1). No loop change has yet been shown to move the team median itself.
