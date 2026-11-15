"""Hand side work to Devin (Cognition's terminal agent) so the research keeps moving. Uses your own Devin login.

Usage:
  python3 tools/devin.py ask "<question>"            read-only, in this checkout; waits and prints the answer
  python3 tools/devin.py run <name> "<task>"         a change, in the background: Devin works in its own worktree
                                                     ../iterate-hack-devin-<name> on branch devin/<name>, cut from
                                                     your HEAD (--base <ref> for another start); returns at once
  python3 tools/devin.py ls                          every run: state, minutes, commits on its branch
  python3 tools/devin.py wait <name>                 block until the run ends, then print what show prints
  python3 tools/devin.py show <name>                 Devin's report, then the commits and changed files of its branch
  python3 tools/devin.py rm <name>                   delete the worktree, the branch and the run record; refuses
                                                     while the branch has work you did not merge (--force drops it)

ask and run use swe-2-high, which is fast and free. --strong uses gpt-6-sol-high, paid from your Devin credits:
take it for a change across several files and for a review that must not share Claude's blind spots. --model <id>
picks any other (`devin models`). --file <path> reads the question or task from a file.

Devin's report is a claim. Before merging, read `git diff HEAD...devin/<name>` and run the check yourself.
Each run keeps prompt.md, out.txt and meta.json in ~/.cache/iterate-hack/devin/<name>/.
"""
import argparse
import json
import os
import pathlib
import shlex
import shutil
import subprocess
import time

MODEL = "swe-2-high"
STRONG = "gpt-6-sol-high"  # another model family than Claude and SWE-2: 2 USD per million input tokens, 10 output
RUNS = pathlib.Path.home() / ".cache/iterate-hack/devin"

ASK = """You answer a question for another agent of the iterate-hack research team. This is read-only: change no
file, start no job, post nothing to the board and send no message. The work item on the board belongs to the agent
that asked, so do not claim one. Answer first, in at most 15 lines, and give the file and line behind each claim.

Question:
"""

RUN = """You are a worker for another agent of the iterate-hack research team. That agent owns the work item on
the board and will review and merge what you do, so the coordination flow of AGENTS.md is not yours to run:
- Do not post, comment or close anything on the board (tools/board.py) and send no message (tools/msg.py).
- Do not start or spend anything: no tools/gpu.py submit, no tools/vast.py, no modal, no model on this machine.
- Work only in this directory, a git worktree on branch {branch}. Do not git push. Do not edit AGENTS.md or CLAUDE.md.
- Commit your change on this branch, naming each file (never git add -A or git add .).
- Run the check that shows the change works, and fail loudly: no try/except that hides an error.
- End with a report of at most 10 lines: the files you changed, the check command with its real output, and what
  is left undone. If the task cannot be done as written, change nothing and say why.

Task:
"""


def sh(*command, cwd=None):
    done = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if done.returncode:
        raise SystemExit(f"{' '.join(command)}\n{done.stderr.strip()}")
    return done.stdout.strip()


def devin(prompt_file, model, mode):
    if not shutil.which("devin"):
        raise SystemExit("devin is not installed or not on PATH: see README, Devin.")
    # Your Devin settings plus one key: Devin then reads AGENTS.md and skips what is written for Claude Code (your
    # private ~/.claude/CLAUDE.md, .claude/skills, and the hooks of .claude/settings.json, which would run in Devin).
    user_config = pathlib.Path.home() / ".config/devin/config.json"
    settings = json.loads(user_config.read_text()) if user_config.exists() else {}
    RUNS.mkdir(parents=True, exist_ok=True)
    settings["read_config_from"] = {**settings.get("read_config_from", {}), "claude": False}
    (RUNS / "config.json").write_text(json.dumps(settings))
    return ["devin", "--config", str(RUNS / "config.json"), "-p", "--prompt-file", str(prompt_file), "--model", model,
            "--permission-mode", mode, "--respect-workspace-trust", "false"]


def text_of(args, what):
    text = pathlib.Path(args.file).read_text() if args.file else args.text
    if not text:
        raise SystemExit(f"Give the {what} on the command line or with --file.")
    return text


def run_dir(name):
    folder = RUNS / name
    if not (folder / "meta.json").exists():
        raise SystemExit(f"No run named {name}: python3 tools/devin.py ls")
    return folder, json.loads((folder / "meta.json").read_text())


def state(folder, meta):
    """running, done, failed (Devin exited with an error) or lost (the process is gone and left no exit code)."""
    if (folder / "exit").exists():
        return "done" if (folder / "exit").read_text().strip() == "0" else "failed"
    # The pid alone is not enough: after a restart of the machine another process can hold it.
    command = subprocess.run(["ps", "-o", "command=", "-p", str(meta["pid"])], capture_output=True, text=True).stdout
    return "running" if str(folder) in command else "lost"


def minutes(folder, meta):
    end = (folder / "exit").stat().st_mtime if (folder / "exit").exists() else time.time()
    return (end - meta["started"]) / 60


def commits(meta):
    """The branch's commits since its start, or None when the branch was deleted outside this tool."""
    log = subprocess.run(["git", "log", "--oneline", f"{meta['base']}..{meta['branch']}"], capture_output=True, text=True)
    return None if log.returncode else log.stdout.splitlines()


