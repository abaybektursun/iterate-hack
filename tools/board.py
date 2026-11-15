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
  uv run tools/board.py score <result id> <base|rl|other> <benchmark> <right>/<n> "<configuration>" [--tokens <per problem>]
                                                  attach one score to a result already posted, for the hill-climbing
                                                  chart of tools/view.py. base = the untrained model, rl = the RL
                                                  checkpoint, other = any other model (weight blends, other
                                                  checkpoints): stored, not drawn
  uv run tools/board.py plain <result id> "<title>" "<what>" "<why>" ["<caveat>"] [--score <benchmark> <right>/<n>]
                                                  describe a result already posted in plain words, for the people who
                                                  read the board page; with --score, describe one score of it. A
                                                  second write with the same result and score replaces the first
  uv run tools/board.py plain --file <path.json>  the same for a JSON list of {"item": "result-xxxxxx", "title", "what",
                                                  "why", "caveat" (optional), "score": {"benchmark", "right", "n"}
                                                  (optional)}; every entry is checked before any row is written

A result's text can carry its scores itself, one per line, and post and done then write them:
  score: base MATH-500 378/500 tokens 4690 | cue, T 0.6 / top-p 1.0

A result's text also says in plain words what the result is, for a reader who has not seen the project. One field
per line; post and done write them as plain rows, and the lines stay in the text:
  title: Break vote ties with the shortest answer
  what: When the 4 sampled answers have no majority, take the shortest answer that finished.
  why: Not known yet.
  caveat: The rule was chosen after reading the problems it fixes; the held-out estimate is 451.
title, at most 60 characters: the change or the finding, without ids or settings. what, at most 240: what was changed
or tested. why, at most 240: why the number moved, only a mechanism that the result states or measures, otherwise
exactly "Not known yet." caveat, optional, at most 240: what weakens the number. A line over its limit stops the post.
Lines before the first score line describe the result as a whole. Lines after a score line, up to the next score
line, describe that one score: use them when one result holds several scores. A result without title, what and why
is accepted, and post prints a reminder to add them with plain.

