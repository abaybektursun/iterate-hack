# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35"]
# ///
"""Build data.json for the switchboard prototype: who talked to whom among the agents.

  uv run studies/sitelab/prototypes/switchboard/build.py

Read-only. Source: the team table of tools/team.py (the rows time-helix and music-box read), by queries:
the team key may not scan the table, so an item that is in no list and that no message names is not read.
  broadcast   a row of chan#all (msg.py send all, and the announcements board.py makes there)
  direct      a row of chan#@<person> that is not the copy of a comment
  comment     a comment row of a board item (item#<id> / comment#...), or a message in the item's thread
              (chan#<item id>), written by another agent than the item's author. Receiver: the author's agent.
  own note    the same, written by the item's author: counted (`own_notes`), not stored
  work        every work item with the time it was posted and closed: the lamp above its agent's jack

An agent is person/branch plus the first 4 characters of its session id (msg.py: "an agent is a session plus a git
branch"). Each person keeps a jack for their KEEP busiest agents (messages sent + comments received + work items);
the rest share one "other sessions" jack. Tables are column arrays; a time is whole seconds after `t0` (unix seconds,
UTC). msgs: t time, k kind (0 broadcast, 1 direct, 2 comment), a sender (index of `names`), j sender's jack, b and r
the receiving agent and its jack (comments), p the receiving person, c channel (index of `chans`), x text. work: t
posted, e closed (null: open), a agent, j jack, id, x text. jacks: person, name (-1: the pooled jack), agents in it.
Text is cut to CUT characters. Email addresses, home folders and anything shaped like a key are replaced; the build
stops if one is left, or if a count differs from the board's own.
"""
import calendar
import collections
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "tools"))

from boto3.dynamodb.conditions import Key  # noqa: E402

import board  # noqa: E402

KEEP, CUT, HOLD_MIN = 14, 140, 30
LISTS = ("work", "result", "idea", "knowledge", "skill", "work-closed")
PRIVATE = [(re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]*\w"), "[email]"), (re.compile(r"/(?:home|Users)/[^/\s\"']+"), "~"),
           (re.compile(r"\b(?:sk|hf|ghp|gho|ak|as|xoxb|xoxp)[-_][A-Za-z0-9_-]{16,}|\bAKIA[A-Z0-9]{16}\b"), "[key]")]


def text(s):
    for pattern, word in PRIVATE:
        s = pattern.sub(word, s)
    s = " ".join(s.split())
    return s if len(s) <= CUT else s[:CUT - 1].rstrip() + "…"


def agent(r):
    """The key of the agent that wrote a row: (person, branch, first 4 of the session id)."""
    return (r["who"], r.get("branch") or "", (r.get("session") or "")[:4])


def name(a):
    return a[0] + ("/" + a[1] if a[1] else "") + (" " + a[2] if a[2] else "")


q = lambda pk: board.rows(KeyConditionExpression=Key("pk").eq(pk))
ID = re.compile(r"\b(?:work|result|idea|knowledge|skill)-[0-9a-f]{6}\b")
with ThreadPoolExecutor(16) as pool:
    lists = list(pool.map(lambda l: board.rows(IndexName="new", KeyConditionExpression=Key("listed").eq(l)), LISTS))
    listed = {r["id"] for page in lists for r in page}
    people = sorted({r["who"] for page in lists for r in page})
    everyone = q("chan#all")
    inbox = list(pool.map(lambda p: q(f"chan#@{p}"), people))
    # the first items were stored before the lists existed: they are found by the ids the messages name
    named = {i for ms in [everyone, *inbox] for m in ms for i in ID.findall(m["text"])} - listed
    ids = sorted(listed | named)
    stored = dict(zip(ids, pool.map(lambda i: q(f"item#{i}"), ids)))   # the item, its comments and its votes
    items = {i: next(r for r in rs if r["sk"] == "item") for i, rs in stored.items() if rs}
    assert listed <= set(items)
    threads = list(pool.map(lambda i: q(f"chan#{i}"), items))
commented = list(items)
comments = [[r for r in stored[i] if r["sk"].startswith("comment#")] for i in items]
assert all(len(c) == int(items[i].get("n_comments", 0)) for i, c in zip(items, comments)), "comments read != an item's n_comments"
assert {m["who"] for ms in [everyone, *inbox, *threads, *comments] for m in ms} <= set(people), "a sender that never posted an item"

ns = lambda sk: int(sk.split("#")[0])
msgs, own_notes = [], 0   # [time ns, kind, sender agent, receiver agent or None, receiver person or None, channel, text]
for m in everyone:
    msgs.append([ns(m["sk"]), 0, agent(m), None, None, "all", m["text"]])
on_item = [(i, int(c["sk"].split("#")[1]), c) for i, rows in zip(commented, comments) for c in rows]
on_item += [(i, ns(m["sk"]), m) for i, rows in zip(items, threads) for m in rows]
told = set()   # (time ns, sender) of every comment: board.py copies one by another agent to the author's channel
for item_id, t, c in on_item:
    owner = agent(items[item_id])
    told.add((t, c["who"]))
    if agent(c) == owner:
        own_notes += 1
        continue
    msgs.append([t, 2, agent(c), owner, owner[0], item_id, c["text"]])
