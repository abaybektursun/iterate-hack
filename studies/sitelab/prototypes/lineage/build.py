# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35"]
# ///
"""Builds data.json for the lineage prototype: every board item and every real reference between items.

  uv run studies/sitelab/prototypes/lineage/build.py

Nodes: every item of the DynamoDB table iterate-board (open and closed), the finding pages (tools/finding_*.py) and
the theory rounds (studies/theory/results/engine/round-*).
Edges (kind "ref"): item A names item B's id in its text or in a comment on it; a finding page's source names an
item; a theory round's targets.jsonl or run.json names an item. The edge runs from the older of the two to the newer.
Edges (kind "session"): consecutive items posted by the same agent session.
Nothing is estimated: an id that is named but is not in the table gets no node.
"""
import json, re, subprocess, sys, time, calendar
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "tools"))
import team  # noqa: E402

ID = re.compile(r"\b(?:work|result|idea|knowledge|skill)-[0-9a-f]{6}\b")


def git(*a):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True, check=True).stdout


def ns(iso):
    return calendar.timegm(time.strptime(iso[:19], "%Y-%m-%dT%H:%M:%S")) * 10**9


from boto3.dynamodb.conditions import Key  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402


def query(**q):
    found = []
    while True:
        page = team.table().query(**q)
        found += page["Items"]
        if "LastEvaluatedKey" not in page:
            return found
        q["ExclusiveStartKey"] = page["LastEvaluatedKey"]


# the key may query but not scan: items by the index board.py ls uses (open kinds and closed work), then each item's rows
team.table()
with ThreadPoolExecutor(16) as pool:
    listed = [i for part in pool.map(lambda k: query(IndexName="new", KeyConditionExpression=Key("listed").eq(k)),
                                     ("idea", "skill", "knowledge", "result", "work", "work-closed")) for i in part]
    rows = [r for part in pool.map(lambda i: query(KeyConditionExpression=Key("pk").eq(f"item#{i['id']}")), listed) for r in part]
rows += query(KeyConditionExpression=Key("pk").eq("scores")) + query(KeyConditionExpression=Key("pk").eq("plain"))

nodes, comments, scores, plain = {}, {}, {}, {}
for r in rows:
    pk, sk = str(r["pk"]), str(r["sk"])
    if pk.startswith("item#") and sk == "item":
        nodes[r["id"]] = {"id": r["id"], "kind": r["kind"], "who": r["who"], "branch": r.get("branch", ""),
                          "text": r["text"], "at": int(r["at_ns"]) // 10**6, "open": r.get("listed") == "work",
                          "ups": int(r.get("ups", 0)), "downs": int(r.get("downs", 0)),
                          "agent": r.get("agent", ""), "session": r.get("session", ""), "closed": r.get("closed_at", "")}
    elif pk.startswith("item#") and sk.startswith("comment#"):
        comments.setdefault(pk[5:], []).append({"who": r["who"], "at": r["at"], "text": r["text"]})
    elif pk == "scores":
        scores.setdefault(r["result"], []).append({"model": r["model"], "benchmark": r["benchmark"], "right": int(r["right"]),
                                                   "n": int(r["n"]), "config": r.get("config", ""),
                                                   "tokens": int(r["tokens"]) if r.get("tokens") is not None else None})
    elif pk == "plain" and "score" not in r and r.get("title"):
        plain[r.get("item", sk)] = {k: r[k] for k in ("title", "what", "why", "caveat") if r.get(k)}

for i, n in nodes.items():
    n["comments"] = sorted(comments.get(i, []), key=lambda c: c["at"])
    if i in scores:
        n["scores"] = scores[i]
    if i in plain:
        n["plain"] = plain[i]

# commits whose message names an item
commits = {}
for line in git("log", "--all", "--format=%h\t%at\t%an\t%s").splitlines():
    h, at, an, s = line.split("\t", 3)
    for i in set(ID.findall(s)):
        if i in nodes:
            commits.setdefault(i, []).append([h, int(at), an, s[:160]])
for i, c in commits.items():
    nodes[i]["commits"] = sorted(c, key=lambda x: x[1])[:8]
    nodes[i]["n_commits"] = len(c)

