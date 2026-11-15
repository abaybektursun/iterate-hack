# SPEC1: our harness against Karpathy's autoresearch, on his task

Written 2026-11-15 UTC, before any GPU run. Board: work-49fdd2.

## Question

At an equal number of GPU experiments and with the same agent model, does our harness (AGENTS.md: several
agents, board, messages, team memory, literature search, meta review) find a better 5-minute training script than
Karpathy's autoresearch loop (one agent, `program.md`, keep or discard)?

The task is Karpathy's own, unchanged, because it is the baseline's home ground: `train.py` of
github.com/karpathy/autoresearch at commit 228791f, a GPT trained for 5 minutes of wall clock on one H100, scored
by `val_bpb` (bits per byte on a pinned validation shard, lower is better).

## Hypothesis and what refutes it

H: the best valid `train.py` of the arm `ours` scores lower than the baseline arm's on the holdout shard, by more
than 2 standard deviations of the run-to-run noise of the unchanged `train.py`.
Refuted when the difference is within 2 sd, or the baseline is lower. Either outcome is posted as the result.

## Arms

| Arm | What runs | Where |
|---|---|---|
| `calib` | the unchanged `train.py`, 3 times | operator |
| `baseline` | one Claude Code agent, Karpathy's `program.md` and prompt, changed in 4 places for the remote GPU (`arms/baseline/setup.py` lists them) | a fresh git repository outside this one |
| `ours` | 4 Claude Code agents under AGENTS.md, with `arms/ours/TASK.md` in place of `DIRECTION.md` | worktrees of this repository |

