# Failure classes whose cause is still in place (one line each; delete the row when its change lands)

- vLLM environment built inside every job by studies/rlneurons/jobs/setup_vllm.sh (3 failed or cancelled of 8 jobs on 2026-11-14 20:32-20:41; 7-60 s per job) -> put the /opt/rln-vllm venv in the runner image once (infra/runner.py), and drop the script.
- tools/cycle.py prints negative run minutes for a job whose start record is later than its cancel (26e0 -149.3, 175e -4.3; total "-130.0 of them in failed or cancelled jobs", meta/reviews/sameraslan/20261115-0247/cycle.txt) -> cycle.py: no run minutes when the end is before the start.
