# cleanneurons: neuron-level edits of the Olmo 3 base

Can a change to a small set of MLP neurons move the base `allenai/Olmo-3-1025-7B` toward
`allenai/Olmo-3.1-7B-RL-Zero-Math` on MATH-500, and what do those neurons do? Spec: `specs/SPEC1.md` (Parts T, L, I, G).
Models, prompt, cue, graders and stored answers are those of `studies/rlneurons`. A neuron (l, n) is unit n of layer l's
gated MLP: row n of `gate_proj` and `up_proj`, column n of `down_proj`; 32 x 11,008 = 352,256 neurons.

All code runs from the repository root (`python -m studies.cleanneurons.<folder>.<module>`).

## Layout

| Path | What it is |
|---|---|
| `specs/SPEC1.md` | The plan, written before the runs: definitions, the edit-file format, hypotheses with their refutations, controls. |
| `lib/neurons.py` | Neuron ranking by weight change, edit files, edits applied in memory with undo, checkpoint build and diff. `python -m studies.cleanneurons.lib.neurons` runs its self-check on a tiny random model. |
| `lib/loops.py` | Token-id loop detector, batched sampling whose noise depends on (seed, row, step) only, interventions (zero neurons, top-K activation mask). |
| `jobs/transplant_curve.py` | Part T: the base with RL neurons copied in, scored against RL by teacher forcing on stored answers. |
| `jobs/loop_neurons.py` | Part L: loops from the base's own prefixes, neuron rankings, held-out loop rate under each intervention, edit files. |
| `jobs/run_edit.py` | Part G: builds a checkpoint from an edit file and runs `studies.rlneurons.jobs.run_cell` on it. |
| `analysis/transplant_readout.py` | Part T closures recomputed without the three cue positions, from `kl.npz`. |
| `results/transplant/curve_attr-01/` | Part T2 run (attribution ranking, scored on held-out rows): `metrics.json`, `rank_attr_readout.json`, `edit_attr1.json`, `edit_attr_top100.json`, `run.json`. |
| `jobs/describe_neurons.py`, `analysis/describe_report.py` | Part I: what a neuron set does (activation record, top contexts, output tokens, timing against the loop onset, dose, base against RL) and its figures. |
| `results/transplant/curve_bias-01/` | Part T3 run (constant shift per layer, always-on neurons): `metrics.json` (`bias`, arms `bias_*`, `dense*`), `edit_dense.json`, `run.json`. |
| `results/describe/attr_top100-01/` | Part I on the 100 best Part T2 neurons: `neurons.json`, `density_readout.json`, `descriptions_test.json` (the sentences and the blind test), `run.json`. |
| `analysis/describe_test.py` | Part I item 7: prepares the blind description test and scores it. |
| `results/loops/real-01/`, `real-02/` | Part L runs on real looping answers (14 and 34 held-out loops): `metrics.json`, `examples.json`, the edit files `edit_<ranking><k>.json`, `run.json`. |
| `results/describe/attr1000_loops-01/` | Part I on 1,000 loop neurons: `metrics.json`, `dose_summary.json`, `onset_summary.json`, `run.json`. |
| `results/gen/<arm>_t06-01/`, `results/gen/readout_t06.json` | Part G: MATH-500 at T 0.6 with an edit, and the paired readout against the unedited cell. |
| `analysis/page_grid.py`, `results/gen/page_grid.json` | Per-problem state (right, wrong, loop) of each Part G cell, for a site page; totals asserted against `readout_t06.json`. |
| `results/gen/readout_t06_real02.json`, `readout_t06_seed2.json`, `results/gen/*r2_*-01/`, `base_t06s2-01/` | Part G with the run-2 neuron sets: seed 1, seed 2 and T 1.0 cells. |
| `analysis/vote_pair.py`, `results/gen/readout_vote_t06.json`, `results/gen/vote_*-0*/` | Part G over four samples per problem: edited against unedited, sample by sample, pooled, and under the vote. |
| `analysis/gen_readout.py` | Part G: an edited run against the unedited run, problem by problem (points, interval, loops, tokens, examples). |
| `tools/finding_rl_every_neuron.py`, `tools/finding_neurons_you_can_describe.py` | The site pages of Part T2 and Part I (`/finding/rl-every-neuron`, `/finding/neurons-you-can-describe`, tiles on `/findings`). |
| `tools/finding_loop_neurons.py` | The site page of Parts L and G (`/finding/loop-neurons`): one dot per MATH-500 problem, a switch that turns the loop neurons off. `python3 tools/finding_loop_neurons.py` checks its numbers against the artifacts. |
| `results/transplant/curve-01/` | Part T full run: `metrics.json`, `profile.json`, `examples.json`, `readout_after_cue.json`, `run.json`, edit files of four arms. |

