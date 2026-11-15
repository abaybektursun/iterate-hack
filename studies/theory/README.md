# theory

Question: which theories connect the team's experiments, measured by how well they predict results they have not seen?

A round is run with the `theory` skill (`.claude/skills/theory/SKILL.md`), which holds the procedure. Subagents propose
theories from the board items before a cutoff time. Rounds 01-03 scored each theory by how much it improves a predictor's
guesses of the numbers posted after the cutoff, against the same predictor without the theory. From round 04 the main score
is the theory's own offline predictions, computed from stored per-problem rows, against two no-theory readers' predictions of
the same numbers; the numbers posted after the cutoff can only remove a survivor.

## Files

| Path | What |
|---|---|
| `specs/SPEC_round02.md` | Plan of round 02, written before the run: the new score, the reversal control, hypotheses H1-H3. |
| `lib/check.py` | The mechanical steps: `dump` splits the board at the cutoff, `check` verifies every quote against its board item, `score` compares each theory's predictions with the two no-theory predictors (round 01's score). Usage in its docstring. |
| `lib/v2.py` | Round 02's check and score: each theory's own claims, divergent wins and losses against the two no-theory agents, the reversal control, targets of `exposed.json` left out. Writes `metrics_v2.json`. Usage in its docstring. |
| `results/engine/round-<nn>/` | One round: `run.json`, `before.jsonl`, `after.jsonl`, `targets.jsonl`, `targets_blind.jsonl` (targets without values), `theories/`, `predictions/`, `examples.json`; round 01 also `metrics.json` and `predictions_measured.json`. |
| `results/engine/round-02/` (new files) | `external.md` (25 published findings, by mechanism), `theories.sha256` (theory files fixed before the claims), `claims/<theory>.jsonl` (each author's value and interval per target; `.rev.jsonl` the reversal's), `reversed/` (the reversed theories), `reviews/` (refutation search, novelty, verdict), `exposed.json` (items left out of the score and why), `metrics_v2.json`. |
| `specs/SPEC_round03.md` | Plan of round 03, written before the run: version 3 on held-out items no earlier round used, hypotheses H1-H4. |
| `lib/round.py` | Runs a whole round, stage by stage. Version 3 (round 03): `split`, `standing`, `inventory`, `targets`, `external`, `generate`, `null`, `claims`, `score`, `reverse`, `test`, `review`; writes `metrics_v3.json`. Version 4 (commit bb43116, round 04): `split`, `standing`, `inventory`, `external`, `mechanisms`, `develop`, `null_tests`, `test`, `score_tests`, `heldout`, `review`; writes `metrics_v4.json`; `--version 3` keeps the old order. Every model call except inventory, test and review is a headless Claude run in an empty directory with Read and Write only. Log-gain score with bootstrap interval. Usage in its docstring. |
| `lib/papers.py` | Paper-only access for the `external` stage: `tools/recall.py` entries whose sources are all papers or web pages, and `tools/exa.py` search and fetch. |
| `lib/prompts/` | One prompt per stage (`inventory.md`, `targets.md`, `external.md`, `generate.md`, `fix.md`, `null.md`, `claims.md`, `reverse.md`, `test.md`, `review.md`; version 4 adds `mechanisms.md`, `develop.md`, `null_tests.md`). |
| `results/engine/round-03/` (new files) | `inventory.md` (stored per-problem row files, how to fetch them, their fields; no result numbers), `prior_scores.json` and `prior_reviews/` (round 02's scores and reviews of the carried theories), `external_<start>.md` (each generator's part of `external.md`), `drafts/` (theories before the checks), `dropped.json`, `tests/<theory>/p<k>.py` and `.out.txt` (offline test scripts and their output) and `tests/<theory>.json`, `metrics_v3.json`, `diagnosis.md` (why theories lose, what the tests needed, the hypotheses). |
| `specs/SPEC_round04.md` | Plan of round 04, written before the run: version 4, computed offline tests as the main test, hypotheses H1-H4. |
| `results/engine/round-04/` (new files) | `graveyard.json` (the 32 earlier theories and why each failed), `mechanisms.json` (12 candidate mechanisms), `dropped.json` (2 abandoned), `tests_blind.jsonl` (the 42 offline recipes without values) and `predictions/nulltest-{1,2}.jsonl` (the two no-theory readers' predictions of them), `tests/`, `metrics_v4.json`, `replication/` (independent recomputation of 7 predictions: scripts, outputs, `replication.json`), `board_posts.md` (drafts), `diagnosis.md`; from the rival stages (plan `specs/SPEC_round04_duel.md`): `rivals/` (per survivor the rival and its tests, the defender's predictions, scripts and outputs; `<theory>.turn2*` the second turn), `metrics_v5.json` (both turns), `duel.md`, `replication/replication_turn2.json`. |
| `lib/round.py` version 6 and 6.1 | Version 6 (commit b7f1ae2) adds the stage `account` after `develop` (prompt `lib/prompts/account.md`): one blind job writes `theories/r<N>-account.json`, a budget of the base-to-RL gap with ordered rules per part, tested and duelled like a theory; `--only-account` skips `mechanisms` and `develop`. Version 6.1 (commit 856971b): the account spans at least 3 cells, and budgets already on the board are input (`known`). |
| `specs/SPEC_account01.md`, `specs/SPEC_account02.md` | Plans of account runs 01 and 02, written before each run: hypotheses A1-A4 and B1-B4. |
| `results/account/run-<nn>/` | One account run: the round files (`before.jsonl`, `after.jsonl`, `inventory.md`, `external.md`, `graveyard.json`, `facts.json`, `incumbent_account.json`, `theories/`, `tests_blind.jsonl`, `predictions/`, `tests/`, `metrics_v4.json`) and `run.json`; run 02 also `check/` (independent recomputation, equal-E version, null cell, raw-text reads), `readout.md`, `examples.json`, `board_posts.md`. |

## Round 01 (2026-11-15, cutoff 11-14 23:42 UTC)

`results/engine/round-01/`. 60 board items before the cutoff, 21 held out, 58 targets from 13 held-out items, 6 theories
from 3 generators, 1 planted theory (`all-1` with every effect reversed), 9 predictors. 14 subagents.

**Result: no theory beat the null, and the backtest did not discriminate.** Noise (null-1 against null-2) is 3. The planted
theory scored like the real ones (`metrics.json`):

| Theory | closer, farther vs null-1 | vs null-2 | Beats the null |
|---|---|---|---|
| all-1 | 24, 17 | 18, 15 | no |
| across-1 | 21, 14 | 19, 17 | no |
| across-2 | 23, 17 | 22, 20 | no |
| planted | 22, 14 | 23, 21 | no |
| all-2 | 22, 20 | 18, 21 | no |
| surprises-2 | 15, 22 | 17, 22 | no |
| surprises-1 | 21, 21 | 16, 24 | no |

Cause, read from the predictions: about 16 of the 58 targets (the weight-difference cells of result-9b6af3 and
result-4b0d5f) are numbers a theory speaks about. On the others (GPU repeatability, opener counts, neuron statistics,
Code-pair facts) all nine predictors give nearly the same number and the count is predictor noise. On those 16 targets
alone the planted theory still scores best (9, 1 and 11, 3), so restricting the targets does not repair the count.
Each predictor took about 25 s for 58 numbers. Steps 8 and 9 of the skill were not run for any theory.

**The theories' own predictions that the held-out items had measured** (`predictions_measured.json`; matched by hand
by the coordinator after scoring, not a step of the skill in this round): 5 of 7 inside their interval, and 6 of 7
closer to the measured value than both no-theory predictors. The planted theory has no prediction among them, so
this table has no control yet. A round-01 author later copied its git status lines, and none held a result number
(`round-02/exposed.json`, key `round_01_agents`), so this table was not exposed through commit subjects.

| Theory | Experiment (MATH-500, T 1.0, v3, n=500) | Predicted | Measured | | null-1, null-2 |
|---|---|---|---|---|---|
| all-2 | base + 0.25*(RL - base), plain | 375 [330, 415] | 405 | inside | 300, 300 |
| all-2 | base + 0.5*(RL - base), plain | 432 [415, 450] | 443 | inside | 430, 420 |
| all-2 | base + 0.5*(RL - base), cue minus plain | 3 [-10, 15] | 9 | inside | 20, 25 |
| all-2 | Code-RL, plain | 320 [270, 375] | 390 | outside | 270, 300 |
| across-2 | base + 0.5*(RL - base), cue | 447 [436, 457] | 452 | inside | 450, 445 |
| surprises-1 | Code-RL, plain | 340 [280, 400] | 390 | inside | 270, 300 |
| surprises-1 | Code-RL, cue | 410 [390, 432] | 450 | outside | 400, 400 |

Examples (`examples.json`): all-2's predictor on t49 (measured 405: it said 380, the nulls 300 and 300) and on t48
(base + 1.5*(RL - base), cue, measured 453: it said 400, the nulls 440 and 440).

## Round 02 (2026-11-15, cutoff 11-14 23:42 UTC)

`results/engine/round-02/`, plan `specs/SPEC_round02.md`. Same cutoff as round 01. 60 board items before the cutoff, 25
held out, 68 targets from 15 held-out items. The 7 targets of result-5d032f are left out (`exposed.json`), so 61 targets
are scored. 16 theories: the 6 of round 01 unchanged (`theories/r1-*.json`, byte-identical to round 01's files) and 10
new from 5 generators (all, surprises, across, external, revise; `theories/r2-*.json`), each importing at least one
published mechanism from `external.md` (25 findings). 2 no-theory agents (opus), 5 reversals, 3 reviews. 17 new
subagents plus the 3 round-01 generators resumed (`run.json`).

**Result: 5 of 16 theories pass the new score, each with a net above its reversal's (every reversal's net is -2 or
lower), but each rests on only 2 to 5 divergent claims, and all 3 passers that were reviewed were refuted (r1-all-1) or
judged weak (r2-all-2, r2-across-2)** (`metrics_v2.json`, `reviews/`). A claim is divergent when both no-theory agents'
numbers lie outside its interval. Sorted as `v2.py score` prints them (by net):

