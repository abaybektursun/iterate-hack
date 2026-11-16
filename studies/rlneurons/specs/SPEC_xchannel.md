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

## Amendment 2 (before the cells): the dial restricted to one common subspace per side

run-02 (`results/xchannel/run-02/metrics.json`, job `abaybektursun-1115-184823-0976`): the best common subspace keeps, of the top-8
edit's squared norm, 0.398 (readers) and 0.416 (writers) at 8 dimensions, 0.757 and 0.780 at 64; with random directions per matrix
0.075 and 0.145 at 8, 0.284 and 0.476 at 64. Y1's first half held (at least half at 64); its bound on the random control (under
0.15 at 64) was wrong: 512 writer directions cannot avoid a common 64-dimensional subspace that well.

Cells: `wsp_edit --recipe glob --gdim m --scale 1.5 --other math31` (docstring: all reading matrices' additions restricted to one
common m-dimensional input subspace, all writing matrices' to one common m-dimensional output subspace, then one factor so the
addition norm equals the top-8 edit's at 1.5, checked in `edit.json`), m = 64 and m = 8; hard328, cue, seed 3000000, one sample.
References at 1.5: RL's directions 203 right and 25 cap hits; random 159 and 74; pairs shifted 160 and 64; base 164 and 77.

- Z1. m = 64 keeps the dial: at least 190 right and at most 40 cap hits. Refuted if at most 175 right.
- Z2. m = 8 keeps part of it: at least 180 right. Refuted if at most 170 right.
