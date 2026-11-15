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
| `analysis/axis.py`, `analysis/axis_test.py`, `specs/SPEC_axis.md` | One axis or several: per-problem vectors of every arm, pair overlap and oracle union against the rest-score null, Rasch against Rasch plus one bilinear term, the floor; planted checks. See "One axis or several?". |
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
| `analysis/anatomy.py` | Gap anatomy from the Day-1 #3 four-sample runs (laptop): joint k-of-4 table, held-out-sample decomposition, subject and level, error types, tokens, divergence proxy, `pool_k_le3.json`. See "Gap anatomy". |
| `analysis/anatomy_judge.py` | Slip against wrong plan: `prep` draws the items and the two controls and writes blind batches; `score` reads the judges' labels (agreement, controls, first wrong step). |
| `grader/repair_v4.py`, `grader/repair_v4_test.py` | Grader v4 / v4a: grader v3 plus five label-free answer-statement rules (placeholder, lower-case marker, last-line math, trailing brace, form), and its planted tests. A grader version for both models, not a method. See "Answer-statement repair". |
| `analysis/repair.py`, `prep/repair_plan.py`, `data/repair/plan_v1.json` | Answer-statement repair: the gold-aware upper bound, the rule table and the vote under v4 (laptop); the plan of the forced-suffix job (not run). |
| `data/anatomy/math500_meta.json` | Subject, level and reference solution of the 500 problems (HuggingFaceH4/MATH-500 `test.jsonl`, revision `6e4ed1a`), same order and `unique_id` as `data/rln4/math500.json`. |
| `specs/SPEC5_map.md` | RLN-5 map spec: where the RL model still disagrees with the cued base; hypothesis H and its refutation rules; controls. |
| `jobs/rln5_map.py` | RLN-5 map job (inference only, team runner): both models over the stored T1 and T2 answers with teacher forcing; per-position shards and `checks.json` in `$OUT_DIR`. See "RLN-5 map". |
| `analysis/rln5_map_analyze.py` | RLN-5 map readout: reads `runs/<job-id>/`, writes `metrics.json` and `examples.json` (analysis a-e of SPEC5_map.md §6, the test of H). |
| `specs/SPEC_day1_3.md` | Day-1 #3 spec: four samples and up to two restarts per sample in one job, seeds, the vote and its tie rule, the restart row, token accounting, hypotheses, test record and the MATH-500 results. |
| `analysis/day1_vote.py`, `analysis/day1_vote_test.py` | Day-1 #3 readout from one `run_cell --samples k --restarts r` run: single, restart, vote, pass@k and vote-after-restart rows (grader v3, Wilson, tokens per problem, paired bootstrap, `--minus` another run), `rows.jsonl`; and its planted cases. See "Day-1 #3". |
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

## Day-1 #3: restart and four-sample vote (MATH-500, n = 500, T 1.0 / top-p 1.0, grader v3, board work-63fac2)

One job per model: `run_cell --samples 4 --restarts 2` (sample s, attempt a of problem i has seed + 10000 s + 1000 a + i; an
attempt that hits the 16,384 cap is sampled again in the same job, up to twice). Rows by `analysis/day1_vote.py`; procedure,
tie rule and hypotheses in `specs/SPEC_day1_3.md`. Single = sample 0, attempt 0. Restart = sample 0, its first attempt that
did not hit the cap, else its last. Vote = plurality over attempt 0 of the four samples, answers grouped with `rln4_lib.agree`;
a sample with no extracted answer casts no vote; ties go to the group with the lowest sample number. pass@4 = any of the four
right: an oracle, the upper bound of the vote, not a method. Tokens per problem = every generated token of every attempt the
row uses. Wilson 95 % interval in percent; paired bootstrap, 5,000 resamples, seed 0, in points.

| Row | Base with cue: right [95 %] | Tokens per problem | RL plain: right [95 %] | Tokens per problem | RL minus base, points [95 %] |
|---|---|---|---|---|---|
| single | 405 of 500 [77.3, 84.2] | 3,808 | 456 of 500 [88.4, 93.4] | 4,675 | 10.2 [7.2, 13.2] |
| restart, up to 2 | 413 [79.0, 85.7] | 4,852 | 458 [88.8, 93.7] | 4,899 | 9.0 [6.0, 12.0] |
| vote over 4 | 446 [86.2, 91.6] | 16,034 | 474 [92.5, 96.4] | 18,747 | 5.6 [3.6, 7.8] |
| vote over 4 after restart | 450 [87.1, 92.3] | 19,697 | 475 [92.7, 96.6] | 19,864 | 5.0 [3.0, 7.0] |
| pass@4 (oracle) | 467 [90.9, 95.3] | 16,034 | 482 [94.4, 97.7] | 18,747 | 3.0 [1.4, 4.8] |

| | Base with cue | RL plain |
|---|---|---|
| Run folder | `results/day1_3/math500_base_cue-01/` | `results/day1_3/math500_rl-01/` |
| Job (one H100, commit `c36f562`) | `abaybektursun-1114-153825-208b` | `abaybektursun-1114-183640-e828` |
| Rows (attempts), restarts | 2,137, 137 | 2,041, 41 |
| Generated tokens, tokens/s, wall | 9.85 M, 1,213, 8,191 s | 9.93 M, 1,360, 7,369 s |
| Right in samples 0 to 3 (single) | 405, 409, 410, 418 | 456, 462, 464, 458 |
| Cap hits in samples 0 to 3 | 25, 23, 22, 20 | 6, 10, 5, 11 |
| `rows.jsonl` lines, sha256 (first 16 hex) | 2,137, `686585cfcbef4e19` | 2,041, `289a3c0914342676` |

Each run folder holds `run.json`, `metrics.json`, `readout.json` (rows, per-problem 0/1 vectors), `examples.json` (one vote and
one restart problem scored right and one scored wrong, every attempt's seed, extracted answer, score and last 2,000
characters) and `rows.jsonl`: every attempt without its text (`problem_index`, `sample`, `attempt`, `seed`, `n_new`, `cap_hit`,
`finish_reason`, `loop_A`, `extracted_v3`, `score_v3`, `gold`), for offline scoring. The full answers are `answers.jsonl` in the
job's `$OUT_DIR` in abaybektursun's Modal workspace, not committed.

- Against each model's own single row: base restart +1.6 [0.6, 2.8], vote +8.2 [5.8, 10.8], vote after restart +9.0
  [6.4, 11.8]; RL restart +0.4 [0.0, 1.0], vote +3.6 [2.0, 5.2], vote after restart +3.8 [2.2, 5.6]. Published prior: Maj@4
  adds 0.8 points to a 73.6 % model on MATH-500 (arXiv 2507.18122, Table 1).
- At equal procedure RL stays ahead: 5.6 points under the vote, against 10.2 single. The base's vote against one RL sample:
  -2.0 points [-4.0, 0.2], with 3.4 times the tokens (16,034 against 4,675). At 16 to 20 k tokens per problem RL's vote has
  474 to 475, the base's 446 to 450.
- Tokens per added point for the base: restart about 650 (1,044 more tokens, 1.6 points), vote about 1,490 (12,226, 8.2).
- Instrument check: sample 0 repeats T1 and T2 on their seeds: 405 right and 25 cap hits against 410 and 27; 456 and 6 against
  463 and 6. Texts differ (other GPU, other batch). The same seeds in another job gave RL vote 469 (the first attempts of
  `abaybektursun-1114-153833-f4ab`), so about 1 point of a vote row is run-to-run variation.
- Raw rows, read by hand. Base: the vote turns 43 problems from wrong to right and 2 from right to wrong (50 and 403: a wrong
  answer with 3 and 2 votes against a right sample 0); in the 43, sample 0 had a wrong answer 28 times and no answer 15 times
  (10 cap hits). 36 ties for first, 5 scored right. RL: 18 wrong to right, 0 right to wrong, 16 ties, 3 right. No winning group
  mixes right and wrong members; `agree` kept two right answers apart in 2 base problems (`east` / `East`, `$f(3) = 8$` / `8`)
  without changing a score. Base sample-0 restarts: of 25 cap hits, 8 end right, 8 wrong, 9 hit the cap three times. Rule A
  flags 0 of the base's 166 cap-hit attempts and 1 of RL's 44: at T 1.0 a cap hit is a long answer, not a loop. Of the 54
  problems the base's vote misses, RL's vote misses 24.
