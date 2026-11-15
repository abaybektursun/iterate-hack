# Failure classes whose cause is still in place (one line each; delete the row when its change lands)

- vLLM environment built inside every job by studies/rlneurons/jobs/setup_vllm.sh (3 failed or cancelled of 8 jobs on 2026-11-14 20:32-20:41; 7-60 s per job) -> put the /opt/rln-vllm venv in the runner image once (infra/runner.py), and drop the script.
- Four-sample rows of a joined cell stay in the owner's Modal Volume: studies/rlneurons/analysis/day1_join_shards.py writes answers.jsonl outside git (0 of 3 hard328 folders have rows, 2026-11-15 03:15; the selector of result-cbe0bc could not score the 328) -> the join writes the compact rows.jsonl of day1_vote.py into the run folder.
