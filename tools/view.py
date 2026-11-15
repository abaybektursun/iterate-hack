# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35"]
# ///
"""The board and the messages as a live web page on this laptop, read-only.

  uv run tools/view.py [--port 8765] [--hours 6]

Opens http://127.0.0.1:8765 in the browser (only when started from a terminal). The page shows one sentence on the
state of the board (and what changed since the reader's last visit, kept in localStorage), one hill-climbing chart per
benchmark with 95% intervals and its record steps listed under it, each with its finding, then open work (longest idle
first, red after 60 minutes, with its last comment), results with their scores and the messages on the channel `all`;
below them one lane per person with every post and message of the last --hours, then ideas, knowledge and skills, and
recently closed work. It reads /data every 10 s and rewrites only what changed. A click on an item opens its full
text, scores, votes, comments and message thread in a side panel whose address is /#<item id>; the filters are in the
address too (/?who=<name>&q=<text>&idle=1). Keys: / filter, j and k move, 1 2 3 jump to a column, Enter opens, Esc
closes, ? lists the keys. A click on a person shows only that person.

  GET /architecture    the Design tab, how the harness works: one interactive picture (architecture.py), fed by the same /data
  GET /findings        the Findings tab: one tile per finding (findings.py), each a link to the page of that finding
  GET /finding/<slug>  the page of one finding (finding_<slug>.py; .claude/skills/finding-page/SKILL.md)
  GET /proof           the Proof tab: one tile per experiment that tests the team's method itself (the page of findings.py)
  GET /proof/<slug>    the page of one such experiment (proof_<slug>.py, made like a finding page)
  GET /data            the newest 60 items of each kind and list, the messages on `all` of the last --hours, every score
                       (board.py score), which the hill-climbing charts draw, the first line of each scored result's
                       finding (climb.finding) and the newest comment of each open work item idle over an hour (JSON),
                       with only the fields the pages read. One snapshot serves every reader for 5 s. Its ETag comes from
                       the content and its time is in the header X-Snapshot-Ns, so a browser that asks again with
                       If-None-Match gets 304 and no body while the board has not changed. The page stops reading while
                       its tab is hidden.
  GET /data/<item id>  one item with its votes, comments and thread (JSON); 404 for an unknown id

It reads the same DynamoDB table as board.py and msg.py, with Query and GetItem only, and never writes to it or moves an
agent's message position. A failed read answers 500 with the error text; the page keeps the last data, says "Offline" in its
status and logs the error to the browser console.
"""
import glob
import hashlib
import importlib
import json
import os
import sys
import threading
import time
import traceback
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from boto3.dynamodb.conditions import Key

import architecture
import board
import climb
import findings
import team

PORT = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8765
HOURS = float(sys.argv[sys.argv.index("--hours") + 1]) if "--hours" in sys.argv else 6.0
LISTS = ("work", "result", "idea", "knowledge", "skill", "work-closed")
# One page per finding: every tools/finding_<slug>.py (TITLE, LINE, PAGE) is served at /finding/<slug> and has a tile
# on /findings. Its ICON, the JavaScript source of the tile's icon, is written into that page here (findings.py).
FINDINGS = {os.path.basename(f)[len("finding_"):-3].replace("_", "-"): importlib.import_module(os.path.basename(f)[:-3])
            for f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "finding_*.py")))}


def tiles_page(modules, differences=()):
    """The tile page of findings.py with the icons of these modules written in, and the given text differences applied."""
    page = findings.PAGE.replace("__ICONS__", "{" + ", ".join(f"{json.dumps(s)}: {m.ICON}" for s, m in modules.items() if hasattr(m, "ICON")) + "}")
    for old, new in differences:
        assert page.count(old) == 1, f"findings.PAGE no longer holds {old!r} once"
        page = page.replace(old, new)
    return page


FINDINGS_PAGE = tiles_page(FINDINGS)
# One page per experiment that tests the team's method itself: every tools/proof_<slug>.py, with the same four values
# as a finding page, is served at /proof/<slug> and has a tile on /proof.
PROOFS = {os.path.basename(f)[len("proof_"):-3].replace("_", "-"): importlib.import_module(os.path.basename(f)[:-3])
          for f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "proof_*.py")))}
PROOF_PAGE = tiles_page(PROOFS, findings.PROOF)


def newest(listed, n=60):
    return team.table().query(IndexName="new", KeyConditionExpression=Key("listed").eq(listed), ScanIndexForward=False, Limit=n)["Items"]


# What the pages read of each row (grep tools/view.py and tools/architecture.py before dropping one); the rest stays out of /data.
ITEM = ("id", "listed", "kind", "who", "branch", "text", "at_ns", "active_ns", "closed_at", "closed_by", "ups", "downs", "n_comments", "agent", "session")
MESSAGE = ("sk", "who", "branch", "text", "agent", "session")
SCORE = ("sk", "result", "model", "benchmark", "right", "n", "config", "tokens", "who")
LATE_NS = 59 * 60 * 10**9  # the board shows the last comment of open work idle over an hour; a minute early, so it is there in time
COMMENTS = {}  # (work id, n_comments) -> its newest comment; a new comment changes n_comments
FOUND = {}  # result id -> the first line of its finding; board.py never changes an item's text after posting


def cols(rows, keys):
    return [{k: r[k] for k in keys if k in r} for r in rows]


def last_comment(item_id):
    found = team.table().query(KeyConditionExpression=Key("pk").eq(f"item#{item_id}") & Key("sk").begins_with("comment#"),
                               ScanIndexForward=False, Limit=1)["Items"]
    return {k: found[0][k] for k in ("who", "text", "at")}


def finding(item_id):  # not BatchGetItem: the team key and the Lambda role (infra/monitor) allow only Query and GetItem
    return climb.finding(team.table().get_item(Key={"pk": f"item#{item_id}", "sk": "item"})["Item"]["text"])


def snapshot():
    start = f"{time.time_ns() - int(HOURS * 3600 * 10**9):020d}"
    with ThreadPoolExecutor(len(LISTS) + 2) as pool:  # every list, the messages and the scores at the same time
        messages = pool.submit(board.rows, KeyConditionExpression=Key("pk").eq("chan#all") & Key("sk").gt(start))
        scores = pool.submit(board.rows, KeyConditionExpression=Key("pk").eq("scores"))  # every score, in the order its result was posted
        items = [item for page in pool.map(newest, LISTS) for item in page]
        messages, scores = messages.result(), scores.result()
        late = [(i["id"], i["n_comments"]) for i in items if i["listed"] == "work" and i.get("n_comments")
                and time.time_ns() - int(i.get("active_ns", i["at_ns"])) >= LATE_NS]
        new = [k for k in late if k not in COMMENTS]
        COMMENTS.update(zip(new, pool.map(lambda k: last_comment(k[0]), new)))
        texts = {i["id"]: i["text"] for i in items}
        scored = [r for r in dict.fromkeys(s["result"] for s in scores) if r not in FOUND]
        # one GetItem per scored result that is not among the newest 60 results, once per process
        FOUND.update(zip(scored, pool.map(lambda r: climb.finding(texts[r]) if r in texts else finding(r), scored)))
    return {"hours": HOURS, "test": team.TEST, "items": cols(items, ITEM), "messages": cols(messages, MESSAGE), "scores": cols(scores, SCORE),
            "last_comments": {k[0]: COMMENTS[k] for k in late}, "finding": {r: FOUND[r] for r in dict.fromkeys(s["result"] for s in scores)},
            "findings": [{"slug": slug, "title": m.TITLE, "line": m.LINE} for slug, m in FINDINGS.items()],
            "proofs": [{"slug": slug, "title": m.TITLE, "line": m.LINE} for slug, m in PROOFS.items()]}


SNAPSHOT = {"at": 0.0, "ns": 0, "body": ""}
SNAPSHOT_LOCK = threading.Lock()
FRESH_S = 5  # readers within 5 s of each other share one set of queries; wall time, because a frozen Lambda stops the monotonic clock


def snapshot_json():
    with SNAPSHOT_LOCK:  # a reader that arrives while the queries run waits for them instead of starting its own
        if time.time() - SNAPSHOT["at"] >= FRESH_S:
            body = json.dumps(snapshot(), default=int, separators=(",", ":"))  # DynamoDB numbers are Decimal; all are integers
            SNAPSHOT.update(at=time.time(), ns=time.time_ns(), body=body)
        return SNAPSHOT["body"], SNAPSHOT["ns"]


