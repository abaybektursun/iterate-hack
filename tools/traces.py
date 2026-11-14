# /// script
# requires-python = ">=3.11"
# dependencies = ["modal>=1.4"]
# ///
"""Agent traces and team records, for whoever analyzes how the team worked. Both commands write to the Volume
iterate-traces in the team workspace (tools/team.py).

  uv run tools/traces.py push      upload your agent transcripts for this repository and your GPU job records
  uv run tools/traces.py export    copy the board and the events from their Modal Dicts to the Volume

push uploads every Claude Code transcript (subagents included) and every Codex session whose working folder is this
repository or one of its worktrees, to iterate-traces/<who>/, and the records of your GPU jobs (the Dict
iterate-jobs in your own workspace) to <who>/jobs.json. A transcript holds everything typed and every tool output,
file contents included. Strings that look like keys are replaced with [REDACTED] first; that catches common formats
only, so run push only on transcripts you are willing to share. Running it again uploads the current versions.

export writes iterate-traces/export/<time>/{board,events}.json. The Dicts drop entries after 7 days without reads
or writes; the Volume keeps them. Read everything with
`modal volume get --profile abaybektursun iterate-traces / traces/`.
"""
import io
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import modal

import team

ROOT = Path(__file__).resolve().parent.parent
PREFIX = str(ROOT)  # the main checkout and its ../<repository>-<name> worktrees
KEYS = re.compile(r"past_sk_\w+|sk-[\w-]{20,}|AKIA[0-9A-Z]{16}|gh[pousr]_\w{30,}|hf_\w{30,}|xox[abp]-[\w-]+")
ASSIGNED = re.compile(r"(?i)([\w-]*(?:key|token|secret|password|authorization)\\?[\"']?\s*[:=]\s*\\?[\"']?(?:Bearer\s+)?)"
                      r"[\w./+=-]{16,}")


def redact(text):
    return ASSIGNED.sub(r"\1[REDACTED]", KEYS.sub("[REDACTED]", text))


def transcripts():
    claude = Path.home() / ".claude" / "projects"
    escaped = re.sub(r"[^A-Za-z0-9]", "-", PREFIX)
    for folder in claude.glob(escaped + "*"):
        for path in folder.rglob("*.jsonl"):
            yield "claude", path, path.relative_to(folder.parent)
    for path in (Path.home() / ".codex" / "sessions").rglob("rollout-*.jsonl"):
        with open(path) as f:
            meta = json.loads(f.readline()).get("payload", {})
        if str(meta.get("cwd", "")).startswith(PREFIX):
            yield "codex", path, path.name


def push(who):
    count = 0
    jobs = dict(modal.Dict.from_name("iterate-jobs", create_if_missing=True).items())
    with team.store(modal.Volume, "iterate-traces").batch_upload(force=True) as upload:
        upload.put_file(io.BytesIO(json.dumps(jobs, indent=1, sort_keys=True).encode()), f"/{who}/jobs.json")
        for source, path, name in transcripts():
            upload.put_file(io.BytesIO(redact(path.read_text(errors="replace")).encode()), f"/{who}/{source}/{name}")
            count += 1
    print(f"uploaded {count} transcripts and {len(jobs)} job records to iterate-traces/{who}/")


def export():
    stamp = time.strftime("%Y%m%d-%H%M%S")
    with team.store(modal.Volume, "iterate-traces").batch_upload(force=True) as upload:
        for name in ("board", "events"):
            data = dict(team.store(modal.Dict, f"iterate-{name}").items())
            upload.put_file(io.BytesIO(json.dumps(data, indent=1, sort_keys=True).encode()), f"/export/{stamp}/{name}.json")
            print(f"{name}: {len(data)} entries")
    print(f"exported to iterate-traces/export/{stamp}/")


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "help"
    email = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True, check=True).stdout
    {"push": lambda: push(email.strip().split("@")[0]), "export": export}.get(command, lambda: sys.exit(__doc__))()
