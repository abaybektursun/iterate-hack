---
name: theory
description: Build theories that connect the team's experiments, and test each on stored per-problem rows instead of by opinion. One round runs studies/theory/lib/round.py - headless Claude runs in empty directories propose pairwise different mechanisms from the board items before a cutoff and develop each into a theory with offline predictions; scripts written before any number is seen compute those predictions from the stored rows, against two no-theory readers; each survivor then meets the strongest rival a fresh agent can write, on tests the rival chooses, scored by the same log gain; held-out board numbers and a review can only remove a survivor; survivors are posted with their duel result and GPU predictions before the experiments run, refuted theories as a result. Use when the user asks for a theory, an explanation across experiments or what the results mean together, and after every fifth closed result. Writes studies/theory/results/engine/round-<nn>/ and updates studies/theory/README.md.
---

# Theory round (version 5.1)

A theory is one mechanism sentence that explains numbers from the board and predicts numbers nobody has computed.
A theory survives when its own offline predictions, fixed before any row was read, were computed, none met its
refuting condition, and together they gained probability against readers with no theory. It then meets its
strongest rival on tests the rival chose. Held-out claims and the review can only remove it. GPU predictions
measured later are the strongest evidence and are posted first.

## What four rounds showed

- Rounds 01-02: helping a predictor on held-out targets did not separate theories from a reversed control; git
  commit subjects leaked held-out results into subagents.
- Round 03: theories lost to the no-theory readers where they diverged (15 of 21), and 10 theories were 2 mechanisms.
- Round 04 (version 4, tests on stored rows): 3 of 10 theories survive, 4 are refuted by their own computed
  predictions, 3 are untested because the test environment lacked the grader's packages (math-verify, sympy's LaTeX
  parser). Every review said "weak" and named a rival mechanism that nobody had computed.
- Round 04's duel (version 5): 9 of 9 rival tests computed, 0 separated (the defender's centre lay inside the
  rival's interval on all 9), 1 of 3 survivors decided (r4-m01, +4.43 nats). The rival had attacked its own reading of
  the theory, not the advocate's; so version 5.1 gives it a second turn against the advocate's numbers.

## The coordinator's job

Run the stages, read the tables, decide what to post. Write no mechanism, theory, recipe, claim or target, and edit no
agent's file: you have read the whole board. Work in your own worktree, claim a `work` item, and run
`git pull origin main` first so the inventory sees every committed row file.

## Keeping held-out numbers hidden

- Every model call except `inventory`, `test`, `duel_test` and `review` is a headless `claude -p --restricted` run in
  an empty directory outside the repository, with only Read and Write: no git status, CLAUDE.md, memory or board.
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
| `standing --from $P` | none | `graveyard.json` (every earlier theory, state, verdict, reason), `theories/` (survivors with their tests, untested once), `prior_reviews/` |
| `inventory` | opus, repository | `inventory.md`: row files, exact fetch command, readable now yes/no, fields |
| `external` | opus, papers.py only | `external.md`: 20-30 published mechanisms with their numbers |
| `mechanisms --n-mechanisms 12` | opus | `mechanisms.json`: pairwise different, none restating the graveyard |
| `develop` | opus, 1 per mechanism | `theories/r<n>-m<id>.json` (3+ offline, 1+ GPU predictions), `dropped.json`, `theories.sha256` |
| `null_tests` | opus, 2 jobs | `tests_blind.jsonl`, `predictions/nulltest-{1,2}.jsonl` |
| `test` | opus, repository, laptop only | `tests/<theory>/p<k>.py` written first, run once by the script; `tests/<theory>.json` |
| `score_tests` | none | `metrics_v4.json`, table |
| `heldout` | sonnet, opus | survivors only: `targets.jsonl`, `predictions/null-*.jsonl`, `claims/`, strikes |
| `rival` | opus, 1 per survivor | `rivals/<theory>.json`: the strongest rival, 2-4 tests where the two differ, its predictions (top 3 survivors) |
| `defend` | opus, 1 per survivor | `rivals/<theory>.defend.json`: predictions for the rival's tests from the theory alone |
| `rival2`, `defend` | opus | second turn where fewer than 2 tests separate: `rivals/<theory>.turn2.json` (replacement tests, or `no_offline_test` with one GPU experiment), `.turn2.defend.json` |
| `duel_test` | opus, repository, laptop only | both turns: `rivals/<theory>[.turn2]/p<k>.py` written first, run once; `.tests.json` |
| `score_duel` | none | `metrics_v5.json`, table |
| `review` | opus, repository | `reviews/<theory>.json` for the same survivors; the verdict names the duel state |

