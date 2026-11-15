"""The experiment runner of the autobench study, one Modal app in your own workspace. Deploy once:

    modal deploy studies/autobench/jobs/modal_app.py

Both arms send every experiment through `submit`, so both are measured by the same instrument:

  submit(arm, source)        CPU. Claims the arm's next experiment number in the ledger (refuses when the arm's
                             budget is used), runs train_job, stores train.py, the log and the record in the
                             Volume autobench-runs, returns the log.
  train_job(source)          H100. Runs one train.py under lib/launch.py with the pinned prepare.py. The data
                             Volume is read-only, the network is blocked, Modal is not reachable, the container is
                             used once, the process is killed at 600 s. The holdout shard is not mounted.
  score_final(label, source) CPU. The same run through train_job_holdout, which mounts the holdout shard and
                             also records test_bpb. For the operator, after both arms have ended.
  prep, warm, prep_holdout   one-time data preparation (prepare.py as pinned; the attention kernel; the holdout).

The image has the versions of Karpathy's uv.lock at commit 228791f (Python 3.10, torch 2.9.1+cu128), not the
versions of requirements.txt, which is why this study does not run through tools/gpu.py.
"""
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import modal

STUDY = Path(__file__).resolve().parent.parent
PREPARE_SHA256 = "4f2ba9cbb8ba8c4a3d35be405a913e2f3be3af9aea103ed52ef7b2a662058150"  # data/karpathy-228791f/SHA256SUMS
CACHE = "/root/.cache/autoresearch"   # where the pinned prepare.py keeps the shards and the tokenizer
HOLDOUT_SHARD = 6541                  # val is shard 6542; training uses shards 0 to 9
HOLDOUT_FILE = f"/holdout/shard_{HOLDOUT_SHARD:05d}.parquet"
WALL_LIMIT = 600                      # seconds; program.md: "If a run exceeds 10 minutes, kill it"
ARM = re.compile(r"[a-z][a-z0-9-]{0,30}")

image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("build-essential")
    .pip_install("torch==2.9.1", index_url="https://download.pytorch.org/whl/cu128")
    .pip_install("kernels==0.12.1", "huggingface-hub==1.5.0", "numpy==2.2.6", "pandas==2.3.3", "pyarrow==23.0.1",
                 "requests==2.32.5", "rustbpe==0.1.0", "tiktoken==0.12.0", "regex==2026.2.19", "matplotlib==3.10.8")
    .env({"HF_HOME": f"{CACHE}/hf", "PYTHONUNBUFFERED": "1", "AUTOBENCH_PREPARE_SHA256": PREPARE_SHA256})
    .add_local_file(str(STUDY / "data/karpathy-228791f/prepare.py"), "/trusted/prepare.py", copy=True)
    .add_local_file(str(STUDY / "lib/launch.py"), "/trusted/launch.py", copy=True)
)
data = modal.Volume.from_name("autobench-data", create_if_missing=True)
holdout = modal.Volume.from_name("autobench-holdout", create_if_missing=True)
runs = modal.Volume.from_name("autobench-runs", create_if_missing=True)
ledger = modal.Dict.from_name("autobench-ledger", create_if_missing=True)

app = modal.App("autobench")
gpu_job = dict(image=image, gpu="H100", cpu=8, memory=32768, timeout=WALL_LIMIT + 300, retries=0, block_network=True,
               restrict_modal_access=True, single_use_containers=True, max_containers=6)


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def run_train(source, holdout_file=None):
    """Run one train.py under the launcher; return its log, the launcher's record and the wall-clock seconds."""
    gpu = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], capture_output=True, text=True,
                         check=True).stdout.strip()
    work = tempfile.mkdtemp()
    Path(work, "train.py").write_text(source)
    record_path = Path(tempfile.mkdtemp()) / "record.json"
    env = {**os.environ, "AUTOBENCH_RECORD": str(record_path), "HF_HUB_OFFLINE": "1"}
    if holdout_file:
        env["AUTOBENCH_HOLDOUT"] = holdout_file
    start = time.time()
    with open(Path(work, "log"), "w") as log:
        proc = subprocess.Popen([sys.executable, "/trusted/launch.py"], cwd=work, env=env, stdout=log,
                                stderr=subprocess.STDOUT, start_new_session=True)
        try:
            proc.wait(timeout=WALL_LIMIT)
            timed_out = False
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
            timed_out = True
    return {"exit_code": proc.returncode, "timed_out": timed_out, "wall_seconds": round(time.time() - start, 1),
            "gpu": gpu, "cpus": os.cpu_count(), "log": Path(work, "log").read_text(errors="replace"),
            "record": json.loads(record_path.read_text()) if record_path.exists() else None}