- Not scored: `abaybektursun-1114-153833-f4ab`, the first RL job, died at 2,013 of 2,034 rows with `FileExistsError` on
  `/runs/<job>` in the runner (suspected: the container restarted and `infra/runner.py` creates the folder without
  `exist_ok`; not confirmed). The readout refuses an unfinished run. Smoke: `abaybektursun-1114-152646-e76b`, 10 problems,
  45 rows, 5 restarts, single 8 of 10.
- The harder 328 with this procedure is not run here (board work-140e13).

## Label-free selector over the four stored samples (MATH-500, n = 500, laptop, board work-3095f1, idea-664670)

Question: does a rule that sees no answer key beat the plurality vote on the four samples of Day-1 #3? Answer: one tie-break
does on the base, by 7 problems, and the rule is not confirmed on RL or on the 328. `analysis/selector.py` scores 11 rules fixed
in `specs/SPEC_selector.md` before scoring (written after reading the 21 problems the vote misses and pass@4 has, so the
MATH-500 numbers are optimistic), and `cv_pick`: the best of the 12 on four folds scored on the fifth. All rules use the same
tokens as the vote (16,034 base, 18,747 RL). Paired bootstrap against the vote, 5,000 resamples, seed 0, in points.

| Rule | Base with cue: right [95 %] | minus vote [95 %], fixed / broken | RL plain: right | minus vote [95 %], fixed / broken |
|---|---|---|---|---|
| vote (baseline; a tie goes to the lowest sample) | 446 [86.2, 91.6] | | 474 | |
| `tie_short`: a tie goes to the group with the shortest finished sample | 453 [87.7, 92.9] | +1.4 [0.4, 2.4], 7 / 0 | 475 | +0.2 [0.0, 0.6], 1 / 0 |
| `tie_aprob`: a tie goes to the highest stored answer probability | 451 | +1.0 [-0.2, 2.2], 8 / 3 | 475 | +0.2 [-0.4, 1.0], 2 / 1 |
| `tie_mlp`: a tie goes to the highest mean token log-probability | 450 | +0.8 [-0.4, 2.0], 7 / 3 | 477 | +0.6 [0.0, 1.4], 3 / 0 |
| `tie_clean`, `drop_cap` | 446, 446 | 0 / 0 | 475, 475 | 1 / 0 |
| `tie_restate` | 445 | -0.2 [-1.2, 0.8], 3 / 4 | 474 | 1 / 1 |
| `w_invlen`: votes weighted 1 / tokens | 445 | -0.2 [-1.6, 1.2], 7 / 8 | 474 | 2 / 2 |
| `w_aprob`: votes weighted by answer probability | 452 | +1.2 [0.0, 2.6], 9 / 3 | 474 | 1 / 1 |
| `short1`: the shortest finished sample | 434 | -2.4 [-4.4, -0.4], 8 / 20 | 471 | -0.6 [-1.8, 0.6], 3 / 6 |
| `max_aprob`: the most confident sample | 423 | -4.6 [-7.2, -2.2], 8 / 31 | 464 | -2.0 [-3.6, -0.4], 3 / 13 |
| `max_mlp`: the most likely sample | 427 | -3.8 [-6.2, -1.4], 9 / 28 | 472 | -0.4 [-1.8, 1.0], 5 / 7 |
| `cv_pick` (held-out folds) | 451 [87.3, 92.5] | +1.0 [0.0, 2.0], 6 / 1 | 477 | +0.6 [0.0, 1.4], 3 / 0 |
| pass@4 (oracle) | 467 | | 482 | |
| control: random tie-break, expected | 448.2 | | 474.3 | |
| control: a tie goes to the longest finished sample | 446 | | 476 | |

- Base: `tie_short` has 453, 3 below one RL sample (456) and 14 below pass@4. It only changes the 36 ties: 12 right, against 5
  for the lowest sample, 5 for the longest and 7.2 expected for a random choice. So the gain over a fair tie-break is about 5
  problems of 36, and all 7 fixed problems (11, 20, 71, 94, 189, 303, 352) were read before the rule was written. `cv_pick`
  chose `tie_short` on four folds and `w_aprob` on one: 451, interval [0.0, 2.0].
- RL: the same rule fixes 1 of 16 ties and the longest-sample control fixes 2. Shortness is not confirmed on RL; its `cv_pick`
  chose `tie_mlp` (477, +3).
- Choosing one sample by confidence or by length is below the vote on both models (423 to 434 on the base), as in arXiv
  2507.18122 Table 1. `short1` with the other three samples stopped when the first finishes would cost 9,795 tokens per
  problem on the base (434) and 14,504 on RL (471).
- The 21 base problems the vote misses and pass@4 has: 15 ties the lowest sample lost (6 with four different answers, 3 with
  three, 3 with two after cap hits, 3 ties of 2 against 2) and 6 with a wrong answer in the majority. No rule here touches the 6.
- The 328: not scored. `tie_short` passes the spec's rule for going to the 328 (`cv_pick` above the vote, its interval above
  0), but sameraslan's four-sample rows (board result-1dedfe) are in his Modal Volume; git has only per-problem 0/1 vectors and
  token counts, not the extracted answers. With the joined `answers.jsonl` and `metrics.json` in `runs/<dir>`:
  `python -m studies.rlneurons.analysis.selector --run runs/<dir> --out studies/rlneurons/results/selector/hard328_base_cue-01`
  and read the `tie_short` row only (82 ties of 328 there, against 36 of 500 here).

Run folders `results/selector/math500_base_cue-01/` and `results/selector/math500_rl-01/`: `run.json` (commit, command, source
job), `readout.json` (rows, controls, per-problem 0/1 and chosen sample per rule, the rule chosen per fold), `examples.json` (one
problem the best rule gets right against the vote, one it gets wrong although a sample is right: 11 and 39 on the base). Inputs:
`runs/abaybektursun-1114-153825-208b/answers.jsonl` and `runs/abaybektursun-1114-183640-e828/answers.jsonl` (the rules need
`text`, `answer_prob`, `mean_logprob`, which `rows.jsonl` lacks). Test (planted rows, rules that must fail, a planted oracle):

```
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.selector_test
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.selector --run runs/abaybektursun-1114-153825-208b --out studies/rlneurons/results/selector/math500_base_cue-01
```

## Gap anatomy: reliability shift or new problems (MATH-500, n = 500, 4 samples, laptop, board work-5b7270, idea-9e3dff)

Question: is RL's gain over the cued base problems the base already solves in some samples, or problems it does not solve?
Answer: mostly the first. Of the 198-sample gap (base 1,642 right of 2,000, RL 1,840), 81 % sits in problems the base solves
at least once in 4 and 19 % [11, 27] in problems it solves 0 of 4; the cell "base 3 of 4, RL 4 of 4" alone holds 86 samples
(43 %). Scored on a held-out sample, so that noise in "0 of 4" cannot inflate it, the class "base wrong on the other three
samples" holds 14 % [5, 23] of the gap. Spec, hypotheses and nulls, written before the script: `specs/SPEC_anatomy.md`.
Inputs: attempt 0 of samples 0 to 3 of the two Day-1 #3 jobs, grader v3. Intervals: bootstrap over problems, 5,000
resamples, seed 0. The planner's counts (86; 250 / 89 / 19 base errors) are confirmed.

Problems by right samples of 4 (rows: base with cue; columns: RL plain); the share of the gap is n (r - b) / 198:

| base k, RL k in columns | 0 | 1 | 2 | 3 | 4 | problems | share of the gap [95 %] | homogeneous null, problems |
|---|---|---|---|---|---|---|---|---|
| 0 | 16 | 4 | 8 | 3 | 2 | 33 | 18.7 % [10.5, 27.4] | 0.5 |
| 1 | 2 | 2 | 3 | 7 | 10 | 24 | 22.7 % [13.4, 32.2] | 9.4 |
| 2 | 0 | 1 | 6 | 4 | 17 | 28 | 18.7 % [11.2, 26.7] | 64.8 |
| 3 | 0 | 0 | 0 | 12 | 86 | 98 | 43.4 % [34.8, 53.2] | 198.1 |
| 4 | 0 | 0 | 0 | 7 | 310 | 317 | -3.5 % [-6.8, -1.0] | 227.2 |
| RL problems | 18 | 7 | 17 | 33 | 425 | 500 | | |

Gross: RL gains 208 samples and loses 10. The homogeneous null (every problem has the model's mean solve probability, 0.821
and 0.920) predicts 0.5 problems at 0 of 4 and 142 in the (3, 4) cell; the data have 33 and 86: solve probability differs
between problems (H3 holds).

Held-out sample: class a problem by three of its base samples, score the fourth, over the 4 choices of the fourth.

