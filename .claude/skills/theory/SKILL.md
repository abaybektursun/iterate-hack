---
name: theory
description: Build theories that connect the team's experiments, and test each on stored per-problem rows instead of by opinion. One round runs studies/theory/lib/round.py - headless Claude runs in empty directories propose pairwise different mechanisms from the board items before a cutoff and develop each into a theory with offline predictions; scripts written before any number is seen compute those predictions from the stored rows, against two no-theory readers; held-out board numbers and a review can only remove a survivor; survivors are posted with their GPU predictions before the experiments run, refuted theories as a result. Use when the user asks for a theory, an explanation across experiments or what the results mean together, and after every fifth closed result. Writes studies/theory/results/engine/round-<nn>/ and updates studies/theory/README.md.
---

# Theory round (version 4)

A theory is one mechanism sentence that explains numbers from the board and predicts numbers nobody has computed.
A theory survives when its own offline predictions, fixed before any row was read, were computed, none met its
refuting condition, and together they gained probability against readers with no theory. Held-out claims and the
review can only remove it. GPU predictions measured later are the strongest evidence and are posted first.

## What three rounds showed

- Round 01: helping a predictor on all held-out targets did not separate theories from a reversed control.
- Round 02: commit subjects in the git status leaked held-out results into subagents; reviews decided more than the
  score.
- Round 03: on clean fresh data, theories lost to the no-theory readers exactly where they diverged (15 of 21
  divergent claims lost), and 10 theories were 2 mechanisms, copied from the external findings' "Bears on" text.

So version 4 tests each theory on numbers it chose itself, computed from stored rows, and gets different mechanisms
by construction: one agent lists pairwise different mechanisms against a list of every failed theory, and a separate
agent develops each.

## The coordinator's job

Run the stages, read the tables, decide what to post. Write no mechanism, theory, recipe, claim or target, and edit no
agent's file: you have read the whole board. Work in your own worktree, claim a `work` item, and run
`git pull origin main` first so the inventory sees every committed row file.

## Keeping held-out numbers hidden

- Every model call except `inventory`, `test` and `review` is a headless `claude -p --restricted` run in an empty
  directory outside the repository, with only Read and Write: no git status, CLAUDE.md, memory or board.
- `external` may also run `lib/papers.py`: paper entries of `tools/recall.py` and `tools/exa.py`, nothing else. Its
  findings state a mechanism and where it was measured, never what it means for the team's models.
- `inventory.md` names row files, fetch commands and fields, never a result number. Read it before `mechanisms`; if
  it holds an accuracy or a difference, delete that line.
- `graveyard.json` holds earlier rounds' theories and their failure reasons. Its numbers are from before the cutoff.
  `standing` stops if the previous round's held-out items are not all before the new cutoff.
- When a held-out number reaches an agent another way, list its item in `<round>/exposed.json`.

## Choosing the cutoff

The cutoff is the posting time of the oldest result or knowledge item no earlier round held out. Print the newest
items with `uv run tools/board.py ls result knowledge --new --n 40` and compare with the previous round's
`after.jsonl` (when it has one): the new cutoff is after every item of that file.

## The commands

`R=studies/theory/results/engine/round-<nn>` (next free number), `P=` the previous round's folder.

```
uv run studies/theory/lib/round.py $R all --cutoff <ISO time> --skip gpuprice --from $P
```

runs every stage in order; a job whose outputs exist is skipped, so the same command resumes a stopped round. Job
dirs (prompt.txt, out.txt) are under a printed temp folder. Prompts: `studies/theory/lib/prompts/<stage>.md`.

