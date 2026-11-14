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
| `analysis/rln4_temp.py` | T2/T3 readout: temperature differences, accuracy and cap hits by RL-solution-length quartile, examples. |
| `analysis/rln4_t1_t2_items.py` | Per-problem T1 against T2 under grader v3; wrote `results/rln4/t1_t2_items-01/` (from commit `8b6a836`, unchanged). |
| `specs/SPEC5_map.md` | RLN-5 map spec: where the RL model still disagrees with the cued base; hypothesis H and its refutation rules; controls. |
| `jobs/rln5_map.py` | RLN-5 map job (inference only, team runner): both models over the stored T1 and T2 answers with teacher forcing; per-position shards and `checks.json` in `$OUT_DIR`. See "RLN-5 map". |
| `analysis/rln5_map_analyze.py` | RLN-5 map readout: reads `runs/<job-id>/`, writes `metrics.json` and `examples.json` (analysis a-e of SPEC5_map.md §6, the test of H). |
| `grader/rln4_grader_v3.py` | Rescores every saved MATH-500 cell with v1, v2, v3; writes `results/rln4/grader_v3/readout.json`. `CELLS` lists the S3 key of each cell. |
| `grader/rln4_grader_v3_test.py`, `grader/cases.json` | Grader v3 tests: 22 audited rows plus planted equal and unequal pairs. |
| `data/rln3/` | `math500.json` (500), `hard.json` (400 harder problems), `frozen.json` (models, revisions, seeds, caps, sha256 of the inputs). |
| `data/rln4/` | `frozen4.json` (models, revisions, cue ids, cells, seeds, cap, loop detector, stop times), `k.json` (78 K prefixes, 2.8 MB), `g.json`, `check.json`, `check_rl.json`, `math500.json`, `prompt_ids.json` (n13's tokenized MATH-500 prompts; also the RLN-3 input of that name). |
| `data/rln5/` | `map_inputs.json`: sha256 and size of the stored T1 and T2 answers that the map job reads from the Volume `iterate-runs` (`inputs/rln5/`). |
| `results/rln4/t1_t2_items-01/` | `per_problem.json` (500 rows: right and wrong for T1 and T2 under grader v3, token counts, cap hits, hand label `failure_type`), `metrics.json`, `notes.md`, `run.json`. |
| `results/rln5/map-01/` | RLN-5 map, full run: `run.json`, `metrics.json` (analysis a-e), `examples.json` (real items), `checks.json` (the job's controls), `tokenize_check.json`. |
| `results/rln3/` | `rln3_overlap.json` (per-problem overlap flags), `offline/` (prep checks and offline gate). |
| `results/rln4/` | `grader_v3/readout.json` (the final table), `modal_k-01/`, `modal_t2-01/`, `modal_t3-01/` (readouts, metrics, run records), `offline/`. |

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

Continuation test K (`results/rln4/modal_k-01/readout.json`, 78 of the 86 problems where the base with cue hit the cap at
T 0.6 and RL was right, SPEC4 §2; grader v1): from the RL model's prefix the base finishes 48 of 78; from its own prefix 23 of 78; fresh restart 38
of 78. Frozen label: "the base can finish from a sound prefix" (both counts at the threshold edge, 47 and 23).

Grader v1 to v3 moved 113 answers from wrong to right and 1 from right to wrong over the 9 cells (`flips_v1_to_v3`,
`flip_review`). The v1 numbers 57.2 (base) and 92.0 (RL) quoted in older notes are the n13 cells under v1 (286 and 460).

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

**The GPU path is untested.** Tested: the laptop dry run (stand-in engine, below) and a cpu job on the runner
(`abaybektursun-1114-123453-8c3d` and `abaybektursun-1114-124132-b234`: setup, prompts, grading of canned answers, files in `$OUT_DIR`). One H100 job
(`abaybektursun-1114-123728-8181`) got through setup, weight download and engine start (140 s for download and start together) and was cancelled on
instruction before any answer finished. No generated answer, score or time per problem from this entry point exists yet. The
first GPU run should be 10 problems of a cell with a known number (the T1 command with `--n 10`) and its rows read by hand.

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

Time estimate per full row, not measured with this entry point: earlier H100 runs of the same engine generated 1,415 tokens/s
(T3, `results/rln4/modal_t3-01/metrics.json`, 500 problems in 745 s) and 1,803 tokens/s (T2 on an H200,
`results/rln4/modal_t2-01/metrics.json`, 2.35 M tokens in 1,302 s). A row where every answer hits the 16,384 cap is
328 x 16,384 = 5.4 M tokens, about 1 h at 1,500 tokens/s; that is the upper bound for #1. For #2, the T 0.6 / top-p 0.95 cue row had 119 cap hits, so about 2 M tokens in capped answers plus about 1 M in the rest
(an estimate), about 35 min.
Add about 3 min for setup and engine start. `--hours 2` leaves room; the runner kills the job at `--hours`.

Day-1 #3 (restart and four-sample vote) is not runnable yet. Four samples: four `run_cell` jobs with seeds 10000 apart (the
RLN-3 rule seed + 10000 x sample + index) work today, but no script computes the vote (`rln4_lib.agree` is the equivalence
test to use). Restart: `run_cell` has no option to run only the problems that hit the cap in an earlier run, and no script
merges a restart into its parent row.

Laptop dry run (no vLLM, no weights; downloads only the tokenizer files):

```
uv run --no-project --with numpy --with math-verify==0.9.0 --with transformers==5.19.0 --with tokenizers==0.23.3 --with huggingface_hub --with jinja2 python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set math500 --temperature 1.0 --top-p 1.0 --seed 41000000 --n 10 --dry-run --out /tmp/rc --commit $(git rev-parse HEAD)
```

It must print 4 right, 3 cap hits of 10 (the stand-in serves right, wrong, cap hit in turn).

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
2. `jobs/run_cell.py` covers T1, T2, T3, the harder set and Day-1 #1 and #2, but its GPU path is untested (see "Day-1 cells on
   the team runner"). Day-1 #3 needs a vote script and a restart option.
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

- The harder set (328) is scored only for the base at T 0.6 (RLN-3 base-01, per `DIRECTION.md`); no readout file for it is in
  the source.
- Temperature and top-p are not separated (T 0.6 / top-p 0.95 against T 1.0 / top-p 1.0).
- No second model has read the grader v3 rescoring.
- RLN-3 rows for RL step 400 and the first release at T 0.6 are not scored (`DIRECTION.md`; board `knowledge-c3f1bf`).
- SPEC4 §0's accuracy and cap rate by RL-length quartile (2 % to 66 %, pass@3 97 / 96 / 84 / 47) are the coordinator's
  numbers; no script for them is in the source. `analysis/rln4_temp.py` computes quartiles for T2 and T3 only.

## Left out of the copy

RLN-1 and RLN-2 (neuron-statistics studies in the same source folder: `SPEC.md`, `SPEC2.md`, `label.py`, `overlap.py`,
`analyze2.py`, `explain/`, the `.npz` statistics, label JSONL files up to 82 MB): a different question. The `pg` launcher
(`infra/aws_pg/`), `pipeline.py`, and the rest of the modules that `hf_helpers.py` replaces.
