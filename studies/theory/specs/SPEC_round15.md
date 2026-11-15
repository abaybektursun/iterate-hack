# Round 15 (engine 15): three single accounts of every direct fact, each tested on new consequences

Written before the round (2026-11-15, about 23:10 UTC, abaybektursun). Board work-4948a7, idea-09edb8. Engine version
15 (`lib/forecast.py synthesis`, `.claude/skills/theory/SKILL.md` version 15, commit 46338f7), on branch `theory`
(main is frozen; nothing goes to main). No GPU jobs; no model forward pass on the laptop.

## Why

Rounds 13 and 14 ran 34 direct tests: 9 hold, 16 refuted, the rest undecided; in round 14 the null's range won 3 of 5
pairs. Mechanisms written about one surprise at a time lose to the null. The 42 direct facts (refuted.json and
direct_tested.json, each once) and the last 24 hours of board results have never been put into one account.

## Command

Only standing, direct facts and synthesis this round (no surprise pairs):

```
uv run studies/theory/lib/forecast.py synthesis studies/theory/results/wide/round-15 --from studies/theory/results/wide/round-14 studies/theory/results/wide/round-13 studies/theory/results/wide/round-12 studies/theory/results/wide/round-11 studies/theory/results/wide/round-10 studies/theory/results/wide/round-09 studies/theory/results/forecast/run-0{2,3,4,5,6,7,8} studies/theory/results/forecast/cells-01
```

Run to the gate (log `round15.log` in the round folder), commit the account files at once, run every test in
`synthesis_tests.md` (disagreements first; one opus subagent per test, at most 9 at once, each with its own spec,
worktree and branch from `origin/theory`; offline on stored rows; script under `studies/theory/analysis/`, outputs
under `studies/theory/results/direct/<name>-01/`, n and 90 % bootstrap interval, the engine-14 verdict rule), record
rows with `forecast.py add-rows`, then the same command again for `synthesis.md`. Before each test, check that no
posted result already decides it; if one does, use the posted number.

## Hypotheses (each with the observation that refutes it)

- H1 (idea-09edb8): at least one account's new consequence holds against a strong null on n of 50 or more (90 %
  interval wholly inside the account's range, which is disjoint from the null's). Refuted when no consequence of any
  account holds.
- H2 (accounts beat the per-surprise mechanisms): the share of the accounts' consequences that hold is above round
  14's share of rival tests that held (1 of 12 rival rows, 0.08). Refuted at 1 of 9 or fewer.
- H3 (accounts are honest about contradictions): every kept account marks at least one fact "contradicts" or "not
  addressed". Refuted when an account marks all 42 facts "explained" (an account that fits everything is too vague
  to be tested).
- H4 (the accounts disagree somewhere testable): the judge lists at least one disagreement whose test separates two
  accounts on stored rows, and the test decides it (one account holds, another is refuted). Refuted when the judge
  finds no disagreement, or every disagreement test is undecided or refutes all accounts it names.
- H5 (speed): standing, direct facts and the three accounts with the judge take under 20 minutes of running time.
  Refuted at 20 or more.
- H6 (plans are runnable as written): at least 2 of 3 test plans run on their named stored rows with n of 50 or
  more. Refuted when more than a third need other rows or have fewer than 50.

## Outputs

`studies/theory/results/wide/round-15/`: `standing.*`, `direct_facts.json`, `synthesis_facts.json`,
`account-<k>.json`, `disagreements.json`, `synthesis_tests.md` / `.json`, `synthesis.md`, `run.json`, `round15.log`,
`jobs/`. Test outputs under `results/direct/<name>-01/`; rows in `results/direct_tested.json` (refuted also in
`refuted.json`). README section "Round 15".
