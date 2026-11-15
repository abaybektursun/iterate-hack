"""Reduce the local Claude Code transcripts of this repository to data.json for the trace-ribbons prototype.

  python3 studies/sitelab/prototypes/trace-ribbons/build.py

Reads ~/.claude/projects/-home-abay-Projects-iterate-hack*/**/*.jsonl (main sessions and their subagents). Writes,
per transcript ("ribbon"): its parent and spawn time, its tool calls (start, duration from the tool_use record to the
tool_result record, category, a short label, output size in characters) and its state intervals. No prompt, no
output text, no path beyond a file's base name leaves this script.
"""
import glob, json, os, re, sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOTS = glob.glob(str(Path.home() / ".claude" / "projects" / "-home-abay-Projects-iterate-hack*"))
CATS = ["model", "idle", "gpu", "wait", "read", "web", "edit", "board", "git", "agent", "shell", "other", "sub"]
CI = {c: i for i, c in enumerate(CATS)}
KEYS = re.compile(r"past_sk_\w+|sk-[\w-]{20,}|AKIA[0-9A-Z]{16}|gh[pousr]_\w{30,}|hf_\w{30,}|xox[abp]-[\w-]+|\S+@\S+\.\w+")
RUNNERS = {"python3", "python", "uv", "run", "bash", "sh", "node", "timeout", "time", "env", "nohup", "sudo", "exec", "xargs"}
READERS = {"cat", "head", "tail", "sed", "grep", "rg", "ls", "find", "wc", "awk", "jq", "tree", "stat", "file", "diff", "cut", "sort", "du"}
IDLE_GAP = 300  # seconds without any record while no tool call is pending: counted as idle, not as the model writing


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def bash_label(cmd):
    """The verb of a shell command: program base name, plus a script's base name and one subcommand word."""
    cmd = re.sub(r"^\s*(cd\s+\S+\s*(&&|;)\s*)+", "", cmd.strip())
    words = [w for w in re.split(r"\s+", re.split(r"[|;&<>\n]", cmd)[0]) if w and "=" not in w.split("/")[0]]
    out = []
    for w in words:
        if w.startswith("-") or re.fullmatch(r"\d+[smh]?", w):
            continue
        base = os.path.basename(w.strip("'\""))
        if not re.fullmatch(r"[\w.+-]{1,32}", base):
            break
        out.append(base)
        if base not in RUNNERS and len(out) >= 1 and not (len(out) == 1 and base in ("git", "gh", "modal", "aws", "docker", "npm", "pip")):
            if base.endswith((".py", ".sh", ".js", ".mjs")) and len(out) < 6:
                continue  # keep one subcommand word after a script
            break
    out = [w for w in out if w not in RUNNERS] or out[:1]
    label = " ".join(out[-2:]) if out else "shell"
    return {"for": "loop", "while": "loop", "until": "loop"}.get(label, label)


def classify(name, inp):
    """(category, label) of one tool call."""
    if name == "Bash":
        cmd = inp.get("command", "")
        label = bash_label(cmd)
        first = label.split(" ")[0]
        if re.search(r"\b(gpu\.py|vast\.py)\b|\bmodal (run|deploy|app|volume)", cmd):
            cat = "gpu"
        elif re.search(r"msg\.py wait|\bsleep \d", cmd):
            cat = "wait"
        elif re.search(r"\b(board|msg)\.py\b", cmd):
            cat = "board"
        elif first in ("git", "gh"):
            cat = "git"
        elif first in READERS:
            cat = "read"
        elif first in ("curl", "wget", "exa.py"):
            cat = "web"
        else:
            cat = "shell"
        return cat, label
    if name in ("Read", "Grep", "Glob"):
        return "read", os.path.basename(inp.get("file_path") or inp.get("path") or "") or name.lower()
    if name in ("Edit", "Write", "NotebookEdit"):
        return "edit", os.path.basename(inp.get("file_path") or inp.get("notebook_path") or "")
    if name in ("Agent", "Task"):
        return "agent", KEYS.sub("", inp.get("description", ""))[:40]
    if name in ("SendMessage", "TaskStop", "Workflow"):
        return "agent", ""
    if name == "Monitor":
        return "wait", ""
    if name == "WebFetch":
        return "web", re.sub(r"^https?://([^/]+).*", r"\1", inp.get("url", ""))[:40]
    if name == "WebSearch" or "exa" in name:
        return "web", ""
    if name == "Skill":
        return "other", str(inp.get("skill", ""))[:30]
    return "other", ""


