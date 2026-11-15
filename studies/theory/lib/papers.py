"""Paper-only access to the team's memory and to Exa, for the external stage of a theory round (lib/round.py).

  python3 studies/theory/lib/papers.py recall "<query>"   tools/recall.py, keeping only entries whose every source is a
                                                           paper or web page ([arxiv-...] or [web-...]); board items and
                                                           Claude Code sessions are dropped, since they can hold
                                                           held-out numbers
  python3 studies/theory/lib/papers.py search "<query>"   tools/exa.py search
  python3 studies/theory/lib/papers.py fetch <url>        tools/exa.py fetch
"""
import os
import re
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[3] / "tools"
ENTRY = re.compile(r"^\d{4}-\d{2}-\d{2}  ")  # recall.py starts each entry with its date; continuation lines do not
SOURCE = re.compile(r"\[([^\[\]\s]+):[^\[\]\s]+\]")  # the source ids in an entry's trailing brackets, e.g. [arxiv-2610.37719:7a6b]


def paper_only(text):
    entries = []
    for line in text.splitlines():
        if ENTRY.match(line):
            entries.append([line])
        elif entries and not line.startswith("["):
            entries[-1].append(line)
    kept = [e for e in entries if (s := SOURCE.findall("\n".join(e))) and all(x.startswith(("arxiv-", "web-")) for x in s)]
    return "".join("\n".join(e) + "\n" for e in kept) + f"[{len(kept)} paper entries of {len(entries)}]"


if __name__ == "__main__":
    command, *rest = sys.argv[1:]
    if command == "recall":
        out = subprocess.run([sys.executable, str(TOOLS / "recall.py"), *rest], capture_output=True, text=True, check=True).stdout
        print(paper_only(out))
    elif command in ("search", "fetch"):
        os.execv(sys.executable, [sys.executable, str(TOOLS / "exa.py"), command, *rest])
    else:
        sys.exit(__doc__)