def detail(item_id):
    rows = board.rows(KeyConditionExpression=Key("pk").eq(f"item#{item_id}"))  # the item, its votes and its comments
    item = next((r for r in rows if r["sk"] == "item"), None)
    if not item:
        return None
    return {"item": item, "votes": [r for r in rows if r["sk"].startswith("vote#")],
            "comments": sorted((r for r in rows if r["sk"].startswith("comment#")), key=lambda c: c["sk"]),
            "thread": board.rows(KeyConditionExpression=Key("pk").eq(f"chan#{item_id}"))}


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"  # Chrome revalidates with If-None-Match only for HTTP/1.1 responses

    def send(self, status, kind, body, headers=()):
        data = body.encode()
        tag = f'"{hashlib.blake2b(data, digest_size=16).hexdigest()}"'  # from the content, so an unchanged board answers 304
        if status == 200 and self.headers.get("If-None-Match") == tag:
            self.send_response(304)
            data = b""
        else:
            self.send_response(status)
            self.send_header("Content-Type", f"{kind}; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
        if status == 200:
            self.send_header("ETag", tag)
            self.send_header("Cache-Control", "no-cache")  # the browser keeps the body and asks again with If-None-Match
        else:
            self.send_header("Cache-Control", "no-store")
        for header in headers:
            self.send_header(*header)
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/":
            return self.send(200, "text/html", PAGE)
        if path == "/architecture":
            return self.send(200, "text/html", architecture.PAGE)
        if path == "/findings":
            return self.send(200, "text/html", FINDINGS_PAGE)
        if path.startswith("/finding/") and path[len("/finding/"):] in FINDINGS:
            return self.send(200, "text/html", FINDINGS[path[len("/finding/"):]].PAGE)
        if path == "/proof":
            return self.send(200, "text/html", PROOF_PAGE)
        if path.startswith("/proof/") and path[len("/proof/"):] in PROOFS:
            return self.send(200, "text/html", PROOFS[path[len("/proof/"):]].PAGE)
        if path != "/data" and not path.startswith("/data/"):
            return self.send(404, "text/plain", f"no page {path}")
        try:  # the page shows the error text; the traceback goes to this terminal
            if path == "/data":  # the time of the read goes in a header, so the body and its ETag change only with the board
                body, ns = snapshot_json()
                return self.send(200, "application/json", body, [("X-Snapshot-Ns", str(ns))])
            found = detail(path[len("/data/"):])
        except (Exception, SystemExit) as error:
            traceback.print_exc()
            return self.send(500, "text/plain", f"{type(error).__name__}: {error}")
        if found is None:
            return self.send(404, "text/plain", f"no item {path[len('/data/'):]}")
        self.send(200, "application/json", json.dumps(found, default=int))  # DynamoDB numbers are Decimal; all are integers

    def log_message(self, *args):
        pass


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Team board</title>
<link rel="preload" href="/data" as="fetch" crossorigin>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap" media="print" onload="this.media='all'">
<style>
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34;
  --pl: .56; --pc: .15;
  --grid: color-mix(in srgb, var(--rule) 60%, var(--paper));
  --blue-wash: color-mix(in srgb, var(--blue) 10%, transparent);
  --red-wash: color-mix(in srgb, var(--red) 10%, transparent);
  --scrim: rgb(16 24 32 / .18);
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --pl: .78; --pc: .13;
    --grid: color-mix(in srgb, var(--rule) 70%, var(--paper));
    --blue-wash: color-mix(in srgb, var(--blue) 14%, transparent);
    --red-wash: color-mix(in srgb, var(--red) 15%, transparent);
    --scrim: rgb(0 0 0 / .4);
  }
}
* { box-sizing: border-box; }
[hidden] { display: none !important; }
html { background: var(--paper); }
body {
  margin: 0; color: var(--ink); background: var(--paper); overflow-anchor: none;
  font: 400 15px/1.45 "Archivo", ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif; -webkit-font-smoothing: antialiased;
}
button { font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; text-align: inherit; }
a { color: inherit; text-decoration: none; }
code { font: inherit; font-weight: 600; }
:focus-visible { outline: 2px solid var(--blue); outline-offset: 2px; border-radius: 3px; }
.num, .meta, .status, .count, .hp svg, .axis { font-variant-numeric: tabular-nums; }
.wrap { max-width: 1840px; margin: 0 auto; padding: 20px 40px 72px; }

/* Header: name, links, filter, status */
.top { display: flex; align-items: center; gap: 8px 22px; flex-wrap: wrap; min-height: 36px; }
.name { margin: 0; font-size: 15px; font-weight: 600; font-stretch: 112%; letter-spacing: .01em; white-space: nowrap; }
.links { display: flex; flex-wrap: wrap; gap: 4px 18px; font-size: 13px; color: var(--mute); min-width: 0; }
.links a:hover { color: var(--ink); }
.links a[aria-current] { color: var(--ink); font-weight: 600; }
.test { color: var(--red); font-weight: 600; font-size: 13px; }
.search { margin-left: auto; position: relative; display: flex; align-items: center; }
.search input {
  width: 280px; font: inherit; font-size: 14px; color: var(--ink); background: var(--sheet);
  border: 1px solid var(--rule); border-radius: 8px; padding: 6px 34px 6px 12px;
}
.search input::placeholder { color: var(--faint); }
.search input:focus { outline: 2px solid var(--blue); outline-offset: 0; border-color: transparent; }
kbd {
  font: 400 12px/1 "Archivo", sans-serif; color: var(--mute); border: 1px solid var(--rule); border-radius: 4px;
  padding: 3px 6px; background: var(--paper);
}
.search kbd { position: absolute; right: 8px; pointer-events: none; }
.status { font-size: 13px; color: var(--mute); white-space: nowrap; display: flex; align-items: center; gap: 8px; }
.status::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--faint); }
.status.live::before { background: var(--blue); box-shadow: 0 0 0 3px var(--blue-wash); }
.status.bad { color: var(--red); }
.status.bad::before { background: var(--red); }

/* One sentence on the state of the board; above it, what changed since the last visit */
.lede { margin-top: 18px; min-height: 29px; }
.since { margin: 0 0 6px; font-size: 15px; }
.since::before { content: ""; display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: var(--blue); margin-right: 9px; vertical-align: .08em; }
.sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); white-space: nowrap; }
.since b { font-weight: 600; }
.summary { margin: 0; font-size: 22px; line-height: 1.3; font-weight: 300; letter-spacing: -.005em; }
.summary b { font-weight: 600; }
.summary .warn { color: var(--red); }
.summary button, .summary a { text-decoration: underline 1px; text-underline-offset: 4px; text-decoration-color: color-mix(in srgb, currentColor 35%, transparent); }
.summary button:hover, .summary a:hover, .summary button[aria-pressed="true"] { text-decoration-color: currentColor; }
.filters { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.filters:empty { display: none; }
.chip {
  display: inline-flex; align-items: center; gap: 6px; font-size: 13px; color: var(--mute);
  border: 1px solid var(--rule); border-radius: 999px; padding: 3px 4px 3px 12px; background: var(--sheet);
}
.chip button { color: var(--mute); border-radius: 999px; padding: 0 7px; }
.chip button:hover { color: var(--ink); }

/* Hill: per benchmark, the best untrained-base score so far against the best RL score */
.hill { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 540px), 1fr)); gap: 24px 56px; margin-top: 26px; }
.hp h2 { border-bottom-color: var(--rule); }
.hp-body { display: grid; grid-template-columns: 230px minmax(0, 1fr); gap: 20px; margin-top: 14px; }
.hp-stats { display: flex; flex-direction: column; gap: 12px; }
.hp-stats p { margin: 2px 0 0; font-size: 13px; color: var(--mute); text-wrap: balance; }
.hp-stats p.cfg { color: var(--ink); font-size: 12.5px; }
.big { display: block; font-size: 40px; line-height: 1; font-weight: 600; font-stretch: 112%; letter-spacing: -.02em; color: var(--blue); width: max-content; }
.big small { font-size: 17px; font-weight: 400; letter-spacing: 0; margin-left: 3px; color: var(--mute); }
.togo { margin: 0 !important; font-size: 15px !important; color: var(--ink) !important; }
.togo b { color: var(--red); font-weight: 600; font-size: 22px; font-stretch: 112%; letter-spacing: -.01em; margin-right: 2px; }
.hp-chart { min-width: 0; height: 184px; }
.hp svg { display: block; overflow: visible; }
.hp svg text {
  font: 400 11px "Archivo", ui-sans-serif, system-ui, sans-serif; fill: var(--mute);
  paint-order: stroke; stroke: var(--paper); stroke-width: 4px; stroke-linejoin: round;
}
.hp .brk { stroke: var(--paper); stroke-width: 5px; }
.hp .brk-line { stroke: var(--blue); stroke-width: 1.4px; }
.hp .grid { stroke: var(--rule); stroke-width: 1; }
.hp .gap { fill: var(--red-wash); }
.hp .target { stroke: var(--ink); stroke-width: 1.2; stroke-dasharray: 3 4; opacity: .6; }
.hp text.rl { fill: var(--ink); }
.hp text.rl tspan { font-weight: 600; }
.hp .tread, .hp .rise { fill: none; stroke: var(--blue); stroke-width: 2.25; stroke-linecap: round; }
.hp .rise.noise { opacity: .32; }
.hp .ci { stroke: var(--faint); stroke-width: 1; opacity: .55; }
.hp .ci.rec { stroke: var(--blue); opacity: .6; }
.hp .dot { fill: var(--paper); stroke: var(--faint); stroke-width: 1.5; }
.hp .dot.rec { fill: var(--blue); stroke: var(--paper); stroke-width: 2; }
.hp .x { stroke: var(--faint); stroke-width: 1.6; stroke-linecap: round; }
.hp .hit { fill: transparent; }
.hp .under { fill: var(--paper); }
.hp a:hover .dot, .hp a:focus-visible .dot { stroke: var(--ink); }
.hp a:hover .x, .hp a:focus-visible .x { stroke: var(--ink); }
.hp text.gain { fill: var(--ink); font-weight: 600; }
.hp text.quiet { fill: var(--faint); }
.steps { margin-top: 12px; font-size: 13px; }
.steps a { display: grid; grid-template-columns: 3.4em minmax(0, 1fr); gap: 1px 12px; padding: 6px 0; border-top: 1px solid var(--rule); color: var(--mute); }
.steps a > * { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.steps b { grid-row: span 2; color: var(--ink); font-weight: 600; }
.steps .fin { color: var(--ink); }
.steps .noise, .steps .noise b, .steps .noise .fin { color: var(--faint); }
.steps a:hover .fin { text-decoration: underline 1px; text-underline-offset: 3px; }
.hkey { grid-column: 1 / -1; display: flex; flex-wrap: wrap; gap: 6px 16px; margin-top: -8px; font-size: 12.5px; color: var(--mute); }
.hkey span { display: inline-flex; align-items: center; gap: 7px; }
.hkey svg { overflow: visible; }

/* Board columns */
.board {
  display: grid; gap: 0 48px; align-items: start; margin-top: 34px;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.08fr) minmax(0, 1fr);
}
section { min-width: 0; }
h2 {
  margin: 0; font-size: 15px; font-weight: 600; font-stretch: 112%; letter-spacing: .005em;
  display: flex; align-items: baseline; gap: 10px; padding-bottom: 9px; border-bottom: 1px solid var(--ink);
}
h2 .count { color: var(--faint); font-weight: 400; font-stretch: 100%; font-size: 13px; }
h2 .toggle { margin-left: auto; font-size: 13px; font-weight: 400; font-stretch: 100%; color: var(--mute); white-space: nowrap; }
h2 .toggle:hover { color: var(--ink); }
.empty { color: var(--mute); font-size: 14px; padding: 14px 0; max-width: 46ch; margin: 0; }
.more { display: block; padding: 10px 0; font-size: 13px; color: var(--mute); }
.more:hover { color: var(--ink); }

