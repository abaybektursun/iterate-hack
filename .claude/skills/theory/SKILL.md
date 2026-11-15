---
name: theory
description: Build theories that connect the team's experiments, and test each on stored per-problem rows instead of by opinion. One round runs studies/theory/lib/round.py - headless Claude runs in empty directories propose pairwise different mechanisms from the board items before a cutoff and develop each into a theory with offline predictions; scripts written before any number is seen compute those predictions from the stored rows, against two no-theory readers; one account per round budgets the whole gap between the cued base and RL-Zero-Math into mechanisms whose computed shares add up; each survivor then meets the strongest rival a fresh agent can write, on tests the rival chooses, scored by the same log gain; held-out board numbers and a review can only remove a survivor; survivors are posted with their duel result and GPU predictions before the experiments run, refuted theories as a result. Use when the user asks for a theory, an explanation across experiments or what the results mean together, and after every fifth closed result. Writes studies/theory/results/engine/round-<nn>/ and updates studies/theory/README.md.
---

# Theory round (version 6.2)

A theory is one mechanism sentence that explains numbers from the board and predicts numbers nobody has computed.
It survives when its offline predictions, fixed before any row was read, were computed, none was refuted beyond
noise, together they gained probability against readers with no theory, and one of them won where the readers
expected otherwise. It then meets the strongest rival a fresh agent can write; a rival that beats it takes its
place in the next round and faces a fresh rival in turn. A mechanism stays only while no fresh agent can write a
rival that beats it on stored rows.

Each round also writes one account: the round's overarching theory of the team's question, how the gap in right
answers between the cued base and the final RL model is made up. It is a budget of 3 to 6 parts, each a mechanism
with a rule on stored rows that assigns every gap problem to the first part that takes it, plus `unassigned`, so the
shares add up by construction and a wrong account shows as a measured share. Narrow theories feed it: the carried
theories, the graveyard and every computed number are its inputs, and the previous account is the one to improve.
One list of parts spans 3 or more cells that differ in two of problem set, sampling and model pair, beside a null
cell (the base against an independent base sample): each share is stated also as its difference from the null, and
every gap gross and net. A board item's budget is a claim (`known_claim`): the account's own rules are fitted to that
cell and not scored; one evidence set serves every cell; a share 0 by construction is neither scored nor counted.

## What the rounds showed

- Rounds 01-03: held-out targets did not separate theories from a reversed control; commit subjects leaked results.
- Round 04: 3 of 10 theories survive, 4 refuted by their own computed predictions (two within noise), 3 untested
  (grader packages missing). Duel, first turn: 0 of 9 tests separated; second turn: r4-m10 lost both separating tests
  (mean_logprob, -7.81 nats in all), r4-m08 lost (-2.65), r4-m01 not separated (+1.11). Every theory was narrow.
- Account runs: run 01 restated the one budget the board tabulates (no gain, -1.30 nats), hence the span rule. Run 02
  (20 of 20 computed, refuted by one share) was reproduced by hand, which found the faults the null cell, the claim
  rule, the single evidence set and the by-construction rule now prevent.

## The coordinator's job

Run the stages, read the tables, decide what to post. Write no mechanism, theory, recipe, claim or target and edit no
agent's file: you have read the whole board. Work in your own worktree and `git pull origin main` first.

## Keeping held-out numbers hidden

- Every model call except `inventory`, `test`, `duel_test` and `review` is a headless `claude -p --restricted` run in
  an empty directory outside the repository, with only Read and Write: no git status, CLAUDE.md, memory or board.
- `external` may also run `lib/papers.py` (paper entries only); its findings state mechanisms, not team numbers.
- `inventory.md` holds no result number: read it before `mechanisms` and delete any line with an accuracy.
- `standing` stops if the previous round's held-out items are not all before the new cutoff.
- When a held-out number reaches an agent another way, list its item in `<round>/exposed.json`.

## Choosing the cutoff

The cutoff is the posting time of the oldest result or knowledge item no earlier round held out, after every item
of the previous round's `after.jsonl` (`uv run tools/board.py ls result knowledge --new --n 40`).

## The commands

`R=studies/theory/results/engine/round-<nn>` (next free number), `P=` the previous round's folder.

```
uv run studies/theory/lib/round.py $R all --cutoff <ISO time> --skip gpuprice --from $P
```

