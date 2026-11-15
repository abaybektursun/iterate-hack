I added `studies/gapmap/jobs/submit_batch.py`, which runs a whole batch with one command. It should cut each of the remaining two batches (`tokens`, `tokens_both_right`) from about 6 minutes to about 2. I tested it only against a stub runner, so no real batch has run through it yet.

**What I found in the last hour.** The `accuracy` and `cap_hit` batches each took about 6 minutes. The job logs show where the time went:
- **Serial launches:** each cell runs for about 50 s (15 s to set up the environment, 30 s of bootstrap), plus a verification rerun after it. The `subject` cell went first and the other five only after it finished, so each batch waited through two of those cell-plus-rerun rounds.
- **Hand typos:** both batches needed 2 fix commits for the hand-edited `subject` cell. `accuracy` had `ci: 90` and `"cvs"`; `cap_hit` had `ci: 99` and `digits: "3"`. The `check_cell.py` added at 20:01 now catches these, but only one cell at a time.
- **Manual results step:** the results folder and `run.json` were put together by hand each time.

**The change** (commit `73e149f`, pushed to `dana/gapmap`):
- **Checks first:** it checks every cell and that the commit is pushed, and launches nothing if any check fails.
- **Parallel launch:** it runs `submit.sh` for every cell at the same time, keeping each cell's verification rerun.
- **Results written for you:** it copies each cell's output into the next free `results/<batch>-NN/` and writes `run.json`.
- **Failures are loud:** if a cell fails, it prints that cell's output and writes no results folder.

**Testing.** I ran it against a stub `submit.sh` in a scratch repo:
- Four cells of 2 s each finished in 2.4 s total, so they ran in parallel.
- A cell with `ci: 90`, an unpushed commit, and a failing cell each stopped the batch.
- A second run wrote to the next folder number.

The README's "How to run" now uses the new script. `submit.sh` still works for running one cell.

There are two more savings I didn't make:
- **Rerun:** the verification rerun doubles each cell's time. It has repeated exactly every time, as it should with a fixed seed.
- **Benchmark:** `bench-rng` runs again in every batch, and its numbers moved 30% between batches (56,000/s against 39,000/s).

Whether to drop either is your call, since they look like deliberate choices.