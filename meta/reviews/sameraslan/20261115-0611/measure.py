# python3 meta/reviews/sameraslan/20261115-0611/measure.py ~/.claude/projects/<this worktree>/75f8d396-cab4-4ab4-ae90-5e915a78fea3/subagents > before.txt
# (run from the repository root; the transcripts are on sameraslan's machine and in the uploaded traces)
# Section 1: browser tool calls of each subagent of session 75f8d396 (work-99952d), from its transcript.
# Section 2: finding pages and the template: lines that start the frame loop, and a timer that settles the picture
#            when no animation frame fires (a hidden browser pane fires none).
# Section 3: words of the first view that the finding-page skill fixes (PROBLEM, LINE, the five panel names).
import glob, importlib.util, json, os, re, sys

def calls(path):
    out = []
    for line in open(path):
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        content = (rec.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                out.append((rec.get("timestamp", ""), block["name"], block.get("input") or {}))
    return out

def flat(cs):  # a browser_batch counts as its inner actions
    for ts, name, inp in cs:
        if name.endswith("browser_batch"):
            for a in inp.get("actions") or []:
                yield ts, "mcp__Claude_Browser__" + a.get("name", "?"), a.get("input") or {}
        else:
            yield ts, name, inp

folder = sys.argv[1]
print("1. browser tool calls per subagent (a batch counted as its actions)")
print("agent | description | tool calls | browser | screenshot or zoom | javascript_exec | of them naming the frame loop | navigate | first | last")
tot = [0, 0, 0, 0, 0, 0]
for path in sorted(glob.glob(os.path.join(folder, "agent-*.jsonl"))):
    meta = path[:-6] + ".meta.json"
    desc = json.load(open(meta)).get("description", "?") if os.path.exists(meta) else "?"
    cs = calls(path)
    fl = list(flat(cs))
    br = [c for c in fl if "Claude_Browser" in c[1]]
    shots = [c for c in br if c[1].endswith("computer") and c[2].get("action") in ("screenshot", "zoom")]
    js = [c for c in br if c[1].endswith("javascript_tool")]
    nav = [c for c in br if c[1].endswith("navigate")]
    ts = sorted(c[0] for c in cs if c[0])
    loop = [c for c in js if re.search(r"frame\(|requestAnimationFrame|S\.grow|settle\(", json.dumps(c[2]))]
    row = [len(cs), len(br), len(shots), len(js), len(loop), len(nav)]
    if desc.startswith("Build"):
        tot = [a + b for a, b in zip(tot, row)]
    print(os.path.basename(path)[6:14], "|", desc, "|", " | ".join(map(str, row)), "|", ts[0][11:19] if ts else "-", "|", ts[-1][11:19] if ts else "-")
print("the four builders |  |", " | ".join(map(str, tot)))

print("\n2. frame loop start and no-frame timer, per page file")
files = sorted(glob.glob("tools/finding_*.py")) + [".claude/skills/finding-page/template.py", "tools/findings.py"]
n_raf = n_timer = 0
for p in files:
    src = open(p).read()
    raf = len(re.findall(r"requestAnimationFrame\(", src))
    timer = len(re.findall(r"setTimeout\([^\n]*(settle|grow|place|rest)", src))
    n_raf += raf > 0; n_timer += raf > 0 and timer > 0
    print(p, "| requestAnimationFrame calls", raf, "| timer that settles without a frame", timer)
print("files with a frame loop:", n_raf, "| of them with a no-frame timer:", n_timer)

print("\n3. words the skill fixes in the first view")
w = lambda s: len(re.findall(r"\S+", s))
names = ["What is new", "Why it matters", "How we know", "What it does not show", "How to reproduce it"]
print("five panel names:", sum(map(w, names)), "words | limits: PROBLEM 12 + LINE 16 + panel names", sum(map(w, names)), "=", 28 + sum(map(w, names)), "| limit of the first view: 40")
over = 0
for p in sorted(glob.glob("tools/finding_*.py")):
    spec = importlib.util.spec_from_file_location("m", p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    keys = list(m.PANELS) if isinstance(m.PANELS, dict) else [x[0] if isinstance(x, (list, tuple)) else x.get("id") or x.get("name") or x.get("title") for x in m.PANELS]
    n = w(m.PROBLEM) + w(m.LINE) + sum(w(names[i]) for i, k in enumerate(["new", "why", "how", "limits", "run"]) if k in keys)
    over += n > 40
    print(p, "| PROBLEM", w(m.PROBLEM), "| LINE", w(m.LINE), "| panels", len(m.PANELS), "| these three, without the names in the picture:", n)
print("pages over 40 before any name in the picture:", over, "of", len(glob.glob("tools/finding_*.py")))
