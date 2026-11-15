# Round 16 (engine 16): accounts tested against an adversary's alternative for every consequence

Written before the round (2026-11-15, about 23:50 UTC, abaybektursun). Board work-5d5e8a, knowledge-ab9881. Engine
version 16 (`lib/forecast.py synthesis`, `.claude/skills/theory/SKILL.md` version 16, commit d2ab1c4), branch `theory`
only (main is frozen; nothing goes to main). No GPU jobs; no model forward pass on the laptop.

## Why

Round 15: 6 of 9 consequences held, but the audit (knowledge-ab9881) found 3 of 4 designs faulty (a null false by
construction, a null that ignores accuracy, one measurement credited twice) and the three accounts barely differed.
Engine 16 adds accounts written in sequence with denials, a blind adversary per consequence whose value the interval
must exclude, one measurement one credit, and blind fact markers.

## Command

```
PYTHONUNBUFFERED=1 uv run studies/theory/lib/forecast.py synthesis studies/theory/results/wide/round-16 --from studies/theory/results/wide/round-15 studies/theory/results/wide/round-14 studies/theory/results/wide/round-13 studies/theory/results/wide/round-12 studies/theory/results/wide/round-11 studies/theory/results/wide/round-10 studies/theory/results/wide/round-09 studies/theory/results/forecast/run-0{2,3,4,5,6,7,8} studies/theory/results/forecast/cells-01 2>&1 | tee studies/theory/results/wide/round-16/round16.log
```

Run to the gate; commit the account, marker, adversary and plan files at once, before any test runs. Then one opus
subagent per test in `synthesis_tests.md` (denied consequences first, at most 9 at once; each: spec committed first,
own worktree and branch from `origin/theory`, offline stored rows only, own script under `studies/theory/analysis/`,
outputs under `studies/theory/results/direct/<name>-01/`, the adversary's value computed FIRST, n and 90 % bootstrap
interval, 10 raw rows read, rows through `forecast.py add-rows`, board work item closed with `done`). Rerun the same
command for `synthesis.md`.

Re-test of round 15's three audited consequences under the new rule (one subagent, `retest15-01`): s100vote with the
audit's adversary value +6.24 (final RL's per-right-count vote gain applied to step 100); edit0of4 under one
measurement, one credit (same rows as d1); merge328 against the adversary "wrong answers share values at the measured
wrong-pair agreement" (value computed from the stored rows by simulation that keeps each problem's right count).
Mechanisms `round-15/account-2/c<j>@16`.

## Hypotheses (each with the observation that refutes it)

- H1 (an account survives a real adversary): at least 2 consequences of one account hold (interval inside its range,
  excludes the adversary's value, n of 50 or more). Refuted when no account has 2 such consequences.
- H2 (the adversary bites): at least 2 of the 9 consequences come out `not separated` (interval inside the range but
  containing the adversary's value). Refuted at 0 or 1: then the adversaries were too weak to matter, or the accounts
  already guarded against covariates.
- H3 (sequence makes the accounts differ): the accounts disagree on at least 4 testable claims (denials that pass the
  code check). Refuted at fewer than 4 (the check requires 4 when no account is dropped, so this is also a check that no
  account is dropped).
- H4 (denials decide): at least 2 denials are decided (the denied consequence refuted or the denier's range refuted).
  Refuted when 0 or 1 denial is decided (all undecided).
- H5 (self-marking is generous): the blind marker marks more facts "contradicts" or "not addressed" than the account's
  own marks, for at least 2 of 3 accounts. Refuted when the marker is as generous as or more generous than the accounts.
- H6 (round 15 under the new rule): s100vote is `not separated` (+6.24 inside [6.03, 8.37]); edit0of4 earns no
  separate credit; merge328 is `not separated`. Refuted for each consequence that holds under the new rule.
- H7 (speed): standing to the gate under 35 minutes (accounts are now sequential: about 3 x 7 minutes). Refuted at 35
  or more.

## Outputs

`studies/theory/results/wide/round-16/`: `standing.*`, `direct_facts.json`, `synthesis_facts.json`,
`account-<k>.json`, `marks-account-<k>.json`, `adversary/`, `synthesis_tests.md` / `.json`, `synthesis.md`,
`run.json`, `round16.log`. Test outputs under `results/direct/<name>-01/`; rows in `results/direct_tested.json`
(refuted also in `refuted.json`). README section "Round 16".
