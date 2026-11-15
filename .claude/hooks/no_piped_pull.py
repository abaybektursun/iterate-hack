"""PreToolUse hook for Bash: refuse `git pull` or `git merge` piped into another command.

A pipe returns the exit status of its last command, so `git merge origin/main 2>&1 | tail -3` reports success when
the merge stopped on a conflict or was aborted. Exit 2 refuses the call and shows the reason to the agent.
"""
import json
import re
import sys

cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "")
for part in re.split(r"&&|\|\||;|\n", cmd):
    if re.search(r"\bgit\s+(pull|merge)(\s|$)", part) and "|" in part:
        print("Refused: a pipe after `git pull` or `git merge` hides its exit status. Run it without the pipe "
              "(add -q to keep the output short) and check `git status` after it.", file=sys.stderr)
        sys.exit(2)
