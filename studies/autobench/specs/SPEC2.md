# SPEC2: Karpathy's autoresearch loop on our task, against the swarm's record

Written 2026-11-15 UTC, before any GPU run. Board: work-947254. It replaces SPEC1 (both methods on Karpathy's GPT
training task, commit caab264), which was not what was asked and never ran.

## Question

On our task, using the base model `allenai/Olmo-3-1025-7B` better on MATH-500 with no training and no reward, how
far does Karpathy's autoresearch method get in 40 experiments, and how does that compare with what the swarm found?

Karpathy's method is kept as it is: one agent, one file it may edit, one fixed metric, a fixed time budget per
experiment, keep the commit when the metric improves and reset when it does not. `arms/karpathy/program.md` is his
`program.md` (`data/karpathy-228791f/`) with the task-specific parts rewritten: `train.py` becomes `solve.py`,
`val_bpb` becomes `right`, 5 minutes of training become 6 minutes of generation, and a noise note and the rule
against problem-specific content are added.

## Same inputs as the swarm

Nothing is copied or redefined; `lib/harness.py` and `lib/grade.py` import the rlneurons study's code and data.

| | Source |
|---|---|
| Problems | `studies/rlneurons/data/rln4/math500.json` (sha256 checked by `run_cell.problems`), the 328 harder problems of `data/rln3/hard.json` |
| Prompt | the tokenizer's chat template, pair1 (`n13_score.render_ids`), as `run_cell.py` |
| Model, tokenizer | the revisions of `data/rln4/frozen4.json`, from the Volume `iterate-hf-cache` |
| Engine | `rln4_gen.VllmEngine`, vLLM 0.32.0 installed by `jobs/setup_vllm.sh`, cap 16,384, max length 2,048 + 16,384 |
| Grader | `rln4_lib.grade_v3` |

## The experiment

`solve.py` defines `solve(problems, h)`. It gets the 100 dev problems (`data/dev100-v1.json`: 100 of the 500,
drawn once with a fixed seed) and generates only through `h.generate`, which stops at 360 s of wall clock
(model loading excluded). The start is the plain prompt at T 0.6 / top-p 0.95, one sample, where the swarm
started. Budget: 40 experiments, counted by the runner, crashes included.

## Hypothesis and what refutes it

H: at the tokens per problem that the Karpathy arm's best `solve.py` uses, it scores lower on the 328 harder
problems than the swarm's best base configuration at the same or fewer tokens, by more than the 95 % interval of
the difference. Refuted when it is equal within the interval, or higher. Either outcome is the result.

## Measures

1. Finals, each run once through this runner: the Karpathy arm's best `solve.py` (highest `right` in the ledger;
   ties: the earlier experiment) and the swarm's cue configuration (`arms/swarm/solve_cue.py`), on `math400` (the
   400 MATH-500 problems that no experiment used, 1,440 s) and on `hard328` (2,362 s: twice the seconds per
   problem, because answers there are twice as long).
2. The swarm's record: its best base score at equal or fewer tokens per problem, from the board (result-40ed3b
   and the hill-climbing chart), stated with its own conditions (no time limit).
3. The curve: best `right` of 100 after each experiment; GPU hours; agent tokens from the transcript.

## Leaks and their controls

| | Leak | Control | Checked by |
|---|---|---|---|
| L1 | Selection on the 100 dev problems over 40 keep-or-discard decisions; 100 problems have a standard error of about 4 to 5 points | Finals on `math400` and `hard328`, which no experiment reads | sets built in `lib/grade.py` |
| L2 | Answers reach `solve.py` | The GPU container gets problem texts only: its image has no data file and `solve_job` receives no answer. Grading runs on the CPU side. `last_run.jsonl` has no reference answer | first GPU run: `find / -name math500.json` in the container finds nothing |
| L3 | Answers or worked dev problems written into `solve.py` by the agent (the problems are public) | Forbidden in `program.md`; it cannot help on the finals; `analysis/audit.py` flags per-problem code and long literals; the operator reads the final diff | audit run on a planted file: flagged |
| L4 | More generation than the budget, or another model or outside text | `h.generate` is the only path to the engine and owns the clock; no network, Hugging Face offline, read-only weights, Modal not reachable; a new container per experiment | `lib/test_harness.py`; audit flags `h._`, the clock, files and processes |
| L5 | The Karpathy agent learns the swarm's findings (the cue, T 1.0, the vote) | Its folder is outside the repository and names no path of it (`arms/karpathy/setup.py` refuses otherwise); no board, hooks, memory. Its transcript is searched for `iterate-hack`, `invariant.team` and the team's GitHub repository | transcript search, in the result |
| L6 | Published work on this exact model and benchmark (Wang et al. 2610.06851 report the cue) | Not blocked: the swarm also found the cue in the literature. Every URL the agent fetched is listed in the result | transcript search |
| L7 | The operator changes the arm after seeing results | `program.md`, `solve.py`, the budget and the model are fixed by the commit before experiment 1 | `run.json` commit |

Limit: `solve.py` runs in the harness's process and the agent holds the operator's Modal credentials, so L3 and
L4 are evidence of tampering, not a sandbox.

## What this comparison is and is not

The swarm's record was not made under a 6-minute budget, an experiment budget or isolation, and it used many
agents over two days. So measure 1 is the controlled part (two `solve.py` files, one runner, unseen problems) and
measure 2 is context. A controlled pair would need the swarm rerun from the plain prompt without its memory.

## Procedure

1. Deploy. `init check 1`, then `submit check arms/swarm/solve_cue.py`: the pipeline check. Expected: the first run
   loads the model offline, about 80 of 100 right less what the 360 s cut (the swarm's row is 410 of 500 with no
   time limit), total near 9 minutes. Read `last_run.jsonl`.
2. `init karpathy 40`, `arms/karpathy/setup.py <folder>`, start the agent.
3. After `BUDGET EXHAUSTED`: audit and read the best `solve.py`, run the four finals, `analysis/readout.py`, the
   transcript searches, the result on the board, the README.

## Cost and time (estimate, nothing has run)

One experiment: about 2.5 min of container start and model loading (not measured in this app), 6 min of generation,
under 1 min of grading: about 9 min of H100 at 3.95 USD/h, about 0.60 USD.

| Step | GPU runs | Cost | Wall clock |
|---|---|---|---|
| Pipeline check | 1 | about 0.60 USD | 10 min |
| Karpathy arm, 40 experiments | 40 | about 24 USD | about 7.3 h (9.5 min per run plus about 1.5 min of agent work) |
| Finals: 2 files on `math400` (27 min each) and `hard328` (42 min each) | 4 | about 9 USD | 45 min, run at the same time |
| Total | 45 | about 34 USD | about 8.5 h |

The arm can be stopped at any experiment; the curve and the finals stay valid for the experiments done.

## Open points

1. The engine has not started in this app: offline loading from the read-only Volume and the load time are checked
   by step 1.
2. The agent needs a headless Claude Code (`claude -p`) started in the folder; the `claude` command is not on this
   laptop's PATH.
3. One run of one agent is one sample of the method.
4. Requests cut by the time budget return no text, and their tokens are not counted in `generated_tokens`.
