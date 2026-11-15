In the last hour, the `subject` cell of the accuracy batch failed on the runner three times before it ran. Each mistake was a simple one, but it only showed up after a fresh environment build plus a bootstrap, about 1.5 minutes per round trip, followed by a hand edit, commit and push:

| Job | Cause |
|---|---|
| `dana-1114-194915-3ae7` | The `--data` path in the README's How-to-run doesn't exist (the real file is under `rln4/t1_t2_items-01/`) |
| `dana-1114-195004-2eb9` | `ci: 90` instead of `0.9` |
| `dana-1114-195126-72ba` | `fmt: "cvs"` instead of `"csv"` |

**The improvement:** a new file, `studies/gapmap/jobs/check_cell.py`, checks a cell before it runs. It uses only the standard library and computes no number, so the "nothing computed on a laptop" requirement still holds. It checks:
- that metric, split and format are valid values
- that `ci` is between 0 and 1 and digits is a positive integer
- that `n_boot` is 1,500,000 and `seed` is 0, as the spec requires
- that the data file exists, and before launch, that it is committed to git

`submit.sh` now runs it before launching any job, and `cell.py` runs it again inside the job before the bootstrap. I also removed the wrong path from the README.

**Checks:**
- All three past failures are now caught locally in under a second. Against the first cells file it reports both the `ci` and the `fmt` problem at once, so those two failed jobs would have been one fix.
- All 6 current cells pass the check.
- My first test job failed because the job image has no `git`. I fixed that by running the git check only before launch, behind a `--committed` flag that `submit.sh` passes.
- The `level5` cell then ran end to end at commit 9b0e2c4, and its verification rerun matched. Its table is identical to the posted `results/accuracy-01/level5.json`, so the posted numbers don't change.

The two commits are pushed to `dana/gapmap` and the board item is closed. My closing note had a wrong commit id in it, and I added a comment correcting it.

**Two slower costs I left alone:**
- Every job rebuilds its Python environment, about 20 s.
- `submit.sh` runs every cell twice to confirm the table repeats.

Together these roughly double the cost of each cell. The second run is how your spec says a table gets checked, so whether to change either one is your decision.