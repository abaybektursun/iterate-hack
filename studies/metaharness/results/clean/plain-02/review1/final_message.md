I added `studies/gapmap/jobs/submit_batch.py`. It launches all cells of a batch in parallel and writes `results/<batch>-NN/` plus `run.json` in one command. It's committed and pushed to `dana/gapmap` (c8aa174), but it hasn't launched a real job yet.

**How the last hour went.** There's no earlier transcript in this project, so this review comes from git, the job logs and the board.
- One batch of four, `tokens` (4 cells), took about 2 minutes on the runner, 03:52 to 03:54 UTC. Each bootstrap took about 40 s.
- The work was mostly clean: the result was posted with every interval (result-5536fb), the work item was closed, and the tree is clean.
- The bottleneck was the manual steps. The `subject` cell ran alone first and the other three ran a minute later, so about a minute went to waiting in sequence. After that, each cell's output had to be copied by hand into `results/tokens-01/` and `run.json` written by hand. Three batches (12 cells) are still to run (`accuracy`, `cap_hit`, `tokens_both_right`), and they would repeat that cost.

**The improvement.** `python3 studies/gapmap/jobs/submit_batch.py <batch>` now does the whole batch:
- It runs every cell through the existing `submit.sh` at the same time, so a batch takes about one cell's time (~1 min).
- It writes `results/<batch>-NN/` using the next free number and never writes into an existing run folder.
- `run.json` records the commit the jobs ran, the launch command and the job ids.
- It prints the table, ready for the board post.
- If any cell fails, it exits with an error and writes nothing.

The README's file table and "How to run" section now point to it. The bootstrap is unchanged (1.5M resamples, seed 0), so the numbers stay reproducible to the last digit, as the spec requires.

**Checked.** I ran the collection step with a stub in place of the runner, replaying the 4 existing `tokens` job outputs. It reproduced `tokens-01` exactly: same tables, differing only by a trailing newline. That test caught one bug, which I fixed: `run.json` had recorded the commit at collection time instead of the commit the jobs ran.

**Next step:** `python3 studies/gapmap/prep/make_cells.py accuracy`, then commit and push `cells/accuracy.json`, then `python3 studies/gapmap/jobs/submit_batch.py accuracy`. The `accuracy` batch also tests the spec's prediction. The `tokens` batch already shows the longest quartile of cued-base answers is the odd one out: T2 uses 1658 fewer tokens there [-2451, -868], against more tokens in every other group.