.row { position: relative; padding: 12px 0 12px 14px; border-bottom: 1px solid var(--rule); cursor: pointer; }
.row::before { content: ""; position: absolute; left: 0; top: 14px; bottom: 14px; width: 3px; border-radius: 2px; background: var(--pc-color); }
.row:hover { background: linear-gradient(to right, var(--sheet), transparent 90%); }
.row.current { background: var(--sheet); }
.row .open { display: block; border-radius: 2px; }
.text { display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden; overflow-wrap: anywhere; white-space: pre-line; }
.result .text { -webkit-line-clamp: 3; }
.n { font-weight: 600; font-variant-numeric: tabular-nums; }
.closed .text { color: var(--mute); }
.last { margin: 5px 0 0; font-size: 13px; color: var(--mute); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.meta { display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: baseline; gap: 14px; margin-top: 6px; font-size: 13px; color: var(--mute); }
.meta .m { min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.meta .m > * { margin-right: 12px; vertical-align: baseline; }
.meta .m > :last-child { margin-right: 0; }
.who { color: oklch(var(--pl) var(--pc) var(--h)); font-weight: 600; }
.who:hover { text-decoration: underline; text-underline-offset: 3px; }
.branch { display: inline-block; vertical-align: top !important; max-width: 14ch; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.id { color: var(--faint); }
.fresh { color: var(--blue); }
.idle { display: inline-flex; align-items: center; gap: 8px; white-space: nowrap; }
.meter { width: 44px; height: 3px; border-radius: 2px; background: var(--rule); overflow: hidden; }
.meter i { display: block; height: 100%; background: var(--faint); }
.late .idle { color: var(--red); font-weight: 600; }
.late .meter i { background: var(--red); }
.scores { display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 14px; margin-top: 6px; font-size: 13px; color: var(--mute); }
.score { white-space: nowrap; color: var(--mute); }
.score b { color: var(--ink); font-weight: 600; }
.new::after { content: ""; position: absolute; left: -11px; top: calc(13px + .75em - 3px); width: 6px; height: 6px; border-radius: 50%; background: var(--blue); }

.msgs { list-style: none; margin: 0; padding: 0; }
.msg { position: relative; padding: 11px 0; border-bottom: 1px solid var(--rule); cursor: pointer; }
.msg .meta { display: flex; gap: 12px; margin: 0 0 3px; }
.msg.full .text { display: block; }
a.ref { color: var(--blue); text-decoration: underline; text-decoration-color: var(--blue-wash); text-underline-offset: 3px; }
a.ref:hover { text-decoration-color: var(--blue); }

/* Placeholders before the first read */
.ph { display: block; height: 10px; border-radius: 5px; background: var(--rule); }
.ph-row { display: grid; gap: 10px; padding: 18px 0 18px 14px; border-bottom: 1px solid var(--rule); }
.ph-row .ph:nth-child(2) { width: 70%; }
.ph-row .ph:nth-child(3) { width: 40%; height: 8px; opacity: .7; }

/* Activity: one lane per person, every post and message of the last hours as a mark */
.activity { margin-top: 44px; }
.lanes { margin-top: 8px; }
.lane { display: grid; grid-template-columns: 150px minmax(0, 1fr); align-items: center; height: 28px; }
.lane > button {
  font-size: 13px; color: var(--mute); padding-right: 12px; overflow: hidden; text-overflow: ellipsis;
  white-space: nowrap; display: flex; align-items: center; gap: 8px;
}
.lane > button::before { content: ""; flex: none; width: 8px; height: 8px; border-radius: 50%; background: var(--pc-color); }
.lane > button:hover, .lane.on > button { color: var(--ink); }
.lane.off { opacity: .28; }
.track {
  position: relative; height: 100%;
  background: linear-gradient(var(--rule), var(--rule)) 0 50% / 100% 1px no-repeat,
              linear-gradient(to right, var(--grid) 1px, transparent 1px) 0 0 / var(--hour) 100%;
}
.mk { position: absolute; top: 50%; transform: translate(-50%, -50%); border-radius: 50%; --c: var(--pc-color); }
.mk.res { width: 9px; height: 9px; background: var(--c); z-index: 3; }
.mk.scored { box-shadow: 0 0 0 1.5px var(--paper), 0 0 0 3px var(--blue); }
.mk.claim { width: 9px; height: 9px; border: 1.5px solid var(--c); background: var(--paper); z-index: 2; }
.mk.idea { width: 5px; height: 5px; background: var(--c); z-index: 1; }
.mk.tick { width: 1px; height: 11px; border-radius: 0; background: var(--faint); opacity: .8; }
a.mk::before { content: ""; position: absolute; inset: -6px; }
a.mk:hover, a.mk:focus-visible { --c: var(--ink); }
.axis { display: grid; grid-template-columns: 150px minmax(0, 1fr); font-size: 12px; color: var(--faint); }
.axis div { position: relative; height: 18px; }
.axis div span { position: absolute; top: 4px; transform: translateX(-50%); white-space: nowrap; }
.axis div span:first-child { transform: none; }
.axis div span:last-child { transform: translateX(-100%); }
.legend { display: flex; flex-wrap: wrap; gap: 6px 20px; margin: 10px 0 0 150px; font-size: 13px; color: var(--mute); }
.legend span { display: inline-flex; align-items: center; gap: 8px; }
.legend .mk { position: relative; top: auto; transform: none; flex: none; --c: var(--mute); }

.rest { margin-top: 44px; }

/* Item panel */
.scrim { position: fixed; inset: 0; z-index: 2; background: var(--scrim); animation: fade .18s ease-out; }
@keyframes fade { from { opacity: 0; } }
.panel {
  position: fixed; top: 0; right: 0; bottom: 0; width: min(620px, 100vw); z-index: 3;
  background: var(--sheet); border-left: 1px solid var(--rule); overflow-y: auto;
  box-shadow: -24px 0 60px -30px rgb(0 0 0 / .45); animation: slide .18s ease-out;
}
@keyframes slide { from { transform: translateX(24px); opacity: 0; } }
.phead {
  position: sticky; top: 0; z-index: 1; background: var(--sheet); display: flex; align-items: center; gap: 12px;
  padding: 18px 28px 14px; border-bottom: 1px solid var(--rule);
}
#ptitle:focus { outline: none; }
.phead h2 { border: 0; padding: 0; margin: 0; font-size: 17px; }
.phead .kind { color: var(--mute); font-size: 13px; }
.phead .kind.warn { color: var(--red); font-weight: 600; }
.phead .actions { margin-left: auto; display: flex; gap: 6px; }
.phead .actions button { font-size: 13px; color: var(--mute); padding: 5px 10px; border-radius: 6px; border: 1px solid var(--rule); }
.phead .actions button:hover { color: var(--ink); border-color: var(--faint); }
.pbody { padding: 22px 28px 48px; }
.full { font-size: 16px; line-height: 1.6; white-space: pre-wrap; overflow-wrap: anywhere; margin: 0 0 26px; max-width: 70ch; }
.facts { display: grid; grid-template-columns: max-content minmax(0, 1fr); gap: 7px 20px; margin: 0 0 30px; font-size: 13.5px; }
.facts dt { color: var(--mute); }
.facts dd { margin: 0; overflow-wrap: anywhere; }
.facts dd p { margin: 0 0 4px; }
.pbody h3 { font-size: 14px; font-weight: 600; font-stretch: 112%; margin: 0 0 4px; display: flex; gap: 10px; }
.pbody h3 span { color: var(--faint); font-weight: 400; font-stretch: 100%; }
.pbody .msgs { margin-bottom: 28px; }
.pbody .msg { cursor: auto; }
.pbody .msg .text { display: block; }
.note { color: var(--mute); font-size: 14px; margin: 6px 0 28px; }

/* Keys */
.keys {
  position: fixed; right: 24px; bottom: 24px; z-index: 4; background: var(--sheet); border: 1px solid var(--rule);
  border-radius: 10px; padding: 16px 20px 18px; box-shadow: 0 20px 50px -24px rgb(0 0 0 / .5); font-size: 13px;
}
.keys h2 { border: 0; padding: 0 0 10px; }
.keys dl { display: grid; grid-template-columns: max-content 1fr; gap: 8px 16px; margin: 0; align-items: center; }
.keys dt { display: flex; gap: 4px; }
.keys dd { margin: 0; color: var(--mute); }

@media (max-width: 1400px) { .ncom { display: none; } }
@media (max-width: 1100px) {
  .board { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); }
  .board .s-msgs, .rest .s-closed { grid-column: 1 / -1; margin-top: 40px; }
}
@media (max-width: 820px) {
  .wrap { padding: 16px 16px 48px; }
  .status { margin-left: auto; order: 1; }
  .links { order: 2; width: 100%; }
  .search { order: 3; margin-left: 0; width: 100%; }
  .search input { width: 100%; }
  .summary { font-size: 20px; }
  .hp-body { grid-template-columns: 1fr; gap: 12px; }
  .hp-stats { flex-direction: row; flex-wrap: wrap; gap: 8px 36px; }
  .hkey { display: grid; grid-template-columns: repeat(3, max-content); }  /* 3 + 2, no single item on a line */
  .wrap { display: flex; flex-direction: column; }
  .board.main-cols { display: contents; }
  .s-work { order: 2; margin-top: 30px; } .s-result { order: 3; margin-top: 40px; }
  .hill { order: 4; margin-top: 44px; } .s-msgs { order: 5; margin-top: 40px; }
  .activity { order: 6; } .rest { order: 7; display: block; }
  .rest section + section { margin-top: 40px; }
  .lane, .axis { grid-template-columns: 104px minmax(0, 1fr); }
  .legend { margin-left: 0; }
}
@media (prefers-reduced-motion: reduce) {
  .arrived, .panel, .scrim { animation: none; }
}
.arrived { animation: arrive 2.6s ease-out; }
@keyframes arrive { from { background-color: var(--blue-wash); } }
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <h1 class="name">Team board</h1>
    <nav class="links"><a href="/" aria-current="page">Board</a><a href="/architecture">Design</a><a href="/proof">Proof</a><a href="/findings">Findings</a></nav>
    <span class="test" id="test" hidden>test table</span>
    <label class="search"><input id="q" type="search" placeholder="Filter items and messages" aria-label="Filter items and messages" autocomplete="off"><kbd>/</kbd></label>
    <span class="status" id="status" role="status">Reading the board</span>
  </header>
  <div class="lede">
    <p class="since" id="since" hidden></p>
    <span class="sr" id="live" aria-live="polite"></span>
    <p class="summary" id="summary"><span class="ph" style="width:min(620px,80%);height:14px;margin-top:8px"></span></p>
    <div class="filters" id="filters"></div>
  </div>
  <div class="hill" id="hill" aria-label="Best untrained-base score per benchmark against RL">
    <section class="hp"><h2>&nbsp;</h2><div class="hp-body"><div class="ph-row" style="border:0"><span class="ph"></span><span class="ph"></span><span class="ph"></span></div><div class="hp-chart"></div></div></section>
    <section class="hp"><h2>&nbsp;</h2><div class="hp-body"><div class="ph-row" style="border:0"><span class="ph"></span><span class="ph"></span><span class="ph"></span></div><div class="hp-chart"></div></div></section>
  </div>
  <main class="board main-cols">
    <section class="s-work"><h2>Open work <span class="count" id="n-work"></span></h2><div id="work"></div><div id="work-more"></div></section>
    <section class="s-result"><h2>Results <span class="count" id="n-result"></span></h2><div id="result"></div><div id="result-more"></div></section>
    <section class="s-msgs"><h2>Messages on all <span class="count" id="n-msgs"></span><button class="toggle" id="autos" hidden></button></h2><ul class="msgs" id="msgs"></ul><div id="msgs-more"></div></section>
  </main>
  <section class="activity"><h2>Activity <span class="count" id="n-lanes"></span></h2><div class="lanes" id="lanes"></div>
    <div class="legend" aria-label="Key">
      <span><i class="mk res"></i>result</span><span><i class="mk res scored"></i>result with a score</span>
      <span><i class="mk claim"></i>work claim</span><span><i class="mk idea"></i>idea or note</span><span><i class="mk tick"></i>message</span>
    </div>
  </section>
  <div class="board rest">
    <section><h2>Ideas <span class="count" id="n-idea"></span></h2><div id="idea"></div><div id="idea-more"></div></section>
    <section><h2>Knowledge and skills <span class="count" id="n-knowledge"></span></h2><div id="knowledge"></div><div id="knowledge-more"></div></section>
    <section class="s-closed"><h2>Closed work <span class="count" id="n-closed"></span></h2><div id="closed"></div><div id="closed-more"></div></section>
  </div>
</div>
<div class="scrim" id="scrim" hidden></div>
<aside class="panel" id="panel" role="dialog" aria-labelledby="ptitle" hidden></aside>
<div class="keys" id="keys" role="dialog" aria-label="Keys" hidden>
  <h2>Keys</h2>
  <dl>
    <dt><kbd>/</kbd></dt><dd>Filter items and messages</dd>
    <dt><kbd>j</kbd><kbd>k</kbd></dt><dd>Next and previous: open work, results, messages, ideas</dd>
    <dt><kbd>1</kbd><kbd>2</kbd><kbd>3</kbd></dt><dd>Open work, results, messages</dd>
    <dt><kbd>Enter</kbd></dt><dd>Open the item, or the whole message</dd>
    <dt><kbd>Esc</kbd></dt><dd>Close</dd>
    <dt><kbd>?</kbd></dt><dd>These keys</dd>
  </dl>
</div>
<script>
const $ = id => document.getElementById(id);
const S = {
  lookedAt: 0, selAt: 0, changed: new Set(),
  data: null, readAt: 0, error: null, who: null, q: "", idle: false, open: null, detail: null, seen: null,
  autos: false, more: new Set(), full: new Set(), since: null, acked: true, pointer: null,
};
const HUES = [325, 150, 65, 195, 105, 45, 175, 350];  // far apart first; none in 230-310, where the data blue is
const KINDS = { work: "Open work", "work-closed": "Closed work", result: "Result", idea: "Idea", knowledge: "Knowledge", skill: "Skill" };
const LIMIT = { result: 12, msgs: 20, idea: 8, knowledge: 8, closed: 8 };
const ID = /\b((?:work|result|idea|knowledge|skill)-[0-9a-f]{6})\b|(?<![\w.-])(\d+(?:[.,]\d+)*(?: ?%)?)(?![\w-])/g;
const AUTO = /^(started|done|closed) (work|idea|result|knowledge|skill)-[0-9a-f]{6}\b/;  // what board.py announces by itself
const SEEN_KEY = "board.lastSeen";
const small = matchMedia("(max-width: 820px)");
let people = [];

const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const hue = name => HUES[Math.max(0, people.indexOf(name)) % HUES.length];  // by sorted name: the same colors on every page
const pstyle = name => `--h:${hue(name)};--pc-color:oklch(var(--pl) var(--pc) ${hue(name)})`;
const now = () => S.data ? S.data.now_ns + (Date.now() - S.readAt) * 1e6 : Date.now() * 1e6;
const mins = ns => Math.max(0, Math.floor((now() - Number(ns)) / 6e10));
const dur = m => m < 60 ? `${m}m` : m < 1440 ? `${Math.floor(m / 60)}h` : `${Math.floor(m / 1440)}d`;
const durHM = m => m < 60 ? `${m}m` : m < 1440 ? `${Math.floor(m / 60)}h ${m % 60}m` : `${Math.floor(m / 1440)}d ${Math.floor(m % 1440 / 60)}h`;
const rel = ns => mins(ns) < 1 ? "now" : dur(mins(ns));
const utc = ns => new Date(Number(ns) / 1e6).toISOString().slice(0, 19).replace("T", " ") + " UTC";
const clock = ms => new Date(ms).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false });
const when = (ns, suffix = "") => `<time title="${utc(ns)}">${rel(ns)}${mins(ns) >= 1 ? suffix : ""}</time>`;
const msgNs = m => Number(m.sk.slice(0, 20));
const activeNs = i => Number(i.active_ns ?? i.at_ns);
const plural = (n, word, many = word + "s") => `<b>${n}</b> ${n === 1 ? word : many}`;
const f1 = v => v.toFixed(1);
const store = {  // a private window throws on localStorage; the page works without it
  get(k) { try { return localStorage.getItem(k); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch {} },
};

/* Statistics: a 95% Wilson interval for one proportion, and the normal-approximation interval of the difference of two. */
function wilson(right, n, z = 1.96) {
  const p = right / n, d = 1 + z * z / n, mid = (p + z * z / (2 * n)) / d;
  const half = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d;
  return [100 * (mid - half), 100 * (mid + half)];
}
function diffCI(a, b, z = 1.96) {  // a minus b, in points, for two independent samples
  const pa = a.right / a.n, pb = b.right / b.n, se = Math.sqrt(pa * (1 - pa) / a.n + pb * (1 - pb) / b.n);
  return [100 * (pa - pb - z * se), 100 * (pa - pb + z * se)];
}

/* Writes that do not disturb reading: skip an unchanged string, skip while the reader has text selected in it. */
const selecting = el => {  // a selection younger than 60 s pauses writes to the region that holds it
  if (!S.selAt || Date.now() - S.selAt >= 60000) return false;  // no selection (selectionchange keeps S.selAt): skip getSelection
  const s = getSelection();
  return s && !s.isCollapsed && el.contains(s.anchorNode);
};
document.addEventListener("selectionchange", () => { S.selAt = getSelection().isCollapsed ? 0 : Date.now(); });
function put(el, html) {
  if (el._html === html || selecting(el)) return;
  el.innerHTML = html; el._html = html;
}
function node(html) { const t = document.createElement("template"); t.innerHTML = html; const n = t.content.firstElementChild; n._html = html; return n; }
function putRows(el, rows, empty) {  // rows: [key, html]; only changed rows are replaced, so hover and focus stay
  const html = rows.map(r => r[1]).join("") || empty;
  if (el._html === html || selecting(el)) return;
  const kids = [...el.children];
  if (rows.length && kids.length === rows.length && kids.every((k, i) => k.dataset.key === rows[i][0])) {
    rows.forEach(([, h], i) => { if (kids[i]._html !== h) kids[i].replaceWith(node(h)); });
  } else if (rows.length) {
    const old = new Map(kids.map(k => [k.dataset.key, k]));
    el.replaceChildren(...rows.map(([key, h]) => old.get(key)?._html === h ? old.get(key) : node(h)));
  } else el.innerHTML = empty;
  el._html = html;
}

/* Text from the board, escaped; item ids become links, and in results the numbers are set heavier. */
function rich(text, { links = true, numbers = false } = {}) {
  return esc(text).replace(ID, (all, id, num) =>
    id ? (links ? `<a class="ref" href="#${id}">${id}</a>` : id) : numbers ? `<span class="n">${num}</span>` : num);
}
const who = (name, branch) =>  // the branch only when it is not main
  `<button class="who" style="${pstyle(name)}" data-who="${esc(name)}" title="Show only ${esc(name)}">${esc(name)}</button>` +
  (branch && branch !== "main" ? `<span class="branch" title="${esc(branch)}">${esc(branch)}</span>` : "");
const match = (...fields) => (!S.q || fields.join("\n").toLowerCase().includes(S.q));
const shown = i => (!S.who || i.who === S.who) && match(i.id, i.text, i.who, i.branch);
const filtering = () => Boolean(S.q || S.who || S.idle);
const isNew = key => S.seen && !S.seen.has(key);
/* What changed since the last look: new results, closed work, work that crossed an hour idle. The dots and the count use this. */
function changed(items) {
  const since = S.since, t = now();
  if (!since) return { result: [], closed: [], idle: [] };
  return {
    result: items.filter(i => i.kind === "result" && i.at_ns > since),
    closed: items.filter(i => i.closed_ns > since),
    idle: items.filter(i => i.listed === "work" && activeNs(i) + 36e11 > since && activeNs(i) + 36e11 <= t),
  };
}

const MODELS = { base: 0, rl: 1 };
function scoreChips(id) {
  const all = (S.scores.get(id) || []).slice().sort((a, b) => (MODELS[a.model] ?? 2) - (MODELS[b.model] ?? 2) || b.right / b.n - a.right / a.n);
  const seen = new Set(), top = all.filter(s => !seen.has(s.model + s.benchmark) && seen.add(s.model + s.benchmark)).slice(0, 2);
  return !top.length ? "" : `<div class="scores">` + top.map(s => `<span class="score">${esc(s.model)} ${esc(s.benchmark)} <b>${s.right}/${s.n}</b></span>`).join("") +
    (all.length > top.length ? `<span>${all.length - top.length} more</span>` : "") + `</div>`;
}

function row(i) {
  const open = i.listed === "work", closed = i.listed === "work-closed";
  const idle = open ? mins(activeNs(i)) : 0, late = idle >= 60;
  const t = open ? activeNs(i) : i.at_ns, fresh = mins(t) < 10;
  const last = open && late && S.data.last_comments?.[i.id];
  const cls = ["row", i.kind, late && "late", closed && "closed", S.open === i.id && "current", isNew(i.id) && "arrived", S.changed.has(i.id) && "new"];
  const meta = [
    who(i.who, i.branch),
    `<span class="id">${esc(i.id)}</span>`,
    closed ? `<span>closed ${when(i.closed_ns ?? 0, " ago")}${i.closed_by ? " by " + esc(i.closed_by.split("/")[0]) : ""}</span>`
           : open ? "" : `<span${fresh ? ' class="fresh"' : ""}>${when(t, " ago")}</span>`,
    i.kind === "skill" ? "<span>skill</span>" : "",
    i.ups || i.downs ? `<span>+${i.ups} −${i.downs}</span>` : "",
    i.n_comments ? `<span class="ncom">${i.n_comments} comment${i.n_comments > 1 ? "s" : ""}</span>` : "",
  ].join("");
  const right = open ? `<span class="idle" title="Minutes since the item was posted or last commented on">idle ${dur(idle)}` +
    `<span class="meter"><i style="width:${Math.min(100, idle / 60 * 100)}%"></i></span></span>` : "";
  return `<article class="${cls.filter(Boolean).join(" ")}" style="${pstyle(i.who)}" data-key="${esc(i.id)}">` +
    `<a class="open" href="#${esc(i.id)}"><span class="text">${rich(i.text, { links: false, numbers: i.kind === "result" })}</span></a>` +
    (last ? `<p class="last">Last comment: ${esc(last.text)}</p>` : "") + (i.kind === "result" ? scoreChips(i.id) : "") +
    `<div class="meta"><div class="m">${meta}</div>${right}</div></article>`;
}

function message(m) {
  const cls = ["msg", isNew(m.sk) && "arrived", S.full.has(m.sk) && "full"];
  return `<li class="${cls.filter(Boolean).join(" ")}" data-key="${esc(m.sk)}" tabindex="-1"><div class="meta">${who(m.who, m.branch)}${when(msgNs(m), " ago")}</div>` +
    `<div class="text">${rich(m.text)}</div></li>`;
}

function list(id, items, total, empty, draw = row) {
  const cut = filtering() || S.more.has(id) || !LIMIT[id] ? items : items.slice(0, LIMIT[id]);
  putRows($(id), cut.map(i => [i.id ?? i.sk, draw(i)]), `<p class="empty">${empty}</p>`);
  put($(id + "-more"), cut.length < items.length ? `<button class="more" data-more="${id}">Show all ${items.length}</button>` : "");
  put($("n-" + id), filtering() ? `${items.length} of ${total}` : String(total));
}

function render() {
  const d = S.data;
  const anchor = readingAnchor(), before = anchor?.getBoundingClientRect().top;
  const focused = document.activeElement?.closest("[data-key]")?.dataset.key;
  status();
  put($("filters"), (S.who ? `<span class="chip">Showing ${esc(S.who)} only <button data-clear="who" aria-label="Show everyone">✕</button></span>` : "") +
    (S.idle ? `<span class="chip">Open work idle over an hour <button data-clear="idle" aria-label="Show all open work">✕</button></span>` : ""));
  if (!d) return;
  $("test").hidden = !d.test;

  people = [...new Set([...d.items, ...d.messages].map(r => r.who))].sort();
  S.scores = new Map();
  (d.scores || []).forEach(s => S.scores.set(s.result, [...(S.scores.get(s.result) || []), s]));
  const items = d.items.map(i => ({ ...i, closed_ns: i.closed_at ? Date.parse(i.closed_at) * 1e6 : null }));
  if (document.visibilityState === "visible" && document.hasFocus()) S.lookedAt = d.now_ns;  // the reader saw this read
  const ch = changed(items);
  S.changed = new Set([...ch.result, ...ch.closed, ...ch.idle].map(i => i.id));
  const of = kinds => items.filter(i => kinds.includes(i.listed));
  const by = (kinds, order) => { const all = of(kinds).sort(order); return [all.filter(shown), all.length]; };
  const newest = (a, b) => b.at_ns - a.at_ns;
  const [work, nWork] = by(["work"], (a, b) => activeNs(a) - activeNs(b));  // longest idle first; a row crossing an hour does not move
  const workShown = S.idle ? work.filter(i => mins(activeNs(i)) >= 60) : work;
  const [results, nResults] = by(["result"], newest);
  const [ideas, nIdeas] = by(["idea"], newest);
  const [notes, nNotes] = by(["knowledge", "skill"], newest);
  const [closed, nClosed] = by(["work-closed"], (a, b) => (b.closed_ns ?? 0) - (a.closed_ns ?? 0));
  const talk = d.messages.filter(m => (!S.who || m.who === S.who) && match(m.text, m.who, m.branch)).reverse();
  const autos = talk.filter(m => AUTO.test(m.text)).length;
  const msgs = S.autos ? talk : talk.filter(m => !AUTO.test(m.text));
  const none = filtering() ? "Nothing matches the filter." : "";

  list("work", workShown, nWork, none || "No open work. An agent claims work with <code>board.py post work</code>.");
  list("result", results, nResults, none || "No results yet.");
  list("idea", ideas, nIdeas, none || "No ideas yet.");
  list("knowledge", notes, nNotes, none || "No knowledge or skills yet.");
  list("closed", closed, nClosed, none || "No work has been closed yet.");
  list("msgs", msgs, d.messages.length - (S.autos ? 0 : d.messages.filter(m => AUTO.test(m.text)).length),
    none || `No messages on all in the last ${d.hours} h.`, message);
  $("autos").hidden = !autos;
  put($("autos"), S.autos ? "Hide announcements" : `Show ${autos} announcement${autos > 1 ? "s" : ""}`);
  $("autos").setAttribute("aria-pressed", S.autos);

  summary(items, ch);
  hill(d.scores || []);
  lanes(items, d);
  S.seen = new Set([...d.items.map(i => i.id), ...d.messages.map(m => m.sk)]);
  if (focused && !document.activeElement?.closest("[data-key]")) document.querySelector(`[data-key="${CSS.escape(focused)}"] .open, .msg[data-key="${CSS.escape(focused)}"]`)?.focus({ preventScroll: true });
  const after = anchor?.isConnected ? anchor : anchor && document.querySelector(`[data-key="${CSS.escape(anchor.dataset.key)}"]`);
  if (after && scrollY > 0) scrollBy(0, after.getBoundingClientRect().top - before);  // rows added above the reader do not push the text
}

/* The row being read: the focused one, else the one under the pointer, else the one at the middle of the screen. */
function readingAnchor() {
  const f = document.activeElement?.closest?.(".board [data-key]");
  if (f) return f;
  const p = S.pointer ?? { x: innerWidth / 2, y: innerHeight / 2 };
  return document.elementFromPoint(p.x, p.y)?.closest(".board [data-key]") ?? null;
}

function status() {
  const s = $("status"), d = S.data;
  s.className = "status" + (S.error ? " bad" : d ? " live" : "");
  s.textContent = S.error ? (d ? `Offline, last read ${clock(S.readAt)}` : "Offline, not read yet") : d ? "Live" : "Reading the board";
  s.title = d ? `Last read ${utc(d.now_ns)}` : "";
}

function summary(items, ch) {
  const open = items.filter(i => i.listed === "work");
  const idle = open.filter(i => mins(activeNs(i)) >= 60).length;
  const ppl = new Set(open.map(i => i.who)).size;
  const last = items.filter(i => i.kind === "result").sort((a, b) => b.at_ns - a.at_ns)[0];
  put($("summary"), (open.length
      ? `${plural(open.length, "open work item")} from ${plural(ppl, "person", "people")}, ` +
        (idle ? `<button class="warn" id="idlebtn" aria-pressed="${S.idle}" title="Show only open work idle over an hour"><b>${idle}</b> idle over an hour</button>.` : "none idle over an hour.")
      : "No open work.") +
    (last ? ` <a href="#${esc(last.id)}">Last result ${mins(last.at_ns) < 1 ? "just now" : `<b>${rel(last.at_ns)}</b> ago`}</a> from ${esc(last.who)}.` : " No results yet."));
  put($("live"), `${open.length} open work items, ${idle} idle over an hour, ${items.filter(i => i.kind === "result").length} results.`);  // changes only with the counts
  if (!S.since) { $("since").hidden = true; document.title = "Team board"; return; }
  const since = S.since;
  const parts = [[ch.result.length, "result"], [ch.closed.length, "closed", "closed"], [ch.idle.length, "newly idle", "newly idle"]].filter(p => p[0]);
  const count = parts.reduce((a, p) => a + p[0], 0);
  $("since").hidden = false;
  put($("since"), `<span>${count ? `Since ${clock(since / 1e6)}: ${parts.map(p => plural(...p)).join(", ")}.` : `Nothing new since ${clock(since / 1e6)}.`}</span>`);
  document.title = count && !S.acked ? `(${count}) Team board` : "Team board";
}

/* Hill chart */
const note = /\s*\(.*?\)/g;  // a parenthesised note on a configuration, such as "(reference, job 151534-e72c)"
const shortConfig = (c, max = 30) => {
  const s = c.replace(/,?\s*\bT \d[\d.]*(\s*\/\s*(top-p|min-p) [\d.]+)*/g, "").replace(note, "").replace(/^,\s*/, "") || c;  // sampling settings and notes are in the full text
  return s.length > max ? s.slice(0, max - 1).trimEnd() + "…" : s;
};
let measure;
function textWidth(t) {
  measure ??= document.createElement("canvas").getContext("2d");
  measure.font = '400 11px "Archivo", ui-sans-serif, system-ui, sans-serif';
  return measure.measureText(t).width;
}

function benches(scores) {
  const pct = s => 100 * s.right / s.n;
  const names = [...new Set(scores.map(s => s.benchmark))].sort((a, b) => (b === "MATH-500") - (a === "MATH-500") || a.localeCompare(b));
  const bs = names.map(name => {
    const seen = new Set();  // a run reported in two results, or again with a note, is one attempt
    const base = scores.filter(s => s.benchmark === name && s.model === "base")
      .filter(s => { const k = `${s.right}/${s.n} ${s.config.replace(note, "")}`; return !seen.has(k) && seen.add(k); });
    if (!base.length) return null;
    const rl = scores.filter(s => s.benchmark === name && s.model === "rl").sort((a, b) => pct(b) - pct(a))[0];
    let lead = null;
    const pts = base.map((s, i) => {
      const q = { s, i, p: pct(s), ci: wilson(s.right, s.n), plain: /^plain\b/.test(s.config) };
      if (!lead || q.p > lead.p) { if (lead) { q.prev = lead; q.clears = q.p > lead.ci[1]; } q.rec = true; lead = q; }
      return q;
    });
    const plains = pts.filter(q => q.plain).map(q => q.p), vals = pts.map(q => q.p).concat(rl ? [pct(rl)] : []);
    const lo = Math.max(0, plains.length ? Math.round((Math.max(...plains) - 5) / 10) * 10 : Math.floor((Math.min(...vals) - 4) / 10) * 10);
    return { name, pts, lead, rl, rlP: rl && pct(rl), lo, hi: Math.min(100, Math.ceil((Math.max(...vals) + 2) / 10) * 10) };
  }).filter(Boolean);
  const span = Math.max(...bs.map(b => b.hi - b.lo));  // every chart spans the same points, so heights compare
  bs.forEach(b => { b.hi = Math.min(100, b.lo + span); b.lo = b.hi - span; });
  return bs;
}

const KEY = `<div class="hp hkey" aria-label="Key to the charts">` +
  `<span><svg width="12" height="12"><circle class="dot rec" cx="6" cy="6" r="4.5"/></svg>new best</span>` +
  `<span><svg width="12" height="12"><circle class="dot" cx="6" cy="6" r="3.5"/></svg>other attempt</span>` +
  `<span><svg width="12" height="12"><path class="x" d="M2.5,2.5l7,7m0,-7l-7,7"/></svg>plain prompt</span>` +
  `<span><svg width="12" height="12"><line class="ci" x1="6" x2="6" y1="0" y2="12" style="opacity:1"/></svg>95% interval</span>` +
  `<span><svg width="14" height="10"><rect class="gap" width="14" height="10"/></svg>gap to RL</span></div>`;

function hill(scores) {
  const bs = benches(scores);
  S.benches = bs;
  put($("hill"), bs.map(b => {
    const { lead, rl, rlP, pts } = b, after = pts.length - 1 - lead.i;
    const gap = rl ? rlP - lead.p : null, ci = rl && diffCI(rl, lead.s);
    return `<section class="hp"><h2>${esc(b.name)} <span class="count">untrained base against RL, n ${lead.s.n}</span></h2><div class="hp-body"><div class="hp-stats">` +
      `<div><a class="big num" href="#${esc(lead.s.result)}" title="${esc(lead.s.config)}">${f1(lead.p)}<small>%</small></a>` +
      `<p class="num">best base, ${lead.s.right}/${lead.s.n}</p><p class="cfg">${esc(lead.s.config)}</p>` +
      `<p class="num">last record ${durHM(mins(Number(lead.s.sk.slice(0, 20))))} ago, ${after ? `${after} attempt${after > 1 ? "s" : ""}` : "no attempts"} since</p></div>` +
      (rl ? `<div><p class="togo">${gap > 0 ? `<b class="num">${f1(gap)}</b> points below RL` : "<b>0</b> points below RL"}</p>` +
            `<p class="num">95% interval ${f1(ci[0])} to ${f1(ci[1])}</p><p>RL: ${esc(shortConfig(rl.config, 60))}</p></div>`
          : `<div><p>RL not measured on ${esc(b.name)}</p></div>`) +
      `</div><div class="hp-chart" data-bench="${esc(b.name)}"></div></div>${steps(b)}</section>`;
  }).join("") + (bs.length ? KEY : "") || `<p class="empty">No scores yet. Attach one to a result: <code>board.py score &lt;result id&gt; base MATH-500 410/500 "cue, T 1.0"</code></p>`);
  charts();
}

function steps(b) {  // the chart's record steps (q.rec, as in chart), newest first, each with the first line of its finding
  return `<div class="steps">` + b.pts.filter(q => q.rec).reverse().map(q => {
    const fin = S.data.finding[q.s.result] ?? "", noise = q.prev && !q.clears;
    return `<a href="#${esc(q.s.result)}"${noise ? ' class="noise"' : ""}><b class="num">${q.prev ? "+" + f1(q.p - q.prev.p) : "first"}</b>` +
      `<span class="fin" title="${esc(fin)}">${esc(fin)}</span><span class="num" title="${esc(q.s.config)}">` +
      `${q.prev ? f1(q.prev.p) + " → " : ""}${f1(q.p)} %${noise ? ", within noise" : ""}, ${esc(q.s.config)}</span></a>`;
  }).join("") + `</div>`;
}

function charts() {
  document.querySelectorAll(".hp-chart[data-bench]").forEach(el => {
    const b = S.benches.find(x => x.name === el.dataset.bench);
    if (b && el.clientWidth) put(el, chart(b, el.clientWidth, small.matches));
  });
}

function chart(b, W, narrow) {
  const { pts, lead, rl, rlP } = b;
  const { lo, hi } = b, H = 184, T = 18, B = 24, L = narrow ? 26 : 30, R = 60;
  const y = v => T + (hi - Math.max(lo, Math.min(hi, v))) / (hi - lo) * (H - T - B);
  const x = i => L + (i + .5) / pts.length * (W - L - R);
  const out = [], boxes = [];
  const inside = bx => bx.x0 >= L - 4 && bx.x1 <= W && bx.y0 >= 0;
  const hits = bx => boxes.filter(o => bx.x0 < o.x1 && bx.x1 > o.x0 && bx.y0 < o.y1 && bx.y1 > o.y0).length;
  const label = (text, cls, spots, force) => {  // the first spot that overlaps nothing; spots are [x, y, anchor]
    const w = textWidth(text);
    const box = ([sx, sy, a]) => { const x0 = a === "end" ? sx - w : a === "middle" ? sx - w / 2 : sx; return { x0: x0 - 2, x1: x0 + w + 2, y0: sy - 11, y1: sy + 5 }; };  // with the halo
    let at = spots.find(s => inside(box(s)) && !hits(box(s)));
    if (!at && force) at = spots.filter(s => inside(box(s))).sort((a, b) => hits(box(a)) - hits(box(b)))[0] ?? spots[0];  // the spot that overlaps least
    if (!at) return;
    boxes.push(box(at));
    out.push(`<text class="${cls}" x="${at[0].toFixed(1)}" y="${at[1].toFixed(1)}" text-anchor="${at[2]}">${esc(text)}</text>`);
  };

  const svg = [];
  for (let v = lo; v <= hi; v += 10) {
    svg.push(`<line class="grid" x1="${L}" x2="${W - R}" y1="${y(v)}" y2="${y(v)}"/>`);
    svg.push(`<text x="${L - 8}" y="${y(v) + 4}" text-anchor="end">${v}</text>`);
  }
  svg.push(`<text x="${L - 8}" y="${T - 9}" text-anchor="end">%</text>`);

  const recs = pts.filter(q => q.rec), shown = recs.filter(q => q.p >= lo);  // a best below the floor has no tread
  const first = shown[0], start = first.prev ? x(first.i) : L;
  const step = [[start, y(first.p)]];
  shown.forEach((q, k) => { if (k) step.push([x(q.i), y(q.prev.p)], [x(q.i), y(q.p)]); });
  step.push([W - R, y(lead.p)]);
  if (rl) {
    const top = y(rlP), poly = [[start, top], [W - R, top], ...step.slice().reverse().map(([px, py]) => [px, Math.max(py, top)])];
    svg.push(`<path class="gap" d="M${poly.map(p => p.map(n => n.toFixed(1)).join(",")).join("L")}Z"/>`);
    svg.push(`<line class="target" x1="${L}" x2="${W - R}" y1="${top}" y2="${top}"/>`);
    boxes.push({ x0: W - R + 4, x1: W, y0: top - 9, y1: top + 5 }, { x0: L, x1: W - R, y0: top - 1.5, y1: top + 1.5 });
    svg.push(`<a href="#${esc(rl.result)}"><title>${esc(`RL, ${rl.config}: ${rl.right}/${rl.n}, ${rl.result}`)}</title>` +
      `<text class="rl" x="${W - R + 8}" y="${top + 4}">RL <tspan>${f1(rlP)}</tspan></text></a>`);
  }
  recs.forEach((q, k) => {
    const x1 = k ? x(q.i) : L, x2 = recs[k + 1] ? x(recs[k + 1].i) : W - R;
    if (q.p >= lo) {
      svg.push(`<line class="tread" x1="${x1}" x2="${x2}" y1="${y(q.p)}" y2="${y(q.p)}"/>`);
      boxes.push({ x0: x1, x1: x2, y0: y(q.p) - 2, y1: y(q.p) + 2 });
    }
    if (!k) return;
    boxes.push({ x0: x(q.i) - 2, x1: x(q.i) + 2, y0: y(q.p), y1: y(q.prev.p) });
    svg.push(`<line class="rise${q.clears ? "" : " noise"}" x1="${x(q.i)}" x2="${x(q.i)}" y1="${y(q.prev.p)}" y2="${y(q.p)}"/>`);
    if (q.prev.p < lo) {  // the rise starts below the floor: an axis break where it leaves the chart
      const bx = x(q.i), by = y(lo) - 6;
      svg.push(`<path class="brk" d="M${bx - 5},${by + 2}l10,-4"/><path class="brk-line" d="M${bx - 5},${by}l10,-4M${bx - 5},${by + 4}l10,-4"/>`);
    }
  });

  const marks = pts.map(q => {
    const cx = x(q.i), cy = y(q.p), clipped = q.p < lo;
    boxes.push({ x0: cx - 7, x1: cx + 7, y0: cy - 7, y1: cy + 7 });
    if (!clipped) boxes.push({ x0: cx - 1.5, x1: cx + 1.5, y0: y(q.ci[1]), y1: y(q.ci[0]) });
    const ci = clipped ? "" : `<line class="ci${q.rec ? " rec" : ""}" x1="${cx}" x2="${cx}" y1="${y(q.ci[1])}" y2="${y(q.ci[0])}"/>`;
    const tip = `${q.s.config}: ${q.s.right}/${q.s.n} (${f1(q.p)} %, 95% ${f1(q.ci[0])} to ${f1(q.ci[1])})` +
      `${q.s.tokens ? `, ${Number(q.s.tokens).toLocaleString("en-US")} tokens per problem` : ""}, ${q.s.who}, ${q.s.result}`;
    const x7 = `<circle class="under" cx="${cx}" cy="${cy}" r="4.5"/><path class="x" d="M${cx - 3.5},${cy - 3.5}l7,7m0,-7l-7,7"`;
    const mark = q.plain && !q.rec ? `${x7}/>` : q.plain ? `${x7} style="stroke:var(--blue)"/>`
      : `<circle class="dot${q.rec ? " rec" : ""}" cx="${cx}" cy="${cy}" r="${q.rec ? 4.5 : 3.5}"/>`;
    return { ci, a: `<a href="#${esc(q.s.result)}" aria-label="${esc(tip)}"><title>${esc(tip)}</title><circle class="hit" cx="${cx}" cy="${cy}" r="9"/>${mark}</a>` };
  });

  const caption = `${pts.length} attempts in the order posted`;
  boxes.push({ x0: W - R - textWidth(caption), x1: W - R, y0: H - 14, y1: H });
  out.push(`<text class="quiet" x="${W - R}" y="${H - 4}" text-anchor="end">${caption}</text>`);
  recs.forEach(q => {  // a new record: its gain and short configuration, or "within noise" when it does not clear the last record's interval
    if (!q.prev || !q.clears) return;
    const xr = x(q.i), mid = (y(q.prev.p) + y(q.p)) / 2 + 4, text = `+${f1(q.p - q.prev.p)} ${shortConfig(q.s.config)}`;
    const spots = [0, -14, 14, -28, 28].flatMap(dy => [[xr + 8, mid + dy, "start"], [xr - 8, mid + dy, "end"]]);
    label(text, "gain", [...spots, [xr + 8, y(q.p) - 10, "start"], [xr - 8, y(q.p) - 10, "end"], [xr + 8, y(q.p) + 18, "start"]], true);
  });
  pts.filter(q => q.p < lo).forEach(q =>  // below the floor: say its value
    label(`↓ ${f1(q.p)}`, "quiet", [[x(q.i), y(q.p) + 20, "middle"], [x(q.i) - 5, y(q.p) + 20, "start"], [x(q.i) + 12, y(q.p) + 4, "start"]], true));
  if (!narrow) {
    recs.filter(q => q.prev && !q.clears).forEach(q =>
      label("within noise", "quiet", [[x(q.i) + 8, y(q.p) - 8, "start"], [x(q.i) - 8, y(q.p) - 8, "end"], [x(q.i) + 8, y(q.p) + 16, "start"]]));
    if (pts.length <= 12) pts.filter(q => !q.rec).forEach(q =>
      label(shortConfig(q.s.config), "quiet", [[x(q.i), y(q.p) + 20, "middle"], [x(q.i), y(q.p) - 12, "middle"], [x(q.i) + 12, y(q.p) + 4, "start"], [x(q.i) - 12, y(q.p) + 4, "end"]]));
  }

  return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(b.name)}: best base ${f1(lead.p)} %, RL ${rl ? f1(rlP) + " %" : "not measured"}">` +
    svg.join("") + marks.map(m => m.ci).join("") + marks.map(m => m.a).join("") + out.join("") + `</svg>`;
}

