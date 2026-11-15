# python3 meta/reviews/sameraslan/20261115-0713/hooktest.py <session c97b34e7 transcript .jsonl> > before.txt (after.txt)
# Feeds every `git pull` / `git merge` Bash command of the session, plus fixed controls, to each PreToolUse hook
# of .claude/settings.json whose matcher fits Bash, and prints the exit code (2 = refused, 0 or no hook = allowed).
import json, re, subprocess, sys

settings = json.load(open(".claude/settings.json"))
hooks = [h["command"] for e in settings.get("hooks", {}).get("PreToolUse", [])
         if re.fullmatch(e.get("matcher", ".*") or ".*", "Bash") for h in e["hooks"]]
print("PreToolUse hooks for Bash:", len(hooks))

cmds = []
for line in open(sys.argv[1]):
    r = json.loads(line)
    c = (r.get("message") or {}).get("content")
    if r.get("type") == "assistant" and isinstance(c, list):
        for b in c:
            if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "Bash":
                cmd = b["input"].get("command", "")
                if re.search(r"git (pull|merge)\b", cmd):
                    cmds.append(("session " + r["timestamp"][11:19], cmd))
controls = [("control plain pull", "git pull origin main"),
            ("control pull then log piped", "git pull -q origin main && git log --oneline | head -3"),
            ("control pull or-else", "git pull origin main || echo failed"),
            ("control piped log", "git log --oneline -5 | head"),
            ("control piped merge", "git merge origin/main 2>&1 | tail -3")]
for name, cmd in cmds + controls:
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}})
    codes = [subprocess.run(h, shell=True, input=payload, capture_output=True, text=True,
                            env={"CLAUDE_PROJECT_DIR": ".", "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"}).returncode
             for h in hooks]
    verdict = "refused" if 2 in codes else "allowed"
    print(f"{name}: {verdict} {codes} | {cmd[:90].replace(chr(10), ' ')}")
