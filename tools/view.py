# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35"]
# ///
"""The board and the messages as a web page on this laptop, read-only.

  uv run tools/view.py [--port 8765] [--hours 6]

Opens http://127.0.0.1:8765 in the browser. Columns: open work (with idle minutes), results, ideas, knowledge and
skills, recently closed work, and the messages on the channel `all` of the last --hours. A click on an item id opens
its full text, votes, comments and message thread. The page reloads every 15 s unless an item's text is expanded.
It reads the same DynamoDB table as board.py and msg.py and never moves an agent's message position.
"""
import colorsys
import hashlib
import html
import sys
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from boto3.dynamodb.conditions import Key

import board
import team

PORT = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8765
HOURS = float(sys.argv[sys.argv.index("--hours") + 1]) if "--hours" in sys.argv else 6.0
COLUMNS = [("Open work", ["work"]), ("Results", ["result"]), ("Ideas", ["idea"]), ("Knowledge and skills", ["knowledge", "skill"]),
           ("Closed work", ["work-closed"])]
e = html.escape


def ago(ns):
    minutes = (time.time_ns() - int(ns)) // (60 * 10**9)
    return f"{minutes}m ago" if minutes < 120 else f"{minutes // 60}h ago"


def person(name):
    """A chip with a color fixed by the person's name, so each person's items are easy to pick out."""
    hue = int(hashlib.sha1(name.encode()).hexdigest()[:4], 16) / 0xFFFF
    r, g, b = (int(c * 255) for c in colorsys.hls_to_rgb(hue, 0.45, 0.55))
    return f'<span class="who" style="--c:rgb({r},{g},{b})">{e(name)}</span>'


def newest(listed, n=60):
    return team.table().query(IndexName="new", KeyConditionExpression=Key("listed").eq(listed), ScanIndexForward=False, Limit=n)["Items"]


def card(item):
    idle = ""
    if item.get("listed") == "work":
        minutes = (time.time_ns() - int(item.get("active_ns", item["at_ns"]))) // (60 * 10**9)
        idle = f'<span class="idle{" stale" if minutes >= 60 else ""}">idle {minutes}m</span>'
    counts = "".join(f"<span>{label}</span>" for label in [
        f"+{item['ups']} -{item['downs']}" if item["ups"] or item["downs"] else "", f"{item['n_comments']} comments" if item["n_comments"] else ""] if label)
    first, *rest = item["text"].split("\n", 1)
    body = e(first[:300]) + (f"<details><summary>more</summary><pre>{e(first[300:] + chr(10) + (rest[0] if rest else ''))}</pre></details>"
                             if len(first) > 300 or rest else "")
    return (f'<div class="card"><div class="meta"><a href="/item/{e(item["id"])}">{e(item["id"])}</a>{person(item["who"])}'
            f'<span class="branch">{e(item.get("branch", ""))}</span><span>{ago(item["at_ns"])}</span>{idle}{counts}</div>'
            f'<div class="text">{body}</div></div>')


def messages():
    start = f"{time.time_ns() - int(HOURS * 3600 * 10**9):020d}"
    found = board.rows(KeyConditionExpression=Key("pk").eq("chan#all") & Key("sk").gt(start))
    return "".join(f'<div class="msg"><div class="meta">{person(m["who"])}<span class="branch">{e(m.get("branch", ""))}</span>'
                   f'<span>{ago(m["sk"][:20])}</span></div><div class="text">{e(m["text"])}</div></div>' for m in reversed(found))


