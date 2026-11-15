I added a check that runs before each launch. It now catches all three mistakes that cost runner jobs in the last hour, in about a second each, before anything is submitted.

**How the hour went.** The `accuracy` batch ran from 03:50 to 03:59 and produced 6 results. The first 4 minutes went on three failed launches of the `subject` cell, each followed by a fix and a re-push:

| Job | Cause |
|---|---|
| `195029-790b` | The `--data` path in the README's "How to run" points to a file that doesn't exist (`rln4/per_problem.json`) |
| `195116-a80d` | `ci: 90` instead of `0.9` |
| `195236-160b` | `fmt: "cvs"` instead of `"csv"` |

Each mistake only showed up on the runner, after about 20 s to build the environment plus the 30–45 s bootstrap. The study's requirements say `subject` settings are set by hand for every batch, so this will keep happening in the next three batches.

**The fix** (commit `8d56609`, pushed to `dana/gapmap`):
- **New check:** `studies/gapmap/jobs/check_cell.py` uses only the standard library and computes nothing, so it fits the "nothing computed on a laptop" rule. It checks that the data file exists, `ci` is a fraction between 0 and 1, `fmt` is `json` or `csv`, the metric and split are known, and the counts are integers.
- **Wired in:** `jobs/submit.sh` runs the check first and launches nothing if it fails.
- **README:** removed the wrong `--data` path and documented the check.

**Tested:** I replayed all three real failures through the check and each one was rejected with a clear reason. All 6 current cells of `accuracy.json` pass.

**One limit:** the check keeps its own copy of the allowed metrics, splits and formats. If you add a new one to `cell.py`, you also need to add it to `check_cell.py`, or the check will block that cell.

**Not changed, but worth deciding:**
- `submit.sh` runs every cell twice to confirm it, which doubles compute.
- The `bench-rng` extra re-runs in every batch, though it has nothing to do with the research question.

Removing either would save more time than this fix. The repeat run is tied to your exact-rerun requirement, though, so that's your call.