# autobench: Karpathy's autoresearch loop on our MATH-500 task

Runs Karpathy's autoresearch method (one agent, one editable file, a fixed time budget, keep or discard) on this
repository's task, the base Olmo model on MATH-500 with no training, and compares what it reaches in 40
experiments with the swarm's record. Problems, prompt, model revisions, engine and grader are the rlneurons
study's, imported, not copied.

**State: built, nothing has run on a GPU. No numbers yet.** Plan, leak controls and cost (about 34 USD, about
8.5 h) are in `specs/SPEC2.md`.

| Path | What it is |
|---|---|
| `specs/SPEC2.md` | Question, inputs shared with the swarm, hypothesis, measures, leaks L1 to L7 with their controls, procedure, cost and time, open points. |
| `data/dev100-v1.json` | The 100 MATH-500 indices every experiment is scored on, with the rule that drew them. Frozen. |
| `data/karpathy-228791f/` | `program.md` and `README.md` of github.com/karpathy/autoresearch at commit 228791f (MIT, per its README), the source of `arms/karpathy/program.md`. Frozen. |
| `lib/harness.py` | The fixed harness in the GPU container: loads the model as `run_cell.py` does, gives `solve.py` the object `h`, ends generation at the time budget. Holds no answers. |
| `lib/test_harness.py` | Checks of the harness with a stand-in engine: `python3 studies/autobench/lib/test_harness.py`, on the laptop. |
| `lib/grade.py` | The sets `dev100`, `math400`, `hard328` (from `run_cell.problems`) and grading with `rln4_lib.grade_v3`. CPU side only. |
| `jobs/modal_app.py` | The Modal app `autobench`: `submit` (budget, ledger, grading, storage), `solve_job` (H100, no network, read-only weights, one container per experiment), `score_final`. |
| `jobs/exp.py` | The client: `submit` for the agent; `init`, `ledger`, `final` for the operator. |
| `arms/karpathy/` | The agent's files: `program.md`, `README.md`, the starting `solve.py` (plain prompt, T 0.6 / top-p 0.95), and `setup.py`, which makes its folder outside this repository. |
| `arms/swarm/solve_cue.py` | The swarm's cue configuration (T 1.0 / top-p 1.0) as a `solve.py`, for the pipeline check and the finals. |
| `analysis/audit.py` | Flags lines of a `solve.py` that touch the harness internals, the clock, files or single problems. |
| `analysis/readout.py` | Ledger to `results/math500-loop/<arm>-<nn>/metrics.json` and `run.json`, and the readout. |

## Run

```
modal deploy studies/autobench/jobs/modal_app.py
uv run studies/autobench/jobs/exp.py init check 1
uv run studies/autobench/jobs/exp.py submit check studies/autobench/arms/swarm/solve_cue.py     # pipeline check, about 0.60 USD
uv run studies/autobench/jobs/exp.py init karpathy 40
python3 studies/autobench/arms/karpathy/setup.py ~/autoresearch-math
```

Then, in that folder, a headless Claude Code with Karpathy's prompt and one added sentence, because nobody is
there to confirm the setup: "Hi have a look at program.md and let's kick off a new experiment! let's do the setup
first. The setup is confirmed in advance, the run tag is nov15: go straight into the experiment loop."

After `BUDGET EXHAUSTED` (`<best>` is the arm's best `solve.py`, from `modal volume get autobench-runs karpathy/<nnn>/solve.py`):

```
python3 studies/autobench/analysis/audit.py <best>
uv run studies/autobench/jobs/exp.py final karpathy math400 <best>
uv run studies/autobench/jobs/exp.py final karpathy hard328 <best>
uv run studies/autobench/jobs/exp.py final swarm-cue math400 studies/autobench/arms/swarm/solve_cue.py
uv run studies/autobench/jobs/exp.py final swarm-cue hard328 studies/autobench/arms/swarm/solve_cue.py
uv run studies/autobench/analysis/readout.py 01 karpathy karpathy swarm-cue
```

Every experiment's `solve.py`, log, returned texts and grades are in the Modal Volume `autobench-runs` of the
person who ran it (`<arm>/<nnn>/`, finals in `final/`). They are not committed.

## Numbers

None yet.
