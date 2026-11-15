# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35"]
# ///
"""The board and the messages as a live web page on this laptop, read-only.

  uv run tools/view.py [--port 8765] [--hours 6]

Opens http://127.0.0.1:8765 in the browser (only when started from a terminal). The page shows one sentence on the
state of the board, one lane per person with every post and message of the last --hours, then open work (idle work
first, red after 60 minutes), results, ideas, knowledge and skills, recently closed work, and the messages on the
channel `all`. It reads /data every 10 s and updates in place. A click on an item opens its full text, votes,
comments and message thread in a side panel whose address is /#<item id>. Keys: / filter, j and k (or arrows) move,
Enter opens, Esc closes. A click on a person shows only that person.

  GET /architecture    how the harness works: one interactive picture (architecture.py), fed by the same /data
  GET /finding/<slug>  the page of one finding (finding_<slug>.py; .claude/skills/finding-page/SKILL.md)
  GET /data            the newest 60 items of each kind and list, and the messages on `all` of the last --hours (JSON)
                       and every score (board.py score), which the hill-climbing chart at the top draws
  GET /data/<item id>  one item with its votes, comments and thread (JSON); 404 for an unknown id

It reads the same DynamoDB table as board.py and msg.py, with Query only, and never writes to it or moves an agent's
message position. A failed read answers 500 with the error text, which the page shows.
"""
import glob
import importlib
import json
import os
import sys
import time
import traceback
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from boto3.dynamodb.conditions import Key

import architecture
import board
import team

PORT = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8765
HOURS = float(sys.argv[sys.argv.index("--hours") + 1]) if "--hours" in sys.argv else 6.0
LISTS = ("work", "result", "idea", "knowledge", "skill", "work-closed")
# One page per finding: every tools/finding_<slug>.py (TITLE, LINE, PAGE) is served at /finding/<slug>.
FINDINGS = {os.path.basename(f)[len("finding_"):-3].replace("_", "-"): importlib.import_module(os.path.basename(f)[:-3])
            for f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "finding_*.py")))}


def newest(listed, n=60):
    return team.table().query(IndexName="new", KeyConditionExpression=Key("listed").eq(listed), ScanIndexForward=False, Limit=n)["Items"]


def snapshot():
    with ThreadPoolExecutor(len(LISTS)) as pool:  # one query per list, at the same time
        items = [item for page in pool.map(newest, LISTS) for item in page]
    start = f"{time.time_ns() - int(HOURS * 3600 * 10**9):020d}"
    messages = board.rows(KeyConditionExpression=Key("pk").eq("chan#all") & Key("sk").gt(start))
    scores = board.rows(KeyConditionExpression=Key("pk").eq("scores"))  # every score, in the order its result was posted
    return {"now_ns": time.time_ns(), "hours": HOURS, "test": team.TEST, "items": items, "messages": messages, "scores": scores,
            "findings": [{"slug": slug, "title": m.TITLE, "line": m.LINE} for slug, m in FINDINGS.items()
                         if getattr(m, "LISTED", True)]}  # LISTED = False: served at its address, not linked in the header


def detail(item_id):
    rows = board.rows(KeyConditionExpression=Key("pk").eq(f"item#{item_id}"))  # the item, its votes and its comments
    item = next((r for r in rows if r["sk"] == "item"), None)
    if not item:
        return None
    return {"item": item, "votes": [r for r in rows if r["sk"].startswith("vote#")],
            "comments": sorted((r for r in rows if r["sk"].startswith("comment#")), key=lambda c: c["sk"]),
            "thread": board.rows(KeyConditionExpression=Key("pk").eq(f"chan#{item_id}"))}


class Handler(BaseHTTPRequestHandler):
    def send(self, status, kind, body):
        data = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", f"{kind}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/":
            return self.send(200, "text/html", PAGE)
        if path == "/architecture":
            return self.send(200, "text/html", architecture.PAGE)
        if path.startswith("/finding/") and path[len("/finding/"):] in FINDINGS:
            return self.send(200, "text/html", FINDINGS[path[len("/finding/"):]].PAGE)
        if path != "/data" and not path.startswith("/data/"):
            return self.send(404, "text/plain", f"no page {path}")
        try:  # the page shows the error text; the traceback goes to this terminal
            found = snapshot() if path == "/data" else detail(path[len("/data/"):])
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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
:root {
  color-scheme: light dark;
  --paper: #eef2ec; --sheet: #f8faf7; --ink: #17201b; --mute: #5f6b64; --faint: #8e9a93; --rule: #d5ddd6; --grid: #dfe6df;
  --blue: #2448d8; --blue-wash: #2448d81a; --red: #d2283c; --red-wash: #d2283c12;
  --pl: .55; --pc: .13;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #0e1311; --sheet: #151c19; --ink: #e4ebe6; --mute: #95a39b; --faint: #66736c; --rule: #25302a; --grid: #1b2420;
    --blue: #8aa4ff; --blue-wash: #8aa4ff22; --red: #ff6577; --red-wash: #ff657714;
    --pl: .76; --pc: .11;
  }
}
* { box-sizing: border-box; }
[hidden] { display: none !important; }
html { background: var(--paper); }
body {
  margin: 0; color: var(--ink); background: var(--paper);
  font: 400 15px/1.5 "Archivo", ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif;
  font-variant-numeric: tabular-nums; -webkit-font-smoothing: antialiased;
}
button { font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; }
a { color: inherit; text-decoration: none; }
:focus-visible { outline: 2px solid var(--blue); outline-offset: 2px; border-radius: 3px; }
.wrap { max-width: 1840px; margin: 0 auto; padding: 28px 40px 64px; }