copies = 0
for p, rows in zip(people, inbox):
    for m in rows:
        if (ns(m["sk"]), m["who"]) in told and m["text"].startswith("comment on your "):
            copies += 1
            continue
        assert not m["text"].startswith("comment on your "), f"a comment copy without its comment: {m['sk']}"
        msgs.append([ns(m["sk"]), 1, agent(m), None, p, "@" + p, m["text"]])
msgs.sort(key=lambda m: m[0])

work = [r for r in items.values() if r["kind"] == "work"]
assert all(("closed_at" in r) == (r.get("listed") != "work") for r in work), "a work item that is neither listed open nor closed with a time"

# ---- the jacks: each person's KEEP busiest agents, the rest pooled
busy = collections.Counter()
for m in msgs:
    busy[m[2]] += 1
    if m[3]:
        busy[m[3]] += 1
for r in work:
    busy[agent(r)] += 1
jacks, jack_of = [], {}
names = {}
nm = lambda a: names.setdefault(name(a), len(names))
for p, person in enumerate(people):
    mine = sorted((a for a in busy if a[0] == person), key=lambda a: (-busy[a], a))
    for a in mine[:KEEP]:
        jack_of[a] = len(jacks)
        jacks.append([p, nm(a), 1])
    if mine[KEEP:]:
        for a in mine[KEEP:]:
            jack_of[a] = len(jacks)
        jacks.append([p, -1, len(mine) - KEEP])

t0 = min(msgs[0][0], min(int(r["at_ns"]) for r in work)) // 10**9
sec = lambda t_ns: t_ns // 10**9 - t0
clock = lambda s, f: calendar.timegm(time.strptime(s, f))


def closed(r):
    """Seconds after t0 at which a work item was closed. The first rows hold local times without a zone ('2026-11-14
    12:17:43'): their zone is the difference between the row's own `at` in that form and its at_ns."""
    if r["closed_at"].endswith("Z"):
        return clock(r["closed_at"], "%Y-%m-%dT%H:%M:%SZ") - t0
    local = "%Y-%m-%d %H:%M:%S"
    return clock(r["closed_at"], local) + int(r["at_ns"]) // 10**9 - clock(r["at"], local) - t0


chans = {}
M = {"t": [], "k": [], "a": [], "j": [], "b": [], "r": [], "p": [], "c": [], "x": []}
for t, k, a, rcv, rp, chan, body in msgs:
    for col, v in zip("tkajbrpcx", (sec(t), k, nm(a), jack_of[a], nm(rcv) if rcv else -1, jack_of[rcv] if rcv else -1,
                                   people.index(rp) if rp else -1, chans.setdefault(chan, len(chans)), text(body))):
        M[col].append(v)
W = {"t": [], "e": [], "a": [], "j": [], "id": [], "x": []}
for r in sorted(work, key=lambda r: int(r["at_ns"])):
    for col, v in zip(("t", "e", "a", "j", "id", "x"), (sec(int(r["at_ns"])), closed(r) if "closed_at" in r else None,
                                                         nm(agent(r)), jack_of[agent(r)], r["id"], text(r["text"]))):
        W[col].append(v)
assert all(e is None or e >= t - 60 for t, e in zip(W["t"], W["e"])), "a work item closed before it was posted"

kinds = collections.Counter(M["k"])
assert kinds[0] == len(everyone) and kinds[1] + copies == sum(map(len, inbox)), "a message was lost or counted twice"
out = {"built": int(time.time()), "t0": t0, "t1": max(M["t"] + W["t"] + [e for e in W["e"] if e is not None]),
       "hold_min": HOLD_MIN, "keep": KEEP, "people": people, "names": list(names), "chans": list(chans), "jacks": jacks,
       "own_notes": own_notes, "msgs": M, "work": W}
blob = json.dumps(out, separators=(",", ":"), ensure_ascii=False)
for pattern, _ in PRIVATE:
    if found := pattern.search(blob):
        sys.exit(f"private text left in the data: {found[0][:12]}")
assert all(n.split("/")[0].split(" ")[0] in people for n in names), "a name that is not a board handle"
assert len(blob.encode()) < 400_000, len(blob.encode())
(HERE / "data.json").write_text(blob)

L = list(names)
pairs = collections.Counter((L[a], L[b] if b >= 0 else "@" + people[p]) for a, b, p, k in zip(M["a"], M["b"], M["p"], M["k"]) if k)
print(f"data.json {len(blob.encode()) // 1024} kB: {len(msgs)} messages = {kinds[0]} broadcasts + {kinds[1]} direct + {kinds[2]} comments; "
      f"{own_notes} own notes not stored; {len(work)} work items; {len(names)} agents on {len(jacks)} jacks")
print("busiest lines:", pairs.most_common(4))