@app.function(volumes={CACHE: data.read_only()}, **gpu_job)
def train_job(source: str):
    return run_train(source)


@app.function(volumes={CACHE: data.read_only(), "/holdout": holdout.read_only()}, **gpu_job)
def train_job_holdout(source: str):
    return run_train(source, HOLDOUT_FILE)


def run_and_store(key, folder, source, job):
    """Run a claimed experiment, store its files in the Volume autobench-runs and its row in the ledger."""
    row = ledger[key]
    try:
        result = job.remote(source)
    except Exception as error:
        ledger[key] = {**row, "state": "infra_error", "error": repr(error), "ended_at": now()}
        raise
    log = result.pop("log")
    evals = (result["record"] or {}).get("evals", [])
    row = {**row, "state": "done", "ended_at": now(), "exit_code": result["exit_code"], "timed_out": result["timed_out"],
           "wall_seconds": result["wall_seconds"], "gpu": result["gpu"], "cpus": result["cpus"], "n_evals": len(evals),
           "val_bpb": evals[-1]["val_bpb"] if evals else None, "test_bpb": evals[-1].get("test_bpb") if evals else None,
           "val_loader_refused": (result["record"] or {}).get("val_loader_refused"), "folder": folder}
    out = Path("/runs") / folder
    out.mkdir(parents=True)
    (out / "train.py").write_text(source)
    (out / "log").write_text(log)
    (out / "record.json").write_text(json.dumps({**row, "record": result["record"]}, indent=1))
    runs.commit()
    ledger[key] = row
    return row, log


def claim(prefix, limit, source):
    """Take the first free number under prefix, atomically; None when all `limit` numbers are taken."""
    for n in range(limit):
        row = {"n": n, "state": "running", "claimed_at": now(), "train_sha256": hashlib.sha256(source.encode()).hexdigest()}
        if ledger.put(f"{prefix}:{n:03d}", row, skip_if_exists=True):
            return n
    return None


@app.function(image=image, volumes={"/runs": runs}, timeout=WALL_LIMIT + 3600)
def submit(arm: str, source: str):
    if not ARM.fullmatch(arm):
        raise ValueError(f"arm name {arm!r}")
    budget = ledger[f"budget:{arm}"]   # KeyError: the operator has not run `run_exp.py init <arm> <budget>`
    n = claim(f"exp:{arm}", budget, source)
    if n is None:
        return {"exhausted": True, "budget": budget}
    row, log = run_and_store(f"exp:{arm}:{n:03d}", f"{arm}/{n:03d}", source, train_job)
    return {"exhausted": False, "n": n, "budget": budget, "log": log, "exit_code": row["exit_code"],
            "timed_out": row["timed_out"]}


@app.function(image=image, volumes={"/runs": runs}, timeout=WALL_LIMIT + 3600)
def score_final(label: str, source: str):
    if not ARM.fullmatch(label):
        raise ValueError(f"label {label!r}")
    n = claim(f"final:{label}", 100, source)
    row, _ = run_and_store(f"final:{label}:{n:03d}", f"final/{label}-{n:03d}", source, train_job_holdout)
    return row


@app.function(image=image, cpu=8, memory=16384, volumes={CACHE: data}, timeout=3600)
def prep():
    """The pinned prepare.py, unchanged: 10 training shards, the val shard, the tokenizer."""
    subprocess.run([sys.executable, "/trusted/prepare.py"], check=True)
    data.commit()
    return {name: os.path.getsize(f"{CACHE}/data/{name}") for name in sorted(os.listdir(f"{CACHE}/data"))}


@app.function(image=image, gpu="H100", volumes={CACHE: data}, timeout=900)
def warm():
    """Download the attention kernel that train.py loads (its lines 21 to 24) into the Volume, because train_job
    has no network."""
    import torch
    from kernels import get_kernel

    cap = torch.cuda.get_device_capability()
    repo = "varunneal/flash-attention-3" if cap == (9, 0) else "kernels-community/flash-attn3"
    get_kernel(repo).flash_attn_interface
    data.commit()
    return {"capability": cap, "kernel": repo}


@app.function(image=image, volumes={"/holdout": holdout}, timeout=900)
def prep_holdout():
    sys.path.insert(0, "/trusted")
    import prepare

    prepare.DATA_DIR = "/holdout"
    if not prepare.download_single_shard(HOLDOUT_SHARD):
        raise RuntimeError("holdout shard not downloaded")
    holdout.commit()
    return {HOLDOUT_FILE: os.path.getsize(HOLDOUT_FILE)}