Same for both: the agent model and its effort setting (written into each arm's `run.json` before the start), the
budget of N experiments counted by the runner (a crash counts), the runner (`jobs/modal_app.py`), the rules of
`program.md` (only `train.py` changes, no new packages, 5 minutes), web access allowed.

Not equal, and reported instead: wall-clock time (the baseline is serial by design, ours runs 4 at once) and agent
tokens (read from the Claude Code transcripts of each arm).

## Measures

1. Primary: `test_bpb` of each arm's best valid `train.py`, retrained once by the operator, minus the `test_bpb`
   of the unchanged `train.py` in the same scoring batch.
2. The curve: best valid `val_bpb` after each experiment, both arms on one axis of experiment count.
3. Experiments, wall-clock hours and agent tokens until each arm first passes the other's final `val_bpb`.
4. Crashed and invalid experiments per arm.

An arm's best valid `train.py` is taken from the runner's ledger (lowest recorded `val_bpb` among valid
experiments), not from what an agent names.

## Leaks and their controls

| | Leak | Control | Checked by |
|---|---|---|---|
| L1 | Selection on val: N keep-or-discard decisions fit the validation shard | Final score on holdout shard 6541. It is in a separate Volume, mounted only by `train_job_holdout`, and downloaded only after both arms end | `lib/test_launch.py`: the holdout score reaches the record, never the log |
| L2 | Score tampering: a changed `prepare.py`, or a printed `val_bpb` that was not computed | The launcher imports the pinned `prepare.py` (sha256 checked) before `train.py`; only `train.py` is sent; the score of record is the return value of the pinned `evaluate_bpb` | `lib/test_launch.py`: fake printed score, own `prepare.py`, wrong sha256 |
| L3 | Training on val or on outside data or weights | `make_dataloader` refuses the val split outside `evaluate_bpb`; no network in the GPU container, Hugging Face offline; `analysis/audit.py` on every kept `train.py`; the operator reads the full diff of both finals | `lib/test_launch.py`; audit run on a planted `"val"` loader: flagged |
| L4 | More training than 5 minutes: a changed loop, or evaluation calls during training | The process is killed at 600 s (Karpathy's rule). An experiment is valid only when its wall time is at most the median of `calib` plus 60 s. The record counts every `evaluate_bpb` call | ledger columns `wall_seconds`, `n_evals` |
| L5 | State carried between experiments (a saved checkpoint resumed in the next run) | Each experiment gets a new container (`single_use_containers`), the data Volume is read-only, nothing else is mounted | first GPU run: write to the Volume must fail |
| L6 | One arm reads the other's experiments | The baseline folder is outside the repository (no board, hooks, memory). The GPU container cannot reach Modal (`restrict_modal_access`) and mounts no results. `TASK.md` forbids `ledger baseline`; both arms' transcripts are searched for the other arm's name and paths | transcript search, in the result |
| L7 | Published solutions to this exact task (forks and write-ups of autoresearch runs) | Web access is equal in both arms and not blocked. Every URL either arm fetched is listed from the transcripts; fetched autoresearch results are reported next to the score. The model's own memory of them is equal by construction | transcript search, in the result |
| L8 | The operator tunes our arm after seeing the baseline | `TASK.md`, `program.md` changes, N and the model are fixed by the commit that precedes the first arm experiment; both arms start in the same hour | `run.json` commit |
| L9 | Hardware differs between arms | One Modal function for both (H100, 8 CPU, 32 GB). GPU name and CPU count are recorded per experiment | ledger columns `gpu`, `cpus` |

Limit of these controls: `train.py` runs in the launcher's process and the agents hold the operator's Modal
credentials. L2 to L4 and L6 are therefore evidence of tampering, not a sandbox. A deliberate bypass shows in the
diff, the audit, the ledger or the transcripts.

## Procedure

1. Deploy, `prep`, then one run of the unchanged `train.py` under arm `calib` (budget 3). Check: `val_bpb` near
   0.998 (the example in `program.md`), wall time near 330 s, the record has one eval.
2. The other two `calib` runs. They give the noise sd and the wall limit.
3. Commit N, the model and the wall limit. `init baseline N`, `init ours N`. Start both arms.
4. After both say `BUDGET EXHAUSTED`: `holdout`, then `final` for the unchanged `train.py` and each arm's best
   valid `train.py`. Audit and read both diffs.
5. `analysis/readout.py`, the transcript searches, the result on the board, this README.

## Cost and time (estimate, nothing has run)

Per experiment: about 360 s billed (container start, about 330 s of script, of which 300 s is training) at
0.001097 USD/s for the H100 (modal.com/pricing) plus about 16 % for 8 CPUs and 32 GB: about 0.46 USD. A crash
costs a few cents; a run killed at 600 s costs 0.76 USD.

| N per arm | GPU runs (2 arms + 3 calib + 3 finals) | GPU cost | Baseline wall clock (serial, 8 min per cycle) | Ours (4 at once) |
|---|---|---|---|---|
| 20 | 46 | about 21 USD | 2.7 h | about 1 h |
| 40 | 86 | about 40 USD | 5.3 h | about 2 h |
| 100 (Karpathy's "overnight") | 206 | about 95 USD | 13 h | about 4.5 h |

The two arms run at the same time, so the pair takes the baseline's wall clock. Step 1 alone costs about 0.50 USD
and settles the open feasibility points below. Agent tokens are not estimated in USD here: they depend on the
plan the agents run under, and step 5 reports them per arm.

## Open feasibility points

1. The image (torch 2.9.1+cu128, the flash-attention kernel loaded offline from a read-only Volume) has not run.
   Step 1 tests it. If the kernel cannot load offline, it moves into the image.
2. The baseline needs a headless Claude Code (`claude -p`); the `claude` command is not installed on this laptop.
3. One pair of runs is one sample of each harness. Agent runs vary; a second pair costs the same again.
4. The team AWS key (board, messages) ends Sunday 2026-11-15 23:59 PST, which bounds the arm `ours`.

## Threats that remain

- Our arm has 4 agents and the baseline 1, so agent tokens differ. The comparison is at equal GPU experiments;
  the token ratio is reported.
- The 5-minute budget makes the score depend on the host CPU (tokenization in the loader). L9 records it.
- `val_bpb` on Modal will differ from Karpathy's 0.9979; only differences inside this study are compared.

## Closest published work (search results only, not read in full, no claim taken from them)

- novix-science/autoresearch: an 8-agent swarm on 8 H100s on this task.
- joinplank.com, "A multi-agent loop for Karpathy's autoresearch": reports 0.98 val_bpb in 12 runs against about 40.
- FutureSpeakAI/asimovs-mind-research: ungoverned, governed single and governed swarm arms on a 5-minute GPT task.

None reports a holdout shard or an equal-experiment budget enforced by the runner; read them in full before the
result is written.