def short_tool(name):
    if name.startswith("mcp__"):
        parts = name.split("__")
        return "mcp " + parts[1].replace("claude_ai_", "").replace("claude-in-", "")[:14]
    return name


def size(content):
    if isinstance(content, str):
        return len(content)
    return sum(len(c.get("text", "")) if isinstance(c, dict) else len(str(c)) for c in content or [])


def parse(path):
    recs, calls, by_id, title, tokens, seen_msg = [], [], {}, "", 0, set()
    for line in open(path):
        d = json.loads(line)
        kind = d.get("type")
        if kind == "ai-title":
            title = d.get("aiTitle", "")
        if kind not in ("user", "assistant") or "timestamp" not in d:
            continue
        t = ts(d["timestamp"])
        msg = d["message"]
        content = msg.get("content")
        if kind == "assistant":
            if msg.get("id") not in seen_msg:  # one message is written as several records, each with the same usage
                seen_msg.add(msg.get("id"))
                tokens += (msg.get("usage") or {}).get("output_tokens", 0)
            started = []
            for c in content:
                if c.get("type") == "tool_use":
                    cat, label = classify(c["name"], c.get("input") or {})
                    call = {"id": c["id"], "t": t, "d": None, "cat": cat, "tool": short_tool(c["name"]), "label": label, "out": 0}
                    calls.append(call)
                    by_id[c["id"]] = call
                    started.append(c["id"])
            recs.append((t, "a", started, msg.get("stop_reason") == "end_turn"))
        else:
            done = []
            if isinstance(content, list):
                for c in content:
                    if c.get("type") == "tool_result" and c.get("tool_use_id") in by_id:
                        call = by_id[c["tool_use_id"]]
                        call["d"] = max(0.0, t - call["t"])
                        call["out"] = size(c.get("content"))
                        done.append(c["tool_use_id"])
            recs.append((t, "u", done, False))
    if not recs:
        return None
    recs.sort(key=lambda r: r[0])
    # state intervals: between two records the ribbon is in the oldest pending tool call's category, else the model
    # is writing, else (after end_turn, or a silent gap over IDLE_GAP) it is idle
    iv, pending, ended = [], [], False
    for (t0, k, ids, end), (t1, *_) in zip(recs, recs[1:]):
        if k == "a":
            pending += ids
            ended = end and not ids
        else:
            pending = [i for i in pending if i not in ids]
            ended = False
        if t1 <= t0:
            continue
        if pending:
            state = by_id[pending[0]]["cat"]
        elif ended or t1 - t0 > IDLE_GAP:
            state = "idle"
        else:
            state = "model"
        if iv and iv[-1][2] == CI[state]:
            iv[-1][1] = t1
        else:
            iv.append([t0, t1, CI[state]])
    last = recs[-1]
    finished = last[1] == "a" and last[3]
    return {"t0": recs[0][0], "t1": recs[-1][0], "calls": calls, "iv": iv, "title": KEYS.sub("", title)[:60],
            "tokens": tokens, "finished": finished}


