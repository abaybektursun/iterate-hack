"""Search the team's past.dev memory: paper findings and everyone's Claude Code sessions.

Usage: python3 tools/recall.py "<question>" [max_tokens]
"""
import sys

from past import IDENTITY, call

query = sys.argv[1]
max_tokens = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
page = call("POST", "recall", {"query": query, "identity": IDENTITY, "maxTokens": max_tokens})

if "pending" in page:
    print(f"[past.dev: {page['pending']['dataPoints']} data points still processing, not in this result]")
for result in page["results"]:
    labels = ", ".join(f"{s.get('label')} [{s['sourceId']}]" for s in result["sources"])
    print(f"{result['occurredAt'][:10]}  {result['content']}  ({labels})")
print(f"[{len(page['results'])} results, {page['usedEvidenceTokens']} tokens]")
