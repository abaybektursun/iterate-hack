# Account run 01 (version 6): one account of the whole gap, with parts that add up

Written before the run (2026-11-15). Code: `lib/round.py` with the stage `account` (commit named in the run's
`run.json`). Folder: `results/account/run-01/`. Evidence: board items before 2026-11-15T04:29:33, the theories and
computed numbers of rounds 01 to 04 (`--from results/engine/round-04`).

## Why

Four rounds gave narrow theories: each explains one phenomenon (loops, cap hits over checkpoints, recall). The request
was for overarching theories built from all experiments. The team's question is a quantity: how the gap in right
answers between the cued Olmo 3 base and RL-Zero-Math is made up, and how much of it needs no training. An account of
that gap can be wrong in a way a narrow theory cannot: its parts must add up to the measured gap on stored rows.

## What runs

One blind agent (headless, empty directory) gets the items before the cutoff, every failed theory with the test that
decided it, the carried theories with their computed tests, the computed numbers of earlier rounds, the inventory of
stored rows and the external findings. It writes one account: 3 to 6 parts, each a mechanism with a rule computable
from stored rows that assigns every gap problem to exactly one part, plus an unassigned part. It predicts each part's
share and at least 2 further numbers the account implies and a different budget would get wrong. Then the usual
stages: two readers with no theory predict the same quantities; scripts written before any row is read compute them,
with n and a bootstrap interval; a rival agent writes a different budget and separating tests (two turns); a review
searches the board and the literature.

## Hypotheses

- A1 (computable): at least three quarters of the account's offline predictions return a number. Refuted below.
- A2 (the shares are right): the account survives its own tests by the version-5.2 rule (2 or more computed, none
  outside beyond noise twice, total gain above 0, one win the readers did not expect). I expect this to fail: shares
  are hard to guess and no earlier theory had to state them. If it fails, the measured shares are still the result.
- A3 (holds against a different budget): the rival does not beat it (total above -2 nats).
- A4 (tells the team where to work): the measured shares name at least one part of 10 % of the gap or more for which
  the board holds no base-only intervention result. Checked by the review against the board. Refuted if every part
  of that size already has one, or if the unassigned part is above half.

## What is reported whatever the outcome

The measured share of each part with n and interval, the rule that produced it, and the script path: a budget of the
gap computed by rules fixed before the rows were read.

## Known limits

- One account from one agent. The next round's account job gets this one as the incumbent to improve.
- The rules assign problems, so a problem with two causes goes to the first rule that takes it; the order is part of
  the account and the rival may attack it.
- Single samples per problem in most cells: a problem's side of the gap is partly sampling noise. The scripts print
  intervals; shares are read with them.
