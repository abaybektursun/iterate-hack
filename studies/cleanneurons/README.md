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
- Limit: closure is a teacher-forced distance to RL, not accuracy, and the ranking is by weight change only. An attribution
  ranking (which neurons' copy lowers the KL most) is the open test before "no sparse set exists" can be said.
- Example of each kind (`examples.json`): a position where RL and the base disagree strongly and `top1` barely moves it:
  after "...the class average is 84.\n\n**Answer" the written token is ":**", KL(RL || base) 2.03, with `top1` 1.95.
