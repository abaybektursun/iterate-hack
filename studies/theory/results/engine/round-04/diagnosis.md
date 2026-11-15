# Round 04 diagnosis

All four hypotheses hold, and the round produced one new, replicated measurement: plain MATH-500 cap hits at T 0.6 / top-p 0.95 rise from 65 (base)
to 103 (RL step 100) and 98 (step 400), then fall to 19 (step 2,800), n = 500 each. But the three survivors are all judged weak, the largest gain
(r4-m10, +9.86 nats) is one contrast counted three times, and the survival rule let through a theory whose distinctive test had the wrong sign.
Sources: `metrics_v4.json`, `theories/*.json`, `tests/`, `predictions/nulltest-{1,2}.jsonl`, `reviews/`, `replication/replication.json`, `inventory.md`.

## (a) Hypotheses

- H1 (at least 6 different mechanisms): holds, 9 groups among the 10 developed theories (round 03: 2 among 10). Rule: two theories are one group if
  no single experiment gives them different predictions. r4-m02 and r4-m06 are one group: both say RL's added checking does not depend on whether the
  answer is right, and the re-check-rate test (r4-m06 p1) measures both. Each of the others stands alone: m01 (loop hazard follows the
  self-similarity of the text so far), m04 (partial delta = per-answer mixture of endpoint modes), m07 (RL keeps the base's attractor wrong answers),
  m08 (pretraining recall), m09 (Code-RL gain is an ending policy), m10 (cap hits rise then fall over RL steps), m11 (last-marker grading), m12
  (grader v3 false negatives on hard328). m11 and m12 both blame the grader, on different answer sets, so one regrade separates them.
- H2 (half the offline predictions return a number): holds, 29 of 42 (69 %); round 03: 0 of 3.
- H3 (a theory refuted by its own computed predictions): holds, 4 (r4-m02, r4-m04, r4-m07, r4-m09). Two of the four rest on numbers within noise of
  their bounds (section c).
- H4 (a survivor with gain above 0 that its review does not call refuted or published): holds by the rule, 3 (r4-m10 +9.86, r4-m01 +1.41, r4-m08
  +0.12 nats). All three reviews say "weak", all three novelty checks say "partly published", and each review names an untested rival.

## (b) New numbers

Not on the board or in git before the cutoff (checked against `before.jsonl`, `studies/rlneurons/README.md`, `replication.json` step5.b):
- r4-m10: cap hits at T 0.6 / top-p 0.95, plain: step 100 103 of 500, step 400 98 of 500, step 400 on the clean 328 160 (base 137); 78 of 98 step-400
  cap hits are rule-A loops. Readers' centres for the three differences: -0.025/-0.03, -0.06/-0.07, -0.12/-0.12: both expected a fall, the theory a rise.
  For the loop share, readers 0.65/0.60, theory 0.85, measured 0.80. The rise is 8 to 10 times the 0 to 4 of 500 rerun spread; replicated 7 of 7.
- r4-m01: the base's first 3,000 characters compress better than RL step 2,800's on 0.633 of 311 problems (readers 0.54/0.43, did not expect it);
  opening compressibility predicts a later loop, AUROC 0.671 (183 rows, 51 loops; readers 0.60); K continuations 0.558 (readers 0.59/0.57, expected).
- r4-m04: at a = 0.25 the answers take RL's format (share 0.716, readers 0.75/0.75) and RL's boxed accuracy (-0.046, readers -0.07/-0.04) but not
  RL's 'Wait' rate (share 0.327 plain, 0.212 cue; readers 0.38/0.50 and 0.42/0.45, closer than the theory's 0.76 and 0.66).
- r4-m07: 35 of 131 RL wrong answers equal a base wrong answer on the same problem (readers 0.35/0.30); RL's vote fixes 12 of 16 problems where the
  base repeats one wrong value (readers 0.45/0.35) and 18 of 38 where it does not (readers 0.55/0.60).
- r4-m02: within-problem concordance of length with wrongness, finished samples: base 0.622 (405 pairs, 137 problems), RL 0.718 (156 pairs, 50
  problems). Readers expected about the same for both (0.66/0.70 and 0.67/0.68); the theory expected RL far lower (0.55).
- r4-m09: Code-RL fixes 44 of 63 base finished-wrong MATH-500 problems against 35 for the random-delta cell; on hard328 10 of 74 base cap-hit-wrong
  and 27 of 90 base finished-wrong. Readers 0.14/0.10, 0.25/0.25, 0.28/0.32: they were near; the theory was not.
- r4-m08: post-cutoff minus pre-cutoff gap +6.9 points (60 post problems), length-ratio difference +0.14, entropy ratio 0.84; readers bracketed all
  three. Not new: r4-m09 p3 (Code-RL cue cap hits 7 of 500, `studies/rlneurons/README.md` line 584) and p6 (25 of 328, line 727).

## (c) Where the score misled

- r4-m10, +9.86 nats on 4 tests: p1-p3 give 8.89 nats and are one contrast (cap hits early in RL versus the base) measured on overlapping rows (p1
  and p2 share the base file; p2 and p3 share the step-400 checkpoint); p2 and p3 sit at the +3 clip. No test measures entropy or the top-p lock,
  although the rows store mean_logprob. p4 (accuracy on finished answers) was not computed. Step 100/400 texts never start with the cue (0 of 500),
  step 2,800's do (495 of 500), and steps 100/400 ran in a later job: an opening or length change explains the same counts (review: length growth).
