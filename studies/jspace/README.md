# jspace: what the RL model holds in its workspace that the base does not

Reads Anthropic's Jacobian lens (J-lens, arXiv 2607.15495) on the base `allenai/Olmo-3-1025-7B` and on
`allenai/Olmo-3.1-7B-RL-Zero-Math` over the stored MATH-500 answers of `studies/rlneurons` (T1: base with cue, T2: RL,
T 1.0). Goal: explain the 53-problem gap with per-problem examples, and find tokens for a no-reward intervention.
Spec: `specs/SPEC1_lensdiff.md`. Board: idea-8a0a28, work-50d329.

All code runs from the repository root with the root on `PYTHONPATH`.

## Layout

| Path | What it is |
|---|---|
| `specs/SPEC1_lensdiff.md` | The plan, the instrument checks, hypotheses H1 to H3 and what refutes each. Written before any GPU job. |
| `lib/jlens_read.py` | The fitted base lens (`neuronpedia/jacobian-lens`, pinned revision), block-output hooks, the readout, the word-like token mask, the hit@K count. |
| `jobs/lensdiff.py` | The GPU job: both models over the stored answers with teacher forcing; aggregates, per-position shards and `checks.json` in `$OUT_DIR`. Imports `build` and `load` from `studies/rlneurons/jobs/rln5_map.py`. |

## Run it

```
uv run tools/gpu.py submit h100 --hours 1 -- "python -m studies.jspace.jobs.lensdiff --commit $(git rev-parse HEAD) --store-layers 16,24"
uv run tools/gpu.py get <job-id>
```

Smoke run: add `--n 12 --pick 20,36,46 --check-every 1`. Laptop dry run with small random models (no weights): add
`--dry-run --n 3 --inputs <folder with T1.jsonl and T2.jsonl> --out <new folder>`.

Inputs are in the Volume `iterate-runs` under `inputs/rln5/` (sha256 in `studies/rlneurons/data/rln5/map_inputs.json`).
Per-position shards stay in the Volume and in `runs/<job-id>/` (not committed).

## Numbers

None yet.
