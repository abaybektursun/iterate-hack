# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35"]
# ///
"""The team board: ideas, skills, knowledge, results and current work, with votes and comments.

  uv run tools/board.py post <kind> "<text>"     kind: idea, skill, knowledge, result, work; at most 4000 characters.
                                                  post work also announces the item on the channel all
  uv run tools/board.py ls [kind ...] [--new] [--n 50] [--full]
                                                  the 50 open items with the highest score (--new: the 50 newest);
                                                  --full prints whole texts instead of 100 characters
  uv run tools/board.py show <id>                 full text, voters, comments, and the messages on the item's channel
  uv run tools/board.py up <id>                   one vote per person; voting again replaces it
  uv run tools/board.py down <id>
  uv run tools/board.py comment <id> "<text>"     at most 280 characters; the item's author gets it as a message
  uv run tools/board.py done <id> ["<result>"]    close a work item and announce it on all; with a text, also post
                                                  it as a result item, in the same command

Each line of ls is: id, person/branch of the agent that posted it, time (UTC, month-day hour:minute), for a work
item the minutes since it was posted or last commented on (idle), votes up and down and number of comments (only
when there are any), then the text.

Stored in the DynamoDB table iterate-board (tools/team.py). Every command reads and writes a fixed number of
rows, so its time does not grow with the board: ls asks an index for the top or newest n items of each kind, and
an item carries its own vote and comment counts. A vote or a comment changes its own row and the item's count in
one transaction. Rows:
  item#<id> / item                  the item, with ups, downs, score, n_comments; `listed` = its kind while open,
                                    work-closed once done (ls never asks for it; tools/cycle.py does)
  item#<id> / vote#<who>            one person's vote
  item#<id> / comment#<ns>#<who>    one comment
  claim#<named id> / <work id>      a work item that names another item

result and knowledge posts are also sent to the team's past.dev memory (tools/past.py), so
`python3 tools/recall.py` finds them next to paper findings and sessions, about a minute after the post.

To claim an idea, post a work item whose text names the idea id. post then prints any other open work item that
names the same id. If one of those is older than yours, close yours with done and pick another.
"""
import re
import secrets
import sys
import time
from concurrent.futures import ThreadPoolExecutor

from boto3.dynamodb.conditions import Key

import events
import msg
import team

KINDS = ("idea", "skill", "knowledge", "result", "work")
REMEMBERED = ("result", "knowledge")
COMMENT_LIMIT = 280
POST_LIMIT = 4000
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


def author(row):
    """person/branch, e.g. samer.aslan/probe-l12. Rows written before the branch was recorded show the person."""
    return f"{row['who']}/{row['branch']}" if row.get("branch") else row["who"]


def line(item, full):
    """id, person/branch, UTC month-day hour:minute, idle minutes (work), votes and comments (only when there are any), text."""
    text = item["text"] if full else item["text"].splitlines()[0][:100]
    idle = ""
    if item["kind"] == "work":  # minutes since the item was posted or last commented on
        idle = f" idle {(time.time_ns() - int(item.get('active_ns', item['at_ns']))) // (60 * 10**9)}m"
    votes = f" +{item['ups']}-{item['downs']}" if item["ups"] or item["downs"] else ""
    comments = f" {item['n_comments']}c" if item["n_comments"] else ""
    return f"{item['id']} {author(item)} {item['at'][5:16].replace('T', ' ')}{idle}{votes}{comments}: {text}"


def post(kind, text, who, me):
    assert kind in KINDS, f"kind must be one of {KINDS}"
    if len(text) > POST_LIMIT:
        sys.exit(f"text is {len(text)} characters; the limit is {POST_LIMIT}. Put long material in a file and name its path.")
    item_id = f"{kind}-{secrets.token_hex(3)}"
    ns = time.time_ns()
    team.table().put_item(Item={"pk": f"item#{item_id}", "sk": "item", "id": item_id, "kind": kind, "text": text, "who": who, **me,
                                "at": team.now(), "at_ns": ns, "active_ns": ns, "listed": kind, "ups": 0, "downs": 0, "score": 0, "n_comments": 0})
    print(item_id)
    if kind in REMEMBERED and not team.TEST:  # past.dev has no test project
        remember(item_id, kind, text, who)
    return item_id


