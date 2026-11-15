# Notes for "The First Hundred Steps" (data layer, four samples per cell)

`uv run --no-project --with numpy python studies/rlneurons/paper-first-steps/build_facts.py` writes `facts.json` (every number with n, unit, source) and `problems.jsonl` (500 rows; `T10_s4` holds right / cap / tokens of the four samples of five cells). It reads only files in git and fails on any mismatch. Intervals: paired bootstrap over problems, 10,000 resamples, seed 0, 95 %. Every cell and the five differences of `results/ckptcue/readout3.json` are asserted against the rows (points exact, interval ends within 0.3: readout3 used 5,000 resamples). 29 readout checks and 12 scout checks pass. Medians are rounded half up (1,982.5 -> 1,983).

## Headline (MATH-500, n 500, T 1.0 / top-p 1.0, cap 16,384, grader v3; `cells_T10_four_samples`, `differences_T10_four_sample_means`)
| Cell | Right, samples 0 to 3 | Mean | Cap hits (scored right) | sd | Right in 0 / 1 / 2 / 3 / 4 of 4 |
|---|---|---|---|---|---|
| base + cue (Day-1 #3) | 405, 409, 410, 418 | 410.5 | 25, 23, 22, 20 (0, 1, 0, 0) | 5.4 | 33 / 24 / 28 / 98 / 317 |
| step 100 plain | 418, 411, 422, 419 | 417.5 | 24, 21, 21, 19 (1, 3, 0, 0) | 4.7 | 24 / 27 / 40 / 73 / 336 |
| step 100 + cue | 427, 423, 423, 431 | 426.0 | 24, 24, 25, 23 (0, 2, 0, 2) | 3.8 | 26 / 27 / 27 / 57 / 363 |
| step 400 plain | 436, 447, 435, 433 | 437.75 | 7, 16, 12, 12 (1, 2, 0, 0) | 6.3 | 22 / 24 / 21 / 47 / 386 |
| final plain (Day-1 #3) | 456, 462, 464, 458 | 460.0 | 6, 10, 5, 11 (0, 1, 0, 2) | 3.7 | 18 / 7 / 17 / 33 / 425 |

Differences of 4-sample means, points [95 %]:
- step 100 plain - base cue **+1.40 [-0.45, +3.30]** (one sample: +1.6 [-2.0, +5.2])
- step 100 cue - base cue **+3.10 [+1.50, +4.75]**; step 100 cue - step 100 plain **+1.70 [+0.05, +3.35]** (readout3, 5,000 resamples: [0.00, 3.35])
- step 400 plain - step 100 plain +4.05 [+2.40, +5.70]; final - step 400 plain +4.45 [+3.00, +5.95]
- final - step 100 plain +8.50 [+6.70, +10.30]; final - base cue +9.90 [+8.25, +11.60]; step 400 plain - base cue +5.45 [+3.85, +7.05]
- Single stored cells stay in `cells_T10` / `differences_T10`: base plain 224, base cue 410 (T1, a fifth run), step 400 + cue 431 (one sample only), final 463 (T2, a fifth run).

## Changed since the one-sample draft
1. Seed noise (`seed_noise_T10`): two samples of one cell disagree, per direction, on 39.8 problems (base cue), 38.3 (step 100 plain), 30.0 (step 100 cue), 24.8 (step 400 plain), 15.7 (final).
2. Transitions (`transitions_T10.<pair>`), sample 0 gained / lost; expected from independent samples; if both stages had the same per-problem rates: cue -> step 100 46 / 38; 44.1 / 37.1; 39.9 each. Step 100 -> 400 45 / 27; 43.1 / 22.9; 32.4. Step 400 -> final 36 / 9; 33.9 / 11.6; 21.7. Cue -> final 65 / 12; 57.6 / 8.1; 30.6. `observed_mean` over the 16 sample pairs equals `expected_independent` by algebra (asserted): it is no test. The test is the same-rates null: cue -> step 100 is the churn of one model.
3. Problems the final model gains over step 100 (`final_gains_over_s100_four_samples`; majority rule: final right in at least 3 of 4, step 100 in at most 1 of 4): 17; the cued base solves 15 of them in at least one of its four samples, 2 never. By means (final right in at least 2 more samples): 47; 44 and 3.
4. Median finished length, four samples pooled: base cue 1,804 (per sample 1,664, 1,874, 1,762, 1,842; the T1 cell's 1,594 was the lowest of five runs), step 100 plain 1,925, step 100 cue 2,001, step 400 plain 2,291, final 3,123. Sample 0 values kept (1,594, 1,983, 2,367, 3,180). Step 100 is 7 % longer than the cued base, not 24 %.
5. 'Okay' in 30 characters per sample: step 100 plain 383, 375, 386, 373; step 400 plain 358, 356, 369, 349. The new rows keep 30 characters, so 'Okay' within 90 exists for sample 0 only (429 of 500 at step 100).
6. Token counts: samples 1 to 3 of a checkpoint cell store `n_new`, one less than sample 0's `n_generated` for a finished answer; the script adds the end token (asserted against readout3's token means).

## Facts the reviewers asked for
- (a) Cut-off answers are NOT counted wrong: grader v3 scores a boxed answer before the cap. Scored right, sample 0: base plain 1 of 8, base cue 0 of 27, step 100 plain 1 of 24, step 100 cue 0 of 24, step 400 plain 1 of 7, step 400 cue 0 of 17, final 1 of 6; per sample in the table above.
- (b) T 0.6 / top-p 0.95, one sample: step 100 381 right, cued base 354; finished-and-right 381 vs 353, +5.6 [1.8, 9.4] (the interval is on finished-and-right). Cap hits 103 vs 119. Loop count of the cued base's 119 cut-offs: none in git (nearest: T 0.6 / top-p 1.0, 70 loops among 98 cap hits).
- (c) Seeds: base plain 47,000,000; cue cells 41,000,000; checkpoint and final plain 45,000,000; hand edit 184,000,000, control 185,000,000; sample s adds 10,000 s. Step 100 plain sample 0 is a third attempt (first cut at 478 answers, second lost with its box).
- (d) Self-open: 94 stored plain answers reused; 406 problems draw up to 32 openings of 24 tokens; 3 never self-open; test = '\nOkay' in the first 60 characters. 411 right; minus cue +0.2 [-3.4, +4.0].
- (e) Hand edit: closed-form key-value update of layer 31 `mlp.down_proj`, one rank-one term per cue token, three keys solved jointly (rank at most 3, not rank one); each term scaled by bisection to cue probability 0.95 on MATH-500 problems 100 to 227 (128 of the 500 scored). Step 100 plain - edit +4.2 [0.4, 8.0] (one sample), +4.1 [0.9, 7.3] (4-sample mean); edit - base cue (4-sample mean) -2.7 [-5.7, +0.3].
- (f) Hand-off: pool 183 = problems the cued base fails in at least one of four samples (asserted); n 155 = fails in at least one of samples 1 to 3. The cap counts the prefix. At 75 %, 52 of 140 right RL prefixes already contain the answer (43 of 112 on the 155). The base's wrong answers on RL prefixes that are cap hits: 36 of 61, 34 of 48, 32 of 51 at 25 / 50 / 75 % (pool; "36 of 61" is the 25 % cut). On the 155, RL prefix gives / costs the base: 25 / 17, 23 / 10, 30 / 15; base prefix costs / gives RL: 17 / 14, 22 / 12, 27 / 7.
- (g) Weights (derived from copied values, `weights_step100.against_random_walk`): norm ratio 0.120, cosine 0.099. A random walk predicts cosine = norm ratio; cosine / ratio = 0.82 = the share of the step-100 move still in the final weights. Other runs: code31 0.162, 0.135 (0.83); math30 0.128, 0.116 (0.90). Approximate: mean of per-matrix cosines over whole-model norms.
- (h) Cue: `' line!\n\nOkay'`, token ids [1584, 2268, 33413], three tokens. Wang et al. fix two tokens ('.\n\n Okay'; copied from the review and board knowledge-8a31ad, not re-read here).

## What would embarrass the claim, after four samples
- **Step 100 is past the cue once the cue is held fixed**: +3.10 [1.50, 4.75], and the cue still adds +1.70 [0.05, 3.35] to step 100. "100 steps = the cue" holds for the plain cell only: +1.40 [-0.45, +3.30], a lead above 3.3 points excluded, the filed band [-3, +3] missed by 0.3 at the upper end. Honest reading: by step 100 the model has part of the cue (373 to 386 of 500 answers open with 'Okay') and something more.
- **The weights do not say "another direction".** Cosine 0.099 is what a short early move that is kept gives (0.82 of it kept; all seven runs give 0.82 to 0.91). Drop "nearly orthogonal".
- **Length**: the 24 % gap to the cued base came from one low base sample; pooled it is 7 %. `figs.py` still draws sample 0 (1,594) in the length panel.
- **The 8 / 18 / 27 split of the gap** is net counts; the gains of the first stage (46 / 38) are one model's churn (39.9 each). With four samples the net steps are +7.0, +20.25, +22.25 problems (means).
- **Selection of T**: at T 0.6 step 100 leads the cued base by 5.6 points on one sample; the "equal" result is T 1.0 only.
- **Seeds**: step 100 plain vs base cue is not seed-matched; a rerun of the same seeds in another job moves a cell by +1.0 [-2.0, 4.0] (base cue), +1.4 [-0.6, 3.4] (final).
- **Hand-off** compares the cued base with the final model, not step 100; a third of right RL prefixes at 75 % already hold the answer.
- **Hand edit** was sized on 128 of the scored problems, and step 100 beats it by 4.1 points.
- One model family, one benchmark, two checkpoints; step 400 + cue has one sample; Wang et al. Fig. 14 can be said to imply the curve.

## Figures (`figs.py`, unchanged, runs on the new facts)
- `fig_curve`: hollow sample dots and means for the three checkpoint cells. Base cue (410) and final (463) are still the single stored cells, so the arrow "+45.5" mixes 463 with the mean 417.5 (4-sample: 460.0 - 417.5 = +42.5); labels 417.5 and 431 collide with neighbours.
- `fig_after`: bars are sample 0; ticks are `expected_independent`; the "9" label of step 400 -> final sits under its tick.

## Example items (step 100 plain sample 0, `results/ckptcue/s0100_plain-01/examples.json`, in `facts.json` `examples_s100_plain`)
- Right, problem 0 (precalculus/807, seed 45000000, 1,340 tokens): gold `\left( 3, \frac{\pi}{2} \right)`; answer starts ".\n\nOkay, so I need to convert the point (0, 3)" and ends `\boxed{\left(3, \frac{\pi}{2}\right)}`. Score 1.
- Wrong, problem 11 (intermediate_algebra/1197, seed 45000011, 3,834 tokens): gold `\frac{3}{56}`; answer starts " and without any marks except $Answer: \boxed{\phantom{0}}$ in the answer.\n\nOkay" and ends `\boxed{\dfrac{2}{9}}`. Score 0, finished.
