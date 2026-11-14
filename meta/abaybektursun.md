# Meta review: abaybektursun

## 2026-11-14 21:55 UTC (after result-bede69, literature work-a028d2)

- Last entry's checks: --shard has not landed (`grep shard studies/rlneurons/jobs/run_cell.py`: none); e72c, 86ef, d4fa still running at 34-36 min; work-d8aa69 open 41 min. Carried.
- Direction: mission = "how much of a published RL gain an untrained base model reaches with no training" (DIRECTION.md). work-a028d2 read 7 papers (48 findings, knowledge-29fdeb), no GPU. It sets priors for two Day-1 steps: RAST 2506.15710 already shows decode-time RL-minus-base logit transfer recovers 95 % on Qwen-32B MATH-500, so the weight-scaling study (Day-1 #4) adds only its Code-RL and random controls and the same-size weight form; short-m@k 2505.17813 says length rules work only within a problem (sent to work-a992bd). No drift.
- Research: no replication. Power sampling 2510.14901 gets most of its gain from T 0.25 alone (69.0 of 74.8) at a 3,072 cap, the opposite of our T 0.6 loops: a setting difference to state, not a run.
- Turnaround (`uv run tools/cycle.py --hours 1`): to-job 0, jobs 5 (was 5), to-answer none closed. 134.4 container min (13.6), 0 failed (3.6). Queue wait now 8.0 and 12.9 min for 7f81, 7ba0, three jobs queued: 4 H100 busy, so the GPU limit is the new slowest part of jobs.
- Failure: Exa MCP returned 401 at the first search (EXA_API_KEY unset; .mcp.json sends an empty header), found only after planning. Change (step 2 then 5, code): the SessionStart hook in .claude/settings.json prints a warning when EXA_API_KEY is unset, so the session learns at start.
- Next entry checks: --shard landed or not; queue wait of a32d, 208b, f4ab; whether a session starts with the Exa warning gone after the key is set.

## 2026-11-14 21:21 UTC (after the 5th GPU job since the last entry)

- Last entry's checks: Day-1 #1 claimed 21:10 (work-d8aa69), check job abaybektursun-1114-151028-ec3c submitted 21:10:28, first token about 21:12:50, so 30 min from runnable (20:43) to first token. team-meta-review loads the project text.
- Direction: mission = "how much of a published RL gain an untrained base model reaches with no training" (DIRECTION.md). Since 21:10: 3 jobs, all 3 test the mission sentence (check 8/10 v3, then base+cue and RL on hard328 at T 1.0, both running). Day-1 #2 (work-55d1fe) and #3 (work-63fac2) are claimed. 1 non-mission step: tools/view.py (75f0bf4). No drift.
- Research: no replication. sameraslan's knowledge-d692e4 and knowledge-8a31ad (21:12) list what is published; Day-1 #3's vote row has a prior (Maj@4 +0.8 points, 2507.18122 Table 1; comment on idea-8b9cc7): check it before spending the 4x tokens.
- Turnaround (`uv run tools/cycle.py`, previous in brackets): median to-job 0 min, jobs 5 min, to-answer not yet closed; slowest stage: jobs (was: decision to first job). 13.6 container minutes (6.7), 3.6 failed or cancelled (3.6): 0 of the 3 new jobs failed. Median queue wait 0.1 min.
- Cause, from the logs (`gpu.py logs`): generation is limited by KV memory, not by setup. e72c: KV cache 196,916 tokens, 128 sequences running at 21:16:37 (6,786 tok/s), 26 running and 291 waiting at 21:18:47 (965 tok/s, KV 99.7 %), 11 of 328 finished after 140 s. Same finding as SPEC4.md section 3. Setup is small beside it: setup_vllm.sh 30 s, engine init 29 s; 86ef took 3 min to first token (first load of the RL weights). In the check job, 125 s of 231 s wall were generation and the last 90 s were one request at 135 tok/s.
- Change (step 4; steps 1-2: the 16,384 cap and T 1.0 are the mission's settings, nothing to delete): split a cell over N GPUs, `run_cell.py --shard k/N` taking `probs[k::N]` (seeds are per problem index, so rows do not change). 4 shards cut a KV-bound cell about 4x. Not made in this session: run_cell.py has a writer now (work-63fac2), and two writers never edit one file. Carried to that writer.
- Failures: none since the last entry. meta/FAILURES.md row (vLLM built per job, 30 s) stays; it is 30 s of a job that runs tens of minutes, so it is not the next change.
- Next entry checks: wall minutes of e72c and 86ef against the first sharded cell; whether --shard landed; to-answer minutes of work-d8aa69.

## 2026-11-14 21:10 UTC (first entry)

- Direction: mission = base vs RL gap on the 328 harder problems (DIRECTION.md). Day-1 #1 and #2 (idea-b19ad2, idea-1bd34f) posted 20:14, runnable since 20:43 (knowledge-e1d4b9), unclaimed at 21:10: 56 min from decision with no mission GPU second. 0 of 8 jobs today test any part of the mission sentence (all porting and smoke, `uv run tools/cycle.py --hours 3`). This session spent 20:32-21:02 on coordination tools (2d5ee99, 4016064) while the rows waited: conflicts with "small, cheap, decisive runs".
- Research: no replication run; the open steps (#1, #2) are not answerable from published tables (Wang et al. 2610.06851 use T 0.6, cap 31,744, their grader).
- Turnaround: slowest stage is decision to first job (no claim), not the job. Per job on H100 (job abaybektursun-1114-123728-8181 log): setup_vllm.sh 24 s, weights 9 s, engine init 53 s (compile 19.5 s), so ~1.5 min to first token. Failed or cancelled: 3 of 8 jobs, 3.6 of 6.7 container minutes (the vLLM setup fix loop, 20:32-20:41).
- Failures: the personal skill ~/.claude/skills/meta-review shadowed the project skill of the same name, so this person's agents loaded EC2 instructions. Step 2 (delete the collision): project skill renamed to team-meta-review, references updated. vLLM built per job: meta/FAILURES.md.
- Change: the rename (this commit). Next step for the mission: claim and run Day-1 #1 and #2 now (the T1 --n 10 check first, studies/rlneurons/README.md).
- Next entry checks: minutes from 20:43 to the first Day-1 job's first token, and whether team-meta-review loads the project text.
