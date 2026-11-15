---
name: theory
description: Build theories that connect the team's experiments, and score each by prediction instead of by opinion. One round runs studies/theory/lib/round.py - headless Claude runs in empty directories write theories from the board items before a cutoff; fresh advocate agents state intervals for the held-out numbers after the cutoff; each theory is scored by log gain against two no-theory readers and against its own reversal; candidates' offline predictions are computed from stored per-problem rows by scripts fixed before the run; survivors get a refutation search, a novelty check, and forward predictions posted before their experiments run. Use when the user asks for a theory, an explanation across experiments or what the results mean together, and after every fifth closed result. Writes studies/theory/results/engine/round-<nn>/ and updates studies/theory/README.md.
---

# Theory round (version 3)

A theory is one mechanism sentence that explains numbers from at least two studies and predicts numbers nobody has
measured. A theory stands when all three hold:

1. Its advocate's claims gain probability on held-out results against two readers with no theory, and gain more than
   the claims for its reversal (the same theory with every effect reversed).
2. None of its offline predictions, computed from stored per-problem rows, meets its own refuting condition.
3. The review finds no result that contradicts it and that its scope does not exclude.

(2) and forward predictions measured later are the stronger evidence; (1) is a filter that picks what to test.

## The coordinator's job

Run the stages, read the tables, decide what to post. Write no theory, claim, target or prediction, and do not edit
the agents' files: you have read the whole board, so anything you write carries held-out numbers. Work in your own
worktree, claim a `work` item, and `git pull origin main` first so the inventory sees every committed row file.

## Keeping held-out numbers hidden

- Every model call except `inventory`, `test` and `review` is a headless `claude -p --restricted` run in an empty
  directory outside the repository, with only Read and Write. Its context holds no git status (whose commit subjects
  carried held-out numbers in round 02), no CLAUDE.md, no memory, no board. It sees only the files copied in.
- `external` may also run `lib/papers.py`, which passes paper entries of `tools/recall.py` (board items and session
  notes are filtered out) and `tools/exa.py`. Every other command is denied.
- `inventory.md` names row files and their fields, never a result number. Read it before `generate`; if it holds an
  accuracy or a difference, delete that line.
- When a held-out number reaches an agent another way, list its item in `<round>/exposed.json`
  (`{"items": [...], "why": "..."}`): `score` leaves its targets out.
- `standing` stops if the previous round's held-out items are not all before the new cutoff.

## Choosing the cutoff

The cutoff is the posting time of the oldest result or knowledge item that no earlier round held out. Print the
newest items with `uv run tools/board.py ls result knowledge --new --n 40` and compare with the previous round's
`after.jsonl`: the new cutoff is after every item of that file. Wait for about 15 new result items (40-70 targets).

## The commands

`R=studies/theory/results/engine/round-<nn>` (next free number), `P=` the previous round's folder.

```
uv run studies/theory/lib/round.py $R all --cutoff <ISO time> --skip gpuprice --from $P
```

runs every stage in order; a job whose outputs exist is skipped, so the same command resumes a stopped round. Job
dirs (prompt.txt, out.txt) are under a printed temp folder. Prompts: `studies/theory/lib/prompts/<stage>.md`.

| stage | model | writes |
|---|---|---|
| `split --cutoff T --skip W` | none | `before.jsonl`, `after.jsonl` (check.py dump) |
| `standing --from $P` | none | `theories/` (previous passing theories, unchanged, minus reviews saying refuted or published), `prior_reviews/`, `prior_scores.json` |
| `inventory` | opus, repository, read-only | `inventory.md`: every stored per-problem row file, how to fetch it, its setting and row fields |
| `targets` | sonnet | `targets.jsonl` (targets whose quote or value fails the check are dropped and printed), `targets_blind.jsonl` |
| `external` | opus, papers.py only | `external.md`: 20 to 30 published findings by mechanism |
| `generate --starts all,surprises,across,external,revise` | opus | `external_<start>.md`, `drafts/`, `theories/r<n>-<start>-<k>.json`, `dropped.json`, `theories.sha256` |
| `null` | opus, 2 jobs | `predictions/null-1.jsonl`, `null-2.jsonl`: value and 90 % interval for every target |
| `claims` | opus, 1 advocate per theory | `claims/<theory>.jsonl`: intervals only where the mechanism speaks |
| `score` | none | `metrics_v3.json`, table |
| `reverse` | sonnet rewrite, opus advocate | `reversed/<theory>.json`, `claims/<theory>.rev.jsonl` on the same target ids, then score |
| `test` | opus, repository, laptop only | `tests/<theory>/p<k>.py` written by the agent, run once by the script: `tests/<theory>.json`, then score |
| `review` | opus, repository | `reviews/<theory>.json` for the top 3 passing theories |

