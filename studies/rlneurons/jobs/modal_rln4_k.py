"""RLN-4 K cell (studies/rlneurons/SPEC4.md §2, §6, §7) on Modal: the AWS job's child (studies/rlneurons/jobs/rln4_gen.run) on Modal GPUs.

    modal run studies/rlneurons/jobs/modal_rln4_k.py --step download                 # both snapshots into the rln4-hf Volume, G-WEIGHTS sha256 check
    modal run studies/rlneurons/jobs/modal_rln4_k.py --step check --prefix modal_k-01 # base F, problems 0-49, base-01's seeds (SPEC4 §6)
    modal run studies/rlneurons/jobs/modal_rln4_k.py --step k --prefix modal_k-01     # K_rl + K_own on one GPU, K_fresh (+ K_fresh2) on another
    modal run --detach studies/rlneurons/jobs/modal_rln4_k.py --step t2 --prefix modal_t2-01 --stop-utc <launch + spend limit>  # RL check, then T2
    modal run --detach studies/rlneurons/jobs/modal_rln4_k.py --step t3 --prefix modal_t3-01 --stop-utc <...>                   # T3 (base plain, T 1.0)

Every request, seed, prefix, sampling and cap comes from rln4_gen.run and the frozen inputs (s3 .../r4/inputs/, sha256 against
frozen4.json); this file only provides the GPU, the weights and the copying. The child writes <out>/<cell>.jsonl per request and
<out>/metrics.json; the parent copies <out> to s3://pg-lineage-769063704696/results/rlneurons/r4/<prefix>/<sub>/ every 60 s and
commits the rln4-out Volume. Engine build as the AWS job: vLLM 0.32.0, math-verify 0.9.0, then transformers 5.19.0 / tokenizers
0.23.3 (rln4_gen.TOKENIZER_PINS). Fail loud: no try/except, no fallback.
"""
import pathlib
import time

import modal

BUCKET = "pg-lineage-769063704696"
S3_INPUTS = "results/rlneurons/r4/inputs/"
S3_OUT = "results/rlneurons/r4/"
GPU = "H100"
ROOT = pathlib.Path(__file__).resolve().parents[3]       # repository root
PY = modal.FilePatternMatcher("**/*.py")

image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("gcc")                      # torch inductor / Triton compile a C stub at engine start (n13_setup.python_headers)
    .pip_install("vllm==0.32.0", "math-verify==0.9.0")
    .pip_install("transformers==5.19.0", "tokenizers==0.23.3", "boto3")
    .env({"VLLM_USE_FLASHINFER_SAMPLER": "0", "HF_HOME": "/vol/hf", "HF_HUB_DISABLE_XET": "1", "PYTHONPATH": "/repo"})
    .add_local_dir(ROOT / "studies/rlneurons", "/repo/studies/rlneurons", ignore=~PY)
)
vol_hf = modal.Volume.from_name("rln4-hf", create_if_missing=True)
vol_out = modal.Volume.from_name("rln4-out", create_if_missing=True)
app = modal.App("rln4-k", secrets=[modal.Secret.from_name("hf-token"), modal.Secret.from_name("rln4-aws")])


def inputs(dst):
    import boto3
    from studies.rlneurons.jobs import rln4_gen as J
    dst = pathlib.Path(dst)
    dst.mkdir(parents=True, exist_ok=True)
    s3 = boto3.client("s3", region_name="us-east-1")
    for f in J.INPUTS:
        s3.download_file(BUCKET, S3_INPUTS + f, str(dst / f))
    return dst


def snapshot(fz, model):
    repo, _, rev = fz["models"][model]
    return f"/vol/hf/hub/models--{repo.replace('/', '--')}/snapshots/{rev}"


@app.function(image=image, volumes={"/vol/hf": vol_hf}, timeout=3600, cpu=8.0, memory=16384)
def download(model: str) -> dict:
    import json
    import os
    from studies.rlneurons.lib.hf_helpers import hf_setup
    assert os.environ.get("HF_TOKEN"), "the hf-token secret has no HF_TOKEN"
    hf_setup()
    from studies.rlneurons.jobs import rln4_gen as J
    fz = json.loads((inputs("/tmp/inputs") / "frozen4.json").read_text())
    rec = J.weights(model, fz, None)            # snapshot_download at the frozen commit + every shard's sha256 = HF LFS oid
    assert pathlib.Path(rec["dir"]).resolve() == pathlib.Path(snapshot(fz, model)).resolve(), (rec["dir"], snapshot(fz, model))
    vol_hf.commit()
    return rec


def upload(s3, out, key):
    for p in sorted(out.iterdir()):
        if p.is_file() and not p.name.endswith(".tmp"):
            s3.upload_file(str(p), BUCKET, key + p.name)


TIMEOUT_S = 2 * 3600