| Theory | Claims | Divergent win, loss | Non-divergent inside, outside | State | Reversal win, loss | Review |
|---|---|---|---|---|---|---|
| r2-all-2 | 8 | 2, 0 | 4, 2 | passes | 0, 6 | weak |
| r1-all-1 | 12 | 2, 1 | 3, 6 | passes | 1, 6 | refuted |
| r1-all-2 | 13 | 3, 2 | 3, 5 | passes | 0, 5 | not reviewed |
| r1-surprises-2 | 19 | 3, 2 | 11, 3 | passes | 1, 11 | not reviewed |
| r2-across-2 | 15 | 3, 2 | 5, 5 | passes | 6, 8 | weak |
| r2-revise-1 | 10 | 1, 0 | 3, 6 | fails | | |
| r1-across-1 | 13 | 2, 2 | 5, 4 | fails | | |
| r1-across-2 | 16 | 1, 1 | 9, 5 | fails | | |
| r1-surprises-1 | 8 | 0, 0 | 6, 2 | fails | | |
| r2-across-1 | 6 | 1, 1 | 4, 0 | fails | | |
| r2-external-1 | 5 | 1, 1 | 3, 0 | fails | | |
| r2-revise-2 | 2 | 0, 0 | 0, 2 | fails | | |
| r2-all-1 | 5 | 0, 1 | 2, 2 | fails | | |
| r2-external-2 | 6 | 1, 2 | 2, 1 | fails | | |
| r2-surprises-1 | 4 | 0, 1 | 1, 2 | fails | | |
| r2-surprises-2 | 9 | 0, 1 | 5, 3 | fails | | |

Claims are counted on the 61 scored targets only. Candidate = wins >= 2 and wins > losses; passes = net (wins - losses)
above the reversal's net.

Hypotheses of the spec:

- H1, the new score separates theories: not refuted. 5 candidates, each net above its reversal's (r2-all-2 +2 vs -6,
  r1-all-1 +1 vs -5, r1-all-2 +1 vs -5, r1-surprises-2 +1 vs -10, r2-across-2 +1 vs -2). But a net of +1 or +2 is one or
  two targets, and r2-across-2's reversal scored 6 wins, more than the theory's 3.
- H2, imports yield passing theories whose import carries a win: not refuted by the spec's rule, on one theory only.
  r2-across-2's review says no: its 3 wins come from result-904bbf's additivity, a fitted map and 2404.16792; its import
  2610.37719 drives t37, t38 and t47, none divergent (`reviews/r2-across-2.json`, `import_carries_win`). r2-all-2's review
  says yes: t51 rests on 2512.12895 and t09 on 2007.14966; it adds that without the imports t51 is a sign guess inside
  noise (-1.2 points [-4.6, 2.2]) and t09 follows from a grader format fact with no import (knowledge-499152)
  (`reviews/r2-all-2.json`).
- H3, round-01 all-2 and across-2 are candidates: half refuted. r1-all-2 is a candidate (3 wins, 2 losses) and passes;
  r1-across-2 is not (1 win, 1 loss).

What round 02 showed about the engine:

1. Commit subjects leak results. Claude Code gives every subagent a git status block with the 5 newest commit subjects.
   One subject (d1f0136) held the 7 numbers of result-5d032f, and the nulls and new generators had it in context. The
   r2-all author reported it. Those 7 targets are left out of the score (`exposed.json`, read by `v2.py`). A headless
   run from an empty directory has no such block (tested by the coordinator).
2. The interval rule discards closeness. r1-all-2 claimed 370 [340, 400] for t40, measured 405, nulls 300 and 290: the
   claim was 35 off and the nulls 105 and 115 off, and it counts as a loss.
3. The control is not matched. The author of a theory wrote its claims; a fresh agent wrote its reversal's claims.
4. Round 02's passes are not an independent test. It scored the same held-out items as round 01, and the score was
   changed after round 01's numbers had been seen by the coordinator.
5. Five of the ten new theories import 2610.37719, and four of them (r2-across-2, r2-all-1, r2-external-1, r2-revise-1)
   predict the same DARE drop on the MLP delta at keep 0.01 %: 340 [220, 405], 20 [0, 120], 40 [0, 200] and 40
   [0, 150] right of 500. That is one prediction, not four.
6. The reviews, not the score, did the deciding: all 3 reviewed passers were refuted or judged weak (`reviews/`).
7. Forward predictions work. idea-0b2ad8 (P1, posted 02:24 UTC) was measured by another agent's experiment,
   result-e45bf4 (03:17 UTC, 53 minutes later), and refuted r1-all-1 by its own refutation rule.

Examples (`examples.json`), r1-all-2 on the plain prompt, MATH-500 n=500, T 1.0, v3: a divergent win on t41 (base +
0.5*(RL - base): measured 443, claim 432 [415, 450], nulls 400 and 380) and a divergent loss on t40 (base +
0.25*(RL - base): measured 405, claim 370 [340, 400], nulls 300 and 290).

## Round 03 (2026-11-15, cutoff 11-15 02:59 UTC)

`results/engine/round-03/`, plan `specs/SPEC_round03.md`, code `lib/round.py` (version 3). 85 board items before the
cutoff, 13 held out, 51 targets from 10 held-out items, none exposed. No earlier round scored these items. 14 theories:
4 carried from round 02 (r1-all-2, r1-surprises-2, r2-across-2, r2-all-2; r1-all-1 not carried, its review said
refuted) and 10 new from 5 generators. 28 headless jobs, about 28 minutes (`run.json`). Diagnosis: `diagnosis.md`.

**Result: no theory stands. 13 of 14 fail; r3-across-2 passes on a single claim (+0.67 nats against its reversal's
+0.29), its 3 offline tests returned no number (S3 403), and its review says weak. Summed over all 80 claims, the
theories lose 25.55 nats to the no-theory readers** (`metrics_v3.json`, `tests/r3-across-2.json`,
`reviews/r3-across-2.json`). Score table as printed (gain in nats; interval = 90 % bootstrap of the total):

| Theory | Claims | Total | Mean | 90 % interval | Reversal | Tests in/out | State | Review |
|---|---|---|---|---|---|---|---|---|
| r1-all-2 | 12 | 2.62 | 0.22 | [-3.81, 7.98] | | | fails | |
| r3-across-2 | 1 | 0.67 | 0.67 | [0.67, 0.67] | 0.29 | 0/0 (3 not computed) | passes | weak |
| r2-all-2 | 0 | 0.00 | 0.00 | [0.00, 0.00] | | | fails | |
| r3-revise-2 | 0 | 0.00 | 0.00 | [0.00, 0.00] | | | fails | |
| r3-surprises-1 | 4 | -0.24 | -0.06 | [-1.67, 1.18] | | | fails | |
| r3-across-1 | 6 | -0.35 | -0.06 | [-2.64, 1.67] | | | fails | |
| r3-all-2 | 3 | -1.36 | -0.45 | [-3.27, 0.56] | | | fails | |
| r3-external-1 | 2 | -1.43 | -0.72 | [-3.78, 0.91] | | | fails | |
| r3-all-1 | 4 | -2.67 | -0.67 | [-5.65, 0.42] | | | fails | |
| r3-revise-1 | 11 | -2.69 | -0.24 | [-10.17, 4.07] | | | fails | |
| r2-across-2 | 7 | -3.20 | -0.46 | [-10.49, 3.83] | | | fails | |
| r3-surprises-2 | 11 | -4.35 | -0.40 | [-12.14, 2.47] | | | fails | |
| r1-surprises-2 | 8 | -4.60 | -0.57 | [-13.80, 4.96] | | | fails | |
| r3-external-2 | 11 | -7.95 | -0.72 | [-16.47, 0.15] | | | fails | |

Hypotheses of the spec:

- H1, a candidate beats its reversal: not refuted by the rule, on one claim. r3-across-2 +0.67 vs +0.29; a bootstrap
  of one claim gives the point [0.67, 0.67]. Its review: the gap is the advocate's narrower interval on t13, and the
  reversal argued the same constant push.
- H2, a carried theory totals above 0: not refuted by the rule. r1-all-2 +2.62 nats on 12 claims, but its interval
  [-3.81, 7.98] reaches 0, so it fails. r2-all-2 made no claim; r2-across-2 -3.20; r1-surprises-2 -4.60.
- H3, half of the tested offline predictions return a number: refuted, 0 of 3.
- H4, a theory stands after tests and review: refuted. The engine still produces no theory worth a GPU run.

What round 03 showed (`diagnosis.md`):

1. Theories lose by wrong centres, not wrong widths. 37 claims whose centre is farther from the measured value than the
   midpoint of the null centres sum to -50.25 nats; the 43 as close or closer sum to +24.70 (40 of them gain).
2. The losses are the theories' own distinctive predictions, and they are wrong. 21 claims put both null centres
   outside their interval; 15 lose (-21.17 nats), 11 at the -3 clip. WSP-1 contradicts r1-surprises-2 (RL minus its
   top-8 directions: 91/100, claim 55; bulk64: 86, claim 50) and r2-across-2 (top-8 alone: 88/100, claim 58; 427/500,
   claim 305). result-edceef contradicts "any RL-Zero delta carries the shared part": RL-Zero-IF 377 and RL-Zero-Code
   3.0 411 with the cue, claims 436-446. r1-all-2 put RL-Zero-Mix plain at 438; measured 372.
3. Where theories agree with the no-theory readers they add nothing: the 59 non-divergent claims sum to -4.38 nats. The
   two readers are nearly one: their centres differ by a median 1.8 % of the measured value. Their 90 % intervals hold
   the measured value 42 and 43 times of 51; the advocates' 60 of 80, with a median width 0.62 of the nulls'.
4. The held-out set is mostly not about the theories. 22 of 51 targets drew no claim; the 9 interpretability readouts
   drew 1; 71 of 80 claims fall on 4 items. No target is about temperature or loops, which is the subject of 6 theories
   (10 claims among them).
