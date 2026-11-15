# Day-1 turnaround analysis, for the optimization round (2026-11-14, 20:10-23:20 UTC)

Sources: the command log (1,232 board.py, gpu.py and paper.py calls, 3 people), the board (32 work items, 25 results,
24 ideas), abaybektursun's 18 Modal job records and logs, 30 local Claude Code transcripts of abaybektursun (10
sessions, 20 subagents), git (116 commits). Three Opus subagents did the reading; the queue waits and stage medians
were checked against `uv run tools/cycle.py --hours 30`. Teammates' transcripts and job records were not in the
store, so their side is known only from the command log and the board.

## Where the time goes

| Measure | Number | Source |
|---|---|---|
| Median work item with GPU jobs | 0 min claim to first job, 46 min in jobs, 2 min to answer | cycle.py |
| One 328-problem cell on one H100 | 51-52 min; generation is 3,043 of 3,090 s (98.5 %) | job e72c log |
| Throughput | about 1,050 tokens/s; KV cache 97-100 % full; 19-26 requests running, about 290 waiting | job e72c log |
| Fixed overhead per job | 1.2-3.5 min (container 8 s, setup 1-34 s, model load 42-158 s) | job logs |
| Queue wait | 8.0, 12.9, 27.3, 28.9, 28.9 min on 5 of 9 late jobs; cause: `max_containers=4` | infra/runner.py:79, job records |
| Tokens spent on answers that hit the 16,384 cap | 41 % (e72c), 35 % (7ba0), 13 % (a32d), 11 % (86ef), 68 % (d4fa, T 0.6) | answers.jsonl |
| Agent wall time, 10 top-level sessions | 596 min: 377 waiting for the person, 114 waiting on background work, 47 model, 40 tools | transcripts |
| Job polling | 318 `gpu.py ls`/`logs` calls, 270 within 2 min of the same agent's previous call | command log |
| `paper.py add` | 9 of 22 calls in one session hit the 120 s Bash timeout; 7 reader subagents spent about 80 of 91 min on adds | transcripts |
| Same cell generated again | 328 base+cue T 1.0 about 5 times | command log, board |
| Tooling share | 13 of 32 work items, 300 of 1,072 agent-minutes, 56 of 116 commits; AGENTS.md changed 17 times | board, git |
| Results | 25 in 3.15 h; 7 are research results (5 from new GPU cells) | board |

## Proposed changes, ranked by minutes saved per experiment

| # | Change | Saves | Effort | Kind |
|---|---|---|---|---|
| 1 | H100 `max_containers` 4 to 8 | the 8-29 min queue (measured) | 5 min | infra; spends credits twice as fast |
| 2 | `run_cell.py --shard k/N` by default, 4 shards | 51 to about 14 min per cell (estimate) | 20 min + merge of rows | infra |
| 3 | List of finished cells in git, keyed by (model, prompt, set, T, top-p, seed, n); run_cell reuses rows | a 51 min cell per avoided repeat (about 4 today) | 30 min | infra |
| 4 | One background `gpu.py wait <ids>` instead of polling | about 300 calls and 4.8M cached tokens in one subagent (measured) | 5 min | workflow |
| 5 | `paper.py add` returns after the POST; many findings per call | about 80 of 91 subagent minutes per survey (measured) | 20 min | infra |
| 6 | Standing permissions: claim the next item after `done`, merge without asking, Day-1 runs under a USD limit | part of the 377 idle minutes; 66 min on work-383069 | a rule | workflow |
| 7 | Stop a looping answer (zlib ratio < 0.15 over 6,000 characters) | 34 % of tokens at T 0.6 (measured offline); nothing at T 1.0 | 45 min | infra; changes cap-hit rows |
| 8 | GPU access for frustea | 0 GPU jobs all day | account | people |
| 9 | vLLM installed in the image | 25-47 s per fresh container (measured) | 20 min | infra |
| 10 | FP8 KV cache or B200 | about 1.8-2.5x tokens/s (estimate, no pilot yet) | 10 min + 50-problem check | infra; not comparable with bf16 cells |

Not worth doing: several cells in one container (the KV cache is already full); fixing the small command errors
(under 1 min each); hook overhead (about 100k characters all day).

## What the traces could not show, and the fix

| Gap | Fix |
|---|---|
| Teammates' transcripts and job records | done: hooks upload them every 10 minutes and at session end (main 74c8786) |
| Stage times of a job (setup, model load, generation), tokens/s, KV use, GPU utilisation: read from log text by hand | the runner writes them into the job record |
| Which work item a job belongs to: matched by branch, 12 of 42 submits recorded no branch, cycle.py printed -51 min | `gpu.py submit --work <id>` |
| `msg.py`, `recall.py`, `exa.py`, `vast.py` calls | log them like the other tools (tools/events.py) |
| Whether an idle agent waited for a person who was away or busy elsewhere | not recoverable from transcripts |
