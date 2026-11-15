"""One review run inside an arena: a fresh headless Claude Code session in the arena's repository, given one sentence.

  MH_HOME=<dir> python3 -m studies.metaharness.prep.review <arena id> <round 1..3>

The session gets the arm's prompt (lib/arena.py PROMPTS) and nothing else. It loads the arena's own project files
(AGENTS.md, .claude/settings.json with its hooks, .claude/skills) and no user-level settings, memory, skills or MCP
servers. The pastdotdev plugin is switched off so the session is not written to the team's memory. Tools: Bash, Read,
Edit, Write, Glob, Grep, Skill. Limits: 90 turns, 40 minutes.

After the session: a change left uncommitted is committed by this script, a branch it left unmerged is merged into
the work branch, and both are recorded; the next window runs whatever the work branch then holds.
"""
import json
import subprocess
import sys
import time

from studies.metaharness.lib import arena as A

arena_id, round_index = sys.argv[1], int(sys.argv[2])
arena = A.load(arena_id)
repo = A.repo(arena_id)
out = A.state_dir(arena_id) / f"review{round_index}"
assert not out.exists(), f"{out} exists: a review is never rerun in place"
out.mkdir(parents=True)
env = A.env(arena)
before = A.git(arena_id, "rev-parse", "HEAD")
command = ["gtimeout", "2400", "claude", "-p", A.PROMPTS[arena["arm"]], "--model", A.MODEL, "--max-turns", "90",
           "--output-format", "json", "--setting-sources", "project,local",
           "--settings", json.dumps({"enabledPlugins": {"pastdotdev@pastdotdev": False}}),
           "--strict-mcp-config", "--mcp-config", json.dumps({"mcpServers": {}}),
           "--allowedTools", "Bash", "Read", "Edit", "Write", "Glob", "Grep", "Skill",
           "--disallowedTools", "Agent", "Task", "WebSearch", "WebFetch", "--permission-mode", "acceptEdits"]
t0 = time.time()
done = subprocess.run(command, cwd=repo, env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL)
t1 = time.time()
(out / "stdout.json").write_text(done.stdout)
(out / "stderr.txt").write_text(done.stderr)
try:
    session = json.loads(done.stdout)
except json.JSONDecodeError:
    session = {"result": None, "error": f"exit {done.returncode}, output is not JSON"}

record = {"arena": arena_id, "round": round_index, "arm": arena["arm"], "prompt": A.PROMPTS[arena["arm"]], "model": A.MODEL,
          "command": command, "t0": t0, "t1": t1, "minutes": round((t1 - t0) / 60, 1), "exit_code": done.returncode,
          "before": before, "turns": session.get("num_turns"), "cost_usd": session.get("total_cost_usd"),
          "session_id": session.get("session_id"), "usage": session.get("usage"), "harness": []}

branch = A.git(arena_id, "rev-parse", "--abbrev-ref", "HEAD")
status = A.git(arena_id, "status", "--porcelain")
if status:
    A.git(arena_id, "add", "-A")
    A.git(arena_id, "commit", "-q", "-m", "change left uncommitted by the review session")
    record["harness"].append(f"committed for the session (it left the tree dirty on {branch}):\n{status}")
if branch != A.BRANCH:
    A.git(arena_id, "switch", "-q", A.BRANCH)
    record["harness"].append(f"switched back from {branch}")
A.git(arena_id, "fetch", "-q", "origin")
for line in A.git(arena_id, "branch", "-a", "--no-merged", A.BRANCH, "--format=%(refname:short)").splitlines():
    if line and not line.endswith("/HEAD"):
        merged = A.sh(["git", "merge", "-q", "--no-edit", line], repo, env, check=False)
        record["harness"].append(f"merged {line} into {A.BRANCH}: exit {merged.returncode} {merged.stderr.strip()[:200]}")
        if merged.returncode != 0:
            A.git(arena_id, "merge", "--abort", check=False)
A.git(arena_id, "push", "-q", "origin", A.BRANCH)
after = A.git(arena_id, "rev-parse", "HEAD")
record["after"] = after
(out / "final_message.md").write_text(session.get("result") or "")
(out / "commits.txt").write_text(A.git(arena_id, "log", "--format=%h %an %ad %s", "--date=iso", f"{before}..{after}"))
(out / "change.diff").write_text(A.git(arena_id, "diff", before, after))
(out / "files.txt").write_text(A.git(arena_id, "diff", "--stat", before, after))
entry = repo / "meta" / "dana.md"
if entry.exists():
    (out / "meta_entry.md").write_text(entry.read_text())
jobs = A.dump_jobs(arena, t0 - 5, t1 + 5)
(out / "jobs.json").write_text(json.dumps(jobs, indent=1))
record["jobs"] = len(jobs)
record["job_minutes"] = round(sum((r["end"]["at"] - r["start"]["at"]) / 60 for r in jobs if "end" in r and "start" in r), 2)
(out / "review.json").write_text(json.dumps(record, indent=1))
print(json.dumps({k: record[k] for k in ("arena", "round", "arm", "minutes", "turns", "cost_usd", "jobs", "exit_code", "harness")}))