| stage | model | writes |
|---|---|---|
| `split --cutoff T --skip W` | none | `before.jsonl`, `after.jsonl` |
| `standing --from $P` | none | `graveyard.json` (every earlier theory, state, verdict, reason), `theories/` (survivors carried), `prior_reviews/` |
| `inventory` | opus, repository | `inventory.md`: row files, exact fetch command, readable now yes/no, fields |
| `external` | opus, papers.py only | `external.md`: 20-30 published mechanisms with their numbers |
| `mechanisms --n-mechanisms 12` | opus | `mechanisms.json`: pairwise different, none restating the graveyard |
| `develop` | opus, 1 per mechanism | `theories/r<n>-m<id>.json` (3+ offline, 1+ GPU predictions), `dropped.json`, `theories.sha256` |
| `null_tests` | opus, 2 jobs | `tests_blind.jsonl`, `predictions/nulltest-{1,2}.jsonl` |
| `test` | opus, repository, laptop only | `tests/<theory>/p<k>.py` written first, run once by the script; `tests/<theory>.json` |
| `score_tests` | none | `metrics_v4.json`, table |
| `heldout` | sonnet, opus | survivors only: `targets.jsonl`, `predictions/null-*.jsonl`, `claims/`, strikes |
| `review` | opus, repository | `reviews/<theory>.json` for up to 3 survivors |

`develop` may abandon a mechanism the items already contradict (in `dropped.json`); that is a good outcome. A theory
that fails the check (form, verbatim quotes, recipes) is sent back once, then dropped. A test script prints a number,
"not computable" with the reason, or "refuted" when the recipe says a case refutes without a number. S3 reads use
`AWS_PROFILE=iterate-ecr`. Version 3 (`--version 3`) is still runnable. `--model-all sonnet --min-targets 3
--n-mechanisms 3` runs a cheap smoke test on a hand-made round folder outside `studies/`.

## The score

A prediction (value, low, high) is a normal density with sd = max((high - low) / 3.29, 0.01 * max(|value|, 1)); the
null is the equal mixture of the two test readers' densities. Gain = log prediction density minus log null density
at the computed value, clipped to [-3, 3] nats. States: `refuted` (any refuting condition met, or two computed
predictions outside their intervals), `survives` (2 or more computed, none refuted, total gain above 0), `untested`
(fewer than 2 computed), `no gain` (otherwise). Held-out: a claim both readers contradict that misses its own interval
is a strike; two strikes refute. A review verdict of refuted or published sets that state.

## When a stage stops

It prints the job and its `out.txt`. A model that wrote no file or broken JSON: rerun the same command. A crashing test
script (`tests/<theory>/p<k>.out.txt`): delete `tests/<theory>/` once for fresh scripts. Never edit a recipe or a
script. A recipe that is not computable stays not computable.

## Posting

- Every survivor as an `idea`: statement, its computed tests (measured, interval, readers, gain), total gain, strikes,
  the review's nearest published claim, and its GPU predictions with intervals, posted before those experiments run.
  Then the GPU experiment where survivors differ most per GPU minute, naming the theories it separates.
- Every refuted theory of the round in one `knowledge` item: statement, the test that refuted it and the measured
  number. A wrong prediction is a result.
- Before each round, score the open GPU predictions of earlier rounds in `studies/theory/README.md` against the board.

## Recording

`$R/run.json`: commit, cutoff, counts (items, mechanisms, abandoned, theories, offline predictions, computed, not
computable), jobs per stage, the temp folder. `$R/examples.json`: one computed test inside its interval and one
outside, with script path and readers. One row per theory in `studies/theory/README.md` (statement, tests computed,
in/out, gain, state, verdict, GPU predictions) in the same commit. Close the `work` item with `done`:
`theory round <nn>: <s> of <m> theories survive; <c> of <o> offline predictions computed, <i> inside, <x> outside;
<r> refuted. $R/metrics_v4.json`

## Cost per round

About 45 headless jobs, nearly all opus: 1 inventory, 1 external, 1 mechanisms, 12 developers plus send-backs, 2 test
readers, about 12 test writers (6 at a time), held-out (1 targets, 2 nulls, 1 advocate per survivor), up to 3 reviews.
No GPU. External, developers and test writers take longest (10 to 20 minutes each, in parallel).

## What a round may claim

- A survivor passed its own tests once. Say how many predictions were computed and the total gain every time.
- A refuted theory is refuted by the measured number, not by a model's opinion.
- The held-out items enter `before.jsonl` of the next round: a theory is tested on them once.
