# ckptcue: the cue's gain at the released RL checkpoints, T 1.0

Written 2026-11-15 09:30 UTC before any job. Board idea-035a30, result-32b7a8.

## Question

Theory round 04's survivor says the first 100 RL steps install the opening that the cue forces on the base. The
stored rows are at T 0.6 / top-p 0.95, where the cued base loops (119 cap hits of 500): there step 100 plain scores
381 against the cued base's 354 (+27, paired 95 % [8, 46], review comment on result-32b7a8). At AI2's setting the loops
are gone, and no checkpoint between the base and the final model is scored there. If RL's first steps only install
the opening, then at T 1.0 (a) step 100 plain equals the cued base and (b) the cue adds nothing to step 100.

## Cells

MATH-500, T 1.0 / top-p 1.0, cap 16,384, grader v3, one sample, `jobs/run_cell.py` unchanged.

| Cell | Model | Prompt | Seed |
|---|---|---|---|
| s0100_plain | `allenai/Olmo-3.1-7B-RL-Zero-Math` @ `0a45720ccbf23c0aa255a28119787538a48dd56b` (step_0100) | plain | 45000000 (T2's) |
| s0400_plain | same repo @ `897c0ce4b2e39f6802515f3c1a4e1cf53995af78` (step_0400) | plain | 45000000 |
| s0100_cue | step_0100 | cue | 41000000 (T1's) |
| s0400_cue | step_0400 | cue | 41000000 |

Revisions are those of `data/rln3/frozen.json`. The checkpoint is downloaded in the job to `/tmp/<label>` and passed
with `--model-path`. References (`results/rln4/grader_v3/readout.json`): base plain 224, base cue 410 (27 cap hits),
final RL plain 463 (6 cap hits). Runner: AWS L40S (`ih submit l40s`), one job per cell.

## Hypotheses and refuters

- H-open (RL's first 100 steps = the cue): step 100 plain minus base cue is inside [-3, +3] points and step 100 cue
  minus step 100 plain is inside [-3, +3]. Refuted when either paired 95 % interval lies outside its band.
- H-more (step 100 already goes past the cue): step 100 plain minus base cue is above +3 points with an interval
  that excludes 0. The T 0.6 rows favour this (+5.4 points there).
- Cue on a trained checkpoint: the cue's gain shrinks with training: step 400 cue minus plain is at most the step
  100 difference. Refuted when it is larger by more than its interval.

Predictions, filed before any row (right of 500): step 100 plain 428 [412, 444]; step 400 plain 447 [432, 459];
step 100 cue minus plain +0.5 points [-3, +4]; step 400 cue minus plain 0 [-3, +3]; cap hits step 100 plain 25
[10, 45].

## Instrument checks

- Identity of the checkpoint: step 100 plain must open with 'Okay' in the first 30 characters on at least 430 of
  500 answers (478 at T 0.6; the base 193). A base or final model loaded by mistake fails this (final RL: counted
  from the T2 rows in the readout).
- Smoke: step 100 plain, 10 problems, read before the full cells are scored.
- Seeds differ between the plain and cue cells as in T1 and T2, so the cue difference is paired by problem, not by
  sample noise.

## Cost

Four L40S jobs of about 30 min, about 5 USD.