edges = {}  # (older, newer) -> {"k": kind, "via": where the reference is written}


def link(a, b, via, kind="ref", at=0):
    """at: when the reference was written (ms); the edge exists from then, and not before both items do."""
    if a == b or a not in nodes or b not in nodes:
        return
    old, new = sorted((a, b), key=lambda i: (nodes[i]["at"], i))
    at = max(at, nodes[new]["at"])
    had = edges.get((old, new))
    if not had or (kind == "ref" and (had["k"] != "ref" or at < had["at"])):
        edges[(old, new)] = {"k": kind, "via": via, "at": at}


items = list(nodes.values())
for n in items:
    for m in set(ID.findall(n["text"])):
        link(n["id"], m, "text")
    for c in n["comments"]:
        for m in set(ID.findall(c["text"])):
            link(n["id"], m, "comment", at=ns(c["at"]) // 10**6)

# finding pages: time of the commit that added the file
for f in sorted((REPO / "tools").glob("finding_*.py")):
    src = f.read_text()
    added = git("log", "--all", "--diff-filter=A", "--format=%at\t%ae", "--", f"tools/{f.name}").splitlines()
    if not added:
        continue
    at, an = added[-1].split("\t")
    t = re.search(r'^TITLE = "(.*)"', src, re.M)
    ln = re.search(r'^LINE = \(?\s*"(.*)"', src, re.M)
    slug = f.stem[len("finding_"):].replace("_", "-")
    i = f"finding/{slug}"
    nodes[i] = {"id": i, "kind": "finding", "who": an, "branch": "", "text": (ln.group(1) if ln else ""), "at": int(at) * 1000,
                "plain": {"title": t.group(1) if t else slug}, "path": f"tools/{f.name}", "comments": [], "session": ""}
    for m in set(ID.findall(src)):
        link(i, m, "page source")

# theory rounds: the cutoff is when the round read the board
for d in sorted((REPO / "studies/theory/results/engine").glob("round-*")):
    run = json.loads((d / "run.json").read_text())
    i = f"theory/{d.name}"
    named = set(ID.findall(json.dumps(run)))
    tg = d / "targets.jsonl"
    if tg.exists():
        named |= set(ID.findall(tg.read_text()))
    added = git("log", "--all", "--diff-filter=A", "--format=%at\t%ae", "--", str((d / "run.json").relative_to(REPO))).splitlines()
    at, an = added[-1].split("\t")
    nodes[i] = {"id": i, "kind": "theory", "who": an, "branch": "", "at": int(at) * 1000, "session": "", "comments": [],
                "text": f"Theory round {d.name[-2:]}: theories proposed from the board items before {run.get('cutoff', '?')} UTC, "
                        f"scored on {len(set(ID.findall(tg.read_text()))) if tg.exists() else 0} later board items (targets.jsonl).",
                "plain": {"title": f"Theory round {d.name[-2:]}"}, "path": str(d.relative_to(REPO))}
    for m in named:
        link(i, m, "targets.jsonl / run.json")

# consecutive items of one agent session
by = {}
for n in items:
    if n["session"]:
        by.setdefault(n["session"], []).append(n)
for s in by.values():
    s.sort(key=lambda n: n["at"])
    for a, b in zip(s, s[1:]):
        link(a["id"], b["id"], "same agent session", "session")

for n in nodes.values():  # a git email becomes the board name, by the rule of team.who()
    if "@" in n["who"]:
        n["who"] = n["who"].split("@")[0].split("+")[-1]
out = {"built": team.now(), "nodes": sorted(nodes.values(), key=lambda n: n["at"]),
       "edges": sorted(({"s": a, "t": b, **e} for (a, b), e in edges.items()), key=lambda e: e["at"])}
(HERE / "data.json").write_text(json.dumps(out, separators=(",", ":")))
print(len(out["nodes"]), "nodes", sum(e["k"] == "ref" for e in out["edges"]), "ref edges",
      sum(e["k"] == "session" for e in out["edges"]), "session edges", (HERE / "data.json").stat().st_size, "bytes")