/* Activity lanes */
function lanes(items, d) {
  const hours = small.matches ? Math.min(2, d.hours) : d.hours;
  const span = hours * 3600e9, start = now() - span;
  const x = ns => ((Number(ns) - start) / span * 100).toFixed(3) + "%";
  const events = [
    ...items.filter(i => i.at_ns >= start).map(i => ({ who: i.who, ns: i.at_ns, item: i })),
    ...d.messages.filter(m => msgNs(m) >= start).map(m => ({ who: m.who, ns: msgNs(m), msg: m })),
  ];
  const lanePeople = [...new Set(events.map(e => e.who))].sort();
  put($("n-lanes"), `last ${hours} h`);
  put($("lanes"), lanePeople.map(p => {
    const marks = events.filter(e => e.who === p).map(e => {
      if (e.msg) return `<span class="mk tick" style="left:${x(e.ns)}"></span>`;
      const i = e.item, k = i.kind === "result" ? "res" : i.kind === "work" ? "claim" : "idea";
      return `<a class="mk ${k}${k === "res" && S.scores.has(i.id) ? " scored" : ""}" style="left:${x(e.ns)}" href="#${esc(i.id)}" tabindex="-1" ` +
        `title="${esc(i.id)}, ${rel(e.ns)} ago: ${esc(i.text.slice(0, 140))}"></a>`;
    }).join("");
    const cls = S.who ? (S.who === p ? "on" : "off") : "";
    return `<div class="lane ${cls}" style="${pstyle(p)}"><button data-who="${esc(p)}" title="Show only ${esc(p)}">${esc(p)}</button>` +
      `<div class="track" style="--hour:calc(100% / ${hours})">${marks}</div></div>`;
  }).join("") + (lanePeople.length ? `<div class="axis"><i></i><div>${
    Array.from({ length: Math.floor(hours) + 1 }, (_, h) => `<span style="left:${(100 - h / hours * 100).toFixed(3)}%">${h ? h + "h ago" : "now"}</span>`)
      .reverse().join("")}</div></div>` : `<p class="empty">No posts or messages in the last ${hours} h.</p>`));
}

