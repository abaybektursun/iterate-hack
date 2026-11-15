# Account run 02: readout of the independent check

**The three new budgets reproduce exactly: 18 of 18 shares and bootstrap intervals equal the engine's (`check/budget.out.txt`). One cross-cell
difference is firm: at T 0.6 against RL step 400 the loop part takes 0.44 [0.33, 0.53] of 66 gap problems and reliability falls to 0.38
[0.29, 0.47], against 0.63 [0.52, 0.72] in the known cell under the same rules and equal evidence. The share the account got wrong (p16) is
mostly grader v1: 9 of its 25 problems are right answers v1 rejects; the 14 real slips give 0.21, inside the prediction [0.07, 0.25]. At T 1.0 a
fresh base sample's gap has the same budget as RL's within intervals.**
## Budgets (share of gross gap problems, 90 % bootstrap over gap problems, 2,000 resamples, seed 0; unassigned 0 in every cell)

| Cell | Gap / base-only | Loop | Budget | Answer statement | Reliability, full E / E = 3 | Capability, full E / E = 3 |
|---|---|---|---|---|---|---|
| known, r6 rules: MATH-500 T 1.0, base cue vs RL plain | 65 / 12 | 0 | .246 [.169, .338] | .031 [0, .062] | .662 [.569, .754] / .631 [.523, .723] | .062 [.015, .108] / .092 [.031, .154] |
| known as given to the account (hand labels, result-5e17a6) | 65 / 12 | 0 | .246 | .154 | .538 | .062 |
| theta0.5 cue, MATH-500 T 1.0 | 53 / 11 | 0 | .208 [.113, .302] | .038 [0, .075] | .698 [.585, .792] / .642 [.528, .755] | .057 [.019, .113] / .113 [.057, .189] |
| Code-RL cue, hard328 T 1.0 | 37 / 14 | 0 | .270 [.162, .405] | .027 [0, .081] | .432 [.297, .568] (E is 3) | .270 [.162, .378] (E is 3) |
| RL step 400 plain, MATH-500 T 0.6 / top-p 0.95 | 66 / 27 | .439 [.333, .530] | .121 [.061, .182] | .061 [.015, .121] | .379 [.288, .470] / same | 0 [0, 0] / same |
| null: base + random direction cue (fresh sample), T 1.0 | 42 / 35 | 0 | .167 [.071, .262] | .024 [0, .071] | .714 [.595, .833] / .667 [.548, .786] | .095 [.024, .167] / .143 [.071, .238] |

Engine numbers (`metrics_v4.json`, `tests/r6-account/`) equal the full-E column for the three new cells. Per-problem parts: `check/assign.json`.
## What the account predicted right and wrong
- Right: theta0.5 reliability 0.70 against 0.698 (readers 0.53, 0.52; +1.94 nats) and capability 0.04 against 0.057 (+1.18); all 6 hard328
  shares inside; T 0.6 loop 0.50 [0.37, 0.63] against 0.44. The theta0.5 win is mostly a rule change: the known cell under r6's own rules is
  already 0.662, while the account and both readers started from the hand-label 0.538.
- Wrong: T 0.6 reliability 0.379 against 0.15 [0.07, 0.25] (p16, refuting), capability 0 against 0.05 [0.01, 0.11] (p17), answer statement 0.061
  against 0.17 (p15, within noise). Why p16 failed: the account expected v1's misses on the base's answer lines to land in answer statement, but
  its text rule N() does not map ³, √, ∞, \( \), a second box or a copied prompt template onto the gold string, so these rows fall through to
  reliability, where E (4 cued T 1.0 samples, v3) solves them. Hand read (`check/s0400_reliability_hand.json`): 9 v1 misses on right answers,
  2 template echoes, 14 wrong values. p17: with E drawn at T 1.0, every finished-wrong gap problem has kB of 1 or more.
## Comparability
- E (rows behind kB): known, theta0.5, step 400: 4 rows, day1_3 cued base T 1.0 attempt 0, v3. hard328: 3 rows, F_hard (cue, T 0.6, v1), P_hard
  (plain, T 0.6, v1), 7ba0 (plain, T 1.0, v3); 40 of 111 at the cap; these files get 119, 102 and 76 of 328 right, the cell's own base 164.
- Graders: known, theta0.5, hard328 v3 on both sides; step 400 v1 on both sides. Prompts: base always cue; RL side plain (known, step 400), cue
  (theta0.5, Code-RL). Every gap is gross; base-only problems against it: 12, 11, 14, 27 (null 35). day1_3 sample 0 has the T1 base row's seed
  (equal length on 56 of 500 non-cap problems, other samples 0 or 1); in the gaps this touches 1 non-cap problem, which stays in reliability.
