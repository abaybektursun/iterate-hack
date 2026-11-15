# Step-back 1 (loop cycle 4), 2026-11-15 08:15 UTC

Read: every entry of meta/*.md (24 by abaybektursun, 5 by sameraslan, 2 by frustea) and the loop record.

## Target number per cycle (Team line of cycle.py, last 1 h)

| cycle | UTC | median / upper quartile, min | items | results per hour |
|---|---|---|---|---|
| 1 | 04:55 (2 h window) | 15 / 69 | 24 | 20.0 |
| 2 | 05:59 | 16 / 46 | 19 | 18.0 |
| 3 | 07:02 | 24 / 124 | 6 | 16.0 |
| 4 | 08:10 | 103 / 171 | 6 | 8.0 |

Last 4 h at 08:10: 31 / 100 min over 45 items, 16.2 results per hour. The 1 h number follows what kind of work closes
in the hour (offline analyses close in about 10 min, GPU items in 1 to 3 h) and how many sessions are active. No change
of the loop can be read from it. From cycle 5 the loop records the 4 h window.

## 1. Which changes moved a number, and what they have in common

| change | measured effect | score |
|---|---|---|
| H100 limit 4 -> 10 running (02:37) | 4 running / 15 queued -> 10 / 8 | helped |
| restarted job runs again (02:25) | 3 jobs and 231 container min lost in 3 h -> 0 in 51 jobs | helped |
| vLLM environment in the image (04:15) | setup median 26 s -> 1 s, 9 jobs | helped, 2 % of container time |
| review notices off for a looped person (05:00) | 3 entries per hour by other sessions -> 0 | helped (agent time, not the target) |
| runs.reload() at job start (frustea, 03:06) | 1 of 1 -> 0 of 9 failing on a new input | helped, then caused the open-file class: 7 + 31 jobs died (05:xx, 07:04-07:18) |
| reservation of 2 H100 removed (07:06) | 0 of 21 long jobs started in 39 min -> 7 of 14 started, median wait 10.0 min (lanes_after_redeploy.txt) | helped, weak: the same hour had the 31 deaths and their fix |
| cycle.py fixes (02:35, 06:08) | measure corrected | no effect on the target |
| paper.py add returns at queued (01:00) | about 60 of 81 min before; after never measured | unknown |

Common to those that helped: each removed a wait or a failure in shared tools or infra, the reviewer could make it
alone within the hour, and job records already held the before number. None is visible in the team median.

Correction to cycle 3: its "9 running / 24 queued after 3 min" counted jobs that a broken container took and killed
(31 deaths 07:04-07:18, fixed 07:22 by one container per job). The queue was not moving as written.

## 2. What the skill kept naming and never fixed

9 lines in meta/abaybektursun.md say "proposal", "not made" or "carried". The same three items return:
- minutes per cell and GPUs per question (entries 21:21, 22:13, 23:30, 03:05, 03:53): study code with another writer;
- four-sample rows kept in a Modal Volume, not in git (03:15, 03:53, 04:15): another writer's script;
- H100 capacity (02:37, 04:36, cycle 1, cycle 3): needs credits; the person has since said Modal credit is nearly used.
Cause: a proposal written into a meta entry is read by the next reviewer, not by the owner of the code. The one case
posted as an idea with its baseline (idea-24bba3) is the only one the person answered.

Skill edit (the one allowed): the rule "a change named and not made is carried to the next entry" becomes "a change the
reviewer cannot make is posted as an idea with its baseline, not carried". Lines: 131 before, 131 after.
It is measured over cycles 5 to 8: proposals in entries that reach an owner (idea claimed or answered), against 1 of 9.

## 3. Which section produced nothing

Section 2 (Research): 19 "Research" lines in 31 entries, 0 changes made from them; in loop cycles 1 to 3 it was not
run. Section 1 (Direction): observations in every entry, 0 changes, but it is what kept two entries from optimizing
runs that test no part of the mission. Section 2 is the candidate for deletion at step-back 2 (cycle 8) if cycles 5 to
7 again make nothing of it.
