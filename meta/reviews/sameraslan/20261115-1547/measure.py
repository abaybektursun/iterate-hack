# Command (from the repository root): python3 meta/reviews/sameraslan/20261115-1547/measure.py > meta/reviews/sameraslan/20261115-1547/before.txt
# Reads cycle.txt of this folder, the board, git and Modal's app history. Starts no job.
import re, subprocess, datetime as dt, pathlib
here = pathlib.Path(__file__).parent
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.rstrip()
def z(t): return t.strftime("%H:%M:%SZ")

print("## 1. Runner deployed in this workspace against origin/main")
print(sh("uv run modal app history iterate-runner 2>&1 | grep -E 'v[0-9]'"))
print("runner commits of origin/main after d02eebc (v4):", sh("git log --format=%h d02eebc..origin/main -- infra/runner.py | wc -l").strip())
print(sh("git log --format='%h %cI %s' d02eebc..origin/main -- infra/runner.py | cut -c1-120"))
for c in ("d02eebc", "63a76e6", "132d10f", "origin/main"):
    print("blob of infra/runner.py at", c, sh(f"git rev-parse --short {c}:infra/runner.py"))

print("\n## 2. Job ends (submit time of the id, PST, plus 8 h, plus wait, plus run; cycle.txt)")
ends = {}
for line in (here / "cycle.txt").read_text().splitlines():
    m = re.match(r"\s+sameraslan-1114-(\d{6})-(\w{4})\s+(.*?)\s+NVIDIA H100\s+([\d.]+)\s+([\d.]+|-)\s+(.*)", line)
    if not m: continue
    hms, tag, state, wait, run, cmd = m.groups()
    sub = dt.datetime(2026, 11, 14, int(hms[:2]), int(hms[2:4]), int(hms[4:])) + dt.timedelta(hours=8)
    end = sub + dt.timedelta(minutes=float(wait) + (float(run) if run != "-" else 0))
    ends[tag] = (sub, end)
    if tag in ("d05c", "f46b", "2e30", "7014", "aa97", "36e7", "b300", "82fa", "5d2f"):
        flags = " ".join(re.findall(r"--(?:samples|restarts|hours|temperature|seed|set)\s+\S+", cmd))
        print(tag, state[:28], "submit", z(sub), "wait", wait, "run", run, "end", z(end), "|", flags)
print("7014 submit to 5d2f submit, min:", round((ends["5d2f"][0] - ends["7014"][0]).total_seconds() / 60, 1))
print("36e7 submit to 5d2f submit, min:", round((ends["5d2f"][0] - ends["36e7"][0]).total_seconds() / 60, 1))
print(sh(f"tail -6 {here}/cycle.txt | grep -E 'container minutes'"))

print("\n## 3. Board item times and the nearest job end before each")
t = {}
for i in ("result-6de887", "result-d92d4a", "result-460e0a", "result-79784b", "result-666223"):
    head = sh(f"uv run tools/board.py show {i} 2>&1 | head -4")
    t[i] = dt.datetime.strptime(re.search(r"at (2026-\S+Z)", head).group(1), "%Y-%m-%dT%H:%M:%SZ")
    body = [l for l in head.splitlines()[1:] if l.strip() and not l.startswith("+")]
    print(i, z(t[i]), "|", body[0][:150] if body else "")
for tag, i in (("d05c", "result-460e0a"), ("f46b", "result-79784b"), ("5d2f", "result-666223")):
    print(tag, "end to", i, "min:", round((t[i] - ends[tag][1]).total_seconds() / 60, 1))
c = dt.datetime(2026, 11, 15, 7, 6, 41)
print("2e30 end to the comment of 07:06:41Z on result-79784b, min:", round((c - ends["2e30"][1]).total_seconds() / 60, 1))
print("result-6de887 to result-666223, min:", round((t["result-666223"] - t["result-6de887"]).total_seconds() / 60, 1))
print("result-d92d4a to result-666223, min:", round((t["result-666223"] - t["result-d92d4a"]).total_seconds() / 60, 1))

print("\n## 4. Commits of tools/finding_loop_neurons.py on origin/main (UTC)")
print(sh("TZ=UTC git log --date=format-local:%Y-%m-%dT%H:%M:%SZ --format='%h %cd %an' origin/main -- tools/finding_loop_neurons.py"))

print("\n## 5. Rows of meta/FAILURES.md: is the cause still in place")
print("finding pages with requestAnimationFrame and no setTimeout:", sh("for f in tools/finding_*.py; do grep -q requestAnimationFrame $f && ! grep -q 'setTimeout(' $f && echo $f; done | tr '\\n' ' '"))
print("finding pages:", sh("ls tools/finding_*.py | wc -l").strip())
print("hook lines of .claude/settings.json naming git pull:", sh("grep -c 'git pull' .claude/settings.json") or "0")

print("\n## 6. Scripts and readout of the four-sample cell")
print(sh("git ls-files | grep -E 'run_cell|vote_pair|readout' | grep -v results/ | head"))
import json
d = json.load(open("studies/cleanneurons/results/gen/readout_vote_t06.json"))
print("keys:", list(d))
for s in d["per_sample"]:
    print("sample", s["sample"], "unedited", s["unedited"]["right_v3"], "loops", s["unedited"]["loops_rule_A"], "edited", s["edited"]["right_v3"], "points", s["points_edited_minus_unedited"], [round(x, 1) for x in s["interval95"]])
for k in d:
    if k not in ("note", "setting", "grader", "runs", "per_sample"):
        print(k, json.dumps(d[k])[:420])
