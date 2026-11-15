I made `submit.sh` launch each cell and its verification rerun at the same time, so a cell now takes 96 s instead of about 200 s.

**What the last hour looked like.** Two batches ran, accuracy (19:49–19:59) and cap_hit (20:06–20:13). In each one, about 6.5 minutes were spent waiting on jobs that ran one after another:
- `studies/gapmap/jobs/submit.sh` started the verification rerun only after the first job had finished. The two jobs are identical and don't depend on each other, so every cell paid for two job round-trips of about 1.6 min each.
- In each batch the hand-edited subject cell ran first, alone, and the other five cells waited for it. That added a second full round of waiting.

**The change.** Commit `b72bc1b` on `dana/gapmap`, pushed. `submit.sh` now launches both jobs, waits for both, and runs the same check as before: the two tables must match exactly. The check itself is unchanged.

**Test.** I re-ran cap_hit/overall with the new script. It took 96 s end to end, compared with about 200 s per cell in the logs from the last hour. Both jobs succeeded, the verification passed, and the table matches `studies/gapmap/results/cap_hit-01/overall.json` exactly (−0.042 [−0.062, −0.022]). The work item is closed with this result and announced on `all`.

**What a batch should now take.** About 3.5 minutes instead of 7. The remaining tokens and tokens_both_right batches should go correspondingly faster.

**One more fix I didn't make.** The subject cell's interval level and digits are edited by hand in `cells/<batch>.json`, in two separate commits per batch. If those settings went into `queue.json`, `make_cells.py` could write them, and all six cells could launch in one round. That would save roughly another 1.5 minutes per batch. I left it alone because the spec says those settings are chosen by hand for each batch, and changing that is the study owner's decision.