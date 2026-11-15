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

**cell-m20-01** (cells-01 entry m20, readout `m20-r1`; plan `specs/SPEC_cell_m20.md`; board idea-e9dfd5, work-a68dfd, result-a74ac3). The
untrained base (`allenai/Olmo-3-1025-7B` @ `a81bae42`), plain prompt (no opening cue), fresh2026 (136 problems), 1 sample, T 1.0 / top-p 1.0,
seed 93,000,000 + index, cap 16,384, grader v3. **10 of 136** (90 % bootstrap [5, 15]), 13 cap hits, 4,732 generated tokens per problem
(median 1,661), 44 answers with no extractable answer. With the cue the base gets 28, 28, 32, 30 per sample on the same problems. The
training-data forecasts (run-06/f2-m02 3 [0, 8], run-06/f2-m06 2 [0, 7]) are refuted; the problem-structure and grader forecasts
(run-07/f2-m06 16 [9, 23], run-08/f2-m01 14 [8, 20]) and both readers (14, 13) hold, all with centres above 10. Raw answers: 23 of 136 open
with "Okay" in their first 60 characters on their own (6 right, 7 cap hits, 11,207 tokens on average); the other 113 are short (3,414 tokens),
often off-format (code, "Answer:\n173" with no box, instructions to the reader) and give 4 right.
- Files: `analysis/cell_m20.py` (readout); outputs `results/experiments/cell-m20-01/` (`run.json` with job and commit, `metrics.json`,
  `per_problem.json`, `examples.json`); the count is in `results/forecast/cells-01/measured.json`.
- Job `abaybektursun-1115-093940-3d06` (vast.ai, commit `1a004c1`, command in `run.json`; a 4-problem 256-token smoke run first, in
  `smoke/`). Raw answers (not committed): `runs/abaybektursun-1115-093940-3d06/` on the laptop of the run and `jobs/<job-id>.tar` in the
  team store.

**cell-m06-01** (cells-01 entry m06, readout `m06-r1`; plan `specs/SPEC_cell_m06.md`; board idea-e9dfd5, work-844e38, result-9ce8ed).
`allenai/Olmo-3.1-7B-RL-Zero-Math` at step 100 (revision `0a45720c`, loaded with `--model-path` as in the ckptcue cells), plain prompt, the
first 164 problems of hard328 (`--n 164`), 1 sample, T 1.0 / top-p 1.0, seed 3,000,000 + index, cap 16,384, grader v3. **m06-r1 (finished,
wrong, at most 2,000 generated tokens): 7 of 164** (90 % bootstrap [3, 11]); 3 of the 7 are empty or 9-token answers. run-06/f2-m02 6 [2, 12]
and run-05/f2-m04 8 [3, 16] hold; run-03/f2-m06 26 [15, 38] and both readers (20 [9, 34], 22 [10, 36]) are refuted. Right 67 of 164 [57, 77],
37 cap hits, 10,340 generated tokens per problem. Same problems and seeds from stored rows (`rlneurons/results/day1_3/`, sample 0): base + cue
65 right, 53 cap hits, r1 1; final RL plain 84 right, 26 cap hits, r1 0. Raw answers: 126 of 164 open with "Okay" in their first 30
characters (49 right, 31 cap hits); the 38 that do not are mostly long (median 8,814 tokens; 18 right, 6 cap hits, 5 quick wrong), some
derail into off-topic text. The 37 cap hits have no loop (loop_A 0): they are still reasoning at 16,384 tokens.
- Files: `analysis/cell_m06.py` (readout); outputs `results/experiments/cell-m06-01/` (`run.json` with job and commit, `metrics.json`,
  `per_problem.json`, `examples.json`); the count is in `results/forecast/cells-01/measured.json`.
- Job `abaybektursun-1115-093138-81b3` (vast.ai, commit `4e80803`, command in `run.json`; a 4-problem smoke run first,
  `abaybektursun-1115-092454-12d1`, 4 of 4 right). Raw answers (not committed): `runs/abaybektursun-1115-093138-81b3/` on the laptop of the run
  and `jobs/<job-id>.tar` in the team store.

**cell-m29-01** (cells-01 entry m29, readout `m29-r1`; plan `specs/SPEC_cell_m29.md`; board idea-e9dfd5, work-290625, result-d82083).
`allenai/Olmo-3-1025-7B` @ `a81bae42` + 2 x the top 8 singular directions per matrix of (`allenai/Olmo-3.1-7B-RL-Zero-Math` @ `364820b0` -
base), written by `rlneurons/jobs/wsp_edit.py --recipe top8 --other math31 --scale 2 --rounding stochastic --seed 0`; opening cue, MATH-500
(500), 1 sample, T 1.0 / top-p 1.0, seed 3,000,000 + index (the seed of the 1.5x cell; cells.md wrote 105,000,000), cap 16,384, grader v3.
**448 of 500** (90 % bootstrap [437, 459]), 2 cap hits, 4,369 generated tokens per problem, 2 answers with no extractable answer. Paired with
the 1.5x cell on the same seeds (`rlneurons/results/xreward/dial15_math500-01/`, 456): -8 problems [-16, 0], 17 right only at 1.5x, 9 right
only at 2x. run-07/f2-m01 423 [410, 436] is refuted; run-04/f2-m06 455, run-05/f2-m01 449, run-05/f2-m02 455, run-08/f2-m01 450,
r5-m03-rival 449 and both readers (445, 448) hold. Raw answers, 10 of the 52 wrong read: 6 finish with a confident structured write-up and a
wrong boxed answer, 2 decay into word salad (problems 100, 103), 1 hits the cap while rechecking (problem 9), 1 is a format miss (`E` for
`east`). The edit's added norm equals the stored hard328 2x edit (2.538); the written norm differs in the fourth digit because the stochastic
rounding draws differ on another GPU.
- Files: `analysis/cell_m29.py` (readout, paired against the 1.5x rows); outputs `results/experiments/cell-m29-01/` (`run.json` with job and
  commit, `metrics.json`, `per_problem.json`, `examples.json`); the count is in `results/forecast/cells-01/measured.json`.
- Job `abaybektursun-1115-094140-e5b5` (vast.ai, commit `620faa0`, command in `run.json`; a 4-problem 1,024-token smoke run first,
  `abaybektursun-1115-092654-c975`, 2 of 4 right). Raw answers (not committed): `runs/abaybektursun-1115-094140-e5b5/` on the laptop of the
  run and `jobs/<job-id>.tar` in the team store.

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

**top8x4-01** (idea-7ca1fe, work-22359d; plan `specs/SPEC_top8x4.md`, written before any new row). Base + 1x the top-8 singular
directions per matrix of the RL-Math weight change (`rlneurons/jobs/wsp_edit.py --recipe top8`), plain prompt, MATH-500, T 1.0 /
top-p 1.0, cap 16,384, grader v3. 3 new samples per problem (seed 187,000,000 + 10,000 s + index) plus the stored sample of
`rlneurons/results/wsp1/full500/top8_plain-01/`: 4 per problem, 2,000 samples. Short = 1,000 generated tokens or fewer. Solve bin =
right answers of 4 of the cued base (`rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl`, attempt 0; bins 0-4 hold 33, 24, 28,
98, 317 problems). **The smooth-blend prediction holds and the top-8 switch prediction (r5-m03-rival) is refuted: short samples are
right 87.2 % of the time where the cued base solves 4 of 4 (252 of 289), and 81 % of short samples sit in that bin, which holds 63 %
of all samples.**
- Right per sample: 427 (stored), 426, 429, 445 of 500; cap hits 12, 14, 9, 13; mean tokens 3,962, 4,037, 3,810, 4,046.
- Short share 17.8 % [15.7, 20.0] (356 of 2,000; 90 % bootstrap over problems). Predicted 10-15 % (P1a refuted).
- Short accuracy 82.9 % [79.2, 86.2] (295 of 356). Predicted about 50 % (P1b refuted).
- Short accuracy by bin 0-4: 0 of 5, 0 of 2, 8 of 14, 35 of 46, 252 of 289 (87.2 %): it rises with the bin, not flat (P1c refuted).
  Long accuracy by bin: 34 of 127, 64 of 94, 66 of 98, 310 of 346, 958 of 979 (97.9 %).
- Short samples per problem (0-4): 318, 88, 42, 24, 28 problems. 30.8 % of all problems have both a short and a long sample;
  84.6 % of the 182 problems with a short sample also have a long one (P1d holds: short and long samples do share problems).
- Thresholds: at 600 tokens 6.7 % short [5.7, 7.9], 62.7 % right (84 of 134), bin 4 71.0 % (76 of 107), bins 0-1 0 of 5; at
  1,500 tokens 32.1 % short [29.3, 34.8], 89.2 % right (572 of 641), bin 4 92.3 % (488 of 529), bins 0-1 1 of 9. The 85 % line in
  bin 4 holds at 1,000 and 1,500 tokens and fails at 600.
- What the switch theory keeps: on bin-4 problems short samples are wrong 12.8 % of the time against 2.1 % for long ones. Of 44
  short wrong new samples, 26 have no extracted answer (12 are empty, 2 tokens or fewer) and others continue the prompt, write code
  with an invented output or a template without an answer (10 short samples read by hand): the plain base's formats, not wrong
  math. One (`Answer: cot x`, gold `\cot x`) is scored wrong by v3 although it is right.
- Caveat: the stored sample ran on an H100 and the new ones on RTX PRO 6000 boxes; the edit's `add_norm` is identical and its
  BF16 stochastic rounding differs in the 6th digit of the written norm. Sample 0 alone gave the same picture (18.4 % short,
  81.5 % right, bin 4 86.3 %).
- Files: `analysis/top8x4.py` (readout; without `--runs` it reads the stored sample alone); outputs `results/experiments/top8x4-01/`
  (`run.json` with the job ids, `metrics.json`, `per_problem.json`, `examples.json`: one short right and one short wrong new sample).
- Raw generations (not committed): `runs/abaybektursun-1115-085111-e8c2`, `runs/abaybektursun-1115-085127-c0c4`,
  `runs/abaybektursun-1115-085134-75f7` in the worktree `iterate-hack-top8x4` of the run, and `jobs/<job-id>.tar` in the team store.

**cell-r9-m21-01** (round-09 entry m21, readout `m21-r1`; plan `specs/SPEC_cells_r9b.md`; board work-ef61c7, result-ac7104). Base + 1.0 x
the top 8 singular directions per matrix of (Olmo-3.1-7B-RL-Zero-Code - base) (`rlneurons/jobs/wsp_edit.py --recipe top8 --other
rl_code --scale 1.0 --rounding stochastic --seed 0`), plain prompt, MATH-500 first 250 problems, T 1.0 / top-p 1.0, seed 64,000,000 +
index, cap 16,384, grader v3. **Quick wrong answers (1,000 generated tokens or fewer, finished, v3 wrong): 60 of 250** (90 % bootstrap
[49, 71]). Only run-05/f2-m06 (45 [28, 64]) holds; the other ten forecasts are refuted, all from below: both readers (25 [10, 45],
18 [8, 32]), run-05/f2-m03 (40 [24, 58]), and the stopping forecasts run-03/f2-m02 (14 [7, 23]) and round-09/stopping-m06 (15 [8, 24]).
- Right 157 of 250, 4 cap hits, 2,674 generated tokens per problem (median 1,088). On the same 250 problems: plain base (T3) 107 right
  and 105 quick wrong; base + the Math 3.1 top-8 directions, plain (`rlneurons/results/wsp1/full500/top8_plain-01/`), 217 right and
  9 quick wrong; matched random rank-8, plain, 100 and 104. The Code directions move both numbers about halfway from the plain base
  to the Math directions.
- Raw answers: 103 of 250 open with "Okay" in their first 60 characters. Short answers (121, at most 1,000 tokens) are right 61 times;
  long ones (129) 96 times. Of the 60 quick wrong answers 35 have no extracted answer and 14 are 5 tokens or fewer (10 empty); the
  rest are the plain base's formats (instructions to the reader, a multiple-choice template, Python with no output, `Answer: $Answer$`)
  or short worked solutions with a slip. One (problem 0, `$(3, \frac{\pi}{2})$` followed by a note) is right and scored wrong by v3;
  it is the stored wrong example.
- Files: `analysis/cells_r9b.py` (readout); outputs `results/experiments/cell-r9-m21-01/` (`run.json` with job and commit,
  `metrics.json`, `per_problem.json`, `examples.json`); the count is in `results/wide/round-09/measured.json`.
- Job `abaybektursun-1115-103050-eae1` (commit `cd2f8d0`, command in `run.json`; a 4-problem 256-token smoke run first, in `smoke/`).
  Raw answers (not committed): `runs/abaybektursun-1115-103050-eae1/` in the worktree `iterate-hack-cells-r9b` and
  `jobs/<job-id>.tar` in the team store.

**cell-r9-m18-01** (round-09 entry m18, readout `m18-r1`; plan `specs/SPEC_cells_r9b.md`; board work-ef61c7, result-ac7104). Base +
0.125 x (RL-Math 3.1 - base), whole difference, stochastic BF16 rounding (`rlneurons/jobs/merge_weights.py --other rl --alpha 0.125
--rounding stochastic`; effective alpha 0.12502), plain prompt, MATH-500 all 500, T 1.0 / top-p 1.0, seed 61,000,000 + index, cap
16,384, grader v3. **316 of 500 right** (90 % bootstrap [298, 334]). Held: run-05/f2-m06 (300 [260, 340]), round-09/sampling-m03
(308 [272, 342]), run-03/f2-m02 (330 [280, 375]), round-09/stopping-m06 (345 [295, 390]), reader-1 (355 [315, 392]). Refuted:
round-09/problems-m03 (395 [365, 420]), round-09/weights-m06 (365 [330, 400], the saturating plain curve), reader-2 (362 [320, 400]).
- 15 cap hits, 3,076 generated tokens per problem (median 1,432). References with the plain prompt on the same 500: base (T3) 224,
  theta 0.25 405, theta 0.5 443, RL 463 (`rlneurons/results/day1_wdiff/`). The step from alpha 0 to 0.125 (+92) is about half the
  step from 0 to 0.25 (+181).
- Even-index half 153 of 250 (plain base 113 on the same problems), odd-index half 163.
- Raw answers: 221 of 500 open with "Okay" in their first 60 characters. Of the 184 wrong answers 108 are quick wrong (1,000 tokens
  or fewer, finished) and 62 finished answers have no extracted answer, against 199 quick wrong for the plain base. Read by hand
  (10): wrong ones are empty answers, instructions to the reader, a "Cues & Strategy Menu" template, Python with no output, a
  conclusion "no such number exists" after 142 tokens, and long "Okay, let's ..." derivations that end on a wrong value (8,392 and
  15,866 tokens); right ones are either short step lists (problem 3, 485 tokens) or "Okay" derivations (problem 1, 2,190 tokens).
- Caveat: shard 1/2 was cut off at 247 of 250 rows when its machine stopped; the shard was rerun whole at the same commit and the
  rerun is the stored half. The two runs share seeds but not generations (52 of 247 texts identical, scores agree on 222): 155 right
  in the cut-off run against 162 in the rerun on the same 247.
