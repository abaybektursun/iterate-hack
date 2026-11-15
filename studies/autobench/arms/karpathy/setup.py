"""Make the working folder of the Karpathy arm, as a fresh git repository outside this repository, so the agent in
it sees no board, no hook, no CLAUDE.md, no team memory and none of the swarm's results.

    python3 studies/autobench/arms/karpathy/setup.py <new folder outside the repository>

The folder holds program.md, README.md and solve.py of this directory, a read-only copy of lib/harness.py, and
the client (jobs/exp.py, with run.sh). Nothing in it names this repository or its path.
Then start the agent there (README.md of the study, "Run").
"""
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent.parent
REPO = STUDY.parent.parent
FILES = {"program.md": HERE / "program.md", "README.md": HERE / "README.md", "solve.py": HERE / "solve.py",
         "harness.py": STUDY / "lib" / "harness.py", "exp.py": STUDY / "jobs" / "exp.py"}


def main():
    target = Path(sys.argv[1]).resolve()
    if REPO in target.parents or target == REPO or "iterate-hack" in str(target):
        sys.exit(f"{target} is inside the repository or names it: the Karpathy arm must not see it")
    target.mkdir(parents=True)   # fails when the folder exists
    for name, source in FILES.items():
        shutil.copy(source, target / name)
    (target / "run.sh").write_text("#!/bin/sh\nexec uv run -q exp.py submit karpathy solve.py\n")
    (target / "run.sh").chmod(0o755)
    (target / ".gitignore").write_text("results.tsv\nrun.log\nlast_run.jsonl\n.pending_call\n__pycache__/\n")
    git = ["git", "-C", str(target)]
    subprocess.run([*git, "init", "-q", "-b", "master"], check=True)
    subprocess.run([*git, "add", ".gitignore", "run.sh", *FILES], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "autoresearch on a math benchmark: start"], check=True)
    print(target)


if __name__ == "__main__":
    main()