5. The offline tests failed on credentials. The scripts called `aws s3 cp` with the default profile (403). With
   `--profile iterate-ecr` the bucket's `results/rlneurons/` keys read, so 2 of the 3 recipes were computable;
   `results/next_n13/` is 403 even with it. Of all 29 recipes of the new theories, 27 can be read on this machine now
   (8 from git alone, 14 with abaybektursun's Modal volume, 5 with the S3 profile); only one theory was tested.
6. The 10 new theories are 2 mechanisms, one of each per generator: a two-part delta (a shared low-dose part plus a
   math-specific part for long, hard problems; 5 theories) and a sampler-tail account of temperature and loops (5). Both
   restate earlier theories (r1-surprises-1, r2-all-2) and the "Bears on ... Prediction" paragraphs of `external.md`.
   Splitting the findings spread the citations (17 distinct papers, most used in 2 of 10; round 02: 12 distinct,
   2610.37719 in 5 of 10) but not the mechanisms.
7. The two-part-delta theories' own hard328 prediction failed: 4 of its theories put Code-RL 3.1 on hard328 at 171-177 of 328;
   measured 187, 0.9 points below theta(0.5) (t28, t33).

Examples (`examples.json`), r1-all-2 (most claims, highest total): a gain on t44 (base + top 8 singular directions per
matrix, MATH-500 n=500, plain, T 1.0, v3: measured 427, claim 380 [330, 425], nulls 300 [210, 415] and 330 [230, 425],
+1.05 nats; outside the interval but far closer than the nulls) and a loss on t39 (RL-Zero-Mix, plain: measured 372,
claim 438 [405, 462], nulls 415 [350, 460] and 415 [330, 460], -3.00 nats; the theory's switch did not carry over).

## Round 04 (2026-11-15, cutoff 11-15 03:40:58 UTC)

`results/engine/round-04/`, plan `specs/SPEC_round04.md`, code `lib/round.py` version 4 (commit bb43116). 98 board items before the cutoff, 16
after. No theory was carried: one blind agent got all 32 earlier theories and why each failed (`graveyard.json`) and listed 12 pairwise different
mechanisms (`mechanisms.json`); 12 blind agents developed one each, and 2 abandoned theirs (`dropped.json`). Each of the 10 theories stated 3 to 6
offline predictions with exact recipes on stored per-problem rows, fixed by sha256 before any row was read (`theories.sha256`). One test agent per
theory wrote scripts from the recipes, and round.py ran each once (`tests/`). Two no-theory readers predicted the same 42 numbers from the recipes and
the board alone (`tests_blind.jsonl`, `predictions/nulltest-{1,2}.jsonl`). Survivors then made claims on 70 held-out targets from 13 items (two strikes
remove a theory) and got a review. 37 headless jobs, about 57 minutes; the command ran twice, because one review wrote malformed JSON and the
second run redid only that review (`run.json`). Diagnosis: `diagnosis.md`.

**Result: 3 of 10 theories survive, and all 3 reviews say weak. 29 of 42 offline predictions were computed: 18 inside their 90 % interval, 11
outside; 4 theories refuted, 3 untested.** One new measurement, replicated: plain MATH-500 cap hits at T 0.6 / top-p 0.95 go from 65 (base) to 103
(RL step 100) and 98 (step 400), then down to 19 (step 2,800), n = 500 each (`tests/r4-m10.json`, `replication/replication.json`). Table as
`metrics_v4.json` holds it (gain in nats against the two readers; GPU predictions from `theories/<name>.json`, not run):

| Theory | Statement | Computed | In / out | Gain | State | Review | GPU prediction [90 %] |
|---|---|---|---|---|---|---|---|
| r4-m10 | Early RL (steps 100-400) lowers entropy, so T 0.6 / top-p 0.95 sampling loops more and cap hits rise above the base's; truncation-as-failure training later removes the loops. | 4 of 5 | 4 / 0 | +9.86 | survives | weak: rise real, entropy mechanism untested; length growth gives the same counts | step 400, plain, T 1.0, MATH-500: 440 [415, 458] of 500 right, cap hits below 98 |
| r4-m01 | The cued base's T 0.6 loops feed on its own text: loop hazard grows with how compressible (zlib) the text so far is; the base finishes from RL's prefix because RL's text is less self-similar. | 3 of 4 | 3 / 0 | +1.41 | survives (held-out strikes 0 of 3) | weak: gain is one descriptive test (p3); held-out ablation claims -3.00 each; core partly published | delete repeated lines from the 78 K_own prefixes: 32 [26, 39] of 78 finish |
| r4-m08 | Part of the cued base's accuracy is recall from pretraining, so at matched difficulty the RL-minus-base gap is larger on problems published after the base's data cutoff. | 3 of 3 | 3 / 0 | +0.12 | survives | weak: only gain from 60 post-cutoff problems; distinctive test p2 has the opposite sign | flag problems the base completes verbatim: gap flagged minus unflagged -6 [-15, 1] points |
| r4-m12 | Part of the hard328 gap is grader v3 false negatives on the base's equivalent but non-canonical answers to non-integer problems; RL writes canonical forms. | 1 of 4 | 1 / 0 | -0.32 | untested | | re-state each finished wrong hard328 answer in simplest form: base 168 [165, 173] of 328 right |
| r4-m06 | RL added a constant hold-on bias and no error detector, so it re-checks right and wrong intermediate answers at the same added rate. | 0 of 3 | | 0 | untested | | RL continues its own right box or a planted wrong one: re-check difference 0.06 [0.0, 0.16] |
| r4-m11 | The cued base often keeps writing after its answer and states a new one; the last-marker grader scores the later one, so part of its MATH-500 deficit is a stopping artifact. | 0 of 5 | | 0 | untested | | continue base answers cut after their first marker: 0.15 [0.06, 0.30] write on without EOS for 50 tokens |
| r4-m02 | Within a problem, a longer finished base sample means abandoned attempts, so length reads out failure for the base; RL's extra tokens are habitual checks, so RL length carries little signal. | 3 of 3 | 2 / 1 | -3.76 | refuted | | 4 fresh base samples on mixed problems: shortest minus longest right 0.22 [0.08, 0.36] |
| r4-m04 | base + a(RL - base) is a per-answer mixture of the two endpoint modes, so the RL share implied by accuracy also shows in 'Wait' rate, format and boxed accuracy. | 4 of 4 | 2 / 2 | -5.28 | refuted | | theta(0.125), plain, T 1.0, MATH-500: 345 [305, 385] of 500 right |
| r4-m09 | Code-RL 3.1's math gain is only an ending policy (finish under the cap with one answer, then stop); it adds nothing where the base finishes wrongly. | 6 of 6 | 3 / 3 | -6.70 | refuted | | Code-RL minus base per-sample accuracy on base finished-wrong problems: 2 [-7, 9] points |
| r4-m07 | Base wrong answers are shared attractors plus scattered slips; RL removes the slips and keeps the attractors, so RL's wrong answers mostly equal the base's. | 5 of 5 | 0 / 5 | -12.65 | refuted | | 8 RL samples on base-attractor problems: 0.32 [0.17, 0.48] right |

Abandoned: r4-m03 (Math and Code RL make the same KL-nearest change), contradicted by result-edceef (Code 3.0 cue 411, Math 3.0 448); r4-m05 (the
residual gap sits where the cue fails to override the exam register), contradicted by result-fdc8da (121 of 132 'Answer:'-line answers right) and
result-9b6af3 (`dropped.json`). The 13 predictions not computed: 12 because the test scripts ran under plain python3 without the grader's packages
(math_verify; sympy's LaTeX parser), fixed after the round in commit ae194ae; 1 (r4-m01 p1) because base-01 F_math500 holds one sample per problem,
although `inventory.md` says 1 to 4. The untested r4-m06, r4-m11 and r4-m12 are carried to round 05.

Hypotheses of the spec (`diagnosis.md` a):

- H1, at least 6 different mechanisms: holds, 9 groups among 10 theories (round 03: 2). Only r4-m02 and r4-m06 share a claim one test measures
  (RL's added checking does not depend on whether the answer is right).
- H2, half the offline predictions return a number: holds, 29 of 42 (round 03: 0 of 3).
- H3, a theory refuted by its own computed predictions: holds, 4. r4-m04 (p1 0.327, bootstrap 90 % [0.25, 0.41], against the bound 0.60) and
  r4-m07 (p1 35 of 131 = 0.27 against 0.36; p3 12 of 16 = 0.75 against 0.50) are firm. r4-m02 (p2 0.718, cluster bootstrap [0.64, 0.80], bound 0.68)
  and r4-m09 (p2, p4, p5 each about one standard error past their bounds) are within noise of their bounds, though far from their own centres.
- H4, a survivor with gain above 0 that its review does not call refuted or published: holds by the rule, 3. All three reviews say weak and all three
  novelty checks say partly published.

Replication (`replication/replication.json`): an agent that had not seen `tests/` recomputed the 7 computed predictions of r4-m10 and r4-m01 from the
recipes alone; all 7 equal. Cap hits at T 0.6 / top-p 0.95, plain, sample 0: MATH-500 base 65, step 100 103, step 400 98, step 2,800 19 (n = 500
each); clean 328 base 137, step 400 160, step 2,800 64. The rise is 8 to 10 times the rerun spread of 0 to 4 of 500 (`studies/rlneurons/README.md`
lines 101-107, 189, 252). No committed file or board item before the cutoff held the step-100 or step-400 counts. r4-m01 p4's interval [0.47, 0.65]
includes 0.5, and its text[:3000] is mostly the prefix the model was handed.

What round 04 showed (`diagnosis.md`):

1. The tests run and can fail a theory: 29 of 42 computed, 4 theories refuted; the scripts read against their recipes (r4-m07 p1 and p3, r4-m04 p1,
   and in the reviews r4-m10 p2, r4-m08 p1, r4-m01 p2) implement them as written.
2. The largest gain is one contrast counted three times: r4-m10 p1-p3 give 8.89 of its 9.86 nats. No test measured entropy or the top-p lock, though
   the rows store mean_logprob; step 100/400 answers never start with the cue (0 of 500) while step 2,800's do (495 of 500).
3. Survival is too easy. r4-m01's total rests on p3 (+1.59; without it -0.18); r4-m08's on p1 (+0.70; without it -0.58), and its separating test p2
   came out +0.143 against a predicted -0.3, inside only because the bound was 0.15.
4. The two readers are calibrated, not weak: inside their intervals 25 and 24 of 29 times, the theories 18 of 29; the theories lose 17.32 nats to them
   over all 29 tests. They are one reader twice: 6 of 29 centres equal, same side of the measured value 25 of 29.

Examples (`examples.json`): r4-m10 p2 inside (step 400 minus base cap-hit rate, measured 0.066, predicted 0.06 [0.015, 0.12], readers -0.06 and
-0.07, +3.00 nats, `tests/r4-m10/p2.py`) and r4-m04 p1 outside (theta(0.25) plain 'Wait'-rate share, measured 0.327, predicted 0.76 [0.60, 0.90],
readers 0.38 and 0.50, -3.00 nats, `tests/r4-m04/p1.py`).

Raw job folders: `/var/folders/9j/yjj9b3jj47v01_299q09_nc40000gn/T/theory-round-7oea0ind` (first run) and `theory-round-rkccxu3q` (the review rerun),
on abaybektursun's laptop; row files fetched by the scripts in `runs/theory-tests/` and by the replication in `runs/replication/` (not committed).

### Round 04, rival stages (version 5)

Plan `specs/SPEC_round04_duel.md` (ea73cfc, before the run), code commit 1f1ea4e, stages `rival`, `defend`, `duel_test`, `score_duel`; 9 headless
jobs, about 7 minutes (`run.json` key `duel`). For each survivor a blind agent wrote the strongest other mechanism and 2 to 4 offline tests where the
two differ, with its own predictions; a second blind agent predicted the same tests from the theory; scripts computed them once. Gain = log density
of the theory's prediction minus the rival's, clipped to [-3, 3] nats (`metrics_v5.json`, `rivals/`). Diagnosis: `duel.md`.

**Result: r4-m01 beats its rival (+4.43 nats, +3.00 of it from one test); r4-m10 (-1.30) and r4-m08 (-1.57) print "loses to rival", but none of
their 6 tests reaches 1 nat, and on all 9 tests the defender's centre lies inside the rival's interval.**

| Theory | Rival | Computed | Gain | State as printed | Reading |
|---|---|---|---|---|---|
| r4-m01 | The loop hazard is a property of the problem; compressibility predicts loops only across problems. | 3 of 3 | +4.43 | beats rival | Within one problem the capped sample's opening compresses better than a finishing restart's in 37 of 46 (0.804; 25 of 32 without samples whose loop starts before character 6,000). Compressibility keeps its signal within quartiles of difficulty (0.645). Cause still open: an early impasse may make the text repetitive. |
| r4-m10 | By step 100 RL has installed the opening the cue forces, so cap hits go to about the cued base's 119 of 500, with no entropy change. | 3 of 3 | -1.30 | loses to rival | Step-100 plain answers open in the 'Okay' format 478 of 500 (base 193 by the same recipe); finished length 2.25 times the base's; at step 400 the cue adds no cap hits (-0.028). These fit the rival better than the theory as written, but no test measured entropy. |
| r4-m08 | No exposure effect: the gap follows difficulty and termination; the +6.9-point excess is noise. | 3 of 3 | -1.57 | loses to rival | The post-cutoff excess changes sign at T 0.6 (-5.6 points, 60 post problems); RL's short right answers have low entropy too (0.77). Fits the rival; gains small because the defender's intervals were wide. |

Hypotheses (`duel.md`): D1 (the stage runs) holds, 3 of 3 survivors with 3 computed tests. D2 (half the tests separate by 1 nat or more) refuted,
1 of 9. D3 (the defender reads the theory as the rival's `theory_should_say` does) holds by the letter, 9 of 9, but on r4-m10 the defender, who was
given the board, moved 76 % to 82 % of the way to the rival's numbers. D4 refuted: r4-m10 and r4-m08 lose as predicted, r4-m01 wins.

Second turn (version 5.1, code 74ceb42; `run.json` key `duel.turn2`): not in the spec, added after D2 was refuted, with no hypothesis stated before
the run. Each rival saw the defender's turn-1 numbers and wrote replacement tests (7, all computed); `metrics_v5.json` now scores both turns, and a
total of 2 nats or more in size decides. The defender's centre was inside the rival's interval on 5 of the 7 new tests.

| Theory | Turn-2 tests (measured; theory; rival; gain) | Total, both turns | State now | Reading |
|---|---|---|---|---|
| r4-m10 | step-400 share of finished answers sharper (mean_logprob) than the cued base's median 0.480; 0.76 [0.62, 0.89]; 0.58; -3.00. Step 400's position between cued base and step 2,800 0.067; 0.75; 0.25; -3.00. Step 100 share 0.554; 0.63; 0.53; -0.50 | -7.81 (6 tests) | loses to rival | Steps 100 and 400 are as sharp per sampled token as the cued base (medians -0.155, -0.163 against -0.161), not sharper; the opening switch explains the cap hits. Step 2,800 (-0.192) is less sharp than the cued base. Recomputed independently, 3 of 3 equal (`replication/replication_turn2.json`). |
| r4-m01 | RL-prefix finish advantage where RL's opening is as compressible 0.375 (24 problems); 0.12; 0.25; -1.85. Opening compressibility against loop onset, rank correlation -0.074 (62 loops); 0.2; 0.06; -1.47 | +1.11 (5 tests) | not separated from rival | Self-similarity marks the sample that will loop (37 of 46) but explains neither RL's prefix advantage nor onset timing. |
| r4-m08 | base/RL length variability on short problems 0.518 (214); 0.05; 0.2; -0.87. Short minus long -0.020; -0.15; 0.1; -0.21 | -2.65 (5 tests) | loses to rival | Every test sits at or past the rival. |

## Round 05 (2026-11-15, cutoff 11-15 04:29:33 UTC, coordinator frustea)

Plan `specs/SPEC_round05.md` (before the run), engine version 5.1 unchanged (main a54a897), work-9abc35. One command, one run, exit 0:
`round.py results/engine/round-05 all --cutoff 2026-11-15T04:29:33 --skip gpuprice --skip "theory round" --skip "theory skill" --skip "Theory engine" --from results/engine/round-04`.
114 items before the cutoff, 41 held out; 12 mechanisms, 2 abandoned, 10 developed, 3 untested theories carried from round 04; 54 headless
jobs, about 62 minutes, no GPU (`results/engine/round-05/run.json`). Examples: `results/engine/round-05/examples.json`.

**Result: 1 of 13 theories survives its offline tests and the review (r5-m03, review "weak", loses to its rival by -8.77 nats); 45 of 48
offline predictions computed, 22 inside and 23 outside their intervals; 11 refuted (9 by their own computed predictions, 2 by the review),
1 no gain. r5-m08 is the first theory of five rounds to beat its rival with both turns counted (+8.75 nats, 5 tests, 3 separating), but the
review refutes its stated cause. No theory both beats its rival and stands.** Tables: `metrics_v4.json` (tests), `metrics_v5.json` (duel).

Hypotheses of the spec: H1 holds (45 of 48 computed; the 3 without a number: 2 need another workspace's Modal volume, 1 had a group under
20 rows). H2 holds (the 3 carried theories each have 3 or more computed predictions). H3 holds by the duel rule only (see r5-m08).

| Theory | Statement | Tests computed | In / out | Gain (nats) | State | Duel | Review | What decided it |
|---|---|---|---|---|---|---|---|---|
| r5-m08 | Code 3.0 learned a runaway long-generation mode, so at T 1.0 it keeps Code 3.1's gain on short MATH-500 problems and loses it on the longest quartile through cap hits. | 4 of 4 | 4 / 0 | +5.76 | refuted (review) | beats rival, +8.75 (5 tests, 3 separating) | refuted | The length pattern holds: 0.795 of Code 3.1's lead is in the longest quartile; on the short half Code 3.0 is 3 problems ahead of Code 3.1 (246 against 243 of 250) and 7.25 ahead of the cued base; in the longest quartile it is 11.25 behind the cued base. The cause does not: the scored Code 3.0 cell has 5 cap hits of 500 (base 27, Code 3.1 7). |
| r5-m03 | The top-8 singular directions of the RL-Math weight change act like the opening cue and nothing more. | 3 of 3 | 2 / 1 | +1.86 | survives | loses to rival, -8.77 (3 tests, 3 separating) | weak | Its gain is one test, the count of quick finished-wrong answers of top8 plain (22; predicted 11 [5, 21]), which lies outside its own interval. Rival: top8 is a per-sample mixture of RL-like answers and plain-base answers. top8's quick wrong answers fall on problems the cued base solves at a mean rate of 0.818 (theory 0.5, rival 0.76); 0.773 of them have at most 1,000 tokens (theory 0.4, rival 0.63). |
| r5-m10 | At T 1.0 the plain base picks one of two whole answer modes in its first tokens; the cue's gain is the mode share times the accuracy difference, and nothing after the opening adds. | 3 of 3 | 3 / 0 | +0.72 | refuted (review) | loses to rival, -8.84 (6 tests, 3 separating) | refuted | Self-opened plain answers do score like cued ones (difference 0.00) and are 1.21 times as long. But plain answers that do not self-open and contain 'Wait' or 'Hmm' later score +0.356 above the other non-self-opened answers and only 0.075 below cued answers on the same problems (theory -0.47). The standing part is in Wang et al. 2610.06851, App. C.8. |
| r5-m06 | The problems RL solves and the cued base misses 4 of 4 are ones the base already solves a few percent of the time per sample. | 3 of 3 | 2 / 1 | +4.76 | refuted (own test) | | | A pool of other samples solves 11 of these 17 problems at least once (0.647), 0.522 more than of the 16 that RL also misses, as predicted. Correction after the audit of result-07f566: the pool is not base-only (it holds cap-hit restarts, the base with a random weight edit, the base with 3 examples, a T 1.5 min-p cell and a T 0.6 cell); 4 of the 11 are solved only by the edited or example-prompted base, and the base's own restarts solve 7 of 17. Refuted on the size: the per-sample rate is 0.237, not "a few percent" (predicted 0.09 [0.03, 0.18]). |
| r4-m12 | Part of the hard328 gap is grader v3 false negatives on the base's non-canonical answers to non-integer problems. | 4 of 4 | 2 / 2 | -1.15 | refuted (own test) | | | Numeric equivalence recovers 0 of the cued base's finished v3-wrong non-integer answers; the gap after regrading stays 12.8 points. |
| r5-m11 | Code-RL 3.1 reaches Math-RL's MATH-500 total through a code-style habit that pays on discrete subjects. | 3 of 3 | 1 / 2 | -2.50 | refuted (own test) | | | Code-style markers are no more frequent in Code-RL's hard328 answers than in the cued base's (difference 0.00); marked answers score 0.123 below unmarked ones. |
| r4-m06 | RL added a constant hold-on bias and no error detector. | 3 of 3 | 2 / 1 | -2.72 | no gain | | | RL's re-check rate after wrong against right candidates is 1.24 and the base-RL difference is -0.087, both as predicted and as the readers said; the share of final-right answers with a re-checked right candidate is 0.44 higher in RL (predicted 0.12). |
| r5-m07 | By RL step 100 the policy differs from the base almost only in opening with the RL cue. | 3 of 4 | 1 / 2 | -3.44 | refuted (own test) | | | 3.4 % of step-100 plain answers at T 0.6 open with 'line' (predicted 0.68); 4.5 % of finished ones keep the base's 'Answer:' line (predicted 0.30). |
| r5-m04 | Think-SFT's remaining errors are mostly cap hits on the problems where RL writes longest. | 5 of 5 | 1 / 4 | -4.17 | refuted (own test) | | | 25 cap hits of 500 (predicted 38 [28, 55]); in the longest quartile Think-SFT is 6 problems ahead of RL, not behind. |
| r4-m11 | The cued base keeps writing after its answer and the last-marker grader scores a later, wrong one. | 3 of 5 | 0 / 3 | -4.48 | refuted (own test) | | | Of the cued base's v3-wrong answers, 0 have a right first answer marker. |
| r5-m02 | The cued base's wrong finished samples are shorter than their right siblings on Levels 1-3 and longer on Level 5. | 4 of 4 | 2 / 2 | -5.84 | refuted (own test) | | | On Levels 1-3 wrong samples are longer, not shorter (median log length ratio +0.193; predicted -0.2). |
| r5-m05 | The base flags a doubtful step as well as RL but restates its value after the hold-on token, while RL re-derives it. | 3 of 3 | 1 / 2 | -6.12 | refuted (own test) | | | Base and RL revise the value after a hold-on at the same rate (ratio 1.04; predicted 0.55). |
| r5-m09 | About a quarter of the cued base's finished-wrong samples on usually-solved problems box a number from the problem statement. | 4 of 4 | 1 / 3 | -8.13 | refuted (own test) | | | Base minus RL share of wrong finals equal to a problem-statement number is -0.043 (predicted +0.14). Its p1 and p2 are 0 by data layout (the field they read is null on real items) and decide nothing. |

Abandoned by their developers (`dropped.json`): r5-m01 and r5-m12. Held-out filter: 70 targets, 7 claims by the 3 survivors, 0 strikes.

GPU predictions, none run: r5-m03, base + top8 edit with the cue on MATH-500, 425 [412, 438] of 500, refuted at 441 or more or below 405
(45 GPU minutes); its rival's mixture account is the one to test with the same cell. r5-m08 (40 minutes, cap hits of Code 3.0 on the
longest quartile) and r5-m10 (40 minutes, prefilled '.\n\nOkay') belong to refuted theories.

Not done: no independent recomputation of the computed numbers; the reviews read items after the cutoff, by design.

## Account runs (version 6 and 6.1, cutoff 11-15 04:29:33 UTC)

Stage `account` (`lib/round.py` version 6, commit b7f1ae2; version 6.1, commit 856971b; prompt `lib/prompts/account.md`): one blind agent
writes one account of the gap in right answers between the cued Olmo 3 base and an RL-side model. The account is a fixed ordered list of parts
(loop, budget, answer statement, reliability, capability, unassigned), each with a rule on stored rows that puts every gap problem in exactly one
part, so the shares sum to 1 per cell. Its predictions are tested like a theory's: scripts written from the recipes before any row is read, two
no-theory readers, log gain in nats. `--only-account` skips mechanisms and develop. In 6.1 the account must span at least 3 cells, and a budget the
board already gives is input (`known`), not a prediction. Plans `specs/SPEC_account01.md` and `specs/SPEC_account02.md`; records
`results/account/run-0<n>/run.json`; independent check and readout of run 02 in `results/account/run-02/check/` and `readout.md`.

| Run | Code | Cells predicted | Computed | Inside / within noise / outside | Gain | State | Reading |
|---|---|---|---|---|---|---|---|
| `results/account/run-01/` | b7f1ae2 | 1: MATH-500 T 1.0, cued base against RL, 65 gap problems (already tabulated by result-5e17a6) | 9 of 9 | 8 / 1 / 0 | -1.30 | no gain | Restated the board's budget; its budget and answer-statement shares equal both readers' centres. |
| `results/account/run-02/` | 856971b | 3 new cells, known cell as input | 20 of 20 | 17 / 1 / 2 | +1.61 | refuted by p16 | Budgets reproduce exactly; p16 (reliability at T 0.6, 0.379 against 0.15 [0.07, 0.25]) fails mostly on grader v1. |
| `results/account/run-03/` | 537adb7 | 5 new cells, 3 claimed cells fitted (not scored), 1 null cell | 46 of 46 scored (66 offline) | 40 / 6 / 0 | +8.23 | survives; loses to rival, -5.16; review weak | 51 of 51 shares recomputed equal; no part of the MATH-500 T 1.0 gaps differs from the null; +8.77 nats come from answer-statement shares. |

Budgets of run 02 (share of gross gap problems; 90 % bootstrap over gap problems, 2,000 resamples, seed 0; reliability and capability with all
evidence rows E and with E cut to 3 rows; unassigned 0 everywhere). Engine values: `results/account/run-02/metrics_v4.json` and `tests/r6-account/`;
recomputation, known cell under the same rules and null cell: `results/account/run-02/check/budget.out.txt` (`check/budget.py`).

| Cell | Gap / base-only | Loop | Budget | Answer statement | Reliability, full E / E = 3 | Capability, full E / E = 3 |
|---|---|---|---|---|---|---|
| known: MATH-500 T 1.0, base cue against RL plain, r6 rules | 65 / 12 | 0 | 0.246 [0.169, 0.338] | 0.031 [0, 0.062] | 0.662 [0.569, 0.754] / 0.631 [0.523, 0.723] | 0.062 [0.015, 0.108] / 0.092 [0.031, 0.154] |
| theta0.5 cue, MATH-500 T 1.0 (p1-p6) | 53 / 11 | 0 | 0.208 [0.113, 0.302] | 0.038 [0, 0.075] | 0.698 [0.585, 0.792] / 0.642 [0.528, 0.755] | 0.057 [0.019, 0.113] / 0.113 [0.057, 0.189] |
| Code-RL cue, clean harder 328 T 1.0 (p7-p12) | 37 / 14 | 0 | 0.270 [0.162, 0.405] | 0.027 [0, 0.081] | 0.432 [0.297, 0.568] (E is 3) | 0.270 [0.162, 0.378] (E is 3) |
| RL step 400 plain, MATH-500 T 0.6 / top-p 0.95, grader v1 (p13-p18) | 66 / 27 | 0.439 [0.333, 0.530] | 0.121 [0.061, 0.182] | 0.061 [0.015, 0.121] | 0.379 [0.288, 0.470] / same | 0 [0, 0] / same |
| null: base + random direction with the cue (a fresh base sample), T 1.0 | 42 / 35 | 0 | 0.167 [0.071, 0.262] | 0.024 [0, 0.071] | 0.714 [0.595, 0.833] / 0.667 [0.548, 0.786] | 0.095 [0.024, 0.167] / 0.143 [0.071, 0.238] |

- The board's version of the known cell (hand labels, result-5e17a6), given to the account as input, is 0.246 / 0.154 / 0.538 / 0.062; under the
  account's own text rule answer statement is 0.031 and reliability 0.662.
- At equal E, 90 % intervals apart: the T 0.6 cell's loop part and its lower reliability and capability against every MATH-500 T 1.0 cell, and hard328
  capability against the known cell (by 0.008). Nothing else; RL's T 1.0 budget and the fresh base sample's agree in every part. hard328's 3 evidence rows are weaker
  (T 0.6 or plain, 2 graded v1, 40 of 111 at the cap), so its capability share is an upper bound.
- Hand read of the 25 T 0.6 reliability problems (`check/s0400_reliability_hand.json`): 9 are right answers grader v1 rejects (Unicode forms, two
  boxes, \( \)), 2 copy the prompt template on the answer line, 14 are wrong values (0.212 of 66, inside the prediction). 3 of the 10 hard328
  capability problems are right in a stored forced-commit base row (`check/rawtext.out.txt`).
- No board item or committed file before this run gave a breakdown of the three new cells. Hypotheses: A1 holds, A2 refuted, A3 and A4 not run
  (no rival, no review); B1 holds only on the readers' mean (9 of 18), B2 holds, B3 refuted, B4 holds (`results/account/run-02/readout.md`).

Run 03 (version 6.2, code 537adb7, plan `specs/SPEC_account03.md`, record `results/account/run-03/run.json`, readout
`results/account/run-03/readout.md`, examples `results/account/run-03/examples.json`). New in 6.2: a null cell (cued base against a second
cued-base sample), every share also as its difference from the null, gross and net counts, one evidence set for all cells (2 plain-base rows,
grader v3), claimed cells fitted and not scored, shares 0 by construction not scored, a `replicate` stage, and the review always. Account
`r7-account` (`results/account/run-03/theories/r7-account.json`): parts loop, budget, answer statement, reliability (a plain-base row right),
deliberation (no plain-base row right). Shares of gross gap problems (`results/account/run-03/metrics_v4.json`, `tests/r7-account/p<k>.out.txt`;
90 % intervals in the readout); * = 90 % interval apart from the null's; unassigned 0 everywhere.

| Cell | Gap / base-only / net | Loop | Budget | Answer statement | Reliability | Deliberation |
|---|---|---|---|---|---|---|
| null: second cued-base sample, MATH-500 T 1.0 | 27 / 32 / -5 | 0 | 0.111 | 0.037 | 0.481 | 0.370 |
| fit: RL plain, MATH-500 T 1.0 | 65 / 13 / +52 | 0 | 0.246 | 0.031 | 0.431 | 0.292 |
| fit: RL plain, hard328 T 1.0 | 52 / 7 / +45 | 0 | 0.365 * | 0.019 | 0.212 * | 0.404 |
| fit: RL step 2,800 plain, MATH-500 T 0.6 | 112 / 9 / +103 | 0.598 * | 0.179 | 0.009 | 0.152 * | 0.062 * |
| Code-RL cue, MATH-500 T 1.0 | 57 / 17 / +40 | 0 | 0.228 | 0.035 | 0.474 | 0.263 |
| theta0.5 cue, hard328 T 1.0 | 40 / 13 / +27 | 0 | 0.375 * | 0.025 | 0.250 | 0.350 |
| step 400 plain, MATH-500 T 0.6 | 55 / 29 / +26 | 0.527 * | 0.145 | 0.018 | 0.218 * | 0.091 * |
| step 100 plain, MATH-500 T 0.6 | 61 / 33 / +28 | 0.590 * | 0.115 | 0.016 | 0.197 * | 0.082 * |
| 3.0 first release plain, MATH-500 T 0.6 | 76 / 58 / +18 | 0.605 * | 0.145 | 0.013 | 0.171 * | 0.066 * |

- Every difference from the null that clears the intervals (15) is in a T 0.6 or hard328 cell; the null is MATH-500 T 1.0, so these also change
  temperature or problem set. The matched cells, RL and Code-RL on MATH-500 T 1.0, differ from the null in no part (0 of 10).
- Replication (`results/account/run-03/replication/r7-account.json`, `r7-account.duel.json`): 51 of 51 shares and 2 of 2 duel tests equal.
- The account's mechanism (RL multiplies a deliberation mode) missed where tested: Code-RL deliberation 0.263 against 0.43 [0.30, 0.56] (p33,
  -2.06 nats) and reliability 0.474 against 0.29 [0.17, 0.42] (p32, -1.82), both outside within noise. Its gain is answer-statement shares
  (+8.77 nats over 6 cells) and undeclared zeros (+1.95).
- Rival (`results/account/run-03/metrics_v5.json`): one difficulty axis plus sampling (result-5da8a9). theta0.5 cue on MATH-500, 52 gap problems:
  reliability 0.481 (account 0.31, rival 0.45, -2.85 nats), deliberation 0.269 (account 0.40, rival 0.28, -1.68); Think-SFT cue, 65 gap
  problems: reliability 0.385 (account 0.29, rival 0.43, -0.63). Total -5.16, loses to rival. Review weak
  (`results/account/run-03/reviews/r7-account.json`): the rival's one-axis premise is contradicted off MATH-500 by result-bf6124; its core is on
  the board (result-5da8a9, result-f39ba8) and partly in Yue et al. 2504.13837.
- Held-out: 6 claims, 0 strikes; 2 of them (t58, t60, +3.0 each) were in the account's inputs (`graveyard.json`, `facts.json`).
- Hypotheses: C1 to C4 hold (`results/account/run-03/readout.md`). Nothing new for the board against result-f39ba8; draft confirmation and
  correction in `results/account/run-03/board_posts.md`.

## Promoted run 01 (version 6.2, cutoff 11-15 04:29:33 UTC)

Plan `specs/SPEC_promoted01.md`; code 537adb7 (replicate and review at 28db85f); record `results/promoted/run-01/run.json`, readout
`results/promoted/run-01/readout.md`. The round-04 winner r4-m10-rival (RL's first 100 steps install the opening the cue forces, with no per-token
sharpening; 6 carried tests, +7.81 nats) met a fresh rival: truncation-negative reward prunes T 0.6 loops from the first steps, so cap hits fall
steadily. Three rival tests (`results/promoted/run-01/metrics_v5.json`, `rivals/r4-m10-rival/`), plain prompt, T 0.6 / top-p 0.95:

| Test | n | Measured | Theory | Rival | Gain |
|---|---|---|---|---|---|
| Step-400 cap-hit rate, MATH-500 | 500 | 0.196 [0.166, 0.226] | 0.235 | 0.15 | +0.39 |
| Step 100 minus step 400, paired, MATH-500 | 500 | +0.010 [-0.020, 0.040] | 0 | 0.05 | +0.81 |
| Step 400 minus cued base, paired, 400-problem hard set | 400 | -0.0475 [-0.0875, -0.0075] | -0.01 | -0.10 | +0.29 |

- Total +1.49 nats, not separated from rival. Tests 1 and 2 restate numbers already in `results/promoted/run-01/facts.json` (entries 24 and 25,
  round-04 step 100 and step 400 minus base: 0.076 and 0.066). No duel test reached 1 nat, so nothing was recomputed.
- Review weak (`results/promoted/run-01/reviews/r4-m10-rival.json`): 6.0 of the 7.81 offline nats rest on one measurement implied by Wang et al.
  2610.06851; the flat-cap-hit claim was fitted to counts the theory had seen, and step 100 and step 400 sit below the cued base (103 and 98
  against 119 of 500). P1, P2, P3 hold; P4 not tested. Separating test: plain T 0.6 cap hits at a checkpoint between steps 800 and 1,600.

## GPU experiments

**selfopen-01** (round-05 entry `r5-m10:theory:intervention`; plan `specs/SPEC_selfopen01.md`). Rejection sampling on the plain base's own
opening, no prefilled tokens: per problem up to 32 openings of 24 tokens, keep the first with '\nOkay' in its first 60 characters, continue it
to 16,384 tokens (T 1.0 / top-p 1.0, grader v3). **411 of 500** (cap hits 20, 3,795 tokens per answer), against the stored plain T3 224 and the
stored cue T1 410. r5-m10 predicted 375 [348, 400] (refuted); its rival 405 [386, 422] (holds). Control (first draw that does not self-open,
continued the same way): 137 of 403 on the problems that self-opened, against 332 of 403 for the main arm, +48.4 points [42.9, 53.6]; T1 on the
same 403: 329. 94 stored T3 rows already self-opened (78 right); of the 406 regenerated problems 403 self-opened within 32 draws (median 4
draws), 3 never did (1 right).
- Files: `prep/selfopen01_t3.py` writes `data/selfopen01_t3.json` (the 94 stored self-opened rows, the 406 to regenerate); `jobs/selfopen_gen.py`
  (GPU, `--shard k/4`); `analysis/selfopen01.py` (readout, merges the shards). Outputs `results/experiments/selfopen-01/` (`run.json` with the
  job ids, `metrics.json`, `per_problem.json`, `examples.json`).
- Raw generations (not committed): `runs/abaybektursun-1115-021039-24f7/{s0,s2}`, `runs/ih-1115-095450-2b5a`, `runs/abaybektursun-1115-015601-2e73`
  on the laptop of the run; the AWS shard also in `s3://pg-lineage-769063704696/results/ih/ih-1115-095450-2b5a/out/`.

## Round 06 (2026-11-15, cutoff 11-15 06:51:23 UTC, coordinator frustea)

Plan `specs/SPEC_round06.md` (before the run), engine version 6.3 with `--account-from results/account/run-03`, work-a9a6dd, launched with
`jobs/round.sh`. Two runs: the first stopped in the replicate stage (a print in `round.py` failed on a test without a refuting condition;
fixed on ali/theory06, no score changes), the second resumed. 62 headless jobs, about 125 minutes, no GPU (`results/engine/round-06/run.json`,
logs `round06.log`, `round06b.log`, examples `examples.json`).

**Correction (2026-11-15 12:10 UTC, after the audit on result-8b0706 and the re-scoring with engine 7.1): no theory stands. Under the 7.1
duel rule (a test where the defender's centre is inside the rival's interval adds 0; a win needs 2 separating tests) r5-m03-rival has +3.00 on
1 of 6 tests, r5-m10-rival +3.00 on 1 of 6 and the account 0 of 5: all three are "not separated from rival". r5-m03-rival's one separating
test has a group of 22 problems (-0.057, 90 % [-0.23, 0.13], rival 0.25), and its 3 carried tests are round-05 duel wins, not tests against
no-theory readers. The result below is as printed by engine 6.3 and is kept for the record; read "beats rival" and "stands" as weak.**

**Result: r5-m03-rival is the first theory of six rounds that survives its tests, beats a fresh rival (+6.70 nats, 6 tests, 1 separating) and
whose review says "stands". r5-m10-rival also beats its fresh rival (+13.20, 6 tests, 1 separating) but its review says "weak". The account
r6-account has 43 of 44 scored predictions inside (+35.41 nats, 38 of 38 decisive numbers replicated) and loses to a one-axis rival (-3.11,
0 separating tests). Of 6 new theories 5 are refuted by their own predictions and 1 is untested; 6 mechanisms were abandoned by their developers.
67 of 71 offline predictions computed: 56 inside, 3 within noise, 8 outside.**

Hypotheses of the spec: H1 holds (both carried rivals beat their fresh rivals). H2 refuted (54 of 55 recomputed numbers equal; r6-m11 p1
differs and is left out of its score). H3 holds (inventory and external both done after 826 s; 1,359 s in round 05).

| Theory | Statement | Tests computed | In / noise / out | Gain (nats) | State | Duel | Review | What decided it |
|---|---|---|---|---|---|---|---|---|
| r5-m03-rival | The top-8 edit of the RL-Math weight change is an incomplete switch per sample: most base+top8 plain answers follow a weak dose of RL's policy, 10-15 % stay in the plain-base register. | 3 of 3 (carried from round 05) | 3 / 0 / 0 | +8.77 | survives | beats rival, +6.70 (6 tests, 1 separating) | stands | Fresh rival: the quick wrong answers are a per-problem plain-prompt failure. On top8's quick-wrong problems the plain base's wrong rate is 0.455 (n 22; theory 0.52, rival 0.68) and, against top8-right easy problems, -0.057 higher (n 401; theory 0.03, rival 0.25). The review asks to drop "whatever the difficulty": plain-register accuracy does depend on difficulty (0.232 and 0.491 contrasts). |
| r5-m10-rival | The cue's gain at T 1.0 is robustness to sampling noise: the terse plain register is derailed after its opening by tail tokens; the deliberative register checks itself. | 6 of 6 (carried) | 5 / 0 / 1 | +8.84 | survives, 1 strike of 5 held-out claims | beats rival, +13.20 (6 tests, 1 separating) | weak | Fresh rival (a stopping and last-marker grading failure) fails: 0.8 % of the plain base's wrong non-self-opened answers have a right first marker (n 260), run-on share 0.089 (n 259). Weak because one test separates (n 25), the defender missed 5 of 6 intervals, the Wait/Hmm tests are confounded with late self-opening, and its own temperature prediction missed (0.158 against 0.29). |
| r6-account | Six ordered rules split the problems an RL-side model gets right and the base side wrong: loop, budget, answer-statement, slip, sharpening, reach; one null cell (cued base against another cued-base sample). | 44 of 44 | 43 / 1 / 0 | +35.41 | survives, 0 strikes of 5 | loses to rival, -3.11 (5 tests, 0 separating) | weak | Shares of the 65 RL-only problems on MATH-500 at T 1.0: budget 0.246, slip 0.185, sharpening 0.446, reach 0.092, answer-statement 0.031, loop 0; the null cell (46 problems) has 0.152, 0.261, 0.478, 0.065, 0.043, 0. Plain base against RL (247 problems): answer-statement 0.514. At min-p 0.1 loop is 0.406, at T 0.6 0.52-0.57. Rival: no RL-specific finishing policy, one difficulty axis; its win is one test (-2.14). |
| r6-m11 | The cued base often writes its answer marker early and then justifies it; these early commitments are wrong more often. | 2 of 3 | 1 / 0 / 1 | -0.32 | refuted (own test) | | | Of the cued base's quick finished-wrong answers, 0 of 13 are early-marker answers (predicted 0.45). p1 not scored: differs from its replication. |
| r6-m01 | The cued base's deliberative register fades with distance from the cue; long answers slide into textbook continuation. | 3 of 3 | 2 / 0 / 1 | -1.14 | refuted (own test) | | | 0.7 % of hard328 base answers of at least 12,000 tokens have a textbook header in their second half (n 136; predicted 0.25). |
| r6-m04 | On base + a(Think-SFT - base) the length policy arrives at a small dose, so intermediate models hit the cap more than either end. | 3 of 3 | 1 / 1 / 1 | -3.52 | refuted (own test) | | | No cap-hit bump (-2 against the endpoints); at a = 0.25 only 0.065 of the log length change has arrived (predicted 0.8). |
| r6-m10 | The first 100 RL steps install the opening, format and length; the lower error rate on finished answers comes after step 400. | 3 of 3 | 1 / 0 / 2 | -3.79 | refuted (own test) | | | Step 100's finished answers are already 4.6 points more often right than the cued base's on the same problems (n 345, 90 % [-6.7, -2.6]). |
| r6-m05 | RL's extra 'Wait' and 'Hmm' come from a timer: their excess grows with the text since the last stated result. | 3 of 3 | 0 / 1 / 2 | -4.24 | refuted (own test) | | | The RL/base hold-on ratio far from a result over near it is 0.97 (predicted 1.7); near a result it is already 1.38. |
| r6-m06 | The cued base's wrong steps come from head tokens; RL's text has as many p < 0.01 tokens as the base's. | 0 of 3 | | | untested | | | The stored hard328 rows have no per-token probability field. |

GPU predictions, none run: r6-account, a vote over 9 cued-base samples on MATH-500 (one new sample, 35 H100 minutes): 456 [449, 462] of 500.
r5-m03 (round 05), base + top8 + cue on MATH-500, 425 [412, 438]: still not measured.

## Round 07 (2026-11-15, cutoff 11-15 09:09:43 UTC, coordinator frustea, plan by abaybektursun)

Plan `specs/SPEC_round07.md`, engine version 7.1 unchanged, no account. Taken over as work-466a39 after work-8fd317 was silent for 86 minutes.
One run, exit 0, 37 headless jobs, 55 minutes, no GPU (`results/engine/round-07/run.json`, log `round07.log`, examples `examples.json`,
ranked experiments `experiments.md`).

**Result: no theory stands and no new theory survives. Of 12 mechanisms 5 were abandoned by their developers; of the 7 developed, 2 are
refuted by their own predictions and 5 gain nothing over the no-theory readers (total gain -0.30 to -4.00 nats). 24 of 27 offline predictions
computed: 16 inside, 6 outside within noise, 2 outside. The carried r5-m03-rival stays "not separated from rival" (1 separating test of 6),
review "weak". The experiments stage found 1 open experiment, on which both sides predict the same count (450 of 500), below the best known
base-only count (454).**

Hypotheses of the spec: G1 holds (55 minutes; round 06: 125). G2 refuted (5 of 12 abandoned). G3 refuted (no duel with 2 separating tests).
G4 refuted (no change to the base predicted above the best known count). G5 refuted (no carried theory wins a duel).

| Theory | Statement | Tests computed | In / noise / out | Gain (nats) | State | What decided it |
|---|---|---|---|---|---|---|
| r5-m03-rival | The top-8 edit is an incomplete switch per sample (carried). | carried | | | survives; not separated from rival; review weak | One separating duel test of 6; its "whatever the difficulty" clause is contradicted by duel tests p4 and p5. |
| r6-account-rival | No RL-specific finishing policy: cap hits are the hard end of one difficulty axis (carried). | carried, 5 | 5 / 0 / 0 | | no gain | Total gain above 0, but no prediction won where the readers were outside its interval. |
| r7-m03 | Many of the cued base's arithmetic slips are single T 1.0 draws of a wrong number token; cooling removes them. | 4 of 4 | 2 / 1 / 1 | -2.44 | refuted (own test) | The self-inconsistent-equation rate at T 1.0 is 0.36 times the rate at T 0.6 (n 377; predicted 3). |
| r7-m12 | RL-written examples in context help only on problems of the examples' subject. | 3 of 3 | 2 / 0 / 1 | -2.74 | refuted (own test) | Same-subject minus other-subject gain is -0.018 (n 223, 90 % [-0.058, 0.022]; predicted +0.08). |
| r7-m05 | The cued base's misread and slip steps are what its language prior writes for a generic problem of the kind. | 3 of 3 | 2 / 1 / 0 | -0.30 | no gain | Inside, but the readers predicted the same. |
| r7-m08 | Code-RL 3.1 raises accuracy by lowering the base's own misread and slip steps, without replacement tokens. | 3 of 3 | 3 / 0 / 0 | -0.52 | no gain | Groups of 16 to 33 items; intervals too wide to gain. |
| r7-m11 | The cued base's wrong value is set by the shared prompt and opening, so wrong answers under one opening agree. | 3 of 3 | 2 / 1 / 0 | -1.09 | no gain | p2 0.164 against 0 predicted, within noise (n 28). |
| r7-m07 | The 3.0 RL-Zero releases learned to stop before about 12k tokens and close long problems early and unchecked. | 4 of 4 | 3 / 1 / 0 | -1.84 | no gain | p3 -0.371 against -0.12 predicted (n 80). |
| r7-m09 | Think-SFT's excess wrong answers on easy problems are final formats that grader v3 rejects. | 4 of 4 | 2 / 2 / 0 | -4.00 | no gain | Groups of 6 to 9 items. |
| r6-m06 | (carried untested) | 0 of 3 | | | untested | The stored rows still have no per-token probability field. |

## Forecast runs

Every unrefuted theory of the newest round (at most 6, survivors first, then by total gain) and two readers with no
theory forecast the numbers the open `work` items will report, before they post. Code `lib/forecast.py` (imports the
job runner and the log density from `lib/round.py`), prompts `lib/prompts/forecast_targets.md`, `forecast.md`,
`forecast_score.md`.

```
uv run studies/theory/lib/forecast.py make studies/theory/results/forecast/run-<nn>   # fails if the folder exists
uv run studies/theory/lib/forecast.py score studies/theory/results/forecast/run-<nn>  # rerun as results post
```

`make` writes `targets.json` (item id, cell, unit, quote), `forecasts.json`, `forecasts.md` (one table per target),
`run.json` (commit, command, board snapshot time). `score` reads only items posted after the snapshot and writes
`scores.json` (measured value, item, quote per target; gain per forecast against the equal mixture of the two readers,
clipped to [-3, 3] nats) and `scores.md`. Job dirs (prompts, outputs) are under the temp folder in `run.json`.

**run-01** (plan `specs/SPEC_forecast01.md`; snapshot 2026-11-15 14:45:56 UTC; `results/forecast/run-01/`): 20 targets
from 7 open work items (RL step 100, vote over 9 and 12, cap 32,768, transplant a = 2, 1.5x edit replication,
autobench, fresh2026); forecasters reader-1, reader-2, r5-m03-rival, r6-account-rival, r6-m06, r7-m05, r7-m08,
r7-m11. The theories forecast 1 to 3 targets each (r6-m06: none); the rest "theory says nothing". F1 holds (20 targets).
First score (14:50:25 UTC, `scores.md`): 6 of 20 measured, all fresh2026 (result-5251c9). No theory forecast any of
them, so F2 is not decided. reader-2 has all 6 inside its interval (mean gain +0.30 nats), reader-1 4 of 6 (-0.77).
F3 is refuted at this score (every measured value inside some interval) and is checked again as the other 14 post.
Second score (15:03:15 UTC): 9 of 20 measured (adds t10-t12, the 1.5x edit replication, result-95a4dc: 200.25, 214, 456).
r5-m03-rival 3 of 3 inside, +1.83 nats (mean +0.61, only 3 targets); reader-2 9 of 9 inside, +2.14; reader-1 6 of 9,
-5.12. No value outside every interval.

**run-02** (plan `specs/SPEC_forecast02.md`; `make ... --propose 6`; snapshot 2026-11-15 14:53:16 UTC;
`results/forecast/run-02/`; `run.json` names commit 46875c7, the `--propose` code was committed after the run in the
same commit as the run folder): 17 targets from 8 open work items, the fresh2026 numbers of result-5251c9 left out.
Forecasters as in run-01 plus 6 mechanisms written about the targets (`mechanisms.json`, one job, 595 s): all 6 passed
the checks on the first draft (P1 holds). Each forecasts 9 or 10 targets and lies outside both readers' intervals on
exactly 3 (`forecasts.md`). The engine's theories forecast 0 to 3 of 17. First score: 3 of 17 measured (t10-t12,
result-95a4dc). f2-m03 (the 8 directions set only when the base stops) was outside both readers on all three and wrong
on all three (-7.07 nats); f2-m05 wrong on its one (t10). P3 so far: 0 of 4 disagreements right (needs 8 to decide).
P2 not decided.

## Theories

Status after round 04. Full text in `results/engine/round-04/theories/<name>.json` for the round-04 theories, in
`results/engine/round-03/theories/<name>.json` for the round-03 and carried theories, and in
`results/engine/round-02/theories/<name>.json` for the others (`r1-*` are round 01's files, unchanged). Round-02
score from `round-02/metrics_v2.json`; round-03 result from `round-03/metrics_v3.json` (claims, total gain in nats,
90 % interval, state; then the largest wrong claim, measured value from `round-03/targets.jsonl`); round-04 result from
`round-04/metrics_v4.json` (offline predictions computed, inside / outside, total gain in nats against the two test readers,
state); verdicts from `round-02/reviews/`, `round-03/reviews/` and `round-04/reviews/`; rival-stage results from `round-04/metrics_v5.json`. Only the 4 carried theories and the 10
new ones were scored in round 03. Round 04 carried no earlier theory (all 32 went to its mechanisms agent as `graveyard.json`),
so the rows before r4-* are unchanged; the round-04 GPU predictions are in the Round 04 section.

| Theory | Statement | Round | Round-02 score (wins, losses, state) | Review | Round-03 or round-04 result | Status |
|---|---|---|---|---|---|---|
| r1-all-1 | The cued base has RL's per-step skill; the gap is the base degrading as its own long solution grows, which RL repaired by training truncated rollouts as failures. | 01 | 2, 1, passes | refuted | not carried (refuted) | refuted |
| r1-all-2 | Most of the RL gain is one answer-mode switch (deliberate, box the answer, stop), stored redundantly along a diffuse direction, so any small unbiased fraction of the delta flips it. | 01 | 3, 2, passes | none | 12 claims, +2.62 [-3.81, 7.98], fails; RL-Zero-Mix plain claim 438, measured 372 | fails |
| r1-across-1 | The base's loops and cap hits come from early-to-mid-layer circuits that copy its own earlier text; RL's cap-hit gain weakens that pathway in layers 0-15. | 01 | 2, 2, fails | none | not scored | fails |
| r1-across-2 | RL's lead is a learned token-budget controller, trained because 3.1 scores truncated rollouts as failures; it is not new math skill. | 01 | 1, 1, fails | none | not scored | fails |
| r1-surprises-1 | The gain is a general deliberation shift that the cue, Code-RL and 3.0 share, plus stopping calibration that only 3.1 learned; the cued-base gap is the second part. | 01 | 0, 0, fails | none | not scored | fails |
| r1-surprises-2 | The working part of the weight change is low-rank and near-linear; the high-rank remainder, which holds most of its energy, is optimizer noise. | 01 | 3, 2, passes | none | 8 claims, -4.60 [-13.80, 4.96], fails; WSP-1 claims wrong (RL minus top-8: 55 vs 91; bulk64: 50 vs 86) | fails, predictions wrong |
| r2-all-1 | The delta acts through coherent signs along high-curvature directions, about 700 times a random direction; unbiased resampling keeps the gain, random signs remove it, SFT deltas break. | 02 | 0, 1, fails | none | not scored | fails |
| r2-all-2 | Base accuracy at a sampler setting depends on the per-token surprise of its text (too low: loops; too high: drift); the cue lowers entropy, so truncation hurts the cued base. | 02 | 2, 0, passes | weak | 0 claims, fails | weak, untested in round 03 |
| r2-surprises-1 | Loops and slips are two ends of one axis, the per-token surprise of sampled text; the cue lowers entropy, RL sits far from both ends, and raising surprise cuts loops. | 02 | 0, 1, fails | none | not scored | fails |
| r2-surprises-2 | The base and optimizer set which entries move, and how far; the task is written only in the signs, which act on any math text and leave general text alone. | 02 | 0, 1, fails | none | not scored | fails |
| r2-across-1 | The weight change lowers next-token entropy only at the base's high-entropy fork tokens, so RL ignores temperature while the base loops when cooled and errs when heated. | 02 | 1, 1, fails | none | not scored | fails |
| r2-across-2 | The delta's effect sits in its coherent sign pattern, with hundreds to thousands of times a random direction's Fisher curvature; DARE fails near keep 0.01-0.05 %. | 02 | 3, 2, passes | weak | 7 claims, -3.20 [-10.49, 3.83], fails; WSP-1 claims wrong (top-8 alone: 58 vs 88 of 100, 305 vs 427 of 500) | fails, predictions wrong |
| r2-external-1 | The delta moves output 700 times more per unit energy than a random direction; DARE holds to keep 0.1 % and collapses near 0.01 %; random weight noise reduces loops. | 02 | 1, 1, fails | none | not scored | fails |
| r2-external-2 | One global temperature acts on two kinds of positions: low temperature starts loops at rare fork tokens, high temperature causes slips elsewhere; a per-position temperature would fix the base. | 02 | 1, 2, fails | none | not scored | fails |
| r2-revise-1 | Accuracy is carried by the dense sign pattern of many small entries; an edit recovers accuracy in proportion to the share of it kept; Code-RL gives no math gain. | 02 | 1, 0, fails | none | not scored | fails |
| r2-revise-2 | The cued base's gap is a weak error detector, not weaker per-step math: RL notices and re-derives errors more often, so a 4-sample vote closes about half the base's gap. | 02 | 0, 0, fails | none | not scored | fails |
| r3-across-1 | The RL delta has a general reliability part, shared with Code-RL and saturated at a = 0.25, and a dose-growing math part needed only on problems the base rarely solves. | 03 | | none | 6 claims, -0.35 [-2.64, 1.67], fails; Code-RL hard328 claim 176, measured 187 | fails |
| r3-across-2 | The cued base leaves loops only through low-probability tail tokens that T < 1 and truncation delete; RL adds a constant push toward probable 'Wait'/'Hmm', so it ignores temperature. | 03 | | weak | 1 claim, +0.67, reversal +0.29, passes; offline tests 3 not computed (S3 403) | weak (1 claim, tests not computed) |
| r3-all-1 | RL's gain over the cued base is two stopping habits: a general commit-and-box habit (Code-RL shares it, a = 0.25 holds it) and a math-specific check-before-stopping habit for long problems. | 03 | | none | 4 claims, -2.67 [-5.65, 0.42], fails; Code-RL hard328 claim 173, measured 187 | fails |
| r3-all-2 | On hard problems the base spreads probability at progress steps; low temperature turns the spread into self-reinforcing loops, T 1.0 into wrong turns; RL is concentrated, so temperature barely matters. | 03 | | none | 3 claims, -1.36 [-3.27, 0.56], fails | fails |
| r3-external-1 | Over-truncated sampling sends a pretrained-style policy into repetition basins; 3.1, trained at exact T 1.0 with truncated rollouts as negatives, suppressed them, so 3.1 ignores temperature and 3.0 does not. | 03 | | none | 2 claims, -1.43 [-3.78, 0.91], fails | fails |
| r3-external-2 | The delta is an early sharpening part, overshot several-fold and fully expressed at a = 0.25, plus a late part, growing with a, that solves what the base rarely solves. | 03 | | none | 11 claims, -7.95 [-16.47, 0.15], fails; RL-Zero-IF claim 436, measured 377 | fails |
| r3-revise-1 | The RL-Zero gain is a general 'deliberate, then commit' part (every RL-Zero delta has it, saturated at a = 0.25, replaceable by the cue) plus a math-specific part linear in a. | 03 | | none | 11 claims, -2.69 [-10.17, 4.07], fails; RL-Zero-IF and Code 3.0 claims 444, 446, measured 377, 411 | fails |
| r3-revise-2 | A loop is an absorbing hazard that opens at impasses; T 0.6 traps finishable medium-length solutions, while at T >= 1 only fixed long, mostly lost problems loop. | 03 | | none | 0 claims, fails | fails |
| r3-surprises-1 | The cued base's T 1.0 deficit is low-probability tail tokens that derail steps, adding up with length; RL shrinks the tail; label-free tail cuts also remove loop escapes, netting zero. | 03 | | none | 4 claims, -0.24 [-1.67, 1.18], fails | fails |
| r3-surprises-2 | Any outcome-reward RL delta has a shared low-dose part gating settle, verify and stop (saturated at a = 0.25) and a math-specific part paying only on long, hard problems. | 03 | | none | 11 claims, -4.35 [-12.14, 2.47], fails; RL-Zero-IF and Code 3.0 claims 440, 445, measured 377, 411 | fails |
| r4-m10 | Early RL (steps 100-400) lowers entropy, so T 0.6 / top-p 0.95 sampling loops more and cap hits rise above the base's; truncation-as-failure training later removes the loops. | 04 | | weak (entropy mechanism untested; length growth gives the same counts) | 4 of 5 computed, 4 in / 0 out, +9.86, survives; cap hits base 65, step 100 103, step 400 98 of 500; rival stages, both turns: loses to rival, -7.81 on 6 tests (rival: step 100 installs the cue's opening, 478 of 500; steps 100-400 no sharper than the cued base) | loses to rival; entropy step refuted on stored rows |
| r4-m01 | The cued base's T 0.6 loops feed on its own text: loop hazard grows with how compressible (zlib) the text so far is; the base finishes from RL's prefix because RL's text is less self-similar. | 04 | | weak (gain is one descriptive test; core partly published) | 3 of 4 computed, 3 in / 0 out, +1.41, survives; held-out strikes 0 of 3; rival stages, both turns: not separated from rival, +1.11 on 5 tests (turn 1 +4.43, turn 2 -3.32) | not separated from rival |
| r4-m08 | Part of the cued base's accuracy is recall from pretraining, so at matched difficulty the RL-minus-base gap is larger on problems published after the base's data cutoff. | 04 | | weak (only gain from 60 problems; distinctive test opposite sign) | 3 of 3 computed, 3 in / 0 out, +0.12, survives; p2 +0.143, predicted -0.3 [-0.9, 0.15]; rival stages, both turns: loses to rival, -2.65 on 5 tests (T 0.6 excess -5.6 points) | loses to rival |
| r4-m12 | Part of the hard328 gap is grader v3 false negatives on the base's equivalent but non-canonical answers to non-integer problems; RL writes canonical forms. | 04 | | none | 1 of 4 computed, 1 in / 0 out, -0.32, untested (3 need sympy's LaTeX parser) | untested, carried to round 05 |
| r4-m06 | RL added a constant hold-on bias and no error detector, so it re-checks right and wrong intermediate answers at the same added rate. | 04 | | none | 0 of 3 computed (math_verify missing), untested | untested, carried to round 05 |
| r4-m11 | The cued base often keeps writing after its answer and states a new one; the last-marker grader scores the later one, so part of its MATH-500 deficit is a stopping artifact. | 04 | | none | 0 of 5 computed (math_verify missing), untested | untested, carried to round 05 |
| r4-m02 | Within a problem, a longer finished base sample means abandoned attempts, so length reads out failure for the base; RL's extra tokens are habitual checks, so RL length carries little signal. | 04 | | none | 3 of 3 computed, 2 in / 1 out, -3.76, refuted; RL concordance 0.718, predicted 0.55 [0.43, 0.67], bound 0.68 | refuted (within noise of the bound) |
| r4-m04 | base + a(RL - base) is a per-answer mixture of the two endpoint modes, so the RL share implied by accuracy also shows in 'Wait' rate, format and boxed accuracy. | 04 | | none | 4 of 4 computed, 2 in / 2 out, -5.28, refuted; 'Wait'-rate share 0.327 plain, predicted 0.76 [0.60, 0.90] | refuted |
| r4-m09 | Code-RL 3.1's math gain is only an ending policy (finish under the cap with one answer, then stop); it adds nothing where the base finishes wrongly. | 04 | | none | 6 of 6 computed, 3 in / 3 out, -6.70, refuted; hard328 Code fixes 27 of 90 base finished-wrong, predicted 0.15 [0.07, 0.25] | refuted (within noise of the bounds) |
| r4-m07 | Base wrong answers are shared attractors plus scattered slips; RL removes the slips and keeps the attractors, so RL's wrong answers mostly equal the base's. | 04 | | none | 5 of 5 computed, 0 in / 5 out, -12.65, refuted; 35 of 131 RL wrong answers equal a base wrong answer, predicted 0.50 [0.36, 0.65] | refuted |

Round-01 forward predictions of idea-0b2ad8 that have been measured (`round-02/reviews/r1-all-1.json`,
`forward_predictions_measured`):

- P1, base + 0.5*(RL - base), cue, T 1.0, hard 328, cap hits: measured 73 of 328, with 190 right (result-e45bf4;
  `studies/rlneurons/results/day1_wdiff328/readout.json`, cell `theta0.5_cue`). Outside r1-all-1's 45 [30, 60], inside
  the planted reversal's 72 [60, 85]. r1-all-1's own rule (refuted if cap hits stay at 70 or more while accuracy rises
  above 175) is met.
- P2, stored T 1.0 MATH-500 answers of cued base and RL cut at 4,096 generated tokens, RL minus cued base: -9.2 points
  [-13.0, -5.4] (base 337, RL 291 of 500). Inside r1-all-1's -7 [-14, 0], outside the planted reversal's +7 [0, 14]. Not
  a board item: the reviewer computed it from `studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json` as right
  and generated tokens <= 4,096, which counts wrong an answer that boxed its answer before token 4,096 but kept writing.
  It follows from RL writing longer answers (result-5e17a6) and does not separate the mechanisms.

P3 to P6 have no measurement in this record (P3: not measured by the team, per the same review).

Page of the engine's record: `tools/finding_theories_on_trial.py`, served at `/finding/theories-on-trial`: every prediction of every round as one mark (interval and measured number) against the readers with no theory. After a new round: `uv run tools/finding_theories_on_trial.py --write`, then the check, then names for the new theories in NAMES.

Page of the self-opened draw (selfopen-01): `tools/finding_base_opens_itself.py`, served at `/finding/base-opens-itself`; running the file checks it against `results/experiments/selfopen-01/`.

Page of the gap account (run-02): `tools/finding_where_the_gap_goes.py`, served at `/finding/where-the-gap-goes`; its numbers are read from `results/account/run-02/check/` and `python3 tools/finding_where_the_gap_goes.py` checks them.
