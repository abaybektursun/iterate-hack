# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35"]
# ///
"""Swarm map, step 1 (laptop, read-only): every board item, open or closed, with its comments, from the team table.

    uv run studies/basins/prep/swarm_export.py runs/swarm/board-<UTC time>.json

Queries of the DynamoDB table `iterate-board` (tools/team.py): index `new` for every `listed` value (open
kinds and work-closed), then each item's comment rows. It writes nothing to the table. The snapshot stays in runs/ (not committed): it holds teammates' text.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "tools"))
import team  # noqa: E402

out = pathlib.Path(sys.argv[1])
out.parent.mkdir(parents=True, exist_ok=True)
from boto3.dynamodb.conditions import Key  # noqa: E402

LISTED = ("idea", "skill", "knowledge", "result", "work", "work-closed")  # `listed` of every item (tools/board.py)


def query(**q):
    found = []
    while True:
        page = team.table().query(**q)
        found += page["Items"]
        if "LastEvaluatedKey" not in page:
            return found
        q["ExclusiveStartKey"] = page["LastEvaluatedKey"]


def plain(r):
    return {k: (int(v) if type(v).__name__ == "Decimal" else v) for k, v in r.items()}


items = {}
for listed in LISTED:  # index "new" (listed, at_ns): the same index tools/cycle.py reads
    for r in query(IndexName="new", KeyConditionExpression=Key("listed").eq(listed)):
        items[r["id"]] = plain(r)
n_comments = 0
for iid, it in items.items():
    if it.get("n_comments"):
        cs = query(KeyConditionExpression=Key("pk").eq(f"item#{iid}") & Key("sk").begins_with("comment#"))
        it["comments"] = [{"at": c.get("at"), "who": c.get("who"), "text": c.get("text")} for c in map(plain, cs)]
        n_comments += len(cs)
rows = list(items.values())
out.write_text(json.dumps(sorted(items.values(), key=lambda r: int(r["at_ns"])), indent=1, default=str))
from collections import Counter  # noqa: E402
print(f"{len(items)} items {dict(Counter(r['kind'] for r in rows))}, {n_comments} comments -> {out}")
