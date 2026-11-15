# SPEC_fresh: Think-SFT, RL and the cued base on competition problems published in 2026

Board: idea-67db73, work-7c069c. Builds on result-818c20 (Think-SFT + cue 241 of 328 under the vote over 4, RL 221, cued base
192) and result-f6a8bc (prompt-only overlap scan of the Think-SFT training data: 6 of the 328). Written 2026-11-15 UTC before
any model saw the set.

## Question

Does Think-SFT's lead over RL-Zero-Math under the four-sample vote hold on competition problems that were published after the
training data of all three models was made? An overlap scan can only show overlap it can match; a problem that did not exist
cannot be in the data in any form.

## Cutoffs (primary sources, read 2026-11-15)

| Model | Stated cutoff | Hard upper bound (Hugging Face commit dates) |
|---|---|---|
| base `allenai/Olmo-3-1025-7B` @ `a81bae4` | model card: "Date cutoff: Dec 2024"; paper 2512.13961 section 3: "104 dumps from the CommonCrawl corpus, with a cutoff date of December 31, 2024" | weights committed 2025-10-09 |
| Think-SFT `allenai/Olmo-3-7B-Think-SFT` @ `6ff8575` | model card: "Date cutoff: Dec. 2024."; data `allenai/Dolci-Think-SFT-7B`: card states none | weights 2025-10-14; all 156 data files 2025-10-16 |
| RL `allenai/Olmo-3.1-7B-RL-Zero-Math` @ `364820b` | model card: "Date cutoff: Dec. 2023." (contradicts the base card; unexplained); data `allenai/Dolci-RL-Zero-Math-7B`: card states none | weights 2025-12-12; data 2025-11-19 |

The stated cutoff (December 2024) covers the web crawl only: the post-training prompt sets were assembled in 2025 and state no
date. The bound used here is therefore the upload of the last weights, 2025-12-12. Every problem of the set was first held as
a contest on or after 2026-02-05.

What "fresh" guarantees: the contest papers of the set were published after every weight file existed, so the training data
cannot hold these papers, their solutions or discussions of them. What it does not guarantee: that a contest did not reuse or
vary an older problem. The overlap check below found one such case and it is dropped; a reused problem whose older source is
not in the RL training prompts would not be found (the Think-SFT data is not scanned here).

## The set: `data/fresh/fresh2026_v1.json`, n = 136 (`prep/fresh_prep.py`)

Candidates (165), all of each source:

- AIME 2026 I (2026-02-05) and II (2026-02-11): `MathArena/aime_2026` @ `d61f486` (cc-by-nc-sa-4.0), 30 problems.
- HMMT February 2026 (2026-02-14), Algebra and Number Theory, Combinatorics, Geometry and 3 Team problems:
  `MathArena/hmmt_feb_2026` @ `589a53f` (cc-by-nc-sa-4.0), 33 problems.
- HMMT February 2026 Guts round, 36 problems, and HMMT November 2026 (2026-11-07) General 10, Theme 10, Team 10, Guts 36: the
  official solutions PDFs (urls, sha256 and header dates in `data/fresh/transcribed_v1/sources.json`), transcribed on
  2026-11-15 by Claude subagents from the rendered pages and cross-checked with `pdftotext`: statement verbatim, mathematics
  in LaTeX, the official answer from the "Answer:" line. The transcription is by a language model and no person has checked
  it: the AIME + HMMT February subset from Hugging Face (59 problems) is reported separately for that reason.

Drop rules, fixed before any model output, applied in this order (counts in `data/fresh/fresh2026_v1_meta.json`):

1. Published before 2026: AIME 2026 I #1 is the 2020 Purple Comet Middle School #8 and an exact match in the RL training
   prompts (found by the overlap check on the candidates). 1 dropped.
2. Figure: the statement contains `[asy]` or one of the words figure, diagram, shown, pictured; or the transcriber marked that
   the PDF has a figure which the words do not fully describe; or a published dataset card says the official diagram is
   needed (HMMT February Geometry, MathArena index 25; `kumarjau1998/HMMT2026` card). 20 dropped.
3. Estimation problems of the Guts rounds (scored by closeness). 7 dropped.
4. More than one final answer (a tuple or list), or proof only. 1 dropped.
5. Grader v3 check, laptop: `Answer: $<gold>$` must grade right against the gold; `Answer: $<gold> + 1$` and the next
   problem's gold must grade wrong. 0 dropped: all 136 pass both. An answer printed as two equal forms `a = b` has gold `a`,
   and `b` must grade right against `a` (asserted; all pass).

By source: AIME 27, HMMT Feb (MathArena) 32, HMMT Feb Guts 28, HMMT Nov General 7, Theme 6, Team 8, Guts 28.

Overlap with the RL training prompts (`analysis/rln3_overlap.py`, unchanged, against `allenai/Dolci-RL-Zero-Math-7B` @
`93b5e49`, 13,314 prompts): 0 exact, 0 near of the 136; the largest 8-gram share is 0.375 (shared boilerplate of the AIME
answer format). `results/fresh/overlap-01/overlap.json`.

## Cells

