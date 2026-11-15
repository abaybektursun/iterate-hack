"""Your GPU job runner on Modal. Each person deploys it once in their own Modal workspace, and again after
changing requirements.txt or the limits:

    modal secret create hf-token HF_TOKEN=<your Hugging Face token>     # once, in your own terminal
    modal deploy infra/runner.py

Jobs are paid from your own Modal credits. Each GPU class is one Modal function whose max_containers limits how
many of your jobs run at once; a job over the limit waits in Modal's queue. Submit and inspect jobs with
tools/gpu.py.

A job runs one commit of this repository, uploaded by tools/gpu.py to the Volume iterate-code as <sha>.tar. The
command runs from the repository root with OUT_DIR=/runs/<job-id>; the output written there, and the command's
log, end up in the Volume iterate-runs. HF_HOME is the Volume iterate-hf-cache, so each model downloads once.
All three Volumes are in your own workspace.
"""
import os
import shutil
import signal
import subprocess
import tarfile
import time
from pathlib import Path

import modal

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install_from_requirements(str(Path(__file__).resolve().parent.parent / "requirements.txt"))
    .env({"HF_HOME": "/hf", "PYTHONUNBUFFERED": "1"})
)
runs = modal.Volume.from_name("iterate-runs", create_if_missing=True)
code = modal.Volume.from_name("iterate-code", create_if_missing=True)
hf_cache = modal.Volume.from_name("iterate-hf-cache", create_if_missing=True)
jobs = modal.Dict.from_name("iterate-jobs", create_if_missing=True)

app = modal.App("iterate-runner")
common = dict(
    image=image,
    volumes={"/runs": runs, "/code": code, "/hf": hf_cache},
    secrets=[modal.Secret.from_name("hf-token")],
    timeout=24 * 3600,
    retries=0,
)


def run(job_id):
    job = jobs[f"job:{job_id}"]
    gpu = "cpu"
    if shutil.which("nvidia-smi"):
        query = ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"]
        gpu = subprocess.run(query, capture_output=True, text=True, check=True).stdout.strip()
    jobs[f"start:{job_id}"] = {"at": int(time.time()), "gpu": gpu}

    code.reload()  # a container that started before this commit was uploaded does not see the file otherwise
    runs.reload()  # the same for inputs put on the Volume iterate-runs (modal volume put) after the container started
    with tarfile.open(f"/code/{job['sha']}.tar") as tar:
        tar.extractall("/repo", filter="data")
    out = Path("/runs") / job_id
    if out.exists():  # Modal restarted the container: keep the interrupted run's output beside the new one
        out.rename(f"{out}.interrupted-{int(time.time())}")
    out.mkdir(parents=True)
    deadline = time.time() + job["hours"] * 3600
    with open(out / "log", "w") as log:
        proc = subprocess.Popen(job["cmd"], shell=True, cwd="/repo", stdout=log, stderr=subprocess.STDOUT,
                                env={**os.environ, "OUT_DIR": str(out), "JOB_ID": job_id, "PYTHONPATH": "/repo"}, start_new_session=True)
        last_commit = time.time()
        while proc.poll() is None:
            time.sleep(5)
            if time.time() - last_commit > 30:
                runs.commit()  # makes the log readable by tools/gpu.py logs while the job runs
                last_commit = time.time()
            if time.time() > deadline:
                os.killpg(proc.pid, signal.SIGKILL)  # the shell and every process it started
                proc.wait()
    runs.commit()
    jobs[f"end:{job_id}"] = {"at": int(time.time()), "exit_code": proc.returncode, "timed_out": time.time() > deadline}
    if proc.returncode != 0:
        raise RuntimeError(f"{job_id} exited with code {proc.returncode}")


# One function per GPU class. max_containers is how many of your jobs of that class run at once. The limits are read at deploy
# time: `ITERATE_MAX_H100=24 ITERATE_MAX_B200=4 modal deploy infra/runner.py` changes them for your workspace only.
@app.function(gpu="H100", max_containers=int(os.environ.get("ITERATE_MAX_H100", 20)), **common)
def h100(job_id: str):
    run(job_id)


@app.function(gpu="B200", max_containers=int(os.environ.get("ITERATE_MAX_B200", 2)), **common)
def b200(job_id: str):
    run(job_id)


@app.function(cpu=4, max_containers=8, **common)
def cpu(job_id: str):
    run(job_id)