- Survive at equal E (90 % intervals apart): loop at T 0.6 against every T 1.0 cell; reliability at T 0.6 (.379) against known .631, theta0.5
  .642 and null .667; capability on hard328 (.270) against known .092 (apart by 0.008); T 0.6 capability 0 (bootstrap [0, 0]) against all.
- Do not survive: hard328 reliability against known (overlap .523 to .568; at full E apart by 0.001); hard328 capability against theta0.5 and the
  null; every budget and answer-statement difference; theta0.5 against known in any part. hard328's E is weaker in kind as well as count, so its
  capability share is an upper bound, as the account said. Null: RL's T 1.0 budget and a fresh base sample's agree within intervals in every part.
## Raw text (`check/rawtext.out.txt`)
- T 0.6 loop 4 and 21: one repeats the Asymptote label block and its recount, the other one paragraph ("a discrepancy of about 140"), to the cap. Fits.
- T 0.6 reliability 25: found both roots, wrote \boxed{-2} and \boxed{1}; v1 graded the last box. A grading failure, not a slip.
- T 0.6 reliability 30: converted 42 to 502_8 (gold 52_8); all 4 T 1.0 samples right. Fits.
- hard328 capability 94: 2583 after a wrong count of permutations (gold 279); 0 of 6 stored base rows right. Fits the rows.
- hard328 capability 157: 899 for gold 901 (both interval ends dropped); 0 of 6 rows right. A repeated boundary slip; the name overstates it.
- hard328 budget 68 and 76: still computing (Grundy values; triangle algebra) at 16,384 tokens. Fits.
- 3 of the 10 hard328 capability problems are right in another stored base row: 207 (forced-commit rows CF_hard and CP_hard; e72c and 7ba0 wrote
  f(m) = m^2 for gold f(n)=n^{2}, the v3 false negative studies/rlneurons/README.md line 754 notes for theta0.5), 348 (CF_hard), 359 (CP_hard).
  7 of 10 are right in none. The hard328 4-sample cued base rows (result-1dedfe) are in another workspace and not readable.
## Novelty
No breakdown of the three new cells is on the board or in git; only gap sizes are: Code-RL hard328 37 fixed, 14 lost (studies/rlneurons/README.md
line 734); theta0.5 53 fixed, 11 lost (result-9b6af3, before.jsonl line 77); step 400 T 0.6 cap hits 98 of 500 (result-32b7a8, after.jsonl line
34). The known cell's breakdown is result-5e17a6 (before.jsonl line 16).
## Hypotheses
- A1 holds (9 of 9). A2 refuted (no gain, -1.30 nats, no unexpected win). A3 not tested (no rival ran). A4 not tested by the stage (no review);
  against the board it fails: every part of 10 % or more has a base-only result (budget 0.246: result-e870a1, result-2c2cae, result-44b4df;
  answer statement 0.154: result-c57b51; reliability 0.538: result-5d032f, result-cbe0bc).
- B1: 3 untabulated cells; readers' centres more than 0.02 from the account on 9 of 18 shares by the readers' mean (holds at the edge), 8 and 7 of
  18 by each reader, 4 of 18 by both (refuted on those readings). B2 holds (20 of 20). B3 refuted (p16; p16 and p17 outside beyond noise;
  total +1.61 nats). B4 holds: T 0.6 loop 0.44 [0.33, 0.53] against 0 in the known cell.
## Faults of the account stage
1. Known shares enter from the board, not recomputed under the account's rules: answer statement 0.154 and reliability 0.538 become 0.031 and
   0.662 under r6's rules, so predicted moves against the known cell partly measure the change of rules.
2. Each cell picks its own E for kB, so the reliability/capability split is not comparable: hard328 uses 3 rows of other prompts, temperatures
   and grader v1 (40 of 111 at the cap); MATH-500 uses 4 rows of the base row's own setting, one sharing its seed.
3. No null cell and gross gaps only: a fresh base sample's 42-problem gap has the same budget within intervals, and 11 to 27 base-only problems
   per cell are not counted, so reliability, the largest part, is not shown to be specific to RL.
4. Shares fixed by construction count as tests: loop at T 1.0 (rule A found 0 loops in the T 1.0 cells T1-T3, knowledge-787e53) and unassigned
   (needs empty E) are 5 of 18 share predictions and give +0.64 of the +1.61 nats (p7 +0.51, p1 +0.13).
