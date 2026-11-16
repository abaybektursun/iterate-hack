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
| `specs/SPEC_wsp1.md` | WSP-1 spec: anatomy of the RL-Math, RL-Code and Think-SFT weight deltas, then edited-weight cells. Job `jobs/wsp_delta_anatomy.py`, results `results/wsp1/`. |
| `specs/SPEC_wsp2.md` | WSP-2 spec: a hand-written key-value edit of layer 31 `mlp.down_proj` that writes the opening cue, built with no RL weights, and its random-value control. Job `jobs/wsp_handedit.py`, results `results/wsp2/`. |
| `jobs/wsp_handedit.py` | WSP-2 job: computes the edit from the base model's own activations, checks it on held-out prompts, writes the edited model directory for `run_cell.py --model-path` and `handedit.json` (`--control` for random values, `--selftest` for the planted checks). |
| `specs/SPEC4.md` | RLN-4 spec: T1 (cue, T 1.0), continuation test K, T2 (RL, T 1.0), T3 (plain base, T 1.0), G, R1; Modal deviations; grader v3. |
| `specs/SPEC_fresh.md`, `specs/fresh_jobs.txt` | Fresh held-out set: cutoffs with sources, selection rules, hypotheses, predictions; the 12 job commands. |
| `data/fresh/`, `prep/fresh_prep.py`, `jobs/run_fresh.py` | `fresh2026_v1.json`: 136 competition problems published in 2026 (AIME, HMMT Feb and Nov), the transcribed PDF problems, the prep script, and `run_cell` with `--set fresh2026`. |
| `specs/SPEC_drift.md`, `analysis/drift.py`, `analysis/drift_test.py`, `analysis/drift_read.py` | Drift: label-free signs in a sample's text per token position (switch to a non-Latin script, repeated 50-token windows, rule A on the prefix, "wait", restart phrases), planted tests, and the readout Q1 to Q4 with the stop-at-first-sign replay. Results `results/drift/`. |
| `analysis/fresh_read.py`, `analysis/fresh_sft_overlap.py` | Readout of the three models on the fresh set; scan of the Think-SFT training data for the fresh set. |
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
| `analysis/rate.py`, `analysis/rate_test.py`, `specs/SPEC_rate.md` | Exchange-rate table: each arm's ability shift in logits, tokens and training signal; leave-one-arm-out transfer to the 328; predictions filed before held-out cells were read. Outputs `results/rate/`. |
| `analysis/hazard.py`, `analysis/hazard_test.py`, `specs/SPEC_hazard.md` | Slip-hazard law: hazard-link item model against the Rasch logit model held out, hazard ratio of every arm and its constancy over difficulty, transfer to the 328, chain length and independence of the 4 samples, filed predictions. Outputs `results/hazard/`. |
| `analysis/seen.py`, `analysis/seen_test.py`, `specs/SPEC_seen.md` | Seen against unseen: the 72 harder problems in the RL training prompts against 130 source-matched unseen ones, four arms, 4 samples; D = (RL - control) seen minus unseen. Sets `run_cell --set hard72`, `--set hardmatch`. Outputs `results/seen/`. |
| `analysis/profile.py`, `analysis/profile_test.py`, `specs/SPEC_profile.md` | Difficulty profiles of Think-SFT and RL: error reduction by difficulty bin with difficulty defined without the arms compared, profile contrast against same-arm and one-axis noise floors, 2PL against Rasch held out, unions, cap hits by level, filed predictions for Think-SFT on hard328. Outputs `results/profile/`; input `data/profile/math500_meta_v1.json`. |
| `lib/egate.py`, `jobs/egate_cell.py`, `analysis/egate.py`, `specs/SPEC_egate.md` | Entropy-gated temperature: a vLLM logits processor that lowers the temperature only at positions chosen by next-token entropy, at random, or outside the stretch after a repeat; the multi-arm job; the readout. Outputs `results/egate/`. |
| `jobs/delta_sum.py`, `analysis/transplant.py`, `analysis/cap32_m2.py`, `specs/SPEC_transplant.md` | Delta transplant: writes host + a (donor - base) for three fine-tunes of one base (Think-SFT + a times the RL-Math delta, or matched noise), and the readout against the stored Think-SFT and RL samples. Outputs `results/transplant/`. |
| `jobs/delta_align.py` | Two weight changes compared tensor by tensor (norms, cosine, share of each inside the other's top-8 singular directions). Weights only. Writes `$OUT_DIR/delta_align.json`. |
| `analysis/transplant_restart.py` | M(2) at cap 32,768 (seed 3,000,000) counted at both caps, and chains over stored 16,384 samples: the answer of the first sample that did not hit the cap. Writes `results/transplant/<run>/readout.json`. |
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
| `analysis/rln4_t1_t3_items.py` | Per-problem T3 (base, plain, T 1.0) and T1 (base, cue, T 1.0) under grader v3, with the extracted answers and the start of each answer; wrote `results/rln4/t1_t3_items-01/` (224 and 410 of 500, as in `grader_v3/readout.json`; the cue turns 209 problems right and 23 wrong). |
| `analysis/anatomy.py` | Gap anatomy from the Day-1 #3 four-sample runs (laptop): joint k-of-4 table, held-out-sample decomposition, subject and level, error types, tokens, divergence proxy, `pool_k_le3.json`. See "Gap anatomy". |
| `analysis/anatomy_judge.py` | Slip against wrong plan: `prep` draws the items and the two controls and writes blind batches; `score` reads the judges' labels (agreement, controls, first wrong step). |
| `specs/SPEC_checks.md`, `analysis/checks.py` | Checks or per-step error: checking markers per 1,000 tokens in the four-sample texts (`stats`), blind judge batches for check events (`prep`, `score`). Results `results/checks/`. See "Checks or per-step error". |
| `tools/finding_rl_reliability.py` | The public page of "Gap anatomy" and "Checks or per-step error", served at `/finding/rl-reliability`: the joint k-of-4 table as columns, with a switch from problems to share of the gain. Its numbers are read from `results/anatomy/math500-01/readout.json` and `results/checks/`. |
| `tools/finding_opening_cue.py` | The public page of the opening cue on MATH-500 ("Established numbers"), served at `/finding/opening-cue`: the cue's tokens at the start of a real answer, one dot per MATH-500 problem with a switch from Base to Base + cue, and RL as a marked level; a click on a dot shows the problem and the start of both answers. Its numbers are read from `results/rln4/grader_v3/readout.json` (cells `base_plain_1.0`, `base_opener_1.0`, `rl_1.0`) and `results/day1_3/`, its dots from `results/rln4/t1_t3_items-01/per_problem.json` (run the file to check them). |
| `tools/finding_restart_on_cap.py` | The public page of the restart of cut-off answers ("Established numbers" and "Day-1 #3"), served at `/finding/restart-on-cap`: the 500 answers as marks, with a switch from no restart to restart. Its numbers are read from `results/rln4/grader_v3/readout.json`, `results/day1_3/` and `results/commit1/base-01/readout.json`. |
| `tools/finding_vote_over_four.py` | The public page of "Day-1 #3" and "Label-free selector", served at `/finding/vote-over-four`: the base model and the RL model as two bars, with a switch from one sample to the vote over four. Its numbers are read from `results/day1_3/math500_base_cue-01/readout.json`, `results/day1_3/math500_rl-01/readout.json` and `results/selector/math500_base_cue-01/readout.json`. |
| `tools/finding_equal_token_frontier.py` | The public page of "Token frontier", served at `/finding/equal-token-frontier`: right answers against tokens per problem for the 24 rules on both models, one RL sample as a level line, a token budget the reader drags (the best base rule within it and its distance to one RL sample, with the interval) and a strip of the 500 problems. Its numbers are copied from `results/frontier/math500-01/` (readout.json, frontier.json, per_problem.json, examples.json); `python3 tools/finding_equal_token_frontier.py` checks the copy. |
| `tools/finding_cue_on_code.py` | The public page "The cue beyond math" ("Code pair" and "Outside math and code"), served at `/finding/cue-on-code`: MATH-500, the 538 code problems and the 500 general questions side by side, one mark per item, with a switch Base, Base + cue, RL, Think-SFT + cue. Only the MATH-500 marks are real problems; code and general marks fill by count, because those runs commit counts only. The general numbers are a checked copy of `results/ood1/readout.json` (branch `ali/ood`, 99b2d5d). |
| `tools/finding_rl_edge_comes_early.py` | The public page of "Prefix hand-off", served at `/finding/rl-edge-comes-early`: one answer as a bar of text cut at 25, 50 or 75 %, the 183 problems as dots, a switch for who writes the start and a draggable cut; its large number is the share of the gap between the two models alone that the hand-off closes (81 % at 50 %, 29 of 36 problems; 65 %, 13 of 20, on the 155 chosen without the base's own answers). Its numbers and dots are read from `results/handoff/base-01/rows.jsonl`, `rl-01/rows.jsonl` and `readout-01/readout.json` (run the file to check them). |
| `tools/finding_a_quarter_of_rl.py` | The public page of "Weight-difference line" (MATH-500 and the 328), served at `/finding/a-quarter-of-rl`: right answers against a for base + a (RL - base) with the cue, each point with its paired 95 % interval, the random change and Code-RL as reference marks, a slider on a that snaps to the measured values, a switch between MATH-500 and the 328, and one dot per problem. Its numbers are read from `results/day1_wdiff/readout.json`, `results/day1_wdiff328/readout.json`, `results/axis/math500-01/vectors.json`, `results/axis/hard328-01/vectors.json` and `results/rln4/t1_t2_items-01/per_problem.json` (run the file to check them). |
| `tools/finding_one_difficulty_axis.py` | The public page of "One axis or several?", served at `/finding/one-difficulty-axis`: the 36 single-sample arms as rows against the 500 problems in one difficulty order, two arms the reader picks (or "Any pair" through the 618 pairs of different arms), their union against the difficulty-matched prediction, and all pairs' excess as a dot histogram with the 12 same-arm pairs. Its marks and pair excesses are copied from `results/axis/math500-01/` (vectors.json, readout.json); `PYTHONPATH=. uv run --no-project --with numpy python tools/finding_one_difficulty_axis.py` recomputes the pair table with `analysis/axis.py` and checks the copy against `pair_z_matrix`. |
| `tools/finding_imitation_beats_rl.py` | The public page of "Think-SFT with the cue under the vote rules", served at `/finding/imitation-beats-rl`: the base with the cue, RL and Think-SFT with the cue as three rows of the same problems in one order, with a switch from one sample (four dots per problem) to the vote over four (the dots merge) and to MATH-500, Think-SFT minus RL with its paired interval, and every answer of a clicked problem. Its marks are copied from the rows.jsonl of `results/thinkvote/hard328_sft1_cue_s4-01/`, `math500_sft1_cue_s4-01/` and `results/day1_3/` (base and RL), its numbers from `results/thinkvote/scored-01/readout.json` and the frontier readouts, the training-overlap flags and the vote without the 6 flagged problems (235 against 215 of 322) from `results/wsp1/sft_overlap-03/`, the long-answer counts from `results/riskcov/hard328-01/`; `PYTHONPATH=. uv run --no-project --with numpy --with math-verify==0.9.0 python tools/finding_imitation_beats_rl.py` recomputes the votes and checks the copy. |
| `tools/finding_cut_off_is_unfinished.py` | The public page of "Token cap 32,768 on the 328", served at `/finding/cut-off-is-unfinished`: one bar per answer, as long as its generated tokens, one slider over the tokens allowed (16,384 to 32,768), and a switch between Think-SFT + cue, RL and Base + cue. Reads `results/cap32/readout.json`, `results/cap32/rows-01/` and `rows-02/`; running the file checks it (command in its docstring). |
| `tools/finding_how_much_of_the_gap.py` | The public page of "Configurations on the 328 with committed rows, in one table" (it still names the section by its former title, "All configurations on the 328 in one table", and shows the rows of hard328-01 only), served at `/finding/how-much-of-the-gap`: every configuration as one row on the axis "share of the gap closed" (0 % Base + cue, 100 % RL) with its interval, and a switch between one sample, the vote over 4 samples and the tokens of one RL sample. Its DATA is a checked copy of `results/table/hard328-01/table.json`; `uv run tools/finding_how_much_of_the_gap.py` checks it. |
| `tools/finding_the_finish_dial.py` | The public page of "The finish dial" (xreward), served at `/finding/the-finish-dial`: the 328 problems as marks in three columns (finished right, finished wrong, cut off) and one slider over the size of the 8 RL directions, with the random directions as a switch. Its DATA is a checked copy of `results/xreward/edits/readout.json`; the replication of `results/day1_3/hard328_top8x1.5_cue_s4-01/` is stated in its panel. |
| `tools/finding_rl_change_on_imitation.py` | The public page of "Delta transplant", served at `/finding/rl-change-on-imitation`: the 328 problems as marks in three bands and one slider over a in Think-SFT + a × (RL − base), with the noise control as a switch. Its DATA is checked against `results/transplant/hard328-01/` by running the file (command in its docstring). |
| `tools/finding_no_early_warning.py` | The public page of the drift measurement, served at `/finding/no-early-warning`: the AUROC of six text signs for a failing Think-SFT sample, with its interval, at token 4,000, 8,000 and 12,000, against a planted sign (0.807), and the tokens saved by the stop rule (0.8 %). Reads `results/drift/{describe,predict,stop}-01/`; running the file checks it. |
| `tools/finding_rl_directions_move_activations.py` | The public page of the xshift measurement, served at `/finding/rl-directions-move-activations`: one mark per weight edit (28), its weight norm against the shift of the layer-24 residual stream, with views for the direction of the shift and for cut-off answers (the refuted prediction). Reads `results/xshift/run-01/readout.json`; running the file checks it. |
| `tools/finding_two_jobs_in_the_edit.py` | The public page of the depth and rank split of the 1.5x edit, served at `/finding/two-jobs-in-the-edit`: each part of the edit as one mark on right answers against cut-off answers, by layer band and by direction, with the code pair where the depth split was refuted. Reads `results/xreward/depth3/readout.json`, `xreward/edits/readout.json` and `xreward/code_depth/readout.json`; running the file checks it. |
| `tools/finding_rl_avoids_the_slip.py` | The public page of the wrong-step measurement, served at `/finding/rl-avoids-the-slip`: the 51 located first wrong steps of Base + cue as one mark each on an axis of log-probability change, by kind of error, with a switch over the model scored. Reads `results/wrongstep/math500-01/`; running the file checks it. |
| `tools/finding_rl_learns_the_opening_first.py` | The public page of the RL checkpoints (steps 100, 400, 2,800), served at `/finding/rl-learns-the-opening-first`: 500 answers as marks in three bands with a switch along training. Its PROBLEMS literal is a copy of the round-04 replication rows (not committed; `runs/replication/` of the theory worktree), checked against `studies/theory/results/engine/round-04/replication/`. |
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
| `specs/SPEC_frontier.md`, `analysis/frontier.py`, `analysis/frontier_test.py` | Token frontier: 24 reward-free test-time rules (single, restart, length caps, votes, the sequential vote that stops when two samples agree) replayed on the stored four-sample rows of both models; tokens per problem, 24 draw orders, base against one RL sample, the 5-fold choice per token budget, `--fixed` for the 328. Imports `day1_vote`, `selector`, `day1_length_rules`. See "Token frontier". |
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
| `results/rln4/t1_t3_items-01/` | `per_problem.json` (500 rows: right and wrong for T3 and T1 under grader v3, cut off, tokens, extracted answers, the first 240 characters of each answer), `metrics.json`, `run.json`. |
| `results/rln5/map-01/` | RLN-5 map, full run: `run.json`, `metrics.json` (analysis a-e), `examples.json` (real items), `checks.json` (the job's controls), `tokenize_check.json`. |
| `results/rln3/` | `rln3_overlap.json` (per-problem overlap flags), `offline/` (prep checks and offline gate). |
| `results/day1/` | Day-1 rows from `jobs/run_cell.py`: `readout.json` and one folder per job (`check_t1_n10-01/`, `hard328_base_cue_t10-01/`, `hard328_rl_plain_t10-01/`, `math500_base_cue_t06_p10-01/`). |
| `results/rln4/` | `grader_v3/readout.json` (the final table), `modal_k-01/`, `modal_t2-01/`, `modal_t3-01/` (readouts, metrics, run records), `t1_t2_items-01/` (per-problem T1 against T2, hand labels of the base failures), `offline/`. |
| `results/day1_wdiff/` | `readout.json` (cells, differences, predictions, check), `merge_stats.json` (RL and Code-RL differences from the base by tensor group and layer; Code against RL cosine) and per cell `<arm>-01/` (`run.json`, `metrics.json`, `merge.json`, `examples.json`). |
| `results/day1_hard328/` | `readout.json` (seven-cell table, per source, differences, check) and per T 1.0 cell `<arm>-01/` (`run.json`, `metrics.json` from the job, `examples.json`: one right, one wrong). |
| `specs/SELFDISTILL_2026-11-15.md` | Self-distillation spec: data arms V (vote), U (random), S (shortest), LoRA hyperparameters, merge, cells, seeds, predictions D1-D5, cost. |
| `jobs/distill_data.py`, `jobs/distill_data_test.py` | Builds the arms from the Day-1 #3 base cue rows on the laptop without reading any gold field; writes `data/selfdistill/arms-v1.json`. Planted cases. |
| `jobs/distill_train.py` | `train`: LoRA fine-tune (GPU), adapter, `train.json` (loss, generation check, difference statistics against RL - base). `merge`: rebuilds the merged bf16 model from a saved adapter for `run_cell --model-path`, hash checked. |
| `analysis/selfdistill.py` | Self-distillation readout: five 328 cells beside base cue, theta(0.5) cue, RL plain; sanity cell; training reports; predictions; `--hand`. |
| `data/selfdistill/arms-v1.json` | Per arm: problem index, sample, tokens, extracted answer and text sha256 of each training example (texts on S3, `r5/selfdistill-01/data/arms-v1.jsonl`). |
| `results/selfdistill/` | `readout.json`, per cell `<arm>-01/` (`run.json`, `metrics.json`, `examples.json`), `train_<arm>-01/` (`run.json`, `train.json`), `sanity_V_plain_math500_n100-01/`. |
| `specs/SPEC_handoff.md` | Prefix hand-off spec: writers, pool, cut rule on token ids, seeds, strata, the own-prefix control, hypotheses H0-H4 with refuters, deviations. |
| `lib/handoff_lib.py`, `prep/handoff_plan.py`, `data/handoff/plan_v1.json` | The prefix rule (writer jobs, cuts, seeds, `answer_ids`), and the frozen plan it gives: pool of 183, per writer sample its stratum, id count, text sha256, and per cut the prefix length and id sha256. |
| `jobs/handoff_gen.py` | Hand-off generation job: one finisher model continues both writers' prefixes; writes each raw row (ids, prefix text, continuation) before anything else and does not score. |
| `analysis/handoff.py`, `analysis/handoff_test.py` | Hand-off readout (grader v3 on prefix + continuation, strata tables, paired bootstrap, own-prefix control) and its planted checks. |
| `results/handoff/` | `base-01/`, `rl-01/` (one per finisher: `run.json`, `metrics.json`, `rows.jsonl` without text, `examples.json`) and `readout-01/` (`readout.json`, `readout.txt`). |
| `specs/SPEC_table.md` (addendum 1), `analysis/config_table.py`, `results/table/hard328-02/` (current), `results/table/hard328-01/` (first run, 49 rows) | One table of the full-set configurations on hard328 whose per-problem rows are committed: counts, intervals, share of the base-to-RL gap closed, tokens, clean 322, grader v4, a check per posted number; a separate fresh2026 table. See "Configurations on the 328 with committed rows, in one table". |
| `specs/SPEC_relay.md`, `prep/relay_plan.py`, `data/handoff/plan_v2.json`, `analysis/relay.py`, `results/relay/` | Relay on hard328 (Think-SFT writes, RL finishes, and the three other writer x finisher pairs): spec with filed predictions, the frozen plan for all 328 problems, the readout (imports `analysis/handoff.py`), run folders `{rl,think}_c{25,50}-01/` and `readout-01/`. `jobs/handoff_gen.py --plan plan_v2.json [--finisher-path]` generates. |

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

## Configurations on the 328 with committed rows, in one table (hard328, n = 328, laptop, board work-44d747, idea-44d6e1)

Question (DIRECTION.md): how much of the RL-Zero-Math gain is reached without reward training, chosen on MATH-500 and scored
once on the 328? The full-set configurations whose per-problem rows are committed, rebuilt by `analysis/config_table.py`
(spec `specs/SPEC_table.md`, commit `eb7afd0`, written before the script; addendum 1, commit `73264e8`, written before the
second run). Run folder `results/table/hard328-02/`: `table.md` (every column, also the clean 322 and grader v4, and the
fresh2026 table), `table.json` (with the per-problem vectors), `checks.json`, `v4_rows.jsonl`, `run.json`. It is not every
configuration ever run on the 328: the list "Left out" below names what is absent. Formerly titled "All configurations on the
328 in one table"; the first run, `results/table/hard328-01/` (49 rows, result-389164), is kept and its 49 rows are identical
in hard328-02, which adds 17 rows (review of result-389164: the top-8 dial was absent): the finish dial at six sizes with
four random-direction controls, the 1.5 size replicated with four samples, and Think-SFT + a (RL - base).

1. No reward-trained weights, nothing chosen on the 328: Think-SFT + cue (trained on traces, so not training-free). One
   sample closes 122 % [103, 144] of the base-to-RL gap (209.0 of 328 against RL 200.0 and the cued base 158.5), the vote
   over 4 closes 169 % [128, 250] (241 against 221 and 192). With no training at all, the cued base's best rule closes 20 %
   [13, 29] at one sample (restart after a cap hit, 167.0) and 24 % [0, 50] under the vote (after restart, ties to the
   shortest, 199).
2. At the tokens of one RL sample (9,325 per problem): one Think-SFT + cue sample costs 1.08 times [1.06, 1.11] as much.
   Stopped at 14,028 tokens it costs the same (1.00 [0.98, 1.02]) and closes 79 % [62, 98]: 191.2 right, 2.7 points
   [0.2, 5.1] below one RL sample and level with RL stopped at the same length (191.0; +0.1 [-2.2, +2.4]). The untrained
   base at that budget is its one sample: 0 % at 0.99 times.
3. Unexplained: the 12.7 points [10.1, 15.5] between one cued-base sample and one RL sample (8.8 [5.2, 12.8] under the
   vote) are reached by no rule on the untrained weights. Think-SFT's lead over RL is 17.8 right answers per sample (5.4
   points [4.0, 6.9]) that are longer than 14,028 tokens; whether RL stops too early there is untested (work-ceccc0, open).

The three sentences are those of hard328-01: no row added in hard328-02 changes them. The best row with no reward-trained
weights and nothing chosen on the 328 is unchanged (Think-SFT + cue: 209.0 one sample, 241 under the vote; its single draws
of 219 were already in the table). The only added rows with "no" in both columns are controls: Think-SFT + noise (209) and
the random directions (158 to 167). Every added row above RL uses RL's weights: base + 1.5 x the top-8 RL directions closes
107 % [84, 133] on the sample its size was chosen on and 101 % [88, 115] on four new draws, at 0.95 times the tokens of one
RL sample (vote 214, 76 % [45, 110]); Think-SFT + 2 (RL - base) closes 176 % [152, 207] (231.5, a chosen on the 328), a = 1,
not chosen, 148 % [124, 177] (220). Status of sentence 3's open item: work-ceccc0 is closed (result-c8b994, section "Token
cap 32,768": with twice the cap RL gains 2 problems, Think-SFT 23); it is not a row here because its rows are not on main.

Share of the gap closed = (accuracy - base) / (RL - base), base = base + cue, RL = RL plain, in the row's family. Single: the
mean of the four stored samples (158.5 and 200.0; denominator 12.7 points [10.1, 15.5]). Vote: the plain vote over 4 (192
and 221; denominator 8.8 points [5.2, 12.8], 29 problems, so every vote share has a wide interval). 0 % = the cued base,
100 % = RL. Intervals: percentile bootstrap over the 328 problems, 5,000 resamples, seed 0, the same resamples in every
column; the share's interval is the interval of the ratio. Abstained = no extracted answer (for a vote: no sample has one).
Tokens = generated tokens per problem over every sample and restart drawn (relay: prefix plus continuation). Rows named
"mean of 4" or "mean of 24 orders" have fractional counts. T 1.0 / top-p 1.0, cap 16,384, grader v3.

| Configuration | Samples | Right / wrong / abstained of 328 | Accuracy, % [95 %] | Share of the gap closed, % [95 %] | minus one RL sample, points [95 %] | Tokens per problem (multiple of one RL sample) | Reward-trained weights | Chosen on the 328 | MATH-500: right, tokens |
|---|---|---|---|---|---|---|---|---|---|
| base + cue, one sample (mean of 4) | 1 | 158.5 / 103.5 / 66 | 48.3 [43.5, 53.1] | 0 [0, 0] (single) | -12.7 [-15.5, -10.1] | 9,225 (0.99) | no | no | 410.5, 4,008 |
| base + cue, one sample, restart after a cap hit (mean of 4) | 1 | 167 / 135 / 26 | 50.9 [46.1, 55.6] | 20 [13, 29] (single) | -10.1 [-12.7, -7.6] | 13,827 (1.48) | no | no | 418, 4,924 |
| base + cue, vote over 4 | 4 | 192 / 124 / 12 | 58.5 [53.0, 64.0] | 0 [0, 0] (vote) | -2.4 [-5.6, +0.6] | 36,902 (3.96) | no | no | 446, 16,034 |
| base + cue, vote over 4 after restart | 4 | 195 / 132 / 1 | 59.5 [54.0, 64.9] | 10 [-8, 29] (vote) | -1.5 [-4.8, +1.6] | 55,306 (5.93) | no | no | 450, 19,697 |
| base + cue, vote over 4, ties to the shortest | 4 | 191 / 125 / 12 | 58.2 [52.7, 63.7] | -3 [-29, 17] (vote) | -2.7 [-5.9, +0.2] | 36,902 (3.96) | no | no (tie rule in-sample on MATH-500) | 453, 16,034 |
| base + cue, vote over 4 after restart, ties to the shortest | 4 | 199 / 128 / 1 | 60.7 [55.2, 66.2] | 24 [0, 50] (vote) | -0.3 [-3.3, +2.5] | 55,306 (5.93) | no | no (tie rule in-sample on MATH-500) | 454, 19,697 |
| base + cue, sequential vote, at most 3 (mean of 24 orders) | 3 | 178.8 / 130.8 / 18.5 | 54.5 [49.4, 59.6] | -46 [-98, -21] (vote) | -6.5 [-9.3, -3.9] | 25,567 (2.74) | no | no | 442.2, 9,978 |
| base + cue, sequential vote, at most 4, restarts (mean of 24 orders) | 4 | 190.8 / 136.2 / 1 | 58.2 [52.8, 63.4] | -4 [-33, 14] (vote) | -2.8 [-5.7, -0.1] | 46,817 (5.02) | no | no | 452.1, 14,193 |
| base + cue, sequential vote, at most 4, restarts, ties to the shortest (mean of 24 orders) | 4 | 198.5 / 128.5 / 1 | 60.5 [55.0, 66.0] | 22 [-2, 47] (vote) | -0.5 [-3.4, +2.4] | 46,817 (5.02) | no | no (tie rule in-sample on MATH-500) | 453, 14,193 |
| RL plain, one sample (mean of 4) | 1 | 200 / 119 / 9 | 61.0 [56.2, 65.7] | 100 [100, 100] (single) | +0.0 [+0.0, +0.0] | 9,325 (1.00) | yes | no | 460, 4,687 |
| RL plain, one sample, restart after a cap hit (mean of 4) | 1 | 204.5 / 121 / 2.5 | 62.3 [57.6, 67.0] | 111 [105, 118] (single) | +1.4 [+0.6, +2.2] | 11,027 (1.18) | yes | no | 463, 4,966 |
| RL plain, vote over 4 | 4 | 221 / 107 / 0 | 67.4 [62.2, 72.6] | 100 [100, 100] (vote) | +6.4 [+4.4, +8.4] | 37,299 (4.00) | yes | no | 474, 18,747 |
| RL plain, vote over 4 after restart | 4 | 224 / 104 / 0 | 68.3 [63.1, 73.5] | 110 [92, 140] (vote) | +7.3 [+5.1, +9.7] | 44,108 (4.73) | yes | no | 475, 19,864 |
| RL plain, vote over 4, ties to the shortest | 4 | 222 / 106 / 0 | 67.7 [62.5, 72.9] | 103 [82, 132] (vote) | +6.7 [+4.6, +8.9] | 37,299 (4.00) | yes | no (tie rule in-sample on MATH-500) | 475, 18,747 |
| RL plain, vote over 4 after restart, ties to the shortest | 4 | 220 / 108 / 0 | 67.1 [61.9, 72.3] | 97 [74, 126] (vote) | +6.1 [+4.0, +8.3] | 44,108 (4.73) | yes | no (tie rule in-sample on MATH-500) | 475, 19,864 |
| RL plain, sequential vote, at most 3 (mean of 24 orders) | 3 | 212.7 / 115.3 / 0 | 64.8 [59.9, 69.7] | 71 [52, 88] (vote) | +3.9 [+2.8, +4.9] | 23,575 (2.53) | yes | no | 470.4, 10,495 |
| RL plain, sequential vote, at most 4, restarts (mean of 24 orders) | 4 | 218.2 / 109.8 / 0 | 66.5 [61.4, 71.6] | 91 [69, 118] (vote) | +5.6 [+3.7, +7.5] | 31,620 (3.39) | yes | no | 476.1, 11,771 |
| RL plain, sequential vote, at most 4, restarts, ties to the shortest (mean of 24 orders) | 4 | 220.5 / 107.5 / 0 | 67.2 [62.0, 72.4] | 98 [77, 126] (vote) | +6.2 [+4.3, +8.4] | 31,620 (3.39) | yes | no (tie rule in-sample on MATH-500) | 475, 11,771 |
| Think-SFT + cue, one sample (mean of 4) | 1 | 209 / 37.5 / 81.5 | 63.7 [58.9, 68.4] | 122 [103, 144] (single) | +2.7 [+0.4, +5.2] | 10,103 (1.08) | no | no | 460.2, 4,876 |
| Think-SFT + cue, vote over 4 | 4 | 241 / 57 / 30 | 73.5 [68.6, 78.4] | 169 [128, 250] (vote) | +12.5 [+9.3, +15.8] | 40,410 (4.33) | no | no | 481, 19,503 |
| Think-SFT + cue, vote over 4, ties to the shortest | 4 | 239 / 59 / 30 | 72.9 [68.0, 77.7] | 162 [122, 242] (vote) | +11.9 [+8.8, +15.0] | 40,410 (4.33) | no | no (tie rule in-sample on MATH-500) | 481, 19,503 |
| Think-SFT + cue, vote over 4 after restart, ties to the shortest (no restart rows: restart = none) | 4 | 239 / 59 / 30 | 72.9 [68.0, 77.7] | 162 [122, 242] (vote) | +11.9 [+8.8, +15.0] | 40,410 (4.33) | no | no (tie rule in-sample on MATH-500) | 481, 19,503 |
| Think-SFT + cue, sequential vote, at most 3 (mean of 24 orders) | 3 | 233.2 / 54.3 / 40.5 | 71.1 [66.3, 75.9] | 142 [107, 208] (vote) | +10.1 [+7.1, +13.0] | 26,114 (2.80) | no | no | 478.5, 10,837 |
| Think-SFT + cue, sequential vote, at most 4, restarts (mean of 24 orders) (no restart rows: restart = none) | 4 | 238.9 / 59.1 / 30 | 72.8 [67.9, 77.6] | 162 [122, 239] (vote) | +11.9 [+8.7, +15.0] | 30,837 (3.31) | no | no | 480.8, 11,420 |
| Think-SFT + cue, sequential vote, at most 4, restarts, ties to the shortest (mean of 24 orders) (no restart rows: restart = none) | 4 | 239.5 / 58.5 / 30 | 73.0 [68.0, 77.7] | 164 [124, 244] (vote) | +12.0 [+8.9, +15.2] | 30,837 (3.31) | no | no (tie rule in-sample on MATH-500) | 480.5, 11,420 |
| Think-SFT + cue, one sample stopped at 14,028 tokens (tokens matched to one RL sample; mean of 4) | 1 | 191.2 / 16 / 120.8 | 58.3 [53.4, 63.1] | 79 [62, 98] (single) | -2.7 [-5.1, -0.2] | 9,325 (1.00) | no | L set from the 328's token counts, no score read |  |
| RL plain, one sample stopped at the same 14,028 tokens (mean of 4) | 1 | 191 / 66 / 71 | 58.2 [53.4, 63.0] | 78 [70, 86] (single) | -2.7 [-3.9, -1.8] | 8,970 (0.96) | yes | L set from the 328's token counts, no score read |  |
| mixed vote, 2 RL plain + 2 Think-SFT + cue (mean over combinations) | 4 | 228.1 / 99.5 / 0.4 | 69.5 [64.7, 74.3] | 124 [103, 167] (vote) | +8.6 [+6.8, +10.4] | 38,855 (4.17) | partly | no (every mix is reported, none picked) |  |
| mixed vote, 2 RL plain + 2 base + cue (mean over combinations) | 4 | 207.6 / 120 / 0.3 | 63.3 [58.3, 68.1] | 54 [37, 68] (vote) | +2.3 [+1.1, +3.5] | 37,101 (3.98) | partly | no (every mix is reported, none picked) |  |
| mixed vote, 2 Think-SFT + cue + 2 base + cue (mean over combinations) | 4 | 220.8 / 91 / 16.2 | 67.3 [62.4, 72.0] | 99 [75, 143] (vote) | +6.3 [+4.0, +8.7] | 38,656 (4.15) | no | no (every mix is reported, none picked) |  |
| mixed vote, 4 RL plain + 4 Think-SFT + cue (mean over combinations) | 8 | 239 / 89 / 0 | 72.9 [67.8, 77.7] | 162 [131, 230] (vote) | +11.9 [+9.2, +14.6] | 77,710 (8.33) | partly | no (every mix is reported, none picked) |  |
| mixed vote, 4 Think-SFT + cue + 4 base + cue (mean over combinations) | 8 | 238 / 87 / 3 | 72.6 [67.5, 77.4] | 159 [120, 237] (vote) | +11.6 [+8.7, +14.6] | 77,312 (8.29) | no | no (every mix is reported, none picked) |  |
| relay: RL writes the first 25 %, RL finishes | 1 | 206 / 113 / 9 | 62.8 [57.3, 68.0] | 114 [90, 141] (single) | +1.8 [-1.3, +5.0] | 9,559 (1.03) | yes | no (arms and cuts filed in SPEC_relay) |  |
| relay: RL writes the first 50 %, RL finishes | 1 | 193 / 128 / 7 | 58.8 [53.7, 64.0] | 83 [61, 106] (single) | -2.1 [-5.0, +0.8] | 9,519 (1.02) | yes | no (arms and cuts filed in SPEC_relay) |  |
| relay: RL writes the first 25 %, Think-SFT + cue finishes | 1 | 204 / 30 / 94 | 62.2 [57.0, 67.7] | 110 [85, 137] (single) | +1.2 [-1.9, +4.3] | 10,511 (1.13) | partly | no (arms and cuts filed in SPEC_relay) |  |
| relay: RL writes the first 50 %, Think-SFT + cue finishes | 1 | 199 / 35 / 94 | 60.7 [55.5, 66.2] | 98 [72, 126] (single) | -0.3 [-3.6, +3.0] | 10,664 (1.14) | partly | no (arms and cuts filed in SPEC_relay) |  |
| relay: Think-SFT + cue writes the first 25 %, RL finishes | 1 | 207 / 117 / 4 | 63.1 [57.6, 68.3] | 117 [92, 145] (single) | +2.1 [-1.1, +5.3] | 8,900 (0.95) | partly | no (arms and cuts filed in SPEC_relay) |  |
| relay: Think-SFT + cue writes the first 50 %, RL finishes | 1 | 209 / 119 / 0 | 63.7 [58.2, 68.9] | 122 [97, 151] (single) | +2.7 [-0.4, +5.9] | 8,923 (0.96) | partly | no (arms and cuts filed in SPEC_relay) |  |
| relay: Think-SFT + cue writes the first 25 %, Think-SFT + cue finishes | 1 | 219 / 38 / 71 | 66.8 [61.6, 72.0] | 146 [119, 180] (single) | +5.8 [+2.5, +9.2] | 10,029 (1.08) | no | no (arms and cuts filed in SPEC_relay) |  |
| relay: Think-SFT + cue writes the first 50 %, Think-SFT + cue finishes | 1 | 211 / 37 / 80 | 64.3 [58.8, 69.5] | 127 [97, 162] (single) | +3.4 [-0.5, +7.2] | 10,423 (1.12) | no | no (arms and cuts filed in SPEC_relay) |  |
| base plain, one sample | 1 | 76 / n/a (cap hits 35) | 23.2 [18.6, 27.7] | -199 [-274, -144] (single) | -37.8 [-42.8, -32.9] | 4,928 (0.53) | no | no |  |
| base + cue, one sample, Day-1 #1 draw | 1 | 164 / n/a (cap hits 77) | 50.0 [44.5, 55.5] | 13 [-15, 40] (single) | -11.0 [-14.7, -7.4] | 9,344 (1.00) | no | no |  |
| RL plain, one sample, Day-1 #1 draw | 1 | 206 / n/a (cap hits 20) | 62.8 [57.3, 68.0] | 114 [92, 140] (single) | +1.8 [-1.1, +4.7] | 9,315 (1.00) | yes | no |  |
| RL + cue, one sample | 1 | 205 / n/a (cap hits 25) | 62.5 [57.0, 67.7] | 112 [91, 137] (single) | +1.5 [-1.2, +4.3] | 9,316 (1.00) | yes | no |  |
| base + 0.25 (RL - base) + cue, one sample | 1 | 182 / n/a (cap hits 56) | 55.5 [50.0, 60.7] | 57 [31, 81] (single) | -5.5 [-8.9, -2.3] | 9,097 (0.98) | partly | no |  |
| base + 0.5 (RL - base) + cue, one sample | 1 | 190 / n/a (cap hits 73) | 57.9 [52.4, 63.4] | 76 [51, 102] (single) | -3.0 [-6.2, +0.2] | 9,656 (1.04) | partly | no |  |
| RL-Zero-Code + cue, one sample | 1 | 187 / n/a (cap hits 25) | 57.0 [51.5, 62.5] | 69 [45, 93] (single) | -4.0 [-7.2, -0.8] | 7,613 (0.82) | yes (code reward) | no |  |
| Think-SFT + cue, one sample, other workspace (sameraslan) | 1 | 219 / n/a (cap hits 89) | 66.8 [61.3, 72.0] | 146 [120, 178] (single) | +5.8 [+2.7, +8.9] | 10,123 (1.09) | no | no |  |
| Think-SFT plain, one sample (sameraslan) | 1 | 203 / n/a (cap hits 86) | 61.9 [56.7, 67.1] | 107 [80, 138] (single) | +0.9 [-2.6, +4.4] | 9,376 (1.01) | no | no |  |
| base + -1 x top-8 RL directions + cue, one sample | 1 | 118 / 114 / 96 | 36.0 [30.8, 41.2] | -98 [-143, -63] (single) | -25.0 [-29.3, -20.7] | 9,968 (1.07) | partly (RL-derived directions) | no (one size of the sweep of 7, every size reported) |  |
| base + 0.5 x top-8 RL directions + cue, one sample | 1 | 170 / 118 / 40 | 51.8 [46.3, 57.3] | 28 [-1, 53] (single) | -9.1 [-12.9, -5.6] | 8,731 (0.94) | partly (RL-derived directions) | no (one size of the sweep of 7, every size reported) |  |
| base + 1 x top-8 RL directions + cue, one sample | 1 | 192 / 110 / 26 | 58.5 [53.0, 64.0] | 81 [56, 105] (single) | -2.4 [-5.5, +0.6] | 9,284 (1.00) | partly (RL-derived directions) | no (one size of the sweep of 7, every size reported) |  |
| base + 1.5 x top-8 RL directions + cue, one sample | 1 | 203 / 115 / 10 | 61.9 [56.4, 67.1] | 107 [84, 133] (single) | +0.9 [-2.1, +3.9] | 8,916 (0.96) | partly (RL-derived directions) | yes (1.5 is the best of 7 sizes scored on the 328) |  |
| base + 2 x top-8 RL directions + cue, one sample | 1 | 190 / 138 / 0 | 57.9 [52.4, 63.1] | 76 [52, 99] (single) | -3.0 [-6.1, -0.2] | 8,207 (0.88) | partly (RL-derived directions) | no (one size of the sweep of 7, every size reported) |  |
| base + 3 x top-8 RL directions + cue, one sample | 1 | 117 / 137 / 74 | 35.7 [30.5, 41.2] | -100 [-147, -64] (single) | -25.3 [-29.6, -21.1] | 8,257 (0.89) | partly (RL-derived directions) | no (one size of the sweep of 7, every size reported) |  |
| base + -1 x 8 random directions (control) + cue, one sample | 1 | 159 / 109 / 60 | 48.5 [43.0, 54.0] | 1 [-28, 29] (single) | -12.5 [-16.5, -8.5] | 9,118 (0.98) | no (random directions) | no (control) |  |
| base + 1 x 8 random directions (control) + cue, one sample | 1 | 158 / 118 / 52 | 48.2 [42.7, 53.7] | -1 [-30, 25] (single) | -12.8 [-16.8, -9.0] | 9,139 (0.98) | no (random directions) | no (control) |  |
| base + 2 x 8 random directions (control) + cue, one sample | 1 | 167 / 95 / 66 | 50.9 [45.4, 56.4] | 20 [-7, 48] (single) | -10.1 [-14.1, -6.2] | 9,243 (0.99) | no (random directions) | no (control) |  |
| base + 3 x 8 random directions (control) + cue, one sample | 1 | 163 / 103 / 62 | 49.7 [44.2, 54.9] | 11 [-17, 36] (single) | -11.3 [-15.0, -7.9] | 9,376 (1.01) | no (random directions) | no (control) |  |
| base + 1.5 x top-8 RL directions + cue, one sample (mean of 4 new draws) | 1 | 200.25 / 119 / 8.75 | 61.1 [56.0, 65.7] | 101 [88, 115] (single) | +0.1 [-1.7, +1.8] | 8,898 (0.95) | partly (RL-derived directions) | yes (1.5 is the best of 7 sizes scored on the 328); the 4 samples are new draws on the same problems, not a held-out set | 456, 4,422 |
| base + 1.5 x top-8 RL directions + cue, vote over 4 new draws | 4 | 214 / 114 / 0 | 65.2 [59.8, 70.4] | 76 [45, 110] (vote) | +4.3 [+1.9, +6.6] | 35,593 (3.82) | partly (RL-derived directions) | yes (1.5 is the best of 7 sizes scored on the 328); the 4 samples are new draws on the same problems, not a held-out set |  |
| Think-SFT + 1 (RL - base) + cue, one sample | 1 | 220 / 47 / 61 | 67.1 [61.9, 72.3] | 148 [124, 177] (single) | +6.1 [+3.2, +8.9] | 9,667 (1.04) | partly (RL weight change added to Think-SFT) | no (prediction filed before the run) | 467, 4,771 |
| Think-SFT + 2 (RL - base) + cue, one sample (mean of 2) | 1 | 231.5 / 55.5 / 41 | 70.6 [65.7, 75.2] | 176 [152, 207] (single) | +9.6 [+6.9, +12.3] | 9,502 (1.02) | partly (RL weight change added to Think-SFT) | yes (a = 2 is the best of 4 values on the 328; the second sample was pre-registered with the threshold 222) |  |
| Think-SFT + 3 (RL - base) + cue, one sample | 1 | 227 / 80 / 21 | 69.2 [64.0, 74.4] | 165 [139, 199] (single) | +8.2 [+5.3, +11.3] | 9,709 (1.04) | partly (RL weight change added to Think-SFT) | no (one value of the sweep of 4, every value reported) |  |
| Think-SFT + 4 (RL - base) + cue, one sample | 1 | 213 / 105 / 10 | 64.9 [59.5, 70.1] | 131 [106, 159] (single) | +4.0 [+0.8, +7.0] | 10,333 (1.11) | partly (RL weight change added to Think-SFT) | no (one value of the sweep of 4, every value reported) |  |
| Think-SFT + noise of the RL delta's norm + cue (control), one sample | 1 | 209 / 31 / 88 | 63.7 [58.5, 68.9] | 122 [98, 151] (single) | +2.7 [-0.3, +5.9] | 10,109 (1.08) | no | no (control) |  |

- Chosen on the 328: four rows were picked on 328 scores, all added in hard328-02 and all with RL's weights in them: the
  three rows of the 1.5 size of the top-8 edit (the best of 7 sizes; its four-sample rows are new draws on the same
  problems, not a held-out set; MATH-500 is the held-out reading, 456 of 500) and Think-SFT + 2 (RL - base) (the best of 4
  values of a; its second sample, 229, was pre-registered with the threshold 222). No other row's model, prompt or rule was
  picked on 328 scores. Two rows use a length set from the 328's token counts (no score read). The tie-to-shortest rule was written on MATH-500 after reading the problems it fixes (453
  there is in-sample); on the 328 it is held out: 191 against the vote's 192, 199 against 195 after restart (+2.1 points
  [0.0, 4.6] over the plain vote). Picking the best relay arm or the best mix from this table would be a choice on the 328.
- Clean 322 (without the 6 problems of `results/wsp1/sft_overlap-03/flags.json`): no share moves by more than 3.2 points
  (Think-SFT + cue: one sample 204.0 of 322, 124 % [105, 148]; vote 235, 169 % [128, 250]).
- Grader v4 (v4a of `grader/repair_v4.py`, votes recounted on its extraction; text from the local raw answers of jobs
  `e8e6`, `5ff2` and the four Think-SFT jobs, extraction stored in `v4_rows.jsonl`): no row changes by more than 1 problem
  (Think-SFT one sample 209.5, 123 % [104, 146]; vote 241; the base's vote after restart 194 instead of 195). The relay rows,
  the one-sample cells from `axis/hard328-01/vectors.json`, sameraslan's two cells and the 17 rows added in hard328-02 have no
  v4 cell: their text was not read.
- Instrument checks (`checks.json` of hard328-02): 270 of 270 posted numbers reproduce from the committed rows, 0 fail: the
  176 of hard328-01 and 94 new ones (the finish dial 34: right, cap hits and tokens of its 12 cells against
  `results/xreward/edits/readout.json`, its size 0 and RL columns equal to `axis/hard328-01/vectors.json`, four paired
  differences; the four-sample replication 10; "Delta transplant" 29; fresh2026 21), counts, tokens and intervals. The 176
  of hard328-01 are README sections "The 328
  with four samples and restarts", "Think-SFT with the cue under the vote rules", "Mixed-model vote", "Risk-coverage"
  outcome tables, "Think-SFT training-data overlap", "Relay", the Day-1 #1 and #4b cells, `frontier/hard328-01`, board
  result-32ff47, and 39 MATH-500 numbers of "Token frontier"), counts, tokens and intervals. Planted (`--test`): a
  configuration equal to RL gives 100 % [100, 100], equal to the base 0 % [0, 0], their mean 50 %; a vector with one
  flipped problem fails its check; a denominator carried by 6 problems is marked unstable.
- Left out, still absent (no per-problem rows on main; metrics and readouts only): cap 32,768 (result-c8b994,
  `results/cap32/`: Think-SFT + cue 230 at 32,768 and 207 at 16,384 on the same answers, RL plain 195 and 193; no rows on
  branch `cap32` either); self-distillation (`results/selfdistill/`: V cue 167, U cue 168, S cue 171, V plain 161);
  signed self-training (`results/signed1/`); solved examples in context (`results/shots1b/hard328_rl-01/`); the loop-neuron
  edit (sameraslan, result-79784b); the T 0.6 cells on the 328; the 14 other xreward edit cells (top-1, top-64, bulk,
  attention-only, MLP-only, Code-RL and other donors, projections: `results/xreward/edits/readout.json`); base + cue at cap
  32,768 and the vote at cap 32,768 (no result on main). Read from outside `results/`: the one-sample dial cells come from
  `PROBLEMS` in `tools/finding_the_finish_dial.py` (outcome, tokens and extracted answer per problem, written from the jobs'
  answers; their run folders hold metrics only); sameraslan's two Think-SFT cells from commit `bdba62b` of branch
  `claude/weight-space-programming-research-ddd44e` (not on main). No full-set hard328 configuration of frustea is on the
  board.
- fresh2026 (n = 136, result-5251c9, section "Fresh held-out set") is another benchmark: its rows are a separate table with no
  share of the gap. Abstained = no extracted answer; accuracy interval from the same bootstrap over the 136 problems; the
  differences are the posted ones (draws of `analysis/fresh_read.py`).

  | fresh2026 configuration | Samples | Right / wrong / abstained of 136 | Accuracy, % [95 %] | minus RL plain under the same rule, points [95 %] | Tokens per problem | Reward-trained weights |
  |---|---|---|---|---|---|---|
  | Think-SFT + cue, one sample (mean of 4) | 1 | 60 / 18.75 / 57.25 | 44.1 [36.9, 51.7] | +7.0 [+3.1, +11.0] | 13,043 | no |
  | Think-SFT + cue, vote over 4 | 4 | 75 / 40 / 21 | 55.1 [47.1, 63.2] | +13.2 [+7.4, +19.1] | 52,170 | no |
  | RL plain, one sample (mean of 4) | 1 | 50.5 / 80.75 / 4.75 | 37.1 [30.3, 44.5] | +0.0 [+0.0, +0.0] | 12,083 | yes |
  | RL plain, vote over 4 | 4 | 57 / 79 / 0 | 41.9 [33.8, 50.7] | +0.0 [+0.0, +0.0] | 48,331 | yes |
  | base + cue, one sample (mean of 4) | 1 | 29.5 / 56 / 50.5 | 21.7 [16.4, 27.8] | -15.4 [-19.9, -11.4] | 12,790 | no |
  | base + cue, vote over 4 | 4 | 38 / 87 / 11 | 27.9 [20.6, 36.0] | -14.0 [-19.9, -8.1] | 51,158 | no |
- One right and one wrong item with input, output and score are in each source run folder's `examples.json`.

```
P="uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.config_table"
$P --test
$P --out studies/rlneurons/results/table/hard328-03 --v4-rows studies/rlneurons/results/table/hard328-01/v4_rows.jsonl
```

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
`flip_review`: 40 of the 113 read). A second reader (Claude Fable 5.2) read all 114 (`analysis/grader_v3_read2.py`,
`results/rln4/grader_v3_read2/readout.json`): 112 of the 113 wrong-to-right flips are right; 1 is not (base plain T 1.0, problem 142: the box
holds an expression equal to the gold, the stated number is wrong), and the 1 right-to-wrong flip is a v3 error on the same
cell, so that cell's count is unchanged net; no RL flip and no cue-cell flip is wrong. The 114 flips are 104 distinct texts. The v1 numbers 57.2 (base) and 92.0 (RL) quoted in older notes are the n13 cells under v1 (286 and 460).

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

## Code pair: the cue on HumanEval+ and MBPP+ (538 problems, T 1.0, one sample, board work-d84808)

Spec `specs/SPEC_code1.md`. `jobs/run_code_cell.py` samples one answer per problem with the Code model's raw template and
`lib/code_lib.py` runs the extracted program against the EvalPlus tests; 4 of the 542 problems fail the grader check with
their reference solution and are excluded for every cell. RL = `allenai/Olmo-3.1-7B-RL-Zero-Code`. The Code cue is the
RL-Code model's own opening, 12 tokens (`' as shown in the prompt. I hope this helps!\n\nOkay'`); the Math cue is
`' line!\n\nOkay'`. Readout `analysis/code1_readout.py` -> `results/code1/readout.json` and one folder per cell
(`run.json`, `metrics.json`, `examples.json`: the first passed and the first failed problem). Paired bootstrap, 5,000
resamples, in points.

| Cell | Passed of 538 | HumanEval+ of 163 | MBPP+ of 375 | Cap hits | No code block | Tokens per problem | Job |
|---|---|---|---|---|---|---|---|
| RL-Code, plain | 401 (74.5 %) | 135 | 266 | 8 | 8 | 4,054 | `abaybektursun-1114-170253-f661` |
| base, plain | 222 (41.3 %) | 72 | 150 | 15 | 43 | 2,241 | `abaybektursun-1114-170258-388e` |
| base, Code cue | 317 (58.9 %) | 106 | 211 | 27 | 34 | 4,148 | `abaybektursun-1114-170304-c03c` |
| base, Math cue | 326 (60.6 %) | 120 | 206 | 22 | 33 | 4,119 | `abaybektursun-1114-170309-b137` |

- RL minus plain base: 33.3 [28.8, 37.7]. The cue gives the base +17.7 [12.8, 22.5] (Code cue) and +19.3 [14.3, 24.3]
  (Math cue): 53 % and 58 % of the gain, against 78 % on MATH-500. H1 (at least half) held, H2 (no gain to recover) refuted.
- The two cues are equal: Code minus Math -1.7 [-5.8, 2.8] (H3 held). What helps is the opening word `Okay` and a
  reasoning start, not the text before it.
- RL stays ahead of the cued base by 15.6 [11.5, 19.9] and 13.9 [10.0, 17.8] points at the same tokens per problem.
- Without the 3 problems that overlap the RL training prompts: 399, 221, 315, 323 of 535.
- Not run: the vote over four samples after restart (the configuration chosen on MATH-500), and RL-Code with a cue (the
  model writes the cue itself in 10 of 10 smoke answers).

## Self-distillation of the base's own vote (board work-9763ed, spec specs/SELFDISTILL_2026-11-15.md)

Question: does a short supervised fine-tune of the base on its own vote-selected cue samples from MATH-500 (no reward, no gold
answer) raise it on the 328 harder problems it never saw? Answer: no. The fine-tuned model with the cue scores 167 of 328 against the
base's 164 (+0.9 points, [-3.0, 4.9]), and the vote selection does no better than a random own sample (V cue - U cue -0.3,
[-4.9, 4.3]). What it does learn is the format: with the plain prompt it now writes the cue in 328 of 328 answers and scores 161,
level with the cued base (base plain: 76). All from `results/selfdistill/readout.json` (`analysis/selfdistill.py`); grader v3; T 1.0 /
top-p 1.0, cap 16,384, one sample per problem; paired bootstrap, 5,000 resamples, seed 0, 95 % percentile interval, in points.

Training data (`jobs/distill_data.py`, `data/selfdistill/arms-v1.json`): attempt 0 of the 4 samples per problem of Day-1 #3 base cue
(job `abaybektursun-1114-153825-208b`). V: the shortest finished member of the plurality group (at least 2 votes, no tie); 455 of 500
problems (45 without a plurality). U: one finished sample at random on the same 455. S: the shortest finished sample on the same 455
(length control; V picks the same sample as S on 422 of 455). Each example: the plain prompt, target = the stored completion with
its cue plus the stop token. Right under v3 (read after the build): V 439 of 455, U 407, S 416. LoRA rank 16, alpha 32, all q, k,
v, o, gate, up, down; lr 1e-4 constant, 2 epochs, 16,384 target tokens per step; merged to bf16 with stochastic rounding.

| Arm | Examples | Target tokens | Steps | Loss first / last step | Loss epoch 1 / 2 | ‖D‖ / ‖W‖ | Cosine with RL - base | Train job, folder |
|---|---|---|---|---|---|---|---|---|
| V | 455 | 898,064 | 96 | 0.366 / 0.258 | 0.394 / 0.381 | 0.46 % | 0.0025 | `abaybektursun-1114-194352-feef`, `train_V-01/` |
| U | 455 | 1,353,449 | 140 | 0.387 / 0.290 | 0.441 / 0.429 | 0.58 % | 0.0022 | `abaybektursun-1114-194358-195f`, `train_U-01/` |
| S | 455 | 839,231 | 91 | 0.372 / 0.286 | 0.388 / 0.375 | 0.44 % | 0.0025 | `abaybektursun-1114-194405-bbb6`, `train_S-01/` |

‖D‖ / ‖W‖ is over the adapted matrices (float32 LoRA difference; RL - base is 0.24 % on the same matrices, so the fine-tune
moved the weights twice as far as RL did, in a direction nearly orthogonal to it: 0.001 to 0.003 per tensor group). Effective scale
of the merge 1.000 in every arm; the merge with the adapter scaled by 0 is tensor-identical to the base (asserted).

| Cell (328 problems) | Right (v3) | Cap hits | Rule-A loops | Mean tokens | Starts with cue | Seed base | Job id, run folder |
|---|---|---|---|---|---|---|---|
| base, cue | 164 | 77 | 1 | 9,344 | 328 | 3,000,000 | `abaybektursun-1114-151534-e72c`, `day1/hard328_base_cue_t10-01/` |
| V, plain | 161 | 74 | 0 | 9,075 | 328 | 81,000,000 | `abaybektursun-1114-201013-47c5`, `selfdistill/V_plain-01/` |
| V, cue | 167 | 74 | 0 | 8,625 | 328 | 82,000,000 | `abaybektursun-1114-201021-095e`, `selfdistill/V_cue-01/` |
| U, plain | 154 | 80 | 0 | 9,257 | 327 | 83,000,000 | `abaybektursun-1114-201028-1adf`, `selfdistill/U_plain-01/` |
| U, cue | 168 | 76 | 2 | 9,103 | 328 | 84,000,000 | `abaybektursun-1114-201035-c6c0`, `selfdistill/U_cue-01/` |
| S, cue | 171 | 65 | 1 | 8,535 | 328 | 85,000,000 | `abaybektursun-1114-201132-3c04`, `selfdistill/S_cue-01/` |
| theta(0.5), cue | 190 | 73 | 0 | 9,656 | 328 | 73,000,000 | `abaybektursun-1114-181228-34ad`, `day1_wdiff328/theta0.5_cue-01/` |
| RL, plain | 206 | 20 | 0 | 9,315 | 271 | 3,000,000 | `abaybektursun-1114-151540-86ef`, `day1/hard328_rl_plain_t10-01/` |

| Difference (paired, 328) | Points | 95 % interval |
|---|---|---|
| V cue minus base cue | 0.9 | [-3.0, 4.9] |
| V plain minus base cue | -0.9 | [-5.5, 3.7] |
| V plain minus U plain | 2.1 | [-2.1, 6.4] |
| V cue minus U cue | -0.3 | [-4.9, 4.3] |
| V cue minus S cue | -1.2 | [-5.5, 3.0] |
| S cue minus base cue | 2.1 | [-2.1, 6.7] |
| U cue minus base cue | 1.2 | [-3.0, 5.8] |
| V cue minus theta(0.5) cue | -7.0 | [-11.6, -2.7] |
| V cue minus RL plain | -11.9 | [-16.2, -7.9] |

Against base cue (164 right, 164 wrong), fixed / lost: V plain 29 / 32, V cue 25 / 22, U plain 22 / 32, U cue 30 / 26, S cue 31 / 24;
theta(0.5) cue 40 / 14, RL plain 49 / 7. The fine-tuned cells change about as many problems as a fresh sample of the base does, in
both directions; RL fixes many and loses few.

- Predictions (spec): D1 held (V plain 161, interval of V plain - base cue [-5.5, 3.7] includes 0). D2, the main claim, refuted
  (+0.9, [-3.0, 4.9]). D3 refuted at both prompt arms (plain +2.1 [-2.1, 6.4], cue -0.3 [-4.9, 4.3]): the vote selection adds
  nothing over a random own finished sample, and the length control S is no different (V cue - S cue -1.2). D4 held (11.9 points
  under RL plain). D5 held by its rule (74 and 74 cap hits under 77), but the difference is 3 problems.
- Published prior confirmed: arXiv 2607.13643 Table 1 (LMSI, vote-filtered SFT on own text, Qwen3-4B-Instruct) moves held-out
  AIME 2024 / 2025 by 0.0 / -0.8 points. Here on a pretrained base, 455 prompts, the same: the only effect is the format the
  training texts share (the cue opening), which the plain prompt then reproduces. That gain (base plain 76 -> 161) is the cue's
  own gain; the cue at inference gives it for free.
- Sanity cell, in-distribution (the 100 problems were trained on; a check that training worked, not a result): V plain on
  MATH-500 first 100 scores 90, all 100 answers start with the cue; base plain (T3) 49, base cue (T1) 82 on the same 100. Job
  `abaybektursun-1114-200050-c260`, `results/selfdistill/sanity_V_plain_math500_n100-01/`.
- Generation check (`train.json` `generations_before` / `_after`, greedy, 3 training prompts, plain prompt): before training the
  base writes `.\n\nOkay, so I need to ...` or `.\n\nTo convert ...`; after training all three arms write ` line!\n\nOkay, ...`.
- Hand read: per cell, 20 finished answers scored wrong (numpy seed 0, `--hand <arm>`): 0 of 20 right in each of the five cells.
  Five of the 100 have no extracted answer although the finish reason is `stop`: the model emitted the stop token mid-sentence
  (V plain 61, 179; U cue 91, 291) or after a repeated line (V cue 289: `2026 - 393 = 1633. Not a palindrome.` repeated). V plain,
  10 answers read (numpy seed 0): worked solutions or long unfinished reasoning at the cap; no empty answers in any cell; no
  copying of training solutions (largest share of an answer's 12-word sequences found in the V training texts: 1.7 %, mean
  0.05 %). Two tails: problem 150 (right) `...So he can't afford $51 shoes. Therefore, $50 is the maximum.\n\nSo the answer should
  be $50.\boxed{50}`; problem 109 (cap hit) `...sum to295.03°, which is roughly 295, but maybe it's 180° when weighted.
  295.03°=180° +115.`
- No two compared cells share a seed base; no two cells share an identical non-empty completion for any problem
  (`identical_nonempty_texts`, all 0).
- Not done: a second round of distillation (out of scope); more than one sample per cell (the five fine-tuned cells span 154 to
  171, inside one another's intervals).
- Cost at 3.95 USD per H100-hour (start to end record of each job, H100 80GB HBM3): smoke 4.4 min 0.29 USD
  (`abaybektursun-1114-193821-520c`, 8 longest U examples), train V 13.3 min 0.87, U 17.2 min 1.13, S 9.8 min 0.65, sanity 8.6 min
  0.56, V plain 51.5 min 3.39, V cue 48.2 min 3.17, U plain 52.1 min 3.43, U cue 51.1 min 3.36, S cue 46.0 min 3.03; 19.89 USD in
  all (limit 25). Training throughput 2,760 to 3,540 target tokens/s; a merge takes 29 to 47 s.
- Raw answers and adapters: `runs/<job-id>/` after `uv run tools/gpu.py get <job-id>`, and
  `s3://pg-lineage-769063704696/results/rlneurons/r5/selfdistill-01/<job-id>/` (`answers.jsonl` of the six scored jobs;
  `adapter.safetensors` and `train.json` of the three training jobs); training texts `.../selfdistill-01/data/arms-v1.jsonl`.
  Run: `uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.selfdistill`; tests
  `python -m studies.rlneurons.jobs.distill_data_test`; commands of every job in each run folder's `run.json`.

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

## Reward content test: the five Olmo 3 RL-Zero rewards on MATH-500 (board idea-46b68c, work-069eca)

Spec `specs/SPEC_reward5.md` (predictions R1-R5, written before the jobs). Does the MATH-500 gain over the cued base depend on
what the RL reward graded? AI2's five Olmo 3 RL-Zero models share the base `allenai/Olmo-3-1025-7B` (names and revisions in
`jobs/merge_weights.py` `OTHERS`). Cells: `run_cell` on `merge_weights --other <key> --alpha 1 --rounding nearest` (all 355
tensors identical to the named model in every job), T 1.0 / top-p 1.0, one sample, cap 16,384, grader v3, n = 500, the 3.1
tokenizer. Readout `results/reward5/readout.json`, written by `analysis/reward5.py`; one run folder
`results/reward5/<arm>-01/` per cell (`run.json`, `metrics.json`, `merge.json`, `examples.json`). Jobs at commit `3b4ab2a`.

| Model | Cue: right of 500 | Cue minus base cue, points [95 %] | Plain: right of 500 | Tokens per problem (cue) | Relative norm of the weight difference |
|---|---|---|---|---|---|
| base (T1, T3) | 410 | | 224 | 3,932 | |
| Math 3.0 | 448 | +7.6 [4.2, 11.0] | 443 | 4,527 | 0.127 % |
| Mix 3.0 | 440 | +6.0 [2.6, 9.4] | 372 | 5,203 | 0.090 % |
| General 3.0 | 429 | +3.8 [0.4, 7.0] | 323 | 3,839 | 0.064 % |
| Code 3.0 | 411 | +0.2 [-3.4, 3.8] | 360 | 3,069 | 0.151 % |
| IF 3.0 | 377 | -6.6 [-10.6, -2.6] | 55 | 2,667 | 0.138 % |
| Math 3.1 (day1_wdiff) | 457 | +9.4 [6.2, 12.6] | 463 | 4,696 | 0.13 % |
| Code 3.1 (day1_wdiff) | 450 | +8.0 [4.6, 11.2] | 390 | 3,336 | 0.109 % |

Paired bootstrap over problems, 5,000 resamples, seed 0. Other paired differences: Code 3.0 cue minus Math 3.0 cue -7.4
[-10.8, -4.0]; IF 3.0 cue minus Math 3.0 cue -14.2 [-17.8, -10.8]; Code 3.1 cue minus Code 3.0 cue +7.8 [4.4, 11.2]; Math 3.1
cue minus Math 3.0 cue +1.8 [-0.4, 4.2].

- R1 held: Math 3.0 with the cue is above the cued base.
- R2 refuted: the IF model gains nothing. Of its 123 wrong cue answers, 34 have a broken answer line (`Answer: Answer`, or an
  empty `Answer:`: 24 placeholder, 10 nothing extracted; counted from the rows, 6 read by hand and all 6 had the right value in
  the text); with all 34 counted right it is 411, level with the base. Plain, the IF model answers at once (median 5 tokens, 55 right).
- R3 refuted: Code 3.0 with the cue equals the cued base (411), 37 problems below Math 3.0. The 450 of Code 3.1 does not hold for
  the earlier Code release, although Code 3.0 moved the weights further (0.151 % against 0.109 %).
- R4: Mix held (-1.6 [-4.4, 1.2]); General refuted at the stated bound (-3.8 [-6.8, -0.8]).
- R5 held: Math 3.0 plain 443 (+219 over base plain); IF plain 55.

Reading: in the Olmo 3 models the gain follows the share of math in the reward (Math > Mix > General > Code = base > IF). The
earlier finding that the Code-RL difference gives the math gain (above, `day1_wdiff`) is a property of the 3.1 Code release. The
model cards do not state what changed between the 3.0 and 3.1 Code runs. No answer of any cell contains an `extra_id` token
text (the 3.0 tokenizer's `<think>`/`<answer>` ids print that way under the 3.1 tokenizer).

### Step 2: do the models change the same tokens? (`specs/SPEC_reward5_tokens.md`, predictions S1-S3)

`jobs/score_tokens.py` scores the 500 first answers of the cued base (job `abaybektursun-1114-153825-208b`, 405 right; 1,904,493
answer positions; 465 of 500 answers tokenize to the stored token count) under every model. r_m = log p_m(stored token) - log
p_base. Readout `results/reward5/tokens-01/metrics.json` (with `examples.json`: two positions with every model's numbers), written by
`analysis/reward5_tokens.py` from jobs `abaybektursun-1114-191457-f9da` and `abaybektursun-1114-193153-3c4c`. Intervals: bootstrap
over answers. The Mix model is loaded through `merge_weights --alpha 1` (its own `config.json` names a model type transformers
does not load; job `abaybektursun-1114-191504-5599` failed on it).

| Model | Pearson r of r_m with r_Math 3.1 [95 %] | Where Math 3.1's top token differs from the base's: share with Math 3.1's token / the base's | Mean abs r_m | Cue gain, points |
|---|---|---|---|---|
| theta(0.25) | 0.820 [0.811, 0.827] | 0.178 / 0.802 | 0.030 | +6.2 |
| Code 3.1 | 0.405 [0.400, 0.411] | 0.270 / 0.667 | 0.081 | +8.0 |
| Math 3.0 | 0.271 [0.259, 0.286] | 0.326 / 0.526 | 0.238 | +7.6 |
| Code 3.0 | 0.240 [0.229, 0.252] | 0.272 / 0.617 | 0.129 | +0.2 |
| Mix 3.0 | 0.168 [0.159, 0.179] | 0.221 / 0.703 | 0.103 | +6.0 |
| General 3.0 | 0.162 [0.153, 0.172] | 0.074 / 0.906 | 0.028 | +3.8 |
| IF 3.0 | 0.039 [0.030, 0.048] | 0.086 / 0.881 | 0.045 | -6.6 |
| random difference | -0.001 [-0.004, 0.003] | 0.013 / 0.983 | 0.004 | +1.4 |

Math 3.1 itself: mean abs r 0.159; its top token differs from the base's at 151,701 positions (8.0 %).

- Instrument checks passed: theta(0.25) highest, the random difference at 0.
- S1 held: Code 3.1 changes the same tokens as Math 3.1 (0.405), more than the earlier Math release does (0.271).
- S2 refuted: where Math 3.1's top token differs from the base's, Code 3.1 keeps the base's token (0.667) more often than it
  takes Math 3.1's (0.270).
- S3 held: the IF model is near the random difference.
- The agreement does not order the models by gain: Code 3.0 (no gain) agrees as much as Math 3.0 and more than Mix and General,
  which gain.
- Not a critic: the summed r_m over an answer separates right from wrong base answers at AUROC 0.853 for Math 3.1, the same as
  the answer's length alone (0.855); computed from the same files, not in `metrics.json`.

## Critic at decoding time: can the base's activations tell early which sample will fail? (board idea-eec971, work-5d5dc3)

Spec `specs/SPEC_critic.md` (predictions C1-C3, written before the activation job). Thesis tested: the rest of the RL gain is
reliability (result-afc423), so a critic that stops a failing sample early and starts again could replace the weight change.
Data: the 2,000 stored samples of the cued base on MATH-500 (4 per problem, T 1.0 / top-p 1.0, job
`abaybektursun-1114-153825-208b`, 1,642 right). No weights changed, no new samples.

**Stage 0, the ceiling** (`analysis/critic_ceiling.py`, `results/critic/ceiling-02/metrics.json`): stop-and-restart with a perfect
critic that looks once after 1,000 tokens, at most 4 samples, the last kept.

| Critic | Right of 500 | Tokens per problem |
|---|---|---|
| none: one sample | 405 | 3,808 |
| perfect, label-free flag (the sample is in the largest group of agreeing answers, group of 2 or more) | 438.7 | 4,125 |
| perfect, answer key | 459.2 | 4,013 |
| RL, one sample (plain) | 456 | 4,675 |

The label-free flag equals correctness on 96.5 % of base samples. `ceiling-01` compared answer strings instead of grouping
equal answers (the flag then matched correctness on 85.3 %); its numbers are superseded.

**Stage 1, the probe** (`jobs/critic_acts.py`, job `abaybektursun-1114-212139-0b2b`; `analysis/critic_probe.py`,
`results/critic/probe-02/`): logistic regression on the residual stream of layer 12, 20 or 28 at the position after 250, 500,
1,000 or 2,000 answer tokens, 5 folds by problem, trained on the label-free flag. The deciding number is the within-problem
AUROC: over problems with both outcomes among their samples, the share of (good, bad) pairs ordered correctly (0.5 = chance;
a probe that only knows how hard the problem is scores 0.5).

| After tokens (samples that long) | Best probe, within-problem AUROC [95 %] | Same probe trained on the answer key | Mean log-prob so far | Mean entropy so far |
|---|---|---|---|---|
| 250 (1,993) | 0.510 [0.448, 0.572] (L28) | 0.554 [0.498, 0.612] (L12) | 0.555 | 0.566 |
| 500 (1,854) | 0.542 [0.481, 0.600] (L12) | 0.551 [0.492, 0.610] (L12) | 0.551 | 0.565 |
| 1,000 (1,441) | 0.571 [0.509, 0.634] (L12) | 0.525 [0.460, 0.592] (L12) | 0.521 | 0.535 |
| 2,000 (977) | 0.509 [0.430, 0.589] (L20) | 0.510 [0.436, 0.586] (L20) | 0.498 | 0.491 |

110 to 137 problems have both outcomes at a checkpoint. Checks: at the last prompt token (same activations for all samples of
a problem) the within-problem AUROC is exactly 0.500; probes trained on flags shuffled within problems give 0.49 to 0.50 at 1,000
tokens; on synthetic activations with a planted signal the script finds it. Positive control on the real activations: across
problems the probe at the last prompt token predicts the flag at AUROC 0.73 to 0.77 (layers 12 to 28), so the probe can read what is there.

**Offline policy** (stop a sample at 1,000 tokens when its held-out probe score is below a threshold chosen on the training
folds, at most 4 samples): 414.1 of 500 at 4,345 tokens per problem, against 410.5 for one sample (mean of the 4) at 4,008 and 410.1
for the same stop rate with scores given to random samples; probe minus random +0.8 points [-0.7, 2.4].

- C1 refuted: 0.571 at 1,000 tokens, below 0.60, and the probe trained on the answer key does no better (0.525).
- C2 refuted: no rise with the checkpoint (0.51, 0.54, 0.57, 0.51).
- C3 refuted: 414 of 500, not 420, and not above the random score.

Reading: the base's residual stream encodes how hard the problem is before it writes anything, but not which of its own samples
of that problem will go wrong, at least not linearly at one position within the first 2,000 tokens. The 34 to 54 problems that a
perfect critic would add are not reachable by this critic. Limits: linear probe, one position per checkpoint, 2,000 samples, 3
layers; an interval upper end of 0.63 is not excluded; a critic that reads the finished answer was not tested. `probe-01` (string
flag, larger C values) gave the same reading: best 0.574 at 1,000 tokens, policy 416.8.

## Wrong steps: do the RL models make the base's own mistakes less likely? (board work-40ec05)

Spec `specs/SPEC_wrongstep.md` (predictions W1-W4). Items: the judged finished-wrong samples of the cued base on MATH-500 with a
located first wrong step (`results/anatomy/judge-01/labels.json`; 51 of 60 located by `jobs/score_tokens.py --labels`: 21 slip, 16
wrong plan, 14 misread; the 8 `format` items and 1 other have no quote in the text). Each whole answer is scored under 10
models (job `abaybektursun-1114-213223-4179`). D_m = [log p_m - log p_base] summed over the wrong step's tokens (median 29
tokens, median position 0.20 of the answer) minus the same sum over 200 control spans of equal length in the same answer. Readout
`results/wrongstep/math500-01/metrics.json`, per item `items.json`, written by `analysis/wrongstep.py`. Intervals: bootstrap over items.

| Model | Mean D, nats [95 %] | exp(mean D) | Median D | First 5 tokens of the step [95 %] | Cue gain on MATH-500, points |
|---|---|---|---|---|---|
| Mix 3.0 | -0.80 [-1.34, -0.28] | 0.45 | -0.39 | -0.40 [-0.65, -0.17] | +6.0 |
| Math 3.1 | -0.71 [-1.48, 0.01] | 0.49 | -0.26 | -0.35 [-0.69, -0.03] | +9.4 |
| Math 3.0 | -0.58 [-1.51, 0.35] | 0.56 | -0.17 | -0.66 [-1.10, -0.24] | +7.6 |
| Code 3.1 | -0.45 [-0.79, -0.12] | 0.64 | -0.42 | -0.21 [-0.38, -0.06] | +8.0 |
| Code 3.0 | -0.32 [-0.95, 0.27] | 0.72 | -0.05 | -0.29 [-0.56, -0.02] | +0.2 |
| General 3.0 | -0.14 [-0.31, 0.00] | 0.87 | -0.01 | -0.07 [-0.16, 0.01] | +3.8 |
| theta(0.25) | -0.10 [-0.22, 0.03] | 0.91 | -0.12 | -0.03 [-0.09, 0.04] | +6.2 |
| random difference | 0.00 [-0.02, 0.02] | 1.00 | 0.01 | 0.00 [-0.01, 0.01] | +1.4 |
| IF 3.0 | +0.17 [-0.07, 0.40] | 1.18 | 0.04 | +0.12 [0.02, 0.23] | -6.6 |

- W1 not met as written: Math 3.1's interval touches 0 (-0.71 [-1.48, 0.01]); on the first 5 tokens of the step it is below 0.
  The effect sits in a minority of items: the median is -0.26 and 57 % of items are below 0.
- W2 held: Code 3.0 (-0.32) and IF (+0.17) are above the mean of the four gaining models (-0.63). The order of the 9 models by D
  follows their cue gain (Spearman -0.67, n 9); Code 3.0 and theta(0.25) are the exceptions in opposite directions.
- W3 held at the point estimate: relative to other text of the same answer, Math 3.1 is 0.49 times as likely as the base to write
  the base's wrong step; the measured ratio of first wrong steps per 1,000 tokens is 0.39 (0.015 / 0.038, 'Checks or per-step error').
- W4 refuted: the base's wrong step is not an unlikely sample. Its log-probability per token under the base is -0.53 against
  -0.63 for control spans (span minus control +4.1 nats [-0.4, 9.9]). A rule that removes unlikely tokens cannot remove these
  steps, in line with the truncation results ('Truncation rules at T 1.0').
- By the judge's label, Math 3.1: misread -1.52 (n 14), slip -0.72 (n 21), wrong plan +0.03 (n 16). RL lowers the base's
  misreadings and slips, not its wrong plans; RL's own remaining errors are mostly wrong plans ('Slip against wrong plan').
- Instrument checks passed: the random difference is at 0; theta(0.25) has Math 3.1's sign and a seventh of its size.
- Two items read: problem 217 sample 1, slip '450 factors into 2 x 3^2 x 5^3' (it is 5^2): Math 3.1 D = -7.1. Problem 21 sample
  3, slip '1136 sqrt 7 - 88 sqrt 7 = 1148 sqrt 7': D = +5.2, RL does not mark it.

Limits: 51 items, wide intervals; the quote marks where a judge saw the error, and the judges are the team's subagents.

### Screening decoding rules on the same wrong steps (board work-d10ae6, `specs/SPEC_rulescreen.md`)

The same statistic D for rules that need only the base model (`jobs/rule_screen.py`, job `abaybektursun-1114-214538-9e63`;
`results/wrongstep/rules-01/`, written by `analysis/wrongstep.py <job> rules-01`). 51 items.

| Rule | Mean D, nats [95 %] | exp(mean D) | Median D | misread (14) | slip (21) | wrong plan (16) |
|---|---|---|---|---|---|---|
| temperature 0.6 | +0.77 [-0.21, 1.91] | 2.17 | +0.53 | +0.34 | +0.68 | +1.27 |
| problem contrast, a = 0.5: softmax(1.5 logits - 0.5 logits without the problem) | -0.58 [-1.01, -0.19] | 0.56 | +0.02 | -1.71 | 0.00 | -0.34 |
| problem contrast, a = 1 | -1.69 [-3.06, -0.53] | 0.18 | +0.08 | -4.62 | +0.07 | -1.44 |
| the problem stated twice | -0.07 [-0.24, 0.08] | 0.93 | -0.02 | -0.22 | -0.05 | +0.02 |

S1 not refuted (temperature 0.6 raises the wrong steps), S2 held (contrast lowers them, most on misreadings), S3 held weakly.
The contrast acts on a minority of items: its median D is at 0 and 41 % of items are below 0; slips are untouched. Both
contrast strengths pass the spec's bar for a generation test.

### Generation test from the prefix before each wrong step (board work-d10ae6, `specs/SPEC_prefixtest.md`)

Predictions G0-G2 were written before the run; the cap was lowered from 6,000 to 4,000 new tokens before the full run. Does a
rule that lowers the probability of the base's wrong steps (the screen above) produce more right answers when the text continues
from the token before the wrong step? 51 located wrong steps of the cued base, 6 continuations per prefix (306 per arm),
T 1.0 / top-p 1.0, grader v3 on prefix + continuation. Job `jobs/prefix_cell.py`, input
`data/wrongstep/base_cue_judged_rows_v1.jsonl` (the 60 judged rows of job `abaybektursun-1114-153825-208b`), readout
`analysis/prefixtest.py`, results `results/wrongstep/prefix-01/` (`metrics.json`, `per_prefix.json`, `examples.json`, `run.json`
with the job ids). Ran on vast.ai (RTX PRO 6000, 96 GB); raw rows are in `runs/<job id>/` on Abay's laptop, not in git. Jobs that
ran out of GPU memory on the longest prefixes kept their finished batches; the rest ran with `--start` at a smaller batch.

| Arm | Right of 306 | Percent [95 %] | Minus base, points [95 %] | Hit the cap | Right and ended before the cap |
|---|---|---|---|---|---|
| base, plain sampling (control) | 99 | 32.4 [23.2, 41.5] | | 170 | 90 |
| base, problem contrast a = 1 | 104 | 34.0 [24.2, 44.1] | +1.6 [-4.2, 7.8] | 177 | 96 |
| Math-RL 3.1 continues the base prefix | 132 | 43.1 [32.7, 53.6] | +10.8 [5.6, 16.3] | 167 | 90 |

By the judge's label (difference to base in points, interval over prefixes): contrast: misread (14 prefixes) +10.7 [-1.2, 22.6],
slip (21) -2.4 [-12.7, 9.5], wrong plan (16) -1.0 [-4.2, 2.1]; RL: misread +20.2 [8.3, 33.3], slip +7.1 [0.0, 13.5], wrong plan
+7.3 [1.0, 14.6].

- G0 held: the base continues to a right answer in 32.4 % of continuations (wrong plans 10.4 %, slips 49.2 %).
- G1 held by the registered statistic, with a caveat that changes its reading: all of RL's gain is in continuations that hit the
  cap. RL has 42 capped rows scored right against 9 for the base: it writes a boxed answer, then keeps checking until the cap, and
  grader v3 scores the last box. Counting only continuations that ended, RL and the base both have 90 right.
- G2 refuted: contrast minus base is +1.6 points [-4.2, 7.8]; the test excludes a gain above 8 points, not any gain. The direction on misreadings matches the screen (27 to 36 right of
  84) but its interval includes 0, and slips and wrong plans do not move. Cap hits are equal (177 against 170), so the rule does
  not break the text. Decision of the spec: no MATH-500 cell with this rule.
- Limit of the test: 55 % of continuations in every arm hit the 4,000-token cap, so more than half of each arm's rows are
  unfinished text.

### Is the answer already lost before the judged wrong step? (laptop, `analysis/prefix_vs_scratch.py`)

Right rate of the base's continuations from the prefix (table above) against the base's right rate from the start of the same
problem, in its other three stored samples, counting a from-scratch sample right only if it is right within the same token budget
(prefix tokens + 4,000). Results `results/wrongstep/prefix_vs_scratch-01/metrics.json`.

| Judge's label | Prefixes | From the start, within budget | From the prefix | Difference, points [95 %] |
|---|---|---|---|---|
| all | 51 | 42.5 % | 32.4 % | -10.1 [-19.6, -1.6] |
| slip | 21 | 47.6 % | 49.2 % | +1.6 [-11.9, 14.3] |
| misread | 14 | 64.3 % | 32.1 % | -32.1 [-50.0, -16.7] |
| wrong plan | 16 | 16.7 % | 10.4 % | -6.2 [-19.8, 5.2] |

Before a judged misreading half of the chance is already gone, so the misreading starts earlier than the sentence the judge
quoted (in 3 of the 14 prefixes it is visible in the prefix). For slips the two rates agree within about 13 points; that does not
separate 'no damage in the prefix' from a constant per-step error rate (53.9 % predicted from the prefix), so it is a failure to
reject, not a finding. The same numbers for RL
continuing the base prefix are in the file; they are not comparable in the same way, because 42 of RL's right rows are capped rows
scored on a box inside the reasoning.

### Problem dependence of the early text does not tell a wrong sample from a right one (work-2cd5d0, `specs/SPEC_probdep.md`)

d_t = log p_base(token | problem, text) - log p_base(token | empty problem, text) over the first 1,000 answer tokens of the 2,000
stored samples of the cued base (the quantity context-aware decoding adds to the logits, Shi et al. 2023, arXiv 2305.14739; here
only read). Job `jobs/probdep_tokens.py` (vast.ai job `abaybektursun-1115-014547-2c8c`, A100, input
`data/wrongstep/base_cue_answer_heads_v1.jsonl.gz`), readout `analysis/probdep.py`, results `results/wrongstep/probdep-02/`
(same numbers as `probdep-01`, plus one right and one wrong example and the feature without the first 50 tokens: mean d_t over
tokens 50 to 1,000 gives 0.504 [0.440, 0.568]; 62 % of the summed difference sits in the first 50 tokens, the restatement of the problem).
Within-problem AUROC of right against wrong (150 problems with both outcomes, 478 pairs, bootstrap over problems, 2,000 resamples):

| Feature | 250 tokens | 500 tokens | 1,000 tokens |
|---|---|---|---|
| mean d_t | 0.504 [0.447, 0.560] | 0.515 [0.459, 0.569] | 0.531 [0.468, 0.589] |
| mean of the lowest tenth of d_t | 0.515 | 0.559 [0.501, 0.615] | 0.575 [0.516, 0.637] |
| mean log p of the base alone | 0.517 | 0.544 | 0.519 [0.463, 0.576] |

Controls: mean d_t shuffled within the problem 0.483 [0.430, 0.540]; a shorter answer 0.680 [0.621, 0.738]; pairs where both
samples are longer than 1,000 tokens: mean d_t 0.552 [0.488, 0.616], shorter answer 0.735. Activation probe at 1,000 tokens (above):
0.571 [0.509, 0.634].

- P1 refuted: 0.531, interval includes 0.55. P2 not tested further (P1 failed).
- P3 refuted: among the judged wrong samples the mean d_t of misreadings is not the lowest (misread 0.132 nats per token, n 14;
  slip 0.094, n 21; wrong plan 0.154, n 17). Wrong samples have a higher mean d_t than right ones across problems
  (0.110 against 0.086): harder problems make the text depend more on the problem.
- Reading: the 4.62-nat drop of misread steps under contrast is a property of those few tokens, not of the early text of the
  sample. Three label-free signals now fail to separate the base's own samples of a problem early: activations, the base's own
  likelihood, and problem dependence. Answer length remains the strongest (0.68), and it is known only at the end.

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

## WSP-1 delta anatomy: what the RL weights changed (weights only, no forward pass)

Spec `specs/SPEC_wsp1.md`. Job `jobs/wsp_delta_anatomy.py` (`--selftest` runs 7 planted-input checks; the job runs them first),
Modal job `sameraslan-1114-153637-0929`, commit `97ac320`, 111 s for 355 tensors on an H200. Artifact:
`results/wsp1/anatomy-01/` (`summary.json`, `metrics.json` per tensor, `readout.json`, `run.json`). A delta is model minus
base `allenai/Olmo-3-1025-7B`; RL-Math = `Olmo-3.1-7B-RL-Zero-Math` `364820b`, RL-Code = `Olmo-3.1-7B-RL-Zero-Code` `1ca3bb3`,
Think-SFT = `Olmo-3-7B-Think-SFT` `6ff8575` (imitation of reasoning traces, no reward). Means are over the 224 layer matrices
(q, k, v, o, gate, up, down in 32 layers) unless stated. Null = a Gaussian delta of the RL-Math delta's norm, 5 seeds, layer 16.

| Quantity (`summary.json` key) | RL-Math | RL-Code | Think-SFT | Null |
|---|---|---|---|---|
| Delta norm / base norm (`layer_matrices.delta.*.rel`) | 0.24 % | 0.20 % | 24.8 % | |
| Entries bitwise equal to the base (`unchanged`) | 51 % | 56 % | 0.7 % | |
| Share of squared norm in the top 8 singular directions (`top8_share`) | 0.118 | 0.127 | 0.030 | 0.005 to 0.008 |
| Largest `top8_share` of one matrix (`hypotheses.H3`) | 0.391, layer 31 `v_proj` | | | 0.008 |
| Cosine with the RL-Math delta (`pair.*.cos`) | | 0.0160 | -0.00001 | sd 0.00013 |
| Overlap of top-8 output subspaces with RL-Math (`overlap_left`) | | 0.096 | 0.051 | 0.002 |
| Readouts in layers 24-31 with a cue token in the top 15 (`readout.json`) | 13 of 96 | 15 of 96 | 0 of 96 | 0 of 30 |

- The RL-Math delta's relative norm is the same in every layer (0.24 % to 0.27 %, `by_layer`), so its size says nothing about
  where the change matters; its spectrum does (top-8 share 0.09 to 0.22 by layer, highest in layers 0 and 27 to 31).
- Readout = a top-3 output direction of a layer's `mlp.down_proj` or `self_attn.o_proj` delta, times the base `lm_head`. In RL-Math
  the late MLP directions read as words of deliberation: layer 29 `down_proj` direction 1 `Okay, consider, considering`
  (cue token `Okay` at rank 0) against `perhaps, maybe, probably, possibly`; direction 2 `WAIT, wait, Wait`; layer 24
  directions 1 and 2 `recall, considerations, !\n\n, Consider, Okay`. One readout with a cue token and one without are
  in `readout.json` (layer 29 `down` direction 1 `+`; layer 31 `down` direction 0 `+`).
- H1 (the no-reward delta points the same way as RL) is refuted: mean cosine -0.00001 against a null sd of 0.00013. H2 holds
  (RL-Math and RL-Code share a part: cosine 0.016, 120 null sd). H3: the largest top-8 share is 0.39, below the 0.5 the
  spec named and 51 times the null. H4 holds (cue tokens in 13 of 96 late readouts, 0 of 30 null readouts).
- Not controlled: the top-8 subspace overlap of Think-SFT with RL-Math (0.051, 25 times the null) may come from directions
  that any fine-tune of this base shares; the overlap with the base weights' own top subspace is not measured.

## WSP-1 edited weights: which part of a weight change carries the gain

Spec `specs/SPEC_wsp1.md` (amendments 1 to 5). `jobs/wsp_edit.py` writes an edited model directory (selftest of 6 planted
checks runs first; BF16 by `merge_weights.to_bf16`, stochastic rounding), `jobs/run_cell.py --model-path` scores it,
`analysis/wsp1_readout.py` writes the run folders and `results/wsp1/readout.json` (run it with
`uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.wsp1_readout`; it reads the
cells from `runs/<job id>/`, copied with `tools/gpu.py get`). MATH-500, T 1.0 / top-p 1.0, one sample, grader v3. Raw rows
are in the Modal Volume `iterate-runs` of workspace sameraslan under the job ids in each `run.json`.

"Layer matrices" are the 224 q, k, v, o, gate, up, down tensors. `top8` = base + the top 8 singular directions of each
layer matrix's RL-Math delta (9.8 % of the delta's squared norm; the addition is 0.074 % of the weight norm;
`metrics.json` `edit`). `rand8` = the same 8 singular values with random orthonormal vectors. `bulk` = RL-Math minus its
top 8 directions. `sft1` = Think-SFT as released (imitation of reasoning traces written by other models, no reward).

All 500 problems (`results/wsp1/full500/<cell>-01/`, `readout.json` `full500_vs_references`); references T3 224, T1 410,
T2 463 from `results/rln4/grader_v3/readout.json`:

| Cell | Right of 500 | Against |
|---|---|---|
| `top8` plain | 427 | `rand8` plain +46.0 points [40.8, 51.0]; T2 (RL plain) -7.2 [-10.2, -4.2] |
| `rand8` plain | 197 | T3 (base plain) -5.4 [-11.5, 0.7], unpaired |
| `sft1` cue | 454 | T1 (cued base) +8.8 [5.4, 12.4]; T2 -1.8 [-4.2, 0.6] |
| `sft1` plain | 440 | T2 -4.6 [-7.8, -1.4] |

First 100 problems (`results/wsp1/screen100/<cell>-01/`), right of 100. Plain, seed base 80,000,000: base 34, RL 96,
`top8` 88, `rand8` 36, `bulk` 91, `bulk64` (RL minus its top 64 directions) 86, `top1` (one direction per matrix) 42,
`late3` (top 3 directions of `mlp.down_proj` in layers 24 to 31 only) 41, `sft1` 91, `sft025` (base + 0.25 of the Think-SFT
delta) 58. Cue, seed base 81,000,000: base 82, `sft1` 92, `sft05` 88, `sft025` 89.

- Eight directions per matrix of the RL change are sufficient (427 against the matched control's 197) and not necessary
  (`bulk` 91, `bulk64` 86 of 100): the change is redundant across directions. One direction per matrix is not enough.
- The same slice of the imitation change breaks the model: `sfttop8` and `sfttop64` (base + the top 8 or 64 directions of
  the Think-SFT delta, 3.7 % and 7.9 % of the weight norm) gave 0 right of the 6 and 1 answers that finished, 5 and 1 of them
  loops at the cap; both jobs then stopped on an IndexError in `lib/rln4_lib.onset_lines` (`screen100/sfttop8_plain-01/`,
  `sfttop64_plain-01/`, status crashed). The prediction of amendment 4 (not concentrated) held.
- Think-SFT with the cue solves 58 of the 65 problems that T2 solves and T1 does not (14 of 16 cap hits, 11 of 14
  misreadings, 14 of 14 slips, 7 of 9 wrong methods) and misses 17 of the 398 that both solve. A fresh sample of the cued
  base would also solve some of the 65; that share is not measured here.
- Closest published result: Spectral Rewiring (arXiv 2607.03065) keeps the RL gain with a compact part of the update on
  models that include this pair. New here: the matched-spectrum random control at 8 directions, the removal cells, and the
  comparison with a no-reward delta.
- Finding page: `tools/finding_eight_directions.py` (`/finding/eight-directions`, a tile on `/findings`). It compares the 8 directions
  with Base + cue, not with the plain prompt alone: on MATH-500 (plain prompt) 427 of 500 against Base + cue 410, +3.4 points, paired
  95 % interval −0.4 to 7.2 (from `full500/top8_plain-01/per_problem.json` and `results/rln4/t1_t2_items-01/per_problem.json`,
  5,000 resamples, seed 0); on the 328 harder problems with the cue 192 against 164 (+8.5 points [4.3, 12.8], branch `sharedsub`).

The 328 harder problems (amendment 5; `results/wsp1/hard328/<cell>-01/`, `readout.json` `hard328_vs_references`). `sft1`
cells use seed base 3,000,000, the seeds of the cued base and RL plain references. References are the Day-1 #1 cells of
`results/day1_hard328/readout.json`, paired by problem index through their 0/1 rows in `results/axis/hard328-01/vectors.json`:
cued base 164 (77 cap hits), RL plain 206 (20), RL cue 205 (25), plain base 76 (35). Mean tokens are the mean of `n_new`
(RL plain 9,315, cued base 9,344).

| Cell | Right of 328 | Cap hits | Mean tokens | Against (paired, points [95 % bootstrap]) |
|---|---|---|---|---|
| `sft1` cue | 219 | 89 | 10,123 | cued base +16.8 [12.5, 21.3]; RL plain +4.0 [0.0, 7.9]; RL cue +4.3 [0.9, 7.6] |
| `sft1` plain | 203 | 86 | 9,375 | RL plain -0.9 [-5.2, 3.4]; plain base +38.7 [33.2, 44.2] |

- The prediction of amendment 5 holds: `sft1` cue (219) is within 5 points of RL plain (190 to 222 right). Think-SFT
  is within 5 points of RL on the harder set, with more than 4 times RL's cap hits (89 and 86 against 20).
- The 328 were screened against the RL training prompts only. The full scan of the Think-SFT training data (section
  "Think-SFT training-data overlap", `results/wsp1/sft_overlap-03/`) finds 6 of the 328 in its training prompts, all in
  user turns; the `sft1` numbers above include those 6.

## WSP-2 hand-written edit: the cue written into one matrix with no RL weights

Spec `specs/SPEC_wsp2.md` (amendment 1). The edit changes one tensor, layer 31 `mlp.down_proj`, so that the base writes the
opening cue ` line!\n\nOkay` (3 tokens) when the answer starts. Keys are the mean inputs to that matrix at each cue position
over 128 calibration prompts (MATH-500 problems 100 to 227); values are the unembedding directions of the cue tokens; the
edit is the ROME-style key-value update that moves other inputs as little as their second moments allow, scaled by bisection
until each cue token has mean probability 0.95. It uses no RL weights, no reward and no answers. The control `cueprog_rand`
has the same keys and scales with random unit vectors as values (seed 0). The job solved the three keys jointly
(`handedit.json` `solution`: "joint: R K^T = I") and ran with `--batch 1`.

How to run: `bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_handedit --dir
/tmp/theta --batch 1 [--control] && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta
--model-label cueprog --prompt plain --set math500 --temperature 1.0 --top-p 1.0 --seed 80000000 --n 100 --commit <commit>`
(`run.json` of each cell has the exact command). `analysis/wsp1_readout.py` scores the cells (cell table `CELLS2`) and
writes `results/wsp2/<experiment>/<cell>-01/` and `results/wsp2/readout.json`.

First 100 MATH-500 problems, plain prompt, T 1.0, top-p 1.0, seed base 80,000,000, grader v3
(`results/wsp2/screen100/<cell>-01/`, `readout.json` `screen100_differences`). References are the WSP-1 cells of
`results/wsp1/screen100/` on the same problems (the cued base used seed base 81,000,000; pairing is by problem).

| Cell | Right of 100 | Cap hits | Open with `Okay` | Against (paired, points [95 % bootstrap]) |
|---|---|---|---|---|
| `cueprog` | 85 | 5 | 96 | `cueprog_rand` +47.0 [36.0, 58.0]; base plain +51.0 [41.0, 61.0]; base cue +3.0 [-4.0, 11.0]; `top8` -3.0 [-10.0, 3.0]; RL -11.0 [-18.0, -5.0] |
| `cueprog_rand` | 38 | 1 | 19 | base plain +4.0 [-3.0, 11.0] |
| base plain | 34 | | | |
| base cue | 82 | | | |
| `top8` plain | 88 | | | |
| RL plain | 96 | | | |

- `handedit.json` (in `metrics.json` `handedit`): mean held-out probability of the 3 cue tokens in their contexts (64
  prompts, problems 228 to 291) 0.000, 0.006, 0.286 before and 0.952, 0.952, 0.952 after; the control leaves them at 0.000,
  0.004, 0.305. Mean KL(base || edited) on other positions 6.6e-05 nats (control 5.9e-06). The edit is 6.6 % of the
  tensor's Frobenius norm in both cells.
- H1 (the edit reproduces the cue) holds on the screen: 85 right and 96 of 100 answers open with `Okay`, and the control
  is 47 points lower.
- H2 (the edit goes past the cue) is refuted: 85 is not above 92, and `cueprog` is 3.0 points above the cued base with an
  interval that includes 0.
- Closest published result: Wang et al. (arXiv 2610.06851, App. D.5) report a one-matrix edit that raises the cue
  probability to 0.95 and scores 0.78 on MATH-500.

All 500 MATH-500 problems, plain prompt, T 1.0, top-p 1.0, one sample, grader v3, commit `db7c499`
(`results/wsp2/full500/<cell>-01/`, `readout.json` `full500_vs_references`). `cueprog` seed base 184,000,000 (job
`sameraslan-1114-221130-eb90`), `cueprog_rand` 185,000,000 (job `sameraslan-1114-221138-a65c`). References: T3 plain base
224, T1 cued base 410, T2 RL 463 (`results/rln4/grader_v3/readout.json`), `top8` 427 and `rand8` (`results/wsp1/full500/`).

| Cell | Right of 500 | Wilson 95 % | Cap hits | Open with `Okay` | Against (paired by problem, points [95 % bootstrap]) |
|---|---|---|---|---|---|
| `cueprog` | 397 (79.4 %) | [75.6, 82.7] | 21 | 92.6 % (463) | `cueprog_rand` +38.6 [34.0, 43.6]; T1 cued base -2.6 [-6.4, 1.2]; T2 RL -13.2 [-16.6, -9.8]; `top8` -6.0 [-9.8, -2.0]; `rand8` +40.0 [34.8, 45.0] |
| `cueprog_rand` | 204 (40.8 %) | [36.6, 45.2] | 8 | 21.2 % (106) | `rand8` +1.4 [-4.6, 7.0] |

- H1 (the edit reproduces the cue) holds on all 500: 79.4 % is within 10 points of the cued base (82.0 %), 92.6 % of
  answers open with `Okay`, and the control is 38.6 points lower.
- H2 (the edit goes past the cue) is refuted: 79.4 % is not above 92 %, and `cueprog` is 2.6 points below the cued base
  with an interval that includes 0.
- Finding page: `tools/finding_hand_written_edit.py` (`/finding/hand-written-edit`).

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

## Checks or per-step error: does RL check more, or err less per step? (MATH-500, n = 500, 4 samples, laptop, board work-768257, idea-60d3e1)

Question: is RL more reliable than the cued base because it checks its work more, or because each step is less often wrong?
Answer: RL writes more checking markers, 13.1 against 9.5 per 1,000 tokens (paired +3.6 [3.4, 3.9], 457 of 500 problems), but
checking text does not separate right from wrong samples of the same model and problem (base, right minus wrong at matched
length: +0.08 [-0.64, 0.77]; the spec asked for +1.0), a wrong step is followed by markers at the same rate as any other
position, and 6 % of check events fix something, RL no more than the base. What differs is the number of wrong steps left in
finished answers: 0.015 first wrong steps per 1,000 tokens for RL against 0.038 for the base. Spec, marker list and
hypotheses, written before the script: `specs/SPEC_checks.md`. Inputs: attempt 0 of samples 0 to 3 of the two Day-1 #3 jobs,
grader v3, and the located first wrong steps of `results/anatomy/judge-01/labels.json`. A token position is character x
n_new / len(text) (no tokenizer on the laptop). Intervals: bootstrap over problems, 5,000 resamples, seed 0.

Markers (frozen in the spec, case-insensitive): backtrack `wait, hold on, hmm, actually, oops, scratch that, on second
thought`; check `check, double-check, recheck, re-examine, verify, confirm, sanity`; error `mistake, error, wrong, incorrect,
correction, miscalculat*, misread, messed up, that can't be, doesn't make sense, not right / correct`. Primary measure: the
three families together. `alternatively, perhaps, maybe` is reported apart.

a. Base against RL on the same problems (markers per 1,000 tokens, per problem, its samples pooled):

| Samples | Problems | Base with cue | RL | RL minus base [95 %] |
|---|---|---|---|---|
| all | 500 | 9.51 | 13.13 | +3.62 [3.37, 3.87] |
| finished | 497 | 9.56 | 13.12 | +3.56 [3.31, 3.81] |
| right only | 465 | 9.58 | 13.15 | +3.57 [3.30, 3.82] |
| all, backtrack family | 500 | 6.12 | 9.74 | +3.62 [3.41, 3.84] |
| all, check family | 500 | 2.42 | 2.30 | -0.12 [-0.18, -0.05] |
| all, error family | 500 | 0.97 | 1.08 | +0.11 [0.04, 0.19] |
| all, `alternatively, perhaps, maybe` | 500 | 3.31 | 6.00 | +2.69 [2.48, 2.90] |
| all, cell base 3 of 4 and RL 4 of 4 | 86 | 10.03 | 13.69 | +3.66 [3.08, 4.25] |

- H2 (RL checks more) holds, and the whole difference is the backtrack family (`wait`); RL writes `check / verify` slightly
  less often. By base k of 4 the difference is +4.2, +3.4, +3.2, +3.8, +3.6 for k = 0 to 4: the same where the base fails and
  where it does not. Pooled over all tokens: 9.17 and 13.24. The planner's preview (9.7 against 7.1, another list) has the
  same direction.

b. Wrong against right samples of the same model and problem (markers per 1,000 tokens; "first N" = the first N tokens of
every wrong x right pair, N the shorter of the two):

| Model, wrong samples | Problems | Right | Wrong | Wrong minus right [95 %] | First N: right | wrong | Wrong minus right [95 %] |
|---|---|---|---|---|---|---|---|
| base, any wrong | 150 | 9.70 | 9.07 | -0.63 [-1.28, 0.01] | 9.56 | 9.48 | -0.08 [-0.77, 0.64] |
| base, finished-wrong | 124 | 9.73 | 9.03 | -0.70 [-1.38, -0.04] | 9.68 | 9.48 | -0.20 [-0.96, 0.55] |
| RL, any wrong | 57 | 12.96 | 13.28 | +0.32 [-0.29, 0.90] | 13.11 | 14.22 | +1.10 [0.42, 1.80] |
| RL, finished-wrong | 50 | 13.30 | 13.49 | +0.20 [-0.45, 0.86] | 13.48 | 14.49 | +1.02 [0.24, 1.79] |

- H1 (per-step error, not checking; refuted if right samples have at least 1 more marker per 1,000 tokens) is not refuted.
  The largest difference in that direction is the base's 0.70 over the whole answer, and it is 0.20 [-0.55, 0.96] at matched
  length: wrong answers are longer and their late part has fewer markers. In RL the wrong samples have more markers.

c. Around the located first wrong steps (pass A quotes; 300 tokens before the quote and 300 after its end):

| Steps | n (with a right sibling) | Markers per 1k after the step | Same position, right siblings | Random positions, same answer | Marker within 500 tokens after | Random positions |
|---|---|---|---|---|---|---|
| base, all | 52 (40) | 9.2 (40), 9.3 (52) | 9.2, difference -0.01 [-2.46, 2.60] | 9.7, -0.38 [-2.56, 1.85] | 46 of 52 (88 %) | 87 % |
| base, slips | 21 (18) | 7.6, 7.8 | 7.8, -0.18 [-3.95, 4.11] | 9.3, -1.55 [-4.94, 2.15] | 18 of 21 (86 %) | 86 % |
| RL, all | 30 (24) | 14.4, 13.7 | 14.3, +0.14 [-4.28, 4.54] | 13.3, +0.41 [-2.62, 3.69] | 30 of 30 | 91 % |

- H4 (the base does not notice its slips) is not refuted: after a wrong step the marker rate equals that of a right sibling
  at the same relative position and of random positions. The base writes a marker within 500 tokens after 46 of 52 wrong
  steps and still ends wrong; that is the rate of any 500-token window (87 %), so a marker after a slip is not a detection.
  Before the step the rates are also equal (base 8.8 against 9.4 in the siblings).
- 11 base slips read from the step on (`results/checks/math500-01/hand_reads.json`): in 6 a check follows and repeats the
  slip (`150 + 130 + 150 + 130 = 580` is written three times under "let me verify" and "check the calculations again",
  problem 189; three recounts each leave out day 27, problem 128); in 3 the answer notices two values that disagree and keeps
  the wrong one (21, 52, 60); in 2 the wrong step is never looked at again.

d. Effective checks. A check event is a marker with no marker in the 100 characters before it: 5.61 per 1,000 tokens in the
base's right samples, 6.75 in RL's. 40 events per model from right samples (seed 0, one per problem) and 20 planted controls,
labeled blind by judges that see the problem and about 250 tokens on each side of the marked word, not the model or the
score. Judges: Claude Code subagents (the agent's own model), rubric `results/checks/judge-01/rubric.md`, one subagent per
batch, two passes over all 100 items in other batches and orders. No hosted provider key works on this machine.

| Label (pass A; pass B) | Base, 40 | RL, 40 |
|---|---|---|
| fix: a specific earlier statement was wrong and is corrected | 3; 4 | 2; 1 |
| switch: the method or the reading changes | 4; 5 | 3; 4 |
| confirm: an earlier statement is tested and kept | 21; 21 | 21; 22 |
| filler: nothing is re-examined | 12; 10 | 14; 13 |

- Agreement of the two passes: 74 of 80 with the same label, Cohen's kappa 0.88 (fix or not: 78 of 80). Both passes are the
  same model, so this is its consistency. Controls (pass at 8 of 10): planted filler 10 and 9 of 10, planted correction 10
  and 10 of 10. The planted items are easy (`Wait, that's not right. Let me redo that:`), so they show that the labels work
  on a clear case, not on a subtle one.
- H3 (RL's checks fix more often) is refuted: fix share RL minus base -2.5 points [-12.5, 7.5] in pass A, -7.5 [-17.5, 2.5]
  in pass B. Over both models 5 of 80 events are a fix (6 % [3, 14]), 53 % confirm, 33 % are filler.
- The spec's rule for a revising event (a retraction cue and a new number in the next 200 tokens) is rejected: of 20 flagged
  events read by hand 3 revise a value (base 3 of 10, RL 0 of 10), and of the 14 judged events it flags the judges call 2 a
  fix or a switch (they label 12 so). Its shares (12 % of base events, 10 % of RL events) are not used.
- 12 RL spans read (`results/checks/judge-01/hand_reads_rl.json`): 4 fix a value (1.3 squared 1.79 to 1.69, problem 159; a
  point recomputed, 497; two start from two computations that disagree, 394 and 180), 1 fixes wording, 3 switch method, 4
  confirm or are filler.

e. Wrong steps per token:

| | Base with cue | RL | Base over RL |
|---|---|---|---|
| Finished samples, tokens | 1,910, 6.54 M | 1,968, 8.85 M | |
| Finished-wrong samples (one first wrong step each) | 250 | 131 | |
| First wrong steps per 1,000 tokens | 0.038 | 0.015 | 2.6 |
| Of those slips (judged 21 of 60, 5 of 30), per 1,000 tokens [Wilson of the share] | 0.013 [0.009, 0.018] | 0.0025 [0.0010, 0.0050] | 5.4 |
| Fixes per 1,000 tokens of right samples (events x fix share, pass A) [Wilson of the share] | 0.42 [0.15, 1.11] | 0.34 [0.09, 1.11] | |

- A fix is about ten times as frequent as a remaining first wrong step in both models (0.42 against 0.038, 0.34 against
  0.015). So most errors that are made are corrected by both models, and the share that is missed (8 % base, 4 % RL from these
  point values) is not separable with 40 events per model. What the data exclude is that RL's 3.6 extra markers per 1,000
  tokens are extra fixes: its fix rate is not above the base's, and its extra markers are `wait` in confirmations and filler.
- Not measured: whether RL makes fewer errors or resolves a detected conflict right more often. The hand reads point to the
  second as a part of it (the base notices the conflict in 21, 52 and 60 and keeps the wrong value; RL in 394 and 180 goes
  back to the wrong step), on 5 spans.

Prediction for work-74703c (steering Wait into the cued base), filed on that item before it reports: at the dose that brings
the base to RL's marker rate, accuracy on MATH-500 changes by 0 points, within -2 to +1, against the no-steering control of
the same code, and tokens per problem rise; larger doses lose points to cap hits. Refuted by a gain of 3 points or more over
both the no-steering and the random-direction control at n = 500. Consistent priors: an appended review pass changes the
base by 0.0 points (result-96e819), and zero-RL raised MATH-500 with `wait` below 0.05 per 1,000 tokens in 17 of 18 runs
(arXiv 2610.30882, Sec. 4, from the team's memory).

Limits: markers are words, not checks (a third of the events are filler); 4 samples per problem; first wrong steps exist only
for 82 finished-wrong samples and slips in cap hits are unlabeled; 40 judged events per model, from right samples only; one
judge model of the agent's own family; hand reads by one reader who knew the model; observational, MATH-500 only.

Run folders: `results/checks/math500-01/` (`readout.json`: tables a, b, c, the rule and the uncaught part of e;
`examples.json`: a base slip with no marker in the 500 tokens after it (problem 245), one with markers after it that still
ends wrong (problem 1), a sibling set with its rates; `rule_sample.json`: the 20 rule-flagged events; `hand_reads.json`;
`run.json`) and `results/checks/judge-01/` (`readout.json`: labels, agreement, controls, table e; `labels.json`: both passes'
label and reason per item with its excerpt; `examples.json`: a check that fixes a slip in RL (problem 497) and in the base
(195), a filler, a disagreement of the passes, a planted control of each kind scored right (pass A scored none wrong);
`hand_reads_rl.json`; `rubric.md`; `run.json`). The batch files and raw labels are in `runs/checks_judge/` (not committed).

```
R="--base runs/abaybektursun-1114-153825-208b --rl runs/abaybektursun-1114-183640-e828"
PY="uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.checks"
$PY stats $R --labels studies/rlneurons/results/anatomy/judge-01/labels.json --out studies/rlneurons/results/checks/math500-02
$PY prep $R --work runs/checks_judge-02
$PY score $R --work runs/checks_judge-02 --stats studies/rlneurons/results/checks/math500-02/readout.json --out studies/rlneurons/results/checks/judge-02
```

## Exchange-rate table: every method as one logit shift, and its transfer to the 328 (laptop, board work-c45b70, idea-31636e)

Question: if all arms lie on one axis (section above), each method is one number. What is it, what does it cost, and does it
predict the 328 better than "same point gain"? Answer: no better. Leave-one-arm-out over the 5 arms on both sets, the
calibrated logit rule misses the 328 score by 5.1 problems on average and "same point gain" by 5.1 (rerun noise 4, binomial sd
5.7); on the two held-out vote cells scored so far the logit rule misses by 8.4 and the point rule by 3.7. The logit scale
does rule out two other rules: "same relative error reduction" misses by 45.0 and "same change in the logit of the total" by
25.2. Spec and hypotheses, written first: `specs/SPEC_rate.md`. Code: `analysis/rate.py` (imports the fit of `axis.py`);
planted test: `analysis/rate_test.py`.

Method. Item difficulties from `axis.fit` on the 36 single-sample arms (ridge 0.3); the ability of any 0/1 vector is the
maximum-likelihood a given those difficulties, so votes and restarts get an ability too. Shift = ability minus the ability of
base + cue sample 0 (405 of 500; the pooled four samples sit 0.12 above it). Interval: paired bootstrap over problems, 2,000
resamples, 95 %. Noise floor: the sd of the abilities of four same-config samples is 0.12 logits (base + cue) and 0.17 (RL
plain); one single-sample shift has a 95 % interval of about +/- 0.4. Tokens per problem from each run's `metrics.json`.
All 47 rows: `results/rate/math500-01/table.md` and `table.json`; selected rows:

| Method (MATH-500) | Right of 500 | Shift, logits [95 %] | Tokens per problem | Training signal |
|---|---|---|---|---|
| RL plain, vote over 4 after restart | 475 | +2.46 [+2.03, +2.92] | 19,864 | RL reward |
| RL plain, vote over 4 | 474 | +2.40 [+1.95, +2.84] | 18,747 | RL reward |
| RL plain, one sample (4 samples) | 456 to 464 | +1.46 to +1.83 | 4,675 | RL reward |
| RL, cue | 457 | +1.50 [+1.06, +1.94] | 4,696 | RL reward |
| Think-SFT, cue | 454 | +1.38 [+0.91, +1.87] | 4,888 | SFT data |
| base + cue, vote over 4, ties to the shortest | 453 | +1.34 [+1.01, +1.71] | 16,034 | none |
| base + 0.5 (RL - base), cue | 452 | +1.30 [+0.87, +1.75] | 4,626 | RL reward (weights) |
| Code-RL 3.1, cue | 450 | +1.22 [+0.79, +1.66] | 3,336 | RL reward, other task |
| base + cue, vote over 4 after restart | 450 | +1.22 [+0.90, +1.58] | 19,697 | none |
| base + cue, vote over 4 | 446 | +1.08 [+0.79, +1.40] | 16,034 | none |
| base + 0.25 (RL - base), cue | 441 | +0.91 [+0.52, +1.28] | 4,036 | RL reward (weights) |
| base + cue + 3 RL-written solved problems (n 497; a second draw of examples has 404, see below) | 435 | +0.81 [+0.43, +1.20] | 4,379 | RL reward (text in context) |
| base + top 8 directions of the RL delta, plain | 427 | +0.51 [+0.05, +0.97] | 3,962 | RL reward (weights) |
| base + random difference, cue (control) | 417 | +0.26 [-0.11, +0.63] | 3,944 | none |
| base + cue + 3 base-written solved problems (n 497) | 414 | +0.26 [-0.12, +0.62] | 3,365 | own samples (in context) |
| base + cue, restart up to 2 | 413 | +0.17 [+0.06, +0.31] | 4,852 | none |
| base + cue, sample 0 (reference) | 405 | 0 | 3,808 | none |

Test-time methods against the model's own single sample (pooled four samples; restart against sample 0):

| Method | Base + cue: logits [95 %], points | Extra tokens | Logits per 1,000 extra tokens | RL plain: logits [95 %], points | Extra tokens | Logits per 1,000 |
|---|---|---|---|---|---|---|
| restart, up to 2 | +0.17 [+0.06, +0.31], 1.6 | 1,044 | 0.164 | +0.09 [+0.00, +0.22], 0.4 | 224 | 0.383 |
| vote over 2 (mean of 6 subsets) | +0.18 [+0.07, +0.30], 1.6 | 4,008 | 0.045 | -0.01 [-0.14, +0.12], -0.1 | 4,687 | -0.003 |
| vote over 3 (mean of 4 subsets) | +0.81 [+0.65, +0.99], 6.2 | 8,017 | 0.101 | +0.43 [+0.26, +0.64], 1.7 | 9,374 | 0.046 |
| vote over 4 | +0.96 [+0.74, +1.24], 7.1 | 12,025 | 0.080 | +0.76 [+0.49, +1.11], 2.8 | 14,060 | 0.054 |
| vote over 4, ties to the shortest | +1.22 [+0.96, +1.53], 8.5 | 12,025 | 0.102 | | | |
| vote over 4 after restart | +1.11 [+0.85, +1.43], 7.9 | 15,689 | 0.071 | +0.83 [+0.55, +1.19], 3.0 | 15,177 | 0.055 |

- One logit costs the base about 12,000 extra generated tokens per problem by voting (0.08 to 0.10 logits per 1,000). The RL
  weights give +1.4 to +1.5 logits for about 900 more tokens per problem, Think-SFT +1.38 for about 1,100, half of the RL
  weight difference +1.30 for about 800. The label-free vote with ties to the shortest answer (+1.34) equals half the RL
  weight difference at 3.5 times the tokens. A vote over 2 buys nothing (ties go to sample 0).
- In logits the vote is worth about the same for both models (+0.96 base, +0.76 RL; intervals overlap); in points it is 7.1
  against 2.8.
- Theta sweep (cue, against the pooled base): 0.25 +0.80, 0.5 +1.18, 0.75 +1.15, 1 +1.39, 1.25 +1.11, 1.5 +1.22. Ability is
  not linear in theta: theta 0.25 has 57 % of the full shift and theta 0.5 lies 0.49 logits above the line through 0 and 1
  (4.1 sd of the base noise floor, 2.9 of RL's): H3 refuted. Past theta 0.5 the points are inside noise of each other. The
  random difference of the same norm sits at +0.15 (1.2 sd): inside noise.

Transfer MATH-500 -> hard328 (`results/rate/transfer-01/readout.json`). Reference: pooled base + cue (410.5 of 500; 162 of
328 from the two runs 164 and 160). Each arm held out of the hard328 difficulty fit and of the calibration. Rules: Lc =
Rasch logit shift times c, c the slope of hard328 shift on MATH-500 shift over the other arms (0.81 to 0.89; all five 0.87);
L1 = the same with c = 1; P = same point gain; M = same change in logit of the total; R = same relative error.

| Held-out arm | Observed of 328 | Lc | L1 | P | M | R |
|---|---|---|---|---|---|---|
| RL plain | 206 | 201.7 | 210.0 | 194.5 | 232.8 | 253.8 |
| RL cue | 205 | 197.7 | 205.9 | 192.5 | 227.4 | 248.3 |
| theta 0.25 cue | 182 | 184.3 | 187.7 | 182.0 | 201.4 | 218.6 |
| theta 0.5 cue | 190 | 195.2 | 199.1 | 189.2 | 218.8 | 239.0 |
| Code-RL 3.1 cue | 187 | 193.3 | 197.4 | 187.9 | 215.5 | 235.3 |
| Mean absolute error, problems | | 5.07 | 5.99 | 5.14 | 25.18 | 44.97 |

- H1 (Lc better than P): 5.07 against 5.14 is a tie inside noise, and the held-out cells below go to P. Read as refuted:
  the logit shift does not predict the 328 better than the point gain. P is within 1 problem on the three partial arms and
  12 low on the two RL arms; Lc is 4 to 7 low on RL and 2 to 6 high on the others.
- H2 (the item model adds to the logit of the total): holds, 5.1 against 25.2.
- Planted test (20 seeds, 5 arms each, a known one-axis model, second set 2.2 logits harder): Lc 8.5, L1 8.4, M 9.2, P 15.2,
  R 20.8 problems; an arm with +1.2 logits on the first set only shows an error of 51.9 problems (4.8 sd). So the instrument
  can tell Lc from P when a one-axis world separates them; on the real pair of sets the two rules happen to agree.

Predictions filed before the cells were read (`results/rate/predict-01/`, commit `640d00b`, pushed 04:44:16 UTC;
`predict-02/`, commit `14e2f4e`, 04:49:14 UTC; scores in `results/rate/scored-01/readout.json`):

| Cell | Predicted right [80 %] | Point rule | Observed | Error Lc, P | Inside 80 % |
|---|---|---|---|---|---|
| hard328 base + cue, vote over 4, no restart (result-1dedfe) | 188.5 [179, 198] | 185.3 | 179 | +9.5, +6.3 | yes (on the edge) |
| hard328 RL plain, vote over 4, no restart, 246 finished problems (result-1dedfe) | 168.2 [160, 177] | 159.9 | 161 | +7.2, -1.1 | yes |
| hard328 base + cue, vote over 4 after restart | 192.3 [182, 202] | 187.9 | running | | |
| hard328 RL plain, vote over 4 after restart | 227.1 [217, 239] | 215.8 | running | | |
| hard328 base + cue + 3 RL-written solved problems | 181.4 [171, 192] | 179.8 | running | | |
| hard328 base + top 8 directions, cue | 173.1 [164, 193] | 172.8 | not found on the board | | |
| hard328 vote distillation V, cue and plain (category prior) | 175.5 [162, 189] | none | running | | |
| hard328 unfiltered control U, cue and plain (category prior) | 162.0 [151, 173] | none | running | | |
| MATH-500 shots, second draw, RL-written (of 497; job `abaybektursun-1114-195350-bc00`) | 435 [422, 448] | the same | 404 | +31 | no |
| MATH-500 shots, second draw, base-written (of 497; job `abaybektursun-1114-195357-6936`) | 414 [399, 429] | the same | 405 | +9 | yes |
| MATH-500 shots, second draw, Code-RL-written (of 497) | 412 [397, 427] | the same | not submitted | | |
| MATH-500 Think-SFT cue, vote over 4 | 473.1 [466, 480] (`axis.py`: 471.5 +/- 7) | 489.5 | not run | | |

- The second draw of RL-written examples (problems 3, 5, 6 as examples) has 404 of 497, against 435 for the first draw and
  405 for base-written examples: the +0.81 logits of the RL-written row belong to one draw of three examples, not to the
  method. Counted here from the finished jobs' `answers.jsonl` (`score_v3`, 406 and 408 of 500 before masking); the owner's
  readout (work-be7af1) is the reference.
- On the two scored hard328 cells the vote gained less on the 328 than either rule said (base +19.5 problems over its own four
  samples' mean of 159.5; Lc predicted +26.5, P +23.3). Mean absolute error: Lc 8.35, P 3.7, M 23.4, R 36.65. Scored in all: 4 of 14 filed cells, 3 inside their 80 % interval.
- The V and U rows are category priors, not measured shifts (those arms were trained on MATH-500). The note in
  `predict-01/predictions.json` about "246 of 328" misread a problem count as a score; no hard328 vote score was seen
  before filing (`predict-01/run.json`).

Limits. Five arms on both sets, one sample each on the 328, all of them RL-weight arms; the two scored held-out cells are
votes. Difficulties on the 328 come from 7 arms, which is why c is below 1. Tokens are generated tokens only; the three
solved problems in context add prompt tokens that are not counted.

Run: `uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.rate table|transfer|score`
(`predict`, `predict2` refuse to overwrite the filed files); `... python -m studies.rlneurons.analysis.rate_test`.

## Slip-hazard law: is the RL gain one constant hazard ratio? (MATH-500 n = 500, hard328 n = 328, laptop, board work-26c268, idea-7928c0)

Question: is P(right) = exp(-h L_i), with each method multiplying the hazard h by one constant on every problem, a better
description of the arms than the Rasch logit model? Answer: no. Held out, the hazard link fits worse than the logit link
(-0.2854 against -0.2790 nats per cell, 17,991 cells, all 5 folds; the test separates the two links with power 1.0 at this
size), and RL's hazard ratio is not constant: 0.48 on the hardest problems, 0.23 in the middle, 0.11 on the easiest. The
law is refuted as stated. What survives: one number per method on the logit scale, and the size of the average ratio (RL
0.33 to 0.37, matching the 0.39 ratio of located first wrong steps per token). Spec, hypotheses and amendments:
`specs/SPEC_hazard.md`. Code: `analysis/hazard.py` (imports the fit and loaders of `axis.py` and `rate.py`); planted checks:
`analysis/hazard_test.py`. Literature (read by a subagent, WebSearch because `tools/exa.py` had no key): the constant-hazard
form is published for agent tasks against human task time (Ord, arXiv 2505.05115, tested only by eye and by T80/T50 = 0.322
predicted against 0.25 measured) and was later found to fit worse than a declining hazard (Weibull shape about 0.6 for
every model, Ord's post of 4 Feb 2026); no paper found compares a hazard link with a logit link on item-level LLM data or
states a hazard ratio for a base-against-RL pair.

Model. Hazard link: -log p_ij = exp(-(a_j + b_i)); hazard ratio of an arm against the pooled 4 base + cue samples =
exp(-(a_arm - a_ref)). Logit link: `axis.fit`. Same parameters (one per arm, one per problem), same Adam loop, ridge on b
chosen per link on the 5 folds of `axis.py` (logit 0.3, hazard 1.0). The 17 problems that every arm or no arm solves stay
in both fits; on the 483 others alone the difference is the same (-0.0063).

1. Link (H1, refuted). T = held-out log-likelihood per cell, hazard minus logit:

| | T, nats per cell |
|---|---|
| Real matrix (36 arms x 500 problems) | -0.0064 (folds -0.0074, -0.0064, -0.0088, -0.0044, -0.0050; se 0.0008) |
| 200 matrices simulated from the fitted logit model | -0.0026 [5 %, 95 %: -0.0048, -0.0010], minimum -0.0063 |
| 200 matrices simulated from the fitted hazard model | +0.0031 [+0.0021, +0.0042], minimum +0.0011 |

Verdict by the rule fixed in the spec: logit. Power at this size: 100 % of hazard-simulated matrices lie above the 95th
percentile of the logit-simulated ones and the reverse, so 36 x 500 is enough to tell the links apart. The real T is lower
than all 200 logit simulations: the data lie on the other side of the logit link from the hazard link. Post hoc (not in the
spec): the mirrored hazard link, 1 - p = exp(-exp(a + b)), reaches -0.2807, 0.0017 below logit, where logit-simulated data
put it 0.0069 below [0.0081, 0.0057]. The best link is between logit and the mirror; the hazard link is the worst of the
three. Planted checks: a planted hazard matrix gives "hazard" and a planted logit matrix "logit" at 36 x 500 (also at the
real fitted abilities, 4 of 4); 4 arms x 100 problems gives "cannot tell" (power 0.18 to 0.38).

2. Hazard ratios (H2, refuted for RL). All rows: `results/hazard/math500-01/table.md`, `table.json`. Against the pooled base
+ cue samples (410.5 of 500), bootstrap over problems, 2,000 resamples:

| Method (MATH-500) | Right of 500 | Hazard ratio [95 %] | Logit shift | By difficulty: hardest, middle, easiest | Hardest minus easiest, log scale (range if constant) |
|---|---|---|---|---|---|
| RL plain, 4 samples pooled | 460.0 | 0.33 [0.28, 0.40] | +1.52 | 0.48, 0.23, 0.11 | -1.47 (-0.55 to +0.30): not constant |
| RL, cue | 457 | 0.37 [0.27, 0.48] | +1.39 | 0.48, 0.33, 0.11 | -1.47 (-0.85 to +0.59): not constant |
| Think-SFT, cue | 454 | 0.37 [0.27, 0.49] | +1.26 | 0.33, 0.32, 0.55 | +0.52 (-1.19 to +0.67): constant |
| base + 0.75 (RL - base), cue | 451 | 0.43 [0.32, 0.57] | +1.15 | 0.60, 0.38, 0.11 | -1.70 (-0.94 to +0.64): not constant |
| base + 0.5 (RL - base), cue | 452 | 0.43 [0.32, 0.55] | +1.18 | 0.59, 0.36, 0.17 | -1.27 (-0.79 to +0.51): not constant |
| Code-RL 3.1, cue | 450 | 0.44 [0.32, 0.57] | +1.11 | 0.51, 0.35, 0.39 | -0.27 (-0.92 to +0.47): constant |
| base + 0.25 (RL - base), cue | 441 | 0.56 [0.44, 0.73] | +0.80 | 0.79, 0.44, 0.39 | -0.71 (-0.76 to +0.43): constant |
| base + random difference, cue (control) | 417 | 0.85 [0.66, 1.09] | +0.15 | | |

| Vote (against the model's own single samples) | Base + cue: hazard ratio [95 %] | RL plain: hazard ratio [95 %] |
|---|---|---|
| vote over 2 (mean of 6 subsets) | 0.87 [0.80, 0.95] | 1.01 [0.92, 1.11] |
| vote over 3 (mean of 4 subsets) | 0.57 [0.50, 0.64] | 0.76 [0.65, 0.86] |
| vote over 4 | 0.51 [0.42, 0.61] | 0.60 [0.46, 0.74] |
| vote over 4 after restart | 0.45 [0.35, 0.55] | 0.57 [0.43, 0.71] |
| vote over 4, ties to the shortest | 0.42 [0.34, 0.51] | |

- Difficulty groups: problems sorted by b fitted on the 22 arms that are neither base samples nor a tested arm, cut so that
  each group holds a third of those arms' wrong cells (46, 119, 335 problems; pooled base right 15 %, 73 %, 95 %). "Range if
  constant" is the central 95 % of the same statistic on 100 matrices simulated from the fitted hazard model.
- Raw counts behind the RL row (wrong cells of base, then RL, 4 samples each): hardest 157 and 117 of 184, middle 130 and
  35 of 476, easiest 71 and 8 of 1,340. RL removes 89 % of the base's errors on the 335 easiest problems, 73 % on the middle
  119 and 25 % on the hardest 46. A constant hazard ratio of 0.33 would leave about 24 errors in the easiest group, not 8.
- Under the logit link the same statistic for RL plain is -0.93 (range if constant -0.72 to +0.50): also outside, by less.
  RL cue, theta 0.25, 0.5 and Code-RL are inside the logit range; theta 0.75 (-1.28) and Think-SFT (+1.35: 1.95 logits on the
  hardest group, 0.61 on the easiest) are outside. One sample per arm except RL plain; the hardest group has 46 problems.
- Theta (H2b, refuted): log hazard is no more linear in theta than the logit. Hazard ratio at theta 0.25, 0.5, 0.75, 1, 1.25,
  1.5: 0.56, 0.43, 0.43, 0.37, 0.45, 0.41. Theta 0.25 has 57 % of the log hazard ratio of theta 1 (logit: 57 %); theta 0.5 is
  off the line by 3.3 sd of the base noise floor (logit: 4.1).

3. Transfer to the 328 (H3, refuted; `results/hazard/transfer-01/readout.json`). The leave-one-arm-out procedure of the rate
section with the hazard link (ridge on the 328: 0.3). The same code with the logit link reproduces 5.07 and 5.99.

| Rule | Mean absolute error, problems of 328 (5 arms) |
|---|---|
| Hazard shift times c (the rule fixed in the spec; c 0.68 to 0.75) | 8.03 |
| Same hazard ratio, c = 1 (the law verbatim) | 5.11 |
| Point: same point gain | 5.14 |
| Logit shift times c (rate section) | 5.07 |
| Same hazard ratio on totals, no item model | 34.84 |

Three rules tie at 5.1 problems (rerun noise 4, binomial sd 5.7); the hazard form predicts the 328 no better than the
point rule. "Same hazard ratio" without an item model is 35 problems off.

4. Chain length and independence (H4a holds in rank, fails in size; H4b mixed).
- Fitted work against the length of right answers (b fitted without the model's own samples): Spearman 0.48 for base + cue
  (467 problems) and 0.59 for RL (482), shuffled range -0.09 to +0.09. But the slope of log fitted work on log tokens is 0.45
  [0.38, 0.53] for the base and 0.77 [0.67, 0.87] for RL, not 1: from the shortest to the longest third of problems the
  right answers grow 7.3 times (849 to 6,167 tokens, base) and the fitted work 2.4 times. The implied slips per 1,000 tokens
  fall with length: base 0.103, 0.049, 0.032; RL 0.018, 0.011, 0.011 (thirds by length). They bracket the located first
  wrong steps per 1,000 tokens of the checks section (base 0.038, RL 0.015). Tokens are not the unit of work.
- Independence of the 4 samples, p_i from the other 32 arms: the variance statistic D is 1.03 (base) and 0.90 (RL), inside
  the range of 200 matrices with independent cells (95th percentile 1.17 and 1.15): no over-dispersion in the bulk. The
  lower end is heavier than binomial: 33 problems with 0 of 4 right for the base against 25.1 expected (excess 7.9, 95th
  percentile of the simulations 7.0) and 18 against 6.1 for RL (excess 11.9, 95th percentile 5.0). The vote over 4 is 10.0
  (base, 446 against 456.0) and 9.3 (RL, 474 against 483.3) problems below what independent slips predict (5th percentile
  of the simulations -6.9 and -5.0). About 8 to 12 problems per model fail in every sample for a reason the common
  difficulty axis does not carry; the rest of the failures behave as independent draws.
- `examples.json`: problem 180 (p 0.75, base 3 of 4, the wrong sample is the short one, 276 tokens) and problem 210 (p 0.82
  from the other arms, base 0 of 4 with answers 3, 6, 6, 12 against gold 10, 4,468 to 12,087 tokens).

5. Predictions (`results/hazard/predict-01/`, commit `1da4655`, pushed 05:05 UTC, before the board and `gpu.py ls` were read
for finished cells). None of the blind cells had finished (hard328 vote jobs e8e6 and 5ff2 and the shots job 351b were
still running). Filed rule Hc; c = 1 and the logit prediction of `results/rate/predict-0*` beside it:

| Cell | Hazard Hc [80 %] | Hazard, c = 1 | Logit Lc | Point | Observed |
|---|---|---|---|---|---|
| hard328 base + cue, vote over 4 after restart | 184.2 [174, 195] | 193.8 | 192.3 | 187.9 | running |
| hard328 RL plain, vote over 4 after restart | 218.8 [207, 232] | 226.2 | 227.1 | 215.8 | running |
| hard328 base + cue + 3 RL-written solved problems | 174.7 [164, 185] | 180.9 | 181.4 | 179.8 | running |
| hard328 base + top 8 directions, cue | 171.3 [159, 183] | 176.4 | 173.1 | 172.8 | not found |
| MATH-500 Think-SFT cue, vote over 4 | 472.1 [464, 480] | | 473.1 | 489.5 | not run |
| hard328 base + cue, vote over 4, no restart (computed after the observation) | 179.5 [170, 189] | 187.4 | 188.5 | 185.3 | 179 |
| hard328 RL plain, vote over 4, no restart, 246 problems (computed after the observation) | 161.6 [152, 172] | 166.7 | 168.2 | 159.9 | 161 |

On the two cells whose observation was already known (`results/hazard/scored-01/readout.json`) Hc misses by 0.6 problems
on average, the point rule by 3.7, c = 1 by 7.1, logit Lc by 8.4. That is not a blind score, and on the 5-arm transfer the
same rule is the worst (8.03). To score the blind cells: add the observed counts to `OBSERVED` in `analysis/hazard.py` and
run `hazard score`.

Limits. One sample per arm except base + cue and RL plain. The difficulty groups come from 22 arms and the hardest holds
46 problems. The link test compares two fixed links; the post hoc mirror fit says the true link is not the logit either.
The vote and zero-of-4 statistics use p_i estimated from other arms; their nulls come from simulation, not from a second
set of samples.

Run: `uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.hazard fit|transfer|score`
(about 15 minutes for `fit`; `predict` refuses to overwrite the filed file); `... python -m studies.rlneurons.analysis.hazard_test`.
Run folders: `results/hazard/math500-01/` (`readout.json`, `table.json`, `table.md`, `examples.json`, `run.json`),
`transfer-01/`, `predict-01/`, `scored-01/`.

## Token frontier: right answers against generated tokens per problem, base + cue and RL (MATH-500, n = 500, laptop, board work-86ad1e, idea-aa7280)

Question (DIRECTION.md, mission 3): at equal generated tokens and with RL given the same procedure, which reward-free rule
gives the base the most right answers per token, and does any reach one RL sample? Answer: none does. The best base rule has
454 of 500 at 19,697 tokens (vote over 4 after restart, ties to the shortest), 1.2 points [-3.0, +0.6] below one RL sample
(460.0 of 500 at 4,687 tokens, the mean of the four RL samples) at 4.20 times its tokens. The cheapest base rule whose
interval includes 0 is the sequential vote with ties to the shortest: 452.0 at 11,256 tokens (stored order 451 at 11,369),
-1.6 points [-3.3, +0.2] at 2.40 times [2.25, 2.56] the tokens of one RL sample. RL under the same rule has 474.5 at 11,080
tokens: +4.5 points [2.6, 6.5]. RL stays ahead under every one of the 24 rules (smallest lead +4.2 [2.4, 6.0]).

`analysis/frontier.py` replays 24 rules, fixed in `specs/SPEC_frontier.md` before scoring, on the stored rows of Day-1 #3
(`results/day1_3/math500_*/rows.jsonl`; T 1.0 / top-p 1.0, cap 16,384, grader v3). A rule sees `n_new`, `cap_hit` and
`extracted_v3` of each attempt and nothing else (a rule that reads `score_v3` or `gold` raises `KeyError`). Tokens = every
generated token of every attempt the rule drew, cap hits and restarts included; a sample abandoned at L costs L. "Agree" is
`rln4_lib.agree`. Right = stored draw order (samples 0, 1, 2, 3); right (24) = mean over all 24 draw orders. Wilson 95 %
interval; paired bootstrap, 5,000 resamples, seed 0, on the 24-order means. The stopping rule itself is published
(Adaptive-Consistency, arXiv 2305.11860: up to 7.9 times fewer samples at under 0.1 % accuracy drop; Early-Stopping
Self-Consistency, arXiv 2401.10480: 33.8 % fewer samples on MATH; both from the abstracts only; short-m@k, arXiv 2505.17813).
New here: the frontier of a base against its own RL-trained version at equal tokens.

The deliverable table on MATH-500 (the 328 is not scored yet, see below). Every rule and every other arm: `results/frontier/math500-01/frontier.md`.

| Configuration | Model | Right | Percent [95 %] | Right (24) | Tokens per problem | Training signal |
|---|---|---|---|---|---|---|
| one sample | base + cue | 405 | 81.0 [77.3, 84.2] | 410.5 | 3,808 | none |
| one sample, restart after a cap hit | base + cue | 413 | 82.6 [79.0, 85.7] | 418.0 | 4,852 | none |
| one sample, abandoned at 8,000 tokens and drawn again (`R8000`) | base + cue | 428 | 85.6 [82.3, 88.4] | 424.0 | 6,116 | none |
| vote over 2, ties to the shortest | base + cue | 423 | 84.6 [81.2, 87.5] | 428.7 | 7,952 | none |
| sequential vote, at most 3 (`seq3`) | base + cue | 439 | 87.8 [84.6, 90.4] | 442.2 | 10,042 | none |
| sequential vote, at most 4 (`seq4`) | base + cue | 446 | 89.2 [86.2, 91.6] | 448.2 | 11,369 | none |
| sequential vote, at most 4, ties to the shortest (`seq4_short`) | base + cue | 451 | 90.2 [87.3, 92.5] | 452.0 | 11,369 | none |
| draw 2; if they differ draw 2 more; vote, ties to the shortest (`seq_2then4_short`) | base + cue | 452 | 90.4 [87.5, 92.7] | 452.7 | 12,086 | none |
| vote over 4 | base + cue | 446 | 89.2 [86.2, 91.6] | 448.2 | 16,034 | none |
| vote over 4, ties to the shortest | base + cue | 453 | 90.6 [87.7, 92.9] | 453.0 | 16,034 | none |
| vote over 4 after restart, ties to the shortest | base + cue | 454 | 90.8 [87.9, 93.0] | 454.0 | 19,697 | none |
| one sample | RL plain | 456 | 91.2 [88.4, 93.4] | 460.0 | 4,675 | RL reward |
| one sample, abandoned at 12,000 tokens and drawn again (`R12000`) | RL plain | 464 | 92.8 [90.2, 94.8] | 466.2 | 6,155 | RL reward |
| vote over 2, ties to the shortest | RL plain | 463 | 92.6 [90.0, 94.6] | 468.0 | 9,263 | RL reward |
| sequential vote, at most 4 (`seq4`) | RL plain | 474 | 94.8 [92.5, 96.4] | 474.3 | 11,098 | RL reward |
| sequential vote, at most 4, ties to the shortest (`seq4_short`) | RL plain | 475 | 95.0 [92.7, 96.6] | 474.5 | 11,098 | RL reward |
| sequential vote, at most 4, restart after a cap hit (`seq4_restart`) | RL plain | 475 | 95.0 [92.7, 96.6] | 476.1 | 11,803 | RL reward |
| vote over 4 | RL plain | 474 | 94.8 [92.5, 96.4] | 474.3 | 18,747 | RL reward |
| vote over 4 after restart | RL plain | 475 | 95.0 [92.7, 96.6] | 476.1 | 19,864 | RL reward |
| Olmo-3-7B-Think-SFT, cue, one sample (other arm, `results/rate/math500-01/table.json`) | Think-SFT | 454 | 90.8 | | 4,888 | SFT data |
| base + 0.5 (RL - base), cue, one sample (other arm) | weight blend | 452 | 90.4 | | 4,626 | RL reward |
| RL-Zero-Code 3.1, cue, one sample (other arm) | Code-RL | 450 | 90.0 | | 3,336 | RL reward (code) |
| base + 0.25 (RL - base), cue, one sample (other arm) | weight blend | 441 | 88.2 | | 4,036 | RL reward |

Base rule against one RL sample (460.0 at 4,687 tokens) and RL under the same rule, 24-order means:

| Base rule | Base right (24) | minus RL single, points [95 %] | Tokens, multiple of one RL sample [95 %] | RL, same rule | RL minus base, points [95 %] |
|---|---|---|---|---|---|
| `single` | 410.5 | -9.9 [-11.6, -8.3] | 0.86 [0.82, 0.89] | 460.0 | +9.9 [8.3, 11.6] |
| `restart` | 418.0 | -8.4 [-10.1, -6.8] | 1.05 [0.97, 1.14] | 463.0 | +9.0 [7.4, 10.7] |
| `R8000` | 424.0 | -7.2 [-9.0, -5.4] | 1.37 [1.25, 1.49] | 464.2 | +8.0 [6.3, 9.9] |
| `seq3` | 442.2 | -3.6 [-5.1, -2.0] | 2.13 [2.02, 2.24] | 470.4 | +5.7 [4.0, 7.4] |
| `seq4` | 448.2 | -2.4 [-4.0, -0.7] | 2.40 [2.25, 2.56] | 474.3 | +5.2 [3.4, 7.2] |
| `seq4_short` | 452.0 | -1.6 [-3.3, +0.2] | 2.40 [2.25, 2.56] | 474.5 | +4.5 [2.6, 6.5] |
| `vote4` | 448.2 | -2.4 [-4.0, -0.7] | 3.42 [3.28, 3.56] | 474.3 | +5.2 [3.4, 7.2] |
| `vote4_short` | 453.0 | -1.4 [-3.2, +0.4] | 3.42 [3.28, 3.56] | 475.0 | +4.4 [2.4, 6.4] |
| `vote4_restart_short` | 454.0 | -1.2 [-3.0, +0.6] | 4.20 [3.87, 4.56] | 475.0 | +4.2 [2.4, 6.0] |

Rule chosen per token budget, five folds (chosen on four, scored on the fifth; 24-order means), and the rule chosen on all
500, which is the one to score on the 328 (`chosen.json`):

| Budget, tokens per problem | Base: chosen on all | Base held-out right, tokens | RL: chosen on all | RL held-out right, tokens |
|---|---|---|---|---|
| 5,000 | `restart` | 416.5, 4,589 | `restart` | 462.8, 4,909 |
| 7,500 | `R8000` | 422.0, 6,110 | `R12000` | 466.2, 6,225 |
| 10,000 | `seq3` | 438.0, 9,382 | `vote2_short` | 468.0, 9,374 |
| 12,500 | `seq_2then4_short` | 452.0, 11,774 | `seq4_restart` | 474.3, 11,625 |
| 15,000 | `seq4_restart_short` | 450.3, 13,804 | `seq4_restart` | 474.3, 11,625 |
| 17,500 | `seq4_restart_short` | 450.5, 14,597 | `seq4_restart` | 474.3, 11,625 |
| 20,000 | `vote4_restart_short` | 450.0, 16,878 | `seq4_restart` | 474.3, 11,625 |

- The sequential vote has the fixed vote's score at 29 % fewer tokens on the base (448.2 at 11,256 against 448.2 at 16,034,
  24-order means) and 41 % fewer on RL (474.3 at 11,080 against 18,747). It stops after 2 samples on 373 of 500 base problems
  (368 right), after 3 on 65 (57 right), and uses all 4 on 62 (21 right); RL: 444 (441 right), 34 (27), 22 (6). Mean samples
  drawn: 2.38 base, 2.16 RL. Above 12,500 tokens neither model gains on held-out folds: the frontier is flat from there.
- The base needs 2.4 times the tokens of one RL sample to come within 1.6 points of it, not 3.4 times (the fixed vote of
  Day-1 #3). It does not reach it: no base rule has a point estimate at or above one RL sample at any multiple up to 4.2.
  With the plain tie rule the sequential vote is 2.4 points [-4.0, -0.7] below one RL sample.
- Caveat on `short`: the tie rule was written after reading the problems it fixes ("Label-free selector"), so the 451 to 454
  rows are optimistic; the plain-tie rows (446 to 450) are the safe reading until the 328 is scored.
- Order luck is small: the 24-order mean moves the base's `seq4` from 446 to 448.2 and `seq4_short` from 451 to 452.0.
  `R8000` is the exception: 428 in stored order, 424.0 over the orders.
- Length caps do not help the sequential vote: `seq4_L12000` 450.0 at 11,002 tokens (base), 472.8 (RL, below its 474.3);
  `seq4_L8000` 444.6 and 467.0. The emulation ran out of stored samples (the fourth exceeded L and ran in full) on 36 and 76
  base problems for L 12,000 and 8,000 (RL 26 and 67), and on 13 and 37 for `R12000` and `R8000` (RL 12 and 50): on those
  problems a real run would draw a fifth sample, so these rows are approximate. Accepting a short finished answer at once
  (`seq4_stop1000`, `seq4_stop2000`) loses 6 to 9 base problems for 3 to 8 % of the tokens.
- Weight edits against test-time compute: Think-SFT with the cue (454 at 4,888 tokens, no reward) and the half-way weight
  blend (452 at 4,626) reach in one sample what the base's votes reach at 11,300 to 19,700 tokens.
- Hypotheses of the spec. H1 (sequential keeps the vote's score at 25 % fewer tokens): not refuted, 0.0 points at 29 %.
  H2 (no base rule reaches one RL sample at 2.0 times its tokens or less): not refuted. H3 (RL ahead under every rule, interval
  above 0): not refuted. H4 (order moves the base's `seq4` by under 3 problems): not refuted, 2.2.
- Reconciliation of two earlier counts on these rows. "447 at 12,614" is reproduced exactly by: draw 2; if they do not agree
  draw both remaining samples; plurality over 4, ties to the lowest sample; agreement = the two extracted strings are equal
  (no normalisation). "452 at 11,314" (RL 476 at 11,206) is not reproduced to the token; its description (draw 2, stop when two
  agree, else one more at a time up to 4, plurality) with `rln4_lib.agree` gives 446 at 11,369 with ties to the lowest sample
  and 451 at 11,369 with ties to the shortest (RL 474 and 475 at 11,098); with a string comparison after stripping `$`,
  spaces, `\left`, `\right` it gives 451 at 11,597 (RL 476 at 11,235). So the two counts differ in three things: one more
  sample at a time against two more at once (about 700 tokens), grader equivalence against string equality as agreement
  (about 450 tokens, 1 problem), and ties to the shortest against the lowest sample (5 problems). The parallel rule of
  `specs/DAY1_hard328_vote_2026-11-14.md` amendment 1 (`par4_m2`) reproduces at 447 at 13,403 (RL 473 at 16,553).
- Examples (`examples.json`, with every sample's seed, extracted answer, score and last 2,000 characters): base problem 0
  stops after 2 samples and is right (1,195 tokens against 3,177 for the vote); base problem 20 stops after 2 and is wrong:
  samples 0 and 1 agree on `117 + 41i`, samples 2 and 3 have the gold `6 + 9i`. RL problem 369: all four samples say 189, gold 21.
- The 328: not scored. The four-sample rows with restarts are jobs `abaybektursun-1114-200457-e8e6` (base) and
  `-200505-5ff2` (RL) of board work-1a972a, still running at 100 minutes when this was written; no hard328 `rows.jsonl` is in
  git. When `analysis/day1_vote.py` has written their run folders, this one command scores `single` and the 9 chosen rules
  once (it refuses a `chosen.json` made on the same set):

```
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.frontier --base studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01 --rl studies/rlneurons/results/day1_3/hard328_rl_plain_s4r2-01 --fixed studies/rlneurons/results/frontier/math500-01/chosen.json --out studies/rlneurons/results/frontier/hard328-01
```

Run folder `results/frontier/math500-01/`: `run.json` (commit, command, source jobs), `readout.json` (every rule and model:
right, interval, tokens in both orders, samples drawn, ran-out counts, both comparisons, the fold choices), `per_problem.json`
(score, tokens and samples drawn per problem and rule), `frontier.md` and `frontier.json` (the full table), `chosen.json`,
`examples.json`. Test (planted rows; a rule that reads the score must raise; four identical answers cost 2 samples, four
different cost 4; two agreeing wrong answers must score 0) and the run:

```
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.frontier_test
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.frontier --base studies/rlneurons/results/day1_3/math500_base_cue-01 --rl studies/rlneurons/results/day1_3/math500_rl-01 --out studies/rlneurons/results/frontier/math500-01 --base-run runs/abaybektursun-1114-153825-208b --rl-run runs/abaybektursun-1114-183640-e828
```

## Difficulty profiles: do supervised fine-tuning and RL help on different problems? (MATH-500 n = 500, laptop, board work-d13a7f, idea-095c0d)

Question: RL removes most of the cued base's errors on easy problems and few on hard ones (hazard section). Does Think-SFT
(imitation of reasoning traces, no reward; cue, one sample, 454 of 500) do the opposite, which would make it the
complementary partner of RL? Answer: yes for the profile, with one caveat that is not controlled; no for a gain from
pairing the two on MATH-500. The prediction filed blind from the MATH-500 profile held on the 328 harder problems:
Think-SFT cue scored 219 of 328 (profile rule 217.6; the one-axis rules 190.5 to 201.1; RL 205 and 206) and plain 203
(one-axis 181.4 to 186.2). Not controlled: overlap of the 328 with Think-SFT's training traces (the owner's check is
running, result-d9d6f3). On MATH-500 the profile contrast of Think-SFT against the four RL samples is C = -1.54 by MATH
level (one-axis range -0.89 to +0.83, largest same-arm value 0.61; -1.45 and -1.52 under the two other difficulty
definitions). It comes mostly from the easy side: on levels 1-2 Think-SFT has 10 wrong against RL's 2.0 per sample and the
base's 8.5 (z 3.7); on level 5 it has 23 against RL's 25.5 (samples 21 to 30; z -1.5, inside noise). The union of
Think-SFT with one RL sample is 2.8 problems above the union of two RL samples; 4 problems are solved by Think-SFT and by
none of the 4 RL samples. Spec, hypotheses and literature: `specs/SPEC_profile.md`. Code: `analysis/profile.py` (imports the fits of
`axis.py`, `rate.py`, `hazard.py`); planted checks: `analysis/profile_test.py`. Run folder `results/profile/math500-01/`
(`readout.json`, `table.md`, `examples.json`, `run.json`).

Literature (subagent; WebSearch and WebFetch because `tools/exa.py` has no key and the Exa MCP returned 401): ReLIFT (arXiv
2506.07527, Section 2.1, Fig. 1a; Qwen2.5-Math-7B, SFT on DeepSeek-R1 traces against RL, 1,000 questions binned by the base's
accuracy over 8 samples) states "RL outperforms SFT on Easy and Medium questions" and "SFT achieves better results than RL on
the Hardest questions", as a figure without per-bin numbers or a noise floor. No per-level table for this contrast, no 2PL
fit by training method and nothing on the Olmo 3 pair was found.

Difficulty is defined without the arms compared (a problem an arm fails looks hard if that arm helps define "hard"):
D-level = MATH level, which uses no model output (`data/profile/math500_meta_v1.json`, from the Hugging Face dataset
`HuggingFaceH4/MATH-500`); D-rest = `hazard.groups` on the 19 single-sample arms that are not base samples, RL 3.1, Think-SFT
or a row of the table (mostly RL-weight arms: hard for RL-like models); D-base = right count among two base samples, the
random-difference control and the base-written-examples cell, with the other two base samples as the reference, both halves
(hard for the base). Reference: the 4 base + cue samples. Error reduction = 1 - wrong(arm) / wrong(reference), bootstrap over
problems, 2,000 resamples, 95 %; wrong cells per sample in brackets. D-level (D-rest and D-base in `table.md`):

| Arm | Level 5 (134 problems) | Level 4 (128) | Level 3 (105) | Level 1-2 (133) |
|---|---|---|---|---|
| base + cue (reference), wrong | 47.5 | 20 | 13.5 | 8.5 |
| RL plain, 4 samples pooled | 46 % [36, 57] (25.5) | 54 % [38, 70] (9.25) | 76 % [60, 90] (3.25) | 76 % [56, 96] (2) |
| RL plain, the 4 samples one by one | 37 to 56 % (21 to 30) | 50 to 60 % (8 to 10) | 63 to 85 % (2 to 5) | 65 to 88 % (1 to 3) |
| RL, cue | 43 % [26, 59] (27) | 65 % [44, 85] (7) | 63 % [35, 91] (5) | 53 % [11, 89] (4) |
| Think-SFT, cue | 52 % [36, 66] (23) | 75 % [53, 94] (5) | 41 % [-2, 75] (8) | -18 % [-93, 43] (10) |
| Think-SFT, plain | 35 % [14, 53] (31) | 55 % [29, 78] (9) | 26 % [-33, 67] (10) | -18 % [-112, 47] (10) |
| Code-RL 3.1, cue | 41 % [26, 57] (28) | 40 % [7, 67] (12) | 56 % [22, 84] (6) | 53 % [10, 88] (4) |
| base + 0.25 (RL - base), cue | 24 % [7, 41] (36) | 50 % [22, 74] (10) | 48 % [13, 80] (7) | 29 % [-28, 76] (6) |
| base + 0.5 (RL - base), cue | 41 % [25, 57] (28) | 50 % [26, 73] (10) | 63 % [37, 90] (5) | 41 % [-4, 81] (5) |
| base + 0.75 (RL - base), cue | 43 % [29, 58] (27) | 40 % [14, 65] (12) | 41 % [-6, 74] (8) | 76 % [43, 100] (2) |
| base + top 8 RL directions, plain | 35 % [16, 53] (31) | 30 % [-6, 60] (14) | -4 % [-70, 43] (14) | -65 % [-180, 12] (14) |
| RL-Zero-Math 3.0, cue | 37 % [19, 54] (30) | 55 % [32, 80] (9) | 33 % [-8, 69] (9) | 53 % [9, 89] (4) |

By MATH level RL's profile is flatter than in the hazard section (46 % on level 5, 76 % on levels 1-2, against 25 % and
89 % on the model-defined groups): part of the hazard section's slope comes from defining "hard" with RL-weight arms.
On D-rest RL plain has 26 %, 78 %, 87 % (hardest 48, middle 120, easiest 332 problems) and Think-SFT cue 40 %, 61 %, 47 %.

1. Earlier readings (`readout.json` `earlier_readings`). All three are the same data. The planner's count is reproduced with
a ranking that leaves the compared arms out: hardest 50 problems base 42.75, RL 31.25, Think-SFT 26; easiest 200: 7.25,
0.5, 8 (with all 36 arms in the ranking: 43.5, 32, 28 and 4, 0, 6). The hazard section's 0.33, 0.32, 0.55 are hazard
ratios, where smaller is better: they also say Think-SFT helps most on the hardest group. "Roughly flat" is right on the
error-ratio scale (Think-SFT removes 40 %, 61 %, 47 % of the errors in the three D-rest groups, RL 26 %, 78 %, 87 %) and the
hazard link's null is wide (-1.19 to +0.67), so it printed "constant"; on the logit scale the same counts are 1.95 against
0.61 and outside the null. Dated note, 2026-11-15, on the hazard section's Think-SFT row: "constant" there means "inside
the hazard-link null", not "the same profile as RL"; against RL the profile differs (this section). The planner's reading
"helps more than RL on hard problems" overstates: see 2.

2. H1 (Think-SFT's gain is concentrated in hard problems, RL's in easy ones): not refuted as a contrast, and it comes from
the easy side. C = log(wrong Think-SFT / wrong RL) in the hardest bin minus the same in the easiest bin; negative =
Think-SFT relatively better on hard problems (`H1_profile_contrast`):

| Difficulty | C [95 % bootstrap] | One-axis range (200 Rasch simulations), z | Same arm, one sample against its other three | Think-SFT minus RL wrong, hardest bin (one-axis range), z | Easiest bin, z |
|---|---|---|---|---|---|
| D-level | -1.54 [-2.74, -0.69] | -0.89 to +0.83, -3.3 | RL -0.45 to +0.61, base -0.26 to +0.48 | -2.5 (-3.5 to +11.3), -1.5 | +8.0 (-2.8 to +4.5), +3.7 |
| D-rest | -1.45 [-2.28, -0.47] | -0.78 to +0.80, -3.3 | RL -0.77 to +0.87, base -0.12 to +0.10 | -6.0 (-4.0 to +9.0), -2.7 | +6.75 (-3.5 to +6.0), +2.1 |
| D-base | -1.52 [-2.29, -0.68] | -0.67 to +0.76, -3.7 | not computed (the bins use base samples) | -5.0 (-3.3 to +8.3), -2.5 | +7.75 (-3.8 to +7.0), +2.4 |

On the two model-defined splits Think-SFT has 5 to 6 fewer errors than RL in the hardest group (below every RL sample: 25
against 28 to 34); by MATH level the difference is 2.5 on level 5 (inside noise) and 4.25 on level 4 (z -2.2). Both
model-defined splits share weights with RL (the RL change is 0.24 % of the weight norm, Think-SFT's 24.8 %), so "hard for
the base" is also "hard for RL" by family; MATH level is the only split free of that. This contrast was tested because
three readings had noticed it among about 30 arms, so its size is selected upward.

3. What the stored rows show (`cap_hits_by_level`, `examples.json`). The raw text of the Think-SFT cells is in the Modal
Volume of workspace sameraslan (jobs `sameraslan-1114-185940-514f`, `-185947-4681`) and could not be read; asked on
`@sameraslan`, no answer when this was written. From `per_problem.json` (score, cap hit, tokens). Wrong cells per sample =
cap hits (16,384 tokens, no answer) + finished wrong:

| Arm | Level 5 | Level 4 | Level 3 | Level 1-2 |
|---|---|---|---|---|
| base + cue, 4 samples | 47.5 = 16.75 + 30.75 | 20 = 3.25 + 16.75 | 13.5 = 2 + 11.5 | 8.5 = 0.25 + 8.25 |
| RL plain, 4 samples | 25.5 = 5.75 + 19.75 | 9.25 = 1 + 8.25 | 3.25 = 0.25 + 3 | 2 = 0.25 + 1.75 |
| Think-SFT, cue | 23 = 15 + 8 | 5 = 1 + 4 | 8 = 4 + 4 | 10 = 4 + 6 |
| Think-SFT, plain | 31 = 14 + 17 | 9 = 2 + 7 | 10 = 2 + 8 | 10 = 1 + 9 |
| base + top 8 RL directions, plain | 31 = 5 + 26 | 14 = 1 + 13 | 14 = 3 + 11 | 14 = 0 + 14 |

- 24 of Think-SFT cue's 46 errors are cap hits (base 25 % of its errors, RL 18 %). On level 5 it finishes with a wrong
  answer 8 times against RL's 19.75: where it cannot solve a problem it mostly runs to the cap instead of committing.
- On levels 1 to 3 it has 8 cap hits where the base has 2.25 and RL 0.5 per sample: half of its excess over RL there is
  non-termination, the other half finished wrong answers (10 against RL's 4.75). Whether those 10 are wrong mathematics or
  answer-format failures cannot be told without the text. The refutation clause of the spec (cap-hit share of the easy
  errors above twice that of the others) is not met: 4 of 10 on levels 1-2 against 20 of 36.
- 14 errors on easy problems (level 1-2 or the easiest D-rest group): all 4 RL samples are right on 12 of them, the base
  on 7 (e.g. problem 182, `test/prealgebra/1922.json`, gold 1251, Think-SFT wrong after 924 tokens; problem 387,
  `test/algebra/849.json`, gold 18, cap hit).
- 4 problems are solved by Think-SFT cue and by none of the 4 RL samples (168 and 286, level 5; 460 and 352, level 4; the RL
  answers to each are four different wrong values; RL with cue solves 352). 17 are solved by all 4 RL samples and missed
  by Think-SFT cue.
- Where they differ (`where_they_differ`): Think-SFT right and RL right at most once in 4: 6 problems, all level 4 or 5,
  5 subjects. Think-SFT wrong and RL right at least 3 times in 4: 22 problems, levels 1 to 5 (4, 4, 6, 2, 6), 7 subjects.
  No subject stands out.

4. H2 (2PL against Rasch, held out): holds. Logit p = a_j + (1 + g_j) b_i, ridge 30 on g, the folds of `axis.heldout`:
-0.27515 against -0.27900 nats per cell, gain 0.00386 (17,991 cells; 0.00384 with twice the steps); 20 Rasch-simulated
matrices give -0.00026 on average, maximum -0.00007. The free bilinear term of `axis.py` did not find this (500 extra
problem parameters, shrunk to zero); 36 arm parameters do. g by family: RL 3.1 (4 plain samples, cue) 0.36, base + cue
(4 samples) 0.33, Think-SFT (cue, plain) -0.15; RL minus Think-SFT 0.50 (Rasch simulations -0.16 to +0.10). The nine
lowest g: Think-SFT plain -0.26, Code-RL plain -0.17, random rank-8 plain -0.15, Mix 3.0 plain -0.14, top-8 plain -0.13,
General 3.0 plain -0.07, Think-SFT cue -0.03, theta 0.25 plain 0.02, IF 3.0 cue 0.11; the other 27 arms lie between 0.20
and 0.46. So the second parameter does not separate SFT from RL: the cued base and RL have the same discrimination, and
low discrimination marks arms that fail easy problems at a rate unrelated to difficulty (seven plain-prompt arms and
Think-SFT under either prompt). Dated note, 2026-11-15, on the axis section: its statement that the prompt format is no
second axis holds for the pair test; under 2PL seven of the nine lowest-discrimination arms are plain-prompt arms.
Planted checks (`profile_test.py`, all pass): a Rasch matrix gives gain -0.00035 and C inside the range on all three
splits; a planted 2PL with g of sd 0.3 is detected (gain 0.0024, correlation of fitted and planted g 0.83); an arm of RL's
ability that also fails 5 % of all problems whatever their difficulty gives C -0.71 to -0.89, outside on all three.

5. H3 (the pair is complementary beyond noise): refuted by the rule of the spec. Unions of Think-SFT cue with one RL sample:
476, 481, 479, 478; of two RL samples: 472 to 479 (mean 475.7): +2.8 problems, below the 5 named in the spec. Three RL
samples plus Think-SFT: 484.75 on average against 482 for the four RL samples. Power (`H3_power`): the profile planted as
Think-SFT's three logit shifts (2.07, 1.18, 0.67 by D-rest group) gives a mean C of -0.38 by level and -0.80 by D-rest, a
quarter to a half of the observed -1.5 (a logit shift cannot produce an arm that removes none of the easy errors); it is
detected in 19 % (level) and 37 % (D-rest) of 200 simulations with one sample, 33 % and 75 % with four, 42 % and 76 % with
eight. Samples: one sample decides the contrast and the easy side (z -3.3 and +3.7); the level-5 difference of 2.5
problems would need 3 Think-SFT samples to reach z 1.96 if it is real. No GPU job was run for this (step 6 of the plan
skipped): the hard328 cells of work-9ecc56 test the hard side directly.

6. Predictions for Think-SFT on hard328 (work-9ecc56), filed before its numbers were opened (`results/profile/predict-01/`,
commit `fc4f971`, pushed 05:47 UTC; the item was read by its title only). Profile rule = the arm's logit shift per D-rest
group, applied to each hard328 problem by its reference probability. On the 5 arms measured on both sets the profile rule
is the worst (mean absolute error 8.4 problems, 4.9 to 16.7 too high on every arm; Lc 5.1, P 5.1), so a version with that
mean error subtracted was filed beside it.

| Cell (of 328) | Lc [80 %] | L1 | P | Profile [80 %] | Profile, corrected | Author's guess | Observed |
|---|---|---|---|---|---|---|---|
| Think-SFT cue, one sample | 196.3 [186, 206] | 201.1 | 190.5 | 217.6 [204, 231] | 209.2 | 200 | 219 |
| Think-SFT plain, one sample | 183.2 [172, 194] | 186.2 | 181.4 | 218.3 [204, 234] | 209.9 | 195 | 203 |

One axis (Lc, P) puts Think-SFT cue at 190 to 196, below RL's 205; a hard-problem-weighted arm should reach RL or pass
it (209 to 218). Observed (board result-d9d6f3, posted 05:48:33 UTC, 92 s after the push; jobs
`sameraslan-1114-204845-1055`, `-204852-d527`; its run folders were not committed when this was scored, so the two counts
are read from the board, not from an artifact): cue 219, plain 203. Mean absolute error over the two cells
(`results/profile/scored-01/readout.json`): profile 8.35, profile corrected 8.35, author's guess 13.5, L1 17.35, Lc 21.25,
P 25.05. Both cells are above Lc's 80 % interval; cue is inside the profile interval, plain is 1 below it and inside the
corrected one. The cue cell passes RL (205, 206) by 13 to 14 problems; the plain cell does not (203), and the profile rule
is 15 too high on it. Think-SFT cue has 89 cap hits on the 328 (RL 20) and 10,123 tokens per problem, so most of its 109
errors there are answers that did not finish.

Verdict. Second axis: yes. A second parameter exists (2PL), Think-SFT's profile differs from RL's on MATH-500 (C outside
both noise floors on all three splits), and the profile predicted the 328 where the one-axis rules missed by 17 to 29
problems. Two parts have different support. "RL adds reliability on easy problems that Think-SFT lacks": 18 wrong on
levels 1 to 3 against RL's 5.25, 8 of them cap hits. "Think-SFT solves hard problems RL does not": on MATH-500 28 wrong on
levels 4 and 5 against 34.75 (RL samples 31 to 40), 4 problems no RL sample solves, oracle union +2.8; on the 328 the cue
cell is 13 above RL in one sample, with the training-set overlap unchecked. Until that check is in, "SFT adds knowledge"
may be "SFT has seen these problems". The stack to run, for the lead to decide (not submitted):
Think-SFT + 1.0 (RL-Math - base) with cue, one sample, on MATH-500 and on hard328. `jobs/wsp_edit.py` (branch
`claude/weight-space-programming-research-ddd44e`) builds base + alpha (other - base) only, so it needs an option that adds
the RL-Math difference onto the Think-SFT weights (about 10 lines), then `run_cell --model-path /tmp/theta --model-label
sft1_rl --prompt cue --set math500|hard328 --temperature 1.0 --top-p 1.0 --seed <new>` on h100: about 30 H100 minutes for
MATH-500 (the Think-SFT cells started 03:01 and were posted 03:36 UTC) and about 1 H100 hour for the 328 (the RL cell took
51 minutes), about 6 USD together. If the two changes add, on MATH-500 the stack has RL's errors on levels 1 to 3 (5.25)
and Think-SFT's on levels 4 and 5 (28): 467 of 500, against RL 456 to 464 and Think-SFT 454; 460 or less refutes it. On
the 328 it should keep Think-SFT's 219; below 206 means the RL change removes the hard-problem lead. The RL change was
learned on the base and its cosine with the Think-SFT change is -0.00001 (WSP-1), so it may not act on Think-SFT at all.
The cheaper no-reward test of the same weakness needs no new code: Think-SFT cue with `--samples 4 --restarts 2` (the job
of the axis section plus restarts), since 24 of its 46 errors on MATH-500 and up to 89 of its 109 on the 328 are cap
hits; it also gives the 3 further samples.

Limits. One Think-SFT sample per prompt and per set. The hard328 counts are from a board post; overlap of the 328 with Think-SFT's training data is unchecked. No raw text of Think-SFT was read. MATH level is coarse (4 bins); the two
model-defined splits are not family-free. The contrast was chosen after it had been noticed. The profile rule failed its
own check on the 5 known arms.

Run: `uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.profile fit --runs runs`
(about 1 minute; `--runs` is the folder of `tools/gpu.py get` copies, used for the RL-cue answers in `examples.json`),
`... profile score`, `... python -m studies.rlneurons.analysis.profile_test`; `predict` refuses to overwrite the filed file.

## Prefix hand-off: where inside an answer RL's advantage enters (MATH-500 pool of 183, T 1.0 / top-p 1.0, grader v3, board work-b68a26, idea-17d5b7)

RL's advantage is in the first half of the answer, and most of it is written into the text by the halfway point. A stored
answer (sample 0, attempt 0 of the Day-1 #3 jobs) is cut after 25, 50 or 75 % of its token ids and a finisher model writes the
rest: writer {base + cue, RL} x finisher {base, RL} x cut, one sample each, on the 183 problems where the base is right in at
most 3 of its 4 stored samples (the same list as `results/anatomy/math500-01/pool_k_le3.json`). Request = plain prompt ids +
prefix ids; the 16,384 cap counts the prefix. Spec `specs/SPEC_handoff.md` (hypotheses written before the run); readout
`results/handoff/readout-01/readout.json` and `readout.txt` (`analysis/handoff.py`; Wilson 95 % in percent, paired bootstrap
5,000 resamples, seed 0, in points).

Whole pool, right of 183 (cap hits), generated tokens per problem / total with the prefix:

| cut | base finishes base | base finishes RL | RL finishes base | RL finishes RL |
|---|---|---|---|---|
| 25 % | 107 (27), 5,914 / 7,624 | 122 (39), 6,552 / 8,414 | 131 (4), 5,420 / 7,130 | 139 (10), 5,754 / 7,616 |
| 50 % | 106 (22), 4,037 / 7,457 | 135 (36), 4,753 / 8,478 | 122 (5), 3,516 / 6,936 | 142 (12), 3,981 / 7,706 |
| 75 % | 100 (27), 2,515 / 7,645 | 132 (32), 2,766 / 8,353 | 108 (3), 2,108 / 7,238 | 139 (9), 2,091 / 7,678 |

Stored sample 0 on the pool: base 88, RL 140. Of the 17.5 to 21.3 points between the two own-prefix columns, the base
finishing an RL prefix recovers 8.2 [0.5, 16.4] at 25 %, 15.8 [8.7, 23.0] at 50 % and 17.5 [9.3, 25.1] at 75 % (47 %, 81 % and
82 % of the gap, counted in problems: 15 of 32, 29 of 36 and 32 of 39; biased pool, see the next paragraph). RL finishing a base prefix loses 4.4 [-2.2, 10.4], 10.9 [3.8, 18.0] and 16.9 [10.4, 23.5] against its own.

Correction (audit on board result-a6ab7a): the pool of 183 overstates the recovery. The pool was picked with base sample 0,
which also supplies the base prefixes, so 28 problems are in it only because sample 0 was wrong; that lowers the base's
own-prefix column and widens the gap. On the unbiased subset U (n = 155, in the pool whatever sample 0 did; `unbiased` in
`data/handoff/plan_v1.json`) the base finishing an RL prefix recovers 42 %, 65 % and 71 % of the gap at 25, 50 and 75 %: 5.2
[-2.6, 12.9] of 12.3 [4.5, 20.0] points, 8.4 [1.3, 15.5] of 12.9 [5.8, 20.6] and 9.7 [1.3, 18.1] of 13.5 [5.8, 21.3]. Right
of 155 at 25 / 50 / 75 %: base finishes base 92 / 94 / 90, base finishes RL 100 / 107 / 105, RL finishes base 108 / 104 / 91,
RL finishes RL 111 / 114 / 111; RL finishing a base prefix loses 1.9 [-5.2, 9.0], 6.5 [-0.6, 14.2] and 12.9 [5.8, 20.0]. The
recovery at 25 % no longer excludes 0. The 47 / 80 / 82 % above and in H2 below are the biased pool; use the U numbers.
Artifact `results/handoff/unbiased-01/readout.json`, recomputed from the committed `rows.jsonl` of `base-01/` and `rl-01/` by
`analysis/handoff_unbiased.py` (paired bootstrap as above):
`uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.handoff_unbiased --nn <nn>`.

By the writer sample's own outcome, right of n [Wilson 95 %]; "fresh" = the finisher model's stored samples 1 to 3 on the same
problems, in percent:

| prefix | cut | base finisher | RL finisher | RL minus base finisher | fresh base / RL |
|---|---|---|---|---|---|
| base, wrong (n = 70) | 25 % | 25 [26, 47] | 37 [41, 64] | +17.1 [4.3, 30.0] | 53 / 74 |
| | 50 % | 20 [19, 40] | 32 [35, 57] | +17.1 [5.7, 28.6] | |
| | 75 % | 17 [16, 35] | 21 [21, 42] | +5.7 [-2.9, 14.3] | |
| base, right (n = 88) | 25 % | 74 [75, 90] | 84 [89, 98] | +11.4 [3.4, 19.3] | 58 / 92 |
| | 50 % | 83 [87, 98] | 83 [87, 98] | 0.0 [-6.8, 5.7] | |
| | 75 % | 81 [84, 96] | 82 [86, 97] | +1.1 [-4.5, 6.8] | |
| base, cap hit (n = 25) | 25 % | 8 | 10 | +8.0 [-16.0, 32.0] | 29 / 53 |
| | 50 % | 3 | 7 | +16.0 [0.0, 36.0] | |
| | 75 % | 2 | 5 | +12.0 [0.0, 28.0] | |
| RL, right (n = 140) | 25 % | 110 [71, 85] | 131 [88, 97] | +15.0 [8.6, 21.4] | 63 / 93 |
| | 50 % | 131 [88, 97] | 134 [91, 98] | +2.1 [-2.1, 6.4] | |
| | 75 % | 131 [88, 97] | 136 [93, 99] | +3.6 [0.7, 7.1] | |
| RL, wrong (n = 37) | 25 % | 9 [13, 40] | 8 [11, 37] | -2.7 [-21.6, 16.2] | 19 / 40 |
| | 50 % | 4 [4, 25] | 8 [11, 37] | +10.8 [2.7, 21.6] | |
| | 75 % | 1 [0, 14] | 3 [3, 21] | +5.4 [0.0, 13.5] | |
| RL, cap hit (n = 6) | 25 / 50 / 75 % | 3 / 0 / 0 | 0 / 0 / 0 | | 6 / 33 |

Without the prefixes that already contain the right answer (base 0 / 0 / 6 of 88, RL 0 / 9 / 52 of 140 at 25 / 50 / 75 %): RL
right prefixes at 75 % give base 79 of 88, RL 84 of 88, +5.7 [1.1, 11.4]; the other differences move by at most 0.2 points.

- H0 (instrument), holds: a model finishing its own prefix scores what its stored sample scored. Base on the 155 pool
  problems that are in the pool whatever sample 0 did: 92, 94, 90 against 88 stored (+2.6 [-4.5, 9.7], +3.9 [-1.3, 9.0], +1.3
  [-3.9, 6.5]); RL on the pool: 139, 142, 139 against 140 (intervals include 0). Smoke (`abaybektursun-1114-222829-ce39`, RL
  finisher, 10 problems, cuts 0 to 100): a cut at 100 % gives 0 new tokens and the writer's score in 20 of 20; a cut at 0 is the
  plain prompt (ids equal `prompt_ids.json`, laptop test).
- H1 (RL's advantage is late checking or finishing), refuted: on wrong base prefixes cut at 75 % the RL finisher has 21 of 70
  and the base 17 (+5.7 [-2.9, 14.3]). The RL finisher's advantage is at 25 % and 50 % (+17.1 both) and on right prefixes only
  at 25 % (+11.4 base prefixes, +15.0 RL prefixes); from 50 % on, a right prefix is finished equally by both (83 and 83 of 88).
- H2 (the plan chosen in the first quarter), refuted by its own rule, narrowly: the base on an RL prefix cut at 25 % recovers
  8.2 of 17.5 points (47 %, the rule asked for half); at 50 % it recovers 81 %, 29 of 36 problems (biased pool; on U 42 % and 65 %). The advantage enters between the start and the
  halfway point, not in the first quarter alone.
- H3 (wrong base prefixes are poisoned), refuted as stated (RL finisher 32 of 70 at 50 %, lower bound 35 %, above 15 %), but
  the prefix does carry the error: against fresh rates of 53 % (base) and 74 % (RL), a wrong base prefix leaves the base 36,
  29, 24 % and RL 53, 46, 30 % at 25, 50, 75 %. 5 of the 70 wrong base answers have no extracted answer (a format failure);
  both finishers fix 3 to 5 of those 5 at every cut.
- H4 (the base loses at most 5 points on right RL prefixes), refuted at 25 % (+15.0 [8.6, 21.4]), holds at 50 % and 75 %.
- Raw rows, read by hand. Every continuation resumes mid-sentence. The base's failures on RL prefixes are cap hits: 36, 34
  and 32 of its 61, 48 and 51 wrong answers at the three cuts (RL on its own prefixes: 8, 10, 9); it keeps reworking a long
  RL derivation and does not close it (problem 295 at 50 %: both finishers hit the cap from the same prefix). Recovery:
  problem 63, base answer cut at 75 % after "the sum is 0 + 2 + 5 + 1 = 8. Let me verify once again"; the base re-adds the same
  four terms and boxes 8; RL goes back to the factorization, finds the fifth factor and boxes 10. Of the 12 right base
  prefixes the base itself spoils at 50 and 75 %, 7 end in a final line v3 cannot read or grade (`East.`, `Navin**.`, `16/27.`,
  no answer line), 2 hit the cap and 3 change the answer. Problem 20: the base's wrong
  prefix reads `(1+2i)6` as a sixth power; both finishers keep 117 + 41i at all three cuts.
- Tokens: base finisher 4.86 M generated (1,210 tokens/s, 4,112 s wall, 183 cap hits of 1,098), RL finisher 4.19 M (935
  tokens/s, 4,568 s, 43 cap hits). Rule-A loops 2 and 0; loop-detector errors 0.
- Limits: one sample per prefix and one prefix per problem; the pool is the 183 problems the base does not always solve, so
  the rates are not MATH-500 accuracies. Prefix ids are the stored text re-tokenized (the count differs from the sampled count
  in 50 of 366 answers, by at most 8 ids). Cuts 0 and 100 ran only in the smoke, RL finisher only.
- Jobs (one H100 each, commit `bd403e1`): base finisher `abaybektursun-1114-231144-7399`, RL finisher
  `abaybektursun-1114-231154-44ea`. Raw rows: `answers.jsonl` in each job's `$OUT_DIR` (Volume `iterate-runs`), not committed.

## Relay: Think-SFT writes, RL finishes (hard328, n = 328, T 1.0 / top-p 1.0, grader v3, board work-1c43cf, idea-968e5b)

No relay beats Think-SFT finishing its own answer. A stored answer (sample 0; Think-SFT + cue `abaybektursun-1115-000503-1e5f`,
212 of 328, 89 cap hits, 10,140 tokens per problem; RL plain `abaybektursun-1114-151540-86ef`, 206, 20 cap hits, 9,315) is cut
after 25 or 50 % of its token ids (a cap-hit answer: 4,096 or 8,192 ids) and a finisher model writes the rest, one sample, all
328 problems. Both models use the RL tokenizer, so the prefix ids pass unchanged. Spec `specs/SPEC_relay.md` (hypotheses and
numeric predictions filed before any job, commit `141c605`); plan `data/handoff/plan_v2.json`; readout
`results/relay/readout-01/readout.json`, `readout.txt` (`analysis/relay.py`; Wilson 95 % in percent, paired bootstrap 5,000
resamples, seed 0, in points).

Right of 328 [Wilson 95 %], cap hits, tokens per problem generated by the finisher / total with the prefix:

| writer -> finisher | cut 25 % | cut 50 % |
|---|---|---|
| Think -> Think (control) | 219 [62, 72], 86, 7,494 / 10,029 | 211 [59, 69], 96, 5,353 / 10,423 |
| Think -> RL (the relay) | 207 [58, 68], 17, 6,365 / 8,900 | 209 [58, 69], 13, 3,853 / 8,923 |
| RL -> RL (control) | 206 [57, 68], 29, 7,230 / 9,559 | 193 [53, 64], 23, 4,861 / 9,519 |
| RL -> Think | 204 [57, 67], 104, 8,182 / 10,511 | 199 [55, 66], 108, 6,006 / 10,664 |

Think -> RL minus Think -> Think: -3.7 [-7.6, +0.3] at 25 %, -0.6 [-4.3, +3.0] at 50 %. Think -> RL at 50 % against the stored
Think-SFT sample: -0.9 [-4.9, +3.0] (19 problems gained, 22 lost) with 12 % fewer tokens and 13 cap hits for 89; against the
stored RL sample +0.9 [-3.0, +4.9]. RL -> Think minus RL -> RL: -0.6 [-4.3, +3.0] and +1.8 [-1.5, +5.2]. For scale: the
Think-SFT vote over 4 has 241 at 40,410 tokens, the RL vote 221 ("Think-SFT with the cue under the vote rules"); the weight
stack Think-SFT + a (RL - base) has 220 (a = 1) and 234 (a = 2) in one sample (work-3d1e3b, first numbers, not final).

By the writer sample's outcome, right of n, Think finisher / RL finisher, and RL minus Think finisher in points:

| prefix | cut 25 % | cut 50 % |
|---|---|---|
| Think, right (208) | 194 / 184, -4.8 [-9.1, -0.5] | 191 / 187, -1.9 [-6.2, +2.4] |
| Think, finished wrong (31) | 7 / 5, -6.5 [-19.4, +6.5] | 4 / 5, +3.2 [0.0, +9.7] |
| Think, cap hit (89; 4 scored right as stored) | 18 / 18, 0.0 [-10.1, +9.0] | 16 / 17, +1.1 [-6.7, +9.0] |
| RL, right (206) | 188 / 187 | 186 / 188 |
| RL, finished wrong (102) | 13 / 14 | 10 / 4 (Think minus RL +5.9 [+1.0, +10.8]) |
| RL, cap hit (20) | 3 / 5 | 3 / 1 |

AIME (68) against the other sources (260), Think -> RL minus Think -> Think: -5.9 [-16.2, +4.4] and -3.1 [-7.3, +1.2] at 25 %;
-8.8 [-17.6, 0.0] and +1.5 [-2.3, +5.4] at 50 % (AIME 33 against 39; others 176 against 172).

- H0 (instrument): the smoke (`abaybektursun-1115-013352-9d6c`, RL finisher, 10 problems, cuts 0 to 100) gave 0 new tokens and
  the writer's score at cut 100 in 18 of 18; laptop checks in `analysis/handoff_test.py --plan plan_v2.json`. In the main run
  Think-SFT on its own prefix has 219 and 211 against 212 stored (intervals include 0). RL on its own prefix has 206 at 25 % and
  193 at 50 % against 206: -4.0 [-6.7, -1.2] at 50 %, so H0 fails for that arm: of its 206 right prefixes it keeps 188, of its
  102 wrong ones it turns 4. The cross arms are therefore read against the own-prefix arms.
- H1 (Think -> RL at 50 % at least 8 above the Think-SFT sample), refuted: 209, and the interval against the control includes 0.
- H2 (the gain comes from cap-hit prefixes), refuted: there is no gain there. On the 89 cap-hit prefixes the RL finisher has 18
  and 17 right, the Think finisher 18 and 16. What changes is how the answer ends: with the Think finisher 64 and 67 of the 89
  hit the cap again; with the RL finisher 13 and 8 do, and 59 and 65 end with a wrong boxed answer. Both finishers score above
  the stored 4 of 89, so a cap hit is partly chance: a second tail from the same prefix solves 16 to 18.
- H3 (RL -> Think is no better than RL -> RL), not refuted over the 328. On RL's 102 finished-wrong answers cut at 50 % the
  Think finisher has 10 and RL 4 (+5.9 [+1.0, +10.8]); it pays with 71 cap hits on those 102 against 14.
- H4 (RL as finisher stops), holds: 17 and 13 cap hits against 86 and 96, 8,900 and 8,923 tokens against 10,137.
- Predictions (spec): 6 of the 8 arm scores inside the filed 80 % ranges (outside: Think -> Think 25 % 219 for 205 [193, 217];
  RL -> RL 50 % 193 for 205 [195, 215]); the filed difference -7 [-20, +6] against -2 observed, "no arm reaches 220" held.
  Wrong: cap hits of the RL finisher on Think prefixes (filed 40 and 55, observed 17 and 13) and of the Think finisher on RL
  prefixes (70 and 50, observed 104 and 108); the cap stratum (filed 12 / 16 and 8 / 11, observed 18 / 18 and 16 / 17).
- Raw rows, read by hand (`results/relay/readout-01/examples.json`: 10 gained, 10 lost, 6 cap-hit prefixes of Think -> RL at
  50 %). RL resumes mid-sentence and keeps the Think-SFT plan in every row read; it then writes a formatted solution and a boxed
  answer. Of the 19 problems gained over the Think-SFT sample, 14 are cap-hit prefixes and 5 finished-wrong ones; of the 22
  lost, 20 are right prefixes that RL finishes with a wrong answer (problem 68: RL continues Think-SFT's table of winning
  positions from n = 28 and boxes 1215 for 809; Think-SFT's own continuation of the same prefix is right). Problem 265: the Think-SFT prefix is a loop repeating the prompt's
  last sentence; RL leaves the loop after 730 tokens and boxes 1938, right. Problems 101 and 70: RL closes a cap-hit prefix by
  boxing a number its own text does not support ("close to 80"; `\sqrt{3} \times 988` then `\boxed{78}`).
- Limits: one sample per prefix, one prefix per problem. Think-SFT is trained (no reward, not no training); its training
  prompts match 6 of the 328 (result-f6a8bc). A relay needs both models loaded, which the token count does not price.
- Jobs (one H100 each, commit `141c605`): RL finisher `abaybektursun-1115-013411-6d5e` (25 %, 4.46 M tokens, 5,153 s),
  `-013431-3d3b` (50 %, 2.86 M, 3,650 s); Think finisher `-013421-6338` (25 %, 5.14 M, 6,165 s), `-013441-d35a` (50 %, 3.73 M,
  4,923 s); with the smoke 5.6 H100-hours. Run folders `results/relay/{rl,think}_c{25,50}-01/` (`run.json`, `metrics.json`,
  `rows.jsonl` without text, `examples.json`: one right, one wrong). Raw rows: `answers.jsonl` in each job's `$OUT_DIR` (Volume
  `iterate-runs`), not committed.

## Entropy-gated temperature: no gate beats T 1.0; forks and confident positions make loops together (board work-deec92, idea-069f19)

Spec `specs/SPEC_egate.md` (written before any run; amendment 1 before the repeat-aware arm). Every request runs at
T 1.0 / top-p 1.0; the logits processor `lib/egate.py` divides the logits by `t_low` at the positions its arm names. H is the
entropy of the next-token distribution at temperature 1; the threshold h0 = 0.9 nats is the 80th percentile of H over 69,978
positions of 50 MATH-500 problems at T 1.0 (calibration in `results/egate/calib-01/metrics.json`, mean H 0.416 nats). Base +
cue, grader v3, cap 16,384, vast.ai RTX PRO 6000 (vLLM 0.32.0, Model Runner V2, engine in-process).

### Screen: first 100 MATH-500 problems, one sample, seed 61,000,000 + index (`results/egate/screen-01/`, `screen_esc-01/`)

| Arm | Positions sharpened | t_low | Share sharpened | Right | Cap hits | Rule-A loops | Right of finished | Tokens per problem |
|---|---|---|---|---|---|---|---|---|
| t1 | none | | 0 | 87 | 4 | 0 | 87 of 96 | 3,905 |
| all6 | all (constant T 0.6) | 0.6 | 1 | 80 | 17 | 12 | 80 of 83 | 4,006 |
| hi6 | H > h0 | 0.6 | 0.119 | 87 | 6 | 2 | 87 of 94 | 3,418 |
| lo6 | H <= h0 | 0.6 | 0.872 | 90 | 4 | 3 | 90 of 96 | 2,950 |
| rnd6 | random, probability 0.187 | 0.6 | 0.188 | 88 | 3 | 1 | 88 of 97 | 3,634 |
| hi3 | H > h0 | 0.3 | 0.090 | 82 | 9 | 7 | 81 of 91 | 3,581 |
| hi1 | H > h0 | 0.1 | 0.090 | 81 | 8 | 7 | 81 of 92 | 3,398 |
| lo3 | H <= h0 | 0.3 | 0.911 | 82 | 17 | 10 | 81 of 83 | 4,389 |
| esc6 | all, except 256 positions after a repeat | 0.6 | 0.752 | 80 | 8 | 4 | 80 of 92 | 3,255 |
| esc3 | all, except 256 positions after a repeat | 0.3 | 0.620 | 82 | 8 | 7 | 82 of 92 | 3,008 |
| esc6k | all, except 1,024 positions after a repeat | 0.6 | 0.579 | 83 | 5 | 5 | 83 of 95 | 3,257 |
| esc3k | all, except 1,024 positions after a repeat | 0.3 | 0.504 | 84 | 6 | 6 | 84 of 94 | 3,167 |

- Instrument checks of the spec hold: all6 through the processor reproduces the stored constant T 0.6 cell on these 100 problems
  (17 cap hits, 12 loops, 80 right against 18, 12, 77 in job -151718-d4fa); t1 (87 right, 4 cap hits) is inside the four stored
  T 1.0 samples (77 to 87 right, 2 to 6 cap hits); the processor sharpened 0 % of t1's positions, 100 % of all6's and 11.9 %
  of hi6's. The planted tests of the gate, the percentile and the repeat detector run at the start of every job.
- Neither single-regime hypothesis of the spec holds. At t_low 0.6 neither gate alone reaches the midpoint of 10.5 cap hits
  (hi6 6, lo6 4, all6 17). At t_low 0.3 the confident positions alone loop as much as constant T 0.6 (lo3 17 cap hits, 10
  loops) and the forks alone about half as much (hi3 9 and 7; hi1 8 and 7). Loops rise with the strength of sharpening in
  either regime.
- The first 100 problems are too few to read a difference in right answers (one arm's standard error is about 4 points), and
  the screen misled on cap hits too: lo6 had 4 of 100 here and 4 to 10 on the same 100 problems in the four fresh samples below.
- Raw answers: of the 82 looping answers on these 100 problems over all jobs of this section, the repeated block opens with
  `Wait` in 19, `But` in 14 and `Alternatively` in 6: the model returns to a doubt it has already stated (two blocks per arm
  read in full for all6, lo3, hi1 and lo6).

### The 2x2 at n = 500 and the stage-2 test (`results/egate/math500_lo6-01/`, `math500_hi6-01/`, `math500_esc3k-01/`)

All 500 problems, fresh seeds (sample s: 61,000,000 + 10,000 s + index, s from 1, so that no row repeats a screen seed). The
reference is the four stored T 1.0 samples of job -153825-208b (`results/day1_3/math500_base_cue-01/rows.jsonl`, attempt 0).
Differences are per problem (mean over the samples), 95 % bootstrap over problems, 5,000 resamples, seed 0.

| Cell | Samples | Right per 500 | Minus T 1.0, points | Cap hits per 500 | Rule-A loops per 500 | Right of finished | Tokens per problem |
|---|---|---|---|---|---|---|---|
| T 1.0 (stored) | 4 | 410.5 | | 22.5 | 0 | 85.9 % (1,641 of 1,910) | 4,008 |
| lo6: T 0.6 where H <= 0.9 (87 % of positions) | 4 | 403.5 | -1.4 [-3.2, 0.4] | 44.2 | 20.8 | 88.3 % (1,609 of 1,823) | 3,954 |
| hi6: T 0.6 where H > 0.9 (12.1 % of positions) | 2 | 403.5 | -1.4 [-3.5, 0.8] | 33.0 | 13.0 | 86.0 % (803 of 934) | 3,876 |
| constant T 0.6 (stored, 1 sample) | 1 | 378 | | 98 | 71 | 94.0 % (378 of 402) | 4,690 |
| esc3k: T 0.3, back to T 1.0 for 1,024 positions after a repeat | 1 | 404 | -1.3 [-4.3, 1.5] | 47 | 23 | 89.0 % (403 of 453) | 3,798 |

- Stage 2 of the spec is refuted for both gates. lo6 (the screen's best arm, 90 of 100) scores 403.5 of 500 over four fresh
  samples (413, 399, 393, 409) and hi6 the same 403.5 over two (395, 412): both -1.4 points against T 1.0, intervals through 0.
  The screen's 90 was a lucky sample.
- Each gate raises the share of finished answers that are right (lo6 88.3 %, T 1.0 85.9 %) and loses more answers to the cap
  than it gains: the trade of constant T 0.6, at a smaller size.
- The two regimes interact. Cap hits per 500: T 1.0 22.5, forks only 33.0 (+10.5), confident positions only 44.2 (+21.8),
  both 98 (+75.5). If the two effects added, both together would give 54.8 cap hits; the stored T 0.6 cell has 98 (rule-A
  loops: 13.0 + 20.8 = 33.8 added, 71 observed). A loop needs a sharpened choice at the fork and a sharpened continuation after
  it. The 12 % of positions with H > 0.9 carry a third of the added cap hits, about 4 times their share of positions.
  Caveat: the T 0.6 cell is one stored sample; its 98 cap hits are far outside the range of the gated samples (30 to 51).
- Returning to T 1.0 after a repeat removes half of the loops and none of the cost: esc3k (T 0.3 at 57 % of positions) has
  47 cap hits and 23 loops, half of constant T 0.6 at a lower temperature, and 404 right, -1.3 points [-4.3, 1.5]. Its
  right of finished is the highest of the section (89.0 %). One sample only: the second (job -232552-5470) finished, and I
  destroyed its box while the copy was running.
- Across this section, the truncation rules of result-44b4df (min-p, top-p) and constant T 0.6, every rule that removes
  randomness from the cued base raises accuracy among finished answers and adds loops that cost as much or more. No decoding
  rule tested here beats plain T 1.0 sampling on MATH-500, so none was run on the 328.
- Deviations from the spec: stage 2 used fresh seeds (samples 1 to 4) instead of the screen's sample 0, so that the arm picked
  for its screen score is not scored on the same draws; hi6 has 2 samples and esc3k 1 instead of 4 (box lifetime).

Stage 3 (the 328) was not run: the spec allows it only for an arm whose stage-2 interval is above 0.

Run folders `results/egate/<run>/`: `run.json` (job ids, commit, command arguments, h0), `metrics.json` (the jobs' own counts and
the processor's entropy histograms), `rows.jsonl` (per answer: arm, problem, sample, seed, tokens, cap hit, loop, extracted
answer, score), `examples.json` (one right and one wrong answer per arm, with the prompt), `readout.json`. Raw answers:
`runs/<job-id>/answers.jsonl` on the laptop of abaybektursun (not committed; the vast.ai boxes are destroyed). Cost: about
17 USD of vast.ai rent.

```
python3 tools/vast.py run <box> -- 'PIP_BREAK_SYSTEM_PACKAGES=1 bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.egate_cell --model base --set math500 --n 100 --seed 61000000 --h0 0.9 --rnd-share 0.1869444682614536 --arms t1=off:1 hi6=hi:0.6 --commit <sha>'
uv run --with numpy python -m studies.rlneurons.analysis.egate screen-01 runs/<job-id> [runs/<job-id> ...]
uv run --with numpy python -m studies.rlneurons.analysis.egate math500_lo6-01 runs/<job-id> ... --ref studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl
```

## Signed self-training with no reward: it loses points, by making the base doubt and run out of tokens (hard328, board work-d9a824, idea-0d55a4)

Spec `specs/SPEC_signed1.md` (written before the runs, amended once before the cells). The missing cell of the 2x2
{vote, key} x {positives only, signed}: one LoRA epoch on the base's own 4 stored cue samples per MATH-500 problem (job
abaybektursun-1114-153825-208b), loss = sum of advantage x mean per-token NLL, advantage = return minus the problem's mean
return. Arm P: return 1 for a finished sample in the plurality group (no reward, no key; 138 problems). Arm G: return = grader
v3 score (uses the key; 150 problems). Data `data/signed/arms-v1.json` (`jobs/signed_data.py`), trainer `jobs/signed_train.py`
(LoRA, hyperparameters and merge of `jobs/distill_train.py`), readouts `analysis/signed1.py`, `analysis/signed1_read.py`.

Cue, T 1.0 / top-p 1.0, cap 16,384, grader v3, seed 3000000, one sample, n 328 (`results/signed1/readout.json`, `read.json`):

| model | right of 328 | minus base cue, points [95 %] | cap hits | tokens per problem | Wait per 1,000 tokens |
|---|---|---|---|---|---|
| base cue (job e72c) | 164 | | 77 | 9,344 | 4.6 |
| signed P, vote as return (`results/signed1/P-01/`) | 140 | -7.3 [-11.9, -3.1] | 178 | 11,775 | 10.5 |
| signed G, key as return (`results/signed1/G-01/`) | 155 | -2.7 [-7.0, 1.5] | 145 | 11,055 | 8.7 |
| for reference: SFT on voted samples V / U, cue | 167 / 168 | | | | |

- H1 (the sign carries RL's gain) is refuted: P is below the base with the interval below 0. H2 is refuted too: the key as
  return (G) gives no gain either. So neither the sign nor the reward's information, applied offline for one epoch to 4 stored
  samples per problem, moves the base toward RL (206 plain).
- What the raw answers show: the loss is in answers that no longer finish. Cap hits go from 77 to 178 (P) and 145 (G); 2 and 1
  of them repeat a line, so they are not loops. The word Wait doubles. On the problems both models finish, accuracy is the
  same: P 127 against 124 of 144, G 141 against 134 of 168. Of P's 107 new cap hits the base had 37 right.
  Lowering the probability of whole wrong samples taught the model to doubt and restart, not to avoid the wrong step.
- The pre-registered instrument check (NLL of wrong minus right samples on not-yet-trained problems) did not rise over the
  epoch (P 0.123 then 0.090 nats per token by half; G 0.128 then 0.072): the update did not learn to tell right from wrong
  samples on new problems. Cosine of the merged difference with RL minus base: 0.001 (P), 0.003 (G).
- Not tested: more epochs, online resampling after each update, a smaller step. Train jobs abaybektursun-1114-214246-17cc (P),
  -214255-116e (G); cells -220703-1a4c, -220719-fa57; raw answers in the Modal Volume under /runs/<job>.

## Seen against unseen: is the RL gain practice on its training prompts? (harder set, 72 seen + 130 unseen, 4 samples, board work-fec451, idea-c1d00f)

No. RL's advantage over Code-RL is 6.9 points on the 72 problems that are in its training prompts and 4.0 on matched unseen
problems: D = +2.9 points, 95 % interval [-4.8, +10.6]. The hypothesis D >= +15 is refuted: the point is inside +/-8 and the
interval excludes +15. The interval is not wholly inside +/-8 (half-width 7.7 here; the spec expected about 9.5 before
the run), so a practice effect of up to about 10 points is not excluded.

All from `results/seen/readout.json` and `readout.md` (`analysis/seen.py`, spec `specs/SPEC_seen.md`, written before the run).
T 1.0 / top-p 1.0, cap 16,384, 4 samples per problem, no restart, grader v3, seed 3,000,000 + 10,000 s + index. Seen = the 72
of `hard.json` with overlap flag exact (43, all AIME 2022 and 2023) or near (29: AIME 9, AMC 23 12, OlympiadBench 8);
`run_cell --set hard72`. Unseen = `--set hardmatch`, 130 of the 328: every AIME (68: 59 of them 2024 or 2025), every AMC 23
(28), every sixth OlympiadBench problem (34). The match is by source family only, not by year: each unseen number is the mean of
the three family means weighted by the family shares of the seen set beside it. Percent right; bootstrap over problems (seen and
each unseen family resampled separately, arms paired), 5,000 resamples, seed 0, 95 % percentile, in points.

| Arm (all 72 against unseen) | Per sample: seen | unseen | seen - unseen | Vote over 4: seen | unseen | seen - unseen | Tokens per answer: seen | unseen |
|---|---|---|---|---|---|---|---|---|
| base, cue | 20.8 | 40.0 | -19.1 [-28.7, -9.2] | 30.6 | 52.7 | -22.1 [-35.8, -8.1] | 12,952 | 10,541 |
| RL, plain | 37.5 | 55.5 | -18.0 [-29.6, -5.9] | 45.8 | 64.2 | -18.3 [-32.5, -3.6] | 12,097 | 10,344 |
| Code-RL, cue | 30.6 | 51.4 | -20.9 [-32.7, -9.0] | 34.7 | 57.9 | -23.2 [-37.1, -8.8] | 11,068 | 9,195 |
| Think-SFT, cue | 46.2 | 62.0 | -15.9 [-28.1, -3.3] | 63.9 | 72.7 | -8.8 [-22.5, 4.8] | 13,107 | 11,145 |

| Per sample, percent right | base, cue | RL, plain | Code-RL, cue | Think-SFT, cue |
|---|---|---|---|---|
| seen, exact (43) | 13.4 | 32.6 | 22.7 | 41.9 |
| unseen, AIME only (68) | 30.5 | 47.1 | 40.4 | 54.4 |
| seen, near (29) | 31.9 | 44.8 | 42.2 | 52.6 |
| unseen, weighted as near | 54.0 | 67.9 | 67.7 | 73.3 |

| D = (RL - control) seen minus unseen | Per sample: seen | unseen | D | Vote over 4: seen | unseen | D |
|---|---|---|---|---|---|---|
| Code-RL, cue (primary), all 72 | 6.9 [0.7, 13.2] | 4.0 [-0.6, 8.6] | +2.9 [-4.8, 10.6] | 11.1 [1.4, 20.8] | 6.2 [-0.6, 13.4] | +4.9 [-7.3, 17.2] |
| base, cue, all 72 | 16.7 [10.4, 22.9] | 15.5 [11.1, 20.0] | +1.2 [-6.4, 8.8] | 15.3 [5.6, 25.0] | 11.5 [5.2, 18.3] | +3.8 [-7.8, 15.8] |
| Think-SFT, cue, all 72 | -8.7 [-14.6, -2.8] | -6.6 [-10.9, -2.6] | -2.1 [-9.1, 5.0] | -18.1 [-27.8, -6.9] | -8.5 [-14.3, -3.7] | -9.5 [-21.0, 2.3] |
| Code-RL, exact 43 | 9.9 [4.1, 16.3] | 6.6 [0.7, 12.5] | +3.3 [-5.0, 12.3] | 16.3 [7.0, 27.9] | 10.3 [1.5, 19.1] | +6.0 [-7.7, 20.8] |
| base, exact 43 | 19.2 [11.1, 28.5] | 16.5 [11.0, 22.4] | +2.6 [-7.2, 13.5] | 23.3 [11.6, 37.2] | 16.2 [8.8, 25.0] | +7.1 [-7.9, 22.5] |
| Code-RL, near 29 | 2.6 [-9.5, 14.7] | 0.2 [-4.4, 4.5] | +2.3 [-10.9, 15.1] | 3.5 [-13.8, 20.7] | 0.2 [-6.1, 6.3] | +3.2 [-16.6, 22.4] |
| base, near 29 | 12.9 [4.3, 21.6] | 14.0 [9.7, 18.4] | -1.0 [-10.6, 8.7] | 3.5 [-10.3, 20.7] | 4.5 [-2.3, 11.1] | -1.1 [-18.1, 15.7] |

- The seen problems are harder, not easier, for every arm: the base with cue has 20.8 % on them against 40.0 % on matched
  unseen problems (-19.1 [-28.7, -9.2]), Code-RL -20.9, RL -18.0. So there is no sign of pretraining exposure helping on the
  older AIME years. The likely cause is how the training set was built: the Olmo 3 paper (arXiv 2512.13961, section 6.1) removes
  prompts that the base solved 8 of 8 times, so the problems that stayed are the ones the base fails. Consistent with it: none
  of the 43 exact problems is solved 4 of 4 by the base with cue (29 are solved 0 of 4). Not tested further.
- RL carries the same difficulty penalty as the models that did not train on these prompts (-18.0 against -19.1 and -20.9):
  2,800 steps of RL on prompts that include these 72 did not make them easier than unseen problems of the same source.
- Exact against near: D(Code-RL) +3.3 on the 43 exact and +2.3 on the 29 near, intervals about +/-9 and +/-13. No difference
  that these n can show.
- Vote over 4 gives the same sign with wider intervals (D(Code-RL) +4.9 [-7.3, 17.2]); it cannot exclude +15.
- Think-SFT with the cue is ahead of RL on both sets (46.2 against 37.5 seen, 62.0 against 55.5 unseen per sample; vote 63.9
  against 45.8 seen), with more cap hits (47.9 % of its seen answers against RL's 19.8 %). Its seen - unseen difference under
  the vote is the smallest of the four (-8.8 against -18 to -23), interval [-22.5, 4.8]. Its SFT data has 753 k math prompts from
  OpenThoughts3 whose overlap with AIME is not checked, so it is not a clean control here.
- Is Code-RL a valid control? Yes, as far as its cards say: model card "reinforcement learning from verifiable rewards on the
  Dolci-RL-Zero-Code-7B dataset which consists of coding queries", dataset card "13.3k coding questions and answers"; no math
  prompts named. Same base, same release (3.1).
- Raw rows, read by hand. The 6 seen problems that RL solves at least 3 of 4 times and the base at most once (25, 27, 38, 40,
  53, 311): RL's answers are worked solutions of 2,574 to 13,174 tokens (problem 38: counts pairs of lines, C(40,2) - 173 = 607;
  problem 25: enumerates prime pairs case by case, then doubts and rechecks 72). No RL answer on a seen problem states the
  answer without work: the shortest right one has 2,574 tokens, none is under 2,000. RL's right answers on seen AIME problems
  are longer than on unseen AIME ones (median 9,346 tokens, n 67, against 6,802, n 128), the opposite of recall. Phrases such
  as "I recall" or "known problem" occur in 78 of RL's 288 seen answers and in 77 of the base's 288: generic ("I remember that
  in combinatorial geometry ..."), not a quoted solution.
- Checks: `analysis/seen_test.py` (planted D = +20 gives an interval above 0; planted D = 0 and a seen set that is only easier
  for every arm give intervals that include 0; half-width on planted rows 10.1 points). Smoke `abaybektursun-1114-234109-8937`
  (Think-SFT, 10 problems, 2 samples): 20 rows read, seeds as planned, 8 right, 12 cap hits. `run_cell --set hard328` dry-run
  rows are identical before and after the change (every field but the time stamp).
- Not controlled: the year (51 of 52 seen AIME problems are 2022 or 2023, 59 of 68 unseen are 2024 or 2025; only 9 unseen AIME
  problems are from 2022 or 2023). The base and RL unseen rows are attempt 0 of each sample of the hard328 vote jobs
  (`--restarts 2`, commit `2c58f34`), so they shared a GPU batch with restart requests; the other six cells ran at `d01a65e`.
- Literature (WebSearch; the Exa tools had no key): no published accuracy of an RL-trained model on RL-seen against matched
  unseen test problems was found. Nearest: arXiv 2602.11792 and 2511.14045 (membership inference on RLVR data: detection
  scores, no accuracy), read in HTML, not in full.

| Run folder (`results/seen/`) | Job id | Rows | Right (v3) | Cap hits |
|---|---|---|---|---|
| `base_hard72-01/` | `abaybektursun-1114-234946-5a29` | 288 | 60 | 125 |
| `rl_hard72-01/` | `abaybektursun-1114-234953-16b2` | 288 | 108 | 57 |
| `code_hard72-01/` | `abaybektursun-1114-235001-9aae` | 288 | 88 | 55 |
| `sft_hard72-01/` | `abaybektursun-1114-235010-8446` | 288 | 133 | 138 |
| `code_hardmatch-01/` | `abaybektursun-1114-235021-8606` | 520 | 298 | 60 |
| `sft_hardmatch-01/` | `abaybektursun-1114-235030-602b` | 520 | 345 | 154 |
| `base_hardmatch-01/` | `abaybektursun-1114-200457-e8e6` (work-1a972a; 520 of its rows) | 520 | 230 | 133|
| `rl_hardmatch-01/` | `abaybektursun-1114-200505-5ff2` (work-1a972a; 520 of its rows) | 520 | 312 | 61|

Each run folder: `run.json`, `metrics.json` (the job's, for the two reused jobs over all its rows), `rows.jsonl` (every row used,
without text), `examples.json` (one answer scored right, one scored wrong, with prompt and text). No row is missing in any job.
Raw answers: `runs/<job-id>/answers.jsonl` after `uv run tools/gpu.py get <job-id>` (abaybektursun's Modal workspace). Cost: six
H100 jobs and the smoke, 7.1 GPU-hours, about 28 USD at 3.95 USD per hour. Commands (one per arm and set; Code-RL and Think-SFT
as in "Weight-difference line" and WSP-1):

```
uv run tools/gpu.py submit h100 --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model rl --prompt plain --set hard72 --temperature 1.0 --top-p 1.0 --seed 3000000 --samples 4 --commit $(git rev-parse HEAD)"
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.seen
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.seen_test
```

## Think-SFT with the cue under the vote rules: 241 of 328, above RL under every rule (hard328 n = 328, MATH-500 n = 500, 4 samples, board work-0a00c2, idea-1d9f26)

Question: Think-SFT (`allenai/Olmo-3-7B-Think-SFT` at `6ff8575`, imitation of reasoning traces: no reward, but training) with
the opening cue had 219 of 328 in one sample (result-d9d6f3). What does it score under the rules chosen on MATH-500, and is it
ahead of RL under the same rule? Answer: yes on the 328. Vote over 4: Think-SFT 241 of 328 (73.5 % [68.4, 78.0]) at 40,410
tokens per problem, RL plain 221 (224 after restart), base + cue 192 (195): Think-SFT minus RL +6.1 points [3.0, 9.5], paired.
One sample: 212, 212, 211, 201 (mean 209.0) against RL 207, 190, 209, 194 (mean 200.0): +2.7 points [0.4, 5.2] on the
24-order means. On MATH-500 the vote is 481 of 500 against RL 474: +1.4 points [-0.4, 3.2], not separated; singles 461, 457,
462, 461 against RL 456 to 464. Spec and predictions, filed before any job finished: `specs/SPEC_thinkvote.md` (commit
`a1822c8`). T 1.0 / top-p 1.0, cap 16,384, grader v3, no restarts for Think-SFT (its `restart` rows equal the plain rows).

Caveats. (1) Think-SFT is trained on 2.27 M traces: the route uses no reward, not no training. (2) Overlap with its training
prompts (result-f6a8bc, sameraslan; prompts only, 33 code shards unscanned): 6 of the 328 and 25 of MATH-500 match. Without
them: hard328 n = 322 vote 235 against RL 215 (+6.2 points), single 207 against 201; MATH-500 n = 475 vote 456 against 450.
(3) RL and base rows have up to two restarts per sample, Think-SFT none; the comparison above uses the no-restart vote of all
three, and RL's vote after restart (224) is still 17 below.

| Rule (chosen on MATH-500) | Set | Think-SFT + cue: right, right (24), tokens | RL plain: right, right (24), tokens | base + cue: right, right (24), tokens |
|---|---|---|---|---|
| one sample | hard328 | 212, 209.0, 10,137 | 207, 200.0, 9,437 | 161, 158.5, 9,074 |
| vote over 4 (no restart) | hard328 | 241, , 40,410 | 221, , 37,299 | 192, , 36,902 |
| sequential vote, at most 3 (`seq3`) | hard328 | 241, 233.2, 26,269 | 216, 212.7, 23,613 | 183, 178.8, 25,601 |
| sequential vote, at most 4 (`seq4_restart`) | hard328 | 241, 238.9, 30,904 | 224, 218.2, 31,326 | 194, 190.8, 46,317 |
| sequential vote, at most 4, ties to the shortest (`seq4_restart_short`) | hard328 | 240, 239.5, 30,904 | 222, 220.5, 31,326 | 198, 198.5, 46,317 |
| vote over 4 after restart, ties to the shortest | hard328 | 239, 239.0, 40,410 | 220, 220.0, 44,108 | 199, 199.0, 55,306 |
| one sample | MATH-500 | 461, 460.2, 4,900 | 456, 460.0, 4,675 | 405, 410.5, 3,808 |
| vote over 4 | MATH-500 | 481, 480.8, 19,503 | 474, 474.3, 18,747 | 446, 448.2, 16,034 |
| sequential vote, at most 4 (`seq4`) | MATH-500 | 481, 480.8, 11,521 | 474, 474.3, 11,098 | 446, 448.2, 11,369 |
| sequential vote, at most 4, ties to the shortest (`seq4_short`) | MATH-500 | 481, 480.5, 11,521 | 475, 474.5, 11,098 | 451, 452.0, 11,369 |

Right = stored draw order, right (24) = mean over the 24 draw orders, tokens = generated tokens per problem. RL and base rows
on the 328 are those of `results/day1_3/hard328_*_s4r2-01/` and `results/frontier/hard328-01/` (board work-1a972a), not
recomputed; MATH-500 rows of `results/frontier/math500-01/`. These are the Think-SFT rows for the deliverable table of "Token
frontier": the best reward-free configuration on the 328 is Think-SFT + cue with the sequential vote, 241 (238.9 over the
orders) at 30,904 tokens, against RL's best 224 at 31,326 under the same rule (-6.3 points [-9.5, -3.3] for RL).

Instrument checks. hard328 sample 0 repeats sameraslan's cell on its seeds: 212 right and 89 cap hits against 219 and 89
(other GPU; inside the 12 allowed). MATH-500 sample 0: 461 against the stored 454. The join of four one-sample jobs was
tested against one `--samples 4` dry run: the same (problem, sample, attempt, seed) for all 40 rows, and a run with the
wrong seed offset is refused. Smoke (10 problems): cue ids in the prompt, 355 tensors bit-identical to Think-SFT, 9 of 10.

Predictions scored (`results/thinkvote/scored-01/readout.json`):

- H1, MATH-500 vote over 4, filed blind by the rate and hazard studies: 473.1 [466, 480] and 472.1 [464, 480]. Observed 481:
  outside both intervals by one problem, and above the 479 that result-bf6124 named as refuting the one-axis claim. Part of
  the miss is the input: both rules started from the stored single cell (454), and the four singles here have 457 to 462.
- H2, hard328 vote over 4: observed 241. Rasch with RL's vote shift 238.6 (miss 2.4), Rasch with the base's vote shift 243.8
  (2.8), mine 238 [228, 250] (3.0, held), point rule from MATH-500 245.9 (4.9), point rule from the 328 234 (7.0). The Rasch
  rule wins, all five inside sampling noise (binomial sd 8). They were anchored at 219; from the measured single (212) the
  vote gained 29 problems, more than any rule's gain (15 to 27).
- hard328 single, the profile study's rules against the mean of four samples (209.0): `profile_corrected` 209.2, profile
  217.6, L1 201.1, Lc 196.3, P 190.5. The profile rule still wins; the one-axis rules miss low by 8 to 18.
- H3 (Think-SFT ahead of RL under the vote on the 328 by at least 2 points): held, +6.1 [3.0, 9.5].
- H4 (RL stays ahead on MATH-500 under the vote): refuted, 481 against 474, not separated.
- H5 (sequential vote within 1.5 points of the vote at 25 % fewer tokens): held on MATH-500 (480.8 against 480.8, 41 % fewer);
  refuted on the 328 by the token bar (238.9 against 241, 24 % fewer).
- H6 (cap hits are unfinished reasoning, not loops): held. Rule A flags 6 of 378 cap hits on the 328.

What the raw rows show (`analysis/thinkvote_read.py`, counts in `scored-01/readout.json`):

- Think-SFT abstains where RL answers wrong. On the 328 it hits the cap on 378 of 1,312 samples (29 %; RL 114, 9 %), and
  its finished answers are right 88.0 % of the time (RL 66.2 %). A cap hit casts no vote, so the vote is almost pass@4: 241
  against 244 (RL 221 against 240, base 192 against 207). This is why its vote gains 29 problems and RL's 14.
- The cap hits are long reasoning that keeps trying cases: median share of distinct lines in the last 6,000 characters 0.99
  (sample 0), and 86 of the 378 contain more than 20 Chinese characters (RL: 1 of 114). 61 problems hit the
  cap in both of the first two samples. A higher cap is the untested lever.
- 13 of the 328 have the Think-SFT vote right and no RL sample right in any attempt (75, 98, 109, 112, 116, 162, 168, 169,
  199, 232, 289, 369, 392: olympiad, AIME and HMMT problems; on them RL mostly finishes with a wrong answer, e.g. problem 75: Think-SFT 73 in all four samples, RL 234 three times). The reverse set has 5 problems, and
  Think-SFT hits the cap on 19 of its 20 samples there. Vote right for one model only: Think-SFT 26, RL 6.
- Its errors on easy MATH-500 problems are mostly the answer line, not the mathematics. Levels 1-2, three samples read by
  hand: 16 errors = 8 with the right answer in a form grader v3 does not take (`Answer:` then the answer on the next line,
  `Answer: $Answer`, `137 1/2` for `137 \frac{1}{2}`), 3 cap hits, 5 wrong (problem 18 three times, an Asymptote figure).
  Over all four samples 16 of its 74 finished wrong answers on MATH-500 end in a line that equals the gold (RL: 0 of 131); on
  the 328, 4 of 112. Grader v3 is unchanged, so Think-SFT's MATH-500 singles are about 4 problems low per sample; this is the
  "easy-side" deficit of "Difficulty profiles" in part.

Part B (the stack Think-SFT + RL difference) was not run here: work-3d1e3b claimed it. `jobs/thinkvote_stack.py` (stochastic
BF16 rounding of sft + scale (rl - base), effective-scale check, selftest on synthetic weights) is in the repository for it.

Jobs (abaybektursun's Modal, H100/H200, one per sample, 5.6 GPU-hours of job time, about 22 USD at Modal's H100 price): hard328 `abaybektursun-1115-000503-1e5f`,
`-000525-ea4e`, `-014823-ef56`, `-014833-1daa` (seeds 3000000 + 10000 s); MATH-500 `-000512-ee03`, `-014843-85d9`,
`-000607-0e92`, `-000621-1d7e` (181000000 + 10000 s); smoke `-000018-b6b5`. Three jobs died twice at start under the old
runner (no rows) and were resubmitted. Raw answers: `runs/<job>/answers.jsonl` in that workspace. Run folders
`results/thinkvote/{hard328,math500}_sft1_cue_s4-01/` (`run.json`, `metrics.json`, `readout.json`, `rows.jsonl`,
`examples.json`: one vote right, one wrong), `frontier_{hard328,math500}-01/` (the `--base` slot holds Think-SFT; labels in
`frontier.md` edited, numbers untouched), `scored-01/`. Commands:

```
uv run tools/gpu.py submit h100 --hours 2.5 -- "bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe interp --other think_sft --alpha 1.0 --rounding nearest --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label sft1 --prompt cue --set hard328 --temperature 1.0 --top-p 1.0 --seed <3000000 + 10000 s> --commit $(git rev-parse HEAD)"
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.thinkvote_join --runs runs/<s0> runs/<s1> runs/<s2> runs/<s3> --out runs/thinkvote_hard328_sft1_cue_s4
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_vote --run runs/thinkvote_hard328_sft1_cue_s4 --out studies/rlneurons/results/thinkvote/hard328_sft1_cue_s4-01 --minus studies/rlneurons/results/day1_3/hard328_rl_plain_s4r2-01/readout.json
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.frontier --base studies/rlneurons/results/thinkvote/hard328_sft1_cue_s4-01 --rl studies/rlneurons/results/day1_3/hard328_rl_plain_s4r2-01 --fixed studies/rlneurons/results/frontier/math500-01/chosen.json --out studies/rlneurons/results/thinkvote/frontier_hard328-01
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.thinkvote_read --out studies/rlneurons/results/thinkvote/scored-01
```

### One cell on N GPUs: `run_cell --shard k/N` and `analysis/shard_join.py`

On a 48 GB card (AWS L40S) a cell is limited by the KV cache: the long answers fill it, 9 to 12 sequences run and the rest
wait (job `ih-1115-092337-b35c`, 110 of 500 answers after 23 minutes, about 200 tokens/s). `--shard k/N` gives one job the
problems k, k+N, k+2N, ... of the set; a request's seed depends on its problem index, so the N jobs have the requests of the
one job. `analysis/shard_join.py` checks the N folders (all done, shards 0..N-1 once each, same config, seed and commit, no
problem twice) and writes the folder the one job would have written. Checks: `analysis/shard_join_test.py` (7 planted cases,
5 that must fail); laptop dry run, `--n 11 --samples 2`, 3 shards against the unsharded run: the same 22 requests, seeds and
prompts.

```
<submit> "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell <the cell's arguments> --shard 0/4 --commit $(git rev-parse HEAD)"   # and 1/4, 2/4, 3/4
uv run --no-project python -m studies.rlneurons.analysis.shard_join --runs runs/<job 0> runs/<job 1> runs/<job 2> runs/<job 3> --out runs/<name>
uv run --no-project python -m studies.rlneurons.analysis.shard_join_test
```

## Delta transplant: Think-SFT + 2 (RL-Math - base) scores 231.5 of 328, above both parents (hard328, cue, board work-3d1e3b)

Spec `specs/SPEC_transplant.md` (written before any run; amendment 1 before a = 3, a = 4 and the second sample of a = 2).
M(a) = Think-SFT + a (RL-Math - base), every tensor, written by `jobs/delta_sum.py` (stochastic rounding to BF16; the written
model carries a to 5 digits: effective a 1.00000, 2.00000). ||Think-SFT - base|| = 467.4, ||RL-Math - base|| = 4.12 (113 times
smaller), cosine -0.002. Cue, T 1.0 / top-p 1.0, cap 16,384, grader v3, vast.ai RTX PRO 6000, one sample per job.

Method is published for another pair: 2605.00610 sums an SFT and a GRPO vector on Qwen2.5-Math-7B (47.8 against parents 44.1
and 45.5 on six sets). New here: the RL donor was trained from the base with no demonstrations, the SFT parent on other data,
the set is held out from the RL prompts, and the coefficient is followed past the peak with cap hits and a noise control.

### hard328, n = 328 (`results/transplant/hard328-01/`)

References are committed rows of the same harness: Think-SFT cue, 4 samples (`results/thinkvote/hard328_sft1_cue_s4-01/rows.jsonl`,
first attempts) and RL plain, 4 samples (`results/day1_3/hard328_rl_plain_s4r2-01/rows.jsonl`, first attempts). Differences are
per problem against the mean of the reference's 4 samples, 95 % bootstrap over problems, 5,000 resamples, seed 0.

| Model | Samples | Right of 328 | Minus Think-SFT, points | Cap hits | Right of finished | Tokens per problem |
|---|---|---|---|---|---|---|
| RL-Math plain | 4 | 200.0 (190 to 209) | | 28.5 | 66.2 % (793 of 1,198) | 9,325 |
| Think-SFT (a = 0) | 4 | 209.0 (201 to 212) | | 94.5 | 88.0 % (822 of 934) | 10,103 |
| Think-SFT + noise of the RL delta's norm | 1 | 209 | 0.0 [-2.7, 2.7] | 97 | 90.0 % (208 of 231) | 10,109 |
| M(1) | 1 | 220 | +3.4 [0.5, 6.2] | 75 | 85.8 % (217 of 253) | 9,667 |
| M(2) | 2 | 231.5 (234, 229) | +6.9 [4.6, 9.3] | 54.0 (51, 57) | 83.8 % (459 of 548) | 9,502 |
| M(3) | 1 | 227 | +5.5 [2.5, 8.5] | 44 | 78.9 % (224 of 284) | 9,709 |
| M(4) | 1 | 213 | +1.2 [-2.0, 4.4] | 33 | 71.5 % (211 of 295) | 10,333 |

- M(2) is above both parents: +6.9 points over Think-SFT and +9.6 [6.9, 12.3] over RL plain, on two seeds (3,000,000 and
  3,100,000; the second sample was pre-registered in amendment 1 with the threshold 222 and scored 229).
- The RL delta acts on Think-SFT as a dial for finishing. Cap hits fall with a at every step (94.5, 75, 54, 44, 33; RL itself
  28.5), and the share of finished answers that are right falls with it (88.0, 85.8, 83.8, 78.9, 71.5 %; RL itself 66.2 %).
  Right answers are the product of the two and peak at a = 2. The model does not break at a = 4: it becomes RL-like.
- The gain is on the problems Think-SFT does not finish. On the 80 problems where Think-SFT hits the cap in at least 3 of its
  4 samples it has 5.25 right per sample; M(1) has 11 and M(2) 16 (first sample). On the 166 problems Think-SFT solves in all
  4 samples M(2) has 166 right and M(1) 162.
- The control rules out "any small perturbation": Gaussian noise per tensor in place of the RL delta leaves right answers
  (209) and cap hits (97) at Think-SFT's values. BF16 rounding inflates this dense noise to 1.40 times the RL delta's norm
  (`delta_sum.json`, `written_norm_over_intended`), so the control is the larger perturbation; its inner product with the RL
  delta is 0.000008 of the delta's squared norm.
- Predictions. H-add (filed in "Difficulty profiles" before the run): hard328 at least 219, held (220); MATH-500 467, held
  exactly (below). The spec's added line "cap hits fall to 70 or fewer at a = 1" is refuted (75); they reach it at a = 2.
  H-inert and H-clash are refuted (interval above 0; 220 is not below 206). The stored-rows ceiling filed on the board before
  the results, 227 for a = 1 (Think-SFT's finished answers plus RL's right answers on its cap-hit problems), was not reached
  at a = 1 and was passed at a = 2. H-dose (amendment 1: a = 3 at least 228) missed by one (227); H-peak is refuted (229).
- Not measured: a = 0.5 (the job stopped logging with one request running, twice, on two boxes; no rows), a second sample of
  a = 1, 3, 4, and the vote over 4 samples (Think-SFT's vote is 241, result-818c20).
- Raw answers read: two M(2) answers right on problems Think-SFT has 0 of 4 on (problems 100 and 110) derive the gold number
  step by step and close the thinking block; `Wait` per 1,000 tokens is 6.7 for M(1) and 6.6 for M(2).

### MATH-500, n = 500, M(1), one sample, seed 182,000,000 (`results/transplant/math500-01/`)

467 of 500, 17 cap hits, 4,771 tokens per problem. Think-SFT cue 454 (25 cap hits, `results/wsp1/full500/sft1_cue-01/`), RL cue
456 to 464 over 4 samples: M(1) minus RL +1.4 points [-0.6, 3.3]. The filed prediction was 467, with 460 or less refuting it.

### hard328, third sample of M(2) and the vote (`results/transplant/hard328-02/`, amendment 2, board work-8b4030)

Seed 3,200,000 (job -082840-a8f8, folder `hard328_s2`): 237 right, 54 cap hits, 9,304 tokens per problem. The three samples of
M(2) are 234, 229, 237: mean 233.3, +7.4 points [5.2, 9.8] over Think-SFT's 209.0 and +10.2 [7.6, 12.7] over RL plain's 200.0;
cap hits 54.0 against 94.5 (-12.3 points [-15.2, -9.6]). Every M(2) sample is above every sample of both parents.

Vote (`day1_vote.vote`) over the 3 samples: 246 of 328. Think-SFT's vote over its 4 samples is 241 and RL's 221. With the same
number of samples, Think-SFT's four votes over 3 are 241, 237, 231, 231: M(2) minus those is +1.5 [-1.5, 4.9], +2.7 [-0.3, 5.8],
+4.6 [1.5, 7.9], +4.6 [1.5, 7.9]. So under the vote the lead shrinks from 7.4 points to between 1.5 and 4.6, and 2 of the 4
comparisons do not separate. The fourth sample (seed 3,300,000) of amendment 2 was not run (account spend limit), so its
prediction "vote over 4 above 241" is not tested as filed; the vote over 3 is already 246.

### fresh2026, n = 136, M(2) with the coefficient fixed: the gain transfers (`results/transplant/fresh2026-02/`, board work-8b4030)

Amendment 2 of the spec, written before the runs. 136 competition problems published in 2026 (`specs/SPEC_fresh.md`), cue,
T 1.0, cap 16,384, `jobs/run_fresh.py`, seeds 7,000,000 + 10,000 s, 4 samples. References: the 4 Think-SFT cue and 4 RL plain
samples of work-7c069c at the same seeds (jobs -024256-58c8, -024347-94e1, -024432-d87b, -024621-af01 and -024606-5843,
-024132-1f6e, -024700-b8c3, -024804-390f; rows in the team store under handoff/fresh/). Vote: `day1_vote.vote` over the 4
samples; it reproduces the posted 75 and 57 of result-5251c9.

| Model | Right of 136, per sample | Mean | Minus Think-SFT, points | Cap hits per sample | Right of finished | Vote over 4 |
|---|---|---|---|---|---|---|
| RL-Math plain | 49, 50, 53, 50 | 50.5 | | 21.0 | 42.8 % (197 of 460) | 57 |
| Think-SFT | 65, 59, 56, 60 | 60.0 | | 62.0 | 80.4 % (238 of 296) | 75 |
| M(2) | 69, 75, 70, 75 | 72.25 | +9.0 [5.3, 12.7] | 45.75 | 78.9 % (285 of 361) | 83 |

- The prediction of amendment 2 holds: M(2) minus Think-SFT is +9.0 points per sample with the interval above 0, on a set
  the coefficient was not chosen on (the 328 gave +6.9). Against RL plain it is +16.0 [11.2, 21.0]. Every M(2) sample is
  above every Think-SFT sample.
- Under the vote over 4 it is 83 against 75 of 136: +5.9 points [1.5, 11.0]; against RL's 57, +19.1 [12.5, 25.7]. 83 is the
  highest count on this set so far.
- As on the 328, the gain is finished answers: cap hits fall by 11.9 points [-16.4, -7.7] while the share of finished
  answers that are right stays near Think-SFT's (78.9 against 80.4 %).
- `results/transplant/fresh2026-01/` is the interim readout on samples 0, 2 and 3 (+8.1 [4.4, 11.8]; vote over 3: 78
  against 74). Sample 1 needed three boxes (one slowed down, one failed with an NVML error, one was stopped with the account
  at 16:15 UTC); its rows are job -082840-a8f8, folder `fresh_s1`.
- Not run: MATH-500 for M(2) (its job was stopped with the account) and the vote over 4 on the 328 (samples 3 and 4).

### hard328, M(2) at cap 32,768, seed 3,010,000: 245 right, 0 cap hits (`results/transplant/cap32_m2_s1-01/`, amendment 4, board work-441e5b)

One sample, Modal H100, 4 shards (jobs abaybektursun-1115-140745-b1e2, -140758-d51e, -140811-353b, -140826-c2f4, commit
ca5adf4; M(2) built in each job by `delta_sum`, effective a 2.0000; smoke -140001-11a6). Readout `analysis/cap32_m2.py`, scored
as `analysis/cap32.py` does (the 16,384 view counts an answer right only if it finished within 16,384 tokens). Reference:
Think-SFT + cue at 32,768, sample 1 of work-dc9359 (jobs -082022-5d48 and -093636-bb67, same per-problem seeds; team store
handoff/cap32vote/). Paired bootstrap over the 328 problems, 10,000 resamples, seed 0.

| Model, seed 3,010,000 | Right at 16,384 view | Right at 32,768 | Cap hits 16,384 / 32,768 | Answers past 16,384: right | Tokens per problem 16,384 view / 32,768 |
|---|---|---|---|---|---|
| Think-SFT + cue | 210 | 234 | 90 / 1 | 90: 24 | 10,043 / 11,512 |
| M(2) | 232 | 245 | 56 / 0 | 56: 13 | 9,348 / 9,875 |

- M(2) minus Think-SFT at 32,768: +3.4 points [-0.6, 7.0] (11 problems); at the 16,384 view +6.7 [3.1, 10.4]. M(2)'s own gain
  from the doubled cap is +4.0 [2.1, 6.1] (13 problems), against Think-SFT's +7.3.
- Amendment 3's filed reading: 245 is in "240+ = the delta adds right answers" (H-more), above Think-SFT's four 32,768
  samples (230, 234, 235, 232). The paired test against the same seed does not separate (interval includes 0), so this one
  sample supports H-more by the filed count but not by the paired test. M(2) also uses 14 % fewer tokens (9,875 against 11,512).
- Amendment 3's own run (seed 3,000,000, vast.ai, work-8b4030) is a second sample. Raw answers: `runs/<job-id>/` in the worktree
  iterate-hack-m2cap of abaybektursun and the Modal Volume iterate-runs (not committed). About 5 USD of Modal H100.

```
uv run tools/gpu.py submit h100 --hours 1.5 -- "bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.delta_sum --host think_sft --donor rl_math --alpha 2.0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label sft1_rl20 --prompt cue --set hard328 --temperature 1.0 --top-p 1.0 --max-tokens 32768 --seed 3010000 --shard <k>/4 --commit <sha>"
python3 -m studies.rlneurons.analysis.shard_join --runs runs/<job k=0..3> --out runs/m2_cap32_s1_joined
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.cap32_m2 --m2 runs/m2_cap32_s1_joined --think runs/think_cap32_s1_joined --out studies/rlneurons/results/transplant/cap32_m2_s1-01 --command '<job command>'
```

### hard328, M(2) at cap 32,768, seed 3,000,000: 241 right, 0 cap hits; restart against a longer cap (`results/transplant/hard328_cap32-01/`, amendment 3, board work-8b4030)

Amendment 3's own run: vast.ai RTX PRO 6000, job abaybektursun-1115-115611-7095, commit 94e5d06, the M(2) written by job
-064729-a4fb (effective a 2.0000). The first attempt (job -110620-f975) was cut by the account stop at 19:50 UTC and is not used.
`python3 -m studies.rlneurons.analysis.transplant_restart hard328_cap32-01 --cap32 runs/abaybektursun-1115-115611-7095/hard328_cap32`.

| M(2), seed 3,000,000 | Right | Cap hits | Tokens per problem |
|---|---|---|---|
| Counted at 16,384 | 229 | 57 | 9,299 |
| At 32,768 | 241 | 0 | 9,827 |

- Filed in amendment 3: 225 to 235 = the delta only saves tokens, 240 or more = it adds right answers. Both samples are in
  "240 or more": 241 here and 245 at seed 3,010,000 (section above), mean 243.0, against Think-SFT's four samples at 32,768 of
  230, 234, 235, 232 (mean 232.75; the 230 is this seed). Every M(2) sample is above every Think-SFT sample, by 10 problems on
  average, with 15 % fewer tokens (9,851 against about 11,650). The per-problem test of this seed against Think-SFT is not made
  here: Think-SFT's 32,768 rows are not on main.
- 57 answers pass 16,384 tokens, all finish, 12 are right (21 %; Think-SFT 23 of 91 at this seed in result-c8b994).
- Restart or continue (chains over the stored 16,384 samples, every assignment of distinct samples; `readout.json`, `chains`):

| What is done after a cap hit | Right of 328 | Cap hits left | Tokens per problem |
|---|---|---|---|
| M(2), nothing | 233.3 | 54.0 | 9,436 |
| M(2), continue to 32,768 (2 runs) | 243.0 | 0 | 9,851 |
| M(2), one new M(2) sample | 240.5 (238 to 244) | 29.7 | 11,966 |
| M(2), up to two new M(2) samples | 242.8 (240 to 246) | 21.0 | 13,395 |
| M(2), then M(4) | 237.0 | 15.7 | 11,827 |
| M(2), then M(3), then M(4) | 238.7 | 7.7 | 12,917 |
| M(2), then RL plain | 235.4 | 13.1 | 11,750 |
| Think-SFT, nothing | 209.0 | 94.5 | 10,103 |
| Think-SFT, one new Think-SFT sample | 222.0 | 68.8 | 14,559 |
| Think-SFT, then M(2) | 233.6 | 43.2 | 14,328 |

  Continuing the cut answer is the cheapest: 243 at 9,851 tokens, against 240.5 at 11,966 for a new sample. Passing a cut
  problem to a model with more of the RL delta (M(3), M(4), RL), which finishes more often, gives fewer right answers than a
  new sample of M(2) itself at the same tokens: finishing more often does not pay for the lower share of right answers.
  The chains were computed after the rows were seen (no prediction filed); M(3) and M(4) have one stored sample each.

### Another host: the released final Think model + 2 (RL-Math - base) (`results/transplant/host_think-01/`, amendment 5, board work-989736)

Host `allenai/Olmo-3-7B-Think` (revision d97e442; Think-SFT after DPO and RLVR, so a host already trained with reward; not run
here before). H(a) = host + a (RL-Math - base) by `delta_sum --host allenai/Olmo-3-7B-Think@<revision>`; a = 0 writes the host
through the same path (written norm 0, checked). hard328, cue, T 1.0, cap 16,384, v3, one sample each, seed 3,000,000, vast.ai
RTX PRO 6000 (jobs abaybektursun-1115-140453-8369 for H(0), -135625-8909 for H(2), commit b4a9014, branch egate-fresh).
||host - base|| = 467.4 and its cosine with the RL delta is -0.002, the values of Think-SFT to 4 digits.

| Model, seed 3,000,000 | Right of 328 | Cap hits | Right of finished | Tokens per problem |
|---|---|---|---|---|
| Think-SFT (this seed; 4-sample mean 209.0, 94.5) | 212 | 89 | | |
| Final Think, H(0) | 213 | 113 | 94.9 % (204 of 215) | 10,984 |
| Final Think + 2 x RL delta, H(2) | 224 | 88 | 90.0 % (216 of 240) | 10,908 |
| Think-SFT + 2 x RL delta, M(2) (this seed) | 234 | 51 | | 9,505 |

- H(2) minus H(0): +3.4 points [-0.6, 7.3] (11 problems), cap hits -7.6 points [-11.9, -3.4] (25 fewer). By the filed
  terms this is undecided for right answers: the point estimate passes +3, the interval includes 0, and cap hits fall by
  22 %, under the filed third. The delta makes this host finish more often, as it did Think-SFT, and by less: on Think-SFT
  the same coefficient gave +7.4 points and 40 fewer cap hits.
- H-absorbed is refuted in its first clause: the final Think model does not finish more often than Think-SFT. It has 113 cap
  hits against Think-SFT's 94.5 (+5.6 points [2.1, 9.2]) and 213 right against 209.0 (+1.2 [-2.2, 4.6]): DPO and RLVR did
  not make it better on the 328 at this cap. H-clash is refuted (H(2) is not below H(0)).
- Where the 11 come from: on the 113 problems the host cuts, H(2) has 31 right against the host's 9 (cut answers that already
  held the answer); on the 215 the host finishes, H(2) has 193 against 204, and 13 of those 215 are now cut. The delta moves
  answers across the cap in both directions on this host.
- One sample against one sample. A second seed of both was filed only for the case H-adds and was not run.

### The Think lineage's reward step against the RL-Zero delta: nearly orthogonal (`results/transplant/align_think-01/`, amendment 6, board work-001ff1)

`jobs/delta_align.py --a allenai/Olmo-3-7B-Think@d97e442... --a0 think_sft --b rl_math --b0 base`, weights only, AWS L40S, job
ih-1116-005552-daed, commit def2511. D_T = final Think - Think-SFT (DPO and RLVR); D_R = RL-Math - base.

| | Value |
|---|---|
| Norm of D_T, of D_R (Think-SFT - base: 467.45) | 2.81, 4.12 |
| Cosine of D_T with D_R, all tensors | +0.0038 |
| Cosine per matrix (226 matrices): median, range, number above 0 | +0.0028, -0.011 to +0.021, 203 |
| Share of D_T's squared norm inside D_R's top-8 directions, median | 0.030 % (93 times the 64 / (rows x columns) of a random matrix) |
| Share of each change in its own top-8 directions, median | D_T 9.8 %, D_R 9.4 % |
| Cosine of D_T with Think-SFT - base | -0.0020 |

- Filed H-opposite (cosine below -0.02) is refuted: the reward step that leaves the Think model with more cap hits is not the
  RL-Zero delta with the sign turned. H-same-sign (above +0.02) is refuted too. The cosine is inside H-unrelated's band
  (under 0.01); that hypothesis's second clause (share within 3 times chance) fails by its letter at 93 times, but the share
  itself is 0.03 % of D_T, so the two changes are orthogonal to 3 decimal places in every matrix type.
- A small common part exists: the per-matrix cosine is above 0 in 203 of 226 matrices. It is 0.0014 % of the squared norms.
- Read with amendment 5: the two reward trainings have opposite effects on cap hits (Think +18.5 over Think-SFT, RL delta
  -25 on the Think host) through different directions of weight space, and they add when summed (H(2) keeps most of
  both). The "noise per matrix" value to compare the cosine with was not measured; the control would be another fine-tune's
  difference (RL-Code - base, Think-SFT step branches).

Run folders hold `readout.json`, `metrics.json` and `delta_sum.json` (per arm), `rows.jsonl` (arms and references, per answer)
and `examples.json` (one right and one wrong finished answer per arm, with the prompt). Jobs: hard328 a = 1 -000934-51f9,
a = 2 -000954-b526 and -020508-879c, a = 3 -020435-c76d, a = 4 -020500-36ed, control -020021-e9d1; MATH-500 -004808-bb28 (all
abaybektursun-1115-). Raw answers: `runs/<job-id>/answers.jsonl` on the laptop of abaybektursun, worktree iterate-hack-egate
(not committed; the boxes are destroyed). About 29 USD of vast.ai rent.

```
python3 tools/vast.py run <box> -- 'PIP_BREAK_SYSTEM_PACKAGES=1 bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.delta_sum --host think_sft --donor rl_math --alpha 2.0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label sft1_rl20 --prompt cue --set hard328 --temperature 1.0 --top-p 1.0 --seed 3000000 --samples 1 --restarts 0 --commit <sha>'
uv run --with numpy python -m studies.rlneurons.analysis.transplant hard328-01 --arm sft1_rl20=runs/<job>,runs/<job> [--arm ...] --ref think=studies/rlneurons/results/thinkvote/hard328_sft1_cue_s4-01/rows.jsonl --ref rl=studies/rlneurons/results/day1_3/hard328_rl_plain_s4r2-01/rows.jsonl
```

## Token cap 32,768 on the 328: Think-SFT gains 23 problems, the base 4, RL 2 (board work-ceccc0)

Spec `specs/SPEC_cap32.md` (written before the runs). `run_cell --set hard328 --max-tokens 32768`, T 1.0 / top-p 1.0, grader
v3, one sample, seed 3000000, on vast.ai (RTX PRO 6000). Each cell is scored twice from the same answers: right at 32,768, and
right with at most 16,384 generated tokens, so the gain is paired inside one run. Readout `analysis/cap32.py`,
`results/cap32/readout.json`.

Per-problem rows of both cells (tokens generated, cut off at 32,768 or not, score, extracted answer, last 400 characters): `results/cap32/rows-01/` (`sft_cue.jsonl`, `rl_plain.jsonl`, `run.json`), written by `analysis/cap32_rows.py` from `runs/<job>/answers.jsonl`; its totals are checked against `results/cap32/readout.json` (230 and 207, 195 and 193). The base cue cell's rows in the same format are in `results/cap32/rows-02/` (`base_cue.jsonl`, `run.json`), written by the one-off command recorded in its `run.json` from `runs/cap32_base_cue_joined/answers.jsonl` (the 4 shards joined) and checked against the readout (156 and 152, 64 past 16,384 with 4 right).

| cell | right at 16,384 (same answers) | right at 32,768 | gain, points [95 %] | answers past 16,384: finished / right | tokens per problem, 16,384 / 32,768 |
|---|---|---|---|---|---|
| Think-SFT cue (`results/cap32/sft_cue-01/`) | 207 | 230 | +7.0 [4.3, 9.8] | 93: 91 / 23 | 10,048 / 11,795 |
| RL plain (`results/cap32/rl_plain-01/`) | 193 | 195 | +0.6 [0.0, 1.5] | 20: 20 / 2 | 9,293 / 9,421 |
| base cue (`results/cap32/base_cue-01/`, 4 shards on AWS L40S) | 152 | 156 | +1.2 [0.3, 2.4] | 64: 63 / 4 | 9,145 / 9,995 |

- H1 held: Think-SFT's cut answers are unfinished work. 91 of 93 finish inside the second 16,384 tokens and 23 are right, for
  1,747 more tokens per problem. 230 of 328 is the best single-sample row on the 328 so far (vote over 4 Think-SFT samples at
  16,384: 241 at 40,410 tokens).
- H3 held: RL gains 2.
- Instrument: the 16,384 scores of these runs are 207 (stored cells 212, 219) and 193 (stored 206). 193 is 13 below 206, one
  outside the spec's limit of 12, and inside the range of RL's four stored samples on the 328 (207, 190, 209, 194,
  `results/day1_3/hard328_rl_plain_s4r2-01/`). Not rerun; the gain is measured inside the run.
- Of the 68 long Think-SFT answers that finish wrong, none is a loop by the runner's loop count (3 in the whole cell).
- H2 held: the base's long answers also finish with more tokens (63 of 64) but only 4 are right. Share right among answers past
  16,384: Think-SFT 23 of 93, RL 2 of 20, base 4 of 64. The base's 16,384 score in this run is 152 (stored 164, limit 12: inside).
  Base jobs ih-1115-144232-448b, -144318-6d57, -144428-85af, -144457-42b8, joined with `analysis/shard_join.py`.
- Jobs abaybektursun-1115-005756-309b (Think-SFT), -005823-8ac9 (RL); raw answers in `runs/<job>/` on the laptop, not in git.

## Fresh held-out set: Think-SFT's lead over RL holds on problems published in 2026 (fresh2026, n = 136, 4 samples, board work-7c069c, idea-67db73)

Question: Think-SFT + cue beats RL under the vote on the 328 (241 against 221), but its training data could hold those
problems in a form an overlap scan cannot match. Does the lead hold on competition problems published after the weights of all
three models existed? Answer: yes, and it is larger. Vote over 4 on 136 problems from AIME 2026, HMMT February 2026 and HMMT
November 2026: Think-SFT + cue 75 of 136 (55.1 %), RL plain 57 (41.9 %), base + cue 38 (27.9 %). Think-SFT minus RL +13.2
points [+7.4, +19.1], paired bootstrap; one sample (mean of 4) 60.0 against 50.5 against 29.5, +7.0 points [+3.1, +11.0]. Spec
and predictions, filed before any model saw the set: `specs/SPEC_fresh.md` (commit `1232554`; refuting observations of P1 to P3
added in `a29e390` before any full-run row was read). T 1.0 / top-p 1.0, cap 16,384, grader v3, no restarts, prompt `pair1`.

What "fresh" guarantees. Every problem was first set at a contest held between 2026-02-05 and 2026-11-07. The last weights
(RL-Zero-Math) were uploaded 2025-12-12, Think-SFT's on 2025-10-14 and its training data on 2025-10-16, the base's on
2025-10-09; the model cards state "Date cutoff: Dec 2024" (base), "Dec. 2024." (Think-SFT) and "Dec. 2023." (RL), and the
Olmo 3 paper (2512.13961, section 3) "a cutoff date of December 31, 2024" for the crawl. The Dolci dataset cards state no
cutoff, so the bound is the upload dates. The contest papers, their solutions and discussions of them therefore cannot be in
any training data. Not guaranteed: that a contest did not reuse an older problem. One was found and dropped (AIME 2026 I #1 is
the 2020 Purple Comet Middle School #8, an exact match in the RL training prompts). Both training sets were then scanned for
the 136: 0 exact, 0 near in the 13,314 RL prompts (`results/fresh/overlap-01/overlap.json`, largest 8-gram share 0.375) and 0
in every message of the 2,268,178 Think-SFT rows (`results/fresh/sft_overlap-01/`, largest share 0.429; the controls hard/0
and hard/38, known to be in that data, were flagged exact).

The set: `data/fresh/fresh2026_v1.json` (sha256 `dcf571ea8a4654228e17975e8c1e255e50072f74061c9b083f5aad5c21d8e7d7`, built by
`prep/fresh_prep.py`, counts in `fresh2026_v1_meta.json`). 165 candidates: `MathArena/aime_2026` @ `d61f486` (30),
`MathArena/hmmt_feb_2026` @ `589a53f` (33), and the official HMMT solutions PDFs of the February Guts round (36) and of
November 2026 General, Theme, Team and Guts (66), transcribed by Claude subagents into `data/fresh/transcribed_v1/` (urls and
sha256 of the PDFs in `sources.json`). Dropped by rules written before any model output: 1 published before 2026, 20 that need
a figure, 7 estimation problems, 1 with a tuple answer; 0 by the grader check (every gold grades right against itself and
wrong against gold + 1 and against another problem's gold). Kept: AIME 27, HMMT Feb 32 + Guts 28, HMMT Nov 49. Caveats: the
77 PDF problems were transcribed by a language model (the answer keys were checked against the official ones by the main
session; three statements on which all models agree on one wrong answer were compared with the PDF text here and are
verbatim); `aime2026/25` has MathArena's wording (the sum of all possible BC, gold 850), not the contest paper's; for
`hmmt_feb2026/9` (gold `50(1 - \frac{1}{2^{101} - 1})`) grader v3 takes 50.0 but not 50: no sample of any model answers 50 or
the gold (4 cap hits for Think-SFT, RL 100, 100 and two other expressions, base 3 cap hits and 101/2), so the counts are the
same without it (75, 57, 38 of 135; +13.3 points [+6.7, +20.0]).

| fresh2026, n = 136 | Think-SFT + cue | RL plain | base + cue |
|---|---|---|---|
| one sample: the 4 samples; mean | 65, 59, 56, 60; 60.0 | 49, 50, 53, 50; 50.5 | 28, 28, 32, 30; 29.5 |
| vote over 4 | 75 | 57 | 38 |
| any of 4 right (pass@4) | 77 | 68 | 48 |
| sequential vote, at most 3 (`seq3`): right, right (24), tokens | 71, 72.5, 34,718 | 56, 54.9, 32,394 | 34, 36.2, 36,313 |
| sequential vote, at most 4 (`seq4_restart`, no restarts run): right, right (24), tokens | 75, 75.5, 42,251 | 57, 55.8, 37,443 | 38, 38.8, 46,047 |
| cap hits, share of the 544 samples | 45.6 % | 15.4 % | 40.3 % |
| precision of finished answers | 80.4 % (238 of 296) | 42.8 % (197 of 460) | 36.0 % (117 of 325) |
| generated tokens per sample; per problem for the vote | 13,043; 52,170 | 12,083; 48,331 | 12,790; 51,158 |

Differences, points, paired bootstrap over problems (`results/fresh/readout-01/readout.md` has every group):

| | vote over 4 | one sample |
|---|---|---|
| Think-SFT minus RL, all 136 | +13.2 [+7.4, +19.1] | +7.0 [+3.1, +11.0] |
| Think-SFT minus RL, Hugging Face subset (AIME + HMMT Feb, 59): 29 against 22 | +11.9 [+3.4, +22.0] | +8.5 [+1.7, +15.7] |
| Think-SFT minus RL, transcribed subset (77): 46 against 35 | +14.3 [+6.5, +23.4] | +5.8 [+1.3, +10.7] |
| Think-SFT minus RL, HMMT November 2026 only (49, eight days old at the run): 30 against 23 | +14.3 [+6.1, +24.5] | +6.1 [+1.0, +11.7] |
| Think-SFT minus base, all | +27.2 [+19.9, +35.3] | +22.4 [+17.5, +27.8] |
| RL minus base, all (the control: the instrument separates the models as on the 328) | +14.0 [+8.1, +19.9] | +15.4 [+11.4, +19.9] |

Hypotheses and predictions scored (`results/fresh/readout-01/readout.json`, `predictions`):

- H1 (Think-SFT's vote beats RL's by at least 2 points; refuted if the interval is at or below 0): held, +13.2 [+7.4, +19.1].
- H2 (Think-SFT abstains more and is more precise, each by at least 10 points): held, cap hits +30.1 points [+24.1, +36.6],
  precision +37.6 [+30.9, +44.0].
- H3 (base + cue below RL): held, 38 against 57 under the vote, 29.5 against 50.5 in one sample.
- The 12 table predictions (vote, single, cap hits, precision for three models): all inside their intervals. Vote 74 / 64 / 49
  predicted, 75 / 57 / 38 observed; single 59 / 54 / 36 against 60.0 / 50.5 / 29.5; cap hits 40 / 14 / 33 % against 45.6 /
  15.4 / 40.3; precision 80 / 50 / 42 % against 80.4 / 42.8 / 36.0. Think-SFT was predicted within 1 problem; RL and the base
  came out 7 and 11 problems lower than predicted. Tokens per sample 12,000 / 11,000 / 11,000 against 13,043 / 12,083 / 12,790.
- P1 (difference +7 points, refuted above +12): refuted, +13.2; the interval half-width (5.9 points) was as stated.
- P2 (Hugging Face subset 26 / 20 / 14): held, 29 / 22 / 13.
- P3 (the models are closest on HMMT November, 35 / 33 / 27): refuted. 30 / 23 / 17, and the difference there (+14.3 points)
  is not smaller than on the other 87 problems (+12.6). HMMT November was not the easier part for these models.

What the raw rows show (all 1,632 extracted answers read beside the golds; texts of right, wrong and cap-hit rows read):

- The mechanism of the 328 repeats. Think-SFT hits the cap on 248 of 544 samples and is right in 80 % of the answers it
  finishes; RL finishes 460 and is right in 43 %. A cap hit casts no vote, so Think-SFT's vote is almost its pass@4 (75 of
  77); RL's vote loses 11 of its 68 problems with a right sample to its own wrong finished answers (`aime2026/4`: 65, 71, 70,
  65 against gold 70). Vote right for one model only: Think-SFT 20, RL 2 (`aime2026/18`: four Think-SFT cap hits).
- RL answers with a confident wrong value where Think-SFT is right (`hmmt_feb2026/12`: 875/128 four times against RL's 10
  four times; `hmmt_feb2026_guts/15` and `hmmt_nov2026_guts/25`: Think-SFT right twice and two cap hits, RL four wrong answers).
- 66 of Think-SFT's 248 cap hits hold more than 20 Chinese characters (RL 3 of 84, base 0 of 219), as on the 328.
- The grader takes equivalent forms: `\sqrt{14 + 3\sqrt{19}}` for `\frac{\sqrt{38}+3\sqrt{2}}{2}`, `\frac{2027! - 2026!}{2}`
  for `1013 \cdot 2026!`, `0.87` for `\frac{87}{100}` (checked by hand). No finished answer equal to its
  gold and scored wrong was seen in the table of extracted answers.
- Problems where all three models agree on one wrong answer (`aime2026/30`: 243 for 393; `hmmt_feb2026_guts/21`: 34 for 102;
  `hmmt_nov2026_team/4`: 2025 for 64) are verbatim statements with the official answers.

Jobs. Smoke: Modal `abaybektursun-1115-042802-2fae` (base + cue, first 10 problems: 3 right, 3 cap hits; rows read). The 12
cells ran from the main session on vast.ai, one RTX PRO 6000 96 GB per job, commit `94d9863`, commands in
`specs/fresh_jobs.txt`, 12.1 GPU-hours of job time (450 to 545 tokens/s): Think-SFT `abaybektursun-1115-024256-58c8`,
`-024347-94e1`, `-024432-d87b`, `-024621-af01`; RL `-024606-5843`, `-024132-1f6e`, `-024700-b8c3`, `-024804-390f`; base
`-040403-80d7`, `-024927-4a44`, `-025027-51c8`, `-025153-2e87` (samples 0 to 3, seeds 7000000 + 10000 s; arm and seed read
from each job's `metrics.json`, each done with 136 rows). Raw answers: `s3://iterate-hack-team-769063704696/handoff/fresh/<job>/`.
Run folders `results/fresh/{sft1_cue,rl_plain,base_cue}_s4-01/` (`run.json`, `metrics.json`, `readout.json`, `rows.jsonl`,
`examples.json`), `frontier_sft_rl-01/` (the `--base` slot holds Think-SFT; labels in `frontier.md` edited, numbers
untouched), `frontier_base_rl-01/`, `readout-01/`. `jobs/run_fresh.py` is `run_cell` with `--set fresh2026` registered.

```
uv run --no-project --with numpy --with math-verify==0.9.0 --with pyarrow --with huggingface_hub python -m studies.rlneurons.prep.fresh_prep
uv run --no-project --with pyarrow python -I studies/rlneurons/analysis/rln3_overlap.py <dir with train.parquet, math500.json, the fresh set as hard.json> <out.json>
PYTHONPATH=. uv run --no-project --with huggingface_hub --with pyarrow --with numpy python -m studies.rlneurons.analysis.fresh_sft_overlap --tmp <dir> --out studies/rlneurons/results/fresh/sft_overlap-01
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.thinkvote_join --runs runs/fresh_handoff/<s0> <s1> <s2> <s3> --out runs/fresh_<arm>_s4
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_vote --run runs/fresh_<arm>_s4 --out studies/rlneurons/results/fresh/<arm>_s4-01 [--minus <readout.json>]
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.frontier --base studies/rlneurons/results/fresh/sft1_cue_s4-01 --rl studies/rlneurons/results/fresh/rl_plain_s4-01 --fixed studies/rlneurons/results/frontier/math500-01/chosen.json --out studies/rlneurons/results/fresh/frontier_sft_rl-01
uv run --no-project --with numpy python -m studies.rlneurons.analysis.fresh_read --sft studies/rlneurons/results/fresh/sft1_cue_s4-01 --rl studies/rlneurons/results/fresh/rl_plain_s4-01 --base studies/rlneurons/results/fresh/base_cue_s4-01 --out studies/rlneurons/results/fresh/readout-01 --texts runs/fresh_sft1_cue_s4 runs/fresh_rl_plain_s4 runs/fresh_base_cue_s4
```

## Paper: The First Hundred Steps (`paper-first-steps/`, board work-184476)

A 4-page paper: `paper-first-steps/the-first-hundred-steps.pdf`, served at
https://monitor.invariant.team/paper/the-first-hundred-steps.pdf. Claim: on MATH-500 (n = 500, T 1.0 / top-p 1.0, cap
16,384, grader v3, four samples per model) the three-token opening cue takes the base from 224 to 410.5 right, within
+1.4 points [-0.45, 3.30] of the released RL step 100 (417.5); steps 100 to 2,800 add 42.5 problems (final 460.0), almost
all on problems the cued base already solves in some samples (47 gained, 44 of them solved by the cued base at least once).

| File | What it is |
|---|---|
| `paper-first-steps/build_facts.py` | Reads the committed rows (`results/ckptcue/`, `results/selfopen/`, `results/wsp2/`, `results/handoff/`) and writes `facts.json` and `problems.jsonl`. No GPU. Run: `python studies/rlneurons/paper-first-steps/build_facts.py`. |
| `paper-first-steps/facts.json` | Every number in the paper, with the path of the rows it came from (`_about.sources`). |
| `paper-first-steps/problems.jsonl` | One line per MATH-500 problem: right counts per model over the four samples. |
| `paper-first-steps/NOTES.md` | Definitions, the arms and their prompts, what each number does not show. |
| `paper-first-steps/figs.py`, `fig_curve.pdf` | The figure, drawn from `facts.json`. Run: `python studies/rlneurons/paper-first-steps/figs.py`. |
| `paper-first-steps/paper.tex`, `refs.bib`, `fonts/` | Source; build with `tectonic paper.tex` in the folder. |

## Paper: No Early Warning (`paper-no-warning/`, board work-184476)

A 4-page paper: `paper-no-warning/no-early-warning.pdf`, served at https://monitor.invariant.team/paper/no-early-warning.pdf.
Claim (MATH-500, n = 500, base + cue, 4 samples, T 1.0 / top-p 1.0, cap 16,384, grader v3; 150 problems with both
outcomes, 478 pairs): a perfect critic at token 1,000 would lift the base from 410.5 to at most 459.2 [447.9, 469.9]
at 4,013 tokens per problem (RL 460.0), but within a problem the best probe cell scores AUROC 0.571 [0.509, 0.634]
(340 pairs) and its restart policy gains 0.8 points [-0.7, 2.4] over random stopping. Length carries the signal later:
which attempts have ended scores 0.572 [0.523, 0.619] at token 4,000, final length 0.680 [0.620, 0.738], agreement with
the other three samples 0.893 [0.855, 0.929]. Restarting any attempt still running at token 4,000 gains 1.15 points
[0.60, 1.73] at 4,886 tokens. The within-problem control is published (Bulut, arXiv 2609.03436, to 512 tokens).

| File | What it is |
|---|---|
| `paper-no-warning/build_facts.py` | Recomputes length, agreement, text signs, ceilings and replays from the committed rows (`results/day1_3/`), copies the probe numbers from `results/critic/probe-02/metrics.json`, checks 64 values against stored readouts, writes `facts.json` and `examples.json`. Run: `uv run --no-project --with numpy --with math-verify==0.9.0 python studies/rlneurons/paper-no-warning/build_facts.py`. |
| `paper-no-warning/facts.json`, `examples.json` | Every number in the paper with its source; one problem with a right and a wrong sample. |
| `paper-no-warning/NOTES.md` | Definitions, arms, caveats, what could not be recomputed. |
| `paper-no-warning/figs.py`, `fig_warning.pdf` | The figure, drawn from `facts.json`. |
| `paper-no-warning/paper.tex`, `refs.bib`, `fonts/` | Source; build with `tectonic paper.tex` in the folder. |

## Think-SFT in its own chat format ties the raw template with the cue (hard328, board work-8b2ec9)

Spec `specs/SPEC_native.md` (written before the runs). Every other Think-SFT row prompts the model with the study's raw
template and the base's three-token cue. Here the same user text goes through the model's own chat template (system line,
`<|im_start|>` markers, answer opened with `<think>`): `run_cell --prompt native --native-tokenizer
allenai/Olmo-3-7B-Think-SFT@6ff857587e040d6d523a3d5f3a56e918f5401d66`. T 1.0 / top-p 1.0, grader v3, one sample, seed 3000000,
cap 32,768, scored also at 16,384 from the same answers; paired by problem with the cue cell of `results/cap32/`. Readout
`analysis/native.py`, `results/native/hard328-01/readout.json`.

| cap | own chat format | raw template + cue | difference, points [95 %] | only own format / only cue | tokens per problem |
|---|---|---|---|---|---|
| 32,768 | 232 | 230 | +0.6 [-3.4, 4.6] | 23 / 21 | 12,158 / 11,795 |
| 16,384 (same answers) | 204 | 207 | -0.9 [-4.3, 2.4] | 15 / 18 | 10,170 / 10,048 |

- Neither H1 (own format at least 10 problems better) nor H2 (cue at least 10 better) holds: the formats tie. The cue on a raw
  prompt brings out all of what Think-SFT's own format gives on the 328, so the Think-SFT rows of this study are not held back
  by the prompt, and the cue is not what puts Think-SFT above RL.
- The larger cap helps both formats alike: own format 204 to 232 (104 answers past 16,384, 3 cap hits at 32,768).
- MATH-500 (`analysis/native_math500.py`, `results/native/math500-01/readout.json`, seed 182000000, n 500): own format 464 at
  16,384 and 474 at 32,768 (25 answers past 16,384, 0 cap hits, 5,154 tokens per problem). The four stored cue samples at
  16,384 score 461, 457, 462, 461 (`results/thinkvote/math500_sft1_cue_s4-01/`): own format minus cue +0.4 to +1.4 points,
  every interval includes 0. A tie at the same cap here too; 474 is above every single-sample MATH-500 row of RL (456 to 460).
  Jobs ih-1115-174427-f4d9, ih-1115-183414-a2cc.
- Instrument: 325 of 328 answers close the thinking part with `</think>`; all finished answers end at the stop id, none at
  `<|im_end|>`. Smoke job ih-1115-161250-2a8e (8 MATH-500 problems, 7 right).
- Jobs ih-1115-163313-7486 and ih-1115-163401-a4ba (AWS L40S, 2 shards, joined with `analysis/shard_join.py`); raw answers in
  `runs/` on the laptop and in S3 under results/ih/<job>/, not in git.

## Paper: Two Token Limits (`paper-two-caps/`, board work-184476)

A 4-page paper: `paper-two-caps/two-token-limits.pdf`, served at https://monitor.invariant.team/paper/two-token-limits.pdf.
Claim (hard328, n = 328, T 1.0 / top-p 1.0, grader v3, one sample per model, the same answers scored at a limit of 16,384
and of 32,768 tokens): RL - base + cue +12.5 -> +11.9 points (change -0.6 [-2.1, 0.9]); Think-SFT + cue - RL +4.3 -> +10.7
(change +6.4 [3.7, 9.5]); M(2) - Think-SFT +6.7 -> +3.4 [-0.6, 7.0] (change -3.4 [-6.4, -0.3]; [-7.3, 0.3] at 98.33 %,
suggestive only). Answers longer than 16,384 tokens that end right: Think-SFT 23 of 93, M(2) 13 of 56, base 4 of 64,
RL 2 of 20. No ordering of the models changes.

| File | What it is |
|---|---|
| `paper-two-caps/build_facts.py` | Recomputes every comparison from the committed rows (`results/cap32/`, `results/transplant/`, `results/thinkvote/`, `results/day1_3/`, `results/fresh/`), copies the own-chat-format numbers from `results/native/`, checks 153 values against stored readouts, writes `facts.json` and `examples.json`. Run: `uv run --no-project --with numpy python studies/rlneurons/paper-two-caps/build_facts.py`. |
| `paper-two-caps/facts.json`, `examples.json` | Every number in the paper with its source (`review`: the numbers the reviews asked for); one problem Think-SFT gets right only past 16,384 tokens. |
| `paper-two-caps/NOTES.md` | Definitions, arms, caveats, what is pending. |
| `paper-two-caps/figs.py`, `fig_caps.pdf` | The figure, drawn from `facts.json`. |
| `paper-two-caps/paper.tex`, `refs.bib`, `fonts/` | Source; build with `tectonic paper.tex` in the folder. |

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

### Prefix hand-off

```
uv run --no-project --with numpy --with math-verify==0.9.0 --with transformers==5.19.0 --with tokenizers==0.23.3 --with huggingface_hub --with jinja2 python -m studies.rlneurons.analysis.handoff_test --runs runs
uv run tools/gpu.py submit h100 --hours 4 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.handoff_gen --finisher base --cuts 25,50,75 --commit $(git rev-parse HEAD)"
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.handoff --run base=runs/<job> --run rl=runs/<job> --out studies/rlneurons/results/handoff --nn <nn>
```

The test and `prep/handoff_plan.py` read the writers' `answers.jsonl` from `runs/<writer job>/` (`uv run tools/gpu.py get`); the
job reads them from `/runs/` in the Volume. `--finisher rl` for the second job; `--n 10 --cuts 0,25,50,75,100` for the smoke.

### Relay on hard328

```
uv run --no-project --with numpy --with math-verify==0.9.0 --with transformers==5.19.0 --with tokenizers==0.23.3 --with huggingface_hub --with jinja2 python -m studies.rlneurons.analysis.handoff_test --runs runs --plan plan_v2.json
uv run tools/gpu.py submit h100 --hours 3 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.handoff_gen --finisher rl --plan plan_v2.json --cuts 25 --commit $(git rev-parse HEAD)"
uv run tools/gpu.py submit h100 --hours 3 -- "bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe interp --other think_sft --alpha 1.0 --rounding nearest --seed 0 --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.handoff_gen --finisher think --finisher-path /tmp/theta --plan plan_v2.json --cuts 25 --commit $(git rev-parse HEAD)"
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.relay --run runs/<job> --run runs/<job> --run runs/<job> --run runs/<job> --out studies/rlneurons/results/relay --nn <nn>
```

One job per finisher and cut (`--cuts 50` for the other two); `--n 10 --cuts 0,25,50,100` for the smoke.

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

## The 328 with four samples and restarts: both models under the MATH-500 procedure (hard328, n = 328, T 1.0 / top-p 1.0, grader v3, board work-1a972a)

Question (`specs/DAY1_hard328_vote_2026-11-14.md`, written before launch): what do both models score on the 328 with the
procedure fixed on MATH-500 (four samples, each sampled again up to twice after a cap hit, plurality vote)? Answer: base +
cue 195 of 328 (59.5 %), RL plain 224 of 328 (68.3 %); RL minus base 8.8 points [5.5, 12.5]. The vote narrows the gap from
14.0 points [9.5, 18.9] on one sample; it does not close it. Nothing was chosen on the 328.

Jobs `abaybektursun-1114-200457-e8e6` (base, 18.1 M generated tokens, 1,731 rows) and `-200505-5ff2` (RL, 14.5 M, 1,466 rows),
`jobs/run_cell.py --set hard328 --samples 4 --restarts 2 --temperature 1.0 --top-p 1.0 --seed 3000000`. Raw answers: Volume
`iterate-runs`, `<job id>/answers.jsonl`. Readout `analysis/day1_vote.py` (RL with `--minus` the base readout; paired
bootstrap, 5,000 resamples, seed 0). Tokens = generated tokens per problem, restarts included.

| Row | base + cue: right, percent | tokens | RL plain: right, percent | tokens | RL minus base, points [95 %] |
|---|---|---|---|---|---|
| single (sample 0, attempt 0) | 161, 49.1 | 9,074 | 207, 63.1 | 9,437 | +14.0 [9.5, 18.9] |
| restart after a cap hit | 172, 52.4 | 13,665 | 213, 64.9 | 11,484 | +12.5 [7.9, 17.4] |
| vote over 4 | 192, 58.5 | 36,902 | 221, 67.4 | 37,299 | +8.8 [5.2, 12.8] |
| vote over 4 after restart | 195, 59.5 | 55,306 | 224, 68.3 | 44,108 | +8.8 [5.5, 12.5] |
| pass@4 (oracle, not a method) | 207, 63.1 | 36,902 | 240, 73.2 | 37,299 | +10.1 [6.4, 14.0] |
| pass@4 after restart (oracle) | 219, 66.8 | 55,306 | 243, 74.1 | 44,108 | +7.3 [4.0, 11.0] |
| Run folder | `results/day1_3/hard328_base_cue_s4r2-01/` | | `results/day1_3/hard328_rl_plain_s4r2-01/` | | |

- Instrument check: sample 0, attempt 0 repeats Day-1 #1 on its seeds: base 161 against 164, RL 207 against 206 (rule:
  within 10). Each sample alone: base 161, 161, 152, 160 (cap hits 71, 66, 81, 68); RL 207, 190, 209, 194 (35, 26, 24, 29).
  One-sample cells on this set differ by up to 9 (base) and 19 (RL) problems between seeds.
- Prediction 1 (RL vote over 4 = 215, range 205 to 225): holds, 221.
- Prediction 2 (base vote over 4 = 184, range 174 to 194): holds, 192.
- Prediction 3 (restarts add at least 2.0 points to the base's vote): refuted, +0.9 (195 against 192). Restarts add 3.4
  points [1.5, 5.5] to one sample but the vote already absorbs most cap hits; they cost 50 % more tokens.
- Prediction 4 (RL ahead by 5 to 12 points under vote after restart, interval above 0): holds, 8.8 [5.5, 12.5].
- Prediction 5 (`tie_short` beats the plain vote by at least 1.0 point on the base): refuted, 191 against 192, -0.3
  [-2.1, +1.5] (`results/selector/hard328_base_cue-01/`, `analysis/selector.py`). The 453 of 500 of `tie_short` on MATH-500
  was chosen on those problems; the plain vote's 446 (450 after restart) is the number to quote there.
- Prediction 6 (stop when two agree is within 1.5 points of the vote and saves at least 20 % of the base's tokens):
  accuracy holds (base 192 against 192; RL 218 against 221, -0.9 points), token saving refuted: 7.4 % for the base (34,162
  against 36,902) and 5.9 % for RL (35,093 against 37,299). On this set fewer problems reach an early agreement.
- No base rule reaches one RL sample at equal tokens: the base's vote after restart (195 at 55,306 tokens) is below one RL
  sample (207 at 9,437; mean of the four samples 200.0). The nine rules chosen on MATH-500, scored once here:
  `results/frontier/hard328-01/frontier.md` (the command at the end of "Token frontier").
- The base loses 39 % of its single-sample accuracy from MATH-500 to the 328 (81.0 to 49.1 %), RL 31 % (91.2 to 63.1 %).

## Released RL checkpoints at T 1.0, plain and cue (ckptcue)

Spec and predictions, written before any job: `specs/SPEC_ckptcue.md`. Readout: `analysis/ckptcue.py`, output
`results/ckptcue/readout.json`; one folder per cell `results/ckptcue/<cell>-01/` (`run.json`, the job's `metrics.json`,
`per_problem.json`, `examples.json`). MATH-500, n = 500, T 1.0 / top-p 1.0, cap 16,384, grader v3, one sample; plain
cells use seed 45000000 (T2's), cue cells 41000000 (T1's). The checkpoints are `allenai/Olmo-3.1-7B-RL-Zero-Math` at
revisions `step_0100` (`0a45720c`) and `step_0400` (`897c0ce4`), downloaded in the job and passed with `--model-path`.
Raw answers: `runs/<job id>/answers.jsonl` in the worktree `iterate-hack-ckpt` on abaybektursun's laptop (the vast.ai
boxes are destroyed).

| Cell | Right of 500 | Cap hits | Tokens per problem | Job |
|---|---|---|---|---|
| base, plain (T3, reference) | 224 | 8 | | |
| base, cue (T1, reference) | 410 | 27 | | |
| RL step 100, plain | 418 | 24 | 4,120 | `abaybektursun-1115-064532-6a2f` |
| RL step 100, cue | 427 | 24 | 4,118 | `abaybektursun-1115-032509-fc06` |
| RL step 400, plain | 436 | 7 | 4,080 | `abaybektursun-1115-015818-b11d` |
| RL step 400, cue | 431 | 17 | 4,279 | `abaybektursun-1115-015852-a31f` |
| RL final (step 2,800), plain (T2, reference) | 463 | 6 | | |

| Difference (paired bootstrap over problems, 5,000 resamples) | Points | 95 % interval |
|---|---|---|
| step 100 plain minus base cue | +1.6 | [-2.0, +5.2] |
| step 100 cue minus step 100 plain | +1.8 | [-1.2, +4.8] |
| step 400 plain minus base cue | +5.2 | [+2.0, +8.4] |
| step 400 cue minus step 400 plain | -1.0 | [-4.0, +2.0] |
| step 400 plain minus step 100 plain | +3.6 | [+0.2, +7.0] |
| final plain minus step 400 plain | +5.4 | [+2.8, +8.0] |

Reading. At AI2's setting the first 100 RL steps bring the plain prompt from 224 to 418, and the cue alone brings the
untrained base to 410: the two are not separated (+1.6 points, interval includes 0), and the cue adds nothing
measurable to either checkpoint. H-open (the first 100 steps install what the cue gives) is not refuted; H-more (step
100 is past the cue) is not supported here, unlike at T 0.6 where step 100 leads the looping cued base by 5.4 points
(381 against 354). Of the 53 problems between the cued base and the final model, 8 come by step 100, 18 more by step
400 and 27 after step 400. All five filed predictions hold (step 100 plain 428 [412, 444]: 418; step 400 plain 447
[432, 459]: 436; cue gain at step 100 +0.5 [-3, +4]: +1.8; at step 400 0 [-3, +3]: -1.0; cap hits 25 [10, 45]: 24).

Limits. One sample per cell, so each count carries about 2 points of sampling noise; the step 100 difference cannot
exclude a lead of up to 5 points. The spec's identity check failed as written: 'Okay' in the first 30 characters is 383 of
500 at step 100 and 358 at step 400, below the 430 threshold taken from T 0.6 rows. At T 1.0 the plain answers open in
more ways (step 400: 243 start ' and resubmit.' and reach 'Okay' later), so the marker is not valid here. The
checkpoint's identity rests on the pinned revision in each job's command and `model_dir`, and on the scores lying
between the base's and the final model's. Three step 100 plain answers are empty (the model stops at once).
The first step 100 plain job (AWS `ih-1115-092337-b35c`) was cut by its 2-hour limit at 478 answers (405 right) and is not
used; a second run was lost with its box.

### Four samples per cell (ckptcue3, board work-f8ecb6)

Spec and predictions, written before any job: `specs/SPEC_ckptcue3.md`. Readout: `analysis/ckptcue3.py`, output
`results/ckptcue/readout3.json`. Three more samples of step 100 plain, step 100 cue and step 400 plain, one Modal H100 job
per cell (`run_cell.py --seed <S + 10000> --samples 3`, so the seeds are those of samples 1 to 3 of the cell's seed S):
`results/ckptcue/<cell>_s123-01/` (`run.json`, `metrics.json`, `rows.jsonl` in the shape of the Day-1 #3 rows with sample
= 1 to 3, `examples.json` with one right and one wrong answer). Sample 0 is the cell's `-01` folder above. The references
are now four samples each: attempt 0 of `results/day1_3/math500_base_cue-01/rows.jsonl` and
`results/day1_3/math500_rl-01/rows.jsonl`. Raw answers: `runs/<job id>/answers.jsonl` in the worktree
`iterate-hack-ckptcue3` on abaybektursun's laptop and in his Modal Volume.

```
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.ckptcue3 --runs runs s0100_plain=abaybektursun-1115-102945-9b20 s0100_cue=abaybektursun-1115-102956-6e9a s0400_plain=abaybektursun-1115-103006-7462
```

| Cell | Right of 500, samples 0 to 3 | Mean | Cap hits per sample | 'Okay' in first 30 characters | Tokens per problem | Job of samples 1 to 3 |
|---|---|---|---|---|---|---|
| base, cue (Day-1 #3) | 405, 409, 410, 418 | 410.5 | 25, 23, 22, 20 | not stored | 4,008 | |
| RL step 100, plain | 418, 411, 422, 419 | 417.5 | 24, 21, 21, 19 | 383, 375, 386, 373 | 4,049 | `abaybektursun-1115-102945-9b20` |
| RL step 100, cue | 427, 423, 423, 431 | 426.0 | 24, 24, 25, 23 | 500 each | 4,171 | `abaybektursun-1115-102956-6e9a` |
| RL step 400, plain | 436, 447, 435, 433 | 437.75 | 7, 16, 12, 12 | 358, 356, 369, 349 | 4,175 | `abaybektursun-1115-103006-7462` |
| RL final, plain (Day-1 #3) | 456, 462, 464, 458 | 460.0 | 6, 10, 5, 11 | not stored | 4,687 | |

| Difference of four-sample means (per problem the mean over 4 samples; paired bootstrap over problems, 5,000 resamples) | Points | 95 % interval | One sample, above |
|---|---|---|---|
| step 100 plain minus base cue | +1.40 | [-0.50, +3.25] | +1.6 [-2.0, +5.2] |
| step 100 cue minus step 100 plain | +1.70 | [0.00, +3.35] | +1.8 [-1.2, +4.8] |
| step 100 cue minus base cue | +3.10 | [+1.45, +4.70] | +3.4 [+0.2, +6.6] |
| step 400 plain minus step 100 plain | +4.05 | [+2.40, +5.70] | +3.6 [+0.2, +7.0] |
| final plain minus step 400 plain | +4.45 | [+3.05, +5.95] | +5.4 [+2.8, +8.0] |

Reading. With four samples the step 100 lead over the cued base is +1.4 points and its interval still includes 0, but its
upper end (+3.25) is outside the [-3, +3] band: by the spec's rule H-open is undecided, not supported, so "equals" is not
earned; the supported statement is "step 100 plain is within 3.3 points of the cued base, and not shown to differ". H-more
is not supported. The cue on top of step 100 adds +1.7 points with an interval whose lower end is exactly 0.00, so it is
borderline, and step 100 with the cue is above the cued base by +3.1 [+1.45, +4.70]: the one-sample lead was real. The
100 RL steps and the cue are therefore not interchangeable: together they give more than the cue alone. Step 400 leads
step 100 by +4.05 and the final model leads step 400 by +4.45, both intervals clear of 0. Of the 49.5 problems between the
cued base and the final model (four-sample means), 7 come by step 100, 20 more by step 400 and 22 after.

All filed predictions hold: means 417.5, 426.0, 437.75 (filed 418 [411, 425], 423 [416, 430], 437 [430, 444]); the five
differences lie inside their filed ranges; cap hits per new sample 21, 21, 19 (filed 24 [12, 36]). Identity check: each
new sample is within 15 of its cell's sample 0 (largest gap 11, step 400 sample 1). Smoke: job
`abaybektursun-1115-102326-6e86`, 30 rows read before the full jobs.

Limits. The interval is over problems; four samples leave a quarter of the sample variance in each mean (per-sample
counts spread over 11 to 14 problems within a cell). The plain and cue cells use different seeds. One benchmark, one
model family. Four of the 1,500 new step 100 plain answers and one step 400 answer are empty.

## Mixed-model vote on the 328: do two models' samples vote better together? (hard328, n = 328, laptop, board work-0d465a)

Question: the vote's remaining errors are problems where a model never writes the right answer ("The 328 with four samples
and restarts"). Do RL and Think-SFT fail on different problems, so that a vote over two samples of each beats four of
either? Answer: no. Four Think-SFT samples alone are the best row: 241 of 328 (73.5 %) at 40,410 tokens per problem; two RL
plus two Think-SFT have 228.1, 3.9 points [1.8, 6.2] below it, and all eight samples have 239.0 (-0.6 [-2.7, +1.7]).

`analysis/mixvote.py` (plurality vote of `analysis/day1_vote.py`, grader v3 as stored, attempt 0 of each sample, T 1.0 /
top-p 1.0, cap 16,384). Every way of taking the stated samples from each model is scored, in both interleaved orders; the
table has the mean and the range. Rows: RL plain `abaybektursun-1114-200505-5ff2`, base + cue `-200457-e8e6` (work-1a972a),
Think-SFT + cue `abaybektursun-1115-000503-1e5f`, `-000525-ea4e`, `-014823-ef56`, `-014833-1daa` (one sample each, work-0a00c2;
single right 212, 212, 211, 201). Readout `results/mixvote/hard328-01/readout.json`. Paired bootstrap, 5,000 resamples, seed 0.

| Samples | Right of 328 (mean) | Range over combinations | Tokens per problem |
|---|---|---|---|
| 1 base + cue | 158.5 | 152 to 161 | 9,225 |
| 1 RL | 200.0 | 190 to 209 | 9,325 |
| 1 Think-SFT + cue | 209.0 | 201 to 212 | 10,103 |
| 4 base + cue | 192 | | 36,902 |
| 4 RL | 221 | | 37,299 |
| 4 Think-SFT + cue | 241 | | 40,410 |
| 2 RL + 2 Think-SFT | 228.1 | 214 to 237 | 38,855 |
| 2 RL + 2 base | 207.6 | 193 to 221 | 37,101 |
| 2 Think-SFT + 2 base | 220.8 | 210 to 233 | 38,656 |
| 4 RL + 4 Think-SFT | 239.0 | 238 to 240 | 77,710 |
| 4 Think-SFT + 4 base | 238.0 | 237 to 239 | 77,312 |

- Think-SFT (no reward) minus RL: +2.7 points [0.4, 5.2] on one sample (mean of four each), +6.1 [3.0, 9.5] under the vote
  over 4. The vote helps Think-SFT more (+32 problems) than RL (+21). Under the vote Think-SFT alone is right on 26 problems
  where RL is wrong, RL alone on 6; both 215, neither 81.
- A mixed vote lands between its two models every time (2 RL + 2 Think-SFT: +2.2 [0.3, 4.2] over 4 RL, -3.9 [-6.2, -1.8]
  under 4 Think-SFT). RL adds almost no problems that Think-SFT misses, so mixing dilutes the better model.
- Caveats: Think-SFT's training prompts match 6 of the 328 (board result-f6a8bc; the lead holds without them); its samples
  have no restart rows; the vote's tie rule prefers the earlier sample, hence both orders.

## Risk-coverage: Think-SFT's lead over RL on the 328 is in long answers to hard problems (hard328 n = 328, MATH-500 n = 500, laptop, board work-4ecc65, work-55ae25, idea-ce2272)

Question: on the 328 Think-SFT + cue has vote 241 against RL 221 (result-818c20), hits the cap on 29 % of samples (RL 9 %),
and its finished answers are right 88 % of the time (RL 66 %). Is it more precise than RL at the same coverage, and on which
answers? Answer: only on the long ones. Keeping each model's shortest answers, the two are equally precise up to half of all
samples (coverage 0.50: 94.8 % against 93.0 %, +1.8 points [-0.8, +5.5]); the difference opens at 0.55 (+3.7 [0.6, 7.1]) and
is +8.8 [6.4, 12.5] at 0.75, the largest coverage all three models reach. Finished answers over 12,000 tokens are right
68.2 % of the time for Think-SFT (135 of 198), 24.4 % for RL (87 of 356), 16.7 % for the base (41 of 246); under 4,000
tokens all three are at 88 to 100 %. Of Think-SFT's 53 right samples on the 26 problems where its vote is right and RL's is
not, 49 are over 8,000 tokens and 35 over 12,000. On MATH-500 there is no lead in precision at any matched coverage (area
-0.8 [-1.7, +0.1]). Spec, written before the script: `specs/SPEC_riskcov.md` (commit `7a779d0`).

Correction (work-55ae25, after a reviewer's comment on result-b006f5; `specs/SPEC_riskcov.md` addendum 1, commit `fc4bf28`,
written before `analysis/riskcov_strat.py`; run folder `results/riskcov/hard328_strat-01/`). "Only on the long ones" and
"equally precise up to coverage 0.50" above confound length with difficulty; the numbers stand, the reading changes. Both
length and difficulty matter, and neither reading alone survives:

- The reviewer's numbers reproduce. Of the samples kept at coverage 0.50, 81.1 % (Think-SFT) and 80.6 % (RL) come from the
  149 problems the cued base solves 3 or 4 times of 4, where both are right 98.5 % of the time: the equal precision is this
  mix. On the 179 problems the base solves at most twice Think-SFT leads at coverage 0.30 by +15.8 points [7.4, 25.6]
  (78.6 % against 62.8 %).
- That point is not a short answer: the last sample kept there has 12,715 tokens (Think-SFT) and 11,161 (RL). On hard
  problems nearly every answer is long. On the 121 problems the base never solves, Think-SFT has 11 finished answers of at
  most 8,000 tokens and RL 18 (lead +14.1 [-17.2, +73.3]): short answers to the hardest problems cannot be tested here.
- Difficulty held, length matters. Lead in finished answers over 8,000 tokens against at most 8,000, by the base's right
  count: 1-2: +29.1 [19.1, 39.4] (113 of 126 against 89 of 147) against +4.4 [-3.8, +14.1] (47 of 48, 58 of 62), long minus
  short +24.8 [10.5, 38.4]; 3-4: +6.8 [-0.6, +13.4] (96 of 102, 103 of 118) against 0.0 [-1.2, +1.1], and +22.7 [3.4, 37.9]
  over 12,000 tokens (32 of 35, 22 of 32). No stratum with enough samples has a lead in short answers.
- Length held, difficulty matters. Lead in answers over 8,000 tokens: +34.5 [24.9, 43.7] where the base is never right
  (86 of 163 against 69 of 377), +29.1 at 1-2, +6.8 at 3-4; never right minus 3-4: +27.6 [15.8, 39.9].
- Problem held (problem x model fixed effects, finished answers). An RL answer over 8,000 tokens is right 12.5 points less
  often than its shorter answers to the same problem [-20.8, -4.8] (57 problems carry it); Think-SFT's +1.2 [-4.0, +7.0] (53);
  difference +13.7 [3.9, 23.8]. Per 1,000 tokens: RL -4.0 points [-5.4, -2.6], Think-SFT -0.4 [-1.4, +0.6], difference +3.6
  [1.9, 5.4], and excluding 0 in each base stratum (+4.1 [0.3, 7.9], +5.4 [1.5, 8.9], +2.6 [0.1, 4.9]). On the 155 problems
  where both models have a finished answer over 8,000 tokens Think-SFT leads by +20.6 [15.6, 25.5]; on the 149 with one of at
  most 8,000 each, +0.7 [-0.3, +1.8]. The 28 problems with both give long minus short +10.3 [-3.7, +25.0]: same sign, covers 0.
- Second stratifier, without the base and without the sample's own rows: per sample s, the right samples among the other
  three of Think-SFT and the other three of RL (0 to 6). Same conclusion on length: at 4-6, lead +18.2 [12.8, 23.7] over 8,000
  tokens (216 of 227 against 190 of 247) against +0.4 [-1.0, +1.8] below, long minus short +17.9 [12.3, 23.5]. Difficulty is
  not monotone: +39.4 [25.6, 52.2] at 1-3 (71 of 91, 61 of 158), +6.7 [-0.2, +15.9] at 0 (8 of 73, 10 of 237: both near zero
  where no other sample of either model is right).

Reading that survives: the lead is in long answers, and its size there grows with difficulty until both models fail; "hard
problems, not long answers" and "long answers, not hard problems" are both refuted by the criteria of the addendum. Caveats:
the base's count is 4 samples; Think-SFT's finished long answers are a selected set (it hits the cap on 29 % of samples, RL on
9 %); long = over 8,000 tokens was fixed by the first spec. Instrument check (`analysis/riskcov_test.py`): with right planted
from problem and model only, the raw lead is larger in long answers and the within-problem slope difference covers 0; planted
from model and length only, it excludes 0. `table.md` has every stratum, bin and coverage step; `examples.json` one right
Think-SFT and one wrong RL answer of at most 8,000 tokens on problems the base never solves.

`analysis/riskcov.py` on the stored rows (T 1.0 / top-p 1.0, cap 16,384, grader v3 as stored, 4 samples per problem; attempt
0 of each sample for all three models, since the RL and base runs have restarts and Think-SFT has none). A sample is
answered when it has an extracted answer; coverage = kept samples over all samples; precision = right over kept. Signals see
tokens, cap hit and extracted answers only. Intervals: bootstrap over problems (2,000 resamples, paired across models).
Instrument checks: the vote over attempt 0 reproduces 241 / 221 / 192 on the 328 and 481 / 474 / 446 on MATH-500 (asserted);
`analysis/riskcov_test.py`: planted perfect abstention gives precision 1 at every coverage, shuffled lengths give a flat
curve (every band holds the overall precision) while the real lengths do not, planted lengths give precision 1 up to the
right share. Run folders `results/riskcov/hard328-01/`, `math500-01/` (`readout.json`, `curves.json`, `table.md`,
`examples.json`: one long right Think-SFT answer, one long wrong RL answer), `read-01/` (the 25 rows read by hand, `notes.json`).

Precision at matched coverage, signal = fewer generated tokens first (`table.md` has every 0.05 step and the signal
agreement-then-length):

| Set | Coverage | Think-SFT + cue | RL plain | base + cue | Think-SFT - RL, points [95 %] |
|---|---|---|---|---|---|
| hard328 | 0.30 | 98.5 | 99.0 | 91.4 | -0.5 [-2.3, +1.0] |
| hard328 | 0.50 | 94.8 | 93.0 | 82.3 | +1.8 [-0.8, +5.5] |
| hard328 | 0.60 | 93.0 | 87.3 | 76.1 | +5.7 [+2.2, +9.9] |
| hard328 | 0.70 | 88.8 | 79.4 | 67.5 | +9.4 [+6.3, +12.3] |
| hard328 | 0.75 | 85.0 | 76.1 | 63.9 | +8.8 [+6.4, +12.5] |
| MATH-500 | 0.30 | 98.7 | 99.8 | 96.0 | -1.2 [-2.2, -0.2] |
| MATH-500 | 0.50 | 98.8 | 99.9 | 96.3 | -1.1 [-2.0, -0.3] |
| MATH-500 | 0.70 | 98.9 | 99.6 | 95.2 | -0.7 [-1.4, -0.1] |
| MATH-500 | 0.90 | 97.8 | 97.6 | 89.3 | +0.2 [-0.8, +1.2] |
| MATH-500 | 0.95 | 96.5 | 95.6 | 86.4 | +0.9 [-0.4, +2.1] |

Area (mean precision over the grid up to the common coverage), hard328: by length 95.3 / 93.1 / 84.8 (Think-SFT minus RL
+2.2 [0.6, 4.2]); by agreement among the four samples, then length 97.1 / 95.1 / 89.7 (+2.0 [0.8, 3.7]); in a random order
83.6 / 62.0 / 61.6 (+21.6). So a label-free order removes most of the 21-point difference in raw precision: RL's wrong
answers are its long and its lone ones. With agreement first, RL is at 100.0 % up to coverage 0.35 and 99.8 % at 0.40.

Finished answered samples by generated tokens, hard328 (right / samples, %; in brackets the 267 problems where all three
models have a finished answered sample):

| Tokens | Think-SFT + cue | RL plain | base + cue |
|---|---|---|---|
| 0 to 2,000 | 74 / 75, 98.7 | 59 / 59, 100.0 | 171 / 177, 96.6 |
| 2,000 to 4,000 | 170 / 173, 98.3 | 185 / 186, 99.5 | 169 / 191, 88.5 |
| 4,000 to 8,000 | 283 / 292, 96.9 | 288 / 310, 92.9 (93.2) | 161 / 221, 72.9 (74.8) |
| 8,000 to 12,000 | 160 / 193, 82.9 (83.2) | 174 / 286, 60.8 (66.5) | 88 / 164, 53.7 (56.2) |
| 12,000 to the cap | 135 / 198, 68.2 (67.6) | 87 / 356, 24.4 (33.8) | 41 / 246, 16.7 (22.1) |

Right answers counted, not rated: under 12,000 tokens RL has more right samples than Think-SFT (706 against 687 of 1,312);
over 12,000 Think-SFT has 135 against 87 (plus 14 against 7 right cap hits). Its whole lead of 36 right samples (836 against
800) is there. MATH-500: 12,000 to the cap 76.9 % (70 of 91) against 39.7 % (46 of 116) and 39.6 % (42 of 106).

Outcomes on the 328, Think-SFT + cue (rows) against RL plain (columns):

| One sample (4 pairs per problem, summed; 1,312) | RL abstained | RL wrong | RL right |
|---|---|---|---|
| Think-SFT abstained | 26 | 248 | 52 |
| Think-SFT wrong | 2 | 121 | 27 |
| Think-SFT right | 8 | 107 | 721 |

| Vote over 4 (328 problems) | RL abstained | RL wrong | RL right |
|---|---|---|---|
| Think-SFT abstained | 0 | 26 | 4 |
| Think-SFT wrong | 0 | 55 | 2 |
| Think-SFT right | 0 | 26 | 215 |

Where a Think-SFT sample gives no answer, RL's sample is wrong 248 times, right 52, also without an answer 26. Of RL's 476
wrong samples, 248 (52 %) face a Think-SFT sample without an answer, 121 a wrong one, 107 a right one.

- H1 (the lead is in the long answers): held. Difference by length inside +-2 points with intervals covering 0 up to
  coverage 0.50, excluding 0 from 0.55; bins above. Not uniform across length, and not absent. Corrected above: this test
  alone does not separate length from difficulty; with difficulty held the lead is still in long answers, and its size
  depends on difficulty.
- H2 (RL is wrong where Think-SFT abstains, beyond difficulty): mostly difficulty. On the 141 problems with at least one
  Think-SFT cap hit, RL's finished answers are right 31.2 % of the time (144 of 461; 66.2 % on all problems), and it finishes
  82 % of its samples there. The control: RL's precision per stratum of the base's number of right samples (0 to 4), weighted
  to these problems, gives 35.2 %: observed minus expected -3.9 points [-6.9, -1.0], below the 5 points the spec asked for.
  The strata rates there include the 141 problems themselves; with rates from the other 187 problems only (added after the
  spec) the expected value is 48.9 % and the difference -17.6 [-31.0, -4.5]. The residual sits where all four Think-SFT
  samples hit the cap (48 problems): RL 8.8 % (13 of 147) against 22.8 % expected, -14.0 [-20.5, -7.5]; the base 3.8 % (3 of
  79). MATH-500, 52 problems: 62.7 % against 72.3 %, -9.6 [-14.8, -4.3]. Reverse: on the 67 problems with an RL cap hit
  Think-SFT's finished answers are right 75.6 % (68 of 90) against 69.5 % expected, +6.0 [-4.4, +15.7], and it hits the cap
  on 66 % of its samples there. The base strata are a coarse control (121 of the 328 share the stratum "never right").
- H3 (a length cut before the vote does not help RL or the base): held. Rule: drop every sample longer than L tokens before
  the vote; if none is left, the plain vote. L chosen on MATH-500 only, scored once on the 328: RL L = 16,000, 224 against
  221 (+0.9 points [0.0, 2.1], 37,168 tokens per problem if generation stops at L, 37,299 as run); base L = 12,000, 189
  against 192 (-0.9 [-2.7, +0.6]; 35,124 / 36,902); Think-SFT L = 4,000, 240 against 241. On MATH-500 the chosen cuts gained
  1, 4 and 1 problems. No cut reaches Think-SFT's 241. Without the fall-back the cut only abstains (RL at 12,000: 210 right,
  59 wrong, 59 abstained).
- Score = right - lambda x wrong, hard328, one sample (mean of four): lambda 0: 209.0 / 200.0 / 158.5; lambda 0.5: 190.2 /
  140.5 / 106.8; lambda 1: 171.5 / 81.0 / 55.0. Vote: 241 / 221 / 192; 212.5 / 167.5 / 130.0; 184 / 114 / 68. MATH-500 one
  sample: 460.2 / 460.0 / 410.5; lambda 1: 440.0 / 421.8 / 344.5. A metric that charges for wrong answers widens Think-SFT's
  lead from 9 to 90 problems per sample.

Hand read of 25 rows (seed 0, `results/riskcov/read-01/`; the end of each text, not a measurement). 10 finished wrong RL
answers of 8,000 tokens or more on problems where Think-SFT hit the cap: 2 derive the boxed number with an error, 1 derives
it from an assumption it never checks, 1 closes with a false step (problem 117: "Simplify: x_4 = 25/11"), 6 box a number the
write-up does not derive, three in so many words (problem 189: "the correct answer based on the common geometric properties
and the boxed integer result is 6"; problem 165: "typically the answer is expected to be an integer"). All ten end in a
formatted final answer. 10 finished right Think-SFT answers of 8,000 tokens or more: 8 derive the answer in the write-up, 2
hedge. 5 Think-SFT cap hits on the same problems as the RL rows: 4 are mid-computation or re-checking (problem 117: still
computing the exact fractions RL cut short), 1 is cut inside a right final write-up. A rough count outside the spec: 5 of
RL's 1,197 finished answers end in text that is not mathematics, so the long wrong answers are ordinary write-ups.

Reading: RL writes a final answer on 97 % of samples and Think-SFT on 75 %. On problems neither solves, Think-SFT runs to the
cap and RL boxes a number, which costs RL no right answers and most of its precision.
Think-SFT's lead in right answers is in answers of 12,000 tokens and more, where it is right 68 % of the time against 24 %.
Not tested here: whether RL's long answers are wrong because it stops too early (work-ceccc0 raises the cap for all three).

```
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.riskcov_test
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.riskcov --set math500 --out studies/rlneurons/results/riskcov/math500-01 --think-run runs/thinkvote_math500_sft1_cue_s4 --rl-run runs/abaybektursun-1114-183640-e828
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.riskcov --set hard328 --out studies/rlneurons/results/riskcov/hard328-01 --fixed studies/rlneurons/results/riskcov/math500-01/chosen.json --think-run runs/thinkvote_hard328_sft1_cue_s4 --rl-run runs/abaybektursun-1114-200505-5ff2
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.riskcov --set hard328 --read studies/rlneurons/results/riskcov/read-01 --think-run runs/thinkvote_hard328_sft1_cue_s4 --rl-run runs/abaybektursun-1114-200505-5ff2
```

## Think-SFT training-data overlap, every shard and every turn (hard328 and MATH-500, laptop, board work-173c5c)

Question: are the test problems in the training data of allenai/Olmo-3-7B-Think-SFT (allenai/Dolci-Think-SFT-7B, revision
83f618e), in any turn of any row? Answer: the full scan finds no new hard328 problem. The same 6 of 328 match as in the
first-user-message scan (board result-f6a8bc), and all 6 match in user turns. Without them the headline holds: vote over 4,
Think-SFT + cue 235 and RL 215 of 322, +6.2 points [3.1, 9.6] (all 328: 241 against 221, +6.1 [3.0, 9.5]). MATH-500: 29 of
500 match (25 before). The 4 new ones match only in assistant turns, and their raw text shows a phrase from the problem
inside a reasoning trace about a different problem, not a copy.

Method: `analysis/wsp1_sft_overlap.py --turns all` (the teammate's script from branch
`claude/weight-space-programming-research-ddd44e`, extended). It scans all 156 shards and 2,268,178 rows, and matches every
message: 2,368,984 user turns and 2,368,984 assistant turns (the data has no system turns). Each role is matched apart. The
rule is the one in `analysis/rln3_overlap.py`: lower case, non-alphanumerics to spaces. A problem is exact when it equals a
message and near when at least half of its word 8-grams occur in one message. Assistant turns reach the matcher only when
one of their 8-grams hashes to a test 8-gram (245,709 do). The selftest shows this filter changes no match on 3,000 real
assistant turns. hard328 is the 328 problems with RL-overlap flag none (as in `jobs/run_cell.py`). The vote difference
reads rows "4 think" and "4 rl" of `results/mixvote/hard328-01/readout.json` (paired bootstrap, 5,000 resamples, seed 0).
Run folder `results/wsp1/sft_overlap-03/`: `run.json` (commit 385e301, command, shards), `metrics.json` (counts by role,
vote difference), `flags.json` (per problem: flag, share, best row per role with id, shard and row), `selftest.txt`.
Wall time 57 min on 10 processes, bound by download speed.

| Set | Flagged (exact + near) | Matched in user turns | Matched in assistant turns | Matched only in assistant turns | Before (first user message, 123 shards) |
|---|---|---|---|---|---|
| hard328 | 6 (4 + 2) | 6 | 1 (hard/272, the same row as its user match) | 0 | 6 |
| MATH-500 | 29 (3 + 26) | 25 | 12 | 4: 289, 406, 438, 439 (share 0.50 to 0.80) | 25 |

| hard328, vote over 4 | n | Think-SFT + cue | RL | Think-SFT minus RL, points [95 % interval] |
|---|---|---|---|---|
| All problems | 328 | 241 | 221 | +6.1 [3.0, 9.5] |
| Without the 6 flagged | 322 | 235 | 215 | +6.2 [3.1, 9.6] |

- Selftest (`selftest.txt`): a planted exact copy in a user turn is flagged exact. A copy with changed whitespace and LaTeX
  spacing inside a longer user turn is flagged near (share 1.0). A copy inside an assistant turn is flagged near in the
  assistant role and not in the user role. A 40 % copy is not flagged (share 0.34). A real training row is found exact in
  its own shard.
- The 33 shards that the first scan skipped (code rows) add no match. The hard328 matches come from
  SYNTHETIC-2-SFT (5) and OpenThoughts3 math (1).
- Caveats: the rule detects copies of the text only. A paraphrase, a translation or a variant with changed numbers is not
  detected. About 14 of the first 25 MATH-500 flags are template siblings with other numbers (board result-f6a8bc comments).
  A problem of fewer than 8 words (13 in MATH-500, none in hard328) is flagged only when a whole message equals it.

## Derived or asserted: when it finishes long and wrong, RL boxes an underived number as often as the base; it finishes more often, so per sample it emits more of them (hard328, laptop, board work-dd4773, idea-6f4b9e)

Question: the hand read of result-b006f5 found 6 of 10 long wrong RL answers that box a number their text never derives. Did
reward training add this, and does the label help? Answer: no, and little. A blind judge labels 72.5 % [63.1, 81.3] of RL's
finished wrong answers over 8,000 tokens as asserted, 66.2 % [54.6, 77.2] of the cued base's and 36.2 % [24.4, 48.6] of
Think-SFT's (80 rows each): RL minus base +6.2 points [-6.7, +19.1], RL minus Think-SFT +36.2 [23.3, 49.1], base minus
Think-SFT +30.0 [14.7, 45.6]. So the untrained base does it as often as RL; the model that differs is Think-SFT. The label
carries information about correctness (RL: asserted answers are right 17.0 % of the time, derived ones 66.1 %), but as an
abstention signal it does no better than length alone (+0.5 points [-1.4, +2.6]). Spec, rubric and predictions, pushed
before any judging: `specs/SPEC_derived.md` (commit `a9b65ed`).

Reworded after a review of result-02da9f (addendum 1, "Per generated sample" below). The first headline, "RL did not add the
habit", holds only among long finished wrong answers. Per generated sample RL emits an asserted wrong answer in 21.1 %
[16.9, 25.1] of 1,312 samples, the base in 14.2 % [11.1, 17.4], Think-SFT in 2.7 % [1.6, 3.8]: RL minus base +6.9 points
[3.1, 10.6]. RL does not assert more often when it finishes long and wrong, but it finishes long and wrong more often (381
samples against 281), on the problems where the base hits the cap (286 cap hits against RL's 114).

`analysis/derived.py`. Rows: attempt 0 of the three stored 4-sample hard328 runs (T 1.0 / top-p 1.0, cap 16,384, grader v3);
per model 80 finished wrong and 60 finished right answers over 8,000 tokens, drawn by the seeded rule of the spec, at most 2
per problem and stratum. The judge sees the problem and the last 3,000 tokens of the answer (characters in proportion; think
tags removed), not the model, the gold answer, the score or the length. Labels: DERIVED (the shown steps arrive at the final
value, right or not), ASSERTED (the value is stated without shown steps that arrive at it: a give-up, an appeal to the
expected answer, a value picked after contradicting computations, a decisive step that is only claimed), UNCLEAR (never
used). Judge A, every table: `claude-sonnet-5-5`, effort low. Judge B: `claude-haiku-5-5`, also on the other 502 long
finished RL answers. Both through the `anthropic` SDK; cost 7.37 USD from the saved token usage (A 5.30, B 0.65, full-text
condition 1.42). Two departures from the spec: the reply is forced to the JSON schema by the API instead of parsed by
`swarm_judge`'s rule, and three smoke items were judged while the hand labels were being written. Intervals: bootstrap over problems, 2,000 resamples, seed 0.

Instrument checks:

- Planted positives (15 long answers cut at 60 % and closed with a bare `The answer is \boxed{N}`): ASSERTED 15 of 15, both
  judges. Planted negatives (15 right answers under 3,000 tokens): DERIVED 15 of 15, both judges.
- Two judges on the 420 rows: 379 agree, Cohen's kappa 0.80 (Think-SFT 0.79, RL 0.86, base 0.73).
- 30 rows labelled blind by the agent before any judge call (a fork of the session that saw the same text and no model,
  score or length; another model, not a person): 25 of 30 agree with judge A, kappa 0.60, exactly at the spec's bar; with
  judge B 23 of 30, kappa 0.49. All 5 disagreements with A are hand DERIVED, judge ASSERTED (hand 6 asserted, judge 11): an
  answer that rests on an unproven uniqueness claim, a pattern from small cases or an unchecked existence (rows i0000,
  i0874, i0917, i0942, i0663 of `labels.jsonl`). So the judge's "asserted" is wider than "boxes a number out of nowhere":
  it includes answers whose decisive step is a conjecture. Read the shares as the judge's, and the differences between
  models as the result. The hand labels alone, 5 wrong rows per model: Think-SFT 0 asserted, RL 1, base 5.
- Tail against the whole text (40 rows, judge A): 38 agree, kappa 0.84. The judge's quote is found in the shown text in 420
  of 450 rows.

Long finished answers by label, judge A (judge B in `table.md`: 42.5 / 72.5 / 66.2 % asserted among the wrong ones):

| Model | Stratum | Rows | Derived | Asserted | Unclear | Asserted, % [95 %] |
|---|---|---|---|---|---|---|
| Think-SFT + cue | wrong | 80 | 51 | 29 | 0 | 36.2 [24.4, 48.6] |
| Think-SFT + cue | right | 60 | 55 | 5 | 0 | 8.3 [1.9, 15.7] |
| RL plain | wrong | 80 | 22 | 58 | 0 | 72.5 [63.1, 81.3] |
| RL plain | right | 60 | 47 | 13 | 0 | 21.7 [11.1, 33.9] |
| base + cue | wrong | 80 | 27 | 53 | 0 | 66.2 [54.6, 77.2] |
| base + cue | right | 60 | 48 | 12 | 0 | 20.0 [10.4, 30.6] |

- H1 (RL's asserted share among long wrong answers is 20 points above both others): refuted by the base. Against Think-SFT
  it holds (+36.2 [23.3, 49.1]; judge B +30.0 [15.0, 44.8]); against the base it is +6.2 [-6.7, +19.1] (judge B +6.2
  [-8.0, +19.8]), under the 10 points the spec asked for. As predicted in the spec.
- H2 (asserted answers are rarely right): held. Strata weighted back to the pool of long finished answers:

| Model | Asserted share of long finished answers, % | Right among asserted, % | Right among derived, % | Difference |
|---|---|---|---|---|
| Think-SFT + cue (96 wrong, 295 right) | 15.2 [9.4, 21.6] | 41.4 [13.4, 62.5] | 81.5 [75.3, 86.9] | 40.1 [18.4, 68.6] |
| RL plain (381, 261) | 51.8 [43.3, 60.3] | 17.0 [9.0, 25.6] | 66.1 [56.5, 75.2] | 49.1 [34.7, 62.6] |
| base + cue (281, 129) | 51.7 [42.3, 60.5] | 12.2 [6.1, 18.9] | 52.1 [42.3, 62.6] | 39.9 [26.6, 53.0] |

  Judge B on all 642 long finished RL answers, no weighting: asserted 54 of 319 right (16.9 % [11.6, 22.8]), derived 207 of
  323 (64.1 % [56.7, 70.5]). Half of RL's and of the base's long finished answers are asserted, 15 % of Think-SFT's.
- H3 (the flag beats length as an abstention signal; descriptive, the judge is another model, no `score:` line): not held.
  RL's 1,312 samples: all answered, coverage 97.3 %, precision 62.7 %. Dropping the 319 answers judge B flags (54 of them
  right): coverage 72.9 %, precision 78.0 % [73.9, 81.6]. Keeping the shortest answers to the same coverage: 77.4 %
  [73.0, 81.1]. Difference +0.5 points [-1.4, +2.6] (predicted +4). From judge A's sample weighted to the pool: 78.8 %
  against 78.4 % at coverage 71.9 %. A judge call per answer buys nothing over counting tokens.
- By length (judge A, wrong answers; asserted / rows): 8,000 to 12,000 tokens Think-SFT 4 / 25 (16 %), RL 15 / 22 (68 %),
  base 8 / 25 (32 %); 12,000 to the cap Think-SFT 25 / 55 (45 %), RL 43 / 58 (74 %), base 45 / 55 (82 %). RL's share is
  already high at 8,000 to 12,000; the base's rises with length. Cells of 22 to 58 rows.
- RL's long wrong answers on the 48 problems where all four Think-SFT samples hit the cap against the other problems:
  judge A's sample 23 of 30 (76.7 % [62.1, 90.0]) against 35 of 50 (70.0 % [56.5, 82.5]); judge B on all 381: 111 of 133
  (83.5 % [76.6, 89.8]) against 154 of 248 (62.1 % [54.7, 69.6]). Where Think-SFT runs to the cap, RL's wrong answer is
  more often asserted.
- Predictions of the spec: asserted share of long wrong answers 45 / 20 / 35 % (RL / Think-SFT / base), observed 72.5 /
  36.2 / 66.2: the order was right, every level too low. Under 10 % among right answers: wrong for RL and the base (21.7,
  20.0). Kappa between judges 0.60 predicted, 0.80 observed; hand against judge 0.70 predicted, 0.60 observed.

What an asserted RL ending looks like (rows read in `labels.jsonl` and the raw text): the reasoning stops with a statement
that time is up, and the value is named as a guess. Then comes a final write-up in numbered steps, formatted like a
solution, in which the step that should produce the value is a phrase. Problem 109, sample 3 (boxes 180, gold 336): "since
this is taking too long and I need to conclude, the answer is 180°, which I think is a common result"; its write-up ends
"After considering the symmetry and the properties of the nine-point circle, we conclude that the required value is". Problem
274, sample 1 (208, gold 10): "Perhaps the answer is \boxed{208} and I have to go with that." Problem 361, sample 1 (1,
gold 4/3): "After struggling for so long, and seeing that my time is up, I think the answer is likely 1." The base's asserted
endings read the same ("I might hazard a guess that the intended answer is \boxed{18}, but I am not confident", problem 222).
Give-up wording
(`give up, guess, hazard, time, go with, likely, ...`) is in the judge's quote for 32 of RL's 71 asserted rows, 27 of the
base's 65 and 10 of Think-SFT's 34 (a keyword count outside the spec); the others rest on a conjecture or an unproven claim.

Reading: when a model of this family finishes a long answer it has not solved, it names a value and formats it as a solution.
The base does this without any reward, so the RL reward did not create it; RL also did not remove it, and RL finishes 97 %
of its samples. Think-SFT, trained on traces, does it half as often among its long wrong answers and, mostly, does not finish
at all (cap hits on 29 % of samples). Limits: one sampling setting; the judge's label is wider than the hand label and the
hand agreement is at the bar; Think-SFT's long finished wrong answers are a small, selected pool (96 rows, 80 judged);
the hand labels come from a model, not a person; the literature was searched with WebSearch only (no Exa key), no paper
was read in full.

### Per generated sample (addendum 1 of the spec, after a review of result-02da9f)

The tables above condition on a long finished answer; a sample that hits the cap is in none of them. Here the unit is the
generated sample: attempt 0 of the 4 samples, 1,312 per model, each with exactly one outcome. Finished answers of at most
8,000 tokens were not judged and are given as right or wrong only. The judged strata are weighted back to their pools (pool
rows x label share of the judged sample / 1,312; the code of H2). No new judge call: the labels are those of
`results/derived/hard328-01/labels.jsonl`. Addendum written and pushed before the numbers (commit `05739a6`), after the
reviewer's two numbers (about 21 % and 14 %; cap hits 286 and 114), which reproduce: 381 x 58 / 80 / 1,312 = 21.1 %,
281 x 53 / 80 / 1,312 = 14.2 %, cap hits 286 (base), 114 (RL), 378 (Think-SFT).

% of the model's 1,312 samples [95 %, bootstrap over problems, 2,000 resamples, seed 0], judge A:

| Outcome | Think-SFT + cue | RL plain | base + cue |
|---|---|---|---|
| long right, derived | 20.6 [17.3, 24.1] | 15.6 [12.2, 19.1] | 7.9 [6.0, 9.7] |
| long right, asserted | 1.9 [0.4, 3.7] | 4.3 [2.1, 6.9] | 2.0 [1.0, 3.1] |
| long wrong, derived | 4.7 [3.2, 6.3] | 8.0 [5.3, 10.9] | 7.2 [4.8, 9.9] |
| long wrong, asserted | 2.7 [1.6, 3.8] | 21.1 [16.9, 25.1] | 14.2 [11.1, 17.4] |
| short right (at most 8,000 tokens, not judged) | 40.2 [35.1, 45.2], 527 | 40.5 [35.6, 45.8], 532 | 38.2 [33.4, 42.9], 501 |
| short wrong (not judged) | 1.0 [0.4, 1.8], 13 | 1.8 [0.9, 2.7], 23 | 6.7 [5.3, 8.2], 88 |
| cap hit | 28.8 [24.6, 33.2], 378 | 8.7 [6.6, 10.8], 114 | 21.8 [18.4, 25.2], 286 |
| no answer, no cap hit | 0.2 [0.0, 0.5], 3 | 0.1 [0.0, 0.2], 1 | 2.1 [1.4, 2.8], 27 |

Judge B, weighted the same way: long wrong asserted 3.1 / 21.1 / 14.2 % (Think-SFT / RL / base). Judge B labelled the whole
pool only for RL (all 642 long finished answers); for the base and Think-SFT only the 140 sampled rows exist. RL counted on
its whole pool: long wrong asserted 265 of 1,312 samples, 20.2 % [17.0, 23.5]; long wrong derived 116, 8.8 %; long right
asserted 54, 4.1 %; long right derived 207, 15.8 %. A cap hit counts as a cap hit also when the text holds a boxed value
(55 / 79 / 49 samples, Think-SFT / RL / base; 14 / 7 / 4 of them graded right).

Asserted wrong answers per sample, paired differences in points. The difference splits exactly into a pool term (how often
the model finishes long and wrong, at the other model's asserted share) and a share term (how often such an answer is
asserted, at the model's own pool):

| Judge | Pair | Difference | Pool term | Share term |
|---|---|---|---|---|
| A | RL - base | +6.9 [3.1, 10.6] | +5.0 [2.9, 7.6] | +1.8 [-2.0, 5.6] |
| A | RL - Think-SFT | +18.4 [14.6, 22.3] | +7.9 [5.0, 11.0] | +10.5 [6.5, 14.8] |
| B | RL - base | +6.9 [3.1, 10.8] | +5.0 [2.9, 7.6] | +1.8 [-2.3, 5.7] |
| B | RL - Think-SFT | +17.9 [14.0, 21.8] | +9.2 [6.1, 12.5] | +8.7 [4.2, 13.3] |
| B, RL counted on its whole pool | RL - base | +6.0 [2.8, 9.4] | | |
| B, RL counted on its whole pool | RL - Think-SFT | +17.1 [14.0, 20.2] | | |

Cap-hit rate: RL minus base -13.1 points [-16.3, -10.2], RL minus Think-SFT -20.1 [-24.0, -16.5].

- H4 (per sample, RL emits more asserted wrong answers than the base): held, +6.9 points [3.1, 10.6].
- H5 (the difference comes from how often RL finishes long and wrong, not from the asserted share): held. The pool term is
  5.0 of the 6.9 points [2.9, 7.6]; the share term is 1.8 [-2.0, 5.6], which is H1's +6.2 points of share, not different
  from 0.
- Where RL's extra long wrong answers are. Samples on the 137 problems where the base hits the cap at least once, base
  against RL: cap hits 286 against 103, long finished wrong 176 against 291, long finished right 32 against 117. On the 191
  problems where the base never hits the cap: cap hits 0 against 11, long wrong 105 against 90, long right 97 against 144.
  So all of RL's 100 extra long wrong answers (381 against 281) are on the problems where the base hits the cap: there RL
  has 183 fewer cap hits, 115 more long wrong answers and 85 more long right ones. Of RL's 265 long wrong answers that judge
  B labels asserted, 224 are on these 137 problems. Think-SFT there: 338 cap hits, 49 long wrong, 132 long right.

What survives. (a) Among long finished wrong answers RL and the base assert equally often (72.5 % against 66.2 %, +6.2
[-6.7, +19.1]): unchanged. (b) Per generated sample RL emits more asserted wrong answers than the base (21.1 % against
14.2 %), and about three quarters of that difference is RL finishing where the base hits the cap. The headline "RL did not
add the habit" is too strong and is reworded: RL does not assert more often when it finishes long and wrong, but it finishes
more often, so per sample it emits more asserted wrong answers. What RL changed is the stopping, not the share: on the
problems where the base runs out of tokens, RL stops and answers, and the answer is right in 117 samples and long and wrong
in 291. Against Think-SFT both terms count: RL finishes long and wrong four times as often (381 against 96) and asserts
twice as often when it does. Limits: the split by the base's cap hits is descriptive (samples of different models are not
paired; only problems are); the base's and Think-SFT's rates rest on 80 judged rows per stratum; short answers are not
judged, so asserted answers under 8,000 tokens are not counted for any model.

Run folder `results/derived/hard328_persample-01/`: `readout.json`, `table.md` (both judges, every count), `run.json`.

Run folder `results/derived/hard328-01/`: `readout.json` (every number of the first part), `table.md`, `labels.jsonl` (952 items with
both judges' label, quote and reason, no answer text), `hand.json`, `examples.json` (per model one DERIVED and one ASSERTED
wrong answer with the quote, the reason and the last 1,500 characters; one planted control of each kind), `rubric.md`,
`run.json`. Prompts, raw replies and token usage: `runs/derived/` (not committed).

```
P="uv run --no-project --with numpy --with math-verify==0.9.0 --with anthropic --with brotli>=1.2.0 python -m studies.rlneurons.analysis.derived"
$P prep --runs runs --work runs/derived-02
$P judge --work runs/derived-02 --judge A    # also B and F; the hand labels go to runs/derived-02/hand.json first
$P score --work runs/derived-02 --out studies/rlneurons/results/derived/hard328-02
$P score --per-sample --out studies/rlneurons/results/derived/hard328_persample-02   # addendum 1; reads hard328-01/labels.jsonl, no judge call
```

## Outside math and code: MMLU-Pro and BBH (500 items, T 1.0, one sample, board work-8cde9c)

Question: every configuration here was chosen on MATH-500; do its gains appear on benchmarks that are neither math nor code?
Answer: yes. The Math cue, unchanged, takes the untrained base from 136 to 286 of 500 (+30.0 points [24.6, 35.4]), 77 % of
what RL-Zero-Math gains there (332), against 78 % on MATH-500 and 58 % on code. Spec `specs/SPEC_ood1.md` (written before the
runs; amendment 1 adds grader v2). Items `data/ood1/ood1_items.json` (250 MMLU-Pro from the 9 categories outside math, physics,
chemistry, engineering and computer science; 250 BBH from 10 one-letter tasks; built by `prep/ood1_build.py`, seed 0), prompt
= the math prompt `pair1` unchanged, cap 16,384, seed 61000000 + index. `jobs/run_mcq_cell.py` -> `analysis/ood1_readout.py`
-> `results/ood1/readout.json` and one folder per cell (`run.json`, `metrics.json`, `examples.json`). Grader `lib/mcq_lib.py`
(tests `lib/mcq_lib_test.py`). Raw answers: `runs/<job>/answers.jsonl` in frustea's Modal workspace (not committed).
Paired bootstrap, 5,000 resamples, in points.

| Cell | Right of 500, grader v2 | MMLU-Pro of 250 | BBH of 250 | No letter (v2) | Cap hits | Tokens per item | Right, grader v1 | Job |
|---|---|---|---|---|---|---|---|---|
| base, plain | 136 (27.2 %) | 48 | 88 | 214 | 3 | 992 | 114 | `frustea-1115-070655-258c` |
| base, Math cue | 286 (57.2 %) | 116 | 170 | 30 | 1 | 2,049 | 229 | `frustea-1115-070659-494e` |
| RL-Zero-Math, plain | 332 (66.4 %) | 133 | 199 | 13 | 0 | 3,165 | 78 | `frustea-1115-070704-88e2` |
| Think-SFT, Math cue | 342 (68.4 %) | 137 | 205 | 6 | 4 | 2,941 | 332 | `frustea-1115-070709-bf07` |

- Chance is 28.4 of 250 (MMLU-Pro) and 67.9 of 250 (BBH): the plain base is near chance on BBH because 214 of its 500
  answers give no letter (empty, a continuation of the prompt, or text without an answer).
- H1 held under both graders: cue minus plain base +30.0 [24.6, 35.4] (v2), +23.0 [17.6, 28.4] (v1); MMLU-Pro +27.2
  [19.6, 34.4], BBH +32.8 [24.4, 40.8] (v2).
- H2: RL on math transfers, +39.2 [34.0, 44.2] over the plain base (v2). Under v1, the grader of the spec, RL scores 78 and
  H2 reads as refuted: RL-Zero-Math writes its answer as `\boxed{X}` in most answers, which v1 does not read. v1 is not a
  valid instrument for this model; v2 was added from cells 1 and 2 before cell 3 was read.
- H3 held (v2): the cue gives 150 of RL's 196 problems over the plain base (77 %). RL stays ahead of the cued base by 9.2
  [4.6, 13.8] at 3,165 against 2,049 tokens per item.
- H4 held: Think-SFT + cue minus RL +2.0 [-2.4, 6.2] (v2).
- Not run: the vote over four samples, RL with the cue, Think-SFT plain. One seed. The 500 items are a sample of each
  benchmark, not the full sets, so the counts are not comparable to published MMLU-Pro or BBH scores.

## The 1.5x top-8 edit, replicated with four samples on the 328 (hard328, n = 328, cue, T 1.0, grader v3, board work-ab0f72)

Question: base + 1.5 times the top 8 directions of (RL-Math - base) scored 203 of 328 on one sample (board result-6f1bb7),
and 1.5 was the best of seven sizes tried on the 328. Does it hold on new samples? Answer: yes for one sample, not fully under
the vote. Four samples: 207, 198, 199, 197, mean 200.25 (RL plain 200.0: 207, 190, 209, 194). Vote over 4: 214 of 328 at
35,593 tokens per problem, 2.1 points [-5.2, +0.6] below RL's vote (221) and 6.7 points [3.4, 10.4] above the base's (192).
Under the vote the edit alone is right on 8 problems, RL alone on 15. MATH-500, one sample: 456 of 500, 7 cap hits (RL 457,
base + cue 410; job `abaybektursun-1115-055652-3a2d`).

Job `abaybektursun-1115-055641-b417` (`--model-label top8x1.5_math31 --prompt cue --set hard328 --samples 4 --seed 3000000`,
no restarts; cap hits per sample 20, 14, 20, 22, against 71, 66, 81, 68 for the base and 35, 26, 24, 29 for RL). Readout
`analysis/day1_vote.py --minus` the RL readout: `results/day1_3/hard328_top8x1.5_cue_s4-01/`. The edit uses the RL
checkpoint's weights, so it is not a route without reward; its size was chosen on the 328, and these four samples are new
draws on the same problems, not a held-out set (MATH-500 is the held-out reading).

## xreward: what RL runs with different rewards write into the same base (board work-4fa42e, idea-ac4e14)

Spec `specs/SPEC_xreward.md` (written before each run; amendments 1 to 4). Branch `sharedsub`.

| File | What it does |
|---|---|
| `jobs/xreward_overlap.py` | Weights only. Top-8 singular subspaces of (model - base) for seven RL-Zero models, Think-SFT and the base matrix itself, per layer matrix (224), and every pairwise overlap; `--steps` adds the step-100 checkpoint of each RL run. Selftest with a planted shared subspace. |
| `analysis/xreward_overlap.py` | Readout of the overlap job: key-by-key tables, by module type, nearest neighbours, X1 to X3, S1, S2. |
| `jobs/wsp_edit.py` | Edited weights. Added here: `--mods` (module filter), `--scale`, recipes `proj` / `projc` (the top-k edit split by a donor model's input subspace), `--other` / `--donor` keys of `xreward_overlap.MODELS`; selftest checks 7 to 9. |
| `analysis/xreward_edits.py` | Paired readout of the edit cells on the 328 against base cue, RL, theta(0.25), theta(0.5), Code-RL. |
| `results/xreward/overlap-01/` | `readout.json`, `run.json` of job `abaybektursun-1114-220151-daaa` (final models). Raw per-matrix rows (3 MB): `runs/<job>/metrics.json`, Volume `iterate-runs`. |
| `results/xreward/overlap_steps-01/` | The same with the seven step-100 checkpoints, job `abaybektursun-1114-221259-0871`. |
| `results/xreward/edits/` | `readout.json` and one run folder per cell (`run.json`, `metrics.json`, `edit.json`, `examples.json`). |

### Part 1: overlap of the top-8 subspaces (weights only, 224 layer matrices)

Overlap = ||Va^T Vb||_F^2 / 8 for the input (right) side, the same with U for the output side; a random 8-dimensional subspace
gives 0.002. Means over the 224 matrices, `results/xreward/overlap-01/readout.json`, key `tables`.

| Pair | Input side | Output side |
|---|---|---|
| Math 3.0, Math 3.1 | 0.476 | 0.098 |
| Code 3.0, Code 3.1 | 0.425 | 0.082 |
| Math 3.1, Code 3.1 | 0.260 | 0.096 |
| Math 3.1, Code 3.0 | 0.218 | 0.072 |
| IF, General | 0.187 | 0.049 |
| Mix with IF / Code 3.0 / General / Math 3.0 | 0.380 / 0.306 / 0.244 / 0.197 | 0.120 / 0.099 / 0.069 / 0.061 |
| Math 3.1, IF | 0.026 | 0.030 |
| Math 3.1, General | 0.045 | 0.047 |
| Math 3.1, Think-SFT | 0.109 | 0.051 |
| Math 3.1, the base matrix's own top-8 | 0.042 | 0.018 |

- The RL runs do not share one subspace. Math and Code share one; IF and General share another; Mix overlaps every ingredient.
  Math against IF or General is below Math against Think-SFT.
- Each release pair is the other's nearest neighbour (4 of 4), so the reward is readable from the weights of another run.
- The sharing is on the input side, 3 to 5 times the output side.
- X1 (RL pairs above RL-SFT pairs): 0.186 against 0.063 on average, 14 of 21 pairs. X2 held (base matrix 0.037). X3: Spearman of the
  overlap with Math 3.1 against the MATH-500 cue score 0.77, n 6; Code 3.0 overlaps 0.218 and gains nothing.
- Step 100 (`overlap_steps-01`, differences of 0.03 to 0.19 % of the weight norm): for each step-100 checkpoint the nearest final
  model of another run is the other release of its reward (Math, Code) or Mix (IF, General); Mix is nearest General (6 of 7 as
  predicted, S1 held). Mean input-side overlap between a reasoning run and an instruction run at step 100: 0.076 (finals 0.049), S2 held.

### Part 2: rank-8 edits with the cue on the 328 harder problems

T 1.0 / top-p 1.0, seed 3000000, one sample, grader v3, `results/xreward/edits/readout.json`. Edits are 0.074 % of the weight norm
(Math) and carry 9.8 % of the squared norm of the difference; effective scale after BF16 rounding 1.000.

| Cell | Right of 328 | Cap hits | Minus base cue, points [95 %] | Run folder, job |
|---|---|---|---|---|
| base, cue | 164 | 77 | | `results/day1/hard328_base_cue_t10-01/` |
| base + matched random rank-8, cue | 158 | 67 | -1.8 [-5.8, 2.4] | `edits/rand8_math31-01/`, `abaybektursun-1114-221040-5f1e` |
| base + Math 3.1 top-8, cue | 192 | 46 | +8.5 [4.3, 12.8] | `edits/top8_math31-01/`, `abaybektursun-1114-221034-007d` |
| base + Code 3.1 top-8, cue | 178 | 41 | +4.3 [0.3, 8.2] | `edits/top8_code31-01/`, `abaybektursun-1114-221053-fb3f` |
| Math 3.1 minus its top-8, cue | 190 | 90 | +7.9 [3.7, 12.2] | `edits/bulk_math31-01/`, `abaybektursun-1114-221100-1e31` |
| RL, plain | 206 | 20 | +12.8 | `results/day1/hard328_rl_plain_t10-01/` |

- Math top-8 minus the random control: +10.4 points [5.8, 14.9]. Minus RL: -4.3 [-8.2, -0.3]. Minus theta(0.5) (190): +0.6 [-3.4, 4.6].
- Math 3.1 minus its top-8, against RL cue (205): -4.6 [-8.2, -1.2]. P2 of amendment 1 (the rest keeps the gain) is refuted.
- Each half alone solves 30 of the 49 problems that RL solves and the cued base does not; 19 are the same problems, which is what
  independent resampling gives (18.4), and RL with the cue at another seed solves 37 of them. The two halves are not additive
  (28 + 26 problems against RL's 42) and fix the same kinds of problems: of the base's 90 finished wrong answers 27 and 26, of its
  74 wrong cap hits 14 and 13.
- Cap hits fall with the 8 directions (77 to 46) and rise without them (90 against RL cue 25). They are not repetition loops: rules A
  and B flag 0 cap hits in every cell, and 13 read by hand are all still working at the cap. The 90 has no control yet: the cell
  carries BF16 rounding noise (norm 2.26 against 4.05 for the whole difference) that RL does not.
- Audit by a second agent from the raw rows (work-4fa42e): all seven counts recomputed with `grade_v3`, same 328 problems, prompts
  and seeds 3,000,000 + index in the paired cells (RL cue and theta(0.5) use other seeds); 24 answers read by hand, one lenient
  match (`(4, \log 2)` for `(4, \log_{10} 2)` in the minus-top-8 cell). The clean contrast is top-8 against the random control:
  both carry the rounding noise (written norm 2.60 and 2.67 for an addition of 1.27), the base cell does not.
- Raw rows (read by a subagent, not committed): with the top-8 edit `Wait` rises from 9.2 to 12.3 per 1,000 words (RL 12.9) and
  finished answers with no boxed answer fall from 22 to 1.

#### Second batch (amendments 3 and 4): rank, module family, scale, shared input subspace, control for the minus-top-8 cell

Same settings, edits of Math 3.1 unless named, `--rounding stochastic --seed 0`. "Right per finished" = right / (328 - cap hits).

| Cell (`wsp_edit` arguments) | Right of 328 | Cap hits | Right per finished | Minus random rank-8, points [95 %] | Edit, % of weight norm | Run folder, job |
|---|---|---|---|---|---|---|
| base, cue | 164 | 77 | 0.65 | | | |
| 1 direction per matrix (`top8 --k 1`) | 181 | 51 | 0.65 | +7.0 [2.4, 11.3] | 0.048 | `edits/top1_math31-01/`, `abaybektursun-1115-000358-d11a` |
| 8 directions (first batch) | 192 | 46 | 0.68 | +10.4 [5.8, 14.9] | 0.074 | `edits/top8_math31-01/` |
| 64 directions (`top8 --k 64`) | 200 | 42 | 0.70 | +12.8 [8.5, 17.4] | 0.115 | `edits/top64_math31-01/`, `abaybektursun-1115-003755-b90d` |
| 8 directions, attention only (`--mods q,k,v,o`) | 178 | 59 | 0.66 | +6.1 [1.8, 10.4] | 0.103 | `edits/top8attn_math31-01/`, `abaybektursun-1115-012835-a431` |
| 8 directions, MLP only (`--mods gate,up,down`) | 181 | 40 | 0.63 | +7.0 [2.7, 11.3] | 0.059 | `edits/top8mlp_math31-01/`, `abaybektursun-1115-012846-905e` |
| 8 directions at twice the size (`--scale 2`) | 190 | 5 | 0.59 | +9.8 [5.5, 14.0] | 0.148 | `edits/top8x2_math31-01/`, `abaybektursun-1115-012855-d7ed` |
| 8 directions, part reading Code 3.0's input subspace (`proj --donor code30`) | 171 | 54 | 0.62 | +4.0 [-0.6, 8.5] | 0.040 | `edits/proj_math31_code30-01/`, `abaybektursun-1115-012905-8f73` |
| 8 directions, the rest (`projc --donor code30`) | 176 | 69 | 0.68 | +5.5 [0.9, 10.1] | 0.062 | `edits/projc_math31_code30-01/`, `abaybektursun-1115-012915-6618` |
| Code 3.0's own 8 directions (`top8 --other code30`) | 173 | 23 | 0.57 | +4.6 [0.0, 8.8] | 0.107 | `edits/top8_code30-01/`, `abaybektursun-1115-012925-b15d` |
| Math 3.1 minus a matched random rank-8 (`rbulk`) | 195 | 33 | 0.66 | | | `edits/rbulk_math31-01/`, `abaybektursun-1115-012935-2836` |
| Math 3.1 minus its 8 directions (first batch) | 190 | 90 | 0.80 | | | `edits/bulk_math31-01/` |
| RL, plain | 206 | 20 | 0.67 | | | |

Against the predictions of amendments 3 and 4:

- Rank: 1 direction 181 (predicted 170 to 180), 64 directions 200 (predicted 192 to 200). 64 directions against RL: -1.8 points
  [-5.5, 1.8]. The steps 1 to 8 (+3.4 [-1.2, 7.9]) and 8 to 64 (+2.4 [-1.5, 6.4]) are each inside the noise of one sample.
- Module family: MLP 181, attention 178, difference +0.9 [-3.0, 4.9]. "One module family carries it" is refuted; the predicted
  MLP lead is not shown.
- Scale 2: 190 right, 5 cap hits. The predicted 195 to 206 is refuted; the fall of cap hits (46 to 5, RL 20) is far larger than
  predicted. On the 77 problems where the cued base hits the cap (3 right), the cells finish and answer: 8 directions 25 cap hits,
  17 right, 36 finished wrong; twice the size 0 cap hits, 14 right, 63 finished wrong; RL 11, 19, 47. Three of the 63 read by
  hand end in a boxed answer after an unfinished argument ("After testing various values, we find ...").
- So the 8 directions mainly make the model finish with an answer. Cap hits follow their size in both directions: removed from
  RL 90, base 77, one direction 51, eight 46, twice the size 5. Right answers per finished answer stay near 0.65 and fall to
  0.59 at twice the size; RL minus the directions finishes least and is right most often when it does (0.80).
- Control for the minus-top-8 cell (amendment 4): RL minus a random rank-8 scores 195 with 33 cap hits. Against the minus-top-8
  cell: +1.5 points [-2.1, 5.2] and 57 fewer cap hits. So the loss of right answers in the minus-top-8 cell (190 against 205) is
  not separable from the perturbation; the rise in cap hits (90 against 33) is the 8 directions.
- Shared input subspace: the part of the edit that reads Code 3.0's input subspace 171, the rest 176, difference -1.5
  [-6.1, 3.4]. "The shared input directions carry the gain" is refuted; neither part reaches the whole edit (192).
- Code 3.0's 8 directions: 173 right, 23 cap hits, right per finished 0.57. They also make the model finish, with fewer right answers.
- Correction after review (comment on result-51a0e7): "finish, not be right" overstates it. Split by the base's own outcome, half
  of the gain is on problems the base finishes. On those 251 (base 161 right): random rank-8 149, one direction 166, eight 175
  (+5.6 points against base [0.8, 10.8], +10.4 against random [4.8, 15.9]), 64 directions 182, twice the size 176, RL 187. On the
  77 the base leaves at the cap (3 right): 9, 15, 17, 18, 14, 19. Conditioning on the base's finished sample favours the base, so
  the +5.6 is a lower bound. The directions make the model finish and also raise right answers where it already finished; only
  the step from size 1 to 2 adds finishing without right answers (175 to 176, 17 to 14).
- One sample per cell: contrasts under about 5 points are not resolved.

#### The finish dial (amendment 5, work-e02ba4): the 8 directions at seven sizes, a random edit at four

Same settings. "On 251" = right on the 251 problems the cued base finishes (base 161). "No box" = finished answers without `\boxed`.

| Size | Math 3.1's 8 directions: right of 328 | cap hits | on 251 | no box | Random rank-8: right | cap hits | Run folders (`edits/`) |
|---|---|---|---|---|---|---|---|
| -1 | 118 | 96 | 113 | 61 | 159 | 71 | `top8xm1_math31-01/` (`abaybektursun-1115-031209-1273`), `rand8xm1_math31-01/` (`...031249-1dcd`) |
| 0 (base) | 164 | 77 | 161 | 23 | | | |
| 0.5 | 170 | 50 | 156 | 7 | | | `top8x0.5_math31-01/` (`...031219-19af`) |
| 1 | 192 | 46 | 175 | 2 | 158 | 67 | first batch |
| 1.5 | 203 | 25 | 184 | 2 | | | `top8x1.5_math31-01/` (`...031229-5991`) |
| 2 | 190 | 5 | 176 | 4 | 167 | 70 | `top8x2_math31-01/`, `rand8x2_math31-01/` (`...031304-cf34`) |
| 3 | 117 | 9 | 115 | 113 | 163 | 79 | `top8x3_math31-01/` (`...031240-1106`), `rand8x3_math31-01/` (`...031315-b328`) |
| RL | 206 | 20 | 187 | 0 | | | |

- D1 (cap hits fall with size) held in order: 96, 77, 50, 46, 25, 5, 9. The predicted values at the ends were missed (above 100 at
  -1: 96; at most 2 at 3: 9).
- D2 (the directions, not the size of a perturbation) held: the random edit has 67 to 79 cap hits and 158 to 167 right at every
  size, including 3 times the size (0.22 % of the weight norm).
- D3 (right answers peak between 1 and 1.5, below the base at -1 and 3) held: 203 at 1.5, which is -0.9 points from RL [-4.9, 2.7]
  and +13.7 points above the random edit [9.2, 18.3]; 118 at -1 and 117 at 3.
- Raw answers. At -1 the model stops boxing its answer (61 finished answers without a box, base 23; they end "Answer: 27") and is
  wrong more often when it finishes (0.51 right per finished, base 0.65). At 3 it finishes but 113 answers decay into strings of
  function words. So the 8 directions carry three things that move together: finishing, the boxed answer format, and right
  answers on problems the base already finishes (113, 161, 175, 184 at -1, 0, 1, 1.5).
- One sample per cell; 1.5 against 1 is +3.4 points [-0.9, 7.6].

Replication of size 1.5 (work-ab0f72, board result-95a4dc; 1.5 was the best of seven sizes on one sample of the 328, so it is
scored again here):

| Cell | Base + 8 directions at 1.5 | RL, plain | Base, cue | 1.5 minus RL, points [95 %] | Run folder, job |
|---|---|---|---|---|---|
| 328, four samples, each | 207, 198, 199, 197 (mean 200.25) | mean 200.0, sample 0 207 | mean 158.5 | sample 0: 0.0 [-4.0, 4.0] | `results/xreward/dial15_s4_vs_rl_plain-01/`, `abaybektursun-1115-055641-b417` |
| 328, vote over 4 | 214 | 221 | 192 | -2.1 [-5.2, 0.6]; minus base +6.7 [3.4, 10.4] | the same; against base `dial15_s4_vs_base_cue-01/` |
| 328, right in any of 4 | 235 | 240 | 207 | -1.5 [-4.3, 1.2] | the same |
| 328, cap hits per sample | 20, 14, 20, 22 | | | | the same |
| MATH-500, one sample | 456 | 456 (four samples 456 to 464) | 405 (405 to 418) | 0.0 [-2.2, 2.2] | `results/xreward/dial15_math500-01/`, `abaybektursun-1115-055652-3a2d` |

Readout `analysis/day1_vote.py` with `--minus` (references `results/day1_3/`). One sample of the edited base equals one sample of
RL on both sets; under the vote over four it is 7 problems behind RL. The edit is derived from the RL weights: it compresses the
RL difference (8 directions per matrix, 0.11 % of the weight norm as intended; the written BF16 change is 0.19 % because of
rounding noise), it does not reach RL without RL. No random-edit cell exists at size 1.5 (sizes 1 and 2: 158 and 167).

Two controls (amendment 6, work-e1b23a), one sample each:

| Cell | Right of 328 | Cap hits | On 251 | No box | Minus base cue, points [95 %] | Run folder, job |
|---|---|---|---|---|---|---|
| random rank-8 at size 1.5 (0.111 % of the weight norm) | 159 | 74 | 152 | 24 | -1.5 [-5.8, 2.7] | `edits/rand8x1.5_math31-01/`, `abaybektursun-1115-090241-0229` |
| Think-SFT's 8 directions at Math's edit norm (`--scale 0.02`, 0.074 %) | 156 | 75 | 149 | 23 | -2.4 [-6.4, 1.5] | `edits/top8x0.02_think_sft-01/`, `abaybektursun-1115-090252-65bf` |

Both predictions held. The random edit is flat at all five sizes (-1, 1, 1.5, 2, 3: 67 to 79 cap hits, 158 to 167 right). The
largest 8 directions of Think-SFT's difference, at the size at which Math's give 192 right and 46 cap hits, change nothing (-11.0
points against Math's [-15.6, -6.4]): fine-tuning on reasoning traces does not write the finishing directions into its largest
directions. Limit: these are the top 8 of a difference 50 times larger than Math's, 2 % of its squared norm.

Which reward writes the finishing directions (8 directions of each model added to the base):

| Donor | Right of 328 | Cap hits | No box | Edit, % of weight norm | Run folder, job |
|---|---|---|---|---|---|
| Math 3.0 | 182 | 43 | 1 | 0.078 | `top8_math30-01/`, `abaybektursun-1115-031326-369f` |
| Math 3.1 | 192 | 46 | 2 | 0.074 | first batch |
| Code 3.1 | 178 | 41 | 12 | 0.064 | first batch |
| Code 3.0 | 173 | 23 | 7 | 0.107 | second batch |
| IF | 155 | 41 | 158 | 0.107 | `top8_if30-01/`, `abaybektursun-1115-031336-56ff` |
| General | 164 | 88 | 14 | 0.038 | `top8_general30-01/`, `abaybektursun-1115-031346-5113` |
| Think-SFT | 0 | 327 | | 3.68 | `top8_think_sft-01/`, `abaybektursun-1115-031356-77f0` |

- R1 is refuted for IF: its 8 directions cut cap hits as far as Math's (41), by ending early with an unboxed "Answer: 27" (158 of
  287 finished answers have no box, median 2,140 tokens; 108 of the 152 with an answer marker are right). Math 3.0 behaves as
  Math 3.1 (43 cap hits, 182 right, +7.3 points above the random edit [2.7, 11.6]). General's edit changes nothing in right answers.
- Finishing is therefore written by the Math, Code and IF rewards alike; what the reasoning rewards add is the boxed format and
  right answers.
- The Think-SFT cell is not a test: its top-8 edit is 3.7 % of the weight norm (50 times Math's) and the model writes commas
  until the cap. A norm-matched Think-SFT edit is open.

#### The smallest edit (amendment 8, work-d80b27): one larger direction, and three layer bands

Same settings as the dial (hard328, cue, one sample). `wsp_edit --layers lo-hi` restricts the edit to those layers.

| Cell | Right of 328 | Cap hits | On 251 | No box | Right per finished | Edit, % of weight norm | Run folder (`edits/`), job |
|---|---|---|---|---|---|---|---|
| 1 direction per matrix at 1 (second batch) | 181 | 51 | 166 | | 0.65 | 0.048 | `top1_math31-01/` |
| 1 direction at 2 | 184 | 23 | 169 | 8 | 0.60 | 0.097 | `top1x2_math31-01/`, `abaybektursun-1115-105247-1603` |
| 1 direction at 3 | 168 | 10 | 157 | 67 | 0.53 | 0.145 | `top1x3_math31-01/`, `abaybektursun-1115-105259-789c` |
| 8 directions at 1.5, layers 0 to 10 | 184 | 98 | 169 | 2 | 0.80 | 0.107 | `top8x1.5_L0-10_math31-01/`, `abaybektursun-1115-105312-7e19` |
| 8 directions at 1.5, layers 11 to 21 | 183 | 49 | 168 | 12 | 0.66 | 0.101 | `top8x1.5_L11-21_math31-01/`, `abaybektursun-1115-105324-5f61` |
| 8 directions at 1.5, layers 22 to 31 | 166 | 57 | 156 | 15 | 0.61 | 0.126 | `top8x1.5_L22-31_math31-01/`, `abaybektursun-1115-105335-a886` |
| 8 directions at 1.5, all layers | 203 | 25 | 184 | 2 | 0.67 | 0.111 | `top8x1.5_math31-01/` |

- M1 refuted: one larger direction does not reach 187. Making it larger keeps cutting cap hits (51, 23, 10) while right answers
  stay (181, 184) and then fall (168, with 67 unboxed answers). The first direction carries finishing; the right answers of the
  8-direction edit (192 to 203) need the other seven.
- M2 refuted: no band reaches 185 and two bands are above 180. The bands differ in kind, not only in size:
  layers 0 to 10 add right answers (184; 169 on the 251, +7.9 points above the random edit [3.7, 12.2]) and raise cap hits to 98
  (base 77), so 0.80 of the finished answers are right, the same profile as RL minus its 8 directions (190 right, 90 cap hits,
  0.80); layers 11 to 21 add right answers and cut cap hits (183, 49); layers 22 to 31 cut cap hits (57) with no gain in right
  answers (166, +2.4 above random [-2.4, 7.3]).
- So on math finishing and right answers come apart by rank (the first direction finishes, the rest add right answers) and, in
  these one-sample cells, by depth. The split by depth did not hold on the Code pair (next section). No edit smaller than 8
  directions in all layers reached 190.
- One sample per cell; differences under about 5 points are not resolved.

#### The depth split tested on the Code pair (amendment 9, work-b5f51c): two of three predictions refuted

Code 3.1's 8 directions at 1.5 in one band of layers, HumanEval+ and MBPP+ (538), Code cue, one sample; readout
`code1_readout --out=xreward/code_depth` -> `results/xreward/code_depth/readout.json`.

| Cell | Passed of 538 | Cap hits | No code block | Minus random edit, points [95 %] | Run folder (`results/xreward/code_depth/`), job |
|---|---|---|---|---|---|
| base, Code cue | 317 | 27 | 34 | | |
| random rank-8 at 1.5, all layers | 331 | 27 | 45 | | `../code_dial/code_rand8x1.5_code31-01/` |
| layers 0 to 10 | 372 | 12 | 17 | +7.6 [3.5, 11.9] | `code_top8x1.5_L0-10_code31-01/`, `abaybektursun-1115-120127-70c3` |
| layers 11 to 21 | 366 | 6 | 9 | +6.5 [2.2, 10.8] | `code_top8x1.5_L11-21_code31-01/`, `abaybektursun-1115-120138-c4be` |
| layers 22 to 31 | 342 | 34 | 40 | +2.0 [-2.2, 6.1] | `code_top8x1.5_L22-31_code31-01/`, `abaybektursun-1115-120151-bee2` |
| all layers | 399 | 4 | 5 | +12.6 [8.7, 16.7] | `../code_dial/code_top8x1.5_code31-01/` |

- L1 (early layers: right answers without finishing) refuted: 372 passed as predicted, but cap hits fall to 12 (predicted at least 20).
- L2 (late layers: finishing without right answers) refuted: 342 passed as predicted, but cap hits are 34 (predicted at most 14).
- L3 (middle layers: both) held: 366 passed, 6 cap hits.
- What holds on both pairs: the directions in layers 22 to 31 add no right answers (math +2.4 points above the random edit
  [-2.4, 7.3], code +2.0 [-2.2, 6.1]), those in layers 0 to 10 and 11 to 21 each add 6 to 8 points, and no band reaches the
  all-layer edit. What does not hold on code: that early layers leave the model unfinished and late layers make it finish. The
  "split by depth" of amendment 8 is a property of the math cells (one sample each), not of the dial in general.

#### The depth and rank split with more samples and two controls (specs/SPEC_depth3.md, work-3baa2c)

The table above had one sample per cell and its depth reading was made after the run. `SPEC_depth3.md` states the readings as
predictions before the run. Same settings (hard328, n 328, cue, T 1.0 / top-p 1.0, cap 16,384, grader v3), new seeds
(sample s: 3000000 + 10000 s + problem index), each new sample as two `run_cell --shard k/2` jobs. New flag `wsp_edit --skip 1`:
directions 2 to 8 of each matrix (selftest check 10). Readout:
`uv run --no-project --with numpy python -m studies.rlneurons.analysis.depth3_readout` -> `results/xreward/depth3/readout.json`;
per-problem rows of every new sample in `results/xreward/depth3/<cell>_s<sample>-01/rows.jsonl`, of the older one-sample jobs in
`results/xreward/depth3/sample0_rows/`. Raw answers: `runs/<job>/answers.jsonl` (job ids in each `run.json`; `uv run tools/gpu.py get`).
Differences are paired over the 328 problems (per problem, mean over samples), in points of 328, 95 % interval from 10,000
resamples of the problems.

| Cell (base + edit at 1.5, cue) | Samples | Right of 328, mean (each) | Cap hits, mean (each) | Right per finished | Right minus base, points | Cap hits minus base, points |
|---|---|---|---|---|---|---|
| base, cue | 4 | 158.5 (161, 161, 152, 160) | 71.5 (71, 66, 81, 68) | 0.62 | | |
| random rank-8, all layers | 1 | 159 | 74 | 0.63 | +0.1 [-3.2, 3.4] | +0.8 [-3.0, 4.6] |
| random rank-8, layers 0-10 (new) | 1 | 162 | 70 | 0.63 | +1.1 [-2.4, 4.5] | -0.5 [-4.3, 3.5] |
| 8 directions, layers 0-10 | 4 | 183.5 (184, 186, 180, 184) | 92.0 (98, 89, 95, 86) | 0.78 | +7.6 [5.3, 10.0] | +6.2 [3.6, 9.1] |
| 8 directions, layers 11-21 | 2 | 181.0 (183, 179) | 45.0 (49, 41) | 0.64 | +6.9 [4.0, 9.8] | -8.1 [-11.3, -5.0] |
| 8 directions, layers 22-31 | 2 | 163.5 (166, 161) | 56.0 (57, 55) | 0.60 | +1.5 [-1.1, 4.1] | -4.7 [-7.2, -2.1] |
| directions 2 to 8, all layers (new) | 1 | 183 | 69 | 0.71 | +7.5 [4.4, 10.7] | -0.8 [-4.7, 3.1] |
| 8 directions, all layers | 4 | 200.25 (207, 198, 199, 197) | 19.0 (20, 14, 20, 22) | 0.65 | +12.7 [10.2, 15.4] | -16.0 [-19.1, -13.0] |

- B1 held: layers 0-10 add right answers, +7.6 points [5.3, 10.0] (25 problems).
- B2 held, in its stronger reading: layers 0-10 add cap hits, +6.2 points [3.6, 9.1] (92.0 against 71.5). The cap-hit answers
  are not loops (rule A: 0 in every L0-10 sample); 14 of the 368 cap-hit answers were scored right.
- B3 held: against the random rank-8 edit in layers 0-10 (same singular values, sample 1 of each) the L0-10 edit is +7.3 points
  right [3.4, 11.3] and +5.8 points cap hits [0.9, 10.7]; the random edit stays at the base (162 right, 70 cap hits).
- B4 held: layers 22-31 cut cap hits (-4.7 [-7.2, -2.1]) with no resolved gain in right answers (+1.5 [-1.1, 4.1]).
- B5 held: layers 11-21 do both (+6.9 [4.0, 9.8] right, -8.1 [-11.3, -5.0] cap hits).
- R1 held: directions 2 to 8 without direction 1 give 183 right (predicted at least 180) with 69 cap hits (predicted at least
  40; base 71.5): the right-answer gain without any finishing. Against the random all-layer edit: +7.3 [3.0, 11.6] right.
- R2 held: directions 2 to 8 are -5.3 points [-8.3, -2.4] below all 8 in right answers, with +15.2 points [11.2, 19.5] more cap hits.
- Together with the one-direction cells above (direction 1 at 3x: 168 right, 10 cap hits): direction 1 removes cut-off answers,
  directions 2 to 8 add right answers and leave cut-offs at the base's level, and the two parts add up (183 and 181 alone,
  200 together). By depth the early band adds right answers and more cut-offs, the late band only removes cut-offs.
- Limits: one model pair, one benchmark, one sample for each of the two new cells and for the random controls; the bands at
  2 samples. 7 samples instead of the 13 first planned (budget, stated in the spec before the run). Sample 0 of the all-layer
  cell differs between its two jobs with the same seeds (203 and 207): vLLM sampling is not reproducible across jobs.
- Cost: 14 H100 jobs, 6.4 h of `run_cell` wall time (the sum of `wall_s` in the 14 `metrics.json`; 23 to 30 min each) plus
  setup and the edit (about 3 min per job): about 7.2 H100-hours, about 28 USD. The minutes column of `gpu.py ls` is the time
  since submission, not the run time. Smoke job `abaybektursun-1115-122317-6624`: 100 s. 21.8 M generated tokens.

#### The directions on other hosts (amendment 10, work-30f0ed): Think-SFT, and Math + Code in one edit

`wsp_edit --onto <model key or directory>` writes the addition (computed from other - base) onto another model. One sample per cell.

A. Think-SFT as host, hard328, cue, seed 3000000 (references from "Delta transplant": Think-SFT 209.0 right, 94.5 cap hits, four
samples; Think-SFT + dense noise 209; Think-SFT + 2 x the whole RL-Math difference, 0.47 % of the weight norm: 231.5, 54):

| Cell | Right of 328 | Cap hits | Edit, % of weight norm | Run folder (`edits/`), job |
|---|---|---|---|---|
| Think-SFT + random rank-8 at 3 | 213 | 82 | 0.215 | `sft_rand8x3_math31-01/`, `abaybektursun-1115-130307-5e33` |
| Think-SFT + Math 3.1's 8 directions at 1.5 | 220 | 76 | 0.108 | `sft_top8x1.5_math31-01/`, `abaybektursun-1115-130242-4696` |
| Think-SFT + Math 3.1's 8 directions at 3 | 232 | 60 | 0.215 | `sft_top8x3_math31-01/`, `abaybektursun-1115-130255-5098` |

- A1 held: 232 right with 60 cap hits (predicted at least 225, at most 65); the random edit 213 (within 209 +- 9). The 8
  directions at 3 against the random edit at 3: +5.8 points [2.1, 9.8]; against RL plain (206, same seed): +7.9 [4.3, 11.6].
- The 8 directions written onto a model trained without a reward give what twice the whole RL difference gives (231.5), with an
  edit of less than half its norm. Cap hits fall with size on this host too (94.5, 76, 60).

B. Math 3.1's and Code 3.1's 8 directions in one edit of the base (two passes; the first pass's statistics are `edit1.json` of
the job), on hard328 (cue) and on HumanEval+ and MBPP+ (Code cue; readout `results/xreward/code_hosts/readout.json`):

| Edit of the base | Right of 328 | Cap hits | Passed of 538 | Cap hits | Run folders, jobs |
|---|---|---|---|---|---|
| none (cued base) | 164 | 77 | 317 | 27 | |
| Math at 1 | 192 | 46 | | | |
| Math at 1.5 | 203 | 25 | 368 | 1 | |
| Code at 1 / at 1.5 | 178 (at 1) | 41 | 386 / 399 | 9 / 4 | |
| Math at 1 + Code at 1 | 193 | 32 | 411 | 2 | `edits/math1_code1-01/` (`abaybektursun-1115-130346-f701`), `code_hosts/math1_code1-01/` (`...130400-064d`) |
| Math at 1.5 + Code at 1.5 | 191 | 4 | 387 | 0 | `edits/math1.5_code1.5-01/` (`...130320-3e7b`), `code_hosts/math1.5_code1.5-01/` (`...130332-eba9`) |
| Math at 1.5 + random at 1.5 (control) | 197 | 24 | 365 | 1 | `edits/math1.5_rand1.5-01/` (`...130413-750d`), `code_hosts/math1.5_rand1.5-01/` (`...130426-5898`) |
| RL-Math / RL-Code | 206 | 20 | 401 | 8 | |

- B1 is neither met nor refuted: no size gives both at least 198 of 328 and at least 390 of 538 (at 1: 193 and 411), and neither
  size is at or below 186 or 372. B2 held: the control stays at 197 (203 +- 12) and 365 (368 +- 15).
- On code the sum at 1 passes 411: +1.9 points above RL-Code [-1.1, 4.8], +4.6 above Code's directions alone at 1 [1.5, 7.6] and
  +8.6 above the control [5.2, 11.9]. Math's directions add to Code's on code.
- On math the sum at 1 scores 193, the same as Math's directions alone at 1 (192) and +8.8 points above the base [4.6, 13.1];
  Code's directions add nothing on math, and the sum is -3.0 points from Math alone at 1.5 [-7.0, 0.9] and -4.0 from RL-Math
  [-8.2, 0.0]. At 1.5 + 1.5 cap hits fall to 4 and 0 and right answers fall (191 and 387): the two edits add up in finishing, as
  one edit at twice the size does.
- So one edit of about 0.10 % of the weight norm (Math 0.074 % + Code 0.064 %) gives the base 193 of 328 on math and 411 of 538
  on code, against 164 and 317 for the base and 206 and 401 for the two RL models.

More samples of the two headlines (amendment 11, work-f58d89); both predictions held:

| Cell | Seed 51000000 | 52000000 | 53000000 | Mean of 538 | Run folders, jobs |
|---|---|---|---|---|---|
| base + Math at 1 + Code at 1 | 411 | 407 | 401 | 406.3 | `results/xreward/code_hosts_s52/`, `code_hosts_s53/` (`abaybektursun-1115-143215-6942`, `...143301-ec55`) |
| base + Code at 1 | 386 | 397 | 391 | 391.3 | the same (`...143231-15bb`, `...143316-628e`) |
| RL-Code, plain | 401 | 395 | 403 | 399.7 | the same (`...143247-929d`, `...143331-10da`) |

- E1 held (mean at least 398 and at least 10 above Code alone). Paired over problems, three seeds each: the sum minus Code alone
  +2.8 points [1.0, 4.6]; the sum minus RL-Code +1.2 [-0.6, 3.0]; Code alone minus RL-Code -1.5 [-3.5, 0.3].
- E2 held: Think-SFT + Math's 8 directions at 3, seed 3100000: 240 right, 42 cap hits (`edits/sft_top8x3_math31-02/`,
  `abaybektursun-1115-143344-809f`; the readout `xreward_edits` holds the seed-3000000 cell). Two samples: 232 and 240, mean 236.0, against Think-SFT's
  four samples (209.0): +8.2 points [5.6, 11.0]. The whole-difference transplant at 2 has 234 and 229 on the same two seeds.

#### The dial on a second model pair and benchmark (amendment 7, work-df5e0a)

Base + the 8 directions per matrix of (Code 3.1 minus base), on HumanEval+ and MBPP+ (538 scored problems), Code cue, T 1.0 /
top-p 1.0, seed 51000000, one sample. `jobs/run_code_cell.py --model-path` after `wsp_edit`; readout
`python -m studies.rlneurons.analysis.code1_readout --out=xreward/code_dial @base_cue=<job> ...` ->
`results/xreward/code_dial/readout.json` (references: the cells of "Code pair").

| Cell | Passed of 538 | Cap hits | No code block | Minus cued base, points [95 %] | Run folder (`results/xreward/code_dial/`), job |
|---|---|---|---|---|---|
| base, Code cue | 317 | 27 | 34 | | `results/code1/base_cue-01/` |
| base + random rank-8 at 1.5 | 331 | 27 | 45 | +2.6 [-1.3, 6.3] | `code_rand8x1.5_code31-01/`, `abaybektursun-1115-101457-ef2c` |
| base + Code's 8 directions at 1 | 386 | 9 | 8 | +12.8 [8.9, 16.7] | `code_top8_code31-01/`, `abaybektursun-1115-101423-4a7d` |
| at 1.5 | 399 | 4 | 5 | +15.2 [11.2, 19.3] | `code_top8x1.5_code31-01/`, `abaybektursun-1115-101434-4511` |
| at 2 | 394 | 0 | 0 | +14.3 [9.9, 18.6] | `code_top8x2_code31-01/`, `abaybektursun-1115-101445-e35e` |
| base + Math 3.1's 8 directions at 1.5 | 368 | 1 | 6 | +9.5 [5.2, 13.6] | `code_top8x1.5_math31-01/`, `abaybektursun-1115-101508-33f0` |
| RL-Code, plain | 401 | 8 | 8 | +15.6 [11.5, 19.9] | `results/code1/rl_plain-01/` |

- C1 held: 386 and 399 (predicted at least 345 and 360); the random edit 331 (within 317 +- 15). Code's directions at 1.5 against
  RL-Code: -0.4 points [-3.5, 2.8]; against the random edit: +12.6 [8.7, 16.7].
- C2 held: cap hits 27, 9, 4, 0 and answers with no code block 34, 8, 5, 0 at sizes 0, 1, 1.5, 2; the random edit 27 and 45.
- C3 held: Math's directions at 1.5 pass 368 on code (predicted at least 335), +6.9 points above the random edit [2.4, 11.3] and
  -6.1 below RL-Code [-10.0, -2.4].
- The sizes were fixed before the run (1.5 came from the math dial); one sample per cell, so 1, 1.5 and 2 are not separated.

#### Lengths, token budgets and a restart cascade from the stored rows (work-e02ba4, laptop)

`analysis/xreward_lengths.py` -> `results/xreward/lengths-01/readout.json` (prediction in the module docstring, written first).

- Lengths, on problems both the base and the cell finish (tokens, base p10 / p50 / p90 -> cell): 8 directions 1,252 / 5,513 /
  14,398 -> 1,654 / 6,094 / 14,816; 64 directions 1,270 / 5,652 / 14,299 -> 2,186 / 6,487 / 13,610; twice the size 1,297 / 6,409 /
  14,487 -> 2,107 / 7,088 / 12,308; RL 1,295 / 6,174 / 13,532 -> 2,401 / 7,718 / 13,532; random rank-8 unchanged (ratio 1.00).
  The prediction "median within 10 %, only the tail falls" is refuted: short and median answers get longer (p10 +32 to +72 %),
  and only the long tail gets shorter, clearly so only at twice the size (p90 -15 %).
- Right of 328 within a budget of C tokens (stored run cut at C): at 4k base 81, 8 directions 78, 64 directions 66, RL 69; at 12k
  150, 169, 181, 179; at 16,384 164, 192, 200, 206. Below 4k tokens the base leads.
- Cascade: 64 directions cut at C, unfinished problems restart with the twice-size edit: 196 (C 8k), 204 (12k), 207 (14k; +0.3
  points against RL [-3.4, 4.0]) at 11,696 to 12,392 mean tokens, against RL alone 206 at 9,316. The same cascade restarting with
  the random-edit cell: 178, 194, 198. With RL cue as the restart: 206, 208, 207. The cascade reaches RL's count with no RL
  weights beyond 64 directions per matrix, at 26 % more tokens; it is not a saving.
- Truncating a stored run at C estimates a cap-C run; RL cue uses another seed base.

Run: `uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.xreward_edits`, after
`uv run tools/gpu.py get <job>` for the jobs it names.

#### xshift: the edits in activation space (spec `specs/SPEC_xshift.md`, branch `trace`)

The claim "edits that are orthogonal in weight space shift the residual stream along one shared direction, whose projection
predicts cap hits" is refuted: P1 refuted, P3 refuted for IF, P2 held.

| File | What it does |
|---|---|
| `jobs/xshift.py` | One H100 job, no generation. Base in float32; 48 stored base + cue answers of hard328 (24 cap hits, 24 finished, first 2,048 answer tokens, every 16th position: 6,144 positions); each of 28 scored edits is added to the weights in memory (float32, no rounding), the residual stream at the output of every layer is compared with the base's, the weights are restored. Selftest on the real model: zero edit, restore, addition = `wsp_edit.target`, planted direction. |
| `analysis/xshift.py` | numpy readout: P1 to P3, per-edit rows, cosine matrix, logit lens. |
| `results/xshift/run-01/` | `readout.json`, `run.json`, `metrics.json` (per edit, group, layer), `examples.json`. Job `abaybektursun-1115-130144-40a0`, commit `b053152`, 24 min. Mean shift vectors (39 MB): `runs/<job>/shifts.npz`, not committed. |

Run: `uv run tools/gpu.py submit h100 --hours 2 -- "python -m studies.rlneurons.jobs.xshift --commit $(git rev-parse HEAD)"`, then
`uv run tools/gpu.py get <job>` and `uv run --no-project --with numpy python -m studies.rlneurons.analysis.xshift --job <job>`.

All numbers at layer 24 (0-based, fixed before the run), `results/xshift/run-01/readout.json`; the base residual's RMS norm there is 41.2.

- P1 refuted. Spearman correlation over the 23 non-random edits between the projection (key `P1`; Math 3.1 cells on Code 3.1's
  direction, the others on Math 3.1's) and the stored cap hits: -0.67 (predicted at most -0.8). The plain norm of the mean shift
  gives -0.62, inside the 0.05 margin. Best layer 20 to 21: -0.76. The layers 0-10 band at 1.5 breaks any single-direction
  reading: projection +0.37, 98 cap hits.
- P2 held. The five random edits project 0.0002 to 0.0005 of Math-1x's norm on its direction. A random rank-8 edit of the same
  weight norm moves the residual 95 times less than the 8 singular directions: RMS shift 0.066 against 6.23 (keys
  `edits.rand8_math31.rms_shift`, `edits.top8_math31.rms_shift`). Think-SFT at 0.02, also norm-matched: 0.75.
- P3: IF part refuted, cosine with Math 3.1 0.09 (predicted above 0.5); Think-SFT 0.02 -0.02 and General 0.24 as predicted
  (below 0.3).
- Donors do not share a mean direction (key `cosine_at_layer`): Math 3.1 with Code 3.1 0.37, with Math 3.0 0.29, with Code 3.0
  0.18; Code 3.1 with Code 3.0 0.19; Math 3.0 with Code 3.0 0.40. Within Math 3.1 the direction is stable: sizes 0.5 to 3 have
  cosine 0.93 to 0.99 with size 1, size -1 has -0.83, one direction (k = 1) 0.83, 64 directions 0.96.
- The mean direction carries 7 to 19 % of the summed squared shift of the all-layer edits (`frac_mean_dir`); the shift is mostly
  position-specific. Cap-hit and finished inputs get the same mean shift (cosine 0.98 to 1.00 for every non-random edit but Think-SFT 0.02, 0.93).
- Logit lens (key `logit_lens`; raw logit change, so a common offset is included): Math 3.1 at 1 raises ` which`, ` it`,
  ` actually`, `Hmm`, ` perhaps` (+0.31 to +0.06) and lowers bracket openers ` ((`, `.*(`, ` (-` (-1.8 to -1.5); at 2 the same
  tokens at +1.0 and -3.8; at -1 the bracket openers rise (+1.6). Math 3.0 raises `.`, `.\n\n`, ` that`, `Wait` (+2.6 to +1.7);
  Code 3.0 ` all`, `,`, ` the` (+4.2 to +3.6); IF and General raise nothing and lower code-like junk tokens by about 1.2; the
  random edit moves no logit by more than 0.005.
- Instrument: every edit's `add_rel` equals the scored cell's to 2e-15. Rounding the sum to BF16 by nearest would keep 38 to 88 %
  of an edit (`nearest_bf16_effective_scale`), growing with size, which is why the job adds in float32 (spec, choice 1). The scored
  cells had stochastic BF16 rounding; this measures the edit without that noise.

## Drift: a switch to Chinese marks a cut-off Think-SFT answer but no label-free sign predicts one early (hard328 n = 328, fresh2026 n = 136, MATH-500 n = 500, laptop, board work-76a232, idea-e37da1)

Question: Think-SFT + cue hits the 16,384 cap on 29 % (hard328) and 45.6 % (fresh2026) of its samples, and a quarter of those
cap hits hold Chinese text. What is that text, does it predict the outcome, and can a label-free sign stop a failing sample
early? Answer: no sign read at token 4,000, 8,000 or 12,000 tells a failing sample from a right one of the same problem
(best within-problem AUROC 0.568 [0.480, 0.657], `zratio` at 12,000; every interval covers 0.5), and the stop rule chosen on
MATH-500 saves 0.8 % of the sequential vote's tokens on hard328 [-0.3, +1.8] and 1.1 % on fresh2026 for -0.5 right answers:
H2 (10 % at no loss) is refuted. The switch is real and late: 156 of 1,312 Think-SFT samples on hard328 and 104 of 544 on
fresh2026 switch script (RL 12 and 9, base 9 and 6), 98 % of the letters are Chinese, the median first switch is at token
13,589, and English resumes after 85 % of first episodes. One place where it does predict: in the 32,768 sample, cut answers
that had switched before token 16,384 finish right 1 time of 24, the others 22 of 69 (-24.0 points [-36.8, -10.6] inside
strata of the base's right count). Spec with predictions, written after the instrument checks and before any other number:
`specs/SPEC_drift.md` (commit `9045c7c`). Stored rows and texts only; no GPU.

Definitions. Token positions are positions in the text re-tokenized with the run's tokenizer (`tokenizer.json` of
`allenai/Olmo-3.1-7B-RL-Zero-Math` @ `364820b` from the local cache; re-tokenized length minus `n_new` is 3 at the median, the
cue, and at most 53). Switch: an episode of at least 5 letters of a non-Latin script (Greek excluded) within 200 characters
of each other; its position is the token of the 5th letter. `rep50`: share of the 50-token windows of the prefix equal to an
earlier window. `loopA`: the runner's rule A (`rln4_lib.onset_lines`) on the prefix. `zratio`: zlib ratio of the prefix.
`wait`, `restart`: the word "wait" and 20 restart phrases per 1,000 tokens. Attempt 0 of every sample.

Instrument checks. `analysis/drift_test.py`: 10 planted passages (Chinese long, short and inside mathematics, Japanese,
Korean, Russian, Arabic, Hindi, Thai, mixed) are each found within 12 tokens of the planted position; 10 negatives (LaTeX,
Greek letters, names with diacritics, double-struck and mathematical letters, full-width punctuation, four stray letters,
emoji, code) are not flagged; a planted loop is found by `loopA` and `rep50`. The posted counts reproduce: cap hits with more
than 20 Chinese characters, fresh2026 Think-SFT 66 of 248, RL 3 of 84, base 0 of 219; hard328 86 of 378 and 1 of 114. With
switch flags shuffled inside problems the Q2 difference is -0.1 [-8.0, +10.7]; a planted sign (80 % of not-right, 20 % of
right samples) has within-problem AUROC 0.807; a stop that never fires reproduces the frontier rows (241 at 30,904 and 75 at
42,251 tokens, stored order).

Q1, description (`results/drift/describe-01/table.md`):

| Cell | Samples | With a switch | Cap hits: with a switch | Finished with a switch (right) | First switch at token: quartiles | English resumes: yes / no / text ends |
|---|---|---|---|---|---|---|
| hard328 Think-SFT + cue | 1,312 | 156 (11.9 %) | 378: 99 | 57 (39) | 10,733 / 13,589 / 15,048 | 135 / 2 / 19 |
| hard328 RL plain | 1,312 | 12 | 114: 3 | 9 (1) | 4,512 / 12,145 / 13,884 | 12 / 0 / 0 |
| hard328 base + cue | 1,312 | 9 | 286: 5 | 4 (0) | 11,111 / 12,173 / 13,132 | 5 / 1 / 3 |
| fresh2026 Think-SFT + cue | 544 | 104 (19.1 %) | 248: 76 | 28 (14) | 11,353 / 13,583 / 15,121 | 87 / 5 / 12 |
| fresh2026 RL plain | 544 | 9 | 84: 4 | 5 (0) | 12,955 / 13,379 / 14,416 | 8 / 0 / 1 |
| fresh2026 base + cue | 544 | 6 | 219: 1 | 5 (1) | 3,488 / 6,029 / 11,584 | 4 / 1 / 1 |
| MATH-500 Think-SFT + cue | 2,000 | 61 (3.1 %) | 93: 19 | 42 (34) | 3,750 / 10,249 / 13,147 | 57 / 0 / 4 |
| hard328 Think-SFT, cap 32,768, one sample | 328 | 83 (25.3 %): 38 before token 16,384, 45 after | 2: 1 | 82 (18) | 13,971 / 16,774 / 19,499 | 80 / 3 / 0 |

- Script: of the non-Latin letters in Think-SFT's hard328 samples 40,579 are CJK, 369 Cyrillic, 180 Hangul, 86 kana, 62
  Arabic. After the first switch a median 4.2 % of the letters are non-Latin: the text stays mostly English.
- Hand read of 20 switched samples (seed 0; read by the agent, not a blind judge; `describe-01/hand_read.md` with quotes
  and translations): in 15 the same working goes on and Chinese connectives or half-sentences replace English ones ("因此，
  x = ab + 1 ... 不，原式 ... 所以：", "therefore, ... no, the original expression ... so:"; "Wait，我先重新看一下方程的推导",
  "let me first look at the derivation of the equation again"); in 4 it is one stray word (Arabic "انضمامات", Russian
  "академ"); in 1 the sample gives up and guesses in Chinese ("可能正确的答案是 ... 但没有依据", "the right answer may be ...
  but there is no basis"). None is a loop or unrelated text. The English beside a switch is often already broken.
- Problem or sample: both. Pairs of samples of one problem that both switch: hard328 74 against 27.8 under flags permuted
  over all samples and 48.9 under flags permuted over cap hits only (p = 0.0001 each, 10,000 permutations); fresh2026 66
  against 29.6 and 41.9. 65 of the 102 hard328 problems with a switch have it in one sample only.
- Predictions: P1 (105 and 82 samples) low on both sets (156, 104). P2 (over 95 % Chinese) held. P3 (median past 8,000,
  under 10 % before 4,000) held on the median; 16 of 156 (10.3 %) start before 4,000. P4 (fewer than 40 % switch back)
  refuted: 85 %. P5 (not clustered given a cap hit) refuted.

Q2, does a switch predict the outcome (`results/drift/predict-01/table.md`):

| Think-SFT samples still running at t, hard328 + fresh2026 | switched by t: right | not switched: right | within problem, points [95 %] (problems) | inside base strata, weighted |
|---|---|---|---|---|
| t = 4,000 | 8 of 20 | 818 of 1,580 | +1.8 [0.0, +5.3] (19) | -11.7 [-18.4, -4.9] |
| t = 8,000 (primary) | 6 of 29 | 462 of 1,200 | +5.3 [-2.0, +13.3] (25) | -9.6 [-21.0, +2.8] |
| t = 12,000 | 11 of 70 | 201 of 852 | +1.0 [-6.7, +9.0] (50) | -4.7 [-12.8, +3.4] |

- H1 refuted: within problem the interval covers 0 at every t, with the sign opposite to the prediction (-10). The raw
  deficit (21 % against 39 % at 8,000) is the problem: 23 of the 29 switched samples are on problems the base never solves.
  Only 29 samples have switched by 8,000, so the test is weak; it cannot exclude a difference of 10 points either way.
- H1b held (the 32,768 sample, `cap32_sft`): of 93 answers longer than 16,384 tokens, 24 had switched before 16,384 and 1
  ends right; 22 of the other 69 do (Fisher p = 0.006). Base never right: 0 of 21 against 13 of 55, -23.6 [-35.3, -12.7];
  weighted over strata -24.0 [-36.8, -10.6]. Predicted 2 of 22 against 21 of 71. One sample per problem, so this is not
  matched within problem, and a switch first seen after 16,384 goes with 9 of 45 right.

Q3, AUROC of each sign for "the sample does not end right", Think-SFT, hard328 + fresh2026 (1,856 samples, 780 not right):

| Sign | t = 4,000: all / running, within problem | t = 8,000 | t = 12,000 |
|---|---|---|---|
| `length` (still running at t), baseline | 0.612 [0.591, 0.633] / 0.5 by construction | 0.771 [0.746, 0.797] / 0.5 | 0.874 [0.854, 0.894] / 0.5 |
| `switch` | 0.504 / 0.499 [0.495, 0.500] | 0.507 / 0.492 [0.480, 0.502] | 0.527 / 0.498 [0.474, 0.521] |
| `rep50` | 0.494 / 0.500 [0.487, 0.515] | 0.491 / 0.486 [0.463, 0.508] | 0.497 / 0.477 [0.451, 0.500] |
| `loopA` | 0.500 / 0.500 | 0.501 / 0.503 [0.500, 0.511] | 0.501 / 0.502 [0.500, 0.508] |
| `zratio` | 0.701 / 0.509 [0.440, 0.579] | 0.745 / 0.530 [0.458, 0.606] | 0.764 / 0.568 [0.480, 0.657] |
| `wait` | 0.552 / 0.453 [0.391, 0.520] | 0.537 / 0.500 [0.431, 0.570] | 0.535 / 0.462 [0.378, 0.546] |
| `restart` | 0.521 / 0.466 [0.414, 0.517] | 0.564 / 0.478 [0.415, 0.539] | 0.581 / 0.535 [0.460, 0.611] |
| pairs within problem (running) | 348 | 315 | 213 |

"all": every sample, pooled, the sign frozen when the sample ended. "running, within problem": pairs of a not-right and a
right sample of one problem, both still running at t. No sign beats `length` over all samples, and among running samples
none separates the samples of one problem: the prediction (none reaches 0.60, no interval above 0.55) held. `zratio` reaches
0.62 to 0.65 pooled over running samples and 0.51 to 0.57 within problem: it reads the problem, as the probe of
result-b30f15 did (0.571 [0.509, 0.634] within problem; result-f3d708 0.531 [0.468, 0.589]). The controls agree: best
within-problem value 0.643 [0.539, 0.744] (`zratio`, RL, 12,000, 129 pairs, one of 42 cells), base 0.548. Of the 70 samples
switched by 12,000, 11 end right (16 %, not the predicted under 10 %).

Q4, stop a sample at its first sign (`results/drift/stop-01/table.md`). A replay on stored rows: `analysis/frontier.py`'s
`seq4` (draw 2, stop when two agree, at most 4) on rows in which a stopped sample is a cap hit at its stop token (it costs
those tokens and casts no vote); the new sample is the next stored one. 12 candidates fixed in the spec; counted signs fire
when the sign is above the 75th or 90th percentile of MATH-500 samples running at that checkpoint. Chosen on MATH-500
(fewest tokens among candidates that stop at least 30 samples and lose at most 0.5 right): `rep50_p75`, which there means
any repeated 50-token window at a checkpoint. hard328 and fresh2026 are held out from the choice.

| Rule under the sequential vote | hard328: right, right (24), tokens (24) | minus plain, right (24) | tokens saved | fresh2026: right, right (24), tokens (24) | minus plain | tokens saved |
|---|---|---|---|---|---|---|
| plain `seq4` | 241, 238.9, 30,837 | | | 75, 75.5, 42,901 | | |
| `seq3` (at most 3 samples) | 241, 233.2, 26,114 | -5.7 | 15.3 % | 71, 72.5, 35,157 | -3.0 | 18.1 % |
| `seq4_L12000` (frontier: abandon at 12,000) | 219, 221.2, 29,664 | -17.7 | 3.8 % | 68, 65.8, 39,382 | -9.7 | 8.2 % |
| `rep50_p75`, chosen | 240, 238.4, 30,602 | -0.5 [-3.0, +2.0] | 0.8 % [-0.3, +1.8] | 74, 75.0, 42,446 | -0.5 [-1.5, 0.0] | 1.1 % [-0.1, +2.4] |
| `switch` (not chosen) | 235, 234.6, 30,545 | -4.3 [-8.7, -0.8] | 0.9 % | 73, 73.5, 41,621 | -2.0 [-5.5, +0.5] | 3.0 % |
| `zratio_p75` (not chosen) | 228, 226.1, 25,671 | -12.8 [-20.3, -6.3] | 16.8 % | 69, 69.5, 35,624 | -6.0 [-11.5, -1.5] | 17.0 % |
| `zratio_p90` (not chosen) | 236, 233.9, 28,518 | -5.0 [-10.0, -1.0] | 7.5 % | 75, 75.0, 41,117 | -0.5 [-3.0, +1.5] | 4.2 % |
| `len12000` (stop every sample at 12,000) | 204, 203.5, 28,203 | -35.4 | 8.5 % | 58, 58.0, 37,111 | -17.5 | 13.5 % |
| perfect sign at 4,000 (uses the answer key; a ceiling) | 244, 244.0, 16,250 | +5.1 [+1.8, +9.2] | 47.3 % | 77, 77.0, 19,248 | +1.5 | 55.1 % |

- H2 refuted, as predicted: the chosen rule saves 0.8 % and 1.1 %, not 10 %. No candidate saves 10 % without losing
  answers; at matched tokens the signs do not beat drawing fewer samples (`zratio_p75`: 226.1 at 25,671 against `seq3` 233.2
  at 26,114 on hard328).
- Why stopping at a switch costs answers: 39 of the 156 switched samples on hard328 end right (14 of 104 on fresh2026), and
  a switch comes at a median 13,589 tokens, so little is left to save.
- The ceiling is large: a detector that knew at token 4,000 which samples will not end right would halve the tokens and add
  5 problems on hard328. The signs here do not approach it.
- Under the plain vote over 4 the chosen rule gives 240 at 39,201 tokens against 241 at 40,410 (3.0 % fewer).
- Example of the rule's weakness (`stop-01/examples.json`): problem 0, sample 3 is stopped at token 8,000 after it boxed 116,
  because its closing summary restates the problem; a deployed rule should not stop after an answer.

Literature (WebSearch; four papers read in full by a subagent, findings added with `tools/paper.py`): 2507.15849 reports
switching in 0.0 to 0.6 % of English MATH500 problems and switching answers scoring higher (0.438 against 0.281, Table 6, no
matching); 2505.14815 that mixing rises with difficulty; 2505.17813 that the shortest sample is right most often; 2604.04930
a logit-based stop. None reads a text sign at a fixed token or redraws a stopped sample under a vote. idea-6fb0de items 2, 3
and 6 are different rules and were not run.

Caveats. One hand reader. Greek prose is not detected. The 32,768 result is one sample per problem. The Q4 thresholds are
quantiles on MATH-500, where `rep50`'s 75th percentile is 0. A replay cannot continue a stopped sample.

```
uv run --no-project --with numpy --with tokenizers python -m studies.rlneurons.analysis.drift_test
uv run --no-project --with numpy --with tokenizers python -m studies.rlneurons.analysis.drift --runs runs --out runs/drift_features
uv run --no-project --with numpy --with math-verify==0.9.0 --with tokenizers python -m studies.rlneurons.analysis.drift_read --features runs/drift_features --runs runs --out studies/rlneurons/results/drift --nn 01
```

Run folders `results/drift/{describe,predict,stop}-01/` (`run.json`, `readout.json`, `table.md`, `examples.json`;
`describe-01/hand_read.md`). The per-sample signs (`runs/drift_features/<cell>.jsonl`) are on the laptop, not in git.

## Paper: The Finish Dial (`paper/`, board work-0a1b10)

A short paper on the xreward dial, the removal test, the four-sample replication, the reward table and the delta
transplant. Public at https://monitor.invariant.team/paper/the-finish-dial.pdf (`tools/view.py` serves
`paper/the-finish-dial.pdf`; `infra/monitor/deploy.sh` ships it).

- `paper/facts.json`: every number of the paper with its value, n, unit and source (artifact path and key, or job
  id); `audit_recomputed` holds the intervals recomputed from raw rows for the paper.
- `paper/figs.py`: draws `fig_dial.pdf` and `fig_plane.pdf` from `facts.json`
  (`uv run --no-project --with matplotlib --with numpy python studies/rlneurons/paper/figs.py`); `paper/fonts/` is
  TeX Gyre Pagella, the body face (GUST font licence).
- `paper/paper.tex`, `paper/refs.bib`: the text; `tectonic paper.tex` builds `paper.pdf`, renamed to
  `the-finish-dial.pdf` for the site.
- Review: four independent reviews of draft 1 (number audit against the artifacts, skeptical review, citation check
  against arXiv, visual review) and one final check of draft 2. The main change: flat precision between sizes 0 and
  1.5 is two offsetting effects (newly finished answers are right 19 of 64 times; right answers on the 251 problems
  the base already finishes rise 161 to 184), so the paper claims the directions set finishing, not that they leave
  correctness alone.

- Answered-only control (`analysis/ood1_rows.py` -> `results/ood1/rows-01/answered.json`; per-item rows in `rows.json`): the
  plain base gives no option letter on 214 of 500 items (cue 30, RL 13, Think-SFT + cue 6), so part of the +30.0 is the cue
  making the base write an answer. On the 264 items where both the plain and the cued base give a letter the cue adds +12.5
  points [4.9, 19.7] (156 against 123 right; MMLU-Pro +10.2 [0.0, 20.3] of 118, BBH +14.4 [4.1, 25.3] of 146). RL on its 277
  shared items: +19.1 [11.9, 26.4]. So less than half of the cue's gain here is better answers; the rest is answers given at all.

## The 1.5x top-8 edit on the fresh 2026 set (fresh2026, n = 136, cue, T 1.0, grader v3, board work-16773f)

Question (`specs/SPEC_fresh_top8.md`, written before any job): the edit's size was chosen on the 328. Is base + 1.5 times the
top 8 directions of (RL-Math 3.1 - base) level with RL on 136 problems published in 2026, where nothing about it was chosen?
Answer: yes within the interval, slightly below. Four samples: 50, 52, 45, 46 right, mean 48.25 (RL plain 49, 50, 53, 50,
mean 50.5; base + cue 28, 28, 32, 30): edit minus RL -1.7 points [-5.3, +1.8], edit minus base + cue +13.8 [9.6, 18.2]. Vote
over 4: 53 of 136 at 45,750 tokens per problem (RL 57, base 38): -2.9 [-8.1, +2.2] against RL, +11.0 [5.1, 16.9] against the
base. Under the vote the edit alone is right on 4 problems, RL alone on 8.

Jobs `ih-1115-150237-83a4`, `-155322-598b`, `-155844-4392`, `-155905-0426` (AWS L40S, commit bcce43b; seeds 7000000 +
10000 s, the seeds of `SPEC_fresh.md`; each log repeats the edit statistics of job b417: add_rel 0.0011109, cos_written_add
0.585). RL and base rows: the 12 runs of board result-5251c9. Readout `analysis/mixvote.py`:
`results/mixvote/fresh2026_top8x1.5-01/readout.json` (paired bootstrap, 5,000 resamples, seed 0).

- Prediction 1 (single-sample mean in [44.5, 56.5]): holds, 48.25.
- Prediction 2 (vote over 4 in [50, 62]): holds, 53.
- Prediction 3 (cap hits per sample at most 30): holds, 14, 16, 14, 12 of 136 (RL 20 to 23, base 49 to 59). The edit's
  effect on finishing carries over to unseen problems, and it finishes more often than RL.
- The edit recovers 89 % of RL's single-sample gain over the cued base here ((48.25 - 29.5) / (50.5 - 29.5)) and 79 % of
  its gain under the vote ((53 - 38) / (57 - 38)); on the 328 the same shares are 101 % and 76 %.
- The edit uses the RL checkpoint's weights, so it is not a route without reward. Think-SFT + cue (no reward) has 60.0 on
  one sample and 75 under the vote on this set.

## Vote over k samples of the cued base, k = 1 to 12 (MATH-500 n = 500, base + cue, T 1.0, grader v3, board work-60f040)

Question (`specs/SPEC_votek.md`, written before the jobs): where does the plurality vote of the untrained cued base stop
rising, and does it reach RL's one-sample score (456 to 463) with no training? Answer: it reaches it at 6 samples (456.6 of
500) and is still rising at 12 (466 of 500, 95 % interval [455, 476]). RL with the same vote over 4 has 474 at 18,747 tokens
per problem, so at equal tokens RL stays ahead; the base needs about 5 times RL's one-sample tokens to match RL's one sample.

Samples: 0 to 3 are attempt 0 of the stored job `abaybektursun-1114-153825-208b` (seed 41000000); 4 to 11 are new,
`jobs/run_cell.py --model base --prompt cue --set math500 --temperature 1.0 --top-p 1.0 --seed 41040000 --samples 8`, no
restarts, cap 16,384, as shards: vast.ai `abaybektursun-1115-082353-a18c` (1/4), `-082400-c790` (2/4), `-064850-01eb` (3/4);
AWS `ih-1115-161922-9bfd` (4/8) and `ih-1115-201414-43ed` (0/8: 493 rows copied from the cut job `ih-1115-161910-44ea` with
`--resume`, 11 rows generated). Raw answers: `runs/<job id>/` (not committed; vast.ai jobs in the team store, AWS jobs under
the bridge's S3 results). Readout `analysis/votek.py`, output `results/votek/math500_base_cue-01/` (`metrics.json`,
`rows.jsonl` with every sample's extracted answer and score, `examples.json`: problem 0 voted right with 11 of 12 votes,
problem 9 voted wrong, two answers with 2 votes each and the wrong one drawn first).

```
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.votek --runs runs/abaybektursun-1114-153825-208b runs/ih-1115-201414-43ed+runs/ih-1115-161922-9bfd+runs/abaybektursun-1115-082353-a18c+runs/abaybektursun-1115-082400-c790+runs/abaybektursun-1115-064850-01eb --out studies/rlneurons/results/votek/math500_base_cue-01
```

Right of 500, mean over 200 random subsets of k of the 12 samples (bootstrap over problems, 2,000 resamples):

| k | vote right [95 %] | lowest, highest subset | at least one of k right | tokens per problem |
|---|---|---|---|---|
| 1 | 410.0 [397.9, 421.6] | 405, 418 | 410.0 | 4,059 |
| 2 | 418.9 [407.2, 430.4] | 411, 426 | 452.3 | 8,122 |
| 3 | 440.8 [429.4, 451.8] | 430, 452 | 464.7 | 12,155 |
| 4 | 449.2 [437.9, 460.0] | 441, 457 | 471.0 | 16,228 |
| 6 | 456.6 [445.6, 467.1] | 448, 465 | 478.4 | 24,370 |
| 8 | 460.1 [449.6, 470.2] | 454, 467 | 482.4 | 32,463 |
| 9 | 461.4 [450.9, 471.6] | 455, 468 | 483.8 | 36,487 |
| 12 | 466 [455.0, 476.0] | one subset | 487 | 48,680 |

Control: the vote over the 4 stored samples in order reproduces 446. The stored four are a low draw: the mean over subsets of
4 is 449.2 and subsets of 4 range from 441 to 457.

Vote with an early stop (draw samples until one answer has m votes or all 12 are drawn; mean over 200 random orders; the
fixed-threshold form of adaptive self-consistency, Aggarwal et al. 2023, arXiv 2305.11860):

| stop at m votes | right of 500 | samples per problem | tokens per problem |
|---|---|---|---|
| 2 | 459.0 | 2.71 | 15,882 |
| 3 | 463.5 | 4.00 | 22,564 |
| 4 | 465.7 | 5.19 | 27,863 |
| 6 | 466.6 | 7.32 | 35,807 |

At the tokens of the fixed vote over 4 (16,228) the stop at 2 votes has 459.0 against 449.2: about 10 more problems for the
same tokens, because easy problems stop after two samples and the split ones get up to 12. Paired bootstrap over problems
(`results/votek/math500_base_cue-02/metrics.json`, the same rows read again with this difference added; its `rows.jsonl` is
identical to run 01 and not committed): stop at 2 minus vote over 4, +9.9 problems [6.1, 14.1]; stop at 3 minus vote over 6,
+6.9 [3.5, 10.5]; stop at 4 minus vote over 7, +7.3 [4.0, 11.1]. Each stop rule is compared with the smallest fixed vote
that costs at least as many tokens. The interval covers the choice of problems, not a new draw of the 12 samples.

Predictions:
- V1 (theory round 06: vote over 9 inside [449, 462]): holds, 461.4.
- V2 (mine: vote over 12 minus vote over 6 under 3 problems): refuted, 9.4. The vote does not stop at 6.
- V3 (vote over 12 below 456): refuted, 466.

What is left: of the 34 problems the vote over 12 gets wrong, 13 have no right sample among 12, 11 have one, 7 have two, and
3 have a wrong answer held by more than 6 samples. At least one of 12 samples is right on 487 problems.

Limits: one seed family; the interval of each k is over problems, and the subsets of one k share samples. RL was not sampled
12 times, so this section does not say where RL's vote stops. The same cell on the 328 (spec section "The 328") was started
twice on vast.ai and cut both times when the account balance reached 0; it has no rows.