/* Header: name, filter, status; then one sentence on the state of the board */
.top { display: flex; align-items: center; gap: 20px; flex-wrap: wrap; }
.name { font-weight: 700; font-stretch: 112%; font-size: 15px; letter-spacing: .01em; margin: 0; }
.how { font-size: 13px; color: var(--mute); }
.how:hover { color: var(--ink); }
#finds { display: contents; }
.test { color: var(--red); font-weight: 600; font-size: 13px; }
.search { margin-left: auto; position: relative; display: flex; align-items: center; }
.search input {
  width: 300px; font: inherit; font-size: 14px; color: var(--ink); background: var(--sheet);
  border: 1px solid var(--rule); border-radius: 8px; padding: 7px 34px 7px 12px;
}
.search input::placeholder { color: var(--faint); }
.search input:focus { outline: 2px solid var(--blue); outline-offset: 0; border-color: transparent; }
.search kbd {
  position: absolute; right: 9px; font: 500 12px/1 "Archivo", sans-serif; color: var(--faint);
  border: 1px solid var(--rule); border-radius: 4px; padding: 3px 6px; pointer-events: none;
}
.status { font-size: 13px; color: var(--mute); white-space: nowrap; display: flex; align-items: center; gap: 8px; }
.status::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--blue); }
.status.bad { color: var(--red); }
.status.bad::before { background: var(--red); }
.summary {
  margin: 22px 0 0; font-size: clamp(22px, 2.1vw, 30px); line-height: 1.25; font-weight: 340; font-stretch: 104%;
  letter-spacing: -.01em; max-width: 60ch;
}
.summary b { font-weight: 640; }
.summary .warn { color: var(--red); }
.chip {
  display: inline-flex; align-items: center; gap: 8px; margin-top: 14px; font-size: 13px; color: var(--mute);
  border: 1px solid var(--rule); border-radius: 999px; padding: 4px 6px 4px 12px; background: var(--sheet);
}
.chip button { color: var(--mute); border-radius: 999px; padding: 0 7px; }
.chip button:hover { color: var(--ink); }

.error {
  margin-top: 20px; border-left: 3px solid var(--red); background: var(--red-wash); padding: 12px 16px;
  max-width: 900px; font-size: 14px;
}
.error strong { color: var(--red); font-weight: 600; }
.error code { font-size: 13px; overflow-wrap: anywhere; }

/* Hill: per benchmark, the best untrained-base score so far against the best RL score */
.hill { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 440px), 1fr)); gap: 28px 56px; margin-top: 34px; }
.hp h2 { border-bottom-color: var(--rule); }
.hp-nums { display: flex; align-items: flex-end; gap: 28px; margin: 14px 0 6px; flex-wrap: wrap; }
.hp-num { display: grid; gap: 2px; }
.hp-num b { font-size: 46px; line-height: .95; font-weight: 600; font-stretch: 108%; letter-spacing: -.02em; color: var(--blue); }
.hp-num.rl b, .hp-num.gap b { font-size: 24px; font-weight: 500; color: var(--ink); }
.hp-num.gap b { color: var(--red); }
.hp-num small { font-size: 12px; color: var(--mute); }
.hp svg { display: block; width: 100%; height: auto; overflow: visible; }
.hp svg text { font: 400 11px "Archivo", ui-sans-serif, system-ui, sans-serif; fill: var(--faint); }
.hp .grid { stroke: var(--grid); stroke-width: 1; }
.hp .band { fill: var(--red-wash); }
.hp .target { stroke: var(--ink); stroke-width: 1.2; stroke-dasharray: 4 4; opacity: .55; }
.hp text.label { fill: var(--mute); }
.hp text.gaplabel { fill: var(--red); font-weight: 600; }
.hp .climb { fill: none; stroke: var(--blue); stroke-width: 2.5; stroke-linejoin: round; }
.hp .dot { fill: var(--sheet); stroke: var(--faint); stroke-width: 1.5; }
.hp .dot.best { fill: var(--blue); stroke: var(--blue); }
.hp a:hover .dot, .hp a:focus-visible .dot { stroke: var(--ink); stroke-width: 2.5; }
.hp text.best { fill: var(--ink); font-weight: 600; }

