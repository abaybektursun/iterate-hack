"""One record per command of board.py, gpu.py and paper.py, for whoever analyzes how the team worked.

Stored in the Modal Dict "iterate-events" under ev:<time in ns>:<who>, so writers never collide. Each record has the
time, the person, the agent (claude-code or codex, with its session id; "human" when no agent ran it), the commit,
the tool, and the full command line. tools/traces.py export copies it to the Volume iterate-traces.
"""
import os
import subprocess
import time


def agent():
    if os.environ.get("CODEX_SESSION_ID"):  # checked first: a Codex started from Claude Code inherits its variables
        return {"agent": f"codex {os.environ.get('CODEX_VERSION', '')}".strip(), "session": os.environ["CODEX_SESSION_ID"]}
    if os.environ.get("CLAUDE_CODE_SESSION_ID"):
        return {"agent": os.environ.get("AI_AGENT", "claude-code"), "session": os.environ["CLAUDE_CODE_SESSION_ID"],
                "child": os.environ.get("CLAUDE_CODE_CHILD_SESSION") == "1"}
    return {"agent": "human", "session": ""}


def log(tool, argv, who):
    import modal

    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    record = {"at": time.strftime("%Y-%m-%d %H:%M:%S"), "who": who, **agent(), "sha": sha, "tool": tool, "argv": argv}
    modal.Dict.from_name("iterate-events", create_if_missing=True)[f"ev:{time.time_ns()}:{who}"] = record
