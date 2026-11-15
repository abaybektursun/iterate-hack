# SPEC: direct test of round-09/training-m01, "the template sets where the answer is stated, not how the model reasons"

Board work-996b09. Theory round 13, plan in `studies/theory/results/wide/round-13/direct_tests.json` (entry
`round-09/training-m01`). Written before the readout was computed. Stored texts only: no GPU job, no forward pass;
a tokenizer (no weights) on CPU.

## The claim

Mechanism `round-09/training-m01`: Think-SFT learned to state its answer inside its ChatML template (opened by
`<think>`). On the raw template with the cue it reasons as well, but sometimes puts the final answer where grader v3
misses it. Its own template restores the trained ending and leaves reasoning length and cap behaviour unchanged.

Consequence tested: the own template does not make Think-SFT drift less. On hard328 at cap 32,768, the share of rows
whose first 16,384 generated tokens show a drift sign is the same in the own-template cell as in the raw-template cue
cell, within the seed scatter of the raw-cue cell.

## Why only this mechanism

The one rival that talks about the template, `run-04/f2-m05`, predicts the opposite: in its own format Think-SFT
samples on-distribution, so fewer long answers drift. Every other carried mechanism in round 13 (direction split,
rescoring of capped rows, seed scatter, vote abstention, difficulty mix, edit strata) says nothing about a template
effect on drift. No posted result measures drift in the own-template cell (checked: `tools/recall.py`, board
result-dd9239 reports only right counts).

## Files

- Own template, cap 32,768, seed 3000000, 1 sample: `studies/rlneurons/results/native/hard328-01` (result-dd9239,
  232 right at 32,768, 204 at 16,384). Texts: `runs/native_sft_hard328_joined/answers.jsonl` (join of jobs
  ih-1115-163313-7486 and ih-1115-163401-a4ba; not in git, read from the `iterate-hack-shots` worktree).
- Raw template + cue, cap 32,768, seed 3000000, 1 sample: `studies/rlneurons/results/cap32/sft_cue-01` (result-c8b994,
  230 right at 32,768, 207 at 16,384; job abaybektursun-1115-005756-309b). Texts:
  `runs/abaybektursun-1115-005756-309b/answers.jsonl` (same worktree).
- Raw template + cue, cap 16,384, 4 samples: `studies/rlneurons/results/thinkvote/hard328_sft1_cue_s4-01`. Texts: one
  folder per sample, jobs abaybektursun-1115-000503-1e5f (sample 0), -000525-ea4e (1), -014823-ef56 (2),
  -014833-1daa (3), `runs/theory-tests/<job>/answers.jsonl` (in the `iterate-hack-theory` worktree). Sample = (seed -
  3000000 - index) / 10000.
- Drift instrument: `studies/rlneurons/analysis/drift.py` (unchanged, imported), its planted tests
  `analysis/drift_test.py`, its stored readout `studies/rlneurons/results/drift/describe-01`.

## Computation

1. Load the three cells (328 rows each; 4 x 328 for thinkvote). Check v3 right counts: own template 232 at 32,768 and
   204 counting rows with `n_new` > 16,384 wrong; raw cue 230 and 207. Stop on a mismatch.
2. Tokenize each text with drift.py's tokenizer (`allenai/Olmo-3.1-7B-RL-Zero-Math` @ 364820b, the tokenizer the
   runs generated with; the plan named the Think-SFT tokenizer, changed so the instrument is exactly the one that
   produced describe-01; both are the Olmo 3 vocabulary). The cue cells' text begins with the 3 cue tokens, so the cut
   is at token 16,384 + max(0, n_tok - n_new) of the re-tokenized text, i.e. the first 16,384 generated tokens. The
   cut text is text[:char end of that token]. The thinkvote rows (cap 16,384) are therefore not cut.
3. Drift signs on the cut text, both from drift.py: (a) `switch`: `drift.episodes(cut text)` is non-empty (at least 5
   non-Latin letters within 200 characters of each other); (b) `repeat`: `drift.repeated(cut ids)` has any 1 (a
   50-token window equal to an earlier one). Drifted = (a) or (b). Both signs and the union are reported per cell.
4. Primary statistic: D = 100 x (drifted share, own template) - 100 x (drifted share, raw cue 32k), points of 328.
   Paired bootstrap over the 328 problems, 10,000 resamples, numpy default_rng(0); 95 % percentile interval (the
   plan's level) and 90 % (the study's level).
5. Null: drifted share of each of the 4 thinkvote samples; all 6 pairwise differences; S_max = largest absolute
   pairwise difference. Also D_k = own template (cut) minus thinkvote sample k, k = 0..3.
6. Secondary, not deciding: (i) cap hits at 16,384 (n_new > 16,384) and median n_new of rows finished within 32,768,
   own template against raw cue; (ii) raw-cue 32k rows that finished and v3 grades wrong: how many have, after the last
   line that reads just "Answer:" (case-insensitive, `*`, `#`, `_` and spaces stripped), a next non-empty line that
   math-verify 0.9.0 judges equal to the gold answer; (iii) the same count for the own-template cell; (iv) each sign
   separately, own template against raw cue.

## Refuting observation and frozen threshold (the plan's, unchanged)

Refuted if all three hold: D <= -2.0 points; the upper end of D's paired 95 % interval < 0; |D| > S_max.
If any one fails, the claim holds. A positive D is also reported as evidence against `run-04/f2-m05`.

## Null

Seed scatter within one template: the drift-share differences between the four stored raw-cue samples (same model,
prompt and grader, other seeds). A template difference inside S_max cannot be told from re-sampling. Weakness, stated
in advance: S_max is the largest of 6 differences, a generous bar; the paired interval rule carries the rest.

## Instrument checks (before the readout)

- `analysis/drift_test.py` passes (10 planted script switches found, 10 negatives not flagged, a planted loop found
  by the 50-token repeat, a clean text not).
- Reproduce describe-01 from the texts: hard328_sft switch on 156 of 1,312 thinkvote samples; cap32_sft switch on 83 of
  328 full (uncut) raw-cue 32k texts.
- The cut can fail: report how many 32k rows have a switch only after token 16,384 (counted drifted uncut, not cut).

## Seen before writing this spec

Right counts of both 32k cells (match the posted ones). Thinkvote sample 0 only, full text: any repeated 50-token
window on 30 of 328 rows, a switch on 34 (to check the repeat sign is not near 100 %). 16 of 328 cap-32k raw-cue
texts share their first 2,000 characters with thinkvote sample 0 (same seed and prompt, other hardware); the
other 312 are different draws. describe-01's published counts. No drift number of the own-template cell.

## Outputs

`studies/theory/analysis/direct_template.py` -> `studies/theory/results/direct/template-01/`: `readout.json`,
`examples.json` (one row drifted, one not, real text excerpts and score), `rows.jsonl` (per row flags, no text),
`reading.md` (10 raw rows read by hand), `run.json`.