/* Lanes: one per person, every post and message of the last hours as a stem */
.lanes { margin: 30px 0 8px; }
.lane { display: grid; grid-template-columns: 150px 1fr; align-items: end; height: 30px; }
.lane > button {
  text-align: left; font-size: 13px; color: var(--mute); padding: 0 12px 3px 0; overflow: hidden;
  text-overflow: ellipsis; white-space: nowrap; display: flex; align-items: center; gap: 8px;
}
.lane > button::before { content: ""; flex: none; width: 8px; height: 8px; border-radius: 50%; background: var(--pc-color); }
.lane > button:hover, .lane.on > button { color: var(--ink); }
.lane.off { opacity: .28; }
.track {
  position: relative; height: 100%; border-bottom: 1px solid var(--rule);
  background-image: linear-gradient(to right, var(--grid) 1px, transparent 1px);
  background-size: var(--hour) 100%;
}
.stem { position: absolute; bottom: 0; width: 2px; margin-left: -1px; background: var(--pc-color); }
.stem.msg { height: 7px; width: 1px; background: var(--faint); opacity: .7; }
.stem.note { height: 11px; }
.stem.work { height: 17px; }
.stem.result { height: 24px; }
.stem.result::after {
  content: ""; position: absolute; top: -4px; left: -3px; width: 8px; height: 8px; border-radius: 50%; background: var(--pc-color);
}
a.stem::before { content: ""; position: absolute; inset: -4px -5px; }
a.stem:hover, a.stem:focus-visible { background: var(--ink); }
a.stem:hover::after { background: var(--ink); }
.axis { display: grid; grid-template-columns: 150px 1fr; font-size: 12px; color: var(--faint); }
.axis div { position: relative; height: 18px; }
.axis div span { position: absolute; top: 4px; transform: translateX(-50%); white-space: nowrap; }
.axis div span:first-child { transform: none; }
.axis div span:last-child { transform: translateX(-100%); }

/* Board */
.board {
  display: grid; gap: 0 56px; margin-top: 30px; align-items: start;
  grid-template-columns: minmax(0, 1.12fr) minmax(0, 1.12fr) minmax(0, 1fr);
  grid-template-areas: "main side talk";
}
.main { grid-area: main; } .side { grid-area: side; } .talk { grid-area: talk; }
.talk { position: sticky; top: 0; max-height: 100vh; overflow-y: auto; scrollbar-width: thin; }
section { margin-bottom: 44px; }
h2 {
  margin: 0 0 6px; font-size: 15px; font-weight: 650; font-stretch: 115%; letter-spacing: .005em;
  display: flex; align-items: baseline; gap: 10px; padding-bottom: 10px; border-bottom: 1px solid var(--ink);
}
h2 span { color: var(--faint); font-weight: 450; font-stretch: 100%; }
.empty { color: var(--faint); font-size: 14px; padding: 14px 0; max-width: 46ch; }