`develop` may abandon a mechanism the items already contradict (in `dropped.json`); that is a good outcome. A theory
that fails the check (form, verbatim quotes, recipes) is sent back once, then dropped; any other job whose output
fails its check (broken JSON included) is sent back once with the error, then stops the round. The rival sees the
theory and its computed tests; the defender sees only the theory, the items and the rival's recipes, never the
rival's statement or numbers; the duel test writer sees only the recipes. The rival's second turn gets the
defender's numbers and reasons and attacks the theory as defended; a fresh defender predicts its tests. A test
script runs under `uv run
--no-project --with numpy --with math-verify==0.9.0 --with antlr4-python3-runtime==4.11` with the repository root on
PYTHONPATH, so it imports the team's graders (`studies.rlneurons.lib.rln4_lib`, `grader.repair_v4`). S3 reads use
`AWS_PROFILE=iterate-ecr`. Stages run by name on an existing round, for example
`round.py $R rival defend rival2 defend duel_test score_duel`; `--version 4` runs the old order without the duel. `--model-all
sonnet --min-targets 3 --n-mechanisms 3` runs a cheap smoke test on a hand-made round folder outside `studies/`.

## The score

A prediction (value, low, high) is a normal density with sd = max((high - low) / 3.29, 0.01 * max(|value|, 1)); the
null is the equal mixture of the two test readers' densities. Gain = log prediction density minus log null density
at the computed value, clipped to [-3, 3] nats. States: `refuted` (any refuting condition met, or two computed
predictions outside their intervals), `survives` (2 or more computed, none refuted, total gain above 0), `untested`
(fewer than 2 computed), `no gain` (otherwise). Held-out: a claim both readers contradict that misses its own interval
is a strike; two strikes refute. A review verdict of refuted or published sets that state.

The duel uses the same density and clip: on each computed rival test, gain = log density of the defender's
prediction minus log density of the rival's, at the computed value, over the tests of both turns (first-turn tests
are still computed and printed, marked turn 1). With 2 or more computed: `beats rival` at a total of +2 nats or more,
`loses to rival` at -2 or less, `not separated from rival` between; `not tested against rival` with fewer than 2. Each
test records `same_prediction` (the defender's centre inside the rival's interval). A review may not call a theory
that beats its rival "weak" only because some rival exists.

`standing` carries survivors (state survives, verdict not refuted, published or weak) with their computed tests,
gains, rival files and duel result, which the new round neither computes nor duels again, and carries an `untested`
theory once. Refuted and `no gain` theories go to the graveyard only.

## When a stage stops

It prints the job and its `out.txt` (`out.sendback.txt` after a send-back). A model that wrote no file or broken JSON
twice: rerun the same command. A crashing test script (`tests/<theory>/p<k>.out.txt`, or `rivals/<theory>/` for the
duel): delete that script folder once for fresh scripts. Never edit a recipe or a script. A recipe that is not
computable stays not computable.

## What a round delivers

1. The computed numbers that were new to the team, each with the theory or rival that asked for it and whether the
   no-theory readers expected it. These are the round's most reliable product: post them as `result` items.
2. The surviving mechanisms, each with its rival and the experiment that separates the pair.
3. The refuted theories.

## Posting

- Every survivor as an `idea`: statement, computed tests (measured, interval, readers, gain), strikes, duel state
  and tests (computed value, both predictions, gain), the review's nearest published claim, and its GPU predictions,
  posted before those experiments run. Then the GPU experiment that separates the most pairs per GPU minute.
- A rival that beats or is not separated from its theory is posted as an `idea` too, with its duel tests (a rival
  that beats the theory replaces it, and the theory is listed as refuted by those numbers). This is how the next
  round's `mechanisms` stage sees the rival.
- Every refuted theory of the round in one `knowledge` item: statement, the test that refuted it and the measured
  number. A wrong prediction is a result.
- Before each round, score the open GPU predictions of earlier rounds in `studies/theory/README.md` against the board.

## Recording

`$R/run.json`: commit, cutoff, counts (items, mechanisms, abandoned, theories, offline predictions, computed, not
computable, duel tests computed), jobs per stage, the temp folder. `$R/examples.json`: one computed test inside
its interval and one outside, with script path and readers. One row per theory in `studies/theory/README.md`
(statement, tests computed, in/out, gain, state, duel state, verdict, GPU predictions) in the same commit. Close the `work` item with `done`:
`theory round <nn>: <s> of <m> theories survive; <c> of <o> offline predictions computed, <i> inside, <x> outside;
<r> refuted; <b> beat their rival. $R/metrics_v4.json $R/metrics_v5.json`

## Cost per round

About 55 to 65 headless jobs, nearly all opus: 1 inventory, 1 external, 1 mechanisms, 12 developers, 2 test readers,
about 12 test writers, held-out (1 targets, 2 nulls, 1 advocate per survivor), 3 duel jobs per survivor and 3 more on
a second turn, up to 3 reviews. No GPU. Developers and test writers take 10 to 20 minutes each, in parallel; the duel
adds 15 to 30 minutes.

## What a round may claim

- A survivor passed its own tests once. Say how many predictions were computed and the total gain every time.
- A duel is won against one rival on 2 to 8 tests. Say the rival, the tests computed and how many separated.
- A refuted theory is refuted by the measured number, not by a model's opinion.
- The held-out items enter `before.jsonl` of the next round: a theory is tested on them once.
