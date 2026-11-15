---
name: theory
description: Build theories that connect the team's experiments, test each on stored per-problem rows instead of by opinion, and turn them into the next GPU experiment. One round runs studies/theory/lib/round.py - headless Claude runs in empty directories propose pairwise different mechanisms from the board items before a cutoff and develop each into a theory with offline predictions, GPU predictions and one change to the untrained base it implies; scripts written before any number is seen compute the offline predictions from stored rows, against two no-theory readers; with --with-account, one account budgets the gap between the cued base and RL-Zero-Math into mechanisms whose computed shares add up; each survivor meets the strongest rival a fresh agent can write, scored by the same log gain; each side of a pair then predicts the other side's GPU experiments blind, and the open experiments are ranked by separation per GPU minute and by gain over the best known base count; the top one is posted and run, and its result scores both sides next round. Use when the user asks for a theory, an explanation across experiments or what the results mean together, and after every fifth closed result. Writes studies/theory/results/engine/round-<nn>/ and updates studies/theory/README.md.
---

# Theory round (version 7.1)

A theory is one mechanism sentence that explains numbers from the board, predicts numbers nobody has computed, and
names the change to the untrained base it implies should raise right answers. It survives when its offline
predictions, fixed before any row was read, were computed, none was refuted beyond noise, together they gained
probability against readers with no theory, and one of them won where the readers expected otherwise. It then meets
the strongest rival a fresh agent can write; a rival that beats it takes its place in the next round and faces a
fresh rival in turn.

A round run with `--with-account` also writes one account (`prompts/account.md`): a budget of the gap in right answers between the cued
base and the final RL model, 3 to 6 parts with ordered rules on stored rows plus `unassigned`, so the shares add up by
construction, over 3 or more cells beside a null cell (two base samples). A board item's budget is a claim: fitted,
not scored.

Stored rows test a mechanism only on numbers the team already has; the team wants a change to the untrained base
that reaches the RL model's score. So every theory, account and rival states one `intervention`
(`prompts/intervention.md`): a change to the base only (prompt, sampling, decoding, selection; no training, no RL
weights or directions from them) in one cell of the team's chart, its predicted count of right answers, the best
base-only count known for that set (with the item id), GPU minutes and why; or `null` with a reason, printed.

## What the rounds showed

- Rounds 01-03: held-out targets did not separate theories from a reversed control; commit subjects leaked results.
  Round 04: duels separated 0 of 9 tests on the first turn. Account runs 01-02 gave the span, null and claim rules.
- Round 05 and account run 03: numbers computed, replicated and duelled, but every review said weak, refuted or
  partly published, and nothing led to a new experiment. Hence version 7's interventions and cross-predictions.
- Round 06 (version 6.3): the account took 68 of 125 minutes and lost to a one-axis rival again; duels were decided
  by one separating test; a decisive n counted 401 rows for a claim about 22. Hence version 7.1's changes below.

## The coordinator's job

Run the stages, read the tables, decide what to post, run the top experiment. Write no mechanism, theory, recipe,
claim or target and edit no agent's file: you have read the whole board. Work in your own worktree and
`git pull origin main` first.

## Keeping held-out numbers hidden

- Every model call except `inventory`, `test`, `duel_test` and `review` is a headless `claude -p --restricted` run in
  an empty directory outside the repository, with only Read and Write: no git status, CLAUDE.md, memory or board.
- `external` may also run `lib/papers.py` (paper entries only); its findings state mechanisms, not team numbers.
- `inventory.md` holds no result number: read it before `mechanisms` and delete any line with an accuracy.
- `standing` stops if the previous round's held-out items are not all before the new cutoff. Its `facts.json` (every
  number computed so far, cumulative) goes to every agent as known: no prediction or rival test may ask for one.
- When a held-out number reaches an agent another way, list its item in `<round>/exposed.json`.

## Choosing the cutoff

The cutoff is the posting time of the oldest result or knowledge item no earlier round held out, after every item
of the previous round's `after.jsonl` (`uv run tools/board.py ls result knowledge --new --n 40`).

## The commands

`R=studies/theory/results/engine/round-<nn>` (next free number), `P=` the previous round's folder.

```
uv run studies/theory/lib/round.py $R all --cutoff <ISO time> --skip gpuprice --from $P
```

runs every stage in order except the account (7.1: add `--with-account` to run the account job and to test, duel,
replicate and review accounts, new or carried); a job whose outputs exist is skipped, so the same command resumes a stopped round. `split`
stops if the folder exists, so to reuse files (`external.md`; `inventory.md` at the same cutoff) run `split` first,
copy them in, then `all`. Job dirs (prompt.txt, out.txt) are under a printed temp folder. Prompts: `lib/prompts/<stage>.md`.

