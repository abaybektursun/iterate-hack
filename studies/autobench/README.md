# autobench: our research harness against Karpathy's autoresearch

Compares two ways of running research agents on one task: Karpathy's autoresearch loop and this repository's
harness, on Karpathy's task (best `val_bpb` of a GPT trained for 5 minutes on one H100), at an equal number of
GPU experiments, scored on a shard no experiment has read.

**State: built, nothing has run on a GPU. No numbers yet.** The plan, the leak controls and the cost estimate
(about 40 USD of Modal for 40 experiments per arm) are in `specs/SPEC1.md`.

| Path | What it is |
|---|---|
| `specs/SPEC1.md` | Question, hypothesis, arms, measures, leaks L1 to L9 with their controls, procedure, cost and time, open feasibility points. |
| `data/karpathy-228791f/` | github.com/karpathy/autoresearch at commit 228791f (MIT, per its README): `prepare.py`, `train.py`, `program.md`, `README.md`, `pyproject.toml`, `.gitignore`, and `SHA256SUMS`. Frozen. |
| `lib/launch.py` | Runs one `train.py` in the GPU container with the pinned `prepare.py`: refuses the val split outside the evaluation, records the score, scores the holdout when it is mounted. |
| `lib/test_launch.py` | 6 checks that the launcher fails on inputs that should make it fail. `python3 studies/autobench/lib/test_launch.py`, on the laptop. |
| `jobs/modal_app.py` | The Modal app `autobench`: `submit` (budget, ledger, storage), `train_job` (H100, no network, read-only data, one container per experiment, killed at 600 s), `score_final` with the holdout, data preparation. |
| `jobs/run_exp.py` | The client: `submit` for the agents; `prep`, `init`, `ledger`, `holdout`, `final` for the operator. |
| `analysis/audit.py` | Flags lines of a `train.py` that touch the val split, the evaluation, the time budget, files or the network more than the pinned file does. |
| `analysis/readout.py` | Ledger to `results/karpathy-task/<arm>-<nn>/metrics.json` and `run.json`, and the comparison. |
| `arms/baseline/setup.py` | Makes the baseline's folder outside this repository; the 4 changes to `program.md`. |
| `arms/ours/TASK.md` | The task statement for the agents of our harness. |

## Run

```
modal deploy studies/autobench/jobs/modal_app.py
uv run studies/autobench/jobs/run_exp.py prep
uv run studies/autobench/jobs/run_exp.py init calib 3
uv run studies/autobench/jobs/run_exp.py submit calib studies/autobench/data/karpathy-228791f/train.py > run.log 2>&1   # 3 times
uv run studies/autobench/jobs/run_exp.py init baseline 40
uv run studies/autobench/jobs/run_exp.py init ours 40
```

Baseline arm: `python3 studies/autobench/arms/baseline/setup.py ~/autobench-baseline`, then in that folder a
headless Claude Code with Karpathy's prompt and one added sentence, because nobody is there to confirm the setup:
"Hi have a look at program.md and let's kick off a new experiment! let's do the setup first. The setup is confirmed
in advance, the run tag is nov15: go straight into the experiment loop."

Arm `ours`: 4 Claude Code sessions, each in its own worktree of this repository, started with "Read
studies/autobench/arms/ours/TASK.md and work on it."

After both arms end:

```
uv run studies/autobench/jobs/run_exp.py holdout
uv run studies/autobench/jobs/run_exp.py final pinned studies/autobench/data/karpathy-228791f/train.py
uv run studies/autobench/jobs/run_exp.py final baseline <its best valid train.py>
uv run studies/autobench/jobs/run_exp.py final ours <its best valid train.py>
uv run studies/autobench/analysis/readout.py 01 calib baseline ours
```

Every experiment's `train.py`, log and record are in the Modal Volume `autobench-runs` of the person who ran it
(`<arm>/<nnn>/`, finals in `final/`); `modal volume get autobench-runs <arm> runs/` copies them. They are not
committed. The data is in the Volume `autobench-data`, the holdout shard in `autobench-holdout`.

## Numbers

None yet.
