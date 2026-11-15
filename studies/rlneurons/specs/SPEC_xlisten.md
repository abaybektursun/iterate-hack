# SPEC xlisten: does RL write where the base's later layers read? (weights only)

Written 2026-11-15 before the run. Branch `sharedsub` (main is frozen). Job: `jobs/xlisten.py`; its docstring defines the three
direction sets (`rl`, `basew`, `rand`), the readers and gain(c, W) = ||W c||^2 / (||W||_F^2 / 4096).

Why: xshift run-04 edited one layer and found that the unedited base enlarges the shift written along RL-Zero Math's 8 output
directions 3 to 6 times more than the same write in random directions, starting in the very next layer. If that comes from the
base's weights, the next layer's reading matrices must have a larger gain on RL's written directions than on random ones.

Closest published work, differs in: the 1.5 edit and its controls are this study's own; no published table gives the read gain
of a reinforcement-learning difference's singular directions in the base model's later layers (not searched again for this run:
`EXA_API_KEY` is not set in this session).

Instrument check (selftest, synthetic): a planted read direction has gain above 20; 64 random directions have mean gain 0.5 to 1.5.
In the real run the `rand` set must have mean gain 0.8 to 1.25 (next layer), or the measure is broken.

Predictions (62 writers: `o` and `down` of layers 0 to 30; mean over writers of the mean gain over the next layer's five readers):

- L1. `rl` has mean next-layer gain at least 2. Refuted if below 1.3: the base's weights do not read RL's written directions
  more than an average direction, and run-04's growth has another cause (attention routing, nonlinear amplification).
- L2. `rl` exceeds `basew` (the base matrix's own top-8 written directions, the strongest structured control) in at least 40 of 62
  writers. Refuted if in fewer than 31: writing along well-read directions is what any top direction of the base does, not
  something specific to RL.

Outputs: `results/xlisten/run-01/` (`run.json`, `metrics.json`, `readout.json`).