@app.function(image=image, gpu=GPU, volumes={"/vol/hf": vol_hf, "/vol/out": vol_out}, timeout=TIMEOUT_S, cpu=8.0, memory=65536)
def gen(prefix: str, sub: str, phase: str, arms: str, stop_utc: str, model: str = "base", gate: str = "") -> dict:
    """gate: a check.json on the rln4-out Volume whose verdict must be 'pass' before this phase runs."""
    import json
    import os
    import subprocess
    import sys
    import boto3
    from studies.rlneurons.lib import n13_gen as G
    from studies.rlneurons.jobs import rln4_gen as J
    out = pathlib.Path("/vol/out") / prefix / sub
    assert not out.exists(), f"{out} exists: one fresh prefix per attempt"
    out.mkdir(parents=True)
    key = f"{S3_OUT}{prefix}/{sub}/"
    s3 = boto3.client("s3", region_name="us-east-1")
    assert s3.list_objects_v2(Bucket=BUCKET, Prefix=key)["KeyCount"] == 0, f"s3://{BUCKET}/{key} is not empty"
    ind = inputs(f"/tmp/inputs_{sub}")
    fz = json.loads((ind / "frozen4.json").read_text())
    if gate:
        chk = json.loads((pathlib.Path("/vol/out") / gate).read_text())
        assert chk["verdict"] == "pass", f"{gate}: verdict {chk['verdict']}: {phase} does not run"
    # The stop is set at launch for the spend limit (SPEC4 Deviations); it must fall inside the function timeout so that the child
    # aborts, lists and saves before Modal kills the container.
    assert J.epoch(stop_utc) <= time.time() + TIMEOUT_S - 600, f"stop {stop_utc} is not 10 minutes inside the {TIMEOUT_S} s timeout"
    shift = J.epoch(stop_utc) - J.epoch(fz["stop_utc"])
    freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"], check=True, capture_output=True, text=True).stdout
    (out / "pip_freeze.txt").write_text(freeze)
    pins = dict(l.split("==") for l in freeze.splitlines() if "==" in l)
    want = {"vllm": "0.32.0", "math-verify": "0.9.0", **J.TOKENIZER_PINS}
    assert all(pins.get(k) == v for k, v in want.items()), {k: pins.get(k) for k in want}
    gpu = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], check=True, capture_output=True, text=True).stdout.strip()
    run = {"app": "rln4-k", "phase": phase, "arms": arms, "gpu": gpu, "modal_gpu": GPU, "stop_utc": stop_utc, "time_shift_s": shift,
           "frozen_stop_utc": fz["stop_utc"], "pins": {k: pins[k] for k in want}, "started_utc": J.utc(),
           "model": model, "gate": gate, "model_dir": snapshot(fz, model), "tok_dir": snapshot(fz, "s2800")}
    (out / "run.json").write_text(json.dumps(run, indent=1))
    log = open(f"/tmp/child_{sub}.log", "w")
    p = subprocess.Popen([sys.executable, "-m", "studies.rlneurons.jobs.rln4_gen", "--inner", "--phase", phase, "--arms", arms, "--out", str(out),
                          "--model-dir", run["model_dir"], "--tok-dir", run["tok_dir"], "--inputs-dir", str(ind), "--time-shift", str(shift)],
                         env=G.child_env(os.environ), cwd="/repo", stdout=log, stderr=subprocess.STDOUT)
    while p.poll() is None:
        time.sleep(60)
        upload(s3, out, key)
        vol_out.commit()
    log.close()
    run.update(rc=p.returncode, finished_utc=J.utc(), seconds=time.time() - J.epoch(run["started_utc"]))
    (out / "run.json").write_text(json.dumps(run, indent=1))
    (out / "child.log").write_bytes(pathlib.Path(f"/tmp/child_{sub}.log").read_bytes())
    upload(s3, out, key)
    vol_out.commit()
    assert p.returncode == 0, f"{sub}: child exited {p.returncode}; log s3://{BUCKET}/{key}child.log"
    return run


@app.local_entrypoint()
def main(step: str, prefix: str = "", stop_utc: str = "2026-11-14T13:18:00Z"):
    if step == "download":
        for rec in download.map(["base", "s2800"]):
            print({k: rec[k] for k in ("repo", "commit", "n_shards", "retries", "pass")})
    elif step == "check":
        print(gen.remote(prefix, "check", "check", "", stop_utc))
    elif step == "k":
        gate = f"{prefix}/check/check.json"
        calls = [gen.spawn(prefix, "k_a", "k", "K_rl,K_own", stop_utc, gate=gate), gen.spawn(prefix, "k_b", "k", "K_fresh", stop_utc, gate=gate)]
        for c in calls:
            print(c.get())
    elif step == "t2":      # RL check (problems 0-49 at T 0.6 against n13's RL), then T2, one engine; run with `modal run --detach`
        print(gen.remote(prefix, "t2", "rl_check", "", stop_utc, model="s2800"))
    elif step == "t3":      # T3 alone; gated on the base check of modal_k-01 (42 of 50, pass)
        print(gen.remote(prefix, "t3", "t3", "", stop_utc, model="base", gate="modal_k-01/check/check.json"))
    else:
        raise ValueError(step)
