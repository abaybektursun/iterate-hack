# Account run 03: readout

**The account r7-account passes its own tests and replicates exactly, but it adds nothing the board did not have. 40 of 46 scored predictions are inside, 6 outside within noise, +8.23 nats; 51 of 51 shares were recomputed equal. At MATH-500 T 1.0 no part of RL's 65-problem gap or Code-RL's 57-problem gap differs from the gap of a second cued-base sample (27 problems); only the size does (net +52 and +40 against -5). Its own claim, that RL multiplies a deliberation mode, missed in both cells that test it (Code-RL deliberation 0.263 against 0.43, reliability 0.474 against 0.29) and lost to a one-axis rival, -5.16 nats on 3 tests. +8.77 of its +8.23 nats come from answer-statement shares.**

## (a) Budget (share of gross gap problems, 90 % bootstrap over gap problems; `metrics_v4.json`, `tests/r7-account/p<k>.out.txt`)

Gap = other side right, cued base wrong; base-only = the reverse; net = gap minus base-only (90 % bootstrap over problems). After each interval: share minus the null's share; * = interval does not overlap the null share's interval. Unassigned is 0 in every cell. Evidence for kB: plain base T 0.6 (`r3/base-01 P_*`) and plain base T 1.0 (`T3.jsonl`, job 7ba0), grader v3.

| Cell (predictions) | Gap / base-only / net [90 %] | Loop | Budget | Answer statement | Reliability | Deliberation |
|---|---|---|---|---|---|---|
| null: 2nd cued-base sample, MATH-500 T 1.0 (p1-p7) | 27 / 32 / -5 [-18, 8] | .000 [.000, .000] | .111 [.037, .222] | .037 [.000, .111] | .481 [.333, .630] | .370 [.222, .519] |
| fit: RL plain, MATH-500 T 1.0 (p8-p14) | 65 / 13 / +52 [39, 66] | .000 [.000, .000] +.000 | .246 [.169, .338] +.135 | .031 [.000, .062] -.006 | .431 [.338, .538] -.051 | .292 [.200, .385] -.078 |
| fit: RL plain, hard328 T 1.0 (p15-p21) | 52 / 7 / +45 [33, 57] | .000 [.000, .000] +.000 | .365 [.269, .481] +.254 * | .019 [.000, .058] -.018 | .212 [.115, .308] -.270 * | .404 [.288, .519] +.033 |
| fit: RL step 2,800 plain, MATH-500 T 0.6 (p22-p28) | 112 / 9 / +103 [86, 119] | .598 [.518, .679] +.598 * | .179 [.116, .241] +.067 | .009 [.000, .027] -.028 | .152 [.098, .205] -.330 * | .062 [.027, .098] -.308 * |
| Code-RL cue, MATH-500 T 1.0 (p29-p35) | 57 / 17 / +40 [26, 54] | .000 [.000, .000] +.000 | .228 [.140, .333] +.117 | .035 [.000, .070] -.002 | .474 [.368, .579] -.008 | .263 [.175, .368] -.107 |
| theta0.5 cue, hard328 T 1.0 (p36-p42) | 40 / 13 / +27 [15, 39] | .000 [.000, .000] +.000 | .375 [.250, .500] +.264 * | .025 [.000, .075] -.012 | .250 [.125, .375] -.231 | .350 [.225, .475] -.020 |
| step 400 plain, MATH-500 T 0.6 (p43-p49) | 55 / 29 / +26 [10, 41] | .527 [.418, .636] +.527 * | .145 [.073, .218] +.034 | .018 [.000, .055] -.019 | .218 [.127, .309] -.263 * | .091 [.036, .164] -.279 * |
| step 100 plain, MATH-500 T 0.6 (p50-p56) | 61 / 33 / +28 [12, 44] | .590 [.492, .689] +.590 * | .115 [.049, .180] +.004 | .016 [.000, .049] -.021 | .197 [.115, .279] -.285 * | .082 [.033, .148] -.288 * |
| 3.0 first release plain, MATH-500 T 0.6 (p57-p63) | 76 / 58 / +18 [-2, 37] | .605 [.500, .697] +.605 * | .145 [.079, .211] +.034 | .013 [.000, .039] -.024 | .171 [.105, .250] -.310 * | .066 [.026, .118] -.305 * |

