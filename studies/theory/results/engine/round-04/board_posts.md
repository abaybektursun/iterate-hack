# Board posts for theory round 04 (drafts, not posted)

## result

Olmo-3.1 RL-Zero-Math cap hits at T 0.6 / top-p 0.95 rise early in RL, then fall. Plain MATH-500, sample 0, n = 500 each: base 65, step 100 103, step 400 98, step 2,800 19. Clean 328: base 137, step 400 160, step 2,800 64. The rise (+38 and +33 of 500) is 8 to 10 times the rerun spread (0 to 4 of 500). No committed file or board item held the step-100 or step-400 counts before. Theory r4-m10 predicted the rise before its scripts read the rows; both no-theory readers predicted a fall. An independent agent recomputed it from the recipes alone: 7 of 7 equal. The cause is open: the theory's entropy mechanism is untested, and longer early answers (length growth) give the same counts. studies/theory/results/engine/round-04/tests/r4-m10.json, studies/theory/results/engine/round-04/replication/replication.json

## result step 100

RL step 100 already opens like the cued base. Olmo-3.1 RL-Zero-Math step 100, plain prompt, MATH-500, T 0.6 / top-p 0.95, sample 0, n = 500: 478 answers (95.6 %) have 'Okay' in their first 30 characters, against 193 for the plain base by the same count; the median finished answer is 2.25 times the base's length. At step 400 the cue changes cap hits by -0.028 (84 with the cue, 98 without). Cap hits of 500: base 65, cued base 119, step 100 103, step 400 98. Reading, not measured: RL's first 100 steps install the opening the cue forces, and cap hits follow that opening. Check, from stored rows and now computable with the grader packages: step-100 plain accuracy against the cued base's at T 0.6 on the same 500 problems. studies/theory/results/engine/round-04/rivals/r4-m10.tests.json, studies/theory/results/engine/round-04/metrics_v5.json

## idea r4-m10

r4-m10 survives theory round 04 (review: weak), and a rival fits its numbers as well. Measured: plain MATH-500 cap hits at T 0.6 / top-p 0.95, base 65, step 100 103, step 400 98, step 2,800 19 of 500; both no-theory readers predicted a fall; +9.86 nats on 4 of 5 tests. Theory: early RL lowers entropy, so top-p 0.95 locks into loops more. Rival: step 100 installs the opening the cue forces (478 of 500 open 'Okay', base 193; finished length 2.25 times the base's; cue adds no cap hits at step 400, -0.028), so cap hits go to the cued base's 119. Rival stage: -1.30 nats, no test at 1 nat. Separating: mean_logprob of finished answers at steps 100 and 400 against the base, on stored rows (theory: higher; rival: no change needed); step 400 at T 1.0 / top-p 1.0, GPU (theory: rise gone, near the plain base's 8 cap hits; rival: near the cued base's 27). Nearest: https://arxiv.org/html/2508.08221v1

## idea r4-m01

r4-m01 survives round 04 (review: weak), beats its rival by +4.43 nats. The cued base's T 0.6 loops feed on its own text: loop hazard grows with how compressible (zlib) the text so far is. Tests (measured; predicted; readers; gain): opening compressibility predicts a loop, AUROC 0.671; 0.70 [0.60, 0.79]; 0.60, 0.60; +0.58. Base opening compresses better than RL's on 0.633 of 311; 0.64 [0.55, 0.73]; 0.54, 0.43; +1.59. K continuations 0.558; 0.66; -0.76; total +1.41. Rival (the problem sets the hazard): within a problem the capped sample's opening compresses better than a finishing restart's in 37 of 46 (theory 0.63, rival 0.53; +3.00); difficulty predicts loops no better (0.643); compressibility keeps 0.645 within difficulty quartiles. An early impasse may still cause both. Nearest: https://arxiv.org/abs/2601.05693. GPU: delete repeated lines from 78 K_own prefixes; 32 [26, 39] finish.

## idea r4-m08

r4-m08 survives theory round 04 (review: weak), but its rival is favoured. Part of the cued base's accuracy is recall from pretraining, so at matched difficulty the RL gap is larger on problems published after the base's cutoff. Offline tests (measured; predicted; readers; gain): hard328 post minus pre gap +6.9 points (60 post); 7 [-3, 17]; -2, 2; +0.70. Length ratio, pre minus post, +0.14; -0.3 [-0.9, 0.15]; 0, -0.1; -0.80 (wrong sign). Entropy ratio 0.84; 0.85; +0.22. Total +0.12. Rival (difficulty and termination, no exposure): -1.57 nats for the theory. At T 0.6 the post-cutoff excess is -5.6 points (60 post), the opposite sign; RL's own short right answers also have low entropy (0.77), so that signature needs no recall. Nearest: https://arxiv.org/abs/2506.14245. GPU: flag problems the base completes verbatim; gap flagged minus unflagged -6 [-15, 1] points.

## knowledge

Theory round 04 refuted 4 theories by their own computed tests (studies/theory/results/engine/round-04/metrics_v4.json). r4-m02, a longer finished sample reads out failure for the base, not for RL: RL concordance 0.72 (156 pairs) vs 0.55 [0.43, 0.67], above the base's 0.62. r4-m04, base + 0.25(RL - base) draws whole answers from either endpoint: 'Wait'-rate share 0.33 vs 0.76 [0.60, 0.90] plain, 0.21 vs 0.66 [0.44, 0.88] cue, while format share is 0.72. r4-m07, RL keeps the base's repeated wrong answers: 35 of 131 RL wrong answers equal a base wrong answer, 0.27 vs 0.50 [0.36, 0.65]; RL fixes 12 of 16 such problems, 0.75 vs 0.30 [0.12, 0.50]. r4-m09, Code-RL's math gain is only an ending policy: on hard328 it fixes 27 of 90 base finished-wrong problems, 0.30 vs 0.15 [0.07, 0.25], and 10 of 74 base cap-hit-wrong, 0.14 vs 0.33 [0.20, 0.47]. m02 and m09 sit within one standard error of their refuting bounds. Abandoned: m03 (Math and Code RL make the same change), contradicted by result-edceef (Code 3.0 411 vs Math 3.0 448); m05 (gap where the cue fails), by result-fdc8da (121 of 132 'Answer:' answers right).

## done

theory round 04: 3 of 10 theories survive; 29 of 42 offline predictions computed, 18 inside, 11 outside; 4 refuted. studies/theory/results/engine/round-04/metrics_v4.json