.row {
  position: relative; padding: 13px 0 13px 16px; border-bottom: 1px solid var(--rule); cursor: pointer;
}
.row::before { content: ""; position: absolute; left: 0; top: 15px; bottom: 15px; width: 3px; border-radius: 2px; background: var(--pc-color); }
.row:hover { background: linear-gradient(to right, var(--sheet), transparent); }
.row.current { background: var(--sheet); }
.row .open { display: block; border-radius: 2px; }
.row .text {
  display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 3; overflow: hidden;
  overflow-wrap: anywhere; white-space: pre-line;
}
.result .text { font-size: 16px; line-height: 1.5; -webkit-line-clamp: 4; }
.n { font-weight: 620; }
.row.idea .text, .row.knowledge .text, .row.skill .text, .closed .text { font-size: 14px; }
.closed .text { color: var(--mute) !important; }
.meta {
  display: flex; flex-wrap: wrap; align-items: center; gap: 4px 14px; margin-top: 6px; font-size: 12.5px; color: var(--mute);
}
.who { color: oklch(var(--pl) var(--pc) var(--h)); font-weight: 600; }
.who:hover { text-decoration: underline; text-underline-offset: 3px; }
.branch { max-width: 22ch; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.id { color: var(--faint); }
.fresh { color: var(--blue); font-weight: 560; }
.idle { display: inline-flex; align-items: center; gap: 8px; margin-left: auto; }
.meter { width: 64px; height: 3px; border-radius: 2px; background: var(--rule); overflow: hidden; }
.meter i { display: block; height: 100%; background: var(--mute); }
.stale { background: var(--red-wash); }
.stale .idle { color: var(--red); font-weight: 600; }
.stale .meter i { background: var(--red); }
.stale.row::after { content: ""; position: absolute; inset: 0 0 0 -12px; border-left: 3px solid var(--red); pointer-events: none; }

.msgs { list-style: none; margin: 0; padding: 0; }
.msg { padding: 11px 0; border-bottom: 1px solid var(--rule); font-size: 14px; }
.msg .meta { margin: 0 0 3px; }
.msg .text { overflow-wrap: anywhere; white-space: pre-line; }
a.ref { color: var(--blue); text-decoration: underline; text-decoration-color: var(--blue-wash); text-underline-offset: 3px; }
a.ref:hover { text-decoration-color: var(--blue); }

/* One restrained motion: a new item or message arrives */
.arrived { animation: arrive 2.6s ease-out; }
@keyframes arrive { from { background-color: var(--blue-wash); box-shadow: inset 3px 0 0 var(--blue); } }

/* Item panel */
.panel {
  position: fixed; top: 0; right: 0; bottom: 0; width: min(620px, 100vw); z-index: 2;
  background: var(--sheet); border-left: 1px solid var(--rule); overflow-y: auto;
  box-shadow: -24px 0 60px -30px rgb(10 20 15 / .35); animation: slide .18s ease-out;
}
@keyframes slide { from { transform: translateX(24px); opacity: 0; } }
.phead {
  position: sticky; top: 0; background: var(--sheet); display: flex; align-items: center; gap: 12px;
  padding: 20px 28px 14px; border-bottom: 1px solid var(--rule);
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
.facts { display: grid; grid-template-columns: max-content 1fr; gap: 6px 20px; margin: 0 0 30px; font-size: 13.5px; }
.facts dt { color: var(--faint); }
.facts dd { margin: 0; overflow-wrap: anywhere; }
.pbody h3 { font-size: 14px; font-weight: 650; font-stretch: 112%; margin: 0 0 4px; display: flex; gap: 10px; }
.pbody h3 span { color: var(--faint); font-weight: 450; font-stretch: 100%; }
.pbody .msgs { margin-bottom: 28px; }
.note { color: var(--faint); font-size: 14px; margin: 6px 0 28px; }

@media (max-width: 1040px) {
  .board { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); grid-template-areas: "main side" "talk talk"; }
  .talk { position: static; max-height: none; overflow: visible; }
}
@media (max-width: 820px) {
  .wrap { padding: 20px 16px 48px; }
  .search { margin-left: 0; width: 100%; }
  .search input { width: 100%; }
  .board { display: flex; flex-direction: column; }
  .main, .side, .talk { display: contents; }  /* one column: open work, results, messages, then the rest */
  .board section { order: 4; }
  .board .s-work { order: 1; } .board .s-result { order: 2; } .board .s-msgs { order: 3; }
  .lane, .axis { grid-template-columns: 116px 1fr; }
  .axis div span:nth-child(2) { display: none; }  /* it would overlap the first label */
}
@media (prefers-reduced-motion: reduce) {
  .arrived, .panel { animation: none; }
}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="top">
      <h1 class="name">Team board</h1>
      <a class="how" href="/architecture">How it works</a>
      <span id="finds"></span>
      <span class="test" id="test" hidden>test table</span>
      <label class="search"><input id="q" type="search" placeholder="Filter items and messages" aria-label="Filter items and messages" autocomplete="off"><kbd>/</kbd></label>
      <span class="status" id="status" role="status">Reading the board</span>
    </div>
    <p class="summary" id="summary"></p>
    <div id="chip"></div>
    <div id="error"></div>
  </header>
  <div class="hill" id="hill" aria-label="Best untrained-base score per benchmark against RL"></div>
  <div class="lanes" id="lanes" aria-label="Activity per person" hidden></div>
  <main class="board" id="board" hidden>
    <div class="main">
      <section class="s-work"><h2>Open work <span id="n-work"></span></h2><div id="work"></div></section>
      <section><h2>Ideas <span id="n-idea"></span></h2><div id="idea"></div></section>
    </div>
    <div class="side">
      <section class="s-result"><h2>Results <span id="n-result"></span></h2><div id="result"></div></section>
      <section><h2>Knowledge and skills <span id="n-knowledge"></span></h2><div id="knowledge"></div></section>
      <section><h2>Closed work <span id="n-closed"></span></h2><div id="closed"></div></section>
    </div>
    <div class="talk">
      <section class="s-msgs"><h2>Messages on all <span id="n-msgs"></span></h2><ul class="msgs" id="msgs"></ul></section>
    </div>
  </main>
</div>
<aside class="panel" id="panel" hidden aria-labelledby="ptitle"></aside>
<script>
const $ = id => document.getElementById(id);
const S = { data: null, readAt: 0, error: null, who: null, q: "", open: null, detail: null, seen: null };
const HUES = [300, 155, 70, 215, 340, 115, 255, 35];  // far apart first; red (stale) and blue (fresh) last
let people = [];
const KINDS = { work: "Open work", "work-closed": "Closed work", result: "Result", idea: "Idea", knowledge: "Knowledge", skill: "Skill" };
const ID = /\b((?:work|result|idea|knowledge|skill)-[0-9a-f]{6})\b|(?<![\w.-])(\d+(?:[.,]\d+)*(?: ?%)?)(?![\w-])/g;

const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const hue = name => HUES[Math.max(0, people.indexOf(name)) % HUES.length];  // by sorted name: the same colors on every screen
const pstyle = name => `--h:${hue(name)};--pc-color:oklch(var(--pl) var(--pc) ${hue(name)})`;
const now = () => S.data ? S.data.now_ns + (Date.now() - S.readAt) * 1e6 : Date.now() * 1e6;
const mins = ns => Math.max(0, Math.floor((now() - Number(ns)) / 6e10));
const rel = ns => { const m = mins(ns); return m < 1 ? "now" : m < 120 ? `${m}m` : m < 2880 ? `${Math.floor(m / 60)}h` : `${Math.floor(m / 1440)}d`; };
const utc = ns => new Date(Number(ns) / 1e6).toISOString().slice(0, 19).replace("T", " ") + " UTC";
const when = (ns, prefix = "") => `<time title="${utc(ns)}">${prefix}${rel(ns)}</time>`;
const msgNs = m => Number(m.sk.slice(0, 20));

/* Text from the board, escaped; item ids become links, and in results the numbers are set heavier. */
function rich(text, { links = true, numbers = false } = {}) {
  return esc(text).replace(ID, (all, id, num) =>
    id ? (links ? `<a class="ref" href="#${id}">${id}</a>` : id) : numbers ? `<span class="n">${num}</span>` : num);
}
const who = (name, branch) =>
  `<button class="who" style="${pstyle(name)}" data-who="${esc(name)}" title="Show only ${esc(name)}">${esc(name)}</button>` +
  (branch ? `<span class="branch" title="${esc(branch)}">${esc(branch)}</span>` : "");
const match = (...fields) => (!S.q || fields.join("\n").toLowerCase().includes(S.q));
const shown = i => (!S.who || i.who === S.who) && match(i.id, i.text, i.who, i.branch);

function row(i) {
  const open = i.listed === "work", closed = i.listed === "work-closed";
  const idle = open ? mins(i.active_ns ?? i.at_ns) : 0;
  const fresh = mins(open ? i.active_ns ?? i.at_ns : i.at_ns) < 10;
  const cls = ["row", i.kind, open && idle >= 60 && "stale", closed && "closed", S.open === i.id && "current", isNew(i.id) && "arrived"];
  const meta = [
    who(i.who, i.branch),
    `<span class="id">${i.id}</span>`,
    closed ? `<span>closed ${when(i.closed_ns ?? 0)} ago${i.closed_by ? " by " + esc(i.closed_by.split("/")[0]) : ""}</span>`
           : fresh ? `<span class="fresh">${when(open ? i.active_ns ?? i.at_ns : i.at_ns)}</span>` : `<span>${when(i.at_ns)}</span>`,
    i.kind === "skill" ? "<span>skill</span>" : "",
    i.ups || i.downs ? `<span>+${i.ups} −${i.downs}</span>` : "",
    i.n_comments ? `<span>${i.n_comments} comment${i.n_comments > 1 ? "s" : ""}</span>` : "",
    open ? `<span class="idle" title="Minutes since the item was posted or last commented on">idle ${idle < 120 ? idle + "m" : rel(i.active_ns ?? i.at_ns)}` +
           `<span class="meter"><i style="width:${Math.min(100, idle / 60 * 100)}%"></i></span></span>` : "",
  ].join("");
  return `<article class="${cls.filter(Boolean).join(" ")}" style="${pstyle(i.who)}" data-key="${i.id}">` +
    `<a class="open" href="#${i.id}" title="${i.id}"><span class="text">${rich(i.text, { links: false, numbers: i.kind === "result" })}</span></a>` +
    `<div class="meta">${meta}</div></article>`;
}

function message(m) {
  return `<li class="msg${isNew(m.sk) ? " arrived" : ""}"><div class="meta">${who(m.who, m.branch)}${when(msgNs(m))}</div>` +
    `<div class="text">${rich(m.text)}</div></li>`;
}

const isNew = key => S.seen && !S.seen.has(key);

function list(id, items, empty) {
  $(id).innerHTML = items.length ? items.map(row).join("") : `<p class="empty">${empty}</p>`;
}

function render() {
  const d = S.data;
  const focused = document.activeElement?.closest("[data-key]")?.dataset.key;
  $("status").className = "status" + (S.error ? " bad" : "");
  $("status").textContent = !d ? (S.error ? "Not read" : "Reading the board")
    : S.error ? `Not updated for ${Math.round((Date.now() - S.readAt) / 1000)} s` : "Live";
  $("status").title = d ? `Last read ${utc(d.now_ns)}` : "";
  $("error").innerHTML = S.error ? errorText(S.error) : "";
  $("chip").innerHTML = S.who ? `<span class="chip">Showing ${esc(S.who)} only <button id="clearwho" aria-label="Show everyone">✕</button></span>` : "";
  $("board").hidden = $("lanes").hidden = !d;
  if (!d) return;
  $("test").hidden = !d.test;
  $("finds").innerHTML = (d.findings || []).map(f => `<a class="how" href="/finding/${esc(f.slug)}" title="${esc(f.line)}">${esc(f.title)}</a>`).join("");

  people = [...new Set([...d.items, ...d.messages].map(r => r.who))].sort();
  const items = d.items.map(i => ({ ...i, closed_ns: i.closed_at ? Date.parse(i.closed_at) * 1e6 : null }));
  const by = list => items.filter(i => list.includes(i.listed) && shown(i));
  const work = by(["work"]).sort((a, b) => {
    const ia = mins(a.active_ns ?? a.at_ns), ib = mins(b.active_ns ?? b.at_ns);
    return (ib >= 60) - (ia >= 60) || (ib >= 60 ? ib - ia : ia - ib);  // idle over an hour first, then most recently active
  });
  const results = by(["result"]).sort((a, b) => b.at_ns - a.at_ns);
  const ideas = by(["idea"]).sort((a, b) => b.at_ns - a.at_ns);
  const notes = by(["knowledge", "skill"]).sort((a, b) => b.at_ns - a.at_ns);
  const closed = by(["work-closed"]).sort((a, b) => (b.closed_ns ?? 0) - (a.closed_ns ?? 0));
  const msgs = d.messages.filter(m => (!S.who || m.who === S.who) && match(m.text, m.who, m.branch)).reverse();
  const filtered = S.q || S.who ? "Nothing matches the filter." : "";

  list("work", work, filtered || "No open work. An agent claims work with <code>board.py post work</code>.");
  list("result", results, filtered || "No results yet.");
  list("idea", ideas, filtered || "No ideas yet.");
  list("knowledge", notes, filtered || "No knowledge or skills yet.");
  list("closed", closed, filtered || "No work has been closed yet.");
  $("msgs").innerHTML = msgs.length ? msgs.map(message).join("") : `<li class="empty">${filtered || `No messages on all in the last ${d.hours} h.`}</li>`;
  [["n-work", work], ["n-result", results], ["n-idea", ideas], ["n-knowledge", notes], ["n-closed", closed], ["n-msgs", msgs]]
    .forEach(([id, l]) => $(id).textContent = l.length);

  summary(items);
  hill(d.scores || []);
  lanes(items, d);
  S.seen = new Set([...d.items.map(i => i.id), ...d.messages.map(m => m.sk)]);
  if (focused) document.querySelector(`[data-key="${focused}"] .open`)?.focus({ preventScroll: true });
}

function summary(items) {
  const open = items.filter(i => i.listed === "work");
  const stale = open.filter(i => mins(i.active_ns ?? i.at_ns) >= 60).length;
  const people = new Set(open.map(i => i.who)).size;
  const last = items.filter(i => i.kind === "result").sort((a, b) => b.at_ns - a.at_ns)[0];
  $("summary").innerHTML = (open.length
      ? `<b>${open.length}</b> open work item${open.length > 1 ? "s" : ""} from <b>${people}</b> ${people > 1 ? "people" : "person"}, ` +
        (stale ? `<b class="warn">${stale}</b> <span class="warn">idle over an hour</span>.` : "none idle over an hour.")
      : "No open work.") +
    (last ? ` Last result <b>${rel(last.at_ns)}</b>${mins(last.at_ns) ? " ago" : ""} from ${esc(last.who)}.` : " No results yet.");
}

function hill(scores) {
  const pct = s => 100 * s.right / s.n, f1 = v => v.toFixed(1);
  const benches = [...new Set(scores.map(s => s.benchmark))].sort((a, b) => (b === "MATH-500") - (a === "MATH-500") || a.localeCompare(b));
  $("hill").innerHTML = benches.map(name => {
    const seen = new Set();  // a run reported in two results is one attempt
    const base = scores.filter(s => s.benchmark === name && s.model === "base")
      .filter(s => { const k = `${s.right}/${s.n} ${s.config}`; return !seen.has(k) && seen.add(k); });
    const rl = scores.filter(s => s.benchmark === name && s.model === "rl").sort((a, b) => pct(b) - pct(a))[0];
    if (!base.length) return "";
    let top = -1;
    const pts = base.map(s => { const p = pct(s), best = p > top; if (best) top = p; return { s, p, best }; });
    const lead = pts.filter(q => q.best).at(-1);
    const W = 640, H = 230, L = 34, R = 104, T = 14, B = 30;
    const vals = pts.map(q => q.p).concat(rl ? [pct(rl)] : []);
    const lo = Math.max(0, Math.floor((Math.min(...vals) - 4) / 10) * 10), hi = Math.min(100, Math.ceil((Math.max(...vals) + 2) / 10) * 10);
    const y = v => T + (hi - v) / (hi - lo) * (H - T - B);
    const x = i => L + (i + .5) / pts.length * (W - L - R);
    const grid = [];
    for (let v = lo; v <= hi; v += 10) grid.push(`<line class="grid" x1="${L}" x2="${W - R}" y1="${y(v)}" y2="${y(v)}"/><text x="${L - 8}" y="${y(v) + 4}" text-anchor="end">${v}</text>`);
    let path = `M${L},${y(pts[0].p)}`;
    pts.forEach((q, i) => { if (q.best && i) path += `H${x(i)}V${y(q.p)}`; });
    path += `H${W - R}`;
    const gap = rl ? pct(rl) - lead.p : null;
    const rlPart = rl ? `<rect class="band" x="${L}" width="${W - R - L}" y="${y(pct(rl))}" height="${Math.max(0, y(lead.p) - y(pct(rl)))}"/>` +
      `<line class="target" x1="${L}" x2="${W - R}" y1="${y(pct(rl))}" y2="${y(pct(rl))}"/>` +
      `<text class="label" x="${W - R + 10}" y="${y(pct(rl)) + 4}">RL ${f1(pct(rl))}</text>` +
      (gap > 0 ? `<text class="gaplabel" x="${W - R + 10}" y="${(y(pct(rl)) + y(lead.p)) / 2 + 4}">gap ${f1(gap)}</text>` : "") : "";
    const dots = pts.map((q, i) => {
      const tip = `${q.s.config}: ${q.s.right}/${q.s.n} (${f1(q.p)} %)${q.s.tokens ? `, ${Number(q.s.tokens).toLocaleString("en-US")} tokens per problem` : ""}, ${q.s.who}, ${q.s.result}`;
      return `<a href="#${esc(q.s.result)}" aria-label="${esc(tip)}"><title>${esc(tip)}</title>` +
        `<circle class="dot${q.best ? " best" : ""}" cx="${x(i)}" cy="${y(q.p)}" r="${q.best ? 5 : 4}"/></a>`;
    }).join("");
    const li = pts.indexOf(lead);
    const leadLabel = `<text class="best" x="${x(li)}" y="${y(lead.p) - 12}" text-anchor="${li > pts.length / 2 ? "end" : "middle"}">${esc(lead.s.config)}</text>`;
    const axis = `<text x="${L}" y="${H - 8}">Attempts in the order found (${pts.length})</text><text x="${W - R}" y="${H - 8}" text-anchor="end">% right</text>`;
    return `<section class="hp"><h2>${esc(name)} <span>untrained base against RL, n ${lead.s.n}</span></h2>` +
      `<div class="hp-nums"><div class="hp-num"><b>${f1(lead.p)}</b><small>best base, ${lead.s.right}/${lead.s.n}</small></div>` +
      (rl ? `<div class="hp-num rl"><b>${f1(pct(rl))}</b><small>RL, ${esc(rl.config)}</small></div>` +
            `<div class="hp-num gap"><b>${gap > 0 ? f1(gap) : "0"}</b><small>${gap > 0 ? "points to go" : "gap closed"}</small></div>` : "") + `</div>` +
      `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(name)}: best base ${f1(lead.p)} %, RL ${rl ? f1(pct(rl)) : "not measured"}">` +
      grid.join("") + rlPart + `<path class="climb" d="${path}"/>` + dots + leadLabel + axis + `</svg></section>`;
  }).join("") || `<p class="empty">No scores yet. Attach one to a result: <code>board.py score &lt;result id&gt; base MATH-500 410/500 "cue, T 1.0"</code></p>`;
}

function lanes(items, d) {
  const span = d.hours * 3600e9, start = now() - span;
  const x = ns => ((Number(ns) - start) / span * 100).toFixed(3) + "%";
  const events = [
    ...items.filter(i => i.at_ns >= start).map(i => ({ who: i.who, ns: i.at_ns, item: i })),
    ...d.messages.map(m => ({ who: m.who, ns: msgNs(m), msg: m })),
  ];
  const people = [...new Set(events.map(e => e.who))].sort();
  const hour = `calc(100% / ${d.hours})`;
  $("lanes").innerHTML = people.map(p => {
    const stems = events.filter(e => e.who === p).sort((a, b) => (a.item ? 1 : 0) - (b.item ? 1 : 0)).map(e => {
      if (e.msg) return `<span class="stem msg" style="left:${x(e.ns)}" title="${esc(e.msg.text.slice(0, 140))}"></span>`;
      const k = e.item.kind === "result" ? "result" : e.item.kind === "work" ? "work" : "note";
      return `<a class="stem ${k}" style="left:${x(e.ns)}" href="#${e.item.id}" tabindex="-1" ` +
        `title="${e.item.id}, ${rel(e.ns)} ago: ${esc(e.item.text.slice(0, 140))}"></a>`;
    }).join("");
    const cls = S.who ? (S.who === p ? "on" : "off") : "";
    return `<div class="lane ${cls}" style="${pstyle(p)}"><button data-who="${esc(p)}" title="Show only ${esc(p)}">${esc(p)}</button>` +
      `<div class="track" style="--hour:${hour}">${stems}</div></div>`;
  }).join("") + (people.length ? `<div class="axis"><i></i><div>${
    Array.from({ length: Math.floor(d.hours) + 1 }, (_, h) => {
      const left = (100 - h / d.hours * 100).toFixed(3);
      return `<span style="left:${left}%">${h ? h + "h ago" : "now"}</span>`;
    }).reverse().join("")}</div></div>` : `<p class="empty">No posts or messages in the last ${d.hours} h.</p>`);
}

function errorText(e) {
  if (e.server) return `<div class="error"><strong>The view server does not answer.</strong> It may have stopped. ` +
    `Start it again with <code>uv run tools/view.py</code>; the page keeps trying every 10 s.</div>`;
  return `<div class="error"><strong>The server cannot read the board table.</strong> ` +
    `Check that the AWS profile <code>iterate-ecr</code> exists on this machine (README, Setup step 2), that the key has not expired, ` +
    `and that the network is up. The terminal running view.py has the full traceback.<br><code>${esc(e.text)}</code></div>`;
}

async function get(path) {
  const r = await fetch(path).catch(() => { throw { server: true }; });
  if (r.status === 404) return null;
  if (!r.ok) throw { text: `${r.status}: ${await r.text()}` };
  return r.json();
}

function poll() {
  get("/data")
    .then(data => { S.data = data; S.readAt = Date.now(); S.error = null; return S.open && loadDetail(); })
    .catch(e => { S.error = e; console.error(e); })
    .finally(() => { render(); renderPanel(); setTimeout(poll, 10000); });
}

async function loadDetail() {
  const id = S.open;
  const found = await get("/data/" + encodeURIComponent(id));
  if (S.open === id) S.detail = found ?? { missing: id };
}

/* Item panel */
function renderPanel() {
  const panel = $("panel");
  if (!S.open) { panel.hidden = true; panel.innerHTML = ""; return; }
  const scroll = panel.scrollTop, focused = panel.contains(document.activeElement) && document.activeElement.id;
  const base = S.detail?.item ?? S.data?.items.find(i => i.id === S.open);
  panel.hidden = false;
  if (S.detail?.missing) {
    panel.innerHTML = head(S.open, "") + `<div class="pbody"><p class="note">No item named ${esc(S.open)} on this board. ` +
      `The link may be mistyped, or the item is on the test table.</p></div>`;
  } else if (!base) {
    panel.innerHTML = head(S.open, "") + `<div class="pbody"><p class="note">Reading ${esc(S.open)}</p></div>`;
  } else {
    const i = base, d = S.detail;
    const open = i.listed === "work", idle = mins(i.active_ns ?? i.at_ns);
    const state = open ? `${KINDS.work}, ${idle ? "idle " + rel(i.active_ns ?? i.at_ns) : "active now"}` :
      i.listed === "work-closed" ? `Closed by ${esc(i.closed_by)} ${when(Date.parse(i.closed_at) * 1e6)} ago` : KINDS[i.kind];
    const votes = d ? d.votes.map(v => `${esc(v.who)} ${v.vote > 0 ? "+" : "−"}`).join(", ") : "";
    const facts = [
      ["Posted by", who(i.who)], ["Branch", esc(i.branch || "not recorded")],
      ["Agent", esc([i.agent, (i.session || "").slice(0, 8)].filter(Boolean).join(", ") || "not recorded")],
      ["Posted", `${when(i.at_ns)} ago, ${utc(i.at_ns)}`],
      ["Votes", `+${i.ups} −${i.downs}${votes ? ": " + votes : ""}`],
    ].map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("");
    const thread = (title, rows, empty) => `<h3>${title} <span>${d ? rows.length : ""}</span></h3>` + (!d ? `<p class="note">Reading</p>` :
      rows.length ? `<ul class="msgs">${rows.map(r => `<li class="msg"><div class="meta">${who(r.who, r.branch)}` +
        `${when(Date.parse(r.at) * 1e6)}</div><div class="text">${rich(r.text)}</div></li>`).join("")}</ul>` : `<p class="note">${empty}</p>`);
    panel.innerHTML = head(i.id, state, open && idle >= 60) +
      `<div class="pbody"><p class="full">${rich(i.text, { numbers: i.kind === "result" })}</p><dl class="facts">${facts}</dl>` +
      thread("Comments", d?.comments ?? [], "No comments.") +
      thread("Messages on this item", d?.thread ?? [], `No messages sent to ${esc(i.id)}.`) + "</div>";
  }
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
  if (!id) {
    renderPanel();
    document.querySelector(`[data-key="${CSS.escape(was)}"] .open`)?.focus({ preventScroll: true });
    return;
  }
  renderPanel();
  if (!was) $("ptitle").focus({ preventScroll: true });  // opened from the board: focus moves into the panel
  loadDetail().catch(e => { S.error = e; console.error(e); render(); }).finally(renderPanel);
}

function closePanel() { history.pushState(null, "", location.pathname); fromHash(); }

function move(step) {
  const links = [...document.querySelectorAll("#board .row .open")];
  if (!links.length) return;
  const from = document.activeElement.closest("#panel") ? document.querySelector(`[data-key="${CSS.escape(S.open)}"] .open`) : document.activeElement;
  const at = links.indexOf(from);  // from the open item when focus is in the panel
  const next = links[at < 0 ? (step > 0 ? 0 : links.length - 1) : Math.max(0, Math.min(links.length - 1, at + step))];
  next.focus({ preventScroll: true });
  next.scrollIntoView({ block: "nearest" });
  if (S.open) location.replace("#" + next.closest("[data-key]").dataset.key);
}

document.addEventListener("click", e => {
  const person = e.target.closest("[data-who]");
  if (person) { S.who = S.who === person.dataset.who ? null : person.dataset.who; render(); return; }
  if (e.target.closest("#clearwho")) { S.who = null; render(); return; }
  if (e.target.closest("#close")) { closePanel(); return; }
  if (e.target.closest("#copy")) {
    navigator.clipboard.writeText(location.href).then(() => { $("copy").textContent = "Copied"; });
    return;
  }
  const r = e.target.closest(".row");
  if (r && !e.target.closest("a")) location.hash = r.dataset.key;
});
document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.target === $("q")) {
    if (e.key === "Escape") { $("q").value = ""; S.q = ""; render(); $("q").blur(); }
    if (e.key === "Enter" || e.key === "ArrowDown") { e.preventDefault(); $("q").blur(); move(1); }
    return;
  }
  const inPanel = e.target.closest?.("#panel");
  if (e.key === "/") { e.preventDefault(); $("q").focus(); $("q").select(); }
  else if (e.key === "Escape") { if (S.open) closePanel(); else if (S.who) { S.who = null; render(); } }
  else if (e.key === "j" || (e.key === "ArrowDown" && !inPanel)) { e.preventDefault(); move(1); }
  else if (e.key === "k" || (e.key === "ArrowUp" && !inPanel)) { e.preventDefault(); move(-1); }
});
$("q").addEventListener("input", () => { S.q = $("q").value.trim().toLowerCase(); render(); });
addEventListener("hashchange", fromHash);
fromHash();
poll();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    if {"--help", "-h"} & set(sys.argv):
        sys.exit(__doc__)
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"board at http://127.0.0.1:{PORT}  (Ctrl-C stops it)")
    if sys.stdout.isatty():
        webbrowser.open(f"http://127.0.0.1:{PORT}")
    server.serve_forever()