def remember(item_id, kind, text, who):
    from past import call

    receipt = call("POST", "ingest", {
        "id": f"board:{item_id}",
        "label": f"board {item_id}",
        "content": f"Board {kind} {item_id}, posted by {who}:\n{text}",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "metadata": {"board": item_id, "kind": kind, "who": who},
    })
    print(f"past.dev: {receipt['status']}")


def main(argv, who):
    command, *args = argv or ["help"]
    table = team.table()
    client = table.meta.client  # for transactions: several rows change together or not at all
    now = team.now()
    me = events.agent()  # agent type, session id, branch: stored on every item, vote and comment

    if command == "post":
        kind, text = args
        item_id = post(kind, text, who, me)
        if kind == "work":
            for named in sorted(set(re.findall(NAMED, text))):
                table.put_item(Item={"pk": f"claim#{named}", "sk": item_id, "who": who, **me, "at": now, "text": text[:100], "is_open": True})
                for other in rows(KeyConditionExpression=Key("pk").eq(f"claim#{named}"), ConsistentRead=True):
                    if other["is_open"] and other["sk"] != item_id:
                        print(f"also claimed: {other['sk']} by {author(other)} at {other['at']}: {other['text']}")
            msg.send("all", f"started {item_id}: {text.splitlines()[0][:200]}", who, me)
            print("announced on all")

    elif command == "ls":
        full, newest = "--full" in args, "--new" in args
        n = int(args[args.index("--n") + 1]) if "--n" in args else 50
        kinds = [a for a in args if a in KINDS] or KINDS
        index, order = ("new", "at_ns") if newest else ("top", "score")
        with ThreadPoolExecutor(len(kinds)) as pool:  # one query per kind, at the same time
            pages = pool.map(lambda kind: table.query(IndexName=index, KeyConditionExpression=Key("listed").eq(kind),
                                                      ScanIndexForward=False, Limit=n)["Items"], kinds)
            found = [item for page in pages for item in page]
        for item in sorted(found, key=lambda i: -i[order])[:n]:
            print(line(item, full))

    elif command == "show":
        (item_id,) = args
        item = get(item_id)
        rest = rows(KeyConditionExpression=Key("pk").eq(f"item#{item_id}"))
        votes = [r for r in rest if r["sk"].startswith("vote#")]
        state = "open" if item.get("listed") == item["kind"] else f"closed by {item.get('closed_by')} at {item.get('closed_at')}"
        print(f"{item_id} ({item['kind']}, {state}) by {author(item)} ({item.get('agent', 'agent not recorded')} {item.get('session', '')[:8]}) at {item['at']}")
        print(f"+{item['ups']} -{item['downs']}: " + ", ".join(f"{v['who']} {'+' if v['vote'] == 1 else '-'}" for v in votes))
        print(f"\n{item['text']}\n")
        for c in sorted((r for r in rest if r["sk"].startswith("comment#")), key=lambda c: c["sk"]):
            print(f"  {c['at']}  {author(c)}: {c['text']}")
        thread = rows(KeyConditionExpression=Key("pk").eq(f"chan#{item_id}"))  # messages sent with msg.py send <item id>
        if thread:
            print("\nmessages on this item's channel:")
        for m in thread:
            print(f"  {m['at']}  {author(m)}: {m['text']}")

    elif command in ("up", "down"):
        (item_id,) = args
        get(item_id)
        vote = 1 if command == "up" else -1
        key = {"pk": f"item#{item_id}", "sk": f"vote#{who}"}
        for _ in range(5):  # the vote row and the item's counts change in one transaction; retry if this person's vote changed meanwhile
            old = table.get_item(Key=key, ConsistentRead=True).get("Item", {}).get("vote", 0)
            if old == vote:
                break
            unchanged = ({"ConditionExpression": "vote = :old", "ExpressionAttributeValues": {":old": old}} if old
                         else {"ConditionExpression": "attribute_not_exists(pk)"})
            try:
                client.transact_write_items(TransactItems=[
                    {"Put": {"TableName": table.name, "Item": {**key, "who": who, **me, "at": now, "vote": vote}, **unchanged}},
                    {"Update": {"TableName": table.name, "Key": {"pk": f"item#{item_id}", "sk": "item"},
                                "UpdateExpression": "ADD ups :u, downs :d, score :s",
                                "ExpressionAttributeValues": {":u": (vote == 1) - (old == 1), ":d": (vote == -1) - (old == -1), ":s": vote - old}}}])
                break
            except client.exceptions.TransactionCanceledException:
                continue
        else:
            sys.exit(f"vote on {item_id} not recorded: this person's vote kept changing during 5 attempts")
        print(f"voted {command} on {item_id}")

    elif command == "comment":
        item_id, text = args
        item = get(item_id)
        if len(text) > COMMENT_LIMIT:
            sys.exit(f"comment is {len(text)} characters; the limit is {COMMENT_LIMIT}")
        ns = time.time_ns()
        comment = {"pk": f"item#{item_id}", "sk": f"comment#{ns}#{who}", "who": who, **me, "at": now, "text": text}
        writes = [{"Put": {"TableName": table.name, "Item": comment}},
                  {"Update": {"TableName": table.name, "Key": {"pk": f"item#{item_id}", "sk": "item"},
                              "UpdateExpression": "ADD n_comments :one SET active_ns = :ns", "ExpressionAttributeValues": {":one": 1, ":ns": ns}}}]
        if (item["who"], item.get("session"), item.get("branch")) != (who, me["session"], me["branch"]):  # tell the item's author: it arrives with their next msg.py read
            writes.append({"Put": {"TableName": table.name, "Item": {
                "pk": f"chan#@{item['who']}", "sk": f"{ns:020d}#{who}", "channel": f"@{item['who']}", "who": who, **me, "at": now,
                "text": f"comment on your {item_id}: {text}"}}})
        client.transact_write_items(TransactItems=writes)
        print(f"commented on {item_id}")

    elif command == "done":
        item_id, *result = args
        item = get(item_id)
        assert item["kind"] == "work", f"{item_id} is a {item['kind']}, not a work item"
        result_id = post("result", result[0], who, me) if result else None  # first, so a refused result leaves the item open
        writes = [{"Update": {"TableName": table.name, "Key": {"pk": f"item#{item_id}", "sk": "item"},
                              "UpdateExpression": "SET closed_by = :who, closed_at = :at, listed = :closed",
                              "ExpressionAttributeValues": {":who": f"{who}/{me['branch']}", ":at": now, ":closed": "work-closed"}}}]
        for named in set(re.findall(NAMED, item["text"])):
            writes.append({"Update": {"TableName": table.name, "Key": {"pk": f"claim#{named}", "sk": item_id},
                                      "UpdateExpression": "SET is_open = :no", "ExpressionAttributeValues": {":no": False}}})
        client.transact_write_items(TransactItems=writes)
        print(f"closed {item_id}")
        if result_id:
            msg.send("all", f"done {item_id}, {result_id}: {result[0].splitlines()[0][:200]}", who, me)
            print("A result closed: run the team-meta-review skill (uv run tools/cycle.py first).")
        else:
            msg.send("all", f"closed {item_id}: {item['text'].splitlines()[0][:200]}", who, me)
        print("announced on all")

    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    if {"--help", "-h"} & set(sys.argv[: sys.argv.index("--") if "--" in sys.argv else None]):
        sys.exit(__doc__)
    events.log("board", sys.argv[1:], team.who())
    main(sys.argv[1:], team.who())
