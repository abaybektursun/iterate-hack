# cue100-01: 10 raw rows read by hand

The 10 MATH-500 problems with the largest per-problem gap between step-100 cue and step-100 plain (right of 4
samples each, grader v3 as stored). Format: problem, gold, cue answers (right), plain answers (right).

1. 50, gold 203: cue 203 / "(the result after summing all odd-length subarrays)" / 29 / 256 (1 of 4); plain 203 x4 (4). Cue sample 1 wrote a placeholder, not a number.
2. 120, gold even: cue "even**." / even / even / even (3; sample 0 lost to a markdown "**." left in the extracted answer); plain "neither" x4 (0). A real reasoning difference, plus one grader-format loss.
3. 168, gold 19: cue 10 / 14 / 13 / 24 (0); plain 19 / 19 / cap hit / 19 (3). Cue answers scatter; plain agrees.
4. 184, gold (2, inf): cue [2, inf) x2, another interval, (2, inf) (1); plain (2, inf) x4 (4). Cue closes the endpoint.
5. 279, gold 7pi: cue 7pi / 4pi / 4pi / 4pi (1); plain 7pi x4 (4). Same wrong value three times under the cue.
6. 351, gold 1/16: cue cap hit / -1/16 / cap hit / 1/16 (1); plain 1/16 x4 (4). Two cue cap hits.
7. 475, gold 29: cue cap hit / 29 / "m/n = p ... m+n=75." / 13 (1); plain 29 x4 (4).
8. 490, gold 14: cue 16 / cap hit / 12 / 14 (1); plain 14 x4 (4).
9. 491, gold 64: cue 64 / 64 / cap hit / 64 (3); plain 3000 / 32 / 864 / 32 (0). The cue fixes a problem plain never solves.
10. 32, gold 720: cue 720 / 240 (cap hit) / 720 / 1440 (2); plain 720 x4 (4).

What they show: the largest single-problem swings mostly go against the cue (8 of 10 favour plain, 7 of the 9
three-sample swings), often through cap hits (6 cue cap hits in these rows against 1 plain) and scattered wrong
values. The cue's net lead (+8.5 problems per 500) comes from many small gains: 73 problems where the cue has one
more right sample, 46 where plain has one more; 18 against 7 at two more; 2 against 7 at three more. So the cue
moves problems in both directions, and the net is positive but small. The stored answers are real, distinct
extractions (no duplicated draws across arms: seeds 41,0x0,000 for cue and 45,0x0,000 for plain); one row (120,
sample 0) shows a grader-format loss that costs the cue a point, so grader v3 does not inflate the cue's count here.
