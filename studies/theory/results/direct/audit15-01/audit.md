# Audit 15: four round-15 numbers recomputed from stored rows

Script `studies/theory/analysis/audit15.py` (written before reading the tests' scripts; raw texts in `runs/` for seed
checks), output `metrics.json` here; 10,000 bootstrap resamples of problems, default_rng(15); times UTC.

**Verdict.** All four numbers reproduce. The ranges were frozen in the gate commit 4881d61 (23:15:27), before any test
spec (23:17:43 to 23:19:33) or output (23:19:07 to 23:23:29); the final commit 644e0b8 changed only verdict lines. No
board result showed any of the four values before its test round. Faults: the s100vote null is not the strongest null
(an accuracy-matched null lands inside the account's range); merge328's null is the weakest possible one; edit0of4
and d1 are two functions of the same counts, so account-2 is credited twice for one measurement.

## 1. merge328: real minus merged wrong answers, hard328 vote of 4 (posted 0.109 [0.078, 0.142], n 88)
(a) 0.1089 [0.0777, 0.1420], n 88, with my string normaliser and with math-verify 0.9.0 alike: matches. D > 0 on 25
problems, 0 on 63, never < 0. (b) Frozen first. The MATH-500 analogue was posted before (result-dd9b25, 0.070); the
hard328 value was not. New, but an extension of a known effect that the account quotes. (c) The null "all wrong
answers of a problem are one value" gives D = 0 by construction; any two differing wrong answers make D > 0, so
excluding it shows only that wrong answers are not all identical. The quantity behind the claim (slips are one-off,
not shared values) is wrong-pair agreement: 0.218 of 257 same-problem wrong pairs agree on hard328, far above chance
(about 0.005). Shared wrong values exist; D above 0.06 does not rule them out. (d) No selection beyond the kept rule.
(e) Changes: problem 66, answers 673, 16011, 721, 721, gold 721: real vote 1, merged 0.5. No change: problem 0,
answers 108, 116, 116, 116, gold 116. (f) Letting cap hits with an answer vote gives 0.122. Grader v3; robust.

## 2. s100vote: step-100 vote-over-4 gain, MATH-500 (posted +7.18 [6.03, 8.37], n 500)
(a) +7.28 [6.13, 8.45]: matches within 0.1 point (I pool all right samples as one key; the test groups right answers
by text, 0.52 votes fewer). Cued base +7.55 and final RL +2.87 reproduce. (b) Frozen first; no step-100 vote posted
before result-53addf. New. (c) **Fault.** The null "final RL's gain, +2.87" ignores that the vote's gain is capped by
accuracy: final RL solves 425 of 500 problems 4 of 4, step 100 only 336. Final RL's own mean gain at each right count
k (0-4), applied to step 100's k distribution, gives **+6.24**, inside the account range [5, 10]; step 100's excess
over it is +1.05 [0.00, 2.15]. The test cannot tell "step 100 kept the base's slips" from "step 100 has final RL's
slip structure at lower accuracy". Wrong-pair agreement points against the account: step 100 0.298 (114 pairs), final
RL 0.283 (106), cued base 0.201 (154). (d) Same 4 samples, cap 16,384, T 1.0 in all three cells (step-100 sample 0
from vast, samples 1-3 from Modal, same settings). 1.85 points come from problems with no finished wrong answer, where
108 answerless rows (final RL 7) cast no vote. (e) Vote right: problem 5, answers (none), 42, 42, "42 inches", all
right. Vote wrong: problem 18, answers 56, 56, 28, 56, gold 28: a shared wrong value. (f) Grader v3; abstention moves G.

## 3. edit0of4: edit minus RL, base-0-of-4 hard328 (posted -0.012 [-0.037, 0.010], n 121; null -0.097)
(a) -0.0124 [-0.0351, 0.0124], n 121 (edit 69/484, RL 75/484); null D0 -0.0967 [-0.1358, -0.0594], n 120: matches.
(b) Frozen first. But result-fe30d5 (editreach-01, 23:19:14) had already printed edit minus RL -0.020 on 102 of these
problems, 19 s before the edit0of4 spec commit (23:19:33), and that agent read editreach-01 (it found its id bug). c3
is d1's secondary line on the same rows: not an independent consequence. (c) The planned null range [-0.35, -0.12] was
wrong; the measured null's interval overlaps the account range [-0.08, 0.08]. The test still separates: D - D0 = edit
minus a fresh base sample = +0.084 [0.051, 0.119]. (d) Selection on the base's 0-of-4 does not bias E - R: both are
fresh draws of other models. They share the base's seeds, so I checked coupling: same-seed score agreement with the
base 0.816 (edit), 0.800 (RL) vs other-seed 0.807, 0.802; median common text prefix 25 and 18 characters. None. Same
4 attempt-0 samples, cap 16,384, T 1.0; edit cued, RL plain (by design). The null is biased: its fresh base samples
are restarts, which exist only after a cap hit. (e) Edit right: problem 70 sample 0, boxed 104, gold 104, finished
derivation. Edit wrong: problem 29 sample 0, gold 244, text degenerates into multilingual noise. (f) Grader v2: -0.0124
[-0.037, 0.012], no change. The cap matters: base cap hits 234 of 484 (edit 61, RL 89); much of the gain is finishing.

## 4. d1 editreach-02: S = (E - B) / (R - B) (posted 0.88 [0.69, 1.13], n 120)
(a) 0.880 [0.683, 1.143], n 120; R - B 0.104 [0.065, 0.144]: matches. (b) Frozen first. -02 reran after -01 gave S
0.80 (account-2 undecided); the fix is correct (the spec selects all 121 base-0-of-4 problems, -01 looped over ids
0-327) and my loop over stored ids gives 0.88. Not posted before. (c) Null S = 0 is fair; account-1's range is the real
rival and S is wholly above it. (d) B is the cap32 sample, which shares sample 0's seed; its text matches sample 0 on a
median 2.6 % of characters, one problem (identical, dropped by sha256) on over 99 %: fresh. B rests on 6 right of 120.
B from restarts plus cap32 gives S 0.871; cap32 scored at 32k gives 0.880. (e) As in 3. (f) Grader v3, cut 16,384.

**Accept:** d1 with edit0of4 (one measurement): where the cued base misses 4 of 4, the edit is right as often as RL
(68 vs 74 of 480), well above a fresh base sample (6 of 120). merge328: the vote gains from differing wrong answers,
which does not show slips are independent. s100vote: right number, but an accuracy-matched null predicts most of it.