- Files: `analysis/cells_r9b.py` (readout; joins the shards with `rlneurons/analysis/shard_join.py`); outputs
  `results/experiments/cell-r9-m18-01/`; the count is in `results/wide/round-09/measured.json`.
- Jobs `abaybektursun-1115-103513-3558` (shard 0/2, with a 4-problem 256-token smoke run first) and
  `abaybektursun-1115-115102-884c` (shard 1/2), commit `cd2f8d0`; the cut-off run `abaybektursun-1115-103543-61f9`. Raw answers (not
  committed): `runs/<job-id>/` in the worktree `iterate-hack-cells-r9b`; the two finished jobs also as `jobs/<job-id>.tar` in the
  team store.

**cell-r9-m11-01** (round-09 entry m11, readout `m11-r1`; plan `specs/SPEC_cells_r9a.md`; board work-739554, result-f8e596). Base - 1.0 x the top 8
singular directions per matrix of (RL-Math 3.1 - base) (`rlneurons/jobs/wsp_edit.py --recipe top8 --other rl_math --scale -1.0`,
stochastic BF16 rounding seed 0), cue, MATH-500, T 1.0 / top-p 1.0, seed 41,000,000 + index (the seeds of the stored cued base), cap
16,384, grader v3. Stopped by the coordinator before the end: only the odd-index half is complete. **20 cap hits of 250** (90 %
bootstrap [13, 27]); the cued base at the same seeds (sample 0 of `rlneurons/results/day1_3/math500_base_cue-01`) has 10 on the same
250, +10 [3, 18]. Right v3 188 of 250 [177, 199] against the base's 209, -21 [-33, -9]. 4,187 generated tokens per problem (median
1,569; base 3,559).
- Forecasts are cap hits of all 500; nothing is scaled. The rows bound that count to [30, 176]: 20 found in the odd half, 10 among the
  104 even-index rows that finished before the stop, 146 even-index problems with no row. round-09/stopping-m03 (16 [8, 26], sign
  does not matter, -1 cuts cap hits like +1) is refuted by the lower bound; every other forecast (25 to 60) is not decided. On the
  same 250 the edit doubles the base's cap hits (15 problems the base finishes now hit the cap, 5 the other way): the sign matters.
- Raw answers (10 read): 141 of 250 answers carry no `\boxed` and end with a plain "Answer: X" line (103 of them right), as the
  size -1 edit did on hard328 (61 unboxed against 23). Cap hits stop mid-derivation (problems 9, 11, 43); finished wrong answers
  include a binary-to-octal answer that degenerates into one repeated digit string for 16,238 tokens (problem 71), a numeric
  approximation boxed as 13596 for gold 13535 (problem 21), and a box of -1 after the text names 3 (problem 19). Right answers are
  short "Okay, let's see" derivations (problem 3, 654 tokens).
- Caveat: n 250 (odd indices), not 500. The 104 finished even-index rows are summarised apart in `metrics.json` `partial_shard`
  (10 cap hits, 76 right; base 10 and 81 on the same problems) and are not in the readout: they are the answers that finished first,
  so biased toward short ones. Missing problems: the 146 listed in `partial_shard.missing`. Round-09 entry m13 was dropped before it
  generated (its separation came from the same refuted forecaster).
- Files: `analysis/cells_r9a.py` (readout); outputs `results/experiments/cell-r9-m11-01/` (`run.json`, `metrics.json`,
  `per_problem.json` with the base's row per problem, `examples.json`); the count is in `results/wide/round-09/measured.json`.
- Jobs (commit `4a524a2`, command in `run.json`; each ran a 2-problem 256-token smoke run first, in `smoke/`): shard 1/2
  `ih-1115-184625-e391` (complete); shard 0/2 `ih-1115-195318-e122` (stopped at 104 of 250 rows). An earlier shard 0/2 run was cut
  off at about 216 rows when its machine stopped and left no rows. Raw answers (not committed): `runs/<job-id>/` in the worktree
  `iterate-hack-cells-r9a`.

**exact1x-01** (idea-de5c0e, work-20e6ec; offline, no GPU cell). Question: is the dial's 1x (base + top-8 RL-Math directions, 192 of 328,
46 cap hits) under-applied by BF16 rounding, so that an exact 1x merge would score like 1.5x (203, 25; run-05/f2-m06), or is 1.5x the
dial's own optimum (run-05/f2-m01)? **The premise of the rounding account is false on the stored edits, so no cell was run.** Every dial cell
was written by `rlneurons/jobs/wsp_edit.py --rounding stochastic` (unbiased rounding, `merge_weights.to_bf16`). The projection of the written
change on the intended addition (`effective_scale` in `edit.json`) is 0.99996 at 1x and 0.99998 at 1.5x: the 1x edit is applied at full
size. The written change is larger than the intended one (norm 2.596 against 1.269 at 1x, cosine 0.489; 3.254 against 1.904 at 1.5x, cosine
0.585), the extra being a zero-mean residue orthogonal to the addition (norm 2.26 at 1x, 2.64 at 1.5x). The random rank-8 cells carry
residues of 2.35 to 3.36 and score 158 to 163 against base cue 164. The 0.11 % / 0.19 % / cosine 0.585 quoted for "1x" are the 1.5x cell's
figures. An exact merge would need a new float32 writer and a float32 dtype in `run_cell`'s vLLM engine (it has no dtype flag); it would
remove only the residue, which neither mechanism names as the cause.
- Files: `results/experiments/exact1x-01/offline.json` (the numbers of 7 stored edit cells and base cue, the code that read them, the
  command). Inputs: `rlneurons/results/xreward/edits/<cell>/edit.json`, `readout.json`.

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

## Round 08 (2026-11-15, cutoff 11-15 14:15:27 UTC, plan by abaybektursun)

Plan `specs/SPEC_round08.md`, engine version 8 (open targets and forecasts inside the round), no account. Two runs: the first
stopped in `replicate` (`replication/r8-m02/p2.py` ran at 100 % CPU for 20 minutes and was killed; its bootstrap recounts the
switch-marker regex over about 3,900 full answer texts in each of 2,000 resamples). `run_scripts` in `lib/round.py` now gives a
test, duel or replication script 600 s; a script that times out or exits non-zero is written into its result as "not computed:
script failed (<exit code or timeout>)" with its output path, counted in the round line, and the round goes on (in `replicate`
it counts as "not replicated"). The second run skipped every finished stage and ended with exit 0. 58 headless jobs, 106 minutes,
no GPU (`results/engine/round-08/run.json`, log `round08.log`, ranked experiments `experiments.md`, forecasts `forecasts.md`).

**Result: the forecasts written with the open targets say what the readers say, and no theory separates on an open number.
16 open targets from 6 work items. The 4 new theories forecast 6 to 8 targets each; 0 of 37 theory forecasts has its centre
outside both readers' intervals, the largest gap is 0.61 of the readers' half-width, and no target has two theories with
disjoint intervals. Of 12 mechanisms 8 were abandoned (the board already contradicted them); of the 4 developed, r8-m02 is
refuted by its own test, r8-m10 and r8-m12 gain nothing a reader did not expect, r8-m09 survives offline and loses its duel
(-3.05 nats on 2 separating tests). The carried r3-across-2 is refuted (its first computed test). 21 of 23 offline predictions
computed: 15 inside, 3 outside within noise, 3 outside; 1 replication script timed out.**

Hypotheses of the spec: K1 holds (16 targets). K2 refuted (4 theories forecast a third of the targets or more: r8-m02, r8-m09,
r8-m10 8 of 16, r8-m12 6 of 16). K3 refuted (0 targets with two disjoint theory intervals; 5 needed). K4 is scored in round 09.
K5 refuted (106 minutes; about 30 of them the stop in `replicate`, about 76 without it).

| Theory | Statement | Tests computed | In / noise / out | Gain (nats) | State | What decided it |
|---|---|---|---|---|---|---|
| r8-m09 | Think-SFT puts its value on the line after 'Answer:', which grader v3 reads as blank, at a fixed rate per answer; the RL delta at a >= 2 replaces that ending. | 4 of 4 | 3 / 1 / 0 | +1.65 | survives offline; loses to rival; review weak | Rival (the 'Answer:' template is used on short, easy answers): duel p2 measured 0.35 (n 20), theory 0.95 [0.6, 1.45], rival 0.55 [0.32, 0.85]; total -3.05 on 2 separating tests. |
| r8-m12 | On long hard328 problems the cued base reaches a right answer at a flat per-token rate fixed by the problem; cap hits are reasoning still under way. | 4 of 4 | 2 / 1 / 1 | +2.60 | no gain | p1, within-problem rate ratio of right finishes late against early: 3.24 (n 279, 90 % [2.24, 4.77]) against 0.85 [0.5, 1.3]. The rate rises; outside its interval, but +3.00 nats because the readers said 0.6. |
| r8-m10 | Precision falls with answer length only past the length the model's training let it run (RL-Zero-Math about 8,000 tokens; Think-SFT longer). | 4 of 4 | 4 / 0 / 0 | +1.70 | no gain | All inside, but the readers' centres were inside the same intervals. |
| r8-m02 | The cued base loses finished answers by switching lines of attack early ('Alternatively', 'Let me try a different'); RL switches less per token. | 4 of 4 | 2 / 1 / 1 | -3.69 | refuted (own test) | Base / RL switch-marker rate per token 0.758 (n 497, 90 % [0.71, 0.80]) against 1.6 [1.15, 2.4]: RL switches more. Replication timed out (not replicated). |
| r3-across-2 | The cued base leaves loops only through low-probability tail tokens; RL adds a constant push toward probable 'Wait' / 'Hmm' (carried). | 2 of 3 | 1 / 0 / 1 | -1.24 | refuted (own test) | p5 0.179 (n 473, 90 % [0.02, 0.30]) against 0.62 [0.42, 0.85], replicated; p4 not computable (S3 403). |
| r4-m01 | The base's T 0.6 loop hazard grows with how self-similar its text is (carried). | carried, 3 of 4 | 3 / 0 / 0 | +1.41 | survives (round-04 tests) | No new number; 0 forecasts; 0 held-out claims. |
| r5-m03-rival | The top-8 edit is an incomplete switch per sample (carried). | carried | | | survives; not separated from rival; review weak | 1 separating duel test of 6; 3 forecasts, all inside the readers' intervals; 0 strikes of 3 held-out claims. |
| r5-m10-rival | The cue's gain at T 1.0 is robustness to sampled tail tokens, not a choice between two modes (carried). | carried | | | survives; not separated from rival; review weak | 1 separating duel test of 6; 2 forecasts; 0 strikes of 4 held-out claims. |

Abandoned: r8-m01, r8-m03, r8-m04, r8-m05, r8-m06, r8-m07, r8-m08, r8-m11 (`dropped.json`, each with the board items that
contradict it).

Minutes per stage (file times): inventory and external 16 (parallel), targets_open 2.5, mechanisms 12, develop 6, forecast 1,
null_tests and test 12, replicate 28 to the kill + 11 after the resume (p2 timeout 600 s), heldout 3, rival to score_duel 5.5,
cross_predict 3, duel replication 2.5, review and experiments 2.

Forecasts (`forecasts.md`, board snapshot 15:46:24 UTC): t01-t02 finish-dial controls (random rank-8 at 1.5x; Think-SFT's 8
directions at Math's norm; hard328), t03-t04 dial at 1.5x on fresh2026 (vote over 4, single), t05-t06 cued base vote over 9 and
12 on MATH-500, t07-t08 cued base at cap 32,768 on hard328, t09-t12 Think-SFT + 2 x (RL - base) on fresh2026, hard328 and
MATH-500, t13-t16 Think-SFT at cap 32,768 and cut at 16,384 (hard328, fresh2026). Readers forecast all 16. r8-m02: t05-t08,
t13-t16; r8-m09 and r8-m10: t09-t16; r8-m12: t07, t08, t13-t16; r5-m03-rival: t01, t03, t04; r3-across-2 and r5-m10-rival:
t07, t08; r4-m01: none. No two theories' intervals are disjoint on any target; the widest split is t15 (fresh2026, Think-SFT
cap 32,768, vote over 4): r8-m12 76 [68, 84] and r8-m10 75 [67, 83] against r8-m02 70 [62, 78], all overlapping.

Experiments (`experiments.md`): 7 open, 5 of them changes to the base, all below the best known base count (454). Top by
separation: r4-m01:theory:g5, remove repeated lines from the base's own stuck prefix and continue at T 0.6 / top-p 0.95 on the
78 cap-hit problems: r4-m01 32 [26, 39] against its rival 24 [17, 31] finishes, +1.84 nats in 25 GPU minutes.

## Forecast runs

Every unrefuted theory of the newest round (at most 6, survivors first, then by total gain) and two readers with no
theory forecast the numbers the open `work` items will report, before they post. Code `lib/forecast.py` (imports the
job runner and the log density from `lib/round.py`), prompts `lib/prompts/forecast_targets.md`, `forecast.md`,
`forecast_score.md`, `forecast_propose.md` (`--propose N [--lens "<family of causes>"]`).

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

Third score (2026-11-15 15:28 UTC, `scores-2026-11-15T152845.*` and `scores-2026-11-15T152839.*`; `score` now writes a
time-stamped pair when `scores.json` exists). The autobench result (result-6e7b64: 338 of 400, 139 of 328, dev100 84.0)
adds 2 targets to run-01 and 3 to run-02. run-01, 11 of 20 measured: reader-2 10 of 11 inside, +3.01 nats; reader-1 7 of 11,
-8.36; r5-m03-rival 3 of 3, +1.83. t14 (autobench on hard328, 139) is outside every interval. run-02, 6 of 17 measured:
f2-m01 (autobench buys votes by shortening samples) was outside both readers on t14 (338 against 362 and 356) and t15
(139 against 190 and 197) and right on both, +3.25 nats over 4 targets. f2-m02 -8.62 over 4, f2-m03 -7.07 over 3, f2-m05
-5.89 over 3. P3 so far: 2 of 7 disagreements right (needs 8 to decide).

Fourth score (16:33 UTC, `scores-2026-11-15T163347.*`, `scores-2026-11-15T163337.*`). run-01, 15 of 20 measured:
reader-2 14 of 15 inside, +3.00 nats; reader-1 11 of 15, -8.40; r5-m03-rival +1.83 over 3; r6-account-rival +0.91
over 2. run-02, 9 of 17 measured: f2-m01 4 of 6 inside, +5.38 nats (mean +0.90 over 6 targets, so P2 holds for f2-m01);
f2-m04 +1.44 over 3; reader-1 +0.96 over 9; reader-2 -4.12 over 9; f2-m06 -0.19 over 4; f2-m03 -5.45 over 5; f2-m05
-5.89 over 3; f2-m02 -8.62 over 4. P3 so far: 3 of 8 disagreements right (more than 1 in 4: P3 holds at this count).

