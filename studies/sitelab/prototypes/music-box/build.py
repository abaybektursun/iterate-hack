# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35"]
# ///
"""Build data.json for the music-box prototype: every commit, board item, message on `all` and score line.

  uv run studies/sitelab/prototypes/music-box/build.py

Commits come from `git log --all` (time, author's GitHub name, short hash, subject) and are checked against
`git rev-list --all --count`. Board items (open kinds and closed work), the messages on `all`, the score lines and the
plain titles come from the team table of tools/team.py, in the shape of the site's /data so the page reads both alike.
A mismatch with a stored total, an unknown author or an address in a text stops the build.
"""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "tools"))
import board  # noqa: E402
from boto3.dynamodb.conditions import Key  # noqa: E402

git = lambda *a: subprocess.run(["git", "-C", HERE, *a], capture_output=True, text=True, check=True).stdout

WHO = {"Abay Bektursun": "abaybektursun", "Ali Rad": "frustea", "sameraslan": "sameraslan", "Samer Aslan": "sameraslan"}
PRIVATE = re.compile(r"[\w.+-]+@[\w-]+\.[a-z]{2,}|/home/\w|/Users/\w|\bsk-[A-Za-z0-9]{16}|AKIA[A-Z0-9]{12}")


def clean(text, where):
    if PRIVATE.search(text):
        raise SystemExit(f"{where} has an address, a key or a home path: {PRIVATE.search(text).group(0)!r}")
    return text


commits = []
for line in git("log", "--all", "--format=%at%x09%an%x09%h%x09%s").splitlines():
    at, name, sha, subject = line.split("\t", 3)
    if name not in WHO:
        raise SystemExit(f"unknown commit author {name!r}: add it to WHO")
    subject = subject.split(" Co-Authored-By:")[0]  # a trailer folded into the subject carries an address
    commits.append([int(at), WHO[name], sha, clean(subject, f"commit {sha}")[:300]])
commits.sort()
total = int(git("rev-list", "--all", "--count"))
if len(commits) != total:
    raise SystemExit(f"{len(commits)} commits read, git rev-list --all --count says {total}")

LISTS = ("idea", "skill", "knowledge", "result", "work", "work-closed")
with ThreadPoolExecutor(8) as pool:
    lists = list(pool.map(lambda l: board.rows(IndexName="new", KeyConditionExpression=Key("listed").eq(l)), LISTS))
    messages, scores, plain = pool.map(lambda pk: board.rows(KeyConditionExpression=Key("pk").eq(pk)), ("chan#all", "scores", "plain"))

items = [{"id": r["id"], "kind": r["kind"], "who": r["who"], "at_ns": int(r["at_ns"]), "text": clean(r["text"], r["id"])[:700]}
         for l in lists for r in l]
if len({i["id"] for i in items}) != len(items):
    raise SystemExit("an item is in two lists")
msgs = [{"sk": str(r["sk"]), "who": r["who"], "text": clean(r["text"], "message " + str(r["sk"]))[:400]} for r in messages]
scs = [{"sk": str(r["sk"]), "result": r["result"], "model": r["model"], "benchmark": r["benchmark"], "right": int(r["right"]),
        "n": int(r["n"]), "config": r.get("config", ""), "tokens": int(r["tokens"]) if r.get("tokens") is not None else None,
        "who": r.get("who", "")} for r in scores]
titles = {r.get("item", str(r["sk"])): {"title": r["title"]} for r in plain if "score" not in r and r.get("title")}
titles = {k: v for k, v in titles.items() if k in {i["id"] for i in items}}

out = os.path.join(HERE, "data.json")
json.dump({"commits_total": total, "head": git("rev-parse", "--short", "HEAD").strip(), "commits": commits,
           "items": items, "messages": msgs, "scores": scs, "plain": titles},
          open(out, "w"), separators=(",", ":"), ensure_ascii=False)
size = os.path.getsize(out)
if size > 1_000_000:
    raise SystemExit(f"data.json is {size} bytes, over 1 MB")
print(f"{total} commits, {len(items)} items, {len(msgs)} messages, {len(scs)} scores, {size} bytes -> {out}")
