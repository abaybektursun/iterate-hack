# abstain-01: 10 raw rows read by hand

Think-SFT + cue on hard328. Vote = samples 1-3 of `thinkvote/hard328_sft1_cue_s4-01` (cap 16,384) + the cap-32,768 row
(`cap32/rows-01/sft_cue.jsonl`, last 250 characters of its text read). "c32" = the cap-32,768 row; tokens in brackets.

Ties the frozen rule gives to the native row (a wrong converted row against one right native row, the other two cap hits):

1. 61 (gold 113): c32 boxes 87 after "complex algebraic manipulations ... approximate value" [25,469]; sample 2 says 113 [13,938]. 1-1 tie, the shorter right row wins. Under a random tie-break this is half a flip.
2. 70 (gold 104): c32 boxes 199 - sqrt(8481), "choosing the physically meaningful solution" [20,398]; sample 2 right [13,194]. Same 1-1 tie.
3. 76 (gold 468): c32 boxes 208 [25,956], a clean-looking finish; sample 2 right [13,624]. Same tie.
4. 98 (gold 62): c32 boxes 36 [31,639] after Chinese words mid-sentence ("I will assume最终答案 is 36"), then a second answer section starts; sample 1 right [13,069]. Drifted guess, same tie.
5. 109 (gold 336): c32 boxes 312 [24,128]; the right vote is sample 2, itself a 16,384 cap hit whose cut text holds a box (336) that v3 credits. Same tie.

Gains (all three native samples hit the cap and abstain; the converted row alone decides):

6. 80 (gold 211): c32 boxes 211 [29,546]. Wrong in A (no vote at all), right in B.
7. 110 (gold 293): c32 boxes 293 [18,538]. Same pattern.
8. 170 (gold 56): c32 boxes 56 [16,532], 148 tokens past the cut. Same pattern.
9. 283 (gold 5762): c32 ends "Answer: 5762" twice, no box [23,651]; v3 takes it. Same pattern.

RL plain contrast, the one D problem:

10. 135 (gold -1): RL sample 1 is a 16,384 cap hit with an extracted 2023; sample 2 finishes -1 [13,058]; RL's converted row also says 2023 [21,008]. 1-1 becomes 2-1 for 2023: a plurality flip from two agreeing wrong answers.

What they show: in the frozen design (one converted vote) a wrong converted row never agrees with a wrong native answer on
a problem the vote had right; its only route to a flip is a 1-1 tie (9 problems), and the length tie-break always gives
those to the native row, which is shorter by construction. All 5 gains come from problems where every native sample hit
the cap. Read for the secondary (4 converted rows, `cap32vote` rows, not deciding): problems 88 (two converted rows agree
on 7 against a right 127), 168 (two converted 0 against 1037) and 394 (5 twice against 11) are the plurality flips the
mechanism describes; they need two wrong late answers to agree, which one converted vote cannot supply.