**run-03 to run-08** (plan `specs/SPEC_forecast03.md`; `make ... --propose 6 --lens "<lens>"`, six processes at once,
commit 2a88c41; snapshot 2026-11-15 16:32:52 UTC; `results/forecast/run-03/` ... `run-08/`). `--lens` gives the
proposing job the family its mechanisms come from; the rule that a mechanism lies outside both readers on 3 targets is
gone; every forecast carries `vs_readers` ("agree ..." or "disagree ..." and why); `forecasts.md` lists every mechanism
forecast beside both readers' values and intervals. Lenses: run-03 stopping (cap, loops, end-of-text, answer markers);
run-04 sampling (temperature, top-p, next-token entropy, votes); run-05 weight space (the RL change, top directions,
scaling, transplants); run-06 training data and objective (Think-SFT imitation, RL reward, pretraining, exposure);
run-07 problem structure (difficulty, domain, answer type, derivation length); run-08 the grader and the measurement
(extraction, equivalence, seeds, set composition). Each run rebuilt its own targets (23, 31, 25, 31, 24, 23 from 12 open
work items) and readers. All 36 mechanisms passed the checks (L1 holds); runs 04 and 06 needed one send-back each (a
statement over 80 words). Mechanisms forecast 12 to 19 targets each and say "disagree" on 0 to 5 of them; without the
forced rule they stay near the readers: the largest gap on any target is 0.8 of the readers' mean 90 % half-width
(run-05/f2-m03, Code-RL top-8 at 1.5x on HumanEval+ and MBPP+, 385 against 357 and 362), and no centre lies outside
both readers' intervals. No two mechanisms from different lenses have disjoint intervals on the same open target; the
nearest split is the same code cell (Code-RL top-8 at 1.5x and 2x, work-df5e0a): run-05/f2-m03 385 [360, 408] and
run-05/f2-m06 378 [350, 402] (weight space) against run-08/f2-m03 342 [322, 362] and 330 [308, 352] (the edit adds only
by converting cap hits). First score (16:45 UTC, `scores.*`): 0 targets measured in any of the six. L2 and L3 not
decided.

## Cells designed by the theories

The open cells did not separate the mechanisms, so the mechanisms design cells. Code `lib/forecast.py cells` (runs the
jobs) and `lib/cells.py` (inputs, checks, ranking, `cells.md`); prompts `lib/prompts/cells_propose.md`,
`cells_merge.md`, `cells_forecast.md`; plan `specs/SPEC_cells01.md`.

```
uv run studies/theory/lib/forecast.py cells studies/theory/results/forecast/cells-<nn> --from <forecast run folders...>
```

