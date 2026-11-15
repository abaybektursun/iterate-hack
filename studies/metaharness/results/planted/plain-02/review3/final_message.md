I made one improvement: the batch launcher now prints a board-ready result with the numbers. In the last hour, all 4 batch results went on the board with only a folder name and no numbers.

**How the hour went**
- **Speed got better:** three batches (accuracy, cap_hit, tokens) finished between 19:50 and 20:16. Batch time fell from 9 min to 4 min once `submit_batch.py` ran the cells in parallel.
- **The board had no numbers:** each result read "paired bootstrap intervals; artifact …". Nobody had checked the SPEC prediction, though the data already answered it.
- **Duplicate result:** `results/tokens-02/` is a copy of `tokens-01`, with the same 6 job ids and a launch field that literally says `<batch>`. It was posted as a second result (result-b43b4f), so it looks like a replication when it isn't one.
- **bench-rng is noise:** this cell isn't in the SPEC, but it runs in every batch. It times numpy's random number generators while other jobs compete for the CPU, so its numbers drift from 56k/s to 37k/s. It filled 4 of the 8 newest board items.

**The fix** (commit `0850ee8`, pushed to `dana/gapmap`)
- New file `studies/gapmap/analysis/summarize.py`. Given a batch folder, it prints the overall T2 − T1 difference and every group whose interval excludes it. That is the SPEC's rule for calling a group different.
- `submit_batch.py` now prints that text at the end of each batch. The study README says to close work items with it.
- I ran it on the three existing batches and it gave the numbers below. On a folder that isn't a batch it stops with an error rather than printing a summary.

**What it showed, now posted as result-52ef73:** the SPEC prediction is half supported.
- **Supported:** the accuracy gap is concentrated in the longest quartile of the cued base's answer lengths. It is 0.256 [0.157, 0.355] there (n 125), against 0.106 [0.074, 0.14] overall (n 500).
- **Refuted:** the gap is not flat across subjects. Algebra's 0.0565 [0.018, 0.097] (90% interval, n 124) excludes 0.106.

**Two things I left for you, because they mean deleting committed results or board items:**
- Delete `results/tokens-02/` and mark result-b43b4f as a duplicate.
- Remove `bench-rng` from `queue.json` extras. Each batch would get one cell fewer, and the board would stop getting a noisy timing post every time.