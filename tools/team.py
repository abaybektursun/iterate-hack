"""The team store: one private GitHub repository, abaybektursun/iterate-hack-team, that holds everything the team
shares: the board, the events, the traces and the shared credentials. Modal is not used for it, because each
person has their own Modal workspace.

It is cloned to ~/.iterate-hack-team on first use (needs `gh auth login` and access to the repository). A Store
is a folder of JSON files, one file per key, so two writers never touch the same file. Every write is a commit
that is pushed at once; if someone else pushed first, it pulls with rebase and pushes again.
"""
import contextlib
import fcntl
import json
import subprocess
from pathlib import Path

REPO = "abaybektursun/iterate-hack-team"
DIR = Path.home() / ".iterate-hack-team"


def git(*args, check=True):
    return subprocess.run(["git", "-C", str(DIR), *args], capture_output=True, text=True, check=check)


@contextlib.contextmanager
def locked():
    """One git command sequence at a time on this machine: several agents of one person share the clone."""
    with open(str(DIR) + ".lock", "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        yield


def sync():
    with locked():
        if DIR.exists():
            git("pull", "-q", "--rebase", "--autostash")
        else:
            subprocess.run(["gh", "repo", "clone", REPO, str(DIR), "--", "-q"], check=True)


def push(message):
    with locked():
        git("add", "--all")  # this clone holds only store files
        if git("diff", "--cached", "--quiet", check=False).returncode == 0:
            return
        git("commit", "-qm", message)
        for _ in range(5):
            if git("push", "-q", check=False).returncode == 0:
                return
            git("pull", "-q", "--rebase")
        raise RuntimeError(f"could not push to {REPO} after 5 attempts")


class Store:
    def __init__(self, name):
        sync()
        self.name = name
        self.dir = DIR / name
        self.dir.mkdir(exist_ok=True)

    def path(self, key):
        return self.dir / (key.replace(":", "__") + ".json")

    def __getitem__(self, key):
        if not self.path(key).exists():
            raise KeyError(key)
        return json.loads(self.path(key).read_text())

    def put(self, key, value, publish=True):
        self.path(key).write_text(json.dumps(value, indent=1, sort_keys=True))
        if publish:
            push(f"{self.name}: {key}")

    def __setitem__(self, key, value):
        self.put(key, value)

    def items(self):
        return [(p.stem.replace("__", ":"), json.loads(p.read_text())) for p in sorted(self.dir.glob("*.json"))]
