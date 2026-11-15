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
| `analysis/day1_join_shards.py`, `analysis/day1_join_shards_test.py` | Joins the shard runs of one cell (`studies/metaharness/jobs/shard_cell.py --shard k/N`) into one run folder under `runs/` that `day1_vote.py` and `day1_length_rules.py` load: rows unchanged, counts summed, shard job ids recorded. Refuses a shard that is not `done`, a missing or swapped shard, a shard of another cell, a missing row. See "Joining shard runs". With `--missing-shard k/N --missing-reason` it joins a cell that lacks one shard, on the set minus exactly that shard's positions, and marks the folder partial. The test file holds its planted cases, with inputs that must be refused. |
| `analysis/day1_length_rules_headline.py` | One table from the `day1_length_rules.py --fixed` run folders (one per model, each scored alone) and the `day1_vote.py` run folders of the same joined runs: single, the fixed rules, vote, pass@4; with the RL folders also RL minus base and the equal-tokens line over the fixed rules. Scores nothing itself. |
| `specs/day1_length_rules_chosen_prereg.json` | The `--fixed` file used on the 328: S = 2,000 and L = 12,000 from board idea-ecc123 and idea-3f3378 (posted before the hard328 four-sample jobs). Not written by `--choose`; its `source` and `caveats` fields say so. |
| `analysis/day1_hard328.py` | Day-1 #1 readout: the 328 at T 1.0 (four cells) beside the three T 0.6 cells, grader v3, per source, paired bootstrap, identical-text counts, the 50-problem check against T1. |
| `specs/DAY1_hard328_2026-11-14.md` | Day-1 #1 plan, written before launch: prediction, check rule, seeds, cost. |
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
| `results/day1_length_rules/` | Length rules on the 328, four samples per problem: `hard328_base-01/` (`day1_length_rules.py --fixed`, base alone: `run.json`, `metrics.json`, `per_problem.tsv`, `examples.json`), `hard328_headline_base-01/` (`day1_length_rules_headline.py`: the base table with vote and pass@4). RL folders do not exist yet. Partial, 246 of 328 problems, RL shard 2 missing: `hard328_partial246_base-01/`, `hard328_partial246_rl-01/` (each model alone, `--fixed`), `hard328_partial246_headline-01/` (both models, RL minus base, equal tokens); their vote folders are `results/day1_3/hard328_partial246_base_cue_s4r0-01/` and `results/day1_3/hard328_partial246_rl_plain_s4r0-01/`. |
| `results/day1_3/` | `day1_vote.py` readouts of joined four-sample runs: `hard328_base_cue_s4r0-01/` (`readout.json`, `examples.json`, `run.json`, `metrics.json` of the joined run with the shard job ids). |
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

### Harder 328: length rules and four-sample vote (board work-a992bd, sampling work-140e13)

The table below is base + cue on all 328. RL is scored on 246 of the 328 only (RL shard 2 was cancelled): see "Partial paired
comparison: 246 of 328 problems, RL shard 2 missing" below. Four samples per
problem, T 1.0 / top-p 1.0, seed 3000000, cap 16,384, no restarts, grader v3, n = 328. Rows: `runs/hard328_base_cue_s4_join-01`
(four shard jobs, "Raw answers"). Thresholds S = 2,000 and L = 12,000 were fixed before any hard328 four-sample row existed
(`specs/day1_length_rules_chosen_prereg.json`, commit a5e02fd, from board idea-ecc123 and idea-3f3378; not a `--choose` run;
idea-3f3378 gives its counts at 12,000 and says the cutoff is chosen on MATH-500). `--fixed` scores only the single row and
these three rules, once; no other setting of the grid was scored on the 328.

Instrument check: sample 0 of the joined base run gives 160 right, 67 cap hits, 9,168 tokens per problem, against 164, 77 and
9,345 in the single-sample cell with the same seeds (`results/day1/hard328_base_cue_t10-01/`): inside 164 +- 12. The cap hits
are 10 lower; samples 1 to 3 give 158, 160, 160 right and 65, 67, 64 cap hits (`results/day1_3/hard328_base_cue_s4r0-01/readout.json`,
`each_sample`). The cause of 77 against 64 to 67 is not checked.