`jobs/run_fresh.py` = `run_cell` with `--set fresh2026` registered (run_cell.py itself is being edited under work-ab6833).
Same prompt template (`pair1`), T 1.0 / top-p 1.0, cap 16,384, grader v3, no restarts, 4 samples, one job per sample: sample s
is `--samples 1 --seed 7000000 + 10000 s` (problem i gets `seed + 10000 s + i`, the rule of SPEC_day1_3 and SPEC_thinkvote),
joined with `analysis/thinkvote_join.py`.

- Think-SFT + cue: `wsp_edit --recipe interp --other think_sft --alpha 1.0 --rounding nearest --seed 0`, then
  `run_fresh --model-path /tmp/theta --model-label sft1 --prompt cue`.
- RL plain: `run_fresh --model rl --prompt plain`.
- base + cue: `run_fresh --model base --prompt cue`. The control: it shows the set's difficulty and that the instrument
  separates models as it does on the 328.

Smoke before the full jobs: the first 10 problems, base + cue; rows read by hand (statement rendered, worked answers, grading
of right and wrong rows).

Cost estimate: about 11,500 generated tokens per answer (AIME 2025 and HMMT Feb 2025 rows of the 328: 11,700 to 14,300), so
1.6 M tokens and about 35 minutes per job, 12 jobs, about 7 GPU-hours, about 28 USD at Modal's H100 price.

## Readout

`analysis/day1_vote.py` per model (single, vote over 4, pass@4, tokens; `--minus` for Think-SFT minus RL and each minus the
base, paired bootstrap), `analysis/frontier.py --fixed results/frontier/math500-01/chosen.json` (sequential vote and the 24
draw orders; rules chosen on MATH-500, nothing chosen on this set), cap hits and precision of finished answers per model, and
the same on the Hugging Face subset (59) and by source. Run folders `results/fresh/<arm>-01/`.

## Power, stated before the run

With n = 136 the paired 95 % interval of the vote difference is about +/- 5 to 6 points (the 328 gave +/- 3.3; scaled by
sqrt(328 / 136)). A true difference of the size seen on the 328 (+6.1) would exclude 0 in roughly two runs of three. An
interval that contains 0 is therefore "not separated on 136 problems", not "no lead".

## Hypotheses, each with the observation that refutes it

H1. Think-SFT's vote over 4 beats RL's by at least 2 points on the fresh set. Refuted if the paired interval of Think-SFT
minus RL is at or below 0; held if the point estimate is at least +2 and the interval is above 0; otherwise not separated.

H2. Think-SFT still abstains more and is more precise: cap-hit rate above RL's by at least 10 points and precision of
finished answers above RL's by at least 10 points. Refuted if either difference is below 5 points.

H3. The instrument works on this set: base + cue is below RL in one sample and under the vote (as on the 328). Refuted if the
base's vote is at or above RL's.

## Predictions (from the 328's rows by source: AIME 2025, HMMT Feb 2025; HMMT November is an easier contest)

| | Think-SFT + cue | RL plain | base + cue |
|---|---|---|---|
| vote over 4, right of 136 | 74 [62, 86] | 64 [52, 76] | 49 [38, 60] |
| one sample, mean of 4, right of 136 | 59 [49, 70] | 54 [44, 65] | 36 [27, 46] |
| cap hits, share of samples | 40 % [30, 50] | 14 % [8, 22] | 33 % [23, 43] |
| precision of finished answers | 80 % [70, 88] | 50 % [40, 60] | 42 % [32, 52] |
| tokens per sample | 12,000 | 11,000 | 11,000 |

P1. Vote, Think-SFT minus RL: +7 points (10 problems), interval half-width 5 to 6 points. Refuted if the point estimate is
below +2 or above +12 points (fewer than 3 or more than 16 problems), or if the half-width of the paired interval is outside
4 to 7 points.
P2. On the Hugging Face subset (59): Think-SFT vote 26, RL 20, base 14. Refuted if Think-SFT's vote is not above RL's on the
59, or if any of the three counts is more than 6 problems from its prediction.
P3. On HMMT November (49): the three models are closest there (Think-SFT 35, RL 33, base 27). Refuted if the vote difference
Think-SFT minus RL in points is larger on HMMT November than on the other 87 problems, or if any of the three counts is more
than 6 problems from its prediction.

Added 2026-11-15 after the main session's review, before any full-run row was read (the jobs were running; only the 10-row
smoke of the cued base had been read): the refuting observations of P1 to P3 above, and two notes on the set.

- `hmmt_feb2026/9` (gold `50(1 - \frac{1}{2^{101} - 1})`): grader v3 takes a boxed 50.0 or 49.9999999 as right but not 50
  (found by the main session). Grader and data stay as they are; this problem's 12 samples are read by hand and every headline
  number is reported twice, as graded and without this problem (n = 135).
- `aime2026/25` has MathArena's wording (the sum of all possible BC, gold 850), which differs from the contest paper's; it is
  self-consistent and kept.
- The Think-SFT training data (`allenai/Dolci-Think-SFT-7B` @ `83f618e`, every message of every row) is scanned for the 136
  with the rule of `analysis/wsp1_sft_overlap.py --turns all`; flags are reported, and every headline number is also given
  without flagged problems.
