# SPEC selfopen-01: rejection sampling on the plain base's own opening

Written 2026-11-15 before any job. Work item work-c82156, idea idea-f1bae8. The experiment is the entry
`r5-m10:theory:intervention` of `results/engine/round-05/experiments.md` (both predictions are on file there); this spec
implements its "Run" text and writes down every choice the text leaves open.

## Question

The plain-prompt Olmo-3 base at T 1.0 opens about one answer in five on its own with a newline then "Okay", and those answers
are right far more often than the others. Is the self-opened answer the cued answer as a whole (pick the base's own
self-opening drafts and the plain cell rises toward the cue's 410), or does the opening only mark easy problems and luck?

## Measurement

- Model `allenai/Olmo-3-1025-7B` at revision `a81bae42db3975be1671e27b9c9a56da1a9f980f`, tokenizer of
  `allenai/Olmo-3.1-7B-RL-Zero-Math` at `364820b002fc8e81d11a81c7fc9dd6b49c83cd05` (both from
  `studies/rlneurons/data/rln4/frozen4.json`, the T3 cell's own file). MATH-500, `data/rln4/math500.json` (500 problems).
  Prompt: the team's plain MATH-500 prompt (pair1 chat template, `n13_score.render_ids`, checked against
  `data/rln4/prompt_ids.json`), no prefilled tokens. Sampling T 1.0, top-p 1.0, repetition penalty 1.0, vLLM 0.32.0 through
  `rln4_gen.VllmEngine` (the engine of T3). Cap 16,384 new tokens counted from the start of the answer, the opening included.
- Stored rows: T3 (plain base, T 1.0, seed base 47,000,000)
  `s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t3-01/t3/T3.jsonl`, sha256 `65a519ba...e87a`; T1 (base + cue
  ids [1584, 2268, 33413], T 1.0, seed base 41,000,000) `.../r4/base_rl-02/out/T1.jsonl`, sha256 `c65a12fc...ea85`.
- Self-open test: `'\nOkay' in text[:60]` (case-sensitive), as in the round-05 test scripts.
- For each problem i whose stored T3 row does not pass the test (`data/selfopen01_t3.json` "regenerate", written by
  `prep/selfopen01_t3.py`): draws j = 1..32 of at most 24 new tokens, seed 47,000,000 + i + 10,000 j. Arm **main** keeps the
  first draw that passes the test (draw 1 if none does) and continues it to the cap with the draw's own seed. Problems whose
  stored T3 row passes the test keep that row unchanged.
- **Count**: right answers of 500 by grader v3 (`rln4_lib.grade_v3`, the grader of `grader/rln4_grader_v3.py`), one answer per
  problem: the stored T3 row for self-opened T3 rows, otherwise the continued answer. Cap hits keep v3's score; an empty
  extraction is wrong.
- Recorded without changing the count: per problem the draws used and whether any draw self-opened; problems that never
  self-open in 32; cap hits; mean generated tokens; accuracy on (a) the stored self-opened rows, (b) the regenerated problems
  that self-opened, (c) the never-self-opened fallbacks; the stored plain T3 and cue T1 counts on the same 500 and on each
  subset (graded v3 from the stored text).

## Predictions on file (round 05)

| Who | Count of 500 | Interval |
|---|---|---|
| r5-m10 (the opening picks the whole mode; never-self-open problems fall back to the plain mode) | 375 | [348, 400] |
| r5-m10-rival (self-checking register; self-opened continuations at cued accuracy) | 405 | [386, 422] |
| stored reference: plain base T3 | 224 | |
| stored reference: base + cue T1 | 410 | |

Both predictions assumed about 168 stored self-opened T3 rows. The instrument check below finds 94. The predictions are
scored as the frozen numbers they are.

## What each outcome means

- Count in [348, 385]: only r5-m10's interval holds. In [386, 400]: both hold; the absolute errors decide. In [401, 422]:
  only the rival's holds. Below 348 or above 422: both are refuted.
- Refutes "the self-opened answer is the cued answer as a whole": accuracy (b) more than 10 points below T1's accuracy on the
  same (b) problems, or (b) not above the control arm on the same problems (next section).
- Refutes "the opening only marks easy problems": main minus control on the (b) problems is above 0 with the bootstrap
  interval excluding 0, on problems that are the same in both arms.

## Control arm (selection step), same job

For the same regenerated problems, keep the first draw that does NOT pass the test (draw 1 if all 32 pass) and continue it
the same way. The selection effect is main minus control on the (b) problems: right answers, in points, with a paired
bootstrap 95 % interval (`n13_score.paired_bootstrap`, 5,000 resamples, seed 0). Expected under "the opening sets the mode":
control near the plain T3 level on those problems. If the interval contains 0, the selection step measures nothing.

## Choices the entry leaves open (most literal reading)

1. The test runs on the decoded text of the draw (at most 24 tokens) for draws, and on the full stored answer text for T3
   rows. A draw shorter than 60 characters is tested on what it has.
2. All 32 draws of a problem are generated in one batch. Each draw has its fixed seed, so the first passing draw is the one a
   draw-by-draw loop would find. "Draws used" is the index of the first passing draw (32 when none passes).
3. A draw that emits the stop token inside its 24 tokens is a whole answer; it is scored as it is, not continued.
4. A continuation is the prompt ids plus the draw's own token ids (no retokenized text), `max_tokens` = 16,384 minus the
   draw's length, with the draw's seed. The answer text is the decoded draw plus the decoded continuation, as in the
   K-continuation jobs (`rln4_gen.record`). Its tokens per problem are draw plus continuation.
5. When main and control pick the same draw (problems where no draw self-opens), one continuation serves both arms.
6. Stored T3 and T1 rows are regraded with v3 from their text; the job does not regenerate them.

## Instrument check (run on the stored rows before any job)

- Must fire: `".\n\nOkay, so"`; must not fire: `" Okay, so"` and `"x" * 56 + "\nOkay"` (outside the first 60 characters).
  Asserted in `prep/selfopen01_t3.py` and in the job.
- On the stored T3 rows the test flags **94 of 500** (78 of them right by v3, 83 %). T3 by v3: 224; T1 by v3: 410 (both
  reproduce the stored numbers). The brief expected about 168: that is the count of the T 0.6 plain cell's self-opened
  openings (board knowledge-0b450e; on `r3/base-01/out/P_math500.jsonl`, T 0.6, this test flags 204). At T 1.0 the base
  self-opens less often. So 406 problems are regenerated, not about 332, and the never-self-open share may differ from the
  entry's 10-15 %.

## Run plan and budget

- Code: `jobs/selfopen_gen.py` (GPU), `analysis/selfopen01.py` (laptop). Generation, engine, record, loaders and grader are
  imported from `studies/rlneurons` (`run_cell`, `rln4_gen`, `n13_score`, `rln4_lib`).
- Compute (amended before the smoke job, 09:22 UTC): the AWS bridge `interp_research-iterate/infra/aws_pg/ih` (one L40S
  48 GB per job); vast.ai if it fails. The full run is split with `--shard k/K` over the regenerate list when one job
  would take more than about 60 minutes; the readout merges the shard folders. Stop rule in L40S minutes: 180. Smoke first: `--n 8 --draws 4 --max-tokens 2048`, check that `openings.jsonl`, `choices.json`, `answers.jsonl`
  and `metrics.json` are written and that continuations ran. Then the full run (406 problems, 32 draws, cap 16,384).
- Expected size: 13,000 draws of 24 tokens, then about 800 continuations (about 2.5M tokens). Stop and report if the total
  would pass 90 GPU minutes.
- Outputs: `results/experiments/selfopen-01/` (`run.json`, `metrics.json`, `per_problem.json`, `examples.json`). Raw
  generations stay in `runs/<job-id>/` (not committed), location in the study README.