| Base + cue, row | Right of 328 | % [Wilson 95 %] | Tokens per problem | Minus single, points [paired bootstrap 95 %] | Fixed | Broke |
|---|---|---|---|---|---|---|
| single (sample 0) | 160 | 48.8 [43.4, 54.2] | 9,168 | | | |
| D(2000) | 163 | 49.7 [44.3, 55.1] | 9,675 | +0.9 [0.0, +2.1] | 3 | 0 |
| R(12000) | 169 | 51.5 [46.1, 56.9] | 20,091 | +2.7 [-0.3, +5.8] | 17 | 8 |
| D(2000)+R(12000) | 172 | 52.4 [47.0, 57.8] | 20,597 | +3.7 [+0.6, +7.0] | 20 | 8 |
| vote@4 | 179 | 54.6 [49.2, 59.9] | 36,721 | +5.8 [+3.0, +8.8] | 21 | 2 |
| pass@4 (any of four right; upper bound of the vote) | 205 | 62.5 [57.1, 67.6] | 36,721 | +13.7 [+10.1, +17.7] | 45 | 0 |

Artifacts: rule rows `results/day1_length_rules/hard328_base-01/metrics.json` (`per_problem.tsv`, `examples.json`: one
problem each rule fixed and one it broke; D(2000) broke none); vote and pass@4 `results/day1_3/hard328_base_cue_s4r0-01/readout.json`
(its restart row equals its single row because the jobs ran with no restarts); the whole table
`results/day1_length_rules/hard328_headline_base-01/metrics.json`.

- Why D(2000) does little: 47 of the 328 first answers finish within 2,000 tokens and 6 of them are wrong (263 of 500 and 13
  on MATH-500). The rule fixed 3 of the 6.
- Why R(12000) costs 2.2 times the single row: 140 of the 328 first answers are longer than 12,000 tokens (11 right, 129
  wrong; 67 are cap hits). Each stop costs 12,000 tokens and the next sample is often long again.
- Raw answers read (13 problems: 3 D(2000) fixed, 4 R(12000) fixed, 6 R(12000) broke). D(2000) fixed: the first answer is
  short and wrong (one off-topic text with no answer, one unboxed `x = 8` for gold 1000, one boxed 7 for gold 6) and the next
  two samples agree on the gold. R(12000) fixed: a finished wrong answer of 12,000 to 15,000 tokens is replaced by a right
  one; in 2 of the 4 the right answer came only from sample 3 after three stops (51,000 tokens). R(12000) broke: 7 of the 8
  are finished right answers of 12,000 to 16,384 tokens that the rule discards for a shorter wrong sample; 1 is a cap hit
  that had extracted the right answer.
- Equal tokens (provisional): the budget is RL's single row. The RL four-sample rows are not scored, so the single-sample RL
  cell of the same seeds stands in: 9,316 tokens per problem, 206 right (`results/day1/hard328_rl_plain_t10-01/`). No fixed
  rule of the base is within it (D(2000) is 359 tokens above). At equal tokens the base is its single row: 160 against 206,
  -14.0 points, unpaired normal interval [-21.5, -6.5] (formula of `day1_rows.unpaired`, by hand). The paired number needs
  the RL lines of "Joining shard runs".
