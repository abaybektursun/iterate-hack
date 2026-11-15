# Round 04, rival stages (version 5)

r4-m01 beats its rival by +4.43 nats, almost all from one test (within a problem, the capped sample's opening compresses better in 37 of 46).
r4-m10 (-1.30) and r4-m08 (-1.57) "lose", but none of their tests reaches 1 nat, and on all 9 tests the defender's centre lies inside the rival's
interval. Spec ea73cfc, code 1f1ea4e, 9 jobs, 05:44:53Z to 05:51:53Z (`round04duel.log`); numbers from `metrics_v5.json` and `rivals/`.

## Hypotheses

- D1 (2 of 3 survivors get 2 or more computed tests): holds, 3 of 3, each 3 of 3 computed.
- D2 (half the tests have a gain of 1 nat or more in size): refuted, 1 of 9 (r4-m01 p1, +3.00); the other 8 lie between -0.95 and +0.74.
- D3 (defender on the side of the rival's value that `theory_should_say` names): holds by the letter, 9 of 9. But the defender moved from that
  reading toward the rival: r4-m10 82, 79, 76 % of the way; r4-m08 50, 17, 56 %; r4-m01 5, 41, -12 %. On r4-m10 the tests measure width.
- D4 (r4-m10 and r4-m08 lose, r4-m01 within 1 nat of 0): refuted; r4-m10 and r4-m08 lose as predicted, r4-m01 wins by +4.43.

## r4-m10 against "early RL installs the cue's opening" (n = 500 problems per file)

Rival: by step 100 RL has taught the plain base the opening the cue forces, so cap hits go to about the cued base's 119 of 500, no entropy change.
Each test: measured; theory [90 %]; rival [90 %]; `theory_should_say`; gain.
- p1, step-100 plain answers with 'Okay' in the first 30 characters: 0.956 (478); 0.65 [0.38, 0.92]; 0.72 [0.48, 0.93]; about 0.34; -0.43. The 0.34
  is knowledge-0b450e's 168; this recipe gives the base 193 of 500 (computed here from base-01 P_math500), step 400 417, step 2,800 495.
- p2, step-400 cap-hit rate, cue minus plain: -0.028 (84 against 98); 0.025 [-0.03, 0.085]; 0.01 [-0.04, 0.06]; +0.05 to +0.11; -0.51.
- p3, median finished length, step 100 over base: 2.25; 1.8 [1.0, 3.0]; 2.0 [1.3, 2.9]; 1.0 to 1.3; -0.37.
Reading: all three values lie at or beyond the rival's centre and far from the rival's reading of the theory. Against the theory as its developer
wrote it (lower entropy makes top-p 0.95 lock into loops) they fit the rival better: step 100 switched its opening (193 to 478 of 500), more than
doubled finished length, and the cue adds no cap hits at step 400; steps 100 and 400 have 87 % and 82 % of the cued base's cap hits. They do not
refute the theory: "concentrates on the base's own paths" can absorb the switch, since '.\n\nOkay' is one of the base's own openings, and the defender
read it that way. No test measured entropy, so the theory's distinctive step is still untested.
Script check, `rivals/r4-m10/p1.py`: implements the recipe (sample 0, first row per problem, 'Okay' inside text[:30], 500 rows kept).

## r4-m01 against "the loop hazard is a property of the problem"

Rival: a stuck model locks into a repeat at a steady rate per token, so hard problems collect the loops; compressibility works only across problems.
- p1, within a problem, capped base-01 F sample's text[:3000] compresses better than a finished K_fresh restart's: 0.804 (37 of 46); 0.63 [0.51,
  0.75]; 0.53 [0.41, 0.65]; 0.62-0.65; +3.00 (clip).
- p2, RL step-2,800 answer length as loop predictor, AUROC (183 rows, 51 loops): 0.643; 0.67 [0.58, 0.76]; 0.72 [0.61, 0.83]; 0.6-0.67; +0.74.
- p3, compressibility AUROC within quartiles of RL length: 0.645 (quartiles 0.74, 0.52, 0.59, 0.73; 7 to 19 loops each); 0.66 [0.56, 0.76]; 0.57
  [0.46, 0.68]; 0.65; +0.69.
Reading: p1 refutes a hazard fixed by the problem: the sample that loops was more repetitive early than a sibling that finished. Difficulty predicts
no better than compressibility (0.643 against 0.671, same rows) and does not remove its signal (0.645). Cause is open: an early impasse in one
sample may make its text repetitive, the review's sample-level rival, which this rival was not.
Script check, `rivals/r4-m01/p1.py`: implements the recipe. 46 kept of 119 K_fresh rows (69 restarts also capped, 4 too short). Both openings are
3,000 characters and start with the 3-token cue (46 of 46); K_fresh restarts from the opening (n_prefix 3), so neither holds a handed prefix. In 6 of
46 capped samples rule A (my recomputation) puts the loop onset before character 3,000; dropping samples with onset before 6,000 gives 25 of 32 (0.78).

## r4-m08 against "difficulty and termination only"

Rival: no exposure effect; the +6.9-point excess is noise on 60 problems; short low-entropy right answers are generic.
- p1, post-minus-pre gap at T 0.6, stored v1 score, clean 328 (60 post, 268 pre): -5.6 points; 4.0 [-9, 17]; 1.0 [-10, 12]; about +7; -0.42.
- p2, base/RL log length ratio, pre minus post, both right (103 pre, 7 post): -0.19; -0.25 [-1.0, 0.5]; 0.0 [-0.5, 0.5]; about -0.3; -0.21.
- p3, RL's own short/long right-answer entropy ratio (148 short, 314 long): 0.77; 0.9 [0.75, 1.05]; 0.82 [0.68, 0.96]; near 1.0; -0.95.
Reading: the excess changes sign (+6.9 at T 1.0 v3, -5.6 at T 0.6 v1), as noise on 60 problems would; RL's short right answers have low entropy
too (0.77; base 0.84), so that signature needs no recall. p2 has the theory's sign on 7 post problems.

## What the stage got wrong

1. Small totals get state names: -1.30 and -1.57 print "loses to rival" with no test at 1 nat (fix decided for 5.1).
2. The defender got `before.jsonl` and `inventory.md` (`defend` in round.py at 1f1ea4e); the spec says theory and recipes only. On r4-m10 it used
   board numbers (168 of 500; the cue's 65 to 119) and wrote the rival's opening switch into its reading, so its centres fell in the rival's intervals.
3. The rival's tests confirm its own mechanism: no r4-m10 test reads mean_logprob or T 1.0 cap hits, the two measurements the review named.
4. `theory_should_say` numbers are asserted, not computed (0.34 is 0.386 under the rival's recipe). r4-m08 p1 changes T, samples and grader at once.
