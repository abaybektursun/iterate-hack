# Reward content test, step 1: the five Olmo 3 RL-Zero rewards on MATH-500 (board idea-46b68c, work-069eca)

Written 2026-11-15 02:35 UTC, before any GPU job of this item. Branch `reward5`. Follows `specs/DAY1_wdiff_2026-11-14.md`.

## Question

Does the MATH-500 gain of an RL-Zero model over the cued base need a math reward, a reward that grades reasoning, or only RL
from the base? AI2 released one RL-Zero model per reward from the same base `allenai/Olmo-3-1025-7B` (each card's `base_model`,
7,298,011,136 parameters each, HF API 2026-11-15): Math, Code, IF (instruction following), General, Mix. Names and revisions
are in `jobs/merge_weights.py` `OTHERS`.

Known (MATH-500, n 500, T 1.0 / top-p 1.0, grader v3, `results/day1_wdiff/readout.json`): base cue 410, base plain 224, random
matched-norm difference cue 417, Olmo 3.1 Math-RL cue 457 and plain 463, Olmo 3.1 Code-RL cue 450 and plain 390.

The 3.1 models are a later, stronger release: Wang et al. 2610.06851 App. C.1 Table 6 report Olmo-3-7B-RL-Zero-Math (3.0) at
75.0 % on MATH-500 (T 0.6, their grader), below their cued base (77.9 %). IF, General and Mix exist only as 3.0, so the
comparison for them is the 3.0 Math and 3.0 Code model under the same cell, not the 3.1 models.

Literature (team memory, Exa, 2026-11-15): 2608.03573 reports near-zero cosine between RL updates of different tasks and no
harm to other tasks; 2509.01363 Sec 4.4 a 2-point cross-task gain of a code-RL weight difference on GSM8K, no control. No
published MATH-500 number for the IF, General or Mix model was found.

## Cells

All: `--set math500 --temperature 1.0 --top-p 1.0`, one sample per problem, cap 16,384, grader v3, RL 3.1 tokenizer and
config as in every merged cell, weights from `merge_weights --other <key> --alpha 1 --rounding nearest` (asserts tensor identity
with the named model in all 355 tensors, so each cell checks its own weights). Problem i is sampled with seed base + i.

| Arm (run folder) | `--other` | Prompt | Seed base |
|---|---|---|---|
| `if30_cue` | `if30` | cue | 91,000,000 |
| `general30_cue` | `general30` | cue | 92,000,000 |
| `mix30_cue` | `mix30` | cue | 93,000,000 |
| `math30_cue` | `math30` | cue | 94,000,000 |
| `code30_cue` | `code30` | cue | 95,000,000 |
| `if30_plain` | `if30` | plain | 96,000,000 |
| `general30_plain` | `general30` | plain | 97,000,000 |
| `mix30_plain` | `mix30` | plain | 98,000,000 |
| `math30_plain` | `math30` | plain | 99,000,000 |
| `code30_plain` | `code30` | plain | 100,000,000 |

Command form (one line per job; read back from `uv run tools/gpu.py ls` for `--other`, `--prompt`, `--seed`):

```
uv run tools/gpu.py submit h100 --hours 2.5 -- "bash studies/rlneurons/jobs/setup_vllm.sh && rm -rf /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.merge_weights --other if30 --alpha 1 --rounding nearest --dir /tmp/theta && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/theta --model-label if30 --prompt cue --set math500 --temperature 1.0 --top-p 1.0 --seed 91000000 --commit $(git rev-parse HEAD)"
```

No separate smoke: the merge and cell path ran 12 cells today, and the only new input is the model name, which fails at
download in the first minute if wrong. The first finished job's rows are read before the others are scored.

## Scoring

Paired by problem against base cue (T1, 410) with the bootstrap of `analysis/day1_wdiff.py`, 95 % interval. Gain of a model =
its cue cell minus base cue. Each model's `merge.json` gives the fraction of entries changed and the relative norm.

## Predictions (each with what refutes it)

- R1 The 3.0 Math model with the cue is above the cued base: paired interval above 0. If the interval includes 0, the 3.0
  family shows no MATH-500 gain at this setting, the reward question cannot be answered with these models, and that is the
  result.
- R2 (the hypothesis under test: the gain does not depend on what the reward grades) IF cue gains at least half of the 3.0
  Math gain. Refuted if the paired interval of math30 cue minus if30 cue lies above half of the math30 gain.
- R3 code30 cue is within its paired interval of math30 cue, as the 3.1 pair was (450 vs 457). Refuted if the interval
  excludes 0.
- R4 Mix and General cue are not below math30 cue by more than 3 points. Refuted if either paired interval lies below -3.
- R5 Plain cells: math30 plain is at least 150 problems above base plain (224), as 3.1 Math is; if30 plain is below math30
  plain (the IF reward does not teach the answer format of this prompt). Refuted if if30 plain >= math30 plain.

Readings: R1 and R2 hold: reasoning-unrelated RL from this base gives a math gain; step 2 (token agreement, idea-46b68c)
follows. R1 holds and R2 is refuted with R3 holding: the reward must grade a reasoning task.

Cost: 10 H100 jobs of about 25 minutes, about 20 USD.