## How to run

```
uv run tools/gpu.py submit h100 --hours 0.7 -- "python -m studies.cleanneurons.jobs.transplant_curve --commit $(git rev-parse HEAD)"     # add --smoke for 2 min
uv run tools/gpu.py submit h100 --hours 1.5 -- "python -m studies.cleanneurons.jobs.loop_neurons --commit $(git rev-parse HEAD)"
uv run --no-project --with numpy python -m studies.cleanneurons.analysis.transplant_readout runs/<job-id> <out.json>
```

Both jobs read `/runs/inputs/rln5/T1.jsonl` and `T2.jsonl` (see `studies/rlneurons/data/rln5/map_inputs.json`). Each job's docstring
lists its flags and output fields. Raw outputs stay in the Modal Volume `iterate-runs:<job-id>/` of the person who ran the job.

## Numbers

### Part T: the RL change is not concentrated in neurons (job `sameraslan-1114-151017-b683`, commit `fab81ec`)

80 stored answers (40 base-with-cue T1, 40 RL T2), 131,237 positions after the cue. Closure = share of KL(RL || base) that
disappears when the named part of the base is replaced by RL's, at the "decisive" 4 % of positions with the largest KL
(2,360 in T1, 2,889 in T2), cue positions left out. All from `results/transplant/curve-01/readout_after_cue.json`
(`metrics.json` holds the same table with the cue positions in; 24 % of its decisive KL sits on the three cue tokens).

| Part of RL copied into the base | Neurons | Share of the squared weight change | Closure, T1 text | Closure, T2 text |
|---|---|---|---|---|
| top 0.1 % of neurons by weight change | 352 | 0.2 % | 1.0 % | 1.8 % |
| top 1 % | 3,523 | 1.5 % | 3.9 % | 5.7 % |
| random 1 % (two draws) | 3,523 | 1.0 % | 0.7 % | 0.9 % |
| top 10 % | 35,226 | 11.8 % | 14.7 % | 20.3 % |
| random 10 % | 35,226 | 10.0 % | 7.0 % | 9.7 % |
| top 30 % | 105,677 | 32.9 % | 28.3 % | 42.7 % |
| random 30 % | 105,677 | 30.0 % | 20.0 % | 31.2 % |
| all MLP neurons | 352,256 | 100 % | 69.4 % | 85.8 % |
| all attention projections | 0 | | 50.4 % | 67.7 % |
| norms, embeddings, lm_head | 0 | | 4.0 % | 4.6 % |
| MLP of layers 0-7 / 8-15 / 16-23 / 24-31 | 88,064 each | 24 to 26 % each | 23.0 / 24.5 / 9.8 / 8.0 % | 41.6 / 31.1 / 13.6 / 12.4 % |

- Hypothesis T1 (top 1 % closes at least 50 %) is refuted: 3.9 % and 5.7 %. Closure grows about in proportion to the number of
  neurons copied; ranking by weight change gains a factor of 1.4 to 6 over random, largest for the smallest sets.
- The weight change itself is flat: every layer holds 3.0 to 3.2 % of the MLP change, and the top 1 % of neurons hold 1.5 %
  (`profile.json`). MLPs hold 66 % of the squared weight change, attention 31 %, the rest 3 %.