/* Reading /data */
async function get(path) {
  const r = await fetch(path).catch(() => { throw { server: true }; });
  if (r.status === 404) return null;
  if (!r.ok) throw { text: `${r.status}: ${await r.text()}` };
  return r.json();
}

function failed(e) {
  S.error = e;
  console.error(e.server ? "The view server does not answer. Start it again with: uv run tools/view.py. The page tries again every 10 s."
    : "The server cannot read the board table. Check that the AWS profile iterate-ecr exists on this machine (README, Setup step 2), " +
      "that the key has not expired, and that the network is up. The terminal running view.py has the full traceback.", e.text ?? e);
}

async function read() {  // an unchanged board comes back as a 304 with the same ETag: nothing to parse
  const r = await fetch("/data").catch(() => { throw { server: true }; });
  if (!r.ok) throw { text: `${r.status}: ${await r.text()}` };
  const tag = r.headers.get("ETag");
  if (!S.data || tag !== S.etag) { S.data = await r.json(); S.etag = tag; }
  S.data.now_ns = Number(r.headers.get("X-Snapshot-Ns"));  // the time of the read, kept out of the body so the ETag holds
  S.readAt = Date.now(); S.error = null;
}

let timer = 0, reading = false;
function poll() {  // every 10 s while the tab is visible; a hidden tab stops, and reads at once when it is shown again
  clearTimeout(timer);
  if (reading) return;
  reading = true;
  read()
    .then(() => S.open && loadDetail())
    .catch(failed)
    .finally(() => { reading = false; render(); renderPanel(); if (!document.hidden) timer = setTimeout(poll, 10000); });
}

