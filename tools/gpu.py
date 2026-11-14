# /// script
# requires-python = ">=3.11"
# dependencies = ["modal>=1.4"]
# ///
"""Submit jobs to the team's GPU pool and see what everyone is running.

  uv run tools/gpu.py submit <class> [--hours 2] -- <command>   class: h100, b200, cpu
  uv run tools/gpu.py ls [--all]          queued and running jobs; --all adds finished ones
  uv run tools/gpu.py logs <job-id> [n]   last n lines of the job's log (default 30)
  uv run tools/gpu.py kill <job-id>

A job runs the current commit: the tree must be clean and the commit pushed. The command runs from the
repository root and writes its outputs to $OUT_DIR. Download them with
  modal volume get iterate-runs <job-id> runs/<job-id>
The log is updated every 30 seconds. The pool itself is infra/pool.py.
"""
import io
import secrets
import subprocess
import sys
import time

import modal

PER_PERSON = 4  # queued plus running jobs per person
CLASSES = ("h100", "b200", "cpu")
jobs = modal.Dict.from_name("iterate-jobs", create_if_missing=True)


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout.strip()


def load():
    """Merge the per-writer keys (job, call, start, end, cancel) into one record per job."""
    records = {}
    for key, value in jobs.items():
        kind, job_id = key.split(":", 1)
        records.setdefault(job_id, {"id": job_id})[kind] = value
    return records


def state(r):
    if "end" in r:
        return "done" if r["end"]["exit_code"] == 0 else ("timeout" if r["end"]["timed_out"] else f"exit {r['end']['exit_code']}")
    if "cancel" in r:
        return "cancelled"
    if "call" not in r:
        return "submitting"
    try:
        modal.FunctionCall.from_id(r["call"]).get(timeout=0)
    except TimeoutError:
        return "running" if "start" in r else "queued"
    except Exception as e:  # the container died without writing its end record; the name says how
        return f"died: {type(e).__name__}"
    return "done"


def submit(args):
    gpu_class, rest = args[0], args[1:]
    assert gpu_class in CLASSES, f"class must be one of {CLASSES}"
    hours = 2.0
    if rest[0] == "--hours":
        hours, rest = float(rest[1]), rest[2:]
    assert rest[0] == "--", "put the command after --"
    cmd = " ".join(rest[1:])

    assert not git("status", "--porcelain"), "commit your changes first: a job runs one commit"
    sha = git("rev-parse", "HEAD")
    assert git("branch", "-r", "--contains", sha), "push the commit first, so others can read the code"
    who = git("config", "user.email").split("@")[0]
    active = [r for r in load().values() if r["job"]["who"] == who and state(r) in ("queued", "running")]
    if len(active) >= PER_PERSON:
        sys.exit(f"{who} already has {len(active)} queued or running jobs; the limit is {PER_PERSON}")

    volume = modal.Volume.from_name("iterate-code", create_if_missing=True)
    if f"{sha}.tar" not in {entry.path for entry in volume.listdir("/")}:
        tar = subprocess.run(["git", "archive", "--format=tar", sha], capture_output=True, check=True).stdout
        with volume.batch_upload() as upload:
            upload.put_file(io.BytesIO(tar), f"/{sha}.tar")

    job_id = f"{who}-{time.strftime('%m%d-%H%M%S')}-{secrets.token_hex(2)}"
    jobs[f"job:{job_id}"] = {"who": who, "class": gpu_class, "sha": sha, "cmd": cmd, "hours": hours, "at": int(time.time())}
    call = modal.Function.from_name("iterate-pool", gpu_class).spawn(job_id)
    jobs[f"call:{job_id}"] = call.object_id
    print(job_id)


def ls(args):
    rows = sorted(load().values(), key=lambda r: r["job"]["at"])
    for r in rows:
        s = state(r)
        if "--all" not in args and s not in ("queued", "running"):
            continue
        j = r["job"]
        minutes = (time.time() - j["at"]) / 60
        gpu = r["start"]["gpu"] if "start" in r else j["class"]
        print(f"{r['id']}  {s}  {gpu}  {minutes:.0f}m  {j['sha'][:7]}  {j['cmd'][:80]}")


def logs(args):
    job_id, n = args[0], int(args[1]) if len(args) > 1 else 30
    data = b"".join(modal.Volume.from_name("iterate-runs").read_file(f"{job_id}/log"))
    print("\n".join(data.decode(errors="replace").splitlines()[-n:]))


def kill(args):
    (job_id,) = args
    r = load()[job_id]
    modal.FunctionCall.from_id(r["call"]).cancel()
    jobs[f"cancel:{job_id}"] = {"at": int(time.time()), "by": git("config", "user.email").split("@")[0]}


if __name__ == "__main__":
    command, *args = sys.argv[1:] or ["help"]
    {"submit": submit, "ls": ls, "logs": logs, "kill": kill}.get(command, lambda _: sys.exit(__doc__))(args)