- Hypothesis T2 holds: the MLPs close more than attention. The two overlap (69 + 50 > 100 on T1 text).
- The lower half of the layers carries more of it than the upper half.
- Controls passed: copying every tensor gives KL 0, the unedited arm reproduces the base exactly, every edit is undone bit for bit.
- Limit: closure is a teacher-forced distance to RL and says nothing about accuracy. Ranking by weight change is a poor ranking; Part T2 below ranks by effect.
- Example of each kind (`examples.json`): a position where RL and the base disagree strongly and `top1` barely moves it:
  after "...the class average is 84.\n\n**Answer" the written token is ":**", KL(RL || base) 2.03, with `top1` 1.95.

### Part T2: ranked by effect, the best 1 % of neurons closes 14 to 19 % (job `sameraslan-1114-153108-a93d`, commit `51b022a`)

Neurons ranked on half the rows (20 + 20 answers) by the first-order drop of the decisive KL when the neuron is copied from RL,
then scored on the other half (1,163 decisive positions in T1 text, 1,509 in T2 text, cue left out). From
`results/transplant/curve_attr-01/metrics.json` (`closure_decisive_after_cue_half_B`) and `rank_attr_readout.json`.

| Neurons copied from RL | By effect (`attr`) T1 / T2 | By weight change (`top`) | Random |
|---|---|---|---|
| 0.1 % (352) | 5.4 / 7.3 % | 1.0 / 1.9 % | 0.1 / 0.2 % |
| 0.3 % (1,057) | 8.5 / 11.3 % | 2.2 / 3.3 % | 0.4 / 0.3 % |
| 1 % (3,523) | 13.7 / 18.6 % | 4.2 / 5.8 % | 0.7 / 1.0 % |
| 3 % (10,568) | 21.0 / 29.6 % | 7.8 / 10.6 % | 2.3 / 3.0 % |
| 10 % (35,226) | 33.6 / 48.9 % | 15.5 / 20.9 % | 7.4 / 10.0 % |
| all MLP (352,256) | 67.7 / 86.4 % | | |

- Hypothesis T3 (`attr1` closes at least 30 %) is not met: 13.7 % and 18.6 %; the refutation line of 15 % is crossed on T1 text only.
  A ranking by effect finds a set three times better than weight change and about 18 times better than random, and it is still far from
  carrying the change: closing half of it takes more than 10 % of the neurons.
- 88 % of all neurons have a positive score (copying them alone moves the base toward RL). The top 1 % hold 19 % of the positive
  score, the top 10 % hold 50 %.
- The effects add up: the sum of the first-order scores of all MLP neurons predicts a drop of 0.542 nats on the ranking rows and
  copying all of them gives 0.549 (of 0.708). RL acts as a small change of almost every neuron whose effects are close to linear.
- Where: `attr1` has 381 of its 3,523 neurons in layer 9 and 302 in layer 31; layers 1 to 15 hold 2,392, layers 16 to 28 hold 606.
  Only 610 of the 3,523 are also in the top 1 % by weight change.
- Controls passed, including: the top set lowers the KL on its own rows by the amount the scores predict (`metrics.json` `attr`).

### Part I on the 100 best neurons: always-on and describable (job `sameraslan-1114-154532-cdc8`, commit `2dd4da7`)

The 100 neurons with the largest Part T2 score against 100 layer-matched random neurons, on 131,397 positions of 80 stored
answers. From `results/describe/attr_top100-01/density_readout.json` and `descriptions_test.json`.

