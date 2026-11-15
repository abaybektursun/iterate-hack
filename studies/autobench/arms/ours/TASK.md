# Task for the agents of the arm `ours`

For this run, this file replaces `DIRECTION.md`. Everything else in `AGENTS.md` applies as written: the board,
the messages, team memory, Exa, papers, the meta review. Work the way the harness prescribes.

## Goal

Get the lowest `val_bpb` of a GPT trained for 5 minutes on one H100. The starting point is
`studies/autobench/data/karpathy-228791f/train.py` (Karpathy's autoresearch, commit 228791f); `prepare.py` in the
same folder is the fixed data loading and evaluation. Read both, and that folder's `README.md`.

## Rules (the same as the other arm's)

- You change `train.py` only. Everything in it is open: architecture, optimizer, hyperparameters, training loop,
  batch size, model size.
- `prepare.py` is fixed. The runner always uses the pinned copy.
- No new packages: only what `pyproject.toml` in that folder lists.
- Training runs for the fixed 5 minutes of `TIME_BUDGET` (wall clock, startup and compilation excluded). A run
  longer than 10 minutes in total is killed.
- VRAM is a soft limit. All else equal, simpler code is better.
- The first experiment is the unchanged `train.py`.

## How to run an experiment

Keep your copy of `train.py` in your own worktree, in `studies/autobench/arms/ours/work/<your agent name>/train.py`,
and commit each version before you run it. Then:

    uv run studies/autobench/jobs/run_exp.py submit ours <path to train.py> > run.log 2>&1
    grep "^val_bpb:\|^peak_vram_mb:" run.log

Do not let the log into your context: it has one line per training step. An empty grep means a crash; read
`tail -n 50 run.log`.

## Budget

The arm has a fixed number of experiments, shared by all its agents and counted by the runner; a crash counts.
`uv run studies/autobench/jobs/run_exp.py ledger ours` shows what is used. When `run.log` says `BUDGET EXHAUSTED`,
the run is over: post your result and stop. Up to 4 experiments run at once.

## Not allowed

- Reading anything of the other arm: its ledger (`ledger baseline`), its folder, its transcripts.
- The commands `holdout` and `final` of `run_exp.py`, and the Volume `autobench-holdout`.
- Posting `score:` lines to the board: this run is not on the hill-climbing chart. Start every board item of this
  run with `autobench:`.

The score that counts is not the `val_bpb` you see. After both arms end, the operator retrains the arm's best
valid `train.py` once and scores it on a shard that no experiment has read.
