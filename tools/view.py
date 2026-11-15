# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35"]
# ///
"""The board and the messages as a live web page on this laptop, read-only.

  uv run tools/view.py [--port 8765] [--hours 6]

Opens http://127.0.0.1:8765 in the browser (only when started from a terminal). The page is the Board tab of the team
site, for people. At the top, what changed since the reader's last look ("Nothing new since 22:54.") and one sentence on
the board: open work items, from how many people, how many idle over an hour (a click shows only those, ?idle=1), the
last result (a click opens it). Then one benchmark at a time (?bench=): the reach bar, from 0 % to the best RL score,
with the best untrained-base score at its left, one segment per record step (faint when within noise) and the points
still missing to RL as its empty rest; the hill-climbing chart with 95% intervals; and beside the chart (under it below
1100 px) the ladder of record steps, the RL line first with the gap's 95% interval, then one line per step: the gain,
the step's title, previous best -> new best, "within noise". A click on a step, its segment or its dot (?step=<right>)
opens it under its line: what changed, why it works, is it real, cost, settings. The words come from the plain rows
that agents write for a result (board.py plain); a step without them shows what its configuration gained and lost
against the step before and the first sentence of the result's text. Below: Now (open work, longest idle first, red
from 60 minutes) and Learned (results that set no record and announce nothing), one line per item; then one row, More
(?more=), that opens one list at a time: results that announce a page or a tool (told apart by a rule on their text,
ANNOUNCE in the page), ideas, knowledge and skills, closed work, the messages on `all`, and one lane per person with
every post and message of the last --hours. A term of tools/glossary.py is explained in one sentence on click,
in an opened step and in the side panel. The page reads /data every 10 s and rewrites only what changed.
A click on an item opens its title, what, why and caveat, its full text, scores, votes, comments and message thread in
a side panel whose address is /#<item id>; the filters are in the address too (/?who=<name>&q=<text>&idle=1). Keys:
/ filter, j and k move, 1 2 3 jump to the record steps, Now and Learned, Enter opens, Esc closes, ? lists the keys. A
click on a person shows only that person. The look is that of the Design tab (.claude/skills/site-ui/SKILL.md).

  GET /demo            the talk as a deck of twelve 16:9 slides (demo_deck.py): keys step, p prints one slide per page
  GET /demo/fig/<name> the pictures the deck embeds (climb, harness, beyond, efficiency, basins), with their
                       header, words column and key hidden (demo_deck.FIGS)
  GET /demo/story      the stepped story of the talk over the Design page's picture (demo.py), fed by the same /data
  GET /demo/ali/<name> Ali's slides of the talk, slide1 to slide3: the idea map, the idea tree and the accuracy climb
                       (demo_ali.py, with its data in demo_ali_data.py); /demo/ali leads to the first
  GET /architecture    the Design tab, how the harness works: one interactive picture (architecture.py), fed by the same /data
  GET /findings        the Findings tab: one tile per finding (findings.py), each a link to the page of that finding
  GET /finding/<slug>  the page of one finding (finding_<slug>.py; .claude/skills/finding-page/SKILL.md)
  GET /proof           the Proof tab: one tile per experiment that tests the team's method itself (the page of findings.py)
  GET /proof/<slug>    the page of one such experiment (proof_<slug>.py, made like a finding page)
  GET /lab/            the site lab: twelve interactive 3D pictures of the team's work (studies/sitelab/index.html), each at
                       /lab/prototypes/<slug>/ with its data.json; static files, fed by the same /data
  GET /favicon.svg     the tab icon of every page; send() writes the link to it into the head of each HTML page
  GET /data            the newest 60 items of each kind and list, the messages on `all` of the last --hours, every score
                       (board.py score), which the hill-climbing chart draws, the plain rows of those results
                       (board.py plain: every title; what, why and caveat only of scored results), the first line of
                       the finding of each scored result older than the newest 60 (climb.finding) and the newest comment
                       of each open work item idle over an hour (JSON), with only the fields the pages read: 9 queries.
                       One snapshot serves every reader for 5 s. Its ETag comes from
                       the content and its time is in the header X-Snapshot-Ns, so a browser that asks again with
                       If-None-Match gets 304 and no body while the board has not changed. The page stops reading while
                       its tab is hidden.
  GET /data/<item id>  one item with its votes, comments, thread and, for a result, its plain rows (JSON); 404 for an unknown id

It reads the same DynamoDB table as board.py and msg.py, with Query and GetItem only, and never writes to it or moves an
agent's message position. A failed read answers 500 with the error text; the page keeps the last data, says "Offline" in its
status and logs the error to the browser console.
"""
import glob
import hashlib
import importlib
import json
import os
import re
import sys
import threading
import time
import traceback
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from boto3.dynamodb.conditions import Key

import architecture
import board
import climb
import demo
import demo_ali
import demo_deck
import exa_page
import findings
import glossary
import home
import pastdev
import psychosis
import sitekit
import team

PORT = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8765
HOURS = float(sys.argv[sys.argv.index("--hours") + 1]) if "--hours" in sys.argv else 6.0
LISTS = ("work", "result", "idea", "knowledge", "skill", "work-closed")
# One page per finding: every tools/finding_<slug>.py (TITLE, LINE, PAGE) is served at /finding/<slug> and has a tile
# on /findings. Its ICON, the JavaScript source of the tile's icon, is written into that page here (findings.py).
FINDINGS = {os.path.basename(f)[len("finding_"):-3].replace("_", "-"): importlib.import_module(os.path.basename(f)[:-3])
            for f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "finding_*.py")))}
FINDING_ROWS = [findings.entry(slug, m) for slug, m in FINDINGS.items()]  # read once, so a module that changed fails here
FINDING_PAGES = {slug: sitekit.add(m.PAGE) for slug, m in FINDINGS.items()}  # each with the kit of sitekit.py (terms, math)


def tiles_page(modules, rows, differences=()):
    """The tile page of findings.py with the icons of these modules and the rows written in, and the given text differences applied."""
    page = findings.PAGE.replace("__ICONS__", "{" + ", ".join(f"{json.dumps(s)}: {m.ICON}" for s, m in modules.items() if hasattr(m, "ICON")) + "}")
    page = page.replace("__ROWS__", json.dumps(rows, ensure_ascii=False))
    for old, new in differences:
        assert page.count(old) == 1, f"findings.PAGE no longer holds {old!r} once"
        page = page.replace(old, new)
    return page


FINDINGS_PAGE = {}  # built at its first request: two marks of its picture are board scores, read once


def findings_page():
    if not FINDINGS_PAGE:
        scores = board.rows(KeyConditionExpression=Key("pk").eq("scores"))
        FINDINGS_PAGE["page"] = sitekit.add(tiles_page(FINDINGS, findings.resolve(FINDING_ROWS, scores)))
    return FINDINGS_PAGE["page"]


# One page per experiment that tests the team's method itself: every tools/proof_<slug>.py, with the same four values
# as a finding page, is served at /proof/<slug> and has a tile on /proof.
PROOFS = {os.path.basename(f)[len("proof_"):-3].replace("_", "-"): importlib.import_module(os.path.basename(f)[:-3])
          for f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "proof_*.py")))}
PROOF_PAGE = tiles_page(PROOFS, [{"slug": slug, "title": m.TITLE, "line": m.LINE} for slug, m in PROOFS.items()], findings.PROOF)


