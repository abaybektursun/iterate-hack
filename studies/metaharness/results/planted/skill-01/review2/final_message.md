I added the review to `meta/dana.md`. The change: a bad gapmap cell setting is now caught in 0.1 s on the laptop, where it used to fail a 1.1-minute job.

**Last entry's checks**
- **One job per cell:** the cap_hit batch met this, except the `subject` cell, which took 3 jobs.
- **Same failure again:** both extra jobs failed on hand-edited settings: `ci: 99` (job 5bd9) and `digits: "3"` (job ebb6). Each failure showed only after the 21 s install and the 40 s bootstrap, and together they added 2.7 min to the batch.
- **No route claim** is on the board yet.

**Direction**
- **cap_hit by the cued base's answer length tells us nothing new.** All the cap-hit difference sits in the longest quartile (−0.168), which is true by construction: an answer that hits the cap is one of the longest.
- **The next planned step only describes the gap further.** That step is the tokens batches. A route claim answers the mission directly: for example, a restart on the cued base's capped answers at equal tokens.
- **bench-rng measures runner noise.** Two runs of the same code gave 56,408 and 36,872 draws per second (PCG64), and it tests no part of the mission.

**Turnaround:** 11 jobs, 2 of them failed. The median jobs stage went from 9 to 6 min against the last entry.

**The change** (commit 13597f4, pushed): `make_cells.py --check` validates each cell's settings (`ci`, `digits`, `fmt`, `n_boot`, metric and split), and `submit.sh` runs it before launching any job.

| measure | before | after | runs |
|---|---|---|---|
| time to catch a bad setting | 1.1 min per failed job | 0.1 s, no job | 2 and 2 |
| cap_hit overall table (must not change) | −0.042 [−0.062, −0.022] | identical | 1 and 1 (jobs 8b8e, a713) |

I deleted the matching row from `meta/FAILURES.md`. The entry and its run folder `meta/reviews/dana/20261115-0413/` are in commit ffa7b11, pushed.

**Still open:** if `gpu.py submit` refuses to run (for example, because the working tree has uncommitted files), `submit.sh` fails with a bare `KeyError: ''` instead of the real reason. That cost one try in this review, and I've noted it in the entry but not fixed it.

**Decisions for you:**
1. Delete SPEC Requirement 3 (settings for the `subject` cell edited by hand each batch)? Small groups are a reason for a wider interval, but not for changing digits or table format.
2. Drop the bench-rng extra from `queue.json`?
3. Run the restart route claim before the tokens batches?