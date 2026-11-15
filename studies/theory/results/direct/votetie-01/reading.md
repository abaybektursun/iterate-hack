# votetie-01 (round-13/s3-b): reading

## 10 raw rows read (problems in G: wrong by the vote over samples 0-3, right by the vote over 12)

Format: problem, gold, right samples of 12, k=4 group sizes, k=12 group sizes, what the 12 answers show.

1. 166, gold 270/7: right 2 of 12; k=4 [1,1,1]; k=12 nine groups, the right one (samples 6, 9) the only pair. Eight wrong values (4pi/7, 900/7, 540/7, 360/7, 15, 150, 30, 1/5): wrong answers split, right wins with 2.
2. 491, gold 64: right 3; k=4 four singletons (324, 64, junk, 32); k=12 ten groups, right is the only triple. Split wrong answers.
3. 94, gold 80: right 4; k=4 a 2-2 tie (30 vs 80) lost by sample order; k=12 [3,4,...]: 30 grows to 3, right to 4, six other wrong singletons. A tie at k=4, but p = 1/3.
4. 189, gold 160: right 4; 6 rows with no extracted answer (cap hits); k=12 [1,4,1]. Wins because cap hits cast no vote, not mainly because wrong answers split.
5. 295, gold 11: right 2; 9 rows with no answer, one wrong (13). Same cause as 189: the vote runs over 3 answer-bearing rows.
6. 71, gold 2516_8: right 6; k=4 four singletons (516_8, 2552, 2516, 3516); k=12 right 6, six wrong singletons. A k=4 tie with p = 0.5: the only b-type row here.
7. 403, gold 3: right 6; k=4 [1,2,1] with the wrong value 1 holding 2; k=12 6 vs 5 (value 1). A near-even wrong attractor, beaten by one sample: neither a split nor a tie.
8. 232, gold 1997/2: right 7; k=4 winner 999 (2 of 4); k=12 7 right vs 999/998/1997. A wrong pair at k=4 overtaken by a majority.
9. 50, gold 203: right 7; k=4 the wrong value 29 holds 3 of 4; k=12 right 7, 29 stays at 3. A wrong attractor at k=4, majority at 12.
10. 39, gold 23: right 9; k=4 four singletons (32, an extraction fragment "the answer to the", 59, 23); k=12 right 9. A k=4 tie lost by sample order with a near-certain right answer: b-type, p = 0.75.

## What they show

|G| = 21. Only 2 of 21 (rows 6 and 10: problems 71 and 39) were k=4 ties with the right answer in the tied top group and
right in at least half of 12 (S_b = 0.095, 90 % interval [0.000, 0.190]). Ties at k=4 with a right group are common in G
(9 of 21), but 7 of those 9 have p < 0.5 (rows 2-3: 491 and 94 are ties at p 1/4 and 1/3). Only 7 of 21 have
p >= 0.5; 4 of the other 5 were lost at k=4 to a wrong pair or triple (rows 7-9, and 80), and 170 had no right sample in 0-3. Null F (k=4 failures with
a right sample in 0-3 that 12 does not fix, n = 7): 1 of 7 (0.143). S_b - S_null = -0.048 [-0.286, 0.143]. Verdict:
refuted (S_b < 0.60 and difference < 0.20).
