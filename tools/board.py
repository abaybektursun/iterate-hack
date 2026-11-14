# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35"]
# ///
"""The team board: ideas, skills, knowledge, results and current work, with votes and comments.

  uv run tools/board.py post <kind> "<text>"     kind: idea, skill, knowledge, result, work
  uv run tools/board.py ls [kind] [--new] [--n 50] [--full]
                                                  the 50 open items with the highest score (--new: the 50 newest);
                                                  --full prints whole texts instead of 100 characters
  uv run tools/board.py show <id>                 full text, voters, comments
  uv run tools/board.py up <id>                   one vote per person; voting again replaces it
  uv run tools/board.py down <id>
  uv run tools/board.py comment <id> "<text>"     at most 280 characters
  uv run tools/board.py done <id>                 close a work item

Stored in the DynamoDB table iterate-board (tools/team.py). Every command reads and writes a fixed number of
rows, so its time does not grow with the board: ls asks an index for the top or newest n items of each kind, and
an item carries its own vote and comment counts. Rows:
  item#<id> / item                  the item, with ups, downs, score, n_comments; `listed` = its kind while open
  item#<id> / vote#<who>            one person's vote
  item#<id> / comment#<ns>#<who>    one comment
  claim#<named id> / <work id>      a work item that names another item

To claim an idea, post a work item whose text names the idea id. post then prints any other open work item that
names the same id. If one of those is older than yours, close yours with done and pick another.
"""
import re
import secrets
import subprocess
import sys
import time

from boto3.dynamodb.conditions import Key

import events
import team

KINDS = ("idea", "skill", "knowledge", "result", "work")
COMMENT_LIMIT = 280
NAMED = r"\b(?:idea|skill|knowledge|result)-[0-9a-f]{6}\b"


def rows(**query):
    """Every row of a query, following pages."""
    found = []
    while True:
        page = team.table().query(**query)
        found += page["Items"]
        if "LastEvaluatedKey" not in page:
            return found
        query["ExclusiveStartKey"] = page["LastEvaluatedKey"]


def get(item_id):
    item = team.table().get_item(Key={"pk": f"item#{item_id}", "sk": "item"}).get("Item")
    if not item:
        sys.exit(f"no item {item_id}")
    return item


def line(item, full):
    text = item["text"] if full else item["text"].splitlines()[0][:100]
    return f"{item['id']}  +{item['ups']} -{item['downs']}  {item['n_comments']}c  {item['who']}  {item['at']}  {text}"


def main(argv, who):
    command, *args = argv or ["help"]
    table = team.table()
    now = time.strftime("%Y-%m-%d %H:%M:%S")

    if command == "post":
        kind, text = args
        assert kind in KINDS, f"kind must be one of {KINDS}"
        item_id = f"{kind}-{secrets.token_hex(3)}"
        table.put_item(Item={"pk": f"item#{item_id}", "sk": "item", "id": item_id, "kind": kind, "text": text, "who": who,
                             "at": now, "at_ns": time.time_ns(), "listed": kind, "ups": 0, "downs": 0, "score": 0, "n_comments": 0})
        print(item_id)
        if kind == "work":
            for named in sorted(set(re.findall(NAMED, text))):
                table.put_item(Item={"pk": f"claim#{named}", "sk": item_id, "who": who, "at": now, "text": text[:100], "is_open": True})
                for other in rows(KeyConditionExpression=Key("pk").eq(f"claim#{named}")):
                    if other["is_open"] and other["sk"] != item_id:
                        print(f"also claimed: {other['sk']} by {other['who']} at {other['at']}: {other['text']}")

    elif command == "ls":
        full, newest = "--full" in args, "--new" in args
        n = int(args[args.index("--n") + 1]) if "--n" in args else 50
        kinds = [a for a in args if a in KINDS] or KINDS
        index, order = ("new", "at_ns") if newest else ("top", "score")
        found = []
        for kind in kinds:
            found += table.query(IndexName=index, KeyConditionExpression=Key("listed").eq(kind), ScanIndexForward=False, Limit=n)["Items"]
        for item in sorted(found, key=lambda i: -i[order])[:n]:
            print(line(item, full))

    elif command == "show":
        (item_id,) = args
        item = get(item_id)
        rest = rows(KeyConditionExpression=Key("pk").eq(f"item#{item_id}"))
        votes = [r for r in rest if r["sk"].startswith("vote#")]
        print(f"{item_id} ({item['kind']}, {'open' if 'listed' in item else 'closed'}) by {item['who']} at {item['at']}")
        print(f"+{item['ups']} -{item['downs']}: " + ", ".join(f"{v['who']} {'+' if v['vote'] == 1 else '-'}" for v in votes))
        print(f"\n{item['text']}\n")
        for c in sorted((r for r in rest if r["sk"].startswith("comment#")), key=lambda c: c["sk"]):
            print(f"  {c['at']}  {c['who']}: {c['text']}")

    elif command in ("up", "down"):
        (item_id,) = args
        get(item_id)
        vote = 1 if command == "up" else -1
        old = table.put_item(Item={"pk": f"item#{item_id}", "sk": f"vote#{who}", "who": who, "vote": vote},
                             ReturnValues="ALL_OLD").get("Attributes", {}).get("vote", 0)
        table.update_item(Key={"pk": f"item#{item_id}", "sk": "item"}, UpdateExpression="ADD ups :u, downs :d, score :s",
                          ExpressionAttributeValues={":u": (vote == 1) - (old == 1), ":d": (vote == -1) - (old == -1), ":s": vote - old})

    elif command == "comment":
        item_id, text = args
        get(item_id)
        if len(text) > COMMENT_LIMIT:
            sys.exit(f"comment is {len(text)} characters; the limit is {COMMENT_LIMIT}")
        table.put_item(Item={"pk": f"item#{item_id}", "sk": f"comment#{time.time_ns()}#{who}", "who": who, "at": now, "text": text})
        table.update_item(Key={"pk": f"item#{item_id}", "sk": "item"}, UpdateExpression="ADD n_comments :one",
                          ExpressionAttributeValues={":one": 1})

    elif command == "done":
        (item_id,) = args
        item = get(item_id)
        assert item["kind"] == "work", f"{item_id} is a {item['kind']}, not a work item"
        table.update_item(Key={"pk": f"item#{item_id}", "sk": "item"}, UpdateExpression="SET closed_by = :who, closed_at = :at REMOVE listed",
                          ExpressionAttributeValues={":who": who, ":at": now})
        for named in set(re.findall(NAMED, item["text"])):
            table.update_item(Key={"pk": f"claim#{named}", "sk": item_id}, UpdateExpression="SET is_open = :no",
                              ExpressionAttributeValues={":no": False})

    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    email = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True, check=True).stdout.strip()
    if {"--help", "-h"} & set(sys.argv[: sys.argv.index("--") if "--" in sys.argv else None]):
        sys.exit(__doc__)
    events.log("board", sys.argv[1:], email.split("@")[0])
    main(sys.argv[1:], email.split("@")[0])
