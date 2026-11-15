"""Your GPU job runner on Modal. Each person deploys it in their own Modal workspace, and again whenever this
file, requirements.txt or the limits change:

    modal secret create hf-token HF_TOKEN=<your Hugging Face token>     # once, in your own terminal
    uv run tools/gpu.py deploy     # runs modal deploy and records which runner.py is deployed; submit checks it

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
    # The rlneurons engine (vLLM in /opt/rln-vllm) is built once here, by the study's own script. A job that runs
    # the script again finds everything installed and takes about a second.
    .add_local_file(str(Path(__file__).resolve().parent.parent / "studies/rlneurons/jobs/setup_vllm.sh"), "/setup_vllm.sh", copy=True)
    .run_commands("bash /setup_vllm.sh")
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
    # One job per container: a process a cancelled job left behind held its log open, so every job sent to that container
    # next died at runs.reload() with "open files preventing the operation" (31 jobs in 15 min, 2026-11-15 07:04-07:18)
    single_use_containers=True,
)


SILENT = 15 * 60  # seconds without a new log line after which a job is ended: it holds a GPU and is most likely hung


def run(job_id):
    job = jobs[f"job:{job_id}"]
    if f"cancel:{job_id}" in jobs:  # gpu.py kill on a queued job does not always stop Modal from starting it
        print(f"{job_id} was cancelled before it started; not running it")
        return
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
        try:
            last_commit = last_output = time.time()
            size = 0
            stop = None
            while proc.poll() is None:
                time.sleep(5)
                if time.time() - last_commit > 30:
                    runs.commit()  # makes the log readable by tools/gpu.py logs while the job runs
                    last_commit = time.time()
                    if f"cancel:{job_id}" in jobs:
                        stop = "cancelled by gpu.py kill"
                if (out / "log").stat().st_size != size:
                    size, last_output = (out / "log").stat().st_size, time.time()
                if time.time() - last_output > SILENT:
                    stop = f"no new log line for {SILENT // 60} min"
                if time.time() > deadline:
                    stop = f"time limit of {job['hours']} h"
                if stop:
                    os.killpg(proc.pid, signal.SIGKILL)  # the shell and every process it started
                    proc.wait()
                    log.write(f"\nrunner: job ended: {stop}\n")
        finally:  # whenever run() ends, also when Modal interrupts it (cancel, shutdown): the job's processes, and any
            # background process it left (a server started with &), run in their own session and would otherwise keep
            # running in this container, holding /runs open so that the next job dies at runs.reload()
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:  # every process of the job has already exited
                pass
            proc.wait()
    runs.commit()
    jobs[f"end:{job_id}"] = {"at": int(time.time()), "exit_code": proc.returncode, "timed_out": time.time() > deadline, "stopped": stop}
    if proc.returncode != 0:
        raise RuntimeError(f"{job_id} exited with code {proc.returncode}")


# One function per GPU class. max_containers is how many of your jobs of that class run at once. The limits are read at deploy
# time: `ITERATE_MAX_H100=24 ITERATE_MAX_B200=4 uv run tools/gpu.py deploy` changes them for your workspace only.
@app.function(gpu="H100", max_containers=int(os.environ.get("ITERATE_MAX_H100", 10)), **common)
def h100(job_id: str):
    run(job_id)


# A queue of its own for short jobs (at most 30 min, enforced by gpu.py submit). It reserves nothing by default: with
# ITERATE_MAX_H100 at the workspace's GPU limit (10) both lanes compete for the same GPUs. Holding 2 GPUs back for it
# (ITERATE_MAX_H100=8) left them idle: 4 GPU-min used in 39 min while 20 long jobs waited (meta/reviews/abaybektursun/20261115-0702).
@app.function(gpu="H100", max_containers=int(os.environ.get("ITERATE_MAX_SHORT", 2)), **common)
def short(job_id: str):
    run(job_id)


@app.function(gpu="B200", max_containers=int(os.environ.get("ITERATE_MAX_B200", 2)), **common)
def b200(job_id: str):
    run(job_id)


@app.function(cpu=4, max_containers=8, **common)
def cpu(job_id: str):
    run(job_id)