- Hypotheses of `specs/SPEC_day1_length_rules.md` on the 328, base part: H1 refuted (D(2000) +0.9 points, interval includes
  0, fixed minus broke 3 < 8, and 9,675 tokens is above the stand-in RL single row); H2 refuted (R(12000) interval includes
  0, and 20,091 tokens against 9,168 single); H3 not refuted so far (no base rule within the budget; even vote@4 at 36,721
  tokens, 179, is below RL's 206). The RL parts of H1 and H2 and the paired interval of H3 are not checked on the 328; on 246 of them see the next
  section.

#### Partial paired comparison: 246 of 328 problems, RL shard 2 missing (board work-a992bd)

Both models on the same 246 problems: positions 0, 1 and 3 mod 4 of the 328. RL shard 2 of 4 (`sameraslan-1114-145306-26e0`)
hung after a container restart and was cancelled with about half its rows. None of its rows is used: a problem finishes late
when its answer is long, so its finished rows are a biased sample. Base shard 2 (`sameraslan-1114-145246-73ad`, done) is left
out so that the comparison is paired. The 82 missing problems are listed in `joined_from.missing` of
`results/day1_3/hard328_partial246_rl_plain_s4r0-01/metrics.json`. Settings as above: four samples, T 1.0 / top-p 1.0, seed
3000000, cap 16,384, no restarts, grader v3, S = 2,000 and L = 12,000 from `specs/day1_length_rules_chosen_prereg.json`,
`--fixed`, each model scored once. The subset is fixed by shard position (which job failed), by no score. Its numbers are
numbers of the 246; the full 328 needs a rerun of RL shard 2.

Instrument check, on the subset, before any rule was read: RL sample 0 gives 148 of 246 = 60.2 %, 15 cap hits, 9,362 tokens
per problem. The single-sample RL cell with the same seeds has only its totals in the repo (206 of 328 = 62.8 %, 20 cap hits,
9,316 tokens; `results/day1/hard328_rl_plain_t10-01/`): 60.2 is inside 62.8 +- 6, and 20 cap hits of 328 scale to 15 of 246.
That cell's three example rows (problems 0, 29, 62) have the same seed, score and first 60 characters as sample 0 here. Base
sample 0 on the subset: 123 of 246 = 50.0 %, 43 cap hits (160 of 328 = 48.8 % on the full set). Samples 0 to 3 give 148, 156,
148, 154 right for RL and 123, 120, 120, 122 for the base.

Right of 246, % [Wilson 95 %], generated tokens per problem; differences in points [paired bootstrap 95 %, 5,000 resamples]:

| Row | Base + cue | Base tokens | Base minus its single | RL plain | RL tokens | RL minus its single | RL minus base, same row |
|---|---|---|---|---|---|---|---|
| single (sample 0) | 123, 50.0 [43.8, 56.2] | 9,065 | | 148, 60.2 [53.9, 66.1] | 9,362 | | +10.2 [+5.7, +14.6] |
| D(2000) | 126, 51.2 [45.0, 57.4] | 9,529 | +1.2 [0.0, +2.8] | 148, 60.2 [53.9, 66.1] | 9,461 | 0.0 [0.0, 0.0] | +8.9 [+4.5, +13.4] |
| R(12000) | 130, 52.8 [46.6, 59.0] | 19,616 | +2.8 [-0.4, +6.1] | 156, 63.4 [57.2, 69.2] | 18,748 | +3.3 [0.0, +6.5] | +10.6 [+6.1, +15.0] |
| D(2000)+R(12000) | 133, 54.1 [47.8, 60.2] | 20,080 | +4.1 [+0.4, +7.7] | 156, 63.4 [57.2, 69.2] | 18,914 | +3.3 [0.0, +6.5] | +9.3 [+5.3, +13.4] |
| vote@4 | 138, 56.1 [49.8, 62.2] | 36,478 | +6.1 [+2.8, +9.4] | 161, 65.4 [59.3, 71.1] | 36,970 | +5.3 [+2.4, +8.1] | +9.3 [+5.3, +13.4] |
| pass@4 (upper bound of the vote) | 157, 63.8 [57.6, 69.6] | 36,478 | +13.8 [+9.8, +18.3] | 175, 71.1 [65.2, 76.4] | 36,970 | +11.0 [+7.3, +15.0] | +7.3 [+3.7, +11.4] |

Fixed / broke against the model's single row: base D(2000) 3 / 0, R(12000) 12 / 5, both 15 / 5, vote 17 / 2; RL D(2000) 0 / 0,
R(12000) 13 / 5, both 13 / 5, vote 13 / 0.

Artifacts: the whole table, RL minus base and the equal-tokens block `results/day1_length_rules/hard328_partial246_headline-01/metrics.json`;
rule rows per model `results/day1_length_rules/hard328_partial246_base-01/` and `results/day1_length_rules/hard328_partial246_rl-01/`
(`metrics.json`, `per_problem.tsv`, `examples.json`: one problem each rule fixed and one it broke, with the real text ends and
scores); vote and pass@4 `results/day1_3/hard328_partial246_base_cue_s4r0-01/readout.json` and
`results/day1_3/hard328_partial246_rl_plain_s4r0-01/readout.json`. Jobs: base shards 0, 1, 3 `sameraslan-1114-145237-d124`,
`sameraslan-1114-145241-fee9`, `sameraslan-1114-145251-9228`; RL shards 0, 1, 3 `sameraslan-1114-145256-f5ac`,
`sameraslan-1114-145301-e465`, `sameraslan-1114-145311-d31f`. Commands: "Joining shard runs".

- Equal tokens, budget = RL single, 9,362 tokens per problem. (a) No fixed rule of the base is within the budget: D(2000), the
  cheapest, costs 9,529 (167 above). At equal tokens the base is its single row: 123 against 148, -10.2 points [-14.6, -5.7].
  (b) The same rule for both models is then the single row: RL minus base +10.2 [+5.7, +14.6]. Under D(2000), the nearest
  rule above the budget, RL minus base is +8.9 [+4.5, +13.4]. (c) Base vote@4 against RL single: 138 at 36,478 tokens against
  148 at 9,362 tokens, -4.1 points [-8.5, +0.4]; the base's vote spends 3.9 times the tokens and its interval includes 0.
- H1 refuted on the subset, on all three conditions: base D(2000) +1.2 points with an interval that includes 0, fixed minus
  broke 3 < 8, and 9,529 tokens is above RL single's 9,362. Its RL part holds: D(2000) adds 0.0 points to RL (12 of RL's
  first answers finish within 2,000 tokens and none is wrong; the base has 33, 5 wrong).