One blind job per family (each `--from` run's mechanisms; round 07's unrefuted theories) proposes per mechanism one
GPU cell that it gets right and a named other mechanism gets wrong (cell, job file, command, readout, value with 90 %
interval, the alternative's value outside it, L40S minutes at most 120, `base_only` with the best known base count).
It sees the board, the mechanisms, `known.json` (the runs' targets and round 07's `facts.json`) and `jobs.md` (the
job rows and "How to run" of `studies/rlneurons/README.md` and each job file's `add_argument` lines). One job merges
the same runs; fresh family jobs (one forecast per mechanism) and two readers forecast every readout blind. Ranked in
code: pairs of forecasters from different families whose intervals do not overlap, per GPU minute; base-only readouts
by the highest forecast minus the best known base count. Job outputs stay in `<folder>/jobs/`, so a rerun resumes.

**cells-01** (`results/forecast/cells-01/`: `cells.md`, `cells.json`, `cell_forecasts.json`, `jobs/`; code commit
e56af14; about 25 minutes, 17 jobs; 3 proposing jobs needed one send-back for a job field naming two files). 44
cells proposed, 41 after merging (C1 holds); 3 merged cells have 3 or more cross-family pairs with intervals that do
not overlap, 4 have any (C2 refuted: needs 5). The mechanisms gave a number on 367 of 1,936 mechanism-readout pairs;
the rest "theory says nothing". The named alternative's own blind forecast fell outside the proposer's interval in 20
of 44 proposals (9 said nothing), so in most designed cells the disagreement exists only in the proposer's account
of the other mechanism. 6 base-only readouts have a forecast above the best known base count (C3 holds as coded), but
every such count is a scaled estimate, not a measured count at the same number of samples, and every top forecast is
inside both readers' intervals. Top by separation: m20 base plain on fresh2026 (50 min; run-06 2-3 [0, 8] against
run-07/f2-m06 16 [9, 23] and run-08/f2-m01 14 [8, 20]), m29 base + RL-Math top 8 at 2x on MATH-500 (110 min; 423
[410, 436] against 449-455), m33 the same edit on code, answers with no code block (95 min; 3-4 against 35-38; the
board's 1.5x cell already points to the low side), m06 RL step 100 on hard328 (70 min). Hand check at the end of
`cells.md`: m29, m33 and m06 have commands with flags the jobs do not take (`--recipe topk`, `--model s0100`), which
the checks do not catch.

## Engine version 8 (forecasts inside the round)

`lib/round.py --version 8` (now the default; 7 still runs) adds `targets_open` after `standing` and `forecast` after
`develop` and `account`, both through `lib/forecast.py`'s functions. Mechanisms list the targets they give a number for
(a third of them or more, at least 3); new theories carry `forecasts`; the readers and carried theories forecast blind.
The next round's `standing` scores the forecasts (`forecast_scores.json`): 3 or more scored targets with a total at or
below -2 nats refute; "stands" needs a total above 0 on 3 or more. Smoke run (sonnet, 3 mechanisms, outside the
repository, about 14 minutes through `split standing targets_open mechanisms develop forecast`): 21 targets, 3 mechanisms
with 7 targets each, 2 theories developed (7 and 11 forecasts), 1 abandoned; a second smoke folder's `standing` scored
them (6 targets measured). Both folders deleted.

## Engine version 9 (the wide round is the default)

Plan `specs/SPEC_engine_v9.md`; skill `.claude/skills/theory/SKILL.md` (version 9). The default round is now
`lib/forecast.py round <folder> --from <previous round, or forecast run and cells folders>`: `standing` (scores every
source's forecasts and its cells' `measured.json`; carries mechanisms with a total gain above 0 on 3 or more scored
numbers, sends those at or below -2 nats on 3 or more to `graveyard.json`), `targets_open`, `forecast` (readers and
carried mechanisms), `propose` (six lens jobs at once, 6 mechanisms each, each with `holds_against`: the two known
numbers nearest to contradicting it), `cells`, `experiments` (`experiments.md`). Output under `results/wide/round-<nn>/`.
`lib/round.py` is the `--deep` tool: `--deep <wide round>` makes the carried mechanisms its `mechanisms.json`.

Score change, everywhere a log gain meets a measured value (`round.py` `gain_rows`, `score_duel`, `gpu_tests`;
forecast and cell scores): a prediction whose measured value lies outside its own 90 % interval gains at most 0;
losses are unchanged. Cells: `lib/cells.py` `job_flags` parses each job file's `add_argument` calls (flags and
`choices` values); a proposed or merged cell whose command names a missing job file, flag or value is sent back once,
then dropped (`cells.json` `dropped`). On cells-01 the check fails 21 of 41 merged commands (`--recipe topk` or
`minus_topk` where `wsp_edit.py` takes `top8`, `bulk`, ...; `--model s0100`, `s0400`, `think_sft` where `run_cell.py`
takes `base`, `rl`).

**Re-score of forecast runs 01-08** (`forecast.py score <run> --rescore`: the measured values of each run's newest
score file, no job; `results/forecast/run-0N/scores-2026-11-15T1731*.json/.md`). The top three are unchanged:
run-06/f2-m03 +5.56 nats (5 of 5 inside), run-02/f2-m01 +5.38 to +5.10 (4 of 6), run-05/f2-m03 +4.85 (5 of 5).
run-07/f2-m02 falls from +5.21 to +3.29 (2 of 5 inside; third to fifth), run-04/f2-m03 from +2.54 to +0.26 (2 of 5),
run-05/f2-m02 from +1.88 to -0.29 (1 of 5), run-05/f2-m06 from +3.36 to +2.66; run-01's reader-2 from +3.00 to
+2.32. The bottom is unchanged (run-08/f2-m03 -12.27, run-02/f2-m02 -8.62, run-02/f2-m05 -5.88): the cap removes
gains, never losses.

Smoke run (outside the repository, `--from results/forecast/run-07 --propose 2 --model-all sonnet`, then deleted):
`standing` carried run-07/f2-m02 (+3.29 nats on 5) and sent run-07/f2-m05 (-2.59 on 5) to the graveyard; 23 targets
from 15 open work items; 12 new mechanisms (all six lens jobs needed one send-back: too few forecasts or a statement
over 80 words; every `holds_against` passed); 13 cells proposed, 0 dropped, 13 merged, 0 of 13 commands fail the flag
check (on cells-01, 21 of 41 did), 2 cells with a pair of families whose intervals do not overlap. About 11 minutes of
jobs (5.5 to `forecasts.json`, 5.7 for cells and experiments), plus two resumes after fixes found by the smoke run (the
board dump folder was reused within one process; mechanism and cell proposals shared a file name).

## Round 09 (wide path, engine 9)

Board snapshot 2026-11-15T17:45:51 UTC (board work-0a9281), code commit 0959d61, 40.0 minutes in one run (standing
written 17:45:51, `cells.md` 18:25:15 UTC), 48 forecasters. Command:

```
uv run studies/theory/lib/forecast.py round studies/theory/results/wide/round-09 --from studies/theory/results/forecast/run-0{2,3,4,5,6,7,8} studies/theory/results/forecast/cells-01
```

Files in `results/wide/round-09/`: `standing.md` / `standing.json` / `standing/` (scores of each source),
`graveyard.json`, `targets.json` and `work.md` (27 targets from 16 open work items), `mechanisms.json` (10 carried + 36
new), `forecasts.json` / `forecasts.md`, `cells.json` / `cell_forecasts.json` / `cells.md`, `experiments.md`,
`run.json`, `round09.log` (the console log), `jobs/` (each job's JSON output, 720 KB). Job prompts and raw outputs stay
in the temp folder named in `run.json`.

**Standing** (42 mechanisms, 25 scored). Carried, total gain on scored numbers: run-06/f2-m03 +5.56 (5 of 5 inside),
run-02/f2-m01 +5.10 (4 of 6), run-05/f2-m03 +4.85 (5 of 5), run-05/f2-m01 +4.40 (5 of 5), run-07/f2-m02 +3.29 (2 of 5),
run-05/f2-m06 +2.66 (3 of 5), run-03/f2-m02 +2.22 (4 of 5), run-02/f2-m04 +1.43 (2 of 3), run-03/f2-m05 +0.49 (2 of 5),
run-04/f2-m03 +0.26 (2 of 5). Eight of the ten are scored only on result-a1bf75 (the code dial: 5 targets of one
experiment, where both readers forecast 20 to 45 below every measured edit count); run-02/f2-m01 rests on 4 experiments
(result-fad48d, 0c1eef, 95a4dc, 6e7b64) and run-02/f2-m04 on 3. Graveyard: run-07/f2-m05 -2.59, run-08/f2-m04 -4.23,
run-04/f2-m06 -4.60, run-02/f2-m03 -5.45, run-02/f2-m05 -5.88, run-02/f2-m02 -8.62, run-08/f2-m03 -12.27 (5, 5, 5, 5,
3, 4, 5 scored numbers).

**New mechanisms** (ids `round-09/<family>-mNN`; full text in `mechanisms.json`):

- stopping: m01 a cap hit abstains in a vote; m02 Think-SFT's stopping point lies past 16,384 tokens, the RL delta moves
  it earlier; m03 stopping follows the root summed squared singular values an edit adds, at any rank; m04 a change that
  keeps the length distribution moves only precision; m05 late terminators are seldom attached to a derived result; m06
  the terse register stops right after its first stated result.
- sampling: m01 per-problem independent draws, SD 5 to 7 per 500; m02 a vote counts only committed answers; m03
  temperature sets how often a plain prompt opens in the deliberative register; m04 an edit past a logit-shift threshold
  puts mass on near-certain tokens and text decays; m05 ending is sampled, a cap raise finishes the tail at that model's
  long-answer precision; m06 solve rates are bimodal, votes plateau.
- weights: m01 finishing sits in the top-1 direction per matrix; m02 the edit is a sum of small pushes, a part acts as
  the whole scaled to its share; m03 finishing is read out in layers 22-31; m04 the RL delta on Think-SFT only finishes;
  m05 the step-100 change points elsewhere than the final one (cosine 0.099); m06 stochastic rounding is unbiased,
  scores follow nominal dose.
- training: m01 Think-SFT's answer placement is learned inside its ChatML template; m02 Think-SFT's cuts are mid-derivation
  work; m03 group-relative reward moves mid-difficulty problems first; m04 pretraining fixes each problem's modal value;
  m05 the top-1 direction carries answer form, stopping is spread over the next directions; m06 the update sits on
  early and middle layer features, the first third gives most.
- problems: m01 bimodal solve probability, the vote converts only the middle band; m02 more budget pays only where cut
  text is a sound derivation; m03 the plain terse register derails on short problems; m04 RL fixes problems in order of
  derivation length; m05 contest problems are limited by plans, which only imitation supplies; m06 the best dose is
  lower on harder sets.
- grader: m01 a single cell is one draw, notable cells sit above their mean; m02 vote gain is set by abstaining
  instead of answering wrong; m03 an edited model's null is the random-edit null (about 161 on hard328), not the
  base's 164; m04 a count depends on the set's difficulty mix; m05 even-k ties are broken by sample order; m06 a cap
  count hides unfinished work, the 32k-minus-16k count is its yield.

**SPEC_engine_v9 hypotheses.** V1 (under 40 minutes to `cells.md`): refuted, 40.0 minutes (propose 704 s, cells about
22 minutes). V2 (at least 8 merged cells with a cross-family pair whose 90 % intervals do not overlap): holds, 8 (m11
10 pairs, m13 7, m21 3, m05 3, m18 2, m14 1, m06 1, m29 1). V3 (top 10 of list A pass the flag check, checked by hand):
holds as worded, 10 of 10 name existing job files and flags; but m14's `--mods mlp` fails `wsp_edit.py`'s assertion
(`--mods` takes q,k,v,o,gate,up,down), so its command stops at run time (the check does not test free-text values).
Cell checks of `cells.md`: C1 holds (46 proposed, 39 merged, 0 dropped), C2 refuted (4 cells with 3 or more pairs,
needs 5), C3 refuted (0 base-only readouts forecast above the best known base count; 4 of 39 cells are base-only).

**Top 6 cells of list A** (`experiments.md`; every forecaster that gave a number, value [90 % interval]; R1, R2 are
the readers; ids without a run prefix are `round-09/`):

1. m11, base - 1.0 x top-8 RL-Math directions, cue, MATH-500 n 500, cap hits of 500 (105 min, 10 pairs, all against
   stopping-m03): stopping-m03 16 [8, 26]; grader-m03 36 [25, 49]; stopping-m02 36 [26, 48]; run-03/f2-m02 36 [26, 48];
   weights-m02 37 [27, 49]; run-04/f2-m03 38 [26, 52]; weights-m01 38 [27, 50]; weights-m06 38 [27, 50]; problems-m06
   40 [27, 55]; R2 40 [28, 55]; run-05/f2-m01 40 [29, 53]; training-m05 40 [30, 54]; run-06/f2-m03 40 [30, 54];
   run-07/f2-m02 42 [28, 58]; R1 42 [28, 60].
2. m13, base + 2.0 x top-64 RL-Math directions, cue, hard328 shard 0/2, right of 164 (80 min, 7 pairs, all with
   stopping-m03): stopping-m03 58 [40, 80]; run-03/f2-m05 70 [45, 92]; sampling-m04 84 [60, 102]; problems-m06 88
   [74, 102]; R1 90 [72, 104]; run-04/f2-m03 90 [74, 104]; run-03/f2-m02 90 [78, 101]; R2 92 [78, 104]; problems-m02 92
   [78, 105]; run-05/f2-m01 94 [84, 103]; problems-m05 95 [82, 106]; run-06/f2-m03 95 [83, 106]; weights-m01 95 [85,
   104]; stopping-m02 96 [84, 106]; weights-m06 96 [86, 105]; grader-m03 97 [82, 108]; weights-m02 100 [91, 108].
3. m21, base + 1.0 x top-8 RL-Code directions, plain, MATH-500 first 250, quick wrong answers (at most 1,000 tokens,
   not a cap hit, not right) of 250 (55 min, 3 pairs): run-03/f2-m02 14 [7, 23]; stopping-m06 15 [8, 24];
   run-04/f2-m03 18 [7, 32]; R2 18 [8, 32]; sampling-m03 20 [8, 35]; problems-m03 20 [10, 32]; R1 25 [10, 45];
   run-06/f2-m03 25 [10, 45]; run-07/f2-m02 27 [14, 40]; run-05/f2-m03 40 [24, 58]; run-05/f2-m06 45 [28, 64].
4. m05, untrained base, plain, MATH-500 first 100, vote over 8, right of 100 (90 min, 3 pairs; base-only, best base
   90 scaled from result-5d032f): stopping-m01 42 [32, 52]; training-m04 52 [38, 66]; grader-m05 54 [42, 65];
   grader-m02 56 [44, 67]; sampling-m06 58 [46, 69]; run-02/f2-m01 60 [47, 72]; R2 62 [48, 75]; R1 62 [48, 76];
   stopping-m06 62 [50, 74]; sampling-m02 66 [54, 76]; problems-m01 70 [56, 82]; problems-m03 72 [58, 84].
5. m18, base + 0.125 x (RL-Math - base), plain, MATH-500 n 500, right of 500 (90 min, 2 pairs): run-05/f2-m06 300
   [260, 340]; sampling-m03 308 [272, 342]; run-03/f2-m02 330 [280, 375]; stopping-m06 345 [295, 390]; R1 355 [315,
   392]; R2 362 [320, 400]; weights-m06 365 [330, 400]; problems-m03 395 [365, 420].
6. m14, base + 3.0 x top-8 RL-Math directions in MLP matrices only, cue, hard328 shard 0/2, right of 164 (75 min, 1
   pair; command fails, see V3): weights-m01 62 [42, 82]; run-03/f2-m05 65 [45, 85]; R1 80 [55, 100]; problems-m06 80
   [62, 98]; run-06/f2-m03 82 [62, 100]; R2 85 [65, 100]; run-05/f2-m01 85 [68, 100]; run-03/f2-m02 85 [70, 98];
   grader-m03 90 [76, 102]; stopping-m03 90 [78, 100]; sampling-m04 92 [76, 105]; run-04/f2-m03 92 [78, 104];
   stopping-m02 92 [80, 102]; weights-m02 97 [87, 106].

The cell ids restart at m01 in every run: round-09 m06 and m29 are not the cells-01 m06 and m29 of work-844e38 and
work-290625.

**First score of round 09** (18:28 UTC, `forecast.py score results/wide/round-09`: `round-09/scores.md`). 12 of 27
targets measured (result-6832a8, 306787, d02d46, a74ac3), none outside every interval; readers +0.04 and -0.19 nats.
Best: training-m06 +1.65 on 7 (layers 0-10 carry the right answers), run-05/f2-m01 +1.18, run-05/f2-m03 +1.11,
sampling-m03 +1.04. Worst: weights-m03 -6.31 on 9 (layers 22-31 at 1.5x forecast 189 [176, 202], measured 166; layers
0-10 forecast 166 [154, 178], measured 184), stopping-m03 -4.47 on 8 (top-1 at 3x forecast 196 [183, 208], measured
168), problems-m06 -1.99 on 6, weights-m02 -1.90 on 9. stopping-m03 is one side of every pair of cells m11 and m13.

Forecast runs 02-08 scored again against the items posted since their snapshots (`forecast.py score`, files
`results/forecast/run-0N/scores-2026-11-15T1828*.json/.md`): the new numbers are result-6832a8's four-sample step-100
counts (t08-t11 of runs 03-08), where every forecaster sits within a few problems of the readers (-0.8 to +0.3 nats per
number); run-02 is unchanged. run-06/f2-m03 +5.70 on 9, run-05/f2-m03 +4.86 on 9, run-08/f2-m04 -3.92 on 8; run-04/f2-m04
+0.57 on 5, run-08/f2-m01 +0.52 on 5, run-04/f2-m05 +0.42 on 4 and run-03/f2-m06 +0.19 on 5 now pass the carry rule by
agreeing with the readers.

cells-01 scored on its `measured.json` (rows already in SKILL.md's format) with `lib/forecast.py` `cell_scores`, the
function `standing` uses (no stand-alone command exists for cells): `cells-01/scores.json/.md`. m20-r1 measured 10 of 136
(result-a74ac3): readers 14 [7, 22] and 13 [6, 21]; run-06/f2-m02 3 [0, 8] and run-06/f2-m06 2 [0, 7] -3.00 each,
run-07/f2-m06 16 [9, 23] -0.63, run-08/f2-m01 14 [8, 20] -0.08.

## Engine version 10 (two tracks)

Plan `specs/SPEC_engine_v10.md`; skill version 10. Same command (`forecast.py round $W --from ...`), with these changes
in `lib/forecast.py` and `lib/cells.py`:

- Carry rule by experiments: each scored row carries the board item that posted its number (version-9 rows get it from
  their round's `standing/` files); carried needs a total gain above 0 on 3 or more distinct items, the graveyard -2
  nats or less on 2 or more items. `standing` reads each `--from` folder once and keeps one row per (folder, number).
  Re-applied to round 09's cached scores (a copy, runs 02-08): 2 of the 10 stay carried, run-02/f2-m01 (+5.10 nats, 6
  numbers from 4 items) and run-02/f2-m04 (+1.43, 3 numbers from 3 items); the other 8 have one item each
  (result-a1bf75). Graveyard by the new rule: run-02/f2-m03 (-5.45, 3 items) and run-02/f2-m02 (-8.62, 2 items); the
  other five of round 09's seven have one item.
- Separation: forecasters with a record at or below -2 nats are left out (`cells.json` `left_out`); a readout separates
  when the rest split into a low and a high side with 2 or more families on each side; list A ranks by separating
  readouts per GPU minute.
- Track 2, no-reward routes (`prompts/routes_propose.md`, list C): one route per family from the base alone or
  Think-SFT, with an RL arm, tokens per problem, four readouts (route and RL on a hard328 subset and on MATH-500) and
  the gap parts it targets (`gap.md`: result-f39ba8 and the rlneurons "Gap anatomy"). Everyone forecasts every route
  in the same job as the cells. Ranked by the median forecast minus the best known count of the same model at equal or
  fewer tokens, from a table built in code from the board's `score:` lines (49 rows at the time of writing: base
  rows, and Think-SFT rows that name no RL change).
- `studies/theory/jobs/free_cell.py`: no existing job takes free prompt text, opening text and a repetition penalty, so
  this one imports run_cell's sets, rln4_gen's engine and row record and grader v3 and takes `--model base|rl|think_sft`,
  `--prompt-suffix`, `--opening-text`, `--temperature`, `--top-p`, `--min-p`, `--repetition-penalty`, `--max-tokens`,
  `--samples`, `--seed`, `--set`, `--n`, `--shard`, `--dry-run`. Tested on the laptop by the dry path only (tokenizer and
  canned answers: 6 rows on hard328 shard 0/2, suffix and opening in the prompt as intended); it has not run on a GPU.
- Duplicate judge (`prompts/duplicates.md`, `duplicates.json`): one blind job before the forecasts; the newer
  mechanism of each pair is dropped. Cell ids carry the round (`r10-m05`, routes `r10-n01`). The flag check covers
  `studies/theory/jobs/` and reads a single-quoted value as one word (version 9 stopped at the first quote).

Smoke run (outside the repository, `--from results/forecast/run-07 --propose 2 --model-all sonnet`, then deleted;
about 12 minutes over two runs: the stopping family's job failed its forecast-count check after the send-back, and a
rerun of the same command resumed): 28 targets, 12 new mechanisms, 6 dropped as duplicates (4 of each other, 2 of
earlier entries), 7 cells and 6 routes, 0 dropped by the flag check, 0 cells with a 2-and-2 family split. With
Think-SFT routes measured against Think-SFT's own counts, 2 of 6 routes have a median above the best known count (the
first ranking, against the base table, put all 6 above and was fixed). A route's token figure is the proposer's
estimate: one base route claimed 5,000 tokens per problem with the cue, which runs about 9,300, and so met the plain
76-of-328 row.

## Round 10 (engine 10, two tracks)

Board snapshot 2026-11-15T18:58:29 UTC (board work-744158), code commit ca281af, 46.8 minutes in one run (standing
18:58:29, forecasts 19:20:30, `cells.md` and `experiments.md` 19:44:35 UTC), 44 forecasters. Targets, mechanisms and
forecasts were committed at 19:20 UTC, before any scoring. Command:

```
uv run studies/theory/lib/forecast.py round studies/theory/results/wide/round-10 --from studies/theory/results/wide/round-09 studies/theory/results/forecast/run-0{2,3,4,5,6,7,8} studies/theory/results/forecast/cells-01
```

**Standing.** 78 mechanisms, 77 scored: 30 carried, 9 in the graveyard. The 30 carried rest on 11 distinct board
items, but result-a1bf75 (the code dial) still supplies 23.3 of their 47.9 nats of total gain (49 %). Top: run-06/f2-m03
+6.20 (16 numbers, 5 items), run-05/f2-m03 +6.02 (19, 5), run-05/f2-m01 +5.76 (16, 4), run-02/f2-m01 +5.64 (7, 5).

**Proposals.** 36 new mechanisms; the duplicate judge dropped 24 (`duplicates.json`; 13 restate a round-09
mechanism, 10 a forecast-run mechanism, 1 another round-10 mechanism), leaving 12 new. 39 merged
cells, 7 routes, 0 dropped by the flag check.

**SPEC_engine_v10 hypotheses.**

- W1 (at least 4 routes with a median forecast above the best known count at equal tokens): holds as computed, 6 of
  7. It carries no information: the 6 margins are 0.4 to 2.7 problems on subsets of 41 to 164 problems, inside one
  binomial SD of the subset (about 3 to 4 problems), and every MATH-500 margin is between -0.1 and -0.8.
- W2 (at most 10 of 36 new mechanisms dropped as duplicates): refuted, 24 of 36.
- W3 (at least 5 cells with a readout split by 2 or more families on each side): refuted, 0 of 39 cells. Even with 1
  family per side only 3 of 69 cell readouts have any two forecasters with disjoint 90 % intervals.
- W4 (under 45 minutes): refuted, 46.8 minutes.

**List C, no-reward routes** (`experiments.md` section C). Units: right answers (grader v3, cap hits wrong) on the
route's own subset of hard328 (n problems, a `--shard`) and of MATH-500. "Best known" is the best board `score:` row of
the same model at equal or fewer tokens per problem, a full-set count multiplied by n / 328 or n / 500 (not a measured
subset count). The last column restates the hard328 median per 328 problems for comparison across routes.

| route | family | change | tokens per problem (proposer) | hard328 n | median / best known | MATH-500 n | median / best known | hard328 per 328 |
|---|---|---|---|---|---|---|---|---|
| r10-n01 | training | Think-SFT, cue, cap 32,768, sequential vote over up to 3 | 26,500 | 66 | 49 / 46.3 | 50 | 48 / 48.1 | 243.5 |
| r10-n07 | grader | Think-SFT, cue, cap 32,768, 2 samples, agree-or-finished-or-shorter rule | 23,600 | 82 | 59 / 57.5 | 50 | 47.5 / 48.1 | 236 |
| r10-n06 | sampling | Think-SFT, cue, cap 32,768, 2 samples, agree-or-finished rule | 23,600 | 55 | 40 / 38.6 | 50 | 47.5 / 48.1 | 238.5 |
| r10-n05 | stopping | Think-SFT, opening ` line!\n\n<think>\nOkay` + a `</think>` instruction, cap 16,384, 1 sample | 9,000 | 164 | 104 / 103.5 | 100 | 92 / 92.2 | 208 |
| r10-n02 | weights | Think-SFT, cue, cap 32,768, majority of 3 | 35,400 | 41 | 30.5 / 30.1 | 50 | 48 / 48.1 | 244 |
| r10-n04 | problems | Think-SFT, cue, cap 32,768, sequential vote over up to 3 | 35,400 | 41 | 30.5 / 30.1 | 100 | 96 / 96.2 | 244 |
| r10-n03 | run-02 | Think-SFT, cue, cap 12,288, 3 samples, capped samples abstain | 25,500 | 41 | 28 / 28.8 | 84 | 80 / 80.8 | 224 |

Best known rows used: hard328 230/328 at 11,795 tokens (result-c8b994, one sample at cap 32,768) for n01, n03, n06,
n07; 241/328 at 30,904 (result-818c20, sequential vote up to 4 at cap 16,384) for n02, n04; for n05 no row is at or
below 9,000 tokens, so the code fell back to the cheapest row, 207/328 at 10,048 (result-c8b994 at 16,384), and not
the 212/328 at 10,137 of result-818c20 (against 212 the median is 2 below). MATH-500: 481/500 at 19,503 tokens
(result-818c20) for all but n05 (461/500 at 4,900). Measured since (work-dc9359, 19:39 UTC): Think-SFT + cue at cap
32,768 on hard328, singles 230, 234, 235, 232 and vote over 4 244/328; its four samples' rows can score the hard328
route readouts of n01, n02, n04, n06, n07 (and n03 rescored at 12,288) without a GPU run. No route changes the base
alone; no route was run.

Files in `results/wide/round-10/`: `standing.md` / `standing.json` / `standing/`, `graveyard.json`, `targets.json` and
`work.md` (33 targets from 19 open work items), `mechanisms.json` (30 carried + 12 new), `duplicates.json`,
`forecasts.json` / `forecasts.md`, `cells.json` (cells, routes, best-known table) / `cell_forecasts.json` / `cells.md`,
`experiments.md`, `run.json`, `round10.log` (the console log), `jobs/` (each job's JSON output, 1.0 MB). Job prompts
and raw outputs stay in the temp folder named in `run.json`.

## Round 11 (engine 11, score first)

Plan `specs/SPEC_engine_v11.md`; engine version 11 (`lib/forecast.py round`: standing, surprises, targets_open, forecast
by readers and carried mechanisms, rival pairs only about the top surprises, cells and routes checked against open work;
`--propose-wide` keeps version 10). Board work-0f3aae (work-502f19). Board snapshot 2026-11-15T20:05:26 UTC, code
commits 5063fab, 349e857 and the fix after it; three runs of the same command, 20:04:12 to 20:22:55 UTC (12.7 + 1.5 + 3.4
minutes of running; the round stopped twice in `cells` on bugs the smoke run did not reach, see Problems). `surprises.md`
and `targets.json` were committed at 20:09, `forecasts.json` and `mechanisms.json` at 20:17, before any of their numbers
posted. Command:

```
uv run studies/theory/lib/forecast.py round studies/theory/results/wide/round-11 --from studies/theory/results/wide/round-10 studies/theory/results/wide/round-09 studies/theory/results/forecast/run-0{2,3,4,5,6,7,8} studies/theory/results/forecast/cells-01
```

**Standing** (`standing.md`). 90 mechanisms, 89 scored; 32 carried (top: run-06/f2-m03 +6.00 nats on 7 results,
run-05/f2-m01 +5.95 on 6, run-05/f2-m03 +5.81 on 6, run-02/f2-m01 +5.79 on 6, run-05/f2-m06 +4.24 on 6). Newly carried:
round-09/stopping-m01 +0.64, grader-m02 +0.45, grader-m05 +0.37, training-m01 +0.08, training-m02 +0.05 (each 3
results). No longer carried: round-09/grader-m03 -0.83, weights-m01 -0.96, problems-m05 -0.38 (6 results each).
Graveyard, 10 (new: run-02/f2-m05 -5.31 on 2 results): run-08/f2-m03 -11.80 (3), run-02/f2-m02 -9.53 (3),
round-09/weights-m03 -6.05 (5), run-02/f2-m03 -5.28 (4), run-04/f2-m06 -4.68 (3), round-09/stopping-m03 -3.97 (5),
run-08/f2-m04 -3.92 (2), run-06/f2-m06 -3.01 (3), run-07/f2-m05 -2.54 (2).

**New numbers.** Numbers from results posted after round 10's forecasts (19:20 UTC): 6 distinct, result-6f7ca3 (five
numbers, round 10's t03-t07: 183.5, 181, 163.5, 183, 162) and result-83f648 (244, Think-SFT + cue vote over 4 at cap
32,768 on hard328, the work-dc9359 number as quoted in round 10's own result, scored in round-09 t26, round-10 t30 and
run-02 t16). work-dc9359 had posted no result of its own.

**Surprises** (`surprises.md`, 8, all from results posted before round 10; none of the 6 new numbers is one). Measured
value, reader-1 and reader-2 (90 % intervals), z:

| # | number | result | measured | reader-1 | reader-2 | z | outside every forecaster |
|---|---|---|---|---|---|---|---|
| 1 | autobench final configuration, hard328 (run-02 t15) | result-6e7b64 | 139 | 190 [165, 210] | 197 [180, 210] | 3.73 | no (run-02/f2-m01) |
| 2 | base + 8 RL-Code directions at 1.5x, HumanEval+ and MBPP+ (run-04 t02) | result-a1bf75 | 399 | 357 [330, 384] | 357 [328, 386] | 2.38 | yes |
| 3 | autobench best dev100 score (run-02 t13) | result-6e7b64 | 84 | 89 [86, 93] | 89 [86, 93] | 2.35 | yes |
| 4 | base + 8 RL-Code directions at 1x, code (run-04 t01) | result-a1bf75 | 386 | 350 [325, 376] | 350 [325, 376] | 2.32 | yes |
| 5 | autobench final configuration, math400 (run-02 t14) | result-6e7b64 | 338 | 362 [345, 375] | 356 [342, 368] | 2.28 | no (run-02/f2-m01) |
| 6 | base + 8 RL-Code directions at 2x, code (run-07 t03) | result-a1bf75 | 394 | 347 [312, 378] | 350 [316, 380] | 2.26 | yes |
| 7 | base + 8 RL-Math directions at 1.5x, code (run-07 t05) | result-a1bf75 | 368 | 338 [314, 362] | 333 [310, 358] | 2.06 | yes |
| 8 | cells-01 m06: quick finished-wrong answers of 164 | result-9ce8ed | 7 | 20 [9, 34] | 22 [10, 36] | 1.71 | no (run-05/f2-m04, run-06/f2-m02) |

**Rival pairs** (`pairs.json`, `duplicates.json`). Six jobs, one per surprise 1-6, wrote 12 rivals; the judge dropped 9
as restatements (s1-a of run-02/f2-m01, s1-b of round-09/training-m04, s2-a of round-10/weights-m05, s3-a of
round-09/stopping-m06, s3-b and s5-b of s1-b, s4-a of round-10/problems-m03, s5-a of s1-a, s6-a of run-07/f2-m05),
leaving s2-b, s4-b, s6-b. Before the judge, four pairs differed on open targets (s2: t18, t21; s3: t13, t14; s4: t05,
t21; s6: t18, t27) and two named cells (s1, s5). After it, only s1 and s5 stand, both through carried stand-ins, and both
resolve to the same two mechanisms, run-02/f2-m01 (short per-sample budgets cannot reach long hard328 solutions) against
round-09/training-m04 (the vote converges to the plain register's modal answer). Their cells: r11-m01, the base, plain,
T 0.6, cap 4,096, one sample on hard328 (45 min): 66 [52, 82] against 98 [86, 110] in the proposal, but in the blind
forecasts 84 [70, 98] against 96 [82, 110], overlapping, readers 90 and 90; r11-m02, vote over 6 at cap 8,192 minus the
same vote with samples over 4,096 tokens counted as abstaining, MATH-500 first 100 (110 min): 4 [2.5, 8] against 0.5
[-1.5, 2] in the proposal, 1 against 1 blind. As in cells-01, the disagreement exists only in the proposer's account.
0 of 2 cells split; 0 cells or routes were turned into free targets (`jobs/answered.json` empty), 0 dropped.

**Routes** (list C): r11-n01, Think-SFT + cue, sequential vote up to 5, hard328 shard 0/8 (41 problems): median 33.5
against the stored 34 of that subset in the nearest row (sequential vote up to 4, ties to the shortest, 30,837 tokens;
sd 2.41), margin -0.21 sd; r11-n02, Think-SFT + cue, min-p 0.05, majority of 3, shard 0/5 (66): median 48 against the
stored 49 of the same row (sd 3.55), -0.28 sd. Neither beats its stored subset count.

**SPEC_engine_v11 hypotheses.** X1 (15 or more new numbers, among them work-dc9359's hard328 rows): refuted, 6, and
work-dc9359's own rows are not posted (only its vote 244, quoted in result-83f648). X2 (3 or more surprises): holds, 8,
but all 8 come from results scored before; no number posted since round 10 is a surprise. X3 (2 or more rival pairs
that differ by more than their intervals after the judge): refuted as distinct pairs, 1 (s1 and s5 resolve to the same
two mechanisms, and their blind forecasts overlap). X4 (under 30 minutes): holds, 17.6 minutes of running, 18.7 wall.

**Problems.** The cells stage stopped twice on the first real pair cells (a family made only of stand-ins had no
mechanisms for its route job; the check job read readouts before the proposers' fields were attached); both were fixed
in `lib/forecast.py` and the same command resumed. The smoke run had no pair with a cell, so it never reached them.

Files in `results/wide/round-11/`: `standing.md` / `standing.json` / `standing/`, `graveyard.json`, `surprises.md` /
`surprises.json`, `targets.json` / `work.md` (28 targets from 20 open work items), `pairs.json`, `duplicates.json`,
`mechanisms.json` (32 carried + 3 new), `forecasts.json` / `forecasts.md`, `cells.json` / `cell_forecasts.json` /
`cells.md`, `experiments.md`, `run.json` (of the last run), `round11.log` (the three console logs), `jobs/`.

## Round 12 (engine 11, score first)

Plan `specs/SPEC_round12.md`. Board work-b66b4c (work-502f19). Engine 11 unchanged (code commit 521533f). Board
snapshot 2026-11-15T20:38:56 UTC; one run, 12.4 minutes, exit 0, no fix needed. `surprises.md` committed at 20:39,
`targets.json` 20:41, `forecasts.json` and `mechanisms.json` 20:50, before any of their numbers posted. Command:

```
uv run studies/theory/lib/forecast.py round studies/theory/results/wide/round-12 --from studies/theory/results/wide/round-11 studies/theory/results/wide/round-10 studies/theory/results/wide/round-09 studies/theory/results/forecast/run-0{2,3,4,5,6,7,8} studies/theory/results/forecast/cells-01
```

**New numbers.** 23 distinct numbers (79 rows across folders) from 6 results posted after 20:05 UTC: result-dd9239,
result-0a0a5a (Think-SFT own chat format), result-ac7104 (round-09 cells m21, m18 from `round-09/measured.json`),
result-6776d8 (RL's 8 directions on Think-SFT; Math + Code on the base), result-1c9e40 (vote over k of 12),
result-d82083 (8 RL-Math directions at 2x, 448). result-42cc6c (M(2) at cap 32,768, 245) was not scored: it used seed
3,010,000 and the open targets named seeds 3,100,000 (round-11 t02) and 3,000,000 (t26). result-d82083 is cell m29 of
round-09 but has no row in `round-09/measured.json`, so the cell's own forecasts were not scored.

**Standing** (`standing.md`). 93 mechanisms scored; 42 carried, 18 in the graveyard. Top: run-05/f2-m06 +7.19 nats on
49 numbers from 9 results (bf16 rounding thresholds small edits), run-05/f2-m01 +6.79 on 10 (top-8 directions are a
signed finishing dial), run-06/f2-m03 +5.19 on 10 (outcome reward piles into a few finishing directions; was +6.00),
run-05/f2-m03 +3.74 on 9 (directions act in proportion to input-subspace excitation), run-02/f2-m04 +2.67 on 9 (capped
samples abstain in a vote). Most carried records count the same number more than once (146 repeated rows: the same
result and value scored in round-09, round-10 and round-11 targets); counted once, the top four keep their order
(+6.75, +6.62, +6.40, +5.03) and round-09/training-m01, weights-m04 and grader-m04 fall to 0 or below. New in the
graveyard: run-03/f2-m05 -7.34, round-09/problems-m03 -6.83, round-11/s6-b -8.11, s2-b -4.66, s4-b -3.94 (round 11's
three surviving rivals, refuted by result-6776d8 and result-ac7104), round-09/grader-m03 -3.91, weights-m01 -3.29,
run-04/f2-m03 -2.29. run-02/f2-m01 is no longer carried (-1.77).

**Surprises** (`surprises.md`, 13; 5 new):

| number | result | measured | reader-1 | reader-2 | inside |
|---|---|---|---|---|---|
| round-09 m21-r1: quick wrong, base + Code-RL top-8 at 1x, plain, MATH-500 first 250 | result-ac7104 | 60 | 25 [10, 45] | 18 [8, 32] | run-05/f2-m06 |
| round-10 t16: cued base, vote over 12, MATH-500 | result-1c9e40 | 466 | 453.5 [446, 461] | 454 [446, 462] | nobody |
| round-11 t22: base + Math 1x + Code 1x directions, HumanEval+/MBPP+ | result-6776d8 | 411 | 390 [372, 405] | 392 [372, 408] | nobody |
| run-06 t14: Think-SFT own chat format, MATH-500, cap 32,768 | result-0a0a5a | 474 | 462 [451, 472] | 463 [452, 473] | run-06/f2-m01 |
| run-04 t17: cued base, vote over 6, MATH-500 | result-1c9e40 | 456.6 | 450 [443, 456] | 449 [443, 456] | run-04/r6-account-rival, r6-m06 |

**Rival pairs** (`pairs.json`, `duplicates.json`). Six jobs (surprises 1 to 6) wrote 12 rivals; the judge dropped 10,
leaving s1-b (the plain base's confident wrong answers repeat across samples, so the vote locks onto them) and s6-b
(Code-RL's directions hold a format part that saturates by 0.5x and a dose-graded correctness part). No pair survived
whole: a dropped rival has a stand-in only when it restates a carried mechanism, and in every pair at least one
member restated a mechanism that is not carried (run-02/f2-m01, r5-m03-rival, run-02/f2-m02, round-11/s2-b) or
another rival. So `cells` did nothing: no `cells.json`, `experiments.md`, routes or free targets. The m21 pair (s2)
named a cell, the same edit with the cue on the same 250 problems, quick wrong answers: s2-a (an incomplete
sample-by-sample register switch the cue completes) 7 [2, 14] against s2-b (Code-RL's terse stop policy, which the cue
does not remove) 40 [26, 56], in the proposal only; s2-a restates r5-m03-rival and s2-b round-10/problems-m06, and no
blind forecast of the cell exists.

**SPEC_round12 hypotheses.** Z1 (12 or more new numbers from 4 or more results): holds, 23 from 6. Z2 (a carried
mechanism with gain on 8 or more results): holds, 13 mechanisms (run-05/f2-m01 and run-06/f2-m03 on 10;
round-09/grader-m01 +2.39 on 12). Z3 (2 or more new surprises): holds, 5. Z4 (the m21 surprise gets a pair with
disjoint blind intervals on a named cell): refuted, both members were judged restatements and no cell was forecast.
Z5 (under 25 minutes): holds, 12.4.

**Forecasts written after their result.** round-11 t07, t08, t11, t12 (result-dd9239 posted 20:07:48; round 11's
forecast jobs wrote 20:08:53 to 20:12:26), and older rows still in carried records: round-09 t04-t07 (result-6832a8,
17:54:56) for all round-09 lens mechanisms, t13-t14 (result-d02d46, 17:56:01) for the problems, training, grader,
sampling and stopping lenses, t08-t12 (result-306787, 18:00:54) for sampling and stopping (lens jobs finished 17:55:36
to 18:03:05). Every such job read the board snapshot taken before the result, so none saw it, but the record rule
"measured after the forecast" is broken: `find_measured` takes results from the snapshot time, not from the time each
forecast was written.

Files in `results/wide/round-12/`: `standing.md` / `standing.json` / `standing/`, `graveyard.json`, `surprises.md` /
`surprises.json`, `targets.json` / `work.md` (20 targets), `pairs.json`, `duplicates.json`, `mechanisms.json` (42
carried + 2 new), `forecasts.json` / `forecasts.md`, `run.json`, `round12.log`, `jobs/`.

## Round 13 (engine 13, direct tests before forecasts)

Plan `specs/SPEC_round13.md`. Board work-d758db. First end-to-end run of engine 13: a mechanism forecasts only if it
holds a direct test on stored data. Board snapshot 2026-11-15T21:27:03 UTC. Command (run three times: to a crash, to
the gate, past the gate):

```
uv run studies/theory/lib/forecast.py round studies/theory/results/wide/round-13 --from studies/theory/results/wide/round-12 studies/theory/results/wide/round-11 studies/theory/results/wide/round-10 studies/theory/results/wide/round-09 studies/theory/results/forecast/run-0{2,3,4,5,6,7,8} studies/theory/results/forecast/cells-01
```

**Minutes per stage** (UTC, from file times and `round13.log`). standing 1.7 (21:25:23 to 21:27:03); surprises 0.0;
targets 2.7 (to 21:29:46); carried direct-test plans 1.5 (to 21:31:18); propose crashed at once. 18 minutes lost:
the crash was seen only at 21:47 (the coordinator's watcher matched its own command line). Resumed 21:49:16: propose
6.0 (6 jobs, 5 sent back once), duplicate judge 0.8, gate at 21:56:04. Running time to the gate 12.6 minutes; wall
clock 30.7. Direct tests: the 5 carried plans ran from 21:35 (4 to 8 minutes each, 5 agents in parallel), the 12
rival plans from 21:53 in 6 agents (3.4 to 7.3 minutes each); the last row at 22:04:11. Past the gate 5.9 minutes
(forecasts 1.9, routes, check and blind forecasts 4.0), done 22:10:07. Whole round 44.7 minutes of wall clock.

**Fixes** (each committed, then resumed). (1) `prompts/surprise_propose.md`, `routes_propose.md`, `cells_propose.md`:
the no-git rule's `$(git rev-parse HEAD)` is an invalid `string.Template` placeholder; escaped as `$$`. (2)
`lib/forecast.py`: a resumed round read the current board, not the board at its snapshot, so the resumed propose
and forecast jobs saw result-2a5195 (posted 21:27:39, 36 s after the snapshot), which answers targets t03 to t09; the
readers' t03 to t08 centres equal its measured numbers. Fixed after the forecasts were written; no score is affected
(a forecast written after its result is not scored, rule 11.1), but t03 to t09 cannot score anyone. (3) No code
change: a test undecided by its frozen rule gets a row in `direct_tested.json` with verdict `undecided` (not
holding, not refuted, not in `refuted.json`), so it can be tested again.

**Standing** (`standing.md`). 95 mechanisms scored, 44 carried. The top four by gain are all cause-refuted
(run-05/f2-m06 +8.21, run-06/f2-m03 +6.73, run-02/f2-m01 +6.69, run-05/f2-m01 +6.49). Top carried untested:
run-05/f2-m03 +5.14 (skipped by the planner: its m21 cell forecast missed), round-10/weights-m06 +1.85, run-08/f2-m02
+1.72, round-09/grader-m01 +1.67, run-08/f2-m06 +1.56, round-09/training-m01 +1.44. 14 surprises, 1 new
(round-09 m11-r1, result-f8e596, 20 cap hits against readers 40-42).

**Direct tests** (17 plans, `direct_tests.md`; one opus agent per plan or per pair sharing one data file; details in
"Direct tests" below). Carried: round-09/training-m01 holds (template-01: drift 57 vs 63 of 328, D -1.8 points
[-6.4, +2.7], null seed scatter 2.7); round-09/grader-m01 refuted (cue100-01: step-100 cue minus plain +8.5 of 500
[+1.25, +15.5]); run-08/f2-m06 refuted (abstain-01: 0 vote-right problems flipped, threshold 2); round-10/weights-m06
undecided (rank1-01: rank-1 edit +7.2 points [1.7, 12.6] on base-finished-wrong problems, about as much as directions
2-8); run-08/f2-m02 undecided (capbox-01: 6.1 % of RL's native cap-hit rows credited, needed 10 %). Rivals (two per
surprise; the judge called all 12 restatements of older mechanisms, reported only):

| rival | surprise | test | verdict | deciding number (90 %), n, null |
|---|---|---|---|---|
| s1-a: the 4,096 cap removes every right route | autobench final 139 of 328 | karpcap-01 | holds (proxy) | lost problems with every right base sample > 4,096 tokens 0.714 [0.595, 0.833], n 42; matched won 0.173, n 133 |
| s1-b: agreeing short wrong answers | same | karpagree-01 | refuted | agreement excess 0.064 [-0.130, 0.236] (needed 0.10); base's own agreement 0.167 |
| s2-a: partial opening switch | m21 60 quick wrong | m21open-01 | refuted | answer-first share 0.25 [0.17, 0.35], n 60 (floor 0.40); plain base 0.21 |
| s2-b: code-commit policy | same | m21hard-01 | refuted | solve-rate gap 0.005 [-0.066, 0.075] (needed 0.10); plain base's quick wrong problems |
| s3-a: wrong answers split, right answer wins as mode | vote over 12, 466 | votesplit-01 | holds | gained problems right in < 6 of 12: 0.667 [0.476, 0.810], n 21; merged-wrong null keeps 0.381 |
| s3-b: the vote over 4 loses to ties | same | votetie-01 | refuted | 0.095 [0.000, 0.190], n 21 (needed 0.60) |
| s4-a: Code's directions add right programs, Math's add finishes | Code top-8 1.5x, 399 | codepass-01 | holds (point) | pass rate among finished, Code minus random +7.0 points [3.7, 10.3]; Math/Code ratio 0.21 [-0.46, 0.62], n 538 |
| s4-b: the edit sharpens the base onto its own programs | same | sharpen-01 | holds | extra passes in the base's solved set, edit minus random +0.055 [-0.029, 0.139] (refuted below -0.10), n 113 vs 63 |
| s5-a: cap and time budget set the dev100 ceiling | autobench dev100 84 | devcut-01 | undecided | per-sample rows only in a Modal Volume the team cannot read |
| s5-b: plain T 0.6 wrong answers share one mode | same | devmode-01 | undecided | same; null ready, G_cue 0.40 [0.34, 0.46] |
| s6-a: Code top-8 repairs the answer contract | Code top-8 1x, 386 | codecontract-01 | refuted | contract share of fixes 0.43 [0.35, 0.51] (needed 0.50); random 0.37 |
| s6-b: the code gap is per-sample reliability | same | codereliab-01 | holds | fixes the base solves elsewhere 0.75 [0.68, 0.82], n 100; all base failures 0.48; RL-Code's fixes 0.74 |

**Who forecast** (`mechanisms.json`, `forecasts.json`, `forecasts.md`). 7 holders: round-09/training-m01,
round-10/weights-m03 (held host-01 in round 12, not distinctive), and s1-a, s3-a, s4-a, s4-b, s6-b; plus the two
readers. On the 25 targets, one holder forecast is disjoint from both readers: s4-b on t04 (Math 1x + Code 1x on code,
second new seed) 416 [407, 427] against 401 [398, 404] and 401 [397, 405]. result-2a5195 had already measured 401
before the forecasts were written (the readers saw it through bug 2), so s4-b was already wrong there. On targets
still open no holder differs from both readers. Pairs whose both rivals hold: s4 only, and it named no cell. One
no-reward route, r13-n01 (from s4-b): cued base, T 1.0, min-p 0.05, vote over 4, hard328 shard 0/8, 230 GPU minutes
(proposer's guess). Blind forecasts of right of 41: readers 23 [18, 28], s1-a 21 [16.5, 25.5], s3-a 22.5, s4-a, s4-b
and s6-b 23 against the stored 22: margin +0.31 sd, no separation; work-180a48 already found no truncation rule beats
untruncated sampling at T 1.0. No cell split; nothing in `experiments.md` is worth GPU time. Command, not run:
`bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set hard328 --shard 0/8 --temperature 1.0 --top-p 1.0 --min-p 0.05 --samples 4 --seed 3000000 --commit COMMIT_SHA`.

**SPEC_round13 hypotheses.** R1 (2 or more new mechanisms hold against a stronger null): holds, 5 (s1-a on a proxy,
s4-a on point estimates). R2 (gate under 20 minutes): holds on running time (12.6), refuted on wall clock (30.7, the
crash). R3 (proposals agree with the direct facts): holds; s1-a and s5-a restate run-02/f2-m01 but agree with its
refuting number (median right length 3,921 tokens), and s2-a's test does not rest on the refuted r5-m03-rival. R4
(2 of 3 plans well posed): refuted, 6 of 17 failed the check: s5-a and s5-b could not run (rows not readable), s1-a
and s1-b ran only on proxies, s4-b's test cannot refute it against s4-a, s2-a's gap test could not separate the pair;
9 more plans needed a fix before computing (a shared seed, a double-counted denominator, a wrong field name). R5 (a
ranked cell from holders): refuted, no cell.

**What the round shows.** The gate works as a filter: 8 of 17 plans refuted, 4 undecided, 6 hold, and the top
forecast-gain mechanisms no longer forecast. But what holds is weak: the holders forecast nothing on open work that
the readers do not. The good pair was s3: its two tests count complementary parts of one set, so exactly one could
hold, and one did. The s4 pair's tests measured different numbers, so both held.

Files in `results/wide/round-13/`: `standing.md` / `standing.json` / `standing/`, `graveyard.json`,
`direct_facts.json`, `surprises.md` / `surprises.json`, `targets.json` / `work.md` (25 targets), `direct_tests.md` /
`direct_tests.json` (17 plans), `pairs.json`, `duplicates.json`, `jobs/` (plans and rival files), `mechanisms.json`
(7 holders), `forecasts.json` / `forecasts.md`, `cells.json` / `cells.md` / `cell_forecasts.json`, `experiments.md`,
`run.json`, `round13.log`.

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

Page of the forecasts of open GPU numbers (results/forecast/run-NN): `tools/finding_forecasts_before_results.py`, served at `/finding/forecasts-before-results`. After new scores: `uv run tools/finding_forecasts_before_results.py --write`, then run it with no argument to check.

Page of the engine's record: `tools/finding_theories_on_trial.py`, served at `/finding/theories-on-trial`: every prediction of every round as one mark (interval and measured number) against the readers with no theory. After a new round: `uv run tools/finding_theories_on_trial.py --write`, then the check, then names for the new theories in NAMES.

Page of the self-opened draw (selfopen-01): `tools/finding_base_opens_itself.py`, served at `/finding/base-opens-itself`; running the file checks it against `results/experiments/selfopen-01/`.

Page of the gap account (run-02): `tools/finding_where_the_gap_goes.py`, served at `/finding/where-the-gap-goes`; its numbers are read from `results/account/run-02/check/` and `python3 tools/finding_where_the_gap_goes.py` checks them.

## Direct tests

One test per top mechanism of the claim only its stated cause makes, offline where stored data decides it.

### reward-01: run-06/f2-m03's cause (result-82eb02, refuted)

Claim: the change concentrates in a few directions because the outcome reward pays only for a gradable final answer.
Readout: mean over 224 matrices of the top-8 share of squared singular values of (model - base), from the stored SVD rows of
job abaybektursun-1114-221259-0871. RL-Zero-General (LM-judge reward on chat, no gradable answer) 0.127 [0.115, 0.139];
Math 3.0 0.135, Math 3.1 0.118, Code 3.0 0.174, IF 0.206; Think-SFT 0.030; Gaussian floor 0.005-0.008. General sits
P = 0.685 [0.609, 0.765] of the way from Think-SFT to Math/Code/IF 3.0 (90 % bootstrap over 32 layers); the spec's rule,
refuted if the lower bound is 0.5 or more, was fixed after the summary means had been seen. Size-matched (Code 3.0 at step
100) +0.005 [-0.008, 0.019]. The rivals run-05/f2-m01 and run-05/f2-m03 predict nothing here. Not tested: whether any
sequence-level reward concentrates; General's directions do not finish math (88 cap hits vs 77). Row added to
`results/refuted.json`.

| Path | What |
|---|---|
| `specs/SPEC_direct_reward.md` | Plan, decision rule, rivals' predictions. |
| `analysis/direct_reward.py` | `extract` (per-matrix table from the job's `metrics.json`), `analyze` (readout). |
| `data/direct_reward/top8_share_v1.json` | Per-matrix top-8 share and norm of 16 keys (input). |
| `results/direct/reward-01/` | `readout.json`, `examples.json` (matrix where General most exceeds Math 3.0, and most falls below), `run.json`. |

### dial-01: run-05/f2-m01, "a signed termination dial, no added skill" (board work-1645c5, result-124593, refuted)

Claim tested: base + 1.5x Math 3.1's top-8 directions gains by finishing, not by being right more often. Readout: condition
on one cued-base sample per problem (finished-right FR, finished-wrong FW, cap hit CH, pooled over the 4 choices) and
compare the edit's right rate with a second base sample on another seed (and with RL plain). hard328 (4 samples each, n 396
FW conditioning samples on 201 problems): on FW the edit is right 36.4 %, the second base sample 22.9 %, RL 35.2 %: edit
minus base +13.5 points [9.7, 17.3], RL +12.3 [8.8, 15.9], edit minus RL +1.2 [-1.2, 3.6]. Right per finished answer on FW
+7.0 [2.6, 11.3]. On the 191 problems where no base sample hits the cap: edit 85.9 %, base 75.8 %, +10.1 [7.5, 12.8] (RL
+9.0). Of the edit's gain over the second base sample, 42 % sits in FR, 32 % [25, 38] in FW, 26 % [20, 33] in CH. MATH-500
(edit 1 sample, base and RL 4): FW +17.8 [11.0, 24.8] (RL +19.2); CH share 11 %. Verdict by the frozen rule: adds skill,
like RL, on both sets. Signed side: at -1x, on problems where the -1x sample finishes, it is right 51.5 % against 70.0 % for
the base's finished samples (hard328, 227 problems, -18.5 [-22.6, -14.3]); MATH-500 odd 250: -8.0 [-11.9, -4.1]. Only 2 of
114 and 2 of 42 of its finished wrong answers hold the gold string, so the loss is not answer format. The 8 directions carry
finishing and right answers together in both signs; they are not a pure finishing dial. 10 raw answers read
(`reading.md`): the edit's right answers on FW problems are derivations, graded correctly. Row added to
`results/refuted.json`.

| Path | What |
|---|---|
| `specs/SPEC_direct_dial.md` | Claim, refuting observation, frozen verdict rule (written and pushed first, bafbd38). |
| `analysis/direct_dial.py` | Readout from committed rows (hard328, MATH-500, cell-r9-m11-01) and the -1x hard328 job's rows. |
| `results/direct/dial-01/` | `readout.json`, `examples.json` (edit right and wrong on base-FW problems), `m1x_hard328_rows.jsonl`, `reading.md`, `run.json`. |

### input-01: run-05/f2-m03, "a direction acts only as far as the text drives its input subspace" (board work-cd2924, undecided offline)

Claim tested: within hard328, the top-8 edit's effect on a problem is proportional to how strongly that problem's text drives
Math 3.1's top-8 input subspace. Drive D per problem: trace-01's r = ||diag(s) V^T x|| / ||W_base x|| (the relative change the
edit makes to the matrix output), mean over the first 6,000 tokens of the base answer, 3 matrices, 4 layer bands. Effect per
problem: 4 edit sizes (0.5 to 2) against the 2 random rank-8 arms, in log length and in finishing. Statistic b = slope of
effect on D / mean(D), divided by the mean effect: f2-m03 predicts 1, its rival f2-m01 (same on every text) 0. Result, n 328:
drive barely varies across math texts (CV 6.8 %, top over bottom tertile 1.13 [1.12, 1.15]) and follows answer length
(Spearman 0.58). With difficulty controlled, b = -1.0 [-11.4, 6.2] for finishing and -11 [-56, 56] for length; with D shuffled
b already spans [-3.2, 3.6], so 0 and 1 cannot be told apart. The frozen primary (length, no control) gave -64 [-252, -30] and
the rule "refuted", but that number measures answer length, not drive (spec, Amendment 1). The claim that separates the
rivals is cross-domain, and no code-text activation is stored. Cheapest deciding cell: `jobs/xreward_trace.py` on the
base's stored Code-cue answers of HumanEval+/MBPP+ (538), conditions math31, code31, random; f2-m03 predicts Math's drive on
code text at about 0.54 of its drive on math text.

| Path | What |
|---|---|
| `specs/SPEC_direct_input.md` | Claim, refuting observation, rival's prediction (pushed first, 8eb2244), Amendment 1. |
| `analysis/direct_input.py` | Readout from trace-01's per-position drive (`runs/abaybektursun-1115-005830-2145/trace_00*.npz`) and 7 hard328 cells' `answers.jsonl` (Modal Volume `iterate-runs`). |
| `results/direct/input-01/` | `readout.json`, `examples.json` (a high-drive and a low-drive problem that the edit shortens as much), `run.json`. |

### drive-01: run-05/f2-m03 across domains (board work-c51f89, refuted)

Claim tested: Math 3.1's top-8 directions moved code accuracy about half as far as Code's own (368 against 399 of 538,
random 331: transfer 0.54) because code text drives their input subspace about half as much as math text. Readout: trace-01's
per-answer drive D (r = ||diag(s) V^T x|| / ||W_base x||, mean over the first 6,000 answer tokens, 3 matrices, 4 bands) on the
538 base Code-cue answers (new job) over the same on the 328 hard328 math answers (trace-01). Result:
R_math = 0.869 [0.861, 0.877] (90 % bootstrap over texts); random rank-8 control 0.990 [0.988, 0.991]; R_math / R_rand 0.878
[0.870, 0.887]. Frozen rule: above 0.85 refutes. Every band (0.85 to 0.88) and matrix (0.86 to 0.88) agrees. Reverse
(secondary): Code 3.1's directions on math text over code text 0.686 [0.679, 0.693], against a predicted 0.45 to 0.47. So the
Math subspace is driven by code text at 87 % of its math level, while its accuracy transfer is 54 %: input drive does not
explain the half transfer. Check: 16 re-traced math answers match trace-01 within 0.07 %.

| Path | What |
|---|---|
| `specs/SPEC_direct_drive.md` | Claim, verdict rule, control (pushed first, 12f9227). |
| `prep/drive_inputs.py` | Builds `data/drive/code_cue_answers_v1.jsonl.gz` (job abaybektursun-1114-170304-c03c) and `math_check_v1.jsonl.gz`. |
| `jobs/drive_trace.py` | The trace on code text (imports `studies/rlneurons/jobs/xreward_trace.py`); raw output `runs/ih-1115-214816-0563/`. |
| `analysis/direct_drive.py` | Readout, bootstrap, re-trace check. |
| `results/direct/drive-01/` | `metrics.json`, `rows.json` (per code text D of every condition), `examples.json` (highest and lowest drive code text), `run.json`. |

### short-01: run-02/f2-m01, "autobench buys votes with short samples" (board work-4c1119, result-ebf7a4, refuted)

Claim tested (engine 12's plan, with the mechanism's own MATH-500 half added as control): hard328 solutions need 6,000-14,000
tokens, so under 20 % of the hard328 problems the cued base solves have a right sample of 2,000 tokens or fewer, against over
50 % on MATH-500. No other top mechanism predicts anything about the base's solution lengths. Readout from the committed
day1_3 rows (base + cue, T 1.0 / top-p 1.0, 4 samples, cap hits resampled up to 2 times, every row counted), 90 % bootstrap
over solved problems: hard328 72 of 220, 32.7 % [27.7, 38.2]; MATH-500 320 of 474, 67.5 % [63.9, 71.1]. Rule fixed in
advance: refuted if the hard328 lower bound is 20 % or more. Median right length 3,921 tokens [3,541, 4,390] on hard328 (the
cause says 6,000-14,000), 1,594 on MATH-500. At 1,100 tokens 12.7 % [9.1, 16.4] against 50.4 %; at 4,096, 56.4 % against
84.0 %. The contrast holds in direction, not in size: the short right answers sit on easy problems inside hard328 (94.5 % of
their samples right, against 56.6 % on the other solved problems). 10 raw rows read (`reading.md`): AMC and OlympiadBench
problems, right values no guess would give, grading correct; answer texts are not committed. Row added to
`results/refuted.json`. The mechanism was already not carried in round-12 (-1.77 nats).

| Path | What |
|---|---|
| `specs/SPEC_direct_short.md` | Claim, refuting observation, rule (pushed first, 00ccb83). |
| `analysis/direct_short.py` | Readout from `studies/rlneurons/results/day1_3/{hard328_base_cue_s4r2-01,math500_base_cue-01}/rows.jsonl`. |
| `results/direct/short-01/` | `readout.json`, `examples.json` (a solved problem with no short right sample, one with), `reading.md`, `run.json`. |

### ending-01: run-03/f2-m04, "accuracy depends on how the answer ends" (board work-8965b9, refuted)

Claim tested (engine 12's plan): on code, RL-Math's 8 directions at 1.5x add at least 8 finished answers with no code block,
because Math's directions push a boxed ending that displaces the final python block. No other top mechanism predicts it.
HumanEval+ and MBPP+, 538 problems, Code cue, seed 51000000, one sample per cell. Finished no-block answers: cued base 12
[7, 18], random rank-8 at 1.5x 23 [16, 31], Math edit 6 [2, 10], Code edit 1x 0, 1.5x 1. Math minus random -17 [-26, -8]
(rule: refuted if the upper end is below +8); Math minus base -6 [-13, 1]. Answers with `\boxed`: 0 of 538 in the Math cell
(base 1). The Math edit removes no-block endings, as every finishing edit does (cap hits 27 to 1). The 10 raw answers read
(`reading.md`) end in broken fences or stop before the code, never in a box. The posted count (result-a1bf75: 6 no-block
answers in the Math cell) already bounded this; the test adds the finished split and the intervals. Only 1.5x exists; no
Math-alone 1x code cell. Row added to `results/refuted.json`.

| Path | What |
|---|---|
| `specs/SPEC_direct_ending.md` | Claim, derivation check, frozen rule (pushed first, a236bf4). |
| `analysis/direct_ending.py` | Readout from 5 code cells' `answers.jsonl` (Modal Volume `iterate-runs`, `gpu.py get`). |
| `results/direct/ending-01/` | `readout.json`, `examples.json` (Math edit: finished no-block, finished with block and failed), `reading.md`, `run.json`. |

### host-01: round-10/weights-m03, "an added RL change depends on its host" (board work-ae598b, result-3abd6f, holds, not distinctive)

Claim tested (engine 12's plan, sharpened): Think-SFT's own weight change lies in RL-Math 3.1's top-8 input (right singular)
subspace more than chance, and more than in the top-8 input subspace of the same rank in the same matrix from non-math
changes. Readout: cap_right = ||d_ThinkSFT V||^2 / ||d_ThinkSFT||^2 per matrix (stored rows of job
abaybektursun-1114-221259-0871), 224 matrices, 90 % bootstrap over matrices. Share inside Math 3.1's subspace 0.0088 =
4.80x the random rank-8 expectation 8/n_in [4.55, 5.08] (over layers [4.35, 5.35]); the plan's 2x holds. Against
structured nulls: 2.23x [2.12, 2.34] IF-RL 3.0's subspace, 1.99x [1.89, 2.08] General-RL 3.0's, but 1.33x [1.28, 1.39]
the base matrix's own top-8 (above it in 188 of 224 matrices). Verdict by the frozen rule: holds, not distinctive (needed
1.5x over every null). Positive control: Math 3.0's change sits 49x chance and 6.8x the base subspace, so the instrument
shows a specific overlap where one exists. Think-SFT sits almost as much in Code 3.1's and Math 3.0's subspaces (Math 3.1
over them 1.19x, 1.10x): it shares the input directions of reasoning RL in general, not of math RL. Output side (cap_left)
1.11x to 1.32x the nulls. run-05/f2-m03 predicts the same overlap, and weights alone cannot show the overlap shrinks
RL's effect; that needs Think-SFT + RL with the overlapping part projected out. Row added to `results/direct_tested.json`.

| Path | What |
|---|---|
| `specs/SPEC_direct_host.md` | Claim, why the plan's chance level is weak, frozen verdict rule (pushed first, 07a692f). |
| `analysis/direct_host.py` | `extract` (per-matrix caps from the job's `metrics.json`), `analyze` (readout). |
| `data/direct_host/cap_v1.json` | Per-matrix cap_right, cap_left, cap_both of Think-SFT, Math 3.0, Code 3.1 against 11 subspaces (input). |
| `results/direct/host-01/` | `readout.json`, `examples.json` (matrices with the largest and smallest ratio over the base subspace), `run.json`. |

### cue100-01: round-09/grader-m01, "step-100 cue and plain pool to one level" (board work-6b73e9, result-6ecd35, refuted)

Claim tested (engine 13's plan): at RL step 100 the cue adds nothing beyond seed scatter on MATH-500. The 4 stored samples per arm pooled, the paired cue-minus-plain difference is D = +8.5 problems per 500, 95 % [+0.24, +16.75] (90 % [+1.25, +15.5]), label-permutation p 0.044, n 500 problems. That meets the frozen rule, so the claim is refuted, but only just: 2.5 % of bootstrap D values are at or below 0. All 16 single-sample cue-minus-plain pairs are positive (+1 to +20); pairs within one arm differ by at most 11 (seed-folder null +0.7, +1.3). Positive control: step 400 plain minus step 100 plain +20.25 [12.0, 28.5]. In the raw rows the cue moves problems both ways, often through cap hits; net 73 problems gain one right sample, 46 lose one. result-6832a8 had not decided it (lower end 0.00, no permutation p).

| Path | What |
|---|---|
| `specs/SPEC_direct_cue100.md` | Claim, null, frozen rule (pushed first). |
| `analysis/direct_cue100.py` | Readout from the four `studies/rlneurons/results/ckptcue/s0100_*` folders. |
| `results/direct/cue100-01/` | `readout.json`, `examples.json`, `reading.md`, `run.json`. |

### abstain-01: run-08/f2-m06, "a cap hit casts no vote" (board work-37a3db, result-3605ba, refuted)

Claim tested (engine 13's plan): on hard328, letting Think-SFT's 16,384-token cap hits finish inside a 4-sample vote turns 2 or more vote-right problems wrong. Vote of 3 stored Think-SFT + cue 16,384-cap samples plus its cap-32,768 row: scored at 16,384 (a longer row abstains) 240 of 328; at 32,768 (it votes) 245; the null, where wrong converted rows abstain, also 245. No problem the vote had right turned wrong (D = 0, threshold 2), so the claim is refuted. The vote gain is 0.22 of the 23-problem single gain, 95 % [0.05, 0.40], below half as predicted, but the ceiling account predicts that too. All 5 gains are problems where every native sample hit the cap. Reported only: the frozen tie rule (shortest row) gives the converted row's 9 ties to the native row; random ties give D 4.5; the 4-converted-row run (branch cap32vote) gives D 3 and a cost of 9 [4, 15]. RL contrast: D 1.

| Path | What |
|---|---|
| `specs/SPEC_direct_abstain.md` | Claim, abstention null, frozen rule (pushed first). |
| `analysis/direct_abstain.py` | Vote readout from cap32 and thinkvote rows. |
| `results/direct/abstain-01/` | `readout.json`, `examples.json`, `reading.md`, `run.json`. |

### rank1-01: round-10/weights-m06, "direction 1 adds finishes, directions 2-8 add right answers" (board work-2843ca, result-efc74d, undecided)

Claim tested (engine 13's plan): on hard328 problems where a cued-base sample finished wrong, the rank-1 edit (direction 1 per matrix of RL-Math 3.1's change, 1x) is right no more often than a second base sample, while directions 2-8 at 1.5x are. Selector: base samples on seeds 3,020,000 and 3,030,000 (the plan's selector shared seed 3,000,000 with the rank-1 cell, whose rows correlate with it; moved before computing). Rank-1 edit +7.2 points [0.7, 13.6] (95 %), directions 2-8 +9.3 [3.0, 15.8], gap +2.1 [-6.1, 10.5], n 190 pairs on 139 problems; second base sample right 21.8 %, random rank-8 +0.4, top-8 1.5x control +14.0 (result-124593: +13.5). Neither refuting threshold is met, but "holds" needed the rank-1 gain below half the 2-8 gain: undecided, does not hold. Direction 1 adds right answers about as much as directions 2-8, with full derivations. Rank-1 rows from job abaybektursun-1115-000358-d11a (Modal Volume). Row in `direct_tested.json` with verdict undecided (not in `refuted.json`).

| Path | What |
|---|---|
| `specs/SPEC_direct_rank1.md` | Claim, selector change, frozen rule (pushed first). |
| `analysis/direct_rank1.py` | Readout from the base, rank-1, directions-2-8, top-8 and random rows. |
| `results/direct/rank1-01/` | `readout.json`, `examples.json`, `reading.md`, `run.json`. |

### template-01: round-09/training-m01, "the template moves the answer, not the drift" (board work-996b09, result-ab26c4, holds)

Claim tested (engine 13's plan): Think-SFT's own ChatML `<think>` template does not make it drift less. Drift signs of `studies/rlneurons` `drift.py` (a non-Latin script switch or a repeated 50-token window) on the first 16,384 generated tokens of each hard328 row: own template 57 of 328, raw template with the cue at cap 32,768 63 of 328, D = -1.8 points, 95 % [-7.3, +3.7] (90 % [-6.4, +2.7]). The four stored raw-cue samples drift on 57 to 66 rows (null S_max 2.7 points), so D sits inside seed scatter: holds. The rival run-04/f2-m05 predicted a clear drop in the own template. Instrument: the planted tests pass and describe-01's counts (156 of 1,312, 83 of 328) reproduce. The repeat sign also fires on harmless restatements of the problem, 27 rows in each cell. Weak hold: one sample per template, and the interval allows a 7-point drop. No raw-cue finished-wrong row (0 of 96) held the right answer after a bare "Answer:" line, so the mechanism's answer-placement half is not supported on hard328.

| Path | What |
|---|---|
| `specs/SPEC_direct_template.md` | Claim, null, frozen rule (pushed first). |
| `analysis/direct_template.py` | Drift readout on native hard328-01 and cap32 sft_cue rows. |
| `results/direct/template-01/` | `readout.json`, `examples.json`, `reading.md`, `run.json`. |

### capbox-01: run-08/f2-m02, "a native 16k run credits boxes written before the cut" (board work-cb6617, result-a9b0bc, undecided)

Claim tested (engine 13's plan): in native 16,384-cap hard328 runs grader v3 credits a right answer to 10 % or more of RL plain's cap-hit rows, more than Think-SFT's share. The premise holds (68 % of RL's native cap-hit rows hold a box; base 15 %, Think-SFT 11 %), but v3 credits 7 of 114 (attempt 0, 4 samples), 6.1 %, Wilson 95 % [3.0, 12.1]; Think-SFT 14 of 378, 3.7 %; RL minus Think-SFT +2.4 points [-2.4, +8.1]. Undecided by the frozen rule, does not hold (with restart rows 9 of 171, upper bound 9.7 %: refuted). The 7 credited RL rows are finished solutions followed by a restated write-up that ran into the cap, not boxes written mid-reasoning. Cutting cap32 texts at 16,384 credits RL 2 of 20 and Think-SFT 4 of 93 rows the rescore counts wrong: the rescore loses 2 to 4 problems of 328. Grader checks pass (gold box appended: all right; wrong box appended: all wrong). Row in `direct_tested.json` with verdict undecided.

| Path | What |
|---|---|
| `specs/SPEC_direct_capbox.md` | Claim, nulls, frozen rule (pushed first). |
| `analysis/direct_capbox.py` | Readout from native 16k rows and cap32 rows. |
| `results/direct/capbox-01/` | `readout.json`, `examples.json`, `reading.md`, `run.json`. |

### codepass-01: round-13/s4-a, "Code's directions add right programs, Math's mostly add finished ones" (board work-ef2d53, result-d15c5e, holds on point estimates)

Claim tested (the rival's own plan): among finished answers with a code block, Code's top-8 directions at 1.5x raise the HumanEval+/MBPP+ pass rate by 3 or more points over the random rank-8 1.5x edit, and Math's top-8 at 1.5x by less than half of that. Pass rates per finished-with-block problem, 538 problems, one sample per cell: Code 399/533 = 74.9 %, Math 368/531 = 69.3 %, random 331/488 = 67.8 %. dC = +7.0 points, 90 % [3.7, 10.3]; dM = +1.5 [-2.2, 5.1]; dM/dC = 0.21 [-0.46, 0.62] (paired bootstrap). The frozen rule holds on point estimates, but the ratio interval contains rival s4-b's 0.54. On problems both cells finished the ratio is 0.36. Planted control (Math's columns replaced by Code's) gives ratio 1.0 and "refuted". The plan's denominator counted cap hits without a block twice; fixed to a per-problem count (random 488, not 466) before computing.

| Path | What |
|---|---|
| `specs/SPEC_direct_codepass.md` | Claim, rival's prediction, frozen rule (pushed first). |
| `analysis/direct_codepass.py` | Readout from `studies/rlneurons/results/xreward/code_dial` cells. |
| `results/direct/codepass-01/` | `readout.json`, `examples.json`, `reading.md`, `run.json`. |

### sharpen-01: round-13/s4-b, "the edit sharpens the base onto its own programs" (board work-8e9805, result-63cacd, holds)

Claim tested (the rival's own plan): the Code top-8 1.5x edit's extra passes over the cued base fall on problems the untrained base solves under another prompt (plain or Math cue; set U, 378 of 538) as often as the random rank-8 1.5x edit's extra passes do. Of the 221 problems the cued base fails, Code 1.5x passes 113, 78 in U (0.690); random passes 63, 40 in U (0.635). D = +0.055, 90 % [-0.029, 0.139]; refuted only if D < -0.10: holds. The null is not saturated: a cued-base failure lies in U 43 % of the time, and a planted arm (base with the Math cue) reads 1.0. Of the 61 problems only Code adds, 41 (0.67) are in U. In the raw rows most extra passes are easy problems the base missed by a slip (a missing import, leftover template text, an edge case) or a cap hit. Weak separation: rival s4-a does not strictly forbid D near 0, so this fails to refute s4-b without refuting s4-a.

| Path | What |
|---|---|
| `specs/SPEC_direct_sharpen.md` | Claim, floor and planted control, frozen rule (pushed first). |
| `analysis/direct_sharpen.py` | Readout from `code1` base cells and `xreward/code_dial`. |
| `results/direct/sharpen-01/` | `readout.json`, `examples.json`, `reading.md`, `run.json`. |

### votesplit-01: round-13/s3-a, "wrong answers split, the right answer wins as the mode" (board work-5d6316, result-4c9189, holds)

Claim tested (the rival's own plan): most problems the vote over 12 gains over the vote over samples 0-3 have the right answer in under half of the 12 samples. Cued base, MATH-500, 12 samples at T 1.0 (rows of result-1c9e40); the team's vote (`votek.vote`, `rln4_lib.agree`) gives back the posted 446 (k = 4) and 466 (k = 12). Gained set G: 21 problems (22 flip right, 1 flips wrong). 14 of 21 have the right answer in under half the samples: S_a = 0.667, 90 % [0.476, 0.810]: holds. Example: problem 166, right answer twice against eight different wrong values. Null, wrong answers merged into one value per problem: keeps 8 of 21 gains (0.381, refuted at 0.80 or more), so 13 gains need the wrong answers to split. Caveat: 3 of the 14 win because most samples are cap hits that cast no vote; without them 11 of 21 = 0.524. n is small.

### votetie-01: round-13/s3-b, "the vote over 4 is pulled down by ties" (board work-5d6316, result-4c9189, refuted)

Same rows, vote and G (21). Only 2 of 21 were k = 4 ties with the right answer in a tied top group and right in at least 6 of 12: S_b = 0.095, 90 % [0.000, 0.190] (refuted below 0.60). Ties with a right group are common in G (9 of 21), but 7 of those 9 have the right answer in under half the samples. Null (k = 4 failures with a right sample that k = 12 does not fix, n 7): 0.143; difference -0.048 [-0.286, 0.143]. S_a and S_b count complementary parts of one set, so at most one could hold.

| Path | What |
|---|---|
| `specs/SPEC_direct_vote13.md` | Both claims, nulls, frozen rules (pushed first). |
| `analysis/direct_vote13.py` | Readout from `studies/rlneurons/results/votek/math500_base_cue-01`. |
| `results/direct/votesplit-01/`, `results/direct/votetie-01/` | `readout.json`, `examples.json`, `reading.md`, `run.json`. |

### karpcap-01: round-13/s1-a, "the 4,096 cap removes every right route" (board work-f5966a, result-4b64da, holds on a proxy)

Claim tested (the rival's plan, on a proxy): the hard328 problems the kept autobench method (plain prompt, T 0.6, 12 votes, cap 4,096) loses although the cued base solves them (2 or more of 4 samples) are lost to the 4,096-token cap. The 12 samples per problem are not stored where the team can read them (frustea's Modal Volume; only the per-problem winners are committed), so the cap-hit share is replaced by the share of problems whose right cued-base samples are all longer than 4,096 tokens. finals-01 reproduces 139 of 328. Lost problems 0.714, 90 % [0.595, 0.833], n 42; matched problems the method gets right 0.173 [0.120, 0.226], n 133; difference 0.541 [0.414, 0.665]: holds. The losing winners look like what a cut sample writes when forced to answer (1, 0, 2024, "Answer").

### karpagree-01: round-13/s1-b, "agreeing short wrong answers" (board work-f5966a, result-4b64da, refuted)

Same 42 problems: the cap removes every right route on 71 % (refuted above 0.35). The method's wrong winner agrees with the cued base's wrong answers at 0.23 (39 pairs), the base's wrong answers with each other at 0.17 (12 pairs): difference 0.064 [-0.130, 0.236], below 0.10. On 19 of 27 comparable problems the winner matches no base wrong answer.

| Path | What |
|---|---|
| `specs/SPEC_direct_karp13.md` | Both claims, the proxies, frozen rules (pushed first). |
| `analysis/direct_karp13.py` | Readout from `studies/autobench/results/math500-loop/finals-01` and day1_3 hard328 rows. |
| `results/direct/karpcap-01/`, `results/direct/karpagree-01/` | `readout.json`, `examples.json`, `reading.md`, `run.json`. |

### m21open-01: round-13/s2-a, "partial opening switch" (board work-16161e, result-cc7288, refuted)

Claim tested (the rival's own plan): cell m21's 60 quick wrong answers (base + Code-RL top-8 at 1x, plain prompt, MATH-500 first 250) are plain-base answer-first replies. 25 % [17, 35] meet the answer-first rule (floor 0.40): refuted. By eye the rule over-counts (rows that start with "(" or echo the prompt's "Answer:"); only 3 to 5 are real answer-first replies. The plain base's own 105 quick wrong answers are 21 % answer-first, so the gap test (0.04 [-0.07, 0.15]) does not separate the rivals. Both sets hold the same failures: prompt continuations, empty replies (10 in m21), web text, short attempts.

### m21hard-01: round-13/s2-b, "code-commit policy" (board work-16161e, result-cc7288, refuted)

The cued base solves the problems behind m21's 60 quick wrong answers at 0.833 (of 4 samples), those behind the plain base's 105 at 0.838, all 250 at 0.814: r_N - r_Q = 0.005 [-0.066, 0.075], below 0.10: refuted. The instrument can fail: m21's long wrong answers score 0.40. Only 2 of the 60 open with "Okay": they are format failures on easy problems, not early-committed deliberation.

| Path | What |
|---|---|
| `specs/SPEC_direct_m21q.md` | Both claims, nulls, frozen rules (pushed first). |
| `analysis/direct_m21q.py` | Readout from `results/experiments/cell-r9-m21-01` and `rln4/t1_t3_items-01`. |
| `results/direct/m21open-01/`, `results/direct/m21hard-01/` | `readout.json`, `examples.json`, `reading.md`, `run.json`. |

### codecontract-01: round-13/s6-a, "Code top-8 repairs the answer contract" (board work-93874a, result-04f363, refuted)

Claim tested (the rival's own plan): the base code failures that Code-RL's top-8 directions at 1x fix are enriched for answer-contract failures beyond what a random edit fixes. The cued base fails 221 of 538 HumanEval+/MBPP+ problems; 73 are contract failures (cap hit 25, no closed block 12, unparsable block 11, no def of the function the tests call 25). The edit fixes 100 failures, 43 of them contract failures: S_top8 0.43, 90 % [0.35, 0.51] (refuted below 0.50); random rank-8 1.5x 0.37 (n 63), difference [-0.02, 0.15]; fix rate on contract over logic failures 1.53 [1.21, 1.93] (needed 2.0): refuted on all three conditions. Most of what the edit fixes is logic.

### codereliab-01: round-13/s6-b, "the code gap is per-sample reliability" (board work-93874a, result-04f363, holds)

Same 100 fixes: 75 are problems that one of two stored base-like cells (base + Math cue, random rank-8 1.5x) passes: Q_top8 0.75 [0.68, 0.82]; among all 221 base failures 0.48; difference [0.21, 0.33] (needed lower bound above 0.10): holds. RL-Code's own 116 fixes give 0.74, the same profile. The edit fixes 22 % of failures no base-like cell passes and 71 % of the others. Caveat: the random cell shares seed and prompt with the edit; with the Math-cue cell alone Q_top8 is 0.56 against 0.35 (difference [0.15, 0.27]), below the plan's 0.60 level. Control: a random subset of base failures in place of the fixes refutes, as it should.

| Path | What |
|---|---|
| `specs/SPEC_direct_code13.md` | Both claims, nulls, frozen rules (pushed first). |
| `analysis/direct_code13.py` | Readout from the 5 code cells' `answers.jsonl`. |
| `results/direct/codecontract-01/`, `results/direct/codereliab-01/` | `readout.json`, `examples.json`, `reading.md`, `run.json`. |

### devcut-01 and devmode-01: round-13/s5-a and s5-b, autobench dev100 losses (board work-ab9ae3, result-cfe997, both undecided)

s5-a: the kept autobench method's dev100 vote losses are samples cut at 4,096 tokens or left unrun by the time budget; s5-b: they go to one shared wrong value. The kept method's per-sample dev100 rows are only in frustea's Modal Volume, so neither statistic can be computed from data the team can read: both undecided (do not hold). Ready for the rows: s5-b's null, the cued base's 12-sample votes, G_cue 0.40 [0.34, 0.46] (34 vote-wrong problems of 500), so s5-b needs G_plain >= 0.52; instrument check on cued-base rows cut at 4,096: dev100 94 to 86 right, D 0.73 [0.50, 0.91], n 14. Rerun: `direct_dev13.py --plain <rows.jsonl>` once the rows are exported.

| Path | What |
|---|---|
| `specs/SPEC_direct_dev13.md` | Both claims, nulls, frozen rules (pushed first). |
| `analysis/direct_dev13.py` | Readout (needs the kept method's per-sample rows). |
| `results/direct/devcut-01/`, `results/direct/devmode-01/` | `readout.json`, `run.json`. |

## Paper: Theories on Trial (`paper/`, board work-184476)

A short paper on the engine's rounds 1 to 7: the theories' own predictions against the two no-theory readers
(nearer count, interval coverage, log gain), the round-6 budget, the contests against rivals, the self-open
experiment and the faults found in the engine's scores. Public at
https://monitor.invariant.team/paper/theories-on-trial.pdf (`tools/view.py` serves `paper/theories-on-trial.pdf`;
`infra/monitor/deploy.sh` ships it).

- `paper/build_facts.py` (`uv run --no-project --with numpy python studies/theory/paper/build_facts.py`): reads the
  committed round files and writes `paper/predictions.jsonl` (one row per prediction), `paper/facts.json` (every
  number of the paper with its value, n, unit and source) and `paper/calibration.json`. Every stored gain is
  recomputed and must match to 0.002. `paper/NOTES.md`: how each headline is computed and what weakens it.
- `paper/figs.py` (`uv run --no-project --with matplotlib --with numpy python studies/theory/paper/figs.py`): draws
  `fig_truth.pdf`, `fig_rounds.pdf`, `fig_duel.pdf` from those files; `paper/fonts/` is TeX Gyre Pagella (GUST font
  licence).
- `paper/paper.tex`, `paper/refs.bib`: the text; `tectonic paper.tex` builds `paper.pdf`, copied to
  `theories-on-trial.pdf` for the site.
- Headline: theories nearer than the readers in 190 of 394 comparisons (48.2 % [39.7, 55.1]); 90 % intervals held
  164 of 236 (69.5 %) against 197 and 202 for the readers (gap -15.0 points [-27.6, -5.1]); log gain -58.85 nats on
  236, -94.27 on 192 without the round-6 budget.
- Review: four independent reviews of draft 1 (number audit, about 200 numbers, 13 corrected; skeptical review;
  check of every description of the engine and every citation; visual review) and one final check of draft 2. The
  main change: authors and readers had different prompts (authors chose the quantities, were asked for predictions
  a reader would not guess, and were not told how intervals are scored), so the paper claims that the theories'
  chosen predictions were no nearer and less often inside their intervals, not that writing a mechanism causes it.
