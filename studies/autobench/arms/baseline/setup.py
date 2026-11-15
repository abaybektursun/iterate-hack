"""Make the working folder of the baseline arm: Karpathy's autoresearch at commit 228791f, as a fresh git
repository outside this repository, so the agent in it sees no board, no hook, no CLAUDE.md and no team memory.

    python3 studies/autobench/arms/baseline/setup.py <new folder outside the repository>

program.md is changed in four places and nowhere else, because the GPU is remote: the data check, the launch
command (twice), and the stop signal. Each replacement must match exactly once, or this script fails.
Then start the agent there with Karpathy's prompt (README.md of this study, "Run").
"""
import shutil
import subprocess
import sys
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent.parent
PIN = STUDY / "data" / "karpathy-228791f"
REPO = STUDY.parent.parent

CHANGES = [
    ("4. **Verify data exists**: Check that `~/.cache/autoresearch/` contains data shards and a tokenizer. If not, "
     "tell the human to run `uv run prepare.py`.",
     "4. **Data**: the data shards and the tokenizer are on the remote GPU machine that `./run.sh` sends `train.py` "
     "to. They are prepared; there is nothing to check on this computer."),
    ("You launch it simply as: `uv run train.py`.",
     "You launch it simply as: `./run.sh` (it sends `train.py` to a remote H100, runs it there and prints its output)."),
    ("4. Run the experiment: `uv run train.py > run.log 2>&1`",
     "4. Run the experiment: `./run.sh > run.log 2>&1`"),
    ("The loop runs until the human interrupts you, period.",
     "The loop runs until the human interrupts you, period. The human's interrupt is this: when `run.log` says "
     "`BUDGET EXHAUSTED`, the run is over and you stop."),
]


def main():
    target = Path(sys.argv[1]).resolve()
    if REPO in target.parents or target == REPO:
        sys.exit(f"{target} is inside the repository: the baseline arm must not see it")
    target.mkdir(parents=True)   # fails when the folder exists
    for name in ("prepare.py", "train.py", "README.md", "pyproject.toml", ".gitignore"):
        shutil.copy(PIN / name, target / name)
    program = (PIN / "program.md").read_text()
    for old, new in CHANGES:
        if program.count(old) != 1:
            sys.exit(f"program.md: expected exactly one match of {old!r}")
        program = program.replace(old, new)
    (target / "program.md").write_text(program)
    run = target / "run.sh"
    run.write_text(f"#!/bin/sh\nexec uv run -q {STUDY / 'jobs' / 'run_exp.py'} submit baseline train.py\n")
    run.chmod(0o755)
    with open(target / ".gitignore", "a") as f:
        f.write("run.log\n")
    git = ["git", "-C", str(target)]
    subprocess.run([*git, "init", "-q", "-b", "master"], check=True)
    subprocess.run([*git, "add", "prepare.py", "train.py", "README.md", "pyproject.toml", ".gitignore", "program.md",
                    "run.sh"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "autoresearch 228791f; program.md and run.sh for a remote GPU"], check=True)
    print(target)


if __name__ == "__main__":
    main()
