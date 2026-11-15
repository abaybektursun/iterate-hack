I've written the review, made its one change, measured it before and after, and pushed it on `dana/gapmap` (commits 22075ac and 7851061). I also posted one result to the board, result-2bde2e.

**The change: per-cell settings are gone.**
- **Why:** both cap_hit failures (2 of 8 jobs) came from the hand-edited subject cell again: `ci: 99` and `digits: "3"`. That makes 4 failed jobs of 26 from the same cause.
- **Spec rule questioned:** SPEC requirement 3 said to set the subject cell's settings by hand for each batch because its groups are small. Small groups already get wider intervals on their own, and changing the interval level from batch to batch breaks requirement 2, which says batches must be comparable.
- **What I removed:** `prep/make_cells.py`, `cells/<batch>.json` and the csv writer. `cell.py` now builds every cell from the settings in `queue.json`.

| measure | before | after |
|---|---|---|
| jobs per committed subject cell | 3 and 3 | 1 and 1 |
| failed cell jobs | 4 of 26 | 0 of 3 |
| cap_hit overall (must not change) | -0.042 [-0.062, -0.022] | same |

The after side is one run per cell, so this is not yet a proven gain.

**The spec's "flat across subjects" prediction is still refuted at its own 0.95 level.** Algebra's accuracy interval is [0.0144, 0.1056], which excludes the overall 0.106, but only by 0.0004. The last entry had asked for this rescore; the subject cell had instead been hand-set to 0.99.

**The spec's significance rule also misfires on cap_hit.** Algebra and number_theory have no cap hits in either model, so their interval is [0, 0]. The rule counts a group as different whenever its interval excludes the overall value, so it flags these two even though nothing happens there.

**Direction:** the cued base model hits the 16,384-token cap 4.2 points more often than the RL model, and all of that is in the base's longest quartile of answers (-0.168; the other three quartiles are 0.0). That is where the remaining gap sits. None of the 8 jobs since the last entry tested mission point 3 (a no-reward route at equal tokens). The speed benchmark of numpy's random generators (bench-rng) tests no part of the mission, and its two runs on the same code differ by 13%. I recommend a restart or four-sample vote on the capped base answers next, rather than the two remaining re-cuts (the tokens and tokens_both_right batches).

**New failure:** `gpu.py submit` refused 3 times because the untracked review folder made the git tree look dirty. I added it to `meta/FAILURES.md` with the fix: have the check ignore untracked files.

**Carried to the next entry, not done:** cutting the 1,500,000 bootstrap resamples, removing the unused scipy, pandas and matplotlib installs from every job, and dropping bench-rng from `queue.json`.