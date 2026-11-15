# Experiments, round-11

Each cell's forecasts and proposers are in `cells.md`. Run from the top; write each readout's number into `measured.json` (a list of {readout, measured, n, interval, artifact, item}).

## A: separation per GPU minute

1. r11-m01 (0 split readouts, 45 min): base Olmo-3-1025-7B (untrained); plain; hard328, n 328. Readouts: r11-m01-r1.
   `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt plain --set hard328 --temperature 0.6 --top-p 1.0 --max-tokens 4096 --seed 3000000 --commit $(git rev-parse HEAD)"`
2. r11-m02 (0 split readouts, 110 min): base Olmo-3-1025-7B (untrained); plain (no cue, no opening text); math500, n 100. Readouts: r11-m02-r1.
   `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model base --set math500 --n 100 --temperature 0.6 --top-p 1.0 --samples 6 --max-tokens 8192 --seed 71000000 --commit $(git rev-parse HEAD)"`

## B: base-only cells by the highest forecast over the best known base count


## C: no-reward routes by the margin of the median forecast over the stored subset count, in its sd

1. r11-n01 (s1; margin -0.21 sd; 31000 tokens per problem, 200 min): Think-SFT with the cue at T 1.0 and the full 16,384 cap, sequential vote of up to 5 samples: stop when the first two answers agree, else keep drawing until a value has 3 votes or 5 samples are used; answer = plurality (ties to the earliest), tokens counted for the drawn samples only. hard328 0/8 median 33.5 against stored 34 (sd 2.41).
   `uv run tools/gpu.py submit l40s --hours 4 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model think_sft --opening-text $' line!\n\nOkay' --set hard328 --shard 0/8 --temperature 1.0 --top-p 1.0 --samples 5 --seed 71000000 --commit $(git rev-parse HEAD)"`
   RL arm: `uv run tools/gpu.py submit l40s --hours 4 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model rl --opening-text $' line!\n\nOkay' --set hard328 --shard 0/8 --temperature 1.0 --top-p 1.0 --samples 5 --seed 71000000 --commit $(git rev-parse HEAD)"`
2. r11-n02 (s5; margin -0.28 sd; 28800 tokens per problem, 190 min): Think-SFT with the cue sampled at T 1.0 / top-p 1.0 with min-p 0.05 (tail tokens cut), 3 samples per problem at cap 16,384, majority vote over the 3 (ties to the first sample). hard328 0/5 median 48 against stored 49 (sd 3.55).
   `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model think_sft --opening-text $' line!\n\nOkay' --set hard328 --shard 0/5 --temperature 1.0 --top-p 1.0 --min-p 0.05 --max-tokens 16384 --samples 3 --seed 3400000 --commit $(git rev-parse HEAD)"`
   RL arm: `uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell --model rl --opening-text $' line!\n\nOkay' --set hard328 --shard 0/5 --temperature 1.0 --top-p 1.0 --min-p 0.05 --max-tokens 16384 --samples 3 --seed 3400000 --commit $(git rev-parse HEAD)"`

## Free targets: cells and routes an open work item already answers (scored next round from its report)

none
