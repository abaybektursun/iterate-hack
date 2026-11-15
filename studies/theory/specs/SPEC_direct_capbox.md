# SPEC: direct test of run-08/f2-m02, "a native 16k run credits boxes written before the cut"

Board work-cb6617. Stored rows and stored answer texts only: no GPU job, no forward pass. A tokenizer (no weights,
already in the local Hugging Face cache) is loaded on CPU for one check only (step 6).

## The claim

Mechanism `run-08/f2-m02` (round 13, `studies/theory/results/wide/round-13/direct_tests.json`, gain 1.721): a count
"at 16,384" rescored from a 32k run differs from a native 16k run. The rescore scores every row longer than 16,384
tokens wrong; a native run lets grader v3 credit a box already written inside a row cut at the cap ("RL 69 % of capped
rows, base 17 %, Think-SFT rarely"). Plan claim: in native 16,384-cap hard328 runs, grader v3 credits a right answer to
a real share of the cap-hit rows: for RL plain at least 10 % of its cap-hit rows, and more than Think-SFT's share.

## Does the claim follow from this mechanism alone?

- From the cause: if a capped RL row often holds a box and v3 takes the last box, some of those boxes are right, so
  C/H (credited cap-hit rows over cap-hit rows) is well above 0 for RL and near 0 for a model that rarely boxes
  mid-reasoning (Think-SFT).
- Rivals: round-09/grader-m06 (a count at a cap scores every unfinished answer wrong) and run-08/f2-m06 (a cap hit
  abstains) both predict C/H near 0 for every model. Seed-scatter mechanisms predict nothing about capped rows. So a
  large RL C/H is predicted by this mechanism only. Agreed.
- The 69 % / 17 % figures come from knowledge-16c62a, which is about MATH-500 cued rows ("RL capped rows already hold a
  boxed answer in 69 % of cases"), not hard328, and they count a box, not a right box. The 10 % threshold is the plan's.
- No posted board result gives the credited share of native hard328 cap-hit rows (recall search, 2026-11-15).

## Seen before this spec was written (while checking the files)

From the committed rows.jsonl files, before any interval was computed: RL plain (day1_3, attempt 0) 7 of 114 cap-hit
rows have score_v3 = 1; with restart attempts 1-2 added, 9 of 171. Base cue attempt 0: 4 of 286; all attempts 5 of
498. Think-SFT cue: 14 of 378 (no restarts). Nothing about texts, boxes, intervals or the 32k cut was seen.

## Change to the plan, and why

The plan says "load every row of rows.jsonl". The RL and base day1_3 folders hold restart rows (attempt 1, 2): a new
draw on the same problem made only after a cap hit. Think-SFT's folder has none. Primary rows are attempt 0 of each of
the 4 samples, for all three models: one unconditioned draw per (problem, sample), the same row set for the three
models, and the rows behind the posted single-sample counts (readout `cap_hits_attempt_0`). All rows including
restarts are reported as a secondary line with the same rule applied, and the report states if the verdict differs.
This choice was made after seeing the counts above (7/114 against 9/171); both are reported side by side.

## Files

- Native 16,384 cap, 4 samples, hard328: `studies/rlneurons/results/day1_3/hard328_rl_plain_s4r2-01/rows.jsonl`
  (job abaybektursun-1114-200505-5ff2), `day1_3/hard328_base_cue_s4r2-01/rows.jsonl` (abaybektursun-1114-200457-e8e6),
  `thinkvote/hard328_sft1_cue_s4-01/rows.jsonl` (4 jobs 1115-000503-1e5f, -000525-ea4e, -014823-ef56, -014833-1daa).
- Texts: `runs/<job>/answers.jsonl` from `uv run tools/gpu.py get <job>` (not committed).
- Single-sample check: day1 jobs abaybektursun-1114-151540-86ef (RL plain, 20 cap hits) and -151534-e72c (base cue,
  77 cap hits); their rows are only in `runs/`.
- 32k rows: `studies/rlneurons/results/cap32/rows-01/{rl_plain,sft_cue}.jsonl`, `rows-02/base_cue.jsonl`; texts in
  `runs/abaybektursun-1115-005823-8ac9`, `runs/abaybektursun-1115-005756-309b` (copied from the iterate-hack-shots
  worktree's runs/).
- Grader: `studies/rlneurons/lib/rln4_lib.py` `grade_v3` / `extract_v3` (what run_cell wrote as score_v3).

## Computation (`studies/theory/analysis/direct_capbox.py`)

1. Load rows. Cap hit = `cap_hit` true (equals finish_reason == 'length'; checked). Check per-sample attempt-0 cap hits
   against each readout's `cap_hits_attempt_0` (RL [35, 26, 24, 29], base [71, 66, 81, 68], Think-SFT [89, 95, 92,
   102]) and all-attempt totals against metrics.json (171, 498, 378). Stop on any mismatch.
2. For each model, H = cap-hit rows, C = those with score_v3 = 1. C/H with a Wilson 95 % interval (the rule) and a
   90 % cluster bootstrap over problems (10,000 resamples of the 328 problem indices, all rows of a drawn problem kept
   together, numpy default_rng(0)).
3. RL - Think-SFT and RL - base shares, same cluster bootstrap (each model's problems resampled with the same index
   draw), 95 % (the rule) and 90 % intervals.
4. Texts: join every cap-hit row to its answer text by (problem_index, sample, attempt). Regrade the text with
   grade_v3 and require that the stored score_v3 and extracted_v3 are reproduced on every row (instrument check).
   Report per model: share of cap-hit rows whose text holds any `\boxed{`, share where v3 extracts any answer, and for
   each credited row the v3 mode (boxed or 'Answer:' marker) and the character position of the winning candidate as a
   share of the text length.
5. Planted controls of the grader on truncated text (instrument can fail and can pass): (a) take every finished right
   row of each model and cut its text just before the start of the winning v3 candidate: the regrade must credit
   almost none (a box before it can still be right; report the count). (b) take every uncredited cap-hit row and append
   `\boxed{<gold>}` to its text: the regrade must credit all.
6. 32k consistency: in cap32 rows with n_new > 16,384, count rows the 16,384 rescore credits (0 by construction, it
   counts them wrong). Then cut each such text at 16,384 generated tokens (re-tokenize the text with the
   Olmo-3.1-7B-RL-Zero-Math tokenizer, the one every run used, and decode the first 16,384 ids) and regrade with v3:
   C32/H32, the same quantity as C/H measured on 32k text. Report the token-count match between the re-tokenized text
   and stored n_new on these rows.
7. Secondary lines, reported, not deciding: all attempts; base sample 0 against samples 1-3 (second-sample scatter of
   the share); day1 single-sample RL and base C/H from runs/ texts; per-sample C/H.

## Refuting observation and frozen threshold (the plan's, unchanged)

- Refuted: RL plain attempt-0 C/H Wilson 95 % upper bound < 0.10, or the bootstrap 95 % upper bound of
  (RL share - Think-SFT share) <= 0.
- Holds: RL C/H point estimate >= 0.10 and the 95 % lower bound of (RL - Think-SFT) > 0.
- Otherwise undecided (counts as not holding). This includes an RL point estimate below 0.10 with a Wilson upper bound
  at or above 0.10, a case the plan's text does not name.

## Nulls

Primary: Think-SFT cue's native cap-hit rows (same set, same cap). Secondary: base cue's cap-hit rows, and base
sample 0 against samples 1-3. Rival null (grader-m06): credited share 0, which the 32k rescore gives by construction.
The cut-32k regrade (step 6) is the direct analog that tells whether the native and rescored counts would differ.

## Outputs

`studies/theory/results/direct/capbox-01/`: `readout.json`, `examples.json` (one credited cap-hit row, one uncredited
cap-hit row holding a wrong box: text tail, extracted answer, gold, score), `reading.md` (10 raw cap-hit rows read by
hand, one line each), `run.json` (commit, command, input jobs).
