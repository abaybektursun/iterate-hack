"""Serve the visualization prototypes of studies/sitelab with the team site's live data.

  python3 studies/sitelab/serve.py [port]     (default 8777)

Static files come from this folder; /data and /data/<id> are passed through to https://monitor.invariant.team, so a
prototype fetches '/data' exactly as a page of tools/view.py does.
"""
import http.server, os, sys, urllib.request

SITE = "https://monitor.invariant.team"
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class H(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/data" or self.path.startswith("/data/"):
            with urllib.request.urlopen(SITE + self.path, timeout=20) as r:
                body = r.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass


http.server.ThreadingHTTPServer(("127.0.0.1", int(sys.argv[1]) if len(sys.argv) > 1 else 8777), H).serve_forever()
