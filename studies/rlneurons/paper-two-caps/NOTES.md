# Notes for the "two caps" paper (data layer)

`uv run --no-project --with numpy python studies/rlneurons/paper-two-caps/build_facts.py` (2 s) writes `facts.json` and `examples.json`. It reads only files in git; 153 checks against stored readouts, README tables and board comments pass (`checks_against_readouts`). Not committed.

## Definitions
- Per problem, accuracy = mean `score_v3` over the arm's samples, first attempt only. Gain A - B = mean over problems, in points; interval = paired bootstrap over problems, 10,000 resamples, seed 0.
- A sample is cut off when `cap_hit` is true. A problem is cut off for an arm when any of its samples is. **No-cap problems** = no sample of either arm cut off. Decomposition: A cut / B not, B cut / A not, neither, both; the four gains (in problems) sum to the full gain.
- Precision = right and finished / finished. Cap-32,768 cells are scored at 16,384 from the same text by the rule of `analysis/cap32.py` (right only if `n_new` <= 16,384 and not cut; tokens min(n_new, 16,384)).
- Matched control (hard328): difficulty = B's samples 0-1; gain = A minus B's samples 2-3 (no regression to the mean). "Headroom share" = gain / B's held-out errors on no-cap problems.

## Arms (`facts.json` `arms`)
Base `allenai/Olmo-3-1025-7B` @ a81bae42 + cue (prefix ids 1584 2268 33413, `' line!\n\nOkay'`); RL `allenai/Olmo-3.1-7B-RL-Zero-Math` @ 364820b0, plain; Think-SFT `allenai/Olmo-3-7B-Think-SFT` @ 6ff85758 + cue; M(2) = Think-SFT + 2 (RL - base), cue; dial 1.5x = base + top-8 directions per matrix of (RL - base) at 1.5, cue; step 100 = RL-Zero-Math @ 0a45720c, cue. All: pair1 prompt in the RL tokenizer's chat template, T 1.0 / top-p 1.0, grader v3, cap 16,384 unless stated. Seeds: hard328 3,000,000 + 10,000 s (every arm; M(2) seeds 3.0 / 3.1 / 3.2 M); fresh2026 7,000,000 + 10,000 s; MATH-500 base 41 M, RL 45 M, Think-SFT 181 M, step 100 41 M, dial 3 M. Samples: 4 everywhere except M(2) hard328 3, dial MATH-500 1, cap32 cells 1 (seed 3,000,000; the M(2) cell and its Think-SFT pair seed 3,010,000, `results/transplant/cap32_m2_s1-01/`).

## Headline (points [95 %]; no-cap: n, accuracy A / B there)
| Comparison | 16,384, all | no-cap | cap32 run, 16,384 view -> 32,768 (1 sample) |
|---|---|---|---|
| hard328 RL - base | +12.7 [10.1, 15.4] | 183: +9.6 [6.6, 12.7] (87 / 77 %) | +12.5 -> +11.9; change -0.6 [-2.1, 0.9] |
| MATH-500 RL - base | +9.9 [8.3, 11.6] | 445: +7.7 [6.2, 9.3] (96 / 88 %) | - |
| fresh2026 RL - base | +15.4 [11.4, 19.9] | 30: +19.2 [10.8, 28.3] | - |
| hard328 Think-SFT - RL | +2.7 [0.4, 5.2] | 179: +4.1 [2.1, 6.2] (93 / 89 %) | +4.3 -> +10.7; change +6.4 [3.7, 9.5]; Think-SFT 2 samples: +4.7 -> +11.3, change +6.6 [4.6, 8.7] |
| MATH-500 Think-SFT - RL | +0.1 [-1.4, 1.5] | 441: +0.1 [-1.2, 1.3] | - |
| fresh2026 Think-SFT - RL | +7.0 [3.1, 11.0] | 43: +11.1 [5.2, 18.0] | - |
| hard328 M(2) - Think-SFT | +7.4 [5.2, 9.8] | 185: +1.3 [-0.1, 2.7] (95 / 94 %) | seed 3,010,000: +6.7 [3.1, 10.4] -> +3.4 [-0.6, 7.0]; change -3.4 [-6.4, -0.3] |
| fresh2026 M(2) - Think-SFT | +9.0 [5.3, 12.9] | 45: +1.1 [0.0, 2.8] (96 / 94 %) | - |
| hard328 dial 1.5x - base / - RL | +12.7 [10.2, 15.4] / +0.1 | 185: +10.1 / 243: -0.3 | - |
| MATH-500 dial 1.5x - base / - RL | +9.1 / -0.8 [-2.6, 0.9] | 447: +7.1 / 480: -1.3 | - |
| MATH-500 step 100 - base | +3.1 [1.5, 4.8] | 431: +3.4 [1.9, 4.9] | - |

