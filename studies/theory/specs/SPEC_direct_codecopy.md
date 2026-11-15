# SPEC: shared direct test of rival pair round-14/s6 (codecopy-01)

Board work-e60cfb. Written before the readout was computed. Stored rows only: no GPU job, no forward pass.

## The claim

Surprise: base + RL-Code's top-8 directions per matrix at 1.5x passes 399 of 538 (result-a1bf75). Plan:
`studies/theory/results/wide/round-14/jobs/rivals-s6.json`, field `test`.

- Rival `a` (base-mode sharpening): the edit raises the probability of the base's own passing programs. On problems
  the cued base passes but RL-Code mostly fails, the edit keeps the pass and lifts it above a base resample.
- Rival `b` (RL-policy copy): the top-8 directions carry RL-Code's own per-problem programs. On the same problems the
  edit loses the pass as RL-Code does.

## Set, rows and n

L = problems (of 538) that `code1/base_cue-01` passes and on which RL-Code fails in at least 2 of its 3 stored samples
(seeds 51M `code1/rl_plain-01`, 52M `xreward/code_hosts_s52/rl_plain-01`, 53M `xreward/code_hosts_s53/rl_plain-01`).

Rows entering: (problem in L, edit sample) for 5 edit samples per problem: Code top-8 1x at 51M
(`code_dial/code_top8_code31-01`), 52M (`code_hosts_s52/code_top8_code31-01`), 53M (`code_hosts_s53/code_top8_code31-01`),
Code top-8 1.5x (`code_dial/code_top8x1.5_code31-01`) and 2x (`code_dial/code_top8x2_code31-01`), all with the Code cue.
n = 5 x |L| rows; the plan expects about 100.

## Files

The committed folders hold only cell metrics and 2 examples. Per-problem rows are the job outputs
`runs/<job>/answers.jsonl` (copied with `gpu.py get`, not committed), job ids from each folder's `run.json`:

| cell | job |
|---|---|
| cued base | abaybektursun-1114-170304-c03c |
| RL-Code 51M | abaybektursun-1114-170253-f661 |
| RL-Code 52M | abaybektursun-1115-143247-929d |
| RL-Code 53M | abaybektursun-1115-143331-10da |
| Code top-8 1x 51M | abaybektursun-1115-101423-4a7d |
| Code top-8 1x 52M | abaybektursun-1115-143231-15bb |
| Code top-8 1x 53M | abaybektursun-1115-143316-628e |
| Code top-8 1.5x 51M | abaybektursun-1115-101434-4511 |
| Code top-8 2x 51M | abaybektursun-1115-101445-e35e |
| plain base (null) | abaybektursun-1114-170258-388e |
| Math-cue base (null) | abaybektursun-1114-170309-b137 |
| random rank-8 1.5x, Code cue (null) | abaybektursun-1115-101457-ef2c |

## Computation (as the plan)

1. One row per problem per cell (each cell holds one sample per problem). Pass = the stored `passed` field (all tests
   passed under the cell's grader); cap hits and no-block answers count as fail.
2. Build L.
3. Per problem in L, e = mean pass of its 5 edit samples. S = mean of e over L.
4. 90 % interval: 10,000 bootstrap resamples of the problems in L (with replacement, numpy default_rng(0)), 5th and
   95th percentiles of S.
5. Null: the same mean over L of the 3 base-like samples (plain base, Math-cue base, random rank-8 1.5x), same
   bootstrap. Also reported (not in the rule): RL-Code's mean pass on L and the edit's mean per cell.

Instrument check before the readout: the passed count of every cell's answers.jsonl must equal `counts.all.passed` in
its committed metrics.json; the same check fed the wrong file (RL-Code 52M rows against the Code top-8 1x 52M metrics)
must fail. Stop if either does not happen.

## Frozen ranges (copied from the plan)

a [0.70, 1.0]; b [0.0, 0.34]; null [0.38, 0.66].

## Verdict rule (engine 14)

n >= 50 required. An interval wholly inside one rival's range holds that rival and refutes the other. An interval
inside neither range and wholly outside both refutes both. An interval straddling a range boundary is undecided for
the rival(s) whose range it touches (the other is refuted if the interval is wholly outside its range).

## Changes from the plan

- The plan's files are cell folders; their per-problem rows are not committed, so the rows are read from the job
  outputs listed above (same jobs as each folder's run.json). No change to set, rows, statistic or ranges.
