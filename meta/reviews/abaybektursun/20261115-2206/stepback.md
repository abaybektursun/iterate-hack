# Step-back 4 (loop cycle 16), 2026-11-15 22:06 UTC

Read: the entries since step-back 3 in meta/abaybektursun.md (loop cycles 13 to 15 and four by other sessions: 19:45,
20:20, 20:45, 22:00), the loop record, cycle.txt of this folder.

## Target number per cycle (Team line of cycle.py, last 4 h)

| cycle | UTC | median / upper quartile, min | items | results per hour |
|---|---|---|---|---|
| 12 | 17:55 | 54 / 184 | 21 | 6.5 |
| 13 | 18:57 | 51 / 110 | 26 | 8.0 |
| 14 | 19:59 | 43 / 68 | 31 | 9.5 |
| 15 | 21:04 | 48 / 106 | 34 | 10.2 |
| 16 | 22:06 | 14 / 56 | 70 | 19.2 |

Cycles 13 to 16 beat cycles 9 to 12 on both parts (medians 51, 43, 48, 14 against 131, 174, 48, 54 min; rates 8.0 to
19.2 against 3.0 to 6.5 per hour). The gap is large, and it is not the loop's: cycles 9 and 10 held the outage, and
the last window holds many short items (site pages, offline tests on stored rows: 70 items against 21 to 34). For
items with GPU jobs the stages are to-job 3, jobs 50, to-answer 3 min, as before.

## 1. Which changes moved a number, and what they have in common

| change | measured effect | score |
|---|---|---|
| spend line in vast.py ls and up (cycle 13) | read and quoted at 19:31; the account ran empty at 19:50 anyway | no effect |
| 10-minute upload of a running job (cycle 14) | local test 1 of 1; 2 vast.ai jobs since 20:10, 0 part tars in the store | not measurable |
| none (cycle 15) | | |

No loop change of these four cycles helped. What stopped the account from running empty again was a refusal built
by another session (`up` stops at 18 USD per hour), not the printed line: information that the reader may ignore
did not change the outcome, a limit in the tool did.

## 2. What the skill kept naming and never fixed

- Reviews by other sessions: 4 more in 2.5 h. AGENTS.md rule 8, the person's decision, asked since cycle 2.
- Sharding as one command: sessions do it by hand; asked of the person since cycle 9.
- Generation minutes per cell: the only stage left (50 of 56 min for items with jobs). It is compute and study
  design, outside this skill.

## 3. Which section produced nothing over the last four cycles

Section 1 (Direction), as at step-back 3: not run by the loop; other sessions use it. Its deletion waits for the
person. Sections 2 and 3 were used in every cycle; in cycle 15 they found nothing to change.

## 4. Skill edits

None at step-back 3, so nothing to compare or revert. None now: 120 lines.

## Stop rule

Step-backs in a row with no loop change that helped: 1 (this one). The loop stops at 3.
What the records say about the loop's reach: queue wait 0.2 min, 0.2 % of container minutes in failed jobs, to-job
3 min, to-answer 3 min. The waits and failures the loop could remove alone are removed; the rest needs the person
(credits, AGENTS.md) or belongs to study design.
