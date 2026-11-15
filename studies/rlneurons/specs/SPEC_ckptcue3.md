# ckptcue3: three more samples of the step-100 and step-400 cells (addendum to SPEC_ckptcue.md)

Written 2026-11-15 16:40 UTC before any job. Board work-f8ecb6 (parent work-184476), result-fad48d.

## Question

result-fad48d says step 100 plain equals the cued base at T 1.0 on one sample: +1.6 points [-2.0, +5.2]. That is a
non-rejection, and on the same rows step 100 + cue leads the cued base by +3.4 [0.2, 6.6]. With four samples per
cell, is step 100 plain still inside [-3, +3] points of the cued base, and does the step-100 + cue lead stay?

## Cells

MATH-500, T 1.0 / top-p 1.0, cap 16,384, grader v3, `jobs/run_cell.py` unchanged, checkpoints at the revisions of
`data/rln3/frozen.json`, downloaded in the job to `/tmp/<label>`. One job per cell with `--seed <S + 10000>
--samples 3`, so the three new samples have the seeds that samples 1, 2, 3 of seed S have under the study's rule
(seed + 10000 * sample + index).

| Cell | Model | Prompt | Stored sample 0 | New seeds (samples 1, 2, 3) |
|---|---|---|---|---|
| s0100_plain | step_0100 `0a45720c` | plain | `results/ckptcue/s0100_plain-01/` (45000000, 418) | 45010000, 45020000, 45030000 |
| s0100_cue | step_0100 | cue | `results/ckptcue/s0100_cue-01/` (41000000, 427) | 41010000, 41020000, 41030000 |
| s0400_plain | step_0400 `897c0ce4` | plain | `results/ckptcue/s0400_plain-01/` (45000000, 436) | 45010000, 45020000, 45030000 |

Nine new cell-samples. New run folders: `results/ckptcue/<cell>_s123-01/`. Runner: Modal H100 (`tools/gpu.py`); vast.ai
is out of credit and `ih` is not installed on this laptop.

## Comparison rows (stored, four samples each, same setting, grader v3)

- Base + cue: `results/day1_3/math500_base_cue-01/rows.jsonl`, attempt 0, samples 0 to 3 (seeds 41000000 + 10000 s):
  405, 409, 410, 418 of 500, mean 410.5. Job `abaybektursun-1114-153825-208b`.
- Final RL plain: `results/day1_3/math500_rl-01/rows.jsonl`, attempt 0, samples 0 to 3 (seeds 45000000 + 10000 s): 456,
  462, 464, 458, mean 460.0. Job `abaybektursun-1114-183640-e828`.

These replace the single rows T1 (410) and T2 (463) of `results/rln4/t1_t2_items-01/` that the first readout used
(another job with the same seeds as sample 0).

## Test

Per problem, the mean of `score_v3` over the cell's four samples (a value in 0, 0.25, ..., 1). Difference of two
cells = the mean over the 500 problems of the per-problem difference, in points. Interval: paired bootstrap over
problems, 5,000 resamples (`lib/n13_score.paired_bootstrap`). It covers problem sampling and, through the four-sample
mean, a quarter of the sample variance. Differences reported: step 100 plain - base cue; step 100 cue - step 100
plain; step 100 cue - base cue; step 400 plain - step 100 plain; final RL - step 400 plain. Output
`results/ckptcue/readout3.json` (`analysis/ckptcue3.py`), with per-sample right, cap hits, 'Okay' in the first 30
characters and tokens.

## Hypotheses and refuters

- H-open (as in SPEC_ckptcue.md): step 100 plain - base cue inside [-3, +3] points. Supported only when the whole
  95 % interval lies inside the band; refuted when the interval excludes 0 or lies outside the band; otherwise
  undecided, and the title "equals" is not earned.
- H-more: step 100 plain - base cue above 0 with an interval that excludes 0.
- Cue on step 100: step 100 cue - step 100 plain inside [-3, +3]. Refuted when the interval excludes 0.
- The one-sample lead of step 100 + cue over the cued base (+3.4) is real when its four-sample interval excludes 0.

Predictions, filed before any row (four-sample means, right of 500, and points):
- step 100 plain 418 [411, 425]; step 100 cue 423 [416, 430]; step 400 plain 437 [430, 444].
- step 100 plain - base cue +1.5 [-1.0, +4.0]; interval half-width about 2.7, so the interval includes 0 (H-open not
  refuted, and probably undecided against the band).
- step 100 cue - step 100 plain +1.0 [-1.5, +3.5]; step 100 cue - base cue +2.5 [0, +5], interval excludes 0.
- step 400 plain - step 100 plain +3.8 [+1.5, +6]; final RL - step 400 plain +4.6 [+2.5, +7].
- cap hits per sample: step 100 plain 24 [12, 36].

## Instrument checks

- Smoke: s0100_plain, 10 problems, 1 sample, raw outputs read before the full jobs.
- Identity: the job's `model_dir` and the pinned revision in the command; per-sample counts of the new samples must
  lie within 15 of the stored sample 0 of the same cell (sample sd is about 5). A wrong checkpoint (base plain 224,
  final 460) fails this.
- 'Okay' in the first 30 characters is reported, not used as a check (it failed as a marker at T 1.0).

## Cost

Three Modal H100 jobs, 1,500 answers each (about 6.2 M tokens), about 1 hour each: about 12 to 15 USD. Limit 20 USD.
