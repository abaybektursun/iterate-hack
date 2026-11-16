# Round 17 (engine 17): accounts read the explore half of the problems, tests run on the test half

Written before the round (2026-11-16, about 00:27 UTC, abaybektursun). Board work-360669. Engine version 17
(`lib/forecast.py synthesis`, `lib/rows.py`, `data/split_v1.json`, `.claude/skills/theory/SKILL.md` version 17, commit
ac2f163), branch `theory` only (main is frozen; nothing goes to main). No GPU jobs; no model forward pass on the laptop.

## Why

Round 16: 0 of 9 consequences held against the adversary; 6 were undecided at the edge of a guessed range, and 7 of 9
adversary values were guesses at the wrong scale, because neither the account writers nor the adversaries could read
the stored rows. Engine 17 splits every problem set's ids once into explore and test halves; writers and adversaries
compute on the explore half (Bash in a folder holding only those rows), and tests run on the test half.

## Command

```
PYTHONUNBUFFERED=1 uv run studies/theory/lib/forecast.py synthesis studies/theory/results/wide/round-17 --from studies/theory/results/wide/round-16 studies/theory/results/wide/round-15 studies/theory/results/wide/round-14 studies/theory/results/wide/round-13 studies/theory/results/wide/round-12 studies/theory/results/wide/round-11 studies/theory/results/wide/round-10 studies/theory/results/wide/round-09 studies/theory/results/forecast/run-0{2,3,4,5,6,7,8} studies/theory/results/forecast/cells-01 2>&1 | tee studies/theory/results/wide/round-17/round17.log
```

Run to the gate; commit the account, marker, adversary and plan files at once, before any test runs. Then one opus
subagent per test of `synthesis_tests.md` that is neither rejected nor dropped (at most 9 at once; each: spec committed
first, own worktree and branch from `origin/theory`, test half only via `rows.load(set, cell, "test")`, own script under
`studies/theory/analysis/`, outputs under `studies/theory/results/direct/<name>-01/`, the adversary's test-half value
computed FIRST, n and 90 % bootstrap interval over problems, 10 raw rows read, rows through `forecast.py add-rows`,
board work item closed with `done`). Rerun the same command for `synthesis.md`. Stop and report if the round passes 75
minutes.

## Hypotheses (each with the observation that refutes it)

- H1 (reading rows makes consequences that separate): at least 3 of the 9 consequences survive the explore-half filter
  (the adversary's explore value lies outside the account's explore interval) and are not rejected. Refuted at 2 or
  fewer.
- H2 (they replicate on unseen problems): at least 2 of the surviving consequences hold on the test half (interval
  inside the range, excluding the adversary's test-half value, n >= 50). Refuted at 0 or 1.
- H3 (ranges fit the noise): fewer than half of the tests end `undecided`. Refuted when half or more do (then 2.5
  explore interval widths is still too narrow, or n of the test half too small).
- H4 (adversaries land on scale): the adversary's test-half value lies within one explore interval width of the
  measured test value in at least half of the tests (round 16: 2 of 9 inside the interval). Refuted below half.
- H5 (explore predicts test): the test value lies inside the account's explore 90 % interval widened by sqrt(2) in at
  least 70 % of the tests. Refuted below 70 % (a sign of selection on the explore half: the writers picked statistics
  whose explore value was high by chance).
- H6 (speed): standing to the gate under 25 minutes (accounts in parallel again, but with Bash and computation).
  Refuted at 25 or more.

## Outputs

`studies/theory/results/wide/round-17/`: `standing.*`, `direct_facts.json`, `synthesis_facts.json`,
`explore_manifest.md`, `account-<k>.json`, `marks-account-<k>.json`, `adversary/`, `synthesis_tests.md` / `.json`,
`synthesis.md`, `run.json`, `round17.log`. Test outputs under `results/direct/<name>-01/`; rows in
`results/direct_tested.json` (refuted also in `refuted.json`). README section "Round 17".
