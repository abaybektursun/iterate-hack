#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["websockets>=13", "brotli>=1.1"]
# ///
"""Benchmark of the team board page (tools/view.py) as deployed: network, Lambda cold start, client in headless Chrome.

    uv run infra/monitor/bench.py https://monitor.invariant.team [--n 20] [--json out.json]

1. Network (stdlib http.client, one kept-alive HTTPS connection, Accept-Encoding: gzip, br): for / and /data, the
   body bytes on the wire and decoded, header bytes, content-encoding, cache headers, ETag, whether a conditional
   re-request gets 304, and N paced requests: TTFB (request sent to headers read) and total (to body read).
2. Lambda (aws logs filter-log-events, profile fuelos): REPORT lines of the last --hours at the current memory size.
   Init Duration of cold starts, the Duration of the first request after each cold start, and the Duration of warm
   invocations of 50 ms or more, which are /data (/ returns a constant string in under 10 ms; the logs hold no path).
3. Client (headless Chrome over the DevTools protocol, fresh profile, so a cold cache): first paint, first
   contentful paint, time until the first `--ready` element exists (default ".board [data-key]": the first row of
   data), JS time and longest main-thread task from navigation to that moment + 1 s, then 60 s of the open tab:
   bytes, and the main-thread time of each poll cycle (trace self-time, split into script, style+layout,
   paint+composite, GC, other), plus a sampled CPU profile naming the page's functions. Then the page is told it is
   hidden (document.visibilityState and document.hidden overridden to "hidden"/true and a visibilitychange event
   dispatched) and the /data requests of the next 30 s are counted.
4. Font: the Google Fonts CSS and font files, their bytes, whether Chrome marks the CSS render-blocking, and when
   each finished against first paint.
"""
import argparse
import brotli
import gzip
import http.client
import json
import re
import shutil
import statistics
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from websockets.sync.client import connect

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FUNCTION, PROFILE, REGION = "iterate-monitor", "fuelos", "us-east-1"
POLL_WINDOW_S, HIDDEN_WINDOW_S = 60, 30
GAP_S = 0.5  # between request starts: the API stage allows 3 requests/s
TRACE_CATEGORIES = ",".join([
    "-*", "toplevel", "v8", "v8.execute", "blink.user_timing", "loading", "devtools.timeline",
    "disabled-by-default-devtools.timeline", "disabled-by-default-devtools.timeline.frame", "disabled-by-default-v8.gc",
])


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, round(p / 100 * (len(xs) - 1)))]


def ms(seconds):
    return round(seconds * 1000, 1)


# 1. Network

def request(conn, path, headers):
    start = time.perf_counter()
    conn.request("GET", path, headers={"Accept-Encoding": "gzip, br", **headers})
    r = conn.getresponse()
    ttfb = time.perf_counter() - start
    body = r.read()
    total = time.perf_counter() - start
    return r, body, ttfb, total


def decode(body, encoding):
    if encoding == "gzip":
        return gzip.decompress(body)
    if encoding == "br":
        return brotli.decompress(body)
    assert encoding is None, f"unknown content-encoding {encoding}"
    return body