`generate` checks every new theory: the form, at least 5 quotes from 2 items, imports that are external.md headings,
at least 2 offline predictions with a `recipe` and `gpu_minutes: 0`, and every quote verbatim (check.py). A failing
theory is sent back once with the messages, then dropped. `--model-all sonnet --min-targets 3` runs a cheap smoke
test on a hand-made round folder outside `studies/`.

## The score

A claim (value, low, high) is a normal density with sd = max((high - low) / 3.29, 0.01 * max(|value|, 1)); the
null is the equal mixture of the two no-theory readers' densities built the same way. Gain = log claim density minus
log null density at the measured value, clipped to [-3, 3] nats. Per theory: claims, total and mean gain, and a 90 %
bootstrap interval of the total (2,000 resamples, seed 0). States: `fails` (interval reaches 0 or below),
`candidate` (lower bound above 0, no reversal yet), `passes` (total above its reversal's total),
`fails: reversal as good`, `refuted` (an offline test met its refuting condition; overrides passes).

## When a stage stops

It prints the job and its `out.txt`. Read out.txt. A model that wrote no file or broken JSON: delete nothing, rerun
the same command; the job runs again. A crashing test script (`tests/<theory>/p<k>.out.txt`) printed no number:
delete `tests/<theory>/` once for fresh scripts. Never edit a recipe or a script. Fewer than 15 targets: post that
the board has too few new results and stop.

## Posting

For each theory with state `passes` and a review verdict of `stands` or `weak`, post one `idea` item: the statement,
total gain with its interval and number of claims, the reversal's total, offline tests inside / outside, the nearest
published claim, and its GPU predictions with intervals. Predictions are posted before their experiments run. Then
post as an `idea` the experiment where the passing theories' predictions differ most per GPU minute, naming the
theories it separates. A theory whose review says `published` is posted as a `knowledge` item instead.

Before each round, score the open forward predictions in `studies/theory/README.md` (measured value, item, inside or
outside; two outside refute the theory).

## Recording

`$R/run.json`: commit, cutoff, counts of items, targets, theories, jobs per stage, the temp folder. `$R/examples.json`:
one claim of the best theory with a positive gain and one with a negative gain, with both nulls. Add a row per theory
to the table in `studies/theory/README.md` (statement, round, total gain and interval, reversal, tests, state,
verdict, forward predictions) in the same commit. Close the `work` item with `done`:
`theory round <nn>: <k> of <m> theories pass (<claims> claims, total <g> nats [lo, hi]); offline tests <i> inside,
<o> outside; forward predictions of earlier rounds: <i> inside, <o> outside. $R/metrics_v3.json`

## Cost per round

About 40 headless jobs, nearly all opus: 1 inventory, 1 targets (sonnet), 1 external, 5 generators plus up to 10
send-backs, 2 nulls, one advocate per theory (about 15), 3 per candidate (reversal rewrite, its advocate, tests), up
to 3 reviews. No GPU. Generators and the external search take longest (10 to 20 minutes each, run in parallel).

## What a round may claim

- A gain is evidence about these targets, not proof of the mechanism. Say the number of claims and the interval
  every time: a theory with few claims can pass on luck.
- The held-out items enter `before.jsonl` of the next round: a theory is tested on them once.
