# Failure classes whose cause is still in place (one line each; delete the row when its change lands)

- vLLM environment built inside every job by studies/rlneurons/jobs/setup_vllm.sh (3 failed or cancelled of 8 jobs on 2026-11-14 20:32-20:41; 7-60 s per job) -> put the /opt/rln-vllm venv in the runner image once (infra/runner.py), and drop the script.
- A container that Modal restarts dies with FileExistsError at out.mkdir in infra/runner.py and the job's work is lost (3 cpu jobs on 2026-11-15 UTC: c51a, 277d, 74c7) -> a restarted run writes into <job>/restart-<n>/, or the job is marked non-preemptible; deploy when no job is running.