def network(base, path, n):
    u = urlparse(base)
    conn = http.client.HTTPSConnection(u.netloc, timeout=30)
    r, body, ttfb, total = request(conn, path, {})  # first request: may be a cold start, not in the stats
    assert r.status == 200, (path, r.status, body[:200])
    h = {k.lower(): v for k, v in r.getheaders()}
    out = {
        "status": r.status,
        "first_request_ms": ms(total),
        "body_wire_bytes": len(body),
        "body_decoded_bytes": len(decode(body, h.get("content-encoding"))),
        "header_bytes": len(f"HTTP/1.1 {r.status} {r.reason}\r\n") + sum(len(f"{k}: {v}\r\n") for k, v in r.getheaders()) + 2,
        "content_encoding": h.get("content-encoding", "none"),
        "cache_control": h.get("cache-control", "none"),
        "etag": h.get("etag"),
        "last_modified": h.get("last-modified"),
    }
    validator = {"If-None-Match": h["etag"]} if "etag" in h else {"If-Modified-Since": h["last-modified"]} if "last-modified" in h else None
    if validator:
        time.sleep(GAP_S)
        r2, body2, _, _ = request(conn, path, validator)
        out["conditional_status"] = r2.status
        out["conditional_wire_bytes"] = len(body2)
    else:
        out["conditional_status"] = "no validator"
    ttfbs, totals, statuses = [], [], []
    reused = 0
    for _ in range(n):
        time.sleep(GAP_S)
        reused += conn.sock is not None
        r, body, ttfb, total = request(conn, path, {})
        statuses.append(r.status)
        if r.status == 200:
            ttfbs.append(ttfb)
            totals.append(total)
    conn.close()
    out["reused_connection"] = reused
    out["statuses"] = {s: statuses.count(s) for s in sorted(set(statuses))}
    out["ttfb_ms"] = {"median": ms(statistics.median(ttfbs)), "p90": ms(pct(ttfbs, 90))}
    out["total_ms"] = {"median": ms(statistics.median(totals)), "p90": ms(pct(totals, 90))}
    return out


# 2. Lambda REPORT lines

def lambda_logs(hours):
    now = time.time()
    raw = subprocess.run(
        ["aws", "--profile", PROFILE, "--region", REGION, "logs", "filter-log-events", "--log-group-name", f"/aws/lambda/{FUNCTION}",
         "--filter-pattern", '"REPORT RequestId"', "--start-time", str(int((now - hours * 3600) * 1000)), "--output", "json"],
        check=True, capture_output=True, text=True).stdout
    events = sorted(json.loads(raw)["events"], key=lambda e: e["timestamp"])
    rows = []
    for e in events:
        f = dict(re.findall(r"(Duration|Billed Duration|Memory Size|Max Memory Used|Init Duration): ([\d.]+)", e["message"]))
        rows.append({"t": e["timestamp"] / 1000, "duration": float(f["Duration"]), "billed": float(f["Billed Duration"]),
                     "memory": int(f["Memory Size"]), "init": float(f["Init Duration"]) if "Init Duration" in f else None})
    assert rows, f"no REPORT lines in the last {hours} h"
    memory = rows[-1]["memory"]
    first = max(i for i, r in enumerate(rows) if r["memory"] != memory) + 1 if any(r["memory"] != memory for r in rows) else 0
    rows = rows[first:]  # only the invocations since the memory size last changed
    span_h = (now - rows[0]["t"]) / 3600
    cold = [r for r in rows if r["init"] is not None]
    warm_data = [r["duration"] for r in rows if r["init"] is None and r["duration"] >= 50]

    def dist(xs):
        return {"n": len(xs), "median": round(statistics.median(xs), 1), "p90": round(pct(xs, 90), 1), "max": round(max(xs), 1)} if xs else {"n": 0}
    return {
        "memory_mb": memory,
        "hours": round(span_h, 2),
        "invocations": len(rows),
        "invocations_per_hour": round(len(rows) / span_h),
        "gb_seconds_per_hour": round(sum(r["billed"] for r in rows) / 1000 * memory / 1024 / span_h, 1),
        "cold_starts": len(cold),
        "init_ms": dist([r["init"] for r in cold]),
        "cold_first_request_ms": dist([r["duration"] for r in cold if r["duration"] >= 50]),
        "warm_data_ms": dist(warm_data),
        "under_50ms": sum(1 for r in rows if r["duration"] < 50),
    }


# 3. Client

