# theory

Question: which theories connect the team's experiments, measured by how well they predict results they have not seen?

A round is run with the `theory` skill (`.claude/skills/theory/SKILL.md`), which holds the procedure. Subagents propose
theories from the board items before a cutoff time. Each theory is scored by how much it improves a predictor's guesses of
the numbers posted after the cutoff, against the same predictor without the theory.

## Files

| Path | What |
|---|---|
| `lib/check.py` | The mechanical steps: `dump` splits the board at the cutoff, `check` verifies every quote against its board item, `score` compares each theory's predictions with the two no-theory predictors. Usage in its docstring. |
| `results/engine/round-<nn>/` | One round: `run.json`, `before.jsonl`, `after.jsonl`, `targets.jsonl`, `theories/`, `predictions/`, `metrics.json`, `examples.json`. |

## Theories

No round has run yet.

| Theory | Statement | Round | Backtest (closer, farther vs each null; noise) | Status | Forward predictions |
|---|---|---|---|---|---|
