I ran the review. The entry is in `meta/dana.md`, the raw material is in `meta/reviews/dana/20261115-0413/`, and both commits are pushed: 56a8633 (the change) and ed506c9 (the review).

**Direction:** The cap_hit batch shows where the remaining gap comes from: answers the base model doesn't finish. Among the longest quarter of the cued base's answers, the base hits the 16,384-token cap 16.8 points more often than the RL model, CI [-0.246, -0.093] for RL minus base. In the other three quarters the difference is 0.000. That lines up with the +0.256 accuracy gap in the same quarter. The better next step is a route for mission point 3: stop or restart a looping base answer, at equal tokens. The planned tokens batches would only ask the next question about the last result. Of the two runs since the last review, bench-rng tests no part of the mission. Its speed moved 7% between two runs, more than the 3% spread between generators, so it measures noise.

**Research:** The subject split uses a 90% interval in the accuracy batch and 99% in cap_hit, with 4 and 3 digits. Each was set by hand. This undercuts the spec's own reason for comparing tables between batches. The spec still names no closest published experiment.

**Failures and the change:** The failure from the last review happened again. 2 of the 8 cap_hit jobs failed on hand-edited subject settings (`ci: 99`, `digits: "3"`), which cost a 3-minute fix loop. `submit.sh` now runs a settings check, `make_cells.py --check`, before it launches a job. It rejects all 4 broken cell files in git history and accepts both committed ones.

| measure | before | after | runs |
|---|---|---|---|
| seconds from submit to error, broken cell | 67.3 (needed a job) | 0.07 (no job) | 1 and 1 |
| seconds per good cell (must not change) | 61–72 | 61.2 | 6 and 1 |
| cap_hit subject table (must not change) | committed result | rerun job ffa6 | identical |

Those are single runs on each side. I deleted the hand-edit row from `meta/FAILURES.md`, since broken settings can no longer reach a job. The per-job venv row is still open.

**Your call:** I didn't touch your spec's Requirement 3 (subject settings set by hand per batch). I'd suggest removing three things: the unused `fmt` setting, the per-batch `digits`, and bench-rng from `queue.json`.