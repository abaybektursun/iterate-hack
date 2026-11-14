"""Rent your own GPU on vast.ai, with your own account and credit. Nothing here is shared with the team:
the instances, the costs and the records in runs/vast/ belong to whoever runs it.

  python3 tools/vast.py offers [--ram 24] [--n 10]          cheapest offers with at least that many GB of GPU memory
  python3 tools/vast.py up <offer-id> [--hours 3] [--image <image>]
                                                            rent it, check its download speed, wait until ready;
                                                            the box destroys itself --hours after it boots
  python3 tools/vast.py run <instance-id> -- '<command>'    run the current commit there; prints the job id
  python3 tools/vast.py logs <instance-id> <job-id> [n]     last n lines of the job's log (default 30)
  python3 tools/vast.py get <instance-id> <job-id>          copy the job's $OUT_DIR to runs/<job-id>/
  python3 tools/vast.py ls                                  your instances: state, $/h, hours since start
  python3 tools/vast.py down <instance-id>                  destroy it now; stopped instances still bill storage

Setup once: `uv tool install vastai`, `vastai set api-key <your key>` (in your terminal, not in a chat), and add your
ssh public key at https://cloud.vast.ai/manage-keys/.

The default image is the official pytorch image with requirements.txt installed on top, the same versions as the
Modal pool. --image takes any other image; README.md lists the team's ECR images. Install anything else in the
command, with `python -m pip install -q --break-system-packages <pkg> && python exp/run.py`. A job runs one clean, pushed commit, from
the repository root, and writes its outputs to $OUT_DIR. The deadline runs on the box itself, with the instance's own
key, so it fires even when your laptop is closed. Copy results out before it fires: destroying deletes the disk.
"""
import json
import secrets
import shlex
import subprocess
import sys
import time
from pathlib import Path

IMAGE = "pytorch/pytorch:2.15.0-cuda13.2-cudnn9-runtime"  # the same torch as the Modal pool
ECR = "769063704696.dkr.ecr.us-east-1.amazonaws.com"
FILTER = "num_gpus=1 verified=true reliability>0.98 rentable=true inet_down>=500 cuda_vers>=13.2 disk_space>=100"
ROOT = Path(__file__).resolve().parent.parent
RECORDS = ROOT / "runs" / "vast"
MIN_MB_S = 20      # a box that downloads slower than this is destroyed at once (9 of 32 earlier rentals were slow)
BOOT_MINUTES = 20  # a box not reachable by ssh within this time is destroyed
# The deadline: python and the instance's own key, so it works on any image and with the laptop closed.
DESTROY = ("python3 -c \"import os, urllib.request as u; u.urlopen(u.Request("
           "'https://console.vast.ai/api/v0/instances/' + os.environ['CONTAINER_ID'] + '/', method='DELETE', "
           "headers={'Authorization': 'Bearer ' + os.environ['CONTAINER_API_KEY']}))\"")
SPEED = ("python3 -c \"import time, urllib.request as u; t = time.time(); r = u.urlopen(u.Request("
         "'https://huggingface.co/openai-community/gpt2/resolve/main/model.safetensors', "
         "headers={'Range': 'bytes=0-199999999'})); n = len(r.read()); print(n / 1e6 / (time.time() - t))\"")


def sh(*cmd, input=None):
    return subprocess.run(cmd, input=input, capture_output=True, check=True).stdout


def vast(*args):
    return json.loads(sh("vastai", *args, "--raw"))


