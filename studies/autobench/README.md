# autobench: Karpathy's autoresearch loop on our MATH-500 task

Runs Karpathy's autoresearch method (one agent, one editable file, a fixed time budget, keep or discard) on this
repository's task, the base Olmo model on MATH-500 with no training, and compares what it reaches in 40
experiments with the swarm's record. Problems, prompt, model revisions, engine and grader are the rlneurons
study's, imported, not copied.

**State: run on 2026-11-15.** On 400 unseen MATH-500 problems the Karpathy arm's method equals the swarm's cue with
one sample (338 of 400 each) at 2.7 times the tokens; on the 328 harder problems it is 6.4 points lower [-10.7, -2.1].
Plan and leak controls are in `specs/SPEC2.md`.

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
| `analysis/paired.py` | Paired difference of two finals on one set with a bootstrap interval, from their per-problem grades. |
| `arms/swarm/solve_vote4.py` | The swarm's vote over 4 samples as a `solve.py`, for the finals. |
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

All with base `allenai/Olmo-3-1025-7B`, grader v3, one H200, 3.6 s of generation per problem (7.2 s on `hard328`).
Run folders: `results/math500-loop/karpathy-01/` (ledger of the 40 experiments and of the finals, `run.json`) and
`results/math500-loop/finals-01/` (per-problem grades of the six finals). Raw answers, logs and every `solve.py`
are in the Modal Volume `autobench-runs` of frustea (`karpathy/<nnn>/`, `final/<set>-<label>-<nnn>/`).

### Finals on problems no experiment used (2026-11-15)

| Configuration | math400: right of 400 | tokens per problem | hard328: right of 328 | tokens per problem |
|---|---|---|---|---|
| Karpathy arm's kept `solve.py` (plain prompt, T 0.6, 12 samples, vote, two passes) | 338 (84.5 %) | 11,254 | 139 (42.4 %) | 20,407 |
| Swarm cue, one sample (`arms/swarm/solve_cue.py`) | 338 (84.5 %) | 4,097 | 160 (48.8 %) | 9,351 |
| Swarm cue, vote over 4 (`arms/swarm/solve_vote4.py`) | 344 (86.0 %) | 6,372 | 161 (49.1 %) | 9,060 |

Paired differences, Karpathy minus swarm, 95 % interval from a paired bootstrap over problems (`analysis/paired.py`):

- math400 against the cue with one sample: 0.0 points [-3.5, +3.5] (25 problems only Karpathy right, 25 only the cue),
  at 2.7 times the tokens.
- math400 against the vote over 4: -1.5 points [-5.2, +2.2].
- hard328 against the cue with one sample: **-6.4 points [-10.7, -2.1]** (16 only Karpathy right, 37 only the cue), at
  2.2 times the tokens. Against the vote over 4: -6.7 [-11.3, -2.1].

The hypothesis of SPEC2 holds: on the 328 harder problems the Karpathy arm's method is below the swarm's
configuration at fewer tokens, outside the interval. On the easier 400 the two are equal and the Karpathy method
costs 2.7 times the tokens.

Read with these:

- The time budget cut the swarm's vote: 872 of 1,600 requests on math400 and 972 of 1,312 on hard328 never ran, so
  on hard328 the vote is close to one sample per problem. Without a time limit the swarm's posted record is 192 of
  328 for the vote over 4 at 36,902 tokens and 161 for one sample (board result-5c961a).
- The Karpathy method caps a sample at 4,096 tokens and always returns an answer (0 of 328 without one; the cue
  leaves 69 of 328 without one). On hard328 3,910 of its samples hit a cap. It was tuned on problems where
  short samples are enough.
- One problem of `hard328-karpathy-000` scored right: index 0, extracted `116`; one scored wrong: index 29,
  extracted `35`.
- `solve_vote4.py` was written after the arm ended and run once.

### The Karpathy arm (40 experiments on the 100 dev problems, 2026-11-15 07:07 to 13:14 UTC)

- Start (plain prompt, T 0.6 / top-p 0.95, one sample): 61 of 100 at 3,289 tokens per problem.
- Experiment 2 (8 samples, majority vote): 81. Best single run: 86 (experiments 11, 17, 18, 26, 27, 36, 39).
- The kept method, 7 runs with different seeds: 83, 86, 86, 84, 83, 86, 80, mean 84.0, at about 10,800 tokens per
  problem. So one run of 100 is good to about 3 problems, and every step after experiment 2 is inside that.
- No crash. 5.33 h of GPU containers. The agent (Claude Code headless, `claude-fable-5-2`) reports 7.91 USD.
- Transcript search (`~/.claude/projects/-Users-ali-autoresearch-math`): no web search, no web fetch, no path
  outside its folder, no mention of this repository or the team site. It did not find the opening cue.
- Audit of the kept `solve.py` (experiment 036): one flag, the word "deadline" in a comment. Read in full: no
  per-problem content, 82 lines.
- What it tried, with its own notes, is in `results/math500-loop/karpathy-01/metrics.json` and on the board as
  idea-6fb0de.

For comparison on the same 100 problems and runner: the swarm's cue with one sample scores 84 at 3,599 tokens per
problem (arm `check`, experiment 002).

### Deviations from SPEC2

- The final file is the agent's kept `solve.py`, not the highest single run in the ledger: that run (experiment 11,
  86) was an A/B file whose score the agent itself read as noise, and it has the same method.
- The vote over 4 was added to the finals, because the cue with one sample uses a third of the tokens.
- Finals ran through `solve_job_final`, which can reach Modal and the network: a result above a few MB is returned
  through blob storage, and the restricted container cannot write there (9 final attempts ended with AuthError 401
  or a name-resolution error and have no score). The 40 experiments ran in the restricted container.
- Experiments 000 and 001 of `check` have no score: 001 was cancelled when its client died with the session; 000
  was cancelled on Modal's side after 349 s for a reason that was not found.
- Cost: 59.92 USD of Modal for the app `autobench` on 2026-11-15 (`modal billing report`), against the 34 USD
  estimated: experiments took 8 minutes each, not 6.5, and the failed finals cost about 12 USD.

### What the comparison does not show

It compares what each side produced under one evaluation, not the two methods at equal resources: the swarm had
several agents and two days, the Karpathy arm one agent, 40 experiments and 6 hours, and one run is one sample of
the method. An equal-agents version is three or four independent Karpathy loops sharing one experiment budget.
