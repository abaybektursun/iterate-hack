"""One record per command of board.py, gpu.py and paper.py, for whoever analyzes how the team worked.

Stored in the team store (tools/team.py, S3), prefix events, under ev:<time in ns>:<who>, so writers never collide.
Each record has the time, the person, the agent (claude-code or codex, with its session id; "human" when no agent
ran it), the commit, the tool, and the full command line.
"""
import os
import subprocess
import time

import team


def agent():
    """Who is running: the agent type, its session id, and its git branch. Subagents share their parent's session
    id, and every agent works on its own branch, so the branch is what tells two agents of one session apart."""
    branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True).stdout.strip()
    return {**session(), "branch": branch}


def session():
    if os.environ.get("CODEX_SESSION_ID"):  # checked first: a Codex started from Claude Code inherits its variables
        return {"agent": f"codex {os.environ.get('CODEX_VERSION', '')}".strip(), "session": os.environ["CODEX_SESSION_ID"]}
    if os.environ.get("CLAUDE_CODE_SESSION_ID"):
        return {"agent": os.environ.get("AI_AGENT", "claude-code"), "session": os.environ["CLAUDE_CODE_SESSION_ID"],
                "child": os.environ.get("CLAUDE_CODE_CHILD_SESSION") == "1"}
    return {"agent": "human", "session": ""}


def log(tool, argv, who):
    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    record = {"at": team.now(), "who": who, **agent(), "sha": sha, "tool": tool, "argv": argv}
    team.Store("events")[f"ev:{time.time_ns()}:{who}"] = record
