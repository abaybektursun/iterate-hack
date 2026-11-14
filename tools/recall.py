"""Search the team's shared past.dev memory.

Usage: python3 tools/recall.py "what did we decide about the eval set?" [max_tokens]

Reads the key and identity from ~/.past/config.json (the same file the past.dev plugin uses);
PAST_API_KEY and PAST_IDENTITY in the environment override it. API: POST /api/v1/recall,
https://past.dev/docs/memory-api/api-reference
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

config_path = Path.home() / ".past" / "config.json"
config = json.loads(config_path.read_text()) if config_path.exists() else {}
key = os.environ.get("PAST_API_KEY") or config["apiKey"]
identity = os.environ.get("PAST_IDENTITY") or config["identity"]

query = sys.argv[1]
max_tokens = int(sys.argv[2]) if len(sys.argv) > 2 else 2000

request = urllib.request.Request(
    "https://api.past.dev/api/v1/recall",
    data=json.dumps({"query": query, "identity": identity, "maxTokens": max_tokens}).encode(),
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
)
page = json.load(urllib.request.urlopen(request))

if "pending" in page:
    print(f"[past.dev: {page['pending']['dataPoints']} data points still processing, not in this result]")
for result in page["results"]:
    labels = ", ".join(f"{s.get('label')} [{s['sourceId']}]" for s in result["sources"])
    print(f"{result['occurredAt'][:10]}  {result['content']}  ({labels})")
print(f"[{len(page['results'])} results, {page['usedEvidenceTokens']} tokens]")
