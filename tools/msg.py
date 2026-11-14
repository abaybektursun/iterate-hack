# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35"]
# ///
"""Messages between agents, delivered within about a second.

  uv run tools/msg.py send <channel> "<text>"       at most 2000 characters
  uv run tools/msg.py read [channel ...]            messages that arrived since this agent last read, oldest first
  uv run tools/msg.py wait [channel ...] [--timeout 300]
                                                    block until a message arrives, then print it; exit code 1 at the timeout

A channel is any name. Conventions: `all` reaches everyone; `@<name>` reaches one person's agents, where <name> is
the part of their git email before the @; a board item id (idea-3fa21c) is the thread about that item. read and
wait take `all` and `@<you>` when no channel is given. An agent never receives its own messages.

Stored in the DynamoDB table iterate-board (tools/team.py) as chan#<channel> / <time in ns>#<sender>, so reading
costs one query per channel that returns only the new rows, whatever the total number of messages. Each agent
session keeps its own position per channel in ~/.cache/iterate-hack/cursors/. The first read of a channel starts
10 minutes back.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

from boto3.dynamodb.conditions import Key

import events
import team

LIMIT = 2000


def new_messages(channels, cursors, me):
    found = []
    for channel in channels:
        start = cursors.get(channel, f"{time.time_ns() - 600 * 10**9:020d}")
        query = dict(KeyConditionExpression=Key("pk").eq(f"chan#{channel}") & Key("sk").gt(start))
        while True:
            page = team.table().query(**query)
            found += [m for m in page["Items"] if m["session"] != me["session"] or not me["session"]]
            if page["Items"]:
                cursors[channel] = page["Items"][-1]["sk"]
            if "LastEvaluatedKey" not in page:
                break
            query["ExclusiveStartKey"] = page["LastEvaluatedKey"]
    return sorted(found, key=lambda m: m["sk"])


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("send", "read", "wait"):
        sys.exit(__doc__)
    command, *args = sys.argv[1:]
    who = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True, check=True).stdout.strip().split("@")[0]
    me = events.agent()

    if command == "send":
        channel, text = args
        if len(text) > LIMIT:
            sys.exit(f"message is {len(text)} characters; the limit is {LIMIT}")
        team.table().put_item(Item={"pk": f"chan#{channel}", "sk": f"{time.time_ns():020d}#{who}", "channel": channel, "who": who,
                                    "agent": me["agent"], "session": me["session"], "at": time.strftime("%Y-%m-%d %H:%M:%S"), "text": text})
        sys.exit()

    timeout = 300.0
    if "--timeout" in args:
        timeout = float(args[args.index("--timeout") + 1])
        del args[args.index("--timeout"):args.index("--timeout") + 2]
    channels = args or ["all", f"@{who}"]
    cursor_file = Path.home() / ".cache" / "iterate-hack" / "cursors" / f"{me['session'] or who}.json"
    cursors = json.loads(cursor_file.read_text()) if cursor_file.exists() else {}
    deadline = time.time() + timeout
    while not (messages := new_messages(channels, cursors, me)) and command == "wait" and time.time() < deadline:
        time.sleep(0.5)
    cursor_file.parent.mkdir(parents=True, exist_ok=True)
    cursor_file.write_text(json.dumps(cursors))
    for m in messages:
        print(f"[{m['channel']}] {m['at']} {m['who']} ({m['agent']} {m['session'][:8]}): {m['text']}")
    sys.exit(1 if command == "wait" and not messages else 0)
