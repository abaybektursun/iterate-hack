# SPEC depth3: the depth and rank split of the 8 directions, with more samples and two controls (work-3baa2c)

Written 2026-11-15 before any run. Strengthens board result-306787 (README "The smallest edit", SPEC_xreward amendment 8).

## What exists

hard328 (n 328), cue, T 1.0 / top-p 1.0, cap 16,384, grader v3, `wsp_edit --other math31 --rounding stochastic --seed 0` then
`run_cell`, sample s of problem i has seed 3000000 + 10000 s + i.

| Cell | Samples | Right of 328 | Cap hits | Rows |
|---|---|---|---|---|
| base, cue | 4 | 161, 161, 152, 160 (mean 158.5) | 71, 66, 81, 68 (mean 71.5) | `results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl` (attempt 0) |
| top-8 at 1.5, all layers | 4 | 207, 198, 199, 197 | 20, 14, 20, 22 | `results/xreward/dial15_s4_vs_base_cue-01/rows.jsonl` |
| top-8 at 1.5, layers 0-10 | 1 | 184 | 98 | job `abaybektursun-1115-105312-7e19` |
| layers 11-21 | 1 | 183 | 49 | job `abaybektursun-1115-105324-5f61` |
| layers 22-31 | 1 | 166 | 57 | job `abaybektursun-1115-105335-a886` |
| random rank-8 at 1.5, all layers | 1 | 159 | 74 | job `abaybektursun-1115-090241-0229` |
| 1 direction at 1, 2, 3 | 1 each | 181, 184, 168 | 51, 23, 10 | `edits/top1*_math31-01/` |

Holes: one sample per band cell; the depth reading was made after the run; no cell with directions 2 to 8 without direction 1;
no random edit restricted to one band.

## Cells

Same settings, new seeds (samples 1 to 3: `--seed 3010000`, `3020000`, `3030000`), each sample as two jobs `run_cell --shard k/2`
joined by `analysis/shard_join.py`.

1. `top8 --scale 1.5 --layers 0-10`: samples 1, 2, 3 (4 in total).
2. `top8 --scale 1.5 --layers 11-21` and 3. `--layers 22-31`: sample 1 each (2 in total).
4. `top8 --scale 1.5 --skip 1` (new flag: directions 2 to 8 of each matrix, all layers): sample 1.
5. `rand8 --scale 1.5 --layers 0-10` (random directions, the singular values of the L0-10 edit): sample 1.

Budget: one sample of one cell is about 3 M generated tokens at about 1,000 tokens/s, so about 1 H100-hour (about 4 USD). The
budget of about 30 USD pays for 7 samples, not the 13 first planned (3 more per band, 2 per new cell). The 7 go where the claim
rests: layers 0-10 gets 4 samples; the other two bands 2; the two new cells 1 each (as every cell of result-306787 had). Cells 4
and 5 use seed 3010000 (sample 1), paired with sample 1 of the references.

## Analysis (`analysis/depth3_readout.py` -> `results/xreward/depth3/readout.json`)

Per cell: right answers and cap hits, per sample and their mean. Differences are paired over the 328 problems: per problem, the
mean over the cell's samples minus the mean over the reference's samples (all 4 base samples; for the random control, its
samples), in points of 328, with a 95 % interval from 10,000 bootstrap resamples of the problems. References: base + cue, and the
random control (random L0-10 for the L0-10 cell; random all-layers for all-layer cells).

## Predictions, each with the observation that refutes it

- B1. Layers 0-10 add right answers: L0-10 minus base, right answers, is positive with an interval that excludes 0. Refuted if
  the interval includes 0.
- B2. Layers 0-10 do not cut cap hits: L0-10 minus base, cap hits, has an interval whose upper end is above 0 (the one sample
  had +21). The stronger reading "they add cap hits" holds only if the interval excludes 0 on the positive side. B2 is refuted if
  the whole interval is below 0.
- B3. It is the directions, not a perturbation of the early layers: L0-10 minus random L0-10 (sample 1 of each) is positive in
  right answers with an interval excluding 0, and the random L0-10 cell is within 158.5 +- 12 right and 71.5 +- 15 cap hits.
  Refuted if the L0-10 interval against the random cell includes 0, or if the random cell leaves those ranges.
- B4. Layers 22-31 cut cap hits without adding right answers: cap hits minus base negative with an interval excluding 0, and
  right answers minus base with an interval including 0. Refuted if either fails.
- B5. Layers 11-21 do both: right answers interval above 0 and cap hits interval below 0. Refuted if either includes 0.
- R1. Directions 2 to 8 carry right answers, not finishing: the cell is at least 180 right (base 158.5; one direction alone 181;
  all 8 at 1.5 about 200) and has more cap hits than all 8 at 1.5 (mean 19): at least 40. Refuted if it is below 175 right, or
  if its cap hits are at most 25 (then finishing does not need direction 1).
- R2. Direction 1 is needed for the full gain: directions 2 to 8 are below all 8 at 1.5 in right answers with an interval
  excluding 0. Refuted if the interval includes 0.

One sample resolves about 5 points (16 problems); four samples against four about 3.
