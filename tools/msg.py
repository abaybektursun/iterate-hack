# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35"]
# ///
"""Messages between agents, delivered within about a second.

  uv run tools/msg.py send <channel> "<text>"       at most 2000 characters
  uv run tools/msg.py read [channel ...]            messages that arrived since this agent last read, oldest first
  uv run tools/msg.py wait [channel ...] [--timeout 300]
                                                    block until a message arrives, then print it; exit code 1 at the timeout
  uv run tools/msg.py read --hook                   for the Claude Code hook in .claude/settings.json: at most one check
                                                    per 20 s, output in the hook's JSON format

A channel is any name made of letters, digits and @ . _ -. Conventions: `all` reaches everyone; `@<name>` reaches
one person's agents, where <name> is the part of their git email before the @; a board item id (idea-3fa21c) is
the thread about that item, which `board.py show <id>` also prints. read and wait take `all` and `@<you>` when no
channel is given, so name the item id to follow a thread. A comment on a board item also arrives on its author's
`@<name>` channel.

An agent never receives its own messages. An agent is a session plus a git branch: subagents share their parent's
session id, and each works on its own branch.

Stored in the DynamoDB table iterate-board (tools/team.py) as chan#<channel> / <UTC time in ns>#<sender>, so
reading costs one query per channel that returns only recent rows, whatever the total number of messages. Each
agent keeps its position per channel in ~/.cache/iterate-hack/cursors/. Senders' clocks differ, so a message can
be stored with a time slightly before one already read: each read therefore goes back SKEW seconds before its
position and skips the messages it has already shown. The first read of a channel starts 10 minutes back.
"""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import events
import team

LIMIT = 2000
SKEW = 30  # seconds of clock difference between two laptops that a reader tolerates
NS = 10**9


def new_messages(channels, state, me):
    """state is {channel: {"cursor": newest key read, "seen": keys shown within SKEW of the cursor}}."""
    from boto3.dynamodb.conditions import Key

    found = []
    for channel in channels:
        if isinstance(state.get(channel), str):  # position files written before the seen list existed
            state[channel] = {"cursor": state[channel], "seen": []}
        entry = state.setdefault(channel, {"cursor": f"{time.time_ns() - 600 * NS:020d}", "seen": []})
        start = f"{int(entry['cursor'][:20]) - SKEW * NS:020d}"
        query = dict(KeyConditionExpression=Key("pk").eq(f"chan#{channel}") & Key("sk").gt(start), ConsistentRead=True)
        while True:
            page = team.table().query(**query)
            for m in page["Items"]:
                if m["sk"] in entry["seen"]:
                    continue
                entry["seen"].append(m["sk"])
                entry["cursor"] = max(entry["cursor"], m["sk"])
                if not me["session"] or (m["session"], m.get("branch")) != (me["session"], me["branch"]):
                    found.append(m)
            if "LastEvaluatedKey" not in page:
                break
            query["ExclusiveStartKey"] = page["LastEvaluatedKey"]
        oldest_kept = f"{int(entry['cursor'][:20]) - SKEW * NS:020d}"
        entry["seen"] = [sk for sk in entry["seen"] if sk > oldest_kept]
    return sorted(found, key=lambda m: m["sk"])


def show(m):
    return f"[{m['channel']}] {m['at']} {m['who']}/{m.get('branch', '?')} ({m['agent']} {m['session'][:8]}): {m['text']}"


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("send", "read", "wait"):
        sys.exit(__doc__)
    command, *args = sys.argv[1:]
    who = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True, check=True).stdout.strip().split("@")[0]
    me = events.agent()
    agent_file = f"{me['session'] or who}-{me['branch'].replace('/', '_')}"

    if command == "send":
        channel, text = args
        if not re.fullmatch(r"[\w@.-]+", channel):
            sys.exit(f"channel '{channel}' may hold only letters, digits and @ . _ -")
        if len(text) > LIMIT:
            sys.exit(f"message is {len(text)} characters; the limit is {LIMIT}")
        team.table().put_item(Item={"pk": f"chan#{channel}", "sk": f"{time.time_ns():020d}#{who}", "channel": channel, "who": who, **me,
                                    "at": team.now(), "text": text})
        print(f"sent to {channel}")
        sys.exit()

    hook = "--hook" in args
    if hook:
        args.remove("--hook")
        stamp = team.CACHE / "hook" / agent_file
        if stamp.exists() and time.time() - stamp.stat().st_mtime < 20:
            sys.exit()
        stamp.parent.mkdir(parents=True, exist_ok=True)
        stamp.touch()
    timeout = 300.0
    if "--timeout" in args:
        timeout = float(args[args.index("--timeout") + 1])
        del args[args.index("--timeout"):args.index("--timeout") + 2]
    channels = args or ["all", f"@{who}"]
    state_file = team.CACHE / "cursors" / f"{agent_file}.json"
    state = json.loads(state_file.read_text()) if state_file.exists() else {}
    deadline = time.time() + timeout
    while not (messages := new_messages(channels, state, me)) and command == "wait" and time.time() < deadline:
        time.sleep(0.5)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state))
    if hook and messages:
        text = "New messages from the team's agents (tools/msg.py). Act on what applies to your work:\n" + "\n".join(map(show, messages))
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": text}}))
    elif not hook:
        print("\n".join(map(show, messages)), end="\n" if messages else "")
    sys.exit(1 if command == "wait" and not messages else 0)