async function loadDetail() {  // a failed read of one item is logged; the rest of the page stays live
  const id = S.open;
  const found = await get("/data/" + encodeURIComponent(id)).catch(e => { console.error(`Reading ${id} failed:`, e.text ?? e); return undefined; });
  if (found !== undefined && S.open === id) S.detail = found ?? { missing: id };
}

/* Item panel */
function renderPanel() {
  const panel = $("panel");
  $("scrim").hidden = !S.open;
  if (!S.open) { panel.hidden = true; put(panel, ""); return; }
  const base = S.detail?.item ?? S.data?.items.find(i => i.id === S.open);
  let html;
  if (S.detail?.missing) {
    html = head(S.open, "") + `<div class="pbody"><p class="note">No item named ${esc(S.open)} on this board. ` +
      `The link may be mistyped, or the item is on the test table.</p></div>`;
  } else if (!base) {
    html = head(S.open, "") + `<div class="pbody"><p class="note">Reading ${esc(S.open)}</p></div>`;
  } else {
    const i = base, d = S.detail;
    const open = i.listed === "work", idle = mins(activeNs(i));
    const state = open ? `${KINDS.work}, ${idle ? "idle " + dur(idle) : "active now"}` :
      i.listed === "work-closed" ? `Closed by ${esc(i.closed_by)} ${when(Date.parse(i.closed_at) * 1e6, " ago")}` : KINDS[i.kind];
    const votes = d ? d.votes.map(v => `${esc(v.who)} ${v.vote > 0 ? "+" : "−"}`).join(", ") : "";
    const scores = (S.scores?.get(i.id) || []).map(s => `<p><span class="score">${esc(s.model)} ${esc(s.benchmark)} <b>${s.right}/${s.n}</b></span>, ` +
      `${f1(100 * s.right / s.n)} %, ${esc(s.config)}${s.tokens ? `, ${Number(s.tokens).toLocaleString("en-US")} tokens per problem` : ""}</p>`).join("");
    const facts = [
      ...(scores ? [["Scores", scores]] : []),
      ["Posted by", who(i.who)], ["Branch", esc(i.branch || "not recorded")],
      ["Agent", esc([i.agent, (i.session || "").slice(0, 8)].filter(Boolean).join(", ") || "not recorded")],
      ["Posted", `${when(i.at_ns, " ago")}, ${utc(i.at_ns)}`],
      ["Votes", `+${i.ups} −${i.downs}${votes ? ": " + votes : ""}`],
    ].map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("");
    const thread = (title, rows, empty) => `<h3>${title} <span>${d ? rows.length : ""}</span></h3>` + (!d ? `<p class="note">Reading</p>` :
      rows.length ? `<ul class="msgs">${rows.map(r => `<li class="msg"><div class="meta">${who(r.who, r.branch)}` +
        `${when(Date.parse(r.at) * 1e6, " ago")}</div><div class="text">${rich(r.text)}</div></li>`).join("")}</ul>` : `<p class="note">${empty}</p>`);
    html = head(i.id, state, open && idle >= 60) +
      `<div class="pbody"><p class="full">${rich(i.text, { numbers: i.kind === "result" })}</p><dl class="facts num">${facts}</dl>` +
      thread("Comments", d?.comments ?? [], "No comments.") +
      thread("Messages on this item", d?.thread ?? [], `No messages sent to ${esc(i.id)}.`) + "</div>";
  }
  panel.hidden = false;
  if (panel._html === html || selecting(panel)) return;
  const scroll = panel.scrollTop, focused = panel.contains(document.activeElement) && document.activeElement.id;
  put(panel, html);
  panel.scrollTop = scroll;
  if (focused) $(focused)?.focus({ preventScroll: true });
}