| base right in the other 3 | problems per choice | base, held-out sample right | RL, same sample | share of the held-out gap [95 %] |
|---|---|---|---|---|
| 0 | 39.0 | 15.4 % (24 of 156) | 33.3 % (52) | 14.1 % [5.0, 23.2] |
| 1 | 32.0 | 43.8 % (56 of 128) | 78.1 % (100) | 22.2 % [10.9, 33.2] |
| 2 | 87.5 | 84.0 % (294 of 350) | 95.4 % (334) | 20.2 % [11.6, 29.8] |
| 3 | 341.5 | 92.8 % (1,268 of 1,366) | 99.1 % (1,354) | 43.4 % [34.5, 53.4] |

- The largest part of the gap is in problems where the base's other three samples are all right: there the base still fails
  7.2 % of the time and RL 0.9 %. Halves (class by base k of 2, score the other two samples, 6 splits): k = 0 holds 21.5 %
  [13.1, 29.7] of the gap, k = 1 28.3 %, k = 2 50.2 %. Half-to-half correlation of k of 2: base 0.63, RL 0.73.
- H1 (reliability shift; refuted under 30 % of the gap in base k >= 2): 58.6 %, not refuted. H2 (new problems; refuted
  under 30 % in base k = 0): 18.7 %, refuted. The "0 of 3" class is not "never": the base solves 15 % of held-out samples
  there. Of the 33 problems with base 0 of 4, RL has 0 of 4 on 16 and 4 of 4 on 2 (problems 170 and 279).
- Prior: Yue et al. (arXiv 2504.13837, Table 2) find the same from coverage: pass@128 of the base is above the RL model's.
  Here pass@4 is 467 against 482.

By level and subject (H4: level 5 holds more of the gap than of the problems; holds):

| Level | Problems | Base right samples | RL | Gap, samples per problem [95 %] | Share of the gap [95 %] | Share of problems |
|---|---|---|---|---|---|---|
| 1 | 43 | 93.6 % | 98.8 % | 0.21 [0.07, 0.37] | 5 % [1, 8] | 9 % |
| 2 | 90 | 93.6 % | 98.3 % | 0.19 [0.11, 0.28] | 9 % [5, 13] | 18 % |
| 3 | 105 | 87.1 % | 96.9 % | 0.39 [0.27, 0.52] | 21 % [14, 28] | 21 % |
| 4 | 128 | 84.4 % | 92.8 % | 0.34 [0.22, 0.47] | 22 % [14, 30] | 26 % |
| 5 | 134 | 64.6 % | 81.0 % | 0.66 [0.49, 0.84] | 44 % [35, 54] | 27 % |

| Subject | Problems | Base | RL | Gap, samples per problem [95 %] | Share of the gap [95 %] | Share of problems |
|---|---|---|---|---|---|---|
| Algebra | 124 | 94.8 % | 98.6 % | 0.15 [0.06, 0.26] | 10 % [4, 16] | 25 % |
| Counting & Probability | 38 | 75.0 % | 88.2 % | 0.53 [0.29, 0.79] | 10 % [5, 16] | 8 % |
| Geometry | 41 | 71.3 % | 78.7 % | 0.29 [0.12, 0.49] | 6 % [2, 11] | 8 % |
| Intermediate Algebra | 97 | 73.2 % | 88.7 % | 0.62 [0.44, 0.80] | 30 % [22, 39] | 19 % |
| Number Theory | 62 | 88.7 % | 97.6 % | 0.35 [0.18, 0.55] | 11 % [5, 17] | 12 % |
| Prealgebra | 82 | 80.2 % | 91.8 % | 0.46 [0.28, 0.67] | 19 % [12, 28] | 16 % |
| Precalculus | 56 | 77.7 % | 89.7 % | 0.48 [0.29, 0.68] | 14 % [8, 21] | 11 % |

Wrong samples by type, and the other model's four samples on the same problems:

| Model, error type | Samples | Problems | Other model right on those problems [95 %] | Own k of 4 on those problems (0, 1, 2, 3) |
|---|---|---|---|---|
| base, finished-wrong | 250 | 152 | RL 68.4 % [65.5, 71.2] | 28, 22, 25, 77 |
| base, cap hit | 89 | 50 | RL 48.9 % [43.7, 54.1]; RL hits the cap in 69 of 356 samples | 19, 11, 12, 8 |
| base, no answer | 19 | 19 | RL 82.9 % [72.9, 89.7] | 3, 1, 2, 13 |
| RL, finished-wrong | 131 | 68 | base 21.2 % [17.9, 24.9] | 18, 6, 15, 29 |
| RL, cap hit | 29 | 18 | base 15.5 % [10.0, 23.2] | 6, 2, 6, 4 |

- H5 (RL does as well on the base's cap-hit problems as on its finished-wrong problems) is refuted: 48.9 % against 68.4 %.
  A base cap hit marks a problem that is hard for both models. In the (3, 4) cell the one wrong base sample is finished-wrong
  66 times, no answer 13 times, a cap hit 7 times.
- Tokens: base right samples have mean 2,746 (median 1,561), wrong 9,800; RL right 3,984 (2,843), wrong 12,774. Within a
  problem that has both, wrong samples are longer: base +2,324 tokens [1,701, 2,972] (150 problems; finished only +1,359
  [817, 1,939], 137), RL +2,443 [1,624, 3,292] (57 problems).

### Slip against wrong plan (`results/anatomy/judge-01/`)

60 base and 30 RL finished-wrong samples (random, at most one per problem per model), labeled by a judge that sees the
problem, the gold answer, the reference solution, the answer and the shortest right sample of the same model when one exists,
and not the model's name. Judge: Claude Code subagents (the agent's own model) with the fixed rubric `rubric.md`, one subagent
per batch file. No hosted provider was used: the `OPENAI_API_KEY` on this machine is rejected by the API, and the repo has no
other provider code. Pass A covers all 120 items; pass B a random half of the real items and all controls, in other batches.

| Pass A label | Base, 60 | RL, 30 |
|---|---|---|
| computation slip (right method) | 21, 35 % [24, 48] | 5, 17 % [7, 34] |
| wrong plan | 17, 28 % [19, 41] | 20, 67 % [49, 81] |
| misread problem | 14, 23 % [14, 35] | 5, 17 % [7, 34] |
| format (work reaches the gold value, final line differs) | 8, 13 % [7, 24] | 0 |

- Agreement of the two passes: 44 of 45 real items with the same label, Cohen's kappa 0.97 (base 29 of 30, RL 15 of 15).
  Both passes are the same model, so this is its consistency, not a second opinion.
- Controls. Shuffled problem and answer: `mismatch` 15 of 15 in both passes (pass at 13). Planted slip: `slip` 11 of 15 in
  pass A and 13 of 15 in pass B (pass at 12: pass A fails by one). All 6 misses are `format`: the planted wrong value sits
  in the last step after the answer has stated the right value earlier, which fits the rubric's `format`. So the boundary
  between slip and format is not reliable for an error in the final restatement; slip or format: 15 of 15. The judge's quote
  is within 5 % of the planted step in 12 of 15.