Each line of ls is: id, person/branch of the agent that posted it, time (UTC, month-day hour:minute), for a work
item the minutes since it was posted or last commented on by its owner (idle), votes up and down and number of comments (only
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
  scores / <result's ns>#<ns>       one score of a result: model, benchmark, right, n, configuration, tokens; ordered
                                    by the time of its result, so the chart's attempts are in the order they were found
  plain / <result id>               the plain-language description of a result: item (the result id), title, what, why,
                                    caveat (each only when given)
  plain / <result id>#<benchmark>#<right>/<n>
                                    the same for one score of the result, benchmark spelled as on its score row

result and knowledge posts are also sent to the team's past.dev memory (tools/past.py), so
`python3 tools/recall.py` finds them next to paper findings and sessions, about a minute after the post.

To claim an idea, post a work item whose text names the idea id. post then prints any other open work item that
names the same id. If one of those is older than yours, close yours with done and pick another.
"""
import json
import re
import secrets
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from boto3.dynamodb.conditions import Key

import events
import msg
import team

KINDS = ("idea", "skill", "knowledge", "result", "work")
REMEMBERED = ("result", "knowledge")
COMMENT_LIMIT = 280
POST_LIMIT = 4000
NAMED = r"\b(?:idea|skill|knowledge|result)-[0-9a-f]{6}\b"
PLAIN = {"title": 60, "what": 240, "why": 240, "caveat": 240}  # the plain-language fields of a result, with their limits in characters


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


SCORE_LINE = re.compile(r"score: (base|rl|other) (\S+) (\d+)/(\d+)(?: tokens (\d+))? \| (.+)")


def score_lines(text):
    """The scores in a result's text: lines 'score: <base|rl|other> <benchmark> <right>/<n> [tokens <per problem>] | <configuration>'."""
    found = []
    for line in text.splitlines():
        if line.strip().startswith("score:"):
            m = SCORE_LINE.fullmatch(line.strip())
            assert m, f"score line not understood: {line.strip()!r}; write e.g. 'score: base MATH-500 378/500 tokens 4690 | cue, T 0.6'"
            model, benchmark, right, n, tokens, config = m.groups()
            assert int(right) <= int(n), f"{right}/{n}: right must be at most n"
            found.append((model, benchmark, int(right), int(n), config.strip(), int(tokens) if tokens else None))
    return found


def same(benchmark):
    """hard-328, Hard 328 and hard328 are one benchmark."""
    return re.sub(r"[^a-z0-9]", "", benchmark.lower())


def add_score(result_id, result_ns, result_at, model, benchmark, right, n, config, tokens, who, me):
    known = {same(s["benchmark"]): s["benchmark"] for s in rows(KeyConditionExpression=Key("pk").eq("scores"))}
    benchmark = known.get(same(benchmark), benchmark)  # keep the spelling already on the chart
    team.table().put_item(Item={"pk": "scores", "sk": f"{int(result_ns):020d}#{time.time_ns()}", "result": result_id, "model": model,
                                "benchmark": benchmark, "right": right, "n": n, "config": config, "tokens": tokens, "who": who, **me,
                                "at": team.now(), "result_at": result_at})
    print(f"score {model} {benchmark} {right}/{n} ({100 * right / n:.1f} %) on {result_id}")
    return benchmark


def check_plain(fields, where):
    """Stops on an empty field or a field over its limit. fields: {title, what, why, caveat: text}, any of them."""
    for field, value in fields.items():
        assert isinstance(value, str) and value.strip(), f"{where}: {field} is empty; write its text or leave the field out"
        if len(value) > PLAIN[field]:
            sys.exit(f"{where}: {field} is {len(value)} characters; the limit is {PLAIN[field]}. Shorten it: {value!r}")


def plain_lines(text):
    """The plain-language lines in a result's text, 'title: ...', 'what: ...', 'why: ...', 'caveat: ...', as {place: {field: text}}.
    place is None for the lines before the first score line (the result as a whole), and i for the lines between score line i
    (counted from 0) and the next score line (that one score)."""
    found, place = {}, None
    for line in text.splitlines():
        field, colon, value = line.strip().partition(":")
        if colon and field == "score":
            place = 0 if place is None else place + 1
        elif colon and field in PLAIN:
            where = "before the first score line" if place is None else f"after score line {place + 1}"
            assert field not in found.setdefault(place, {}), f"two {field}: lines {where}; keep one"
            found[place][field] = value.strip()
            check_plain({field: value.strip()}, where)
    return found


def add_plain(result_id, score, fields, who, me):
    """score: None for the result as a whole, or (benchmark as on its score row, right, n) for one score of it."""
    sk = result_id if score is None else f"{result_id}#{score[0]}#{score[1]}/{score[2]}"
    team.table().put_item(Item={"pk": "plain", "sk": sk, "item": result_id, **fields, "who": who, **me, "at": team.now()})
    print(f"plain {sk}: {fields.get('title', '(no title)')}")


def plain_entry(entry, scores):
    """Checks one entry of the plain command, {item, title, what, why, caveat (optional), score: {benchmark, right, n} (optional)},
    against the score rows of the board, and returns the arguments of add_plain: (result id, score, fields). Writes nothing."""
    assert isinstance(entry, dict) and "item" in entry and not set(entry) - {"item", "score", *PLAIN}, (
        f"entry not understood: {entry!r}; its keys are item, title, what, why, and optionally caveat and score")
    item_id, fields = entry["item"], {field: entry[field] for field in PLAIN if field in entry}
    missing = [field for field in ("title", "what", "why") if field not in fields]
    assert not missing, f"{item_id}: no {', '.join(missing)}; title, what and why are required (why can be exactly 'Not known yet.')"
    check_plain(fields, item_id)
    result = get(item_id)
    assert result["kind"] == "result", f"{item_id} is a {result['kind']}; plain describes a result"
    if "score" not in entry:
        return item_id, None, fields
    want = entry["score"]
    understood = isinstance(want, dict) and set(want) == {"benchmark", "right", "n"} and isinstance(want["right"], int) and isinstance(want["n"], int)
    assert understood, f"{item_id}: score not understood: {want!r}; write e.g. {{'benchmark': 'MATH-500', 'right': 453, 'n': 500}}"
    own = [s for s in scores if s["result"] == item_id]
    wanted = (same(want["benchmark"]), want["right"], want["n"])
    row = next((s for s in own if (same(s["benchmark"]), s["right"], s["n"]) == wanted), None)
    assert row, (f"{item_id} has no score {want['benchmark']} {want['right']}/{want['n']}; its scores are: "
                 + (", ".join(f"{s['benchmark']} {s['right']}/{s['n']}" for s in own) or "none"))
    return item_id, (row["benchmark"], want["right"], want["n"]), fields


def post(kind, text, who, me):
    assert kind in KINDS, f"kind must be one of {KINDS}"
    if len(text) > POST_LIMIT:
        sys.exit(f"text is {len(text)} characters; the limit is {POST_LIMIT}. Put long material in a file and name its path.")
    scores = score_lines(text) if kind == "result" else []  # read first: a bad score line stops the post
    plain = plain_lines(text) if kind == "result" else {}  # the same for a title, what, why or caveat line
    keys = [(same(scores[i][1]), *scores[i][2:4]) for i in plain if i is not None]
    assert len(keys) == len(set(keys)), "two scores with the same benchmark and right/n share one plain row; describe one of them"
    item_id = f"{kind}-{secrets.token_hex(3)}"
    ns = time.time_ns()
    at = team.now()
    team.table().put_item(Item={"pk": f"item#{item_id}", "sk": "item", "id": item_id, "kind": kind, "text": text, "who": who, **me,
                                "at": at, "at_ns": ns, "active_ns": ns, "listed": kind, "ups": 0, "downs": 0, "score": 0, "n_comments": 0})
    print(item_id)
    spelled = [add_score(item_id, ns, at, *score, who, me) for score in scores]  # each benchmark as its score row spells it
    for place, fields in plain.items():
        add_plain(item_id, None if place is None else (spelled[place], *scores[place][2:4]), fields, who, me)
    if kind == "result" and not any({"title", "what", "why"} <= set(fields) for fields in plain.values()):
        print("no title:, what: and why: lines, so the board page cannot say in plain words what this result is. "
              f'Add them: uv run tools/board.py plain {item_id} "<title>" "<what>" "<why>"')
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
                              "UpdateExpression": "ADD n_comments :one", "ExpressionAttributeValues": {":one": 1}}}]
        if (item["who"], item.get("branch")) == (who, me["branch"]):  # only the owner's comment ends the idle time: a question from another agent leaves the item idle
            writes[1]["Update"]["UpdateExpression"] += " SET active_ns = :ns"
            writes[1]["Update"]["ExpressionAttributeValues"][":ns"] = ns
        if (item["who"], item.get("session"), item.get("branch")) != (who, me["session"], me["branch"]):  # tell the item's author: it arrives with their next msg.py read
            writes.append({"Put": {"TableName": table.name, "Item": {
                "pk": f"chan#@{item['who']}", "sk": f"{ns:020d}#{who}", "channel": f"@{item['who']}", "who": who, **me, "at": now,
                "text": f"comment on your {item_id}: {text}"}}})
        client.transact_write_items(TransactItems=writes)
        print(f"commented on {item_id}")

    elif command == "score":
        tokens = int(args.pop(args.index("--tokens") + 1)) if "--tokens" in args else None
        args = [a for a in args if a != "--tokens"]
        result_id, model, benchmark, fraction, config = args
        result = get(result_id)
        assert result["kind"] == "result", f"{result_id} is a {result['kind']}, not a result"
        assert model in ("base", "rl", "other"), "model is base (the untrained Olmo 3 base), rl (Olmo-3.1-7B-RL-Zero-Math) or other (any other model: weight blends, other checkpoints; stored, not drawn)"
        right, n = map(int, fraction.split("/"))
        assert 0 <= right <= n, f"{fraction}: right must be between 0 and n"
        add_score(result_id, result["at_ns"], result["at"], model, benchmark, right, n, config, tokens, who, me)

    elif command == "plain":
        if args[:1] == ["--file"]:
            _, path = args
            entries = json.loads(Path(path).read_text())
            assert isinstance(entries, list), f"{path} must hold a JSON list of entries"
        else:
            score = {}
            if "--score" in args:
                at = args.index("--score")
                _, benchmark, fraction = args[at:at + 3]
                del args[at:at + 3]
                right, n = map(int, fraction.split("/"))
                score = {"score": {"benchmark": benchmark, "right": right, "n": n}}
            item_id, title, what, why, *caveat = args
            assert len(caveat) <= 1, f"{len(args)} texts after plain; write <result id> \"<title>\" \"<what>\" \"<why>\" [\"<caveat>\"]"
            entries = [{"item": item_id, "title": title, "what": what, "why": why, **({"caveat": caveat[0]} if caveat else {}), **score}]
        scores = rows(KeyConditionExpression=Key("pk").eq("scores"))
        checked = [plain_entry(entry, scores) for entry in entries]  # every entry first: a bad one stops the command before any write
        keys = [(item_id, score) for item_id, score, _ in checked]
        assert len(keys) == len(set(keys)), f"{next(k for k in keys if keys.count(k) > 1)} is described twice; keep one entry"
        for entry in checked:
            add_plain(*entry, who, me)

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
            if not team.review_loop(who):
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