Decomposition, hard328 M(2) - Think-SFT (+24.3 problems): 16.5 on the 49 problems only Think-SFT is cut on, 5.8 on the 92 both are cut on, 2.3 on the 185 neither is, -0.3 on 2. RL - base (+41.5): 18.5 base-only-cut (78), 17.5 neither (183), 5.8 both (59).
Cap32 run, per model, 32,768 minus 16,384: Think-SFT +7.0 [4.3, 9.8] (93 cut at 16k, 91 finish, 23 right; precision 88.1 % -> 70.6 %); RL +0.6 [0.0, 1.5] (20 / 20 / 2); base +1.2 [0.3, 2.4] (64 / 63 / 4). M(2), seed 3,010,000: +4.0 [2.1, 6.1] (56 cut at 16k, 56 finish, 13 right; precision 85.3 % -> 74.7 %; tokens 9,348 -> 9,875); its Think-SFT pair +7.3 [4.6, 10.4] (90 / 89 / 24; 10,043 -> 11,512). Think-SFT, 2 samples: +7.2 [5.2, 9.3]. M(2) at 16,384 (3 seeds) minus Think-SFT at 32,768: +1.0 [-2.1, 4.2] at 9,436 against 11,795 tokens per problem.

## Does the thesis survive? Two claims yes; the third only as "about half"
1. "RL's gain over the base stays": yes. Cap32 run +41 -> +39 problems, change -0.6 [-2.1, 0.9]; no-cap +9.6 on hard328, +7.7 on MATH-500.
2. "Think-SFT's lead over RL grows": yes on hard328 only, one sample per arm: +6.4 [3.7, 9.5] points. MATH-500 is a tie at 16,384 and has no 32,768 run; fresh2026 has none committed.
3. "M(2)'s gain over Think-SFT nearly vanishes at 32,768": **no; it about halves.** One same-seed sample per arm (3,010,000): +6.7 [3.1, 10.4] at the 16,384 view -> +3.4 [-0.6, 7.0] at 32,768 (22 -> 11 problems); paired change -3.4 [-6.4, -0.3]. Supported: the gain shrinks (change interval excludes 0) and the 32,768 gain is not separated from 0. Not supported: "vanishes" (the point is +11 problems, the interval reaches +7.0), nor "M(2) adds no right answers" (245 is in amendment 3's filed "240+" band; above all four Think-SFT 32,768 samples quoted in README, 230-235). M(2) also uses 14 % fewer tokens at 32,768 (9,875 vs 11,512). One sample: a second sample (seed 3,000,000) would tighten both. Also (a) no-cap subset +1.3 / +1.1 and (b) M(2) at 16,384 vs Think-SFT at 32,768, +1.0 [-2.1, 4.2].
- **Hostile: no-cap is mostly ceiling.** On M(2)'s no-cap problems Think-SFT is already 94 % right (held-out 93.2 %, 12.5 errors in 185 problems). M(2) removes **0.31 [0.04, 0.57]** of those held-out errors; RL removes 0.44 [0.31, 0.57] of the base's, the dial 0.47, Think-SFT 0.41 of RL's. The intervals overlap: at matched headroom M(2)'s no-cap gain is not shown to be smaller than RL's. Reweighted to the same difficulty mix (B's samples 0-1), RL - base gives +8.6 [4.8, 13.0] against M(2)'s +2.1 [0.2, 4.3], but inside the top stratum the base is 88.5 % right and Think-SFT 96.2 %, so this match does not equalise headroom. Honest wording: "M(2)'s gain sits where Think-SFT's errors are, on cut-off answers; once Think-SFT may finish, about half of it remains, on one sample."
- No-cap is a post-treatment subset: it drops exactly the problems on which finishing differs, and it is defined from all samples of both arms (more samples = smaller subset; M(2) hard328 has 3 samples, the rest 4).
## Caveats
- Think-SFT runs with the base's cue and the RL tokenizer's chat template, not its own ChatML / `<think>` format (work-8b2ec9 open). RL is plain, the base and Think-SFT cued.
- Every 32,768 number is one sample per arm (seed 3,000,000; M(2) pair 3,010,000; Think-SFT 2 samples in the extra row, RL still 1), and claim 2 and claim 3 use different seeds; reruns at one seed are not identical (vLLM): the cap32 run's 16,384 scores (207, 193, 152) differ from the stored sample 0 at the same seed (212, 207, 161); 1 / 2 / 7 of 328 token counts match. Its 16,384 score scores a cut answer 0; the stored 16k cells score 5-27 cut samples right (grader finds an answer in a cut text), so cap32's 16k is slightly conservative.
- The 16,384 -> 32,768 change counts problems near the cap: 93 Think-SFT answers past 16,384 decide it; 68 of them finish wrong.
- Single-sample cells: dial MATH-500, all cap32 cells. Post-hoc: the no-cap split, the decomposition, the matched control and the headroom share are defined in this script, after the results; only the cap32 run (SPEC_cap32) and M(2) amendments were filed in advance.
- Fresh2026 no-cap subsets are 30 to 45 problems; headroom share there is undefined in 156 of 10,000 resamples.