def main():
    ribbons, owner = [], {}  # owner: tool_use id -> (ribbon index, start time)
    files = sorted(p for r in ROOTS for p in glob.glob(r + "/**/*.jsonl", recursive=True))
    for path in files:
        r = parse(path)
        if not r:
            continue
        rel = Path(path)
        is_main = rel.parent.name.startswith("-home-")
        r["main"] = is_main
        r["sid"] = rel.stem if is_main else next(p.name for p in rel.parents if re.fullmatch(r"[0-9a-f-]{36}", p.name))
        meta = Path(path[:-6] + ".meta.json")
        m = json.load(open(meta)) if meta.exists() else {}
        r["spawn_id"] = m.get("toolUseId")
        if not is_main:
            r["title"] = KEYS.sub("", m.get("description") or m.get("agentType") or "subagent")[:60]
        ribbons.append(r)
    # a resumed or forked session repeats the records of its predecessor: drop a main session whose calls all recur
    ids = [set(c["id"] for c in r["calls"]) for r in ribbons]
    keep = []
    for i, r in enumerate(ribbons):
        dup = r["main"] and ids[i] and any(j != i and ribbons[j]["main"] and ids[i] < ids[j] for j in range(len(ribbons)))
        if dup:
            print("dropped (records repeated in a later session):", r["sid"][:8], file=sys.stderr)
        else:
            keep.append(r)
    dropped = {r["sid"] for r in ribbons} - {r["sid"] for r in keep if r["main"]}
    ribbons = [r for r in keep if r["sid"] not in dropped]
    ribbons.sort(key=lambda r: (not r["main"], r["t0"]))
    for i, r in enumerate(ribbons):
        for c in r["calls"]:
            owner.setdefault(c["id"], (i, c["t"]))
    main_of = {r["sid"]: i for i, r in enumerate(ribbons) if r["main"]}
    T0 = min(r["t0"] for r in ribbons)
    labels, tools, out = {}, {}, []

    def idx(table, s):
        return table.setdefault(s, len(table))

    for i, r in enumerate(ribbons):
        parent, spawn = -1, None
        if not r["main"]:
            if r["spawn_id"] in owner and owner[r["spawn_id"]][0] != i:
                parent, spawn = owner[r["spawn_id"]]
            else:  # a workflow's agent has no spawning tool call on record: it hangs off its session at its first record
                parent, spawn = main_of[r["sid"]], r["t0"]
        out.append({
            "sid": r["sid"], "main": int(r["main"]), "title": r["title"], "parent": parent,
            "spawn": None if spawn is None else round(min(spawn, r["t0"]) - T0, 1),
            "t0": round(r["t0"] - T0, 1), "t1": round(r["t1"] - T0, 1), "finished": int(r["finished"]), "tokens": r["tokens"],
            # call: [start s, duration s (-1: no result on record), category, tool, label, output characters]
            "calls": [[round(c["t"] - T0, 1), -1 if c["d"] is None else round(c["d"], 1), CI[c["cat"]],
                       idx(tools, c["tool"]), idx(labels, c["label"]), c["out"]] for c in r["calls"]],
            "iv": [[round(a - T0, 1), round(b - T0, 1), s] for a, b, s in r["iv"]],
        })
    # an idle stretch during which a subagent of this ribbon is alive is "sub": waiting for a subagent
    for i, r in enumerate(out):
        kids = sorted((k["spawn"], k["t1"]) for k in out if k["parent"] == i)
        if not kids:
            continue
        iv = []
        for a, b, s in r["iv"]:
            if s != CI["idle"]:
                iv.append([a, b, s])
                continue
            cuts = sorted({a, b} | {x for k in kids for x in k if a < x < b})
            for x, y in zip(cuts, cuts[1:]):
                s2 = CI["sub"] if any(k0 <= x and y <= k1 for k0, k1 in kids) else CI["idle"]
                if iv and iv[-1][2] == s2 and iv[-1][1] == x:
                    iv[-1][1] = y
                else:
                    iv.append([x, y, s2])
        r["iv"] = iv
    data = {"t0_unix": T0, "built_unix": max(r["t1"] for r in ribbons), "cats": CATS, "tools": list(tools), "labels": list(labels),
            "idle_gap_s": IDLE_GAP, "ribbons": out}
    (HERE / "data.json").write_text(json.dumps(data, separators=(",", ":")))
    n = sum(len(r["calls"]) for r in out)
    print(f"{len(out)} ribbons ({sum(r['main'] for r in out)} sessions), {n} tool calls, {os.path.getsize(HERE / 'data.json') // 1000} kB")


main()
