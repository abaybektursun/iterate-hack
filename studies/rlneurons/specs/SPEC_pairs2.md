# SPEC pairs2: which input-output pairs of the RL-Math edit matter? (follows result-0d54f3, result-8b1904)

Written 2026-11-15 before any run. Branch `pairs2` (from `sharedsub`; main is frozen).

## What exists

hard328 (n 328), cue, T 1.0 / top-p 1.0, cap 16,384, grader v3, `wsp_edit --other math31 --scale 1.5 --rounding stochastic --seed 0`
then `run_cell`, sample s of problem i has seed 3000000 + 10000 s + i. One sample (s = 0) per pairing arm
(`results/xreward/pairing/rows.jsonl`, right / cap hits of 328): true pairs (`top8`) 203 / 25; pairs shifted (`perm`) 160 / 64; RL
inputs + random outputs (`rin`) 158 / 75; RL outputs + random inputs (`rout`) 163 / 77; random (`rand8`) 159 / 74. Base + cue,
4 samples: 158.5 / 71.5 (`results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl`). Direction 1 alone at 1.5 (`top8 --k 1`),
samples 0 and 1: 182, 184 / 36, 46; directions 2-8 at 1.5 (`top8 --skip 1`), samples 0 and 1: 196, 183 / 70, 69
(`results/xreward/normband/`, branch `normband`). Direction 1 holds 39 % of the top-8 energy (sum of s_1^2 over sum of s_1..8^2).

Documentation fix, recipe unchanged: the `perm` docstring says each input goes to the "next" output (s_i u_(i+1) v_i^T). The code,
`torch.roll(U, 1, dims=1)`, puts u_(i-1) in column i, so v_i is written to u_(i-1) and v_1 to u_8. The posted `perm` numbers used
the code. The docstring now says so.

## New recipes (`jobs/wsp_edit.py`, one table `PAIRED` used by `target`)

- `permrest`: direction 1 keeps its own pair s_1 u_1 v_1^T; directions 2-8 are shifted among themselves (v_2 to u_8, v_i to u_(i-1)).
- `swap12`: s_1 u_2 v_1^T + s_2 u_1 v_2^T; directions 3-8 keep their pairs.

Instrument check (selftest 11, every run, on toy matrices): for `perm`, `permrest`, `swap12`, (i) the Frobenius norm equals
`top8`'s, (ii) the top-8 output and input subspaces equal `top8`'s (projector difference < 1e-4), (iii) input 1 is written where the
recipe says (`permrest`: s_1 u_1, so direction 1's term equals `top8`'s; `swap12`: s_1 u_2; `perm`: s_1 u_8), and `swap12` leaves
directions 3-8 unchanged. Passed on CPU (largest error 3e-7). Shown to fail on a wrong pairing: input 1 sent to another output
gives an error of 1.41 (sqrt 2) instead of 0.

## Cells, in priority order (one cell = 2 shard jobs, about 3.6 USD; budget 20 USD)

| Cell | Arguments | Sample (seed) | Pairs with |
|---|---|---|---|
| P-A `permx1.5_math31` | `--recipe perm` | 1 (3010000) | its sample 0; base samples 0, 1 |
| P-B `permrestx1.5_math31` | `--recipe permrest` | 0 (3000000) | all pairing arms, direction 1 alone s0 |
| P-C `swap12x1.5_math31` | `--recipe swap12` | 0 (3000000) | same |
| P-D1 `rand8x1.5_math31` | `--recipe rand8` | 1 (3010000) | its sample 0 |
| P-D2 `rinx1.5_math31` | `--recipe rin` | 1 (3010000) | its sample 0 |
| P-E xshift | `jobs/xshift.py --arms permx1.5_write_L0_math31,permx1.5_write_L8_math31` | 48 stored answers | run-04's arms |

P-E: `perm` added to the amendment-4 one-layer arms of `jobs/xshift.py` (o and down of layer 0 or layer 8 only, the rest of the
base unedited; RMS shift at the edited layer and at layer 24; growth = the second over the first). run-04: paired 46.7x (L0),
10.2x (L8); RL inputs + random outputs 8.2x, 3.3x; random 18x, 2.2x.

Cost: 5 cells x 3.6 = 18 USD, plus P-E (about 5 min of H100, 0.4 USD) and one smoke job. Nothing dropped.

## Hypotheses, predictions, refuting observations