- H6 (over half of the base's finished-wrong answers are slips; refuted under a third): 35 % [24, 48], neither.
- With a right sibling (base, 48 items): 18 slip, 9 wrong plan, 13 misread, 8 format. Without one (the base has 0 of 4, 12
  items): 3 slip, 8 wrong plan, 1 misread. Problems the base solves sometimes fail by slip, misreading or form (39 of 48);
  problems it never solves fail by plan. RL's remaining errors are mostly wrong plans (20 of 30).
- The 8 base `format` items: 3 leave the prompt's placeholder as the answer (`$Answer$`; problems 45, 266, 484), 1 puts two
  solutions in two boxes (25), 4 state the gold value in another form that grader v3 rejects (`12th grade` for 12, `(C)
  Plane`, `-I` for the matrix, the decimal of 12 pi; problems 379, 227, 248, 313). With the 19 no-answer samples, about
  52 of the base's 358 wrong samples (8 / 60 x 250 + 19; 36 to 79 by the interval) fail in the statement of the answer, not
  in the mathematics; RL has 0 of 30 and no no-answer sample. Not tested: a rerun of the base with these forms accepted.
- First wrong step (the judge's verbatim quote, located in the answer; 82 of 82 quotes found): median position 0.20 of the
  answer's characters for the base (quartiles 0.05, 0.55), 0.29 for RL; a misreading sits at 0.06, a slip at 0.25, a wrong
  plan at 0.26. 65 % of first wrong steps are in the first third of the answer. The two passes quote steps within 0.15 of
  each other in 37 of 41.
- The spec's proxy for the divergence point (first number absent from the right siblings) is rejected: it is within 0.15
  of the judge's step in 18 of 38 (the spec asked for 10 of 15), and its position in right samples scored the same way is
  about the same (median 0.30 against 0.26 for wrong samples).
- 15 pairs read at both positions (the first 15 base rows of `labels.json` with a proxy position). The judge's quotes are
  single checkable steps: `1136 - 88 = 1148` (problem 21), `150 + 130 + 150 + 130 = 580` (189), 450 factored with 5 cubed
  (217), day 27 left out of a count (128), graph axes swapped (4), subscripts read as digits (137), a draw without
  replacement assumed (190). The proxy lands on decimal approximations and side computations. Three answers reach the gold
  value and then leave it (52: computes 12, then redoes the denominator; 136: derives 64, then discards the bound; 60: has
  p and q right, a sign error on r fails its own check and it abandons the method).

Limits: 4 samples per problem; one judge model of the agent's own family; cap hits and no-answer samples are counted, not
labeled; the MATH-500 problems only.

Run folders: `results/anatomy/math500-01/` (`readout.json`: every table above; `examples.json`: a (3, 4) problem with its
right and wrong base samples, a (0, 4) problem in both models, an RL loss, a cap hit; `pairs.json`: the 168 wrong and right
sibling pairs with the proxy position; `pool_k_le3.json`: the 183 problems with base k <= 3, with base and RL k, subject,
level and the type of each base sample, for the prefix hand-off study; `run.json`, whose commit is the parent of `9df9b40`, which
added the script unchanged together with the folder) and `results/anatomy/judge-01/` (`readout.json`, `labels.json`: both passes' label,
quote and reason per item, `rubric.md`, `examples.json`: one item per label and one control scored right and one scored
wrong, `run.json`). The batch files and raw labels are in `runs/anatomy_judge/` (not committed).

```
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.anatomy --base runs/abaybektursun-1114-153825-208b --rl runs/abaybektursun-1114-183640-e828 --out studies/rlneurons/results/anatomy/math500-02
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.anatomy_judge prep --base runs/abaybektursun-1114-153825-208b --rl runs/abaybektursun-1114-183640-e828 --work runs/anatomy_judge-02
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.anatomy_judge score --work runs/anatomy_judge-02 --pairs studies/rlneurons/results/anatomy/math500-01/pairs.json --out studies/rlneurons/results/anatomy/judge-02
```

## Answer-statement repair: how much of the gap is a failure to state the answer (MATH-500, n = 500, 4 samples, laptop, board work-655434, idea-ae6eba)

Question: how many of the 9.9 points between the cued base and RL (mean of the 4 samples, grader v3) come back when the base's
answer is only read better, with RL read the same way? Answer: 0.5 point. Label-free extraction rules turn 10 of the base's
2,000 samples from wrong to right and 0 of RL's 2,000: base 1,642 to 1,652, RL 1,840, gap 9.9 to 9.4 points (change -0.5
[-0.8, -0.2]). With the gold in hand the ceiling is 31 base samples (1.55 points) against 5 for RL. The whole gain is a grader
correction; no generation step was run. Spec with hypotheses, written before any count: `specs/SPEC_repair.md`. Inputs: attempt
0 of samples 0 to 3 of the two Day-1 #3 jobs. Intervals: paired bootstrap over problems, 5,000 resamples, seed 0.

Kept apart: a rule that changes extraction or normalization is a grader version (`grader/repair_v4.py`; `grade_v3` is
unchanged), applies to both models and corrects the measured gap; it is not a route to RL. A step that changes generation
(Part B) is a method; it was not run.

Rules (never read the gold): R1 a placeholder answer (`$Answer$`) falls back to the candidate before it within 5 non-empty
lines; R2 with nothing extracted, the rest of the last line after `answer:` / `answer is` in any case; R3 with nothing
extracted and the answer finished, the last math span of the last line, or that line itself when it has at most 30 characters
and a digit; R4 a trailing unmatched `}` is removed; R5 `(C) Plane` becomes `C` and `12th grade` becomes `12` (written from two
judged items, so optimistic). v4 = the rules as written before scoring. v4a = after reading v4's 16 flips: R2 only on answers
that ended with the stop token, and R3 before R2.

| Rule set (grader) | Base with cue: right of 2,000 (per sample) | minus v3, points [95 %] | wrong to right / right to wrong | accepted, judged wrong by hand | RL: right of 2,000 | changed |
|---|---|---|---|---|---|---|
| v3 (baseline) | 1,642 (405, 409, 410, 418) | | | | 1,840 (456, 462, 464, 458) | |
| R1 placeholder | 1,642 | 0 | 0 / 0 (fires on 2) | 0 | 1,840 | 0 |
| R2 lower-case marker | 1,653 | +0.55 [0.25, 0.95] | 11 / 0 (fires on 53, 44 of them cap hits) | 6 | 1,840 | 0 (fires on 2 cap hits) |
| R3 last-line math | 1,648 | +0.30 [0.10, 0.55] | 6 / 0 (fires on 10) | 0 | 1,840 | 0 |
| R4 trailing brace | 1,642 | 0 | 0 / 0 (fires on 0) | 0 | 1,840 | 0 |
| R5 form | 1,644 | +0.10 [0.00, 0.25] | 2 / 0 | 0 | 1,840 | 0 |
| v4, as written before scoring | 1,658 (409, 413, 415, 421) | +0.80 [0.40, 1.25] | 16 / 0 | 6 | 1,840 | 0 |
| R2 on finished answers only | 1,648 | +0.30 [0.10, 0.55] | 6 / 0 (fires on 9) | 1 | 1,840 | 0 |
| v4a, amended | 1,652 (407, 412, 413, 420) | +0.50 [0.20, 0.80] | 10 / 0 | 0 | 1,840 | 0 |

| RL minus base, points [95 %] | mean of 4 samples | sample 0 |
|---|---|---|
| v3 | 9.9 [8.25, 11.6] | 10.2 [7.2, 13.2] |
| v4 | 9.1 [7.5, 10.75] | 9.4 [6.4, 12.4] |
| v4a | 9.4 [7.75, 11.1] | 9.8 [6.8, 12.8] |

Vote over 4 (the rule of `analysis/day1_vote.py`): base 446 under v3, 446 under v4a (0 fixed, 0 broken), 447 under v4 (170 and
189 fixed by wrongly accepted cap-hit samples, 481 broken); RL 474 under all three.

- H3 (the rules accept no wrong answer) is refuted for v4 as written: 6 of its 16 accepted samples are wrong on reading. 5 are
  cap hits where a lower-case "the answer is X" sits in unfinished reasoning (26, 170, 189 twice, 317: "the answer is 0. But
  how?"), 1 is a finished answer whose reasoning says 326.5 and whose final line says 315.5 (399). v4a removes these 6 and
  keeps the 10 whose final statement is the gold (22, 45, 81, 114, 122, 141, 227, 237, 379, 430). The amendment was made on the
  same 2,000 samples, so the v4a numbers are optimistic; planted cases of both failures are in the test.
- H1 (at least 2 points of the gap are answer-statement failures a label-free rule recovers) is refuted: +0.5 point on the
  base (under the 1 point set in the spec). H2 (RL has none) holds: 0 of RL's 2,000 samples change, and RL has 0 samples with
  no extracted answer.
- Upper bound with the gold (a value the grader accepts as equal to the gold: boxes, marker rests, one-line math spans, the
  part after a span's last `=`, each of the last 5 lines as plain text). Wrong samples with such a value:

| Model, sample type | Samples | in the last line | in the last 5 non-empty lines | anywhere |
|---|---|---|---|---|
| base, finished-wrong | 250 | 6 | 23 | 46 |
| base, no answer | 19 | 6 | 8 | 8 |
| base, cap hit | 89 | 2 | 7 | 10 |
| RL, finished-wrong | 131 | 0 | 5 | 18 |
| RL, cap hit | 29 | 1 | 2 | 5 |

- 20 of the base's 31 finished or no-answer samples with the gold in the last 5 lines, read by hand
  (`upper_bound_read.json`): 14 state the gold as their answer and 6 do not (the gold is an intermediate value or a list
  number: 458, 403 twice, 136, 214, 399). Of the 14, v4a reads 5; the other 9 are two roots in two boxes joined by
  `\text{ and }` (25, 284 twice), the prompt's template around the value (`$Answer: 83$ where $Answer is ...`, `\(Answer:
  23\)Where ...`, `$Answer (without quotes)`: 49, 39, 484), an unmatched `$` after the value (331), `137 1/2` for a mixed
  number (472) and `-I` for the matrix (248). Scaled, about 22 of the base's 2,000 samples (1.1 points) are answer-statement
  failures, against at most 5 of RL's (0.25): at most about 1 point of the 9.9.
- H4 (the judge's extrapolation of 52, range 36 to 79, overstates what extraction can recover) holds: 31 by the upper bound,
  about 22 after reading. The prompt's own words appear in 12 extracted base answers (`$Answer`, "the answer to the
  problem"), 3 of them right, and in 0 of RL's.
- Read by R2 and still scored wrong: `east.` for gold `east` (97, sample 1: the final period).

Part B, forced suffix (a method), was not run. The prefix-file input for `jobs/run_cell.py` had not landed on `main` or
`origin/handoff` when Part A ended (`jobs/handoff_gen.py` on `origin/handoff` continues sample 0 from a cut and takes no
suffix). Eligible samples (finished, v3 extraction unusable; the gold is not read): 21 of the base's 2,000 (19 no answer, 2
placeholders; 8 already right under v4a) and 0 of RL's. So the step can add at most 13 base samples (0.65 point) over v4a and
nothing to RL. The exact job is in `specs/SPEC_repair.md` ("Part B job, not run"); its plan, with 100 control samples per
model, is `data/repair/plan_v1.json` (suffix `\n\nThus, the final answer is \(\boxed{`, RL's most frequent non-empty answer-line
opening, in 46 of its right answers and 19 of the base's; RL boxes 1,838 of its 1,840 right answers, the base 1,176 of
1,642).

Limits: 4 samples per problem; the rules and the amendment were fixed on MATH-500 and not scored on the 328; one reader for
the flips and the 20 upper-bound samples; the upper bound reads one-line math spans only, so a gold-equal value in a
multi-line display is missed.

Run folder `results/repair/offline-01/`: `readout.json` (every table above), `rows.jsonl` (per sample: type, v3 and v4a
extraction and score, the v4 score, upper-bound flags, Part B eligibility), `flips.json` (every sample whose score changes
under v4 or v4a, with its last 700 characters and the hand judgement), `upper_bound_read.json` (the 20 samples read),
`examples.json` (one sample v4a turns right, one that v4 accepts wrongly, one with the gold in the last 5 lines that stays
wrong), `run.json`.

```
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.grader.repair_v4_test
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.repair --base runs/abaybektursun-1114-153825-208b --rl runs/abaybektursun-1114-183640-e828 --out studies/rlneurons/results/repair/offline-02
```

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

### The same cells on the 328 harder problems (Day-1 #4b, board work-43d4a1)

All from `results/day1_wdiff328/readout.json` (`analysis/day1_wdiff328.py`, plan `specs/DAY1_wdiff328_2026-11-14.md`). The 328
problems of "Harder 328", T 1.0 / top-p 1.0, cue, one sample per problem, cap 16,384, grader v3. Merges as on MATH-500
(`jobs/merge_weights.py`; theta cells stochastic rounding, effective a 0.2500 and 0.5000; the Code-RL merge is bit-identical to
Code-RL in 355 of 355 tensors). All three jobs at commit `e7b86c8`. The four T 1.0 cells of "Harder 328" are reused, not rerun.
Paired bootstrap, 5,000 resamples, seed 0, 95 % percentile interval, in points.

| Cell (328 problems) | Right (v3) | Hand-read right of 20 | Cap hits | Rule-A loops | Mean tokens | Seed base | Job id, run folder |
|---|---|---|---|---|---|---|---|
| base, plain | 76 |  | 35 | 3 | 4,928 | 50,000,000 | `abaybektursun-1114-132922-7ba0`, `day1_hard328/base_plain_T1-01/` |
| base, cue | 164 |  | 77 | 1 | 9,344 | 3,000,000 | `abaybektursun-1114-151534-e72c`, `day1/hard328_base_cue_t10-01/` |
| theta(0.25), cue | 182 | 0 | 56 | 0 | 9,097 | 72,000,000 | `abaybektursun-1114-181222-a5f4`, `day1_wdiff328/theta0.25_cue-01/` |
| theta(0.5), cue | 190 | 1 | 73 | 0 | 9,656 | 73,000,000 | `abaybektursun-1114-181228-34ad`, `day1_wdiff328/theta0.5_cue-01/` |
| Code-RL, cue | 187 | 0 | 25 | 0 | 7,613 | 71,000,000 | `abaybektursun-1114-181216-a619`, `day1_wdiff328/code1_cue-01/` |
| RL, plain | 206 |  | 20 | 0 | 9,315 | 3,000,000 | `abaybektursun-1114-151540-86ef`, `day1/hard328_rl_plain_t10-01/` |
| RL, cue | 205 |  | 25 | 0 | 9,316 | 50,000,000 | `abaybektursun-1114-132929-a32d`, `day1_hard328/rl_cue_T1-01/` |

Right per source (`per_source_right_v3`):

| Source (n) | base cue | theta(0.25) cue | theta(0.5) cue | Code-RL cue | RL plain | RL cue |
|---|---|---|---|---|---|---|
| OlympiadBench (202) | 114 | 131 | 127 | 130 | 137 | 140 |
| AIME 2024 (29) | 10 | 12 | 13 | 13 | 16 | 15 |
| AIME 2025 (30) | 7 | 7 | 10 | 7 | 12 | 11 |
| HMMT Feb 2025 (30) | 5 | 5 | 7 | 6 | 11 | 8 |
| AMC 23 (28) | 22 | 21 | 26 | 25 | 23 | 25 |
| AIME 2022 (6) | 5 | 5 | 5 | 5 | 5 | 4 |
| AIME 2023 (3) | 1 | 1 | 2 | 1 | 2 | 2 |

| Difference (paired, 328) | Points | 95 % interval |
|---|---|---|
| theta(0.25) cue minus base cue | 5.5 | [1.5, 9.5] |
| theta(0.5) cue minus base cue | 7.9 | [3.7, 12.2] |
| Code-RL cue minus base cue | 7.0 | [2.7, 11.3] |
| theta(0.25) cue minus RL plain | -7.3 | [-11.6, -3.0] |
| theta(0.5) cue minus RL plain | -4.9 | [-8.8, -1.2] |
| Code-RL cue minus RL plain | -5.8 | [-10.1, -1.8] |
| Code-RL cue minus theta(0.5) cue | -0.9 | [-5.5, 3.7] |
| RL plain minus base cue | 12.8 | [8.5, 17.1] |

Problems that change against base cue (164 right, 164 wrong; `fixed_lost_vs_base_cue`):

| Cell | Base-cue wrong, now right | Base-cue right, now wrong |
|---|---|---|
| theta(0.25) cue | 33 | 15 |
| theta(0.5) cue | 40 | 14 |
| Code-RL cue | 37 | 14 |
| RL plain | 49 | 7 |
| RL cue | 49 | 8 |

- The MATH-500 pattern holds in sign and roughly in size: every difference raises the cued base (+5.5 to +7.9 points; MATH-500
  +6.2 to +8.4) and every one stays under RL plain. But on the 328 none comes within its interval of RL plain: theta(0.5) is
  4.9 points under ([-8.8, -1.2]; MATH-500 -2.2, [-4.6, 0.2]) and Code-RL 5.8 under ([-10.1, -1.8]; MATH-500 -2.6). Half the
  difference closes 62 % of the gap (26 of 42 problems), a quarter 43 % (18 of 42).
- The new cells lose 14 to 15 of the base's right problems, twice RL's 7 to 8: one fresh sample changes some outcomes, and RL
  loses fewer of them. Seed sharing does not explain this: RL cue, on its own seed base (50,000,000), also loses only 8, and base
  cue and RL plain (both 3,000,000) have the same first 100 characters on only 8 of 328 problems, the same as pairs on different
  seeds (6 to 13; `same_first_100_chars` in `results/day1_hard328/readout.json`, 13 for theta(0.25) against base cue).
- Code-RL and theta(0.5) are indistinguishable (-0.9, [-5.5, 3.7]); the gain is not specific to the math-RL difference here
  either. Code-RL writes shorter answers (7,613 tokens) and hits the cap as rarely as RL (25).
- Cap hits do not fall with a: 77, 56, 73 for a = 0, 0.25, 0.5, then 20 to 25 for RL. theta(0.5)'s 73 cap hits are long
  reasoning still in progress at the cap (rule-A loops 0), as in the base.
- Predictions (spec): Q1 not refuted by its rule (RL plain minus Code-RL 5.8, interval [1.8, 10.1], lower end under 5), but
  the interval excludes 0, so "within its interval of RL plain" did not happen. Q2 held at the edge (190 >= 190; 191 with the
  hand-read correction). Q3 refuted (182 < 185). Q4 refuted (theta(0.5) has 17 more cap hits than theta(0.25)).
- Hand read, per new cell: 20 finished answers that v3 scored wrong (numpy seed 0, `--hand <arm>`). Code-RL 0 of 20 and theta(0.25)
  0 of 20 are in fact right; theta(0.5) 1 of 20: problem 207, gold `f(n)=n^{2}`, the model wrote `\boxed{f(m) = m^2}`, which
  is the same answer with another variable name. Corrected counts: 187, 182, 191.
- No two of the 7 cells share an identical non-empty completion for any problem (`identical_nonempty_texts`, 21 pairs, all 0).
- One sample per cell: the three new cells differ by at most 8 of 328, inside one another's intervals.
- Cost at 3.95 USD per H100-hour (start to end record of each job, H100 80GB HBM3): Code-RL 40.8 min 2.68 USD, theta(0.25)
  50.4 min 3.32 USD, theta(0.5) 53.4 min 3.52 USD; 9.52 USD in all (limit 12 USD). Merges took 35 to 47 s.
- Raw answers: `runs/<job-id>/answers.jsonl` after `uv run tools/gpu.py get <job-id>`, and
  `s3://pg-lineage-769063704696/results/rlneurons/r5/day1_wdiff328-01/<job-id>/answers.jsonl` for the three new jobs; the four
  reused cells as in "Harder 328" (`.../r5/day1_hard328-01/<job-id>/answers.jsonl`).
  Run: `uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_wdiff328`.

## Truncation rules at T 1.0: min-p and top-p (board work-180a48, spec specs/SPEC_minp.md)

No truncation rule beats untruncated sampling. MATH-500, n = 500, cue, cap 16,384, grader v3, one sample, seeds of the min-p 0
cells (base 41000000, RL 66000000); paired 95 % bootstrap intervals. Readout `results/day1_minp/readout.json`
(`analysis/day1_minp.py`); run folders `results/day1_minp/<arm>-01/`.

| cell | right | minus min-p 0 cell (points, 95 %) | cap hits | rule-A loops | tokens/problem |
|---|---|---|---|---|---|
| base, T 1.0, top-p 1.0 (T1, reference) | 410 | - | 27 | 0 | 3,932 |
| base, T 1.0, min-p 0.1 | 404 | -1.2 [-4.6, 2.2] | 58 | 34 | 4,086 |
| base, T 1.5, min-p 0.1 | 412 | +0.4 [-3.2, 3.8] | 29 | 0 | 4,355 |
| base, T 1.0, top-p 0.95 | 409 | -0.2 [-3.8, 3.2] | 35 | 12 | 4,017 |
| RL, T 1.0, top-p 1.0 (rl_cue-01, reference) | 457 | - | 8 | 0 | 4,696 |
| RL, T 1.0, min-p 0.1 | 460 | +0.6 [-1.6, 2.6] | 19 | 0 | 4,452 |

Cutting the tail at T 1.0 brings back loops: the 34 looped problems at min-p 0.1 had 2 cap hits and 21 right answers at min-p 0.
min-p 0.1 at T 1.5 removes them again and keeps the text coherent. Instrument check (smoke job frustea-1114-175514-c4ca): sampled
tokens with raw probability below 1e-2 fall from 17.1 per 1,000 at min-p 0 to 0.02 at min-p 0.1. Job ids in each run.json; raw
rows in frustea's Modal Volume `iterate-runs/<job>/answers.jsonl`.

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

## Solved examples in context: no gain that survives a second draw or the 328 (shots1, board work-be7af1)

**Correction (2026-11-15 05:20 UTC).** The first draw below gave +5.6 points for RL-written examples (result-6d422d). A second
draw of 3 examples (MATH-500 problems 3, 5, 6, same rule, `data/shots1/{base_b,rl_b}.json`) gave none, and the first draw gave
none on the 328. Counts on the 494 MATH-500 problems that are no example of any arm (`results/shots1b/readout.json`):

| cell | right of 494 | vs no examples (points, 95 %) | cap hits | generated tokens per problem |
|---|---|---|---|---|
| base, cue, no examples (T1) | 404 | | 27 | 3,966 |
| base-written, draw 1 | 411 | +1.4 [-2.0, 4.7] | 17 | 3,395 |
| base-written, draw 2 | 403 | -0.2 [-3.9, 3.4] | 16 | 3,741 |
| Code-RL-written, draw 1 | 409 | +1.0 [-2.6, 4.5] | 19 | 3,848 |
| Math-RL-written, draw 1 | 432 | +5.7 [2.6, 8.7] | 31 | 4,418 |
| Math-RL-written, draw 2 | 401 | -0.6 [-4.5, 3.2] | 32 | 4,361 |

RL-written draw 1 minus draw 2: +6.3 [2.6, 9.9]. So the gain belongs to those three texts, not to their writer. On the 328
(`results/shots1b/hard328_rl-01/readout.json`, seed 3000000, paired with the cued base's job -151534-e72c): RL-written draw 1
164 of 328 against 164, 0.0 [-4.3, 4.3]; 26 problems only with examples, 26 only without; cap hits 107 against 77; generated
tokens 9,933 against 9,344. Reading: three examples in context do not move the cued base toward RL on hard problems. What
remains open is why one set of three texts gave 28 more right answers on MATH-500 than another set by the same writer.
`analysis/shots_hard328.py` makes the 328 readout; `analysis/shots1.py shots1b <arm>=<job> ...` the five-arm table (jobs:
base e840, rl fd89, code d9d6, base_b abaybektursun-1114-195357-6936, rl_b abaybektursun-1114-195350-bc00).

The loop planned on top of this (specs/SPEC_shots2.md, `jobs/shots_loop.py`, board work-eb10d7) stopped in round 0: on the 36
hard problems outside the 328, at cap 8,192, 124 of 144 base answers hit the cap, 12 were right, and 1 problem had 3 agreeing
finished answers (vast.ai job abaybektursun-1114-203934-5e03, rows not committed). No examples could be picked. Not rerun,
because both hypotheses it rested on (long own answers help; RL-like text helps) lost their support above.

The first readout, as posted:


Spec `specs/SPEC_shots1.md`. The cued base on MATH-500 at T 1.0 / top-p 1.0, grader v3, with 3 solved problems (MATH-500
indices 0, 1, 2) in front of every prompt. The arms hold the same 3 problems and differ only in which model wrote the 3 answers.
The 3 problems are left out of every count: n = 497. No weight is changed.

| cell | right of 497 | cap hits | generated tokens per problem | example tokens in the prompt |
|---|---|---|---|---|
| base, cue, no examples (T1) | 407 | 27 | 3,948 | - |
| examples written by the cued base | 414 | 17 | 3,380 | 4853 |
| examples written by Code-RL 3.1 | 412 | 19 | 3,832 | 6638 |
| examples written by Math-RL 3.1 | 435 | 31 | 4,400 | 8240 |
| base + 0.25 (RL - base), cue, no examples | 438 | 13 | 4,047 | - |
| Math-RL 3.1, cue, no examples | 454 | 8 | 4,708 | - |

Paired differences in points, 95 % bootstrap interval over problems: RL-written examples minus no examples +5.6 [2.6, 8.7];
RL-written minus base-written +4.2 [1.2, 7.4]; base-written minus no examples +1.4 [-2.0, 4.8];
Code-RL-written minus RL-written -4.6 [-8.1, -1.2]; RL-written minus theta 0.25 -0.6 [-3.4, 2.2];
RL-written minus RL itself -3.8 [-6.4, -1.2].

Reading: H1 held (three answers written by Math-RL, placed in the base's context, give the gain of a quarter of the weight
difference), H2 refuted (the base's own right answers give none), H3 refuted (Code-RL's answers give none, although Code-RL 3.1
itself scores 450 of 500 with the cue).

Limits, not yet controlled: one draw of 3 examples per arm; RL's examples are longer (8,240 against 4,853 and 6,638 tokens);
seeds differ from T1's (71000000 against 41000000). Cap hits rise with RL's examples (31 against 17 with the base's): the gain
is in finished answers (433 right of 466 finished against 414 of 480). Hand read of 22 finished wrong answers per arm: all
truly wrong; two RL-arm answers copy the example answer 14/3 (problems 94 and 270).

Files: `data/shots1/{base,rl,code}.json` (the examples, built by `prep/shots1_build.py`), `jobs/run_cell.py --shots`,
`analysis/shots1.py`, `results/shots1/readout.json` and run folders `results/shots1/{base,rl,code}-01/` (run.json, metrics.json,
one right and one wrong example). Raw rows: `runs/<job>/answers.jsonl` after `uv run tools/gpu.py get <job>` (abaybektursun's
Modal workspace), jobs abaybektursun-1114-183855-e840 (base), -183901-fd89 (rl), -183907-d9d6 (code). Run:

```
uv run tools/gpu.py submit h100 --hours 2.5 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --shots studies/rlneurons/data/shots1/rl.json --set math500 --temperature 1.0 --top-p 1.0 --seed 71000000 --commit $(git rev-parse HEAD)"
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.shots1 shots1 base=<job> rl=<job> code=<job>
```

## Closing cue: forcing a long answer to commit loses problems (commit1, board work-3d68e2)

Spec `specs/SPEC_commit1.md`. A stored answer of the cued base (T 1.0 / top-p 1.0, one sample) that ran past N tokens is cut at N
tokens, a commit line is appended and the base continues: `box` = `Final answer: \boxed{` (64 new tokens at most, the RLN-3 arm C
that was never scored), `voice` = a sentence in the answer's own voice (1,024 at most). Only the continuation is graded (v3).
Each row is a policy over the whole set: answers of at most N tokens count as stored.

MATH-500 (n 500, stored rows of job abaybektursun-1114-153825-208b, sample 0):

| configuration | right | vs stored (points, 95 %) | generated tokens per problem | answers cut | still right of those right when left alone | right of stored cap hits |
|---|---|---|---|---|---|---|
| stored answers, no cut | 405 | | 3,808 | | | |
| box, N 4,000 | 387 | -3.6 [-6.2, -1.2] | 2,216 | 145 | 41 of 70 | 4 of 25 |
| voice, N 4,000 | 381 | -4.8 [-7.4, -2.4] | 2,297 | 145 | 37 of 70 | 2 of 25 |
| box, N 8,000 | 406 | +0.2 [-1.0, 1.4] | 3,079 | 82 | 19 of 23 | 3 of 25 |
| voice, N 8,000 | 401 | -0.8 [-2.0, 0.2] | 3,120 | 82 | 17 of 23 | 0 of 25 |
| box, N 12,000 | 407 | +0.4 [-0.6, 1.4] | 3,546 | 40 | 0 of 2 | 2 of 25 |
| voice, N 12,000 | 405 | +0.0 [-0.8, 0.8] | 3,571 | 40 | 0 of 2 | 1 of 25 |

The 328 harder problems (stored rows of job abaybektursun-1114-151534-e72c):

| configuration | right | vs stored (points, 95 %) | generated tokens per problem | answers cut | still right of those right when left alone | right of stored cap hits |
|---|---|---|---|---|---|---|
| stored answers, no cut | 164 | | 9,344 | | | |
| box, N 4,000 | 130 | -10.4 [-14.0, -6.7] | 3,478 | 241 | 44 of 83 | 0 of 77 |
| voice, N 4,000 | 126 | -11.6 [-15.6, -7.9] | 3,686 | 241 | 40 of 83 | 2 of 77 |
| box, N 8,000 | 152 | -3.7 [-6.4, -1.2] | 6,016 | 184 | 24 of 40 | 1 of 77 |
| voice, N 8,000 | 151 | -4.0 [-6.7, -1.2] | 6,185 | 184 | 23 of 40 | 2 of 77 |
| box, N 12,000 | 159 | -1.5 [-4.0, 0.9] | 7,927 | 136 | 4 of 14 | 2 of 77 |
| voice, N 12,000 | 158 | -1.8 [-3.7, 0.0] | 8,063 | 136 | 6 of 14 | 2 of 77 |

Chosen on MATH-500 by the spec's rule: box_8000. Headline on the 328: 152 of 328 against 164, -3.7 points
[-6.4, -1.2], at 6,017 generated tokens per problem against 9,344. H1 refuted (no configuration gains on either set), H2 refuted
(box is at or above voice at every N on both sets), H3 at the edge (at N 8,000 on the 328 the commit keeps 24 of the 40
answers that end right when left alone).

Reading: the base's long answers on the 328 do not hold an answer that a commit line can release. Of the 77 stored cap hits,
a forced commit at 12,000 tokens is right on 2; of the 184 answers over 8,000 tokens, 28 are right when forced against 40 when
left alone. So the cap hits are failures to solve, not failures to stop, and the tokens after 8,000 are productive for 16
problems. Hand read of 14 forced boxes at N 8,000: 4 right, 10 guesses unrelated to the last line of work. The token saving is
real: -1.5 points [-4.0, 0.9] for 15 % fewer tokens at N 12,000 (box).

Files: `jobs/commit_cue.py`, `analysis/commit1.py`, `results/commit1/base-01/` (readout.json, run.json, metrics.json,
examples.json). Raw rows: `runs/abaybektursun-1114-212437-d6d2/rows.jsonl` after `uv run tools/gpu.py get` (1,656 rows, 8 min on
an H100). Smoke: job abaybektursun-1114-212215-f08c. The RL model was not run: the spec asks for it only if H1 holds. Run:

```
uv run tools/gpu.py submit h100 --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.commit_cue --model base --commit $(git rev-parse HEAD)"
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.commit1 base <job>
```

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

## One axis or several? Item-level structure of every arm (MATH-500 n = 500, hard328 n = 328, laptop, board work-1aa34c, idea-1c8b73)

Question: do the partial routes toward the RL model fix the same problems or different ones? Answer: the same. On MATH-500 two
different arms are no more different from each other than two samples of one arm: the 618 pairs of different arms have a
mean excess union of -0.05 problems (z mean -0.04, sd 0.97) against +0.29 (z mean 0.17) for the 12 same-config pairs, and one
bilinear term added to the Rasch model gains nothing held out. Stacking two arms is predicted to add less than 1.0 point
(5.1 problems, the largest upper bound among the 7 pairs named in the spec) beyond what a second sample of an equally able arm
adds. No cross-arm stack is worth a GPU run as a complementarity bet. Spec, hypotheses and the amendments made after the
planted checks: `specs/SPEC_axis.md`. Code: `analysis/axis.py`; planted checks: `analysis/axis_test.py`.

Data. One 0/1 vector per arm, grader v3 (`score_v3` of `run_cell`), T 1.0 / top-p 1.0, attempt 0. MATH-500: 36 single-sample
arms (4 samples of base + cue, 4 of RL plain, 11 weight-difference cells, 10 Reward-content cells, 3 solved-examples cells with
n = 497, 4 WSP-1 cells) and 3 derived arms (base vote, base `tie_short`, RL vote). hard328: 7 single-sample arms.
`results/axis/<set>-01/manifest.json` gives each arm's job id, run folder, source path, commit and sha256; every right count
equals the committed `metrics.json` of its run folder. `vectors.json` holds the vectors. Raw rows of the cells that have no
committed per-problem file were read from `runs/<job id>/answers.jsonl`. Excluded (reason in the manifest): min-p and
self-review cells and the hard328 4-sample rows (raw rows in a teammate's Modal workspace, only totals committed), metaharness
reruns (no per-problem scores), T 0.6 cells, the n = 100 screens, RLN-4 T1/T2/T3 (S3).

Method. Excess union of a pair = problems right under A or B, minus the same count when B is permuted among problems of equal
rest score (the share of the other independent arms that are right: the Mantel-Haenszel test with the rest score as
difficulty). Bias and sd of the excess come from 200 matrices drawn from the fitted Rasch model. Positive = the arms fail on
different problems more than difficulty explains. "Fixed" = base + cue sample 0 wrong, arm right. A union is an oracle: it needs
the answer key, so it is the upper bound of any selector over the two answers, not a method.

| Pair (MATH-500) | Right A, B | Union (over best) | Excess, problems (sd), z | Fixed A, B, both (one-axis expectation) | Jaccard of fixed sets (expected) |
|---|---|---|---|---|---|
| base + cue, two samples (6 pairs; noise floor) | 405 to 418 | 445 to 454 (+34 to +39) | -3.0 to +3.0, z -1.21 to 1.18 | s1, s2: 40, 44, 30 (30.1) | 0.556 (0.558) |
| RL plain, two samples (6 pairs; noise floor) | 456 to 464 | 472 to 479 (+9 to +16) | -1.1 to +1.1, z -0.77 to 0.81 | s1, s2: 68, 67, 60 (59.6) | 0.800 (0.790) |
| theta 0.5 cue + Think-SFT cue | 452, 454 | 478 (+24) | +1.34 (1.58), 0.85 | 59, 65, 50 (50.7) | 0.676 (0.692) |
| theta 0.5 cue + Code-RL 3.1 cue | 452, 450 | 473 (+21) | +1.86 (1.62), 1.15 | 59, 60, 49 (49.7) | 0.700 (0.716) |
| theta 0.5 cue + RL-written examples (n 497) | 449, 435 | 464 (+15) | -1.45 (1.54), -0.94 | 59, 51, 45 (42.8) | 0.692 (0.637) |
| Think-SFT cue + RL-written examples (n 497) | 452, 435 | 474 (+22) | +0.28 (1.67), 0.17 | 65, 51, 44 (43.1) | 0.611 (0.590) |
| theta 0.25 cue + Think-SFT cue | 441, 454 | 476 (+22) | +0.58 (1.64), 0.35 | 51, 65, 44 (44.4) | 0.611 (0.621) |
| Code-RL 3.1 cue + Think-SFT cue | 450, 454 | 478 (+24) | -0.27 (1.52), -0.18 | 60, 65, 50 (50.2) | 0.667 (0.670) |
| Math 3.0 cue + Think-SFT cue | 448, 454 | 478 (+24) | -0.70 (1.62), -0.43 | 59, 65, 50 (49.9) | 0.676 (0.673) |
| Think-SFT cue + base vote over 4 (null not bias-corrected) | 454, 446 | 474 (+20) | -1.05 (1.16), -0.90 | 65, 43, 39 (39.0) | 0.565 (0.565) |
| theta 0.5 cue + base vote over 4 (null not bias-corrected) | 452, 446 | 467 (+15) | +0.23 (1.84), 0.13 | 59, 43, 40 (38.1) | 0.645 (0.597) |
| RL plain sample 0 + Think-SFT cue | 456, 454 | 476 (+20) | -0.76 (1.59), -0.48 | 58, 65, 52 (51.3) | 0.732 (0.715) |

- All 618 pairs of different arms: z mean -0.04, sd 0.97, range -3.80 to 2.83, 3 pairs (0.5 %) beyond |z| = 3 (0.3 % expected);
  the three are "alike" pairs (IF 3.0 cue with Math 3.0 cue -3.80, Math 3.0 cue with top-8 plain -3.70, RL sample 0 with
  theta 1.5 cue -3.04). No group of arms stands out: mean z is between -0.52 and 0.44 for every pair of groups (base samples,
  RL 3.1, theta blends, 3.0 checkpoints, examples in context, Think-SFT, controls), -0.00 for same-prompt pairs and -0.06
  for plain-with-cue pairs. The prediction in the spec that the prompt format is a second axis was wrong.
- Item model, held-out log-likelihood per cell (5 folds over 17,991 cells, nats): constant -0.4735, Rasch -0.2790, Rasch on
  data with arm labels shuffled within each problem -0.3689, Rasch plus one bilinear term -0.2790 (gain -3e-07 at ridge 10 on the bilinear
  term, where the term is shrunk to zero; -0.0142, -0.0357, -0.0565 at ridge 3, 1, 0.3, where it is free to fit; 95th
  percentile of the gain on 20 Rasch-simulated data sets 0). The 21 cue arms alone: -0.2409 for both. Arm ability explains 0.09 nats per
  cell, a second axis nothing.
- Same seed is not the same answers: the first 50 MATH-500 problems of base + cue sample 0, rerun with the same seed in another
  job, are scored differently on 6 problems (37 and 43 right). A same-seed rerun is a new sample.
- Unions (oracles): two different arms near 452 reach 473 to 478, inside the 472 to 479 of two RL samples; RL pass@4 is 482,
  base pass@4 467, any of the 29 non-RL single-sample arms 494. The largest union of two non-RL arms is Math 3.0 cue with
  Think-SFT plain, 482 (excess +1.0, z 0.62).
- Floor: 6 of 500 problems are solved by none of the 39 arms, RL's vote included (indices 103, 154, 264, 308, 340, 422:
  four geometry/precalculus, two intermediate algebra; the four stored RL answers to each are wrong maths, not grader misses). 0 problems are solved only by RL 3.1 arms. 13 problems are solved by
  no arm that is free of RL weights and RL output (base samples and votes, base-written examples, random controls, Think-SFT).
- One-axis prediction of a vote over 4 samples of an arm that has one sample (`one_axis_vote_prediction`: share of problems the
  stored vote gets right as a function of the Rasch per-sample probability): Think-SFT cue 471.5, theta 0.5 cue 469.9, RL cue
  473.5, theta 0.25 cue 464.3, against the stored RL vote 474 and base vote 446. Predicting each stored vote from the other
  family's curve misses by -6.5 (base) and +3.2 (RL) problems, so read these as +/- 7.

hard328 (7 arms, one sample each, no second sample of any arm): 21 pairs, z mean 0.30, sd 1.08, range -1.80 to 2.11; no
second axis in the item model (Rasch -0.3115 for both). The same-seed rerun of base + cue by a second person (164 and 160 right)
is scored differently on 42 of 328 problems and its union is 183 (+19), against +14 to +15 for base + cue with a theta blend
and +23 for theta 0.25 with theta 0.5. Floor: 90 of 328 solved by no arm; 13 solved only by the two RL arms, 7 of them by
one RL arm only. With two RL arms among seven and one sample each, no null for this count was computed.

Verdict. One axis: do not run a cross-arm stack (weight blend + vote of the base, Think-SFT + shots, and so on) to gain
complementary problems. If a vote is run, run it inside the most able reward-free arm. The job that tests the prediction above
(for the lead to decide; not submitted): the `sft1_cue` cell of WSP-1 with four samples,
`bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe interp --other think_sft --alpha 1.0 --rounding nearest --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label sft1 --prompt cue --set math500 --temperature 1.0 --top-p 1.0 --seed 182000000 --samples 4 --restarts 0 --commit <commit>`
(`wsp_edit` is on branch `claude/weight-space-programming-research-ddd44e`), then `analysis/day1_vote.py`. One axis predicts a
vote of 471.5 +/- 7 of 500; a vote above 479, or a vote over two Think-SFT and two theta 0.5 samples that beats the
four-sample Think-SFT vote by 5 problems or more, refutes it.

Limits. One sample per arm except base + cue and RL plain. The pair test has little power for one pair: a planted second axis
of 1.5 logits on 30 % of the problems gives a mean excess of 1.8 problems (z 0.64), 4 logits 4.8 problems (z 1.94); the item
model detects both (gain 0.0032 and 0.0271 nats per cell). So the claim is "no second axis as large as 1.5 logits on 30 % of
the problems shared by a group of arms", and per pair "excess below 5.1 problems", not "no difference at all". Votes cannot be
simulated from 0/1 data: pairs with a vote keep the uncorrected null, which is about 1.5 problems low. Planted checks
(`analysis/axis_test.py`, all pass): one axis gives pair z mean 0.09, sd 0.94, 0.2 % beyond 3 and no detection; two identical
arms give z -10.1. Grader v3 errors (hand reads in the weight-difference section) are shared across arms and count as difficulty.

Run folders `results/axis/math500-01/` and `results/axis/hard328-01/`: `run.json`, `manifest.json`, `vectors.json`,
`readout.json` (every pair's z in `pair_z_matrix`), `examples.json` (one floor problem and one problem both theta 0.5 cue and
Think-SFT cue fix, with the stored answers of the Day-1 #3 samples).

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

Day-1 #3, four samples with up to two restarts each, one job per model (about 10 M tokens, 2.1 to 2.3 h measured; `--hours 6`
because a killed job is not scored), then the readout (`specs/SPEC_day1_3.md`). On the 328: `--set hard328 --seed 3000000`.

```
uv run tools/gpu.py submit h100 --hours 6 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set math500 --temperature 1.0 --top-p 1.0 --seed 41000000 --samples 4 --restarts 2 --commit $(git rev-parse HEAD)"
uv run tools/gpu.py submit h100 --hours 6 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model rl --prompt plain --set math500 --temperature 1.0 --top-p 1.0 --seed 45000000 --samples 4 --restarts 2 --commit $(git rev-parse HEAD)"
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_vote --run runs/<base job> --out studies/rlneurons/results/day1_3/<set>_base_cue-<nn>
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_vote --run runs/<rl job> --out studies/rlneurons/results/day1_3/<set>_rl-<nn> --minus studies/rlneurons/results/day1_3/<set>_base_cue-<nn>/readout.json
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_vote_test
```

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
2. `jobs/run_cell.py` covers T1, T2, T3, the harder set and Day-1 #1 and #2 (run, see "Day-1 rows"). Day-1 #3 runs with
   `--samples` and `--restarts` (see "Day-1 #3").
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