- r4-m01, +1.41 on 3 tests: p3 alone gives +1.59; without it the total is -0.18. p3 is a descriptive premise. p4's 90 % interval [0.47, 0.65]
  includes 0.5, and its text[:3000] is mostly the prefix the model was handed (K_own shares a median 6,568 leading characters with base-01's answer),
  so it does not test generated text. Its held-out claims on the neuron ablation missed at -3.00 each (loops 19, claim 66 [48, 84]; cap hits 39,
  claim 94 [76, 112]) but count as no strike, because both readers also put the loops near 55-60.
- r4-m08, +0.12 on 3 tests: p1 gives +0.70; without it -0.58. p1 rests on 60 post-cutoff problems and its interval [-3, 17] spans both signs. p2, the
  test that separates it from its rival, came out +0.143 against a predicted -0.3; it counts as inside only because the bound was 0.15.
- "Survives" is too easy: at least 2 computed, none refuted, total above 0. r4-m08 survives with no test on which the readers disagree with it (0 of
  3 divergent) and its distinctive sign wrong. Of the survivors' 10 computed tests, 5 are divergent (m10 p1, p2, p3, p5; m01 p3).
- Refutations, by reliability of the number. Firm: r4-m04 p1 0.327, bootstrap 90 % [0.25, 0.41] (500 answers per file) against the bound 0.60;
  r4-m07 p1 35/131 = 0.27 (binomial 90 % about [0.21, 0.33]) against 0.36, and p3 12/16 = 0.75 against 0.50. Marginal: r4-m02 p2 0.718, cluster
  bootstrap over problems 90 % [0.64, 0.80] against the bound 0.68 (the centre 0.55 is excluded, and RL's 0.72 is above the base's 0.62, the reverse
  of the theory); r4-m09 p2 9/63 net against 0.12, p4 10/74 = 0.135 (SE 0.04) against 0.19, p5 27/90 = 0.30 (SE 0.05) against 0.26. Each m09 bound is
  within about one standard error, but p4 and p5 are 4.9 and 3.1 standard errors from the theory's centres. r4-m07 p4 (18/38) and p5 (8/42) are
  within noise of their bounds.
- Scripts checked against recipes: `tests/r4-m07/p1.py` and `p3.py` implement them as written (attempt 0, cap hits not answered, the listed
  normalisation, pooled ratio; vote from readout.json). Exact string matching undercounts equal values written differently, which lowers p1, as the
  writer's note says. `tests/r4-m04/p1.py` implements its recipe (first row per problem, all rows, statistics.median = numpy.median).

## (d) The two no-theory readers on the offline tests

Inside their 90 % intervals: reader 1 25 of 29 (86 %), reader 2 24 of 29 (83 %); theories 18 of 29 (62 %), with a median width 0.77 of the readers'.
Centres differ by a median 13 % of the measured value (inflated by quantities near 0), 7 % of the readers' interval width; 6 of 29 centres are equal,
the two sit on the same side of the measured value in 25 of 29, and they disagree in sign once. Round 03: 1.8 %. They are calibrated, not weak: the
theories lose 17.32 nats to them over all 29 tests (-27.18 without r4-m10). They are one reader twice (same model, prompt and input); on the 9 divergent
tests the theories won 5 and lost 4. They missed the rise even though `knowledge-b15a21` was on the board (3.0: 29.1 % vs 17.8 % length-limit hits).

## (e) Predictions not computed (13 of 42)

- Environment, 12, fixed by ae194ae: math_verify missing under plain python3 (r4-m06 p1-p3, r4-m11 p1-p5, r4-m10 p4); sympy's LaTeX parser and numpy
  missing (r4-m12 p1, p2, p4; the writer read test.md as "standard library only").
- Missing rows, 1: r4-m01 p1 needs two samples of one problem; base-01 F_math500 holds sample 0 only (500 rows). `inventory.md` line 31 says "MATH-500
  1 to 4 (column sample)": the inventory was wrong, and this was the theory's own separating test.
- Recipe faults, 0 not computed; in computed tests 3: r4-m01 p4 (handed prefix), r4-m10 p5 (0.10 cut gives 0.87 at 0.12), r4-m07 p1 (strings, not values).

## (f) Changes to the engine, by expected effect

1. Score findings, not predictions: tests of one contrast on overlapping rows count once (mean gain). r4-m10's 8.89 of 9.86 nats is one contrast.
2. Inventory from the files: count rows and samples per problem in each file, and list stored rows no board item has scored, for the developers.
   inventory.md line 31 was wrong (r4-m01 p1 lost); the round's one new finding came from step 100/400 rows marked "not scored".
3. Each test reports n and a bootstrap 90 % interval of its measured value; a refuting bound or "inside" counts only when that interval clears the
   bound, otherwise "within noise". r4-m02 p2, r4-m09 p2/p4/p5, r4-m08 p2 (0.143 against 0.15) and r4-m01 p4 sit within noise of their bounds.
4. Survival needs one divergent test won (both reader centres outside the theory's interval, measured inside). r4-m08 survived with 0 divergent tests.
5. A held-out claim derived from the mechanism that misses its interval is a strike whether or not the readers also missed. r4-m01 missed t14 and t15
   at -3.00 each with 0 strikes; r4-m10 and r4-m08 made no held-out claim on 70 targets.