def show(name):
    folder, meta = run_dir(name)
    print(f"{name}: {state(folder, meta)} after {minutes(folder, meta):.1f} min, {meta['model']}, {meta['worktree']}")
    print((folder / "out.txt").read_text().strip() or "(no output yet)")
    if commits(meta) is None:
        raise SystemExit(f"\nThe branch {meta['branch']} is gone: python3 tools/devin.py rm {name}")
    print(f"\nCommits on {meta['branch']} since {meta['base'][:7]}:")
    print("\n".join(commits(meta)) or "(none)")
    print(sh("git", "diff", "--stat", f"{meta['base']}..{meta['branch']}"))
    left = sh("git", "status", "--short", cwd=meta["worktree"])
    if left:
        print(f"Not committed in the worktree:\n{left}")


parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
commands = parser.add_subparsers(dest="command", required=True)
for command in ("ask", "run"):
    sub = commands.add_parser(command)
    if command == "run":
        sub.add_argument("name", help="short name, letters, digits and dashes: it names the branch and the worktree")
        sub.add_argument("--base", default="HEAD", help="the commit Devin starts from")
    sub.add_argument("text", nargs="?")
    sub.add_argument("--file")
    sub.add_argument("--model", default=MODEL)
    sub.add_argument("--strong", action="store_true", help=f"use {STRONG}")
commands.add_parser("ls")
for command in ("wait", "show", "rm"):
    sub = commands.add_parser(command)
    sub.add_argument("name")
    if command == "rm":
        sub.add_argument("--force", action="store_true", help="also when work on the branch is not merged")
args = parser.parse_args()
if getattr(args, "strong", False):
    args.model = STRONG

if args.command == "ask":
    # "auto" approves only tools that read, so Devin can read files and git history and can change nothing.
    RUNS.mkdir(parents=True, exist_ok=True)
    prompt = RUNS / f"ask-{time.time_ns()}.txt"
    prompt.write_text(ASK + text_of(args, "question"))
    done = subprocess.run(devin(prompt, args.model, "auto"), stderr=subprocess.PIPE, text=True)
    prompt.unlink()
    # In this mode Devin is refused every tool that writes or executes; one warning per refusal is not an error.
    print("".join(line for line in done.stderr.splitlines(True) if "rejected a tool call" not in line), end="")
    raise SystemExit(done.returncode)

if args.command == "run":
    if not args.name.replace("-", "").isalnum():
        raise SystemExit("The name takes letters, digits and dashes only.")
    folder = RUNS / args.name
    if folder.exists():
        raise SystemExit(f"A run named {args.name} exists: show it, or rm it first.")
    task = text_of(args, "task")
    branch = f"devin/{args.name}"
    base = sh("git", "rev-parse", args.base)
    main_checkout = pathlib.Path(sh("git", "rev-parse", "--path-format=absolute", "--git-common-dir")).parent
    worktree = main_checkout.parent / f"iterate-hack-devin-{args.name}"
    sh("git", "worktree", "add", "-b", branch, str(worktree), base)
    # From here a run record exists, so rm can always undo the branch and the worktree.
    folder.mkdir(parents=True)
    meta = {"pid": 0, "started": time.time(), "model": args.model, "branch": branch, "base": base,
            "worktree": str(worktree)}
    (folder / "meta.json").write_text(json.dumps(meta, indent=1))
    (folder / "prompt.md").write_text(RUN.format(branch=branch) + task)
    (folder / "out.txt").write_text("")
    # "smart" lets Devin edit, run checks and commit without a person; a fast model stops what it judges unsafe.
    line = shlex.join(devin(folder / "prompt.md", args.model, "smart"))
    out, code = shlex.quote(str(folder / "out.txt")), shlex.quote(str(folder / "exit"))
    process = subprocess.Popen(f"{line} > {out} 2>&1; echo $? > {code}", shell=True, cwd=worktree,
                               start_new_session=True, stdin=subprocess.DEVNULL)
    (folder / "meta.json").write_text(json.dumps({**meta, "pid": process.pid}, indent=1))
    print(f"{args.name}: started on {branch} in {worktree}\nwhen it ends: python3 tools/devin.py wait {args.name}")

if args.command == "ls":
    for folder in sorted(RUNS.glob("*/meta.json"), key=lambda path: path.stat().st_mtime):
        meta = json.loads(folder.read_text())
        count = "branch gone" if commits(meta) is None else f"{len(commits(meta))} commits"
        print(f"{folder.parent.name:24} {state(folder.parent, meta):8} {minutes(folder.parent, meta):5.1f} min  "
              f"{count}  {meta['branch']}")

if args.command == "wait":
    folder, meta = run_dir(args.name)
    while state(folder, meta) == "running":
        time.sleep(2)
    show(args.name)

if args.command == "show":
    show(args.name)

if args.command == "rm":
    folder, meta = run_dir(args.name)
    if state(folder, meta) == "running":
        os.killpg(meta["pid"], 15)
        while state(folder, meta) == "running":  # let Devin stop before its worktree goes
            time.sleep(0.5)
    there = pathlib.Path(meta["worktree"]).exists()
    left = sh("git", "status", "--short", cwd=meta["worktree"]) if there else ""
    ahead = sh("git", "log", "--oneline", f"HEAD..{meta['branch']}") if commits(meta) is not None else ""
    if (left or ahead) and not args.force:
        raise SystemExit(f"{args.name} has work that is not in your branch:\n{left}\n{ahead}\n"
                         f"git merge {meta['branch']}, or rm --force to drop it.")
    if there:
        sh("git", "worktree", "remove", "--force", meta["worktree"])
    if commits(meta) is not None:
        sh("git", "branch", "-D", meta["branch"])
    shutil.rmtree(folder)
    print(f"{args.name}: removed {meta['branch']} and {meta['worktree']}")
