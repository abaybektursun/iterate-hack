# Direct test loopshare-01: round-14/s3 rival pair a / b (shared test)

Board work item: work-1b9f99. Plan: `studies/theory/results/wide/round-14/jobs/rivals-s3.json`, field `test`.
Surprise: the autobench final configuration (plain prompt, T 0.6, 12 votes, cap 4,096) scores 139 of 328 on hard328
(result-6e7b64). Earlier tests on the same surprise: karpcap-01 (holds, proxy) and karpagree-01 (refuted).

## Claim

Among the base model's T 0.6 hard328 answers that run past 4,096 generated tokens (the answers a 4,096 cap would cut),
the share that are rule-A repetition loops.

- Rival a (budget-bound): the cut answers are mostly live derivations; loop share in [0.05, 0.40].
- Rival b (loops at T 0.6): the cut answers are mostly loops that never finish; loop share in [0.45, 1.0].
- Null (the no-loop regime the readers assumed, cued base at T 1.0): [0.0, 0.03].

## Statistic

S = (rule-A loops among kept answers) / (kept answers), kept = answers with generated tokens `n_new` > 4,096.
Unit: one answer (one per problem). 90 % percentile bootstrap interval, 10,000 resamples of the kept answers with
replacement, `numpy.random.default_rng(0)`.

## Changes from the plan (written before computing)

1. **Cell.** The plan names `studies/cleanneurons/results/gen/hard328_base_t06-01` (base, cue, T 0.6 / top-p 1.0, seed
   3,000,000). Only its `metrics.json` and `run.json` are committed; its rows are only in sameraslan's Modal Volume
   (`iterate-runs:sameraslan-1114-220554-2e30/answers.jsonl`). It cannot be read here.
   The plan also says "cued base" while the coordinator's statistic line, rival b's statement and the autobench
   configuration all say plain prompt. The stored T 0.6 hard328 cells with text are the RLN-3 base cells
   (seed 3,000,000 + index, T 0.6 / top-p 0.95, cap 16,384), in the team's S3 bucket and copied to `runs/s3/`:
   - **Primary (decides the verdict): plain base**, `s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/P_hard.jsonl`
     (posted 107 right, 137 cap hits, 98 rule-A loops of 328; result-099916). Same prompt as the autobench
     configuration and the same top-p 0.95 as the plan's own GPU cell.
   - **Secondary (reported, no verdict weight): cued base**, `.../r3/base-01/out/F_hard.jsonl` (posted 119, 173, 132).
     Closest stored cell to the plan's cue cell (top-p 0.95 instead of 1.0).
   - For the plan's named cell, the committed counts give only bounds (94 loops, 156 cap hits), reported as bounds.
2. **Loop state.** The plan reads the state from `page_grid.json`; that file holds no hard328 cell (only four MATH-500
   cells). Loop = rule A recomputed on the answer text with `studies/rlneurons/lib/rln4_lib.onset_lines`, the same
   function that produced the posted loop counts (`studies/rlneurons/analysis/day1_hard328.py`).
3. **Problem set.** hard328 = the 328 problems flagged `none` in `studies/rlneurons/results/rln3/rln3_overlap.json`
   (the RLN-3 files hold 400 hard problems), as in `day1_hard328.py`; one row per problem (asserted).
4. **n.** The plan's n 210 is an estimate; n is whatever count passes `n_new > 4,096` in the primary cell.
5. **Null.** Cued base T 1.0 / top-p 1.0 hard328, job abaybektursun-1114-151534-e72c (posted 164 right, 77 cap hits,
   1 loop), rows from `runs/abaybektursun-1114-151534-e72c/answers.jsonl` (local copy of the job output).

## Instrument checks (before the readout; stop if any fails)

1. `rln4_lib.selfcheck()` passes (rule A fires on a constructed loop and not on a non-loop).
2. Recomputed right v3, cap hits and rule-A loops on the 328 problems equal the posted counts: plain T 0.6 107 / 137 / 98,
   cued T 0.6 119 / 173 / 132, cued T 1.0 164 / 77 / 1.

## Verdict rule (engine 14, rival pair shared test, primary cell only)

- Interval wholly inside [0.05, 0.40] and n >= 50: a holds, b refuted.
- Interval wholly inside [0.45, 1.0] and n >= 50: b holds, a refuted.
- Interval wholly outside both ranges (inside neither, e.g. wholly below 0.05 or wholly in (0.40, 0.45)): both refuted.
- Interval straddling a range boundary: undecided for the rival(s) whose range it touches; a rival whose range it does
  not touch at all is refuted. If n < 50: both undecided, with the n that would decide.

## Files

- `studies/theory/analysis/direct_loopshare.py` (run: `uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.theory.analysis.direct_loopshare` from the worktree root).
- Output: `studies/theory/results/direct/loopshare-01/{metrics.json, examples.json, rows.json}`.
