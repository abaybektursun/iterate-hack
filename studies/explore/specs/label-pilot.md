# Label pilot: does the label "current program" decide the method a frontier model writes? (written before the runs, 2026-11-17)

Design agreed in a two-round exchange with a second model (gpt-6.2-sol through the Codex CLI). Follows assign-01:
gpt-5.4-mini listed an optimizer among good methods and did not write one when asked to improve a hand-made program.

- Every call shows the task and the same two working programs A and B in the same order, built on different
  methods with close validation scores (`data/label_pilot_v1/`, frozen; re-scored 2026-11-17: ahc014 A 0.571,
  B 0.552; circles26 A 2.583, B 2.594). Only the label changes: one is "the CURRENT PROGRAM", the other "a
  REFERENCE PROGRAM". Two label conditions per task: A current, B current.
- Calls per task and label condition: 1 ranking call (rank the 4 menu methods of `tasks.json` by the validation score
  expected from ONE reply with a complete program under the task's limits), F free calls ("Write your next
  version."), 1 call assigned the top-ranked method, 1 call assigned the runner-up. Fresh chat for every call.
- Model: gpt-6.2-sol, default settings. Tasks: ahc014 and circles26 (the second model asked for three tasks; only
  two have a scorer and stored programs of two methods, so both must pass).
- Measures. built_on: line-level similarity (difflib ratio) of a submission to A and to B; it builds on X when
  sim(X) - sim(other) > 0.15, else "neither". Method of a free submission: read by hand against the menu, using
  the code (a loop that removes part of a kept solution and regrows = A on ahc014; a loop that builds from scratch
  = B; kept set of partial states = C; temperature acceptance = D; same idea for circles26), hybrids and
  unclassified kept in the count. Validation score of every submission.
- H2 (label): the free submissions build on the program labelled current under both label conditions, while the
  top-ranked method is the same under both. Refuted on a task if free submissions build on the same program (or
  neither) regardless of the label.
- H1 (own advice): a free submission whose method differs from the top-ranked one scores below the assigned-top
  submission by at least 10 % of the gap between the lower reference score and the best known score (ahc014 1.0,
  circles26 2.636), and assigned-top also beats assigned-runner-up.
- Stop rule: continue to the 12-task run only if H2 or H1 holds on both tasks. A pilot of this size decides spending,
  not a claim.
- Cost cap: 15 USD (`--max-usd`); the script stops before a call that could exceed it.
