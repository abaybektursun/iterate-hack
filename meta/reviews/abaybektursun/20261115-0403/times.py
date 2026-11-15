# /// script
# requires-python = ">=3.11"
# dependencies = ["modal>=1.4"]
# ///
"""Seconds from submit to start and from start to end of one job, from the Modal Dict iterate-jobs.
  uv run meta/reviews/abaybektursun/20261115-0403/times.py <job id>"""
import sys

import modal

jobs, job = modal.Dict.from_name("iterate-jobs"), sys.argv[1]
print(job, "submit to start", jobs[f"start:{job}"]["at"] - jobs[f"job:{job}"]["at"], "s; start to end",
      jobs[f"end:{job}"]["at"] - jobs[f"start:{job}"]["at"], "s; exit", jobs[f"end:{job}"]["exit_code"])