# The tab icon of every page: the lit body of the Design page and one orbit around it, on the dark paper, with the light
# from the upper left. The orbit is faint behind the body and heavier in front of it.
FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
<radialGradient id="b" cx=".34" cy=".3" r=".8"><stop offset="0" stop-color="#f6f9ff"/><stop offset=".45" stop-color="#8fb1ff"/><stop offset="1" stop-color="#2f4fb8"/></radialGradient>
<rect width="32" height="32" rx="7" fill="#080c11"/>
<g transform="rotate(-24 16 16)" fill="none" stroke="#8fb1ff" stroke-linecap="round">
<path d="M2.4 16A13.6 5.6 0 0 1 29.6 16" stroke-width="1.8" opacity=".45"/>
<circle cx="16" cy="16" r="7.4" fill="url(#b)" stroke="none"/>
<path d="M2.4 16A13.6 5.6 0 0 0 29.6 16" stroke-width="2.6"/>
</g>
</svg>
"""
ICON_LINK = '<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'


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


def plain_rows(item_id=None):
    """The plain-language rows of results (board.py plain): all of them in one Query, or those of one result."""
    key = Key("pk").eq("plain")
    return board.rows(KeyConditionExpression=key & Key("sk").begins_with(item_id) if item_id else key)


def plain_words(rows, full=lambda row: True):
    """{sk: {title, what, why, caveat}} of plain rows; only the title of a row for which full(row) is false."""
    return {r["sk"]: {k: r[k] for k in (board.PLAIN if full(r) else ("title",)) if k in r} for r in rows}


def snapshot():
    start = f"{time.time_ns() - int(HOURS * 3600 * 10**9):020d}"
    with ThreadPoolExecutor(len(LISTS) + 3) as pool:  # every list, the messages, the scores and the plain rows at the same time
        messages = pool.submit(board.rows, KeyConditionExpression=Key("pk").eq("chan#all") & Key("sk").gt(start))
        scores = pool.submit(board.rows, KeyConditionExpression=Key("pk").eq("scores"))  # every score, in the order its result was posted
        plain = pool.submit(plain_rows)
        items = [item for page in pool.map(newest, LISTS) for item in page]
        messages, scores, plain = messages.result(), scores.result(), plain.result()
        late = [(i["id"], i["n_comments"]) for i in items if i["listed"] == "work" and i.get("n_comments")
                and time.time_ns() - int(i.get("active_ns", i["at_ns"])) >= LATE_NS]
        new = [k for k in late if k not in COMMENTS]
        COMMENTS.update(zip(new, pool.map(lambda k: last_comment(k[0]), new)))
        texts = {i["id"]: i["text"] for i in items}
        scored = set(s["result"] for s in scores)
        old = [r for r in dict.fromkeys(s["result"] for s in scores) if r not in texts]  # scored results that are not among the newest 60
        FOUND.update(zip([r for r in old if r not in FOUND], pool.map(finding, [r for r in old if r not in FOUND])))  # one GetItem each, once per process
    # the page reads a result's title from "plain"; what, why and caveat only of scored results, the rest with /data/<item id>
    return {"hours": HOURS, "test": team.TEST, "items": cols(items, ITEM), "messages": cols(messages, MESSAGE), "scores": cols(scores, SCORE),
            "last_comments": {k[0]: COMMENTS[k] for k in late}, "finding": {r: FOUND[r] for r in old},
            "plain": plain_words([r for r in plain if r["item"] in scored or r["item"] in texts], lambda r: r["item"] in scored)}


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
            "plain": plain_words(plain_rows(item_id)) if item["kind"] == "result" else {},
            "comments": sorted((r for r in rows if r["sk"].startswith("comment#")), key=lambda c: c["sk"]),
            "thread": board.rows(KeyConditionExpression=Key("pk").eq(f"chan#{item_id}"))}


# The papers (studies/<study>/paper/<name>.pdf), served at /paper/<name>.pdf: beside this file on AWS (infra/monitor/deploy.sh), in their study here.
# The site lab's static files: beside the code in the Lambda zip (infra/monitor/deploy.sh), in the study in the repository.
LAB = (Path(__file__).with_name("sitelab"), Path(__file__).parent.parent / "studies/sitelab")
LAB_FILE = re.compile(r"(prototypes/[a-z-]+/)?(index\.html|data\.json)?")
PAPERS = {name: (Path(__file__).with_name(name), Path(__file__).parent.parent / "studies" / folder / name)
          for name, folder in (("the-finish-dial.pdf", "rlneurons/paper"), ("theories-on-trial.pdf", "theory/paper"),
                               ("the-first-hundred-steps.pdf", "rlneurons/paper-first-steps"),
                               ("no-early-warning.pdf", "rlneurons/paper-no-warning"))}
DECK_PAGE = demo_deck.page(len(FINDINGS), PAPERS)  # the talk deck at /demo, with the number of finding pages and the papers


# The home page (home.py) is the page / of invariant.team; on any other host / is the board and the home page is /home.
# API Gateway passes the name the browser asked for in the Host header.
HOME_HOSTS = ("invariant.team", "www.invariant.team")
HOME_PAGE = home.PAGE.replace("__COUNTS__", json.dumps({
    "findings": len(FINDINGS), "proof": len(PROOFS),
    "lab": max(len(list((d / "prototypes").glob("*/index.html"))) for d in LAB)}))


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"  # Chrome revalidates with If-None-Match only for HTTP/1.1 responses

    def send(self, status, kind, body, headers=()):
        if kind == "text/html":  # every page gets the tab icon here, so no page module holds it
            body = body.replace("<title>", ICON_LINK + "<title>", 1)
        data = body if isinstance(body, bytes) else body.encode()
        tag = f'"{hashlib.blake2b(data, digest_size=16).hexdigest()}"'  # from the content, so an unchanged board answers 304
        if status == 200 and self.headers.get("If-None-Match") == tag:
            self.send_response(304)
            data = b""
        else:
            self.send_response(status)
            self.send_header("Content-Type", kind if isinstance(body, bytes) else f"{kind}; charset=utf-8")
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
        host = (self.headers.get("X-Forwarded-Host") or self.headers.get("Host") or "").split(":")[0].lower()
        if path == "/home" or (path == "/" and host in HOME_HOSTS):
            return self.send(200, "text/html", HOME_PAGE)
        if path == "/board":  # the board was here for two hours on 2026-11-15
            return self.send(302, "text/plain", "", [("Location", "/")])
        if path == "/":
            return self.send(200, "text/html", PAGE)
        if path == "/demo":
            return self.send(200, "text/html", DECK_PAGE)
        if path == "/demo/story":
            return self.send(200, "text/html", demo.PAGE)
        if path.startswith("/demo/fig/") and path[len("/demo/fig/"):] in demo_deck.FIGS:
            return self.send(200, "text/html", demo_deck.FIGS[path[len("/demo/fig/"):]])
        if path in ("/demo/ali", "/demo/ali/"):
            return self.send(302, "text/plain", "", [("Location", "/demo/ali/slide1")])
        if path.startswith("/demo/ali/") and path[len("/demo/ali/"):] in demo_ali.PAGES:
            return self.send(200, "text/html", demo_ali.PAGES[path[len("/demo/ali/"):]])
        if path == "/architecture":
            return self.send(200, "text/html", architecture.PAGE)
        if path == "/findings":
            return self.send(200, "text/html", findings_page())
        if path.startswith("/finding/") and path[len("/finding/"):] in FINDING_PAGES:
            return self.send(200, "text/html", FINDING_PAGES[path[len("/finding/"):]])
        if path == "/proof":
            return self.send(200, "text/html", PROOF_PAGE)
        if path.startswith("/proof/") and path[len("/proof/"):] in PROOFS:
            return self.send(200, "text/html", PROOFS[path[len("/proof/"):]].PAGE)
        if path == "/exa":
            return self.send(200, "text/html", exa_page.PAGE)
        if path == "/pastdev":
            return self.send(200, "text/html", pastdev.PAGE)
        if path == "/psychosis":
            return self.send(200, "text/html", psychosis.PAGE)
        if path == "/favicon.svg":
            return self.send(200, "image/svg+xml", FAVICON)
        if path == "/lab":  # the pages link to their files relative to the folder
            return self.send(302, "text/plain", "", [("Location", "/lab/")])
        if path.startswith("/lab/") and LAB_FILE.fullmatch(path[len("/lab/"):]):
            name = path[len("/lab/"):] + ("index.html" if path.endswith("/") else "")
            found = [d / name for d in LAB if (d / name).is_file()]
            if not found:  # a deploy without the folder answers 404 and the other pages stay up
                return self.send(404, "text/plain", f"no page {path}")
            if name.endswith(".html"):
                return self.send(200, "text/html", found[0].read_text())
            return self.send(200, "application/json", found[0].read_bytes())
        if path.startswith("/paper/") and path[7:] in PAPERS:
            found = [p for p in PAPERS[path[7:]] if p.exists()]  # a deploy without the file answers 404 and the other pages stay up
            return self.send(200, "application/pdf", found[0].read_bytes()) if found else self.send(404, "text/plain", f"no page {path}")
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
<title>Invariant: Board</title>
<link rel="preload" href="/data" as="fetch" crossorigin>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap" media="print" onload="this.media='all'">
<style>
/* The tokens and the type of architecture.py (.claude/skills/site-ui/SKILL.md). This page is lists and one chart, so it
   has no lit object: the chart is its one picture. Blue means live, fresh or selected. Red means a problem. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34; --on-blue: #fff;
  --pl: .56; --pc: .15; --dim: .16;
  --blue-wash: color-mix(in srgb, var(--blue) 10%, transparent);
  --gap: color-mix(in srgb, var(--ink) 5%, transparent);
  --scrim: rgb(16 24 32 / .2);
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c; --on-blue: #080c11;
    --pl: .78; --pc: .13; --dim: .24;
    --blue-wash: color-mix(in srgb, var(--blue) 14%, transparent);
    --gap: color-mix(in srgb, var(--ink) 7%, transparent);
    --scrim: rgb(0 0 0 / .5);
  }
}
* { box-sizing: border-box; }
[hidden] { display: none !important; }
html { background: var(--paper); }
body {
  margin: 0; color: var(--ink); background: var(--paper); overflow-anchor: none;
  font: 400 15px/1.5 "Archivo", ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif;
  font-variant-numeric: tabular-nums; -webkit-font-smoothing: antialiased;
}
button { font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; text-align: left; }
a { color: inherit; text-decoration: none; }
code { font: inherit; font-weight: 600; }
p, h1, h2, h3, dl, dd { margin: 0; }
:focus-visible { outline: 2px solid var(--blue); outline-offset: 3px; border-radius: 3px; }
.sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); white-space: nowrap; }
.wrap { max-width: 1840px; margin: 0 auto; padding: 20px 40px 56px; }

/* Header, as on the Design and Findings tabs */
.top { display: flex; align-items: center; flex-wrap: wrap; gap: 6px 26px; font-size: 13px; padding-bottom: 16px; border-bottom: 1px solid var(--rule); }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; margin: 0 6px 0 0; }
.top a { color: var(--mute); white-space: nowrap; transition: color .15s ease; }
.top a:hover { color: var(--ink); }
.top a[aria-current] { color: var(--ink); font-weight: 600; }
.test { color: var(--red); font-weight: 600; }
.status { margin-left: auto; color: var(--mute); white-space: nowrap; display: flex; align-items: center; gap: 10px; }
.status::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: var(--faint); }
.status.live::before { background: var(--blue); box-shadow: 0 0 0 4px color-mix(in srgb, var(--blue) 20%, transparent); }
.status.bad { color: var(--red); }
.status.bad::before { background: var(--red); box-shadow: 0 0 0 4px color-mix(in srgb, var(--red) 20%, transparent); }

/* The one sentence, on the state of the board; above it, what changed since the last look */
.lede { margin-top: clamp(14px, 2.6vh, 26px); min-height: 32px; }
.since { margin: 0 0 4px; font-size: 13px; line-height: 18px; color: var(--mute); }
.since.fresh::before { content: ""; display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: var(--blue); margin-right: 9px; vertical-align: .1em; }
.since b { font-weight: 600; color: var(--ink); }
.summary { font-size: clamp(19px, 1.5vw, 24px); line-height: 1.3; font-weight: 300; letter-spacing: -.005em; max-width: 60em; }
.summary b { font-weight: 600; }
.summary .warn { color: var(--red); }
.summary button, .summary a { text-decoration: underline 1px; text-underline-offset: 4px; text-decoration-color: color-mix(in srgb, currentColor 35%, transparent); }
.summary button:hover, .summary a:hover, .summary button[aria-pressed="true"] { text-decoration-color: currentColor; }
.cv::before { content: ""; position: absolute; left: 0; top: .62em; width: 6px; height: 6px; border-radius: 50%; background: var(--red); }
.benches { display: flex; flex-wrap: wrap; gap: 4px 26px; margin-top: 14px; min-height: 27px; font-size: 13.5px; }
.benches button { color: var(--mute); padding: 3px 0; border-bottom: 2px solid transparent; }
.benches button:hover { color: var(--ink); }
.benches button[aria-pressed="true"] { color: var(--ink); font-weight: 600; border-bottom-color: var(--blue); }
.benches b { font-weight: inherit; margin-left: 3px; }

/* A term of the glossary: a click opens its one sentence */
.term { cursor: pointer; text-decoration: underline dotted 1px; text-underline-offset: .22em; text-decoration-color: color-mix(in srgb, currentColor 55%, transparent); border-radius: 2px; font-weight: inherit; }
.term:hover, .term[aria-expanded="true"] { text-decoration-color: var(--blue); text-decoration-style: solid; }
.def {
  position: fixed; z-index: 6; width: max-content; max-width: min(340px, calc(100vw - 32px)); padding: 10px 14px 11px; border-radius: 8px;
  background: var(--sheet); border: 1px solid var(--rule); font-size: 13.5px; line-height: 1.45; color: var(--mute);
}
.def b { color: var(--ink); font-weight: 600; margin-right: 2px; }

/* Reach: how far the best untrained-base score has come toward the RL score, one segment per record step */
.reach { position: relative; height: 92px; margin-top: clamp(14px, 2.4vh, 24px); }
.reach .ends { display: flex; align-items: baseline; gap: 10px; height: 46px; white-space: nowrap; }
.reach .big { font-size: 34px; line-height: 40px; font-weight: 300; letter-spacing: -.01em; }
.reach .big.base { color: var(--blue); }
.reach .lab { font-size: 13px; color: var(--mute); }
.reach .rl-end { margin-left: auto; display: flex; align-items: baseline; gap: 10px; }
.reach .bar8 { position: relative; height: 8px; margin-top: 6px; }
.reach .piece { position: absolute; top: 0; height: 8px; }
.reach .piece i { position: absolute; inset: 0 0 0 2px; min-width: 1px; background: var(--blue); }
.reach .piece.first i { left: 0; border-radius: 4px 0 0 4px; }
.reach .piece.last i { border-radius: 0 4px 4px 0; }
.reach .piece.first.last i { border-radius: 4px; }
.reach .piece.noise i { opacity: .45; }
.reach .piece.togo i { background: var(--rule); }
.reach .fill { position: absolute; inset: 0; }
.reach .fill.grow { animation: grow .6s cubic-bezier(.22, .61, .36, 1) backwards;  /* backwards: no clip-path is left after it, so the hit areas and the focus ring are not cut */ }
@keyframes grow { from { clip-path: inset(0 100% 0 0); } to { clip-path: inset(0 0 0 0); } }
.reach button.piece::after { content: ""; position: absolute; left: var(--hx, 0px); right: var(--hx, 0px); top: -10px; height: 28px; }
.reach button.piece:focus-visible { outline: none; }
.reach button.piece:focus-visible i { outline: 2px solid var(--blue); outline-offset: 3px; }
.reach button.piece:hover i { filter: brightness(1.12); }
.reach.has-sel button.piece i { opacity: calc(var(--dim) + .12); transition: opacity .28s ease; }
.reach.has-sel button.piece.on i { opacity: 1; }
.reach .marks { position: relative; height: 18px; margin-top: 8px; font-size: 13px; line-height: 18px; color: var(--mute); }
.reach .marks span { position: absolute; top: 0; white-space: nowrap; }

/* The chart and, beside it, the ladder of record steps */
.hero { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 20px 56px; margin-top: clamp(12px, 2vh, 20px); align-items: start; }
.chart { height: 320px; min-width: 0; }
.chart svg { display: block; overflow: visible; }
.chart svg text {
  font: 400 11.5px "Archivo", ui-sans-serif, system-ui, sans-serif; fill: var(--mute);
  paint-order: stroke; stroke: var(--paper); stroke-width: 4px; stroke-linejoin: round;
}
.chart .brk { stroke: var(--paper); stroke-width: 5px; }
.chart .brk-line { stroke: var(--blue); stroke-width: 1.4px; }
.chart .grid { stroke: var(--rule); stroke-width: 1; }
.chart .gap { fill: var(--gap); }
.chart .target { stroke: var(--ink); stroke-width: 1.1; stroke-dasharray: 3 4; opacity: .6; }
.chart text.rl { fill: var(--ink); }
.chart text.rl tspan, .chart text.gain { font-weight: 600; }
.chart text.gain { fill: var(--ink); }
.chart text.lead { fill: var(--blue); font-weight: 600; }
.chart text.quiet { fill: var(--faint); }
.chart .tread, .chart .rise { fill: none; stroke: var(--blue); stroke-width: 2.25; stroke-linecap: round; }
.chart .rise.noise { opacity: .32; }
.chart .ci { stroke: var(--faint); stroke-width: .8; opacity: .5; }
.chart .ci.rec { stroke: var(--blue); opacity: .6; }
.chart .dot { fill: var(--paper); stroke: var(--faint); stroke-width: 1.2; }
.chart .dot.rec { fill: var(--blue); stroke: var(--paper); stroke-width: 2; }
.chart .x { stroke: var(--faint); stroke-width: 1.4; stroke-linecap: round; }
.chart .hit { fill: transparent; }
.chart .under { fill: var(--paper); }
.chart a:hover .dot, .chart a:focus-visible .dot, .chart a:hover .x, .chart a:focus-visible .x { stroke: var(--ink); }
.chart .has-sel .tread, .chart .has-sel .rise, .chart .has-sel .ci, .chart .has-sel .mark, .chart .has-sel text.gain { opacity: calc(var(--dim) + .12); transition: opacity .28s ease; }
.chart .has-sel .on { opacity: 1; }
.chart .ckey { display: flex; flex-wrap: wrap; gap: 2px 16px; margin: 6px 0 0; font-size: 13px; line-height: 18px; color: var(--mute); }
.chart .ckey span { display: inline-flex; align-items: center; gap: 6px; white-space: nowrap; }
.chart .ckey svg { display: inline-block; }
h2 { font-size: 13px; font-weight: 600; color: var(--mute); display: flex; align-items: baseline; flex-wrap: wrap; gap: 4px 10px; padding-bottom: 7px; }
h2 .count { font-weight: 400; color: var(--faint); }
.lrow {
  display: grid; grid-template-columns: 3.5em minmax(0, 1fr) auto .6em; column-gap: 14px; align-items: baseline; width: 100%;
  padding: 8px 0; border-top: 1px solid var(--rule); font-size: 14.5px; line-height: 1.35;
}
.lrow > b { font-size: 15px; font-weight: 620; font-stretch: 108%; text-align: right; }
.lrow .lt { min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.lrow .lt small { font-size: 13px; color: var(--mute); margin-left: 7px; }
.lrow .lr { font-size: 13px; color: var(--mute); white-space: nowrap; }
.lrow .flag { color: var(--mute); margin-left: 9px; }
.lrow .chev { color: var(--mute); justify-self: end; display: inline-block; transition: transform .15s ease; }
.lrow[aria-expanded="true"] .chev { transform: rotate(90deg); }
.lrow.noise > b { color: var(--faint); }
.lrow:hover .lt { text-decoration: underline 1px; text-underline-offset: 3px; text-decoration-color: color-mix(in srgb, currentColor 40%, transparent); }
.lrow[aria-expanded="true"] > b { color: var(--blue); }
.lrow[aria-expanded="true"] .lt { font-weight: 600; white-space: normal; }
.sd { display: grid; grid-template-columns: 6.2em minmax(0, 1fr); gap: 7px 14px; margin: 0 0 13px; font-size: 14px; line-height: 1.45; animation: fade .2s ease-out; }
.sd dt { font-size: 13px; font-weight: 600; color: var(--mute); padding-top: 1px; }
.sd dd { max-width: 80ch; }
.sd dd p + p { margin-top: 4px; }
.sd .cv { position: relative; padding-left: 15px; }
.sd .set { font-size: 13px; color: var(--mute); }
.sd .raw { color: var(--mute); }
.sd a.go { font-size: 13px; color: var(--mute); white-space: nowrap; margin-left: 8px; text-decoration: underline 1px; text-underline-offset: 3px; text-decoration-color: color-mix(in srgb, currentColor 40%, transparent); }
.sd a.go:hover { color: var(--ink); }
@keyframes fade { from { opacity: 0; } }

/* Above the lists: the people, the filter */
.bar { display: flex; align-items: center; flex-wrap: wrap; gap: 8px 26px; margin-top: 34px; min-height: 30px; font-size: 13px; color: var(--mute); }
.people { display: flex; flex-wrap: wrap; gap: 4px 18px; margin-left: auto; }
.people button { display: inline-flex; align-items: center; gap: 7px; }
.people button:hover, .people button[aria-pressed="true"] { color: var(--ink); }
.people button[aria-pressed="true"] { font-weight: 600; }
.people.picked button[aria-pressed="false"] { opacity: .45; }
.search { position: relative; display: flex; align-items: center; }
.search input {
  width: 210px; font: inherit; font-size: 13.5px; color: var(--ink); background: none; border: 0; border-bottom: 1px solid var(--rule);
  border-radius: 0; padding: 4px 26px 4px 0; -webkit-appearance: none; appearance: none;
}
.search input::placeholder { color: var(--faint); }
.search input:focus { outline: none; border-bottom-color: var(--blue); }
kbd { font: 400 12px/1 "Archivo", sans-serif; color: var(--mute); border: 1px solid var(--rule); border-radius: 4px; padding: 3px 6px; }
.search kbd { position: absolute; right: 0; pointer-events: none; }

/* Lists: one line per item */
.board.main-cols { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 0 56px; align-items: start; margin-top: 14px; }
section { min-width: 0; }
h2 .warn { color: var(--red); font-weight: 600; text-decoration: underline 1px; text-underline-offset: 3px; text-decoration-color: color-mix(in srgb, currentColor 35%, transparent); }
h2 .warn:hover, h2 .warn[aria-pressed="true"] { text-decoration-color: currentColor; }
.empty { color: var(--mute); font-size: 14px; padding: 9px 0; max-width: 52ch; border-top: 1px solid var(--rule); }
.all { display: block; padding: 9px 0; font-size: 13px; color: var(--mute); border-top: 1px solid var(--rule); width: 100%; }
.all:hover { color: var(--ink); }
.row, .msg { position: relative; border-top: 1px solid var(--rule); --c: oklch(var(--pl) var(--pc) var(--h)); break-inside: avoid; }
.row .open, .msg { display: grid; grid-template-columns: 11px minmax(0, 1fr) auto; column-gap: 12px; align-items: center; min-height: 34px; font-size: 14.5px; line-height: 1.35; }
.row .open { padding: 6px 0; border-radius: 2px; }
.row .t { min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.row .r, .msg .r { font-size: 12.5px; color: var(--mute); white-space: nowrap; }
.row .r.late { color: var(--red); font-weight: 600; }
.row .r.fresh { color: var(--blue); }
.row:hover .t, .row.current .t { text-decoration: underline 1px; text-underline-offset: 3px; text-decoration-color: color-mix(in srgb, currentColor 40%, transparent); }
.row.current .t { font-weight: 600; }
.shut .t { color: var(--mute); }
.new::after { content: ""; position: absolute; left: -12px; top: calc(50% - 3px); width: 6px; height: 6px; border-radius: 50%; background: var(--blue); }
.g { display: block; justify-self: center; flex: none; width: 9px; height: 9px; border-radius: 50%; background: var(--c, var(--mute)); }
.g.ring { background: none; border: 1.5px solid var(--c, var(--mute)); }
.late .g.ring { border-color: var(--red); }
.g.shut { opacity: .45; }
.g.small { width: 5px; height: 5px; opacity: .7; }
.g.tick { width: 1px; height: 11px; border-radius: 0; background: var(--faint); }
.msg { padding: 6px 0; cursor: pointer; align-items: start; }
.msg .g { margin-top: 5px; }
.msg .r { padding-top: 2px; }
.msg .t { min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.msg .t b { font-weight: 600; color: var(--c); margin-right: 5px; }
.msg.full .t { white-space: pre-line; overflow: visible; overflow-wrap: anywhere; }
.n { font-weight: 600; }
a.ref { color: var(--blue); text-decoration: underline; text-decoration-color: var(--blue-wash); text-underline-offset: 3px; }
a.ref:hover { text-decoration-color: var(--blue); }
.arrived { animation: arrive 2.6s ease-out; }
@keyframes arrive { from { background-color: var(--blue-wash); } }

/* More: the other lists, one open at a time */
.rest { margin-top: 34px; }
.tabs { display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 24px; font-size: 13.5px; padding-bottom: 9px; }
.tabs .lab { font-size: 13px; font-weight: 600; color: var(--mute); }
.tabs button { color: var(--mute); padding: 3px 0; border-bottom: 2px solid transparent; }
.tabs button:hover { color: var(--ink); }
.tabs button[aria-pressed="true"] { color: var(--ink); font-weight: 600; border-bottom-color: var(--blue); }
.tabs .count { color: var(--faint); font-weight: 400; margin-left: 2px; }
.mhead { font-size: 13px; color: var(--mute); padding-bottom: 8px; }
.mhead button { text-decoration: underline 1px; text-underline-offset: 3px; text-decoration-color: color-mix(in srgb, currentColor 40%, transparent); }
.mhead button:hover { color: var(--ink); }
.cols2 { columns: 2; column-gap: 56px; }

/* Activity: one lane per person, every post and message of the last hours as a mark */
.lane { display: grid; grid-template-columns: 150px minmax(0, 1fr); align-items: center; height: 28px; --c: oklch(var(--pl) var(--pc) var(--h)); }
.lane > button { font-size: 13px; color: var(--mute); padding-right: 12px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: flex; align-items: center; gap: 8px; }
.lane > button:hover, .lane.on > button { color: var(--ink); }
.lane.off { opacity: .28; }
.track {
  position: relative; height: 100%;
  background: linear-gradient(var(--rule), var(--rule)) 0 50% / 100% 1px no-repeat,
              linear-gradient(to right, color-mix(in srgb, var(--rule) 60%, var(--paper)) 1px, transparent 1px) 0 0 / var(--hour) 100%;
}
.mk { position: absolute; top: 50%; transform: translate(-50%, -50%); border-radius: 50%; }
.mk.res { width: 9px; height: 9px; background: var(--c); z-index: 3; }
.mk.claim { width: 9px; height: 9px; border: 1.5px solid var(--c); background: var(--paper); z-index: 2; }
.mk.idea { width: 5px; height: 5px; background: var(--c); opacity: .7; z-index: 1; }
.mk.tick { width: 1px; height: 11px; border-radius: 0; background: var(--faint); opacity: .8; }
a.mk::before { content: ""; position: absolute; inset: -6px; }
a.mk:hover, a.mk:focus-visible { --c: var(--ink); }
.axis { display: grid; grid-template-columns: 150px minmax(0, 1fr); font-size: 12px; color: var(--faint); }
.axis div { position: relative; height: 18px; }
.axis div span { position: absolute; top: 4px; transform: translateX(-50%); white-space: nowrap; }
.axis div span:first-child { transform: none; }
.axis div span:last-child { transform: translateX(-100%); }

/* The key of the glyphs */
.key { display: flex; flex-wrap: wrap; gap: 6px 22px; margin-top: 40px; padding-top: 14px; border-top: 1px solid var(--rule); font-size: 12.5px; color: var(--mute); }
.key span { display: inline-flex; align-items: center; gap: 8px; }
.key .keys-hint { margin-left: auto; }

/* Placeholders before the first read */
.ph { display: block; height: 10px; border-radius: 5px; background: var(--rule); }
.ph-row { display: block; padding: 12px 0; border-top: 1px solid var(--rule); }
.ph-row .ph { width: 62%; }

/* Item panel */
.scrim { position: fixed; inset: 0; z-index: 2; background: var(--scrim); animation: fade .18s ease-out; }
.panel {
  position: fixed; top: 0; right: 0; bottom: 0; width: min(600px, 100vw); z-index: 3;
  background: var(--paper); border-left: 1px solid var(--rule); overflow-y: auto; animation: slide .18s ease-out;
}
@keyframes slide { from { transform: translateX(24px); opacity: 0; } }
.phead { position: sticky; top: 0; z-index: 1; background: var(--paper); padding: 20px 32px 0; }
.phead > div { display: flex; align-items: baseline; gap: 12px; padding-bottom: 12px; border-bottom: 1px solid var(--ink); }
#ptitle:focus { outline: none; }
.phead h2 { padding: 0; font-size: 17px; font-weight: 660; font-stretch: 114%; letter-spacing: .008em; color: var(--ink); white-space: nowrap; }
.phead .kind { color: var(--mute); font-size: 13px; min-width: 0; }
.phead .kind.warn { color: var(--red); font-weight: 600; }
.phead .actions { margin-left: auto; display: flex; gap: 16px; white-space: nowrap; }
.phead .actions button { font-size: 13px; color: var(--mute); }
.phead .actions button:hover { color: var(--ink); }
.pbody { padding: 18px 32px 48px; }
.lead { font-size: clamp(17px, 1.3vw, 21px); line-height: 1.36; font-weight: 380; max-width: 30em; margin-bottom: 16px; }
.pbody .sd { margin: 0 0 24px; grid-template-columns: 4.6em minmax(0, 1fr); animation: none; }
.pbody h3 { font-size: 13px; font-weight: 600; color: var(--mute); margin: 0 0 4px; display: flex; gap: 10px; }
.pbody h3 span { color: var(--faint); font-weight: 400; }
.full { font-size: 14.5px; line-height: 1.6; white-space: pre-wrap; overflow-wrap: anywhere; margin: 0 0 26px; max-width: 70ch; }
.full.only { font-size: 16px; }
.facts { display: grid; grid-template-columns: max-content minmax(0, 1fr); gap: 0 20px; margin: 0 0 28px; font-size: 13.5px; }
.facts dt, .facts dd { padding: 7px 0; border-top: 1px solid var(--rule); }
.facts dt { color: var(--mute); }
.facts dd { overflow-wrap: anywhere; }
.facts dd p + p { margin-top: 4px; }
.facts .who { color: oklch(var(--pl) var(--pc) var(--h)); font-weight: 600; }
.facts small { font-size: inherit; color: var(--mute); }
.pbody .msgs { margin-bottom: 26px; }
.pmsg { padding: 9px 0; border-top: 1px solid var(--rule); font-size: 14.5px; --c: oklch(var(--pl) var(--pc) var(--h)); }
.pmsg .meta { font-size: 12.5px; color: var(--mute); display: flex; gap: 10px; margin-bottom: 2px; }
.pmsg .meta b { color: var(--c); font-weight: 600; }
.pmsg .text { white-space: pre-line; overflow-wrap: anywhere; }
.note { color: var(--mute); font-size: 14px; margin: 4px 0 26px; }

/* Keys */
.keys { position: fixed; right: 24px; bottom: 24px; z-index: 5; background: var(--sheet); border: 1px solid var(--rule); border-radius: 10px; padding: 16px 20px 18px; font-size: 13px; }
.keys h2 { color: var(--ink); padding-bottom: 10px; }
.keys dl { display: grid; grid-template-columns: max-content 1fr; gap: 8px 16px; align-items: center; }
.keys dt { display: flex; gap: 4px; }
.keys dd { color: var(--mute); }

@media (max-width: 1099px) {
  .hero { grid-template-columns: minmax(0, 1fr); }
  .chart { height: 250px; }
}
@media (max-width: 900px) {
  .wrap { padding: 16px 16px 40px; }
  .top { gap: 6px 13px; padding-bottom: 12px; }
  .name { font-stretch: 112%; margin-right: 0; }
  .chart { height: 200px; }
  .board.main-cols { grid-template-columns: minmax(0, 1fr); }
  .s-result { margin-top: 30px; }
  .cols2 { columns: 1; }
  .people { margin-left: 0; }
  .search { width: 100%; }
  .search input { width: 100%; }
  .lrow { grid-template-columns: 3.1em minmax(0, 1fr) .6em; }
  .lrow .chev { grid-column: 3; grid-row: 1; }
  .lrow .lt { white-space: normal; }
  .lrow .lt small { display: block; margin-left: 0; }
  .lrow .lr { grid-column: 2; }
  .lrow .flag { margin-left: 0; }
  .lrow .flag::before { content: " · "; }
  .sd { grid-template-columns: minmax(0, 1fr); gap: 2px; }
  .sd dd { margin-bottom: 9px; }
  .pbody .sd { grid-template-columns: minmax(0, 1fr); }
  .phead { padding: 16px 16px 0; }
  .pbody { padding: 16px 16px 40px; }
  .lane, .axis { grid-template-columns: 104px minmax(0, 1fr); }
  .key .keys-hint { display: none; }
}
@media (max-width: 699px) {
  .ladder { order: -1; }
  .top { padding-bottom: 2px; }
  .top a { padding: 11px 0; }
  .benches { flex-wrap: nowrap; gap: 4px 12px; margin-top: 2px; font-size: 12.5px; overflow-x: auto; scrollbar-width: none; }
  .benches button { padding: 10px 0; white-space: nowrap; flex: none; }
  .reach { height: 82px; }
  .reach .ends { height: 36px; gap: 8px; }
  .reach .rl-end { gap: 8px; }
  .reach .big { font-size: 26px; line-height: 32px; }
}
@media (prefers-reduced-motion: reduce) {
  .arrived, .panel, .scrim, .sd, .reach .fill.grow { animation: none; }
  .chart * { transition: none !important; }
}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <h1 class="name">Invariant</h1>
    <a href="/" aria-current="page">Board</a>
    <a href="/architecture">Design</a>
    <a href="/proof">Proof</a>
    <a href="/findings">Findings</a>
    <span class="test" id="test" hidden>test table</span>
    <span class="status" id="status" role="status">Reading the board</span>
  </header>
  <span class="sr" id="live" aria-live="polite"></span>
  <section class="lede" aria-label="The state of the board">
    <p class="since" id="since" hidden></p>
    <p class="summary" id="summary"><span class="ph" style="width:min(620px,80%);height:14px;margin-top:8px"></span></p>
  </section>
  <div class="benches" id="benches" role="group" aria-label="Benchmark"></div>
  <section class="reach" id="reach" aria-label="The best untrained-base score against RL"><span class="ph" style="position:absolute;left:0;right:0;top:52px;height:8px;border-radius:4px"></span></section>
  <div class="hero">
    <div class="chart" id="chart"></div>
    <section class="ladder"><h2>Record steps <span class="count" id="n-steps"></span></h2><div id="ladder"><span class="ph-row"><span class="ph"></span></span><span class="ph-row"><span class="ph"></span></span><span class="ph-row"><span class="ph"></span></span></div></section>
  </div>
  <div class="bar">
    <div class="people" id="people" aria-label="Show one person"></div>
    <label class="search"><input id="q" type="search" placeholder="Filter the lists" aria-label="Filter the lists" autocomplete="off"><kbd>/</kbd></label>
  </div>
  <main class="board main-cols">
    <section class="s-work"><h2>Now <span class="count" id="n-work"></span></h2><div id="work"></div><div id="work-all"></div></section>
    <section class="s-result"><h2>Learned <span class="count" id="n-result"></span></h2><div id="result"></div><div id="result-all"></div></section>
  </main>
  <section class="board rest" aria-label="More lists">
    <div class="tabs" id="tabs"></div>
    <div class="mhead" id="more-head"></div>
    <div id="more"></div>
    <div id="more-all"></div>
  </section>
  <footer class="key" aria-label="Key">
    <span><i class="g ring"></i>open work</span><span><i class="g"></i>result</span><span><i class="g small"></i>idea or note</span><span><i class="g tick"></i>message</span>
    <span class="keys-hint"><kbd>?</kbd> keys</span>
  </footer>
</div>
<div class="def" id="def" role="tooltip" hidden></div>
<div class="scrim" id="scrim" hidden></div>
<aside class="panel" id="panel" role="dialog" aria-labelledby="ptitle" hidden></aside>
<div class="keys" id="keys" role="dialog" aria-label="Keys" hidden>
  <h2>Keys</h2>
  <dl>
    <dt><kbd>/</kbd></dt><dd>Filter the lists</dd>
    <dt><kbd>j</kbd><kbd>k</kbd></dt><dd>Next and previous line</dd>
    <dt><kbd>1</kbd><kbd>2</kbd><kbd>3</kbd></dt><dd>Record steps, Now, Learned</dd>
    <dt><kbd>Enter</kbd></dt><dd>Open the step, the item or the whole message</dd>
    <dt><kbd>Esc</kbd></dt><dd>Close</dd>
    <dt><kbd>?</kbd></dt><dd>These keys</dd>
  </dl>
</div>
<script>
const $ = id => document.getElementById(id);
const GLOSSARY = __GLOSSARY__;  // tools/glossary.py: term, match, definition
const S = {
  lookedAt: 0, selAt: 0, changed: new Set(),
  data: null, readAt: 0, error: null, who: null, q: "", idle: false, open: null, detail: null, seen: null,
  bench: null, step: null, more: null, term: null,
  autos: false, all: new Set(), full: new Set(), since: null, acked: true, pointer: null,
};
const HUES = [325, 150, 65, 195, 105, 45, 175, 350];  // far apart first; none in 230-310, where the data blue is
const KINDS = { work: "Open work", "work-closed": "Closed work", result: "Result", idea: "Idea", knowledge: "Knowledge", skill: "Skill" };
const MORE = [["tools", "Tools and site"], ["idea", "Ideas"], ["knowledge", "Knowledge and skills"], ["closed", "Closed work"], ["msgs", "Messages"], ["activity", "Activity"]];
const LIMIT = { result: 12, more: 20 };
const ID = /\b((?:work|result|idea|knowledge|skill)-[0-9a-f]{6})\b|(?<![\w.-])(\d+(?:[.,]\d+)*(?: ?%)?)(?![\w-])/g;
const AUTO = /^(started|done|closed) (work|idea|result|knowledge|skill)-[0-9a-f]{6}\b/;  // what board.py announces by itself
/* The board stores no field that tells a research result from an announcement ("Live at https://..."). This rule on the
   text was fitted on 60 results (10 announcements, all found, no other result): a result with no score whose first 160
   characters name the site, an artifact link, a finding page or a tool, or say that something is live, on main or ready. */
const ANNOUNCE = /monitor\.invariant\.team|claude\.ai\/artifact|\/finding\/\w|\bis (?:live|on main|on branch|ready)\b|\blive (?:at|on)\b|, live\b|\bpage built\b|\bis a team skill\b|\bskill ready\b|^(?:uv run |python3 )?tools\/\w+\.py/i;
const META = /^(?:score|title|what|why|caveat):/;  // lines of a result's text that are not its finding (climb.finding)
const SEEN_KEY = "board.lastSeen", TITLE = "Invariant: Board";
const small = matchMedia("(max-width: 900px)");
let people = [];

const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);  // every attribute is in double quotes
const hue = name => HUES[Math.max(0, people.indexOf(name)) % HUES.length];  // by sorted name: the same colors on every page
const pstyle = name => `--h:${hue(name)}`;
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
const num = v => Number(v).toLocaleString("en-US");
const cap = s => s.charAt(0).toUpperCase() + s.slice(1);
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

/* The glossary. A spelling with a capital matches exactly, any other in either case; the longest spelling wins. */
const SPELL = new Map();
GLOSSARY.forEach(t => t.match.forEach(m => SPELL.set(/[A-Z]/.test(m) ? m : m.toLowerCase(), t)));
const TERM = new RegExp("(?<![\\w-])(?:" + [...SPELL.keys()].sort((a, b) => b.length - a.length).map(s => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|") + ")(?![\\w-])", "gi");
const termOf = word => SPELL.get(word) ?? SPELL.get(word.toLowerCase());
const termBtn = (t, word) => `<span class="term" role="button" tabindex="0" data-term="${esc(t.term)}" aria-expanded="false">${esc(word)}</span>`;  // a span wraps with its sentence; a button would not
const tb = word => termOf(word) ? termBtn(termOf(word), word) : esc(word);  // one word of the page's own sentences

/* Text from the board, escaped. Item ids become links, in results the numbers are set heavier, and where the text is
   shown in full the first occurrence of each glossary term becomes a button. */
function rich(text, { links = true, numbers = false, terms = false } = {}) {
  const part = s => esc(s).replace(ID, (all, id, n) => id ? (links ? `<a class="ref" href="#${id}">${id}</a>` : id) : numbers ? `<span class="n">${n}</span>` : n);
  if (!terms || !SPELL.size) return part(text);
  const used = new Set();
  let out = "", at = 0;
  for (const m of String(text).matchAll(TERM)) {
    const t = termOf(m[0]);
    if (!t || used.has(t.term)) continue;
    used.add(t.term);
    out += part(text.slice(at, m.index)) + termBtn(t, m[0]);
    at = m.index + m[0].length;
  }
  return out + part(text.slice(at));
}
function showDef(btn) {
  const was = S.term;
  hideDef();
  if (was === btn) return;
  const t = GLOSSARY.find(g => g.term === btn.dataset.term), d = $("def");
  if (!t) return;
  S.term = btn;
  d.innerHTML = `<b>${esc(t.term)}</b> ${esc(t.definition)}`;
  d.hidden = false;
  btn.setAttribute("aria-expanded", "true");
  btn.setAttribute("aria-describedby", "def");
  const r = btn.getBoundingClientRect(), w = d.offsetWidth, h = d.offsetHeight;
  const below = r.bottom + 8 + h <= innerHeight || r.top - 8 - h < 0;
  d.style.left = Math.max(16, Math.min(innerWidth - 16 - w, r.left)) + "px";
  d.style.top = (below ? r.bottom + 8 : r.top - 8 - h) + "px";
}
function hideDef() {
  if (!S.term) return;
  S.term.setAttribute("aria-expanded", "false");
  S.term.removeAttribute("aria-describedby");
  S.term = null;
  $("def").hidden = true;
}

/* One line for an item: the title an agent wrote for a result (board.py plain), else the first clause of its text. */
const plain = () => S.data?.plain ?? {};
const body = text => String(text).split("\n").filter(l => l.trim() && !META.test(l.trim())).join("\n");
function clause(text) {
  const t = body(text).replace(/\s*\b(?:idea|work|result|knowledge|skill)-[0-9a-f]{6}\b/g, "").replace(/\s*\([^)]*\)/g, "").replace(/(?:\s*,)+/g, ",").trim();
  const m = /: |; |\. |\? |\n/.exec(t.slice(16));
  return (m ? t.slice(0, 16 + m.index) : t).replace(/[.:;]$/, "");
}
const sentence = text => { const t = body(text), m = /[.?!] (?=[A-Z])|\n/.exec(t.slice(40)); return m ? t.slice(0, 41 + m.index).trim() : t; };
const firstSentence = text => text.split(/(?<=[.?!])\s+(?=[A-Z])/)[0];
const title = i => (i.kind === "result" && plain()[i.id]?.title) || clause(i.text);
const announcement = i => i.kind === "result" && !S.scores.has(i.id) && ANNOUNCE.test(i.text.slice(0, 160));

const match = (...fields) => (!S.q || fields.join("\n").toLowerCase().includes(S.q));
const shown = i => (!S.who || i.who === S.who) && match(i.id, i.text, i.who, i.branch, plain()[i.id]?.title ?? "");
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

function row(i) {
  const open = i.listed === "work", closed = i.listed === "work-closed";
  const idle = open ? mins(activeNs(i)) : 0, late = idle >= 60, t = closed ? i.closed_ns ?? 0 : i.at_ns;
  const glyph = open ? "ring" : closed ? "ring shut" : i.kind === "result" && !announcement(i) ? "" : "small";
  const right = open ? `<span class="r${late ? " late" : ""}">${late ? "idle " : ""}${durHM(idle)}</span>`
    : `<span class="r${!closed && mins(t) < 10 ? " fresh" : ""}">${closed ? "closed " : ""}${rel(t)}</span>`;
  const cls = ["row", i.kind, late && "late", closed && "shut", S.open === i.id && "current", isNew(i.id) && "arrived", S.changed.has(i.id) && "new"];
  return `<article class="${cls.filter(Boolean).join(" ")}" style="${pstyle(i.who)}" data-key="${esc(i.id)}">` +
    `<a class="open" href="#${esc(i.id)}"><i class="g ${glyph}"></i><span class="t">${esc(title(i))}</span>${right}<span class="sr">, ${esc(i.who)}</span></a></article>`;
}

function message(m) {
  const full = S.full.has(m.sk), cls = ["msg", isNew(m.sk) && "arrived", full && "full"];
  return `<article class="${cls.filter(Boolean).join(" ")}" style="${pstyle(m.who)}" data-key="${esc(m.sk)}" tabindex="0">` +
    `<i class="g tick"></i><div class="t"><b>${esc(m.who)}</b> ${rich(m.text, { links: full })}</div><span class="r">${rel(msgNs(m))}</span></article>`;
}

function list(id, key, items, total, empty, draw = row) {
  const cut = filtering() || S.all.has(key) || !LIMIT[id] ? items : items.slice(0, LIMIT[id]);
  putRows($(id), cut.map(i => [i.id ?? i.sk, draw(i)]), `<p class="empty">${empty}</p>`);
  put($(id + "-all"), cut.length < items.length ? `<button class="all" data-all="${key}">Show all ${items.length}</button>` : "");
  return filtering() ? `${items.length} of ${total}` : String(total);
}

function render() {
  const d = S.data;
  const anchor = readingAnchor(), before = anchor?.getBoundingClientRect().top;
  const focused = document.activeElement?.closest("[data-key]")?.dataset.key, fkey = document.activeElement?.dataset?.fkey;
  status();
  if (!d) return;
  $("test").hidden = !d.test;

  people = [...new Set([...d.items, ...d.messages].map(r => r.who))].sort();
  S.scores = new Map();
  (d.scores || []).forEach(s => S.scores.set(s.result, [...(S.scores.get(s.result) || []), s]));
  S.benches = benches(d.scores || []);
  const items = d.items.map(i => ({ ...i, closed_ns: i.closed_at ? Date.parse(i.closed_at) * 1e6 : null }));
  S.item = new Map(items.map(i => [i.id, i]));
  if (document.visibilityState === "visible" && document.hasFocus()) S.lookedAt = d.now_ns;  // the reader saw this read
  const ch = changed(items);
  S.changed = new Set([...ch.result, ...ch.closed, ...ch.idle].map(i => i.id));
  const of = kinds => items.filter(i => kinds.includes(i.listed));
  const by = (all, order) => { all.sort(order); return [all.filter(shown), all.length]; };
  const newest = (a, b) => b.at_ns - a.at_ns;
  const records = new Set(S.benches.flatMap(b => b.pts.filter(q => q.rec).map(q => q.s.result)));  // these results are the ladder
  const results = of(["result"]).filter(i => !records.has(i.id));
  const [work, nWork] = by(of(["work"]), (a, b) => activeNs(a) - activeNs(b));  // longest idle first; a row crossing an hour does not move
  const idleN = work.filter(i => mins(activeNs(i)) >= 60).length;
  const lists = {
    result: by(results.filter(i => !announcement(i)), newest),
    tools: by(results.filter(announcement), newest),
    idea: by(of(["idea"]), newest),
    knowledge: by(of(["knowledge", "skill"]), newest),
    closed: by(of(["work-closed"]), (a, b) => (b.closed_ns ?? 0) - (a.closed_ns ?? 0)),
  };
  const talk = d.messages.filter(m => (!S.who || m.who === S.who) && match(m.text, m.who, m.branch)).reverse();
  const autos = talk.filter(m => AUTO.test(m.text)).length, nAutos = d.messages.filter(m => AUTO.test(m.text)).length;
  const none = filtering() ? "Nothing matches the filter." : "";

  hero();
  summary(items, ch);
  put($("people"), people.map(p => `<button data-who="${esc(p)}" data-fkey="who-${esc(p)}" aria-pressed="${S.who === p}" style="${pstyle(p)};--c:oklch(var(--pl) var(--pc) var(--h))"><i class="g"></i>${esc(p)}</button>`).join(""));
  $("people").classList.toggle("picked", Boolean(S.who));

  const nw = list("work", "work", S.idle ? work.filter(i => mins(activeNs(i)) >= 60) : work, nWork, none || "No open work. An agent claims work with <code>board.py post work</code>.");
  put($("n-work"), nWork ? nw : "");
  put($("n-result"), list("result", "result", lists.result[0], lists.result[1], none || "No results yet."));

  const count = { msgs: [S.autos ? talk.length : talk.length - autos, d.messages.length - (S.autos ? 0 : nAutos)] };
  Object.keys(lists).forEach(k => { count[k] = [lists[k][0].length, lists[k][1]]; });
  put($("tabs"), `<span class="lab">More</span>` + MORE.map(([k, name]) => `<button data-more="${k}" data-fkey="more-${k}" aria-pressed="${S.more === k}">${name} ` +
    `<span class="count">${k === "activity" ? `${d.hours} h` : filtering() ? `${count[k][0]} of ${count[k][1]}` : count[k][1]}</span></button>`).join(""));
  const more = $("more"), head = $("more-head");
  more.classList.toggle("cols2", Boolean(lists[S.more]) && S.more !== "result");
  if (S.more === "activity") {
    put(head, ""); put($("more-all"), "");
    put(more, lanes(items, d));
  } else if (S.more === "msgs") {
    put(head, autos ? `<button id="autos" data-fkey="autos" aria-pressed="${S.autos}">${S.autos ? "Hide" : "Show"} ${autos} announcement${autos > 1 ? "s" : ""} of board.py</button>` : "");
    list("more", "msgs", S.autos ? talk : talk.filter(m => !AUTO.test(m.text)), count.msgs[1], none || `No messages on all in the last ${d.hours} h.`, message);
  } else if (lists[S.more]) {
    put(head, S.more === "tools" ? "Results that announce a page, a tool or a skill. The page tells them apart by their words, so a few may be in the wrong list." : "");
    list("more", S.more, lists[S.more][0], lists[S.more][1], none || "Nothing here yet.");
  } else { put(head, ""); put($("more-all"), ""); put(more, ""); }

  const open = items.filter(i => i.listed === "work");
  put($("live"), `${open.length} open work items, ${idleN} idle over an hour, ${items.filter(i => i.kind === "result").length} results.`);  // changes only with the counts
  S.seen = new Set([...d.items.map(i => i.id), ...d.messages.map(m => m.sk)]);
  if (S.term && !S.term.isConnected) { S.term = null; $("def").hidden = true; }
  if (focused && !document.activeElement?.closest("[data-key]")) document.querySelector(`[data-key="${CSS.escape(focused)}"] .open, .msg[data-key="${CSS.escape(focused)}"]`)?.focus({ preventScroll: true });
  if (fkey && document.activeElement?.dataset?.fkey !== fkey) document.querySelector(`[data-fkey="${CSS.escape(fkey)}"]`)?.focus({ preventScroll: true });
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

/* The one sentence: open work, the people behind it, how many are idle over an hour (a click shows only those), the last
   result (a click opens it). Above it, what changed since the reader's last look. */
function summary(items, ch) {
  const open = items.filter(i => i.listed === "work");
  const idle = open.filter(i => mins(activeNs(i)) >= 60).length;
  const ppl = new Set(open.map(i => i.who)).size;
  const last = items.filter(i => i.kind === "result").sort((a, b) => b.at_ns - a.at_ns)[0];
  put($("summary"), (open.length
      ? `${plural(open.length, "open work item")} from ${plural(ppl, "person", "people")}, ` +
        (idle ? `<button class="warn" id="idlebtn" data-fkey="idle" aria-pressed="${S.idle}"><b>${idle}</b> idle over an hour</button>.` : "none idle over an hour.")
      : "No open work.") +
    (last ? ` <a href="#${esc(last.id)}" data-fkey="last">Last result ${mins(last.at_ns) < 1 ? "just now" : `<b>${rel(last.at_ns)}</b> ago`}</a> from ${esc(last.who)}.` : " No results yet."));
  const el = $("since");
  if (!S.since) { el.hidden = true; document.title = TITLE; return; }
  const parts = [[ch.result.length, "result"], [ch.closed.length, "closed", "closed"], [ch.idle.length, "newly idle", "newly idle"]].filter(p => p[0]);
  const count = parts.reduce((a, p) => a + p[0], 0);
  el.hidden = false;
  el.classList.toggle("fresh", count > 0);
  put(el, count ? `Since ${clock(S.since / 1e6)}: ${parts.map(p => plural(...p)).join(", ")}.` : `Nothing new since ${clock(S.since / 1e6)}.`);
  document.title = count && !S.acked ? `(${count}) ${TITLE}` : TITLE;
}

/* The scores of one benchmark: every untrained-base attempt in the order posted, the record steps among them, the best RL score. */
const note = /\s*\(.*?\)/g;  // a parenthesised note on a configuration, such as "(reference, job 151534-e72c)"
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
  return bs;
}
const bench = () => S.benches.find(b => b.name === S.bench) ?? S.benches[0];
const stepOf = b => S.step && b.pts.find(q => q.rec && String(q.s.right) === S.step);

/* The words of a record step: the plain row of its score, else the plain row of its result when that result holds no
   other step of this benchmark (two steps of one result would otherwise show the same words). */
function words(q, b) {
  const p = plain(), own = p[`${q.s.result}#${b.name}#${q.s.right}/${q.s.n}`];
  return own ?? (b.pts.filter(x => x.rec && x.s.result === q.s.result).length === 1 ? p[q.s.result] : null) ?? {};
}
/* Without those words: what the configuration gained and lost against the step before. Parts are split at ", " and " / ";
   a part that only got longer or shorter shows the words that changed. */
const parts = c => c.replace(note, "").split(/,\s+|\s+\/\s+/).map(s => s.trim()).filter(Boolean);
function configDiff(q) {
  const a = parts(q.s.config), b = parts(q.prev.s.config);
  let added = a.filter(p => !b.includes(p)), removed = b.filter(p => !a.includes(p));
  added = added.map(x => { const y = removed.find(y => x.startsWith(y + " ")); if (y) removed = removed.filter(r => r !== y); return y ? x.slice(y.length).trim() : x; })
    .filter(x => { const y = removed.find(y => y.startsWith(x + " ")); if (y) removed = removed.map(r => r === y ? y.slice(x.length).trim() : r); return !y; });
  return { added, removed };
}
function stepTitle(q, b) {
  const w = words(q, b);
  if (w.title) return w.title;
  if (!q.prev) return cap(q.s.config.replace(note, ""));
  const { added: all, removed } = configDiff(q), main = all.filter(p => !/^(?:T|top-p|min-p) [\d.]+$/.test(p)), added = main.length ? main : all;  // a sampling setting names the step only when nothing else was added
  return added.length ? cap(added.join(", ")) : removed.length ? "Without " + removed.join(", ") : cap(q.s.config.replace(note, ""));
}
const rawOf = id => S.item.get(id)?.text ?? S.data.finding?.[id] ?? "";

function hero() {
  const b = bench();
  if (!b) {
    put($("benches"), "");
    put($("reach"), `<p class="lab">No scores yet. Attach one to a result: <code>board.py score &lt;result id&gt; base MATH-500 410/500 "cue, T 1.0"</code></p>`);
    put($("chart"), ""); put($("ladder"), ""); put($("n-steps"), "");
    return;
  }
  put($("benches"), S.benches.length > 1 ? S.benches.map(x =>
    `<button data-bench="${esc(x.name)}" data-fkey="bench-${esc(x.name)}" aria-pressed="${x === b}">${esc(x.name)} <b>${f1(x.lead.p)}</b></button>`).join("") : "");
  put($("n-steps"), `${esc(b.name)}, newest first`);
  drawReach();
  ladder(b);
  drawChart();
}

/* Reach: one thin bar from 0 % to the best RL score (to the base score when that is higher, to 100 without an RL score).
   One segment per record step, from the step before to its score; a step within noise is drawn faint, as on the chart.
   The empty rest is what is still missing to RL. A segment opens its step like its line in the ladder. */
let measure13;
const width13 = t => { measure13 ??= document.createElement("canvas").getContext("2d"); measure13.font = '400 13px "Archivo", ui-sans-serif, system-ui, sans-serif'; return measure13.measureText(t).width; };
function drawReach() {
  const el = $("reach"), b = S.benches && bench(), W = el.clientWidth;
  if (!b || !W) return;
  const { lead, rl, rlP } = b, sel = stepOf(b), recs = b.pts.filter(q => q.rec);
  const top = rl ? Math.max(rlP, lead.p) : 100, at = v => v / top * 100, px = v => v / top * W;
  const matched = rl && lead.p >= rlP - .05, full = lead.p >= top - .05;  // full: no empty rest is drawn
  const segs = recs.map((q, k) => {
    const from = q.prev ? q.prev.p : 0, noise = q.prev && !q.clears, last = k === recs.length - 1 && full;
    const name = q.prev ? `+${f1(q.p - q.prev.p)}` : `start ${f1(q.p)}`, w = px(q.p - from);
    const label = `${q.prev ? `Step +${f1(q.p - q.prev.p)}` : "Start"}, ${stepTitle(q, b)}, ${q.prev ? `${f1(from)} to ${f1(q.p)}` : f1(q.p)}${noise ? ", within noise" : ""}`;
    const cls = ["piece", !k && "first", last && "last", noise && "noise", q === sel && "on"].filter(Boolean).join(" ");
    const hx = w < 12 ? `--hx:${((w - 12) / 2).toFixed(1)}px;z-index:1;` : "";  // a sliver gets a hit area 12 px wide
    return { q, k, from, name, w, html: `<button class="${cls}" style="left:${at(from).toFixed(3)}%;width:${at(q.p - from).toFixed(3)}%;${hx}" data-step="${q.s.right}" data-fkey="reach-${q.s.right}" aria-label="${esc(label)}" aria-expanded="${q === sel}"><i></i></button>` };
  });
  const rest = !full ? `<span class="piece togo last" style="left:${at(lead.p).toFixed(3)}%;width:${at(top - lead.p).toFixed(3)}%"><i></i></span>` : "";
  const go = rl ? (matched ? "RL matched" : `${f1(rlP - lead.p)} points to go`) : "", goW = go ? width13(go) : 0;
  const marks = segs.map(s => {  // a gain under its segment where it fits and stays clear of the note at the right end
    const tw = width13(s.name), x = s.k ? Math.min(px(s.from) + s.w / 2 - tw / 2, W - (go ? goW + 12 : 0) - tw) : 0;  // centred, or moved left of the note
    if (s.w < tw + 10 || x < (s.k ? px(s.from) + 2 : 0)) return "";
    return `<span style="left:${x.toFixed(1)}px">${s.name}</span>`;
  }).join("") + (go ? `<span style="right:0">${go}</span>` : "");
  put(el, `<div class="ends"><span class="big base">${f1(lead.p)}</span><span class="lab">untrained base</span>` +
    (rl ? `<span class="rl-end"><span class="lab">RL-trained</span><span class="big">${f1(rlP)}</span></span>` : "") + `</div>` +
    `<div class="bar8" role="group" aria-label="${esc(`${b.name}: best base ${f1(lead.p)} %${rl ? `, RL ${f1(rlP)} %` : ", no RL score"}; one part per record step`)}">${rest}<div class="fill">${segs.map(s => s.html).join("")}</div></div>` +
    `<div class="marks" aria-hidden="true">${marks}</div>`);
  el.classList.toggle("has-sel", Boolean(sel));
  const fill = el.querySelector(".fill");
  if (S.grown !== b.name) {  // one entrance: on the first draw and when the benchmark changes, never on a refresh
    S.grown = b.name; S.grewAt = performance.now();
    fill.classList.remove("grow"); void fill.offsetWidth; fill.classList.add("grow");
  } else if (!fill.classList.contains("grow") && performance.now() - S.grewAt < 600) {  // rewritten mid-entrance (fonts, a click): it goes on where it was
    fill.style.animationDelay = `${-(performance.now() - S.grewAt).toFixed(0)}ms`; fill.classList.add("grow");
  }
}

function ladder(b) {
  const sel = stepOf(b);
  const rows = b.pts.filter(q => q.rec).reverse().map(q => {
    const noise = q.prev && !q.clears, on = q === sel, id = `step-${q.s.right}`;
    return `<button class="lrow${noise ? " noise" : ""}" data-step="${q.s.right}" data-fkey="${id}" aria-expanded="${on}"${on ? ` aria-controls="sd-${q.s.right}"` : ""}>` +
      `<b>${q.prev ? "+" + f1(q.p - q.prev.p) : "start"}</b><span class="lt">${esc(stepTitle(q, b))}</span>` +
      `<span class="lr">${q.prev ? f1(q.prev.p) + " → " : ""}${f1(q.p)}${noise ? ` <span class="flag">within noise</span>` : ""}</span><span class="chev" aria-hidden="true">›</span></button>` + (on ? detail(q, b) : "");
  });
  const ci = b.rl && diffCI(b.rl, b.lead.s);  // the 95 % interval of RL minus the best base, in points
  const rl = b.rl ? `<a class="lrow rl" href="#${esc(b.rl.result)}" data-fkey="step-rl"><b>${f1(b.rlP)}</b><span class="lt">RL-trained model, the target</span><span class="lr">gap ${f1(ci[0])} to ${f1(ci[1])}</span></a>` : "";
  put($("ladder"), rl + rows.join(""));
}

/* An opened step: what changed, why it works, whether it is real, what it costs, and its exact configuration. */
function detail(q, b) {
  const w = words(q, b), s = q.s, prev = q.prev, item = S.item.get(s.result), T = { links: false, terms: true };
  let what;
  if (w.what) what = `<p>${rich(w.what, T)}</p>`;
  else {
    const d = prev && configDiff(q), raw = sentence(rawOf(s.result));
    what = (prev ? `<p>${[d.added.length ? `Added to the configuration: ${rich(d.added.join(", "), T)}.` : "", d.removed.length ? `Removed: ${rich(d.removed.join(", "), T)}.` : ""].filter(Boolean).join(" ") ||
      "The configuration differs from the step before only in its note."}</p>` : `<p>The first base score posted on this benchmark.</p>`) +
      (raw ? `<p class="raw">From the result's text: ${rich(raw, T)}</p>` : "");
  }
  const why = w.why ? rich(w.why, T) : "No explanation in plain words is written for this step yet.";
  const real = (prev ? `${prev.s.n === s.n ? `${prev.s.right} → ${s.right} of ${s.n}` : `${prev.s.right} of ${prev.s.n} → ${s.right} of ${s.n}`}. ` +
      (q.clears ? `Larger than chance: ${f1(q.p)} % is above the ${tb("95 % interval")} of the step before (${f1(prev.ci[0])} to ${f1(prev.ci[1])}).`
                : `Too small to tell from chance: ${f1(q.p)} % is inside the ${tb("95 % interval")} of the step before (${f1(prev.ci[0])} to ${f1(prev.ci[1])}).`)
    : `${s.right} of ${s.n} right. Its ${tb("95 % interval")} is ${f1(q.ci[0])} to ${f1(q.ci[1])} %.`);
  const cost = (s.tokens ? `${num(s.tokens)} ${tb("tokens per problem")}` + (prev ? (prev.s.tokens ? `; ${num(prev.s.tokens)} at the step before.` : "; not recorded at the step before.") : ".")
    : "Tokens per problem are not recorded for this score.");
  const nc = item?.n_comments;
  return `<dl class="sd" id="sd-${s.right}"><dt>${prev ? "What changed" : "What it is"}</dt><dd>${what}</dd>` +
    `<dt>Why it works</dt><dd>${why}</dd>` +
    `<dt>Is it real</dt><dd><p>${real}</p>${w.caveat ? `<p class="cv">${rich(w.caveat, T)}</p>` : ""}</dd>` +
    `<dt>Cost</dt><dd>${cost} <a class="go" href="#${esc(s.result)}">Raw result${nc ? ` and ${nc} comment${nc > 1 ? "s" : ""}` : ""}</a></dd>` +
    `<dt>Settings</dt><dd class="set">${rich(s.config, T)}</dd></dl>`;
}

/* Hill chart */
let measure;
function textWidth(t) {
  measure ??= document.createElement("canvas").getContext("2d");
  measure.font = '400 11.5px "Archivo", ui-sans-serif, system-ui, sans-serif';
  return measure.measureText(t).width;
}
function drawChart() {
  const el = $("chart"), b = S.benches && bench();
  if (b && el.clientWidth) put(el, chart(b, el.clientWidth, el.clientHeight - (small.matches ? KEY_H * 2 - 4 : KEY_H), small.matches) + chartKey());
}

/* The key under the chart, drawn with the chart's own marks */
const KEY_H = 24;  // the height of the key's one line and its margin, taken from the chart's height (two lines on a narrow screen)
const glyph = inner => `<svg width="12" height="12" viewBox="-6 -6 12 12" aria-hidden="true">${inner}</svg>`;
const chartKey = () => `<p class="ckey">` +
  `<span>${glyph('<circle class="dot rec" r="4.5" style="stroke-width:0"/>')}record</span>` +
  `<span>${glyph('<circle class="dot" r="3"/>')}other attempt</span>` +
  `<span>${glyph('<path class="x" d="M-3.5,-3.5l7,7m0,-7l-7,7"/>')}plain prompt, no cue</span>` +
  `<span>${glyph('<line class="ci" x1="0" x2="0" y1="-6" y2="6" style="opacity:1"/>')}95 % interval</span></p>`;
function chart(b, W, H, narrow) {
  const { pts, lead, rl, rlP } = b, sel = stepOf(b);
  const { lo, hi } = b, T = 18, B = 24, L = narrow ? 26 : 30, R = 60;
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
  const on = q => q === sel ? " on" : "";

  const svg = [];
  for (let v = lo; v <= hi; v += 10) {
    svg.push(`<line class="grid" x1="${L}" x2="${W - R}" y1="${y(v)}" y2="${y(v)}"/>`);
    svg.push(`<text x="${L - 8}" y="${y(v) + 4}" text-anchor="end">${v}</text>`);
  }
  svg.push(`<text x="${L - 8}" y="${T - 9}" text-anchor="end">%</text>`);

  const recs = pts.filter(q => q.rec), shownRecs = recs.filter(q => q.p >= lo);  // a best below the floor has no tread
  const first = shownRecs[0], start = first.prev ? x(first.i) : L;
  const step = [[start, y(first.p)]];
  shownRecs.forEach((q, k) => { if (k) step.push([x(q.i), y(q.prev.p)], [x(q.i), y(q.p)]); });
  step.push([W - R, y(lead.p)]);
  if (rl) {
    const top = y(rlP), poly = [[start, top], [W - R, top], ...step.slice().reverse().map(([px, py]) => [px, Math.max(py, top)])];
    svg.push(`<path class="gap" d="M${poly.map(p => p.map(n => n.toFixed(1)).join(",")).join("L")}Z"/>`);
    svg.push(`<line class="target" x1="${L}" x2="${W - R}" y1="${top}" y2="${top}"/>`);
    boxes.push({ x0: W - R + 4, x1: W, y0: top - 9, y1: top + 5 }, { x0: L, x1: W - R, y0: top - 1.5, y1: top + 1.5 });
    svg.push(`<a href="#${esc(rl.result)}" aria-label="${esc(`RL, ${rl.config}: ${rl.right} of ${rl.n}, ${rl.result}`)}">` +
      `<text class="rl" x="${W - R + 8}" y="${top + 4}">RL <tspan>${f1(rlP)}</tspan></text></a>`);
  }
  recs.forEach((q, k) => {
    const x1 = k ? x(q.i) : L, x2 = recs[k + 1] ? x(recs[k + 1].i) : W - R;
    if (q.p >= lo) {
      svg.push(`<line class="tread${on(q)}" x1="${x1}" x2="${x2}" y1="${y(q.p)}" y2="${y(q.p)}"/>`);
      boxes.push({ x0: x1, x1: x2, y0: y(q.p) - 2, y1: y(q.p) + 2 });
    }
    if (!k) return;
    boxes.push({ x0: x(q.i) - 2, x1: x(q.i) + 2, y0: y(q.p), y1: y(q.prev.p) });
    svg.push(`<line class="rise${q.clears ? "" : " noise"}${on(q)}" x1="${x(q.i)}" x2="${x(q.i)}" y1="${y(q.prev.p)}" y2="${y(q.p)}"/>`);
    if (q.prev.p < lo) {  // the rise starts below the floor: an axis break where it leaves the chart
      const bx = x(q.i), by = y(lo) - 6;
      svg.push(`<path class="brk" d="M${bx - 5},${by + 2}l10,-4"/><path class="brk-line" d="M${bx - 5},${by}l10,-4M${bx - 5},${by + 4}l10,-4"/>`);
    }
  });

  const marks = pts.map(q => {
    const cx = x(q.i), cy = y(q.p), clipped = q.p < lo;
    boxes.push({ x0: cx - 7, x1: cx + 7, y0: cy - 7, y1: cy + 7 });
    if (!clipped) boxes.push({ x0: cx - 1.5, x1: cx + 1.5, y0: y(q.ci[1]), y1: y(q.ci[0]) });
    const ci = clipped ? "" : `<line class="ci${q.rec ? " rec" : ""}${on(q)}" x1="${cx}" x2="${cx}" y1="${y(q.ci[1])}" y2="${y(q.ci[0])}"/>`;
    const tip = `${q.s.config}: ${q.s.right} of ${q.s.n} (${f1(q.p)} %, 95% ${f1(q.ci[0])} to ${f1(q.ci[1])})` +
      `${q.s.tokens ? `, ${num(q.s.tokens)} tokens per problem` : ""}, ${q.s.who}, ${q.s.result}`;
    const x7 = `<circle class="under" cx="${cx}" cy="${cy}" r="4.5"/><path class="x" d="M${cx - 3.5},${cy - 3.5}l7,7m0,-7l-7,7"`;
    const mark = q.plain && !q.rec ? `${x7}/>` : q.plain ? `${x7} style="stroke:var(--blue)"/>`
      : `<circle class="dot${q.rec ? " rec" : ""}" cx="${cx}" cy="${cy}" r="${q.rec ? 4.5 : 3}"/>`;
    const to = q.rec ? `href="${esc(address({ step: String(q.s.right) }))}" data-step="${q.s.right}" data-keep="1"` : `href="#${esc(q.s.result)}"`;  // a record opens its step, any other attempt its result
    return { ci, a: `<a class="mark${on(q)}" ${to} aria-label="${esc(tip)}"><circle class="hit" cx="${cx}" cy="${cy}" r="9"/>${mark}</a>` };
  });

  const caption = `${pts.length} attempt${pts.length > 1 ? "s" : ""} in the order posted`;
  boxes.push({ x0: W - R - textWidth(caption), x1: W - R, y0: H - 14, y1: H });
  out.push(`<text class="quiet" x="${W - R}" y="${H - 4}" text-anchor="end">${caption}</text>`);
  label(f1(lead.p), "lead", [0, 14, -14, 28].map(dy => [W - R + 8, y(lead.p) + 4 + dy, "start"]), true);  // the best base score, at the end of its line
  recs.forEach(q => {  // a record that clears the interval of the one before: its gain
    if (!q.prev || !q.clears) return;
    const xr = x(q.i), mid = (y(q.prev.p) + y(q.p)) / 2 + 4, text = `+${f1(q.p - q.prev.p)}`;
    const spots = [0, -14, 14, -28, 28].flatMap(dy => [[xr + 8, mid + dy, "start"], [xr - 8, mid + dy, "end"]]);
    label(text, "gain", [...spots, [xr + 8, y(q.p) - 10, "start"], [xr - 8, y(q.p) - 10, "end"], [xr + 8, y(q.p) + 18, "start"]], true);
  });
  pts.filter(q => q.p < lo).forEach(q =>  // below the floor: say its value
    label(`↓ ${f1(q.p)}`, "quiet", [[x(q.i), y(q.p) + 20, "middle"], [x(q.i) - 5, y(q.p) + 20, "start"], [x(q.i) + 12, y(q.p) + 4, "start"]], true));

  return `<svg class="${sel ? "has-sel" : ""}" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="group" aria-label="${esc(b.name)}: best base ${f1(lead.p)} %, RL ${rl ? f1(rlP) + " %" : "not measured"}">` +
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
  return lanePeople.map(p => {
    const marks = events.filter(e => e.who === p).map(e => {
      if (e.msg) return `<span class="mk tick" style="left:${x(e.ns)}"></span>`;
      const i = e.item, k = i.kind === "result" ? "res" : i.kind === "work" ? "claim" : "idea";
      return `<a class="mk ${k}" style="left:${x(e.ns)}" href="#${esc(i.id)}" tabindex="-1" aria-label="${esc(`${i.id}, ${rel(e.ns)} ago: ${title(i)}`)}"></a>`;
    }).join("");
    const cls = S.who ? (S.who === p ? "on" : "off") : "";
    return `<div class="lane ${cls}" style="${pstyle(p)}"><button data-who="${esc(p)}"><i class="g"></i>${esc(p)}</button>` +
      `<div class="track" style="--hour:calc(100% / ${hours})">${marks}</div></div>`;
  }).join("") + (lanePeople.length ? `<div class="axis"><i></i><div>${
    Array.from({ length: Math.floor(hours) + 1 }, (_, h) => `<span style="left:${(100 - h / hours * 100).toFixed(3)}%">${h ? h + "h ago" : "now"}</span>`)
      .reverse().join("")}</div></div>` : `<p class="empty">No posts or messages in the last ${hours} h.</p>`);
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
    const i = base, d = S.detail, T = { links: false, terms: true };
    const open = i.listed === "work", idle = mins(activeNs(i));
    const state = open ? `${KINDS.work}, ${idle ? "idle " + dur(idle) : "active now"}` :
      i.listed === "work-closed" ? `Closed by ${esc(i.closed_by)} ${when(Date.parse(i.closed_at) * 1e6, " ago")}` : KINDS[i.kind];
    const w = i.kind === "result" ? d?.plain?.[i.id] ?? plain()[i.id] : null;  // the whole plain row comes with the item; its title is on the board already
    const part = (name, text, cls = "") => text ? `<dt>${name}</dt><dd${cls}>${rich(text, T)}</dd>` : "";
    const said = !w ? "" : (w.title ? `<p class="lead">${esc(w.title)}</p>` : "") +
      (w.what || w.why || w.caveat ? `<dl class="sd">${part("What", w.what)}${part("Why", w.why)}${part("Caveat", w.caveat, ' class="cv"')}</dl>` : "");
    const votes = d ? d.votes.map(v => `${esc(v.who)} ${v.vote > 0 ? "+" : "−"}`).join(", ") : "";
    const scores = (S.scores?.get(i.id) || []).map(s => `<p>${esc(s.model)} ${esc(s.benchmark)} <b class="n">${s.right}/${s.n}</b>, ${f1(100 * s.right / s.n)} % ` +
      `<small>${esc(s.config)}${s.tokens ? `, ${num(s.tokens)} tokens per problem` : ""}</small></p>`).join("");
    const facts = [
      ...(scores ? [["Scores", scores]] : []),
      ["Posted by", `<span class="who" style="${pstyle(i.who)}">${esc(i.who)}</span>`], ["Branch", esc(i.branch || "not recorded")],
      ["Agent", esc([i.agent, (i.session || "").slice(0, 8)].filter(Boolean).join(", ") || "not recorded")],
      ["Posted", `${when(i.at_ns, " ago")}, ${utc(i.at_ns)}`],
      ["Votes", `+${i.ups} −${i.downs}${votes ? ": " + votes : ""}`],
    ].map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("");
    const thread = (name, rows, empty) => `<h3>${name} <span>${d ? rows.length : ""}</span></h3>` + (!d ? `<p class="note">Reading</p>` :
      rows.length ? `<div class="msgs">${rows.map(r => `<div class="pmsg" style="${pstyle(r.who)}"><div class="meta"><b>${esc(r.who)}</b>` +
        `${when(Date.parse(r.at) * 1e6, " ago")}</div><div class="text">${rich(r.text)}</div></div>`).join("")}</div>` : `<p class="note">${empty}</p>`);
    html = head(i.id, state, open && idle >= 60) + `<div class="pbody">${said}` +
      (said ? `<h3>Raw text</h3>` : "") + `<p class="full${said ? "" : " only"}">${rich(i.text, { numbers: i.kind === "result", terms: true })}</p>` +
      `<dl class="facts">${facts}</dl>` +
      thread("Comments", d?.comments ?? [], "No comments.") +
      thread("Messages on this item", d?.thread ?? [], `No messages sent to ${esc(i.id)}.`) + "</div>";
  }
  panel.hidden = false;
  if (panel._html === html || selecting(panel)) return;
  const scroll = panel.scrollTop, focused = panel.contains(document.activeElement) && document.activeElement.id;
  put(panel, html);
  panel.scrollTop = scroll;
  if (focused) $(focused)?.focus({ preventScroll: true });
  if (S.term && !S.term.isConnected) { S.term = null; $("def").hidden = true; }
}

const head = (id, state, warn) => `<div class="phead"><div><h2 id="ptitle" tabindex="-1">${esc(id)}</h2>` +
  `<span class="kind${warn ? " warn" : ""}">${state}</span><span class="actions">` +
  `<button id="copy">Copy link</button><button id="close">Close</button></span></div></div>`;

function fromHash() {
  const id = decodeURIComponent(location.hash.slice(1)) || null;
  if (id === S.open) return;
  const was = S.open;
  hideDef();
  S.open = id; S.detail = null;
  document.querySelectorAll(".row.current").forEach(r => r.classList.remove("current"));
  if (id) document.querySelector(`.row[data-key="${CSS.escape(id)}"]`)?.classList.add("current");
  renderPanel();
  if (!id) { if (was) document.querySelector(`[data-key="${CSS.escape(was)}"] .open`)?.focus({ preventScroll: true }); return; }
  if (!was) $("ptitle").focus({ preventScroll: true });  // opened from the board: focus moves into the panel
  loadDetail().then(renderPanel);
}

function closePanel() { history.pushState(null, "", location.pathname + location.search); fromHash(); }

/* Every state is in the address, beside the open item: /?bench=hard328&step=164&more=idea&who=frustea&q=cue&idle=1#result-8b1c48 */
function address(over = {}) {
  const v = { bench: S.bench, step: S.step, more: S.more, who: S.who, q: $("q").value.trim(), idle: S.idle, ...over }, p = new URLSearchParams();
  ["bench", "step", "more", "who", "q"].forEach(k => { if (v[k]) p.set(k, v[k]); });
  if (v.idle) p.set("idle", "1");
  const qs = p.toString();
  return location.pathname + (qs ? "?" + qs : "") + location.hash;
}
function set(change) {
  hideDef();
  Object.assign(S, change);
  history.replaceState(null, "", address());
  render();
}

/* Keys: j and k walk every visible line; 1 2 3 jump to the record steps, Now and Learned */
const walk = () => [...document.querySelectorAll("#ladder .lrow, #work .open, #result .open, #more .open, #more .msg")];
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
  const term = t.closest(".term");
  if (term) { e.preventDefault(); showDef(term); return; }
  if (!t.closest("#def")) hideDef();
  const step = t.closest("[data-step]");
  if (step) {  // a ladder line and a segment of the reach bar close their own step on a second click; the chart only opens
    e.preventDefault();
    const n = step.dataset.step, keep = step.dataset.keep;
    set({ step: S.step === n && !keep ? null : n });
    if (keep) document.querySelector(`.lrow[data-step="${CSS.escape(n)}"]`)?.focus({ preventScroll: true });
    $("sd-" + n)?.scrollIntoView({ block: "nearest" });  // the whole opened step, when it reaches below the screen
    return;
  }
  const b = t.closest("[data-bench]");
  if (b) return set({ bench: b.dataset.bench === S.benches[0]?.name ? null : b.dataset.bench, step: null });
  const more = t.closest("[data-more]");
  if (more) return set({ more: S.more === more.dataset.more ? null : more.dataset.more });
  const person = t.closest("[data-who]");
  if (person) return set({ who: S.who === person.dataset.who ? null : person.dataset.who });
  if (t.closest("#idlebtn")) return set({ idle: !S.idle });
  const all = t.closest("[data-all]");
  if (all) { S.all.add(all.dataset.all); render(); return; }
  if (t.closest("#autos")) { S.autos = !S.autos; render(); return; }
  if (t.closest("#close") || t.closest("#scrim")) { closePanel(); return; }
  if (t.closest("#copy")) {
    navigator.clipboard.writeText(location.href).then(() => { $("copy").textContent = "Copied"; });
    return;
  }
  const m = t.closest("#more .msg");
  if (m && !t.closest("a, button") && getSelection().isCollapsed) toggleFull(m);
});
function toggleFull(m) {
  const k = m.dataset.key;
  S.full.has(k) ? S.full.delete(k) : S.full.add(k);
  render();
}
document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.target.matches?.(".term") && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); showDef(e.target); return; }
  if (e.target === $("q")) {
    if (e.key === "Escape") { $("q").value = ""; set({ q: "" }); $("q").blur(); }
    if (e.key === "Enter" || e.key === "ArrowDown") { e.preventDefault(); $("q").blur(); go(document.querySelector("#work .open, #result .open, #more .open, #more .msg")); }
    return;
  }
  const inPanel = e.target.closest?.("#panel");
  if (e.key === "/") { e.preventDefault(); $("q").scrollIntoView({ block: "center" }); $("q").focus(); $("q").select(); }
  else if (e.key === "?") { $("keys").hidden = !$("keys").hidden; }
  else if (e.key === "Escape") {
    if (S.term) { const b = S.term; hideDef(); b.focus(); }
    else if (!$("keys").hidden) $("keys").hidden = true;
    else if (S.open) closePanel();
    else if (S.step) set({ step: null });
    else if (S.idle || S.who) set({ idle: false, who: null });
  }
  else if (e.key === "j" || (e.key === "ArrowDown" && !inPanel)) { e.preventDefault(); move(1); }
  else if (e.key === "k" || (e.key === "ArrowUp" && !inPanel)) { e.preventDefault(); move(-1); }
  else if ("123".includes(e.key) && e.key.length === 1) go(document.querySelector({ 1: "#ladder .lrow[data-step]", 2: "#work .open", 3: "#result .open" }[e.key]));
  else if (e.key === "Enter" && e.target.matches?.("#more .msg")) toggleFull(e.target);
});
$("q").addEventListener("input", () => set({ q: $("q").value.trim().toLowerCase() }));
addEventListener("hashchange", fromHash);
addEventListener("scroll", hideDef, { passive: true, capture: true });
addEventListener("pointermove", e => { S.pointer = { x: e.clientX, y: e.clientY }; }, { passive: true });
new ResizeObserver(() => { hideDef(); drawChart(); }).observe($("chart"));
new ResizeObserver(() => drawReach()).observe($("reach"));
small.addEventListener("change", () => S.data && render());
document.fonts.ready.then(() => { drawChart(); drawReach(); });

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
S.bench = params.get("bench"); S.step = params.get("step"); S.more = MORE.some(m => m[0] === params.get("more")) ? params.get("more") : null;
$("q").value = params.get("q") ?? ""; S.q = $("q").value.trim().toLowerCase();
S.since = Number(store.get(SEEN_KEY)) || null; S.acked = !S.since;
if (S.since) { $("since").hidden = false; $("since").innerHTML = `<span class="ph" style="width:150px;margin-top:4px"></span>`; }  // its line is held before the first read
["work", "result"].forEach(id => { $(id).innerHTML = `<span class="ph-row"><span class="ph"></span></span>`.repeat(4); });
fromHash();
poll();
</script>
</body>
</html>
"""

PAGE = PAGE.replace("__GLOSSARY__", json.dumps([{k: t[k] for k in ("term", "match", "definition")} for t in glossary.TERMS]))

if __name__ == "__main__":
    if {"--help", "-h"} & set(sys.argv):
        sys.exit(__doc__)
    team.table()  # once, before the threads of the first /data: each would build its own boto3 resource (0.84 s instead of 0.05 s)
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"board at http://127.0.0.1:{PORT}  (Ctrl-C stops it)")
    if sys.stdout.isatty():
        webbrowser.open(f"http://127.0.0.1:{PORT}")
    server.serve_forever()