- Exceed the null, 15 differences: loop in all 4 T 0.6 cells (0.53 to 0.61 against 0), with reliability and deliberation below it there (0.06 to 0.22 against 0.48 and 0.37); budget on hard328 for RL and theta0.5 (0.365, 0.375 against 0.111); RL reliability on hard328 (0.212). Each of the 15 compares a T 0.6 or hard328 cell with a MATH-500 T 1.0 null, so temperature or problem set changes as well as the model.
- Do not exceed the null: all 10 parts of the two matched cells (RL and Code-RL, MATH-500 T 1.0); theta0.5 hard328 reliability and deliberation. Within T 0.6, step 100 (net +28) and step 2,800 (net +103) have the same composition in every part. With 27 null gap problems a share must differ from the null by about 0.2 to 0.25 before the intervals separate.

## (b) What the account predicted that both readers missed

One win the readers did not expect: p3, null answer statement 0.037 (predicted 0.04, readers 0.11 and 0.15, +1.69). Gains above 1 nat: p3, p31, p38, p45, p52, p59 (answer statement in 6 cells: measured 0.013 to 0.037, predicted 0.02 to 0.04, readers 0.06 to 0.15; +8.77 nats together), p36 (hard328 T 1.0 loop 0, +1.40) and p56 (step-100 net 28; same centre as the readers, wider interval, +1.21). Common to all 8: none is about reliability or deliberation. The answer-statement wins are the account's own text rule under grader v3, fitted on its claimed cells (0.031, 0.019, 0.009); the readers centred between run 01's hand-label 0.154 and run 02's 0.027 to 0.061 (`facts.json`). The hard328 T 1.0 loop share is 0 by the account's own statement ("cannot fire at T 1.0") but was not declared 0 by construction. The mechanism's parts lost: reliability shares -2.42 nats (p32 -1.82), deliberation shares -1.68 (p33 -2.06).

## (c) Replication (`replication/r7-account.json`, `replication/r7-account.duel.json`)

A separate agent wrote new scripts from the recipes alone (`replication/r7-account/`, shared module `acct_lib.py`). 51 of 51 shares and fits equal the first computation exactly; bootstrap intervals differ by one gap problem at one end in 5 (p16, p39, p44, p50, p57), which moves no * mark. Duel tests with a gain of 1 nat or more: 2 of 2 equal. Not recomputed by rule: the 9 net counts, the 3 cross fractions, duel p3 (-0.63).

## (d) The rival (`rivals/r7-account.json`, `metrics_v5.json`)

Rival budget: the same five parts and rules, but kB and the base cap hit only sort gap problems into difficulty and length strata on one shared per-problem difficulty axis (result-5da8a9). Any stronger arm's MATH-500 T 1.0 gap then has the null's composition (reliability about 0.45, deliberation about 0.28); on hard328 the strata shift toward cap hits and kB = 0 with no mode change. The rival wrote its tests after reading the account's computed shares; the defender predicted from the theory alone.

| Test (MATH-500, T 1.0, cue on the other side) | n | Measured [90 %] | Account (defender) | Rival | Gain |
|---|---|---|---|---|---|
| theta0.5 gap, reliability share (p1, replicated) | 52 | 0.481 [0.365, 0.596] | 0.31 [0.20, 0.43] | 0.45 [0.33, 0.57] | -2.85 |
| theta0.5 gap, deliberation share (p2, replicated) | 52 | 0.269 [0.173, 0.385] | 0.40 [0.28, 0.52] | 0.28 [0.17, 0.39] | -1.68 |
| Think-SFT gap, reliability share (p3) | 65 | 0.385 [0.292, 0.477] | 0.29 [0.18, 0.41] | 0.43 [0.30, 0.56] | -0.63 |

