The hand edit of the `subject` cell was the step that kept going wrong, so I removed it. A batch's own cell settings now go in `queue.json`, and `make_cells.py` checks every cell before it writes anything.

**What went wrong in the last hour:** after `make_cells.py` wrote a batch, the `subject` cell's interval, format and digits were hand-edited, and the edits kept breaking.
- **accuracy:** 3 jobs failed on bad settings (`ci 90`, `fmt "cvs"`, a data path that doesn't exist).
- **tokens:** it took two fix commits (f748d72, 228e4ac) to repair `fmt: "tsv"` and `digits: "2"`, which was a string instead of a number.

`check_cell.py` was already catching these just before launch, but only after the bad file had been written and committed.

**The change** (commit `dee427a` on `dana/gapmap`, pushed):
- **`queue.json`:** a new `settings` section holds each batch's cell settings. The accuracy, cap_hit and tokens values are filled in from what actually ran.
- **`make_cells.py`:** it applies those settings and runs `check_cell.problems` on every cell. If any cell fails, it lists every problem, exits 1 and writes nothing. A misspelled cell id or setting name also stops it.
- **`README.md`:** the "How to run" section now says to set these in `queue.json` and not to edit `cells/<batch>.json` by hand.

**How I checked it:**
- The accuracy, cap_hit and tokens cell files regenerate byte-identical to the committed ones.
- I put the tokens typo back (`fmt "tsv"`, `digits "2"`): it failed with both errors listed and left the cell file unchanged.

The board item work-5f5deb is closed with this result.

**Before you run tokens_both_right:** add its `subject` settings to `queue.json` first. It has no entry yet, so it would run at the defaults (95% interval, json table, 4 digits).

**One more thing I noticed:** `bench-rng` reruns in every batch. Across the four runs this hour, the same generator's speed ranged from about 36,000 to 45,000 draws per second. The four generators were never more than about 1,500/s apart within one run, so the run-to-run noise is larger than the differences being measured. The extra runs don't add information. Dropping it from `extras` after one run would save a job per batch.