def ssh_args(url):
    host, port = url.strip().removeprefix("ssh://").rsplit(":", 1)
    return ["ssh", "-o", "StrictHostKeyChecking=accept-new", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", "-p", port, host]


def ssh(instance_id, remote, input=None):
    return sh(*ssh_args(sh("vastai", "ssh-url", instance_id).decode()), remote, input=input)


def reachable(instance_id):
    url = subprocess.run(["vastai", "ssh-url", instance_id], capture_output=True, text=True)
    return url.stdout.startswith("ssh://") and subprocess.run([*ssh_args(url.stdout), "true"], capture_output=True).returncode == 0


def git(*args):
    return sh("git", *args).decode().strip()


def record(name, **fields):
    RECORDS.mkdir(parents=True, exist_ok=True)
    (RECORDS / f"{name}.json").write_text(json.dumps({**fields, "at": time.strftime("%Y-%m-%d %H:%M:%S")}, indent=1))


def offers(args):
    ram = float(args[args.index("--ram") + 1]) if "--ram" in args else 24
    n = int(args[args.index("--n") + 1]) if "--n" in args else 10
    rows = vast("search", "offers", f"{FILTER} gpu_ram>={ram}", "-o", "dph_total")
    for o in rows[:n]:
        print(f"{o['id']}  {o['gpu_name']} {o['gpu_ram'] / 1024:.0f}GB  ${o['dph_total']:.3f}/h  "
              f"{o['total_flops']:.0f}TF  down {o['inet_down']:.0f}Mb/s  rel {o['reliability']:.3f}  {o['geolocation']}")


def up(args):
    offer_id = args[0]
    hours = float(args[args.index("--hours") + 1]) if "--hours" in args else 3.0
    image = args[args.index("--image") + 1] if "--image" in args else IMAGE
    t0 = time.time()
    onstart = f"(sleep {int(hours * 3600)}; {DESTROY}) > /root/deadline.log 2>&1 &"
    if image == IMAGE:  # install the pinned versions, so a job sees the same packages as on the Modal pool
        pins = " ".join(shlex.quote(p) for p in (ROOT / "requirements.txt").read_text().split())
        onstart += f" python -m pip install -q --break-system-packages {pins} > /root/pip.log 2>&1;"
    onstart += " touch /root/ready"
    login = []
    if image.startswith(ECR):  # pull access from the iterate-ecr profile, valid until 2026-11-16 08:00 UTC
        token = sh("aws", "ecr", "get-login-password", "--region", "us-east-1", "--profile", "iterate-ecr").decode().strip()
        login = ["--login", f"-u AWS -p {token} {ECR}"]
    created = vast("create", "instance", offer_id, "--image", image, "--disk", "100", "--ssh", "--direct",
                   "--onstart-cmd", onstart, *login)
    instance_id = str(created["new_contract"])
    print(f"{instance_id} created; waiting for ssh", flush=True)
    while not reachable(instance_id):
        if time.time() - t0 > BOOT_MINUTES * 60:
            down([instance_id])
            sys.exit(f"not reachable after {BOOT_MINUTES} min; destroyed. Try another offer.")
        time.sleep(15)
    booted = time.time() - t0
    mb_s = float(ssh(instance_id, SPEED))
    if mb_s < MIN_MB_S:
        down([instance_id])
        sys.exit(f"downloads at {mb_s:.0f} MB/s, under {MIN_MB_S}; destroyed. Try another offer.")
    ssh(instance_id, "while [ ! -e /root/ready ]; do sleep 2; done")
    record(f"instance-{instance_id}", offer=offer_id, hours=hours, image=image, boot_s=round(booted),
           ready_s=round(time.time() - t0), mb_s=round(mb_s))
    print(f"{instance_id} ready in {time.time() - t0:.0f} s (ssh at {booted:.0f} s, {mb_s:.0f} MB/s); "
          f"destroys itself {hours} h after it booted")


def run(args):
    instance_id, sep, *cmd = args
    assert sep == "--", "put the command after --"
    cmd = cmd[0] if len(cmd) == 1 else shlex.join(cmd)
    assert not git("status", "--porcelain"), "commit your changes first: a job runs one commit"
    sha = git("rev-parse", "HEAD")
    assert git("branch", "-r", "--contains", sha), "push the commit first, so the job can be traced to its code"
    who = git("config", "user.email").split("@")[0]
    job_id = f"{who}-{time.strftime('%m%d-%H%M%S')}-{secrets.token_hex(2)}"
    tar = subprocess.run(["git", "archive", "--format=tar", sha], capture_output=True, check=True).stdout
    ssh(instance_id, f"mkdir -p /root/{job_id}/repo /root/{job_id}/out && tar -x -C /root/{job_id}/repo", input=tar)
    job = f"cd /root/{job_id}/repo && OUT_DIR=/root/{job_id}/out JOB_ID={job_id} bash -c {shlex.quote(cmd)}"
    script = f"{{ {job}; echo \"exit $?\"; }} > /root/{job_id}/out/log 2>&1"
    ssh(instance_id, f"setsid nohup bash -c {shlex.quote(script)} > /dev/null 2>&1 < /dev/null &")
    record(job_id, instance=instance_id, sha=sha, cmd=cmd)
    print(job_id)


def logs(args):
    instance_id, job_id = args[:2]
    n = int(args[2]) if len(args) > 2 else 30
    print(ssh(instance_id, f"tail -n {n} /root/{job_id}/out/log").decode(errors="replace"), end="")


def get(args):
    instance_id, job_id = args
    dest = RECORDS.parent / job_id
    dest.mkdir(parents=True, exist_ok=True)
    data = ssh(instance_id, f"tar -c -C /root/{job_id}/out .")
    subprocess.run(["tar", "-x", "-C", str(dest)], input=data, check=True)
    print(dest)


def ls(args):
    for i in vast("show", "instances"):
        hours = (time.time() - i["start_date"]) / 3600 if i.get("start_date") else 0
        print(f"{i['id']}  {i['actual_status']}  {i['gpu_name']}  ${i['dph_total']:.3f}/h  up {hours:.2f} h  {i.get('status_msg') or ''}"[:160])


def down(args):
    (instance_id,) = args
    sh("vastai", "destroy", "instance", instance_id, "-y")
    print(f"destroyed {instance_id}")


if __name__ == "__main__":
    command, *args = sys.argv[1:] or ["help"]
    {"offers": offers, "up": up, "run": run, "logs": logs, "get": get, "ls": ls, "down": down}.get(
        command, lambda _: sys.exit(__doc__))(args)
