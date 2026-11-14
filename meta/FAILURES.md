# Failure classes whose cause is still in place (one line each; delete the row when its change lands)

- vLLM environment built inside every job by studies/rlneurons/jobs/setup_vllm.sh (3 failed or cancelled of 8 jobs on 2026-11-14 20:32-20:41; 7-60 s per job) -> put the /opt/rln-vllm venv in the runner image once (infra/runner.py), and drop the script.
