"""Spawn and finish times (UTC) of the subagents of one Claude Code session, from its transcript.

    python3 meta/reviews/abaybektursun/20261115-1655-paper2/stages.py ~/.claude/projects/-home-abay-Projects-iterate-hack/a55ee22f-3b35-48b7-a76f-994f9dbac2a8.jsonl > before.txt
"""
import json
import re
import sys

seen = set()
for line in open(sys.argv[1]):
    d = json.loads(line)
    c = d.get("message", {}).get("content")
    ts = d.get("timestamp", "")[11:19]
    if isinstance(c, list):
        for b in c:
            if b.get("type") == "tool_use" and b.get("name") == "Agent" and b["id"] not in seen:
                seen.add(b["id"])
                print(ts, "spawn ", b["input"].get("description"))
    if d.get("type") == "user" and isinstance(c, str) and "task-notification" in c:
        s = re.search(r"<summary>(.*?)</summary>", c, re.S)
        print(ts, "notice", s.group(1) if s else "")
