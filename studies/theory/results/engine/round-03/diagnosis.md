# Round 03 diagnosis

Sources: `metrics_v3.json` (`theories.<name>.rows`), `targets.jsonl`, `predictions/null-{1,2}.jsonl`, `theories/*.json` (`statement`, `imports`,
`predictions[].recipe`), `tests/`, `reviews/r3-across-2.json`, `external*.md`. 80 scored claims from 14 theories on 51 targets; summed gain -25.55 nats.

## 1. Why theories lose to the no-theory readers

Wrong centres, not wrong widths. Split by whether the claim's centre is farther from the measured value than the midpoint of the two null centres:

| cause | claims | summed gain (nats) | gain > 0 | gain <= 0 |
|---|---|---|---|---|
| (a) centre farther than the nulls' midpoint | 37 | -50.25 | 7, +1.21 | 30, -51.46 |
| (b) centre as close or closer | 43 | +24.70 | 40, +25.56 | 3, -0.86 |

In (a), 17 claims missed with an interval narrower than the nulls': -43.82 nats. In (b), 40 of 43 gain: a right centre with a narrower interval
is rewarded. Against each null separately: farther than both 30 claims (-46.41), closer than both 38 (+23.54), between 12 (-2.68).
11 claims sit at the -3.00 clip, none at +3.00. Divergent claims (both null centres outside the claim's interval): 21, of which 6 gain, -21.17 nats; the other 59: -4.38.
Calibration on the 51 targets: null-1's 90 % interval holds the measured value 42 times (82 %), null-2's 43 (84 %); the advocates' 60 of 80 (75 %).
Advocate width / mean null width: median 0.62, narrower in 78 of 80 claims. The two nulls are nearly one reader: centres differ by a median 1.8 % of the measured value.
Subsets. By type: accuracy cells 75 claims, -27.88; token counts 4 claims, +1.67; interpretability readouts 1 claim, +0.67. By item: result-edceef
(RL-Zero variants) 21 claims, -16.56; result-e45bf4 (hard328 deltas) 29, -4.70; result-ad3c24 10, -2.12; result-d2933e 11, -1.33; result-96e819 1, -1.63;
result-cbe0bc 6, +0.03; result-e78dfe 1, +0.10; result-c4411d 1, +0.67. No subset with more than 6 claims has a positive total.

Largest gains (measured; claim [interval]; null centres): +2.40 r1-surprises-2 t44 (base + top-8 directions, all 500, plain: 427; 412 [370, 445]; 300, 330);
+1.84 r3-external-2 t34 (RL-Zero-Math 3.0, cue: 448; 447 [435, 459]; 405, 430); +1.81 r1-surprises-2 t01 (top-8, first 100: 88; 82 [70, 92]; 62, 68);
+1.73 r3-surprises-2 t34 (448 [434, 461]); +1.17 r1-all-2 t34 (443 [418, 462]).
Largest losses, all -3.00 (clipped), 11 claims: r1-all-2 t39 (RL-Zero-Mix plain: 372; 438 [405, 462]; 415, 415); r1-surprises-2 t03 (RL minus top-8
directions: 91; 55 [42, 70]; 88, 86); r1-surprises-2 t48 (base + bulk64: 86; 50 [37, 63]; 80, 80); r1-surprises-2 t47 (top-1 direction: 42; 70 [55, 85]; 50, 55);
r2-across-2 t01 (top-8: 88; 58 [44, 72]; 62, 68); the other 6: r2-across-2 t44 (427; 305) and r3-external-2 t38, r3-revise-1 t37/t38, r3-surprises-2 t37/t38
(RL-Zero-IF cue 377, RL-Zero-Code 3.0 cue 411; claims 436-446; nulls 415-425).
The clipped losses are the theories' own distinctive predictions, and they are wrong:
- r1-surprises-2 ("high-rank remainder is optimizer noise") and r2-across-2 ("function is in the sign pattern, not the large entries") both fail on WSP-1:
  top-8 directions per matrix are sufficient (88/100, 427/500) and not necessary (RL minus them 91/100; bulk64 86/100).
- Family A below ("a shared low-dose part that any RL-Zero delta carries") fails on result-edceef (IF 377, Code 3.0 411 with the cue; claims about 440),
  and 4 of its theories put Code-RL 3.1 on hard328 at 171-177 (t28): measured 187, 0.9 points below theta(0.5) (t33).

## 2. How many targets a theory speaks about

Claims per theory (of 51): r1-all-2 12, r3-external-2 11, r3-revise-1 11, r3-surprises-2 11, r1-surprises-2 8, r2-across-2 7, r3-across-1 6, r3-all-1 4,
r3-surprises-1 4, r3-all-2 3, r3-external-1 2, r3-across-2 1, r2-all-2 0, r3-revise-2 0. 22 of 51 targets drew no claim. Items with no claim:
result-abb853 (J-lens workspace, 3 targets), result-a2dc6f (matched lenses, 2). The 9 readout targets drew 1 claim; result-96e819 (self-review, 5) drew 1.
71 of 80 claims fall on 4 items: WSP-1 (d2933e, ad3c24), RL-Zero variants (edceef), hard328 deltas (e45bf4). The held-out set holds no temperature,
sampler or loop target, while 6 theories (family B and r2-all-2) are about exactly that; they made 10 claims (-2.36 nats), all outside their mechanism.

## 3. Why the offline tests returned no number

Only r3-across-2 was tested (the only candidate). All 3 recipes need S3 files. Each script ran `aws s3 cp` with the default profile and got 403 on
HeadObject (`tests/r3-across-2/p{3,4,5}.out.txt`); the test job's out.txt says "I did not try the other AWS profiles". The cause is credentials,
not a missing file, a missing field or a wrong script. Checked now:
`aws s3 ls s3://pg-lineage-769063704696/results/rlneurons/ --profile iterate-ecr` works (c_code/ h1/ inputs/ r3/ r4/ r5/ ...; T1, T2, T3, F_math500, F_hard,
s2800-01 P_hard all list). Without a profile (a user in another AWS account): AccessDenied on ListObjectsV2. `results/next_n13/...` is 403 even with the profile.
So p3 (T1, F_math500) and p5 (T1 plus two Modal cells, which download) were computable; p4 (n13) was not.

All 29 recipes of the 10 new theories (the carried theories have none): 27 readable on this machine now. 8 use only committed files (`per_problem.json`,
`rln5/map-01/checks.json`, `rln3_overlap.json`; the named fields exist); 14 also need answers files on abaybektursun's Modal volume `iterate-runs`
(all 7 job folders list); 5 need S3 with `--profile iterate-ecr`; 2 cannot be read: r3-across-2 p4 (n13) and r3-surprises-1 p5 (shards in sameraslan's
Modal workspace). Row files missing from git that most recipes need: theta0.25_cue b029 (6 recipes), code_cue 0203 (5), random_cue 6429 (5), rl_cue e985 (4),
base cue T 0.6 d4fa (3). A committed per-problem table (problem_index, score_v3, cap_hit, n_generated) of these 5 cells plus theta0.75_cue af79 makes
22 of 29 recipes computable from git alone.

## 4. Quality of the new theories

The 10 new theories are 2 mechanisms, and each of the 5 generators wrote exactly one of each:
- A, two-part delta (across-1, all-1, external-2, revise-1, surprises-2): a shared, domain-general low-dose part (saturated at a = 0.25, Code-RL has it) plus
  a math-specific part that grows with dose and pays on long or hard problems. It restates round 01's r1-surprises-1 and the external.md paragraphs of
  2506.14965 and 2505.19439, which already state its prediction (Code-RL short of Math-RL on hard328). Its predictions failed (section 1).
- B, sampler tail (across-2, all-2, external-1, revise-2, surprises-1): the cued base needs untruncated T 1.0 tail mass to leave loops or slips; sharpening
  removes it; RL is insensitive. It restates carried r2-all-2; across-2's first half is the 2610.24715 paragraph ("Truncation deletes the escape mass").
revise-1 and revise-2 restate their parents (r1-all-2, r2-all-2) by design. By this reading all 10 restate a carried or earlier theory or an external.md paragraph.
Imports: 22, from 17 distinct papers; the most used appears in 2 of 10 theories (round 02: 26 imports, 12 distinct, 2610.37719 in 5 of 10). Every generator
imported only from its own split. The split spread the citations, not the mechanisms: every split starts with the same 10 "unexplained results", and each split
held a paper for each family.

## 5. Hypotheses

- H1 (a candidate beats its reversal): not refuted by the rule, on one claim. r3-across-2 +0.67 vs reversal +0.29; its interval [0.67, 0.67] is one claim resampled.
- H2 (a carried theory totals above 0): not refuted by the rule. r1-all-2 +2.62 nats, 12 claims, interval [-3.81, 7.98] (fails); r2-all-2 0 claims; r2-across-2 -3.20; r1-surprises-2 -4.60.
- H3 (half of tested offline predictions return a number): refuted, 0 of 3 (S3 403 with the default profile).
- H4 (a theory stands after tests and review): refuted. r3-across-2's review says weak. The engine still produced no theory worth a GPU run.

## 6. Judgement

1. Run the offline tests for every theory, not only candidates, with `AWS_PROFILE=iterate-ecr` and a committed per-problem table of the 6 Modal cells:
   27 of 29 recipes are readable today, the theory chose them, and they are fixed before they are computed. Round 03 computed none.
2. Let a divergent claim that lands outside its interval refute the theory, as an offline test does, and let no theory with fewer than about 5 claims be a
   candidate. The score already finds the failures (21 divergent claims, 15 lose, 11 at the clip) but sums them into a total that one claim can carry.
Stop: giving generators external.md's per-paper "Bears on ... Prediction" text and the shared list of 10 unexplained results. Those paragraphs are the theories.
The quoted reading is half supported. Where theories agree with the nulls they add nothing (59 claims, -4.38 nats). Where they diverge they add information,
and it was wrong (15 of 21 lose): the held-out score works as a refutation filter, not as confirmation. The second half holds: the targets were incidental
(22 of 51 unclaimed; no temperature target for 6 sampler theories) and no theory-chosen test was computed.
