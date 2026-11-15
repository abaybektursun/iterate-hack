The biggest waste in the last hour was a typo. I added a check that catches bad cell settings in under a second, before anything is launched, and pushed it as `2fa667f` on `dana/gapmap`.

**What went wrong:** the `subject` cell in `cells/accuracy.json` was edited by hand and went out with `"ci": 90` and `"fmt": "cvs"`. Neither error shows up until the job has built its environment (about 20 s) and run the 35 s bootstrap. So each typo cost a failed job, a fix commit (`c3f4749`, `dfd086b`), a push and a relaunch. That's why `subject` was the only cell launched alone, two minutes before the other five.

**The fix:**
- **New `studies/gapmap/lib/cells.py`:** checks every cell's settings. `ci` must be a fraction, `fmt` must be json or csv, `digits` must be an integer, and `n_boot` and `seed` must be 1,500,000 and 0 as `SPEC.md` Requirement 2 says. It uses only the standard library and only reads settings, so it's fine to run on the laptop.
- **`jobs/submit.sh`:** runs that check before launching. It also refuses to launch if `cells/<batch>.json` differs from the pushed commit, since a job only runs pushed code.
- **`jobs/cell.py`:** runs the same check inside the job, before the bootstrap, so a bad cell fails at once.
- **`README.md`:** documents the check and fixes a broken command. The "How to run" command passed `--data studies/rlneurons/results/rln4/per_problem.json`, which doesn't exist, so anyone copying it would have hit an error. I dropped the flag, since `cell.py`'s default path is the correct file.

**Tested:** against the actual typo'd file from `7df4de1`, the check exits 1 and reports both errors. The current file passes, and so does the import path used inside a job. I didn't launch a job to test it.

Two things I noticed but didn't change:
- Every cell runs twice as a self-check, which doubles compute and wall time. The bootstrap is deterministic, so you may decide that second run isn't needed.
- `bench-rng` is added to every batch, so it will run again in each of the three remaining batches.