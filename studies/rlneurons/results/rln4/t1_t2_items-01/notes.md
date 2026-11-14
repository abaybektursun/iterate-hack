# T1 (base + cue, T 1.0) against T2 (RL, T 1.0) on MATH-500: failure diagnosis

Inputs: runs/diag_t1t2/T1.jsonl, T2.jsonl. Grader v3 imported from studies/rlneurons/lib/rln4_lib.py
(python3 -I, system site-packages has math-verify 0.9.0 and numpy; no uv needed). Scripts: score.py, view.py in this folder.

## Cross-check T1
score.py on T1: 410 right, 27 cap hits, 25 nothing extracted, 0 rule-A loops (onset_lines). Matches readout.json
cells.base_opener_1.0 (410 / 27 / 25). Modes: 340 boxed, 135 marker, 25 none.

## Raw reading notes, T1 wrong (90 rows)
Cap hits (27), tails read for all: none is a repetition loop (rule A fires on 0). All are long free-running
reasoning that does not converge: two computations disagree and the text keeps re-deriving (21, 26, 306, 340, 444),
no method found (96, 110, 126, 145, 248, 392, 422), brute numeric search (352, 43, 401).
Several cap hits state the gold answer and keep going: 26 (144 then doubts it), 308 (2 sqrt3 + 1 stated at the cap),
219 (writes "boxed{1/2}" then a long summary), 295 (boxed 7, wrong, then starts a second write-up and hits the cap).

## Cross-check T2
score.py on T2: 463 right, 6 cap hits (110, 136, 308, 444, 460, 481), 1 nothing extracted (168), 0 rule-A loops.
Matches readout.json cells.rl_1.0 (463 / 6 / 1). T2 is boxed in 499 of 500 answers; T1 is boxed in 340, "Answer:" marker in 135, nothing in 25.
Both models' texts begin with " line!\n\nOkay" (it is the RL model's own opening).

## 1. 2x2 (grader v3, n = 500)
|                 | RL right | RL wrong |
|---|---|---|
| cued base right | 398 | 12 |
| cued base wrong | 65 | 25 |
Rows 410 / 90, columns 463 / 37. Net gap 65 - 12 = 53 problems (10.6 points).

## 2. The 65 "RL right, cued base wrong" problems, by failure type (hand labels, one reader)
Every tail (last 420-480 characters) read; 30 finished answers read in more depth (problem + 750-1,300 characters before the
tail): 4 36 46 60 62 64 71 80 101 137 138 159 176 222 228 242 272 279 358 385 389 396 403 419 438 458 466 485 491 497;
148 and 180 read in full; 188 probed at four positions. RL answers read for 46 62 137 148 228 229 272 358 378 403 458.
Labelled from the tail only (least certain): 20 103 170 189 445 478 439.

| type | n | ids | T1 tokens median | T2 tokens median |
|---|---|---|---|---|
| cap hit, no loop (reasoning does not converge) | 16 | 21 26 43 96 120 126 145 219 224 239 248 352 401 412 425 475 | 16,384 | 8,594 |
| wrong method, missed case, or question not answered | 9 | 80 103 138 170 189 228 358 445 478 | 10,393 | 8,029 |
| misread or mis-copied problem or diagram | 14 | 4 71 101 137 222 272 279 385 389 396 403 458 485 491 | 4,392 | 5,242 |
| arithmetic or algebra slip, method right | 14 | 20 36 46 60 62 64 159 176 242 419 438 439 466 497 | 5,305 | 5,375 |
| reached the gold answer, then changed it | 2 | 97 372 | 10,924 | 8,714 |
| answer right, form rejected by grader v3 | 5 | 135 165 338 354 447 | 792 | 1,923 |
| answer right in the reasoning, final "Answer:" line garbled | 3 | 148 229 378 | 492 | 1,225 |
| drift to another document, no answer | 2 | 180 188 | 4,230 | 3,924 |
"Stopped early or little working" as a separate type: 0. The short failures are in the form, misread and slip rows.
Rule-A loops (onset_lines): 0 of 500 in either cell.

Quotes (problem id, gold):
- cap, 26 (gold 144): "we computed valid arrangements as 144 [...] But according to the calculation of invalid as 432, valid
  would be 288 [...] Wait, perhaps the manual counting was wrong" (cut at 16,384).
- cap, 126 (gold 1+274i): "Given the time I've spent and lack of progress, I think it's time to look for another approach".
- wrong method, 228 (gold 288 pi): "the region enclosed by S is a sphere with radius 6. \boxed{\text{Sphere}}" (RL: "V = 4/3 pi 6^3 = 288 pi").
- misread, 272 (gold 1030; problem 0.\overline{1331}): "we start by setting x = 0.1313131313... Since the repeating part is three
  digits" (RL: "Let me confirm that. The overline is over the four digits 1331").