- H2 refuted on the subset: base R(12000) +2.8 points, interval [-0.4, +6.1] includes 0, at 19,616 tokens against 9,065 for
  its single row (2.2 times). RL gains about as much, +3.3 [0.0, +6.5], at 18,748 tokens (2.0 times); its interval also
  touches 0.
- H3 not refuted on the subset: the base at equal tokens (its single row) is 10.2 points below RL single and the paired
  interval [-14.6, -5.7] excludes 0. With 3.9 times the tokens (vote@4) the base is within 4.1 points and the interval
  includes 0.
- Why R(12000) costs twice the single row for RL: 93 of RL's 246 first answers are longer than 12,000 tokens (15 right, 78
  wrong; 15 are cap hits); the base has 101 (7 right, 94 wrong). The rule stopped 212 RL samples and 240 base samples.
- Raw answers read (RL, R(12000): 4 problems it fixed and 4 it broke, of 13 and 5; counts over all 18). Fixed: sample 0 is a
  cap hit in 5 and a finished wrong answer above 12,000 tokens in 8 (problem 75: boxed 234 for gold 73 at 12,417 tokens, then
  sample 1 boxed 73 at 7,425; problem 65: cap hit inside a determinant, then sample 1 boxed 104 = gold). The right answer came
  from sample 1 in 8, sample 2 in 1 and sample 3 after three stops in 4. Broke: all 5 are finished right answers of 12,515 to
  15,713 tokens that the rule discards (problem 181: boxed 63 = gold at 13,688 tokens; samples 1 to 3 are all longer than
  12,000 and sample 3, run in full, boxed 41). In 4 of the 5 the answer fell to sample 3; in problems 267 and 300 sample 1 was
  right too but was also stopped at 12,000.
- Not checked: the 82 problems of shard 2 for RL; whether the 246 give the same differences as the 328 (the base's single row
  is 50.0 % on the 246 and 48.8 % on the 328); a per-problem comparison of sample 0 against the single-sample RL cell (only
  its totals and three example rows are in the repo); the MATH-500 `--choose` run.

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
the token accounting and the hypotheses are in `specs/SPEC_day1_length_rules.md`. Numbers: the base on the 328, under
"Harder 328: length rules and four-sample vote"; both models on 246 of the 328, under "Partial paired comparison: 246 of 328
problems, RL shard 2 missing"; no MATH-500 number exists yet.

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

### Joining shard runs (laptop, no GPU)

A cell sampled in N shards (`studies/metaharness/jobs/shard_cell.py --shard k/N`, one job per shard) is joined into one run
folder under `runs/` (not committed) before any readout. Shard folders are given in shard order:

```
uv run tools/gpu.py get <job-id>          # once per shard job, gives runs/<job-id>/
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_join_shards --out runs/<name> runs/<job of shard 0> runs/<job of shard 1> ... runs/<job of shard N-1>
```

It prints sample 0's right count and cap hits (the instrument check against the single-sample cell with the same seeds). The
joined `metrics.json` has `job_id` = `join:` + the shard job ids, and `joined_from.shards` with each shard's job id, counts,
GPU and times. Only hard328 is supported (the order of its problem indices is written in the script).

A cell that lacks one shard is joined only with `--missing-shard k/N --missing-reason "<why>"` and the other N - 1 folders in
shard order. The script asserts that exactly N - 1 folders are given, that each is `done` and holds exactly its own positions
with every sample, and that the joined problems are the set minus exactly positions k, k+N, .... The joined folder says it is
partial in `PARTIAL.json` (missing positions, their problem indices, the reason), in `metrics.json` (`config.partial`,
`joined_from.missing`) and in `job_id` (`join-partial(missing k/N):...`); `config.n_problems` is the number joined. Join the
other model with the same `--missing-shard` to put both on the same problems. Without the flags a missing shard is refused.
Test (planted rows, no network; includes inputs that must be refused):

```
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_join_shards_test
```

The 328 as run on 2026-11-14 (`--samples 4`, no restarts; job ids under "Raw answers"):

```
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_join_shards --out runs/hard328_base_cue_s4_join-01 runs/sameraslan-1114-145237-d124 runs/sameraslan-1114-145241-fee9 runs/sameraslan-1114-145246-73ad runs/sameraslan-1114-145251-9228
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_join_shards --out runs/hard328_rl_plain_s4_join-01 runs/sameraslan-1114-145256-f5ac runs/sameraslan-1114-145301-e465 runs/sameraslan-1114-145306-26e0 runs/sameraslan-1114-145311-d31f
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_vote --run runs/hard328_base_cue_s4_join-01 --out studies/rlneurons/results/day1_3/hard328_base_cue_s4r0-01
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_vote --run runs/hard328_rl_plain_s4_join-01 --out studies/rlneurons/results/day1_3/hard328_rl_plain_s4r0-01 --minus studies/rlneurons/results/day1_3/hard328_base_cue_s4r0-01/readout.json
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_length_rules --base runs/hard328_base_cue_s4_join-01 --out studies/rlneurons/results/day1_length_rules/hard328_base-01 --fixed studies/rlneurons/specs/day1_length_rules_chosen_prereg.json
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_length_rules --rl runs/hard328_rl_plain_s4_join-01 --out studies/rlneurons/results/day1_length_rules/hard328_rl-01 --fixed studies/rlneurons/specs/day1_length_rules_chosen_prereg.json
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_length_rules_headline --rules-base studies/rlneurons/results/day1_length_rules/hard328_base-01 --vote-base studies/rlneurons/results/day1_3/hard328_base_cue_s4r0-01 --out studies/rlneurons/results/day1_length_rules/hard328_headline_base-01
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_length_rules_headline --rules-base studies/rlneurons/results/day1_length_rules/hard328_base-01 --vote-base studies/rlneurons/results/day1_3/hard328_base_cue_s4r0-01 --rules-rl studies/rlneurons/results/day1_length_rules/hard328_rl-01 --vote-rl studies/rlneurons/results/day1_3/hard328_rl_plain_s4r0-01 --out studies/rlneurons/results/day1_length_rules/hard328_headline-01
```

State on 2026-11-15: the base lines (1, 3, 5, 7) have run. The RL lines (2, 4, 6, 8) have not and cannot: RL shard 2
(`sameraslan-1114-145306-26e0`) hung after a container restart (164 of 328 rows, no output since 2026-11-14 23:52:32 UTC) and
is `cancelled` in `gpu.py ls`. They need a rerun of that shard as a new job.

Partial, 246 of 328 problems, RL shard 2 missing (both models on positions 0, 1, 3 mod 4; `R` is the reason text, see
`PARTIAL.json` of each joined folder and `config.partial` in `results/day1_3/hard328_partial246_*/metrics.json`):