- 44 of the 100 are on almost everywhere (|a| beyond the layer's p97 at more than half of all positions); 1 of 100 random
  neurons is. Median mean |a| 0.213 against 0.020.
- RL left their weights alone: the cosine between the base's and RL's gate, up and down vectors is 1.0000 (median, both sets).
  Their activations differ more between the two models than a random neuron's (median correlation 0.960 against 0.987),
  which comes from the changes upstream.
- Blind description test (30 of the best, 15 random; the stronger pole of each): a reader writes one sentence from 10 top
  contexts; a second reader, with the sentence only, picks the 10 firing snippets out of 20 (10 held-out top contexts, 10
  random positions of the same answers). Right: 90.7 % [86.0, 94.7] for the best neurons, 71.3 % [60.0, 81.3] for random
  neurons, chance 50 %. Sentences that scored 100 %: "A hesitation word 'Hmm', 'Wait' or 'wait' starting a sentence right
  after a period or 'But', mostly just after the problem is restated" (layer 10, neuron 7275); "The period that ends a sentence
  finishing with a computed number or expression, just before a new sentence such as 'Then', 'Wait' or 'So'" (layer 29,
  neuron 2637). One that failed (20 %): a random neuron described as firing on modular-arithmetic tokens.
- Limits: the test covers the strongest firings only; writer and tester are the same LLM (Claude subagents).

### Part T3: a constant vector per layer carries a quarter to a third (job `sameraslan-1114-184552-a899`, commit `a2ec2c9`)

Scored on the held-out half (2,672 decisive positions after the cue), `closure_decisive_after_cue_half_B` in
`results/transplant/curve_bias-01/metrics.json`. T1 text / T2 text.

| Arm | What is added to the base | Closure |
|---|---|---|
| `bias_layer` | one constant vector per layer: the mean of (RL layer output - base layer output) on the base's layer inputs | 23.4 / 31.2 % |
| `bias_mlp` | one constant vector per layer on the MLP output, before the layer norm | 14.0 / 15.1 % |
| `bias_mlp_rnd` | a random vector of the same norm per layer | -1.6 / -4.7 % |
| `dense` | the 472 always-on neurons copied from RL | 2.6 / 3.4 % |
| `dense_rnd` | 472 other neurons, same number per layer | 0.2 / 0.1 % |
| `mlp` (for scale) | all MLP weights from RL | 67.7 / 86.4 % |

- Hypothesis T4 (the MLP change is mostly one constant vector per layer) is refuted: `bias_mlp` closes 21 % and 17 % of what
  `mlp` closes, under the quarter that the spec set. A constant vector in the residual stream (`bias_layer`) does more, 23 to
  31 % of the whole RL change, and a random vector of the same size makes things worse, so the direction is specific.
- Only 472 of 352,256 neurons are always-on (110 of them in the last layer). Copying them closes 15 to 25 times what the same
  number of other neurons closes, and still only about 3 %: they are over-represented among the best neurons, and they are not
  the carrier.
- Picture so far: RL = a fixed push per layer (about a quarter to a third) plus small input-dependent changes spread over almost
  every neuron (the rest). Controls passed (zero vector reproduces the base; hooks removed after each arm).

### Part L: about 100 neurons hold the loops (jobs `sameraslan-1114-184558-8a70`, commit `a2ec2c9`, and `sameraslan-1114-195047-4022`, commit `e455a80`)

