# /// script
# requires-python = ">=3.11"
# dependencies = ["modal>=1.4"]
# ///
"""Runs a finished job's id through the runner a second time, which is what Modal does when it restarts a container.
  uv run meta/reviews/abaybektursun/20261115-0215/rerun.py <job id>"""
import sys

import modal

job_id = sys.argv[1]
call = modal.Function.from_name("iterate-runner", "cpu").spawn(job_id)
try:
    call.get()
    print(f"second run of {job_id}: finished")
except Exception as error:  # the measurement is which error the second run ends with
    print(f"second run of {job_id}: {type(error).__name__}: {error}")
print("folders:", sorted(e.path for e in modal.Volume.from_name("iterate-runs").listdir("/") if job_id in e.path))
