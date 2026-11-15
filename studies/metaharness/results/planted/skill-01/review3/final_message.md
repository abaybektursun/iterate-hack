I ran the review. Each gapmap job no longer rebuilds its Python environment: setup went from 16 s to 0 s, and the tokens overall table came out identical to the last digit. The entry is the newest one in `meta/dana.md` (commit d0fe6a9, pushed), with its raw files in `meta/reviews/dana/20261115-0421/`.

**Last entry's three checks**
- **Tokens batch:** ran with 0 failed jobs out of 6. The new settings check caught the hand-edited subject cell before any job launched.
- **Requirement 3 and bench-rng:** Requirement 3 is still in `SPEC.md`, and bench-rng still runs.
- **Route claim:** none on the board yet.

**Direction:** all three gapmap batches describe the gap, and none tests a route to the ~11 points (DIRECTION.md point 3). One new number matters for a route: the RL model uses **+761 tokens per problem** more than the cued base (95% interval 495 to 1020). That is the budget a cued-base route may spend at equal tokens. The next planned batch, tokens_both_right, is a fourth description. A better next step is a restart on the cued base's capped answers within that 761-token budget.

**Turnaround:** the median job took 3 min (6 in the last entry). 2 of 15 jobs failed, both left over from the last entry, with 0.1 min queue wait. The slowest stage is the jobs themselves. Each job spent 15–24 s building a fresh venv that installed exactly the package versions the runner image already has, and `cell.py` only imports numpy.

**Change (step 2, delete):** I removed the venv and pip install from `run_cell.sh` and added a check that numpy is version 2.5.4 (commit 604a713). This also removed the gapmap row from `meta/FAILURES.md`.

| measure | before | after | runs |
|---|---|---|---|
| seconds from job start to bootstrap start | 16 (15–24 over 6 jobs) | 0 | 1 and 1 |
| job run time, tokens overall | 45 s | 44 s | 1 and 1 |
| tokens overall table (must not change) | 760.948 [495.14, 1019.8781] | identical | 1 and 1 |

The whole job did not get faster in this one run: the bootstrap took 43 s instead of 29 s, which is CPU noise on the runner. The next entry checks job time over a full batch.

**Decisions for you:**
- **Requirement 2's 1,500,000 resamples:** the bootstrap is now almost all of each job (29–44 s). A rerun with the same seed gives the same table at any resample count, so this count isn't what makes reruns reproducible.
- **Requirement 3 and bench-rng:** both are still in place, as the last entry noted.

**Open bug:** `submit.sh` still fails with a bare `KeyError: ''` when the working tree has uncommitted files. I got around it in this review by stashing my files before submitting; the bug itself is not fixed.