```
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_join_shards --out runs/hard328_rl_plain_s4_partial246_join-01 --missing-shard 2/4 --missing-reason "$R" runs/sameraslan-1114-145256-f5ac runs/sameraslan-1114-145301-e465 runs/sameraslan-1114-145311-d31f
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_join_shards --out runs/hard328_base_cue_s4_partial246_join-01 --missing-shard 2/4 --missing-reason "$R" runs/sameraslan-1114-145237-d124 runs/sameraslan-1114-145241-fee9 runs/sameraslan-1114-145251-9228
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_vote --run runs/hard328_base_cue_s4_partial246_join-01 --out studies/rlneurons/results/day1_3/hard328_partial246_base_cue_s4r0-01
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_vote --run runs/hard328_rl_plain_s4_partial246_join-01 --out studies/rlneurons/results/day1_3/hard328_partial246_rl_plain_s4r0-01 --minus studies/rlneurons/results/day1_3/hard328_partial246_base_cue_s4r0-01/readout.json
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_length_rules --base runs/hard328_base_cue_s4_partial246_join-01 --out studies/rlneurons/results/day1_length_rules/hard328_partial246_base-01 --fixed studies/rlneurons/specs/day1_length_rules_chosen_prereg.json
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_length_rules --rl runs/hard328_rl_plain_s4_partial246_join-01 --out studies/rlneurons/results/day1_length_rules/hard328_partial246_rl-01 --fixed studies/rlneurons/specs/day1_length_rules_chosen_prereg.json
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_length_rules_headline --rules-base studies/rlneurons/results/day1_length_rules/hard328_partial246_base-01 --vote-base studies/rlneurons/results/day1_3/hard328_partial246_base_cue_s4r0-01 --rules-rl studies/rlneurons/results/day1_length_rules/hard328_partial246_rl-01 --vote-rl studies/rlneurons/results/day1_3/hard328_partial246_rl_plain_s4r0-01 --out studies/rlneurons/results/day1_length_rules/hard328_partial246_headline-01
```

## Raw answers

One JSONL row per answer (for RLN-4 cells: prompt index, seed, text, token counts, cap hit, loop flags, extracted answer, v1
and v2 scores) in the owner's bucket, `s3://pg-lineage-769063704696/results/rlneurons/r3/` (RLN-3: `base-01/`, `s2800-01/`, `fr-01/`,
`s0400_s0100-01/`, `inputs/`) and `.../r4/` (RLN-4: `base_rl-02/`, `modal_k-01/`, `modal_t2-01/`, `modal_t3-01/`,
`inputs/`), plus the n13 cells under `s3://pg-lineage-769063704696/results/next_n13/s3gate-03/`. Not copied here.
`results/rln4/grader_v3/readout.json` `files` gives the sha256 of each cell file used for the table.

The 328 with four samples per problem (`--samples 4`, no restarts, T 1.0 / top-p 1.0, seed 3000000, commit 34a8ccd; board
work-140e13): eight shard jobs on sameraslan's Modal workspace, `answers.jsonl` in each job's `$OUT_DIR` (`uv run
tools/gpu.py get <job-id>` by that workspace's owner; teammates cannot read it). Base + cue, shards 0 to 3:
`sameraslan-1114-145237-d124`, `sameraslan-1114-145241-fee9`, `sameraslan-1114-145246-73ad`, `sameraslan-1114-145251-9228`.
RL, plain prompt, shards 0 to 3: `sameraslan-1114-145256-f5ac`, `sameraslan-1114-145301-e465`,
`sameraslan-1114-145306-26e0`, `sameraslan-1114-145311-d31f`. The joined folders `runs/hard328_base_cue_s4_join-01/` and
`runs/hard328_rl_plain_s4_join-01/` are rebuilt from them with `analysis/day1_join_shards.py` ("Joining shard runs").
RL shard 2 (`sameraslan-1114-145306-26e0`) was cancelled and its rows are not used; `runs/hard328_rl_plain_s4_join-01/` does
not exist. The partial folders `runs/hard328_base_cue_s4_partial246_join-01/` and `runs/hard328_rl_plain_s4_partial246_join-01/`
hold shards 0, 1 and 3 of each model (246 problems).

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
