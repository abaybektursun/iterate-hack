# /// script
# requires-python = ">=3.11"
# dependencies = ["modal>=1.4", "boto3>=1.35"]
# ///
"""Submit GPU jobs to your own Modal workspace (deploy infra/runner.py there once) and inspect them.

  uv run tools/gpu.py submit <class> [--hours 2] -- <command>   class: h100, b200, cpu
  uv run tools/gpu.py ls [--all]          jobs of the last 3 hours, any state; --all: every job
  uv run tools/gpu.py wait <job-id>       block until the job ends, then print its state and last 20 log lines
  uv run tools/gpu.py logs <job-id> [n]   last n lines of the job's log (default 30)
  uv run tools/gpu.py kill <job-id>       a queued job never starts; a running one is ended within about 30 s
  uv run tools/gpu.py get <job-id>        copy the job's $OUT_DIR (outputs and log) to runs/<job-id>/

The command is a shell string: one quoted argument, e.g.
  uv run tools/gpu.py submit cpu -- 'pip install -q einops && python exp/train.py --lr 3e-4'
Several arguments are quoted one by one and joined.

A job runs the current commit: the tree must be clean and the commit pushed. The command runs from the
repository root and writes its outputs to $OUT_DIR. The log is updated every 30 seconds. Jobs, outputs and the
model cache are in your own workspace: teammates cannot read them, so commit small result files to share them.
The runner ends a job whose log gets no new line for 15 minutes (it holds a GPU and is most likely hung), so a
long silent step should print a line now and then; ls then shows "stopped: no new log line for 15 min".
"""
import io
import secrets
import shlex
import subprocess
import sys
import time

import modal

import team

CLASSES = ("h100", "b200", "cpu")
jobs = modal.Dict.from_name("iterate-jobs", create_if_missing=True)


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout.strip()


def load():
    """Merge the per-writer keys (job, call, start, end, cancel, died) into one record per job."""
    records = {}
    for key, value in jobs.items():
        kind, job_id = key.split(":", 1)
        records.setdefault(job_id, {"id": job_id})[kind] = value
    return records


def state(r):
    if "end" in r and r["end"].get("stopped"):  # the runner ended it: cancelled, silent too long, or over its hours
        return f"stopped: {r['end']['stopped']}"
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
    except Exception as e:  # the container died without writing its end record; the error says how
        if "died" not in r:  # the first time anyone sees it dead: tools/cycle.py ends the job's run here
            r["died"] = {"at": int(time.time())}
            jobs[f"died:{r['id']}"] = r["died"]
        return f"died: {type(e).__name__}: {str(e)[:120]}"
    return "done"


def submit(args):
    gpu_class, rest = args[0], args[1:]
    assert gpu_class in CLASSES, f"class must be one of {CLASSES}"
    hours = 2.0
    if rest[0] == "--hours":
        hours, rest = float(rest[1]), rest[2:]
    assert rest[0] == "--", "put the command after --"
    cmd = rest[1] if len(rest) == 2 else shlex.join(rest[1:])

    assert not git("status", "--porcelain"), "commit your changes first: a job runs one commit"
    sha = git("rev-parse", "HEAD")
    assert git("branch", "-r", "--contains", sha), "push the commit first, so others can read the code"
    who = team.who()

    # Upload on every submit, overwriting: the file is named by its commit, so the bytes are the same. Checking
    # first with listdir hits Modal's rate limit when many agents submit at once.
    tar = subprocess.run(["git", "archive", "--format=tar", sha], capture_output=True, check=True).stdout
    with modal.Volume.from_name("iterate-code", create_if_missing=True).batch_upload(force=True) as upload:
        upload.put_file(io.BytesIO(tar), f"/{sha}.tar")

    job_id = f"{who}-{time.strftime('%m%d-%H%M%S')}-{secrets.token_hex(2)}"
    branch = git("rev-parse", "--abbrev-ref", "HEAD")  # tools/cycle.py matches jobs to work items by branch
    jobs[f"job:{job_id}"] = {"who": who, "class": gpu_class, "sha": sha, "cmd": cmd, "hours": hours, "at": int(time.time()), "branch": branch}
    try:
        call = modal.Function.from_name("iterate-runner", gpu_class).spawn(job_id)
    except Exception:  # Modal rejected the job (spend limit): without this its record stays in "submitting" for ever
        del jobs[f"job:{job_id}"]
        raise
    jobs[f"call:{job_id}"] = call.object_id
    print(job_id)
    if sum(key.startswith("job:") for key in jobs.keys()) % 5 == 0 and not team.review_loop(who):
        print("This is your 5th job since the last multiple of 5: run the team-meta-review skill (uv run tools/cycle.py first).", file=sys.stderr)


def ls(args):
    rows = sorted(load().values(), key=lambda r: r["job"]["at"])
    for r in rows:
        if "--all" not in args and time.time() - r["job"]["at"] > 3 * 3600:
            continue
        s = state(r)
        j = r["job"]
        minutes = (time.time() - j["at"]) / 60
        gpu = r["start"]["gpu"] if "start" in r else j["class"]
        print(f"{r['id']}  {s}  {gpu}  {minutes:.0f}m  {j['sha'][:7]}  {j['cmd'][:80]}")


def logs(args):
    job_id, n = args[0], int(args[1]) if len(args) > 1 else 30
    try:
        data = b"".join(modal.Volume.from_name("iterate-runs").read_file(f"{job_id}/log"))
    except FileNotFoundError:
        sys.exit(f"{job_id} has no log yet; state: {state(load()[job_id])}")
    print("\n".join(data.decode(errors="replace").splitlines()[-n:]))


def wait(args):
    (job_id,) = args
    while (s := state(load()[job_id])) in ("submitting", "queued", "running"):
        time.sleep(10)
    print(s)
    if not s.startswith("died") and s != "cancelled":
        logs([job_id, 20])


def get(args):
    (job_id,) = args
    subprocess.run(["mkdir", "-p", "runs"], check=True)
    subprocess.run([sys.executable, "-m", "modal", "volume", "get", "iterate-runs", job_id, "runs/"], check=True)


def kill(args):
    (job_id,) = args
    r = load()[job_id]
    modal.FunctionCall.from_id(r["call"]).cancel()
    jobs[f"cancel:{job_id}"] = {"at": int(time.time()), "by": team.who()}


if __name__ == "__main__":
    import events

    if {"--help", "-h"} & set(sys.argv[: sys.argv.index("--") if "--" in sys.argv else None]):
        sys.exit(__doc__)
    events.log("gpu", sys.argv[1:], team.who())
    command, *args = sys.argv[1:] or ["help"]
    {"submit": submit, "ls": ls, "wait": wait, "logs": logs, "kill": kill, "get": get}.get(command, lambda _: sys.exit(__doc__))(args)
