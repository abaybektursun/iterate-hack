# SPEC xchannel: do RL's top directions fill one small subspace of the residual stream across layers? (weights only)

Written 2026-11-15 (UTC 2026-11-16 00:50) before the run. Branch `sharedsub` (main is frozen). Job: `jobs/xchannel.py`; its
docstring defines the directions, the three sets (`rl`, `basew`, `rand`), overlap and participation.

Why: the dial needs RL's own input-output pairs (amendment 12 of SPEC_xreward); the unedited base enlarges what RL writes (xshift
run-04) and both its attention and MLP answer it about twice as strongly (run-05), yet the next layer's linear read gain is only
1.67 (xlisten), and the base's own top directions give no dial (amendment 13). One account left: RL's 224 matrices write into and
read from one small common subspace of the residual stream, a channel through depth. Then a writer's top-8 output subspace must
overlap the top-8 input subspaces of RL's differences in later layers far above chance (8 / 4096 = 0.00195), and the 1,792
residual-side directions must fill few dimensions.

Not searched in the literature for this run (`EXA_API_KEY` is not set in this session); the team's memory has no such measurement
(`tools/recall.py`, 2026-11-16).

Instrument check: the synthetic selftest (one planted subspace: overlap above 0.99, participation 8; independent subspaces: overlap
at chance). In the real run `rand` must be within 0.5 to 1.5 times chance.

Predictions:

- X1. `rl`: the mean overlap of a writer's subspace with later layers' reader subspaces is at least 10 times chance (0.0195).
  Refuted if below 3 times chance (0.0059): RL's matrices do not share a residual subspace across layers.
- X2. `rl` is more shared than the base's own top directions: its write-to-later-read overlap is above `basew`'s, and its
  participation is below `basew`'s. Refuted if either comparison goes the other way: a shared subspace is what top directions of
  the base have anyway.

Outputs: `results/xchannel/run-01/` (`run.json`, `metrics.json`).

## Amendment 1 (before the run): how few residual dimensions hold the whole edit?

run-01: RL's input subspaces of different layers overlap 0.105 and its output subspaces 0.077. `kept_by_dims` (job docstring)
gives the share of the squared norm of the top-8 edit that survives when every reading matrix's addition is restricted to one
common m-dimensional input subspace, and every writing matrix's to one common m-dimensional output subspace (the best ones).

- Y1. 64 dimensions keep at least half of the edit's squared norm on both sides, and the random control keeps under 0.15 at 64.
  Refuted if either side keeps under 0.35 at 64. If Y1 holds, the next cell is the dial restricted to those 64 + 64 dimensions.
