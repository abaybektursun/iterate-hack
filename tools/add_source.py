"""Add one piece of prior work (paper, blog post, published result) to the team's past.dev memory.

Usage:
  python3 tools/add_source.py --id arxiv:2401.12345 --title "Paper title" --date 2024-01-22 \
      --url https://arxiv.org/abs/2401.12345 --kind paper fulltext.txt

The text file holds the raw, complete text (extracted from HTML or PDF), not a summary: past.dev
extracts the claims itself. Texts over 32,000 characters are split at paragraph boundaries into parts
with ids <id>.1, <id>.2, ... Sending the same --id again replaces the earlier version.
Waits until past.dev has processed the send, since a recall before that finds nothing.

Key from ~/.past/config.json or PAST_API_KEY. API: https://past.dev/docs/memory-api/sending-data
"""
import argparse
import hashlib
import json
import os
import time
import urllib.request
from pathlib import Path

PART_CHARS = 32000

parser = argparse.ArgumentParser()
parser.add_argument("--id", required=True, help="stable id without '/', e.g. arxiv:2401.12345")
parser.add_argument("--title", required=True)
parser.add_argument("--date", required=True, help="publication date, YYYY-MM-DD")
parser.add_argument("--url", required=True)
parser.add_argument("--kind", required=True, choices=["paper", "blog", "result"])
parser.add_argument("text_file")
args = parser.parse_args()
assert "/" not in args.id, "past.dev refuses ids containing '/'; use ':'"

config_path = Path.home() / ".past" / "config.json"
config = json.loads(config_path.read_text()) if config_path.exists() else {}
key = os.environ.get("PAST_API_KEY") or config["apiKey"]


def call(method, path, body=None):
    request = urllib.request.Request(
        f"https://api.past.dev/api/v1/{path}",
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    return json.load(urllib.request.urlopen(request))


# Split at paragraph boundaries so each part, with its header line, stays under PART_CHARS.
header = f"{args.title} ({args.kind}, {args.date}, {args.url})"
limit = PART_CHARS - len(header) - 2
parts, current = [], ""
for paragraph in Path(args.text_file).read_text().split("\n\n"):
    if current and len(current) + len(paragraph) + 2 > limit:
        parts.append(current)
        current = ""
    current = f"{current}\n\n{paragraph}" if current else paragraph
parts.append(current)
assert all(len(p) <= limit for p in parts), "a single paragraph is over the part size limit"

items = []
for n, text in enumerate(parts, 1):
    single = len(parts) == 1
    items.append({
        "id": args.id if single else f"{args.id}.{n}",
        "label": args.title if single else f"{args.title}, part {n}",
        "content": f"{header}\n\n{text}",
        "timestamp": f"{args.date}T00:00:00Z",
        "metadata": {"kind": args.kind, "url": args.url},
    })

digest = hashlib.sha256(json.dumps(items).encode()).hexdigest()[:16]
receipt = call("POST", "ingest/batch", {"idempotencyKey": f"{args.id}-{digest}", "items": items})
print(f"sent {len(items)} part(s), ingestionId {receipt['ingestionId']}, status {receipt['status']}")

while receipt["status"] != "completed":
    time.sleep(5)
    receipt = call("GET", f"ingest/{receipt['ingestionId']}")
    assert receipt["status"] != "failed", receipt["failure"]
print("completed: searchable with tools/recall.py")