const head = (id, state, warn) => `<div class="phead"><h2 id="ptitle" tabindex="-1">${esc(id)}</h2>` +
  `<span class="kind${warn ? " warn" : ""}">${state}</span><div class="actions">` +
  `<button id="copy">Copy link</button><button id="close" title="Esc">Close</button></div></div>`;

function fromHash() {
  const id = decodeURIComponent(location.hash.slice(1)) || null;
  if (id === S.open) return;
  const was = S.open;
  S.open = id; S.detail = null;
  document.querySelectorAll(".row.current").forEach(r => r.classList.remove("current"));
  if (id) document.querySelector(`.row[data-key="${CSS.escape(id)}"]`)?.classList.add("current");
  renderPanel();
  if (!id) { if (was) document.querySelector(`[data-key="${CSS.escape(was)}"] .open`)?.focus({ preventScroll: true }); return; }
  if (!was) $("ptitle").focus({ preventScroll: true });  // opened from the board: focus moves into the panel
  loadDetail().then(renderPanel);
}

function closePanel() { history.pushState(null, "", location.pathname + location.search); fromHash(); }

/* Filters live in the address, beside the open item: /?who=frustea&q=cue#result-8b1c48 */
function syncURL() {
  const p = new URLSearchParams();
  if (S.who) p.set("who", S.who);
  if ($("q").value.trim()) p.set("q", $("q").value.trim());
  if (S.idle) p.set("idle", "1");
  const qs = p.toString();
  history.replaceState(null, "", location.pathname + (qs ? "?" + qs : "") + location.hash);
}
function filter(change) { Object.assign(S, change); syncURL(); render(); }

