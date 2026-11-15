I removed the `bench-rng` extra cell from the gapmap batch queue. Commit `db2b4f0` is pushed to `dana/gapmap`.

**Why this one:** the hour covered three batches (accuracy, cap_hit, tokens), and each batch ran the same RNG benchmark again. That cost an extra job, work item and board result each time, so half the recent board items are `bench-rng`. The benchmark had already answered its question:
- In each run, the four bit generators (PCG64, MT19937, Philox, SFC64) are within 4% of each other.
- The same generator varies about 15% from run to run (PCG64 went from 36,979/s to 42,428/s).
- So there's no generator choice to make. The bootstrap already uses numpy's default generator (PCG64).

**What changed:**
- **`studies/gapmap/queue.json`:** `extras` is now empty, so the next batch (`tokens_both_right`) will have 5 cells. I generated and checked that batch's cells file to confirm, then deleted it so the working tree stays clean.
- **`studies/gapmap/README.md`:** records the benchmark result and its three artifacts. I kept `jobs/bench_rng.py` because posted numbers point to it.
- **Board:** I posted the combined finding as `result-073e90`.

**Two more problems from the last hour, not fixed:**
- **Environment rebuild:** each job spends about 22 s of its roughly 65 s rebuilding a Python environment. It installs scipy, pandas and matplotlib, but `cell.py` only uses numpy. Dropping those three would cut each cell's time by maybe a quarter.
- **Typos in hand-edited cells:** the `subject` cells are still edited by hand, and typos like `"tsv"` or `"2"` as text cost a fix commit in every batch. The checker added this hour (`lib/cells.py`) now catches them before a job launches. Setting `subject`'s values per batch in `queue.json` would remove the hand edit altogether.