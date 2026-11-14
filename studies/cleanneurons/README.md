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
- Limit: closure is a teacher-forced distance to RL, not accuracy. Ranking by weight change is a poor ranking; Part T2 below ranks by effect.
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