| stage | model | writes |
|---|---|---|
| `split --cutoff T --skip W` | none | `before.jsonl`, `after.jsonl` |
| `standing --from $P` | none | `graveyard.json`, `theories/` (survivors with their tests, untested once, `<theory>-rival` for each rival that won), `prior_reviews/`, `facts.json`, `incumbent_account.json`, `gpu_tests.json` (see The score) |
| `inventory` | opus, repository | `inventory.md`: row files, fetch command, readable now, rows, problems and samples per problem counted from the file, fields |
| `external` | opus, papers.py only | `external.md`: 20-30 published mechanisms with their numbers |
| `mechanisms --n-mechanisms 12` | opus | `mechanisms.json`: pairwise different, none restating the graveyard or a theory that lost its duel. 7.1: each names in `holds_against` the two items, facts or graveyard theories nearest to contradicting it and why it holds; at least half are about the gap between the cued base and RL-Zero-Math at T 1.0 / top-p 1.0 and give a `base_change` (base alone, same tokens) |
| `develop` | opus, 1 per mechanism | `theories/r<n>-m<id>.json` (3+ offline, 1+ GPU predictions, an intervention), `dropped.json`, `theories.sha256` |
| `account` | opus, 1 job; 7.1: only with `--with-account` | `theories/r<n>-account.json`: cells (one null), parts with ordered rules, evidence, shares per cell with `vs_null`, fits for claimed cells, a net count per cell, 2+ cross-predictions, 1 GPU prediction, an intervention |
| `null_tests` | opus, 2 jobs | `tests_blind.jsonl`, `predictions/nulltest-{1,2}.jsonl` |
| `test` | opus, repository, laptop only | `tests/<theory>/p<k>.py` written first, run once by the script; `tests/<theory>.json`. 7.1: `n` is the size of the smallest group the number depends on; a script that contrasts groups prints each group's size (same rule for duel and replication scripts) |
| `score_tests` | none | `metrics_v4.json`, table, a round total line. 7.1: a promoted `<theory>-rival`'s carried duel tests are not offline tests: its entry shows `carried_duel` (gain, tests) and 0 computed, kept out of the round's totals |
| `replicate` | opus, repository, laptop only | after `score_tests` and after `score_duel`: every decisive number recomputed from its recipe alone, `replication/<theory>[.duel].json`; one that differs is left out until a person resolves it. 7.1: when both the first script and the replication meet the refuting condition, they agree, and the prediction stays in the score as refuted |
| `heldout` | sonnet, opus | survivors only: `targets.jsonl`, `predictions/null-*.jsonl`, `claims/`, strikes |
| `rival` | opus, 1 per survivor | `rivals/<theory>.json`: the strongest rival, 2-4 tests where the two differ, its predictions, its intervention (top 3 survivors) |
| `defend` | opus, 1 per survivor | `rivals/<theory>.defend.json`: predictions for the rival's tests from the theory alone |
| `rival2`, `defend` | opus | second turn where fewer than 2 tests separate: `rivals/<theory>.turn2.json` (replacement tests, or `no_offline_test` with one GPU experiment), `.turn2.defend.json` |
| `duel_test` | opus, repository, laptop only | both turns: `rivals/<theory>[.turn2]/p<k>.py` written first, run once; `.tests.json` |
| `score_duel` | none | `metrics_v5.json`, table. 7.1: a `same` test adds 0 and prints as not separating; deciding needs 2 separating computed tests |
| `cross_predict` | opus, 2 per pair, blind | `experiments/<theory>.json`: for every theory with a rival file (any duel state; the account too; a carried pair keeps its file), each side predicts the other side's GPU predictions and intervention (value, low, high, why) from its own mechanism, without the other's statement or numbers. A side with no intervention (a folder before version 7) writes one in the same job; the other side predicts it in a second job |
| `review` | opus, repository | `reviews/<theory>.json` for the same survivors and for the account (with `--with-account`) whatever its state; names the duel state; about the rival when it won. 7.1: "stands" needs 2 or more separating duel tests won, the smallest n among them 50 or more; otherwise at most "weak" |
| `experiments` | none | `experiments.json`, `experiments.md`: every open experiment ranked (a) by separation per GPU minute, (b) interventions by gain over best; each entry has the setting to run and both predictions |