/* Keys: j and k walk open work, results, ideas, messages; 1 2 3 jump to a column */
const walk = () => [...$("work").querySelectorAll(".open"), ...$("result").querySelectorAll(".open"), ...$("msgs").querySelectorAll(".msg"), ...$("idea").querySelectorAll(".open")];
function move(step) {
  const links = walk();
  if (!links.length) return;
  const from = document.activeElement.closest("#panel") ? document.querySelector(`[data-key="${CSS.escape(S.open)}"] .open`) : document.activeElement;
  const at = links.indexOf(from);
  go(links[at < 0 ? (step > 0 ? 0 : links.length - 1) : Math.max(0, Math.min(links.length - 1, at + step))]);
}
function go(el) {
  if (!el) return;
  el.focus({ preventScroll: true });
  el.scrollIntoView({ block: "nearest" });
  if (S.open && el.classList.contains("open")) location.replace("#" + el.closest("[data-key]").dataset.key);
}

document.addEventListener("click", e => {
  const t = e.target;
  const person = t.closest("[data-who]");
  if (person) return filter({ who: S.who === person.dataset.who ? null : person.dataset.who });
  if (t.closest("#idlebtn")) return filter({ idle: !S.idle });
  const clear = t.closest("[data-clear]");
  if (clear) return filter({ [clear.dataset.clear]: clear.dataset.clear === "who" ? null : false });
  const more = t.closest("[data-more]");
  if (more) { S.more.add(more.dataset.more); render(); return; }
  if (t.closest("#autos")) { S.autos = !S.autos; render(); return; }
  if (t.closest("#close") || t.closest("#scrim")) { closePanel(); return; }
  if (t.closest("#copy")) {
    navigator.clipboard.writeText(location.href).then(() => { $("copy").textContent = "Copied"; });
    return;
  }
  const m = t.closest("#msgs .msg");
  if (m && !t.closest("a, button") && getSelection().isCollapsed) { toggleFull(m); return; }
  const r = t.closest(".row");
  if (r && !t.closest("a")) location.hash = r.dataset.key;
});
function toggleFull(m) {
  const k = m.dataset.key;
  S.full.has(k) ? S.full.delete(k) : S.full.add(k);
  render();
}
document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.target === $("q")) {
    if (e.key === "Escape") { $("q").value = ""; filter({ q: "" }); $("q").blur(); }
    if (e.key === "Enter" || e.key === "ArrowDown") { e.preventDefault(); $("q").blur(); move(1); }
    return;
  }
  const inPanel = e.target.closest?.("#panel");
  if (e.key === "/") { e.preventDefault(); $("q").focus(); $("q").select(); }
  else if (e.key === "?") { $("keys").hidden = !$("keys").hidden; }
  else if (e.key === "Escape") {
    if (!$("keys").hidden) $("keys").hidden = true;
    else if (S.open) closePanel();
    else if (S.idle || S.who) filter({ idle: false, who: null });
  }
  else if (e.key === "j" || (e.key === "ArrowDown" && !inPanel)) { e.preventDefault(); move(1); }
  else if (e.key === "k" || (e.key === "ArrowUp" && !inPanel)) { e.preventDefault(); move(-1); }
  else if ("123".includes(e.key) && e.key.length === 1) go({ 1: $("work"), 2: $("result"), 3: $("msgs") }[e.key].querySelector(".open, .msg"));
  else if (e.key === "Enter" && e.target.matches?.("#msgs .msg")) toggleFull(e.target);
});
$("q").addEventListener("input", () => filter({ q: $("q").value.trim().toLowerCase() }));
addEventListener("hashchange", fromHash);
addEventListener("pointermove", e => { S.pointer = { x: e.clientX, y: e.clientY }; }, { passive: true });
new ResizeObserver(() => S.benches && charts()).observe($("hill"));
small.addEventListener("change", () => S.data && render());
document.fonts.ready.then(() => S.benches && charts());

/* Since the last look: the last read shown while the tab was visible and focused is kept when the reader leaves
   (blur, hidden, closed) and becomes the reference when the reader comes back (focus, visible). */
const keepSeen = () => S.lookedAt && store.set(SEEN_KEY, String(S.lookedAt));
const back = () => { S.since = Number(store.get(SEEN_KEY)) || S.since; S.acked = false; if (S.data) render(); };
const ack = () => { if (!S.acked && document.hasFocus()) { S.acked = true; render(); } };
document.addEventListener("visibilitychange", () => { if (document.hidden) { keepSeen(); clearTimeout(timer); } else { back(); poll(); } });
addEventListener("blur", keepSeen);
addEventListener("focus", back);
addEventListener("pagehide", keepSeen);
addEventListener("scroll", ack, { passive: true });
addEventListener("keydown", ack);

const params = new URLSearchParams(location.search);
S.who = params.get("who"); S.idle = params.get("idle") === "1";
$("q").value = params.get("q") ?? ""; S.q = $("q").value.trim().toLowerCase();
S.since = Number(store.get(SEEN_KEY)) || null; S.acked = !S.since;
const ph = tag => `<${tag} class="ph-row"><span class="ph"></span><span class="ph"></span><span class="ph"></span></${tag}>`;
["work", "result", "idea", "knowledge", "closed"].forEach(id => { $(id).innerHTML = ph("div").repeat(3); });
$("msgs").innerHTML = ph("li").repeat(4);
$("lanes").innerHTML = `<div class="lane"><span class="ph" style="width:96px"></span><div class="track" style="--hour:16.6%"></div></div>`.repeat(3);
fromHash();
poll();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    if {"--help", "-h"} & set(sys.argv):
        sys.exit(__doc__)
    team.table()  # once, before the threads of the first /data: each would build its own boto3 resource (0.84 s instead of 0.05 s)
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"board at http://127.0.0.1:{PORT}  (Ctrl-C stops it)")
    if sys.stdout.isatty():
        webbrowser.open(f"http://127.0.0.1:{PORT}")
    server.serve_forever()
