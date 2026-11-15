# Command (from the repository root): uv run python meta/reviews/sameraslan/20261115-0542/measure.py > meta/reviews/sameraslan/20261115-0542/before.txt
# Reads only: Modal app history, git, the job records (tools/gpu.py load), job logs on the Volume, board items.
# 1. the runner deployed in this workspace against the runner commits on origin/main
# 2. setup_vllm.sh seconds per vLLM job of sameraslan submitted after a76a56a (runner image holds the vLLM environment)
# 3. jobs hit by a failure whose runner fix was already in git
# 4. minutes from a job's end record to the board item of its result, study cleanneurons
import re, subprocess, sys, time

sys.path.insert(0, "tools")
import gpu
import modal

DEPLOYED = "7be6204"  # column Commit of the newest row of `modal app history iterate-runner`
WHO = "sameraslan"


def sh(*a):
    return subprocess.run(a, capture_output=True, text=True).stdout.strip()


def utc(s):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(s))


def epoch(iso):
    return int(subprocess.run(["date", "-j", "-u", "-f", "%Y-%m-%dT%H:%M:%SZ", iso, "+%s"], capture_output=True, text=True).stdout)


recs = gpu.load()
runs = modal.Volume.from_name("iterate-runs")

print("## 1. deployed runner (uv run modal app history iterate-runner)")
print(sh("uv", "run", "modal", "app", "history", "iterate-runner"))
log = sh("git", "log", "--no-merges", "--format=%h %cI %s", f"{DEPLOYED}..origin/main", "--", "infra/runner.py")
print(f"\nrunner commits on origin/main after {DEPLOYED} (git log --no-merges {DEPLOYED}..origin/main -- infra/runner.py):")
print("\n".join(line[:150] for line in log.splitlines()))
print("runner commits not deployed:", len(log.splitlines()))

print("\n## 2. setup_vllm.sh seconds per vLLM job submitted after a76a56a (2026-11-15T04:08:15Z)")
t_image = epoch("2026-11-15T04:08:15Z")
secs = []
for r in sorted(recs.values(), key=lambda r: r["job"]["at"]):
    j = r["job"]
    if j["who"] != WHO or "setup_vllm.sh" not in j["cmd"] or j["at"] < t_image or "start" not in r:
        continue
    try:
        text = b"".join(runs.read_file(f"{r['id']}/log")).decode(errors="replace")
    except FileNotFoundError:
        text = ""
    m = re.search(r"setup_vllm\.sh: (\d+) s", text)
    s = int(m.group(1)) if m else None
    if s is not None:
        secs.append(s)
    print(r["id"], utc(j["at"]), gpu.state(r)[:40], "setup_s", s)
if secs:
    secs.sort()
    print(f"jobs with a setup line: {len(secs)}; median {secs[len(secs) // 2]} s; sum {sum(secs) / 60:.1f} min")

print("\n## 3. failures after their runner fix was in git")
for tail, fix, what in (("57fb", "aa9166a 2026-11-15T02:16:01Z", "restart"), ("5a4d", "aa9166a 2026-11-15T02:16:01Z", "restart"), ("5442", "539d0c6 2026-11-15T02:38:53Z", "stale Volume view")):
    r = next(r for r in recs.values() if r["id"].endswith(tail) and r["job"]["who"] == WHO)
    end = r.get("end", {}).get("at")
    print(r["id"], "fix", fix, "| start record", utc(r["start"]["at"]), "| end", utc(end) if end else "-", "| state", gpu.state(r)[:60], "|", what)
w = next(r for r in recs.values() if r["id"].endswith("9d69"))
print("writer of the file 5442 read:", w["id"], "end record", utc(w["end"]["at"]), "exit", w["end"]["exit_code"])

print("\n## 4. job end record to board item, study cleanneurons (uv run tools/board.py show <id>)")
for item, tail in (("result-156f7b", "b683"), ("result-904bbf", "a93d"), ("result-4227c6", "cdc8"), ("result-54f212", "a899"), ("result-6de887", "cf9f"), ("result-2048b1", "4022")):
    head = sh("uv", "run", "tools/board.py", "show", item).splitlines()[0]
    at = re.search(r"at (\S+Z)", head).group(1)
    r = next(r for r in recs.values() if r["id"].endswith(tail) and r["job"]["who"] == WHO)
    print(item, "posted", at, "| last job", r["id"], "end", utc(r["end"]["at"]), "| minutes", round((epoch(at) - r["end"]["at"]) / 60, 1))
