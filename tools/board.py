# /// script
# requires-python = ">=3.11"
# dependencies = ["modal>=1.4"]
# ///
"""The team board: ideas, skills, knowledge, results and current work, with votes and comments.

  uv run tools/board.py post <kind> "<text>"     kind: idea, skill, knowledge, result, work
  uv run tools/board.py ls [kind]                 highest score first; closed work is hidden
  uv run tools/board.py show <id>                 full text, voters, comments
  uv run tools/board.py up <id>                   one vote per person; voting again replaces it
  uv run tools/board.py down <id>
  uv run tools/board.py comment <id> "<text>"     at most 280 characters
  uv run tools/board.py done <id>                 close a work item

Stored in the Modal Dict "iterate-board". Each item, each person's vote on an item and each comment
has its own key, so two people writing at the same time never overwrite each other. Modal deletes an
entry after 7 days with no reads or writes.
"""
import secrets
import subprocess
import sys
import time

KINDS = ("idea", "skill", "knowledge", "result", "work")
COMMENT_LIMIT = 280


def snapshot(board):
    items, votes, comments = {}, {}, {}
    for key, value in board.items():
        kind, item_id = key.split(":")[:2]
        if kind == "item":
            items[item_id] = value
        elif kind == "vote":
            votes.setdefault(item_id, []).append(value)
        elif kind == "comment":
            comments.setdefault(item_id, []).append(value)
    return items, votes, comments


def tally(item_votes):
    ups = sum(1 for v in item_votes if v["vote"] == 1)
    return ups, len(item_votes) - ups


def main(argv, board, who):
    command, *args = argv or ["help"]
    now = time.strftime("%Y-%m-%d %H:%M")

    if command == "post":
        kind, text = args
        assert kind in KINDS, f"kind must be one of {KINDS}"
        item_id = f"{kind}-{secrets.token_hex(3)}"
        board[f"item:{item_id}"] = {"id": item_id, "kind": kind, "text": text, "who": who, "at": now, "open": True}
        print(item_id)

    elif command == "ls":
        items, votes, comments = snapshot(board)
        shown = [i for i in items.values() if (not args or i["kind"] == args[0]) and i["open"]]
        for item in sorted(shown, key=lambda i: -(lambda u, d: u - d)(*tally(votes.get(i["id"], [])))):
            ups, downs = tally(votes.get(item["id"], []))
            line = item["text"].splitlines()[0][:100]
            print(f"{item['id']}  +{ups} -{downs}  {len(comments.get(item['id'], []))}c  {item['who']}  {item['at']}  {line}")

    elif command == "show":
        (item_id,) = args
        item = board[f"item:{item_id}"]
        items, votes, comments = snapshot(board)
        ups, downs = tally(votes.get(item_id, []))
        print(f"{item_id} ({item['kind']}, {'open' if item['open'] else 'closed'}) by {item['who']} at {item['at']}")
        print(f"+{ups} -{downs}: " + ", ".join(f"{v['who']} {'+' if v['vote'] == 1 else '-'}" for v in votes.get(item_id, [])))
        print(f"\n{item['text']}\n")
        for c in sorted(comments.get(item_id, []), key=lambda c: c["at"]):
            print(f"  {c['at']}  {c['who']}: {c['text']}")

    elif command in ("up", "down"):
        (item_id,) = args
        board[f"item:{item_id}"]  # fails on an unknown id
        board[f"vote:{item_id}:{who}"] = {"who": who, "vote": 1 if command == "up" else -1}

    elif command == "comment":
        item_id, text = args
        board[f"item:{item_id}"]
        if len(text) > COMMENT_LIMIT:
            sys.exit(f"comment is {len(text)} characters; the limit is {COMMENT_LIMIT}")
        board[f"comment:{item_id}:{time.time_ns()}:{who}"] = {"who": who, "at": now, "text": text}

    elif command == "done":
        (item_id,) = args
        item = board[f"item:{item_id}"]
        assert item["kind"] == "work", f"{item_id} is a {item['kind']}, not a work item"
        board[f"item:{item_id}"] = {**item, "open": False}

    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    import modal

    email = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True, check=True).stdout.strip()
    main(sys.argv[1:], modal.Dict.from_name("iterate-board", create_if_missing=True), email.split("@")[0])
