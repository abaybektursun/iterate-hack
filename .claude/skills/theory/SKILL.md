---
name: theory
description: Build theories that connect the team's experiments, and score each by prediction instead of by opinion. One round - subagents propose theories from the board items posted before a cutoff time; each theory is scored by how much it improves a predictor's guesses of the numbers posted after the cutoff, against the same predictor without the theory; survivors get a search for contradicting results, an Exa novelty check, and forward predictions posted to the board before the experiments run. Use when the user asks for a theory, an explanation across experiments or what the results mean together, and after every fifth closed result. Writes studies/theory/results/engine/round-<nn>/ and updates studies/theory/README.md.
---

# Theory round

A theory here is one mechanism sentence that explains numbers from at least two studies and predicts numbers nobody has
measured. It is accepted on one ground only: a predictor that reads it guesses held-out results better than the same
predictor without it. No model rates a theory's accuracy or its own novelty.

You are the coordinator. You have read the whole board, so you do not write, reword or choose between theories:
subagents write them, `studies/theory/lib/check.py` scores them. You pass files along, run the script and report.

## What keeps the held-out numbers hidden

The backtest means nothing if a held-out number reaches a generator or a predictor. Three rules:

1. Generators and predictors are told the exact files to read and the one file to write, and that no other tool call
   is allowed: no board, no messages, no git, no search. The measured values are in the repository and on the board.
   (The message hook does nothing for a subagent's tool call, so reading a file by path is safe.)
2. Their files are only `before.jsonl`, and for predictors `targets_blind.jsonl` and at most one theory. Never
   `after.jsonl`, `targets.jsonl`, your own summary of a result, or another theory's score.
3. A target's `what` describes the measurement without its outcome: "right of 500, MATH-500, T 1.0, cue, base + 0.5 *
   (RL - base)", never "the gain from the RL direction".

## The round

Work in your own worktree (`AGENTS.md`). Claim a `work` item first. `<round>` is
`studies/theory/results/engine/round-<nn>`, with the next free number.

### 1. Score the open forward predictions

`studies/theory/README.md` lists the forward predictions of earlier rounds. For each open one, search the board for a result
that measured it. Write the measured value, its item id and "inside" or "outside" the predicted interval beside it. A theory
with two predictions outside its interval is marked refuted. This step is the engine's real test: report the count
inside and outside in the round's result.

### 2. Split the board

```
uv run studies/theory/lib/check.py dump <round> --skip gpuprice
```

writes `before.jsonl` and `after.jsonl` and prints the cutoff: the newest quarter of result and knowledge items is held
out. `--skip` drops items of other projects. With more than 150 items in `before.jsonl`, give each generator a random
100 of them, a different sample each.

### 3. Targets (one subagent, model sonnet)

It reads both files and writes `<round>/targets.jsonl`, one line per measured number in `after.jsonl`:

```
{"id": "t01", "item": "result-9b6af3", "what": "<the measurement, without its outcome>", "unit": "right of 500", "value": 441, "quote": "theta0.25 441"}
```

`quote` is copied verbatim from the item and holds the value. It skips a number that already appears in `before.jsonl`
(a repost), a count of files or papers, and a cost. It aims for 20 to 60 targets. Fewer than 15 targets: stop and
report that the board has too few new results for a round.

### 4. Generators (three subagents, model opus, at the same time)

Each prompt holds `DIRECTION.md`, the items of `before.jsonl` and the theory form below. Each returns its two best
theories. The three differ in where they start:

- **all**: the items as a whole.
- **surprises**: only from hypotheses the items report as refuted, predictions that failed, and controls that did as
  well as the treatment. A theory must explain at least two of these.
- **across**: each theory must connect two studies whose items do not cite each other (for example a sampling result
  and a weight-difference result).

Save each as `<round>/theories/<start>-<n>.json`:

```
{"name": "across-1",
 "statement": "<one sentence: the mechanism>",
 "scope": "<models, settings and benchmarks it claims to cover, and what it does not cover>",
 "explains":  [{"item": "result-xxxxxx", "quote": "<verbatim from the item>", "how": "<one sentence>"}],
 "conflicts": [{"item": "result-xxxxxx", "quote": "<verbatim>", "how": "<why it does not fit>"}],
 "rival": "<the strongest other explanation of the same items, and the observation that would separate the two>",
 "predictions": [{"experiment": "<one not yet run, exact setting>", "unit": "right of 500", "value": 447, "low": 440, "high": 455,
                  "refuted_by": "<the observation that refutes the theory>", "gpu_minutes": 20}]}
```

At least three predictions, each on an experiment that no item reports, and `explains` from at least two studies.
An empty `conflicts` list is allowed only when the generator states it looked.

### 5. The planted theory (one subagent, model sonnet)

It gets `all-1.json` and writes `<round>/theories/planted.json`: the same form with the direction of every effect
reversed. The backtest must score it below the null. If it beats the null, the backtest does not discriminate: report
that as the round's result and accept no theory.

### 6. Check, then predict (model sonnet, all at the same time)

```
uv run studies/theory/lib/check.py check <round>
```

fails on any quote that is not in its item, and writes `targets_blind.jsonl`. A theory that fails goes back to its
generator once with the script's message, then is dropped.

Then one predictor per theory, and two predictors with no theory (`null-1`, `null-2`). Each prompt holds
`before.jsonl`, `targets_blind.jsonl` and one theory or none, the same wording otherwise. Each returns one number for
every target, saved as `<round>/predictions/<theory name>.jsonl` (`null-1.jsonl`, `null-2.jsonl`), lines
`{"id": "t01", "value": 447}`.

### 7. Score

```
uv run studies/theory/lib/check.py score <round>
```

For each theory: the number of targets where its predictor is closer to the measured value than each null, and
farther. `noise` is the same count between the two nulls. A theory beats the null when closer minus farther, against
each null, is above `noise`. The table is in `<round>/metrics.json`. If no theory beats the null, that is the result:
post it and stop.

### 7b. Predictions the held-out items already measured

Some of a theory's own predictions name an experiment that a held-out item reports. One subagent (model sonnet) gets
`theories/` and `targets.jsonl` and writes `<round>/predictions_measured.json`: theory, experiment, predicted value,
interval, the target ids, the measured value, inside or outside, and the two nulls' predictions for the same targets.
Report the count inside and outside per theory next to the backtest line. In round 01 the count over all targets
(step 7) did not separate real theories from the planted one, and this table did carry information: most targets are
measurements no theory speaks about.

### 8. Refutation and novelty (one subagent per surviving theory, model opus, tools allowed)

Each survivor's subagent gets the theory and both item files, and returns two things, appended to the theory's file
under `"review"`:

- **Refutation.** The item, with a verbatim quote, that contradicts the theory most strongly, read at its artifact in
  git when the item names one; or "none found" with the items it read. Then whether the `rival` explains the held-out
  targets as well.
- **Novelty.** `python3 tools/recall.py` and `python3 tools/exa.py search` with at least three phrasings of the
  mechanism in the field's terms. The nearest published claim, its URL, and in one sentence what the theory says that
  the paper does not. If a paper states the theory, it is marked "published" and posted as a `knowledge` item instead.

A theory with a contradicting item that its scope does not exclude is marked refuted.

### 9. Post

For each theory that survived step 8, post one `idea` item: the statement, its backtest line from `metrics.json`, the
nearest published claim, and its predictions with intervals. Then choose the experiment where the surviving theories'
predictions differ most per GPU minute and post it as an `idea` naming the theories it separates. Predictions are
posted before any of their experiments run.

### 10. Record

In `<round>/run.json`: commit, cutoff, counts of items, targets and theories, the subagent count. Save one target the
best theory predicted closely and one it missed, with both predictions, as `<round>/examples.json`. Update
`studies/theory/README.md` in the same commit: one row per theory with its statement, round, backtest line, status
(open, refuted, published) and its forward predictions with their state. Close the `work` item with `done`:

```
theory round <nn>: <k> of <m> theories beat the null on <t> held-out targets (noise <x>); planted theory +<a> -<b>;
forward predictions of earlier rounds: <i> inside, <o> outside. studies/theory/results/engine/round-<nn>/metrics.json
```

## Cost

About 17 subagents a round: 1 for targets, 3 generators, 1 planted, about 9 predictors, up to 3 reviews. The
predictors are short calls with no tools. No GPU.

## What a round may claim

- "Beats the null" means the theory helped predict this round's held-out numbers. It is evidence about those targets,
  not proof of the mechanism. Say the number of targets and the noise every time.
- A theory becomes more than a candidate only through step 1: forward predictions, posted first, that came out inside
  their intervals.
- The held-out quarter is not seen by generators in its own round. It is in `before.jsonl` of the next round.