A theory failing its check is sent back once, then dropped; any other failing job is sent back once, then stops
the round. The rival sees the theory and its computed tests; the defender sees only the theory, the items and the
rival's recipes; the duel test writer only the recipes. Test scripts run in the graders' environment (`TEST_PYTHON`
in round.py) and print through `lib/noise.py`: the number, n and a 90 % bootstrap interval over problems, or a
binomial interval or none for a single count. S3 reads use `AWS_PROFILE=iterate-ecr`. Stages run by name on an
existing folder (`round.py $R cross_predict experiments` on an earlier version's folder writes only `experiments/`,
`experiments.json`, `experiments.md`). A folder not named `round-<nn>` is the round after `--from`. `--only-account`
tests and duels only the account and implies `--with-account`; `--account-from <folder>` adds another chain's accounts to its inputs; `--version 6`
runs without interventions; `--model-all sonnet --min-targets 3 --n-mechanisms 3` smoke-tests a folder outside `studies/`.

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
prediction minus log density of the rival's, at the computed value, over the tests of both turns. With 2 or more
computed: `not tested against rival` with fewer than 2. A test with `same_prediction` (the defender's centre inside
the rival's interval) is not separating and adds 0 to the total (7.1); `separating` counts the others. `beats rival`
needs 2 or more separating computed tests and a total of +2 nats or more, `loses to rival` the same and -2 or less;
otherwise `not separated from rival`. A review may not call a theory that beats its rival "weak" only because some rival exists.

An open experiment's `separation` is the proposer's log gain over the other side if the proposer's value is
measured, by the same density and clip; `gain_over_best` (interventions) is the predicted count minus the best known
base-only count. A measured experiment is scored by `standing` for both sides by the duel rule (each side's log
density minus the other's at the measured value) into `gpu_tests.json` (cumulative), `facts.json` (kind `gpu`) and
the table (`GPU test`, kept out of the offline total). A side whose measured value lies outside its interval, and
outside the measured 90 % interval when one is given, gets a strike; two strikes send it to the graveyard (`refuted
by GPU tests`), and a rival with two is not promoted.

`standing` carries survivors (verdict not refuted, published or weak) with their tests, rival files, experiments and
duel result, none computed again, and an `untested` theory once. A theory that `loses to rival` goes to the
graveyard and its rival enters as `<theory>-rival`, its duel tests as its record, to meet a fresh rival. That record
is reported as `carried_duel` ("carried duel win, +8.77 nats over 3 tests"), never as predictions computed or inside.

## When a stage stops

It prints the job and its `out.txt` (`out.sendback.txt` after a send-back); rerun the same command. A crashing test
script: delete its script folder once for fresh scripts. Never edit a recipe or a script; not computable stays so.

## What a round delivers

1. The computed numbers new to the team, each with who asked for it and whether the readers expected it (`result`).
2. `experiments.md`: open experiments by separation per GPU minute and changes to the base by gain over the best
   known base count, both sides' predictions beside each; the top entries are the next experiments.
3. The surviving mechanisms, each with its rival. 4. The refuted theories.

## Posting

- The top entry of each list in `experiments.md` as an `idea` with its setting and both predictions, before anyone
  runs it. Run the top experiment when it costs at most 30 GPU minutes (the AWS PG tool of the parent repository
  first, then vast.ai, never the laptop), add it to this round's `experiments_measured.json` (a list of {id,
  measured, n, interval or null, artifact, item}) and post it as a `result`; the next `standing` scores both sides.
- Every survivor as an `idea`: statement, computed tests (measured, interval, readers, gain), strikes, duel state
  and tests (computed value, both predictions, gain), the review's nearest published claim, its GPU predictions.
- A rival that beats or is not separated from its theory is posted as an `idea` too, with its duel tests and the
  review of it; the next round's `mechanisms` stage sees it there, and `standing` promotes a winner.
- Every refuted theory in one `knowledge` item: statement, refuting test, measured number. A wrong prediction is a result.

## Recording

`$R/run.json`: commit, cutoff, counts (items, mechanisms, abandoned, theories, offline predictions, computed, not
computable, duel tests computed), jobs per stage, the temp folder. `$R/examples.json`: one computed test inside
its interval and one outside, with script path and readers. One row per theory in `studies/theory/README.md`
(statement, tests computed, in/noise/out, gain, state, duel state, verdict, GPU predictions) in the same commit. For an
entry with `carried_duel`, write "carried duel win, +<gain> nats over <n> tests" in place of tests computed and gain.
Close the `work` item: `theory round <nn>: <s> of <m> survive; <c> of <o> computed, <i> inside, <x> outside; <r>
refuted; <b> beat their rival. $R/metrics_v4.json $R/metrics_v5.json $R/experiments.md`

## Cost per round

65 to 80 headless jobs, nearly all opus, about 1.5 hours: 12 developers, about 13 test writers and as many
replicators, 3 to 6 duel jobs and 2 cross_predict jobs per pair, the rest single jobs. No GPU in the round; the top
experiment after it takes up to 30 GPU minutes.

## What a round may claim

- A number is posted only when `replicate` reproduced it (within 1 %, or 0.005).
- A survivor passed its own tests once. Say the predictions computed, the total gain and the unexpected wins.
- An account's measured shares are a result whatever its state: report each with n, interval and its rule.
- A duel is won against one rival on 2 or more separating tests. Say the rival, the tests computed and how many separated.
- An experiment's two predictions were fixed before it ran; its result scores both sides once.
- A refuted theory is refuted by the measured number, not by a model's opinion. Held-out items enter the next
  round's `before.jsonl`: a theory is tested on them once.
