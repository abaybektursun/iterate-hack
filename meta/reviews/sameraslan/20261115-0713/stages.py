# python3 meta/reviews/sameraslan/20261115-0713/stages.py <session c97b34e7 transcript .jsonl> > before.txt
# Splits work-c50976 (claim 05:32:31Z, close 07:12:48Z) into stages from the session transcript:
# person messages, assistant tool calls per stage, and Bash calls about merging main.
import json, sys, re
from datetime import datetime

T0, T1 = "2026-11-15T05:32:31", "2026-11-15T07:12:49"
MARKS = [("claim", "2026-11-15T05:32:31"), ("write side done", "2026-11-15T05:47:48"),
         ("page built 8c81801", "2026-11-15T06:10:59"), ("merge 1 d4c2aca", "2026-11-15T06:11:25"),
         ("waiting for review comment", "2026-11-15T06:35:49"), ("f79e5a7", "2026-11-15T07:07:55"),
         ("merge 2 61247bb", "2026-11-15T07:08:32"), ("merge 3 9102249", "2026-11-15T07:11:06"),
         ("close", "2026-11-15T07:12:48")]
MERGE = re.compile(r"git (merge|pull|fetch)|--theirs|--ours|<<<<<<<|merge --abort|conflict", re.I)

def ts(r):
    return (r.get("timestamp") or "")[:19]

rows = [json.loads(l) for l in open(sys.argv[1])]
rows = [r for r in rows if T0 <= ts(r) <= T1]
person, calls = [], []
for r in rows:
    m = r.get("message") or {}
    c = m.get("content")
    if r.get("type") == "user" and not r.get("isMeta"):
        texts = [c] if isinstance(c, str) else [b.get("text", "") for b in (c or []) if isinstance(b, dict) and b.get("type") == "text"]
        texts = [t for t in texts if t.strip() and not t.lstrip().startswith("<")]
        if texts:
            person.append((ts(r), len(" ".join(texts).split())))
    if r.get("type") == "assistant" and isinstance(c, list):
        for b in c:
            if isinstance(b, dict) and b.get("type") == "tool_use":
                inp = json.dumps(b.get("input", {}))
                calls.append((ts(r), b.get("name"), bool(MERGE.search(inp)) and b.get("name") in ("Bash", "Edit", "Read")))

print("section 1: person messages in the window (UTC, word count; text not copied)")
for t, n in person:
    print(" ", t, n, "words")
print("section 2: stages, minutes, tool calls, merge-related calls")
for (a, ta), (b, tb) in zip(MARKS, MARKS[1:]):
    mins = (datetime.fromisoformat(tb) - datetime.fromisoformat(ta)).total_seconds() / 60
    sel = [c for c in calls if ta <= c[0] < tb]
    print(f"  {a} -> {b}: {mins:.1f} min, {len(sel)} tool calls, {sum(c[2] for c in sel)} merge-related")
print("section 3: totals")
print(f"  tool calls {len(calls)}, merge-related {sum(c[2] for c in calls)}")
mt = [c[0] for c in calls if c[2]]
print("  merge-related call times:", " ".join(t[11:] for t in mt))