def page(title, body, reload=True):
    script = ("<script>setInterval(() => { if (!document.querySelector('details[open]')) location.reload() }, 15000)</script>"
              if reload else "")
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title><style>
:root {{ --bg:#f6f6f4; --panel:#fff; --ink:#1d1d1b; --mute:#6b6b66; --line:#e2e2dd; --warn:#b4471b; --link:#1f5fbf; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#141413; --panel:#1e1e1c; --ink:#ecebe6; --mute:#9a9992; --line:#33332f;
  --warn:#f08a5d; --link:#7fb0ff; }} }}
* {{ box-sizing:border-box; }}
body {{ margin:0; padding:16px; background:var(--bg); color:var(--ink); font:14px/1.45 -apple-system, system-ui, sans-serif; }}
h1 {{ font-size:16px; margin:0 0 12px; }} h1 span {{ color:var(--mute); font-weight:400; }}
.board {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(230px, 1fr)); gap:12px; align-items:start; }}
.col {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:10px; max-height:88vh; overflow:auto; }}
.col h2 {{ font-size:13px; margin:0 0 8px; color:var(--mute); text-transform:uppercase; letter-spacing:.04em; }}
.card, .msg {{ border-top:1px solid var(--line); padding:8px 0; }}
.meta {{ display:flex; flex-wrap:wrap; gap:6px; align-items:center; font-size:12px; color:var(--mute); margin-bottom:3px; }}
.who {{ background:var(--c); color:#fff; border-radius:4px; padding:0 6px; font-weight:600; }}
.branch {{ font-family:ui-monospace, monospace; font-size:11px; }}
.idle.stale {{ color:var(--warn); font-weight:600; }}
a {{ color:var(--link); text-decoration:none; font-family:ui-monospace, monospace; }}
.text {{ overflow-wrap:anywhere; }} pre {{ white-space:pre-wrap; font:inherit; margin:4px 0 0; }}
summary {{ cursor:pointer; color:var(--link); font-size:12px; }}
.single {{ max-width:900px; }}
</style></head><body>{body}{script}</body></html>"""


def overview():
    columns = []
    for title, kinds in COLUMNS:
        items = sorted((i for kind in kinds for i in newest(kind)), key=lambda i: -int(i["at_ns"]))
        columns.append(f'<div class="col"><h2>{e(title)} ({len(items)})</h2>{"".join(map(card, items))}</div>')
    columns.append(f'<div class="col"><h2>Messages on all, last {HOURS:g} h</h2>{messages()}</div>')
    stamp = time.strftime("%H:%M:%S", time.gmtime())
    return page("Team board", f'<h1>Team board <span>{"test table, " if team.TEST else ""}read at {stamp} UTC, reloads every 15 s</span></h1>'
                              f'<div class="board">{"".join(columns)}</div>')


def item_page(item_id):
    item = board.get(item_id)
    rest = board.rows(KeyConditionExpression=Key("pk").eq(f"item#{item_id}"))
    votes = ", ".join(f"{v['who']} {'+' if v['vote'] == 1 else '-'}" for v in rest if v["sk"].startswith("vote#")) or "none"
    comments = "".join(f'<div class="msg"><div class="meta">{person(c["who"])}<span class="branch">{e(c.get("branch", ""))}</span>'
                       f'<span>{e(c["at"])}</span></div><div class="text">{e(c["text"])}</div></div>'
                       for c in sorted((r for r in rest if r["sk"].startswith("comment#")), key=lambda c: c["sk"]))
    thread = "".join(f'<div class="msg"><div class="meta">{person(m["who"])}<span>{e(m["at"])}</span></div><div class="text">{e(m["text"])}</div></div>'
                     for m in board.rows(KeyConditionExpression=Key("pk").eq(f"chan#{item_id}")))
    state = "open" if item.get("listed") == item["kind"] else f"closed by {item.get('closed_by')} at {item.get('closed_at')}"
    body = (f'<div class="single"><p><a href="/">&larr; board</a></p><h1>{e(item_id)} <span>{e(item["kind"])}, {e(state)}</span></h1>'
            f'<div class="meta">{person(item["who"])}<span class="branch">{e(item.get("branch", ""))}</span><span>{e(item["at"])}</span>'
            f'<span>{e(item.get("agent", ""))} {e(item.get("session", "")[:8])}</span><span>votes: {e(votes)}</span></div>'
            f'<pre class="text">{e(item["text"])}</pre><h2>Comments</h2>{comments or "<p>none</p>"}'
            f'<h2>Messages on this item\'s channel</h2>{thread or "<p>none</p>"}</div>')
    return page(item_id, body, reload=False)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            body = overview()
        elif self.path.startswith("/item/") and team.table().get_item(Key={"pk": f"item#{self.path[6:]}", "sk": "item"}).get("Item"):
            body = item_page(self.path[len("/item/"):])
        else:
            self.send_error(404)
            return
        data = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    if {"--help", "-h"} & set(sys.argv):
        sys.exit(__doc__)
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"board at http://127.0.0.1:{PORT}  (Ctrl-C stops it)")
    webbrowser.open(f"http://127.0.0.1:{PORT}")
    server.serve_forever()
