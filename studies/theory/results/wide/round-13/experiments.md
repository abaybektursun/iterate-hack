# Experiments, round-13

Each cell's forecasts and proposers are in `cells.md`. Run from the top; write each readout's number into `measured.json` (a list of {readout, measured, n, interval, artifact, item}).

## A: separation per GPU minute


## B: base-only cells by the highest forecast over the best known base count


## C: no-reward routes by the margin of the median forecast over the stored subset count, in its sd

1. r13-n01 (s4; margin +0.31 sd; 35500 tokens per problem, 230 min): Cued untrained base at T 1.0 / top-p 1.0 with min-p 0.05 truncation, 4 samples per problem, plurality vote over the finished answers (cap hits cast no vote). hard328 0/8 median 23 against stored 22 (sd 3.19).
   `bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set hard328 --shard 0/8 --temperature 1.0 --top-p 1.0 --min-p 0.05 --samples 4 --seed 3000000 --commit COMMIT_SHA && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set math500 --shard 0/5 --temperature 1.0 --top-p 1.0 --min-p 0.05 --samples 4 --seed 41000000 --commit COMMIT_SHA`
   RL arm: `bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model rl --prompt plain --set hard328 --shard 0/8 --temperature 1.0 --top-p 1.0 --min-p 0.05 --samples 4 --seed 3000000 --commit COMMIT_SHA`

## Free targets: cells and routes an open work item already answers (scored next round from its report)

none
