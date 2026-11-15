# Outside math and code, step 1 (2026-11-15 UTC, written before the first run)

Question: every configuration of this study was chosen on MATH-500. Do the gains it found (the opening cue on the untrained base,
and Think-SFT with the cue, the best row on hard328) also appear on benchmarks that are neither math nor code? The objection it
answers: a swarm that hill-climbs one benchmark may only have fitted that benchmark.

Closest published numbers: Wang et al. 2610.06851 test the cue on math sets and HumanEval only (Table 6); our code pair
(`SPEC_code1.md`, result-59ed1a) gives the cue +19.3 points on HumanEval+ and MBPP+. No published or team number has the cue on a
benchmark outside math and code (Exa, 2026-11-15, two phrasings). For RL from a base model on math data, SimpleRL-Zoo
(2503.18892, Table 2) reports gains on MMLU and GPQA for other model families, with no cue arm.

## Measurement

- Items: `data/ood1/ood1_items.json` (sha256 in `data/ood1/frozen_ood1.json`), built by `prep/ood1_build.py`, seed 0, before any
  generation. 250 of MMLU-Pro (test; the 9 categories that are not math, physics, chemistry, engineering or computer science; 28
  or 27 per category; up to 10 options) and 250 of BBH (10 tasks with a one-letter target and no arithmetic or code, 25 each).
  Chance: 28.4 of 250 and 67.9 of 250.
- Prompt: the study's math prompt unchanged (`pair1`: "Solve the following problem step by step ... Answer: $Answer"), RL-Math
  tokenizer, for every model. The problem text ends with "The answer is the letter of the correct option."
- Sampling: T 1.0 / top-p 1.0, cap 16,384, one sample per item, seed 61000000 + item index, the same seeds in every cell.
- Grader: `lib/mcq_lib.py`: the first option letter after the last "Answer:"; no "Answer:" or no letter is wrong; a cap hit is
  graded like any answer. Checked by `lib/mcq_lib_test.py` (12 cases, 7 that must be wrong) and, in every job before generation,
  on all 500 items (gold answer right, next letter wrong, no "Answer:" wrong). Known weakness: a capital "I" after "Answer:"
  reads as option I.
- Cells, one job each (`jobs/run_mcq_cell.py`): (1) base plain; (2) base + Math cue `' line!\n\nOkay'`; (3) RL-Zero-Math plain;
  (4) Think-SFT + Math cue. Nothing is chosen on these items: the cue, the setting and the cap are those of the math cells.
- Statistics: right of 500 and per benchmark, Wilson intervals; cell differences by paired bootstrap (5,000) over items, in
  points; cap hits, answers without a letter and generated tokens per item for every cell.

## Hypotheses

- H1, the cue is not fitted to math: (2) minus (1) is above 0 on the 500 and on each benchmark. Refuted if an interval includes
  0 or is negative. A refutation on both benchmarks supports the overfitting objection for the cue.
- H2, RL on math transfers: (3) minus (1) is above 0. Refuted if the interval includes 0.
- H3, the cue carries at least half of what RL gives here, as on math (78 %) and code (58 %): ((2) - (1)) / ((3) - (1)) >= 0.5.
  Tested only if H2 holds.
- H4, the best row keeps its order: (4) is not below (3). Refuted if the interval of (4) minus (3) is below 0. Think-SFT was
  trained on general data, so H4 holding says less about overfitting than H1.

Not run (one seed, lowest cost first): the vote over four samples after restart, RL-Math with the cue, Think-SFT plain.

Cost: 500 answers per cell. Smoke first: `--grader-check-only` on the laptop (no model), then `--n 10` on the base with the
cue. Expected under 15 H100 minutes per cell, about 1 H100 hour for the four.

## Amendment 1, 2026-11-15 15:25 UTC (after cells 1 and 2 were read, before cells 3 and 4 finished)

Reading the 235 and 114 answers of cells 1 and 2 that grader v1 gave no letter: many end with the answer in another form
(`**Answer**: $\boxed{C}$`, `The answer is (D)`, a bare `\boxed{G}`), which v1 counts as wrong. The cued base writes these forms
more often than it writes nothing, so v1 understates every cell by a different amount. Grader v2 (`mcq_lib.grade_v2`): the first
option letter within 40 characters after the last of "Answer:" (markup allowed before the colon), "answer is" (not the prompt's
own sentence "answer is the letter of") and `\boxed{`. Tested in `mcq_lib_test.py` (10 more cases, 5 that must be wrong). The
readout reports both graders for every cell and difference, from the same texts. The hypotheses are judged under v1, as written;
v2 is the better estimate of each score. Cells 1 and 2 on the 500: v1 114 and 229, v2 as in the readout.