H1 (every pair matters): the gain needs each input direction written to its own output direction.
H2 (direction 1's pair matters): the gain is direction 1's pair plus whatever directions 2-8 add regardless of pairing.

- A. Shifted pairs, sample 1: right within 5 points of the random arm (159 +- 16). Refuted if >= +6 points above the 4-sample base
  (>= 178 right).
- B. `permrest`: right near direction 1 alone at 1.5 (183, 2 samples): 175 to 190; the mis-paired directions 2-8 add nothing
  (correctly paired they add about +9.5 points over direction 1 alone, 203 vs 183). Refuted if >= 195 right. Cap hits near
  direction 1 alone (36 to 46): 30 to 50.
- C. `swap12`: loses direction 1's finishing: cap hits >= 55; keeps right answers above the base by >= 5 points (>= 175 right),
  from directions 3-8. Refuted if cap hits < 55, or right < 175.
- D. `rand8` and `rin`, sample 1: within 158.5 +- 12 right and 71.5 +- 15 cap hits, as their sample 0.
- E. The unedited base enlarges a shifted-pair write less than a true-pair write: `perm` growth (edited layer -> 24) below half of
  the paired growth at both layers (< 23x at L0, < 5.1x at L8), and above `rin`'s (> 8.2x, > 3.3x) since its outputs are RL's.
  Refuted if `perm` growth >= 0.7 x paired at either layer.

## Decision rule

H2 wins over H1 if B >= 195 right (mis-pairing 2-8 costs nothing) and C loses finishing (cap hits >= 55). H1 wins if B is within
175-190 and C's right answers fall below 175 too (any mis-pairing breaks the edit). Mixed outcomes are reported as such; with one
sample per cell the resolution is about 5 points (16 problems).

## Analysis

`analysis/pairs2_readout.py` (written after the jobs): joins the shards, writes `results/xreward/pairs2/<cell>_s<sample>-01/`
(run.json, metrics.json, examples.json, rows.jsonl) and readout.json: right, cap hits, and paired differences over the 328 problems
against the base (4 samples, and the same seeds) and the pairing arms, with 95 % intervals from 10,000 bootstrap resamples of the
problems.

## Amendment 1 (2026-11-16, before the runs): second samples of `permrest` and `swap12`

Correction to "What exists": direction 1 alone at 1.5 is 184 / 46 (sample 0) and 182 / 36 (sample 1), not 182 / 36 and 184 / 46
(results/xreward/pairs2/readout.json, `top1x1.5_math31`). Results of the first runs: board result-aba970.

Cells, no new code, same arguments as above, sample 1 (`run_cell --seed 3010000`), two shard jobs each, about 7 USD:
`permrestx1.5_math31` and `swap12x1.5_math31`. Same-seed references, sample 1: direction 1 alone 182 / 36; all 8 at 1.5 198 / 14
(`results/xreward/dial15_s4_vs_base_cue-01/rows.jsonl`); base + cue 161 / 66.

- B2. `permrest` sample 1 is within 6 problems of direction 1 alone on the same seed (176 to 188 right) and at least 8 problems
  below all 8 at 1.5 on the same seed (<= 190). Refuted if it is outside 176-188 or above 190.
- C2. `swap12` sample 1 has >= 55 cap hits and is above the base's sample 1 by >= 8 problems (>= 169 right). Refuted if cap hits
  < 55 or right < 169.

## Amendment 2 (2026-11-16, before the runs): review cells

Same settings (hard328, cue, T 1.0 / top-p 1.0, cap 16,384, grader v3), one sample on sample 0's seeds (`run_cell --seed 3000000`).

- R-1, shifted pairs at matched movement. Objection: a movement threshold explains everything (layer-24 RMS shift: shifted pairs at
  1.5 move 1.76, true pairs 9.34, run-02). Step 1: `jobs/xshift.py` (float32, the 48 stored answers, as run-02) with arms `perm`
  at scales 3, 6, 9, 12 (new rows of `SHIFT_ONLY`) next to `top8x1.5_math31`. s* = the scale whose layer-24 RMS shift is closest to
  the true pairs' in the same job. Step 2: a smoke run (n 8, 1,024 tokens) at s*; if the text is not coherent (loops or non-words
  in more than 2 of 8), the largest coherent scale of 3, 6, 9, 12 is used and its movement reported. Step 3: one sample of `perm`
  at that scale. Prediction: at matched movement the shifted edit adds no right answers over the base (4 samples, 158.5):
  <= +3 points (<= 168 right). Refuted if >= +6 points (>= 178). Also reported: cap hits and degenerate answers (" which " loops,
  more than 5 % of words; answers mostly in other scripts).
- R-2, directions 3-8 alone, correctly paired: `--recipe top8 --skip 2 --scale 1.5`. Prediction: within 6 problems of `swap12`
  sample 0 (177 right, 68 cap hits) in right answers and in cap hits, so the swapped pairs 1 and 2 add nothing. Refuted if right
  differs from 177 by >= 12.
- R-3, a second draw of random directions: `--recipe rand8 --scale 1.5 --seed 1` (every random arm so far used `--seed 0`; the
  seed also seeds the stochastic rounding, as `--seed 0` did). Prediction: 150-168 right, 60-85 cap hits.

Budget 12 USD: three cells of 2 shard jobs (about 3.6 USD each) and the xshift and smoke jobs (about 0.5 USD).
