# /// script
# requires-python = ">=3.11"
# dependencies = ["modal>=1.4"]
# ///
"""Agent traces, for whoever analyzes how the team worked.

  uv run tools/traces.py push      upload your agent transcripts for this repository and your GPU job records

push copies every Claude Code transcript (subagents included) and every Codex session whose working folder is this
repository or one of its worktrees to the team store (tools/team.py), folder traces/<who>/, and the records of your
GPU jobs (the Dict iterate-jobs in your Modal workspace) to traces/<who>/jobs.json. A transcript holds everything
typed and every tool output, file contents included. Strings that look like keys are replaced with [REDACTED]
first; that catches common formats only, so run push only on transcripts you are willing to share. Running it
again uploads the current versions. The analyst reads everything by cloning abaybektursun/iterate-hack-team.
"""
import json
import re
import subprocess
import sys
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
    team.sync()
    out = team.DIR / "traces" / who
    jobs = dict(modal.Dict.from_name("iterate-jobs", create_if_missing=True).items())
    out.mkdir(parents=True, exist_ok=True)
    (out / "jobs.json").write_text(json.dumps(jobs, indent=1, sort_keys=True))
    count = 0
    for source, path, name in transcripts():
        target = out / source / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(redact(path.read_text(errors="replace")))
        count += 1
    team.push(f"traces: {who}")
    print(f"pushed {count} transcripts and {len(jobs)} job records to {team.REPO}, traces/{who}/")


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "help"
    email = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True, check=True).stdout
    {"push": lambda: push(email.strip().split("@")[0])}.get(command, lambda: sys.exit(__doc__))()