runs every stage in order; a job whose outputs exist is skipped, so the same command resumes a stopped round. `split`
stops if the folder exists, so to reuse files (`external.md`; `inventory.md` at the same cutoff) run `split` first,
copy them in, then `all`. Job dirs (prompt.txt, out.txt) are under a printed temp folder. Prompts: `studies/theory/lib/prompts/<stage>.md`.

| stage | model | writes |
|---|---|---|
| `split --cutoff T --skip W` | none | `before.jsonl`, `after.jsonl` |
| `standing --from $P` | none | `graveyard.json`, `theories/` (survivors with their tests, untested once, `<theory>-rival` for each rival that won), `prior_reviews/`, `facts.json` (the previous round's computed numbers), `incumbent_account.json` |
| `inventory` | opus, repository | `inventory.md`: row files, fetch command, readable now, rows, problems and samples per problem counted from the file, fields |
| `external` | opus, papers.py only | `external.md`: 20-30 published mechanisms with their numbers |
| `mechanisms --n-mechanisms 12` | opus | `mechanisms.json`: pairwise different, none restating the graveyard |
| `develop` | opus, 1 per mechanism | `theories/r<n>-m<id>.json` (3+ offline, 1+ GPU predictions), `dropped.json`, `theories.sha256` |
| `account` | opus, 1 job | `theories/r<n>-account.json`: cells (one null), parts with ordered rules, evidence, shares per cell with `vs_null`, fits for claimed cells, a net count per cell, 2+ cross-predictions, 1 GPU prediction; same check and send-back |
| `null_tests` | opus, 2 jobs | `tests_blind.jsonl`, `predictions/nulltest-{1,2}.jsonl` |
| `test` | opus, repository, laptop only | `tests/<theory>/p<k>.py` written first, run once by the script; `tests/<theory>.json` |
| `score_tests` | none | `metrics_v4.json`, table |
| `replicate` | opus, repository, laptop only | after `score_tests` and after `score_duel`: every decisive number recomputed from its recipe alone, `replication/<theory>[.duel].json`; one that differs is left out until a person resolves it |
| `heldout` | sonnet, opus | survivors only: `targets.jsonl`, `predictions/null-*.jsonl`, `claims/`, strikes |
| `rival` | opus, 1 per survivor | `rivals/<theory>.json`: the strongest rival, 2-4 tests where the two differ, its predictions (top 3 survivors) |
| `defend` | opus, 1 per survivor | `rivals/<theory>.defend.json`: predictions for the rival's tests from the theory alone |
| `rival2`, `defend` | opus | second turn where fewer than 2 tests separate: `rivals/<theory>.turn2.json` (replacement tests, or `no_offline_test` with one GPU experiment), `.turn2.defend.json` |
| `duel_test` | opus, repository, laptop only | both turns: `rivals/<theory>[.turn2]/p<k>.py` written first, run once; `.tests.json` |
| `score_duel` | none | `metrics_v5.json`, table |
| `review` | opus, repository | `reviews/<theory>.json` for the same survivors and for the account whatever its state; names the duel state; about the rival when it won |

`develop` may abandon a contradicted mechanism (`dropped.json`). A theory failing the check is sent back once, then
dropped; any other job whose output fails its check is sent back once, then stops the round. The rival sees the
theory and its computed tests; the defender sees only the theory, the items and the rival's recipes, never the
rival's statement or numbers; the duel test writer sees only the recipes. The rival's second turn gets the
defender's numbers and reasons and attacks the theory as defended; a fresh defender predicts its tests. Test
scripts run under `uv run --no-project --with numpy --with math-verify==0.9.0 --with antlr4-python3-runtime==4.11`,
root on PYTHONPATH, import the team's graders, and print through `lib/noise.py`: the number, n and a 90 % bootstrap
interval over problems (2,000 resamples, seed 0), or a binomial interval or none for a single count. S3 reads use
`AWS_PROFILE=iterate-ecr`. Stages run by name on an existing round (`round.py $R rival2 defend duel_test
score_duel`). `--only-account` skips `mechanisms` and `develop` and tests and duels only the account; a folder not
named `round-<nn>` is the round after `--from`, given with every command. `--version 5` runs without the account;
`--model-all sonnet --min-targets 3 --n-mechanisms 3` runs a smoke test on a hand-made folder outside `studies/`.

## The score

A prediction (value, low, high) is a normal density with sd = max((high - low) / 3.29, 0.01 * max(|value|, 1)); the
null is the equal mixture of the two test readers' densities. Gain = log prediction density minus log null density
at the computed value, clipped to [-3, 3] nats. A value outside its interval counts as `outside` (and a refuting
condition as met) only when the measured 90 % interval misses the predicted one; otherwise it prints `outside,
within noise`. States: `refuted` (a refuting condition met, or two predictions outside), `survives` (2 or more
computed, total gain above 0, and one prediction inside its interval while both readers' centres lie outside it),
`untested` (fewer than 2 computed), `no gain` (otherwise; the table says why). Two held-out strikes (claims both
readers contradict that miss their interval) refute. A review verdict of refuted or published sets that state.

The duel uses the same density and clip: on each computed rival test, gain = log density of the defender's
prediction minus log density of the rival's, at the computed value, over the tests of both turns (first-turn tests
are still computed and printed, marked turn 1). With 2 or more computed: `beats rival` at a total of +2 nats or more,
`loses to rival` at -2 or less, `not separated from rival` between; `not tested against rival` with fewer than 2. Each
test records `same_prediction` (the defender's centre inside the rival's interval). A review may not call a theory
that beats its rival "weak" only because some rival exists.

`standing` carries survivors (state survives, verdict not refuted, published or weak) with their tests, gains,
rival files and duel result, which the new round neither computes nor duels again, and an `untested` theory once. A
theory that `loses to rival` goes to the graveyard ("lost to its rival", with the decisive tests), and its rival
enters as `<theory>-rival`: its duel tests are its computed record (the defeated theory as reader), it skips
`develop`, `null_tests` and `test`, and meets a fresh rival. Refuted and `no gain` theories go to the graveyard only.

## When a stage stops

It prints the job and its `out.txt` (`out.sendback.txt` after a send-back); rerun the same command. A crashing test
script: delete its script folder once for fresh scripts. Never edit a recipe or a script; not computable stays so.

## What a round delivers

1. The computed numbers that were new to the team, each with the theory or rival that asked for it and whether the
   no-theory readers expected it. These are the round's most reliable product: post them as `result` items.
2. The surviving mechanisms, each with its rival and the experiment that separates the pair; 3. the refuted theories.

## Posting

- Every survivor as an `idea`: statement, computed tests (measured, interval, readers, gain), strikes, duel state
  and tests (computed value, both predictions, gain), the review's nearest published claim, and its GPU predictions,
  posted before those experiments run. Then the GPU experiment that separates the most pairs per GPU minute.
- A rival that beats or is not separated from its theory is posted as an `idea` too, with its duel tests and the
  review of it; the next round's `mechanisms` stage sees it there, and `standing` promotes a winner.
- Every refuted theory in one `knowledge` item: statement, refuting test, measured number. A wrong prediction is a result.
- Before each round, score the open GPU predictions of earlier rounds in `studies/theory/README.md` against the board.

## Recording

`$R/run.json`: commit, cutoff, counts (items, mechanisms, abandoned, theories, offline predictions, computed, not
computable, duel tests computed), jobs per stage, the temp folder. `$R/examples.json`: one computed test inside
its interval and one outside, with script path and readers. One row per theory in `studies/theory/README.md`
(statement, tests computed, in/noise/out, gain, state, duel state, verdict, GPU predictions) in the same commit.
Close the `work` item: `theory round <nn>: <s> of <m> survive; <c> of <o> computed, <i> inside, <x> outside; <r>
refuted; <b> beat their rival. $R/metrics_v4.json $R/metrics_v5.json`

## Cost per round

60 to 70 headless jobs, nearly all opus: inventory, external, mechanisms, 12 developers, 1 account, 2 test readers,
about 13 test writers and as many replicators, held-out, 3 to 6 duel jobs per survivor, up to 4 reviews. No GPU.
About 1.5 hours; developers and test writers take 10 to 20 minutes each, in parallel.

## What a round may claim

- A number is posted only when `replicate` reproduced it (within 1 %, or 0.005).
- A survivor passed its own tests once. Say the predictions computed, the total gain and the unexpected wins.
- An account's measured shares are a result whatever its state: report each with n, interval and its rule.
- A duel is won against one rival on 2 to 8 tests. Say the rival, the tests computed and how many separated.
- A refuted theory is refuted by the measured number, not by a model's opinion. Held-out items enter the next
  round's `before.jsonl`: a theory is tested on them once.