## Review of draft 1 (`facts.json` `review`)
- `bonferroni` (98.33 %, same resamples): RL - base -0.6 [-2.4, 1.2]; Think-SFT - RL +6.4 [3.1, 10.1]; M(2) - Think-SFT -3.4 [-7.3, +0.3]: the M(2) change no longer excludes 0.
- `strict_32768`: Think-SFT problem 320 (seed 3,010,000) is cut at 32,768 and graded right; scored wrong: 233, M(2) - Think-SFT +3.7 [-0.3, 7.3], change -3.1 [-6.1, 0.0] (98.33 %: [-6.7, 0.6]). Answers reaching 32,768 in all cap32 cells: Think-SFT 2 + 1, base 1, RL 0, M(2) 0; graded right: only problem 320.
- `right_but_cut_off_16384` (estimate): stored 16k runs grade cut samples right at 3.5 (Think-SFT), 1.75 (RL), 2 (M(2)), 1 (base) per sample; crediting them in the 16k view moves the changes to -0.8, +5.9, -2.9.
- `native_format`: own ChatML/<think> format, hard328 seed 3,000,000, 1 sample: 204 -> 232 (cue 207 -> 230; native - cue -0.9 [-4.3, 2.4], +0.6 [-3.4, 4.6]); 104 answers past 16,384, 3 cap hits. Native - RL +3.4 -> +11.3, change +7.9 points, totals only (rows not in git, no interval). MATH-500 (seed 182,000,000): 464 -> 474.
- `rl_reference`: RL's 193 at the 16k view is 13 below the spec's 206 (limit 12): the rerun rule was triggered and not applied. Stored samples 207, 190, 209, 194 (mean 200.0). With 200 + 2 in place of 195, Think-SFT - RL at 32,768 is +8.5 (two Think-SFT samples: +9.1), not +10.7.
- `late_precision`: right among answers past 16,384: base 4/64, RL 2/20, Think-SFT 23/93 and 24/90, M(2) 13/56. Still cut at 32,768: 1, 0, 2, 1, 0: further gain at most 0.6 points per model.
## Pending (not in git at the last pull)
- Second M(2) sample at 32,768, seed 3,000,000 (amendment 3, work-8b4030, job f975). `facts.json` `pending`.
- Think-SFT at 32,768, hard328 samples 2-3 (README: 235, 232) and the vote (238 -> 244), and all fresh2026 samples (work-dc9359): rows only in s3 handoff/cap32vote/. In git: sample 0 (`cap32/rows-01`) and sample 1 (inside `transplant/cap32_m2_s1-01/rows.jsonl`); the README's 4-sample +6.7 [5.0, 8.5] is not recomputed.

## Reproduced / not reproduced
- Reproduced: every per-sample count of every cell, M(2) +7.4 [5.2, 9.8], fresh +9.0, the audit's no-cap +1.1 [0, 2.8] n 45, the board's +0.5 [-2.7, 3.8] (here [-2.74, 3.66]), the cap32_m2_s1-01 readout (245/232, 234/210, cap hits, tokens, 56:13 and 90:24 late answers, the three differences and intervals), the cap32 readout (230/207, 195/193, 156/152; 93/91/23, 20/20/2, 64/63/4; tokens).
- Not reproduced: README cap32 "stored 164" (base) and "206" (RL) are the spec's reference numbers; day1_3 sample 0 is 161 and 207 (164 is not a first-attempt or restart count of day1_3). Scout: step 100 - base +3.0 / no-cap +3.1 used samples 1-3 only; with sample 0 (`per_problem.json`) it is +3.1 / +3.4. Everything else in the scout's table matches.

**Example (`examples.json`):** hard328 problem 57 (AIME 2023 II #7, gold 928): Think-SFT is cut at 16,384 and right at 28,502 tokens; RL finishes wrong (3072) at 13,516 tokens; RL's 4 stored samples are all finished and wrong; Think-SFT's stored samples: 3 cut, 1 wrong.