- misread, 137 (problem 413_5 / 2_5): "The quotient of 413_5 ÷ 25_5 in base 5 is \boxed{149_5}".
- slip, 159 (gold 3.21): "b + c = 1.3 + 1.91 = 3.2 [...] Thus, the final answer is \boxed{3.2}".
- slip, 62 (gold 4): "A^T A = [...] = (4 0; 0 4)" (true product (4 6; 6 13); RL gets eigenvalues 16 and 1).
- changed, 372 (gold 90): "leading to x = 90°. 8. Reconcile contradictions: However, further analysis shows [...] ∠BAC = 75°".
- changed, 97 (gold east): "rotating 90° clockwise [...] results in facing east. However, considering a mathematical model [...] \boxed{West}".
- form, 135 (gold 9): "**Answer:** There are 9 zeros at the end of $42!$."   338 (gold 4343_6): "**Answer:**  \n4343_6" (answer on the next line).
- garbled, 378 (gold 3): "So the answer is 3. [...] Answer: $Answer where $Answer is the answer to the problem." (the prompt's own template echoed)
  148 (gold 11): "So x = 11 is the solution. [...] **Answer**: $-$".
- drift, 188: "Keep the story to exactly 500 words. **The Mysterious Attic: A Journey Through Time**"; 180: incoherent from the first tokens
  ("Okay 2-digit integer is can only be Even by definition [...] Ron Mewcid to 4 President").

Three groups by length:
- 16 cap hits (25 %).
- 23 answers under 4,000 tokens (35 %): 8 form/garbled, 6 misread, 6 slip, 2 wrong method, 1 drift. T1 median 1,592 tokens, T2 median 3,878 on the
  same problems; the base is shorter in 22 of 23. T2 has 0 wrong answers under 4,000 tokens (its shortest wrong answer has 6,215); all 23 of T1's
  wrong answers under 4,000 tokens are in this cell.
- 26 finished answers of 4,000 tokens or more (40 %): 8 slip, 8 misread, 7 wrong method, 2 changed answer, 1 drift.

## 3. Subject, level, tokens
subject: n | both, RL only, base only, neither | T1 right %, T2 right %
algebra 124 | 115 8 1 0 | 94 99
counting_and_probability 38 | 29 5 1 3 | 79 89
geometry 41 | 27 6 3 5 | 73 80
intermediate_algebra 97 | 70 17 2 8 | 74 90
number_theory 62 | 53 7 2 0 | 89 97
prealgebra 82 | 61 12 3 6 | 78 89
precalculus 56 | 43 10 0 3 | 77 95
level 5: 134 | 88 24 5 17 | 69 84
levels 1-4: 366 | 310 41 7 8 | 87 96
Level source: math500.json has no level field. Level 5 comes from a file outside the repo,
~/Library/Application Support/Claude/side-session-notes/local_c3a767d5-.../hackathon-research/results/A1-gate/data/math500_l5.json
(134 problems, all 134 matched by problem text). Levels 1 to 4 could not be separated.
Type by level 5: cap 8 of 16, wrong method 5 of 9, slip 5 of 14, misread 4 of 14, form/garbled 1 of 8.
Type by subject: cap hits are intermediate algebra 8, precalculus 4, counting 3, geometry 1. Form/garbled are prealgebra 5, algebra 2, number theory 1.

Generated tokens (n_generated), median / 90th percentile / n:
T1 base right 1,432 / 7,054 / 410; wrong 10,548 / 16,384 / 90; wrong and finished 5,775 / 14,162 / 63.
T2 RL right 3,014 / 8,430 / 463; wrong 13,455 / 16,384 / 37; wrong and finished 12,298 / 15,616 / 32.
By cell (T1 median, T2 median): both 1,400 and 2,710 (base shorter in 340 of 398, under half the RL length in 171);
RL only 7,128 and 6,408; base only 7,763 and 11,541; neither 15,849 and 13,494.
RL-only, finished (n = 49): base median 4,721, RL 5,075; base shorter in 36, under half of RL in 14.

## 4. Signals a reward-free procedure could use
- Length. n_generated separates wrong from right: AUC 0.83 for T1 (all 500), 0.96 for T2. T1: above 4,000 tokens 67 of 141 wrong, below 23 of 359.
  T2: above 4,000 tokens 37 of 214 wrong, below 0 of 286. Among finished answers the mean token log-probability does as well for T1 (AUC 0.76, same as length).
- Probability of the answer span (answer_prob): median 0.998 on T1 wrong answers (n = 46), 0.999 on right ones. No signal.
- Gold answer present in the wrong text: at least 13 of 65 (8 form/garbled, 219 which wrote "boxed{1/2}" and ran on to the cap, cap hits 26 and 120,
  changed answers 97 and 372). The regex count alone finds 8 of 65.
- Final answer against earlier results in the same text. Regex (an "answer is X" or box before the final one that differs from it):
  T1 wrong-RL-right 24 of 48 with an extracted answer; T1 right 91 of 398; T2 right on the same 65 problems 34 of 65. Not specific: RL revises more than the base.
  First box against last box (answers with 2 or more boxes): differ in 3 of 43 T1 wrong finished, 8 of 212 T1 right; the write-up after the first box
  never turned a right first box into a wrong last box (0 cases in T1, 1 in T2).
  By reading, 10 of the 49 finished answers show a conflict the text itself mentions or contains: 20 64 71 176 (two computations disagree, one picked),
  97 372 (right answer replaced), 189 445 (number in the working differs from the boxed one), 242 (working says 32,372, box says 32772), 438 (0.274, then "last nonzero digit is 7").
  Cap hits whose tail states a conflict between two results: 21 26 120 (3 of 16); the other 13 are searching for a method.
- Self-doubt and restarts. "Wait/Hmm/mistake/contradict/..." per 1,000 tokens, median: T1 wrong-RL-right 6.4, T1 right 5.3, T2 right 7.8 to 9.0. Restart phrases
  per 1,000 tokens: 1.4, 1.2, 1.7 to 1.9. RL doubts and restarts more often than the base, so these counts do not mark base failures (AUC of "Wait" density 0.72 for T1 finished).
- Drift away from the solution format. Another document type: 2 of 65 (180 from about token 5 of 266; 188 at about token 7,200 of 8,195, a story-writing prompt).
  Code block after the answer: 36 (token 1,561 of 1,592, a ```sage block, answer already given). Non-Latin script inside the reasoning: 96 (Chinese, token 10,220),
  439 (Cyrillic, token 6,410), 9 in the neither cell (Chinese, token 10,365); a few characters, then English again. Non-Latin script occurs in 3 of 90 T1 wrong and 0 of 410
  T1 right answers, and in 5 of 37 T2 wrong and 0 of 463 T2 right. Prompt template echoed in the final line: 229 378 (and 94 in the neither cell). No answer starts a new
  problem or chat turn by the regex (Problem:/Question:/User:/...); 2 T1 right answers match it.
  Token positions are character offsets scaled by tokens per character, not tokenizer positions.
- Format. 12 of 65 end with an "Answer:" marker and 17 have neither box nor marker (16 of them cap hits or drift). RL boxes 499 of 500.

## 5. The 12 "cued base right, RL wrong" problems
100 119 128 168 217 273 303 309 317 324 361 473. No cap hit. All RL answers are long: 6,215 to 15,674 tokens, median 11,541 (base median 7,763 on the same problems).
5 are level 5. 361: RL derives 16 sqrt 3 (gold) then writes "side length [...] is 8 sqrt 3" and boxes 8. 168: RL stops at 15,674 tokens mid-reasoning with no box.
303: "1/2 x 28 = 14 ⟹ 21", box 21. 217: 10111111100 for 11111111100. 273: write-up answers "the sum of numbers from 1 to 40" (820, gold 1250).
119 128 309 317 100 324 473: a finished, boxed, wrong answer after long reasoning. These look like the same long-answer errors as the 25 "neither" problems
(T1 cap 11, T2 cap 5, 17 of 25 level 5), where one model's sample happened to come out right.

## Not checked
- Levels 1 to 4. Level 5 flag comes from a file outside the repo.
- Labels come from one reader in one pass, with no second reader. The slip / misread / wrong-method split is a judgment from partial reads; 7 labels use the tail only. I did not re-derive the mathematics of each problem.
- One sample per problem: I cannot say which failures would repeat on a second sample (misreads and slips look like sampling noise but that is untested here).
- The regex signals (candidate answers, doubt words) were not validated against hand counts beyond the cases listed.
- Grader: 5 answers (135 165 338 354 447) state the gold answer in the final line and are scored wrong by v3; I did not check how many RL or base "right" answers v3 accepts wrongly (473 T1 is accepted with extracted text ": 7$} The solution is found by...").

Files: per_problem.json (500 rows), T1_scored.json, T2_scored.json, feats.json, sig2.json, cells.json, isl5.json; scripts score.py view.py view2.py feat.py agg.py sig2.py labels.py.