`rivals/r7-account/p1.py` implements the recipe as written (B from per_problem t1, O first row per problem, E = P_math500 sample 0 + T3 regraded v3 with cap hits wrong, rule A, N(), rules in order); p2 and p3 differ from p1 only in the target part and the O file. "The script implementing the recipe as written" is the review's required check that a duel script computes the rival's recipe; the -5.16 holds only if it does. Other fair readings of the recipe, rerun on the same rows (`runs/theory-tests/duel-r7-account/`, not committed): R3 by grader-v3 equivalence instead of the literal box string moves 1 problem per cell (reliability 0.462 and 0.369; total -4.20); kB without forcing cap hits wrong gives the same values; counting theta0.5's one v3-right cap hit (problem 138) adds one gap problem. None changes the state. A different reading of the theory does: had the defender given each test the account's predicted null shares (0.36 [0.22, 0.50], 0.37 [0.23, 0.51]), as its sentence "the composition of RL-side gaps stays close to the null" allows, the total is -1.95 nats, not separated. That reading drops deliberation above the null, the account's only difference from the rival.

## (e) Hypotheses of `specs/SPEC_account03.md`

- C1 holds, against the spec's expectation: 53 of 53 recomputed numbers equal (51 shares, 2 duel tests).
- C2 holds by the letter (15 differences apart), as expected: loop at T 0.6, nothing on MATH-500 T 1.0. None is against a matched null.
- C3 holds: survives, 40 / 6 / 0, +8.23 nats; the two predictions that carry the mechanism (p32, p33) are outside within noise, -3.88 nats.
- C4 holds: net inside in 5 of 5 predicted cells (Code-RL 40 in [35, 44], theta0.5 27 in [21, 30], step 400 26 in [5, 45], step 100 28 in [-12, 32], 3.0 18 in [-5, 55]); the readers had the same centres on all 9 nets; the last two intervals are 44 and 60 problems wide.

## (f) Is anything new for the board after account runs 01 to 03?

1. At MATH-500 T 1.0 the gaps of RL and Code-RL have a second cued-base sample's composition in every part; only the net differs (+52, +40, -5). On the board before: result-f39ba8 (null base + random direction), result-5da8a9, result-afc423; partly published (Yue et al. 2504.13837).
2. Plain-base-unsolved ("deliberation") problems are not new capability: 14 of 15 in the Code-RL cell have a right answer among the 4 cued-base samples of day1_3 (p65, 0.93 [0.80, 1.00]). On the board before: result-afc423 (81 % of RL's gap on problems the base solves once in 4).
3. At T 0.6 loops are 0.53 to 0.61 of the gap at steps 100, 400, 2,800 and the 3.0 release while the net grows from +18 to +103; 25 of 29 step-400 loop problems are solved by the cued base's T 1.0 sample (p64). Before: result-f39ba8 (step 400, 0.44 under v1), knowledge-13cff3 (T 1.0 resampling of cap hits); top-p lock published (2610.24715). New: only the equality across checkpoints, with no T 0.6 base-against-base null.

## (g) Faults of the stage seen in this run

1. One null for nine cells: MATH-500 T 1.0, 27 gap problems. All 15 differences that clear it are T 0.6 or hard328 cells, where temperature or problem set also differs; the stage did not ask for a null per sampling setting and problem set.
2. The score does not measure the mechanism: answer-statement shares +8.77 nats, undeclared zeros +1.95 (p36 +1.40, six unassigned +0.55), reliability and deliberation shares -4.09. Outside within noise counts as a pass, so the account survives while p32 and p33 miss (both scripts print refuted_by_met true).
3. Leaks: each net experiment string carries the account's gross counts, so the readers had the same centre on 9 of 9 nets. Held-out t58 (step 100, 103 cap hits) and t60 (478 'Okay' openings) are in `graveyard.json` and `facts.json`, both account inputs; they give +6.0 held-out nats.
4. Cost, about 69 minutes (before.jsonl 23:45, review 00:54): account writer 1,051 s plus a 454 s fix after a format send-back (offline predictions without gpu_minutes 0, no GPU prediction, p67 without a cell); test writer 1,043 s for 66 scripts, 54 of them shares that are 9 partitions of one rule set (one script per cell would do); 20 of 66 not scored; the review needed one send-back to name the duel state.