Loops are taken from the base's own MATH-500 answers at T 0.6 / top-p 1.0 (cue, seed 1,000,000). Detector version 2 flags a
row when 95 % of its last max(240, p) tokens repeat with a period p of 2 to 600 tokens; version 1 (period up to 120) missed 25
of 38 cap hits whose repeated block was 124 to 588 tokens long. Half of the loops rank the neurons, by effect (`attr`: first-order
change of the looping tokens' log-probability against normal text when the neuron is zeroed) or by activation difference
(`act`). On the other half the answer is cut 300 tokens before the loop starts and continued for 1,600 tokens with the neurons
zeroed. "Loss" is the relative change of the log-loss on 40 normal answers. From `metrics.json` of each run.

| Neurons zeroed | Run 1: loops of 14 | Run 1: loss | Run 2: loops of 34 | Run 2: loss |
|---|---|---|---|---|
| none | 4 | | 19 | |
| 100 by effect | 2 | +2.8 % | 1 | +5.0 % |
| 1,000 by effect | 0 | +8.2 % | 0 | +8.0 % |
| 100 by activation | 1 | +1.2 % | 5 | +1.7 % |
| 1,000 by activation | 1 | +9.1 % | 2 | +11.6 % |
| 100 random (two draws in run 1) | 3, 5 | +0.1 % | 19 | +0.1 % |
| 1,000 random (two draws) | 3, 4 | +0.3 to 0.7 % | 15, 18 | +0.5 to 0.9 % |

- Run 1 ranked on the 14 loops of a 414-row file (the baseline job was cut by the workspace spend limit) and only 4 of its 14
  held-out rows loop again, so it separates little. Run 2 uses all 500 rows (68 loops, 34 + 34) and 19 of 34 loop again.
  Its neuron sets are other files (`real-02/edit_*.json`). Job `5442` between the two read a stale 173-row copy and is not used.
- Hypothesis L1 holds on run 2: 100 of 352,256 neurons remove 18 of 19 held-out loops, and 100 random neurons remove none.
- Top-K activation mask (run 1, keep the K largest activations per layer): K 3,300 costs +3.2 % loss, 1,100 +26 %, 860 +37 %,
  330 +114 %; a random 860 costs +2,461 %. At the sparsity Goodfire reports for other models this model loses a third
  of its fit, and the mask does not remove loops (2 to 4 of 14).
- Controls: planted loop flagged, 20 normal answers not flagged; zeroing by hook equals the weight edit (logit difference 0);
  padding and KV-cache agree within bf16 steps (tolerances in `jobs/loop_neurons.py`).

### Part I on the loop neurons: a dial for loops (job `sameraslan-1114-195041-abf7`, commit `e455a80`)

The 1,000 `attr` neurons of run 1 against 1,000 layer-matched random neurons. From `results/describe/attr1000_loops-01/`.

| Activations multiplied by | 0 | 0.5 | 1 | 2 |
|---|---|---|---|---|
| Loop neurons: loops of 14 | 1 | 1 | 3 | 8 |
| Random neurons: loops of 14 | 3 | | 3 | 3 |

- The loop rate follows the dose in both directions, and random neurons do nothing at either end (`dose_summary.json`).
- Timing (`onset_summary.json`, 28 loops, z against normal text): the loop neurons already deviate 200 to 50 tokens before the
  loop starts (mean |z| 0.17 against 0.08 for random neurons), and the deviation grows through the loop: 0.22 in the last 50
  tokens before, 0.26 in the first cycle, 0.38 in the second (random: 0.10, 0.10, 0.12). The signed mean stays at 0: some rise
  and some fall.
- RL left these neurons' weights alone (cosine 1.0 for gate, up and down) and their activations are as correlated between the
  two models as random neurons' (0.981 against 0.978).
- Limits: 14 rows per dose. The control `same_noise` failed (a repeat of factor 1 with the same noise gave identical tokens in
  5 of 14 rows, and the same 3 loops), so a difference of one or two loops is noise; 1 against 8 is not. Sentence descriptions
  and the blind test of these neurons are not done.

### Part G: zeroing loop neurons removes loops and tokens while accuracy stays (MATH-500, T 0.6 / top-p 1.0, n = 500)

The base with the cue, one sample, grader v3, seed 1,000,000, with the neurons of run 1 zeroed in the checkpoint, paired with
the unedited cell (job `9d69`, identical to the team's cell). From `results/gen/readout_t06.json` (`analysis/gen_readout.py`).

| Model | Right | Points against unedited | Cap hits | Loops (rule A) | Tokens per problem |
|---|---|---|---|---|---|
| unedited | 378 | | 98 | 71 | 4,690 |
| 100 by activation zeroed (`act100`, job `842c`) | 393 | +3.0 [-0.8, 6.6] | 68 | 47 | 4,246 |
| 1,000 by effect zeroed (`attr1000`, job `6dcf`) | 381 | +0.6 [-3.4, 4.6] | 39 | 19 | 3,870 |
| 1,000 random zeroed (`rnd1000`, job `cf9f`) | 370 | -1.6 [-5.4, 2.2] | 104 | 74 | 4,874 |

- 1,000 neurons (0.28 %) remove 73 % of the loops and 17 % of the tokens at unchanged accuracy; 1,000 random neurons remove
  neither. No row reaches the 415 of the best single-answer row without RL.
- Why no accuracy: of the 71 problems that looped, 33 are right with `attr1000`, and 25 are right with the random edit, which
  only changes the sampling path. A loop sits on a problem the model mostly cannot solve; removing it buys one more try.
- Published: neurons that drive repetition, with a dose response in both directions, were reported for 2B to 3B models on
  ordinary text (Hiraoka and Inui, arXiv 2410.13497; no task score measured). A count-based repetition penalty leaves MATH-500
  accuracy unchanged on two other models (arXiv 2610.24715, Table 16). New here: what zeroing such neurons does to a math
  benchmark's loops, tokens and score.
- Examples (one finished right, one finished wrong per arm) are in `readout_t06.json`. Raw generations stay in the Volume
  (`run.json` of each folder).

### Part G with the run-2 sets: fewer loops and tokens on two seeds, no reliable score gain, a loss at T 1.0

Same cell with the run-2 sets (`results/loops/real-02/edit_attr100.json`, `edit_attr1000.json`). T 0.6 rows are paired with the
unedited cell of the same seed (`results/gen/readout_t06_real02.json`, `readout_t06_seed2.json`); the T 1.0 rows are compared
with the team's stored cell of the same seeds by totals only (its rows are not in this repository).

| Cell (MATH-500, cue, top-p 1.0, one sample) | Right | Points against unedited | Cap hits | Loops (rule A) | Tokens per problem | Job |
|---|---|---|---|---|---|---|
| T 0.6, seed 1,000,000, unedited | 378 | | 98 | 71 | 4,690 | `9d69` |
| T 0.6, seed 1,000,000, 100 zeroed | 412 | +6.8 [2.8, 10.6] | 34 | 22 | 3,742 | `ef4f` |
| T 0.6, seed 1,000,000, 1,000 zeroed | 414 | +7.2 [3.2, 11.2] | 22 | 4 | 3,464 | `15f9` |
| T 0.6, seed 2,000,000, unedited | 394 | | 87 | 61 | 4,357 | `bbdc` |
| T 0.6, seed 2,000,000, 100 zeroed | 398 | +0.8 [-2.8, 4.4] | 40 | 18 | 3,621 | `47fd` |
| T 0.6, seed 2,000,000, 1,000 zeroed | 399 | +1.0 [-2.8, 4.6] | 26 | 9 | 3,523 | `d05c` |
| T 1.0, seed 41,000,000, unedited (team cell T1) | 410 | | 27 | 0 | 3,966 | `rlneurons` README (rows T1) |
| T 1.0, seed 41,000,000, 100 zeroed | 390 | -4.0 (unpaired) | 18 | 0 | 4,074 | `5599` |
| T 1.0, seed 41,000,000, 1,000 zeroed | 372 | -7.6 (unpaired) | 13 | 0 | 3,967 | `7858` |

- Loops and tokens: on both seeds the 1,000 set removes 85 to 94 % of the loops and 19 to 26 % of the tokens; the 100 set removes
  about 70 % and 17 to 20 %.
- Score: the unedited cell itself moves from 378 to 394 between the two seeds. The gain of seed 1 (+7) does not repeat on seed
  2 (+1), so one seed's paired interval understates the noise of a whole run. Four samples per arm settle it (next section).
- At T 1.0 the base does not loop and the edit only costs: 390 and 372 against 410. The edit is a repair for the loop-prone
  setting and gives nothing to the setting the scoreboard uses.
- The edited T 0.6 cells (398 to 414 at 3,464 to 3,742 tokens) sit at the level of the unedited T 1.0 cell (405 to 410).

### Part G over four samples: about +4 points at T 0.6, a tie under the vote at 21 % fewer tokens

`run_cell --samples 4 --restarts 2`, MATH-500, T 0.6 / top-p 1.0, seed 1,000,000: edited (1,000 run-2 neurons zeroed, job `aa97`)
against unedited (job `5d2f`). The unedited job was stopped by its 4-hour limit after every first attempt was written, so both
arms are read on attempt 0 only. From `results/gen/readout_vote_t06.json` (`analysis/vote_pair.py`); the edited run's full
rows (restart, vote after restart) are in `results/gen/vote_attr1000r2_t06-01/readout.json`.

| Row (500 problems) | Unedited | 1,000 zeroed | Edited minus unedited, points [95 %] |
|---|---|---|---|
| single, samples 0 to 3 | 382, 371, 388, 391 | 415, 397, 401, 400 | +4.05 [2.00, 6.15] pooled |
| single, with the seed-2 pair (394, 399) | | | +3.44 [1.60, 5.36] pooled over 5 draws |
| cap hits per sample | 85 to 99 | 17 to 28 | |
| loops (rule A) per sample | 59 to 73 | 4 to 10 | |
| vote over 4 | 441 at 18,173 tokens | 441 at 14,399 tokens | 0.0 [-2.4, 2.4] |
| right in all 4 samples / in none | 292 / 47 | 323 / 40 | |

- At T 0.6 the edit adds about 3.4 to 4 points to a single answer: every one of the five paired draws is positive (+5 to +33
  problems). The two single-seed readouts above could not show this.
- The single answers of the edited T 0.6 model (397 to 415, mean 403) are at the level of the unedited T 1.0 cell (405 to 410,
  3,808 to 3,966 tokens) at about 3,500 to 3,700 tokens.
- Under a vote over 4 the gain is gone (441 and 441) and the token saving stays: 21 %. The team's unedited T 1.0 vote has 446 at
  16,034 tokens (`studies/rlneurons/README.md`, Day-1 #3).

### Part G on the harder 328: no gain, and a loss at T 1.0 with the 1,000 set

Cue, top-p 1.0, one sample, seed 3,000,000, grader v3; `counts` in `metrics.json` of each `results/gen/hard328_*-01/`.
The unedited T 1.0 cell is the team's (`studies/rlneurons/README.md`, "Harder 328"), compared by totals; identical requests on
the 328 scored 155, 160, 164 and 168 there (comment on result-d9d6f3), so differences under about 10 problems are noise.

| Cell (328 problems) | Right | Cap hits | Loops (rule A) | Tokens per problem | Job |
|---|---|---|---|---|---|
| T 1.0, unedited (team cell) | 164 | 77 | 1 | 9,344 | `abaybektursun-1114-151534-e72c` |
| T 1.0, 100 zeroed | 155 | 47 | 1 | 8,706 | `d4a3` |
| T 1.0, 1,000 zeroed | 130 | 32 | 1 | 8,556 | `f46b` |
| T 0.6, unedited | 134 | 156 | 94 | 9,842 | `2e30` |
| T 0.6, 100 zeroed | 149 (+4.6 points [0.0, 9.1], paired) | 77 | 24 | 8,819 | `86c9` |
| T 0.6, 1,000 zeroed | 149 (+4.6 [0.0, 9.1]) | 55 | 6 | 8,486 | `2a56` |

- At T 1.0 the edit turns cap hits into finished answers (77 to 47 and 32) without making them right: 155 is inside the noise
  of 164, and 130 is a loss of 34 problems. This agrees with result-51fd20: cap hits on the 328 are failures to solve.
- At T 0.6 the edit carries over to these unseen problems: loops fall from 94 to 24 and 6, tokens by 10 and 14 %, and 15 more
  problems are right, with an interval that touches 0 (`results/gen/readout_hard328_t06.json`). The edited T 0.6 cells (149)
  stay under the unedited T 1.0 cell (164).
- Summary of Part G: zeroing loop neurons is a reward-free way to remove loops and 17 to 26 % of the tokens at T 0.6, and it
  adds about 4 points to a single answer there. That only reaches the level of the unedited T 1.0 cell, and at T 1.0 the edit
  costs right answers, so it sets no record on MATH-500 or the 328.