class CDP:
    def __init__(self, ws):
        self.ws = ws
        self.id = 0
        self.events = []

    def call(self, method, **params):
        self.id += 1
        self.ws.send(json.dumps({"id": self.id, "method": method, "params": params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == self.id:
                assert "error" not in m, (method, m["error"])
                return m["result"]
            self.events.append(m)

    def pump(self, seconds):
        end = time.monotonic() + seconds
        while (left := end - time.monotonic()) > 0:
            try:
                self.events.append(json.loads(self.ws.recv(timeout=left)))
            except TimeoutError:
                return

    def js(self, expr):
        r = self.call("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
        assert "exceptionDetails" not in r, r["exceptionDetails"]
        return r["result"].get("value")


def requests_between(events, url_part):
    """Network requests in a slice of CDP events: (url, encodedDataLength) of each finished request."""
    urls = {e["params"]["requestId"]: e["params"]["request"]["url"] for e in events if e.get("method") == "Network.requestWillBeSent"}
    done = [(urls.get(e["params"]["requestId"], "?"), e["params"]["encodedDataLength"]) for e in events if e.get("method") == "Network.loadingFinished"]
    return [d for d in done if url_part in d[0]]


def classify(e):
    name, cat = e["name"], e.get("cat", "")
    if "GC" in name or "gc" in cat.split(","):
        return "gc"
    if name in {"UpdateLayoutTree", "Layout", "RecalculateStyles", "InvalidateLayout", "ScheduleStyleRecalculation", "ParseAuthorStyleSheet"}:
        return "style_layout"
    if name in {"Paint", "PrePaint", "Layerize", "PaintImage", "UpdateLayer", "UpdateLayerTree", "CompositeLayers", "Commit", "Decode Image"}:
        return "paint"
    if name in {"EvaluateScript", "FunctionCall", "TimerFire", "EventDispatch", "FireAnimationFrame", "RunMicrotasks", "XHRLoad",
                "FireIdleCallback", "CompileScript", "ParseScript"} or name.startswith(("v8.", "V8.")):
        return "script"
    return "other"


def self_times(evs):
    """Self time (us) of each complete event on one thread: its duration minus that of its direct children."""
    out, stack = [], []
    for e in sorted(evs, key=lambda e: (e["ts"], -e["dur"])):
        while stack and stack[-1][0]["ts"] + stack[-1][0]["dur"] <= e["ts"]:
            out.append(stack.pop())
        if stack:
            parent = stack[-1][0]
            stack[-1][1] -= min(e["dur"], parent["ts"] + parent["dur"] - e["ts"])
        stack.append([e, e["dur"]])
    return out + stack


def main_thread_cost(timed, t0, t1):
    """Main-thread time in [t0, t1) us of trace time: totals by kind (ms) and the longest top-level task (ms)."""
    inside = [(e, s) for e, s in timed if t0 <= e["ts"] < t1]
    kinds = {k: 0.0 for k in ("script", "style_layout", "paint", "gc", "other")}
    for e, s in inside:
        kinds[classify(e)] += s / 1000
    tasks = [e["dur"] / 1000 for e, _ in inside if e["name"] in ("RunTask", "ThreadControllerImpl::RunTask")]
    return {"busy": round(sum(kinds.values()), 1), **{k: round(v, 1) for k, v in kinds.items()},
            "longest_task": round(max(tasks), 1) if tasks else 0}


def profile_functions(profile, page_url, polls, top=8):
    """Self and inclusive time per function per poll (ms) from a sampled CPU profile."""
    nodes = {n["id"]: n for n in profile["nodes"]}
    parent = {c: n["id"] for n in profile["nodes"] for c in n.get("children", [])}

    def key(n):
        f = n["callFrame"]
        name = f["functionName"] or "(anonymous)"
        return f"{name}:{f['lineNumber'] + 1}" if f["url"] == page_url else name if not f["url"] else f"{name} ({f['url'].rsplit('/', 1)[-1]})"
    self_t, incl_t = {}, {}
    for sample, dt in zip(profile["samples"], profile["timeDeltas"][1:] + [0]):
        k = key(nodes[sample])
        self_t[k] = self_t.get(k, 0) + dt
        seen, i = set(), sample
        while i is not None:
            seen.add(key(nodes[i]))
            i = parent.get(i)
        for k in seen:
            incl_t[k] = incl_t.get(k, 0) + dt
    skip = {"(idle)", "(root)", "(program)"}

    def rank(d):
        return [[k, round(v / 1000 / polls, 2)] for k, v in sorted(d.items(), key=lambda kv: -kv[1]) if k not in skip][:top]
    return {"self_ms_per_poll": rank(self_t), "inclusive_ms_per_poll": rank(incl_t)}


OBSERVER = """
new MutationObserver((_, o) => { if (document.querySelector(%s)) { performance.mark("board-data"); o.disconnect(); } })
  .observe(document, {childList: true, subtree: true});
window.__longtasks = [];
new PerformanceObserver(l => window.__longtasks.push(...l.getEntries().map(e => Math.round(e.duration)))).observe({type: "longtask", buffered: true});
"""
HIDE = """
Object.defineProperty(document, "visibilityState", {get: () => "hidden", configurable: true});
Object.defineProperty(document, "hidden", {get: () => true, configurable: true});
document.dispatchEvent(new Event("visibilitychange"));
"""


def client(base, ready, trace_path):
    page_url = base.rstrip("/") + "/"
    profile_dir = tempfile.mkdtemp(prefix="bench-chrome-")
    chrome = subprocess.Popen([CHROME, "--headless=new", "--remote-debugging-port=0", f"--user-data-dir={profile_dir}",
                               "--window-size=1440,900", "--no-first-run", "--no-default-browser-check", "about:blank"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    port_file = Path(profile_dir) / "DevToolsActivePort"
    for _ in range(100):
        if port_file.exists() and port_file.read_text().strip():
            break
        time.sleep(0.1)
    port = port_file.read_text().split()[0]
    page = next(t for t in json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list")) if t["type"] == "page")
    with connect(page["webSocketDebuggerUrl"], max_size=None, open_timeout=30) as ws:
        cdp = CDP(ws)
        cdp.call("Network.enable")
        cdp.call("Page.enable")
        cdp.call("Page.addScriptToEvaluateOnNewDocument", source=OBSERVER % json.dumps(ready))
        cdp.call("Tracing.start", categories=TRACE_CATEGORIES, transferMode="ReportEvents")

        # Load: navigation until the first row of data exists
        cdp.call("Page.navigate", url=page_url)
        for _ in range(600):
            cdp.pump(0.1)
            if cdp.js('performance.getEntriesByName("board-data").length'):
                break
        else:
            raise AssertionError(f"no element matches {ready} 60 s after navigation")
        cdp.pump(1.0)
        load_end = len(cdp.events)
        marks = cdp.js("""({paint: Object.fromEntries(performance.getEntriesByType("paint").map(e => [e.name, e.startTime])),
                            ready: performance.getEntriesByName("board-data")[0].startTime, longtasks: window.__longtasks.slice()})""")

        # The open tab: 60 s of polling, traced and CPU-profiled
        cdp.call("Profiler.enable")
        cdp.call("Profiler.setSamplingInterval", interval=200)
        cdp.call("Profiler.start")
        cdp.pump(POLL_WINDOW_S)
        profile = cdp.call("Profiler.stop")["profile"]
        window_end = len(cdp.events)
        cdp.call("Tracing.end")
        while not any(e.get("method") == "Tracing.tracingComplete" for e in cdp.events[window_end:]):
            cdp.pump(1.0)
        trace = [t for e in cdp.events if e.get("method") == "Tracing.dataCollected" for t in e["params"]["value"]]
        if trace_path:
            Path(trace_path).write_text(json.dumps({"traceEvents": trace}))

        # Hidden
        hidden_start = len(cdp.events)
        cdp.js(HIDE)
        cdp.pump(HIDDEN_WINDOW_S)
        hidden_polls = sum(1 for e in cdp.events[hidden_start:] if e.get("method") == "Network.requestWillBeSent"
                           and urlparse(e["params"]["request"]["url"]).path == "/data")
    chrome.terminate()
    chrome.wait()
    shutil.rmtree(profile_dir)

    # Trace: the renderer main thread is the one that sent /data
    sends = [e for e in trace if e["name"] == "ResourceSendRequest"]
    data_sends = [e for e in sends if urlparse(e["args"]["data"]["url"]).path == "/data"]
    main = (data_sends[0]["pid"], data_sends[0]["tid"])
    nav = [e for e in trace if e["name"] == "navigationStart" and e["pid"] == main[0]
           and e["args"].get("data", {}).get("documentLoaderURL", "").startswith("http")][-1]["ts"]
    ready_ts = [e for e in trace if e["name"] == "board-data"][0]["ts"]
    timed = self_times([e for e in trace if (e["pid"], e["tid"]) == main and e.get("ph") == "X" and "dur" in e])
    load = main_thread_cost(timed, nav, ready_ts + 1e6)
    polls = [main_thread_cost(timed, a["ts"], b["ts"]) for a, b in zip(data_sends[1:], data_sends[2:])]  # whole cycles after the first render
    assert polls, "fewer than 3 /data requests in the trace"

    window = requests_between(cdp.events[load_end:window_end], "")
    window_polls = sum(1 for u, _ in window if urlparse(u).path == "/data")
    load_reqs = requests_between(cdp.events[:load_end], "")
    finishes = {e["args"]["data"]["requestId"]: e["ts"] for e in trace if e["name"] == "ResourceFinish"}
    fonts = []
    for e in sends:
        url = e["args"]["data"]["url"]
        if "fonts.g" in url:
            fonts.append({"url": url[:100], "render_blocking": e["args"]["data"].get("renderBlocking"),
                          "wire_bytes": sum(b for u, b in load_reqs + window if u == url),
                          "finished_ms": round((finishes[e["args"]["data"]["requestId"]] - nav) / 1000, 1)})
    return {
        "first_paint_ms": round(marks["paint"]["first-paint"], 1),
        "first_contentful_paint_ms": round(marks["paint"]["first-contentful-paint"], 1),
        "board_data_ms": round(marks["ready"], 1),
        "load": load,
        "load_requests": len(load_reqs),
        "load_wire_bytes": sum(b for _, b in load_reqs),
        "longtasks_during_load_ms": marks["longtasks"],
        "polls": polls,
        "poll_median": {k: round(statistics.median(p[k] for p in polls), 1) for k in polls[0]},
        "window_s": POLL_WINDOW_S,
        "window_requests": len(window),
        "window_data_requests": window_polls,
        "window_wire_bytes": sum(b for _, b in window),
        "functions": profile_functions(profile, page_url, window_polls),
        "hidden_method": "document.visibilityState='hidden' and document.hidden=true overridden, visibilitychange dispatched",
        "hidden_window_s": HIDDEN_WINDOW_S,
        "hidden_data_requests": hidden_polls,
        "fonts": fonts,
    }


def table(res):
    rows = []
    for path, r in res["network"].items():
        rows += [
            (f"net {path}", "body on wire / decoded", f"{r['body_wire_bytes']:,} / {r['body_decoded_bytes']:,} B"),
            (f"net {path}", "response headers", f"{r['header_bytes']:,} B"),
            (f"net {path}", "content-encoding", r["content_encoding"]),
            (f"net {path}", "cache-control", r["cache_control"]),
            (f"net {path}", "ETag / Last-Modified", f"{r['etag'] or 'none'} / {r['last_modified'] or 'none'}"),
            (f"net {path}", "conditional re-request", str(r["conditional_status"])),
            (f"net {path}", "first request (maybe cold)", f"{r['first_request_ms']} ms"),
            (f"net {path}", f"TTFB median / p90 (n={sum(r['statuses'].values())})", f"{r['ttfb_ms']['median']} / {r['ttfb_ms']['p90']} ms"),
            (f"net {path}", "total median / p90", f"{r['total_ms']['median']} / {r['total_ms']['p90']} ms"),
            (f"net {path}", "statuses, kept-alive connection", " ".join(f"{k}x{v}" for k, v in r["statuses"].items()) + f", {r['reused_connection']}/{sum(r['statuses'].values())} reused"),
        ]
    lam = res["lambda"]
    rows += [
        ("lambda", "window / memory", f"{lam['hours']} h at {lam['memory_mb']} MB"),
        ("lambda", "invocations / per hour", f"{lam['invocations']:,} / {lam['invocations_per_hour']:,}"),
        ("lambda", "billed GB-s per hour", f"{lam['gb_seconds_per_hour']}"),
        ("lambda", "cold starts", str(lam["cold_starts"])),
        ("lambda", "Init Duration median / max", f"{lam['init_ms'].get('median')} / {lam['init_ms'].get('max')} ms"),
        ("lambda", f"first /data after init median / max (n={lam['cold_first_request_ms']['n']})",
         f"{lam['cold_first_request_ms'].get('median')} / {lam['cold_first_request_ms'].get('max')} ms"),
        ("lambda", f"warm /data Duration median / p90 / max (n={lam['warm_data_ms']['n']})",
         f"{lam['warm_data_ms'].get('median')} / {lam['warm_data_ms'].get('p90')} / {lam['warm_data_ms'].get('max')} ms"),
        ("lambda", "invocations under 50 ms (/ and the like)", str(lam["under_50ms"])),
    ]
    c = res["client"]
    pm = c["poll_median"]
    rows += [
        ("client", "first paint / first contentful paint", f"{c['first_paint_ms']} / {c['first_contentful_paint_ms']} ms"),
        ("client", "first row of data in the DOM", f"{c['board_data_ms']} ms"),
        ("client", "load: requests / bytes on wire", f"{c['load_requests']} / {c['load_wire_bytes']:,} B"),
        ("client", "load: main thread busy / JS", f"{c['load']['busy']} / {c['load']['script']} ms"),
        ("client", "load: longest task", f"{c['load']['longest_task']} ms"),
        ("client", f"per poll (median of {len(c['polls'])}): busy", f"{pm['busy']} ms"),
        ("client", "per poll: script / style+layout / paint / gc / other",
         f"{pm['script']} / {pm['style_layout']} / {pm['paint']} / {pm['gc']} / {pm['other']} ms"),
        ("client", "per poll: longest task", f"{pm['longest_task']} ms"),
        ("client", f"open tab {c['window_s']} s: requests (/data) / bytes",
         f"{c['window_requests']} ({c['window_data_requests']}) / {c['window_wire_bytes']:,} B"),
        ("client", f"hidden {c['hidden_window_s']} s: /data requests", str(c["hidden_data_requests"])),
    ]
    rows += [("client", "top self time per poll", ", ".join(f"{k} {v}" for k, v in c["functions"]["self_ms_per_poll"][:5]) + " ms")]
    rows += [("client", "top inclusive per poll", ", ".join(f"{k} {v}" for k, v in c["functions"]["inclusive_ms_per_poll"][:5]) + " ms")]
    for f in c["fonts"]:
        rows.append(("font", f["url"][:60], f"{f['wire_bytes']:,} B, {f['render_blocking']}, done {f['finished_ms']} ms"))
    w = [max(len(r[i]) for r in rows) for i in range(3)]
    return "\n".join(f"{a:<{w[0]}}  {b:<{w[1]}}  {c_}" for a, b, c_ in rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("base", help="e.g. https://monitor.invariant.team")
    ap.add_argument("--n", type=int, default=20, help="warm requests per endpoint")
    ap.add_argument("--hours", type=float, default=3, help="how far back to read the Lambda REPORT lines")
    ap.add_argument("--ready", default=".board [data-key]", help="CSS selector whose first match means the board shows data")
    ap.add_argument("--json", help="write all numbers to this file")
    ap.add_argument("--trace", help="write the Chrome trace of load + 60 s here (opens in the DevTools Performance panel)")
    a = ap.parse_args()
    res = {"base": a.base, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "n": a.n,
           "network": {p: network(a.base, p, a.n) for p in ("/", "/data")},
           "lambda": lambda_logs(a.hours),
           "client": client(a.base, a.ready, a.trace)}
    print(table(res))
    if a.json:
        Path(a.json).write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
