# rlneurons: RL gain without training (RLN-3, RLN-4)

How much of the MATH-500 gain of AI2's `allenai/Olmo-3.1-7B-RL-Zero-Math` (RL step 2,800) over its base
`allenai/Olmo-3-1025-7B` the base reaches with no training: a three-token opening cue copied from the RL model's answers,
sampling temperature, continuation from an RL prefix, and restarts. Copied from `interp_research` (branch `clean-neurons`,
commit `6ec0f0f90`, 2026-11-14). The specs are the full record: `specs/SPEC3.md` (RLN-3) and `specs/SPEC4.md` (RLN-4, with
its dated deviations and the grader v3 definition).

All code runs from the repository root with the root on `PYTHONPATH` (`python -m studies.rlneurons.<folder>.<module>`).

## Layout

| Path | What it is |
|---|---|
| `specs/SPEC3.md` | RLN-3 spec: base, RL steps 100/400/2,800 and the first release; arms P (plain), F (opening cue), C (forced commit); MATH-500 and the 400-problem harder set; training-set overlap (§11). |
| `specs/SPEC4.md` | RLN-4 spec: T1 (cue, T 1.0), continuation test K, T2 (RL, T 1.0), T3 (plain base, T 1.0), G, R1; Modal deviations; grader v3. |
| `lib/n13_score.py` | Prompt template (`TEMPLATE["pair1"]` inside the model's chat template), answer extraction and grader v1 (`extract`, `grade`, rule `dollar_both`), `wilson`, `paired_bootstrap`, `selfcheck`. |
| `lib/rln4_lib.py` | Grader v2 (`extract_v2`, `grade_v2`), grader v3 (`extract_v3`, `norm_v3`, `grade_v3`), loop-onset detectors (rule A `onset_lines`, rule B `onset_period`, `zratio`), `agree`, prefix encoding. |
| `lib/n13_gen.py` | vLLM engine settings and sampling (`SAMPLING`, `ENGINE_ENV`, `child_env`, `dump`) that the RLN jobs reuse. From the n13 study. |
| `lib/n13_setup.py` | Hugging Face tree and LFS-oid checks, engine venv build and pip-freeze pins (AWS path). From n13. |
| `lib/n13_arms.py`, `lib/n13_plan.py` | Weight hashing (`file_sha256`) and n13's seed sets and time plan, imported by `n13_gen`. From n13. |
| `lib/alwayson_edit.py` | Reference `boxed_last` and `row_sha256` that `n13_score` checks itself against. From the alwayson study. |
| `lib/hf_helpers.py` | `hf_setup`, `hf_online_setup`, `retry_transport`, copied verbatim from three large unrelated modules. |
| `jobs/rln4_gen.py` | RLN-4 generation job. Child (`--inner --phase ...`): one vLLM engine, every request with its own seed, one JSONL row per finished request. Parent: AWS `pg` setup. |
| `jobs/modal_rln4_k.py` | The Modal app that ran K, T2 and T3 (`modal run ... --step download|check|k|t2|t3`). Runs the `rln4_gen` child on an H100. |
| `jobs/run_cell.py` | One cell (model, prompt arm, problem set, temperature, top-p, seed) through the team runner `tools/gpu.py`. Reuses `rln4_gen`'s engine and row record, adds grader v3, reads `data/`. See "Day-1 cells on the team runner". |
| `jobs/setup_vllm.sh` | Installs vLLM 0.32.0, math-verify 0.9.0, transformers 5.19.0, tokenizers 0.23.3 into the venv `/opt/rln-vllm` at job start. |
| `jobs/rln3_gen.py` | RLN-3 generation job (arms P, F, C on MATH-500 and the harder set), AWS `pg` only. |
| `jobs/aws_pg_steps/*.json` | The two `pg` pipeline step files that ran RLN-3 s0400 and s0100 on one instance. Record only. |
| `prep/rln3_prep.py`, `prep/rln4_prep.py` | Build the frozen inputs in `data/` from n13's banks, the raw benchmark parquet files and the Dolci training prompts (laptop, no model). |
| `prep/rln3_offline.py`, `prep/rln4_offline.py` | Offline gates: run the jobs' child end to end with a stand-in engine that serves saved texts. |
| `analysis/rln3_analyze.py` | RLN-3 readout and verdict (SPEC3 §6-§8). |
| `analysis/rln3_overlap.py` | Training-set overlap: each test problem against the 13,314 Dolci-RL-Zero-Math-7B prompts (exact, or at least half of its word 8-grams). |
| `analysis/rln4_analyze.py` | RLN-4 readout (SPEC4 §7): T1 and K labels, cap hits, rule-A loops, Wilson and bootstrap intervals, examples. |
| `analysis/day1_rows.py` | Day-1 readout from `run_cell` outputs: one run folder per job (`run.json`, `metrics.json`, `examples.json`) and `results/day1/readout.json` (Wilson intervals, paired bootstrap, cap hits, loops, tokens per problem). |
| `analysis/rln4_temp.py` | T2/T3 readout: temperature differences, accuracy and cap hits by RL-solution-length quartile, examples. |
| `analysis/rln4_t1_t2_items.py` | Per-problem T1 against T2 under grader v3; wrote `results/rln4/t1_t2_items-01/` (from commit `8b6a836`, unchanged). |
| `specs/SPEC5_map.md` | RLN-5 map spec: where the RL model still disagrees with the cued base; hypothesis H and its refutation rules; controls. |
| `jobs/rln5_map.py` | RLN-5 map job (inference only, team runner): both models over the stored T1 and T2 answers with teacher forcing; per-position shards and `checks.json` in `$OUT_DIR`. See "RLN-5 map". |
| `analysis/rln5_map_analyze.py` | RLN-5 map readout: reads `runs/<job-id>/`, writes `metrics.json` and `examples.json` (analysis a-e of SPEC5_map.md §6, the test of H). |
| `specs/SPEC_day1_length_rules.md` | Day-1 length rules spec: double-check short answers D(S), stop at a length cutoff and restart R(L), their combination; token accounting; the choice on MATH-500 and its fixed use on the 328; hypotheses. |
| `analysis/day1_length_rules.py`, `analysis/day1_length_rules_test.py` | Offline readout of the length rules from the rows of two `run_cell --samples 4` runs (base, RL), and its planted cases. Imports `day1_vote` (`chains`, `vote`, `row`, `tail`). See "Day-1 length rules". |
| `analysis/day1_hard328.py` | Day-1 #1 readout: the 328 at T 1.0 (four cells) beside the three T 0.6 cells, grader v3, per source, paired bootstrap, identical-text counts, the 50-problem check against T1. |
| `specs/DAY1_hard328_2026-11-14.md` | Day-1 #1 plan, written before launch: prediction, check rule, seeds, cost. |
| `jobs/merge_weights.py` | Day-1 #4: writes base + a (other - base), or base + a random difference of matched per-tensor norm, as a bf16 model directory for `run_cell --model-path`; per-tensor statistics of the difference (changed entries, norms, size in bf16 ulps); `--cos-with-rl` for the Code-RL against Math-RL cosine. |
| `jobs/merge_weights_test.py` | Planted cases for the merge: endpoints exact (with an entry where b + (o - b) is not exact in float32), effective a under both roundings, random-control norm, cosine, shard-layout mismatch. |
| `analysis/day1_wdiff.py` | Day-1 #4 readout: the weight-difference line, Code-RL and random control beside T1, T2, T3; paired bootstrap; predictions; hand reads (`HAND`); word-salad tail flag. |
| `specs/DAY1_wdiff_2026-11-14.md` | Day-1 #4 plan, written before launch: cells, seeds, rounding rule, predictions with refuters, check rule, cost. |
| `grader/rln4_grader_v3.py` | Rescores every saved MATH-500 cell with v1, v2, v3; writes `results/rln4/grader_v3/readout.json`. `CELLS` lists the S3 key of each cell. |
| `grader/rln4_grader_v3_test.py`, `grader/cases.json` | Grader v3 tests: 22 audited rows plus planted equal and unequal pairs. |
| `data/rln3/` | `math500.json` (500), `hard.json` (400 harder problems), `frozen.json` (models, revisions, seeds, caps, sha256 of the inputs). |
| `data/rln4/` | `frozen4.json` (models, revisions, cue ids, cells, seeds, cap, loop detector, stop times), `k.json` (78 K prefixes, 2.8 MB), `g.json`, `check.json`, `check_rl.json`, `math500.json`, `prompt_ids.json` (n13's tokenized MATH-500 prompts; also the RLN-3 input of that name). |
| `data/rln5/` | `map_inputs.json`: sha256 and size of the stored T1 and T2 answers that the map job reads from the Volume `iterate-runs` (`inputs/rln5/`). |
| `results/rln4/t1_t2_items-01/` | `per_problem.json` (500 rows: right and wrong for T1 and T2 under grader v3, token counts, cap hits, hand label `failure_type`), `metrics.json`, `notes.md`, `run.json`. |
| `results/rln5/map-01/` | RLN-5 map, full run: `run.json`, `metrics.json` (analysis a-e), `examples.json` (real items), `checks.json` (the job's controls), `tokenize_check.json`. |
| `results/rln3/` | `rln3_overlap.json` (per-problem overlap flags), `offline/` (prep checks and offline gate). |
| `results/day1/` | Day-1 rows from `jobs/run_cell.py`: `readout.json` and one folder per job (`check_t1_n10-01/`, `hard328_base_cue_t10-01/`, `hard328_rl_plain_t10-01/`, `math500_base_cue_t06_p10-01/`). |
| `results/rln4/` | `grader_v3/readout.json` (the final table), `modal_k-01/`, `modal_t2-01/`, `modal_t3-01/` (readouts, metrics, run records), `t1_t2_items-01/` (per-problem T1 against T2, hand labels of the base failures), `offline/`. |
| `results/day1_wdiff/` | `readout.json` (cells, differences, predictions, check), `merge_stats.json` (RL and Code-RL differences from the base by tensor group and layer; Code against RL cosine) and per cell `<arm>-01/` (`run.json`, `metrics.json`, `merge.json`, `examples.json`). |
| `results/day1_hard328/` | `readout.json` (seven-cell table, per source, differences, check) and per T 1.0 cell `<arm>-01/` (`run.json`, `metrics.json` from the job, `examples.json`: one right, one wrong). |

Old paths: `infra/pg/*.py` and `infra/aws_pg/jobs/n13_*.py` are in `lib/`; `infra/aws_pg/jobs/rln*_gen.py` and
`infra/modal_rln4_k.py` are in `jobs/`; `studies/rlneurons/rln{3,4}/inputs/` is `data/rln{3,4}/`; `rln{3,4}/offline/`,
`rln4/modal_*` and `rln4/grader_v3/readout.json` are under `results/`. The specs still name the old paths.

## Definitions

- Models (`data/rln4/frozen4.json`): base `allenai/Olmo-3-1025-7B` at `a81bae42db3975be1671e27b9c9a56da1a9f980f`; RL
  `allenai/Olmo-3.1-7B-RL-Zero-Math` at `364820b002fc8e81d11a81c7fc9dd6b49c83cd05`; both use the RL model's tokenizer.
- Prompt: `lib/n13_score.TEMPLATE["pair1"]` rendered with the chat template (`render_ids`). Cap 16,384 generated tokens.
- Opening cue ("opener", arm F): the token ids `[1584, 2268, 33413]`, text `' line!\n\nOkay'` (`frozen4.json` `prefill_ids`,
  `prefill_text`), placed after the prompt as the start of the answer.
- Harder set: `data/rln3/hard.json`, 400 problems (AIME 2022-2025, AMC 23, HMMT Feb 2025, OlympiadBench), `index` 0-399. 72 are
  in the RL training prompts (43 exact, 29 near); the 328 clean ones have flag `none`:

  ```python
  import json
  flags = json.load(open("studies/rlneurons/results/rln3/rln3_overlap.json"))["sets"]["hard"]["flags"]
  clean = [int(i) for i, f in flags.items() if f["flag"] == "none"]       # 328 indices into hard.json
  ```
- Graders: v1 `n13_score.grade(gold, n13_score.extract(text)[0])`; v2 `rln4_lib.grade_v2(gold, text)`; v3
  `rln4_lib.grade_v3(gold, text)` (SPEC4 "Grader v3"). The table below uses v3.
- Loops: rule A (`rln4_lib.onset_lines`, window 8,000 characters, compression ratio below 0.10). A cap hit is an answer that
  reached 16,384 tokens without the stop token.

## Established numbers (MATH-500, n = 500, one sample per problem, grader v3)

All from `results/rln4/grader_v3/readout.json` (`cells`, `differences_v3`; paired bootstrap, 5,000 resamples, 95 %
percentile interval, in points).

| Cell | Right of 500 | Cap hits | Right with v1 | Raw answers (`s3://pg-lineage-769063704696/results/`) |
|---|---|---|---|---|
| base, plain, T 0.6 / top-p 0.95 (RLN-3 base-01) | 319 | 65 | 302 | `rlneurons/r3/base-01/out/P_math500.jsonl` |
| base, plain, T 0.6 (n13 run) | 305 | 69 | 286 | `next_n13/s3gate-03/out/base/base/math500/generations.jsonl` |
| base, cue, T 0.6 / top-p 0.95 | 354 | 119 | 340 | `rlneurons/r3/base-01/out/F_math500.jsonl` |
| base, cue, T 1.0 / top-p 1.0 (T1) | 410 | 27 | 389 | `rlneurons/r4/base_rl-02/out/T1.jsonl` |
| base, plain, T 1.0 / top-p 1.0 (T3) | 224 | 8 | 196 | `rlneurons/r4/modal_t3-01/t3/T3.jsonl` |
| RL, plain, T 0.6 (n13 run) | 464 | 16 | 460 | `next_n13/s3gate-03/out/rl/rl/math500/generations.jsonl` |
| RL, plain, T 1.0 / top-p 1.0 (T2) | 463 | 6 | 458 | `rlneurons/r4/modal_t2-01/t2/T2.jsonl` |
| base, cue, T 0.6, restart up to 2 times on a cap hit | 414 | | | `rlneurons/r4/modal_k-01/k_b/K_fresh*.jsonl` |

| Difference | Points | 95 % interval |
|---|---|---|
| RL T 1.0 minus base with cue T 1.0 | 10.6 | [7.4, 13.8] |
| RL T 0.6 minus base with cue T 0.6 | 22.0 | [18.4, 25.8] |
| base with cue, T 1.0 minus T 0.6 | 11.2 | [7.2, 15.2] |
| RL, T 1.0 minus T 0.6 | -0.2 | [-1.8, 1.4] |
| base plain, T 1.0 minus T 0.6 | -19.0 | [-24.8, -13.4] |
| restart row minus RL T 0.6 | -10.0 | [-13.2, -7.0] |

## Day-1 rows (`jobs/run_cell.py` on the team runner, one sample per problem, grader v3)

All from `results/day1/readout.json` (written by `analysis/day1_rows.py`; Wilson 95 % interval in percent; paired bootstrap,
5,000 resamples, seed 0). Each run folder holds `run.json` (commit, command, job id), `metrics.json` and `examples.json` (one
problem scored right, one scored wrong, one cap hit, with the real prompt and answer). Raw answers are not committed: they are
`answers.jsonl` in the job's `$OUT_DIR` in abaybektursun's Modal workspace (`uv run tools/gpu.py get <job-id>` copies it to
`runs/<job-id>/`).

| Row | Right | Percent [95 %] | Cap hits | Rule-A loops | Right with v1 | Tokens per problem | Tokens/s | Run folder, job id |
|---|---|---|---|---|---|---|---|---|
| base, cue, harder 328, T 1.0 / top-p 1.0 | 164 of 328 | 50.0 [44.6, 55.4] | 77 | 1 | 163 | 9,345 | 1,007 | `results/day1/hard328_base_cue_t10-01/`, `abaybektursun-1114-151534-e72c` |
| RL, plain, harder 328, T 1.0 / top-p 1.0 | 206 of 328 | 62.8 [57.5, 67.9] | 20 | 0 | 206 | 9,316 | 1,050 | `results/day1/hard328_rl_plain_t10-01/`, `abaybektursun-1114-151540-86ef` |
| base, cue, MATH-500, T 0.6 / top-p 1.0 | 378 of 500 | 75.6 [71.6, 79.2] | 98 | 71 | 367 | 4,690 | 1,048 | `results/day1/math500_base_cue_t06_p10-01/`, `abaybektursun-1114-151718-d4fa` |
| check: base, cue, MATH-500 first 10, T 1.0 / top-p 1.0 | 8 of 10 | | 1 | 0 | 6 | 3,012 | 242 | `results/day1/check_t1_n10-01/`, `abaybektursun-1114-151028-ec3c` |

- Harder 328, RL minus base with cue at T 1.0: 12.8 points, paired 95 % interval [8.5, 17.1] (RL only 49, base only 7, both 157,
  neither 115). On MATH-500 at the same setting the difference is 10.6 [7.4, 13.8]. Both models generate the same number of
  tokens per problem (9,316 and 9,345). Three of the base's 77 cap hits are scored right (a boxed answer before the cap); none
  of RL's 20.
- MATH-500, base with cue at T 0.6: top-p 1.0 gives 378, against 354 at top-p 0.95 (same seeds) and 410 at T 1.0 / top-p 1.0.
  Differences: +4.8 points for top-p alone, unpaired 95 % interval [-0.7, 10.3]; -6.4 points against T 1.0, unpaired
  [-11.5, -1.3]. Unpaired because the per-problem scores of the 354 and 410 rows are not in the repository (only their totals,
  in `results/rln4/grader_v3/readout.json`); a paired interval needs their raw answers from S3. Cap hits go 119, 98, 27 and
  the T 0.6 / top-p 1.0 row still loops (71 rule-A loops, 70 of them among the 98 cap hits).
- Check run, read by hand: all 10 answers start from the cue and are worked solutions. The two answers that v3 scores right
  and v1 wrong are right (`**Answer: 42**` inside the last line; `3√13` with the Unicode root sign). The cap hit has 16,384
  generated tokens, finish reason `length`, no loop. T1's full row has 410 of 500 and 27 cap hits.
- The RL model writes the cue itself: its plain-prompt answers begin with `' line!\n\nOkay'`.

### Harder 328: four cells at T 1.0 beside the three at T 0.6 (Day-1 #1, board work-a50d39)

All from `results/day1_hard328/readout.json` (`analysis/day1_hard328.py`, plan `specs/DAY1_hard328_2026-11-14.md`; grader v3;
paired bootstrap, 5,000 resamples, seed 0, 95 % percentile interval, in points). T 0.6 rows are RLN-3's, rescored here with v3
from S3 (`readout.json` `cells.*.answers`); all three reproduce the expected counts.

| Cell (328 problems) | Right (v3) | Cap hits | Rule-A loops | Tokens per problem | Seed base | Job id, run folder |
|---|---|---|---|---|---|---|
| base, plain, T 1.0 / top-p 1.0 | 76 | 35 | 3 | 4,928 | 50,000,000 | `abaybektursun-1114-132922-7ba0`, `results/day1_hard328/base_plain_T1-01/` |
| base, cue, T 1.0 / top-p 1.0 | 164 | 77 | 1 | 9,344 | 3,000,000 | `abaybektursun-1114-151534-e72c`, `results/day1/hard328_base_cue_t10-01/` |
| RL, plain, T 1.0 / top-p 1.0 | 206 | 20 | 0 | 9,315 | 3,000,000 | `abaybektursun-1114-151540-86ef`, `results/day1/hard328_rl_plain_t10-01/` |
| RL, cue, T 1.0 / top-p 1.0 | 205 | 25 | 0 | 9,316 | 50,000,000 | `abaybektursun-1114-132929-a32d`, `results/day1_hard328/rl_cue_T1-01/` |
| base, plain, T 0.6 / top-p 0.95 (RLN-3) | 107 | 137 | 98 | 8,424 | 3,000,000 | `rlneurons/r3/base-01/out/P_hard.jsonl` |
| base, cue, T 0.6 / top-p 0.95 (RLN-3) | 119 | 173 | 132 | 10,211 | 3,000,000 | `rlneurons/r3/base-01/out/F_hard.jsonl` |
| RL, plain, T 0.6 / top-p 0.95 (RLN-3) | 204 | 64 | 26 | 9,377 | 3,000,000 | `rlneurons/r3/s2800-01/out/P_hard.jsonl` |

| Difference (paired, 328) | Points | 95 % interval |
|---|---|---|
| RL plain T 1.0 minus base cue T 1.0 | 12.8 | [8.5, 17.1] |
| RL cue T 1.0 minus base cue T 1.0 | 12.5 | [8.2, 16.8] |
| base cue, T 1.0 minus T 0.6 | 13.7 | [8.8, 18.9] |

Right per source (`readout.json` `per_source_right_v3`):

| Source (n) | base plain T 1.0 | base cue T 1.0 | RL plain T 1.0 | RL cue T 1.0 |
|---|---|---|---|---|
| OlympiadBench (202) | 55 | 114 | 137 | 140 |
| AIME 2024 (29) | 1 | 10 | 16 | 15 |
| AIME 2025 (30) | 5 | 7 | 12 | 11 |
| HMMT Feb 2025 (30) | 3 | 5 | 11 | 8 |
| AMC 23 (28) | 9 | 22 | 23 | 25 |
| AIME 2022 (6) | 3 | 5 | 5 | 4 |
| AIME 2023 (3) | 0 | 1 | 2 | 2 |

- Prediction (spec): partly held. The base with cue gains 13.7 points over T 0.6 ([8.8, 18.9], above the 8-point bar) and its
  cap hits fall from 173 to 77, but 77 is not under 60. Not refuted (77 is under 120 and the interval excludes 0).
- The gap at T 1.0 is the same size as on MATH-500 (10.6 [7.4, 13.8]): about 13 points on the 328. The cue does nothing for RL
  (205 against 206), which already writes it. RL is flat in temperature here too (206 at T 1.0, 204 at T 0.6).
- At T 1.0 the base's cap hits are long reasoning that does not repeat (rule-A loops 1 of 77); at T 0.6, 132 of its 173 cap hits
  are loops. The base without the cue is worse at T 1.0 than at T 0.6 (76 against 107), as on MATH-500.
- Reproduction check (spec rule, fixed before the run): T1's cell on its seeds, MATH-500 first 50, job
  `abaybektursun-1114-132917-7f81` (`results/day1_hard328/check_t1_n50-01/`): 43 right, 2 cap hits, against T1's 40 and 4 on
  the same 50. Passed (rule: within 6 and within 4). Same seeds on another GPU: 7 of 50 texts identical, 45 of 50 share the
  first 200 characters.
- Same-seed cells: no two of the seven cells share an identical text for any problem (`identical_texts`, all 21 pairs 0).
  Cells that share seed base 3,000,000 at different temperatures share the first 100 characters often (base cue 106 of 328,
  RL plain 123 of 328; `same_first_100_chars`), so their paired difference is computed on correlated samples.
- Hand read, per T 1.0 cell: the first 20 finished answers (by problem index) that v3 scores wrong. Base plain 0 of 20, base
  cue 0 of 20, RL plain 0 of 20, RL cue 0 of 20 are in fact right; the corrected counts equal the v3 counts. One base-plain
  answer ends `Therefore ANSWER is 265.` (gold 154) with no marker v3 reads; it is wrong either way.
- Raw answers: `runs/<job-id>/answers.jsonl` after `uv run tools/gpu.py get <job-id>` (abaybektursun's Modal workspace); the
  T 0.6 files and T1 are read from `runs/s3/<key>` after `aws s3 cp s3://pg-lineage-769063704696/results/rlneurons/<key>`.
  Run: `uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_hard328`.
- Cost at 3.95 USD per H100-hour (start to end record of each job): check 5.0 min 0.33 USD, base plain 25.4 min 1.67 USD, RL
  cue 51.3 min 3.38 USD, base cue 51.8 min 3.41 USD, RL plain 51.6 min 3.40 USD.

Continuation test K (`results/rln4/modal_k-01/readout.json`, 78 of the 86 problems where the base with cue hit the cap at
T 0.6 and RL was right, SPEC4 §2; grader v1): from the RL model's prefix the base finishes 48 of 78; from its own prefix 23 of 78; fresh restart 38
of 78. Frozen label: "the base can finish from a sound prefix" (both counts at the threshold edge, 47 and 23).

Grader v1 to v3 moved 113 answers from wrong to right and 1 from right to wrong over the 9 cells (`flips_v1_to_v3`,
`flip_review`). The v1 numbers 57.2 (base) and 92.0 (RL) quoted in older notes are the n13 cells under v1 (286 and 460).

## Weight-difference line: base + a (RL - base), Code-RL and a random control (Day-1 #4, board work-d36669)

All from `results/day1_wdiff/readout.json` (`analysis/day1_wdiff.py`, plan `specs/DAY1_wdiff_2026-11-14.md`). MATH-500, T 1.0 /
top-p 1.0, one sample per problem, cap 16,384, grader v3, RL tokenizer for every cell. theta(a) = base + a (RL - base), written by
`jobs/merge_weights.py` on the GPU box and loaded with `run_cell --model-path`. Code-RL is `allenai/Olmo-3.1-7B-RL-Zero-Code` at
`1ca3bb30f0e51b7ef05f7d0fefcf0e6b14eefc90` (model card: base `allenai/Olmo-3-1025-7B`; same 355 tensors and shard layout; the 3.1
release, matching the Math model). Random control: base + R, R per tensor Gaussian (seed 0) rescaled to that tensor's
||RL - base||. Paired bootstrap, 5,000 resamples, seed 0, 95 % percentile interval, in points.

| Cell | a | Right of 500 (v3) | Hand-read right of 20 | Cap hits | Rule-A loops | Word-salad tails | Mean tokens | Seed base | Job id, run folder |
|---|---|---|---|---|---|---|---|---|---|
| T3_base_plain | 0 | 224 |  | 8 | 0 | 3 | 2,107 | 47,000,000 | `r4/modal_t3-01/t3/T3.jsonl` (S3) |
| theta0.25_plain | 0.25 | 405 | 1 | 19 | 0 | 0 | 3,653 | 64,000,000 | `abaybektursun-1114-163704-ffca`, `day1_wdiff/theta0.25_plain-01/` |
| theta0.5_plain | 0.5 | 443 | 0 | 21 | 0 | 2 | 4,536 | 65,000,000 | `abaybektursun-1114-163658-8118`, `day1_wdiff/theta0.5_plain-01/` |
| T2_rl_plain | 1 | 463 |  | 6 | 0 | 2 | 4,693 | 45,000,000 | `r4/modal_t2-01/t2/T2.jsonl` (S3) |
| T1_base_cue | 0 | 410 |  | 27 | 0 | 0 | 3,932 | 41,000,000 | `r4/base_rl-02/out/T1.jsonl` (S3) |
| theta0.25_cue | 0.25 | 441 | 2 | 13 | 1 | 2 | 4,036 | 60,000,000 | `abaybektursun-1114-153102-b029`, `day1_wdiff/theta0.25_cue-01/` |
| theta0.5_cue | 0.5 | 452 | 0 | 22 | 0 | 1 | 4,626 | 61,000,000 | `abaybektursun-1114-152855-683b`, `day1_wdiff/theta0.5_cue-01/` |
| theta0.75_cue | 0.75 | 451 | 1 | 12 | 1 | 2 | 4,654 | 62,000,000 | `abaybektursun-1114-153106-af79`, `day1_wdiff/theta0.75_cue-01/` |
| rl_cue | 1 | 457 | 0 | 8 | 0 | 0 | 4,696 | 66,000,000 | `abaybektursun-1114-153110-e985`, `day1_wdiff/rl_cue-01/` |
| theta1.25_cue | 1.25 | 450 | 1 | 2 | 0 | 14 | 4,852 | 70,000,000 | `abaybektursun-1114-163851-0cec`, `day1_wdiff/theta1.25_cue-01/` |
| theta1.5_cue | 1.5 | 453 | 0 | 4 | 0 | 34 | 4,862 | 63,000,000 | `abaybektursun-1114-153057-45e7`, `day1_wdiff/theta1.5_cue-01/` |
| random_cue |  | 417 | 3 | 23 | 0 | 0 | 3,944 | 69,000,000 | `abaybektursun-1114-153047-6429`, `day1_wdiff/random_cue-01/` |
| code_plain |  | 390 | 2 | 4 | 0 | 0 | 3,066 | 67,000,000 | `abaybektursun-1114-153052-5013`, `day1_wdiff/code_plain-01/` |
| code_cue |  | 450 | 2 | 7 | 0 | 1 | 3,336 | 68,000,000 | `abaybektursun-1114-162452-0203`, `day1_wdiff/code_cue-01/` |

"Hand-read right of 20": of 20 finished answers that v3 scored wrong (drawn with numpy seed 0), how many are in fact right
(`readout.json` `cells.<arm>.hand_read_right_of_20` lists each with what the model wrote). All are grader gaps already known for v3:
prose answers without a marker, two boxes, a trailing period or unit, "$Answer" placeholder text. T1, T2 and T3 were not hand read
the same way, so comparisons use the v3 counts. Word-salad tails: a crude flag (`day1_wdiff.word_salad`, function-word pairs or CJK
characters in the last 3,000 characters), descriptive only.

| Difference (paired, 500) | Points | 95 % interval |
|---|---|---|
| theta0.25_cue minus T1_base_cue | 6.2 | [3.0, 9.6] |
| theta0.25_cue minus T2_rl_plain | -4.4 | [-7.0, -1.8] |
| theta0.5_cue minus T1_base_cue | 8.4 | [5.4, 11.6] |
| theta0.5_cue minus T2_rl_plain | -2.2 | [-4.6, 0.2] |
| theta0.75_cue minus T1_base_cue | 8.2 | [5.2, 11.2] |
| theta0.75_cue minus T2_rl_plain | -2.4 | [-4.6, -0.4] |
| theta1.25_cue minus T1_base_cue | 8.0 | [5.0, 11.0] |
| theta1.25_cue minus T2_rl_plain | -2.6 | [-5.0, -0.2] |
| theta1.5_cue minus T1_base_cue | 8.6 | [5.6, 11.8] |
| theta1.5_cue minus T2_rl_plain | -2.0 | [-4.2, 0.2] |
| theta0.5_cue minus theta0.25_cue | 2.2 | [-0.2, 4.6] |
| theta0.75_cue minus theta0.5_cue | -0.2 | [-2.8, 2.4] |
| rl_cue minus theta0.75_cue | 1.2 | [-1.2, 3.6] |
| theta1.25_cue minus rl_cue | -1.4 | [-4.0, 1.0] |
| theta1.5_cue minus theta1.25_cue | 0.6 | [-1.8, 3.0] |
| random_cue minus T1_base_cue | 1.4 | [-2.0, 4.8] |
| code_plain minus T2_rl_plain | -14.6 | [-18.01, -11.0] |
| code_plain minus T1_base_cue | -4.0 | [-8.2, 0.2] |
| code_plain minus T3_base_plain | 33.2 | [27.4, 38.6] |
| code_cue minus T1_base_cue | 8.0 | [4.6, 11.2] |
| rl_cue minus T2_rl_plain | -1.2 | [-3.6, 1.2] |
| theta0.25_plain minus T3_base_plain | 36.2 | [30.8, 41.4] |
| theta0.5_plain minus T3_base_plain | 43.8 | [38.8, 48.6] |
| code_cue minus rl_cue | -1.4 | [-4.0, 1.0] |
| code_cue minus code_plain | 12.0 | [8.2, 15.8] |
| theta0.5_plain minus T2_rl_plain | -4.0 | [-6.6, -1.4] |

- The gain needs an RL difference, and a small one. a = 0.25 with the cue already gives 441 (+6.2 over T1, [3.0, 9.6]); from
  a = 0.5 on the cue row is flat at 450 to 457 (adjacent steps all inside [-2.8, 4.6]) and stays 2 to 2.6 points under RL plain.
  Extrapolation does not help: a = 1.5 gives 453 (-2.0 against RL plain, [-4.2, 0.2]) and breaks the text: 34 of 500 answers end
  in word salad (14 at a = 1.25, at most 3 in every other cell), 12 of them still scored right. Two theta(1.5) tails:
  problem 9 "...it is it this with which I must chnang e nusrsed got able this it takes I ruined so I which6 value..." and
  problem 22 "ther answer 后 ... ,那 4， from that Buster后,正确...".
- Without the cue, a = 0.25 takes the plain prompt from 224 (T3) to 405 (+36.2, [30.8, 41.4]) and a = 0.5 to 443; only 1 and 91
  of their answers start with the cue text the RL model writes (RL plain: 406 of 500).
- The direction is not math-specific: Code-RL with the cue scores 450 (+8.0 over T1, [4.6, 11.2]; -1.4 against RL cue,
  [-4.0, 1.0]). Without the cue Code-RL scores 390: +33.2 over base plain, -4.0 against the cued base ([-8.2, 0.2]); it never writes
  the cue and gives 14 empty answers. The Code-RL and Math-RL differences are nearly orthogonal (cosine 0.014 over 7.3 B entries,
  0.002 to 0.037 per tensor group; `merge_stats.json` `code_vs_rl`): they change the same entries 1.64 times more often than
  independent changes would (2.03 B shared, 1.24 B expected) but agree in sign on only 50.8 % of them.
- A random difference of the same per-tensor norm does nothing: 417 against T1's 410 (+1.4, [-2.0, 4.8]). Its norm after
  rounding is 1.018 times ||RL - base|| and its cosine with RL - base is 0.0002 (`random_cue-01/merge.json`). Two of its tails:
  problem 287 "testify,Sexisting basis will More Daily Scanner Thesias-oriented) invisible me..." and problem 100, which drifts
  to "What is the sum of 1-40? ... So the answer is 820." (gold 145 degrees).
- Predictions (spec): P1 held (monotone to RL cue: steps +6.2, +2.2, -0.2, +1.2, no interval entirely below 0); P2 held (452 >= 437);
  P3 held (a = 1.5 is not above RL plain); P4 held (random +1.4, interval includes 0); P5 refuted (Code-RL plain 390 < 437; Code-RL
  with the cue is 450); P6 held (a = 0.5 plain 443 >= 400).
- What RL changed (`merge_stats.json`, job `abaybektursun-1114-152416-de10`): 43.2 % of the 7.30 B entries, relative norm
  ||RL - base|| / ||base|| = 0.13 % overall; 0.22 to 0.27 % in every attention and MLP matrix (k_proj 59.7 % of entries changed,
  q_proj 57.5 %, o_proj 46.7 %, v_proj 46.2 %, MLP 43.5 to 44.2 %), 0.16 % in lm_head (29.0 % changed), 0.01 % in the embedding
  (3.8 % changed), almost nothing in the norm weights (0.2 to 3.2 % changed, final norm 0); flat over layers (0.22 to 0.25 %, first
  and last layers highest). Of the changed entries 53.6 % moved by at most one bf16 unit in the last place of the base value, 16.9 %
  by more than 1 and up to 2, 5.1 % by more than 16. Code-RL: 39.2 % of entries, relative norm 0.11 %, the same pattern by group.
- Rounding. Because most changes are one bf16 ulp, rounding base + a (RL - base) to the nearest bf16 moves a = 0.25 to an
  effective a of 0.12 and a = 0.75 to 0.88 (`merge_stats.json` `rl.points`). The line cells use stochastic rounding (effective a
  0.250, 0.500, 0.750, 1.250, 1.500 in each `merge.json`); the cost is noise orthogonal to RL - base (||M - B|| / ||RL - B|| is 0.42
  at a = 0.25, 0.62 at a = 0.5). The rule was fixed in the spec before any cell ran.
- Checks. Merge identity: theta(1) and the Code-RL merge are bit-identical to RL and Code-RL in all 355 tensors (asserted in the
  job; the first version, b + (o - b) in float32, was not, in 79 tensors, and failed job `abaybektursun-1114-152420-32f3`).
  Reproduction (rule fixed before the run): theta(1) through the merge path, plain, T2's seeds, first 50 problems, job
  `abaybektursun-1114-152849-c7c6`: 47 right and 1 cap hit against T2's 47 and 0. Passed. No two cells share a non-empty
  completion for any problem; two empty answers (stop token first) match T3 by chance (`identical_empty_texts`).
- Not run (budget): base + 0.5 (Code-RL - base) with the cue. One sample per cell: no seed-to-seed spread; the a = 0.5 to 1.5 cue
  cells differ by at most 7 of 500.
- Cost at 3.95 USD per H100-hour (start to end record of each job, all on H100 80GB HBM3): 317.5 min, 20.9 USD in all; MATH-500
  cells 20.5 to 31.9 min (1.35 to 2.10 USD) at 1,270 to 1,500 tokens/s; the merge takes 29 to 42 s; statistics and cosine jobs
  0.30 USD; check 0.41 USD; four failed jobs 0.11 USD (`32f3`, `e931`, `c6cf`, `fa08`; the last two got no `--alpha` value from a
  zsh loop and were resubmitted).
- Raw answers: `runs/<job-id>/answers.jsonl` after `uv run tools/gpu.py get <job-id>` (abaybektursun's Modal workspace); T1, T2,
  T3 in `runs/s3/<key>` after `aws s3 cp s3://pg-lineage-769063704696/results/rlneurons/<key>`. The per-tensor rows are in
  `runs/abaybektursun-1114-152416-de10/merge_{rl,code}.json` (not committed).
  Run: `uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_wdiff`.

## Draft-critique-revision: intrinsic self-review of the T 1.0 cue answers (board work-70152d, spec specs/SPEC_critique.md)

Self-review fixes no math for either model. Each finished T 1.0 cue draft (base 473, RL 492; cap hits keep their score) is continued
after "Wait, before I finalize, let me check this solution carefully for mistakes." at T 1.0 (`jobs/revise.py`, 4 shards per
model). MATH-500, n = 500, paired 95 % intervals. Readout `results/day1_critique/readout.json` (`analysis/day1_critique.py`).

| model | draft | v3 on whole text | v3-stated (post hoc) | fixed / broken (v3-stated) | revision tokens per revised draft |
|---|---|---|---|---|---|
| base | 410 | 410, 0.0 [-1.4, 1.6] | 415, +1.0 [0.0, 2.2] | 7 / 2 | 375 |
| RL | 457 | 446, -2.2 [-3.6, -1.0] | 454, -0.6 [-1.4, 0.0] | 0 / 3 | 231 |

v3 reads "the answer is correct." as the answer "correct." (8 of RL's 11 v3 flips); v3-stated drops the "Answer is" marker form
from the revision before grading. Read by hand: 6 of base's 7 fixes are format repairs (the draft's number sat inside a sentence v3
cannot read, e.g. 135, 165, 447); one is a math fix (372, 75 -> 90). Every break on either model is a real changed answer (base 14,
156; RL 71, 193, 236). RL fixes none of its 35 wrong finished drafts. Raw rows in frustea's Modal Volume
`iterate-runs/<job>/answers.jsonl`; drafts in `iterate-runs/inputs/critique/` (`prep/critique_drafts.py`).

## RLN-5 map: where RL still disagrees once the cue is given

Spec `specs/SPEC5_map.md`; run folder `results/rln5/map-01/` (`run.json`, `metrics.json`, `examples.json`, `checks.json`,
`tokenize_check.json`). Job `sameraslan-1114-135831-c3ec` (H100, 597 s, commit `e6354d6`) ran both models with teacher forcing
over the 1,000 stored T1 and T2 answers: 4,314,803 positions after the prompt. All numbers below are keys of
`results/rln5/map-01/metrics.json`; log-probs and KL in nats. D = ln P_RL - ln P_base of the token where the base starts its
final answer.

Result: H is refuted (`c.verdict`). On the base's wrong answers of under 4,000 tokens that RL solved, RL's probability of
the answer-start token is within a factor 2 of the base's in the median (median D -0.53, n = 21 of the 23; 2 have no
extracted answer), and right base answers of at most 2,000 tokens show the same distribution (median D -0.21, n = 250;
permutation p = 0.82). Rule 3 did not fire: KL at the answer start is at the 96.5th percentile of its answer in the median
group-i answer, and at the 99.4th in the control. What separates D is the format of the base's final answer:

| Base's final answer (`c.by_format`, all finished T1 answers with an extracted answer) | n | right | median D (quartiles) | D below -ln 2 | RL top-1 is the written token | RL P(stop) below 0.5 at the base's true end |
|---|---|---|---|---|---|---|
| "Answer:" line (marker) | 132 | 121 | -8.36 (-12.03, -4.20) | 84 % | 15 % | 43.9 % (base 10.6 %) |
| `\boxed{}` | 338 | 289 | 0.000 (0.000, 0.023) | 7 % | 89 % | 5.6 % (base 1.5 %) |

At the 132 "Answer:" starts RL's top-1 token is `Final` 46, `Answer` 20, `Wait` 15, `To` 12, `**` 11, `\` 8, `But` 6,
`Alternatively` 3: mostly another answer header, and a continuation word in at least 36 (27 %). Where the base boxes a wrong answer, RL
gives the box the same probability: median D 0.001 in group i (n = 10) and 0.0001 for the 39 other wrong finished answers
(`c.groups.iii_other_wrong_finished`).

| Analysis | Number | Key |
|---|---|---|
| a. Top-1 tokens differ, share of generated positions | T1 7.98 % of 1,966,404; T2 8.20 % of 2,346,899 (per answer: median 7.8 % and 7.7 %) | `a.*.top1_differ_share_pooled` |
| a. Share of summed KL in the top 1 % / top 4 % of positions | T1, KL(base\|\|RL): 17.4 % / 38.7 %; T2, KL(RL\|\|base): 17.9 % / 36.1 % | `a.*.kl_own_share_top_*` |
| a. Mean KL per position; base entropy where top-1 differs / agrees | T1 0.064, T2 0.059; T1 1.40 / 0.38 | `a.*.mean_kl_own`, `mean_entropy_base_where_*` |
| b. KL at the three cue positions | T1 (cue prefilled): 10.5, 12.0, 8.0; T2 (RL writes the opening itself, 406 answers): 7.8, 5.2, 1.3 | `b.*.opening_positions_mean_kl` |
| b. First 10 tokens after the cue, mean KL | T1: 0.008, 0.41, 0.04, 0.58, 0.02, 0.57, 0.25, 0.18, 0.21, 0.10 | `b.T1.first_10_after_opening_mean_kl` |
| b. Deciles of the answer, mean KL (mean over answers) | T1: 0.085, 0.075, 0.071, 0.068, 0.069, 0.073, 0.079, 0.081, 0.062, 0.113; T2: 0.072, 0.061, 0.059, 0.060, 0.061, 0.062, 0.066, 0.066, 0.046, 0.023 | `b.*.decile_mean_kl_mean_over_answers` |
| b. Last 50 tokens before the stop token, mean KL | T1 0.136 (by tens: 0.044, 0.039, 0.063, 0.144, 0.388; 473 answers); T2 0.020 (403 answers) | `b.*.last_50_before_stop_*` |
| c. D by group: median (quartiles), n | i: -0.53 (-6.91, 0.0001), 21; ii: -0.21 (-7.92, 0.006), 250; iii: 0.0001 (0.0000, 0.014), 39 | `c.groups.*.D` |
| c. RL's top-1 token at the answer start, group i | `(\` 5, `Final` 4, `\` 4, `**` 2, ` \` 2, `Wait` 1, `Answer` 1, `5` 1, `[` 1 | `c.groups.*.rl_top1_top10` |
| d. 16 cap-hit base answers that RL solved: the 5 largest gaps of each (80 positions) | median D -4.5 (-5.0, -4.0); relative position median 0.19 (0.06, 0.56); RL's top-1 there: ` Wait` 4, ` too` 4, ` Hmm` 3, digits and ordinary words; RL's largest P(stop) anywhere in these answers is 0.027 | `d`, `examples.json` `d_cap_hits` |
| e. T2 tokens with the largest summed KL(RL\|\|base) | ` the` 4.1 %, `,` 4.0 %, `.` 3.7 %, space 2.6 %, ` line` 2.3 %, ` is` 2.3 %, `!\n\n` 1.7 %, ` Wait` 1.2 % (30 listed) | `e.by_written_token_top30` |
| e. P(stop) at the true end of RL's answers | RL median 1.000, base median 1.000; below 0.5 in 2 of 494 for each | `e.stop_probability_at_true_end_T2` |
| e. P(stop) at the true end of the base's answers | RL below 0.5 in 16.5 % of 473, base in 4.2 % | `e.stop_probability_at_true_end_T1` |

Controls of the full job (`results/rln5/map-01/checks.json`): identity max |KL| 0 over 475 positions; P(cue) after the prompt
3.2e-07 under the base and 0.835 under RL (median of 500); mean log-prob of written tokens plus mean entropy -0.0004 (T1) and
+0.0005 (T2); median |mean log-prob minus the sampler's stored `mean_logprob`| 0.00017 (T1) and 0.00014 (T2); cached pass
against one pass, mean |difference| 0.0045. Re-tokenization (`tokenize_check.json`): 459 (T1) and 466 (T2) of 500 rows give the
stored token count, the rest differ by 1 to 5 tokens and are kept.

Not established: part d's test "RL would end after the base states the gold answer" found the gold in 3 of the 16 texts, and 2
of the 3 matches are intermediate numbers, so it supports no claim. The format split was added after reading the positions
(SPEC5_map.md §8). One sample per problem; the hand labels behind group i are one reader's.

Run it:

```
modal volume put iterate-runs <T1.jsonl> inputs/rln5/T1.jsonl      # and T2.jsonl; sha256 in data/rln5/map_inputs.json
uv run tools/gpu.py submit h100 --hours 0.6 -- "python -m studies.rlneurons.jobs.rln5_map --commit $(git rev-parse HEAD)"
uv run tools/gpu.py get <job-id>
PYTHONPATH=. uv run --no-project --with numpy --with torch --with transformers==5.22.2 --with huggingface_hub --with jinja2 python -m studies.rlneurons.analysis.rln5_map_analyze runs/<job-id> --t1 <T1.jsonl> --t2 <T2.jsonl> --out studies/rlneurons/results/rln5/map-02
```

Smoke run: add `--n 10 --mid 1 --long 1` to the job (3 minutes). Laptop dry run with stand-in models: add `--dry-run --n 3
--inputs <dir> --out <dir>`. The per-position shards (120 MB: written token, both log-probs, entropies, both KL, top-1 tokens,
ranks, stop and marker log-probs; arrays listed in the job's docstring) are in the Volume `iterate-runs` under
`sameraslan-1114-135831-c3ec/` and in `runs/sameraslan-1114-135831-c3ec/` after `gpu.py get`; not committed.

## T1 against T2, problem by problem (MATH-500, n = 500, grader v3)

Run folder `results/rln4/t1_t2_items-01/`: `per_problem.json` (one row per problem), `metrics.json`, `run.json`, `notes.md`
(the reader's full notes with quotes). The script needs the two raw answer files (T1 and T2 rows of the table above) and runs
on the laptop:

```
python3 -m studies.rlneurons.analysis.rln4_t1_t2_items <T1.jsonl> <T2.jsonl> <new out dir>
```

This is the command of the run (Python 3.11.1 with math-verify 0.9.0 and numpy installed); without them, put
`uv run --no-project --with numpy --with math-verify==0.9.0` in front, as in the laptop checks below (not run in that form).

It writes the machine columns of `per_problem.json` and `metrics.json`. Three columns of the committed `per_problem.json` are
not from the script: `failure_type` and `label_from_tail_only` are hand labels by one reader, an agent, with no second reader;
`level5` came from a file outside the repo (`run.json`).

| | RL (T2) right | RL (T2) wrong |
|---|---|---|
| base with cue (T1) right | 398 | 12 |
| base with cue (T1) wrong | 65 | 25 |

T1 410 right, 27 cap hits; T2 463 right, 6 cap hits (`metrics.json`; equal to the table above).

The 65 problems that RL solved and the base with cue did not, by hand label (`per_problem.json`, `failure_type`):

| Why the base answer is wrong | Problems of 65 |
|---|---|
| Cap hit without a loop (the reasoning does not converge) | 16 |
| Misread or mis-copied problem or diagram | 14 |
| Arithmetic or algebra slip, method right | 14 |
| Wrong method, missed case, or question not answered | 9 |
| Right answer in a final line that grader v3 rejects (5) or that is garbled (3) | 8 |
| Reached the gold answer, then changed it | 2 |
| Drift to another document, no answer | 2 |

Generated tokens (`metrics.json`): base answers of at most 2,000 tokens: 263, of which 13 wrong. RL answers of at most 4,000
tokens: 286, of which 0 wrong. Median and 90th percentile: T1 right 1,431.5 and 7,054 (n = 410), T1 wrong 10,547.5 and 16,384
(n = 90); T2 right 3,014 and 8,430 (n = 463), T2 wrong 13,455 and 16,384 (n = 37).

## How to run

Laptop checks (no GPU, no weights):

```
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.grader.rln4_grader_v3_test
uv run --no-project --with numpy --with math-verify==0.9.0 python -c "from studies.rlneurons.lib import n13_score, rln4_lib; n13_score.selfcheck(); rln4_lib.selfcheck()"
```

Rescoring and readouts need the raw answers (table above), then for example
`python -m studies.rlneurons.grader.rln4_grader_v3 --data <dir with <cell>.jsonl> --out <readout.json>`. Each script's
docstring gives its arguments.

GPU, through the study's Modal app (vLLM 0.32.0, math-verify 0.9.0, transformers 5.19.0, tokenizers 0.23.3 on an H100):

```
modal run studies/rlneurons/jobs/modal_rln4_k.py --step download
modal run studies/rlneurons/jobs/modal_rln4_k.py --step check --prefix <new prefix> --stop-utc <UTC, within 1 h 50 min>
modal run --detach studies/rlneurons/jobs/modal_rln4_k.py --step t3 --prefix <new prefix> --stop-utc <...>
```

It runs today only for someone with the owner's `rln4-aws` Modal secret (see "Needs porting"). Teammates use `jobs/run_cell.py`
below.

### Day-1 cells on the team runner

`jobs/run_cell.py` runs one cell in your own Modal workspace through `tools/gpu.py`: no S3, no secret besides `hf-token`. The
command first runs `jobs/setup_vllm.sh`, which installs the study's engine versions into the venv `/opt/rln-vllm` (24 s on a fresh H100 container and 60 s on a fresh cpu container,
measured), so the runner image and `requirements.txt` stay unchanged. Weights download once into your
`iterate-hf-cache` Volume at the revisions in `data/rln4/frozen4.json`. Problem i is sampled with seed `--seed` + i. Outputs in
`$OUT_DIR` (copy with `uv run tools/gpu.py get <job-id>`): `answers.jsonl`, one row per finished problem written as it
finishes (prompt, completion, finish reason, generated tokens, extracted answers, grades v1, v2, v3), and `metrics.json`
(right with v3 and v1, n, cap hits, mean generated tokens, tokens per second, the config, the commit, the job id). A job killed
at `--hours` keeps every finished row. Use double quotes: `$(git rev-parse HEAD)` must expand on your laptop to the commit
that `gpu.py` submits.

The GPU path is tested: the check run and the three Day-1 rows above ran through it on H100s ("Day-1 rows"). Also tested:
the laptop dry run (stand-in engine, below) and a cpu job on the runner (`abaybektursun-1114-123453-8c3d` and
`abaybektursun-1114-124132-b234`). Before trusting a new cell, run the check command below and read its rows.

Day-1 #1, the 328 harder problems at T 1.0 / top-p 1.0 (seeds 3000000 + index, the harder-set seeds of RLN-3 base-01):

```
uv run tools/gpu.py submit h100 --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set hard328 --temperature 1.0 --top-p 1.0 --seed 3000000 --commit $(git rev-parse HEAD)"
uv run tools/gpu.py submit h100 --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model rl --prompt plain --set hard328 --temperature 1.0 --top-p 1.0 --seed 3000000 --commit $(git rev-parse HEAD)"
```

Day-1 #2, base with cue at T 0.6 / top-p 1.0 on MATH-500 (seeds 1000000 + index, the seeds of the T 0.6 / top-p 0.95 cue row,
354 of 500, so the two rows differ only in top-p):

```
uv run tools/gpu.py submit h100 --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set math500 --temperature 0.6 --top-p 1.0 --seed 1000000 --commit $(git rev-parse HEAD)"
```

Check run, before any new number is trusted: T1's cell (410 of 500) on its seeds, first 10 problems. Texts will not be
identical to T1's (other GPU), so compare the score and cap hits on the 10 with T1's rows:

```
uv run tools/gpu.py submit h100 --hours 0.5 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set math500 --temperature 1.0 --top-p 1.0 --seed 41000000 --n 10 --commit $(git rev-parse HEAD)"
```

Measured time per full row on one H100 (`results/day1/*/metrics.json`): 1,007 to 1,050 generated tokens/s over the whole
row; 51 min for each 328 row (3.06 M tokens) and 39 min for the MATH-500 row (2.34 M tokens), setup and engine start included.
This is below the 1,415 tokens/s of T3 (`results/rln4/modal_t3-01/metrics.json`): the engine log shows the GPU KV cache
98 to 99 % full with 18 to 25 answers running (`max_num_seqs` is 128) and the waiting count rising at times, so vLLM
preempts answers and recomputes them. `--hours 2` leaves room; the runner kills the job at `--hours`.

Day-1 #3 (restart and four-sample vote) is not runnable yet. Four samples: four `run_cell` jobs with seeds 10000 apart (the
RLN-3 rule seed + 10000 x sample + index) work today, but no script computes the vote (`rln4_lib.agree` is the equivalence
test to use). Restart: `run_cell` has no option to run only the problems that hit the cap in an earlier run, and no script
merges a restart into its parent row.

Day-1 #4, one cell on a merged model (merge, then the cell on `/tmp/theta`; `analysis/day1_wdiff.py` `CELLS` has every command):

```
uv run tools/gpu.py submit h100 --hours 2.5 -- "bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.merge_weights --other rl --alpha 0.5 --rounding stochastic --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label theta0.5 --prompt cue --set math500 --temperature 1.0 --top-p 1.0 --seed 61000000 --commit $(git rev-parse HEAD)"
uv run --no-project --with torch --with safetensors --with numpy python -m studies.rlneurons.jobs.merge_weights_test
```

`rm -rf /tmp/theta`: Modal reuses containers, `/tmp` included. Statistics only (no weights written): `merge_weights --other rl`
or `--other code [--cos-with-rl] --stats \$OUT_DIR/<name>.json`.

Laptop dry run (no vLLM, no weights; downloads only the tokenizer files):

```
uv run --no-project --with numpy --with math-verify==0.9.0 --with transformers==5.19.0 --with tokenizers==0.23.3 --with huggingface_hub --with jinja2 python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set math500 --temperature 1.0 --top-p 1.0 --seed 41000000 --n 10 --dry-run --out /tmp/rc --commit $(git rev-parse HEAD)
```

It must print 4 right, 3 cap hits of 10 (the stand-in serves right, wrong, cap hit in turn).

### Day-1 length rules (laptop, no GPU)

`analysis/day1_length_rules.py` scores two procedures from the rows of the Day-1 #3 jobs (`run_cell --samples 4 --restarts 2`,
one run per model; `specs/SPEC_day1_3.md`), reading only attempt 0 of samples 0 to 3. D(S): a finished answer of at most S
tokens is checked against the next sample, and against a third when the two differ. R(L): an answer longer than L tokens is
stopped at L and the next sample is taken. Grid: S in {off, 1000, 2000, 4000}, L in {off, 8000, 10000, 12000}. Per model and
setting it gives right of n, the Wilson interval, generated tokens per problem and the paired difference against the single
row; with both runs also RL minus base and the base's best setting at no more tokens per problem than one RL sample. The rules,
the token accounting and the hypotheses are in `specs/SPEC_day1_length_rules.md`. No number exists yet: the Day-1 #3 rows do
not exist yet.

Test (planted rows, no network):

```
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_length_rules_test
```

MATH-500: all 16 settings, and the choice of S and L (written to `chosen.json`):

```
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_length_rules --base runs/<base math500 job> --rl runs/<rl math500 job> --out studies/rlneurons/results/day1_length_rules/math500-01 --choose
```

The 328: the chosen setting unchanged (the script refuses a `chosen.json` made on the same problem set):

```
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_length_rules --base runs/<base hard328 job> --rl runs/<rl hard328 job> --out studies/rlneurons/results/day1_length_rules/hard328-01 --fixed studies/rlneurons/results/day1_length_rules/math500-01/chosen.json
```

Each run folder `results/day1_length_rules/<set>-<nn>/` gets `run.json`, `metrics.json`, `per_problem.tsv` (per model and
problem: the four `n_new`, and per setting `right tokens samples`; `x` after a sample number = stopped at L, `*` = the sample
answered with), `examples.json` (one problem a rule fixed and one it broke) and, with `--choose`, `chosen.json`. An unfinished
run is refused.

## Raw answers

One JSONL row per answer (for RLN-4 cells: prompt index, seed, text, token counts, cap hit, loop flags, extracted answer, v1
and v2 scores) in the owner's bucket, `s3://pg-lineage-769063704696/results/rlneurons/r3/` (RLN-3: `base-01/`, `s2800-01/`, `fr-01/`,
`s0400_s0100-01/`, `inputs/`) and `.../r4/` (RLN-4: `base_rl-02/`, `modal_k-01/`, `modal_t2-01/`, `modal_t3-01/`,
`inputs/`), plus the n13 cells under `s3://pg-lineage-769063704696/results/next_n13/s3gate-03/`. Not copied here.
`results/rln4/grader_v3/readout.json` `files` gives the sha256 of each cell file used for the table.

## Needs porting

1. `jobs/modal_rln4_k.py` (K, T2, T3) still reads its inputs from and copies its outputs to
   `s3://pg-lineage-769063704696/results/rlneurons/r4/` with the owner's Modal secret `rln4-aws`. Teammates run cells with
   `jobs/run_cell.py` instead; the K continuation arms and the check phases have no port.
2. `jobs/run_cell.py` covers T1, T2, T3, the harder set and Day-1 #1 and #2 (run, see "Day-1 rows"). Day-1 #3 needs a vote
   script and a restart option.
3. `jobs/rln3_gen.py` and the parent (non-`--inner`) mode of `jobs/rln4_gen.py` need the AWS `pg` launcher and AMI (the
   `/opt/n13` vLLM venv built by `lib/n13_setup.venv_n13`, the `aws` CLI, inputs in the owner's S3). Not in this repository.
4. `lib/hf_helpers.hf_online_setup` reads `HF_TOKEN`; without it, it calls AWS SSM `/pg-lineage/hf-token` in the owner's account.
5. `prep/*` and `analysis/*` read n13's and base-01's banks, the raw benchmark parquet files and the Dolci prompts from local
   directories that came from the owner's S3 and Hugging Face. The prep scripts load the RL tokenizer.
6. `lib/n13_setup.venv_olmes` imports `n13_known` (n13's olmes reproduction), which is not copied; no rlneurons code calls it.
   `lib/n13_plan` names n13 modules that are not copied in its step-file builder; no rlneurons code calls it.
7. Frozen stop times in `data/rln4/frozen4.json` are 2026-11-14; every new run must shift them (`--stop-utc` on Modal,
   `--time-shift` on the child).

## Open

- The harder set (328) has one sample per problem per cell (seven cells, "Harder 328: four cells at T 1.0"); no second sample
  and no seed-to-seed spread on it yet.
- Temperature and top-p are separated only by totals: 354 (T 0.6 / top-p 0.95), 378 (T 0.6 / top-p 1.0), 410 (T 1.0 /
  top-p 1.0). The top-p step (+4.8 points) has an unpaired interval that includes 0; the paired intervals need the per-problem
  scores of the 354 and 410 rows (raw answers in S3). T 1.0 / top-p 0.95 is not run.
- `run_cell` generates about 1,000 tokens/s on an H100 with the KV cache full; fewer parallel answers (`max_num_seqs`) may be
  faster. Not tested.
- No second model has read the grader v3 rescoring.
- RLN-3 rows for RL step 400 and the first release at T 0.6 are not scored (`DIRECTION.md`; board `knowledge-c3f1bf`).
- SPEC4 §0's accuracy and cap rate by RL-length quartile (2 % to 66 %, pass@3 97 / 96 / 84 / 47) are the coordinator's
  numbers; no script for them is in the source. `analysis/rln4_temp.py` computes quartiles for T2 and T3 only.

## Left out of the copy

RLN-1 and RLN-2 (neuron-statistics studies in the same source folder: `SPEC.md`, `SPEC2.md`, `label.py`, `overlap.py`,
`analyze2.py`, `explain/`, the `.npz` statistics, label JSONL files up to 82 MB): a different question. The `pg` launcher
(`infra/aws_pg/`), `pipeline.py`, and the rest of the modules that `hf_helpers.py` replaces.
